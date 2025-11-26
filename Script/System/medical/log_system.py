# -*- coding: UTF-8 -*-
"""医疗经营系统日志工具模块

负责记录每日医疗经营结算的摘要信息，便于在 UI 中回溯最近几天的运营数据。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from Script.Core import cache_control, game_type
from Script.System.Medical import medical_constant, medical_core

def _ensure_storage(rhodes_island: game_type.Rhodes_Island) -> List[Dict[str, Any]]:
    """确保基地对象上存在医疗日志存储列表。

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地对象。
    返回:
        List[Dict[str, Any]]: 可写的日志存储列表引用。
    """

    # 优先读取现有列表，若缺失或类型异常则重建空列表。
    storage: Optional[List[Dict[str, Any]]] = getattr(rhodes_island, "medical_recent_reports", None)
    if not isinstance(storage, list):
        storage = []
        rhodes_island.medical_recent_reports = storage
    return storage


def append_medical_report(
    report: Dict[str, Any],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, Any]:
    """追加一条医疗经营日志记录并返回规范化后的数据。

    参数:
        report (Dict[str, Any]): 待写入的日志内容，允许包含 time、lines 等字段。
        target_base (Optional[game_type.Rhodes_Island]): 指定写入的基地，缺省时自动解析。
    返回:
        Dict[str, Any]: 归一化后的日志条目，附带时间字符串。
    """

    # --- 解析日志写入目标的基地对象 ---
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    # --- 复制一份日志字典并补全时间戳/文本字段 ---
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

    # --- 获取日志存储容器，在容量超限时截断旧记录 ---
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
    """按时间倒序返回最近的医疗经营日志列表。

    参数:
        limit (int): 返回的日志数量上限，<=0 表示返回全部。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地，缺省读取全局缓存。
    返回:
        List[Dict[str, Any]]: 倒序排列的日志列表，最新记录在最前。
    """

    # --- 若找不到基地对象，则返回空列表 ---
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return []

    # --- 复制日志列表，避免修改原始数据 ---
    storage = list(getattr(rhodes_island, "medical_recent_reports", []) or [])
    if not storage:
        return []

    # --- 根据 limit 截取最新若干条目，并倒序返回 ---
    if limit > 0:
        storage = storage[-limit:]
    storage.reverse()
    return storage


__all__ = ["append_medical_report", "get_recent_medical_reports"]
