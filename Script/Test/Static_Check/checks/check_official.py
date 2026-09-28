# -*- coding: UTF-8 -*-
"""静态检查系统 - 公务队列与事件履历。不要求历史uid仍在配置表中。"""

from datetime import datetime
from typing import List

from Script.Core import cache_control
from ..check_registry import CheckFailure, register_check, make_failure


@register_check("OFFICIAL-01", "队列条目")
def check_official_01() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 检查队列及字段类型；角色引用失效单独警示。部门id由写入方保存为int。"""
    cache = cache_control.cache
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return []
    queue = getattr(ri, "official_event_queue", None)
    if not isinstance(queue, list):
        return [make_failure("OFFICIAL-01", "队列条目", f"cid=None key=official_event_queue value={queue!r}；须为list", [])]
    characters = getattr(cache, "character_data", None)
    failures = []
    for index, item in enumerate(queue):
        prefix = f"official_event_queue[{index}]"
        if not isinstance(item, dict):
            failures.append(make_failure("OFFICIAL-01", "队列条目", f"cid=None key={prefix} value={item!r}；须为dict", []))
            continue
        cid = item.get("chara_id")
        ids = [cid] if type(cid) is int else []
        for key, kind in (("uid", str), ("department", int), ("chara_id", int), ("partner_id", int), ("add_time", datetime)):
            value = item.get(key)
            valid = type(value) is int if kind is int else isinstance(value, kind)
            if not valid:
                failures.append(make_failure("OFFICIAL-01", "队列条目", f"cid={cid!r} key={prefix}.{key} value={value!r}；须为{kind.__name__}", ids))
            elif key in ("chara_id", "partner_id") and value != 0 and isinstance(characters, dict) and value not in characters:
                failures.append(make_failure("OFFICIAL-01", "队列条目", f"[warning] cid={cid!r} key={prefix}.{key} value={value!r}；角色不在character_data中", ids))
    return failures


@register_check("OFFICIAL-02", "事件履历")
def check_official_02() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 全局与角色履历条目须为dict，time为datetime，choice为非负整数。"""
    cache = cache_control.cache
    histories = [(None, "official_event_history", getattr(getattr(cache, "rhodes_island", None), "official_event_history", None))]
    characters = getattr(cache, "character_data", None)
    if isinstance(characters, dict):
        for cid, character in characters.items():
            histories.append((cid, "child_growth.event_history", getattr(getattr(character, "child_growth", None), "event_history", None)))
    failures = []
    for cid, prefix, history in histories:
        if not isinstance(history, dict):
            continue
        ids = [cid] if type(cid) is int else []
        for uid, entry in history.items():
            key = f"{prefix}[{uid!r}]"
            if not isinstance(entry, dict):
                failures.append(make_failure("OFFICIAL-02", "事件履历", f"cid={cid!r} key={key} value={entry!r}；须为dict", ids))
                continue
            for field in ("time", "choice"):
                value = entry.get(field)
                valid = isinstance(value, datetime) if field == "time" else type(value) is int and value >= 0
                if not valid:
                    failures.append(make_failure("OFFICIAL-02", "事件履历", f"cid={cid!r} key={key}.{field} value={value!r}；time须为datetime，choice须为非负整数", ids))
    return failures
