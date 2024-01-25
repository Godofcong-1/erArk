import os, glob
from typing import List
from Script.Core import json_handle,game_type,get_text

character_config_file = os.path.join("data","Character.json")
""" 角色模板配置文件路径 """
character_config_data = {}
""" 原始角色模板数据 """
character_tem_list:List[game_type.NpcTem] = []
""" 角色模板数据列表 """

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
            # 新的服装数据读取，读取的是str，直接获得服装数据
            elif k.startswith("C|"):
                now_k = int(k.lstrip("C|"))
                # 针对默认服装
                if now_k in [5999, 8999]:
                    continue
                # print(f"debug : {k} {v}")
                # 针对还没有修改完毕类型的服装的特别转换
                if len(k) >= 5:
                    now_data_len = len(k) - 4
                    now_k = int(k[2: 2 + now_data_len])
                    if now_k > 13:
                        now_k  = int(now_k / 10)
                    # print(f"debug : now_k = {now_k}")
                cloth_list = [v, now_k]
                now_tem.Cloth.append(cloth_list)
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
