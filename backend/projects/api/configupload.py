import json
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from projects.models import (
    Project,
    Site,
    Commodity,
    ComType,
    Process,
    ProcessCommodity,
    ProcComDir,
    Storage,
    Demand,
    SupIm,
    Transmission,
    TransmissionType,
    DSM,
    BuySellPrice,
    TimeVarEff,
)


def parse_num(num):
    if num == "inf":
        return -1
    else:
        return num


def opt_num(obj, key):
    if key in obj:
        return parse_num(obj[key])
    else:
        return None


def default():
    return defaultdict(default)


@login_required
@require_POST
def upload(request, project_name):
    if Project.objects.filter(user=request.user, name=project_name).exists():
        return HttpResponse("Project name already exists", status=409)

    readConfig(request.user, project_name, json.loads(request.body))
    return HttpResponse("Project created")


def readConfig(user, project_name, config):
    if "CO2 limit" in config["global"]:
        co2limit = config["global"]["CO2 limit"]
    else:
        co2limit = 150000000
    if "Cost limit" in config["global"]:
        costlimit = config["global"]["Cost limit"]
    else:
        costlimit = 35000000000
    project = Project(
        user=user, name=project_name, co2limit=co2limit, costlimit=costlimit
    )
    project.save()

    for siteName, dataSite in config["site"].items():
        site = Site(
            project=project,
            name=siteName,
            area=None if dataSite["area"] == "NaN" else dataSite["area"],
            lat=dataSite["lat"],
            lon=dataSite["lon"],
        )
        site.save()

        for commodityName, dataCommodity in dataSite["commodity"].items():
            commodity = Commodity(
                name=commodityName,
                site=site,
                type=ComType[dataCommodity["Type"]],
                price=opt_num(dataCommodity, "price"),
                max=opt_num(dataCommodity, "max"),
                maxperhour=opt_num(dataCommodity, "maxperhour"),
                unitR=dataCommodity["unitR"],
                unitC=dataCommodity["unitC"],
            )
            commodity.save()

            if "supim" in dataCommodity:
                supim = SupIm(
                    name="",
                    commodity=commodity,
                    description="",
                    steps=dataCommodity["supim"],
                )
                supim.save()

            if "demand" in dataCommodity:
                demand = Demand(
                    name="imported",
                    commodity=commodity,
                    description="",
                    steps=dataCommodity["demand"],
                    quantity=1,
                )
                demand.save()

            if "storage" in dataCommodity:
                for storageName, dataStorage in dataCommodity["storage"].items():
                    storage = Storage(
                        site=site,
                        commodity=commodity,
                        name=storageName,
                        description=dataStorage["description"],
                        instcapc=dataStorage["inst-cap-c"],
                        caploc=dataStorage["cap-lo-c"],
                        capupc=opt_num(dataStorage, "cap-up-c"),
                        instcapp=dataStorage["inst-cap-p"],
                        caplop=dataStorage["cap-lo-p"],
                        capupp=opt_num(dataStorage, "cap-up-p"),
                        effin=dataStorage["eff-in"],
                        effout=dataStorage["eff-out"],
                        invcostp=dataStorage["inv-cost-p"],
                        invcostc=dataStorage["inv-cost-c"],
                        fixcostp=dataStorage["fix-cost-p"],
                        fixcostc=dataStorage["fix-cost-c"],
                        varcostp=dataStorage["var-cost-p"],
                        varcostc=dataStorage["var-cost-c"],
                        wacc=dataStorage["wacc"],
                        depreciation=dataStorage["depreciation"],
                        init=dataStorage["init"],
                        discharge=dataStorage["discharge"],
                        epratio=opt_num(dataStorage, "ep-ratio"),
                    )
                    storage.save()

            if "dsm" in dataCommodity:
                dataDSM = dataCommodity["dsm"]
                dsm = DSM(
                    commodity=commodity,
                    delay=dataDSM["delay"],
                    eff=dataDSM["eff"],
                    recov=dataDSM["recov"],
                    capmaxdo=dataDSM["cap-max-do"],
                    capmaxup=dataDSM["cap-max-up"],
                )
                dsm.save()

        for processName, processData in dataSite["process"].items():
            process = Process(
                name=processName,
                site=site,
                description=processData["description"],
                instcap=processData["inst-cap"],
                caplo=processData["cap-lo"],
                capup=opt_num(processData, "cap-up"),
                maxgrad=opt_num(processData, "max-grad"),
                minfraction=processData["min-fraction"],
                invcost=processData["inv-cost"],
                fixcost=processData["fix-cost"],
                varcost=processData["var-cost"],
                wacc=processData["wacc"],
                depreciation=processData["depreciation"],
                areapercap=opt_num(processData, "area-per-cap"),
            )
            process.save()

            for processCommodityName, processCommodityData in processData[
                "commodity"
            ].items():
                processCommodity = Commodity.objects.get(
                    site=site, name=processCommodityName
                )
                processCommodity = ProcessCommodity(
                    process=process,
                    commodity=processCommodity,
                    direction=ProcComDir[processCommodityData["Direction"]],
                    ratio=processCommodityData["ratio"],
                    ratiomin=opt_num(processCommodityData, "ratio-min"),
                )
                processCommodity.save()

            if "timevareff" in processData:
                timevareff = TimeVarEff(
                    process=process, steps=processData["timevareff"]
                )
                timevareff.save()

    for siteName, dataSite in config["site"].items():
        site = Site.objects.get(project=project, name=siteName)
        for commodityName, dataCommodity in dataSite["commodity"].items():
            commodity = Commodity.objects.get(site=site, name=commodityName)
            if "transmission" in dataCommodity:
                for siteinName, dataTransmission in dataCommodity[
                    "transmission"
                ].items():
                    sitein = Site.objects.get(project=project, name=siteinName)
                    commodityin = Commodity.objects.get(site=sitein, name=commodityName)
                    transmission = Transmission(
                        type=TransmissionType[dataTransmission["Transmission"]],
                        commodityout=commodity,
                        commodityin=commodityin,
                        eff=dataTransmission["eff"],
                        invcost=dataTransmission["inv-cost"],
                        fixcost=dataTransmission["fix-cost"],
                        varcost=dataTransmission["var-cost"],
                        instcap=dataTransmission["inst-cap"],
                        caplo=dataTransmission["cap-lo"],
                        capup=parse_num(dataTransmission["cap-up"]),
                        wacc=dataTransmission["wacc"],
                        depreciation=dataTransmission["depreciation"],
                        reactance=opt_num(dataTransmission, "reactance"),
                        difflimit=opt_num(dataTransmission, "difflimit"),
                        basevoltage=opt_num(dataTransmission, "basevoltage"),
                    )
                    transmission.save()

    if "buysellprice" in config:
        for commodityName, dataBuySellPrice in config["buysellprice"].items():
            buysellprice = BuySellPrice(
                project=project,
                name=commodityName,
                steps=dataBuySellPrice,
            )
            buysellprice.save()
