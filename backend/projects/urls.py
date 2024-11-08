from django.urls import path

from projects.api import project, site, commodity

urlpatterns = [
    path('projects/', project.list_projects),
    path('project/<str:project_name>/', project.project_details),
    path('project/<str:project_name>/update/', project.update_project),
    path('project/<str:project_name>/sites/', site.list_sites),
    path('project/<str:project_name>/site/<str:site_name>/', site.edit_site),
    path('project/<str:project_name>/site/<str:site_name>/commodities/', site.list_sites),
]