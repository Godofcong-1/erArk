# -*- coding: UTF-8 -*-
"""医疗经营系统日志工具模块

负责记录每日医疗经营结算的摘要信息，便于在 UI 中回溯最近几天的运营数据。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from Script.Core import cache_control, game_type
from Script.System.Medical import medical_constant


def _resolve_base(target_base: Optional[game_type.Rhodes_Island]) -> Optional[game_type.Rhodes_Island]:
    """解析目标基地对象，缺省情况下返回全局缓存中的罗德岛对象"""

    if target_base is not None:
        return target_base
    cache_obj = getattr(cache_control, "cache", None)
    return getattr(cache_obj, "rhodes_island", None)


def _ensure_storage(rhodes_island: game_type.Rhodes_Island) -> List[Dict[str, Any]]:
    """确保基地对象上存在医疗日志存储列表"""

    storage: List[Dict[str, Any]] = getattr(rhodes_island, "medical_recent_reports", []) or []
    if storage is not getattr(rhodes_island, "medical_recent_reports", None):
        rhodes_island.medical_recent_reports = list(storage)
    return rhodes_island.medical_recent_reports


def append_medical_report(
    report: Dict[str, Any],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, Any]:
    """追加一条医疗经营日志记录并返回规范化后的数据"""

    rhodes_island = _resolve_base(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    entry: Dict[str, Any] = dict(report or {})
    game_time = getattr(cache_control.cache, "game_time", None)
    entry.setdefault("time", game_time)

    time_obj = entry.get("time")
    try:
        entry["time_str"] = time_obj.strftime("%Y-%m-%d %H:%M")  # type: ignore[attr-defined]
    except Exception:
        entry["time_str"] = str(time_obj)

    lines = entry.get("lines")
    if isinstance(lines, list):
        entry.setdefault("text", "\n".join(str(line) for line in lines))
    else:
        entry.setdefault("text", str(entry.get("text", "")))

    storage = _ensure_storage(rhodes_island)
    storage.append(entry)
    if len(storage) > medical_constant.MAX_RECENT_REPORTS:
        del storage[0 : len(storage) - medical_constant.MAX_RECENT_REPORTS]

    return entry


def get_recent_medical_reports(
    limit: int = 3,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[Dict[str, Any]]:
    """按时间倒序返回最近的医疗经营日志列表"""

    rhodes_island = _resolve_base(target_base)
    if rhodes_island is None:
        return []

    storage = list(getattr(rhodes_island, "medical_recent_reports", []) or [])
    if not storage:
        return []

    if limit > 0:
        storage = storage[-limit:]
    storage.reverse()
    return storage


__all__ = ["append_medical_report", "get_recent_medical_reports"]
