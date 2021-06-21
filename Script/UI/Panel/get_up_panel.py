from types import FunctionType
from Script.UI.Moudle import draw
from Script.UI.Panel import see_character_info_panel
from typing import Tuple, List
from Script.Design import game_time
from Script.Core import get_text, cache_control, game_type, flow_handle
from Script.Config import game_config, normal_config
from Script.Core import (
    cache_control,
    get_text,
    value_handle,
    game_type,
    text_handle,
    py_cmd,
    flow_handle,
    constant,
)
_: FunctionType = get_text._
""" 翻译api """

cache: game_type.Cache = cache_control.cache
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """

class GetUpPanel_1:
    """
    用于查看角色起床界面面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self,character_id:int,width:int):
        """ 初始化绘制对象 """
        self.width:int = width
        """ 绘制的最大宽度 """
        self.character_id:int = character_id
        """ 要绘制的角色id """

    def draw(self):
        """ 绘制面板 """
        while 1:
            title_draw = draw.TitleLineDraw(_("主页"), self.width)
            character_data = cache.character_data[self.character_id]
            title_draw.draw()
            date_draw = draw.NormalDraw()
            date_draw.width = self.width
            date_draw.text = f"{game_time.get_date_text()} {game_time.get_week_day_text()} "
            date_draw.draw()
            name_draw = draw.Button(character_data.name,character_data.name,cmd_func=self.see_character)
            name_draw.width = self.width - len(date_draw)
            name_draw.draw()
            flow_handle.askfor_all([name_draw.return_text])

    def see_character(self):
        """ 绘制角色属性 """
        attr_panel = see_character_info_panel.SeeCharacterInfoPanel(self.character_id,self.width)
        attr_panel.draw()


class GetUpPanel:
    """
    带切换控制的总起床面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    character_list -- 角色id列表
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.title_draw = draw.TitleLineDraw(_("睡梦面板"), self.width)
        cache.now_panel_id = constant.Panel.IN_SCENE
        self.back_draw = draw.CenterButton(_("[起床]"), _("返回"), self.width / 3)
        self.time_draw = draw.CenterButton(_("[睡觉时间]"), _("返回"), self.width / 3)
        character_list = [0,1,2,3]
        now_list = list(character_list)
        self.now_character_panel = see_character_info_panel.SeeCharacterInfoHandle(self.character_id, self.width, now_list)
        self.chara_data_draw = draw.CenterButton(_("[角色列表]"), _("角色列表"), self.width / 3, cmd_func=self.now_character_panel.draw)


    def draw(self):
        """绘制面板"""
        
        old_button_draw = draw.CenterButton(
            _("[上一人]"), _("上一人"), self.width / 3, cmd_func=self.old_character
        )
        next_button_draw = draw.CenterButton(
            _("[下一人]"), _("下一人"), self.width / 3, cmd_func=self.next_character
        )
        while 1:
            self.title_draw.draw()
            self.return_list = []
            # self.now_character_panel.draw()
            # old_button_draw.draw()
            self.back_draw.draw()
            self.chara_data_draw.draw()
            # next_button_draw.draw()
            line_feed.draw()
            # self.return_list.append(old_button_draw.return_text)
            self.return_list.append(self.back_draw.return_text)
            self.return_list.append(self.chara_data_draw.return_text)
            # self.return_list.append(next_button_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn == self.back_draw.return_text:
                break

    def old_character(self):
        """切换显示上一人"""
        # now_index = self.character_list.index(self.character_id)
        # self.character_id = self.character_list[now_index - 1]

    def next_character(self):
        """切换显示下一人"""
        # now_index = self.character_list.index(self.character_id) + 1
        # if now_index > len(self.character_list) - 1:
        #     now_index = 0
        # self.character_id = self.character_list[now_index]
