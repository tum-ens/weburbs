import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from projects.api.helper import get_project, get_site, get_commodity
from projects.helper.validator import checkProfile
from projects.models import Demand, DefDemand


@login_required
def getDefaultDemands(request):
    defaults = DefDemand.objects.all().order_by("name").values("name", "description")
    return JsonResponse(list(defaults), safe=False)


@login_required
@require_POST
def updateDemands(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    demands = list(Demand.objects.filter(commodity=commodity).all())
    ndemands = json.loads(request.body)

    for demand in demands:
        if demand.name not in map(lambda dem: dem["name"], ndemands):
            demand.delete()
    for ndemand in ndemands:
        demand = next(
            (demand for demand in demands if demand.name == ndemand["name"]), None
        )

        if "default" in ndemand and ndemand["default"]:
            if demand is not None:
                demand.delete()
            defdemand = DefDemand.objects.get(name=ndemand["name"])
            demand = Demand(
                name=ndemand["name"],
                description=defdemand.description,
                steps=defdemand.steps,
                defdemand=defdemand,
                commodity=commodity,
            )
        elif "steps" in ndemand and ndemand["steps"]:
            if demand is not None:
                demand.delete()
            if not checkProfile(ndemand["steps"]):
                return HttpResponse(
                    "Profile needs to be an array with exactly 8760 numbers", status=400
                )
            demand = Demand(
                name=ndemand["name"],
                description=ndemand["description"],
                steps=ndemand["steps"],
                defdemand=None,
                commodity=commodity,
            )
        else:
            if demand is None:
                return HttpResponse(
                    "Not existing profile needs to be default or upload", status=400
                )
        demand.quantity = ndemand["quantity"]
        demand.save()
    return HttpResponse("Demand was updated", status=200)


def getDemand(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    demands = (
        Demand.objects.filter(commodity=commodity)
        .values("name", "description", "steps", "quantity")
        .all()
    )
    return JsonResponse(list(demands), safe=False)
