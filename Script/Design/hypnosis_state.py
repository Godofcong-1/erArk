from Script.Core import cache_control, game_type


cache: game_type.Cache = cache_control.cache
"""游戏缓存数据"""


def clear_hypnosis_sub_states(target_character_id: int) -> None:
    """
    清理目标角色退出催眠时结束的心体催眠子状态。
    Keyword arguments:
    target_character_id -- 目标角色id
    Return arguments:
    None
    """
    target_character_data: game_type.Character = cache.character_data[target_character_id]

    target_character_data.hypnosis.increase_body_sensitivity = False
    target_character_data.hypnosis.blockhead = False
    target_character_data.hypnosis.active_h = False
    target_character_data.hypnosis.pain_as_pleasure = False
    target_character_data.hypnosis.roleplay = []
