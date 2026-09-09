# -*- coding: UTF-8 -*-
"""存档兼容：CHILD_GROWTH 字段回填、成绩单迁移、罗德岛新字段、真实存档只读载入"""
from _bootstrap import *  # noqa: F401,F403

section("CHILD_GROWTH 字段级回填")
mother = make_character(102, "母亲", 0)
student_a = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102)
student_b = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102)
adult = make_character(301, "成年干员", 21)
ga = growth_handle.get_child_growth(201)
gb = growth_handle.get_child_growth(202)
for name in ("semester_id", "report_card_history", "schedule_override", "follow_mother_flag", "last_absent_period"):
    delattr(ga, name)
    delattr(gb, name)
ga.last_report_card = {"year": 2026, "month": 6, "grade": 1}
del adult.child_growth
del student_b.pregnancy.prenatal_point
save_handle._normalize_loaded_save_paths(cache)
default_names = set(vars(game_type.CHILD_GROWTH()))
check("两个孩子的字段集合与新结构体一致", set(vars(ga)) == default_names and set(vars(gb)) == default_names, set(vars(ga)) ^ default_names)
check("dict / list 不被两个角色共享", ga.report_card_history is not gb.report_card_history and ga.schedule_override is not gb.schedule_override)
check("旧的单份成绩单并进历史列表并删掉旧字段", ga.report_card_history == [{"year": 2026, "month": 6, "grade": 1}] and not hasattr(ga, "last_report_card"))
check("没有养成数据的角色补出 child_growth = None", adult.child_growth is None)
check("母亲侧胎教字段回填", student_b.pregnancy.prenatal_point == 0.0)

section("教育区娱乐改编号的读档迁移（175~178 → 152~155）")
migrated = [save_handle._migrate_entertainment_cid(value) for value in (175, 176, 177, 178, 152, 58, 0, None, True)]
check("迁移函数：旧编号换新、新编号与无关值不动", migrated == [152, 153, 154, 155, 152, 58, 0, None, True], migrated)
cache.rhodes_island.child_schedule_template = {9: {"name": "旧模板", "slot": {0: 178, 1: 58, 2: 177}}, 10: {"name": "空模板", "slot": {}}}
count = save_handle._migrate_child_schedule_template(cache.rhodes_island)
check("模板侧：时段里的旧编号换成新编号并计数", count == 2 and cache.rhodes_island.child_schedule_template[9]["slot"] == {0: 155, 1: 58, 2: 154}, cache.rhodes_island.child_schedule_template)
check("模板侧：再跑一次是幂等的", save_handle._migrate_child_schedule_template(cache.rhodes_island) == 0)
ga.schedule_override = {1: 176, 2: 152}
student_a.entertainment.entertainment_type = [175, 58, 178]
save_handle._normalize_loaded_save_paths(cache)
check("角色侧：单孩覆盖与当天娱乐槽位换成新编号", ga.schedule_override == {1: 153, 2: 152} and student_a.entertainment.entertainment_type == [152, 58, 155], (ga.schedule_override, student_a.entertainment.entertainment_type))
cache.rhodes_island.child_schedule_template = {}

section("真实存档只读载入")
candidate_list = [name for name in sorted(os.listdir(os.path.join(ROOT, "save"))) if name.isdigit()]
check("有可用的存档目录", bool(candidate_list), candidate_list)
loaded = 0
problem = []
for save_id in candidate_list:
    if not save_handle.judge_save_file_exist(save_id):
        continue
    try:
        save_handle.input_load_save(save_id)
    except Exception as error:
        problem.append((save_id, "load", repr(error)))
        continue
    loaded += 1
    for cid, character_data in cache.character_data.items():
        if not hasattr(character_data, "child_growth"):
            problem.append((save_id, cid, "no child_growth attr"))
            break
        if character_data.child_growth is not None and set(vars(character_data.child_growth)) != default_names:
            problem.append((save_id, cid, "growth fields", set(vars(character_data.child_growth)) ^ default_names))
            break
        if scene_str(character_data.position) not in cache.scene_data:
            problem.append((save_id, cid, "dead scene", character_data.position))
            break
    for field in ("class_schedule", "temp_sex_class", "child_schedule_template", "official_event_queue", "official_event_history"):
        if not hasattr(cache.rhodes_island, field):
            problem.append((save_id, "rhodes", field))
    # 课表结构：{教室: {星期: {节次: [科目, 教师]}}}
    for room, week in cache.rhodes_island.class_schedule.items():
        for day, cells in week.items():
            for period, cell in cells.items():
                if not (isinstance(cell, list) and len(cell) == 2):
                    problem.append((save_id, "class_schedule", room, day, period, cell))
    # 学期结算在真实存档上幂等
    try:
        first = semester_handle.settle_semester_change()
        second = semester_handle.settle_semester_change()
        if second:
            problem.append((save_id, "semester not idempotent", second))
    except Exception as error:
        problem.append((save_id, "semester", repr(error)))
    # 教育面板在真实存档上能画出来（不取输入）
    try:
        from Script.System.Education_System import class_schedule_panel, course_select_panel, growth_panel, schedule_template_panel

        for panel in (class_schedule_panel.Class_Schedule_Panel(190), course_select_panel.Course_Select_Panel(190),
                      growth_panel.Growth_Panel(190), schedule_template_panel.Schedule_Template_Panel(190)):
            panel.draw_page([])
    except Exception as error:
        problem.append((save_id, "panel", repr(error)))
check(f"载入了 {loaded} 个存档", loaded > 0)
check("全部存档：养成字段完整、无死场景、罗德岛新字段齐全、课表结构合法、学期结算幂等、四个面板可画", not problem, problem[:6])

finish()
