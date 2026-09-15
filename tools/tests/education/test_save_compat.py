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
for name in ("semester_id", "report_card_history", "schedule_override", "follow_mother_flag", "last_absent_period", "skip_count", "skip_caught_day", "semester_base_work_type",
             "skip_class_day", "sex_class_count"):
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
check("Plan 30 的三个新字段按默认值回填：累计翘课 0、被抓日 0、学期初岗位 -1（未知）",
      all(one.skip_count == 0 and one.skip_caught_day == 0 and one.semester_base_work_type == -1 for one in (ga, gb)))
check("Plan 31 的两个新字段按默认值回填：翘课 flag 的日期 0（读作不是今天）、累计实操课次数 0",
      all(one.skip_class_day == 0 and one.sex_class_count == 0 for one in (ga, gb)))

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

section("Plan 32 L22：挪了桶的养成事件，履历里的旧 uid 读档时改成新 uid（萝莉 1 / 20 / 26 → 期末 17 / 18 / 19）")
from Script.System.Official_Event_System import official_event_handle  # noqa: E402

_record = {"time": cache.game_time, "choice": 2}
ga.event_history = {"萝莉1": dict(_record), "萝莉20": dict(_record), "萝莉2": dict(_record)}
save_handle._normalize_loaded_save_paths(cache)
_expect_history = {"期末17": _record, "期末18": _record, "萝莉2": _record}
check("孩子的履历：萝莉 1 / 20 改成期末 17 / 18、记录原样保留，其余 uid 不动", ga.event_history == _expect_history, ga.event_history)
check("改名后按新 uid 去重：经历过萝莉 1 的孩子不会在学期切换时再遇到同文的期末 17；没经历过萝莉 26 的照常能遇到期末 19",
      official_event_handle.judge_event_done("期末17", 201) and not official_event_handle.judge_event_done("期末19", 201))
save_handle._normalize_loaded_save_paths(cache)
check("再读一次档是幂等的", ga.event_history == _expect_history, ga.event_history)
_global_history = {"萝莉26@305": dict(_record), "萝莉1": dict(_record), "通用3@305": dict(_record)}
check("罗德岛的全局履历（没有养成数据的主体，键为「uid@角色id」）同样改名，计数 2",
      save_handle._migrate_official_event_history(_global_history) == 2 and set(_global_history) == {"期末19@305", "期末17", "通用3@305"}, _global_history)
_both_history = {"萝莉1": {"choice": 1}, "期末17": {"choice": 3}}
check("新 uid 已有记录时不覆盖（旧键留着，养成总览查不到配置会跳过它）",
      save_handle._migrate_official_event_history(_both_history) == 0 and _both_history == {"萝莉1": {"choice": 1}, "期末17": {"choice": 3}}, _both_history)
ga.event_history = {}

OLD_REPORT_UID_SET = frozenset(save_handle._OFFICIAL_EVENT_UID_MIGRATE)
""" Plan 32 L22 挪进期末桶的三条旧 uid（萝莉 1 / 20 / 26） """


def find_old_report_uid_left(label) -> list:
    """
    找出缓存里还留着的旧 uid 履历：罗德岛全局履历的键是「uid@角色id」（没有主体时就是 uid），孩子的 event_history 以 uid 为键
    Keyword arguments:
    label -- 写进结果里的来源标记（存档编号）
    Return arguments:
    list -- [(来源, "rhodes" 或角色id, 键), ...]，没有残留时为空列表
    """
    result = []
    for key in cache.rhodes_island.official_event_history:
        if isinstance(key, str) and key.partition("@")[0] in OLD_REPORT_UID_SET:
            result.append((label, "rhodes", key))
    for cid, character_data in cache.character_data.items():
        growth_data = getattr(character_data, "child_growth", None)
        if growth_data is None:
            continue
        for key in sorted(set(growth_data.event_history) & OLD_REPORT_UID_SET):
            result.append((label, cid, key))
    return result


section("Plan 32 实施复审补：读档后查旧 uid 残留的辅助函数（L22；下面真实存档一段逐个存档拿它查）")
_saved_global_history = cache.rhodes_island.official_event_history
ga.event_history = {"萝莉26": dict(_record), "萝莉2": dict(_record)}
cache.rhodes_island.official_event_history = {"萝莉1@305": dict(_record), "通用3@305": dict(_record)}
check("L22 迁移之前查得到两处残留：孩子履历里的萝莉 26、罗德岛全局履历里的「萝莉1@305」（萝莉 2、通用 3 不算）",
      {one[2] for one in find_old_report_uid_left("本地")} == {"萝莉26", "萝莉1@305"}, find_old_report_uid_left("本地"))
save_handle._normalize_loaded_save_paths(cache)
save_handle._migrate_official_event_history(cache.rhodes_island.official_event_history)
check("L22 照读档的两处迁移（孩子走 _normalize_loaded_save_paths，罗德岛走 input_load_save 里的 _migrate_official_event_history）之后查不到残留",
      find_old_report_uid_left("本地") == [], find_old_report_uid_left("本地"))
ga.event_history = {}
cache.rhodes_island.official_event_history = _saved_global_history

section("真实存档只读载入")
# 本机没有 save 目录、或里面没有存档时跳过这一段（2026-09-15 用户拍板）：存档不入库，换机器、换目录后常常没带过来。
#    先判目录在不在：save_handle.get_save_dir_path 会顺手建出 save 目录，只读的测试不该留下它
_save_dir = os.path.join(ROOT, "save")
candidate_list = [name for name in sorted(os.listdir(_save_dir)) if name.isdigit()] if os.path.isdir(_save_dir) else []
if not candidate_list:
    print("  跳过：本机没有可读的存档（save 目录不存在或为空）")
    finish()
check("有可用的存档目录", bool(candidate_list), candidate_list)
loaded = 0
problem = []
_old_report_uid_gone = not (OLD_REPORT_UID_SET & set(game_config.config_official_event))
""" 配置里已没有这三个旧 uid：读档迁移只在这时改名 """
l22_left = []
""" 各存档读档后残留的旧 uid 履历（Plan 32 实施复审补） """
for save_id in candidate_list:
    if not save_handle.judge_save_file_exist(save_id):
        continue
    try:
        save_handle.input_load_save(save_id)
    except Exception as error:
        problem.append((save_id, "load", repr(error)))
        continue
    loaded += 1
    # Plan 32 L22（实施复审补）：读档时挪了桶的旧 uid 已改名，罗德岛全局履历与孩子的履历里都查不到
    if _old_report_uid_gone:
        l22_left.extend(find_old_report_uid_left(save_id))
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

section("Plan 32 实施复审补：真实存档读档后，履历里挪了桶的旧 uid 都已改名（L22）")
check("L22 逐个存档读档后：罗德岛全局履历里没有以「萝莉1@」「萝莉20@」「萝莉26@」开头（或就是这三个 uid）的键，孩子的 event_history 里也没有这三个键（前提：配置里已没有这三个 uid）",
      _old_report_uid_gone and not l22_left, (_old_report_uid_gone, l22_left[:6]))

finish()
