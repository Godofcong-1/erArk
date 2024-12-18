import os
import csv
import cache_control

premise_path = "csv/Premise.csv"
premise_group_path = "csv/PremiseGroup.csv"
status_path = "csv/Status.csv"
effect_path = "csv/Effect.csv"
ability_path = "csv/Ability.csv"
state_path = "csv/CharacterState.csv"
experience_path = "csv/Experience.csv"
juel_path = "csv/Juel.csv"
talent_path = "csv/Talent.csv"
birthplace_path = "csv/Birthplace.csv"
nation_path = "csv/Nation.csv"
profession_path = "csv/Profession.csv"
race_path = "csv/Race.csv"
body_path = "csv/BodyPart.csv"
clothing_path = "csv/ClothingType.csv"
organ_path = "csv/Organ.csv"


def load_config():
    """载入配置文件"""
    with open(premise_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.premise_data[i["cid"]] = i["premise"]
            cache_control.premise_type_data.setdefault(i["premise_type"], set())
            cache_control.premise_type_data[i["premise_type"]].add(i["cid"])
    with open(premise_group_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            if "&" in i["premise_cid"]:
                promise_list = i["premise_cid"].split("&")
                if len(promise_list) > 1:
                    cache_control.premise_group_data[i["cid"]] = promise_list
    with open(status_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.status_data[i["cid"]] = i["status"]
            cache_control.status_all_data[i["cid"]] = i
            # print(f"debug i[cid] = {i['cid']}, type = {type(i['cid'])}, status = {i['status']}, type = {type(i['status'])}")
            cache_control.status_type_data.setdefault(i["type"], [])
            cache_control.status_type_data[i["type"]].append(i["cid"])
    with open(effect_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        for i in now_read:
            cache_control.effect_data[i["cid"]] = i["effect"]
            cache_control.effect_type_data.setdefault(i["effect_type"], set())
            cache_control.effect_type_data[i["effect_type"]].add(i["cid"])
    with open(ability_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "能力对应类型和文字描述":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.ability_data[i["cid"]] = i["name"]
    with open(state_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "角色状态属性表":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.state_data[i["cid"]] = i["name"]
    with open(experience_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "经验名字":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.experience_data[i["cid"]] = i["name"]
    with open(juel_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "珠名字":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.juel_data[i["cid"]] = i["name"]
    with open(talent_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "素质对应类型和文字描述":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.talent_data[i["cid"]] = i["name"]
    # print(f"debug cache_control.talent_data = {cache_control.talent_data}")
    with open(birthplace_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "出生地列表":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.birthplace_data[i["cid"]] = i["name"]
    with open(nation_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "势力列表":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.nation_data[i["cid"]] = i["name"]
    with open(profession_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "职业类型名称":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.profession_data[i["cid"]] = i["name"]
    with open(race_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "种族类型名称":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.race_data[i["cid"]] = i["name"]
    with open(body_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "身体部位表":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.body_data[i["cid"]] = i["name"]
    with open(clothing_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "衣服种类配置":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.clothing_data[i["cid"]] = i["name"]
    with open(organ_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "器官对应性别限定和文字描述":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.organ_data[i["cid"]] = i["name"]
