import math
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import pandas as pd

from projects.models import (
    Project,
    Site,
    Commodity,
    ComType,
    Process,
    ProcessCommodity,
    ProcComDir,
    Storage,
    Demand,
    SupIm,
    Transmission,
    TransmissionType,
    DSM,
    BuySellPrice,
    BuySellPriceType,
    TimeVarEff,
)


def parse_num(val):
    if val == "inf":
        return -1
    if math.isinf(val):
        return -1
    if math.isnan(val):
        return None
    return val


def default():
    return defaultdict(default)


@login_required
@require_POST
def upload(request, project_name):
    if Project.objects.filter(user=request.user, name=project_name).exists():
        return HttpResponse("Project name already exists", status=409)

    if "file" not in request.FILES:
        return HttpResponse("File is missing", status=400)

    uploaded_file = request.FILES["file"]

    with pd.ExcelFile(uploaded_file) as xls:
        global_prop = xls.parse("Global").set_index(["Property"])
        if "CO2 limit" in global_prop.value:
            co2limit = global_prop.value["CO2 limit"]
        else:
            co2limit = 150000000
        if "Cost limit" in global_prop.value:
            costlimit = global_prop.value["Cost limit"]
        else:
            costlimit = 35000000000

        project = Project(
            user=request.user, name=project_name, co2limit=co2limit, costlimit=costlimit
        )
        project.save()

        sites_tab = xls.parse("Site")
        sites = dict()
        for index, row in sites_tab.iterrows():
            site = Site(
                project=project,
                name=row["Name"],
                area=parse_num(row["area"]),
                lat=0,
                lon=0,
            )
            site.save()
            sites[row["Name"]] = site

        coms_tab = xls.parse("Commodity")
        coms = default()
        for index, row in coms_tab.iterrows():
            com = Commodity(
                site=sites[row["Site"]],
                name=row["Commodity"],
                type=ComType[row["Type"]],
                price=parse_num(row["price"]),
                max=parse_num(row["max"]),
                maxperhour=parse_num(row["maxperhour"]),
                unitC="kWh",
                unitR="kW",
            )
            com.save()
            coms[row["Site"]][row["Commodity"]] = com

        proc_tab = xls.parse("Process")
        procs = default()
        for index, row in proc_tab.iterrows():
            proc = Process(
                site=sites[row["Site"]],
                name=row["Process"],
                instcap=parse_num(row["inst-cap"]),
                caplo=parse_num(row["cap-lo"]),
                capup=parse_num(row["cap-up"]),
                maxgrad=parse_num(row["max-grad"]),
                minfraction=parse_num(row["min-fraction"]),
                invcost=parse_num(row["inv-cost"]),
                fixcost=parse_num(row["fix-cost"]),
                varcost=parse_num(row["var-cost"]),
                wacc=parse_num(row["wacc"]),
                depreciation=parse_num(row["depreciation"]),
                areapercap=parse_num(row["area-per-cap"]),
            )
            proc.save()
            procs[row["Site"]][row["Process"]] = proc

        proccom_tab = xls.parse("Process-Commodity")
        for index, row in proccom_tab.iterrows():
            for s, ps in procs.items():
                proc = row["Process"]
                if proc in ps:
                    proccom = ProcessCommodity(
                        process=ps[proc],
                        commodity=coms[s][row["Commodity"]],
                        direction=ProcComDir[row["Direction"]],
                        ratio=parse_num(row["ratio"]),
                        ratiomin=parse_num(row["ratio-min"]),
                    )
                proccom.save()

        storage_tab = xls.parse("Storage")
        for index, row in storage_tab.iterrows():
            storage = Storage(
                site=sites[row["Site"]],
                name=row["Storage"],
                commodity=coms[row["Site"]][row["Commodity"]],
                instcapc=parse_num(row["inst-cap-c"]),
                caploc=parse_num(row["cap-lo-c"]),
                capupc=parse_num(row["cap-up-c"]),
                instcapp=parse_num(row["inst-cap-p"]),
                caplop=parse_num(row["cap-lo-p"]),
                capupp=parse_num(row["cap-up-p"]),
                effin=parse_num(row["eff-in"]),
                effout=parse_num(row["eff-out"]),
                invcostp=parse_num(row["inv-cost-p"]),
                invcostc=parse_num(row["inv-cost-c"]),
                fixcostp=parse_num(row["fix-cost-p"]),
                fixcostc=parse_num(row["fix-cost-c"]),
                varcostp=parse_num(row["var-cost-p"]),
                varcostc=parse_num(row["var-cost-c"]),
                wacc=parse_num(row["wacc"]),
                depreciation=parse_num(row["depreciation"]),
                init=parse_num(row["init"]),
                discharge=parse_num(row["discharge"]),
                epratio=parse_num(row["ep-ratio"]),
            )
            storage.save()

        demand_tab = xls.parse("Demand").set_index(["t"])
        for key in demand_tab:
            site, com = key.split(".")
            demand = Demand(
                commodity=coms[site][com],
                name="Sum",
                quantity=1,
                steps=demand_tab[key].tolist()[1::],
            )
            demand.save()

        supim_tab = xls.parse("SupIm").set_index(["t"])
        for key in supim_tab:
            site, com = key.split(".")
            supim = SupIm(commodity=coms[site][com], steps=supim_tab[key].tolist()[1::])
            supim.save()

        transmission_tab = xls.parse("Transmission")
        for index, row in transmission_tab.iterrows():
            sitein = Site.objects.get(project=project, name=row["Site In"])
            siteout = Site.objects.get(project=project, name=row["Site Out"])
            comin = Commodity.objects.get(site=sitein, name=row["Commodity"])
            comout = Commodity.objects.get(site=siteout, name=row["Commodity"])
            transmission = Transmission(
                commodityin=comin,
                commodityout=comout,
                type=TransmissionType[row["Transmission"]],
                eff=parse_num(row["eff"]),
                invcost=parse_num(row["inv-cost"]),
                fixcost=parse_num(row["fix-cost"]),
                varcost=parse_num(row["var-cost"]),
                instcap=parse_num(row["inst-cap"]),
                caplo=parse_num(row["cap-lo"]),
                capup=parse_num(row["cap-up"]),
                wacc=parse_num(row["wacc"]),
                depreciation=parse_num(row["depreciation"]),
                reactance=parse_num(row["reactance"]),
                difflimit=parse_num(row["difflimit"]),
                basevoltage=parse_num(row["base_voltage"]),
            )
            transmission.save()

        dsm_tab = xls.parse("DSM")
        for index, row in dsm_tab.iterrows():
            site = Site.objects.get(project=project, name=row["Site"])
            commodity = Commodity.objects.get(site=site, name=row["Commodity"])
            dsm = DSM(
                commodity=commodity,
                delay=parse_num(row["delay"]),
                eff=parse_num(row["eff"]),
                recov=parse_num(row["recov"]),
                capmaxdo=parse_num(row["cap-max-do"]),
                capmaxup=parse_num(row["cap-max-up"]),
            )
            dsm.save()

        bsp_tab = xls.parse("Buy-Sell-Price").set_index(["t"])
        for key in bsp_tab:
            com, type = key.split(" ")
            commodities = Commodity.objects.filter(name=com)
            steps = bsp_tab[key].tolist()[1::]
            for commodity in commodities:
                bsp = BuySellPrice(
                    commodity=commodity,
                    type=BuySellPriceType[type],
                    steps=steps,
                )
                bsp.save()

        tve_tab = xls.parse("TimeVarEff").set_index(["t"])
        for key in tve_tab:
            site, proc = key.split(".")
            site = Site.objects.get(project=project, name=site)
            process = Process.objects.get(site=site, name=proc)

            tve = TimeVarEff(process=process, steps=tve_tab[key].tolist()[1::])
            tve.save()

    return HttpResponse("Project created")
