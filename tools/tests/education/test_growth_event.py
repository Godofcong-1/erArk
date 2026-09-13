# -*- coding: UTF-8 -*-
"""growth_event_handle：候选人、同胞与同学、事件桶、入队、注册式容量与抬头"""
from _bootstrap import *  # noqa: F401,F403
from Script.System.Official_Event_System import official_event_handle

open_all_classroom()
clear_schedules()
mother = make_character(102, "母亲", 0)
mother_b = make_character(103, "另一位母亲", 0)
loli = make_character(201, "萝莉", 152, daughter=True, stage=103, mother_id=102, born_days=300)
child = make_character(202, "幼女", 152, daughter=True, stage=102, mother_id=102, born_days=120)
half_sib = make_character(203, "异母姐妹", 152, daughter=True, stage=103, mother_id=103, born_days=300)
baby = make_character(204, "婴儿", 152, daughter=True, stage=101, mother_id=103, born_days=5)
stranger = make_character(205, "别人家的孩子", 152, stage=103)
stranger.relationship.father_id = 50
stranger.relationship.mother_id = 51
adult = make_character(301, "成年干员", 21)
E = education_constant

section("候选人与阶段")
check("阶段读取", growth_event_handle.get_character_stage(201) == 103 and growth_event_handle.get_character_stage(301) == 0)
check("只看玩家的女儿", sorted(growth_event_handle.get_growth_event_character_list()) == [201, 202, 203, 204])
check("名单按 id 升序", growth_event_handle.get_growth_event_character_list() == sorted(growth_event_handle.get_growth_event_character_list()))
check("同胞：同父即算（异母也算），婴儿不算（Plan 26）", sorted(growth_event_handle.get_sibling_child_list(201)) == [202, 203])
check("双亲都没登记的孩子不互认", growth_event_handle.get_sibling_child_list(205) == [])
# 同学只算每周课表上确有的课（Plan 30 §3.6），两间教室的这一格都要在全局课表上排上
schedule_handle.set_class_cell(_("理论教室一"), 0, 0, 45, -1)
schedule_handle.set_class_cell(_("理论教室二"), 0, 0, 45, -1)
schedule_handle.set_selected_course(201, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室一"))
schedule_handle.set_selected_course(203, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室一"))
schedule_handle.set_selected_course(202, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室二"))
check("同学：同一格子同一目标", growth_event_handle.get_classmate_list(201) == [203] and growth_event_handle.get_classmate_list(202) == [])
check("没课表的没有同学", growth_event_handle.get_classmate_list(204) == [])

section("事件桶与互动对象")
by_key = game_config.config_official_event_by_sub_key
any_bucket = list(by_key.get((E.GROWTH_EVENT_DEPARTMENT, E.STAGE_ANY), ()))
loli_bucket = list(by_key.get((E.GROWTH_EVENT_DEPARTMENT, 103), ()))
semester_bucket = list(by_key.get((E.GROWTH_EVENT_DEPARTMENT, E.SEMESTER_EVENT_SUB_KEY), ()))
check("通用桶 / 萝莉桶 / 期末桶都有内容", any_bucket and loli_bucket and semester_bucket, (len(any_bucket), len(loli_bucket), len(semester_bucket)))
check("期末桶与日常桶无交集", not (set(semester_bucket) & (set(any_bucket) | set(loli_bucket))))
check("通用桶事件对萝莉成立、对成年不成立", growth_event_handle.judge_stage_pass(any_bucket[0], 201) and not growth_event_handle.judge_stage_pass(any_bucket[0], 301))
check("萝莉桶事件对幼女不成立", not growth_event_handle.judge_stage_pass(loli_bucket[0], 202))
check("不存在的事件不成立", not growth_event_handle.judge_stage_pass("不存在999", 201))
sibling_uid = next((uid for uid in any_bucket + loli_bucket if constant_promise.Premise.SELF_HAVE_SIBLING_CHILD in game_config.config_official_event[uid].get("premise", "")), None)
classmate_uid = next((uid for uid in any_bucket + loli_bucket if constant_promise.Premise.SELF_HAVE_CLASSMATE in game_config.config_official_event[uid].get("premise", "")), None)
check("存在同胞事件与同学事件", sibling_uid is not None and classmate_uid is not None)
if sibling_uid:
    check("同胞事件的互动对象是兄弟姐妹", growth_event_handle.get_event_partner(sibling_uid, 201) in (202, 203, 204))
if classmate_uid:
    check("同学事件的互动对象是同学", growth_event_handle.get_event_partner(classmate_uid, 201) == 203)
check("普通事件互动对象为博士", growth_event_handle.get_event_partner(any_bucket[0], 201) == 0 or growth_event_handle.get_event_partner(any_bucket[0], 201) in (202, 203, 204))

section("候选列表与每日派发")
candidate = growth_event_handle.get_candidate_event_list(201)
check("萝莉有候选事件，且都在两个桶里", candidate and all(one[0] in any_bucket + loli_bucket for one in candidate), len(candidate))
check("候选项形状 [uid, 权重>0, 对象id]", all(len(one) == 3 and one[1] > 0 for one in candidate))
growth_handle.get_child_growth(201).event_history[candidate[0][0]] = {"time": cache.game_time, "choice": 0}
check("经历过的事件不再是候选", candidate[0][0] not in [one[0] for one in growth_event_handle.get_candidate_event_list(201)])
_orig_randint = random.randint
random.randint = lambda a, b: a
pick_list = growth_event_handle.get_today_growth_event_pick_list()
random.randint = _orig_randint
check("每日派发：每个女儿至多 1 条", len(pick_list) <= 4 and len({one["chara_id"] for one in pick_list}) == len(pick_list), pick_list)
check("派发项形状", all(set(one) == {"uid", "chara_id", "partner_id"} and one["uid"] in game_config.config_official_event for one in pick_list))
random.randint = lambda a, b: b
check("掷不中时一条也不派", growth_event_handle.get_today_growth_event_pick_list() == [])
random.randint = _orig_randint

section("注册式容量与抬头")
grown = make_character(206, "已成年的女儿", 152, daughter=True, stage=104, mother_id=102, born_days=500)
check("已成年的少女不进每日派发名单（第五轮）", 206 not in growth_event_handle.get_growth_event_character_list())
check("已成年的少女、婴儿都不是同胞互动对象（Plan 26）", 206 not in growth_event_handle.get_sibling_child_list(201) and 204 not in growth_event_handle.get_sibling_child_list(201))
check("容量 = 4 × 未成年女儿数（成年少女不占容量）", growth_event_handle.get_growth_event_queue_capacity() == E.GROWTH_EVENT_QUEUE_PER_CHILD * 4)
check("容量已注册进公务事件系统", official_event_handle.get_queue_max() >= official_event_handle.OFFICIAL_EVENT_QUEUE_MAX_EXTRA + E.GROWTH_EVENT_QUEUE_PER_CHILD * 4)
title = growth_event_handle.get_growth_event_title({"chara_id": 201})
check("抬头：名字 · 萝莉期第 N 天", title.startswith("萝莉 · ") and "期第" in title, title)
check("抬头：角色不存在时退回部门名", growth_event_handle.get_growth_event_title({"chara_id": 999}) == official_event_handle.get_department_name(E.GROWTH_EVENT_DEPARTMENT))

section("入队")
cache.rhodes_island.official_event_queue = []
growth_event_handle.push_graduation_event(201)
queue = official_event_handle.get_queue()
check("毕业典礼在队首、成年纪念紧随其后", [one["uid"] for one in queue[:2]] == [E.GRADUATION_EVENT_UID, E.ADULT_MEMORIAL_EVENT_UID])
check("队列项带主体", queue[0]["chara_id"] == 201)
# 一辈子一次的毕业典礼不受队列容量上限约束（第五轮）：队列满了也不能丢
cache.rhodes_island.official_event_queue = [{"uid": E.GRADUATION_EVENT_UID, "department": E.GROWTH_EVENT_DEPARTMENT, "chara_id": 999, "partner_id": 0, "add_time": cache.game_time}
                                            for _index in range(official_event_handle.get_queue_max())]
growth_event_handle.push_graduation_event(206)
check("队列已满时毕业典礼照样插到队首", official_event_handle.get_queue()[0]["chara_id"] == 206 and official_event_handle.get_queue()[0]["uid"] == E.GRADUATION_EVENT_UID)
check("队列已满时普通事件仍被挡", not official_event_handle.push_official_event(E.GRADUATION_EVENT_UID, 201))
cache.rhodes_island.official_event_queue = []
check("期末事件入队", growth_event_handle.push_semester_event(201) and len(official_event_handle.get_queue()) == 1)
check("入队的是期末桶里的事件", official_event_handle.get_queue()[0]["uid"] in semester_bucket)
check("待处理计数", growth_event_handle.get_growth_event_queue_count(201) == 1 and growth_event_handle.get_growth_event_queue_count(202) == 0)
cache.rhodes_island.official_event_queue = []
for uid in semester_bucket:
    growth_handle.get_child_growth(202).event_history[uid] = {"time": cache.game_time, "choice": 0}
check("池子抽干时返回 False 且不入队", not growth_event_handle.push_semester_event(202) and official_event_handle.get_queue() == [])
check("批量：只给能入队的计数", growth_event_handle.push_semester_event_for_list([201, 202]) == 1)

section("Plan 26：婴儿不抽写会走会说的孩子的通用事件；期末事件只推幼女 / 萝莉；期末 13 要有课可评")
baby_excluded = {"通用%d" % cid for cid in (3, 4, 5, 9, 23, 25, 29, 39, 42, 43, 44, 45, 49, 50, 51, 52, 53)}
check("这 17 条都带排除婴儿的前提", all("CVP_A1_T|101_E_0" in game_config.config_official_event[uid].get("premise", "") for uid in baby_excluded))
baby_candidate = {one[0] for one in growth_event_handle.get_candidate_event_list(204)}
check("婴儿的候选里没有这 17 条", baby_candidate and not (baby_candidate & baby_excluded), sorted(baby_candidate & baby_excluded))
cache.rhodes_island.official_event_queue = []
check("成年女儿不入队期末事件", growth_event_handle.push_semester_event_for_list([206]) == 0 and official_event_handle.get_queue() == [])
check("期末 13 的前提：上一份成绩单不是「无课可评」", game_config.config_official_event["期末13"].get("premise", "") == "CVP_A1_Growth|7_NE_3")

section("Plan 28 §3.1：婴儿不在 npc_id_got 也照常派养成事件")
check("夹具与真实婴儿对齐：婴儿不在 npc_id_got（Plan 28 §3.9）", 204 not in cache.npc_id_got)
check("婴儿照样进每日派发名单（此前只遍历 npc_id_got，婴儿桶的事件一条都派不出来）", 204 in growth_event_handle.get_growth_event_character_list())
random.randint = lambda a, b: a
_picked = {one["chara_id"] for one in growth_event_handle.get_today_growth_event_pick_list()}
random.randint = _orig_randint
check("必派时派得到婴儿", 204 in _picked, _picked)
cache.npc_id_got.discard(202)
check("离线的幼女不进名单、不占容量（幼女 / 萝莉仍要求在 npc_id_got 里）", 202 not in growth_event_handle.get_growth_event_character_list()
      and growth_event_handle.get_growth_event_queue_capacity() == E.GROWTH_EVENT_QUEUE_PER_CHILD * 3, growth_event_handle.get_growth_event_character_list())
cache.npc_id_got.add(202)
check("婴儿占 4 条容量，成年少女照旧不进", growth_event_handle.get_growth_event_queue_capacity() == E.GROWTH_EVENT_QUEUE_PER_CHILD * 4
      and 206 not in growth_event_handle.get_growth_event_character_list())
_title = growth_event_handle.get_growth_event_title({"chara_id": 204})
check("婴儿的抬头：名字 · 婴儿期第 N 天", _title.startswith("婴儿 · ") and "{0}期第".format(E.STAGE_TALENT_NAME[101]) in _title, _title)

section("Plan 28 §3.1：走真实出生路径的婴儿（character_handle.born_new_character）")
real_baby_id = character_handle.born_new_character(102, "新生儿")
# 生产面板随后会写出生时刻（born_event_panel），这里照做
cache.character_data[real_baby_id].pregnancy.born_time = cache.game_time - datetime.timedelta(days=20)
check("真实出生的婴儿不在 npc_id_got（到长成幼女才上线），是玩家的女儿、阶段 101", real_baby_id not in cache.npc_id_got
      and handle_premise.handle_self_is_player_daughter(real_baby_id) and growth_event_handle.get_character_stage(real_baby_id) == 101)
check("她进每日派发名单", real_baby_id in growth_event_handle.get_growth_event_character_list())
_baby_uid_list = sorted(set(game_config.config_official_event_by_sub_key.get((E.GROWTH_EVENT_DEPARTMENT, 101), ()))
                        | {one[0] for one in growth_event_handle.get_candidate_event_list(real_baby_id)})
_error_list = []
_option_count = 0
for _uid in _baby_uid_list:
    for _option in official_event_handle.get_option_list(_uid, real_baby_id, 0):
        _option_count += 1
        try:
            official_event_handle.settle_official_event_option(_uid, real_baby_id, 0, _option["index"])
        except Exception as now_error:
            _error_list.append((_uid, _option["index"], repr(now_error)))
check("婴儿桶与她可抽的通用事件逐条逐选项结算，都不报错（修好之后这些事件真的会派到婴儿身上）", bool(_baby_uid_list) and _option_count > 0 and not _error_list,
      (len(_baby_uid_list), _option_count, _error_list[:5]))

section("Plan 29 §3.3 / L2：抬头写本阶段第几天（Plan 32 M1 起按可游玩天）；改了岗的萝莉照推期末事件（用户拍板：成绩单照出并写明理由，推送不收窄）")
# 出生日要落在季月（Plan 32 §2.5-4）。今天 2026-09-07 09:00：萝莉与幼女的本阶段都从 2026-06-07 09:00 起，中间跳过 7、8 两个非季月
set_time(DEFAULT_TIME)
loli.pregnancy.born_time = datetime.datetime(2025, 9, 10, 9, 0)
child.pregnancy.born_time = datetime.datetime(2026, 3, 9, 9, 0)
baby.pregnancy.born_time = datetime.datetime(2026, 9, 2, 9, 0)
check("M1 萝莉 2025-09-10 出生：「萝莉期第 31 天」（6/7 起 30 个可游玩天；按日历天会写第 93 天，按出生以来会写第 362 天）",
      growth_event_handle.get_growth_event_title({"chara_id": 201}) == "{0} · {1}期第 31 天".format(loli.name, E.STAGE_TALENT_NAME[103]),
      growth_event_handle.get_growth_event_title({"chara_id": 201}))
check("M1 幼女 2026-03-09 出生：同样是第 31 天；婴儿 9/2 出生：第 6 天（出生当天为第 1 天）",
      growth_event_handle.get_growth_event_title({"chara_id": 202}).endswith(_("期第 {0} 天").format(31))
      and growth_event_handle.get_growth_event_title({"chara_id": 204}).endswith(_("期第 {0} 天").format(6)),
      (growth_event_handle.get_growth_event_title({"chara_id": 202}), growth_event_handle.get_growth_event_title({"chara_id": 204})))
cache.rhodes_island.official_event_queue = []
loli.work.work_type = 21
check("改了岗（岗位 21）的萝莉：学期结束照推期末事件", growth_event_handle.push_semester_event_for_list([201]) == 1
      and official_event_handle.get_queue()[0]["chara_id"] == 201)
loli.work.work_type = 152
cache.rhodes_island.official_event_queue = []

section("Plan 30 §3.6：同学与「有课」只算学生岗的真课；§3.2：期末 9 / 10 进得了待努力的候选；§3.1：萝莉 2 按翘课数")
HP = handle_premise.handle_premise
check("对照：两人同在理论教室一，互为同学", 203 in growth_event_handle.get_classmate_list(201) and 201 in growth_event_handle.get_classmate_list(203))
half_sib.work.work_type = 21
check("她改了岗（课表残留）：不再是同学，自己也没有同学，self_have_any_course 不成立（此前三者都成立）",
      203 not in growth_event_handle.get_classmate_list(201) and growth_event_handle.get_classmate_list(203) == [] and HP("self_have_any_course", 203) == 0)
_class_uid = [one[0] for one in growth_event_handle.get_candidate_event_list(203)
              if any(k in game_config.config_official_event[one[0]].get("premise", "") for k in ("self_have_any_course", "self_have_classmate"))]
check("改了岗的萝莉抽不到写上课 / 同学的事件（此前 24 条）", not _class_uid, _class_uid[:5])
half_sib.work.work_type = 152
check("改回学生岗恢复", 203 in growth_event_handle.get_classmate_list(201) and HP("self_have_any_course", 203) == 1)
schedule_handle.clear_class_cell(_("理论教室一"), 0, 0)
check("每周课表那一格停了课：不再是同学，self_have_any_course 也不成立", growth_event_handle.get_classmate_list(201) == [] and HP("self_have_any_course", 201) == 0)
schedule_handle.set_class_cell(_("理论教室一"), 0, 0, 45, -1)
_g201 = growth_handle.get_child_growth(201)
_g201.report_card_history = []
semester_handle.push_report_card(201, {"year": 2026, "month": 6, "attend": 4, "absent": 6, "rate": 40, "level_change": {}, "grade": E.REPORT_GRADE_POOR, "reason": ""})
# 推送时本学期已重置：本学期 0/0，出勤率按 100
_g201.semester_base_attend = _g201.attend_class_count
_g201.semester_base_absent = _g201.absent_count
_sem = sorted(uid for uid in semester_bucket if official_event_handle.judge_event_can_enqueue(uid, 201)
              and official_event_handle.judge_premise_pass(game_config.config_official_event[uid].get("premise", ""), 201, growth_event_handle.get_event_partner(uid, 201)))
check("待努力的萝莉：期末 9 / 10 都在候选里（此前前提带「本学期出勤率 < 70」，推送时本学期已重置，永远判不过）", "期末9" in _sem and "期末10" in _sem, _sem)
growth_handle.get_child_growth(202).report_card_history = [{"year": 2026, "month": 6, "grade": E.REPORT_GRADE_POOR}]
check("待努力的幼女：期末 9 的前提成立、期末 10（限萝莉）不成立",
      official_event_handle.judge_premise_pass(game_config.config_official_event["期末9"]["premise"], 202, 0)
      and not official_event_handle.judge_premise_pass(game_config.config_official_event["期末10"]["premise"], 202, 0))
check("萝莉 2（翘课被报上来）的前提读累计翘课数", game_config.config_official_event["萝莉2"].get("premise") == "CVP_A1_Growth|24_GE_3")
_g201.absent_count, _g201.skip_count = 5, 0
check("只因体力缺课缺了 5 节：萝莉 2 判不过（此前缺够 3 节就判得过）", not official_event_handle.judge_premise_pass(game_config.config_official_event["萝莉2"]["premise"], 201, 0))
_g201.skip_count = 3
check("翘过 3 节：判得过（此前翘课从不计数，永远判不过）", official_event_handle.judge_premise_pass(game_config.config_official_event["萝莉2"]["premise"], 201, 0))
_g201.absent_count, _g201.skip_count = 0, 0
_g201.report_card_history = []
growth_handle.get_child_growth(202).report_card_history = []

section("Plan 31 §3.11（L7）：同班同学只取幼女 / 萝莉，仍在学生岗的成年姐姐不算")
import inspect  # noqa: E402

from Script.System.Pregnancy_System import pregnancy_handle  # noqa: E402

clear_schedules()
set_time(period_time(0))
ROOM3 = _("理论教室三")
little = make_character(212, "幼女D", 152, daughter=True, stage=102, mother_id=103, born_days=120)
big_sister = make_character(214, "成年姐姐", 152, daughter=True, stage=104, mother_id=103, born_days=500)
schedule_handle.set_class_cell(ROOM3, 2, 3, 45, -1)
schedule_handle.set_selected_course(212, 2, 3, E.COURSE_TYPE_THEORY, ROOM3)
schedule_handle.set_selected_course(214, 2, 3, E.COURSE_TYPE_THEORY, ROOM3)
check("L7 幼女与仍在学生岗的成年姐姐同在一格：姐姐不算她的同学，同学前提不成立（此前算，幼女 41 的对象会是她）",
      214 not in growth_event_handle.get_classmate_list(212) and HP(constant_promise.Premise.SELF_HAVE_CLASSMATE, 212) == 0,
      growth_event_handle.get_classmate_list(212))
check("L7 幼女 41「班上的{TargetName}」不在她的候选里", "幼女41" not in {one[0] for one in growth_event_handle.get_candidate_event_list(212)})
mate = make_character(211, "萝莉C", 152, daughter=True, stage=103, mother_id=103, born_days=300)
schedule_handle.set_selected_course(211, 2, 3, E.COURSE_TYPE_THEORY, ROOM3)
check("L7 再来一个同班的萝莉：同学只有她", growth_event_handle.get_classmate_list(212) == [211], growth_event_handle.get_classmate_list(212))
check("L7 幼女 41 进候选，互动对象是萝莉、不是成年姐姐", "幼女41" in {one[0] for one in growth_event_handle.get_candidate_event_list(212)}
      and growth_event_handle.get_event_partner("幼女41", 212) == 211)

section("Plan 31 §3.2（M2）：成年结算在毕业典礼、成年纪念之后把通用 59 / 60 推到队尾")
_adult_bucket = set(by_key.get((E.GROWTH_EVENT_DEPARTMENT, 104), ()))
check("M2 通用 59 / 60 在成年桶里（部门 15、sub_key 104），日常派发与默认提供者都翻不到", set(E.ADULT_EXTRA_EVENT_UID_LIST) <= _adult_bucket, sorted(_adult_bucket))
_adult_order = [E.GRADUATION_EVENT_UID, E.ADULT_MEMORIAL_EVENT_UID] + list(E.ADULT_EXTRA_EVENT_UID_LIST)
cache.rhodes_island.official_event_queue = []
growth_event_handle.push_graduation_event(214)
_queue_uid = [one["uid"] for one in official_event_handle.get_queue()]
check("M2 空队列：成年结算后依次是通用 1 / 2 / 59 / 60，主体都是她（此前只推 1 / 2，59 / 60 永远出不来）",
      _queue_uid == _adult_order and all(one["chara_id"] == 214 for one in official_event_handle.get_queue()), _queue_uid)
cache.rhodes_island.official_event_queue = []
official_event_handle.push_official_event(loli_bucket[0], 201)
growth_event_handle.push_graduation_event(214)
_queue_uid = [one["uid"] for one in official_event_handle.get_queue()]
check("M2 队里已有日常事件：1 / 2 插到队首，59 / 60 排在它后面（队尾）", _queue_uid == _adult_order[:2] + [loli_bucket[0]] + _adult_order[2:], _queue_uid)
growth_event_handle.push_graduation_event(214)
check("M2 已在队列里的 59 / 60 不重复推（judge_event_can_enqueue）",
      all(sum(1 for one in official_event_handle.get_queue() if one["uid"] == uid and one["chara_id"] == 214) == 1 for uid in E.ADULT_EXTRA_EVENT_UID_LIST))
cache.rhodes_island.official_event_queue = []
growth_handle.get_child_growth(214).event_history[E.ADULT_EXTRA_EVENT_UID_LIST[0]] = {"time": cache.game_time, "choice": 0}
growth_event_handle.push_graduation_event(214)
_queue_uid = [one["uid"] for one in official_event_handle.get_queue()]
check("M2 已经历过的通用 59 不再推，通用 60 照推", _queue_uid == _adult_order[:2] + [E.ADULT_EXTRA_EVENT_UID_LIST[1]], _queue_uid)
growth_handle.get_child_growth(214).event_history.pop(E.ADULT_EXTRA_EVENT_UID_LIST[0], None)
# 队列已满：59 / 60 与毕业典礼、成年纪念一样不受容量上限约束（Plan 31 §3.2，实施时补）——成年桶没有别的入口，按普通入队会永远丢掉
cache.rhodes_island.official_event_queue = [{"uid": loli_bucket[0], "department": E.GROWTH_EVENT_DEPARTMENT, "chara_id": 999, "partner_id": 0, "add_time": cache.game_time}
                                            for _index in range(official_event_handle.get_queue_max())]
growth_event_handle.push_graduation_event(214)
_queue_uid = [one["uid"] for one in official_event_handle.get_queue() if one["chara_id"] == 214]
check("M2 队列已满：通用 1 / 2 照样插到队首、59 / 60 照样追加到队尾（此前按普通入队被挡，永远丢掉）",
      _queue_uid == _adult_order and [one["uid"] for one in official_event_handle.get_queue()[-2:]] == list(E.ADULT_EXTRA_EVENT_UID_LIST), _queue_uid)
check("M2 队列已满时普通事件仍被挡", not official_event_handle.push_official_event(loli_bucket[0], 201))
cache.rhodes_island.official_event_queue = []
check("M2 真实的成年结算（pregnancy_handle.check_grow_to_girl）走的就是 push_graduation_event",
      "growth_event_handle.push_graduation_event(" in inspect.getsource(pregnancy_handle.check_grow_to_girl))


def candidate_uid_set(cid: int) -> set:
    """
    取某个孩子此刻的候选事件 uid 集合
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    set -- 候选事件的 uid 集合
    """
    return {one[0] for one in growth_event_handle.get_candidate_event_list(cid)}


section("Plan 31 §3.14（Q4 / L11）：点名课型的事件改挂按课型查课表的前提")
clear_schedules()
set_time(period_time(0))
growth_handle.get_child_growth(211).selected_course = {}
growth_handle.get_child_growth(212).selected_course = {}
_intern_work = next(cid for cid in game_config.config_work_type
                    if cid and not game_config.config_work_type[cid].tag and game_config.config_work_type[cid].ability_id
                    and cid not in E.EXCLUDE_INTERN_WORK_TYPE and game_config.config_work_type[cid].place_tag in constant.place_data)
schedule_handle.set_class_cell(_("理论教室一"), 0, 0, 45, -1)
schedule_handle.set_class_cell(_("实践教室一"), 0, 1, 43, -1)
schedule_handle.set_selected_course(211, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室一"))
_loli_steps = [
    ("萝莉7", E.COURSE_TYPE_PE, _("木桩房"), 2),
    ("萝莉8", E.COURSE_TYPE_INTERN, _intern_work, 3),
    ("萝莉9", E.COURSE_TYPE_INTEREST, E.ENTERTAINMENT_PLAY_HOUSE, 4),
    ("萝莉16", E.COURSE_TYPE_PRACTICE, _("实践教室一"), 1),
]
_step_uid_list = [step[0] for step in _loli_steps]
_hit = sorted(set(_step_uid_list) & candidate_uid_set(211))
check("L11 只排理论课的萝莉：萝莉 7 / 8 / 9 / 16（体育 / 实习 / 兴趣 / 实践课）都不在候选里（此前都在）", not _hit, _hit)
_added = []
for _step_uid, _step_type, _step_target, _step_period in _loli_steps:
    schedule_handle.set_selected_course(211, 0, _step_period, _step_type, _step_target)
    _added.append(_step_uid)
    _now = candidate_uid_set(211)
    check("L11 再排一格{0}：{1}进候选，还没排的课型对应的事件仍不在".format(E.COURSE_TYPE_NAME[_step_type], _step_uid),
          all(uid in _now for uid in _added) and not any(uid in _now for uid in _step_uid_list if uid not in _added), sorted(set(_step_uid_list) & _now))
schedule_handle.set_selected_course(212, 0, 2, E.COURSE_TYPE_PE, _("木桩房"))
growth_handle.get_child_growth(212).attend_class_count = 3
_now = candidate_uid_set(212)
check("L11 只排体育课、听过课的幼女：幼女 1（第一次坐进理论教室）、幼女 22（实践课）都不在候选里（此前都在）", "幼女1" not in _now and "幼女22" not in _now)
schedule_handle.set_selected_course(212, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室一"))
check("L11 排上理论课：幼女 1 进候选", "幼女1" in candidate_uid_set(212))
growth_handle.get_child_growth(212).attend_class_count = 0
check("L11 一节课都没听过：幼女 1 仍不在（保留累计听课 ≥ 1）", "幼女1" not in candidate_uid_set(212))
schedule_handle.set_selected_course(212, 0, 1, E.COURSE_TYPE_PRACTICE, _("实践教室一"))
check("L11 排上实践课：幼女 22 进候选", "幼女22" in candidate_uid_set(212))

section("Plan 31 §3.14（Q4 / L10）：写成绩单的事件要有待查看的新成绩单；萝莉 6 读本学期出勤")
_growth_211 = growth_handle.get_child_growth(211)
_growth_211.attend_class_count = 20
_growth_211.report_card_flag = False
# Plan 32 L22：写成绩单的萝莉 1 / 20 / 26 挪进了期末桶（期末 17 / 18 / 19），学期切换时与其它期末事件同池抽，日常派发任何状态下都抽不到。
#    期末侧的覆盖（良好档萝莉成立、档位 3 与幼女不成立）在 test_talk_data
_report_uid = {"萝莉1", "萝莉20", "萝莉26", "期末17", "期末18", "期末19"}
check("Plan 32 L22 原萝莉 1 / 20 / 26 已从事件表删去", not any(uid in game_config.config_official_event for uid in ("萝莉1", "萝莉20", "萝莉26")))
_now = candidate_uid_set(211)
check("L10 / Plan 32 L22 听过 20 节课、有课、有同胞，没有待查看的新成绩单：原萝莉 1 / 20 / 26 与期末 17 / 18 / 19 都不在日常候选里",
      not (_report_uid & _now), sorted(_report_uid & _now))
_growth_211.report_card_flag = True
_now = candidate_uid_set(211)
check("Plan 32 L22 有待查看的新成绩单：它们也都不在日常候选里（挪进期末桶，只在学期切换时推）", not (_report_uid & _now), sorted(_report_uid & _now))
_growth_211.report_card_history = [{"grade": E.REPORT_GRADE_NO_CLASS}]
_now = candidate_uid_set(211)
check("Plan 32 L22 待查看的新成绩单是档位 3：同样都不在日常候选里", not (_report_uid & _now), sorted(_report_uid & _now))
_growth_211.report_card_history = []
_growth_211.report_card_flag = False
_growth_211.attend_class_count, _growth_211.absent_count = 50, 5
_growth_211.semester_base_attend, _growth_211.semester_base_absent = 46, 0
check("L10 终身出勤 50 / 55（此前按终身出勤率 ≥ 90 判），本学期 4 听 5 缺：萝莉 6「这学期一节课都没落下」不在候选里", "萝莉6" not in candidate_uid_set(211))
_growth_211.semester_base_attend, _growth_211.semester_base_absent = 30, 5
check("L10 本学期 20 听 0 缺：萝莉 6 进候选", "萝莉6" in candidate_uid_set(211))
_growth_211.attend_class_count = _growth_211.absent_count = _growth_211.semester_base_attend = _growth_211.semester_base_absent = 0

section("Plan 31 §3.14（Q4 / L13）：生日、季月交替、断奶的事件只在正文写的时点出现")
_saved_born_211 = mate.pregnancy.born_time
mate.pregnancy.born_time = cache.game_time.replace(year=cache.game_time.year - 1, hour=6)
check("L13 今天是她的生日：通用 3 进候选", "通用3" in candidate_uid_set(211))
mate.pregnancy.born_time = mate.pregnancy.born_time - datetime.timedelta(days=1)
check("L13 生日是昨天：通用 3 不在候选里（此前任意一天都抽得到）", "通用3" not in candidate_uid_set(211))
mate.pregnancy.born_time = _saved_born_211
# 通用 15 的正文是「被人抱着从一个部门送到另一个部门」，Plan 32 L23 起不派萝莉：正反两向改用幼女 212，另验萝莉判不过
check("L13 学期第 7 天（进度约 21%）：通用 15「季月交替的这几天」不在幼女的候选里", "通用15" not in candidate_uid_set(212), semester_handle.get_semester_progress())
set_time(datetime.datetime(2026, 9, 29, 0, 5))
check("L13 季月最后几天（进度 ≥ 90）：通用 15 进幼女的候选", "通用15" in candidate_uid_set(212), semester_handle.get_semester_progress())
check("Plan 32 L23 季月最后几天：萝莉判不过通用 15（此前照派）", "通用15" not in candidate_uid_set(211), semester_handle.get_semester_progress())
set_time(period_time(0))
baby_e = make_character(213, "婴儿E", 0, daughter=True, stage=101, mother_id=103, born_days=5)
check("L13 出生 5 天的婴儿：婴儿 4「断奶的日子到了」、婴儿 50「断奶之后」都不在候选里（此前出生当天就有）",
      not ({"婴儿4", "婴儿50"} & candidate_uid_set(213)), sorted({"婴儿4", "婴儿50"} & candidate_uid_set(213)))
# 出生日落在季月（Plan 32 §2.5-4）：9/1 06:00 出生，婴儿期 9/1 ~ 11/30 跳过 10、11 月共 29 个可游玩天；每天 00:05（跨天派发的时刻）取样
baby_e.pregnancy.born_time = datetime.datetime(2026, 9, 1, 6, 0)
set_time(datetime.datetime(2026, 9, 16, 0, 5))
check("L13 / M1 第 14 / 29 个可游玩天（进度约 48.3%）：婴儿 4、婴儿 50 都还不在", not ({"婴儿4", "婴儿50"} & candidate_uid_set(213)), growth_handle.get_stage_progress(213))
set_time(datetime.datetime(2026, 9, 17, 0, 5))
_now = candidate_uid_set(213)
check("L13 / M1 第 15 / 29 个可游玩天（进度约 51.7%）：婴儿 4 进候选，婴儿 50 仍不在（要 ≥ 60，排在断奶之后）", "婴儿4" in _now and "婴儿50" not in _now,
      growth_handle.get_stage_progress(213))
set_time(datetime.datetime(2026, 9, 19, 0, 5))
check("L13 / M1 第 17 / 29 个可游玩天（进度约 58.6%）：婴儿 50 仍不在", "婴儿50" not in candidate_uid_set(213), growth_handle.get_stage_progress(213))
set_time(datetime.datetime(2026, 9, 20, 0, 5))
check("L13 / M1 第 18 / 29 个可游玩天（进度约 62.1%）、母亲可跟随：婴儿 50 进候选，与婴儿 4 首次成立相隔 3 个可游玩日（此前按日历天多数出生日期是同一天）",
      "婴儿50" in candidate_uid_set(213) and class_ai.judge_mother_available(213) == 103, growth_handle.get_stage_progress(213))
set_time(period_time(0))
check("L18 期末推送处的注释改成 Plan 30 Q1 的口径，不再写「已成年的女儿照旧出成绩单」",
      "照旧出成绩单" not in inspect.getsource(growth_event_handle.push_semester_event_for_list)
      and "Plan 30 Q1" in inspect.getsource(growth_event_handle.push_semester_event_for_list))
clear_schedules()

# ---------------------------------------------------------------------------
# Plan 32（第十三轮复查）
# ---------------------------------------------------------------------------
from Script.Design import talk  # noqa: E402
from Script.Settle import past_day_settle  # noqa: E402


def queue_pair_list() -> list:
    """
    取公务队列里每一项的 (uid, 主体角色id)
    Keyword arguments:
    无
    Return arguments:
    list -- [(uid str, 角色id int), ...]，按队列顺序
    """
    return [(one["uid"], one["chara_id"]) for one in official_event_handle.get_queue()]


section("Plan 32 M2：生日当天，跨天结算直接把生日事件（通用 3）插到队首")
clear_schedules()
set_time(datetime.datetime(2026, 9, 7, 0, 5))
mate.pregnancy.born_time = datetime.datetime(2025, 9, 7, 6, 0)
big_sister.pregnancy.born_time = datetime.datetime(2024, 9, 7, 6, 0)
check("M2 前提：萝莉 C 与成年姐姐今天都过生日",
      HP(constant_promise.Premise.SELF_BIRTHDAY_TODAY, 211) and HP(constant_promise.Premise.SELF_BIRTHDAY_TODAY, 214))
official_event_handle.push_official_event(loli_bucket[0], 201)
_pushed = growth_event_handle.push_birthday_event()
check("M2 今天过生日的萝莉：通用 3 插在队首、主体是她；成年姐姐不在日常派发名单里、不推（此前只能靠每晚 70% 再按权重抽中，约 1.6%）",
      _pushed == [211] and queue_pair_list() == [(E.BIRTHDAY_EVENT_UID, 211), (loli_bucket[0], 201)], (_pushed, queue_pair_list()))
check("M2 推入之后日常派发不会再抽到它（已在队列里）", E.BIRTHDAY_EVENT_UID not in candidate_uid_set(211))
check("M2 再调一次不重复推", growth_event_handle.push_birthday_event() == [] and queue_pair_list().count((E.BIRTHDAY_EVENT_UID, 211)) == 1)
cache.rhodes_island.official_event_queue = [{"uid": loli_bucket[0], "department": E.GROWTH_EVENT_DEPARTMENT, "chara_id": 999, "partner_id": 0, "add_time": cache.game_time}
                                            for _index in range(official_event_handle.get_queue_max())]
check("M2 队列已满：照样插到队首（与毕业典礼一样不受容量上限约束）",
      growth_event_handle.push_birthday_event() == [211] and queue_pair_list()[0] == (E.BIRTHDAY_EVENT_UID, 211))
cache.rhodes_island.official_event_queue = []
growth_handle.get_child_growth(211).event_history[E.BIRTHDAY_EVENT_UID] = {"time": cache.game_time, "choice": 1}
check("M2 已经历过的不再推", growth_event_handle.push_birthday_event() == [] and official_event_handle.get_queue() == [])
growth_handle.get_child_growth(211).event_history.pop(E.BIRTHDAY_EVENT_UID, None)
set_time(datetime.datetime(2026, 9, 8, 0, 5))
check("M2 第二天（不是生日）不推", growth_event_handle.push_birthday_event() == [] and official_event_handle.get_queue() == [])
_new_day_src = inspect.getsource(past_day_settle.update_new_day)
check("M2 跨天结算在日常派发（check_new_day_official_event）之前推生日事件",
      0 <= _new_day_src.find("growth_event_handle.push_birthday_event(") < _new_day_src.find("official_event_handle.check_new_day_official_event("))
set_time(period_time(0))

section("Plan 32 L16：孩子长大时清掉队列里对不上阶段的日常养成事件（drop_stale_stage_event）")
clear_schedules()
set_time(period_time(0))
child_bucket = list(by_key.get((E.GROWTH_EVENT_DEPARTMENT, 102), ()))
growing = make_character(215, "长大中的孩子", 152, daughter=True, stage=101, mother_id=103, born_days=5)
for _uid in ("婴儿5", "通用27", semester_bucket[0]):
    official_event_handle.push_official_event(_uid, 215)
official_event_handle.push_official_event("婴儿5", 204)
official_event_handle.push_official_event(loli_bucket[0], 201)
growing.talent[101], growing.talent[102] = 0, 1
_dropped = growth_event_handle.drop_stale_stage_event(215)
_left = queue_pair_list()
check("L16 婴儿→幼女：她的婴儿 5 清掉（1 条），通用 27（通用桶）与期末事件照留，别的孩子的不动",
      _dropped == 1 and _left == [("通用27", 215), (semester_bucket[0], 215), ("婴儿5", 204), (loli_bucket[0], 201)], (_dropped, _left))
check("L16 再调一次没有可清的：返回 0、队列不变", growth_event_handle.drop_stale_stage_event(215) == 0 and queue_pair_list() == _left)
official_event_handle.push_official_event(child_bucket[0], 215)
growing.talent[102], growing.talent[103] = 0, 1
_dropped = growth_event_handle.drop_stale_stage_event(215)
check("L16 幼女→萝莉：幼女桶的清掉（1 条），通用桶照留", _dropped == 1 and queue_pair_list() == _left, (_dropped, queue_pair_list()))
official_event_handle.push_official_event(loli_bucket[0], 215)
official_event_handle.push_official_event(E.GRADUATION_EVENT_UID, 215)
growing.talent[103], growing.talent[104] = 0, 1
_dropped = growth_event_handle.drop_stale_stage_event(215)
_left_215 = [one[0] for one in queue_pair_list() if one[1] == 215]
check("L16 萝莉→少女：萝莉桶与通用桶都清掉（2 条），期末桶（200）与成年桶（104）不动",
      _dropped == 2 and _left_215 == [semester_bucket[0], E.GRADUATION_EVENT_UID], (_dropped, _left_215))
remove_character(215)

section("Plan 32 L16：真实的成长结算在换完素质后清残留；成年时毕业典礼照在队首")
_orig_must_show = talk.must_show_talk_check
# 必显二段的口上显示与本条无关，打桩成空函数（跑完即还原）
talk.must_show_talk_check = lambda character_id: None
clear_schedules()
set_time(period_time(0))
to_loli = make_character(216, "要长成萝莉的幼女", 152, daughter=True, stage=102, mother_id=103)
to_loli.pregnancy.born_time = datetime.datetime(2025, 12, 1, 9, 0)  # 出生 280 个日历天，满 270 长成萝莉
official_event_handle.push_official_event(child_bucket[0], 216)
official_event_handle.push_official_event("通用27", 216)
pregnancy_handle.check_grow_to_loli(216)
check("L16 幼女长成萝莉（pregnancy_handle.check_grow_to_loli）：素质已换成萝莉，幼女桶的事件清掉、通用桶照留",
      to_loli.talent[103] == 1 and to_loli.talent[102] == 0 and queue_pair_list() == [("通用27", 216)], queue_pair_list())
to_girl = make_character(217, "要成年的萝莉", 152, daughter=True, stage=103, mother_id=103)
to_girl.pregnancy.born_time = datetime.datetime(2025, 6, 1, 9, 0)  # 出生 463 个日历天，满 450 成年
for _uid in (loli_bucket[0], "通用27", semester_bucket[0]):
    official_event_handle.push_official_event(_uid, 217)
pregnancy_handle.check_grow_to_girl(217)
talk.must_show_talk_check = _orig_must_show
_left_217 = [one[0] for one in queue_pair_list() if one[1] == 217]
check("L16 萝莉成年（pregnancy_handle.check_grow_to_girl）：残留的萝莉桶、通用桶事件清掉，期末事件照留；毕业典礼在队首、成年纪念紧随，通用 59 / 60 在队尾",
      to_girl.talent[104] == 1 and queue_pair_list()[0] == (E.GRADUATION_EVENT_UID, 217)
      and _left_217 == [E.GRADUATION_EVENT_UID, E.ADULT_MEMORIAL_EVENT_UID, semester_bucket[0]] + list(E.ADULT_EXTRA_EVENT_UID_LIST), (_left_217, queue_pair_list()))
_src_baby = inspect.getsource(pregnancy_handle._settle_baby_grow_up)
_src_loli = inspect.getsource(pregnancy_handle.check_grow_to_loli)
_src_girl = inspect.getsource(pregnancy_handle.check_grow_to_girl)
check("L16 三处阶段转换都在换完素质之后清残留，成年结算排在推毕业典礼之前",
      0 <= _src_baby.find("talent[102] = 1") < _src_baby.find("drop_stale_stage_event(")
      and 0 <= _src_loli.find("talent[103] = 1") < _src_loli.find("drop_stale_stage_event(")
      and 0 <= _src_girl.find("talent[104] = 1") < _src_girl.find("drop_stale_stage_event(") < _src_girl.find("push_graduation_event("))
remove_character(216)
remove_character(217)
clear_schedules()

finish()
