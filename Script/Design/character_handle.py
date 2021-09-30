import random
import math
import numpy
import datetime
from Script.Core import (
    cache_control,
    value_handle,
    constant,
    game_type,
)
from Script.Design import (
    attr_calculation,
    map_handle,
    attr_text,
    character,
)
from Script.Config import game_config, normal_config, character_config


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def init_character_list():
    """
    初始生成所有npc数据
    """
    init_character_tem()
    id_list = iter([i + 1 for i in range(len(cache.npc_tem_data))])
    npc_data_iter = iter(cache.npc_tem_data)
    for now_id, now_npc_data in zip(id_list, npc_data_iter):
        # print("now_id=",now_id,". now_npc_data:",now_npc_data)
        init_character(now_id, now_npc_data)


def init_character(character_id: int, character_tem: game_type.NpcTem):
    """
    按id生成角色属性
    Keyword arguments:
    character_id -- 角色id
    character_tem -- 角色生成模板数据
    """
    # print("进入init_character")
    # print("生成阶段，character_id :",character_id)
    # print("character_id=",character_id)
    now_character = game_type.Character()
    now_character.cid = character_id
    now_character.name = character_tem.Name
    now_character.sex = character_tem.Sex
    now_character.profession= character_tem.Profession
    now_character.race= character_tem.Race
    now_character.adv = character_tem.AdvNpc
    now_character.target_character_id = character_id
    now_character.favorability = attr_calculation.get_Favorability_zero()
    now_character.trust = attr_calculation.get_Trust_zero()
    now_character.ability = character_tem.Ability
    now_character.experience = character_tem.Experience
    now_character.talent = character_tem.Talent
    now_character.hit_point_max = character_tem.Hp
    now_character.mana_point_max = character_tem.Mp
    now_character.dormitory = character_tem.Dormitory
    # now_character.age = attr_calculation.get_age(character_id)
    if character_tem.Age != "":
        # print("character_tem = ",character_tem)
        # print("character_tem.Age = ",character_tem.Age)
        now_character.age = character_tem.Age
        # now_character.age = attr_calculation.get_age(character_tem.Age)
    # if character_tem.Chest:
    #     now_character.chest_tem = character_tem.Chest
    cache.character_data[character_id] = now_character
    character.init_attr(character_id)


def init_character_tem():
    """
    初始化角色模板数据
    """
    #init_random_npc_data()
    #npc_data = cache.random_npc_list
    #numpy.random.shuffle(npc_data)
    # print("初始化角色模板数据")
    cache.npc_tem_data = character_config.character_tem_list


# random_npc_max = normal_config.config_normal.random_npc_max
# random_teacher_proportion = normal_config.config_normal.proportion_teacher
# random_student_proportion = normal_config.config_normal.proportion_student
# age_weight_data = {
#     "teacher": random_teacher_proportion,
#     "student": random_student_proportion,
# }
# age_weight_regin_data = value_handle.get_region_list(age_weight_data)
# age_weight_regin_list = list(map(int, age_weight_regin_data.keys()))
# age_weight_max = sum([int(age_weight_data[age_weight]) for age_weight in age_weight_data])


# def init_random_npc_data() -> list:
#     """
#     生成所有随机npc的数据模板
#     """
#     cache.random_npc_list = []
#     for i in range(random_npc_max):
#         create_random_npc(i)


def create_random_npc(id) -> dict:
    """
    生成随机npc数据模板
    """
    # now_age_weight = random.randint(-1, age_weight_max - 1)
    # now_age_weight_regin = value_handle.get_next_value_for_list(now_age_weight, age_weight_regin_list)
    # age_weight_tem = age_weight_regin_data[now_age_weight_regin]
    random_npc_sex = get_rand_npc_sex()
    random_npc_name = attr_text.get_random_name_for_sex(random_npc_sex)
    random_npc_new_data = game_type.NpcTem()
    random_npc_new_data.Name = random_npc_name
    random_npc_new_data.Sex = random_npc_sex
    random_npc_new_data.Position = ["0"]
    random_npc_new_data.AdvNpc = 0
    # if random_npc_sex in {1, 2}:
    #     random_npc_new_data.Chest = attr_calculation.get_rand_npc_chest_tem()
    # else:
    #     random_npc_new_data.Chest = 0
    cache.random_npc_list.append(random_npc_new_data)


sex_weight_data = game_config.config_random_npc_sex_region
sex_weight_max = sum([sex_weight_data[weight] for weight in sex_weight_data])
sex_weight_regin_data = value_handle.get_region_list(sex_weight_data)
sex_weight_regin_list = list(map(int, sex_weight_regin_data.keys()))


def get_rand_npc_sex() -> int:
    """
    随机获取npc性别
    Return arguments:
    int -- 性别id
    """
    now_weight = random.randint(0, sex_weight_max - 1)
    weight_regin = value_handle.get_next_value_for_list(now_weight, sex_weight_regin_list)
    return sex_weight_regin_data[weight_regin]


def init_character_dormitory():
    """
    分配角色宿舍
    玩家分配到博士房间，角色分配到csv里所写的宿舍名所对应的房间坐标
    """
    Dr_room = {
        key: constant.place_data[key] for key in constant.place_data if "Dr_room" in key
    }
    Dr_room = {
        x: 0 for j in [k[1] for k in sorted(Dr_room.items(), key=lambda x: x[0])] for x in j
    }
    dormitory = {
        key: constant.place_data[key] for key in constant.place_data if "Dormitory" in key
    }
    dormitory = {
        x: 0 for j in [k[1] for k in sorted(dormitory.items(), key=lambda x: x[0])] for x in j
    }
    # print("Dr_room :",Dr_room)
    # print("dormitory :",dormitory)
    # print("cache.scene_data[list(Dr_room.keys())[0]].scene_name :",cache.scene_data[list(Dr_room.keys())[0]].scene_name)
    for character_id in cache.character_data:
        # print("character_id :",character_id)
        # print("cache.character_data[character_id].dormitory :",cache.character_data[character_id].dormitory)
        if character_id == 0:
            now_room = list(Dr_room.keys())[0]
            cache.character_data[character_id].dormitory = now_room
        else:
            # print("list(dormitory.keys()) :",list(dormitory.keys()))
            for n in list(dormitory.keys()):
                # print("n :",n)
                if cache.scene_data[n].scene_name == cache.character_data[character_id].dormitory:
                    cache.character_data[character_id].dormitory = n
        # print("cache.character_data[character_id].dormitory :",cache.character_data[character_id].dormitory)


def init_character_position():
    """初始化角色位置"""
    for character_id in cache.character_data:
        character_position = cache.character_data[character_id].position
        character_dormitory = cache.character_data[character_id].dormitory
        character_dormitory = map_handle.get_map_system_path_for_str(character_dormitory)
        # print("character_dormitory = ",character_dormitory)
        map_handle.character_move_scene(character_position, character_dormitory, character_id)


def add_favorability(
    character_id: int,
    target_id: int,
    now_add_favorability: int,
    target_change: game_type.TargetChange,
    now_time: datetime.datetime,
):
    """
    增加目标角色对当前角色的好感
    Keyword arguments:
    character_id -- 当前角色id
    target_id -- 目标角色id
    now_add_favorability -- 增加的好感
    target_change -- 角色状态改变对象
    now_time -- 增加好感的时间
    """
    target_data: game_type.Character = cache.character_data[target_id]
    target_data.favorability.setdefault(character_id, 0)
    if target_change is not None:
        target_change.status_data.setdefault(12, 0)
    old_add_favorability = now_add_favorability
    # if 12 in target_data.status:
    #     disgust = target_data.status[12]
    #     if disgust:
    #         if now_add_favorability >= disgust:
    #             now_add_favorability -= disgust
    #             target_data.status[12] = 0
    #             if now_add_favorability:
    #                 target_data.favorability[character_id] += now_add_favorability
    #                 if target_change is not None:
    #                     target_change.favorability += now_add_favorability
    #             del target_data.status[12]
    #         else:
    #             target_data.status[12] -= now_add_favorability
    #             if target_change is not None:
    #                 target_change.status[12] -= now_add_favorability
    #     else:
    #         target_data.favorability[character_id] += now_add_favorability
    #         if target_change is not None:
    #             target_change.favorability += now_add_favorability
    # else:
    target_data.favorability[character_id] += now_add_favorability
    if target_change is not None:
        target_change.favorability += now_add_favorability
    target_data.social_contact_last_cut_down_time[character_id] = now_time
    if target_change is not None:
        add_favorability(target_id, character_id, old_add_favorability, None, now_time)
