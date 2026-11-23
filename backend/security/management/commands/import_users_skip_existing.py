import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from security.models import UserVerification


class Command(BaseCommand):
    help = (
        "Import auth.User and security.UserVerification from a dumpdata JSON file. "
        "Skips any username that already exists on this database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture_path",
            type=str,
            help="Path to JSON file (from: dumpdata auth.user security.userverification)",
        )

    def handle(self, *args, **options):
        path = options["fixture_path"]
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except OSError as exc:
            raise CommandError(f"Cannot read {path}: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("Fixture must be a JSON list.")

        users = [row for row in data if row.get("model") == "auth.user"]
        verifications = [
            row for row in data if row.get("model") == "security.userverification"
        ]

        imported_users = 0
        skipped_users = 0
        pk_to_user: dict[int, User] = {}

        for entry in users:
            fields = entry["fields"]
            username = fields["username"]
            if User.objects.filter(username__iexact=username).exists():
                self.stdout.write(f"skip user {username} (already exists)")
                skipped_users += 1
                continue

            user = User(
                username=username,
                email=fields.get("email", ""),
                first_name=fields.get("first_name", ""),
                last_name=fields.get("last_name", ""),
                is_superuser=fields.get("is_superuser", False),
                is_staff=fields.get("is_staff", False),
                is_active=fields.get("is_active", True),
            )
            user.password = fields["password"]
            if fields.get("last_login"):
                user.last_login = parse_datetime(fields["last_login"])
            if fields.get("date_joined"):
                user.date_joined = parse_datetime(fields["date_joined"])
            user.save()
            pk_to_user[entry["pk"]] = user
            imported_users += 1
            self.stdout.write(self.style.SUCCESS(f"imported user {username}"))

        imported_verifications = 0
        skipped_verifications = 0
        for entry in verifications:
            user = pk_to_user.get(entry["fields"]["user"])
            if user is None:
                skipped_verifications += 1
                continue
            if UserVerification.objects.filter(user=user).exists():
                self.stdout.write(
                    f"skip verification for {user.username} (already exists)"
                )
                skipped_verifications += 1
                continue

            fields = entry["fields"]
            UserVerification.objects.create(
                user=user,
                is_email_verified=fields.get("is_email_verified", False),
                is_admin_approved=fields.get("is_admin_approved", False),
                is_admin_rejected=fields.get("is_admin_rejected", False),
                rejected_at=(
                    parse_datetime(fields["rejected_at"])
                    if fields.get("rejected_at")
                    else None
                ),
                token=fields.get("token"),
                token_date=(
                    parse_datetime(fields["token_date"])
                    if fields.get("token_date")
                    else None
                ),
                reset_token=fields.get("reset_token"),
                reset_token_date=(
                    parse_datetime(fields["reset_token_date"])
                    if fields.get("reset_token_date")
                    else None
                ),
            )
            imported_verifications += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Done: "
                f"{imported_users} users imported, {skipped_users} users skipped, "
                f"{imported_verifications} verifications imported, "
                f"{skipped_verifications} verifications skipped"
            )
        )
