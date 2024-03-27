import os
import json
from Script.Core import cache_control, value_handle, game_type
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
scene_path_edge_path = os.path.join("data", "ScenePath")
""" 寻路路径配置文件路径 """
scene_path_edge = {}
""" 寻路路径 """
width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def get_map_draw_for_map_path(map_path_str: str) -> str:
    """
    从地图路径获取地图绘制数据
    Keyword arguments:
    map_path -- 地图路径
    """
    map_data = get_map_data_for_map_path(map_path_str)
    return map_data.map_draw


def get_scene_id_in_map_for_scene_path_on_map_path(scene_path: list, map_path: list) -> list:
    """
    获取场景在地图上的相对位置
    Keyword arguments:
    scene_path -- 场景路径
    map_path -- 地图路径
    """
    return scene_path[len(map_path)]


def get_map_for_path(scene_path: list) -> list:
    """
    查找场景所在地图路径
    Keyword arguments:
    scene_path -- 场景路径
    """
    map_path = scene_path[:-1]
    map_path_str = get_map_system_path_str_for_list(map_path)
    if map_path_str in cache.map_data:
        return map_path
    return get_map_for_path(map_path)


def get_map_data_for_map_path(map_path_str: str) -> game_type.Map:
    """
    从地图路径获取地图数据
    Keyword arguments:
    map_path -- 地图路径
    Return arguments:
    game_type.Map -- 地图数据
    """
    return cache.map_data[map_path_str]


def get_scene_list_for_map(map_path_str: str) -> list:
    """
    获取地图下所有场景
    Keyword arguments:
    map_path -- 地图路径
    """
    map_data = get_map_data_for_map_path(map_path_str)
    scene_list = list(map_data.path_edge.keys())
    return scene_list


def get_scene_name_list_for_map_path(map_path_str: str):
    """
    获取地图下所有场景的名字
    Keyword arguments:
    map_path -- 地图路径
    """
    scene_list = get_scene_list_for_map(map_path_str)
    scene_name_data = {}
    for scene in scene_list:
        load_scene_data = get_scene_data_for_map(map_path_str, scene)
        scene_name = load_scene_data.scene_name
        scene_name_data[scene] = scene_name
    return scene_name_data


def character_move_scene(old_scene_path: list, new_scene_path: list, character_id: int):
    """
    将角色移动至新场景
    Keyword arguments:
    old_scene_path -- 旧场景路径
    new_scene_path -- 新场景路径
    character_id -- 角色id
    """
    old_scene_path_str = get_map_system_path_str_for_list(old_scene_path)
    new_scene_path_str = get_map_system_path_str_for_list(new_scene_path)
    character_data = cache.character_data[character_id]
    # 从旧场景移除角色
    if character_id in cache.scene_data[old_scene_path_str].character_list:
        cache.scene_data[old_scene_path_str].character_list.remove(character_id)
    # 在新场景添加角色
    if character_id not in cache.scene_data[new_scene_path_str].character_list:
        character_data.position = new_scene_path
        cache.scene_data[new_scene_path_str].character_list.add(character_id)
    # 如果角色已经在新场景角色列表中，但位置还没有移动到新场景，则移动位置
    elif character_data.position != new_scene_path:
        character_data.position = new_scene_path
    # 刷新移动起止位置
    character_data.behavior.move_src = old_scene_path
    character_data.behavior.move_target = new_scene_path
    # 清零最终目的地
    if new_scene_path == character_data.behavior.move_final_target:
        character_data.behavior.move_final_target = []
        # print(f"debug {character_data.name} 清零最终目的地")


def get_map_system_path_str_for_list(now_list: list) -> str:
    """
    将地图路径列表数据转换为字符串
    Keyword arguments:
    now_list -- 地图路径列表数据
    """
    # print(f"debug now_list = {now_list}")
    return os.sep.join(now_list)


def get_path_finding(map_path_str: str, now_node: str, target_node: str) -> (str, game_type.TargetPath):
    """
    查询寻路路径
    Keyword arguments:
    map_path -- 地图路径
    now_node -- 当前节点相对位置
    target_node -- 目标节点相对位置
    Return arguments:
    str:end -- 寻路路径终点
    game_type.TargetPath -- 寻路路径
    """
    if now_node == target_node:
        return "End", game_type.TargetPath()
    else:
        return (
            "",
            cache.map_data[map_path_str].sorted_path[now_node][target_node],
        )


def get_scene_to_scene_map_list(now_scene_path: list, target_scene_path: list) -> (str, list):
    """
    获取场景到场景之间需要经过的地图列表
    如果两个场景属于同一地图并在同一层级，则返回common
    Keyword arguments:
    now_scene_path -- 当前场景路径
    target_scene_path -- 目标场景路径
    Return arguments:
    str:common -- 两个场景在同一层级
    list -- 场景层级路径列表
    """
    scene_affiliation = judge_scene_affiliation(now_scene_path, target_scene_path)
    if scene_affiliation == "common":
        return "common", []
    elif scene_affiliation == "subordinate":
        return (
            "",
            get_map_hierarchy_list_for_scene_path(now_scene_path, target_scene_path),
        )
    elif scene_affiliation == "nobelonged":
        common_map = get_common_map_for_scene_path(now_scene_path, target_scene_path)
        now_scene_to_common_map = get_map_hierarchy_list_for_scene_path(now_scene_path, common_map)
        target_scene_to_common_map = get_map_hierarchy_list_for_scene_path(target_scene_path, common_map)
        common_map_to_target_scene = value_handle.reverse_array_list(target_scene_to_common_map)
        return "", now_scene_to_common_map + common_map_to_target_scene[1:]


def get_common_map_for_scene_path(scene_a_path: list, scene_b_path: list) -> list:
    """
    查找场景共同所属地图
    Keyword arguments:
    scene_aPath -- 场景A路径
    scene_bpath -- 场景B路径
    """
    hierarchy = []
    if scene_a_path[:-1] == [] or scene_b_path[:-1] == []:
        return hierarchy
    else:
        for i in range(0, len(scene_a_path)):
            try:
                if scene_a_path[i] == scene_b_path[i]:
                    hierarchy.append(scene_a_path[i])
                else:
                    break
            except IndexError:
                break
        return get_map_path_for_true(hierarchy)


def get_map_hierarchy_list_for_scene_path(now_scene_path: list, target_scene_path: list) -> list:
    """
    查找当前场景到目标场景之间的层级列表(仅当当前场景属于目标场景的子场景时可用)
    Keyword arguments:
    now_scene_path -- 当前场景路径
    target_scene_path -- 目标场景路径
    Return arguments:
    hierarchy_list -- 当前场景路径到目标场景路径之间的层级列表
    """
    hierarchy_list = []
    now_path = None
    while True:
        if now_path is None:
            now_path = now_scene_path[:-1]
        if now_path != target_scene_path:
            hierarchy_list.append(now_path)
            now_path = now_path[:-1]
        else:
            break
    return hierarchy_list


def get_map_path_for_true(map_path: list) -> list:
    """
    判断地图路径是否是有效的地图路径，若不是，则查找上层路径，直到找到有效地图路径并返回
    Keyword arguments:
    map_path -- 当前地图路径
    """
    map_path_str = get_map_system_path_str_for_list(map_path)
    if map_path_str in cache.map_data:
        return map_path
    else:
        new_map_path = map_path[:-1]
        return get_map_path_for_true(new_map_path)


def judge_scene_is_affiliation(now_scene_path: list, target_scene_path: list) -> str:
    """
    获取场景所属关系
    当前场景属于目标场景的子场景 -> 返回'subordinate'
    目标场景属于当前场景的子场景 -> 返回'superior'
    other -> 返回'common'
    Keyword arguments:
    now_scene_path -- 当前场景路径
    target_scene_path -- 目标场景路径
    """
    if judge_scene_affiliation(now_scene_path, target_scene_path) == "subordinate":
        return "subordinate"
    elif judge_scene_affiliation(target_scene_path, now_scene_path) == "subordinate":
        return "superior"
    return "common"


def judge_scene_affiliation(now_scene_path: list, target_scene_path: list) -> str:
    """
    判断场景有无所属关系
    当前场景属于目标场景的子场景 -> 返回'subordinate'
    当前场景与目标场景的第一个上级场景相同 -> 返回'common'
    other -> 返回'nobelonged'
    Keyword arguments:
    now_scene_path -- 当前场景路径
    target_scene_path -- 目标场景路径
    """
    judge = 1
    for i in range(len(now_scene_path)):
        if len(target_scene_path) - 1 >= i:
            if now_scene_path[i] != target_scene_path[i]:
                judge = 0
                break
        if i > len(target_scene_path) - 1:
            break
        if target_scene_path[i] != now_scene_path[i]:
            judge = 0
            break
    if judge:
        return "subordinate"
    now_father = now_scene_path[:-1]
    target_father = target_scene_path[:-1]
    if now_father == target_father:
        return "common"
    return "nobelonged"


def get_relation_map_list_for_scene_path(scene_path: list) -> list:
    """
    获取场景所在所有直接地图(当前场景id为0，所在地图在上层地图相对位置也为0，视为直接地图)位置
    Keyword arguments:
    scene_path -- 当前场景路径
    """
    now_path = scene_path
    now_map_path = scene_path[:-1]
    now_pathId = now_path[-1]
    map_list = []
    if now_map_path != [] and now_map_path[:-1] != []:
        map_list.append(now_map_path)
        if now_pathId == "0":
            return map_list + get_relation_map_list_for_scene_path(now_map_path)
        else:
            return map_list
    else:
        map_list.append(now_map_path)
        return map_list


def get_scene_data_for_map(map_path_str: str, map_scene_id: str) -> game_type.Scene:
    """
    载入地图下对应场景数据
    Keyword arguments:
    map_path -- 地图路径
    map_scene_id -- 场景相对位置
    Return arguments:
    game_type.Scene -- 场景数据
    """
    if map_path_str == "":
        scene_path_str = map_scene_id
    else:
        scene_path_str = map_path_str + os.sep + str(map_scene_id)
    scene_path = get_map_system_path_for_str(scene_path_str)
    scene_path = get_scene_path_for_true(scene_path)
    scene_path_str = get_map_system_path_str_for_list(scene_path)
    return cache.scene_data[scene_path_str]


def get_scene_path_for_map_scene_id(map_path: list, map_scene_id: str) -> list:
    """
    从场景在地图中的相对位置获取场景路径
    Keyword arguments:
    map_path -- 地图路径
    map_scene_id -- 场景在地图中的相对位置
    """
    new_scene_path = map_path.copy()
    new_scene_path.append(map_scene_id)
    new_scene_path = get_scene_path_for_true(new_scene_path)
    return new_scene_path


def get_map_system_path_for_str(path_str: str) -> list:
    """
    将地图系统路径文本转换为地图系统路径
    """
    return path_str.split(os.sep)


def get_map_scene_id_for_scene_path(map_path: list, scene_path: list) -> str:
    """
    从场景路径查找场景在地图中的相对位置
    Keyword arguments:
    map_path -- 地图路径
    scene_path -- 场景路径
    """
    return scene_path[len(map_path)]


def get_scene_path_for_true(scene_path: list) -> list:
    """
    获取场景的有效路径(当前路径下若不存在场景数据，则获取当前路径下相对位置为0的路径)
    Keyword arguments:
    scene_path -- 场景路径
    """
    scene_path_str = get_map_system_path_str_for_list(scene_path)
    # print(f"debug scene_path_str = {scene_path_str} ")
    # print(f"debug cache.scene_data = {cache.scene_data} ")
    if scene_path_str in cache.scene_data:
        return scene_path
    else:
        scene_path.append("0")
        return get_scene_path_for_true(scene_path)


def get_map_door_data_for_scene_path(scene_path: list) -> dict:
    """
    从场景路径获取当前地图到其他地图的门数据
    Keyword arguments:
    scene_path -- 场景路径
    """
    map_path = get_map_for_path(scene_path)
    map_path_str = get_map_system_path_str_for_list(map_path)
    return get_map_door_data(map_path_str)


def get_map_door_data(map_path_str: str) -> dict:
    """
    获取地图下通往其他地图的门数据
    Keyword arguments:
    map_path -- 地图路径
    """
    map_data = cache.map_data[map_path_str]
    if "MapDoor" in map_data:
        return map_data["MapDoor"]
    else:
        return {}


def get_scene_character_name_list(scene_path_str: str, remove_own_character=False) -> list:
    """
    获取场景上所有角色的姓名列表
    Keyword arguments:
    scene_path -- 场景路径
    remove_own_character -- 从姓名列表中移除主角 (default False)
    """
    scene_character_data = cache.scene_data[scene_path_str].character_list
    now_scene_character_list = list(scene_character_data)
    name_list = []
    if remove_own_character:
        now_scene_character_list.remove(0)
    for character_id in now_scene_character_list:
        character_name = cache.character_data[character_id].name
        name_list.append(character_name)
    return name_list


def get_character_id_by_character_name(character_name: str, scene_path_str: str) -> str:
    """
    获取场景上角色姓名对应的角色id
    Keyword arguments:
    character_name -- 角色姓名
    scene_path -- 场景路径
    """
    character_nameList = get_scene_character_name_list(scene_path_str)
    character_nameIndex = character_nameList.index(character_name)
    character_idList = get_scene_character_id_list(scene_path_str)
    return character_idList[character_nameIndex]


def get_scene_character_id_list(scene_path_str: str) -> list:
    """
    获取场景上所有角色的id列表
    Keyword arguments:
    scene_path -- 场景路径
    """
    return list(cache.scene_data[scene_path_str].character_list)


def sort_scene_character_id(scene_path_str: str):
    """
    对场景上的角色按好感度进行排序
    Keyword arguments:
    scene_path -- 场景路径
    """
    now_scene_character_intimate_data = {}
    for character in cache.scene_data[scene_path_str].character_list:
        now_scene_character_intimate_data[character] = cache.character_data[character].intimate
    new_scene_character_intimate_data = sorted(
        now_scene_character_intimate_data.items(),
        key=lambda x: (x[1], -int(x[0])),
        reverse=True,
    )
    new_scene_character_intimate_data = value_handle.two_bit_array_to_dict(
        new_scene_character_intimate_data
    )
    cache.scene_data[scene_path_str].character_list = set(new_scene_character_intimate_data)


def init_scene_edge_path_data():
    """初始化全部地图寻路数据"""
    global scene_path_edge
    scene_path_edge = {}
    for now_position_str in cache.scene_data:
        scene_path_edge[now_position_str] = {}
        # 忽略大地图
        if "泰拉" in now_position_str:
            continue
        for target_scene_str in cache.scene_data:
            if target_scene_str == now_position_str:
                continue
            # 忽略大地图
            if "泰拉" in target_scene_str:
                continue
            now_position = get_map_system_path_for_str(now_position_str)
            target_scene = get_map_system_path_for_str(target_scene_str)
            scene_hierarchy = judge_scene_affiliation(now_position, target_scene)
            if scene_hierarchy == "common":
                map_path = get_common_map_for_scene_path(now_position, target_scene)
                now_map_scene_id = get_map_scene_id_for_scene_path(map_path, now_position)
                target_map_scene_id = get_map_scene_id_for_scene_path(map_path, target_scene)
                tem_1, tem_2, now_move_target, now_move_time = identical_map_move(
                    now_position, map_path, now_map_scene_id, target_map_scene_id
                )
            else:
                tem_1, tem_2, now_move_target, now_move_time = difference_map_move(now_position, target_scene)
            scene_path_edge[now_position_str][target_scene_str] = [now_move_target, now_move_time]
    with open(scene_path_edge_path, "w") as path_edge_file:
        json.dump(scene_path_edge, path_edge_file)


def difference_map_move(now_position: list, target_scene: list) -> (str, list, list, int):
    """
    角色跨地图层级移动
    Keyword arguments:
    target_scene -- 寻路目标场景(在地图系统下的绝对坐标)
    Return arguments:
    str:null -- 未找到路径
    str:end -- 当前位置已是路径终点
    list -- 路径
    list -- 本次移动到的位置
    int -- 本次移动花费的时间
    """
    is_affiliation = judge_scene_affiliation(now_position, target_scene)
    now_true_position = get_scene_path_for_true(now_position)
    now_true_map = get_map_for_path(now_true_position)
    if is_affiliation == "subordinate":
        now_true_affiliation = judge_scene_is_affiliation(now_true_position, target_scene)
        if now_true_affiliation == "subordinate":
            now_map_scene_id = get_map_scene_id_for_scene_path(now_true_map, now_true_position)
            return identical_map_move(now_position, now_true_map, now_map_scene_id, "0")
        now_map = get_map_for_path(target_scene)
        now_map_scene_id = get_map_scene_id_for_scene_path(now_map, now_position)
        return identical_map_move(now_position, now_map, now_map_scene_id, "0")
    relation_map_list = get_relation_map_list_for_scene_path(now_true_position)
    now_scene_real_map = relation_map_list[-1]
    now_map_scene_id = get_map_scene_id_for_scene_path(now_scene_real_map, now_true_position)
    common_map = get_common_map_for_scene_path(now_true_position, target_scene)
    if now_scene_real_map != common_map:
        if now_map_scene_id == "0":
            now_true_position = now_scene_real_map.copy()
            relation_map_list = get_relation_map_list_for_scene_path(now_true_position)
            now_scene_real_map = relation_map_list[-1]
    target_map_scene_id = get_map_scene_id_for_scene_path(common_map, target_scene)
    if now_scene_real_map == common_map:
        now_map_scene_id = get_map_scene_id_for_scene_path(common_map, now_true_position)
    else:
        now_map_scene_id = get_map_scene_id_for_scene_path(now_scene_real_map, now_true_position)
        target_map_scene_id = "0"
        common_map = now_scene_real_map
    return identical_map_move(now_position, common_map, now_map_scene_id, target_map_scene_id)


def identical_map_move(
    now_position: list,
    now_map: list,
    now_map_scene_id: str,
    target_map_scene_id: str,
) -> (str, list, list, int):
    """
    角色在相同地图层级内移动
    Keyword arguments:
    now_position -- 当前场景位置
    now_map -- 当前地图路径
    now_map_scene_id -- 当前角色所在场景(当前地图层级下的相对坐标)
    target_map_scene_id -- 寻路目标场景(当前地图层级下的相对坐标)
    Return arguments:
    str:null -- 未找到路径
    str:end -- 当前位置已是路径终点
    list -- 路径
    list -- 本次移动到的位置
    int -- 本次移动花费的时间
    """
    now_map_str = get_map_system_path_str_for_list(now_map)
    move_end, move_path = get_path_finding(now_map_str, now_map_scene_id, target_map_scene_id)
    now_target_position = []
    now_need_time = 0
    if move_path != []:
        now_target_scene_id = move_path.path[0]
        now_need_time = move_path.time[0]
        now_target_position = get_scene_path_for_map_scene_id(now_map, now_target_scene_id)
    return move_end, move_path, now_target_position, now_need_time

def judge_scene_accessible(target_scene_str : str, character_id : int) -> int :
    """
    判断目标地点是否可以进入
    Keyword arguments:
    target_scene_str -- 目标场景位置（例：A\B\C）
    Return arguments:
    str -- open:可以进入,wait_open:未解锁,door_lock:门上锁,private:私密场所
    """

    # print(f"debug target_scene_str = {target_scene_str}")
    now_scene_data = cache.scene_data[target_scene_str]
    character_data = cache.character_data[character_id]
    pl_character_data = cache.character_data[0]
    # print(f"debug now_scene_data.name = {now_scene_data.scene_name}")

    # 遍历设施开放清单，如果名称和地图名称一样的话，则进行判断
    for open_cid in game_config.config_facility_open:
        # print(f"debug game_config.config_facility_open[open_cid].name = {game_config.config_facility_open[open_cid].name}")
        if game_config.config_facility_open[open_cid].name == now_scene_data.scene_name:

            # 如果该设施已开放，则正常通过
            if cache.rhodes_island.facility_open[open_cid]:
                return "open"
            # 是玩家的话输出提示信息
            elif character_id == 0:
                # 获取设施的解锁条件数据
                facility_effect_cid = game_config.config_facility_open[open_cid].zone_cid
                facility_npc_cid = game_config.config_facility_open[open_cid].NPC_id

                # 如果是需要设施等级解锁的话
                info_text = ""
                if facility_effect_cid:
                    zone_data = game_config.config_facility_effect[facility_effect_cid]
                    zone_name,zone_lv = zone_data.name,str(zone_data.level)
                    info_text += f"\n  ●目标移动房间——{now_scene_data.scene_name}，当前尚未解锁，解锁需要将{zone_name}升到{zone_lv}级\n"
                # 也可能需要NPC才能解锁
                if facility_npc_cid:
                    for character_id in cache.character_data:
                        character_data = cache.character_data[character_id]
                        if character_data.adv == facility_npc_cid:
                            info_text += f"\n  ●目标移动房间——{now_scene_data.scene_name}，当前尚未解锁，解锁需要获得干员{character_data.name}\n"
                            break

                line = draw.LineDraw("-", width)
                line.draw()
                info_draw = draw.WaitDraw()
                info_draw.text = info_text
                info_draw.width = width
                info_draw.draw()

            return "wait_open"

    # 锁门判断
    if now_scene_data.close_flag == 1:
        # 即使关门，也可以进去自己的宿舍
        if character_data.dormitory == target_scene_str:
            pass
        # 助理可以进锁门了的玩家房间
        elif character_id and character_id == pl_character_data.assistant_character_id:
            pass
        # 博士可以无条件进博士房间和博士办公室
        elif character_id == 0 and ("Dr_room" in now_scene_data.scene_tag or "Dr_office" in now_scene_data.scene_tag):
            pass
        else:
            # 如果是玩家的话输出提示信息
            if character_id == 0:
                line = draw.LineDraw("-", width)
                line.draw()
                info_draw = draw.WaitDraw()
                info_draw.text = f"\n  ●目标移动房间——{now_scene_data.scene_name}，当前门是锁着的，需要钥匙或其他方法进入\n"
                info_draw.width = width
                info_draw.draw()
            return "door_lock"

    # 私密场所判断，仅限干员
    if character_id:
        # 博士房间
        if "Dr_room" in now_scene_data.scene_tag:
            # 助理可以进
            if character_id == pl_character_data.assistant_character_id:
                pass
            else:
                return "private"
        # 男厕所
        elif "Toilet_Male" in now_scene_data.scene_tag:
            return "private"
        # 非自己的宿舍
        elif "Dormitory" in now_scene_data.scene_tag and character_data.dormitory != target_scene_str:
            return "private"

    return "open"

def judge_scene_name_open(full_scene_str : str) -> int :
    """
    通过地点名判断目标地点是否可以进入
    Keyword arguments:
    full_scene_str -- 目标场景位置（例：A\B\C）
    Return arguments:
    int -- 是否可以进入
    """
    from Script.Config import game_config
    now_scene_data = cache.scene_data[full_scene_str]

    # print(f"debug scene_name = {now_scene_data.scene_name}")
    # 遍历设施开放清单，如果名称和地图名称一样的话，则进行判断
    for open_cid in game_config.config_facility_open:
        # print(f"debug game_config.config_facility_open[open_cid].name = {game_config.config_facility_open[open_cid].name}")
        if game_config.config_facility_open[open_cid].name == now_scene_data.scene_name:
            if cache.rhodes_island.facility_open[open_cid]:
                return 1
            else:
                return 0

    # 关了门的房间进不去
    if now_scene_data.close_flag == 1:
        return 0

    return 1
