from typing import List
from types import FunctionType
from Script.Core import get_text, flow_handle, game_type, cache_control, constant

from Script.UI.Moudle import draw, panel
from Script.UI.Panel import see_character_info_panel
from Script.Config import normal_config, game_config
from Script.Design import handle_talent, character_handle

import copy

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
        self.pl_extra_growth_count = 0
        """ 继承玩家属性上限成长 """
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
        self.show_panel_flag_list = [False, False, False, False, False, False]
        """ 面板显示列表 """
        self.all_fall_chara_list = []
        """ 所有陷落干员列表 """
        self.farewell_npc_id = 0
        """ 送别干员id """
        self.show_world_setting = False
        """ 显示世界设定面板 """


    def draw(self):
        """绘制面板"""
        while 1:
            title_text = _("周目点数结算")
            title_draw = draw.TitleLineDraw(title_text, self.width)
            title_draw.draw()
            pl_character_data = cache.character_data[0]
            self.round_point_all = 0
            self.round_point_cost = 0
            self.return_list = []
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
            self.all_fall_chara_list = []
            button_text = _("○全陷落干员")
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
                    self.all_fall_chara_list.append(chara_id)
                    now_character_data = cache.character_data[chara_id]
                    talent_name = game_config.config_talent[talent_id].name
                    point_add = talent_id % 10 # 取个位数字
                    point_add *= 2
                    chara_point_all += point_add
                    chara_count += 1
                    if self.show_npc_flag:
                        # 用空格对齐
                        draw_chara_name = now_character_data.name.rjust(6, "　")
                        now_chara_text = ("  {0}-{1}(+{2})").format(draw_chara_name, talent_name, point_add)
                        info_text += now_chara_text
                        # 每8个换行
                        if chara_count % 8 == 0:
                            info_text += "\n"
            if self.show_npc_flag:
                info_text += "\n"
            self.round_point_all += chara_point_all
            info_text += _("  陷落干员总数：{0}，总点数：{1}\n\n").format(chara_count, chara_point_all)
            info_draw.text = info_text
            info_draw.draw()

            # 收藏品
            info_text = _("○全收藏品")
            now_pan_count, now_socks_count = 0, 0
            for chara_cid in pl_character_data.pl_collection.npc_panties:
                now_pan_count += len(pl_character_data.pl_collection.npc_panties[chara_cid])
            for chara_cid in pl_character_data.pl_collection.npc_socks:
                now_socks_count += len(pl_character_data.pl_collection.npc_socks[chara_cid])
            collection_point = now_pan_count + now_socks_count
            self.round_point_all += collection_point
            info_text += _("全干员内裤共{0}条，全干员袜子共{1}双，总点数{2}\n\n").format(now_pan_count, now_socks_count, collection_point)
            info_draw.text = info_text
            info_draw.draw()

            # debug模式下补满
            if cache.debug_mode:
                self.round_point_all += 9999
                info_text = _("debug模式+9999\n\n").format(self.round_point_all)
                info_draw.text = info_text
                info_draw.draw()

            # 总点数
            info_text = _("总周目点数：{0}\n\n").format(self.round_point_all)
            info_draw.text = info_text
            info_draw.draw()

            # 玩家源石技艺
            button_text = _("[0]博士的源石技艺")
            if self.show_panel_flag_list[0]:
                button_text += "▼"
            else:
                button_text += "▶"
            button = draw.LeftButton(button_text, button_text, len(button_text) * 2, cmd_func=self.show_panel_change, args=(0,))
            self.return_list.append(button_text)
            button.draw()
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[0][self.pl_originium_arts_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = self.calculate_originium_arts_cost()
            self.round_point_cost += now_cost
            info_text = _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_originium_arts_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_0", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,0))
            self.return_list.append(add_button.return_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_0", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,0))
            self.return_list.append(reduce_button.return_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家源石技艺
            if self.show_panel_flag_list[0]:
                talent_draw = see_character_info_panel.PlayerAbilityText(0, self.width, 8)
                talent_draw.draw()
            line_feed_draw.draw()

            # 玩家能力与经验
            button_text = _("[1]博士的能力与经验")
            if self.show_panel_flag_list[1]:
                button_text += "▼"
            else:
                button_text += "▶"
            button = draw.LeftButton(button_text, button_text, len(button_text) * 2, cmd_func=self.show_panel_change, args=(1,))
            self.return_list.append(button_text)
            button.draw()
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[1][self.pl_abi_and_exp_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            self.round_point_cost += now_cost
            info_text = _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_abi_and_exp_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_1", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,1))
            self.return_list.append(add_button.return_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_1", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,1))
            self.return_list.append(reduce_button.return_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家能力与经验
            if self.show_panel_flag_list[1]:
                abi_draw = CharacterabiText(0, self.width, now_rate)
                experience_draw = CharacterExperienceText(0, self.width, 8, now_rate)
                abi_draw.draw()
                experience_draw.draw()
            line_feed_draw.draw()

            # 玩家属性上限成长
            info_text = _("[2]博士的属性上限成长")
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[2][self.pl_extra_growth_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = self.calculate_pl_extra_growth_count()
            self.round_point_cost += now_cost
            info_text += _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_extra_growth_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_2", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,2))
            self.return_list.append(add_button.return_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_2", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,2))
            self.return_list.append(reduce_button.return_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家属性上限成长
            hp_extra_grouth = 1000 + int((pl_character_data.hit_point_max - 1000) * now_rate / 100)
            mp_extra_grouth = 1000 + int((pl_character_data.mana_point_max - 1000) * now_rate / 100)
            santy_extra_grouth = 100 + int((pl_character_data.sanity_point_max - 100) * now_rate / 100)
            semen_extra_grouth = 100 + int((pl_character_data.semen_point_max - 100) * now_rate / 100)
            info_text = _("  属性上限成长：当前体力上限{0}(→{1})，气力上限{2}(→{3})，理智上限{4}(→{5})，精液上限{6}(→{7})\n\n").format(
                pl_character_data.hit_point_max, hp_extra_grouth, pl_character_data.mana_point_max, mp_extra_grouth,
                pl_character_data.sanity_point_max, santy_extra_grouth, pl_character_data.semen_point_max, semen_extra_grouth
            )
            info_draw.text = info_text
            info_draw.draw()

            # 玩家收藏品
            info_text = _("[3]博士的收藏品")
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[3][self.pl_collection_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            self.round_point_cost += now_cost
            info_text += _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.pl_collection_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_3", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,3))
            self.return_list.append(add_button.return_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_3", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,3))
            self.return_list.append(reduce_button.return_text)
            reduce_button.draw()
            line_feed_draw.draw()
            # 绘制玩家收藏品
            new_pan_count = int(now_pan_count * now_rate / 100)
            new_socks_count = int(now_socks_count * now_rate / 100)
            info_text = _("  收藏品统计：当前内裤{0}(→{1})条，袜子{2}(→{3})双\n\n").format(now_pan_count, new_pan_count, now_socks_count, new_socks_count)
            info_draw.text = info_text
            info_draw.draw()

            # 干员好感与信任
            info_text = _("已陷落干员将直接继承至新的周目，无需重新招募\n")
            info_text += _("耗费点数可以进一步继承这些干员一定比例的好感、信赖、能力、经验\n")
            info_text += _("\n[4]干员的好感与信任")
            info_draw.text = info_text
            info_draw.draw()
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[4][self.chara_fon_and_trust_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            self.round_point_cost += now_cost
            info_text = _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.chara_fon_and_trust_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_4", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,4))
            self.return_list.append(add_button.return_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_4", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,4))
            self.return_list.append(reduce_button.return_text)
            reduce_button.draw()
            line_feed_draw.draw()

            # 干员能力与经验
            info_text = _("\n[5]干员的能力与经验")
            info_draw.text = info_text
            info_draw.draw()
            # 继承选项
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[5][self.chara_abi_and_exp_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            now_cost = now_inherit_data.point_cost
            self.round_point_cost += now_cost
            info_text = _("\n   当前继承等级{0}，继承比例{1}%，点数消耗{2}\n  ").format(self.chara_abi_and_exp_count, now_rate, now_cost)
            info_draw.text = info_text
            info_draw.draw()
            # 提高和降低按钮
            add_button_text = _(" [提高] ")
            add_button = draw.CenterButton(add_button_text, add_button_text + "_5", len(add_button_text) * 2, cmd_func=self.value_change_buton, args=(1,5))
            self.return_list.append(add_button.return_text)
            add_button.draw()
            reduce_button_text = _(" [降低] ")
            reduce_button = draw.CenterButton(reduce_button_text, reduce_button_text + "_5", len(reduce_button_text) * 2, cmd_func=self.value_change_buton, args=(-1,5))
            self.return_list.append(reduce_button.return_text)
            reduce_button.draw()
            line_feed_draw.draw()

            # 输出总点数的花费与剩余
            info_text = _("\n总点数消耗：{0}，剩余：{1}\n").format(self.round_point_cost, self.round_point_all - self.round_point_cost)
            info_draw.text = info_text
            info_draw.draw()

            # 世界设定部分
            info_text = _("\n○世界设定（不消耗周目点数）")
            info_draw.text = info_text
            info_draw.draw()
            # 世界设定按钮
            button_text = _(" [更改世界设定] ")
            if self.show_world_setting:
                button_text = _(" [隐藏世界设定] ")
            button = draw.CenterButton(button_text, button_text, len(button_text) * 2, cmd_func=self.toggle_world_setting)
            self.return_list.append(button_text)
            button.draw()
            line_feed_draw.draw()
            
            # 显示世界设定面板
            world_setting_return_list = []
            if self.show_world_setting:
                from Script.UI.Flow import creator_character_flow
                world_setting_panel = creator_character_flow.World_Setting(self.width)
                world_setting_panel.draw()
                # 保存世界设定面板的返回列表，但不立即添加到主返回列表
                world_setting_return_list = world_setting_panel.return_list.copy()
                line_feed_draw.draw()

            # 选择送别干员
            info_text = _("\n○送别干员：")
            if self.farewell_npc_id:
                info_text += "{0}".format(cache.character_data[self.farewell_npc_id].name)
            else:
                info_text += _("未选择")
            info_text += "        "
            info_draw.text = info_text
            info_draw.draw()
            # 更改送别干员按钮
            button_text = _(" [更改送别干员] ")
            button = draw.CenterButton(button_text, button_text, len(button_text) * 2, cmd_func=self.farewell_npc_change)
            self.return_list.append(button_text)
            button.draw()
            line_feed_draw.draw()
            line_feed_draw.draw()

            line_feed_draw.draw()
            yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width)
            if self.round_point_all >= self.round_point_cost:
                yes_draw.draw()
                self.return_list.append(yes_draw.return_text)
                line_feed_draw.draw()
            
            # 将世界设定的返回列表添加到主返回列表
            self.return_list.extend(world_setting_return_list)
            
            yrn = flow_handle.askfor_all(self.return_list)
            
            # 只有点击主面板的确定按钮才会退出
            if yrn == yes_draw.return_text:
                self.start_new_round()
                cache.now_panel_id = constant.Panel.IN_SCENE
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

    def calculate_originium_arts_cost(self):
        """
        计算源石技艺消耗
        """
        if self.pl_originium_arts_count == 0:
            return 0
        else:
            all_cost = 0
            pl_character_data = cache.character_data[0]
            # 初级源石技艺
            for i in [304, 307, 310, 316, 331]:
                if pl_character_data.talent[i]:
                    all_cost += 10
            # 中级源石技艺
            for i in [305, 308, 311, 317, 332]:
                if pl_character_data.talent[i]:
                    all_cost += 30
            # 高级源石技艺
            for i in [306, 309, 312, 318, 333]:
                if pl_character_data.talent[i]:
                    all_cost += 60
            # 特级源石技艺
            for i in [334]:
                if pl_character_data.talent[i]:
                    all_cost += 120
            return all_cost

    def calculate_pl_extra_growth_count(self):
        """
        计算玩家属性上限成长消耗\n
        每50点hp、mp消耗1点\n
        每1点sanity、semen消耗1点\n
        """
        if self.pl_extra_growth_count == 0:
            return 0
        else:
            all_cost = 0
            pl_character_data = cache.character_data[0]
            now_inherit_data_cid = game_config.config_new_round_inherit_type_data[2][self.pl_extra_growth_count]
            now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
            now_rate = now_inherit_data.inherit_rate
            # 体力上限成长
            hp_extra_grouth = (pl_character_data.hit_point_max - 1000) * now_rate / 100
            all_cost += int(hp_extra_grouth / 50)
            # 气力上限成长
            mp_extra_grouth = (pl_character_data.mana_point_max - 1000) * now_rate / 100
            all_cost += int(mp_extra_grouth / 50)
            # 理智上限成长
            san_extra_grouth = (pl_character_data.sanity_point_max - 100) * now_rate / 100
            all_cost += int(san_extra_grouth)
            # 精液上限成长
            semen_extra_grouth = (pl_character_data.semen_point_max - 100) * now_rate / 100
            all_cost += int(semen_extra_grouth)
            return all_cost

    def value_change_buton(self, value: int, type: int):
        """
        提高或降低继承等级
        Keyword arguments:
        value -- 提高或降低的数值
        type -- 继承类型
        """
        if type == 0:
            self.pl_originium_arts_count += value
            if self.pl_originium_arts_count < 0:
                self.pl_originium_arts_count = 0
            elif self.pl_originium_arts_count > len(game_config.config_new_round_inherit_type_data[0]) - 1:
                self.pl_originium_arts_count = len(game_config.config_new_round_inherit_type_data[0]) - 1
        elif type == 1:
            self.pl_abi_and_exp_count += value
            if self.pl_abi_and_exp_count < 0:
                self.pl_abi_and_exp_count = 0
            elif self.pl_abi_and_exp_count > len(game_config.config_new_round_inherit_type_data[1]) - 1:
                self.pl_abi_and_exp_count = len(game_config.config_new_round_inherit_type_data[1]) - 1
        elif type == 2:
            self.pl_extra_growth_count += value
            if self.pl_extra_growth_count < 0:
                self.pl_extra_growth_count = 0
            elif self.pl_extra_growth_count > len(game_config.config_new_round_inherit_type_data[2]) - 1:
                self.pl_extra_growth_count = len(game_config.config_new_round_inherit_type_data[2]) - 1
        elif type == 3:
            self.pl_collection_count += value
            if self.pl_collection_count < 0:
                self.pl_collection_count = 0
            elif self.pl_collection_count > len(game_config.config_new_round_inherit_type_data[3]) - 1:
                self.pl_collection_count = len(game_config.config_new_round_inherit_type_data[3]) - 1
        elif type == 4:
            self.chara_fon_and_trust_count += value
            if self.chara_fon_and_trust_count < 0:
                self.chara_fon_and_trust_count = 0
            elif self.chara_fon_and_trust_count > len(game_config.config_new_round_inherit_type_data[4]) - 1:
                self.chara_fon_and_trust_count = len(game_config.config_new_round_inherit_type_data[4]) - 1
        elif type == 5:
            self.chara_abi_and_exp_count += value
            if self.chara_abi_and_exp_count < 0:
                self.chara_abi_and_exp_count = 0
            elif self.chara_abi_and_exp_count > len(game_config.config_new_round_inherit_type_data[5]) - 1:
                self.chara_abi_and_exp_count = len(game_config.config_new_round_inherit_type_data[5]) - 1

    def farewell_npc_change(self):
        """
        更改送别干员
        """
        while 1:
            title_text = _("送别干员")
            title_draw = draw.TitleLineDraw(title_text, self.width)
            title_draw.draw()
            return_list = []
            info_text = ""
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_text += _("选择送别干员\n")
            info_draw.text = info_text
            info_draw.draw()
            chara_count = 0
            for chara_id in self.all_fall_chara_list:
                now_character_data = cache.character_data[chara_id]
                button_text = f"[{now_character_data.adv}]{now_character_data.name}"
                button_len = max(len(button_text), 24)
                button = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.farewell_npc_change_confirm, args=(chara_id,))
                if chara_id == self.farewell_npc_id:
                    button = draw.LeftButton(button_text, button_text, button_len, normal_style = "gold_enrod", cmd_func=self.farewell_npc_change_confirm, args=(chara_id,))
                return_list.append(button_text)
                button.draw()
                chara_count += 1
                if chara_count % 8 == 0:
                    line_feed_draw.draw()
            line_feed_draw.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def farewell_npc_change_confirm(self, chara_id: int):
        """
        确认送别干员
        Keyword arguments:
        chara_id -- 干员id
        """
        self.farewell_npc_id = chara_id

    def toggle_world_setting(self):
        """
        切换世界设定面板的显示状态
        """
        self.show_world_setting = not self.show_world_setting

    def start_new_round(self):
        """
        开始新的周目
        """
        from Script.Design import talk, second_behavior
        from Script.UI.Panel import achievement_panel

        # 输出送别干员的送别口上
        if self.farewell_npc_id:
            now_character_data = cache.character_data[self.farewell_npc_id]
            second_behavior.character_get_second_behavior(self.farewell_npc_id, "new_round_farewell")
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            line_feed_draw.draw()
            line_feed_draw.draw()
            talk.must_show_talk_check(self.farewell_npc_id)
            line_feed_draw.draw()
            line_feed_draw.draw()
            line_feed_draw.draw()


        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()

        # 继承玩家数据
        self.inherit_player_data()
        # 继承干员数据
        self.inherit_npc_data()
        # 重置游戏数据
        self.reset_game_data()

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw_text = "\n\n\n\n\n\n\n\n\n"
        info_draw.text = info_draw_text
        info_draw.draw()

        while 1:

            return_list = []
            button_draw = draw.CenterButton(
                _("[醒来]"),
                _("醒来\n"),
                self.width
            )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                achievement_panel.achievement_flow(_("周目"))
                break

    def build_new_character_data(self, character_id: int):
        """
        构建新的角色数据
        Keyword arguments:
        character_id -- 角色id
        """
        character_handle.init_character(character_id, cache.npc_tem_data[character_id])

    def inherit_player_data(self):
        """
        继承玩家数据
        """
        from Script.Design import character
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw_text = "\n\n"
        info_draw_text += _("开始继承玩家数据\n")

        # 记录旧的玩家数据
        old_pl_character_data = copy.deepcopy(cache.character_data[0])
        # 构建新的玩家数据
        cache.character_data[0] = game_type.Character()
        character.init_attr(0)
        new_pl_character_data = cache.character_data[0]
        new_pl_character_data.name = old_pl_character_data.name

        # 玩家能力与经验
        now_inherit_data_cid = game_config.config_new_round_inherit_type_data[1][self.pl_abi_and_exp_count]
        now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
        now_rate = now_inherit_data.inherit_rate
        for i in old_pl_character_data.ability:
            new_pl_character_data.ability[i] = int(old_pl_character_data.ability[i] * now_rate / 100)
        for i in old_pl_character_data.experience:
            new_pl_character_data.experience[i] = int(old_pl_character_data.experience[i] * now_rate / 100)
        info_draw_text += _("玩家能力与经验继承完毕\n")

        # 玩家源石技艺
        if self.pl_originium_arts_count > 0:
            for i in range(301, 350):
                if i in old_pl_character_data.talent and old_pl_character_data.talent[i]:
                    new_pl_character_data.talent[i] = old_pl_character_data.talent[i]
        info_draw_text += _("玩家源石技艺继承完毕\n")

        # 玩家属性上限成长
        now_inherit_data_cid = game_config.config_new_round_inherit_type_data[2][self.pl_extra_growth_count]
        now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
        now_rate = now_inherit_data.inherit_rate
        # 体力上限成长
        hp_extra_grouth = (old_pl_character_data.hit_point_max - 1000) * now_rate / 100
        new_pl_character_data.hit_point_max = int(1000 + hp_extra_grouth)
        # 气力上限成长
        mp_extra_grouth = (old_pl_character_data.mana_point_max - 1000) * now_rate / 100
        new_pl_character_data.mana_point_max = int(1000 + mp_extra_grouth)
        # 理智上限成长
        san_extra_grouth = (old_pl_character_data.sanity_point_max - 100) * now_rate / 100
        new_pl_character_data.sanity_point_max = int(100 + san_extra_grouth)
        # 精液上限成长
        semen_extra_grouth = (old_pl_character_data.semen_point_max - 100) * now_rate / 100
        new_pl_character_data.semen_point_max = int(100 + semen_extra_grouth)
        info_draw_text += _("玩家属性上限成长继承完毕\n")

        # 玩家收藏品
        now_inherit_data_cid = game_config.config_new_round_inherit_type_data[3][self.pl_collection_count]
        now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
        now_rate = now_inherit_data.inherit_rate
        # 首先计算旧的收藏品数量和新的收藏品数量
        old_pan_count, old_socks_count = 0, 0
        for chara_cid in old_pl_character_data.pl_collection.npc_panties:
            old_pan_count += len(old_pl_character_data.pl_collection.npc_panties[chara_cid])
        for chara_cid in old_pl_character_data.pl_collection.npc_socks:
            old_socks_count += len(old_pl_character_data.pl_collection.npc_socks[chara_cid])
        new_pan_count = int(old_pan_count * now_rate / 100)
        new_socks_count = int(old_socks_count * now_rate / 100)

        # 在当前计数收藏品不超过新的数量的情况下，进行收藏品继承
        now_pan_count, now_socks_count = 0, 0
        for chara_cid in old_pl_character_data.pl_collection.npc_panties:
            pan_count = len(old_pl_character_data.pl_collection.npc_panties[chara_cid])
            now_pan_count += pan_count
            new_pl_character_data.pl_collection.npc_panties[chara_cid] = old_pl_character_data.pl_collection.npc_panties[chara_cid]
            if now_pan_count > new_pan_count:
                break
        for chara_cid in old_pl_character_data.pl_collection.npc_socks:
            socks_count = len(old_pl_character_data.pl_collection.npc_socks[chara_cid])
            now_socks_count += socks_count
            new_pl_character_data.pl_collection.npc_socks[chara_cid] = old_pl_character_data.pl_collection.npc_socks[chara_cid]
            if now_socks_count > new_socks_count:
                break
        info_draw_text += _("玩家收藏品继承完毕\n")
        info_draw.text = info_draw_text
        info_draw.draw()

    def inherit_npc_data(self):
        """
        继承干员数据
        """
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw_text = "\n"
        info_draw_text += _("开始继承干员数据\n")

        # 记录旧的干员数据
        old_npc_data = copy.deepcopy(cache.character_data)
        cache.npc_id_got = set()

        id_list = iter([i + 1 for i in range(len(cache.npc_tem_data))])
        npc_data_iter = iter(cache.npc_tem_data)
        for now_id, now_npc_data in zip(id_list, npc_data_iter):

            # 仅继承陷落干员
            if now_id not in self.all_fall_chara_list:
                character_handle.init_character(now_id, now_npc_data, collect_reset=False)
            else:
                character_handle.init_character(now_id, now_npc_data, collect_reset=False)
                new_npc_data = cache.character_data[now_id]
                cache.npc_id_got.add(now_id)

                # 干员好感与信任
                now_inherit_data_cid = game_config.config_new_round_inherit_type_data[4][self.chara_fon_and_trust_count]
                now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
                now_rate = now_inherit_data.inherit_rate
                new_npc_data.trust = int(old_npc_data[now_id].trust * now_rate / 100)
                new_npc_data.favorability[0] = int(old_npc_data[now_id].favorability[0] * now_rate / 100)

                # 干员能力与经验
                now_inherit_data_cid = game_config.config_new_round_inherit_type_data[5][self.chara_abi_and_exp_count]
                now_inherit_data = game_config.config_new_round_inherit[now_inherit_data_cid]
                now_rate = now_inherit_data.inherit_rate
                for i in old_npc_data[now_id].ability:
                    new_npc_data.ability[i] = int(old_npc_data[now_id].ability[i] * now_rate / 100)
                for i in old_npc_data[now_id].experience:
                    new_npc_data.experience[i] = int(old_npc_data[now_id].experience[i] * now_rate / 100)
        info_draw_text += _("干员好感与信任继承完毕\n")
        info_draw_text += _("干员能力与经验继承完毕\n")
        info_draw.text = info_draw_text
        info_draw.draw()


    def reset_game_data(self):
        """
        重置游戏数据
        """
        global cache
        from Script.Design import attr_calculation, basement, game_time
        from Script.UI.Flow import creator_character_flow
        from Script.Config import map_config
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw_text = "\n"
        info_draw_text += _("开始重置游戏数据\n")

        # 要保留的数据
        old_cache = copy.deepcopy(cache_control.cache)
        new_game_round = old_cache.game_round + 1
        new_character_data = old_cache.character_data
        new_npc_id_got = old_cache.npc_id_got
        new_world_setting = old_cache.world_setting
        new_system_setting = old_cache.all_system_setting
        new_achievement = old_cache.achievement

        # 开始重置
        cache_control.cache = cache
        map_config.init_map_data()
        game_time.init_time()
        cache.rhodes_island = basement.get_base_zero()
        cache.all_system_setting = attr_calculation.get_system_setting_zero()
        cache.rhodes_island.physical_examination_setting = attr_calculation.get_physical_exam_setting_zero()
        info_draw_text += _("游戏数据重置完毕\n")

        # 覆盖要保留的数据
        creator_character_flow.first_bonus_and_setting_updata()
        cache.world_setting = new_world_setting
        cache.all_system_setting = new_system_setting
        cache.achievement = new_achievement
        cache.game_round = new_game_round
        cache.character_data = new_character_data
        cache.npc_id_got = new_npc_id_got
        creator_character_flow.game_start()

        # 根据继承的角色，将有人住的宿舍设为开放
        for now_id in new_npc_id_got:
            # 获取地点数据
            now_character_data = cache.character_data[now_id]
            now_dormitory = now_character_data.dormitory
            now_scene_data = cache.scene_data[now_dormitory]
            # 如果该地点在设施开放列表中
            if now_scene_data.scene_name in game_config.config_facility_open_name_set:
                open_cid = game_config.config_facility_open_name_to_cid[now_scene_data.scene_name]
                # 如果未开放，则开放
                if cache.rhodes_island.facility_open[open_cid] == False:
                    cache.rhodes_island.facility_open[open_cid] = True

        info_draw_text += _("继承数据覆盖完毕\n")
        info_draw.text = info_draw_text
        info_draw.draw()

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
