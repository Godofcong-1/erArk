from distutils.command.config import config
from itertools import count
from Script.UI.Flow import creator_character_flow
from uuid import UUID
from typing import Tuple, List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import see_clothing_info_panel, see_item_info_panel
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
from Script.Design import character_handle, map_handle, attr_calculation
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
                line_feed.draw()
                return_list = []

                info_draw = draw.WaitDraw()
                info_draw.width = self.width
                info_draw.width = self.width
                info_draw.text = f"\n得知了{mom_character_data.name}即将生产的消息后，你第一时间来到了候产室外等候\n"
                info_draw.draw()
                line_feed.draw()
                button_text = "等待"
                button_draw = draw.LeftButton( _(button_text), _("\n"), self.width)
                button_draw.draw()
                return_list.append(button_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list:
                    break
            while 1:
                info_draw.text = f"经过了漫长的等待之后，{doctor_character_data.name}推开手术室的门，告诉你{mom_character_data.name}生了一个可爱的女儿，母女平安\n"
                info_draw.draw()
                line_feed.draw()
                break

            character_handle.born_new_character(self.mother_character_id)

            mom_character_data.talent[22] = 0
            mom_character_data.talent[23] = 1
            mom_character_data.talent[30] = 0
            draw_text = "\n※※※※※※※※※\n"
            draw_text += f"\n{mom_character_data.name}的生产结束了，母女平安，孩子很健康\n"
            draw_text += f"\n{mom_character_data.name}仍需要在住院部休息几天，之后会恢复正常的工作和生活\n"
            draw_text += f"\n{mom_character_data.name}从[临盆]转变为[产后]\n"
            draw_text += f"\n{mom_character_data.name}失去了[孕肚]\n"
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


            # askfor_panel = panel.OneMessageAndSingleColumnButton()
            # askfor_list = [_("是"), _("否")]
            # askfor_panel.set(askfor_list, _(info_text), 0)
            # askfor_panel_return_list = askfor_panel.get_return_list()
            # return_list.extend(askfor_panel_return_list.keys())
            # now_draw.draw_list.append(askfor_panel)

            # yrn = flow_handle.askfor_all(return_list)
            # if yrn in return_list:
            #     if askfor_panel_return_list[yrn] == askfor_list[0]:
            #         return 1
            #     return 0
            break

