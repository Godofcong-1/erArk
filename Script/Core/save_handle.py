import os
import sys
import pickle
import shutil
import datetime
import platform
import multiprocessing
from types import FunctionType
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    get_text,
)
from Script.Config import normal_config, game_config
from Script.Design import attr_calculation, clothing, character_handle, basement
from Script.UI.Moudle import draw

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
        return 0
    save_path = os.path.join(get_save_dir_path(save_id), "1")
    if not os.path.exists(save_path):
        return 0
    return 1


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


def load_save(save_id: str) -> dict:
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
        return pickle.load(f)


def input_load_save(save_id: str):
    """
    载入存档存档id对应数据，覆盖当前游戏内存
    Keyword arguments:
    save_id -- 存档id
    """
    # 创建一个新的类实例，这个实例会包含所有的默认键值
    new_cache = game_type.Cache()
    new_cache.rhodes_island = basement.get_base_zero()
    character_data_type = game_type.Character()
    update_count = 0

    # 从存档中加载字典
    loaded_dict = load_save(save_id).__dict__

    draw_text = _(f"\n开始检测存档的数据结构是否需要跨版本更新\n")
    now_draw = draw.LeftDraw()
    now_draw.text = draw_text
    now_draw.draw()

    # 递归地更新 loaded_dict
    update_count += update_dict_with_default(loaded_dict, new_cache.__dict__)
    # 更新角色预设
    update_count += update_tem_character(loaded_dict)

    # 遍历更新全角色属性
    cloth_update_count = 0
    for key, value in loaded_dict["character_data"].items():
        # print(f"debug name = {value.name}")
        update_count += update_dict_with_default(value.__dict__, character_data_type.__dict__)
        # 角色素质、经验、宝珠、能力的更新
        update_count += update_character_config_data(value)
        tem_character = loaded_dict["npc_tem_data"][value.cid - 1]
        # 角色服装数据的更新
        cloth_update_count += update_chara_cloth(value, tem_character)
    if cloth_update_count:
        draw_text = _(f"\n共有{cloth_update_count}个角色的服装数据已重置\n")
        now_draw.text = draw_text
        now_draw.draw()

    # 更新罗德岛的资源
    for all_cid in game_config.config_resouce:
    # 不存在的资源数量设为0
        if all_cid not in loaded_dict["rhodes_island"].materials_resouce:
            loaded_dict["rhodes_island"].materials_resouce[all_cid] = 0
            update_count += 1

    # 重置系统设置
    if not len(loaded_dict["system_setting"]):
        loaded_dict["system_setting"] = attr_calculation.get_system_setting_zero()
        draw_text = _(f"\n系统设置已重置，如有需要请手动修改\n")
        now_draw.text = draw_text
        now_draw.draw()

    # 更新游戏地图
    update_count += update_map(loaded_dict)

    now_draw = draw.LeftDraw()
    draw_text = _(f"\n检测完毕，共有{update_count}条数据完成了更新\n")
    now_draw.text = draw_text
    now_draw.draw()

    # 使用 update() 方法来更新 cache 的字典
    cache.__dict__.update(loaded_dict)


def update_dict_with_default(loaded_dict, default_dict):
    """
    递归地更新字典
    Keyword arguments:
    loaded_dict -- 要更新的字典
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
            draw_text = _(f"存档跨版本更新: key {key}, not found，已设为默认值 {value}\n")
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
            draw_text = _(f"存档跨版本更新: key {key}, type not match，原type {type(loaded_dict[key])}，新type {type(default_dict[key])}, 已设为默认值 {value}\n")
            now_draw = draw.LeftDraw()
            now_draw.text = draw_text
            # now_draw.draw()
    return update_count


def update_tem_character(loaded_dict):
    """
    更新角色预设
    Keyword arguments:
    loaded_dict -- 存档数据
    """

    update_count = 0
    # 用新的角色预设属性代替旧的属性
    all_new_tem_data = cache.npc_tem_data.copy()
    for i in range(len(loaded_dict["npc_tem_data"])):
        now_npc_tem_data = loaded_dict["npc_tem_data"][i]
        for j in range(len(cache.npc_tem_data)):
            if cache.npc_tem_data[j].Name == now_npc_tem_data.Name:
                loaded_dict["npc_tem_data"][i] = cache.npc_tem_data[j]
                all_new_tem_data.remove(cache.npc_tem_data[j])
                # print(f"debug 更新了{now_npc_tem_data.Name}的角色预设 ")
                break
    # 没有被替代的加在后面
    for now_npc_tem_data in all_new_tem_data:
        loaded_dict["npc_tem_data"].append(now_npc_tem_data)
        # print(f"debug 新增了{now_npc_tem_data.Name}的角色预设 ")
    # 更新新角色
    update_count += update_new_character(loaded_dict)
    # 修正loaded_dict["npc_tem_data"]的元素的序号，如果与实际的序号不一致，将其修正
    for key, value in loaded_dict["character_data"].items():
        i = -10
        # 跳过玩家
        if value.cid == 0:
            continue
        while 1:
            tem_cid = value.cid - 1 + i
            # 如果超出了角色预设的数量，则赋予空白模板，然后跳出循环
            if tem_cid >= len(loaded_dict["npc_tem_data"]):
                tem_npc_data = character_handle.create_empty_character_tem()
                loaded_dict["npc_tem_data"].insert(value.cid - 1, tem_npc_data)
                i = 0
                break
            tem_character = loaded_dict["npc_tem_data"][tem_cid]
            # 循环的终止条件为找到名字相同的角色
            if value.name == tem_character.Name:
                break
            i += 1
            # print(f"debug i = {i}")
        # 如果i不为0，说明序号不一致，需要修正
        if i != 0:
            # print(f"debug new_tem_cid = {value.cid - 1}, old_tem_cid = {tem_cid}")
            tem_npc_data = loaded_dict["npc_tem_data"][tem_cid]
            loaded_dict["npc_tem_data"].pop(tem_cid)
            loaded_dict["npc_tem_data"].insert(value.cid - 1, tem_npc_data)
            now_draw = draw.LeftDraw()
            draw_text = _(f"存档跨版本更新: 角色 {value.name} 的序号不一致，已修正\n")
            now_draw.text = draw_text
            # now_draw.draw()
    return update_count


def update_character_config_data(value):
    """
    更新角色属性数据
    Keyword arguments:
    value -- 角色数据
    """
    update_count = 0
    # 更新角色素质、经验、宝珠、能力
    # 素质
    if len(value.talent) != len(game_config.config_talent):
        for key in game_config.config_talent:
            if key not in value.talent:
                value.talent[key] = 0
                update_count += 1
                # print(f"debug key = {key}")
    # 经验
    if len(value.experience) != len(game_config.config_experience):
        for key in game_config.config_experience:
            if key not in value.experience:
                value.experience[key] = 0
                update_count += 1
    # 宝珠
    if len(value.juel) != len(game_config.config_juel):
        for key in game_config.config_juel:
            if key not in value.juel:
                value.juel[key] = 0
                update_count += 1
    # 能力
    if len(value.ability) != len(game_config.config_ability):
        for key in game_config.config_ability:
            if key not in value.ability:
                value.ability[key] = 0
                update_count += 1
    return update_count


def update_chara_cloth(value, tem_character):
    """
    更新角色服装数据
    Keyword arguments:
    value -- 角色数据
    """
    # 跳过玩家
    if value.cid == 0:
        return 0
    # print(f"debug value.cid = {value.cid}")
    tem_character = tem_character

    # 判断是否需要重置服装数据
    reset_cloth_flag = False
    if len(value.cloth.cloth_wear):
        for now_type in value.cloth.cloth_wear:
            now_type_cloth_data = value.cloth.cloth_wear[now_type]
            for now_cloth_id in now_type_cloth_data:
                    # 查找该编号的服装数据是否存在，如果不存在，则重置该角色的服装数据
                    if (
                        now_cloth_id >= 10001 and
                        now_cloth_id not in game_config.config_clothing_tem
                    ):
                        reset_cloth_flag = True
                        break
            if reset_cloth_flag:
                break
    # 进行服装数据的重置
    # print(f"debug old value.cloth.cloth_wear = {value.cloth.cloth_wear}")
    if reset_cloth_flag:
        value.cloth = attr_calculation.get_cloth_zero()
        value.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
        for cloth_id in tem_character.Cloth:
            if cloth_id not in game_config.config_clothing_tem:
                continue
            type = game_config.config_clothing_tem[cloth_id].clothing_type
            value.cloth.cloth_wear[type].append(cloth_id)
        bra_id, pan_id = clothing.get_random_underwear()
        if not len(value.cloth.cloth_wear[6]):
            value.cloth.cloth_wear[6].append(bra_id)
        if not len(value.cloth.cloth_wear[9]):
            value.cloth.cloth_wear[9].append(pan_id)
        # print(f"debug new value.cloth.cloth_wear = {value.cloth.cloth_wear}")
        return 1
    return 0


def update_new_character(loaded_dict):
    """
    更新新角色
    Keyword arguments:
    loaded_dict -- 存档数据
    """
    update_count = 0
    # 遍历角色预设，如果该角色在预设中但不在角色属性中，将其添加到需要增加的角色属性中
    add_new_character_list = [now_npc_data for now_npc_data in loaded_dict["npc_tem_data"] 
                              if not any(char_data.adv == now_npc_data.AdvNpc for char_data in loaded_dict["character_data"].values())]

    # 新增该角色
    len_old_character = len(loaded_dict["character_data"])
    for i, now_npc_data in enumerate(add_new_character_list):
        new_character_cid = len_old_character + i
        new_character = character_handle.init_character(new_character_cid, now_npc_data)
        loaded_dict["character_data"][new_character_cid] = new_character
        update_count += 1

    return update_count


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
    # 如果地图数据有变化，将地图路径也更新，同时删除不存在的地图数据
    if change_map_flag:
        loaded_dict["map_data"] = cache.map_data
        for key, value in loaded_dict["scene_data"].copy().items():
            if key not in cache.scene_data:
                del loaded_dict["scene_data"][key]
                update_count += 1
        now_draw = draw.LeftDraw()
        draw_text = _(f"\n游戏地图已更新\n")
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
