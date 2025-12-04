# -*- coding: UTF-8 -*-
"""门诊病人生成与倍率处理模块

负责门诊病人的生成、并发症组合以及价格倍率的工具函数，
供医疗系统其他模块复用。
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set
from types import FunctionType

from Script.Config import game_config
from Script.Core import cache_control, game_type, get_text
from Script.System.Medical import medical_constant, medical_core, medical_service

_: FunctionType = get_text._
""" 翻译函数 """


def _clear_player_session_state(patient: medical_constant.MedicalPatient) -> None:
    """清理玩家诊疗流程写入的临时状态字段。

    参数:
        patient (medical_constant.MedicalPatient): 目标病人对象。
    返回:
        None: 重置患者对象上的玩家相关临时数据。
    """

    # 安全检查，防止 None 对象导致异常。
    if patient is None:
        return

    # 重置玩家会话相关的显式字段。
    patient.player_session_active = False
    patient.player_previous_state = ""
    patient.player_used_checks = 0
    patient.player_confirmed_complications.clear()
    patient.player_check_records.clear()
    patient.player_pending_checks.clear()


def _acquire_patient_for_player(
    doctor_character: Optional[game_type.Character],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> Optional[medical_constant.MedicalPatient]:
    """根据当前优先策略为玩家诊疗会话选定病人。

    参数:
        doctor_character (Optional[game_type.Character]): 玩家当前操控的医生。
        rhodes_island (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        Optional[medical_constant.MedicalPatient]: 分配到的病人对象，若无则返回 None。
    """

    # 没有基地上下文时无法为玩家选择病人。
    if rhodes_island is None:
        return None

    # 若玩家已有锁定病人则优先返回该对象。
    current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
    if current_id:
        patient = rhodes_island.medical_patients_today.get(current_id)
        if patient is not None:
            return patient

    # 过滤出符合状态与医生绑定条件的候选病人。
    candidates: List[medical_constant.MedicalPatient] = []
    for patient in rhodes_island.medical_patients_today.values():
        if patient.state not in medical_constant.WAITING_QUEUE_STATE_SET:
            continue
        assigned_doctor = int(getattr(patient, "assigned_doctor_id", 0) or 0)
        if doctor_character is not None and assigned_doctor not in {0, doctor_character.cid}:
            continue
        candidates.append(patient)

    # 没有候选者时返回 None。
    if not candidates:
        return None

    return medical_service.select_triage_candidate(candidates, rhodes_island)


def start_player_diagnose_session(
    doctor_character: Optional[game_type.Character] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Optional[medical_constant.MedicalPatient]:
    """
    初始化玩家诊疗会话。

    参数:
        doctor_character (Optional[game_type.Character]): 玩家当前操控的医生角色。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        Optional[medical_constant.MedicalPatient]: 分配到的病人对象，若无则返回 None。
    """

    # 确定会话关联的基地对象。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return None

    # 玩家医生为空时默认使用主角（ID 0）。
    if doctor_character is None:
        doctor_character = getattr(cache_control.cache, "character_data", {}).get(0)

    if doctor_character is None:
        return None

    # 按当前优先策略分配待诊病人。
    patient = _acquire_patient_for_player(doctor_character, rhodes_island)
    if patient is None:
        return None

    # 初始化玩家会话所需的元数据。
    if not patient.player_session_active:
        patient.player_previous_state = patient.state.value
        patient.player_session_active = True
        patient.player_used_checks = 0
        patient.player_confirmed_complications = []
        patient.player_check_records = []
        patient.player_pending_checks = []

    # 绑定医生与病人，记录当前处理对象。
    patient.assigned_doctor_id = doctor_character.cid if doctor_character is not None else 0
    medical_service.set_patient_state(patient, medical_constant.MedicalPatientState.IN_TREATMENT_PLAYER)
    rhodes_island.medical_player_current_patient_id = patient.patient_id

    if doctor_character is not None and hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = patient.patient_id

    return patient

def abort_player_diagnose_session(
    doctor_character: Optional[game_type.Character] = None,
    *,
    patient: Optional[medical_constant.MedicalPatient] = None,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """终止玩家诊疗会话并恢复病人原始状态。"""

    # 获取基地对象，若缺失则直接退出。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    # 若未显式指定病人，则回退到当前锁定的对象。
    if patient is None:
        current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
        if current_id:
            patient = rhodes_island.medical_patients_today.get(current_id)

    if patient is None:
        return

    # 恢复病人的原始状态并解除医生绑定。
    previous_state = getattr(patient, "player_previous_state", "")
    restored_state = medical_constant.MedicalPatientState.REFRESHED
    if previous_state:
        try:
            restored_state = medical_constant.MedicalPatientState(previous_state)
        except ValueError:
            restored_state = medical_constant.MedicalPatientState.REFRESHED
    medical_service.set_patient_state(patient, restored_state)
    patient.assigned_doctor_id = 0

    # 清理会话数据并重置当前病人 ID。
    _clear_player_session_state(patient)
    rhodes_island.medical_player_current_patient_id = 0

    # 若未提供医生对象则默认选取主角。
    if doctor_character is None:
        doctor_character = getattr(cache_control.cache, "character_data", {}).get(0)
    if doctor_character is not None and hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = 0


def commit_player_diagnose_session(
    doctor_character: Optional[game_type.Character] = None,
    *,
    patient: Optional[medical_constant.MedicalPatient] = None,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """完成玩家诊疗流程并返回结算摘要"""

    # 校验基地上下文
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    # 缺省使用玩家作为执行医生
    if doctor_character is None:
        doctor_character = getattr(cache_control.cache, "character_data", {}).get(0)

    if doctor_character is None:
        return {"success": False, "reason": "no_doctor"}

    # 若未指定病人则读取会话关联的当前病人
    if patient is None:
        current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
        if current_id:
            patient = rhodes_island.medical_patients_today.get(current_id)

    # 校验病人对象
    if patient is None:
        return {"success": False, "reason": "no_patient"}

    # 读取病情配置
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return {"success": False, "reason": "no_severity_config"}

    # 准备推进诊疗进度并绑定医生
    base_hours = max(float(severity_config.base_hours or 0.0), 0.1)
    patient.diagnose_progress = max(float(patient.diagnose_progress or 0.0), base_hours - 0.1)
    patient.assigned_doctor_id = doctor_character.cid if doctor_character is not None else 0

    # 调用常规诊疗推进，并记录诊疗收入变化。
    income_before = float(rhodes_island.medical_income_today or 0.0)
    medical_service.advance_diagnose(patient.patient_id, doctor_character, target_base=rhodes_island)
    income_after = float(rhodes_island.medical_income_today or 0.0)

    # 根据最近一次用药记录还原药费收益，用于界面提示
    medicine_success = patient.state == medical_constant.MedicalPatientState.MEDICINE_GRANTED

    # 计算诊疗收益
    diagnose_income = medical_service.estimate_patient_diagnose_income(patient, target_base=rhodes_island)

    # 计算药费收益
    income_delta = int(round(income_after - income_before))
    medicine_income = max(0, income_delta - diagnose_income)

    # 清理临时数据并解除医生绑定。
    _clear_player_session_state(patient)
    rhodes_island.medical_player_current_patient_id = 0

    return {
        "success": True,
        "patient_id": patient.patient_id,
        "diagnose_income": diagnose_income,
        "medicine_income": medicine_income,
        "medicine_success": medicine_success,
        "state": patient.state.value,
    }


def execute_player_diagnose_checks(
    selections: List[Dict[str, int]],
    *,
    patient: Optional[medical_constant.MedicalPatient] = None,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """执行玩家选择的检查条目并记录结果。"""

    # 验证基地上下文。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    # 若未指定病人则沿用当前会话对象。
    if patient is None:
        current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
        if current_id:
            patient = rhodes_island.medical_patients_today.get(current_id)

    if patient is None:
        return {"success": False, "reason": "no_patient"}

    if not selections:
        return {"success": False, "reason": "empty_selection"}

    # 更新检查次数并准备记录集合。
    # 累计玩家使用的检查次数。
    used_checks = int(getattr(patient, "player_used_checks", 0) or 0) + 1
    patient.player_used_checks = used_checks

    # 记录已确诊与实际存在的并发症集合，供比对使用。
    confirmed_set: Set[int] = set(int(cid) for cid in getattr(patient, "player_confirmed_complications", []))
    actual_complications: Set[int] = {int(cid) for cid in getattr(patient, "complications", [])}

    # 将追踪信息转换成便于检索的列表结构。
    trace_info: List[Dict[str, int]] = [
        {
            "system_id": int(entry.get("system_id", 0)),
            "part_id": int(entry.get("part_id", 0)),
            "severity_level": int(entry.get("severity_level", 0)),
            "cid": int(entry.get("cid", entry.get("complication_id", 0))),
        }
        for entry in getattr(patient, "complication_trace", [])
    ]

    # 预处理每个部位的最高严重程度，用于回诊提示。
    highest_severity_by_part: Dict[int, int] = {}
    for entry in trace_info:
        part_id = entry["part_id"]
        severity_level = entry["severity_level"]
        highest_severity_by_part[part_id] = max(highest_severity_by_part.get(part_id, -1), severity_level)

    records: List[Dict[str, object]] = []
    for option in selections:
        comp_id = int(option.get("cid", 0) or 0)
        system_id = int(option.get("system_id", 0) or 0)
        part_id = int(option.get("part_id", 0) or 0)
        severity_level = int(option.get("severity_level", 0) or 0)
        config_entry = game_config.config_medical_complication.get(comp_id)

        result_type = "unknown"
        message = ""
        hint_severity = None

        # 根据并发症是否命中决定结果类型。
        if comp_id and comp_id in actual_complications:
            result_type = "positive"
            confirmed_set.add(comp_id)
            message = getattr(config_entry, "exam_result_positive", "") if config_entry else ""
            if not message:
                message = _("检查结果提示确诊，请准备治疗方案。")
        else:
            # 如果同部位存在更严重的并发症，则提示复检。
            actual_highest = highest_severity_by_part.get(part_id, -1)
            if actual_highest >= 0:
                result_type = "recheck"
                hint_severity = actual_highest
                if config_entry:
                    if actual_highest <= 0:
                        message = config_entry.recheck_hint_mild
                    elif actual_highest == 1:
                        message = config_entry.recheck_hint_moderate
                    else:
                        message = config_entry.recheck_hint_severe
                if not message:
                    message = _("该部位存在其他异常，需更换检查方法。")
            else:
                # 未命中任何异常则返回阴性结果。
                result_type = "negative"
                if config_entry:
                    message = config_entry.exam_result_negative
                if not message:
                    message = _("未发现该部位存在明显异常。")

        record = {
            "cid": comp_id,
            "system_id": system_id,
            "part_id": part_id,
            "severity_level": severity_level,
            "result": result_type,
            "message": message,
            "hint_severity": hint_severity,
            "check_index": used_checks,
            "name": getattr(config_entry, "name", ""),
            "exam_method": getattr(config_entry, "exam_method", ""),
        }
        records.append(record)

    # 将本次检查结果写入记录，并保留最近 30 条。
    previous_records: List[Dict[str, object]] = list(getattr(patient, "player_check_records", []))
    previous_records.extend(records)
    patient.player_check_records = previous_records[-30:]
    patient.player_confirmed_complications = sorted(confirmed_set)
    patient.player_pending_checks = []

    return {
        "success": True,
        "results": records,
        "used_checks": used_checks,
    }


def build_player_check_catalog(
    patient: Optional[medical_constant.MedicalPatient],
) -> Dict[int, Dict[str, object]]:
    """构建玩家诊疗用的系统/部位/并发症选择树。"""

    # 未指定病人时返回空目录。
    if patient is None:
        return {}

    # 按系统遍历配置，构建嵌套的选择结构。
    catalog: Dict[int, Dict[str, object]] = {}
    for system_id, part_map in sorted(game_config.config_medical_body_system_by_system.items()):
        if not isinstance(part_map, dict) or not part_map:
            continue

        first_entry = next(iter(part_map.values()), None)
        system_name = getattr(first_entry, "system_name", f"System {system_id}") if first_entry else f"System {system_id}"

        part_catalog: Dict[int, Dict[str, object]] = {}
        for part_id, part_info in sorted(part_map.items()):
            if part_info is None:
                continue
            complication_map = game_config.config_medical_complication_detail.get(system_id, {}).get(part_id, {})
            options: List[Dict[str, object]] = []
            for severity_level in sorted(complication_map.keys()):
                for comp in complication_map[severity_level]:
                    # 将并发症配置映射为玩家可选择的条目。
                    options.append(
                        {
                            "cid": comp.cid,
                            "name": comp.name,
                            "severity_level": comp.severity_level,
                            "exam_method": comp.exam_method,
                            "system_id": system_id,
                            "part_id": part_id,
                        }
                    )
            if not options:
                continue
            part_catalog[int(part_id)] = {
                "part_name": getattr(part_info, "part_name", str(part_id)),
                "part_type": getattr(part_info, "part_type", 0),
                "gender_limit": int(getattr(part_info, "gender_limit", 2)),
                "options": options,
            }

        if part_catalog:
            # 仅当系统下存在可用部位时收录。
            catalog[int(system_id)] = {
                "system_name": system_name,
                "parts": part_catalog,
            }

    return catalog

def estimate_patient_treatment_summary(
    patient: Optional[medical_constant.MedicalPatient],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """估算诊疗收益与资源需求摘要。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 待评估的病人对象。
        target_base (Optional[game_type.Rhodes_Island]): 指定罗德岛基座，用于读取倍率与库存。
    返回:
        Dict[str, object]: 汇总后的收益、倍率与资源需求数据。
    """

    # 缺少病人对象时直接返回失败结果
    if patient is None:
        return {"success": False, "reason": "no_patient"}

    # 解析罗德岛对象并获取病情配置
    rhodes_island = medical_core._get_rhodes_island(target_base)
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return {"success": False, "reason": "no_severity_config"}

    # 计算诊疗收益
    diagnose_income = medical_service.estimate_patient_diagnose_income(patient, target_base=rhodes_island)

    # 计算潜在药费收益与资源需求摘要
    price_ratio = medical_service.get_medical_price_ratio(target_base=rhodes_island)
    income_multiplier = medical_core.resolve_price_income_multiplier(price_ratio)
    medicine_income_ratio = float(severity_config.medicine_income_ratio or 0.0)
    predicted_medicine_income = 0.0
    resource_summary: List[Dict[str, object]] = []
    # 遍历病人所需的药物资源，计算潜在收益并构造摘要
    for resource_id, amount in patient.need_resources.items():
        need_value = float(amount or 0.0)
        if need_value <= 0:
            continue
        resource_config = game_config.config_resouce.get(resource_id)
        unit_price = float(getattr(resource_config, "price", 0.0) or 0.0)
        predicted_medicine_income += unit_price * need_value * medicine_income_ratio * income_multiplier
        resource_summary.append(
            {
                "resource_id": resource_id,
                "name": getattr(resource_config, "name", str(resource_id)),
                "amount": need_value,
            }
        )

    return {
        "success": True,
        "price_ratio": price_ratio,
        "income_multiplier": income_multiplier,
        "diagnose_income": diagnose_income,
        "predicted_medicine_income": int(round(predicted_medicine_income)),
        "resources": resource_summary,
    }
