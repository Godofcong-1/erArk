from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


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


@add_premise(constant_promise.Premise.HP_1)
def handle_hp_1(character_id: int) -> int:
    """
    自身疲劳（体力=1）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.tired == 1:
        return 999
    else:
        return 0


@add_premise(constant_promise.Premise.HP_G_1)
def handle_hp_g_1(character_id: int) -> int:
    """
    自身未疲劳（体力>1）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.tired == 1:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.SELF_OR_TARGET_HP_1)
def handle_self_or_target_hp_1(character_id: int) -> int:
    """
    自身或交互对象疲劳（体力=1）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.sp_flag.tired == 1:
        return 1
    elif target_data.sp_flag.tired == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SELF_AND_TARGET_HP_G_1)
def handle_self_and_target_hp_g_1(character_id: int) -> int:
    """
    自身和交互对象均未疲劳（体力>1）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_or_target_hp_1(character_id):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.SHOWER_FLAG_0)
def handle_shower_flag_0(character_id: int) -> int:
    """
    自身没有洗澡状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SHOWER_FLAG_GE_1)
def handle_shower_flag_ge_1(character_id: int) -> int:
    """
    自身有某一种洗澡状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SHOWER_FLAG_123)
def handle_shower_flag_123(character_id: int) -> int:
    """
    自身有正在进行的洗澡状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower in {1,2,3}:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SHOWER_FLAG_1)
def handle_shower_flag_1(character_id: int) -> int:
    """
    自身要脱衣服（洗澡）状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.SHOWER_FLAG_2)
def handle_shower_flag_2(character_id: int) -> int:
    """
    自身要洗澡状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower == 2:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.SHOWER_FLAG_3)
def handle_shower_flag_3(character_id: int) -> int:
    """
    自身要披浴巾状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower == 3:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.SHOWER_FLAG_4)
def handle_shower_flag_4(character_id: int) -> int:
    """
    自身已洗澡状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.shower == 4:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.EAT_FOOD_FLAG_GE_1)
def handle_eat_food_flag_ge_1(character_id: int) -> int:
    """
    自身有某一种吃饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.eat_food >= 1:
        return 1
    elif character_data.sp_flag.help_buy_food >= 1:
        return 1
    elif character_data.sp_flag.help_make_food >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.EAT_FOOD_FLAG_1)
def handle_eat_food_flag_1(character_id: int) -> int:
    """
    自身要取餐状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.eat_food == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.EAT_FOOD_FLAG_2)
def handle_eat_food_flag_2(character_id: int) -> int:
    """
    自身要进食状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.eat_food == 2:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_FLAG_0)
def handle_sleep_flag_0(character_id: int) -> int:
    """
    自身无要睡觉状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.sleep == 0:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_FLAG_1)
def handle_sleep_flag_1(character_id: int) -> int:
    """
    自身要睡觉状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.sleep == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.REST_FLAG_1)
def handle_rest_flag_1(character_id: int) -> int:
    """
    自身要休息状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.rest == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.PEE_FLAG_1)
def handle_pee_flag_1(character_id: int) -> int:
    """
    自身要撒尿状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.pee == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_FLAG_1)
def handle_milk_flag_1(character_id: int) -> int:
    """
    自身要挤奶状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.milk == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.SWIM_FLAG_0)
def handle_swim_flag_0(character_id: int) -> int:
    """
    自身没有游泳状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.swim == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SWIM_FLAG_1)
def handle_swim_flag_1(character_id: int) -> int:
    """
    自身要换泳衣状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.swim == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SWIM_FLAG_2)
def handle_swim_flag_2(character_id: int) -> int:
    """
    自身要游泳状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.swim == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.BATHHOUSE_ENTERTAINMENT_FLAG_0)
def handle_bathhouse_entertainment_flag_0(character_id: int) -> int:
    """
    自身没有大浴场娱乐状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.bathhouse_entertainment == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.BATHHOUSE_ENTERTAINMENT_FLAG_1)
def handle_bathhouse_entertainment_flag_1(character_id: int) -> int:
    """
    自身大浴场娱乐_要更衣状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.bathhouse_entertainment == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.BATHHOUSE_ENTERTAINMENT_FLAG_2)
def handle_bathhouse_entertainment_flag_2(character_id: int) -> int:
    """
    自身大浴场娱乐_要娱乐状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.bathhouse_entertainment == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.WORK_MAINTENANCE_FLAG_0)
def handle_work_maintenance_flag_0(character_id: int) -> int:
    """
    自身没有要检修状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.work_maintenance == 1:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.WORK_MAINTENANCE_FLAG_1)
def handle_work_maintenance_flag_1(character_id: int) -> int:
    """
    自身要检修状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.work_maintenance == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.FIELD_COMMISSION_0)
def handle_field_commission_0(character_id: int) -> int:
    """
    自身没有在出外勤委托
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sp_flag.field_commission == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.FIELD_COMMISSION_1)
def handle_field_commission_1(character_id: int) -> int:
    """
    自身正在出外勤委托
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_field_commission_0(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_DIPLOMATIC_VISIT_0)
def handle_in_diplomatic_visit_0(character_id: int) -> int:
    """
    自身没有在外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sp_flag.in_diplomatic_visit == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_DIPLOMATIC_VISIT_1)
def handle_in_diplomatic_visit_1(character_id: int) -> int:
    """
    自身正在外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_diplomatic_visit_0(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_DIPLOMATIC_VISIT_1_AND_OTHER_COUNTRY)
def handle_in_diplomatic_visit_1_and_other_country(character_id: int) -> int:
    """
    自身正在外交访问且对方是非当前所在国家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_diplomatic_visit_1(character_id):
        target_coutry_cid = cache.character_data[character_id].sp_flag.in_diplomatic_visit
        if target_coutry_cid != cache.rhodes_island.current_location[0]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_VISITOR_FLAG_1)
def handle_self_visitor_flag_1(character_id: int) -> int:
    """
    自身是访问中的访客
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.sp_flag.vistor == 1


@add_premise(constant_promise.Premise.TARGET_VISITOR_FLAG_1)
def handle_target_visitor_flag_1(character_id: int) -> int:
    """
    交互对象是访问中的访客
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_visitor_flag_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_VISITOR_FLAG_1)
def handle_target_not_visitor_flag_1(character_id: int) -> int:
    """
    交互对象不是访问中的访客
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_self_visitor_flag_1(character_data.target_character_id)



@add_premise(constant_promise.Premise.IS_FOLLOW)
def handle_is_follow(character_id: int) -> int:
    """
    校验正在跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_follow:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_FOLLOW)
def handle_not_follow(character_id: int) -> int:
    """
    校验是否没有跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_is_follow(character_id)


@add_premise(constant_promise.Premise.IS_FOLLOW_1)
def handle_is_follow_1(character_id: int) -> int:
    """
    校验是否正智能跟随玩家(权重20)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_follow == 1:
        return 20
    return 0


@add_premise(constant_promise.Premise.NOT_FOLLOW_1)
def handle_not_follow_1(character_id: int) -> int:
    """
    校验是否没有智能跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not character_data.sp_flag.is_follow == 1


@add_premise(constant_promise.Premise.IS_FOLLOW_3)
def handle_is_follow_3(character_id: int) -> int:
    """
    校验是否当前正前往博士办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_follow == 3:
        return 100
    return 0


@add_premise(constant_promise.Premise.IS_FOLLOW_4)
def handle_is_follow_4(character_id: int) -> int:
    """
    校验是否当前正前往博士所在位置
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_follow == 4:
        return 100
    return 0


@add_premise(constant_promise.Premise.TARGET_IS_FOLLOW)
def handle_target_is_follow(character_id: int) -> int:
    """
    校验交互对象是否正跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.sp_flag.is_follow


@add_premise(constant_promise.Premise.TARGET_NOT_FOLLOW)
def handle_target_not_follow(character_id: int) -> int:
    """
    校验交互对象是否没有跟随玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.sp_flag.is_follow


@add_premise(constant_promise.Premise.HELP_BUY_FOOD_FLAG_0)
def handle_help_buy_food_flag_0(character_id: int) -> int:
    """
    自身没有帮忙买午饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_buy_food == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HELP_BUY_FOOD_FLAG_1)
def handle_help_buy_food_flag_1(character_id: int) -> int:
    """
    自身要买饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_buy_food == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HELP_BUY_FOOD_FLAG_2)
def handle_help_buy_food_flag_2(character_id: int) -> int:
    """
    自身要买第二份饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_buy_food == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HELP_BUY_FOOD_FLAG_3)
def handle_help_buy_food_flag_3(character_id: int) -> int:
    """
    自身买饭后要送饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_buy_food == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HELP_MAKE_FOOD_FLAG_0)
def handle_help_make_food_flag_0(character_id: int) -> int:
    """
    自身没有帮忙做饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_make_food == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HELP_MAKE_FOOD_FLAG_1)
def handle_help_make_food_flag_1(character_id: int) -> int:
    """
    自身要做饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_make_food == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HELP_MAKE_FOOD_FLAG_2)
def handle_help_make_food_flag_2(character_id: int) -> int:
    """
    自身做饭后要送饭状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.help_make_food == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MORIING_SALUTATION_FLAG_0)
def handle_morning_salutation_flag_0(character_id: int) -> int:
    """
    自身没有早安问候状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.morning_salutation == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MORIING_SALUTATION_FLAG_1)
def handle_morning_salutation_flag_1(character_id: int) -> int:
    """
    自身要早安问候状态（权重100）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_morning_salutation_time
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.morning_salutation == 1:
        weight = handle_morning_salutation_time(character_id)
        return 100 + weight
    else:
        return 0


@add_premise(constant_promise.Premise.MORIING_SALUTATION_FLAG_2)
def handle_morning_salutation_flag_2(character_id: int) -> int:
    """
    自身已早安问候状态（权重100）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.morning_salutation == 2:
        return 100
    else:
        return 0


@add_premise(constant_promise.Premise.NIGHT_SALUTATION_FLAG_0)
def handle_night_salutation_flag_0(character_id: int) -> int:
    """
    自身没有晚安问候状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.night_salutation == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NIGHT_SALUTATION_FLAG_1)
def handle_night_salutation_flag_1(character_id: int) -> int:
    """
    自身要晚安问候状态（权重100）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.night_salutation == 1:
        return 100
    else:
        return 0


@add_premise(constant_promise.Premise.NIGHT_SALUTATION_FLAG_2)
def handle_night_salutation_flag_2(character_id: int) -> int:
    """
    自身已晚安问候状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.night_salutation == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.IN_ASSISTANT_AI_LINK)
def handle_assistant_salutation_of_ai_disable(character_id: int) -> int:
    """
    自己正在助理服务的行动链中（AI判断专用），包括送饭和早晚问候
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 是否为要买饭或者要送饭
    if handle_help_make_food_flag_1(character_id):
        return 1
    elif handle_help_make_food_flag_2(character_id):
        return 1
    elif handle_help_buy_food_flag_1(character_id):
        return 1
    elif handle_help_buy_food_flag_2(character_id):
        return 1
    elif handle_help_buy_food_flag_3(character_id):
        return 1
    # 是否为要早晚安问候
    elif handle_morning_salutation_flag_1(character_id):
        return 1
    elif handle_night_salutation_flag_1(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.BE_BAGGED_0)
def handle_be_bagged_0(character_id: int) -> int:
    """
    自身没有被装袋搬走
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.be_bagged == 1:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.BE_BAGGED_1)
def handle_be_bagged_1(character_id: int) -> int:
    """
    自身被装袋搬走
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.be_bagged == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.PL_BAGGING_CHARA)
def handle_pl_bagging_chara(character_id: int) -> int:
    """
    玩家正在装袋搬走某个角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.sp_flag.bagging_chara_id:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.PL_NOT_BAGGING_CHARA)
def handle_pl_not_bagging_chara(character_id: int) -> int:
    """
    玩家没有正在装袋搬走某个角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.sp_flag.bagging_chara_id:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.IMPRISONMENT_1)
def handle_imprisonment_1(character_id: int) -> int:
    """
    自身被监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.imprisonment == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.IMPRISONMENT_0)
def handle_imprisonment_0(character_id: int) -> int:
    """
    自身没有被监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_imprisonment_1(character_id)


@add_premise(constant_promise.Premise.T_IMPRISONMENT_0)
def handle_t_imprisonment_0(character_id: int) -> int:
    """
    交互对象没有被监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_imprisonment_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_IMPRISONMENT_1)
def handle_t_imprisonment_1(character_id: int) -> int:
    """
    交互对象被监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_imprisonment_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.ESCAPING_1)
def handle_escaping_1(character_id: int) -> int:
    """
    自身正在逃跑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.sp_flag.escaping


@add_premise(constant_promise.Premise.ESCAPING_0)
def handle_escaping_0(character_id: int) -> int:
    """
    自身没有在逃跑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_escaping_1(character_id)


@add_premise(constant_promise.Premise.T_ESCAPING_1)
def handle_t_escaping_1(character_id: int) -> int:
    """
    交互对象正在逃跑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_escaping_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_ESCAPING_0)
def handle_t_escaping_0(character_id: int) -> int:
    """
    交互对象没有在逃跑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_escaping_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_0)
def handle_aromatherapy_flag_0(character_id: int) -> int:
    """
    自身没有香薰疗愈状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_1)
def handle_aromatherapy_flag_1(character_id: int) -> int:
    """
    自身香薰疗愈-回复
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_2)
def handle_aromatherapy_flag_2(character_id: int) -> int:
    """
    自身香薰疗愈-习得
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_3)
def handle_aromatherapy_flag_3(character_id: int) -> int:
    """
    自身香薰疗愈-反感
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_4)
def handle_aromatherapy_flag_4(character_id: int) -> int:
    """
    自身香薰疗愈-快感
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 4:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_5)
def handle_aromatherapy_flag_5(character_id: int) -> int:
    """
    自身香薰疗愈-好感
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.AROMATHERAPY_FLAG_6)
def handle_aromatherapy_flag_6(character_id: int) -> int:
    """
    自身香薰疗愈-催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.aromatherapy == 6:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_0)
def handle_t_aromatherapy_flag_0(character_id: int) -> int:
    """
    交互对象没有香薰疗愈状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_0(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_1)
def handle_t_aromatherapy_flag_1(character_id: int) -> int:
    """
    交互对象香薰疗愈-回复
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_1(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_2)
def handle_t_aromatherapy_flag_2(character_id: int) -> int:
    """
    交互对象香薰疗愈-习得
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_2(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_3)
def handle_t_aromatherapy_flag_3(character_id: int) -> int:
    """
    交互对象香薰疗愈-反感
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_3(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_4)
def handle_t_aromatherapy_flag_4(character_id: int) -> int:
    """
    交互对象香薰疗愈-快感
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_4(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_5)
def handle_t_aromatherapy_flag_5(character_id: int) -> int:
    """
    交互对象香薰疗愈-好感
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_5(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AROMATHERAPY_FLAG_6)
def handle_t_aromatherapy_flag_6(character_id: int) -> int:
    """
    交互对象香薰疗愈-催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_aromatherapy_flag_6(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.MASTUREBATE_FLAG_0)
def handle_masturebate_flag_0(character_id: int) -> int:
    """
    自身没有要自慰状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_masturebate_flag_g_0(character_id):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.MASTUREBATE_FLAG_G_0)
def handle_masturebate_flag_g_0(character_id: int) -> int:
    """
    自身要自慰状态(含全位置)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate > 0:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.MASTUREBATE_FLAG_1)
def handle_masturebate_flag_1(character_id: int) -> int:
    """
    自身要自慰状态_洗手间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate == 1:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.MASTUREBATE_FLAG_2)
def handle_masturebate_flag_2(character_id: int) -> int:
    """
    自身要自慰状态_宿舍
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate == 2:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.MASTUREBATE_FLAG_3)
def handle_masturebate_flag_3(character_id: int) -> int:
    """
    自身要自慰状态_群交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate == 3:
        return 400
    else:
        return 0


@add_premise(constant_promise.Premise.MASTUREBATE_BOFORE_SLEEP_FLAG_0)
def handle_masturebate_bofore_sleep_flag_0(character_id: int) -> int:
    """
    自身没有要睡前自慰状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate_before_sleep == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MASTUREBATE_BOFORE_SLEEP_FLAG_1)
def handle_masturebate_bofore_sleep_flag_1(character_id: int) -> int:
    """
    自身要睡前自慰状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate_before_sleep == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MASTUREBATE_BOFORE_SLEEP_FLAG_2)
def handle_masturebate_bofore_sleep_flag_2(character_id: int) -> int:
    """
    自身已睡前自慰状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.masturebate_before_sleep == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NOT_NEED_MASTUREBATE_BEFORE_SLEEP_OR_ALREADY_MASTUREBATE)
def handle_not_need_masturebate_before_sleep_or_already_masturebate(character_id: int) -> int:
    """
    自身不需要睡前自慰或已经睡前自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_ask_masturbation_before_sleep
    if not handle_ask_masturbation_before_sleep(character_id):
        return 1
    elif handle_masturebate_bofore_sleep_flag_2(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.IS_UNCONSCIOUS_H)
def handle_is_unconscious_h(character_id: int) -> int:
    """
    当前为无意识奸模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h or character_data.sp_flag.unconscious_h:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_UNCONSCIOUS_H)
def handle_not_unconscious_h(character_id: int) -> int:
    """
    当前不是无意识奸模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_is_unconscious_h(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_0)
def handle_unconscious_flag_0(character_id: int) -> int:
    """
    自身没有无意识状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_unconscious_flag_ge_1(character_id)


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_GE_1)
def handle_unconscious_flag_ge_1(character_id: int) -> int:
    """
    自身有无意识状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.sp_flag.unconscious_h


@add_premise(constant_promise.Premise.UNCONSCIOUS_HYPNOSIS_FLAG)
def handle_unconscious_hypnosis_flag(character_id: int) -> int:
    """
    自身有无意识_任意一种催眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h in {4,5,6,7}:
        return 1
    return 0


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_1)
def handle_unconscious_flag_1(character_id: int) -> int:
    """
    自身有无意识_睡眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_2)
def handle_unconscious_flag_2(character_id: int) -> int:
    """
    自身有无意识_醉酒状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_3)
def handle_unconscious_flag_3(character_id: int) -> int:
    """
    自身有无意识_时停状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_4)
def handle_unconscious_flag_4(character_id: int) -> int:
    """
    自身有无意识_平然状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 4:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_5)
def handle_unconscious_flag_5(character_id: int) -> int:
    """
    自身有无意识_空气状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NOT_UNCONSCIOUS_FLAG_5)
def handle_not_unconscious_flag_5(character_id: int) -> int:
    """
    自身没有无意识_空气状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 5:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_6)
def handle_unconscious_flag_6(character_id: int) -> int:
    """
    自身有无意识_体控状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 6:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNCONSCIOUS_FLAG_7)
def handle_unconscious_flag_7(character_id: int) -> int:
    """
    自身有无意识_心控状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h == 7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_0)
def handle_t_unconscious_flag_0(character_id: int) -> int:
    """
    对方没有无意识状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG)
def handle_t_unconscious_flag(character_id: int) -> int:
    """
    对方有无意识状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_HYPNOSIS_FLAG)
def handle_t_unconscious_hypnosis_flag(character_id: int) -> int:
    """
    对方有无意识_任意一种催眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_unconscious_hypnosis_flag(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_1)
def handle_t_unconscious_flag_1(character_id: int) -> int:
    """
    对方有无意识_睡眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NOT_UNCONSCIOUS_FLAG_1)
def handle_t_not_unconscious_flag_1(character_id: int) -> int:
    """
    对方有无意识_睡眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_unconscious_flag_1(character_id)


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_2)
def handle_t_unconscious_flag_2(character_id: int) -> int:
    """
    对方有无意识_醉酒状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_3)
def handle_t_unconscious_flag_3(character_id: int) -> int:
    """
    对方有无意识_时停状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_4)
def handle_t_unconscious_flag_4(character_id: int) -> int:
    """
    对方有无意识_平然状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 4:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NOT_UNCONSCIOUS_FLAG_4)
def handle_t_not_unconscious_flag_4(character_id: int) -> int:
    """
    对方没有无意识_平然状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 4:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_5)
def handle_t_unconscious_flag_5(character_id: int) -> int:
    """
    对方有无意识_空气状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NOT_UNCONSCIOUS_FLAG_5)
def handle_t_not_unconscious_flag_5(character_id: int) -> int:
    """
    对方没有无意识_空气状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 5:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_6)
def handle_t_unconscious_flag_6(character_id: int) -> int:
    """
    对方有无意识_体控状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 6:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NOT_UNCONSCIOUS_FLAG_6)
def handle_t_not_unconscious_flag_6(character_id: int) -> int:
    """
    对方没有无意识_体控状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 6:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_UNCONSCIOUS_FLAG_7)
def handle_t_unconscious_flag_7(character_id: int) -> int:
    """
    对方有无意识_心控状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NOT_UNCONSCIOUS_FLAG_7)
def handle_t_not_unconscious_flag_7(character_id: int) -> int:
    """
    对方没有无意识_心控状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h == 7:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.SLEEP_H_AWAKE_0)
def handle_sleep_h_awake_0(character_id: int) -> int:
    """
    自身没有睡奸中醒来状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sp_flag.sleep_h_awake == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SLEEP_H_AWAKE_1)
def handle_sleep_h_awake_1(character_id: int) -> int:
    """
    自身睡奸中醒来状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_sleep_h_awake_0(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_SLEEP_H_AWAKE_0)
def handle_t_sleep_h_awake_0(character_id: int) -> int:
    """
    交互对象没有睡奸中醒来状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_sleep_h_awake_0(target_chara_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_SLEEP_H_AWAKE_1)
def handle_t_sleep_h_awake_1(character_id: int) -> int:
    """
    交互对象睡奸中醒来状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_sleep_h_awake_0(target_chara_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.HIDDEN_SEX_MODE_0)
def handle_hidden_sex_mode_0(character_id: int) -> int:
    """
    自己不在隐奸模式中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.hidden_sex_mode == 0


@add_premise(constant_promise.Premise.PLAYER_NOT_IN_HIDDEN_SEX_MODE)
def handle_player_not_in_hidden_sex_mode(character_id: int) -> int:
    """
    玩家不在隐奸模式中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return handle_hidden_sex_mode_0(0)


@add_premise(constant_promise.Premise.TARGET_NOT_IN_HIDDEN_SEX_MODE)
def handle_target_not_in_hidden_sex_mode(character_id: int) -> int:
    """
    交互对象不在隐奸模式中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_hidden_sex_mode_0(character_data.target_character_id)


@add_premise(constant_promise.Premise.HIDDEN_SEX_MODE_GE_1)
def handle_hidden_sex_mode_ge_1(character_id: int) -> int:
    """
    自己在某个隐奸模式中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.hidden_sex_mode > 0

@add_premise(constant_promise.Premise.HIDDEN_SEX_MODE_1)
def handle_hidden_sex_mode_1(character_id: int) -> int:
    """
    判断角色是否处于双不隐模式中
    参数:
        character_id (int): 角色id
    返回:
        int: 权重，若角色处于双不隐模式中则返回1，否则返回0
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.hidden_sex_mode == 1


@add_premise(constant_promise.Premise.HIDDEN_SEX_MODE_2)
def handle_hidden_sex_mode_2(character_id: int) -> int:
    """
    判断角色是否处于女隐模式中
    参数:
        character_id (int): 角色id
    返回:
        int: 权重，若角色处于女隐模式中则返回1，否则返回0
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.hidden_sex_mode == 2


@add_premise(constant_promise.Premise.HIDDEN_SEX_MODE_3)
def handle_hidden_sex_mode_3(character_id: int) -> int:
    """
    判断角色是否处于男隐模式中
    参数:
        character_id (int): 角色id
    返回:
        int: 权重，若角色处于男隐模式中则返回1，否则返回0
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.hidden_sex_mode == 3


@add_premise(constant_promise.Premise.HIDDEN_SEX_MODE_4)
def handle_hidden_sex_mode_4(character_id: int) -> int:
    """
    判断角色是否处于双隐模式中
    参数:
        character_id (int): 角色id
    返回:
        int: 权重，若角色处于双隐模式中则返回1，否则返回0
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.hidden_sex_mode == 4


@add_premise(constant_promise.Premise.FIND_FOOD_WEIRD_FLAG_0)
def handlefind_food_weird_flag_0(character_id: int) -> int:
    """
    自身没有发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.find_food_weird == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.FIND_FOOD_WEIRD_FLAG_1)
def handlefind_food_weird_flag_1(character_id: int) -> int:
    """
    自身发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.find_food_weird == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_FIND_FOOD_WEIRD_FLAG_0)
def handlefind_t_food_weird_flag_0(character_id: int) -> int:
    """
    交互对象没有发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.find_food_weird == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_FIND_FOOD_WEIRD_FLAG_1)
def handlefind_t_food_weird_flag_1(character_id: int) -> int:
    """
    交互对象发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.find_food_weird == 1:
        return 1
    else:
        return 0

