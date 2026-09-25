"""上课时段的行为决策（Plan 22 一期 §2.8）

每到一个上课节次，孩子（或选了课的干员）要先过两道闸，再决定这一节实际去做什么：

    1. 体力闸（方案 §3.14）：体力低于30%就上不动课了，转为休息并累计一节缺课。
       这是**被动**缺课，不置翘课flag、不触发「翘课被抓」事件。
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
from Script.System.Education_System import education_constant, schedule_handle, growth_handle, schedule_template_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


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
    for state_id in education_constant.NEGATIVE_STATE_ID_LIST:
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
    for max_sum, rate in education_constant.SKIP_CLASS_RATE_TABLE:
        if level_sum < max_sum:
            return rate
    return education_constant.SKIP_CLASS_RATE_MAX


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
    记一节缺课。同一节课只记一次——休息行为30分钟、一节课45分钟，
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


def judge_must_attend_sex_class(character_id: int, now_course: Optional[dict] = None) -> bool:
    """
    判断本节课是不是玩家点名要这名学生必修的性技实操课

    必修名单存在临时课程条目里，由玩家排课时手动指定；被点名的学生无论原本排了什么课都来，
    且不会因为心情差而翘课。
    Keyword arguments:
    character_id -- 角色id
    now_course -- 本节课数据，None时不查（仅按当前时刻的临时课判定）
    Return arguments:
    bool -- 是否为必修
    """
    from Script.System.Education_System import sex_class_handle

    period = game_time.get_class_period(character_id)
    if period == -1:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    temp_class = sex_class_handle.get_temp_class(now_time.date().toordinal(), period)
    if temp_class is None:
        return False
    return character_id in temp_class.get("must_attend", [])


def judge_pre_arrive_sex_class(character_id: int) -> int:
    """
    预到岗判定：下一节是自己要上的性技实操课时，提前若干分钟就动身去教室

    既有节次表首尾相接、没有课间（game_time.py:519 CLASS_PERIOD_START），9个节次里有7个的
       "提前10分钟"落在上一节课的最后10分钟内。命中时学生会**中止当前节次的课**转为移动
       （口径62 提前退场）——这是有意为之，玩家踩着点到教室时人应该已经在了。
    提前退场的那一节**不算缺课**：这里绝不能调 settle_absent()。那个函数用 last_absent_period
       对「日期序数+节次」做去重，被提前退场占掉标记后，当天真正的缺课就再也记不上了（口径66）。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 状态机id，不该预到岗则为0
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    temp_class, classroom = get_next_sex_class(character_id, now_time)
    if temp_class is None:
        return 0
    # 人已经在目标教室了就不用走了
    if judge_in_scene(character_id, classroom):
        return 0
    return constant.StateMachine.MOVE_TO_CLASS_ROOM


def get_next_sex_class(character_id: int, now_time) -> tuple:
    """
    取该角色下一节要上的性技实操课（仅在距开始 PRE_ARRIVE_MINUTE 分钟内时返回）

    "要上"有两种：被玩家点名必修，或个人课表里这一节本来就选了这间教室（选修）。
    后者是零改动的那一半——学生的个人课表存的是"这一节去哪间教室"而不是"上什么科目"，
    教室里的内容从料理实践换成性技实操，她照旧走进来。
    Keyword arguments:
    character_id -- 角色id
    now_time -- 参照时刻
    Return arguments:
    tuple -- (临时课程dict, 教室名str)，不该去则为(None, "")
    """
    import datetime

    from Script.System.Education_System import sex_class_handle

    date_ordinal = now_time.date().toordinal()
    week_day = now_time.weekday()
    for period, (hour, minute) in enumerate(game_time.CLASS_PERIOD_START):
        start_time = now_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # 只看还没开始的节次
        if start_time <= now_time:
            continue
        if start_time - now_time > datetime.timedelta(minutes=education_constant.PRE_ARRIVE_MINUTE):
            break
        temp_class = sex_class_handle.get_temp_class(date_ordinal, period)
        if temp_class is None:
            continue
        classroom = temp_class.get("classroom", "")
        # 必修：玩家点了名
        if character_id in temp_class.get("must_attend", []):
            return temp_class, classroom
        # 选修：个人课表这一节本来就指向这间教室
        selected = schedule_handle.get_selected_course(character_id, week_day, period)
        if selected is not None and selected[0] in education_constant.CLASSROOM_COURSE_TYPE_SET and selected[1] == classroom:
            return temp_class, classroom
    return None, ""


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
    # 上课接管即离开见学状态。这里不能省：本函数排在见学判定之前，
    #    幼女从见学转去上课时走不到 judge_follow_mother_state_machine，标记会一直挂着
    clear_follow_mother_flag(character_id)

    # 本节是不是玩家指定的必修性技实操课——两道闸对必修生的处理都不一样（Plan 22 四期 口径65）
    must_attend_flag = judge_must_attend_sex_class(character_id, now_course)

    # 第一道闸：体力。上不动课就去休息，并记一节缺课
    if character_data.hit_point_max and character_data.hit_point / character_data.hit_point_max < education_constant.ABSENT_HP_RATE:
        # 必修的实操课例外：人照常到场、不计缺课，只是到了教室也不进H模板，站在一边旁观（口径65）。
        # 体力不足是"做不动"而不是"不想来"，缺席的板子不该打在被玩家点名的学生头上
        if not must_attend_flag:
            settle_absent(character_id)
            return constant.StateMachine.REST

    # 第二道闸：心情。今日已经翘了就翘到底，否则按四个负面状态的等级和掷一次
    # 必修的实操课整道闸都跳过——玩家点了名就不许翘（口径60）
    growth_data = growth_handle.get_child_growth(character_id)
    if not must_attend_flag:
        if growth_data.skip_class_flag:
            return constant.StateMachine.EDUCATION_SKIP_CLASS
        skip_rate = get_skip_class_rate(character_id)
        if skip_rate and random.random() < skip_rate:
            return constant.StateMachine.EDUCATION_SKIP_CLASS

    # 派课：班级式的教室课
    if now_course["course_type"] in education_constant.CLASSROOM_COURSE_TYPE_SET:
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


def judge_mother_available(character_id: int) -> int:
    """
    判断幼女此刻能不能去跟着母亲见学，返回有效的母亲id

    回落链的每一条都必须有出路（方案 §3.24 的表），否则幼女会卡在 SHARE_BLANKLY。
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
    # 绝不能让幼女跟进 H 场景：H中 / 无意识H中 / 被监禁
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
        1. 幼女期的默认行为 —— 在节次内、本节没排课，**且该时段没有明确排别的日程活动**
           （方案 §3.24 的触发条件；2026-09-10 二期方案 §9.2.9 收窄：日程明确排了具体活动就去做那个活动，
           排「自由选择」、或活动没写进槽位（need 不过、退回自由选择）时才默认见学）
        2. 日程模板把当前娱乐时段排成了「跟随母亲」—— 晚上或没课的时段也能跟；
           **萝莉只有这一个入口**（2026-09-09 二期方案 §9.2.3 放宽：口径 10 的「萝莉自由时段自由行动」
           仍是默认，玩家明确在日程里排了「跟随母亲」时才去见学）
    有课永远优先：在节次内且本节排了课时，两种入口都不成立
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否应当见学
    """
    character_data: game_type.Character = cache.character_data[character_id]
    stage = growth_handle.get_character_stage(character_id)
    if stage not in (102, 103):
        return False
    # get_now_course 已经把"不在节次内"和"没排课"都归为None，所以这里要自己再判一次是不是真的在节次内
    in_period = game_time.get_class_period(character_id) != -1
    if in_period and schedule_handle.get_now_course(character_id) is not None:
        return False
    # 当前娱乐时段的槽位值；不在任何娱乐时段（如 8:40~9:00 的到岗时间、17:45~18:00）时为 -1
    enter_time = game_time.judge_entertainment_time(character_id)
    slot = enter_time - 1 if enter_time else -1
    slot_value = character_data.entertainment.entertainment_type[slot] if slot >= 0 else -1
    # 入口2：当前娱乐时段的日程活动就是「跟随母亲」（幼女 / 萝莉共用）
    if slot_value == education_constant.ENTERTAINMENT_FOLLOW_MOTHER:
        return True
    # 入口1：幼女在节次内且本节没课。该时段明确排了别的活动、且已经写进槽位时不见学，交给娱乐链去做那个活动；
    #        「自由选择」（模板值 0）或活动没写进槽位（need 不过）时才是默认见学
    if stage == 102 and in_period:
        explicit_id = schedule_template_handle.get_child_slot_activity(character_id, slot) if slot >= 0 else 0
        if explicit_id and slot_value == explicit_id:
            return False
        return True
    return False


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
        # 本时刻不该见学了（上了年纪、排上课、日程换成别的），顺手把标记清掉
        clear_follow_mother_flag(character_id)
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


def judge_in_follow_mother(character_id: int) -> bool:
    """
    校验一个角色此刻是否处于跟随母亲见学的状态（Plan 22 二期）

    这是 child_growth.follow_mother_flag 的统一读口，前提系统与角色状态标识都走它。
    不要在外部直接读那个字段：全岛绝大多数干员的 child_growth 是 None，直接读会 AttributeError
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否正在见学
    """
    if character_id not in cache.character_data:
        return False
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None:
        return False
    return bool(getattr(growth_data, "follow_mother_flag", False))


def clear_follow_mother_flag(character_id: int) -> None:
    """
    清掉见学标记（Plan 22 二期）

    置位只有见学状态机一处，清位却有四处——自由玩耍、见学结算、上课接管、见学判定不成立。
       少一处，「见学中」这个状态标识就会粘在孩子身上摘不掉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id not in cache.character_data:
        return
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None:
        return
    growth_data.follow_mother_flag = False
