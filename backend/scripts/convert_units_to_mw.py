#!/usr/bin/env python3
"""One-off helper: convert kW/kWh preset configs to MW/MWh (and kg to tonnes)."""

import json
import math
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "config")


def is_num(v):
    return isinstance(v, (int, float)) and not math.isnan(v)


def scale_power(v):
    if not is_num(v) or v < 0:
        return v
    return v / 1000


def scale_energy_cap(v):
    if not is_num(v) or v < 0:
        return v
    return v / 1000


def scale_cost_per_power(v):
    if not is_num(v):
        return v
    return v * 1000


def scale_cost_per_energy(v):
    if not is_num(v):
        return v
    return v * 1000


def convert_process(proc):
    for key in ("instcap", "caplo", "capup", "maxgrad"):
        if key in proc:
            proc[key] = scale_power(proc[key])
    for key in ("invcost", "fixcost"):
        if key in proc:
            proc[key] = scale_cost_per_power(proc[key])
    if "varcost" in proc:
        proc["varcost"] = scale_cost_per_energy(proc["varcost"])
    if "areapercap" in proc and is_num(proc["areapercap"]):
        proc["areapercap"] = proc["areapercap"] * 1000


def convert_storage(stor):
    for key in ("instcapc", "caploc", "capupc"):
        if key in stor:
            stor[key] = scale_energy_cap(stor[key])
    for key in ("instcapp", "caplop", "capupp"):
        if key in stor:
            stor[key] = scale_power(stor[key])
    for key in ("invcostc", "fixcostc", "varcostc"):
        if key in stor:
            stor[key] = scale_cost_per_energy(stor[key])
    for key in ("invcostp", "fixcostp", "varcostp"):
        if key in stor:
            stor[key] = scale_cost_per_power(stor[key])


UNIT_MAP = {
    "kW": "MW",
    "kWh": "MWh",
    "kg/h": "tonnes/h",
    "kg": "tonnes",
    "tonne/h": "tonnes/h",
    "tonne": "tonnes",
}


def convert_commodity_units(com):
    com_type = com.get("Type") or com.get("type")
    if com_type == "Env":
        com["unitR"] = "tonnes/h"
        com["unitC"] = "tonnes"
        if is_num(com.get("max")) and com["max"] > 0:
            com["max"] = com["max"] / 1000
        if is_num(com.get("maxperhour")) and com["maxperhour"] > 0:
            com["maxperhour"] = com["maxperhour"] / 1000
        return
    if com.get("unitC") == "l" or com.get("unitR") == "l/h":
        return
    for key in ("unitR", "unitC"):
        if key in com and com[key] in UNIT_MAP:
            com[key] = UNIT_MAP[com[key]]


def convert_urbs_site(site):
    for com in site.get("commodity", {}).values():
        convert_commodity_units(com)
    for proc in site.get("process", {}).values():
        mapped = {
            "instcap": proc.get("inst-cap", proc.get("instcap")),
            "caplo": proc.get("cap-lo", proc.get("caplo")),
            "capup": proc.get("cap-up", proc.get("capup")),
            "maxgrad": proc.get("max-grad", proc.get("maxgrad")),
            "invcost": proc.get("inv-cost", proc.get("invcost")),
            "fixcost": proc.get("fix-cost", proc.get("fixcost")),
            "varcost": proc.get("var-cost", proc.get("varcost")),
            "areapercap": proc.get("area-per-cap", proc.get("areapercap")),
        }
        convert_process(mapped)
        if "inst-cap" in proc:
            proc["inst-cap"] = mapped["instcap"]
            proc["cap-lo"] = mapped["caplo"]
            proc["cap-up"] = mapped["capup"]
            proc["max-grad"] = mapped["maxgrad"]
            proc["inv-cost"] = mapped["invcost"]
            proc["fix-cost"] = mapped["fixcost"]
            proc["var-cost"] = mapped["varcost"]
            if mapped["areapercap"] is not None:
                proc["area-per-cap"] = mapped["areapercap"]
    for com in site.get("commodity", {}).values():
        for stor in com.get("storage", {}).values():
            mapped = {
                "instcapc": stor.get("inst-cap-c", stor.get("instcapc")),
                "caploc": stor.get("cap-lo-c", stor.get("caploc")),
                "capupc": stor.get("cap-up-c", stor.get("capupc")),
                "instcapp": stor.get("inst-cap-p", stor.get("instcapp")),
                "caplop": stor.get("cap-lo-p", stor.get("caplop")),
                "capupp": stor.get("cap-up-p", stor.get("capupp")),
                "invcostc": stor.get("inv-cost-c", stor.get("invcostc")),
                "fixcostc": stor.get("fix-cost-c", stor.get("fixcostc")),
                "varcostc": stor.get("var-cost-c", stor.get("varcostc")),
                "invcostp": stor.get("inv-cost-p", stor.get("invcostp")),
                "fixcostp": stor.get("fix-cost-p", stor.get("fixcostp")),
                "varcostp": stor.get("var-cost-p", stor.get("varcostp")),
            }
            convert_storage(mapped)
            if "inst-cap-c" in stor:
                stor["inst-cap-c"] = mapped["instcapc"]
                stor["cap-lo-c"] = mapped["caploc"]
                stor["cap-up-c"] = mapped["capupc"]
                stor["inst-cap-p"] = mapped["instcapp"]
                stor["cap-lo-p"] = mapped["caplop"]
                stor["cap-up-p"] = mapped["capupp"]
                stor["inv-cost-c"] = mapped["invcostc"]
                stor["fix-cost-c"] = mapped["fixcostc"]
                stor["var-cost-c"] = mapped["varcostc"]
                stor["inv-cost-p"] = mapped["invcostp"]
                stor["fix-cost-p"] = mapped["fixcostp"]
                stor["var-cost-p"] = mapped["varcostp"]
        demands = com.get("demand", {})
        if isinstance(demands, list):
            demand_items = demands
        else:
            demand_items = demands.values()
        for dem in demand_items:
            if not isinstance(dem, dict):
                continue
            if "steps" in dem and isinstance(dem["steps"], list):
                dem["steps"] = [x / 1000 if is_num(x) else x for x in dem["steps"]]
            if is_num(dem.get("quantity")):
                dem["quantity"] = dem["quantity"] / 1000


def main():
    procs_path = os.path.join(ROOT, "base_procs.json")
    with open(procs_path, encoding="utf-8") as f:
        data = json.load(f)
    for proc in data.get("process", {}).values():
        convert_process(proc)
    with open(procs_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("Updated base_procs.json")

    stor_path = os.path.join(ROOT, "base_stor.json")
    with open(stor_path, encoding="utf-8") as f:
        data = json.load(f)
    for stor in data.get("storage", {}).values():
        convert_storage(stor)
    with open(stor_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("Updated base_stor.json")

    demand_path = os.path.join(ROOT, "base_demand.json")
    with open(demand_path, encoding="utf-8") as f:
        data = json.load(f)
    for dem in data.get("demand", {}).values():
        if "steps" in dem:
            dem["steps"] = [x / 1000 if is_num(x) else x for x in dem["steps"]]
    with open(demand_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Updated base_demand.json")

    for sub in ("defaultProjects", "defaultProjectsLoaded"):
        folder = os.path.join(ROOT, sub)
        for name in os.listdir(folder):
            if not name.endswith(".urbs"):
                continue
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8") as f:
                project = json.load(f)
            for site in project.get("site", {}).values():
                convert_urbs_site(site)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(project, f, separators=(",", ":"))
            print(f"Updated {sub}/{name}")


if __name__ == "__main__":
    main()
