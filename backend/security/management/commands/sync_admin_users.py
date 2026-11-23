from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from security.admin_users import apply_preapproved_admin, get_admin_usernames
from security.models import UserVerification


class Command(BaseCommand):
    help = "Promote users listed in ADMIN_USERNAMES to admin (approved, active)."

    def handle(self, *args, **options):
        usernames = get_admin_usernames()
        if not usernames:
            self.stdout.write("ADMIN_USERNAMES is empty; nothing to sync.")
            return

        for name in sorted(usernames):
            try:
                user = User.objects.get(username__iexact=name)
            except User.DoesNotExist:
                self.stdout.write(f"skip {name} (not registered yet)")
                continue

            verification, _ = UserVerification.objects.get_or_create(user=user)
            conflict = apply_preapproved_admin(user, verification)
            if conflict:
                self.stdout.write(
                    self.style.WARNING(f"skip {user.username}: {conflict}")
                )
                continue
            self.stdout.write(self.style.SUCCESS(f"promoted {user.username}"))
