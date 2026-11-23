import datetime
import json
import logging
import os
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from projects.api.simulate import stop_simulation_record
from projects.models import SimulationResult
from security.admin_users import (
    apply_preapproved_admin,
    is_preapproved_admin,
    try_sync_preapproved_admin,
)
from security.email import send_resend_email, use_resend
from security.email_approval import email_approval_conflict
from security.models import UserVerification
from security.presence import is_user_online, touch_user_presence
from security.user_deletion import permanently_delete_user


def _require_admin(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Not authenticated"}, status=401)
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"detail": "Admin only"}, status=403)
    return None


def get_csrf(request):
    response = JsonResponse({"detail": "CSRF cookie set"})
    response["X-CSRFToken"] = get_token(request)
    return response


@require_POST
def loginUser(request):
    data = json.loads(request.body)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if username is None or password is None:
        return JsonResponse(
            {"detail": "Please provide username and password."}, status=400
        )

    try:
        user_obj = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return JsonResponse({"detail": "Invalid credentials."}, status=400)

    verification, _ = UserVerification.objects.get_or_create(user=user_obj)

    conflict = try_sync_preapproved_admin(user_obj, verification)
    if conflict:
        return JsonResponse({"detail": conflict}, status=403)

    user_obj.refresh_from_db()
    verification.refresh_from_db()

    if not verification.is_email_verified:
        return JsonResponse({"detail": "Not yet verified"}, status=406)

    if not verification.is_admin_approved or not user_obj.is_active:
        return JsonResponse({"detail": "Account not approved yet"}, status=403)

    user = authenticate(username=user_obj.username, password=password)

    if user is None:
        return JsonResponse({"detail": "Invalid credentials."}, status=400)

    login(request, user)
    touch_user_presence(user)
    return JsonResponse({"detail": "Successfully logged in."})


def logoutUser(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "You're not logged in."}, status=400)

    logout(request)
    return JsonResponse({"detail": "Successfully logged out."})


@ensure_csrf_cookie
def session(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False})

    touch_user_presence(request.user)
    return JsonResponse({"isAuthenticated": True})


@require_POST
def presence(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Not authenticated"}, status=401)

    touch_user_presence(request.user)
    return JsonResponse({"detail": "ok"})


def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False}, status=401)

    user = request.user
    return JsonResponse(
        {
            "isAuthenticated": True,
            "username": user.username,
            "email": user.email,
            "isStaff": user.is_staff,
            "isSuperuser": user.is_superuser,
        }
    )


@require_POST
def register(request):
    data = json.loads(request.body)

    if len(data["username"]) <= 3:
        return JsonResponse({"detail": "Username is too short"}, status=400)
    try:
        validate_email(data["email"])
    except ValidationError:
        return JsonResponse({"detail": "Invalid E-Mail"}, status=400)
    if len(data["password"]) < 5:
        return JsonResponse({"detail": "Password is too short"}, status=400)

    preapproved_admin = is_preapproved_admin(data["username"])

    if preapproved_admin:
        conflict = email_approval_conflict(data["email"])
        if conflict:
            return JsonResponse({"detail": conflict}, status=409)

    try:
        user = User.objects.create_user(**data)

        verification = UserVerification(user=user)
        verification.token = uuid4()
        verification.token_date = datetime.datetime.now(datetime.UTC)

        if preapproved_admin:
            conflict = apply_preapproved_admin(user, verification)
            if conflict:
                user.delete()
                return JsonResponse({"detail": conflict}, status=409)
        else:
            user.is_active = False
            user.save()
            verification.is_admin_approved = False
            verification.save()

        from projects.api.projectpresets import initUser

        initUser(user)
    except IntegrityError:
        return JsonResponse(
            {"detail": "User with this name already exists"}, status=409
        )
    except Exception as e:  # noqa: BLE001
        return JsonResponse({"detail": f"Registration failed: {e!s}"}, status=500)

    if preapproved_admin:
        return JsonResponse(
            {
                "detail": "Admin account was created. You can log in now.",
            },
            status=201,
        )

    # Step 1: email verification (token link). Step 2: admin approval.
    try:
        send_verification_mail(user.username, user.email, verification.token)
    except (OSError, ValueError, RuntimeError):
        logging.getLogger(__name__).warning(
            "Failed to send verification email", exc_info=True
        )

    return JsonResponse(
        {
            "detail": "User was created. Verify your email, then wait for admin approval."
        },
        status=201,
    )


def pending_users(request):
    err = _require_admin(request)
    if err:
        return err

    pending = (
        UserVerification.objects.select_related("user")
        .filter(
            is_email_verified=True, is_admin_approved=False, is_admin_rejected=False
        )
        .order_by("-user__date_joined")
    )
    data = [
        {
            "username": v.user.username,
            "email": v.user.email,
            "date_joined": v.user.date_joined,
            "is_active": v.user.is_active,
        }
        for v in pending
    ]
    return JsonResponse({"pending": data})


def list_users(request):
    err = _require_admin(request)
    if err:
        return err

    status = request.GET.get("status", "pending")
    search = (request.GET.get("search") or "").strip()
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "50")), 1), 50)
    except ValueError:
        page_size = 50

    qs = UserVerification.objects.select_related("user")

    if status == "approved":
        qs = qs.filter(is_admin_approved=True)
    elif status == "rejected":
        qs = qs.filter(is_admin_rejected=True)
    elif status == "unverified":
        qs = qs.filter(
            is_email_verified=False,
            is_admin_rejected=False,
        )
    else:
        qs = qs.filter(
            is_email_verified=True, is_admin_approved=False, is_admin_rejected=False
        )

    if search:
        from django.db.models import Q

        qs = qs.filter(
            Q(user__username__icontains=search) | Q(user__email__icontains=search)
        )

    if status == "unverified":
        qs = qs.order_by("-user__date_joined")
    else:
        qs = qs.order_by("user__username")

    total = qs.count()
    total_pages = (total + page_size - 1) // page_size if total else 1
    page = min(page, total_pages)

    start = (page - 1) * page_size
    end = start + page_size
    rows = qs[start:end]

    results = []
    for v in rows:
        row = {
            "username": v.user.username,
            "email": v.user.email,
            "date_joined": v.user.date_joined,
            "is_active": v.user.is_active,
        }
        if status == "rejected" and v.rejected_at:
            row["rejected_at"] = v.rejected_at.isoformat()
        if status == "unverified" and v.token_date:
            row["token_date"] = v.token_date.isoformat()
        if status == "approved":
            row["is_online"] = is_user_online(v)
            if v.last_seen_at:
                row["last_seen_at"] = v.last_seen_at.isoformat()
        results.append(row)

    return JsonResponse(
        {
            "results": results,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "status": status,
            "search": search,
        }
    )


@require_POST
def approve_user(request, username):
    err = _require_admin(request)
    if err:
        return err

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"detail": "User not found"}, status=404)

    conflict = email_approval_conflict(user.email, exclude_user_id=user.id)
    if conflict:
        return JsonResponse({"detail": conflict}, status=409)

    verification, _ = UserVerification.objects.get_or_create(user=user)
    verification.is_admin_approved = True
    verification.is_admin_rejected = False
    verification.rejected_at = None
    verification.save()

    user.is_active = True
    user.save()

    return JsonResponse({"detail": f"Approved {username}"})


@require_POST
def reject_user(request, username):
    err = _require_admin(request)
    if err:
        return err

    user = User.objects.get(username=username)
    verification, _ = UserVerification.objects.get_or_create(user=user)
    verification.is_admin_approved = False
    verification.is_admin_rejected = True
    verification.rejected_at = timezone.now()
    verification.save()

    user.is_active = False
    user.save()

    return JsonResponse({"detail": f"Rejected {username}"})


@require_POST
def delete_user_permanently(request, username):
    err = _require_admin(request)
    if err:
        return err

    try:
        user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return JsonResponse({"detail": "User not found"}, status=404)

    if user.id == request.user.id:
        return JsonResponse(
            {"detail": "You cannot delete your own account"}, status=400
        )

    try:
        verification = UserVerification.objects.get(user=user)
    except UserVerification.DoesNotExist:
        return JsonResponse({"detail": "User is not in the rejection list"}, status=400)

    deletable = verification.is_admin_rejected or (
        not verification.is_email_verified and not verification.is_admin_approved
    )
    if not deletable:
        return JsonResponse(
            {"detail": "Only rejected or unverified users can be permanently deleted"},
            status=400,
        )

    deleted_username = user.username
    permanently_delete_user(user)
    return JsonResponse({"detail": f"Permanently deleted {deleted_username}"})


@require_GET
def running_simulations(request):
    err = _require_admin(request)
    if err:
        return err

    running = (
        SimulationResult.objects.filter(completed=False)
        .select_related("project", "project__user")
        .order_by("-timestamp")
    )

    by_user: dict[str, list[dict]] = {}
    for sim in running:
        username = sim.project.user.username
        by_user.setdefault(username, []).append(
            {
                "id": str(sim.id),
                "project": sim.project.name,
                "timestamp": sim.timestamp.isoformat(),
            }
        )

    return JsonResponse({"by_user": by_user})


@require_POST
def admin_stop_simulation(request, simid):
    err = _require_admin(request)
    if err:
        return err

    try:
        simres = SimulationResult.objects.select_related("project__user").get(id=simid)
    except SimulationResult.DoesNotExist:
        return JsonResponse({"detail": "Simulation not found"}, status=404)

    if simres.completed:
        return JsonResponse({"detail": "Simulation already finished"}, status=400)

    stop_simulation_record(simres)
    return JsonResponse({"detail": "Simulation stopped"})


@require_POST
def verify_mail(request, username, token):
    verification = UserVerification.objects.select_related("user").get(
        user__username__iexact=username
    )

    if (
        datetime.datetime.now(datetime.UTC) - verification.token_date
    ).total_seconds() > 5 * 60:
        return JsonResponse({"detail": "Token expired"}, status=400)

    if verification.token != token:
        return JsonResponse({"detail": "Invalid token"}, status=400)

    verification.is_email_verified = True
    verification.save()

    conflict = try_sync_preapproved_admin(verification.user, verification)
    if conflict:
        return JsonResponse({"detail": conflict}, status=409)

    if is_preapproved_admin(verification.user.username):
        return JsonResponse(
            {"detail": "E-Mail verified. Admin account is ready to log in."}
        )

    return JsonResponse({"detail": "E-Mail verified"})


@require_POST
def resend_mail(request, username):
    user = User.objects.get(username=username)

    verification = UserVerification.objects.get(user=user)

    if (
        verification.token_date is not None
        and (
            datetime.datetime.now(datetime.UTC) - verification.token_date
        ).total_seconds()
        < 5 * 60
    ):
        return JsonResponse(
            {"detail": "Cannot resend the token yet. Please wait some minutes..."},
            status=400,
        )

    verification.token = uuid4()
    verification.token_date = datetime.datetime.now(datetime.UTC)
    verification.save()

    try:
        send_verification_mail(username, user.email, verification.token)
    except (OSError, ValueError, RuntimeError) as e:
        logging.getLogger(__name__).warning("Failed to send verification email: %s", e)
        return JsonResponse({"detail": f"Failed to send email: {e!s}"}, status=500)

    return JsonResponse({"detail": "E-Mail was sent"})


PASSWORD_RESET_EXPIRY_SECONDS = 30 * 60


@require_POST
def request_password_reset(request):
    data = json.loads(request.body)
    email = (data.get("email") or "").strip()

    generic = JsonResponse(
        {
            "detail": "If an account with that email exists, a reset link has been sent.",
        }
    )

    if not email:
        return JsonResponse({"detail": "Please provide your email."}, status=400)

    user = User.objects.filter(email__iexact=email).order_by("-is_active").first()
    if user is None:
        # Don't reveal whether the email is registered.
        return generic

    verification, _ = UserVerification.objects.get_or_create(user=user)
    verification.reset_token = uuid4()
    verification.reset_token_date = datetime.datetime.now(datetime.UTC)
    verification.save()

    try:
        send_password_reset_mail(user.username, user.email, verification.reset_token)
    except (OSError, ValueError, RuntimeError) as e:
        logging.getLogger(__name__).warning(
            "Failed to send password reset email: %s", e
        )

    return generic


@require_POST
def reset_password(request, username, token):
    data = json.loads(request.body)
    password = data.get("password") or ""

    if len(password) < 5:
        return JsonResponse({"detail": "Password is too short"}, status=400)

    try:
        verification = UserVerification.objects.select_related("user").get(
            user__username__iexact=username
        )
    except UserVerification.DoesNotExist:
        return JsonResponse({"detail": "Invalid or expired reset link"}, status=400)

    if verification.reset_token is None or verification.reset_token_date is None:
        return JsonResponse({"detail": "Invalid or expired reset link"}, status=400)

    if str(verification.reset_token) != str(token):
        return JsonResponse({"detail": "Invalid or expired reset link"}, status=400)

    age = (
        datetime.datetime.now(datetime.UTC) - verification.reset_token_date
    ).total_seconds()
    if age > PASSWORD_RESET_EXPIRY_SECONDS:
        return JsonResponse({"detail": "This reset link has expired"}, status=400)

    user = verification.user
    user.set_password(password)
    user.save()

    verification.reset_token = None
    verification.reset_token_date = None
    verification.save()

    return JsonResponse({"detail": "Password was reset. You can now log in."})


def send_password_reset_mail(username, email, token):
    origins = os.environ.get("ORIGINS", "http://localhost").split(",")
    base_url = origins[0].strip().rstrip("/")
    link = f"{base_url}/resetPassword/{username}/{token}/"
    message = (
        f"Hi {username},\n"
        f"\n"
        f"We received a request to reset your WebUrbs password.\n"
        f"\n"
        f"You can set a new password using the following link:\n"
        f"{link}\n"
        f"\n"
        f"This link is valid for 30 minutes. "
        f"If you did not request this, you can ignore this email.\n"
        f"\n"
        f"Greetings from WebUrbs!"
    )

    if use_resend():
        send_resend_email(
            to=email,
            subject="[WebUrbs] Password Reset",
            text=message,
        )
        return

    send_mail(
        subject="[WebUrbs] Password Reset",
        message=message,
        recipient_list=[email],
        from_email=os.environ.get("EMAIL_HOST_USER"),
    )


def send_verification_mail(username, email, token):
    origins = os.environ.get("ORIGINS", "http://localhost").split(",")
    base_url = origins[0].strip().rstrip("/")
    link = f"{base_url}/verify_mail/{username}/{token}/"
    message = (
        f"Hi {username},\n"
        f"\n"
        f"Thank you for registering to WebUrbs.\n"
        f"\n"
        f"You can verify your E-Mail by using the following address:\n"
        f"{link}\n"
        f"\n"
        f"Greetings from WebUrbs!"
    )

    if use_resend():
        send_resend_email(
            to=email,
            subject="[WebUrbs] Mail Verification",
            text=message,
        )
        return

    send_mail(
        subject="[WebUrbs] Mail Verification",
        message=message,
        recipient_list=[email],
        from_email=os.environ.get("EMAIL_HOST_USER"),
    )
