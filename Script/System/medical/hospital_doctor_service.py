# -*- coding: UTF-8 -*-
"""住院医生相关逻辑模块

提供住院医生查房、手术等行为所需的工具函数，
并向门诊医生模块暴露住院患者分配能力。
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

from Script.Config import game_config
from Script.Core import cache_control, game_type
from Script.Design import handle_ability
from Script.System.Medical import medical_constant, medical_core, medical_service


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
            patient.metadata["assigned_hospital_doctor_id"] = doctor_character.cid
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
        assigned = int(patient.metadata.get("assigned_hospital_doctor_id", 0) or 0)
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
    patient.metadata["assigned_hospital_doctor_id"] = doctor_character.cid
    if work_data is not None:
        work_data.medical_patient_id = patient.patient_id
    return patient


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
        work_data = getattr(doctor_character, "work", None)
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
        patient.metadata.pop("assigned_hospital_doctor_id", None)
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0

    medical_core._sync_legacy_patient_counters(rhodes_island)
    return outcome


def perform_surgery_for_doctor(
    doctor_character: Optional[game_type.Character],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """尝试为指定医生安排并执行一台手术。

    参数:
        doctor_character (Optional[game_type.Character]): 执行手术的医生角色。
        target_base (Optional[game_type.Rhodes_Island]): 医疗部所属基地实例。
    返回:
        Dict[str, object]: 手术执行报告，包含收益与病人结局。
    """

    # 确定当前手术所在基地。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if doctor_character is None or rhodes_island is None:
        return {"patient": None, "success": False, "result": "no_doctor"}

    # 分配需要手术的病人。
    patient = _acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=True)
    if patient is None:
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0
        return {"patient": None, "success": False, "result": "no_candidate"}

    # 记录手术前的关键信息，便于输出对比。
    severity_before = int(getattr(patient, "severity_level", 0) or 0)
    income_before = int(rhodes_island.medical_income_today)
    success = _attempt_surgery_on_patient(rhodes_island, patient, doctor_character)
    income_after = int(rhodes_island.medical_income_today)

    result: Dict[str, object] = {
        "patient": patient,
        "success": success,
        "discharged": patient.state == medical_constant.MedicalPatientState.DISCHARGED,
        "result": "success" if success else patient.metadata.get("last_surgery_result", "failed"),
        "income_delta": income_after - income_before,
        "severity_before": severity_before,
        "severity_after": int(getattr(patient, "severity_level", severity_before) or severity_before),
    }

    # 手术完成或失效时解除医生绑定。
    if success or patient.surgery_blocked or not patient.need_surgery:
        patient.metadata.pop("assigned_hospital_doctor_id", None)
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0

    medical_core._sync_legacy_patient_counters(rhodes_island)
    return result


def attempt_surgery(
    patient_id: int,
    doctor_character: game_type.Character,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """按病人 ID 触发一次手术流程。

    参数:
        patient_id (int): 住院病人的唯一编号。
        doctor_character (game_type.Character): 尝试手术的医生角色。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地上下文，默认读取全局缓存。
    返回:
        bool: 手术是否顺利完成。
    """

    # 无医生对象时不允许尝试手术。
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

    # 不需要手术时直接返回失败。
    if not patient.need_surgery:
        return False

    # 被阻塞的手术需要外界条件解除后才可执行。
    if patient.surgery_blocked:
        return False

    return _attempt_surgery_on_patient(rhodes_island, patient, doctor_character)


def _attempt_surgery_on_patient(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    doctor: game_type.Character,
) -> bool:
    """执行住院病人的手术操作。"""

    # 读取病情配置，缺失时视为手术失败。
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return False

    # 检查医生能力是否满足当前病情的最低要求。
    ability_requirement = medical_constant.SURGERY_ABILITY_REQUIREMENT.get(patient.severity_level, 4)
    doctor_ability_level = doctor.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0)
    if doctor_ability_level < ability_requirement:
        patient.surgery_blocked = True
        patient.metadata["last_surgery_result"] = "ability_insufficient"
        _record_surgery_attempt(
            rhodes_island,
            patient,
            doctor,
            status="ability_insufficient",
            extra={"required_level": ability_requirement, "doctor_level": doctor_ability_level},
        )
        return False

    # 解析手术所需资源并检查库存是否充足。
    resource_plan = medical_service.resolve_surgery_requirements(severity_config)
    inventory = getattr(rhodes_island, "materials_resouce", {})
    resource_usage: Dict[int, int] = {}
    for resource_id, amount in resource_plan.items():
        units = int(math.ceil(max(amount, 0.0) - medical_constant.FLOAT_EPSILON))
        if units <= 0:
            continue
        stock = int(inventory.get(resource_id, 0) or 0)
        if stock < units:
            patient.surgery_blocked = True
            patient.metadata["last_surgery_result"] = "resource_shortage"
            patient.metadata["surgery_blocked_resource"] = resource_id
            _record_surgery_attempt(
                rhodes_island,
                patient,
                doctor,
                status="resource_shortage",
                extra={"resource_id": resource_id, "need": units, "stock": stock},
            )
            return False
        resource_usage[resource_id] = units

    # 扣除库存并记录消耗总量。
    consumed_total = 0
    for resource_id, units in resource_usage.items():
        inventory[resource_id] = int(inventory.get(resource_id, 0) or 0) - units
        consumed_total += units

    if consumed_total:
        medical_core._bump_daily_counter(rhodes_island, "medicine_consumed", consumed_total)

    # 计算手术收入，考虑收费倍率与医生加成。
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = medical_core.resolve_price_income_multiplier(price_ratio)
    doctor_adjust = float(handle_ability.get_ability_adjust(doctor_ability_level))
    base_income = float(severity_config.diagnose_income)
    surgery_income_ratio = float(severity_config.hospital_success_income_ratio or 1.0)
    surgery_income = base_income * surgery_income_ratio * doctor_adjust * price_ratio * income_multiplier
    income_value = int(round(surgery_income))

    severity_before = patient.severity_level
    new_severity = patient.severity_level - 1

    # 记录手术结果并标记消耗情况。
    patient.metadata["last_surgery_result"] = "success"
    patient.metadata["last_surgery_doctor_id"] = doctor.cid
    patient.metadata["surgery_consumed_units"] = resource_usage
    patient.surgery_blocked = False

    if income_value > 0:
        medical_core._apply_income_to_rhodes(rhodes_island, income_value)

    medical_core._bump_daily_counter(rhodes_island, "surgeries_performed", 1)

    # 病情降至 0 以下时直接出院并发放奖励。
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

    # 更新病情等级并刷新用药需求。
    patient.severity_level = new_severity
    next_config = game_config.config_medical_severity.get(new_severity)
    if next_config is not None:
        patient.metadata["severity_name"] = next_config.name
        medical_service.refresh_patient_hospital_needs(patient, next_config, reset_progress=True)
    else:
        patient.metadata.pop("severity_name", None)

    # 低于阈值时不再需要手术。
    patient.need_surgery = new_severity >= 2
    if not patient.need_surgery:
        patient.surgery_blocked = False

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
