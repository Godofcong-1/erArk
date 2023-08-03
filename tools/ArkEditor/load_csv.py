import os
import csv
import cache_control

premise_path = "tools\Premise.csv"
status_path = "tools\Status.csv"
effect_path = "tools\Effect.csv"


def load_config():
    """载入配置文件"""
    with open(premise_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.premise_data[i["cid"]] = i["premise"]
            cache_control.premise_type_data.setdefault(i["premise_type"], set())
            cache_control.premise_type_data[i["premise_type"]].add(i["cid"])
    with open(status_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.status_data[i["cid"]] = i["status"]
    with open(effect_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.effect_data[i["cid"]] = i["effect"]
            cache_control.effect_type_data.setdefault(i["effect_type"], set())
            cache_control.effect_type_data[i["effect_type"]].add(i["cid"])
