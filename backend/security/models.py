from django.contrib.auth.models import User
from django.db import models


class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    is_admin_approved = models.BooleanField(default=False)
    is_admin_rejected = models.BooleanField(default=False)
    rejected_at = models.DateTimeField(null=True, blank=True)
    token = models.UUIDField(null=True)
    token_date = models.DateTimeField(null=True)
    reset_token = models.UUIDField(null=True, blank=True)
    reset_token_date = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
