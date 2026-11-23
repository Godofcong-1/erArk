# -*- coding: UTF-8 -*-
"""baby_growth_handle：胎教累积与出生折习得珠（Plan 26）；六个照料行为的效果串与 CVE；喂奶 556；胎教 555"""
from _bootstrap import *  # noqa: F401,F403

clear_schedules()
mother = make_character(102, "母亲", 0)
baby_a = make_character(203, "婴儿A", 152, daughter=True, stage=101, mother_id=102, born_days=3)
baby_b = make_character(204, "婴儿B", 152, daughter=True, stage=101, mother_id=102, born_days=3)
nurse = make_character(105, "保育员", 153)
E = education_constant

section("胎教累积")
check("初始 0", baby_growth_handle.get_prenatal_point(102) == 0.0 and baby_growth_handle.get_prenatal_point(999) == 0.0)
check("一次 +0.5", baby_growth_handle.add_prenatal_point(102) == 0.5)
check("两次 1.0", baby_growth_handle.add_prenatal_point(102) == 1.0)
check("次数折算", baby_growth_handle.get_prenatal_count(102) == 2)
check("封顶 100", baby_growth_handle.add_prenatal_point(102, 999) == E.PRENATAL_POINT_MAX)
check("对不存在的角色返回 0", baby_growth_handle.add_prenatal_point(999) == 0.0)
check("换算：100 点 → 1000 珠、1 点 → 10 珠、0.5 点 → 5 珠、负数 → 0", baby_growth_handle.get_prenatal_juel_value(100.0) == 1000 and baby_growth_handle.get_prenatal_juel_value(1.0) == 10
      and baby_growth_handle.get_prenatal_juel_value(0.5) == 5 and baby_growth_handle.get_prenatal_juel_value(-5) == 0)

section("出生转写：折成习得珠、不给任何经验（Plan 26 §3.2）")
J = E.LEARN_STATE_ID
subject_exp_set = {growth_handle.get_subject_exp_id(a) for a in E.SUBJECT_ABILITY_LIST} - {0}
mother.pregnancy.prenatal_point = 40.0
exp_before_a = dict(baby_a.experience)
text_a = baby_growth_handle.settle_prenatal_to_child(102, 203)
text_b = baby_growth_handle.settle_prenatal_to_child(102, 204)
check("双胎各自全额 40 点", baby_a.child_growth.prenatal_point == 40.0 and baby_b.child_growth.prenatal_point == 40.0)
check("转写不清零母亲侧", mother.pregnancy.prenatal_point == 40.0)
check("双胎各得 400 个习得珠", baby_a.juel.get(J, 0) == 400 and baby_b.juel.get(J, 0) == 400, (baby_a.juel.get(J, 0), baby_b.juel.get(J, 0)))
check("经验一项都没动（18 门科目的升级经验，含 7 种性交类，全是 0）", dict(baby_a.experience) == exp_before_a and all(baby_a.experience.get(e, 0) == 0 for e in subject_exp_set))
juel_name = baby_growth_handle.get_learn_juel_name()
check("说明文本含次数、珠数与珠名", "80" in text_a and "400" in text_a and bool(juel_name) and juel_name in text_a, text_a)
check("读口：孩子出生时折得的珠与胎教次数", baby_growth_handle.get_child_prenatal_juel(203) == 400 and baby_growth_handle.get_child_prenatal_count(203) == 80
      and baby_growth_handle.get_child_prenatal_juel(102) == 0 and baby_growth_handle.get_child_prenatal_count(999) == 0)
baby_growth_handle.clear_prenatal_point(102)
check("清零", baby_growth_handle.get_prenatal_point(102) == 0.0)
check("无胎教不出文本、不建养成数据", baby_growth_handle.settle_prenatal_to_child(102, 105) == "" and nurse.child_growth is None)
mother.pregnancy.prenatal_point = 1.0
juel_before = baby_b.juel.get(J, 0)
text = baby_growth_handle.settle_prenatal_to_child(102, 204)
check("1 点：折 10 个珠，也有一句文本", baby_b.child_growth.prenatal_point == 1.0 and baby_b.juel.get(J, 0) - juel_before == 10 and "10" in text, text)
_orig_juel_rate = E.PRENATAL_JUEL_PER_POINT
E.PRENATAL_JUEL_PER_POINT = 0
juel_before = baby_b.juel.get(J, 0)
text = baby_growth_handle.settle_prenatal_to_child(102, 204)
E.PRENATAL_JUEL_PER_POINT = _orig_juel_rate
check("比例调到 0 时折不出珠：不加珠、给「还不足以留下什么」那句", baby_b.juel.get(J, 0) == juel_before and "还不足以留下什么" in text, text)
mother.pregnancy.prenatal_point = 0.0

section("胎教结算 555")
change = game_type.CharacterStatusChange()
pl.target_character_id = 102
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.PRENATAL_ADD_ADJUST](0, 30, change, cache.game_time)
check("对孕肚说话一次 +0.5", mother.pregnancy.prenatal_point == 0.5)
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.PRENATAL_ADD_ADJUST](0, 0, change, cache.game_time)
check("add_time=0 不累积", mother.pregnancy.prenatal_point == 0.5)
pl.target_character_id = 0
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.PRENATAL_ADD_ADJUST](0, 30, change, cache.game_time)
check("没有交互对象不累积", mother.pregnancy.prenatal_point == 0.5)
check("三条胎教指令的效果串都挂了 555", all(555 in game_config.config_behavior_effect_data[b] for b in ("prenatal_talk", "prenatal_music", "prenatal_touch")))

section("六个照料行为的效果串")
chain = {b: [e for e in game_config.config_behavior_effect_data[b]] for b in ("hold_child", "sing_children_song", "nuirse_child", "change_diapers", "teach_talk", "give_toy")}
common = chain["hold_child"][:6]
check("前 6 项六个行为相同", all(one[:6] == common for one in chain.values()), chain)
check("六条链的追加项互不相同", len({tuple(one[6:]) for one in chain.values()}) == 6)
check("抱小孩：照料 +0.3、坚强 +0.5", "CVE_A2_Growth|20_G_0.3" in chain["hold_child"] and "CVE_A2_Growth|11_G_0.5" in chain["hold_child"])
check("换尿布：羞耻方向（倾向 3 减）", "CVE_A2_Growth|13_L_0.5" in chain["change_diapers"])
check("喂奶：556", 556 in chain["nuirse_child"])
check("哼唱：音乐经验 + 热情", "CVE_A2_E|85_G_8" in chain["sing_children_song"] and "CVE_A2_Growth|12_G_0.5" in chain["sing_children_song"])

section("CVE 实跑")
pl.target_character_id = 203
change = game_type.CharacterStatusChange()
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|11", "G", "0.5"], change)
check("倾向 1 +0.5（坚强方向）", baby_a.child_growth.personality_point.get(1, 0.0) == 0.5)
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|13", "L", "0.5"], change)
check("倾向 3 -0.5（羞耻方向）", baby_a.child_growth.personality_point.get(3, 0.0) == -0.5)
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|20", "G", "0.3"], change)
check("照料值 +0.3", abs(baby_a.child_growth.care_point - 0.3) < 1e-9)
exp_before = baby_a.experience.get(85, 0)
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "E|85", "G", "8"], change)
check("音乐经验 +8", baby_a.experience.get(85, 0) - exp_before == 8)
settle_behavior.handle_comprehensive_value_effect(0, ["A2", "Growth|0", "G", "9"], change)
check("出勤数不可被 CVE 改写", baby_a.child_growth.attend_class_count == 0)

section("喂奶 556")
hp_max = baby_a.hit_point_max
favor_before = baby_a.favorability.get(0, 0)
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.NUIRSE_CHILD_ADD_ADJUST](0, 30, change, cache.game_time)
check("玩家喂奶：体力上限 +2、好感增加", baby_a.hit_point_max == hp_max + E.NUIRSE_CHILD_HP_MAX_ADD and baby_a.favorability.get(0, 0) > favor_before)
nurse.target_character_id = 203
favor_before = baby_a.favorability.get(0, 0)
hp_max = baby_a.hit_point_max
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.NUIRSE_CHILD_ADD_ADJUST](105, 30, change, cache.game_time)
check("保育员喂奶：只加体质不加好感", baby_a.hit_point_max == hp_max + E.NUIRSE_CHILD_HP_MAX_ADD and baby_a.favorability.get(0, 0) == favor_before)
pl.target_character_id = 102
hp_max = mother.hit_point_max
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.NUIRSE_CHILD_ADD_ADJUST](0, 30, change, cache.game_time)
check("非婴儿不生效", mother.hit_point_max == hp_max)
pl.target_character_id = 203
hp_max = baby_a.hit_point_max
constant.settle_behavior_effect_data[constant_effect.BehaviorEffect.NUIRSE_CHILD_ADD_ADJUST](0, 0, change, cache.game_time)
check("add_time=0 不生效", baby_a.hit_point_max == hp_max)

# ---------------------------------------------------------------------------
# Plan 32（第十三轮复查）
# ---------------------------------------------------------------------------
from Script.Design import basement, talk  # noqa: E402
from Script.Settle import past_day_settle  # noqa: E402
from Script.System.Official_Event_System import official_event_handle  # noqa: E402
from Script.System.Pregnancy_System import pregnancy_handle  # noqa: E402

section("Plan 32 L19 / L16：婴儿长成幼女（真实的 pregnancy_handle._settle_baby_grow_up）")
# 上线时刷娱乐走成年随机池，要读场所开放表与派对日表；长大提示要读教师岗名单——夹具里这三样默认都是空的
open_all_classroom()
cache.rhodes_island.party_day_of_week = {day: 0 for day in range(7)}
cache.rhodes_island.all_work_npc_set.setdefault(E.TEACHER_WORK_TYPE, set())
clear_schedules()
official_event_handle.push_official_event("婴儿5", 203)
official_event_handle.push_official_event("通用27", 203)
_orig_must_show = talk.must_show_talk_check
# 母亲一侧必显二段的口上显示与本条无关，打桩成空函数（跑完即还原）
talk.must_show_talk_check = lambda character_id: None
pregnancy_handle._settle_baby_grow_up(102, 203)
talk.must_show_talk_check = _orig_must_show
check("L19 前提：长成幼女（素质 101 → 102）、已上线（进了 npc_id_got）", baby_a.talent[102] == 1 and baby_a.talent[101] == 0 and 203 in cache.npc_id_got)
_slot_list = [baby_a.entertainment.entertainment_type[slot] for slot in range(3)]
check("L19 当天娱乐三个时段都在幼女默认池（过家家 / 自由玩耍）里（此前上线时她还算婴儿，刷的是成年随机池，玩家午夜后入睡时要用一整天）",
      all(one in E.CHILD_DEFAULT_ENTERTAINMENT_LIST for one in _slot_list), _slot_list)
_left_203 = [one["uid"] for one in official_event_handle.get_queue() if one["chara_id"] == 203]
check("L16 婴儿期入队、还没处理的婴儿 5 清掉，通用 27（通用桶）照留", _left_203 == ["通用27"], _left_203)

section("Plan 32 L5 / M2：真实的跨天结算只清过期的翘课 flag；今天过生日的女儿队首是生日事件")
_new_day = datetime.datetime(2026, 9, 8, 0, 5)  # 周二：避开周日的外交结算与周一的助理轮换
set_time(_new_day)
skip_new = make_character(206, "新一天翘了课的萝莉", 152, daughter=True, stage=103, mother_id=102)
skip_old = make_character(207, "昨天翘了课的萝莉", 152, daughter=True, stage=103, mother_id=102)
birthday_girl = make_character(208, "今天过生日的萝莉", 152, daughter=True, stage=103, mother_id=102)
skip_new.pregnancy.born_time = datetime.datetime(2025, 9, 20, 9, 0)
skip_old.pregnancy.born_time = datetime.datetime(2025, 9, 20, 9, 0)
birthday_girl.pregnancy.born_time = datetime.datetime(2025, 9, 8, 6, 0)
_g_new = growth_handle.get_child_growth(206)
_g_old = growth_handle.get_child_growth(207)
# 玩家一步跨过午夜：NPC 阶段先跑完新一天的早上，549 挂上新一天的 flag（flag 与日期一起写，README 夹具陷阱）；另一个是前一天的残留
_g_new.skip_class_flag, _g_new.skip_class_day, _g_new.follow_mother_flag = True, _new_day.toordinal(), True
_g_old.skip_class_flag, _g_old.skip_class_day, _g_old.follow_mother_flag = True, _new_day.toordinal() - 1, True
clear_schedules()
_orig_base_newday = basement.update_base_resouce_newday
# 基建日结在夹具里缺 materials_resouce（README 夹具陷阱），排在角色刷新段之后，换成空函数
basement.update_base_resouce_newday = lambda: None
_new_day_error = ""
try:
    past_day_settle.update_new_day()
except Exception as now_error:
    import traceback  # noqa: E402

    traceback.print_exc()
    _new_day_error = repr(now_error)
finally:
    basement.update_base_resouce_newday = _orig_base_newday
check("跨天结算在夹具里跑通", not _new_day_error, _new_day_error)
check("L5 新一天挂上的翘课 flag 跨天后仍在，今天仍算已翘课（此前被无条件清掉，当天余下节次重新掷翘课）",
      _g_new.skip_class_flag and class_ai.judge_skip_class_today(206, _new_day))
check("L5 对照：前一天的残留照清", not _g_old.skip_class_flag and not class_ai.judge_skip_class_today(207, _new_day))
check("L5 见学 flag 照旧无条件清", not _g_new.follow_mother_flag and not _g_old.follow_mother_flag)
_queue = official_event_handle.get_queue()
check("M2 今天过生日的萝莉：跨天结算后队首是她的生日事件，且只有一条（在日常派发之前推入，日常派发不会再抽到它）",
      bool(_queue) and _queue[0]["uid"] == E.BIRTHDAY_EVENT_UID and _queue[0]["chara_id"] == 208
      and sum(1 for one in _queue if one["uid"] == E.BIRTHDAY_EVENT_UID) == 1, [(one["uid"], one["chara_id"]) for one in _queue])

finish()
