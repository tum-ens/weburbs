from django.http import Http404

from projects.models import Project, Site, Commodity


def get_project(user, project_name):
    try:
        project = Project.objects.get(user=user, name=project_name)
        return project
    except Project.DoesNotExist:
        raise Http404("Project not found")


def get_site(project, site_name):
    try:
        site = Site.objects.get(project=project, name=site_name)
        return site
    except Site.DoesNotExist:
        raise Http404("Site not found")

def get_commodity(site, commodity_name):
    try:
        commodity = Commodity.objects.get(site=site, name=commodity_name)
        return commodity
    except Commodity.DoesNotExist:
        raise Http404("Commodity not found")
