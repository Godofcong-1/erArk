"""部位心理处女系统。

心理处女表示角色是否已经认识到某个快感部位经历过具有性意义的刺激。
系统使用经验、意识与事后发现证据进行判断，并保存已经形成的认知，避免状态随污浊清除而倒退。
"""

from types import FunctionType
from typing import Dict, Iterable, List, Set, Tuple

from Script.Config import game_config
from Script.Core import cache_control, game_type, get_text
from Script.System.Sex_System import sex_knowledge


cache: game_type.Cache = cache_control.cache
"""游戏缓存数据。"""
_: FunctionType = get_text._
"""翻译接口。"""


MENTAL_VIRGINITY_INTACT = 0
"""没有已知性经历，心理处女保有。"""
MENTAL_VIRGINITY_UNAWARE = 1
"""客观上存在性经历，但角色尚未意识到。"""
MENTAL_VIRGINITY_SUSPECTED = 2
"""角色察觉到异常或性刺激，但尚未完全确认。"""
MENTAL_VIRGINITY_LOST = 3
"""角色已经明确理解该部位经历过具有性意义的刺激。"""


_PART_FIRST_RECORD_IDS: Dict[int, Tuple[int, ...]] = {
    0: (0, 1, 4, 5, 10, 11),
    1: (3,),
    2: (),
    3: (),
    4: (6,),
    5: (8,),
    6: (9,),
    7: (7,),
    21: (2, 15),
    22: (12, 13, 14),
    23: (),
}
"""快感状态编号到部位交初体验记录编号的映射。"""


_BODY_EVIDENCE_TO_PART_IDS: Dict[int, Tuple[int, ...]] = {
    0: (0,),
    1: (0,),
    2: (21,),
    3: (1,),
    4: (0,),
    5: (0,),
    6: (4,),
    7: (7,),
    8: (5,),
    9: (6,),
    10: (0,),
    11: (0,),
    12: (22,),
    13: (22,),
    14: (22,),
    15: (21,),
    16: (0,),
    17: (0,),
    18: (0,),
}
"""无意识期间身体污浊部位到心理处女快感部位的映射。"""


_CLOTH_EVIDENCE_TO_PART_IDS: Dict[int, Tuple[int, ...]] = {
    0: (0,),
    1: (0,),
    2: (0, 22),
    3: (0,),
    4: (21,),
    5: (0, 1),
    6: (1,),
    7: (0,),
    8: (0,),
    9: (2, 4, 5, 6),
    10: (0,),
    11: (0,),
    12: (0,),
    13: (0,),
}
"""无意识期间衣物污浊部位到可能被察觉的快感部位映射。"""


_EXPERIENCE_TO_PART_IDS: Dict[int, Set[int]] = {}
"""经验编号到受影响快感部位的反向索引。"""


def _register_experience(experience_id: int, part_state_id: int) -> None:
    """
    向经验反向索引登记一个部位。

    Keyword arguments:
    experience_id -- 经验编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    None -- 仅更新模块内部映射。
    """
    _EXPERIENCE_TO_PART_IDS.setdefault(experience_id, set()).add(part_state_id)


# 反向索引覆盖基础、高潮、无意识、专属、理论和通用插入经验，供通用经验结算入口快速筛选。
for _part_id, (_base_id, _climax_id) in sex_knowledge._PART_BASE_EXPERIENCE.items():
    _register_experience(_base_id, _part_id)
    _register_experience(_climax_id, _part_id)
    _register_experience(sex_knowledge._PART_UNCONSCIOUS_EXPERIENCE[_part_id], _part_id)
    for _experience_id in sex_knowledge._PART_EXTRA_EXPERIENCE[_part_id]:
        _register_experience(_experience_id, _part_id)
    for _experience_id in sex_knowledge._PART_THEORY_EXPERIENCE[_part_id]:
        _register_experience(_experience_id, _part_id)
# 通用插入经验只提供低权重知识，不作为任一具体部位实际发生性经历的证据，
# 因此不登记到心理处女的经验触发索引中。


def _get_character_data(character_id: int):
    """
    安全读取角色数据。

    Keyword arguments:
    character_id -- 角色编号。

    Return arguments:
    Character|None -- 角色数据，不存在时为None。
    """
    if cache is None or not isinstance(character_id, int):
        return None
    return cache.character_data.get(character_id)


def _get_record_dict(character_data: game_type.Character) -> dict:
    """
    获取角色心理处女认知记录并兼容旧存档异常字段。

    Keyword arguments:
    character_data -- 角色数据对象。

    Return arguments:
    dict -- 可写入的心理处女认知字典。
    """
    record_dict = getattr(character_data, "mental_virginity", None)
    if not isinstance(record_dict, dict):
        record_dict = {}
        character_data.mental_virginity = record_dict
    return record_dict


def is_part_applicable(character_id: int, part_state_id: int) -> bool:
    """
    判断指定快感部位是否适用于角色自身的心理处女显示。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 是否适用。通用部位始终适用，生殖器官按性别、兽部按相关身体素质判断。
    """
    character_data = _get_character_data(character_id)
    if character_data is None or not sex_knowledge.is_supported_part(part_state_id):
        return False
    if character_data.sex == 0 and part_state_id in {2, 4, 7}:
        return False
    if character_data.sex == 1 and part_state_id == 3:
        return False
    if part_state_id == 22:
        talent_data = getattr(character_data, "talent", {})
        return isinstance(talent_data, dict) and any(talent_data.get(talent_id, 0) for talent_id in (111, 112, 113, 114, 115, 116))
    return True


def _has_first_record(character_data: game_type.Character, part_state_id: int) -> bool:
    """
    判断指定部位是否存在初体验或高潮履历。

    Keyword arguments:
    character_data -- 角色数据对象。
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 是否存在可证明实际经历的履历。
    """
    first_record = getattr(character_data, "first_record", None)
    if first_record is None:
        return False
    # 初吻使用独立字段保存，不在first_part_sex_dict中；它同样是口喉部位的明确经历。
    if part_state_id == 21 and getattr(first_record, "first_kiss_id", -1) != -1:
        return True
    part_record_dict = getattr(first_record, "first_part_sex_dict", {})
    if isinstance(part_record_dict, dict) and any(record_id in part_record_dict for record_id in _PART_FIRST_RECORD_IDS.get(part_state_id, ())):
        return True
    for record_name in ("first_strong_orgasm_dict", "first_super_orgasm_dict"):
        record_dict = getattr(first_record, record_name, {})
        if isinstance(record_dict, dict) and part_state_id in record_dict:
            return True
    return False


def _has_confirmed_actual_experience(character_data: game_type.Character, part_state_id: int, summary: dict) -> bool:
    """
    判断指定部位是否存在足以证明实际性经历的数据。

    绝顶经验不单独作为证明：部分旧存档会仅残留口喉、心理绝顶计数，却没有对应的
    基础经验、行为经验或初体验履历。将这种孤立计数直接视为性经历会造成心理处女误判。

    Keyword arguments:
    character_data -- 角色数据对象。
    part_state_id -- 快感状态编号。
    summary -- 性知识模块生成的经验构成。

    Return arguments:
    bool -- 是否存在基础经历、无意识经历、明确行为经历或初体验履历。
    """
    return (
        summary.get("base", 0) > 0
        or summary.get("unconscious", 0) > 0
        or summary.get("extra", 0) > 0
        or _has_first_record(character_data, part_state_id)
    )


def _get_derived_state(character_id: int, part_state_id: int) -> int:
    """
    根据累计数据保守推导心理处女状态，用于新角色和旧存档兜底。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    int -- 推导出的心理处女状态。
    """
    character_data = _get_character_data(character_id)
    summary = sex_knowledge.get_part_experience_summary(character_id, part_state_id)
    if character_data is None or not summary:
        return MENTAL_VIRGINITY_INTACT

    # 理论知识本身不会使心理处女失去；孤立的旧绝顶计数也不足以证明实际性经历。
    has_actual_experience = _has_confirmed_actual_experience(character_data, part_state_id, summary)
    if not has_actual_experience:
        return MENTAL_VIRGINITY_INTACT

    knowledge_level = sex_knowledge.get_part_knowledge_level(character_id, part_state_id)
    has_conscious_experience = any(summary[key] > 0 for key in ("conscious", "conscious_climax", "conscious_extra"))
    if has_conscious_experience:
        if knowledge_level >= sex_knowledge.KNOWLEDGE_LEVEL_BASIC:
            return MENTAL_VIRGINITY_LOST
        return MENTAL_VIRGINITY_SUSPECTED
    return MENTAL_VIRGINITY_UNAWARE


def get_part_mental_virginity_state(character_id: int, part_state_id: int) -> int:
    """
    获取角色指定快感部位的心理处女状态。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    int -- 0保有、1无自觉、2怀疑、3已失去；无效参数按保有处理。
    """
    character_data = _get_character_data(character_id)
    if character_data is None or not sex_knowledge.is_supported_part(part_state_id):
        return MENTAL_VIRGINITY_INTACT
    record_dict = _get_record_dict(character_data)
    try:
        recorded_state = int(record_dict.get(part_state_id, MENTAL_VIRGINITY_INTACT))
    except (TypeError, ValueError):
        recorded_state = MENTAL_VIRGINITY_INTACT
    recorded_state = max(MENTAL_VIRGINITY_INTACT, min(recorded_state, MENTAL_VIRGINITY_LOST))
    return max(recorded_state, _get_derived_state(character_id, part_state_id))


def record_part_mental_virginity_state(character_id: int, part_state_id: int, state: int) -> int:
    """
    固化角色已经形成的心理处女认知；普通流程只允许状态前进，避免清洗或换装后倒退。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。
    state -- 要记录的状态编号。

    Return arguments:
    int -- 写入后的状态；参数无效时返回保有。
    """
    character_data = _get_character_data(character_id)
    if character_data is None or not sex_knowledge.is_supported_part(part_state_id):
        return MENTAL_VIRGINITY_INTACT
    try:
        state = int(state)
    except (TypeError, ValueError):
        state = MENTAL_VIRGINITY_INTACT
    state = max(MENTAL_VIRGINITY_INTACT, min(state, MENTAL_VIRGINITY_LOST))
    record_dict = _get_record_dict(character_data)
    current_state = get_part_mental_virginity_state(character_id, part_state_id)
    final_state = max(current_state, state)
    if final_state > MENTAL_VIRGINITY_INTACT:
        record_dict[part_state_id] = final_state
    return final_state


def update_from_experience(character_id: int, experience_id: int, unconscious: bool = False) -> None:
    """
    在经验结算后刷新受影响部位的心理处女认知。

    Keyword arguments:
    character_id -- 获得经验的角色编号。
    experience_id -- 本次增加的经验编号。
    unconscious -- 本次经验是否发生于无意识状态。

    Return arguments:
    None -- 仅更新角色的认知记录。
    """
    character_data = _get_character_data(character_id)
    if character_data is None or character_id == 0:
        return
    experience_config = game_config.config_experience.get(experience_id)
    if experience_config is None:
        return
    experience_type = experience_config.type
    for part_state_id in _EXPERIENCE_TO_PART_IDS.get(experience_id, set()):
        # 理论经验只会让角色重新思考已有经历，不会单独制造一次“失去”。
        if experience_type == 12:
            if get_part_mental_virginity_state(character_id, part_state_id) == MENTAL_VIRGINITY_UNAWARE:
                if sex_knowledge.get_part_knowledge_level(character_id, part_state_id) >= sex_knowledge.KNOWLEDGE_LEVEL_BASIC:
                    record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_SUSPECTED)
            continue
        # 旧存档和少数结算路径可能只有绝顶计数而没有对应的基础或行为经验。
        # 先等待同次行为的明确经验结算，再推进心理处女，避免仅凭孤立绝顶计数误判。
        if experience_type == 2:
            summary = sex_knowledge.get_part_experience_summary(character_id, part_state_id)
            if not _has_confirmed_actual_experience(character_data, part_state_id, summary):
                continue
        if unconscious or experience_type == 4:
            record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_UNAWARE)
            continue
        knowledge_level = sex_knowledge.get_part_knowledge_level(character_id, part_state_id)
        if knowledge_level >= sex_knowledge.KNOWLEDGE_LEVEL_BASIC:
            record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_LOST)
        else:
            record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_SUSPECTED)


def record_unconscious_discovery(character_id: int, body_part_ids: Iterable[int], cloth_part_ids: Iterable[int]) -> None:
    """
    记录角色恢复意识后从身体和衣物污浊中发现的性经历证据。

    Keyword arguments:
    character_id -- 角色编号。
    body_part_ids -- 无意识期间出现精液的身体部位编号。
    cloth_part_ids -- 无意识期间出现精液的衣物部位编号。

    Return arguments:
    None -- 根据知识等级将相关部位推进至怀疑或已失去。
    """
    strong_evidence_part_ids: Set[int] = set()
    weak_evidence_part_ids: Set[int] = {23}
    for body_part_id in body_part_ids:
        strong_evidence_part_ids.update(_BODY_EVIDENCE_TO_PART_IDS.get(body_part_id, ()))
    for cloth_part_id in cloth_part_ids:
        weak_evidence_part_ids.update(_CLOTH_EVIDENCE_TO_PART_IDS.get(cloth_part_id, ()))
    # 身体上的直接证据可以在知识充分时形成确认。
    for part_state_id in strong_evidence_part_ids:
        if not is_part_applicable(character_id, part_state_id):
            continue
        knowledge_level = sex_knowledge.get_part_knowledge_level(character_id, part_state_id)
        if knowledge_level >= sex_knowledge.KNOWLEDGE_LEVEL_BASIC:
            record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_LOST)
        else:
            record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_SUSPECTED)
    # 衣物污浊和服装失窃只能说明可能发生过性行为，无法确认具体部位，最多推进到怀疑。
    for part_state_id in weak_evidence_part_ids:
        if is_part_applicable(character_id, part_state_id):
            record_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_SUSPECTED)


def get_mental_virginity_state_name(state: int) -> str:
    """
    获取可翻译的心理处女状态名称。

    Keyword arguments:
    state -- 心理处女状态编号。

    Return arguments:
    str -- 对应状态名称，异常值按“保有”处理。
    """
    state_name_dict = {
        MENTAL_VIRGINITY_INTACT: _("保有"),
        MENTAL_VIRGINITY_UNAWARE: _("无自觉"),
        MENTAL_VIRGINITY_SUSPECTED: _("怀疑"),
        MENTAL_VIRGINITY_LOST: _("已失去"),
    }
    try:
        state = int(state)
    except (TypeError, ValueError):
        state = MENTAL_VIRGINITY_INTACT
    return state_name_dict.get(state, state_name_dict[MENTAL_VIRGINITY_INTACT])


def get_part_mental_virginity_name(character_id: int, part_state_id: int) -> str:
    """
    获取角色指定部位的心理处女状态名称。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    str -- 可直接用于属性页或口上的状态名称。
    """
    return get_mental_virginity_state_name(get_part_mental_virginity_state(character_id, part_state_id))


def is_part_mental_virginity_state(character_id: int, part_state_id: int, state: int) -> bool:
    """
    判断角色指定部位是否处于给定心理处女状态，供口上和事件前提调用。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。
    state -- 要匹配的心理处女状态。

    Return arguments:
    bool -- 当前状态是否与给定状态相同。
    """
    return get_part_mental_virginity_state(character_id, part_state_id) == state


def is_part_mental_virginity_intact(character_id: int, part_state_id: int) -> bool:
    """
    判断角色指定部位的心理处女是否处于“保有”。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 仅“保有”状态返回True。
    """
    return is_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_INTACT)


def is_part_mental_virginity_unaware(character_id: int, part_state_id: int) -> bool:
    """
    判断角色指定部位的心理处女是否处于“无自觉”。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 仅“无自觉”状态返回True。
    """
    return is_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_UNAWARE)


def is_part_mental_virginity_suspected(character_id: int, part_state_id: int) -> bool:
    """
    判断角色指定部位的心理处女是否处于“怀疑”。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 仅“怀疑”状态返回True。
    """
    return is_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_SUSPECTED)


def is_part_mental_virginity_lost(character_id: int, part_state_id: int) -> bool:
    """
    判断角色指定部位的心理处女是否处于“已失去”。

    Keyword arguments:
    character_id -- 角色编号。
    part_state_id -- 快感状态编号。

    Return arguments:
    bool -- 仅“已失去”状态返回True。
    """
    return is_part_mental_virginity_state(character_id, part_state_id, MENTAL_VIRGINITY_LOST)


def iter_character_mental_virginity(character_id: int, include_inapplicable: bool = False) -> Iterable[Tuple[int, str, int]]:
    """
    遍历角色各快感部位的心理处女状态。

    Keyword arguments:
    character_id -- 角色编号。
    include_inapplicable -- 是否包含角色自身不具备的器官和兽部。

    Return arguments:
    Iterable[Tuple[int, str, int]] -- 快感状态编号、部位名称、心理处女状态。
    """
    for part_state_id in sex_knowledge.get_supported_part_state_ids():
        if not include_inapplicable and not is_part_applicable(character_id, part_state_id):
            continue
        if part_state_id not in game_config.config_character_state:
            continue
        yield part_state_id, game_config.config_character_state[part_state_id].name, get_part_mental_virginity_state(character_id, part_state_id)


def get_character_mental_virginity_text(character_id: int) -> List[str]:
    """
    构建属性页面使用的心理处女状态文本。

    Keyword arguments:
    character_id -- 角色编号。

    Return arguments:
    list[str] -- 角色适用部位的心理处女状态文本。
    """
    return [
        _("{0}:{1}").format(part_name, get_mental_virginity_state_name(state))
        for _part_state_id, part_name, state in iter_character_mental_virginity(character_id)
    ]
