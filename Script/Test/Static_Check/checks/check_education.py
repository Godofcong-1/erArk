# -*- coding: UTF-8 -*-
"""静态检查系统 - 养成值、课表与学期快照。只读现有 child_growth，不创建养成数据。"""

import math
from typing import List

from Script.Core import cache_control
from Script.Config import game_config
from Script.System.Education_System import education_constant
from ..check_registry import CheckFailure, register_check, make_failure

# 检查名供注册与逐元素诊断共用。
_NAMES = {
    "EDU-01": "照料值",
    "EDU-02": "性格倾向",
    "EDU-03": "胎教值",
    "EDU-04": "出勤累计",
    "EDU-05": "学期基线",
    "EDU-06": "学期号",
    "EDU-07": "成绩单快照",
    "EDU-08": "全局课表结构",
    "EDU-09": "个人课表结构",
    "EDU-10": "模板与覆盖槽",
    "EDU-11": "模板引用",
    "EDU-12": "课时去重标记",
}


def _characters(cache):
    """参数: cache(缓存对象)；返回值: dict；功能: 只读取角色表，缺失或类型错误时跳过。"""
    data = getattr(cache, "character_data", None)
    return data if isinstance(data, dict) else {}


def _growths(cache):
    """参数: cache(缓存对象)；返回值: 迭代器(cid,养成对象)；功能: 遍历已有养成数据，绝不惰性创建。"""
    for cid, character in _characters(cache).items():
        growth = getattr(character, "child_growth", None)
        if growth is not None:
            yield cid, growth


def _finite(value):
    """参数: value(任意值)；返回值: bool；功能: 接受有限整数或浮点数，排除布尔值与非有限浮点。"""
    return type(value) is int or (type(value) is float and math.isfinite(value))


def _int_range(value, low, high=None):
    """参数: value(任意值)、low(int)、high(int或None)；返回值: bool；功能: 检查整数及闭区间。"""
    return type(value) is int and value >= low and (high is None or value <= high)


def _failure(check_id, cid, key, value, rule, warning=False):
    """参数: check_id/ key/ rule(str)、cid(角色id或None)、value(任意值)、warning(bool)；返回值: CheckFailure；功能: 给出元素定位与原值。"""
    return make_failure(check_id, _NAMES[check_id], f"{'[warning] ' if warning else ''}cid={cid!r} key={key} value={value!r}；{rule}", [cid] if type(cid) is int else [])


def _cells(table, check_id, cid, prefix, failures):
    """参数: table(dict)、check_id/prefix(str)、cid(角色id或None)、failures(list)；返回值: 迭代器；功能: 校验星期与节次，返回结构完好的格子。"""
    if not isinstance(table, dict):
        return
    for day, periods in table.items():
        day_key = f"{prefix}[{day!r}]"
        if not _int_range(day, 0, 6) or not isinstance(periods, dict):
            failures.append(_failure(check_id, cid, day_key, periods, "星期须为0–6整数，节次表须为dict"))
            continue
        for period, cell in periods.items():
            key = f"{day_key}[{period!r}]"
            if not _int_range(period, 0, 8) or not isinstance(cell, list) or len(cell) != 2:
                failures.append(_failure(check_id, cid, key, cell, "节次须为0–8整数，格子须为二元素list"))
                continue
            yield key, cell


@register_check("EDU-01", _NAMES["EDU-01"])
def check_edu_01() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 照料值须为有限非负数。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        value = getattr(growth, "care_point", None)
        if not _finite(value) or value < 0:
            failures.append(_failure("EDU-01", cid, "care_point", value, "须为有限非负数"))
    return failures


@register_check("EDU-02", _NAMES["EDU-02"])
def check_edu_02() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 性格倾向须为dict，键为0–3，值有限，允许负值与缺键。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        points = getattr(growth, "personality_point", None)
        if not isinstance(points, dict):
            failures.append(_failure("EDU-02", cid, "personality_point", points, "须为dict"))
            continue
        for key, value in points.items():
            if not _int_range(key, 0, 3) or not _finite(value):
                failures.append(_failure("EDU-02", cid, f"personality_point[{key!r}]", value, "键须为0–3整数，值须为有限数"))
    return failures


@register_check("EDU-03", _NAMES["EDU-03"])
def check_edu_03() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 检查全角色妊娠与已有养成记录的胎教值及常量上限。"""
    cache = cache_control.cache
    failures = []
    for cid, character in _characters(cache).items():
        for field in ("pregnancy", "child_growth"):
            data = getattr(character, field, None)
            if data is None:
                continue
            value = getattr(data, "prenatal_point", None)
            if not _finite(value) or not 0 <= value <= education_constant.PRENATAL_POINT_MAX:
                failures.append(_failure("EDU-03", cid, f"{field}.prenatal_point", value, f"须为0–{education_constant.PRENATAL_POINT_MAX}的有限数"))
    return failures


@register_check("EDU-04", _NAMES["EDU-04"])
def check_edu_04() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 出勤、缺课和翘课累计为非负整数，翘课不超过缺课。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        for key in ("attend_class_count", "absent_count", "skip_count"):
            value = getattr(growth, key, None)
            if not _int_range(value, 0):
                failures.append(_failure("EDU-04", cid, key, value, "须为非负整数"))
        skip, absent = getattr(growth, "skip_count", None), getattr(growth, "absent_count", None)
        if _int_range(skip, 0) and _int_range(absent, 0) and skip > absent:
            failures.append(_failure("EDU-04", cid, "skip_count", skip, f"不得超过absent_count={absent}"))
    return failures


@register_check("EDU-05", _NAMES["EDU-05"])
def check_edu_05() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 学期出勤、缺课基线须为非负整数且不超过对应累计。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        for key, counter in (("semester_base_attend", "attend_class_count"), ("semester_base_absent", "absent_count")):
            value, total = getattr(growth, key, None), getattr(growth, counter, None)
            if not _int_range(value, 0) or (_int_range(total, 0) and value > total):
                failures.append(_failure("EDU-05", cid, key, value, f"须为非负整数且不超过{counter}={total!r}"))
    return failures


@register_check("EDU-06", _NAMES["EDU-06"])
def check_edu_06() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 学期号为空列表或[整数年,季月]，不要求等于当前学期。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        value = getattr(growth, "semester_id", None)
        if not (isinstance(value, list) and (not value or (len(value) == 2 and type(value[0]) is int and type(value[1]) is int and value[1] in (3, 6, 9, 12)))):
            failures.append(_failure("EDU-06", cid, "semester_id", value, "须为[]或[整数年,3/6/9/12]"))
    return failures


@register_check("EDU-07", _NAMES["EDU-07"])
def check_edu_07() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 校验成绩单年份、季月、出缺勤与整数百分比，超出历史上限只警示。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        history = getattr(growth, "report_card_history", None)
        if not isinstance(history, list):
            failures.append(_failure("EDU-07", cid, "report_card_history", history, "须为list"))
            continue
        if len(history) > education_constant.REPORT_CARD_HISTORY_MAX:
            failures.append(_failure("EDU-07", cid, "report_card_history.length", len(history), f"超过保留上限{education_constant.REPORT_CARD_HISTORY_MAX}", True))
        for index, entry in enumerate(history):
            prefix = f"report_card_history[{index}]"
            if not isinstance(entry, dict):
                failures.append(_failure("EDU-07", cid, prefix, entry, "须为dict"))
                continue
            for key in ("year", "month", "attend", "absent", "rate"):
                value = entry.get(key)
                valid = type(value) is int
                if valid:
                    if key == "month":
                        valid = value in (3, 6, 9, 12)
                    elif key == "year":
                        valid = 1 <= value <= 9999
                    else:
                        valid = value >= 0 and (key != "rate" or value <= 100)
                if not valid:
                    failures.append(_failure("EDU-07", cid, f"{prefix}.{key}", value, "年份须为1–9999、季月须为3/6/9/12、计数非负、百分比0–100，均为整数"))
    return failures


@register_check("EDU-08", _NAMES["EDU-08"])
def check_edu_08() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 全局课表按星期、节次存[能力id,教师id]，教师可为-1，不要求在场或在岗。"""
    cache = cache_control.cache
    schedule = getattr(getattr(cache, "rhodes_island", None), "class_schedule", None)
    if not isinstance(schedule, dict):
        return []
    abilities = getattr(game_config, "config_ability", None)
    characters = getattr(cache, "character_data", None)
    failures = []
    for room, table in schedule.items():
        for key, cell in _cells(table, "EDU-08", None, f"class_schedule[{room!r}]", failures):
            ability, teacher = cell
            if (
                type(ability) is not int
                or (isinstance(abilities, dict) and ability not in abilities)
                or type(teacher) is not int
                or (teacher != -1 and isinstance(characters, dict) and teacher not in characters)
            ):
                failures.append(_failure("EDU-08", None, key, cell, "能力须在配置表中，教师须为-1或现有角色id"))
    return failures


@register_check("EDU-09", _NAMES["EDU-09"])
def check_edu_09() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 个人课表按课型检查场景名、娱乐配置id或岗位配置id。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        for key, cell in _cells(getattr(growth, "selected_course", None), "EDU-09", cid, "selected_course", failures):
            course_type, target = cell
            valid = _int_range(course_type, 0, 5)
            if valid and course_type <= 3:
                valid = isinstance(target, str)
            elif valid:
                config = getattr(game_config, "config_entertainment" if course_type == 4 else "config_work_type", None)
                valid = type(target) is int and (not isinstance(config, dict) or target in config)
            if not valid:
                failures.append(_failure("EDU-09", cid, key, cell, "课型须为0–5；0–3目标为场景名，4为娱乐配置id，5为岗位配置id"))
    return failures


def _check_slots(slots, cid, prefix, failures):
    """参数: slots(dict)、cid(角色id或None)、prefix(str)、failures(list)；返回值: None；功能: 检查模板与覆盖表的时段及活动id。"""
    if not isinstance(slots, dict):
        return
    config = getattr(game_config, "config_entertainment", None)
    for key, value in slots.items():
        if not _int_range(key, 0, 2) or type(value) is not int or (value != 0 and isinstance(config, dict) and value not in config):
            failures.append(_failure("EDU-10", cid, f"{prefix}[{key!r}]", value, "时段须为0–2，活动须为0或娱乐配置id"))


@register_check("EDU-10", _NAMES["EDU-10"])
def check_edu_10() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 校验模板slot和角色覆盖表，空模板合法。"""
    cache = cache_control.cache
    failures = []
    templates = getattr(getattr(cache, "rhodes_island", None), "child_schedule_template", None)
    if isinstance(templates, dict):
        for key, template in templates.items():
            if isinstance(template, dict):
                _check_slots(template.get("slot"), None, f"child_schedule_template[{key!r}].slot", failures)
    for cid, growth in _growths(cache):
        _check_slots(getattr(growth, "schedule_override", None), cid, "schedule_override", failures)
    return failures


@register_check("EDU-11", _NAMES["EDU-11"])
def check_edu_11() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 角色模板引用须为0或当前模板表内的键。"""
    cache = cache_control.cache
    templates = getattr(getattr(cache, "rhodes_island", None), "child_schedule_template", None)
    if not isinstance(templates, dict):
        return []
    failures = []
    for cid, growth in _growths(cache):
        value = getattr(growth, "schedule_template_id", None)
        if type(value) is not int or (value != 0 and value not in templates):
            failures.append(_failure("EDU-11", cid, "schedule_template_id", value, "须为0或已有模板id"))
    return failures


@register_check("EDU-12", _NAMES["EDU-12"])
def check_edu_12() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 出缺勤去重标记须为空列表或[正整数日期序数,0–8节次]。"""
    cache = cache_control.cache
    failures = []
    for cid, growth in _growths(cache):
        for key in ("last_attend_period", "last_absent_period"):
            value = getattr(growth, key, None)
            if not (isinstance(value, list) and (not value or (len(value) == 2 and _int_range(value[0], 1) and _int_range(value[1], 0, 8)))):
                failures.append(_failure("EDU-12", cid, key, value, "须为[]或[正整数日期序数,0–8整数节次]"))
    return failures
