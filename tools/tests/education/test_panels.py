# -*- coding: UTF-8 -*-
"""面板：页签容器、全局课表、个人课表、日程模板、养成总览、选人按钮（通用 NPC 选择面板）、临时课编辑、Web 适配器冒烟"""
from _bootstrap import *  # noqa: F401,F403
from Script.System.Education_System import class_schedule_panel, course_select_panel, growth_panel, schedule_template_panel

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

section("必修名单含成年学生岗（Plan 25 §3.7）")
from Script.Design import instuct_judege  # noqa: E402

_orig_judge = instuct_judege.calculation_instuct_judege
flow_handle.askfor_all = scripted_askfor
answers[:] = [lambda o: o == "DONE"]
panel._select_must_attend([], ROOM_P, 2, 3)
check("成年学生不满足 H 模式实行值 → 不列出，女儿照常列出", "MUST_301" not in captured["rl"] and "MUST_201" in captured["rl"], captured["rl"])
instuct_judege.calculation_instuct_judege = lambda *a, **k: (1, 0, "")
answers[:] = [lambda o: o == "DONE"]
panel._select_must_attend([], ROOM_P, 2, 3)
check("满足实行值的成年学生岗列入必修名单", "MUST_301" in captured["rl"], captured["rl"])
check("非学生岗（教师）不在必修名单", not any(r in captured["rl"] for r in ("MUST_101", "MUST_103", "MUST_104", "MUST_105", "MUST_102")))
instuct_judege.calculation_instuct_judege = _orig_judge
flow_handle.askfor_all = fake_askfor

section("个人课表面板与选人")
cs = course_select_panel.Course_Select_Panel(W)
rl = []
drawn_text.clear()
cs.draw_page(rl)
check("名单 = 全部学生岗（含成年学生），12 人", cs.student_list == [201 + i for i in range(11)] + [301])
check("首屏只有顶在行首的[选择学生]（不写「尚未选择」），没有人名页签与格子，也不画周表", E.SELECT_STUDENT_RETURN in rl and not any(r.startswith("\nSTU_") or r.startswith("\nMYCELL_") for r in rl)
      and cs.now_student == -1 and "EDIT_SCHEDULE" not in rl and not any("尚未选择学生" in t for t in drawn_text) and any(t == "[选择学生]" for t in drawn_text))
answers[:] = [lambda o: o == "女儿03"]
flow_handle.askfor_all = scripted_askfor
cs.handle_yrn(E.SELECT_STUDENT_RETURN)
check("通用选择面板列出了预筛名单（12 人，不含教师）", "女儿01" in captured["rl"] and "成年学生" in captured["rl"] and "教师甲" not in captured["rl"] and _("返回") in captured["rl"])
check("点人名 → 选中", cs.now_student == 203)
rl = []
cs.draw_page(rl)
check("选中后：63 个格子 + 日程行 + 三个按钮", sum(1 for r in rl if r.startswith("\nMYCELL_")) == 63 and "EDIT_SCHEDULE" in rl and _("一键选课") in rl and _("复制") in rl and _("清空") in rl)
answers[:] = [lambda o: o == _("返回")]
cs.handle_yrn(E.SELECT_STUDENT_RETURN)
check("选人时点[返回] → 选中不变", cs.now_student == 203)
answers[:] = [lambda o: o == "成年学生"]
cs.handle_yrn(E.SELECT_STUDENT_RETURN)
check("换成成年学生", cs.now_student == 301)
flow_handle.askfor_all = fake_askfor
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
answers[:] = [lambda o: o == "女儿01"]
cs.handle_yrn(E.SELECT_STUDENT_RETURN)
check("换回女儿01", cs.now_student == 201)
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

section("养成总览面板与选人")
gp = growth_panel.Growth_Panel(W)
rl = []
drawn_text.clear()
gp.draw_page(rl)
check("名单只有女儿，11 人；首屏未选人、只有[选择学生]、不画正文", gp.student_list == [201 + i for i in range(11)] and E.SELECT_STUDENT_RETURN in rl and gp.now_student == -1
      and not any(r.startswith("\nGSTU_") for r in rl) and not any("科目水平" in t for t in drawn_text))
answers[:] = [lambda o: o == "女儿01"]
flow_handle.askfor_all = scripted_askfor
gp.handle_yrn(E.SELECT_STUDENT_RETURN)
check("通用选择面板只列女儿", "女儿11" in captured["rl"] and "成年学生" not in captured["rl"] and "教师甲" not in captured["rl"])
flow_handle.askfor_all = fake_askfor
check("选中女儿01", gp.now_student == 201)
rl = []
drawn_text.clear()
gp.draw_page(rl)
check("画出阶段 / 科目 / 出勤 / 性格四栏", all(any(key in t for t in drawn_text) for key in ("当前阶段", "科目水平", "出勤", "性格倾向")))
stage_text = next((t for t in drawn_text if "母亲" in t), "")
check("阶段行：母亲名、距少女还有 150 天（日历天）、预计日期", mother.name in stage_text and "150" in stage_text and "日历天" in stage_text and "预计" in stage_text and "少女" in stage_text, stage_text)
cache.character_data[201].talent[E.GROWTH_STOP_TALENT_ID] = 1
drawn_text.clear()
gp.draw_page([])
check("成长停滞时写明阶段不会推进", any("停滞" in t and "不会推进" in t for t in drawn_text))
cache.character_data[201].talent[E.GROWTH_STOP_TALENT_ID] = 0
cache.character_data[201].relationship.mother_id = -1
drawn_text.clear()
gp.draw_page([])
check("没有母亲时显示未知", any(_("未知") in t and "母亲" in t for t in drawn_text))
cache.character_data[201].relationship.mother_id = 102
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
answers[:] = [lambda o: o == "女儿02"]
flow_handle.askfor_all = scripted_askfor
gp.handle_yrn(E.SELECT_STUDENT_RETURN)
check("切人重置成绩单下标", gp.now_student == 202 and gp.report_card_index == -1)
g.skip_class_flag = True
g.show_off_ability = {45: 2}
g.report_card_flag = True
answers[:] = [lambda o: o == "女儿01"]
gp.handle_yrn(E.SELECT_STUDENT_RETURN)
flow_handle.askfor_all = fake_askfor
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

section("student_select 组件")
from Script.System.Education_System import student_select

rl = []
drawn_text.clear()
check("未选人：返回 False、只登记选人哨兵、行首直接是[选择学生]而不是「尚未选择」、画提示", not student_select.draw_select_student_line(W, -1, rl) and rl == [E.SELECT_STUDENT_RETURN]
      and drawn_text[0] == "[选择学生]" and not any("尚未选择学生" in t for t in drawn_text) and any("点击[选择学生]" in t for t in drawn_text))
rl = []
drawn_text.clear()
check("已选人：返回 True、显示当前学生", student_select.draw_select_student_line(W, 201, rl) and rl == [E.SELECT_STUDENT_RETURN] and any("女儿01" in t for t in drawn_text))
answers[:] = [lambda o: o == "女儿05"]
flow_handle.askfor_all = scripted_askfor
check("按返回值反查选中者（无 cmd_func 的桩）", student_select.select_student([201, 202, 205], "t", "", 201) == 205)
answers[:] = [lambda o: o == _("返回")]
check("点[返回]原样返回当前选中者", student_select.select_student([201, 202, 205], "t", "", 202) == 202)
check("名单里不存在的角色被跳过、不报错", student_select.select_student([201, 999], "t", "", -1) in (-1, 201))
flow_handle.askfor_all = fake_askfor

section("Plan 26 §3.6：被今天的临时实操课顶替的格子")
clear_schedules()
set_time(period_time(0))
_weekday = cache.game_time.weekday()
schedule_handle.set_class_cell(ROOM_P, _weekday, 4, 43, 101)
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 4, ROOM_P, 70)
panel = class_schedule_panel.Class_Schedule_Panel(W)
panel.now_room = ROOM_P
drawn_text.clear()
panel.draw_page([])
check("周表上覆盖格带「[临]」", any(t.startswith("[临]") for t in drawn_text), [t for t in drawn_text if "临" in t][:3])
flow_handle.askfor_all = scripted_askfor
answers[:] = [lambda o: o == _("清空本格")]
drawn_text.clear()
panel._edit_cell(ROOM_P, _weekday, 4)
check("选科目页写明今天由临时课顶替、每周课表这一格是什么", any("临时实操课" in t and "每周课表这一格" in t for t in drawn_text))
check("清空按钮写成「清空每周课表这一格」", any("清空每周课表这一格" in t for t in drawn_text))
check("清掉的是每周课表那一格，临时课还在", schedule_handle.get_class_cell(ROOM_P, _weekday, 4, include_temp=False) is None
      and schedule_handle.get_class_cell(ROOM_P, _weekday, 4) == [70, 0])
answers[:] = [lambda o: o == _("取消")]
drawn_text.clear()
panel._edit_cell(ROOM_P, _weekday, 5)
check("没被覆盖的格子仍是「清空本格」、没有说明行", any(t == _("[清空本格]") for t in drawn_text) and not any("临时实操课" in t for t in drawn_text))

section("Plan 26 L4：排实操课页提示该节已在别的教室排了")
_date = sex_class_handle.get_date_ordinal_by_week_day(2, 6)
sex_class_handle.set_temp_class(_date, 6, _("大礼堂"), 71, must_attend=[201])
answers[:] = [lambda o: o == "BACK"]
drawn_text.clear()
panel._edit_sex_class(ROOM_P, 2, 6)
check("提示「该节已在大礼堂排了实操课，确定后改到本教室」", any("该节已在" in t and _("大礼堂") in t for t in drawn_text))
answers[:] = [lambda o: o == "OK"]
panel._edit_sex_class(ROOM_P, 2, 6)
check("确定后那一节改到本教室、必修名单沿用", sex_class_handle.get_temp_class(_date, 6)["classroom"] == ROOM_P and sex_class_handle.get_temp_class(_date, 6)["must_attend"] == [201])
flow_handle.askfor_all = fake_askfor
clear_schedules()

section("Plan 26 §3.8：个人课表选目标时，未开放与条件不符的置灰")
cs = course_select_panel.Course_Select_Panel(W)
play_house_name = game_config.config_entertainment[E.ENTERTAINMENT_PLAY_HOUSE].name
drawn_text.clear()
cs._select_target(301, 0, 0, E.COURSE_TYPE_INTEREST)
check("成年学生看过家家：标「（条件不符）」、不是按钮", any(t == _(" {0}（条件不符）").format(play_house_name) for t in drawn_text)
      and not any(t == _("[{0}]").format(play_house_name) for t in drawn_text))
drawn_text.clear()
cs._select_target(201, 0, 0, E.COURSE_TYPE_INTEREST)
check("萝莉看过家家：可选", any(t == _("[{0}]").format(play_house_name) for t in drawn_text))
pool = _("游泳池")
cache.rhodes_island.facility_open[game_config.config_facility_open_name_to_cid[pool]] = False
drawn_text.clear()
cs._select_target(201, 0, 0, E.COURSE_TYPE_PE)
check("未解锁的游泳池：体育课标「（未开放）」（此前永远不会出现）", any(t == _(" {0}（未开放）").format(pool) for t in drawn_text))
open_all_classroom()

section("Plan 26 §3.3：课堂模式下的邀请名单按实操课门槛筛")
from Script.System.Sex_System import group_sex_panel  # noqa: E402
from Script.UI.Panel import common_select_NPC  # noqa: E402

_invite_captured = {}
_orig_select_func = common_select_NPC.common_select_npc_button_list_func


def capture_invite(now_panel, *a, **k):
    """
    记下邀请名单并直接返回，让面板的 while 循环在 fake_askfor 返回「返回」后退出
    Keyword arguments:
    now_panel -- 面板的名单控制对象
    Return arguments:
    tuple -- (return_list, other_return_list, select_state)
    """
    _invite_captured["list"] = [one[0] for one in now_panel.text_list]
    return [_("返回")], [], {}


common_select_NPC.common_select_npc_button_list_func = capture_invite
flow_handle.askfor_all = fake_askfor
cache.sex_class_mode = True
cache.group_sex_mode = True
schedule_handle.set_class_cell(ROOM_P, 3, 8, 74, -1)
schedule_handle.set_selected_course(202, 3, 8, E.COURSE_TYPE_PRACTICE, ROOM_P)
move_to(0, classroom_path(ROOM_P))
group_sex_panel.Edit_Group_Sex_Temple_Panel(W).show_invite_npc_panel()
invite_list = _invite_captured.get("list", [])
check("课堂模式：修过性技课的学生岗女儿在名单里，教师与非学生的母亲不在", 202 in invite_list and 101 not in invite_list and 102 not in invite_list, invite_list)
check("没修过性技课、也没被点名的学生不在", 203 not in invite_list, invite_list)
cache.sex_class_mode = False
cache.group_sex_mode = False
common_select_NPC.common_select_npc_button_list_func = _orig_select_func
move_to(0, SCENE_DORM)
clear_schedules()

section("Plan 27 §3.1 / L5：选择活动面板的「未开放」标注、周日实习课只画一句提示")
from Script.Core import text_handle  # noqa: E402

flow_handle.askfor_all = scripted_askfor
answers[:] = []
_game_room_cid = game_config.config_facility_open_name_to_cid[_("黄澄澄游戏室")]
cache.rhodes_island.facility_open[_game_room_cid] = False
drawn_text.clear()
check("选择活动：点[取消]返回 None", schedule_template_panel.Schedule_Template_Panel(W)._select_activity() is None)
_play_house_button = _("[{0}]").format(_("{0}（{1}，未开放）").format(play_house_name, schedule_template_handle.get_activity_age_limit_text(E.ENTERTAINMENT_PLAY_HOUSE)))
check("游戏室没解锁：过家家的按钮标「限幼女/萝莉，未开放」，仍是按钮（可选）", _play_house_button in drawn_text, [t for t in drawn_text if play_house_name in t])
check("按钮宽度不超过每格 31 列", text_handle.get_text_index(_play_house_button) <= int(W / 6), text_handle.get_text_index(_play_house_button))
check("地点开放的活动不带「未开放」", _("[{0}]").format(_("下棋")) in drawn_text and not any("未开放" in t and _("下棋") in t for t in drawn_text))
cache.rhodes_island.facility_open[_game_room_cid] = True
drawn_text.clear()
schedule_template_panel.Schedule_Template_Panel(W)._select_activity()
check("解锁之后不再标注", not any("未开放" in t for t in drawn_text))
drawn_text.clear()
course_select_panel.Course_Select_Panel(W)._select_target(201, 6, 0, E.COURSE_TYPE_INTERN)
check("周日排实习课：只画「周日全岛无人上班」一句，不再接着画「本节次没有可选的内容」（L5）", any("周日全岛无人上班" in t for t in drawn_text)
      and not any("本节次没有可选的内容" in t for t in drawn_text))
flow_handle.askfor_all = fake_askfor

section("Plan 28：个人课表格子的「/条件不符」「/未开放」、必修名单的顶替标记、待处理写学期名、选择活动没有照料卵")
from Script.UI.Panel import character_info_head  # noqa: E402
from Script.System.Pregnancy_System import pregnancy_constant  # noqa: E402

clear_schedules()
_pool_cid = game_config.config_facility_open_name_to_cid[pool]
_cell_width = max(8, int((W - 14) / len(E.WEEK_NAME)))
cs = course_select_panel.Course_Select_Panel(W)
schedule_handle.set_selected_course(301, 0, 0, E.COURSE_TYPE_INTEREST, E.ENTERTAINMENT_PLAY_HOUSE)
_text_need = cs._get_cell_text(301, 0, 0)
check("成年学生排着过家家兴趣课：格子写「[兴]过家家/条件不符」（此前照常写，上课判定却已不认这节课）",
      _text_need == _("{0}/条件不符").format("[{0}]{1}".format(E.COURSE_TYPE_SHORT[E.COURSE_TYPE_INTEREST], play_house_name)), _text_need)
cache.rhodes_island.facility_open[_pool_cid] = False
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_PE, pool)
_text_open = cs._get_cell_text(201, 0, 0)
check("体育课排在未解锁的游泳池：格子写「[体]游泳池/未开放」", _text_open == _("{0}/未开放").format("[{0}]{1}".format(E.COURSE_TYPE_SHORT[E.COURSE_TYPE_PE], pool)), _text_open)
cache.rhodes_island.facility_open[_pool_cid] = True
check("解锁后不再标注", cs._get_cell_text(201, 0, 0) == "[{0}]{1}".format(E.COURSE_TYPE_SHORT[E.COURSE_TYPE_PE], pool), cs._get_cell_text(201, 0, 0))
_too_wide = []
for _cid in game_config.config_entertainment:
    if game_config.config_entertainment[_cid].class_ok:
        _one = _("{0}/条件不符").format("[{0}]{1}".format(E.COURSE_TYPE_SHORT[E.COURSE_TYPE_INTEREST], game_config.config_entertainment[_cid].name))
        if text_handle.get_text_index(_one) > _cell_width:
            _too_wide.append(_one)
for _place in E.PE_PLACE_DATA:
    _one = _("{0}/未开放").format("[{0}]{1}".format(E.COURSE_TYPE_SHORT[E.COURSE_TYPE_PE], _place))
    if text_handle.get_text_index(_one) > _cell_width:
        _too_wide.append(_one)
check("全部兴趣课的「/条件不符」、全部体育场地的「/未开放」都放得进一格（{0} 列）".format(_cell_width), not _too_wide, _too_wide)
schedule_handle.clear_selected_course(301, 0, 0)
schedule_handle.clear_selected_course(201, 0, 0)

ROOM2 = _("理论教室二")
for _cid in (201, 202, 203, 204, 205):
    schedule_handle.clear_selected_course(_cid, 2, 3)
schedule_handle.set_selected_course(201, 2, 3, E.COURSE_TYPE_PE, _("木桩房"))
schedule_handle.set_selected_course(202, 2, 3, E.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_class_cell(ROOM2, 2, 3, 45, 101)
schedule_handle.set_selected_course(203, 2, 3, E.COURSE_TYPE_THEORY, ROOM2)
schedule_handle.set_selected_course(205, 2, 3, E.COURSE_TYPE_PE, pool)
cache.rhodes_island.facility_open[_pool_cid] = False
flow_handle.askfor_all = scripted_askfor
answers[:] = [lambda o: o == "DONE"]
drawn_text.clear()
class_schedule_panel.Class_Schedule_Panel(W)._select_must_attend([], ROOM_P, 2, 3)
flow_handle.askfor_all = fake_askfor
cache.rhodes_island.facility_open[_pool_cid] = True
_replace_line = next((t for t in drawn_text if "会顶替原本的课" in t), "")
_pe_text = character_info_head.get_course_text({"course_type": E.COURSE_TYPE_PE, "target": _("木桩房")})
check("必修名单：排了体育课的学生标「*」，明细写「女儿01→体育课·木桩房」（此前只看教室课，不标）",
      "[  女儿01*]" in drawn_text and "女儿01→{0}".format(_pe_text) in _replace_line, (_replace_line, [t for t in drawn_text if "女儿01" in t]))
check("每周课表上已停课的教室课不标、不进明细（此前标「*」）", "[  女儿02]" in drawn_text and "女儿02" not in _replace_line, _replace_line)
check("确有的教室课照标，明细写教室与科目", "[  女儿03*]" in drawn_text and "女儿03→{0}的{1}".format(ROOM2, game_config.config_ability[45].name) in _replace_line, _replace_line)
check("上不成的个人式课（未解锁的游泳池）不标；没排课的不标", "[  女儿05]" in drawn_text and "女儿05" not in _replace_line and "[  女儿04]" in drawn_text, _replace_line)
clear_schedules()
for _cid in (201, 202, 203, 205):
    schedule_handle.clear_selected_course(_cid, 2, 3)

_g201 = growth_handle.get_child_growth(201)
_g201.report_card_flag = True
drawn_text.clear()
growth_panel.Growth_Panel(W)._draw_flag(201)
_last = semester_handle.get_last_report_card(201)
_want = _("{0}的成绩单待查看（用「检查成绩单」指令）").format(semester_handle.get_semester_name(_last["year"], _last["month"]))
check("养成总览的待处理写明是哪个学期的成绩单（此前写「本学期」，待查看的其实是刚结束那一学期的）", any(_want in t for t in drawn_text)
      and not any("本学期成绩单" in t for t in drawn_text), [t for t in drawn_text if "成绩单" in t])
_g201.report_card_flag = False
_g210 = growth_handle.get_child_growth(210)
_g210.report_card_flag = True
drawn_text.clear()
growth_panel.Growth_Panel(W)._draw_flag(210)
check("一份成绩单都还没有时写「新的成绩单待查看」", any(_("新的成绩单待查看（用「检查成绩单」指令）") in t for t in drawn_text), [t for t in drawn_text if "成绩单" in t])
_g210.report_card_flag = False

flow_handle.askfor_all = scripted_askfor
answers[:] = []
drawn_text.clear()
schedule_template_panel.Schedule_Template_Panel(W)._select_activity()
flow_handle.askfor_all = fake_askfor
_tend_name = game_config.config_entertainment[pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID].name
check("选择活动里没有照料卵（Plan 28 §3.3）", drawn_text and not any(_tend_name in t for t in drawn_text), [t for t in drawn_text if _tend_name in t])

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
