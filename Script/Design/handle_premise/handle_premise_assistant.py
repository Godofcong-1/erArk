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


@add_premise(constant_promise.Premise.IS_ASSISTANT)
def handle_is_assistant(character_id: int) -> int:
    """
    自己是当前的助理干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 玩家自己不能是助理
    if character_id == 0:
        return 0
    pl_character_data: game_type.Character = cache.character_data[0]
    return pl_character_data.assistant_character_id == character_id


@add_premise(constant_promise.Premise.NOT_ASSISTANT)
def handle_not_assistant(character_id: int) -> int:
    """
    自己不是当前的助理干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_is_assistant(character_id)


@add_premise(constant_promise.Premise.TARGET_IS_ASSISTANT)
def handle_target_is_assistant(character_id: int) -> int:
    """
    交互对象是当前的助理干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_is_assistant(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_ASSISTANT)
def handle_target_not_assistant(character_id: int) -> int:
    """
    交互对象不是当前的助理干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_is_assistant(character_data.target_character_id)


@add_premise(constant_promise.Premise.ASSISTANT_HELP_WORK_1)
def handle_assistant_help_work_1(character_id: int) -> int:
    """
    自己的助理属性中的辅佐服务开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_FOLLOW_1)
def handle_assistant_follow_1(character_id: int) -> int:
    """
    自己的助理属性中的跟随服务开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.assistant_services.setdefault(2, 0)
    if character_data.assistant_services[2]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_HELP_WORK_0)
def handle_assistant_help_work_0(character_id: int) -> int:
    """
    自己的助理属性中的辅佐服务关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[3]:
        return 0
    return 1


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_0)
def handle_assistant_send_food_0(character_id: int) -> int:
    """
    自己的助理属性中的送饭服务未开启
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[4]:
        return 0
    return 1


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_1)
def handle_assistant_send_food_1(character_id: int) -> int:
    """
    自己的助理属性中的送饭服务为帮忙买午饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[4] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_2)
def handle_assistant_send_food_2(character_id: int) -> int:
    """
    自己的助理属性中的送饭服务为亲手做午饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[4] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_3)
def handle_assistant_send_food_3(character_id: int) -> int:
    """
    自己的助理属性中的送饭服务为亲手做三餐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[4] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_OF_AI_DISABLE)
def handle_assistant_send_food_of_ai_disable(character_id: int) -> int:
    """
    自己的助理属性中的送饭服务不影响AI吃饭的情况（包括未开启，开启午饭但当前非午饭）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if not character_data.assistant_services[4]:
        return 1
    if character_data.assistant_services[4] in {1,2} and character_data.behavior.start_time.hour in {7, 8, 18, 19}:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_1_ABLE)
def handle_assistant_send_food_1_able(character_id: int) -> int:
    """
    自己的助理属性满足帮忙买午饭（设定为1，flag为0，且当前为午饭）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[4] == 1 and character_data.sp_flag.help_buy_food == 0 and character_data.behavior.start_time.hour in {12, 13}:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_SEND_FOOD_2_ABLE)
def handle_assistant_send_food_2_able(character_id: int) -> int:
    """
    自己的助理属性满足帮忙做饭（含午饭与三餐）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[4] == 2 and character_data.sp_flag.help_make_food == 0 and character_data.behavior.start_time.hour in {12, 13}:
        return 1
    elif character_data.assistant_services[4] == 3 and character_data.sp_flag.help_make_food == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_MORIING_SALUTATION_0)
def handle_assistant_morning_salutation_0(character_id: int) -> int:
    """
    自己的助理属性中的早安问候服务未开启
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[5]:
        return 0
    return 1


@add_premise(constant_promise.Premise.ASSISTANT_MORIING_SALUTATION_ON)
def handle_assistant_morning_salutation_on(character_id: int) -> int:
    """
    自己的助理属性中的早安问候服务开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[5]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_MORIING_SALUTATION_1)
def handle_assistant_morning_salutation_1(character_id: int) -> int:
    """
    自己的助理属性中的早安问候服务为-早上叫起床
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[5] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_MORIING_SALUTATION_2)
def handle_assistant_morning_salutation_2(character_id: int) -> int:
    """
    自己的助理属性中的早安问候服务为-早安吻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[5] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_MORIING_SALUTATION_3)
def handle_assistant_morning_salutation_3(character_id: int) -> int:
    """
    自己的助理属性中的早安问候服务为-早安咬
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[5] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_NIGHT_SALUTATION_0)
def handle_assistant_night_salutation_0(character_id: int) -> int:
    """
    自己的助理属性中的晚安问候服务未开启
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[6]:
        return 0
    return 1


@add_premise(constant_promise.Premise.ASSISTANT_NIGHT_SALUTATION_ON)
def handle_assistant_night_salutation_on(character_id: int) -> int:
    """
    自己的助理属性中的晚安问候服务开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[6]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_NIGHT_SALUTATION_1)
def handle_assistant_night_salutation_1(character_id: int) -> int:
    """
    自己的助理属性中的晚安问候服务为-晚上催睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[6] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_NIGHT_SALUTATION_2)
def handle_assistant_night_salutation_2(character_id: int) -> int:
    """
    自己的助理属性中的晚安问候服务为-晚安吻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[6] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_NIGHT_SALUTATION_3)
def handle_assistant_night_salutation_3(character_id: int) -> int:
    """
    自己的助理属性中的晚安问候服务为-晚安咬
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.assistant_services[6] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_SALUTATION_OF_AI_DISABLE)
def handle_assistant_salutation_of_ai_disable(character_id: int) -> int:
    """
    自己的助理属性中的问候服务不影响AI行动的情况（包括未开启，开启但当前非问候时间）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_morning_salutation_flag_2, handle_night_salutation_flag_2, handle_time_0_to_9, handle_time_18_to_23,
    )
    # 早安问候
    if handle_time_0_to_9(character_id):
        if handle_assistant_morning_salutation_0(character_id):
            return 1
        else:
            if handle_morning_salutation_flag_2(character_id):
                return 1
            # elif handle_morning_salutation_flag_2(character_id):
            #     return 1
            return 0
    # 晚安问候
    if handle_time_18_to_23(character_id):
        if handle_assistant_night_salutation_0(character_id):
            return 1
        # 只要已开启，则必须在问候完才能睡觉
        else:
            if handle_night_salutation_flag_2(character_id):
                # print("已晚安问候，可以睡觉了")
                return 1
            # print("未晚安问候，不能睡觉")
            return 0
    return 1


@add_premise(constant_promise.Premise.ASSISTANT_LIVE_TOGETHER_ON)
def handle_assistant_live_together_on(character_id: int) -> int:
    """
    自己的助理属性为正在同居
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.assistant_services[7] == 1


@add_premise(constant_promise.Premise.ASSISTANT_LIVE_TOGETHER_OFF)
def handle_assistant_live_together_off(character_id: int) -> int:
    """
    自己的助理属性为未同居
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_assistant_live_together_on(character_id)


@add_premise(constant_promise.Premise.TARGET_ASSISTANT_LIVE_TOGETHER_ON)
def handle_target_assistant_live_together_on(character_id: int) -> int:
    """
    交互对象的助理属性为正在同居
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_assistant_live_together_on(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_ASSISTANT_LIVE_TOGETHER_OFF)
def handle_target_assistant_live_together_off(character_id: int) -> int:
    """
    交互对象的助理属性为未同居
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_assistant_live_together_on(character_data.target_character_id)


@add_premise(constant_promise.Premise.PL_ASSISTANT_CHANGE_EVERY_WEEK_ON)
def handle_pl_assistant_change_every_week_on(character_id: int) -> int:
    """
    玩家设置了每周一轮换助理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    assistant_chara_id = pl_character_data.assistant_character_id
    if assistant_chara_id == 0:
        return 0
    assistant_character_data: game_type.Character = cache.character_data[assistant_chara_id]
    assistant_character_data.assistant_services.setdefault(10, 0)
    if assistant_character_data.assistant_services[10] == 1:
        return 1
    return 0
