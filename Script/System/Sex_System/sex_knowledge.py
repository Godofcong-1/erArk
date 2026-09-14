"""性知识推导模块。

性知识是由角色已有的性经验实时推导出的派生数据，不单独写入存档。
部位范围与高潮系统保持一致，包含普通部位、口喉、兽部和心理部位。
"""

from types import FunctionType
from typing import Dict, Iterable, List, Tuple

from Script.Config import game_config
from Script.Core import cache_control, game_type, get_text


cache: game_type.Cache = cache_control.cache
"""游戏缓存数据。"""
_: FunctionType = get_text._
"""翻译接口。"""


# 与 Script.Settle.orgasm_settle.orgasm_part_to_state_id 保持同一套状态编号。
# 这里不直接导入 orgasm_settle，避免性知识模块与高潮结算模块形成循环导入。
KNOWLEDGE_PART_STATE_MAP: Dict[str, int] = {
    "s": 0,
    "b": 1,
    "c": 2,
    "p": 3,
    "v": 4,
    "a": 5,
    "u": 6,
    "w": 7,
    "m": 21,
    "f": 22,
    "h": 23,
}
"""可独立产生快感或高潮的部位标识到快感状态编号的映射。"""

KNOWLEDGE_LEVEL_NONE = 0
"""完全不了解。"""
KNOWLEDGE_LEVEL_LOW = 1
"""略有了解。"""
KNOWLEDGE_LEVEL_BASIC = 2
"""基本了解。"""
KNOWLEDGE_LEVEL_FAMILIAR = 3
"""熟悉。"""
KNOWLEDGE_LEVEL_FULL = 4
"""充分了解。"""

_SCORE_SCALE = 10
"""知识分数倍率，用整数表示百分比权重，避免浮点误差。"""
_GENERAL_INSERTION_WEIGHT = 2
"""通用插入经验的权重，2/10即专属经验的20%。"""


_PART_BASE_EXPERIENCE: Dict[int, Tuple[int, int]] = {
    0: (0, 10),
    1: (1, 11),
    2: (2, 12),
    3: (3, 13),
    4: (4, 14),
    5: (5, 15),
    6: (6, 16),
    7: (7, 17),
    21: (153, 156),  # 口喉经验
    22: (154, 157),  # 兽部经验
    23: (155, 158),  # 心理经验
}
"""各快感部位对应的基础经验和高潮经验编号。"""


_PART_UNCONSCIOUS_EXPERIENCE: Dict[int, int] = {
    0: 70,
    1: 71,
    2: 72,
    3: 73,
    4: 74,
    5: 75,
    6: 76,
    7: 77,
    21: 159,
    22: 160,
    23: 161,
}
"""各快感部位对应的无意识经验编号。"""


_PART_EXTRA_EXPERIENCE: Dict[int, Tuple[int, ...]] = {
    0: (),
    1: (43,),  # 乳交
    2: (),
    3: (),
    4: (61, 65),
    5: (62, 66),
    6: (63, 67),
    7: (64, 68),
    21: (40, 42),  # 接吻、口交
    22: (48,),  # 兽部交
    23: (30, 31, 32, 33, 34, 35, 36, 37),  # 心理快感经验
}
"""各部位可用于推导性知识的补充经验编号。"""


_GENERAL_INSERTION_PART_IDS = {3, 4, 5, 6, 7}
"""会受到通用插入经验影响的部位状态编号。"""


_PART_THEORY_EXPERIENCE: Dict[int, Tuple[int, ...]] = {
    0: (),
    1: (173,),  # 乳交理论经验
    2: (),
    3: (170, 174, 176),  # 手交、性交、榨精理论经验
    4: (174,),  # 性交理论经验
    5: (175,),  # 肛交理论经验
    6: (),
    7: (174,),  # 性交理论经验
    21: (171,),  # 口交理论经验
    22: (),
    23: (),
}
"""各快感部位可直接使用的理论经验编号；没有明确对应关系的理论经验暂不强行分配。"""


if set(KNOWLEDGE_PART_STATE_MAP.values()) != set(_PART_BASE_EXPERIENCE):
    raise ValueError("性知识部位映射与经验映射不一致")
if set(_PART_EXTRA_EXPERIENCE) != set(_PART_BASE_EXPERIENCE):
    raise ValueError("性知识补充经验映射不完整")
if set(_PART_THEORY_EXPERIENCE) != set(_PART_BASE_EXPERIENCE):
    raise ValueError("性知识理论经验映射不完整")
if set(_PART_UNCONSCIOUS_EXPERIENCE) != set(_PART_BASE_EXPERIENCE):
    raise ValueError("性知识无意识经验映射不完整")


def get_supported_part_state_ids() -> Tuple[int, ...]:
    """
    获取性知识系统支持的快感部位状态编号。

    Return arguments:
    tuple[int, ...] -- 支持的快感状态编号，顺序与高潮系统一致。
    """
    return tuple(KNOWLEDGE_PART_STATE_MAP.values())


def is_supported_part(part_state_id: int) -> bool:
    """
    判断指定快感状态是否受性知识系统支持。

    Keyword arguments:
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 该状态是否属于性知识部位。
    """
    return isinstance(part_state_id, int) and part_state_id in _PART_BASE_EXPERIENCE


def _get_experience_value(character_data: game_type.Character, experience_id: int) -> int:
    """
    读取角色指定经验值，并兼容旧存档缺少经验字段的情况。

    Keyword arguments:
    character_data -- 角色数据对象。
    experience_id -- 经验编号。

    Return arguments:
    int -- 非负经验值。
    """
    experience_data = getattr(character_data, "experience", {})
    if not isinstance(experience_data, dict):
        return 0
    try:
        return max(0, int(experience_data.get(experience_id, 0)))
    except (TypeError, ValueError, AttributeError):
        return 0


def get_part_experience_summary(character_id: int, part_state_id: int) -> dict:
    """
    获取指定快感部位的经验构成，供性知识与心理处女系统共同使用。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    dict -- 包含基础、清醒估算、无意识、高潮、专属、理论和通用插入经验的字典；参数无效时返回空字典。
    """
    if not is_supported_part(part_state_id) or cache is None:
        return {}
    character_data = cache.character_data.get(character_id)
    if character_data is None:
        return {}

    base_experience_id, climax_experience_id = _PART_BASE_EXPERIENCE[part_state_id]
    base_value = _get_experience_value(character_data, base_experience_id)
    unconscious_value = _get_experience_value(character_data, _PART_UNCONSCIOUS_EXPERIENCE[part_state_id])
    conscious_value = max(0, base_value - unconscious_value)
    # 基础经验会同时累计清醒与无意识经历，用其比例保守估算高潮、性交和扩张经验中的可认知部分。
    if base_value > 0:
        conscious_ratio = min(1.0, conscious_value / base_value)
    elif unconscious_value > 0:
        conscious_ratio = 0.0
    else:
        conscious_ratio = 1.0
    climax_value = _get_experience_value(character_data, climax_experience_id)
    extra_value = sum(_get_experience_value(character_data, experience_id) for experience_id in _PART_EXTRA_EXPERIENCE.get(part_state_id, ()))
    general_insertion_value = _get_experience_value(character_data, 60) if part_state_id in _GENERAL_INSERTION_PART_IDS else 0
    return {
        "base": base_value,
        # 原结算会在无意识时同时增加基础经验和无意识经验，因此二者相减可保守估算清醒经验。
        "conscious": conscious_value,
        "unconscious": unconscious_value,
        "climax": climax_value,
        "conscious_climax": int(climax_value * conscious_ratio),
        "extra": extra_value,
        "conscious_extra": int(extra_value * conscious_ratio),
        "theory": sum(_get_experience_value(character_data, experience_id) for experience_id in _PART_THEORY_EXPERIENCE.get(part_state_id, ())),
        "general_insertion": general_insertion_value,
        "conscious_general_insertion": int(general_insertion_value * conscious_ratio),
    }


def get_part_knowledge_score(character_id: int, part_state_id: int) -> int:
    """
    根据已有性经验计算指定快感部位的原始知识分数。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号，必须属于支持的部位集合。

    Return arguments:
    int -- 非负知识分数。该分数是内部推导值，不直接展示给玩家。
    """
    if not is_supported_part(part_state_id) or cache is None:
        return 0
    character_data = cache.character_data.get(character_id)
    experience_summary = get_part_experience_summary(character_id, part_state_id)
    if character_data is None or not experience_summary:
        return 0

    # 只有可与无意识记录区分开的清醒经验按完整权重形成知识；无意识经验作为事实保留，但不直接增加认知。
    score = experience_summary["conscious"] * _SCORE_SCALE
    # 高潮经验只有在同部位还存在基础经验或明确行为经验时才计入性知识。
    # 高品质食物等非性行为也可能产生口喉、心理绝顶；孤立绝顶记录不能证明角色获得了对应的性知识。
    confirmed_practical_value = experience_summary["conscious"] + experience_summary["conscious_extra"]
    if confirmed_practical_value > 0:
        conscious_climax_value = experience_summary["conscious_climax"]
        if part_state_id in {21, 23}:
            # 口喉和心理绝顶可能由高品质食物产生；即使日后新增一次真实经历，
            # 也不能让此前积累的全部非性行为绝顶突然转化为性知识。
            conscious_climax_value = min(conscious_climax_value, confirmed_practical_value)
        score += conscious_climax_value * _SCORE_SCALE * 2
    score += experience_summary["conscious_extra"] * _SCORE_SCALE

    # 理论经验直接代表对相关性行为的理解，权重与高潮经验相同。
    score += experience_summary["theory"] * _SCORE_SCALE * 2

    # 插入总经验能提供通用认识，但仅按专属经验的20%影响具体部位，避免不同插入部位相互污染。
    score += experience_summary["conscious_general_insertion"] * _GENERAL_INSERTION_WEIGHT

    # “性无知”是已有的粗粒度认知状态。它不抹除事实经验，只降低由经验推导出的理解程度。
    if getattr(character_data, "talent", {}).get(222, 0):
        score //= 2
    return max(0, score)


def get_part_knowledge_level(character_id: int, part_state_id: int) -> int:
    """
    获取角色对指定快感部位的性知识等级。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    int -- 0 到 4 的知识等级，0 表示完全不了解。
    """
    score = get_part_knowledge_score(character_id, part_state_id)
    if score <= 0:
        return KNOWLEDGE_LEVEL_NONE
    if score <= 2 * _SCORE_SCALE:
        return KNOWLEDGE_LEVEL_LOW
    if score <= 8 * _SCORE_SCALE:
        return KNOWLEDGE_LEVEL_BASIC
    if score <= 20 * _SCORE_SCALE:
        return KNOWLEDGE_LEVEL_FAMILIAR
    return KNOWLEDGE_LEVEL_FULL


def get_knowledge_level_name(level: int) -> str:
    """
    获取可翻译的性知识等级名称。

    Keyword arguments:
    level -- 性知识等级。

    Return arguments:
    str -- 等级对应的文本，异常等级按“完全不了解”处理。
    """
    level_name_dict = {
        KNOWLEDGE_LEVEL_NONE: _("完全不了解"),
        KNOWLEDGE_LEVEL_LOW: _("略有了解"),
        KNOWLEDGE_LEVEL_BASIC: _("基本了解"),
        KNOWLEDGE_LEVEL_FAMILIAR: _("熟悉"),
        KNOWLEDGE_LEVEL_FULL: _("充分了解"),
    }
    try:
        level = int(level)
    except (TypeError, ValueError):
        level = KNOWLEDGE_LEVEL_NONE
    return level_name_dict.get(level, level_name_dict[KNOWLEDGE_LEVEL_NONE])


def get_part_knowledge_name(character_id: int, part_state_id: int) -> str:
    """
    获取指定部位的可翻译性知识等级名称。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    str -- 性知识等级名称。
    """
    level = get_part_knowledge_level(character_id, part_state_id)
    return get_knowledge_level_name(level)


def iter_part_knowledge(character_id: int) -> Iterable[Tuple[int, str, int]]:
    """
    遍历角色所有支持的快感部位及其知识等级。

    Keyword arguments:
    character_id -- 角色编号。

    Return arguments:
    Iterable[Tuple[int, str, int]] -- 状态编号、部位名称、知识等级。
    """
    for part_state_id in get_supported_part_state_ids():
        if part_state_id not in game_config.config_character_state:
            continue
        part_name = game_config.config_character_state[part_state_id].name
        yield part_state_id, part_name, get_part_knowledge_level(character_id, part_state_id)


def get_character_knowledge_text(character_id: int) -> List[str]:
    """
    构建属性页面使用的性知识文本。

    Keyword arguments:
    character_id -- 角色编号。

    Return arguments:
    list[str] -- 每个支持部位一行的可翻译文本。
    """
    knowledge_text: List[str] = []
    for _part_state_id, part_name, level in iter_part_knowledge(character_id):
        knowledge_text.append(_("{0}:{1}").format(part_name, get_knowledge_level_name(level)))
    return knowledge_text
