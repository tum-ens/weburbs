import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_GET

from projects.models import Project, Site, Commodity


@login_required
@require_GET
def list_projects(request):
    projects = (Project.objects.filter(user=request.user)
                .order_by('name').values('name', 'description'))

    return JsonResponse(list(projects), safe=False)


@login_required
@require_GET
def project_details(request, project_name):
    project = get_project(project_name)

    return JsonResponse({
        'name': project.name,
        'description': project.description,
        'co2limit': project.co2limit,
        'costlimit': project.costlimit,
    }, safe=False)


@login_required
@require_POST
def update_project(request, project_name):
    data = json.loads(request.body)

    try:
        project = Project.objects.get(name=project_name)
        project.name = data['name']
        project.description = data['description']
        project.co2limit = data['co2limit']
        project.costlimit = data['costlimit']
        project.save()
    except Project.DoesNotExist:
        (Project(user=request.user, name=data['name'], description=data['description'], co2limit=data['co2limit'],
                 costlimit=data['costlimit'])
         .save())

    return JsonResponse({'detail': 'Project created'})

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
            (Site(project=project, name=data['name'], area=data['area'], long=data['long']/(60*60*1000), lat=data['lat']/(60*60*1000))
             .save())
            return JsonResponse({'detail': 'Site created'})
        else:
            return HttpResponseNotAllowed(['POST', 'DELETE'])


@login_required
@require_GET
def list_commodities(request, project_name, site_name):
    project = get_project(project_name)
    site = get_site(project, site_name)

    commodities = (Commodity.objects.filter(site=site)
                   .order_by('name').values('name', 'type', 'price', 'max', 'maxperhour'))

    return JsonResponse(list(commodities), safe=False)


def get_project(project_name):
    try:
        project = Project.objects.get(name=project_name)
        return project
    except Project.DoesNotExist:
        raise Http404("Project not found")


def get_site(project, site_name):
    try:
        site = Site.objects.get(project=project, name=site_name)
        return site
    except Site.DoesNotExist:
        raise Http404("Site not found")
