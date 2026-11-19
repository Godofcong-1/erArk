# -*- coding: UTF-8 -*-
"""静态检查系统 - 生育开关、关闭后的卵生存量与烹饪记忆。"""

from typing import List

from Script.Core import cache_control
from Script.Config import game_config
from Script.System.Pregnancy_System import pregnancy_constant
from ..check_registry import CheckFailure, register_check, make_failure


@register_check("BIRTH-01", "生育开关")
def check_birth_01() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 生育开关覆盖配置键，值为0/1，多余键仅警示。"""
    cache = cache_control.cache
    setting = getattr(cache, "all_system_setting", None)
    if setting is None:
        return []
    values = getattr(setting, "birth_type_setting", None)
    if not isinstance(values, dict):
        return [make_failure("BIRTH-01", "生育开关", f"cid=None key=birth_type_setting value={values!r}；须为dict", [])]
    config = getattr(game_config, "config_birth_type_setting", None)
    failures = []
    if isinstance(config, dict):
        for key in config:
            if key not in values:
                failures.append(make_failure("BIRTH-01", "生育开关", f"cid=None key=birth_type_setting[{key!r}] value=<缺失>；配置要求此键", []))
    for key, value in values.items():
        if isinstance(config, dict) and key not in config:
            failures.append(make_failure("BIRTH-01", "生育开关", f"[warning] cid=None key=birth_type_setting[{key!r}] value={value!r}；配置表无此键", []))
        if type(value) is not int or value not in (0, 1):
            failures.append(make_failure("BIRTH-01", "生育开关", f"cid=None key=birth_type_setting[{key!r}] value={value!r}；须为0或1", []))
    return failures


@register_check("BIRTH-02", "已关闭卵生存量")
def check_birth_02() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 按原始种族生育方式检查关闭后的卵、无壳排卵机会与博士持卵索引，不检查胎数。"""
    cache = cache_control.cache
    values = getattr(getattr(cache, "all_system_setting", None), "birth_type_setting", None)
    characters = getattr(cache, "character_data", None)
    races = getattr(game_config, "config_race", None)
    if not isinstance(values, dict) or not isinstance(characters, dict) or not isinstance(races, dict):
        return []
    disabled = {kind for kind in (pregnancy_constant.BIRTH_TYPE_EGG, pregnancy_constant.BIRTH_TYPE_EGG_SOFT) if values.get(kind, 1) == 0}
    mothers = set()
    failures = []
    for cid, character in characters.items():
        if cid == 0:
            continue
        race = getattr(character, "race", None)
        if type(race) is not int:
            continue
        birth_type = getattr(races.get(race), "birth_type", pregnancy_constant.BIRTH_TYPE_SINGLE)
        if type(birth_type) is not int or birth_type not in disabled:
            continue
        mothers.add(cid)
        pregnancy = getattr(character, "pregnancy", None)
        eggs = getattr(pregnancy, "eggs", None)
        if isinstance(eggs, dict):
            for key, value in eggs.items():
                failures.append(make_failure("BIRTH-02", "已关闭卵生存量", f"cid={cid!r} key=pregnancy.eggs[{key!r}] value={value!r}；birth_type={birth_type}已关闭", [cid]))
        chance = getattr(pregnancy, "external_ovulation_chance", False)
        if birth_type == pregnancy_constant.BIRTH_TYPE_EGG_SOFT and chance:
            failures.append(make_failure("BIRTH-02", "已关闭卵生存量", f"cid={cid!r} key=external_ovulation_chance value={chance!r}；无壳卵生已关闭", [cid]))
    held = getattr(getattr(characters.get(0), "pl_collection", None), "held_eggs", None)
    if isinstance(held, dict):
        for key, value in held.items():
            if isinstance(value, (list, tuple)) and len(value) == 2 and type(value[0]) is int and value[0] in mothers:
                failures.append(make_failure("BIRTH-02", "已关闭卵生存量", f"cid={value[0]} key=pl_collection.held_eggs[{key!r}] value={value!r}；母亲的卵生方式已关闭", [0, value[0]]))
    return failures


def _check_cook_memory(ri, field, check_id, name, low, high):
    """参数: ri(罗德岛对象)、field/check_id/name(str)、low/high(int)；返回值: List[CheckFailure]；功能: 校验烹饪记忆字典的页签与数值范围。"""
    if ri is None:
        return []
    memory = getattr(ri, field, None)
    if not isinstance(memory, dict):
        return [make_failure(check_id, name, f"cid=None key={field} value={memory!r}；须为dict", [])]
    failures = []
    for key, value in memory.items():
        if type(key) is not int or key not in (0, 1, 2) or type(value) is not int or not low <= value <= high:
            failures.append(make_failure(check_id, name, f"cid=None key={field}[{key!r}] value={value!r}；键须为0–2整数，值须为{low}–{high}整数", []))
    return failures


@register_check("COOK-01", "烹饪模式记忆")
def check_cook_01() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 烹饪模式字典只允许0–2页签，模式为0或1，允许缺键。"""
    cache = cache_control.cache
    return _check_cook_memory(getattr(cache, "rhodes_island", None), "makefood_cook_mode", "COOK-01", "烹饪模式记忆", 0, 1)


@register_check("COOK-02", "制作份数记忆")
def check_cook_02() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 制作份数字典只允许0–2页签，份数为1–10整数。"""
    cache = cache_control.cache
    return _check_cook_memory(getattr(cache, "rhodes_island", None), "makefood_make_count", "COOK-02", "制作份数记忆", 1, 10)
