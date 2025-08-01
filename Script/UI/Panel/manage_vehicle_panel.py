from typing import Tuple, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
import random

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

def update_basement_vehicle_data():
    """
    更新基地载具数据
    """
    vehicle_data = game_config.config_vehicle
    for vehicle_id in vehicle_data:
        if vehicle_id not in cache.rhodes_island.vehicles:
            cache.rhodes_island.vehicles[vehicle_id] = [0, 0]


def settle_vehicle(commision_id: int) -> str:
    """
    结算载具损坏与回收
    Keyword arguments:
    commision_id -- 委托编号
    Return arguments:
    vehicle_text -- 载具损坏与回收信息
    """
    vehicle_text = ""
    send_vehicle_list = cache.rhodes_island.ongoing_field_commissions[commision_id][2]
    # 损坏概率与等级相关
    base_rate = 0.05 * game_config.config_commission[commision_id].level
    for vehicle_id in send_vehicle_list:
        # 根据基准概率判断载具是否损坏
        if random.random() < base_rate:
            cache.rhodes_island.vehicles[vehicle_id][0] += -1
            cache.rhodes_island.vehicles[vehicle_id][1] += -1
            vehicle_text += _("({0}损坏)").format(game_config.config_vehicle[vehicle_id].name)
            # 如果损坏了，则概率下降一半，以免连续损坏
            base_rate *= 0.5
        else:
            cache.rhodes_island.vehicles[vehicle_id][1] -= 1

    return vehicle_text

class Manage_Vehicle_Panel:
    """
    用于显示载具管理界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("常规载具")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.send_npc_list = []
        """ 派遣人员列表 """
        self.vehicle_count = 0
        """ 当前拥有载具数量 """

    def draw(self):
        """绘制对象"""

        title_text = _("载具管理")
        commission_type_list = [_("常规载具"), _("特殊载具")]

        # 更新基地载具数据
        update_basement_vehicle_data()

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
            facility_data = game_config.config_facility[14]
            facility_name = facility_data.name
            now_level = str(cache.rhodes_island.facility_level[14])
            facility_cid = game_config.config_facility_effect_data[facility_name][int(now_level)]
            vehicle_num_limit = str(game_config.config_facility_effect[facility_cid].effect)
            # 载具数量
            self.vehicle_count = 0
            for vehicle_id in cache.rhodes_island.vehicles:
                self.vehicle_count += cache.rhodes_island.vehicles[vehicle_id][0]
            facility_info_text = ""
            facility_info_text += _("○载具用于给执行外勤委托的干员提供交通和其他方面的辅助，提高委托效率\n")
            facility_info_text += _("○当前机库等级：{0}，载具数量：{1}/{2}\n").format(now_level, self.vehicle_count, vehicle_num_limit)

            facility_info_draw = draw.NormalDraw()
            facility_info_draw.text = facility_info_text
            facility_info_draw.width = self.width
            facility_info_draw.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 绘制提示信息
            info_text_list = [_("载具名称"), _("外勤中数量/总持有量"), _("载具速度"), _("运载量"), _("特殊效果(未实装)")]
            for info_text in info_text_list:
                info_draw = draw.CenterDraw()
                info_draw.text = info_text
                info_draw.width = self.width / len(info_text_list)
                info_draw.draw()
            line_feed.draw()
            line = draw.LineDraw("~", self.width)
            line.draw()

            # 获取载具列表
            all_vehicle_list = []
            for cid in game_config.config_vehicle:
                vehicle_data = game_config.config_vehicle[cid]
                # 获得方式
                acquire_way = vehicle_data.acquiring
                vehicle_count = cache.rhodes_island.vehicles[vehicle_id][0]
                if self.now_panel == _("常规载具") and acquire_way != _("基础"):
                    continue
                if self.now_panel == _("特殊载具"):
                    if acquire_way == _("基础"):
                        continue
                    # 非基础的载具在未拥有时不显示
                    elif acquire_way != _("基础") and vehicle_count == 0:
                        continue
                all_vehicle_list.append(cid)

            # 绘制载具信息
            for vehicle_id in all_vehicle_list:
                vehicle_data = game_config.config_vehicle[vehicle_id]
                vehicle_name = vehicle_data.name
                # 计算出字符串中除中文汉字外的字符数量
                if vehicle_name[0] == " ":
                    extra_width_count = 3
                else:
                    extra_width_count = 0
                vehicle_speed = str(vehicle_data.speed)
                vehicle_capacity = str(vehicle_data.capacity)
                vehicle_special = vehicle_data.special
                vehicle_count = cache.rhodes_island.vehicles[vehicle_id][0]
                vehicle_count_str = str(cache.rhodes_island.vehicles[vehicle_id][1]) + "/" + str(cache.rhodes_island.vehicles[vehicle_id][0])
                text_width = int(self.width / (len(info_text_list)))
                str_text_width = int(text_width / 2)
                vehicle_text = f"{vehicle_name.center(str_text_width + extra_width_count,'　')}{vehicle_count_str.center(text_width,' ')}{vehicle_speed.center(text_width,' ')}{vehicle_capacity.center(text_width,' ')}{vehicle_special.center(str_text_width,'　')}"

                # 可以进行的，绘制为按钮
                vehicle_draw = draw.LeftButton(
                    vehicle_text,
                    "\n" + vehicle_name,
                    self.width,
                    cmd_func=self.vehicle_info,
                    args=(vehicle_id,),
                )
                vehicle_draw.draw()
                return_list.append(vehicle_draw.return_text)
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

    def vehicle_info(self, vehicle_id: int):
        """
        显示载具详细信息
        Keyword arguments:
        vehicle_id -- 载具编号
        """

        # 载具信息
        vehicle_data = game_config.config_vehicle[vehicle_id]
        vehicle_name = vehicle_data.name
        vehicle_speed = str(vehicle_data.speed)
        vehicle_capacity = str(vehicle_data.capacity)
        vehicle_special = vehicle_data.special
        vehicle_description = vehicle_data.description
        vehicle_price = vehicle_data.price
        vehicle_acquiring = vehicle_data.acquiring
        # 将\n替换为换行符
        if "\\n" in vehicle_description:
            vehicle_description = vehicle_description.replace("\\n", "\n      ")

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制载具信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n载具名称：{0}").format(vehicle_name)
            info_draw.text += _("\n载具速度：{0}").format(vehicle_speed)
            info_draw.text += _("\n运载量：{0}").format(vehicle_capacity)
            info_draw.text += _("\n购入价格：{0}（出售价格为购入的0.8倍）").format(vehicle_price)
            info_draw.text += _("\n特殊效果：{0}").format(vehicle_special)
            info_draw.text += _("\n介绍：{0}").format(vehicle_description)
            info_draw.width = self.width
            info_draw.draw()
            line_feed.draw()
            line_feed.draw()

            # 设施信息
            facility_data = game_config.config_facility[14]
            facility_name = facility_data.name
            now_level = cache.rhodes_island.facility_level[14]
            facility_cid = game_config.config_facility_effect_data[facility_name][now_level]
            vehicle_num_limit = game_config.config_facility_effect[facility_cid].effect

            # 基础型载具，如果还有载具购买空间，则绘制购买按钮
            if vehicle_acquiring == _("基础") and self.vehicle_count < int(vehicle_num_limit):
                buy_vehicle_draw = draw.CenterButton(
                    _("【购买载具】"),
                    _("\n【购买载具】"),
                    self.width / 3,
                    cmd_func=self.buy_vehicle,
                    args=(vehicle_id,),
                )
                buy_vehicle_draw.draw()
                return_list.append(buy_vehicle_draw.return_text)
            
            # 基础型载具，如果有空闲载具，绘制出售按钮
            if vehicle_acquiring == _("基础") and cache.rhodes_island.vehicles[vehicle_id][0] - cache.rhodes_island.vehicles[vehicle_id][1] > 0:
                sell_vehicle_draw = draw.CenterButton(
                    _("【出售载具】"),
                    _("\n【出售载具】"),
                    self.width / 3,
                    cmd_func=self.sell_vehicle,
                    args=(vehicle_id,),
                )
                sell_vehicle_draw.draw()
                return_list.append(sell_vehicle_draw.return_text)

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def buy_vehicle(self, vehicle_id: int):
        """
        购买载具
        Keyword arguments:
        vehicle_id -- 载具编号
        """
        from Script.UI.Panel import achievement_panel

        vehicle_data = game_config.config_vehicle[vehicle_id]
        vehicle_price = vehicle_data.price
        info_draw = draw.WaitDraw()
        info_draw.width = window_width
        # 购买载具
        if cache.rhodes_island.materials_resouce[1] >= vehicle_price:
            cache.rhodes_island.materials_resouce[1] -= vehicle_price
            cache.rhodes_island.vehicles[vehicle_id][0] += 1
            self.vehicle_count += 1
            info_draw.text = _("\n花费 {0} 龙门币购买了一个 {1}\n").format(vehicle_price, vehicle_data.name)
        else:
            info_draw.text = _("\n资金不足，无法购买\n")
            info_draw.style = "red"
        info_draw.draw()
        # 结算成就
        # achievement_panel.achievement_flow(_("载具"))

    def sell_vehicle(self, vehicle_id: int):
        """
        出售载具
        Keyword arguments:
        vehicle_id -- 载具编号
        """

        vehicle_data = game_config.config_vehicle[vehicle_id]
        vehicle_price = vehicle_data.price * 0.8
        # 出售载具
        cache.rhodes_island.materials_resouce[1] += vehicle_price
        cache.rhodes_island.vehicles[vehicle_id][0] -= 1
        self.vehicle_count -= 1
        info_draw = draw.WaitDraw()
        info_draw.width = window_width
        info_draw.text = _("\n出售了一个 {0}，获得了 {1} 龙门币\n").format(vehicle_data.name, vehicle_price)
        info_draw.draw()
