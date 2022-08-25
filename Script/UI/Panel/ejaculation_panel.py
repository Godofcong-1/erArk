from typing import Tuple
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle
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


class Ejaculation_Panel:
    """
    用于显示射精界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """

    def draw(self):
        """绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        title_name = "射精部位选择"
        title_draw = draw.TitleLineDraw(title_name, self.width)
        handle_panel = panel.PageHandlePanel([], Ejaculation_NameDraw, 10, 6, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()
            position_list = []
            for i in range(11):
                position_list.append(target_data.dirty.body_semen[i][0])
            handle_panel.text_list = position_list
            handle_panel.update()
            handle_panel.draw()
            return_list.extend(handle_panel.return_list)
            cache.now_panel_id = constant.Panel.IN_SCENE
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            # if yrn == back_draw.return_text:
            cache.now_panel_id = constant.Panel.IN_SCENE
            break


class Ejaculation_NameDraw:
    """
    点击后可选择射精部位按钮对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(self, text: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text = text
        """ 道具id """
        self.draw_text: str = ""
        """ 道具名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        name_draw = draw.NormalDraw()
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text} {self.text}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.shoot_here
                )
            else:
                button_text = f"[{self.text}]"
                name_draw = draw.CenterButton(
                    button_text, self.text, self.width, cmd_func=self.shoot_here
                )
                self.button_return = self.text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{self.text}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def shoot_here(self):
        py_cmd.clr_cmd()
        character_data: game_type.Character = cache.character_data[0]
        cache.shoot_position = self.button_id
        position_text_list = ["头发","脸部","嘴部","胸部","腋部","手部","小穴","后穴","尿道","腿部","脚部"]
        position_text = position_text_list[self.button_id]
        now_text = "在",position_text,"射精"
        now_draw = draw.WaitDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()
        line_feed.draw()
        line_feed.draw()

