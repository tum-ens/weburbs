from django.db import migrations, models
from django.utils import timezone


def set_rejected_at_for_existing(apps, schema_editor):
    UserVerification = apps.get_model("security", "UserVerification")
    now = timezone.now()
    UserVerification.objects.filter(
        is_admin_rejected=True, rejected_at__isnull=True
    ).update(rejected_at=now)


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0003_userverification_is_admin_rejected"),
    ]

    operations = [
        migrations.AddField(
            model_name="userverification",
            name="rejected_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(set_rejected_at_for_existing, migrations.RunPython.noop),
    ]
