# -*- coding: UTF-8 -*-
"""挤出避孕套精液的处女限制与极细针筒注射器：道具配置、部位面板的可选部位与标注、针筒注入不夺走处女且地文前提可区分、目标部位变量与综合数值前提「避孕套位置」、地文数据；胎生生产时清掉阴道处女，卵生破壳不清"""
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
section("针筒注入：精液进入部位并照常流动，不夺走处女，地文前提只认针筒注入")
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
check("玩家行为数据记下目标部位 6（编码同阴茎插入位置），地文前提只有「针筒注入」成立、不算普通身体部位",
      pl.behavior.condom_position == 6 and handle_premise.handle_premise("condom_operation_syringe", 0) == 1
      and handle_premise.handle_premise("condom_operation_to_body", 0) == 0 and handle_premise.handle_premise("condom_operation_to_cloth", 0) == 0,
      pl.behavior.condom_position)
PART_PREMISE = {6: "condom_operation_syringe_to_vagina", 8: "condom_operation_syringe_to_anal", 9: "condom_operation_syringe_to_urethra"}
""" 针筒注入部位 → 该部位的地文差分前提 """
premise_result = {}
for part_cid in PART_PREMISE:
    pl.pl_collection.used_condoms = [10]
    condom_handle.settle_squeeze(TARGET_ID, 0, part_cid, [0])
    premise_result[part_cid] = {premise: handle_premise.handle_premise(premise, 0) for premise in list(PART_PREMISE.values()) + ["condom_operation_syringe"]}
check("注入小穴 / 后穴 / 尿道：通用的「针筒注入」前提都成立，部位前提只有对应部位那一个成立",
      all(now_result["condom_operation_syringe"] == 1 and all(now_result[premise] == (1 if premise == PART_PREMISE[part_cid] else 0) for premise in PART_PREMISE.values())
          for part_cid, now_result in premise_result.items()),
      premise_result)
pl.pl_collection.used_condoms = [10]
condom_handle.settle_squeeze(TARGET_ID, 0, 1, [0])
check("挤到脸部：记下部位 1，按普通身体部位处理，三个部位前提都不成立",
      pl.behavior.condom_position == 1 and handle_premise.handle_premise("condom_operation_to_body", 0) == 1
      and all(handle_premise.handle_premise(premise, 0) == 0 for premise in PART_PREMISE.values()), pl.behavior.condom_position)
target.talent[1] = 0
pl.pl_collection.used_condoms = [10]
condom_handle.settle_squeeze(TARGET_ID, 0, 8, [0])
check("挤进已不是处女的后穴：记下部位 8，按普通身体部位处理，「针筒注入」前提不成立",
      pl.behavior.condom_position == 8 and handle_premise.handle_premise("condom_operation_to_body", 0) == 1
      and handle_premise.handle_premise("condom_operation_syringe", 0) == 0, pl.behavior.condom_position)
target.talent[1] = 1

# ==== 3b. 目标部位变量 ====
section("避孕套行为的目标部位：挂装饰 / 取回 / 挤出共用一个变量，服装部位从 20 起编码，行为结束重建后清空")
CLOTH_TYPE = next(iter(game_config.config_clothing_type))
saved_cloth_wear = target.cloth.cloth_wear[CLOTH_TYPE]
target.cloth.cloth_wear[CLOTH_TYPE] = [next(iter(game_config.config_clothing_tem))]
pl.pl_collection.used_condoms = [10, 10]
condom_handle.settle_hang(TARGET_ID, 1, CLOTH_TYPE, [0])
check("挂到服装部位：记为 20 + 服装部位cid，「服装部位」前提成立、「身体部位」不成立",
      pl.behavior.condom_position == 20 + CLOTH_TYPE and handle_premise.handle_premise("condom_operation_to_cloth", 0) == 1
      and handle_premise.handle_premise("condom_operation_to_body", 0) == 0, pl.behavior.condom_position)
condom_handle.settle_hang(TARGET_ID, 0, 0, [0])
check("挂到头发：记为 0，「身体部位」前提成立", pl.behavior.condom_position == 0 and handle_premise.handle_premise("condom_operation_to_body", 0) == 1, pl.behavior.condom_position)
condom_handle.settle_take_back(TARGET_ID, [((1, CLOTH_TYPE), 0), ((0, 0), 0)])
check("取回多处装饰：按第一个选中的位置记录", pl.behavior.condom_position == 20 + CLOTH_TYPE, pl.behavior.condom_position)
target.cloth.cloth_wear[CLOTH_TYPE] = saved_cloth_wear
cvp_result = {
    token: handle_premise.handle_premise(token, 0)
    for token in (f"CVP_A2_CondomPos|C{CLOTH_TYPE}_E_1", f"CVP_A1_CondomPos|C{CLOTH_TYPE}_E_1", f"CVP_A2_CondomPos|B{CLOTH_TYPE}_E_1")
}
check("综合数值前提「避孕套位置」：服装部位写 C+编号时命中，主体写自己或交互对象都一样，同编号的身体部位 B 不命中",
      list(cvp_result.values()) == [1, 1, 0], cvp_result)
pl.pl_collection.used_condoms = [10]
condom_handle.settle_squeeze(TARGET_ID, 0, 6, [0])
cvp_result = {token: handle_premise.handle_premise(token, 0) for token in ("CVP_A2_CondomPos|B6_E_1", "CVP_A2_CondomPos|B8_E_1")}
check("综合数值前提「避孕套位置」：针筒注入小穴时 B6 命中、B8 不命中", list(cvp_result.values()) == [1, 0], cvp_result)
pl.behavior = game_type.Behavior()
check("行为结束重建行为数据后为 -1，身体 / 服装 / 针筒前提都不成立（不会把上一次的部位带进下一个行为）",
      pl.behavior.condom_position == -1 and all(handle_premise.handle_premise(premise, 0) == 0 for premise in ("condom_operation_to_body", "condom_operation_to_cloth", "condom_operation_syringe", "CVP_A2_CondomPos|B6_E_1")))
del pl.behavior.condom_position
check("旧存档里尚未重建过、没有该字段的行为数据：读取不报错，前提都不成立",
      condom_handle.get_condom_location() is None and handle_premise.handle_premise("condom_operation_to_body", 0) == 0)
pl.behavior = game_type.Behavior()

# ==== 4. 地文数据 ====
section("地文：挤出避孕套精液有针筒注入专用的地文")
syringe_talk_list = [
    talk_cid for talk_cid, talk_data in game_config.config_talk.items()
    if talk_data.behavior_id == "squeeze_condom_semen" and "condom_operation_syringe" in game_config.config_talk_premise_data.get(talk_cid, set())
]
check("构建后的文本数据里至少有一条挤出避孕套精液的针筒注入地文", len(syringe_talk_list) >= 1, syringe_talk_list)
missing_part_list = [
    premise for premise in PART_PREMISE.values()
    if not any(
        talk_data.behavior_id == "squeeze_condom_semen" and premise in game_config.config_talk_premise_data.get(talk_cid, set())
        for talk_cid, talk_data in game_config.config_talk.items()
    )
]
check("小穴 / 后穴 / 尿道各有至少一条部位差分地文", missing_part_list == [], missing_part_list)
missing_state_list = [
    (premise, state) for premise in PART_PREMISE.values() for state in ("t_unconscious_flag_0", "t_unconscious_flag")
    if not any(
        talk_data.behavior_id == "squeeze_condom_semen" and {premise, state} <= game_config.config_talk_premise_data.get(talk_cid, set())
        for talk_cid, talk_data in game_config.config_talk.items()
    )
]
check("三个部位的差分地文都同时有对方有意识与对方无意识两种版本（对方无意识时只认前提名带 unconscious 的文本）", missing_state_list == [], missing_state_list)

# ==== 4b. 各部位的地文选取 ====
section("挤到每个身体 / 服装部位时，按部位与对方意识状态选出对应的差分地文")
SQUEEZE_BODY_LIST = [0, 1, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18]
""" 挤出面板可选的身体部位（口腔、子宫、胃部不可选） """
saved_behavior_id = pl.behavior.behavior_id
pl.behavior.behavior_id = "squeeze_condom_semen"
set_virgin(target, False)


def pick_candidate(part_type: int, part_cid: int, unconscious: int, behavior_id: str = "squeeze_condom_semen") -> list:
    """
    记下目标部位与对方意识状态后，取该避孕套行为此刻可被选中的全部地文
    Keyword arguments:
    part_type -- 部位类型，0=身体，1=服装
    part_cid -- 部位cid
    unconscious -- 对方的无意识H模式编号，0为有意识
    behavior_id -- 行为id，默认为挤出避孕套精液
    Return arguments:
    list -- [(地文cid, 前提集合)]
    """
    condom_handle.set_condom_position(part_type, part_cid)
    target.sp_flag.unconscious_h = unconscious
    from Script.Design import talk

    pl.behavior.behavior_id = behavior_id
    now_talk_data, _calculated = talk.handle_talk_sub(0, behavior_id, {})
    return [(talk_cid, game_config.config_talk_premise_data[talk_cid]) for talk_set in now_talk_data.values() for talk_cid in talk_set]


def collect_wrong_selection(behavior_id: str, body_cid_list: list) -> list:
    """
    逐个身体部位与全部服装部位、有意识与无意识两种状态取候选地文，收集不合要求的组合
    Keyword arguments:
    behavior_id -- 行为id
    body_cid_list -- 要检查的身体部位cid列表
    Return arguments:
    list -- [(部位前提, 意识状态, 本部位差分条数, 混入的其他部位地文, 无意识时混入的清醒文本)]，全部合格时为空
    """
    wrong_list = []
    for part_type, cid_list in ((0, body_cid_list), (1, sorted(game_config.config_clothing_type))):
        for part_cid in cid_list:
            position_token = f"CVP_A2_CondomPos|{'B' if part_type == 0 else 'C'}{part_cid}_E_1"
            for unconscious, state in ((0, "t_unconscious_flag_0"), (1, "t_unconscious_flag")):
                candidate_list = pick_candidate(part_type, part_cid, unconscious, behavior_id)
                part_line_list = [talk_cid for talk_cid, premise_set in candidate_list if any(premise.startswith("CVP_A2_CondomPos") for premise in premise_set)]
                other_part_list = [talk_cid for talk_cid, premise_set in candidate_list if any(premise.startswith("CVP_A2_CondomPos") and premise != position_token for premise in premise_set)]
                conscious_leak_list = [talk_cid for talk_cid, premise_set in candidate_list if unconscious and not any("unconscious" in premise for premise in premise_set)]
                if len(part_line_list) < 10 or other_part_list or conscious_leak_list:
                    wrong_list.append((position_token, state, len(part_line_list), other_part_list[:3], conscious_leak_list[:3]))
    return wrong_list


wrong_list = collect_wrong_selection("squeeze_condom_semen", SQUEEZE_BODY_LIST)
check("挤出：16 个可选身体部位与全部服装部位、有意识与无意识两种状态：都至少选得出 10 条本部位的差分，不混入其他部位的，对方无意识时也不混入清醒反应的文本",
      wrong_list == [], wrong_list[:5])
wrong_list = collect_wrong_selection("hang_condom_decoration", [0, 3])
check("挂装饰：头发、胸部（系在乳头上）与全部服装部位、有意识与无意识两种状态：同样各自选得出 10 条以上本部位的差分，不串部位、无意识时不混入清醒文本",
      wrong_list == [], wrong_list[:5])
wrong_list = collect_wrong_selection("take_back_condom_decoration", [0, 3])
check("取回装饰：头发、胸部与全部服装部位、有意识与无意识两种状态：同样各自选得出 10 条以上本部位的差分，不串部位、无意识时不混入清醒文本",
      wrong_list == [], wrong_list[:5])
set_virgin(target, True)
pl.item[condom_handle.SYRINGE_ITEM_ID] = 1
syringe_candidate = pick_candidate(0, 6, 0)
check("对方仍是处女、用针筒注入小穴时，不会选到「直接挤进小穴」的差分（那些文本要求不是针筒注入）",
      not [talk_cid for talk_cid, premise_set in syringe_candidate if "CVP_A2_CondomPos|B6_E_1" in premise_set]
      and any("condom_operation_syringe_to_vagina" in premise_set for _talk_cid, premise_set in syringe_candidate))
target.sp_flag.unconscious_h = 0
pl.behavior.behavior_id = saved_behavior_id
pl.behavior.condom_position = -1

# ==== 4c. 地文的显示 ====
section("挤出地文的显示：每一行都能替换完占位符，服装名取对方正穿戴的衣物，没穿时给兜底文本")
from Script.Design import talk  # noqa: E402

saved_cloth_wear_dict = {clothing_type: list(cloth_list) for clothing_type, cloth_list in target.cloth.cloth_wear.items()}
cloth_of_type = {}
for cloth_id, cloth_config in game_config.config_clothing_tem.items():
    cloth_of_type.setdefault(cloth_config.clothing_type, cloth_id)
any_cloth_id = next(iter(game_config.config_clothing_tem))
for clothing_type in game_config.config_clothing_type:
    target.cloth.cloth_wear[clothing_type] = [cloth_of_type.get(clothing_type, any_cloth_id)]
render_error_list = []
leftover_list = []
for talk_cid, talk_data in game_config.config_talk.items():
    if talk_data.behavior_id not in ("squeeze_condom_semen", "hang_condom_decoration", "take_back_condom_decoration"):
        continue
    try:
        render_text = talk.code_text_to_draw_text(talk_data.context, 0)
    except Exception as error:  # noqa: BLE001  占位符缺失会抛 KeyError，要把它变成失败的断言
        render_error_list.append((talk_cid, repr(error)))
        continue
    if "{" in render_text or "}" in render_text:
        leftover_list.append(talk_cid)
check("对方各部位都穿戴着衣物时，挤出避孕套精液、挂避孕套装饰与取回避孕套装饰的全部文本都能显示、不残留占位符", render_error_list == [] and leftover_list == [], (render_error_list[:3], leftover_list[:3]))
glasses_name = game_config.config_clothing_tem[target.cloth.cloth_wear[1][0]].name
weapon_name = game_config.config_clothing_tem[target.cloth.cloth_wear[12][0]].name
render_text = talk.code_text_to_draw_text("{TargetGlassesName}|{TargetWeaponName}", 0)
check("眼镜 / 武器占位符换成对方正穿戴的那件的名字", render_text == f"{glasses_name}|{weapon_name}", render_text)
target.cloth.cloth_wear[13] = [any_cloth_id, cloth_of_type.get(13, any_cloth_id)]
render_text = talk.code_text_to_draw_text("{TargetAttachmentName}", 0)
check("同一部位穿戴两件时用顿号连接", render_text == "、".join(game_config.config_clothing_tem[cloth_id].name for cloth_id in target.cloth.cloth_wear[13]), render_text)
target.cloth.cloth_wear[0] = []
target.cloth.cloth_wear[11] = []
render_text = talk.code_text_to_draw_text("{TargetHatName}|{TargetShoeName}", 0)
check("没戴帽子、没穿鞋子时给兜底文本", render_text == _("没戴帽子的头顶") + "|" + _("没穿鞋子的双脚"), render_text)

# 服装名占位符合并成统一循环后，原有各项的取值规则不变
up_cloth_name = game_config.config_clothing_tem[target.cloth.cloth_wear[5][0]].name
pan_cloth_name = game_config.config_clothing_tem[target.cloth.cloth_wear[9][0]].name
render_text = talk.code_text_to_draw_text("{SelfUpClothName}|{SelfDownClothName}|{UpClothName}|{TargetUpClothName}", 0)
check("玩家视角：自己的上衣 / 下衣固定为兜帽与长裤，「自己穿着的上衣」为兜底文本，对方的上衣取她正穿着的",
      render_text == "|".join([_("兜帽"), _("长裤"), _("没有穿上衣的裸露身体"), up_cloth_name]), render_text)
saved_pan_name, saved_socks_name = pl.behavior.pan_name, pl.behavior.socks_name
target.cloth.cloth_wear[9] = []
pl.behavior.pan_name = "测试用内裤"
render_text = talk.code_text_to_draw_text("{TargetPanName}", 0)
pl.behavior.pan_name = ""
render_text += "|" + talk.code_text_to_draw_text("{TargetPanName}", 0)
check("玩家视角：对方没穿内裤时先用行动记下的内裤名，没有再用兜底文本", render_text == "测试用内裤|" + _("没有穿内裤的阴部"), render_text)
target.cloth.cloth_wear[9] = [cloth_of_type.get(9, any_cloth_id)]
target.cloth.cloth_wear[10] = []
pl.behavior.socks_name = "测试用袜子"
saved_target_target = target.target_character_id
target.target_character_id = 0
render_text = talk.code_text_to_draw_text("{UpClothName}|{SelfUpClothName}|{PanName}|{SocName}|{TargetUpClothName}", TARGET_ID)
check("NPC 视角：自己的上衣 / 内裤取她正穿着的，没穿袜子时用行动记下的袜子名，「对方的上衣」为兜底文本",
      render_text == "|".join([up_cloth_name, up_cloth_name, pan_cloth_name, "测试用袜子", _("没有穿上衣的裸露身体")]), render_text)
bra_cloth_name = game_config.config_clothing_tem[target.cloth.cloth_wear[6][0]].name
render_text = talk.code_text_to_draw_text("{SelfWeaponName}|{SelfBraName}|{SelfHatName}|{SelfSocName}|{TargetWeaponName}", TARGET_ID)
check("NPC 视角：Self 组取她自己正穿戴的（没戴帽子给兜底，没穿袜子用行动记下的名字），Target 组为兜底文本",
      render_text == "|".join([weapon_name, bra_cloth_name, _("没戴帽子的头顶"), "测试用袜子", _("没拿武器的双手")]), render_text)
pl.behavior.socks_name = ""
render_text = talk.code_text_to_draw_text("{SelfWeaponName}|{SelfSocName}|{SocName}", 0)
check("玩家视角：Self 组为兜底文本，与不带前缀的旧名一致", render_text == "|".join([_("没拿武器的双手"), _("没有穿袜子的双腿"), _("没有穿袜子的双腿")]), render_text)
target.target_character_id = saved_target_target
pl.behavior.pan_name, pl.behavior.socks_name = saved_pan_name, saved_socks_name
target.cloth.cloth_wear = saved_cloth_wear_dict

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
