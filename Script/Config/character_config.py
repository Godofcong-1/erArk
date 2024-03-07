import os, glob
from typing import List
from Script.Core import json_handle,game_type,get_text
from Script.Config import game_config, config_def

character_config_file = os.path.join("data","Character.json")
""" 角色模板配置文件路径 """
character_config_data = {}
""" 原始角色模板数据 """
character_tem_list:List[game_type.NpcTem] = []
""" 角色模板数据列表 """
init_character_cloth_count = 10000
""" 角色服装数据起始编号 """

def init_character_tem_data():
    """ 初始化预设角色数据 """
    global character_config_data
    character_config_data = json_handle.load_json(character_config_file)
    directory = 'data/talk/chara'
    for character_name in character_config_data:
        now_tem = game_type.NpcTem()
        now_data = character_config_data[character_name]
        for k in now_data:
            # print("k :",k)
            v = get_text._(now_data[k])
            # print("v :",v)
            if k.startswith("A|"):
                now_k = int(k.lstrip("A|"))
                # print("now_k :",now_k)
                now_tem.Ability[now_k] = v
            elif k.startswith("E|"):
                now_k = int(k.lstrip("E|"))
                # print("now_k :",now_k)
                now_tem.Experience[now_k] = v
            elif k.startswith("T|"):
                now_k = int(k.lstrip("T|"))
                now_tem.Talent[now_k] = 1
            # 旧的服装数据读取，读取的是编号，然后在服装csv中查找对应的服装数据
            # elif k.startswith("C|"):
            #     now_k = int(k.lstrip("C|"))
            #     now_tem.Cloth.append(now_k)
            # 新的服装数据读取，读取的是str，直接获得服装数据，然后写入服装模板数据
            elif k.startswith("C|"):
                now_k = int(k.lstrip("C|"))
                # 针对默认服装
                if now_k in [5999, 8999]:
                    now_cloth_cid = now_k
                else:
                    cloth_list = [v, now_k]
                    now_cloth_cid = add_cloth_data_to_config_data(cloth_list)
                # print(f"debug : k={k}, now_k ={now_k}, v={v}, now_cloth_cid = {now_cloth_cid}")
                now_tem.Cloth.append(now_cloth_cid)
            elif k == "TextColor":
                chara_id = now_data["AdvNpc"]
                chara_name = now_data["Name"]
                text_color_list = [chara_id, chara_name, v]
                add_text_color_data_to_config_data(text_color_list)
                now_tem.__dict__[k] = v
            else:
                now_tem.__dict__[k] = v
        # 截取_之后的文本
        find_name = character_name.split("_")[1]
        talk_sizes = find_files_and_get_size(directory, find_name)
        # 如果存在对话文件，将对话文件大小赋值给角色模板
        if len(talk_sizes):
            # 仅需要值，不需要键，除以1024是为了将文件大小转换为kb，进1保留到个位
            now_tem.Talk_Size = int((sum(talk_sizes.values()) / 1024) + 1)
        character_tem_list.append(now_tem)

def find_files_and_get_size(directory, character):
    # 构造文件路径
    path = os.path.join(directory, '*')
    # 查找文件名包含特定字符的文件
    files = glob.glob(path)
    target_files = [file for file in files if character in os.path.basename(file)]
    # 获取文件大小
    file_sizes = {file: os.path.getsize(file) for file in target_files}
    return file_sizes

def add_cloth_data_to_config_data(cloth_list: List[int]):
    """ 将服装数据加入服装模板数据 """
    global init_character_cloth_count
    # print(f"debug cloth_list = {cloth_list}")
    # 新增服装数据到config_clothing_tem
    name, type = cloth_list[0], cloth_list[1]
    # tag的修正
    if "必带" in name:
        tag = 6
        name = name.split(" ",1)[0]
    else:
        tag = 0
    # 裤子和裙子的tag修正
    if type == 8:
        if "裤" in name:
            tag = 4
        else:
            tag = 5
    cloth_data = {'cid':init_character_cloth_count, 'name':name, 'clothing_type':type, 'npc':0, 'tag':tag, 'describe':name + '的服装'}
    # print(f"debug cloth_data = {cloth_data}")
    now_cloth = config_def.ClothingTem()
    now_cloth.__dict__ = cloth_data
    game_config.config_clothing_tem[now_cloth.cid] = now_cloth
    init_character_cloth_count += 1
    return now_cloth.cid

def add_text_color_data_to_config_data(text_color_list: List[str]):
    """ 将口上颜色加入角色模板数据 """
    character_id, character_name, text_color = text_color_list[0], text_color_list[1], text_color_list[2]
    # 用同Script\Config\game_config.py\load_font_data的方式赋予到config_font
    tem_data = {'cid':1000 + character_id,'name':character_name,'foreground':text_color, 'info': character_name + '的文本颜色'}
    # print(f"debug tem_data = {tem_data}")
    now_font = config_def.FontConfig()
    now_font.__dict__ = tem_data
    game_config.config_font[now_font.cid] = now_font
    game_config.config_font_data[now_font.name] = now_font.cid
