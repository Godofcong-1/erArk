# -*- coding: UTF-8 -*-
"""挤出避孕套精液的处女限制与极细针筒注射器：道具配置、部位面板的可选部位与标注、针筒注入不夺走处女且口上前提可区分、口上数据；胎生生产时清掉阴道处女，卵生破壳不清"""
from _bootstrap import *  # noqa: F401,F403
from unittest import mock

from Script.Design import character as design_character
from Script.System.Item_System import condom_handle, condom_panel
from Script.System.Pregnancy_System import born_event_panel

TARGET_ID = 9501
VIRGIN_PART_SET = {6, 8, 9}
""" 受处女限制的部位：小穴 / 后穴 / 尿道 """

pl.item = attr_calculation.get_item_zero({})
target = make_character(TARGET_ID, "挤精测试干员")
pl.target_character_id = TARGET_ID
enable_clickable_buttons()


def set_virgin(character_data: game_type.Character, virgin: bool):
    """
    设定角色的阴道 / 肛门 / 尿道处女素质
    Keyword arguments:
    character_data -- 角色
    virgin -- True 为三项都保有，False 为三项都已失去
    Return arguments:
    无
    """
    for talent_id in (0, 1, 2):
        character_data.talent[talent_id] = 1 if virgin else 0


def selectable_parts(mode: str = "squeeze") -> set:
    """
    逐个点部位面板里的每个可选项，收集选中后返回的部位
    Keyword arguments:
    mode -- 面板模式
    Return arguments:
    set -- 可选到的 (部位类型, 部位cid) 集合
    """
    panel_obj = condom_panel.Condom_Select_Panel(100, mode)
    run_panel(lambda: panel_obj.select_part(TARGET_ID), ["cancel"])
    option_list = [option for option in ask_log[0][0] if option.startswith("part_")]
    result_set = set()
    for option in option_list:
        result_holder = []
        run_panel(lambda: result_holder.append(panel_obj.select_part(TARGET_ID)), [option])
        result_set.add(result_holder[0])
    return result_set


def panel_text(mode: str = "squeeze") -> str:
    """
    取部位面板绘制出的全部文本
    Keyword arguments:
    mode -- 面板模式
    Return arguments:
    str -- 拼起来的绘制文本
    """
    panel_obj = condom_panel.Condom_Select_Panel(100, mode)
    run_panel(lambda: panel_obj.select_part(TARGET_ID), ["cancel"])
    return "\n".join(drawn_text)


# ==== 1. 道具 ====
section("极细针筒注射器套装：H用机器，商店按类别列出，非消耗品")
item_config = game_config.config_item.get(condom_handle.SYRINGE_ITEM_ID)
check("道具 141 是极细针筒注射器套装、类型 H_Machine（成人用品商店按类型自动列进「H用机器」，买一次永久持有）",
      item_config is not None and item_config.name == "极细针筒注射器套装" and item_config.type == "H_Machine",
      item_config and (item_config.name, item_config.type))
check("新角色的道具表里有它（get_item_zero 按配置补齐）", attr_calculation.get_item_zero({}).get(condom_handle.SYRINGE_ITEM_ID) == 0)

# ==== 2. 部位面板 ====
section("挤出的部位面板：仍是处女的小穴 / 后穴 / 尿道没有针筒时不可选，有针筒时可选并标注")
set_virgin(target, True)
pl.item[condom_handle.SYRINGE_ITEM_ID] = 0
now_set = selectable_parts()
check("三处都是处女、没有针筒：小穴 / 后穴 / 尿道都选不到，其余身体部位照常可选",
      not ({(0, part_cid) for part_cid in VIRGIN_PART_SET} & now_set) and (0, 1) in now_set and (0, 16) in now_set, sorted(now_set))
now_text = panel_text()
check("没有针筒：受限部位以「(处女)」灰显并提示可用针筒注入",
      all(f"[{game_config.config_body_part[part_cid].name}(处女)]" in now_text for part_cid in VIRGIN_PART_SET) and "极细针筒注射器套装" in now_text, now_text[-300:])

pl.item[condom_handle.SYRINGE_ITEM_ID] = 1
now_set = selectable_parts()
check("有针筒：小穴 / 后穴 / 尿道可选", {(0, part_cid) for part_cid in VIRGIN_PART_SET} <= now_set, sorted(now_set))
now_text = panel_text()
check("有针筒：受限部位标「(针筒)」，没有「(处女)」灰显",
      all(f"[{game_config.config_body_part[part_cid].name}(针筒)]" in now_text for part_cid in VIRGIN_PART_SET) and "(处女)]" not in now_text, now_text[-300:])

pl.item[condom_handle.SYRINGE_ITEM_ID] = 0
target.talent[1] = 0
now_set = selectable_parts()
check("只失去了肛门处女、没有针筒：后穴可选，小穴 / 尿道仍不可选",
      (0, 8) in now_set and (0, 6) not in now_set and (0, 9) not in now_set, sorted(now_set))
set_virgin(target, False)
now_set = selectable_parts()
check("三处都不是处女：不需要针筒就都能选，面板上没有任何标注",
      {(0, part_cid) for part_cid in VIRGIN_PART_SET} <= now_set and "(处女)]" not in panel_text() and "(针筒)]" not in panel_text(), sorted(now_set))
set_virgin(target, True)
check("挂装饰模式不受影响：只有头发与已穿着的服装部位", (0, 6) not in selectable_parts("hang") and (0, 0) in selectable_parts("hang"))

# ==== 3. 结算 ====
section("针筒注入：精液进入部位并照常流动，不夺走处女，口上前提只认针筒注入")
set_virgin(target, True)
pl.item[condom_handle.SYRINGE_ITEM_ID] = 1
target.dirty = attr_calculation.get_zero_dirty()
pl.pl_collection.used_condoms = [30, 20]
condom_handle.settle_squeeze(TARGET_ID, 0, 6, [0, 1])
flow_to_womb = [
    flow_data for flow_data in target.dirty.semen_flow
    if flow_data["source"] == {"type": 0, "id": 6} and any(now_target["type"] == 0 and now_target["id"] == 7 for now_target in flow_data["targets"])
]
check("注入小穴：两套共 50ml 进入小穴，并挂上流向子宫的自然流动（随时间流进子宫，可以受孕）",
      pl.pl_collection.used_condoms == [] and target.dirty.body_semen[6][3] == 50 and len(flow_to_womb) == 1,
      (pl.pl_collection.used_condoms, target.dirty.body_semen[6], target.dirty.semen_flow))
check("注入后阴道 / 肛门 / 尿道处女都还在", [target.talent[talent_id] for talent_id in (0, 1, 2)] == [1, 1, 1])
check("行为目标标记为 2，口上前提只有「针筒注入」成立",
      pl.sp_flag.condom_cloth_flag == 2 and handle_premise.handle_premise("condom_operation_syringe", 0) == 1
      and handle_premise.handle_premise("condom_operation_to_body", 0) == 0 and handle_premise.handle_premise("condom_operation_to_cloth", 0) == 0,
      pl.sp_flag.condom_cloth_flag)
target.talent[1] = 0
pl.pl_collection.used_condoms = [10]
condom_handle.settle_squeeze(TARGET_ID, 0, 8, [0])
check("挤进已不是处女的后穴：按普通身体部位记标记 0，「针筒注入」前提不成立",
      pl.sp_flag.condom_cloth_flag == 0 and handle_premise.handle_premise("condom_operation_syringe", 0) == 0, pl.sp_flag.condom_cloth_flag)
target.talent[1] = 1

# ==== 4. 口上数据 ====
section("口上：挤出避孕套精液有针筒注入专用的口上")
syringe_talk_list = [
    talk_cid for talk_cid, talk_data in game_config.config_talk.items()
    if talk_data.behavior_id == "squeeze_condom_semen" and "condom_operation_syringe" in game_config.config_talk_premise_data.get(talk_cid, set())
]
check("构建后的口上里至少有一条挤出避孕套精液的针筒注入口上", len(syringe_talk_list) >= 1, syringe_talk_list)

# ==== 5. 生产时破处 ====
section("生产：仍是阴道处女的产妇胎生生产时失去阴道处女，卵生破壳不清")
MOTHER_ID = 9502
saved_npc_id_got = set(cache.npc_id_got)


def run_born(mother_data: game_type.Character, egg_mode: bool = False) -> tuple:
    """
    跑一遍生产事件面板（取名、成就、移动打桩），跑完撤掉生下的孩子
    Keyword arguments:
    mother_data -- 产妇
    egg_mode -- 是否为卵生破壳
    Return arguments:
    tuple -- (面板抛出的异常, 绘制文本)
    """
    before_set = set(cache.character_data)
    mother_data.talent[22] = 0 if egg_mode else 1
    mother_data.talent[26] = 0 if egg_mode else 1
    with mock.patch.object(design_character, "input_name_func", return_value="测试女儿"), \
            mock.patch.object(born_event_panel.achievement_panel, "achievement_flow"), \
            mock.patch.object(born_event_panel, "move_to_inpatient_department_for_born"):
        error = run_panel(lambda: born_event_panel.Born_Panel(MOTHER_ID, egg_mode=egg_mode, egg_id_list=[1] if egg_mode else None).draw(), [])
    now_text = "\n".join(drawn_text)
    for child_id in set(cache.character_data) - before_set:
        remove_character(child_id)
    mother_data.relationship.child_id_list = []
    pl.relationship.child_id_list = []
    return error, now_text


mother = make_character(MOTHER_ID, "产妇测试干员")
mother.talent[0] = 1
error, now_text = run_born(mother)
check("胎生生产：面板跑完不报错，阴道处女被清掉并提示", error is None and mother.talent[0] == 0 and _("失去了[阴道处女]") in now_text, (repr(error), mother.talent[0]))
mother.talent[0] = 0
error, now_text = run_born(mother)
check("产妇本就不是处女：不再提示失去处女", error is None and _("失去了[阴道处女]") not in now_text, repr(error))
mother.talent[0] = 1
error, now_text = run_born(mother, egg_mode=True)
check("卵生破壳（卵在体外孵化）：阴道处女保留", error is None and mother.talent[0] == 1 and _("失去了[阴道处女]") not in now_text, (repr(error), mother.talent[0]))
remove_character(MOTHER_ID)
cache.npc_id_got.clear()
cache.npc_id_got.update(saved_npc_id_got)

remove_character(TARGET_ID)
finish()
