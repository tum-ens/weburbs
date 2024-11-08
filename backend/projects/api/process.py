from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.models import DefProcess, Process, Site, DefProcessCommodity
from projects.api import commodity


@login_required
@require_GET
def list_def_processes(request):
    processes = (DefProcess.objects.all()
                 .order_by('name')
                 .values('name', 'description', 'instcap', 'caplo', 'capup', 'maxgrad', 'minfraction', 'invcost',
                         'fixcost', 'varcost', 'wacc', 'deprecation', 'areapercap'))

    return JsonResponse(list(processes), safe=False)


@login_required
@require_GET
def list_processes(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    processes = (Process.objects.filter(site=site)
                 .order_by('name')
                 .values('name', 'description', 'instcap', 'caplo', 'capup', 'maxgrad', 'minfraction', 'invcost',
                         'fixcost', 'varcost', 'wacc', 'deprecation', 'areapercap'))

    return JsonResponse(list(processes), safe=False)


def add_def_to_project(def_process: DefProcess, site: Site):
    process = Process(site=site, default=def_process, name=def_process.name, description=def_process.description,
                      instcap=def_process.instcap, caplo=def_process.caplo, capup=def_process.capup,
                      maxgrad=def_process.maxgrad, minfraction=def_process.minfraction, invcost=def_process.invcost,
                      fixcost=def_process.fixcost, varcost=def_process.varcost, wacc=def_process.wacc,
                      deprecation=def_process.deprecation, areapercap=def_process.areapercap)
    process.save()
    return process


@login_required
@require_POST
def add_def_process(request, project_name, site_name, def_proc_name):
    try:
        def_process = DefProcess.objects.get(name=def_proc_name)
    except DefProcess.DoesNotExist:
        raise Http404("Default process not found")

    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    if Process.objects.filter(site=site, name=def_proc_name).exists():
        return HttpResponse("Process with the same name already exists", status=409)

    # Start adding process and all process commodities
    process = add_def_to_project(def_process, site)

    for def_proccom in DefProcessCommodity.objects.filter(def_commodity=def_process):
        def_com = def_proccom.def_commodity
        coms = def_com.usages.filter(site=site)
        if len(coms) > 1:
            return HttpResponse("Internal error: more than one commodity references a default commodity",
                                status=500)

        if len(coms) == 1:
            com = coms[0]
        else:
            com = commodity.add_def_to_project(def_com, site)

        proccom = DefProcessCommodity(commodity=com, process=process, direction=def_com.direction, ratio=def_com.ratio,
                                      ratiomin=def_com.ratiomin)
        proccom.save()
