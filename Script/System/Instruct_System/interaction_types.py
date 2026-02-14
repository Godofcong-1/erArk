# -*- coding: utf-8 -*-
"""
指令交互类型 - 大类和小类定义
Web模式下使用的新分类系统

大类型：嘴、手、阴茎、道具、技艺、其他（共6个）
- 嘴：对话、亲吻、舔吸（共3个小类）
- 手：抚摸、拍打、穿脱、日常、娱乐、工作（共6个小类）
- 阴茎：摩擦、插入（共2个小类）
- 道具：药物、道具（共2个小类）
- 技艺：信息素、透视、催眠、时停（共4个小类）
- 其他：不属于上述类别的交互

【重构说明】2026-01-19
- 大类和小类不再使用数字，改为小写英语字符串标识符
- 如嘴类从 0 改为 'mouth'，手类从 1 改为 'hand'
- 小类同理，如嘴对话从 0 改为 'mouth_talk'

【重构说明】2026-01-20
- 删除停止交互(stop)大类，该功能不再作为独立的交互类型
"""

from typing import Optional, List


class InteractionMajorType:
    """
    交互大类型
    按照使用的器官/工具分类
    所有值均为小写英语字符串标识符
    """

    MOUTH = "mouth"
    """ 嘴类：使用口腔进行的交互 """

    HAND = "hand"
    """ 手类：使用手进行的交互 """

    SEX = "sex"
    """ 性爱类：与性爱直接相关的交互（开始/结束、基础动作等） """

    PENIS = "penis"
    """ 阴茎类：使用阴茎进行的交互 """

    TOOL = "tool"
    """ 道具类：使用道具/药物进行的交互 """

    ARTS = "arts"
    """ 技艺类：使用源石技艺进行的交互 """

    OTHER = "other"
    """ 其他：不属于上述类别的交互 """


class InteractionMinorType:
    """
    交互小类型
    每个大类下的子分类
    所有值均为小写英语字符串标识符
    """

    # ========== 嘴类（MOUTH='mouth'）小类 ==========
    MOUTH_TALK = "mouth_talk"
    """ 嘴-对话：说话、聊天等语言交流 """

    MOUTH_KISS = "mouth_kiss"
    """ 嘴-亲吻：亲吻、接吻等 """

    MOUTH_LICK = "mouth_lick"
    """ 嘴-舔吸：舔、吸等口部动作 """

    # ========== 手类（HAND='hand'）小类 ==========
    HAND_DAILY = "hand_daily"
    """ 手-日常：日常类的手部交互 """

    HAND_PLAY = "hand_play"
    """ 手-娱乐：娱乐类的手部交互 """

    HAND_WORK = "hand_work"
    """ 手-工作：工作类的手部交互 """

    HAND_SCENE = "hand_scene"
    """ 手-场景：场景类的手部交互 """

    HAND_TOUCH = "hand_touch"
    """ 手-抚摸：摸头、抚摸身体等 """

    HAND_SLAP = "hand_slap"
    """ 手-拍打：打屁股、掌掴等 """

    HAND_DRESS = "hand_dress"
    """ 手-穿脱：穿脱衣物 """

    # ========== 性爱类（SEX='sex'）小类 ==========
    SEX_START_END = "sex_start_end"
    """ 性爱-开始与结束：邀请H、结束H等开始和结束性行为的交互 """

    SEX_BASE = "sex_base"
    """ 性爱-基础：与性爱直接相关的基础交互 """

    # ========== 阴茎类（PENIS='penis'）小类 ==========
    PENIS_RUB = "penis_rub"
    """ 阴茎-摩擦：素股、乳交等 """

    PENIS_INSERT = "penis_insert"
    """ 阴茎-插入：各种体位的性交 """

    # ========== 道具类（TOOL='tool'）小类 ==========
    TOOL_BASE = "tool_base"
    """ 道具-药物：基础 """

    TOOL_DRUG = "tool_drug"
    """ 道具-药物：使用药物 """

    TOOL_ITEM = "tool_item"
    """ 道具-道具：使用道具 """

    # ========== 技艺类（ARTS='arts'）小类 ==========
    ARTS_BASE = "arts_base"
    """ 技艺-基础 """

    ARTS_HORMONE = "arts_hormone"
    """ 技艺-信息素：使用信息素技艺 """

    ARTS_XRAY = "arts_xray"
    """ 技艺-透视：使用透视技艺 """

    ARTS_HYPNOSIS = "arts_hypnosis"
    """ 技艺-催眠：使用催眠技艺 """

    ARTS_TIME_STOP = "arts_time_stop"
    """ 技艺-时停：使用时间停止技艺 """

    # ========== 其他类（OTHER='other'）小类 ==========
    OTHER_ATTRIBUTE = "other_attribute"
    """ 其他-属性：与属性查看或调整相关的交互 """

    OTHER_SAVE = "other_save"
    """ 其他-存档：与存档相关的交互 """

    OTHER_SETTING = "other_setting"
    """ 其他-设置：与系统设置相关的交互 """

    OTHER_MISC = "other_misc"
    """ 其他-杂项：不属于上述类别的交互 """


# 大类型的中文名称映射
MAJOR_TYPE_NAMES = {
    InteractionMajorType.MOUTH: "嘴",
    InteractionMajorType.HAND: "手",
    InteractionMajorType.SEX: "性爱",
    InteractionMajorType.PENIS: "阴茎",
    InteractionMajorType.TOOL: "道具",
    InteractionMajorType.ARTS: "技艺",
    InteractionMajorType.OTHER: "其他",
}

# 大类型的显示顺序
MAJOR_TYPE_ORDER = [
    InteractionMajorType.MOUTH,
    InteractionMajorType.HAND,
    InteractionMajorType.SEX,
    InteractionMajorType.PENIS,
    InteractionMajorType.TOOL,
    InteractionMajorType.ARTS,
    InteractionMajorType.OTHER,
]

# 小类型的中文名称映射
MINOR_TYPE_NAMES = {
    # 嘴类
    InteractionMinorType.MOUTH_TALK: "对话",
    InteractionMinorType.MOUTH_KISS: "亲吻",
    InteractionMinorType.MOUTH_LICK: "舔吸",
    # 手类
    InteractionMinorType.HAND_DAILY: "日常",
    InteractionMinorType.HAND_PLAY: "娱乐",
    InteractionMinorType.HAND_WORK: "工作",
    InteractionMinorType.HAND_SCENE: "场景",
    InteractionMinorType.HAND_TOUCH: "抚摸",
    InteractionMinorType.HAND_SLAP: "拍打",
    InteractionMinorType.HAND_DRESS: "穿脱",
    # 性爱类
    InteractionMinorType.SEX_START_END: "开始与结束",
    InteractionMinorType.SEX_BASE: "基础",
    # 阴茎类
    InteractionMinorType.PENIS_RUB: "摩擦",
    InteractionMinorType.PENIS_INSERT: "插入",
    # 道具类
    InteractionMinorType.TOOL_BASE: "基础",
    InteractionMinorType.TOOL_DRUG: "药物",
    InteractionMinorType.TOOL_ITEM: "道具",
    # 技艺类
    InteractionMinorType.ARTS_BASE: "基础",
    InteractionMinorType.ARTS_HORMONE: "信息素",
    InteractionMinorType.ARTS_XRAY: "透视",
    InteractionMinorType.ARTS_HYPNOSIS: "催眠",
    InteractionMinorType.ARTS_TIME_STOP: "时停",
    # 其他类
    InteractionMinorType.OTHER_ATTRIBUTE: "属性",
    InteractionMinorType.OTHER_SAVE: "存档",
    InteractionMinorType.OTHER_SETTING: "设置",
    InteractionMinorType.OTHER_MISC: "杂项",
}

# 每个大类下的小类列表
MAJOR_TO_MINOR_TYPES = {
    InteractionMajorType.MOUTH: [
        InteractionMinorType.MOUTH_TALK,
        InteractionMinorType.MOUTH_KISS,
        InteractionMinorType.MOUTH_LICK,
    ],
    InteractionMajorType.HAND: [
        InteractionMinorType.HAND_DAILY,
        InteractionMinorType.HAND_PLAY,
        InteractionMinorType.HAND_WORK,
        InteractionMinorType.HAND_SCENE,
        InteractionMinorType.HAND_TOUCH,
        InteractionMinorType.HAND_SLAP,
        InteractionMinorType.HAND_DRESS,
    ],
    InteractionMajorType.SEX: [
        InteractionMinorType.SEX_START_END,
        InteractionMinorType.SEX_BASE,
    ],
    InteractionMajorType.PENIS: [
        InteractionMinorType.PENIS_RUB,
        InteractionMinorType.PENIS_INSERT,
    ],
    InteractionMajorType.TOOL: [
        InteractionMinorType.TOOL_BASE,
        InteractionMinorType.TOOL_DRUG,
        InteractionMinorType.TOOL_ITEM,
    ],
    InteractionMajorType.ARTS: [
        InteractionMinorType.ARTS_BASE,
        InteractionMinorType.ARTS_HORMONE,
        InteractionMinorType.ARTS_XRAY,
        InteractionMinorType.ARTS_HYPNOSIS,
        InteractionMinorType.ARTS_TIME_STOP,
    ],
    InteractionMajorType.OTHER: [
        InteractionMinorType.OTHER_ATTRIBUTE,
        InteractionMinorType.OTHER_SAVE,
        InteractionMinorType.OTHER_SETTING,
        InteractionMinorType.OTHER_MISC,
    ],
}

# 小类到大类的反向映射
MINOR_TO_MAJOR_TYPE = {}
for major, minors in MAJOR_TO_MINOR_TYPES.items():
    for minor in minors:
        MINOR_TO_MAJOR_TYPE[minor] = major


def get_major_type(minor_type: str) -> str:
    """根据小类获取对应的大类"""
    return MINOR_TO_MAJOR_TYPE.get(minor_type, InteractionMajorType.OTHER)


def get_minor_types(major_type: str) -> List[str]:
    """获取大类下的所有小类"""
    return MAJOR_TO_MINOR_TYPES.get(major_type, [InteractionMinorType.OTHER_MISC])


def get_minor_type_name(minor_type: str) -> str:
    """获取小类的中文名称"""
    return MINOR_TYPE_NAMES.get(minor_type, "未知")


def get_major_type_name(major_type: str) -> str:
    """获取大类的中文名称"""
    return MAJOR_TYPE_NAMES.get(major_type, "未知")
