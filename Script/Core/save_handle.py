import os
import pickle
import shutil
import datetime
from types import FunctionType
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    get_text,
    io_init,
    old_chara_to_new
)
from Script.Config import normal_config, game_config, character_config
from Script.Design import attr_calculation, character_handle
from Script.UI.Moudle import draw
import json

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def get_save_dir_path(save_id: str) -> str:
    """
    按存档id获取存档所在系统路径
    Keyword arguments:
    save_id -- 存档id
    """
    save_path = os.path.join("save")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    return os.path.join(save_path, save_id)


def judge_save_file_exist(save_id: str) -> bool:
    """
    判断存档id对应的存档是否存在
    Keyword arguments:
    save_id -- 存档id
    """
    save_head_path = os.path.join(get_save_dir_path(save_id), "0")
    if not os.path.exists(save_head_path):
        return False
    save_path = os.path.join(get_save_dir_path(save_id), "1")
    if not os.path.exists(save_path):
        return False
    return True


def establish_save(save_id: str):
    """
    将游戏数据存入指定id的存档内
    Keyword arguments:
    save_id -- 存档id
    """
    establish_save_linux(save_id)
    return


def establish_save_linux(save_id: str):
    """
    针对linux的并行自动存档函数
    笔记:得益于unix的fork机制,子进程直接复制了一份内存,效率高,且不用创建传参管道,数据进程安全,不受玩家操作影响
    Keyword argumentsL
    save_id -- 当前存档id
    """
    # 如果是web模式且不是自动存档
    if cache.web_mode and save_id != "auto":
        # 清理Web模式图片缓存（避免缓存数据被序列化到存档中）
        try:
            from Script.System.Web_Draw_System.image_processor import clear_image_cache
            clear_image_cache()
        except ImportError:
            pass  # 如果模块不存在，忽略
    
    save_verson = {
        "game_verson": normal_config.config_normal.verson,
        "game_time": cache.game_time,
        "character_name": cache.character_data[0].name,
        "save_time": datetime.datetime.now(),
    }
    data = {
        "1": cache,
        "0": save_verson,
    }
    for key, value in data.items():
        write_save_data(save_id, key, value)


def load_save_info_head(save_id: str) -> dict:
    """
    获取存档的头部信息
    Keyword arguments:
    save_id -- 存档id
    """
    save_path = get_save_dir_path(save_id)
    file_path = os.path.join(save_path, "0")
    with open(file_path, "rb") as f:
        return pickle.load(f)


def write_save_data(save_id: str, data_id: str, write_data: dict):
    """
    将存档数据写入文件
    Keyword arguments:
    save_id -- 存档id
    data_id -- 要写入的数据在存档下的文件id
    write_data -- 要写入的数据
    """
    save_path = get_save_dir_path(save_id)
    file_path = os.path.join(save_path, data_id)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(file_path, "wb+") as f:
        pickle.dump(write_data, f)


def _normalize_save_path(path_text):
    """
    将存档中的路径文本转换为当前系统的路径格式
    Keyword arguments:
    path_text -- 可能包含其他系统路径分隔符的值
    Return arguments:
    str/object -- 字符串路径会被归一化，其他类型原样返回
    """
    foreign_sep = "\\" if os.sep == "/" else "/"
    if isinstance(path_text, str) and foreign_sep in path_text:
        return path_text.replace(foreign_sep, os.sep)
    return path_text


def _normalize_save_path_keys(path_dict):
    """
    归一化以场景或地图路径为键的存档字典
    Keyword arguments:
    path_dict -- 以路径文本为键的字典
    Return arguments:
    dict/object -- 有外来分隔符时返回归一化后的字典，否则原样返回
    """
    if not isinstance(path_dict, dict):
        return path_dict
    if not any(_normalize_save_path(key) != key for key in path_dict):
        return path_dict
    return {_normalize_save_path(key): value for key, value in path_dict.items()}


def _normalize_loaded_save_paths(loaded_cache: game_type.Cache) -> None:
    """
    归一化反序列化存档中已知的结构性路径字段
    Keyword arguments:
    loaded_cache -- 从存档反序列化得到的游戏缓存
    Return arguments:
    None
    """
    scene_data = getattr(loaded_cache, "scene_data", None)
    if isinstance(scene_data, dict):
        loaded_cache.scene_data = _normalize_save_path_keys(scene_data)
        for scene in loaded_cache.scene_data.values():
            if hasattr(scene, "scene_path"):
                scene.scene_path = _normalize_save_path(scene.scene_path)

    map_data = getattr(loaded_cache, "map_data", None)
    if isinstance(map_data, dict):
        loaded_cache.map_data = _normalize_save_path_keys(map_data)
        for map_data_value in loaded_cache.map_data.values():
            if hasattr(map_data_value, "map_path"):
                map_data_value.map_path = _normalize_save_path(map_data_value.map_path)

    character_data = getattr(loaded_cache, "character_data", None)
    if isinstance(character_data, dict):
        for character in character_data.values():
            if hasattr(character, "dormitory"):
                character.dormitory = _normalize_save_path(character.dormitory)
            if hasattr(character, "pre_dormitory"):
                character.pre_dormitory = _normalize_save_path(character.pre_dormitory)
            work_data = getattr(character, "work", None)
            if work_data is not None and hasattr(work_data, "dormitory_admin_target_room"):
                work_data.dormitory_admin_target_room = _normalize_save_path(work_data.dormitory_admin_target_room)
            ability_data = getattr(character, "pl_ability", None)
            if ability_data is not None and hasattr(ability_data, "air_hypnosis_position"):
                ability_data.air_hypnosis_position = _normalize_save_path(ability_data.air_hypnosis_position)

    rhodes_island = getattr(loaded_cache, "rhodes_island", None)
    if rhodes_island is not None:
        facility_damage_data = getattr(rhodes_island, "facility_damage_data", None)
        if isinstance(facility_damage_data, dict):
            rhodes_island.facility_damage_data = _normalize_save_path_keys(facility_damage_data)
        maintenance_place = getattr(rhodes_island, "maintenance_place", None)
        if isinstance(maintenance_place, dict):
            for character_id, place in maintenance_place.items():
                maintenance_place[character_id] = _normalize_save_path(place)


def load_save(save_id: str) -> game_type.Cache:
    """
    按存档id读取存档数据
    Keyword arguments:
    save_id -- 存档id
    Return arguments:
    game_type.Cache -- 游戏缓存数据
    """
    save_path = get_save_dir_path(save_id)
    file_path = os.path.join(save_path, "1")
    with open(file_path, "rb") as f:
        loaded_cache = pickle.load(f)
    _normalize_loaded_save_paths(loaded_cache)
    return loaded_cache

def input_load_save(save_id: str):
    """
    载入存档存档id对应数据，覆盖当前游戏内存
    Keyword arguments:
    save_id -- 存档id
    """
    from Script.Design import basement
    from Script.System.Cooking_System import cooking
    from Script.System.Medical_System import medical_service
    # 创建一个新的类实例，这个实例会包含所有的默认键值
    new_cache = game_type.Cache()
    new_cache.rhodes_island = basement.get_base_zero()
    update_count = 0


    # 从存档中加载字典
    loaded_dict = load_save(save_id).__dict__

    draw_text = _("\n开始检测存档的数据结构是否需要跨版本更新\n")
    now_draw = draw.LeftDraw()
    now_draw.text = draw_text
    now_draw.draw()

    # 检测是否为旧版存档（npc_tem_data是List而不是Dict）
    if isinstance(loaded_dict.get("npc_tem_data"), list):
        draw_text = _("\n检测到旧版存档，开始迁移角色ID系统...\n")
        now_draw = draw.LeftDraw()
        now_draw.text = draw_text
        now_draw.draw()
        
        migrate_count = old_chara_to_new.migrate_old_save_data(loaded_dict)
        
        draw_text = _("\n角色ID迁移完成，共处理{0}条数据\n").format(migrate_count)
        now_draw = draw.LeftDraw()
        now_draw.text = draw_text
        now_draw.draw()
        update_count += migrate_count

    # 递归地更新 loaded_dict
    update_count += update_dict_with_default(loaded_dict, new_cache.__dict__)
    # 更新角色预设
    update_count += old_chara_to_new.update_tem_character(loaded_dict)
    # 修正编号错误的角色数据
    update_count += old_chara_to_new.fix_wrong_character(loaded_dict)

    # ========== 角色替换迁移（新旧角色ID映射） ==========
    # 用于将旧角色的数据迁移到新角色，例如：1478号梅捷缇克缇 → 4056号缇缇
    character_replacement_map = {
        891: 4212,  # NPC娜斯提 → 干员娜斯提
        1040: 4052,  # 蒂拉 → 寻澜
        1478: 4056,  # 梅捷缇克缇 → 缇缇
    }
    # 检测是否需要进行角色替换迁移
    need_migration = False
    for old_id in character_replacement_map.keys():
        if old_id in loaded_dict["character_data"]:
            need_migration = True
            break
    
    if need_migration:
        draw_text = _("\n检测到需要进行角色替换迁移...\n")
        now_draw = draw.LeftDraw()
        now_draw.text = draw_text
        now_draw.draw()
        
        migration_count = old_chara_to_new.migrate_character_replacement(loaded_dict, character_replacement_map)
        
        if migration_count > 0:
            draw_text = _("\n角色替换迁移完成，共迁移{0}个角色\n").format(migration_count)
            now_draw = draw.LeftDraw()
            now_draw.text = draw_text
            now_draw.draw()
            update_count += migration_count

    # 更新绘制模式
    loaded_dict["web_mode"] = cache.web_mode
    # 重置游戏更新流程的嵌套深度
    loaded_dict["game_update_flow_running"] = 0

    # 遍历更新全角色属性
    cloth_update_count = 0
    color_update_count = 0
    for key, value in loaded_dict["character_data"].items():
        new_character_data = game_type.Character()
        recursive_update(new_character_data, value)
        # new_character_data.__dict__.update(value.__dict__)
        # print(f"debug name = {value.name}")
        # 角色素质、经验、宝珠、能力、设置的更新
        update_count += old_chara_to_new.update_character_config_data(new_character_data)
        # 当前角色模板数据（使用Dict方式访问，兼容新旧存档）
        tem_character = loaded_dict["npc_tem_data"].get(new_character_data.cid, None)
        if tem_character is None:
            # 如果找不到，尝试用adv
            tem_character = loaded_dict["npc_tem_data"].get(new_character_data.adv, None)
        if tem_character is None:
            # 处理找不到模板的情况（玩家跳过，NPC创建空白模板）
            if new_character_data.cid != 0:
                tem_character = character_handle.create_empty_character_tem()
                tem_character.Name = new_character_data.name
                tem_character.AdvNpc = new_character_data.adv
                loaded_dict["npc_tem_data"][new_character_data.cid] = tem_character
            else:
                # 玩家没有模板，跳过模板相关更新
                loaded_dict["character_data"][key] = new_character_data
                continue
        # 更新角色服装
        cloth_update_count += old_chara_to_new.update_chara_cloth(new_character_data, tem_character)
        # 更新角色口上颜色
        if new_character_data.cid != 0 and tem_character.TextColor != new_character_data.text_color:
            # print(f"debug value.name = {value.name}，tem_character.TextColor = {tem_character.TextColor}，value.text_color = {value.text_color}")
            new_character_data.text_color = tem_character.TextColor
            text_color_list = [new_character_data.adv, new_character_data.name, tem_character.TextColor]
            character_config.add_text_color_data_to_config_data(text_color_list)
            update_count += 1
            color_update_count += 1
        # 更新角色的口上大小
        if new_character_data.cid != 0 and tem_character.Talk_Size != new_character_data.talk_size:
            # print(f"debug value.name = {value.name}，tem_character.TextSize = {tem_character.TextSize}，value.text_size = {value.text_size}")
            new_character_data.talk_size = tem_character.Talk_Size
            update_count += 1
        # 更新角色势力与出身地
        if new_character_data.cid != 0 and tem_character.Nation != new_character_data.relationship.nation:
            new_character_data.relationship.nation = tem_character.Nation
            update_count += 1
        if new_character_data.cid != 0 and tem_character.Birthplace != new_character_data.relationship.birthplace:
            new_character_data.relationship.birthplace = tem_character.Birthplace
            update_count += 1
        # 更新到玩家收藏品列表
        if new_character_data.cid != 0 and new_character_data.cid not in loaded_dict["character_data"][0].pl_collection.token_list:
            loaded_dict["character_data"][0].pl_collection.token_list[new_character_data.cid] = False
            loaded_dict["character_data"][0].pl_collection.first_panties[new_character_data.cid] = ""
            loaded_dict["character_data"][0].pl_collection.npc_panties[new_character_data.cid] = []
            loaded_dict["character_data"][0].pl_collection.npc_socks[new_character_data.cid] = []
            # print(f"debug value.cid = {value.cid}, value.name = {value.name}")
            update_count += 1
        # 被监禁的角色检查是否在囚犯列表中，需要排除正在逃跑的人
        if new_character_data.sp_flag.imprisonment and not new_character_data.sp_flag.escaping and new_character_data.cid not in loaded_dict["rhodes_island"].current_prisoners:
            loaded_dict["rhodes_island"].current_prisoners[new_character_data.cid] = [cache.game_time, 0]
            update_count += 1
        # 重新指向新的角色数据
        loaded_dict["character_data"][key] = new_character_data
    if cloth_update_count:
        now_draw = draw.LeftDraw()
        draw_text = _("\n共有{0}个角色的服装数据已重置\n").format(cloth_update_count)
        now_draw.text = draw_text
        now_draw.draw()

    # 更新字体颜色
    if color_update_count:
        io_init.init_style()
        now_draw = draw.LeftDraw()
        draw_text = _("\n共有{0}个角色的口上颜色已更新\n").format(color_update_count)
        now_draw.text = draw_text
        now_draw.draw()

    # 更新罗德岛的资源
    for all_cid in game_config.config_resouce:
    # 不存在的资源数量设为0
        if all_cid not in loaded_dict["rhodes_island"].materials_resouce:
            loaded_dict["rhodes_island"].materials_resouce[all_cid] = 0
            update_count += 1
    # 更新罗德岛的设施等级
    for all_cid in game_config.config_facility:
        # 没有记录的设施改为初始等级0
        if all_cid not in loaded_dict["rhodes_island"].facility_level:
            loaded_dict["rhodes_island"].facility_level[all_cid] = 1
            update_count += 1
    # 更新罗德岛的设施开启状态
    for all_cid in game_config.config_facility_open:
        # 没有记录的设施改为初始关闭
        if all_cid not in loaded_dict["rhodes_island"].facility_open:
            loaded_dict["rhodes_island"].facility_open[all_cid] = False
        # 已关闭的查询是否可以被已有角色开启
        if loaded_dict["rhodes_island"].facility_open[all_cid] == False:
            if game_config.config_facility_open[all_cid].NPC_id != 0:
                for chara_cid in loaded_dict["npc_id_got"]:
                    character_data = loaded_dict["character_data"][chara_cid]
                    if character_data.adv == game_config.config_facility_open[all_cid].NPC_id:
                        loaded_dict["rhodes_island"].facility_open[all_cid] = True
                        break
    # 更新食谱
    loaded_dict["recipe_data"] = cooking.init_recipes()
    # 更新图书借阅
    for all_cid in game_config.config_book:
        if all_cid not in loaded_dict["rhodes_island"].book_borrow_dict:
            loaded_dict["rhodes_island"].book_borrow_dict[all_cid] = -1

    # 更新各项设置
    update_count += update_settings(loaded_dict)

    # 更新大地图势力数据
    loaded_dict["country"] = attr_calculation.get_country_reset(loaded_dict["country"])

    # 更新游戏地图
    update_count += update_map(loaded_dict)

    # 更新医疗系统存档结构
    medical_service.update_medical_save_data_structure(loaded_dict)

    # 最后输出
    now_draw = draw.NormalDraw()
    draw_text = _("\n检测完毕，共有{0}条数据完成了更新\n").format(update_count)
    now_draw.text = draw_text
    now_draw.draw()

    # 使用 update() 方法来更新 cache 的字典
    cache.__dict__.update(loaded_dict)


def update_dict_with_default(loaded_dict, default_dict):
    """
    递归地赋值字典
    Keyword arguments:
    loaded_dict -- 要赋值的字典
    default_dict -- 默认字典
    """
    update_count = 0
    for key, value in default_dict.items():
        # print("存档修复: key", key, "value", value)
        # 跳过Python的内置方法
        if key.startswith('__') and key.endswith('__'):
            continue
        # 如果 key 不在 loaded_dict 中，将其添加到 loaded_dict 中
        if key not in loaded_dict:
            loaded_dict[key] = value
            update_count += 1
            # 只有在不是私有属性时才会输出
            draw_text = _("存档跨版本更新: key {0}, not found，已设为默认值 {1}\n").format(key, value)
            now_draw = draw.LeftDraw()
            now_draw.text = draw_text
            # now_draw.draw()
        elif isinstance(value, game_type.Cache):
            update_count += update_dict_with_default(loaded_dict[key].__dict__, value.__dict__)
        elif hasattr(value, '__dict__'):  # 检查 value 是否是一个类的实例
            update_count += update_dict_with_default(loaded_dict[key].__dict__, value.__dict__)
        # 如果key的类型不同，且value不为None，类型也不为int或float时，将其设为默认值
        elif type(loaded_dict[key]) != type(default_dict[key]) and value != None and type(value) != int and type(value) != float:
            loaded_dict[key] = value
            update_count += 1
            draw_text = _("存档跨版本更新: key {0}, type not match，原type {1}，新type {2}, 已设为默认值 {3}\n").format(key, type(loaded_dict[key]), type(default_dict[key]), value)
            now_draw = draw.LeftDraw()
            now_draw.text = draw_text
            # now_draw.draw()
    return update_count

def recursive_update(target, source):
    """
    递归更新字典
    Keyword arguments:
    target -- 要被更新的目标字典
    source -- 数据来源的源字典
    """
    for key, value in source.__dict__.items():
        if isinstance(value, object) and hasattr(value, '__dict__'):
            if key in target.__dict__ and isinstance(target.__dict__[key], object) and hasattr(target.__dict__[key], '__dict__'):
                recursive_update(target.__dict__[key], value)
            else:
                target.__dict__[key] = value
        else:
            target.__dict__[key] = value


def update_map(loaded_dict):
    """
    更新地图
    Keyword arguments:
    loaded_dict -- 存档数据
    """

    update_count = 0

    # 遍历地图数据，如果该地图在缓存数据中但不在存档中，将其添加到存档中
    change_map_flag = False
    for key, value in cache.scene_data.items():
        if key not in loaded_dict["scene_data"]:
            loaded_dict["scene_data"][key] = value
            update_count += 1
            change_map_flag = True
        if value.scene_tag != loaded_dict["scene_data"][key].scene_tag:
            loaded_dict["scene_data"][key].scene_tag = value.scene_tag
            update_count += 1
            change_map_flag = True
        if not hasattr(loaded_dict["scene_data"][key], 'scene_img') or value.scene_img != loaded_dict["scene_data"][key].scene_img:
            loaded_dict["scene_data"][key].scene_img = value.scene_img
            update_count += 1
            change_map_flag = True
        if not hasattr(loaded_dict["scene_data"][key], 'room_area') or value.room_area != loaded_dict["scene_data"][key].room_area:
            loaded_dict["scene_data"][key].room_area = value.room_area
            update_count += 1
            change_map_flag = True
    # 如果地图数据有变化，将地图路径也更新，同时删除不存在的地图数据
    if change_map_flag:
        loaded_dict["map_data"] = cache.map_data
        # 在2024.7月的版本中将人气快餐开封菜改为了约翰老妈汉堡店
        if '贸易\人气快餐开封菜' in loaded_dict["scene_data"]:
            # print("发现存档存在人气快餐开封菜")
            for key, value in loaded_dict["character_data"].items():
                if value.position[-1] == '人气快餐开封菜':
                    value.position[-1] = '约翰老妈汉堡店'
                    # print(f"已将{value.name}的位置从人气开封菜改为约翰老妈汉堡店")
        for key, value in loaded_dict["scene_data"].copy().items():
            # print(f"debug 地图数据: key = {key}, value = {value.scene_tag}")
            if key not in cache.scene_data:
                del loaded_dict["scene_data"][key]
                update_count += 1
        now_draw = draw.LeftDraw()
        draw_text = _("\n游戏地图已更新\n")
        now_draw.text = draw_text
        now_draw.draw()

    return update_count

def update_settings(loaded_dict):
    """
    更新设置
    Keyword arguments:
    loaded_dict -- 存档数据
    """
    update_count = 0
    zero_system_setting = attr_calculation.get_system_setting_zero()
    base_setting = zero_system_setting.base_setting
    if len(loaded_dict["all_system_setting"].base_setting) != len(base_setting):
        for key in base_setting:
            if key not in loaded_dict["all_system_setting"].base_setting:
                loaded_dict["all_system_setting"].base_setting[key] = base_setting[key]
                update_count += 1
        now_draw = draw.NormalDraw()
        draw_text = _("\n系统设置已更新，如有需要请手动修改\n")
        now_draw.style = "gold_enrod"
        now_draw.text = draw_text
        now_draw.draw()
    draw_setting = zero_system_setting.draw_setting
    if len(loaded_dict["all_system_setting"].draw_setting) != len(draw_setting):
        for key in draw_setting:
            if key not in loaded_dict["all_system_setting"].draw_setting:
                loaded_dict["all_system_setting"].draw_setting[key] = draw_setting[key]
                update_count += 1
        now_draw = draw.NormalDraw()
        draw_text = _("\n绘制设置已更新，如有需要请手动修改\n")
        now_draw.style = "gold_enrod"
        now_draw.text = draw_text
        now_draw.draw()
    difficulty_setting = zero_system_setting.difficulty_setting
    if len(loaded_dict["all_system_setting"].difficulty_setting) != len(difficulty_setting):
        for key in difficulty_setting:
            if key not in loaded_dict["all_system_setting"].difficulty_setting:
                loaded_dict["all_system_setting"].difficulty_setting[key] = difficulty_setting[key]
                update_count += 1
        now_difficulty = draw.NormalDraw()
        draw_text = _("\n难度设置已更新，如有需要请手动修改\n")
        now_difficulty.style = "gold_enrod"
        now_difficulty.text = draw_text
        now_difficulty.draw()
    # 角色口上选择设置
    character_text_version = zero_system_setting.character_text_version
    # 获取玩家的女儿角色列表
    daughter_characters = loaded_dict["character_data"][0].relationship.child_id_list
    for daughter_cid in daughter_characters:
        if daughter_cid not in character_text_version:
            character_text_version[daughter_cid] = 1
    if len(loaded_dict["all_system_setting"].character_text_version) != len(character_text_version):
        for key in character_text_version:
            if key not in loaded_dict["all_system_setting"].character_text_version:
                loaded_dict["all_system_setting"].character_text_version[key] = character_text_version[key]
                update_count += 1
        now_draw = draw.NormalDraw()
        draw_text = _("\n角色口上选择设置已更新，如有需要请手动修改\n")
        now_draw.style = "gold_enrod"
        now_draw.text = draw_text
        now_draw.draw()
    # 更新AI设置
    if len(loaded_dict["ai_setting"].ai_chat_setting) != len(game_config.config_ai_chat_setting):
        for key in game_config.config_ai_chat_setting:
            if key not in loaded_dict["ai_setting"].ai_chat_setting:
                loaded_dict["ai_setting"].ai_chat_setting[key] = 0
                update_count += 1
        now_draw = draw.NormalDraw()
        draw_text = _("\n文本生成AI设置已更新，如有需要请手动修改\n")
        now_draw.style = "gold_enrod"
        now_draw.text = draw_text
        now_draw.draw()
    # 更新体检设置
    zero_physical_exam_setting = attr_calculation.get_physical_exam_setting_zero()
    if len(loaded_dict["rhodes_island"].physical_examination_setting) != len(zero_physical_exam_setting):
        for key in zero_physical_exam_setting:
            if key not in loaded_dict["rhodes_island"].physical_examination_setting:
                loaded_dict["rhodes_island"].physical_examination_setting[key] = zero_physical_exam_setting[key]
                update_count += 1
        now_draw = draw.NormalDraw()
        draw_text = _("\n体检设置已更新，如有需要请手动修改\n")
        now_draw.style = "gold_enrod"
        now_draw.text = draw_text
        now_draw.draw()
    # 更新监禁调教设置
    if len(loaded_dict["rhodes_island"].confinement_training_setting) != len(game_config.config_confinement_training_setting):
        for key in game_config.config_confinement_training_setting:
            if key not in loaded_dict["rhodes_island"].confinement_training_setting:
                loaded_dict["rhodes_island"].confinement_training_setting[key] = 0
                update_count += 1
        now_draw = draw.NormalDraw()
        draw_text = _("\n监禁调教设置已更新，如有需要请手动修改\n")
        now_draw.style = "gold_enrod"
        now_draw.text = draw_text
        now_draw.draw()
    return update_count


def remove_save(save_id: str):
    """
    删除存档id对应存档
    Keyword arguments:
    save_id -- 存档id
    """
    save_path = get_save_dir_path(save_id)
    if os.path.isdir(save_path):
        shutil.rmtree(save_path)


def _get_save_info_path() -> str:
    """
    获取 save_info.json 的路径（用于记录界面相关的简单配置）
    """
    save_dir = os.path.join("save")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return os.path.join(save_dir, "save_info.json")

def load_save_info_file() -> dict:
    """
    读取 save/save_info.json 并返回字典，文件不存在时返回空字典
    """
    path = _get_save_info_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_save_info_file(data: dict) -> None:
    """
    将 data 字典写入 save/save_info.json（覆盖写）
    """
    path = _get_save_info_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # 忽略写入错误，避免影响保存流程
        pass

def get_last_save_page() -> int:
    """方便的包装，返回保存的 last_save_page，默认 0"""
    info = load_save_info_file()
    try:
        return int(info.get("last_save_page", 0))
    except Exception:
        return 0

def set_last_save_page(page: int) -> None:
    """方便的包装，写入 last_save_page 到 save_info.json"""
    info = load_save_info_file()
    info["last_save_page"] = int(page)
    save_save_info_file(info)

def get_last_save_id() -> str:
    """返回上次保存的存档 id，默认空字符串"""
    info = load_save_info_file()
    try:
        v = info.get("last_save_id", "")
        return str(v) if v is not None else ""
    except Exception:
        return ""

def set_last_save_id(save_id: str) -> None:
    """写入上次保存的存档 id 到 save_info.json"""
    info = load_save_info_file()
    info["last_save_id"] = str(save_id)
    save_save_info_file(info)
