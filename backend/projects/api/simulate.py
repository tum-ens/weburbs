import json
import os

import requests
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from projects.api.helper import get_project
from projects.models import (
    Site,
    Commodity,
    Process,
    ProcessCommodity,
    SupIm,
    Demand,
    Storage,
    SimulationResult,
    SimulationResultStatus,
    DSM,
    TimeVarEff,
    BuySellPrice,
    Transmission,
    Project,
)


def negInf(n):
    return n if n >= 0 else "inf"


def create_dsm_config(commodity: Commodity):
    if not DSM.objects.filter(commodity=commodity).exists():
        return None
    dsm = DSM.objects.get(commodity=commodity)
    return {
        "delay": dsm.delay,
        "eff": dsm.eff,
        "recov": dsm.recov,
        "cap-max-do": dsm.capmaxdo,
        "cap-max-up": dsm.capmaxup,
    }


def create_transmission_config(commodity: Commodity):
    transmissions = Transmission.objects.filter(commodityout=commodity)
    if len(transmissions) == 0:
        return None
    transmission_config = {}
    for transmission in transmissions:
        site_name = transmission.commodityin.site.name
        transmission_config[site_name] = {
            "Transmission": transmission.get_trans_type_label(),
            "eff": transmission.eff,
            "inv-cost": transmission.invcost,
            "fix-cost": transmission.fixcost,
            "var-cost": transmission.varcost,
            "inst-cap": transmission.instcap,
            "cap-lo": transmission.caplo,
            "cap-up": negInf(transmission.capup),
            "wacc": transmission.wacc,
            "depreciation": transmission.depreciation,
            "reactance": transmission.reactance,
            "difflimit": transmission.difflimit,
            "basevoltage": transmission.basevoltage,
        }
    return transmission_config


def create_buysellprice_config(project: Project):
    buysellprices = BuySellPrice.objects.filter(project=project)
    if len(buysellprices) == 0:
        return None
    buysellprice_config = {}
    for bsp in buysellprices:
        buysellprice_config[bsp.name] = bsp.steps
    return buysellprice_config


@login_required
@require_POST
def trigger_simulation(request, project_name):
    fr_config = json.loads(request.body)

    project = get_project(request.user, project_name)
    sites = Site.objects.filter(project=project)
    commodities = Commodity.objects.filter(site__in=sites)
    supims = SupIm.objects.filter(commodity__in=commodities)
    demands = Demand.objects.filter(commodity__in=commodities)
    timesteps = min(
        min(map(lambda supim: len(supim.steps), supims), default=999999),
        min(map(lambda demand: len(demand.steps), demands), default=999999),
    )

    simres = SimulationResult(project=project)
    config = {
        "c_timesteps": timesteps,
        "global": {"CO2 limit": project.co2limit, "Cost limit": project.costlimit},
        "site": {
            site.name: {
                "area": "NaN" if site.area is None else site.area,
                "lat": str(site.lat),
                "lon": str(site.lon),
                "commodity": {
                    commodity.name: {
                        "Type": commodity.get_com_type_label(),
                        "price": commodity.price,
                        "max": None if commodity.max is None else negInf(commodity.max),
                        "maxperhour": None
                        if commodity.maxperhour is None
                        else negInf(commodity.maxperhour),
                        "supim": SupIm.objects.filter(commodity=commodity).get().steps
                        if SupIm.objects.filter(commodity=commodity).exists()
                        else None,
                        "demand": calculateDemand(
                            timesteps,
                            list(Demand.objects.filter(commodity=commodity).all()),
                        )
                        if Demand.objects.filter(commodity=commodity).exists()
                        else None,
                        "storage": {
                            storage.name: {
                                "description": storage.description,
                                "inst-cap-c": storage.instcapc,
                                "cap-lo-c": storage.caploc,
                                "cap-up-c": negInf(storage.capupc),
                                "inst-cap-p": storage.instcapp,
                                "cap-lo-p": storage.caplop,
                                "cap-up-p": negInf(storage.capupp),
                                "eff-in": storage.effin,
                                "eff-out": storage.effout,
                                "inv-cost-p": storage.invcostp,
                                "inv-cost-c": storage.invcostc,
                                "fix-cost-p": storage.fixcostp,
                                "fix-cost-c": storage.fixcostc,
                                "var-cost-p": storage.varcostp,
                                "var-cost-c": storage.varcostc,
                                "wacc": storage.wacc,
                                "depreciation": storage.depreciation,
                                "init": storage.init,
                                "discharge": storage.discharge,
                                "ep-ratio": storage.epratio,
                            }
                            for storage in Storage.objects.filter(
                                commodity=commodity
                            ).all()
                        }
                        if Storage.objects.filter(commodity=commodity).exists()
                        else None,
                        "dsm": create_dsm_config(commodity),
                        "unitR": commodity.unitR,
                        "unitC": commodity.unitC,
                        "transmission": create_transmission_config(commodity),
                    }
                    for commodity in Commodity.objects.filter(site=site)
                },
                "process": {
                    process.name: {
                        "description": process.description,
                        "inst-cap": process.instcap,
                        "cap-lo": process.caplo,
                        "cap-up": negInf(process.capup),
                        "max-grad": negInf(process.maxgrad),
                        "min-fraction": process.minfraction,
                        "inv-cost": process.invcost,
                        "fix-cost": process.fixcost,
                        "var-cost": process.varcost,
                        "wacc": process.wacc,
                        "depreciation": process.depreciation,
                        "area-per-cap": process.areapercap,
                        "commodity": {
                            proccom.commodity.name: {
                                "Direction": proccom.get_direction_type_label(),
                                "ratio": proccom.ratio,
                                "ratio-min": proccom.ratiomin,
                            }
                            for proccom in ProcessCommodity.objects.filter(
                                process=process
                            )
                        },
                        "timevareff": TimeVarEff.objects.filter(process=process)
                        .get()
                        .steps
                        if TimeVarEff.objects.filter(process=process).exists()
                        else None,
                    }
                    for process in Process.objects.filter(site=site)
                },
            }
            for site in sites
        },
        "buysellprice": {
            bsp.name: bsp.steps for bsp in BuySellPrice.objects.filter(project=project)
        }
        if BuySellPrice.objects.filter(project=project).exists()
        else None,
    }
    config = remove_none(config)
    simres.config = config
    simres.save()

    run_config = {}
    run_config["callback"] = (
        os.getenv("URBS_CALLBACK", "http://localhost:8000")
        + f"/callback/simulation/{simres.id}/"
    )
    if "generate_report" in fr_config:
        if fr_config["generate_report"] == "summary":
            run_config["generate_report"] = "summary"
        elif fr_config["generate_report"] == "full":
            run_config["generate_report"] = "full"
        else:
            raise BadRequest("Invalid generate_report")
    if "generate_h5" in fr_config:
        if fr_config["generate_h5"]:
            run_config["generate_h5"] = True

    config["run_config"] = run_config

    response = requests.post(
        os.getenv("URBS", "http://localhost:5000/simulate"), json=config
    )
    if response.status_code != 200:
        print(response.text)
        return HttpResponse("Simulation failed", status="400")

    return JsonResponse(
        {"id": simres.id, "timestamp": simres.timestamp, "completed": False}
    )


def calculateDemand(timesteps, demands):
    result = [0] * timesteps
    for demand in demands:
        for i in range(timesteps):
            result[i] += demand.steps[i] * demand.quantity
    return result


@csrf_exempt
@require_POST
def report_simulation(request, simid):
    try:
        simres = SimulationResult.objects.get(id=simid)
        if simres.result is not None:
            return HttpResponse("Result already reported", status="400")

        simulation = json.loads(request.body)
        simres.completed = True
        simres.result = simulation["data"]
        simres.log = simulation["log"]
        if simulation["status"] == "optimal":
            simres.status = SimulationResultStatus.Optimal
        elif simulation["status"] == "infeasible":
            simres.status = SimulationResultStatus.Infeasible
        else:
            simres.status = SimulationResultStatus.Error
        simres.save()
        return HttpResponse("Simulation saved", status="200")
    except SimulationResult.DoesNotExist:
        return HttpResponse("Invalid simid", status="401")


@login_required
@require_GET
def get_simulations(request, project_name):
    project = get_project(request.user, project_name)

    simres = (
        SimulationResult.objects.filter(project=project)
        .order_by("timestamp")
        .reverse()
        .values("id", "timestamp", "name", "completed", "status")
    )
    return JsonResponse(
        list(
            map(
                lambda res: {
                    "id": res["id"],
                    "timestamp": res["timestamp"],
                    "name": res["name"] if "name" in res else None,
                    "completed": res["completed"],
                    "status": res["status"],
                },
                simres,
            )
        ),
        status=200,
        safe=False,
    )


@login_required
@require_GET
def get_simulation_result(request, project_name, simid):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    if not simres.completed:
        return HttpResponse("No result has been reported...", status="204")

    return JsonResponse(
        {
            "id": simres.id,
            "timestamp": simres.timestamp,
            "name": simres.name,
            "completed": simres.completed,
            "status": simres.status,
            "result": simres.result,
        }
    )


@login_required
@require_GET
def get_simulation_logs(request, project_name, simid):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    if not simres.completed:
        return HttpResponse("No result has been reported...", status="204")

    return HttpResponse(simres.log)


@login_required
@require_GET
def get_simulation_config(request, project_name, simid):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    if simres is None:
        return HttpResponse("Simulation not found", status="204")

    return JsonResponse(simres.config)


@login_required
@require_POST
def update_simulation_name(request, project_name, simid, name=None):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    if simres is None:
        return HttpResponse("Simulation not found", status="204")

    simres.name = name
    simres.save()
    return HttpResponse("Name was updated")


def remove_none(d):
    if isinstance(d, dict):
        return {k: remove_none(v) for k, v in d.items() if v is not None}
    else:
        return d
