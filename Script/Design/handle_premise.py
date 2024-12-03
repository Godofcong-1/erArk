import datetime
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.Design import map_handle, game_time, attr_calculation, character
from Script.Config import normal_config, game_config
from Script.UI.Panel import dirty_panel

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
    elif "CVP" in premise:
        premise_all_value_list = premise.split("_")[1:]
        return handle_comprehensive_value_premise(character_id, premise_all_value_list)
    else:
        return 0


def get_weight_from_premise_dict(premise_dict: dict, character_id: int, weight_all_to_1_flag: bool = False, unconscious_pass_flag: bool = False) -> int:
    """
    遍历前提字典，计算总权重
    Keyword arguments:
    premise_dict -- 前提字典
    character_id -- 角色id
    weight_all_to_1_flag -- 将所有非high的前提权重转换为1，默认为False
    unconscious_h_pass_flag -- 跳过无意识判定，默认为false，不可以跳过
    Return arguments:
    now_weight -- int，总权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    target_character_data = cache.character_data[target_character_id]
    behavior_id = character_data.behavior.behavior_id
    now_weight = 0 # 总权重
    now_premise_data = {} # 记录已经计算过的前提
    # 遍历前提字典
    for premise in premise_dict:
        # 判断是否为权重类空白前提
        if premise[:5] == "high_":
            high_flag = True
        else:
            high_flag = False
        # 是否必须显示
        if not unconscious_pass_flag:
            # 无意识模式判定
            if unconscious_pass_flag == False and handle_unconscious_flag_ge_1(target_character_id):
                # 有技艺tag的行为则直接通过
                status_data = game_config.config_status[behavior_id]
                if _("技艺") in status_data.tag:
                    unconscious_pass_flag = True
                # 需要前提里有无意识的判定
                for now_premise in premise_dict:
                    # 如果前提里有无意识，则正常通过
                    if "unconscious" in now_premise:
                        unconscious_pass_flag = True
                        break
                # 如果没有无意识的前提，则直接返回0
                if not unconscious_pass_flag:
                    now_weight = 0
                    break
        # 已录入前提的判定
        if premise in now_premise_data:
            if not now_premise_data[premise]:
                now_weight = 0
                break
            else:
                if weight_all_to_1_flag and not high_flag:
                    now_weight += 1
                else:
                    now_weight += now_premise_data[premise]
        else:
            # 综合数值前提判定
            if "CVP" in premise:
                premise_all_value_list = premise.split("_")[1:]
                now_add_weight = handle_comprehensive_value_premise(character_id, premise_all_value_list)
                now_premise_data[premise] = now_add_weight
            # 其他正常口上判定
            else:
                now_add_weight = constant.handle_premise_data[premise](character_id)
                now_premise_data[premise] = now_add_weight
            # 计算总权重
            if now_add_weight:
                if weight_all_to_1_flag and not high_flag:
                    now_weight += 1
                else:
                    now_weight += now_add_weight
            else:
                now_weight = 0
                break
    return now_weight


def handle_comprehensive_value_premise(character_id: int, premise_all_value_list: list) -> int:
    """
    综合型基础数值前提
    Keyword arguments:
    character_id -- 角色id
    premise_all_value_list -- 前提的各项数值
    Return arguments:
    int -- 前提权重加成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"debug character_id = {character_id}, premise_all_value_list = {premise_all_value_list}")

    # 进行主体A的判别，A1为自己，A2为交互对象，A3为指定id角色(格式为A3|15)
    if premise_all_value_list[0] == "A1":
        final_character_data = character_data
    elif premise_all_value_list[0] == "A2":
        # 如果没有交互对象，则返回0
        if character_data.target_character_id == character_id:
            return 0
        final_character_data = cache.character_data[character_data.target_character_id]
    elif premise_all_value_list[0][:2] == "A3":
        final_character_adv = int(premise_all_value_list[0][3:])
        final_character_id = 0
        # 遍历拥有的全角色，找到对应的角色
        for character_id in cache.npc_id_got:
            tem_character_data = cache.character_data[character_id]
            if tem_character_data.adv == final_character_adv:
                final_character_id = character_id
                final_character_data = cache.character_data[character_id]
                break
        # 如果还没拥有该角色，则返回0
        if final_character_id == 0:
            return 0

    # 进行数值B的判别,A能力,T素质,Time时间,J宝珠,E经验,S状态,F好感度,Flag作者用flag,X信赖,G攻略程度,Instruct指令,Son子嵌套事件,OtherChara其他角色在场
    if len(premise_all_value_list[1]) > 1 and "Time" not in premise_all_value_list[1]:
        type_son_id = int(premise_all_value_list[1].split("|")[1])
    if "Son" in premise_all_value_list[1]:
        return 0
    if premise_all_value_list[1][0] == "A":
        final_value = final_character_data.ability[type_son_id]
    elif premise_all_value_list[1][0] == "T":
        if "Time" in premise_all_value_list[1]:
            final_value = final_character_data.behavior.start_time.hour
        else:
            final_value = final_character_data.talent[type_son_id]
    elif premise_all_value_list[1][0] == "J":
        final_value = final_character_data.juel[type_son_id]
    elif premise_all_value_list[1][0] == "E":
        final_value = final_character_data.experience[type_son_id]
    elif premise_all_value_list[1][0] == "S":
        final_value = final_character_data.status_data[type_son_id]
    elif premise_all_value_list[1][0] == "F":
        if "Flag" in premise_all_value_list[1]:
            final_character_data.author_flag.chara_int_flag_dict.setdefault(type_son_id, 0)
            final_value = final_character_data.author_flag.chara_int_flag_dict[type_son_id]
        else:
            final_value = final_character_data.favorability[0]
    elif premise_all_value_list[1][0] == "X":
        final_value = final_character_data.trust

    # 进行方式C和数值D的判别
    judge_value = int(premise_all_value_list[3])
    # print(f"debug final_value = {final_value}, judge_value = {judge_value}")

    # 攻略程度进行单独计算
    if premise_all_value_list[1][0] == "G":
        if judge_value > 0:
            all_talent_list = [201,202,203,204]
            talent_id_index = 200 + judge_value
        elif judge_value < 0:
            all_talent_list = [211,212,213,214]
            talent_id_index = 210 - judge_value
        else:
            return 0
        # 攻略程度的运算符判定
        if premise_all_value_list[2] == "G":
           # 获取all_talent_list中所有比talent_id_index大的作为一个新列表
            new_talent_list = [i for i in all_talent_list if i > talent_id_index]
        elif premise_all_value_list[2] == "L":
            new_talent_list = [i for i in all_talent_list if i < talent_id_index]
        elif premise_all_value_list[2] == "E":
            new_talent_list = [i for i in all_talent_list if i == talent_id_index]
        elif premise_all_value_list[2] == "GE":
            new_talent_list = [i for i in all_talent_list if i >= talent_id_index]
        elif premise_all_value_list[2] == "LE":
            new_talent_list = [i for i in all_talent_list if i <= talent_id_index]
        elif premise_all_value_list[2] == "NE":
            new_talent_list = [i for i in all_talent_list if i != talent_id_index]
        # 最后判定
        for talent_id in new_talent_list:
            if final_character_data.talent[talent_id]:
                return 1
        return 0

    # 前指令的单独计算
    if premise_all_value_list[1][0] == "I":
        if "Instruct" in premise_all_value_list[1]:
            len_pre_status = len(cache.pl_pre_status_instruce)
            type_son_id = int(premise_all_value_list[1].split("|")[1])
            # 指令计数
            count = 0
            for i in range(len_pre_status):
                last_cmd = cache.pl_pre_status_instruce[len_pre_status - 1 - i]
                # 跳过当前指令
                if count == 0:
                    count += 1
                    continue
                if last_cmd == type_son_id:
                    # 判定是否为该指令
                    if premise_all_value_list[2] == "E":
                        return 1
                    if premise_all_value_list[2] == "NE":
                        return 0
                if premise_all_value_list[2] == "E":
                    return 0
                if premise_all_value_list[2] == "NE":
                    return 1
            return 0

    # 其他角色在场的判定
    if premise_all_value_list[1][0] == "O":
        if "OtherChara" in premise_all_value_list[1]:
            if character_data.position == final_character_data.position:
                return 1 if judge_value >= 1 else 0
            else:
                return 0 if judge_value >= 1 else 1

    # 正常的运算符判定
    if premise_all_value_list[2] == "G":
        if final_value > judge_value:
            # print(f"debug 成功进入G判定，返回值为1")
            return 1
    elif premise_all_value_list[2] == "L":
        if final_value < judge_value:
            return 1
    elif premise_all_value_list[2] == "E":
        if final_value == judge_value:
            return 1
    elif premise_all_value_list[2] == "GE":
        if final_value >= judge_value:
            return 1
    elif premise_all_value_list[2] == "LE":
        if final_value <= judge_value:
            return 1
    elif premise_all_value_list[2] == "NE":
        if final_value != judge_value:
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
    if character_data.behavior.start_time is not None:
        if character_data.behavior.start_time.hour in {0, 1, 2, 3, 4, 5, 22, 23}:
            now_hour = character_data.behavior.start_time.hour if character_data.behavior.start_time.hour > 20 else character_data.behavior.start_time.hour + 24
            # print(f"debug {character_data.name}的睡觉前提判定，now_hour = {now_hour}，返回值为{(now_hour-21) *100}")
            return (now_hour - 21) * 100
    value = character_data.tired_point / 160
    if value > 0.74:
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
def handle_morning_salutation_time(character_id: int) -> int:
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
    if game_time.judge_date_big_or_small(end_time, now_time):
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


@add_premise(constant_promise.Premise.HAVE_FOOD)
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


@add_premise(constant_promise.Premise.NOT_HAVE_FOOD)
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
        if character_data.food_bag[food_id]:
            return 0
    return food_index


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


@add_premise(constant_promise.Premise.HAVE_MOVED)
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
    NPC需要进行一次5分钟的等待（wait_flag = 1)
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
    NPC距离上次战斗训练已经超过两天了
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
    NPC今天还没有洗澡
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
    NPC今天已经洗过澡了
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
    NPC今天还没有起床
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time = cache.game_time
    wake_up_time = character_data.action_info.wake_time
    if wake_up_time.day != now_time.day:
        return 1
    return 0


@add_premise(constant_promise.Premise.FIRST_KISS_IN_TODAY)
def handle_first_kiss_in_today(character_id: int) -> int:
    """
    自己今天失去了初吻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if game_time.count_day_for_datetime(character_data.first_record.first_kiss_time, cache.game_time) == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.FIRST_SEX_IN_TODAY)
def handle_first_sex_in_today(character_id: int) -> int:
    """
    自己今天失去了V处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if game_time.count_day_for_datetime(character_data.first_record.first_sex_time, cache.game_time) == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.FIRST_A_SEX_IN_TODAY)
def handle_first_a_sex_in_today(character_id: int) -> int:
    """
    自己今天失去了A处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if game_time.count_day_for_datetime(character_data.first_record.first_a_sex_time, cache.game_time) == 0:
        return 1
    return 0


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


@add_premise(constant_promise.Premise.HIGH_1)
def handle_high_1(character_id: int) -> int:
    """
    优先度为1的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 1


@add_premise(constant_promise.Premise.HIGH_2)
def handle_high_2(character_id: int) -> int:
    """
    优先度为2的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 2


@add_premise(constant_promise.Premise.HIGH_5)
def handle_high_5(character_id: int) -> int:
    """
    优先度为5的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 5


@add_premise(constant_promise.Premise.HIGH_10)
def handle_high_10(character_id: int) -> int:
    """
    优先度为10的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 10


@add_premise(constant_promise.Premise.HIGH_999)
def handle_high_999(character_id: int) -> int:
    """
    优先度为999的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 999


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_LOW_OBSCENITY)
def handle_instruct_judge_low_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值足以轻度性骚扰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id:
        if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"), not_draw_flag = True)[0]:
            return 1
    return 0


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_HIGH_OBSCENITY)
def handle_instruct_judge_high_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值足以重度性骚扰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id:
        if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"), not_draw_flag = True)[0]:
            return 1
    return 0


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_H)
def handle_instruct_judge_h(character_id: int) -> int:
    """
    口上用：当前实行值足以邀请H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id:
        if character.calculation_instuct_judege(0, character_data.target_character_id, _("H模式"), not_draw_flag = True)[0]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HAVE_CHARA_DIY_INSTRUCT)
def handle_target_have_chara_diy_instruct(character_id: int) -> int:
    """
    交互对象有角色自定义指令且至少有一个序号0的子事件满足全前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.UI.Panel import event_option_panel
    len_son_event_list, son_event_list = event_option_panel.get_target_chara_diy_instruct(character_id)
    if len_son_event_list:
        return 1
    return 0


@add_premise(constant_promise.Premise.NORMAL_ALL)
def handle_normal_all(character_id: int) -> int:
    """
    没有任何异常的绝对正常状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_1_2_4)
def handle_normal_1_2_4(character_id: int) -> int:
    """
    124正常的普通状态
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n包括2:临盆、产后、监禁
    \n包括4:大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_4(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2_3_4)
def handle_normal_2_3_4(character_id: int) -> int:
    """
    234正常的普通状态
    \n包括2:临盆、产后、监禁
    \n包括3:助理、跟随模式下
    \n包括4:大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2_5_6)
def handle_normal_2_5_6(character_id: int) -> int:
    """
    256正常的普通状态
    \n包括2:临盆、产后、监禁
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_1)
def handle_normal_1(character_id: int) -> int:
    """
    1正常的普通状态
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
        handle_rest_flag_1(character_id)
        or handle_sleep_flag_1(character_id)
        or handle_pee_flag_1(character_id)
        or handle_eat_food_flag_ge_1(character_id)
        or handle_shower_flag_123(character_id)
        or handle_milk_flag_1(character_id)
        or handle_masturebate_flag_g_0(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_2)
def handle_normal_2(character_id: int) -> int:
    """
    \n2:AI行动基本停止：临盆、产后、监禁
    \n包括2:临盆、产后、监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
        handle_parturient_1(character_id)
        or handle_postpartum_1(character_id)
        or handle_imprisonment_1(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_3)
def handle_normal_3(character_id: int) -> int:
    """
    3正常的普通状态
    \n3:助理或跟随：助理、跟随模式下
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
         handle_is_assistant(character_id)
        or handle_is_follow(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_4)
def handle_normal_4(character_id: int) -> int:
    """
    4正常的普通状态
    \n4:服装异常：大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
        handle_cloth_off(character_id)
        or handle_cloth_most_off(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_5)
def handle_normal_5(character_id: int) -> int:
    """
    5正常的普通状态
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
        (handle_sleep_level_0(character_id) and (handle_action_sleep(character_id) or handle_unconscious_flag_1(character_id)))
        or handle_unconscious_flag_4(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_6)
def handle_normal_6(character_id: int) -> int:
    """
    6正常的普通状态
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
         (handle_sleep_level_1(character_id) and (handle_action_sleep(character_id) or handle_unconscious_flag_1(character_id)))
        or (handle_sleep_level_2(character_id) and (handle_action_sleep(character_id) or handle_unconscious_flag_1(character_id)))
        or (handle_sleep_level_3(character_id) and (handle_action_sleep(character_id) or handle_unconscious_flag_1(character_id)))
        or handle_unconscious_flag_5(character_id)
        or (handle_time_stop_on(character_id) or handle_unconscious_flag_3(character_id))
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_7)
def handle_normal_7(character_id: int) -> int:
    """
    7正常的普通状态
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if(
        handle_be_bagged_1(character_id)
        or handle_field_commission_1(character_id)
        or handle_t_baby_1(character_id)
        or handle_in_diplomatic_visit_1_and_other_country(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_NORMAL_6)
def handle_t_normal_6(character_id: int) -> int:
    """
    交互对象6正常的普通状态
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_normal_6(target_chara_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2_4)
def handle_normal_2_4(character_id: int) -> int:
    """
    24正常的普通状态
    \n包括2:临盆、产后、监禁
    \n包括4:大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_4(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_267)
def handle_normal_267(character_id: int) -> int:
    """
    267正常（可能基础异常、AI跟随、服装异常或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2467)
def handle_normal_2467(character_id: int) -> int:
    """
    2467正常（可能基础异常、AI跟随或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_2467)
def handle_t_normal_2467(character_id: int) -> int:
    """
    交互对象2467正常（可能基础异常、AI跟随或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_2(target_chara_id) and 
        handle_normal_4(target_chara_id) and 
        handle_normal_6(target_chara_id) and 
        handle_normal_7(target_chara_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_23467)
def handle_normal_23467(character_id: int) -> int:
    """
    23467正常（可能基础异常或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n3:助理或跟随：助理、跟随模式下
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_24567)
def handle_normal_24567(character_id: int) -> int:
    """
    24567正常（可能基础异常、AI跟随）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_24567)
def handle_t_normal_24567(character_id: int) -> int:
    """
    交互对象24567正常（可能基础异常、AI跟随）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_2(target_chara_id) and 
        handle_normal_4(target_chara_id) and 
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id) and 
        handle_normal_7(target_chara_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_124567)
def handle_normal_124567(character_id: int) -> int:
    """
    124567正常（可能基础异常、AI跟随）
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_1267)
def handle_normal_1267(character_id: int) -> int:
    """
    1267正常（可能AI跟随、服装异常或意识模糊）
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n2:AI行动基本停止：临盆、产后、监禁
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_123467)
def handle_normal_123467(character_id: int) -> int:
    """
    123467正常（可能意识模糊）
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n2:AI行动基本停止：临盆、产后、监禁
    \n3:助理或跟随：助理、跟随模式下
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_2)
def handle_t_normal_2(character_id: int) -> int:
    """
    交互对象2正常的普通状态
    \n包括2:临盆、产后、监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_normal_2(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNNORMAL)
def handle_unnormal(character_id: int) -> int:
    """
    有特殊需求的异常状态
    \n包括1~7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and
        handle_normal_7(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.UNNORMAL_2)
def handle_unnormal_2(character_id: int) -> int:
    """
    2异常
    \n2:AI行动基本停止：临盆、产后、监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.UNNORMAL_27)
def handle_unnormal_27(character_id: int) -> int:
    """
    27异常（AI停止或离线）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_7(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_NORMAL_5_6)
def handle_t_normal_5_6(character_id: int) -> int:
    """
    交互对象56正常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_UNNORMAL_5_6)
def handle_t_unnormal_5_6(character_id: int) -> int:
    """
    交互对象5异常或6异常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_UNNORMAL_6)
def handle_t_unnormal_6(character_id: int) -> int:
    """
    交互对象6异常
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_normal_6(target_chara_id):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.UNNORMAL_567)
def handle_unnormal_567(character_id: int) -> int:
    """
    自身5或6或7异常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG)
def handle_t_normal_256_or_unconscious_flag(character_id: int) -> int:
    """
    交互对象256正常或无意识
    \n包括2:临盆、产后、监禁
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_2(target_chara_id) and 
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 1
    if target_data.sp_flag.unconscious_h != 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NORMAL_56_OR_UNCONSCIOUS_FLAG)
def handle_t_normal_56_or_unconscious_flag(character_id: int) -> int:
    """
    交互对象56正常或无意识
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 1
    if target_data.sp_flag.unconscious_h != 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UNNORMAL_567)
def handle_t_unnormal_567(character_id: int) -> int:
    """
    交互对象5或6或7异常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id) and 
        handle_normal_7(target_chara_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_ALL_EXCEPT_SPECIAL_HYPNOSIS)
def handle_normal_all_except_special_hypnosis(character_id: int) -> int:
    """
    没有任何异常的普通状态或被空气或体控催眠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    elif (
        handle_unconscious_flag_5(character_id) or
        handle_unconscious_flag_6(character_id)
        ):
        return 1
    else:
        return 0


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


@add_premise(constant_promise.Premise.IMPRISONMENT_0)
def handle_imprisonment_0(character_id: int) -> int:
    """
    自身没有被监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.imprisonment == 1:
        return 0
    else:
        return 1


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
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.imprisonment == 1:
        return 0
    else:
        return 1


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
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.imprisonment == 1:
        return 1
    else:
        return 0


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
    自身要自慰状态(含两类位置)
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
    if not handle_ask_masturbation_before_sleep(character_id):
        return 1
    elif handle_masturebate_bofore_sleep_flag_2(character_id):
        return 1
    return 0


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


@add_premise(constant_promise.Premise.HP_LOW)
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


@add_premise(constant_promise.Premise.HP_HIGH)
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


@add_premise(constant_promise.Premise.HP_MAX)
def handle_hp_max(character_id: int) -> int:
    """
    角色自身体力等于100%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.hit_point / character_data.hit_point_max
    if value >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MP_0)
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
        return_value = max(1, character_data.hit_point_max - character_data.hit_point)
        return return_value
    else:
        return 0


@add_premise(constant_promise.Premise.MP_LOW)
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


@add_premise(constant_promise.Premise.MP_HIGH)
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


@add_premise(constant_promise.Premise.MP_MAX)
def handle_mp_max(character_id: int) -> int:
    """
    自身气力等于100%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point / character_data.mana_point_max
    if value >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HP_OR_MP_LOW)
def handle_hp_or_mp_low(character_id: int) -> int:
    """
    自身体力或气力有一项低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    hp_value = character_data.hit_point / character_data.hit_point_max
    mp_value = character_data.mana_point / character_data.mana_point_max
    if hp_value < 0.3:
        return 1
    elif mp_value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HP_OR_MP_GE_80)
def handle_hp_or_mp_ge_80(character_id: int) -> int:
    """
    自身体力或气力有一项低于80%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    hp_value = character_data.hit_point / character_data.hit_point_max
    mp_value = character_data.mana_point / character_data.mana_point_max
    if hp_value < 0.8:
        return 1
    elif mp_value < 0.8:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HP_LOW)
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


@add_premise(constant_promise.Premise.TARGET_HP_HIGH)
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


@add_premise(constant_promise.Premise.TARGET_HP_NE_1)
def handle_target_hp_ne_1(character_id: int) -> int:
    """
    交互对象体力不等于1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.hit_point > 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MP_0)
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


@add_premise(constant_promise.Premise.TARGET_MP_LOW)
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


@add_premise(constant_promise.Premise.TARGET_MP_HIGH)
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


@add_premise(constant_promise.Premise.SELF_AND_TARGET_HP_GE_70)
def handle_self_and_target_hp_ge_70(character_id: int) -> int:
    """
    自身和交互对象体力都高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value1 = character_data.hit_point / character_data.hit_point_max
    value2 = target_data.hit_point / target_data.hit_point_max
    if value1 > 0.7 and value2 > 0.7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_LE_0)
def handle_tired_le_0(character_id: int) -> int:
    """
    疲劳条≤0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value <= 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_10)
def handle_tired_ge_10(character_id: int) -> int:
    """
    疲劳条≥10%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value >= 0.1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_50)
def handle_tired_ge_50(character_id: int) -> int:
    """
    疲劳条≥50%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value >= 0.5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_LE_74)
def handle_tired_le_74(character_id: int) -> int:
    """
    疲劳条≤74%，全指令自由
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value <= 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_75)
def handle_tired_ge_75(character_id: int) -> int:
    """
    疲劳条≥75%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value > 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_LE_84)
def handle_tired_le_84(character_id: int) -> int:
    """
    疲劳条≤84%，自由活动的极限
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value <= 0.84:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_85)
def handle_tired_ge_85(character_id: int) -> int:
    """
    疲劳条≥85%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value > 0.84:
        return character_data.tired_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_L_100)
def handle_tired_l_100(character_id: int) -> int:
    """
    疲劳条<100%，还不至于当场爆睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value < 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_100)
def handle_tired_100(character_id: int) -> int:
    """
    疲劳条100%，当场爆睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value >= 1:
        return character_data.tired_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_GE_50)
def handle_t_tired_ge_50(character_id: int) -> int:
    """
    交互对象疲劳条≥50%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value >= 0.5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_LE_74)
def handle_t_tired_le_74(character_id: int) -> int:
    """
    交互对象疲劳条≤74%，全指令自由
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value <= 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_GE_75)
def handle_t_tired_ge_75(character_id: int) -> int:
    """
    交互对象疲劳条≥75%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value > 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_LE_84)
def handle_t_tired_le_84(character_id: int) -> int:
    """
    交互对象疲劳条≤84%，自由活动的极限
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value <= 0.84:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_GE_85)
def handle_t_tired_ge_85(character_id: int) -> int:
    """
    交互对象疲劳条≥85%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value > 0.84:
        return target_data.tired_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_100)
def handle_t_tired_100(character_id: int) -> int:
    """
    交互对象疲劳条100%，当场爆睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value >= 1:
        return 1
    else:
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


@add_premise(constant_promise.Premise.COOK_1)
def handle_cook_1(character_id: int) -> int:
    """
    校验角色是否料理技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_2)
def handle_cook_2(character_id: int) -> int:
    """
    校验角色是否料理技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_3)
def handle_cook_3(character_id: int) -> int:
    """
    校验角色是否料理技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_4)
def handle_cook_4(character_id: int) -> int:
    """
    校验角色是否料理技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_LE_1)
def handle_cook_le_1(character_id: int) -> int:
    """
    校验角色是否料理技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_GE_3)
def handle_cook_ge_3(character_id: int) -> int:
    """
    校验角色是否料理技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_GE_5)
def handle_cook_ge_3(character_id: int) -> int:
    """
    校验角色是否料理技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_1)
def handle_music_1(character_id: int) -> int:
    """
    校验角色是否音乐技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_2)
def handle_music_2(character_id: int) -> int:
    """
    校验角色是否音乐技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_3)
def handle_music_3(character_id: int) -> int:
    """
    校验角色是否音乐技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_4)
def handle_music_4(character_id: int) -> int:
    """
    校验角色是否音乐技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_LE_1)
def handle_music_le_1(character_id: int) -> int:
    """
    校验角色是否音乐技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_GE_3)
def handle_music_ge_3(character_id: int) -> int:
    """
    校验角色是否音乐技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_GE_5)
def handle_music_ge_3(character_id: int) -> int:
    """
    校验角色是否音乐技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_GE_2_LE_4)
def handle_music_ge_2_le_4(character_id: int) -> int:
    """
    校验自身音乐技能>=2,<=4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 2 <= character_data.ability[44] <= 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.TECHNIQUE_GE_3)
def handle_technique_ge_3(character_id: int) -> int:
    """
    校验角色是否技巧技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[30] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TECHNIQUE_GE_5)
def handle_technique_ge_3(character_id: int) -> int:
    """
    校验角色是否技巧技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[30] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_DESIRE_GE_5)
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
    if target_data.ability[33] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_DESIRE_GE_7)
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
    if target_data.ability[33] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.TALK_LE_1)
def handle_talk_le_1(character_id: int) -> int:
    """
    校验角色是否话术技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[40] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TALK_GE_3)
def handle_talk_ge_3(character_id: int) -> int:
    """
    校验角色是否话术技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[40] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TALK_GE_5)
def handle_talk_ge_5(character_id: int) -> int:
    """
    校验角色是否话术技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[40] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TALK_LE_1)
def handle_t_talk_le_1(character_id: int) -> int:
    """
    校验交互对象是否话术技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[40] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TALK_GE_3)
def handle_t_talk_ge_3(character_id: int) -> int:
    """
    校验交互对象是否话术技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[40] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TALK_GE_5)
def handle_t_talk_ge_5(character_id: int) -> int:
    """
    校验交互对象是否话术技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[40] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_1)
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
    if target_data.ability[43] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_2)
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
    if target_data.ability[43] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_3)
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
    if target_data.ability[43] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_4)
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
    if target_data.ability[43] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_LE_1)
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
    if target_data.ability[43] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_LE_3)
def handle_target_cook_le_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能<=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] <= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_GE_3)
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
    if target_data.ability[43] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_G_3)
def handle_target_cook_g_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_GE_5)
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
    if target_data.ability[43] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_1)
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
    if target_data.ability[44] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_2)
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
    if target_data.ability[44] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_3)
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
    if target_data.ability[44] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_4)
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
    if target_data.ability[44] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_LE_1)
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
    if target_data.ability[44] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_GE_3)
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
    if target_data.ability[44] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_GE_5)
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
    if target_data.ability[44] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_8)
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
    if target_data.ability[32] == 8:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_LE_1)
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
    if target_data.ability[32] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_GE_3)
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
    if target_data.ability[32] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_GE_5)
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
    if target_data.ability[32] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_TECHNIQUE_GE_3)
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
    if target_data.ability[30] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_TECHNIQUE_GE_5)
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
    if target_data.ability[30] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_1)
def handle_t_yield_mark_1(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_2)
def handle_t_yield_mark_2(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_3)
def handle_t_yield_mark_3(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_GE_1)
def handle_t_yield_mark_ge_1(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_LE_2)
def handle_t_yield_mark_le_2(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印<=2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] <= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_1)
def handle_t_finger_tec_ge_1(character_id: int) -> int:
    """
    校验交互对象是否指技>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_3)
def handle_t_finger_tec_ge_3(character_id: int) -> int:
    """
    校验交互对象是否指技>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_5)
def handle_t_finger_tec_ge_5(character_id: int) -> int:
    """
    校验交互对象是否指技>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_7)
def handle_t_finger_tec_ge_7(character_id: int) -> int:
    """
    校验交互对象是否指技>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_0)
def handle_t_finger_tec_0(character_id: int) -> int:
    """
    校验交互对象是否指技==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_L_3)
def handle_t_finger_tec_l_3(character_id: int) -> int:
    """
    校验交互对象是否指技<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_L_7)
def handle_t_finger_tec_l_7(character_id: int) -> int:
    """
    校验交互对象是否指技<7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] < 7:
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


@add_premise(constant_promise.Premise.SELF_FALL)
def handle_self_fall(character_id: int) -> int:
    """
    自己有陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {201, 202, 203, 204, 211, 212, 213, 214}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_FALL)
def handle_self_not_fall(character_id: int) -> int:
    """
    自己无陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_fall(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_FALL_1)
def handle_self_fall_1(character_id: int) -> int:
    """
    自己有1级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {201, 211}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_2)
def handle_self_fall_2(character_id: int) -> int:
    """
    自己有2级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {202, 212}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_3)
def handle_self_fall_3(character_id: int) -> int:
    """
    自己有3级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {203, 213}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_4)
def handle_self_fall_4(character_id: int) -> int:
    """
    自己有4级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {204, 214}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_LOVE)
def handle_self_fall_love(character_id: int) -> int:
    """
    自己有爱情系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {201, 202, 203, 204}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_OBEY)
def handle_self_fall_obey(character_id: int) -> int:
    """
    自己有隶属系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {211, 212, 213, 214}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_FALL)
def handle_target_not_fall(character_id: int) -> int:
    """
    交互对象无陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_fall(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_FALL)
def handle_target_fall(character_id: int) -> int:
    """
    交互对象有陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_fall(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_1)
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
    if target_data.talent[201]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_2)
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
    if target_data.talent[202]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_3)
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
    if target_data.talent[203]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_4)
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
    if target_data.talent[204]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_GE_1)
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
    for i in {201, 202, 203, 204}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_GE_2)
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
    for i in {202, 203, 204}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_GE_3)
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
    for i in {203, 204}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_LE_2)
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
    for i in {201, 202}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_0_OR_LE_1)
def handle_target_love_0_or_le_1(character_id: int) -> int:
    """
    交互对象无陷落或爱情系<=思慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_love_1(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_0_OR_LE_2)
def handle_target_love_0_or_le_2(character_id: int) -> int:
    """
    交互对象无陷落或爱情系<=恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_love_le_2(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_1)
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
    if target_data.talent[211]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_2)
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
    if target_data.talent[212]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_3)
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
    if target_data.talent[213]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_4)
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
    if target_data.talent[214]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_GE_1)
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
    for i in {211, 212, 213, 214}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_GE_2)
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
    for i in {212, 213, 214}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_GE_3)
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
    for i in {213, 214}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_LE_2)
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
    for i in {211, 212}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_0_OR_LE_1)
def handle_target_obey_0_or_le_1(character_id: int) -> int:
    """
    交互对象无陷落或隶属系==屈从
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_obey_1(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_0_OR_LE_2)
def handle_target_obey_0_or_le_2(character_id: int) -> int:
    """
    交互对象无陷落或隶属系<=驯服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_obey_le_2(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_FIRST_KISS)
def handle_have_first_kiss(character_id: int) -> int:
    """
    玩家保有初吻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.talent[4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NO_FIRST_KISS)
def handle_no_first_kiss(character_id: int) -> int:
    """
    玩家未保有初吻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.talent[4]:
        return 0
    return 1


@add_premise(constant_promise.Premise.PL_HAVE_VIRGIN)
def handle_pl_have_virgin(character_id: int) -> int:
    """
    校验玩家是否是童贞
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.talent[5]:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_NO_VIRGIN)
def handle_pl_no_virgin(character_id: int) -> int:
    """
    玩家非童贞
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.talent[5]:
        return 0
    return 1


@add_premise(constant_promise.Premise.HAVE_A_VIRGIN)
def handle_have_a_virgin(character_id: int) -> int:
    """
    校验玩家是否是A处
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.talent[1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NO_A_VIRGIN)
def handle_no_a_virgin(character_id: int) -> int:
    """
    玩家非A处
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    if character_data.talent[1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_NO_FIRST_KISS)
def handle_target_no_first_kiss(character_id: int) -> int:
    """
    校验交互对象是否初吻不在了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_target_have_first_kiss(character_id)


@add_premise(constant_promise.Premise.TARGET_HAVE_FIRST_KISS)
def handle_target_have_first_kiss(character_id: int) -> int:
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


@add_premise(constant_promise.Premise.NO_VIRGIN)
def handle_no_virgin(character_id: int) -> int:
    """
    校验自己是否非处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[0] == 0


@add_premise(constant_promise.Premise.HAVE_VIRGIN)
def handle_have_virgin(character_id: int) -> int:
    """
    校验自己是处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_no_virgin(character_id)


@add_premise(constant_promise.Premise.TARGET_NO_VIRGIN)
def handle_target_no_virgin(character_id: int) -> int:
    """
    校验交互对象是否非处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_target_have_virgin(character_id)


@add_premise(constant_promise.Premise.TARGET_HAVE_VIRGIN)
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
    return target_data.talent[0] == 1


@add_premise(constant_promise.Premise.TARGET_NO_A_VIRGIN)
def handle_target_no_a_virgin(character_id: int) -> int:
    """
    校验交互对象是否非A处女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_target_have_a_virgin(character_id)


@add_premise(constant_promise.Premise.TARGET_HAVE_A_VIRGIN)
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
    return target_data.talent[1] == 1


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


@add_premise(constant_promise.Premise.PATIENT_WAIT)
def handle_patient_wait(character_id: int) -> int:
    """
    有患者正等待就诊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.patient_now > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.NEW_NPC_WAIT)
def handle_new_npc_wait(character_id: int) -> int:
    """
    有已招募待确认的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.rhodes_island.recruited_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_OFFICE_WORK_NEED_TO_DO)
def handle_have_office_work_need_to_do(character_id: int) -> int:
    """
    有需要处理的公务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.office_work > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PINK_CERTIFICATE_G_10)
def handle_pink_certificate_g_10(character_id: int) -> int:
    """
    拥有粉红凭证数量大于10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.materials_resouce[4] > 10:
        return 1
    return 0


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


@add_premise(constant_promise.Premise.SCENE_ONLY_ONE)
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


@add_premise(constant_promise.Premise.SELF_CHEST_IS_CLIFF)
def handle_self_chest_is_cliff(character_id: int) -> int:
    """
    自己胸部大小是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[121]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_CLIFF)
def handle_target_chest_is_cliff(character_id: int) -> int:
    """
    交互对象胸部大小是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_cliff(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_SMALL)
def handle_self_chest_is_small(character_id: int) -> int:
    """
    自己胸部大小是贫乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[122]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_SMALL)
def handle_target_chest_is_small(character_id: int) -> int:
    """
    交互对象胸部大小是贫乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_small(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_NORMAL)
def handle_self_chest_is_normal(character_id: int) -> int:
    """
    自己胸部大小是普乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[123]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_NORMAL)
def handle_target_chest_is_normal(character_id: int) -> int:
    """
    交互对象胸部大小是普乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_normal(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_BIG)
def handle_self_chest_is_big(character_id: int) -> int:
    """
    自己胸部大小是巨乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[124]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_BIG)
def handle_target_chest_is_big(character_id: int) -> int:
    """
    交互对象胸部大小是巨乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_big(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_SUPER)
def handle_self_chest_is_super(character_id: int) -> int:
    """
    自己胸部大小是爆乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[125]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_SUPER)
def handle_target_chest_is_super(character_id: int) -> int:
    """
    交互对象胸部大小是爆乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_super(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_BUTTOCKS_IS_SMALL)
def handle_target_buttock_is_small(character_id: int) -> int:
    """
    交互对象屁股大小是小臀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[126]


@add_premise(constant_promise.Premise.TARGET_BUTTOCKS_IS_NORMAL)
def handle_target_buttock_is_normal(character_id: int) -> int:
    """
    交互对象胸部大小是普臀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[127]


@add_premise(constant_promise.Premise.TARGET_BUTTOCKS_IS_BIG)
def handle_target_buttock_is_big(character_id: int) -> int:
    """
    交互对象胸部大小是巨臀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[128]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_EARS)
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
    return not target_data.talent[111]


@add_premise(constant_promise.Premise.TARGET_HAVE_EARS)
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
    return target_data.talent[111]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_HORN)
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
    return not target_data.talent[112]


@add_premise(constant_promise.Premise.TARGET_HAVE_HORN)
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
    return target_data.talent[112]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_TAIL)
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
    return not target_data.talent[113]


@add_premise(constant_promise.Premise.TARGET_HAVE_TAIL)
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
    return target_data.talent[113]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_RING)
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
    return not target_data.talent[114]


@add_premise(constant_promise.Premise.TARGET_HAVE_RING)
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
    return target_data.talent[114]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_WING)
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
    return not target_data.talent[115]


@add_premise(constant_promise.Premise.TARGET_HAVE_WING)
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
    return target_data.talent[115]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_TENTACLE)
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
    return not target_data.talent[116]


@add_premise(constant_promise.Premise.TARGET_HAVE_TENTACLE)
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
    return target_data.talent[116]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_CAR)
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
    return not target_data.talent[117]


@add_premise(constant_promise.Premise.TARGET_HAVE_CAR)
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
    return target_data.talent[117]


@add_premise(constant_promise.Premise.TARGET_NOT_PATIENT)
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


@add_premise(constant_promise.Premise.TARGET_IS_PATIENT)
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


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_CRYSTAL)
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


@add_premise(constant_promise.Premise.TARGET_HAVE_CRYSTAL)
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


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_DILIGENT)
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
    return not target_data.talent[271]


@add_premise(constant_promise.Premise.TARGET_HAVE_DILIGENT)
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
    return target_data.talent[271]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_LAZY)
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
    return not target_data.talent[272]


@add_premise(constant_promise.Premise.TARGET_HAVE_LAZY)
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
    return target_data.talent[272]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_FRAGILE)
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
    return not target_data.talent[273]


@add_premise(constant_promise.Premise.TARGET_HAVE_FRAGILE)
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
    return target_data.talent[273]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_FORCEFUL)
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
    return not target_data.talent[274]


@add_premise(constant_promise.Premise.TARGET_HAVE_FORCEFUL)
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
    return target_data.talent[274]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_ENTHUSIACTIC)
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
    return not target_data.talent[275]


@add_premise(constant_promise.Premise.TARGET_HAVE_ENTHUSIACTIC)
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
    return target_data.talent[275]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_ALONE)
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
    return not target_data.talent[276]


@add_premise(constant_promise.Premise.TARGET_HAVE_ALONE)
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
    return target_data.talent[276]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_SHAME)
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
    return not target_data.talent[277]


@add_premise(constant_promise.Premise.TARGET_HAVE_SHAME)
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
    return target_data.talent[277]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_OPEN)
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
    return not target_data.talent[278]


@add_premise(constant_promise.Premise.TARGET_HAVE_OPEN)
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
    return target_data.talent[278]


@add_premise(constant_promise.Premise.AT_LEAST_ONE_ARTS_ON)
def handle_at_least_one_arts_on(character_id: int) -> int:
    """
    至少有一种源石技艺开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 催眠
    if handle_target_in_hypnosis(character_id):
        return 1
    # 透视
    if handle_penetrating_vision_on(character_id):
        return 1
    # 时停
    if handle_time_stop_on(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PRIMARY_HYPNOSIS)
def handle_primary_hypnosis(character_id: int) -> int:
    """
    自己拥有初级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[331]


@add_premise(constant_promise.Premise.INTERMEDIATE_HYPNOSIS)
def handle_intermediate_hypnosis(character_id: int) -> int:
    """
    自己拥有中级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[332]


@add_premise(constant_promise.Premise.ADVANCED_HYPNOSIS)
def handle_advanced_hypnosis(character_id: int) -> int:
    """
    自己拥有高级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[333]


@add_premise(constant_promise.Premise.SPECIAL_HYPNOSIS)
def handle_special_hypnosis(character_id: int) -> int:
    """
    自己拥有特级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[334]


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_0)
def handle_target_hypnosis_0(character_id: int) -> int:
    """
    交互对象的被催眠程度为0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.hypnosis.hypnosis_degree == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_NE_0)
def handle_target_hypnosis_ne_0(character_id: int) -> int:
    """
    交互对象的被催眠程度不是0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_target_hypnosis_0(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_HYPNOSIS)
def handle_target_has_been_hypnosis(character_id: int) -> int:
    """
    交互对象有至少一种被催眠素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    for cid in {71,72,73}:
        if target_data.talent[cid]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HAS_NOT_BEEN_HYPNOSIS)
def handle_target_has_not_been_hypnosis(character_id: int) -> int:
    """
    交互对象没有任何被催眠素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_target_has_been_hypnosis(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_PRIMARY_HYPNOSIS)
def handle_target_has_been_primary_hypnosis(character_id: int) -> int:
    """
    交互对象拥有被浅层催眠素质(50%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[71]


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_DEEP_HYPNOSIS)
def handle_target_has_been_deep_hypnosis(character_id: int) -> int:
    """
    交互对象拥有被深层催眠素质(100%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[72]


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_COMPLETE_HYPNOSIS)
def handle_target_has_been_complete_hypnosis(character_id: int) -> int:
    """
    交互对象拥有被完全催眠素质(200%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[73]


@add_premise(constant_promise.Premise.IN_HYPNOSIS)
def handle_in_hypnosis(character_id: int) -> int:
    """
    自己正在被催眠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_HYPNOSIS)
def handle_not_in_hypnosis(character_id: int) -> int:
    """
    自己没有正在被催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_IN_HYPNOSIS)
def handle_target_in_hypnosis(character_id: int) -> int:
    """
    交互对象正在被催眠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_IN_HYPNOSIS)
def handle_target_not_in_hypnosis(character_id: int) -> int:
    """
    交互对象没有正在被催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 0
    return 1


@add_premise(constant_promise.Premise.PRIMARY_PENETRATING_VISION)
def handle_primary_penetrating_vision(character_id: int) -> int:
    """
    拥有初级透视
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[307]


@add_premise(constant_promise.Premise.INTERMEDIATE_PENETRATING_VISION)
def handle_intermediate_penetrating_vision(character_id: int) -> int:
    """
    拥有中级透视
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[308]


@add_premise(constant_promise.Premise.ADVANCED_PENETRATING_VISION)
def handle_advanced_penetrating_vision(character_id: int) -> int:
    """
    拥有高级透视
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[309]


@add_premise(constant_promise.Premise.PENETRATING_VISION_ON)
def handle_penetrating_vision_on(character_id: int) -> int:
    """
    透视开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.pl_ability.visual


@add_premise(constant_promise.Premise.PENETRATING_VISION_OFF)
def handle_penetrating_vision_off(character_id: int) -> int:
    """
    透视关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not character_data.pl_ability.visual


@add_premise(constant_promise.Premise.PRIMARY_HORMONE)
def handle_primary_hormone(character_id: int) -> int:
    """
    拥有初级信息素
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[304]


@add_premise(constant_promise.Premise.INTERMEDIATE_HORMONE)
def handle_intermediate_hormone(character_id: int) -> int:
    """
    拥有中级信息素
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[305]


@add_premise(constant_promise.Premise.ADVANCED_HORMONE)
def handle_advanced_hormone(character_id: int) -> int:
    """
    拥有高级信息素
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[306]


@add_premise(constant_promise.Premise.HORMONE_ON)
def handle_hormone_on(character_id: int) -> int:
    """
    信息素开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.pl_ability.hormone


@add_premise(constant_promise.Premise.HORMONE_OFF)
def handle_hormone_off(character_id: int) -> int:
    """
    信息素关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not character_data.pl_ability.hormone


@add_premise(constant_promise.Premise.PRIMARY_TELEKINESIS)
def handle_primary_telekinesis(character_id: int) -> int:
    """
    拥有初级隔空肢体
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[310]


@add_premise(constant_promise.Premise.INTERMEDIATE_TELEKINESIS)
def handle_intermediate_telekinesis(character_id: int) -> int:
    """
    拥有中级隔空肢体
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[311]


@add_premise(constant_promise.Premise.ADVANCED_TELEKINESIS)
def handle_advanced_telekinesis(character_id: int) -> int:
    """
    拥有高级隔空肢体
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[312]


@add_premise(constant_promise.Premise.HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    自己被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.increase_body_sensitivity


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_not_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    自己未被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_increase_body_sensitivity(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_target_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    交互对象被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_increase_body_sensitivity(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_target_not_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    交互对象未被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_increase_body_sensitivity(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_FORCE_OVULATION)
def handle_hypnosis_force_ovulation(character_id: int) -> int:
    """
    自己被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.force_ovulation


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_FORCE_OVULATION)
def handle_not_hypnosis_force_ovulation(character_id: int) -> int:
    """
    自己未被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_force_ovulation(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_FORCE_OVULATION)
def handle_target_hypnosis_force_ovulation(character_id: int) -> int:
    """
    交互对象被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_force_ovulation(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_FORCE_OVULATION)
def handle_target_not_hypnosis_force_ovulation(character_id: int) -> int:
    """
    交互对象未被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_force_ovulation(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_BLOCKHEAD)
def handle_hypnosis_blockhead(character_id: int) -> int:
    """
    自己被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.blockhead


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_BLOCKHEAD)
def handle_not_hypnosis_blockhead(character_id: int) -> int:
    """
    自己未被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_blockhead(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_BLOCKHEAD)
def handle_target_hypnosis_blockhead(character_id: int) -> int:
    """
    交互对象被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_blockhead(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_BLOCKHEAD)
def handle_target_not_hypnosis_blockhead(character_id: int) -> int:
    """
    交互对象未被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_blockhead(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_ACTIVE_H)
def handle_hypnosis_active_h(character_id: int) -> int:
    """
    自己被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.active_h


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_ACTIVE_H)
def handle_not_hypnosis_active_h(character_id: int) -> int:
    """
    自己未被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_active_h(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ACTIVE_H)
def handle_target_hypnosis_active_h(character_id: int) -> int:
    """
    交互对象被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_active_h(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_ACTIVE_H)
def handle_target_not_hypnosis_active_h(character_id: int) -> int:
    """
    交互对象未被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_active_h(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_ROLEPLAY)
def handle_hypnosis_roleplay(character_id: int) -> int:
    """
    自己被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.roleplay


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_ROLEPLAY)
def handle_not_hypnosis_roleplay(character_id: int) -> int:
    """
    自己未被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_roleplay(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY)
def handle_target_hypnosis_roleplay(character_id: int) -> int:
    """
    交互对象被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_roleplay(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_ROLEPLAY)
def handle_target_not_hypnosis_roleplay(character_id: int) -> int:
    """
    交互对象未被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_roleplay(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_1)
def handle_target_hypnosis_roleplay_1(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-妻子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.hypnosis.roleplay == 1


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_2)
def handle_target_hypnosis_roleplay_2(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-妹妹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.hypnosis.roleplay == 2


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_3)
def handle_target_hypnosis_roleplay_3(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-女儿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.hypnosis.roleplay == 3


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_4)
def handle_target_hypnosis_roleplay_4(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-女仆
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.hypnosis.roleplay == 4


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_5)
def handle_target_hypnosis_roleplay_5(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-宠物猫
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.hypnosis.roleplay == 5


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_6)
def handle_target_hypnosis_roleplay_6(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-宠物狗
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.hypnosis.roleplay == 6


@add_premise(constant_promise.Premise.HYPNOSIS_PAIN_AS_PLEASURE)
def handle_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    自己被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.pain_as_pleasure


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_PAIN_AS_PLEASURE)
def handle_not_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    自己未被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_pain_as_pleasure(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_PAIN_AS_PLEASURE)
def handle_t_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    交互对象被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_pain_as_pleasure(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_PAIN_AS_PLEASURE)
def handle_t_not_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    交互对象未被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_pain_as_pleasure(character_data.target_character_id)


@add_premise(constant_promise.Premise.PRIMARY_TIME_STOP)
def handle_primary_time_stop(character_id: int) -> int:
    """
    自己拥有初级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent[316]:
        return 1
    return 0


@add_premise(constant_promise.Premise.INTERMEDIATE_TIME_STOP)
def handle_intermediate_time_stop(character_id: int) -> int:
    """
    自己拥有中级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent[317]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ADVANCED_TIME_STOP)
def handle_advanced_time_stop(character_id: int) -> int:
    """
    自己拥有高级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent[318]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_STOP_ON)
def handle_time_stop_on(character_id: int) -> int:
    """
    时停开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.time_stop_mode


@add_premise(constant_promise.Premise.TIME_STOP_OFF)
def handle_time_stop_off(character_id: int) -> int:
    """
    时停关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_time_stop_on(character_id)


@add_premise(constant_promise.Premise.TIME_STOP_JUDGE_FOR_MOVE)
def handle_time_stop_judge_for_move(character_id: int) -> int:
    """
    (移动用)未开启时停，或时停开启且有中级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_time_stop_off(character_id):
        return 1
    else:
        if handle_intermediate_time_stop(character_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.NOBODY_FREE_IN_TIME_STOP)
def handle_nobody_free_in_time_stop(character_id: int) -> int:
    """
    没有指定可以在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.pl_ability.free_in_time_stop_chara_id > 0:
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_CARRY_ANYBODY_IN_TIME_STOP)
def handle_not_carry_anybody_in_time_stop(character_id: int) -> int:
    """
    没有在时停中搬运干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.pl_ability.carry_chara_id_in_time_stop > 0:
        return 0
    return 1


@add_premise(constant_promise.Premise.CARRY_SOMEBODY_IN_TIME_STOP)
def handle_carry_somebody_in_time_stop(character_id: int) -> int:
    """
    正在时停中搬运干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_not_carry_anybody_in_time_stop(character_id)


@add_premise(constant_promise.Premise.SOMEBODY_FREE_IN_TIME_STOP)
def handle_somebody_free_in_time_stop(character_id: int) -> int:
    """
    玩家已指定可以在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_nobody_free_in_time_stop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_FREE_IN_TIME_STOP)
def handle_self_free_in_time_stop(character_id: int) -> int:
    """
    自己是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if character_id > 0 and character_id == pl_character_data.pl_ability.free_in_time_stop_chara_id:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_FREE_IN_TIME_STOP)
def handle_self_not_free_in_time_stop(character_id: int) -> int:
    """
    自己不是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_free_in_time_stop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_FREE_IN_TIME_STOP)
def handle_target_free_in_time_stop(character_id: int) -> int:
    """
    交互对象是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_free_in_time_stop(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_FREE_IN_TIME_STOP)
def handle_target_not_free_in_time_stop(character_id: int) -> int:
    """
    交互对象不是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_free_in_time_stop(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.HAVE_WORK)
def handle_have_work(character_id: int) -> int:
    """
    自己有工作
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type > 0


@add_premise(constant_promise.Premise.WORK_IS_MAINTENANCE_ENGINEER)
def handle_work_is_maintenance_engineer(character_id: int) -> int:
    """
    自己的工作为检修工程师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 21


@add_premise(constant_promise.Premise.WORK_IS_BLACKSMITH)
def handle_work_is_blacksmith(character_id: int) -> int:
    """
    自己的工作为铁匠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 22


@add_premise(constant_promise.Premise.WORK_IS_DOCTOR)
def handle_work_is_doctor(character_id: int) -> int:
    """
    自己的工作为医生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 61


@add_premise(constant_promise.Premise.WORK_IS_HR)
def handle_work_is_hr(character_id: int) -> int:
    """
    自己的工作为人事
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 71


@add_premise(constant_promise.Premise.WORK_IS_LIBRARY_MANAGER)
def handle_work_is_library_manager(character_id: int) -> int:
    """
    自己的工作为图书馆管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 101


@add_premise(constant_promise.Premise.T_WORK_IS_LIBRARY_MANAGER)
def handle_t_work_is_library_manager(character_id: int) -> int:
    """
    交互对象的工作为图书馆管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.work.work_type == 101


@add_premise(constant_promise.Premise.WORK_IS_TEACHER)
def handle_work_is_teacher(character_id: int) -> int:
    """
    自己的工作为教师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 151


@add_premise(constant_promise.Premise.WORK_IS_STUDENT)
def handle_work_is_student(character_id: int) -> int:
    """
    自己的工作为学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 152


@add_premise(constant_promise.Premise.WORK_IS_COMBAT_TRAINING)
def handle_work_is_combat_training(character_id: int) -> int:
    """
    自己的工作为战斗训练
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 91


@add_premise(constant_promise.Premise.WORK_IS_FITNESS_TRAINER)
def handle_work_is_fitness_trainer(character_id: int) -> int:
    """
    自己的工作为健身锻炼员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 92


@add_premise(constant_promise.Premise.WORK_IS_COOK)
def handle_work_is_cook(character_id: int) -> int:
    """
    自己的工作为厨师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 51


@add_premise(constant_promise.Premise.WORK_IS_PRODUCTION_WORKER)
def handle_work_is_production_worker(character_id: int) -> int:
    """
    自己的工作为生产工人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 121


@add_premise(constant_promise.Premise.WORK_IS_MASSAGE_THERAPIST)
def handle_work_is_massage_therapist(character_id: int) -> int:
    """
    自己的工作为按摩师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 171


@add_premise(constant_promise.Premise.WORK_IS_DIPLOMAT)
def handle_work_is_diplomat(character_id: int) -> int:
    """
    自己的工作为外交官
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 131


@add_premise(constant_promise.Premise.WORK_IS_INVITATION_COMMISSIONER)
def handle_work_is_invitation_commissioner(character_id: int) -> int:
    """
    自己的工作为邀请专员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 132


@add_premise(constant_promise.Premise.WORK_IS_MEDICINAL_PLANTER)
def handle_work_is_medicinal_planter(character_id: int) -> int:
    """
    自己的工作为药材种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 161


@add_premise(constant_promise.Premise.WORK_IS_FLORAL_PLANTER)
def handle_work_is_floral_planter(character_id: int) -> int:
    """
    自己的工作为花草种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 162


@add_premise(constant_promise.Premise.WORK_IS_SEX_TRAINEE)
def handle_work_is_sex_trainee(character_id: int) -> int:
    """
    自己的工作为性爱练习生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 193


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_READ)
def handle_entertainment_is_read(character_id: int) -> int:
    """
    自己当前时段的娱乐为读书
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 101


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_SING)
def handle_entertainment_is_sing(character_id: int) -> int:
    """
    自己当前时段的娱乐为唱歌
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 51


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_CLASSIC_INSTRUMENT)
def handle_entertainment_is_play_classic_instrument(character_id: int) -> int:
    """
    自己当前时段的娱乐为演奏传统乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 53


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_MODEN_INSTRUMENT)
def handle_ENTERTAINMENT_IS_PLAY_MODEN_INSTRUMENT(character_id: int) -> int:
    """
    自己当前时段的娱乐为演奏现代乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 54


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_WATCH_MOVIE)
def handle_entertainment_is_watch_movie(character_id: int) -> int:
    """
    自己当前时段的娱乐为看电影
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 55


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PHOTOGRAPHY)
def handle_entertainment_is_photography(character_id: int) -> int:
    """
    自己当前时段的娱乐为摄影
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 56


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_WATER)
def handle_entertainment_is_play_water(character_id: int) -> int:
    """
    自己当前时段的娱乐为玩水
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 57


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_CHESS)
def handle_entertainment_is_play_chess(character_id: int) -> int:
    """
    自己当前时段的娱乐为下棋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 58


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_MAHJONG)
def handle_entertainment_is_play_mahjong(character_id: int) -> int:
    """
    自己当前时段的娱乐为打麻将
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 59


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_CARDS)
def handle_entertainment_is_play_cards(character_id: int) -> int:
    """
    自己当前时段的娱乐为打牌
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 60


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_REHEARSE_DANCE)
def handle_entertainment_is_rehearse_dance(character_id: int) -> int:
    """
    自己当前时段的娱乐为排演舞剧
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 61


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_ARCADE_GAME)
def handle_entertainment_is_play_arcade_game(character_id: int) -> int:
    """
    自己当前时段的娱乐为玩街机游戏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 111


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_TEA)
def handle_entertainment_is_taste_tea(character_id: int) -> int:
    """
    自己当前时段的娱乐为品茶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 112


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_COFFEE)
def handle_entertainment_is_taste_coffee(character_id: int) -> int:
    """
    自己当前时段的娱乐为品咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 113


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_DESSERT)
def handle_entertainment_is_taste_dessert(character_id: int) -> int:
    """
    自己当前时段的娱乐为品尝点心
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 114


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_FOOD)
def handle_entertainment_is_taste_food(character_id: int) -> int:
    """
    自己当前时段的娱乐为品尝美食
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 115


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_HOUSE)
def handle_entertainment_is_play_house(character_id: int) -> int:
    """
    自己当前时段的娱乐为过家家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 151


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_STYLE_HAIR)
def handle_entertainment_is_style_hair(character_id: int) -> int:
    """
    自己当前时段的娱乐为修整发型
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 116


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_FULL_BODY_STYLING)
def handle_entertainment_is_full_body_styling(character_id: int) -> int:
    """
    自己当前时段的娱乐为全身造型服务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 117


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_BATHHOUSE_TYPE)
def handle_entertainment_is_bathhouse_type(character_id: int) -> int:
    """
    自己当前时段的娱乐为大浴场类的娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    for cid in {171,172,173,174,175,176}:
        if character_data.entertainment.entertainment_type[i] == cid:
            return 1

    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_ENTERTAINMENT_IS_BATHHOUSE_TYPE)
def handle_scene_someone_entertainment_is_bathhouse_type(character_id: int) -> int:
    """
    当前场景里有人当前时段的娱乐为大浴场类的娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于1时进行检测
    if len(scene_data.character_list) > 1:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 遍历非自己的角色
            if chara_id != character_id:
                other_character_data: game_type.Character = cache.character_data[chara_id]

                # 开始判定
                i = game_time.judge_entertainment_time(character_id)
                if i:
                    i -= 1
                else:
                    continue

                for cid in {171,172,173,174,175,176}:
                    if other_character_data.entertainment.entertainment_type[i] == cid:
                        return 1

    return 0


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_BATHHOUSE_SHOWER_CLOTH_TYPE)
def handle_entertainment_is_bathhouse_shower_cloth_type(character_id: int) -> int:
    """
    自己当前时段的娱乐为大浴场类_需要换浴衣的娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    for cid in {172,173,174}:
        if character_data.entertainment.entertainment_type[i] == cid:
            return 1

    return 0


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_SOAK_FEET)
def handle_entertainment_is_soak_feet(character_id: int) -> int:
    """
    自己当前时段的娱乐为泡脚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 171


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_STEAM_SAUNA)
def handle_entertainment_is_steam_sauna(character_id: int) -> int:
    """
    自己当前时段的娱乐为蒸桑拿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 172


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_HYDROTHERAPY_TREATMENT)
def handle_entertainment_is_hydrotherapy_treatment(character_id: int) -> int:
    """
    自己当前时段的娱乐为水疗护理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 173


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_ONSEN_BATH)
def handle_entertainment_is_onsen_bath(character_id: int) -> int:
    """
    自己当前时段的娱乐为泡温泉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 174


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_SWIMMING)
def handle_entertainment_is_swimming(character_id: int) -> int:
    """
    自己当前时段的娱乐为游泳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 91


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_WINE)
def handle_entertainment_is_taste_wine(character_id: int) -> int:
    """
    自己当前时段的娱乐为品酒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 62

@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input and (last_cmd == str(constant.Instruct.BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_MAKING_OUT)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.MAKING_OUT)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_KISS_H)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.KISS_H)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BREAST_CARESS)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.BREAST_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_TWIDDLE_NIPPLES)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.TWIDDLE_NIPPLES)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BREAST_SUCKING)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.BREAST_SUCKING)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_CLIT_CARESS)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.CLIT_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_OPEN_LABIA)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.OPEN_LABIA)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_CUNNILINGUS)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.CUNNILINGUS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FINGER_INSERTION)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FINGER_INSERTION)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_ANAL_CARESS)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.ANAL_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_MAKE_MASTUREBATE)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.MAKE_MASTUREBATE)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HANDJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HANDJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_PAIZURI)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.PAIZURI)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FOOTJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FOOTJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HAIRJOB)
def handle_last_cmd_hairjob(character_id: int) -> int:
    """
    前一指令为发交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HAIRJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_AXILLAJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.AXILLAJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_RUB_BUTTOCK)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.RUB_BUTTOCK)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_LEGJOB)
def handle_last_cmd_legjob(character_id: int) -> int:
    """
    前一指令为腿交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.LEGJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_TAILJOB)
def handle_last_cmd_tailjob(character_id: int) -> int:
    """
    前一指令为尾交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.TAILJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FACE_RUB)
def handle_last_cmd_face_rub(character_id: int) -> int:
    """
    前一指令为阴茎蹭脸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FACE_RUB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HORN_RUB)
def handle_last_cmd_horn_rub(character_id: int) -> int:
    """
    前一指令为阴茎蹭角
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HORN_RUB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_EARS_RUB)
def handle_last_cmd_ears_rub(character_id: int) -> int:
    """
    前一指令为阴茎蹭耳朵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.EARS_RUB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HAND_BLOWJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HAND_BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_TITS_BLOWJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.TITS_BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_DEEP_THROAT)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.DEEP_THROAT)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FOCUS_BLOWJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FOCUS_BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_NORMAL_SEX)
def handle_last_cmd_normal_sex(character_id: int) -> int:
    """
    前一指令为正常位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.NORMAL_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BACK_SEX)
def handle_last_cmd_back_sex(character_id: int) -> int:
    """
    前一指令为背后位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.BACK_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_RIDING_SEX)
def handle_last_cmd_riding_sex(character_id: int) -> int:
    """
    前一指令为骑乘位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.RIDING_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_FACE_SEAT_SEX)
def handle_last_cmd_face_seat_sex(character_id: int) -> int:
    """
    前一指令为对面座位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.FACE_SEAT_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BACK_SEAT_SEX)
def handle_last_cmd_back_seat_sex(character_id: int) -> int:
    """
    前一指令为背面座位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.BACK_SEAT_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_FACE_STAND_SEX)
def handle_last_cmd_face_stand_sex(character_id: int) -> int:
    """
    前一指令为对面立位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.FACE_STAND_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BACK_STAND_SEX)
def handle_last_cmd_back_stand_sex(character_id: int) -> int:
    """
    前一指令为背面立位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.BACK_STAND_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_STIMULATE_G_POINT)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.STIMULATE_G_POINT)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_WOMB_OS_CARESS)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.WOMB_OS_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_PENIS_POSITION)
def handle_last_cmd_penis_position(character_id: int) -> int:
    """
    前一指令为阴茎位置相关指令_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.NORMAL_SEX), str(constant.Instruct.BACK_SEX), str(constant.Instruct.RIDING_SEX),
        str(constant.Instruct.FACE_SEAT_SEX), str(constant.Instruct.BACK_SEAT_SEX),
        str(constant.Instruct.FACE_STAND_SEX), str(constant.Instruct.BACK_STAND_SEX),
        str(constant.Instruct.STIMULATE_G_POINT), str(constant.Instruct.WOMB_OS_CARESS),
        str(constant.Instruct.WOMB_INSERTION),
        str(constant.Instruct.NORMAL_ANAL_SEX), str(constant.Instruct.BACK_ANAL_SEX),
        str(constant.Instruct.RIDING_ANAL_SEX),
        str(constant.Instruct.FACE_SEAT_ANAL_SEX), str(constant.Instruct.BACK_SEAT_ANAL_SEX),
        str(constant.Instruct.FACE_STAND_ANAL_SEX), str(constant.Instruct.BACK_STAND_ANAL_SEX),
        str(constant.Instruct.STIMULATE_SIGMOID_COLON), str(constant.Instruct.STIMULATE_VAGINA),
        str(constant.Instruct.URETHRAL_SEX),
        str(constant.Instruct.HANDJOB), str(constant.Instruct.HAND_BLOWJOB),
        str(constant.Instruct.BLOWJOB), str(constant.Instruct.PAIZURI),
        str(constant.Instruct.TITS_BLOWJOB), str(constant.Instruct.FOCUS_BLOWJOB),
        str(constant.Instruct.DEEP_THROAT), str(constant.Instruct.SIXTY_NINE),
        str(constant.Instruct.FOOTJOB), str(constant.Instruct.HAIRJOB),
        str(constant.Instruct.AXILLAJOB), str(constant.Instruct.RUB_BUTTOCK),
        str(constant.Instruct.LEGJOB), str(constant.Instruct.TAILJOB),
        str(constant.Instruct.FACE_RUB), str(constant.Instruct.HORN_RUB),
        str(constant.Instruct.EARS_RUB),
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_OR_HANDJOB)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.HANDJOB)):
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_OR_PAIZURI)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.PAIZURI)):
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_OR_CUNNILINGUS)
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
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.CUNNILINGUS)):
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_SEX)
def handle_last_cmd_sex(character_id: int) -> int:
    """
    前一指令为V性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)

    sex = {
        str(constant.Instruct.NORMAL_SEX), str(constant.Instruct.BACK_SEX), str(constant.Instruct.RIDING_SEX),
        str(constant.Instruct.FACE_SEAT_SEX), str(constant.Instruct.BACK_SEAT_SEX),
        str(constant.Instruct.FACE_STAND_SEX), str(constant.Instruct.BACK_STAND_SEX),
        str(constant.Instruct.STIMULATE_G_POINT), str(constant.Instruct.WOMB_OS_CARESS)
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_W_SEX)
def handle_last_cmd_w_sex(character_id: int) -> int:
    """
    前一指令为W性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    sex = {
        str(constant.Instruct.WOMB_INSERTION), str(constant.Instruct.WOMB_SEX)
    }
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_SEX_OR_W_SEX)
def handle_last_cmd_sex_or_w_sex(character_id: int) -> int:
    """
    前一指令为V性交或W性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_last_cmd_sex(character_id):
        return 1
    elif handle_last_cmd_w_sex(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_A_SEX)
def handle_last_cmd_a_sex(character_id: int) -> int:
    """
    前一指令为A性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    sex = {
        str(constant.Instruct.NORMAL_ANAL_SEX), str(constant.Instruct.BACK_ANAL_SEX),
        str(constant.Instruct.RIDING_ANAL_SEX),
        str(constant.Instruct.FACE_SEAT_ANAL_SEX), str(constant.Instruct.BACK_SEAT_ANAL_SEX),
        str(constant.Instruct.FACE_STAND_ANAL_SEX), str(constant.Instruct.BACK_STAND_ANAL_SEX),
        str(constant.Instruct.STIMULATE_SIGMOID_COLON), str(constant.Instruct.STIMULATE_VAGINA)
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_U_SEX)
def handle_last_cmd_u_sex(character_id: int) -> int:
    """
    前一指令为U性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    sex = {
        str(constant.Instruct.URETHRAL_SEX)
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BREAST_CARESS_TYPE)
def handle_last_cmd_breast_caress_type(character_id: int) -> int:
    """
    前一指令为胸部爱抚类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.BREAST_CARESS), str(constant.Instruct.TWIDDLE_NIPPLES),
        str(constant.Instruct.BREAST_SUCKING)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HANDJOB_TYPE)
def handle_last_cmd_handjob_type(character_id: int) -> int:
    """
    前一指令为手交类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.HANDJOB), str(constant.Instruct.HAND_BLOWJOB)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_TYPE)
def handle_last_cmd_blowjob_type(character_id: int) -> int:
    """
    前一指令为口交类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.BLOWJOB), str(constant.Instruct.HAND_BLOWJOB),
        str(constant.Instruct.TITS_BLOWJOB), str(constant.Instruct.FOCUS_BLOWJOB),
        str(constant.Instruct.DEEP_THROAT), str(constant.Instruct.SIXTY_NINE), str(constant.Instruct.CLEAN_BLOWJOB)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_PAIZURI_TYPE)
def handle_last_cmd_paizuri_type(character_id: int) -> int:
    """
    前一指令为乳交类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = cache.input_cache
    len_input = len(len_input)
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.PAIZURI), str(constant.Instruct.TITS_BLOWJOB)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.H_IN_LOVE_HOTEL)
def handle_h_in_love_hotel(character_id: int) -> int:
    """
    当前正在爱情旅馆中H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.h_in_love_hotel:
        return 1
    return 0


@add_premise(constant_promise.Premise.H_NOT_IN_LOVE_HOTEL)
def handle_h_not_in_love_hotel(character_id: int) -> int:
    """
    当前不在爱情旅馆中H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_h_in_love_hotel(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_LIVE_IN_LOVE_HOTEL)
def handle_not_live_inlove_hotel(character_id: int) -> int:
    """
    还未在爱情旅馆中入住
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.LIVE_IN_LOVE_HOTEL)
def handle_live_inlove_hotel(character_id: int) -> int:
    """
    已在爱情旅馆中入住
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.LOVE_HOTEL_ROOM_V1)
def handle_love_hotel_room_v1(character_id: int) -> int:
    """
    在爱情旅馆中入住房间为标间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.LOVE_HOTEL_ROOM_V2)
def handle_love_hotel_room_v2(character_id: int) -> int:
    """
    在爱情旅馆中入住房间为情趣主题房
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.LOVE_HOTEL_ROOM_V3)
def handle_love_hotel_room_v3(character_id: int) -> int:
    """
    在爱情旅馆中入住房间为顶级套房
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_HAIR)
def handle_penis_in_t_hair(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_发交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_FACE)
def handle_penis_in_t_face(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_阴茎蹭脸中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_MOUSE)
def handle_penis_in_t_mouse(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_口交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_BREAST)
def handle_penis_in_t_breast(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_乳交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_AXILLA)
def handle_penis_in_t_axilla(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_腋交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_HAND)
def handle_penis_in_t_hand(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_手交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_VAGINA)
def handle_penis_in_t_vagina(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_V插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 6:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_WOMB)
def handle_penis_in_t_womb(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_W插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_ANAL)
def handle_penis_in_t_anal(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_A插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 8:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_URETHRAL)
def handle_penis_in_t_nrethral(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_U插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 9:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_LEG)
def handle_penis_in_t_leg(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_腿交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_FOOT)
def handle_penis_in_t_foot(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_足交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 11:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_TAIL)
def handle_penis_in_t_tail(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_尾交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 12:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_HORN)
def handle_penis_in_t_horn(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_阴茎蹭角中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 13:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_EARS)
def handle_penis_in_t_ears(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_阴茎蹭耳朵中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 14:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_BODY)
def handle_shoot_in_t_body(character_id: int) -> int:
    """
    在交互对象的身体上射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body != -1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_HAIR)
def handle_shoot_in_t_hair(character_id: int) -> int:
    """
    在交互对象的头发射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_FACE)
def handle_shoot_in_t_face(character_id: int) -> int:
    """
    在交互对象的脸部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_MOUSE)
def handle_shoot_in_t_mouse(character_id: int) -> int:
    """
    在交互对象的口腔射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_BREAST)
def handle_shoot_in_t_breast(character_id: int) -> int:
    """
    在交互对象的胸部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_AXILLA)
def handle_shoot_in_t_axilla(character_id: int) -> int:
    """
    在交互对象的腋部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_HAND)
def handle_shoot_in_t_hand(character_id: int) -> int:
    """
    在交互对象的手部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_VAGINA)
def handle_shoot_in_t_vagina(character_id: int) -> int:
    """
    在交互对象的小穴射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 6:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_WOMB)
def handle_shoot_in_t_womb(character_id: int) -> int:
    """
    在交互对象的子宫射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_ANAL)
def handle_shoot_in_t_anal(character_id: int) -> int:
    """
    在交互对象的后穴射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 8:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_URETHRAL)
def handle_shoot_in_t_nrethral(character_id: int) -> int:
    """
    在交互对象的尿道射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 9:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_LEG)
def handle_shoot_in_t_leg(character_id: int) -> int:
    """
    在交互对象的腿部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_FOOT)
def handle_shoot_in_t_foot(character_id: int) -> int:
    """
    在交互对象的脚部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 11:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_TAIL)
def handle_shoot_in_t_tail(character_id: int) -> int:
    """
    在交互对象的尾巴射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 12:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_HORN)
def handle_shoot_in_t_horn(character_id: int) -> int:
    """
    在交互对象的兽角射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 13:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_EARS)
def handle_shoot_in_t_ears(character_id: int) -> int:
    """
    在交互对象的兽耳射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 14:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_CLOTH)
def handle_shoot_in_t_cloth(character_id: int) -> int:
    """
    在交互对象的衣服上射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_cloth != -1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_ORGASM_0)
def handle_t_turn_orgasm_0(character_id: int) -> int:
    """
    交互对象本次H中还没有绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for body_part in game_config.config_body_part:
        if target_data.h_state.orgasm_count[body_part][1]:
            return 0
    return 1


@add_premise(constant_promise.Premise.T_TURN_ORGASM_G_1)
def handle_t_turn_orgasm_g_1(character_id: int) -> int:
    """
    交互对象本次H中绝顶次数>1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    count = 0
    for body_part in game_config.config_body_part:
        count += target_data.h_state.orgasm_count[body_part][1]
        if count > 1:
            return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_ORGASM_G_5)
def handle_t_turn_orgasm_g_5(character_id: int) -> int:
    """
    交互对象本次H中绝顶次数>5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    count = 0
    for body_part in game_config.config_body_part:
        count += target_data.h_state.orgasm_count[body_part][1]
        if count > 5:
            return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_ORGASM_G_10)
def handle_t_turn_orgasm_g_10(character_id: int) -> int:
    """
    交互对象本次H中绝顶次数>10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    count = 0
    for body_part in game_config.config_body_part:
        count += target_data.h_state.orgasm_count[body_part][1]
        if count > 10:
            return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_N_ORGASM_G_3)
def handle_t_turn_n_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中N绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[0][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_B_ORGASM_G_3)
def handle_t_turn_b_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中B绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[1][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_C_ORGASM_G_3)
def handle_t_turn_c_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中C绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[2][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TURN_P_ORGASM_G_1)
def handle_turn_p_orgasm_g_1(character_id: int) -> int:
    """
    玩家本次H中射精次数>1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.h_state.orgasm_count[3][1] > 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TURN_P_ORGASM_G_3)
def handle_turn_p_orgasm_g_3(character_id: int) -> int:
    """
    玩家本次H中射精次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.h_state.orgasm_count[3][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_V_ORGASM_G_3)
def handle_t_turn_v_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中V绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[4][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_A_ORGASM_G_3)
def handle_t_turn_a_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中A绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[5][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_U_ORGASM_G_3)
def handle_t_turn_u_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中U绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[6][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_W_ORGASM_G_3)
def handle_t_turn_w_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中W绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[7][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_M_ORGASM_G_3)
def handle_t_turn_m_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中M绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[8][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_LE_2)
def handle_pl_semen_le_2(character_id: int) -> int:
    """
    玩家当前精液量小于等于2ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point <= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_LE_50)
def handle_pl_semen_le_50(character_id: int) -> int:
    """
    玩家当前精液量小于等于50ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point <= 50:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_GE_50)
def handle_pl_semen_ge_50(character_id: int) -> int:
    """
    玩家当前精液量大于等于50ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point >= 50:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_GE_100)
def handle_pl_semen_ge_100(character_id: int) -> int:
    """
    玩家当前精液量大于等于100ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point >= 100:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_JUST_SHOOT)
def handle_pl_just_shoot(character_id: int) -> int:
    """
    玩家前指令射精了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.h_state.just_shoot:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_NOT_JUST_SHOOT)
def handle_pl_not_just_shoot(character_id: int) -> int:
    """
    玩家前指令未射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_pl_just_shoot(0):
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_ORGASM_EDGE)
def handle_self_orgasm_edge(character_id: int) -> int:
    """
    自己正在被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.orgasm_edge == 1


@add_premise(constant_promise.Premise.SELF_NOT_ORGASM_EDGE)
def handle_self_not_orgasm_edge(character_id: int) -> int:
    """
    自己没有被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.orgasm_edge == 0


@add_premise(constant_promise.Premise.SELF_ORGASM_EDGE_RELAESE)
def handle_self_orgasm_edge_relase(character_id: int) -> int:
    """
    自己被绝顶寸止解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.orgasm_edge == 2


@add_premise(constant_promise.Premise.TARGET_ORGASM_EDGE)
def handle_target_orgasm_edge(character_id: int) -> int:
    """
    交互对象正在被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_orgasm_edge(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_ORGASM_EDGE)
def handle_target_not_orgasm_edge(character_id: int) -> int:
    """
    交互对象没有被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_not_orgasm_edge(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_ORGASM_EDGE_RELAESE)
def handle_target_orgasm_edge_relase(character_id: int) -> int:
    """
    交互对象被绝顶寸止解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_orgasm_edge_relase(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_TIME_STOP_ORGASM_RELAESE)
def handle_self_time_stop_orgasm_relase(character_id: int) -> int:
    """
    自己被时停解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.time_stop_release


@add_premise(constant_promise.Premise.TARGET_TIME_STOP_ORGASM_RELAESE)
def handle_target_time_stop_orgasm_relase(character_id: int) -> int:
    """
    交互对象被时停解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_time_stop_orgasm_relase(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_ORGASM_EDGE_RELAESE_OR_TIME_STOP_ORGASM_RELAESE)
def handle_self_orgasm_edge_relase_or_time_stop_orgasm_relase(character_id: int) -> int:
    """
    自己被绝顶寸止解放或时停解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_orgasm_edge_relase(character_id) or handle_self_time_stop_orgasm_relase(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.NPC_ACTIVE_H)
def handle_npc_active_h(character_id: int) -> int:
    """
    自己正在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.npc_active_h:
        return 1
    return 0


@add_premise(constant_promise.Premise.NPC_NOT_ACTIVE_H)
def handle_npc_not_active_h(character_id: int) -> int:
    """
    自己没有在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.npc_active_h:
        return 0
    return 1


@add_premise(constant_promise.Premise.T_NPC_ACTIVE_H)
def handle_t_npc_active_h(character_id: int) -> int:
    """
    交互对象正在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.npc_active_h:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NPC_NOT_ACTIVE_H)
def handle_t_npc_not_active_h(character_id: int) -> int:
    """
    交互对象没有在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.npc_active_h:
        return 0
    return 1


@add_premise(constant_promise.Premise.GROUP_SEX_FAIL_AND_SELF_AGREE)
def handle_group_sex_fail_and_self_agree(character_id: int) -> int:
    """
    多P邀请失败了，但自己不是拒绝者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if character_id in pl_character_data.action_info.ask_group_sex_refuse_chara_id_list:
        return 0
    return 1


@add_premise(constant_promise.Premise.GROUP_SEX_FAIL_AND_SELF_REFUSE)
def handle_group_sex_fail_and_self_refuse(character_id: int) -> int:
    """
    多P邀请失败了，自己是拒绝者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_group_sex_fail_and_self_agree(character_id)


# 以下为道具系前提

@add_premise(constant_promise.Premise.HAVE_CAMERA)
def handle_have_camera(character_id: int) -> int:
    """
    校验角色是否已持有相机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[50] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_VIDEO_RECORDER)
def handle_have_video_recorder(character_id: int) -> int:
    """
    校验角色是否已持有录像机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[51] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_INSTRUMENT)
def handle_have_instrument(character_id: int) -> int:
    """
    校验角色是否已持有乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[52] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_NIPPLE_CLAMP)
def handle_have_nipple_clamp(character_id: int) -> int:
    """
    校验角色是否已持有乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[122] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_NIPPLE_CLAMP)
def handle_self_now_nipple_clamp(character_id: int) -> int:
    """
    校验自己是否正在乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[0][1]


@add_premise(constant_promise.Premise.TARGET_NOW_NIPPLE_CLAMP)
def handle_target_now_nipple_clamp(character_id: int) -> int:
    """
    校验交互对象是否正在乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_nipple_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_NIPPLE_CLAMP)
def handle_target_not_nipple_clamp(character_id: int) -> int:
    """
    校验交互对象是否没有在乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_target_now_nipple_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.HAVE_LOVE_EGG)
def handle_have_love_egg(character_id: int) -> int:
    """
    校验角色是否已持有跳蛋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[121] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CLIT_CLAMP)
def handle_have_clit_clamp(character_id: int) -> int:
    """
    校验角色是否已持有阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[123] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_CLIT_CLAMP)
def handle_self_now_clit_clamp(character_id: int) -> int:
    """
    校验自己是否正在阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[1][1]


@add_premise(constant_promise.Premise.TARGET_NOW_CLIT_CLAMP)
def handle_target_now_clit_clamp(character_id: int) -> int:
    """
    校验交互对象是否正在阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_clit_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_CLIT_CLAMP)
def handle_target_not_clit_clamp(character_id: int) -> int:
    """
    校验交互对象是否没有在阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_clit_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.HAVE_ELECTRIC_MESSAGE_STICK)
def handle_have_electric_message_stick(character_id: int) -> int:
    """
    校验角色是否已持有电动按摩棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[124] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_VIBRATOR)
def handle_have_vibrator(character_id: int) -> int:
    """
    校验角色是否已持有震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[125] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_VIBRATOR_INSERTION)
def handle_self_now_vibrator_insertion(character_id: int) -> int:
    """
    校验自己V正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[2][1]


@add_premise(constant_promise.Premise.TARGET_NOW_VIBRATOR_INSERTION)
def handle_target_now_vibrator_insertion(character_id: int) -> int:
    """
    校验交互对象V正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_vibrator_insertion(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION)
def handle_target_not_vibrator_insertion(character_id: int) -> int:
    """
    校验交互对象V没有在插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_vibrator_insertion(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_NOW_VIBRATOR_INSERTION_ANAL)
def handle_self_now_vibrator_insertion_anal(character_id: int) -> int:
    """
    校验自己A正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[3][1]


@add_premise(constant_promise.Premise.TARGET_NOW_VIBRATOR_INSERTION_ANAL)
def handle_target_now_vibrator_insertion_anal(character_id: int) -> int:
    """
    校验交互对象A正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_vibrator_insertion_anal(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL)
def handle_target_not_vibrator_insertion_anal(character_id: int) -> int:
    """
    校验交互对象A没有在插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_vibrator_insertion_anal(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_MILKING_MACHINE)
def handle_target_now_milking_machine(character_id: int) -> int:
    """
    交互对象正在搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[4][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_MILKING_MACHINE)
def handle_target_not_milking_machine(character_id: int) -> int:
    """
    交互对象没有在搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[4][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_NOW_URINE_COLLECTOR)
def handle_target_now_urine_collector(character_id: int) -> int:
    """
    交互对象正在采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[5][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_URINE_COLLECTOR)
def handle_target_not_urine_collector(character_id: int) -> int:
    """
    交互对象没有在采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[5][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_SEELP_PIILS)
def handle_self_sleep_pills(character_id: int) -> int:
    """
    自己已服用安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[9][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_SEELP_PIILS)
def handle_self_not_sleep_pills(character_id: int) -> int:
    """
    自己没有服用安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_sleep_pills(character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_BIRTH_CONTROL_PILLS_BEFORE)
def handle_target_now_birth_control_pills_before(character_id: int) -> int:
    """
    交互对象已服用事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[11][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_BIRTH_CONTROL_PILLS_BEFORE)
def handle_target_not_birth_control_pills_before(character_id: int) -> int:
    """
    交互对象没有服用事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_target_now_birth_control_pills_before(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_NOW_BIRTH_CONTROL_PILLS_AFTER)
def handle_target_now_birth_control_pills_after(character_id: int) -> int:
    """
    交互对象已服用事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[12][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_BIRTH_CONTROL_PILLS_AFTER)
def handle_target_not_birth_control_pills_after(character_id: int) -> int:
    """
    交互对象没有服用事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_target_now_birth_control_pills_after(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.NOW_CONDOM)
def handle_now_condom(character_id: int) -> int:
    """
    自己正戴着避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[13][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOW_NOT_CONDOM)
def handle_now_not_condom(character_id: int) -> int:
    """
    自己没有戴着避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[13][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_USE_CONDOM_IN_H)
def handle_not_use_condom_in_h(character_id: int) -> int:
    """
    本次H中没有已用掉的避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_1)
def handle_use_condom_in_h_ge_1(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_3)
def handle_use_condom_in_h_ge_3(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_5)
def handle_use_condom_in_h_ge_5(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_10)
def handle_use_condom_in_h_ge_10(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_MILKING_MACHINE)
def handle_have_milking_machine(character_id: int) -> int:
    """
    校验角色是否已持有搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[133] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_URINE_COLLECTOR)
def handle_have_urine_collector(character_id: int) -> int:
    """
    校验角色是否已持有采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[134] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BONDAGE)
def handle_have_bondage(character_id: int) -> int:
    """
    校验角色是否已持有绳子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[135] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_PATCH)
def handle_have_patch(character_id: int) -> int:
    """
    校验角色是否已持有眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[132] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BIG_VIBRATOR)
def handle_have_big_vibrator(character_id: int) -> int:
    """
    校验角色是否已持有加粗震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[126] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_HUGE_VIBRATOR)
def handle_have_huge_vibrator(character_id: int) -> int:
    """
    校验角色是否已持有巨型震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[127] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CLYSTER_TOOLS)
def handle_have_clyster_tools(character_id: int) -> int:
    """
    校验角色是否已持有灌肠套装
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[128] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_ANAL_BEADS)
def handle_have_anal_beads(character_id: int) -> int:
    """
    校验角色是否已持有肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[129] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOW_ANAL_BEADS)
def handle_target_now_anal_beads(character_id: int) -> int:
    """
    校验交互对象是否正在肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[7][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_ANAL_BEADS)
def handle_target_not_anal_beads(character_id: int) -> int:
    """
    校验交互对象是否没有在肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[7][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.HAVE_ANAL_PLUG)
def handle_have_anal_plug(character_id: int) -> int:
    """
    校验角色是否已持有肛塞
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    # if character_data.item[130] > 0:
    # return 1
    return 0
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1


@add_premise(constant_promise.Premise.HAVE_WHIP)
def handle_have_whip(character_id: int) -> int:
    """
    校验角色是否已持有鞭子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[131] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_NEEDLE)
def handle_have_needle(character_id: int) -> int:
    """
    校验角色是否已持有针
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[137] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CONDOM)
def handle_have_condom(character_id: int) -> int:
    """
    校验角色是否已持有避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[120] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_SAFE_CANDLES)
def handle_have_safe_candles(character_id: int) -> int:
    """
    校验角色是否已持有低温蜡烛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[136] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_COTTON_STICK)
def handle_have_cotton_stick(character_id: int) -> int:
    """
    校验角色是否已持有无菌棉签
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[139] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BIRTH_CONTROL_PILLS_BEFORE)
def handle_have_birth_control_pills_before(character_id: int) -> int:
    """
    校验角色是否已持有事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[101] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BIRTH_CONTROL_PILLS_AFTER)
def handle_have_birth_control_pills_after(character_id: int) -> int:
    """
    校验角色是否已持有事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[102] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BODY_LUBRICANT)
def handle_have_body_lubricant(character_id: int) -> int:
    """
    校验角色是否已持有润滑液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[100] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_PHILTER)
def handle_have_philter(character_id: int) -> int:
    """
    校验角色是否已持有媚药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[103] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_ENEMAS)
def handle_have_enemas(character_id: int) -> int:
    """
    校验角色是否已持有灌肠液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[104] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_DIURETICS_ONCE)
def handle_have_diuretics_once(character_id: int) -> int:
    """
    校验角色是否已持有一次性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[105] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_DIURETICS_PERSISTENT)
def handle_have_diuretics_persistent(character_id: int) -> int:
    """
    校验角色是否已持有持续性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[106] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_SLEEPING_PILLS)
def handle_have_sleeping_pills(character_id: int) -> int:
    """
    校验角色是否已持有安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[107] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CLOMID)
def handle_have_clomid(character_id: int) -> int:
    """
    校验角色是否已持有排卵促进药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[108] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_RING)
def handle_have_ring(character_id: int) -> int:
    """
    已持有戒指
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[201] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_COLLAR)
def handle_have_collar(character_id: int) -> int:
    """
    已持有项圈
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[202] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BAG)
def handle_have_bag(character_id: int) -> int:
    """
    已持有干员携袋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[151] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.A_SHIT)
def handle_a_shit(character_id: int) -> int:
    """
    自身肠内脏污
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_A_SHIT)
def handle_t_a_shit(character_id: int) -> int:
    """
    交互对象肠内脏污
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ENEMA)
def handle_enema(character_id: int) -> int:
    """
    自身正在灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_ENEMA)
def handle_t_enema(character_id: int) -> int:
    """
    交互对象正在灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_ENEMA)
def handle_not_enema(character_id: int) -> int:
    """
    自身非灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean not in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NOT_ENEMA)
def handle_t_not_enema(character_id: int) -> int:
    """
    交互对象非灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean not in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ENEMA_END)
def handle_enema_end(character_id: int) -> int:
    """
    自身已灌肠（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [2, 4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_ENEMA_END)
def handle_t_enema_end(character_id: int) -> int:
    """
    交互对象已灌肠（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [2, 4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NORMAL_ENEMA)
def handle_normal_enema(character_id: int) -> int:
    """
    自身普通灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NORMAL_ENEMA)
def handle_t_normal_enema(character_id: int) -> int:
    """
    交互对象普通灌肠中
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


@add_premise(constant_promise.Premise.SEMEN_ENEMA)
def handle_semen_enema(character_id: int) -> int:
    """
    自身精液灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SEMEN_ENEMA)
def handle_t_semen_enema(character_id: int) -> int:
    """
    交互对象精液灌肠中
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


@add_premise(constant_promise.Premise.NORMAL_ENEMA_END)
def handle_normal_enema_end(character_id: int) -> int:
    """
    自身已普通灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [2]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NORMAL_ENEMA_END)
def handle_t_normal_enema_end(character_id: int) -> int:
    """
    交互对象已普通灌肠
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


@add_premise(constant_promise.Premise.SEMEN_ENEMA_END)
def handle_semen_enema_end(character_id: int) -> int:
    """
    自身已精液灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SEMEN_ENEMA_END)
def handle_t_semen_enema_end(character_id: int) -> int:
    """
    交互对象已精液灌肠
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


@add_premise(constant_promise.Premise.T_HAIR_SEMEN)
def handle_t_hair_semen(character_id: int) -> int:
    """
    交互对象当前头发有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.body_semen[0][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WOMB_SEMEN)
def handle_t_womb_semen(character_id: int) -> int:
    """
    交互对象当前子宫有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.body_semen[7][1]:
        return 1
    return 0

@add_premise(constant_promise.Premise.VW_SEMEN_G_1)
def handle_vw_semen_g_1(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量大于1ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count > 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_G_1)
def handle_t_vw_semen_g_1(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量大于1ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count > 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_LE_200)
def handle_vw_semen_le_200(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量小于等于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count <= 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_LE_200)
def handle_t_vw_semen_le_200(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量小于等于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count <= 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_G_200)
def handle_vw_semen_g_200(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量大于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count > 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_G_200)
def handle_t_vw_semen_g_200(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量大于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count > 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_LE_1000)
def handle_vw_semen_le_1000(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量小于等于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count <= 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_LE_1000)
def handle_t_vw_semen_le_1000(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量小于等于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count <= 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_G_1000)
def handle_vw_semen_g_1000(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量大于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count > 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_G_1000)
def handle_t_vw_semen_g_1000(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量大于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count > 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_PENIS_SEMEN_DIRTY)
def handle_pl_penis_semen_dirty(character_id: int) -> int:
    """
    玩家阴茎上精液污浊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    penis_dirty = pl_character_data.dirty.penis_dirty_dict.get("semen", False)
    if penis_dirty:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_PENIS_NOT_SEMEN_DIRTY)
def handle_pl_penis_not_semen_dirty(character_id: int) -> int:
    """
    玩家阴茎上没有精液污浊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_pl_penis_semen_dirty(0):
        return 0
    return 1


@add_premise(constant_promise.Premise.URINATE_LE_49)
def handle_urinate_le_49(character_id: int) -> int:
    """
    尿意条≤49%，可以继续喝咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value <= 0.49:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_LE_79)
def handle_urinate_le_79(character_id: int) -> int:
    """
    尿意条≤79%，不需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_GE_80)
def handle_urinate_ge_80(character_id: int) -> int:
    """
    尿意条≥80%，需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value > 0.79:
        extra_value = character_data.urinate_point -  240 * 0.8
        return extra_value * 5
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_GE_125)
def handle_urinate_ge_125(character_id: int) -> int:
    """
    尿意条≥125%，需要当场排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value >= 1.25:
        return character_data.urinate_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_URINATE_LE_49)
def handle_target_urinate_le_49(character_id: int) -> int:
    """
    交互对象尿意条≤49%，可以继续喝咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.urinate_point / 240
    if value <= 0.49:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_URINATE_LE_79)
def handle_target_urinate_le_79(character_id: int) -> int:
    """
    交互对象尿意条≤79%，不需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.urinate_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_URINATE_GE_80)
def handle_target_urinate_ge_80(character_id: int) -> int:
    """
    交互对象尿意条≥80%，需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.urinate_point / 240
    if value > 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HUNGER_LE_79)
def handle_hunger_le_79(character_id: int) -> int:
    """
    饥饿值≤79%，不需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.hunger_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HUNGER_GE_80)
def handle_hunger_ge_80(character_id: int) -> int:
    """
    饥饿值≥80%，需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.hunger_point / 240
    if value > 0.79:
        # print(f"debug {character_id}角色饿了")
        extra_value = character_data.hunger_point -  240 * 0.8
        return extra_value * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HUNGER_LE_79)
def handle_target_hunger_le_79(character_id: int) -> int:
    """
    交互对象饥饿值≤79%，不需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.hunger_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HUNGER_GE_80)
def handle_target_hunger_ge_80(character_id: int) -> int:
    """
    交互对象饥饿值≥80%，需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.hunger_point / 240
    if value > 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_LE_29)
def handle_milk_le_29(character_id: int) -> int:
    """
    奶量≤29%，无法挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max
    if value <= 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_GE_30)
def handle_milk_ge_30(character_id: int) -> int:
    """
    奶量≥30%，可以挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max
    if value > 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_LE_79)
def handle_milk_le_79(character_id: int) -> int:
    """
    奶量≤79%，未涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_GE_80)
def handle_milk_ge_80(character_id: int) -> int:
    """
    奶量≥80%，涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.pregnancy.milk == 0:
        return 0

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max

    if value > 0.80:
        return character_data.pregnancy.milk
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_LE_29)
def handle_target_milk_le_29(character_id: int) -> int:
    """
    交互对象奶量≤29%，无法挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value <= 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_GE_30)
def handle_target_milk_ge_30(character_id: int) -> int:
    """
    交互对象奶量≥30%，可以挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value > 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_LE_79)
def handle_target_milk_le_79(character_id: int) -> int:
    """
    交互对象奶量≤79%，未涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_GE_80)
def handle_target_milk_ge_80(character_id: int) -> int:
    """
    交互对象奶量≥80%，涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value > 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_0)
def handle_sanity_point_0(character_id: int) -> int:
    """
    理智值为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_G_0)
def handle_sanity_point_g_0(character_id: int) -> int:
    """
    理智值不为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point > 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_L_5)
def handle_sanity_point_l_5(character_id: int) -> int:
    """
    理智值<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point < 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_5)
def handle_sanity_point_ge_5(character_id: int) -> int:
    """
    理智值≥5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_L_10)
def handle_sanity_point_l_10(character_id: int) -> int:
    """
    理智值<10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point < 10:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_10)
def handle_sanity_point_ge_10(character_id: int) -> int:
    """
    理智值≥10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 10:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_20)
def handle_sanity_point_ge_20(character_id: int) -> int:
    """
    理智值≥20
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 20:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_40)
def handle_sanity_point_ge_40(character_id: int) -> int:
    """
    理智值≥40
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 40:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_50)
def handle_sanity_point_ge_50(character_id: int) -> int:
    """
    理智值≥50
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 50:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.DESIRE_POINT_GE_80)
def handle_desire_point_ge_80(character_id: int) -> int:
    """
    欲望值≥80
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.desire_point >= 80:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.DESIRE_POINT_L_80)
def handle_desire_point_l_80(character_id: int) -> int:
    """
    欲望值<80
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.desire_point < 80:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.DESIRE_POINT_GE_100)
def handle_desire_point_ge_100(character_id: int) -> int:
    """
    欲望值≥100
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.desire_point >= 100:
        return character_data.desire_point * 2
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_0)
def handle_sleep_level_0(character_id: int) -> int:
    """
    睡眠等级：半梦半醒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_1)
def handle_sleep_level_1(character_id: int) -> int:
    """
    睡眠等级：浅睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_2)
def handle_sleep_level_2(character_id: int) -> int:
    """
    睡眠等级：熟睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_3)
def handle_sleep_level_3(character_id: int) -> int:
    """
    睡眠等级：完全深眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 3:
        return 1
    else:
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


@add_premise(constant_promise.Premise.TARGET_WEAR_HAT)
def handle_t_wear_hat(character_id: int) -> int:
    """
    交互对象穿着帽子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[0]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_HAT)
def handle_t_not_wear_hat(character_id: int) -> int:
    """
    交互对象没有穿着帽子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_not_wear_hat(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_GLASS)
def handle_t_wear_glass(character_id: int) -> int:
    """
    交互对象戴着眼镜
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[1]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_GLASS)
def handle_t_not_wear_glass(character_id: int) -> int:
    """
    交互对象没有戴着眼镜
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_glass(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_IN_EAR)
def handle_t_wear_in_ear(character_id: int) -> int:
    """
    交互对象戴耳饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[2]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_EAR)
def handle_t_not_wear_in_ear(character_id: int) -> int:
    """
    交互对象没有戴耳饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_ear(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_IN_NECK)
def handle_t_wear_in_neck(character_id: int) -> int:
    """
    交互对象戴脖饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[3]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_NECK)
def handle_t_not_wear_in_neck(character_id: int) -> int:
    """
    交互对象没有戴脖饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_neck(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_IN_MOUSE)
def handle_t_wear_in_mouse(character_id: int) -> int:
    """
    交互对象戴口饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[4]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_MOUSE)
def handle_t_not_wear_in_mouse(character_id: int) -> int:
    """
    交互对象没有戴口饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_mouse(character_id)


@add_premise(constant_promise.Premise.WEAR_IN_UP)
def handle_wear_in_up(character_id: int) -> int:
    """
    穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[5]):
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_WEAR_IN_UP)
def handle_not_wear_in_up(character_id: int) -> int:
    """
    没有穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_wear_in_up(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_WEAR_IN_UP)
def handle_t_wear_in_up(character_id: int) -> int:
    """
    交互对象穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_wear_in_up(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_UP)
def handle_t_not_wear_in_up(character_id: int) -> int:
    """
    交互对象没有穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_wear_in_up(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.WEAR_BRA)
def handle_wear_bra(character_id: int) -> int:
    """
    穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[6]):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NOT_WEAR_BRA)
def handle_not_wear_bra(character_id: int) -> int:
    """
    没有穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_wear_bra(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_BRA)
def handle_t_wear_bra(character_id: int) -> int:
    """
    交互对象穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_wear_bra(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_BRA)
def handle_t_not_wear_bra(character_id: int) -> int:
    """
    交互对象没有穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_wear_bra(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_GLOVES)
def handle_t_wear_gloves(character_id: int) -> int:
    """
    交互对象戴着手套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[7]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_GLOVES)
def handle_t_not_wear_gloves(character_id: int) -> int:
    """
    交互对象没有戴着手套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_gloves(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_IN_DOWN)
def handle_t_wear_in_down(character_id: int) -> int:
    """
    交互对象穿着下衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[8]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_DOWN)
def handle_t_not_wear_in_down(character_id: int) -> int:
    """
    交互对象没有穿着下衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_down(character_id)


@add_premise(constant_promise.Premise.WEAR_SKIRT)
def handle_wear_skirt(character_id: int) -> int:
    """
    穿着裙子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[8]):
        cloth_id = character_data.cloth.cloth_wear[8][0]
        if game_config.config_clothing_tem[cloth_id].tag == 5:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_WEAR_SKIRT)
def handle_t_wear_skirt(character_id: int) -> int:
    """
    交互对象穿着裙子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[8]):
        cloth_id = target_data.cloth.cloth_wear[8][0]
        if game_config.config_clothing_tem[cloth_id].tag == 5:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_WEAR_TROUSERS)
def handle_t_wear_trousers(character_id: int) -> int:
    """
    交互对象穿着裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[8]):
        cloth_id = target_data.cloth.cloth_wear[8][0]
        if game_config.config_clothing_tem[cloth_id].tag == 4:
            return 1
    return 0


@add_premise(constant_promise.Premise.WEAR_PAN)
def handle_wear_pan(character_id: int) -> int:
    """
    穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[9]):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NOT_WEAR_PAN)
def handle_not_wear_pan(character_id: int) -> int:
    """
    没有穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_wear_pan(character_id)


@add_premise(constant_promise.Premise.TARGET_WEAR_PAN)
def handle_t_wear_pan(character_id: int) -> int:
    """
    交互对象穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[9]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_PAN)
def handle_t_not_wear_pan(character_id: int) -> int:
    """
    交互对象没有穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_pan(character_id)


@add_premise(constant_promise.Premise.NOW_WEAR_BRA_OR_PAN)
def handle_not_wear_bra_or_pan(character_id: int) -> int:
    """
    自己没有穿着胸衣或内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_not_wear_bra(character_id) or handle_not_wear_pan(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.WEAR_SOCKS)
def handle_wear_socks(character_id: int) -> int:
    """
    穿着袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[10]):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_WEAR_SOCKS)
def handle_t_wear_socks(character_id: int) -> int:
    """
    交互对象穿着袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_wear_socks(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_SOCKS)
def handle_t_not_wear_socks(character_id: int) -> int:
    """
    交互对象没有穿着袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_wear_socks(character_data.target_character_id)


@add_premise(constant_promise.Premise.NOT_WEAR_SHOES)
def handle_not_wear_shoes(character_id: int) -> int:
    """
    没有穿着鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[11]):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.TARGET_WEAR_SHOES)
def handle_t_wear_shoes(character_id: int) -> int:
    """
    交互对象穿着鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[11]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_SHOES)
def handle_t_not_wear_shoes(character_id: int) -> int:
    """
    交互对象没有穿着鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_shoes(character_id)


@add_premise(constant_promise.Premise.TARGET_TAKE_WEAPON)
def handle_t_take_weapon(character_id: int) -> int:
    """
    交互对象拿着武器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[12]):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_TAKE_WEAPON)
def handle_t_not_take_weapon(character_id: int) -> int:
    """
    交互对象没有拿着武器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_take_weapon(character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_TAKE_EXTRAS)
def handle_t_not_take_extras(character_id: int) -> int:
    """
    交互对象没有拿着附属物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[13]):
        return 0
    return 1


@add_premise(constant_promise.Premise.CLOTH_OFF)
def handle_cloth_off(character_id: int) -> int:
    """
    当前全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for clothing_type in game_config.config_clothing_type:
        if len(character_data.cloth.cloth_wear[clothing_type]):
            return 0
    return 1


@add_premise(constant_promise.Premise.NOT_CLOTH_OFF)
def handle_not_cloth_off(character_id: int) -> int:
    """
    当前不是全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_cloth_off(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.CLOTH_MOST_OFF)
def handle_cloth_most_off(character_id: int) -> int:
    """
    当前大致全裸（没穿上下外衣内衣）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for clothing_type in [5, 6, 8, 9]:
        if len(character_data.cloth.cloth_wear[clothing_type]):
            return 0
    return 1


@add_premise(constant_promise.Premise.NOT_CLOTH_MOST_OFF)
def handle_not_cloth_most_off(character_id: int) -> int:
    """
    当前不是大致全裸（没穿上下外衣内衣）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_cloth_most_off(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SHOWER_CLOTH)
def handle_shower_cloth(character_id: int) -> int:
    """
    围着浴巾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 551 in character_data.cloth.cloth_wear[5] and 851 in character_data.cloth.cloth_wear[8]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_SHOWER_CLOTH)
def handle_not_shower_cloth(character_id: int) -> int:
    """
    没有围着浴巾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_shower_cloth(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SLEEP_CLOTH)
def handle_sleep_cloth(character_id: int) -> int:
    """
    穿着睡衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 552 in character_data.cloth.cloth_wear[5] and 852 in character_data.cloth.cloth_wear[8]:
        return 1
    elif 553 in character_data.cloth.cloth_wear[5] and 853 in character_data.cloth.cloth_wear[8]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SLEEP_CLOTH_OR_NOT_NORMAL_4)
def handle_sleep_cloth_or_not_normal_4(character_id: int) -> int:
    """
    穿着睡衣或服装异常
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_sleep_cloth(character_id):
        return 1
    elif not handle_normal_4(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAT_SEMEN)
def handle_hat_semen(character_id: int) -> int:
    """
    自身当前帽子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[0][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAT_SEMEN)
def handle_t_hat_semen(character_id: int) -> int:
    """
    交互对象当前帽子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[0][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.GLASS_SEMEN)
def handle_glass_semen(character_id: int) -> int:
    """
    自身当前眼镜有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[1][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_GLASS_SEMEN)
def handle_t_glass_semen(character_id: int) -> int:
    """
    交互对象当前眼镜有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[1][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_EAR_SEMEN)
def handle_in_ear_semen(character_id: int) -> int:
    """
    自身当前耳饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[2][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_IN_EAR_SEMEN)
def handle_t_in_ear_semen(character_id: int) -> int:
    """
    交互对象当前耳饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[2][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_NECK_SEMEN)
def handle_in_neck_semen(character_id: int) -> int:
    """
    自身当前脖饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[3][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_IN_NECK_SEMEN)
def handle_t_in_neck_semen(character_id: int) -> int:
    """
    交互对象当前脖饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[3][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_MOUSE_SEMEN)
def handle_in_mouse_semen(character_id: int) -> int:
    """
    自身当前口饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[4][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_IN_MOUSE_SEMEN)
def handle_t_in_mouse_semen(character_id: int) -> int:
    """
    交互对象当前口饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[4][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.UP_CLOTH_SEMEN)
def handle_up_cloth_semen(character_id: int) -> int:
    """
    自身当前上衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[5][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UP_CLOTH_SEMEN)
def handle_t_up_cloth_semen(character_id: int) -> int:
    """
    交互对象当前上衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[5][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.BRA_SEMEN)
def handle_bra_semen(character_id: int) -> int:
    """
    自身当前胸衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[6][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BRA_SEMEN)
def handle_t_bra_semen(character_id: int) -> int:
    """
    交互对象当前胸衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[6][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.GLOVE_SEMEN)
def handle_glove_semen(character_id: int) -> int:
    """
    自身当前手套有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[7][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_GLOVE_SEMEN)
def handle_t_glove_semen(character_id: int) -> int:
    """
    交互对象当前手套有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[7][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.DOWN_CLOTH_SEMEN)
def handle_down_cloth_semen(character_id: int) -> int:
    """
    自身当前下衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[8][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BOTTOM_CLOTH_SEMEN)
def handle_t_botton_cloth_semen(character_id: int) -> int:
    """
    交互对象当前下衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[8][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.PAN_SEMEN)
def handle_pan_semen(character_id: int) -> int:
    """
    自身当前内裤有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[9][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_PAN_SEMEN)
def handle_t_pan_semen(character_id: int) -> int:
    """
    交互对象当前内裤有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[9][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SOCKS_SEMEN)
def handle_socks_semen(character_id: int) -> int:
    """
    自身当前袜子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[10][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SOCKS_SEMEN)
def handle_t_socks_semen(character_id: int) -> int:
    """
    交互对象当前袜子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[10][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOES_SEMEN)
def handle_shoes_semen(character_id: int) -> int:
    """
    自身当前鞋子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[11][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SHOES_SEMEN)
def handle_t_shoes_semen(character_id: int) -> int:
    """
    交互对象当前鞋子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[11][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.WEAPON_SEMEN)
def handle_weapon_semen(character_id: int) -> int:
    """
    自身当前武器有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[12][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WEAPON_SEMEN)
def handle_t_weapon_semen(character_id: int) -> int:
    """
    交互对象当前武器有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[12][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.EXTRAS_SEMEN)
def handle_extras_semen(character_id: int) -> int:
    """
    自身当前附属物有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[13][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXTRAS_SEMEN)
def handle_t_extras_semen(character_id: int) -> int:
    """
    交互对象当前附属物有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[13][1]:
        return 1
    return 0


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
    玩家已启用H模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    return target_data.sp_flag.is_h


@add_premise(constant_promise.Premise.NOT_H)
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
    return not target_data.sp_flag.is_h


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


@add_premise(constant_promise.Premise.GROUP_SEX_MODE_ON)
def handle_group_sex_mode_on(character_id: int) -> int:
    """
    多P模式开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.group_sex_mode


@add_premise(constant_promise.Premise.GROUP_SEX_MODE_OFF)
def handle_group_sex_mode_off(character_id: int) -> int:
    """
    多P模式未开启
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
    该事件在已触发记录中(需搭配记录结算)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 本前提在以下地方进行调用，此处不进行实际处理
    # Script/Design/event.py#L11
    return 0


@add_premise(constant_promise.Premise.THIS_EVENT_NOT_IN_TRIGGERED_RECORD)
def handle_this_event_not_in_triggered_record(character_id: int) -> int:
    """
    该事件不在已触发记录中(需搭配记录结算)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 本前提在以下地方进行调用，此处不进行实际处理
    # Script/Design/event.py#L11
    return 0


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


@add_premise(constant_promise.Premise.IS_ASSISTANT)
def handle_is_assistant(character_id: int) -> int:
    """
    自己是当前的助理干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    if pl_character_data.assistant_character_id == character_id:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_ASSISTANT)
def handle_not_assistant(character_id: int) -> int:
    """
    自己不是当前的助理干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    if pl_character_data.assistant_character_id == character_id:
        return 0
    return 1


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
    pl_character_data: game_type.Character = cache.character_data[0]
    if pl_character_data.assistant_character_id == character_data.target_character_id:
        return 1
    return 0


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
    pl_character_data: game_type.Character = cache.character_data[0]
    if pl_character_data.assistant_character_id == character_data.target_character_id:
        return 0
    return 1


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
    if character_data.assistant_services[7] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASSISTANT_LIVE_TOGETHER_OFF)
def handle_assistant_live_together_off(character_id: int) -> int:
    """
    自己的助理属性为未同居
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_assistant_live_together_on(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.ASK_GIVE_PAN_EVERYDAY)
def handle_ask_give_pan_everyday(character_id: int) -> int:
    """
    自己被要求每天上交内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[1]


@add_premise(constant_promise.Premise.ASK_GIVE_SOCKS_EVERYDAY)
def handle_ask_give_socks_everyday(character_id: int) -> int:
    """
    自己被要求每天上交袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[2]


@add_premise(constant_promise.Premise.ASK_NOT_WEAR_CORSET)
def handle_ask_not_wear_corset(character_id: int) -> int:
    """
    自己被要求以后不再穿胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[3]


@add_premise(constant_promise.Premise.ASK_NOT_WEAR_CLOTH_IN_SLEEP)
def handle_ask_not_wear_cloth_in_sleep(character_id: int) -> int:
    """
    自己被要求以后睡觉时不穿衣服裸睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[4]


@add_premise(constant_promise.Premise.ASK_EQUP_NIPPLE_CLAMP_IN_DAY)
def handle_ask_equp_nipple_clamp_in_day(character_id: int) -> int:
    """
    自己被要求白天时戴着乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[11]


@add_premise(constant_promise.Premise.ASK_EQUP_CLIT_CLAMP_IN_DAY)
def handle_ask_equp_clit_clamp_in_day(character_id: int) -> int:
    """
    自己被要求白天时戴着阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[12]


@add_premise(constant_promise.Premise.ASK_EQUP_V_VIBRATOR_IN_DAY)
def handle_ask_equp_v_bibrator_in_day(character_id: int) -> int:
    """
    自己被要求白天时V里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[13]


@add_premise(constant_promise.Premise.ASK_EQUP_A_VIBRATOR_IN_DAY)
def handle_ask_equp_a_bibrator_in_day(character_id: int) -> int:
    """
    自己被要求白天时A里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[14]


@add_premise(constant_promise.Premise.ASK_EQUP_NIPPLE_CLAMP_IN_SLEEP)
def handle_ask_equp_nipple_clamp_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时戴着乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[15]


@add_premise(constant_promise.Premise.ASK_EQUP_CLIT_CLAMP_IN_SLEEP)
def handle_ask_equp_clit_clamp_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时戴着阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[16]


@add_premise(constant_promise.Premise.ASK_EQUP_V_VIBRATOR_IN_SLEEP)
def handle_ask_equp_v_bibrator_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时V里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[17]


@add_premise(constant_promise.Premise.ASK_EQUP_A_VIBRATOR_IN_SLEEP)
def handle_ask_equp_a_bibrator_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时A里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[18]


@add_premise(constant_promise.Premise.ASK_NOT_WASH_SEMEN)
def handle_ask_not_wash_semen(character_id: int) -> int:
    """
    自己被要求洗澡时不再清洗阴道内的精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[21]


@add_premise(constant_promise.Premise.ASK_MASTURBATION_BEFORE_SLEEP)
def handle_ask_masturbation_before_sleep(character_id: int) -> int:
    """
    自己被要求每天晚上睡前都要自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[22]


@add_premise(constant_promise.Premise.ASK_NOT_MASTURBATION)
def handle_ask_not_masturbation(character_id: int) -> int:
    """
    自己被要求禁止自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[23]


@add_premise(constant_promise.Premise.NOT_ASK_NOT_MASTURBATION)
def handle_not_ask_not_masturbation(character_id: int) -> int:
    """
    自己没有被要求禁止自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_ask_not_masturbation(character_id)


@add_premise(constant_promise.Premise.ASK_NONE_EXERCISES)
def handle_ask_none_exercises(character_id: int) -> int:
    """
    自己没有被要求进行任何练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_ask_one_exercises(character_id)


@add_premise(constant_promise.Premise.ASK_ONE_EXERCISES)
def handle_ask_one_exercises(character_id: int) -> int:
    """
    自己被要求进行了至少一项练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for i in range(30,40):
        if i in character_data.body_manage and character_data.body_manage[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.ASK_GE_3_EXERCISES)
def handle_ask_ge_3_exercises(character_id: int) -> int:
    """
    自己被要求进行了至少3项练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    count = 0
    for i in range(30,40):
        if i in character_data.body_manage and character_data.body_manage[i]:
            count += 1
    if count >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASK_SUCKING_AND_SWALLOWING_EXERCISES)
def handle_ask_sucking_and_swallowing_exercises(character_id: int) -> int:
    """
    自己被要求进行吮吸与吞咽力练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[31]


@add_premise(constant_promise.Premise.ASK_ARMPIT_CLAMPING_EXERCISES)
def handle_ask_armpit_clamping_exercises(character_id: int) -> int:
    """
    自己被要求进行腋下夹持力练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[32]


@add_premise(constant_promise.Premise.ASK_BREAST_CLAMPING_EXERCISES)
def handle_ask_breast_clamping_exercise(character_id: int) -> int:
    """
    自己被要求进行胸部夹持力练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[33]


@add_premise(constant_promise.Premise.ASK_HANDS_FLEXIBILITY_EXERCISES)
def handle_ask_hands_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行手部灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[34]


@add_premise(constant_promise.Premise.ASK_FOOTS_FLEXIBILITY_EXERCISES)
def handle_ask_foots_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行足部灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[35]


@add_premise(constant_promise.Premise.ASK_VAGINA_FIRMNESS_EXERCISES)
def handle_ask_vagina_firmness_exercises(character_id: int) -> int:
    """
    自己被要求进行阴道紧致度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[36]


@add_premise(constant_promise.Premise.ASK_INTESTINE_FIRMNESS_EXERCISES)
def handle_ask_intestine_firmness_exercises(character_id: int) -> int:
    """
    自己被要求进行肠道紧致度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[37]


@add_premise(constant_promise.Premise.ASK_TAIL_FLEXIBILITY_EXERCISES)
def handle_ask_tail_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行尾巴灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[38]


@add_premise(constant_promise.Premise.ASK_TENTACLE_FLEXIBILITY_EXERCISES)
def handle_ask_tentacle_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行触手灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[39]


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
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_follow:
        return 0
    else:
        return 1


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


@add_premise(constant_promise.Premise.T_NFEEL_GE_1)
def handle_t_nfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_GE_3)
def handle_t_nfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_GE_5)
def handle_t_nfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_GE_7)
def handle_t_nfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_L_1)
def handle_t_nfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_L_3)
def handle_t_nfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_L_5)
def handle_t_nfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_1)
def handle_t_bfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_3)
def handle_t_bfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_5)
def handle_t_bfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_7)
def handle_t_bfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_L_1)
def handle_t_bfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_L_3)
def handle_t_bfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_L_5)
def handle_t_bfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_1)
def handle_t_cfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_3)
def handle_t_cfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_5)
def handle_t_cfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_7)
def handle_t_cfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_L_1)
def handle_t_cfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_L_3)
def handle_t_cfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_L_5)
def handle_t_cfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_1)
def handle_pfeel_ge_1(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_3)
def handle_pfeel_ge_3(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_5)
def handle_pfeel_ge_5(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_7)
def handle_pfeel_ge_7(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_L_1)
def handle_pfeel_l_1(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_L_3)
def handle_pfeel_l_3(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_L_5)
def handle_pfeel_l_5(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_1)
def handle_t_vfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_3)
def handle_t_vfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_5)
def handle_t_vfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_7)
def handle_t_vfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_L_1)
def handle_t_vfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_L_3)
def handle_t_vfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_L_5)
def handle_t_vfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_1)
def handle_t_afeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_3)
def handle_t_afeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_5)
def handle_t_afeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_7)
def handle_t_afeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_L_1)
def handle_t_afeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_L_3)
def handle_t_afeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_L_5)
def handle_t_afeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_1)
def handle_t_ufeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_3)
def handle_t_ufeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_5)
def handle_t_ufeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_7)
def handle_t_ufeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_L_1)
def handle_t_ufeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_L_3)
def handle_t_ufeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_L_5)
def handle_t_ufeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_1)
def handle_t_wfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_3)
def handle_t_wfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_5)
def handle_t_wfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_7)
def handle_t_wfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_L_1)
def handle_t_wfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_L_3)
def handle_t_wfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_L_5)
def handle_t_wfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_1)
def handle_t_u_dilate_ge_1(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_2)
def handle_t_u_dilate_ge_2(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_3)
def handle_t_u_dilate_ge_3(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_5)
def handle_t_u_dilate_ge_5(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_W_DILATE_GE_3)
def handle_t_w_dilate_ge_3(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｗ扩张>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[12] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_W_DILATE_GE_5)
def handle_t_w_dilate_ge_5(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｗ扩张>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[12] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_1)
def handle_s_ge_1(character_id: int) -> int:
    """
    校验角色是否施虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_3)
def handle_s_ge_3(character_id: int) -> int:
    """
    校验角色是否施虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_5)
def handle_s_ge_5(character_id: int) -> int:
    """
    校验角色是否施虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_7)
def handle_s_ge_7(character_id: int) -> int:
    """
    校验角色是否施虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_L_1)
def handle_s_l_1(character_id: int) -> int:
    """
    校验角色是否施虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_L_3)
def handle_s_l_3(character_id: int) -> int:
    """
    校验角色是否施虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_L_5)
def handle_s_l_5(character_id: int) -> int:
    """
    校验角色是否施虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_1)
def handle_t_s_ge_1(character_id: int) -> int:
    """
    校验交互对象是否施虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_3)
def handle_t_s_ge_3(character_id: int) -> int:
    """
    校验交互对象是否施虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_5)
def handle_t_s_ge_5(character_id: int) -> int:
    """
    校验交互对象是否施虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_7)
def handle_t_s_ge_7(character_id: int) -> int:
    """
    校验交互对象是否施虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_L_1)
def handle_t_s_l_1(character_id: int) -> int:
    """
    校验交互对象是否施虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_L_3)
def handle_t_s_l_3(character_id: int) -> int:
    """
    校验交互对象是否施虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_L_5)
def handle_t_s_l_5(character_id: int) -> int:
    """
    校验交互对象是否施虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_1)
def handle_m_ge_1(character_id: int) -> int:
    """
    校验角色是否受虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_3)
def handle_m_ge_3(character_id: int) -> int:
    """
    校验角色是否受虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_5)
def handle_m_ge_5(character_id: int) -> int:
    """
    校验角色是否受虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_7)
def handle_m_ge_7(character_id: int) -> int:
    """
    校验角色是否受虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_L_1)
def handle_m_l_1(character_id: int) -> int:
    """
    校验角色是否受虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_L_3)
def handle_m_l_3(character_id: int) -> int:
    """
    校验角色是否受虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_L_5)
def handle_m_l_5(character_id: int) -> int:
    """
    校验角色是否受虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_1)
def handle_t_m_ge_1(character_id: int) -> int:
    """
    校验交互对象是否受虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_3)
def handle_t_m_ge_3(character_id: int) -> int:
    """
    校验交互对象是否受虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_5)
def handle_t_m_ge_5(character_id: int) -> int:
    """
    校验交互对象是否受虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_7)
def handle_t_m_ge_7(character_id: int) -> int:
    """
    校验交互对象是否受虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_L_1)
def handle_t_m_l_1(character_id: int) -> int:
    """
    校验交互对象是否受虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_L_3)
def handle_t_m_l_3(character_id: int) -> int:
    """
    校验交互对象是否受虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_L_5)
def handle_t_m_l_5(character_id: int) -> int:
    """
    校验交互对象是否受虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_1)
def handle_t_submit_ge_1(character_id: int) -> int:
    """
    校验交互对象是否顺从>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_3)
def handle_t_submit_ge_3(character_id: int) -> int:
    """
    校验交互对象是否顺从>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_5)
def handle_t_submit_ge_5(character_id: int) -> int:
    """
    校验交互对象是否顺从>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_7)
def handle_t_submit_ge_7(character_id: int) -> int:
    """
    校验交互对象是否顺从>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_L_1)
def handle_t_submit_l_1(character_id: int) -> int:
    """
    校验交互对象是否顺从<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_L_3)
def handle_t_submit_l_3(character_id: int) -> int:
    """
    校验交互对象是否顺从<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_L_5)
def handle_t_submit_l_5(character_id: int) -> int:
    """
    校验交互对象是否顺从<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LOVE_SENSE_TASTE_0)
def handle_t_love_sense_taste_0(character_id: int) -> int:
    """
    校验交互对象是否精爱味觉==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[31] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_SEXUAL_IGNORANCE_0)
def handle_self_sexual_ignorance_0(character_id: int) -> int:
    """
    校验自己没有性无知
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[222] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_SEXUAL_IGNORANCE_1)
def handle_self_sexual_ignorance_1(character_id: int) -> int:
    """
    校验自己有性无知
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[222] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LOVE_SENSE_TASTE_1)
def handle_t_love_sense_taste_1(character_id: int) -> int:
    """
    校验交互对象是否精爱味觉==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[31] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SADISM_0)
def handle_t_sadism_0(character_id: int) -> int:
    """
    校验交互对象是否施虐狂==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[229] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SADISM_1)
def handle_t_sadism_1(character_id: int) -> int:
    """
    校验交互对象是否施虐狂==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[229] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_MASOCHISM_0)
def handle_t_masochism_0(character_id: int) -> int:
    """
    校验交互对象是否受虐狂==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[230] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_MASOCHISM_1)
def handle_t_masochism_1(character_id: int) -> int:
    """
    校验交互对象是否受虐狂==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[230] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_OESTRUS_0)
def handle_t_oestrus_0(character_id: int) -> int:
    """
    校验交互对象是否发情期==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[62] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_OESTRUS_1)
def handle_t_oestrus_1(character_id: int) -> int:
    """
    校验交互对象是否发情期==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[62] == 1:
        return 1
    return 0


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


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_1)
def handle_t_exhibit_ge_1(character_id: int) -> int:
    """
    校验交互对象是否露出>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_3)
def handle_t_exhibit_ge_3(character_id: int) -> int:
    """
    校验交互对象是否露出>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_5)
def handle_t_exhibit_ge_5(character_id: int) -> int:
    """
    校验交互对象是否露出>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_7)
def handle_t_exhibit_ge_7(character_id: int) -> int:
    """
    校验交互对象是否露出>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_L_1)
def handle_t_exhibit_l_1(character_id: int) -> int:
    """
    校验交互对象是否露出<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_L_3)
def handle_t_exhibit_l_3(character_id: int) -> int:
    """
    校验交互对象是否露出<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_L_5)
def handle_t_exhibit_l_5(character_id: int) -> int:
    """
    校验交互对象是否露出<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_1)
def handle_t_happy_mark_1(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_2)
def handle_t_happy_mark_2(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_3)
def handle_t_happy_mark_3(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_GE_1)
def handle_t_happy_mark_ge_1(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_LE_2)
def handle_t_happy_mark_le_2(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印<=2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] <= 2:
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
    character_data = cache.character_data[0]
    last_state = character_data.last_state[-1]
    if last_state == constant.CharacterStatus.STATUS_SLEEP:
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
    character_data = cache.character_data[0]
    last_state = character_data.last_state[-1]
    if last_state == constant.CharacterStatus.STATUS_SLEEP:
        return 0
    return 1


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
    if character_data.state == constant.CharacterStatus.STATUS_SLEEP:
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
    if character_data.state == constant.CharacterStatus.STATUS_SLEEP:
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
    if target_data.state == constant.CharacterStatus.STATUS_SLEEP:
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
    if target_data.state == constant.CharacterStatus.STATUS_SLEEP:
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
    if character_data.state == constant.CharacterStatus.STATUS_REST:
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
    if character_data.state == constant.CharacterStatus.STATUS_MOVE:
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
    if 151 <= character_data.state <= 250:
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


@add_premise(constant_promise.Premise.SELF_IS_CHILD)
def handle_self_is_child(character_id: int) -> int:
    """
    校验自己是幼女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[102] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CHILD_OR_LOLI_1)
def handle_t_child_or_loli_1(character_id: int) -> int:
    """
    校验交互对象是否幼女或萝莉==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[102] == 1 or target_data.talent[103] == 1:
        return 1
    return 0
