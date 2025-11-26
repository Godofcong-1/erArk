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

_: Callable[[str], str] = get_text._


def _bump_daily_counter(
    rhodes_island: Optional[game_type.Rhodes_Island],
    key: str,
    value: int,
) -> None:
    """更新医疗日度统计表中的计数。

    功能:
        在基地对象的 ``medical_daily_counters`` 字段中对指定键进行加总，
        便于后续生成日报或统计面板。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 指向当前罗德岛基地的引用，可能为 None。
        key (str): 需要累计的指标名称，例如 ``"medicine"``。
        value (int): 本次需要增加的数值，可以为负值表示回退。

    返回:
        None: 函数仅产生副作用，不返回实际数据。
    """

    if rhodes_island is None or value == 0:
        return
    # medical_daily_counters 以松散字典形式保存每日统计的数据段
    stats = rhodes_island.__dict__.setdefault("medical_daily_counters", {})
    stats[key] = int(stats.get(key, 0) or 0) + int(value)


def _get_specialization_categories() -> List[Dict[str, Any]]:
    """构建分科配置列表。

    功能:
        根据配置表 ``config_medical_body_system_by_system`` 提取系统列表，
        并附加默认的全科条目，便于后续 UI 与逻辑共用。

    返回:
        List[Dict[str, Any]]: 每个字典包含 ``key``、``name`` 与 ``system_id``。
    """

    categories: List[Dict[str, Any]] = [
        {"key": medical_constant.SPECIALIZATION_GENERAL_KEY, "name": _("全科"), "system_id": None}
    ]
    body_system_map = getattr(game_config, "config_medical_body_system_by_system", {}) or {}
    for system_id, part_map in sorted(body_system_map.items(), key=lambda item: item[0]):
        sample = next(iter(part_map.values()), None)
        system_name = getattr(sample, "system_name", str(system_id)) if sample else str(system_id)
        categories.append({"key": str(system_id), "name": system_name, "system_id": system_id})
    return categories


def get_specialization_categories() -> List[Dict[str, Any]]:
    """获取分科配置的对外副本。

    功能:
        向 UI 或其他系统返回分科配置的浅拷贝，避免调用者直接修改内部缓存。

    返回:
        List[Dict[str, Any]]: 与 :func:`_get_specialization_categories` 相同结构的副本。
    """

    return [dict(item) for item in _get_specialization_categories()]


def _get_role_doctor_ids(rhodes_island: Optional[game_type.Rhodes_Island], role_key: str) -> List[int]:
    """查询岗位医生列表。

    功能:
        根据岗位键（门诊或住院）返回对应的医生 ID 副本，防止外部对原数据做原地修改。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 当前基地引用，可能为 None。
        role_key (str): 岗位标识，见 ``medical_constant.SPECIALIZATION_ROLE_*``。

    返回:
        List[int]: 对应岗位的医生 ID 列表，若无数据返回空列表。
    """

    if rhodes_island is None:
        return []
    if role_key == medical_constant.SPECIALIZATION_ROLE_CLINIC:
        return list(getattr(rhodes_island, "medical_clinic_doctor_ids", []) or [])
    if role_key == medical_constant.SPECIALIZATION_ROLE_HOSPITAL:
        return list(getattr(rhodes_island, "medical_hospital_doctor_ids", []) or [])
    return []


def _ensure_specialization_structure(rhodes_island: game_type.Rhodes_Island) -> None:
    """同步医生分科结构，保持岗位数据一致。

    功能:
        保障 ``medical_doctor_specializations`` 的数据结构完整，并强制校准
        每个岗位与分科的医生列表，使其与岗位成员保持一致。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前罗德岛基地对象。

    返回:
        None: 操作直接修改传入对象的属性。
    """

    if rhodes_island is None:
        return

    categories = _get_specialization_categories()
    category_keys = [item["key"] for item in categories]
    raw_spec = getattr(rhodes_island, "medical_doctor_specializations", {})
    if not isinstance(raw_spec, dict):
        raw_spec = {}

    normalized: Dict[str, Dict[str, List[int]]] = {}
    for role_key in medical_constant.SPECIALIZATION_ROLES:
        # 收集当前岗位所有医生，作为最终分科的基准集合
        doctor_ids = set(int(value) for value in _get_role_doctor_ids(rhodes_island, role_key))
        role_bucket = raw_spec.get(role_key)
        assigned_tracker: Dict[int, str] = {}
        if isinstance(role_bucket, dict):
            for category_key, doctor_list in role_bucket.items():
                if category_key not in category_keys:
                    continue
                for doctor_id in doctor_list or []:
                    if doctor_id in doctor_ids and doctor_id not in assigned_tracker:
                        # 记录医生当前的分科归属，后续用于还原
                        assigned_tracker[int(doctor_id)] = category_key

        cleaned: Dict[str, List[int]] = {key: [] for key in category_keys}
        for doctor_id in doctor_ids:
            category_key = assigned_tracker.get(doctor_id, medical_constant.SPECIALIZATION_GENERAL_KEY)
            cleaned.setdefault(category_key, []).append(int(doctor_id))

        for category_key in cleaned:
            # 某分科中可能出现重复条目，这里统一去重并排序
            cleaned[category_key] = sorted({int(value) for value in cleaned[category_key]})

        normalized[role_key] = cleaned

    rhodes_island.medical_doctor_specializations = normalized


def _resolve_doctor_specialization(
    rhodes_island: game_type.Rhodes_Island,
    role_key: str,
    doctor_id: int,
) -> str:
    """解析指定医生的分科归属。

    功能:
        先确保分科结构有效，再返回医生当前所属的分科键；若未登记，则视为全科。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
        role_key (str): 岗位标识。
        doctor_id (int): 医生的角色 ID。

    返回:
        str: 医生归属的分科键，缺省为 ``SPECIALIZATION_GENERAL_KEY``。
    """

    _ensure_specialization_structure(rhodes_island)
    role_bucket = getattr(rhodes_island, "medical_doctor_specializations", {}).get(role_key, {})
    for category_key, doctor_list in role_bucket.items():
        if doctor_id in doctor_list:
            return category_key
    return medical_constant.SPECIALIZATION_GENERAL_KEY


def assign_doctor_specialization(
    role_key: str,
    doctor_id: int,
    category_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, Any]:
    """调整医生分科归属。

    功能:
        将指定医生移动到目标分科，并返回调整结果，供 UI 更新或日志记录。

    参数:
        role_key (str): 岗位标识。
        doctor_id (int): 目标医生 ID。
        category_key (str): 希望归属的分科键。
        target_base (Optional[game_type.Rhodes_Island]): 指定操作的基地对象。

    返回:
        Dict[str, Any]: 包含 ``success``、``category_name`` 等信息的结果字典。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None or role_key not in medical_constant.SPECIALIZATION_ROLES:
        return {"success": False, "reason": "invalid_role"}

    doctor_ids = _get_role_doctor_ids(rhodes_island, role_key)
    if doctor_id not in doctor_ids:
        return {"success": False, "reason": "doctor_not_in_role"}

    categories = _get_specialization_categories()
    category_keys = [item["key"] for item in categories]
    resolved_category = category_key if category_key in category_keys else medical_constant.SPECIALIZATION_GENERAL_KEY

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
    """列举岗位医生。

    功能:
        返回指定岗位当前登记的所有医生 ID，用于统计或 UI 展示。

    参数:
        role_key (str): 岗位标识。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地；为 None 时使用全局缓存。

    返回:
        List[int]: 岗位对应的医生 ID 列表。
    """

    rhodes_island = _get_rhodes_island(target_base)
    return _get_role_doctor_ids(rhodes_island, role_key)


def get_doctor_specialization_overview(
    role_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[Dict[str, Any]]:
    """生成岗位分科概览。

    功能:
        汇总各分科下的医生信息、能力与加成数据，主要供 UI 面板展示。

    参数:
        role_key (str): 岗位标识。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地。

    返回:
        List[Dict[str, Any]]: 由 ``category_key``、``doctor_details`` 等字段组成的统计列表。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None or role_key not in medical_constant.SPECIALIZATION_ROLES:
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
    """提取病人可能关联的系统键。

    功能:
        从病人的并发症追踪信息与并发症列表中推断涉及的系统编号，
        并写回 ``metadata``，为分科加成与筛选提供依据。

    参数:
        patient (medical_constant.MedicalPatient): 目标病人实例。

    返回:
        Set[str]: 去重后的系统键集合。
    """

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
    """计算医生在特定分科下的加成系数。

    功能:
        根据医生当前分科与病人涉及的系统是否匹配，返回命中状态与倍率。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
        role_key (str): 岗位标识。
        doctor_character (Optional[game_type.Character]): 执行诊疗的医生。
        patient (Optional[medical_constant.MedicalPatient]): 待诊的病人。

    返回:
        Tuple[str, bool, float]: (分科键, 是否命中系统, 能力对应加成倍率)。
    """

    if rhodes_island is None or doctor_character is None or patient is None:
        return (medical_constant.SPECIALIZATION_GENERAL_KEY, True, 1.0)

    specialization_key = _resolve_doctor_specialization(rhodes_island, role_key, doctor_character.cid)
    if specialization_key == medical_constant.SPECIALIZATION_GENERAL_KEY:
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
    """为执行诊疗的医生分配待诊病人。

    功能:
        结合医生分科、基地优先策略与病人状态，挑选最适合的候选并
        更新绑定关系。

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
    requires_match = specialization_key != medical_constant.SPECIALIZATION_GENERAL_KEY

    # 优先复用既有分配，避免频繁切换病人导致流程中断
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
    """为住院医生挑选合适的住院病人。

    功能:
        依据病人状态、是否需要手术以及当前分配状况，返回最优的住院病人。

    参数:
        doctor_character (Optional[game_type.Character]): 住院科负责的医生。
        rhodes_island (Optional[game_type.Rhodes_Island]): 当前基地引用。
        require_surgery (bool): 为 True 时仅考虑待手术且未被阻塞的病人。

    返回:
        Optional[medical_constant.MedicalPatient]: 选中的病人，若无符合条件者则返回 None。
    """

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
        # 住院优先级：病情 -> 已住院天数 -> ID，均取反实现最大堆效果
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
    """解析基地当前的病人接诊优先策略。

    功能:
        读取并校验基地上配置的接诊优先级，确保其始终落在枚举范围内。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 基地引用。

    返回:
        medical_constant.MedicalPatientPriority: 修正后的优先级枚举值。
    """

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
    """在候选病人中挑选最优对象。

    功能:
        按基地配置的接诊策略筛选候选病人，使用 ``min`` 与自定义排序键避免全量排序。

    参数:
        candidates (List[medical_constant.MedicalPatient]): 候选病人列表。
        rhodes_island (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        Optional[medical_constant.MedicalPatient]: 成功时返回匹配度最高的病人，否则返回 None。
    """

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
    """清理玩家诊疗流程写入的临时元数据。

    功能:
        将诊疗过程中写入 ``MedicalPatient.metadata`` 的会话数据全部清空，
        确保下次诊疗以干净状态开始。

    参数:
        patient (medical_constant.MedicalPatient): 需要清理的病人对象。

    返回:
        None: 仅执行清理操作。
    """

    if patient is None:
        return
    for key in medical_constant.PLAYER_METADATA_KEYS:
        patient.metadata.pop(key, None)


def _acquire_patient_for_player(
    doctor_character: Optional[game_type.Character],
    rhodes_island: Optional[game_type.Rhodes_Island],
) -> Optional[medical_constant.MedicalPatient]:
    """根据当前优先策略为玩家诊疗会话选定病人。

    功能:
        与自动诊疗类似，但额外确保不与其他医生分配冲突，同时支持复用玩家现有会话。

    参数:
        doctor_character (Optional[game_type.Character]): 由玩家操控的医生角色。
        rhodes_island (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        Optional[medical_constant.MedicalPatient]: 可供玩家诊疗的病人，若无则返回 None。
    """

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
    """初始化玩家诊疗会话。

    功能:
        建立玩家与病人的诊疗会话，初始化会话元数据并返回目标病人。

    参数:
        doctor_character (Optional[game_type.Character]): 玩家操控的医生角色，缺省时读取玩家本体。
        target_base (Optional[game_type.Rhodes_Island]): 指定操作的基地对象。

    返回:
        Optional[medical_constant.MedicalPatient]: 进入会话的病人实例，无可用病人时返回 None。
    """

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
    """终止玩家诊疗会话并恢复病人原始状态。

    功能:
        便于玩家在中途退出诊疗流程时回滚病人状态、解绑医生并清理会话数据。

    参数:
        doctor_character (Optional[game_type.Character]): 玩家操控的医生，用于重置绑定。
        patient (Optional[medical_constant.MedicalPatient]): 可选指定的病人；为空时使用当前会话。
        target_base (Optional[game_type.Rhodes_Island]): 基地引用。

    返回:
        None: 仅执行回滚与清理。
    """

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
    """完成玩家诊疗流程并返回结算摘要。

    功能:
        推进诊疗进度、尝试扣药并汇总收入信息，最终输出用于 UI 展示的结果。

    参数:
        doctor_character (Optional[game_type.Character]): 执行结算的医生。
        patient (Optional[medical_constant.MedicalPatient]): 参与会话的病人。
        apply_medicine (bool): 是否尝试扣除药物并结算收益。
        target_base (Optional[game_type.Rhodes_Island]): 基地引用。

    返回:
        Dict[str, object]: 包含收入、病人状态与药物结果的字典。
    """

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
    """执行玩家选择的检查条目并记录结果。

    功能:
        将玩家在诊疗界面勾选的检查项目批量执行，依据病人实际并发症生成提示信息。

    参数:
        selections (List[Dict[str, int]]): UI 返回的检查选项列表，需包含并发症标识及部位信息。
        patient (Optional[medical_constant.MedicalPatient]): 当前会话的病人。
        target_base (Optional[game_type.Rhodes_Island]): 基地引用。

    返回:
        Dict[str, object]: ``results`` 字段包含逐项检查结果，``used_checks`` 表示次数。
    """

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
    """构建玩家诊疗用的系统/部位/并发症选择树。

    功能:
        根据全局配置生成系统与部位树状结构，并标记病人既往记录便于 UI 展示。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 当前处理的病人。

    返回:
        Dict[int, Dict[str, object]]: 以系统 ID 为键的嵌套字典，包含部位与并发症列表。
    """

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
    """估算诊疗收益与资源需求摘要。

    功能:
        基于病情等级、价格倍率与所需资源，快速计算诊断收益与预期药品收入。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 待估算的病人对象。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地引用。

    返回:
        Dict[str, object]: 包含 ``diagnose_income``、``predicted_medicine_income`` 等键的结果字典。
    """

    # 验证病人有效性
    if patient is None:
        return {"success": False, "reason": "no_patient"}

    # 获取当前基地与病情配置
    rhodes_island = _get_rhodes_island(target_base)
    severity_config = game_config.config_medical_severity.get(patient.severity_level)
    if severity_config is None:
        return {"success": False, "reason": "no_severity_config"}

    # 计算诊疗收益
    price_ratio = get_medical_price_ratio(target_base=rhodes_island)  # 价格系数
    income_multiplier = patient_management.resolve_price_income_multiplier(price_ratio)  # 收益倍率
    # 诊断收益基于配置表基础值乘以价格系数与综合倍率
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
    """在行为开始时预分配病人。

    功能:
        根据行为类型提前锁定目标病人，使行为流程在不同阶段保持一致。

    参数:
        doctor_character (Optional[game_type.Character]): 执行行为的医生。
        behavior_id (Optional[str]): 行为标识。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        Optional[medical_constant.MedicalPatient]: 被预分配的病人，没有匹配时返回 None。
    """

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
    """执行住院查房流程，返回处理结果摘要。

    功能:
        将医生查房、药品消耗与住院流程推进组合在一起，并对结果做统一封装。

    参数:
        doctor_character (Optional[game_type.Character]): 查房医生。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        Dict[str, object]: ``handled`` 标识是否成功处理，``patient`` 返回参与的病人对象。
    """

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
        # 若已完成治疗或出院，解除医生绑定避免重复操作
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
    """尝试为住院患者安排手术。

    功能:
        获取待手术病人并调用住院流程模块完成具体结算，同时处理医生绑定。

    参数:
        doctor_character (Optional[game_type.Character]): 手术医生。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        Dict[str, object]: 包含 ``handled``、``patient`` 等字段的结果摘要。
    """

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
    """同步旧版医疗统计字段，兼容尚未迁移的 UI 逻辑。

    功能:
        将新版病人状态统计转换为旧字段 ``patient_now``，避免旧版界面出现空值。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。

    返回:
        None: 直接修改基地属性，不返回数据。
    """

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
    """刷新医疗部医生缓存并更新床位上限。

    功能:
        同时更新门诊、住院医生列表及人力强度，随后重算医疗床位上限与分科结构。

    参数:
        clinic_doctors (Optional[List[int]]): 门诊医生 ID 列表，为 None 时沿用旧值。
        hospital_doctors (Optional[List[int]]): 住院医生 ID 列表，为 None 时沿用旧值。
        clinic_power (Optional[float]): 门诊医生合力数值，缺省时自动计算。
        hospital_power (Optional[float]): 住院医生合力数值，缺省时自动计算。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地对象。

    返回:
        None: 通过副作用更新基地缓存。
    """

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
    """根据增量调整医疗部医生目标人数并触发自动排班。

    功能:
        在当前目标基础上加减指定数量，再调用 :func:`dispatch_medical_doctors` 获取最新排班结果。

    参数:
        clinic_delta (int): 门诊医生目标增量，可为负数。
        hospital_delta (int): 住院医生目标增量，可为负数。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地对象。

    返回:
        Dict[str, int]: 排班结果摘要。
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
    """在保持当前目标数量的前提下重新执行自动排班。

    功能:
        以当前目标人数为基准重新计算门诊与住院医生分配，不改变配置。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定基地。

    返回:
        Dict[str, int]: 由 :func:`dispatch_medical_doctors` 返回的排班结果。
    """

    rhodes_island = _get_rhodes_island(target_base)
    return dispatch_medical_doctors(target_base=rhodes_island)


def summarize_dispatch_result(result: Optional[Dict[str, int]]) -> str:
    """将排班结果转化为可读文本，便于面板直接展示。

    功能:
        将排班统计字典格式化为多行字符串，供面板或日志直接使用。

    参数:
        result (Optional[Dict[str, int]]): 排班摘要字典。

    返回:
        str: 格式化后的文本描述，末尾包含换行符。
    """

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
    """初始化医疗系统相关的运行期数据结构。

    功能:
        用于新游戏或读取旧档后设置默认值，可选择是否迁移旧字段与重置运行时状态。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定基地。
        reset_runtime (bool): 是否重置运行期缓存数据。
        migrate_legacy (bool): 是否执行旧版本数据迁移。

    返回:
        None。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    if migrate_legacy:
        # --- 旧数据迁移阶段：统一旧存档中的收入字段 ---
        _migrate_legacy_income(rhodes_island)

    if reset_runtime:
        # --- 重置阶段：清空运行期状态，确保进入全新的一天 ---
        rhodes_island.medical_patients_today = {}
        rhodes_island.medical_hospitalized = {}
        rhodes_island.medical_surgery_records = []
        rhodes_island.medical_inventory_accumulator = {
            resource_id: 0.0 for resource_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS
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
        # --- 校准阶段：对旧档的运行期表结构做类型校正 ---
        _ensure_runtime_dict(rhodes_island)
        rhodes_island.medical_player_current_patient_id = int(
            getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0
        )

    _ensure_specialization_structure(rhodes_island)

    if not rhodes_island.medical_price_ratio or rhodes_island.medical_price_ratio <= 0:
        rhodes_island.medical_price_ratio = _resolve_default_price_ratio()

    # --- 缓存阶段：根据医生情况更新床位与队列统计 ---
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
    """在读取旧存档时修复医疗系统相关字段。

    功能:
        校验存档中的基地对象并执行初始化流程，确保数据结构符合新版要求。

    参数:
        cache_snapshot (Dict[str, Any]): 存档数据快照。

    返回:
        None: 内部调用 :func:`init_medical_department_data` 完成迁移。
    """

    rhodes_island = cache_snapshot.get("rhodes_island")
    if not isinstance(rhodes_island, game_type.Rhodes_Island):
        return

    init_medical_department_data(rhodes_island, reset_runtime=False, migrate_legacy=True)


def refresh_medical_patients(
    level: Optional[int] = None,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[medical_constant.MedicalPatient]:
    """根据医疗部等级刷新当日病人列表。

    参数:
        level (Optional[int]): 指定的医疗部等级，缺省时自动检测。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地。

    返回:
        List[medical_constant.MedicalPatient]: 新增的病人对象列表。
    """

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

    # --- 生成阶段：根据刷新次数批量创建病人并写入当日列表 ---
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
    """推进病人的诊疗进度并在完成时发放诊疗收入。

    参数:
        patient_id (int): 目标病人 ID。
        doctor_character (game_type.Character): 执行诊疗的医生。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        None: 完成后通过副作用修改病人状态与基地收入。
    """

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
        # 无需治疗的病人直接进入待发药阶段
        set_patient_state(patient, medical_constant.MedicalPatientState.WAITING_MEDICATION)
        if patient.metadata.get("assigned_doctor_id") == doctor_character.cid:
            patient.metadata.pop("assigned_doctor_id", None)
        if hasattr(doctor_character, "work"):
            doctor_character.work.medical_patient_id = 0
        _sync_legacy_patient_counters(rhodes_island)
        return

    # --- 诊疗推进阶段：按医生能力计算治疗进度 ---
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

    # --- 收入结算阶段：根据价格系数累计诊疗收入 ---
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
        # 旧版统计兼容，确保累计治愈数量同步
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
    """尝试为病人扣除药物并结算药费。

    参数:
        patient (medical_constant.MedicalPatient): 需要治疗的病人对象。
        is_hospitalized (bool): 是否处于住院流程。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        bool: ``True`` 表示已满足所需药物并结算成功，``False`` 表示库存不足。
    """

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

    # --- 资源处理阶段：针对每种药品资源独立计算需求、库存与扣除情况 ---
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

    overall_success = all(
        resource_success.get(res_id, True) for res_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS
    )

    # --- 收益阶段：根据已扣除的药品数量计算收入并写入历史 ---
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
    """尝试将病人转入住院列表。

    功能:
        检查床位、强制条件等限制，满足时将病人移入住院列表并记录原因。

    参数:
        patient_id (int): 待转入的病人 ID。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        bool: ``True`` 表示住院流程发起成功。
    """

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
    """每日结算住院病人：扣药并判定出院。

    功能:
        遍历住院病人执行药品结算、判定出院，并刷新统计缓存。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        None: 通过副作用完成住院病人的日常结算。
    """

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
    """执行每日医疗经营结算并输出日志。

    功能:
        汇总医疗部当日数据、更新日志、刷新病人队列，并根据需要输出界面文本。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定基地对象。
        draw_flag (bool): 是否在界面上渲染结算文本。

    返回:
        Dict[str, Any]: 包含 ``income``、``stats``、``queue`` 等信息的结算摘要。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    _ensure_runtime_dict(rhodes_island)

    process_hospitalized_patients(target_base=rhodes_island)

    # --- 统计阶段：补全每日统计字典，避免缺失键导致报表数据不完整 ---
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

    # --- 队列快照阶段：分析不同队列的数量，为日志与报表提供概览 ---
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

    # --- 报表文本阶段：逐行构建面板展示用的字符串信息 ---
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
        # --- UI 输出阶段：将结算信息写入滚动文本，供玩家查看 ---
        wait_draw = draw.WaitDraw()
        wait_draw.width = normal_config.config_normal.text_width
        wait_draw.text = report_text
        wait_draw.draw()

    # --- 记录阶段：打包关键指标并写入日志系统，实现历史回放 ---
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

    # --- 清理阶段：重置当日计数并刷新新一天的患者 ---
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
    """尝试为住院病人执行手术。

    功能:
        对指定病人调用住院流程模块进行手术判定，满足条件时推进手术结算。

    参数:
        patient_id (int): 住院病人 ID。
        doctor_character (game_type.Character): 执刀医生。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        bool: ``True`` 表示手术流程启动成功。
    """

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
    """获取指定状态下的病人表引用。

    功能:
        根据 `hospitalized` 标志返回门诊或住院病人字典，便于外部模块统一访问。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。
        hospitalized (bool): ``True`` 返回住院列表，``False`` 返回门诊列表。

    返回:
        Dict[int, medical_constant.MedicalPatient]: 对应状态的病人字典。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return {}
    return rhodes_island.medical_hospitalized if hospitalized else rhodes_island.medical_patients_today


def set_patient_state(patient: medical_constant.MedicalPatient, state: medical_constant.MedicalPatientState) -> None:
    """更新病人的流程状态，并写入标签方便调试。

    功能:
        设置病人状态枚举并将其数值写入元数据，便于存档或调试。

    参数:
        patient (medical_constant.MedicalPatient): 目标病人对象。
        state (medical_constant.MedicalPatientState): 目标状态枚举值。

    返回:
        None。
    """

    if patient is None:
        return
    patient.state = state
    patient.metadata["state"] = state.value


def get_medical_price_ratio(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> float:
    """读取当前医疗部收费系数，若未初始化则返回默认值。

    功能:
        对基地收费系数做兜底校验，确保调用处始终获得正数。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        float: 收费系数。
    """

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
    """更新医疗部收费系数，并重新评估床位上限。

    功能:
        写入新的收费系数并立即重算床位上限，避免出现超限或负值。

    参数:
        price_ratio (float): 新的收费系数。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        None。
    """

    rhodes_island = _get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    rhodes_island.medical_price_ratio = max(float(price_ratio), 0.1)
    rhodes_island.medical_bed_limit = _calculate_medical_bed_limit(rhodes_island)


def get_patient_priority_mode(
    *, target_base: Optional[game_type.Rhodes_Island] = None
) -> medical_constant.MedicalPatientPriority:
    """读取当前病人接诊优先策略，若缺失则回退为默认值。

    功能:
        统一调用 `_resolve_triage_mode`，确保外部始终拿到有效枚举值。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        medical_constant.MedicalPatientPriority: 生效的优先策略枚举。
    """

    rhodes_island = _get_rhodes_island(target_base)
    return _resolve_triage_mode(rhodes_island)


def set_patient_priority_mode(
    priority_mode: Union[str, medical_constant.MedicalPatientPriority],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> medical_constant.MedicalPatientPriority:
    """更新病人接诊优先策略并返回实际生效的枚举值。

    功能:
        将传入值解析为枚举后写入基地对象，并返回实际生效的结果。

    参数:
        priority_mode (Union[str, medical_constant.MedicalPatientPriority]): 目标优先策略。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        medical_constant.MedicalPatientPriority: 确认后的枚举值。
    """

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
    """预测在指定收费系数下的病人刷新数量与倍率。

    功能:
        在不改变真实数据的情况下预估价格调整带来的刷新数量变化与收益倍率。

    参数:
        price_ratio (Optional[float]): 自定义收费系数，缺省时读取基地设置。
        level (Optional[int]): 指定医疗等级，缺省时根据基地设施判定。
        target_base (Optional[game_type.Rhodes_Island]): 当前基地引用。

    返回:
        Dict[str, float]: 包含 ``predicted_count``、``income_multiplier`` 等指标的预测结果。
    """

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
    """依据医院等级与收费系数计算今日应刷新病人数。

    功能:
        应用等级配置、价格惩罚与刷新倍率，返回整数化后的刷新数量。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
        level_config (config_def.Medical_Hospital_Level): 对应等级的配置条目。

    返回:
        int: 今日应刷新病人的数量。
    """

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
    """读取医疗部设施等级，缺省返回 0。

    功能:
        从 ``facility_level`` 字典中拿到医疗部等级，对缺失值提供兜底。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。

    返回:
        int: 医疗部等级。
    """

    return int(rhodes_island.facility_level.get(medical_constant.MEDICAL_FACILITY_ID, 0) or 0)


def _pick_hospital_level_config(level: int) -> Optional[config_def.Medical_Hospital_Level]:
    """根据设施等级选取对应的医院等级配置。

    功能:
        根据传入等级查找最合适的医院配置，支持向下兼容与最小值兜底。

    参数:
        level (int): 医疗部等级。

    返回:
        Optional[config_def.Medical_Hospital_Level]: 匹配的配置对象，若不存在则从相邻等级回退。
    """

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
    """计算当前医疗部床位上限（基础值 + 兜底当前在院人数）。

    功能:
        结合等级上限与医生提供的加成，返回包含兜底的最终床位数。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。

    返回:
        int: 床位上限。
    """

    level_config = _pick_hospital_level_config(_get_medical_facility_level(rhodes_island))
    base_limit = int(level_config.bed_limit) if level_config else 0
    hospital_bonus = (
        len(getattr(rhodes_island, "medical_hospital_doctor_ids", []) or [])
        * medical_constant.HOSPITAL_DOCTOR_BED_BONUS
    )
    total_limit = base_limit + hospital_bonus
    current_occupancy = len(rhodes_island.medical_hospitalized)
    return max(total_limit, current_occupancy)


def _calculate_doctor_power(doctor_ids: Optional[List[int]]) -> float:
    """计算医生列表的医疗能力总和，用于缓存字段刷新。

    功能:
        遍历医生列表累加医疗能力，为排班与床位计算提供依据。

    参数:
        doctor_ids (Optional[List[int]]): 医生 ID 列表。

    返回:
        float: 医疗能力值总和。
    """

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
    """确保医疗运行期字段存在且类型正确。

    功能:
        对所有运行期字段执行类型校正与默认值填充，兼容旧存档。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。

    返回:
        None。
    """

    rhodes_island.medical_patients_today = dict(getattr(rhodes_island, "medical_patients_today", {}) or {})
    rhodes_island.medical_hospitalized = dict(getattr(rhodes_island, "medical_hospitalized", {}) or {})
    rhodes_island.medical_surgery_records = list(getattr(rhodes_island, "medical_surgery_records", []) or [])

    accumulator = dict(getattr(rhodes_island, "medical_inventory_accumulator", {}) or {})
    for resource_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS:
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
    """返回收费系数的默认值，默认 1.0。

    功能:
        提供收费系数的统一兜底，避免出现零值。

    返回:
        float: 默认收费系数。
    """
    return 1.0


def _locate_patient(
    patient_id: int,
    rhodes_island: game_type.Rhodes_Island,
) -> Tuple[Optional[medical_constant.MedicalPatient], bool]:
    """在门诊和住院列表中查找病人，返回病人对象与是否住院标记。

    功能:
        同时在门诊与住院表中查找，返回第一匹配结果及其归属。

    参数:
        patient_id (int): 目标病人 ID。
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。

    返回:
        Tuple[Optional[medical_constant.MedicalPatient], bool]: (病人对象, 是否住院)。
    """

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
    """返回调用环境可用的罗德岛基地对象。

    功能:
        优先使用调用方提供的基地，没有时回退到缓存对象。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 显式传入的基地引用。

    返回:
        Optional[game_type.Rhodes_Island]: 生效的基地对象。
    """

    if target_base is not None:
        return target_base
    cache_obj = getattr(cache_control, "cache", None)
    return getattr(cache_obj, "rhodes_island", None)


def _migrate_legacy_income(rhodes_island: game_type.Rhodes_Island) -> None:
    """兼容旧版存档中医疗收入字段。

    功能:
        将旧字段 ``medical_income`` 合并到新结构，避免数据丢失。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。

    返回:
        None。
    """

    legacy_total = getattr(rhodes_island, "medical_income_total", 0)
    legacy_today = getattr(rhodes_island, "medical_income_today", 0)
    rhodes_island.medical_income_total = int(legacy_total or 0)
    rhodes_island.medical_income_today = int(legacy_today or 0)

    if hasattr(rhodes_island, "medical_income"):
        legacy_income = int(getattr(rhodes_island, "medical_income", 0) or 0)
        rhodes_island.medical_income_total = max(rhodes_island.medical_income_total, legacy_income)
