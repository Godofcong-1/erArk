# -*- coding: UTF-8 -*-
"""class_ai：两道闸、派课、见学回落链、预到岗"""
from _bootstrap import *  # noqa: F401,F403

open_all_classroom()
clear_schedules()
ROOM1 = _("理论教室一")
ROOM_P = _("实践教室一")
teacher = make_character(101, "教师甲", 151, position=classroom_path(ROOM1))
mother = make_character(102, "母亲", 21)
student = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102)
child = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102)

section("翘课概率表")
_orig_sum = class_ai.get_negative_status_level_sum
for level_sum, rate in ((0, 0.0), (3, 0.0), (4, 0.10), (7, 0.10), (8, 0.25), (12, 0.45), (15, 0.45), (16, 0.70), (32, 0.70)):
    class_ai.get_negative_status_level_sum = lambda cid, s=level_sum: s
    check(f"等级和 {level_sum} → 概率 {rate}", abs(class_ai.get_skip_class_rate(201) - rate) < 1e-9, class_ai.get_skip_class_rate(201))
class_ai.get_negative_status_level_sum = _orig_sum
check("等级和按状态等级累加", class_ai.get_negative_status_level_sum(201) == 0)

section("教师可用性")
check("-1 不可用", not class_ai.judge_teacher_available(-1))
check("不存在的角色不可用", not class_ai.judge_teacher_available(999))
check("正常教师可用", class_ai.judge_teacher_available(101))
teacher.sp_flag.is_h = True
check("H 中不可用", not class_ai.judge_teacher_available(101))
teacher.sp_flag.is_h = False
teacher.sp_flag.imprisonment = True
check("监禁中不可用", not class_ai.judge_teacher_available(101))
teacher.sp_flag.imprisonment = False
teacher.sp_flag.field_commission = True
check("外勤中不可用", not class_ai.judge_teacher_available(101))
teacher.sp_flag.field_commission = False
teacher.dead = True
check("死亡不可用", not class_ai.judge_teacher_available(101))
teacher.dead = False

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

section("派课：教室课")
set_time(period_time(0))
check("没排课不接管", class_ai.judge_class_state_machine(201) == 0)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
check("人不在教室 → 移动到教室", class_ai.judge_class_state_machine(201) == constant.StateMachine.MOVE_TO_CLASS_ROOM)
move_to(201, classroom_path(ROOM1))
check("到了教室、教师可用 → 听课", class_ai.judge_class_state_machine(201) == constant.StateMachine.WORK_ATTENT_CLASS)
teacher.sp_flag.is_h = True
check("教师不可用 → 自习", class_ai.judge_class_state_machine(201) == constant.StateMachine.EDUCATION_SELF_STUDY)
teacher.sp_flag.is_h = False
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, -1)
check("课表上没排教师 → 自习", class_ai.judge_class_state_machine(201) == constant.StateMachine.EDUCATION_SELF_STUDY)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)

section("两道闸")
student.hit_point = 10
check("体力 < 30% → 休息", class_ai.judge_class_state_machine(201) == constant.StateMachine.REST)
check("体力缺课记了一节", cache.character_data[201].child_growth.absent_count == 1)
check("体力缺课不置翘课 flag", not cache.character_data[201].child_growth.skip_class_flag)
student.hit_point = 100
cache.character_data[201].child_growth.skip_class_flag = True
check("翘课 flag 挂着 → 继续翘", class_ai.judge_class_state_machine(201) == constant.StateMachine.EDUCATION_SKIP_CLASS)
cache.character_data[201].child_growth.skip_class_flag = False
_orig_rate = class_ai.get_skip_class_rate
_orig_random = random.random
class_ai.get_skip_class_rate = lambda cid: 0.5
random.random = lambda: 0.1
check("掷中翘课概率 → 翘课", class_ai.judge_class_state_machine(201) == constant.StateMachine.EDUCATION_SKIP_CLASS)
random.random = lambda: 0.9
check("没掷中 → 照常上课", class_ai.judge_class_state_machine(201) == constant.StateMachine.WORK_ATTENT_CLASS)
class_ai.get_skip_class_rate = _orig_rate
random.random = _orig_random

section("必修实操课豁免")
today = cache.game_time.date().toordinal()
sex_class_handle.set_temp_class(today, 0, ROOM_P, 70, must_attend=[201])
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
check("必修判定成立", class_ai.judge_must_attend_sex_class(201))
check("非必修的人不成立", not class_ai.judge_must_attend_sex_class(202))
student.hit_point = 10
absent_before = cache.character_data[201].child_growth.absent_count
sm = class_ai.judge_class_state_machine(201)
check("必修 + 体力不足：仍去教室、不记缺课", sm != constant.StateMachine.REST and cache.character_data[201].child_growth.absent_count == absent_before, sm)
student.hit_point = 100
class_ai.get_skip_class_rate = lambda cid: 1.0
random.random = lambda: 0.0
check("必修 + 心情糟糕：不翘课", class_ai.judge_class_state_machine(201) != constant.StateMachine.EDUCATION_SKIP_CLASS)
class_ai.get_skip_class_rate = _orig_rate
random.random = _orig_random
cache.rhodes_island.temp_sex_class = {}
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)

section("派课：个人式课型")
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_PE, _("木桩房"))
check("体育课：人不在场地 → 移动", class_ai.judge_class_state_machine(201) == constant.StateMachine.EDUCATION_MOVE_TO_COURSE_PLACE)
pe_place = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
move_to(201, pe_place)
check("体育课：到场 → 执行该课行为", class_ai.judge_class_state_machine(201) == constant.StateMachine.EDUCATION_DO_COURSE)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_INTEREST, 99999)
check("地点解析不出 → 交回既有 AI", class_ai.judge_class_state_machine(201) == 0)
schedule_handle.clear_selected_course(201, 0, 0)

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
check("幼女在节次内没课 → 该见学", class_ai.judge_should_follow_mother(202))
# 2026-09-10 §9.2.9：该时段明确排了别的活动且已写进槽位 → 不见学，交给娱乐链去做那个活动
_tpl = schedule_template_handle.create_template("幼女白天")
schedule_template_handle.set_template_slot(_tpl, 0, education_constant.ENTERTAINMENT_FREE_PLAY)
schedule_template_handle.apply_template(202, _tpl)
schedule_template_handle.apply_schedule_for_child(202)
check("幼女上午明确排了自由玩耍且已写入 → 不见学", not class_ai.judge_should_follow_mother(202) and child.entertainment.entertainment_type[0] == education_constant.ENTERTAINMENT_FREE_PLAY)
schedule_template_handle.set_template_slot(_tpl, 0, education_constant.ENTERTAINMENT_FOLLOW_MOTHER)
schedule_template_handle.apply_schedule_for_child(202)
check("幼女上午排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(202))
schedule_template_handle.set_template_slot(_tpl, 0, education_constant.ENTERTAINMENT_FREE_PLAY)
child.entertainment.entertainment_type[0] = education_constant.ENTERTAINMENT_PLAY_HOUSE
check("模板排了活动但没写进槽位（退回自由选择）→ 仍默认见学", class_ai.judge_should_follow_mother(202))
schedule_template_handle.set_template_slot(_tpl, 0, 0)
check("时段为自由选择 → 默认见学", class_ai.judge_should_follow_mother(202))
schedule_template_handle.apply_template(202, 0)
child.entertainment.entertainment_type = [0, 0, 0]
check("萝莉不见学", not class_ai.judge_should_follow_mother(201))
schedule_handle.set_selected_course(202, 0, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
check("幼女本节有课 → 不见学", not class_ai.judge_should_follow_mother(202))
schedule_handle.clear_selected_course(202, 0, 0)
set_time(DEFAULT_TIME.replace(hour=19, minute=30))
cache.character_data[202].entertainment.entertainment_type = [0, 0, education_constant.ENTERTAINMENT_FOLLOW_MOTHER]
check("晚上日程排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(202))
cache.character_data[202].entertainment.entertainment_type = [0, 0, 0]
check("晚上日程没排 → 不见学", not class_ai.judge_should_follow_mother(202))

section("见学：萝莉按日程可见学（2026-09-09 放宽）")
student.entertainment.entertainment_type = [0, 0, education_constant.ENTERTAINMENT_FOLLOW_MOTHER]
check("萝莉晚上日程排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(201))
student.entertainment.entertainment_type = [0, 0, 0]
check("萝莉晚上日程没排 → 不见学", not class_ai.judge_should_follow_mother(201))
set_time(period_time(0))
student.entertainment.entertainment_type = [education_constant.ENTERTAINMENT_FOLLOW_MOTHER, 0, 0]
check("萝莉节次内没课、上午日程排了跟随母亲 → 见学", class_ai.judge_should_follow_mother(201))
schedule_handle.set_selected_course(201, cache.game_time.weekday(), 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
check("萝莉本节有课 → 有课优先，不见学", not class_ai.judge_should_follow_mother(201))
schedule_handle.clear_selected_course(201, cache.game_time.weekday(), 0)
student.entertainment.entertainment_type = [0, 0, 0]
check("萝莉节次内没课但日程没排 → 自由行动（口径 10 的默认不变）", not class_ai.judge_should_follow_mother(201))
girl = make_character(203, "女儿C", 152, daughter=True, stage=104, mother_id=102, born_days=500)
girl.entertainment.entertainment_type = [education_constant.ENTERTAINMENT_FOLLOW_MOTHER] * 3
check("少女日程排了跟随母亲也不见学", not class_ai.judge_should_follow_mother(203))
set_time(period_time(0))
move_to(102, SCENE_EDU_ENTRY)
move_to(202, SCENE_DORM)
check("母亲有效、不同场景 → 移动到母亲身边", class_ai.judge_follow_mother_state_machine(202) == constant.StateMachine.EDUCATION_MOVE_TO_MOTHER)
move_to(202, SCENE_EDU_ENTRY)
check("同场景 → 见学", class_ai.judge_follow_mother_state_machine(202) == constant.StateMachine.EDUCATION_FOLLOW_MOTHER)
mother.sp_flag.is_h = True
check("母亲无效 → 回落自由玩耍而不是交回 AI", class_ai.judge_follow_mother_state_machine(202) == constant.StateMachine.ENTERTAIN_FREE_PLAY)
mother.sp_flag.is_h = False
growth_handle.get_child_growth(202).follow_mother_flag = True
check("见学标记读口", class_ai.judge_in_follow_mother(202) and not class_ai.judge_in_follow_mother(201) and not class_ai.judge_in_follow_mother(999))
check("不该见学时顺手清标记", (class_ai.judge_follow_mother_state_machine(201), class_ai.judge_in_follow_mother(202))[0] == 0)
class_ai.clear_follow_mother_flag(202)
check("清标记", not class_ai.judge_in_follow_mother(202))
class_ai.clear_follow_mother_flag(999)
check("对不存在的角色清标记不报错", True)

section("没课节次的去向（2026-09-10 §9.2.9）")
from Script.Design import handle_npc_ai, clothing

set_time(period_time(0))
check("周一上午：学生岗算娱乐时间、教师岗与普通岗不算", handle_premise.handle_all_entertainment_time(201) > 0 and handle_premise.handle_all_entertainment_time(101) == 0
      and handle_premise.handle_all_entertainment_time(102) == 0)
check("非全娱乐时间前提与之互补", handle_premise.handle_not_all_entertainment_time(201) == 0 and handle_premise.handle_not_all_entertainment_time(102) > 0)
set_time(period_time(0, DEFAULT_TIME.date() + datetime.timedelta(days=6)))
check("周日上午：谁都算娱乐时间", handle_premise.handle_all_entertainment_time(201) > 0 and handle_premise.handle_all_entertainment_time(102) > 0)


def prepare_ai(cid: int) -> None:
    """
    把最小 fixture 补成能跑通完整 AI 链的样子：已起床、穿好衣服、异常位刷新
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    无
    功能: 没起床会先被「起床」目标（target 205）接管；全裸则 normal_all 不成立，娱乐的自动 AI 根本不跑
    """
    cd = cache.character_data[cid]
    cd.action_info.wake_time = cache.game_time
    clothing.get_npc_cloth(cid)
    handle_premise.refresh_unnormal_flag(cid)


def dispatch(cid: int) -> int:
    """
    跑一遍 find_character_target，记下它派发的状态机id
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    int -- 派发的状态机id，没派发则为 0
    功能: 每次先把上一轮留下的移动 / 行为清掉，否则会被「继续移动」目标接管
    """
    cd = cache.character_data[cid]
    cd.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    cd.behavior.duration = 0
    cd.behavior.move_target = []
    cd.behavior.move_final_target = []
    cd.state = constant.CharacterStatus.STATUS_ARDER
    hit = []
    origin = dict(constant.handle_state_machine_data)
    for sid, func in origin.items():
        constant.handle_state_machine_data[sid] = (lambda s, f: (lambda c: (hit.append(s), f(c))[1]))(sid, func)
    try:
        set_time(period_time(0))
        handle_npc_ai.find_character_target(cid, cache.game_time)
    finally:
        constant.handle_state_machine_data.clear()
        constant.handle_state_machine_data.update(origin)
    return hit[0] if hit else 0


set_time(period_time(0))
for _cid in (201, 202):
    prepare_ai(_cid)
clear_schedules()
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [education_constant.ENTERTAINMENT_FREE_PLAY, 0, 0]
check("萝莉周一上午没课、日程排了自由玩耍 → 去育儿室，而不是被工作链送进教室", dispatch(201) == constant.StateMachine.MOVE_TO_NURSERY)
move_to(201, SCENE_NURSERY)
check("到了育儿室 → 自由玩耍", dispatch(201) == constant.StateMachine.ENTERTAIN_FREE_PLAY)
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [education_constant.ENTERTAINMENT_SELF_STUDY, 0, 0]
check("排了上课（无课时自习）、人在宿舍 → 去教室", dispatch(201) == constant.StateMachine.MOVE_TO_CLASS_ROOM)
move_to(201, classroom_path(ROOM1))
check("到了教室 → 自习", dispatch(201) == constant.StateMachine.EDUCATION_SELF_STUDY)
move_to(201, SCENE_DORM)
student.entertainment.entertainment_type = [0, 0, 0]
move_to(202, SCENE_DORM)
move_to(102, SCENE_EDU_ENTRY)
_tpl2 = schedule_template_handle.create_template("幼女白天2")
schedule_template_handle.set_template_slot(_tpl2, 0, education_constant.ENTERTAINMENT_FREE_PLAY)
schedule_template_handle.apply_template(202, _tpl2)
schedule_template_handle.apply_schedule_for_child(202)
check("幼女周一上午没课、日程排了自由玩耍 → 去育儿室而不是见学", dispatch(202) == constant.StateMachine.MOVE_TO_NURSERY)
schedule_template_handle.apply_template(202, 0)
child.entertainment.entertainment_type = [0, 0, 0]
check("幼女时段为自由选择 → 默认见学（移动到母亲身边）", dispatch(202) == constant.StateMachine.EDUCATION_MOVE_TO_MOTHER)
set_time(period_time(0))

section("预到岗")
clear_schedules()
today = cache.game_time.date().toordinal()
sex_class_handle.set_temp_class(today, 1, ROOM_P, 70, must_attend=[201])
set_time(period_time(1) - datetime.timedelta(minutes=8))
move_to(201, SCENE_DORM)
temp_class, classroom = class_ai.get_next_sex_class(201, cache.game_time)
check("距开始 8 分钟：必修者要动身", temp_class is not None and classroom == ROOM_P)
check("预到岗返回移动到教室", class_ai.judge_pre_arrive_sex_class(201) == constant.StateMachine.MOVE_TO_CLASS_ROOM)
set_time(period_time(1) - datetime.timedelta(minutes=15))
check("距开始 15 分钟：还不动身", class_ai.get_next_sex_class(201, cache.game_time)[0] is None)
set_time(period_time(1) - datetime.timedelta(minutes=8))
check("非必修且没选修的人不动身", class_ai.get_next_sex_class(202, cache.game_time)[0] is None)
schedule_handle.set_selected_course(202, cache.game_time.weekday(), 1, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
check("选修了这间教室的人也动身", class_ai.get_next_sex_class(202, cache.game_time)[0] is not None)
move_to(201, classroom_path(ROOM_P))
check("已在教室则不再移动", class_ai.judge_pre_arrive_sex_class(201) == 0)
check("预到岗不记缺课", cache.character_data[201].child_growth.absent_count == 1)

finish()
