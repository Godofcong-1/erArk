import os
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
            elif k.startswith("C|"):
                now_k = int(k.lstrip("C|"))
                now_tem.Cloth.append(now_k)
            else:
                now_tem.__dict__[k] = v
        character_tem_list.append(now_tem)
