import json
import threading

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site, validate_name_http_response
from projects.api.supim import querySolar, queryWind
from projects.models import AutoQuery, Commodity, DefCommodity, Site, Transmission


@login_required
@require_GET
def list_def_commodities(request):
    commodities = (
        DefCommodity.objects.all()
        .order_by("name")
        .values("name", "type", "price", "max", "maxperhour", "unitR", "unitC")
    )

    return JsonResponse(list(commodities), safe=False)


@login_required
@require_GET
def list_commodities(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    commodities = (
        Commodity.objects.filter(site=site)
        .order_by("name")
        .values("name", "type", "price", "max", "maxperhour", "unitR", "unitC")
    )

    return JsonResponse(list(commodities), safe=False)


@login_required
@require_GET
def list_all_commodities(request, project_name):
    project = get_project(request.user, project_name)

    com_names = (
        Commodity.objects.filter(site__project=project)
        .order_by("name")
        .values_list("name", flat=True)
        .distinct()
    )

    return JsonResponse(list(com_names), safe=False)


def add_def_to_project(def_commodity: DefCommodity, site: Site):
    # Use get_or_create to handle race conditions and prevent duplicates
    commodity, created = Commodity.objects.get_or_create(
        site=site,
        name=def_commodity.name,
        defaults={
            "defcommodity": def_commodity,
            "type": def_commodity.type,
            "price": def_commodity.price,
            "max": def_commodity.max,
            "maxperhour": def_commodity.maxperhour,
            "unitR": def_commodity.unitR,
            "unitC": def_commodity.unitC,
        },
    )

    # If the commodity already existed, update its properties to match the default
    if not created:
        commodity.defcommodity = def_commodity
        commodity.type = def_commodity.type
        commodity.price = def_commodity.price
        commodity.max = def_commodity.max
        commodity.maxperhour = def_commodity.maxperhour
        commodity.unitR = def_commodity.unitR
        commodity.unitC = def_commodity.unitC
        commodity.save()

    if def_commodity.autoquery is not None:
        if def_commodity.autoquery == AutoQuery.Solar:
            threading.Thread(target=querySolar, args=(site, commodity)).start()
        elif def_commodity.autoquery == AutoQuery.Wind:
            threading.Thread(target=queryWind, args=(site, commodity)).start()
    return commodity


@login_required
@require_POST
def add_def_commodity(request, project_name, site_name, def_com_name):
    try:
        def_commodity = DefCommodity.objects.get(name=def_com_name)
    except DefCommodity.DoesNotExist:
        return HttpResponse("Default commodity not found", status="404")

    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    if Commodity.objects.filter(site=site, name=def_com_name).exists():
        return HttpResponse("Commodity with the same name already exists", status=409)

    # Start adding commodity
    add_def_to_project(def_commodity, site)

    return JsonResponse({"detail": "Commodity added"})


@login_required
@require_POST
def update_commodity(request, project_name, site_name, commodity_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    data = json.loads(request.body)

    err = validate_name_http_response(data.get("name"), "Commodity name")
    if err:
        return err

    if (
        commodity_name != data["name"]
        and Commodity.objects.filter(site=site, name=data["name"]).exists()
    ):
        return HttpResponse("Commodity with the same name already exists", status=409)

    try:
        commodity = Commodity.objects.get(site=site, name=commodity_name)
    except Commodity.DoesNotExist:
        commodity = Commodity(site=site)
    commodity.name = data["name"]
    commodity.type = data["type"]
    commodity.price = data.get("price")
    commodity.max = data.get("max")
    commodity.maxperhour = data.get("maxperhour")
    commodity.unitR = data["unitR"]
    commodity.unitC = data["unitC"]
    commodity.save()

    return JsonResponse({"detail": "Commodity updated"})


@login_required
@require_POST
def delete_commodity(request, project_name, site_name, commodity_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    commodity = Commodity.objects.get(site=site, name=commodity_name)
    commodity.delete()

    return JsonResponse({"detail": "Commodity deleted"})


@login_required
@require_POST
def duplicate_commodity(request, project_name, site_name, commodity_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    try:
        original_commodity = Commodity.objects.get(site=site, name=commodity_name)
    except Commodity.DoesNotExist:
        return HttpResponse("Commodity not found", status=404)

    # Find the next available name with _1, _2, etc.
    base_name = original_commodity.name
    counter = 1
    new_name = f"{base_name}_{counter}"

    while Commodity.objects.filter(site=site, name=new_name).exists():
        counter += 1
        new_name = f"{base_name}_{counter}"

    # Create the duplicate
    duplicate_commodity = Commodity(
        site=site,
        defcommodity=original_commodity.defcommodity,
        name=new_name,
        type=original_commodity.type,
        price=original_commodity.price,
        max=original_commodity.max,
        maxperhour=original_commodity.maxperhour,
        unitR=original_commodity.unitR,
        unitC=original_commodity.unitC,
    )
    duplicate_commodity.save()

    return JsonResponse({"detail": "Commodity duplicated", "new_name": new_name})


@login_required
@require_POST
def cleanup_duplicate_commodities(request, project_name):
    """
    Cleanup function to remove duplicate commodities in a project.
    This function finds commodities with the same name in the same site
    and keeps only the first one, removing the rest.
    """
    project = get_project(request.user, project_name)

    # Find all commodities in the project
    commodities = Commodity.objects.filter(site__project=project).order_by(
        "site__name", "name", "id"
    )

    seen_combinations = set()
    duplicates_removed = 0

    for commodity in commodities:
        combination = (commodity.site.id, commodity.name)

        if combination in seen_combinations:
            # This is a duplicate, remove it
            commodity.delete()
            duplicates_removed += 1
        else:
            seen_combinations.add(combination)

    return JsonResponse(
        {
            "detail": f"Cleanup completed. Removed {duplicates_removed} duplicate commodities."
        }
    )


@login_required
@require_POST
def cleanup_invalid_transmissions(request, project_name):
    """
    Cleanup function to remove invalid transmissions in a project.
    This function finds transmissions that reference non-existent commodities
    or have invalid data and removes them.
    """
    project = get_project(request.user, project_name)

    # Find all transmissions in the project
    transmissions = Transmission.objects.filter(commodityin__site__project=project)

    invalid_removed = 0

    for transmission in transmissions:
        # Check if both commodities still exist
        try:
            transmission.commodityin.refresh_from_db()
            transmission.commodityout.refresh_from_db()
        except (Commodity.DoesNotExist, Site.DoesNotExist):
            # Remove transmission if commodity or site no longer exists
            transmission.delete()
            invalid_removed += 1
            continue

        # Check if transmission has valid data (not all zeros or None)
        if (
            transmission.eff == 0
            or transmission.invcost == 0
            or transmission.fixcost == 0
            or transmission.varcost == 0
            or transmission.instcap == 0
        ):
            transmission.delete()
            invalid_removed += 1

    return JsonResponse(
        {
            "detail": f"Cleanup completed. Removed {invalid_removed} invalid transmissions."
        }
    )
