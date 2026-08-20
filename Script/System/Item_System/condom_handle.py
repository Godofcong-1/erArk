from typing import Dict, List, Tuple

from Script.Core import cache_control, game_type

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def check_collection_data(character_id: int = 0):
    """
    校验玩家收藏品结构体中避孕套存量池字段是否存在（旧存档兼容），不存在则补上\n
    Keyword arguments:\n
    character_id -- 角色id（仅玩家0有存量池）\n
    Return arguments:\n
    无
    """
    pl_collection = cache.character_data[0].pl_collection
    if not hasattr(pl_collection, "used_condoms"):
        pl_collection.used_condoms = []


def check_dirty_data(character_id: int):
    """
    校验角色污浊结构体中装饰避孕套字段是否存在（旧存档兼容），不存在则补上\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    无
    """
    dirty_data = cache.character_data[character_id].dirty
    if not hasattr(dirty_data, "condom_decoration"):
        dirty_data.condom_decoration = {}


def get_used_condoms() -> List[int]:
    """
    获取玩家的用过的避孕套存量池\n
    Return arguments:\n
    List[int] -- 存量池列表，每个元素为该避孕套内的精液量(ml)
    """
    check_collection_data()
    return cache.character_data[0].pl_collection.used_condoms


def add_used_condom(semen_count: int):
    """
    向存量池中添加一个用过的避孕套（戴套射精时调用）\n
    Keyword arguments:\n
    semen_count -- 该避孕套内的精液量(ml)\n
    Return arguments:\n
    无
    """
    check_collection_data()
    cache.character_data[0].pl_collection.used_condoms.append(semen_count)


def clear_used_condoms():
    """
    清空存量池（下一次H开始时调用），挂在角色身上的装饰不受影响\n
    Return arguments:\n
    无
    """
    check_collection_data()
    cache.character_data[0].pl_collection.used_condoms = []


def get_decoration_dict(character_id: int) -> Dict[tuple, List[int]]:
    """
    获取挂在指定角色身上的装饰避孕套字典（存储在该角色的污浊结构体中）\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    Dict[tuple, List[int]] -- 键为(部位类型, 部位cid)，值为各套精液量列表
    """
    check_dirty_data(character_id)
    return cache.character_data[character_id].dirty.condom_decoration


def get_decoration_count(character_id: int, part_type: int, part_cid: int) -> int:
    """
    获取指定角色指定部位上挂着的装饰避孕套个数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    part_type -- 部位类型，0=身体（仅头发0），1=服装部位\n
    part_cid -- 部位cid\n
    Return arguments:\n
    int -- 该部位上的装饰避孕套个数
    """
    decoration_dict = get_decoration_dict(character_id)
    return len(decoration_dict.get((part_type, part_cid), []))


def get_decoration_total_count(character_id: int) -> int:
    """
    获取指定角色全身挂着的装饰避孕套总个数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    int -- 装饰避孕套总个数
    """
    decoration_dict = get_decoration_dict(character_id)
    return sum(len(value) for value in decoration_dict.values())


def get_decoration_level(decoration_count: int) -> int:
    """
    根据部位上的装饰避孕套个数计算描述等级\n
    1级为1个，2级为2个，3级为3到5个，4级为6到10个，5级为10个以上\n
    Keyword arguments:\n
    decoration_count -- 该部位上的装饰避孕套个数\n
    Return arguments:\n
    int -- 描述等级(1~5)，个数为0时返回0
    """
    if decoration_count <= 0:
        return 0
    if decoration_count == 1:
        return 1
    if decoration_count == 2:
        return 2
    if decoration_count <= 5:
        return 3
    if decoration_count <= 10:
        return 4
    return 5


def move_to_decoration(character_id: int, part_type: int, part_cid: int, condom_index_list: List[int]) -> int:
    """
    将存量池中指定编号的避孕套转移为指定角色指定部位的装饰\n
    Keyword arguments:\n
    character_id -- 角色id\n
    part_type -- 部位类型，0=身体（仅头发0），1=服装部位\n
    part_cid -- 部位cid\n
    condom_index_list -- 存量池中要转移的避孕套下标列表\n
    Return arguments:\n
    int -- 实际转移的个数
    """
    used_condoms = get_used_condoms()
    decoration_dict = get_decoration_dict(character_id)
    location_key = (part_type, part_cid)
    decoration_dict.setdefault(location_key, [])
    # 下标从大到小移除，避免移除时下标错位
    move_count = 0
    for index in sorted(set(condom_index_list), reverse=True):
        if 0 <= index < len(used_condoms):
            decoration_dict[location_key].append(used_condoms.pop(index))
            move_count += 1
    return move_count


def take_back_decoration(character_id: int, location_index_list: List[Tuple[tuple, int]]) -> int:
    """
    将指定角色身上的装饰避孕套取回存量池\n
    Keyword arguments:\n
    character_id -- 角色id\n
    location_index_list -- 要取回的装饰列表，每个元素为((部位类型, 部位cid), 该部位列表中的下标)\n
    Return arguments:\n
    int -- 实际取回的个数
    """
    used_condoms = get_used_condoms()
    decoration_dict = get_decoration_dict(character_id)
    # 按部位分组后下标从大到小移除，避免移除时下标错位
    take_count = 0
    for location_key, index in sorted(set(location_index_list), key=lambda x: (x[0], -x[1])):
        now_list = decoration_dict.get(location_key, [])
        if 0 <= index < len(now_list):
            used_condoms.append(now_list.pop(index))
            take_count += 1
    # 清理空部位
    for location_key in list(decoration_dict.keys()):
        if not decoration_dict[location_key]:
            del decoration_dict[location_key]
    return take_count


def consume_condoms(condom_index_list: List[int]) -> List[int]:
    """
    从存量池中消耗指定编号的避孕套（饮用/挤出时调用）\n
    Keyword arguments:\n
    condom_index_list -- 存量池中要消耗的避孕套下标列表\n
    Return arguments:\n
    List[int] -- 被消耗的各套精液量(ml)列表
    """
    used_condoms = get_used_condoms()
    consumed_list = []
    # 下标从大到小移除，避免移除时下标错位
    for index in sorted(set(condom_index_list), reverse=True):
        if 0 <= index < len(used_condoms):
            consumed_list.append(used_condoms.pop(index))
    return consumed_list


def settle_hang(target_character_id: int, part_type: int, part_cid: int, condom_index_list: List[int]):
    """
    挂上避孕套装饰的结算（由选择面板在确认时直接调用）\n
    Keyword arguments:\n
    target_character_id -- 交互对象角色id\n
    part_type -- 部位类型，0=身体（仅头发0），1=服装部位\n
    part_cid -- 部位cid\n
    condom_index_list -- 存量池中要转移的避孕套下标列表\n
    Return arguments:\n
    无
    """
    move_to_decoration(target_character_id, part_type, part_cid, condom_index_list)
    # 标记当前行为的目标是身体部位还是服装部位，用于口上前提区分
    cache.character_data[0].sp_flag.condom_cloth_flag = 1 if part_type == 1 else 0


def settle_take_back(target_character_id: int, location_index_list: List[Tuple[tuple, int]]):
    """
    取回避孕套装饰的结算（由选择面板在确认时直接调用）\n
    Keyword arguments:\n
    target_character_id -- 交互对象角色id\n
    location_index_list -- 要取回的装饰列表，每个元素为((部位类型, 部位cid), 该部位列表中的下标)\n
    Return arguments:\n
    无
    """
    if not location_index_list:
        return
    # 标记当前行为的目标是身体部位还是服装部位（按第一个选中的装饰位置判定），用于口上前提区分
    first_location = location_index_list[0][0]
    cache.character_data[0].sp_flag.condom_cloth_flag = 1 if first_location[0] == 1 else 0
    take_back_decoration(target_character_id, location_index_list)


def settle_drink(target_character_id: int, condom_index_list: List[int]):
    """
    饮用避孕套精液的结算（由选择面板在确认时直接调用）\n
    消耗选中的避孕套，每套精液按10%残留口腔、90%进入胃部结算，并加精液/饮精经验与口喉快感\n
    Keyword arguments:\n
    target_character_id -- 交互对象角色id\n
    condom_index_list -- 存量池中要饮用的避孕套下标列表\n
    Return arguments:\n
    无
    """
    from Script.UI.Panel import ejaculation_panel
    from Script.Settle.common_default import base_chara_experience_common_settle, base_chara_state_common_settle
    target_data: game_type.Character = cache.character_data[target_character_id]
    # 消耗选中的避孕套
    consumed_list = consume_condoms(condom_index_list)
    if not consumed_list:
        return
    # 按饮下的总精液量增加口喉快感
    base_chara_state_common_settle(target_character_id, sum(consumed_list), 21, 0, tenths_add = False)
    # 每个避孕套里的精液按10%残留口腔、90%进入胃部结算
    temp_position = cache.shoot_position
    cache.shoot_position = 2
    for semen_count in consumed_list:
        mouth_count = max(int(semen_count * 0.1), 1) if semen_count > 0 else 0
        mouth_count = min(mouth_count, semen_count)
        stomach_count = semen_count - mouth_count
        if mouth_count:
            ejaculation_panel.update_semen_dirty(target_character_id, 2, 0, mouth_count, update_shoot_position_flag=False)
        if stomach_count:
            ejaculation_panel.update_semen_dirty(target_character_id, 15, 0, stomach_count, update_shoot_position_flag=False)
        # 每喝一个加一次精液经验和饮精经验
        base_chara_experience_common_settle(target_character_id, 24)
        base_chara_experience_common_settle(target_character_id, 25)
    cache.shoot_position = temp_position
    # 记录精液射入位置为胃部，以联动饮精绝顶二段行为
    target_data.h_state.shoot_position_body = 15


def settle_squeeze(target_character_id: int, part_type: int, part_cid: int, condom_index_list: List[int]):
    """
    挤出避孕套精液的结算（由选择面板在确认时直接调用）\n
    消耗选中的避孕套，将其中精液全额转移到交互对象指定部位（身体部位追加自然流动）\n
    Keyword arguments:\n
    target_character_id -- 交互对象角色id\n
    part_type -- 部位类型，0=身体，1=服装部位\n
    part_cid -- 部位cid\n
    condom_index_list -- 存量池中要挤出的避孕套下标列表\n
    Return arguments:\n
    无
    """
    from Script.UI.Panel import ejaculation_panel
    # 标记当前行为的目标是身体部位还是服装部位，用于口上前提区分
    cache.character_data[0].sp_flag.condom_cloth_flag = 1 if part_type == 1 else 0
    # 消耗选中的避孕套
    consumed_list = consume_condoms(condom_index_list)
    if not consumed_list:
        return
    all_semen_count = sum(consumed_list)
    # 全额转移到目标部位
    ejaculation_panel.update_semen_dirty(target_character_id, part_cid, part_type, all_semen_count, update_shoot_position_flag=False)
    # 身体部位追加自然流动结算
    if part_type == 0 and target_character_id != 0:
        ejaculation_panel.calculate_semen_flow(target_character_id, part_cid, part_type, all_semen_count)


def remove_cloth_decoration(character_id: int, part_cid_list: List[int] = None):
    """
    去除指定角色服装部位上的装饰避孕套记录（换衣/洗衣时调用），头发（身体部位）上的不受影响\n
    Keyword arguments:\n
    character_id -- 角色id\n
    part_cid_list -- 要去除的服装部位cid列表，None则去除全部服装部位\n
    Return arguments:\n
    无
    """
    decoration_dict = get_decoration_dict(character_id)
    for location_key in list(decoration_dict.keys()):
        part_type, part_cid = location_key
        if part_type != 1:
            continue
        if part_cid_list is None or part_cid in part_cid_list:
            del decoration_dict[location_key]
