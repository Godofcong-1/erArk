# -*- coding: UTF-8 -*-
"""病人生成与价格倍率工具模块

该模块负责医疗系统中与病人生成、并发症组合及收费倍率计算相关的逻辑，
为 `medical_service.py` 提供可复用的纯函数与帮助方法。"""
from __future__ import annotations

import random
from typing import Any, Dict, Iterable, List, Optional, Tuple

from Script.Config import config_def, game_config
from Script.Core import value_handle
from Script.System.Medical import medical_constant


def create_patient_stub(severity_level: int, **extra_fields: Any) -> medical_constant.MedicalPatient:
    """创建尚未填充具体症状的病人结构

    参数:
        severity_level (int): 病情等级 ID，用于设定病人的基础严重度。
        extra_fields (Any): 其他需要写入病人结构的字段键值对。

    返回:
        medical_constant.MedicalPatient: 预填 ID、严重度并补齐药品键的病人对象。"""

    # 通过自增计数器生成唯一病人 ID
    patient = medical_constant.MedicalPatient(
        patient_id=next(medical_constant.PATIENT_ID_COUNTER),
        severity_level=severity_level,
        **extra_fields,
    )
    # 确保药品需求字典包含所有资源键，方便后续叠加
    patient.ensure_resource_keys()
    return patient


def pick_severity_level(facility_level: Optional[int] = None) -> Optional[int]:
    """按权重抽取一个病情等级 ID

    参数:
        facility_level (Optional[int]): 当前医疗区等级，用于限制可出现的病情档位。

    返回:
        Optional[int]: 抽取到的病情等级，若无配置则返回 None。"""

    # 若权重表缺失，直接返回 None
    if not game_config.medical_severity_weight_table:
        return None

    # 根据医疗区等级过滤可用档位
    def _is_unlocked(severity_id: int) -> bool:
        if facility_level is None:
            return True
        if severity_id == 3:
            return facility_level >= 4
        if severity_id == 2:
            return facility_level >= 2
        return True

    filtered_entries = [entry for entry in game_config.medical_severity_weight_table if _is_unlocked(entry[0])]
    if not filtered_entries:
        return None

    # 计算总权重并进行权重随机
    total_weight = sum(weight for _, weight in filtered_entries)
    if total_weight <= 0:
        return filtered_entries[0][0]
    roll = random.uniform(0, total_weight)
    cursor = 0.0
    for severity_id, weight in filtered_entries:
        cursor += weight
        if roll <= cursor:
            return severity_id
    # 兜底返回最后一项的病情等级
    return filtered_entries[-1][0]


def generate_patient(
    severity_level: int,
    rhodes_island,
) -> Optional[medical_constant.MedicalPatient]:
    """生成单个病人实体

    参数:
        severity_level (int): 已抽取的病情等级。
        rhodes_island (game_type.Rhodes_Island): 当前基地，用于读取收费系数等信息。

    返回:
        Optional[medical_constant.MedicalPatient]: 成功生成的病人对象，配置缺失时返回 None。"""

    # 获取病情等级配置，若缺失则无法创建病人
    severity_config = game_config.config_medical_severity.get(severity_level)
    if severity_config is None:
        return None

    # 创建病人骨架，并随机生成基本属性
    patient = create_patient_stub(severity_level=severity_level)
    patient.personality_type = random.choice(list(medical_constant.MedicalPatientPersonality))
    patient.race_id = _pick_patient_race_id()
    patient.age = random.randint(10, 60)

    # 构建并发症列表及额外药物需求
    complications, medicine_bonus = _build_complications_for_patient(severity_config)
    patient.complications = [comp.cid for comp in complications]
    if complications:
        patient.metadata["complication_trace"] = [
            {
                "cid": comp.cid,
                "system_id": comp.system_id,
                "part_id": comp.part_id,
                "severity_level": comp.severity_level,
            }
            for comp in complications
        ]
    patient.need_surgery = any(comp.requires_surgery == 1 for comp in complications)

    # 计算基础药物需求量
    normal_resource_id = medical_constant.MedicalMedicineResource.NORMAL.value
    base_normal_need = random.uniform(
        float(severity_config.normal_medicine_min),
        float(max(severity_config.normal_medicine_max, severity_config.normal_medicine_min)),
    )
    patient.need_resources[normal_resource_id] = max(base_normal_need + medicine_bonus, 0.0)

    # 合并特殊药物模板
    special_template = game_config.medical_severity_special_medicine.get(severity_level, {})
    for resource_id, amount in special_template.items():
        patient.need_resources[resource_id] = patient.need_resources.get(resource_id, 0.0) + float(amount)

    # 写入通用元信息方便 UI 展示
    patient.metadata.setdefault("severity_name", severity_config.name)
    patient.metadata.setdefault("price_ratio", rhodes_island.medical_price_ratio)
    return patient


def resolve_price_refresh_multiplier(price_ratio: float) -> float:
    """根据收费系数找到刷新倍率，若配置缺失返回 1.0

    参数:
        price_ratio (float): 当前收费系数。

    返回:
        float: 对应的刷新倍率，默认返回 1.0。"""

    # 尝试匹配最接近的收费配置并返回刷新倍率
    config = _pick_price_config(price_ratio)
    if config is None:
        return 1.0
    return config[0]


def resolve_price_income_multiplier(price_ratio: float) -> float:
    """根据收费系数找到收入倍率，若配置缺失返回 1.0

    参数:
        price_ratio (float): 当前收费系数。

    返回:
        float: 对应的收入倍率，默认返回 1.0。"""

    # 定位收费配置，并读取收入倍率字段
    config = _pick_price_config(price_ratio)
    if config is None:
        return 1.0
    return config[1]


def clamp(value: float, min_value: Optional[float], max_value: Optional[float]) -> float:
    """带上下限的夹取函数，空值表示不限制

    参数:
        value (float): 输入数值。
        min_value (Optional[float]): 最小阈值，None 表示不限制。
        max_value (Optional[float]): 最大阈值，None 表示不限制。

    返回:
        float: 在指定范围内的数值。"""

    # 优先应用最小值限制
    result = value
    if min_value is not None:
        result = max(result, float(min_value))
    # 再应用最大值限制
    if max_value is not None:
        result = min(result, float(max_value))
    return result


def _build_complications_for_patient(
    severity_config: config_def.Medical_Severity,
) -> Tuple[List[config_def.Medical_Complication], float]:
    """基于病情等级配置生成并发症组合

    参数:
        severity_config (config_def.Medical_Severity): 当前病情等级对应的配置。

    返回:
        Tuple[List[config_def.Medical_Complication], float]: 并发症列表与额外普通药需求。"""

    # 根据配置构建目标并发症等级计划
    plan: List[int] = []
    plan.extend([0] * int(severity_config.minor_complication_count))
    plan.extend([1] * int(severity_config.moderate_complication_count))
    plan.extend([2] * int(severity_config.severe_complication_count))
    if not plan:
        return [], 0.0

    complications: List[config_def.Medical_Complication] = []
    bonus_total = 0.0
    # 遍历分配结果，逐项匹配具体并发症
    for system_id, severity_list in _assign_complication_systems(plan, severity_config):
        used_part_ids: set[int] = set()
        for severity_level in severity_list:
            part_id = _pick_part_id(system_id, used_part_ids)
            if part_id is None:
                continue
            used_part_ids.add(part_id)
            complication = _pick_complication(system_id, part_id, severity_level)
            if complication is None:
                continue
            complications.append(complication)
            bonus_total += float(complication.normal_medicine_bonus)
    return complications, bonus_total


def _assign_complication_systems(
    plan: List[int],
    severity_config: config_def.Medical_Severity,
) -> List[Tuple[int, List[int]]]:
    """将计划中的各等级并发症分配到生理系统

    参数:
        plan (List[int]): 并发症严重度计划列表。
        severity_config (config_def.Medical_Severity): 对应病情等级的配置。

    返回:
        List[Tuple[int, List[int]]]: 系统 ID 与其包含的并发症严重度列表。

    当危重病人（中+双重）时会强制拆分两个系统，其余情况仅用单系统。"""

    if not plan:
        return []

    assignments: List[Tuple[int, List[int]]] = []
    # 判断是否触发危重病例拆分逻辑
    hazard_case = int(severity_config.severe_complication_count) >= 2 and int(
        severity_config.moderate_complication_count
    ) >= 1
    if hazard_case:
        # 危重病例需要至少两个系统
        system_a = _pick_system_id()
        if system_a is None:
            return []
        severity_for_a: List[int] = []
        severity_for_b: List[int] = []
        severe_assigned = 0
        moderate_assigned = 0
        for severity_level in plan:
            if severity_level == 1 and moderate_assigned < 1:
                severity_for_a.append(severity_level)
                moderate_assigned += 1
            elif severity_level == 2 and severe_assigned < 1:
                severity_for_a.append(severity_level)
                severe_assigned += 1
            elif severity_level == 2:
                severity_for_b.append(severity_level)
            else:
                severity_for_a.append(severity_level)
        if severity_for_b:
            system_b = _pick_system_id(exclude_ids={system_a}) or system_a
            assignments.append((system_a, severity_for_a))
            assignments.append((system_b, severity_for_b))
        else:
            assignments.append((system_a, severity_for_a))
        return assignments

    # 非危重病例直接选择单个系统承载全部并发症
    system_id = _pick_system_id()
    if system_id is None:
        return []
    assignments.append((system_id, plan))
    return assignments


def _pick_system_id(exclude_ids: Optional[Iterable[int]] = None) -> Optional[int]:
    """按 organ_priority 权重抽取一个系统 ID，可排除给定集合

    参数:
        exclude_ids (Optional[Iterable[int]]): 需要排除的系统 ID 集合。

    返回:
        Optional[int]: 选中的系统 ID，若无可选项则返回 None。"""

    # 构建排除集合并计算候选权重
    exclude_set = set(exclude_ids or [])
    candidates: Dict[int, int] = {}
    for system_id, part_map in game_config.config_medical_body_system_by_system.items():
        if system_id in exclude_set or not part_map:
            continue
        weight = sum(max(1, part.organ_priority) for part in part_map.values())
        if weight <= 0:
            weight = len(part_map)
        candidates[system_id] = int(max(weight, 1))
    if not candidates:
        return None
    # 基于权重随机挑选一个系统 ID
    return value_handle.get_random_for_weight(candidates)


def _pick_part_id(system_id: int, used_part_ids: Iterable[int]) -> Optional[int]:
    """在指定系统中抽取一个未被使用的部位 ID

    参数:
        system_id (int): 目标生理系统 ID。
        used_part_ids (Iterable[int]): 已被占用的部位 ID 列表。

    返回:
        Optional[int]: 可用部位 ID，若无可用部位则返回 None。"""

    # 读取系统下的部位映射
    part_map = game_config.config_medical_body_system_by_system.get(system_id)
    if not part_map:
        return None
    # 构建候选部位权重，排除已使用部位
    used_set = set(used_part_ids)
    candidates: Dict[int, int] = {}
    for part_id, part in part_map.items():
        if part_id in used_set:
            continue
        gender_limit = int(getattr(part, "gender_limit", 2))
        if gender_limit == 0:
            continue
        weight = max(1, part.organ_priority)
        candidates[part_id] = int(weight)
    if not candidates:
        return None
    # 基于权重随机选择部位 ID
    return value_handle.get_random_for_weight(candidates)


def _pick_complication(
    system_id: int,
    part_id: int,
    severity_level: int,
) -> Optional[config_def.Medical_Complication]:
    """在指定系统/部位/等级下随机挑选一条并发症

    参数:
        system_id (int): 生理系统 ID。
        part_id (int): 部位 ID。
        severity_level (int): 并发症严重度。

    返回:
        Optional[config_def.Medical_Complication]: 匹配到的并发症对象，无结果时返回 None。"""

    # 从配置中定位候选并发症列表
    part_map = game_config.config_medical_complication_detail.get(system_id, {}).get(part_id, {})
    candidates = part_map.get(severity_level, [])
    if not candidates:
        return None
    # 按权重随机选择具体并发症
    weights = [max(float(comp.weight), 0.01) for comp in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]


def _pick_patient_race_id() -> int:
    """从已有种族中（排除特殊种族）随机挑选患者种族

    参数:
        无

    返回:
        int: 选中的种族 ID，若无可选项返回 0。"""

    # 跳过不可选中的种族，不可选中id列表为[0,1,2,3,35,36,40,41,42,43,44]，然后随机挑选
    race_ids = [race_id for race_id in game_config.config_race.keys() if race_id not in {0, 1, 2, 3, 35, 40, 41, 42, 43, 44}]
    if not race_ids:
        return 0
    return random.choice(race_ids)

def _pick_price_config(price_ratio: float) -> List[float]:
    """根据收费系数计算刷新倍率与收入倍率

    参数:
        price_ratio (float): 当前收费系数。

    返回:
        List[float]: [刷新倍率, 收入倍率]，默认均为 1.0。"""

    # 以 1.0 为基准，计算与 1.0 的距离
    delta = price_ratio - 1.0

    # 刷新倍率：每相差 0.05，刷新修正乘以 1.08 或 0.92
    steps = int(abs(delta) / 0.05)
    refresh_multiplier = 1.0
    if delta > 0:
        for _ in range(steps):
            refresh_multiplier *= 0.92
    elif delta < 0:
        for _ in range(steps):
            refresh_multiplier *= 1.08

    # 收入倍率：每相差 0.05，收入修正乘以 1.05 或 0.95
    income_multiplier = 1.0
    if delta > 0:
        for _ in range(steps):
            income_multiplier *= 1.05
    elif delta < 0:
        for _ in range(steps):
            income_multiplier *= 0.95

    return [refresh_multiplier, income_multiplier]
