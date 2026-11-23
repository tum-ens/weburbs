from django.core.management.base import BaseCommand

from security.user_deletion import (
    UNVERIFIED_RETENTION_DAYS,
    purge_unverified_users_older_than,
)


class Command(BaseCommand):
    help = (
        f"Permanently delete unverified users older than "
        f"{UNVERIFIED_RETENTION_DAYS} days."
    )

    def handle(self, *args, **options):
        deleted = purge_unverified_users_older_than()
        if not deleted:
            self.stdout.write("No unverified users to purge.")
            return
        for username in deleted:
            self.stdout.write(self.style.SUCCESS(f"purged {username}"))
