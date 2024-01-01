from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import handle_talent
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
import random

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


class System_Setting_Panel:
    """
    用于系统设置的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("系统设置")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的属性 """

    def draw(self):
        """绘制对象"""


        title_text = "系统设置"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            button_text = f"[001]主界面每次刷新时的空行数量："
            now_line_count = cache.system_setting.line_before_main_update
            button_text += f"{now_line_count}行"
            button_draw = draw.LeftButton(
                _(button_text),
                _("1"),
                window_width,
                cmd_func=self.line_before_main_update,
                )
            line_feed.draw()
            button_draw.draw()
            return_list.append(button_draw.return_text)

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def line_before_main_update(self):
        """主界面每次刷新时的空行数量"""
        while 1:
            return_list = []
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            now_line_count = cache.system_setting.line_before_main_update
            info_draw = draw.NormalDraw()
            info_text = ""
            info_text += f"\n当前{now_line_count}行，行数选择："
            info_draw.text = _(info_text)
            info_draw.draw()

            for i in [1,2,3,5,10,50]:
                button_text = f" [{i}行] "
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.change_line_before_main_update, args=i)
                button_draw.draw()
                return_list.append(button_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def change_line_before_main_update(self, line_count):
        """改变主界面每次刷新时的空行数量"""
        cache.system_setting.line_before_main_update = line_count

