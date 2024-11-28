from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.api import commodity
from projects.models import Site, DefStorage, Storage, Commodity
from django.forms.models import model_to_dict


@login_required
@require_GET
def list_def_storage(request):
    storage = DefStorage.objects.order_by("name")

    storageList = [
        {
            **model_to_dict(sto, exclude=["id", "def_commodity"]),
            "commodity": sto.def_commodity.name,
        }
        for sto in storage
    ]
    return JsonResponse(storageList, safe=False)


@login_required
@require_GET
def list_storage(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    storage = Storage.objects.filter(site=site).order_by("name")

    proclist = [
        {
            **model_to_dict(sto, exclude=["id", "def_commodity"]),
            "commodity": sto.commodity.name,
        }
        for sto in storage
    ]
    return JsonResponse(proclist, safe=False)


def add_def_to_project(def_storage: DefStorage, site: Site, com: Commodity):
    storage = Storage(
        site=site,
        commodity=com,
        name=def_storage.name,
        description=def_storage.description,
        instcapc=def_storage.instcapc,
        caploc=def_storage.caploc,
        capupc=def_storage.capupc,
        instcapp=def_storage.instcapp,
        caplop=def_storage.caplop,
        capupp=def_storage.capupp,
        effin=def_storage.effin,
        effout=def_storage.effout,
        invcostp=def_storage.invcostp,
        invcostc=def_storage.invcostc,
        fixcostp=def_storage.fixcostp,
        fixcostc=def_storage.fixcostc,
        varcostp=def_storage.varcostp,
        varcostc=def_storage.varcostc,
        wacc=def_storage.wacc,
        depreciation=def_storage.depreciation,
        init=def_storage.init,
        discharge=def_storage.discharge,
        epratio=def_storage.epratio,
    )
    storage.save()
    return storage


@login_required
@require_POST
def add_def_storage(request, project_name, site_name, def_storage_name):
    try:
        def_storage = DefStorage.objects.get(name=def_storage_name)
    except DefStorage.DoesNotExist:
        return HttpResponse("Default storage not found", status="404")

    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    if Storage.objects.filter(site=site, name=def_storage_name).exists():
        return HttpResponse("Storage with the same name already exists", status=409)

    # Start adding process and all process commodities
    coms = def_storage.def_commodity.usages.filter(site=site)
    if len(coms) == 1:
        com = coms[0]
    else:
        com = commodity.add_def_to_project(def_storage.def_commodity, site)

    storage = add_def_to_project(def_storage, site, com)
    storage.save()

    return JsonResponse({"detail": "Storage added"})
