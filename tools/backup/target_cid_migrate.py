# -*- coding: utf-8 -*-
"""
target.csv 编号体系一次性迁移脚本（Plan 08）

把 data/target/default/target.csv 的 cid 重编为结构化编号：

    新 cid = type * 10000 + 组号 * 100 + 组内序号 * 5

- type：两位，取值同 data/csv/Target_Type.csv，校验规则为 cid // 10000 == type
- 组号：01~99，00 预留给“必须插到该 type 最前面”的紧急情况
- 组内序号：按 5 递增，中间 4 个位置留给插队

「组」的定义 = 同一 type 内、物理行序上连续的同一条行为链。
同一条链若在同一 type 内被拆到不同优先级位置，就会占用多个组——
这是刻意的：优先级顺序高于行为链聚合。

脚本同时会：
1. 把全部数据行按新 cid 升序重排（分区之间用空行分隔，构建器会跳过空行）
2. 同步改写 data/target/default/effect.csv 的 target_id
3. 输出 tools/output/target_cid_mapping.csv 留档
4. 写盘前自检 R1~R5，任何一条不通过就中止

用法：
    .conda/python.exe tools/target_cid_migrate.py
"""
import io
import os
import sys
import collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGET_PATH = os.path.join("data", "target", "default", "target.csv")
EFFECT_PATH = os.path.join("data", "target", "default", "effect.csv")
MAPPING_PATH = os.path.join("tools", "output", "target_cid_mapping.csv")
HEADER_LINES = 5
""" target.csv 前 5 行是表头（字段名/中文说明/类型/gettext标记/类说明） """

CHAIN_BY_OLD_CID = [
    ((0, 20), "待机与跟随"),
    ((21, 32), "睡觉"),
    ((41, 47), "吃饭"),
    ((51, 59), "洗澡"),
    ((61, 63), "休息"),
    ((66, 70), "排泄"),
    ((71, 76), "异常状态直接行动"),
    ((81, 83), "挤奶"),
    ((86, 92), "自慰"),
    ((100, 102), "与玩家随机互动"),
    ((200, 203), "与NPC随机互动"),
    ((321, 324), "工作-图书馆管理员"),
    ((331, 335), "工作-检修工程师"),
    ((341, 346), "工作-住院医生"),
    ((351, 355), "工作-宿舍管理员"),
    ((461, 467), "娱乐-游泳"),
    ((471, 486), "娱乐-大浴场"),
    ((501, 503), "助理-辅佐公务"),
    ((511, 516), "助理-买饭"),
    ((521, 524), "助理-做饭"),
    ((531, 537), "助理-早安问候"),
    ((541, 546), "助理-晚安问候"),
    ((601, 604), "目击H与群交"),
    ((701, 701), "空气催眠待机"),
    ((711, 714), "工作-体检流程"),
    ((801, 806), "工作-性爱练习生"),
    ((901, 908), "助理-博士房间洗澡"),
]
""" 旧 cid 区间 → 行为链名。用于把连续同链的行归进同一个组 """


def chain_of(old_cid):
    """
    查出旧 cid 属于哪条行为链
    Keyword arguments:
    old_cid -- 旧的目标cid
    Return arguments:
    str -- 行为链名，未归类时返回None
    """
    for (low, high), name in CHAIN_BY_OLD_CID:
        if low <= old_cid <= high:
            return name
    return None


def read_target():
    """
    读入 target.csv，拆出表头与数据行
    Return arguments:
    list -- 表头行文本列表
    list -- 数据行字典列表
    """
    raw = io.open(TARGET_PATH, encoding="utf-8", newline="").read()
    lines = raw.split("\r\n")
    header = lines[:HEADER_LINES]
    rows = []
    for index, line in enumerate(lines[HEADER_LINES:], HEADER_LINES + 1):
        if not line.strip():
            continue
        parts = line.split(",", 4)
        if len(parts) < 5:
            raise SystemExit("第 %d 行不是 5 列：%s" % (index, line))
        rows.append({
            "line": index,
            "cid": int(parts[0]),
            "state_machine_id": parts[1],
            "premise_id": parts[2],
            "type": int(parts[3]),
            "remarks": parts[4],
        })
    return header, rows


def build_mapping(rows):
    """
    为每一行算出新 cid，并记录它所在的组
    Keyword arguments:
    rows -- 数据行字典列表（保持物理行序）
    Return arguments:
    dict -- 旧cid到新cid的映射
    dict -- 旧cid到(组号, 行为链名)的映射
    """
    mapping = {}
    group_info = {}
    next_group = collections.Counter()
    last_chain = {}
    bucket = collections.OrderedDict()

    for row in rows:
        chain = chain_of(row["cid"])
        if chain is None:
            raise SystemExit("cid %d 未归入任何行为链，请补 CHAIN_BY_OLD_CID" % row["cid"])
        now_type = row["type"]
        # 同一 type 内，行为链一变就开新组
        if last_chain.get(now_type) != chain:
            next_group[now_type] += 1
            last_chain[now_type] = chain
        group = next_group[now_type]
        if group > 99:
            raise SystemExit("type %d 的组号超过 99" % now_type)
        bucket.setdefault((now_type, group), []).append(row)
        group_info[row["cid"]] = (group, chain)

    for (now_type, group), group_rows in bucket.items():
        if len(group_rows) > 20:
            raise SystemExit("type %d 组 %d 有 %d 行，超过 20 个主位" % (now_type, group, len(group_rows)))
        for order, row in enumerate(group_rows):
            mapping[row["cid"]] = now_type * 10000 + group * 100 + order * 5
    return mapping, group_info


def self_check(rows, mapping):
    """
    写盘前自检 R1~R5，任何一条不通过都直接中止
    Keyword arguments:
    rows -- 原始数据行（物理行序）
    mapping -- 旧cid到新cid的映射
    Return arguments:
    list -- 按新cid升序排好的数据行
    """
    new_values = list(mapping.values())
    # R1 新 cid 唯一
    if len(set(new_values)) != len(new_values):
        raise SystemExit("R1 失败：新 cid 出现重复")
    # R4 cid // 10000 == type
    for row in rows:
        if mapping[row["cid"]] // 10000 != row["type"]:
            raise SystemExit("R4 失败：cid %d 的 type 是 %d" % (mapping[row["cid"]], row["type"]))
    # cid 0 保留给表头占位行
    if 0 in new_values:
        raise SystemExit("R4 失败：新 cid 不能取 0（该值保留给表头占位行）")

    new_rows = sorted(rows, key=lambda r: mapping[r["cid"]])
    # R3 全局新 cid 升序 == 新行序
    if [mapping[r["cid"]] for r in new_rows] != sorted(new_values):
        raise SystemExit("R3 失败：全局 cid 升序与行序不一致")
    # R2 同 type 内新 cid 升序 == 新行序
    per_type = collections.defaultdict(list)
    for row in new_rows:
        per_type[row["type"]].append(mapping[row["cid"]])
    for now_type, values in per_type.items():
        if values != sorted(values):
            raise SystemExit("R2 失败：type %d 内 cid 逆序" % now_type)
    # R5 各 type 内相对优先级顺序与重构前完全一致（行为等价性的核心保证）
    for now_type in per_type:
        old_seq = [r["cid"] for r in rows if r["type"] == now_type]
        new_seq = [r["cid"] for r in new_rows if r["type"] == now_type]
        if old_seq != new_seq:
            raise SystemExit("R5 失败：type %d 的相对顺序被改变\n  旧 %s\n  新 %s" % (now_type, old_seq, new_seq))
    return new_rows


def write_target(header, new_rows, mapping):
    """
    按新 cid 升序、type 分区（空行分隔）写回 target.csv
    Keyword arguments:
    header -- 表头行文本列表
    new_rows -- 按新cid升序排好的数据行
    mapping -- 旧cid到新cid的映射
    Return arguments:
    无
    """
    out = list(header)
    last_type = None
    for row in new_rows:
        # 分区之间插空行；不能写 # 注释行，构建器会把它当数据行写进表里
        if last_type is not None and row["type"] != last_type:
            out.append("")
        last_type = row["type"]
        out.append(",".join([
            str(mapping[row["cid"]]),
            row["state_machine_id"],
            row["premise_id"],
            str(row["type"]),
            row["remarks"],
        ]))
    io.open(TARGET_PATH, "w", encoding="utf-8", newline="").write("\r\n".join(out))


def update_effect(mapping):
    """
    同步改写 effect.csv 的 target_id
    Keyword arguments:
    mapping -- 旧cid到新cid的映射
    Return arguments:
    int -- 改写的行数
    """
    raw = io.open(EFFECT_PATH, encoding="utf-8", newline="").read()
    lines = raw.split("\r\n")
    changed = 0
    for index in range(HEADER_LINES, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        old_target = int(parts[1])
        if old_target not in mapping:
            raise SystemExit("effect.csv 第 %d 行引用了不存在的 target_id %d" % (index + 1, old_target))
        parts[1] = str(mapping[old_target])
        lines[index] = ",".join(parts)
        changed += 1
    io.open(EFFECT_PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))
    return changed


def write_mapping(new_rows, mapping, group_info):
    """
    输出新旧编号对照表留档
    Keyword arguments:
    new_rows -- 按新cid升序排好的数据行
    mapping -- 旧cid到新cid的映射
    group_info -- 旧cid到(组号, 行为链名)的映射
    Return arguments:
    无
    """
    if not os.path.isdir(os.path.dirname(MAPPING_PATH)):
        os.makedirs(os.path.dirname(MAPPING_PATH))
    out = ["old_cid,new_cid,type,group,chain,remark"]
    for row in new_rows:
        group, chain = group_info[row["cid"]]
        out.append("%d,%d,%d,%d,%s,%s" % (
            row["cid"], mapping[row["cid"]], row["type"], group, chain,
            row["remarks"].replace(",", "，")))
    io.open(MAPPING_PATH, "w", encoding="utf-8", newline="").write("\r\n".join(out) + "\r\n")


def main():
    """脚本入口"""
    header, rows = read_target()
    print("读入 %d 行数据" % len(rows))

    mapping, group_info = build_mapping(rows)
    new_rows = self_check(rows, mapping)
    print("自检 R1~R5 全部通过")

    write_target(header, new_rows, mapping)
    effect_changed = update_effect(mapping)
    write_mapping(new_rows, mapping, group_info)

    print("target.csv 已重编号并按 type 分区重排")
    print("effect.csv 改写 %d 行 target_id" % effect_changed)
    print("对照表已写入 %s" % MAPPING_PATH)

    print("\n=== 组分配结果 ===")
    print("%-6s %-5s %-22s %-5s %s" % ("type", "组", "行为链", "行数", "新cid区间"))
    bucket = collections.OrderedDict()
    for row in new_rows:
        bucket.setdefault((row["type"], group_info[row["cid"]][0]), []).append(row)
    for (now_type, group), group_rows in bucket.items():
        chain = group_info[group_rows[0]["cid"]][1]
        print("%-6d %-5d %-22s %-5d %d~%d" % (
            now_type, group, chain, len(group_rows),
            mapping[group_rows[0]["cid"]], mapping[group_rows[-1]["cid"]]))


if __name__ == "__main__":
    main()
