# -*- coding: UTF-8 -*-
"""医疗经营系统日志工具模块

负责记录每日医疗经营结算的摘要信息，便于在 UI 中回溯最近几天的运营数据。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Mapping
from types import FunctionType

from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.UI.Moudle import draw
from Script.System.Medical import medical_constant, medical_core

_: FunctionType = get_text._
""" 翻译函数 """

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


def _normalize_stage_counters(raw_stats: Dict[str, Any]) -> Dict[str, Any]:
    """将日志中的统计字段统一归一化。

    参数:
        raw_stats (Dict[str, Any]): 原始统计字段映射。
    返回:
        Dict[str, Any]: 采用最新字段名称的统计字典。
    """

    # --- 使用结构体解析并返回规范化后的字段集合 ---
    counters = medical_constant.MedicalDailyCounters.from_mapping(raw_stats)
    return counters.as_dict()


def _normalize_consumption_map(value: object) -> Dict[int, float]:
    """将药品消耗字段转换为以资源 ID 为键的浮点映射。

    参数:
        value (object): 原始药品消耗字段，可能为字典、列表或数字。
    返回:
        Dict[int, float]: 转换后的资源 ID 到消耗量映射。
    """

    # --- 使用核心结构体的规范化逻辑获取完整的药品映射 ---
    coerced = medical_constant.MedicalDailyCounters._coerce_consumption_mapping(value)
    normalized: Dict[int, float] = {}
    for resource_id, amount in coerced.items():
        try:
            normalized[int(resource_id)] = float(amount or 0.0)
        except (TypeError, ValueError):
            continue
    return normalized


def _format_medicine_consumption_details(
    consumption_map: Mapping[int, float],
    inventory_detail: Optional[Mapping[int, Mapping[str, object]]] = None,
) -> List[str]:
    """根据药品消耗与库存缺口生成可读的明细文本。

    参数:
        consumption_map (Mapping[int, float]): 资源 ID 到消耗量的映射。
        inventory_detail (Optional[Mapping[int, Mapping[str, object]]]):
            记录消耗、缺口、剩余量的补充数据。
    返回:
        List[str]: 格式化后的文本行列表。
    """

    # --- 解析补充细节映射，便于后续统一读取字段 ---
    detail_map: Dict[int, Dict[str, float]] = {}
    if isinstance(inventory_detail, Mapping):
        for res_id, info in inventory_detail.items():
            try:
                safe_id = int(res_id)
            except (TypeError, ValueError):
                continue
            if not isinstance(info, Mapping):
                continue
            consumed = medical_constant.MedicalDailyCounters._coerce_float(info.get("consumed", 0))
            shortage = medical_constant.MedicalDailyCounters._coerce_float(info.get("shortage", 0))
            remain = medical_constant.MedicalDailyCounters._coerce_float(info.get("remain", 0))
            detail_map[safe_id] = {
                "consumed": consumed,
                "shortage": shortage,
                "remain": remain,
            }

    # --- 合并全部资源 ID，包含消耗列表与补充明细 ---
    resource_ids: set[int] = set()
    for key in consumption_map.keys():
        try:
            resource_ids.add(int(key))
        except (TypeError, ValueError):
            continue
    resource_ids.update(detail_map.keys())

    detail_lines: List[str] = []
    for resource_id in sorted(resource_ids):
        consumed_units = float(consumption_map.get(resource_id, 0.0) or 0.0)
        detail_entry = detail_map.get(resource_id)
        if detail_entry:
            consumed_units = detail_entry.get("consumed", consumed_units)
            shortage_units = detail_entry.get("shortage", 0)
            remain_units = detail_entry.get("remain", 0)
        else:
            shortage_units = 0.0
            remain_units = 0.0

        # --- 过滤掉完全无数据的资源，减少无意义输出 ---
        if (
            abs(consumed_units) <= medical_constant.FLOAT_EPSILON
            and abs(shortage_units) <= medical_constant.FLOAT_EPSILON
            and abs(remain_units) <= medical_constant.FLOAT_EPSILON
        ):
            continue

        resource_config = game_config.config_resouce.get(resource_id)
        resource_name = getattr(resource_config, "name", str(resource_id)) if resource_config else str(resource_id)
        line = _("   {name}：消耗 {consumed:.2f} 单位").format(name=resource_name, consumed=consumed_units)
        if shortage_units > 0:
            line += _("，缺口 {shortage:.2f} 单位").format(shortage=shortage_units)
        line += _("，库存 {remain:.2f} 单位").format(remain=remain_units)
        detail_lines.append(line)

    return detail_lines


def _format_medical_report_entry(entry: Dict[str, Any], day_past_flag: bool = False) -> str:
    """将单条医疗经营日志格式化为可展示的文本块。

    参数:
        entry (Dict[str, Any]): 单条日志内容字典。
        day_past_flag (bool): 判断是否为每日结算日志。
    返回:
        str: 经过格式化后的多行文本。
    """

    # --- 复制统计数据并执行字段归一化，保证数据完整 ---
    stats = dict(entry.get("stats", {}) or {})
    stage_stats = _normalize_stage_counters(stats)
    stats.update(stage_stats)

    # --- 解析队列快照与关键统计指标 ---
    queue = dict(entry.get("queue", {}) or {})
    price_ratio = float(entry.get("price_ratio", 1.0) or 1.0)
    income = int(entry.get("income", 0) or 0)
    surgeries_performed = int(stats.get("surgeries_performed", 0) or 0)
    blocked = int(queue.get("surgery_blocked", 0) or 0)
    medicine_consumption_map = _normalize_consumption_map(stage_stats.get("medicine_consumed", {}))
    medicine_consumed_total = sum(float(amount) for amount in medicine_consumption_map.values())
    hospitalized_today = int(stats.get("hospitalized_today", 0) or 0)
    discharged_today = int(stats.get("discharged_today", 0) or 0)

    # --- 读取队列状态 ---
    waiting_queue = int(queue.get("waiting", 0) or 0)
    waiting_medication = int(queue.get("waiting_medication", 0) or 0)
    hospitalized = int(queue.get("hospitalized", 0) or 0)
    need_surgery = int(queue.get("need_surgery", 0) or 0)
    medicine_granted = int(queue.get("medicine_granted", 0) or 0)

    # --- 拆分诊疗与用药阶段的数据 ---
    diagnose_outpatient = stage_stats.get("diagnose_completed_outpatient", 0)
    diagnose_hospital = stage_stats.get("diagnose_completed_hospital", 0)
    diagnose_total = diagnose_outpatient + diagnose_hospital
    medicine_outpatient = stage_stats.get("medicine_completed_outpatient", 0)
    medicine_hospital = stage_stats.get("medicine_completed_hospital", 0)
    medicine_total = medicine_outpatient + medicine_hospital
    pending_outpatient = stage_stats.get("outpatient_waiting_medicine", 0)
    pending_hospital = stage_stats.get("hospital_waiting_medicine", 0)

    # --- 组装文本段落，保持与结算界面一致的语句风格 ---
    title = str(entry.get("title", "")).strip()
    lines: List[str] = []
    if title:
        lines.append(title)
    if not day_past_flag:
        lines.append(_(" - 记录时间：{0}").format(entry.get("time_str", "-")))
        lines.append(_(" - 收费系数：{0:.0f}%").format(price_ratio * 100))
    lines.append(_(" - 收入：{0} 龙门币").format(income))
    lines.append(
        _(" - 诊疗完成：{0} 人（门诊 {1} / 住院 {2}）").format(
            diagnose_total,
            diagnose_outpatient,
            diagnose_hospital,
        )
    )
    lines.append(
        _(" - 用药完成：{0} 人（门诊 {1} / 住院 {2}）").format(
            medicine_total,
            medicine_outpatient,
            medicine_hospital,
        )
    )
    if pending_outpatient or pending_hospital:
        lines.append(_(" - 待发药：门诊 {0} 人 / 住院 {1} 人").format(pending_outpatient, pending_hospital))
    lines.append(_(" - 药品库存：今日消耗 {0:.2f} 单位").format(medicine_consumed_total))
    inventory_detail = entry.get("inventory_detail") or entry.get("inventory")
    medicine_detail_lines = _format_medicine_consumption_details(medicine_consumption_map, inventory_detail)
    if medicine_detail_lines:
        lines.extend(medicine_detail_lines)
    lines.append(_(" - 今日入院：{0} 人 / 出院：{1} 人").format(hospitalized_today, discharged_today))
    if surgeries_performed or blocked:
        lines.append(_(" - 手术执行：成功 {0} 例 / 待条件 {1} 例").format(surgeries_performed, blocked))
    lines.append(
        _(" - 队列概况：待诊 {0} 人 / 待发药 {1} 人 / 已拿药 {2} 人 / 住院 {3} 人 / 待手术 {4} 人").format(
            waiting_queue,
            waiting_medication,
            medicine_granted,
            hospitalized,
            need_surgery,
        )
    )

    # --- 附加自定义文本，保持日志信息完整 ---
    extra_text = str(entry.get("text", "")).strip()
    if extra_text:
        lines.append(extra_text)

    return "\n".join(lines)


def render_medical_reports(
    reports: List[Dict[str, Any]],
    *,
    width: int,
    draw_flag: bool = True,
    day_past_flag: bool = False,
    empty_message: Optional[str] = None,
) -> str:
    """统一渲染医疗经营日志列表，可复用在结算与面板。

    参数:
        reports (List[Dict[str, Any]]): 需要渲染的日志条目列表。
        width (int): 输出文本的宽度设置。
        draw_flag (bool): 为 True 时立即绘制到界面，否则仅返回文本。
        day_past_flag (bool): 判断是否为每日结算日志。
        empty_message (Optional[str]): 日志为空时的提示文本。
    返回:
        str: 最终渲染的文本内容。
    """

    # --- 若无日志则输出提示信息，避免空白弹窗 ---
    if not reports:
        fallback = empty_message or _("\n暂无医疗经营日志记录。\n")
        text = fallback if fallback.endswith("\n") else fallback + "\n"
        if draw_flag:
            wait_draw = draw.WaitDraw()
            wait_draw.width = width
            wait_draw.text = text
            wait_draw.draw()
        return text

    # --- 逐条格式化日志并使用分隔线拼接，保持展示一致 ---
    sections = [_format_medical_report_entry(entry, day_past_flag = day_past_flag) for entry in reports]
    text = "\n" + "\n--------------------\n".join(sections) + "\n"

    if draw_flag:
        wait_draw = draw.WaitDraw()
        wait_draw.width = width
        wait_draw.text = text
        wait_draw.draw()

    return text


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
    from Script.Design import game_time
    entry: Dict[str, Any] = dict(report or {})
    entry.setdefault("time", cache_control.cache.game_time)

    time_obj = entry.get("time")
    try:
        entry["time_str"] = game_time.get_date_until_day()[3:]
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


__all__ = ["append_medical_report", "get_recent_medical_reports", "render_medical_reports"]
