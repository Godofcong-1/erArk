"""上课时段的行为决策（Plan 22 一期 §2.8）

每到一个上课节次，孩子（或选了课的干员）要先过两道闸，再决定这一节实际去做什么：

    1. 体力闸（方案 §3.14）：体力低于30%就上不动课了，转为休息并累计一节缺课。
       ⚠️ 这是**被动**缺课，不置翘课flag、不触发「翘课被抓」事件。
    2. 心情闸（方案 §3.19）：苦痛(17)+恐怖(18)+抑郁(19)+反感(20)四个负面状态的**等级**和
       越高，越可能主动翘课。判定写法照 `Script/Design/instuct_judege.py:103~104` 的实行值修正。

两道闸的顺序不能反：体力不足是"去不了"，心情糟糕是"不想去"，一个孩子累到爬不起来时
不该再被算一次"叛逆"。

过闸之后按课型派发。班级式的教室课走既有的 移动→听课 链，本节没有可用教师时降级为自习。
个人式的体育/兴趣/实习课则是"人到地点，执行该地点既有的行为"：体育课去木桩房打木桩、
兴趣课去棋牌室下棋、实习课去厨房跟着厨师。
"""
import random
from typing import Optional
from Script.Core import cache_control, game_type, constant
from Script.Design import attr_calculation, game_time, map_handle
from Script.System.Education_System import schedule_handle, growth_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

ABSENT_HP_RATE = 0.3
""" 体力低于该比例则本节缺课去休息。取值与既有前提 `handle_premise_base_value.py:46 handle_hp_low`
    的"体力低"口径一致，不另立一套阈值 """

NEGATIVE_STATE_ID_LIST = [17, 18, 19, 20]
""" 参与翘课判定的四个负面状态：苦痛17 / 恐怖18 / 抑郁19 / 反感20。
    与 `Script/Core/rich_text.py:255~258` 归为负面色的那一组一致 """

SKIP_CLASS_RATE_TABLE = [
    (4, 0.0),
    (8, 0.10),
    (12, 0.25),
    (16, 0.45),
]
""" 翘课概率阶梯（草案，实施时以实测为准）：(等级和上界, 概率)，达不到第一档则为0，
    超过最后一档取 SKIP_CLASS_RATE_MAX。四项各0~8级，理论最大和32 """

SKIP_CLASS_RATE_MAX = 0.70
""" 四项等级和达16以上（濒临崩溃）时的每节翘课概率 """


def get_negative_status_level_sum(character_id: int) -> int:
    """
    取角色四个负面状态的等级和（不是原始数值和）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 苦痛/恐怖/抑郁/反感四项的等级之和，0~32
    """
    character_data: game_type.Character = cache.character_data[character_id]
    level_sum = 0
    for state_id in NEGATIVE_STATE_ID_LIST:
        level_sum += attr_calculation.get_status_level(character_data.status_data.get(state_id, 0))
    return level_sum


def get_skip_class_rate(character_id: int) -> float:
    """
    按四个负面状态的等级和查出每节课的翘课概率
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    float -- 0.0~0.7 的概率
    """
    level_sum = get_negative_status_level_sum(character_id)
    for max_sum, rate in SKIP_CLASS_RATE_TABLE:
        if level_sum < max_sum:
            return rate
    return SKIP_CLASS_RATE_MAX


def judge_teacher_available(teacher_id: int) -> bool:
    """
    判断被排进课表的教师本节能不能到岗（方案 §3.5：H/监禁/外勤/外交访问时本节降级为自习）
    Keyword arguments:
    teacher_id -- 教师的角色id，-1表示课表上本就没排教师
    Return arguments:
    bool -- 是否可授课
    """
    if teacher_id == -1 or teacher_id not in cache.character_data:
        return False
    teacher_data: game_type.Character = cache.character_data[teacher_id]
    if teacher_data.dead:
        return False
    # 这几种状态下教师人不在教室，或不可能讲课
    if teacher_data.sp_flag.is_h or teacher_data.sp_flag.imprisonment:
        return False
    if teacher_data.sp_flag.field_commission or teacher_data.sp_flag.in_diplomatic_visit:
        return False
    return True


def judge_in_scene(character_id: int, scene_name: str) -> bool:
    """
    判断角色此刻是否就在指定名字的场景里
    Keyword arguments:
    character_id -- 角色id
    scene_name -- 场景名
    Return arguments:
    bool -- 是否在该场景
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if now_scene_str not in cache.scene_data:
        return False
    return cache.scene_data[now_scene_str].scene_name == scene_name


def settle_absent(character_id: int) -> None:
    """
    记一节缺课。⚠️ 同一节课只记一次——休息行为30分钟、一节课45分钟，
    不做去重会在同一节课里被反复累加，成绩单的出勤率就废了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    growth_data = growth_handle.get_child_growth(character_id)
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    now_mark = [now_time.toordinal(), game_time.get_class_period(character_id)]
    if growth_data.last_absent_period == now_mark:
        return
    growth_data.last_absent_period = now_mark
    growth_data.absent_count += 1


def judge_class_state_machine(character_id: int) -> int:
    """
    上课时段的行为决策总入口，返回本节该执行的状态机id
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 状态机id，0表示本函数不接管、交回既有AI链
    """
    now_course = schedule_handle.get_now_course(character_id)
    # 不在节次内、或本节没排课 —— 自由行动
    if now_course is None:
        return 0
    character_data: game_type.Character = cache.character_data[character_id]

    # 第一道闸：体力。上不动课就去休息，并记一节缺课
    if character_data.hit_point_max and character_data.hit_point / character_data.hit_point_max < ABSENT_HP_RATE:
        settle_absent(character_id)
        return constant.StateMachine.REST

    # 第二道闸：心情。今日已经翘了就翘到底，否则按四个负面状态的等级和掷一次
    growth_data = growth_handle.get_child_growth(character_id)
    if growth_data.skip_class_flag:
        return constant.StateMachine.EDUCATION_SKIP_CLASS
    skip_rate = get_skip_class_rate(character_id)
    if skip_rate and random.random() < skip_rate:
        return constant.StateMachine.EDUCATION_SKIP_CLASS

    # 派课：班级式的教室课
    if now_course["course_type"] in schedule_handle.CLASSROOM_COURSE_TYPE_SET:
        classroom = now_course["classroom"]
        # 人还没到教室，先走既有的移动状态机（它会按课表挑对教室，见 StateMachine/default.py:434）
        if not judge_in_scene(character_id, classroom):
            return constant.StateMachine.MOVE_TO_CLASS_ROOM
        # 到了教室，看本节有没有能讲课的老师；没有则降级自习
        if judge_teacher_available(now_course["teacher_id"]):
            return constant.StateMachine.WORK_ATTENT_CLASS
        return constant.StateMachine.EDUCATION_SELF_STUDY

    # 派课：个人式的体育/兴趣/实习课——人到地点，然后执行该课对应的既有行为
    to_place = schedule_handle.get_course_place(now_course)
    # 地点解析不出来（娱乐没配地点标签、岗位场景未解锁、体育课地点写错）就交回既有AI，不留死分支
    if not to_place:
        return 0
    if map_handle.get_map_system_path_str_for_list(character_data.position) !=             map_handle.get_map_system_path_str_for_list(to_place):
        return constant.StateMachine.EDUCATION_MOVE_TO_COURSE_PLACE
    return constant.StateMachine.EDUCATION_DO_COURSE


# ---------------------------------------------------------------------------
# 幼女跟随母亲见学（Plan 22 二期 §3.24）
# ---------------------------------------------------------------------------

FOLLOW_MOTHER_ENTERTAINMENT_ID = 176
""" 娱乐配置「跟随母亲」的cid。日程模板把某个时段排成它时，该时段也走见学分支 """


def judge_mother_available(character_id: int) -> int:
    """
    判断幼女此刻能不能去跟着母亲见学，返回有效的母亲id

    ⚠️ 回落链的每一条都必须有出路（方案 §3.24 的表），否则幼女会卡在 SHARE_BLANKLY。
    其中母亲在 H / 监禁 / 无意识时的排除是**硬要求不是优化**：既有的跟随链完全不判这几个状态，
    不显式挡住就会出现幼女跟进 H 场景。
    Keyword arguments:
    character_id -- 幼女的角色id
    Return arguments:
    int -- 有效的母亲角色id，无效则为-1
    """
    character_data: game_type.Character = cache.character_data[character_id]
    mother_id = character_data.relationship.mother_id
    # 没有母亲，或母亲已不在角色表里（旧档 / 数据损坏）
    if mother_id == -1 or mother_id not in cache.character_data:
        return -1
    mother_data: game_type.Character = cache.character_data[mother_id]
    if mother_data.dead:
        return -1
    # ⚠️ 绝不能让幼女跟进 H 场景：H中 / 无意识H中 / 被监禁
    if mother_data.sp_flag.is_h or mother_data.sp_flag.unconscious_h or mother_data.sp_flag.imprisonment:
        return -1
    # 母亲人不在罗德岛（外勤 / 外交访问）
    if mother_data.sp_flag.field_commission or mother_data.sp_flag.in_diplomatic_visit:
        return -1
    # 母亲住院中
    if mother_id in getattr(cache.rhodes_island, "medical_hospitalized", {}):
        return -1
    # 母亲所在场景不可达（未解锁 / 已拆除）
    mother_scene_str = map_handle.get_map_system_path_str_for_list(mother_data.position)
    if mother_scene_str not in cache.scene_data:
        return -1
    return mother_id


def judge_should_follow_mother(character_id: int) -> bool:
    """
    判断本时刻是否应当走见学分支

    两种入口：
        1. 幼女期的默认行为 —— 在节次内、且本节没排课（方案 §3.24 的触发条件）
        2. 日程模板把当前娱乐时段排成了「跟随母亲」—— 晚上或没课的时段也能跟
    ⚠️ 只对幼女（素质102）成立：萝莉期的自由时段是自由行动（口径 10）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否应当见学
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if not character_data.talent.get(102, 0):
        return False
    # 入口1：在节次内且本节没课。get_now_course 已经把"不在节次内"和"没排课"都归为None，
    # 所以这里要自己再判一次是不是真的在节次内
    if game_time.get_class_period(character_id) != -1:
        return schedule_handle.get_now_course(character_id) is None
    # 入口2：当前娱乐时段的日程活动就是「跟随母亲」
    enter_time = game_time.judge_entertainment_time(character_id)
    if not enter_time:
        return False
    slot = enter_time - 1
    return character_data.entertainment.entertainment_type[slot] == FOLLOW_MOTHER_ENTERTAINMENT_ID


def judge_follow_mother_state_machine(character_id: int) -> int:
    """
    见学分支的决策入口，返回本时刻该执行的状态机id

    母亲无效时一律回落到育儿室自由玩耍——这是回落链的唯一出口，
    不返回0交回既有AI链：交回去等于让幼女在没课的时段随机游荡，方案要的是确定的去处。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 状态机id，0表示本函数不接管
    """
    if not judge_should_follow_mother(character_id):
        return 0
    mother_id = judge_mother_available(character_id)
    if mother_id == -1:
        return constant.StateMachine.ENTERTAIN_FREE_PLAY
    character_data: game_type.Character = cache.character_data[character_id]
    mother_data: game_type.Character = cache.character_data[mother_id]
    # 还没到母亲身边，先移动过去
    if character_data.position != mother_data.position:
        return constant.StateMachine.EDUCATION_MOVE_TO_MOTHER
    return constant.StateMachine.EDUCATION_FOLLOW_MOTHER
