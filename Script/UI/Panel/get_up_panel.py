from types import FunctionType
from Script.UI.Moudle import draw
from Script.UI.Panel import see_character_info_panel
from Script.Design import game_time
from Script.Core import get_text, cache_control, game_type, flow_handle

_: FunctionType = get_text._
""" 翻译api """

cache: game_type.Cache = cache_control.cache

class GetUpPanel:
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