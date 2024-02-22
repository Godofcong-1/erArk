import random
import bisect
from typing import List
from Script.Core import (
    cache_control,
    constant,
    game_type,
)
from Script.Design import handle_premise, map_handle
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def get_random_name_for_sex(sex_grade: str) -> str:
    """
    按性别随机生成姓名
    Keyword arguments:
    sex_grade -- 性别
    """
    while 1:
        family_random = random.randint(1, constant.family_region_int_list[-1])
        family_region_index = bisect.bisect_left(constant.family_region_int_list, family_random)
        family_region = constant.family_region_int_list[family_region_index]
        family_name = constant.family_region_list[family_region]
        if sex_grade == "Man":
            sex_judge = 1
        elif sex_grade == "Woman":
            sex_judge = 0
        else:
            sex_judge = random.randint(0, 1)
        if sex_judge == 0:
            name_random = random.randint(1, constant.girls_region_int_list[-1])
            name_region_index = bisect.bisect_left(constant.girls_region_int_list, name_random)
            name_region = constant.girls_region_int_list[name_region_index]
            name = constant.girls_region_list[name_region]
        else:
            name_random = random.randint(1, constant.boys_region_int_list[-2])
            name_region_index = bisect.bisect_left(constant.boys_region_int_list, name_random)
            name_region = constant.boys_region_int_list[name_region_index]
            name = constant.boys_region_list[name_region]
        now_name = f"{family_name}{name}"
        if now_name not in cache.npc_name_data:
            cache.npc_name_data.add(now_name)
            return family_name + name


def get_stature_text(character_id: int) -> str:
    """
    按角色Id获取身材描述信息
    Keyword arguments:
    character_id -- 角色Id
    Return arguments:
    str -- 身材描述文本
    """
    descript_data = {}
    for descript in game_config.config_stature_description_text:
        descript_tem = game_config.config_stature_description_text[descript]
        now_weight = 0
        if descript in game_config.config_stature_description_premise_data:
            for premise in game_config.config_stature_description_premise_data[descript]:
                now_add_weight = handle_premise.handle_premise(premise, character_id)
                if now_add_weight:
                    now_weight += now_add_weight
                else:
                    now_weight = 0
                    break
        else:
            now_weight = 1
        if now_weight:
            descript_data.setdefault(now_weight, set())
            descript_data[now_weight].add(descript_tem.text)
    if len(descript_data):
        max_weight = max(descript_data.keys())
        return random.choice(list(descript_data[max_weight]))
    return ""


def get_scene_path_text(scene_path: List[str]) -> str:
    """
    从场景路径获取场景地址描述文本
    例:控制中枢-博士办公室
    Keyword arguments:
    scene_path -- 场景路径
    Return arguments:
    str -- 场景地址描述文本
    """
    map_list = map_handle.get_map_hierarchy_list_for_scene_path(scene_path, [])
    map_list.reverse()
    scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
    scene_path_text = ""
    for now_map in map_list:
        now_map_map_system_str = map_handle.get_map_system_path_str_for_list(now_map)
        map_name = cache.map_data[now_map_map_system_str].map_name
        scene_path_text += map_name + "-"
    return scene_path_text + cache.scene_data[scene_path_str].scene_name


def get_map_path_text(map_path: List[str]) -> str:
    """
    从地图路径获取地图地址描述文本
    例:控制中枢
    Keyword arguments:
    map_path -- 地图路径
    Return arguments:
    str -- 地图地址描述文本
    """
    map_list = map_handle.get_map_hierarchy_list_for_scene_path(map_path, [])
    map_list.reverse()
    map_list.append(map_path)
    now_path_text = ""
    for now_map in map_list:
        now_map_map_system_str = map_handle.get_map_system_path_str_for_list(now_map)
        map_name = cache.map_data[now_map_map_system_str].map_name
        now_path_text += map_name + "-"
    return now_path_text.rstrip("-")


def get_value_text(value: float) -> str:
    """
    获取数值显示的文本
    Keyword arguments:
    value -- 数值
    Return arguments:
    str -- 文本显示
    """
    value = round(value, 2)
    company = ["K", "M", "G", "T", "P", "E", "Z", "Y", "B", "N", "D"]
    int_value = int(value)
    value_str = str(int_value)
    if len(value_str) < 4:
        value_str = str(value)
    else:
        company_index = int((len(value_str) - 1) / 3)
        if company_index >= len(company):
            company_index = len(company) - 1
        value_str = value_str[: -company_index * 3]
        value_str += company[company_index]
    if int(value) >= 0:
        value_str = "+" + value_str
    return value_str


def get_semen_now_text(level: int,position: int) -> str:
    """
    按当前部位精液覆盖等级(level)和部位(position)返回精液文本
    [0"头发",1"脸部",2"嘴部",3"胸部",4"腋部",5"手部",6"小穴",7"后穴",8"尿道",9"腿部",10"脚部"]
    Keyword arguments:
    value -- 精液量
    Return arguments:
    level -- 精液覆盖等级
    """
    if level == 0:
        return "没有粘上精液"
    elif level == 1:
        return "被射上了一点精液"
    elif level == 2:
        return "被射上了精液"
    elif level == 3:
        return "被射上了很多精液"
    elif level == 4:
        return "被射上了非常多的精液"
    elif level == 5:
        return "被射上了多得数不清的精液"
