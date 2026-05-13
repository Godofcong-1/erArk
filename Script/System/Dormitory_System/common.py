import re
from collections import defaultdict
from typing import Dict, List, Tuple

from Script.Core import cache_control, game_type, constant
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def _get_dormitory_level() -> int:
    """
    获取宿舍区当前等级
    输入类型: 无
    输出类型: int
    功能: 读取罗德岛宿舍区等级，默认1级
    """
    return int(cache.rhodes_island.facility_level.get(4, 1))


def _get_base_open_room_upper_no() -> int:
    """
    获取基础默认开放的宿舍房间上限号
    输入类型: 无
    输出类型: int
    功能: 从1级宿舍区效果文案解析“1区的XXX室”，失败时默认106
    """
    facility_name = game_config.config_facility[4].name
    level_data = game_config.config_facility_effect_data.get(facility_name, {})

    level1_effect_cid = 0
    if isinstance(level_data, dict):
        level1_effect_cid = int(level_data.get(1, 0))
    elif isinstance(level_data, list) and len(level_data) > 1:
        level1_effect_cid = int(level_data[1])

    if level1_effect_cid in game_config.config_facility_effect:
        effect_info = str(game_config.config_facility_effect[level1_effect_cid].info)
        # 示例：宿舍开放至1区的106室
        match = re.search(r"1区的(\d{3})室", effect_info)
        if match:
            return int(match.group(1))

    return 106


def get_dormitory_max_open_layer() -> int:
    """
    根据宿舍区等级获取理论开放层上限
    输入类型: 无
    输出类型: int
    功能: 从 Facility_effect.csv 对应等级说明中解析“开放至X区”，失败时使用保底映射
    """
    dormitory_level = _get_dormitory_level()
    facility_name = game_config.config_facility[4].name

    effect_cid = 0
    if facility_name in game_config.config_facility_effect_data:
        level_data = game_config.config_facility_effect_data[facility_name]
        if isinstance(level_data, dict):
            effect_cid = int(level_data.get(dormitory_level, 0))
        elif isinstance(level_data, list) and 0 <= dormitory_level < len(level_data):
            effect_cid = int(level_data[dormitory_level])

    if effect_cid in game_config.config_facility_effect:
        effect_info = str(game_config.config_facility_effect[effect_cid].info)
        match = re.search(r"开放至(\d)区", effect_info)
        if match:
            return int(match.group(1))

    # 保底值与当前配置表语义一致：1->1区，2->1区，3->3区，4->6区，5->9区。
    fallback = {1: 1, 2: 1, 3: 3, 4: 6, 5: 9}
    return int(fallback.get(dormitory_level, 9))


def get_open_dormitory_rooms_by_layer() -> Dict[int, List[Tuple[str, str]]]:
    """
    统计已开放宿舍房间
    输入类型: 无
    输出类型: Dict[int, List[Tuple[str,str]]]
    功能: 返回已开放房间，key=层号，value=[(房间名, 场景路径)]
    """
    result: Dict[int, List[Tuple[str, str]]] = defaultdict(list)
    scene_name_to_path = {}
    for scene_path in cache.scene_data:
        scene_name_to_path[cache.scene_data[scene_path].scene_name] = scene_path

    max_open_layer = get_dormitory_max_open_layer()
    dormitory_level = _get_dormitory_level()
    base_open_room_upper_no = _get_base_open_room_upper_no()

    for open_cid, open_data in game_config.config_facility_open.items():
        room_name = open_data.name
        if not cache.rhodes_island.facility_open.get(open_cid, False):
            continue
        # 严格按宿舍房间命名格式过滤，避免受语言翻译文本影响。
        match = re.fullmatch(r"宿舍(\d)\d{2}房", room_name)
        if not match:
            continue
        layer = int(match.group(1))
        if layer <= 0 or layer > max_open_layer:
            continue
        room_path = scene_name_to_path.get(room_name, "")
        if room_path:
            result[layer].append((room_name, room_path))

    # 等级1时，101-106为基础默认开放房，未配置在 Facility_open 中，需补齐。
    if dormitory_level >= 1 and max_open_layer >= 1:
        for room_no in range(101, base_open_room_upper_no + 1):
            room_name = f"宿舍{room_no}房"
            room_path = scene_name_to_path.get(room_name, "")
            if room_path:
                result[1].append((room_name, room_path))

    for layer in result:
        # 去重后排序，避免基础补齐与配置项发生重复。
        unique_room = {name: path for name, path in result[layer]}
        result[layer] = sorted(unique_room.items(), key=lambda x: x[0])
    return dict(result)


def get_open_dormitory_room_paths_by_layer(layer: int) -> List[str]:
    """
    获取指定层可巡查的开放宿舍路径列表
    输入类型: layer(int)
    输出类型: List[str]
    功能: 从统一宿舍开放统计结果中提取指定层的房间路径
    """
    if layer <= 0:
        return []

    open_rooms_by_layer = get_open_dormitory_rooms_by_layer()
    if layer not in open_rooms_by_layer:
        return []

    return [room_path for _, room_path in open_rooms_by_layer[layer]]

def get_dormitory_occupants_text() -> str:
    """
    获取当前宿舍区内角色分布文本
    输入类型: 无
    输出类型: str
    功能: 遍历所有宿舍，统计每个宿舍内的角色，并生成格式化文本显示宿舍分布情况
    """
    now_text = ""
    live_npc_id_set = cache.npc_id_got.copy()
    Dormitory_all = constant.place_data["Dormitory"] + constant.place_data["Special_Dormitory"] # 合并普通和特殊宿舍
    # 遍历所有宿舍
    dormitory_count = 0 # 用来计数宿舍总数量
    pre_dormitory_name = "100" # 用来保存上一个宿舍名字
    for dormitory_place in Dormitory_all:
        count = 0
        tem_remove_id_set = set() # 用来保存需要删除id的临时set
        dormitory_name = dormitory_place.split("\\")[-1]
        dormitory_son_text = f"    [{dormitory_name}]："
        # 遍历角色id
        dormitory_npc_name = ""
        for npc_id in live_npc_id_set:
            live_dormitory = cache.character_data[npc_id].dormitory
            # 如果该角色住在该宿舍，则在text中加入名字信息
            if live_dormitory == dormitory_place:
                dormitory_npc_name += f"{cache.character_data[npc_id].name}  "
                # W的名字需要单独处理，减掉一个空格
                if cache.character_data[npc_id].name == "W":
                    dormitory_npc_name = dormitory_npc_name[:-1]
                count += 1
                tem_remove_id_set.add(npc_id)
            # 宿舍满2人则中断循环
            if count >= 2:
                break
        dormitory_son_text += f"{str(dormitory_npc_name).ljust(15,'　')}" # 对齐为15个全角字符
        # 在id集合中删掉本次已经出现过的id
        for npc_id in tem_remove_id_set:
            live_npc_id_set.discard(npc_id)
        # 宿舍有人则显示该宿舍
        if count:
            # 换区或者单独宿舍则换行
            if dormitory_name[0] != pre_dormitory_name[0]:
                now_text += "\n"
                dormitory_count = 0
                if dormitory_name[0] not in {"梅","莱"}:
                    now_text += "\n"
            # 每5个宿舍换行
            elif dormitory_count % 5 == 0:
                now_text += "\n"
            pre_dormitory_name = dormitory_name # 更新上一个宿舍名字
            now_text += dormitory_son_text
            dormitory_count += 1
    return now_text
