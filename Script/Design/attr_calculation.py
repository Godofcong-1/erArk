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


def get_Favorability_zero() -> dict:
    """
    直接将初始好感归为{0:0}
    """
    return {0:0}

def get_Trust_zero() -> dict:
    """
    直接将初始信赖归为0
    """
    return 0

def get_ability_zero(ability_dict) -> dict:
    """
    检查初始能力，将为空的项补为0
    """
    ability_list = ability_dict
    for ability in game_config.config_ability:
        if ability not in ability_dict:
            ability_list[ability] = 0
    return ability_list

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

def get_orgasm_level_zero(orgasm_level_dict) -> dict:
    """
    将绝顶水平全项归零
    """
    orgasm_level_list = orgasm_level_dict
    for orgasm in range(8):
        orgasm_level_list[orgasm] = 0
    return orgasm_level_list

def get_orgasm_count_zero(orgasm_count_dict) -> dict:
    """
    将绝顶次数全项归零
    """
    orgasm_count_list = orgasm_count_dict
    for orgasm in range(8):
        orgasm_count_list[orgasm] = 0
    return orgasm_count_list

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
    position_text_list = ["头发","脸部","口腔","胸部","腋部","手部","小穴","后穴","尿道","腿部","脚部","尾巴","兽角","兽耳"]

    for position_text in position_text_list:
        now_list = [position_text,0,0,0]
        dirty_data.body_semen.append(now_list)

    for clothing_type in game_config.config_clothing_type:
        cloth_text = game_config.config_clothing_type[clothing_type].name
        now_list = [cloth_text,0,0,0]
        dirty_data.cloth_semen.append(now_list)

    dirty_data.a_clean = 0

    return dirty_data

def get_h_state_zero() -> dict:
    """
    直接将H状态结构体归0
    """
    h_state_data = game_type.BODY_H_STATE()
    body_item_list = ["乳头夹","阴蒂夹","V震动棒","A震动棒","搾乳机","采尿器","眼罩","肛门拉珠","持续性利尿剂","睡眠药"]
    # bondage_list = ["未捆绑","后高手缚","直立缚","驷马捆绑","直臂缚","双手缚","菱绳缚","龟甲缚","团缚","逆团缚","吊缚","后手吊缚","单足吊缚","后手观音","苏秦背剑","五花大绑"]

    for body_item in body_item_list:
        now_list = [body_item,False,None]
        h_state_data.body_item.append(now_list)

    return h_state_data

def get_assistant_state_zero() -> dict:
    """
    直接将助理状态结构体归0
    """
    assistant_state_data = game_type.ASSISTANT_STATE()

    return assistant_state_data


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
    action_info_data.last_training_time = cache.game_time

    return action_info_data


def get_cloth_zero() -> dict:
    """
    遍历服装类型，将每个都设为空
    """

    cloth_dict = {}

    for clothing_type in game_config.config_clothing_type:
        cloth_dict[clothing_type] = []

    return cloth_dict


def get_collection_zero() -> dict:
    """
    遍历玩家的收藏品结构体，设为空
    """

    collection_data = game_type.PLAYER_COLLECTION()
    for cid in game_config.config_collection_bonus_data:
        collection_data.collection_bonus[cid] = False

    for npc_id in cache.character_data:
        collection_data.token_list[npc_id] = False
        collection_data.first_panties[npc_id] = ""
        collection_data.npc_panties[npc_id] = []
        collection_data.npc_socks[npc_id] = []

    return collection_data


def get_base_zero() -> dict:
    """
    基地情况结构体，设为空
    """

    base_data = game_type.Base_resouce()

    # 遍历全设施清单
    for all_cid in game_config.config_facility:
        # 全设施等级设为1
        base_data.facility_level[all_cid] = 1

    # 遍历全设施开放
    for all_cid in game_config.config_facility_open:
        # 全设施等级设为1
        base_data.facility_open[all_cid] = False

    # 遍历全资源清单
    for all_cid in game_config.config_resouce:
        # 全资源数量设为0
        base_data.materials_resouce[all_cid] = 0

    return base_data

def get_base_updata() -> dict:
    """
    遍历基地情况结构体，根据设施等级更新全部数值
    """


    cache.base_resouce.power_use = 0

    # 遍历全设施清单
    for all_cid in game_config.config_facility:
        # 全设施等级设为1
        level = cache.base_resouce.facility_level[all_cid]

        # 累加全设施的用电量
        facility_name = game_config.config_facility[all_cid].name
        facility_cid = game_config.config_facility_effect_data[facility_name][level]
        cache.base_resouce.power_use += game_config.config_facility_effect[facility_cid].power_use

        # 如果满足设施开放的前提条件，则开放该设施
        for open_cid in game_config.config_facility_open:
            if game_config.config_facility_open[open_cid].zone_cid == facility_cid:
                cache.base_resouce.facility_open[open_cid] = True

    # print(f"debug power_use = {base_data.power_use}")

        # 初始化供电量
        if facility_name == "动力区":
            cache.base_resouce.power_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化仓库容量
        elif facility_name == "仓储区":
            cache.base_resouce.warehouse_capacity = game_config.config_facility_effect[facility_cid].effect
        # 初始化干员人数上限
        elif facility_name == "宿舍区":
            cache.base_resouce.people_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化生活娱乐区设施数量上限
        elif facility_name == "生活娱乐区":
            cache.base_resouce.life_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化患者人数上限，并刷新当天患者人数
        elif facility_name == "医疗部":
            cache.base_resouce.patient_max = game_config.config_facility_effect[facility_cid].effect
            cache.base_resouce.patient_now = random.randint(1,cache.base_resouce.patient_max)
        # 初始化科研区设施数量上限
        elif facility_name == "科研部":
            cache.base_resouce.research_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化商店数量上限
        elif facility_name == "贸易区":
            cache.base_resouce.shop_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化战斗时干员数量上限
        elif facility_name == "指挥室":
            cache.base_resouce.soldier_max = game_config.config_facility_effect[facility_cid].effect


def get_work_people() -> dict:
    """
    遍历基地情况结构体，根据设施等级更新全部数值
    """
    from Script.Core import constant

    for Clinic_place in constant.place_data["Clinic"]:
        if len(cache.scene_data[Clinic_place].character_list):
            for npc_id in cache.scene_data[Clinic_place].character_list:
                if npc_id:
                    cache.base_resouce.work_people_now += 1


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
    birth_year = now_year - int(age)
    birthday = game_time.get_rand_day_for_year(birth_year)
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
    elif value < 250000:
        level = 8
    elif value < 400000:
        level = 9
    elif value >= 400000:
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


def get_semen_now_level(value: int) -> int:
    """
    按当前部位精液量返回精液覆盖等级
    Keyword arguments:
    value -- 精液量
    Return arguments:
    level -- 精液覆盖等级
    """
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


def get_sleep_level(value: int) -> int:
    """
    按当前困倦程度返回困倦等级[0:0~74,1:75~89,2:89~99,3:100以上]
    Keyword arguments:
    value -- 困倦程度
    Return arguments:
    level -- 困倦等级
    """
    if value / 160 <= 0.74:
        return 0
    elif 0.74 < value / 160 and value / 160 <= 0.89:
        return 1
    elif 0.89 < value / 160 and value / 160 <= 0.99:
        return 2
    elif value / 160 >= 1:
        return 3

