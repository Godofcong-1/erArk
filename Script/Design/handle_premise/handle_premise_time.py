import datetime
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.Design import game_time

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


@add_premise(constant_promise.Premise.TIME_DAY)
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
    if now_time.hour >= 6 and now_time.hour <= 17:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_NIGHT)
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
    if now_time.hour <= 5 or now_time.hour >= 18:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_MIDNIGHT)
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
    if now_time.hour <= 1 or now_time.hour >= 22:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_MORNING)
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
    if now_time.hour >= 4 and now_time.hour <= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_MOON)
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
    if now_time.hour >= 10 and now_time.hour <= 13:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_AFTERMOON)
def handle_time_aftermoon(character_id: int) -> int:
    """
    时间:下午（15点~18点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 15 and now_time.hour <= 17:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_0_TO_9)
def handle_time_0_to_9(character_id: int) -> int:
    """
    时间:0点~9点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 0 and now_time.hour <= 9:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_18_TO_23)
def handle_time_18_to_23(character_id: int) -> int:
    """
    时间:18点~23点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 18 and now_time.hour <= 23:
        return 1
    return 0


@add_premise(constant_promise.Premise.EAT_TIME)
def handle_eat_time(character_id: int) -> int:
    """
    校验当前时间是否处于饭点（早上7~8点、中午12~13点、晚上18~19点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    # print(f"debug start_time = {character_data.behavior.start_time}，now_time = {now_time}")
    if character_data.behavior.start_time.hour in {7, 8, 12, 13, 18, 19}:
        # print(f"debug 当前为饭点={character_data.behavior.start_time.hour}")
        return 1
    return 0


@add_premise(constant_promise.Premise.BREAKFAST_TIME)
def handle_breakfast_time(character_id: int) -> int:
    """
    校验当前时间是否处于早饭饭点（早上7~8点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.behavior.start_time.hour in {7, 8}:
        return 1
    return 0


@add_premise(constant_promise.Premise.LAUNCH_TIME)
def handle_launch_time(character_id: int) -> int:
    """
    校验当前时间是否处于午饭饭点（中午12~13点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.behavior.start_time.hour in {12, 13}:
        return 1
    return 0


@add_premise(constant_promise.Premise.DINNER_TIME)
def handle_dinner_time(character_id: int) -> int:
    """
    校验当前时间是否处于晚饭饭点（晚上18~19点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.behavior.start_time.hour in {18, 19}:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOWER_TIME)
def handle_shower_time(character_id: int) -> int:
    """
    淋浴时间（晚上8点到晚上12点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.behavior.start_time.hour in {20, 21, 22, 23}:
        now_hour = character_data.behavior.start_time.hour
        return (now_hour - 19) * 200
    return 0


@add_premise(constant_promise.Premise.NOT_SHOWER_TIME)
def handle_not_shower_time(character_id: int) -> int:
    """
    非淋浴时间（晚上8点到晚上12点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.behavior.start_time.hour in {20, 21, 22, 23}:
        return 0
    return 1


@add_premise(constant_promise.Premise.SLEEP_TIME)
def handle_sleep_time(character_id: int) -> int:
    """
    角色行动开始时间为睡觉时间（晚上10点到早上6点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    if character_data.behavior.start_time.hour in {0, 1, 2, 3, 4, 5, 22, 23}:
        now_hour = character_data.behavior.start_time.hour if character_data.behavior.start_time.hour > 21 else character_data.behavior.start_time.hour + 24
        # print(f"debug {character_data.name}的睡觉前提判定，当前时间为{character_data.behavior.start_time}")
        # print(f"成功进入睡觉前提if，返回值为{(now_hour-21) *100}")
        return (now_hour - 21) * 100
    return 0


@add_premise(constant_promise.Premise.NOT_SLEEP_TIME)
def handle_not_sleep_time(character_id: int) -> int:
    """
    角色行动开始时间不为睡觉时间（晚上10点到早上6点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    if character_data.behavior.start_time.hour in {0, 1, 2, 3, 4, 5, 22, 23}:
        return 0
    return 1


@add_premise(constant_promise.Premise.GAME_TIME_IS_SLEEP_TIME)
def handle_game_time_is_sleep_time(character_id: int) -> int:
    """
    游戏系统时间为睡觉时间（晚上10点到早上6点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_hour = cache.game_time.hour
    if now_hour in {0, 1, 2, 3, 4, 5, 22, 23}:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIRED_GE_75_OR_SLEEP_TIME)
def handle_tired_ge_75_or_sleep_time(character_id: int) -> int:
    """
    疲劳条≥75%或到了睡觉的时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    # print(f"debug {character_data.name}的疲劳条≥75%或到了睡觉的时间前提判定，当前时间为{character_data.behavior.start_time}，疲劳值为{character_data.tired_point}")
    if character_data.behavior.start_time != datetime.datetime(1, 1, 1):
        if character_data.behavior.start_time.hour in {0, 1, 2, 3, 4, 5, 22, 23}:
            now_hour = character_data.behavior.start_time.hour if character_data.behavior.start_time.hour > 20 else character_data.behavior.start_time.hour + 24
            # print(f"debug {character_data.name}的睡觉前提判定，now_hour = {now_hour}，返回值为{(now_hour-21) *100}")
            return (now_hour - 21) * 100
    value = character_data.tired_point / 160
    if value > 0.74:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIRED_GE_75_OR_SLEEP_TIME_OR_HP_1)
def handle_tired_ge_75_or_sleep_time_or_hp1(character_id: int) -> int:
    """
    疲劳条≥75%或到了睡觉的时间或体力为1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_tired_ge_75_or_sleep_time(character_id):
        return 1
    elif character_data.hit_point <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TO_WORK_TIME)
def handle_to_work_time(character_id: int) -> int:
    """
    到岗时间（早上8:40~早上9:00，下午13:40~下午14:00）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    # 首先需要是工作日
    if game_time.judge_work_today(0):
        if ((character_data.behavior.start_time.hour == 8 and character_data.behavior.start_time.minute >= 40)
        or (character_data.behavior.start_time.hour == 13 and character_data.behavior.start_time.minute >= 40)):
            return 50
    return 0


@add_premise(constant_promise.Premise.WORK_TIME)
def handle_work_time(character_id: int) -> int:
    """
    工作时间（工作日早上9:00~中午12:00，下午14:00~下午18:00）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    # 首先需要是工作日
    if game_time.judge_work_today(0):
        if 9 <= character_data.behavior.start_time.hour < 12 or 14 <= character_data.behavior.start_time.hour < 18:
            return 50
    return 0


@add_premise(constant_promise.Premise.TO_WORK_TIME_OR_WORK_TIME)
def handle_to_work_time_or_work_time(character_id: int) -> int:
    """
    到岗时间或工作时间（工作日早上8:40~中午12:00，下午13:40~下午18:00）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    # 首先需要是工作日
    if game_time.judge_work_today(0):
        if ((character_data.behavior.start_time.hour == 8 and character_data.behavior.start_time.minute >= 40)
        or (character_data.behavior.start_time.hour == 13 and character_data.behavior.start_time.minute >= 40)
        or (9 <= character_data.behavior.start_time.hour < 12)
        or (14 <= character_data.behavior.start_time.hour < 18)):
            return 1
    return 0


@add_premise(constant_promise.Premise.ALL_ENTERTAINMENT_TIME)
def handle_all_entertainment_time(character_id: int) -> int:
    """
    全娱乐时间（休息日为工作时间+下班，工作日为仅下班）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 如果是非工作日，则为工作时间+下班
    if not game_time.judge_work_today(0) or character_data.work.work_type == 0:
        if 9 <= character_data.behavior.start_time.hour < 12 or 14 <= character_data.behavior.start_time.hour < 18 or 19 <= character_data.behavior.start_time.hour < 22:
            return 50
    # 如果是工作日，仅取19:00~22:00的晚上时间
    else:
        if 19 <= character_data.behavior.start_time.hour < 22:
            return 50
    return 0


@add_premise(constant_promise.Premise.NOT_ALL_ENTERTAINMENT_TIME)
def handle_not_all_entertainment_time(character_id: int) -> int:
    """
    非全娱乐时间（休息日为工作时间+下班，工作日为仅下班）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 如果是非工作日，则为工作时间+下班
    if not game_time.judge_work_today(0) or character_data.work.work_type == 0:
        if 9 <= character_data.behavior.start_time.hour < 12 or 14 <= character_data.behavior.start_time.hour < 22:
            return 0
    # 如果是工作日，仅取18:00~22:00的下班时间
    else:
        if 18 <= character_data.behavior.start_time.hour < 22:
            return 0
    return 50


@add_premise(constant_promise.Premise.MORNING_ENTERTAINMENT_TIME)
def handle_morning_entertainment_time(character_id: int) -> int:
    """
    上午娱乐时间（早上9:00~中午12:00）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    if 9 <= character_data.behavior.start_time.hour < 12:
        return 50
    return 0


@add_premise(constant_promise.Premise.AFTERNOON_ENTERTAINMENT_TIME)
def handle_afternoon_entertainment_time(character_id: int) -> int:
    """
    下午娱乐时间（下午14:00~下午18:00）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    if 14 <= character_data.behavior.start_time.hour < 18:
        return 50
    return 0


@add_premise(constant_promise.Premise.NIGHT_ENTERTAINMENT_TIME)
def handle_evening_entertainment_time(character_id: int) -> int:
    """
    晚上娱乐时间（下午19:00~22:00）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    # return (now_time == 4) * 100
    if 19 <= character_data.behavior.start_time.hour < 22:
        return 50
    return 0


@add_premise(constant_promise.Premise.TIME_WORKDAYD)
def handle_time_workday(character_id: int) -> int:
    """
    今天为工作日（周一到周五）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return game_time.judge_work_today(0)


@add_premise(constant_promise.Premise.TIME_WEEKEND)
def handle_time_weekend(character_id: int) -> int:
    """
    今天为周末（周六或周日）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not game_time.judge_work_today(0)


@add_premise(constant_promise.Premise.TODAY_IS_HEALTY_CHECK_DAY)
def handle_today_is_healty_check_day(character_id: int) -> int:
    """
    今天是体检日
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 如果是每天体检的话
    if cache.rhodes_island.physical_examination_setting[3] == 3:
        return 1
    # 如果设置的是周末体检日的话
    elif cache.rhodes_island.physical_examination_setting[7] == 0:
        if handle_time_weekend(character_id):
            return 1
    # 否则手动检查当前星期
    else:
        now_week_day = cache.game_time.weekday()
        if now_week_day in cache.rhodes_island.manually_selected_exam_week_day_list:
            return 1
    return 0


@add_premise(constant_promise.Premise.MORIING_SALUTATION_TIME)
def handle_morning_salutation_time(character_id: int) -> int:
    """
    当前是早安问候时间（玩家醒来时间之后，动态权重50+超时分钟数 * 5）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    now_time_hour, now_time_minute = now_time.hour, now_time.minute
    # 中午12点后不再进行早安问候
    if now_time_hour >= 12:
        return 0
    # 玩家的醒来时间
    pl_character_data = cache.character_data[0]
    plan_to_wake_time = pl_character_data.action_info.plan_to_wake_time
    wake_time_hour, wake_time_minute = plan_to_wake_time[0], plan_to_wake_time[1]
    # print(f"debug {character_data.name}进行玩家的醒来前提判定，当前时间为{now_time}，计划醒来时间为{pl_character_data.action_info.plan_to_wake_time}")
    if now_time_hour > wake_time_hour or (now_time_hour == wake_time_hour and now_time_minute >= wake_time_minute):
        # print(f"debug 判定通过")
        # 超时分钟数
        over_time_minute = (now_time_hour - wake_time_hour) * 60 + now_time_minute - wake_time_minute
        over_time_minute = max(0, over_time_minute)
        return 50 + over_time_minute * 5
    return 0


@add_premise(constant_promise.Premise.NOT_MORIING_SALUTATION_TIME)
def handle_not_morning_salutation_time(character_id: int) -> int:
    """
    当前不是早安问候时间（玩家醒来时间之后）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    now_time_hour, now_time_minute = now_time.hour, now_time.minute
    pl_character_data = cache.character_data[0]
    plan_to_wake_time = pl_character_data.action_info.plan_to_wake_time
    wake_time_hour, wake_time_minute = plan_to_wake_time[0], plan_to_wake_time[1]
    # print(f"debug {character_data.name}进行玩家的醒来前提判定，当前时间为{now_time}，计划醒来时间为{pl_character_data.action_info.plan_to_wake_time}")
    if now_time_hour > wake_time_hour or (now_time_hour == wake_time_hour and now_time_minute >= wake_time_minute):
        # print(f"debug 判定通过")
        return 0
    return 1


@add_premise(constant_promise.Premise.BEFORE_MORNING_SALUTATION_TIME)
def handle_before_morning_salutation_time(character_id: int) -> int:
    """
    当前是早安问候时间之前（玩家醒来时间之前）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    now_time_hour, now_time_minute = now_time.hour, now_time.minute
    # 中午12点后不再进行早安问候
    if now_time_hour >= 12:
        return 0
    # 玩家的醒来时间
    pl_character_data = cache.character_data[0]
    plan_to_wake_time = pl_character_data.action_info.plan_to_wake_time
    wake_time_hour, wake_time_minute = plan_to_wake_time[0], plan_to_wake_time[1]
    # print(f"debug {character_data.name}进行玩家的醒来前提判定，当前时间为{now_time}，计划醒来时间为{pl_character_data.action_info.plan_to_wake_time}")
    if now_time_hour < wake_time_hour or (now_time_hour == wake_time_hour and now_time_minute < wake_time_minute):
        return 50
    return 0

@add_premise(constant_promise.Premise.NIGHT_SALUTATION_TIME)
def handle_night_salutation_time(character_id: int) -> int:
    """
    当前是晚安问候时间（计划睡觉时间之后，权重50）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 当前角色的行为时间
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    now_time_hour, now_time_minute = now_time.hour, now_time.minute
    # 玩家的睡觉时间
    pl_character_data = cache.character_data[0]
    plan_to_sleep_time = pl_character_data.action_info.plan_to_sleep_time
    sleep_time_hour, sleep_time_minute = plan_to_sleep_time[0], plan_to_sleep_time[1]
    # print(f"debug {character_data.name}进行玩家的睡觉前提判定，当前时间为{now_time}，计划睡觉时间为{pl_character_data.action_info.plan_to_sleep_time}")
    if now_time_hour > sleep_time_hour or (now_time_hour == sleep_time_hour and now_time_minute >= sleep_time_minute):
        # print(f"debug 判定通过")
        return 50
    return 0


@add_premise(constant_promise.Premise.NOT_NIGHT_SALUTATION_TIME)
def handle_not_night_salutation_time(character_id: int) -> int:
    """
    当前不是晚安问候时间（计划睡觉时间之后）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 当前角色的行为时间
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    now_time_hour, now_time_minute = now_time.hour, now_time.minute
    # 玩家的睡觉时间
    pl_character_data = cache.character_data[0]
    plan_to_sleep_time = pl_character_data.action_info.plan_to_sleep_time
    sleep_time_hour, sleep_time_minute = plan_to_sleep_time[0], plan_to_sleep_time[1]
    # print(f"debug {character_data.name}进行玩家的睡觉前提判定，当前时间为{now_time}，计划睡觉时间为{pl_character_data.action_info.plan_to_sleep_time}")
    if sleep_time_hour > now_time_hour or (sleep_time_hour == now_time_hour and sleep_time_minute >= now_time_minute):
        # print(f"debug 判定通过")
        return 0
    return 1


@add_premise(constant_promise.Premise.STILL_30_MINUTES_BEFORE_END)
def handle_still_30_minutes_before_end(character_id: int) -> int:
    """
    距离行动结束时间还有至少30分钟
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 当前角色的行为时间
    character_data: game_type.Character = cache.character_data[character_id]
    start_time = character_data.behavior.start_time
    end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
    now_time = cache.game_time
    true_add_time = int((now_time.timestamp() - end_time.timestamp()) / 60)
    if true_add_time >= 30:
        return 1
    return 0


@add_premise(constant_promise.Premise.CHARA_BEHAVIOR_END_TIME_LATEER_THAN_GAME_TIME)
def handle_chara_behavior_end_time_lateer_than_game_time(character_id: int) -> int:
    """
    角色行动结束时间晚于游戏时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 当前角色的行为时间
    character_data: game_type.Character = cache.character_data[character_id]
    start_time = character_data.behavior.start_time
    end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
    now_time = cache.game_time
    if game_time.judge_date_big_or_small(end_time, now_time) == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_OVER_A_YEAR)
def handle_time_over_a_year(character_id: int) -> int:
    """
    游戏时间超过一年
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_time = cache.game_time
    if now_time.year >= 2021:
        return 1
    elif now_time.year == 2020 and now_time.month >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_SPRING)
def handle_time_spring(character_id: int) -> int:
    """
    当前是春季
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_time = cache.game_time
    if now_time.month == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_SUMMER)
def handle_time_summer(character_id: int) -> int:
    """
    当前是夏季
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_time = cache.game_time
    if now_time.month == 6:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_AUTUMN)
def handle_time_autumn(character_id: int) -> int:
    """
    当前是秋季
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_time = cache.game_time
    if now_time.month == 9:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_WINTER)
def handle_time_winter(character_id: int) -> int:
    """
    当前是冬季
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_time = cache.game_time
    if now_time.month == 12:
        return 1
    return 0

