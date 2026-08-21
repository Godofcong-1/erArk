# -*- coding: utf-8 -*-
"""
target.csv 编号规范校验（Plan 08 的常驻检查）

把编号约定固化为可执行的检查，改完 target.csv 后跑一遍即可。

校验规则：
    R1  cid 全表唯一
    R2  同一 type 内，cid 升序 == 物理行序（决定 AI 优先级，最关键）
    R3  全局 cid 升序 == 物理行序（可读性）
    R4  cid // 10000 == type
    R5  premise_id 中每个前提名都能在 constant.handle_premise_data 中解析
    R6  state_machine_id 存在于 constant.handle_state_machine_data
    R7  effect.csv 的每个 target_id 都存在于 target.csv
    R8  数据区每个非空行都是 5 列，且 cid/type/state_machine_id 可转 int

R5/R6 需要载入游戏配置，比较慢；加 --fast 可跳过这两条只做纯文本检查。

用法：
    .conda/python.exe tools/lint_target_csv.py
    .conda/python.exe tools/lint_target_csv.py --fast
"""
import io
import os
import sys
import collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
# 脚本位于 tools/ 下，需要把仓库根目录加进模块搜索路径才能 import Script
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

TARGET_PATH = os.path.join("data", "target", "default", "target.csv")
EFFECT_PATH = os.path.join("data", "target", "default", "effect.csv")
HEADER_LINES = 5
""" target.csv 前 5 行是表头 """

problems = collections.OrderedDict()
""" 规则名 → 问题描述列表 """


def report(rule, message):
    """
    记录一条违规
    Keyword arguments:
    rule -- 规则名
    message -- 问题描述
    Return arguments:
    无
    """
    problems.setdefault(rule, []).append(message)


def load_rows():
    """
    读入 target.csv 的数据行，顺便做 R8 检查
    Return arguments:
    list -- 数据行字典列表（保持物理行序）
    """
    rows = []
    raw = io.open(TARGET_PATH, encoding="utf-8", newline="").read()
    for index, line in enumerate(raw.split("\r\n"), 1):
        if index <= HEADER_LINES or not line.strip():
            continue
        parts = line.split(",", 4)
        # R8 列数与类型
        if len(parts) < 5:
            report("R8 数据区存在非法行", "第 %d 行只有 %d 列：%s" % (index, len(parts), line[:40]))
            continue
        try:
            cid, state_machine_id, now_type = int(parts[0]), int(parts[1]), int(parts[3])
        except ValueError:
            report("R8 数据区存在非法行", "第 %d 行的 cid/状态机/type 无法转为整数：%s" % (index, line[:40]))
            continue
        rows.append({
            "line": index,
            "cid": cid,
            "state_machine_id": state_machine_id,
            "premise_id": parts[2],
            "type": now_type,
        })
    return rows


def check_numbering(rows):
    """
    R1~R4：编号唯一性、顺序与结构
    Keyword arguments:
    rows -- 数据行字典列表
    Return arguments:
    无
    """
    # R1 唯一
    seen = {}
    for row in rows:
        if row["cid"] in seen:
            report("R1 cid重复", "cid %d 同时出现在第 %d 行和第 %d 行" % (row["cid"], seen[row["cid"]], row["line"]))
        seen[row["cid"]] = row["line"]

    # R2 同 type 内升序
    per_type = collections.defaultdict(list)
    for row in rows:
        per_type[row["type"]].append(row)
    for now_type, type_rows in sorted(per_type.items()):
        for before, after in zip(type_rows, type_rows[1:]):
            if after["cid"] < before["cid"]:
                report("R2 同type内cid逆序（会导致AI优先级错乱）",
                       "type%d：第%d行(cid %d) 之后是 第%d行(cid %d)"
                       % (now_type, before["line"], before["cid"], after["line"], after["cid"]))

    # R3 全局升序
    for before, after in zip(rows, rows[1:]):
        if after["cid"] < before["cid"]:
            report("R3 全局cid逆序",
                   "第%d行(cid %d) 之后是 第%d行(cid %d)"
                   % (before["line"], before["cid"], after["line"], after["cid"]))

    # R4 cid 编码 type
    for row in rows:
        if row["cid"] // 10000 != row["type"]:
            report("R4 cid未按 type*10000+组*100+序号*5 编码",
                   "第%d行 cid %d 的 type 是 %d" % (row["line"], row["cid"], row["type"]))


def check_effect(rows):
    """
    R7：effect.csv 的 target_id 不能悬空
    Keyword arguments:
    rows -- target.csv 的数据行
    Return arguments:
    无
    """
    if not os.path.isfile(EFFECT_PATH):
        return
    known = {row["cid"] for row in rows}
    raw = io.open(EFFECT_PATH, encoding="utf-8", newline="").read()
    for index, line in enumerate(raw.split("\r\n"), 1):
        if index <= HEADER_LINES or not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        try:
            target_id = int(parts[1])
        except ValueError:
            report("R7 effect.csv引用异常", "第 %d 行的 target_id 无法转为整数" % index)
            continue
        if target_id not in known:
            report("R7 effect.csv引用了不存在的target", "第 %d 行引用 target_id %d" % (index, target_id))


def check_registry(rows):
    """
    R5/R6：前提名与状态机必须能在运行时解析（需要载入游戏配置，较慢）
    Keyword arguments:
    rows -- 数据行字典列表
    Return arguments:
    无
    """
    from Script.Core import game_type, cache_control
    from Script.Config import normal_config
    cache_control.cache = game_type.Cache()
    normal_config.init_normal_config()
    from Script.Config import game_config
    game_config.init()
    from Script.Core import constant
    import Script.Design.handle_premise  # noqa 触发前提注册
    import Script.StateMachine.default  # noqa 触发状态机注册

    for row in rows:
        for premise in row["premise_id"].split("|"):
            # "0" 是占位值，表示无前提
            if not premise or premise == "0":
                continue
            if premise not in constant.handle_premise_data:
                report("R5 前提名无法解析（该行永远不会被选中）",
                       "第%d行 cid %d 的前提 %s" % (row["line"], row["cid"], premise))
        if row["state_machine_id"] not in constant.handle_state_machine_data:
            report("R6 状态机不存在（选中后会崩溃）",
                   "第%d行 cid %d 的状态机 %d" % (row["line"], row["cid"], row["state_machine_id"]))


def main():
    """脚本入口"""
    fast = "--fast" in sys.argv
    rows = load_rows()
    print("读入 %d 行数据" % len(rows))

    check_numbering(rows)
    check_effect(rows)
    if fast:
        print("（--fast 模式，跳过 R5/R6 的注册表检查）")
    else:
        check_registry(rows)

    if not problems:
        print("\n全部规则通过")
        return 0

    print("")
    for rule, messages in problems.items():
        print("【%s】%d 处" % (rule, len(messages)))
        for message in messages[:10]:
            print("   " + message)
        if len(messages) > 10:
            print("   ...（其余 %d 处省略）" % (len(messages) - 10))
        print("")
    return 1


if __name__ == "__main__":
    sys.exit(main())
