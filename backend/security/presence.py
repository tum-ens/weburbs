from datetime import timedelta

from django.utils import timezone

from security.models import UserVerification

ONLINE_WINDOW = timedelta(minutes=5)
PRESENCE_WRITE_INTERVAL = timedelta(seconds=60)


def touch_user_presence(user) -> None:
    """Record user activity; throttled to one DB write per minute."""
    verification, _ = UserVerification.objects.get_or_create(user=user)
    now = timezone.now()
    if (
        verification.last_seen_at
        and now - verification.last_seen_at < PRESENCE_WRITE_INTERVAL
    ):
        return
    verification.last_seen_at = now
    verification.save(update_fields=["last_seen_at"])


def is_user_online(verification: UserVerification) -> bool:
    if not verification.last_seen_at:
        return False
    return timezone.now() - verification.last_seen_at <= ONLINE_WINDOW
