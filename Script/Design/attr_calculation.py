import random
import datetime
from Script.Core import (
    cache_control,
    value_handle,
    game_type,
)
from Script.Design import game_time
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏内缓存数据 """


def get_ability_zero(ability_dict) -> dict:
    """
    检查初始能力，将为空的项补为0
    """
    ability_list = ability_dict
    for ability in game_config.config_ability:
        if ability not in ability_dict:
            ability_list[ability] = 0
    return ability_list

def get_event_zero() -> dict:
    """
    初始化事件结构体
    """
    event_data = game_type.Chara_Event()
    return event_data

def get_work_zero() -> dict:
    """
    初始化工作结构体
    """
    work_data = game_type.CHARA_WORK()
    return work_data

def get_entertainment_zero() -> dict:
    """
    初始化娱乐结构体
    """
    entertainment_data = game_type.CHARA_ENTERTAINMENT()

    return entertainment_data

def get_pregnancy_zero() -> dict:
    """
    初始化受精怀孕情况数据结构体
    """
    pregnancy_data = game_type.PREGNANCY()
    pregnancy_data.reproduction_period = random.randint(0,6)

    return pregnancy_data

def get_relationship_zero(relationship_dict) -> dict:
    """
    检查初始关系，将为空的项补为0
    """
    relationship_data = relationship_dict
    # for status in game_config.tio:
    #     if status not in status_dict:
    #         status_list[status] = 0
    return relationship_data


def get_status_zero(status_dict) -> dict:
    """
    检查初始状态，将为空的项补为0
    """
    status_list = status_dict
    for status in game_config.config_character_state:
        if status not in status_dict:
            status_list[status] = 0
    return status_list


def get_talent_zero(talent_dict) -> dict:
    """
    检查初始素质，将为空的项补为0
    """
    talent_list = talent_dict
    for talent in game_config.config_talent:
        if talent not in talent_dict:
            talent_list[talent] = 0
    return talent_list

def get_experience_zero(experience_dict) -> dict:
    """
    检查初始经验，将为空的项补为0
    """
    experience_list = experience_dict
    for experience in game_config.config_experience:
        if experience not in experience_dict:
            experience_list[experience] = 0
    return experience_list

def get_juel_zero(juel_dict) -> dict:
    """
    检查初始宝珠，将为空的项补为0
    """
    juel_list = juel_dict
    for juel in game_config.config_juel:
        if juel not in juel_dict:
            juel_list[juel] = 0
    return juel_list


def get_chara_setting_zero() -> dict:
    """
    重置角色初始设置
    """
    chara_setting_list = {}
    for chara_setting in game_config.config_chara_setting:
        chara_setting_list[chara_setting] = 0
    return chara_setting_list


def get_assistant_services_zero() -> dict:
    """
    重置角色助理服务
    """
    assistant_services = {}
    for cid in game_config.config_assistant_services:
        assistant_services[cid] = 0
    return assistant_services


def get_second_behavior_zero(second_behavior_dict) -> dict:
    """
    将二段行为全项归零，暂时为前200项
    """
    second_behavior_list = second_behavior_dict
    for second_behavior in range(1000,1200):
        second_behavior_list[second_behavior] = 0
    return second_behavior_list


def get_time_zero() -> dict:
    """
    时间归为游戏初始时间
    """
    return cache.game_time

def get_token_zero(token_dict) -> dict:
    """
    直接将初始信物归为全员0
    """
    token_list = token_dict
    for i in range(len(cache.npc_tem_data) + 1):
        token_list[i] = 0
    return token_list


def get_dirty_zero() -> dict:
    """
    直接将初始污浊情况归0
    """
    dirty_data = game_type.DIRTY()

    for body_part in game_config.config_body_part:
        body_text = game_config.config_body_part[body_part].name
        now_list = [body_text,0,0,0]
        dirty_data.body_semen.append(now_list)

    for clothing_type in game_config.config_clothing_type:
        cloth_text = game_config.config_clothing_type[clothing_type].name
        now_list = [cloth_text,0,0,0]
        dirty_data.cloth_semen.append(now_list)

    dirty_data.a_clean = 0

    return dirty_data

def get_h_state_zero(old_h_state_data: game_type.BODY_H_STATE) -> dict:
    """
    直接将H状态结构体归0
    """
    h_state_data = old_h_state_data
    body_item_list = ["乳头夹","阴蒂夹","V震动棒","A震动棒","搾乳机","采尿器","眼罩","肛门拉珠","持续性利尿剂","安眠药","排卵促进药","事前避孕药","事后避孕药"]
    # bondage_list = ["未捆绑","后高手缚","直立缚","驷马捆绑","直臂缚","双手缚","菱绳缚","龟甲缚","团缚","逆团缚","吊缚","后手吊缚","单足吊缚","后手观音","苏秦背剑","五花大绑"]

    if len(h_state_data.body_item) == 0:
        for body_item in body_item_list:
            now_list = [body_item,False,None]
            h_state_data.body_item.append(now_list)
    else:
        for i in range(len(h_state_data.body_item)):
            if i not in {8,9,10,11,12}:
                h_state_data.body_item[i] = [body_item_list[i],False,None]

    for body_part in game_config.config_body_part:
        h_state_data.orgasm_level[body_part] = 0
        h_state_data.orgasm_count[body_part] = [0,0]

    return h_state_data


def get_first_record_zero() -> dict:
    """
    直接将初次状态记录结构体归0
    """
    first_record_data = game_type.FIRST_RECORD()

    return first_record_data


def get_pl_ability_zero() -> dict:
    """
    直接将玩家能力结构体归0
    """
    pl_ability_data = game_type.PLAYER_ABILITY()

    return pl_ability_data


def get_action_info_state_zero() -> dict:
    """
    直接将行动信息结构体归0
    """
    action_info_data = game_type.ACTION_INFO()
    action_info_data.talk_time = cache.game_time
    action_info_data.last_move_time = cache.game_time
    action_info_data.last_training_time = game_time.get_sub_date(day=-1)
    action_info_data.last_shower_time = game_time.get_sub_date(day=-1)
    action_info_data.wake_time = cache.game_time
    action_info_data.sleep_time = cache.game_time

    return action_info_data


def get_cloth_zero() -> dict:
    """
    遍历服装类型，将每个都设为空
    """
    coloth_data = game_type.CLOTH()

    for clothing_type in game_config.config_clothing_type:
        coloth_data.cloth_wear[clothing_type] = []
        coloth_data.cloth_off[clothing_type] = []
        coloth_data.cloth_locker[clothing_type] = []

    coloth_data.cloth_see= {6:False,9:False}

    return coloth_data


def get_cloth_wear_zero() -> dict:
    """
    遍历当前穿着服装类型，将每个都设为空
    """
    coloth_wear_data = game_type.CLOTH().cloth_wear

    for clothing_type in game_config.config_clothing_type:
        coloth_wear_data[clothing_type] = []

    return coloth_wear_data


def get_cloth_locker_zero() -> dict:
    """
    将衣柜里的每个衣服类型都设为空
    """
    cloth_locker_data = game_type.CLOTH().cloth_locker

    for clothing_type in game_config.config_clothing_type:
        cloth_locker_data[clothing_type] = []

    return cloth_locker_data


def get_collection_zero() -> dict:
    """
    遍历玩家的收藏品结构体，设为空
    """

    collection_data = game_type.PLAYER_COLLECTION()
    for cid in game_config.config_collection_bonus_data:
        collection_data.collection_bonus[cid] = False

    for i in range(len(cache.npc_tem_data)):
        npc_id = i + 1
        collection_data.token_list[npc_id] = False
        collection_data.first_panties[npc_id] = ""
        collection_data.npc_panties[npc_id] = []
        collection_data.npc_socks[npc_id] = []

    return collection_data


def get_item_zero(item_dict) -> dict:
    """
    检查初始道具，将为空的项补为0
    """
    item_list = item_dict
    for item in game_config.config_item:
        if item not in item_dict:
            item_list[item] = 0
    return item_list


def get_Dr_talent_zero(juel_dict) -> dict:
    """
    检查是否是0号角色，将特定项补为0
    """
    juel_list = juel_dict
    juel_list[4] = 1
    juel_list[5] = 1
    return juel_list


def get_rand_npc_birthday(age: int):
    """
    随机生成npc生日
    Keyword arguments:
    age -- 年龄
    """
    now_year = cache.game_time.year
    now_month = cache.game_time.month
    now_day = cache.game_time.day
    birthday = game_time.get_rand_day_for_year(now_year)
    if now_month < birthday.month or (now_month == birthday.month and now_day < birthday.day):
        birthday = game_time.get_sub_date(year=-1, old_date=birthday)
    return birthday


def get_experience_level_weight(experience: int) -> int:
    """
    按经验计算技能等级权重
    Keyword arguments:
    experience -- 经验数值
    Return arguments:
    int -- 权重
    """
    grade = 0
    if experience < 100:
        grade = 0
    elif experience < 500:
        grade = 1
    elif experience < 1000:
        grade = 2
    elif experience < 2000:
        grade = 3
    elif experience < 3000:
        grade = 4
    elif experience < 5000:
        grade = 5
    elif experience < 10000:
        grade = 6
    elif experience < 20000:
        grade = 7
    elif experience >= 20000:
        grade = 8
    return grade


def judge_grade(experience: int) -> str:
    """
    按能力数值评定等级
    Keyword arguments:
    experience -- 能力数值
    Return arguments:
    str -- 评级
    """
    grade = ""
    if experience <= 0:
        grade = "G"
    elif experience == 1:
        grade = "F"
    elif experience == 2:
        grade = "E"
    elif experience == 3:
        grade = "D"
    elif experience == 4:
        grade = "C"
    elif experience == 5:
        grade = "B"
    elif experience == 6:
        grade = "A"
    elif experience == 7:
        grade = "S"
    elif experience >= 8:
        grade = "EX"
    return grade

def get_status_level(value: int) -> int:
    """
    按状态数值评定数字等级
    Keyword arguments:
    value -- 属性数值
    Return arguments:
    level -- 数字评级
    """
    if value < 100:
        level = 0
    elif value < 500:
        level = 1
    elif value < 3000:
        level = 2
    elif value < 10000:
        level = 3
    elif value < 30000:
        level = 4
    elif value < 60000:
        level = 5
    elif value < 100000:
        level = 6
    elif value < 150000:
        level = 7
    elif value < 500000:
        level = 8
    elif value < 999999:
        level = 9
    elif value >= 999999:
        level = 10
    return level


def get_ability_level(value: int) -> int:
    """
    按能力数值评定数字等级
    Keyword arguments:
    value -- 能力数值
    Return arguments:
    level -- 数字评级
    """
    if value < 100:
        level = 0
    elif value < 500:
        level = 1
    elif value < 3000:
        level = 2
    elif value < 10000:
        level = 3
    elif value < 30000:
        level = 4
    elif value < 60000:
        level = 5
    elif value < 100000:
        level = 6
    elif value < 150000:
        level = 7
    elif value < 250000:
        level = 8
    elif value < 400000:
        level = 9
    elif value >= 400000:
        level = 10
    return level

def get_ability_adjust(value: int) -> int:
    """
    按能力数值评定修正比例
    Keyword arguments:
    value -- 能力数值
    Return arguments:
    just -- 调整比例
    """
    level = get_ability_level(value)
    if level == 0:
        just = 0.2
    elif level == 1:
        just = 0.4
    elif level == 2:
        just = 0.7
    elif level == 3:
        just = 1.0
    elif level == 4:
        just = 1.4
    elif level == 5:
        just = 1.8
    elif level == 6:
        just = 2.3
    elif level == 7:
        just = 2.8
    elif level == 8:
        just = 3.4
    elif level == 9:
        just = 4.0
    elif level == 10:
        just = 5.0
    return just


def get_mark_debuff_adjust(value: int) -> int:
    """
    按刻印等级负面修正比例参数
    Keyword arguments:
    value -- 能力数值
    Return arguments:
    just -- 调整比例
    """
    level = get_ability_level(value)
    if level == 0:
        just = 1
    elif level == 1:
        just = 2
    elif level == 2:
        just = 5
    elif level == 3:
        just = 10
    return just


def get_juel(value: int) -> int:
    """
    按状态等级计算宝珠的最后值
    Keyword arguments:
    value -- 能力数值
    Return arguments:
    juel -- 最终珠值
    """
    level = get_ability_level(value)
    if level == 0:
        juel = round(0.2*value)
    elif level == 1:
        juel = round(0.4*value)
    elif level == 2:
        juel = round(0.7*value)
    elif level == 3:
        juel = round(1.0*value)
    elif level == 4:
        juel = round(1.4*value)
    elif level == 5:
        juel = round(1.8*value)
    elif level == 6:
        juel = round(2.3*value)
    elif level == 7:
        juel = round(2.8*value)
    elif level == 8:
        juel = round(3.4*value)
    elif level == 9:
        juel = round(4.0*value)
    elif level == 10:
        juel = round(5.0*value)
    return juel


def get_pain_adjust(value: int) -> int:
    """
    按润滑程度修正苦痛值比例
    Keyword arguments:
    value -- 能力数值
    Return arguments:
    just -- 调整比例
    """
    level = get_ability_level(value)
    if level == 0:
        just = 10.0
    elif level == 1:
        just = 6.0
    elif level == 2:
        just = 3.4
    elif level == 3:
        just = 2.8
    elif level == 4:
        just = 2.3
    elif level == 5:
        just = 1.8
    elif level == 6:
        just = 1.4
    elif level == 7:
        just = 1.0
    elif level == 8:
        just = 0.7
    elif level == 9:
        just = 0.4
    elif level == 10:
        just = 0.2
    return just


def get_angry_level(value: int) -> int:
    """
    按怒气值返回生气程度
    Keyword arguments:
    value -- 怒气值
    Return arguments:
    level -- 生气程度
    """
    if value <= 5:
        return 1
    elif 5 < value and value <= 30:
        return 0
    elif 30 < value and value <=50:
        return -1
    elif value > 50:
        return -3

def get_angry_text(value: int) -> str:
    """
    按怒气值返回生气程度的文本
    Keyword arguments:
    value -- 怒气值
    Return arguments:
    level -- 生气程度的文本
    """
    if value <= 5:
        return "愉快"
    elif 5 < value and value <= 30:
        return "普通"
    elif 30 < value and value <=50:
        return "不爽"
    elif value > 50:
        return "愤怒"


def get_semen_now_level(value: int, part_cid: int, part_type: int) -> int:
    """
    按当前部位精液量返回精液覆盖等级\n
    Keyword arguments:\n
    value -- 精液量\n
    part_cid -- 部位编号\n
    part_type -- 部位类型，0:身体,1:衣物\n
    Return arguments:\n
    level -- 精液覆盖等级\n
    """
    # 如果没有精液，则返回0
    if value <= 0:
        return 0
    # 如果是身体部位
    if part_type == 0:
        if part_cid == 20:
            voluem_data_list = [300, 1000, 3000, 6000, 9000, 12000]
        else:
            voluem_data_list = game_config.config_body_part_volume[part_cid]
        for i in range(len(voluem_data_list)):
            if value <= voluem_data_list[i]:
                now_level = i + 1
                break
            # 如果超过最大值，则返回最大值
            if i == len(voluem_data_list) - 1:
                now_level = i + 1
    else:
        if value <= 0:
            return 0
        elif 0 < value and value <= 10:
            return 1
        elif 10 < value and value <= 50:
            return 2
        elif 50 < value and value <=200:
            return 3
        elif 200 < value and value <=1000:
            return 4
        elif value > 1000:
            return 5
    # print(f"debug value = {value},now_level = {now_level}")
    return now_level


def get_tired_level(value: int) -> int:
    """
    按当前困倦程度返回困倦等级[0:0~74,1:75~84,2:85~99,3:100以上]
    Keyword arguments:
    value -- 困倦程度
    Return arguments:
    level -- 困倦等级
    """
    if value / 160 <= 0.74:
        return 0
    elif 0.74 < value / 160 <= 0.84:
        return 1
    elif 0.84 < value / 160 < 1:
        return 2
    elif value / 160 >= 1:
        return 3


def get_sleep_level(value: int):
    """
    按当前熟睡值返回当前睡眠等级的str
    Keyword arguments:
    value -- 熟睡值
    Return arguments:
    int -- 睡眠等级,0~3
    str -- 睡眠等级名,随时醒来~完全深眠
    """
    for now_cid in game_config.config_sleep_level:
        now_data = game_config.config_sleep_level[now_cid]
        if value > now_data.sleep_point:
            continue
        else:
            return now_cid,now_data.name


def get_food_quality(value: int):
    """
    按当前食物质量返回当前质量等级的str
    Keyword arguments:
    value -- 食物质量值
    Return arguments:
    int -- 食物质量等级,0~4
    str -- 食物质量名,粗劣~绝珍
    """
    for now_cid in game_config.config_food_quality:
        now_data = game_config.config_food_quality[now_cid]
        if value <= now_data.ability_level:
            return now_cid,now_data.name
        else:
            continue


def get_favorability_level(value: int):
    """
    按当前好感度返回当前好感等级的str
    Keyword arguments:
    value -- 好感度
    Return arguments:
    int -- 好感度等级
    int -- 实行值加成
    """
    for now_cid in game_config.config_favorability_level:
        now_data = game_config.config_favorability_level[now_cid]
        if value > now_data.Favorability_point:
            continue
        return now_cid,now_data.judge_add
    # 到达极限值时输出config_favorability_level的最后一个作为返回值
    max_cid = list(game_config.config_favorability_level.keys())[-1]
    max_data = game_config.config_favorability_level[max_cid]
    return max_cid,max_data.judge_add


def get_trust_level(value: int):
    """
    按当前信赖度返回当前信赖等级的str
    Keyword arguments:
    value -- 信赖度
    Return arguments:
    int -- 信赖度等级
    int -- 实行值加成
    """
    for now_cid in game_config.config_trust_level:
        now_data = game_config.config_trust_level[now_cid]
        if value > now_data.Trust_point:
            continue
        return now_cid,now_data.judge_add
    # 到达极限值时输出config_trust_level的最后一个作为返回值
    max_cid = list(game_config.config_trust_level.keys())[-1]
    max_data = game_config.config_trust_level[max_cid]
    return max_cid,max_data.judge_add


def hypnosis_degree_calculation(target_character_id: int) -> int:
    """
    计算催眠的增长程度
    Keyword arguments:
    target_character_id -- 角色id
    Return arguments:
    int -- 催眠增长系数
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    target_character_data: game_type.Character = cache.character_data[target_character_id]

    if target_character_id == 0:
        return 0

    # 如果已经达到当前玩家的能力上限，则不再增加
    hypnosis_degree_limit = hypnosis_degree_limit_calculation()
    if target_character_data.hypnosis.hypnosis_degree >= hypnosis_degree_limit:
        return 0

    # 根据玩家的催眠能力，计算催眠增长系数
    hypnosis_degree_addition = 1
    if pl_character_data.talent[334]:
        hypnosis_degree_addition = 4
    elif pl_character_data.talent[333]:
        hypnosis_degree_addition = 2

    # 根据无觉刻印的等级，计算催眠增长系数
    hypnosis_degree_addition += get_ability_adjust(target_character_data.ability[19])

    return hypnosis_degree_addition


def hypnosis_degree_limit_calculation() -> int:
    """
    计算催眠的上限
    Keyword arguments:
    target_character_id -- 角色id
    Return arguments:
    int -- 催眠上限
    """
    pl_character_data: game_type.Character = cache.character_data[0]

    # 如果已经达到当前玩家的能力上限，则不再增加
    hypnosis_degree_limit = 0
    for cid in game_config.config_hypnosis_talent_of_pl:
        hypnosis_data = game_config.config_hypnosis_talent_of_pl[cid]
        if pl_character_data.talent[hypnosis_data.hypnosis_talent_id]:
            hypnosis_degree_limit = max(hypnosis_degree_limit, hypnosis_data.max_hypnosis_degree)

    return hypnosis_degree_limit


def judge_require(judge_text_list, character_id):
    """
    判断角色是否满足文本列表里的全部需求\n
    Keyword arguments:\n
    judge_text_list -- 需要判断的文本列表(A能力,T素质,J宝珠,E经验,F好感度,X信赖,O设施解锁)\n
    character_id -- 角色id\n
    Return arguments:\n
    judge -- 是否满足需求\n
    reason -- 不满足需求的原因\n
    """

    character_data: game_type.Character = cache.character_data[character_id]
    judge = 1
    reason = "需要:"

    for judge_text in judge_text_list:
        judge_type = judge_text.split('|')[0][0]
        if len(judge_text.split('|')[0]) >= 2:
            judge_type_id = int(judge_text.split('|')[0][1:])
        judge_value = int(judge_text.split('|')[1])
        if judge_type == "A":
            if character_data.ability[judge_type_id] < judge_value:
                judge = 0
                reason += f"{game_config.config_ability[judge_type_id].name}>={judge_value}  "
                break
        elif judge_type == "T":
            if not character_data.talent[judge_value]:
                judge = 0
                reason += f"{game_config.config_talent[judge_value].name}  "
                break
        elif judge_type == "J":
            if character_data.juel[judge_type_id] < judge_value:
                judge = 0
                reason += f"{game_config.config_juel[judge_type_id].name}>={judge_value}  "
                break
        elif judge_type == "E":
            if character_data.experience[judge_type_id] < judge_value:
                judge = 0
                reason += f"{game_config.config_experience[judge_type_id].name}>={judge_value}  "
                break
        elif judge_type == "F":
            if character_data.favorability[0] < judge_value:
                judge = 0
                reason += f"好感度>={judge_value}  "
                break
        elif judge_type == "X":
            if character_data.trust < judge_value:
                judge = 0
                reason += f"信赖度>={judge_value}  "
                break
        elif judge_type == "O":
            if not cache.rhodes_island.facility_open[judge_type_id]:
                judge = 0
                reason += f"解锁{game_config.config_facility_open[judge_type_id].name}  "
                break

    return judge, reason
