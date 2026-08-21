#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""训练场 AA 地图生成脚本

为什么需要脚本而不是手写：
    本图的留白全部使用 **U+2002 EN SPACE**，而不是 ASCII 空格。原因见
    `tools/map_aa_check.py` 的模块说明——在 `等距更纱黑体 SC` 下，ASCII 空格与框线字符
    分属两个互不通约的度量族，混用会让竖墙逐字符漂移。U+2002 与框线恒定同宽，
    因此只有全部改用 U+2002 才能保证各字号下都对齐。

    U+2002 在编辑器里和普通空格长得一模一样，手抄/复制粘贴极易被静默替换成 ASCII 空格
    而破坏对齐，所以本图必须由本脚本生成。

排版模型：
    令 U = 框线字符的宽度。全图按 U 为单位拼装，总宽 89U。
    1U 字符：框线 `═ ║ │ ┃ ┄ ┅ ┆ ┇ ─`、`▓ ♂ ♀ ¤`、U+2002 留白、`∼`
    2U 字符：全部汉字、`○ ● □ ▣ ♲ －`

已知的可接受偏差：
    1. 靶道里的 `➷` `➹` 属 ASCII 度量族（当前字号下 28px，而 2U = 26px），
       每个箭头让所在行右端多出 2px。它们位于全图最右侧的靶道格内，
       左侧所有竖墙（0/27/46/55）不受影响，只有最右端的 `┃` 相对边框偏移 2px。
    2. 走廊标签行末尾的入口按钮 `0` 是 ASCII 数字（场景目录名，不可改），
       该行没有任何竖墙，不产生可见错位。

用法：
    python tools/map_aa_build_training.py            生成并写入 data/map/训练/Map
    python tools/map_aa_build_training.py --dry-run  只打印结果，不写文件

写完后请务必执行：
    python tools/map_aa_check.py 训练 --tol 2
    rm -f data/SceneData data/MapData data/PlaceData data/ScenePath
    python init_data.py
"""
import os
import re
import sys
from typing import List

sys.path.append(os.getcwd())

OUT_PATH = os.path.join("data", "map", "训练", "Map")
""" 生成目标路径 """

S = " "
""" EN SPACE，宽度恒等于框线字符（1U），用于替代会引起漂移的 ASCII 空格 """

E = "═"
""" 实心横墙 """

WAVE = "∼"
""" ∼ 水面，1U（替代宽度不稳定的 ASCII `~`） """

DASH = "─"
""" ─ 饮水机出水口，1U（替代宽度不稳定的 ASCII `-`） """

WIDE_CHARS = set("○●□▣♲－◎") | set("木桩房射击健身区走廊模拟对战室休息更衣淋浴游泳池男士女洗手间") | set("➷➹")
""" 占 2 格的字符集合。其中 ➷➹ 属 ASCII 度量族、实际是 2 个 ASCII 空格宽而非 2U，
    这里按 2 格计入只是为了让版面算术自洽；真正的偏差由 tools/map_aa_check.py 按像素量出 """


def button(scene_name: str) -> str:
    """
    把场景名包装成地图按钮标签
    Keyword arguments:
    scene_name -- 场景目录名，必须与 data/map/训练/ 下的子目录同名
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


def build_lines() -> List[str]:
    """
    按 U 单位拼装训练场地图的 14 行文本
    Keyword arguments:
    无
    Return arguments:
    List[str] -- 带 mapbutton 标签的 14 行地图文本
    """
    # ── 走廊上方各房间（3 行）──────────────────────────────
    gym_up = [  # 健身区上半，26U
        S * 2 + "●－●" + S * 2 + "●－●" + S * 2 + "●－●" + S * 2,
        S * 26,
        S * 2 + "●－●" + S * 2 + "●－●" + S * 2 + "●－●" + S * 2,
    ]
    wood = [  # 木桩房，18U
        S * 2 + S.join(["○"] * 5) + S * 2,
        S * 6 + button("木桩房") + S * 6,
        S * 2 + S.join(["○"] * 5) + S * 2,
    ]
    shoot = [  # 射击房，8U
        S + "¤" + S + "¤" + S + "¤" + S * 2,
        S + button("射击房") + S,
        S + "¤" + S + "¤" + S + "¤" + S * 2,
    ]
    rng = [  # 靶道，32U（➷➹ 各让所在行多出 2px，属可接受偏差）
        S * 8 + "➷" + S * 20 + "◎",
        S * 30 + "◎",
        S * 14 + "➹" + S * 14 + "◎",
    ]

    # ── 走廊下方各房间（6 行）──────────────────────────────
    gym_dn = [  # 健身区下半，26U
        S * 3 + "▓" + S * 2 + "▓" + S * 2 + "▓" + S * 2 + "▓" + S * 4 + "▣－▣" + S * 3,
        S * 17 + "▣－▣" + S * 3,
        S * 3 + "▓" + S * 2 + "▓" + S * 2 + "▓" + S * 2 + "▓" + S * 4 + "▣－▣" + S * 3,
        S * 17 + "▣－▣" + S * 3,
    ]
    arena = [  # 模拟对战室，18U
        S + "○" + "┅" * 12 + "○" + S,
        S + "┇" + S * 14 + "┇" + S,
        S + "┇" + S * 2 + button("模拟对战室") + S * 2 + "┇" + S,
        S + "┇" + S * 14 + "┇" + S,
        S + "┇" + S * 14 + "┇" + S,
        S + "○" + "┅" * 12 + "○" + S,
    ]
    rest = [  # 休息室（本次新增），12U
        S + "▓¤" + S * 6 + "¤▓" + S,
        S * 12,
        S * 3 + button("休息室") + S * 3,
        S * 12,
        S + "▓¤" + S * 6 + "¤▓" + S,
        S + "□" + DASH + S * 5 + "♲" + S,
    ]
    lock = [  # 更衣室，8U
        S * 8,
        S + button("更衣室") + S,
        "□" + S + "□" + S + "□",
        S * 8,
        "□" + S + "□" + S + "□",
        S * 8,
    ]
    show = [  # 淋浴，6U
        S * 6,
        S + button("淋浴") + S,
        "¤" + S * 4 + "¤",
        "¤" + S * 4 + "¤",
        "¤" + S * 4 + "¤",
        S * 6,
    ]
    pool = [  # 游泳池，12U
        S + WAVE * 10 + S,
        S + WAVE * 10 + S,
        S + WAVE * 2 + button("游泳池") + WAVE * 2 + S,
        S + WAVE * 10 + S,
        S + WAVE * 10 + S,
        S + WAVE * 10 + S,
    ]

    lines = []
    # 顶边框
    lines.append("╔" + E * 26 + "╦" + E * 18 + "╦" + E * 8 + "╦" + E * 32 + "╗")
    # 走廊上方三行
    for k in range(3):
        lines.append("║" + gym_up[k] + "║" + wood[k] + "║" + shoot[k] + "│" + rng[k] + "┃")
    # 走廊上墙（木桩房与射击房各开一道门）
    lines.append("╚" + S * 26 + "╚" + E * 6 + "┄" * 6 + E * 6 + "╩" + E * 2 + "┄" * 4 + E * 2 + "╩" + E * 32 + "╣")
    # 走廊标签行（健身区在左，走廊居中，入口 0 在最右）
    lines.append(S * 11 + button("健身区") + S * 29 + button("走廊") + S * 38 + button("0"))
    # 走廊下墙（模拟对战室、休息室、更衣室各开一道门；淋浴与游泳池不直通走廊）
    lines.append("╔" + S * 26 + "╔" + E * 6 + "┄" * 6 + E * 6 + "╦" + E * 4 + "┄" * 4 + E * 4 + "╦" + E * 2 + "┄" * 4 + E * 2 + "╦" + E * 6 + "╦" + E * 12 + "╣")
    # 走廊下方六行
    sep_locker_shower = ["║", "┆", "┆", "║", "║", "║"]  # 更衣室↔淋浴 的门开在第 9、10 行
    sep_shower_pool = ["║", "║", "║", "┆", "┆", "║"]  # 淋浴↔游泳池 的门开在第 11、12 行
    for k in range(6):
        if k < 4:
            left = "║" + gym_dn[k] + "║"
        elif k == 4:
            # 男女洗手间的上墙，中间 4U 留出与健身区相连的通道
            left = "╠" + E * 10 + "╗" + S * 4 + "╔" + E * 10 + "╣"
        else:
            # ♂♀ 本身充当洗手间的门，占据竖墙位
            left = "║" + button("男士洗手间") + "♂" + S * 4 + "♀" + button("女士洗手间") + "║"
        lines.append(left + arena[k] + "║" + rest[k] + "║" + lock[k] + sep_locker_shower[k] + show[k] + sep_shower_pool[k] + pool[k] + "║")
    # 底边框
    lines.append("╚" + E * 10 + "╩" + E * 4 + "╩" + E * 10 + "╩" + E * 18 + "╩" + E * 12 + "╩" + E * 8 + "╩" + E * 6 + "╩" + E * 12 + "╝")
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

    # U 单位自检：除走廊标签行（末尾是 ASCII 的 "0" 按钮）外，每行都应为 89U
    bad = []
    for idx, line in enumerate(lines):
        plain = strip_tag(line)
        width = unit_width(plain)
        if idx == 5:
            continue
        if width != 89:
            bad.append("L%02d = %dU（应为 89U）" % (idx + 1, width))
        if re.search(r"<(?!/?mapbutton>)[^>]*>", line):
            bad.append("L%02d 含裸尖括号，会被 rich_text.py:233 的正则吞掉" % (idx + 1))
        if " " in plain:
            bad.append("L%02d 含 ASCII 空格，应改用 U+2002" % (idx + 1))

    if bad:
        print("生成自检未通过：")
        for b in bad:
            print("  " + b)
        sys.exit(1)

    print("U 单位自检通过：13 个竖墙行均为 89U，无 ASCII 空格，无裸尖括号")
    print()
    for line in lines:
        print(strip_tag(line))
    print()

    if dry_run:
        print("--dry-run，未写入文件")
        return

    # 与其余地图保持一致：UTF-8 无 BOM、CRLF、末尾不加换行
    data = "\r\n".join(lines).encode("utf-8")
    open(OUT_PATH, "wb").write(data)
    print("已写入 %s：%d 字节，%d 行" % (OUT_PATH, len(data), len(lines)))
    print("请接着执行： python tools/map_aa_check.py 训练 --tol 2")


if __name__ == "__main__":
    main()
