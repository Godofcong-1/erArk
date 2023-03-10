from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, attr_calculation, update, attr_text
from Script.UI.Moudle import draw, panel
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


class Originium_Arts_Panel:
    """
    用于源石技艺的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("源石技艺")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""


        title_text = "源石技艺"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            # line = draw.LineDraw("-", window_width)
            # line.draw()
            cinfo_draw = draw.NormalDraw()
            info_text = f"\n要进行哪方面的管理呢？\n"
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            # 选项面板
            # button_all_draw = panel.LeftDrawTextListPanel()

            DNT_Panel = Down_Negative_Talent_Panel(self.width)
            button0_text = f"[001]消除负面刻印"
            button0_draw = draw.LeftButton(
                _(button0_text),
                _("1"),
                window_width,
                cmd_func=DNT_Panel.draw
                )
            line_feed.draw()
            button0_draw.draw()
            return_list.append(button0_draw.return_text)

            if 1:
                button1_text = f"[002]时间停止(未实装)"
                button1_draw = draw.LeftButton(
                    _(button1_text),
                    _("2"),
                    window_width,
                    cmd_func=self.to_do,
                    args=(),
                    )
                line_feed.draw()
                button1_draw.draw()
                return_list.append(button1_draw.return_text)

            if 1:
                button2_text = f"[003]催眠(未实装)"
                button2_draw = draw.LeftButton(
                    _(button2_text),
                    _("3"),
                    window_width,
                    cmd_func=self.to_do,
                    args=(),
                    )
                line_feed.draw()
                button2_draw.draw()
                return_list.append(button2_draw.return_text)

            if 1:
                button3_text = f"[004]触觉系能力(未实装)"
                button3_draw = draw.LeftButton(
                    _(button3_text),
                    _("4"),
                    window_width,
                    cmd_func=self.to_do,
                    args=(),
                    )
                line_feed.draw()
                button3_draw.draw()
                return_list.append(button3_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def to_do(self):
        """n暂未实装"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n暂未实装\n")
        now_draw.draw()


class SelectRecommendBookButton:
    """
    点击后可选择作为推荐书籍类别的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, book_type_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.book_type_id: int = book_type_id
        """ 书籍类型编号 """
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

        type_data = game_config.config_book_type[self.book_type_id]
        button_text = f"[{str(type_data.cid).rjust(2,'0')}]：{type_data.father_type_name}-{type_data.son_type_name}"
        name_draw = draw.LeftDraw()
        if self.book_type_id in cache.base_resouce.recommend_book_type_set:
            button_text += f" (已推荐)"
            name_draw = draw.LeftButton(button_text, self.button_return, self.width,normal_style = "nowmap", cmd_func=self.button_0)
        else:
            name_draw = draw.LeftButton(button_text, self.button_return, self.width, cmd_func=self.button_0)

        """ 绘制的对象 """
        self.now_draw = name_draw

    def button_0(self):
        """选项1"""
        if self.book_type_id in cache.base_resouce.recommend_book_type_set:
            cache.base_resouce.recommend_book_type_set.remove(self.book_type_id)
        elif 3 - len(cache.base_resouce.recommend_book_type_set):
            cache.base_resouce.recommend_book_type_set.add(self.book_type_id)

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()



class Down_Negative_Talent_Panel:
    """
    用于降低负面素质的面板对象
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

        title_text = "降低负面素质"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        self.ability_id_list = [17,18]

        while 1:
            return_list = []
            # title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = "\n当前拥有反发刻印或恐怖刻印的角色有：\n\n"
            info_draw.text = info_text
            info_draw.draw()

            chara_exist_flag = False

            # 遍历备选人物名字并输出按钮
            for chara_id in cache.npc_id_got:
                character_data = cache.character_data[chara_id]

                for ability_id in self.ability_id_list:
                    if character_data.ability[ability_id]:
                        chara_exist_flag = True
                        name = character_data.name
                        adv_id = character_data.adv
                        button_text = f"[{str(adv_id).rjust(4,'0')}]:{name} "

                        button_draw = draw.LeftButton(
                            _(button_text),
                            _(str(adv_id)),
                            self.width,
                            cmd_func=self.choice_down_which,
                            args=(chara_id,),
                            )
                        # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                        return_list.append(button_draw.return_text)
                        button_draw.draw()
                        line_feed.draw()
                        break # 单角色满足条件则只出现一次

            if not chara_exist_flag:
                info_draw = draw.NormalDraw()
                info_text = "  没有符合条件的角色\n"
                info_draw.text = info_text
                info_draw.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def choice_down_which(self, chara_id):
        """选择照顾的方式"""
        character_data = cache.character_data[chara_id]
        self.chara_id = chara_id
        name = character_data.name

        pl_character_data = cache.character_data[0]
        panties_data = pl_character_data.pl_collection.npc_panties[self.chara_id]


        while 1:
            return_list = []

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = f"\n要降低[{name}]的哪个刻印呢？(需要消耗5条内裤，当前共{len(panties_data)}条)\n\n"
            info_draw.text = info_text
            info_draw.draw()

            for ability_id in self.ability_id_list:
                if character_data.ability[ability_id]:
                    ability_name = game_config.config_ability[ability_id].name
                    ability_lv = character_data.ability[ability_id]
                    button_text = f"{ability_name}[lv{ability_lv}] "

                    button_draw = draw.LeftButton(
                        _(button_text),
                        _(str(ability_id)),
                        self.width,
                        cmd_func=self.settle_down,
                        args=(ability_id,),
                        )
                    # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


    def settle_down(self, ability_id):
        """结算刻印降低"""
        info_draw = draw.NormalDraw()
        character_data = cache.character_data[self.chara_id]

        # 计算当前该角色的胖次数量，大于五则成功，不足则弹出失败提示
        pl_character_data = cache.character_data[0]
        panties_data = pl_character_data.pl_collection.npc_panties[self.chara_id]
        if len(panties_data) >= 5 or cache.debug_mode:
            for i in range(5):
                panties_data.pop()
            character_data.ability[ability_id] -= 1
            info_text = "  随着一阵火焰，5条内裤化为一缕青烟，消散在空中\n"
            info_text += f"  {character_data.name}感觉心里轻松了很多，对{pl_character_data.name}的印象有些改观了，{game_config.config_ability[ability_id].name}下降到了{character_data.ability[ability_id]}级\n"
        else:
            info_text = "  内裤数量不足\n"
        info_draw.text = info_text
        info_draw.draw()

