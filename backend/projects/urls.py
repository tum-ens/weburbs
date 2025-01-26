from django.urls import path

from projects.api import (
    project,
    site,
    commodity,
    process,
    storage,
    supim,
    demand,
    simulate,
)

urlpatterns = [
    path("projects/", project.list_projects),
    path("project/<str:project_name>/", project.project_details),
    # Edit, list and delete Sites
    path("project/<str:project_name>/update/", project.update_project),
    path("project/<str:project_name>/sites/", site.list_sites),
    path("project/<str:project_name>/site/<str:site_name>/", site.edit_site),
    # Commodity: List, List, Update - Default: List, Add
    path(
        "project/<str:project_name>/site/<str:site_name>/commodities/",
        commodity.list_commodities,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/commodity/<str:commodity_name>/update/",
        commodity.update_commodity,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/commodity/<str:commodity_name>/delete/",
        commodity.delete_commodity,
    ),
    path("def_commodities/", commodity.list_def_commodities),
    path(
        "project/<str:project_name>/site/<str:site_name>/def_commodities/<str:def_com_name>/add/",
        commodity.add_def_commodity,
    ),
    # Process: List, Update, Delete, Add - Default: List, Add
    path(
        "project/<str:project_name>/site/<str:site_name>/processes/",
        process.list_processes,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/process/<str:process_name>/update/",
        process.update_process,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/process/<str:process_name>/delete/",
        process.delete_process,
    ),
    path("def_processes/", process.list_def_processes),
    path(
        "project/<str:project_name>/site/<str:site_name>/def_processes/<str:def_proc_name>/add/",
        process.add_def_process,
    ),
    # Storage: List, Update, Delete - Default: List, Add
    path(
        "project/<str:project_name>/site/<str:site_name>/storage/", storage.list_storage
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/storage/<str:storage_name>/update/",
        storage.update_storage,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/storage/<str:storage_name>/delete/",
        storage.delete_storage,
    ),
    path("def_storage/", storage.list_def_storage),
    path(
        "project/<str:project_name>/site/<str:site_name>/def_storage/<str:def_storage_name>/add/",
        storage.add_def_storage,
    ),
    # SupIm: Get/Delete, Query
    path(
        "project/<str:project_name>/site/<str:site_name>/supim/<str:com_name>/",
        supim.handleSupIm,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/supim/<str:com_name>/query/<str:type>/",
        supim.querySupIm,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/supim/<str:com_name>/upload/",
        supim.uploadSupImProfile,
    ),
    # Demand: Get/Delete, Query - Defaults: Lists
    path(
        "project/<str:project_name>/site/<str:site_name>/demand/<str:com_name>/update/",
        demand.updateDemands,
    ),
    path(
        "project/<str:project_name>/site/<str:site_name>/demand/<str:com_name>/",
        demand.getDemand,
    ),
    path(
        "def_demands/",
        demand.getDefaultDemands,
    ),
    # Simulation: Trigger, Get Result, Get Logs, Get Config
    path("project/<str:project_name>/simulate/trigger/", simulate.trigger_simulation),
    path("project/<str:project_name>/simulate/results/", simulate.get_simulations),
    path(
        "project/<str:project_name>/simulate/result/<uuid:simid>/",
        simulate.get_simulation_result,
    ),
    path(
        "project/<str:project_name>/simulate/result/<uuid:simid>/logs",
        simulate.get_simulation_logs,
    ),
    path(
        "project/<str:project_name>/simulate/result/<uuid:simid>/config",
        simulate.get_simulation_config,
    ),
]
