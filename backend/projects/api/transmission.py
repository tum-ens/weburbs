import json
import logging
import math

from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.models import (
    Commodity,
    Transmission,
)

# Set up logging
logger = logging.getLogger(__name__)


@login_required
@require_GET
def debug_transmission_count(request, project_name):
    """Debug endpoint to check transmission counts"""
    project = get_project(request.user, project_name)

    transmissions = Transmission.objects.filter(commodityin__site__project=project)

    debug_info = {
        "project_name": project_name,
        "db_transmission_count": transmissions.count(),
        "transmission_details": [
            {
                "id": trans.id,
                "sitein": trans.commodityin.site.name,
                "siteout": trans.commodityout.site.name,
                "commodity": trans.commodityin.name,
                "type": trans.type,
                "eff": trans.eff,
            }
            for trans in transmissions
        ],
    }

    return JsonResponse(debug_info, safe=False)


@login_required
@require_GET
def list_transmission(request, project_name):
    project = get_project(request.user, project_name)

    transmissions = Transmission.objects.filter(
        commodityin__site__project=project
    ).order_by(
        "commodityin__name", "commodityin__site__name", "commodityout__site__name"
    )

    raw_list = [
        {
            **model_to_dict(trans, exclude=["id", "commodityin", "commodityout"]),
            "sitein": trans.commodityin.site.name,
            "siteout": trans.commodityout.site.name,
            "commodity": trans.commodityin.name,
        }
        for trans in transmissions
    ]

    # Sanitize non-JSON values like Infinity/NaN to ensure valid JSON
    transmissionsList = []
    for item in raw_list:
        sanitized = item.copy()
        for key in [
            "eff",
            "invcost",
            "fixcost",
            "varcost",
            "instcap",
            "caplo",
            "capup",
            "wacc",
            "depreciation",
            "reactance",
            "difflimit",
            "basevoltage",
        ]:
            value = sanitized.get(key)
            if isinstance(value, float):
                if math.isinf(value):
                    # Convert infinity to -1 for capup (maximum capacity)
                    if key == "capup":
                        sanitized[key] = -1
                    else:
                        sanitized[key] = None
                elif math.isnan(value):
                    sanitized[key] = None
        transmissionsList.append(sanitized)

    # Debug logging
    logger.error(
        f"DEBUG: Project {project_name} - DB count: {transmissions.count()}, API response count: {len(transmissionsList)}"
    )
    print(
        f"DEBUG: Project {project_name} - DB count: {transmissions.count()}, API response count: {len(transmissionsList)}"
    )

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

    # Validate required fields to prevent empty transmissions
    required_fields = [
        "type",
        "eff",
        "invcost",
        "fixcost",
        "varcost",
        "instcap",
        "caplo",
        "capup",
        "wacc",
        "depreciation",
    ]
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            return HttpResponse(f"Missing or invalid field: {field}", status=400)

    sitein_new = get_site(project, data["sitein"])
    comin_new = Commodity.objects.get(site=sitein_new, name=com_name)
    siteout_new = get_site(project, data["siteout"])
    comout_new = Commodity.objects.get(site=siteout_new, name=com_name)
    if (
        sitein_name != data["sitein"]
        or siteout_name != data["siteout"]
        or com_name != data["commodity"]
    ) and Transmission.objects.filter(
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
        transmission.reactance = data["reactance"]
    else:
        transmission.reactance = None
    if "difflimit" in data:
        transmission.difflimit = data["difflimit"]
    else:
        transmission.difflimit = None
    if "basevoltage" in data:
        transmission.basevoltage = data["basevoltage"]
    else:
        transmission.basevoltage = None
    transmission.save()

    return JsonResponse({"detail": "Transmission updated"})


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


@login_required
@require_POST
def duplicate_transmission(request, project_name, sitein_name, siteout_name, com_name):
    project = get_project(request.user, project_name)
    sitein = get_site(project, sitein_name)
    comin = Commodity.objects.get(site=sitein, name=com_name)
    siteout = get_site(project, siteout_name)
    comout = Commodity.objects.get(site=siteout, name=com_name)

    try:
        original_transmission = Transmission.objects.get(
            commodityin=comin, commodityout=comout
        )
    except Transmission.DoesNotExist:
        return HttpResponse("Transmission not found", status=404)

    # Check if reverse transmission already exists (from siteout to sitein)
    try:
        reverse_transmission = Transmission.objects.get(
            commodityin=comout, commodityout=comin
        )
        return HttpResponse("Reverse transmission already exists", status=400)
    except Transmission.DoesNotExist:
        pass  # Good, we can create the reverse transmission

    # Create the reverse transmission (from siteout to sitein)
    reverse_transmission = Transmission(
        commodityin=comout,  # Now comout is the input
        commodityout=comin,  # Now comin is the output
        type=original_transmission.type,
        eff=original_transmission.eff,
        invcost=original_transmission.invcost,
        fixcost=original_transmission.fixcost,
        varcost=original_transmission.varcost,
        instcap=original_transmission.instcap,
        caplo=original_transmission.caplo,
        capup=original_transmission.capup,
        wacc=original_transmission.wacc,
        depreciation=original_transmission.depreciation,
        reactance=original_transmission.reactance,
        difflimit=original_transmission.difflimit,
        basevoltage=original_transmission.basevoltage,
    )
    reverse_transmission.save()

    return JsonResponse({"detail": "Reverse transmission created"})
