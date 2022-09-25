import random
from functools import wraps
from typing import List
from types import FunctionType
from Script.Core import get_text, constant, game_type, cache_control, flow_handle, py_cmd

from Script.Design import (
    handle_panel,
    character,
    character_handle,
    cooking,
    map_handle,
    attr_calculation,
)
from Script.UI.Moudle import panel, draw
from Script.UI.Panel import see_character_info_panel
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
line_feed_draw = draw.NormalDraw()
""" 绘制换行对象 """
line_feed_draw.text = "\n"
line = draw.LineDraw("=", width)
""" 标题线绘制对象 """


@handle_panel.add_panel(constant.Panel.CREATOR_CHARACTER)
def creator_character_panel():
    """创建角色面板"""
    cache.character_data[0] = game_type.Character()
    character_handle.init_character_list()
    while 1:
        if input_name_panel():
            character.init_attr(0)
            game_start()
            if confirm_character_attr_panel():
                break
        cache.character_data[0] = game_type.Character()
    cache.now_panel_id = constant.Panel.IN_SCENE


def game_start():
    """初始化游戏数据"""
    character_handle.init_character_dormitory()
    character_handle.init_character_position()
    # course.init_phase_course_hour()
    # interest.init_character_interest()
    # course.init_character_knowledge()
    # course.init_class_teacher()
    # course.init_class_time_table()
    # course.init_teacher_table()
    cooking.init_recipes()
    cooking.init_restaurant_data()
    character_position = cache.character_data[0].position
    map_handle.character_move_scene(["0"], character_position, 0)
    cache.school_longitude = random.uniform(120.9, 122.12)
    cache.school_latitude = random.uniform(30.7, 31.53)


def confirm_character_attr_panel():
    """确认角色属性面板"""
    # now_attr_panel = see_character_info_panel.SeeCharacterInfoPanel(0, width)
    askfor_panel = panel.OneMessageAndSingleColumnButton()
    while 1:
        line_feed_draw.draw()
        now_attr_panel = Character_creat_Handle()
        now_attr_panel.draw()
        ask_list = []
        ask_list.extend(now_attr_panel.return_list)
        now_line = draw.LineDraw("~", width)
        now_line.draw()
        askfor_list = [_("睁开双眼"), _("重新设定")]
        start_id = 0
        now_id_judge = 0
        now_id_list = []
        for now_id in ask_list:
            if now_id.isdigit():
                now_id_judge = 1
                now_id_list.append(int(now_id))
        if now_id_judge:
            start_id = max(now_id_list) + 1
        askfor_panel.set(askfor_list, _("这样可以吗?"), start_id)
        askfor_panel.draw()
        askfor_panel_return_list = askfor_panel.get_return_list()
        ask_list.extend(askfor_panel_return_list.keys())
        yrn = flow_handle.askfor_all(ask_list)
        py_cmd.clr_cmd()
        if yrn in askfor_panel_return_list:
            return askfor_panel_return_list[yrn] == askfor_list[0]


def input_name_panel() -> bool:
    """
    输入角色名面板
    Return arguments:
    bool -- 完成角色创建校验
    """
    character_data = cache.character_data[0]
    ask_name_panel = panel.AskForOneMessage()
    ask_name_panel.set(_("你能回忆起自己的名字吗？（默认称呼为博士，此处仅输入姓名即可）"), 10)
    line_feed_draw.draw()
    line.draw()
    not_num_error = draw.NormalDraw()
    not_num_error.text = _("角色名不能为纯数字，请重新输入\n")
    not_system_error = draw.NormalDraw()
    not_system_error.text = _("角色名不能为系统保留字，请重新输入\n")
    not_name_error = draw.NormalDraw()
    not_name_error.text = _("已有角色使用该姓名，请重新输入\n")
    create_judge = 0
    while 1:
        now_name = ask_name_panel.draw()
        if now_name.isdigit():
            not_num_error.draw()
            continue
        if now_name in get_text.translation_values or now_name in get_text.translation._catalog:
            not_system_error.draw()
            continue
        if now_name in cache.npc_name_data:
            not_name_error.draw()
            continue
        character_data.name = now_name
        character_data.nick_name = "博士"
        create_judge = 1

        break
    return create_judge


class Character_creat_Handle:
    """
    角色创建页面对象
    Keyword arguments:
    """

    def __init__(self):
        """初始化绘制对象"""
        self.width = normal_config.config_normal.text_width
        info_draw = see_character_info_panel.CharacterInfoHead(0, width)
        info_draw.draw_title = False
        sex_draw = Character_Sex(self.width)
        bonus_draw = Character_Bonus(self.width)
        abi_draw = see_character_info_panel.CharacterabiText(0, width)
        tal_draw = see_character_info_panel.CharacterTalentText(0, width, 8, 0)
        self.draw_list: List[draw.NormalDraw] = [
            info_draw,
            sex_draw,
            bonus_draw,
            abi_draw,
            tal_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        title_draw = draw.TitleLineDraw(_("详细设定"), self.width)
        title_draw.draw()
        for label in self.draw_list:
            label.draw()
            if "return_list" in label.__dict__:
                self.return_list.extend(label.return_list)



class Character_Sex:
    """
    角色性别面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        character_data: game_type.Character = cache.character_data[0]
        sex_text = game_config.config_sex_tem[character_data.sex].name
        now_draw = panel.LeftDrawTextListPanel()

        Now_draw = draw.LeftDraw()
        Now_draw.width = 1
        Now_draw.text = f"\n 性别：{sex_text}      "
        now_draw.draw_list.append(Now_draw)
        now_draw.width += len(Now_draw.text)

        button_text = f"    【改变性别】"
        sex_button_draw = draw.LeftButton(
            _(button_text),
            _(str(character_data.sex)),
            self.width /10,
            cmd_func=self.change())
        self.return_list.append(sex_button_draw.return_text)

        now_draw.draw_list.append(sex_button_draw)
        now_draw.width += len(sex_button_draw.text)
        # now_draw.draw_list.append(line_feed_draw)

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed_draw.draw()
            else:
                label.draw()

    def change(self):
        """性别改变"""
        print(f"debug 性别改变")
        character_data: game_type.Character = cache.character_data[0]
        if character_data.sex:
            character_data.sex = 0
        else:
            character_data.sex = 1

class Character_Bonus:
    """
    角色奖励点数面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        self.talent_id = 0
        """ 当前需要改变的素质 """

    def draw(self):
        """绘制面板"""
        character_data: game_type.Character = cache.character_data[0]
        bonus_all = 0

        Now_draw = draw.LeftDraw()
        Now_draw.width = 1
        Now_draw.text = f"\n 当前为第{str(cache.game_round)}周目\n"
        Now_draw.text += f" 当前总奖励点数   ="
        if cache.game_round == 1:
            Now_draw.text += f" 30 (新玩家奖励+30)"
            bonus_all += 30
        Now_draw.draw()
        self.bonus_now = bonus_all

        Now_draw = draw.LeftDraw()
        Now_draw.width = 1
        Now_draw.text = f"\n 可选素质奖励有：\n"
        Now_draw.draw()

        if character_data.talent[304]:
            button_text = f"   ●博士信息素(10)：增加指令实行值"
            self.talent_id = 304
            button_draw = draw.LeftButton(
                _(button_text),
                _(str(self.talent_id)),
                self.width,
                cmd_func=self.get_talent())
            self.return_list.append(button_draw.return_text)
            button_draw.draw()
        else:
            button_text = f"   ○博士信息素(10)：增加指令实行值"
            self.talent_id = 304
            button_draw = draw.LeftButton(
                _(button_text),
                _(str(self.talent_id)),
                self.width,
                cmd_func=self.get_talent())
            self.return_list.append(button_draw.return_text)
            button_draw.draw()
        line_feed_draw.draw()

        if character_data.talent[307]:
            button_text = f"   ●内衣透视(10)：可以看到对方当前穿的内衣"
            self.talent_id = 307
            button_draw = draw.LeftButton(
                _(button_text),
                _(str(self.talent_id)),
                self.width,
                cmd_func=self.get_talent())
            self.return_list.append(button_draw.return_text)
            button_draw.draw()
        else:
            button_text = f"   ○内衣透视(10)：可以看到对方当前穿的内衣"
            self.talent_id = 307
            button_draw = draw.LeftButton(
                _(button_text),
                _(str(self.talent_id)),
                self.width,
                cmd_func=self.get_talent())
            self.return_list.append(button_draw.return_text)
            button_draw.draw()
        line_feed_draw.draw()

        Now_draw = draw.LeftDraw()
        Now_draw.width = 1
        Now_draw.text = f"\n\n 当前剩余奖励点数 = {self.bonus_now}\n"
        Now_draw.draw()


    def get_talent(self):
        """获得素质"""
        character_data: game_type.Character = cache.character_data[0]
        # print(f"debug self.talent_id = {self.talent_id}")
        if character_data.talent[self.talent_id]:
            character_data.talent[self.talent_id] = 0
            self.bonus_now += 10
        else:
            character_data.talent[self.talent_id] = 1
            self.bonus_now -= 10
