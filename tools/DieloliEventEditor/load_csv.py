import os
import csv
import cache_control

# premise_path = os.path.join("..","premise.csv")
# status_path = os.path.join("..","Status.csv")
# settle_path = os.path.join("..","Settle.csv")
premise_path = "C:/code/work/erArk/tools/premise.csv"
status_path = "C:/code/work/erArk/tools/Status.csv"
settle_path = "C:/code/work/erArk/tools/Settle.csv"


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
    with open(settle_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.settle_data[i["settle_id"]] = i["settle_info"]
            cache_control.settle_type_data.setdefault(i["settle_type"],{})
            cache_control.settle_type_data[i["settle_type"]].setdefault(i["son_type"],set())
            cache_control.settle_type_data[i["settle_type"]][i["son_type"]].add(i["settle_id"])
