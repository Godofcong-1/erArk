from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import update, handle_talent

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
        text_draw_introduce.width = 1
        text_draw_introduce_text = _("陷落系素质\n 共通基础前提：")

        # 检测共通基础前提
        judge = 1
        text_draw_introduce_text += _(" 好感度500以上")
        if self.character_data.favorability[0] < 500:
            text_draw_introduce_text += "(X)"
            judge = 0
        else:
            text_draw_introduce_text += "(√)"
        text_draw_introduce_text += _(" 信任度50%以上")
        if self.character_data.trust < 50:
            text_draw_introduce_text += "(X)"
            judge = 0
        else:
            text_draw_introduce_text += "(√)"
        text_draw_introduce_text += _(" 反发刻印0")
        if self.character_data.ability[18] != 0:
            text_draw_introduce_text += "(X)"
            judge = 0
        else:
            text_draw_introduce_text += "(√)"
        text_draw_introduce_text += "\n"
        text_draw_introduce_text += _(" 分为爱情系与隶属系两条路线，只能任选其一，选择后另一路线消失，仅在新周目时可以重置\n")

        text_draw_introduce.text = text_draw_introduce_text
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
            love_judge = 1 if judge == 1 else 0
            line = draw.LineDraw("-", self.width)
            line.draw()
            info_draw_love = draw.NormalDraw()
            info_draw_love.width = 1
            text_draw_love_text = _("爱情路线前提：")

            # 检测爱情路线前提
            text_draw_love_text += _(" 苦痛刻印0")
            if self.character_data.ability[15] != 0:
                text_draw_love_text += "(X)"
                love_judge = 0
            else:
                text_draw_love_text += "(√)"
            text_draw_love_text += _(" 恐怖刻印0")
            if self.character_data.ability[17] != 0:
                text_draw_love_text += "(X)"
                love_judge = 0
            else:
                text_draw_love_text += "(√)"
            text_draw_love_text += _(" 亲密等级至少为2")
            if self.character_data.ability[32] < 2:
                text_draw_love_text += "(X)"
                love_judge = 0
            else:
                text_draw_love_text += "(√)"
            text_draw_love_text += "\n"

            # 输出最高级的提示信息
            if self.character_data.talent[204]:
                text_draw_love_text += _("\n已达到最高级-爱侣\n")
                info_draw_love.text = text_draw_love_text
                info_draw_love.draw()
            # 路线选择
            else:
                info_draw_love.text = text_draw_love_text
                info_draw_love.draw()
                if next_love_id == 0:
                    self.show_gain_need(201, love_judge)
                else:
                    self.show_gain_need(next_love_id, love_judge)

        # 隶属路线
        if next_obey_id or not next_love_id:
            obey_judge = 1 if judge == 1 else 0
            line = draw.LineDraw("-", self.width)
            line.draw()
            info_draw_obey = draw.NormalDraw()
            info_draw_obey.width = 1
            text_draw_obey_text = _("隶属路线前提：")

            # 检测隶属路线前提
            text_draw_obey_text += _(" 快乐刻印>=1")
            if self.character_data.ability[13] == 0:
                text_draw_obey_text += "(X)"
                obey_judge = 0
            else:
                text_draw_obey_text += "(√)"
            text_draw_obey_text += _(" 屈服刻印>=1")
            if self.character_data.ability[14] == 0:
                text_draw_obey_text += "(X)"
                obey_judge = 0
            else:
                text_draw_obey_text += "(√)"
            text_draw_obey_text += _(" 顺从等级至少为2")
            if self.character_data.ability[31] <= 1:
                text_draw_obey_text += "(X)"
                obey_judge = 0
            else:
                text_draw_obey_text += "(√)"
            text_draw_obey_text += "\n"

            # 输出最高级的提示信息
            if self.character_data.talent[214]:
                text_draw_obey_text += _("\n已达到最高级-奴隶\n")
                info_draw_obey.text = text_draw_obey_text
                info_draw_obey.draw()
            # 路线选择
            else:
                info_draw_obey.text = text_draw_obey_text
                info_draw_obey.draw()
                if next_obey_id == 0:
                    self.show_gain_need(211, obey_judge)
                else:
                    self.show_gain_need(next_obey_id, obey_judge)


    def show_gain_need(self, talent_id, judge):
        """具体显示需要什么"""

        need_all = game_config.config_talent_gain_data[talent_id]
        talent_name = game_config.config_talent[talent_id].name

        # 输出素质名
        now_draw = draw.NormalDraw()
        now_draw.text = _("下一级为：[{0}]\n").format(talent_name)
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
                button_text = _("  需要能力[{0}]至少为 {1}\n").format(abi_name, str(need_value))
                if self.character_data.ability[need_type_id] < need_value:
                    judge = 0
            elif need_type == "T":
                tal_name = game_config.config_talent[need_value].name
                button_text = _("  需要素质[{0}]\n").format(tal_name)
                if not self.character_data.talent[need_value]:
                    judge = 0
            elif need_type == "J":
                juel_name = game_config.config_juel[need_type_id].name
                button_text = _("  需要宝珠[{0}]至少为 {1}\n").format(juel_name, str(need_value))
                if self.character_data.juel[need_type_id] < need_value:
                    judge = 0
                # self.jule_dict[need_type_id] = need_value
            elif need_type == "E":
                experience_name = game_config.config_experience[need_type_id].name
                button_text = _("  需要经验[{0}]至少为 {1}\n").format(experience_name, str(need_value))
                if self.character_data.experience[need_type_id] < need_value:
                    judge = 0
            elif need_type == "F":
                button_text = _("  需要好感至少为 {0}\n").format(str(need_value))
                if self.character_data.favorability[0] < need_value:
                    judge = 0
            elif need_type == "X":
                button_text = _("  需要信赖至少为 {0}\n").format(str(need_value))
                if self.character_data.trust < need_value:
                    judge = 0
            now_draw = draw.NormalDraw()
            now_draw.text = button_text
            now_draw.draw()

        if talent_id in {201,211}:
            line_feed.draw()
            if judge:
                now_draw_succed = draw.NormalDraw()
                now_draw_succed.text = _("满足条件，确定选择此路线吗？\n")
                now_draw_succed.draw()

                yes_draw = draw.CenterButton(_("[确定]"), _("确定") + "_" + str(talent_id), self.width / 3, cmd_func=self.level_up, args = talent_id)
                yes_draw.draw()
                self.return_list.append(yes_draw.return_text)
                line_feed.draw()

            else:
                now_draw_failed = draw.NormalDraw()
                now_draw_failed.text = _("不满足条件，无法选择\n")
                now_draw_failed.draw()

        elif talent_id == 203:
            line_feed.draw()
            now_draw = draw.NormalDraw()
            now_draw.text = _("满足条件后需要准备【戒指】，然后进行【告白】，成功后即可获得\n")
            now_draw.draw()

        elif talent_id == 213:
            line_feed.draw()
            now_draw = draw.NormalDraw()
            now_draw.text = _("满足条件后需要准备【项圈】，然后进行【戴上项圈】，成功后即可获得\n")
            now_draw.draw()

        elif judge:
            now_draw_succed = draw.NormalDraw()
            now_draw_succed.text = _("\n满足条件，确定要现在获得该素质吗（也可以在过夜时自动获得）\n")
            now_draw_succed.draw()

            yes_draw = draw.CenterButton(_("[确定]"), _("确定") + "_" + str(talent_id), self.width / 3, cmd_func=self.level_up, args = talent_id)
            yes_draw.draw()
            self.return_list.append(yes_draw.return_text)
            line_feed.draw()

    def level_up(self, talent_id):
        now_draw_succed = draw.WaitDraw()
        now_draw_succed.text = _("选择成功\n")
        now_draw_succed.draw()
        handle_talent.gain_talent(self.character_id, 1, talent_id)

        # 等待1分钟以输出结果
        character_data: game_type.Character = cache.character_data[0]
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.duration = 1
        update.game_update_flow(1)

