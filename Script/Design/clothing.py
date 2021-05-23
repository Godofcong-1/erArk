import random
import math
import uuid
from typing import Dict
from Script.Core import game_type
from Script.Config import game_config


def creator_suit(suit_id: int, sex: int) -> Dict[int, game_type.Clothing]:
    """
    创建套装
    Keyword arguments:
    suit_name -- 套装模板
    sex -- 性别模板
    Return arguments:
    Dict[int,game_type.Clothing] -- 套装数据 服装穿戴位置:服装数据
    """
    suit_data = game_config.config_clothing_suit_data[suit_id][sex]
    clothing_data = {}
    for clothing_id in suit_data:
        clothing = creator_clothing(clothing_id)
        clothing_data[clothing.wear] = clothing
    return clothing_data


def creator_clothing(clothing_tem_id: int) -> game_type.Clothing:
    """
    创建服装的基础函数
    Keyword arguments:
    clothing_tem_id -- 服装id
    Return arguments:
    game_type.Clothing -- 生成的服装数据
    """
    clothing_data = game_type.Clothing()
    clothing_data.uid = uuid.uuid4()
    clothing_data.sexy = random.randint(1, 1000)
    clothing_data.handsome = random.randint(1, 1000)
    clothing_data.elegant = random.randint(1, 1000)
    clothing_data.fresh = random.randint(1, 1000)
    clothing_data.sweet = random.randint(1, 1000)
    clothing_data.warm = random.randint(0, 30)
    clothing_data.price = sum(
        [
            clothing_data.__dict__[x]
            for x in clothing_data.__dict__
            if isinstance(clothing_data.__dict__[x], int)
        ]
    )
    clothing_data.cleanliness = 100
    clothing_data.evaluation = game_config.config_clothing_evaluate_list[
        math.floor(clothing_data.price / 480) - 1
    ]
    clothing_data.tem_id = clothing_tem_id
    clothing_data.wear = game_config.config_clothing_tem[clothing_tem_id].clothing_type
    return clothing_data
