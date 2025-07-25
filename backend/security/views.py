import datetime
import json
import os
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from projects.api.projectpresets import initUser
from security.models import UserVerification
from django.core.mail import send_mail


def get_csrf(request):
    response = JsonResponse({"detail": "CSRF cookie set"})
    response["X-CSRFToken"] = get_token(request)
    return response


@require_POST
def loginUser(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    try:
        verification = UserVerification.objects.get(user__username=username)
        if not verification.is_email_verified:
            return JsonResponse({"detail": "Not yet verified"}, status=406)
    except UserVerification.DoesNotExist:
        UserVerification(user=User.objects.get(username=username)).save()
        return JsonResponse({"detail": "Not yet verified"}, status=406)

    if username is None or password is None:
        return JsonResponse(
            {"detail": "Please provide username and password."}, status=400
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({"detail": "Invalid credentials."}, status=400)

    login(request, user)
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

    return JsonResponse({"isAuthenticated": True})


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

    try:
        user = User.objects.create_user(**data)
        user.save()

        verification = UserVerification(user=user)
        verification.token = uuid4()
        verification.token_date = datetime.datetime.now(datetime.UTC)
        verification.save()

        initUser(user)
    except IntegrityError:
        return JsonResponse(
            {"detail": "User with this name already exists"}, status=409
        )

    send_verification_mail(user.username, user.email, verification.token)

    return JsonResponse({"detail": "User was created"})


@require_POST
def verify_mail(request, username, token):
    verification = UserVerification.objects.get(user__username=username)

    if (
        datetime.datetime.now(datetime.UTC) - verification.token_date
    ).total_seconds() > 5 * 60:
        return JsonResponse({"detail": "Token expired"}, status=400)

    if verification.token != token:
        return JsonResponse({"detail": "Invalid token"}, status=400)

    verification.is_email_verified = True
    verification.save()

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
    send_verification_mail(username, user.email, verification.token)

    return JsonResponse({"detail": "E-Mail was sent"})


def send_verification_mail(username, email, token):
    link = f"{os.environ.get("ORIGINS", "http://localhost:8080")}/verify_mail/{username}/{token}/"
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

    send_mail(
        subject="[WebUrbs] Mail Verification",
        message=message,
        recipient_list=[email],
        from_email=os.environ.get("EMAIL_HOST_USER"),
    )
