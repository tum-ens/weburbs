import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.models import (
    Commodity,
    DSM,
)
from django.forms.models import model_to_dict


@login_required
@require_GET
def list_dsm(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    dsms = DSM.objects.filter(commodity__site=site).order_by("commodity__name")

    dsm_list = [
        {
            **model_to_dict(dsm, exclude=["id", "commodity"]),
            "commodity": dsm.commodity.name,
        }
        for dsm in dsms
    ]

    return JsonResponse(dsm_list, safe=False)


@login_required
@require_POST
def update_dsm(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    com = Commodity.objects.get(site=site, name=com_name)

    data = json.loads(request.body)

    com_new = Commodity.objects.get(site=site, name=data["commodity"])
    if com_name != data["commodity"]:
        if DSM.objects.filter(commodity=com_new).exists():
            return HttpResponse(
                "DSM with for this commodity already exists", status=409
            )

    try:
        dsm = DSM.objects.get(commodity=com)
    except DSM.DoesNotExist:
        dsm = DSM()

    dsm.commodity = com_new
    dsm.delay = data["delay"]
    dsm.eff = data["eff"]
    dsm.recov = data["recov"]
    dsm.capmaxdo = data["capmaxdo"]
    dsm.capmaxup = data["capmaxup"]
    dsm.save()

    return JsonResponse({"detail": "DSM update"})


@login_required
@require_POST
def delete_dsm(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    com = Commodity.objects.get(site=site, name=com_name)

    dsm = DSM.objects.get(commodity=com)
    dsm.delete()

    return JsonResponse({"detail": "DSM deleted"})
