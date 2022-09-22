from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle,attr_text,attr_calculation
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

class Collection_Panel:
    """
    用于显示收藏品界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("信物")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "收藏品"
        collection_type_list = [_("信物"), _("内裤")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], collection_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for collection_type in collection_type_list:
                if collection_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{collection_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(collection_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{collection_type}]",
                        collection_type,
                        self.width / len(collection_type_list),
                        cmd_func=self.change_panel,
                        args=(collection_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()


            name_draw = draw.NormalDraw()

            now_text = ""
            if self.now_panel == "信物":

                for i in range(len(character_data.pl_collection.token_list)):
                    if character_data.pl_collection.token_list[i]:
                        npc_name = cache.character_data[i].name
                        npc_token = cache.character_data[i].token_text
                        now_text += f"\n  {npc_name}：{npc_token}"

            elif self.now_panel == "内裤":

                for npc_id in cache.character_data:
                    if npc_id != 0:

                        if character_data.pl_collection.first_panties[npc_id] != "" or len(character_data.pl_collection.npc_panties[npc_id]):
                            npc_name = cache.character_data[npc_id].name
                            now_text += f"\n  {npc_name}："
                            if npc_id in character_data.pl_collection.first_panties:
                                now_text += f" {character_data.pl_collection.first_panties[npc_id]}"
                            if npc_id in character_data.pl_collection.npc_panties:
                                for pan in character_data.pl_collection.npc_panties[npc_id]:
                                    now_text += f" {pan}"
                            now_text += f"\n"


            name_draw.text = now_text
            name_draw.width = self.width
            name_draw.draw()


            return_list.extend(handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


    def change_panel(self, collection_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        collection_type -- 要切换的面板类型
        """


        if collection_type == "信物":
            self.now_panel = "信物"

        elif collection_type == "内裤":
            self.now_panel = "内裤"


class collection_Draw:
    """
    收藏品绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, text: int, width: int):
        """初始化绘制对象"""
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """

        name_draw = draw.NormalDraw()

        name_draw.text = ""
        name_draw.width = self.width
        self.draw_text = ""
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

