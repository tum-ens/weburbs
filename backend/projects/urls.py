from django.urls import path

from projects.api import project, site, commodity, process

urlpatterns = [
    path('projects/', project.list_projects),
    path('project/<str:project_name>/', project.project_details),
    path('project/<str:project_name>/update/', project.update_project),
    path('project/<str:project_name>/sites/', site.list_sites),
    path('project/<str:project_name>/site/<str:site_name>/', site.edit_site),
    path('project/<str:project_name>/site/<str:site_name>/commodities/', commodity.list_commodities),
    path('project/<str:project_name>/site/<str:site_name>/def_commodities/', commodity.list_def_commodities),
    path('project/<str:project_name>/site/<str:site_name>/processes/', process.list_processes),
    path('project/<str:project_name>/site/<str:site_name>/def_processes/', process.list_def_processes),
    path('project/<str:project_name>/site/<str:site_name>/def_processes/<str:def_proc_name>/add',
         process.add_def_process),
]
