from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from projects.api.helper import get_project, get_site
from projects.models import Commodity


@login_required
@require_GET
def list_commodities(request, project_name, site_name):
    project = get_project(project_name)
    site = get_site(project, site_name)

    commodities = (Commodity.objects.filter(site=site)
                   .order_by('name').values('name', 'type', 'price', 'max', 'maxperhour'))

    return JsonResponse(list(commodities), safe=False)
