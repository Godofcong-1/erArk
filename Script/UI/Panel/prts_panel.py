from typing import Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import character
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
import unicodedata

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


def chara_talk_info():
    """
    干员口上信息
    """

    handle_panel_normal = panel.PageHandlePanel(
        [], ShowCharaNameDraw, 20, 1, window_width, True, False, 0
    )

    while 1:
        line = draw.LineDraw("-", window_width)
        line.draw()
        id_list = []
        return_list = []

        # 循环角色提示信息
        for chara_adv_id in game_config.config_tip_chara_data_by_adv:
            # character_id = character.get_character_id_from_adv(chara_adv_id)
            id_list.append(chara_adv_id)

        # 同步数据
        handle_panel_normal.text_list = id_list
        handle_panel_normal.update()
        # 绘制
        handle_panel_normal.draw()
        return_list.extend(handle_panel_normal.return_list)

        line_feed.draw()
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()
        yrn = flow_handle.askfor_all(return_list)
        if yrn == back_draw.return_text:
            break


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
            chara_talk_info()

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
        self, chara_adv_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.chara_adv_id: int = chara_adv_id
        """ 角色adv_id """
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

        # 地文
        if self.chara_adv_id == 0:
            # 空白的提示
            name_draw = draw.NormalDraw()
            name_draw.text = ""
            name_draw.width = self.width
            # 获取角色提示信息
            tip_chara_data = game_config.config_tip_chara_data[0]
            now_text = _("[0000]通用文本  by {0}").format(tip_chara_data.writer_name)
            # 绘制
            button_draw = draw.LeftButton(
                _(now_text),
                _(now_text),
                self.width,
                normal_style=self.text_color,
                cmd_func=self.show_chara_info,
                args=(now_text, tip_chara_data.text),
                )
        else:
            # 获取角色id
            character_id = character.get_character_id_from_adv(self.chara_adv_id)
            character_data = cache.character_data[character_id]
            # 姓名信息
            name_text = character_data.name.ljust(12,'　')
            # 获取当前版本信息
            now_version = cache.all_system_setting.character_text_version[self.chara_adv_id]
            tip_cid_list = game_config.config_tip_chara_data_by_adv[self.chara_adv_id]
            version_text = "无"
            for tip_cid in tip_cid_list:
                tip_chara_data = game_config.config_tip_chara_data[tip_cid]
                if tip_chara_data.version_id == now_version:
                    version_text = "by {0}({1}kb)".format(tip_chara_data.writer_name, character_data.talk_size)
            # 按显示宽度计算，中文等宽字符计为2，ASCII计为1，末尾以全角空格填充，每两个宽度用一个全角空格，剩余用半角空格补齐
            def _display_width(s: str) -> int:
                w = 0
                for ch in s:
                    if unicodedata.east_asian_width(ch) in ("F", "W"):
                        w += 2
                    else:
                        w += 1
                return w

            target_width = 36
            cur_width = _display_width(version_text)
            if cur_width < target_width:
                pad = target_width - cur_width
                version_text += "　" * (pad // 2) + " " * (pad % 2)
            # 如果name_text中有英文字母或者数字，则按照其数量加上空格
            for char in name_text:
                if char.isascii():
                    name_text += " "
            now_text = f"[{str(self.chara_adv_id).rjust(4,'0')}]{name_text}  "
            now_text += _("当前选择版本：{0}             ").format(version_text)
            name_draw = draw.NormalDraw()
            name_draw.text = now_text
            name_draw.width = self.width
            # 颜色
            if character_data.text_color:
                self.text_color = character_data.name
            name_draw.style = self.text_color
            # 版本切换按钮
            now_text = _(" [版本切换] ")
            button_draw = draw.CenterButton(
                now_text,
                character_data.name,
                len(now_text) * 2,
                normal_style=self.text_color,
                cmd_func=self.show_character_text_version,
            )
        self.info_draw = name_draw
        self.now_draw = button_draw
        self.button_return = button_draw.return_text
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.info_draw.draw()
        self.now_draw.draw()

    def show_character_text_version(self):
        """
        切换角色文本版本
        """

        # 获取角色id
        character_id = character.get_character_id_from_adv(self.chara_adv_id)
        character_data = cache.character_data[character_id]
        # 获取当前版本信息
        tip_cid_list = game_config.config_tip_chara_data_by_adv[self.chara_adv_id]

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()
            line_feed.draw()

            # 提示信息
            info_text = _("○一个角色可能会有多个版本的文本，只能选择其中一个版本，或者不选择任何版本。\n")
            info_text += _("  选择一个版本后，将仅显示该版本的口上与事件。\n")
            info_text += _("  选择不使用版本时，该角色将回到只有地文的通用角色状态，不再使用任何口上。\n\n")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = self.width
            info_draw.draw()

            # 角色信息
            chara_text = f"[{str(self.chara_adv_id).rjust(4,'0')}]{character_data.name}\n\n"
            chara_draw = draw.NormalDraw()
            chara_draw.text = chara_text
            chara_draw.width = self.width
            chara_draw.style = self.text_color
            chara_draw.draw()
            # 获取当前版本信息
            now_version = cache.all_system_setting.character_text_version[self.chara_adv_id]

            # 遍历该角色的全版本
            for tip_cid in tip_cid_list:
                tip_chara_data = game_config.config_tip_chara_data[tip_cid]

                # 显示当前版本的角色信息，以及该版本的选择按钮
                now_text = f"版本：{tip_chara_data.version_id}  "
                now_text += f"by {tip_chara_data.writer_name}"
                # 如果是当前版本，则加上当前版本的标记
                if tip_chara_data.version_id == now_version:
                    now_text += _("(当前版本)")
                self.show_chara_info(now_text, tip_chara_data.text)
                # 版本切换按钮
                now_text = _(" [选择该版本] ")
                button_draw = draw.CenterButton(
                    now_text,
                    str(tip_cid),
                    len(now_text) * 2,
                    normal_style=self.text_color,
                    cmd_func=self.select_character_text_version,
                    args=(tip_chara_data.version_id),
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)
                line_feed.draw()

            # 不使用任何版本的按钮
            line_feed.draw()
            now_text = _(" [不使用任何版本] ")
            button_draw = draw.CenterButton(
                now_text,
                now_text,
                len(now_text) * 2,
                normal_style=self.text_color,
                cmd_func=self.select_character_text_version,
                args=(0),
            )
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed.draw()

            line_feed.draw()
            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            # 选择
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def select_character_text_version(self, version_id: int):
        """
        选择角色文本版本
        """
        # 设置当前版本
        cache.all_system_setting.character_text_version[self.chara_adv_id] = version_id

    def show_chara_info(self, name_text: str, info_text: str):
        """
        显示角色信息
        """

        info_text = info_text.replace("\\n", "\n")

        line_feed.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        line_feed.draw()

        name_draw = draw.NormalDraw()
        name_draw.text = name_text + "\n\n" + info_text + "\n\n"
        name_draw.width = self.width
        name_draw.style = self.text_color
        name_draw.draw()
