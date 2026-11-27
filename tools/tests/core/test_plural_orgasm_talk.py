# -*- coding: UTF-8 -*-
"""多重绝顶的组合纸娃娃地文：分组（每部位取最高程度、固定部位顺序、整组只出一次组合文本、效果照常结算）、组合规则（每部位从 A/B/C 合并抽一段、没有纸娃娃地文时用单部位地文补位、角色口上单独显示、各段先按 A→B→C 分组再按部位排列、提示行合并成一行）"""
from _bootstrap import *  # noqa: F401,F403
import random
from unittest import mock

from Script.Design import second_behavior, talk

NPC_ID = 1
""" 绝顶的干员 """
npc = make_character(NPC_ID, "测试干员")
npc.talent[105] = 1  # 大姐姐：明确成年（游戏本体分组时会做组合文本的判定，测试干员需满足才走得到组合文本）
pl.target_character_id = NPC_ID

PART_ID_LIST = ["b_orgasm_small", "b_orgasm_strong", "c_orgasm_small", "v_orgasm_strong", "f_orgasm_normal"]
""" 一次四重绝顶里的部位绝顶行为：胸部同时有小绝顶与强绝顶 """
PLURAL_ID = "plural_orgasm_4"


def run_second_behavior_effect(behavior_id_list: list, orgasm_settle_flag: bool = True) -> list:
    """
    只激活给出的二段行为后跑一次二段结算，记录文本触发的顺序（单独文本与组合文本都换成记录桩）
    Keyword arguments:
    behavior_id_list -- 要激活的二段行为id列表
    orgasm_settle_flag -- 是否按高潮结算调用
    Return arguments:
    list -- 文本触发记录：("单独", 行为id) 或 ("组合", 多重绝顶行为id, 部位行为id列表)
    """
    for behavior_id in npc.second_behavior:
        npc.second_behavior[behavior_id] = 0
    for behavior_id in behavior_id_list:
        npc.second_behavior[behavior_id] = 1
    npc.h_state.plural_orgasm_set = {1, 2, 4, 22}
    call_log = []
    orgasm_list = [behavior_id for behavior_id in npc.second_behavior if "orgasm" in behavior_id]
    with mock.patch.object(talk, "handle_second_talk", lambda character_id, behavior_id="share_blankly": call_log.append(("单独", behavior_id))), \
            mock.patch.object(talk, "handle_plural_orgasm_talk", lambda character_id, plural_id, part_list: call_log.append(("组合", plural_id, list(part_list)))):
        second_behavior.second_behavior_effect(NPC_ID, game_type.CharacterStatusChange(), orgasm_list if orgasm_settle_flag else [], orgasm_settle_flag=orgasm_settle_flag)
    return call_log


# ==== 1. 分组 ====
section("分组：多重绝顶时整组只出一次组合文本，每部位取最高程度、按固定部位顺序，其余二段行为与效果照常")
behavior_list = PART_ID_LIST + [PLURAL_ID, "extra_orgasm"]
call_log = run_second_behavior_effect(behavior_list)
check(
    "组合文本只触发一次，部位按皮肤→胸部→阴蒂→阴道→…→兽部排列、胸部取强绝顶；额外绝顶照常单独出文本且排在组合之后",
    call_log == [("组合", PLURAL_ID, ["b_orgasm_strong", "c_orgasm_small", "v_orgasm_strong", "f_orgasm_normal"]), ("单独", "extra_orgasm")],
    call_log,
)
check("组内各行为（含较低程度的胸部小绝顶与多重绝顶本身）的效果照常结算、行为值归零", all(npc.second_behavior[behavior_id] == 0 for behavior_id in behavior_list), {k: npc.second_behavior[k] for k in behavior_list})

call_log = run_second_behavior_effect(["b_orgasm_strong", "extra_orgasm"])
check("只有一个部位绝顶（没有多重绝顶）时照旧单独出文本", call_log == [("单独", "b_orgasm_strong"), ("单独", "extra_orgasm")], call_log)

call_log = run_second_behavior_effect(behavior_list, orgasm_settle_flag=False)
check("不是高潮结算的调用不分组，逐个照旧出文本", ("组合", PLURAL_ID, ["b_orgasm_strong", "c_orgasm_small", "v_orgasm_strong", "f_orgasm_normal"]) not in call_log and ("单独", PLURAL_ID) in call_log, call_log)

# ==== 2. 组合规则（假数据） ====
section("组合规则：每部位从 A/B/C 合并抽一段，没有纸娃娃地文时用单部位地文补位，有角色口上的部位单独显示口上，提示行合并成一行")
fake_common_data = {
    "cb_A": mock.Mock(context="〔胸A〕", type_id="action_part_b_orgasm_strong_A"),
    "cb_B": mock.Mock(context="〔胸B〕", type_id="action_part_b_orgasm_strong_B"),
    "cb_C": mock.Mock(context="〔胸C〕", type_id="action_part_b_orgasm_strong_C"),
    "cc_A": mock.Mock(context="〔蒂A〕", type_id="action_part_c_orgasm_small_A"),
    "cv_A": mock.Mock(context="〔阴道纸娃娃〕", type_id="action_part_v_orgasm_strong_A"),
}
""" 纸娃娃地文：胸部强绝顶 A/B/C 各一条，阴蒂小绝顶只有 A，阴道强绝顶的唯一一条前提不满足 """
fake_common_by_type = {"b_orgasm_strong": ["cb_A", "cb_B", "cb_C"], "c_orgasm_small": ["cc_A"], "v_orgasm_strong": ["cv_A"]}
fake_common_premise = {"cb_A": set(), "cb_B": set(), "cb_C": set(), "cc_A": set(), "cv_A": {"never"}}
fake_talk = {
    "t_b": mock.Mock(adv_id=0, context="〔胸单部位〕", behavior_id="b_orgasm_strong"),
    "t_c": mock.Mock(adv_id=0, context="〔蒂单部位〕", behavior_id="c_orgasm_small"),
    "t_v": mock.Mock(adv_id=0, context="〔阴道单部位〕", behavior_id="v_orgasm_strong"),
    "t_f": mock.Mock(adv_id=0, context="〔兽单部位〕", behavior_id="f_orgasm_normal"),
    "t_f_adv": mock.Mock(adv_id=NPC_ID, context="〔兽口上〕", behavior_id="f_orgasm_normal"),
}
""" 单部位文本：各部位都有地文，兽部另有一条角色口上 """
fake_talk_sub_data = {
    "b_orgasm_strong": {1: {"t_b"}},
    "c_orgasm_small": {1: {"t_c"}},
    "v_orgasm_strong": {1: {"t_v"}},
    "f_orgasm_normal": {10: {"t_f_adv"}, 1: {"t_f"}},
}
weight_subject_log = []
""" 纸娃娃地文求值时的（主体, 玩家的交互对象） """


def fake_weight(premise_set, character_id, calculated_premise_dict, **kwargs) -> tuple:
    """
    假的前提求值：前提里有 never 的不通过，其余权重 1；顺带记下求值时的主体与玩家的交互对象
    Keyword arguments:
    premise_set -- 前提集合
    character_id -- 主体角色id
    calculated_premise_dict -- 已算过的前提
    Return arguments:
    tuple -- (权重, 原样的已算前提)
    """
    weight_subject_log.append((character_id, cache.character_data[0].target_character_id))
    return (0 if "never" in premise_set else 1), calculated_premise_dict


def fake_handle_talk_sub(character_id, behavior_id, calculated_premise_dict={}, unconscious_pass_flag=False) -> tuple:
    """
    假的单部位文本候选
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 部位绝顶行为id
    calculated_premise_dict -- 已算过的前提
    unconscious_pass_flag -- 未使用
    Return arguments:
    tuple -- (权重->口上id集合, 原样的已算前提)
    """
    return {weight: set(id_set) for weight, id_set in fake_talk_sub_data.get(behavior_id, {}).items()}, calculated_premise_dict


def run_plural_talk(common_by_type: dict | None = None, part_list: list | None = None) -> list:
    """
    用假数据跑一次组合文本，返回最终送去绘制的文本记录
    Keyword arguments:
    common_by_type -- 各部位绝顶类型下的纸娃娃地文cid列表，默认 fake_common_by_type
    part_list -- 参与的各部位绝顶行为id（已按部位顺序），默认胸部强、阴蒂小、阴道强、兽部普通
    Return arguments:
    list -- [(文本, 行为id, 口上的角色adv)]
    """
    if common_by_type is None:
        common_by_type = fake_common_by_type
    if part_list is None:
        part_list = ["b_orgasm_strong", "c_orgasm_small", "v_orgasm_strong", "f_orgasm_normal"]
    draw_log = []
    with mock.patch.object(game_config, "config_talk_common_cid_list_by_type", common_by_type), \
            mock.patch.object(game_config, "config_talk_common_data", fake_common_data), \
            mock.patch.object(game_config, "config_talk_common_premise_data", fake_common_premise), \
            mock.patch.object(game_config, "config_talk_common_cid_list_by_part", {}), \
            mock.patch.dict(game_config.config_talk, fake_talk), \
            mock.patch.object(handle_premise, "get_weight_from_premise_dict", fake_weight), \
            mock.patch.object(talk, "handle_talk_sub", fake_handle_talk_sub), \
            mock.patch.object(talk, "draw_talk_text", lambda character_id, text, no_wait_flag, behavior_id, adv: draw_log.append((text, behavior_id, adv))):
        talk.handle_plural_orgasm_talk(NPC_ID, PLURAL_ID, part_list)
    return draw_log


pl.target_character_id = 0
drawn_text.clear()
bad_run_list = []
chosen_breast_set = set()
for seed in range(60):
    random.seed(seed)
    draw_log = run_plural_talk()
    breast_list = [segment for segment in ("〔胸A〕", "〔胸B〕", "〔胸C〕") if draw_log and segment in draw_log[0][0]]
    # 阴蒂 A 与补位的阴道单部位地文都在 A 组；胸部抽到 A 时排在 A 组最前（部位顺序胸部在先），抽到 B / C 时排在 A 组之后
    a_group_text = "〔蒂A〕\n〔阴道单部位〕\n"
    expected_text = ""
    if breast_list:
        expected_text = breast_list[0] + "\n" + a_group_text if breast_list[0] == "〔胸A〕" else a_group_text + breast_list[0] + "\n"
    if (
        len(draw_log) != 2
        or len(breast_list) != 1
        or draw_log[0] != (expected_text, PLURAL_ID, 0)
        or draw_log[1] != ("〔兽口上〕", "f_orgasm_normal", NPC_ID)
    ):
        bad_run_list.append((seed, draw_log))
    chosen_breast_set.update(breast_list)
check(
    "组合文本：胸部从 A/B/C 里只取一段，阴蒂取纸娃娃地文，阴道没有符合条件的纸娃娃地文时用单部位地文补位（归入 A 组），各段先按 A→B→C 分组、组内按部位排列；有口上的兽部不进组合，口上在组合之后单独显示",
    not bad_run_list,
    bad_run_list[:3],
)

# 按 A→B→C 分组、组内按部位排序：每个部位只给一个分段可选，结果唯一
fake_common_data.update({
    "cs_B": mock.Mock(context="〔皮肤B〕", type_id="action_part_s_orgasm_normal_B"),
    "cv_A_ok": mock.Mock(context="〔阴道A〕", type_id="action_part_v_orgasm_strong_A"),
    "cw_B": mock.Mock(context="〔子宫B〕", type_id="action_part_w_orgasm_small_B"),
})
fake_common_premise.update({"cs_B": set(), "cv_A_ok": set(), "cw_B": set()})
example_draw_log = run_plural_talk(
    {"b_orgasm_strong": ["cb_C"], "c_orgasm_small": ["cc_A"], "v_orgasm_strong": ["cv_A_ok"]},
    ["b_orgasm_strong", "c_orgasm_small", "v_orgasm_strong"],
)
check(
    "胸部强绝顶的 C、阴蒂小绝顶的 A、阴道强绝顶的 A：先输出两个 A（阴蒂在阴道之前），再输出胸部的 C",
    example_draw_log == [("〔蒂A〕\n〔阴道A〕\n〔胸C〕\n", PLURAL_ID, 0)],
    example_draw_log,
)
example_draw_log = run_plural_talk(
    {"s_orgasm_normal": ["cs_B"], "b_orgasm_strong": ["cb_C"], "c_orgasm_small": ["cc_A"], "v_orgasm_strong": ["cv_A_ok"], "w_orgasm_small": ["cw_B"]},
    ["s_orgasm_normal", "b_orgasm_strong", "c_orgasm_small", "v_orgasm_strong", "w_orgasm_small"],
)
check(
    "五个部位分属 A、B、C 三组时：A 组阴蒂→阴道，B 组皮肤→子宫，C 组胸部",
    example_draw_log == [("〔蒂A〕\n〔阴道A〕\n〔皮肤B〕\n〔子宫B〕\n〔胸C〕\n", PLURAL_ID, 0)],
    example_draw_log,
)
check("多次抽取中胸部的 A、B、C 三段都抽到过（三段合并抽取）", chosen_breast_set == {"〔胸A〕", "〔胸B〕", "〔胸C〕"}, chosen_breast_set)
check("有纸娃娃地文的部位不再用其单部位地文，也不出多重绝顶的占位地文", not any("〔胸单部位〕" in text or "〔蒂单部位〕" in text for text, _bid, _adv in run_plural_talk()))
expected_info = _("\n{0}{1}绝顶（{2}）\n").format(
    npc.name, _("四重"), _("、").join([_("胸部") + _("强绝顶"), _("阴蒂") + _("小绝顶"), _("阴道") + _("强绝顶"), _("兽部") + _("绝顶")])
)
check("提示行合并成一行，列出各部位的绝顶程度", any(expected_info in text for text in drawn_text), drawn_text[:3])
check("纸娃娃地文的前提以玩家为主体、玩家的交互对象临时设为该干员", weight_subject_log and set(weight_subject_log) == {(0, NPC_ID)}, set(weight_subject_log))
check("组合文本结束后玩家的交互对象还原", pl.target_character_id == 0, pl.target_character_id)

npc_draw_setting_old = cache.all_system_setting.draw_setting[2]
cache.all_system_setting.draw_setting[2] = 0
draw_log = run_plural_talk()
cache.all_system_setting.draw_setting[2] = npc_draw_setting_old
check("系统设置不使用地文时不选纸娃娃地文", draw_log and not any(segment in draw_log[0][0] for segment in ("〔胸A〕", "〔胸B〕", "〔胸C〕", "〔蒂A〕")), draw_log)
pl.target_character_id = NPC_ID


# ==== 3. 真实数据 ====
section("真实数据：绝顶纸娃娃地文不串部位，组合文本对各部位组合都能出")
ORGASM_PART_STR_LIST = ["s", "b", "c", "v", "a", "u", "w", "m", "f", "h"]
""" NPC 会绝顶的十个部位 """
bad_type_list = []
for part_str in ORGASM_PART_STR_LIST:
    for degree_str in ("small", "normal", "strong", "super"):
        type_id = f"{part_str}_orgasm_{degree_str}"
        for talk_common_cid in game_config.config_talk_common_cid_list_by_type.get(type_id, []):
            real_type_id = game_config.config_talk_common_data[talk_common_cid].type_id
            if real_type_id.split("part_")[-1][:-2] != type_id:
                bad_type_list.append((type_id, talk_common_cid, real_type_id))
check("每个部位绝顶类型下的纸娃娃地文都属于该部位该程度（组合时不会串部位）", not bad_type_list, bad_type_list[:5])

real_case_list = [
    ("plural_orgasm_2", ["b_orgasm_strong", "v_orgasm_normal"]),
    ("plural_orgasm_3", ["s_orgasm_small", "c_orgasm_super", "f_orgasm_normal"]),
    ("plural_orgasm_10", [f"{part_str}_orgasm_normal" for part_str in ORGASM_PART_STR_LIST]),
]
bad_real_list = []
for plural_id, part_list in real_case_list:
    real_draw_log = []
    try:
        with mock.patch.object(talk, "draw_talk_text", lambda character_id, text, no_wait_flag, behavior_id, adv: real_draw_log.append((behavior_id, adv, "重绝顶的地文" in text))):
            talk.handle_plural_orgasm_talk(NPC_ID, plural_id, part_list)
    except Exception as err:  # noqa: BLE001  报错要变成失败的断言
        bad_real_list.append((plural_id, repr(err)))
        continue
    if not real_draw_log or real_draw_log[0][0] != plural_id or any(has_placeholder for _bid, _adv, has_placeholder in real_draw_log):
        bad_real_list.append((plural_id, real_draw_log))
check("真实数据下各组合都能出组合文本，且不含多重绝顶的占位地文", not bad_real_list, bad_real_list)
check("真实数据跑完后玩家的交互对象还原", pl.target_character_id == NPC_ID, pl.target_character_id)

finish()
