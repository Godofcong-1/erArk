# -*- coding: UTF-8 -*-
"""住院医生相关逻辑模块

提供住院医生查房、手术等行为所需的工具函数，
并向门诊医生模块暴露住院患者分配能力。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, List

from Script.Config import game_config
from Script.Core import cache_control, game_type
from Script.Design import handle_ability
from Script.System.Medical import medical_constant, medical_core, medical_service


@dataclass
class SurgeryPrecheckResult:
    """手术前置条件检查结果结构体。"""

    can_execute: bool
    """是否满足执行条件"""

    reason: str = "unknown"
    """无法执行时的原因标签"""

    resource_usage: Dict[int, int] = field(default_factory=dict)
    """本次手术预计消耗的药品资源，key 为资源 ID，value 为整数单位"""

    severity_config: Optional[Any] = None
    """当前病情等级的配置对象，用于后续计算"""

    doctor_level: int = 0
    """执刀医生的医疗能力等级"""

    ability_requirement: int = 0
    """手术要求的最低医疗能力等级"""

    details: Dict[str, Any] = field(default_factory=dict)
    """补充信息字典，例如缺药明细"""


def _acquire_hospital_patient_for_doctor(
    doctor_character: Optional[game_type.Character],
    rhodes_island: Optional[game_type.Rhodes_Island],
    *,
    require_surgery: bool = False,
) -> Optional[medical_constant.MedicalPatient]:
    """选择并返回一个符合条件的住院病人。

    参数:
        doctor_character (Optional[game_type.Character]): 申请病人的医生角色，若为空直接失败。
        rhodes_island (Optional[game_type.Rhodes_Island]): 医疗部归属的罗德岛基座。
        require_surgery (bool): 是否仅筛选需要手术的病人。
    返回:
        Optional[medical_constant.MedicalPatient]: 成功分配到的病人，否则为 None。
    """

    # 医生或基地不存在时无法分配病人。
    if doctor_character is None or rhodes_island is None:
        return None

    # 读取当前住院病人列表。
    patient_table = rhodes_island.medical_hospitalized
    if not patient_table:
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0
        return None

    # 优先检查医生是否已有绑定病人。
    work_data = getattr(doctor_character, "work", None)
    assigned_id = getattr(work_data, "medical_patient_id", 0) if work_data is not None else 0
    if assigned_id:
        patient = patient_table.get(assigned_id)
        if (
            patient
            and patient.state == medical_constant.MedicalPatientState.HOSPITALIZED
            and (not require_surgery or (patient.need_surgery and not patient.surgery_blocked))
        ):
            patient.assigned_hospital_doctor_id = doctor_character.cid
            return patient
        if work_data is not None:
            work_data.medical_patient_id = 0

    # 遍历住院列表，筛选符合条件的病人候选。
    candidates = []
    for patient in patient_table.values():
        if patient.state != medical_constant.MedicalPatientState.HOSPITALIZED:
            continue
        if require_surgery and (not patient.need_surgery or patient.surgery_blocked):
            continue
        assigned = int(getattr(patient, "assigned_hospital_doctor_id", 0) or 0)
        if assigned and assigned != doctor_character.cid:
            continue
        candidates.append(patient)

    # 没有满足条件的病人时清理绑定。
    if not candidates:
        if work_data is not None:
            work_data.medical_patient_id = 0
        return None

    def _hospital_priority(target: medical_constant.MedicalPatient) -> Tuple[int, int, int]:
        return (
            -int(getattr(target, "severity_level", 0) or 0),
            -int(getattr(target, "stay_days", 0) or 0),
            target.patient_id,
        )

    # 选择优先级最高的病人并记录绑定关系。
    patient = min(candidates, key=_hospital_priority)
    patient.assigned_hospital_doctor_id = doctor_character.cid
    if work_data is not None:
        work_data.medical_patient_id = patient.patient_id
    return patient


def evaluate_surgery_preconditions(
    patient: Optional[medical_constant.MedicalPatient],
    doctor_character: Optional[game_type.Character],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> SurgeryPrecheckResult:
    """判断指定医生是否可以为病人执行手术并给出资源需求。"""

    # 基地、医生或病人不存在时直接返回失败
    if patient is None or doctor_character is None or rhodes_island is None:
        return SurgeryPrecheckResult(False, "no_context")

    # 不需要手术或手术被阻塞时无法执行
    if not patient.need_surgery or patient.surgery_blocked:
        return SurgeryPrecheckResult(False, "not_required")

    # 读取病情配置，缺失时无法执行
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return SurgeryPrecheckResult(False, "missing_config")

    # 检查医生能力是否满足当前病情的最低要求
    ability_requirement = medical_constant.SURGERY_ABILITY_REQUIREMENT.get(patient.severity_level, 4)
    doctor_level = int(doctor_character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0))
    # 能力不足时返回失败
    if doctor_level < ability_requirement:
        return SurgeryPrecheckResult(
            False,
            "ability_insufficient",
            severity_config=severity_config,
            doctor_level=doctor_level,
            ability_requirement=ability_requirement,
        )

    # 解析手术所需资源并检查库存是否充足
    resource_plan = medical_service.resolve_surgery_requirements(severity_config)
    inventory = getattr(rhodes_island, "materials_resouce", {}) or {}
    resource_usage: Dict[int, int] = {}

    for resource_id, amount in resource_plan.items():
        units = int(math.ceil(max(float(amount), 0.0) - medical_constant.FLOAT_EPSILON))
        if units <= 0:
            continue
        stock = int(inventory.get(resource_id, 0) or 0)
        # 库存不足时返回失败
        if stock < units:
            return SurgeryPrecheckResult(
                False,
                "resource_shortage",
                severity_config=severity_config,
                doctor_level=doctor_level,
                ability_requirement=ability_requirement,
                details={"resource_id": resource_id, "need": units, "stock": stock},
            )
        resource_usage[resource_id] = units

    return SurgeryPrecheckResult(
        True,
        "ok",
        resource_usage=resource_usage,
        severity_config=severity_config,
        doctor_level=doctor_level,
        ability_requirement=ability_requirement,
    )


def consume_surgery_resources(
    patient: Optional[medical_constant.MedicalPatient],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> bool:
    """直接扣除病人执行手术所需的药品资源。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 需要执行手术的住院病人对象。
        rhodes_island (Optional[game_type.Rhodes_Island]): 当前所属的罗德岛基地数据。
    返回:
        bool: 药品资源扣除是否完成，True 表示已成功扣除。
    """

    # 校验上下文是否完整，缺失任意一方时无法扣除药品。
    if patient is None or rhodes_island is None:
        return False

    # 读取病情对应的配置对象，缺失配置视为无法执行手术。
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        patient.surgery_blocked = True
        patient.surgery_blocked_resource = None
        return False

    # 准备库存引用并确保病人用药记录容器存在，避免后续写入报错。
    inventory = getattr(rhodes_island, "materials_resouce", None)
    if not isinstance(inventory, dict):
        patient.surgery_blocked = True
        patient.surgery_blocked_resource = None
        return False
    if not isinstance(patient.medicine_consumed_units, dict):
        patient.medicine_consumed_units = {}
    if not isinstance(patient.last_consumed_units, dict):
        patient.last_consumed_units = {}

    # 解析手术药品清单，并逐项确认库存是否充足。
    resource_plan = medical_service.resolve_surgery_requirements(severity_config)
    resource_usage: Dict[int, int] = {}
    for resource_id, amount in resource_plan.items():
        units = int(math.ceil(max(float(amount), 0.0) - medical_constant.FLOAT_EPSILON))
        if units <= 0:
            continue
        stock = int(inventory.get(resource_id, 0) or 0)
        if stock < units:
            patient.surgery_blocked = True
            patient.surgery_blocked_resource = resource_id
            return False
        resource_usage[resource_id] = units

    # 遍历消耗计划，扣减库存并写入病人历史用药记录。
    consumed_total = 0
    for resource_id, units in resource_usage.items():
        current_stock = int(inventory.get(resource_id, 0) or 0)
        inventory[resource_id] = current_stock - units
        consumed_total += units
        patient.medicine_consumed_units[resource_id] = int(
            patient.medicine_consumed_units.get(resource_id, 0) or 0
        ) + units
        patient.last_consumed_units[resource_id] = units

    # 写入统计计数并清除阻塞标记，方便后续正常执行手术。
    if consumed_total:
        # --- 将手术阶段的药剂明细纳入当日统计，支持后续日志明细展示 ---
        medical_core._bump_daily_counter(rhodes_island, "medicine_consumed", resource_usage)

    patient.surgery_blocked = False
    patient.surgery_blocked_resource = None
    return True

def get_surgery_candidate_patient_ids(
    doctor_character: game_type.Character,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[medical_constant.MedicalPatient]:
    """
    返回指定医生角色所有可以进行手术的住院病人ID列表。

    参数:
        doctor_character: game_type.Character: 指定医生角色对象。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地实例，默认读取全局缓存。
    返回:
        List[medical_constant.MedicalPatient]: 符合条件的住院病人列表。
    """
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None or not hasattr(rhodes_island, "medical_hospitalized"):
        return []

    # 获取住院患者列表
    hospitalized = getattr(rhodes_island, "medical_hospitalized", {}) or {}
    if not hospitalized:
        return []

    # 遍历患者列表，检查是否有满足条件的患者
    result = []
    for patient in hospitalized.values():
        if getattr(patient, "state", None) != medical_constant.MedicalPatientState.HOSPITALIZED:
            continue
        if not getattr(patient, "need_surgery", False):
            continue
        if getattr(patient, "surgery_blocked", False):
            continue
        # 检查是否指定了医生
        assigned_doctor = int(getattr(patient, "assigned_hospital_doctor_id", 0) or 0)
        if assigned_doctor and assigned_doctor != doctor_character:
            continue

        # 进行完整的手术前置条件检查
        precheck = evaluate_surgery_preconditions(patient, doctor_character, rhodes_island)
        if not precheck.can_execute:
            continue
        result.append(patient)
    return result

def conduct_ward_round(
    doctor_character: Optional[game_type.Character],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """执行住院部查房流程。

    参数:
        doctor_character (Optional[game_type.Character]): 前来查房的医生角色。
        target_base (Optional[game_type.Rhodes_Island]): 指定查房所在的基地实例。
    返回:
        Dict[str, object]: 查房结果，包含是否处理成功及对应病人信息。
    """

    # 获取执行查房的基地。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if doctor_character is None or rhodes_island is None:
        return {"handled": False, "patient": None, "result": "no_doctor"}

    # 尝试为医生分配一个无需手术的住院病人。
    patient = _acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=False)
    if patient is None:
        work_data = doctor_character.work
        if work_data is not None:
            work_data.medical_patient_id = 0
        return {"handled": False, "patient": None, "result": "no_candidate"}

    def _consume(target_patient: medical_constant.MedicalPatient) -> bool:
        from Script.System.Medical import medical_service

        return medical_service.try_consume_medicine(
            target_patient, is_hospitalized=True, target_base=rhodes_island
        )

    # 执行单名病人的巡诊逻辑。
    outcome = medical_service.process_single_hospitalized_patient(
        rhodes_island,
        patient,
        _consume,
        doctor=doctor_character,
    )
    outcome["patient"] = patient

    # 病人离开住院状态时解除医生绑定。
    if patient.state != medical_constant.MedicalPatientState.HOSPITALIZED:
        patient.assigned_hospital_doctor_id = 0
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0

    medical_core._sync_legacy_patient_counters(rhodes_island)
    return outcome

def attempt_surgery(
    patient_id: int,
    doctor_character: game_type.Character,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """按病人 ID 结算一次手术结果。

    参数:
        patient_id (int): 住院病人的唯一编号。
        doctor_character (game_type.Character): 尝试手术的医生角色。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地上下文，默认读取全局缓存。
    返回:
        bool: 手术是否顺利完成。
    """

    # 无医生对象时无法完成结算。
    if doctor_character is None:
        return False

    # 定位当前基地。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    # 查找病人并确认其仍在住院区。
    patient, hospitalized = medical_core._locate_patient(patient_id, rhodes_island)
    if patient is None or not hospitalized:
        return False

    # 直接进入手术结算流程，由调用方确保前置条件已经满足。
    return _attempt_surgery_on_patient(rhodes_island, patient, doctor_character)


def _attempt_surgery_on_patient(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    doctor: game_type.Character,
) -> bool:
    """结算住院病人的手术结果并更新病人状态。

    参数:
        rhodes_island (game_type.Rhodes_Island): 执行手术的罗德岛基地实例。
        patient (medical_constant.MedicalPatient): 正在接受手术的住院病人对象。
        doctor (game_type.Character): 执刀的医生角色数据。
    返回:
        bool: 手术是否完成结算。
    """

    # 校验手术使用的病情配置，缺失时无法继续结算。
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        patient.last_surgery_result = "missing_config"
        return False

    # 计算医生能力带来的倍率，用于后续收益结算。
    doctor_ability_level = int(doctor.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = medical_core.resolve_price_income_multiplier(price_ratio)
    doctor_adjust = float(handle_ability.get_ability_adjust(doctor_ability_level))

    # 根据病情配置计算本次手术的收入值。
    base_income = float(severity_config.diagnose_income)
    surgery_income_ratio = float(severity_config.hospital_success_income_ratio or 1.0)
    surgery_income = base_income * surgery_income_ratio * doctor_adjust * price_ratio * income_multiplier
    income_value = int(round(surgery_income))

    # 在成功路径下重置病人手术阻塞标记，并准备更新病情等级。
    severity_before = patient.severity_level
    new_severity = patient.severity_level - 1
    patient.last_surgery_result = "success"
    patient.surgery_blocked = False
    patient.surgery_blocked_resource = None

    # 写入手术收入，零值情况下跳过扣费流程。
    if income_value > 0:
        medical_core._apply_income_to_rhodes(rhodes_island, income_value)

    # 记录手术次数，为日报统计提供数据来源。
    medical_core._bump_daily_counter(rhodes_island, "surgeries_performed", 1)

    # 病情已经低于零时直接触发出院流程并记录手术。
    if new_severity < 0:
        discharge_bonus = int(round(float(severity_config.discharge_bonus) * price_ratio * income_multiplier))
        medical_service.discharge_patient(rhodes_island, patient, bonus_income=discharge_bonus)
        patient.need_surgery = False
        _record_surgery_attempt(
            rhodes_island,
            patient,
            doctor,
            status="success",
            extra={"severity_before": severity_before, "severity_after": "discharged", "income": income_value},
        )
        return True

    # 常规情况下降低病情等级并刷新对应的住院需求。
    patient.severity_level = new_severity
    next_config = game_config.config_medical_severity.get(new_severity)
    if next_config is not None:
        patient.severity_name = next_config.name
        medical_service.refresh_patient_hospital_needs(patient, next_config, reset_progress=True)
    else:
        patient.severity_name = ""

    # 判断是否仍需手术，低于阈值时退出后续手术流程。
    patient.need_surgery = new_severity >= 2
    if not patient.need_surgery:
        patient.surgery_blocked = False

    # 最后写入手术记录，为统计界面提供明细信息。
    _record_surgery_attempt(
        rhodes_island,
        patient,
        doctor,
        status="success",
        extra={"severity_before": severity_before, "severity_after": new_severity, "income": income_value},
    )

    return True


def _record_surgery_attempt(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    doctor: game_type.Character,
    *,
    status: str,
    extra: Optional[Dict[str, object]] = None,
) -> None:
    """记录一条手术执行结果。

    参数:
        rhodes_island (game_type.Rhodes_Island): 发生手术的基地实例。
        patient (medical_constant.MedicalPatient): 进行手术的住院病人。
        doctor (game_type.Character): 执刀医生角色对象。
        status (str): 手术结果标签，例如 success、resource_shortage。
        extra (Optional[Dict[str, object]]): 额外写入的补充字段。
    返回:
        None
    """

    # 构造日志条目，记录核心字段。
    record: Dict[str, object] = {
        "time": getattr(cache_control.cache, "game_time", None),
        "patient_id": patient.patient_id,
        "doctor_id": doctor.cid,
        "status": status,
        "severity": patient.severity_level,
    }
    if extra:
        record.update(extra)

    # 写入基地的手术记录列表，并保持长度限制。
    rhodes_island.medical_surgery_records.append(record)
    if len(rhodes_island.medical_surgery_records) > medical_constant.MAX_SURGERY_RECORDS:
        del rhodes_island.medical_surgery_records[0:-medical_constant.MAX_SURGERY_RECORDS]
