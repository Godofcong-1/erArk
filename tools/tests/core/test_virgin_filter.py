# -*- coding: UTF-8 -*-
"""自动挑选行为时的处女过滤：干员还保有某项处女时，NPC 逆推、群交模板各部位的行为列表（含 NPC 自动补位与抢占）、调教助手都不选会夺走它的破处类行为；判定函数的对应关系与数据一致"""
import random
from unittest import mock

from _bootstrap import *  # noqa: F401,F403
from Script.Design import handle_npc_ai_in_h, update, virgin_break_gate
from Script.System.Instruct_System import see_instruct_panel
from Script.System.Sex_System import group_sex_panel
from Script.UI.Panel import confinement_and_training

cache.debug_mode = False
PART_TABLE = game_config.config_behavior_id_list_of_group_sex_body_part
TAG_OF = {behavior_id: set(behavior_data.tag.split("|")) for behavior_id, behavior_data in game_config.config_behavior.items()}
# 设计：处女类素质 → 会夺走它的破处行为所带的部位标签（阴道处女同时对应 V 与 W，见第 1 节）
VIRGIN_PART = {0: {"V", "W"}, 1: {"A"}, 2: {"U"}, 3: {"W"}, 4: {"N"}}
SINGLE_SLOT_SET = {"mouth", "L_hand", "R_hand", "penis", "anal"}


def pass_all_instruct_filter(instruct_id, now_premise_data, *_args, **_kwargs):
    """
    顶替 see_instruct_panel.judge_single_instruct_filter：所有指令都算可用（这里只锁「按处女素质过滤」这一步）
    Keyword arguments:
    instruct_id -- 指令id
    now_premise_data -- 已算过的前提
    Return arguments:
    tuple -- (True, 已算过的前提)
    """
    return True, now_premise_data


def takes_virginity(behavior_id: str, talent_id_set: set) -> bool:
    """
    按设计的对应关系判断一个行为会不会夺走给定的处女类素质之一（不调用被测函数）
    Keyword arguments:
    behavior_id -- 行为id
    talent_id_set -- 仍保有的处女类素质id集合
    Return arguments:
    bool -- 会夺走其中某一项
    """
    tag_set = TAG_OF[behavior_id]
    return "破处" in tag_set and any(tag_set & VIRGIN_PART[talent_id] for talent_id in talent_id_set)


def set_virgin(character_data: game_type.Character, talent_id_set: set) -> None:
    """
    设定角色保有哪些处女类素质
    Keyword arguments:
    character_data -- 角色
    talent_id_set -- 保有的处女类素质id集合
    Return arguments:
    无
    """
    for talent_id in range(5):
        character_data.talent[talent_id] = 1 if talent_id in talent_id_set else 0


def call(func, *args):
    """
    调用一个可能抛异常的函数，把异常变成返回值
    Keyword arguments:
    func -- 要调用的函数
    args -- 传给它的参数
    Return arguments:
    tuple -- (是否没有抛异常, 返回值或异常的 repr)
    """
    try:
        return True, func(*args)
    except Exception as error:  # noqa: BLE001
        return False, repr(error)[:120]


section("1. 判定函数与数据")
first_sex_effect = constant_effect.BehaviorEffect.FIRST_SEX
womb_break_list = [behavior_id for behavior_id, tag_set in TAG_OF.items() if {"破处", "W"} <= tag_set]
no_first_sex = [behavior_id for behavior_id in womb_break_list if first_sex_effect not in game_config.config_behavior_effect_data.get(behavior_id, [])]
check("带破处与 W 标签的行为，结算里都有阴道破处那一条（所以阴道处女也要挡 W 类破处行为）", len(womb_break_list) > 0 and not no_first_sex, (len(womb_break_list), no_first_sex[:5]))
table = {
    "不带破处": virgin_break_gate.takes_kept_virginity(["性爱", "V", "插入"], {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}),
    "V破处-阴道处女": virgin_break_gate.takes_kept_virginity(["性爱", "V", "破处"], {0: 1, 1: 0, 2: 0, 3: 0, 4: 0}),
    "W破处-阴道处女": virgin_break_gate.takes_kept_virginity(["性爱", "W", "破处"], {0: 1, 1: 0, 2: 0, 3: 0, 4: 0}),
    "W破处-子宫处女": virgin_break_gate.takes_kept_virginity(["性爱", "W", "破处"], {0: 0, 1: 0, 2: 0, 3: 1, 4: 0}),
    "V破处-只有子宫处女": virgin_break_gate.takes_kept_virginity(["性爱", "V", "破处"], {0: 0, 1: 0, 2: 0, 3: 1, 4: 0}),
    "A破处-肛门处女": virgin_break_gate.takes_kept_virginity(["性爱", "A", "破处"], {0: 0, 1: 1, 2: 0, 3: 0, 4: 0}),
    "A破处-阴道处女": virgin_break_gate.takes_kept_virginity(["性爱", "A", "破处"], {0: 1, 1: 0, 2: 0, 3: 0, 4: 0}),
    "U破处-尿道处女": virgin_break_gate.takes_kept_virginity(["性爱", "U", "破处"], {0: 0, 1: 0, 2: 1, 3: 0, 4: 0}),
    "N破处-无接吻经验": virgin_break_gate.takes_kept_virginity(["性爱", "N", "口", "破处"], {0: 0, 1: 0, 2: 0, 3: 0, 4: 1}),
    "N破处-都不是处": virgin_break_gate.takes_kept_virginity(["性爱", "N", "口", "破处"], {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}),
    "素质表缺项": virgin_break_gate.takes_kept_virginity(["性爱", "V", "破处"], {}),
}
expect = {"不带破处": False, "V破处-阴道处女": True, "W破处-阴道处女": True, "W破处-子宫处女": True, "V破处-只有子宫处女": False, "A破处-肛门处女": True, "A破处-阴道处女": False,
          "U破处-尿道处女": True, "N破处-无接吻经验": True, "N破处-都不是处": False, "素质表缺项": False}
check("判定函数：带破处、且带仍保有的处女素质对应部位标签时才算会夺走", table == expect, {key: value for key, value in table.items() if value != expect[key]})

section("2. 群交模板各部位的行为列表")
target = make_character(801, "群交对象")
helper = make_character(802, "已在模板里的干员")
for character_data in (pl, target, helper):
    character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
saved_group_sex_mode = cache.group_sex_mode
cache.group_sex_mode = True


def slot_list(slot: str, talent_id_set: set, target_id: int = 801) -> list:
    """
    交互对象保有给定的处女素质时，群交模板某个部位可选的行为列表
    Keyword arguments:
    slot -- 部位（mouth / L_hand / penis / anal / 侍奉）
    talent_id_set -- 交互对象保有的处女类素质id集合
    target_id -- 玩家的交互对象
    Return arguments:
    list -- 行为id列表
    """
    set_virgin(target, talent_id_set)
    pl.target_character_id = target_id
    with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter):
        return group_sex_panel.get_status_id_list_from_group_sex_body_part(slot)


all_virgin = {0, 1, 2, 3, 4}
free_list = slot_list("penis", set())
check("交互对象不是处时，阴茎一栏列出插入类行为（其中有破处类）", len(free_list) > 0 and set(free_list) <= set(PART_TABLE["插入"]) and any("破处" in TAG_OF[b] for b in free_list), len(free_list))
check("交互对象各项都还是处时，阴茎一栏不列任何会破处的行为", [b for b in slot_list("penis", all_virgin) if takes_virginity(b, all_virgin)] == [], slot_list("penis", all_virgin)[:5])
only_v = slot_list("penis", {0})
check("只是阴道处女时，阴茎一栏去掉 V 与 W 的破处行为，A 与 U 的照常列出",
      not [b for b in only_v if TAG_OF[b] & {"V", "W"}] and any("A" in TAG_OF[b] for b in only_v) and any("U" in TAG_OF[b] for b in only_v), [b for b in only_v if TAG_OF[b] & {"V", "W"}][:5])
only_w = slot_list("penis", {3})
check("只是子宫处女时，阴茎一栏去掉 W 的破处行为，V 的照常列出", not [b for b in only_w if "W" in TAG_OF[b]] and any("V" in TAG_OF[b] for b in only_w), [b for b in only_w if "W" in TAG_OF[b]][:5])
no_kiss_mouth, no_kiss_serve, no_kiss_penis = slot_list("mouth", {4}), slot_list("侍奉", {4}), slot_list("penis", {4})
check("没有接吻经验时，嘴与侍奉两栏去掉带 N 的破处行为（其余照常列出），阴茎一栏不受影响",
      len(no_kiss_mouth) > 0 and len(no_kiss_serve) > 0 and not [b for b in no_kiss_mouth + no_kiss_serve if takes_virginity(b, {4})] and set(no_kiss_penis) == set(free_list),
      [b for b in no_kiss_mouth + no_kiss_serve if takes_virginity(b, {4})][:5])
check("嘴与侍奉两栏在对象有接吻经验时确实有带 N 的破处行为（上一条才有意义）", any(takes_virginity(b, {4}) for b in slot_list("mouth", set())) and any(takes_virginity(b, {4}) for b in slot_list("侍奉", set())))
set_virgin(target, all_virgin)
pl.target_character_id = 0
with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter):
    ok, value = call(group_sex_panel.get_status_id_list_from_group_sex_body_part, "penis")
check("玩家没有交互对象时照常列出、不报错", ok and set(value) == set(free_list), str(value)[:100])

section("3. 群交里 NPC 自动补位与抢占")
move_to(801, SCENE_DORM)
move_to(802, SCENE_DORM)
move_to(0, SCENE_DORM)
target.sp_flag.is_h = True
helper.sp_flag.is_h = True
hand_behavior = PART_TABLE["手"][0]
mouth_behavior = [b for b in PART_TABLE["口"] if "破处" not in TAG_OF[b]][0]
anal_behavior = PART_TABLE["肛"][0]


def only_penis_empty_template() -> list:
    """把模板摆成「只有阴茎与侍奉空着，其余部位都由另一名干员占着」，返回模板"""
    pl.h_state = attr_calculation.get_h_state_reset(pl.h_state)
    now_template = pl.h_state.group_sex_body_template_dict["A"]
    now_template[0]["mouth"] = [802, mouth_behavior]
    now_template[0]["L_hand"] = [802, hand_behavior]
    now_template[0]["R_hand"] = [802, hand_behavior]
    now_template[0]["anal"] = [802, anal_behavior]
    return now_template


set_virgin(target, all_virgin)
target.sp_flag.masturebate = 0
template = only_penis_empty_template()
with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), mock.patch.object(random, "choice", lambda candidate_list: candidate_list[0]):
    ok, value = call(handle_npc_ai_in_h.npc_ai_in_group_sex, 801)
check("还是处的干员自动补位抽到阴茎一栏时不补（不会由她自动完成破处）", ok and template[0]["penis"] == [-1, -1] and set(template[0]) == SINGLE_SLOT_SET, (value, template[0]["penis"]))

template = only_penis_empty_template()
with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), mock.patch.object(random, "choice", lambda candidate_list: candidate_list[0]), \
        mock.patch.object(random, "randint", lambda _low, _high: 0):
    ok, value = call(handle_npc_ai_in_h.npc_ai_in_group_sex_type_3)
serve_ok = template[1][0] == [801] and template[1][1] in PART_TABLE["侍奉"] and not takes_virginity(template[1][1], all_virgin)
check("抢占时还是处的干员抢不到阴茎一栏也不报错，改去别的空位（侍奉）且选的不是破处行为",
      ok and template[0]["penis"] == [-1, -1] and set(template[0]) == SINGLE_SLOT_SET and serve_ok, (value, template[0]["penis"], template[1]))

set_virgin(target, set())
template = only_penis_empty_template()
with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), mock.patch.object(random, "choice", lambda candidate_list: candidate_list[0]), \
        mock.patch.object(random, "randint", lambda _low, _high: 0):
    ok, value = call(handle_npc_ai_in_h.npc_ai_in_group_sex_type_3)
check("不是处的干员照常抢到阴茎一栏", ok and template[0]["penis"][0] == 801 and template[0]["penis"][1] in PART_TABLE["插入"], (value, template[0]["penis"]))
# 加入已有的侍奉、顶替别人占着的部位：沿用的是模板里现成的指令，也要过同一道判定
break_serve = [b for b in PART_TABLE["侍奉"] if takes_virginity(b, {4})][0]
safe_serve = [b for b in PART_TABLE["侍奉"] if "破处" not in TAG_OF[b]][0]
break_insert = [b for b in PART_TABLE["插入"] if takes_virginity(b, {0})][0]


def full_template(serve_behavior, penis_behavior) -> list:
    """把模板摆满：单人部位都由另一名干员占着，阴茎与侍奉二选一（给了哪个指令就占哪个），返回模板"""
    now_template = only_penis_empty_template()
    if penis_behavior is not None:
        now_template[0]["penis"] = [802, penis_behavior]
    if serve_behavior is not None:
        now_template[1] = [[802], serve_behavior]
    return now_template


def run_join(serve_behavior, talent_id_set: set) -> tuple:
    """模板里已有侍奉指令时，让 801 自动补位（会抽到「加入侍奉」），返回 (是否没报错, 侍奉栏的角色列表)"""
    set_virgin(target, talent_id_set)
    now_template = full_template(serve_behavior, None)
    with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), mock.patch.object(random, "choice", lambda candidate_list: candidate_list[-1]):
        ok, _value = call(handle_npc_ai_in_h.npc_ai_in_group_sex, 801)
    return ok, list(now_template[1][0])


def run_takeover(serve_behavior, penis_behavior, talent_id_set: set, serve_member_list=None) -> tuple:
    """
    模板摆满时让 801 抢占，且只结算「阴茎 / 侍奉」那一个已占部位（其余已占部位都掷成跳过）
    Keyword arguments:
    serve_behavior -- 侍奉栏的指令，None 表示侍奉栏空着
    penis_behavior -- 阴茎栏的指令，None 表示阴茎栏空着
    talent_id_set -- 801 保有的处女类素质id集合
    serve_member_list -- 侍奉栏里已有的角色，默认只有 802
    Return arguments:
    tuple -- (是否没报错, 阴茎栏的角色, 侍奉栏的角色列表)
    """
    set_virgin(target, talent_id_set)
    now_template = full_template(serve_behavior, penis_behavior)
    if serve_member_list is not None:
        now_template[1][0] = list(serve_member_list)
    not_empty_list = group_sex_panel.get_now_template_part_list()[1]
    wanted_part = "penis" if penis_behavior is not None else "侍奉"
    # 抢占时每个已占部位先掷一次「要不要结算」（掷出 1 为跳过）：按部位顺序只让目标部位掷出 0
    skip_roll = iter([0 if part == wanted_part else 1 for part in not_empty_list])
    with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), mock.patch.object(random, "choice", lambda candidate_list: candidate_list[-1]), \
            mock.patch.object(random, "randint", lambda _low, _high: next(skip_roll, 1)):
        ok, _value = call(handle_npc_ai_in_h.npc_ai_in_group_sex_type_3)
    return ok, now_template[0]["penis"][0], list(now_template[1][0])


check("自动补位：没有接吻经验的干员不加入会夺走初吻的侍奉指令，有接吻经验的照常加入、不破处的侍奉指令也照常加入",
      (run_join(break_serve, {4}), run_join(break_serve, set()), run_join(safe_serve, {4})) == ((True, [802]), (True, [802, 801]), (True, [802, 801])),
      (run_join(break_serve, {4}), run_join(break_serve, set()), run_join(safe_serve, {4})))
check("抢占：阴道处女不顶替别人正在做的插入指令，不是处的照常顶替",
      (run_takeover(None, break_insert, {0})[:2], run_takeover(None, break_insert, set())[:2]) == ((True, 802), (True, 801)),
      (run_takeover(None, break_insert, {0}), run_takeover(None, break_insert, set())))
check("抢占：没有接吻经验的干员不加入别人正在做的、会夺走初吻的侍奉指令，有接吻经验的照常加入",
      (run_takeover(break_serve, None, {4})[2], 801 in run_takeover(break_serve, None, set())[2]) == ([802], True),
      (run_takeover(break_serve, None, {4}), run_takeover(break_serve, None, set())))
full_serve = [802, 803, 804, 805]
check("抢占：侍奉已满 4 人时，没有接吻经验的干员不顶替进会夺走初吻的侍奉指令，有接吻经验的照常顶替掉排在最前的人",
      (run_takeover(break_serve, None, {4}, full_serve)[2], run_takeover(break_serve, None, set(), full_serve)[2]) == ([802, 803, 804, 805], [803, 804, 805, 801]),
      (run_takeover(break_serve, None, {4}, full_serve), run_takeover(break_serve, None, set(), full_serve)))
pl.h_state = attr_calculation.get_h_state_reset(pl.h_state)
cache.group_sex_mode = saved_group_sex_mode

section("4. 调教助手可用的行为")
pl.target_character_id = 801
set_virgin(target, set())
with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter):
    assistant_free = confinement_and_training.get_all_can_use_behavior_id_for_sex_assistant()
set_virgin(target, all_virgin)
with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter):
    assistant_virgin = confinement_and_training.get_all_can_use_behavior_id_for_sex_assistant()
check("调教对象不是处时，调教助手可用的行为里有破处类（下一条才有意义）", any("破处" in TAG_OF[b] for b in assistant_free), len(assistant_free))
check("调教对象各项都还是处时，调教助手不用会破处的行为，其余行为照常可用",
      len(assistant_virgin) > 0 and not [b for b in assistant_virgin if takes_virginity(b, all_virgin)] and set(assistant_virgin) == {b for b in assistant_free if not takes_virginity(b, all_virgin)},
      [b for b in assistant_virgin if takes_virginity(b, all_virgin)][:5])

section("5. NPC 逆推")
target.h_state.npc_active_h = True
part_id_list = sorted(state_id for state_id, state_data in game_config.config_character_state.items() if state_data.type == 0)
candidate_log = []


def active_h_candidate(part_id: int, talent_id_set: set) -> list:
    """
    指定部位喜好与处女素质下，逆推时的候选行为列表
    Keyword arguments:
    part_id -- 部位喜好
    talent_id_set -- 她保有的处女类素质id集合
    Return arguments:
    list -- 候选行为id列表（一个都没有时为空）
    """
    candidate_log.clear()
    set_virgin(target, talent_id_set)

    def record_choice(candidate_list):
        """记下候选并固定选第一个"""
        candidate_log.append(list(candidate_list))
        return candidate_list[0]

    with mock.patch.object(see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), mock.patch.object(update, "game_update_flow", lambda *_a, **_k: None), \
            mock.patch.object(handle_npc_ai_in_h, "evaluate_npc_body_part_prefs", lambda _cid: part_id), mock.patch.object(random, "choice", record_choice):
        handle_npc_ai_in_h.npc_active_h()
    return candidate_log[0] if candidate_log else []


check("部位喜好的取值不止 V / A / U / W 四个（下面按全部取值逐个检查）", len(part_id_list) > 7, part_id_list)
wrong = {}
kept_break = 0
for part_id in part_id_list:
    for talent_id in range(5):
        candidate_list = active_h_candidate(part_id, {talent_id})
        bad_list = [b for b in candidate_list if takes_virginity(b, {talent_id})]
        if bad_list:
            wrong[(part_id, talent_id)] = bad_list[:3]
    kept_break += len([b for b in active_h_candidate(part_id, set()) if "破处" in TAG_OF[b]])
check("她都不是处时，逆推的候选里有破处类行为（下一条才有意义）", kept_break > 0, kept_break)
check("不论部位喜好是哪一个，她还保有某项处女时，逆推都不选会夺走它的破处行为（键为 (部位喜好, 处女素质)）", not wrong, wrong)
mix = active_h_candidate(4, {3})
check("她只是子宫处女、喜好部位为 V 时，V 的破处行为照常可选", any({"V", "破处"} <= TAG_OF[b] for b in mix), len(mix))
target.h_state.npc_active_h = False
pl.target_character_id = 0
remove_character(801)
remove_character(802)

finish()
