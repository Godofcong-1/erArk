from typing import Tuple, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.Design import  attr_calculation

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

def update_nation_data():
    """
    重置矿石病感染率数据
    """
    need_update = True

    # 首先检查是否全势力0声望
    for nation_id in game_config.config_nation:
        if cache.country.nation_reputation[nation_id] != 0:
            need_update = False
            break

    # 如果全势力0声望，则检查是否有全势力0感染率
    if need_update:
        for country_id in game_config.config_birthplace:
            if cache.country.country_infection_rate[country_id] != 0:
                need_update = False
                break

    # 如果全势力0声望0感染率，则更新
    if need_update:
        for country_id in game_config.config_birthplace:
            cache.country.country_infection_rate[country_id] = game_config.config_birthplace[country_id].infect_rate


class Nation_Diplomacy_Panel:
    """
    用于显示势力外交界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("国家及附属势力")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.show_draw_width = 7
        """ 收起显示按钮的宽度 """

    def draw(self):
        """绘制对象"""

        title_text = _("势力外交")
        commission_type_list = [_("国家及附属势力"), _("其他势力")]

        # 更新势力声望数据
        cache.country = attr_calculation.get_country_reset(cache.country)
        # 检查是否有全势力0声望0感染率的，如果有则重置矿石病感染率数据
        update_nation_data()

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制面板类型切换
            for commission_type in commission_type_list:
                if commission_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{commission_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(commission_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{commission_type}]",
                        f"\n{commission_type}",
                        self.width / len(commission_type_list),
                        cmd_func=self.change_panel,
                        args=(commission_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 设施信息
            facility_info_text = ""
            facility_info_text += _("○与势力维持良好的关系有利于在对应地区的行动，包括外勤委托、商品贸易、技术交流、源石病治疗等\n")

            facility_info_draw = draw.NormalDraw()
            facility_info_draw.text = facility_info_text
            facility_info_draw.width = self.width
            facility_info_draw.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 绘制提示信息
            # info_text_list = [_("势力名称"), _("领导人"), _("势力声望"), _("源石病治愈率(未实装)")]
            info_text_list = [_("势力名称"), _("势力声望"), _("源石病治愈率(未实装)"), _("负责外交官")]
            for info_text in info_text_list:
                info_draw = draw.CenterDraw()
                info_draw.text = info_text
                info_draw.width = self.width / len(info_text_list)
                info_draw.draw()
            line_feed.draw()
            line = draw.LineDraw("~", self.width)
            line.draw()

            # 获取势力列表
            now_lacation_nation_list = []
            all_nation_list = []
            for cid in game_config.config_nation:
                nation_data = game_config.config_nation[cid]
                # 跳过罗德岛自己的势力
                if nation_data.country == 0:
                    continue
                # 跳过彩虹小队
                if cid == 502:
                    continue
                # 去掉非当前面板的势力
                if self.now_panel == _("国家及附属势力") and nation_data.country == -1:
                    continue
                if self.now_panel == _("其他势力") and nation_data.country != -1:
                    continue
                # 去掉非国家的附属势力
                if self.now_panel == _("国家及附属势力") and cid not in game_config.config_nation_data_of_country_subordinate:
                    continue
                # 获取当前位置的势力列表
                if self.now_panel == _("国家及附属势力") and nation_data.country == cache.rhodes_island.current_location[0]:
                    now_lacation_nation_list.append(cid)
                all_nation_list.append(cid)

            # 绘制势力信息
            for nation_id in all_nation_list:
                nation_data = game_config.config_nation[nation_id]
                cache.rhodes_island.diplomat_of_country.setdefault(nation_data.country, [0, 0])

                # 势力按钮绘制
                nation_name = nation_data.name
                # 声望
                now_nation_reputation = cache.country.nation_reputation[nation_id]
                tem, now_nation_reputation_level = attr_calculation.get_reputation_level(now_nation_reputation)
                now_nation_reputation_str = f"{now_nation_reputation}({now_nation_reputation_level})"
                # 治愈率
                if nation_data.country == -1:
                    now_country_treatment_progress = _("无")
                else:
                    now_country_treatment_progress = str(cache.country.country_infection_rate[nation_data.country])
                # 外交官
                now_diplomat_chara_id = cache.rhodes_island.diplomat_of_country[nation_data.country][0]
                if now_diplomat_chara_id != 0:
                    now_diplomat_chara_data = cache.character_data[now_diplomat_chara_id]
                    now_diplomat_name = now_diplomat_chara_data.name
                else:
                    now_diplomat_name = _("无")
                # 外交方针
                text_width = int(self.width / (len(info_text_list)))
                str_text_width = int(text_width / 2)
                nation_text = f"{nation_name.center(str_text_width,'　')}{now_nation_reputation_str.center(text_width,' ')}{now_country_treatment_progress.center(text_width,' ')}{now_diplomat_name.center(str_text_width,'　')}"

                # 可以进行的，绘制为按钮
                draw_style = "standard"
                if nation_id in now_lacation_nation_list:
                    draw_style = "gold_enrod"
                nation_draw = draw.LeftButton(
                    nation_text,
                    "\n" + nation_name,
                    self.width,
                    normal_style = draw_style,
                    cmd_func = self.nation_info,
                    args = (nation_id,),
                )
                nation_draw.draw()
                return_list.append(nation_draw.return_text)
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, building_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        building_type -- 要切换的面板类型
        """

        self.now_panel = building_type

    def nation_info(self, nation_id: int):
        """
        显示势力详细信息
        Keyword arguments:
        nation_id -- 势力编号
        """

        # 势力信息
        nation_data = game_config.config_nation[nation_id]
        nation_name = nation_data.name
        nation_leader = nation_data.leader
        nation_introduction = nation_data.introduction
        nation_reputation = cache.country.nation_reputation[nation_id]
        nation_infected_rate = cache.country.country_infection_rate[nation_data.country]
        # 势力特产
        nation_specialty_list = game_config.config_resouce_data_of_nation.get(nation_data.country, [])
        nation_specialty_str = ""
        for rid in nation_specialty_list:
            nation_specialty_str += game_config.config_resouce[rid].name + " "
        # 附属势力
        nation_subordinate_list = game_config.config_nation_data_of_country_subordinate.get(nation_id, [])
        nation_subordinate_str = ""
        for cid in nation_subordinate_list:
            nation_subordinate_str += game_config.config_nation[cid].name + " "
        if "\\n" in nation_introduction:
            nation_introduction = nation_introduction.replace("\\n", "\n      ")

        # 初始化负责外交官数据
        if nation_data.country not in cache.rhodes_island.diplomat_of_country:
            cache.rhodes_island.diplomat_of_country[nation_data.country][0] = 0

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制势力信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n势力名称：{0}").format(nation_name)
            # info_draw.text += _("\n领导人：{0}").format(nation_leader)
            # info_draw.text += _("\n势力简介：{0}").format(nation_introduction)
            info_draw.text += _("\n势力声望：{0}").format(nation_reputation)
            info_draw.text += _("\n源石病感染率：{0}").format(nation_infected_rate)
            info_draw.text += _("\n势力特产：{0}").format(nation_specialty_str)
            info_draw.text += _("\n附属势力：{0}").format(nation_subordinate_str)
            info_draw.width = self.width
            info_draw.draw()
            line_feed.draw()
            line_feed.draw()

            # 当前负责外交官
            info_text = _("○负责地区势力的外交官会长期停留在对应区域，只有在罗德岛本身抵达同一区域后才会回到岛上办公\n")
            info_text += _("当前势力的负责外交官为：")
            now_diplomat_chara_id = cache.rhodes_island.diplomat_of_country[nation_data.country][0]
            if now_diplomat_chara_id != 0:
                now_diplomat_chara_data = cache.character_data[now_diplomat_chara_id]
                now_diplomat_name = now_diplomat_chara_data.name
                now_diplomat_adv = now_diplomat_chara_data.adv
                now_diplomat_ability_lv = now_diplomat_chara_data.ability[40]
                ability_name = game_config.config_ability[40].name
                now_diplomat_ability_effect = 5 * attr_calculation.get_ability_adjust(now_diplomat_ability_lv)
                now_diplomat_text = f"\n  [{str(now_diplomat_adv).rjust(4,'0')}]{now_diplomat_name}  {ability_name}lv{now_diplomat_ability_lv}：{now_diplomat_ability_effect}%"
            else:
                now_diplomat_text = _("  无")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text + now_diplomat_text
            info_draw.width = self.width
            info_draw.draw()

            # 调整负责外交官
            line_feed.draw()
            line_feed.draw()
            adjust_NPC_button_draw = draw.CenterButton(
                _("【调整负责外交官】"),
                _("\n【调整负责外交官】"),
                self.width / 3,
                cmd_func=self.adjust_NPC,
                args=(nation_id,),
            )
            adjust_NPC_button_draw.draw()
            return_list.append(adjust_NPC_button_draw.return_text)

            # 设施信息
            facility_data = game_config.config_facility[14]
            facility_name = facility_data.name
            now_level = cache.rhodes_island.facility_level[14]
            facility_cid = game_config.config_facility_effect_data[facility_name][now_level]
            nation_num_limit = game_config.config_facility_effect[facility_cid].effect

            # # 如果有空闲势力，绘制出售按钮
            # if cache.rhodes_island.nations[nation_id][0] - cache.rhodes_island.nations[nation_id][1] > 0:
            #     sell_nation_draw = draw.CenterButton(
            #         _("【出售势力】"),
            #         _("\n【出售势力】"),
            #         self.width / 3,
            #         cmd_func=self.sell_nation,
            #         args=(nation_id,),
            #     )
            #     sell_nation_draw.draw()
            #     return_list.append(sell_nation_draw.return_text)

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


    def adjust_NPC(self, nation_id: int):
        """
        调整负责外交官
        Keyword arguments:
        nation_id -- 势力编号
        """

        nation_data = game_config.config_nation[nation_id]
        country_id = nation_data.country
        country_name = game_config.config_birthplace[country_id].name

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制可派遣人员
            info_draw_2 = draw.NormalDraw()
            info_draw_2.text = _("\n可选择干员（需要出身地或势力为{0}）：\n\n").format(country_name)
            info_draw_2.width = self.width
            info_draw_2.draw()
            npc_draw_count = 0
            for character_id in cache.npc_id_got:
                character_data: game_type.Character = cache.character_data[character_id]
                # 跳过出身地或势力不是当前势力的干员
                if character_data.relationship.birthplace != country_id and character_data.relationship.nation != nation_id:
                    continue
                draw_style = "standard"
                # 如果已经选择，则绘制为金色
                if character_id == cache.rhodes_island.diplomat_of_country[country_id][0]:
                    draw_style = "gold_enrod"
                character_data: game_type.Character = cache.character_data[character_id]
                character_name = character_data.name
                character_adv = character_data.adv
                character_ability_lv = character_data.ability[40]
                draw_text = f"[{str(character_adv).rjust(4,'0')}]{character_name}:lv{character_ability_lv}"

                # 绘制按钮
                button_draw = draw.LeftButton(
                    draw_text,
                    f"\n{character_id}",
                    self.width / 6 ,
                    normal_style = draw_style,
                    cmd_func = self.sure_NPC,
                    args = (character_id, country_id),
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 每绘制6个角色换行
                npc_draw_count += 1
                if npc_draw_count % 6 == 0:
                    line_feed.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break


    def sure_NPC(self, character_id: int, country_id: int):
        """
        确认负责外交官
        Keyword arguments:
        character_id -- 角色编号
        country_id -- 势力编号
        """

        from Script.Design import talk, handle_premise
        from Script.Settle import default

        # 解除任命旧的外交官
        old_diplomat_id = cache.rhodes_island.diplomat_of_country[country_id][0]
        if old_diplomat_id != 0:
            old_diplomat_chara_data = cache.character_data[old_diplomat_id]
            # 取消外交官的工作类型和负责区域数据
            old_diplomat_chara_data.work.work_type = 0
            cache.rhodes_island.diplomat_of_country[country_id][0] = 0
            # 如果是离线状态，则上线
            if not handle_premise.handle_normal_7(old_diplomat_id):
                default.handle_chara_on_line(old_diplomat_id, 1, change_data = game_type.CharacterStatusChange, now_time = cache.game_time)
            # 根据是本地还是外派，赋予对应的二段行为结算
            if cache.rhodes_island.current_location[0] == country_id:
                old_diplomat_chara_data.second_behavior = 1372
            else:
                old_diplomat_chara_data.second_behavior = 1374
            talk.must_show_talk_check(old_diplomat_id)

        # 任命新的外交官
        if character_id != 0 and character_id != old_diplomat_id:
            new_diplomat_chara_data = cache.character_data[character_id]
            # 设置外交官的工作类型和负责区域数据
            new_diplomat_chara_data.work.work_type = 131
            cache.rhodes_island.diplomat_of_country[country_id][0] = character_id
            # 根据是本地还是外派，赋予对应的二段行为结算
            if cache.rhodes_island.current_location[0] == country_id:
                new_diplomat_chara_data.second_behavior = 1371
                talk.must_show_talk_check(character_id)
            else:
                new_diplomat_chara_data.second_behavior = 1373
                talk.must_show_talk_check(character_id)
                default.handle_chara_off_line(character_id, 1, change_data = game_type.CharacterStatusChange, now_time = cache.game_time)
