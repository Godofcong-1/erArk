from typing import Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import character
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

class Prts_Panel:
    """
    用于显示教程界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("部门总概况")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("普瑞赛斯")

        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            title_draw.draw()

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            return_list = []
            now_draw = panel.LeftDrawTextListPanel()

            pl_name = cache.character_data[0].name
            info_text = _("身份验证通过，最高权限账户——管理员账户\n\n")
            info_text += _("Dr.{0}，欢迎访问普瑞赛斯终端，请问我可以为您做什么？\n\n").format(pl_name)
            info_text += _("○请注意，本终端内的资料查询功能会直接涉及游戏流程和实际内容的介绍和剧透，如果更倾向于自己体验和摸索的话，请仅在必要时刻再使用本功能。\n\n")
            info_draw.text = info_text
            info_draw.draw()

            # 要输出的变量名称以及注释
            draw_text_list = []
            draw_text_list.append(_("[000]查询系统本身的相关资料"))
            draw_text_list.append(_("[001]获得日常生活的建议"))
            draw_text_list.append(_("[002]询问如何与干员相处"))
            draw_text_list.append(_("[003]与干员发生肉体关系时的注意事项"))
            draw_text_list.append(_("[004]怎么样才能更好的经营罗德岛"))
            draw_text_list.append(_("[010]干员的口上信息"))
            draw_text_list.append(_("[011]与普瑞赛斯闲聊（未实装）"))

            # 循环输出以上各个问题
            for i in range(len(draw_text_list)):
                button_draw = draw.LeftButton(
                    draw_text_list[i],
                    f"\n{i}",
                    self.width ,
                    cmd_func=self.select_question,
                    args=i
                )
                now_draw.draw_list.append(button_draw)
                now_draw.width += len(button_draw.text)
                now_draw.draw_list.append(line_feed)
                return_list.append(button_draw.return_text)

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

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, prts_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        prts_type -- 要切换的面板类型
        """

        self.now_panel = prts_type

    def select_question(self, key_index: int):
        """
        选择问题
        """

        # 正常问题部分
        while 1:
            self.fater_type = key_index
            # 跳过未实装的
            if self.fater_type >= 5:
                break

            line = draw.LineDraw("-", self.width)
            line.draw()
            return_list = []

            # 循环输出该父分类下的每个子类的问题
            for son_type in game_config.config_prts_data[self.fater_type]:
                Q_data = game_config.config_prts_data[self.fater_type][son_type][0]
                now_text = f"[{str(son_type).rjust(3,'0')}]{Q_data.text}"
                button_draw = draw.LeftButton(
                    _(now_text),
                    _(now_text),
                     self.width,
                    cmd_func=self.show_answer,
                    args=(son_type,),
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

        # 干员口上信息
        if self.fater_type == 5:
            self.chara_talk_info()

    def chara_talk_info(self):
        """
        干员口上信息
        """

        self.handle_panel_normal = panel.PageHandlePanel(
            [], ShowCharaNameDraw, 15, 1, window_width, 1, 0, 0
        )

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()
            id_list = []
            return_list = []

            # 循环角色提示信息
            for cid in game_config.config_tip_chara:
                tip_chara_data = game_config.config_tip_chara[cid]
                character_id = character.get_character_id_from_adv(tip_chara_data.chara_adv_id)
                # 跳过未招募的
                if character_id not in cache.npc_id_got:
                    continue
                # 跳过没有内容的
                if tip_chara_data.text == _("暂无"):
                    continue
                id_list.append(cid)

            # 同步数据
            self.handle_panel_normal.text_list = id_list
            self.handle_panel_normal.update()
            # 绘制
            self.handle_panel_normal.draw()
            return_list.extend(self.handle_panel_normal.return_list)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def show_answer(self, key_index: int):
        """
        显示答案
        """

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()

            A_data = game_config.config_prts_data[self.fater_type][key_index][1]
            answer_text_list = A_data.text.split('\\n')
            answer_text = ""
            for sub_text in answer_text_list:
                answer_text += f" {sub_text}\n"

            answer_draw = draw.WaitDraw()
            answer_draw.text = answer_text
            answer_draw.width = self.width
            answer_draw.draw()

            line_feed.draw()
            break


class ShowCharaNameDraw:
    """
    点击后可查看角色名字列表的按钮对象
    Keyword arguments:
    text -- 食物名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, cid: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.cid: int = cid
        """ 角色信息id """
        self.draw_text: str = ""
        """ 食物名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        self.text_color: str = "standard"
        """ 文本颜色 """

        # 获取角色提示信息
        tip_chara_data = game_config.config_tip_chara[cid]
        # 获取角色id
        character_id = character.get_character_id_from_adv(tip_chara_data.chara_adv_id)
        character_data = cache.character_data[character_id]
        now_text = f"[{str(tip_chara_data.chara_adv_id).rjust(4,'0')}]{character_data.name}  by {tip_chara_data.writer_name}"
        # 颜色
        if character_data.text_color:
            self.text_color = character_data.name
        # 绘制
        button_draw = draw.LeftButton(
            _(now_text),
            _(now_text),
            self.width,
            normal_style=self.text_color,
            cmd_func=self.show_chara_info,
            args=(now_text, tip_chara_data.text),
            )
        self.button_return = button_draw.return_text

        self.now_draw = button_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def show_chara_info(self, name_text: str, info_text: str):
        """
        显示角色信息
        """

        line_feed.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        line_feed.draw()

        name_draw = draw.WaitDraw()
        name_draw.text = name_text + "\n\n" + info_text
        name_draw.width = self.width
        name_draw.style = self.text_color
        name_draw.draw()

        line_feed.draw()
