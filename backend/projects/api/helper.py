import re

from django.http import Http404, HttpResponse

from projects.models import Commodity, Project, Site

FORBIDDEN_NAME_CHARS_PATTERN = re.compile(r"[/\\?#%]")
FORBIDDEN_NAME_CHARS_LABEL = "/ \\ ? # %"


def name_validation_error(name, field="Name"):
    if name is None or str(name).strip() == "":
        return f"{field} is required"
    if FORBIDDEN_NAME_CHARS_PATTERN.search(str(name)):
        return (
            f"{field} contains characters that are not allowed: "
            f"{FORBIDDEN_NAME_CHARS_LABEL}"
        )
    return None


def validate_name_http_response(name, field="Name"):
    err = name_validation_error(name, field)
    if err:
        return HttpResponse(err, status=400)
    return None


def _collect_name_error(errors, field, name):
    err = name_validation_error(name, field)
    if err:
        errors.append(f'{err} ("{name}")')


def validate_config_names_http_response(config, project_name):
    errors = []
    _collect_name_error(errors, "Project name", project_name)
    for site_name, data_site in config.get("site", {}).items():
        _collect_name_error(errors, "Site name", site_name)
        for commodity_name, data_commodity in data_site.get("commodity", {}).items():
            _collect_name_error(errors, "Commodity name", commodity_name)
            for storage_name in data_commodity.get("storage", {}):
                _collect_name_error(errors, "Storage name", storage_name)
        for process_name in data_site.get("process", {}):
            _collect_name_error(errors, "Process name", process_name)
    for commodity_name in config.get("buysellprice", {}):
        _collect_name_error(errors, "Buy-sell price name", commodity_name)
    if errors:
        return HttpResponse("\n".join(errors[:25]), status=400)
    return None


def validate_excel_names_http_response(xls, project_name):
    errors = []
    _collect_name_error(errors, "Project name", project_name)

    sites_tab = xls.parse("Site")
    for _, row in sites_tab.iterrows():
        _collect_name_error(errors, "Site name", row["Name"])

    coms_tab = xls.parse("Commodity")
    for _, row in coms_tab.iterrows():
        _collect_name_error(errors, "Commodity name", row["Commodity"])

    proc_tab = xls.parse("Process")
    for _, row in proc_tab.iterrows():
        _collect_name_error(errors, "Process name", row["Process"])

    storage_tab = xls.parse("Storage")
    for _, row in storage_tab.iterrows():
        _collect_name_error(errors, "Storage name", row["Storage"])

    bsp_tab = xls.parse("Buy-Sell-Price").set_index(["t"])
    for com in bsp_tab:
        _collect_name_error(errors, "Buy-sell price name", com)

    if errors:
        return HttpResponse("\n".join(errors[:25]), status=400)
    return None


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
