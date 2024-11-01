import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST, require_GET

from projects.models import Project, Global, Site, Commodity


@login_required
@require_GET
def list_projects(request):
    projects = (Project.objects.filter(user=request.user)
                .order_by('name').values('name', 'description'))

    return JsonResponse(list(projects), safe=False)

@login_required
@require_GET
def project_details(request, project_name):
    project = (Project.objects.get(user=request.user, name=project_name))

    return JsonResponse({
        'name': project.name,
        'description': project.description
    }, safe=False)


@login_required
@require_POST
def create_project(request):
    data = json.loads(request.body)

    project = Project(user=request.user, name=data['name'], description=data['description'])
    project.save()

    (Global(project=project, value=150000000,
            description='Limits the sum of all created (as calculated by commodity_balance) CO2 in all sites; Only relevant if not minimized')
     .save())
    (Global(project=project, value=35000000000,
                             description='Limits the sum of all costs in all sites; Only relevant if not minimized')
     .save())

    return JsonResponse({'detail': 'Project created'})

@login_required
@require_POST
def update_project(request, project_name):
    data = json.loads(request.body)

    project = get_project(project_name)
    project.name = data['name']
    project.description = data['description']
    project.save()

    return JsonResponse({'detail': 'Project created'})


@login_required
@require_GET
def list_globals(request, project_name):
    project = get_project(project_name)

    glob = (Global.objects.filter(project=project)
            .order_by('property').values('property', 'value'))

    return JsonResponse(list(glob), safe=False)


@login_required
@require_POST
def update_globals(request, project_name):
    project = get_project(project_name)
    data = json.loads(request.body)

    (Global.objects.filter(project=project)
     .order_by('property').values('property', 'value')
     .delete())

    for glob in data:
        (Global(project=project, property=glob['property'], value=glob['value'], description=glob['description'])
         .save())

    return JsonResponse({'detail': 'Globals updated'})


@login_required
@require_GET
def list_sites(request, project_name):
    project = get_project(project_name)

    sites = (Site.objects.filter(project=project)
             .order_by('name').values('name', 'description', 'area', 'long', 'lat'))

    return JsonResponse(list(sites), safe=False)

@login_required
@require_POST
def create_site(request, project_name):
    project = get_project(project_name)
    data = json.loads(request.body)

    (Site(project=project, data=data['name'], area=data['area'], long=data['long'], lat=data['lat'])
     .save())

    return JsonResponse({'detail': 'Site created'})

@login_required
@require_POST
def update_site(request, project_name, site_name):
    project = get_project(project_name)
    site = get_site(project, site_name)
    data = json.loads(request.body)

    site.name = data['name']
    site.area = data['area']
    site.long = data['long']
    site.lat = data['lat']
    site.save()

    return JsonResponse({'detail': 'Site updated'})

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
