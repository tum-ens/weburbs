import json
import re

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
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
    Site,
    Storage,
    SupIm,
    TimeVarEff,
    Transmission,
)


@login_required
@require_GET
def list_projects(request):
    projects = (
        Project.objects.filter(user=request.user)
        .order_by("name")
        .values("name", "description")
    )

    return JsonResponse(list(projects), safe=False)


@login_required
@require_GET
def project_details(request, project_name):
    project = get_project(request.user, project_name)

    return JsonResponse(
        {
            "name": project.name,
            "description": project.description,
            "co2limit": project.co2limit,
            "costlimit": project.costlimit,
        },
        safe=False,
    )


@login_required
@require_POST
def update_project(request, project_name):
    data = json.loads(request.body)

    err = validate_name_http_response(data.get("name"), "Project name")
    if err:
        return err

    if (
        data["name"] != project_name
        and Project.objects.filter(user=request.user, name=data["name"]).exists()
    ):
        return HttpResponse("A project with this name already exists", status=409)
    if data["name"] == "__new":
        return HttpResponse("Invalid name", status=400)

    try:
        project = Project.objects.get(user=request.user, name=project_name)
        project.name = data["name"]
        project.description = data["description"]
        project.co2limit = data["co2limit"]
        project.costlimit = data["costlimit"]
        project.save()
    except Project.DoesNotExist:
        (
            Project(
                user=request.user,
                name=data["name"],
                description=data["description"],
                co2limit=data["co2limit"],
                costlimit=data["costlimit"],
            ).save()
        )

    return JsonResponse({"detail": "Project created"})


@login_required
@require_POST
def delete_project(request, project_name):
    project = get_project(request.user, project_name)
    project.delete()

    return JsonResponse({"detail": "Project delete"})


def _clone_instance(instance, model, **overrides):
    """Create a new row from an existing instance, regenerating the primary key.

    All concrete (non-pk) fields are copied; foreign keys can be remapped via
    *overrides* using their attname (e.g. site_id=...).
    """
    data = {
        field.attname: getattr(instance, field.attname)
        for field in instance._meta.concrete_fields
        if not field.primary_key
    }
    data.update(overrides)
    clone = model(**data)
    clone.save()
    return clone


@login_required
@require_POST
def duplicate_project(request, project_name):
    source = get_project(request.user, project_name)

    # Derive a scenario name from the base project name (strip an existing
    # _Scenario_N suffix so duplicating a scenario yields the next one).
    base_name = re.sub(r"_Scenario_\d+$", "", source.name)
    counter = 1
    new_name = f"{base_name}_Scenario_{counter}"
    while Project.objects.filter(user=request.user, name=new_name).exists():
        counter += 1
        new_name = f"{base_name}_Scenario_{counter}"

    with transaction.atomic():
        new_project = _clone_instance(source, Project, name=new_name)

        commodity_map = {}
        process_map = {}

        for site in Site.objects.filter(project=source):
            new_site = _clone_instance(site, Site, project_id=new_project.id)

            for commodity in Commodity.objects.filter(site=site):
                new_com = _clone_instance(commodity, Commodity, site_id=new_site.id)
                commodity_map[commodity.id] = new_com

                for demand in Demand.objects.filter(commodity=commodity):
                    _clone_instance(demand, Demand, commodity_id=new_com.id)
                for supim in SupIm.objects.filter(commodity=commodity):
                    _clone_instance(supim, SupIm, commodity_id=new_com.id)
                for dsm in DSM.objects.filter(commodity=commodity):
                    _clone_instance(dsm, DSM, commodity_id=new_com.id)

            for proc in Process.objects.filter(site=site):
                new_proc = _clone_instance(proc, Process, site_id=new_site.id)
                process_map[proc.id] = new_proc

                for tve in TimeVarEff.objects.filter(process=proc):
                    _clone_instance(tve, TimeVarEff, process_id=new_proc.id)

        # Storage links a site and a commodity (both now duplicated).
        for storage in Storage.objects.filter(site__project=source):
            new_com = commodity_map.get(storage.commodity_id)
            if new_com is None:
                continue
            _clone_instance(
                storage,
                Storage,
                site_id=new_com.site_id,
                commodity_id=new_com.id,
            )

        # ProcessCommodity links a process and a commodity.
        for old_proc_id, new_proc in process_map.items():
            for pc in ProcessCommodity.objects.filter(process_id=old_proc_id):
                new_com = commodity_map.get(pc.commodity_id)
                if new_com is None:
                    continue
                _clone_instance(
                    pc,
                    ProcessCommodity,
                    process_id=new_proc.id,
                    commodity_id=new_com.id,
                )

        # Transmission links two commodities within the project.
        for trans in Transmission.objects.filter(
            commodityin_id__in=commodity_map.keys()
        ):
            new_in = commodity_map.get(trans.commodityin_id)
            new_out = commodity_map.get(trans.commodityout_id)
            if new_in is None or new_out is None:
                continue
            _clone_instance(
                trans,
                Transmission,
                commodityin_id=new_in.id,
                commodityout_id=new_out.id,
            )

        for bsp in BuySellPrice.objects.filter(project=source):
            _clone_instance(bsp, BuySellPrice, project_id=new_project.id)

    return JsonResponse({"detail": "Project duplicated", "new_name": new_name})
