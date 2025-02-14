import json
import os

from django.core.management.base import BaseCommand

from projects.models import (
    DefCommodity,
    ComType,
    AutoQuery,
    DefProcess,
    DefProcessCommodity,
    ProcComDir,
    DefStorage,
    DefSupIm,
    DefDemand,
)


class Command(BaseCommand):
    help = "Load defaults from configuration files"

    def handle(self, *args, **options):
        folder_path = "config"
        if not os.path.exists(folder_path):
            return

        commodities = {}
        processes = {}
        storages = {}
        supims = {}
        demands = {}

        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, "r") as file:
                        print(f"Loading {filename}... ", end="")
                        data = json.load(file)

                        if "commodity" in data:
                            for name, com in data["commodity"].items():
                                if name in commodities:
                                    raise Exception(
                                        f"Commodity with name {name} is configured twice"
                                    )
                                commodities[name] = com
                        if "process" in data:
                            for name, process in data["process"].items():
                                if name in processes:
                                    raise Exception(
                                        f"Process with name {name} is configured twice"
                                    )
                                processes[name] = process
                        if "storage" in data:
                            for name, storage in data["storage"].items():
                                if name in storages:
                                    raise Exception(
                                        f"Storage with name {name} is configured twice"
                                    )
                                storages[name] = storage
                        if "supim" in data:
                            for name, supim in data["supim"].items():
                                if name in supims:
                                    raise Exception(f"Supim {name} is configured twice")
                                supims[name] = supim
                        if "demand" in data:
                            for name, demand in data["demand"].items():
                                if name in demands:
                                    raise Exception(
                                        f"Demand {name} is configured twice"
                                    )
                                demands[name] = demand
                        print("\033[92mOK\033[0m")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing file {filename}: {e}")
                    )
                    exit(1)

        for def_com in DefCommodity.objects.all():
            if def_com.name not in commodities.keys():
                def_com.delete()
        for name, com in commodities.items():
            def_procs = DefCommodity.objects.filter(name=name).all()
            if len(def_procs) > 0:
                print(f"Updating commodity {name}... ", end="")
                def_com = def_procs[0]
            else:
                print(f"Adding commodity {name}... ", end="")
                def_com = DefCommodity(name=name)
            def_com.type = {
                "SupIm": ComType.SupIm,
                "Demand": ComType.Demand,
                "Stock": ComType.Stock,
                "Env": ComType.Env,
                "Buy": ComType.Buy,
                "Sell": ComType.Sell,
            }[com["type"]]
            def_com.autoquery = {
                "Solar": AutoQuery.Solar,
                "Wind": AutoQuery.Wind,
                None: None,
            }[getDefault(com, "autoquery", None)]
            def_com.price = getDefault(com, "price", None)
            def_com.max = getDefault(com, "max", None)
            def_com.maxperhour = getDefault(com, "maxperhour", None)
            def_com.autoadd = getDefault(com, "autoadd", False)
            def_com.unitR = getDefault(com, "unitR", "kW")
            def_com.unitC = getDefault(com, "unitC", "kWh")
            def_com.save()
            print("\033[92mOK\033[0m")

        for def_proc in DefProcess.objects.all():
            if def_proc.name not in processes.keys():
                def_proc.delete()
        DefProcessCommodity.objects.all().delete()
        for name, proc in processes.items():
            def_procs = DefProcess.objects.filter(name=name).all()
            if len(def_procs) > 0:
                print(f"Updating process {name}... ", end="")
                def_proc = def_procs[0]
            else:
                print(f"Adding process {name}... ", end="")
                def_proc = DefProcess(name=name)
            def_proc.description = getDefault(proc, "description", "")
            def_proc.instcap = proc["instcap"]
            def_proc.caplo = proc["caplo"]
            def_proc.capup = proc["capup"]
            def_proc.maxgrad = proc["maxgrad"]
            def_proc.minfraction = proc["minfraction"]
            def_proc.invcost = proc["invcost"]
            def_proc.fixcost = proc["fixcost"]
            def_proc.varcost = proc["varcost"]
            def_proc.wacc = proc["wacc"]
            def_proc.depreciation = proc["depreciation"]
            def_proc.areapercap = getDefault(proc, "areapercap", None)
            def_proc.autoadd = getDefault(proc, "autoadd", False)
            def_proc.save()

            for com_name, comproc in proc["commodities"].items():
                def_proccom = DefProcessCommodity(
                    def_commodity=DefCommodity.objects.get(name=com_name),
                    def_process=def_proc,
                )
                def_proccom.direction = {"In": ProcComDir.In, "Out": ProcComDir.Out}[
                    comproc["direction"]
                ]
                def_proccom.ratio = comproc["ratio"]
                def_proccom.ratiomin = getDefault(comproc, "ratiomin", None)
                def_proccom.save()
            print("\033[92mOK\033[0m")

        for def_stor in DefStorage.objects.all():
            if def_stor.name not in storages.keys():
                def_stor.delete()
        for name, stor in storages.items():
            def_stors = DefStorage.objects.filter(name=name).all()
            if len(def_stors) > 0:
                print(f"Updating storage {name}... ", end="")
                def_stor = def_stors[0]
            else:
                print(f"Adding storage {name}... ", end="")
                def_stor = DefStorage(name=name)
            def_stor.description = getDefault(stor, "description", "")
            def_stor.def_commodity = DefCommodity.objects.get(name=stor["commodity"])
            def_stor.instcapc = stor["instcapc"]
            def_stor.caploc = stor["caploc"]
            def_stor.capupc = stor["capupc"]
            def_stor.instcapp = stor["instcapp"]
            def_stor.caplop = stor["caplop"]
            def_stor.capupp = stor["capupp"]
            def_stor.effin = stor["effin"]
            def_stor.effout = stor["effout"]
            def_stor.invcostc = stor["invcostc"]
            def_stor.fixcostc = stor["fixcostc"]
            def_stor.varcostc = stor["varcostc"]
            def_stor.invcostp = stor["invcostp"]
            def_stor.fixcostp = stor["fixcostp"]
            def_stor.varcostp = stor["varcostp"]
            def_stor.wacc = stor["wacc"]
            def_stor.depreciation = stor["depreciation"]
            def_stor.init = stor["init"]
            def_stor.discharge = stor["discharge"]
            def_stor.epratio = getDefault(stor, "epratio", None)
            def_stor.save()
            print("\033[92mOK\033[0m")

        for def_supim in DefSupIm.objects.all():
            if def_supim.name not in supims.keys():
                def_supim.delete()
        for name, supim in supims.items():
            def_supims = DefSupIm.objects.filter(name=name).all()
            if len(def_supims) > 0:
                print(f"Updating supim {name}... ", end="")
                def_supim = def_supims[0]
            else:
                print(f"Adding supim {name}... ", end="")
                def_supim = DefSupIm(name=name)
            def_supim.description = getDefault(supim, "description", "")
            def_supim.steps = supim["steps"]
            def_supim.save()
            print("\033[92mOK\033[0m")

        for def_demand in DefDemand.objects.all():
            if def_demand.name not in demands.keys():
                def_demand.delete()
        for name, demand in demands.items():
            def_demands = list(DefDemand.objects.filter(name=name).all())
            if len(def_demands) > 0:
                print(f"Updating demand {name}... ", end="")
                def_demand = def_demands[0]
            else:
                print(f"Adding demand {name}... ", end="")
                def_demand = DefDemand(name=name)
            def_demand.description = getDefault(demand, "description", "")
            def_demand.steps = demand["steps"]
            def_demand.save()
            print("\033[92mOK\033[0m")


def getDefault(dict, key, default):
    if key in dict:
        return dict[key]
    else:
        return default
