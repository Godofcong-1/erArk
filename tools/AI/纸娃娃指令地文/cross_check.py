# -*- coding: UTF-8 -*-
"""跨指令雷同检查：同组同段里，不同指令的两句去掉占位符后相似度 >= 0.75 即算雷同（只读，不改文件）

用法（仓库根目录）:
    .conda/python.exe tools/AI/纸娃娃指令地文/cross_check.py <行为id>        只查这个指令的句子与其他指令的雷同（去重子代理用）
    .conda/python.exe tools/AI/纸娃娃指令地文/cross_check.py --plan <输出.json>  全部指令两两比较，按「每对只改一句」分好工写成 JSON（主代理用）

同池抽取的只有同一指令内的文本；跨指令雷同不影响游戏逻辑，但玩家换着用相近的指令（同体位换插入部位等）时会读到几乎一样的句子
先用字二元组的 Jaccard 粗筛，再用与 gen_paperdoll 相同的 difflib 比较精算
"""
import difflib
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv
sys.argv = [_argv[0], ".", "--check"]
import gen_paperdoll as g  # noqa: E402

sys.argv = _argv

LIMIT = g.SIMILARITY_LIMIT
# 粗筛门槛：二元组 Jaccard 低于它的句对 difflib 相似度不可能到 0.75 附近（实测留有余量）
JACCARD_LIMIT = 0.45
# 范例与用户已认可的成品，不参与改写分工
PROTECTED = {g.REFERENCE_BEHAVIOR}


def all_behaviors() -> list:
    """列出已有文本源的全部指令"""
    return sorted(n[:-4] for n in os.listdir(g.SRC_DIR) if n.endswith(".txt") and not n.endswith("_无意识.txt"))


def load_lines(behavior: str) -> dict:
    """读入某指令的全部句子：{(组, 段): [(原句, 正文, 二元组集合)]}"""
    result = {}
    for file_name in (f"{behavior}.txt", f"{behavior}_无意识.txt"):
        path = os.path.join(g.SRC_DIR, file_name)
        if not os.path.exists(path):
            continue
        for key, texts in g.parse_text_file(path).items():
            lines = []
            for text in texts:
                body = g.strip_placeholders(text)
                lines.append((text, body, {body[i : i + 2] for i in range(len(body) - 1)}))
            result[key] = lines
    return result


def similar(body_a: str, grams_a: set, body_b: str, grams_b: set, matcher: difflib.SequenceMatcher) -> float:
    """两句的相似度；粗筛不过时返回 0（matcher 的 seq2 须已设为 body_a）"""
    union = len(grams_a | grams_b)
    if not union or len(grams_a & grams_b) / union < JACCARD_LIMIT:
        return 0.0
    matcher.set_seq1(body_b)
    if matcher.quick_ratio() < LIMIT:
        return 0.0
    return matcher.ratio()


def scan(targets: list, data: dict) -> list:
    """比较 targets 中每个指令与其他全部指令；返回 [(相似度, (组, 段), 指令a, 原句a, 指令b, 原句b)]，每对只出现一次"""
    hits = []
    behaviors = sorted(data)
    target_set = set(targets)
    for a in targets:
        for key, lines_a in data[a].items():
            for text_a, body_a, grams_a in lines_a:
                matcher = difflib.SequenceMatcher(autojunk=False)
                matcher.set_seq2(body_a)
                for b in behaviors:
                    # 两边都在 targets 里时只按字典序算一次
                    if b == a or (b in target_set and b < a):
                        continue
                    for text_b, body_b, grams_b in data[b].get(key, []):
                        ratio = similar(body_a, grams_a, body_b, grams_b, matcher)
                        if ratio >= LIMIT:
                            hits.append((round(ratio, 3), key, a, text_a, b, text_b))
    hits.sort(key=lambda h: -h[0])
    return hits


def make_plan(hits: list) -> list:
    """每对只改一句：按相似度从高到低贪心覆盖，改涉及雷同更多的那个指令（打散重灾区），范例不改"""
    load = defaultdict(int)
    for _r, _key, a, _ta, b, _tb in hits:
        load[a] += 1
        load[b] += 1
    marked = set()
    partners = defaultdict(list)
    for r, key, a, ta, b, tb in hits:
        partners[(a, key, ta)].append({"behavior": b, "line": tb, "ratio": r})
        partners[(b, key, tb)].append({"behavior": a, "line": ta, "ratio": r})
    for r, key, a, ta, b, tb in hits:
        if (a, key, ta) in marked or (b, key, tb) in marked:
            continue
        if a in PROTECTED:
            side = (b, key, tb)
        elif b in PROTECTED:
            side = (a, key, ta)
        else:
            side = (a, key, ta) if (load[a], a) >= (load[b], b) else (b, key, tb)
        marked.add(side)
    tasks = defaultdict(list)
    for behavior, key, text in sorted(marked, key=lambda m: (m[0], str(m[1][0]), m[1][1], m[2])):
        tasks[behavior].append({"group": str(key[0]), "segment": key[1], "line": text, "others": partners[(behavior, key, text)]})
    return [{"behavior": b, "items": items} for b, items in sorted(tasks.items())]


if __name__ == "__main__":
    data = {b: load_lines(b) for b in all_behaviors()}
    if len(sys.argv) >= 3 and sys.argv[1] == "--plan":
        hits = scan(sorted(data), data)
        plan = make_plan(hits)
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=1)
        print(f"雷同句对 {len(hits)}；需改写 {sum(len(t['items']) for t in plan)} 句，分到 {len(plan)} 个指令")
        sys.exit(0)
    behavior = sys.argv[1]
    hits = scan([behavior], data)
    for r, key, a, ta, b, tb in hits:
        print(f"{r}\t{key[0]} {key[1]}\t{ta}\n\t\t与 {b}：{tb}")
    print(f"雷同 {len(hits)} 处")
    sys.exit(1 if hits else 0)
