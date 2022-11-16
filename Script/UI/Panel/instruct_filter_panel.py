from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, cooking, update
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


class Instruct_filter_Panel:
    """
    用于查看指令过滤面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("指令过滤", self.width)

        self.handle_panel = panel.PageHandlePanel([], HandleFilterButtonList, 999, 8, self.width, 1, 1, 0)

        instruct_index_list = []
        
        for now_type in cache.instruct_type_filter:
            if now_type != constant.InstructType.SYSTEM:
                for instruct in constant.instruct_type_data[now_type]:
                    instruct_index_list.append(instruct)


        while 1:
            py_cmd.clr_cmd()

            self.handle_panel.text_list = instruct_index_list
            self.handle_panel.update()
            title_draw.draw()
            return_list = []

            line_feed.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class HandleFilterButtonList:
    """
    点击后可调整指令过滤的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, index: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.index: int = index
        """ 指令编号 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        # 按钮绘制
        name_draw = draw.NormalDraw()

        instruct_name = constant.handle_instruct_name_data[self.index]
        button_text = f"[{self.index}]{instruct_name}"

        text_style = "standard" if cache.instruct_index_filter[self.index] else "un_open_mapbutton"

        name_draw = draw.LeftButton(
            button_text, self.button_return, self.width, normal_style = text_style, cmd_func=self.chose_button
        )
        self.button_return = index
        self.now_draw = name_draw
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw

    def chose_button(self):
        """玩家点击了选项"""
        cache.instruct_index_filter[self.index] = 1 if cache.instruct_index_filter[self.index] == 0 else 0

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
