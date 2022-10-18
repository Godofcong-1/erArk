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
        self.now_panel = _("身体")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        title_text = target_data.name + "污浊情况"
        dirty_type_list = [_("身体"), _("服装")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], Dirty_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for dirty_type in dirty_type_list:
                if dirty_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{dirty_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(dirty_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{dirty_type}]",
                        dirty_type,
                        self.width / len(dirty_type_list),
                        cmd_func=self.change_panel,
                        args=(dirty_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()


            name_draw = draw.NormalDraw()

            # 遍历全部位并输出结果
            # 部位列表[0"头发",1"脸部",2"口腔",3"胸部",4"腋部",5"手部",6"小穴",7"后穴",8"尿道",9"腿部",10"脚部",11"尾巴",12"兽角",13"兽耳"]
            # 服装列表[0"帽子",1"眼镜",2"耳部",3"脖子",4"嘴部",5"上衣",6"内衣（上）",7"手套",8"下衣",9"内衣（下）",10"袜子",11"鞋子",12"武器",13"附属物1",14"附属物2",15"附属物3",16"附属物4",17"附属物5"]
            if self.now_panel == "身体":
                a_clean_list = [" <脏污>"," <灌肠中>"," <已灌肠清洁过>"," <精液灌肠中>"," <已精液灌肠过>"]
                now_text = "\n"
                for i in range(11):
                    now_text += "  " + target_data.dirty.body_semen[i][0] + "："

                    # 小穴
                    if i == 6:
                        # 处女判定
                        if not target_data.talent[0]:
                            now_day = cache.game_time.day
                            first_day = target_data.first_record.first_sex_time.day
                            if now_day == first_day:
                                now_text +=" <破处血>"

                        # 润滑判定
                        if target_data.status_data[8]:
                            level = attr_calculation.get_status_level(target_data.status_data[8])
                            if level <= 2:
                                now_text +=" <些许爱液>"
                            elif level <= 4:
                                now_text +=" <充分湿润>"
                            elif level <= 6:
                                now_text +=" <泛滥的一塌糊涂>"
                            else :
                                now_text +=" <泛滥的一塌糊涂>"

                        # 精液判定
                        if target_data.dirty.body_semen[i][1]:
                            now_text +=" <残留的精液>"

                    # 后穴
                    if i == 8:
                        a_clean_text = a_clean_list[target_data.dirty.a_clean]
                        now_text += a_clean_text

                    # 尿道
                    if i == 9:
                        if target_data.urinate_point <= 30:
                            now_text += " <残留的尿渍>"
                        elif target_data.urinate_point <= 120:
                            now_text += " <洁净>"
                        elif target_data.urinate_point <= 191:
                            now_text += " <些许尿意>"
                        elif target_data.urinate_point >= 192:
                            now_text += " <充盈的尿意>"
                    if target_data.dirty.body_semen[i][1] and i != 6:
                        now_text += f" <{str(target_data.dirty.body_semen[i][1])}ml精液>"
                    now_text += "\n"
                now_text += "\n"

            elif self.now_panel == "服装":

                now_text = ""
                # 遍历全部衣服类型
                for clothing_type in game_config.config_clothing_type:
                    type_name = game_config.config_clothing_type[clothing_type].name
                    # 当该类型里有衣服存在的时候才显示
                    if len(target_data.cloth[clothing_type]):
                        # 正常情况下不显示胸部和内裤的服装,debug或该部位可以显示则显示
                        if clothing_type in {6,9} and not cache.debug_mode:
                            if not target_data.cloth_see[clothing_type]:
                                continue
                        now_text += f"  [{type_name}]:"
                        # 如果有多个衣服，则依次显示
                        for cloth_id in target_data.cloth[clothing_type]:
                            cloth_name = game_config.config_clothing_tem[cloth_id].name
                            now_text += f" {cloth_name}"
                            # 如果该部位有精液，则显示精液信息
                            if target_data.dirty.cloth_semen[clothing_type][1] != 0:
                                now_text += f" ({str(target_data.dirty.cloth_semen[clothing_type][1])}ml精液)"
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


    def change_panel(self, dirty_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        dirty_type -- 要切换的面板类型
        """

        self.now_panel = dirty_type


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

