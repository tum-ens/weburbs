from django.core.management.base import BaseCommand

from security.user_deletion import (
    REJECTED_RETENTION_DAYS,
    purge_rejected_users_older_than,
)


class Command(BaseCommand):
    help = (
        f"Permanently delete rejected users older than {REJECTED_RETENTION_DAYS} days."
    )

    def handle(self, *args, **options):
        deleted = purge_rejected_users_older_than()
        if not deleted:
            self.stdout.write("No rejected users to purge.")
            return
        for username in deleted:
            self.stdout.write(self.style.SUCCESS(f"purged {username}"))
