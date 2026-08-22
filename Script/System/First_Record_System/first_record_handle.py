from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.Design import map_handle
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

SECOND_BEHAVIOR_TO_SPECIAL_CID = {
    "fertilization": 1,
    "b_orgasm_to_milk": 3,
    "u_orgasm_to_pee": 4,
}
""" 固定二段行为id到特殊履历配表cid的白名单映射（FirstRecordSpecial.csv） """

EXHIBITIONISM_MODE_NAME_DICT = {
    1: _("无人室内露出"),
    2: _("无人室外露出"),
    3: _("人前露出"),
    4: _("无意识人前露出"),
}
""" 露出H模式编号到模式名的映射（同sp_flag.exhibitionism_sex_mode） """

HIDDEN_SEX_MODE_NAME_DICT = {
    1: _("双方都不隐蔽"),
    2: _("仅女方隐蔽"),
    3: _("仅男方隐蔽"),
    4: _("双方都隐蔽"),
}
""" 隐奸H模式编号到模式名的映射（同sp_flag.hidden_sex_mode） """


def get_part_sex_record(first_record, part_id: int):
    """
    读取部位交/破处初体验记录（带旧快照缺字段防御）\n
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    part_id -- 身体部位编号（同h_state.insert_position 0~15）\n
    Return arguments:
    dict|None -- 该部位的记录dict，无记录时为None
    """
    return getattr(first_record, "first_part_sex_dict", {}).get(part_id, None)


def record_first_special_record(character_id: int, special_cid: int, special_data: str = ""):
    """
    记录特殊履历（FirstRecordSpecial.csv配表驱动，已记录则跳过）\n
    Keyword arguments:
    character_id -- 角色id\n
    special_cid -- FirstRecordSpecial.csv中的配表id\n
    special_data -- 该履历要附记的特殊数据文本
    """
    if special_cid not in game_config.config_first_record_special:
        return
    character_data = cache.character_data[character_id]
    if special_cid in character_data.first_record.first_special_record_dict:
        return
    character_data.first_record.first_special_record_dict[special_cid] = [
        cache.game_time, list(character_data.position), special_data]


def get_semen_source_text(character_id: int) -> str:
    """
    获取饮精类事件的精液来源描述\n
    Keyword arguments:
    character_id -- 饮精角色id\n
    Return arguments:
    str -- H中的精液记当时的H模式；精液食物记食物名称；两者都不是时记"非H"
    """
    # H模式判定统一调用Sex_System的通用函数（函数内延迟导入，断开 handle_talent→本模块→handle_premise→instuct_judege→handle_talent 的启动期导入环）
    from Script.System.Sex_System import h_mode_common
    # H中的精液：记当时的H模式
    h_mode_text = h_mode_common.get_current_h_mode_text(character_id)
    if h_mode_text != _("非H"):
        return h_mode_text
    # 非H时从进食上下文取精液食物名（玩家喂食时食物挂在玩家的行为上，二段结算与进食结算同帧、target_food未被重置）
    for now_chara_id in (character_id, 0):
        now_food = cache.character_data[now_chara_id].behavior.target_food
        if now_food is not None and getattr(now_food, "special_seasoning", 0) in (11, 12):
            if now_food.name:
                return now_food.name
            if now_food.recipe in game_config.config_recipes:
                return game_config.config_recipes[now_food.recipe].name
    return _("非H")


def get_special_data_for_second_behavior(character_id: int, second_behavior_id: str) -> str:
    """
    获取二段行为白名单类特殊履历的附记数据\n
    Keyword arguments:
    character_id -- 角色id\n
    second_behavior_id -- 二段行为id\n
    Return arguments:
    str -- 附记数据文本，无则为空串
    """
    character_data = cache.character_data[character_id]
    # 受精：附记是否为无意识受精（此时pregnancy.py的talent[35]判定已完成）
    if second_behavior_id == "fertilization" and character_data.talent[35]:
        return _("无意识受精")
    # 喷乳绝顶/放尿绝顶：附记当时的H模式（调用Sex_System通用函数，延迟导入理由见get_semen_source_text）
    if second_behavior_id in ("b_orgasm_to_milk", "u_orgasm_to_pee"):
        from Script.System.Sex_System import h_mode_common
        return h_mode_common.get_current_h_mode_text(character_id)
    return ""


def record_first_h_mode(character_id: int, mode_key: str, extra_data: str = ""):
    """
    H模式初体验通用写入（未记录才写）\n
    Keyword arguments:
    character_id -- 角色id\n
    mode_key -- 模式键（unconscious_1~7/group_sex/exhibitionism/hidden_sex/pretend_sleep）\n
    extra_data -- 附加数据文本
    """
    character_data = cache.character_data[character_id]
    if mode_key not in character_data.first_record.first_h_mode_dict:
        character_data.first_record.first_h_mode_dict[mode_key] = [
            cache.game_time, list(character_data.position), extra_data]


def check_first_h_mode(character_id: int):
    """
    H模式初体验的中心判定（由行为结算必经处调用，dict去重使重复判定零成本）\n
    Keyword arguments:
    character_id -- 角色id（玩家不记录，直接返回）
    """
    # 玩家不进履历面板，不做记录
    if not character_id:
        return
    character_data = cache.character_data[character_id]
    # 需要处于H模式中
    if not character_data.sp_flag.is_h:
        return
    # 无意识H按类型拆分为独立键（1睡眠~7心控），一名角色可积累至多7条
    if character_data.sp_flag.unconscious_h:
        record_first_h_mode(character_id, f"unconscious_{character_data.sp_flag.unconscious_h}")
    # 群交（附加数据：当时场景内角色数）
    if cache.group_sex_mode:
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        scene_character_count = 0
        if scene_path_str in cache.scene_data:
            scene_character_count = len(cache.scene_data[scene_path_str].character_list)
        record_first_h_mode(character_id, "group_sex", str(scene_character_count))
    # 露出H（附加数据：模式名）
    if character_data.sp_flag.exhibitionism_sex_mode:
        mode_name = EXHIBITIONISM_MODE_NAME_DICT.get(character_data.sp_flag.exhibitionism_sex_mode, "")
        record_first_h_mode(character_id, "exhibitionism", mode_name)
    # 隐奸H（附加数据：模式名）
    if character_data.sp_flag.hidden_sex_mode:
        mode_name = HIDDEN_SEX_MODE_NAME_DICT.get(character_data.sp_flag.hidden_sex_mode, "")
        record_first_h_mode(character_id, "hidden_sex", mode_name)
    # 装睡H
    if character_data.h_state.pretend_sleep:
        record_first_h_mode(character_id, "pretend_sleep")
