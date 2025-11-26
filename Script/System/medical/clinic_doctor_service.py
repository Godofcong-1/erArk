# -*- coding: UTF-8 -*-
"""门诊医生与通用医生管理模块

负责医生分科、分配以及门诊医生获取病人的相关逻辑，
供医疗服务主模块复用。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from types import FunctionType

from Script.Config import game_config
from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import handle_ability, handle_premise
from Script.System.Medical import (
    hospital_doctor_service,
    medical_constant,
    medical_core,
)
from Script.System.Medical import clinic_patient_management

_: FunctionType = get_text._
""" 翻译函数 """


def _get_specialization_categories() -> List[Dict[str, Any]]:
    """生成医生分科分类列表。

    返回:
        List[Dict[str, Any]]: 每条包含分类键、展示名称与生理系统 ID 的字典。
    """
    # 先插入默认的全科分类作为兜底。
    categories: List[Dict[str, Any]] = [
        {"key": medical_constant.SPECIALIZATION_GENERAL_KEY, "name": _("全科"), "system_id": None}
    ]
    # 遍历医疗系统配置表，映射到具体的系统分类。
    body_system_map = getattr(game_config, "config_medical_body_system_by_system", {}) or {}
    for system_id, part_map in sorted(body_system_map.items(), key=lambda item: item[0]):
        sample = next(iter(part_map.values()), None)
        system_name = getattr(sample, "system_name", str(system_id)) if sample else str(system_id)
        categories.append({"key": str(system_id), "name": system_name, "system_id": system_id})
    return categories


def get_specialization_categories() -> List[Dict[str, Any]]:
    """获取医生分科分类的浅拷贝列表，供 UI 直接使用。"""
    return [dict(item) for item in _get_specialization_categories()]


def _get_role_doctor_ids(rhodes_island: Optional[game_type.Rhodes_Island], role_key: str) -> List[int]:
    """根据角色类型返回对应医生 ID 列表。

    参数:
        rhodes_island (Optional[game_type.Rhodes_Island]): 目标基地对象。
        role_key (str): 角色键，区分门诊与住院医生。
    返回:
        List[int]: 当前角色下的医生编号集合。
    """
    # 无基地对象时直接返回空列表。
    if rhodes_island is None:
        return []
    # 根据不同角色类型返回对应的医生编号集合。
    if role_key == medical_constant.SPECIALIZATION_ROLE_CLINIC:
        return list(getattr(rhodes_island, "medical_clinic_doctor_ids", []) or [])
    if role_key == medical_constant.SPECIALIZATION_ROLE_HOSPITAL:
        return list(getattr(rhodes_island, "medical_hospital_doctor_ids", []) or [])
    return []


def _ensure_specialization_structure(rhodes_island: game_type.Rhodes_Island) -> None:
    """对基地内的医生分科数据结构进行规范化。

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地对象。
    返回:
        None: 若结构缺失或异常将被重建，确保后续访问安全。
    """
    # 无基地对象时不需要执行规范化。
    if rhodes_island is None:
        return

    # 读取所有合法的分科分类键。
    categories = _get_specialization_categories()
    category_keys = [item["key"] for item in categories]
    raw_spec = getattr(rhodes_island, "medical_doctor_specializations", {})
    if not isinstance(raw_spec, dict):
        raw_spec = {}

    # 遍历门诊与住院两个角色，将当前医生列表映射到各分类。
    normalized: Dict[str, Dict[str, List[int]]] = {}
    for role_key in medical_constant.SPECIALIZATION_ROLES:
        # 过滤出当前角色拥有的医生编号。
        doctor_ids = set(int(value) for value in _get_role_doctor_ids(rhodes_island, role_key))
        role_bucket = raw_spec.get(role_key)
        assigned_tracker: Dict[int, str] = {}
        # 记录旧结构中已经登记的分科结果，便于沿用。
        if isinstance(role_bucket, dict):
            for category_key, doctor_list in role_bucket.items():
                if category_key not in category_keys:
                    continue
                for doctor_id in doctor_list or []:
                    if doctor_id in doctor_ids and doctor_id not in assigned_tracker:
                        assigned_tracker[int(doctor_id)] = category_key

        # 初始化每个分类的容器并按默认规则填充。
        cleaned: Dict[str, List[int]] = {key: [] for key in category_keys}
        for doctor_id in doctor_ids:
            category_key = assigned_tracker.get(doctor_id, medical_constant.SPECIALIZATION_GENERAL_KEY)
            cleaned.setdefault(category_key, []).append(int(doctor_id))

        # 去重并排序医生编号，保证序列稳定。
        for category_key in cleaned:
            cleaned[category_key] = sorted({int(value) for value in cleaned[category_key]})

        normalized[role_key] = cleaned

    rhodes_island.medical_doctor_specializations = normalized


def _resolve_doctor_specialization(
    rhodes_island: game_type.Rhodes_Island,
    role_key: str,
    doctor_id: int,
) -> str:
    """计算指定医生在给定角色下的分科键。

    参数:
        rhodes_island (game_type.Rhodes_Island): 当前基地对象。
        role_key (str): 门诊或住院角色键。
        doctor_id (int): 医生角色 ID。
    返回:
        str: 匹配到的分科键，默认为全科。
    """
    # 确保分科结构初始化后再读取。
    _ensure_specialization_structure(rhodes_island)
    role_bucket = getattr(rhodes_island, "medical_doctor_specializations", {}).get(role_key, {})
    for category_key, doctor_list in role_bucket.items():
        if doctor_id in doctor_list:
            return category_key
    return medical_constant.SPECIALIZATION_GENERAL_KEY


def _bind_doctor_to_patient(
    patient: Optional[medical_constant.MedicalPatient],
    doctor_character: Optional[game_type.Character],
) -> None:
    """记录医生与病人的绑定关系，避免存在未同步的引用。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 需要绑定的病人对象。
        doctor_character (Optional[game_type.Character]): 即将接诊的医生对象。
    返回:
        None
    """

    # 缺少任一对象时无需处理绑定。
    if patient is None or doctor_character is None:
        return

    # 写入病人侧的绑定信息并同步医生的运行期字段。
    patient.metadata["assigned_doctor_id"] = doctor_character.cid
    work_data = getattr(doctor_character, "work", None)
    if work_data is not None:
        work_data.medical_patient_id = patient.patient_id


def _clear_doctor_patient_binding(
    patient: Optional[medical_constant.MedicalPatient],
    doctor_character: Optional[game_type.Character],
) -> None:
    """解除医生与病人的绑定，防止残留的旧引用。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 待解除绑定的病人。
        doctor_character (Optional[game_type.Character]): 目标医生对象。
    返回:
        None
    """

    # 清理病人侧的绑定标记，仅当确实指向该医生时才删除。
    if patient is not None:
        assigned = int(patient.metadata.get("assigned_doctor_id", 0) or 0)
        if doctor_character is None or assigned == getattr(doctor_character, "cid", -1):
            patient.metadata.pop("assigned_doctor_id", None)

    # 将医生的运行期病人引用重置为 0，避免重复引用。
    if doctor_character is not None:
        work_data = getattr(doctor_character, "work", None)
        if work_data is not None:
            work_data.medical_patient_id = 0


def _patient_matches_specialization(
    patient: Optional[medical_constant.MedicalPatient],
    specialization_key: str,
) -> bool:
    """判断病人的生理系统是否满足医生分科要求。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 需要匹配的病人对象。
        specialization_key (str): 医生当前的分科键。
    返回:
        bool: True 表示病人满足分科要求。
    """

    # 无病人时直接视为不匹配。
    if patient is None:
        return False

    # 全科医生不限制分科，直接判定成功。
    if specialization_key == medical_constant.SPECIALIZATION_GENERAL_KEY:
        return True

    # 读取或解析病人关联的系统标签，便于后续复用。
    system_keys = set(patient.metadata.get("system_keys", []))
    if not system_keys:
        system_keys = clinic_patient_management._resolve_patient_system_keys(patient)
    return specialization_key in system_keys


def _is_patient_assignable(
    patient: Optional[medical_constant.MedicalPatient],
    doctor_id: int,
    specialization_key: str,
) -> bool:
    """综合判断病人当前是否可以分配给指定医生。

    参数:
        patient (Optional[medical_constant.MedicalPatient]): 候选病人对象。
        doctor_id (int): 医生的角色 ID。
        specialization_key (str): 医生所属的分科键。
    返回:
        bool: True 表示可以分配。
    """

    # 无病人或状态不在待诊集合中时直接失败。
    if patient is None or patient.state not in medical_constant.ASSIGNABLE_PATIENT_STATE_SET:
        return False

    # 已绑定其他医生的病人不能被抢占。
    assigned_doctor = int(patient.metadata.get("assigned_doctor_id", 0) or 0)
    if assigned_doctor and assigned_doctor != doctor_id:
        return False

    # 最终根据医生的分科验证病人的系统标签。
    return _patient_matches_specialization(patient, specialization_key)


def assign_doctor_specialization(
    role_key: str,
    doctor_id: int,
    category_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Dict[str, Any]:
    """为指定医生设置分科信息。

    参数:
        role_key (str): 医生角色键。
        doctor_id (int): 目标医生编号。
        category_key (str): 欲分配的分科键。
        target_base (Optional[game_type.Rhodes_Island]): 指定基地实例，默认读取全局缓存。
    返回:
        Dict[str, Any]: 包含成功标记、角色、分科信息等内容的返回字典。
    """
    # 定位要修改医生分科信息的基地。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None or role_key not in medical_constant.SPECIALIZATION_ROLES:
        return {"success": False, "reason": "invalid_role"}

    # 仅允许修改已登记在该角色下的医生。
    doctor_ids = _get_role_doctor_ids(rhodes_island, role_key)
    if doctor_id not in doctor_ids:
        return {"success": False, "reason": "doctor_not_in_role"}

    # 校验分科键，未找到时回退至全科。
    categories = _get_specialization_categories()
    category_keys = [item["key"] for item in categories]
    resolved_category = category_key if category_key in category_keys else medical_constant.SPECIALIZATION_GENERAL_KEY

    # 重新构建分科结构并将目标医生移动到指定分类。
    _ensure_specialization_structure(rhodes_island)
    role_bucket = rhodes_island.medical_doctor_specializations.setdefault(role_key, {})
    for key in category_keys:
        current_list = role_bucket.setdefault(key, [])
        if doctor_id in current_list:
            current_list.remove(doctor_id)
    target_list = role_bucket.setdefault(resolved_category, [])
    target_list.append(doctor_id)
    role_bucket[resolved_category] = sorted({int(value) for value in target_list})

    # 完成后再次规范化，确保结构一致。
    _ensure_specialization_structure(rhodes_island)

    # 返回带有分科名称的结果字典供 UI 反馈。
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
    """获取指定角色下的医生 ID 列表。

    参数:
        role_key (str): 门诊或住院角色键。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        List[int]: 已登记的医生编号列表。
    """
    # 从环境中获取目标基地对象。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    return _get_role_doctor_ids(rhodes_island, role_key)


def get_doctor_specialization_overview(
    role_key: str,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> List[Dict[str, Any]]:
    """汇总指定角色下各分科的医生与能力信息。

    参数:
        role_key (str): 门诊或住院角色键。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        List[Dict[str, Any]]: 每项包含分科名称、医生列表及能力统计。
    """
    # 获取目标基地并验证角色合法性。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None or role_key not in medical_constant.SPECIALIZATION_ROLES:
        return []

    # 准备好分科结构以便遍历。
    _ensure_specialization_structure(rhodes_island)
    categories = _get_specialization_categories()
    role_bucket = rhodes_island.medical_doctor_specializations.get(role_key, {})
    character_table = getattr(cache_control.cache, "character_data", {})

    overview: List[Dict[str, Any]] = []
    for category in categories:
        # 从结构中取出该分类下的医生列表。
        doctor_ids = list(role_bucket.get(category["key"], []) or [])
        doctor_details: List[Dict[str, Any]] = []
        total_level = 0
        total_adjust = 0.0
        total_bonus = 0.0
        for doctor_id in doctor_ids:
            # 汇总医生能力信息，用于统计与加成计算。
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


def _resolve_specialization_bonus(
    rhodes_island: game_type.Rhodes_Island,
    role_key: str,
    doctor_character: Optional[game_type.Character],
    patient: Optional[medical_constant.MedicalPatient],
) -> Tuple[str, bool, float]:
    """根据医生与病人信息计算分科加成。

    参数:
        rhodes_island (game_type.Rhodes_Island): 目标基地对象。
        role_key (str): 医生角色键。
        doctor_character (Optional[game_type.Character]): 实际医生对象。
        patient (Optional[medical_constant.MedicalPatient]): 当前诊治的病人。
    返回:
        Tuple[str, bool, float]: 分别为分科键、是否匹配、加成倍数。
    """
    # 缺少必要对象时直接返回无加成结果。
    if rhodes_island is None or doctor_character is None or patient is None:
        return (medical_constant.SPECIALIZATION_GENERAL_KEY, True, 1.0)

    # 查找医生在当前角色下的分科。
    specialization_key = _resolve_doctor_specialization(rhodes_island, role_key, doctor_character.cid)
    if specialization_key == medical_constant.SPECIALIZATION_GENERAL_KEY:
        return (specialization_key, True, 1.0)

    # 检查病人的病理系统是否与医生分科匹配。
    system_keys = clinic_patient_management._resolve_patient_system_keys(patient)
    if specialization_key not in system_keys:
        return (specialization_key, False, 1.0)

    # 按医生能力等级计算加成倍率。
    ability_level = int(doctor_character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)
    bonus_multiplier = 1.0 + max(ability_level, 0) * medical_constant.SPECIALIZATION_BONUS_PER_LEVEL
    return (specialization_key, True, bonus_multiplier)


def acquire_patient_for_doctor(
    doctor_character: Optional[game_type.Character],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Optional[medical_constant.MedicalPatient]:
    """为门诊医生选取待诊病人。

    参数:
        doctor_character (Optional[game_type.Character]): 待分配的医生对象。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        Optional[medical_constant.MedicalPatient]: 分配到的病人对象，若无则为 None。
    """
    # --- 无医生对象时无法分配病人 ---
    if doctor_character is None:
        return None

    # --- 获取诊疗所在的基地与当日病人表 ---
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return None
    patient_table = rhodes_island.medical_patients_today
    if not patient_table:
        return None

    # --- 解析医生 ID 与分科信息，用于后续筛选 ---
    doctor_id = int(getattr(doctor_character, "cid", 0) or 0)
    specialization_key = _resolve_doctor_specialization(
        rhodes_island,
        medical_constant.SPECIALIZATION_ROLE_CLINIC,
        doctor_id,
    )

    # --- 若医生已有绑定病人则尝试直接沿用 ---
    work_data = getattr(doctor_character, "work", None)
    assigned_id = int(getattr(work_data, "medical_patient_id", 0) or 0)
    cached_patient = patient_table.get(assigned_id) if assigned_id else None
    if _is_patient_assignable(cached_patient, doctor_id, specialization_key):
        _bind_doctor_to_patient(cached_patient, doctor_character)
        return cached_patient
    if cached_patient is not None:
        _clear_doctor_patient_binding(cached_patient, doctor_character)

    # --- 根据分科与状态过滤可分配的病人列表 ---
    candidates: List[medical_constant.MedicalPatient] = [
        patient
        for patient in patient_table.values()
        if _is_patient_assignable(patient, doctor_id, specialization_key)
    ]
    if not candidates:
        return None

    # --- 按既定分诊策略选出最终病人并写回绑定 ---
    patient = clinic_patient_management._select_triage_candidate(candidates, rhodes_island)
    if patient is None:
        return None
    _bind_doctor_to_patient(patient, doctor_character)
    return patient


def prepare_doctor_medical_behavior(
    doctor_character: Optional[game_type.Character],
    behavior_id: Optional[str],
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> Optional[medical_constant.MedicalPatient]:
    """为指定行为预先准备医生与病人的绑定关系。

    参数:
        doctor_character (Optional[game_type.Character]): 执行行为的医生对象。
        behavior_id (Optional[str]): 当前即将执行的行为 ID。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        Optional[medical_constant.MedicalPatient]: 准备好的病人对象，若无则为 None。
    """
    # 缺少医生或行为标识时无需准备。
    if doctor_character is None or not behavior_id:
        return None

    # 获取行为执行所在的基地。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return None

    # 根据行为类型路由到不同的病人获取流程。
    if behavior_id == constant.Behavior.CURE_PATIENT:
        return acquire_patient_for_doctor(doctor_character, target_base=rhodes_island)
    if behavior_id == getattr(constant.Behavior, "WARD_ROUND", "ward_round"):
        return hospital_doctor_service._acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=False)
    if behavior_id == getattr(constant.Behavior, "PERFORM_SURGERY", "perform_surgery"):
        return hospital_doctor_service._acquire_hospital_patient_for_doctor(doctor_character, rhodes_island, require_surgery=True)
    return None


def update_doctor_assignments(
    clinic_doctors: Optional[List[int]] = None,
    hospital_doctors: Optional[List[int]] = None,
    *,
    clinic_power: Optional[float] = None,
    hospital_power: Optional[float] = None,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> None:
    """同步医生名单与能力值，并自动刷新床位上限。

    参数:
        clinic_doctors (Optional[List[int]]): 门诊医生 ID 列表，None 表示沿用现值。
        hospital_doctors (Optional[List[int]]): 住院医生 ID 列表。
        clinic_power (Optional[float]): 门诊医生医疗能力总和，可由外部预计算传入。
        hospital_power (Optional[float]): 住院医生医疗能力总和。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        None: 直接修改基地缓存字段。
    """
    # 校验并获取目标基地。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    # 若传入新的门诊医生列表，则刷新缓存并计算能力值。
    if clinic_doctors is not None:
        rhodes_island.medical_clinic_doctor_ids = list(clinic_doctors)
        resolved_power = clinic_power if clinic_power is not None else medical_core._calculate_doctor_power(clinic_doctors)
        rhodes_island.medical_clinic_doctor_power = float(resolved_power)
    else:
        rhodes_island.medical_clinic_doctor_ids = list(
            getattr(rhodes_island, "medical_clinic_doctor_ids", []) or []
        )
        rhodes_island.medical_clinic_doctor_power = float(
            getattr(rhodes_island, "medical_clinic_doctor_power", 0.0) or 0.0
        )

    # 同理处理住院医生的名单与能力缓存。
    if hospital_doctors is not None:
        rhodes_island.medical_hospital_doctor_ids = list(hospital_doctors)
        resolved_power = hospital_power if hospital_power is not None else medical_core._calculate_doctor_power(hospital_doctors)
        rhodes_island.medical_hospital_doctor_power = float(resolved_power)
    else:
        rhodes_island.medical_hospital_doctor_ids = list(
            getattr(rhodes_island, "medical_hospital_doctor_ids", []) or []
        )
        rhodes_island.medical_hospital_doctor_power = float(
            getattr(rhodes_island, "medical_hospital_doctor_power", 0.0) or 0.0
        )

    # 重新计算床位上限，并保持分科结构的有效性。
    rhodes_island.medical_bed_limit = medical_core._calculate_medical_bed_limit(rhodes_island)
    _ensure_specialization_structure(rhodes_island)


def _is_medical_doctor_candidate(
    character_id: int,
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
) -> bool:
    """判断指定角色是否可以被纳入医生候选。

    参数:
        character_id (int): 干员 ID。
        target_base (Optional[game_type.Rhodes_Island]): 目标基地对象。
    返回:
        bool: True 表示符合医生候选条件。
    """
    # 角色 ID 为 0 时必然不可用。
    if character_id == 0:
        return False

    cache = cache_control.cache
    if character_id not in cache.character_data:
        return False

    # 无基地上下文时不处理。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return False

    # 仅允许空岗、门诊或住院岗位的干员。
    character = cache.character_data[character_id]
    work_type = getattr(character, "work", None)
    work_id = getattr(work_type, "work_type", 0) if work_type is not None else 0
    clinic_work_id = medical_constant.MedicalDoctorProfession.CLINICIAN.value
    hospital_work_id = medical_constant.MedicalDoctorProfession.HOSPITALIST.value

    if work_id not in {0, clinic_work_id, hospital_work_id}:
        return False

    # 来访者无法被纳入医生队伍。
    visitor_info = getattr(rhodes_island, "visitor_info", {})
    if character_id in visitor_info:
        return False

    # 校验基础前提，确保干员满足正常工作条件。
    if not handle_premise.handle_normal_2(character_id):
        return False
    if not handle_premise.handle_normal_7(character_id):
        return False

    return True
