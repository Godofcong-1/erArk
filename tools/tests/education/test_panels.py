# -*- coding: UTF-8 -*-
"""面板：页签容器、全局课表、个人课表、日程模板、养成总览、学生页签分页、临时课编辑、Web 适配器冒烟"""
from _bootstrap import *  # noqa: F401,F403
from Script.System.Education_System import class_schedule_panel, course_select_panel, growth_panel, schedule_template_panel, student_tab_bar

open_all_classroom()
clear_schedules()
ROOM1 = _("理论教室一")
ROOM_P = _("实践教室一")
teacher = make_character(101, "教师甲", 151)
teacher.ability[45] = 5
teacher_b = make_character(103, "教师乙", 151)
teacher_c = make_character(104, "教师丙", 151)
teacher_d = make_character(105, "教师丁", 151)
mother = make_character(102, "母亲", 0)
daughter_list = [make_character(201 + i, f"女儿{i + 1:02d}", 152, daughter=True, stage=103, mother_id=102, born_days=300) for i in range(11)]
adult_student = make_character(301, "成年学生", 152)
# 容器每轮都会按设施等级刷新房间开放状态，最小 fixture 没有完整的罗德岛数据，钉死它
class_schedule_panel.basement.get_base_updata = lambda *a, **k: None
E = education_constant
W = 190

section("页签容器")
captured = {}


def fake_askfor(return_list, *a, **k):
    captured["rl"] = list(return_list)
    return _("返回")


flow_handle.askfor_all = fake_askfor
container = class_schedule_panel.Education_Manage_Panel(W)
container.draw()
rl = captured["rl"]
check("首屏有 [返回]，回到场景面板", _("返回") in rl and cache.now_panel_id == constant.Panel.IN_SCENE)
check("另三个页签可点", all(f"\n{name}" in rl for name in (_("个人课表"), _("日程模板"), _("养成总览"))))
check("全局课表：教室页签 + 63 个格子 + 两个按钮", sum(1 for r in rl if r.startswith("\nROOM_")) == 9 and sum(1 for r in rl if r.startswith("\nCELL_")) == 63
      and _("一键排课") in rl and _("清空本教室") in rl)
check("return_list 无重复", len(rl) == len(set(rl)), [r for r in rl if rl.count(r) > 1])
check("学期抬头已画出", any("学期" in t for t in drawn_text))
for tab in (_("个人课表"), _("日程模板"), _("养成总览")):
    container.change_panel(tab)
    drawn_text.clear()
    container.draw()
    rl = captured["rl"]
    check(f"页签「{tab}」可画且无重复 return", len(rl) == len(set(rl)) and _("返回") in rl)

section("全局课表面板")
panel = class_schedule_panel.Class_Schedule_Panel(W)
rl = []
panel.draw_page(rl)
check("默认页签落在理论教室一", panel.now_room == ROOM1)
panel.handle_yrn(f"\nROOM_{ROOM_P}")
rl = []
panel.draw_page(rl)
check("切换教室", panel.now_room == ROOM_P)
panel.handle_yrn(_("一键排课"))
check("一键排课排上了", any(schedule_handle.get_class_cell(ROOM1, d, p) for d in range(5) for p in range(9)))
panel.now_room = ROOM1
panel.handle_yrn(_("清空本教室"))
check("清空本教室", not any(schedule_handle.get_class_cell(ROOM1, d, p) for d in range(7) for p in range(9)))
check("别的教室没被清", any(schedule_handle.get_class_cell(_("理论教室二"), d, p) for d in range(5) for p in range(9)))
# 编辑一格：脚本化的 askfor —— 选科目 → 选教师
answers = []


def scripted_askfor(return_list, *a, **k):
    captured["rl"] = list(return_list)
    for want in answers:
        for option in return_list:
            if want(option):
                answers.remove(want)
                return option
    return return_list[-1]


flow_handle.askfor_all = scripted_askfor
answers[:] = [lambda o: o == "0", lambda o: o == "101"]
rl = []
panel.draw_page(rl)
cell_key = next(r for r in rl if r.startswith("\nCELL_0_0"))
panel.handle_yrn(cell_key)
check("点格子 → 选科目 → 选教师 → 写入课表", schedule_handle.get_class_cell(ROOM1, 0, 0) == [E.SUBJECT_ABILITY_LIST[0], 101])
answers[:] = [lambda o: o == _("清空本格")]
panel.handle_yrn(cell_key)
check("清空本格", schedule_handle.get_class_cell(ROOM1, 0, 0) is None)
answers[:] = [lambda o: o == _("取消")]
panel.handle_yrn(cell_key)
check("取消不写入", schedule_handle.get_class_cell(ROOM1, 0, 0) is None)

section("临时实操课编辑")
panel.now_room = ROOM_P
rl = []
panel.draw_page(rl)
cell_key = next(r for r in rl if r.startswith("\nCELL_2_3"))
answers[:] = [lambda o: o == _("排一节性技实操课"), lambda o: o == "ADD_MUST", lambda o: o == "MUST_201", lambda o: o == "DONE", lambda o: o == "OK"]
panel.handle_yrn(cell_key)
date_ordinal = sex_class_handle.get_date_ordinal_by_week_day(2, 3)
temp_class = sex_class_handle.get_temp_class(date_ordinal, 3)
check("排了一节临时课并指定必修", temp_class is not None and temp_class["classroom"] == ROOM_P and temp_class["must_attend"] == [201])
check("临时课不写进全局课表", cache.rhodes_island.class_schedule.get(ROOM_P, {}).get(2, {}).get(3) is None)
answers[:] = [lambda o: o == _("排一节性技实操课"), lambda o: o == "DEL"]
panel.handle_yrn(cell_key)
check("删除本节临时课", sex_class_handle.get_temp_class(date_ordinal, 3) is None)
answers[:] = [lambda o: o == "0", lambda o: o == _("取消")]
panel.handle_yrn(cell_key)
check("选教师时取消不写入", schedule_handle.get_class_cell(ROOM_P, 2, 3) is None)
flow_handle.askfor_all = fake_askfor

section("个人课表面板与分页")
cs = course_select_panel.Course_Select_Panel(W)
rl = []
cs.draw_page(rl)
check("名单 = 学生岗 ∪ 女儿，12 人", cs.student_list == [201 + i for i in range(11)] + [301])
check("首页 7 个页签按钮 + 下一页", sum(1 for r in rl if r.startswith("\nSTU_")) == 7 and E.STUDENT_PAGE_NEXT in rl and E.STUDENT_PAGE_PREV not in rl)
check("63 个格子 + 日程行 + 三个按钮", sum(1 for r in rl if r.startswith("\nMYCELL_")) == 63 and "EDIT_SCHEDULE" in rl and _("一键选课") in rl and _("复制") in rl and _("清空") in rl)
cs.handle_yrn(E.STUDENT_PAGE_NEXT)
rl = []
cs.draw_page(rl)
check("第 2 页 4 人", sum(1 for r in rl if r.startswith("\nSTU_")) == 4 and E.STUDENT_PAGE_NEXT not in rl)
cs.handle_yrn("\nSTU_301")
rl = []
cs.draw_page(rl)
check("选中成年学生且停在第 2 页", cs.now_student == 301 and cs.tab_bar.page == 1)
cs.handle_yrn(_("一键选课"))
auto_schedule.auto_fill_class_schedule()
cs.handle_yrn(_("一键选课"))
check("成年学生也能一键选课", cache.character_data[301].child_growth is not None and any(schedule_handle.get_selected_course(301, d, p) for d in range(5) for p in range(9)))
answers[:] = [lambda o: o == "COPY_201"]
flow_handle.askfor_all = scripted_askfor
cs.handle_yrn(_("复制"))
check("复制到其他学生", schedule_handle.get_selected_course(201, 0, 0) == schedule_handle.get_selected_course(301, 0, 0) and schedule_handle.get_selected_course(201, 0, 0) is not None)
cs.handle_yrn(_("清空"))
check("清空当前学生", not any(schedule_handle.get_selected_course(301, d, p) for d in range(7) for p in range(9)))
cs.handle_yrn("\nSTU_201")
rl = []
cs.draw_page(rl)
cell_key = next(r for r in rl if r.startswith("\nMYCELL_0_1"))
schedule_handle.set_class_cell(ROOM_P, 0, 1, 43, 101)
answers[:] = [lambda o: o == f"CLS_{ROOM_P}"]
cs.handle_yrn(cell_key)
check("点格子选教室课", schedule_handle.get_selected_course(201, 0, 1) == [E.COURSE_TYPE_PRACTICE, ROOM_P])
answers[:] = [lambda o: o == f"CT_{E.COURSE_TYPE_PE}", lambda o: o == f"TG_{_('木桩房')}"]
cs.handle_yrn(cell_key)
check("点格子选体育课", schedule_handle.get_selected_course(201, 0, 1) == [E.COURSE_TYPE_PE, _("木桩房")])
answers[:] = [lambda o: o == _("清空本格")]
cs.handle_yrn(cell_key)
check("清空本格", schedule_handle.get_selected_course(201, 0, 1) is None)
cell_text = cs._get_cell_text(201, 0, 0)
check("格子文本：科目/教室", "/" in cell_text and any(room in cell_text for room in schedule_handle.get_classroom_list()), cell_text)
check("未排课格子为 --", cs._get_cell_text(201, 6, 8) == "--")
answers[:] = [lambda o: o == "CHANGE_TEMPLATE", lambda o: o == "TPL_2" or o.endswith("2") and "TPL" in o, lambda o: o == _("返回日程")]
cs.handle_yrn("EDIT_SCHEDULE")
check("日程编辑能进能出", True)
flow_handle.askfor_all = fake_askfor

section("养成总览面板")
gp = growth_panel.Growth_Panel(W)
rl = []
drawn_text.clear()
gp.draw_page(rl)
check("名单只有女儿，11 人分两页", gp.student_list == [201 + i for i in range(11)] and E.STUDENT_PAGE_NEXT in rl)
check("画出阶段 / 科目 / 出勤 / 性格四栏", all(any(key in t for t in drawn_text) for key in ("当前阶段", "科目水平", "出勤", "性格倾向")))
g = growth_handle.get_child_growth(201)
for index in range(3):
    semester_handle.push_report_card(201, {"year": 2026, "month": 3 * (index + 1), "attend": 5, "absent": 0, "rate": 100, "level_change": {}, "grade": 1})
rl = []
gp.draw_page(rl)
check("多份成绩单：有翻页按钮", E.REPORT_CARD_PREV in rl and E.REPORT_CARD_NEXT not in rl)
gp.handle_yrn(E.REPORT_CARD_PREV)
rl = []
gp.draw_page(rl)
check("翻到上一学期后两个方向都有", E.REPORT_CARD_PREV in rl and E.REPORT_CARD_NEXT in rl and gp.report_card_index == 1)
gp.handle_yrn("\nGSTU_202")
check("切人重置成绩单下标", gp.now_student == 202 and gp.report_card_index == -1)
g.skip_class_flag = True
g.show_off_ability = {45: 2}
g.report_card_flag = True
gp.handle_yrn("\nGSTU_201")
drawn_text.clear()
gp.draw_page([])
check("待处理栏：成绩单 / 炫耀 / 翘课三条都出", any("成绩单待查看" in t for t in drawn_text) and any("炫耀" in t for t in drawn_text) and any("翘课" in t for t in drawn_text))
check("return_list 无重复", (lambda r: len(r) == len(set(r)))(rl))

section("日程模板面板")
tp = schedule_template_panel.Schedule_Template_Panel(W)
rl = []
drawn_text.clear()
tp.draw_page(rl)
check("四套预设都列出", all(any(name in t for t in drawn_text) for name in E.PRESET_TEMPLATE_NAME.values()))
check("有新建与批量套用入口", len(rl) >= 5)

section("Student_Tab_Bar 组件")
bar = student_tab_bar.Student_Tab_Bar(W, "\nX_")
lst = [201 + i for i in range(11)] + [301]
bar.jump_to(lst, 301)
check("jump_to 定位到第 2 页", bar.page == 1)
bar.jump_to(lst, 999)
check("不存在的人不动页码", bar.page == 1)
check("只认自己的前缀", bar.get_student_by_yrn("\nSTU_205", lst) == -1 and bar.get_student_by_yrn("\nX_205", lst) == 205)
bar.page = 99
rl = []
bar.draw(lst, 201, rl)
check("越界夹回末页", bar.page == 1)
bar.page = 0
rl = []
bar.draw(lst[:3], 201, rl)
check("单页不画翻页", E.STUDENT_PAGE_NEXT not in rl and E.STUDENT_PAGE_PREV not in rl and len(rl) == 2)

section("Web 适配器冒烟")
from Script.System.Web_Draw_System import web_draw_adapter

web_draw_adapter.apply_web_adapters()
cache.current_draw_elements = []
problem = []
for name, panel in (("全局课表", class_schedule_panel.Class_Schedule_Panel(W)), ("个人课表", course_select_panel.Course_Select_Panel(W)),
                    ("养成总览", growth_panel.Growth_Panel(W)), ("日程模板", schedule_template_panel.Schedule_Template_Panel(W))):
    try:
        panel.draw_page([])
    except Exception as error:
        problem.append((name, repr(error)))
check("Web 模式下四个子页都能画", not problem, problem)
check("产生了 Web 元素", len(cache.current_draw_elements) > 50, len(cache.current_draw_elements))
check("元素带类型字段", all(isinstance(one, dict) and "type" in one for one in cache.current_draw_elements[:20]), cache.current_draw_elements[:2])

finish()
