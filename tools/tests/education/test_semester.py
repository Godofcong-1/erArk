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

section("Plan 29 §3.1 / L2：只排个人式课的孩子按档评；改了岗的萝莉照出成绩单并写明不全的理由（用户拍板）")
set_time(datetime.datetime(2026, 12, 7, 9, 0))
g.report_card_history = []
g.last_attend_period = []
semester_handle.reset_semester_baseline(201, [2026, 12])
student.work.work_type = 152
check("settle_course_attend：记上一节、同一节再记不重复", growth_handle.settle_course_attend(201) and not growth_handle.settle_course_attend(201)
      and semester_handle.get_semester_attend(201) == (1, 0))
set_time(datetime.datetime(2026, 12, 7, 13, 0))
check("节次外不记", not growth_handle.settle_course_attend(201))
set_time(datetime.datetime(2026, 12, 7, 9, 0))
check("不是女儿也不是学生岗的不记", not growth_handle.settle_course_attend(102) and mother.child_growth is None)
card = semester_handle.build_report_card(201)
check("只排体育 / 兴趣课、一学期没缺过：按档评（出勤率 100%、良好），不再是「无课可评」", card["grade"] == E.REPORT_GRADE_GOOD and card["reason"] == "", card)
g.absent_count += 1
card = semester_handle.build_report_card(201)
check("缺过一节：按实际出勤算（50%、待努力），不再是出勤率 0%", card["rate"] == 50 and card["grade"] == E.REPORT_GRADE_POOR, card)
g.absent_count -= 1
student.work.work_type = 21
card = semester_handle.build_report_card(201)
check("改岗（岗位 21）的萝莉：照按改岗前上过的课评档，快照带不全的理由、写明改任的岗位",
      card["grade"] == E.REPORT_GRADE_GOOD and card["attend"] == 1 and card["reason"] and game_config.config_work_type[21].name in card["reason"], card)
text = semester_handle.get_report_card_text(201, card, True)
check("成绩单正文写出理由", "※ " in text and card["reason"] in text, text)
student.work.work_type = 0
check("岗位为无：理由写「不再担任学生」", "不再担任学生" in semester_handle.build_report_card(201)["reason"])
student.work.work_type = 21
set_time(datetime.datetime(2027, 3, 1, 9, 0))
report_list = semester_handle.settle_semester_change()
check("学期切换：改岗萝莉照出成绩单，理由随快照冻结", report_list == [201] and semester_handle.get_last_report_card(201)["reason"]
      and semester_handle.get_last_report_card(201)["grade"] == E.REPORT_GRADE_GOOD, semester_handle.get_last_report_card(201))
student.work.work_type = 152
check("Plan 30：学期初在岗位 21、此刻回到学生岗 → 理由写「中途回到了学生岗」（此前改回学生岗就当没改过，不写理由）",
      "中途回到了学生岗" in semester_handle.build_report_card(201)["reason"], semester_handle.build_report_card(201)["reason"])
semester_handle.reset_semester_baseline(201, [2027, 3])
text = semester_handle.get_report_card_text(201, semester_handle.build_report_card(201), False)
check("学生岗（学期初也是学生岗）：理由为空、正文没有那一行；旧档没有 reason 键的快照照常出正文",
      semester_handle.build_report_card(201)["reason"] == "" and "※ " not in text and "※ " not in semester_handle.get_report_card_text(201, {"year": 2026, "month": 9}, True))

section("Plan 30 §3.1：成绩单的缺课含翘课")
_day = datetime.date(2027, 3, 8)
set_time(period_time(0, _day))
semester_handle.reset_semester_baseline(201, [2027, 3])
check("学期基线记下学期初的岗位", g.semester_base_work_type == 152)
g.last_absent_period = []
g.last_attend_period = []
_skip_before = g.skip_count
growth_handle.settle_course_attend(201)
for _p in (1, 2, 3):
    set_time(period_time(_p, _day))
    class_ai.settle_absent(201, by_skip=True)
card = semester_handle.build_report_card(201)
check("上 1 节、翘 3 节：出勤 1 / 缺课 3、25%、待努力（此前翘课不计缺课，出勤率 100%、良好）",
      card["attend"] == 1 and card["absent"] == 3 and card["rate"] == 25 and card["grade"] == E.REPORT_GRADE_POOR and g.skip_count == _skip_before + 3, card)
check("节次外不记缺课", (set_time(DEFAULT_TIME.replace(hour=13)), class_ai.settle_absent(201, by_skip=True))[1] is False and g.skip_count == _skip_before + 3)

section("Plan 30 §3.3：改岗理由按学期初的岗位分情形")
_w21 = game_config.config_work_type[21].name


def reason_of(base_work_type: int, now_work_type: int, have_record: bool) -> str:
    """
    按「学期初岗位 / 结算时岗位 / 本学期有无出勤记录」取理由
    Keyword arguments:
    base_work_type -- 学期初的岗位，-1 为未知
    now_work_type -- 结算时的岗位
    have_record -- 本学期是否有一节出勤
    Return arguments:
    str -- 理由文本
    """
    g.semester_base_work_type = base_work_type
    student.work.work_type = now_work_type
    g.semester_base_attend = g.attend_class_count - (1 if have_record else 0)
    g.semester_base_absent = g.absent_count
    return semester_handle.get_report_incomplete_reason(201)


check("学期初学生岗 → 结算时岗位 21：「本学期改任了」（有无记录都是）", reason_of(152, 21, True).startswith(_("{0}本学期改任了{1}").format(student.name, _w21))
      and "本学期改任了" in reason_of(152, 21, False))
check("学期初学生岗 → 结算时岗位为无：「不再担任学生」", "不再担任学生" in reason_of(152, 0, False))
check("整学期在岗位 21、本学期没有记录：「本学期担任…，没有上课」（此前写「本学期改任了」）", reason_of(21, 21, False) == _("{0}本学期担任{1}，没有上课").format(student.name, _w21),
      reason_of(21, 21, False))
check("整学期岗位为无：「本学期不是学生，没有上课」", reason_of(0, 0, False) == _("{0}本学期不是学生，没有上课").format(student.name))
check("学期初岗位 21、结算时岗位 21 但本学期有记录（中途进过学生岗又出去）：按「改任了」写", "本学期改任了" in reason_of(21, 21, True))
check("学期初岗位 21 → 结算时学生岗：「中途回到了学生岗」", "中途回到了学生岗" in reason_of(21, 152, True))
check("学期初与结算时都是学生岗：没有理由", reason_of(152, 152, True) == "")
check("旧档学期初未知（-1）→ 结算时岗位 21：有记录写「改任了」、没有记录写「担任…，没有上课」",
      "本学期改任了" in reason_of(-1, 21, True) and "没有上课" in reason_of(-1, 21, False))
check("旧档学期初未知 → 结算时学生岗：没有理由", reason_of(-1, 152, False) == "")

section("Plan 30 §3.3 Q1（用户拍板）：成年后整学期不在学生岗的女儿不再出成绩单，检查成绩单只对有待查看的开放")
grown_away = make_character(207, "离开学生岗的成年女儿", 21, daughter=True, stage=104, mother_id=102, born_days=500)
grown_student = make_character(208, "仍在学生岗的成年女儿", 152, daughter=True, stage=104, mother_id=102, born_days=500)
set_time(datetime.datetime(2027, 6, 1, 9, 0))
student.work.work_type = 21
semester_handle.reset_semester_baseline(201, [2027, 6])
g.report_card_flag = False
check("第一次记账：成年女儿照立基线、记下学期初岗位", semester_handle.settle_semester_change() == []
      and growth_handle.get_child_growth(207).semester_id == [2027, 6] and growth_handle.get_child_growth(207).semester_base_work_type == 21)
check("judge_adult_out_of_school：成年且不在学生岗才成立（萝莉改岗不算）", semester_handle.judge_adult_out_of_school(207)
      and not semester_handle.judge_adult_out_of_school(208) and not semester_handle.judge_adult_out_of_school(201) and not semester_handle.judge_adult_out_of_school(999))
set_time(datetime.datetime(2027, 9, 1, 9, 0))
report_list = semester_handle.settle_semester_change()
_g207 = growth_handle.get_child_growth(207)
check("成年且整学期不在学生岗：不出成绩单、不置待查看、不进学期结束名单，只把基线挪到新学期（此前每学期一份 0/0「本学期改任了」）",
      207 not in report_list and _g207.report_card_history == [] and not _g207.report_card_flag and _g207.semester_id == [2027, 9], report_list)
check("成年仍在学生岗的女儿：照出", 208 in report_list and len(growth_handle.get_child_growth(208).report_card_history) == 1)
check("萝莉整学期不在学生岗：照出（Plan 29 口径），理由「本学期担任…，没有上课」",
      201 in report_list and semester_handle.get_last_report_card(201)["reason"] == _("{0}本学期担任{1}，没有上课").format(student.name, _w21),
      semester_handle.get_last_report_card(201).get("reason"))
growth_handle.get_child_growth(208).report_card_flag = False
growth_handle.get_child_growth(208).attend_class_count += 2
grown_student.work.work_type = 21
set_time(datetime.datetime(2027, 12, 1, 9, 0))
report_list = semester_handle.settle_semester_change()
_last_208 = semester_handle.get_last_report_card(208)
check("成年女儿学期中途才离开学生岗（本学期有出勤）：照出最后一份，理由「本学期改任了」，待查看置位",
      208 in report_list and _last_208.get("attend") == 2 and "本学期改任了" in _last_208.get("reason", "") and growth_handle.get_child_growth(208).report_card_flag, _last_208)
check("检查成绩单：有待查看时仍可用，看完就不可用；萝莉改了岗照旧可用",
      semester_handle.judge_report_card_checkable(208) and not semester_handle.judge_report_card_checkable(207) and semester_handle.judge_report_card_checkable(201)
      and not semester_handle.judge_report_card_checkable(999))
growth_handle.get_child_growth(208).report_card_flag = False
check("看完之后（flag 清掉）：不可用", not semester_handle.judge_report_card_checkable(208))
_g207.semester_base_work_type = -1
set_time(datetime.datetime(2028, 3, 1, 9, 0))
report_list = semester_handle.settle_semester_change()
check("旧档学期初岗位未知（-1）、本学期 0/0 的成年女儿同样不出；以前的成绩单照旧留着",
      207 not in report_list and _g207.report_card_history == [] and 208 not in report_list and len(growth_handle.get_child_growth(208).report_card_history) == 2,
      report_list)
student.work.work_type = 152
remove_character(207)
remove_character(208)

finish()
