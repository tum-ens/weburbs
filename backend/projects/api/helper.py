from django.http import Http404

from projects.models import Project, Site


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