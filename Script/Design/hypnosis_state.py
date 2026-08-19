from Script.Core import cache_control, game_type


cache: game_type.Cache = cache_control.cache
"""游戏缓存数据"""


def clear_hypnosis_behavior_mode(target_character_id: int) -> None:
    """
    清理目标角色当前所处的催眠行为模式（平然/空气/木头人/逆推/角色扮演），使其回到无模式状态。
    Keyword arguments:
    target_character_id -- 目标角色id
    Return arguments:
    None
    """
    target_character_data: game_type.Character = cache.character_data[target_character_id]
    target_character_data.hypnosis.blockhead = False
    # 逆推模式下由催眠驱动的NPC主动标志随模式一并清理，普通H中玩家指定的主动状态不受影响
    if target_character_data.hypnosis.active_h:
        target_character_data.h_state.npc_active_h = False
    target_character_data.hypnosis.active_h = False
    target_character_data.hypnosis.roleplay = []
    # 无意识标志1~3为睡眠/醉酒/时停等非催眠域状态，仅催眠域内的4~7才随模式清理复位
    if target_character_data.sp_flag.unconscious_h in {4, 5, 6, 7}:
        target_character_data.sp_flag.unconscious_h = 0


def clear_hypnosis_sub_states(target_character_id: int) -> None:
    """
    清理目标角色退出催眠时结束的心体催眠子状态。
    Keyword arguments:
    target_character_id -- 目标角色id
    Return arguments:
    None
    """
    target_character_data: game_type.Character = cache.character_data[target_character_id]

    clear_hypnosis_behavior_mode(target_character_id)
    target_character_data.hypnosis.increase_body_sensitivity = False
    target_character_data.hypnosis.pain_as_pleasure = False
