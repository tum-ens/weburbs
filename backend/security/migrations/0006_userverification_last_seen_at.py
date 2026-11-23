from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("security", "0005_userverification_reset_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="userverification",
            name="last_seen_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
