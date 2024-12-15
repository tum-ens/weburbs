import json
import threading

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_GET

from projects.api import process, commodity, storage
from projects.api.helper import get_project
from projects.api.supim import querySolar, queryWind
from projects.models import (
    Site,
    DefCommodity,
    Commodity,
    AutoQuery,
    SupIm,
    DefProcess,
    DefStorage,
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

    try:
        site = Site.objects.get(project=project, name=site_name)

        if request.method == "POST":
            site.name = data["name"]
            site.area = data["area"] if "area" in data else None
            site.lon = data["lon"]
            site.lat = data["lat"]
            site.save()

            threading.Thread(target=reload_supim, args=[site]).start()
            return JsonResponse({"detail": "Site updated"})
        elif request.method == "DELETE":
            site.delete()
            return JsonResponse({"detail": "Site deleted"})
        else:
            return HttpResponseNotAllowed(["POST", "DELETE"])
    except Site.DoesNotExist:
        if request.method == "POST":
            site = Site(
                project=project,
                name=data["name"],
                area=data["area"] if "area" in data else None,
                lon=data["lon"],
                lat=data["lat"],
            )
            site.save()

            for def_com in DefCommodity.objects.filter(autoadd=True).all():
                commodity.add_def_to_project(def_com, site)
            for def_proc in DefProcess.objects.filter(autoadd=True).all():
                print("found one")
                process.add_def_to_project(def_proc, site)
            for def_stor in DefStorage.objects.filter(autoadd=True).all():
                storage.add_def_to_project(def_stor, site)

            return JsonResponse({"detail": "Site created"})
        else:
            return HttpResponseNotAllowed(["POST", "DELETE"])


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
