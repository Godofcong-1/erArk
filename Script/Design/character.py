import random
import datetime
from typing import List
from Script.Core import (
    cache_control,
    value_handle,
    constant,
    game_type,
)
from Script.Design import (
    attr_calculation,
    clothing,
    game_time,

)
from Script.Config import game_config
from Script.UI.Moudle import draw


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def init_attr(character_id: int):
    """
    初始化角色属性
    Keyword arguments:
    character_id -- 角色id
    """
    # print("进入第二步的init_attr")
    # print("进入第二步的character_id :",character_id)
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.birthday = attr_calculation.get_rand_npc_birthday(character_data.age)
    # character_data.height = attr_calculation.get_height(character_data.sex, character_data.age)
    # character_data.weight = attr_calculation.get_weight(bmi, character_data.height.now_height)

    #一系列归零函数
    character_data.ability = attr_calculation.get_ability_zero(character_data.ability)
    character_data.status_data = attr_calculation.get_status_zero(character_data.status_data)
    character_data.talent = attr_calculation.get_talent_zero(character_data.talent)
    character_data.experience = attr_calculation.get_experience_zero(character_data.experience)
    character_data.juel = attr_calculation.get_juel_zero(character_data.juel)
    character_data.orgasm_level = attr_calculation.get_orgasm_level_zero(character_data.orgasm_level)
    character_data.orgasm_count = attr_calculation.get_orgasm_count_zero(character_data.orgasm_count)
    character_data.second_behavior = attr_calculation.get_second_behavior_zero(character_data.second_behavior)
    character_data.last_move_time = attr_calculation.get_time_zero()
    character_data.dirty = attr_calculation.get_dirty_zero()
    character_data.item = attr_calculation.get_item_zero(character_data.item)
    character_data.h_state = attr_calculation.get_h_state_zero()
    character_data.assistant_state = attr_calculation.get_assistant_state_zero()
    character_data.first_record = attr_calculation.get_first_record_zero()
    character_data.pl_ability = attr_calculation.get_pl_ability_zero()
    character_data.cloth_see = {6:False,9:False}


    #主角的初始处理，HP和MP的最大值默认为2000，EP最大值默认为1000，初始化信物，困倦程度归零
    if character_id == 0 :
        character_data.talent = attr_calculation.get_Dr_talent_zero(character_data.talent)
        character_data.hit_point_max = 2000
        character_data.mana_point_max = 2000
        character_data.eja_point = 0
        character_data.eja_point_max = 1000
        character_data.token_list = attr_calculation.get_token_zero(character_data.token_list)
        character_data.sleep_point = 0

    #一系列初始化函数
    character_data.hit_point = character_data.hit_point_max
    character_data.mana_point = character_data.mana_point_max
    character_data.angry_point = random.randrange(1,35)
    character_data.hunger_point = 240
    if character_id:
        clothing.get_underwear(character_id)
    # default_clothing_data = clothing.creator_suit(character_data.clothing_tem, character_data.sex)
    # for clothing_id in default_clothing_data:
    #     clothing_data = default_clothing_data[clothing_id]
    #     character_data.clothing.setdefault(clothing_id, {})
    #     character_data.clothing[clothing_id][clothing_data.uid] = clothing_data
    #     character_data.clothing_data.setdefault(clothing_data.tem_id, set())
    #     character_data.clothing_data[clothing_data.tem_id].add(clothing_data.uid)
    # init_class(character_data)


def init_character_behavior_start_time(character_id: int, now_time: datetime.datetime):
    """
    将角色的行动开始时间同步为指定时间
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    character_data = cache.character_data[character_id]
    start_time = datetime.datetime(
        now_time.year,
        now_time.month,
        now_time.day,
        now_time.hour,
        now_time.minute,
    )
    character_data.behavior.start_time = start_time


def character_rest_to_time(character_id: int, need_time: int):
    """
    设置角色状态为休息指定时间
    Keyword arguments:
    character_id -- 角色id
    need_time -- 休息时长(分钟)
    """
    character_data = cache.character_data[character_id]
    character_data.behavior["Duration"] = need_time
    character_data.behavior["BehaviorId"] = constant.Behavior.REST
    character_data.state = constant.CharacterStatus.STATUS_REST


def calculation_favorability(character_id: int, target_character_id: int, favorability: int) -> int:
    """
    按角色当前状态、素质和能力计算最终增加的好感值
    Keyword arguments:
    character_id -- 角色id
    target_character_id -- 目标角色id
    favorability -- 基础好感值
    Return arguments:
    int -- 最终的好感值
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[target_character_id]
    fix = 1.0
    #状态相关计算#

    #恭顺、好意、欲情、快乐每级+0.1倍#
    for i in {10, 11, 12, 13}:
        status_level = attr_calculation.get_status_level(target_data.status_data[i])
        fix += status_level*0.1
    #羞耻、苦痛每级-0.1倍#
    for i in {16, 17}:
        status_level = attr_calculation.get_status_level(target_data.status_data[i])
        fix -= status_level*0.2
    #恐怖、抑郁、反感每级-0.4倍#
    for i in {18, 19, 20}:
        status_level = attr_calculation.get_status_level(target_data.status_data[i])
        fix -= status_level*0.4

    #能力相关计算#
    #亲密、快乐刻印、屈服刻印每级+0.2倍#
    for i in {13, 14, 21}:
        status_level = attr_calculation.get_status_level(target_data.ability[i])
        fix += status_level*0.2
    #苦痛刻印、恐怖刻印每级-0.3倍#
    for i in {15, 17}:
        status_level = attr_calculation.get_status_level(target_data.ability[i])
        fix -= status_level*0.3
    #反发刻印每级-1.0倍#
    for i in {18}:
        status_level = attr_calculation.get_status_level(target_data.ability[i])
        fix -= status_level*1.0
    
    #素质相关计算#
    #爱情与隶属系加成0.5~2.0#
    if target_data.talent[10] or target_data.talent[15]:
        fix += 0.5
    if target_data.talent[11] or target_data.talent[16]:
        fix += 1.0
    if target_data.talent[12] or target_data.talent[17]:
        fix += 1.5
    if target_data.talent[13] or target_data.talent[18]:
        fix += 2.0
    #受精、妊娠、育儿均+0.5#
    if target_data.talent[20] or target_data.talent[21] or target_data.talent[22]:
        fix += 0.5
    #感情缺乏-0.2#
    if target_data.talent[223]:
        fix -= 0.2
    #讨厌男性-0.2#
    if target_data.talent[227]:
        fix -= 0.2
    #博士信息素每级+0.5#
    if character_data.talent[304]:
        fix += 0.5
    if character_data.talent[305]:
        fix += 1.0
    if character_data.talent[306]:
        fix += 1.5
    favorability *= fix
    return favorability


def calculation_instuct_judege(character_id: int, target_character_id: int, instruct_name: str) -> int:
    """
    按角色当前状态、素质和能力计算最终该指令是否成功
    Keyword arguments:
    character_id -- 角色id
    target_character_id -- 目标角色id
    instruct_name -- 指令名字
    Return arguments:
    int -- 最终的好感值
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[target_character_id]
    for judge_id in game_config.config_instruct_judge_data:
        #匹配到能力的id与能力等级对应的前提#
        if game_config.config_instruct_judge_data[judge_id].instruct_name == instruct_name:
            judge_data = game_config.config_instruct_judge_data[judge_id]
            judge_data_type = judge_data.need_type
            judge_data_value = judge_data.value

    if judge_data_type == "D":
        calculation_text = "需要基础实行值至少为" + str(judge_data_value) + "\n"
    elif judge_data_type == "S":
        calculation_text = "需要性爱实行值至少为" + str(judge_data_value) + "\n"
    calculation_text += "当前值为："

    judge = 0

    #好感判定#
    favorability = target_data.favorability[0]
    judge_favorability = 0
    if favorability < 100:
        judge_favorability -= 20
    if favorability < 1000:
        judge_favorability += 0
    elif favorability <3000:
        judge_favorability += 50
    elif favorability <5000:
        judge_favorability += 75
    elif favorability <10000:
        judge_favorability += 100
    elif favorability <30000:
        judge_favorability += 150
    else:
        judge_favorability += 200
    calculation_text += "好感修正("+ str(judge_favorability) +")"
    judge += judge_favorability
    
    #信赖判定#
    trust = target_data.trust
    judge_trust = 0
    if trust < 50:
        judge_trust -= 50
    elif trust <100:
        judge_trust -= 20
    elif trust <150:
        judge_trust += 0
    elif trust <200:
        judge_trust += 30
    elif trust <250:
        judge_trust += 50
    else:
        judge_trust += 100
    judge += judge_trust
    calculation_text += "+信赖修正("+ str(judge_trust) +")"

    #状态修正，好意(11)和欲情(12)修正#
    judge_status = int( (target_data.status_data[11] + target_data.status_data[12]) / 10 )
    judge += judge_status
    if judge_status:
        calculation_text += "+状态修正("+ str(judge_status) +")"

    #能力修正，亲密(21)和欲望(22)修正#
    judge_ability = target_data.ability[21]*10 + target_data.ability[22]*5
    judge += judge_ability
    if judge_ability:
        calculation_text += "+能力修正("+ str(judge_ability) +")"

    #刻印修正，快乐(13)、屈服(14)、时停(16)、恐怖(17)、反发(18)修正#
    judge_mark = target_data.ability[13]*20 + target_data.ability[14]*20
    judge_mark -= min(target_data.ability[17] - target_data.ability[16], 0) * 20 + target_data.ability[18]*30
    judge += judge_mark
    if judge_mark:
        calculation_text += "+刻印修正("+ str(judge_mark) +")"

    #心情修正，好心情+10，坏心情-10，愤怒-30
    judge_angry = attr_calculation.get_angry_level(target_data.angry_point) * 10
    judge += judge_angry
    if judge_angry:
        calculation_text += "+心情修正("+ str(judge_angry) +")"

    #陷落素质判定，第一阶段~第四阶段分别为30,50,80,100#
    judge_fall = target_data.talent[10]*30 + target_data.talent[11]*50 + target_data.talent[12]*80 + target_data.talent[13]*100 + target_data.talent[15]*30 + target_data.talent[16]*50 + target_data.talent[17]*80 + target_data.talent[18]*100
    judge += judge_fall
    if judge_fall:
        calculation_text += "+陷落修正("+ str(judge_fall) +")"
    #讨厌男性修正#
    judge_hate = target_data.talent[227]*30
    judge -= judge_hate
    if judge_hate:
        calculation_text += "+讨厌男性(-"+ str(judge_hate) +")"
    #难以越过的底线修正#
    judge_hardlove = target_data.talent[224]*30
    judge -= judge_hardlove
    if judge_hardlove:
        calculation_text += "+难以越过的底线(-"+ str(judge_hardlove) +")"
    #博士信息素修正#
    judge_information = character_data.talent[304]*10 + character_data.talent[305]*25 + character_data.talent[306]*50
    judge += judge_information
    if judge_information:
        calculation_text += "+博士信息素("+ str(judge_information) +")"

    # debug模式修正
    if cache.debug_mode == True:
        judge += 99999
        calculation_text += "+debug模式(+99999)"

    calculation_text += " = " + str(judge) + "\n"
    now_draw = draw.WaitDraw()
    now_draw.width = 1
    now_draw.text = calculation_text
    now_draw.draw()
    if judge >= judge_data_value:
        return 1
    else:
        return 0

# def calculation_favorability(character_id: int, target_character_id: int, favorability: int) -> int:
#     """
#     按角色性格和关系计算最终增加的好感值
#     Keyword arguments:
#     character_id -- 角色id
#     target_character_id -- 目标角色id
#     favorability -- 基础好感值
#     Return arguments:
#     int -- 最终的好感值
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[target_character_id]
#     fix = 1.0
#     for i in {0, 1, 2, 5, 13, 14, 15, 16}:
#         now_fix = 0
#         if character_data.nature[i] > 50:
#             nature_value = character_data.nature[i] - 50
#             now_fix -= nature_value / 50
#         else:
#             now_fix += character_data.nature[i] / 50
#         if target_data.nature[i] > 50:
#             nature_value = target_data.nature[i] - 50
#             if now_fix < 0:
#                 now_fix *= -1
#                 now_fix += nature_value / 50
#                 now_fix = now_fix / 2
#             else:
#                 now_fix += nature_value / 50
#         else:
#             nature_value = target_data.nature[i]
#             if now_fix < 0:
#                 now_fix += nature_value / 50
#             else:
#                 now_fix -= nature_value / 50
#                 now_fix = now_fix / 2
#         fix += now_fix
#     if character_id in target_data.social_contact_data:
#         fix += target_data.social_contact_data[character_id]
#     favorability *= fix
#     return favorability


def judge_character_time_over_24(character_id: int) -> bool:
    """
    校验角色的时间是否已过24点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    start_time: datetime.datetime = character_data.behavior.start_time
    end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
    judge = 0
    if end_time.day != start_time.day:
        judge = 1
    return judge