from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, cooking, update, character
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


class Undress_Panel:
    """
    用于查看脱衣服面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("脱衣服")
        """ 当前绘制的面板类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("脱衣服", self.width)

        self.handle_panel = panel.PageHandlePanel([], SeeUndressButtonList, 10, 1, self.width, 1, 1, 0)
        cooking.init_makefood_data()
        while 1:
            py_cmd.clr_cmd()
            button_text_list = ["脱到只穿内衣      ","脱到只穿袜子手套等","脱到全裸          ","把内裤收走        "]

            self.handle_panel.text_list = button_text_list
            self.handle_panel.update()
            title_draw.draw()
            return_list = []

            line_feed.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class SeeUndressButtonList:
    """
    点击后可选择脱衣服选项的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: str, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.button_name_text: str = text
        """ 指令名字绘制文本 """
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

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        # 按钮绘制
        name_draw = draw.NormalDraw()
        text_flag = False

        index_text = text_handle.id_index(button_id)
        button_text = f"{index_text}{self.button_name_text}"
        # print(f"debug button_id = {button_id}")
        # print(f"debug target_data.cloth = {target_data.cloth}")


        # 0号指令,脱到只穿内衣
        if self.button_id == 0:
            cloth_count = len(target_data.cloth.cloth_wear[5]) + len(target_data.cloth.cloth_wear[8])
            if cloth_count:
                button_text += f" ：会脱掉"
                for i in {5,8}:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += f" ：无可脱的衣服"
                text_flag = True

        # 1号指令,脱到只穿袜子手套等
        elif self.button_id == 1:
            cloth_count = len(target_data.cloth.cloth_wear[5]) + len(target_data.cloth.cloth_wear[6]) + len(target_data.cloth.cloth_wear[8]) + len(target_data.cloth.cloth_wear[9])
            if cloth_count:
                button_text += f" ：会脱掉"
                for i in {5,6,8,9}:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += f" ：无可脱的衣服"
                text_flag = True

        # 2号指令,脱到全裸
        elif self.button_id == 2:
            cloth_count = 0
            for i in game_config.config_clothing_type:
                cloth_count += len(target_data.cloth.cloth_wear[i])
            if cloth_count:
                button_text += f" ：会脱掉"
                for i in game_config.config_clothing_type:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += f" ：无可脱的衣服"
                text_flag = True

        # 3号指令,把内裤收走
        if self.button_id == 3:
            cloth_count = len(target_data.cloth.cloth_wear[9])
            if cloth_count:
                button_text += f" ：会收走"
                for i in {9}:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += f" ：无可收的内裤"
                text_flag = True

        # 如果按钮不可选则变成文本
        if not text_flag:
            name_draw = draw.LeftButton(
                button_text, self.button_return, self.width, cmd_func=self.chose_button
            )
        else:
            name_draw = draw.LeftDraw()
            name_draw.text = button_text
            name_draw.width = self.width

        self.button_return = text
        self.now_draw = name_draw
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw

    def chose_button(self):
        """玩家点击了选项"""
        character.init_character_behavior_start_time(0, cache.game_time)
        character_data = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        character_data.behavior.duration = 5
        update.game_update_flow(5)

        # 0号指令,脱到只穿内衣
        if self.button_id == 0:

            for i in {5,8}:
                target_data.cloth.cloth_off[i],target_data.cloth.cloth_wear[i] = target_data.cloth.cloth_wear[i],[]
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK


        # 1号指令,脱到只穿袜子手套等
        elif self.button_id == 1:
            for i in {5,6,8,9}:
                target_data.cloth.cloth_off[i],target_data.cloth.cloth_wear[i] = target_data.cloth.cloth_wear[i],[]
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

        # 2号指令,脱到全裸
        elif self.button_id == 2:
            for i in game_config.config_clothing_type:
                target_data.cloth.cloth_off[i],target_data.cloth.cloth_wear[i] = target_data.cloth.cloth_wear[i],[]
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

        # 3号指令,把内裤收走
        elif self.button_id == 3:
            for i in {9}:
                pan_id = target_data.cloth.cloth_wear[i][-1]
                pan_name = game_config.config_clothing_tem[pan_id].name
                character_data.pl_collection.npc_panties_tem.setdefault(character_data.target_character_id, [])
                character_data.pl_collection.npc_panties_tem[character_data.target_character_id].append(pan_id)
                target_data.cloth.cloth_wear[i] = []
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = _(f"\n获得了{target_data.name}的{pan_name}，可在藏品馆里纳入收藏\n")
            now_draw.draw()
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
