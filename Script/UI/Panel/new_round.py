from typing import List
from types import FunctionType
from Script.Core import get_text, flow_handle, game_type, cache_control

from Script.UI.Moudle import draw, panel
from Script.UI.Panel import see_character_info_panel
from Script.Config import normal_config, game_config
from Script.Design import handle_talent

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

class New_Round_Handle:
    """
    角色创建页面对象
    Keyword arguments:
    """

    def __init__(self):
        """初始化绘制对象"""
        self.width = normal_config.config_normal.text_width
        """ 屏幕宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.pl_abi_and_exp_count = 0
        """ 继承玩家能力和经验 """
        self.pl_originium_arts_count = 0
        """ 继承玩家源石技艺 """
        self.pl_collection_count = 0
        """ 继承玩家收藏品 """
        self.chara_fon_and_trust_count = 0
        """ 继承干员好感和信任 """
        self.chara_abi_and_exp_count = 0
        """ 继承干员能力和经验 """
        self.round_point_all = 0
        """ 总周目点数 """
        self.round_point_cost = 0
        """ 周目点数消耗 """
        self.show_npc_flag = False
        """ 干员显示 """
        self.show_panel_flag_list = [False, False, False, False, False]
        """ 面板显示列表 """


    def draw(self):
        """绘制面板"""
        while 1:
            title_text = _("周目点数结算")
            title_draw = draw.TitleLineDraw(title_text, self.width)
            title_draw.draw()
            pl_character_data = cache.character_data[0]
            self.round_point_all = 0
            info_text = "\n"
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            # 当前周目数
            now_round = cache.game_round
            point_add = now_round * 20
            self.round_point_all += point_add
            info_text += _("当前周目数：{0}(+{1})\n\n").format(now_round, point_add)
            info_draw.text = info_text
            info_draw.draw()
            # 统计所有干员中已经陷落的
            all_fall_chara_list = []
            button_text = _(" 全陷落干员")
            if self.show_npc_flag:
                button_text += "▼"
            else:
                button_text += "▶"
            button = draw.LeftButton(button_text, button_text, len(button_text) * 2, cmd_func=self.show_npc_change)
            self.return_list.append(button_text)
            button.draw()
            info_text = "\n"
            chara_count, chara_point_all = 0, 0
            # 遍历所有获得的干员
            for chara_id in cache.npc_id_got:
                talent_id = handle_talent.have_fall_talent(chara_id)
                # 如果已经陷落
                if talent_id:
                    all_fall_chara_list.append(chara_id)
                    now_character_data = cache.character_data[chara_id]
                    talent_name = game_config.config_talent[talent_id].name
                    point_add = talent_id % 10 # 取个位数字
                    chara_point_all += point_add
                    chara_count += 1
                    if self.show_npc_flag:
                        info_text += ("  {0}-{1}(+{2})").format(now_character_data.name, talent_name, point_add)
                        if chara_count % 8 == 0:
                            info_text += "\n"
            if self.show_npc_flag:
                info_text += "\n"
            self.round_point_all += chara_point_all
            info_text += _("  陷落干员总数：{0}，总点数：{1}\n\n").format(chara_count, chara_point_all)
            info_draw.text = info_text
            info_draw.draw()

            # 收藏品
            info_text = _(" 收藏品统计：")
            now_pan_count, now_socks_count = 0, 0
            for chara_cid in pl_character_data.pl_collection.npc_panties:
                now_pan_count += len(pl_character_data.pl_collection.npc_panties[chara_cid])
            for chara_cid in pl_character_data.pl_collection.npc_socks:
                now_socks_count += len(pl_character_data.pl_collection.npc_socks[chara_cid])
            collection_point = int(now_pan_count / 10 + now_socks_count / 10)
            self.round_point_all += collection_point
            info_text += _("全干员内裤共{0}条，全干员袜子共{1}双，总点数{2}\n\n").format(now_pan_count, now_socks_count, collection_point)
            info_draw.text = info_text
            info_draw.draw()

            # 总点数
            info_text = _("总周目点数：{0}\n\n").format(self.round_point_all)
            info_draw.text = info_text
            info_draw.draw()

            # 玩家能力与经验
            button_text = _("[0]博士的能力与经验")
            if self.show_panel_flag_list[0]:
                button_text += "▼"
            else:
                button_text += "▶"
            button = draw.LeftButton(button_text, button_text, len(button_text) * 2, cmd_func=self.show_panel_change, args=(0,))
            self.return_list.append(button_text)
            button.draw()
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[1][self.pl_abi_and_exp_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            info_text = _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_abi_and_exp_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_0", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,0))
            self.return_list.append(add_button_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_0", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,0))
            self.return_list.append(reduce_button_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家能力与经验
            if self.show_panel_flag_list[0]:
                abi_draw = CharacterabiText(0, self.width, now_rate)
                experience_draw = CharacterExperienceText(0, self.width, 8, now_rate)
                abi_draw.draw()
                experience_draw.draw()
            line_feed_draw.draw()

            # 玩家源石技艺
            button_text = _("[1]博士的源石技艺")
            if self.show_panel_flag_list[1]:
                button_text += "▼"
            else:
                button_text += "▶"
            button = draw.LeftButton(button_text, button_text, len(button_text) * 2, cmd_func=self.show_panel_change, args=(1,))
            self.return_list.append(button_text)
            button.draw()
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[0][self.pl_originium_arts_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            info_text += _("   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_originium_arts_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_1", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,1))
            self.return_list.append(add_button_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_1", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,1))
            self.return_list.append(reduce_button_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家源石技艺
            if self.show_panel_flag_list[1]:
                talent_draw = see_character_info_panel.PlayerAbilityText(0, self.width, 8)
                talent_draw.draw()
            line_feed_draw.draw()

            # 玩家收藏品
            info_text = _("[2]博士的收藏品")
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[2][self.pl_collection_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            info_text += _("   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_collection_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_2", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,2))
            self.return_list.append(add_button_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_2", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,2))
            self.return_list.append(reduce_button_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家收藏品
            new_pan_count = int(now_pan_count * now_rate / 100)
            new_socks_count = int(now_socks_count * now_rate / 100)
            info_text = _("  收藏品统计：当前内裤{0}(→{1})条，袜子{2}(→{3})双\n\n").format(now_pan_count, new_pan_count, now_socks_count, new_socks_count)
            info_draw.text = info_text
            info_draw.draw()

            line_feed_draw.draw()
            yes_draw = draw.CenterButton(_("[是]"), _("是"), self.width)
            yes_draw.draw()
            self.return_list.append(yes_draw.return_text)
            line_feed_draw.draw()
            yrn = flow_handle.askfor_all(self.return_list)
            if yrn == yes_draw.return_text:
                break

    def show_npc_change(self):
        """
        显示或隐藏陷落干员
        """
        self.show_npc_flag = not self.show_npc_flag

    def show_panel_change(self, type: int):
        """
        显示或隐藏面板
        Keyword arguments:
        type -- 面板类型
        """
        self.show_panel_flag_list[type] = not self.show_panel_flag_list[type]

    def value_change_buton(self, value: int, type: int):
        """
        提高或降低继承等级
        Keyword arguments:
        value -- 提高或降低的数值
        type -- 继承类型
        """
        if type == 0:
            self.pl_abi_and_exp_count += value
            if self.pl_abi_and_exp_count < 0:
                self.pl_abi_and_exp_count = 0
            elif self.pl_abi_and_exp_count > 3:
                self.pl_abi_and_exp_count = 3
        elif type == 1:
            self.pl_originium_arts_count += value
            if self.pl_originium_arts_count < 0:
                self.pl_originium_arts_count = 0
            elif self.pl_originium_arts_count > 1:
                self.pl_originium_arts_count = 1
        elif type == 2:
            self.pl_collection_count += value
            if self.pl_collection_count < 0:
                self.pl_collection_count = 0
            elif self.pl_collection_count > 3:
                self.pl_collection_count = 3
        elif type == 3:
            self.chara_fon_and_trust_count += value
            if self.chara_fon_and_trust_count < 0:
                self.chara_fon_and_trust_count = 0
            elif self.chara_fon_and_trust_count > 3:
                self.chara_fon_and_trust_count = 3
        elif type == 4:
            self.chara_abi_and_exp_count += value
            if self.chara_abi_and_exp_count < 0:
                self.chara_abi_and_exp_count = 0
            elif self.chara_abi_and_exp_count > 3:
                self.chara_abi_and_exp_count = 3


class CharacterabiText:
    """
    角色能力面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int, rate: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.rate = rate
        """ 继承比例 """
        self.type = type
        """ 当前绘制类型 """
        # self.column = column
        # """ 每行状态最大个数 """
        character_data = cache.character_data[self.character_id]
        """ 角色数据 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制对象列表 """
        self.title_list: List[draw.NormalDraw] = []
        """ 绘制标题列表 """
        ability_list = game_config.config_ability_type_data
        title_text = _("能力")
        type_line = draw.LittleTitleLineDraw(title_text, self.width, ":")
        self.draw_list.append(type_line)
        # 进入能力大类#
        for anility_type in ability_list:
            # if anility_type == type:
            type_set = ability_list[anility_type]
            # 去掉玩家的若干能力#
            if self.character_id == 0:
                if anility_type in {0, 1, 2, 6}:
                    continue
            for ability_id in type_set:
                # 去掉与性别不符的能力#
                if character_data.sex == 0:
                    if ability_id in {73, 74, 75}:
                        continue
                elif character_data.sex == 1:
                    if ability_id == 3:
                        continue
                now_draw = draw.NormalDraw()
                now_draw_value = draw.NormalDraw()
                now_draw.text = game_config.config_ability[ability_id].name
                # 这个_1是为了补空格让格式对齐#
                now_draw_1 = draw.NormalDraw()
                now_draw_1.text = " "
                now_draw_1.width = 1
                now_draw.width = self.width / len(type_set)
                now_exp = character_data.ability[ability_id]
                # 仅在这里与原版不同，增加继承比例
                if now_exp > 0:
                    inherit_exp = int(now_exp * self.rate / 100)
                    now_draw_value.text = f"{now_exp}(→{inherit_exp})"
                else:
                    now_draw_value.text = str(now_exp)
                # ↑
                level_draw = draw.ExpLevelDraw(now_exp)
                new_draw = draw.LeftMergeDraw(self.width / 10)
                # 技能类能力里在八个前补个换行
                if ability_id == 48:
                    new_draw_n = draw.NormalDraw()
                    new_draw_n.text = "\n"
                    new_draw_n.width = 1
                    new_draw.draw_list.append(new_draw_n)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(now_draw)
                new_draw.draw_list.append(now_draw_1)
                # 根据不同的类型补不同数量的空格#
                if anility_type != 2 and anility_type != 4 and anility_type != 6:
                    new_draw.draw_list.append(now_draw_1)
                    new_draw.draw_list.append(now_draw_1)
                    if anility_type == 3 or anility_type == 5:
                        new_draw.draw_list.append(now_draw_1)
                        new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(level_draw)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(now_draw_value)
                self.draw_list.append(new_draw)
            # 只有不是最后一个类型就补个换行#
            if anility_type != 6:
                new_draw_n = draw.NormalDraw()
                new_draw_n.text = "\n"
                new_draw_n.width = 1
                self.draw_list.append(new_draw_n)

    def draw(self):
        """绘制对象"""
        line_feed_draw.draw()
        for value in self.draw_list:
            value.draw()


class CharacterExperienceText:
    """
    显示角色经验面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, rate: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.column = column
        """ 每行状态最大个数 """
        self.rate = rate
        """ 继承比例 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        character_data = cache.character_data[character_id]
        type_data = _("经验")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        experience_text_list = []
        for experience_id in game_config.config_experience:
            if character_data.sex == 0:
                if experience_id in {2, 4, 7, 12, 14, 17, 20, 22, 26, 51, 54, 55, 58, 72, 74, 77, 86, 100, 101, 102, 103, 104, 105, 106}:
                    continue
            elif character_data.sex == 1:
                if experience_id == {3, 13, 21, 73}:
                    continue
            experience_text = game_config.config_experience[experience_id].name
            experience_value = 0
            if experience_id in character_data.experience:
                experience_value = character_data.experience[experience_id]
                # 仅在这里与原版不同，增加继承比例
                inherit_exp = int(experience_value * self.rate / 100)
                now_text = f" {experience_text}:{experience_value}(→{inherit_exp})"
                # ↑
            if experience_value > 0:
                experience_text_list.append(now_text)
        now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(experience_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        # title_draw = draw.TitleLineDraw(_("人物状态"), self.width)
        # title_draw.draw()
        line_feed_draw.draw()
        count = 0
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                    count += 1
                line_feed_draw.draw()
            else:
                label.draw()
        if count <= 8:
            line_feed_draw.draw()
            if count == 0:
                line_feed_draw.draw()
