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
        
        # === 排序与翻页相关变量 ===
        self.sort_by = _("默认")
        self.is_ascending = True  # 默认升序
        self.current_page = 1
        self.items_per_page = 10  # 设定中间固定行数（每页最大载具数）

    # === 切换排序条件 ===
    def change_sort_by(self, sort_by_type: str):
        self.sort_by = sort_by_type
        self.current_page = 1

    # === 切换升降序 ===
    def change_sort_order(self):
        self.is_ascending = not self.is_ascending
        self.current_page = 1

    # === 切换页数 ===
    def change_page(self, target_page: int):
        self.current_page = target_page

    def draw(self):
        """绘制对象"""
        from Script.Design import attr_calculation

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
                    now_draw.width = int(self.width / len(commission_type_list))
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{commission_type}]",
                        f"\n{commission_type}",
                        int(self.width / len(commission_type_list)),
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

            money = str(cache.rhodes_island.materials_resouce[1])
            facility_info_text += _("○当前龙门币数量：{0}\n").format(money)

            facility_info_draw = draw.NormalDraw()
            facility_info_draw.text = facility_info_text
            facility_info_draw.width = self.width
            facility_info_draw.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # === 排序按钮 ===
            sort_text_list = [_("默认"), _("持有量"), _("价钱"), _("速度"), _("运载量")]
            for sort_type in sort_text_list:
                if sort_type == self.sort_by:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{sort_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = int(self.width / len(sort_text_list))
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{sort_type}]",
                        f"\n{sort_type}",
                        int(self.width / len(sort_text_list)),
                        cmd_func=self.change_sort_by,
                        args=(sort_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            
            # === 升序降序按钮 ===
            order_text = _("当前排序：升序") if self.is_ascending else _("当前排序：降序")
            order_draw = draw.CenterButton(
                f"[{order_text}]",
                _("\n点击切换升降序"),
                self.width,
                cmd_func=self.change_sort_order,
            )
            order_draw.draw()
            return_list.append(order_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            info_text_list = [_("载具名称"), _("外勤中数量/总持有量"), _(" 价钱"), _(" 载具速度"), _(" 运载量"), _(" 特殊效果(未实装)")]
            # 修正文本宽度
            text_width = int((self.width) / (len(info_text_list)))
            for info_text in info_text_list:
                info_draw = draw.CenterDraw()
                info_draw.text = info_text
                info_draw.width = text_width
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
                vehicle_count = cache.rhodes_island.vehicles[cid][0]
                if self.now_panel == _("常规载具") and acquire_way != _("基础"):
                    continue
                if self.now_panel == _("特殊载具"):
                    if acquire_way == _("基础"):
                        continue
                    # 非基础的载具在未拥有时不显示
                    elif acquire_way != _("基础") and vehicle_count == 0:
                        continue
                all_vehicle_list.append(cid)

            # === 对列表进行排序逻辑处理 ===
            def get_sort_key(cid_key):
                if self.sort_by == _("持有量"):
                    return cache.rhodes_island.vehicles[cid_key][0]
                elif self.sort_by == _("价钱"):
                    return game_config.config_vehicle[cid_key].price
                elif self.sort_by == _("速度"):
                    return game_config.config_vehicle[cid_key].speed
                elif self.sort_by == _("运载量"):
                    return game_config.config_vehicle[cid_key].capacity
                else:
                    return cid_key  # 默认按编号

            all_vehicle_list.sort(key=get_sort_key, reverse=not self.is_ascending)

            # === 分页计算 ===
            total_items = len(all_vehicle_list)
            total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
            if self.current_page > total_pages:
                self.current_page = total_pages
            
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            display_list = all_vehicle_list[start_idx:end_idx]

            # 绘制载具信息 (修改：只绘制当前页内容，并在中间加入价钱数据)
            for vehicle_id in display_list:
                vehicle_data = game_config.config_vehicle[vehicle_id]
                vehicle_name = attr_calculation.pad_display_width(vehicle_data.name, text_width, "center")
                
                # 新增读取并排版价钱
                vehicle_price = attr_calculation.pad_display_width(str(vehicle_data.price), text_width, "center")
                
                vehicle_speed = attr_calculation.pad_display_width(str(vehicle_data.speed), text_width, "center")
                vehicle_capacity = attr_calculation.pad_display_width(str(vehicle_data.capacity), text_width, "center")
                vehicle_special = attr_calculation.pad_display_width(vehicle_data.special, text_width, "center")
                vehicle_count_str = str(cache.rhodes_island.vehicles[vehicle_id][1]) + "/" + str(cache.rhodes_island.vehicles[vehicle_id][0])
                vehicle_count_str = attr_calculation.pad_display_width(vehicle_count_str, text_width, "center")
                
                # 文本中加入 vehicle_price
                vehicle_text = f"{vehicle_name}{vehicle_count_str}{vehicle_price}{vehicle_speed}{vehicle_capacity}{vehicle_special}"

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

            # === 用空行填充剩余的总行数 ===
            drawn_lines = len(display_list)
            for i in range(self.items_per_page - drawn_lines):
                line_feed.draw()

            # === 返回上面加翻页和第几页 ===
            line = draw.LineDraw("-", self.width)
            line.draw()
            
            if total_pages == 1:
                # 只有一页时无法点击
                page_text = _(" 第 {0} / {1} 页 ").format(self.current_page, total_pages)
                page_draw = draw.CenterDraw()
                page_draw.text = page_text
                page_draw.width = self.width
                page_draw.draw()
                line_feed.draw()
            else:
                # 计算循环翻页的目标页
                prev_page = self.current_page - 1 if self.current_page > 1 else total_pages
                next_page = self.current_page + 1 if self.current_page < total_pages else 1

                # 始终绘制上一页按钮
                prev_draw = draw.CenterButton(_("[上一页]"), _("\n上一页"), int(self.width / 3), cmd_func=self.change_page, args=(prev_page,))
                prev_draw.draw()
                return_list.append(prev_draw.return_text)
                    
                # 绘制页数
                page_draw = draw.CenterDraw()
                page_draw.text = _(" 第 {0} / {1} 页 ").format(self.current_page, total_pages)
                page_draw.width = int(self.width / 3)
                page_draw.draw()
                
                # 始终绘制下一页按钮
                next_draw = draw.CenterButton(_("[下一页]"), _("\n下一页"), int(self.width / 3), cmd_func=self.change_page, args=(next_page,))
                next_draw.draw()
                return_list.append(next_draw.return_text)
                
                line_feed.draw()
                
            line = draw.LineDraw("-", self.width)
            line.draw()

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
            
            title_text = _("载具购买")
            title_draw = draw.TitleLineDraw(title_text, self.width)
            title_draw.draw()

            # 绘制载具信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n 载具名称：{0}").format(vehicle_name)
            info_draw.text += _("\n 载具速度：{0}").format(vehicle_speed)
            info_draw.text += _("\n 运载量：{0}").format(vehicle_capacity)
            info_draw.text += _("\n 购入价格：{0}（出售价格为购入的0.8倍）").format(vehicle_price)
            info_draw.text += _("\n 特殊效果：{0}").format(vehicle_special)
            info_draw.text += _("\n 介绍：{0}").format(vehicle_description)
            
            owned_count = cache.rhodes_island.vehicles[vehicle_id][0]
            info_draw.text += _("\n\n 该载具当前已拥有数量：{0}").format(owned_count)
            
            money = str(cache.rhodes_island.materials_resouce[1])
            info_draw.text += _("\n 当前龙门币数量：{0}").format(money)
            info_draw.width = self.width
            info_draw.draw()
            
            # 设施信息(提前获取设施上限以便计算空间)
            facility_data = game_config.config_facility[14]
            facility_name = facility_data.name
            now_level = cache.rhodes_island.facility_level[14]
            facility_cid = game_config.config_facility_effect_data[facility_name][now_level]
            vehicle_num_limit = game_config.config_facility_effect[facility_cid].effect

            money_left_draw = draw.NormalDraw()
            money_left = cache.rhodes_island.materials_resouce[1] - vehicle_price
            money_left_draw.text = _(" 购买后剩余龙门币数量：{0}").format(money_left)
            if money_left < 0:
                money_left_draw.style = "warning"
            money_left_draw.draw()
            
            line_feed.draw()
            
            space_left_draw = draw.NormalDraw()
            space_left = int(vehicle_num_limit) - self.vehicle_count
            space_left_draw.text = _(" 当前剩余载具空间：{0}").format(space_left)
            if space_left <= 0:
                space_left_draw.style = "warning"
            space_left_draw.draw()
            
            line_feed.draw()
            line_feed.draw()
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 定义统一下方按钮的宽度基准
            btn_width = int(self.width / 3)

            # === 判断是否可购买 ===
            buy_condition = (vehicle_acquiring == _("基础") and self.vehicle_count < int(vehicle_num_limit) and money_left >= 0)
            if buy_condition:
                buy_vehicle_draw = draw.CenterButton(
                    _("【购买载具】"),
                    _("\n【购买载具】"),
                    btn_width,
                    cmd_func=self.buy_vehicle,
                    args=(vehicle_id,),
                )
                buy_vehicle_draw.draw()
                return_list.append(buy_vehicle_draw.return_text)
            else:
                buy_vehicle_draw = draw.CenterDraw()
                buy_vehicle_draw.text = _("【购买载具】")
                buy_vehicle_draw.style = "deep_gray"  # 设置为灰色文字
                buy_vehicle_draw.width = btn_width
                buy_vehicle_draw.draw()
            
            # === 判断是否可出售 ===
            sell_condition = (vehicle_acquiring == _("基础") and cache.rhodes_island.vehicles[vehicle_id][0] - cache.rhodes_island.vehicles[vehicle_id][1] > 0)
            if sell_condition:
                sell_vehicle_draw = draw.CenterButton(
                    _("【出售载具】"),
                    _("\n【出售载具】"),
                    btn_width,
                    cmd_func=self.sell_vehicle,
                    args=(vehicle_id,),
                )
                sell_vehicle_draw.draw()
                return_list.append(sell_vehicle_draw.return_text)
            else:
                sell_vehicle_draw = draw.CenterDraw()
                sell_vehicle_draw.text = _("【出售载具】")
                sell_vehicle_draw.style = "deep_gray" # 设置为灰色文字
                sell_vehicle_draw.width = btn_width
                sell_vehicle_draw.draw()

            line_feed.draw()
            line_feed.draw()
            
            # === 返回按钮的宽度设定为上面两者的宽度之和 ===
            back_btn_width = btn_width * 2
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), back_btn_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            
            yrn = flow_handle.askfor_all(return_list)
            # 只有点击返回按钮时才 break 跳出载具信息页面
            if yrn == back_draw.return_text:
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
        achievement_panel.achievement_flow(_("载具"))

    def sell_vehicle(self, vehicle_id: int):
        """
        出售载具
        Keyword arguments:
        vehicle_id -- 载具编号
        """

        vehicle_data = game_config.config_vehicle[vehicle_id]
        vehicle_price = int(vehicle_data.price * 0.8)
        # 出售载具
        cache.rhodes_island.materials_resouce[1] += vehicle_price
        cache.rhodes_island.vehicles[vehicle_id][0] -= 1
        self.vehicle_count -= 1
        info_draw = draw.WaitDraw()
        info_draw.width = window_width
        info_draw.text = _("\n出售了一个 {0}，获得了 {1} 龙门币\n").format(vehicle_data.name, vehicle_price)
        info_draw.draw()
