from django.contrib.auth.models import AbstractUser
from django.http import HttpResponse, JsonResponse

from projects.api.configupload import readConfig
from projects.models import Project, DefProjectLoaded, DefProject


def initUser(user: AbstractUser):
    for default in DefProjectLoaded.objects.all():
        readConfig(user, default.preset.name, default.preset.config)


def list_def_projects(_):
    defs = list(DefProject.objects.order_by("name").values("name").all())
    return JsonResponse(defs, safe=False)


def load_default(request, project_name):
    preset = DefProject.objects.get(name=project_name)

    if Project.objects.filter(user=request.user, name=project_name).exists():
        return HttpResponse("A project with this name already exists", status=409)
    if project_name == "__new":
        return HttpResponse("Invalid name", status=400)

    readConfig(request.user, project_name, preset.config)

    return HttpResponse("Project created")
