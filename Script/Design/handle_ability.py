import datetime
from types import FunctionType
from Script.Design import (
    settle_behavior,
    character,
    character_handle,
    map_handle,
    attr_calculation,
    game_time,
    cooking,
    update,
    attr_text,
    handle_instruct,
    character_behavior,
    basement,
)
from Script.Core import cache_control, constant, constant_effect, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw
from Script.UI.Panel import event_option_panel

import random

_: FunctionType = get_text._
""" 翻译api """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """

def gain_ability(character_id: int):
    """
    结算可以获得的能力\n
    Keyword arguments:
    character_id -- 角色id\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 遍历全能力
    for ability_cid in game_config.config_ability:
        ability_data = game_config.config_ability[ability_cid]
        # 跳过刻印部分
        if ability_data.ability_type == 2:
            continue
        ability_level = character_data.ability[ability_cid]
        ability_up_data = game_config.config_ability_up_data[ability_cid][ability_level]

        # 以&为分割判定是否有多个需求
        if "&" not in ability_up_data.up_need:
            need_list = []
            need_list.append(ability_up_data.up_need)
        else:
            need_list = ability_up_data.up_need.split('&')

        # 遍历升级需求，判断是否符合升级要求
        judge = 1
        jule_dict = {}
        for need_text in need_list:
            need_type = need_text.split('|')[0][0]
            if len(need_text.split('|')[0]) >= 2:
                need_type_id = int(need_text.split('|')[0][1:])
            need_value = int(need_text.split('|')[1])
            # print(f"debug need_type = {need_type},need_type_id = {need_type_id},need_value = {need_value}")
            if need_type == "A":
                if character_data.ability[need_type_id] < need_value:
                    judge = 0
                    break
            elif need_type == "T":
                if not character_data.talent[need_value]:
                    judge = 0
                    break
            elif need_type == "J":
                jule_dict[need_type_id] = need_value
                if character_data.juel[need_type_id] < need_value:
                    judge = 0
                    break
            elif need_type == "E":
                if character_data.experience[need_type_id] < need_value:
                    judge = 0
                    break
            elif need_type == "F":
                if character_data.favorability[0] < need_value:
                    judge = 0
                    break
            elif need_type == "X":
                if character_data.trust < need_value:
                    judge = 0
                    break

            # 如果符合获得条件，则该能力升级
            if judge:
                character_data.ability[ability_cid] += 1
                ability_name = ability_data.name

                # 减少对应的珠
                for need_type_id in jule_dict:
                    character_data.juel[need_type_id] -= jule_dict[need_type_id]

                now_draw_succed = draw.WaitDraw()
                now_draw_succed.text = f"\n{character_data.name}的{ability_name}提升到{str(ability_level+1)}级\n"
                now_draw_succed.draw()
    # print(f"debug {character_data.name}的睡觉结算素质结束，judge = {judge}")
