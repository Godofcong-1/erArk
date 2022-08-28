from typing import List
from types import FunctionType
from Script.Core import cache_control, text_handle, get_text, flow_handle, constant, py_cmd, game_type
from Script.UI.Moudle import panel, draw
from Script.Config import game_config, normal_config


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


class SeeCharacterItemBagPanel:
    """
    查看角色道具背包面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 绘制的角色id """
        self.width: int = width
        """ 最大绘制宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.character_data = cache.character_data[character_id]
        item_list = list(self.character_data.item)
        item_panel = panel.PageHandlePanel(item_list, ItemNameDraw, 20, 7, width, 1, 1, 0, "", "|")
        self.handle_panel = item_panel
        """ 页面控制对象 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("人物道具"), self.width)
        title_draw.draw()
        while 1:
            # 绘制金钱
            money_text = "当前持有龙门币：" + str(self.character_data.money) + "，合成玉：" + str(self.character_data.orundum) + "，至纯源石：" + str(self.character_data.Originite_Prime)
            now_draw = draw.NormalDraw()
            now_draw.text = money_text
            now_draw.width = self.width
            now_draw.draw()
            line_feed.draw()

            # 绘制道具面板
            self.return_list = []
            self.handle_panel.update()
            self.handle_panel.draw()
            self.return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            self.return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class ItemNameDraw:
    """
    按道具id绘制道具名
    Keyword arguments:
    text -- 道具的配表id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    butoon_id -- 数字按钮的id
    """

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text: int = int(text)
        """ 道具的配表id """
        self.draw_text: str = ""
        """ 道具名绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        item_config = game_config.config_item[self.text]
        item_name = item_config.name
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                self.draw_text = f"{index_text} {item_name}"
                self.button_return = str(button_id)
            else:
                self.draw_text = item_name
                self.button_return = item_name
        else:
            self.draw_text = f"[{item_name}]"

    def draw(self):
        """绘制道具"""
        if self.is_button:
            now_draw = draw.Button(self.draw_text, self.button_return, cmd_func=self.draw_item_info)
        else:
            now_draw = draw.NormalDraw()
            now_draw.text = self.draw_text
        now_draw.width = self.width
        now_draw.draw()

    def draw_item_info(self):
        """绘制道具信息"""
        now_draw = ItemInfoDraw(self.text, window_width)
        now_draw.draw()


class ItemInfoDraw:
    """
    按道具id绘制道具数据
    Keyword arguments
    cid -- 道具id
    width -- 最大绘制宽度
    """

    def __init__(self, cid: int, width: int):
        """初始化绘制对象"""
        self.cid: int = int(cid)
        """ 道具的配表id """
        self.width: int = width
        """ 最大宽度 """

    def draw(self):
        """绘制道具信息"""
        py_cmd.clr_cmd()
        item_config = game_config.config_item[self.cid]
        item_draw = draw.WaitDraw()
        item_draw.text = f"{item_config.name}:{item_config.info}"
        item_draw.width = self.width
        item_draw.draw()
        line_feed = draw.NormalDraw()
        line_feed.text = "\n"
        line_feed.width = 1
        line_feed.draw()
