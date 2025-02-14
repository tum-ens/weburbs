import uuid
from enum import IntEnum

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    co2limit = models.BigIntegerField(null=False)
    costlimit = models.BigIntegerField(null=False)


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
    area = models.IntegerField(null=True)
    lon = models.DecimalField(null=False, decimal_places=9, max_digits=12)
    lat = models.DecimalField(null=False, decimal_places=9, max_digits=12)


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


class AutoQuery(IntEnum):
    Solar = 1
    Wind = 2

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class CommodityTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.IntegerField(choices=ComType.choices(), null=False)
    price = models.FloatField(null=True)
    max = models.FloatField(null=True)
    maxperhour = models.FloatField(null=True)
    unitR = models.TextField(null=False)
    unitC = models.TextField(null=False)

    def get_com_type_label(self):
        return ComType(self.type).name

    class Meta:
        abstract = True


class DefCommodity(CommodityTypes):
    name = models.CharField(max_length=255, null=False, unique=True)
    autoquery = models.IntegerField(choices=AutoQuery.choices(), null=True)
    autoadd = models.BooleanField(default=False)


class Commodity(CommodityTypes):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False, unique=False)
    defcommodity = models.ForeignKey(
        DefCommodity, on_delete=models.SET_NULL, null=True, related_name="usages"
    )


class ProcessTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    instcap = models.FloatField(null=False)
    caplo = models.FloatField(null=False)
    capup = models.FloatField(null=False)
    maxgrad = models.FloatField(null=False)
    minfraction = models.FloatField(null=False)
    invcost = models.FloatField(null=False)
    fixcost = models.FloatField(null=False)
    varcost = models.FloatField(null=False)
    wacc = models.FloatField(null=False)
    depreciation = models.FloatField(null=False)
    areapercap = models.FloatField(null=True)

    class Meta:
        abstract = True


class DefProcess(ProcessTypes):
    autoadd = models.BooleanField(default=False)


class Process(ProcessTypes):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=False)


class ProcComDir(IntEnum):
    In = 1
    Out = 2

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ProcessCommodityTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    direction = models.IntegerField(choices=ProcComDir.choices(), null=False)
    ratio = models.FloatField(null=False)
    ratiomin = models.FloatField(null=True)

    def get_direction_type_label(self):
        return ProcComDir(self.direction).name

    class Meta:
        abstract = True


class DefProcessCommodity(ProcessCommodityTypes):
    def_commodity = models.ForeignKey(
        DefCommodity, on_delete=models.CASCADE, null=False
    )
    def_process = models.ForeignKey(DefProcess, on_delete=models.CASCADE, null=False)


class ProcessCommodity(ProcessCommodityTypes):
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=False)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=False)


class StorageType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    instcapc = models.IntegerField(null=False)
    caploc = models.IntegerField(null=False)
    capupc = models.IntegerField(null=False)
    instcapp = models.IntegerField(null=False)
    caplop = models.IntegerField(null=False)
    capupp = models.IntegerField(null=False)
    effin = models.FloatField(null=False)
    effout = models.FloatField(null=False)
    invcostp = models.IntegerField(null=False)
    invcostc = models.FloatField(null=False)
    fixcostp = models.IntegerField(null=False)
    fixcostc = models.FloatField(null=False)
    varcostp = models.FloatField(null=False)
    varcostc = models.IntegerField(null=False)
    wacc = models.FloatField(null=False)
    depreciation = models.IntegerField(null=False)
    init = models.FloatField(null=False)
    discharge = models.FloatField(null=False)
    epratio = models.FloatField(null=True)

    class Meta:
        abstract = True


class DefStorage(StorageType):
    def_commodity = models.ForeignKey(
        DefCommodity, on_delete=models.CASCADE, null=False
    )
    autoadd = models.BooleanField(default=False)


class Storage(StorageType):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=False)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=False)


class DemandType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    steps = models.JSONField(null=False)

    class Meta:
        abstract = True


class DefDemand(DemandType):
    pass


class Demand(DemandType):
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=False)
    defdemand = models.ForeignKey(
        DefDemand, on_delete=models.SET_NULL, null=True, related_name="usages"
    )
    quantity = models.IntegerField(null=False)


class SupImType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    steps = models.JSONField(null=False)

    class Meta:
        abstract = True


class DefSupIm(SupImType):
    pass


class SupIm(SupImType):
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=False)
    defsupim = models.ForeignKey(
        DefSupIm, on_delete=models.SET_NULL, null=True, related_name="usages"
    )


class TransType(IntEnum):
    hvac = 1

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Transmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sitein = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        null=False,
        related_name="incoming_transmissions",
    )
    siteout = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        null=False,
        related_name="outgoing_transmissions",
    )
    transmission = models.IntegerField(choices=TransType.choices(), null=False)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=False)
    eff = models.FloatField(null=False)
    invcost = models.IntegerField(null=False)
    fixcost = models.IntegerField(null=False)
    varcost = models.FloatField(null=False)
    instcap = models.IntegerField(null=False)
    caplo = models.IntegerField(null=False)
    capup = models.IntegerField(null=False)
    wacc = models.FloatField(null=False)
    depreciation = models.FloatField(null=False)
    reactance = models.FloatField(null=False)
    difflimit = models.FloatField(null=False)
    basevoltage = models.FloatField(null=False)

    def get_trans_type_label(self):
        return ComType(self.transmission).name


class BuySellPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=False)
    buy = models.JSONField(null=False)
    sell = models.JSONField(null=False)


class TimeVarEff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=False)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=False)
    steps = models.FloatField(null=False)


class SimulationResultStatus(IntEnum):
    Optimal = 1
    Infeasible = 2
    Error = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SimulationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(null=False, auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    completed = models.BooleanField(default=False)
    config = models.JSONField(null=False)
    status = models.IntegerField(choices=SimulationResultStatus.choices(), null=True)
    result = models.JSONField(null=True)
    log = models.TextField(null=True)
