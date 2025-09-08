"""
前提系统统计补丁 (可选)

目的：稳定记录所有前提函数调用次数与耗时，避免“补丁导入顺序不确定”导致统计为 0。

工作方式：
- 用一个代理字典替换 Script.Core.constant.handle_premise_data，拦截所有注册（setitem）并自动包裹函数；
- 同时对替换当下已经存在于字典中的条目进行一次性包裹；
- 无需改动各 handle_premise_* 模块里本地的 add_premise 定义。

用法（推荐）：
1) 在初始化较早阶段调用 activate_profiler()；
2) 紧接着显式 import Script.Design.handle_premise 以触发所有前提注册；
3) 正常运行游戏循环；
4) 调用 export_premise_profile() 导出统计。
"""

from __future__ import annotations

import time
from typing import Callable, Dict
from Script.Core import constant

premise_profile_stats: Dict[str, Dict] = {}


def _init_premise_stat(pid: str) -> None:
    premise_profile_stats[pid] = {
        "calls": 0,
        "total_time": 0.0,
        "max_time": 0.0,
        "min_time": 999999.0,
        "non_zero": 0,
    }


def _wrap(pid: str, func: Callable) -> Callable:
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

    try:
        wrapped.__name__ = getattr(func, "__name__", "wrapped")
    except Exception:
        pass
    return wrapped


class _PremiseDictProxy(dict):
    """拦截注册的新条目，统一包裹。"""

    def __setitem__(self, key: str, value):
        # 仅对可调用对象包裹
        if callable(value):
            value = _wrap(key, value)
        super().__setitem__(key, value)


def activate_profiler() -> None:
    """启用统计：
    - 替换 constant.handle_premise_data 为代理字典（保留已有关联）；
    - 将已存在的条目全部包裹一次。
    可多次调用，后续调用将保持幂等。
    """
    # 如果已经是代理，则直接返回
    if isinstance(constant.handle_premise_data, _PremiseDictProxy):
        return

    # 1) 复制旧表并包裹
    old = constant.handle_premise_data
    proxy = _PremiseDictProxy()
    for k, v in list(old.items()):
        if callable(v):
            proxy[k] = _wrap(k, v)
        else:
            proxy[k] = v

    # 2) 替换为代理
    constant.handle_premise_data = proxy


def add_premise(premise_id: str):
    """
    兼容用：若某处显式使用了本模块的 add_premise，则仍可工作。
    更推荐方式是使用 activate_profiler() + 代理字典拦截。
    """

    def decorator(func):
        # 确保已激活
        activate_profiler()
        constant.handle_premise_data[premise_id] = func  # 会被代理自动包裹
        return constant.handle_premise_data[premise_id]

    return decorator


def export_premise_profile(path: str) -> None:
    rows = []
    for pid, s in premise_profile_stats.items():
        calls = s["calls"]
        if calls == 0:
            continue
        rows.append(
            {
                "premise_id": pid,
                "calls": calls,
                "non_zero": s["non_zero"],
                "hit_rate": s["non_zero"] / calls if calls else 0.0,
                "total_time": s["total_time"],
                "avg_time": s["total_time"] / calls if calls else 0.0,
                "max_time": s["max_time"],
                "min_time": 0 if s["min_time"] == 999999.0 else s["min_time"],
            }
        )
    rows_sorted = sorted(rows, key=lambda x: x["total_time"], reverse=True)
    import json

    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows_sorted, f, ensure_ascii=False, indent=2)
    print(f"[PremiseProfiler] Exported {len(rows_sorted)} premise stats -> {path}")