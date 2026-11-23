from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from security.models import UserVerification

REJECTED_RETENTION_DAYS = 30
UNVERIFIED_RETENTION_DAYS = 30


def permanently_delete_user(user: User) -> None:
    """Remove user and all related rows (projects cascade, verification cascade)."""
    user.delete()


def purge_rejected_users_older_than(days: int = REJECTED_RETENTION_DAYS) -> list[str]:
    """Delete rejected accounts whose rejection date is older than *days*."""
    cutoff = timezone.now() - timedelta(days=days)
    verifications = UserVerification.objects.filter(
        is_admin_rejected=True,
        rejected_at__isnull=False,
        rejected_at__lt=cutoff,
    ).select_related("user")

    deleted: list[str] = []
    for verification in verifications:
        username = verification.user.username
        permanently_delete_user(verification.user)
        deleted.append(username)
    return deleted


def purge_unverified_users_older_than(
    days: int = UNVERIFIED_RETENTION_DAYS,
) -> list[str]:
    """Delete accounts that never verified their email and registered before *days* ago."""
    cutoff = timezone.now() - timedelta(days=days)
    verifications = UserVerification.objects.filter(
        is_email_verified=False,
        is_admin_rejected=False,
        user__date_joined__lt=cutoff,
    ).select_related("user")

    deleted: list[str] = []
    for verification in verifications:
        username = verification.user.username
        permanently_delete_user(verification.user)
        deleted.append(username)
    return deleted
