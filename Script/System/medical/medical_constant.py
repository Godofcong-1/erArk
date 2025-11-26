# -*- coding: UTF-8 -*-
"""医疗经营系统通用常量、枚举与患者结构定义"""
from __future__ import annotations
from types import FunctionType
from Script.Core import get_text

from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Tuple, Dict, List, Any
_: FunctionType = get_text._
""" 翻译函数 """

MEDICAL_ABILITY_ID: int = 46
"""医疗能力 ID（Ability.csv），决定诊疗/手术效率"""

MEDICAL_FACILITY_ID = 6
"""医疗部设施 ID，与医疗系统保持一致"""

SPECIALIZATION_GENERAL_KEY: str = "general"
"""医生分科中的全科标识，表示不限制系统"""

SPECIALIZATION_ROLE_CLINIC: str = "clinic"
"""门诊医生分科角色键值"""

SPECIALIZATION_ROLE_HOSPITAL: str = "hospital"
"""住院医生分科角色键值"""

ROLE_DISPLAY_NAME: Dict[str, str] = {
    SPECIALIZATION_ROLE_CLINIC: _("门诊医生"),
    SPECIALIZATION_ROLE_HOSPITAL: _("住院医生"),
}
"""岗位键到中文名称的映射，供 UI 展示使用"""

SPECIALIZATION_BONUS_PER_LEVEL: float = 0.04
"""医生对应系统时每级医疗能力提供的额外倍率"""

FLOAT_EPSILON: float = 1e-6
"""浮点数比较的通用安全阈值"""

SURGERY_ABILITY_REQUIREMENT: Dict[int, int] = {2: 4, 3: 6}
"""不同病情等级执行手术所需的最低医疗能力等级映射"""

SURGERY_RESOURCE_MULTIPLIER: float = 1.6
"""手术阶段药物需求相对于常规处方的倍率"""

MAX_SURGERY_RECORDS: int = 50
"""医疗系统中手术记录的保留上限"""

MAX_RECENT_REPORTS: int = 7
"""医疗经营日报保留条目上限"""

HOSPITAL_DOCTOR_BED_BONUS: int = 2
"""每名住院医生提供的额外床位数量"""

PLAYER_METADATA_KEYS: Tuple[str, ...] = (
    "player_previous_state",
    "player_session_active",
    "player_used_checks",
    "player_confirmed_complications",
    "player_check_records",
    "player_pending_checks",
)
"""玩家诊疗流程使用的运行期元数据键集合"""

SPECIALIZATION_ROLES: Tuple[str, str] = (
    SPECIALIZATION_ROLE_CLINIC,
    SPECIALIZATION_ROLE_HOSPITAL,
)
"""医疗系统支持的医生岗位键顺序"""

PATIENT_ID_COUNTER = count(1)
"""病人 ID 自增生成器"""

class MedicalPatientState(str, Enum):
    """病人在整个医疗流程中可能出现的状态枚举"""

    REFRESHED = "refreshed"
    """刚刷新尚未接诊"""
    IN_TREATMENT = "in_treatment"
    """由 NPC 医生诊治中"""
    IN_TREATMENT_PLAYER = "in_treatment_player"
    """玩家手动诊治中"""
    WAITING_MEDICATION = "waiting_medication"
    """诊疗完成等待发药"""
    HOSPITALIZED = "hospitalized"
    """已入院治疗"""
    DISCHARGED = "discharged"
    """已完成治疗出院"""

STATE_DISPLAY_NAME: Dict[MedicalPatientState, str] = {
    MedicalPatientState.REFRESHED: _("待诊"),
    MedicalPatientState.IN_TREATMENT: _("干员诊疗中"),
    MedicalPatientState.IN_TREATMENT_PLAYER: _("博士诊疗中"),
    MedicalPatientState.WAITING_MEDICATION: _("等待用药治疗"),
    MedicalPatientState.HOSPITALIZED: _("住院中"),
    MedicalPatientState.DISCHARGED: _("已出院"),
}
"""病人状态中文名称映射表"""

def get_state_display_name(state: MedicalPatientState) -> str:
    """根据状态枚举返回对应的中文名称"""

    if isinstance(state, MedicalPatientState):
        return STATE_DISPLAY_NAME.get(state, state.value)
    return STATE_DISPLAY_NAME.get(state, str(state))

class MedicalPatientPersonality(str, Enum):
    """刷新病人时使用的性格标识，影响自述文本与事件"""

    RATIONAL = "rational"
    """理智病人，描述客观清晰"""
    IRRATIONAL = "irrational"
    """不理智病人，描述夸张混乱"""


class MedicalDoctorProfession(Enum):
    """医疗部医生职业类型，使用 WorkType.csv 中的职业 ID"""

    CLINICIAN = 61
    """坐诊医生，负责门诊诊断"""
    HOSPITALIST = 62
    """住院医生，负责病房管理"""


class MedicalPatientPriority(str, Enum):
    """医疗部病人接诊优先策略枚举"""

    NORMAL = "normal"
    """默认策略，按病情等级常规排序"""
    FOCUS_CRITICAL = "focus_critical"
    """优先处理重症/危重患者"""
    FOCUS_MILD = "focus_mild"
    """优先处理轻症患者，适用于疏导门诊队列"""


class MedicalMedicineResource(Enum):
    """医疗系统涉及的药物资源枚举，与 Resource.csv 对应"""

    NORMAL = 21
    """普通药物，用于处理常规并发症"""
    SUPPRESSANT_SAMPLE = 22
    """感染抑制剂小样，轻症/中症快速控制"""
    SUPPRESSANT_STANDARD = 23
    """感染抑制合剂，主力治疗特效药"""
    SUPPRESSANT_CONCENTRATE = 24
    """感染抑制剂浓缩液，重症/危重用"""


ALL_MEDICINE_RESOURCE_IDS: Tuple[int, ...] = tuple(resource.value for resource in MedicalMedicineResource)
"""医疗系统使用的全部药物资源 ID 元组，用于遍历统一扣药"""


@dataclass
class MedicalPatient:
    """运行期病人结构，统一记录医疗系统所需全部字段与默认值"""

    patient_id: int = 0
    """病人唯一编号（运行时自增生成）"""
    severity_level: int = 0
    """病情等级，来自 MedicalSeverity.csv"""
    complications: List[int] = field(default_factory=list)
    """已抽取并发症 ID 列表"""
    diagnose_progress: float = 0.0
    """诊疗进度（工时单位）"""
    need_resources: Dict[int, float] = field(default_factory=dict)
    """药物需求累计值，key=资源 ID，value=需求数量"""
    state: MedicalPatientState = MedicalPatientState.REFRESHED
    """病人当前状态"""
    stay_days: int = 0
    """已住院天数"""
    need_surgery: bool = False
    """是否需要手术治疗"""
    surgery_blocked: bool = False
    """手术是否因条件不足被阻塞"""
    personality_type: MedicalPatientPersonality = MedicalPatientPersonality.RATIONAL
    """病人性格"""
    race_id: int = 0
    """病人种族 ID（排除博士）"""
    age: int = 18
    """病人年龄"""
    metadata: Dict[str, Any] = field(default_factory=dict)
    """扩展信息字典，存储检查记录、提示等"""

    def ensure_resource_keys(self) -> None:
        """补齐药物需求键，避免读取和累计过程中出现缺省键"""

        for resource_id in ALL_MEDICINE_RESOURCE_IDS:
            self.need_resources.setdefault(resource_id, 0.0)

# 统一定义病人接诊优先策略的文本转换和选项列表
def translate_priority(mode: MedicalPatientPriority) -> str:
    """将病人接诊优先策略转换为用户可读文本"""
    mapping = {
        MedicalPatientPriority.FOCUS_CRITICAL: _("优先重症"),
        MedicalPatientPriority.NORMAL: _("正常排序"),
        MedicalPatientPriority.FOCUS_MILD: _("优先轻症"),
    }
    return mapping.get(mode, "-")

PRIORITY_OPTIONS = [
    (MedicalPatientPriority.FOCUS_CRITICAL, _("优先重症")),
    (MedicalPatientPriority.NORMAL, _("正常排序")),
    (MedicalPatientPriority.FOCUS_MILD, _("优先轻症")),
]

__all__ = [
    "MedicalPatientState",
    "MedicalPatientPersonality",
    "MedicalDoctorProfession",
    "MedicalPatientPriority",
    "MedicalMedicineResource",
    "MEDICAL_ABILITY_ID",
    "MEDICAL_FACILITY_ID",
    "SPECIALIZATION_GENERAL_KEY",
    "SPECIALIZATION_ROLE_CLINIC",
    "SPECIALIZATION_ROLE_HOSPITAL",
    "SPECIALIZATION_BONUS_PER_LEVEL",
    "FLOAT_EPSILON",
    "SURGERY_ABILITY_REQUIREMENT",
    "SURGERY_RESOURCE_MULTIPLIER",
    "MAX_SURGERY_RECORDS",
    "MAX_RECENT_REPORTS",
    "HOSPITAL_DOCTOR_BED_BONUS",
    "PLAYER_METADATA_KEYS",
    "SPECIALIZATION_ROLES",
    "PATIENT_ID_COUNTER",
    "ALL_MEDICINE_RESOURCE_IDS",
    "MedicalPatient",
    "translate_priority",
    "get_state_display_name",
    "PRIORITY_OPTIONS",
]
