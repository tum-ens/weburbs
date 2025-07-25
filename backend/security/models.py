from django.db import models
from django.contrib.auth.models import User


class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    token = models.UUIDField(null=True)
    token_date = models.DateTimeField(null=True)
