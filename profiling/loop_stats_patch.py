# -*- coding: UTF-8 -*-
"""
主循环 / NPC AI 结构统计补丁（monkey-patch，不改动产品代码）

用途：
    cProfile 能给出函数级耗时，但无法回答以下结构性问题：
    - 每 tick 主循环对全体 NPC 重扫了多少轮（character_behavior 调用数 / NPC 数）
    - search_target 每次实际检索了多长的 target 列表、多久落一次全量兜底
    - 每 tick 耗时随 NPC 数量的分布（均值 / p95 / 最大值）
    本补丁包裹 update.game_update_flow / character_behavior / find_character_target /
    search_target 四个函数，收集上述计数，供 run_profile.py 以 --loop-stats 启用。

注意：
    - 只做只读统计，不改变任何参数与返回值，不破坏 premise_data / null_target_set
      等削减缓存的复用逻辑。
    - 需在 profile 运行前调用 apply_loop_stats_patch()，结束后 export_loop_stats()。
"""
import json
import time

loop_stats = {
    "ticks": 0,
    "npc_count": 0,
    "tick_times": [],
    "character_behavior_calls_player": 0,
    "character_behavior_calls_npc": 0,
    "character_behavior_time": 0.0,
    "find_target_calls": 0,
    "find_target_time": 0.0,
    "search_target_calls": 0,
    "search_target_time": 0.0,
    "search_target_list_len_sum": 0,
    "search_target_list_len_max": 0,
    "search_target_full_scans": 0,
}
""" 结构统计累计数据 """

_applied = False
""" 防止重复打补丁的标志 """


def apply_loop_stats_patch():
    """
    应用主循环结构统计补丁
    参数：无
    返回值类型：无
    功能描述：包裹 update.game_update_flow / character_behavior.character_behavior /
              handle_npc_ai.find_character_target / handle_npc_ai.search_target，
              收集每 tick 耗时、重扫规模与 target 检索规模；幂等
    """
    global _applied
    if _applied:
        return
    _applied = True

    from Script.Core import cache_control
    from Script.Config import game_config
    from Script.Design import update, character_behavior, handle_npc_ai

    cache = cache_control.cache
    # 全量 target 列表长度，用于判定 search_target 是否落入全量兜底扫描
    full_target_count = len(game_config.config_target)

    # ---- tick 级：每 tick 耗时 + NPC 数 ----
    original_game_update_flow = update.game_update_flow

    def _timed_game_update_flow(add_time):
        # 记录单 tick 墙钟耗时与当前 NPC 规模
        t0 = time.perf_counter()
        result = original_game_update_flow(add_time)
        loop_stats["tick_times"].append(time.perf_counter() - t0)
        loop_stats["ticks"] += 1
        loop_stats["npc_count"] = len(cache.npc_id_got)
        return result

    update.game_update_flow = _timed_game_update_flow

    # ---- 角色级：character_behavior 调用规模（重扫放大系数的分子） ----
    original_character_behavior = character_behavior.character_behavior

    def _counted_character_behavior(character_id, now_time, *args, **kwargs):
        # 玩家与 NPC 分开计数，便于算"每 NPC 每 tick 平均被扫多少轮"
        if character_id == 0:
            loop_stats["character_behavior_calls_player"] += 1
        else:
            loop_stats["character_behavior_calls_npc"] += 1
        t0 = time.perf_counter()
        result = original_character_behavior(character_id, now_time, *args, **kwargs)
        loop_stats["character_behavior_time"] += time.perf_counter() - t0
        return result

    character_behavior.character_behavior = _counted_character_behavior

    # ---- AI 决策级：find_character_target / search_target ----
    original_find_target = handle_npc_ai.find_character_target

    def _timed_find_target(character_id, now_time, *args, **kwargs):
        loop_stats["find_target_calls"] += 1
        t0 = time.perf_counter()
        result = original_find_target(character_id, now_time, *args, **kwargs)
        loop_stats["find_target_time"] += time.perf_counter() - t0
        return result

    handle_npc_ai.find_character_target = _timed_find_target

    original_search_target = handle_npc_ai.search_target

    def _timed_search_target(character_id, target_list, null_target, premise_data, target_weight_data, *args, **kwargs):
        # 记录检索列表规模：list_len 逼近全量即为兜底扫描
        list_len = len(target_list)
        loop_stats["search_target_calls"] += 1
        loop_stats["search_target_list_len_sum"] += list_len
        if list_len > loop_stats["search_target_list_len_max"]:
            loop_stats["search_target_list_len_max"] = list_len
        if list_len >= full_target_count:
            loop_stats["search_target_full_scans"] += 1
        t0 = time.perf_counter()
        result = original_search_target(character_id, target_list, null_target, premise_data, target_weight_data, *args, **kwargs)
        loop_stats["search_target_time"] += time.perf_counter() - t0
        return result

    handle_npc_ai.search_target = _timed_search_target


def export_loop_stats(path: str):
    """
    导出结构统计结果
    参数:
        path (str) -- 输出 JSON 文件路径
    返回值类型：无
    功能描述：汇总每 tick 耗时分布（均值/p50/p95/最大）与重扫、检索规模等派生指标后写盘
    """
    tick_times = sorted(loop_stats["tick_times"])
    ticks = loop_stats["ticks"]
    npc_count = loop_stats["npc_count"]
    npc_calls = loop_stats["character_behavior_calls_npc"]

    def _pct(p: float) -> float:
        # 简易百分位：取排序后对应下标值
        if not tick_times:
            return 0.0
        idx = min(len(tick_times) - 1, int(len(tick_times) * p))
        return tick_times[idx]

    summary = {
        "ticks": ticks,
        "npc_count": npc_count,
        "tick_time_ms": {
            "mean": round(sum(tick_times) / ticks * 1000, 3) if ticks else 0.0,
            "p50": round(_pct(0.50) * 1000, 3),
            "p95": round(_pct(0.95) * 1000, 3),
            "max": round(tick_times[-1] * 1000, 3) if tick_times else 0.0,
        },
        "character_behavior": {
            "calls_player": loop_stats["character_behavior_calls_player"],
            "calls_npc": npc_calls,
            "total_time_s": round(loop_stats["character_behavior_time"], 3),
            # 重扫放大系数：每 NPC 每 tick 平均被扫轮数（1.0 为无重扫的理想值）
            "rescan_factor": round(npc_calls / (ticks * npc_count), 2) if ticks and npc_count else 0.0,
        },
        "find_character_target": {
            "calls": loop_stats["find_target_calls"],
            "total_time_s": round(loop_stats["find_target_time"], 3),
        },
        "search_target": {
            "calls": loop_stats["search_target_calls"],
            "total_time_s": round(loop_stats["search_target_time"], 3),
            "avg_list_len": round(
                loop_stats["search_target_list_len_sum"] / loop_stats["search_target_calls"], 1
            ) if loop_stats["search_target_calls"] else 0.0,
            "max_list_len": loop_stats["search_target_list_len_max"],
            # 全量兜底扫描次数：premise 判定量最大的路径
            "full_scans": loop_stats["search_target_full_scans"],
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
