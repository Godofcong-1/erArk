import random
from typing import Dict
from Script.Config import game_config


def get_random_nature() -> Dict[int, int]:
    """
    随机生成角色性格
    Return arguments:
    Dict[int,int] -- 角色性格数据 性格id:性格数值
    """
    nature_data = {}
    for k in game_config.config_nature:
        nature = game_config.config_nature[k]
        nature_data[nature.cid] = random.uniform(0, 100)
    return nature_data
