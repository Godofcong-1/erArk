"""上课状态判定——供工作链的教师 / 学生前提读取（Plan 22 一期 §2.8，Plan 24 并入工作链）

教师与学生的「上班」都是 target.csv 工作链里的目标行（type 21/22 的组 07 教师、组 08 学生），
本模块不直接派发状态机，只把课表换算成互斥的状态，由 handle_premise_work 里的薄前提读取：

    get_teacher_duty  —— 教师此刻的课表职责：本节有课 / 20 分钟内有下一节 / 都没有
    get_course_stage  —— 学生此刻的上课状态：待赴实操课 / 体力缺课 / 翘课 / 照常上课 / 加入正在进行的实操课 / 马上开课 / 与课表无关

另有行为循环打断点用的 get_student_leave_time（Plan 25）：把学生当前的工作 / 娱乐行为截到应离开的时刻
（待赴实操课开课前 10 分钟提前退场、没课的节次在下一节开课前 20 分钟收手）；以及拉学生进听课的
judge_student_pullable（玩家授课与教师 303 共用）/ judge_student_join_class（303 另加课表与两道闸）。

同一个前提在一次决策里按名缓存、被多行共享，所以这里的判定都必须是纯函数：不写数据、不惰性创建养成数据，
翘课的掷骰以「角色 + 日期 + 节次」定种子（roll_skip_class），同一节无论判定多少次结果都相同。

学生每节课要先过两道闸，再决定这一节实际去做什么：

    1. 体力闸（方案 §3.14）：体力低于30%就上不动课了，转为休息并累计一节缺课（记缺课在 721 状态机里做）。
       这是**被动**缺课，不置翘课flag、不触发「翘课被抓」事件。
    2. 心情闸（方案 §3.19）：苦痛(17)+恐怖(18)+抑郁(19)+反感(20)四个负面状态的**等级**和
       越高，越可能主动翘课。判定写法照 `Script/Design/instuct_judege.py:103~104` 的实行值修正。

两道闸的顺序不能反：体力不足是"去不了"，心情糟糕是"不想去"，一个孩子累到爬不起来时
不该再被算一次"叛逆"。

过闸之后按课型分行。班级式的教室课走 移动→听课，本节没有可用教师时降级为自习。
个人式的体育/兴趣/实习课则是"人到地点，执行该地点既有的行为"：体育课去木桩房打木桩、
兴趣课去棋牌室下棋、实习课去厨房跟着厨师。
"""
import random
from typing import List, Tuple
from Script.Config import game_config
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
    功能: 只查表不掷骰；本节到底翘不翘由 roll_skip_class 每节掷一次（Plan 24 §3.5）
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
    功能: 判不过就让学生降级自习；判过了学生就坐下来等教师讲课。
          所以凡是「教师这节确定来不了」的情况都必须在这里挡掉，漏一种学生就空等一整节、零收益（2026-09-12 第五轮补全）。
          凡是教师目标行（target.csv 组 07）的 normal 前提会挡掉、且一节之内不会自行解除的状态，都要在这里同步（Plan 24 §3.4）
    """
    from Script.Design import handle_premise

    if teacher_id == -1 or teacher_id not in cache.character_data:
        return False
    teacher_data: game_type.Character = cache.character_data[teacher_id]
    if teacher_data.dead:
        return False
    # 这几种状态下教师人不在教室，或不可能讲课
    if teacher_data.sp_flag.is_h or teacher_data.sp_flag.imprisonment:
        return False
    # 玩家（临时实操课的授课者）只看上面两条：他来不来由玩家自己决定
    if teacher_id == 0:
        return True
    # 教师的授课行挂着 normal 前提：临盆 / 产后 / 监禁（normal_2）、助理 / 跟随 / 体检中（normal_3）时她不会去授课。
    #    不挂 normal_1（需求）、normal_4（服装）：上个厕所、吃个饭回来照样开讲，学生不该因此整节自习
    if not handle_premise.handle_normal_2(teacher_id) or not handle_premise.handle_normal_3(teacher_id):
        return False
    # 授课行挂的是 normal_all_except_special_hypnosis：意识模糊 / 不清（醉酒、烂醉、半梦半醒等）时她不会来讲课，
    #    空气 / 体控催眠除外——那两种催眠下授课行照样成立（Plan 25 §3.3）
    if (not handle_premise.handle_normal_5(teacher_id) or not handle_premise.handle_normal_6(teacher_id)) and not (
        handle_premise.handle_unconscious_flag_5(teacher_id) or handle_premise.handle_unconscious_flag_6(teacher_id)
    ):
        return False
    if teacher_data.sp_flag.field_commission or teacher_data.sp_flag.in_diplomatic_visit:
        return False
    # 已经不在岛上 / 换了岗：课表里还挂着她，但她的 AI 不会再来上课
    if teacher_id not in cache.npc_id_got or teacher_data.work.work_type != education_constant.TEACHER_WORK_TYPE:
        return False
    # 睡着的、住院的、离线的都来不了
    if teacher_data.sp_flag.sleep:
        return False
    if teacher_id in getattr(cache.rhodes_island, "medical_hospitalized", {}):
        return False
    if not handle_premise.handle_normal_7(teacher_id):
        return False
    return True


def get_teacher_duty(character_id: int) -> Tuple[int, str]:
    """
    教师此刻的课表职责（Plan 24，供工作链的教师前提读取）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Tuple[int, str] -- (TEACHER_DUTY_* 状态, 该职责对应的教室场景名；无职责时为空字符串)
    功能: 本节有课（任何星期都算，周日是玩家特意排的）优先；本节没课再看 20 分钟内开始的下一节（到岗时间 / 课间）。
          课表查的是全局课表反查，含当天临时实操课的覆盖层：被临时课顶掉的那一格查不到，教师就回办公室待命
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == 0 or character_data.work.work_type != education_constant.TEACHER_WORK_TYPE:
        return education_constant.TEACHER_DUTY_NONE, ""
    teaching = schedule_handle.get_now_teaching(character_id)
    if teaching is not None:
        return education_constant.TEACHER_DUTY_NOW, teaching["classroom"]
    upcoming = schedule_handle.get_upcoming_teaching(character_id)
    if upcoming is not None:
        return education_constant.TEACHER_DUTY_UPCOMING, upcoming["classroom"]
    return education_constant.TEACHER_DUTY_NONE, ""


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


def judge_must_attend_sex_class(character_id: int, now_time=None) -> bool:
    """
    判断本节课是不是玩家点名要这名学生必修的性技实操课

    必修名单存在临时课程条目里，由玩家排课时手动指定；被点名的学生无论原本排了什么课都来
    （schedule_handle.get_now_course 会把她这节的课改指临时课的教室），且不会因为心情差而翘课。
    Keyword arguments:
    character_id -- 角色id
    now_time -- 参照时刻，None 时取角色的行为开始时刻（教师拉人时传教师的开讲时刻，Plan 25 §3.5）
    Return arguments:
    bool -- 是否为必修
    """
    from Script.System.Education_System import sex_class_handle

    if now_time is None:
        character_data: game_type.Character = cache.character_data[character_id]
        now_time = character_data.behavior.start_time
        if now_time is None:
            now_time = cache.game_time
    period = game_time.get_class_period_by_time(now_time)
    if period == -1:
        return False
    temp_class = sex_class_handle.get_active_temp_class(now_time.date().toordinal(), period)
    if temp_class is None:
        return False
    return character_id in temp_class.get("must_attend", [])


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
        temp_class = sex_class_handle.get_active_temp_class(date_ordinal, period)
        if judge_sex_class_is_mine(character_id, temp_class, week_day, period):
            return temp_class, temp_class.get("classroom", "")
    return None, ""


def judge_sex_class_is_mine(character_id: int, temp_class, week_day: int, period: int) -> bool:
    """
    判断某节临时实操课是不是这名角色要上的（必修被点名，或选修：个人课表这一节本来就指向这间教室）
    Keyword arguments:
    character_id -- 角色id
    temp_class -- 临时课程dict，None 表示这一节没有临时课
    week_day -- 星期0~6
    period -- 节次0~8
    Return arguments:
    bool -- 是否要上
    功能: get_next_sex_class 与学生的截短规则（get_student_leave_time）共用
    """
    if temp_class is None:
        return False
    classroom = temp_class.get("classroom", "")
    # 必修：玩家点了名
    if character_id in temp_class.get("must_attend", []):
        return True
    # 选修：个人课表这一节本来就指向这间教室
    selected = schedule_handle.get_selected_course(character_id, week_day, period)
    return selected is not None and selected[0] in education_constant.CLASSROOM_COURSE_TYPE_SET and selected[1] == classroom


def get_pending_sex_classroom(character_id: int) -> str:
    """
    学生此刻待赴的性技实操课教室（Plan 24，供预到岗的两个前提判断人在不在那间教室）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 教室场景名，不是学生岗或没有待赴的实操课时为空字符串
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return ""
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    return get_next_sex_class(character_id, now_time)[1]


def get_course_stage(character_id: int) -> int:
    """
    学生此刻的上课状态（Plan 24）：把原先 预到岗 → 到岗时间 → 体力闸 → 心情闸 → 派课 的闸门顺序直译为互斥状态，
    工作链的学生前提都从这里取值，保证 target.csv 组 08 的学生行两两互斥
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- COURSE_STAGE_* 之一
    功能: 待赴实操课（SEX_PENDING）优先于本节的一切：既有节次表首尾相接、没有课间（game_time.py:519 CLASS_PERIOD_START），
             9个节次里有7个的"提前10分钟"落在上一节课的最后10分钟内，命中时学生会**中止当前节次的课**转为移动
             （口径62 提前退场）——这是有意为之，玩家踩着点到教室时人应该已经在了。
          提前退场的那一节**不算缺课**：绝不能在这条路上调 settle_absent()。那个函数用 last_absent_period
             对「日期序数+节次」做去重，被提前退场占掉标记后，当天真正的缺课就再也记不上了（口径66）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return education_constant.COURSE_STAGE_NONE
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    # 预到岗优先于本节的一切（原 find_character_target 里排在上课判定之前）
    pending_class, pending_classroom = get_next_sex_class(character_id, now_time)
    if pending_class is not None:
        # 玩家提前几分钟就在那间教室开讲了（Plan 26 §3.5）：人已经到了、能参加的，不再原地等到开课那一刻才入课
        if judge_pending_class_joinable(character_id, pending_class, pending_classroom):
            return education_constant.COURSE_STAGE_JOIN_SEX_CLASS
        return education_constant.COURSE_STAGE_SEX_PENDING
    now_course = schedule_handle.get_now_course(character_id)
    if now_course is None:
        # 不在节次内、或本节没排课：只有到岗时间（开课前 20 分钟内）要先去第一节课的地方（第五轮）
        if schedule_handle.get_upcoming_course(character_id) is not None:
            return education_constant.COURSE_STAGE_UPCOMING
        return education_constant.COURSE_STAGE_NONE
    # 必修实操课两道闸都跳过（口径 60 / 65）：体力不足也照常到场、不记缺课，只是到了教室不进H模板、在一边旁观；
    #    玩家点了名就不许翘
    if judge_must_attend_sex_class(character_id):
        return get_attend_or_join_stage(character_id, now_course)
    # 第一道闸：体力
    if character_data.hit_point_max and character_data.hit_point / character_data.hit_point_max < education_constant.ABSENT_HP_RATE:
        return education_constant.COURSE_STAGE_ABSENT_HP
    # 第二道闸：心情。今日已经翘了就翘到底，否则本节掷一次。
    #    前提求值不能写数据，所以直接读 child_growth，不走会惰性创建养成数据的 get_child_growth
    growth_data = character_data.child_growth
    if (growth_data is not None and growth_data.skip_class_flag) or roll_skip_class(character_id):
        return education_constant.COURSE_STAGE_SKIP
    return get_attend_or_join_stage(character_id, now_course)


def get_attend_or_join_stage(character_id: int, now_course: dict) -> int:
    """
    过了两道闸之后，判断是照常上课还是直接加入正在进行的实操课（Plan 25 §3.2）
    Keyword arguments:
    character_id -- 角色id
    now_course -- schedule_handle.get_now_course() 的返回值
    Return arguments:
    int -- COURSE_STAGE_JOIN_SEX_CLASS 或 COURSE_STAGE_ATTEND
    功能: 实操课开课后才走进教室的学生，原先会因为玩家在 H 中被判「教师不可用」而坐在一边自习。
          本节的课所在的教室正在上实操课、人已经在这间教室、还没进 H、能参加（必修生豁免前置修习）时，就是 JOIN。
          不在教室时仍是 ATTEND：先走 715 过去，到了再判一次。
          开课模式没开时直接短路，judge_can_join_sex_class 对成年学生要算实行值，不能每次决策都算
    """
    from Script.System.Education_System import sex_class_handle

    if not cache.sex_class_mode:
        return education_constant.COURSE_STAGE_ATTEND
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_h:
        return education_constant.COURSE_STAGE_ATTEND
    running_class = sex_class_handle.get_running_class()
    if running_class is None:
        return education_constant.COURSE_STAGE_ATTEND
    classroom = running_class.get("classroom", "")
    if not classroom or now_course.get("classroom", "") != classroom or not judge_in_scene(character_id, classroom):
        return education_constant.COURSE_STAGE_ATTEND
    must_attend = character_id in running_class.get("must_attend", [])
    if not sex_class_handle.judge_can_join_sex_class(character_id, check_course=not must_attend):
        return education_constant.COURSE_STAGE_ATTEND
    return education_constant.COURSE_STAGE_JOIN_SEX_CLASS


def judge_pending_class_joinable(character_id: int, pending_class: dict, pending_classroom: str) -> bool:
    """
    判断待赴的那节实操课是否已被玩家提前开讲、且这名学生已在那间教室可以直接加入（Plan 26 §3.5）
    Keyword arguments:
    character_id -- 角色id
    pending_class -- get_next_sex_class() 取到的临时课程
    pending_classroom -- 那节课的教室场景名
    Return arguments:
    bool -- 是否直接加入
    功能: 学生开课前 10 分钟到场后在原地等（720）；玩家若提前几分钟开讲，那节课此刻已是 running，
          还按 SEX_PENDING 等到开课那一刻才判 JOIN 的话，她会在课堂 H 旁边干站着。
          与 get_attend_or_join_stage 同口径：模式已开、人在那间教室、还没进 H、能参加（必修生豁免前置修习）
    """
    from Script.System.Education_System import sex_class_handle

    if not cache.sex_class_mode or not pending_class.get("running", False):
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_h or not judge_in_scene(character_id, pending_classroom):
        return False
    must_attend = character_id in pending_class.get("must_attend", [])
    return sex_class_handle.judge_can_join_sex_class(character_id, check_course=not must_attend)


def get_course_place_now_or_upcoming(character_id: int) -> List[str]:
    """
    取本节课（不在节次内时为马上开始的那一节）的上课地点，与 715 移动状态机的取法一致
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    List[str] -- 场景路径，没课或解析不出为空列表
    功能: 个人式课这一节上不成（场所未开放、兴趣课的活动条件不符）的，取数口 get_course_at 起就视为没课（Plan 28 §3.2），
             这里不再重复判定（Plan 26 §3.8 当初把 need 判定加在这里）。
          仍可能解析不出的只有班级式课（教室已不存在等），此时在 / 不在上课地点两个前提都不成立，
             没有行命中，交回既有 AI，不留死分支（Plan 24 §3.7）
    """
    course = schedule_handle.get_now_course(character_id)
    if course is None:
        course = schedule_handle.get_upcoming_course(character_id)
    if course is None:
        return []
    return schedule_handle.get_course_place(course)


def roll_skip_class(character_id: int, now_time=None) -> bool:
    """
    本节是否掷中翘课：以「角色 + 日期 + 节次」定种子，同一节无论判定多少次结果都相同（Plan 24 §3.5）
    Keyword arguments:
    character_id -- 角色id
    now_time -- 参照时刻，None 时取角色的行为开始时刻（教师拉人时传教师的开讲时刻，Plan 25 §3.5）
    Return arguments:
    bool -- 是否掷中
    功能: 前提在一次决策里被「翘课」「照常上课」多行读取，每次调用都重掷的话两行可能同时不成立（上课时间去闲逛）
          或同时成立（随机二选一）；定了种子也让每节的翘课概率严格等于表值。
          教师替学生判时种子相同，所以两边判出来的结果一定一致
    """
    rate = get_skip_class_rate(character_id)
    if rate <= 0:
        return False
    if now_time is None:
        character_data: game_type.Character = cache.character_data[character_id]
        now_time = character_data.behavior.start_time
        if now_time is None:
            now_time = cache.game_time
    period = game_time.get_class_period_by_time(now_time)
    return random.Random(f"{character_id}|{now_time.toordinal()}|{period}").random() < rate


# ---------------------------------------------------------------------------
# 拉学生进课堂与赶去上课（Plan 25）
# ---------------------------------------------------------------------------


def judge_student_pullable(student_id: int) -> bool:
    """
    判断一名角色能不能被授课者直接拉成听课状态（教师 303 与玩家「授课」指令共用的底层判据）
    Keyword arguments:
    student_id -- 角色id
    Return arguments:
    bool -- 是否可拉
    功能: 学生岗（口径 1）、活着、不在 H、不在睡觉、没挂今日翘课 flag、此刻不在休息（体力缺课走的就是休息）。
          睡觉看两样（Plan 27 §3.7，写法同 judge_mother_followable）：要睡觉标记，或行为就是睡觉——
             当场爆睡（疲劳满、安眠药、烂醉 → 状态机 44）只改行为、不置标记，只判标记会把她拉起来听课
    """
    if student_id not in cache.character_data:
        return False
    character_data: game_type.Character = cache.character_data[student_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE or character_data.dead:
        return False
    if character_data.sp_flag.is_h or character_data.sp_flag.sleep or character_data.behavior.behavior_id == constant.Behavior.SLEEP:
        return False
    if character_data.child_growth is not None and character_data.child_growth.skip_class_flag:
        return False
    return character_data.behavior.behavior_id != constant.Behavior.REST


def judge_student_join_class(student_id: int, classroom: str, now_time) -> bool:
    """
    判断 NPC 教师开讲时该不该把这名学生拉进听课（Plan 25 §3.5）
    Keyword arguments:
    student_id -- 角色id
    classroom -- 教师所在的教室场景名
    now_time -- 教师的开讲时刻
    Return arguments:
    bool -- 是否拉进来
    功能: 与学生自己决策时的 get_course_stage 同口径：这一节的课表（含必修覆盖）指向这间教室，必修生直接成立，
          否则过体力闸与心情闸。开课前已在教室里等候的学生，本节该体力缺课或掷中翘课的，不能因为教师先被处理就被拉进来
    """
    if not judge_student_pullable(student_id):
        return False
    period = game_time.get_class_period_by_time(now_time)
    if period == -1:
        return False
    course = schedule_handle.get_course_at(student_id, now_time, period)
    if course is None or course["classroom"] != classroom:
        return False
    if judge_must_attend_sex_class(student_id, now_time):
        return True
    character_data: game_type.Character = cache.character_data[student_id]
    if character_data.hit_point_max and character_data.hit_point / character_data.hit_point_max < education_constant.ABSENT_HP_RATE:
        return False
    return not roll_skip_class(student_id, now_time)


def get_student_leave_time(character_id: int):
    """
    取学生当前行为应当提前结束的时刻（handle_npc_ai.judge_interrupt_character_behavior 调用，Plan 25 §3.1）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    datetime.datetime or None -- 应当结束的时刻，严格落在当前行为的开始与结束之间；不需要提前结束时为 None
    功能: NPC 只在发呆时做决策，听课截到节末、娱乐 10~120 分钟，都不会自己停下来，所以要从外面把行为截短：
            A 待赴实操课：之后开始的某一节是自己要上的实操课（必修或选修）、人不在那间教室
               → 截到开课前 PRE_ARRIVE_MINUTE（口径 62 提前退场，上课中也截）
            B 马上开课：之后开始的某一节有课（已停课、上不成的个人式课都算没课，Plan 27 / 28）、开课前 UPCOMING_MINUTE 那一刻本节没课、人不在上课地点、今天没翘课
               → 截到开课前 UPCOMING_MINUTE（与教师「20 分钟内有下一节先去教室」同口径）
          截短时长而不是「现在就结束」：行为循环里 NPC 按各自的行为时刻推进，cache.game_time 是玩家这一步的结束时刻，
             玩家一步走 45 分钟时，「现在」早已越过开课时刻，拿它判会整个错过；截到应离开的那一刻，NPC 就在那一刻重新决策。
          只截工作 / 娱乐类行为（行为 tag 含「工作」或「娱乐」），需求类（吃饭、如厕、休息、淋浴）不动；
          上课行的门槛 normal_all 不成立时不截——截了 AI 也派不出上课行。
          截出来的结束时刻严格晚于开始时刻（NPC 至少走一分钟），重新决策出的新行为开始于离开时刻，不会被再截一次，行为循环必然收敛。
          截短不回退收益：NPC 的结算发生在行为开始时，被截短的那节课已按整节结算过，也不记缺课（口径 66）
    """
    import datetime

    from Script.Design import handle_premise
    from Script.System.Education_System import sex_class_handle

    if character_id == 0 or character_id not in cache.character_data:
        return None
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return None
    if character_data.sp_flag.is_h or character_data.sp_flag.sleep:
        return None
    behavior_id = character_data.behavior.behavior_id
    if behavior_id not in game_config.config_behavior:
        return None
    behavior_tag = game_config.config_behavior[behavior_id].tag
    if "工作" not in behavior_tag and "娱乐" not in behavior_tag:
        return None
    start_time = character_data.behavior.start_time
    if start_time is None or character_data.behavior.duration <= 0:
        return None
    if not handle_premise.handle_normal_all(character_id):
        return None
    end_time = start_time + datetime.timedelta(minutes=character_data.behavior.duration)
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    # 今天已经翘了课的不赶（B），免得去教室门口等一趟再掉头走；实操课（A）与 get_course_stage 的 SEX_PENDING 同口径，不看翘课
    skip_flag = character_data.child_growth is not None and character_data.child_growth.skip_class_flag
    pre_arrive = datetime.timedelta(minutes=education_constant.PRE_ARRIVE_MINUTE)
    upcoming = datetime.timedelta(minutes=education_constant.UPCOMING_MINUTE)
    date_ordinal = start_time.date().toordinal()
    week_day = start_time.weekday()
    for period, (hour, minute) in enumerate(game_time.CLASS_PERIOD_START):
        class_start = start_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if class_start <= start_time:
            continue
        # 从这一节起离开的时刻都不早于行为结束，后面的节次更不用看
        if class_start - min(pre_arrive, upcoming) >= end_time:
            break
        leave_time = None
        to_place = []
        temp_class = sex_class_handle.get_active_temp_class(date_ordinal, period)
        if judge_sex_class_is_mine(character_id, temp_class, week_day, period):
            leave_time = class_start - pre_arrive
            to_place = schedule_handle.get_classroom_position(temp_class.get("classroom", ""))
        elif not skip_flag:
            course = schedule_handle.get_course_at(character_id, class_start, period)
            # 个人式课这一节上不成（兴趣课条件不符、场所未开放）的，get_course_at 起就视为没课、不截（Plan 28 §3.2）
            if course is not None:
                leave_time = class_start - upcoming
                leave_period = game_time.get_class_period_by_time(leave_time)
                # 离开的那一刻本节还有课：那节课由截到节末的时长自然结束，不必截
                if leave_period != -1 and schedule_handle.get_course_at(character_id, leave_time, leave_period) is not None:
                    leave_time = None
                else:
                    to_place = schedule_handle.get_course_place(course)
        if leave_time is None or not to_place:
            continue
        if now_scene_str == map_handle.get_map_system_path_str_for_list(to_place):
            continue
        # 行为开始时已经进了窗口（比如当时 AI 因为需求没派上课行）：至少别拖过开课
        if leave_time <= start_time:
            leave_time = class_start
        if start_time < leave_time < end_time:
            return leave_time
    return None


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


def judge_mother_followable(character_id: int) -> int:
    """
    判断幼女此刻能不能真的跟着母亲见学：judge_mother_available 之外，母亲还不能在睡觉（Plan 26 L7）
    Keyword arguments:
    character_id -- 幼女的角色id
    Return arguments:
    int -- 有效的母亲角色id，无效则为-1
    功能: 见学的决策、移动、跟随、结算四处都走这里。
          睡觉不写进 judge_mother_available：那个函数还是公务事件前提 self_mother_available 的判据，
             而每日的养成事件在跨天结算时派发，那时母亲多半睡着，写进去会让带母亲的事件几乎抽不到
    """
    mother_id = judge_mother_available(character_id)
    if mother_id == -1:
        return -1
    mother_data: game_type.Character = cache.character_data[mother_id]
    # 要睡觉状态或正睡着（吃药、爆睡未必挂那个标记）：跟到宿舍里看着一个睡着的人学不到手艺，回落育儿室自由玩耍
    if mother_data.sp_flag.sleep or mother_data.behavior.behavior_id == constant.Behavior.SLEEP:
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
    有课永远优先：学生此刻与课表有关（本节有课、马上开课、待赴实操课）时，两种入口都不成立
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否应当见学
    """
    character_data: game_type.Character = cache.character_data[character_id]
    stage = growth_handle.get_character_stage(character_id)
    if stage not in (102, 103):
        return False
    # 上课是工作链里学生岗的目标行（target.csv 组 08），而见学排在工作链之前，这里不让路就会把上课截走（Plan 24 §3.9）。
    #    看的是 get_course_stage 而不是个人课表：改了岗的女儿课表还在，但她不会去上课（口径 1），不该因此不见学
    if get_course_stage(character_id) != education_constant.COURSE_STAGE_NONE:
        return False
    # get_now_course 已经把"不在节次内"和"没排课"都归为None，所以这里要自己再判一次是不是真的在节次内
    in_period = game_time.get_class_period(character_id) != -1
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
        # 本时刻不该见学了（上了年纪、排上课、日程换成别的），顺手把标记清掉。
        #    见学判定排在工作链之前，孩子从见学转去上课时一定先经过这里（Plan 24 起上课接管处不再另清）
        clear_follow_mother_flag(character_id)
        return 0
    mother_id = judge_mother_followable(character_id)
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

    置位只有见学状态机一处，清位却有四处——自由玩耍、见学结算、见学判定不成立、跨天兜底。
       少一处，「见学中」这个状态标识就会粘在孩子身上摘不掉。
       原先的「上课接管」随 Plan 24 并入工作链后不再需要：见学判定排在工作链之前，不成立时自己会清
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
