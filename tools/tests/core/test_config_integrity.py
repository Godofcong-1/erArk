# -*- coding: UTF-8 -*-
"""配置交叉引用：行为→结算效果、二段行为→二段结算、AI目标→状态机与前提、指令→前提、蚀刻章→前置，以及三张注册表本身（运行时缺失只会静默跳过或打印报错的那类引用）"""
import collections
import csv

from _bootstrap import *  # noqa: F401,F403

# 本文件只做静态的 id 解析检查，不执行任何前提 / 结算 / 状态机，也不检查口上与事件正文

PREMISE = constant.handle_premise_data
""" 前提注册表：前提id → 处理函数 """
EFFECT = constant.settle_behavior_effect_data
""" 行为结算注册表：效果id → 处理函数 """
SECOND_EFFECT = constant.settle_second_behavior_effect_data
""" 二段行为结算注册表：效果id → 处理函数 """
STATE_MACHINE = constant.handle_state_machine_data
""" 状态机注册表：状态机id → 处理函数 """
SECOND_BEHAVIOR_ID_SET = set(attr_calculation.get_second_behavior_zero({}))
""" 二段行为id集合：角色 second_behavior 字典的键，这些行为的效果走二段结算注册表（second_behavior.py） """


def premise_resolves(premise_id: str) -> bool:
    """
    判断一个前提id在运行时能否解析到真实的判定
    handle_premise 对未注册、又不含 CVP 的前提id 静默返回 0，写错的前提不会报错，只会让条件永远不成立
    Keyword arguments:
    premise_id -- 前提id
    Return arguments:
    bool -- 能解析时为 True
    """
    if premise_id in PREMISE:
        return True
    # 综合数值前提：CVP_A_B_C_D 格式，至少要有对象、属性、比较三段
    return "CVP" in premise_id and len(premise_id.split("_")) >= 4


def first(item_list: list, count: int = 20) -> list:
    """
    取列表前若干项，用作断言失败时的附带信息
    Keyword arguments:
    item_list -- 列表
    count -- 项数
    Return arguments:
    list -- 截取后的列表
    """
    return sorted(item_list, key=str)[:count]


section("三张注册表本身")
check("前提注册表的值都可调用", all(callable(func) for func in PREMISE.values()))
check("行为结算与二段结算注册表的值都可调用", all(callable(func) for func in EFFECT.values()) and all(callable(func) for func in SECOND_EFFECT.values()))
check("状态机注册表的值都可调用", all(callable(func) for func in STATE_MACHINE.values()))
premise_constant_list = [value for name, value in vars(constant_promise.Premise).items() if not name.startswith("_") and isinstance(value, str)]
# 编辑器的前提表（tools/ArkEditor/csv/Premise.csv：前提id, 常量名, 分组, 说明）是前提的对外清单，说明里写了「弃用」的前提不再有处理函数
with open(os.path.join(ROOT, "tools", "ArkEditor", "csv", "Premise.csv"), encoding="utf-8") as premise_csv:
    editor_row_list = [row for row in csv.reader(premise_csv)][1:]
editor_premise_set = {row[0] for row in editor_row_list if row}
deprecated_premise_set = {row[0] for row in editor_row_list if len(row) >= 4 and "弃用" in row[3]}
unregistered_constant = [value for value in premise_constant_list if value not in PREMISE and value not in deprecated_premise_set]
check("constant_promise.Premise 里定义的前提常量都已注册处理函数（编辑器表中标了弃用的除外）", not unregistered_constant, first(unregistered_constant))
check("编辑器前提表与 Premise 常量一一对应（新增前提要同步进编辑器，见新增指令工作流）", editor_premise_set == set(premise_constant_list), first(editor_premise_set ^ set(premise_constant_list)))

section("行为 → 结算效果")
unknown_behavior = [behavior_id for behavior_id in game_config.config_behavior_effect_data if behavior_id not in game_config.config_behavior]
check("行为效果表里的行为都在行为表中", not unknown_behavior, first(unknown_behavior))
missing_main = []
missing_second = []
bad_str_effect = []
for behavior_id, effect_list in game_config.config_behavior_effect_data.items():
    for effect_id in effect_list:
        if isinstance(effect_id, str):
            # 字符串效果只认综合数值结算 CVE_A_B_C_D，其余字符串在 settle_behavior 里会被当成未注册的结算跳过
            if "CVE" not in effect_id or len(effect_id.split("_")) < 4:
                bad_str_effect.append((behavior_id, effect_id))
        elif behavior_id in SECOND_BEHAVIOR_ID_SET:
            if effect_id not in SECOND_EFFECT:
                missing_second.append((behavior_id, effect_id))
        elif effect_id not in EFFECT:
            missing_main.append((behavior_id, effect_id))
# 未注册的效果在 settle_behavior.handle_settle_behavior 里只打印「error 不存在的结算」后跳过，行为照常进行但该效果永远不生效
check("普通行为引用的结算效果都已注册", not missing_main, first(missing_main))
check("二段行为引用的二段结算效果都已注册", not missing_second, first(missing_second))
check("字符串形式的结算效果都是格式完整的综合数值结算（CVE）", not bad_str_effect, first(bad_str_effect))
second_without_effect = [behavior_id for behavior_id in SECOND_BEHAVIOR_ID_SET if behavior_id not in game_config.config_behavior_effect_data]
check("每个二段行为都配了结算效果（缺了的在 second_behavior 里每次触发都打印 debug 后跳过）", not second_without_effect, first(second_without_effect))
second_not_behavior = [behavior_id for behavior_id in SECOND_BEHAVIOR_ID_SET if behavior_id not in game_config.config_behavior]
check("每个二段行为都在行为表中", not second_not_behavior, first(second_not_behavior))

section("AI 目标 → 状态机与前提")
missing_state_machine = [(cid, target.state_machine_id) for cid, target in game_config.config_target.items() if target.state_machine_id not in STATE_MACHINE]
check("AI 目标引用的状态机都已注册", not missing_state_machine, first(missing_state_machine))
bad_target_premise = [(cid, premise_id) for cid, premise_set in game_config.config_target_premise_data.items() for premise_id in premise_set if not premise_resolves(premise_id)]
check("AI 目标的前提都能解析（写错的前提会让该目标永远选不中）", not bad_target_premise, first(bad_target_premise))
target_without_premise_data = [cid for cid in game_config.config_target if cid not in game_config.config_target_premise_data]
check("每个 AI 目标都有前提数据", not target_without_premise_data, first(target_without_premise_data))
bad_target_type = [(cid, target.type) for cid, target in game_config.config_target.items() if target.type not in game_config.config_target_type]
check("AI 目标的行动类型都在目标类型表中", not bad_target_type, first(bad_target_type))
indexed_target = {cid for cid_list in game_config.config_target_type_index.values() for cid in cid_list}
bad_type_index = [cid for cid in indexed_target if cid not in game_config.config_target]
check("目标类型索引里的目标都存在", not bad_type_index, first(bad_type_index))
bad_effect_target = [(premise_id, cid) for premise_id, cid_set in game_config.config_effect_target_data.items() for cid in cid_set if cid not in game_config.config_target or not premise_resolves(premise_id)]
check("前提 → 可达成该前提的目标 映射里，前提可解析、目标存在", not bad_effect_target, first(bad_effect_target))
deprecated_in_target = [(cid, premise_id) for cid, premise_set in game_config.config_target_premise_data.items() for premise_id in premise_set if premise_id in deprecated_premise_set]
check("AI 目标不使用已弃用的前提", not deprecated_in_target, first(deprecated_in_target))

section("指令 → 前提")
bad_csv_premise = []
for instruct in game_config.config_instruct.values():
    for premise_name in str(getattr(instruct, "premise_set", "") or "").split("|"):
        premise_name = premise_name.strip()
        if not premise_name:
            continue
        # handle_instruct 只收 constant_promise.Premise 上有的名字，没有的静默丢弃，指令就少了这条前提
        if not hasattr(constant_promise.Premise, premise_name) or getattr(constant_promise.Premise, premise_name) not in PREMISE:
            bad_csv_premise.append((instruct.instruct_id, premise_name))
check("指令表 premise_set 里的前提名都是已注册的 Premise 常量（否则被静默丢弃）", not bad_csv_premise, first(bad_csv_premise))
bad_instruct_premise = [(instruct_id, premise_id) for instruct_id, premise_set in constant.instruct_premise_data.items() for premise_id in premise_set if not premise_resolves(premise_id)]
check("已注册指令的前提集合都能解析", not bad_instruct_premise, first(bad_instruct_premise))
handler_without_config = [instruct_id for instruct_id in constant.handle_instruct_data if instruct_id not in game_config.config_instruct_by_id]
check("每个注册了处理函数的指令在指令表中都有配置", not handler_without_config, first(handler_without_config))
bad_instruct_type = [(instruct.instruct_id, instruct.instruct_type) for instruct in game_config.config_instruct.values() if not hasattr(constant.InstructType, str(instruct.instruct_type))]
check("指令表的指令类型都是 InstructType 里的类型", not bad_instruct_type, first(bad_instruct_type))

section("蚀刻章 → 前置")
# 面板按前置决定显示：前置未达成时不显示本条；game_config.config_achievement_id_relation 记「前置 → 后置」，后置达成后隐藏前置
# 前置写错（不存在 / 指向自己）的那条在达成前永远不显示，指向自己时达成后也会被当作「后置已达成」隐藏掉
ACHIEVEMENT = game_config.config_achievement
bad_pre = [(cid, data.pre_id) for cid, data in ACHIEVEMENT.items() if data.pre_id and (data.pre_id not in ACHIEVEMENT or data.pre_id == cid)]
check("蚀刻章的前置都是另一个存在的蚀刻章（不指向自己）", not bad_pre, first(bad_pre))
shared_pre = collections.Counter(data.pre_id for data in ACHIEVEMENT.values() if data.pre_id)
shared_pre = [(pre_id, [cid for cid, data in ACHIEVEMENT.items() if data.pre_id == pre_id]) for pre_id, count in shared_pre.items() if count > 1]
check("每个蚀刻章至多是一个蚀刻章的前置（关系表一对一，共用时后载入的会覆盖前者）", not shared_pre, first(shared_pre))
cross_type_pre = [(cid, data.pre_id) for cid, data in ACHIEVEMENT.items() if data.pre_id in ACHIEVEMENT and ACHIEVEMENT[data.pre_id].type != data.type]
check("前置与本条是同一类型（同一条升级链）", not cross_type_pre, first(cross_type_pre))
loop_pre = []
for cid in ACHIEVEMENT:
    seen_set, now_id = set(), cid
    while now_id in ACHIEVEMENT and ACHIEVEMENT[now_id].pre_id and now_id not in seen_set:
        seen_set.add(now_id)
        now_id = ACHIEVEMENT[now_id].pre_id
    if now_id in seen_set:
        loop_pre.append(cid)
check("前置链不成环", not loop_pre, first(loop_pre))

finish()
