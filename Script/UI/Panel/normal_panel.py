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
from Script.Design import update, map_handle, attr_calculation

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


class Close_Door_Panel:
    """
    用于关门的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("关门")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "关门"

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            now_position = character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]
            now_draw = panel.LeftDrawTextListPanel()

            # 地点关门判定的三个分支
            if now_scene_data.close_type == 0:
                info_text = "\n当前地点无法关门，要继续吗："
            elif now_scene_data.close_type == 1:
                info_text = "\n当前地点可以关门，关上之后其他人就进不来了，要关门吗："
            else:
                info_text = "\n当前地点可以关门，但别人还是可以进入该地点，只是无法发现你们，要关门吗："


            askfor_panel = panel.OneMessageAndSingleColumnButton()
            askfor_list = [_("是"), _("否")]
            askfor_panel.set(askfor_list, _(info_text), 0)
            askfor_panel_return_list = askfor_panel.get_return_list()
            return_list.extend(askfor_panel_return_list.keys())
            now_draw.draw_list.append(askfor_panel)

            self.draw_list: List[draw.NormalDraw] = []
            """ 绘制的文本列表 """
            self.draw_list.extend(now_draw.draw_list)

            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                if askfor_panel_return_list[yrn] == askfor_list[0]:
                    return 1
                return 0


class Read_Book_Panel:
    """
    用于读书的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("读书")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "读书"
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 当前借书数量信息
            book_id_set = character_data.entertainment.borrow_book_id_set

            # 如果未借书的话直接输出提示信息
            if len(book_id_set) == 0:
                info_draw = draw.NormalDraw()
                borrow_limit_text = f"\n当前未持有书籍，请前去图书馆借书\n"
                info_draw.text = borrow_limit_text
                info_draw.width = self.width
                info_draw.draw()
            # 已借书则遍历输出按钮
            else:
                for book_id in book_id_set:
                    book_data = game_config.config_book[book_id]
                    son_type_name = game_config.config_book_type[book_data.type].son_type_name
                    book_text = f"  [{str(book_id).rjust(3,'0')}]({son_type_name}){book_data.name}"

                    button_draw = draw.LeftButton(
                        _(book_text),
                        _(str(book_id)),
                        self.width,
                        cmd_func=self.read,
                        args=(book_id,),
                        )
                    # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()
                    # now_draw.draw_list.append(button_draw)

            # self.draw_list: List[draw.NormalDraw] = []
            # """ 绘制的文本列表 """
            # self.draw_list.extend(now_draw.draw_list)

            # for label in self.draw_list:
            #     if isinstance(label, list):
            #         for value in label:
            #             value.draw()
            #         line_feed.draw()
            #     else:
            #         label.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def read(self, book_id):
        """读选择的书"""
        character_data: game_type.Character = cache.character_data[0]
        book_data = game_config.config_book[book_id]
        character_data.behavior.behavior_id = constant.Behavior.READ_BOOK
        character_data.state = constant.CharacterStatus.STATUS_READ_BOOK
        character_data.behavior.book_id = book_id
        character_data.behavior.book_name = book_data.name
        character_data.behavior.duration = 30
        update.game_update_flow(30)
