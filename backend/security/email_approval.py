from security.models import UserVerification


def email_approval_conflict(
    email: str, *, exclude_user_id: int | None = None
) -> str | None:
    """
    Return an error message if another approved account already uses this email.
    Rejecting the other account frees the email for approval.
    """
    if not (email or "").strip():
        return None

    qs = UserVerification.objects.filter(
        is_admin_approved=True,
        user__email__iexact=email.strip(),
    ).select_related("user")
    if exclude_user_id is not None:
        qs = qs.exclude(user_id=exclude_user_id)

    existing = qs.first()
    if not existing:
        return None

    return (
        f"Another account ({existing.user.username}) is already approved "
        f"with this email. Reject that account first."
    )
