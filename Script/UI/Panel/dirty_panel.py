from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle,attr_text
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

class Dirty_Panel:
    """
    用于显示污浊界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        title_text = target_data.name + "身体部位污浊情况"

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], Dirty_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            name_draw = draw.NormalDraw()

            # 遍历全部位并输出结果
            # 部位列表[0"头发",1"脸部",2"口腔",3"胸部",4"腋部",5"手部",6"小穴",7"后穴",8"尿道",9"腿部",10"脚部",11"尾巴",12"兽角",13"兽耳"]
            # 服装列表[0"帽子",1"眼镜",2"耳部",3"脖子",4"嘴部",5"上衣",6"内衣（上）",7"手套",8"下衣",9"内衣（下）",10"袜子",11"鞋子",12"武器",13"附属物1",14"附属物2",15"附属物3",16"附属物4",17"附属物5"]
            a_clean_list = [" <脏污>"," <灌肠中>"," <已灌肠清洁过>"," <精液灌肠中>"," <已精液灌肠过>"]
            now_text = "\n"
            for i in range(11):
                now_text += "  " + target_data.dirty.body_semen[i][0] + "："
                if i == 7:
                    a_clean_text = a_clean_list[target_data.dirty.a_clean]
                    now_text += a_clean_text
                if i == 8:
                    if target_data.urinate_point <= 30:
                        now_text += " <残留的尿渍>"
                    elif target_data.urinate_point <= 120:
                        now_text += " <洁净>"
                    elif target_data.urinate_point <= 191:
                        now_text += " <些许尿意>"
                    elif target_data.urinate_point >= 192:
                        now_text += " <充盈的尿意>"
                if target_data.dirty.body_semen[i][1] != 0:
                    now_text += " <" + attr_text.get_semen_now_text(target_data.dirty.body_semen[i][2],0) + ">(" + str(target_data.dirty.body_semen[i][1]) + "ml)"
                now_text += "\n"
            now_text += "\n"

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




class Dirty_Draw:
    """
    污浊绘制对象
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

