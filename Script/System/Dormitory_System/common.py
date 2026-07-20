import re
from types import FunctionType
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from Script.Core import cache_control, game_type, constant, get_text
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


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

def get_dormitory_resident_id_set() -> Set[int]:
    """
    获取需要纳入宿舍统计的角色id集合
    输入类型: 无
    输出类型: Set[int]
    功能: 在当前拥有干员(cache.npc_id_got)基础上，追加所有异常状态为7(离岛)的角色id，作为宿舍居住统计的统一角色来源
    """
    from Script.Design.handle_premise import handle_normal_7
    resident_id_set: Set[int] = set(cache.npc_id_got)
    resident_id_set.discard(0)
    # 遍历所有角色，追加处于异常7(离岛)状态但不在拥有干员列表中的角色
    for character_id in cache.character_data:
        if character_id == 0:
            continue
        if character_id in resident_id_set:
            continue
        # handle_normal_7 返回0表示角色处于异常7(离岛)状态
        if not handle_normal_7(character_id):
            resident_id_set.add(character_id)
    return resident_id_set


def get_dormitory_occupants_text() -> str:
    """
    获取当前宿舍区内角色分布文本
    输入类型: 无
    输出类型: str
    功能: 遍历所有宿舍，统计每个宿舍内的角色，并生成格式化文本显示宿舍分布情况
    """
    now_text = ""
    # 统一使用通用函数获取需要纳入统计的角色id集合
    resident_id_set = get_dormitory_resident_id_set()
    live_npc_id_set = resident_id_set.copy()
    # 处于异常7(离岛)状态的角色即为居住集合中不在拥有干员列表内的角色
    unnormal_7_npc_id_set = resident_id_set - set(cache.npc_id_got)
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
                chara_name = cache.character_data[npc_id].name
                # 如果是异常7的角色，则在名字后加上离岛
                if npc_id in unnormal_7_npc_id_set:
                    chara_name += _("(离岛)")
                dormitory_npc_name += f"{chara_name}  "
                # W的名字需要单独处理，减掉一个空格
                if chara_name == "W":
                    dormitory_npc_name = dormitory_npc_name[:-1]
                count += 1
                tem_remove_id_set.add(npc_id)
        room_capacity = max(2, count)
        dormitory_son_text += f"({count}/{room_capacity}) {str(dormitory_npc_name).ljust(15,'　')}" # 对齐为15个全角字符
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

def get_layer_by_dormitory_path(dormitory_path: str) -> int:
    """
    从宿舍场景路径中解析层号
    输入类型: dormitory_path(str)
    输出类型: int
    功能: 从宿舍场景路径对应的场景名中解析层号，失败时返回0
    """
    if dormitory_path == "" or dormitory_path not in cache.scene_data:
        return 0
    room_name = cache.scene_data[dormitory_path].scene_name
    match = re.search(r"宿舍(\d)\d{2}房", room_name)
    if not match:
        return 0
    return int(match.group(1))

def check_have_target_dormitory_layer_key(character_id: int, target_layer: int) -> bool:
    """
    检查角色是否持有目标宿舍层的钥匙
    输入类型: character_id(int), target_layer(int)
    输出类型: bool
    功能: 根据目标层号获取对应钥匙的道具ID，检查角色持有数量是否大于0
    """
    if target_layer <= 0:
        return False
    # 构造目标层钥匙的道具ID，格式为 300 + 层号
    target_key_item_id = 300 + target_layer
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.item.get(target_key_item_id, 0) > 0:
        return True
    return False

def check_have_move_target_room_key(character_id: int, target_scene_str: str) -> bool:
    """
    检查角色是否持有移动目标地点的钥匙
    输入类型: character_id(int), target_scene_str(str)
    输出类型: bool
    功能: 根据目标场景路径解析对应层号，获取该层号对应的钥匙道具ID，检查角色持有数量是否大于0
    """
    target_layer = get_layer_by_dormitory_path(target_scene_str)
    if target_layer <= 0:
        return False
    return check_have_target_dormitory_layer_key(character_id, target_layer)


def init_character_dormitory():
    """
    分配角色宿舍
    角色分配到csv里所写的宿舍名所对应的房间坐标
    """
    cache = cache_control.cache
    dormitory = {
        key: constant.place_data[key] for key in constant.place_data if "Dormitory" in key
    }
    dormitory = {
        x: 0 for j in [k[1] for k in sorted(dormitory.items(), key=lambda x: x[0])] for x in j
    }
    special_dormitory = {
        key: constant.place_data[key] for key in constant.place_data if "Special_Dormitory" in key
    }
    special_dormitory = {
        x: 0 for j in [k[1] for k in sorted(special_dormitory.items(), key=lambda x: x[0])] for x in j
    }
    # print("dormitory :",dormitory)
    # print("cache.scene_data[list(Dr_room.keys())[0]].scene_name :",cache.scene_data[list(Dr_room.keys())[0]].scene_name)
    npc_count = 0
    cache.npc_id_got.discard(0)
    for character_id in cache.npc_id_got:
        character_data = cache.character_data[character_id]
        # print(f"{character_data.name}：{character_data.dormitory}")
        # 普通干员每两个人住一个房间
        if character_data.dormitory == "无":
            n = npc_count // 2
            # print(f"debug n :{n}, len(dormitory) :{len(dormitory)}")
            now_room = list(dormitory.keys())[n]
            # print(f"debug now_room = {now_room}")
            character_data.dormitory = now_room
            npc_count += 1
        # 有单独宿舍的干员住在对应宿舍
        else:
            for n in list(dormitory.keys()):
                if cache.scene_data[n].scene_name == character_data.dormitory:
                    # 如果要住宿舍的话，那先检测宿舍是否已经有人住了
                    if "宿舍" in character_data.dormitory:
                        already_live = False
                        for now_character_id in cache.npc_id_got:
                            if now_character_id == character_id:
                                continue
                            now_character_data = cache.character_data[now_character_id]
                            # 如果已经有人住了，则置flag为true，跳出循环
                            if now_character_data.dormitory == character_data.dormitory:
                                already_live = True
                                break
                        # 如果已经有人住了，则换成普通宿舍，重新分配
                        if already_live:
                            character_data.dormitory = "无"
                            init_character_dormitory()
                            break
                        else:
                            character_data.dormitory = n
                            # print(f"debug n :{n}")
                            break
                    # 非宿舍的话直接住
                    else:
                        character_data.dormitory = n
                        # print(f"debug n :{n}")
                        break


def new_character_get_dormitory(character_id: int):
    """
    给新角色分配宿舍
    Keyword arguments:
    character_id -- 角色id
    """
    character_data = cache.character_data[character_id]
    # 分为访客和普通干员
    if character_id in cache.rhodes_island.visitor_info:
        from Script.UI.Panel import invite_visitor_panel
        guest_room = {
            key: constant.place_data[key] for key in constant.place_data if "Guest_Room" in key
        }
        
        # 按照客房编号进行数字排序
        guest_room_sorted = sorted(guest_room["Guest_Room"], key=invite_visitor_panel.sort_guest_room_key)
        
        final_room_list = []
        for room_id in game_config.config_facility_open:
            # 跳过非客房和未开放的客房
            room_name = game_config.config_facility_open[room_id].name
            if _("客房") not in room_name:
                continue
            # 跳过未开放的客房
            cache.rhodes_island.facility_open.setdefault(room_id,False)
            if not cache.rhodes_island.facility_open[room_id]:
                continue
            # 遍历检查是否有同名客房，使用排序后的列表
            for room_full_path in guest_room_sorted:
                if game_config.config_facility_open[room_id].name == room_full_path.split("\\")[-1]:
                    final_room_list.append(room_full_path)
        
        # 查找第一个空闲的客房
        for room_path in final_room_list:
            room_occupied = False
            # 检查是否有其他访客已经住在这个房间
            for now_character_id in cache.rhodes_island.visitor_info:
                if now_character_id == character_id:
                    continue
                now_character_data = cache.character_data[now_character_id]
                if now_character_data.dormitory == room_path:
                    room_occupied = True
                    break
            # 如果房间未被占用，则分配给当前角色
            if not room_occupied:
                character_data.dormitory = room_path
                return
        
        # 如果所有客房都满了，则分配到列表之外（这种情况理论上不应该发生）
        if len(final_room_list) > 0:
            character_data.dormitory = final_room_list[0]
            print(f"警告：所有客房都已满，{character_data.name}被分配到{final_room_list[0]}。请检查访客区设施。")
    else:
        dormitory = {
            key: constant.place_data[key] for key in constant.place_data if "Dormitory" in key
        }
        dormitory = {
            x: 0 for j in [k[1] for k in sorted(dormitory.items(), key=lambda x: x[0])] for x in j
        }
        npc_count = 0
        for now_character_id in cache.npc_id_got:
            now_character_data = cache.character_data[now_character_id]
            # 普通干员每两个人住一个房间
            if "宿舍" in now_character_data.dormitory:
                npc_count += 1
        n = npc_count // 2
        now_room = list(dormitory.keys())[n]
        character_data.dormitory = now_room
