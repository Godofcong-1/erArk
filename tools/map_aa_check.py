#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""AA 地图逐像素对齐校验工具

背景说明：
    `data/map/*/Map` 里的 AA 地图，最终排版由**字体的实际字宽**决定，而不是由
    `wcwidth.wcswidth` 决定。原因是 `Script/UI/Panel/see_map_panel.py:97-109`
    只用全局 `max_width` 算出一个**所有行共用**的空格前缀，之后把每一段文本原样输出，
    所以行内对齐完全取决于每个字符在字体里的实际推进宽度。

    在 `等距更纱黑体 SC` 下，字符分成两个互不通约的度量族：
      - 框线族：`═ ║ │ ┃ ┄ ┅ ▓ ♂ ♀ ¤` 等，宽度记为 1U；汉字与 `○ ● □ ▣` 等为 2U
      - ASCII 族：ASCII 空格、`~`、`-`、数字、`➷ ➹ ☸` 等
    两族在部分字号下宽度相同（18/22/24/26/30），在另一些字号下不同（14/16/20/40）。
    当前 `config.ini` 反算出的字号正好是 20，所以混用两族的地图会逐字符累积漂移。

    因此校验必须按像素做，不能数列数。

用法：
    python tools/map_aa_check.py                 校验全部地图
    python tools/map_aa_check.py 训练            只校验训练场
    python tools/map_aa_check.py 训练 --tol 2    允许 2 像素容差
    python tools/map_aa_check.py --list-bad      只列出有错位的地图，按严重程度排序

退出码：0 表示全部在容差内，1 表示存在超出容差的错位。
"""
import os
import re
import sys
import tkinter
import tkinter.font
from typing import Dict, List, Tuple

# 允许从仓库根目录直接运行
sys.path.append(os.getcwd())

from Script.Config import normal_config

MAP_ROOT = os.path.join("data", "map")
""" 地图数据根目录 """

WALL_CHARS = set("║╔╗╚╝╠╣╦╩│┆┃♂♀")
""" 参与对齐校验的竖向墙体/门字符（♂♀ 在洗手间里充当门，占据墙位） """

CHECK_SIZES = [12, 14, 16, 18, 20, 22, 24, 26, 30, 40]
""" 校验用的字号列表，覆盖不同 window_width / text_width 组合能反算出的常见字号 """


def get_current_font_size() -> int:
    """
    按 Script/Core/main_frame.py:248 的算法反算当前实际使用的字号
    Keyword arguments:
    无
    Return arguments:
    int -- 当前字号
    """
    cfg = normal_config.config_normal
    return int(cfg.window_width / cfg.text_width) * 2


def load_map_lines(map_name: str) -> List[str]:
    """
    读取指定地图的 AA 文本并剥掉 mapbutton 标签
    Keyword arguments:
    map_name -- 地图目录名，如 "训练"
    Return arguments:
    List[str] -- 剥标签并去掉行尾空白后的各行文本（与游戏内解析结果一致）
    """
    path = os.path.join(MAP_ROOT, map_name, "Map")
    raw = open(path, "r", encoding="utf-8").read()
    # 游戏侧 map_config.py:243 会对每行做 rstrip，这里保持一致
    return [re.sub(r"</?mapbutton>", "", line).rstrip() for line in raw.split("\n")]


def measure_line(font: tkinter.font.Font, line: str) -> Tuple[int, Tuple[int, ...]]:
    """
    计算一行文本的总像素宽度与其中各竖墙的像素位置
    Keyword arguments:
    font -- 已创建的 Tk 字体对象
    line -- 单行文本（已剥标签）
    Return arguments:
    Tuple[int, Tuple[int, ...]] -- (该行总像素宽, 各竖墙的起始像素位置元组)
    """
    x = 0
    positions = []
    for char in line:
        if char in WALL_CHARS:
            positions.append(x)
        x += font.measure(char)
    return x, tuple(positions)


def check_map(map_name: str, fonts: Dict[int, tkinter.font.Font], tolerance: int, verbose: bool) -> Tuple[int, List[str]]:
    """
    校验单张地图在各字号下的像素对齐情况
    Keyword arguments:
    map_name -- 地图目录名
    fonts -- 字号到 Tk 字体对象的映射
    tolerance -- 允许的像素容差
    verbose -- 是否打印每个字号的明细
    Return arguments:
    Tuple[int, List[str]] -- (最大错位像素数, 问题描述列表)
    """
    lines = [l for l in load_map_lines(map_name) if l]
    if not lines:
        return 0, ["地图为空"]

    worst = 0
    problems = []
    for size in sorted(fonts):
        font = fonts[size]
        widths = []
        # 按"这一行有几堵墙"分组，只有结构相同的行才有可比性
        by_wall_count: Dict[int, List[Tuple[int, Tuple[int, ...]]]] = {}
        for idx, line in enumerate(lines):
            width, positions = measure_line(font, line)
            # 完全没有竖墙的行（纯标签行、纯装饰行）不参与对齐校验
            if not positions:
                continue
            widths.append(width)
            by_wall_count.setdefault(len(positions), []).append((idx, positions))

        if not widths:
            continue

        width_gap = max(widths) - min(widths)
        worst = max(worst, width_gap)
        if width_gap > tolerance:
            problems.append("字号%d：竖墙行总宽相差 %dpx（%d~%d）" % (size, width_gap, min(widths), max(widths)))

        # 同结构行的每一堵墙都应落在同一像素位置
        for wall_count, group in sorted(by_wall_count.items()):
            for col in range(wall_count):
                xs = [positions[col] for _, positions in group]
                gap = max(xs) - min(xs)
                worst = max(worst, gap)
                if gap > tolerance:
                    rows = ", ".join("L%02d" % (idx + 1) for idx, _ in group)
                    problems.append("字号%d：%d 堵墙的行（%s）第 %d 堵墙位置相差 %dpx" % (size, wall_count, rows, col + 1, gap))

        if verbose:
            print("    字号 %2d：竖墙行总宽 %s px" % (size, sorted(set(widths))))

    return worst, problems


def main() -> None:
    """
    命令行入口：解析参数并逐张校验地图
    Keyword arguments:
    无
    Return arguments:
    无（通过 sys.exit 返回退出码）
    """
    args = sys.argv[1:]
    tolerance = 0
    list_bad = False
    targets = []
    i = 0
    while i < len(args):
        if args[i] == "--tol":
            tolerance = int(args[i + 1])
            i += 2
        elif args[i] == "--list-bad":
            list_bad = True
            i += 1
        else:
            targets.append(args[i])
            i += 1

    normal_config.init_normal_config()
    cfg = normal_config.config_normal
    cur_size = get_current_font_size()

    root = tkinter.Tk()
    root.withdraw()
    fonts = {size: tkinter.font.Font(family=cfg.font, size=size) for size in CHECK_SIZES}

    unit = fonts[cur_size].measure("═")
    ascii_unit = fonts[cur_size].measure(" ")
    print("字体=%s  当前字号=%d（由 window_width=%d / text_width=%d 反算）" % (cfg.font, cur_size, cfg.window_width, cfg.text_width))
    print("当前字号下：框线 1U=%dpx，ASCII 空格=%dpx %s" % (unit, ascii_unit, "（两族同宽，混用不会漂移）" if unit == ascii_unit else "（两族不同宽，混用会逐字符漂移）"))
    print("容差=%dpx，校验字号=%s" % (tolerance, CHECK_SIZES))
    print()

    if not targets:
        targets = sorted(d for d in os.listdir(MAP_ROOT) if os.path.isfile(os.path.join(MAP_ROOT, d, "Map")))

    results = []
    failed = 0
    for name in targets:
        worst, problems = check_map(name, fonts, tolerance, verbose=not list_bad and len(targets) == 1)
        results.append((worst, name, problems))
        if problems:
            failed += 1

    if list_bad:
        print("%-10s %10s  %s" % ("地图", "最大错位", "状态"))
        for worst, name, problems in sorted(results, reverse=True):
            print("%-10s %8dpx  %s" % (name, worst, "超出容差" if problems else "通过"))
    else:
        for worst, name, problems in results:
            if problems:
                print("[FAIL] %s  最大错位 %dpx" % (name, worst))
                for p in problems[:6]:
                    print("         %s" % p)
                if len(problems) > 6:
                    print("         ...另有 %d 条" % (len(problems) - 6))
            else:
                print("[OK]   %s  最大错位 %dpx" % (name, worst))

    print()
    print("结果：%d / %d 张地图在 %dpx 容差内通过" % (len(results) - failed, len(results), tolerance))
    root.destroy()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
