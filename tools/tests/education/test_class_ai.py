# -*- coding: UTF-8 -*-
"""class_ai：翘课概率与定种子掷骰、教师可用性、上课状态函数、工作链里的师生目标行（Plan 24）、normal 门槛、外层闸、见学回落链"""
from _bootstrap import *  # noqa: F401,F403
from Script.Design import handle_npc_ai, clothing

open_all_classroom()
clear_schedules()
ROOM1 = _("理论教室一")
ROOM_P = _("实践教室一")
teacher = make_character(101, "教师甲", 151, position=classroom_path(ROOM1))
mother = make_character(102, "母亲", 21)
student = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102)
child = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102)
E = education_constant
SM = constant.StateMachine
CLASS_SM_SET = {SM.MOVE_TO_CLASS_ROOM, SM.MOVE_TO_TEACHER_OFFICE, SM.WORK_TEACH, SM.WORK_ATTENT_CLASS, SM.EDUCATION_SELF_STUDY, SM.EDUCATION_SKIP_CLASS,
                SM.EDUCATION_MOVE_TO_COURSE_PLACE, SM.EDUCATION_DO_COURSE, SM.EDUCATION_WAIT_NEXT_PERIOD, SM.EDUCATION_ABSENT_REST}
""" 师生目标行（target.csv 组 07 / 08）会派发的全部状态机：「没有上课行命中」的断言就是派发结果不落在这里面 """
_orig_roll = class_ai.roll_skip_class
_orig_rate = class_ai.get_skip_class_rate


def prepare_ai(cid: int) -> None:
    """
    把最小 fixture 补成能跑通完整 AI 链的样子：已起床、穿好衣服、异常位刷新
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    无
    功能: 没起床会先被「起床」目标（target 205）接管；全裸则 normal_all 不成立，工作 / 娱乐的目标行根本不跑
    """
    cd = cache.character_data[cid]
    cd.action_info.wake_time = cache.game_time
    clothing.get_npc_cloth(cid)
    handle_premise.refresh_unnormal_flag(cid)


def dispatch(cid: int, now_time: datetime.datetime = None) -> int:
    """
    跑一遍 find_character_target，记下它派发的状态机id
    Keyword arguments:
    cid -- 角色id
    now_time -- 派发时刻，缺省为 DEFAULT_TIME 那天第一节的开始
    Return arguments:
    int -- 派发的状态机id，没派发则为 0
    功能: 每次先把上一轮留下的移动 / 行为清掉，否则会被「继续移动」目标接管；
          起床时间拨到当前、全部 NPC 的异常位刷新——测试直接改状态位，不经过游戏里会同步异常位的结算点
    """
    cd = cache.character_data[cid]
    cd.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    cd.behavior.duration = 0
    cd.behavior.move_target = []
    cd.behavior.move_final_target = []
    cd.state = constant.CharacterStatus.STATUS_ARDER
    set_time(now_time if now_time is not None else period_time(0))
    cd.action_info.wake_time = cache.game_time
    for other_id in list(cache.npc_id_got):
        handle_premise.refresh_unnormal_flag(other_id)
    hit = []
    origin = dict(constant.handle_state_machine_data)
    for sid, func in origin.items():
        constant.handle_state_machine_data[sid] = (lambda s, f: (lambda c: (hit.append(s), f(c))[1]))(sid, func)
    try:
        handle_npc_ai.find_character_target(cid, cache.game_time)
    finally:
        constant.handle_state_machine_data.clear()
        constant.handle_state_machine_data.update(origin)
    return hit[0] if hit else 0


section("翘课概率表")
_orig_sum = class_ai.get_negative_status_level_sum
for level_sum, rate in ((0, 0.0), (3, 0.0), (4, 0.10), (7, 0.10), (8, 0.25), (12, 0.45), (15, 0.45), (16, 0.70), (32, 0.70)):
    class_ai.get_negative_status_level_sum = lambda cid, s=level_sum: s
    check(f"等级和 {level_sum} → 概率 {rate}", abs(class_ai.get_skip_class_rate(201) - rate) < 1e-9, class_ai.get_skip_class_rate(201))
class_ai.get_negative_status_level_sum = _orig_sum
check("等级和按状态等级累加", class_ai.get_negative_status_level_sum(201) == 0)

section("翘课每节只掷一次（Plan 24 §3.5）")
set_time(period_time(0))
class_ai.get_skip_class_rate = lambda cid: 0.5
_first = class_ai.roll_skip_class(201)
check("同一节连掷 20 次结果一致（前提在一次决策里被多行读取，读到的必须是同一个结果）", all(class_ai.roll_skip_class(201) == _first for _i in range(20)))
_hits = 0
for _day in range(20):
    for _period in range(9):
        set_time(period_time(_period, DEFAULT_TIME.date() + datetime.timedelta(days=_day)))
        _hits += class_ai.roll_skip_class(201)
check("概率 0.5 时 180 节里约一半掷中（每节一掷，与表值一致）", 60 <= _hits <= 120, _hits)
class_ai.get_skip_class_rate = lambda cid: 0.0
check("概率 0 恒不翘", not class_ai.roll_skip_class(201))
class_ai.get_skip_class_rate = lambda cid: 1.0
check("概率 1 恒翘", class_ai.roll_skip_class(201))
class_ai.get_skip_class_rate = _orig_rate
set_time(period_time(0))


def teacher_available() -> bool:
    """
    刷新教师的异常位后判一次可用性（测试直接改状态位，不经过游戏里会同步异常位的结算点）
    Return arguments:
    bool -- 教师101是否可授课
    """
    handle_premise.refresh_unnormal_flag(101)
    return class_ai.judge_teacher_available(101)


section("教师可用性")
check("-1 不可用", not class_ai.judge_teacher_available(-1))
check("不存在的角色不可用", not class_ai.judge_teacher_available(999))
check("正常教师可用", teacher_available())
teacher.sp_flag.is_h = True
check("H 中不可用", not teacher_available())
teacher.sp_flag.is_h = False
teacher.sp_flag.imprisonment = True
check("监禁中不可用", not teacher_available())
teacher.sp_flag.imprisonment = False
teacher.sp_flag.field_commission = True
check("外勤中不可用", not teacher_available())
teacher.sp_flag.field_commission = False
teacher.dead = True
check("死亡不可用", not teacher_available())
teacher.dead = False
# 第五轮补全：这些情况下教师这节确定来不了，学生必须降级自习而不是空等一整节
teacher.work.work_type = 21
check("换了岗不可用", not teacher_available())
teacher.work.work_type = 151
teacher.sp_flag.is_follow = 1
check("跟随玩家中不可用（normal_3）", not teacher_available())
teacher.sp_flag.is_follow = 0
teacher.sp_flag.sleep = True
check("睡着不可用", not teacher_available())
teacher.sp_flag.sleep = False
cache.rhodes_island.medical_hospitalized = {101: {}}
check("住院不可用", not teacher_available())
cache.rhodes_island.medical_hospitalized = {}
cache.npc_id_got.discard(101)
check("不在岛上（不在 npc_id_got）不可用", not teacher_available())
cache.npc_id_got.add(101)
# Plan 24 §3.4：教师目标行挂着 normal 前提，这些状态下她不会去授课，这里必须同步判为不可用
teacher.talent[22] = 1
check("临盆不可用（normal_2）", not teacher_available())
teacher.talent[22] = 0
teacher.talent[23] = 1
check("产后不可用（normal_2）", not teacher_available())
teacher.talent[23] = 0
pl.assistant_character_id = 101
check("当助理不可用（normal_3）", not teacher_available())
pl.assistant_character_id = 0
cache.rhodes_island.waiting_for_exam_operator_ids.add(101)
check("在体检链中不可用（normal_3）", not teacher_available())
cache.rhodes_island.waiting_for_exam_operator_ids.discard(101)
check("玩家（临时实操课的授课者）可用", class_ai.judge_teacher_available(0))
check("恢复后正常教师可用", teacher_available())

section("缺课去重")
set_time(period_time(0))
class_ai.settle_absent(201)
class_ai.settle_absent(201)
check("同一节只记一次", cache.character_data[201].child_growth.absent_count == 1)
set_time(period_time(1))
class_ai.settle_absent(201)
check("换节次再记一次", cache.character_data[201].child_growth.absent_count == 2)
cache.character_data[201].child_growth.absent_count = 0
cache.character_data[201].child_growth.last_absent_period = []

section("状态函数：教师职责（get_teacher_duty）")
clear_schedules()
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM_P, 0, 0, 43, 101)
check("本节有课 → NOW + 课表上那间教室", class_ai.get_teacher_duty(101) == (E.TEACHER_DUTY_NOW, ROOM_P), class_ai.get_teacher_duty(101))
schedule_handle.clear_class_cell(ROOM_P, 0, 0)
schedule_handle.set_class_cell(ROOM_P, 0, 1, 43, 101)
set_time(period_time(1) - datetime.timedelta(minutes=15))
check("本节没课、15 分钟后下一节有课 → UPCOMING + 下一节的教室", class_ai.get_teacher_duty(101) == (E.TEACHER_DUTY_UPCOMING, ROOM_P), class_ai.get_teacher_duty(101))
schedule_handle.clear_class_cell(ROOM_P, 0, 1)
check("本节与 20 分钟内都没课 → NONE", class_ai.get_teacher_duty(101) == (E.TEACHER_DUTY_NONE, ""))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 201)
set_time(period_time(0))
check("非教师岗恒为 NONE（即使课表上填了她）", class_ai.get_teacher_duty(201) == (E.TEACHER_DUTY_NONE, ""))
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 0, ROOM_P, 70, must_attend=[])
check("玩家恒为 NONE（临时实操课由玩家自己决定来不来）", class_ai.get_teacher_duty(0) == (E.TEACHER_DUTY_NONE, ""))
clear_schedules()
schedule_handle.set_class_cell(ROOM1, 6, 0, 45, 101)
set_time(period_time(0, DEFAULT_TIME.date() + datetime.timedelta(days=6)))
check("周日排了课也是 NOW（不看星期）", class_ai.get_teacher_duty(101) == (E.TEACHER_DUTY_NOW, ROOM1))
clear_schedules()

section("状态函数：学生上课状态（get_course_stage）")
set_time(period_time(0))
check("本节没课、20 分钟内也没有 → NONE", class_ai.get_course_stage(201) == E.COURSE_STAGE_NONE)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
check("本节有课 → ATTEND", class_ai.get_course_stage(201) == E.COURSE_STAGE_ATTEND)
student.hit_point = 10
check("体力 < 30% → ABSENT_HP", class_ai.get_course_stage(201) == E.COURSE_STAGE_ABSENT_HP)
student.hit_point = 100
growth_handle.get_child_growth(201).skip_class_flag = True
check("今日已翘课 → SKIP", class_ai.get_course_stage(201) == E.COURSE_STAGE_SKIP)
growth_handle.get_child_growth(201).skip_class_flag = False
class_ai.roll_skip_class = lambda cid: True
check("本节掷中翘课 → SKIP", class_ai.get_course_stage(201) == E.COURSE_STAGE_SKIP)
class_ai.roll_skip_class = _orig_roll
set_time(period_time(0) - datetime.timedelta(minutes=15))
check("开课前 15 分钟 → UPCOMING", class_ai.get_course_stage(201) == E.COURSE_STAGE_UPCOMING)
set_time(period_time(0) - datetime.timedelta(minutes=30))
check("开课前 30 分钟 → NONE", class_ai.get_course_stage(201) == E.COURSE_STAGE_NONE)
_today = DEFAULT_TIME.date().toordinal()
sex_class_handle.set_temp_class(_today, 1, ROOM_P, 70, must_attend=[201])
set_time(period_time(1) - datetime.timedelta(minutes=8))
check("本节还有理论课、8 分钟后是必修实操课 → SEX_PENDING（优先于本节的一切）", class_ai.get_course_stage(201) == E.COURSE_STAGE_SEX_PENDING)
check("待赴的实操课教室", class_ai.get_pending_sex_classroom(201) == ROOM_P and class_ai.get_pending_sex_classroom(202) == "")
cache.rhodes_island.temp_sex_class = {}
set_time(period_time(0))
sex_class_handle.set_temp_class(_today, 0, ROOM_P, 70, must_attend=[201])
student.hit_point = 10
growth_handle.get_child_growth(201).skip_class_flag = True
class_ai.roll_skip_class = lambda cid: True
check("必修实操课：体力不足、翘课 flag、掷中翘课同时成立也是 ATTEND（口径 60 / 65）", class_ai.get_course_stage(201) == E.COURSE_STAGE_ATTEND)
class_ai.roll_skip_class = _orig_roll
growth_handle.get_child_growth(201).skip_class_flag = False
student.hit_point = 100
cache.rhodes_island.temp_sex_class = {}
schedule_handle.set_selected_course(101, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
check("非学生岗恒为 NONE：教师身上挂着个人课表也不算", class_ai.get_course_stage(101) == E.COURSE_STAGE_NONE)
schedule_handle.clear_selected_course(101, 0, 0)
student.work.work_type = 21
check("非学生岗恒为 NONE：改了岗的女儿课表还在也不算（口径 1）", class_ai.get_course_stage(201) == E.COURSE_STAGE_NONE)
student.work.work_type = 152
adult = make_character(301, "成年学生", 152)
for _premise in [name for name in constant.handle_premise_data if name.startswith(("teacher_", "self_course_", "self_in_course", "self_not_in_course", "self_sex_class_pending", "self_in_pending", "self_not_in_pending"))]:
    handle_premise.handle_premise(_premise, 301)
check("前提只读：对没有养成数据的学生岗跑一遍师生前提，不会惰性创建养成数据", adult.child_growth is None)
remove_character(301)
clear_schedules()

section("整链派发：教室课（210805 / 220815 / 220820）")
set_time(period_time(0))
for _cid in (101, 102, 201, 202):
    prepare_ai(_cid)
move_to(101, classroom_path(ROOM1))
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [E.ENTERTAINMENT_FREE_PLAY] * 3
# clear_schedules 只清全局课表与临时课，个人课表要自己清（上一段给 201 排的那节理论课还挂着）
schedule_handle.clear_selected_course(201, 0, 0)
sm = dispatch(201)
check("没排课 → 没有上课行命中，交回娱乐链（日程排了自由玩耍 → 去育儿室）", sm == SM.MOVE_TO_NURSERY, sm)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
check("人不在教室 → 715 去教室（目的地与原 561 相同）", dispatch(201) == SM.EDUCATION_MOVE_TO_COURSE_PLACE
      and class_ai.get_course_place_now_or_upcoming(201) == classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
check("到了教室、教师可用 → 304 听课", dispatch(201) == SM.WORK_ATTENT_CLASS)
teacher.sp_flag.is_h = True
check("教师 H 中 → 713 自习", dispatch(201) == SM.EDUCATION_SELF_STUDY)
teacher.sp_flag.is_h = False
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, -1)
check("课表上没排教师 → 713 自习", dispatch(201) == SM.EDUCATION_SELF_STUDY)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, "不存在的教室")
move_to(201, SCENE_DORM)
check("教室解析不出 → 没有上课行命中、交回娱乐链，不再在随机理论教室间打转（Plan 24 §3.7）", dispatch(201) == SM.MOVE_TO_NURSERY)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)

section("整链派发：两道闸（220805 / 220810）")
move_to(201, classroom_path(ROOM1))
student.hit_point = 10
_absent = growth_handle.get_child_growth(201).absent_count
check("体力 < 30% → 721 记缺课并休息", dispatch(201) == SM.EDUCATION_ABSENT_REST and student.behavior.behavior_id == constant.Behavior.REST)
check("体力缺课记了一节", growth_handle.get_child_growth(201).absent_count == _absent + 1)
move_to(201, classroom_path(ROOM1))
dispatch(201)
check("同一节再派发一次不重复记", growth_handle.get_child_growth(201).absent_count == _absent + 1)
check("体力缺课不置翘课 flag", not growth_handle.get_child_growth(201).skip_class_flag)
student.hit_point = 100
growth_handle.get_child_growth(201).skip_class_flag = True
move_to(201, classroom_path(ROOM1))
check("翘课 flag 挂着 → 714 翘课", dispatch(201) == SM.EDUCATION_SKIP_CLASS)
growth_handle.get_child_growth(201).skip_class_flag = False
class_ai.roll_skip_class = lambda cid: True
move_to(201, classroom_path(ROOM1))
check("本节掷中翘课 → 714", dispatch(201) == SM.EDUCATION_SKIP_CLASS)
class_ai.roll_skip_class = lambda cid: False
move_to(201, classroom_path(ROOM1))
check("没掷中 → 照常听课", dispatch(201) == SM.WORK_ATTENT_CLASS)
class_ai.roll_skip_class = _orig_roll

section("整链派发：必修实操课豁免与覆盖")
today = cache.game_time.date().toordinal()
sex_class_handle.set_temp_class(today, 0, ROOM_P, 70, must_attend=[201])
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_PRACTICE, ROOM_P)
check("必修判定成立", class_ai.judge_must_attend_sex_class(201))
check("非必修的人不成立", not class_ai.judge_must_attend_sex_class(202))
move_to(201, classroom_path(ROOM_P))
student.hit_point = 10
_absent = growth_handle.get_child_growth(201).absent_count
sm = dispatch(201)
check("必修 + 体力不足：留在教室听课、不记缺课", sm == SM.WORK_ATTENT_CLASS and growth_handle.get_child_growth(201).absent_count == _absent, sm)
student.hit_point = 100
class_ai.roll_skip_class = lambda cid: True
move_to(201, classroom_path(ROOM_P))
check("必修 + 掷中翘课：不翘课", dispatch(201) == SM.WORK_ATTENT_CLASS)
class_ai.roll_skip_class = _orig_roll
# 第五轮：必修生自己这节排的是别的课，也要留在临时课的教室（口径 60）
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
now_course = schedule_handle.get_now_course(201)
check("必修覆盖：本节的课改指临时课教室、授课者为玩家", now_course is not None and now_course["classroom"] == ROOM_P and now_course["teacher_id"] == 0
      and now_course["ability_id"] == 70 and now_course["course_type"] == E.COURSE_TYPE_PRACTICE, now_course)
move_to(201, classroom_path(ROOM1))
check("必修覆盖：人在原来的教室 → 715 去临时课教室", dispatch(201) == SM.EDUCATION_MOVE_TO_COURSE_PLACE
      and class_ai.get_course_place_now_or_upcoming(201) == classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
check("必修覆盖：到了临时课教室 → 留下听课", dispatch(201) == SM.WORK_ATTENT_CLASS)
schedule_handle.clear_selected_course(201, 0, 0)
check("必修覆盖：本节自己没排课也照样来", schedule_handle.get_now_course(201) is not None and schedule_handle.get_now_course(201)["classroom"] == ROOM_P)
check("非必修且没排课的人不受影响", schedule_handle.get_now_course(202) is None)
cache.rhodes_island.temp_sex_class = {}

section("整链派发：个人式课型（210805 / 220825）")
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_PE, _("木桩房"))
move_to(201, SCENE_DORM)
check("体育课：人不在场地 → 715 移动", dispatch(201) == SM.EDUCATION_MOVE_TO_COURSE_PLACE)
pe_place = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
move_to(201, pe_place)
check("体育课：到场 → 716 执行该课行为", dispatch(201) == SM.EDUCATION_DO_COURSE)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTEREST, 99999)
move_to(201, SCENE_DORM)
check("地点解析不出 → 交回既有 AI（去育儿室自由玩耍）", dispatch(201) == SM.MOVE_TO_NURSERY)


def course_start_place(place: list) -> list:
    """
    取派发「不在上课地点」时学生的起点：默认宿舍，上课地点恰好是那间宿舍时改用教育区入口
    Keyword arguments:
    place -- 上课地点的场景路径
    Return arguments:
    list -- 起点的场景路径
    """
    if scene_str(place) == scene_str(SCENE_DORM):
        return SCENE_EDU_ENTRY
    return SCENE_DORM


section("整链派发：兴趣课逐项（Entertainment.csv 里 class_ok 的全部娱乐）")
_interest_list = [cid for cid in game_config.config_entertainment if game_config.config_entertainment[cid].class_ok]
check("可排兴趣课的娱乐有 16 项", len(_interest_list) == 16, len(_interest_list))
_interest_bad = []
for _cid in _interest_list:
    _cfg = game_config.config_entertainment[_cid]
    schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTEREST, _cid)
    set_time(period_time(0))
    _place = class_ai.get_course_place_now_or_upcoming(201)
    if not _place:
        _interest_bad.append((_cid, _cfg.name, "地点解析不出"))
        continue
    move_to(201, course_start_place(_place))
    _move_sm = dispatch(201)
    move_to(201, _place)
    _do_sm = dispatch(201)
    _expect_behavior = schedule_handle.get_behavior_name_by_cid(_cfg.behavior_id)
    if (_move_sm != SM.EDUCATION_MOVE_TO_COURSE_PLACE or _do_sm != SM.EDUCATION_DO_COURSE or not _expect_behavior
            or student.behavior.behavior_id != _expect_behavior or student.state != _cfg.behavior_id or student.behavior.duration != 45):
        _interest_bad.append((_cid, _cfg.name, scene_str(_place), _move_sm, _do_sm, student.behavior.behavior_id, _expect_behavior, student.behavior.duration))
check("兴趣课逐项：不在地点 → 715，到场 → 716 执行该娱乐的行为、时长截到本节结束（45 分钟）", not _interest_bad, _interest_bad)

section("整链派发：实习课逐岗（WorkType.csv 里可排实习的全部岗位）")
_intern_list = [cid for cid in game_config.config_work_type
                if cid and not game_config.config_work_type[cid].tag and game_config.config_work_type[cid].ability_id
                and cid not in E.EXCLUDE_INTERN_WORK_TYPE]
check("可排实习的岗位取到了", len(_intern_list) > 0, _intern_list)
_intern_bad = []
for _wid in _intern_list:
    _cfg = game_config.config_work_type[_wid]
    schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTERN, _wid)
    set_time(period_time(0))
    _place = class_ai.get_course_place_now_or_upcoming(201)
    if not _place:
        _intern_bad.append((_wid, _cfg.name, "地点解析不出"))
        continue
    move_to(201, course_start_place(_place))
    _move_sm = dispatch(201)
    move_to(201, _place)
    _do_sm = dispatch(201)
    if (_move_sm != SM.EDUCATION_MOVE_TO_COURSE_PLACE or _do_sm != SM.EDUCATION_DO_COURSE or student.behavior.behavior_id != constant.Behavior.INTERN_CLASS
            or student.state != constant.CharacterStatus.STATUS_INTERN_CLASS or student.behavior.duration != 45):
        _intern_bad.append((_wid, _cfg.name, scene_str(_place), _move_sm, _do_sm, student.behavior.behavior_id, student.behavior.duration))
check(f"实习课逐岗（{len(_intern_list)} 个岗位，无人在岗）：不在地点 → 715，到场 → 716 执行实习、时长截到本节结束", not _intern_bad, _intern_bad)
# 实习的地点跟着人走（口径 53）：同一标签下有多间房的岗位，导师在哪间学徒就去哪间
_multi_work = next((wid for wid in _intern_list if len(constant.place_data.get(game_config.config_work_type[wid].place_tag, [])) >= 2), None)
check("有同一标签下多间房的实习岗位", _multi_work is not None, _intern_list)
if _multi_work is not None:
    schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTERN, _multi_work)
    set_time(period_time(0))
    _default_place = class_ai.get_course_place_now_or_upcoming(201)
    _other_str = next(s for s in constant.place_data[game_config.config_work_type[_multi_work].place_tag] if s != scene_str(_default_place))
    _other_place = map_handle.get_map_system_path_for_str(_other_str)
    make_character(401, "带教", _multi_work, position=_other_place)
    check("导师在另一间房 → 学徒的上课地点改指导师那间", class_ai.get_course_place_now_or_upcoming(201) == _other_place,
          (game_config.config_work_type[_multi_work].name, scene_str(_default_place), _other_str))
    move_to(201, _default_place)
    check("学徒在默认那间、导师不在 → 715 去导师那间", dispatch(201) == SM.EDUCATION_MOVE_TO_COURSE_PLACE)
    move_to(201, _other_place)
    check("到了导师那间 → 716 实习，并找得到这位导师", dispatch(201) == SM.EDUCATION_DO_COURSE and student.behavior.behavior_id == constant.Behavior.INTERN_CLASS
          and schedule_handle.get_intern_mentor(201, _multi_work) == 401)
    remove_character(401)
move_to(201, SCENE_DORM)
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()

section("见学：母亲有效性")
check("有效母亲", class_ai.judge_mother_available(202) == 102)
mother.sp_flag.is_h = True
check("母亲 H 中 → 无效", class_ai.judge_mother_available(202) == -1)
mother.sp_flag.is_h = False
mother.sp_flag.imprisonment = True
check("母亲被监禁 → 无效", class_ai.judge_mother_available(202) == -1)
mother.sp_flag.imprisonment = False
mother.dead = True
check("母亲死亡 → 无效", class_ai.judge_mother_available(202) == -1)
mother.dead = False
cache.character_data[202].relationship.mother_id = -1
check("没有母亲 → 无效", class_ai.judge_mother_available(202) == -1)
cache.character_data[202].relationship.mother_id = 102

section("见学：触发与回落链")
set_time(period_time(0))
student.entertainment.entertainment_type = [0, 0, 0]
check("幼女在节次内没课 → 该见学", class_ai.judge_should_follow_mother(202))
# 2026-09-10 §9.2.9：该时段明确排了别的活动且已写进槽位 → 不见学，交给娱乐链去做那个活动
_tpl = schedule_template_handle.create_template("幼女白天")
schedule_template_handle.set_template_slot(_tpl, 0, E.ENTERTAINMENT_FREE_PLAY)
schedule_template_handle.apply_template(202, _tpl)
schedule_template_handle.apply_schedule_for_child(202)
check("幼女上午明确排了自由玩耍且已写入 → 不见学", not class_ai.judge_should_follow_mother(202) and child.entertainment.entertainment_type[0] == E.ENTERTAINMENT_FREE_PLAY)
schedule_template_handle.set_template_slot(_tpl, 0, E.ENTERTAINMENT_FOLLOW_MOTHER)
schedule_template_handle.apply_schedule_for_child(202)
check("幼女上午排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(202))
schedule_template_handle.set_template_slot(_tpl, 0, E.ENTERTAINMENT_FREE_PLAY)
child.entertainment.entertainment_type[0] = E.ENTERTAINMENT_PLAY_HOUSE
check("模板排了活动但没写进槽位（退回自由选择）→ 仍默认见学", class_ai.judge_should_follow_mother(202))
schedule_template_handle.set_template_slot(_tpl, 0, 0)
check("时段为自由选择 → 默认见学", class_ai.judge_should_follow_mother(202))
schedule_template_handle.apply_template(202, 0)
child.entertainment.entertainment_type = [0, 0, 0]
check("萝莉不见学", not class_ai.judge_should_follow_mother(201))
# 个人课表指向的格子要在全局课表上有课：空格子按「已停课」算没课（Plan 27 §3.3）
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(202, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
check("幼女本节有课 → 不见学", not class_ai.judge_should_follow_mother(202))
schedule_handle.clear_selected_course(202, 0, 0)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
set_time(DEFAULT_TIME.replace(hour=19, minute=30))
cache.character_data[202].entertainment.entertainment_type = [0, 0, E.ENTERTAINMENT_FOLLOW_MOTHER]
check("晚上日程排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(202))
cache.character_data[202].entertainment.entertainment_type = [0, 0, 0]
check("晚上日程没排 → 不见学", not class_ai.judge_should_follow_mother(202))

section("见学：萝莉按日程可见学（2026-09-09 放宽）")
student.entertainment.entertainment_type = [0, 0, E.ENTERTAINMENT_FOLLOW_MOTHER]
check("萝莉晚上日程排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(201))
student.entertainment.entertainment_type = [0, 0, 0]
check("萝莉晚上日程没排 → 不见学", not class_ai.judge_should_follow_mother(201))
set_time(period_time(0))
student.entertainment.entertainment_type = [E.ENTERTAINMENT_FOLLOW_MOTHER, 0, 0]
check("萝莉节次内没课、上午日程排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(201))
schedule_handle.set_class_cell(ROOM1, cache.game_time.weekday(), 0, 45, 101)
schedule_handle.set_selected_course(201, cache.game_time.weekday(), 0, E.COURSE_TYPE_THEORY, ROOM1)
check("萝莉本节有课 → 有课优先，不见学", not class_ai.judge_should_follow_mother(201))
schedule_handle.clear_selected_course(201, cache.game_time.weekday(), 0)
schedule_handle.clear_class_cell(ROOM1, cache.game_time.weekday(), 0)
student.entertainment.entertainment_type = [0, 0, 0]
check("萝莉节次内没课但日程没排 → 自由行动（口径 10 的默认不变）", not class_ai.judge_should_follow_mother(201))
girl = make_character(203, "女儿C", 152, daughter=True, stage=104, mother_id=102, born_days=500)
girl.entertainment.entertainment_type = [E.ENTERTAINMENT_FOLLOW_MOTHER] * 3
check("少女日程排了跟随母亲也不见学", not class_ai.judge_should_follow_mother(203))
set_time(period_time(0))
move_to(102, SCENE_EDU_ENTRY)
move_to(202, SCENE_DORM)
check("母亲有效、不同场景 → 移动到母亲身边", class_ai.judge_follow_mother_state_machine(202) == SM.EDUCATION_MOVE_TO_MOTHER)
move_to(202, SCENE_EDU_ENTRY)
check("同场景 → 见学", class_ai.judge_follow_mother_state_machine(202) == SM.EDUCATION_FOLLOW_MOTHER)
mother.sp_flag.is_h = True
check("母亲无效 → 回落自由玩耍而不是交回 AI", class_ai.judge_follow_mother_state_machine(202) == SM.ENTERTAIN_FREE_PLAY)
mother.sp_flag.is_h = False
growth_handle.get_child_growth(202).follow_mother_flag = True
check("见学标记读口", class_ai.judge_in_follow_mother(202) and not class_ai.judge_in_follow_mother(201) and not class_ai.judge_in_follow_mother(999))
check("不该见学时顺手清标记", (class_ai.judge_follow_mother_state_machine(201), class_ai.judge_in_follow_mother(202))[0] == 0)
class_ai.clear_follow_mother_flag(202)
check("清标记", not class_ai.judge_in_follow_mother(202))
class_ai.clear_follow_mother_flag(999)
check("对不存在的角色清标记不报错", True)

section("见学让路：学生与课表有关时不见学（Plan 24 §3.9）")
clear_schedules()
move_to(102, SCENE_EDU_ENTRY)
move_to(202, SCENE_DORM)
child.entertainment.entertainment_type = [0, 0, 0]
_pending_time = period_time(1) - datetime.timedelta(minutes=8)
set_time(_pending_time)
check("幼女在节次内没课 → 默认见学", class_ai.judge_should_follow_mother(202))
sex_class_handle.set_temp_class(_pending_time.date().toordinal(), 1, ROOM_P, 70, must_attend=[202])
check("有待赴的必修实操课 → 不见学（原先预到岗排在见学之前）", not class_ai.judge_should_follow_mother(202))
check("整条链：见学让路后派 561 提前去实操教室", dispatch(202, _pending_time) == SM.MOVE_TO_CLASS_ROOM)
child.work.work_type = 21
check("改了岗的幼女不上课，也就不必让路 → 照常见学（口径 1）", class_ai.judge_should_follow_mother(202))
child.work.work_type = 152
cache.rhodes_island.temp_sex_class = {}
class_ai.clear_follow_mother_flag(202)

section("没课节次的去向（2026-09-10 §9.2.9）")
set_time(period_time(0))
check("周一上午：学生岗算娱乐时间、教师岗与普通岗不算", handle_premise.handle_all_entertainment_time(201) > 0 and handle_premise.handle_all_entertainment_time(101) == 0
      and handle_premise.handle_all_entertainment_time(102) == 0)
check("非全娱乐时间前提与之互补", handle_premise.handle_not_all_entertainment_time(201) == 0 and handle_premise.handle_not_all_entertainment_time(102) > 0)
set_time(period_time(0, DEFAULT_TIME.date() + datetime.timedelta(days=6)))
check("周日上午：谁都算娱乐时间", handle_premise.handle_all_entertainment_time(201) > 0 and handle_premise.handle_all_entertainment_time(102) > 0)
set_time(period_time(0))
clear_schedules()
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [E.ENTERTAINMENT_FREE_PLAY, 0, 0]
check("萝莉周一上午没课、日程排了自由玩耍 → 工作链没有行命中，去育儿室", dispatch(201) == SM.MOVE_TO_NURSERY)
move_to(201, SCENE_NURSERY)
check("到了育儿室 → 自由玩耍", dispatch(201) == SM.ENTERTAIN_FREE_PLAY)
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [E.ENTERTAINMENT_SELF_STUDY, 0, 0]
check("排了上课（无课时自习）、人在宿舍 → 去教室", dispatch(201) == SM.MOVE_TO_CLASS_ROOM)
move_to(201, classroom_path(ROOM1))
check("到了教室 → 自习", dispatch(201) == SM.EDUCATION_SELF_STUDY)
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [0, 0, 0]
move_to(202, SCENE_DORM)
move_to(102, SCENE_EDU_ENTRY)
_tpl2 = schedule_template_handle.create_template("幼女白天2")
schedule_template_handle.set_template_slot(_tpl2, 0, E.ENTERTAINMENT_FREE_PLAY)
schedule_template_handle.apply_template(202, _tpl2)
schedule_template_handle.apply_schedule_for_child(202)
check("幼女周一上午没课、日程排了自由玩耍 → 去育儿室而不是见学", dispatch(202) == SM.MOVE_TO_NURSERY)
schedule_template_handle.apply_template(202, 0)
child.entertainment.entertainment_type = [0, 0, 0]
check("幼女时段为自由选择 → 默认见学（移动到母亲身边）", dispatch(202) == SM.EDUCATION_MOVE_TO_MOTHER)
class_ai.clear_follow_mother_flag(202)

section("整链派发：教师按课表走班（210700 ~ 220710）")
clear_schedules()
office_path = map_handle.get_map_system_path_for_str(constant.place_data["Teacher_Office"][0])
move_to(101, classroom_path(ROOM1))
schedule_handle.set_class_cell(ROOM_P, 0, 0, 43, 101)
check("本节课排在实践教室、人在理论教室 → 561 移动（不再原地开讲）", dispatch(101) == SM.MOVE_TO_CLASS_ROOM)
move_to(101, classroom_path(ROOM_P))
check("到了实践教室 → 303 授课", dispatch(101) == SM.WORK_TEACH)
check("非教师不命中教师行", dispatch(201) not in (SM.WORK_TEACH, SM.MOVE_TO_TEACHER_OFFICE))
today = cache.game_time.date().toordinal()
sex_class_handle.set_temp_class(today, 0, ROOM_P, 70, must_attend=[])
check("这一格今天被临时实操课顶掉 → 教师反查查不到", schedule_handle.get_teacher_cell(101, 0, 0) is None)
check("被顶掉的教师 → 562 回办公室待命", dispatch(101) == SM.MOVE_TO_TEACHER_OFFICE)
cache.rhodes_island.temp_sex_class = {}
schedule_handle.clear_class_cell(ROOM_P, 0, 0)
check("本节没课、工作时间 → 562 回教师办公室", dispatch(101) == SM.MOVE_TO_TEACHER_OFFICE)
move_to(101, office_path)
check("已在办公室 → 720 待命", dispatch(101) == SM.EDUCATION_WAIT_NEXT_PERIOD)
check("午休（12:30）没课 → 没有教师行命中（不在到岗 / 工作时间）", dispatch(101, DEFAULT_TIME.replace(hour=12, minute=30)) not in CLASS_SM_SET)
_arrive_time = period_time(0) - datetime.timedelta(minutes=15)
schedule_handle.set_class_cell(ROOM_P, 0, 0, 43, 101)
move_to(101, office_path)
check("到岗时间、第一节在实践教室 → 561 先去实践教室", dispatch(101, _arrive_time) == SM.MOVE_TO_CLASS_ROOM
      and schedule_handle.get_upcoming_teaching(101)["classroom"] == ROOM_P)
move_to(101, classroom_path(ROOM_P))
check("到岗时间已在教室 → 720 等开课", dispatch(101, _arrive_time) == SM.EDUCATION_WAIT_NEXT_PERIOD)
check("等开课的时长截到开课那一刻（15 分钟）", teacher.behavior.behavior_id == constant.Behavior.WAIT and teacher.behavior.duration == 15, teacher.behavior.duration)
sunday = DEFAULT_TIME.date() + datetime.timedelta(days=6)
move_to(101, office_path)
check("周日没课 → 没有教师行命中（休息日）", dispatch(101, period_time(0, sunday)) not in CLASS_SM_SET)
schedule_handle.set_class_cell(ROOM_P, 6, 0, 43, 101)
check("周日玩家特意排了课 → 561 照样去上（外层闸只判有工作）", dispatch(101, period_time(0, sunday)) == SM.MOVE_TO_CLASS_ROOM)
move_to(101, classroom_path(ROOM_P))
check("周日到了教室 → 303 授课", dispatch(101, period_time(0, sunday)) == SM.WORK_TEACH)
clear_schedules()

section("整链派发：学生到岗时间先去第一节课（210810 / 220830）")
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
student.entertainment.entertainment_type = [E.ENTERTAINMENT_FREE_PLAY] * 3
move_to(201, SCENE_DORM)
check("开课前 30 分钟 → 还不动身", dispatch(201, period_time(0) - datetime.timedelta(minutes=30)) not in CLASS_SM_SET)
move_to(201, SCENE_DORM)
check("开课前 15 分钟、人在宿舍 → 715 去第一节课的教室", dispatch(201, _arrive_time) == SM.EDUCATION_MOVE_TO_COURSE_PLACE
      and class_ai.get_course_place_now_or_upcoming(201) == classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
check("已在教室 → 720 原地等开课", dispatch(201, _arrive_time) == SM.EDUCATION_WAIT_NEXT_PERIOD)
check("节次开始时离下一节还有 45 分钟 → 不在「马上开课」窗口里", (set_time(period_time(0)), schedule_handle.get_upcoming_course(201))[1] is None)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_PE, _("木桩房"))
move_to(201, SCENE_DORM)
check("第一节是体育课 → 715 去训练场", dispatch(201, _arrive_time) == SM.EDUCATION_MOVE_TO_COURSE_PLACE
      and class_ai.get_course_place_now_or_upcoming(201) == schedule_handle.get_course_place({"course_type": E.COURSE_TYPE_PE, "target": _("木桩房")}))
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()

section("整链派发：性技实操课预到岗（210800 / 220800）")
today = DEFAULT_TIME.date().toordinal()
sex_class_handle.set_temp_class(today, 1, ROOM_P, 70, must_attend=[201])
_pending_time = period_time(1) - datetime.timedelta(minutes=8)
set_time(_pending_time)
move_to(201, SCENE_DORM)
temp_class, classroom = class_ai.get_next_sex_class(201, cache.game_time)
check("距开始 8 分钟：必修者要动身", temp_class is not None and classroom == ROOM_P)
check("整条链：派 561 去实操教室", dispatch(201, _pending_time) == SM.MOVE_TO_CLASS_ROOM)
set_time(period_time(1) - datetime.timedelta(minutes=15))
check("距开始 15 分钟：还不动身", class_ai.get_next_sex_class(201, cache.game_time)[0] is None)
set_time(_pending_time)
check("非必修且没选修的人不动身", class_ai.get_next_sex_class(202, cache.game_time)[0] is None)
schedule_handle.set_selected_course(202, cache.game_time.weekday(), 1, E.COURSE_TYPE_PRACTICE, ROOM_P)
check("选修了这间教室的人也动身", class_ai.get_next_sex_class(202, cache.game_time)[0] is not None)
schedule_handle.clear_selected_course(202, cache.game_time.weekday(), 1)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
move_to(201, classroom_path(ROOM1))
check("本节还在上理论课 → 提前退场去实操教室（口径 62）", dispatch(201, _pending_time) == SM.MOVE_TO_CLASS_ROOM)
move_to(201, classroom_path(ROOM_P))
_absent = growth_handle.get_child_growth(201).absent_count
check("已在实操教室 → 720 原地等开课（Plan 24 §3.6，原先原地零距离移动空转）", dispatch(201, _pending_time) == SM.EDUCATION_WAIT_NEXT_PERIOD
      and student.behavior.duration == 8, student.behavior.duration)
check("预到岗不记缺课", growth_handle.get_child_growth(201).absent_count == _absent)
clear_schedules()

section("normal 门槛：跟随 / 临盆 / 产后 / 助理 / 体检中（Plan 24 §3.4）")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
for _cid, _name in ((101, "教师"), (201, "学生")):
    _cd = cache.character_data[_cid]
    move_to(0, SCENE_EDU_ENTRY)
    move_to(_cid, SCENE_EDU_ENTRY)
    _cd.sp_flag.is_follow = 1
    _first = dispatch(_cid)
    move_to(_cid, classroom_path(ROOM1))
    _second = dispatch(_cid)
    _cd.sp_flag.is_follow = 0
    check(f"跟随中的{_name}：在玩家身边不被派去教室、在教室被拉回玩家身边（不再来回走）", _first not in CLASS_SM_SET and _second not in CLASS_SM_SET, (_first, _second))
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
_waiting = cache.rhodes_island.waiting_for_exam_operator_ids
for _name, _toggle in (
    ("临盆", lambda on: teacher.talent.__setitem__(22, 1 if on else 0)),
    ("产后", lambda on: teacher.talent.__setitem__(23, 1 if on else 0)),
    ("当助理", lambda on: setattr(pl, "assistant_character_id", 101 if on else 0)),
    ("体检中", lambda on: _waiting.add(101) if on else _waiting.discard(101)),
):
    _toggle(True)
    _available = teacher_available()
    _teacher_sm = dispatch(101)
    move_to(101, classroom_path(ROOM1))
    _student_sm = dispatch(201)
    _toggle(False)
    check(f"{_name}的教师：判为不可用、自己不授课，学生在教室派 713 自习", not _available and _teacher_sm not in CLASS_SM_SET and _student_sm == SM.EDUCATION_SELF_STUDY,
          (_available, _teacher_sm, _student_sm))
move_to(101, classroom_path(ROOM1))
check("状态解除后教师照常授课", dispatch(101) == SM.WORK_TEACH)
check("状态解除后学生照常听课", dispatch(201) == SM.WORK_ATTENT_CLASS)
clear_schedules()

section("外层闸只判有工作（Plan 24 §3.1，与改动前基线一致）")
libm = make_character(301, "图书管理员", 101)
cook = make_character(302, "厨师", 51)
for _cid in (301, 302):
    prepare_ai(_cid)
_work_rows = list(game_config.config_target_type_index[21]) + list(game_config.config_target_type_index[22])
LIBRARY_SM_SET = {game_config.config_target[t].state_machine_id for t in _work_rows if "work_is_library_manager" in game_config.config_target_premise_data.get(t, set())}
COOK_SM_SET = {int(game_config.config_work_type[51].auto_ai_move), int(str(game_config.config_work_type[51].auto_ai_work).split("|")[0])}
check("岗位状态机集合取到了", LIBRARY_SM_SET and len(COOK_SM_SET) == 2, (LIBRARY_SM_SET, COOK_SM_SET))
_times = (("工作日 10:00", DEFAULT_TIME.replace(hour=10)), ("工作日 19:30", DEFAULT_TIME.replace(hour=19, minute=30)),
          ("周日 10:00", DEFAULT_TIME.replace(hour=10) + datetime.timedelta(days=6)))
_result = {}
for _cid in (301, 302):
    for _label, _now in _times:
        move_to(_cid, SCENE_DORM)
        _result[(_cid, _label)] = dispatch(_cid, _now)
check("工作日 10:00：图书馆管理员（auto_ai=0）去图书馆办公室、厨师（auto_ai=1）去厨房", _result[(301, "工作日 10:00")] == 551 and _result[(302, "工作日 10:00")] == 521, _result)
check("下班与周日：工作链没有行命中，与改动前一样落到娱乐链", all(_result[(301, label)] not in LIBRARY_SM_SET and _result[(302, label)] not in COOK_SM_SET
                                                        for label in ("工作日 19:30", "周日 10:00")), _result)
remove_character(301)
remove_character(302)

section("口径收窄：课表只对学生岗（Plan 24 口径 1）")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
student.work.work_type = 21
sm = dispatch(201)
check("女儿改成 21 岗：有课表也不派任何上课行，按新岗位上班", sm not in CLASS_SM_SET, sm)
check("改岗后不在个人课表名单", 201 not in growth_handle.get_course_candidate_list())
student.work.work_type = 152
move_to(201, classroom_path(ROOM1))
check("改回学生岗：课表恢复生效、回到名单", dispatch(201) == SM.WORK_ATTENT_CLASS and 201 in growth_handle.get_course_candidate_list())
clear_schedules()

section("Plan 25 §3.3：教师可用性对齐授课行（醉酒 / 催眠）")
set_time(period_time(0))
teacher.drunk_point = 99999
check("醉到烂醉的教师不可用（授课行的 normal 前提不成立）", not teacher_available())
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
_student_sm = dispatch(201)
_teacher_sm = dispatch(101)
check("醉酒教师：学生在教室派 713 自习、教师自己不授课（原先学生对着她空坐一整节）", _student_sm == SM.EDUCATION_SELF_STUDY and _teacher_sm != SM.WORK_TEACH,
      (_student_sm, _teacher_sm))
teacher.drunk_point = 0
# 醉酒时派发的是睡觉：先把她叫起来，下面只验催眠与恢复
teacher.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
teacher.sp_flag.sleep = False
teacher.sp_flag.unconscious_h = 5
check("空气催眠中的教师仍可用（授课行挂的是 normal_all_except_special_hypnosis）", teacher_available())
teacher.sp_flag.unconscious_h = 0
check("恢复后可用", teacher_available(), (teacher.sp_flag.sleep, teacher.sp_flag.is_h, teacher.behavior.behavior_id, teacher.drunk_point,
                                     [handle_premise.handle_premise(f"normal_{n}", 101) for n in range(1, 8)]))
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()


def begin(cid: int, behavior_id: str, start: datetime.datetime, now: datetime.datetime, duration: int = 60) -> None:
    """
    让角色从 start 起在做某个行为，再把游戏时间拨到 now（打断判定读的是「现在」，不是行为的开始时刻）
    Keyword arguments:
    cid -- 角色id
    behavior_id -- 行为id
    start -- 行为开始时刻
    now -- 当前游戏时间
    duration -- 行为时长
    Return arguments:
    无
    """
    set_time(start)
    cd = cache.character_data[cid]
    cd.behavior.behavior_id = behavior_id
    cd.behavior.duration = duration
    cd.behavior.move_target = []
    cd.behavior.move_final_target = []
    cd.action_info.wake_time = start
    cache.game_time = now
    handle_premise.refresh_unnormal_flag(cid)


section("Plan 25 §3.1：学生赶去上课——把当前行为截到应离开的时刻（A 待赴实操课 / B 马上开课）")
move_to(0, SCENE_DORM)
# 玩家这一步走到了开课之后：「现在」已越过开课时刻，规则按 NPC 自己的行为时间轴截短，不看「现在」
_round_end = period_time(1) + datetime.timedelta(minutes=5)
_leave_a = period_time(1) - datetime.timedelta(minutes=E.PRE_ARRIVE_MINUTE)
_leave_b = period_time(1) - datetime.timedelta(minutes=E.UPCOMING_MINUTE)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
sex_class_handle.set_temp_class(DEFAULT_TIME.date().toordinal(), 1, ROOM_P, 70, must_attend=[201])
move_to(201, classroom_path(ROOM1))
begin(201, constant.Behavior.ATTENT_CLASS, period_time(0), _round_end, 45)
_absent = growth_handle.get_child_growth(201).absent_count
check("A 听课中、下一节是必修实操课 → 截到开课前 10 分钟（口径 62 提前退场；玩家一步跨过开课时刻也照截）",
      handle_npc_ai.judge_interrupt_character_behavior(201) == 1 and student.behavior.behavior_id == constant.Behavior.ATTENT_CLASS and student.behavior.duration == 35,
      student.behavior.duration)
check("A 提前退场不记缺课（口径 66）", growth_handle.get_child_growth(201).absent_count == _absent)
check("A 在离开的那一刻重新决策 → 派 561 去实操教室", dispatch(201, _leave_a) == SM.MOVE_TO_CLASS_ROOM)
move_to(201, classroom_path(ROOM1))
begin(201, constant.Behavior.ATTENT_CLASS, period_time(0), _round_end, 35)
check("A 已截过的行为不再截（离开时刻恰是行为结束）", handle_npc_ai.judge_interrupt_character_behavior(201) == 0 and student.behavior.duration == 35)
cache.rhodes_island.temp_sex_class = {}
sex_class_handle.set_temp_class(DEFAULT_TIME.date().toordinal(), 2, ROOM_P, 70, must_attend=[201])
begin(201, constant.Behavior.ATTENT_CLASS, period_time(0), _round_end, 45)
check("A 实操课在再后面一节 → 离开时刻不在本行为之内，不截", handle_npc_ai.judge_interrupt_character_behavior(201) == 0 and student.behavior.duration == 45)
cache.rhodes_island.temp_sex_class = {}
sex_class_handle.set_temp_class(DEFAULT_TIME.date().toordinal(), 1, ROOM_P, 70, must_attend=[201])
move_to(201, SCENE_DORM)
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
check("A 娱乐中 → 同样截到开课前 10 分钟", handle_npc_ai.judge_interrupt_character_behavior(201) == 1 and student.behavior.duration == 35, student.behavior.duration)
move_to(201, classroom_path(ROOM_P))
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
check("A 人已在实操教室 → 不截", handle_npc_ai.judge_interrupt_character_behavior(201) == 0)
move_to(201, SCENE_DORM)
begin(201, constant.Behavior.WAIT, period_time(0), _round_end)
check("A 在做日常类行为（等待）→ 不截：只截工作 / 娱乐类", handle_npc_ai.judge_interrupt_character_behavior(201) == 0)
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
student.sp_flag.is_follow = 1
handle_premise.refresh_unnormal_flag(201)
check("A 跟随玩家中（normal_all 不成立）→ 不截，截了 AI 也派不出上课行", handle_npc_ai.judge_interrupt_character_behavior(201) == 0)
student.sp_flag.is_follow = 0
handle_premise.refresh_unnormal_flag(201)
begin(101, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
check("非学生岗不截", handle_npc_ai.judge_interrupt_character_behavior(101) == 0)
begin(201, constant.Behavior.FREE_PLAY, _round_end, _round_end)
check("本轮刚开始的行为不截（既有守卫）", handle_npc_ai.judge_interrupt_character_behavior(201) == 0)
clear_schedules()
schedule_handle.clear_selected_course(201, 0, 0)
schedule_handle.set_class_cell(ROOM1, 0, 1, 45, 101)
schedule_handle.set_selected_course(201, 0, 1, E.COURSE_TYPE_THEORY, ROOM1)
set_time(period_time(1) - datetime.timedelta(minutes=15))
check("B 节次内也看下一节：本节没课、15 分钟后有课 → UPCOMING（与教师同口径）", class_ai.get_course_stage(201) == E.COURSE_STAGE_UPCOMING)
move_to(201, SCENE_DORM)
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
check("B 没课的节次在娱乐、下一节有课 → 截到开课前 20 分钟", handle_npc_ai.judge_interrupt_character_behavior(201) == 1 and student.behavior.duration == 25,
      student.behavior.duration)
check("B 在离开的那一刻重新决策 → 715 去上课地点", dispatch(201, _leave_b) == SM.EDUCATION_MOVE_TO_COURSE_PLACE)
move_to(201, classroom_path(ROOM1))
check("B 到了教室 → 720 原地等开课", dispatch(201, _leave_b) == SM.EDUCATION_WAIT_NEXT_PERIOD)
move_to(201, SCENE_DORM)
begin(201, constant.Behavior.FREE_PLAY, period_time(1) - datetime.timedelta(minutes=10), _round_end)
check("B 行为开始时已进窗口 → 至少别拖过开课：截到开课那一刻", handle_npc_ai.judge_interrupt_character_behavior(201) == 1 and student.behavior.duration == 10,
      student.behavior.duration)
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end, 10)
check("B 行为在离开时刻之前就结束 → 不截", handle_npc_ai.judge_interrupt_character_behavior(201) == 0 and student.behavior.duration == 10)
growth_handle.get_child_growth(201).skip_class_flag = True
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
check("B 今天已翘课 → 不截", handle_npc_ai.judge_interrupt_character_behavior(201) == 0)
growth_handle.get_child_growth(201).skip_class_flag = False
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTEREST, _interest_list[0])
begin(201, constant.Behavior.FREE_PLAY, period_time(0), _round_end)
check("B 离开的那一刻本节还有课（个人式课）→ 不截，本节的课由节末自然结束", handle_npc_ai.judge_interrupt_character_behavior(201) == 0)
schedule_handle.clear_selected_course(201, 0, 0)
schedule_handle.clear_selected_course(201, 0, 1)
clear_schedules()

section("Plan 25 §3.2：开课后才到场的学生直接加入课堂")
set_time(period_time(5))
move_to(0, classroom_path(ROOM_P))
schedule_handle.set_class_cell(ROOM_P, 0, 5, 74, -1)
schedule_handle.set_selected_course(202, 0, 5, E.COURSE_TYPE_PRACTICE, ROOM_P)
sex_class_handle.start_sex_class(70, [])
cache.sex_class_mode = True
cache.group_sex_mode = True
pl.sp_flag.is_h = True
_late = period_time(5) + datetime.timedelta(minutes=10)
move_to(202, SCENE_DORM)
check("还没到教室 → 715 先过去（仍是 ATTEND）", dispatch(202, _late) == SM.EDUCATION_MOVE_TO_COURSE_PLACE)
move_to(202, classroom_path(ROOM_P))
_attend = growth_handle.get_child_growth(202).attend_class_count
check("走进正在上实操课的教室 → JOIN_SEX_CLASS", (set_time(_late), class_ai.get_course_stage(202))[1] == E.COURSE_STAGE_JOIN_SEX_CLASS)
sm = dispatch(202, _late)
check("派 722：进 H、看见玩家的 H、到场二段口上（原先 713 在一边自习）", sm == SM.EDUCATION_JOIN_SEX_CLASS and child.sp_flag.is_h and child.sp_flag.see_pl_h
      and child.second_behavior.get(constant.Behavior.JOIN_SEX_CLASS, 0) > 0, sm)
check("晚到的人补记一节出勤", growth_handle.get_child_growth(202).attend_class_count == _attend + 1)
child.sp_flag.is_h = False
child.sp_flag.see_pl_h = False
make_character(301, "成年学生", 152)
prepare_ai(301)
schedule_handle.set_selected_course(301, 0, 5, E.COURSE_TYPE_PRACTICE, ROOM_P)
move_to(301, classroom_path(ROOM_P))
set_time(_late)
check("不满足 H 模式实行值的成年学生 → 仍是 ATTEND，进不了课堂（口径 63 第二层）", class_ai.get_course_stage(301) == E.COURSE_STAGE_ATTEND)
remove_character(301)
pl.sp_flag.is_h = False
sex_class_handle.end_sex_class()
cache.sex_class_mode = False
set_time(_late)
check("下课后不再 JOIN", class_ai.get_course_stage(202) != E.COURSE_STAGE_JOIN_SEX_CLASS)
schedule_handle.clear_selected_course(202, 0, 5)
clear_schedules()
move_to(0, SCENE_DORM)
move_to(202, SCENE_DORM)

section("Plan 25 §3.5：教师开讲时拉人过两道闸")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))


def teach_pull(cid: int) -> bool:
    """
    教师在节次开始时开讲（直接跑 303），看 cid 有没有被拉成听课
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    bool -- 是否被拉成听课
    """
    set_time(period_time(0))
    cache.character_data[cid].behavior.behavior_id = constant.Behavior.WAIT
    constant.handle_state_machine_data[SM.WORK_TEACH](101)
    return cache.character_data[cid].behavior.behavior_id == constant.Behavior.ATTENT_CLASS


check("正常学生被拉进听课", teach_pull(201))
student.hit_point = 10
check("体力 < 30% 的学生不拉（她自己决策时走 721 缺课）", not teach_pull(201))
student.hit_point = 100
class_ai.roll_skip_class = lambda cid, now_time=None: True
check("本节掷中翘课的学生不拉", not teach_pull(201))
class_ai.roll_skip_class = _orig_roll
student.work.work_type = 21
check("课表有残留、已改岗的人不拉（口径 1）", not teach_pull(201))
student.work.work_type = 152
sex_class_handle.set_temp_class(period_time(0).date().toordinal(), 0, ROOM1, 70, must_attend=[201])
student.hit_point = 10
check("必修生体力不足也该来（豁免两道闸）", class_ai.judge_student_join_class(201, ROOM1, period_time(0)))
student.hit_point = 100
check("这一节课表指向别的教室的不算", not class_ai.judge_student_join_class(201, _("理论教室二"), period_time(0)))
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()

section("Plan 25 §3.6：561 预到岗只认学生岗")
from Script.StateMachine import default as sm_default  # noqa: E402

_pending_time = period_time(1) - datetime.timedelta(minutes=8)
schedule_handle.set_class_cell(ROOM1, 0, 1, 45, 101)
schedule_handle.set_selected_course(101, 0, 1, E.COURSE_TYPE_PRACTICE, ROOM_P)
sex_class_handle.set_temp_class(_pending_time.date().toordinal(), 1, ROOM_P, 70, must_attend=[])
move_to(101, SCENE_DORM)
set_time(_pending_time)
_moves = []
_orig_move = sm_default.general_movement_module
sm_default.general_movement_module = lambda cid, target: _moves.append(list(target))
constant.handle_state_machine_data[SM.MOVE_TO_CLASS_ROOM](101)
sm_default.general_movement_module = _orig_move
check("课表有残留的教师：去自己下一节授课的教室，不被带去实操教室", _moves == [classroom_path(ROOM1)], _moves)
schedule_handle.clear_selected_course(101, 0, 1)
clear_schedules()

section("Plan 25 §3.7：点名必修的成年学生岗")
make_character(301, "成年学生", 152)
prepare_ai(301)
schedule_handle.set_class_cell(ROOM1, 0, 1, 45, 101)
schedule_handle.set_selected_course(301, 0, 1, E.COURSE_TYPE_THEORY, ROOM1)
sex_class_handle.set_temp_class(_pending_time.date().toordinal(), 1, ROOM_P, 70, must_attend=[301])
move_to(301, SCENE_DORM)
check("成年必修生：开课前 8 分钟动身去实操教室", class_ai.get_next_sex_class(301, _pending_time)[0] is not None and dispatch(301, _pending_time) == SM.MOVE_TO_CLASS_ROOM)
set_time(period_time(1))
_course = schedule_handle.get_now_course(301)
check("成年必修生：本节的课被覆盖成临时课的教室", _course is not None and _course["classroom"] == ROOM_P and _course["teacher_id"] == 0, _course)
remove_character(301)
clear_schedules()

section("Plan 26 §3.8：未开放的场所、条件不符的兴趣课交回既有 AI")
set_time(period_time(0))
pool = _("游泳池")
pool_open_cid = game_config.config_facility_open_name_to_cid[pool]
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_PE, pool)
student.entertainment.entertainment_type = [E.ENTERTAINMENT_FREE_PLAY] * 3
move_to(201, SCENE_DORM)
cache.rhodes_island.facility_open[pool_open_cid] = False
check("体育课排在未解锁的游泳池：在 / 不在上课地点同为 0", handle_premise.handle_premise("self_in_course_place", 201) == 0
      and handle_premise.handle_premise("self_not_in_course_place", 201) == 0)
check("整条链：没有上课行命中，交回娱乐链（去育儿室），不再走到门口空转", dispatch(201) == SM.MOVE_TO_NURSERY)
cache.rhodes_island.facility_open[pool_open_cid] = True
move_to(201, SCENE_DORM)
check("解锁后恢复：715 去游泳池", dispatch(201) == SM.EDUCATION_MOVE_TO_COURSE_PLACE)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTEREST, E.ENTERTAINMENT_PLAY_HOUSE)
student.talent[103] = 0
student.talent[104] = 1
set_time(period_time(0))
check("少女排着过家家兴趣课（need 限幼女 / 萝莉）：上课地点解析不出", class_ai.get_course_place_now_or_upcoming(201) == [])
move_to(201, SCENE_DORM)
check("整条链：不派 715 / 716", dispatch(201) not in (SM.EDUCATION_MOVE_TO_COURSE_PLACE, SM.EDUCATION_DO_COURSE))
student.talent[104] = 0
student.talent[103] = 1
set_time(period_time(0))
check("回到萝莉：照常解析", bool(class_ai.get_course_place_now_or_upcoming(201)))
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()

section("Plan 26 §3.5：待赴的那节被玩家提前开讲、人已在教室 → 直接 JOIN（722）")
today = DEFAULT_TIME.date().toordinal()
sex_class_handle.set_temp_class(today, 1, ROOM_P, 70, must_attend=[201])
_early = period_time(1) - datetime.timedelta(minutes=5)
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
set_time(_early)
check("开讲前：SEX_PENDING 原地等", class_ai.get_course_stage(201) == E.COURSE_STAGE_SEX_PENDING)
sex_class_handle.start_sex_class(70, [])
cache.sex_class_mode = True
cache.group_sex_mode = True
pl.sp_flag.is_h = True
set_time(_early)
check("玩家提前开讲了那节：人已在教室 → JOIN", class_ai.get_course_stage(201) == E.COURSE_STAGE_JOIN_SEX_CLASS)
_attend = growth_handle.get_child_growth(201).attend_class_count
sm = dispatch(201, _early)
check("整条链：派 722 入课并补记出勤", sm == SM.EDUCATION_JOIN_SEX_CLASS and student.sp_flag.is_h and growth_handle.get_child_growth(201).attend_class_count == _attend + 1, sm)
student.sp_flag.is_h = False
student.sp_flag.see_pl_h = False
move_to(201, SCENE_DORM)
set_time(_early)
check("人还没到教室：仍是 SEX_PENDING，先过去", class_ai.get_course_stage(201) == E.COURSE_STAGE_SEX_PENDING)

section("Plan 26 §3.3：课堂模式下受邀到场走 515 → 722，普通群交走 505 → 96")
_T505, _T515 = "default505", "default515"
""" 构建时 target 的 cid 会带上所在文件夹名（buildconfig：path_list[-2] + cid），target.csv 在 data/target/default 下 """
check("505 挂 sex_class_mode_off、515 挂 sex_class_mode_on 且指向 722", "sex_class_mode_off" in game_config.config_target_premise_data.get(_T505, set())
      and "sex_class_mode_on" in game_config.config_target_premise_data.get(_T515, set()) and game_config.config_target[_T515].state_machine_id == SM.EDUCATION_JOIN_SEX_CLASS)
move_to(201, classroom_path(ROOM_P))
student.sp_flag.go_to_join_group_sex = True
sm = dispatch(201, _early)
check("受邀的学生走到玩家身边 → 722 入课、清掉前往标记", sm == SM.EDUCATION_JOIN_SEX_CLASS and student.sp_flag.is_h and not student.sp_flag.go_to_join_group_sex, sm)
student.sp_flag.is_h = False
student.sp_flag.see_pl_h = False
move_to(102, classroom_path(ROOM_P))
prepare_ai(102)
mother.sp_flag.go_to_join_group_sex = True
sm = dispatch(102, _early)
check("受邀的非学生干员到场 → 722 判不过门槛，原地收场、不进 H", sm == SM.EDUCATION_JOIN_SEX_CLASS and not mother.sp_flag.is_h and not mother.sp_flag.go_to_join_group_sex, sm)
pl.sp_flag.is_h = False
sex_class_handle.end_sex_class()
cache.sex_class_mode = False
mother.sp_flag.go_to_join_group_sex = True
sm = dispatch(102, _early)
check("普通群交（不是课堂）→ 505 → 96 加入群交", sm == 96, sm)
mother.sp_flag.go_to_join_group_sex = False
mother.sp_flag.is_h = False
cache.group_sex_mode = False
move_to(0, SCENE_DORM)
move_to(102, SCENE_EDU_ENTRY)
move_to(201, SCENE_DORM)
clear_schedules()

section("Plan 26 L7：母亲睡着时幼女的见学回落自由玩耍，公务事件的「母亲可见学」不受影响")
set_time(period_time(0))
child.entertainment.entertainment_type = [0, 0, 0]
move_to(202, SCENE_DORM)
check("母亲醒着：去找母亲", class_ai.judge_follow_mother_state_machine(202) == SM.EDUCATION_MOVE_TO_MOTHER)
mother.sp_flag.sleep = True
check("母亲要睡觉：回落育儿室自由玩耍", class_ai.judge_follow_mother_state_machine(202) == SM.ENTERTAIN_FREE_PLAY and class_ai.judge_mother_followable(202) == -1)
check("公务事件前提 self_mother_available 照旧成立（事件在跨天时派发，那时母亲多半睡着）", class_ai.judge_mother_available(202) == 102
      and handle_premise.handle_premise("self_mother_available", 202) == 1)
mother.sp_flag.sleep = False
mother.behavior.behavior_id = constant.Behavior.SLEEP
check("没挂要睡觉标记、但行为是睡觉（吃药 / 爆睡）也算", class_ai.judge_mother_followable(202) == -1)
mother.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
check("醒来后恢复", class_ai.judge_mother_followable(202) == 102)
class_ai.clear_follow_mother_flag(202)

section("Plan 27 §3.3：个人课表指向的教室这一节已停课，视为没课")
clear_schedules()
set_time(period_time(0))
prepare_ai(201)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
student.entertainment.entertainment_type = [E.ENTERTAINMENT_FREE_PLAY] * 3
move_to(201, classroom_path(ROOM1))
check("全局课表那一格空着：当前课程为 None、上课状态 NONE", schedule_handle.get_now_course(201) is None and class_ai.get_course_stage(201) == E.COURSE_STAGE_NONE)
_attend = growth_handle.get_child_growth(201).attend_class_count
sm = dispatch(201)
check("整条链：不派 713 自习，交回娱乐链（日程排了自由玩耍 → 去育儿室），也不记出勤", sm == SM.MOVE_TO_NURSERY and growth_handle.get_child_growth(201).attend_class_count == _attend, sm)
set_time(period_time(0) - datetime.timedelta(minutes=15))
check("不会为一节已停的课提前动身（到岗时间不算 UPCOMING）", class_ai.get_course_stage(201) == E.COURSE_STAGE_NONE)
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, -1)
check("格子在、只是没排教师：仍是一节课 → ATTEND（到了教室降级自习并计出勤）", class_ai.get_course_stage(201) == E.COURSE_STAGE_ATTEND)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
sex_class_handle.set_temp_class(DEFAULT_TIME.date().toordinal(), 0, ROOM_P, 70, must_attend=[201])
check("被点名必修到每周课表空着的实践教室：覆盖层给出格子，照样 ATTEND 并指向那间教室", class_ai.get_course_stage(201) == E.COURSE_STAGE_ATTEND
      and schedule_handle.get_now_course(201)["classroom"] == ROOM_P)
cache.rhodes_island.temp_sex_class = {}
schedule_handle.set_selected_course(201, 0, 1, E.COURSE_TYPE_PRACTICE, ROOM_P)
sex_class_handle.set_temp_class(DEFAULT_TIME.date().toordinal(), 1, ROOM_P, 70, must_attend=[])
set_time(period_time(1) - datetime.timedelta(minutes=8))
check("预约在每周课表空着的实践教室、这一节选修了它：照样 SEX_PENDING（选修读的是个人课表本身）", class_ai.get_course_stage(201) == E.COURSE_STAGE_SEX_PENDING)
set_time(period_time(1))
check("开课那一刻：覆盖层给出格子，照样 ATTEND", class_ai.get_course_stage(201) == E.COURSE_STAGE_ATTEND)
schedule_handle.clear_selected_course(201, 0, 0)
schedule_handle.clear_selected_course(201, 0, 1)
clear_schedules()

section("Plan 27 §3.2：自习的去处只挑已开放的理论教室")
LOCKED_THEORY = [_("理论教室二"), _("理论教室三"), _("理论教室四"), _("理论教室五"), _("理论教室六")]
for _room in LOCKED_THEORY:
    cache.rhodes_island.facility_open[game_config.config_facility_open_name_to_cid[_room]] = False
set_time(period_time(1) + datetime.timedelta(minutes=15))
move_to(201, SCENE_DORM)
_moves = []
sm_default.general_movement_module = lambda cid, target: _moves.append(list(target))
for _seed in range(12):
    random.seed(_seed)
    constant.handle_state_machine_data[SM.MOVE_TO_CLASS_ROOM](201)
check("只开了理论教室一：12 个种子下没课学生的 561 回落都去理论教室一（此前在全部 6 间里随机，会走向锁着的教室）",
      len(_moves) == 12 and all(one == classroom_path(ROOM1) for one in _moves), [scene_str(one) for one in _moves])
open_all_classroom()
_moves.clear()
for _seed in range(12):
    random.seed(_seed)
    constant.handle_state_machine_data[SM.MOVE_TO_CLASS_ROOM](201)
sm_default.general_movement_module = _orig_move
random.seed()
check("全开时回落在已开放的 6 间里随机", len({scene_str(one) for one in _moves}) > 1
      and all(cache.scene_data[scene_str(one)].scene_name in schedule_handle.get_classroom_list(E.COURSE_TYPE_THEORY) for one in _moves),
      [scene_str(one) for one in _moves])

section("Plan 27 §3.7：当场爆睡（行为是睡觉、没挂要睡觉标记）的学生不被拉去听课")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
student.sp_flag.sleep = False
student.behavior.behavior_id = constant.Behavior.SLEEP
student.behavior.duration = 120
check("行为是睡觉：判为不可拉", not class_ai.judge_student_pullable(201))
constant.handle_state_machine_data[SM.WORK_TEACH](101)
check("教师开讲（303）：她继续睡，不被改成听课", student.behavior.behavior_id == constant.Behavior.SLEEP, student.behavior.behavior_id)
check("醒着的照旧被拉进听课", teach_pull(201))
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()

finish()
