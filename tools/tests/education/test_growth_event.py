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

finish()
