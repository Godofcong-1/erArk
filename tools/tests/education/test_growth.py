# -*- coding: UTF-8 -*-
"""growth_handle：速度曲线、教育区加成、成长停滞、上课/见学结算、成年结算、养成数值、候选名单"""
from _bootstrap import *  # noqa: F401,F403

open_all_classroom()
clear_schedules()
ROOM1 = _("理论教室一")
teacher = make_character(101, "教师甲", 151)
mother = make_character(102, "母亲", 0)
student = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102, born_days=300)
child = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102, born_days=120)
adult = make_character(301, "成年学生", 152)

section("速度曲线与教育区加成")
check("师生等级差 +3 → 1.75", abs(growth_handle.get_learn_speed(5, 2) - 1.75) < 1e-9)
check("相等 → 1.0", growth_handle.get_learn_speed(3, 3) == 1.0)
check("学生高 3 级 → 0.4，永不归零", abs(growth_handle.get_learn_speed(2, 5) - 0.4) < 1e-9 and growth_handle.get_learn_speed(0, 8) > 0)
cache.rhodes_island.facility_level[education_constant.EDUCATION_ZONE_CID] = 1
check("教育区 Lv1 无加成", growth_handle.get_education_zone_adjust() == 1.0)
cache.rhodes_island.facility_level[education_constant.EDUCATION_ZONE_CID] = 5
check("教育区 Lv5 → 2.0", abs(growth_handle.get_education_zone_adjust() - 2.0) < 1e-9, growth_handle.get_education_zone_adjust())
cache.rhodes_island.facility_level[education_constant.EDUCATION_ZONE_CID] = 3
check("教育区 Lv3 → 1.2", abs(growth_handle.get_education_zone_adjust() - 1.2) < 1e-9)
cache.rhodes_island.facility_level[education_constant.EDUCATION_ZONE_CID] = 1

section("成长停滞（口径 27）")
teacher.ability[45] = 4
check("无停滞倍率 1.0", growth_handle.get_growth_stop_adjust(201) == 1.0)
check("不存在的角色 1.0", growth_handle.get_growth_stop_adjust(999) == 1.0)
check("总倍率 = 速度 × 加成", abs(growth_handle.get_class_adjust(45, 201, 101) - 2.0) < 1e-9)
student.talent[education_constant.GROWTH_STOP_TALENT_ID] = 1
check("停滞倍率 0.5", growth_handle.get_growth_stop_adjust(201) == education_constant.GROWTH_STOP_LEARN_RATE)
check("停滞后总倍率减半", abs(growth_handle.get_class_adjust(45, 201, 101) - 1.0) < 1e-9)
check("自习也减半", abs(growth_handle.get_class_adjust(45, 201, -1) - 0.5) < 1e-9)
check("教师自己停滞不影响教学", (teacher.talent.__setitem__(28, 1), abs(growth_handle.get_class_adjust(45, 202, 101) - 2.0) < 1e-9)[1])
teacher.talent[28] = 0
student.talent[28] = 0

section("学生侧结算")
set_time(period_time(0))
exp_id = growth_handle.get_subject_exp_id(45)
check("学识科目的经验 id 能从 AbilityUp.csv 解出", exp_id > 0, exp_id)
state_before = student.status_data.get(education_constant.LEARN_STATE_ID, 0)
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 45)
state_gain = student.status_data.get(education_constant.LEARN_STATE_ID, 0) - state_before
exp_gain = student.experience.get(exp_id, 0) - exp_before
check("习得状态增加", state_gain > 0, state_gain)
check("科目经验 = 基础值 × 总倍率", exp_gain == int(education_constant.COURSE_EXP_BASE[education_constant.COURSE_TYPE_THEORY] * 2.0), exp_gain)
check("记了一节出勤", student.child_growth.attend_class_count == 1)
check("记下了本节的去重标记", student.child_growth.last_attend_period == [period_time(0).toordinal(), 0], student.child_growth.last_attend_period)
# 同一节再结算一次：广播（512）与学生侧补结算（557）都会走到这里，第二次必须是空操作（第五轮）
exp_before = student.experience.get(exp_id, 0)
check("同一节第二次结算返回 False", growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 45) is False)
check("同一节不重复发收益与出勤", student.experience.get(exp_id, 0) == exp_before and student.child_growth.attend_class_count == 1)
# 以下几条都在同一节里验数值，每次先清掉去重标记
student.child_growth.last_attend_period = []
student.talent[28] = 1
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 45)
check("停滞后经验减半", student.experience.get(exp_id, 0) - exp_before == int(education_constant.COURSE_EXP_BASE[education_constant.COURSE_TYPE_THEORY] * 1.0))
student.talent[28] = 0
student.child_growth.last_attend_period = []
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 0)
check("add_time=0 不结算", student.experience.get(exp_id, 0) == exp_before and student.child_growth.attend_class_count == 2)
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, -1, 45, education_constant.COURSE_TYPE_THEORY, 45)
check("自习：经验按自习基础值", student.experience.get(exp_id, 0) - exp_before == education_constant.SELF_STUDY_EXP_BASE)
student.child_growth.last_attend_period = []
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, -1, 45, education_constant.COURSE_TYPE_INTERN, 45)
check("实习无导师：见习基础值减半", student.experience.get(exp_id, 0) - exp_before == max(1, education_constant.COURSE_EXP_BASE[education_constant.COURSE_TYPE_INTERN] // 2))
student.child_growth.last_attend_period = []
attend_before = student.child_growth.attend_class_count
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, -1, 45, education_constant.COURSE_TYPE_THEORY, 45, count_attend=False)
check("count_attend=False：给收益不计出勤", student.experience.get(exp_id, 0) > exp_before and student.child_growth.attend_class_count == attend_before)
set_time(period_time(0).replace(hour=12, minute=30))
attend_before = student.child_growth.attend_class_count
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 45)
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 45)
check("节次外（玩家午休手动授课）不去重", student.child_growth.attend_class_count == attend_before + 2)
set_time(period_time(0))

section("教师侧结算")
t_exp_before = teacher.experience.get(exp_id, 0)
t_state_before = teacher.status_data.get(education_constant.LEARN_STATE_ID, 0)
growth_handle.settle_teacher_class_gain(101, 45, 45)
check("教学相长：教师加该科经验与习得", teacher.experience.get(exp_id, 0) > t_exp_before and teacher.status_data.get(education_constant.LEARN_STATE_ID, 0) > t_state_before)
growth_handle.settle_teacher_class_gain(101, 45, 0)
check("add_time=0 不结算", True)

section("见学结算")
check("母亲没工作时科目为 0", growth_handle.get_mother_work_ability_id(102) == 0)
care_before = growth_handle.get_child_growth(202).care_point
growth_handle.settle_follow_mother_gain(202, 102, 60)
check("母亲无工作：只加照料值与好感", growth_handle.get_child_growth(202).care_point == care_before + education_constant.FOLLOW_MOTHER_CARE_POINT
      and child.favorability.get(102, 0) >= education_constant.FOLLOW_MOTHER_FAVORABILITY and mother.favorability.get(202, 0) >= education_constant.FOLLOW_MOTHER_FAVORABILITY)
cook_work = next(cid for cid in game_config.config_work_type if cid and game_config.config_work_type[cid].ability_id == 43)
mother.work.work_type = cook_work
mother.ability[43] = 4
m_exp_id = growth_handle.get_subject_exp_id(43)
exp_before = child.experience.get(m_exp_id, 0)
growth_handle.settle_follow_mother_gain(202, 102, 60)
check("母亲有工作：学该岗位科目", child.experience.get(m_exp_id, 0) - exp_before == max(1, int(education_constant.FOLLOW_MOTHER_EXP_BASE * 2.0)))
check("见学不计入出勤", growth_handle.get_child_growth(202).attend_class_count == 0)
child.talent[28] = 1
exp_before = child.experience.get(m_exp_id, 0)
growth_handle.settle_follow_mother_gain(202, 102, 60)
check("停滞后见学收益减半", child.experience.get(m_exp_id, 0) - exp_before == max(1, int(education_constant.FOLLOW_MOTHER_EXP_BASE * 1.0)))
child.talent[28] = 0
growth_handle.settle_follow_mother_gain(202, 999, 60)
check("母亲不存在不报错", True)

section("成年结算")
g = growth_handle.get_child_growth(201)
g.personality_point = {}
text = growth_handle.settle_personality_talent(201)
check("全为 0：性格尚未定型", "尚未定型" in text)
g.personality_point = {0: 1.5, 1: -2.0, 2: 0.0}
text = growth_handle.settle_personality_talent(201)
check("正数选前者、负数选后者、0 不选", student.talent[271] == 1 and student.talent[272] == 0 and student.talent[273] == 1 and student.talent[274] == 0
      and student.talent[275] == 0 and student.talent[276] == 0, text)
check("文本列出定型的性格", "勤劳" in text and "脆弱" in text)
student.ability[43] = 3
career = growth_handle.get_career_suggestion_text(201)
check("职业倾向按最高科目反查岗位", "料理" in career and game_config.config_work_type[cook_work].name in career, career)
check("没有科目等级时为空串", growth_handle.get_career_suggestion_text(202) == "")
g.care_point = 60.0
check("照料值折算发育偏移", growth_handle.get_care_point_grow_bonus(201) == 12)
g.care_point = 500.0
check("发育偏移封顶", growth_handle.get_care_point_grow_bonus(201) == education_constant.CARE_POINT_CHEST_MAX_BONUS)
check("没有养成数据时偏移为 0", growth_handle.get_care_point_grow_bonus(301) == 0)

section("阶段与进度")
# 夹具的出生日要落在季月（Plan 32 §2.5-4）：游戏时钟只有 3 / 6 / 9 / 12 四个季月，born_days=120 这种写法出生在 5 月，真实时钟下不会出现。
#    今天 2026-09-07 09:00：萝莉 2025-09-10 出生（362 个日历天）、幼女 2026-03-09 出生（182 个日历天），两人的本阶段都从 2026-06-07 09:00 起
student.pregnancy.born_time = datetime.datetime(2025, 9, 10, 9, 0)
child.pregnancy.born_time = datetime.datetime(2026, 3, 9, 9, 0)
check("阶段读取", growth_handle.get_character_stage(201) == 103 and growth_handle.get_character_stage(202) == 102 and growth_handle.get_character_stage(301) == 0)
progress = growth_handle.get_stage_progress(202)
check("M1 幼女：幼女期 6/7 ~ 12/4 跳过 7、8、10、11 月共 57 个可游玩天，已过 30 个，进度约 52.6%（按日历天是 51.1%）", abs(progress - 30 * 100.0 / 57) < 0.01, progress)
check("成年干员进度 100", growth_handle.get_stage_progress(301) == 100.0)

section("养成数值读写口")
V = education_constant
g.attend_class_count = 8
g.absent_count = 2
check("出勤数", growth_handle.get_growth_value(201, V.GROWTH_VALUE_ATTEND) == 8 and growth_handle.get_growth_value(201, V.GROWTH_VALUE_ABSENT) == 2)
check("出勤率 80", growth_handle.get_growth_value(201, V.GROWTH_VALUE_ATTEND_RATE) == 80.0)
check("没养成数据：出勤率 100、档位 -1、其余 0", growth_handle.get_growth_value(301, V.GROWTH_VALUE_ATTEND_RATE) == 100.0
      and growth_handle.get_growth_value(301, V.GROWTH_VALUE_REPORT_GRADE) == V.REPORT_GRADE_NONE and growth_handle.get_growth_value(301, V.GROWTH_VALUE_CARE) == 0.0)
check("没成绩单：档位 -1", growth_handle.get_growth_value(201, V.GROWTH_VALUE_REPORT_GRADE) == V.REPORT_GRADE_NONE)
growth_handle.change_growth_value(201, V.GROWTH_VALUE_PERSONALITY_BASE + 3, 0.5)
check("性格倾向可增", growth_handle.get_growth_value(201, V.GROWTH_VALUE_PERSONALITY_BASE + 3) == 0.5)
growth_handle.set_growth_value(201, V.GROWTH_VALUE_PERSONALITY_BASE + 3, -1.0)
check("性格倾向可设", growth_handle.get_growth_value(201, V.GROWTH_VALUE_PERSONALITY_BASE + 3) == -1.0)
growth_handle.change_growth_value(201, V.GROWTH_VALUE_CARE, -9999)
check("照料值不为负", growth_handle.get_growth_value(201, V.GROWTH_VALUE_CARE) == 0.0)
growth_handle.change_growth_value(201, V.GROWTH_VALUE_ATTEND, 100)
check("出勤数不可被事件改写", growth_handle.get_growth_value(201, V.GROWTH_VALUE_ATTEND) == 8)
check("学期进度读口不依赖养成数据", 0.0 <= growth_handle.get_growth_value(301, V.GROWTH_VALUE_SEMESTER_PROGRESS) <= 100.0)

section("候选名单")
check("女儿名单 = 三阶段女儿", growth_handle.get_student_candidate_list() == [201, 202])
check("个人课表名单 = 学生岗（Plan 24 口径 1）", growth_handle.get_course_candidate_list() == [201, 202, 301])
baby = make_character(203, "婴儿", 152, daughter=True, stage=101, mother_id=102, born_days=10)
check("婴儿不进女儿名单", 203 not in growth_handle.get_student_candidate_list())
check("婴儿不在 npc_id_got（夹具与真实婴儿对齐，Plan 28 §3.9），学生岗也不进个人课表名单", 203 not in cache.npc_id_got and 203 not in growth_handle.get_course_candidate_list())
student.work.work_type = 0
check("女儿换岗后不在个人课表名单（只认学生岗）", 201 not in growth_handle.get_course_candidate_list())
# 换回学生岗：待炫耀只记学生岗（Plan 32 L20），下一段拿她验炫耀
student.work.work_type = education_constant.STUDENT_WORK_TYPE

section("待炫耀只记课程科目、只记幼女/萝莉期的女儿（第五轮）")
from Script.Design import handle_ability

for one in (student, adult):
    growth_handle.get_child_growth(one.cid).show_off_ability = {}
    for juel_id in list(one.juel):
        one.juel[juel_id] = 10 ** 7
    for exp_id_one in list(one.experience):
        one.experience[exp_id_one] = 10 ** 7
    handle_ability.gain_ability(one.cid)
student_show = growth_handle.get_child_growth(201).show_off_ability
check("学生岗的萝莉女儿：升了级的科目记进待炫耀", len(student_show) > 0, student_show)
check("萝莉女儿：只记课程科目（欲望、感觉之类的升级不记）", set(student_show) <= set(education_constant.SUBJECT_ABILITY_LIST), sorted(student_show))
check("成年学生：升级不记待炫耀（口上只写给女儿）", growth_handle.get_child_growth(301).show_off_ability == {}, growth_handle.get_child_growth(301).show_off_ability)

section("Plan 26 §3.1：性技科目的课堂只发理论经验")
E6 = education_constant
check("女学生可学的 7 门性技都映射到类型 12 的理论经验", all(game_config.config_experience[growth_handle.get_class_exp_id(a)].type == 12 for a in E6.SEX_CLASS_ABILITY_LIST))
check("映射表的键都是性技科目、覆盖女学生可学的 7 门", set(E6.SEX_SKILL_THEORY_EXP_ID) <= E6.SEX_SKILL_SUBJECT_SET and set(E6.SEX_CLASS_ABILITY_LIST) <= set(E6.SEX_SKILL_THEORY_EXP_ID))
check("7 种理论经验互不相同", len(set(E6.SEX_SKILL_THEORY_EXP_ID.values())) == len(E6.SEX_SKILL_THEORY_EXP_ID))
check("腰技没有理论经验 → 0（只给习得）", growth_handle.get_class_exp_id(76) == 0)
check("技能科目照旧取升级需求里的经验", all(growth_handle.get_class_exp_id(a) == growth_handle.get_subject_exp_id(a) for a in E6.SUBJECT_ABILITY_LIST if a not in E6.SEX_SKILL_SUBJECT_SET))
theory_student = make_character(205, "上舌技课的萝莉", 152, daughter=True, stage=103, mother_id=102)
set_time(period_time(3))
real_sex_exp = {growth_handle.get_subject_exp_id(a) for a in E6.SEX_SKILL_SUBJECT_SET} - {0}
growth_handle.settle_student_class_gain(205, 101, 71, E6.COURSE_TYPE_THEORY, 45)
check("学生上舌技课：口交理论经验增加，任何真实性交经验都是 0，没有口交初体验", theory_student.experience.get(171, 0) > 0 and all(theory_student.experience.get(e, 0) == 0 for e in real_sex_exp)
      and 2 not in theory_student.first_record.first_part_sex_dict)
teacher_sex_before = {e: teacher.experience.get(e, 0) for e in real_sex_exp}
teacher_theory_before = teacher.experience.get(171, 0)
growth_handle.settle_teacher_class_gain(101, 71, 45)
check("教师教舌技：理论经验增加、真实性交经验不变", teacher.experience.get(171, 0) > teacher_theory_before and all(teacher.experience.get(e, 0) == teacher_sex_before[e] for e in real_sex_exp))
theory_student.child_growth.last_attend_period = []
learn_before = theory_student.status_data.get(E6.LEARN_STATE_ID, 0)
exp_snapshot = dict(theory_student.experience)
growth_handle.settle_student_class_gain(205, 101, 76, E6.COURSE_TYPE_THEORY, 45)
check("腰技课只给习得、不给任何经验", theory_student.status_data.get(E6.LEARN_STATE_ID, 0) > learn_before and dict(theory_student.experience) == exp_snapshot)
remove_character(205)

section("Plan 26 §3.12：未成年且一门性技都没学会时不升技巧")
minor = make_character(206, "攒了珠的萝莉", 152, daughter=True, stage=103, mother_id=102)
minor.juel[E6.LEARN_STATE_ID] = 150
handle_ability.gain_ability(206)
check("萝莉 150 珠、没学过性技：技巧仍 0、珠一个不少", minor.ability[30] == 0 and minor.juel[E6.LEARN_STATE_ID] == 150, (minor.ability[30], minor.juel[E6.LEARN_STATE_ID]))
drawn_text.clear()
check("能力面板的说明写明未成年的额外条件", handle_ability.extra_ability_check(30, 206, draw_flag=True) == 0 and any("未成年干员至少要有一门子性技达到1级" in t for t in drawn_text))
minor.ability[70] = 1
handle_ability.gain_ability(206)
check("学会一门性技（指技 1 级）后：技巧照原规则升 1 级", minor.ability[30] == 1 and minor.juel[E6.LEARN_STATE_ID] == 50, (minor.ability[30], minor.juel[E6.LEARN_STATE_ID]))
grown_npc = make_character(207, "成年干员", 21)
grown_npc.juel[E6.LEARN_STATE_ID] = 150
handle_ability.gain_ability(207)
check("成年干员不受影响：150 珠照旧升技巧 1 级", grown_npc.ability[30] == 1)
remove_character(206)
remove_character(207)

section("Plan 29 §3.3（Plan 32 M1 起按可游玩天）：本阶段第几天（get_stage_day）")
# 出生日都落在季月（Plan 32 §2.5-4）。今天 2026-09-07 09:00；幼女、萝莉、少女的本阶段都从 2026-06-07 09:00 起，中间跳过 7、8 两个非季月
set_time(period_time(0))
student.pregnancy.born_time = datetime.datetime(2025, 9, 10, 9, 0)  # 萝莉：出生 362 个日历天，第 270 天是 2026-06-07
child.pregnancy.born_time = datetime.datetime(2026, 3, 9, 9, 0)  # 幼女：出生 182 个日历天，第 90 天是 2026-06-07
baby.pregnancy.born_time = datetime.datetime(2026, 6, 27, 9, 0)  # 婴儿：出生 72 个日历天
teen = make_character(208, "少女", 152, daughter=True, stage=104, mother_id=102)
teen.pregnancy.born_time = datetime.datetime(2025, 3, 14, 9, 0)  # 少女：出生 542 个日历天，第 450 天是 2026-06-07
check("各阶段起点：婴儿 0 / 幼女 90 / 萝莉 270 / 少女 450，成年干员 0",
      [growth_handle.get_stage_start_day(cid) for cid in (203, 202, 201, 208, 301)] == [0, 90, 270, 450, 0])
check("M1 萝莉期从 6/7 起：6/7 ~ 6/30 与 9/1 ~ 9/7 共 30 个可游玩天（按日历天会是 92）", growth_handle.get_stage_day(201) == 30, growth_handle.get_stage_day(201))
check("M1 幼女、少女同样从 6/7 起：30；婴儿 6/27 出生：6/27 ~ 6/30 与 9/1 ~ 9/7 共 10 个可游玩天（按日历天会是 72）",
      growth_handle.get_stage_day(202) == 30 and growth_handle.get_stage_day(208) == 30 and growth_handle.get_stage_day(203) == 10,
      [growth_handle.get_stage_day(cid) for cid in (202, 208, 203)])
check("成年干员与不存在的角色：0", growth_handle.get_stage_day(301) == 0 and growth_handle.get_stage_day(999) == 0)
student.pregnancy.born_time = datetime.datetime(2026, 3, 1, 9, 0)
check("有效天数低于本阶段起点（成长停滞解除前的近似）：夹到 0", growth_handle.get_stage_day(201) == 0)
student.pregnancy.born_time = datetime.datetime(2025, 9, 10, 9, 0)
check("M1 阶段进度 = 本阶段已过可游玩天 ÷ 本阶段总可游玩天：幼女、萝莉都是 30 / 57（6/7 ~ 12/4），少女 100",
      abs(growth_handle.get_stage_progress(202) - 30 * 100.0 / 57) < 0.01 and abs(growth_handle.get_stage_progress(201) - 30 * 100.0 / 57) < 0.01
      and growth_handle.get_stage_progress(208) == 100.0)
lolified = make_character(219, "萝莉化的干员", 21, stage=103)
check("M1 没有可认出生日的萝莉（不是女儿、born_time 为缺省的公元 1 年）：本阶段天数 0、进度按走完 100",
      lolified.pregnancy.born_time.year == 1 and growth_handle.get_stage_day(219) == 0 and growth_handle.get_stage_progress(219) == 100.0)
remove_character(219)
remove_character(208)

section("Plan 30：养成数值 24、judge_absent_this_period、judge_selected_cell_real")
no_growth = make_character(209, "没有养成数据的干员", 21)
g.skip_count = 3
check("养成数值 24 读累计翘课数；没有养成数据为 0", growth_handle.get_growth_value(201, V.GROWTH_VALUE_SKIP) == 3.0
      and growth_handle.get_growth_value(209, V.GROWTH_VALUE_SKIP) == 0.0 and no_growth.child_growth is None)
g.skip_count = 0
set_time(period_time(2))
g.last_absent_period = []
check("这一节没记缺课：False", not growth_handle.judge_absent_this_period(201, cache.game_time))
g.last_absent_period = [cache.game_time.toordinal(), 2]
_next_day = DEFAULT_TIME.date() + datetime.timedelta(days=1)
check("这一节记了缺课：同一节里任一时刻为 True；下一节、节次外、别的日期为 False",
      growth_handle.judge_absent_this_period(201, period_time(2) + datetime.timedelta(minutes=30)) and not growth_handle.judge_absent_this_period(201, period_time(3))
      and not growth_handle.judge_absent_this_period(201, DEFAULT_TIME.replace(hour=13)) and not growth_handle.judge_absent_this_period(201, period_time(2, _next_day)))
check("没有养成数据、角色不存在：False，且不惰性创建", not growth_handle.judge_absent_this_period(209, period_time(2))
      and not growth_handle.judge_absent_this_period(999, period_time(2)) and no_growth.child_growth is None)
g.last_absent_period = []
student.work.work_type = 152
clear_schedules()
schedule_handle.set_selected_course(201, 2, 3, E6.COURSE_TYPE_THEORY, ROOM1)
check("教室课：每周课表那一格空着（已停课）不算", not growth_handle.judge_selected_cell_real(201, 2, 3))
schedule_handle.set_class_cell(ROOM1, 2, 3, 45, 101)
check("每周课表排了课：算", growth_handle.judge_selected_cell_real(201, 2, 3))
schedule_handle.set_class_cell(ROOM1, 2, 3, 45, -1)
check("格子在、没排教师（降级自习）仍是一节课：算", growth_handle.judge_selected_cell_real(201, 2, 3))
student.work.work_type = 21
check("改了岗：课表残留也不算", not growth_handle.judge_selected_cell_real(201, 2, 3))
student.work.work_type = 152
check("没选课的格子、角色不存在：不算", not growth_handle.judge_selected_cell_real(201, 2, 4) and not growth_handle.judge_selected_cell_real(999, 2, 3))
_lockable_pe = next(p for p in E6.PE_PLACE_DATA if p in game_config.config_facility_open_name_to_cid)
_lockable_cid = game_config.config_facility_open_name_to_cid[_lockable_pe]
schedule_handle.set_selected_course(201, 2, 4, E6.COURSE_TYPE_PE, _lockable_pe)
check("体育课：场地开放时算", growth_handle.judge_selected_cell_real(201, 2, 4), _lockable_pe)
cache.rhodes_island.facility_open[_lockable_cid] = False
check("场地未开放：不算", not growth_handle.judge_selected_cell_real(201, 2, 4))
cache.rhodes_island.facility_open[_lockable_cid] = True
schedule_handle.set_selected_course(201, 2, 5, E6.COURSE_TYPE_INTEREST, E6.ENTERTAINMENT_PLAY_HOUSE)
check("兴趣课过家家：萝莉算", growth_handle.judge_selected_cell_real(201, 2, 5))
student.talent[103] = 0
student.talent[104] = 1
check("长成少女后活动条件不符：不算", not growth_handle.judge_selected_cell_real(201, 2, 5))
student.talent[104] = 0
student.talent[103] = 1
_read_cid = next(cid for cid in game_config.config_entertainment if game_config.config_entertainment[cid].class_ok
                 and schedule_handle.judge_interest_course_is_read_book({"course_type": E6.COURSE_TYPE_INTEREST, "target": cid}))
schedule_handle.set_selected_course(201, 2, 6, E6.COURSE_TYPE_INTEREST, _read_cid)
_saved_borrow = dict(cache.rhodes_island.book_borrow_dict)
for _book_id in cache.rhodes_island.book_borrow_dict:
    cache.rhodes_island.book_borrow_dict[_book_id] = 999
check("读书兴趣课：书库此刻借空仍算（是一时的状态；上课判定 judge_personal_course_valid 则判没课）",
      growth_handle.judge_selected_cell_real(201, 2, 6) and not schedule_handle.judge_personal_course_valid(201, {"course_type": E6.COURSE_TYPE_INTEREST, "target": _read_cid}))
cache.rhodes_island.book_borrow_dict.update(_saved_borrow)
for _p in (3, 4, 5, 6):
    schedule_handle.clear_selected_course(201, 2, _p)
clear_schedules()

section("Plan 31：养成数值 25、judge_have_course_type")
g.sex_class_count = 4
check("L12 养成数值 25 读累计实操课次数；没有养成数据为 0", growth_handle.get_growth_value(201, V.GROWTH_VALUE_SEX_CLASS) == 4.0
      and growth_handle.get_growth_value(209, V.GROWTH_VALUE_SEX_CLASS) == 0.0 and no_growth.child_growth is None)
g.sex_class_count = 0
schedule_handle.set_selected_course(201, 3, 0, E6.COURSE_TYPE_THEORY, ROOM1)
check("L11 理论课那一格已停课：不算有理论课", not growth_handle.judge_have_course_type(201, E6.COURSE_TYPE_THEORY))
schedule_handle.set_class_cell(ROOM1, 3, 0, 45, -1)
check("L11 每周课表排了课：有理论课，没有体育课", growth_handle.judge_have_course_type(201, E6.COURSE_TYPE_THEORY)
      and not growth_handle.judge_have_course_type(201, E6.COURSE_TYPE_PE))
student.work.work_type = 21
check("L11 改了岗：课表残留不算", not growth_handle.judge_have_course_type(201, E6.COURSE_TYPE_THEORY))
student.work.work_type = 152
schedule_handle.set_selected_course(201, 3, 1, E6.COURSE_TYPE_PE, _lockable_pe)
check("L11 体育课场地开放：有体育课", growth_handle.judge_have_course_type(201, E6.COURSE_TYPE_PE), _lockable_pe)
check("L11 没有养成数据、角色不存在都不算，且不惰性创建养成数据",
      not growth_handle.judge_have_course_type(209, E6.COURSE_TYPE_THEORY) and not growth_handle.judge_have_course_type(999, E6.COURSE_TYPE_THEORY)
      and no_growth.child_growth is None)
for _p in (0, 1):
    schedule_handle.clear_selected_course(201, 3, _p)
clear_schedules()
remove_character(209)

# ---------------------------------------------------------------------------
# Plan 32（第十三轮复查）
# ---------------------------------------------------------------------------
import calendar  # noqa: E402
import inspect  # noqa: E402

from Script.System.Official_Event_System import official_event_handle  # noqa: E402
from Script.System.Pregnancy_System import pregnancy_constant, pregnancy_handle  # noqa: E402

DT = datetime.datetime

section("Plan 32 M1：game_time.count_play_day（两个时刻之间的可游玩天数）")
check("M1 同一季月内：与日历天数相同", game_time.count_play_day(DT(2026, 9, 7, 6, 0), DT(2026, 9, 17, 6, 0)) == 10)
check("M1 跨过 10、11 月：9/7 06:00 → 12/1 00:05 是 23 天（9 月余下的 23 天多、12 月的 5 分钟；日历天 84）",
      game_time.count_play_day(DT(2026, 9, 7, 6, 0), DT(2026, 12, 1, 0, 5)) == 23 and game_time.count_day_for_datetime(DT(2026, 9, 7, 6, 0), DT(2026, 12, 1, 0, 5)) == 84)
check("M1 跨年跳过 1、2 月：12/31 12:00 → 次年 3/1 12:00 是 1 天（日历天 60）", game_time.count_play_day(DT(2026, 12, 31, 12, 0), DT(2027, 3, 1, 12, 0)) == 1)
check("M1 终点落在被跳过的月份：只数到季月末（9/7 06:00 → 10/15 是 23 天）", game_time.count_play_day(DT(2026, 9, 7, 6, 0), DT(2026, 10, 15)) == 23)
check("M1 整整一年：四个季月 31 + 30 + 30 + 31 = 122 天", game_time.count_play_day(DT(2026, 3, 1), DT(2027, 3, 1)) == 122)
check("M1 终点早于起点：0", game_time.count_play_day(DT(2026, 9, 17), DT(2026, 9, 7)) == 0)

section("Plan 32 M1：阶段进度按可游玩天（全年 122 个季月出生日期，用真实时钟 sub_time_now 逐日推进）")
_saved_time = cache.game_time
_saved_born = baby.pregnancy.born_time
_new_count = {}
_old_count = {}
for _month in (3, 6, 9, 12):
    for _day in range(1, calendar.monthrange(2026, _month)[1] + 1):
        # 孩子只在季月出生；06:00 出生，此后每天 00:05（跨天结算派养成事件的时刻）取样，直到有效成长天数满 90（长成幼女）
        baby.pregnancy.born_time = DT(2026, _month, _day, 6, 0)
        cache.game_time = DT(2026, _month, _day, 0, 5)
        _new_count[(_month, _day)] = 0
        _old_count[(_month, _day)] = 0
        for _step in range(200):
            game_time.sub_time_now(day=1)
            _grow_day = pregnancy_handle.get_child_grow_day(203)
            if _grow_day >= pregnancy_constant.REARING_COMPLETE_DAY:
                break
            if 30 <= growth_handle.get_stage_progress(203) < 75:
                _new_count[(_month, _day)] += 1
            # 对照：按日历天的旧口径（有效成长天数 ÷ 90）
            if 30 <= _grow_day * 100.0 / pregnancy_constant.REARING_COMPLETE_DAY < 75:
                _old_count[(_month, _day)] += 1
check("M1 枚举了全年 122 个季月出生日期", len(_new_count) == 122, len(_new_count))
check("M1 每个出生日期的婴儿中期窗口 [30%, 75%) 都有 12~14 个可游玩日（婴儿期共 28~31 个可游玩天）",
      min(_new_count.values()) >= 12 and max(_new_count.values()) <= 14, sorted(set(_new_count.values())))
check("M1 对照：按日历天的旧口径，83 / 122 个出生日期的婴儿中期一天都开不出来（季月交替那一夜进度跳约 68 个百分点）",
      sum(1 for one in _old_count.values() if one == 0) == 83, sum(1 for one in _old_count.values() if one == 0))

section("Plan 32 M1：9/7 出生的婴儿跨过季月交替，本阶段天数与进度只走一天")
baby.pregnancy.born_time = DT(2026, 9, 7, 6, 0)
cache.game_time = DT(2026, 9, 30, 0, 5)
_day_before = growth_handle.get_stage_day(203)
_progress_before = growth_handle.get_stage_progress(203)
_grow_before = pregnancy_handle.get_child_grow_day(203)
game_time.sub_time_now(day=1)
check("M1 真实时钟：9/30 的下一个可游玩日是 12/1", cache.game_time == DT(2026, 12, 1, 0, 5), cache.game_time)
check("M1 对照：成长天数（日历天）一夜 +62", pregnancy_handle.get_child_grow_day(203) - _grow_before == 62, pregnancy_handle.get_child_grow_day(203) - _grow_before)
check("M1 婴儿期 9/7 ~ 12/6 共 29 个可游玩天：本阶段第 22 → 23 天、进度 22/29 → 23/29（按日历天是 24.4% → 93.3%）",
      _day_before == 22 and growth_handle.get_stage_day(203) == 23
      and abs(_progress_before - 2200.0 / 29) < 0.01 and abs(growth_handle.get_stage_progress(203) - 2300.0 / 29) < 0.01,
      (_day_before, growth_handle.get_stage_day(203), _progress_before, growth_handle.get_stage_progress(203)))
baby.pregnancy.born_time = _saved_born
set_time(_saved_time)

section("Plan 32 M3：成年后改写性格倾向即重选这一对素质")
grown = make_character(210, "成年女儿", 21, daughter=True, stage=104, mother_id=102)
grown.pregnancy.born_time = DT(2025, 3, 14, 9, 0)
_g_grown = growth_handle.get_child_growth(210)
_g_grown.personality_point = {1: -1.0}
growth_handle.settle_personality_talent(210)
check("M3 前提：成年结算按倾向 -1 给了脆弱（273）、没有坚强（274）", grown.talent[273] == 1 and grown.talent[274] == 0)
official_event_handle.settle_official_event_option(E6.GRADUATION_EVENT_UID, 210, 0, 2)
check("M3 毕业典礼选「坐在台下，看着她自己走完全程」（提示「倾向：坚强」，+4）：倾向 -1 → 3，坚强落上、脆弱清掉（此前只加倾向值，素质仍是脆弱）",
      _g_grown.personality_point.get(1) == 3.0 and grown.talent[274] == 1 and grown.talent[273] == 0,
      (_g_grown.personality_point, grown.talent[274], grown.talent[273]))
growth_handle.change_growth_value(210, V.GROWTH_VALUE_PERSONALITY_BASE + 1, -3.0)
check("M3 倾向改回 0：两侧都不动（坚强仍在）", _g_grown.personality_point.get(1) == 0.0 and grown.talent[274] == 1 and grown.talent[273] == 0)
growth_handle.set_growth_value(210, V.GROWTH_VALUE_PERSONALITY_BASE + 1, -2.0)
check("M3 CVE 的 E 运算（set_growth_value）设成 -2：翻到脆弱、清掉坚强", grown.talent[273] == 1 and grown.talent[274] == 0)
official_event_handle.settle_official_event_option("萝莉38", 210, 0, 1)
check("M3 成年前入队、成年后才处理的萝莉 38（旧档队列里的残留）选「不问，让她自己去买」（倾向：坚强 +3）：倾向 -2 → 1，坚强落上",
      _g_grown.personality_point.get(1) == 1.0 and grown.talent[274] == 1 and grown.talent[273] == 0, (_g_grown.personality_point, grown.talent[274], grown.talent[273]))
check("M3 只重选改写的那一对：其余三对素质都没动", all(grown.talent[talent_id] == 0 for talent_id in (271, 272, 275, 276, 277, 278)))
_minor_before = (student.talent[274], student.talent[273])
growth_handle.change_growth_value(201, V.GROWTH_VALUE_PERSONALITY_BASE + 1, 10.0)
check("M3 未成年（萝莉）的女儿改倾向：只改倾向值、不选边（留到成年结算）",
      g.personality_point.get(1, 0.0) > 0 and (student.talent[274], student.talent[273]) == _minor_before, (g.personality_point.get(1), _minor_before))
growth_handle.change_growth_value(301, V.GROWTH_VALUE_PERSONALITY_BASE + 1, 5.0)
check("M3 成年学生（不是女儿）改倾向：不选边", adult.talent[274] == 0 and adult.talent[273] == 0)
no_growth_m3 = make_character(211, "没有养成数据的干员", 21)
check("M3 settle_personality_pair：返回写上的素质 id；性格对不存在、没有养成数据、角色不存在都返回 0，且不惰性创建养成数据",
      growth_handle.settle_personality_pair(210, 1) == 274 and growth_handle.settle_personality_pair(210, 9) == 0
      and growth_handle.settle_personality_pair(211, 0) == 0 and growth_handle.settle_personality_pair(999, 0) == 0 and no_growth_m3.child_growth is None)
check("M3 settle_adult_personality_pair：只对已成年的女儿生效（未成年女儿、成年学生返回 0）",
      growth_handle.settle_adult_personality_pair(210, 1) == 274 and growth_handle.settle_adult_personality_pair(201, 1) == 0
      and growth_handle.settle_adult_personality_pair(301, 1) == 0)
remove_character(210)
remove_character(211)

section("Plan 32 L28 / L27：基础值回落按课型常量取；557 的说明")
_class_gain_src = inspect.getsource(growth_handle.settle_student_class_gain)
check("L28 表里没有的课型回落到理论课的基础值，按课型常量取、不再写死 [0]",
      "COURSE_LEARN_BASE[0]" not in _class_gain_src and "COURSE_EXP_BASE[0]" not in _class_gain_src
      and "COURSE_LEARN_BASE[education_constant.COURSE_TYPE_THEORY]" in _class_gain_src and "COURSE_EXP_BASE[education_constant.COURSE_TYPE_THEORY]" in _class_gain_src)
check("L27 557 的说明改为「学生坐下听课时，本节教师判能到岗即结算」，不再写「晚到的学生」",
      "晚到的学生" not in growth_handle.settle_student_class_gain.__doc__ and "本节教师判能到岗" in growth_handle.settle_student_class_gain.__doc__)

section("Plan 32 实施复审补：M1 count_play_day 的起点落在被跳过的月份")
check("M1 起点落在被跳过的 11 月：11/26 09:00 → 12/3 00:05，11 月那一截整段不算，只数 12/1 00:00 起的 2 天 5 分钟 → 2（日历天 6）",
      game_time.count_play_day(DT(2026, 11, 26, 9, 0), DT(2026, 12, 3, 0, 5)) == 2
      and game_time.count_day_for_datetime(DT(2026, 11, 26, 9, 0), DT(2026, 12, 3, 0, 5)) == 6,
      game_time.count_play_day(DT(2026, 11, 26, 9, 0), DT(2026, 12, 3, 0, 5)))
check("M1 起点落在被跳过的 1 月、跨过 2 月：2027/1/10 → 3/2 12:00，只数 3/1 00:00 起的 1 天 12 小时 → 1（日历天 51）",
      game_time.count_play_day(DT(2027, 1, 10), DT(2027, 3, 2, 12, 0)) == 1 and game_time.count_day_for_datetime(DT(2027, 1, 10), DT(2027, 3, 2, 12, 0)) == 51,
      game_time.count_play_day(DT(2027, 1, 10), DT(2027, 3, 2, 12, 0)))
check("M1 起点、终点都落在被跳过的月份（10/5 → 11/20）：一个可游玩天都没有 → 0", game_time.count_play_day(DT(2026, 10, 5), DT(2026, 11, 20)) == 0)

section("Plan 32 实施复审补：M1 萝莉期 Growth|3_GE_70 的窗口（全年 122 个季月出生日期，用真实时钟 sub_time_now 逐日推进萝莉期）")
_saved_time = cache.game_time
_saved_born_loli = student.pregnancy.born_time
_loli_ge70 = {}
_loli_ge70_old = {}
_loli_span = pregnancy_constant.GROW_TO_GIRL_DAY - pregnancy_constant.GROW_TO_LOLI_DAY
for _month in (3, 6, 9, 12):
    for _day in range(1, calendar.monthrange(2026, _month)[1] + 1):
        # 06:00 出生，此后每天 00:05（跨天结算派养成事件的时刻）取样；只数有效成长天数落在萝莉期 [270, 450) 的可游玩日
        student.pregnancy.born_time = DT(2026, _month, _day, 6, 0)
        cache.game_time = DT(2026, _month, _day, 0, 5)
        _loli_ge70[(_month, _day)] = 0
        _loli_ge70_old[(_month, _day)] = 0
        for _step in range(400):
            game_time.sub_time_now(day=1)
            _grow_day = pregnancy_handle.get_child_grow_day(201)
            if _grow_day >= pregnancy_constant.GROW_TO_GIRL_DAY:
                break
            if _grow_day < pregnancy_constant.GROW_TO_LOLI_DAY:
                continue
            if growth_handle.get_stage_progress(201) >= 70:
                _loli_ge70[(_month, _day)] += 1
            # 对照：按日历天的旧口径（萝莉期已过的有效成长天 ÷ 180）
            if (_grow_day - pregnancy_constant.GROW_TO_LOLI_DAY) * 100.0 / _loli_span >= 70:
                _loli_ge70_old[(_month, _day)] += 1
student.pregnancy.born_time = _saved_born_loli
set_time(_saved_time)
check("M1 萝莉期：枚举了全年 122 个季月出生日期", len(_loli_ge70) == 122, len(_loli_ge70))
check("M1 萝莉期：每个出生日期都至少有 1 个阶段进度 ≥ 70 的可游玩日（萝莉桶 Growth|3_GE_70 的窗口都开得出来）",
      min(_loli_ge70.values()) >= 1, sorted(set(_loli_ge70.values())))
check("M1 萝莉期对照：按日历天的旧口径，26 / 122 个出生日期一天都到不了 70%（季月交替那一夜进度一跳就越过了这一段）",
      sum(1 for one in _loli_ge70_old.values() if one == 0) == 26, sum(1 for one in _loli_ge70_old.values() if one == 0))

section("Plan 32 实施复审补：M1 婴儿期阶段进度 ≥ 50 首次成立的可游玩日严格早于 ≥ 60（逐个出生日期，真实时钟）")
_saved_time = cache.game_time
_saved_born_baby = baby.pregnancy.born_time
_first_gap = {}
_old_strict = 0
for _month in (3, 6, 9, 12):
    for _day in range(1, calendar.monthrange(2026, _month)[1] + 1):
        baby.pregnancy.born_time = DT(2026, _month, _day, 6, 0)
        cache.game_time = DT(2026, _month, _day, 0, 5)
        _first = {50: None, 60: None}
        _first_old = {50: None, 60: None}
        for _step in range(200):
            game_time.sub_time_now(day=1)
            _grow_day = pregnancy_handle.get_child_grow_day(203)
            if _grow_day >= pregnancy_constant.REARING_COMPLETE_DAY:
                break
            _progress = growth_handle.get_stage_progress(203)
            _progress_old = _grow_day * 100.0 / pregnancy_constant.REARING_COMPLETE_DAY
            for _line in (50, 60):
                if _first[_line] is None and _progress >= _line:
                    _first[_line] = cache.game_time
                if _first_old[_line] is None and _progress_old >= _line:
                    _first_old[_line] = cache.game_time
        _first_gap[(_month, _day)] = game_time.count_play_day(_first[50], _first[60]) if _first[50] and _first[60] and _first[50] < _first[60] else 0
        if _first_old[50] and _first_old[60] and _first_old[50] < _first_old[60]:
            _old_strict += 1
baby.pregnancy.born_time = _saved_born_baby
set_time(_saved_time)
check("M1 婴儿期：122 个出生日期里，阶段进度 ≥ 50（婴儿 4「断奶的日子到了」）首次成立的可游玩日都严格早于 ≥ 60（婴儿 50「断奶之后」）",
      len(_first_gap) == 122 and all(_first_gap.values()), sorted(key for key, one in _first_gap.items() if not one)[:10])
check("M1 婴儿期：两条线首次成立都相隔 3 个可游玩日", set(_first_gap.values()) == {3}, sorted(set(_first_gap.values())))
check("M1 婴儿期对照：按日历天的旧口径，没有一个出生日期的 ≥ 50 严格早于 ≥ 60（两条线在季月交替那一夜一起越过，或那一夜直接跳出了婴儿期）",
      _old_strict == 0, _old_strict)

section("Plan 32 实施复审补：M1 成长加速药——本阶段的起点按「出生 + (阈值 − 加速天数)」换算（get_grow_day_time）")
set_time(DEFAULT_TIME)
accel = make_character(212, "吃过成长加速药的萝莉", 152, daughter=True, stage=103, mother_id=102)
_accel_born = DT(2025, 9, 10, 9, 0)
accel.pregnancy.born_time = _accel_born
accel.pregnancy.growth_acceleration_days = 30.0
_accel_start = _accel_born + datetime.timedelta(days=pregnancy_constant.GROW_TO_LOLI_DAY - 30)
_accel_end = _accel_born + datetime.timedelta(days=pregnancy_constant.GROW_TO_GIRL_DAY - 30)
check("M1 加速药前提：出生 362 个日历天 + 加速药 30 天 = 有效成长 392 天，仍在萝莉期；本阶段起点 2026-05-08 09:00 落在被跳过的 5 月、终点 2026-11-04 09:00",
      pregnancy_handle.get_child_grow_day(212) == 392 and growth_handle.get_character_stage(212) == 103
      and _accel_start == DT(2026, 5, 8, 9, 0) and _accel_end == DT(2026, 11, 4, 9, 0), (pregnancy_handle.get_child_grow_day(212), _accel_start, _accel_end))
check("M1 加速药：本阶段天数 = 从「出生 + (270 − 30) 天」数到此刻的可游玩天（6 月 30 天 + 9/1 ~ 9/7 的 6 天）= 36",
      growth_handle.get_stage_day(212) == game_time.count_play_day(_accel_start, cache.game_time) == 36,
      (growth_handle.get_stage_day(212), game_time.count_play_day(_accel_start, cache.game_time)))
check("M1 加速药：阶段进度 = 36 ÷ 起点到终点的可游玩天（6 月、9 月共 60）= 60%，养成数值 3 读到的是同一个数",
      game_time.count_play_day(_accel_start, _accel_end) == 60 and abs(growth_handle.get_stage_progress(212) - 60.0) < 0.01
      and abs(growth_handle.get_growth_value(212, V.GROWTH_VALUE_STAGE_PROGRESS) - 60.0) < 0.01, growth_handle.get_stage_progress(212))
accel.pregnancy.growth_acceleration_days = 30.7
check("M1 加速药天数带小数（30.7）按整数 30 算，与有效成长天数（get_child_grow_day）同口径",
      growth_handle.get_stage_day(212) == 36 and pregnancy_handle.get_child_grow_day(212) == 392, growth_handle.get_stage_day(212))
accel.pregnancy.growth_acceleration_days = 0.0
check("M1 加速药对照：同一出生日不吃药，本阶段从 2026-06-07 09:00 起、30 天", growth_handle.get_stage_day(212) == 30, growth_handle.get_stage_day(212))
remove_character(212)

section("Plan 32 实施复审补：M3 只重选被改写的那一对——另一对倾向不为 0、素质已清空，改写之后仍为 0")
grown_b = make_character(213, "成年女儿乙", 21, daughter=True, stage=104, mother_id=102)
grown_b.pregnancy.born_time = DT(2025, 3, 14, 9, 0)
_g_grown_b = growth_handle.get_child_growth(213)
_pair_talent = E6.PERSONALITY_PAIR_TALENT
_g_grown_b.personality_point = {0: 2.0, 1: -1.0, 2: -3.0}
for _pair_id in _pair_talent:
    for _talent_id in _pair_talent[_pair_id]:
        grown_b.talent[_talent_id] = 0
check("M3 前提：成年女儿乙四对素质都是 0；勤劳 / 懒散一对倾向 +2、热情 / 孤僻一对 -3（逐对选边的话这两对都会写上）",
      growth_handle.get_character_stage(213) == 104 and all(grown_b.talent[_talent_id] == 0 for _pair_id in _pair_talent for _talent_id in _pair_talent[_pair_id]))
growth_handle.change_growth_value(213, V.GROWTH_VALUE_PERSONALITY_BASE + 1, 4.0)
check("M3 只重选改写的那一对：坚强 / 脆弱一对 -1 → +3，落上坚强；倾向 +2 的勤劳 / 懒散、-3 的热情 / 孤僻两对素质仍为 0（原「其余三对都没动」在它们本就为 0、倾向也为 0 时恒真）",
      grown_b.talent[_pair_talent[1][0]] == 1 and grown_b.talent[_pair_talent[1][1]] == 0
      and all(grown_b.talent[_talent_id] == 0 for _pair_id in (0, 2, 3) for _talent_id in _pair_talent[_pair_id]),
      {_talent_id: grown_b.talent[_talent_id] for _pair_id in _pair_talent for _talent_id in _pair_talent[_pair_id]})
growth_handle.set_growth_value(213, V.GROWTH_VALUE_PERSONALITY_BASE + 3, -1.0)
check("M3 set_growth_value 同理：改写开放 / 羞耻一对只落羞耻一侧，勤劳 / 懒散、热情 / 孤僻两对仍为 0，坚强不动",
      grown_b.talent[_pair_talent[3][1]] == 1 and grown_b.talent[_pair_talent[3][0]] == 0 and grown_b.talent[_pair_talent[1][0]] == 1
      and all(grown_b.talent[_talent_id] == 0 for _pair_id in (0, 2) for _talent_id in _pair_talent[_pair_id]),
      {_talent_id: grown_b.talent[_talent_id] for _pair_id in _pair_talent for _talent_id in _pair_talent[_pair_id]})
check("M3 对照：勤劳 / 懒散一对的倾向确实为正，单独对它逐对选边（settle_personality_pair）就会写上勤劳",
      growth_handle.settle_personality_pair(213, 0) == _pair_talent[0][0] and grown_b.talent[_pair_talent[0][0]] == 1)
remove_character(213)

finish()
