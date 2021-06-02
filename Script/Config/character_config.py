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
            v = get_text._(now_data[k])
            if k.startswith("V|"):
                a = ""
                now_k = int(k.lstrip("V|"))
                now_tem.Ability[now_k] = a
            else:
                now_tem.__dict__[k] = v
        character_tem_list.append(now_tem)
