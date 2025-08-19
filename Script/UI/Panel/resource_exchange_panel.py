from typing import Dict, List
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

def get_resouce_price(resouce_id: int, buy_or_sell_flag: bool):
    """
    获取指定资源的交易价格及波动百分比
    输入: resouce_id(int) 资源ID, buy_or_sell_flag(bool) 买入(True)/卖出(False)
    输出: (int价格, float波动百分比)
    功能: 返回价格和供需波动百分比
    """
    resouce_data = game_config.config_resouce[resouce_id]
    base_price = resouce_data.price
    # 特产卖出价格为1.5倍
    if resouce_data.type == _("特产") and not buy_or_sell_flag:
        base_price = 1.5 * base_price
    else:
        base_price = 1.2 * base_price if buy_or_sell_flag else 0.8 * base_price
    cache.rhodes_island.supply_demand_dict.setdefault(resouce_id, 1)
    supply_demand = cache.rhodes_island.supply_demand_dict[resouce_id]
    price = base_price * supply_demand
    # 计算波动百分比（相对基础价格）
    percent = (supply_demand - 1) * 100
    return int(price), percent

def daily_supply_demand_fluctuation():
    """
    每日供需关系自然波动
    输入: 无
    输出: 无
    功能: 按当前供需系数，随机调整每种资源的供需，模拟经济学规律
    """
    # 供需字典初始化
    supply_demand_dict = cache.rhodes_island.supply_demand_dict
    for res_id in game_config.config_resouce:
        # 跳过货币类（如龙门币）
        if res_id == 1:
            continue
        # 当前供需系数
        cur = supply_demand_dict.get(res_id, 1)
        # 经济学规律：
        # 1. 越偏离1，回归趋势越强（均值回归）
        # 2. 随机波动幅度与偏离程度相关
        # 3. 保证供需系数不为负
        # 回归因子（越远离1，回归越强）
        revert = (1 - cur) * 0.05
        # 随机波动（基础±0.005，偏离越大波动越大）
        rand_fluct = random.uniform(-0.005, 0.005) + random.uniform(-abs(cur-1)*0.02, abs(cur-1)*0.02)
        # 总变化
        delta = revert + rand_fluct
        new_val = max(0.1, cur + delta)
        supply_demand_dict[res_id] = round(new_val, 4)

class Resource_Exchange_Line_Panel:
    """
    用于资源交易的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("资源交易")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.show_resource_type_dict: Dict = {_("材料"): False, _("药剂"): False, _("乳制品"): False, _("香水"): False, _("特产"): False}
        """ 显示的资源类型 """
        self.buy_or_sell_flag = True
        """ 交易状态，True为买入，False为卖出 """
        self.now_select_resouce_id = 11
        """ 当前选择的资源id，默认为11号资源（龙门币） """
        self.quantity_of_resouce = 0
        """ 交易数量，默认为0 """

    def draw(self):
        """绘制对象"""

        title_text = _("资源交易")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 绘制交易信息
            all_info_draw = draw.NormalDraw()
            now_text = ""
            money = cache.rhodes_island.materials_resouce[1]
            now_text += _("\n  当前龙门币数量    ：{0}").format(money)

            resouce_data  = game_config.config_resouce[self.now_select_resouce_id]
            now_resouce_stock = cache.rhodes_island.materials_resouce[self.now_select_resouce_id]
            warehouse_capacity = cache.rhodes_island.warehouse_capacity
            now_text += _("\n\n  要交易的资源为    ：{0}({1}/{2})    ").format(resouce_data.name, now_resouce_stock, warehouse_capacity)
            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            # 检测该商品是否可以购买
            if resouce_data.cant_buy == 1:
                cant_buy_flag = True
            else:
                cant_buy_flag = False

            button_text = _(" [更改交易资源] ")
            button_draw = draw.CenterButton(
                _(button_text),
                _("{0}").format(button_text),
                len(button_text) * 2,
                cmd_func=self.select_exchange_resouce,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            all_info_draw.text = _("\n\n  要交易的数量为    ：{0}    ").format(self.quantity_of_resouce)
            all_info_draw.draw()

            # 绘制数量变更按钮
            button_text_list = [" [-1000] "," [-100] ", " [-10] ", " [-1] ", " [+1] ", " [+10] ", " [+100] ", " [+1000] "]
            for button_text in button_text_list:
                button_draw = draw.CenterButton(
                    _(button_text),
                    _("{0}").format(button_text),
                    len(button_text) * 2,
                    cmd_func=self.settle_quantity,
                    args=(button_text, ),
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

            button_text = _(" [重置] ")
            button_draw = draw.CenterButton(
                _(button_text),
                _("{0}").format(button_text),
                len(button_text) * 2,
                cmd_func=self.reset_quantity,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            # 显示价格
            price, percent = get_resouce_price(self.now_select_resouce_id, self.buy_or_sell_flag)
            all_info_draw.text = _("\n\n  交易的价格为      ：")
            all_info_draw.draw()

            # 绘制买入还是卖出的按钮
            button_text = _(" [买入] ") if self.buy_or_sell_flag else _(" [卖出] ")
            button_draw = draw.CenterButton(
                _(button_text),
                _("{0}").format(button_text),
                len(button_text) * 2,
                cmd_func=self.settle_buy_or_sell,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            # 无法买入的，不显示价格
            if (self.buy_or_sell_flag and not cant_buy_flag) or not self.buy_or_sell_flag:
                # 显示价格波动百分比
                if percent > 0:
                    percent_str = f"(+{percent:.1f}%)"
                elif percent < 0:
                    percent_str = f"({percent:.1f}%)"
                else:
                    percent_str = ""
                all_info_draw.text = _(" {0}龙门币/1单位 {1} ").format(price, percent_str)
                all_info_draw.draw()
            line_feed.draw()

            # 输出总价
            if self.buy_or_sell_flag:
                all_info_draw.text = _("\n  ○预计共花费{0} * {1} = {2}龙门币\n").format(price, self.quantity_of_resouce, price * self.quantity_of_resouce)
                if price * self.quantity_of_resouce > money:
                    all_info_draw.text += _("  ●龙门币不足，无法购买\n")
                # 如果是不可购买的则显示提示
                if cant_buy_flag:
                    all_info_draw.text = _("\n  ●该资源无法购买，只能卖出\n")
            else:
                all_info_draw.text = _("\n  ○预计共获得{0} * {1} = {2}龙门币\n").format(price, self.quantity_of_resouce, price * self.quantity_of_resouce)
                if self.quantity_of_resouce > now_resouce_stock:
                    all_info_draw.text += _("  ●资源不足，无法出售\n")
            all_info_draw.draw()

            line_feed.draw()
            # 以下情况不绘制确定按钮
            # 买入，且钱不足
            # 买入，但是该资源不可买入
            # 卖出，且资源不足
            # 卖出，资源为特产且为本地特产
            if (
                (self.buy_or_sell_flag and price * self.quantity_of_resouce > money) or 
                (self.buy_or_sell_flag and cant_buy_flag) or
                (not self.buy_or_sell_flag and self.quantity_of_resouce > now_resouce_stock) or
                (not self.buy_or_sell_flag and resouce_data.type == _("特产") and resouce_data.specialty == cache.rhodes_island.current_location[0])
                ):
                pass
            else:
                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), int(window_width / 2))
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), int(window_width / 2))
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break
            elif yrn == yes_draw.return_text:
                self.execute_trade()

    def execute_trade(self):
        """
        执行资源交易
        输入: 无
        输出: 无
        功能: 根据当前买入/卖出状态和数量，结算资源与龙门币变动
        """
        # 计算价格和总价
        price, percent = get_resouce_price(self.now_select_resouce_id, self.buy_or_sell_flag)
        total_price = price * self.quantity_of_resouce
        # 买入
        if self.buy_or_sell_flag:
            cache.rhodes_island.materials_resouce[self.now_select_resouce_id] += self.quantity_of_resouce
            cache.rhodes_island.materials_resouce[1] -= total_price
            # 供需关系调整
            cache.rhodes_island.supply_demand_dict.setdefault(self.now_select_resouce_id, 1)
            if self.quantity_of_resouce > 50:
                tem_quantity_of_resouce = self.quantity_of_resouce
                while tem_quantity_of_resouce > 50:
                    tem_quantity_of_resouce -= 50
                    # 增加供需系数，回归越强则增加越少
                    cur_sd = cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id]
                    # 增量公式：基础0.001，越大越难涨
                    delta_sd = 0.001 * 10 * (1 / cur_sd)
                    cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id] = round(cur_sd + delta_sd, 4)
                # 限制最大值
                cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id] = min(5.0, cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id])
        # 卖出
        else:
            cache.rhodes_island.materials_resouce[self.now_select_resouce_id] -= self.quantity_of_resouce
            cache.rhodes_island.materials_resouce[1] += total_price
            # 供需关系调整
            cache.rhodes_island.supply_demand_dict.setdefault(self.now_select_resouce_id, 1)
            if self.quantity_of_resouce > 50:
                tem_quantity_of_resouce = self.quantity_of_resouce
                while tem_quantity_of_resouce > 50:
                    tem_quantity_of_resouce -= 50
                    # 减少供需系数，回归越强则减少越少
                    cur_sd = cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id]
                    # 减量公式：基础0.01，越小越难跌
                    delta_sd = 0.001 * 10 * (cur_sd / 1)
                    cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id] = round(cur_sd - delta_sd, 4)
                # 限制最小值
                cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id] = max(0.1, cache.rhodes_island.supply_demand_dict[self.now_select_resouce_id])
        # 打印交易结果
        info_draw = draw.WaitDraw()
        info_draw.text = _("\n交易成功！\n当前龙门币数量：{0}({1})\n资源{2}数量：{3}/{4}({5})\n").format(
            cache.rhodes_island.materials_resouce[1],
            "-" + str(total_price) if self.buy_or_sell_flag else "+" + str(total_price),
            game_config.config_resouce[self.now_select_resouce_id].name,
            cache.rhodes_island.materials_resouce[self.now_select_resouce_id],
            cache.rhodes_island.warehouse_capacity,
            "+" + str(self.quantity_of_resouce) if self.buy_or_sell_flag else "-" + str(self.quantity_of_resouce)
        )
        info_draw.draw()
        line_feed.draw()

    def select_exchange_resouce(self):
        """选择交易资源"""
        while 1:

                line = draw.LineDraw("-", window_width)
                line.draw()
                line_feed.draw()
                info_draw = draw.NormalDraw()
                info_draw.width = window_width
                return_list = []

                resouce_now_data = game_config.config_resouce[self.now_select_resouce_id]

                info_text = _("当前的交易资源为：{0}").format(resouce_now_data.name)
                info_text += _("\n当前可以交易的资源有：\n")
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()

                # 遍历全资源类型
                resouce_list = [_("材料"), _("药剂"), _("乳制品"), _("香水"), _("特产")]
                for resouce_type in resouce_list:

                    # 判断是否显示该类型的资源
                    if self.show_resource_type_dict[resouce_type]:
                        draw_text = f" ▼[{resouce_type}]"
                    else:
                        draw_text = f" ▶[{resouce_type}]"
                    button_draw = draw.LeftButton(
                    f"{draw_text}",
                    f"{resouce_type}",
                    len(draw_text) * 2,
                    cmd_func=self.settle_show_resource_type,
                    args=(resouce_type)
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    line_feed.draw()

                    # 遍历该类型的资源
                    if not self.show_resource_type_dict[resouce_type]:
                        continue
                    for resouce_id in game_config.config_resouce:
                        resouce_data  = game_config.config_resouce[resouce_id]
                        if resouce_data.type == resouce_type:
                            # 特产商品仅在当地可以买入，其他地方只能卖出
                            if resouce_data.type == _("特产"):
                                if cache.rhodes_island.materials_resouce[resouce_id] == 0 and resouce_data.specialty != cache.rhodes_island.current_location[0]:
                                    continue
                            button_draw = draw.LeftButton(
                            f" [{str(resouce_id).rjust(3,'0')}]{resouce_data.name}：{resouce_data.info}",
                            f"\n{resouce_id}",
                            window_width ,
                            cmd_func=self.settle_now_select_resouce_id,
                            args=(resouce_id)
                            )
                            button_draw.draw()
                            return_list.append(button_draw.return_text)

                            now_text = _("\n      当前存量：{0}/{1}").format(cache.rhodes_island.materials_resouce[resouce_id], cache.rhodes_island.warehouse_capacity)
                            # 判断是否可以买入卖出
                            if resouce_data.cant_buy == 0:
                                price_buy, percent_buy = get_resouce_price(resouce_id, True)
                                if percent_buy > 0:
                                    percent_str_buy = f"(+{percent_buy:.1f}%)"
                                elif percent_buy < 0:
                                    percent_str_buy = f"({percent_buy:.1f}%)"
                                else:
                                    percent_str_buy = "(0%)"
                                now_text += _("   买入:{0}龙门币/1单位 {1}").format(price_buy, percent_str_buy)
                            # 如果是卖出
                            price_sell, percent_sell = get_resouce_price(resouce_id, False)
                            if percent_sell > 0:
                                percent_str_sell = f"(+{percent_sell:.1f}%)"
                            elif percent_sell < 0:
                                percent_str_sell = f"({percent_sell:.1f}%)"
                            else:
                                percent_str_sell = ""
                            now_text += _("   卖出:{0}龙门币/1单位 {1}\n").format(price_sell, percent_str_sell)
                            info_draw.text = now_text
                            info_draw.draw()

                line_feed.draw()
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
                back_draw.draw()
                line_feed.draw()
                return_list.append(back_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list and yrn not in resouce_list:
                    break

    def settle_now_select_resouce_id(self, resouce_id):
        """结算要交易的资源"""
        self.now_select_resouce_id = resouce_id
        resouce_data  = game_config.config_resouce[self.now_select_resouce_id]
        # 默认变成买入，不可买入的则变成卖出
        if self.now_select_resouce_id == 12 or resouce_data.type == _("药剂"):
            self.buy_or_sell_flag = False
        # 特产商品仅在当地可以买入，其他地方只能卖出
        elif resouce_data.type == _("特产"):
            if resouce_data.specialty == cache.rhodes_island.current_location[0]:
                self.buy_or_sell_flag = True
            else:
                self.buy_or_sell_flag = False
        else:
            self.buy_or_sell_flag = not self.buy_or_sell_flag

    def settle_quantity(self, button_text):
        """结算交易数量变更"""
        add_num = int(button_text[2:-2])
        self.quantity_of_resouce += add_num
        # 保证卖出的不超过仓库容量
        if not self.buy_or_sell_flag and self.quantity_of_resouce > cache.rhodes_island.materials_resouce[self.now_select_resouce_id]:
            self.quantity_of_resouce = cache.rhodes_island.materials_resouce[self.now_select_resouce_id]
        # 保证买入的不超过仓库容量
        if self.buy_or_sell_flag and (self.quantity_of_resouce + cache.rhodes_island.materials_resouce[self.now_select_resouce_id]) > cache.rhodes_island.warehouse_capacity:
            self.quantity_of_resouce = cache.rhodes_island.warehouse_capacity - cache.rhodes_island.materials_resouce[self.now_select_resouce_id]
        # 保证不为负数
        if self.quantity_of_resouce < 0:
            self.quantity_of_resouce = 0

    def reset_quantity(self,):
        """重置资源交易数量"""
        self.quantity_of_resouce = 0

    def settle_buy_or_sell(self):
        """切换买入和卖出"""
        self.buy_or_sell_flag = not self.buy_or_sell_flag

    def settle_show_resource_type(self, resouce_type):
        """设置显示的资源类型"""
        self.show_resource_type_dict[resouce_type] = not self.show_resource_type_dict[resouce_type]
