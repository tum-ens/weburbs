import json
import threading

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.api.supim import querySolar, queryWind
from projects.models import Commodity, DefCommodity, Site, AutoQuery


@login_required
@require_GET
def list_def_commodities(request):
    commodities = (
        DefCommodity.objects.all()
        .order_by("name")
        .values("name", "type", "price", "max", "maxperhour", "unitR", "unitC")
    )

    return JsonResponse(list(commodities), safe=False)


@login_required
@require_GET
def list_commodities(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    commodities = (
        Commodity.objects.filter(site=site)
        .order_by("name")
        .values("name", "type", "price", "max", "maxperhour", "unitR", "unitC")
    )

    return JsonResponse(list(commodities), safe=False)


def add_def_to_project(def_commodity: DefCommodity, site: Site):
    commodity = Commodity(
        site=site,
        defcommodity=def_commodity,
        name=def_commodity.name,
        type=def_commodity.type,
        price=def_commodity.price,
        max=def_commodity.max,
        maxperhour=def_commodity.maxperhour,
        unitR=def_commodity.unitR,
        unitC=def_commodity.unitC,
    )
    commodity.save()

    if def_commodity.autoquery is not None:
        if def_commodity.autoquery == AutoQuery.Solar:
            threading.Thread(target=querySolar, args=(site, commodity)).start()
        elif def_commodity.autoquery == AutoQuery.Wind:
            threading.Thread(target=queryWind, args=(site, commodity)).start()
    return commodity


@login_required
@require_POST
def add_def_commodity(request, project_name, site_name, def_com_name):
    try:
        def_commodity = DefCommodity.objects.get(name=def_com_name)
    except DefCommodity.DoesNotExist:
        return HttpResponse("Default commodity not found", status="404")

    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    if Commodity.objects.filter(site=site, name=def_com_name).exists():
        return HttpResponse("Commodity with the same name already exists", status=409)

    # Start adding commodity
    add_def_to_project(def_commodity, site)

    return JsonResponse({"detail": "Commodity added"})


@login_required
@require_POST
def update_commodity(request, project_name, site_name, commodity_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    data = json.loads(request.body)

    if commodity_name != data["name"]:
        if Commodity.objects.filter(site=site, name=data["name"]).exists():
            return HttpResponse(
                "Commodity with the same name already exists", status=409
            )

    try:
        commodity = Commodity.objects.get(site=site, name=commodity_name)
    except Commodity.DoesNotExist:
        commodity = Commodity(site=site)
    commodity.name = data["name"]
    commodity.type = data["type"]
    commodity.price = data["price"] if "price" in data else None
    commodity.max = data["max"] if "max" in data else None
    commodity.maxperhour = data["maxperhour"] if "maxperhour" in data else None
    commodity.unitR = data["unitR"]
    commodity.unitC = data["unitC"]
    commodity.save()

    return JsonResponse({"detail": "Commodity updated"})


@login_required
@require_POST
def delete_commodity(request, project_name, site_name, commodity_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    commodity = Commodity.objects.get(site=site, name=commodity_name)
    commodity.delete()

    return JsonResponse({"detail": "Commodity deleted"})
