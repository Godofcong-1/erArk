import math
import random
import datetime
from uuid import UUID
from types import FunctionType
from typing import Dict
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    constant,
    value_handle,
    get_text,
    save_handle,
)
from Script.Design import (
    settle_behavior,
    game_time,
    character,
    handle_premise,
    event,
    talk,
    map_handle,
    cooking,
    attr_calculation,
    character_move
)
from Script.UI.Moudle import draw
from Script.UI.Panel import draw_event_text_panel
from Script.Config import game_config, normal_config
import time

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """


def get_fertilization_rate(character_id: int):
    """
    根据当前V精液量计算受精概率
    """

    character_data: game_type.Character = cache.character_data[character_id]
    semen_count = character_data.dirty.body_semen[7][1]
    semen_level = character_data.dirty.body_semen[7][2]
    now_reproduction = character_data.pregnancy.reproduction_period
    # 基础概率
    now_rate = math.pow(semen_count / 1000,2) * 100 + semen_level * 5
    # 生理周期修正
    now_rate *= game_config.config_reproduction_period[now_reproduction].type
    character_data.pregnancy.fertilization_rate = now_rate


def check_fertilization(character_id: int):
    """
    计算受精概率并判断是否受精
    """
    get_fertilization_rate(character_id)
    character_data: game_type.Character = cache.character_data[character_id]
    # 如果当前已受精，则跳过判断
    for i in {20,21}:
        if character_data.talent[i] == 1:
            return 0
    # 随机数判断是否受精
    if character_data.pregnancy.fertilization_rate:
        if random.randint(1,100) <= character_data.pregnancy.fertilization_rate:
            draw_text = f"\n精子在{character_data.name}的阴道中游荡，成功与卵子结合了\n"
            draw_text += f"\n{character_data.name}获得了[受精]\n"
            character_data.talent[20] = 1
        else:
            draw_text = f"\n精子在{character_data.name}的阴道中游荡，但未能成功受精\n"
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = draw_text
        now_draw.draw()

