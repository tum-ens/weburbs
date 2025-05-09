import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from projects.api.helper import get_project, get_site, get_commodity
from projects.helper.validator import checkProfile
from projects.models import BuySellPrice, BuySellPriceType


@login_required
def handleBSP(request, project_name, site_name, com_name):
    if request.method == "GET":
        return getBSP(request, project_name, site_name, com_name)
    elif request.method == "DELETE":
        return deleteBSP(request, project_name, site_name, com_name)
    else:
        return HttpResponse("Method not allowed", status=405)


def getBSP(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    bsps = BuySellPrice.objects.filter(commodity=commodity).all()
    if len(bsps) == 0:
        return JsonResponse({})
    elif len(bsps) > 2:
        return HttpResponse(
            "Serverside error: Too many BSPs for one commodity", status=500
        )
    elif len(bsps) == 1:
        if bsps[0].type == BuySellPriceType.buy:
            return JsonResponse({"buy": bsps[0].steps})
        else:
            return JsonResponse({"sell": bsps[0].steps})
    else:
        if bsps[0].type == bsps[1].type:
            return HttpResponse(
                "Serverside error: Too many BSPs for one commodity", status=500
            )
        elif bsps[0].type == BuySellPriceType.buy:
            return JsonResponse({"buy": bsps[0].steps, "sell": bsps[1].steps})
        else:
            return JsonResponse({"buy": bsps[1].steps, "sell": bsps[0].steps})


def deleteBSP(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    BuySellPrice.objects.filter(commodity=commodity).delete()
    return HttpResponse("BuySellPrice deleted", status=200)


@login_required
@require_POST
def uploadBSPProfile(request, project_name, site_name, com_name, ty):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    if ty == "buy":
        ty = BuySellPriceType.buy
    elif ty == "sell":
        ty = BuySellPriceType.sell
    else:
        return HttpResponse("Invalid type", status=400)

    if BuySellPrice.objects.filter(commodity=commodity, type=ty).exists():
        return HttpResponse(
            "BuySellPrice already exists for this commodity", status=409
        )

    profile = json.loads(request.body)
    if not checkProfile(profile):
        return HttpResponse(
            "Profile needs to be an array with exactly 8760 numbers", status=400
        )

    bsp = BuySellPrice(commodity=commodity, type=ty, steps=profile)
    bsp.save()

    return JsonResponse({"detail": "BuySellPrice uploaded"})
