import math
import datetime
from typing import List
from uuid import UUID
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type
from Script.Design import map_handle, game_time, attr_calculation, character
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def add_premise(premise: str) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_premise_data[premise] = return_wrapper
        return return_wrapper

    return decoraror


def handle_premise(premise: str, character_id: int) -> int:
    """
    调用前提id对应的前提处理函数
    Keyword arguments:
    premise -- 前提id
    character_id -- 角色id
    Return arguments:
    int -- 前提权重加成
    """
    if premise in constant.handle_premise_data:
        return constant.handle_premise_data[premise](character_id)
    else:
        return 0


@add_premise(constant.Premise.IN_CAFETERIA)
def handle_in_cafeteria(character_id: int) -> int:
    """
    校验角色是否处于取餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Cafeteria":
        return 1
    return 0


@add_premise(constant.Premise.IN_RESTAURANT)
def handle_in_restaurant(character_id: int) -> int:
    """
    校验角色是否处于就餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Restaurant":
        return 1
    return 0


@add_premise(constant.Premise.IN_BREAKFAST_TIME)
def handle_in_breakfast_time(character_id: int) -> int:
    """
    校验当前时间是否处于早餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return (now_time == 4) * 100


@add_premise(constant.Premise.IN_LUNCH_TIME)
def handle_in_lunch_time(character_id: int) -> int:
    """
    校验当前是否处于午餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return (now_time == 7) * 100


@add_premise(constant.Premise.IN_DINNER_TIME)
def handle_in_dinner_time(character_id: int) -> int:
    """
    校验当前是否处于晚餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return (now_time == 9) * 100


@add_premise(constant.Premise.HUNGER)
def handle_hunger(character_id: int) -> int:
    """
    校验角色是否处于饥饿状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status_data.setdefault(27, 0)
    # if character_data.status[27] > 15:
    #     return math.floor(character_data.status[27]) * 10
    return 0


@add_premise(constant.Premise.HAVE_FOOD)
def handle_have_food(character_id: int) -> int:
    """
    校验角色是否拥有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 0
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id]:
            food_index += 1
    return food_index


@add_premise(constant.Premise.NOT_HAVE_FOOD)
def handle_not_have_food(character_id: int) -> int:
    """
    校验角色是否没有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 1
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id].eat and 27 in character_data.food_bag[food_id].feel:
            return 0
    return food_index


@add_premise(constant.Premise.HAVE_TARGET)
def handle_have_target(character_id: int) -> int:
    """
    校验角色是否有交互对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == character_id:
        return 0
    return 1


@add_premise(constant.Premise.TARGET_NO_PLAYER)
def handle_target_no_player(character_id: int) -> int:
    """
    校验角色目标对像是否不是玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id > 0:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_DRAW_ITEM)
def handle_have_item_by_tag_draw(character_id: int) -> int:
    """
    校验角色是否拥有绘画类道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for item_id in game_config.config_item_tag_data["Draw"]:
        if item_id in character_data.item:
            return 1
    return 0


@add_premise(constant.Premise.HAVE_SHOOTING_ITEM)
def handle_have_item_by_tag_shooting(character_id: int) -> int:
    """
    校验角色是否拥有射击类道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for item_id in game_config.config_item_tag_data["Shooting"]:
        if item_id in character_data.item:
            return 1
    return 0


@add_premise(constant.Premise.HAVE_GUITAR)
def handle_have_guitar(character_id: int) -> int:
    """
    校验角色是否拥有吉他
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 4 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_HARMONICA)
def handle_have_harmonica(character_id: int) -> int:
    """
    校验角色是否拥有口琴
    Keyword arguments:
    character_id --角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 5 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BAM_BOO_FLUTE)
def handle_have_bamboogflute(character_id: int) -> int:
    """
    校验角色是否拥有竹笛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 6 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BASKETBALL)
def handle_have_basketball(character_id: int) -> int:
    """
    校验角色是否拥有篮球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 0 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_FOOTBALL)
def handle_have_football(character_id: int) -> int:
    """
    校验角色是否拥有足球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 1 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_TABLE_TENNIS)
def handle_have_tabletennis(character_id: int) -> int:
    """
    校验角色是否拥有乒乓球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 2 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.IN_SWIMMING_POOL)
def handle_in_swimming_pool(character_id: int) -> int:
    """
    校验角色是否在游泳池中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "SwimmingPool":
        return 1
    return 0


@add_premise(constant.Premise.IN_CLASSROOM)
def handle_in_classroom(character_id: int) -> int:
    """
    校验角色是否处于所属教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    # if now_scene_str == character_data.classroom:
    #     return 1
    return 0


@add_premise(constant.Premise.IS_STUDENT)
def handle_is_student(character_id: int) -> int:
    """
    校验角色是否是学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.age <= 18:
        return 1
    return 0


@add_premise(constant.Premise.IS_TEACHER)
def handle_is_teacher(character_id: int) -> int:
    """
    校验角色是否是老师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return character_id in cache.teacher_school_timetable


@add_premise(constant.Premise.IN_SHOP)
def handle_in_shop(character_id: int) -> int:
    """
    校验角色是否在商店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Shop":
        return 1
    return 0

@add_premise(constant.Premise.IN_KITCHEN)
def handle_in_kitchen(character_id: int) -> int:
    """
    校验角色是否在厨房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Kitchen":
        return 1
    return 0


@add_premise(constant.Premise.IN_DINING_HALL)
def handle_in_dining_hall(character_id: int) -> int:
    """
    校验角色是否在食堂中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Dining_hall":
        return 1
    return 0


@add_premise(constant.Premise.IN_DR_OFFICE)
def handle_in_dr_office(character_id: int) -> int:
    """
    校验角色是否在博士办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Dr_office":
        return 1
    return 0


@add_premise(constant.Premise.IN_DORMITORY)
def handle_in_dormitory(character_id: int) -> int:
    """
    校验角色是否在自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = map_handle.get_map_system_path_str_for_list(character_data.position)
    return now_position == character_data.dormitory


@add_premise(constant.Premise.NOT_IN_DORMITORY)
def handle_not_in_dormitory(character_id: int) -> int:
    """
    校验角色是否不在自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = map_handle.get_map_system_path_str_for_list(character_data.position)
    return now_position != character_data.dormitory


@add_premise(constant.Premise.HAVE_MOVED)
def handle_have_moved(character_id: int) -> int:
    """
    NPC距离上次移动已经至少经过了1小时
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    move_flag = 0
    #同一天内过1小时则判定为1
    if now_time.day == character_data.last_move_time.day and now_time.hour > character_data.last_move_time.hour:
        character_data.last_move_time = now_time
        print("过一小时判定,character_id :",character_id)
        move_flag = 1
    #非同一天也判定为1
    elif now_time.day != character_data.last_move_time.day:
        character_data.last_move_time = now_time
        move_flag = 1
        print("非同一天判定")
    return move_flag


@add_premise(constant.Premise.AI_WAIT)
def handle_ai_wait(character_id: int) -> int:
    """
    NPC需要进行一次5分钟的等待（wait_flag = 1)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.wait_flag:
        # print("判断到需要进行等待，character_id = ",character_id)
        return 999
    else:
        return 0


@add_premise(constant.Premise.IN_SLEEP_TIME)
def handle_in_sleep_time(character_id: int) -> int:
    """
    校验角色当前是否处于睡觉时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 22 or now_time.hour <= 4:
        return 500
    return 0


@add_premise(constant.Premise.IN_SIESTA_TIME)
def handle_in_siesta_time(character_id: int) -> int:
    """
    校验角色是否处于午休时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 12 or now_time.hour <= 15:
        return 100
    return 0


@add_premise(constant.Premise.TARGET_IS_FUTA_OR_WOMAN)
def handle_target_is_futa_or_woman(character_id: int) -> int:
    """
    校验角色的目标对象性别是否为女性或扶她
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex in {1, 2}:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_FUTA_OR_MAN)
def handle_target_is_futa_or_man(character_id: int) -> int:
    """
    校验角色的目标对象性别是否为男性或扶她
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex in {0, 1}:
        return 1
    return 0


@add_premise(constant.Premise.IS_MAN)
def handle_is_man(character_id: int) -> int:
    """
    校验角色是否是男性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if not character_data.sex:
        return 1
    return 0


@add_premise(constant.Premise.IS_WOMAN)
def handle_is_woman(character_id: int) -> int:
    """
    校验角色是否是女性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sex == 1:
        return 1
    return 0


@add_premise(constant.Premise.HIGH_1)
def handle_high_1(character_id: int) -> int:
    """
    优先度为1的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 1


@add_premise(constant.Premise.HIGH_5)
def handle_high_5(character_id: int) -> int:
    """
    优先度为5的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 5


@add_premise(constant.Premise.HIGH_10)
def handle_high_10(character_id: int) -> int:
    """
    优先度为10的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 10


@add_premise(constant.Premise.HP_1)
def handle_hp_1(character_id: int) -> int:
    """
    自身疲劳（体力=1）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.tired == 1:
        return 999
    else:
        return 0


@add_premise(constant.Premise.HP_LOW)
def handle_hp_low(character_id: int) -> int:
    """
    角色体力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.hit_point / character_data.hit_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant.Premise.HP_HIGH)
def handle_hp_high(character_id: int) -> int:
    """
    角色体力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.hit_point / character_data.hit_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant.Premise.MP_0)
def handle_mp_0(character_id: int) -> int:
    """
    角色气力为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point
    if value == 0:
        return 1
    else:
        return 0

@add_premise(constant.Premise.MP_LOW)
def handle_mp_low(character_id: int) -> int:
    """
    角色气力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point / character_data.mana_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant.Premise.MP_HIGH)
def handle_mp_high(character_id: int) -> int:
    """
    角色气力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point / character_data.mana_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_HP_LOW)
def handle_target_hp_low(character_id: int) -> int:
    """
    交互对象体力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.hit_point / target_data.hit_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_HP_HIGH)
def handle_target_hp_high(character_id: int) -> int:
    """
    交互对象体力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.hit_point / target_data.hit_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_MP_0)
def handle_target_mp_0(character_id: int) -> int:
    """
    交互对象气力为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.mana_point
    if value == 0:
        return 1
    else:
        return 0

@add_premise(constant.Premise.TARGET_MP_LOW)
def handle_target_mp_low(character_id: int) -> int:
    """
    交互对象气力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.mana_point / target_data.mana_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_MP_HIGH)
def handle_target_mp_high(character_id: int) -> int:
    """
    交互对象气力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.mana_point / target_data.mana_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_GOOD_MOOD)
def handle_target_good_mood(character_id: int) -> int:
    """
    交互对象心情愉快
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.angry_point
    if value <= 5:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_NORMAL_MOOD)
def handle_target_normal_mood(character_id: int) -> int:
    """
    交互对象心情普通
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.angry_point
    if 5 < value and value <= 30:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_BAD_MOOD)
def handle_target_bad_mood(character_id: int) -> int:
    """
    交互对象心情不好
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.angry_point
    if 30 < value and value <=50:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_ANGRY_MOOD)
def handle_target_angry_mood(character_id: int) -> int:
    """
    交互对象心情愤怒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.angry_point
    if value > 50:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_ABD_OR_ANGRY_MOOD)
def handle_bad_or_angry_mood(character_id: int) -> int:
    """
    交互对象心情不好或愤怒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.angry_point
    if value > 30:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_ANGRY_WITH_PLAYER)
def handle_target_angry_with_player(character_id: int) -> int:
    """
    交互对象被玩家惹火了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.angry_with_player:
        return 1
    else:
        return 0


@add_premise(constant.Premise.TARGET_NOT_ANGRY_WITH_PLAYER)
def handle_target_not_angry_with_player(character_id: int) -> int:
    """
    交互对象没有被玩家惹火
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.angry_with_player:
        return 0
    else:
        return 1


@add_premise(constant.Premise.COOK_1)
def handle_cook_1(character_id: int) -> int:
    """
    校验角色是否料理技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] == 1:
        return 1
    return 0


@add_premise(constant.Premise.COOK_2)
def handle_cook_2(character_id: int) -> int:
    """
    校验角色是否料理技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] == 2:
        return 1
    return 0


@add_premise(constant.Premise.COOK_3)
def handle_cook_3(character_id: int) -> int:
    """
    校验角色是否料理技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] == 3:
        return 1
    return 0


@add_premise(constant.Premise.COOK_4)
def handle_cook_4(character_id: int) -> int:
    """
    校验角色是否料理技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] == 4:
        return 1
    return 0


@add_premise(constant.Premise.COOK_LE_1)
def handle_cook_le_1(character_id: int) -> int:
    """
    校验角色是否料理技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] <= 1:
        return 1
    return 0


@add_premise(constant.Premise.COOK_GE_3)
def handle_cook_ge_3(character_id: int) -> int:
    """
    校验角色是否料理技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.COOK_GE_5)
def handle_cook_ge_3(character_id: int) -> int:
    """
    校验角色是否料理技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[28] >= 5:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_1)
def handle_music_1(character_id: int) -> int:
    """
    校验角色是否音乐技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] == 1:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_2)
def handle_music_2(character_id: int) -> int:
    """
    校验角色是否音乐技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] == 2:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_3)
def handle_music_3(character_id: int) -> int:
    """
    校验角色是否音乐技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] == 3:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_4)
def handle_music_4(character_id: int) -> int:
    """
    校验角色是否音乐技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] == 4:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_LE_1)
def handle_music_le_1(character_id: int) -> int:
    """
    校验角色是否音乐技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] <= 1:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_GE_3)
def handle_music_ge_3(character_id: int) -> int:
    """
    校验角色是否音乐技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.MUSIC_GE_5)
def handle_music_ge_3(character_id: int) -> int:
    """
    校验角色是否音乐技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[29] >= 5:
        return 1
    return 0


@add_premise(constant.Premise.TECHNIQUE_GE_3)
def handle_technique_ge_3(character_id: int) -> int:
    """
    校验角色是否技巧技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[19] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.TECHNIQUE_GE_5)
def handle_technique_ge_3(character_id: int) -> int:
    """
    校验角色是否技巧技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[19] >= 5:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_DESIRE_GE_5)
def handle_target_desire_ge_5(character_id: int) -> int:
    """
    校验交互对象是否欲望技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[22] >= 5:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_DESIRE_GE_7)
def handle_target_desire_ge_7(character_id: int) -> int:
    """
    校验交互对象是否欲望技能>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[22] >= 7:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_1)
def handle_target_cook_1(character_id: int) -> int:
    """
    校验交互对象是否料理技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] == 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_2)
def handle_target_cook_2(character_id: int) -> int:
    """
    校验交互对象是否料理技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] == 2:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_3)
def handle_target_cook_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] == 3:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_4)
def handle_target_cook_4(character_id: int) -> int:
    """
    校验交互对象是否料理技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] == 4:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_LE_1)
def handle_target_cook_le_1(character_id: int) -> int:
    """
    校验交互对象是否料理技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] <= 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_GE_3)
def handle_target_cook_ge_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_COOK_GE_5)
def handle_target_cook_ge_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[28] >= 5:
        return 1
    return 0



@add_premise(constant.Premise.TARGET_MUSIC_1)
def handle_target_music_1(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] == 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_MUSIC_2)
def handle_target_music_2(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] == 2:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_MUSIC_3)
def handle_target_music_3(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] == 3:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_MUSIC_4)
def handle_target_music_4(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] == 4:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_MUSIC_LE_1)
def handle_target_music_le_1(character_id: int) -> int:
    """
    校验交互对象是否音乐技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] <= 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_MUSIC_GE_3)
def handle_target_music_ge_3(character_id: int) -> int:
    """
    校验交互对象是否音乐技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_MUSIC_GE_5)
def handle_target_music_ge_3(character_id: int) -> int:
    """
    校验交互对象是否音乐技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[29] >= 5:
        return 1
    return 0

@add_premise(constant.Premise.TARGET_INTIMACY_8)
def handle_target_intimacy_8(character_id: int) -> int:
    """
    校验交互对象是否亲密==8
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[21] == 8:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_INTIMACY_LE_1)
def handle_target_intimacy_le_1(character_id: int) -> int:
    """
    校验交互对象是否亲密<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[21] <= 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_INTIMACY_GE_3)
def handle_target_intimacy_ge_3(character_id: int) -> int:
    """
    校验交互对象是否亲密>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[21] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_INTIMACY_GE_5)
def handle_target_intimacy_ge_3(character_id: int) -> int:
    """
    校验交互对象是否亲密>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[21] >= 5:
        return 1
    return 0



@add_premise(constant.Premise.TARGET_TECHNIQUE_GE_3)
def handle_t_technique_ge_3(character_id: int) -> int:
    """
    校验交互对象是否技巧技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[19] >= 3:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_TECHNIQUE_GE_5)
def handle_t_technique_ge_3(character_id: int) -> int:
    """
    校验交互对象是否技巧技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[19] >= 5:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_NOT_FALL)
def handle_target_not_fall(character_id: int) -> int:
    """
    角色无陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {10,11,12,13,15,16,17,18}:
        if target_data.talent[i]:
            return 0
    return 1


@add_premise(constant.Premise.TARGET_LOVE_1)
def handle_target_love_1(character_id: int) -> int:
    """
    校验交互对象是否是思慕,爱情系第一阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[10]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_2)
def handle_target_love_2(character_id: int) -> int:
    """
    校验交互对象是否是恋慕,爱情系第二阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[11]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_3)
def handle_target_love_3(character_id: int) -> int:
    """
    校验交互对象是否是恋人,爱情系第三阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[12]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_4)
def handle_target_love_4(character_id: int) -> int:
    """
    校验交互对象是否是爱侣,爱情系第四阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[13]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_GE_1)
def handle_target_love_ge_1(character_id: int) -> int:
    """
    交互对象爱情系>=思慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {10,11,12,13}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_GE_2)
def handle_target_love_ge_2(character_id: int) -> int:
    """
    交互对象爱情系>=恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {11,12,13}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_GE_3)
def handle_target_love_ge_3(character_id: int) -> int:
    """
    交互对象爱情系>=恋人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {12,13}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_LOVE_LE_2)
def handle_target_love_le_2(character_id: int) -> int:
    """
    交互对象爱情系<=恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {12,13}:
        if target_data.talent[i]:
            return 0
    return 1


@add_premise(constant.Premise.TARGET_OBEY_1)
def handle_target_obey_1(character_id: int) -> int:
    """
    校验交互对象是否是屈从,隶属系第一阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[15]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_OBEY_2)
def handle_target_obey_2(character_id: int) -> int:
    """
    校验交互对象是否是驯服,隶属系第二阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[16]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_OBEY_3)
def handle_target_obey_3(character_id: int) -> int:
    """
    校验交互对象是否是宠物,隶属系第三阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[17]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_OBEY_4)
def handle_target_obey_4(character_id: int) -> int:
    """
    校验交互对象是否是奴隶,隶属系第四阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[18]:
        return 1
    return 0

@add_premise(constant.Premise.TARGET_OBEY_GE_1)
def handle_target_obey_ge_1(character_id: int) -> int:
    """
    交互对象隶属系>=屈从
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {15,16,17,18}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_OBEY_GE_2)
def handle_target_obey_ge_2(character_id: int) -> int:
    """
    交互对象隶属系>=驯服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {16,17,18}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_OBEY_GE_3)
def handle_target_obey_ge_3(character_id: int) -> int:
    """
    交互对象隶属系>=宠物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {17,18}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_OBEY_LE_2)
def handle_target_obey_le_2(character_id: int) -> int:
    """
    交互对象隶属系<=驯服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {17,18}:
        if target_data.talent[i]:
            return 0
    return 1


@add_premise(constant.Premise.TARGET_SAME_SEX)
def handle_target_same_sex(character_id: int) -> int:
    """
    校验角色目标对像是否与自己性别相同
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex == character_data.sex:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_NO_FIRST_KISS)
def handle_target_no_first_kiss(character_id: int) -> int:
    """
    校验交互对象是否初吻还在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[4] == 1

@add_premise(constant.Premise.TARGET_HAVE_FIRST_KISS)
def handle_target_have_first_kiss(character_id: int) -> int:
    """
    校验交互对象是否初吻不在了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[4] == 1


@add_premise(constant.Premise.TARGET_NO_VIRGIN)
def handle_target_no_virgin(character_id: int) -> int:
    """
    校验交互对象是否非处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[0] == 1

@add_premise(constant.Premise.TARGET_HAVE_VIRGIN)
def handle_target_have_virgin(character_id: int) -> int:
    """
    校验交互对象是否是处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[0] == 1


@add_premise(constant.Premise.TARGET_NO_A_VIRGIN)
def handle_target_no_a_virgin(character_id: int) -> int:
    """
    校验交互对象是否非A处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[1] == 1

@add_premise(constant.Premise.TARGET_HAVE_A_VIRGIN)
def handle_target_have_a_virgin(character_id: int) -> int:
    """
    校验交互对象是否是A处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[1] == 1


# @add_premise(constant.Premise.TARGET_AGE_SIMILAR)
# def handle_target_age_similar(character_id: int) -> int:
#     """
#     校验角色目标对像是否与自己年龄相差不大
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data = cache.character_data[character_id]
#     target_data = cache.character_data[character_data.target_character_id]
#     if character_data.age >= target_data.age - 2 and character_data.age <= target_data.age + 2:
#         return 1
#     return 0


# @add_premise(constant.Premise.TARGET_AVERAGE_HEIGHT_SIMILAR)
# def handle_target_average_height_similar(character_id: int) -> int:
#     """
#     校验角色目标身高是否与平均身高相差不大
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data = cache.character_data[character_id]
#     target_data = cache.character_data[character_data.target_character_id]
#     age_tem = attr_calculation.judge_age_group(target_data.age)
#     average_height = cache.average_height_by_age[age_tem][target_data.sex]
#     if (
#         target_data.height.now_height >= average_height * 0.95
#         and target_data.height.now_height <= average_height * 1.05
#     ):
#         return 1
#     return 0


# @add_premise(constant.Premise.TARGET_AVERAGE_HEIGHT_LOW)
# def handle_target_average_height_low(character_id: int) -> int:
#     """
#     校验角色目标的身高是否低于平均身高
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data = cache.character_data[character_id]
#     target_data = cache.character_data[character_data.target_character_id]
#     age_tem = attr_calculation.judge_age_group(target_data.age)
#     average_height = cache.average_height_by_age[age_tem][target_data.sex]
#     if target_data.height.now_height <= average_height * 0.95:
#         return 1
#     return 0


@add_premise(constant.Premise.TARGET_IS_PLAYER)
def handle_target_is_player(character_id: int) -> int:
    """
    校验角色目标是否是玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == 0:
        return 1
    return 0


# @add_premise(constant.Premise.TARGET_AVERGAE_STATURE_SIMILAR)
# def handle_target_average_stature_similar(character_id: int) -> int:
#     """
#     校验角色目体型高是否与平均体型相差不大
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data = cache.character_data[character_id]
#     target_data = cache.character_data[character_data.target_character_id]
#     age_tem = attr_calculation.judge_age_group(target_data.age)
#     if age_tem in cache.average_bodyfat_by_age:
#         average_bodyfat = cache.average_bodyfat_by_age[age_tem][target_data.sex]
#         if target_data.bodyfat >= average_bodyfat * 0.95 and target_data.bodyfat <= average_bodyfat * 1.05:
#             return 1
#     return 0


@add_premise(constant.Premise.TARGET_NOT_PUT_ON_UNDERWEAR)
def handle_target_not_put_underwear(character_id: int) -> int:
    """
    校验角色的目标对象是否没穿上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if (1 not in target_data.put_on) or (target_data.put_on[1] == ""):
        return 1
    return 0


@add_premise(constant.Premise.TARGET_NOT_PUT_ON_SKIRT)
def handle_target_put_on_skirt(character_id: int) -> int:
    """
    校验角色的目标对象是否穿着短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if (3 not in target_data.put_on) or (target_data.put_on[3] == ""):
        return 0
    return 1


@add_premise(constant.Premise.DEBUG_MODE_ON)
def handle_idebug_mode_on(character_id: int) -> int:
    """
    校验当前是否已经是debug模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.debug_mode:
        return 1
    return 0


@add_premise(constant.Premise.DEBUG_MODE_OFF)
def handle_idebug_mode_off(character_id: int) -> int:
    """
    校验当前不是debug模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.debug_mode:
        return 0
    return 1


@add_premise(constant.Premise.TO_DO)
def handle_todo(character_id: int) -> int:
    """
    未实装
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.debug_mode:
        return 1
    return 0


@add_premise(constant.Premise.IS_PLAYER)
def handle_is_player(character_id: int) -> int:
    """
    校验指令使用人是否是玩家角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if not character_id:
        return 1
    return 0


@add_premise(constant.Premise.NO_PLAYER)
def handle_no_player(character_id: int) -> int:
    """
    校验指令使用人是否不是玩家角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id:
        return 1
    return 0


@add_premise(constant.Premise.IN_PLAYER_SCENE)
def handle_in_player_scene(character_id: int) -> int:
    """
    校验角色是否与玩家处于同场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if now_character_data.position == cache.character_data[0].position:
        return 1
    return 0


@add_premise(constant.Premise.NOT_IN_PLAYER_SCENE)
def handle_not_in_player_scene(character_id: int) -> int:
    """
    校验角色是否不与玩家处于同场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if now_character_data.position == cache.character_data[0].position:
        return 0
    return 1


@add_premise(constant.Premise.SCENE_ONLY_TWO)
def handle_scene_only_two(character_id: int) -> int:
    """
    该地点仅有玩家和该角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    return len(scene_data.character_list) == 2


@add_premise(constant.Premise.SCENE_OVER_TWO)
def handle_scene_over_two(character_id: int) -> int:
    """
    该地点里有除了玩家和该角色之外的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    return len(scene_data.character_list) > 2


@add_premise(constant.Premise.SCENE_SOMEONE_IS_H)
def handle_scene_someone_is_h(character_id: int) -> int:
    """
    该地点有其他角色在和玩家H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    #场景角色数大于2时进行检测
    if len(scene_data.character_list) > 2 and not (character_data.is_follow or character_data.is_h):
        #遍历当前角色列表
        for chara_id in scene_data.character_list:
            #遍历非自己且非玩家的角色
            if chara_id != character_id and chara_id != 0:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                #检测是否在H
                if other_character_data.is_h:
                    return 999
    return 0


@add_premise(constant.Premise.TATGET_LEAVE_SCENE)
def handle_target_leave_scene(character_id: int) -> int:
    """
    校验角色是否是从玩家场景离开
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if (
        now_character_data.behavior.move_src == cache.character_data[0].position
        and now_character_data.behavior.move_target != cache.character_data[0].position
        and now_character_data.position != cache.character_data[0].position
    ):
        return 1
    return 0


@add_premise(constant.Premise.TIME_DAY)
def handle_time_day(character_id: int) -> int:
    """
    时间:白天（6点~18点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 6 and now_time.hour <= 18:
        return 1
    return 0


@add_premise(constant.Premise.TIME_NIGHT)
def handle_time_night(character_id: int) -> int:
    """
    时间:夜晚（18点~6点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour <= 6 or now_time.hour >= 18:
        return 1
    return 0


@add_premise(constant.Premise.TIME_MIDNIGHT)
def handle_time_midnight(character_id: int) -> int:
    """
    时间:深夜（22点~2点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour <= 2 or now_time.hour >= 22:
        return 1
    return 0


@add_premise(constant.Premise.TIME_MORNING)
def handle_time_morning(character_id: int) -> int:
    """
    时间:清晨（4点~8点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 4 and now_time.hour <= 8:
        return 1
    return 0


@add_premise(constant.Premise.TIME_MOON)
def handle_time_moon(character_id: int) -> int:
    """
    时间:中午（10点~14点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 10 and now_time.hour <= 14:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_ADORE)
def handle_target_is_adore(character_id: int) -> int:
    """
    校验角色当前目标是否是自己的爱慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_id = character_data.target_character_id
    character_data.social_contact.setdefault(5, set())
    if target_id in character_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_ADMIRE)
def handle_target_is_admire(character_id: int) -> int:
    """
    校验角色当前的目标是否是自己的恋慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_id = character_data.target_character_id
    character_data.social_contact.setdefault(4, set())
    if target_id in character_data.social_contact[4]:
        return 1
    return 0


@add_premise(constant.Premise.PLAYER_IS_ADORE)
def handle_player_is_adore(character_id: int) -> int:
    """
    校验玩家是否是当前角色的爱慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    character_data.social_contact.setdefault(5, set())
    if 0 in character_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.EAT_SPRING_FOOD)
def handle_eat_spring_food(character_id: int) -> int:
    """
    校验角色是否正在食用春药品质的食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.food_quality == 4:
        return 1
    return 0


# @add_premise(constant.Premise.IS_HUMOR_MAN)
# def handle_is_humor_man(character_id: int) -> int:
#     """
#     校验角色是否是一个幽默的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     value = 0
#     character_data: game_type.Character = cache.character_data[character_id]
#     for i in {0, 1, 2, 5, 13, 14, 15, 16}:
#         nature = character_data.nature[i]
#         if nature > 50:
#             value -= nature - 50
#         else:
#             value += 50 - nature
#     if value < 0:
#         value = 0
#     return value


@add_premise(constant.Premise.TARGET_IS_BEYOND_FRIENDSHIP)
def handle_target_is_beyond_friendship(character_id: int) -> int:
    """
    校验是否对目标抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        character_data.target_character_id in character_data.social_contact_data
        and character_data.social_contact_data[character_data.target_character_id] > 2
    ):
        return character_data.social_contact_data[character_data.target_character_id]
    return 0


@add_premise(constant.Premise.IS_BEYOND_FRIENDSHIP_TARGET)
def handle_is_beyond_friendship_target(character_id: int) -> int:
    """
    校验目标是否对自己抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if (
        character_id in target_data.social_contact_data
        and target_data.social_contact_data[character_id] > 2
    ):
        return target_data.social_contact_data[character_id]
    return 0


@add_premise(constant.Premise.NO_WEAR_UNDERWEAR)
def handle_no_wear_underwear(character_id: int) -> int:
    """
    校验角色是否没穿上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 1 not in character_data.put_on or character_data.put_on[1] is None or character_data.put_on[1] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_UNDERPANTS)
def handle_no_wear_underpants(character_id: int) -> int:
    """
    校验角色是否没穿内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 7 not in character_data.put_on or character_data.put_on[7] is None or character_data.put_on[7] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_BRA)
def handle_no_wear_bra(character_id: int) -> int:
    """
    校验角色是否没穿胸罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 6 not in character_data.put_on or character_data.put_on[6] is None or character_data.put_on[6] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_PANTS)
def handle_no_wear_pants(character_id: int) -> int:
    """
    校验角色是否没穿裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 2 not in character_data.put_on or character_data.put_on[2] is None or character_data.put_on[2] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SKIRT)
def handle_no_wear_skirt(character_id: int) -> int:
    """
    校验角色是否没穿短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 3 not in character_data.put_on or character_data.put_on[3] is None or character_data.put_on[3] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SHOES)
def handle_no_wear_shoes(character_id: int) -> int:
    """
    校验角色是否没穿鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 4 not in character_data.put_on or character_data.put_on[4] is None or character_data.put_on[4] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SOCKS)
def handle_no_wear_socks(character_id: int) -> int:
    """
    校验角色是否没穿袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 5 not in character_data.put_on or character_data.put_on[5] is None or character_data.put_on[5] == "":
        return 1
    return 0


@add_premise(constant.Premise.WANT_PUT_ON)
def handle_want_put_on(character_id: int) -> int:
    """
    校验角色是否想穿衣服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return (not character_data.no_wear) * 10


@add_premise(constant.Premise.HAVE_UNDERWEAR)
def handle_have_underwear(character_id: int) -> int:
    """
    校验角色是否拥有上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 1 in character_data.clothing and len(character_data.clothing[1]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_UNDERPANTS)
def handle_have_underpants(character_id: int) -> int:
    """
    校验角色是否拥有内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 7 in character_data.clothing and len(character_data.clothing[7]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BRA)
def handle_have_bra(character_id: int) -> int:
    """
    校验角色是否拥有胸罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 6 in character_data.clothing and len(character_data.clothing[6]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_PANTS)
def handle_have_pants(character_id: int) -> int:
    """
    校验角色是否拥有裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 2 in character_data.clothing and len(character_data.clothing[2]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SKIRT)
def handle_have_skirt(character_id: int) -> int:
    """
    校验角色是否拥有短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 3 in character_data.clothing and len(character_data.clothing[3]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SHOES)
def handle_have_shoes(character_id: int) -> int:
    """
    校验角色是否拥有鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 4 in character_data.clothing and len(character_data.clothing[4]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SOCKS)
def handle_have_socks(character_id: int) -> int:
    """
    校验角色是否拥有袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 5 in character_data.clothing and len(character_data.clothing[5]):
        return 1
    return 0


@add_premise(constant.Premise.CHEST_IS_NOT_CLIFF)
def handle_chest_is_not_cliff(character_id: int) -> int:
    """
    校验角色胸围是否不是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return attr_calculation.judge_chest_group(character_data.chest.now_chest)


# @add_premise(constant.Premise.EXCELLED_AT_PLAY_MUSIC)
# def handle_excelled_at_play_music(character_id: int) -> int:
#     """
#     校验角色是否擅长演奏乐器
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[25]
#     if 25 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[25])
#         return weight * level
#     return weight


# @add_premise(constant.Premise.EXCELLED_AT_SINGING)
# def handle_excelled_at_singing(character_id: int) -> int:
#     """
#     校验角色是否擅长演唱
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[15]
#     if 15 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[15])
#         return weight * level
#     return weight


@add_premise(constant.Premise.IN_MUSIC_ROOM)
def handle_in_music_room(character_id: int) -> int:
    """
    校验角色是否处于音乐活动室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Musicroom":
        return 1
    return 0


@add_premise(constant.Premise.NO_EXCELLED_AT_SINGING)
def handle_no_excelled_at_singing(character_id: int) -> int:
    """
    校验角色是否不擅长演唱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 8
    if 15 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[15])
        return 8 - level
    return weight


@add_premise(constant.Premise.SCENE_ONLY_ONE)
def handle_scene_only_one(character_id: int) -> int:
    """
    该地点里没有自己外的其他角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path]
    return len(scene_data.character_list) == 1


@add_premise(constant.Premise.TARGET_HEIGHT_LOW)
def handle_target_height_low(character_id: int) -> int:
    """
    校验交互对象身高是否低于自身身高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.height.now_height < character_data.height.now_height:
        return character_data.height.now_height - target_data.height.now_height
    return 0


@add_premise(constant.Premise.TARGET_ADORE)
def handle_target_adore(character_id: int) -> int:
    """
    校验是否被交互对象爱慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.social_contact.setdefault(5, set())
    if character_id in target_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.NO_EXCELLED_AT_PLAY_MUSIC)
def handle_no_excelled_at_play_music(character_id: int) -> int:
    """
    校验角色是否不擅长演奏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 8
    if 25 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[25])
        return 8 - level
    return weight


@add_premise(constant.Premise.ARROGANT_HEIGHT)
def handle_arrogant_height(character_id: int) -> int:
    """
    校验角色是否傲慢情绪高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status_data.setdefault(15, 0)
    return int(character_data.status_data[15] / 10)


# @add_premise(constant.Premise.IS_LIVELY)
# def handle_is_lively(character_id: int) -> int:
#     """
#     校验角色是否是一个活跃的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[0] >= 50


# @add_premise(constant.Premise.IS_INFERIORITY)
# def handle_is_inferiority(character_id: int) -> int:
#     """
#     校验角色是否是一个自卑的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[16] < 50


# @add_premise(constant.Premise.IS_AUTONOMY)
# def handle_is_autonomy(character_id: int) -> int:
#     """
#     校验角色是否是一个自律的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[7] >= 50


@add_premise(constant.Premise.SCENE_CHARACTER_ONLY_PLAYER_AND_ONE)
def handle_scene_character_only_player_and_one(character_id: int) -> int:
    """
    校验场景中是否只有包括玩家在内的两个角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data: game_type.Scene = cache.scene_data[now_scene_str]
    if 0 not in now_scene_data.character_list:
        return 0
    return len(now_scene_data.character_list) == 2


# @add_premise(constant.Premise.IS_SOLITARY)
# def handle_is_solitary(character_id: int) -> int:
#     """
#     校验角色是否是一个孤僻的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[1] < 50


@add_premise(constant.Premise.NO_BEYOND_FRIENDSHIP_TARGET)
def handle_no_beyond_friendship_target(character_id: int) -> int:
    """
    校验目标是否对自己没有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if (
        character_id in target_data.social_contact_data
        and target_data.social_contact_data[character_id] < 3
    ):
        return 5 - target_data.social_contact_data[character_id]
    elif character_id not in target_data.social_contact_data:
        return 5
    return 0


# @add_premise(constant.Premise.TARGET_IS_HEIGHT)
# def handle_target_is_height(character_id: int) -> int:
#     """
#     校验角色目标身高是否与平均身高相差不大
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if target_data.height.now_height >= character_data.height.now_height * 1.05:
#         return 1
#     return 0


@add_premise(constant.Premise.BEYOND_FRIENDSHIP_TARGET_IN_SCENE)
def handle_beyond_friendship_target_in_scene(character_id: int) -> int:
    """
    校验是否对场景中某个角色抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data: game_type.Scene = cache.scene_data[now_scene_str]
    for i in {3, 4, 5}:
        character_data.social_contact.setdefault(i, set())
        for c in character_data.social_contact[i]:
            if c in now_scene_data.character_list:
                return 1
    return 0


@add_premise(constant.Premise.HYPOSTHENIA)
def handle_hyposthenia(character_id: int) -> int:
    """
    校验角色是否体力不足
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_weight = int((character_data.hit_point_max - character_data.hit_point) / 5)
    now_weight += int((character_data.mana_point_max - character_data.mana_point) / 10)
    return now_weight


@add_premise(constant.Premise.PHYSICAL_STRENGHT)
def handle_physical_strenght(character_id: int) -> int:
    """
    校验角色是否体力充沛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_weight = int((character_data.hit_point_max / 2 - character_data.hit_point) / 5)
    now_weight += int((character_data.mana_point_max / 2 - character_data.mana_point) / 10)
    if now_weight < 0:
        now_weight = 0
    return now_weight


# @add_premise(constant.Premise.IS_INDULGE)
# def handle_is_indulge(character_id: int) -> int:
#     """
#     校验角色是否是一个放纵的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[7] < 50


@add_premise(constant.Premise.IN_FOUNTAIN)
def handle_in_fountain(character_id: int) -> int:
    """
    校验角色是否在会客室入口场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position == ["8"]


# @add_premise(constant.Premise.TARGET_IS_SOLITARY)
# def handle_target_is_solitary(character_id: int) -> int:
#     """
#     校验交互对象是否是一个孤僻的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[1] < 50


@add_premise(constant.Premise.TARGET_CHEST_IS_CLIFF)
def handle_target_chest_is_cliff(character_id: int) -> int:
    """
    交互对象胸部大小是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[80]


@add_premise(constant.Premise.TARGET_CHEST_IS_SMALL)
def handle_target_chest_is_small(character_id: int) -> int:
    """
    交互对象胸部大小是贫乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[81]


@add_premise(constant.Premise.TARGET_CHEST_IS_NORMAL)
def handle_target_chest_is_normal(character_id: int) -> int:
    """
    交互对象胸部大小是普乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[82]


@add_premise(constant.Premise.TARGET_CHEST_IS_BIG)
def handle_target_chest_is_big(character_id: int) -> int:
    """
    交互对象胸部大小是巨乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[83]


@add_premise(constant.Premise.TARGET_CHEST_IS_SUPER)
def handle_target_chest_is_super(character_id: int) -> int:
    """
    交互对象胸部大小是爆乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[84]


@add_premise(constant.Premise.TARGET_BUTTOCKS_IS_SMALL)
def handle_target_buttock_is_small(character_id: int) -> int:
    """
    交互对象屁股大小是小尻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[85]


@add_premise(constant.Premise.TARGET_BUTTOCKS_IS_NORMAL)
def handle_target_buttock_is_normal(character_id: int) -> int:
    """
    交互对象胸部大小是普尻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[86]


@add_premise(constant.Premise.TARGET_BUTTOCKS_IS_BIG)
def handle_target_buttock_is_big(character_id: int) -> int:
    """
    交互对象胸部大小是巨尻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[87]


@add_premise(constant.Premise.TARGET_HAVE_NO_EARS)
def handle_target_have_no_eras(character_id: int) -> int:
    """
    交互对象没有兽耳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[70]


@add_premise(constant.Premise.TARGET_HAVE_EARS)
def handle_target_have_eras(character_id: int) -> int:
    """
    交互对象有兽耳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[70]


@add_premise(constant.Premise.TARGET_HAVE_NO_HORN)
def handle_target_have_no_horn(character_id: int) -> int:
    """
    交互对象没有兽角
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[71]


@add_premise(constant.Premise.TARGET_HAVE_HORN)
def handle_target_have_horn(character_id: int) -> int:
    """
    交互对象有兽角
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[71]


@add_premise(constant.Premise.TARGET_HAVE_NO_TAIL)
def handle_target_have_no_tail(character_id: int) -> int:
    """
    交互对象没有兽尾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[72]


@add_premise(constant.Premise.TARGET_HAVE_TAIL)
def handle_target_have_tail(character_id: int) -> int:
    """
    交互对象有兽尾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[72]


@add_premise(constant.Premise.TARGET_HAVE_NO_RING)
def handle_target_have_no_ring(character_id: int) -> int:
    """
    交互对象没有光环
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[73]


@add_premise(constant.Premise.TARGET_HAVE_RING)
def handle_target_have_ring(character_id: int) -> int:
    """
    交互对象有光环
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[73]


@add_premise(constant.Premise.TARGET_HAVE_NO_WING)
def handle_target_have_no_wing(character_id: int) -> int:
    """
    交互对象没有光翼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[74]


@add_premise(constant.Premise.TARGET_HAVE_WING)
def handle_target_have_wing(character_id: int) -> int:
    """
    交互对象有光翼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[74]


@add_premise(constant.Premise.TARGET_HAVE_NO_TENTACLE)
def handle_target_have_no_tentacle(character_id: int) -> int:
    """
    交互对象没有触手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[75]


@add_premise(constant.Premise.TARGET_HAVE_TENTACLE)
def handle_target_have_tentacle(character_id: int) -> int:
    """
    交互对象有触手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[75]


@add_premise(constant.Premise.TARGET_HAVE_NO_CAR)
def handle_target_have_no_car(character_id: int) -> int:
    """
    交互对象没有小车
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[76]


@add_premise(constant.Premise.TARGET_HAVE_CAR)
def handle_target_have_car(character_id: int) -> int:
    """
    交互对象有小车
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[76]


@add_premise(constant.Premise.TARGET_NOT_PATIENT)
def handle_target_not_patient(character_id: int) -> int:
    """
    交互对象不是源石病感染者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[150]


@add_premise(constant.Premise.TARGET_IS_PATIENT)
def handle_target_is_patient(character_id: int) -> int:
    """
    交互对象是源石病感染者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[150]


@add_premise(constant.Premise.TARGET_HAVE_NO_CRYSTAL)
def handle_target_have_no_crystal(character_id: int) -> int:
    """
    交互对象没有体表源石结晶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[162]


@add_premise(constant.Premise.TARGET_HAVE_CRYSTAL)
def handle_target_have_crystal(character_id: int) -> int:
    """
    交互对象有体表源石结晶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[162]


@add_premise(constant.Premise.TARGET_HAVE_NO_DILIGENT)
def handle_target_have_no_diligent(character_id: int) -> int:
    """
    交互对象非勤劳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[200]


@add_premise(constant.Premise.TARGET_HAVE_DILIGENT)
def handle_target_have_diligent(character_id: int) -> int:
    """
    交互对象勤劳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[200]


@add_premise(constant.Premise.TARGET_HAVE_NO_LAZY)
def handle_target_have_no_lazy(character_id: int) -> int:
    """
    交互对象非懒散
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[201]


@add_premise(constant.Premise.TARGET_HAVE_LAZY)
def handle_target_have_lazy(character_id: int) -> int:
    """
    交互对象懒散
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[201]


@add_premise(constant.Premise.TARGET_HAVE_NO_FRAGILE)
def handle_target_have_no_fragile(character_id: int) -> int:
    """
    交互对象非脆弱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[202]


@add_premise(constant.Premise.TARGET_HAVE_FRAGILE)
def handle_target_have_fragile(character_id: int) -> int:
    """
    交互对象脆弱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[202]


@add_premise(constant.Premise.TARGET_HAVE_NO_FORCEFUL)
def handle_target_have_no_forceful(character_id: int) -> int:
    """
    交互对象非坚强
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[203]


@add_premise(constant.Premise.TARGET_HAVE_FORCEFUL)
def handle_target_have_forceful(character_id: int) -> int:
    """
    交互对象坚强
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[203]


@add_premise(constant.Premise.TARGET_HAVE_NO_ENTHUSIACTIC)
def handle_target_have_no_enthusiactic(character_id: int) -> int:
    """
    交互对象非热情
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[204]


@add_premise(constant.Premise.TARGET_HAVE_ENTHUSIACTIC)
def handle_target_have_enthusiactic(character_id: int) -> int:
    """
    交互对象热情
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[204]


@add_premise(constant.Premise.TARGET_HAVE_NO_ALONE)
def handle_target_have_no_alone(character_id: int) -> int:
    """
    交互对象非孤僻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[205]


@add_premise(constant.Premise.TARGET_HAVE_ALONE)
def handle_target_have_alone(character_id: int) -> int:
    """
    交互对象孤僻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[205]


@add_premise(constant.Premise.TARGET_HAVE_NO_SHAME)
def handle_target_have_no_shame(character_id: int) -> int:
    """
    交互对象非羞耻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[206]


@add_premise(constant.Premise.TARGET_HAVE_SHAME)
def handle_target_have_shame(character_id: int) -> int:
    """
    交互对象羞耻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[206]


@add_premise(constant.Premise.TARGET_HAVE_NO_OPEN)
def handle_target_have_no_open(character_id: int) -> int:
    """
    交互对象非开放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[207]


@add_premise(constant.Premise.TARGET_HAVE_OPEN)
def handle_target_have_open(character_id: int) -> int:
    """
    交互对象开放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[207]


@add_premise(constant.Premise.LAST_CMD_BLOWJOB)
def handle_last_cmd_blowjob(character_id: int) -> int:
    """
    前一指令为口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    if len_input and (last_cmd == str(constant.Instruct.BLOWJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_MAKING_OUT)
def handle_last_cmd_makeing_out(character_id: int) -> int:
    """
    前一指令为身体爱抚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.MAKING_OUT)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_KISS_H)
def handle_last_cmd_kiss_h(character_id: int) -> int:
    """
    前一指令为接吻（H）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.KISS_H)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BREAST_CARESS)
def handle_last_cmd_breast_caress(character_id: int) -> int:
    """
    前一指令为胸爱抚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.BREAST_CARESS)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_TWIDDLE_NIPPLES)
def handle_last_cmd_twiddle_nipples(character_id: int) -> int:
    """
    前一指令为玩弄乳头
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.TWIDDLE_NIPPLES)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BREAST_SUCKING)
def handle_last_cmd_breast_sucking(character_id: int) -> int:
    """
    前一指令为舔吸乳头
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.BREAST_SUCKING)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_CLIT_CARESS)
def handle_last_cmd_clit_caress(character_id: int) -> int:
    """
    前一指令为阴蒂爱抚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.CLIT_CARESS)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_OPEN_LABIA)
def handle_last_cmd_open_labia(character_id: int) -> int:
    """
    前一指令为掰开阴唇观察
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.OPEN_LABIA)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_CUNNILINGUS)
def handle_last_cmd_cunnilingus(character_id: int) -> int:
    """
    前一指令为舔阴
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.CUNNILINGUS)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_FINGER_INSERTION)
def handle_last_cmd_finger_insertion(character_id: int) -> int:
    """
    前一指令为手指插入(V)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.FINGER_INSERTION)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_ANAL_CARESS)
def handle_last_cmd_anal_caress(character_id: int) -> int:
    """
    前一指令为手指插入(A)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.ANAL_CARESS)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_MAKE_MASTUREBATE)
def handle_last_cmd_make_masturebate(character_id: int) -> int:
    """
    前一指令为让对方自慰（H）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.MAKE_MASTUREBATE)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_HANDJOB)
def handle_last_cmd_handjob(character_id: int) -> int:
    """
    前一指令为手交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.HANDJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_PAIZURI)
def handle_last_cmd_paizuri(character_id: int) -> int:
    """
    前一指令为乳交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.PAIZURI)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_FOOTJOB)
def handle_last_cmd_footjob(character_id: int) -> int:
    """
    前一指令为足交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.FOOTJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_AXILLAJOB)
def handle_last_cmd_axillajob(character_id: int) -> int:
    """
    前一指令为腋交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.AXILLAJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_RUB_BUTTOCK)
def handle_last_cmd_rub_buttock(character_id: int) -> int:
    """
    前一指令为素股
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.RUB_BUTTOCK)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_HAND_BLOWJOB)
def handle_last_cmd_hand_blowjob(character_id: int) -> int:
    """
    前一指令为手交口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.HAND_BLOWJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_TITS_BLOWJOB)
def handle_last_cmd_tits_blowjob(character_id: int) -> int:
    """
    前一指令为乳交口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.TITS_BLOWJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_DEEP_THROAT)
def handle_last_cmd_deep_throat(character_id: int) -> int:
    """
    前一指令为深喉插入
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.DEEP_THROAT)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_FOCUS_BLOWJOB)
def handle_last_cmd_focus_blowjob(character_id: int) -> int:
    """
    前一指令为真空口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.FOCUS_BLOWJOB)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_NORMAL_SEX)
def handle_last_cmd_normal_sex(character_id: int) -> int:
    """
    前一指令为正常位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.NORMAL_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BACK_SEX)
def handle_last_cmd_back_sex(character_id: int) -> int:
    """
    前一指令为背后位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.BACK_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_RIDING_SEX)
def handle_last_cmd_riding_sex(character_id: int) -> int:
    """
    前一指令为骑乘位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.RIDING_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_FACE_SEAT_SEX)
def handle_last_cmd_face_seat_sex(character_id: int) -> int:
    """
    前一指令为对面座位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.FACE_SEAT_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BACK_SEAT_SEX)
def handle_last_cmd_back_seat_sex(character_id: int) -> int:
    """
    前一指令为背面座位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.BACK_SEAT_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_FACE_STAND_SEX)
def handle_last_cmd_face_stand_sex(character_id: int) -> int:
    """
    前一指令为对面立位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.FACE_STAND_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BACK_STAND_SEX)
def handle_last_cmd_back_stand_sex(character_id: int) -> int:
    """
    前一指令为背面立位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.BACK_STAND_SEX)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_STIMULATE_G_POINT)
def handle_last_cmd_stimulate_g_point(character_id: int) -> int:
    """
    前一指令为刺激G点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.STIMULATE_G_POINT)):
        return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_WOMB_OS_CARESS)
def handle_last_cmd_womb_os_caress(character_id: int) -> int:
    """
    前一指令为玩弄子宫口
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-2]
    if len_input and (last_cmd == str(constant.Instruct.WOMB_OS_CARESS)):
        return 1
    return 0



@add_premise(constant.Premise.LAST_CMD_BLOWJOB_OR_HANDJOB)
def handle_last_cmd_blowjob_or_handjob(character_id: int) -> int:
    """
    前一指令为口交或手交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.HANDJOB)):
            return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BLOWJOB_OR_PAIZURI)
def handle_last_cmd_blowjob_or_paizuri(character_id: int) -> int:
    """
    前一指令为口交或乳交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.PAIZURI)):
            return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_BLOWJOB_OR_CUNNILINGUS)
def handle_last_cmd_blowjob_or_cunnilingus(character_id: int) -> int:
    """
    前一指令为口交或舔阴_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.CUNNILINGUS)):
            return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_SEX)
def handle_last_cmd_sex(character_id: int) -> int:
    """
    前一指令为V性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    sex = {
        str(constant.Instruct.NORMAL_SEX),str(constant.Instruct.BACK_SEX),str(constant.Instruct.RIDING_SEX),
        str(constant.Instruct.FACE_SEAT_SEX),str(constant.Instruct.BACK_SEAT_SEX),
        str(constant.Instruct.FACE_STAND_SEX),str(constant.Instruct.BACK_STAND_SEX),
        str(constant.Instruct.STIMULATE_G_POINT),str(constant.Instruct.WOMB_OS_CARESS),str(constant.Instruct.WOMB_INSERTION)
        }
    if len_input:
        for cmd in sex:
            if last_cmd == cmd:
                return 1
    return 0


@add_premise(constant.Premise.LAST_CMD_A_SEX)
def handle_last_cmd_a_sex(character_id: int) -> int:
    """
    前一指令为A性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    sex = {
        str(constant.Instruct.NORMAL_ANAL_SEX),str(constant.Instruct.BACK_ANAL_SEX),str(constant.Instruct.RIDING_ANAL_SEX),
        str(constant.Instruct.FACE_SEAT_ANAL_SEX),str(constant.Instruct.BACK_SEAT_ANAL_SEX),
        str(constant.Instruct.FACE_STAND_ANAL_SEX),str(constant.Instruct.BACK_STAND_ANAL_SEX),
        str(constant.Instruct.STIMULATE_SIGMOID_COLON),str(constant.Instruct.STIMULATE_VAGINA)
        }
    if len_input:
        for cmd in sex:
            if last_cmd == cmd:
                return 1
    return 0

@add_premise(constant.Premise.LAST_CMD_U_SEX)
def handle_last_cmd_u_sex(character_id: int) -> int:
    """
    前一指令为U性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache)-1]
    sex = {
        str(constant.Instruct.URETHRAL_INSERTION)
        }
    if len_input:
        for cmd in sex:
            if last_cmd == cmd:
                return 1
    return 0


# 以下为道具系前提

@add_premise(constant.Premise.HAVE_CAMERA)
def handle_have_camera(character_id: int) -> int:
    """
    校验角色是否已持有相机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[50]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_VIDEO_RECORDER)
def handle_have_video_recorder(character_id: int) -> int:
    """
    校验角色是否已持有录像机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[51]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_NIPPLE_CLAMP)
def handle_have_nipple_clamp(character_id: int) -> int:
    """
    校验角色是否已持有乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[122]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_LOVE_EGG)
def handle_have_love_egg(character_id: int) -> int:
    """
    校验角色是否已持有跳蛋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[121]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_CLIT_CLAMP)
def handle_have_clit_clamp(character_id: int) -> int:
    """
    校验角色是否已持有阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[123]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_ELECTRIC_MESSAGE_STICK)
def handle_have_electric_message_stick(character_id: int) -> int:
    """
    校验角色是否已持有电动按摩棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[124]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_VIBRATOR_INSERTION)
def handle_have_vibrator_insertion(character_id: int) -> int:
    """
    校验角色是否已持有震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[125]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_MILKING_MACHINE)
def handle_have_milking_machine(character_id: int) -> int:
    """
    校验角色是否已持有搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[133]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_URINE_COLLECTOR)
def handle_have_urine_collector(character_id: int) -> int:
    """
    校验角色是否已持有采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[134]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BONDAGE)
def handle_have_bondage(character_id: int) -> int:
    """
    校验角色是否已持有绳子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[135]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_PATCH)
def handle_have_patch(character_id: int) -> int:
    """
    校验角色是否已持有眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[132]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BIG_VIBRATOR_INSERTION)
def handle_have_big_vibrator_insertion(character_id: int) -> int:
    """
    校验角色是否已持有加粗震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[126]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_HUGE_VIBRATOR_INSERTION)
def handle_have_huge_vibrator_insertion(character_id: int) -> int:
    """
    校验角色是否已持有巨型震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[127]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_CLYSTER_TOOLS)
def handle_have_clyster_tools(character_id: int) -> int:
    """
    校验角色是否已持有灌肠套装
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[128]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_ANAL_BEADS)
def handle_have_anal_beads(character_id: int) -> int:
    """
    校验角色是否已持有拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[129]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_ANAL_PLUG)
def handle_have_anal_plug(character_id: int) -> int:
    """
    校验角色是否已持有肛塞
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    # if character_data.item[130]:
        # return 1
    return 0


@add_premise(constant.Premise.HAVE_WHIP)
def handle_have_whip(character_id: int) -> int:
    """
    校验角色是否已持有鞭子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[131]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_NEEDLE)
def handle_have_needle(character_id: int) -> int:
    """
    校验角色是否已持有针
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[137]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_COLLAR)
def handle_have_collar(character_id: int) -> int:
    """
    校验角色是否已持有项圈
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[138]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_CONDOM)
def handle_have_condom(character_id: int) -> int:
    """
    校验角色是否已持有避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[120]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SAFE_CANDLES)
def handle_have_safe_candles(character_id: int) -> int:
    """
    校验角色是否已持有低温蜡烛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[136]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_COTTON_STICK)
def handle_have_cotton_stick(character_id: int) -> int:
    """
    校验角色是否已持有无菌棉签
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[139]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BIRTH_CONTROL_PILLS_BEFORE)
def handle_have_birth_control_pills_before(character_id: int) -> int:
    """
    校验角色是否已持有事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[101]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BIRTH_CONTROL_PILLS_AFTER)
def handle_have_birth_control_pills_after(character_id: int) -> int:
    """
    校验角色是否已持有事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[102]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BODY_LUBRICANT)
def handle_have_body_lubricant(character_id: int) -> int:
    """
    校验角色是否已持有润滑液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[100]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_PHILTER)
def handle_have_philter(character_id: int) -> int:
    """
    校验角色是否已持有媚药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[103]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_ENEMAS)
def handle_have_enemas(character_id: int) -> int:
    """
    校验角色是否已持有灌肠液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[104]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_DIURETICS)
def handle_have_diuretics(character_id: int) -> int:
    """
    校验角色是否已持有利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[105]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SLEEPING_PILLS)
def handle_have_sleeping_pills(character_id: int) -> int:
    """
    校验角色是否已持有睡眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[106]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_CLOMID)
def handle_have_clomid(character_id: int) -> int:
    """
    校验角色是否已持有排卵促进药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[107]:
        return 1
    return 0

@add_premise(constant.Premise.A_SHIT)
def handle_a_shit(character_id: int) -> int:
    """
    校验角色是否肠内脏污
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1,3]:
        return 1
    return 0

@add_premise(constant.Premise.ENEMA)
def handle_enema(character_id: int) -> int:
    """
    校验角色是否正在灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1,3]:
        return 1
    return 0


@add_premise(constant.Premise.NOT_ENEMA)
def handle_not_enema(character_id: int) -> int:
    """
    校验角色是否非灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean not in [1,3]:
        return 1
    return 0

@add_premise(constant.Premise.ENEMA_END)
def handle_enema_end(character_id: int) -> int:
    """
    校验角色是否已灌肠（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [2,4]:
        return 1
    return 0

@add_premise(constant.Premise.NORMAL_ENEMA)
def handle_normal_enema(character_id: int) -> int:
    """
    校验角色是否普通灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1]:
        return 1
    return 0

@add_premise(constant.Premise.SEMEN_ENEMA)
def handle_semen_enema(character_id: int) -> int:
    """
    校验角色是否精液灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [3]:
        return 1
    return 0

@add_premise(constant.Premise.NORMAL_ENEMA_END)
def handle_normal_enema_end(character_id: int) -> int:
    """
    校验角色是否已普通灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [2]:
        return 1
    return 0

@add_premise(constant.Premise.SEMEN_ENEMA_END)
def handle_semen_enema_end(character_id: int) -> int:
    """
    校验角色是否已精液灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [4]:
        return 1
    return 0


# @add_premise(constant.Premise.IS_ENTHUSIASM)
# def handle_is_enthusiasm(character_id: int) -> int:
#     """
#     校验角色是否是一个热情的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[15] >= 50


@add_premise(constant.Premise.TARGET_ADMIRE)
def handle_target_admire(character_id: int) -> int:
    """
    校验角色是否被交互对象恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.social_contact.setdefault(4, set())
    if character_id in target_data.social_contact[4]:
        return 1
    return 0


# @add_premise(constant.Premise.TARGET_AVERAGE_STATURE_HEIGHT)
# def handle_target_average_stature_height(character_id: int) -> int:
#     """
#     校验角色目体型高是否比平均体型更胖
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data = cache.character_data[character_id]
#     target_data = cache.character_data[character_data.target_character_id]
#     age_tem = attr_calculation.judge_age_group(target_data.age)
#     if age_tem in cache.average_bodyfat_by_age:
#         average_bodyfat = cache.average_bodyfat_by_age[age_tem][target_data.sex]
#         if target_data.bodyfat > average_bodyfat * 1.05:
#             return 1
#     return 0


@add_premise(constant.Premise.NO_FIRST_KISS)
def handle_no_first_kiss(character_id: int) -> int:
    """
    校验是否初吻还在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[4] == 1


@add_premise(constant.Premise.IS_TARGET_FIRST_KISS)
def handle_is_target_first_kiss(character_id: int) -> int:
    """
    校验是否是交互对象的初吻对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return character_id == target_data.first_kiss_id


@add_premise(constant.Premise.HAVE_OTHER_TARGET_IN_SCENE)
def handle_have_other_target_in_scene(character_id: int) -> int:
    """
    校验场景中是否有自己和交互对象以外的其他人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    return len(scene_data.character_list) > 2


@add_premise(constant.Premise.NO_HAVE_OTHER_TARGET_IN_SCENE)
def handle_no_have_other_target_in_scene(character_id: int) -> int:
    """
    校验场景中是否没有自己和交互对象以外的其他人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    return len(scene_data.character_list) <= 2



@add_premise(constant.Premise.HAVE_FIRST_KISS)
def handle_have_first_kiss(character_id: int) -> int:
    """
    校验是否初吻不在了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.first_kiss != -1


@add_premise(constant.Premise.HAVE_LIKE_TARGET)
def handle_have_like_target(character_id: int) -> int:
    """
    校验是否有喜欢的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.social_contact.setdefault(4, set())
    character_data.social_contact.setdefault(5, set())
    return len(character_data.social_contact[4]) + len(character_data.social_contact[5])


@add_premise(constant.Premise.HAVE_LIKE_TARGET_IN_SCENE)
def handle_have_like_target_in_scene(character_id: int) -> int:
    """
    校验是否有喜欢的人在场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.social_contact.setdefault(4, set())
    character_data.social_contact.setdefault(5, set())
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    character_list = []
    for i in {4, 5}:
        for c in character_data.social_contact[i]:
            if c in scene_data.character_list:
                character_list.append(c)
    return len(character_list)


@add_premise(constant.Premise.TARGET_IS_STUDENT)
def handle_target_is_student(character_id: int) -> int:
    """
    校验交互对象是否是学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.age <= 18


# @add_premise(constant.Premise.TARGET_IS_ASTUTE)
# def handle_target_is_astute(character_id: int) -> int:
#     """
#     校验交互对象是否是一个机敏的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[11] >= 50


# @add_premise(constant.Premise.TARGET_IS_INFERIORITY)
# def handle_target_is_inferiority(character_id: int) -> int:
#     """
#     校验交互对象是否是一个自卑的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[16] < 50


# @add_premise(constant.Premise.TARGET_IS_ENTHUSIASM)
# def handle_target_is_enthusiasm(character_id: int) -> int:
#     """
#     校验交互对象是否是一个热情的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[15] >= 50


# @add_premise(constant.Premise.TARGET_IS_SELF_CONFIDENCE)
# def handle_target_is_self_confidence(character_id: int) -> int:
#     """
#     校验交互对象是否是一个自信的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[16] >= 50


# @add_premise(constant.Premise.IS_ASTUTE)
# def handle_is_astute(character_id: int) -> int:
#     """
#     校验是否是一个机敏的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[11] >= 50


# @add_premise(constant.Premise.TARGET_IS_HEAVY_FEELING)
# def handle_target_is_heavy_feeling(character_id: int) -> int:
#     """
#     校验交互对象是否是一个重情的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[5] >= 50


@add_premise(constant.Premise.TARGET_NO_FIRST_HAND_IN_HAND)
def handle_target_no_first_hand_in_hand(character_id: int) -> int:
    """
    校验交互对象是否没有牵过手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.first_hand_in_hand == -1


@add_premise(constant.Premise.NO_FIRST_HAND_IN_HAND)
def handle_no_first_hand_in_hand(character_id: int) -> int:
    """
    校验是否没有牵过手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.first_hand_in_hand == -1


# @add_premise(constant.Premise.IS_HEAVY_FEELING)
# def handle_is_heavy_feeling(character_id: int) -> int:
#     """
#     校验是否是一个重情的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[5] >= 50


@add_premise(constant.Premise.HAVE_LIKE_TARGET_NO_FIRST_KISS)
def handle_have_like_target_no_first_kiss(character_id: int) -> int:
    """
    校验是否有自己喜欢的人的初吻还在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_index = 0
    for i in {4, 5}:
        character_data.social_contact.setdefault(i, set())
        for c in character_data.social_contact[i]:
            c_data: game_type.Character = cache.character_data[c]
            if c_data.first_kiss == -1:
                character_index += 1
    return character_index


# @add_premise(constant.Premise.TARGET_IS_APATHY)
# def handle_target_is_apathy(character_id: int) -> int:
#     """
#     校验交互对象是否是一个冷漠的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     return target_data.nature[15] < 50


@add_premise(constant.Premise.TARGET_UNARMED_COMBAT_IS_HIGHT)
def handle_target_unarmed_combat_is_hight(character_id: int) -> int:
    """
    校验交互对象徒手格斗技能是否比自己高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    character_data.knowledge.setdefault(32, 0)
    target_data.knowledge.setdefault(32, 0)
    character_level = attr_calculation.get_experience_level_weight(character_data.knowledge[32])
    target_level = attr_calculation.get_experience_level_weight(target_data.knowledge[32])
    if target_level > character_level:
        return target_level - character_level
    return 0


@add_premise(constant.Premise.TARGET_DISGUST_IS_HIGHT)
def handle_target_disgust_is_hight(character_id: int) -> int:
    """
    校验交互对象是否反感情绪高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.status_data.setdefault(12, 0)
    return target_data.status_data[12]


@add_premise(constant.Premise.TARGET_LUST_IS_HIGHT)
def handle_target_lust_is_hight(character_id: int) -> int:
    """
    校验交互对象是否色欲高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.status_data.setdefault(21, 0)
    return target_data.status_data[21]


@add_premise(constant.Premise.TARGET_IS_WOMAN)
def handle_target_is_woman(character_id: int) -> int:
    """
    校验交互对象是否是女性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.sex == 1


# @add_premise(constant.Premise.TARGET_IS_NAKED)
# def handle_target_is_naked(character_id: int) -> int:
#     """
#     校验交互对象是否一丝不挂
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     for i in target_data.put_on:
#         if isinstance(target_data.put_on[i], UUID):
#             return 0
#     return 1


@add_premise(constant.Premise.TARGET_CLITORIS_LEVEL_IS_HIGHT)
def handle_target_clitoris_is_hight(character_id: int) -> int:
    """
    校验交互对象是否阴蒂开发度高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.sex_experience.setdefault(2, 0)
    return attr_calculation.get_experience_level_weight(target_data.sex_experience[2])


@add_premise(constant.Premise.TARGET_IS_MAN)
def handle_target_is_man(character_id: int) -> int:
    """
    校验交互对象是否是男性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.sex


@add_premise(constant.Premise.SEX_EXPERIENCE_IS_HIGHT)
def handle_sex_experience_is_hight(character_id: int) -> int:
    """
    校验角色是否性技熟练
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.knowledge.setdefault(9, 0)
    return attr_calculation.get_experience_level_weight(character_data.knowledge[9])


@add_premise(constant.Premise.IS_COLLECTION_SYSTEM)
def handle_is_collection_system(character_id: int) -> int:
    """
    校验玩家是否已启用收藏模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.is_collection


@add_premise(constant.Premise.UN_COLLECTION_SYSTEM)
def handle_un_collection_system(character_id: int) -> int:
    """
    校验玩家是否未启用收藏模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not cache.is_collection


@add_premise(constant.Premise.IS_H)
def handle_is_h(character_id: int) -> int:
    """
    玩家已启用H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.is_h


@add_premise(constant.Premise.NOT_H)
def handle_not_h(character_id: int) -> int:
    """
    玩家未启用H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    return not target_data.is_h


@add_premise(constant.Premise.IS_FOLLOW)
def handle_is_follow(character_id: int) -> int:
    """
    校验交互对象是否正跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.is_follow


@add_premise(constant.Premise.NOT_FOLLOW)
def handle_not_follow(character_id: int) -> int:
    """
    校验交互对象是否没有跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.is_follow


@add_premise(constant.Premise.TARGET_IS_COLLECTION)
def handle_target_is_collection(character_id: int) -> int:
    """
    校验交互对象是否已被玩家收藏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    return character_data.target_character_id in player_data.collection_character


@add_premise(constant.Premise.TARGET_IS_NOT_COLLECTION)
def handle_target_is_not_collection(character_id: int) -> int:
    """
    校验交互对象是否未被玩家收藏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    return character_data.target_character_id not in player_data.collection_character


@add_premise(constant.Premise.TARGET_IS_LIVE)
def handle_target_is_live(character_id: int) -> int:
    """
    校验交互对象是否未死亡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.dead


@add_premise(constant.Premise.THIRSTY)
def handle_thirsty(character_id: int) -> int:
    """
    校验角色是否处于口渴状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status_data.setdefault(28, 0)
    return math.floor(character_data.status_data[28]) * 10


@add_premise(constant.Premise.HAVE_DRINKS)
def handle_have_drinks(character_id: int) -> int:
    """
    校验角色背包中是否有饮料
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    drinks_list = []
    for food_id in character_data.food_bag:
        now_food: game_type.Food = character_data.food_bag[food_id]
        if now_food.eat and 28 in now_food.feel:
            drinks_list.append(food_id)
    return len(drinks_list)


@add_premise(constant.Premise.NO_HAVE_DRINKS)
def handle_no_have_drinks(character_id: int) -> int:
    """
    校验角色背包中是否没有饮料
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for food_id in character_data.food_bag:
        now_food: game_type.Food = character_data.food_bag[food_id]
        if now_food.eat and 28 in now_food.feel:
            return 0
    return 1


@add_premise(constant.Premise.ATTEND_CLASS_TODAY)
def handle_attend_class_today(character_id: int) -> int:
    """
    校验角色今日是否需要上课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return game_time.judge_attend_class_today(character_id)


# @add_premise(constant.Premise.APPROACHING_CLASS_TIME)
# def handle_approaching_class_time(character_id: int) -> int:
#     """
#     校验角色是否临近上课时间
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     now_time: datetime.datetime = character_data.behavior.start_time
#     now_time_value = now_time.hour * 100 + now_time.minute
#     next_time = 0
#     if character_data.age <= 18:
#         school_id = 0
#         if character_data.age in range(13, 16):
#             school_id = 1
#         elif character_data.age in range(16, 19):
#             school_id = 2
#         for session_id in game_config.config_school_session_data[school_id]:
#             session_config = game_config.config_school_session[session_id]
#             if session_config.start_time > now_time_value:
#                 if next_time == 0 or session_config.start_time < next_time:
#                     next_time = session_config.start_time
#         if next_time == 0:
#             return 0
#     if character_id in cache.teacher_school_timetable:
#         now_week = now_time.weekday()
#         timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[character_id]
#         for timetable in timetable_list:
#             if timetable.week_day != now_week:
#                 continue
#             if timetable.time > now_time_value:
#                 if next_time == 0 or timetable.time < next_time:
#                     next_time = timetable.time
#         if next_time == 0:
#             return 0
#     next_value = int(next_time / 100) * 60 + next_time % 100
#     now_value = int(now_time_value / 100) * 60 + now_time_value % 100
#     add_time = next_value - now_value
#     if add_time > 30:
#         return 0
#     return 3000 / (add_time * 10)


# @add_premise(constant.Premise.IN_CLASS_TIME)
# def handle_in_class_time(character_id: int) -> int:
#     """
#     校验角色是否处于上课时间
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     return character.judge_character_in_class_time(character_id) * 500


@add_premise(constant.Premise.NO_IN_CLASSROOM)
def handle_no_in_classroom(character_id: int) -> int:
    """
    校验角色是否不在所属教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    # if now_scene_str != character_data.classroom:
    #     return 1
    return 0


# @add_premise(constant.Premise.TEACHER_NO_IN_CLASSROOM)
# def handle_teacher_no_in_classroom(character_id: int) -> int:
#     """
#     校验角色所属班级的老师是否不在教室中
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     if not game_time.judge_attend_class_today(character_id):
#         return 1
#     character_data: game_type.Character = cache.character_data[character_id]
#     # if character_data.classroom == "":
#     #     return 1
#     # classroom: game_type.Scene = cache.scene_data[character_data.classroom]
#     now_time: datetime.datetime = character_data.behavior.start_time
#     if now_time is None:
#         now_time = cache.game_time
#     now_week = now_time.weekday()
#     school_id, phase = course.get_character_school_phase(character_id)
#     now_time_value = now_time.hour * 100 + now_time.minute
#     if now_week in cache.course_time_table_data[school_id][phase]:
#         now_course_index = 0
#         next_time = 0
#         for session_config_id in game_config.config_school_session_data[school_id]:
#             session_config = game_config.config_school_session[session_config_id]
#             if not next_time:
#                 if session_config.start_time >= now_time_value:
#                     next_time = session_config.start_time
#                     now_course_index = session_config.session
#                 elif session_config.end_time >= now_time_value:
#                     next_time = session_config.end_time
#                     now_course_index = session_config.session
#                 continue
#             if session_config.start_time >= now_time_value and session_config.start_time < next_time:
#                 next_time = session_config.start_time
#                 now_course_index = session_config.session
#             elif session_config.end_time >= now_time_value and session_config.end_time < next_time:
#                 next_time = session_config.start_time
#                 now_course_index = session_config.session
#         if school_id not in cache.class_timetable_teacher_data:
#             return 1
#         if phase not in cache.class_timetable_teacher_data[school_id]:
#             return 1
        # if character_data.classroom not in cache.class_timetable_teacher_data[school_id][phase]:
        #     return 1
        # if now_week not in cache.class_timetable_teacher_data[school_id][phase][character_data.classroom]:
        #     return 1
        # if (
        #     now_course_index
        #     not in cache.class_timetable_teacher_data[school_id][phase][character_data.classroom][now_week]
        # ):
        #     return 1
        # now_teacher = cache.class_timetable_teacher_data[school_id][phase][character_data.classroom][
        #     now_week
        # ][now_course_index]
        # if now_teacher not in classroom.character_list:
        #     return 1
    #     return 0
    # return 1


# @add_premise(constant.Premise.TEACHER_IN_CLASSROOM)
# def handle_teacher_in_classroom(character_id: int) -> int:
#     """
#     校验角色所属班级的老师是否在教室中
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     return not handle_teacher_no_in_classroom(character_id)


# @add_premise(constant.Premise.IS_NAKED)
# def handle_is_naked(character_id: int) -> int:
#     """
#     校验角色是否一丝不挂
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     for i in character_data.put_on:
#         if isinstance(character_data.put_on[i], UUID):
#             return 0
#     return 1


@add_premise(constant.Premise.IS_BEYOND_FRIENDSHIP_TARGET_IN_SCENE)
def handle_is_beyond_friendship_target_in_scene(character_id: int) -> int:
    """
    校验场景中是否有角色对自己抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    now_weight = 0
    for now_character in scene_data.character_list:
        if now_character == character_id:
            continue
        now_character_data: game_type.Character = cache.character_data[now_character]
        if (
            character_id in now_character_data.social_contact_data
            and now_character_data.social_contact_data[character_id] > 2
        ):
            now_weight += now_character_data.social_contact_data[character_id]
    return now_weight


@add_premise(constant.Premise.HAVE_STUDENTS_IN_CLASSROOM)
def handle_have_students_in_classroom(character_id: int) -> int:
    """
    校验是否有所教班级的学生在教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.age <= 18:
        return 0
    if character_id not in cache.teacher_school_timetable:
        return 0
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    now_week = now_time.weekday()
    now_time = 0
    now_classroom = []
    timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[character_id]
    now_time_value = now_time.hour * 100 + now_time.minute
    for timetable in timetable_list:
        if timetable.week_day != now_week:
            continue
        if now_time == 0:
            if timetable.time >= now_time_value:
                now_time = timetable.time
                now_classroom = timetable.class_room
            elif timetable.end_time >= now_time_value:
                now_time = timetable.end_time
                now_classroom = timetable.class_room
                break
            continue
        if timetable.time >= now_time_value and timetable.time < now_time:
            now_time = timetable.time
            now_classroom = timetable.class_room
            continue
        elif timetable.end_time >= now_time_value and timetable.end_time < now_time:
            now_time = timetable.end_time
            now_classroom = timetable.class_room
    now_room_path_str = map_handle.get_map_system_path_str_for_list(now_classroom)
    now_scene_data: game_type.Scene = cache.scene_data[now_room_path_str]
    class_data = cache.classroom_students_data[now_room_path_str]
    return len(class_data & now_scene_data.character_list)


# @add_premise(constant.Premise.GOOD_AT_ELOQUENCE)
# def handle_good_at_eloquence(character_id: int) -> int:
#     """
#     校验角色是否擅长口才
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[12]
#     if 12 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[12])
#         return weight * level
#     return weight


# @add_premise(constant.Premise.GOOD_AT_LITERATURE)
# def handle_good_at_literature(character_id: int) -> int:
#     """
#     校验角色是否擅长文学
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[2]
#     if 2 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[2])
#         return weight * level
#     return weight


# @add_premise(constant.Premise.GOOD_AT_WRITING)
# def handle_good_at_writing(character_id: int) -> int:
#     """
#     校验角色是否擅长写作
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[28]
#     if 28 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[28])
#         return weight * level
#     return weight


# @add_premise(constant.Premise.GOOD_AT_DRAW)
# def handle_good_at_draw(character_id: int) -> int:
#     """
#     校验角色是否擅长绘画
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[13]
#     if 13 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[13])
#         return weight * level
#     return weight


# @add_premise(constant.Premise.GOOD_AT_ART)
# def handle_good_at_art(character_id: int) -> int:
#     """
#     校验角色是否擅长艺术
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 1 + character_data.knowledge_interest[5]
#     if 5 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[5])
#         return weight * level
#     return weight


# @add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_RELIGION)
# def handle_target_little_knowledge_of_religion(character_id: int) -> int:
#     """
#     校验交互对象是否对宗教一知半解
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if 7 in target_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(target_data.knowledge[7])
#         if level <= 2:
#             return 1
#     return 0


# @add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_FAITH)
# def handle_target_little_knowledge_of_faith(character_id: int) -> int:
#     """
#     校验交互对象是否对信仰一知半解
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if 8 in target_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(target_data.knowledge[8])
#         if level <= 2:
#             return 1
#     return 0


# @add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_ASTRONOMY)
# def handle_target_little_knowledge_of_astronomy(character_id: int) -> int:
#     """
#     校验交互对象是否对天文学一知半解
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if 53 in target_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(target_data.knowledge[53])
#         if level <= 2:
#             return 1
#     return 0


# @add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_ASTROLOGY)
# def handle_target_little_knowledge_of_astrology(character_id: int) -> int:
#     """
#     校验交互对象是否对占星学一知半解
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if 75 in target_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(target_data.knowledge[75])
#         if level <= 2:
#             return 1
#     return 0


# @add_premise(constant.Premise.RICH_EXPERIENCE_IN_SEX)
# def handle_rich_experience_in_sex(character_id: int) -> int:
#     """
#     校验角色是否性经验丰富
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     now_exp = 0
#     for i in character_data.sex_experience:
#         now_exp += character_data.sex_experience[i]
#     now_level = attr_calculation.get_experience_level_weight(now_exp)
#     if now_level > 4:
#         return now_level - 4
#     return 0


@add_premise(constant.Premise.TARGET_IS_SLEEP)
def handle_target_is_sleep(character_id: int) -> int:
    """
    校验交互对象是否正在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.state == constant.CharacterStatus.STATUS_SLEEP


@add_premise(constant.Premise.IN_ROOFTOP_SCENE)
def handle_in_rooftop_scene(character_id: int) -> int:
    """
    校验是否处于天台场景
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Rooftop":
        return 1
    return 0


@add_premise(constant.Premise.TONIGHT_IS_FULL_MOON)
def handle_tonight_is_full_moon(character_id: int) -> int:
    """
    校验今夜是否是满月
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    moon_phase = game_time.get_moon_phase(now_time)
    if moon_phase in {11, 12}:
        return 1
    return 0


# @add_premise(constant.Premise.IS_STARAIGHTFORWARD)
# def handle_is_staraightforward(character_id: int) -> int:
#     """
#     校验角色是否是一个爽直的人
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     return character_data.nature[13] >= 50


# @add_premise(constant.Premise.NO_GOOD_AT_ELOQUENCE)
# def handle_no_good_at_eloquence(character_id: int) -> int:
#     """
#     校验角色是否不擅长口才
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     weight = 8
#     if 12 in character_data.knowledge:
#         level = attr_calculation.get_experience_level_weight(character_data.knowledge[12])
#         return 8 - level
#     return weight


@add_premise(constant.Premise.TARGET_NO_EXPERIENCE_IN_SEX)
def handle_target_no_experience_in_sex(character_id: int) -> int:
    """
    校验交互对象是否没有性经验
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for i in character_data.sex_experience:
        if character_data.sex_experience[i]:
            return 0
    return 1


@add_premise(constant.Premise.LUST_IS_HIGHT)
def handle_lust_is_hight(character_id: int) -> int:
    """
    校验角色是否色欲高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status_data.setdefault(21, 0)
    return character_data.status_data[21]


@add_premise(constant.Premise.IN_GROVE)
def handle_in_grove(character_id: int) -> int:
    """
    校验角色是否处于加工站入口中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] == "7":
        return 1
    return 0


@add_premise(constant.Premise.NO_IN_GROVE)
def handle_no_in_grove(character_id: int) -> int:
    """
    校验角色是否未处于加工站入口中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] != "7":
        return 1
    return 0


# @add_premise(constant.Premise.NAKED_CHARACTER_IN_SCENE)
# def handle_naked_character_in_scene(character_id: int) -> int:
#     """
#     校验场景中是否有人一丝不挂
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     scene_path = map_handle.get_map_system_path_str_for_list(character_data.position)
#     scene_data: game_type.Scene = cache.scene_data[scene_path]
#     for now_character in scene_data.character_list:
#         if handle_is_naked(now_character):
#             return 1
#     return 0


@add_premise(constant.Premise.TARGET_IS_SING)
def handle_target_is_sing(character_id: int) -> int:
    """
    校验交互对象是否正在唱歌
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_id = character_data.target_character_id
    if target_id != character_id:
        target_data: game_type.Character = cache.character_data[target_id]
        return target_data.state == constant.CharacterStatus.STATUS_SINGING
    return 0


@add_premise(constant.Premise.NO_HAVE_GUITAR)
def handle_no_have_guitar(character_id: int) -> int:
    """
    校验角色是否未拥有吉他
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return 4 not in character_data.item


@add_premise(constant.Premise.IN_ITEM_SHOP)
def handle_in_item_shop(character_id: int) -> int:
    """
    校验角色是否在训练场入口中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position == ["11"]


@add_premise(constant.Premise.NO_IN_ITEM_SHOP)
def handle_no_in_item_shop(character_id: int) -> int:
    """
    校验角色是否不在训练场入口中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position != ["11"]
