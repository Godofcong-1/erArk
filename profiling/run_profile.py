#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
erArk 专用性能基准 & 函数级 cProfile 采集脚本 (升级版)

本版本修复：
- 初始化顺序导致的 game_config.config_font KeyError
- 缺失玩家与 NPC 行为初始数据导致的 cache.character_data[0] KeyError
- 无存档环境下的全新游戏最小可运行初始化流程

特性：
- 支持：自动尝试读取存档 / 新建最小可运行世界
- 可配置：tick 数、预热、每 tick 推进分钟、是否加载存档
- 若存在 auto 存档或指定存档，可直接载入，以便更真实的 Profile
- 若无存档则走“新建游戏最小初始化”流程（参考 creator_character_flow & game_start 中关键步骤的精简版本）
- 可选加载前提统计补丁 premise_profiler_patch
- 生成：cProfile 原始 .prof + TopN JSON 汇总 + （可选）premise_stats.json

使用示例：
1) 全新（无存档）基准 4 小时（240 tick，每 tick 1 分钟）：
   python -m profiling.run_profile

2) 尝试加载 auto 存档，不存在则新建：
   python -m profiling.run_profile --try-load-auto

3) 指定加载第 3 号存档：
   python -m profiling.run_profile --load-save 3 --ticks 600 --minutes-per-tick 1

4) 与 py-spy 联用（采样火焰图）：
   py-spy record -o flame.svg -- python -m profiling.run_profile --ticks 600

5) 开启前提统计（确保你已放置补丁文件）：
   python -m profiling.run_profile --with-premise-profiler

查看：
   snakeviz profiling_output/<name>.prof
"""

import argparse
import cProfile
import json
import os
import pstats
import sys
import time
from datetime import datetime

PROFILE_DIR = "profiling_output"
os.makedirs(PROFILE_DIR, exist_ok=True)

# ------------------------- 参数解析 -------------------------
def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=240, help="要模拟的逻辑循环次数 (调用 update.game_update_flow 次数)")
    ap.add_argument("--minutes-per-tick", type=int, default=1, help="每次循环推进的游戏分钟数 add_time")
    ap.add_argument("--warmup", type=int, default=0, help="预热 tick (不计入 profile)")
    ap.add_argument("--profile-name", type=str, default="baseline", help="输出文件前缀")
    ap.add_argument("--export-top", type=int, default=20, help="Top N 函数")
    ap.add_argument("--no-patch-io", action="store_true", help="不打性能基准 IO 补丁")
    ap.add_argument("--try-load-auto", action="store_true", help="尝试加载 auto 存档，失败则新建")
    ap.add_argument("--load-save", type=str, default="", help="指定存档 id (数字 或 auto)")
    ap.add_argument("--with-premise-profiler", action="store_true", help="尝试加载前提统计补丁（需已放置 premise_profiler_patch）")
    ap.add_argument("--premise-stats-json", type=str, default="profiling_output/premise_stats.json", help="前提统计输出路径")
    ap.add_argument("--skip-premise-export", action="store_true", help="跳过前提统计导出")
    return ap.parse_args()


# ------------------------- 日志工具 -------------------------
def log(msg):
    print(f"[run_profile] {msg}")


# ------------------------- IO / 等待补丁 -------------------------
def patch_for_benchmark(no_patch_io=False):
    if no_patch_io:
        log("未应用 IO 补丁 (--no-patch-io)")
        return
    log("应用 IO/等待 补丁以减少噪声...")
    try:
        from Script.Core import py_cmd
        py_cmd.focus_cmd = lambda: None
        py_cmd.clr_cmd = lambda: None
    except Exception as e:
        log(f"补丁 py_cmd 失败: {e}")

    try:
        from Script.UI.Moudle import draw
        if hasattr(draw, "WaitDraw"):
            def fast_wait(self):
                return
            draw.WaitDraw.draw = fast_wait
    except Exception as e:
        log(f"补丁 WaitDraw.draw 失败: {e}")

    # 你可根据需要继续补丁其它 UI / 输入函数
    log("IO 补丁完成.")


# ------------------------- 存档加载 -------------------------
def try_load_save(save_id: str) -> bool:
    """
    尝试加载存档:
        save_id = 'auto' 或 '数字'
    成功返回 True
    """
    try:
        from Script.Core import cache_control, constant
        from Script.Core import save_handle
        cache = cache_control.cache

        if save_id == "auto":
            exist = save_handle.judge_save_file_exist("auto")
            if not exist:
                log("auto 存档不存在")
                return False
            save_handle.input_load_save("auto")
            cache.now_panel_id = constant.Panel.IN_SCENE
            log("已加载 auto 存档")
            return True
        else:
            exist = save_handle.judge_save_file_exist(save_id)
            if not exist:
                log(f"存档 {save_id} 不存在")
                return False
            save_handle.input_load_save(save_id)
            cache.now_panel_id = constant.Panel.IN_SCENE
            log(f"已加载存档 {save_id}")
            return True
    except Exception as e:
        log(f"加载存档异常: {e}")
        return False


# ------------------------- 新建游戏最小初始化 -------------------------
def new_game_minimal_init():
    """
    参考 creator_character_flow.creator_character_panel / game_start 的关键步骤，
    但剔除用户交互与 UI 绘制，仅构造可供 AI 行为循环使用的最小数据环境。
    """
    log("执行新建游戏最小初始化...")
    from Script.Core import cache_control, game_type, constant
    from Script.Design import (
        character_handle,
        character,
        attr_calculation,
        basement,
        game_time,
    )
    from Script.Design import cooking
    from Script.Config import game_config
    from Script.Core import io_init

    cache = cache_control.cache

    # 1. 创建玩家角色
    cache.character_data[0] = game_type.Character()
    # 初始化玩家基础属性
    character_handle.init_character_list()  # 载入 NPC 模板 / 基础角色结构
    character.init_attr(0)

    # 2. 基础基地与设定
    cache.rhodes_island = basement.get_base_zero()

    # 初始奖励 / 世界设定 (等同 first_bonus_and_setting_updata 的核心)
    for cid in game_config.config_first_bonus:
        cache.first_bonus[cid] = False
    for cid in game_config.config_world_setting:
        cache.world_setting[cid] = 0
    cache.all_system_setting = attr_calculation.get_system_setting_zero()
    cache.rhodes_island.materials_resouce[1] = 20000
    cache.rhodes_island.materials_resouce[11] = 20
    cache.rhodes_island.physical_examination_setting = attr_calculation.get_physical_exam_setting_zero()

    # 3. 自动选择所有“初始基础 NPC” (基础集合)
    # constant.first_NPC_name_set 存基础干员名字。quick 选择策略：所有模板里符合的
    from Script.Core import constant as core_constant
    base_names = core_constant.first_NPC_name_set
    # cache.npc_tem_data 在不同场景可能是 dict 或 list，兼容两者
    npc_tem_data = cache.npc_tem_data
    if isinstance(npc_tem_data, dict):
        iterator = npc_tem_data.items()
    else:
        # 假定为 list 或其他可迭代序列，使用 enumerate 提供 cid
        iterator = enumerate(npc_tem_data)

    for cid, npc_tem in iterator:
        # npc_tem 是模板；正式实例化后会进入 character_data?
        # character_handle.init_character_list() 已创建模板，下面实例化/加入?
        # 简化：如果模板名字在基础集合里，就确保加入 npc_id_got
        try:
            name = getattr(npc_tem, "name", None)
        except Exception:
            name = None
        if name in base_names:
            cache.npc_id_got.add(cid)

    # 确保玩家自身加入集合
    cache.npc_id_got.add(0)

    # 4. 初始化 NPC 工作 / 宿舍 / 位置 / 设施 / 娱乐 等
    # 在正式逻辑中 first_NPC_work 依赖已选择 NPC
    try:
        character_handle.first_NPC_work()
    except Exception as e:
        log(f"first_NPC_work 过程中忽略异常: {e}")

    character_handle.init_character_dormitory()
    character_handle.init_character_position()
    character_handle.init_character_facility_open()
    character_handle.handle_character_setting()
    character_handle.init_character_entertainment()

    # 5. 烹饪 / 食品店 / 其他系统
    try:
        cooking.init_recipes()
        cooking.init_food_shop_data(new_day_flag=True)
    except Exception as e:
        log(f"cooking 初始化忽略异常: {e}")

    # 6. 游戏时间
    game_time.init_time()

    # 7. 初始化字体 / 颜色风格 (避免 rich_text / main_frame 缺依赖)
    try:
        io_init.init_style()
    except Exception as e:
        log(f"io_init.init_style 忽略异常: {e}")

    # 8. 初始行为（玩家与 NPC）:
    from Script.Core import constant as cst
    for cid in cache.npc_id_got:
        ch = cache.character_data.get(cid)
        if not ch:
            continue
        # 保留 start_time 默认 sentinel，行为循环会自动补
        ch.behavior.behavior_id = cst.Behavior.SHARE_BLANKLY
        ch.behavior.duration = 5  # 给个最小持续时间，避免 0
        # start_time 留为 (1,1,1) 由 instuct_judege.init_character_behavior_start_time 修正

    log("新建游戏最小初始化完成.")


# ------------------------- 游戏核心初始化（顺序修复） -------------------------
def init_game_environment(args):
    """
    修复顺序：
    1. 先初始化 normal_config / cache
    2. 再 game_config.init() （字体等需要先装）
    3. 再 import 任何会间接触发 UI / main_frame 的模块 (map_config 等)
    4. 载入其他配置 (character 模板、地图等)
    5. 根据参数尝试加载存档 -> 否则新建
    """
    log("开始初始化环境...")
    from Script.Core import game_type, cache_control
    from Script.Config import normal_config

    # Cache & 基础 config
    cache_control.cache = game_type.Cache()
    normal_config.init_normal_config()

    # 重要：先加载 game_config 再 import 依赖 UI 的东西
    from Script.Core import get_text
    from Script.Config import game_config, name_config
    game_config.init()

    # 尝试加载前提统计补丁（需在其余模块大量导入之前，以便覆盖装饰器）
    premise_mod = None
    if args.with_premise_profiler:
        premise_mod = load_premise_profiler(args)
        # 关键：提前激活代理并在其后导入 handle_premise 以触发注册
        try:
            if premise_mod:
                activate = getattr(premise_mod, "activate_profiler", None)
                if callable(activate):
                    activate()
                    # 强制导入以触发所有装饰器注册到代理字典
                    import importlib
                    importlib.import_module("Script.Design.handle_premise")
                    log("前提统计代理已激活并完成注册拦截。")
        except Exception as e:
            log(f"激活前提统计代理失败: {e}")

    # 此时才能安全 import 其它会追溯到 main_frame / 字体的模块
    from Script.Config import character_config
    character_config.init_character_tem_data()

    # 地图 (map_config 会 import rich_text -> draw -> io_init -> main_frame)
    from Script.Config import map_config
    map_config.init_map_data()

    from Script.Design import start_flow, character_handle, game_time
    import Script.Settle
    import Script.StateMachine
    from Script.Core import flow_handle, game_init, io_init
    import Script.UI.Flow

    # 尝试存档逻辑
    loaded = False
    if args.load_save:
        save_id = args.load_save
        loaded = try_load_save(save_id)
    elif args.try_load_auto:
        loaded = try_load_save("auto")

    if not loaded:
        new_game_minimal_init()
    else:
        log("已加载存档，跳过新建流程。")

    # 标记基准模式
    from Script.Core import cache_control as cc2
    setattr(cc2.cache, "benchmark_mode", True)

    log("环境初始化完成.")
    return premise_mod


# ------------------------- 前提统计补丁检测 -------------------------
def load_premise_profiler(args):
    # argparse 会把 --with-premise-profiler 转为 with_premise_profiler
    if not getattr(args, "with_premise_profiler", False):
        return None
    try:
        # 需要你已将补丁文件放到 Script/Design/handle_premise/premise_profiler_patch.py
        import Script.Design.handle_premise.premise_profiler_patch as pmod
        if hasattr(pmod, "premise_profile_stats"):
            log("已加载前提统计补丁.")
            return pmod
        else:
            log("已加载补丁模块，但未发现 premise_profile_stats 属性.")
    except Exception as e:
        log(f"加载前提统计补丁失败: {e}")
    return None


# ------------------------- Tick 驱动 -------------------------
def run_ticks(ticks: int, minutes_per_tick: int):
    from Script.Design import update
    for i in range(ticks):
        print(f"[run_profile] Tick {i+1}/{ticks} (+{minutes_per_tick}min)")
        update.game_update_flow(minutes_per_tick)


# ------------------------- Profile 执行 -------------------------
def profile_run(ticks, minutes_per_tick, warmup, profile_name, top_n):
    if warmup > 0:
        log(f"预热 {warmup} ticks...")
        run_ticks(warmup, minutes_per_tick)

    pr = cProfile.Profile()
    log(f"开始 Profile: ticks={ticks}, step={minutes_per_tick}min")
    wall_start = time.perf_counter()
    pr.enable()
    run_ticks(ticks, minutes_per_tick)
    pr.disable()
    wall_dur = time.perf_counter() - wall_start
    log(f"Profile 结束，墙钟时间 {wall_dur:.3f}s")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    prof_path = os.path.join(PROFILE_DIR, f"{profile_name}_{ts}.prof")
    pr.dump_stats(prof_path)

    stats = pstats.Stats(pr)
    func_stats = []
    for func, stat in getattr(stats, "stats", {}).items():
        cc, nc, tt, ct, callers = stat  # primitive, total, tottime, cumtime
        filename, line, funcname = func
        func_stats.append({
            "func": f"{filename}:{line}:{funcname}",
            "primitive_calls": cc,
            "total_calls": nc,
            "tottime": tt,
            "cumtime": ct,
            "avg_tottime": tt / nc if nc else 0.0,
            "avg_cumtime": ct / nc if nc else 0.0
        })

    top_cum = sorted(func_stats, key=lambda x: x["cumtime"], reverse=True)[:top_n]
    top_tot = sorted(func_stats, key=lambda x: x["tottime"], reverse=True)[:top_n]

    summary = {
        "profile_file": prof_path,
        "ticks": ticks,
        "minutes_per_tick": minutes_per_tick,
        "warmup": warmup,
        "wall_time": wall_dur,
        f"top{top_n}_by_cumtime": top_cum,
        f"top{top_n}_by_tottime": top_tot
    }
    summary_path = os.path.join(PROFILE_DIR, f"{profile_name}_{ts}_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    log(f"cProfile 原始: {prof_path}")
    log(f"汇总 JSON:  {summary_path}")
    return prof_path, summary_path


# ------------------------- 前提统计导出 -------------------------
def export_premise_stats(pmod, path):
    if not pmod:
        return
    try:
        if hasattr(pmod, "export_premise_profile"):
            pmod.export_premise_profile(path)
        else:
            stats = getattr(pmod, "premise_profile_stats", {})
            rows = []
            for pid, s in stats.items():
                calls = s["calls"]
                if calls == 0:
                    continue
                rows.append({
                    "premise_id": pid,
                    "calls": calls,
                    "non_zero": s["non_zero"],
                    "hit_rate": s["non_zero"] / calls if calls else 0.0,
                    "total_time": s["total_time"],
                    "avg_time": s["total_time"] / calls if calls else 0.0,
                    "max_time": s["max_time"],
                    "min_time": 0 if s["min_time"] == 999999.0 else s["min_time"],
                })
            rows.sort(key=lambda x: x["total_time"], reverse=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
        log(f"前提统计已导出 -> {path}")
    except Exception as e:
        log(f"导出前提统计失败: {e}")


# ------------------------- 主入口 -------------------------
def main():
    args = parse_args()

    premise_mod = init_game_environment(args)
    patch_for_benchmark(no_patch_io=args.no_patch_io)

    profile_run(
        ticks=args.ticks,
        minutes_per_tick=args.minutes_per_tick,
        warmup=args.warmup,
        profile_name=args.profile_name,
        top_n=args.export_top
    )

    if premise_mod and not args.skip_premise_export:
        export_premise_stats(premise_mod, args.premise_stats_json)

    log("全部完成。可使用 snakeviz / py-spy / scalene 进行进一步分析。")

    # 退出
    sys.exit(0)


if __name__ == "__main__":
    main()