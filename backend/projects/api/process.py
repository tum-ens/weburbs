from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from projects.api.helper import get_project, get_site
from projects.models import DefProcess, Process, Site, DefProcessCommodity, ProcComDir, ProcessCommodity
from projects.api import commodity


@login_required
@require_GET
def list_def_processes(request):
    processes = (DefProcess.objects
                 .prefetch_related(
        Prefetch('defprocesscommodity_set', queryset=DefProcessCommodity.objects.filter(direction=ProcComDir.In),
                 to_attr='inCom'),
        Prefetch('defprocesscommodity_set', queryset=DefProcessCommodity.objects.filter(direction=ProcComDir.Out),
                 to_attr='outCom'),
    )
                 .order_by('name'))

    proclist = [{
        **model_to_dict(proc, exclude=['id']),
        'in': [proccom.def_commodity.name for proccom in proc.inCom],
        'out': [proccom.def_commodity.name for proccom in proc.outCom],
    }
        for proc in processes]
    return JsonResponse(proclist, safe=False)


@login_required
@require_GET
def list_processes(request, project_name, site_name):
    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    processes = (Process.objects
                .filter(site=site)
                 .prefetch_related(
        Prefetch('processcommodity_set', queryset=ProcessCommodity.objects.filter(direction=ProcComDir.In),
                 to_attr='inCom'),
        Prefetch('processcommodity_set', queryset=ProcessCommodity.objects.filter(direction=ProcComDir.Out),
                 to_attr='outCom'),
    )
                 .order_by('name'))

    proclist = [{
        **model_to_dict(proc, exclude=['id']),
        'in': [proccom.commodity.name for proccom in proc.inCom],
        'out': [proccom.commodity.name for proccom in proc.outCom],
    }
        for proc in processes]
    return JsonResponse(proclist, safe=False)


def add_def_to_project(def_process: DefProcess, site: Site):
    process = Process(site=site, name=def_process.name, description=def_process.description,
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
        return HttpResponse("Default process not found", status="404")

    project = get_project(request.user, project_name)
    site = get_site(project, site_name)

    if Process.objects.filter(site=site, name=def_proc_name).exists():
        return HttpResponse("Process with the same name already exists", status=409)

    # Start adding process and all process commodities
    process = add_def_to_project(def_process, site)

    for def_proccom in DefProcessCommodity.objects.filter(def_process=def_process):
        def_com = def_proccom.def_commodity
        coms = def_com.usages.filter(site=site)
        if len(coms) > 1:
            return HttpResponse("Internal error: more than one commodity references a default commodity",
                                status=500)

        if len(coms) == 1:
            com = coms[0]
        else:
            com = commodity.add_def_to_project(def_com, site)

        proccom = ProcessCommodity(commodity=com, process=process, direction=def_proccom.direction,
                                      ratio=def_proccom.ratio, ratiomin=def_proccom.ratiomin)
        proccom.save()

    return JsonResponse({'detail': 'Process added'})
