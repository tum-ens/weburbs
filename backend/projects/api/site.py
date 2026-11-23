import json
import threading

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api import commodity, process, storage
from projects.api.helper import get_project, get_site, validate_name_http_response
from projects.api.supim import querySolar, queryWind
from projects.models import (
    AutoQuery,
    Commodity,
    DefCommodity,
    DefProcess,
    DefStorage,
    Site,
    SupIm,
)


@login_required
@require_GET
def list_sites(request, project_name):
    project = get_project(request.user, project_name)
    sites = (
        Site.objects.filter(project=project)
        .order_by("name")
        .values("name", "area", "lon", "lat")
    )

    return JsonResponse(list(sites), safe=False)


@login_required
@require_POST
def edit_site(request, project_name, site_name):
    project = get_project(request.user, project_name)
    data = json.loads(request.body)

    err = validate_name_http_response(data.get("name"), "Site name")
    if err:
        return err

    try:
        site = Site.objects.get(project=project, name=site_name)

        site.name = data["name"]
        site.area = data.get("area")
        site.lon = data["lon"]
        site.lat = data["lat"]
        site.save()

        threading.Thread(target=reload_supim, args=[site]).start()
        return JsonResponse({"detail": "Site updated"})
    except Site.DoesNotExist:
        site = Site(
            project=project,
            name=data["name"],
            area=data.get("area"),
            lon=data["lon"],
            lat=data["lat"],
        )
        site.save()

        for def_com in DefCommodity.objects.filter(autoadd=True).all():
            commodity.add_def_to_project(def_com, site)
        for def_proc in DefProcess.objects.filter(autoadd=True).all():
            process.add_def_to_project(def_proc, site)
        for def_stor in DefStorage.objects.filter(autoadd=True).all():
            storage.add_def_to_project(def_stor, site)

        return JsonResponse({"detail": "Site created"})


@login_required
@require_POST
def delete_site(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    site.delete()
    return JsonResponse({"detail": "Site deleted"})


def reload_supim(site: Site):
    commodities = Commodity.objects.filter(site=site)
    for com in commodities:
        def_commodity = com.defcommodity
        if def_commodity is not None and def_commodity.autoquery is not None:
            if SupIm.objects.filter(commodity=com).exists():
                SupIm.objects.get(commodity=com).delete()
            if def_commodity.autoquery == AutoQuery.Solar:
                querySolar(site, com)
            elif def_commodity.autoquery == AutoQuery.Wind:
                queryWind(site, com)
