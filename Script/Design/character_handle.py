import random
from types import FunctionType
from Script.Core import (
    cache_control,
    value_handle,
    constant,
    game_type,
    get_text,
)
from Script.Design import (
    attr_calculation,
    map_handle,
    attr_text,
    character,
    character_behavior,
    basement,
    game_time,
)
from Script.Config import game_config, config_def, character_config


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def init_character_list():
    """
    初始生成所有npc数据
    """
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
    if now_character.name in constant.first_NPC_name_set:
        cache.npc_id_got.add(character_id)
    cache.npc_name_data.add(now_character.name) # 加入到已有干员姓名中
    now_character.sex = character_tem.Sex
    now_character.profession= character_tem.Profession
    now_character.race= character_tem.Race
    now_character.relationship.nation= character_tem.Nation
    now_character.relationship.birthplace= character_tem.Birthplace
    # 如果有母亲的话则加上亲子关系
    if character_tem.Mother_id:
        now_character.relationship.father_id = 0
        now_character.relationship.mother_id = character_tem.Mother_id
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
    # 生成衣服
    now_character.cloth = attr_calculation.get_cloth_zero()
    now_character.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
    for cloth_id in character_tem.Cloth:
        type = game_config.config_clothing_tem[cloth_id].clothing_type
        # print(f"debug {character_tem.Name} cloth_id = {cloth_id},name = {game_config.config_clothing_tem[cloth_id].name},type = {type}")
        now_character.cloth.clothing_tem.append(cloth_id)
        now_character.cloth.cloth_wear[type].append(cloth_id)
        # if type in [6,9] and len(now_character.cloth.cloth_wear[type]):
        #     print(f"debug {character_tem.Name} cloth_wear = {now_character.cloth.cloth_wear}")
    # print(f"debug {character_tem.Name} cloth_wear = {now_character.cloth.cloth_wear}")
    # 生成藏品
    if 0 in cache.character_data:
        pl_character_data = cache.character_data[0]
        pl_character_data.pl_collection.token_list[character_id] = False
        pl_character_data.pl_collection.first_panties[character_id] = ""
        pl_character_data.pl_collection.npc_panties[character_id] = []
        pl_character_data.pl_collection.npc_socks[character_id] = []
    # 文本颜色
    if character_tem.TextColor:
        now_character.text_color = character_tem.TextColor
    # 赋予口上大小
    now_character.talk_size = character_tem.Talk_Size
    # 最后集成
    cache.character_data[character_id] = now_character
    character.init_attr(character_id)
    return cache.character_data[character_id]


def first_NPC_work():
    """
    初始角色的工作安排
    """
    for character_id in cache.npc_id_got:
        character_data = cache.character_data[character_id]
        if character_data.name in {"可露希尔"}:
            character_data.work.work_type = 21
        elif character_data.name in {"凯尔希","华法琳"}:
            character_data.work.work_type = 61
        elif character_data.name in {"特蕾西娅"}:
            character_data.work.work_type = 71
        elif character_data.name in {"杜宾"}:
            character_data.work.work_type = 91
    basement.update_work_people()


def init_character_tem():
    """
    初始化角色模板数据
    """
    #init_random_npc_data()
    #npc_data = cache.random_npc_list
    #numpy.random.shuffle(npc_data)
    # print("初始化角色模板数据")
    cache.npc_tem_data = character_config.character_tem_list


def create_empty_character_tem():
    """
    生成空的角色模板数据
    """
    now_tem = game_type.NpcTem()
    now_tem.Sex = 1
    now_tem.Nation = 0
    now_tem.Birthplace = 0
    now_tem.Ability = {}
    now_tem.Experience = {}
    now_tem.Dormitory = "无"
    now_tem.Token = "无"
    now_tem.Cloth = []
    return now_tem


def born_new_character(mother_id,child_name):
    """
    生成新的小孩模板数据
    """
    #init_random_npc_data()
    #npc_data = cache.random_npc_list
    #numpy.random.shuffle(npc_data)
    # print("初始化角色模板数据")
    mom_character_data: game_type.Character = cache.character_data[mother_id]
    now_tem = create_empty_character_tem()
    now_tem.Name = child_name
    now_tem.Profession = random.randint(0,8)
    now_tem.Race = mom_character_data.race
    now_tem.Mother_id = mother_id
    now_tem.AdvNpc = random.randint(9000,9999)
    # 基础的素质
    now_tem.Talent = {0:1,1:1,2:1,3:1,4:1,6:1,7:1,101:1,121:1,126:1,129:1,131:1,451:1}
    # 遗传母亲的可遗传素质
    for talent_id in game_config.config_talent:
        if game_config.config_talent[talent_id].heredity and mom_character_data.talent[talent_id]:
            # 跳过胸部、臀部、腿和脚
            if 122 <= talent_id <= 132:
                continue
            now_tem.Talent[talent_id] = 1
    now_tem.Talent[121] = 1
    now_tem.Hp = random.randint(1000,2000)
    now_tem.Mp = random.randint(1000,2000)
    cache.npc_tem_data.append(now_tem)
    now_id  = len(cache.npc_tem_data)
    # 给父母加上该孩子的社会关系
    cache.character_data[0].relationship.child_id_list.append(now_id)
    mom_character_data.relationship.child_id_list.append(now_id)
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
    角色分配到csv里所写的宿舍名所对应的房间坐标
    """
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
            # print(f"debug n :{n}, len(dormitory) :{len(dormitory)}")
            now_room = list(dormitory.keys())[n]
            # print(f"debug now_room = {now_room}")
            character_data.dormitory = now_room
            npc_count += 1
        # 有单独宿舍的干员住在对应宿舍
        else:
            for n in list(dormitory.keys()):
                if cache.scene_data[n].scene_name == character_data.dormitory:
                    # 如果要住宿舍的话，那先检测宿舍是否已经有人住了
                    if "宿舍" in character_data.dormitory:
                        already_live = False
                        for now_character_id in cache.npc_id_got:
                            if now_character_id == character_id:
                                continue
                            now_character_data = cache.character_data[now_character_id]
                            # 如果已经有人住了，则置flag为true，跳出循环
                            if now_character_data.dormitory == character_data.dormitory:
                                already_live = True
                                break
                        # 如果已经有人住了，则换成普通宿舍，重新分配
                        if already_live:
                            character_data.dormitory = "无"
                            init_character_dormitory()
                            break
                        else:
                            character_data.dormitory = n
                            # print(f"debug n :{n}")
                            break
                    # 非宿舍的话直接住
                    else:
                        character_data.dormitory = n
                        # print(f"debug n :{n}")
                        break


def new_character_get_dormitory(character_id: int):
    """
    给新角色分配宿舍
    Keyword arguments:
    character_id -- 角色id
    """
    character_data = cache.character_data[character_id]
    # 分为访客和普通干员
    if character_id in cache.rhodes_island.visitor_info:
        guest_room = {
            key: constant.place_data[key] for key in constant.place_data if "Guest_Room" in key
        }
        guest_room = {
            x: 0 for j in [k[1] for k in sorted(guest_room.items(), key=lambda x: x[0])] for x in j
        }
        npc_count = 0
        for now_character_id in cache.npc_id_got:
            now_character_data = cache.character_data[now_character_id]
            # 客房每个人住一间
            if "客房" in now_character_data.dormitory:
                npc_count += 1
        n = npc_count
        now_room = list(guest_room.keys())[n]
        character_data.dormitory = now_room
    else:
        dormitory = {
            key: constant.place_data[key] for key in constant.place_data if "Dormitory" in key
        }
        dormitory = {
            x: 0 for j in [k[1] for k in sorted(dormitory.items(), key=lambda x: x[0])] for x in j
        }
        npc_count = 0
        for now_character_id in cache.npc_id_got:
            now_character_data = cache.character_data[now_character_id]
            # 普通干员每两个人住一个房间
            if "宿舍" in now_character_data.dormitory:
                npc_count += 1
        n = npc_count // 2
        now_room = list(dormitory.keys())[n]
        character_data.dormitory = now_room


def init_character_position():
    """初始化角色位置"""
    id_list = cache.npc_id_got
    id_list.add(0)
    for character_id in id_list:
        character_position = cache.character_data[character_id].position
        character_dormitory = cache.character_data[character_id].dormitory
        character_dormitory_str = map_handle.get_map_system_path_for_str(character_dormitory)
        # print("character_dormitory = ",character_dormitory)
        map_handle.character_move_scene(character_position, character_dormitory_str, character_id)
    character_position = cache.character_data[0].position
    map_handle.character_move_scene(["0","0"], character_position, 0)


def init_character_entertainment():
    """初始化角色娱乐"""
    id_list = cache.npc_id_got
    id_list.add(0)
    for character_id in id_list:
        character_behavior.get_chara_entertainment(character_id)


def init_character_facility_open():
    """初始化角色开放设施"""
    for open_cid in game_config.config_facility_open:
        if game_config.config_facility_open[open_cid].NPC_id == 0:
            continue
        for character_id in cache.npc_id_got:
            # 跳过玩家id
            if character_id == 0:
                continue
            if game_config.config_facility_open[open_cid].NPC_id == cache.character_data[character_id].adv:
                cache.rhodes_island.facility_open[open_cid] = True
                break


def get_new_character(character_id: int, visitor_flag: bool = False):
    """
    获得新角色
    Keyword arguments:
    character_id -- 角色id
    visitor_flag -- 是否为访客
    """
    from Script.Settle import default

    # 角色上线
    default.handle_chara_on_line(character_id, 1, change_data = game_type.CharacterStatusChange, now_time = cache.game_time)

    character_data = cache.character_data[character_id]
    # 清零全特殊状态flag
    character_data.sp_flag = game_type.SPECIAL_FLAG()

    if visitor_flag:
        # 根据访客区的等级，赋予对应的停留时间
        now_level = cache.rhodes_island.facility_level[13]
        facility_cid = game_config.config_facility_effect_data[_("访客区")][int(now_level)]
        facility_effect = game_config.config_facility_effect[facility_cid].effect
        stay_days = facility_effect
        end_time = game_time.get_sub_date(day = stay_days,old_date = cache.game_time)
        cache.rhodes_island.visitor_info[character_id] = end_time
        # 赋予访客flag
        character_data.sp_flag.vistor = 1
    else:
        # 如果满足设施开放的前提条件，则开放该设施
        for open_cid in game_config.config_facility_open:
            if game_config.config_facility_open[open_cid].NPC_id and game_config.config_facility_open[open_cid].NPC_id == character_data.adv:
                cache.rhodes_island.facility_open[open_cid] = True

    # 分配角色宿舍
    if visitor_flag == False:
        new_character_get_dormitory(character_id)
    # 客人则分配客房
    else:
        # 获得空闲客房id
        guest_room_id = basement.get_empty_guest_room_id()
        if guest_room_id:
            # 全客房列表
            guest_room_dict = {
                key: constant.place_data[key] for key in constant.place_data if "Guest_Room" in key
            }
            # 遍历到同名客房
            for guest_room_full_path in guest_room_dict:
                guest_room_name = guest_room_full_path.split('\\')
                now_room = game_config.config_facility_open[guest_room_id].name
                if now_room == guest_room_name[-1]:
                    character_data.dormitory = guest_room_full_path
                    break
        else:
            new_character_get_dormitory(character_id)

    # 初始化新角色位置
    character_position = character_data.position
    office_postion = ['中枢', '博士办公室']
    map_handle.character_move_scene(character_position, office_postion, character_id)

    # 初始化新角色娱乐
    character_behavior.get_chara_entertainment(character_id)

    # 新角色原地等待30分钟
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.behavior.duration = 30
    character_data.behavior.start_time = cache.game_time
    character_data.state = constant.CharacterStatus.STATUS_WAIT


def visitor_to_operator(character_id: int):
    """
    访客留下成为干员
    Keyword arguments:
    character_id -- 角色id
    """

    character_data = cache.character_data[character_id]

    # flag置为已访问
    character_data.sp_flag.vistor = 2

    # 从访客列表中移除
    del cache.rhodes_island.visitor_info[character_id]

    # 如果满足设施开放的前提条件，则开放该设施
    for open_cid in game_config.config_facility_open:
        if game_config.config_facility_open[open_cid].NPC_id and game_config.config_facility_open[open_cid].NPC_id == character_data.adv:
            cache.rhodes_island.facility_open[open_cid] = True

    # 重新分配角色宿舍
    new_character_get_dormitory(character_id)


def visitor_leave(character_id: int):
    """
    访客离开
    Keyword arguments:
    character_id -- 角色id
    """

    character_data = cache.character_data[character_id]

    # flag置为已访问
    character_data.sp_flag.vistor = 2

    # 从访客列表中移除
    del cache.rhodes_island.visitor_info[character_id]

    # 从已有干员列表中移除
    cache.npc_id_got.discard(character_id)

    # 位置初始化
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if character_id in cache.scene_data[scene_path_str].character_list:
        cache.scene_data[scene_path_str].character_list.remove(character_id)
    character_data.position = ["0", "0"]


def add_favorability(
    character_id: int,
    target_id: int,
    now_add_favorability: int,
    change_data: game_type.CharacterStatusChange,
    target_change: game_type.TargetChange,
):
    """
    增加目标角色对当前角色的好感
    Keyword arguments:
    character_id -- 当前角色id
    target_id -- 目标角色id
    now_add_favorability -- 增加的好感
    target_change -- 角色状态改变对象
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

    # NPC对玩家
    if (character_id != 0) and (character_data.target_character_id == 0):
        character_data.favorability[target_id] += now_add_favorability
        character_data.favorability[target_id] = min(100000, character_data.favorability[target_id])
        # print(f"debug change_data = {change_data}")
        if change_data is not None:
            change_data.favorability += now_add_favorability

    # 对NPC
    if character_data.target_character_id != 0:
        target_data.favorability[character_id] += now_add_favorability
        target_data.favorability[character_id] = min(100000, target_data.favorability[character_id])
        if target_change is not None:
            target_change.favorability += now_add_favorability
    # target_data.social_contact_last_cut_down_time[character_id] = now_time
    # if target_change is not None:
    #     add_favorability(target_id, character_id, old_add_favorability, None, None, now_time)

    # 记录好感度增加
    if character_id == 0 or character_data.target_character_id == 0:
        cache.rhodes_island.total_favorability_increased += now_add_favorability


def handle_character_setting():
    """
    处理角色的初始世界设置
    """
    # 遍历所有角色
    for character_id in cache.character_data:
        if character_id == 0:
            continue
        character_data = cache.character_data[character_id]
        # 萝莉化
        if cache.world_setting[1]:
            for talent_id in {104,105,106,107}:
                if character_data.talent[talent_id]:
                    character_data.talent[talent_id] = 0
                    character_data.talent[103] = 1
        # 淫乱化
        if cache.world_setting[2]:
            character_data.talent[40] = 1
        # 泌乳化
        if cache.world_setting[3]:
            character_data.talent[27] = 1
