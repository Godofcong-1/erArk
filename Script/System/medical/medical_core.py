# -*- coding: UTF-8 -*-
"""医疗系统核心通用工具模块

集中存放医疗系统中多个子模块共用的基础辅助函数，
例如缓存对象查找、病人定位、床位与等级计算等。
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from Script.Config import config_def, game_config
from Script.Core import cache_control, game_type
from Script.System.Medical import medical_constant


def _bump_daily_counter(
    rhodes_island: Optional[game_type.Rhodes_Island],
    key: str,
    value: object,
) -> None:
    """更新医疗日度统计表中的计数。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 目标基地缓存对象，None 时直接返回。
        key (str): 统计字段名称，例如 "hospitalized_today"。
        value (object): 本次需要累加的数值或药品消耗映射。
    返回:
        None: 直接在基地对象的计数字典上写入变更。
    """

    # 无可用基地或统计对象时不做处理。
    if rhodes_island is None:
        return

    # 获取显性统计结构，若缺失则自动初始化。
    counters = _obtain_daily_counters(rhodes_island)
    if counters is None:
        return

    # 在目标字段累加增量并写回基对象，保持运行期数据一致。
    counters.bump(key, value)


def _apply_income_to_rhodes(
    rhodes_island: Optional[game_type.Rhodes_Island],
    income_value: int,
) -> None:
    """为罗德岛医疗系统入账指定收入。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 目标基地缓存对象。
        income_value (int): 本次入账的龙门币数值，仅当大于 0 时生效。
    返回:
        None: 在基地对象上累加收入并同步物资仓库。
    """

    # 收入不合法或没有目标基地时直接退出。
    if rhodes_island is None or income_value <= 0:
        return
    # 更新医疗收入字段并累计到全局收益。
    rhodes_island.medical_income_today += income_value
    rhodes_island.medical_income_total += income_value
    rhodes_island.all_income += income_value
    # 同步物资仓库中的龙门币库存。
    inventory = getattr(rhodes_island, "materials_resouce", None)
    if isinstance(inventory, dict):
        inventory[1] = int(inventory.get(1, 0) or 0) + income_value


def _get_rhodes_island(
    target_base: Optional[game_type.Rhodes_Island],
) -> Optional[game_type.Rhodes_Island]:
    """返回调用环境可用的罗德岛基地对象。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 若已显式传入则直接返回该对象。
    返回:
        Optional[game_type.Rhodes_Island]: 实际可用的基地实例，若不存在则为 None。
    """

    # 若调用方已提供目标基地则直接返回。
    if target_base is not None:
        return target_base
    # 否则从缓存中获取默认的罗德岛实例。
    cache_obj = getattr(cache_control, "cache", None)
    return getattr(cache_obj, "rhodes_island", None)


def _obtain_daily_counters(
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> Optional[medical_constant.MedicalDailyCounters]:
    """返回罗德岛对象上的医疗当日统计结构。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 当前需要读写的基地实例。
    返回:
        Optional[medical_constant.MedicalDailyCounters]:
            规范化后的统计对象，若基地不存在则返回 None。
    """

    # 缺少基地对象时无法提供统计结构。
    if rhodes_island is None:
        return None

    # 读取现有统计字段并在必要时转化为结构体实例。
    raw_value = getattr(rhodes_island, "medical_daily_counters", None)
    counters = medical_constant.MedicalDailyCounters.from_mapping(raw_value)

    # 将规范化结果回写至基地对象，确保后续访问保持一致。
    rhodes_island.medical_daily_counters = counters
    return counters


def _locate_patient(
    patient_id: int,
    rhodes_island: game_type.Rhodes_Island,
) -> Tuple[Optional[medical_constant.MedicalPatient], bool]:
    """在门诊和住院列表中查找病人，返回病人对象与是否住院标记。

    参数:
        patient_id (int): 目标病人的唯一编号。
        rhodes_island (game_type.Rhodes_Island): 当前罗德岛缓存对象。
    返回:
        Tuple[Optional[medical_constant.MedicalPatient], bool]:
            找到的病人对象以及是否处于住院列表的布尔标记。
    """

    # 先在门诊病人表中查找。
    patient = rhodes_island.medical_patients_today.get(patient_id)
    if patient is not None:
        return patient, False

    # 再尝试在住院病人表中查找。
    patient = rhodes_island.medical_hospitalized.get(patient_id)
    if patient is not None:
        return patient, True

    return None, False


def _sync_legacy_patient_counters(rhodes_island: game_type.Rhodes_Island) -> None:
    """同步旧版医疗统计字段，兼容尚未迁移的 UI 逻辑。

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地对象。
    返回:
        None: 直接写入 `patient_now` 字段用于旧 UI 显示。
    """

    # 缺少基地对象时无需同步旧字段。
    if rhodes_island is None:
        return
    # 统计待诊病人的数量并写回旧字段。
    waiting_states = medical_constant.WAITING_QUEUE_STATE_SET
    waiting_count = sum(
        1
        for patient in rhodes_island.medical_patients_today.values()
        if patient.state in waiting_states
    )
    rhodes_island.patient_now = waiting_count


def _get_medical_facility_level(rhodes_island: game_type.Rhodes_Island) -> int:
    """读取医疗部设施等级，缺省返回 0。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
    返回:
        int: 医疗部设施等级，缺省为 0。
    """

    return int(rhodes_island.facility_level.get(medical_constant.MEDICAL_FACILITY_ID, 0) or 0)


def _pick_hospital_level_config(level: int) -> Optional[config_def.Medical_Hospital_Level]:
    """根据设施等级选取对应的医院等级配置。

    参数:
        level (int): 医疗设施等级。
    返回:
        Optional[config_def.Medical_Hospital_Level]: 匹配到的配置实例，若无则为 None。
    """

    # 若配置表为空则直接返回。
    if not game_config.config_medical_hospital_level:
        return None
    # 优先命中完全匹配的等级。
    if level in game_config.config_medical_hospital_level:
        return game_config.config_medical_hospital_level[level]
    # 退而求其次选择不超过目标等级的最大配置。
    eligible = [candidate for candidate in game_config.config_medical_hospital_level.keys() if candidate <= level]
    if eligible:
        return game_config.config_medical_hospital_level[max(eligible)]
    # 若仍未命中则使用最小等级作为兜底。
    minimal = min(game_config.config_medical_hospital_level.keys())
    return game_config.config_medical_hospital_level.get(minimal)


def _calculate_patient_refresh_count(
    rhodes_island: game_type.Rhodes_Island,
    level_config: config_def.Medical_Hospital_Level,
) -> int:
    """依据医院等级与收费系数计算今日应刷新病人数。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
        level_config (config_def.Medical_Hospital_Level): 医院等级配置内容。
    返回:
        int: 预计应刷新病人的数量。
    """

    # 读取医院等级配置中的基础病人数。
    base_count = max(int(level_config.daily_patient_base), 0)
    if base_count <= 0:
        return 0

    # 将收费系数转换为加成 / 惩罚倍率。
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    safe_ratio = max(price_ratio, 0.01)
    penalty = 1.0 / safe_ratio
    penalty = clamp(penalty, level_config.ratio_min, level_config.ratio_max)

    # 按价格系数求得刷新倍率，并计算最终刷新数量。
    refresh_multiplier = resolve_price_refresh_multiplier(price_ratio)
    refresh_value = base_count * penalty * refresh_multiplier
    return max(int(math.floor(refresh_value)), 0)


def _calculate_medical_bed_limit(rhodes_island: game_type.Rhodes_Island) -> int:
    """计算当前医疗部床位上限（基础值 + 兜底当前在院人数）。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
    返回:
        int: 计算后的床位上限，至少等于当前在院人数。
    """

    # 根据设施等级查找当前医院等级配置。
    level_config = _pick_hospital_level_config(_get_medical_facility_level(rhodes_island))
    base_limit = int(level_config.bed_limit) if level_config else 0
    # 医生数量提供额外床位加成。
    hospital_bonus = (
        len(getattr(rhodes_island, "medical_hospital_doctor_ids", []) or [])
        * medical_constant.HOSPITAL_DOCTOR_BED_BONUS
    )
    total_limit = base_limit + hospital_bonus
    # 确保床位不低于现有住院人数。
    current_occupancy = len(rhodes_island.medical_hospitalized)
    return max(total_limit, current_occupancy)


def _calculate_doctor_power(doctor_ids: Optional[list[int]]) -> float:
    """计算医生列表的医疗能力总和，用于缓存字段刷新。

    参数:
        doctor_ids (Optional[list[int]]): 医生编号列表，允许为 None 或空列表。
    返回:
        float: 医疗能力等级的加总结果。
    """

    # 没有医生编号时直接返回零。
    if not doctor_ids:
        return 0.0
    # 从全局缓存中检索角色数据以累加能力值。
    cache_obj = getattr(cache_control, "cache", None)
    character_table = getattr(cache_obj, "character_data", {}) if cache_obj else {}
    total_power = 0.0
    for doctor_id in doctor_ids:
        character = character_table.get(doctor_id)
        if character is None:
            continue
        total_power += float(character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)
    return total_power


def _ensure_runtime_dict(rhodes_island: game_type.Rhodes_Island) -> None:
    """确保医疗运行期字段存在且类型正确。

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地对象。
    返回:
        None: 若字段缺失或类型不符，则按默认值修正。
    """

    # 保证病人、住院与手术记录容器存在且为正确类型。
    rhodes_island.medical_patients_today = dict(getattr(rhodes_island, "medical_patients_today", {}) or {})
    rhodes_island.medical_hospitalized = dict(getattr(rhodes_island, "medical_hospitalized", {}) or {})
    rhodes_island.medical_surgery_records = list(getattr(rhodes_island, "medical_surgery_records", []) or [])

    # 校正药品累加器，确保所有资源键都已注册。
    accumulator = dict(getattr(rhodes_island, "medical_inventory_accumulator", {}) or {})
    for resource_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS:
        accumulator.setdefault(resource_id, 0.0)
    rhodes_island.medical_inventory_accumulator = accumulator

    # 转换收入、计数器与日志等字段的类型。
    rhodes_island.medical_income_today = int(getattr(rhodes_island, "medical_income_today", 0) or 0)
    rhodes_island.medical_income_total = int(getattr(rhodes_island, "medical_income_total", 0) or 0)
    rhodes_island.medical_daily_counters = medical_constant.MedicalDailyCounters.from_mapping(
        getattr(rhodes_island, "medical_daily_counters", None)
    )
    rhodes_island.medical_recent_reports = list(
        getattr(rhodes_island, "medical_recent_reports", []) or []
    )
    rhodes_island.medical_clinic_doctor_ids = list(
        getattr(rhodes_island, "medical_clinic_doctor_ids", []) or []
    )
    rhodes_island.medical_hospital_doctor_ids = list(
        getattr(rhodes_island, "medical_hospital_doctor_ids", []) or []
    )
    rhodes_island.medical_clinic_doctor_power = float(
        getattr(rhodes_island, "medical_clinic_doctor_power", 0.0) or 0.0
    )
    rhodes_island.medical_hospital_doctor_power = float(
        getattr(rhodes_island, "medical_hospital_doctor_power", 0.0) or 0.0
    )
    # 处理接诊优先策略，保证值转换为合法枚举。
    priority_value = getattr(
        rhodes_island,
        "medical_patient_priority_mode",
        medical_constant.MedicalPatientPriority.NORMAL.value,
    )
    try:
        resolved_priority = medical_constant.MedicalPatientPriority(str(priority_value))
    except ValueError:
        resolved_priority = medical_constant.MedicalPatientPriority.NORMAL
    rhodes_island.medical_patient_priority_mode = resolved_priority.value


def _resolve_default_price_ratio() -> float:
    """返回收费系数的默认值，默认 1.0。

    返回:
        float: 收费系数默认值。
    """
    return 1.0


def clamp(value: float, min_value: Optional[float], max_value: Optional[float]) -> float:
    """带上下限的数值夹取，None 表示不限制。

    参数:
        value (float): 原始数值。
        min_value (Optional[float]): 允许的最小值，None 表示无下限。
        max_value (Optional[float]): 允许的最大值，None 表示无上限。
    返回:
        float: 夹取后的结果。
    """

    # 按照下限约束数值。
    result = value
    if min_value is not None:
        result = max(result, float(min_value))
    # 再按上限约束数值。
    if max_value is not None:
        result = min(result, float(max_value))
    return result


def _pick_price_config(price_ratio: float) -> List[float]:
    """根据收费系数计算刷新倍率与收入倍率。

    参数:
        price_ratio (float): 当前收费系数。
    返回:
        List[float]: 包含刷新倍率与收入倍率的列表。
    """

    # 计算收费系数偏离 1.0 的幅度，并转换为步数。
    delta = price_ratio - 1.0
    steps = int(abs(delta) / 0.05)

    # 正偏时刷新倍率递减，负偏时递增。
    refresh_multiplier = 1.0
    if delta > 0:
        for _ in range(steps):
            refresh_multiplier *= 0.92
    elif delta < 0:
        for _ in range(steps):
            refresh_multiplier *= 1.08

    # 收入倍率与刷新倍率相反，正偏增长、负偏衰减。
    income_multiplier = 1.0
    if delta > 0:
        for _ in range(steps):
            income_multiplier *= 1.05
    elif delta < 0:
        for _ in range(steps):
            income_multiplier *= 0.95

    return [refresh_multiplier, income_multiplier]


def resolve_price_refresh_multiplier(price_ratio: float) -> float:
    """根据收费系数找到刷新倍率，若配置缺失返回 1.0。

    参数:
        price_ratio (float): 当前收费系数。
    返回:
        float: 刷新倍率，缺省为 1.0。
    """

    # 获取倍率配置并返回刷新倍率分量。
    config = _pick_price_config(price_ratio)
    if not config:
        return 1.0
    return config[0]


def resolve_price_income_multiplier(price_ratio: float) -> float:
    """根据收费系数找到收入倍率，若配置缺失返回 1.0。

    参数:
        price_ratio (float): 当前收费系数。
    返回:
        float: 收入倍率，缺省为 1.0。
    """

    # 获取倍率配置并返回收入倍率分量。
    config = _pick_price_config(price_ratio)
    if not config:
        return 1.0
    return config[1]


def _migrate_legacy_income(rhodes_island: game_type.Rhodes_Island) -> None:
    """兼容旧版存档中医疗收入字段。

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地对象。
    返回:
        None: 将旧字段的数值迁移至新的收入字段。
    """

    # 读取旧字段数值并写入新字段。
    legacy_total = getattr(rhodes_island, "medical_income_total", 0)
    legacy_today = getattr(rhodes_island, "medical_income_today", 0)
    rhodes_island.medical_income_total = int(legacy_total or 0)
    rhodes_island.medical_income_today = int(legacy_today or 0)

    # 兼容更旧的 medical_income 字段。
    if hasattr(rhodes_island, "medical_income"):
        legacy_income = int(getattr(rhodes_island, "medical_income", 0) or 0)
        rhodes_island.medical_income_total = max(rhodes_island.medical_income_total, legacy_income)
