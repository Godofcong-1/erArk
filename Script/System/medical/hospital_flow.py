# -*- coding: UTF-8 -*-
"""住院与手术流程模块

封装医疗系统中与住院管理、每日结算及手术执行相关的逻辑，
供 `medical_service.py` 调用保持核心文件精简。"""
from __future__ import annotations

import math
from typing import Callable, Dict, Optional

from Script.Config import config_def, game_config
from Script.Core import cache_control, game_type
from Script.Design import handle_ability
from Script.System.Medical import medical_constant, patient_management

_MEDICINE_RESOURCE_IDS = medical_constant.ALL_MEDICINE_RESOURCE_IDS
"""医疗系统允许使用的全部药品资源 ID 列表"""

_SURGERY_ABILITY_REQUIREMENT: Dict[int, int] = {
    2: 4,
    3: 6,
}
"""不同严重等级进行手术所需的最低医疗能力等级"""

_SURGERY_RESOURCE_MULTIPLIER = 1.6
"""手术用药相较日常处方的倍率"""

_MAX_SURGERY_RECORDS = 50
"""手术记录列表长度上限，避免无上限增长"""

_FLOAT_EPSILON = 1e-6


def try_hospitalize(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    severity_config: config_def.Medical_Severity,
) -> bool:
    """尝试将病人转入住院队列，成功返回 True

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地缓存对象。
        patient (medical_constant.MedicalPatient): 需要入院的病人。
        severity_config (config_def.Medical_Severity): 病人当前等级对应的配置。
    返回:
        bool: 成功入院返回 True，否则返回 False。"""

    # 从门诊列表移除病人并加入住院字典
    rhodes_island.medical_patients_today.pop(patient.patient_id, None)
    rhodes_island.medical_hospitalized[patient.patient_id] = patient
    patient.state = medical_constant.MedicalPatientState.HOSPITALIZED
    patient.stay_days = 0
    patient.metadata["hospitalized_flag"] = True
    patient.surgery_blocked = False

    # 重置住院处方并更新统计数据
    _prepare_patient_hospital_needs(patient, severity_config, reset_progress=True)
    _increase_daily_counter(rhodes_island, "hospitalized_today", 1)
    return True


def process_hospitalized_patients(
    rhodes_island: game_type.Rhodes_Island,
    consume_medicine: Callable[[medical_constant.MedicalPatient], bool],
) -> None:
    """每日对住院病人进行药物扣除与出院判定"""

    patient_ids = list(rhodes_island.medical_hospitalized.keys())
    for patient_id in patient_ids:
        patient = rhodes_island.medical_hospitalized.get(patient_id)
        if patient is None:
            continue
        process_single_hospitalized_patient(rhodes_island, patient, consume_medicine)


def process_single_hospitalized_patient(
    rhodes_island: game_type.Rhodes_Island,
    patient: Optional[medical_constant.MedicalPatient],
    consume_medicine: Callable[[medical_constant.MedicalPatient], bool],
    *,
    doctor: Optional[game_type.Character] = None,
) -> Dict[str, object]:
    """对单名住院病人执行一次巡诊流程"""

    result: Dict[str, object] = {
        "handled": False,
        "success": False,
        "discharged": False,
        "result": "skip",
        "patient_id": getattr(patient, "patient_id", 0),
        "income_delta": 0,
    }

    if patient is None:
        return result

    severity_before = int(getattr(patient, "severity_level", 0) or 0)
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        _discharge_patient(rhodes_island, patient, bonus_income=0)
        result.update({"handled": True, "discharged": True, "result": "missing_config"})
        return result

    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = patient_management.resolve_price_income_multiplier(price_ratio)

    if patient.need_surgery:
        patient.surgery_blocked = False

    patient.stay_days += 1
    _prepare_patient_hospital_needs(patient, severity_config, reset_progress=False)

    if doctor is not None:
        patient.metadata["last_hospital_doctor_id"] = doctor.cid

    income_before = int(rhodes_island.medical_income_today)
    success = consume_medicine(patient)

    consumed_units = patient.metadata.get("last_consumed_units", {})
    consumed_total = sum(int(value) for value in consumed_units.values()) if consumed_units else 0
    if consumed_total:
        _increase_daily_counter(rhodes_island, "medicine_consumed", consumed_total)

    _increase_daily_counter(rhodes_island, "total_treated_patients", 1)

    result.update(
        {
            "handled": True,
            "success": success,
            "consumed_units": consumed_total,
            "severity_before": severity_before,
        }
    )

    if success:
        _increase_daily_counter(rhodes_island, "hospital_treated_success", 1)
        patient.metadata["last_hospital_result"] = "success"
        new_severity = severity_before - 1
        if new_severity < 0:
            discharge_bonus = int(round(float(severity_config.discharge_bonus) * price_ratio * income_multiplier))
            _discharge_patient(rhodes_island, patient, bonus_income=discharge_bonus)
            result.update({"discharged": True, "result": "discharged", "severity_after": -1})
        else:
            patient.severity_level = new_severity
            next_config = game_config.config_medical_severity.get(new_severity)
            if next_config is None:
                discharge_bonus = int(round(float(severity_config.discharge_bonus) * price_ratio * income_multiplier))
                _discharge_patient(rhodes_island, patient, bonus_income=discharge_bonus)
                result.update({"discharged": True, "result": "discharged", "severity_after": -1})
            else:
                patient.metadata["severity_name"] = next_config.name
                if new_severity < 2:
                    patient.need_surgery = False
                    patient.surgery_blocked = False
                _prepare_patient_hospital_needs(patient, next_config, reset_progress=True)
                result.update({"result": "severity_decreased", "severity_after": new_severity})
    else:
        patient.metadata["last_hospital_result"] = "pending"
        _increase_daily_counter(rhodes_island, "hospital_treated_pending", 1)
        base_income = int(round(float(severity_config.hospital_base_income) * price_ratio * income_multiplier))
        if base_income > 0:
            _apply_income_to_rhodes(rhodes_island, base_income)
        result.update({"result": "pending", "severity_after": patient.severity_level})

    income_after = int(rhodes_island.medical_income_today)
    result["income_delta"] = income_after - income_before
    result.setdefault("severity_after", patient.severity_level)
    return result


def attempt_surgery(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    doctor: game_type.Character,
) -> bool:
    """尝试为住院病人执行手术，返回是否成功

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地缓存对象。
        patient (medical_constant.MedicalPatient): 目标病人。
        doctor (game_type.Character): 执刀干员。
    返回:
        bool: 手术完成返回 True，因条件不足失败返回 False。"""

    # 提取病情配置，缺失时无法继续
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return False

    # 检查医生医疗能力是否达到手术要求
    ability_requirement = _SURGERY_ABILITY_REQUIREMENT.get(patient.severity_level, 4)
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

    # 生成手术所需药品清单，并校验库存
    resource_plan = _resolve_surgery_requirements(severity_config)
    inventory = rhodes_island.materials_resouce
    resource_usage: Dict[int, int] = {}
    for resource_id, amount in resource_plan.items():
        units = int(math.ceil(max(amount, 0.0) - _FLOAT_EPSILON))
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

    # 扣除药品库存并更新每日统计
    consumed_total = 0
    for resource_id, units in resource_usage.items():
        inventory[resource_id] = int(inventory.get(resource_id, 0) or 0) - units
        consumed_total += units

    if consumed_total:
        _increase_daily_counter(rhodes_island, "medicine_consumed", consumed_total)

    # 结合医生能力与收费系数计算手术收益
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = patient_management.resolve_price_income_multiplier(price_ratio)
    doctor_adjust = float(handle_ability.get_ability_adjust(doctor_ability_level))
    base_income = float(severity_config.diagnose_income)
    surgery_income_ratio = float(severity_config.hospital_success_income_ratio or 1.0)
    surgery_income = base_income * surgery_income_ratio * doctor_adjust * price_ratio * income_multiplier
    income_value = int(round(surgery_income))

    # 成功降低病情等级，并按结果记录日志
    severity_before = patient.severity_level
    new_severity = patient.severity_level - 1

    patient.metadata["last_surgery_result"] = "success"
    patient.metadata["last_surgery_doctor_id"] = doctor.cid
    patient.metadata["surgery_consumed_units"] = resource_usage
    patient.surgery_blocked = False

    # 发放手术收入
    if income_value > 0:
        _apply_income_to_rhodes(rhodes_island, income_value)

    _increase_daily_counter(rhodes_island, "surgeries_performed", 1)

    # 病情降至 0 以下时直接出院
    if new_severity < 0:
        discharge_bonus = int(round(float(severity_config.discharge_bonus) * price_ratio * income_multiplier))
        _discharge_patient(rhodes_island, patient, bonus_income=discharge_bonus)
        patient.need_surgery = False
        _record_surgery_attempt(
            rhodes_island,
            patient,
            doctor,
            status="success",
            extra={"severity_before": severity_before, "severity_after": "discharged", "income": income_value},
        )
        return True

    # 正常降低病情等级并刷新处方
    patient.severity_level = new_severity
    next_config = game_config.config_medical_severity.get(new_severity)
    if next_config is not None:
        patient.metadata["severity_name"] = next_config.name
        _prepare_patient_hospital_needs(patient, next_config, reset_progress=True)
    else:
        patient.metadata.pop("severity_name", None)

    # 更新手术需求标记，必要时解除阻断
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


def _build_hospital_prescription(severity_config: config_def.Medical_Severity) -> Dict[int, float]:
    """依据病情等级生成住院用药模板

    参数:
        severity_config (config_def.Medical_Severity): 病情等级配置。
    返回:
        Dict[int, float]: 药品 ID 到需求量的映射。"""

    # 以普通药的均值作为基准需求
    prescription: Dict[int, float] = {}
    normal_amount = (float(severity_config.normal_medicine_min) + float(severity_config.normal_medicine_max)) / 2.0
    normal_amount = max(normal_amount, float(severity_config.normal_medicine_min))
    prescription[medical_constant.MedicalMedicineResource.NORMAL.value] = max(normal_amount, 0.0)
    # 合并特殊药需求模板
    special_template = game_config.medical_severity_special_medicine.get(severity_config.cid, {})
    for resource_id, amount in special_template.items():
        prescription[int(resource_id)] = max(float(amount), 0.0)
    return prescription


def _prepare_patient_hospital_needs(
    patient: medical_constant.MedicalPatient,
    severity_config: config_def.Medical_Severity,
    *,
    reset_progress: bool,
) -> None:
    """为住院病人刷新当日用药需求

    参数:
        patient (medical_constant.MedicalPatient): 需要更新的病人对象。
        severity_config (config_def.Medical_Severity): 对应病情配置。
        reset_progress (bool): 是否重置累积用药进度。
    返回:
        None: 函数直接修改病人对象。"""

    # 按配置生成住院处方模板
    prescription = _build_hospital_prescription(severity_config)
    # 确保病人药品键完整后写入当日需求
    patient.ensure_resource_keys()
    for resource_id in _MEDICINE_RESOURCE_IDS:
        patient.need_resources[resource_id] = float(prescription.get(resource_id, 0.0))
    # 写入处方信息并按需清空进度
    patient.metadata["hospital_prescription"] = prescription
    if reset_progress:
        patient.metadata["medicine_recorded"] = {}
        patient.metadata["medicine_progress"] = {}


def _resolve_surgery_requirements(severity_config: config_def.Medical_Severity) -> Dict[int, float]:
    """根据病情等级生成手术所需药物配方

    参数:
        severity_config (config_def.Medical_Severity): 病情等级配置。
    返回:
        Dict[int, float]: 手术所需药品需求表。"""

    # 以住院处方为基础乘以手术倍率
    base = _build_hospital_prescription(severity_config)
    result: Dict[int, float] = {}
    for resource_id, amount in base.items():
        result[resource_id] = max(amount * _SURGERY_RESOURCE_MULTIPLIER, 0.0)
    # 若处方为空则至少保留普通药需求
    if not result:
        result[medical_constant.MedicalMedicineResource.NORMAL.value] = max(
            float(severity_config.normal_medicine_max), 1.0
        )
    return result


def _discharge_patient(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    *,
    bonus_income: int,
) -> None:
    """处理病人出院逻辑并发放奖励

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地缓存对象。
        patient (medical_constant.MedicalPatient): 即将出院的病人。
        bonus_income (int): 额外发放的收入。
    返回:
        None: 函数直接在缓存上操作。"""

    # 从住院列表移除病人并标记状态
    rhodes_island.medical_hospitalized.pop(patient.patient_id, None)
    patient.state = medical_constant.MedicalPatientState.DISCHARGED
    patient.metadata["discharged_flag"] = True
    # 更新统计并在有奖励时入账
    _increase_daily_counter(rhodes_island, "discharged_today", 1)
    if bonus_income > 0:
        _apply_income_to_rhodes(rhodes_island, bonus_income)


def _record_surgery_attempt(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    doctor: game_type.Character,
    *,
    status: str,
    extra: Optional[Dict[str, object]] = None,
) -> None:
    """将手术执行结果记录到医疗部日志中

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地缓存。
        patient (medical_constant.MedicalPatient): 参与手术的病人。
        doctor (game_type.Character): 执刀干员。
        status (str): 手术结果状态。
        extra (Optional[Dict[str, object]]): 附加记录字段。
    返回:
        None: 函数将数据写入手术记录列表。"""

    # 组装手术记录条目并合并额外字段
    record: Dict[str, object] = {
        "time": getattr(cache_control.cache, "game_time", None),
        "patient_id": patient.patient_id,
        "doctor_id": doctor.cid,
        "status": status,
        "severity": patient.severity_level,
    }
    if extra:
        record.update(extra)
    # 存入手术记录列表并裁剪长度
    rhodes_island.medical_surgery_records.append(record)
    if len(rhodes_island.medical_surgery_records) > _MAX_SURGERY_RECORDS:
        del rhodes_island.medical_surgery_records[0:-_MAX_SURGERY_RECORDS]


def _apply_income_to_rhodes(rhodes_island: game_type.Rhodes_Island, income_value: int) -> None:
    """统一处理医疗收入入账

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地缓存对象。
        income_value (int): 需要入账的收入值。
    返回:
        None: 函数在对象上原地修改数据。"""

    # 收入非正时无需入账
    if income_value <= 0:
        return
    # 更新医疗收入统计和数据库库存
    rhodes_island.medical_income_today += income_value
    rhodes_island.medical_income_total += income_value
    rhodes_island.all_income += income_value
    rhodes_island.materials_resouce[1] = int(rhodes_island.materials_resouce.get(1, 0) or 0) + income_value


def _increase_daily_counter(rhodes_island: game_type.Rhodes_Island, key: str, value: int) -> None:
    """记录医疗系统的日度统计数据

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地缓存对象。
        key (str): 统计项名称。
        value (int): 增量值。
    返回:
        None: 函数直接更新统计字典。"""

    # 变更为 0 时无需更新
    if value == 0:
        return
    # 确保统计字典存在后进行累加
    stats = rhodes_island.__dict__.setdefault("medical_daily_counters", {})
    stats[key] = stats.get(key, 0) + value
