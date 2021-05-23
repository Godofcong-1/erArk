from Script.Core import cache_control, constant, game_type
from Script.Design import map_handle, update

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def own_charcter_move(target_scene: list):
    """
    主角寻路至目标场景
    Keyword arguments:
    target_scene -- 寻路目标场景(在地图系统下的绝对坐标)
    """
    while 1:
        character_data: game_type.Character = cache.character_data[0]
        if character_data.position != target_scene:
            (
                move_now,
                now_path_list,
                now_target_position,
                now_need_time,
            ) = character_move(0, target_scene)
            if move_now == "Null":
                break
            character_data.behavior.behavior_id = constant.Behavior.MOVE
            character_data.behavior.move_target = now_target_position
            character_data.behavior.duration = now_need_time
            character_data.state = constant.CharacterStatus.STATUS_MOVE
            update.game_update_flow(now_need_time)
        else:
            break
    cache.character_data[0].target_character_id = 0
    cache.now_panel_id = constant.Panel.IN_SCENE


def character_move(character_id: int, target_scene: list) -> (str, list, list, int):
    """
    通用角色移动控制
    Keyword arguments:
    character_id -- 角色id
    target_scene -- 寻路目标场景(在地图系统下的绝对坐标)
    Return arguments:
    str:null -- 未找到路径
    str:end -- 当前位置已是路径终点
    list -- 路径
    list -- 本次移动到的位置
    int -- 本次移动花费的时间
    """
    now_position = cache.character_data[character_id].position
    if now_position == target_scene:
        return "end", [], [], 0
    now_position_str = map_handle.get_map_system_path_str_for_list(now_position)
    target_scene_str = map_handle.get_map_system_path_str_for_list(target_scene)
    if (
        now_position_str not in map_handle.scene_path_edge
        or target_scene_str not in map_handle.scene_path_edge[now_position_str]
    ):
        return "null", [], [], 0
    now_path_data = map_handle.scene_path_edge[now_position_str][target_scene_str]
    return "", [], now_path_data[0], now_path_data[1]
