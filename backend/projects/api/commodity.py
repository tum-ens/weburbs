from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from projects.api.helper import get_project, get_site
from projects.models import Commodity, DefCommodity, Site


@login_required
@require_GET
def list_def_commodities(request):
    commodities = (DefCommodity.objects.all()
                   .order_by('name').values('name', 'type', 'price', 'max', 'maxperhour'))

    return JsonResponse(list(commodities), safe=False)


@login_required
@require_GET
def list_commodities(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    commodities = (Commodity.objects.filter(site=site)
                   .order_by('name').values('name', 'type', 'price', 'max', 'maxperhour'))

    return JsonResponse(list(commodities), safe=False)


def add_def_to_project(def_commodity: DefCommodity, site: Site):
    commodity = Commodity(site=site, defcommodity=def_commodity, name=def_commodity.name, type=def_commodity.type,
                          price=def_commodity.price, max=def_commodity.max, maxperhour=def_commodity.maxperhour)
    commodity.save()
    return commodity
