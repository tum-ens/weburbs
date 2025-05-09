import itertools
import json
import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from projects.api.helper import get_project, get_site, get_commodity
from projects.helper.validator import checkProfile
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
def uploadSupImProfile(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    if SupIm.objects.filter(commodity=commodity).exists():
        return HttpResponse("SupIm already exists for this commodity", status=409)

    profile = json.loads(request.body)
    if not checkProfile(profile):
        return HttpResponse(
            "Profile needs to be an array with exactly 8760 numbers", status=400
        )

    supim = SupIm(
        name="Uploaded profile",
        description="Profile uploaded by user",
        commodity=commodity,
        steps=profile,
    )
    supim.save()

    return JsonResponse({"detail": "SupIm uploaded"})


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


year = 2022


def querySolar(site, commodity):
    response1 = requests.get(
        "https://www.renewables.ninja/api/data/pv",
        {
            "lat": site.lat,
            "lon": site.lon,
            "date_from": str(year - 1) + "-12-31",
            "date_to": str(year) + "-06-30",
            "local_time": True,
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
    if response1.status_code != 200:
        return HttpResponse("Data query 1 failed", status="400")
    response2 = requests.get(
        "https://www.renewables.ninja/api/data/pv",
        {
            "lat": site.lat,
            "lon": site.lon,
            "date_from": str(year) + "-07-01",
            "date_to": str(year + 1) + "-01-01",
            "local_time": True,
            "dataset": "merra2",
            "system_loss": 0.1,
            "tracking": 0,
            "azim": 180,
            "format": "json",
            "capacity": 1,
            "tilt": abs(site.lat) * 0.73,
        },
        headers={"Authorization": f"Token {api_key}"},
    )
    if response2.status_code != 200:
        return HttpResponse("Data query 2 failed", status="400")

    data = itertools.chain(
        response1.json()["data"].values(), response2.json()["data"].values()
    )
    supim = SupIm(
        name="Solar",
        description="Solar data queried from renewable ninja",
        commodity=commodity,
        steps=[
            entry["electricity"] for entry in data if str(year) in entry["local_time"]
        ],
    )
    supim.save()


def queryWind(site, commodity):
    response1 = requests.get(
        "https://www.renewables.ninja/api/data/wind",
        {
            "lat": site.lat,
            "lon": site.lon,
            "date_from": str(year - 1) + "-12-31",
            "date_to": str(year) + "-06-30",
            "local_time": True,
            "dataset": "merra2",
            "height": 100,
            "capacity": 1,
            "turbine": "Vestas V80 2000",
            "format": "json",
        },
        headers={"Authorization": f"Token {api_key}"},
    )
    if response1.status_code != 200:
        return HttpResponse("Data query 1 failed", status="400")
    response2 = requests.get(
        "https://www.renewables.ninja/api/data/wind",
        {
            "lat": site.lat,
            "lon": site.lon,
            "date_from": str(year) + "-07-01",
            "date_to": str(year + 1) + "-01-01",
            "local_time": True,
            "dataset": "merra2",
            "height": 100,
            "capacity": 1,
            "turbine": "Vestas V80 2000",
            "format": "json",
        },
        headers={"Authorization": f"Token {api_key}"},
    )
    if response2.status_code != 200:
        return HttpResponse("Data query 2 failed", status="400")

    data = itertools.chain(
        response1.json()["data"].values(), response2.json()["data"].values()
    )
    supim = SupIm(
        name="Wind",
        description="Wind data queried from renewable ninja",
        commodity=commodity,
        steps=[
            entry["electricity"] for entry in data if str(year) in entry["local_time"]
        ],
    )
    supim.save()
