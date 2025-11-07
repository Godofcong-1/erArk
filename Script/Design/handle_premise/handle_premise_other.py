import datetime
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.Design import map_handle, game_time, attr_calculation
from Script.Config import normal_config, game_config

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


@add_premise(constant_promise.Premise.HAVE_TARGET)
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


@add_premise(constant_promise.Premise.HAVE_NO_TARGET)
def handle_have_no_target(character_id: int) -> int:
    """
    校验角色是否没有交互对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_have_target(character_id)


@add_premise(constant_promise.Premise.TARGET_NO_PLAYER)
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


@add_premise(constant_promise.Premise.VISITOR_ZONE_GE_2)
def handle_visitor_zone_ge_2(character_id: int) -> int:
    """
    访客区等级大于等于2级
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_level = cache.rhodes_island.facility_level[13]
    if now_level >= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.VISITOR_ZONE_HAVE_TARGET)
def handle_visitor_zone_have_target(character_id: int) -> int:
    """
    访客区当前有已选择好的邀请目标
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.invite_visitor[0] != 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PERIODIC_HEALTH_CHECK_ON)
def handle_periodic_health_check_on(character_id: int) -> int:
    """
    当前已开启定期体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.physical_examination_setting[2] == 1


@add_premise(constant_promise.Premise.HEALTH_CHECK_DONE_NEED_CHECK_AGAIN)
def handle_health_check_done_need_check_again(character_id: int) -> int:
    """
    已体检的仍需要再次体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.physical_examination_setting[5] == 1


@add_premise(constant_promise.Premise.HEALTH_CHECK_DONE_NOT_NEED_CHECK_AGAIN)
def handle_health_check_done_not_need_check_again(character_id: int) -> int:
    """
    已体检的不需要再次体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_health_check_done_need_check_again(character_id)


@add_premise(constant_promise.Premise.BLACKSMITH_SHOP_OPEN)
def handle_blacksmith_shop_open(character_id: int) -> int:
    """
    铁匠铺已开放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.facility_open[13]


@add_premise(constant_promise.Premise.HAVE_MOVED)
def handle_have_moved(character_id: int) -> int:
    """
    自己距离上次移动已经至少经过了1小时
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    move_flag = 0
    # 同一天内过1小时则判定为1
    if now_time.day == character_data.action_info.last_move_time.day and now_time.hour > character_data.action_info.last_move_time.hour:
        character_data.action_info.last_move_time = now_time
        # print("过一小时判定,character_id :",character_id)
        move_flag = 1
    # 非同一天也判定为1
    elif now_time.day != character_data.action_info.last_move_time.day:
        character_data.action_info.last_move_time = now_time
        move_flag = 1
        # print("非同一天判定")
    return move_flag


@add_premise(constant_promise.Premise.AI_WAIT)
def handle_ai_wait(character_id: int) -> int:
    """
    自己需要进行一次5分钟的等待（wait_flag = 1)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sp_flag.wait_flag:
        # print("判断到需要进行等待，character_id = ",character_id)
        return 999
    else:
        return 0


@add_premise(constant_promise.Premise.HAVE_TRAINED)
def handle_have_trained(character_id: int) -> int:
    """
    自己距离上次战斗训练已经超过两天了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time = cache.game_time
    train_time = character_data.action_info.last_training_time
    add_day = int((now_time - train_time).days)
    if add_day >= 2:
        return (add_day - 1) * 10
    return 0


@add_premise(constant_promise.Premise.NOT_SHOWER)
def handle_not_shower(character_id: int) -> int:
    """
    自己今天还没有洗澡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time = cache.game_time
    shower_time = character_data.action_info.last_shower_time
    if shower_time.day == now_time.day:
        return 0
    elif now_time.hour <= 6 and (game_time.count_day_for_datetime(shower_time, now_time) == 1):
        return 0
    return 1


@add_premise(constant_promise.Premise.HAVE_SHOWERED)
def handle_have_showered(character_id: int) -> int:
    """
    自己今天已经洗过澡了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time = cache.game_time
    shower_time = character_data.action_info.last_shower_time
    if shower_time.day == now_time.day:
        return 1
    elif now_time.hour <= 6 and (game_time.count_day_for_datetime(shower_time, now_time) == 1):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_NOT_WAKE_UP)
def handle_have_not_wake_up(character_id: int) -> int:
    """
    自己今天还没有起床
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time = cache.game_time
    wake_up_time = character_data.action_info.wake_time
    if wake_up_time.day != now_time.day and wake_up_time.day != character_data.behavior.start_time.day:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NEED_HEALTH_CHECK_TODAY)
def handle_self_need_health_check_today(character_id: int) -> int:
    """
    自己今天需要进行体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.action_info.health_check_today > 0


@add_premise(constant_promise.Premise.SELF_NEED_HEALTH_CHECK_MORNING)
def handle_self_need_health_check_morning(character_id: int) -> int:
    """
    自己今天上午需要进行体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.action_info.health_check_today == 1


@add_premise(constant_promise.Premise.SELF_NEED_HEALTH_CHECK_AFTERNOON)
def handle_self_need_health_check_afternoon(character_id: int) -> int:
    """
    自己今天下午需要进行体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.action_info.health_check_today == 2


@add_premise(constant_promise.Premise.SELF_NEED_HEALTH_CHECK_NOW)
def handle_self_need_health_check_now(character_id: int) -> int:
    """
    自己现在需要进行体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.action_info.health_check_today == 3


@add_premise(constant_promise.Premise.IS_MAN)
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


@add_premise(constant_promise.Premise.IS_WOMAN)
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


@add_premise(constant_promise.Premise.GOOD_MOOD)
def handle_good_mood(character_id: int) -> int:
    """
    自己心情愉快
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    value = character_data.angry_point
    if value <= 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_MOOD)
def handle_normal_mood(character_id: int) -> int:
    """
    自己心情普通
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    value = character_data.angry_point
    if 5 < value and value <= 30:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.BAD_MOOD)
def handle_bad_mood(character_id: int) -> int:
    """
    自己心情不好
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    value = character_data.angry_point
    if 30 < value and value <= 50:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.ANGRY_MOOD)
def handle_angry_mood(character_id: int) -> int:
    """
    自己心情愤怒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    value = character_data.angry_point
    if value > 50:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SELF_ANGRY_WITH_PLAYER)
def handle_self_angry_with_player(character_id: int) -> int:
    """
    自己被玩家惹火了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.angry_with_player


@add_premise(constant_promise.Premise.SELF_NOT_ANGRY_WITH_PLAYER)
def handle_self_not_angry_with_player(character_id: int) -> int:
    """
    自己没有被玩家惹火
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_angry_with_player(character_id)


@add_premise(constant_promise.Premise.TARGET_GOOD_MOOD)
def handle_target_good_mood(character_id: int) -> int:
    """
    交互对象心情愉快
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_good_mood(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_NORMAL_MOOD)
def handle_target_normal_mood(character_id: int) -> int:
    """
    交互对象心情普通
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_normal_mood(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_BAD_MOOD)
def handle_target_bad_mood(character_id: int) -> int:
    """
    交互对象心情不好
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_bad_mood(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_ANGRY_MOOD)
def handle_target_angry_mood(character_id: int) -> int:
    """
    交互对象心情愤怒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_angry_mood(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_ABD_OR_ANGRY_MOOD)
def handle_t_bad_or_angry_mood(character_id: int) -> int:
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


@add_premise(constant_promise.Premise.TARGET_ANGRY_WITH_PLAYER)
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
    if target_data.sp_flag.angry_with_player:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_NOT_ANGRY_WITH_PLAYER)
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
    if target_data.sp_flag.angry_with_player:
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.COLLECT_BONUS_102)
def handle_collect_bonus_102(character_id: int) -> int:
    """
    校验收藏奖励_102_解锁索要内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.pl_collection.collection_bonus[102]:
        return 1
    return 0


@add_premise(constant_promise.Premise.COLLECT_BONUS_202)
def handle_collect_bonus_202(character_id: int) -> int:
    """
    校验收藏奖励_203_解锁索要袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.pl_collection.collection_bonus[202]:
        return 1
    return 0


@add_premise(constant_promise.Premise.KISS_0)
def handle_kiss_0(character_id: int) -> int:
    """
    校验自身亲吻经验==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.experience[40] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.KISS_GE_10)
def handle_kiss_ge_10(character_id: int) -> int:
    """
    校验自身亲吻经验>=10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.experience[40] >= 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_KISS_0)
def handle_t_kiss_0(character_id: int) -> int:
    """
    校验交互对象亲吻经验==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.experience[40] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_KISS_GE_10)
def handle_t_kiss_ge_10(character_id: int) -> int:
    """
    校验交互对象亲吻经验>=10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.experience[40] >= 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_SHY_GE_100000)
def handle_self_shy_ge_100000(character_id: int) -> int:
    """
    自身羞耻小于等于100000
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.status_data[16] <= 100000:
        return 1
    return 0


@add_premise(constant_promise.Premise.IS_MEDICAL)
def handle_is_medical(character_id: int) -> int:
    """
    校验自己的职业为医疗
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.profession == 3


@add_premise(constant_promise.Premise.T_IS_MEDICAL)
def handle_t_is_medical(character_id: int) -> int:
    """
    校验交互对象的职业为医疗
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.profession == 3


@add_premise(constant_promise.Premise.FLAG_BABY_EXIST)
def handle_flag_baby_exist(character_id: int) -> int:
    """
    特殊flag 当前有婴儿存在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    for i in range(len(cache.npc_tem_data)):
        chara_id = i + 1
        if chara_id in cache.character_data:
            if cache.character_data[chara_id].talent[101]:
                return 1

    return 0


@add_premise(constant_promise.Premise.POSITION_IN_IN_NURSERY_AND_FLAG_BABY_EXIST)
def handle_position_in_nursery_and_flag_baby_exist(character_id: int) -> int:
    """
    特殊flag 当前自己在育儿室且育儿室有婴儿存在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """

    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Nursery" in now_scene_data.scene_tag:
        for chara_id in now_scene_data.character_list:
            if cache.character_data[chara_id].talent[101]:
                return 1

    return 0


@add_premise(constant_promise.Premise.REPRODUCTION_PERIOD_0)
def handle_reproduction_period_0(character_id: int) -> int:
    """
    自己当前是安全期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    reproduction_period = character_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.REPRODUCTION_PERIOD_1)
def handle_reproduction_period_1(character_id: int) -> int:
    """
    自己当前是普通期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    reproduction_period = character_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.REPRODUCTION_PERIOD_2)
def handle_reproduction_period_2(character_id: int) -> int:
    """
    自己当前是危险期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    reproduction_period = character_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.REPRODUCTION_PERIOD_3)
def handle_reproduction_period_3(character_id: int) -> int:
    """
    自己当前是排卵期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    reproduction_period = character_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_REPRODUCTION_PERIOD_0)
def handle_t_reproduction_period_0(character_id: int) -> int:
    """
    交互对象当前是安全期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    reproduction_period = target_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_REPRODUCTION_PERIOD_1)
def handle_t_reproduction_period_1(character_id: int) -> int:
    """
    交互对象当前是普通期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    reproduction_period = target_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_REPRODUCTION_PERIOD_2)
def handle_t_reproduction_period_2(character_id: int) -> int:
    """
    交互对象当前是危险期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    reproduction_period = target_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_REPRODUCTION_PERIOD_3)
def handle_t_reproduction_period_3(character_id: int) -> int:
    """
    交互对象当前是排卵期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    reproduction_period = target_data.pregnancy.reproduction_period
    now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
    if now_reproduction_period_type == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_REPRODUCTION_PERIOD_NOT_3)
def handle_t_reproduction_period_not_3(character_id: int) -> int:
    """
    交互对象当前不是排卵期
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_reproduction_period_3(character_id)


@add_premise(constant_promise.Premise.T_FERTILIZATION_OR_PREGNANCY)
def handle_t_fertilization_or_pregnancy(character_id: int) -> int:
    """
    交互对象受精或怀孕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[20] or target_data.talent[21] or target_data.talent[22] or target_data.talent[23]:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NOT_FERTILIZATION_OR_PREGNANCY)
def handle_t_not_fertilization_or_pregnancy(character_id: int) -> int:
    """
    交互对象未受精或怀孕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_fertilization_or_pregnancy(character_id)


@add_premise(constant_promise.Premise.SELF_IS_PLAYER_DAUGHTER)
def handle_self_is_player_daughter(character_id: int) -> int:
    """
    校验自己是玩家的女儿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.relationship.father_id == 0


@add_premise(constant_promise.Premise.SELF_NOT_PLAYER_DAUGHTER)
def handle_self_not_player_daughter(character_id: int) -> int:
    """
    校验自己不是玩家的女儿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_is_player_daughter(character_id)


@add_premise(constant_promise.Premise.TARGET_IS_PLAYER_DAUGHTER)
def handle_target_is_player_daughter(character_id: int) -> int:
    """
    校验交互对象是玩家的女儿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_is_player_daughter(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_PLAYER_DAUGHTER)
def handle_target_not_player_daughter(character_id: int) -> int:
    """
    校验交互对象不是玩家的女儿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_is_player_daughter(character_data.target_character_id)


# @add_premise(constant_promise.Premise.TARGET_AGE_SIMILAR)
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


# @add_premise(constant_promise.Premise.TARGET_AVERAGE_HEIGHT_SIMILAR)
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


# @add_premise(constant_promise.Premise.TARGET_AVERAGE_HEIGHT_LOW)
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


@add_premise(constant_promise.Premise.TARGET_IS_PLAYER)
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


@add_premise(constant_promise.Premise.DEBUG_MODE_SETTING_ON)
def handle_debug_mode_setting_on(character_id: int) -> int:
    """
    设置里可以开启debug模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if normal_config.config_normal.debug:
        return 1
    return 0


@add_premise(constant_promise.Premise.DEBUG_MODE_ON)
def handle_debug_mode_on(character_id: int) -> int:
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


@add_premise(constant_promise.Premise.DEBUG_MODE_OFF)
def handle_debug_mode_off(character_id: int) -> int:
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


@add_premise(constant_promise.Premise.TO_DO)
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


@add_premise(constant_promise.Premise.IS_PLAYER)
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


@add_premise(constant_promise.Premise.NO_PLAYER)
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


@add_premise(constant_promise.Premise.FAVORABILITY_LE_2)
def handle_favorability_le_2(character_id: int) -> int:
    """
    指令双方中NPC方对玩家的好感等级小于等于2（1000点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    level = 3
    if character_id == 0:
        level,tem = attr_calculation.get_favorability_level(target_data.favorability[0])
    elif character_data.target_character_id == 0:
        level,tem = attr_calculation.get_favorability_level(character_data.favorability[0])
    if level <= 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.FAVORABILITY_GE_3)
def handle_favorability_ge_3(character_id: int) -> int:
    """
    指令双方中NPC方对玩家的好感等级小于等于3（2500点）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    level = 0
    if character_id == 0:
        level,tem = attr_calculation.get_favorability_level(target_data.favorability[0])
    elif character_data.target_character_id == 0:
        level,tem = attr_calculation.get_favorability_level(character_data.favorability[0])
    if level >= 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TRUST_GE_200)
def handle_target_trust_ge_200(character_id: int) -> int:
    """
    交互对象信赖>=200%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    return target_data.trust >= 200


@add_premise(constant_promise.Premise.HAVE_COLLECTION)
def handle_have_collection(character_id: int) -> int:
    """
    持有藏品
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if len(character_data.pl_collection.npc_panties_tem):
        return 1
    if len(character_data.pl_collection.npc_socks_tem):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.IS_H)
def handle_is_h(character_id: int) -> int:
    """
    当前玩家或玩家交互对象为H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if character_data.sp_flag.is_h or target_data.sp_flag.is_h:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_H)
def handle_not_h(character_id: int) -> int:
    """
    当前玩家或玩家交互对象均不是H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if character_data.sp_flag.is_h or target_data.sp_flag.is_h:
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_IS_H)
def handle_self_is_h(character_id: int) -> int:
    """
    自己在H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.sp_flag.is_h


@add_premise(constant_promise.Premise.SELF_NOT_H)
def handle_self_not_h(character_id: int) -> int:
    """
    自己不在H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_is_h(character_id)


@add_premise(constant_promise.Premise.TARGET_IS_H)
def handle_t_is_h(character_id: int) -> int:
    """
    交互对象在H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_is_h(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_H)
def handle_t_not_h(character_id: int) -> int:
    """
    交互对象不在H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_t_is_h(character_data.target_character_id)


@add_premise(constant_promise.Premise.GROUP_SEX_MODE_ON)
def handle_group_sex_mode_on(character_id: int) -> int:
    """
    群交模式开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.group_sex_mode


@add_premise(constant_promise.Premise.GROUP_SEX_MODE_OFF)
def handle_group_sex_mode_off(character_id: int) -> int:
    """
    群交模式未开启
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_group_sex_mode_on(character_id)


@add_premise(constant_promise.Premise.OPTION_SON)
def handle_option_son(character_id: int) -> int:
    """
    选项的子事件
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 0


@add_premise(constant_promise.Premise.THIS_EVENT_IN_TRIGGERED_RECORD)
def handle_this_event_in_triggered_record(character_id: int) -> int:
    """
    该事件在总次数已触发记录中(需搭配记录结算)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 本前提在以下地方进行调用，此处不进行实际处理
    # Script/Design/event.py#L11
    return 1


@add_premise(constant_promise.Premise.THIS_EVENT_NOT_IN_TRIGGERED_RECORD)
def handle_this_event_not_in_triggered_record(character_id: int) -> int:
    """
    该事件不在总次数已触发记录中(需搭配记录结算)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 本前提在以下地方进行调用，此处不进行实际处理
    # Script/Design/event.py#L11
    return 1


@add_premise(constant_promise.Premise.THIS_EVENT_IN_TODAY_TRIGGERED_RECORD)
def handle_this_event_in_today_triggered_record(character_id: int) -> int:
    """
    该事件在今日已触发记录中(需搭配记录结算)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 本前提在以下地方进行调用，此处不进行实际处理
    # Script/Design/event.py#L11
    return 1


@add_premise(constant_promise.Premise.THIS_EVENT_NOT_IN_TODAY_TRIGGERED_RECORD)
def handle_this_event_not_in_today_triggered_record(character_id: int) -> int:
    """
    该事件不在今日已触发记录中(需搭配记录结算)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 本前提在以下地方进行调用，此处不进行实际处理
    # Script/Design/event.py#L11
    return 1


@add_premise(constant_promise.Premise.DAILY_PANEL_SHOW)
def handle_daily_panel_show(character_id: int) -> int:
    """
    当前日常指令面板可见
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.instruct_type_filter[1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLAY_PANEL_SHOW)
def handle_play_panel_show(character_id: int) -> int:
    """
    当前娱乐指令面板可见
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.instruct_type_filter[2]:
        return 1
    return 0


@add_premise(constant_promise.Premise.WORK_PANEL_SHOW)
def handle_work_panel_show(character_id: int) -> int:
    """
    当前工作指令面板可见
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.instruct_type_filter[3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ARTS_PANEL_SHOW)
def handle_arts_panel_show(character_id: int) -> int:
    """
    当前技艺指令面板可见
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.instruct_type_filter[4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.OBSCENITY_PANEL_SHOW)
def handle_obscenity_panel_show(character_id: int) -> int:
    """
    当前猥亵指令面板可见
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.instruct_type_filter[5]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SEX_PANEL_SHOW)
def handle_sex_panel_show(character_id: int) -> int:
    """
    当前性爱指令面板可见
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.instruct_type_filter[6]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOW_SHOW_NON_H_INSTRUCT)
def handle_now_show_non_h_instruct(character_id: int) -> int:
    """
    当前显示非H类指令
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_now_show_h_instruct(character_id)


@add_premise(constant_promise.Premise.NOW_SHOW_H_INSTRUCT)
def handle_now_show_h_instruct(character_id: int) -> int:
    """
    当前显示H类指令
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_hidden_sex_mode_ge_1,
    )
    # H中
    if handle_is_h(0):
        # 隐奸且已经切换到正常模式，则不显示
        if handle_hidden_sex_mode_ge_1(0) and handle_show_non_h_in_hidden_sex(0):
            return 0
        # 显示
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOW_NON_H_IN_HIDDEN_SEX)
def handle_show_non_h_in_hidden_sex(character_id: int) -> int:
    """
    在隐奸中显示非H类指令
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.show_non_h_in_hidden_sex


@add_premise(constant_promise.Premise.NOT_SHOW_NON_H_IN_HIDDEN_SEX)
def handle_not_show_non_h_in_hidden_sex(character_id: int) -> int:
    """
    不在隐奸中显示非H类指令
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_show_non_h_in_hidden_sex(character_id)


@add_premise(constant_promise.Premise.GENERATE_BY_AI)
def handle_generate_by_ai(character_id: int) -> int:
    """
    该文本由AI自动生成
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 0


@add_premise(constant_promise.Premise.AI_CHAT_ON)
def handle_ai_chat_on(character_id: int) -> int:
    """
    AI文本生成开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    cache.ai_setting.ai_chat_setting.setdefault(1, 0)
    return cache.ai_setting.ai_chat_setting[1]


@add_premise(constant_promise.Premise.SELF_WAITING_FOR_HEALTH_CHECK)
def handle_self_waiting_for_health_check(character_id: int) -> int:
    """
    自己正在等待体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return character_id in cache.rhodes_island.waiting_for_exam_operator_ids


@add_premise(constant_promise.Premise.SELF_NOT_WAITING_FOR_HEALTH_CHECK)
def handle_self_not_waiting_for_health_check(character_id: int) -> int:
    """
    自己没有在等待体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_waiting_for_health_check(character_id)


@add_premise(constant_promise.Premise.SELF_HEALTH_CHECKED)
def handle_self_health_checked(character_id: int) -> int:
    """
    自己本周期内已经体检过
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return character_id in cache.rhodes_island.examined_operator_ids


@add_premise(constant_promise.Premise.SELF_NOT_HEALTH_CHECKED)
def handle_self_not_health_checked(character_id: int) -> int:
    """
    自己本周期内没有体检过
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_health_checked(character_id)


@add_premise(constant_promise.Premise.SELF_HEALTH_CHECKED_TODAY)
def handle_self_health_checked_today(character_id: int) -> int:
    """
    自己今天已经体检过
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return character_id in cache.rhodes_island.today_physical_examination_chara_id_dict


@add_premise(constant_promise.Premise.SELF_NOT_HEALTH_CHECKED_TODAY)
def handle_self_not_health_checked_today(character_id: int) -> int:
    """
    自己今天没有体检过
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_health_checked_today(character_id)


@add_premise(constant_promise.Premise.SELF_IN_HEALTH_CHECK_LIST)
def handle_self_in_health_check_list(character_id: int) -> int:
    """
    自己在体检名单中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_unnormal_27
    )
    # 如果设置了不重复体检，且自己已体检过，则直接返回0
    if handle_health_check_done_not_need_check_again(character_id) and handle_self_health_checked(character_id):
        return 0
    # 跳过27异常
    if handle_unnormal_27(character_id):
        return 0
    character_data: game_type.Character = cache.character_data[character_id]
    # 源石病患者
    if cache.rhodes_island.physical_examination_setting[4] == 0:
        if character_data.talent[150] == 1:
            return 1
    # 全干员
    elif cache.rhodes_island.physical_examination_setting[4] == 1:
        return 1
    # 手动选择干员
    elif cache.rhodes_island.physical_examination_setting[4] == 2:
        if character_id in cache.rhodes_island.manually_selected_exam_operator_ids:
            return 1
    return 0


@add_premise(constant_promise.Premise.SOMEONE_WAITING_FOR_HEALTH_CHECK)
def handle_someone_waiting_for_health_check(character_id: int) -> int:
    """
    当前有正在等待体检的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return len(cache.rhodes_island.waiting_for_exam_operator_ids) > 0


@add_premise(constant_promise.Premise.SELF_IN_HEALTH_CHECK_ACTION_CHAIN)
def handle_self_in_health_check_action_chain(character_id: int) -> int:
    """
    自己当前正在体检行动链中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_morning_entertainment_time, handle_afternoon_entertainment_time
    )
    # 正在等待体检
    if handle_self_waiting_for_health_check(character_id):
        return 1
    # 立刻需要体检
    if handle_self_need_health_check_now(character_id):
        return 1
    # 自己今天上午需要体检，且现在是上午
    if handle_self_need_health_check_morning(character_id) and handle_morning_entertainment_time(character_id):
        return 1
    # 自己是今天下午需要体检，且现在是下午
    if handle_self_need_health_check_afternoon(character_id) and handle_afternoon_entertainment_time(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_HAVE_NICK_NAME_TO_PL)
def handle_self_have_nick_name_to_pl(character_id: int) -> int:
    """
    自己已设定对玩家的称呼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return len(character_data.nick_name_to_pl)


@add_premise(constant_promise.Premise.SELF_NOT_HAVE_NICK_NAME_TO_PL)
def handle_self_not_have_nick_name_to_pl(character_id: int) -> int:
    """
    自己未设定对玩家的称呼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_have_nick_name_to_pl(character_id)


@add_premise(constant_promise.Premise.SELF_HAVE_NICK_NAME_TO_SELF)
def handle_self_have_nick_name_to_self(character_id: int) -> int:
    """
    自己已设定玩家对自己的称呼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return len(character_data.nick_name)


@add_premise(constant_promise.Premise.SELF_NOT_HAVE_NICK_NAME_TO_SELF)
def handle_self_not_have_nick_name_to_self(character_id: int) -> int:
    """
    自己未设定玩家对自己的称呼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_have_nick_name_to_self(character_id)


@add_premise(constant_promise.Premise.JJ_0)
def handle_jj_0(character_id: int) -> int:
    """
    自身阴茎大小为短小
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.pl_ability.jj_size == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.JJ_1)
def handle_jj_1(character_id: int) -> int:
    """
    自身阴茎大小为普通
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.pl_ability.jj_size == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.JJ_2)
def handle_jj_2(character_id: int) -> int:
    """
    自身阴茎大小为粗大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.pl_ability.jj_size == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.JJ_3)
def handle_jj_3(character_id: int) -> int:
    """
    自身阴茎大小为巨根
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.pl_ability.jj_size == 3:
        return 1
    return 0


# @add_premise(constant_promise.Premise.TARGET_IS_COLLECTION)
# def handle_target_is_collection(character_id: int) -> int:
#     """
#     校验交互对象是否已被玩家收藏
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     player_data: game_type.Character = cache.character_data[0]
#     return character_data.target_character_id in player_data.collection_character


# @add_premise(constant_promise.Premise.TARGET_IS_NOT_COLLECTION)
# def handle_target_is_not_collection(character_id: int) -> int:
#     """
#     校验交互对象是否未被玩家收藏
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     player_data: game_type.Character = cache.character_data[0]
#     return character_data.target_character_id not in player_data.collection_character


@add_premise(constant_promise.Premise.T_LUBRICATION_L_1)
def handle_t_lubrication_l_1(character_id: int) -> int:
    """
    校验交互对象是否润滑<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LUBRICATION_GE_3)
def handle_t_lubrication_ge_3(character_id: int) -> int:
    """
    校验交互对象是否润滑>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LUBRICATION_GE_1)
def handle_t_lubrication_ge_1(character_id: int) -> int:
    """
    校验交互对象是否润滑>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LUBRICATION_GE_5)
def handle_t_lubrication_ge_5(character_id: int) -> int:
    """
    校验交互对象是否润滑>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LUBRICATION_GE_7)
def handle_t_lubrication_ge_7(character_id: int) -> int:
    """
    校验交互对象是否润滑>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LUBRICATION_L_3)
def handle_t_lubrication_l_3(character_id: int) -> int:
    """
    校验交互对象是否润滑<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LUBRICATION_L_7)
def handle_t_lubrication_l_7(character_id: int) -> int:
    """
    校验交互对象是否润滑<7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.status_data[8] < 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LACTATION_1)
def handle_t_lactation_1(character_id: int) -> int:
    """
    校验交互对象是否泌乳==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[27] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LACTATION_0)
def handle_t_lactation_0(character_id: int) -> int:
    """
    校验交互对象是否泌乳==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[27] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.FERTILIZATION_0)
def handle_fertilization_0(character_id: int) -> int:
    """
    校验角色是否受精==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[20] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.FERTILIZATION_1)
def handle_fertilization_1(character_id: int) -> int:
    """
    校验角色是否受精==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[20] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PREGNANCY_0)
def handle_pregnancy_0(character_id: int) -> int:
    """
    校验角色是否妊娠==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[21] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PREGNANCY_1)
def handle_pregnancy_1(character_id: int) -> int:
    """
    校验角色是否妊娠==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[21] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FERTILIZATION_0)
def handle_t_fertilization_0(character_id: int) -> int:
    """
    校验交互对象是否受精==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[20] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FERTILIZATION_1)
def handle_t_fertilization_1(character_id: int) -> int:
    """
    校验交互对象是否受精==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[20] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_PREGNANCY_0)
def handle_t_pregnancy_0(character_id: int) -> int:
    """
    校验交互对象是否妊娠==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[21] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_PREGNANCY_1)
def handle_t_pregnancy_1(character_id: int) -> int:
    """
    校验交互对象是否妊娠==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[21] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PARTURIENT_0)
def handle_parturient_0(character_id: int) -> int:
    """
    校验角色是否临盆==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[22] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PARTURIENT_1)
def handle_parturient_1(character_id: int) -> int:
    """
    校验角色是否临盆==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[22] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_PARTURIENT_1)
def handle_t_parturient_1(character_id: int) -> int:
    """
    校验交互对象是否临盆==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[22] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_PARTURIENT_0)
def handle_t_parturient_0(character_id: int) -> int:
    """
    校验交互对象是否临盆==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[22] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.POSTPARTUM_0)
def handle_postpartum_0(character_id: int) -> int:
    """
    校验角色是否产后==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[23] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.POSTPARTUM_1)
def handle_postpartum_1(character_id: int) -> int:
    """
    校验角色是否产后==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[23] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_POSTPARTUM_0)
def handle_t_postpartum_0(character_id: int) -> int:
    """
    校验交互对象是否产后==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[23] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_POSTPARTUM_1)
def handle_t_postpartum_1(character_id: int) -> int:
    """
    校验交互对象是否产后==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[23] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_PARTURIENT_OR_POSTPARTUM)
def handle_self_parturient_or_postpartum(character_id: int) -> int:
    """
    自己正在临盆或产后
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_parturient_1(character_id) or handle_postpartum_1(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.REARING_0)
def handle_rearing_0(character_id: int) -> int:
    """
    校验角色是否育儿==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[24] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.REARING_1)
def handle_rearing_1(character_id: int) -> int:
    """
    校验角色是否育儿==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[24] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_REARING_0)
def handle_t_rearing_0(character_id: int) -> int:
    """
    校验交互对象是否育儿==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[24] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_REARING_1)
def handle_t_rearing_1(character_id: int) -> int:
    """
    校验交互对象是否育儿==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[24] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.INFLATION_0)
def handle_inflation_0(character_id: int) -> int:
    """
    校验角色是否孕肚==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[26] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.INFLATION_1)
def handle_inflation_1(character_id: int) -> int:
    """
    校验角色是否孕肚==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[26] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_INFLATION_0)
def handle_t_inflation_0(character_id: int) -> int:
    """
    校验交互对象是否孕肚==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[26] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_INFLATION_1)
def handle_t_inflation_1(character_id: int) -> int:
    """
    校验交互对象是否孕肚==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[26] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.CUMFLATION_0)
def handle_cumflation_0(character_id: int) -> int:
    """
    校验角色是否精液膨腹==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[32] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.CUMFLATION_1)
def handle_cumflation_1(character_id: int) -> int:
    """
    校验角色是否精液膨腹==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[32] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CUMFLATION_0)
def handle_t_cumflation_0(character_id: int) -> int:
    """
    校验交互对象是否精液膨腹==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[32] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CUMFLATION_1)
def handle_t_cumflation_1(character_id: int) -> int:
    """
    校验交互对象是否精液膨腹==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[32] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.LACTATION_0)
def handle_lactation_0(character_id: int) -> int:
    """
    校验角色是否泌乳==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[27] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.LACTATION_1)
def handle_lactation_1(character_id: int) -> int:
    """
    校验角色是否泌乳==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[27] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_SLEEP)
def handle_pl_action_sleep(character_id: int) -> int:
    """
    校验玩家正在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.pl_pre_behavior_instruce):
        last_behavior = cache.pl_pre_behavior_instruce[-1]
        if last_behavior == constant.Behavior.SLEEP:
            return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_NOT_SLEEP)
def handle_pl_action_not_sleep(character_id: int) -> int:
    """
    校验玩家没有在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_pl_action_sleep(character_id)


@add_premise(constant_promise.Premise.ACTION_SLEEP)
def handle_action_sleep(character_id: int) -> int:
    """
    校验自己正在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.behavior_id == constant.Behavior.SLEEP:
        return 1
    return 0


@add_premise(constant_promise.Premise.ACTION_NOT_SLEEP)
def handle_action_not_sleep(character_id: int) -> int:
    """
    校验自己没有在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.behavior_id == constant.Behavior.SLEEP:
        return 0
    return 1


@add_premise(constant_promise.Premise.T_ACTION_SLEEP)
def handle_t_action_sleep(character_id: int) -> int:
    """
    校验交互对象正在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.behavior.behavior_id == constant.Behavior.SLEEP:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_ACTION_NOT_SLEEP)
def handle_t_action_not_sleep(character_id: int) -> int:
    """
    校验交互对象没有在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.behavior.behavior_id == constant.Behavior.SLEEP:
        return 0
    return 1


@add_premise(constant_promise.Premise.ACTION_REST)
def handle_action_rest(character_id: int) -> int:
    """
    自己正在休息
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.behavior_id == constant.Behavior.REST:
        return 1
    return 0


@add_premise(constant_promise.Premise.ACTION_NOT_REST)
def handle_action_not_rest(character_id: int) -> int:
    """
    自己没有正休息
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_action_rest(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.ACTION_MOVE)
def handle_action_move(character_id: int) -> int:
    """
    自己正在移动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.behavior_id == constant.Behavior.MOVE:
        return 1
    return 0


@add_premise(constant_promise.Premise.ACTION_NOT_MOVE)
def handle_action_not_move(character_id: int) -> int:
    """
    自己没有在移动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_action_move(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.PL_ACTION_MOVE)
def handle_pl_action_move(character_id: int) -> int:
    """
    玩家正在移动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_action_move(0):
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_NOT_MOVE)
def handle_pl_action_not_move(character_id: int) -> int:
    """
    玩家没有在移动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_action_move(0):
        return 0
    return 1


@add_premise(constant_promise.Premise.T_ACTION_MOVE)
def handle_t_action_move(character_id: int) -> int:
    """
    交互对象正在移动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_action_move(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_ACTION_NOT_MOVE)
def handle_t_action_not_move(character_id: int) -> int:
    """
    交互对象没有在移动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_action_move(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.ACTION_WORK_OR_ENTERTAINMENT)
def handle_action_work_or_entertainment(character_id: int) -> int:
    """
    自己正在工作或娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.behavior_id in game_config.config_behavior:
        behavior_data = game_config.config_behavior[character_data.behavior.behavior_id]
        if "工作" in behavior_data.tag or "娱乐" in behavior_data.tag:
            return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_NORMAL)
def handle_pl_action_food_normal(character_id: int) -> int:
    """
    校验食物调味_正常
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SOUR)
def handle_pl_action_food_sour(character_id: int) -> int:
    """
    校验食物调味_酸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SWEET)
def handle_pl_action_food_sweet(character_id: int) -> int:
    """
    校验食物调味_甜
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_BITTER)
def handle_pl_action_food_bitter(character_id: int) -> int:
    """
    校验食物调味_苦
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SPICY)
def handle_pl_action_food_spicy(character_id: int) -> int:
    """
    校验食物调味_辣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SEMEN_HIDDEN)
def handle_pl_action_food_sement_hidden(character_id: int) -> int:
    """
    校验食物调味_巧妙加精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 11:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SEMEN_DIRECT)
def handle_pl_action_food_sement_direct(character_id: int) -> int:
    """
    校验食物调味_直接加精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 12:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_MEDICINE)
def handle_pl_action_food_medicine(character_id: int) -> int:
    """
    校验食物调味_加药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning >= 100:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_BIRTH_CONTROL_AFTER)
def handle_pl_action_food_birth_control_after(character_id: int) -> int:
    """
    校验食物调味_加事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 102:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_PHILTER)
def handle_pl_action_food_philter(character_id: int) -> int:
    """
    校验食物调味_加媚药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 103:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_DIURETICS_ONCE)
def handle_pl_action_food_diuretics_once(character_id: int) -> int:
    """
    校验食物调味_加一次性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 105:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_DIURETICS_PERSISTENT)
def handle_pl_action_food_diuretics_persistent(character_id: int) -> int:
    """
    校验食物调味_加持续性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 106:
        return 1
    return 0

@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SLEEPING_PILLS)
def handle_pl_action_food_sleeping_pills(character_id: int) -> int:
    """
    校验食物调味_加安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 107:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_CLOMID)
def handle_pl_action_food_clomid(character_id: int) -> int:
    """
    校验食物调味_加排卵促进药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.behavior.food_seasoning == 108:
        return 1
    return 0

@add_premise(constant_promise.Premise.AI_EAT_IN_RESTAURANT)
def handle_ai_eat_in_restaurant(character_id: int) -> int:
    """
    AI要在餐厅吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.action_info.eat_food_restaurant >= 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.AI_NOT_EAT_IN_RESTAURANT)
def ai_not_eat_in_restaurant(character_id: int) -> int:
    """
    AI不在餐厅吃饭(即在食堂吃)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_ai_eat_in_restaurant(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.T_BABY_1)
def handle_t_baby_1(character_id: int) -> int:
    """
    校验交互对象是否婴儿==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[101] == 1:
        return 1
    return 0

@add_premise(constant_promise.Premise.SELF_SEMEN_THICK_1)
def handle_self_semen_thick_1(character_id: int) -> int:
    """
    校验自己浓厚精液==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.talent[33]
