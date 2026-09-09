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
             "growth_stop_1", "growth_stop_0"):
    check(f"前提 {name} 已注册", name in constant.handle_premise_data)

section("岗位与女儿前提")
check("work_is_teacher / student", HP("work_is_teacher", 101) == 1 and HP("work_is_teacher", 201) == 0 and HP("work_is_student", 201) == 1 and HP("work_is_student", 101) == 0)
pl.target_character_id = 201
check("t_work_is_student / t_work_is_teacher", HP("t_work_is_student", 0) == 1 and HP("t_work_is_teacher", 0) == 0)
check("女儿前提", HP("self_is_player_daughter", 201) == 1 and HP("self_is_player_daughter", 301) == 0 and HP("self_not_player_daughter", 301) == 1
      and HP("target_is_player_daughter", 0) == 1 and HP("target_not_player_daughter", 0) == 0)
check("同胞前提", HP(P.SELF_HAVE_SIBLING_CHILD, 201) == 1 and HP(P.SELF_HAVE_SIBLING_CHILD, 301) == 0)
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
check("下课但仍在这一节内：临时课占着这节，教师视角仍成立", HP("CVP_A1_Course|74_G_0", 0) == 1)
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

finish()
