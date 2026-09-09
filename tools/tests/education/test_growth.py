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
student.talent[28] = 1
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 45)
check("停滞后经验减半", student.experience.get(exp_id, 0) - exp_before == int(education_constant.COURSE_EXP_BASE[0] * 1.0))
student.talent[28] = 0
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, 101, 45, education_constant.COURSE_TYPE_THEORY, 0)
check("add_time=0 不结算", student.experience.get(exp_id, 0) == exp_before and student.child_growth.attend_class_count == 2)
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, -1, 45, education_constant.COURSE_TYPE_THEORY, 45)
check("自习：经验按自习基础值", student.experience.get(exp_id, 0) - exp_before == education_constant.SELF_STUDY_EXP_BASE)
exp_before = student.experience.get(exp_id, 0)
growth_handle.settle_student_class_gain(201, -1, 45, education_constant.COURSE_TYPE_INTERN, 45)
check("实习无导师：见习基础值减半", student.experience.get(exp_id, 0) - exp_before == max(1, education_constant.COURSE_EXP_BASE[education_constant.COURSE_TYPE_INTERN] // 2))

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
check("阶段读取", growth_handle.get_character_stage(201) == 103 and growth_handle.get_character_stage(202) == 102 and growth_handle.get_character_stage(301) == 0)
check("judge_is_child", growth_handle.judge_is_child(202) and not growth_handle.judge_is_child(301))
progress = growth_handle.get_stage_progress(202)
check("幼女出生 120 天：阶段进度约 16.7%", abs(progress - (120 - 90) * 100.0 / 180) < 0.01, progress)
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
check("个人课表名单 = 学生岗 ∪ 女儿", growth_handle.get_course_candidate_list() == [201, 202, 301])
baby = make_character(203, "婴儿", 152, daughter=True, stage=101, mother_id=102, born_days=10)
check("婴儿不进女儿名单", 203 not in growth_handle.get_student_candidate_list())
check("婴儿是学生岗时进个人课表名单", 203 in growth_handle.get_course_candidate_list())
student.work.work_type = 0
check("女儿换岗后仍在个人课表名单（并集）", 201 in growth_handle.get_course_candidate_list())

finish()
