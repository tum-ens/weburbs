import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_GET

from projects.api.helper import get_project
from projects.models import Site


@login_required
@require_GET
def list_sites(request, project_name):
    project = get_project(project_name)
    sites = (Site.objects.filter(project=project)
             .order_by('name').values('name', 'area', 'long', 'lat'))

    return JsonResponse(list(sites), safe=False)


@login_required
@require_POST
def edit_site(request, project_name, site_name):
    project = get_project(project_name)
    data = json.loads(request.body)

    try:
        site = Site.objects.get(project=project, name=site_name)

        if request.method == "POST":
            site.name = data['name']
            site.area = data['area']
            site.long = data['long']
            site.lat = data['lat']
            site.save()
            return JsonResponse({'detail': 'Site updated'})
        elif request.method == "DELETE":
            site.delete()
            return JsonResponse({'detail': 'Site deleted'})
        else:
            return HttpResponseNotAllowed(['POST', 'DELETE'])
    except Site.DoesNotExist:
        if request.method == "POST":
            (Site(project=project, name=data['name'], area=data['area'], long=data['long'], lat=data['lat'])
             .save())
            return JsonResponse({'detail': 'Site created'})
        else:
            return HttpResponseNotAllowed(['POST', 'DELETE'])
