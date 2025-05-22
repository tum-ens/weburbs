import json

from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from projects.api.helper import get_project
from projects.helper.validator import checkProfile
from projects.models import BuySellPrice, BuySellPriceType


@login_required
def listBSP(request, project_name):
    project = get_project(request.user, project_name)
    BSPs = BuySellPrice.objects.filter(project=project).order_by("name", "type").all()

    bsp_list = [
        {
            **model_to_dict(bsp, exclude=["id", "project"]),
            "type": BuySellPriceType(bsp.type).name,
        }
        for bsp in BSPs
    ]
    return JsonResponse(bsp_list, safe=False)


@login_required
def deleteBSP(request, project_name, com_name, ty):
    if request.method != "DELETE":
        return HttpResponse("Method not allowed", status=405)

    project = get_project(request.user, project_name)

    if ty == "buy":
        ty = BuySellPriceType.buy
    elif ty == "sell":
        ty = BuySellPriceType.sell
    else:
        return HttpResponse("Invalid type", status=400)

    BuySellPrice.objects.filter(project=project, name=com_name, type=ty).delete()
    return HttpResponse("BuySellPrice deleted", status=200)


@login_required
@require_POST
def uploadBSPProfile(request, project_name, com_name, ty):
    project = get_project(request.user, project_name)

    if ty == "buy":
        ty = BuySellPriceType.buy
    elif ty == "sell":
        ty = BuySellPriceType.sell
    else:
        return HttpResponse("Invalid type", status=400)

    if BuySellPrice.objects.filter(project=project, name=com_name, type=ty).exists():
        return HttpResponse(
            "BuySellPrice already exists for this commodity", status=409
        )

    profile = json.loads(request.body)
    if not checkProfile(profile):
        return HttpResponse(
            "Profile needs to be an array with exactly 8760 numbers", status=400
        )

    bsp = BuySellPrice(project=project, name=com_name, type=ty, steps=profile)
    bsp.save()

    return JsonResponse({"detail": "BuySellPrice uploaded"})
