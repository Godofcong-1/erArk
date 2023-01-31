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
    character_handle,
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
from Script.UI.Panel import sp_event_panel
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
    character_data.pregnancy.fertilization_rate += now_rate


def check_fertilization(character_id: int):
    """
    根据受精概率并判断是否受精
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 仅在排卵日进行判定
    if character_data.pregnancy.reproduction_period != 5:
        return 0
    # 如果当前已受精，则跳过判断
    for i in {20,21,22}:
        if character_data.talent[i] == 1:
            character_data.pregnancy.fertilization_rate = 0
            return 0
    # 随机数判断是否受精
    if character_data.pregnancy.fertilization_rate:
        if random.randint(1,100) <= character_data.pregnancy.fertilization_rate:
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n博士的精子与{character_data.name}的卵子结合，成功在子宫里着床了\n"
            draw_text += f"\n{character_data.name}获得了[受精]\n"
            draw_text += "\n※※※※※※※※※\n"
            character_data.talent[20] = 1
            character_data.pregnancy.fertilization_time = cache.game_time
        else:
            draw_text = f"\n精子在{character_data.name}的阴道中游荡，但未能成功受精\n"
            character_data.pregnancy.fertilization_rate = 0
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = draw_text
        now_draw.draw()


def check_pregnancy(character_id: int):
    """
    判断是否由受精变为怀孕
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是受精状态
    if character_data.talent[20]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.fertilization_time
        past_day = (start_date - end_date).days
        # 
        if past_day >= 30:
            character_data.talent[20] = 0
            character_data.talent[21] = 1
            character_data.talent[30] = 1
            character_data.talent[31] = 1
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n随着怀孕的进程，{character_data.name}挺起了大肚子，隆起的曲线下是正在孕育的新生命\n"
            draw_text += f"\n{character_data.name}有孕在身，将会暂停工作和部分娱乐\n"
            draw_text += f"\n{character_data.name}从[受精]转变为[妊娠]\n"
            draw_text += f"\n{character_data.name}获得了[孕肚]\n"
            draw_text += f"\n{character_data.name}获得了[泌乳]\n"
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_near_born(character_id: int):
    """
    判断是否开始临盆
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是妊娠状态
    if character_data.talent[21]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.fertilization_time
        past_day = (start_date - end_date).days
        # 
        if past_day >= 85:
            character_data.talent[21] = 0
            character_data.talent[22] = 1
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n随着怀孕的进程，{character_data.name}临近生产，即将诞下爱的结晶\n"
            draw_text += f"\n{character_data.name}在临盆期内会一直躺在医疗部住院区的病床上，多去陪陪她，静候生产的来临吧\n"
            draw_text += f"\n{character_data.name}从[妊娠]转变为[临盆]\n"
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_born(character_id: int):
    """
    判断是否开始生产
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是临盆状态
    if character_data.talent[22]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.fertilization_time
        past_day = (start_date - end_date).days - 84
        # 每过一天+20%几率判断是否生产
        now_rate = past_day * 20
        # print(f"debug {character_data.name}进入生产检测，当前生产几率为{now_rate}%")
        if random.randint(1,100) <= now_rate:
            draw_panel = sp_event_panel.Born_Panel(character_id)
            draw_panel.draw()


def check_rearing(character_id: int):
    """
    判断是否开始育儿
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是产后状态
    if character_data.talent[23]:
        # 计算经过的天数
        child_id = character_data.relationship.child_id_list[-1]
        child_character_data: game_type.Character = cache.character_data[child_id]
        start_date = cache.game_time
        end_date = child_character_data.pregnancy.born_time
        past_day = (start_date - end_date).days
        # 
        if past_day >= 2:
            character_data.talent[23] = 0
            character_data.talent[24] = 1
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n{character_data.name}的产后休息结束了\n"
            draw_text += f"\n{character_data.name}接下来的行动重心会以照顾{child_character_data.name}为主\n"
            draw_text += f"\n{character_data.name}从[产后]转变为[育儿]\n"
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_rearing_complete(character_id: int):
    """
    判断是否完成育儿
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是育儿状态
    if character_data.talent[24]:
        # 计算经过的天数
        child_id = character_data.relationship.child_id_list[-1]
        child_character_data: game_type.Character = cache.character_data[child_id]
        start_date = cache.game_time
        end_date = child_character_data.pregnancy.born_time
        past_day = (start_date - end_date).days
        # 
        if past_day >= 30:
            character_data.talent[24] = 0
            character_data.talent[30] = 0
            character_handle.get_new_character(child_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n在{character_data.name}的悉心照料下，{child_character_data.name}顺利长大了\n"
            draw_text += f"\n{character_data.name}完成了育儿行动，开始回到正常的工作生活中来\n"
            draw_text += f"\n{child_character_data.name}能够初步独立了，在长大成人之前会一直在教育区上课学习\n"
            draw_text += f"\n{character_data.name}失去了[育儿]\n"
            draw_text += f"\n{character_data.name}失去了[泌乳]\n"
            draw_text += f"\n{child_character_data.name}成为了一名准干员\n"
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_all_pregnancy(character_id: int):
    """
    进行受精怀孕的全流程检查
    \n\n包括刷新受精概率、是否受精、是否由受精变为怀孕、是否结束怀孕
    """

    get_fertilization_rate(character_id)
    check_fertilization(character_id)
    check_pregnancy(character_id)
    check_near_born(character_id)
    check_born(character_id)
    check_rearing(character_id)
    check_rearing_complete(character_id)


def update_reproduction_period(character_id: int):
    """
    刷新生理周期
    """

    character_data: game_type.Character = cache.character_data[character_id]
    now_reproduction = character_data.pregnancy.reproduction_period
    if now_reproduction == 6:
        character_data.pregnancy.reproduction_period = 0
    else:
        character_data.pregnancy.reproduction_period += 1
