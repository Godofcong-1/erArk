# -*- coding: UTF-8 -*-
"""结算器：512 授课 / 557 学生晚到补结算 / 548 自习 / 549 翘课 / 550 检查成绩单 / 552 实习 / 553 见学 / 554 自由玩耍 / 622 炫耀 / 623 翘课被抓 / 10014 10015 课堂H模式"""
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


def reset_mark(*character_id_list):
    """
    清掉学生的「本节已结算」去重标记：同一节里要连着验好几种结算时用（第五轮加的去重）
    Keyword arguments:
    character_id_list -- 角色id
    Return arguments:
    无
    """
    for character_id in character_id_list:
        growth_handle.get_child_growth(character_id).last_attend_period = []


section("注册")
for effect_id in (512, 548, 549, 550, 552, 553, 554, 555, 556, 557, 10014, 10015):
    check(f"效果 {effect_id} 已注册", effect_id in EFFECT)
check("二段 622 / 623 已注册", SE.SHOW_OFF_STUDY in SECOND and SE.CAUGHT_SKIP_CLASS in SECOND)
for behavior, effect_id in (("teach", 512), ("attent_class", 557), ("self_study", 548), ("skip_class", 549), ("check_report_card", 550), ("intern_class", 552),
                            ("follow_mother", 553), ("free_play", 554), ("start_sex_class", 10014), ("end_sex_class", 10015)):
    check(f"{behavior} 的效果串挂了 {effect_id}", effect_id in game_config.config_behavior_effect_data.get(behavior, []))
check("show_off_study / caught_skip_class 的二段效果串", 622 in game_config.config_behavior_effect_data.get("show_off_study", []) and 623 in game_config.config_behavior_effect_data.get("caught_skip_class", []))

section("512 授课")
set_time(period_time(0))
teacher.ability[45] = 4
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_selected_course(202, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
student_b.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
bystander = make_character(204, "别班学生", 152, daughter=True, stage=103, mother_id=102, born_days=300, position=classroom_path(ROOM1))
bystander.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
exp_45 = growth_handle.get_subject_exp_id(45)
change = game_type.CharacterStatusChange()
EFFECT[512](101, 45, change, cache.game_time)
check("教师按课表科目教学相长", teacher.experience.get(exp_45, 0) > 0)
check("本节来这间教室的学生都得到该科目经验并记出勤", student_a.experience.get(exp_45, 0) == int(3 * 2.0) and student_b.experience.get(exp_45, 0) == int(3 * 2.0)
      and student_a.child_growth.attend_class_count == 1 and student_b.child_growth.attend_class_count == 1)
check("NPC 教师不给课表没指向这间教室的人发（第五轮）", bystander.experience.get(exp_45, 0) == 0 and (bystander.child_growth is None or bystander.child_growth.attend_class_count == 0))
EFFECT[512](101, 45, change, cache.game_time)
check("同一节再广播一次不重复记（第五轮）", student_a.child_growth.attend_class_count == 1 and student_a.experience.get(exp_45, 0) == int(3 * 2.0))
remove_character(204)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
teacher.experience[exp_45] = 0
EFFECT[512](101, 45, change, cache.game_time)
check("课表查不到时回落学识", teacher.experience.get(exp_45, 0) > 0)
move_to(0, classroom_path(ROOM1))
reset_mark(201, 202)
# 好感链的实际数值受信物 / 难度 / 连续指令等外部因素影响，这里只验「玩家授课时确实走了好感与信赖结算」
favor_calls = []
_orig_favor = settle_default.base_chara_favorability_and_trust_common_settle
settle_default.base_chara_favorability_and_trust_common_settle = lambda *a, **k: favor_calls.append(a)
EFFECT[512](0, 45, change, cache.game_time)
settle_default.base_chara_favorability_and_trust_common_settle = _orig_favor
check("玩家授课：每个学生各走一次好感与一次信赖结算", len(favor_calls) == 4 and {call[6] for call in favor_calls} == {201, 202}, favor_calls)
move_to(0, SCENE_DORM)

section("512 玩家手动授课：只有课表排在这间教室的节次才计出勤（Plan 25 §3.4）")
# 个人课表指向的格子要在全局课表上有课：上一段把它清掉了，空格子按「已停课」算没课（Plan 27 §3.3）
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, -1)
move_to(0, classroom_path(ROOM1))
settle_default.base_chara_favorability_and_trust_common_settle = lambda *a, **k: None
set_time(DEFAULT_TIME.replace(hour=12, minute=30))
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
reset_mark(201)
attend_before = student_a.child_growth.attend_class_count
exp_before = student_a.experience.get(exp_45, 0)
EFFECT[512](0, 45, change, cache.game_time)
check("午休手动授课：给收益、不计出勤", student_a.experience.get(exp_45, 0) > exp_before and student_a.child_growth.attend_class_count == attend_before,
      (student_a.experience.get(exp_45, 0) - exp_before, student_a.child_growth.attend_class_count - attend_before))
set_time(period_time(0))
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
reset_mark(201)
EFFECT[512](0, 45, change, cache.game_time)
check("本节课表就排在这间教室：计一节出勤", student_a.child_growth.attend_class_count == attend_before + 1)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室二"))
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
reset_mark(201)
EFFECT[512](0, 45, change, cache.game_time)
check("本节课表排在别的教室：只给收益、不计出勤", student_a.child_growth.attend_class_count == attend_before + 1)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
settle_default.base_chara_favorability_and_trust_common_settle = _orig_favor
reset_mark(201, 202)
move_to(0, SCENE_DORM)

section("557 学生侧结算：本节教师判能到岗，学生开始听课时就结算（第五轮加的晚到补结算，Plan 31 §3.1 放宽）")
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
reset_mark(201, 202)
# 教师还在路上：人不在这间教室、也没在授课——玩家一步跨满一整节、教师换教室晚到时，学生坐下那一刻就是这样
move_to(101, SCENE_DORM)
teacher.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
before = student_a.experience.get(exp_45, 0)
attend_before = student_a.child_growth.attend_class_count
EFFECT[557](201, 45, change, cache.game_time)
check("H1 教师还在路上、判能到岗：学生开始听课时就结算这一节（此前要等教师到场开讲，玩家一步跨满一整节时整节白上）",
      student_a.experience.get(exp_45, 0) - before == int(3 * 2.0) and student_a.child_growth.attend_class_count == attend_before + 1,
      (student_a.experience.get(exp_45, 0) - before, student_a.child_growth.attend_class_count - attend_before))
move_to(101, classroom_path(ROOM1))
teacher.behavior.behavior_id = constant.Behavior.TEACH
EFFECT[512](101, 45, change, cache.game_time)
check("H1 教师随后到场开讲：512 广播不再给她重复发（同一节去重）",
      student_a.experience.get(exp_45, 0) - before == int(3 * 2.0) and student_a.child_growth.attend_class_count == attend_before + 1)
EFFECT[557](201, 45, change, cache.game_time)
check("补过之后再补也不重复", student_a.child_growth.attend_class_count == attend_before + 1)
# 教师判来不了：学生这一节该降级自习（548），557 不结算
reset_mark(202)
teacher.sp_flag.is_h = True
before = student_b.experience.get(exp_45, 0)
EFFECT[557](202, 45, change, cache.game_time)
check("H1 教师判来不了（H 中）：557 不结算", student_b.experience.get(exp_45, 0) == before and student_b.child_growth.last_attend_period == [])
teacher.sp_flag.is_h = False
# Plan 31 §3.4：空气催眠只在人已在本节教室时算能到岗，木头人一律来不了（测试直接改状态位，要自己刷新异常位）
teacher.sp_flag.unconscious_h = 5
move_to(101, SCENE_DORM)
handle_premise.refresh_unnormal_flag(101)
EFFECT[557](202, 45, change, cache.game_time)
check("M3 空气催眠的教师、人不在本节教室（去教室的移动行走不了）：557 不结算", student_b.child_growth.last_attend_period == [])
move_to(101, classroom_path(ROOM1))
EFFECT[557](202, 45, change, cache.game_time)
check("M3 空气催眠的教师、人已在本节教室（授课行照样成立）：照常结算", student_b.child_growth.last_attend_period == [cache.game_time.toordinal(), 0],
      student_b.child_growth.last_attend_period)
reset_mark(202)
teacher.sp_flag.unconscious_h = 6
teacher.hypnosis.blockhead = True
handle_premise.refresh_unnormal_flag(101)
EFFECT[557](202, 45, change, cache.game_time)
check("M3 体控-木头人的教师（每轮被锁成原地等待）：人就在教室也不结算", student_b.child_growth.last_attend_period == [])
teacher.hypnosis.blockhead = False
teacher.sp_flag.unconscious_h = 0
handle_premise.refresh_unnormal_flag(101)
# 授课者是玩家（当天的临时实操课）：那是课堂 H，不是授课
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 0, ROOM_P, 70, must_attend=[202])
move_to(202, classroom_path(ROOM_P))
reset_mark(202)
EFFECT[557](202, 45, change, cache.game_time)
check("H1 本节是玩家的临时实操课（授课者为玩家）：557 不结算", student_b.child_growth.last_attend_period == [])
cache.rhodes_island.temp_sex_class = {}
# 学生不在本节的教室里（被玩家拉到别处听课）：她这一节由把她拉去的人结算，557 不接手
move_to(202, SCENE_DORM)
EFFECT[557](202, 45, change, cache.game_time)
check("H1 学生不在本节的教室里：557 不结算", student_b.child_growth.last_attend_period == [])
move_to(202, classroom_path(ROOM1))
teacher.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
reset_mark(201, 202)

section("548 自习 / 549 翘课 / 554 自由玩耍")
schedule_handle.set_class_cell(ROOM1, 0, 0, 43, -1)
exp_43 = growth_handle.get_subject_exp_id(43)
attend_before = student_a.child_growth.attend_class_count
EFFECT[548](201, 45, change, cache.game_time)
check("自习：按本节科目给自习基础值经验", student_a.experience.get(exp_43, 0) == E.SELF_STUDY_EXP_BASE)
check("课表排了课的自习（教师缺席降级）计出勤", student_a.child_growth.attend_class_count == attend_before + 1)
schedule_handle.clear_selected_course(201, 0, 0)
reset_mark(201)
before = student_a.experience.get(exp_45, 0)
attend_before = student_a.child_growth.attend_class_count
EFFECT[548](201, 45, change, cache.game_time)
check("没课表时自习回落学识", student_a.experience.get(exp_45, 0) - before == E.SELF_STUDY_EXP_BASE)
check("日程活动的自习（本节没排课）不计出勤（第五轮）", student_a.child_growth.attend_class_count == attend_before)
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
reset_mark(201)
before = student_a.experience.get(exp_work, 0)
EFFECT[552](201, 45, change, cache.game_time)
half = max(1, E.COURSE_EXP_BASE[E.COURSE_TYPE_INTERN] // 2)
check("无人在岗：见习减半", student_a.experience.get(exp_work, 0) - before == half, student_a.experience.get(exp_work, 0) - before)
mentor = make_character(103, "带教", intern_work, position=place)
mentor.ability[work_ability] = 4
reset_mark(201)
before = student_a.experience.get(exp_work, 0)
_attend_552 = student_a.child_growth.attend_class_count
EFFECT[552](201, 45, change, cache.game_time)
check("有导师：按师徒等级差学该岗位能力", student_a.experience.get(exp_work, 0) - before == int(E.COURSE_EXP_BASE[E.COURSE_TYPE_INTERN] * 2.0))
check("Plan 29 §3.1：实习课的出勤由 552 记一节，同一节 settle_course_attend（716 给体育 / 兴趣课用的）不会再记一份",
      student_a.child_growth.attend_class_count == _attend_552 + 1 and not growth_handle.settle_course_attend(201)
      and student_a.child_growth.attend_class_count == _attend_552 + 1)
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
# 前置修习（口径 63 宽松版）：两个学生各排一节性技科目的教室课
schedule_handle.set_class_cell(ROOM_P, 2, 8, 74, -1)
schedule_handle.set_selected_course(201, 2, 8, E.COURSE_TYPE_PRACTICE, ROOM_P)
schedule_handle.set_selected_course(202, 2, 8, E.COURSE_TYPE_PRACTICE, ROOM_P)
# 开课指令的完整顺序：先 start_sex_class() 建课并记出勤，再结算效果串里的 10014（第五轮：出勤只记这一次）
attend_before = student_a.child_growth.attend_class_count
sex_class_handle.start_sex_class(70)
EFFECT[10014](0, 5, change, cache.game_time)
check("开课：两个标志都置位", cache.sex_class_mode and cache.group_sex_mode)
check("在场学生进 H 状态", student_a.sp_flag.is_h and student_b.sp_flag.is_h)
check("开课整条链路每个学生只记一节出勤（第五轮修正 +2）", student_a.child_growth.attend_class_count == attend_before + 1, student_a.child_growth.attend_class_count - attend_before)
check("到场二段行为已派发", constant.Behavior.JOIN_SEX_CLASS in student_a.second_behavior and student_a.second_behavior[constant.Behavior.JOIN_SEX_CLASS] > 0)
attend_before = student_a.child_growth.attend_class_count
EFFECT[10014](0, 5, change, cache.game_time)
check("重复开课不重复记出勤", student_a.child_growth.attend_class_count == attend_before)
check("有运行中的课", sex_class_handle.get_running_class() is not None)
EFFECT[10015](0, 5, change, cache.game_time)
check("下课：关闭模式、清 running", not cache.sex_class_mode and sex_class_handle.get_running_class() is None)

section("Plan 26 §3.1：性技科目的教室课与自习只发理论经验、不补记初体验")
cache.rhodes_island.temp_sex_class = {}
set_time(period_time(6))
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
move_to(202, SCENE_DORM)
schedule_handle.set_class_cell(ROOM1, 0, 6, 71, 101)
schedule_handle.set_selected_course(201, 0, 6, E.COURSE_TYPE_THEORY, ROOM1)
teacher.behavior.behavior_id = constant.Behavior.TEACH
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
reset_mark(201)
oral_before = (student_a.experience.get(42, 0), teacher.experience.get(42, 0))
theory_before = (student_a.experience.get(171, 0), teacher.experience.get(171, 0))
EFFECT[512](101, 45, change, cache.game_time)
check("512 舌技理论课：师生都拿口交理论经验（171）", student_a.experience.get(171, 0) > theory_before[0] and teacher.experience.get(171, 0) > theory_before[1],
      (student_a.experience.get(171, 0), teacher.experience.get(171, 0)))
check("512 舌技理论课：师生的口交经验（42）不变、都没有口交初体验履历", (student_a.experience.get(42, 0), teacher.experience.get(42, 0)) == oral_before
      and 2 not in student_a.first_record.first_part_sex_dict and 2 not in teacher.first_record.first_part_sex_dict)
schedule_handle.set_class_cell(ROOM1, 0, 7, 74, -1)
schedule_handle.set_selected_course(201, 0, 7, E.COURSE_TYPE_THEORY, ROOM1)
set_time(period_time(7))
student_a.behavior.behavior_id = constant.Behavior.SELF_STUDY
vaginal_before = (student_a.experience.get(61, 0), student_a.experience.get(174, 0))
EFFECT[548](201, 45, change, cache.game_time)
check("548 膣技自习：性交理论经验（174）增加、阴道性交经验（61）不变", student_a.experience.get(174, 0) > vaginal_before[1] and student_a.experience.get(61, 0) == vaginal_before[0])

section("Plan 26 §3.7：玩家在别的教室手动授课，不读当天临时实操课的科目")
set_time(period_time(8))
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 8, ROOM_P, 70)
move_to(0, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
reset_mark(201)
_orig_favor_settle = settle_default.base_chara_favorability_and_trust_common_settle
settle_default.base_chara_favorability_and_trust_common_settle = lambda *a, **k: None
finger_before = (student_a.experience.get(exp_45, 0), student_a.experience.get(170, 0), student_a.experience.get(41, 0))
EFFECT[512](0, 45, change, cache.game_time)
check("玩家在理论教室授课：回落学识，不拿指技的任何经验", student_a.experience.get(exp_45, 0) > finger_before[0] and student_a.experience.get(170, 0) == finger_before[1]
      and student_a.experience.get(41, 0) == finger_before[2])
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
reset_mark(201)
finger_before = (student_a.experience.get(170, 0), student_a.experience.get(41, 0))
EFFECT[512](0, 45, change, cache.game_time)
settle_default.base_chara_favorability_and_trust_common_settle = _orig_favor_settle
check("玩家就在临时课的教室里授课：按那门性技讲，只发指技理论经验（170）", student_a.experience.get(170, 0) > finger_before[0] and student_a.experience.get(41, 0) == finger_before[1])
cache.rhodes_island.temp_sex_class = {}
move_to(0, SCENE_DORM)

section("Plan 27 §3.6：检查成绩单看过之后给本学期截至目前，养成数值 23 读待查看")
pl.target_character_id = 201
growth_a = growth_handle.get_child_growth(201)
growth_a.report_card_flag = False
drawn_text.clear()
EFFECT[550](0, 15, change, cache.game_time)
check("上一份已看过、学期中途再查：给「尚未结束」的截至目前版，不再重发上一份（此前有过成绩单就永远只给上一份）",
      any("尚未结束" in t for t in drawn_text) and not growth_a.report_card_flag)
check("截至目前版的翻看提示：历史里的 2 份都算更早的学期", any("更早的 2 个学期" in t for t in drawn_text), [t[-40:] for t in drawn_text])
check("养成数值 23：没有待查看为 0", growth_handle.get_growth_value(201, E.GROWTH_VALUE_REPORT_PENDING) == 0.0)
growth_a.report_card_flag = True
check("有待查看为 1", growth_handle.get_growth_value(201, E.GROWTH_VALUE_REPORT_PENDING) == 1.0)
drawn_text.clear()
EFFECT[550](0, 15, change, cache.game_time)
_report_text = "".join(drawn_text)
check("有未查看的新成绩单：发冻结的那份并清待查看", "的成绩单" in _report_text and "尚未结束" not in _report_text and not growth_a.report_card_flag
      and growth_handle.get_growth_value(201, E.GROWTH_VALUE_REPORT_PENDING) == 0.0, _report_text[:120])
check("发冻结那份时它自己就是最新一份：提示更早的 1 个学期", "更早的 1 个学期" in _report_text, _report_text[-60:])
check("没有养成数据的角色：养成数值 23 为 0", mother.child_growth is None and growth_handle.get_growth_value(102, E.GROWTH_VALUE_REPORT_PENDING) == 0.0)
pl.target_character_id = 0

section("Plan 27 §3.5 / §3.7：玩家手动授课拉来的学生截到本节下课，爆睡的学生不拉")
from Script.System.Instruct_System import handle_instruct  # noqa: E402

_orig_flow = handle_instruct.update.game_update_flow
handle_instruct.update.game_update_flow = lambda add_time: None
clear_schedules()
move_to(0, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
move_to(202, classroom_path(ROOM1))
set_time(period_time(0) + datetime.timedelta(minutes=30))
student_a.sp_flag.is_h = False
student_b.sp_flag.is_h = False
student_a.behavior.behavior_id = constant.Behavior.SELF_STUDY
student_b.behavior.behavior_id = constant.Behavior.SLEEP
student_b.sp_flag.sleep = False
handle_instruct.handle_teach()
check("9:30 开讲：学生听到 9:45 本节下课（15 分钟，此前固定 45 分钟、压进下一节），玩家自己仍是 45 分钟",
      student_a.behavior.behavior_id == constant.Behavior.ATTENT_CLASS and student_a.behavior.duration == 15 and pl.behavior.duration == 45,
      (student_a.behavior.behavior_id, student_a.behavior.duration, pl.behavior.duration))
check("行为是睡觉、没挂要睡觉标记的学生（当场爆睡）没被拉起来", student_b.behavior.behavior_id == constant.Behavior.SLEEP, student_b.behavior.behavior_id)
set_time(DEFAULT_TIME.replace(hour=12, minute=30))
student_a.behavior.behavior_id = constant.Behavior.SELF_STUDY
handle_instruct.handle_teach()
check("午休 12:30（节次外）开讲：学生仍听 45 分钟", student_a.behavior.behavior_id == constant.Behavior.ATTENT_CLASS and student_a.behavior.duration == 45,
      student_a.behavior.duration)
handle_instruct.update.game_update_flow = _orig_flow
student_b.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
move_to(0, SCENE_DORM)

section("Plan 28 §3.2：548 自习时本节是上不成的个人式课，不计出勤")
set_time(period_time(0))
reset_mark(201)
student_a.talent[103] = 0
student_a.talent[104] = 1
schedule_handle.set_selected_course(201, cache.game_time.weekday(), 0, E.COURSE_TYPE_INTEREST, E.ENTERTAINMENT_PLAY_HOUSE)
change = game_type.CharacterStatusChange()
_exp_45 = growth_handle.get_subject_exp_id(45)
_exp_before = student_a.experience.get(_exp_45, 0)
_attend_before = student_a.child_growth.attend_class_count
EFFECT[548](201, 45, change, cache.game_time)
check("少女排着过家家兴趣课、日程去自习：照给收益（回落学识），不计出勤（此前按「查得到课」多记一节）",
      student_a.experience.get(_exp_45, 0) > _exp_before and student_a.child_growth.attend_class_count == _attend_before,
      (student_a.experience.get(_exp_45, 0) - _exp_before, student_a.child_growth.attend_class_count - _attend_before))
student_a.talent[104] = 0
student_a.talent[103] = 1
reset_mark(201)
EFFECT[548](201, 45, change, cache.game_time)
check("对照：萝莉的同一格是一节课，这次自习计出勤", student_a.child_growth.attend_class_count == _attend_before + 1)
schedule_handle.clear_selected_course(201, cache.game_time.weekday(), 0)
reset_mark(201)

section("Plan 30 §3.4 / §3.5：这一节已记缺课的回来上课照给收益、不计出勤；623 记下被抓的日期")
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
schedule_handle.set_class_cell(ROOM1, 0, 1, 45, 101)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_selected_course(201, 0, 1, E.COURSE_TYPE_THEORY, ROOM1)
move_to(101, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
reset_mark(201)
student_a.child_growth.last_absent_period = []
class_ai.settle_absent(201)
student_a.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
_exp_before = student_a.experience.get(exp_45, 0)
_attend_before = student_a.child_growth.attend_class_count
EFFECT[512](101, 45, change, cache.game_time)
check("本节开课时体力缺课、休完回来：512 广播照给收益、不计出勤", student_a.experience.get(exp_45, 0) > _exp_before and student_a.child_growth.attend_class_count == _attend_before,
      (student_a.experience.get(exp_45, 0) - _exp_before, student_a.child_growth.attend_class_count - _attend_before))
reset_mark(201)
teacher.behavior.behavior_id = constant.Behavior.TEACH
_exp_before = student_a.experience.get(exp_45, 0)
EFFECT[557](201, 45, change, cache.game_time)
check("557 晚到补结算同样照给收益、不计出勤", student_a.experience.get(exp_45, 0) > _exp_before and student_a.child_growth.attend_class_count == _attend_before)
set_time(period_time(1))
reset_mark(201)
EFFECT[557](201, 45, change, cache.game_time)
check("下一节没缺课：照常计出勤", student_a.child_growth.attend_class_count == _attend_before + 1)
teacher.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
student_a.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
student_a.child_growth.skip_class_flag = True
SECOND[SE.CAUGHT_SKIP_CLASS](201, change)
check("623 被抓：记下当天的日期序数（当天剩余节次不再掷翘课）", student_a.child_growth.skip_caught_day == cache.game_time.toordinal() and not student_a.child_growth.skip_class_flag)
student_a.child_growth.skip_caught_day = 0
student_a.child_growth.last_absent_period = []
schedule_handle.clear_selected_course(201, 0, 0)
schedule_handle.clear_selected_course(201, 0, 1)
clear_schedules()
reset_mark(201)

section("Plan 31 §3.6（L2）：549 置翘课 flag 时记下行为开始那一天；前一天挂的 flag 不触发翘课被抓")
from Script.Design import second_behavior  # noqa: E402

growth_a = growth_handle.get_child_growth(201)
_late_start = DEFAULT_TIME.replace(hour=23, minute=40)
set_time(_late_start)
growth_a.skip_class_flag = False
growth_a.skip_class_day = 0
# 结算传进来的 now_time 是行为结束时刻（这里跨过了午夜），日期要按行为开始时刻记
EFFECT[549](201, 45, change, _late_start + datetime.timedelta(minutes=45))
check("L2 549：置 flag，日期记的是行为开始那一天（23:40 开始、跨过午夜才结束）", growth_a.skip_class_flag and growth_a.skip_class_day == _late_start.toordinal(),
      (growth_a.skip_class_flag, growth_a.skip_class_day, _late_start.toordinal()))
check("L2 judge_skip_class_today：挂上那天为真、次日为假", class_ai.judge_skip_class_today(201, _late_start)
      and not class_ai.judge_skip_class_today(201, _late_start + datetime.timedelta(minutes=45)))
# 623 的触发条件：孩子与玩家同场景、双方都醒着、玩家不在隐奸中
set_time(period_time(1))
move_to(0, classroom_path(ROOM1))
move_to(201, classroom_path(ROOM1))
pl.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
student_a.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
second_behavior.character_get_second_behavior(201, "caught_skip_class", reset=True)
growth_a.skip_class_flag = True
growth_a.skip_class_day = period_time(1).toordinal() - 1
second_behavior.judge_child_growth_second_behavior(201)
check("L2 前一天挂上、跨天没清掉的 flag（一步跨过午夜 / 翘课当天离线）：与玩家同场景也不触发翘课被抓",
      student_a.second_behavior.get("caught_skip_class", 0) == 0, student_a.second_behavior.get("caught_skip_class", 0))
growth_a.skip_class_day = period_time(1).toordinal()
second_behavior.judge_child_growth_second_behavior(201)
check("L2 对照：今天挂上的 flag 照常触发翘课被抓", student_a.second_behavior.get("caught_skip_class", 0) == 1)
second_behavior.character_get_second_behavior(201, "caught_skip_class", reset=True)
growth_a.skip_class_flag = False
growth_a.skip_class_day = 0
move_to(0, SCENE_DORM)

finish()
