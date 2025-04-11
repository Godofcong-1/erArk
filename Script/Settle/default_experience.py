import datetime
from Script.Design import (
    settle_behavior,
    map_handle,
    handle_premise
)
from Script.Core import cache_control, constant_effect, game_type

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

def base_chara_experience_common_settle(
        character_id: int,
        experience_id: int,
        base_value: int = 1,
        target_flag: bool = False,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色经验通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    experience_id -- 经验id\n
    base_value -- 基础固定值\n
    target_flag -- 是否加到交互对象身上\n
    change_data -- 状态变更信息记录对象\n
    change_data_to_target_change -- 交互对象结算信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    final_character_id = character_id
    if character_data.dead:
        return
    # 改为加到交互对象身上
    if target_flag:
        final_character_id = character_data.target_character_id
        character_data = cache.character_data[final_character_id]

    # 深度无意识下部分经验不结算
    conscious_experience_set = {30, 31, 32, 33, 34}
    if experience_id in conscious_experience_set and not handle_premise.handle_normal_6(final_character_id):
        return

    # 结算最终值
    character_data.experience.setdefault(experience_id, 0)
    character_data.experience[experience_id] += base_value
    character_data.experience[experience_id] = max(0, character_data.experience[experience_id])

    # 确认结算信息记录对象
    final_change_data = change_data
    if change_data != None and target_flag:
        change_data.target_change.setdefault(final_character_id, game_type.TargetChange())
        final_change_data: game_type.TargetChange = change_data.target_change[final_character_id]
    elif change_data_to_target_change != None:
        change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
        final_change_data: game_type.TargetChange = change_data_to_target_change.target_change[character_id]

    # 结算信息记录对象增加经验
    final_change_data.experience.setdefault(experience_id, 0)
    final_change_data.experience[experience_id] += base_value

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PLACE_ALL_CHARA_ADD_1_BEEN_Hypnosis_EXPERIENCE)
def handle_place_all_chara_add_1_been_hypnosis_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有其他角色均增加1被催眠经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    # 获取当前场景的全角色名单
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    scene_character_list = scene_data.character_list.copy()
    # 去掉里的自己
    if character_id in scene_character_list:
        scene_character_list.remove(character_id)
    for target_id in scene_character_list:
        base_chara_experience_common_settle(target_id, 123, change_data_to_target_change = change_data)
