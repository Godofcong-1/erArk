from distutils.command.config import config
from itertools import count
from Script.UI.Flow import creator_character_flow
from uuid import UUID
from typing import Tuple, List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    value_handle,
    game_type,
    text_handle,
    py_cmd,
    flow_handle,
    constant,
    rich_text,
)
from Script.Config import game_config, normal_config
from Script.Design import character_handle, talk, attr_calculation
import random

panel_info_data = {}

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """


class Born_Panel:
    """
    生孩子事件的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, mother_character_id: int):
        """初始化绘制对象"""
        self.width: int = window_width
        """ 绘制的最大宽度 """
        self.mother_character_id: int = mother_character_id
        """ 绘制的最大宽度 """
        # self.now_panel = _("关门")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        pl_character_data: game_type.Character = cache.character_data[0]
        mom_character_data: game_type.Character = cache.character_data[self.mother_character_id]

        # 如果是凯尔希怀孕则随机选一名医疗干员作为大夫，否则大夫为凯尔希
        doctor_id_list = []
        for character_id in cache.npc_id_got:
            character_data: game_type.Character = cache.character_data[character_id]
            if character_data.profession == 3:
                doctor_id_list.append(character_id)
            if character_data.name == "凯尔希":
                dr_k_id = character_id
        if mom_character_data.name == "凯尔希":
            doctor_id = random.choice(doctor_id_list)
        else:
            doctor_id = dr_k_id
        doctor_character_data: game_type.Character = cache.character_data[doctor_id]

        # 最外层的大循环
        while 1:
            # 内循环1：等待按键
            while 1:
                line = draw.LineDraw("-", window_width)
                line.draw()
                return_list = []

                mom_character_data.second_behavior[1315] = 1
                talk.must_show_talk_check(self.mother_character_id)
                info_draw = draw.WaitDraw()
                info_draw.width = self.width
                info_draw.width = self.width
                info_draw.text = f"\n 得知了{mom_character_data.name}即将生产的消息后，你第一时间来到了待产室，在短暂的陪伴后，目送着她被推入产房\n"
                info_draw.draw()
                line_feed.draw()
                button_text = " 焦急等待"
                button_draw = draw.LeftButton( _(button_text), _("\n"), self.width)
                button_draw.draw()
                return_list.append(button_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list:
                    break
            # 内循环2：起名字
            while 1:
                info_draw.text = f" 经过了漫长的等待之后，随着响亮的哭声，{doctor_character_data.name}推开产房的门，告诉你{mom_character_data.name}生了一个可爱的女儿，母女平安\n"
                info_draw.text += f" {mom_character_data.name}躺在床上，怀里抱着婴儿，对着你微微一笑，催促你给孩子起名\n"
                info_draw.draw()
                line_feed.draw()
                change_value_panel = panel.AskForOneMessage()
                change_value_panel.set(_(" 你决定给女儿取名为——"), 100)
                new_name = change_value_panel.draw()

                # 创建该角色
                character_handle.born_new_character(self.mother_character_id,new_name)
                child_character_data: game_type.Character = cache.character_data[len(cache.npc_tem_data)]
                child_character_data.pregnancy.born_time = cache.game_time

                info_draw.text = f"\n孩子的名字叫做{child_character_data.name}，她是{pl_character_data.name}的第{len(pl_character_data.relationship.child_id_list)}个孩子，也是{mom_character_data.name}的第{len(mom_character_data.relationship.child_id_list)}个孩子，请慢慢养育她长大成人吧\n"
                info_draw.draw()
                line_feed.draw()
                break

            mom_character_data.second_behavior[1317] = 1
            talk.must_show_talk_check(self.mother_character_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n{mom_character_data.name}的生产结束了，但她仍需要在住院部休息几天\n"
            mom_character_data.talent[22] = 0
            mom_character_data.talent[23] = 1
            draw_text += f"\n{mom_character_data.name}从[临盆]转变为[产后]\n"
            mom_character_data.talent[26] = 0
            draw_text += f"\n{mom_character_data.name}失去了[孕肚]\n"
            mom_character_data.experience[65] += 10
            mom_character_data.experience[68] += 10
            mom_character_data.experience[86] += 1
            draw_text += f"\n{mom_character_data.name}的Ｖ扩张经验+10，Ｗ扩张经验+10，妊娠经验+1\n"
            if mom_character_data.ability[9] < 5:
                mom_character_data.ability[9] = 5
                draw_text += f"\n{mom_character_data.name}的Ｖ扩张上升至5级\n"
            if mom_character_data.ability[12] < 5:
                mom_character_data.ability[12] = 5
                draw_text += f"\n{mom_character_data.name}的Ｗ扩张上升至5级\n"
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()
            now_draw = draw.WaitDraw()
            now_draw.text = "\n"
            now_draw.draw()
            now_draw = draw.WaitDraw()
            now_draw.text = "\n"
            now_draw.draw()

            break

