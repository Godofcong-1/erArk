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
        self.show_country_subordinate_dict: dict = {}
        """ 显示的国家及附属势力字典 """
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
        # 收起所有国家的附属势力
        for nation_id in game_config.config_nation:
            if 11 < nation_id < 500:
                # 如果个位是1的话，则是总势力
                if nation_id % 10 == 1:
                    self.show_country_subordinate_dict[nation_id] = False

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
            info_text_list = [" " * self.show_draw_width + _("势力名称"), _("势力声望"), _("源石病治愈率(未实装)")]
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
                # 获取当前位置的势力列表
                if self.now_panel == _("国家及附属势力") and nation_data.country == cache.rhodes_island.current_location[0]:
                    now_lacation_nation_list.append(cid)
                    continue
                # 去掉非当前面板的势力
                if self.now_panel == _("国家及附属势力") and nation_data.country == -1:
                    continue
                if self.now_panel == _("其他势力") and nation_data.country != -1:
                    continue
                all_nation_list.append(cid)

            # 绘制势力信息
            for nation_id in all_nation_list:
                nation_data = game_config.config_nation[nation_id]

                # 在国家的前面加一个三角按钮用来展开与收起附属势力，非国家则显示横杠
                if self.now_panel == _("国家及附属势力"):
                    if nation_id in self.show_country_subordinate_dict:
                        if self.show_country_subordinate_dict[nation_id]:
                            show_text = "▶"
                        else:
                            show_text = "▼"
                        button_draw = draw.CenterButton(
                            show_text,
                            show_text + nation_data.name,
                            self.show_draw_width,
                            cmd_func=self.change_nation_show,
                            args=(nation_id,),
                        )
                        button_draw.draw()
                        return_list.append(button_draw.return_text)
                    else:
                        # 检查是否要绘制附属势力，用除以10取余数的方式获得总势力id
                        base_nation_id = nation_id // 10 * 10 + 1
                        # 如果找不到总势力id，则跳过
                        if base_nation_id not in self.show_country_subordinate_dict:
                            continue
                        # 如果总势力id不显示附属势力，则跳过
                        if not self.show_country_subordinate_dict[base_nation_id]:
                            continue
                        show_text = "--"
                        info_draw = draw.LeftDraw()
                        info_draw.text = show_text
                        info_draw.width = self.show_draw_width
                        info_draw.draw()

                # 势力按钮绘制
                nation_name = nation_data.name
                # 声望与治愈率
                now_nation_reputation = str(cache.country.nation_reputation[nation_id])
                if nation_data.country == -1:
                    now_country_treatment_progress = _("无")
                else:
                    now_country_treatment_progress = str(cache.country.country_infection_rate[nation_data.country])
                text_width = int(self.width / (len(info_text_list)))
                str_text_width = int((text_width - self.show_draw_width) / 2)
                nation_text = f"{nation_name.center(str_text_width,'　')}{now_nation_reputation.center(text_width,' ')}{now_country_treatment_progress.center(text_width,' ')}"

                # 可以进行的，绘制为按钮
                nation_draw = draw.LeftButton(
                    nation_text,
                    "\n" + nation_name,
                    self.width - self.show_draw_width,
                    cmd_func=self.nation_info,
                    args=(nation_id,),
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

    def change_nation_show(self, nation_id: int):
        """
        展开或收起国家的附属势力
        Keyword arguments:
        nation_id -- 势力编号
        """

        if nation_id in self.show_country_subordinate_dict:
            if self.show_country_subordinate_dict[nation_id]:
                self.show_country_subordinate_dict[nation_id] = False
            else:
                self.show_country_subordinate_dict[nation_id] = True
        else:
            self.show_country_subordinate_dict[nation_id] = False


    def nation_info(self, nation_id: int):
        """
        显示势力详细信息
        Keyword arguments:
        nation_id -- 势力编号
        """

        # 势力信息
        nation_data = game_config.config_nation[nation_id]
        nation_name = nation_data.name
        nation_speed = str(nation_data.speed)
        nation_capacity = str(nation_data.capacity)
        nation_special = nation_data.special
        nation_description = nation_data.description
        nation_price = nation_data.price
        # 将\n替换为换行符
        if "\\n" in nation_description:
            nation_description = nation_description.replace("\\n", "\n      ")

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制势力信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n势力名称：{0}").format(nation_name)
            info_draw.text += _("\n势力速度：{0}").format(nation_speed)
            info_draw.text += _("\n运载量：{0}").format(nation_capacity)
            info_draw.text += _("\n购入价格：{0}（出售价格为购入的0.8倍）").format(nation_price)
            info_draw.text += _("\n特殊效果：{0}").format(nation_special)
            info_draw.text += _("\n介绍：{0}").format(nation_description)
            info_draw.width = self.width
            info_draw.draw()
            line_feed.draw()
            line_feed.draw()

            # 设施信息
            facility_data = game_config.config_facility[14]
            facility_name = facility_data.name
            now_level = cache.rhodes_island.facility_level[14]
            facility_cid = game_config.config_facility_effect_data[facility_name][now_level]
            nation_num_limit = game_config.config_facility_effect[facility_cid].effect

            # 如果还有势力购买空间，则绘制购买按钮
            if self.nation_count < int(nation_num_limit):
                buy_nation_draw = draw.CenterButton(
                    _("【购买势力】"),
                    _("\n【购买势力】"),
                    self.width / 3,
                    cmd_func=self.buy_nation,
                    args=(nation_id,),
                )
                buy_nation_draw.draw()
                return_list.append(buy_nation_draw.return_text)
            
            # 如果有空闲势力，绘制出售按钮
            if cache.rhodes_island.nations[nation_id][0] - cache.rhodes_island.nations[nation_id][1] > 0:
                sell_nation_draw = draw.CenterButton(
                    _("【出售势力】"),
                    _("\n【出售势力】"),
                    self.width / 3,
                    cmd_func=self.sell_nation,
                    args=(nation_id,),
                )
                sell_nation_draw.draw()
                return_list.append(sell_nation_draw.return_text)

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def buy_nation(self, nation_id: int):
        """
        购买势力
        Keyword arguments:
        nation_id -- 势力编号
        """

        nation_data = game_config.config_nation[nation_id]
        nation_price = nation_data.price
        info_draw = draw.WaitDraw()
        info_draw.width = window_width
        # 购买势力
        if cache.rhodes_island.materials_resouce[1] >= nation_price:
            cache.rhodes_island.materials_resouce[1] -= nation_price
            cache.rhodes_island.nations[nation_id][0] += 1
            self.nation_count += 1
            info_draw.text = _("\n花费 {0} 龙门币购买了一个 {1}\n").format(nation_price, nation_data.name)
        else:
            info_draw.text = _("\n资金不足，无法购买\n")
            info_draw.style = "red"
        info_draw.draw()

    def sell_nation(self, nation_id: int):
        """
        出售势力
        Keyword arguments:
        nation_id -- 势力编号
        """

        nation_data = game_config.config_nation[nation_id]
        nation_price = nation_data.price * 0.8
        # 出售势力
        cache.rhodes_island.materials_resouce[1] += nation_price
        cache.rhodes_island.nations[nation_id][0] -= 1
        self.nation_count -= 1
        info_draw = draw.WaitDraw()
        info_draw.width = window_width
        info_draw.text = _("\n出售了一个 {0}，获得了 {1} 龙门币\n").format(nation_data.name, nation_price)
        info_draw.draw()
