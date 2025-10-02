import os
import csv
import cache_control

premise_path = "csv/Premise.csv"
premise_group_path = "csv/PremiseGroup.csv"
behavior_data_path = "csv/Behavior_Data.csv"
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
bondage_path = "csv/Bondage.csv"
roleplay_path = "csv/Roleplay.csv"
item_path = "csv/Item.csv"
gift_items_path = "csv/Gift_Items.csv"
resource_path = "csv/Resource.csv"

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
    with open(behavior_data_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "状态描述配置":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.behavior_data[i["en_name"]] = i["name"]
            cache_control.behavior_all_data[i["en_name"]] = i
            # print(f"debug i[cid] = {i['cid']}, type = {type(i['cid'])}, status = {i['status']}, type = {type(i['status'])}")
            cache_control.behavior_type_data.setdefault(i["type"], [])
            cache_control.behavior_type_data[i["type"]].append(i["en_name"])
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
    with open(bondage_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "绳子捆绑":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.bondage_data[i["cid"]] = i["name"]
    with open(roleplay_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "角色扮演列表":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.roleplay_data[i["cid"]] = i["name"]
    with open(item_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "道具配置数据":
                    continue
                else:
                    read_flag = True
                    continue
            cache_control.item_data[i["cid"]] = i["name"]
    with open(gift_items_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "礼物物品":
                    continue
                else:
                    read_flag = True
                    continue
            if i["item_id"] == '0':
                continue
            # 跳过没实装的礼物
            if i["todo"] == '1':
                continue
            cache_control.gift_items_data[i["cid"]] = i["item_id"]
    with open(resource_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        read_flag = False
        for i in now_read:
            if read_flag == False:
                if i["cid"] != "各类基地使用资源一览":
                    continue
                else:
                    read_flag = True
                    continue
            new_cid = str(int(i["cid"]))
            cache_control.resource_data[new_cid] = i["name"]
            if i["specialty"] != '0':
                cache_control.specialty_data.setdefault(i["specialty"], [])
                cache_control.specialty_data[i["specialty"]].append(new_cid)

def load_commission_csv(file_path):
    """
    读取外勤委托CSV文件
    参数:
        file_path: str 文件路径
    返回:
        commissions: list[Commission] 委托对象列表
    功能:
        解析CSV文件，生成委托对象列表
    """
    from game_type import Commission  # 修正为本地导入，避免包路径问题
    commissions = []
    with open(file_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        read_flag = False
        for row in reader:
            if read_flag == False:
                if row["cid"] != "委托任务表":
                    continue
                else:
                    read_flag = True
                    continue
            # 创建Commission对象并加入列表
            commission = Commission(
                row["cid"], row["name"], row["country_id"], row["level"], row["type"],
                row["people"], row["time"], row["demand"], row["reward"],
                row["related_id"], row["special"], row["description"]
            )
            commissions.append(commission)
    return commissions

def save_commission_csv(file_path, commissions):
    """
    保存外勤委托CSV文件
    参数:
        file_path: str 文件路径
        commissions: list[Commission] 委托对象列表
    返回:
        None
    功能:
        将委托对象列表写回CSV文件
    """
    fieldnames = ["cid", "name", "country_id", "level", "type", "people", "time", "demand", "reward", "related_id", "special", "description"]
    text = "委托id,委托名字,国家id(-1为通用),委托等级,委托类型,派遣人数,耗时天数,具体需求,具体奖励(a能力、e经验、j宝珠、t_素质编号_0为取消1为获得、r资源、c_角色adv编号_0不包含1包含、招募_adv编号_0未招募1已招募、攻略_adv编号_程度0~4、m_委托编号_-1不可完成0可以进行1已完成、声望_0为当地其他为对应势力id_加值为小数点后两位),关联的委托id,特殊委托,委托介绍\nint,str,int,int,str,int,int,str,str,int,int,str\n0,1,0,0,0,0,0,0,0,0,0,1\n委托任务表,,,,,,,,,,,"
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # 写入文件头部的说明信息
        f.write(text + "\n")
        for c in commissions:
            writer.writerow({
                "cid": c.cid, "name": c.name, "country_id": c.country_id, "level": c.level, "type": c.type,
                "people": c.people, "time": c.time, "demand": c.demand, "reward": c.reward,
                "related_id": c.related_id, "special": c.special, "description": c.description
            })
