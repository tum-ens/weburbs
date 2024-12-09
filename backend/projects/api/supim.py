import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from projects.api.helper import get_project, get_site, get_commodity
from projects.models import SupIm


@login_required
def handleSupIm(request, project_name, site_name, com_name):
    if request.method == "GET":
        return getSupIm(request, project_name, site_name, com_name)
    elif request.method == "DELETE":
        return deleteSupIm(request, project_name, site_name, com_name)
    else:
        return HttpResponse("Method not allowed", status=405)


def getSupIm(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    supims = SupIm.objects.filter(commodity=commodity).all()
    if len(supims) == 0:
        return JsonResponse({})
    elif len(supims) > 1:
        return HttpResponse(
            "Serverside error: Multiple SupIms for one commodity", status=500
        )
    else:
        return JsonResponse({"data": supims[0].steps})


def deleteSupIm(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    SupIm.objects.filter(commodity=commodity).delete()
    return HttpResponse("SupIm deleted", status=200)


api_key = os.getenv("RN_KEY")


@login_required
@require_POST
def querySupIm(request, project_name, site_name, com_name, type):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    if SupIm.objects.filter(commodity=commodity).exists():
        return HttpResponse("SupIm already exists for this commodity", status=409)

    if type == "Solar":
        querySolar(site, commodity)
    elif type == "Wind":
        queryWind(site, commodity)
    else:
        return HttpResponse(
            "This commodity does not provide a default supim", status=404
        )

    return JsonResponse({"detail": "SupIm added"})


def querySolar(site, commodity):
    response = requests.get(
        "https://www.renewables.ninja/api/data/pv",
        {
            "lat": site.lat,
            "lon": site.lon,
            "date_from": "2023-01-01",
            "date_to": "2023-12-31",
            "dataset": "merra2",
            "system_loss": 0.1,
            "tracking": 0,
            "azim": 180,
            "format": "json",
            "capacity": 1,
            "tilt": 35,
        },
        headers={"Authorization": f"Token {api_key}"},
    )
    if response.status_code != 200:
        return HttpResponse("Data query failed", status="400")

    supim = SupIm(
        name="Solar_Example",
        description="Simple example",
        commodity=commodity,
        steps=[entry["electricity"] for entry in response.json()["data"].values()],
    )
    supim.save()


def queryWind(site, commodity):
    response = requests.get(
        "https://www.renewables.ninja/api/data/wind",
        {
            "lat": site.lat,
            "lon": site.lon,
            "date_from": "2023-01-01",
            "date_to": "2023-12-31",
            "dataset": "merra2",
            "height": 100,
            "capacity": 1,
            "turbine": "Vestas V80 2000",
            "format": "json",
        },
        headers={"Authorization": f"Token {api_key}"},
    )
    if response.status_code != 200:
        return HttpResponse("Data query failed", status="400")
    supim = SupIm(
        name="Wind_Example",
        description="Wind example",
        commodity=commodity,
        steps=[entry["electricity"] for entry in response.json()["data"].values()],
    )
    supim.save()
