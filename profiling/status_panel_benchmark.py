#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""状态面板绘制性能基准脚本"""

import argparse
import json
import os
import sys
from time import perf_counter
from types import SimpleNamespace


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="对 SeeCharacterStatusPanel 初始化耗时进行采样")
    parser.add_argument("--iterations", type=int, default=500, help="测量循环次数")
    parser.add_argument("--warmup", type=int, default=50, help="预热循环次数，避免首次导入抖动")
    parser.add_argument("--character-id", type=int, default=-1, help="目标角色 id，不传则优先使用名称或默认玩家")
    parser.add_argument("--character-name", type=str, default="", help="按角色名称匹配，优先级高于 id")
    parser.add_argument("--panel-width", type=int, default=0, help="状态面板宽度，0 表示使用 normal_config 默认值")
    parser.add_argument("--column", type=int, default=7, help="每行状态栏个数")
    parser.add_argument("--type-number", type=int, default=0, help="状态类型过滤参数，对应面板初始化入参")
    parser.add_argument(
        "--center-status",
        type=int,
        choices=(0, 1),
        default=1,
        help="是否居中绘制状态文本，1 为是 0 为否",
    )
    parser.add_argument("--draw-output", action="store_true", help="执行实际 draw()，可能产生大量输出")
    parser.add_argument("--export-json", type=str, default="", help="可选：保存测量结果 JSON 的路径")
    parser.add_argument("--no-patch-io", action="store_true", help="跳过 IO 补丁，保留真实绘制输出")
    parser.add_argument("--try-load-auto", action="store_true", help="尝试在初始化时加载 auto 存档")
    parser.add_argument("--load-save", type=str, default="", help="指定存档 id 进行加载")
    return parser.parse_args()


def log(message: str) -> None:
    """标准化日志输出"""
    print(f"[status_bench] {message}")


def ensure_environment(args: argparse.Namespace) -> None:
    """初始化游戏环境，使面板实例化所需数据齐备"""
    from profiling.run_profile import init_game_environment, patch_for_benchmark

    env_args = SimpleNamespace(
        with_premise_profiler=False,
        load_save=args.load_save,
        try_load_auto=args.try_load_auto,
    )
    patch_for_benchmark(args.no_patch_io)
    init_game_environment(env_args)


def resolve_character_id(cache, character_id: int, character_name: str) -> int:
    """根据参数确定目标角色 id"""
    if character_name:
        for cid, char_data in cache.character_data.items():
            if getattr(char_data, "name", "") == character_name:
                return cid
        raise SystemExit(f"未找到名称为 {character_name} 的角色")
    if character_id >= 0:
        if character_id in cache.character_data:
            return character_id
        raise SystemExit(f"未找到 id 为 {character_id} 的角色")
    return 0


def consume_draw(label) -> None:
    """递归执行 draw() 以模拟真实渲染"""
    if isinstance(label, (list, tuple)):
        for item in label:
            consume_draw(item)
        return
    draw_method = getattr(label, "draw", None)
    if callable(draw_method):
        draw_method()


def run_iterations(factory, iterations: int, draw_output: bool) -> None:
    """执行预热循环"""
    for _ in range(iterations):
        panel = factory()
        if draw_output:
            consume_draw(panel.draw_list)


def measure_iterations(factory, iterations: int, draw_output: bool) -> float:
    """测量循环耗时"""
    start = perf_counter()
    for _ in range(iterations):
        panel = factory()
        if draw_output:
            consume_draw(panel.draw_list)
    return perf_counter() - start


def export_result(path: str, payload: dict) -> None:
    """写出 JSON 结果"""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    log(f"结果已写入 {path}")


def main() -> None:
    """脚本入口"""
    args = parse_args()
    ensure_environment(args)

    from Script.Config import normal_config
    from Script.Core import cache_control
    from Script.UI.Panel import see_character_info_panel

    cache = cache_control.cache
    if args.panel_width <= 0:
        args.panel_width = normal_config.config_normal.text_width
    center_status = bool(args.center_status)

    character_id = resolve_character_id(cache, args.character_id, args.character_name)
    character_data = cache.character_data[character_id]
    character_name = getattr(character_data, "name", str(character_id))

    log(f"目标角色: id={character_id} name={character_name}")
    log(f"参数: iterations={args.iterations} warmup={args.warmup} width={args.panel_width} column={args.column}")

    factory = lambda: see_character_info_panel.SeeCharacterStatusPanel(
        character_id,
        args.panel_width,
        args.column,
        args.type_number,
        center_status,
    )

    if args.warmup > 0:
        log("开始预热...")
        run_iterations(factory, args.warmup, args.draw_output)

    log("开始正式测量...")
    total_duration = measure_iterations(factory, args.iterations, args.draw_output)
    per_iteration_ms = total_duration / max(args.iterations, 1) * 1000

    log(f"总耗时: {total_duration:.6f}s")
    log(f"单次耗时: {per_iteration_ms:.3f}ms")

    result = {
        "character_id": character_id,
        "character_name": character_name,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "panel_width": args.panel_width,
        "column": args.column,
        "type_number": args.type_number,
        "center_status": center_status,
        "draw_output": args.draw_output,
        "total_duration_sec": total_duration,
        "per_iteration_ms": per_iteration_ms,
    }

    if args.export_json:
        export_result(args.export_json, result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("用户中断.")
        sys.exit(1)
