import json

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.models import (
    DefProcess,
    Process,
    Site,
    DefProcessCommodity,
    ProcComDir,
    ProcessCommodity,
    Commodity,
    DefCommodity,
)
from projects.api import commodity


@login_required
@require_GET
def list_def_processes(request):
    processes = DefProcess.objects.prefetch_related(
        Prefetch(
            "defprocesscommodity_set",
            queryset=DefProcessCommodity.objects.filter(direction=ProcComDir.In),
            to_attr="inCom",
        ),
        Prefetch(
            "defprocesscommodity_set",
            queryset=DefProcessCommodity.objects.filter(direction=ProcComDir.Out),
            to_attr="outCom",
        ),
    ).order_by("name")

    proclist = [
        {
            **model_to_dict(proc, exclude=["id"]),
            "in": [
                {
                    "name": proccom.def_commodity.name,
                    "ratio": proccom.ratio,
                    "ratiomin": proccom.ratiomin,
                }
                for proccom in proc.inCom
            ],
            "out": [
                {
                    "name": proccom.def_commodity.name,
                    "ratio": proccom.ratio,
                    "ratiomin": proccom.ratiomin,
                }
                for proccom in proc.outCom
            ],
        }
        for proc in processes
    ]
    return JsonResponse(proclist, safe=False)


@login_required
@require_GET
def list_processes(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    processes = (
        Process.objects.filter(site=site)
        .prefetch_related(
            Prefetch(
                "processcommodity_set",
                queryset=ProcessCommodity.objects.filter(direction=ProcComDir.In),
                to_attr="inCom",
            ),
            Prefetch(
                "processcommodity_set",
                queryset=ProcessCommodity.objects.filter(direction=ProcComDir.Out),
                to_attr="outCom",
            ),
        )
        .order_by("name")
    )

    proclist = [
        {
            **model_to_dict(proc, exclude=["id"]),
            "in": [
                {
                    "name": proccom.commodity.name,
                    "ratio": proccom.ratio,
                    "ratiomin": proccom.ratiomin,
                }
                for proccom in proc.inCom
            ],
            "out": [
                {
                    "name": proccom.commodity.name,
                    "ratio": proccom.ratio,
                    "ratiomin": proccom.ratiomin,
                }
                for proccom in proc.outCom
            ],
        }
        for proc in processes
    ]
    return JsonResponse(proclist, safe=False)


def add_def_to_project(def_process: DefProcess, site: Site):
    process = Process(
        site=site,
        name=def_process.name,
        description=def_process.description,
        instcap=def_process.instcap,
        caplo=def_process.caplo,
        capup=def_process.capup,
        maxgrad=def_process.maxgrad,
        minfraction=def_process.minfraction,
        invcost=def_process.invcost,
        fixcost=def_process.fixcost,
        varcost=def_process.varcost,
        wacc=def_process.wacc,
        depreciation=def_process.depreciation,
        areapercap=def_process.areapercap,
    )
    process.save()

    for def_proccom in DefProcessCommodity.objects.filter(def_process=def_process):
        def_com = def_proccom.def_commodity
        coms = def_com.usages.filter(site=site)
        if len(coms) > 1:
            return HttpResponse(
                "Internal error: more than one commodity references a default commodity",
                status=500,
            )

        if len(coms) == 1:
            com = coms[0]
        else:
            com = commodity.add_def_to_project(def_com, site)

        proccom = ProcessCommodity(
            commodity=com,
            process=process,
            direction=def_proccom.direction,
            ratio=def_proccom.ratio,
            ratiomin=def_proccom.ratiomin,
        )
        proccom.save()
    return process


@login_required
@require_POST
def add_def_process(request, project_name, site_name, def_proc_name):
    try:
        def_process = DefProcess.objects.get(name=def_proc_name)
    except DefProcess.DoesNotExist:
        return HttpResponse("Default process not found", status="404")

    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    if Process.objects.filter(site=site, name=def_proc_name).exists():
        return HttpResponse("Process with the same name already exists", status=409)

    # Start adding process and all process commodities
    add_def_to_project(def_process, site)

    return JsonResponse({"detail": "Process added"})


@login_required
@require_POST
def update_process(request, project_name, site_name, process_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    data = json.loads(request.body)

    if process_name != data["name"]:
        if Process.objects.filter(site=site, name=data["name"]).exists():
            return HttpResponse("Process with the same name already exists", status=409)

    try:
        process = Process.objects.get(site=site, name=process_name)
    except Process.DoesNotExist:
        process = Process(site=site)
    process.name = data["name"]
    process.description = data["description"]
    process.instcap = data["instcap"]
    process.caplo = data["caplo"]
    process.capup = data["capup"]
    process.maxgrad = data["maxgrad"]
    process.minfraction = data["minfraction"]
    process.invcost = data["invcost"]
    process.fixcost = data["fixcost"]
    process.varcost = data["varcost"]
    process.wacc = data["wacc"]
    process.depreciation = data["depreciation"]
    if "areapercap" in data:
        process.areapercap = data["areapercap"]
    else:
        del process.areapercap
    process.save()

    ProcessCommodity.objects.filter(process=process).delete()

    for in_proccom in data["in"]:
        try:
            com = Commodity.objects.get(site=site, name=in_proccom["name"])
        except Commodity.DoesNotExist:
            def_com = DefCommodity.objects.get(name=in_proccom["name"])
            com = commodity.add_def_to_project(def_com, site)
        ProcessCommodity(
            process=process,
            commodity=com,
            direction=ProcComDir.In,
            ratio=in_proccom["ratio"],
            ratiomin=in_proccom["ratiomin"],
        ).save()
    for out_proccom in data["out"]:
        try:
            com = Commodity.objects.get(site=site, name=out_proccom["name"])
        except Commodity.DoesNotExist:
            def_com = DefCommodity.objects.get(name=out_proccom["name"])
            com = commodity.add_def_to_project(def_com, site)
        (
            ProcessCommodity(
                process=process,
                commodity=com,
                direction=ProcComDir.Out,
                ratio=out_proccom["ratio"],
                ratiomin=out_proccom["ratiomin"],
            ).save()
        )

    return JsonResponse({"detail": "Process updated"})


@login_required
@require_POST
def delete_process(request, project_name, site_name, process_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    process = Process.objects.get(site=site, name=process_name)
    process.delete()

    return JsonResponse({"detail": "Process deleted"})
