# -*- coding: UTF-8 -*-
"""门诊病人生成与倍率处理模块

负责门诊病人的生成、并发症组合以及价格倍率的工具函数，
供医疗系统其他模块复用。
"""
from __future__ import annotations

import math
import random
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from types import FunctionType

from Script.Config import config_def, game_config
from Script.Core import cache_control, game_type, get_text, value_handle
from Script.Design import handle_ability
from Script.System.Medical import medical_constant, medical_core

_: FunctionType = get_text._
""" 翻译函数 """


def create_patient_stub(severity_level: int, **extra_fields: Any) -> medical_constant.MedicalPatient:
    """创建尚未填充具体症状的病人结构。

    参数:
        severity_level (int): 生成病人的初始病情等级。
        **extra_fields (Any): 额外写入 `MedicalPatient` 构造器的字段。
    返回:
        medical_constant.MedicalPatient: 结构完整且已初始化药品键的病人对象。
    """

    # 构造病人基础数据结构并分配唯一 ID。
    patient = medical_constant.MedicalPatient(
        patient_id=next(medical_constant.PATIENT_ID_COUNTER),
        severity_level=severity_level,
        **extra_fields,
    )
    # 确保资源字段齐备，避免后续访问缺键。
    patient.ensure_resource_keys()
    return patient


def pick_severity_level(facility_level: Optional[int] = None) -> Optional[int]:
    """按权重抽取一个病情等级 ID。

    参数:
        facility_level (Optional[int]): 医疗设施等级，若提供则按解锁条件筛选病情档位。
    返回:
        Optional[int]: 抽取到的病情等级编号，若无可用档位返回 None。
    """

    # 配置表缺失时无法抽选病情等级。
    if not game_config.medical_severity_weight_table:
        return None

    def _is_unlocked(severity_id: int) -> bool:
        if facility_level is None:
            return True
        if severity_id == 3:
            return facility_level >= 5
        if severity_id == 2:
            return facility_level >= 3
        return True

    # 根据设施等级过滤可用病情档位。
    filtered_entries = [entry for entry in game_config.medical_severity_weight_table if _is_unlocked(entry[0])]
    if not filtered_entries:
        return None

    # 按权重随机抽样产生病情等级。
    total_weight = sum(weight for _, weight in filtered_entries)
    if total_weight <= 0:
        return filtered_entries[0][0]
    roll = random.uniform(0, total_weight)
    cursor = 0.0
    for severity_id, weight in filtered_entries:
        cursor += weight
        if roll <= cursor:
            return severity_id
    return filtered_entries[-1][0]


def generate_patient(
    severity_level: int,
    rhodes_island,
) -> Optional[medical_constant.MedicalPatient]:
    """生成单个门诊病人实体。

    参数:
        severity_level (int): 目标病情等级。
        rhodes_island: 当前基地对象，用于读取收费系数等字段。
    返回:
        Optional[medical_constant.MedicalPatient]: 成功生成的病人对象，配置缺失时返回 None。
    """

    # 读取目标病情配置，缺失时返回 None。
    severity_config = game_config.config_medical_severity.get(severity_level)
    if severity_config is None:
        return None

    # 构建基础病人信息并随机生成个体特征。
    patient = create_patient_stub(severity_level=severity_level)
    patient.personality_type = random.choice(list(medical_constant.MedicalPatientPersonality))
    patient.race_id = _pick_patient_race_id()
    patient.age = random.randint(10, 60)

    # 依据病情配置生成并发症，并记录追踪信息。
    complications, medicine_bonus = _build_complications_for_patient(severity_config)
    patient.complications = [comp.cid for comp in complications]
    if complications:
        patient.complication_trace = [
            {
                "cid": comp.cid,
                "system_id": comp.system_id,
                "part_id": comp.part_id,
                "severity_level": comp.severity_level,
            }
            for comp in complications
        ]
    patient.need_surgery = any(comp.requires_surgery == 1 for comp in complications)

    # 计算普通药需求量，并叠加并发症额外需求。
    normal_resource_id = medical_constant.MedicalMedicineResource.NORMAL.value
    base_normal_need = random.uniform(
        float(severity_config.normal_medicine_min),
        float(max(severity_config.normal_medicine_max, severity_config.normal_medicine_min)),
    )
    patient.need_resources[normal_resource_id] = max(base_normal_need + medicine_bonus, 0.0)

    # 叠加特殊药品模板中的固定需求。
    special_template = game_config.medical_severity_special_medicine.get(severity_level, {})
    for resource_id, amount in special_template.items():
        patient.need_resources[resource_id] = patient.need_resources.get(resource_id, 0.0) + float(amount)

    # 记录病情标签与当前收费系数，便于后续展示。
    if not patient.severity_name:
        patient.severity_name = severity_config.name
    patient.price_ratio = float(getattr(rhodes_island, "medical_price_ratio", 1.0) or 1.0)
    return patient

def _build_complications_for_patient(
    severity_config: config_def.Medical_Severity,
) -> Tuple[List[config_def.Medical_Complication], float]:
    """基于病情等级配置生成并发症组合。

    参数:
        severity_config (config_def.Medical_Severity): 目标病情等级的配置。
    返回:
        Tuple[List[config_def.Medical_Complication], float]:
            并发症列表以及普通药需求的额外加成总量。
    """

    # 构建计划列表，0/1/2 分别代表轻/中/重并发症。
    plan: List[int] = []
    plan.extend([0] * int(severity_config.minor_complication_count))
    plan.extend([1] * int(severity_config.moderate_complication_count))
    plan.extend([2] * int(severity_config.severe_complication_count))
    if not plan:
        return [], 0.0

    # 逐条生成并发症，同时累加普通药额外需求。
    complications: List[config_def.Medical_Complication] = []
    bonus_total = 0.0
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
    """将计划中的各等级并发症分配到生理系统。

    参数:
        plan (List[int]): 包含轻/中/重等级标记的并发症计划。
        severity_config (config_def.Medical_Severity): 当前病情配置，用于危重逻辑判断。
    返回:
        List[Tuple[int, List[int]]]: 每项为系统 ID 与对应并发症等级列表。
    """

    # 没有计划数据时直接返回空列表。
    if not plan:
        return []

    # 危重情况需要将并发症拆分到两个系统中处理。
    assignments: List[Tuple[int, List[int]]] = []
    hazard_case = int(severity_config.severe_complication_count) >= 2 and int(
        severity_config.moderate_complication_count
    ) >= 1
    if hazard_case:
        system_a = _pick_system_id()
        if system_a is None:
            return []
        severity_for_a: List[int] = []
        severity_for_b: List[int] = []
        severe_assigned = 0
        moderate_assigned = 0
        for severity_level in plan:
            # 尝试将至少一条中症和重症绑定到系统 A。
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

    # 普通情况直接全部绑定到单一系统。
    system_id = _pick_system_id()
    if system_id is None:
        return []
    assignments.append((system_id, plan))
    return assignments


def _pick_system_id(exclude_ids: Optional[Iterable[int]] = None) -> Optional[int]:
    """按 organ_priority 权重抽取一个系统 ID，可排除给定集合。

    参数:
        exclude_ids (Optional[Iterable[int]]): 不参与抽取的系统编号集合。
    返回:
        Optional[int]: 抽取到的系统 ID，失败时返回 None。
    """

    # 将需排除的系统整理成集合并构建候选权重表。
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
    return value_handle.get_random_for_weight(candidates)


def _pick_part_id(system_id: int, used_part_ids: Iterable[int]) -> Optional[int]:
    """在指定系统中抽取一个未被使用的部位 ID。

    参数:
        system_id (int): 目标生理系统编号。
        used_part_ids (Iterable[int]): 已使用的部位集合。
    返回:
        Optional[int]: 可用的部位 ID，若无则返回 None。
    """

    # 读取系统下的全部部位配置。
    part_map = game_config.config_medical_body_system_by_system.get(system_id)
    if not part_map:
        return None
    used_set = set(used_part_ids)
    candidates: Dict[int, int] = {}
    for part_id, part in part_map.items():
        if part_id in used_set:
            continue
        gender_limit = int(getattr(part, "gender_limit", 2))
        if gender_limit == 0:
            continue
        # 以器官优先级作为抽取权重。
        weight = max(1, part.organ_priority)
        candidates[part_id] = int(weight)
    if not candidates:
        return None
    return value_handle.get_random_for_weight(candidates)


def _pick_complication(
    system_id: int,
    part_id: int,
    severity_level: int,
) -> Optional[config_def.Medical_Complication]:
    """在指定系统/部位/等级下随机挑选一条并发症。

    参数:
        system_id (int): 生理系统编号。
        part_id (int): 部位编号。
        severity_level (int): 并发症等级。
    返回:
        Optional[config_def.Medical_Complication]: 抽取到的并发症配置。
    """

    # 从配置中取出指定系统与部位下的并发症列表。
    part_map = game_config.config_medical_complication_detail.get(system_id, {}).get(part_id, {})
    candidates = part_map.get(severity_level, [])
    if not candidates:
        return None
    # 按权重随机挑选一条并发症配置。
    weights = [max(float(comp.weight), 0.01) for comp in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]


def _pick_patient_race_id() -> int:
    """从已有种族中（排除特殊种族）随机挑选患者种族。

    返回:
        int: 选中的种族 ID，找不到候选时回退 0。
    """

    # 过滤掉特殊种族，保留常规种族编号。
    race_ids = [
        race_id
        for race_id in game_config.config_race.keys()
        if race_id not in {0, 1, 2, 3, 35, 40, 41, 42, 43, 44}
    ]
    if not race_ids:
        return 0
    return random.choice(race_ids)


def _resolve_patient_system_keys(patient: medical_constant.MedicalPatient) -> Set[str]:
    """提取病人可能关联的系统键。

    参数:
        patient (medical_constant.MedicalPatient): 目标病人对象。
    返回:
        Set[str]: 记录病人关联生理系统的字符串集合。
    """

    system_keys: Set[str] = set()
    if patient is None:
        return system_keys

    trace = patient.complication_trace or []
    for entry in trace:
        system_id = entry.get("system_id") if isinstance(entry, dict) else None
        if system_id is not None:
            system_keys.add(str(system_id))

    if not system_keys and getattr(patient, "complications", None):
        for comp_id in patient.complications:
            comp = game_config.config_medical_complication.get(comp_id)
            if comp is not None:
                system_keys.add(str(comp.system_id))

    if system_keys:
        patient.system_keys = sorted(system_keys)
    else:
        patient.system_keys = []
    return system_keys


def _resolve_triage_mode(
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> medical_constant.MedicalPatientPriority:
    """解析基地当前的病人接诊优先策略。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        medical_constant.MedicalPatientPriority: 当前接诊优先策略枚举。
    """

    # 缺少基地上下文时使用默认策略。
    if rhodes_island is None:
        return medical_constant.MedicalPatientPriority.NORMAL
    raw_mode = getattr(
        rhodes_island,
        "medical_patient_priority_mode",
        medical_constant.MedicalPatientPriority.NORMAL.value,
    )
    try:
        # 尝试将缓存值解析成合法枚举。
        mode = medical_constant.MedicalPatientPriority(str(raw_mode))
    except ValueError:
        # 解析失败时写入默认值并返回普通模式。
        rhodes_island.medical_patient_priority_mode = medical_constant.MedicalPatientPriority.NORMAL.value
        return medical_constant.MedicalPatientPriority.NORMAL
    # 将解析结果写回缓存以保持数据一致。
    rhodes_island.medical_patient_priority_mode = mode.value
    return mode


def select_triage_candidate(
    candidates: List[medical_constant.MedicalPatient],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> Optional[medical_constant.MedicalPatient]:
    """在候选病人中挑选最优对象。

    参数:
        candidates (List[medical_constant.MedicalPatient]): 病人候选列表。
        rhodes_island (Optional[game_type.Rhodes_Island]): 目标基地对象，用于读取优先策略。
    返回:
        Optional[medical_constant.MedicalPatient]: 挑选出的病人，若无候选返回 None。
    """

    # 没有候选病人时直接返回。
    if not candidates:
        return None

    # 根据当前优先策略决定筛选规则，并优先处理默认分诊逻辑
    mode = _resolve_triage_mode(rhodes_island)

    # 默认策略：若存在危重病人则立即返回，否则按照刷新顺序先来后到
    if mode == medical_constant.MedicalPatientPriority.NORMAL:
        for target in candidates:
            severity_level = int(getattr(target, "severity_level", 0) or 0)
            if severity_level == medical_constant.CRITICAL_SEVERITY_LEVEL:
                return target
        return candidates[0]

    # 轻症优先策略：继续按严重度升序、诊疗进度与编号排序
    if mode == medical_constant.MedicalPatientPriority.FOCUS_MILD:
        key_func = lambda target: (
            int(getattr(target, "severity_level", 0) or 0),
            float(getattr(target, "diagnose_progress", 0.0) or 0.0),
            target.patient_id,
        )
        return min(candidates, key=key_func)

    # 其他策略（默认兼容重症优先）继续采用严重度降序的旧排序逻辑
    key_func = lambda target: (
        -int(getattr(target, "severity_level", 0) or 0),
        -float(getattr(target, "diagnose_progress", 0.0) or 0.0),
        target.patient_id,
    )
    return min(candidates, key=key_func)

def estimate_patient_diagnose_income(
    patient: Optional[medical_constant.MedicalPatient],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> int:
    """
    估算指定病人的诊疗阶段收益（不含药费）。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 目标病人对象。
        target_base (Optional[game_type.Rhodes_Island]): 指定罗德岛基座，用于倍率读取。
    返回:
        int: 诊疗阶段的预期收入，若缺失返回 0。
    """
    # 缺少病人对象时直接返回失败结果
    if patient is None:
        return 0
    # 解析罗德岛对象并获取病情配置
    rhodes_island = medical_core._get_rhodes_island(target_base)
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return 0
    # 读取收费倍率与收入加成后计算诊疗收入，收入会加上玩家检查的次数乘以病情等级
    price_ratio = get_medical_price_ratio(target_base=rhodes_island)
    income_multiplier = medical_core.resolve_price_income_multiplier(price_ratio)
    diagnose_income = severity_config.diagnose_income + patient.player_used_checks * 1000 * patient.severity_level
    diagnose_income = int(round(float(diagnose_income or 0) * income_multiplier))
    # 确保返回非负值
    return max(diagnose_income, 0)

def advance_diagnose(
    patient_id: int,
    doctor_character: game_type.Character,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """推进病人的诊疗进度并在完成时发放诊疗收入。

    参数:
        patient_id (int): 门诊病人的唯一编号。
        doctor_character (game_type.Character): 执行诊疗的医生角色。
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所在的基地实例。
    返回:
        None
    """
    # 没有医生对象时无法推进诊疗
    if doctor_character is None:
        return

    # 定位罗德岛实例，缺失时直接退出
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    # 查找病人信息，并确认是否仍属于门诊流程
    patient, hospitalized = medical_core._locate_patient(patient_id, rhodes_island)
    if patient is None or hospitalized:
        return

    # 将医生与当前病人绑定，便于后续查询
    if hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = patient.patient_id

    # 检查病人状态是否仍需要诊疗，若已进入后续流程则解除绑定
    if patient.state in (
        medical_constant.MedicalPatientState.WAITING_MEDICATION,
        medical_constant.MedicalPatientState.MEDICINE_GRANTED,
        medical_constant.MedicalPatientState.HOSPITALIZED,
        medical_constant.MedicalPatientState.DISCHARGED,
    ):
        # 病人已不在诊疗队列中，解除医生绑定后直接返回
        if getattr(patient, "assigned_doctor_id", 0) == doctor_character.cid:
            patient.assigned_doctor_id = 0
        # 解除医生与病人绑定
        if hasattr(doctor_character, "work"):
            doctor_character.work.medical_patient_id = 0
        medical_core._sync_legacy_patient_counters(rhodes_island)
        return

    # 读取病情配置，若缺失则终止诊疗并清理状态
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        if hasattr(doctor_character, "work"):
            doctor_character.work.medical_patient_id = 0
        patient.assigned_doctor_id = 0
        medical_core._sync_legacy_patient_counters(rhodes_island)
        return

    # 根据配置计算所需诊疗时长，并在异常时直接转入结算阶段
    base_hours = float(severity_config.base_hours)
    if base_hours <= 0:
        finalize_patient_after_diagnose(patient, target_base=rhodes_island)

    # 依据医生能力计算单次推进的进度值
    ability_level = doctor_character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0)
    ability_adjust = float(handle_ability.get_ability_adjust(ability_level))
    progress_increment = max(ability_adjust, 0.25)

    # 写入病人元数据并累加诊疗进度
    patient.assigned_doctor_id = doctor_character.cid
    set_patient_state(patient, medical_constant.MedicalPatientState.IN_TREATMENT)
    patient.diagnose_progress = min(patient.diagnose_progress + progress_increment, base_hours)

    # 诊疗尚未完成时仅同步计数并等待下一次推进
    if patient.diagnose_progress < base_hours:
        medical_core._sync_legacy_patient_counters(rhodes_island)
        return

    # 调用诊疗完成后的结算逻辑
    finalize_patient_after_diagnose(patient, target_base=rhodes_island)

def finalize_patient_after_diagnose(
    patient: medical_constant.MedicalPatient,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """
    病人诊疗完成后的结算处理，包括收入、状态、住院与药物结算。

    参数:
        patient (medical_constant.MedicalPatient): 已完成诊疗的病人对象。
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所属基地。
    返回:
        Dict[str, object]: 包含结算结果、收入、住院与药物处理信息。
    """
    from Script.System.Medical import medical_service

    # 校验对象
    if patient is None:
        return {"success": False, "reason": "no_patient"}

    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return {"success": False, "reason": "no_severity_config"}

    # 病人诊疗进度推进到完成状态
    base_hours = float(severity_config.base_hours)
    patient.diagnose_progress = base_hours

    # 记录诊疗完成统计，区分门诊总量与细分来源
    medical_core._bump_daily_counter(rhodes_island, "diagnose_completed_outpatient", 1)

    # 解除医生与病人绑定
    doctor_chara_id = patient.assigned_doctor_id
    doctor_character_data = cache_control.cache.character_data[doctor_chara_id]
    doctor_character_data.work.medical_patient_id = 0
    patient.assigned_doctor_id = 0

    # 诊疗收入结算
    diagnose_income = estimate_patient_diagnose_income(patient, target_base=rhodes_island)
    if diagnose_income > 0:
        rhodes_island.medical_income_today += diagnose_income
        rhodes_island.medical_income_total += diagnose_income
        rhodes_island.all_income += diagnose_income
        rhodes_island.materials_resouce[1] = rhodes_island.materials_resouce.get(1, 0) + diagnose_income

    # 统计治愈人数
    rhodes_island.patient_cured = int(getattr(rhodes_island, "patient_cured", 0) or 0) + 1
    rhodes_island.patient_cured_all = int(getattr(rhodes_island, "patient_cured_all", 0) or 0) + 1

    # 判断是否需要住院
    hospitalized_success = False
    if getattr(severity_config, "require_hospitalization", 0) == 1:
        hospitalized_success = medical_service.try_hospitalize(patient.patient_id, target_base=rhodes_island)

    # 药物结算（仅门诊流程且未住院时）
    medicine_income = 0
    medicine_success = False
    if not hospitalized_success:
        medicine_success = medical_service.try_consume_medicine(patient, target_base=rhodes_island)

    # 更新病人状态，优先级：住院 > 发药成功 > 等待用药
    if hospitalized_success:
        set_patient_state(patient, medical_constant.MedicalPatientState.HOSPITALIZED)
    elif medicine_success:
        set_patient_state(patient, medical_constant.MedicalPatientState.MEDICINE_GRANTED)
    else:
        set_patient_state(patient, medical_constant.MedicalPatientState.WAITING_MEDICATION)

    # 同步统计字段
    medical_core._sync_legacy_patient_counters(rhodes_island)

    return {
        "success": True,
        "patient_id": patient.patient_id,
        "diagnose_income": diagnose_income,
        "medicine_income": medicine_income,
        "hospitalized": hospitalized_success,
        "medicine_success": medicine_success,
        "state": patient.state.value,
    }

def set_patient_state(
    patient: medical_constant.MedicalPatient,
    state: medical_constant.MedicalPatientState,
) -> None:
    """更新病人的流程状态，并写入标签方便调试。

    参数:
        patient (medical_constant.MedicalPatient): 需要更新状态的病人。
        state (medical_constant.MedicalPatientState): 新的流程状态枚举值。
    返回:
        None
    """

    # 保护性判断，避免空对象写入。
    if patient is None:
        return
    patient.state = state
    patient.state_label = state.value


def get_patient_table(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
    hospitalized: bool,
) -> Dict[int, medical_constant.MedicalPatient]:
    """获取指定状态下的病人表引用。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定基地实例。
        hospitalized (bool): 是否读取住院病人表，False 返回门诊病人表。
    返回:
        Dict[int, medical_constant.MedicalPatient]: 病人 ID 到病人对象的映射。
    """

    # 根据 base 标记返回对应的病人表。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return {}
    return rhodes_island.medical_hospitalized if hospitalized else rhodes_island.medical_patients_today


def get_medical_price_ratio(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> float:
    """读取当前医疗部收费系数，若未初始化则返回默认值。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所在基地。
    返回:
        float: 当前收费系数。
    """

    # 解析收费系数，必要时写入默认值。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return medical_core._resolve_default_price_ratio()
    ratio = float(rhodes_island.medical_price_ratio or 0)
    if ratio <= 0:
        ratio = medical_core._resolve_default_price_ratio()
        rhodes_island.medical_price_ratio = ratio
    return ratio


def set_medical_price_ratio(
    price_ratio: float,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """更新医疗部收费系数，并重新评估床位上限。

    参数:
        price_ratio (float): 新的收费倍率。
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所属基地。
    返回:
        None
    """

    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    # 更新收费系数后重新计算床位上限。
    rhodes_island.medical_price_ratio = max(float(price_ratio), 0.1)
    rhodes_island.medical_bed_limit = medical_core._calculate_medical_bed_limit(rhodes_island)


def get_patient_priority_mode(
    *, target_base: Optional[game_type.Rhodes_Island] = None
) -> medical_constant.MedicalPatientPriority:
    """读取当前病人接诊优先策略，若缺失则回退为默认值。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所属基地。
    返回:
        medical_constant.MedicalPatientPriority: 当前生效的接诊优先级枚举。
    """

    # 读取优先策略，若缺失则保持默认值。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    return _resolve_triage_mode(rhodes_island)


def set_patient_priority_mode(
    priority_mode: str | medical_constant.MedicalPatientPriority,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> medical_constant.MedicalPatientPriority:
    """更新病人接诊优先策略并返回实际生效的枚举值。

    参数:
        priority_mode (str | medical_constant.MedicalPatientPriority): 用户输入的优先策略。
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所属基地。
    返回:
        medical_constant.MedicalPatientPriority: 生效后的接诊优先策略。
    """

    default_mode = medical_constant.MedicalPatientPriority.NORMAL
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return default_mode

    if isinstance(priority_mode, medical_constant.MedicalPatientPriority):
        resolved = priority_mode
    else:
        try:
            resolved = medical_constant.MedicalPatientPriority(str(priority_mode))
        except ValueError:
            resolved = default_mode

    rhodes_island.medical_patient_priority_mode = resolved.value
    return resolved


def predict_medical_patient_refresh(
    price_ratio: Optional[float] = None,
    level: Optional[int] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, float]:
    """预测在指定收费系数下的病人刷新数量与倍率。

    参数:
        price_ratio (Optional[float]): 自定义收费倍率，默认读取基地当前值。
        level (Optional[int]): 医疗部等级，默认读取基地配置。
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所属基地。
    返回:
        Dict[str, float]: 包含倍率、基数与预测刷新数量的摘要。
    """

    # 解析 base 对象，缺失时返回默认预测。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        resolved_ratio = float(price_ratio if price_ratio is not None else 1.0)
        return {
            "price_ratio": resolved_ratio,
            "base_count": 0.0,
            "penalty": 1.0,
            "refresh_multiplier": 1.0,
            "income_multiplier": medical_core.resolve_price_income_multiplier(resolved_ratio),
            "predicted_count": 0.0,
        }

    # 决定使用的收费系数与医疗部等级。
    resolved_ratio = float(price_ratio if price_ratio is not None else get_medical_price_ratio(target_base=rhodes_island))
    resolved_level = int(level if level is not None else medical_core._get_medical_facility_level(rhodes_island))
    level_config = medical_core._pick_hospital_level_config(resolved_level)

    # 计算基础数量与倍率，求得最终预测值。
    base_count = float(getattr(level_config, "daily_patient_base", 0) or 0)
    safe_ratio = max(resolved_ratio, 0.01)
    penalty = 1.0 / safe_ratio
    if level_config:
        penalty = medical_core.clamp(penalty, level_config.ratio_min, level_config.ratio_max)

    refresh_multiplier = medical_core.resolve_price_refresh_multiplier(resolved_ratio)
    predicted_value = base_count * penalty * refresh_multiplier
    predicted_count = max(int(math.floor(predicted_value)), 0)
    income_multiplier = medical_core.resolve_price_income_multiplier(resolved_ratio)

    return {
        "price_ratio": resolved_ratio,
        "base_count": base_count,
        "penalty": penalty,
        "refresh_multiplier": refresh_multiplier,
        "income_multiplier": income_multiplier,
        "predicted_count": float(predicted_count),
    }


def refresh_medical_patients(
    level: Optional[int] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[medical_constant.MedicalPatient]:
    """根据医疗部等级刷新当日病人列表。

    参数:
        level (Optional[int]): 指定使用的医疗部等级，缺省时读取基地等级。
        target_base (Optional[game_type.Rhodes_Island]): 指定医疗部所属基地。
    返回:
        List[medical_constant.MedicalPatient]: 新生成的病人列表。
    """

    # 若无法获取基地对象则直接返回空结果。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return []

    # 判定使用的医疗部等级并获取对应配置。
    level_value = level if level is not None else medical_core._get_medical_facility_level(rhodes_island)
    level_config = medical_core._pick_hospital_level_config(level_value)
    if level_config is None:
        return []

    # 依据配置与收费系数计算需要刷新的病人数量。
    refresh_count = medical_core._calculate_patient_refresh_count(rhodes_island, level_config)
    if refresh_count <= 0:
        return []

    # 循环生成病人并登记到门诊病人表。
    new_patients: List[medical_constant.MedicalPatient] = []
    patient_table = get_patient_table(target_base=rhodes_island, hospitalized=False)

    for _ in range(refresh_count):
        severity_level = pick_severity_level(level_value)
        if severity_level is None:
            break
        patient = generate_patient(severity_level, rhodes_island)
        if patient is None:
            continue
        patient_table[patient.patient_id] = patient
        new_patients.append(patient)

    # 最后同步旧统计字段，保持 UI 数据一致。
    medical_core._sync_legacy_patient_counters(rhodes_island)
    return new_patients
