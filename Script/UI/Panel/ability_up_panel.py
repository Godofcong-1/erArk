from typing import Tuple, List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import see_character_info_panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    py_cmd,
    flow_handle,
    constant,
    rich_text,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, update, handle_talent

panel_info_data = {}

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

class Characterabi_show_Text:
    """
    角色能力升级显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        # self.column = column
        # """ 每行状态最大个数 """
        self.character_data = cache.character_data[self.character_id]
        """ 角色数据 """

    def draw(self):
        """绘制对象"""
        self.return_list = []
        # 绘制标题#
        line_feed.draw()
        title_text = "能力"
        type_line = draw.LittleTitleLineDraw(title_text, self.width, ":")
        type_line.draw()
        ability_list = game_config.config_ability_type_data
        for anility_type in ability_list:
            type_set = ability_list[anility_type]
            # 去掉刻印
            # print("anility_type : ",anility_type)
            if anility_type == 2:
                continue
            for ability_id in type_set:
                # 去掉与性别不符的感度与扩张
                if self.character_data.sex == 0:
                    if ability_id in {2, 4, 7, 9, 12, 34, 39}:
                        continue
                elif self.character_data.sex == 1:
                    if ability_id == 3:
                        continue
                # 这个_1是为了补空格让格式对齐#
                now_exp = 0
                now_exp = self.character_data.ability[ability_id]
                button_text = " "
                button_text += game_config.config_ability[ability_id].name
                button_text += " "
                # 根据不同的类型补不同数量的空格#
                if anility_type != 2 and anility_type != 4 and anility_type != 6:
                    button_text += "  "
                    if anility_type == 3 or anility_type == 5:
                        button_text += "  "
                button_text += attr_calculation.judge_grade(now_exp)
                button_text += " "
                button_text += str(now_exp)
                now_abi_up_panel = Characterabi_cmd_Text(self.character_id, self.width, ability_id)
                button_draw = draw.LeftButton(
                    _(button_text),
                    _(game_config.config_ability[ability_id].name),
                    self.width / 10,
                    cmd_func=now_abi_up_panel.draw)
                self.return_list.append(button_draw.return_text)
                button_draw.draw()
                # py_cmd.clr_cmd()
                # if yrn == self.back_draw.return_text:
                #     break
            # 只有不是最后一个类型就补个换行#
            if anility_type != 6:
                new_draw_n = draw.NormalDraw()
                new_draw_n.text = "\n"
                new_draw_n.width = 1
                new_draw_n.draw()
        # yrn = flow_handle.askfor_all(self.return_list)


class Characterabi_cmd_Text:
    """
    角色能力升级指令面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int, ability_id: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.ability_id = ability_id
        """ 当前的能力id """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        self.character_data = cache.character_data[self.character_id]
        """ 角色数据 """
        self.ability_level = self.character_data.ability[ability_id]
        """ 能力等级 """

    def draw(self):
        """绘制对象"""
        self.return_list = []
        self.jule_dict = {}
        judge = 1
        # 绘制标题#
        while 1:

            # 读取该能力在对应等级下的升级需求
            need_list = game_config.config_ability_up_data[self.ability_id][self.ability_level]
            line = draw.LineDraw(".", self.width)
            line.draw()
            line_feed.draw()

            # 遍历升级需求，并输出信息
            for need_text in need_list:
                # print(f"debug need_text = {need_text}")
                need_type = need_text.split('|')[0][0]
                need_type_id = int(need_text.split('|')[0][1:])
                need_value = int(need_text.split('|')[1])
                if need_type == "A":
                    abi_name = game_config.config_ability[need_type_id].name
                    button_text = "需要能力 : " + abi_name + " 至少为" + str(need_value) + "\n"
                    if self.character_data.ability[need_type_id] < need_value:
                        judge = 0
                elif need_type == "J":
                    juel_name = game_config.config_juel[need_type_id].name
                    button_text = "需要宝珠 : " + juel_name + " 至少为" + str(need_value) + "\n"
                    if self.character_data.juel[need_type_id] < need_value:
                        judge = 0
                    self.jule_dict[need_type_id] = need_value
                elif need_type == "E":
                    experience_name = game_config.config_experience[need_type_id].name
                    button_text = "需要经验 : " + experience_name + " 至少为" + str(need_value) + "\n"
                    if self.character_data.experience[need_type_id] < need_value:
                        judge = 0
                now_draw = draw.NormalDraw()
                now_draw.text = button_text
                now_draw.draw()

            # 判断是否可以升级
            if judge:
                now_draw_succed = draw.NormalDraw()
                now_draw_succed.text = "满足条件，要升级吗？\n"
                now_draw_succed.draw()
            else:
                now_draw_failed = draw.NormalDraw()
                now_draw_failed.text = "不满足条件，无法升级\n"
                now_draw_failed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
            back_draw.draw()
            self.return_list.append(back_draw.return_text)
            if judge:
                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width / 3, cmd_func=self.level_up)
                yes_draw.draw()
                self.return_list.append(yes_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn in self.return_list:
                break

    def level_up(self):
        for need_type_id in self.jule_dict:
            cache.character_data[self.character_id].juel[need_type_id] -= self.jule_dict[need_type_id]
        cache.character_data[self.character_id].ability[self.ability_id] += 1


class Character_talent_show_Text:
    """
    角色素质升级显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        # self.column = column
        # """ 每行状态最大个数 """
        self.character_data = cache.character_data[self.character_id]
        """ 角色数据 """

    def draw(self):
        """绘制对象"""
        self.return_list = []
        # 绘制标题#
        line_feed.draw()
        title_text = "素质"
        type_line = draw.LittleTitleLineDraw(title_text, self.width, ":")
        type_line.draw()
        # 前提说明#
        text_draw_introduce = draw.NormalDraw()
        text_draw_introduce.text = "陷落系素质\n 共通基础前提： 好感度500以上 信任度50%以上 反发刻印0\n 分为爱情系与隶属系两条路线，只能任选其一，选择后另一路线消失，仅在新周目时可以重置\n"
        text_draw_introduce.width = 1
        text_draw_introduce.draw()

        # 检测是哪个路线
        next_love_id,next_obey_id = 0,0
        for talent_id in {201,202,203,204}:
            if self.character_data.talent[talent_id]:
                next_love_id = talent_id + 1
        for talent_id in {211,212,213,214}:
            if self.character_data.talent[talent_id]:
                next_obey_id = talent_id + 1

        # 爱情路线
        if next_love_id or not next_obey_id:
            line = draw.LineDraw("-", self.width)
            line.draw()
            info_draw_love = draw.NormalDraw()
            info_draw_love.text = "爱情路线前提： 苦痛刻印0 恐怖刻印0 亲密等级高于顺从等级\n"
            info_draw_love.width = 1
            info_draw_love.draw()

            text_draw_love = draw.NormalDraw()
            text_draw_love.width = 1
            text_draw_love_text = ""
            judge = 1
            # 输出最高级的提示信息
            if self.character_data.talent[204]:
                text_draw_love_text += "已达到最高级-爱侣\n"
            # 路线选择
            elif next_love_id == 0:

                if self.character_data.favorability[0] < 500 or self.character_data.trust < 50 or self.character_data.ability[18] != 0:
                    text_draw_love_text += "  未满足共通基础前提\n"
                    judge = 0
                if self.character_data.ability[15] != 0 or self.character_data.ability[17] != 0 or self.character_data.ability[32] <= self.character_data.ability[31]:
                    text_draw_love_text += "  未满足爱情路线前提\n"
                    judge = 0
                text_draw_love.text = text_draw_love_text
                text_draw_love.draw()

                self.show_gain_need(201, judge)
            else:
                self.show_gain_need(next_love_id, judge)

        # 隶属路线
        if next_obey_id or not next_love_id:
            line = draw.LineDraw("-", self.width)
            line.draw()
            info_draw_obey = draw.NormalDraw()
            info_draw_obey.text = "隶属路线前提： 快乐刻印>=1 屈服刻印>=1 顺从等级高于亲密等级\n"
            info_draw_obey.width = 1
            info_draw_obey.draw()

            text_draw_obey = draw.NormalDraw()
            text_draw_obey.width = 1
            text_draw_obey_text = ""
            judge = 1
            if self.character_data.talent[214]:
                    text_draw_obey_text += "已达到最高级-奴隶\n"
            elif next_obey_id == 0:

                if self.character_data.favorability[0] < 500 or self.character_data.trust < 50 or self.character_data.ability[18] != 0:
                    text_draw_obey_text += "  未满足共通基础前提\n"
                    judge = 0
                if self.character_data.ability[13] == 0 or self.character_data.ability[14] == 0 or self.character_data.ability[31] <= self.character_data.ability[32]:
                    text_draw_obey_text += "  未满足隶属路线前提\n"
                    judge = 0
                text_draw_obey.text = text_draw_obey_text
                text_draw_obey.draw()

                self.show_gain_need(211, judge)
            else:
                self.show_gain_need(next_obey_id, judge)


    def show_gain_need(self, talent_id, judge):
        """具体显示需要什么"""

        need_all = game_config.config_talent_gain_data[talent_id]
        talent_name = game_config.config_talent[talent_id].name

        # 输出素质名
        now_draw = draw.NormalDraw()
        now_draw.text = f"下一级为：[{talent_name}]\n"
        now_draw.draw()

        # 以&为分割判定是否有多个需求
        if "&" not in need_all.gain_need:
            need_list = []
            need_list.append(need_all.gain_need)
        else:
            need_list = need_all.gain_need.split('&')

        # 遍历升级需求，并输出信息
        for need_text in need_list:
            need_type = need_text.split('|')[0][0]
            if len(need_text.split('|')[0]) >= 2:
                need_type_id = int(need_text.split('|')[0][1:])
            need_value = int(need_text.split('|')[1])
            # print(f"debug need_type = {need_type},need_type_id = {need_type_id},need_value = {need_value}")
            if need_type == "A":
                abi_name = game_config.config_ability[need_type_id].name
                button_text = f"  需要能力[{abi_name}]至少为 {str(need_value)}\n"
                if self.character_data.ability[need_type_id] < need_value:
                    judge = 0
            elif need_type == "T":
                tal_name = game_config.config_talent[need_value].name
                button_text = f"  需要素质[{tal_name}]\n"
                if not self.character_data.talent[need_value]:
                    judge = 0
            elif need_type == "J":
                juel_name = game_config.config_juel[need_type_id].name
                button_text = f"  需要宝珠[{juel_name}]至少为 {str(need_value)}\n"
                if self.character_data.juel[need_type_id] < need_value:
                    judge = 0
                # self.jule_dict[need_type_id] = need_value
            elif need_type == "E":
                experience_name = game_config.config_experience[need_type_id].name
                button_text = f"  需要经验[{experience_name}]至少为 {str(need_value)}\n"
                if self.character_data.experience[need_type_id] < need_value:
                    judge = 0
            elif need_type == "F":
                button_text = f"  需要好感至少为 {str(need_value)}\n"
                if self.character_data.favorability[0] < need_value:
                    judge = 0
            elif need_type == "X":
                button_text = f"  需要信赖至少为 {str(need_value)}\n"
                if self.character_data.trust < need_value:
                    judge = 0
            now_draw = draw.NormalDraw()
            now_draw.text = button_text
            now_draw.draw()

        if talent_id in {201,211}:
            line_feed.draw()
            if judge:
                now_draw_succed = draw.NormalDraw()
                now_draw_succed.text = "满足条件，确定选择此路线吗？\n"
                now_draw_succed.draw()

                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width / 3, cmd_func=self.level_up, args = talent_id)
                yes_draw.draw()
                self.return_list.append(yes_draw.return_text)
                line_feed.draw()

            else:
                now_draw_failed = draw.NormalDraw()
                now_draw_failed.text = "不满足条件，无法选择\n"
                now_draw_failed.draw()

        elif talent_id == 203:
            line_feed.draw()
            now_draw = draw.NormalDraw()
            now_draw.text = "满足条件后需要准备【戒指】，然后进行【告白】，成功后即可获得\n"
            now_draw.draw()

        elif talent_id == 213:
            line_feed.draw()
            now_draw = draw.NormalDraw()
            now_draw.text = "满足条件后需要准备【项圈】，然后进行【戴上项圈】，成功后即可获得\n"
            now_draw.draw()

    def level_up(self, talent_id):
        now_draw_succed = draw.WaitDraw()
        now_draw_succed.text = "选择成功\n"
        now_draw_succed.draw()
        handle_talent.gain_talent(self.character_id, 1, talent_id)

        # 等待1分钟以输出结果
        character_data: game_type.Character = cache.character_data[0]
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.duration = 1
        update.game_update_flow(1)


class Character_abi_up_main_Handle:
    """
    带返回的角色能力上升主面板
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

    def draw(self):
        """绘制面板"""
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
        now_panel_id = _("属性升级")
        while 1:
            self.return_list = []
            now_character_panel = Character_abi_up_sub_Handle(self.character_id, self.width)
            now_character_panel.change_panel(now_panel_id)
            now_character_panel.draw()
            back_draw.draw()
            line_feed.draw()
            self.return_list.extend(now_character_panel.return_list)
            self.return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn == back_draw.return_text:
                break
            elif yrn in now_character_panel.draw_data:
                now_panel_id = yrn


class Character_abi_up_sub_Handle:
    """
    角色能力上升子面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel: str = _("属性升级")
        """ 当前的属性页id """
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        main_first_draw = Character_abi_up_main_panel(character_id, width)
        self.draw_data = {
            _("属性升级"): main_first_draw,
        }
        """ 按钮文本对应属性面板 """
        self.handle_panel = panel.CenterDrawButtonListPanel()
        """ 属性列表的控制面板 """
        self.handle_panel.set(
            [f"[{text}]" for text in self.draw_data.keys()],
            list(self.draw_data.keys()),
            width,
            4,
            f"[{self.now_panel}]",
            self.change_panel,
        )

    def change_panel(self, panel_id: str):
        """
        切换当前面板
        Keyword arguments:
        panel_id -- 要切换的面板id
        """
        self.now_panel = panel_id
        self.handle_panel.set(
            [f"[{text}]" for text in self.draw_data.keys()],
            list(self.draw_data.keys()),
            self.width,
            4,
            f"[{self.now_panel}]",
            self.change_panel,
        )

    def draw(self):
        """绘制面板"""
        self.draw_data[self.now_panel].draw()
        self.return_list = []
        self.return_list.extend(self.draw_data[self.now_panel].return_list)
        line_feed.draw()
        line = draw.LineDraw("=", self.width)
        line.draw()
        self.handle_panel.draw()
        self.return_list.extend(self.handle_panel.return_list)


class Character_abi_up_main_panel:
    """
    角色能力升级面板第一页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = see_character_info_panel.CharacterInfoHead(character_id, width)
        Juel_draw = see_character_info_panel.CharacterJuelText(character_id, width, 8, 0)
        Experience_draw = see_character_info_panel.CharacterExperienceText(character_id, width, 8, 0)
        abi_draw = Characterabi_show_Text(character_id, width)
        tal_draw = Character_talent_show_Text(character_id, width)
        if character_id == 0:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                Juel_draw,
                Experience_draw,
                abi_draw,
            ]
        else:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                Juel_draw,
                Experience_draw,
                abi_draw,
                tal_draw,
            ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()
            if "return_list" in label.__dict__:
                self.return_list.extend(label.return_list)
