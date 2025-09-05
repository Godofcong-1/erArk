"""
前提系统统计补丁 (可选)

使用方法：
1. 将本文件放入 Script/Design/handle_premise/ 目录
2. 确保在前提函数真正注册(add_premise 装饰器被使用)之前被 import
   最简单：在 run_profile.py 的 init 逻辑之前加：
       import Script.Design.handle_premise.premise_profiler_patch  # noqa: F401
3. 正常运行 profiling/run_profile.py
4. 结束后会看到 profiling_output/premise_stats.json

如果你的原 add_premise 定义位置不同，请调整 import constant.handle_premise_data 的路径。
"""

import time
from Script.Core import constant  # 假设 constant.handle_premise_data 为注册字典

premise_profile_stats = {}  # premise_id -> dict

def _init_premise_stat(pid):
    premise_profile_stats[pid] = {
        "calls": 0,
        "total_time": 0.0,
        "max_time": 0.0,
        "min_time": 999999.0,
        "non_zero": 0,
    }

def _wrap(pid, func):
    if pid not in premise_profile_stats:
        _init_premise_stat(pid)
    stat = premise_profile_stats[pid]

    def wrapped(character_id: int):
        start = time.perf_counter()
        result = func(character_id)
        dur = time.perf_counter() - start
        stat["calls"] += 1
        stat["total_time"] += dur
        if dur > stat["max_time"]:
            stat["max_time"] = dur
        if dur < stat["min_time"]:
            stat["min_time"] = dur
        if result:
            stat["non_zero"] += 1
        return result
    wrapped.__name__ = func.__name__
    return wrapped

def add_premise(premise_id: str):
    """
    替换/覆盖原装饰器。
    假设 constant.handle_premise_data 是一个 dict，保存 premise_id -> callable
    如果你的项目用的不是这个名字，请自行修改。
    """
    def decorator(func):
        wrapped = _wrap(premise_id, func)
        constant.handle_premise_data[premise_id] = wrapped
        return wrapped
    return decorator

def export_premise_profile(path: str):
    rows = []
    for pid, s in premise_profile_stats.items():
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
    rows_sorted = sorted(rows, key=lambda x: x["total_time"], reverse=True)
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows_sorted, f, ensure_ascii=False, indent=2)
    print(f"[PremiseProfiler] Exported {len(rows_sorted)} premise stats -> {path}")