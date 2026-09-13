# -*- coding: UTF-8 -*-
"""前提与结算 token：CVP Course / CourseType / CourseShowOff / Growth、CVE Growth、实操课与岗位前提、女儿前提"""
from _bootstrap import *  # noqa: F401,F403

open_all_classroom()
clear_schedules()
ROOM1 = _("理论教室一")
ROOM_P = _("实践教室一")
teacher = make_character(101, "教师甲", 151, position=classroom_path(ROOM1))
mother = make_character(102, "母亲", 0)
student = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102, born_days=300, position=classroom_path(ROOM1))
child = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102, born_days=120)
adult = make_character(301, "成年干员", 21)
P = constant_promise.Premise
E = education_constant
HP = handle_premise.handle_premise

section("注册")
for name in ("work_is_teacher", "t_work_is_teacher", "work_is_student", "t_work_is_student", "have_intern_student", "not_have_intern_student",
             "self_is_player_daughter", "self_not_player_daughter", "target_is_player_daughter", "target_not_player_daughter",
             P.SELF_HAVE_SIBLING_CHILD, P.SELF_HAVE_CLASSMATE, P.SELF_FOLLOW_MOTHER,
             "sex_class_mode_on", "sex_class_mode_off", "sex_class_end_early", "sex_class_end_on_time", "sex_class_end_late",
             "in_sex_class_place", "scene_have_sex_class_student", "self_in_sex_class", "sex_class_reserved", "sex_class_impromptu",
             "self_sex_class_must_attend", "self_sex_class_elective", "in_practice_room", "in_auditorium", "in_class_room",
             "growth_stop_1", "growth_stop_0",
             # Plan 24：教师 / 学生并入工作链的 18 个前提
             "teacher_have_class_now", "teacher_have_upcoming_class", "teacher_no_class_duty", "teacher_in_duty_classroom", "teacher_not_in_duty_classroom",
             "self_sex_class_pending", "self_in_pending_sex_class_room", "self_not_in_pending_sex_class_room",
             "self_course_absent_by_hp", "self_course_skip", "self_course_attend", "self_course_upcoming",
             "self_course_is_classroom", "self_course_is_personal", "self_in_course_place", "self_not_in_course_place",
             "self_course_teacher_available", "self_course_teacher_unavailable"):
    check(f"前提 {name} 已注册", name in constant.handle_premise_data)

section("岗位与女儿前提")
check("work_is_teacher / student", HP("work_is_teacher", 101) == 1 and HP("work_is_teacher", 201) == 0 and HP("work_is_student", 201) == 1 and HP("work_is_student", 101) == 0)
pl.target_character_id = 201
check("t_work_is_student / t_work_is_teacher", HP("t_work_is_student", 0) == 1 and HP("t_work_is_teacher", 0) == 0)
check("女儿前提", HP("self_is_player_daughter", 201) == 1 and HP("self_is_player_daughter", 301) == 0 and HP("self_not_player_daughter", 301) == 1
      and HP("target_is_player_daughter", 0) == 1 and HP("target_not_player_daughter", 0) == 0)
check("同胞前提", HP(P.SELF_HAVE_SIBLING_CHILD, 201) == 1 and HP(P.SELF_HAVE_SIBLING_CHILD, 301) == 0)
# 同学只算每周课表上确有的课（Plan 30 §3.6），这一格要在全局课表上排上；下一段会重排这一格
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_selected_course(202, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
check("同学前提", HP(P.SELF_HAVE_CLASSMATE, 201) == 1)
schedule_handle.clear_selected_course(202, 0, 0)
check("没有同学", HP(P.SELF_HAVE_CLASSMATE, 201) == 0)
growth_handle.get_child_growth(202).follow_mother_flag = True
check("见学前提", HP(P.SELF_FOLLOW_MOTHER, 202) == 1 and HP(P.SELF_FOLLOW_MOTHER, 201) == 0)
growth_handle.get_child_growth(202).follow_mother_flag = False
student.talent[28] = 1
check("成长停滞前提", HP("growth_stop_1", 201) == 1 and HP("growth_stop_0", 201) == 0)
student.talent[28] = 0

section("师生工作链前提只认本岗（Plan 24）")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
check("教师前提：本节有课、人在教室", HP("teacher_have_class_now", 101) == 1 and HP("teacher_in_duty_classroom", 101) == 1
      and HP("teacher_not_in_duty_classroom", 101) == 0 and HP("teacher_no_class_duty", 101) == 0)
check("教师前提对学生岗与普通岗为 0", HP("teacher_have_class_now", 201) == 0 and HP("teacher_in_duty_classroom", 201) == 0
      and HP("teacher_no_class_duty", 201) == 0 and HP("teacher_no_class_duty", 301) == 0)
check("学生前提：本节照常上教室课、人在教室、教师可用", HP("self_course_attend", 201) == 1 and HP("self_course_is_classroom", 201) == 1
      and HP("self_in_course_place", 201) == 1 and HP("self_course_teacher_available", 201) == 1 and HP("self_course_teacher_unavailable", 201) == 0)
check("学生前提对教师岗与普通岗为 0", HP("self_course_attend", 101) == 0 and HP("self_not_in_course_place", 101) == 0
      and HP("self_course_upcoming", 301) == 0 and HP("self_course_teacher_unavailable", 301) == 0)
# 201 的这节理论课留着：下面的 Course 系列 CVP 沿用它（与上面「同学前提」一段留下的是同一格）
schedule_handle.clear_class_cell(ROOM1, 0, 0)

section("Course 系列 CVP")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 43, 101)
check("学生：Course|43 成立、Course|45 不成立", HP("CVP_A1_Course|43_G_0", 201) == 1 and HP("CVP_A1_Course|45_G_0", 201) == 0)
check("教师：按授课表取科目", HP("CVP_A1_Course|43_G_0", 101) == 1)
check("CourseType：学生是理论课", HP("CVP_A1_CourseType|0_E_1", 201) == 1 and HP("CVP_A1_CourseType|1_E_1", 201) == 0)
check("A2 视角：交互对象的课", HP("CVP_A2_Course|43_G_0", 0) == 1)
check("不在节次内不成立", (set_time(DEFAULT_TIME.replace(hour=13)), HP("CVP_A1_Course|43_G_0", 201))[1] == 0)
set_time(period_time(0))
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_PE, _("木桩房"))
check("体育课：没有科目，Course 恒不成立、CourseType|3 成立", HP("CVP_A1_Course|43_G_0", 201) == 0 and HP("CVP_A1_CourseType|3_E_1", 201) == 1)
intern_work = next(cid for cid in game_config.config_work_type if cid and game_config.config_work_type[cid].ability_id == 43 and not game_config.config_work_type[cid].tag)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTERN, intern_work)
check("实习课：科目取岗位的 ability_id", HP("CVP_A1_Course|43_G_0", 201) == 1 and HP("CVP_A1_CourseType|5_E_1", 201) == 1)
growth_handle.get_child_growth(201).show_off_ability = {45: 2}
check("CourseShowOff：待炫耀的科目", HP("CVP_A1_CourseShowOff|45_G_0", 201) == 1 and HP("CVP_A1_CourseShowOff|43_G_0", 201) == 0 and HP("CVP_A1_CourseShowOff|45_G_0", 301) == 0)
schedule_handle.clear_selected_course(201, 0, 0)

section("实操课优先于课表")
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
set_time(period_time(5))
sex_class_handle.start_sex_class(74)
check("玩家：Course|74 成立（正在进行的实操课）", HP("CVP_A1_Course|74_G_0", 0) == 1)
check("在场学生：Course|74 成立", HP("CVP_A1_Course|74_G_0", 201) == 1)
check("在别处的学生不成立", HP("CVP_A1_Course|74_G_0", 202) == 0)
sex_class_handle.end_sex_class()
check("当场开的课下课即交还课表：这一节里教师视角不再成立（第五轮）", HP("CVP_A1_Course|74_G_0", 0) == 0)
set_time(period_time(6))
check("过了这一节就不成立", HP("CVP_A1_Course|74_G_0", 0) == 0)
set_time(period_time(5))

section("Growth 系列 CVP / CVE")
g = growth_handle.get_child_growth(201)
g.attend_class_count = 8
g.absent_count = 2
check("Growth|0 出勤数 ≥ 8", HP("CVP_A1_Growth|0_GE_8", 201) == 1 and HP("CVP_A1_Growth|0_G_8", 201) == 0)
check("Growth|2 出勤率 80", HP("CVP_A1_Growth|2_E_80", 201) == 1)
check("Growth|7 没成绩单时为 -1", HP("CVP_A1_Growth|7_E_-1", 201) == 1 and HP("CVP_A1_Growth|7_E_0", 201) == 0)
check("没养成数据的干员：出勤率按 100", HP("CVP_A1_Growth|2_E_100", 301) == 1)
check("Growth 不会被当成攻略程度", HP("CVP_A1_Growth|0_GE_8", 201) == 1 and HP("CVP_A1_G_GE_8", 201) == 0)
g.report_card_flag = True
check("Growth|23 成绩单待查看：有待查看为 1（Plan 27）", HP("CVP_A1_Growth|23_E_1", 201) == 1)
g.report_card_flag = False
check("Growth|23：看过之后为 0，没有养成数据的干员也是 0", HP("CVP_A1_Growth|23_E_0", 201) == 1 and HP("CVP_A1_Growth|23_E_1", 201) == 0
      and HP("CVP_A1_Growth|23_E_0", 301) == 1)
pl.target_character_id = 201
change = game_type.CharacterStatusChange()
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|10", "G", "0.5"], change)
check("CVE Growth|10 +0.5", g.personality_point.get(0, 0.0) == 0.5)
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|10", "L", "1.5"], change)
check("CVE Growth|10 -1.5 → -1.0", g.personality_point.get(0, 0.0) == -1.0)
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|10", "E", "2.5"], change)
check("CVE Growth|10 E 2.5", g.personality_point.get(0, 0.0) == 2.5)
check("CVP Growth|10 读到 2.5", HP("CVP_A1_Growth|10_G_2", 201) == 1)
settle_behavior.handle_comprehensive_value_effect(201, ["A1", "Growth|20", "G", "3"], change)
check("A1 视角写自己的照料值", g.care_point == 3.0)

section("实操课前提")
cache.sex_class_mode = False
check("模式关：mode_off 成立", HP("sex_class_mode_off", 0) == 1 and HP("sex_class_mode_on", 0) == 0)
check("在实践教室：in_sex_class_place", HP("in_sex_class_place", 0) == 1)
check("场景里的学生没修过性技课：没有可参加的学生（口径 63 宽松版）", HP("scene_have_sex_class_student", 0) == 0)
schedule_handle.set_class_cell(ROOM_P, 3, 8, 74, -1)
schedule_handle.set_selected_course(201, 3, 8, E.COURSE_TYPE_PRACTICE, ROOM_P)
check("场景里有可参加的学生", HP("scene_have_sex_class_student", 0) == 1)
move_to(201, SCENE_DORM)
check("学生走了就不成立", HP("scene_have_sex_class_student", 0) == 0)
move_to(201, classroom_path(ROOM_P))
cache.rhodes_island.temp_sex_class = {}
today = cache.game_time.date().toordinal()
sex_class_handle.set_temp_class(today, 5, ROOM_P, 74, must_attend=[201])
now_class = sex_class_handle.start_sex_class(74)
cache.sex_class_mode = True
check("模式开：mode_on 成立", HP("sex_class_mode_on", 0) == 1)
check("预约的课：sex_class_reserved", HP("sex_class_reserved", 0) == 1 and HP("sex_class_impromptu", 0) == 0)
check("必修 / 选修", HP("self_sex_class_must_attend", 201) == 1 and HP("self_sex_class_elective", 201) == 0 and HP("self_sex_class_elective", 202) == 1)
student.sp_flag.is_h = True
check("自己在课中（在场且已进 H 状态）", HP("self_in_sex_class", 201) == 1 and HP("self_in_sex_class", 202) == 0)
student.sp_flag.is_h = False
check("没进 H 状态不算在课中", HP("self_in_sex_class", 201) == 0)
set_time(period_time(5) + datetime.timedelta(minutes=10))
check("下课三档：提前", HP("sex_class_end_early", 0) == 1 and HP("sex_class_end_on_time", 0) == 0)
set_time(period_time(5) + datetime.timedelta(minutes=44))
check("下课三档：按时", HP("sex_class_end_on_time", 0) == 1)
set_time(period_time(5) + datetime.timedelta(minutes=80))
check("下课三档：拖堂", HP("sex_class_end_late", 0) == 1)
sex_class_handle.end_sex_class()
cache.sex_class_mode = False
cache.rhodes_island.temp_sex_class = {}
set_time(period_time(5))
sex_class_handle.start_sex_class(70)
cache.sex_class_mode = True
check("当场开课：sex_class_impromptu", HP("sex_class_impromptu", 0) == 1 and HP("sex_class_reserved", 0) == 0)
sex_class_handle.end_sex_class()
cache.sex_class_mode = False

section("实习带教前提")
intern_place = None
schedule_handle.set_selected_course(201, cache.game_time.weekday(), 0, E.COURSE_TYPE_INTERN, intern_work)
set_time(period_time(0))
intern_place = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
mentor = make_character(103, "带教", intern_work, position=intern_place)
move_to(201, intern_place)
student.behavior.behavior_id = constant.Behavior.INTERN_CLASS
check("有学徒在跟岗：have_intern_student", HP("have_intern_student", 103) == 1 and HP("not_have_intern_student", 103) == 0)
move_to(201, SCENE_DORM)
check("学徒走了：not_have_intern_student", HP("have_intern_student", 103) == 0 and HP("not_have_intern_student", 103) == 1)

section("Plan 25：新前提、授课指令的前提只看所在场景、三类教室都算")
for name in ("self_course_join_sex_class", "in_education_classroom", "student_not_study_in_classroom"):
    check(f"前提 {name} 已注册", name in constant.handle_premise_data)
check("死前提 teacher_teaching_in_classroom 已删除", "teacher_teaching_in_classroom" not in constant.handle_premise_data)
move_to(0, SCENE_DORM)
check("在宿舍：不在教育区教室", HP("in_education_classroom", 0) == 0)
for room in (ROOM1, ROOM_P, schedule_handle.get_classroom_list(E.COURSE_TYPE_PUBLIC)[0]):
    move_to(0, classroom_path(room))
    check(f"在{room}：在教育区教室", HP("in_education_classroom", 0) == 1)
move_to(0, SCENE_EDU_ENTRY)
move_to(201, classroom_path(ROOM1))
move_to(202, SCENE_DORM)
student.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
check("玩家不在那间教室：别处有闲着的学生也不成立（原先扫全岛）", HP("student_not_study_in_classroom", 0) == 0)
move_to(0, classroom_path(ROOM1))
check("玩家所在的教室里有闲着的学生 → 成立", HP("student_not_study_in_classroom", 0) == 1)
student.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
check("她已经在听课 → 不成立", HP("student_not_study_in_classroom", 0) == 0)
student.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
student.sp_flag.sleep = True
check("她在睡觉 → 不成立", HP("student_not_study_in_classroom", 0) == 0)
student.sp_flag.sleep = False
student.behavior.behavior_id = constant.Behavior.SLEEP
check("她当场爆睡（行为是睡觉、没挂要睡觉标记）→ 不成立（Plan 27 §3.7）", HP("student_not_study_in_classroom", 0) == 0)
student.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
move_to(0, SCENE_DORM)

section("Plan 26 L6：t_baby_0 与检查成绩单挡婴儿")
check("前提 t_baby_0 已注册", "t_baby_0" in constant.handle_premise_data and P.T_BABY_0 == "t_baby_0")
baby = make_character(204, "婴儿", 0, daughter=True, stage=101, mother_id=102)
pl.target_character_id = 204
check("交互对象是婴儿：t_baby_0 = 0、t_baby_1 = 1", HP("t_baby_0", 0) == 0 and HP("t_baby_1", 0) == 1)
report_config = game_config.config_instruct[game_config.config_instruct_by_id["check_report_card"]]
report_tokens = [getattr(P, name) for name in report_config.premise_set.split("|")]
check("检查成绩单的前提对婴儿不成立", "T_BABY_0" in report_config.premise_set and not all(HP(token, 0) for token in report_tokens), report_config.premise_set)
pl.target_character_id = 201
check("对萝莉女儿成立", all(HP(token, 0) for token in report_tokens))
pl.target_character_id = 0
remove_character(204)

section("Plan 28 §3.2 / §3.7：上不成的个人式课视为没课；日程自习的 <课> 悬停")
from Script.UI.Panel import character_info_head  # noqa: E402

set_time(period_time(0))
student.talent[103] = 0
student.talent[104] = 1
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTEREST, E.ENTERTAINMENT_PLAY_HOUSE)
_ct_interest = "CVP_A1_CourseType|{0}_E_1".format(E.COURSE_TYPE_INTEREST)
student.hit_point = 10
check("少女排着过家家兴趣课：CVP CourseType 不成立，照常上课 / 体力缺课两个学生前提都为 0（此前都按有课判）", HP(_ct_interest, 201) == 0
      and HP("self_course_attend", 201) == 0 and HP("self_course_absent_by_hp", 201) == 0)
student.hit_point = 100
student.talent[104] = 0
student.talent[103] = 1
check("回到萝莉：CourseType 成立", HP(_ct_interest, 201) == 1)
schedule_handle.clear_selected_course(201, 0, 0)
student.behavior.behavior_id = constant.Behavior.SELF_STUDY
_self_study_tip = (False, _("自习中（日程安排，此刻没课）"))
check("本节没课的日程自习：<课> 悬停写「自习中」（此前写「上课中」）", character_info_head.get_now_class_tip(201) == _self_study_tip, character_info_head.get_now_class_tip(201))
set_time(DEFAULT_TIME.replace(hour=20))
check("节次外的日程自习（照旧 45 分钟）同样写「自习中」", character_info_head.get_now_class_tip(201) == _self_study_tip, character_info_head.get_now_class_tip(201))
set_time(period_time(0))
student.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
check("听课而此刻没课（玩家在节次外授课拉来的）仍写「上课中」", character_info_head.get_now_class_tip(201) == (False, _("上课中")), character_info_head.get_now_class_tip(201))
student.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY

section("Plan 30：self_have_any_course 只看学生岗的真课、CVP Growth|24、检查成绩单的对象（Q1）")
clear_schedules()
set_time(period_time(0))
student.work.work_type = 152
growth_handle.get_child_growth(201).selected_course = {}
schedule_handle.set_selected_course(201, 1, 2, E.COURSE_TYPE_THEORY, ROOM1)
check("个人课表只有一格已停课的教室课：self_have_any_course 不成立（此前课表非空即成立）", HP(P.SELF_HAVE_ANY_COURSE, 201) == 0)
schedule_handle.set_class_cell(ROOM1, 1, 2, 45, 101)
check("每周课表排上：成立", HP(P.SELF_HAVE_ANY_COURSE, 201) == 1)
student.work.work_type = 21
check("改了岗：课表还在也不成立", HP(P.SELF_HAVE_ANY_COURSE, 201) == 0)
student.work.work_type = 152
schedule_handle.clear_selected_course(201, 1, 2)
clear_schedules()
growth_handle.get_child_growth(201).skip_count = 3
check("CVP Growth|24 累计翘课数", HP("CVP_A1_Growth|24_GE_3", 201) == 1 and HP("CVP_A1_Growth|24_G_3", 201) == 0 and HP("CVP_A1_Growth|24_E_0", 301) == 1)
growth_handle.get_child_growth(201).skip_count = 0
check("前提 target_report_card_checkable 已注册、挂在 1036 的前提串末尾", "target_report_card_checkable" in constant.handle_premise_data
      and P.TARGET_REPORT_CARD_CHECKABLE == "target_report_card_checkable" and report_config.premise_set.split("|")[-1] == "TARGET_REPORT_CARD_CHECKABLE", report_config.premise_set)
report_tokens = [getattr(P, name) for name in report_config.premise_set.split("|")]
grown = make_character(206, "成年女儿", 21, daughter=True, stage=104, mother_id=102, born_days=500)
pl.target_character_id = 206
check("成年后不在学生岗的女儿：检查成绩单不成立（用户拍板）", not all(HP(token, 0) for token in report_tokens) and HP(P.TARGET_REPORT_CARD_CHECKABLE, 0) == 0)
growth_handle.get_child_growth(206).report_card_flag = True
check("她还有一份没看过的成绩单：成立（否则养成总览的待查看永远消不掉）", all(HP(token, 0) for token in report_tokens))
growth_handle.get_child_growth(206).report_card_flag = False
grown.work.work_type = 152
check("成年后仍在学生岗的女儿：成立", all(HP(token, 0) for token in report_tokens))
student.work.work_type = 21
pl.target_character_id = 201
check("改了岗的萝莉女儿：照旧成立（照出成绩单，Plan 29）", all(HP(token, 0) for token in report_tokens))
student.work.work_type = 152
other_student = make_character(302, "不是女儿的成年学生", 152)
pl.target_character_id = 302
check("不是女儿的学生岗角色：不成立（target_is_player_daughter 挡住，用户拍板维持）", not all(HP(token, 0) for token in report_tokens) and HP("target_is_player_daughter", 0) == 0)
pl.target_character_id = 0
remove_character(206)
remove_character(302)

section("Plan 31：六个新前提已注册；§3.14 L11 按课型查整张个人课表的五个前提")
_new_premise_list = (P.SELF_HAVE_THEORY_COURSE, P.SELF_HAVE_PRACTICE_COURSE, P.SELF_HAVE_PE_COURSE, P.SELF_HAVE_INTEREST_COURSE, P.SELF_HAVE_INTERN_COURSE,
                     P.SELF_BIRTHDAY_TODAY)
for name in _new_premise_list:
    check(f"L11 / L13 前提 {name} 已注册", name in constant.handle_premise_data)
clear_schedules()
set_time(period_time(0))
growth_handle.get_child_growth(201).selected_course = {}
_type_premise = {
    E.COURSE_TYPE_THEORY: P.SELF_HAVE_THEORY_COURSE,
    E.COURSE_TYPE_PRACTICE: P.SELF_HAVE_PRACTICE_COURSE,
    E.COURSE_TYPE_PE: P.SELF_HAVE_PE_COURSE,
    E.COURSE_TYPE_INTEREST: P.SELF_HAVE_INTEREST_COURSE,
    E.COURSE_TYPE_INTERN: P.SELF_HAVE_INTERN_COURSE,
}


def course_type_hit(cid: int) -> list:
    """
    取五个课型前提里对某角色成立的课型
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    list -- 成立的课型编号，升序
    """
    return sorted(course_type for course_type, premise_name in _type_premise.items() if HP(premise_name, cid))


check("L11 课表为空：五个课型前提都不成立", course_type_hit(201) == [], course_type_hit(201))
schedule_handle.set_class_cell(ROOM1, 1, 2, 45, 101)
schedule_handle.set_selected_course(201, 1, 2, E.COURSE_TYPE_THEORY, ROOM1)
check("L11 只排理论课：只有 self_have_theory_course 成立（此前点名体育 / 实习 / 兴趣 / 实践课的事件只挂 self_have_any_course，照样抽得到）",
      course_type_hit(201) == [E.COURSE_TYPE_THEORY], course_type_hit(201))
schedule_handle.set_class_cell(ROOM_P, 1, 3, 43, -1)
schedule_handle.set_selected_course(201, 1, 3, E.COURSE_TYPE_PRACTICE, ROOM_P)
schedule_handle.set_selected_course(201, 1, 4, E.COURSE_TYPE_PE, _("木桩房"))
schedule_handle.set_selected_course(201, 1, 5, E.COURSE_TYPE_INTEREST, E.ENTERTAINMENT_PLAY_HOUSE)
schedule_handle.set_selected_course(201, 1, 6, E.COURSE_TYPE_INTERN, intern_work)
check("L11 五种课型各排一格：五个前提都成立", course_type_hit(201) == sorted(_type_premise), course_type_hit(201))
schedule_handle.clear_class_cell(ROOM1, 1, 2)
check("L11 理论课那一格在每周课表上停了课：只有理论课前提不成立", course_type_hit(201) == sorted(set(_type_premise) - {E.COURSE_TYPE_THEORY}), course_type_hit(201))
student.work.work_type = 21
check("L11 改了岗：课表残留不算，五个都不成立", course_type_hit(201) == [], course_type_hit(201))
student.work.work_type = 152
check("L11 前提只读：没有养成数据的干员五个都不成立，也不被惰性创建养成数据", adult.child_growth is None and course_type_hit(301) == [] and adult.child_growth is None)
growth_handle.get_child_growth(201).selected_course = {}
clear_schedules()

section("Plan 31 §3.14 L13：self_birthday_today 读 pregnancy.born_time，2 月 29 日出生的平年按 2 月 28 日过")
_saved_born_time = student.pregnancy.born_time
student.pregnancy.born_time = datetime.datetime(2025, 9, 7, 6, 30)
set_time(datetime.datetime(2026, 9, 7, 0, 5))
check("L13 出生的月日与今天相同：成立", HP(P.SELF_BIRTHDAY_TODAY, 201) == 1)
set_time(datetime.datetime(2026, 9, 8, 0, 5))
check("L13 第二天：不成立（此前没有生日前提，通用 3「今天是{Name}的生日」任意一天都抽得到）", HP(P.SELF_BIRTHDAY_TODAY, 201) == 0)
student.pregnancy.born_time = datetime.datetime(2024, 2, 29, 12, 0)
_leap_birthday = []
for _now_time in (datetime.datetime(2027, 2, 28, 9, 0), datetime.datetime(2027, 3, 1, 9, 0), datetime.datetime(2028, 2, 28, 9, 0), datetime.datetime(2028, 2, 29, 9, 0)):
    set_time(_now_time)
    _leap_birthday.append(HP(P.SELF_BIRTHDAY_TODAY, 201))
check("L13 2 月 29 日出生：平年 2 月 28 日成立、3 月 1 日不成立；闰年 2 月 28 日不成立、2 月 29 日成立", _leap_birthday == [1, 0, 0, 1], _leap_birthday)
set_time(datetime.datetime(2027, 1, 1, 9, 0))
check("L13 born_time 还是缺省值（公元 1 年 1 月 1 日）的干员：1 月 1 日也不成立", adult.pregnancy.born_time.year == 1 and HP(P.SELF_BIRTHDAY_TODAY, 301) == 0)
student.pregnancy.born_time = _saved_born_time
set_time(period_time(0))

section("Plan 31 §3.4（M3）：教师能到岗的两个学生前提传本节教室（空气催眠只在人在教室时算能到岗，木头人一律来不了）")
clear_schedules()
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
move_to(101, classroom_path(ROOM1))


def teacher_premise_pair() -> tuple:
    """
    刷新教师 101 的异常位掩码后，取学生 201 的「教师能到岗 / 来不了」两个前提
    Keyword arguments:
    无
    Return arguments:
    tuple -- (self_course_teacher_available, self_course_teacher_unavailable)
    """
    handle_premise.refresh_unnormal_flag(101)
    return HP("self_course_teacher_available", 201), HP("self_course_teacher_unavailable", 201)


check("M3 对照：教师正常、人在本节教室：能到岗", teacher_premise_pair() == (1, 0), teacher_premise_pair())
teacher.sp_flag.unconscious_h = 5
check("M3 空气催眠、人已在本节教室：仍算能到岗（前提传了教室，授课行照样成立）", teacher_premise_pair() == (1, 0), teacher_premise_pair())
move_to(101, SCENE_DORM)
check("M3 空气催眠、人不在教室：来不了（此前判能到岗，学生空坐整节）", teacher_premise_pair() == (0, 1), teacher_premise_pair())
teacher.sp_flag.unconscious_h = 0
teacher.hypnosis.blockhead = True
move_to(101, classroom_path(ROOM1))
check("M3 木头人：人在教室也来不了（每轮被锁成原地等待；此前判能到岗）", teacher_premise_pair() == (0, 1), teacher_premise_pair())
teacher.hypnosis.blockhead = False
check("M3 解除后恢复能到岗", teacher_premise_pair() == (1, 0), teacher_premise_pair())
schedule_handle.clear_selected_course(201, 0, 0)
clear_schedules()

section("Plan 31 §3.8（L4）：改任实习岗位的女儿在那个岗位上不再亮 <课>，CVP 不再读成实习课")
set_time(period_time(0))
student.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTERN, intern_work)
move_to(201, intern_place)
_tip = character_info_head.get_now_class_tip(201)
check("L4 对照：学生岗、人在实习地点：<课> 写实习课，CVP CourseType 为实习课", _tip is not None and not _tip[0] and HP("CVP_A1_CourseType|5_E_1", 201) == 1, _tip)
student.work.work_type = intern_work
_tip = character_info_head.get_now_class_tip(201)
check("L4 改任这个岗位、本人就在岗：不亮 <课>，CVP CourseType / Course 都不成立（此前按残留课表显示在上实习课）",
      _tip is None and HP("CVP_A1_CourseType|5_E_1", 201) == 0 and HP("CVP_A1_Course|43_G_0", 201) == 0, _tip)
student.work.work_type = 152
check("L4 改回学生岗：恢复", character_info_head.get_now_class_tip(201) is not None)

section("Plan 31 §3.6（L2）：<翘> 只认今天挂上的翘课 flag")
_growth_201 = growth_handle.get_child_growth(201)
_growth_201.skip_class_flag = True
_growth_201.skip_class_day = cache.game_time.toordinal() - 1
_tip = character_info_head.get_now_class_tip(201)
check("L2 前一天挂上、没清掉的 flag（一步跨过午夜 / 翘课当天离线）：不亮 <翘>，照常显示在上课（此前整天挂着 <翘>）", _tip is not None and not _tip[0], _tip)
_growth_201.skip_class_day = cache.game_time.toordinal()
_tip = character_info_head.get_now_class_tip(201)
check("L2 今天挂上的：亮 <翘>", _tip is not None and _tip[0], _tip)
_growth_201.skip_class_flag = False
_growth_201.skip_class_day = 0
schedule_handle.clear_selected_course(201, 0, 0)
move_to(201, SCENE_DORM)

section("Plan 31 §3.10（L6）：前教师改当学生，CVP 按她自己的课表取课，不再读旧授课格")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 43, 101)
schedule_handle.set_selected_course(101, 0, 0, E.COURSE_TYPE_PE, _("木桩房"))
check("L6 对照：教师岗时按授课格读成理论课、科目 43", HP("CVP_A1_CourseType|0_E_1", 101) == 1 and HP("CVP_A1_Course|43_G_0", 101) == 1)
teacher.work.work_type = 152
check("L6 改当学生：CourseType 读她自己的体育课，旧授课格的理论课与科目 43 都不成立（此前读成旧授课格）",
      HP("CVP_A1_CourseType|3_E_1", 101) == 1 and HP("CVP_A1_CourseType|0_E_1", 101) == 0 and HP("CVP_A1_Course|43_G_0", 101) == 0)
teacher.work.work_type = 151
schedule_handle.clear_selected_course(101, 0, 0)
clear_schedules()

section("Plan 31 §3.13（L9）：玩家手动授课时 CVP 按所在教室判课型、科目回落学识（与 512 同口径）")
set_time(period_time(0))
_pl_behavior = pl.behavior.behavior_id
pl.behavior.behavior_id = constant.Behavior.TEACH
move_to(0, classroom_path(ROOM1))
check("L9 在理论教室一手动授课：CourseType 为理论课、Course|45（学识）成立（此前两项都是 -1，授课口上只剩占位地文）",
      HP("CVP_A1_CourseType|0_E_1", 0) == 1 and HP("CVP_A1_Course|45_G_0", 0) == 1)
move_to(0, classroom_path(ROOM_P))
check("L9 在实践教室一：CourseType 为实践课，科目仍回落学识", HP("CVP_A1_CourseType|1_E_1", 0) == 1 and HP("CVP_A1_CourseType|0_E_1", 0) == 0
      and HP("CVP_A1_Course|45_G_0", 0) == 1)
move_to(0, classroom_path(schedule_handle.get_classroom_list(E.COURSE_TYPE_PUBLIC)[0]))
check("L9 在大礼堂：公开课", HP("CVP_A1_CourseType|2_E_1", 0) == 1)
move_to(0, classroom_path(ROOM1))
set_time(DEFAULT_TIME.replace(hour=20))
check("L9 节次外手动授课：同样按教室判（512 也不看节次）", HP("CVP_A1_CourseType|0_E_1", 0) == 1 and HP("CVP_A1_Course|45_G_0", 0) == 1)
set_time(period_time(0))
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 0, ROOM_P, 70)
move_to(0, classroom_path(ROOM_P))
check("L9 人在当天临时实操课的教室里：教师反查优先，科目取那节课的 70、不回落学识", HP("CVP_A1_Course|70_G_0", 0) == 1 and HP("CVP_A1_Course|45_G_0", 0) == 0)
cache.rhodes_island.temp_sex_class = {}
pl.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
check("L9 玩家没在授课：不回落，两项都不成立", HP("CVP_A1_CourseType|1_E_1", 0) == 0 and HP("CVP_A1_Course|45_G_0", 0) == 0)
adult.behavior.behavior_id = constant.Behavior.TEACH
move_to(301, classroom_path(ROOM1))
check("L9 回落只给玩家：行为是授课的非教师 NPC 不按教室判", HP("CVP_A1_CourseType|0_E_1", 301) == 0 and HP("CVP_A1_Course|45_G_0", 301) == 0)
adult.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
move_to(301, SCENE_DORM)
pl.behavior.behavior_id = _pl_behavior
move_to(0, SCENE_DORM)
check("L18 同学前提的 docstring 写上新口径（双方都在学生岗、确有的课、对方是幼女或萝莉）",
      all(k in (handle_premise.handle_self_have_classmate.__doc__ or "") for k in ("学生岗", "确有", "萝莉")))

finish()
