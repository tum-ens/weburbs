import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_GET

from projects.api.helper import get_project
from projects.api.simulate import build_project_config


@login_required
@require_GET
def download(request, project_name):
    project = get_project(request.user, project_name)
    config = build_project_config(project)
    response = HttpResponse(
        json.dumps(config),
        content_type="application/json",
    )
    response["Content-Disposition"] = f'attachment; filename="{project_name}.urbs"'
    return response
