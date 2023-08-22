from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import settle_behavior, game_time
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


class Event_option_Panel:
    """
    总面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width: int = width
        """ 绘制的最大宽度 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        line_feed.draw()
        character_data: game_type.Character = cache.character_data[self.character_id]
        behavior_id = character_data.behavior.behavior_id
        father_event_id = character_data.event.event_id

        # 获取父事件的前提信息
        father_event_data: game_type.Event = game_config.config_event[father_event_id]
        self.handle_panel = panel.PageHandlePanel([], SonEventDraw, 20, 1, self.width, 1, 1, 0)
        father_promise = father_event_data.premise

        son_event_list = []

        # 开始遍历当前行为的事件表
        if behavior_id in game_config.config_event_status_data:
            for event_id in game_config.config_event_status_data[behavior_id]:
                event_config = game_config.config_event[event_id]
                son_flag = True
                # 需要含有子事件前提
                if len(event_config.premise) and "option_son" in event_config.premise:
                    for premise in father_promise:
                        # 子事件的前提必须完全包含父事件的前提
                        if premise not in event_config.premise:
                            son_flag = False
                            break
                    # 加入到子事件的列表中
                    if son_flag:
                        son_event_list.append(event_id)

        while 1:
            py_cmd.clr_cmd()

            self.handle_panel.text_list = son_event_list
            self.handle_panel.update()
            return_list = []
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

class SonEventDraw:
    """
    显示子事件选项对象
    Keyword arguments:
    event_id -- 事件id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, event_id: str, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.event_id = event_id
        """ 事件id """
        self.son_event = game_config.config_event[self.event_id]
        """ 子事件 """
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
        name_draw = draw.NormalDraw()
        # print("text :",text)
        option_text = self.son_event.text.split("|")[0]
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}{option_text}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.run_son_event
                )
            else:
                button_text = f"[{option_text}]"
                name_draw = draw.CenterButton(
                    button_text, option_text, self.width, cmd_func=self.run_son_event
                )
                self.button_return = option_text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{option_text}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """


    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def run_son_event(self):
        """点击后运行对应的子事件"""
        character_data: game_type.Character = cache.character_data[0]
        character_data.event.son_event_id = self.event_id

