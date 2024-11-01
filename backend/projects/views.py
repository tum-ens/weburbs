import json
from http.client import HTTPResponse

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from projects.models import Project


@login_required
@require_POST
def create_project(request):
    data = json.loads(request.body)
    name = data.get('name')
    description = data.get('description')

    project = Project(user=request.user, name=name, description=description)
    project.save()

    return JsonResponse({'detail': 'Project created'})


@login_required
@require_GET
def list_projects(request):
    projects = (Project.objects.filter(user=request.user)
                .order_by('name').values('id', 'name', 'description'))

    return JsonResponse(list(projects), safe=False)
