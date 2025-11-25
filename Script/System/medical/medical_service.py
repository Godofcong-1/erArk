# -*- coding: UTF-8 -*-
"""医疗经营系统核心逻辑模块

该模块提供医疗经营的对外服务接口，并协调 `patient_management` 与
`hospital_flow` 两个子模块完成病人刷新、诊疗推进、药物扣除与住院手术。
"""
from __future__ import annotations

import math
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union

from Script.Config import config_def, game_config, normal_config
from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import handle_ability, handle_premise
from Script.UI.Moudle import draw
from Script.System.Medical import hospital_flow, medical_constant, patient_management, log_system

_MEDICAL_FACILITY_ID = 6
"""医疗部在 facility_level 字典中的设施 ID（来源于 Facility.csv）"""

_MEDICINE_RESOURCE_IDS: Tuple[int, ...] = medical_constant.ALL_MEDICINE_RESOURCE_IDS
"""医疗系统允许使用的全部药品资源 ID 列表"""

_FLOAT_EPSILON = 1e-6
"""浮点比较使用的安全阈值"""

_HOSPITAL_DOCTOR_BED_BONUS = 2
"""每名住院医生额外提供的床位数量"""

_PLAYER_METADATA_KEYS: Tuple[str, ...] = (
    "player_previous_state",
    "player_session_active",
    "player_used_checks",
    "player_confirmed_complications",
    "player_check_records",
    "player_pending_checks",
)
"""玩家诊疗流程使用的临时元数据键集合"""

_: Callable[[str], str] = get_text._

_GENERAL_SPECIALIZATION_KEY: str = medical_constant.SPECIALIZATION_GENERAL_KEY
"""医疗分科中的全科键值"""

_SPECIALIZATION_ROLES: Tuple[str, str] = (
    medical_constant.SPECIALIZATION_ROLE_CLINIC,
    medical_constant.SPECIALIZATION_ROLE_HOSPITAL,
)
"""受支持的医生岗位分科键顺序"""


def _bump_daily_counter(
    rhodes_island: Optional[game_type.Rhodes_Island],
    key: str,
    value: int,
) -> None:
    """在医疗日度统计表中累加指定键值"""

    if rhodes_island is None or value == 0:
        return
    stats = rhodes_island.__dict__.setdefault("medical_daily_counters", {})
    stats[key] = int(stats.get(key, 0) or 0) + int(value)


def _get_specialization_categories() -> List[Dict[str, Any]]:
    """返回按 system_id 排序的分科配置列表"""

    categories: List[Dict[str, Any]] = [
        {"key": _GENERAL_SPECIALIZATION_KEY, "name": _("全科"), "system_id": None}
    ]
    body_system_map = getattr(game_config, "config_medical_body_system_by_system", {}) or {}
    for system_id, part_map in sorted(body_system_map.items(), key=lambda item: item[0]):
        sample = next(iter(part_map.values()), None)
        system_name = getattr(sample, "system_name", str(system_id)) if sample else str(system_id)
        categories.append({"key": str(system_id), "name": system_name, "system_id": system_id})
    return categories


def get_specialization_categories() -> List[Dict[str, Any]]:
    """对外暴露的分科列表副本，供 UI 调用"""

    return [dict(item) for item in _get_specialization_categories()]


def _get_role_doctor_ids(rhodes_island: Optional[game_type.Rhodes_Island], role_key: str) -> List[int]:
    """根据岗位键获取对应医生 ID 列表副本"""

    if rhodes_island is None:
        return []
    if role_key == medical_constant.SPECIALIZATION_ROLE_CLINIC:
        return list(getattr(rhodes_island, "medical_clinic_doctor_ids", []) or [])
    if role_key == medical_constant.SPECIALIZATION_ROLE_HOSPITAL:
        return list(getattr(rhodes_island, "medical_hospital_doctor_ids", []) or [])
    return []


def _ensure_specialization_structure(rhodes_island: game_type.Rhodes_Island) -> None:
    """确保医生分科结构存在且成员与岗位医生保持一致"""

    if rhodes_island is None:
        return

    categories = _get_specialization_categories()
    category_keys = [item["key"] for item in categories]
    raw_spec = getattr(rhodes_island, "medical_doctor_specializations", {})
    if not isinstance(raw_spec, dict):
        raw_spec = {}

    normalized: Dict[str, Dict[str, List[int]]] = {}
    for role_key in _SPECIALIZATION_ROLES:
        doctor_ids = set(int(value) for value in _get_role_doctor_ids(rhodes_island, role_key))
        role_bucket = raw_spec.get(role_key)
        assigned_tracker: Dict[int, str] = {}
        if isinstance(role_bucket, dict):
            for category_key, doctor_list in role_bucket.items():
                if category_key not in category_keys:
                    continue
                for doctor_id in doctor_list or []:
                    if doctor_id in doctor_ids and doctor_id not in assigned_tracker:
                        assigned_tracker[int(doctor_id)] = category_key

        cleaned: Dict[str, List[int]] = {key: [] for key in category_keys}
        for doctor_id in doctor_ids:
            category_key = assigned_tracker.get(doctor_id, _GENERAL_SPECIALIZATION_KEY)
            cleaned.setdefault(category_key, []).append(int(doctor_id))

        for category_key in cleaned:
            cleaned[category_key] = sorted({int(value) for value in cleaned[category_key]})

        normalized[role_key] = cleaned

    rhodes_island.medical_doctor_specializations = normalized


def _resolve_doctor_specialization(
    rhodes_island: game_type.Rhodes_Island,
    role_key: str,
    doctor_id: int,
) -> str:
    """查询医生当前所属的分科键，未匹配时返回全科"""

    _ensure_specialization_structure(rhodes_island)
    role_bucket = getattr(rhodes_island, "medical_doctor_specializations", {}).get(role_key, {})
    for category_key, doctor_list in role_bucket.items():
        if doctor_id in doctor_list:
            return category_key
    return _GENERAL_SPECIALIZATION_KEY


def assign_doctor_specialization(
    role_key: str,
    doctor_id: int,
    category_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, Any]:
    """调整医生分科归属，返回执行结果摘要"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None or role_key not in _SPECIALIZATION_ROLES:
        return {"success": False, "reason": "invalid_role"}

    doctor_ids = _get_role_doctor_ids(rhodes_island, role_key)
    if doctor_id not in doctor_ids:
        return {"success": False, "reason": "doctor_not_in_role"}

    categories = _get_specialization_categories()
    category_keys = [item["key"] for item in categories]
    resolved_category = category_key if category_key in category_keys else _GENERAL_SPECIALIZATION_KEY

    _ensure_specialization_structure(rhodes_island)
    role_bucket = rhodes_island.medical_doctor_specializations.setdefault(role_key, {})
    for key in category_keys:
        current_list = role_bucket.setdefault(key, [])
        if doctor_id in current_list:
            current_list.remove(doctor_id)
    target_list = role_bucket.setdefault(resolved_category, [])
    target_list.append(doctor_id)
    role_bucket[resolved_category] = sorted({int(value) for value in target_list})

    _ensure_specialization_structure(rhodes_island)

    category_name = next((item["name"] for item in categories if item["key"] == resolved_category), resolved_category)
    return {
        "success": True,
        "role": role_key,
        "category_key": resolved_category,
        "category_name": category_name,
        "doctor_id": doctor_id,
    }


def list_role_doctors(
    role_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[int]:
    """返回指定岗位当前所有医生 ID 列表"""

    rhodes_island = _get_rhodes_island(target_base)
    return _get_role_doctor_ids(rhodes_island, role_key)


def get_doctor_specialization_overview(
    role_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[Dict[str, Any]]:
    """汇总指定岗位的分科配置，用于 UI 面板展示"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None or role_key not in _SPECIALIZATION_ROLES:
        return []

    _ensure_specialization_structure(rhodes_island)
    categories = _get_specialization_categories()
    role_bucket = rhodes_island.medical_doctor_specializations.get(role_key, {})
    character_table = getattr(cache_control.cache, "character_data", {})

    overview: List[Dict[str, Any]] = []
    for category in categories:
        doctor_ids = list(role_bucket.get(category["key"], []) or [])
        doctor_details: List[Dict[str, Any]] = []
        total_level = 0
        total_adjust = 0.0
        total_bonus = 0.0
        for doctor_id in doctor_ids:
            character = character_table.get(doctor_id)
            if character is None:
                continue
            ability_level = int(character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)
            ability_adjust = float(handle_ability.get_ability_adjust(ability_level))
            bonus_multiplier = 1.0 + ability_level * medical_constant.SPECIALIZATION_BONUS_PER_LEVEL
            total_level += ability_level
            total_adjust += ability_adjust
            total_bonus += bonus_multiplier
            doctor_details.append(
                {
                    "id": doctor_id,
                    "name": getattr(character, "name", str(doctor_id)),
                    "ability_level": ability_level,
                    "ability_adjust": ability_adjust,
                    "bonus_multiplier": bonus_multiplier,
                }
            )

        average_bonus = total_bonus / len(doctor_details) if doctor_details else 1.0
        overview.append(
            {
                "category_key": category["key"],
                "category_name": category["name"],
                "system_id": category["system_id"],
                "doctor_ids": doctor_ids,
                "doctor_details": doctor_details,
                "doctor_count": len(doctor_details),
                "total_ability_level": total_level,
                "total_ability_adjust": total_adjust,
                "average_bonus_multiplier": average_bonus,
            }
        )

    return overview


def _resolve_patient_system_keys(patient: medical_constant.MedicalPatient) -> Set[str]:
    """提取病人涉及的系统键集合，并同步写入 metadata"""

    system_keys: Set[str] = set()
    if patient is None:
        return system_keys

    trace = patient.metadata.get("complication_trace", []) or []
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
        patient.metadata["system_keys"] = sorted(system_keys)
    else:
        patient.metadata.setdefault("system_keys", [])
    return system_keys


def _resolve_specialization_bonus(
    rhodes_island: game_type.Rhodes_Island,
    role_key: str,
    doctor_character: Optional[game_type.Character],
    patient: Optional[medical_constant.MedicalPatient],
) -> Tuple[str, bool, float]:
    """计算医生匹配分科后是否命中病人系统以及额外倍率"""

    if rhodes_island is None or doctor_character is None or patient is None:
        return (_GENERAL_SPECIALIZATION_KEY, True, 1.0)

    specialization_key = _resolve_doctor_specialization(rhodes_island, role_key, doctor_character.cid)
    if specialization_key == _GENERAL_SPECIALIZATION_KEY:
        return (specialization_key, True, 1.0)

    system_keys = _resolve_patient_system_keys(patient)
    if specialization_key not in system_keys:
        return (specialization_key, False, 1.0)

    ability_level = int(doctor_character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)
    bonus_multiplier = 1.0 + max(ability_level, 0) * medical_constant.SPECIALIZATION_BONUS_PER_LEVEL
    return (specialization_key, True, bonus_multiplier)


def acquire_patient_for_doctor(
    doctor_character: Optional[game_type.Character],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Optional[medical_constant.MedicalPatient]:
    """为执行诊疗的医生分配一名待诊病人

    参数:
        doctor_character (Optional[game_type.Character]): 负责诊疗的干员对象。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地，缺省时使用全局缓存。

    返回:
        Optional[medical_constant.MedicalPatient]: 分配到的病人，若无候选则返回 None。
    """

    if doctor_character is None:
        return None

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return None

    patient_table = rhodes_island.medical_patients_today
    if not patient_table:
        return None

    specialization_key = _resolve_doctor_specialization(
        rhodes_island,
        medical_constant.SPECIALIZATION_ROLE_CLINIC,
        doctor_character.cid,
    )
    requires_match = specialization_key != _GENERAL_SPECIALIZATION_KEY

    # 优先复用已记录的病人 ID
    assigned_id = getattr(getattr(doctor_character, "work", None), "medical_patient_id", 0)
    if assigned_id:
        patient = patient_table.get(assigned_id)
        if patient and patient.state not in (
            medical_constant.MedicalPatientState.WAITING_MEDICATION,
            medical_constant.MedicalPatientState.HOSPITALIZED,
            medical_constant.MedicalPatientState.DISCHARGED,
        ):
            if requires_match:
                system_keys = set(patient.metadata.get("system_keys", []))
                if not system_keys:
                    system_keys = _resolve_patient_system_keys(patient)
                if specialization_key not in system_keys:
                    patient.metadata.pop("assigned_doctor_id", None)
                    if hasattr(doctor_character, "work"):
                        doctor_character.work.medical_patient_id = 0
                else:
                    patient.metadata["assigned_doctor_id"] = doctor_character.cid
                    doctor_character.work.medical_patient_id = patient.patient_id
                    return patient
            else:
                patient.metadata["assigned_doctor_id"] = doctor_character.cid
                doctor_character.work.medical_patient_id = patient.patient_id
                return patient

    # 挑选尚未分配且允许诊疗的病人（默认按病情等级倒序）
    available: List[medical_constant.MedicalPatient] = []
    for patient in patient_table.values():
        if patient.state not in (
            medical_constant.MedicalPatientState.REFRESHED,
            medical_constant.MedicalPatientState.IN_TREATMENT,
        ):
            continue
        assigned_doctor = patient.metadata.get("assigned_doctor_id")
        if assigned_doctor and assigned_doctor != doctor_character.cid:
            continue
        if requires_match:
            system_keys = set(patient.metadata.get("system_keys", []))
            if not system_keys:
                system_keys = _resolve_patient_system_keys(patient)
            if specialization_key not in system_keys:
                continue
        available.append(patient)

    if not available:
        return None

    patient = _select_triage_candidate(available, rhodes_island)
    if patient is None:
        return None
    patient.metadata["assigned_doctor_id"] = doctor_character.cid
    doctor_character.work.medical_patient_id = patient.patient_id
    return patient


def _acquire_hospital_patient_for_doctor(
    doctor_character: Optional[game_type.Character],
    rhodes_island: Optional[game_type.Rhodes_Island],
    *,
    require_surgery: bool = False,
) -> Optional[medical_constant.MedicalPatient]:
    """为住院医生挑选病房病人，可选仅匹配待手术患者"""

    if doctor_character is None or rhodes_island is None:
        return None

    patient_table = rhodes_island.medical_hospitalized
    if not patient_table:
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0
        return None

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

    candidates: List[medical_constant.MedicalPatient] = []
    for patient in patient_table.values():
        if patient.state != medical_constant.MedicalPatientState.HOSPITALIZED:
            continue
        if require_surgery and (not patient.need_surgery or patient.surgery_blocked):
            continue
        assigned = int(patient.metadata.get("assigned_hospital_doctor_id", 0) or 0)
        if assigned and assigned != doctor_character.cid:
            continue
        candidates.append(patient)

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

    patient = min(candidates, key=_hospital_priority)
    patient.metadata["assigned_hospital_doctor_id"] = doctor_character.cid
    if work_data is not None:
        work_data.medical_patient_id = patient.patient_id
    return patient


def _resolve_triage_mode(
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> medical_constant.MedicalPatientPriority:
    """解析基地当前的病人接诊优先策略"""

    if rhodes_island is None:
        return medical_constant.MedicalPatientPriority.NORMAL
    raw_mode = getattr(
        rhodes_island,
        "medical_patient_priority_mode",
        medical_constant.MedicalPatientPriority.NORMAL.value,
    )
    try:
        mode = medical_constant.MedicalPatientPriority(str(raw_mode))
    except ValueError:
        rhodes_island.medical_patient_priority_mode = medical_constant.MedicalPatientPriority.NORMAL.value
        return medical_constant.MedicalPatientPriority.NORMAL
    rhodes_island.medical_patient_priority_mode = mode.value
    return mode


def _select_triage_candidate(
    candidates: List[medical_constant.MedicalPatient],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> Optional[medical_constant.MedicalPatient]:
    """依据当前优先策略挑选最匹配的病人，避免在大列表上全量排序"""

    if not candidates:
        return None

    mode = _resolve_triage_mode(rhodes_island)
    if mode == medical_constant.MedicalPatientPriority.FOCUS_MILD:
        key_func = lambda target: (
            int(getattr(target, "severity_level", 0) or 0),
            float(getattr(target, "diagnose_progress", 0.0) or 0.0),
            target.patient_id,
        )
        return min(candidates, key=key_func)

    key_func = lambda target: (
        -int(getattr(target, "severity_level", 0) or 0),
        -float(getattr(target, "diagnose_progress", 0.0) or 0.0),
        target.patient_id,
    )
    return min(candidates, key=key_func)


def _clear_player_session_metadata(patient: medical_constant.MedicalPatient) -> None:
    """清理玩家诊疗流程写入的临时元数据"""

    if patient is None:
        return
    for key in _PLAYER_METADATA_KEYS:
        patient.metadata.pop(key, None)


def _acquire_patient_for_player(
    doctor_character: Optional[game_type.Character],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> Optional[medical_constant.MedicalPatient]:
    """根据当前优先策略为玩家诊疗会话选定病人"""

    if rhodes_island is None:
        return None

    # 若已有会话使用中的病人则直接复用
    current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
    if current_id:
        patient = rhodes_island.medical_patients_today.get(current_id)
        if patient is not None:
            return patient

    candidates: List[medical_constant.MedicalPatient] = []
    for patient in rhodes_island.medical_patients_today.values():
        if patient.state not in {
            medical_constant.MedicalPatientState.REFRESHED,
            medical_constant.MedicalPatientState.IN_TREATMENT,
            medical_constant.MedicalPatientState.IN_TREATMENT_PLAYER,
        }:
            continue
        assigned_doctor = int(patient.metadata.get("assigned_doctor_id", 0) or 0)
        # 已被其他医生认领的病人不进入候选
        if doctor_character is not None and assigned_doctor not in {0, doctor_character.cid}:
            continue
        candidates.append(patient)

    if not candidates:
        return None

    return _select_triage_candidate(candidates, rhodes_island)


def start_player_diagnose_session(
    doctor_character: Optional[game_type.Character] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Optional[medical_constant.MedicalPatient]:
    """初始化玩家诊疗会话并返回被选中的病人"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return None

    if doctor_character is None:
        doctor_character = getattr(cache_control.cache, "character_data", {}).get(0)

    if doctor_character is None:
        return None

    patient = _acquire_patient_for_player(doctor_character, rhodes_island)
    if patient is None:
        return None

    if not patient.metadata.get("player_session_active"):
        patient.metadata["player_previous_state"] = patient.state.value
        patient.metadata["player_session_active"] = True
        patient.metadata["player_used_checks"] = 0
        patient.metadata["player_confirmed_complications"] = []
        patient.metadata["player_check_records"] = []
        patient.metadata["player_pending_checks"] = []

    patient.metadata["assigned_doctor_id"] = doctor_character.cid if doctor_character is not None else 0
    set_patient_state(patient, medical_constant.MedicalPatientState.IN_TREATMENT_PLAYER)
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
    """终止玩家诊疗会话并恢复病人原始状态"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    if patient is None:
        current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
        if current_id:
            patient = rhodes_island.medical_patients_today.get(current_id)

    if patient is None:
        return

    previous_state = patient.metadata.get("player_previous_state")
    if previous_state:
        try:
            patient.state = medical_constant.MedicalPatientState(previous_state)
        except ValueError:
            patient.state = medical_constant.MedicalPatientState.REFRESHED
    patient.metadata.pop("assigned_doctor_id", None)

    _clear_player_session_metadata(patient)
    rhodes_island.medical_player_current_patient_id = 0

    if doctor_character is None:
        doctor_character = getattr(cache_control.cache, "character_data", {}).get(0)
    if doctor_character is not None and hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = 0


def commit_player_diagnose_session(
    doctor_character: Optional[game_type.Character] = None,
    *,
    patient: Optional[medical_constant.MedicalPatient] = None,
    apply_medicine: bool = True,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """完成玩家诊疗流程并返回结算摘要"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    if doctor_character is None:
        doctor_character = getattr(cache_control.cache, "character_data", {}).get(0)

    if doctor_character is None:
        return {"success": False, "reason": "no_doctor"}

    if patient is None:
        current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
        if current_id:
            patient = rhodes_island.medical_patients_today.get(current_id)

    if patient is None:
        return {"success": False, "reason": "no_patient"}

    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return {"success": False, "reason": "no_severity_config"}

    base_hours = max(float(severity_config.base_hours or 0.0), 0.1)
    patient.diagnose_progress = max(float(patient.diagnose_progress or 0.0), base_hours - 0.1)
    patient.metadata["assigned_doctor_id"] = doctor_character.cid if doctor_character is not None else 0

    income_before = float(rhodes_island.medical_income_today or 0.0)
    advance_diagnose(patient.patient_id, doctor_character, target_base=rhodes_island)
    income_mid = float(rhodes_island.medical_income_today or 0.0)
    diagnose_income = int(round(income_mid - income_before))

    medicine_income = 0
    medicine_success = False
    if apply_medicine:
        income_before_medicine = float(rhodes_island.medical_income_today or 0.0)
        medicine_success = try_consume_medicine(patient, target_base=rhodes_island)
        income_after_medicine = float(rhodes_island.medical_income_today or 0.0)
        medicine_income = int(round(income_after_medicine - income_before_medicine))

    _clear_player_session_metadata(patient)
    rhodes_island.medical_player_current_patient_id = 0

    if doctor_character is not None and hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = 0

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
    """执行玩家选择的检查条目并记录结果"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    if patient is None:
        current_id = int(getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0)
        if current_id:
            patient = rhodes_island.medical_patients_today.get(current_id)

    if patient is None:
        return {"success": False, "reason": "no_patient"}

    if not selections:
        return {"success": False, "reason": "empty_selection"}

    used_checks = int(patient.metadata.get("player_used_checks", 0) or 0) + 1
    patient.metadata["player_used_checks"] = used_checks

    confirmed_set: Set[int] = set(int(cid) for cid in patient.metadata.get("player_confirmed_complications", []))
    actual_complications: Set[int] = {int(cid) for cid in getattr(patient, "complications", [])}

    trace_info: List[Dict[str, int]] = [
        {
            "system_id": int(entry.get("system_id", 0)),
            "part_id": int(entry.get("part_id", 0)),
            "severity_level": int(entry.get("severity_level", 0)),
            "cid": int(entry.get("cid", entry.get("complication_id", 0))),
        }
        for entry in patient.metadata.get("complication_trace", [])
    ]

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

        if comp_id and comp_id in actual_complications:
            result_type = "positive"
            confirmed_set.add(comp_id)
            message = getattr(config_entry, "exam_result_positive", "") if config_entry else ""
            if not message:
                message = _("检查结果提示确诊，请准备治疗方案。")
        else:
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

    previous_records: List[Dict[str, object]] = list(patient.metadata.get("player_check_records", []))
    previous_records.extend(records)
    patient.metadata["player_check_records"] = previous_records[-30:]
    patient.metadata["player_confirmed_complications"] = sorted(confirmed_set)
    patient.metadata["player_pending_checks"] = []

    return {
        "success": True,
        "results": records,
        "used_checks": used_checks,
    }


def build_player_check_catalog(
    patient: Optional[medical_constant.MedicalPatient],
) -> Dict[int, Dict[str, object]]:
    """构建玩家诊疗用的系统/部位/并发症选择树"""

    if patient is None:
        return {}

    # 构建可选并发症目录
    catalog: Dict[int, Dict[str, object]] = {}
    # 遍历所有系统
    for system_id, part_map in sorted(game_config.config_medical_body_system_by_system.items()):
        if not isinstance(part_map, dict) or not part_map:
            continue

        # 获取系统名称
        first_entry = next(iter(part_map.values()), None)
        system_name = getattr(first_entry, "system_name", f"System {system_id}") if first_entry else f"System {system_id}"

        # 遍历系统内所有部位
        part_catalog: Dict[int, Dict[str, object]] = {}
        for part_id, part_info in sorted(part_map.items()):
            if part_info is None:
                continue
            # 调试打印部位信息
            # print(f"Building catalog for System {system_id}，部位名称: {getattr(part_info, 'part_name', part_id)}，部位性别限制: {getattr(part_info, 'gender_limit')}")
            # 获取部位对应的并发症列表
            complication_map = game_config.config_medical_complication_detail.get(system_id, {}).get(part_id, {})
            options: List[Dict[str, object]] = []
            for severity_level in sorted(complication_map.keys()):
                for comp in complication_map[severity_level]:
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
    """估算玩家当前病人的诊疗收益与药品需求摘要"""

    # 验证病人有效性
    if patient is None:
        return {"success": False, "reason": "no_patient"}

    # 获取当前基地与病情配置
    rhodes_island = _get_rhodes_island(target_base)
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return {"success": False, "reason": "no_severity_config"}

    # 计算诊疗收益
    price_ratio = get_medical_price_ratio(target_base=rhodes_island) # 价格系数
    income_multiplier = patient_management.resolve_price_income_multiplier(price_ratio) # 收益倍率
    # 诊断收益
    diagnose_income = int(
        round(float(severity_config.diagnose_income or 0) * price_ratio * income_multiplier)
    )

    medicine_income_ratio = float(severity_config.medicine_income_ratio or 0.0)
    predicted_medicine_income = 0.0
    resource_summary: List[Dict[str, object]] = []
    for resource_id, amount in patient.need_resources.items():
        need_value = float(amount or 0.0)
        if need_value <= 0:
            continue
        resource_config = game_config.config_resouce.get(resource_id)
        unit_price = float(getattr(resource_config, "price", 0.0) or 0.0)
        predicted_medicine_income += unit_price * need_value * medicine_income_ratio * price_ratio * income_multiplier
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


def prepare_doctor_medical_behavior(
    doctor_character: Optional[game_type.Character],
    behavior_id: Optional[str],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Optional[medical_constant.MedicalPatient]:
    """在行为开始时为医生预分配对应病人，便于结算阶段继续处理"""

    if doctor_character is None or not behavior_id:
        return None

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return None

    if behavior_id == constant.Behavior.CURE_PATIENT:
        return acquire_patient_for_doctor(doctor_character, target_base=rhodes_island)
    if behavior_id == getattr(constant.Behavior, "WARD_ROUND", "ward_round"):
        return _acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=False)
    if behavior_id == getattr(constant.Behavior, "PERFORM_SURGERY", "perform_surgery"):
        return _acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=True)
    return None


def conduct_ward_round(
    doctor_character: Optional[game_type.Character],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """执行住院查房流程，返回处理结果摘要"""

    rhodes_island = _get_rhodes_island(target_base)
    if doctor_character is None or rhodes_island is None:
        return {"handled": False, "patient": None, "result": "no_doctor"}

    patient = _acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=False)
    if patient is None:
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0
        return {"handled": False, "patient": None, "result": "no_candidate"}

    def _consume(target_patient: medical_constant.MedicalPatient) -> bool:
        return try_consume_medicine(target_patient, is_hospitalized=True, target_base=rhodes_island)

    outcome = hospital_flow.process_single_hospitalized_patient(
        rhodes_island,
        patient,
        _consume,
        doctor=doctor_character,
    )
    outcome["patient"] = patient

    if patient.state != medical_constant.MedicalPatientState.HOSPITALIZED:
        patient.metadata.pop("assigned_hospital_doctor_id", None)
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0

    _sync_legacy_patient_counters(rhodes_island)
    return outcome


def perform_surgery_for_doctor(
    doctor_character: Optional[game_type.Character],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, object]:
    """尝试为住院患者安排手术，返回执行结果"""

    rhodes_island = _get_rhodes_island(target_base)
    if doctor_character is None or rhodes_island is None:
        return {"patient": None, "success": False, "result": "no_doctor"}

    patient = _acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=True)
    if patient is None:
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0
        return {"patient": None, "success": False, "result": "no_candidate"}

    severity_before = int(getattr(patient, "severity_level", 0) or 0)
    income_before = int(rhodes_island.medical_income_today)
    success = hospital_flow.attempt_surgery(rhodes_island, patient, doctor_character)
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

    if success or patient.surgery_blocked or not patient.need_surgery:
        patient.metadata.pop("assigned_hospital_doctor_id", None)
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0

    _sync_legacy_patient_counters(rhodes_island)
    return result


def _sync_legacy_patient_counters(rhodes_island: game_type.Rhodes_Island) -> None:
    """同步旧版医疗统计字段，兼容尚未迁移的 UI 逻辑"""

    if rhodes_island is None:
        return
    waiting_states = {
        medical_constant.MedicalPatientState.REFRESHED,
        medical_constant.MedicalPatientState.IN_TREATMENT,
        medical_constant.MedicalPatientState.IN_TREATMENT_PLAYER,
    }
    waiting_count = sum(
        1
        for patient in rhodes_island.medical_patients_today.values()
        if patient.state in waiting_states
    )
    rhodes_island.patient_now = waiting_count


def update_doctor_assignments(
    clinic_doctors: Optional[List[int]] = None,
    hospital_doctors: Optional[List[int]] = None,
    *,
    clinic_power: Optional[float] = None,
    hospital_power: Optional[float] = None,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """刷新医疗部医生相关缓存并重新计算床位上限"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    if clinic_doctors is not None:
        rhodes_island.medical_clinic_doctor_ids = list(clinic_doctors)
        resolved_power = clinic_power if clinic_power is not None else _calculate_doctor_power(clinic_doctors)
        rhodes_island.medical_clinic_doctor_power = float(resolved_power)
    else:
        rhodes_island.medical_clinic_doctor_ids = list(
            getattr(rhodes_island, "medical_clinic_doctor_ids", []) or []
        )
        rhodes_island.medical_clinic_doctor_power = float(
            getattr(rhodes_island, "medical_clinic_doctor_power", 0.0) or 0.0
        )

    if hospital_doctors is not None:
        rhodes_island.medical_hospital_doctor_ids = list(hospital_doctors)
        resolved_power = hospital_power if hospital_power is not None else _calculate_doctor_power(hospital_doctors)
        rhodes_island.medical_hospital_doctor_power = float(resolved_power)
    else:
        rhodes_island.medical_hospital_doctor_ids = list(
            getattr(rhodes_island, "medical_hospital_doctor_ids", []) or []
        )
        rhodes_island.medical_hospital_doctor_power = float(
            getattr(rhodes_island, "medical_hospital_doctor_power", 0.0) or 0.0
        )

    rhodes_island.medical_bed_limit = _calculate_medical_bed_limit(rhodes_island)
    _ensure_specialization_structure(rhodes_island)


def dispatch_medical_doctors(
    clinic_target: Optional[int] = None,
    hospital_target: Optional[int] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
    assign_work_func: Optional[Callable[[int, int], bool]] = None,
    refresh_callbacks: Optional[Iterable[Callable[[], None]]] = None,
) -> Dict[str, int]:
    """自动分配医疗部医生并输出执行结果摘要。

    功能说明:
        根据目标数量从现有干员中挑选适合的门诊医生与住院医生，必要时通过
        ``assign_work_func`` 修改干员的当前工作，并在结束时执行 ``refresh_callbacks``
        以刷新衍生缓存。

    参数:
        clinic_target (Optional[int]): 期望的门诊医生数量；``None`` 时沿用基地设置或现有人数。
        hospital_target (Optional[int]): 期望的住院医生数量；``None`` 时沿用基地设置或现有人数。
        target_base (Optional[game_type.Rhodes_Island]): 指定目标基地，缺省时使用全局缓存。
        assign_work_func (Optional[Callable[[int, int], bool]]): 负责调整干员岗位的回调，
            传入 ``(角色ID, 工作类型ID)``；未提供时仅计算方案而不真正变更岗位。
        refresh_callbacks (Optional[Iterable[Callable[[], None]]]): 岗位调整后需要调用的刷新函数
            列表，用于重算工作统计或 UI 数据。

    返回:
        Dict[str, int]:
            - ``clinic_target`` / ``hospital_target``: 解析后的目标数量；
            - ``clinic_assigned`` / ``hospital_assigned``: 实际分配到位的医生数量；
            - ``clinic_shortage`` / ``hospital_shortage``: 当前缺口；
            - ``changes``: 本次岗位调整次数。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {
            "clinic_target": int(clinic_target or 0),
            "hospital_target": int(hospital_target or 0),
            "clinic_assigned": 0,
            "hospital_assigned": 0,
            "clinic_shortage": int(clinic_target or 0),
            "hospital_shortage": int(hospital_target or 0),
            "changes": 0,
        }

    # --- 阶段一：解析目标配置与默认值 ---
    fallback_clinic_target = rhodes_island.medical_clinic_doctor_target or len(rhodes_island.medical_clinic_doctor_ids)
    fallback_hospital_target = rhodes_island.medical_hospital_doctor_target or len(
        rhodes_island.medical_hospital_doctor_ids
    )
    resolved_clinic_target = fallback_clinic_target if clinic_target is None else clinic_target
    resolved_hospital_target = fallback_hospital_target if hospital_target is None else hospital_target
    resolved_clinic_target = max(int(resolved_clinic_target), 0)
    resolved_hospital_target = max(int(resolved_hospital_target), 0)

    # --- 阶段二：收集候选医生列表 ---
    cache = cache_control.cache
    clinic_work_id = medical_constant.MedicalDoctorProfession.CLINICIAN.value
    hospital_work_id = medical_constant.MedicalDoctorProfession.HOSPITALIST.value
    candidates: List[Tuple[int, int, int]] = []
    for npc_id in list(cache.npc_id_got):
        if not _is_medical_doctor_candidate(npc_id, target_base=rhodes_island):
            continue
        character = cache.character_data[npc_id]
        ability = int(character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)
        candidates.append((npc_id, ability, character.work.work_type))

    # --- 阶段三：分别对门诊与住院需求进行排序 ---
    hospital_sorted = sorted(
        candidates,
        key=lambda record: (
            -int(record[2] == hospital_work_id),
            -int(record[2] == clinic_work_id),
            -record[1],
            record[0],
        ),
    )
    clinic_sorted = sorted(
        candidates,
        key=lambda record: (
            -int(record[2] == clinic_work_id),
            -int(record[2] == hospital_work_id),
            -record[1],
            record[0],
        ),
    )

    # --- 阶段四：挑选最终岗位人选 ---
    used_ids: Set[int] = set()
    final_hospital_ids: List[int] = []
    for npc_id, _ability, _work_type in hospital_sorted:
        if npc_id in used_ids:
            continue
        final_hospital_ids.append(npc_id)
        used_ids.add(npc_id)
        if len(final_hospital_ids) >= resolved_hospital_target:
            break

    final_clinic_ids: List[int] = []
    for npc_id, _ability, _work_type in clinic_sorted:
        if npc_id in used_ids:
            continue
        final_clinic_ids.append(npc_id)
        used_ids.add(npc_id)
        if len(final_clinic_ids) >= resolved_clinic_target:
            break

    # --- 阶段五：对比当前岗位并记录变更 ---
    final_hospital_set = set(final_hospital_ids)
    final_clinic_set = set(final_clinic_ids)
    current_hospital_set = set(rhodes_island.medical_hospital_doctor_ids)
    current_clinic_set = set(rhodes_island.medical_clinic_doctor_ids)
    removed_ids = (current_hospital_set - final_hospital_set) | (current_clinic_set - final_clinic_set)
    changes = 0

    # --- 阶段六：执行岗位调整与刷新 ---
    if assign_work_func is not None:
        for npc_id in removed_ids:
            current = cache.character_data.get(npc_id)
            current_work = getattr(getattr(current, "work", None), "work_type", 0) if current else 0
            if current_work and assign_work_func(npc_id, 0):
                changes += 1
        for npc_id in final_clinic_set:
            current = cache.character_data.get(npc_id)
            current_work = getattr(getattr(current, "work", None), "work_type", 0) if current else 0
            if current_work != clinic_work_id and assign_work_func(npc_id, clinic_work_id):
                changes += 1
        for npc_id in final_hospital_set:
            current = cache.character_data.get(npc_id)
            current_work = getattr(getattr(current, "work", None), "work_type", 0) if current else 0
            if current_work != hospital_work_id and assign_work_func(npc_id, hospital_work_id):
                changes += 1

    rhodes_island.medical_clinic_doctor_target = resolved_clinic_target
    rhodes_island.medical_hospital_doctor_target = resolved_hospital_target

    if refresh_callbacks:
        for callback in refresh_callbacks:
            callback()

    _ensure_specialization_structure(rhodes_island)

    # --- 阶段七：汇总最终分配统计 ---
    actual_clinic = len(rhodes_island.medical_clinic_doctor_ids)
    actual_hospital = len(rhodes_island.medical_hospital_doctor_ids)
    clinic_shortage = max(0, resolved_clinic_target - actual_clinic)
    hospital_shortage = max(0, resolved_hospital_target - actual_hospital)

    return {
        "clinic_target": resolved_clinic_target,
        "hospital_target": resolved_hospital_target,
        "clinic_assigned": actual_clinic,
        "hospital_assigned": actual_hospital,
        "clinic_shortage": clinic_shortage,
        "hospital_shortage": hospital_shortage,
        "changes": changes,
    }


def adjust_doctor_targets_by_delta(
    clinic_delta: int = 0,
    hospital_delta: int = 0,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, int]:
    """根据增量调整医疗部医生目标人数并触发自动排班

    参数:
        clinic_delta (int): 需要增减的门诊医生数量，可为负数。
        hospital_delta (int): 需要增减的住院医生数量，可为负数。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地对象，缺省时使用全局缓存。

    返回:
        Dict[str, int]: 同 `dispatch_medical_doctors` 的排班汇总，用于 UI 展示。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return dispatch_medical_doctors(
            clinic_target=max(int(clinic_delta or 0), 0),
            hospital_target=max(int(hospital_delta or 0), 0),
            target_base=None,
        )

    current_clinic_target = rhodes_island.medical_clinic_doctor_target or len(
        rhodes_island.medical_clinic_doctor_ids
    )
    current_hospital_target = rhodes_island.medical_hospital_doctor_target or len(
        rhodes_island.medical_hospital_doctor_ids
    )

    resolved_clinic_target = max(int(current_clinic_target + clinic_delta), 0)
    resolved_hospital_target = max(int(current_hospital_target + hospital_delta), 0)

    return dispatch_medical_doctors(
        clinic_target=resolved_clinic_target,
        hospital_target=resolved_hospital_target,
        target_base=rhodes_island,
    )


def redo_medical_doctor_dispatch(
    *, target_base: Optional[game_type.Rhodes_Island] = None
) -> Dict[str, int]:
    """在保持当前目标数量的前提下重新执行一次自动排班"""

    rhodes_island = _get_rhodes_island(target_base)
    return dispatch_medical_doctors(target_base=rhodes_island)


def summarize_dispatch_result(result: Optional[Dict[str, int]]) -> str:
    """将排班结果转化为可读文本，便于面板直接展示"""

    if not result:
        return "未取得排班结果。\n"

    clinic_target = int(result.get("clinic_target", 0))
    hospital_target = int(result.get("hospital_target", 0))
    clinic_assigned = int(result.get("clinic_assigned", 0))
    hospital_assigned = int(result.get("hospital_assigned", 0))
    clinic_shortage = max(int(result.get("clinic_shortage", 0)), 0)
    hospital_shortage = max(int(result.get("hospital_shortage", 0)), 0)
    changes = int(result.get("changes", 0))

    summary_lines = [
        f"门诊目标：{clinic_target} 人 | 已派：{clinic_assigned} 人 | 缺口：{clinic_shortage} 人",
        f"住院目标：{hospital_target} 人 | 已派：{hospital_assigned} 人 | 缺口：{hospital_shortage} 人",
        f"本次岗位调整 {changes} 次。",
    ]
    return "\n".join(summary_lines) + "\n"


def _is_medical_doctor_candidate(
    character_id: int,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """判定干员是否满足自动分配为医疗部医生的条件。

    功能说明:
        检查干员是否处于可用状态、岗位为空或已在医疗部、未处于访客/异常状态，
        并通过基础健康状况前提验证。

    参数:
        character_id (int): 待评估的干员角色 ID。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地，缺省时使用全局缓存。

    返回:
        bool: ``True`` 表示干员可加入医疗部自动调度；``False`` 表示需跳过。
    """

    if character_id == 0:
        return False

    cache = cache_control.cache
    if character_id not in cache.character_data:
        return False

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    character = cache.character_data[character_id]
    work_type = getattr(character, "work", None)
    work_id = getattr(work_type, "work_type", 0) if work_type is not None else 0
    clinic_work_id = medical_constant.MedicalDoctorProfession.CLINICIAN.value
    hospital_work_id = medical_constant.MedicalDoctorProfession.HOSPITALIST.value

    # 仅允许目前空闲或已经在医疗部的干员进入候选列表
    if work_id not in {0, clinic_work_id, hospital_work_id}:
        return False

    # 排除访客或临时客座干员
    visitor_info = getattr(rhodes_island, "visitor_info", {})
    if character_id in visitor_info:
        return False

    # 通过基础状态预判（健康、意识清醒等）
    if not handle_premise.handle_normal_2(character_id):
        return False
    if not handle_premise.handle_normal_7(character_id):
        return False

    return True


def init_medical_department_data(
    target_base: Optional[game_type.Rhodes_Island] = None,
    *,
    reset_runtime: bool = True,
    migrate_legacy: bool = False,
) -> None:
    """初始化医疗系统相关的运行期数据结构"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    if migrate_legacy:
        _migrate_legacy_income(rhodes_island)

    if reset_runtime:
        rhodes_island.medical_patients_today = {}
        rhodes_island.medical_hospitalized = {}
        rhodes_island.medical_surgery_records = []
        rhodes_island.medical_inventory_accumulator = {
            resource_id: 0.0 for resource_id in _MEDICINE_RESOURCE_IDS
        }
        rhodes_island.medical_income_today = 0
        rhodes_island.medical_income_total = 0
        rhodes_island.medical_daily_counters = {}
        rhodes_island.medical_recent_reports = []
        rhodes_island.medical_clinic_doctor_ids = []
        rhodes_island.medical_clinic_doctor_power = 0.0
        rhodes_island.medical_hospital_doctor_ids = []
        rhodes_island.medical_hospital_doctor_power = 0.0
        rhodes_island.medical_clinic_doctor_target = 0
        rhodes_island.medical_hospital_doctor_target = 0
        rhodes_island.medical_patient_priority_mode = medical_constant.MedicalPatientPriority.NORMAL.value
        rhodes_island.medical_player_current_patient_id = 0
        rhodes_island.medical_doctor_specializations = {}
    else:
        _ensure_runtime_dict(rhodes_island)
        rhodes_island.medical_player_current_patient_id = int(
            getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0
        )

    _ensure_specialization_structure(rhodes_island)

    if not rhodes_island.medical_price_ratio or rhodes_island.medical_price_ratio <= 0:
        rhodes_island.medical_price_ratio = _resolve_default_price_ratio()

    rhodes_island.medical_bed_limit = _calculate_medical_bed_limit(rhodes_island)
    _sync_legacy_patient_counters(rhodes_island)

    # 当日病人列表需要确保在初始化阶段就绪：
    # - 若刚刚重置运行时数据，列表必定为空，需要立刻刷新。
    # - 若读取旧档（reset_runtime=False），仅在当前队列为空时补充，避免重复生成。
    patient_table = getattr(rhodes_island, "medical_patients_today", {})
    should_refresh_patients = reset_runtime or not patient_table
    if should_refresh_patients:
        refresh_medical_patients(target_base=rhodes_island)


def update_medical_save_data_structure(cache_snapshot: Dict[str, Any]) -> None:
    """在读取旧存档时修复医疗系统相关字段"""

    rhodes_island = cache_snapshot.get("rhodes_island")
    if not isinstance(rhodes_island, game_type.Rhodes_Island):
        return

    init_medical_department_data(rhodes_island, reset_runtime=False, migrate_legacy=True)


def refresh_medical_patients(
    level: Optional[int] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[medical_constant.MedicalPatient]:
    """根据医疗部等级刷新当日病人列表"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return []

    level_value = level if level is not None else _get_medical_facility_level(rhodes_island)
    level_config = _pick_hospital_level_config(level_value)
    if level_config is None:
        return []

    refresh_count = _calculate_patient_refresh_count(rhodes_island, level_config)
    if refresh_count <= 0:
        return []

    new_patients: List[medical_constant.MedicalPatient] = []
    patient_table = get_patient_table(target_base=rhodes_island, hospitalized=False)

    for _ in range(refresh_count):
        severity_level = patient_management.pick_severity_level(level_value)
        if severity_level is None:
            break
        patient = patient_management.generate_patient(severity_level, rhodes_island)
        if patient is None:
            continue
        patient_table[patient.patient_id] = patient
        new_patients.append(patient)

    _sync_legacy_patient_counters(rhodes_island)
    return new_patients


def advance_diagnose(
    patient_id: int,
    doctor_character: game_type.Character,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """推进病人的诊疗进度并在完成时发放诊疗收入"""

    if doctor_character is None:
        return

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    patient, hospitalized = _locate_patient(patient_id, rhodes_island)
    if patient is None or hospitalized:
        return

    if hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = patient.patient_id

    if patient.state in (
        medical_constant.MedicalPatientState.WAITING_MEDICATION,
        medical_constant.MedicalPatientState.HOSPITALIZED,
        medical_constant.MedicalPatientState.DISCHARGED,
    ):
        if patient.metadata.get("assigned_doctor_id") == doctor_character.cid:
            patient.metadata.pop("assigned_doctor_id", None)
        if hasattr(doctor_character, "work"):
            doctor_character.work.medical_patient_id = 0
        _sync_legacy_patient_counters(rhodes_island)
        return

    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        if hasattr(doctor_character, "work"):
            doctor_character.work.medical_patient_id = 0
        patient.metadata.pop("assigned_doctor_id", None)
        _sync_legacy_patient_counters(rhodes_island)
        return

    base_hours = float(severity_config.base_hours)
    if base_hours <= 0:
        set_patient_state(patient, medical_constant.MedicalPatientState.WAITING_MEDICATION)
        if patient.metadata.get("assigned_doctor_id") == doctor_character.cid:
            patient.metadata.pop("assigned_doctor_id", None)
        if hasattr(doctor_character, "work"):
            doctor_character.work.medical_patient_id = 0
        _sync_legacy_patient_counters(rhodes_island)
        return

    ability_level = doctor_character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0)
    ability_adjust = float(handle_ability.get_ability_adjust(ability_level))
    progress_increment = max(ability_adjust, 0.25)

    patient.metadata["assigned_doctor_id"] = doctor_character.cid
    set_patient_state(patient, medical_constant.MedicalPatientState.IN_TREATMENT)
    patient.diagnose_progress = min(patient.diagnose_progress + progress_increment, base_hours)
    patient.metadata["last_diagnose_doctor_id"] = doctor_character.cid
    patient.metadata["diagnose_attempts"] = int(patient.metadata.get("diagnose_attempts", 0)) + 1

    if patient.diagnose_progress < base_hours:
        _sync_legacy_patient_counters(rhodes_island)
        return

    patient.diagnose_progress = base_hours
    set_patient_state(patient, medical_constant.MedicalPatientState.WAITING_MEDICATION)

    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = patient_management.resolve_price_income_multiplier(price_ratio)
    raw_income = float(severity_config.diagnose_income) * price_ratio * income_multiplier
    income_value = int(round(raw_income))

    if income_value > 0:
        rhodes_island.medical_income_today += income_value
        rhodes_island.medical_income_total += income_value
        rhodes_island.all_income += income_value
        rhodes_island.materials_resouce[1] = rhodes_island.materials_resouce.get(1, 0) + income_value

    patient.metadata["diagnose_completed"] = True
    patient.metadata["diagnose_completed_doctor_id"] = doctor_character.cid
    patient.metadata.pop("assigned_doctor_id", None)
    if not patient.metadata.get("legacy_cured_flag"):
        rhodes_island.patient_cured = int(getattr(rhodes_island, "patient_cured", 0) or 0) + 1
        rhodes_island.patient_cured_all = int(getattr(rhodes_island, "patient_cured_all", 0) or 0) + 1
        patient.metadata["legacy_cured_flag"] = True

    if hasattr(doctor_character, "work"):
        doctor_character.work.medical_patient_id = 0

    _sync_legacy_patient_counters(rhodes_island)


def try_consume_medicine(
    patient: medical_constant.MedicalPatient,
    *,
    is_hospitalized: bool = False,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """尝试为病人扣除药物并结算药费"""

    if patient is None:
        return False

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return False

    accumulator = rhodes_island.medical_inventory_accumulator
    inventory = rhodes_island.materials_resouce
    recorded_map = patient.metadata.setdefault("medicine_recorded", {})
    progress_map = patient.metadata.setdefault("medicine_progress", {})
    consumed_history = patient.metadata.setdefault("medicine_consumed_units", {})

    resource_success: Dict[int, bool] = {}
    consumed_units: Dict[int, int] = {}

    for resource_id in _MEDICINE_RESOURCE_IDS:
        need_total = float(patient.need_resources.get(resource_id, 0.0) or 0.0)
        accumulator_value = float(accumulator.get(resource_id, 0.0) or 0.0)
        recorded = float(recorded_map.get(resource_id, 0.0) or 0.0)

        if need_total <= _FLOAT_EPSILON:
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
        if to_record > _FLOAT_EPSILON:
            accumulator_value += to_record
            recorded += to_record

        required_units = int(math.floor(accumulator_value + _FLOAT_EPSILON))
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

    overall_success = all(resource_success.get(res_id, True) for res_id in _MEDICINE_RESOURCE_IDS)

    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    income_multiplier = patient_management.resolve_price_income_multiplier(price_ratio)
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
        patient.metadata["medicine_recorded"] = {}
        patient.metadata["medicine_progress"] = {}

    consumed_total_units = sum(int(value) for value in consumed_units.values())
    if not is_hospitalized and consumed_total_units:
        _bump_daily_counter(rhodes_island, "medicine_consumed", consumed_total_units)

    if not is_hospitalized:
        if overall_success:
            _bump_daily_counter(rhodes_island, "total_treated_patients", 1)
            _bump_daily_counter(rhodes_island, "outpatient_cured", 1)
        else:
            _bump_daily_counter(rhodes_island, "outpatient_pending", 1)

    patient.metadata["last_consumed_units"] = consumed_units

    _sync_legacy_patient_counters(rhodes_island)
    return overall_success


def try_hospitalize(
    patient_id: int,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """尝试将病人转入住院列表"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    patient, already_hospitalized = _locate_patient(patient_id, rhodes_island)
    if patient is None or already_hospitalized:
        return False

    if patient.state != medical_constant.MedicalPatientState.WAITING_MEDICATION:
        return False

    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return False

    bed_limit = int(rhodes_island.medical_bed_limit or 0)
    if bed_limit > 0 and len(rhodes_island.medical_hospitalized) >= bed_limit:
        patient.metadata["hospitalize_failed_reason"] = "no_bed"
        return False

    if severity_config.require_hospitalization != 1:
        patient.metadata["hospitalize_failed_reason"] = "not_required"
        return False

    success = hospital_flow.try_hospitalize(rhodes_island, patient, severity_config)
    if success:
        _sync_legacy_patient_counters(rhodes_island)
    return success


def process_hospitalized_patients(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """每日结算住院病人：扣药并判定出院"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None or not rhodes_island.medical_hospitalized:
        return

    def _consume(patient: medical_constant.MedicalPatient) -> bool:
        return try_consume_medicine(patient, is_hospitalized=True, target_base=rhodes_island)

    hospital_flow.process_hospitalized_patients(rhodes_island, _consume)
    _sync_legacy_patient_counters(rhodes_island)


def settle_medical_department(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
    draw_flag: bool = True,
) -> Dict[str, Any]:
    """执行每日医疗经营结算并输出日志"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    _ensure_runtime_dict(rhodes_island)

    process_hospitalized_patients(target_base=rhodes_island)

    stats_source = dict(getattr(rhodes_island, "medical_daily_counters", {}) or {})
    stats: Dict[str, int] = {str(key): int(value) for key, value in stats_source.items()}

    for required_key in (
        "total_treated_patients",
        "hospitalized_today",
        "discharged_today",
        "medicine_consumed",
        "outpatient_cured",
        "outpatient_pending",
        "hospital_treated_success",
        "hospital_treated_pending",
        "surgeries_performed",
    ):
        stats.setdefault(required_key, 0)

    income_today = int(rhodes_island.medical_income_today or 0)
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)

    waiting_states = {
        medical_constant.MedicalPatientState.REFRESHED,
        medical_constant.MedicalPatientState.IN_TREATMENT,
        medical_constant.MedicalPatientState.IN_TREATMENT_PLAYER,
    }
    patients = list(rhodes_island.medical_patients_today.values())
    hospitalized_patients = list(rhodes_island.medical_hospitalized.values())

    waiting_count = sum(1 for patient in patients if patient.state in waiting_states)
    waiting_medication = sum(
        1 for patient in patients if patient.state == medical_constant.MedicalPatientState.WAITING_MEDICATION
    )
    hospitalized_count = len(hospitalized_patients)
    need_surgery_count = sum(1 for patient in hospitalized_patients if patient.need_surgery)
    blocked_surgery_count = sum(1 for patient in hospitalized_patients if patient.need_surgery and patient.surgery_blocked)

    outpatient_cured = stats.get("outpatient_cured", 0)
    hospital_success = stats.get("hospital_treated_success", 0)
    medicine_consumed = stats.get("medicine_consumed", 0)
    hospitalized_today = stats.get("hospitalized_today", 0)
    discharged_today = stats.get("discharged_today", 0)
    surgeries_performed = stats.get("surgeries_performed", 0)
    outpatient_pending = stats.get("outpatient_pending", 0)
    hospital_pending = stats.get("hospital_treated_pending", 0)
    total_treated = stats.get("total_treated_patients", outpatient_cured + hospital_success)

    body_lines: List[str] = []
    body_lines.append(_("今日收入：{0} 龙门币").format(income_today))
    body_lines.append(_("收费系数：{0:.0f}%").format(price_ratio * 100))
    body_lines.append(
        _("诊疗完成：{0} 人（门诊 {1} / 住院 {2}）").format(total_treated, outpatient_cured, hospital_success)
    )
    if outpatient_pending or hospital_pending:
        body_lines.append(
            _("待发药：门诊 {0} 人 / 住院 {1} 人").format(outpatient_pending, hospital_pending)
        )
    body_lines.append(_("药品消耗：{0} 单位").format(medicine_consumed))
    body_lines.append(_("今日入院：{0} 人 / 出院：{1} 人").format(hospitalized_today, discharged_today))
    if surgeries_performed or blocked_surgery_count:
        body_lines.append(
            _("手术执行：成功 {0} 例 / 待条件 {1} 例").format(surgeries_performed, blocked_surgery_count)
        )
    body_lines.append(
        _("队列概况：待诊 {0} 人 / 待发药 {1} 人 / 住院 {2} 人 / 待手术 {3} 人").format(
            waiting_count,
            waiting_medication,
            hospitalized_count,
            need_surgery_count,
        )
    )

    report_text = _("\n医疗部经营结算\n") + "".join(f" - {line}\n" for line in body_lines)

    if draw_flag:
        wait_draw = draw.WaitDraw()
        wait_draw.width = normal_config.config_normal.text_width
        wait_draw.text = report_text
        wait_draw.draw()

    queue_snapshot = {
        "waiting": waiting_count,
        "waiting_medication": waiting_medication,
        "hospitalized": hospitalized_count,
        "need_surgery": need_surgery_count,
        "surgery_blocked": blocked_surgery_count,
    }

    log_header = _("医疗部经营结算")
    log_entry = log_system.append_medical_report(
        {
            "lines": [log_header] + body_lines,
            "income": income_today,
            "price_ratio": price_ratio,
            "stats": stats.copy(),
            "queue": queue_snapshot,
        },
        target_base=rhodes_island,
    )

    from Script.UI.Panel import achievement_panel

    achievement_panel.achievement_flow(_("龙门币"))

    rhodes_island.medical_income_today = 0
    rhodes_island.all_income = 0
    rhodes_island.medical_daily_counters = {}

    refresh_medical_patients(target_base=rhodes_island)
    _sync_legacy_patient_counters(rhodes_island)

    return {
        "success": True,
        "income": income_today,
        "stats": stats,
        "queue": queue_snapshot,
        "report": log_entry,
        "text": report_text,
    }


def attempt_surgery(
    patient_id: int,
    doctor_character: game_type.Character,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """尝试为住院病人执行手术"""

    if doctor_character is None:
        return False

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    patient, hospitalized = _locate_patient(patient_id, rhodes_island)
    if patient is None or not hospitalized:
        return False

    if not patient.need_surgery:
        return False

    if patient.surgery_blocked:
        return False

    return hospital_flow.attempt_surgery(rhodes_island, patient, doctor_character)


def get_patient_table(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
    hospitalized: bool,
) -> Dict[int, medical_constant.MedicalPatient]:
    """获取指定状态下的病人表引用"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {}
    return rhodes_island.medical_hospitalized if hospitalized else rhodes_island.medical_patients_today


def set_patient_state(patient: medical_constant.MedicalPatient, state: medical_constant.MedicalPatientState) -> None:
    """更新病人的流程状态，并写入标签方便调试"""

    if patient is None:
        return
    patient.state = state
    patient.metadata["state"] = state.value


def get_medical_price_ratio(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> float:
    """读取当前医疗部收费系数，若未初始化则返回默认值"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return _resolve_default_price_ratio()
    ratio = float(rhodes_island.medical_price_ratio or 0)
    if ratio <= 0:
        ratio = _resolve_default_price_ratio()
        rhodes_island.medical_price_ratio = ratio
    return ratio


def set_medical_price_ratio(
    price_ratio: float,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """更新医疗部收费系数，并重新评估床位上限"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    rhodes_island.medical_price_ratio = max(float(price_ratio), 0.1)
    rhodes_island.medical_bed_limit = _calculate_medical_bed_limit(rhodes_island)


def get_patient_priority_mode(
    *, target_base: Optional[game_type.Rhodes_Island] = None
) -> medical_constant.MedicalPatientPriority:
    """读取当前病人接诊优先策略，若缺失则回退为默认值"""

    rhodes_island = _get_rhodes_island(target_base)
    return _resolve_triage_mode(rhodes_island)


def set_patient_priority_mode(
    priority_mode: Union[str, medical_constant.MedicalPatientPriority],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> medical_constant.MedicalPatientPriority:
    """更新病人接诊优先策略并返回实际生效的枚举值"""

    default_mode = medical_constant.MedicalPatientPriority.NORMAL
    rhodes_island = _get_rhodes_island(target_base)
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
    """预测在指定收费系数下的病人刷新数量与倍率"""

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        resolved_ratio = float(price_ratio if price_ratio is not None else 1.0)
        return {
            "price_ratio": resolved_ratio,
            "base_count": 0.0,
            "penalty": 1.0,
            "refresh_multiplier": 1.0,
            "income_multiplier": patient_management.resolve_price_income_multiplier(resolved_ratio),
            "predicted_count": 0.0,
        }

    resolved_ratio = float(price_ratio if price_ratio is not None else get_medical_price_ratio(target_base=rhodes_island))
    resolved_level = int(level if level is not None else _get_medical_facility_level(rhodes_island))
    level_config = _pick_hospital_level_config(resolved_level)

    base_count = float(getattr(level_config, "daily_patient_base", 0) or 0)
    safe_ratio = max(resolved_ratio, 0.01)
    penalty = 1.0 / safe_ratio
    if level_config:
        penalty = patient_management.clamp(penalty, level_config.ratio_min, level_config.ratio_max)

    refresh_multiplier = patient_management.resolve_price_refresh_multiplier(resolved_ratio)
    predicted_value = base_count * penalty * refresh_multiplier
    predicted_count = max(int(math.floor(predicted_value)), 0)
    income_multiplier = patient_management.resolve_price_income_multiplier(resolved_ratio)

    return {
        "price_ratio": resolved_ratio,
        "base_count": base_count,
        "penalty": penalty,
        "refresh_multiplier": refresh_multiplier,
        "income_multiplier": income_multiplier,
        "predicted_count": float(predicted_count),
    }


def _calculate_patient_refresh_count(
    rhodes_island: game_type.Rhodes_Island,
    level_config: config_def.Medical_Hospital_Level,
) -> int:
    """依据医院等级与收费系数计算今日应刷新病人数"""

    base_count = max(int(level_config.daily_patient_base), 0)
    if base_count <= 0:
        return 0

    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)
    safe_ratio = max(price_ratio, 0.01)
    penalty = 1.0 / safe_ratio
    penalty = patient_management.clamp(penalty, level_config.ratio_min, level_config.ratio_max)

    refresh_multiplier = patient_management.resolve_price_refresh_multiplier(price_ratio)
    refresh_value = base_count * penalty * refresh_multiplier
    return max(int(math.floor(refresh_value)), 0)


def _get_medical_facility_level(rhodes_island: game_type.Rhodes_Island) -> int:
    """读取医疗部设施等级，缺省返回 0"""

    return int(rhodes_island.facility_level.get(_MEDICAL_FACILITY_ID, 0) or 0)


def _pick_hospital_level_config(level: int) -> Optional[config_def.Medical_Hospital_Level]:
    """根据设施等级选取对应的医院等级配置"""

    if not game_config.config_medical_hospital_level:
        return None
    if level in game_config.config_medical_hospital_level:
        return game_config.config_medical_hospital_level[level]
    eligible = [candidate for candidate in game_config.config_medical_hospital_level.keys() if candidate <= level]
    if eligible:
        return game_config.config_medical_hospital_level[max(eligible)]
    minimal = min(game_config.config_medical_hospital_level.keys())
    return game_config.config_medical_hospital_level.get(minimal)


def _calculate_medical_bed_limit(rhodes_island: game_type.Rhodes_Island) -> int:
    """计算当前医疗部床位上限（基础值 + 兜底当前在院人数）"""

    level_config = _pick_hospital_level_config(_get_medical_facility_level(rhodes_island))
    base_limit = int(level_config.bed_limit) if level_config else 0
    hospital_bonus = len(getattr(rhodes_island, "medical_hospital_doctor_ids", []) or []) * _HOSPITAL_DOCTOR_BED_BONUS
    total_limit = base_limit + hospital_bonus
    current_occupancy = len(rhodes_island.medical_hospitalized)
    return max(total_limit, current_occupancy)


def _calculate_doctor_power(doctor_ids: Optional[List[int]]) -> float:
    """计算医生列表的医疗能力总和，用于缓存字段刷新"""

    if not doctor_ids:
        return 0.0
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
    """确保医疗运行期字段存在且类型正确"""

    rhodes_island.medical_patients_today = dict(getattr(rhodes_island, "medical_patients_today", {}) or {})
    rhodes_island.medical_hospitalized = dict(getattr(rhodes_island, "medical_hospitalized", {}) or {})
    rhodes_island.medical_surgery_records = list(getattr(rhodes_island, "medical_surgery_records", []) or [])

    accumulator = dict(getattr(rhodes_island, "medical_inventory_accumulator", {}) or {})
    for resource_id in _MEDICINE_RESOURCE_IDS:
        accumulator.setdefault(resource_id, 0.0)
    rhodes_island.medical_inventory_accumulator = accumulator

    rhodes_island.medical_income_today = int(getattr(rhodes_island, "medical_income_today", 0) or 0)
    rhodes_island.medical_income_total = int(getattr(rhodes_island, "medical_income_total", 0) or 0)
    rhodes_island.medical_daily_counters = dict(
        getattr(rhodes_island, "medical_daily_counters", {}) or {}
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
    rhodes_island.medical_clinic_doctor_target = int(
        getattr(rhodes_island, "medical_clinic_doctor_target", 0) or 0
    )
    rhodes_island.medical_hospital_doctor_target = int(
        getattr(rhodes_island, "medical_hospital_doctor_target", 0) or 0
    )
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
    _ensure_specialization_structure(rhodes_island)


def _resolve_default_price_ratio() -> float:
    """返回收费系数的默认值，默认 1.0"""
    return 1.0


def _locate_patient(
    patient_id: int,
    rhodes_island: game_type.Rhodes_Island,
) -> Tuple[Optional[medical_constant.MedicalPatient], bool]:
    """在门诊和住院列表中查找病人，返回病人对象与是否住院标记"""

    patient = rhodes_island.medical_patients_today.get(patient_id)
    if patient is not None:
        return patient, False

    patient = rhodes_island.medical_hospitalized.get(patient_id)
    if patient is not None:
        return patient, True

    return None, False


def _get_rhodes_island(
    target_base: Optional[game_type.Rhodes_Island],
) -> Optional[game_type.Rhodes_Island]:
    """返回调用环境可用的罗德岛基地对象"""

    if target_base is not None:
        return target_base
    cache_obj = getattr(cache_control, "cache", None)
    return getattr(cache_obj, "rhodes_island", None)


def _migrate_legacy_income(rhodes_island: game_type.Rhodes_Island) -> None:
    """兼容旧版存档中医疗收入字段"""

    legacy_total = getattr(rhodes_island, "medical_income_total", 0)
    legacy_today = getattr(rhodes_island, "medical_income_today", 0)
    rhodes_island.medical_income_total = int(legacy_total or 0)
    rhodes_island.medical_income_today = int(legacy_today or 0)

    if hasattr(rhodes_island, "medical_income"):
        legacy_income = int(getattr(rhodes_island, "medical_income", 0) or 0)
        rhodes_island.medical_income_total = max(rhodes_island.medical_income_total, legacy_income)
