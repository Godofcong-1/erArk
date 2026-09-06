#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""教育区 AA 地图生成脚本

为什么需要脚本而不是手写：
    本图的留白全部使用 **U+2002 EN SPACE**，而不是 ASCII 空格。原因见
    `tools/map_aa_check.py` 的模块说明——在 `等距更纱黑体 SC` 下，ASCII 空格与框线字符
    分属两个互不通约的度量族，混用会让竖墙逐字符漂移。U+2002 与框线恒定同宽，
    因此只有全部改用 U+2002 才能保证各字号下都对齐。

    U+2002 在编辑器里和普通空格长得一模一样，手抄/复制粘贴极易被静默替换成 ASCII 空格
    而破坏对齐，所以本图必须由本脚本生成。

本次改建（Plan 22 一期）：
    原教育区只有 1 间「教室」，无法支撑按大学制的多教室并行排课。本次拆为
    6 间理论教室 + 3 间实践教室 + 1 个大礼堂，其余房间保留。

    ⚠️ 房间名用汉字数字（理论教室一~六）而非阿拉伯数字（理论教室1~6）：
       ASCII 数字属 ASCII 度量族（字号 20 下 14px），与框线族（13px）不通约，
       每间教室的按钮都会让所在行漂移 1px，6 间累计 6px。汉字数字恒为 2U，零漂移。

排版模型：
    令 U = 框线字符的宽度。全图按 U 为单位拼装，总宽 105U（< text_width 190，不会软换行）。
    1U 字符：框线 `═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ┄`、`▓ ♂ ♀ ¤`、U+2002 留白
    2U 字符：全部汉字、`○ □ ▣`

    版面：上排 8 格 + 走廊 + 下排 8 格，每格恒为 12U，共 9 堵竖墙。
      上排：理论教室一~六、教师办公室、女洗手间
      下排：实践教室一~三、大礼堂、育儿室、游戏室、活动室、男洗手间
    16 间房全部直通走廊，与 Map.json 的星型 PathEdge 一一对应。

已知的可接受偏差：
    走廊标签行末尾的入口按钮 `0` 是 ASCII 数字（场景目录名，不可改），
    该行没有任何竖墙，不产生可见错位。

用法：
    python tools/map_aa_build_education.py            生成并写入 data/map/教/Map
    python tools/map_aa_build_education.py --dry-run  只打印结果，不写文件

写完后请务必执行：
    python tools/map_aa_check.py 教
    rm -f data/SceneData data/MapData data/PlaceData data/ScenePath
    python init_data.py
"""
import os
import re
import sys
from typing import List

sys.path.append(os.getcwd())

OUT_PATH = os.path.join("data", "map", "教", "Map")
""" 生成目标路径 """

S = " "
""" EN SPACE，宽度恒等于框线字符（1U），用于替代会引起漂移的 ASCII 空格 """

E = "═"
""" 实心横墙 """

D = "┄"
""" 虚线横墙，表示可通行的门 """

CELL = 12
""" 每个房间格的内容宽度（U） """

COLS = 8
""" 每排的房间格数 """

TOTAL = COLS * CELL + COLS + 1
""" 全图总宽（U）：8 格 × 12U + 9 堵竖墙 = 105U """

WIDE_CHARS = set("○□▣") | set("理论教室一二三四五六实践大礼堂育儿办公活动游戏女男洗手间走廊")
""" 占 2U 的字符集合（汉字与全角图形符号） """


def button(scene_name: str) -> str:
    """
    把场景名包装成地图按钮标签
    Keyword arguments:
    scene_name -- 场景目录名，必须与 data/map/教/ 下的子目录同名
    Return arguments:
    str -- 形如 <mapbutton>名字</mapbutton> 的标签文本
    """
    return "<mapbutton>" + scene_name + "</mapbutton>"


def strip_tag(line: str) -> str:
    """
    剥掉 mapbutton 标签，得到玩家实际看到的文本
    Keyword arguments:
    line -- 带标签的行文本
    Return arguments:
    str -- 剥标签后的文本
    """
    return re.sub(r"</?mapbutton>", "", line)


def unit_width(text: str) -> int:
    """
    按 U 为单位计算文本宽度，用于生成期自检
    Keyword arguments:
    text -- 已剥标签的文本
    Return arguments:
    int -- 该文本占的 U 数（2U 字符记 2，其余记 1）
    """
    return sum(2 if ch in WIDE_CHARS else 1 for ch in text)


def center(content: str, width: int = CELL) -> str:
    """
    把一段内容按 U 数居中填充到指定宽度
    Keyword arguments:
    content -- 已剥标签的内容文本（调用方传入带标签的文本时请自行保证宽度）
    width -- 目标宽度（U），默认一个房间格宽
    Return arguments:
    str -- 左右补 U+2002 后的定宽文本
    """
    pad = width - unit_width(strip_tag(content))
    if pad < 0:
        raise ValueError("内容 %s 宽 %dU，超过格宽 %dU" % (content, unit_width(strip_tag(content)), width))
    left = pad // 2
    return S * left + content + S * (pad - left)


def theory_room(name: str) -> List[str]:
    """
    生成一间理论教室的 4 行内容（课桌 ▓ + 讲台 □）
    Keyword arguments:
    name -- 教室的场景目录名
    Return arguments:
    List[str] -- 4 行、每行 12U 的内容文本
    """
    desk = S + "▓▓" + S + "▓▓" + S + "▓▓" + S * 3
    return [
        center("□", CELL),
        desk,
        center(button(name), CELL),
        desk,
    ]


def practice_room(name: str) -> List[str]:
    """
    生成一间实践教室的 4 行内容（操作台 ▣）
    Keyword arguments:
    name -- 教室的场景目录名
    Return arguments:
    List[str] -- 4 行、每行 12U 的内容文本
    """
    bench = S + "▣" + S + "▣" + S + "▣" + S * 3
    return [
        bench,
        bench,
        center(button(name), CELL),
        bench,
    ]


def plain_room(name: str, deco: str = "") -> List[str]:
    """
    生成一间普通房间的 4 行内容
    Keyword arguments:
    name -- 房间的场景目录名
    deco -- 装饰行的内容（已按 12U 居中前的原文），为空则整行留白
    Return arguments:
    List[str] -- 4 行、每行 12U 的内容文本
    """
    deco_line = center(deco, CELL) if deco else S * CELL
    return [
        S * CELL,
        deco_line,
        center(button(name), CELL),
        S * CELL,
    ]


def toilet_room(name: str, mark: str) -> List[str]:
    """
    生成一间洗手间的 4 行内容
    Keyword arguments:
    name -- 洗手间的场景目录名
    mark -- 性别标记字符（♀ / ♂，1U）
    Return arguments:
    List[str] -- 4 行、每行 12U 的内容文本
    """
    return [
        S * CELL,
        S * CELL,
        S + mark + button(name) + S * 2,
        S * CELL,
    ]


def build_lines() -> List[str]:
    """
    按 U 单位拼装教育区地图的 15 行文本
    Keyword arguments:
    无
    Return arguments:
    List[str] -- 带 mapbutton 标签的 15 行地图文本
    """
    # ── 走廊上方 8 格 ────────────────────────────────────
    upper = [
        theory_room("理论教室一"),
        theory_room("理论教室二"),
        theory_room("理论教室三"),
        theory_room("理论教室四"),
        theory_room("理论教室五"),
        theory_room("理论教室六"),
        plain_room("办公室", "▓▓"),
        toilet_room("女洗手间", "♀"),
    ]
    # ── 走廊下方 8 格 ────────────────────────────────────
    lower = [
        practice_room("实践教室一"),
        practice_room("实践教室二"),
        practice_room("实践教室三"),
        plain_room("大礼堂", "○" + S + "○" + S + "○"),
        plain_room("育儿", "▓" + S * 2 + "▓"),
        plain_room("游戏室", "□" + S + "□"),
        plain_room("活动室", "▓" + S + "▓"),
        toilet_room("男洗手间", "♂"),
    ]

    door = E * 4 + D * 4 + E * 4
    """ 一格宽的走廊墙：中间 4U 开门 """

    lines = []
    # 顶边框
    lines.append("╔" + "╦".join([E * CELL] * COLS) + "╗")
    # 上排 4 行
    for k in range(4):
        lines.append("║" + "║".join(room[k] for room in upper) + "║")
    # 走廊上墙（每间上排房间各开一道门）
    lines.append("╠" + "╩".join([door] * COLS) + "╣")
    # 走廊内部三行：左端开口即教育区入口
    lines.append("╚" + S * (TOTAL - 2) + "║")
    lines.append(button("0") + S * 49 + button("走廊") + S * 51)
    lines.append("╔" + S * (TOTAL - 2) + "║")
    # 走廊下墙（每间下排房间各开一道门）
    lines.append("╠" + "╦".join([door] * COLS) + "╣")
    # 下排 4 行
    for k in range(4):
        lines.append("║" + "║".join(room[k] for room in lower) + "║")
    # 底边框
    lines.append("╚" + "╩".join([E * CELL] * COLS) + "╝")
    return lines


def main() -> None:
    """
    命令行入口：生成地图、做 U 单位自检、写入文件
    Keyword arguments:
    无
    Return arguments:
    无（通过 sys.exit 返回退出码）
    """
    dry_run = "--dry-run" in sys.argv[1:]
    lines = build_lines()

    # U 单位自检：除走廊标签行（含 ASCII 的 "0" 按钮、且无竖墙）外，每行都应为 TOTAL
    label_row = 7
    bad = []
    for idx, line in enumerate(lines):
        plain = strip_tag(line)
        width = unit_width(plain)
        if idx != label_row and width != TOTAL:
            bad.append("L%02d = %dU（应为 %dU）" % (idx + 1, width, TOTAL))
        if re.search(r"<(?!/?mapbutton>)[^>]*>", line):
            bad.append("L%02d 含裸尖括号，会被 rich_text.py:233 的正则吞掉" % (idx + 1))
        if " " in plain:
            bad.append("L%02d 含 ASCII 空格，应改用 U+2002" % (idx + 1))

    if bad:
        print("生成自检未通过：")
        for b in bad:
            print("  " + b)
        sys.exit(1)

    text = "\r\n".join(lines)
    if dry_run:
        print(text)
        print("\n自检通过：%d 行，每行 %dU" % (len(lines), TOTAL))
        return

    with open(OUT_PATH, "wb") as f:
        f.write(text.encode("utf-8"))
    print("已写入 %s（%d 行，每行 %dU）" % (OUT_PATH, len(lines), TOTAL))


if __name__ == "__main__":
    main()
