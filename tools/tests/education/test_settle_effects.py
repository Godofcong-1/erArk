# -*- coding: UTF-8 -*-
"""结算器：512 授课 / 548 自习 / 549 翘课 / 550 检查成绩单 / 552 实习 / 553 见学 / 554 自由玩耍 / 622 炫耀 / 623 翘课被抓 / 10014 10015 课堂H模式"""
from _bootstrap import *  # noqa: F401,F403
from Script.Settle import default as settle_default
from Script.Settle import Second_effect  # noqa: F401  注册二段结算

open_all_classroom()
clear_schedules()
ROOM1 = _("理论教室一")
ROOM_P = _("实践教室一")
teacher = make_character(101, "教师甲", 151, position=classroom_path(ROOM1))
mother = make_character(102, "母亲", 0)
student_a = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102, born_days=300, position=classroom_path(ROOM1))
student_b = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102, born_days=120, position=classroom_path(ROOM1))
BE = constant_effect.BehaviorEffect
SE = constant_effect.SecondEffect
EFFECT = constant.settle_behavior_effect_data
SECOND = constant.settle_second_behavior_effect_data
E = education_constant
# 授课结算末尾会对每个学生调 judge_character_status（那是行为循环的事），单测里钉死它
settle_default.character_behavior.judge_character_status = lambda cid: 0

section("注册")
for effect_id in (512, 548, 549, 550, 552, 553, 554, 555, 556, 10014, 10015):
    check(f"效果 {effect_id} 已注册", effect_id in EFFECT)
check("二段 622 / 623 已注册", SE.SHOW_OFF_STUDY in SECOND and SE.CAUGHT_SKIP_CLASS in SECOND)
for behavior, effect_id in (("teach", 512), ("self_study", 548), ("skip_class", 549), ("check_report_card", 550), ("intern_class", 552),
                            ("follow_mother", 553), ("free_play", 554), ("start_sex_class", 10014), ("end_sex_class", 10015)):
    check(f"{behavior} 的效果串挂了 {effect_id}", effect_id in game_config.config_behavior_effect_data.get(behavior, []))
check("show_off_study / caught_skip_class 的二段效果串", 622 in game_config.config_behavior_effect_data.get("show_off_study", []) and 623 in game_config.config_behavior_effect_data.get("caught_skip_class", []))

section("512 授课")
set_time(period_time(0))
teacher.ability[45] = 4
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
student_b.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
exp_45 = growth_handle.get_subject_exp_id(45)
change = game_type.CharacterStatusChange()
EFFECT[512](101, 45, change, cache.game_time)
check("教师按课表科目教学相长", teacher.experience.get(exp_45, 0) > 0)
check("场景内听课的学生都得到该科目经验并记出勤", student_a.experience.get(exp_45, 0) == int(3 * 2.0) and student_b.experience.get(exp_45, 0) == int(3 * 2.0)
      and student_a.child_growth.attend_class_count == 1 and student_b.child_growth.attend_class_count == 1)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
teacher.experience[exp_45] = 0
EFFECT[512](101, 45, change, cache.game_time)
check("课表查不到时回落学识", teacher.experience.get(exp_45, 0) > 0)
move_to(0, classroom_path(ROOM1))
# 好感链的实际数值受信物 / 难度 / 连续指令等外部因素影响，这里只验「玩家授课时确实走了好感与信赖结算」
favor_calls = []
_orig_favor = settle_default.base_chara_favorability_and_trust_common_settle
settle_default.base_chara_favorability_and_trust_common_settle = lambda *a, **k: favor_calls.append(a)
EFFECT[512](0, 45, change, cache.game_time)
settle_default.base_chara_favorability_and_trust_common_settle = _orig_favor
check("玩家授课：每个学生各走一次好感与一次信赖结算", len(favor_calls) == 4 and {call[6] for call in favor_calls} == {201, 202}, favor_calls)
EFFECT[512](101, 45, change, cache.game_time)
move_to(0, SCENE_DORM)

section("548 自习 / 549 翘课 / 554 自由玩耍")
schedule_handle.set_class_cell(ROOM1, 0, 0, 43, -1)
exp_43 = growth_handle.get_subject_exp_id(43)
EFFECT[548](201, 45, change, cache.game_time)
check("自习：按本节科目给自习基础值经验", student_a.experience.get(exp_43, 0) == E.SELF_STUDY_EXP_BASE)
schedule_handle.clear_selected_course(201, 0, 0)
before = student_a.experience.get(exp_45, 0)
EFFECT[548](201, 45, change, cache.game_time)
check("没课表时自习回落学识", student_a.experience.get(exp_45, 0) - before == E.SELF_STUDY_EXP_BASE)
student_a.status_data[19] = 100
EFFECT[549](201, 45, change, cache.game_time)
check("翘课：置 flag、抑郁回落一节课的量", student_a.child_growth.skip_class_flag and student_a.status_data[19] == 55)
EFFECT[554](202, 60, change, cache.game_time)
check("自由玩耍不报错", True)

section("623 翘课被抓 / 622 炫耀")
dep_before = student_a.status_data.get(19, 0)
fear_before = student_a.status_data.get(18, 0)
SECOND[SE.CAUGHT_SKIP_CLASS](201, change)
check("被抓：清 flag、抑郁与恐怖上升", not student_a.child_growth.skip_class_flag and student_a.status_data.get(19, 0) > dep_before and student_a.status_data.get(18, 0) > fear_before)
dep_before = student_a.status_data.get(19, 0)
SECOND[SE.CAUGHT_SKIP_CLASS](201, change)
check("没翘课时被抓结算什么都不做", student_a.status_data.get(19, 0) == dep_before)
student_a.child_growth.show_off_ability = {45: 3}
from Script.Settle import common_default

favor_calls = []
_orig_favor = common_default.base_chara_favorability_and_trust_common_settle
common_default.base_chara_favorability_and_trust_common_settle = lambda *a, **k: favor_calls.append(a)
SECOND[SE.SHOW_OFF_STUDY](201, change)
common_default.base_chara_favorability_and_trust_common_settle = _orig_favor
check("炫耀：走一次好感结算并清空待炫耀", len(favor_calls) == 1 and student_a.child_growth.show_off_ability == {})
SECOND[SE.SHOW_OFF_STUDY](201, change)
check("没有待炫耀时什么都不做", True)

section("552 实习 / 553 见学")
intern_work = next(cid for cid in game_config.config_work_type
                   if cid and not game_config.config_work_type[cid].tag and game_config.config_work_type[cid].ability_id
                   and cid not in E.EXCLUDE_INTERN_WORK_TYPE and game_config.config_work_type[cid].place_tag in constant.place_data)
work_ability = game_config.config_work_type[intern_work].ability_id
exp_work = growth_handle.get_subject_exp_id(work_ability)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_INTERN, intern_work)
place = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
move_to(201, place)
before = student_a.experience.get(exp_work, 0)
EFFECT[552](201, 45, change, cache.game_time)
half = max(1, E.COURSE_EXP_BASE[E.COURSE_TYPE_INTERN] // 2)
check("无人在岗：见习减半", student_a.experience.get(exp_work, 0) - before == half, student_a.experience.get(exp_work, 0) - before)
mentor = make_character(103, "带教", intern_work, position=place)
mentor.ability[work_ability] = 4
before = student_a.experience.get(exp_work, 0)
EFFECT[552](201, 45, change, cache.game_time)
check("有导师：按师徒等级差学该岗位能力", student_a.experience.get(exp_work, 0) - before == int(E.COURSE_EXP_BASE[E.COURSE_TYPE_INTERN] * 2.0))
schedule_handle.clear_selected_course(201, 0, 0)
before = student_a.experience.get(exp_work, 0)
EFFECT[552](201, 45, change, cache.game_time)
check("本节不是实习课时不结算", student_a.experience.get(exp_work, 0) == before)
care_before = growth_handle.get_child_growth(202).care_point
EFFECT[553](202, 60, change, cache.game_time)
check("见学：照料值 +0.5", abs(growth_handle.get_child_growth(202).care_point - care_before - E.FOLLOW_MOTHER_CARE_POINT) < 1e-9)
mother.sp_flag.is_h = True
care_before = growth_handle.get_child_growth(202).care_point
EFFECT[553](202, 60, change, cache.game_time)
check("结算时母亲已无效 → 不结算", growth_handle.get_child_growth(202).care_point == care_before)
mother.sp_flag.is_h = False

section("550 检查成绩单")
pl.target_character_id = 201
drawn_text.clear()
EFFECT[550](0, 15, change, cache.game_time)
check("没有冻结成绩单：给「尚未结束」的现算版", any("尚未结束" in t for t in drawn_text))
check("flag 不动", not student_a.child_growth.report_card_flag)
student_a.child_growth.report_card_flag = True
semester_handle.push_report_card(201, {"year": 2026, "month": 6, "attend": 9, "absent": 1, "rate": 90, "level_change": {45: [1, 3], 43: [0, 1]}, "grade": E.REPORT_GRADE_EXCELLENT})
drawn_text.clear()
favor_before = student_a.favorability.get(0, 0)
EFFECT[550](0, 15, change, cache.game_time)
check("有冻结成绩单：发那一份并清 flag", any("优秀" in t and "尚未结束" not in t for t in drawn_text) and not student_a.child_growth.report_card_flag)
check("加了好感", student_a.favorability.get(0, 0) > favor_before)
semester_handle.push_report_card(201, {"year": 2026, "month": 9, "attend": 1, "absent": 0, "rate": 100, "level_change": {}, "grade": E.REPORT_GRADE_GOOD})
drawn_text.clear()
EFFECT[550](0, 15, change, cache.game_time)
check("有多份时提示去养成总览翻看", any("养成总览" in t for t in drawn_text))
pl.target_character_id = 0
EFFECT[550](0, 15, change, cache.game_time)
check("没有交互对象不报错", True)

section("10014 / 10015 课堂H模式")
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
move_to(202, classroom_path(ROOM_P))
set_time(period_time(5))
cache.rhodes_island.temp_sex_class = {}
cache.sex_class_mode = False
cache.group_sex_mode = False
attend_before = student_a.child_growth.attend_class_count
EFFECT[10014](0, 5, change, cache.game_time)
check("开课：两个标志都置位", cache.sex_class_mode and cache.group_sex_mode)
check("在场学生进 H 状态并记出勤", student_a.sp_flag.is_h and student_b.sp_flag.is_h and student_a.child_growth.attend_class_count == attend_before + 1)
check("到场二段行为已派发", constant.Behavior.JOIN_SEX_CLASS in student_a.second_behavior and student_a.second_behavior[constant.Behavior.JOIN_SEX_CLASS] > 0)
attend_before = student_a.child_growth.attend_class_count
EFFECT[10014](0, 5, change, cache.game_time)
check("重复开课不重复记出勤", student_a.child_growth.attend_class_count == attend_before)
sex_class_handle.start_sex_class(70)
check("有运行中的课", sex_class_handle.get_running_class() is not None)
EFFECT[10015](0, 5, change, cache.game_time)
check("下课：关闭模式、清 running", not cache.sex_class_mode and sex_class_handle.get_running_class() is None)

finish()
