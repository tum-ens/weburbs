import uuid
from enum import IntEnum

from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

class Global(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    property = models.CharField(max_length=255, null=False)
    value = models.IntegerField(null=False)

class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False, unique=True)
    area = models.IntegerField(null=False)
    long = models.FloatField(null=False)
    lat = models.FloatField(null=False)

class ComType(IntEnum):
    SupIm = 1
    Demand = 2
    Stock = 3
    Env = 4
    Buy = 5
    Sell = 6

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Commodity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
    type = models.IntegerField(choices=ComType.choices(), null=False)
    price = models.IntegerField(null=False)
    max = models.IntegerField(null=False)
    maxperhour = models.IntegerField(null=False)

    def get_com_type_label(self):
        return ComType(self.type).name.title()


