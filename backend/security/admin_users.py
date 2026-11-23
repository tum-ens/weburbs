import os

from security.email_approval import email_approval_conflict
from security.models import UserVerification


def get_admin_usernames() -> set[str]:
    raw = os.environ.get("ADMIN_USERNAMES", "")
    return {name.strip() for name in raw.split(",") if name.strip()}


def is_preapproved_admin(username: str) -> bool:
    return username.strip().lower() in {n.lower() for n in get_admin_usernames()}


def apply_preapproved_admin(user, verification: UserVerification) -> str | None:
    """Auto-approve and grant admin rights (no manual approval, login-ready)."""
    conflict = email_approval_conflict(user.email, exclude_user_id=user.id)
    if conflict:
        return conflict

    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()

    verification.is_admin_approved = True
    verification.is_email_verified = True
    verification.is_admin_rejected = False
    verification.rejected_at = None
    verification.save()
    return None


def try_sync_preapproved_admin(user, verification: UserVerification) -> str | None:
    """Promote listed admin if not yet approved. Returns error message or None."""
    if not is_preapproved_admin(user.username):
        return None
    if verification.is_admin_approved and user.is_active:
        return None
    return apply_preapproved_admin(user, verification)
