from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

from projects.api.helper import get_project, get_site, get_commodity
from projects.models import Demand, DefDemand


@login_required
def getDefaultDemands(request):
    defaults = DefDemand.objects.all().order_by("name").values("name", "description")
    return JsonResponse(list(defaults), safe=False)

@login_required
def handleDemand(request, project_name, site_name, com_name):
    if request.method == "GET":
        return getDemand(request, project_name, site_name, com_name)
    elif request.method == "DELETE":
        return deleteDemand(request, project_name, site_name, com_name)
    else:
        return HttpResponse("Method not allowed", status=405)


def getDemand(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    demands = Demand.objects.filter(commodity=commodity).all()
    if len(demands) == 0:
        return JsonResponse({})
    elif len(demands) > 1:
        return HttpResponse(
            "Serverside error: Multiple Demands for one commodity", status=500
        )
    else:
        return JsonResponse({"data": demands[0].steps})


def deleteDemand(request, project_name, site_name, com_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    commodity = get_commodity(site, com_name)

    Demand.objects.filter(commodity=commodity).delete()
    return HttpResponse("Demand deleted", status=200)