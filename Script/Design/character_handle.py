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
    # 检测基础干员并加入已有干员列表
    if now_character.name in {"阿米娅","凯尔希","可露希尔","特蕾西娅","华法琳","温蒂","杜宾"}:
        cache.npc_id_got.add(character_id)
    cache.npc_name_data.add(now_character.name) # 加入到已有干员姓名中
    now_character.sex = character_tem.Sex
    now_character.profession= character_tem.Profession
    now_character.race= character_tem.Race
    now_character.adv = character_tem.AdvNpc
    now_character.target_character_id = character_id
    now_character.favorability = {0:0}
    now_character.trust = 0
    now_character.ability = character_tem.Ability
    now_character.experience = character_tem.Experience
    now_character.talent = character_tem.Talent
    now_character.hit_point_max = character_tem.Hp
    now_character.mana_point_max = character_tem.Mp
    now_character.dormitory = character_tem.Dormitory
    now_character.token_text = character_tem.Token
    # if character_tem.Chest:
    #     now_character.chest_tem = character_tem.Chest
    now_character.cloth = attr_calculation.get_cloth_zero()
    now_character.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
    for cloth_id in character_tem.Cloth:
        type = game_config.config_clothing_tem[cloth_id].clothing_type
        # print(f"debug cloth_id = {cloth_id},name = {game_config.config_clothing_tem[cloth_id].name},type = {type}")
        now_character.cloth.cloth_wear[type].append(cloth_id)
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


def born_new_character(mother_id):
    """
    生成新的角色模板数据
    """
    #init_random_npc_data()
    #npc_data = cache.random_npc_list
    #numpy.random.shuffle(npc_data)
    # print("初始化角色模板数据")
    mom_character_data: game_type.Character = cache.character_data[mother_id]
    now_tem = game_type.NpcTem()
    now_tem.Name = "女儿"
    now_tem.Sex = 1
    now_tem.Profession = random.randint(0,8)
    now_tem.Race = mom_character_data.race
    now_tem.AdvNpc = random.randint(9000,9999)
    now_tem.Ability = {}
    now_tem.Experience = {}
    now_tem.Talent = {}
    now_tem.Hp = 1
    now_tem.Mp = 1
    now_tem.Dormitory = "无"
    now_tem.Token = "无"
    now_tem.Cloth = []
    cache.npc_tem_data.append(now_tem)
    now_id  = len(cache.npc_tem_data) + 1
    # cache.npc_id_got.add(now_id)
    init_character(now_id, cache.npc_tem_data[-1])

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
    now_room = list(Dr_room.keys())[0]
    cache.character_data[0].dormitory = now_room
    dormitory = {
        key: constant.place_data[key] for key in constant.place_data if "Dormitory" in key
    }
    dormitory = {
        x: 0 for j in [k[1] for k in sorted(dormitory.items(), key=lambda x: x[0])] for x in j
    }
    special_dormitory = {
        key: constant.place_data[key] for key in constant.place_data if "Special_Dormitory" in key
    }
    special_dormitory = {
        x: 0 for j in [k[1] for k in sorted(special_dormitory.items(), key=lambda x: x[0])] for x in j
    }
    # print("dormitory :",dormitory)
    # print("cache.scene_data[list(Dr_room.keys())[0]].scene_name :",cache.scene_data[list(Dr_room.keys())[0]].scene_name)
    npc_count = 0
    cache.npc_id_got.discard(0)
    for character_id in cache.npc_id_got:
        character_data = cache.character_data[character_id]
        # print(f"{character_data.name}：{character_data.dormitory}")
        # 普通干员每两个人住一个房间
        if character_data.dormitory == "无":
            n = npc_count // 2
            now_room = list(dormitory.keys())[n]
            # print(f"debug now_room = {now_room}")
            character_data.dormitory = now_room
            npc_count += 1
        # 有单独宿舍的干员住在对应宿舍
        else:
            for n in list(dormitory.keys()):
                if cache.scene_data[n].scene_name == character_data.dormitory:
                    character_data.dormitory = n
                    # print(f"debug n :{n}")


def init_character_position():
    """初始化角色位置"""
    id_list = cache.npc_id_got
    id_list.add(0)
    for character_id in id_list:
        character_position = cache.character_data[character_id].position
        character_dormitory = cache.character_data[character_id].dormitory
        character_dormitory = map_handle.get_map_system_path_for_str(character_dormitory)
        # print("character_dormitory = ",character_dormitory)
        map_handle.character_move_scene(character_position, character_dormitory, character_id)


def init_character_facility_open():
    """初始化角色开放设施"""
    for open_cid in game_config.config_facility_open:
        for character_id in cache.npc_id_got:
            # 跳过玩家id
            if character_id == 0:
                continue
            if game_config.config_facility_open[open_cid].NPC_id == cache.character_data[character_id].adv:
                cache.base_resouce.facility_open[open_cid] = True
                break

def get_new_character(character_id: int):
    """获得新角色"""
    cache.npc_id_got.add(character_id)
    character_data = cache.character_data[character_id]
    init_character_dormitory()

    # 初始化新角色位置
    character_position = character_data.position
    pl_postion = cache.character_data[0].position
    map_handle.character_move_scene(character_position, pl_postion, character_id)

    # 新角色原地等待30分钟
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_WAIT

    # 如果满足设施开放的前提条件，则开放该设施
    for open_cid in game_config.config_facility_open:
        if game_config.config_facility_open[open_cid].NPC_id == character_data.adv:
            cache.base_resouce.facility_open[open_cid] = True


def add_favorability(
    character_id: int,
    target_id: int,
    now_add_favorability: int,
    change_data: game_type.CharacterStatusChange,
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
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.favorability.setdefault(target_id, 0)
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

    # 对自己操作
    if (character_id != 0) and (character_data.target_character_id == 0):
        character_data.favorability[target_id] += now_add_favorability
        # print(f"debug change_data = {change_data}")
        if change_data is not None:
            change_data.favorability += now_add_favorability

    # 对交互对象操作
    target_data.favorability[character_id] += now_add_favorability
    if target_change is not None:
        target_change.favorability += now_add_favorability
    # target_data.social_contact_last_cut_down_time[character_id] = now_time
    # if target_change is not None:
    #     add_favorability(target_id, character_id, old_add_favorability, None, None, now_time)
