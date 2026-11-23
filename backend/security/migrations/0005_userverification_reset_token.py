from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0004_userverification_rejected_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="userverification",
            name="reset_token",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userverification",
            name="reset_token_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
