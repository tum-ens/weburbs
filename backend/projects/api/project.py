import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project
from projects.models import Project


@login_required
@require_GET
def list_projects(request):
    projects = (
        Project.objects.filter(user=request.user)
        .order_by("name")
        .values("name", "description")
    )

    return JsonResponse(list(projects), safe=False)


@login_required
@require_GET
def project_details(request, project_name):
    project = get_project(request.user, project_name)

    return JsonResponse(
        {
            "name": project.name,
            "description": project.description,
            "co2limit": project.co2limit,
            "costlimit": project.costlimit,
        },
        safe=False,
    )


@login_required
@require_POST
def update_project(request, project_name):
    data = json.loads(request.body)

    if (
        data["name"] != project_name
        and Project.objects.filter(user=request.user, name=data["name"]).exists()
    ):
        return HttpResponse("A project with this name already exists", status=409)
    if data["name"] == "__new":
        return HttpResponse("Invalid name", status=400)

    try:
        project = Project.objects.get(user=request.user, name=project_name)
        project.name = data["name"]
        project.description = data["description"]
        project.co2limit = data["co2limit"]
        project.costlimit = data["costlimit"]
        project.save()
    except Project.DoesNotExist:
        (
            Project(
                user=request.user,
                name=data["name"],
                description=data["description"],
                co2limit=data["co2limit"],
                costlimit=data["costlimit"],
            ).save()
        )

    return JsonResponse({"detail": "Project created"})
