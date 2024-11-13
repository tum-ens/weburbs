from django.urls import path

from projects.api import project, site, commodity, process, storage, supim, demand, simulate

urlpatterns = [
    path('projects/', project.list_projects),
    path('project/<str:project_name>/', project.project_details),
    path('project/<str:project_name>/update/', project.update_project),
    path('project/<str:project_name>/sites/', site.list_sites),
    path('project/<str:project_name>/site/<str:site_name>/', site.edit_site),
    path('project/<str:project_name>/site/<str:site_name>/commodities/', commodity.list_commodities),
    path('def_commodities/', commodity.list_def_commodities),
    path('project/<str:project_name>/site/<str:site_name>/processes/', process.list_processes),
    path('project/<str:project_name>/site/<str:site_name>/process/<str:process_name>/update/', process.update_process),
    path('def_processes/', process.list_def_processes),
    path('project/<str:project_name>/site/<str:site_name>/def_processes/<str:def_proc_name>/add/',
         process.add_def_process),
    path('project/<str:project_name>/site/<str:site_name>/storage/', storage.list_storage),
    path('def_storage/', storage.list_def_storage),
    path('project/<str:project_name>/site/<str:site_name>/def_storage/<str:def_storage_name>/add/',
         storage.add_def_storage),
    path('project/<str:project_name>/site/<str:site_name>/supim/<str:com_name>/generate/',
         supim.querySupIm),
    path('project/<str:project_name>/site/<str:site_name>/demand/<str:com_name>/generate/',
         demand.queryDemand),

    path('project/<str:project_name>/simulate/trigger/', simulate.trigger_simulation)
]
