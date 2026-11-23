import json
import os

import requests
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, validate_name_http_response
from projects.models import (
    DSM,
    BuySellPrice,
    Commodity,
    Demand,
    Process,
    ProcessCommodity,
    Project,
    SimulationResult,
    SimulationResultStatus,
    Site,
    Storage,
    SupIm,
    TimeVarEff,
    Transmission,
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


def with_t0(values):
    """Prepend URBS t=0 placeholder row to stored timeseries values."""
    return [0.0] + list(values)


def urbs_timestep_count(steps) -> int:
    """Return full URBS timestep count including the t=0 placeholder row."""
    return len(steps) + 1


def resolve_timestep_range(
    config: dict, run_config: dict | None = None
) -> tuple[int, int]:
    """Return validated (timestep_from, timestep_to) inclusive indices."""
    total = config["c_timesteps"]
    run_config = run_config or {}
    t_from = run_config.get("timestep_from", 0)
    t_to = run_config.get("timestep_to", total - 1)
    try:
        t_from = int(t_from)
        t_to = int(t_to)
    except (TypeError, ValueError) as exc:
        raise BadRequest("Invalid timestep range") from exc
    if t_from < 0 or t_to >= total or t_from > t_to:
        raise BadRequest(
            f"Timestep range must satisfy 0 <= from <= to < {total} "
            f"(got from={t_from}, to={t_to})"
        )
    return t_from, t_to


def build_project_config(project: Project):
    sites = Site.objects.filter(project=project)
    commodities = Commodity.objects.filter(site__in=sites)
    supims = SupIm.objects.filter(commodity__in=commodities)
    demands = Demand.objects.filter(commodity__in=commodities)
    timesteps = min(
        min(
            (urbs_timestep_count(supim.steps) for supim in supims),
            default=999999,
        ),
        min(
            (urbs_timestep_count(demand.steps) for demand in demands),
            default=999999,
        ),
    )

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
                        "supim": with_t0(
                            SupIm.objects.filter(commodity=commodity).get().steps
                        )
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
                        "timevareff": with_t0(
                            TimeVarEff.objects.filter(process=process).get().steps
                        )
                        if TimeVarEff.objects.filter(process=process).exists()
                        else None,
                    }
                    for process in Process.objects.filter(site=site)
                },
            }
            for site in sites
        },
        "buysellprice": {
            bsp.name: with_t0(bsp.steps)
            for bsp in BuySellPrice.objects.filter(project=project)
        }
        if BuySellPrice.objects.filter(project=project).exists()
        else None,
    }
    return remove_none(config)


@login_required
@require_GET
def get_simulation_info(request, project_name):
    project = get_project(request.user, project_name)
    config = build_project_config(project)
    return JsonResponse({"c_timesteps": config["c_timesteps"]})


@login_required
@require_POST
def trigger_simulation(request, project_name):
    fr_config = json.loads(request.body)

    project = get_project(request.user, project_name)

    simres = SimulationResult(project=project)
    config = build_project_config(project)
    simres.config = config
    simres.save()

    run_config = {
        "callback": os.getenv("URBS_CALLBACK", "http://localhost:8000")
        + f"/callback/simulation/{simres.id}/",
        "dir": f"{simres.timestamp.strftime('%Y%m%d')}/{simres.id}",
        "sim_id": str(simres.id),
    }
    if "generate_report" in fr_config:
        if fr_config["generate_report"] == "summary":
            run_config["generate_report"] = "summary"
        elif fr_config["generate_report"] == "full":
            run_config["generate_report"] = "full"
        else:
            raise BadRequest("Invalid generate_report")
    if fr_config.get("generate_h5"):
        run_config["generate_h5"] = True
    if "solver" in fr_config and fr_config["solver"] is not None:
        solver = fr_config["solver"]
        if solver not in ("gurobi", "glpk"):
            raise BadRequest("Invalid solver")
        run_config["solver"] = solver
    if "timeseries_commodity_types" in fr_config:
        allowed_types = {"Demand", "Buy", "Sell", "Env"}
        raw_types = fr_config.get("timeseries_commodity_types")
        if raw_types is None:
            run_config["timeseries_commodity_types"] = ["Demand"]
        elif not isinstance(raw_types, list):
            raise BadRequest("Invalid timeseries_commodity_types")
        else:
            cleaned = []
            for item in raw_types:
                if item not in allowed_types:
                    raise BadRequest("Invalid timeseries commodity type")
                if item not in cleaned:
                    cleaned.append(item)
            run_config["timeseries_commodity_types"] = cleaned
    if (
        fr_config.get("timestep_from") is not None
        or fr_config.get("timestep_to") is not None
    ):
        t_from = fr_config.get("timestep_from", 0)
        t_to = fr_config.get("timestep_to", config["c_timesteps"] - 1)
        t_from, t_to = resolve_timestep_range(
            config,
            {"timestep_from": t_from, "timestep_to": t_to},
        )
        run_config["timestep_from"] = t_from
        run_config["timestep_to"] = t_to

    config["run_config"] = run_config
    simres.config = config
    simres.save()

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
    result = [0.0] * timesteps
    for demand in demands:
        series = with_t0([step * demand.quantity for step in demand.steps])
        for i in range(min(timesteps, len(series))):
            result[i] += series[i]
    return result


def _find_callback_json(simres, simulation: dict) -> str | None:
    """Locate callback.json written by the optimizer on the shared result volume."""
    candidates = []
    subdir = simulation.get("result_subdir")
    if subdir:
        candidates.append(os.path.join("result", subdir, "callback.json"))
    candidates.append(
        os.path.join(
            "result",
            simres.timestamp.strftime("%Y%m%d"),
            str(simres.id),
            "callback.json",
        )
    )
    for path in candidates:
        if os.path.exists(path):
            return path

    sim_id = str(simres.id)
    result_root = "result"
    if not os.path.isdir(result_root):
        return None
    for date_dir in os.listdir(result_root):
        path = os.path.join(result_root, date_dir, sim_id, "callback.json")
        if os.path.exists(path):
            return path
    return None


def _load_simulation_callback(simres, simulation: dict) -> dict:
    """Merge optimizer POST body with callback.json on the shared result volume."""
    if not simulation.get("load_from_disk"):
        return simulation

    callback_path = _find_callback_json(simres, simulation)
    if not callback_path:
        print(
            f"callback.json missing for simulation {simres.id}; "
            f"checked result_subdir={simulation.get('result_subdir')!r}"
        )
        return simulation

    with open(callback_path, encoding="utf-8") as handle:
        on_disk = json.load(handle)
    return {
        "status": on_disk.get("status", simulation.get("status")),
        "log": on_disk.get("log", simulation.get("log", "")),
        "data": on_disk.get("data", simulation.get("data", {})),
    }


def _result_summary_for_db(data: dict) -> dict:
    """Keep heavy timeseries on disk; store only summary metadata in the database."""
    if not isinstance(data, dict) or not data.get("results"):
        return data
    return {
        "costs": data.get("costs"),
        "process": data.get("process"),
        "storage": data.get("storage"),
        "process_costs": data.get("process_costs"),
        "storage_costs": data.get("storage_costs"),
        "_timeseries_on_disk": True,
    }


def _merge_result_with_disk(simres, result: dict | None) -> dict:
    if not isinstance(result, dict) or not result.get("_timeseries_on_disk"):
        return result or {}

    callback_path = _find_callback_json(simres, {})
    if not callback_path:
        return result

    with open(callback_path, encoding="utf-8") as handle:
        on_disk = json.load(handle)
    full_data = on_disk.get("data") or {}
    merged = {**result, **full_data}
    merged.pop("_timeseries_on_disk", None)
    return merged


@csrf_exempt
@require_POST
def report_simulation(request, simid):
    try:
        simres = SimulationResult.objects.get(id=simid)
        if simres.completed:
            return HttpResponse("Result already reported", status="400")

        raw = json.loads(request.body)
        simulation = _load_simulation_callback(simres, raw)
        data = simulation.get("data") or {}
        print(
            f"report_simulation {simid}: "
            f"posted_status={raw.get('status')!r} "
            f"final_status={simulation.get('status')!r} "
            f"load_from_disk={raw.get('load_from_disk')} "
            f"result_subdir={raw.get('result_subdir')!r} "
            f"data_keys={list(data.keys()) if isinstance(data, dict) else 'n/a'}"
        )
        simres.completed = True
        simres.result = _result_summary_for_db(data)
        simres.log = simulation.get("log", "")
        if simulation["status"] == "optimal":
            simres.status = SimulationResultStatus.Optimal
        elif simulation["status"] == "infeasible":
            simres.status = SimulationResultStatus.Infeasible
        elif simulation["status"] == "cancelled":
            simres.status = SimulationResultStatus.Cancelled
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
        [
            {
                "id": res["id"],
                "timestamp": res["timestamp"],
                "name": res.get("name"),
                "completed": res["completed"],
                "status": res["status"],
            }
            for res in simres
        ],
        status=200,
        safe=False,
    )


@login_required
@require_GET
def get_simulation_progress(request, project_name, simid):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    result_dir = os.path.join(
        "result", simres.timestamp.strftime("%Y%m%d"), str(simres.id)
    )
    progress_path = os.path.join(result_dir, "progress.json")
    if os.path.exists(progress_path):
        with open(progress_path, encoding="utf-8") as handle:
            return JsonResponse(json.load(handle))

    if simres.completed:
        return HttpResponse("Simulation already completed", status="204")

    run_config = (simres.config or {}).get("run_config") or {}
    generate_report = run_config.get("generate_report")
    generate_h5 = bool(run_config.get("generate_h5"))
    steps = [
        {
            "id": "building_model",
            "label": "Building Pyomo model",
            "status": "in_progress",
        },
        {"id": "optimizing", "label": "Running optimization", "status": "pending"},
    ]
    if generate_report is not None:
        steps.append(
            {"id": "saving_xlsx", "label": "Saving Excel file", "status": "pending"}
        )
    if generate_h5:
        steps.append(
            {"id": "saving_h5", "label": "Saving h5 file", "status": "pending"}
        )
    steps.append(
        {
            "id": "preparing_dashboard",
            "label": "Preparing result dashboard",
            "status": "pending",
        }
    )
    return JsonResponse(
        {
            "steps": steps,
            "current_step": "building_model",
            "failed_at": None,
            "error_message": None,
            "progress_percent": 0,
        }
    )


@login_required
@require_GET
def get_simulation_result(request, project_name, simid):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    if not simres.completed:
        return HttpResponse("No result has been reported...", status="204")

    result_dir = os.path.join(
        "result", simres.timestamp.strftime("%Y%m%d"), str(simres.id)
    )
    xlsx = os.path.exists(os.path.join(result_dir, "result.xlsx"))
    h5 = os.path.exists(os.path.join(result_dir, "result.h5"))

    return JsonResponse(
        {
            "id": simres.id,
            "timestamp": simres.timestamp,
            "name": simres.name,
            "completed": simres.completed,
            "status": simres.status,
            "result": _merge_result_with_disk(simres, simres.result),
            "xlsx": xlsx,
            "h5": h5,
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
@require_GET
def download_simulation_result(request, project_name, simid, file):
    project = get_project(request.user, project_name)

    simres = SimulationResult.objects.get(id=simid, project=project)

    result_dir = os.path.join(
        "result", simres.timestamp.strftime("%Y%m%d"), str(simres.id)
    )

    if file == "xlsx":
        file_path = os.path.join(result_dir, "result.xlsx")
        if not os.path.exists(file_path):
            return BadRequest("No xlsx file found")
        return FileResponse(open(file_path, "rb"), as_attachment=True)
    elif file == "h5":
        file_path = os.path.join(result_dir, "result.h5")
        if not os.path.exists(file_path):
            return BadRequest("No h5 file found")
        return FileResponse(open(file_path, "rb"), as_attachment=True)
    elif file == "ilp":
        file_path = os.path.join(result_dir, "model.ilp")
        if not os.path.exists(file_path):
            return HttpResponse("No IIS file found", status=404)
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename="model.ilp"
        )

    return BadRequest("Invalid file")


@login_required
@require_POST
def compute_simulation_iis(request, project_name, simid):
    """Ask the optimizer to compute an IIS (model.ilp) for an infeasible run."""
    project = get_project(request.user, project_name)

    try:
        simres = SimulationResult.objects.get(id=simid, project=project)
    except SimulationResult.DoesNotExist:
        return JsonResponse({"detail": "Simulation not found"}, status=404)

    if simres.status != SimulationResultStatus.Infeasible:
        return JsonResponse(
            {"detail": "An IIS can only be computed for infeasible simulations."},
            status=400,
        )
    if not simres.config:
        return JsonResponse(
            {"detail": "Simulation config is unavailable; cannot compute IIS."},
            status=400,
        )

    compute_url = f"{_optimizer_base_url()}/compute_iis"
    try:
        response = requests.post(compute_url, json=simres.config, timeout=600)
    except requests.RequestException as exc:
        return JsonResponse({"detail": f"Could not reach optimizer: {exc}"}, status=502)

    if response.status_code != 200:
        detail = "Failed to compute IIS"
        try:
            detail = response.json().get("detail", detail)
        except ValueError:
            pass
        return JsonResponse({"detail": detail}, status=400)

    ilp_path = os.path.join(_simulation_result_dir(simres), "model.ilp")
    content = ""
    if os.path.exists(ilp_path):
        with open(ilp_path, encoding="utf-8", errors="replace") as handle:
            content = handle.read()

    return JsonResponse({"detail": "IIS computed", "content": content})


@login_required
@require_POST
def update_simulation_name(request, project_name, simid, name=None):
    project = get_project(request.user, project_name)

    if name is not None:
        err = validate_name_http_response(name, "Simulation name")
        if err:
            return err

    simres = SimulationResult.objects.get(id=simid, project=project)

    if simres is None:
        return HttpResponse("Simulation not found", status="204")

    simres.name = name
    simres.save()
    return HttpResponse("Name was updated")


def _optimizer_base_url():
    urbs_url = os.getenv("URBS", "http://localhost:5000/simulate")
    if urbs_url.endswith("/simulate"):
        return urbs_url[: -len("/simulate")]
    return urbs_url.rstrip("/")


def _simulation_result_dir(simres) -> str:
    return os.path.join("result", simres.timestamp.strftime("%Y%m%d"), str(simres.id))


def _cancel_progress_file(simres) -> None:
    result_dir = _simulation_result_dir(simres)
    progress_path = os.path.join(result_dir, "progress.json")
    if os.path.exists(progress_path):
        with open(progress_path, encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        run_config = (simres.config or {}).get("run_config") or {}
        generate_report = run_config.get("generate_report")
        generate_h5 = bool(run_config.get("generate_h5"))
        steps = [
            {
                "id": "building_model",
                "label": "Building Pyomo model",
                "status": "cancelled",
            },
            {
                "id": "optimizing",
                "label": "Running optimization",
                "status": "cancelled",
            },
        ]
        if generate_report is not None:
            steps.append(
                {
                    "id": "saving_xlsx",
                    "label": "Saving Excel file",
                    "status": "cancelled",
                }
            )
        if generate_h5:
            steps.append(
                {"id": "saving_h5", "label": "Saving h5 file", "status": "cancelled"}
            )
        steps.append(
            {
                "id": "preparing_dashboard",
                "label": "Preparing result dashboard",
                "status": "cancelled",
            }
        )
        data = {
            "steps": steps,
            "current_step": None,
            "failed_at": None,
            "error_message": "Simulation stopped.",
            "progress_percent": 0,
            "cancelled": True,
        }
        os.makedirs(result_dir, exist_ok=True)
        with open(progress_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle)
        return

    if data.get("cancelled"):
        return

    for step in data.get("steps", []):
        if step.get("status") in ("in_progress", "pending"):
            step["status"] = "cancelled"
    data["current_step"] = None
    data["cancelled"] = True
    data["error_message"] = "Simulation stopped."
    completed = sum(1 for step in data["steps"] if step.get("status") == "completed")
    data["progress_percent"] = max(
        0, min(100, int((completed / max(len(data["steps"]), 1)) * 100))
    )
    with open(progress_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)


def stop_simulation_record(simres) -> None:
    """Stop an in-progress simulation in the optimizer and mark it cancelled."""
    if simres.completed:
        return

    stop_url = f"{_optimizer_base_url()}/simulate/stop/{simres.id}/"
    try:
        requests.post(stop_url, timeout=15)
    except requests.RequestException:
        pass

    try:
        _cancel_progress_file(simres)
    except (OSError, PermissionError, json.JSONDecodeError, TypeError, ValueError):
        pass

    simres.completed = True
    simres.status = SimulationResultStatus.Cancelled
    if simres.result is None:
        simres.result = {}
    simres.log = (simres.log or "") + "\nSimulation stopped."
    simres.save()


@login_required
@require_POST
def stop_simulation(request, project_name, simid):
    project = get_project(request.user, project_name)

    try:
        simres = SimulationResult.objects.get(id=simid, project=project)
    except SimulationResult.DoesNotExist:
        return JsonResponse({"detail": "Simulation not found"}, status=404)

    if simres.completed:
        return JsonResponse({"detail": "Simulation already finished"}, status=400)

    try:
        stop_simulation_record(simres)
    except Exception as exc:  # noqa: BLE001
        print(f"stop_simulation {simid} failed: {exc}")
        return JsonResponse(
            {"detail": f"Could not stop simulation: {exc}"},
            status=500,
        )

    return JsonResponse({"detail": "Simulation stopped"})


def remove_none(d):
    if isinstance(d, dict):
        return {k: remove_none(v) for k, v in d.items() if v is not None}
    else:
        return d
