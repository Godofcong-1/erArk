# -*- coding: UTF-8 -*-
"""医疗经营系统通用常量、枚举与患者结构定义"""
from __future__ import annotations
from types import FunctionType
from Script.Core import get_text

from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Tuple, Dict, List, Any, Optional, ClassVar, Mapping, Iterable
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

WAITING_QUEUE_STATES: Tuple[MedicalPatientState, ...] = (
    MedicalPatientState.REFRESHED,
    MedicalPatientState.IN_TREATMENT,
    MedicalPatientState.IN_TREATMENT_PLAYER,
)
"""门诊排队人数统计所使用的待诊状态元组"""

ASSIGNABLE_PATIENT_STATE_SET = frozenset(
    {
        MedicalPatientState.REFRESHED,
        MedicalPatientState.IN_TREATMENT,
    }
)
"""门诊医生可以接诊的病人状态集合，过滤掉玩家占用等特殊状态"""

WAITING_QUEUE_STATE_SET = frozenset(WAITING_QUEUE_STATES)
"""待诊状态的只读集合，便于在热点路径中进行常数时间判断"""


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
    assigned_doctor_id: int = 0
    """当前绑定的门诊医生编号（0 表示未绑定）"""
    assigned_hospital_doctor_id: int = 0
    """当前绑定的住院医生编号（0 表示未绑定）"""
    severity_name: str = ""
    """病情等级对应的名称标签，用于 UI 展示"""
    price_ratio: float = 1.0
    """刷新/接诊时记录的收费系数快照"""
    complication_trace: List[Dict[str, Any]] = field(default_factory=list)
    """并发症追踪记录，包含系统/部位等辅助信息"""
    system_keys: List[str] = field(default_factory=list)
    """病人关联的生理系统标签集合（字符串形式）"""
    player_session_active: bool = False
    """标记玩家诊疗会话是否处于激活状态"""
    player_previous_state: str = ""
    """玩家介入前病人的原始状态字符串"""
    player_used_checks: int = 0
    """本次玩家诊疗流程已使用的检查次数"""
    player_confirmed_complications: List[int] = field(default_factory=list)
    """玩家诊疗流程中已确诊的并发症 ID 列表"""
    player_check_records: List[Dict[str, Any]] = field(default_factory=list)
    """玩家诊疗流程中产生的检查记录摘要列表"""
    player_pending_checks: List[Dict[str, Any]] = field(default_factory=list)
    """玩家诊疗流程中等待执行的检查计划列表"""
    last_surgery_result: str = ""
    """最近一次手术流程的结果标识"""
    surgery_blocked_resource: Optional[int] = None
    """导致手术阻塞的药物资源 ID，None 表示不存在阻塞"""
    state_label: str = ""
    """调试用途的最新状态字符串"""
    medicine_recorded: Dict[int, float] = field(default_factory=dict)
    """累计登记但尚未扣除的药品需求量"""
    medicine_progress: Dict[int, float] = field(default_factory=dict)
    """住院每日用药进度缓存"""
    medicine_consumed_units: Dict[int, int] = field(default_factory=dict)
    """历史累计消耗的药物单位数"""
    last_consumed_units: Dict[int, int] = field(default_factory=dict)
    """最近一次用药操作实际消耗的资源记录"""

    def ensure_resource_keys(self) -> None:
        """补齐药物需求键，避免读取和累计过程中出现缺省键"""

        for resource_id in ALL_MEDICINE_RESOURCE_IDS:
            self.need_resources.setdefault(resource_id, 0.0)


@dataclass
class MedicalDailyCounters:
    """医疗系统当日统计结构体，统一维护所有计数项。

    该结构替代历史上使用的临时字典字段，提供显性的属性与辅助方法，
    便于在运行期与日志渲染阶段保持字段名称一致性。
    """

    diagnose_completed_outpatient: int = 0
    """今日完成诊疗的门诊病人数"""
    diagnose_completed_hospital: int = 0
    """今日完成诊疗的住院病人数"""
    medicine_completed_outpatient: int = 0
    """今日成功发药的门诊病人数"""
    medicine_completed_hospital: int = 0
    """今日成功发药的住院病人数"""
    outpatient_waiting_medicine: int = 0
    """今日仍在等待发药的门诊病人数"""
    hospital_waiting_medicine: int = 0
    """今日仍在等待发药的住院病人数"""
    hospitalized_today: int = 0
    """今日新增入院的病人数"""
    discharged_today: int = 0
    """今日完成出院的病人数"""
    medicine_consumed: int = 0
    """今日消耗的药品总单位数"""
    surgeries_performed: int = 0
    """今日成功执行的手术次数"""

    DISPLAY_NAME_MAPPING: ClassVar[Dict[str, str]] = {
        "diagnose_completed_outpatient": _("门诊诊疗完成"),
        "diagnose_completed_hospital": _("住院诊疗完成"),
        "medicine_completed_outpatient": _("门诊发药完成"),
        "medicine_completed_hospital": _("住院发药完成"),
        "outpatient_waiting_medicine": _("门诊待发药"),
        "hospital_waiting_medicine": _("住院待发药"),
        "hospitalized_today": _("今日入院"),
        "discharged_today": _("今日出院"),
        "medicine_consumed": _("药品消耗单位"),
        "surgeries_performed": _("手术完成次数"),
    }
    """字段展现用的中文名称映射，供 UI 友好展示使用。"""

    @classmethod
    def from_mapping(cls, source: Optional[object]) -> "MedicalDailyCounters":
        """根据传入对象生成规范化的统计数据实例。

        参数:
            source (Optional[object]): 允许为 dict、同类对象或 None。
        返回:
            MedicalDailyCounters: 规范化后的统计实例，缺省数据置零。
        """

        # --- 若源对象已是目标类型则直接返回，避免重复拷贝 ---
        if isinstance(source, cls):
            return source

        # --- 构造默认实例，并在给定映射时逐项转写字段 ---
        counters = cls()
        if isinstance(source, Mapping):
            for key, value in source.items():
                counters.set_value(str(key), int(value or 0))
        return counters

    def set_value(self, key: str, value: int) -> None:
        """将指定字段设置为给定数值。

        参数:
            key (str): 目标字段名称。
            value (int): 需要写入的整型数值。
        返回:
            None
        """

        # --- 找不到对应属性时直接忽略，防止非法键破坏数据结构 ---
        if key not in self.__dataclass_fields__:
            return

        # --- 写入整型后的安全值，保证负值同样被允许记录 ---
        setattr(self, key, int(value))

    def bump(self, key: str, delta: int) -> None:
        """在指定字段上累加增量。

        参数:
            key (str): 目标字段名称。
            delta (int): 需要累加的增量值，可为正负数。
        返回:
            None
        """

        # --- 零增量无需写入，直接返回避免多余操作 ---
        if delta == 0:
            return

        # --- 解析字段名称并确认其存在 ---
        if key not in self.__dataclass_fields__:
            return

        # --- 执行累加并覆盖原值，统一保持整型 ---
        current_value = int(getattr(self, key, 0))
        setattr(self, key, current_value + int(delta))

    def reset(self) -> None:
        """将全部统计字段重置为零。

        返回:
            None
        """

        # --- 遍历所有 dataclass 字段并逐项清零 ---
        for field_name in self.__dataclass_fields__:
            setattr(self, field_name, 0)

    def as_dict(self) -> Dict[str, int]:
        """以字典形式返回统计数据。

        返回:
            Dict[str, int]: 统计字段到整型值的映射。
        """

        # --- 将所有显性字段转写为纯整数字典 ---
        return {field: int(getattr(self, field, 0)) for field in self.__dataclass_fields__}

    def items(self) -> Iterable[Tuple[str, int]]:
        """返回可迭代的字段键值对，用于 UI 展示。

        返回:
            Iterable[Tuple[str, int]]: 以 (字段名, 数值) 形式输出的可迭代对象。
        """

        # --- 直接遍历字典形式的数据，以保持输出顺序稳定 ---
        for key, value in self.as_dict().items():
            yield key, value


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
    "SPECIALIZATION_ROLES",
    "PATIENT_ID_COUNTER",
    "ALL_MEDICINE_RESOURCE_IDS",
    "MedicalPatient",
    "translate_priority",
    "get_state_display_name",
    "PRIORITY_OPTIONS",
    "WAITING_QUEUE_STATES",
    "WAITING_QUEUE_STATE_SET",
    "MedicalDailyCounters",
]
