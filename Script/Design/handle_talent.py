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

def sleep_gain_talent(character_id: int):
    """
    获得在睡觉时结算的素质\n
    Keyword arguments:
    character_id -- 角色id\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 遍历全素质获得
    for gain_talent_cid in game_config.config_talent_gain:
        gain_talent_data = game_config.config_talent_gain[gain_talent_cid]
        gain_type = gain_talent_data.gain_type
        talent_id = gain_talent_data.talent_id
        # 需要为睡觉结算素质，而且NPC没有该素质
        if gain_type == 3 and character_data.talent[talent_id] == 0:

            # 以&为分割判定是否有多个需求
            if "&" not in gain_talent_data.gain_need:
                need_list = []
                need_list.append(gain_talent_data.gain_need)
            else:
                need_list = gain_talent_data.gain_need.split('&')

            # 遍历升级需求，判断是否符合升级要求
            judge = 1
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

            # 如果符合获得条件，则获得该素质
            if judge:
                character_data.talent[talent_id] = 1
                talent_name = game_config.config_talent[talent_id].name

                # 判断是否需要进行替代旧素质
                if gain_talent_data.replace_talent_id:
                    old_talent_id = gain_talent_data.replace_talent_id
                    character_data.talent[old_talent_id] = 0

                now_draw_succed = draw.WaitDraw()
                now_draw_succed.text = f"\n{character_data.name}获得了{talent_name}\n"
                now_draw_succed.draw()
    # print(f"debug {character_data.name}的睡觉结算素质结束，judge = {judge}")
