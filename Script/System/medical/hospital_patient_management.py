# -*- coding: UTF-8 -*-
"""住院病人流程处理模块

封装医疗系统中与住院病人相关的转院、日结算及用药逻辑，
供医生行为与结算流程复用。
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Optional

from Script.Config import config_def, game_config
from Script.Core import game_type
from Script.System.Medical import medical_service, medical_constant, medical_core


def try_hospitalize(
    patient_id: int,
    *,
    target_base: game_type.Rhodes_Island | None = None,
) -> bool:
    """尝试将病人转入住院列表。

    参数:
        patient_id (int): 等待转住院的病人唯一编号。
        target_base (game_type.Rhodes_Island | None): 指定罗德岛基座，缺省时使用全局缓存。
    返回:
        bool: 是否成功将病人移动至住院列表。
    """

    # 定位当前处理的基地对象。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    # 查找病人并确认尚未在住院列表。
    patient, already_hospitalized = medical_core._locate_patient(patient_id, rhodes_island)
    if patient is None or already_hospitalized:
        return False

    # 仅允许待发药状态的病人转入住院。
    if patient.state != medical_constant.MedicalPatientState.WAITING_MEDICATION:
        return False

    # 缺少病情配置无法判断是否需要住院。
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return False

    # 检查床位是否已满。
    bed_limit = int(rhodes_island.medical_bed_limit or 0)
    if bed_limit > 0 and len(rhodes_island.medical_hospitalized) >= bed_limit:
        return False

    # 病情不要求住院时记录原因并返回。
    if severity_config.require_hospitalization != 1:
        return False

    # 从门诊列表移除并加入住院表，同时重置相关字段。
    outpatient_table = medical_service.get_patient_table(
        target_base=rhodes_island, hospitalized=False
    )
    hospital_table = medical_service.get_patient_table(target_base=rhodes_island, hospitalized=True)
    outpatient_table.pop(patient.patient_id, None)
    hospital_table[patient.patient_id] = patient
    medical_service.set_patient_state(patient, medical_constant.MedicalPatientState.HOSPITALIZED)
    patient.stay_days = 0
    patient.severity_name = severity_config.name
    patient.surgery_blocked = False

    refresh_patient_hospital_needs(patient, severity_config, reset_progress=True)
    medical_core._bump_daily_counter(rhodes_island, "hospitalized_today", 1)
    medical_core._sync_legacy_patient_counters(rhodes_island)
    return True


def process_hospitalized_patients(
    *,
    target_base: game_type.Rhodes_Island | None = None,
) -> None:
    """每日结算住院病人：扣药并判定出院。

    参数:
        target_base (game_type.Rhodes_Island | None): 指定需要处理的基地实例。
    返回:
        None
    """

    # 若基地不存在或无住院病人则直接返回。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None or not rhodes_island.medical_hospitalized:
        return

    def _consume(patient: medical_constant.MedicalPatient) -> bool:
        return try_consume_medicine(patient, is_hospitalized=True, target_base=rhodes_island)

    # 复制病人 ID 避免遍历过程中修改集合。
    patient_ids = list(rhodes_island.medical_hospitalized.keys())
    for patient_id in patient_ids:
        patient = rhodes_island.medical_hospitalized.get(patient_id)
        if patient is None:
            continue
        process_single_hospitalized_patient(rhodes_island, patient, _consume)
    medical_core._sync_legacy_patient_counters(rhodes_island)


def process_single_hospitalized_patient(
    rhodes_island: game_type.Rhodes_Island,
    patient: Optional[medical_constant.MedicalPatient],
    consume_medicine: Callable[[medical_constant.MedicalPatient], bool],
    *,
    doctor: Optional[game_type.Character] = None,
) -> Dict[str, object]:
    """对单名住院病人执行一次巡诊流程。

    参数:
        rhodes_island (game_type.Rhodes_Island): 巡诊所在的基地实例。
        patient (Optional[medical_constant.MedicalPatient]): 目标病人，若 None 则直接跳过。
        consume_medicine (Callable[[medical_constant.MedicalPatient], bool]): 用于扣药的回调。
        doctor (Optional[game_type.Character]): 记录巡诊医生信息的角色对象。
    返回:
        Dict[str, object]: 巡诊结果与收益统计。
    """

    result: Dict[str, object] = {
        "handled": False,
        "success": False,
        "discharged": False,
        "result": "skip",
        "patient_id": getattr(patient, "patient_id", 0),
        "income_delta": 0,
    }

    # 缺少病人对象时返回默认结果。
    if patient is None:
        return result

    # 获取病人当前病情配置，缺失时直接安排出院。
    severity_before = int(getattr(patient, "severity_level", 0) or 0)
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        discharge_patient(rhodes_island, patient, bonus_income=0)
        result.update({"handled": True, "discharged": True, "result": "missing_config"})
        return result

    # 计算当前收费系数对应的收入倍率。
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = medical_core.resolve_price_income_multiplier(price_ratio)

    if patient.need_surgery:
        patient.surgery_blocked = False

    # 住院天数 +1 并刷新当日用药需求。
    patient.stay_days += 1
    refresh_patient_hospital_needs(patient, severity_config, reset_progress=False)

    # 执行扣药回调并统计收入变化。
    income_before = int(rhodes_island.medical_income_today)
    success = consume_medicine(patient)

    # --- 汇总病人本次用药的各类药剂消耗量，用于统计与日志展示 ---
    consumed_units = dict(getattr(patient, "last_consumed_units", {}) or {})
    consumed_total = sum(int(value) for value in consumed_units.values()) if consumed_units else 0
    if consumed_total:
        medical_core._bump_daily_counter(rhodes_island, "medicine_consumed", consumed_units)

    result.update(
        {
            "handled": True,
            "success": success,
            "consumed_units": consumed_total,
            "severity_before": severity_before,
        }
    )

    # 记录诊疗完成次数，便于与后续用药完成分开统计。
    medical_core._bump_daily_counter(rhodes_island, "diagnose_completed_hospital", 1)

    if success:
        # 仅在用药成功时统计完成治疗的住院病人。
        medical_core._bump_daily_counter(rhodes_island, "medicine_completed_hospital", 1)
        new_severity = severity_before - 1
        if new_severity < 0:
            discharge_bonus = int(round(float(severity_config.discharge_bonus) * price_ratio * income_multiplier))
            discharge_patient(rhodes_island, patient, bonus_income=discharge_bonus)
            result.update({"discharged": True, "result": "discharged", "severity_after": -1})
        else:
            patient.severity_level = new_severity
            next_config = game_config.config_medical_severity.get(new_severity)
            if next_config is None:
                discharge_bonus = int(round(float(severity_config.discharge_bonus) * price_ratio * income_multiplier))
                discharge_patient(rhodes_island, patient, bonus_income=discharge_bonus)
                result.update({"discharged": True, "result": "discharged", "severity_after": -1})
            else:
                patient.severity_name = next_config.name
                if new_severity < 2:
                    patient.need_surgery = False
                    patient.surgery_blocked = False
                refresh_patient_hospital_needs(patient, next_config, reset_progress=True)
                result.update({"result": "severity_decreased", "severity_after": new_severity})
    else:
        medical_core._bump_daily_counter(rhodes_island, "hospital_waiting_medicine", 1)
        base_income = int(round(float(severity_config.hospital_base_income) * price_ratio * income_multiplier))
        if base_income > 0:
            medical_core._apply_income_to_rhodes(rhodes_island, base_income)
        result.update({"result": "pending", "severity_after": patient.severity_level})

    # 记录本次处理的收入增量。
    income_after = int(rhodes_island.medical_income_today)
    result["income_delta"] = income_after - income_before
    result.setdefault("severity_after", patient.severity_level)
    return result


def try_consume_medicine(
    patient: medical_constant.MedicalPatient,
    *,
    is_hospitalized: bool = False,
    target_base: game_type.Rhodes_Island | None = None,
) -> bool:
    """尝试为病人扣除药物并结算药费。

    参数:
        patient (medical_constant.MedicalPatient): 等待扣药的病人对象。
        is_hospitalized (bool): 标记病人是否在住院区，用于决定倍率与计数。
        target_base (game_type.Rhodes_Island | None): 指定基地实例，缺省读取全局缓存。
    返回:
        bool: 药物是否全部满足需求。
    """

    # 无病人或基地对象时，无法扣药。
    if patient is None:
        return False

    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return False

    # 准备运行期缓存，包括药品累加器与进度记录。
    accumulator = rhodes_island.medical_inventory_accumulator
    inventory = rhodes_island.materials_resouce
    if not isinstance(patient.medicine_recorded, dict):
        patient.medicine_recorded = {}
    if not isinstance(patient.medicine_progress, dict):
        patient.medicine_progress = {}
    if not isinstance(patient.medicine_consumed_units, dict):
        patient.medicine_consumed_units = {}

    recorded_map = patient.medicine_recorded
    progress_map = patient.medicine_progress
    consumed_history = patient.medicine_consumed_units

    resource_success: dict[int, bool] = {}
    consumed_units: dict[int, int] = {}

    # 遍历所有药品资源，根据需求累加库存并扣减。
    for resource_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS:
        need_total = float(patient.need_resources.get(resource_id, 0.0) or 0.0)
        accumulator_value = float(accumulator.get(resource_id, 0.0) or 0.0)
        recorded = float(recorded_map.get(resource_id, 0.0) or 0.0)

        if need_total <= medical_constant.FLOAT_EPSILON:
            recorded_map[resource_id] = 0.0
            progress_map[resource_id] = 0.0
            consumed_units[resource_id] = 0
            resource_success[resource_id] = True
            accumulator[resource_id] = accumulator_value
            continue

        if recorded < 0:
            recorded = 0.0
        if recorded > need_total:
            recorded = need_total

        to_record = need_total - recorded
        if to_record > medical_constant.FLOAT_EPSILON:
            accumulator_value += to_record
            recorded += to_record

        # 计算应扣除的整数单位。
        required_units = int(math.floor(accumulator_value + medical_constant.FLOAT_EPSILON))
        stock = int(inventory.get(resource_id, 0) or 0)

        if required_units > 0 and stock < required_units:
            accumulator[resource_id] = accumulator_value
            recorded_map[resource_id] = recorded
            consumed_units[resource_id] = 0
            resource_success[resource_id] = False
            continue

        consumed_now = required_units
        if consumed_now > 0:
            inventory[resource_id] = stock - consumed_now
            accumulator_value -= consumed_now

        accumulator[resource_id] = accumulator_value
        recorded_map[resource_id] = recorded
        progress_map[resource_id] = need_total
        consumed_units[resource_id] = consumed_now
        resource_success[resource_id] = True
        patient.need_resources[resource_id] = 0.0

    # 判断所有药品是否全部满足需求。
    overall_success = all(
        resource_success.get(res_id, True) for res_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS
    )

    # 计算用药收入并写入历史记录。
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = medical_core.resolve_price_income_multiplier(price_ratio)
    medicine_ratio = float(
        (
            severity_config.hospital_success_income_ratio
            if is_hospitalized and severity_config.hospital_success_income_ratio
            else None
        )
        or severity_config.medicine_income_ratio
        or 0.0
    )

    total_income = 0
    for resource_id, used_units in consumed_units.items():
        if used_units <= 0:
            continue
        resource_config = game_config.config_resouce.get(resource_id)
        unit_price = float(getattr(resource_config, "price", 0)) if resource_config else 0.0
        consumed_history[resource_id] = int(consumed_history.get(resource_id, 0) or 0) + used_units
        resource_income = unit_price * used_units * medicine_ratio * price_ratio * income_multiplier
        if resource_income <= 0:
            continue
        income_value = int(round(resource_income))
        if income_value <= 0:
            continue
        total_income += income_value

    if total_income > 0:
        rhodes_island.medical_income_today += total_income
        rhodes_island.medical_income_total += total_income
        rhodes_island.all_income += total_income
        inventory[1] = int(inventory.get(1, 0) or 0) + total_income

    if overall_success:
        patient.medicine_recorded = {}
        patient.medicine_progress = {}

    # --- 将门诊病人的药剂消耗以明细形式写入当日统计 ---
    consumed_total_units = sum(int(value) for value in consumed_units.values())
    if not is_hospitalized and consumed_total_units:
        medical_core._bump_daily_counter(rhodes_island, "medicine_consumed", consumed_units)

    if not is_hospitalized:
        # --- 根据扣药结果刷新门诊病人的状态并更新对应统计 ---
        if overall_success:
            medical_service.set_patient_state(patient, medical_constant.MedicalPatientState.MEDICINE_GRANTED)
            medical_core._bump_daily_counter(rhodes_island, "medicine_completed_outpatient", 1)
        else:
            medical_service.set_patient_state(patient, medical_constant.MedicalPatientState.WAITING_MEDICATION)
            medical_core._bump_daily_counter(rhodes_island, "outpatient_waiting_medicine", 1)

    patient.last_consumed_units = consumed_units

    medical_core._sync_legacy_patient_counters(rhodes_island)
    return overall_success


def refresh_patient_hospital_needs(
    patient: medical_constant.MedicalPatient,
    severity_config: config_def.Medical_Severity,
    *,
    reset_progress: bool,
) -> None:
    """刷新住院病人的当日用药需求。

    参数:
        patient (medical_constant.MedicalPatient): 待刷新需求的住院病人。
        severity_config (config_def.Medical_Severity): 对应病情等级配置。
        reset_progress (bool): 是否重置用药记录与进度。
    返回:
        None
    """

    # 依据病情模板刷新每日处方。
    prescription = _build_hospital_prescription(severity_config)
    patient.ensure_resource_keys()
    for resource_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS:
        patient.need_resources[resource_id] = float(prescription.get(resource_id, 0.0))
    if reset_progress:
        patient.medicine_recorded = {}
        patient.medicine_progress = {}


def _build_hospital_prescription(severity_config: config_def.Medical_Severity) -> Dict[int, float]:
    """依据病情等级生成住院用药模板。

    参数:
        severity_config (config_def.Medical_Severity): 病情等级配置。
    返回:
        Dict[int, float]: 资源 ID 到推荐消耗量的映射。
    """

    prescription: Dict[int, float] = {}
    normal_amount = (
        float(severity_config.normal_medicine_min) + float(severity_config.normal_medicine_max)
    ) / 2.0
    normal_amount = max(normal_amount, float(severity_config.normal_medicine_min))
    prescription[medical_constant.MedicalMedicineResource.NORMAL.value] = max(normal_amount, 0.0)
    special_template = game_config.medical_severity_special_medicine.get(severity_config.cid, {})
    for resource_id, amount in special_template.items():
        prescription[int(resource_id)] = max(float(amount), 0.0)
    return prescription


def resolve_surgery_requirements(severity_config: config_def.Medical_Severity) -> Dict[int, float]:
    """根据病情等级生成手术所需药品需求表。

    参数:
        severity_config (config_def.Medical_Severity): 手术对应的病情等级配置。
    返回:
        Dict[int, float]: 手术所需药品资源及数量映射。
    """

    # 手术药品需求基于住院处方，并套用额外倍率。
    base = _build_hospital_prescription(severity_config)
    result: Dict[int, float] = {}
    for resource_id, amount in base.items():
        result[resource_id] = max(amount * medical_constant.SURGERY_RESOURCE_MULTIPLIER, 0.0)
    if not result:
        result[medical_constant.MedicalMedicineResource.NORMAL.value] = max(
            float(severity_config.normal_medicine_max), 1.0
        )
    return result


def discharge_patient(
    rhodes_island: game_type.Rhodes_Island,
    patient: medical_constant.MedicalPatient,
    *,
    bonus_income: int,
) -> None:
    """处理病人出院并入账奖励。

    参数:
        rhodes_island (game_type.Rhodes_Island): 出院所在的基地实例。
        patient (medical_constant.MedicalPatient): 即将出院的病人。
        bonus_income (int): 出院奖励的货币收益。
    返回:
        None
    """

    # 将病人从住院表移除并标记出院状态。
    hospital_table = medical_service.get_patient_table(target_base=rhodes_island, hospitalized=True)
    hospital_table.pop(patient.patient_id, None)
    medical_service.set_patient_state(patient, medical_constant.MedicalPatientState.DISCHARGED)
    medical_core._bump_daily_counter(rhodes_island, "discharged_today", 1)
    medical_core._apply_income_to_rhodes(rhodes_island, bonus_income)
