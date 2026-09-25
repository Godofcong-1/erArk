# -*- coding: UTF-8 -*-
"""baby_growth_handle：胎教累积与出生转写；六个照料行为的效果串与 CVE；喂奶 556；胎教 555"""
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
check("换算：100 点 → 每科 50 经验", baby_growth_handle.get_prenatal_exp_value(100.0) == 50 and baby_growth_handle.get_prenatal_exp_value(1.0) == 0 and baby_growth_handle.get_prenatal_exp_value(-5) == 0)

section("出生转写")
mother.pregnancy.prenatal_point = 40.0
text_a = baby_growth_handle.settle_prenatal_to_child(102, 203)
text_b = baby_growth_handle.settle_prenatal_to_child(102, 204)
check("双胎各自全额 40 点", baby_a.child_growth.prenatal_point == 40.0 and baby_b.child_growth.prenatal_point == 40.0)
check("转写不清零母亲侧", mother.pregnancy.prenatal_point == 40.0)
exp_id_45 = growth_handle.get_subject_exp_id(45)
exp_id_76 = growth_handle.get_subject_exp_id(76)
check("17 门各得 20 经验、腰技不给", baby_a.experience.get(exp_id_45, 0) == 20 and (not exp_id_76 or baby_a.experience.get(exp_id_76, 0) == 0))
check("说明文本含次数与经验", "80" in text_a and "20" in text_a, text_a)
check("底子读口", baby_growth_handle.get_prenatal_exp_dict(203) == {a: 20 for a in E.FEMALE_SUBJECT_LIST} and baby_growth_handle.get_prenatal_exp_dict(102) == {})
baby_growth_handle.clear_prenatal_point(102)
check("清零", baby_growth_handle.get_prenatal_point(102) == 0.0)
check("无胎教不出文本、不建养成数据", baby_growth_handle.settle_prenatal_to_child(102, 105) == "" and nurse.child_growth is None)
mother.pregnancy.prenatal_point = 1.0
text = baby_growth_handle.settle_prenatal_to_child(102, 204)
check("1 点：记录了但经验为 0，仍有一句文本", baby_b.child_growth.prenatal_point == 1.0 and text != "" and "20" not in text)
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

finish()
