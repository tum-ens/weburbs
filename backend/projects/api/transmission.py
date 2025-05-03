import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.models import (
    Commodity,
    Transmission,
)
from django.forms.models import model_to_dict


@login_required
@require_GET
def list_transmission(request, project_name):
    project = get_project(request.user, project_name)

    transmissions = Transmission.objects.filter(
        commodityin__site__project=project
    ).order_by(
        "commodityin__name", "commodityin__site__name", "commodityout__site__name"
    )

    transmissionsList = [
        {
            **model_to_dict(trans, exclude=["id", "commodityin", "commodityout"]),
            "sitein": trans.commodityin.site.name,
            "siteout": trans.commodityout.site.name,
            "commodity": trans.commodityin.name,
        }
        for trans in transmissions
    ]
    return JsonResponse(transmissionsList, safe=False)


@login_required
@require_POST
def update_transmission(request, project_name, sitein_name, siteout_name, com_name):
    project = get_project(request.user, project_name)
    sitein = get_site(project, sitein_name)
    comin = Commodity.objects.get(site=sitein, name=com_name)
    siteout = get_site(project, siteout_name)
    comout = Commodity.objects.get(site=siteout, name=com_name)

    data = json.loads(request.body)

    sitein_new = get_site(project, data["sitein"])
    comin_new = Commodity.objects.get(site=sitein_new, name=com_name)
    siteout_new = get_site(project, data["siteout"])
    comout_new = Commodity.objects.get(site=siteout_new, name=com_name)
    if (
        sitein_name != data["sitein"]
        or siteout_name != data["siteout"]
        or com_name != data["commodity"]
    ):
        if Transmission.objects.filter(
            commodityin=comin_new, commodityout=comout_new
        ).exists():
            return HttpResponse(
                "Transmission between the same commodities name already exists",
                status=409,
            )

    try:
        transmission = Transmission.objects.get(commodityin=comin, commodityout=comout)
    except Transmission.DoesNotExist:
        transmission = Transmission()

    transmission.commodityin = comin_new
    transmission.commodityout = comout_new
    transmission.type = data["type"]
    transmission.eff = data["eff"]
    transmission.invcost = data["invcost"]
    transmission.fixcost = data["fixcost"]
    transmission.varcost = data["varcost"]
    transmission.instcap = data["instcap"]
    transmission.caplo = data["caplo"]
    transmission.capup = data["capup"]
    transmission.wacc = data["wacc"]
    transmission.depreciation = data["depreciation"]
    if "reactance" in data:
        transmission.res = data["reactance"]
    else:
        transmission.res = None
    if "difflimit" in data:
        transmission.difflimit = data["difflimit"]
    else:
        transmission.difflimit = None
    if "basevoltage" in data:
        transmission.basevoltage = data["basevoltage"]
    else:
        transmission.basevoltage = None
    transmission.save()

    return JsonResponse({"detail": "Storage update"})


@login_required
@require_POST
def delete_transmission(request, project_name, sitein_name, siteout_name, com_name):
    project = get_project(request.user, project_name)
    sitein = get_site(project, sitein_name)
    comin = Commodity.objects.get(site=sitein, name=com_name)
    siteout = get_site(project, siteout_name)
    comout = Commodity.objects.get(site=siteout, name=com_name)

    transmission = Transmission.objects.get(commodityin=comin, commodityout=comout)
    transmission.delete()

    return JsonResponse({"detail": "Transmission deleted"})
