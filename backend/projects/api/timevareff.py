import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from projects.api.helper import get_project, get_site
from projects.helper.validator import checkProfile
from projects.models import Process, TimeVarEff


@login_required
def handleTVE(request, project_name, site_name, proc_name):
    if request.method == "GET":
        return getTVE(request, project_name, site_name, proc_name)
    elif request.method == "DELETE":
        return deleteTVE(request, project_name, site_name, proc_name)
    else:
        return HttpResponse("Method not allowed", status=405)


def getTVE(request, project_name, site_name, proc_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    process = Process.objects.get(site=site, name=proc_name)

    tve = TimeVarEff.objects.get(process=process)
    return JsonResponse({"data": tve.steps})


def deleteTVE(request, project_name, site_name, proc_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    process = Process.objects.get(site=site, name=proc_name)

    TimeVarEff.objects.filter(process=process).delete()
    return HttpResponse("BuySellPrice deleted", status=200)


@login_required
@require_POST
def uploadTVEProfile(request, project_name, site_name, proc_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)
    process = Process.objects.get(site=site, name=proc_name)

    if TimeVarEff.objects.filter(process=process).exists():
        return HttpResponse("TimeVarEff already exists for this commodity", status=409)

    profile = json.loads(request.body)
    if not checkProfile(profile):
        return HttpResponse(
            "Profile needs to be an array with exactly 8760 numbers", status=400
        )

    tve = TimeVarEff(process=process, steps=profile)
    tve.save()

    return JsonResponse({"detail": "TimeVarEff uploaded"})
