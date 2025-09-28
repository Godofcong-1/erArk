import os
import pickle
import shutil
import datetime
from types import FunctionType
from Script.Core import (
    cache_control,
    constant,
    game_path_config,
    game_type,
    get_text,
    io_init,
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
    from Script.Design import basement, cooking
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

    # 递归地更新 loaded_dict
    update_count += update_dict_with_default(loaded_dict, new_cache.__dict__)
    # 更新角色预设
    update_count += update_tem_character(loaded_dict)

    # 更新绘制模式
    loaded_dict["web_mode"] = cache.web_mode
    # 重置防止递归调用的标志
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
        update_count += update_character_config_data(new_character_data)
        # 当前角色模板数据
        tem_character = loaded_dict["npc_tem_data"][new_character_data.cid - 1]
        # 更新角色服装
        cloth_update_count += update_chara_cloth(new_character_data, tem_character)
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


def update_tem_character(loaded_dict):
    """
    更新角色预设
    Keyword arguments:
    loaded_dict -- 存档数据
    """

    update_count = 0

    # 将cache.npc_tem_data转换为字典，以便快速查找
    cache_dict = {npc.AdvNpc: npc for npc in cache.npc_tem_data}

    # 更新loaded_dict["npc_tem_data"]，用新的角色预设属性代替旧的属性
    for i, now_npc_tem_data in enumerate(loaded_dict["npc_tem_data"]):
        # 修正深靛的序号错误
        if now_npc_tem_data.AdvNpc == 496 and 469 in cache_dict:
            loaded_dict["npc_tem_data"][i] = cache_dict[469]
            update_count += 1
            del cache_dict[469]
            continue
        if now_npc_tem_data.AdvNpc in cache_dict:
            # print(f"debug 准备更新{now_npc_tem_data.Name}的角色预设 ")
            loaded_dict["npc_tem_data"][i] = cache_dict[now_npc_tem_data.AdvNpc]
            # name = loaded_dict["npc_tem_data"][i].Name
            # print(f"debug 更新{name}的角色预设成功 ")
            # 从cache_dict中移除已经使用的元素
            del cache_dict[now_npc_tem_data.AdvNpc]

    # 将剩余的元素添加到loaded_dict["npc_tem_data"]的末尾
    # print(f"debug cache_dict = {cache_dict}")
    loaded_dict["npc_tem_data"].extend(cache_dict.values())
    update_count += len(cache_dict)

    # 更新新增角色
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
                tem_npc_data.Name = value.name
                tem_npc_data.AdvNpc = value.adv
                tem_npc_data.Mother_id = value.relationship.mother_id
                loaded_dict["npc_tem_data"].insert(value.cid - 1, tem_npc_data)
                i = 0
                break
            tem_character = loaded_dict["npc_tem_data"][tem_cid]
            # 循环的终止条件为找到干员编号相同的角色
            if value.adv == tem_character.AdvNpc:
                break
            i += 1
            # print(f"debug i = {i}")
        # 如果i不为0，说明序号不一致，需要修正
        if i != 0:
            # print(f"debug name = {value.name}, chara_cid = {value.cid}, new_tem_cid = {value.cid - 1}, old_tem_cid = {tem_cid}")
            tem_npc_data = loaded_dict["npc_tem_data"][tem_cid]
            # 修正深靛的序号错误
            if value.name == _("深靛") and value.adv != 469:
                value.adv = 469
                update_count += 1
                continue
            loaded_dict["npc_tem_data"].pop(tem_cid)
            loaded_dict["npc_tem_data"].insert(value.cid - 1, tem_npc_data)
            now_draw = draw.LeftDraw()
            draw_text = _("存档跨版本更新: 角色 {0} 的序号不一致，已修正\n").format(value.name)
            now_draw.text = draw_text
            # now_draw.draw()

    # 如果预设数量大于角色属性，则从尾部开始检查是否有空白预设，如果有则删除到与角色属性数量相同为止
    if len(loaded_dict["npc_tem_data"]) > len(loaded_dict["character_data"]):
        for i in range(len(loaded_dict["npc_tem_data"]) - len(loaded_dict["character_data"]) + 1):
            cid = len(loaded_dict["npc_tem_data"]) - i - 1
            if loaded_dict["npc_tem_data"][-1].Name == "":
                # print(f"debug 删除了空白预设，序号为{len(loaded_dict['npc_tem_data']) - 1}")
                loaded_dict["npc_tem_data"].pop()
                update_count += 1

    return update_count


def update_character_config_data(value):
    """
    更新角色属性数据
    Keyword arguments:
    value -- 角色数据
    """
    update_count = 0
    # 更新角色的各种属性
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
    # 可能存在旧的空编号，所以这里不检查长度
    # if len(value.ability) != len(game_config.config_ability):
    for key in game_config.config_ability:
        if key not in value.ability:
            value.ability[key] = 0
            update_count += 1
    # 状态
    for key in game_config.config_character_state:
        if key not in value.status_data:
            value.status_data[key] = 0
            update_count += 1
        # 该状态的性高潮记录
        if game_config.config_character_state[key].type == 0:
            value.h_state.orgasm_level.setdefault(key, 0)
            value.h_state.orgasm_count.setdefault(key, [0, 0])
            value.h_state.orgasm_edge_count.setdefault(key, 0)
            value.h_state.extra_orgasm_feel.setdefault(key, 0)
            value.h_state.time_stop_orgasm_count.setdefault(key, 0)
            update_count += 1
            # 对错误数据的修复
            if  value.h_state.orgasm_count[key] == 0:
                value.h_state.orgasm_count[key] = [0, 0]
    # 设置
    if len(value.chara_setting) != len(game_config.config_chara_setting):
        for key in game_config.config_chara_setting:
            if key not in value.chara_setting:
                value.chara_setting[key] = 0
                update_count += 1
    # 道具
    if len(value.item) != len(game_config.config_item):
        for key in game_config.config_item:
            if key not in value.item:
                value.item[key] = 0
                update_count += 1
    # 身体管理
    if len(value.body_manage) == 0:
        value.body_manage = attr_calculation.get_body_manage_zero()
        update_count += 1
    if len(value.body_manage) != len(game_config.config_body_manage_requirement):
        for key in game_config.config_body_manage_requirement:
            if key not in value.body_manage:
                value.body_manage[key] = 0
                update_count += 1
    # 助理服务
    if len(value.assistant_services) != len(game_config.config_assistant_services):
        for key in game_config.config_assistant_services:
            if key not in value.assistant_services:
                value.assistant_services[key] = 0
                update_count += 1
    # 身体道具
    if len(value.h_state.body_item) != len(game_config.config_h_item_index):
        # 如果body_item是列表而不是字典，则初始化为空字典
        if isinstance(value.h_state.body_item, list):
            value.h_state.body_item = {}
        for key in game_config.config_h_item_index:
            if key not in value.h_state.body_item:
                item_id = game_config.config_h_item_index[key]
                item_name = game_config.config_item[item_id].name
                value.h_state.body_item[key] = [item_name,False,None]
                update_count += 1
    # 行为
    # 如果行为id是int的话
    if isinstance(value.behavior.behavior_id, int):
        # 遍历Behavior，找到和当前行为id一致的行为键名
        for key in vars(constant.Behavior_Int).keys():
            # 跳过 Python 内置属性
            if key.startswith('__'):
                continue
            # 如果当前行为 ID 与常量值匹配，则更新为常量名称
            if value.behavior.behavior_id == getattr(constant.Behavior_Int, key):
                value.behavior.behavior_id = getattr(constant.Behavior, key)
                # update_count += 1
                # print(f"debug 更新了行为id: {key} -> {value.behavior.behavior_id}")
                break
    second_behavior_copy = value.second_behavior.copy()
    # 遍历原始的二级行为字典，处理整型键的更新或删除
    for second_behavior_id, behavior_data in second_behavior_copy.items():
        # 仅处理整型键
        if isinstance(second_behavior_id, int):
            # 查找匹配的常量名称
            for key in vars(constant.SecondBehavior_Int).keys():
                # 跳过 Python 内置属性
                if key.startswith('__'):
                    continue
                # 如果当前行为 ID 与常量值匹配，则更新为常量名称
                if second_behavior_id == getattr(constant.SecondBehavior_Int, key):
                    new_behavior_id = getattr(constant.SecondBehavior, key)
                    # 添加新的键值对，并删除旧的整型键
                    value.second_behavior[new_behavior_id] = behavior_data
                    del value.second_behavior[second_behavior_id]
                    # 匹配成功后跳出查找
                    break
            else:
                # 如果未找到匹配的常量，也删除该整型键
                del value.second_behavior[second_behavior_id]
    # 遍历二段行为数据库
    for behavior_id in game_config.config_behavior:
        if '二段结算' not in game_config.config_behavior[behavior_id].tag:
            continue
        # 如果二段行为不在角色的二段行为中，则添加
        if behavior_id not in value.second_behavior:
            value.second_behavior[behavior_id] = 0
            update_count += 1
            # print(f"debug 添加了二段行为: {behavior_id}")
    # 角色扮演的跨版本数据结构处理，如果是int类型，则将其转化为列表
    if isinstance(value.hypnosis.roleplay, int):
        value.hypnosis.roleplay = []
        update_count += 1
        # print(f"debug 更新了角色扮演数据: {value.roleplay}")

    return update_count


def update_chara_cloth(value, tem_character):
    """
    更新角色服装数据
    Keyword arguments:
    value -- 角色数据
    """
    from Script.Design import clothing

    # 数据长度不一致时，重置服装数据
    if len(value.cloth.cloth_wear) != len(game_config.config_clothing_type):
        value.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
    if len(value.cloth.cloth_locker_in_shower) != len(game_config.config_clothing_type):
        value.cloth.cloth_locker_in_shower = attr_calculation.get_shower_cloth_locker_zero()
    if len(value.cloth.cloth_locker_in_dormitory) != len(game_config.config_clothing_type):
        value.cloth.cloth_locker_in_dormitory = attr_calculation.get_cloth_locker_in_dormitory_zero()
    empty_dirty_data = attr_calculation.get_zero_dirty()
    if len(value.dirty.cloth_semen) != len(game_config.config_clothing_type):
        value.dirty.cloth_semen = empty_dirty_data.cloth_semen
    if len(value.dirty.cloth_locker_semen) != len(game_config.config_clothing_type):
        value.dirty.cloth_locker_semen = empty_dirty_data.cloth_locker_semen

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
                        # now_cloth_id >= 10001 and
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
        # 跳过深靛
        if now_npc_data.Name == _("深靛"):
            len_old_character -= 1
            continue
        new_character_cid = len_old_character + i
        # print(f"debug new_character_cid = {new_character_cid}")
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
        if value.scene_tag != loaded_dict["scene_data"][key].scene_tag:
            loaded_dict["scene_data"][key].scene_tag = value.scene_tag
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
