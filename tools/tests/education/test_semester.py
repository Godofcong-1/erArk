# -*- coding: UTF-8 -*-
"""semester_handle：学期时间、本学期出勤、成绩档位、学期切换、成绩单历史"""
from _bootstrap import *  # noqa: F401,F403

clear_schedules()
mother = make_character(102, "母亲", 0)
student = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102, born_days=300)
adult = make_character(301, "成年学生", 152)

section("学期时间")
set_time(datetime.datetime(2026, 9, 7, 9, 0))
check("当前学期 (2026, 9)", tuple(game_time.get_now_semester()) == (2026, 9))
check("学期名含秋季", "秋季" in semester_handle.get_semester_name(2026, 9))
check("9 月学期 30 天、2 月学期 28 天", semester_handle.get_semester_day_total(2026, 9) == 30 and semester_handle.get_semester_day_total(2026, 2) == 28)
check("第 7 天进度约 20.7%", abs(semester_handle.get_semester_progress() - 6 * 100.0 / 29) < 0.01, semester_handle.get_semester_progress())
check("剩余 23 天", semester_handle.get_semester_left_day() == 23)
check("未过半", not semester_handle.judge_semester_half_passed())
check("抬头含「第 7 / 30 天」", "7 / 30" in semester_handle.get_semester_head_text(), semester_handle.get_semester_head_text())
set_time(datetime.datetime(2026, 9, 20, 9, 0))
check("第 20 天已过半", semester_handle.judge_semester_half_passed())
set_time(datetime.datetime(2026, 9, 30, 9, 0))
check("最后一天进度 100、剩余 0", semester_handle.get_semester_progress() == 100.0 and semester_handle.get_semester_left_day() == 0)
set_time(datetime.datetime(2026, 9, 7, 9, 0))

section("本学期出勤与档位")
check("没养成数据 → (0, 0)", semester_handle.get_semester_attend(301) == (0, 0) and semester_handle.get_semester_attend(999) == (0, 0))
g = growth_handle.get_child_growth(201)
g.attend_class_count = 10
g.absent_count = 3
g.semester_base_attend = 4
g.semester_base_absent = 1
check("本学期 = 累计 - 基线", semester_handle.get_semester_attend(201) == (6, 2))
g.semester_base_attend = 99
check("基线超过累计时夹到 0", semester_handle.get_semester_attend(201)[0] == 0)
g.semester_base_attend = 4
check("出勤率：0/0 算 100", semester_handle.get_semester_attend_rate(0, 0) == 100)
check("出勤率：7/3 → 70", semester_handle.get_semester_attend_rate(7, 3) == 70)
E = education_constant
check("无课可评", semester_handle.get_report_grade(0, 0, 5) == E.REPORT_GRADE_NO_CLASS)
check("90% + 升 2 门 → 优秀", semester_handle.get_report_grade(9, 1, 2) == E.REPORT_GRADE_EXCELLENT)
check("90% 但只升 1 门 → 良好", semester_handle.get_report_grade(9, 1, 1) == E.REPORT_GRADE_GOOD)
check("89% 差一点不算优秀", semester_handle.get_report_grade(89, 11, 5) == E.REPORT_GRADE_GOOD)
check("70% 整 → 良好", semester_handle.get_report_grade(7, 3, 0) == E.REPORT_GRADE_GOOD)
check("60% → 待努力", semester_handle.get_report_grade(6, 4, 5) == E.REPORT_GRADE_POOR)

section("等级增量")
g.semester_base_ability = {45: 1, 43: 2}
student.ability[45] = 3
student.ability[43] = 2
student.ability[40] = 1
check("只含真涨了的科目", semester_handle.get_semester_level_change(201) == {45: [1, 3], 40: [0, 1]})
check("没养成数据为空", semester_handle.get_semester_level_change(301) == {})
check("最高科目", semester_handle.get_top_ability(201) == (45, 3))
check("一门都没学过 (-1, 0)", semester_handle.get_top_ability(301) == (-1, 0))
text = semester_handle.get_level_change_text({45: [1, 3], 40: [0, 1]})
check("增量文本按能力 id 排序并带评级", text.startswith(game_config.config_ability[40].name) and "→" in text, text)
check("空增量文本为空串", semester_handle.get_level_change_text({}) == "")

section("学期切换")
g.semester_id = []
g.semester_base_attend = 0
g.semester_base_absent = 0
g.semester_base_ability = {}
g.attend_class_count = 0
g.absent_count = 0
student.ability[45] = 1
check("第一次记账只立基线", semester_handle.settle_semester_change() == [] and g.semester_id == [2026, 9] and g.semester_base_ability.get(45) == 1)
check("同一学期再调不出成绩单", semester_handle.settle_semester_change() == [] and g.report_card_history == [])
g.attend_class_count = 9
g.absent_count = 1
student.ability[45] = 3
student.ability[43] = 4
set_time(datetime.datetime(2026, 12, 1, 9, 0))
report_list = semester_handle.settle_semester_change()
check("切学期出成绩单", report_list == [201])
card = semester_handle.get_last_report_card(201)
check("成绩单属于刚结束的 9 月学期", card.get("year") == 2026 and card.get("month") == 9, card)
check("成绩单内容：出勤 9/1、升 2 门、优秀", card.get("attend") == 9 and card.get("absent") == 1 and len(card.get("level_change", {})) == 2
      and card.get("grade") == E.REPORT_GRADE_EXCELLENT, card)
check("成绩单 flag 置位", g.report_card_flag)
check("基线重置到当前", g.semester_id == [2026, 12] and g.semester_base_attend == 9 and g.semester_base_ability.get(45) == 3)
check("再调一次幂等", semester_handle.settle_semester_change() == [] and len(g.report_card_history) == 1)
check("成年学生没被凭空建出养成数据", adult.child_growth is None)
check("终身累计不被污染", g.attend_class_count == 9)
g.attend_class_count = 12
check("新学期听课 3 节", semester_handle.get_semester_attend(201) == (3, 0))

section("成绩单历史")
for index in range(10):
    semester_handle.push_report_card(201, {"year": 2020, "month": 3, "grade": index})
check("历史上限 8 份", len(g.report_card_history) == E.REPORT_CARD_HISTORY_MAX)
check("留的是最近的", g.report_card_history[-1]["grade"] == 9 and g.report_card_history[0]["grade"] == 2)
check("get_last_report_card 取最后一份", semester_handle.get_last_report_card(201)["grade"] == 9)
check("没有历史时为空 dict / 空列表", semester_handle.get_last_report_card(301) == {} and semester_handle.get_report_card_history(999) == [])
text = semester_handle.get_report_card_text(201, card, True)
check("成绩单正文含姓名、出勤与评定", "女儿A" in text and "出勤" in text and "评定" in text and "尚未结束" not in text)
text = semester_handle.get_report_card_text(201, semester_handle.build_report_card(201), False)
check("学期中途的正文标「尚未结束」", "尚未结束" in text)

finish()
