from typing import Dict, List, Tuple, Optional
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation
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


def _ensure_trade_setting(res_id: int) -> Dict[str, int]:
    """确保指定id资源的自动交易配置存在"""

    settings = cache.rhodes_island.resource_type_auto_trade_setting.setdefault(
        res_id,
        {
            "buy_on": False,
            "buy_stock": 0,
            "buy_price_percent": 100,
            "sell_on": False,
            "sell_stock": 0,
            "sell_price_percent": 100,
        },
    )
    for key in ("buy_on", "buy_stock", "buy_price_percent", "sell_on", "sell_stock", "sell_price_percent"):
        settings.setdefault(key, 0)
    return settings

def _get_resource_type_key(resouce_id: int) -> str:
    """获取资源类型并保证相关字典已初始化"""

    resouce_data = game_config.config_resouce[resouce_id]
    res_type = resouce_data.type
    cache.rhodes_island.resource_type_main_trader.setdefault(res_type, 0)
    _ensure_trade_setting(resouce_id)
    return res_type

def get_trade_resource_types() -> List[str]:
    """获取所有可管理的资源类型列表"""

    res_types: List[str] = []
    seen_type: set = set()
    for res_id in game_config.config_resouce:
        if res_id == 0:
            continue
        res_type = game_config.config_resouce[res_id].type
        if res_type in seen_type:
            continue
        seen_type.add(res_type)
        cache.rhodes_island.resource_type_main_trader.setdefault(res_type, 0)
        _ensure_trade_setting(res_id)
        res_types.append(res_type)
    return res_types

def calculate_trade_multiplier(resouce_id: int, buy_flag: bool) -> Tuple[float, float, float]:
    """
    计算交易价格乘数及主副交易员加成\n
    输入: resouce_id(int) 资源ID, buy_flag(bool) 买入(True)/卖出(False)]\n
    输出: (float乘数, float主交易员加成, float副交易员加成)
    """

    TRADE_MAIN_RATE: float = 0.005
    """ 主交易员每级话术带来的价格百分比调整 """
    TRADE_SUB_RATE: float = 0.001
    """ 副交易员每级话术带来的价格百分比调整 """
    MIN_BUY_MULTIPLIER: float = 0.5
    """ 交易员调整的买入价格下限（为基础价格的百分比） """
    MAX_SELL_MULTIPLIER: float = 2.0
    """ 交易员调整的卖出价格上限（为基础价格的百分比） """

    res_type = _get_resource_type_key(resouce_id)
    trade_ids = cache.rhodes_island.trade_operator_ids_list
    main_id = cache.rhodes_island.resource_type_main_trader.get(res_type, 0)
    main_bonus = 0.0
    sub_bonus = 0.0
    if main_id in trade_ids and main_id > 0:
        ability_lv = cache.character_data[main_id].ability.get(40, 0)
        main_bonus = ability_lv * TRADE_MAIN_RATE
    for chara_id in trade_ids:
        if chara_id == main_id or chara_id not in cache.character_data:
            continue
        ability_lv = cache.character_data[chara_id].ability.get(40, 0)
        sub_bonus += ability_lv * TRADE_SUB_RATE
    total_bonus = main_bonus + sub_bonus
    if buy_flag:
        multiplier = max(MIN_BUY_MULTIPLIER, 1 - total_bonus)
    else:
        multiplier = min(MAX_SELL_MULTIPLIER, 1 + total_bonus)
    return multiplier, main_bonus, sub_bonus

def _adjust_supply_demand_after_trade(resouce_id: int, quantity: int, buy_flag: bool) -> None:
    """依据交易数量调整供需系数"""

    if quantity <= 0:
        return
    cache.rhodes_island.supply_demand_dict.setdefault(resouce_id, 1)
    steps = quantity // 50
    if steps <= 0:
        return
    for _step in range(steps):
        cur_sd = cache.rhodes_island.supply_demand_dict[resouce_id]
        today_total = cache.rhodes_island.today_trade_resource_count.get(resouce_id, 0)
        if buy_flag:
            delta_sd = 0.001 * 10 * (1 / cur_sd)
            delta_sd *= 1 + (today_total / 1000)
            cache.rhodes_island.supply_demand_dict[resouce_id] = round(min(5.0, cur_sd + delta_sd), 4)
        else:
            delta_sd = 0.001 * 10 * cur_sd
            delta_sd /= 1 + (today_total / 1000)
            cache.rhodes_island.supply_demand_dict[resouce_id] = round(max(0.1, cur_sd - delta_sd), 4)

def perform_trade(resouce_id: int, quantity: int, buy_flag: bool) -> Optional[Dict[str, int]]:
    """执行具体交易结算，返回实际成交情况"""

    # 数量为0或负数直接返回无效
    if quantity <= 0:
        return None
    resouce_data = game_config.config_resouce[resouce_id]
    price, _percent = get_resouce_price(resouce_id, buy_flag)
    # 价格为0或负数直接返回无效
    if price <= 0:
        return None
    # 初始化资源库存
    cache.rhodes_island.materials_resouce.setdefault(resouce_id, 0)
    cache.rhodes_island.materials_resouce.setdefault(1, 0)

    result_quantity = quantity
    # 买入操作
    if buy_flag:
        capacity_left = cache.rhodes_island.warehouse_capacity - cache.rhodes_island.materials_resouce[resouce_id]
        # 仓库已满无法购买
        if capacity_left <= 0:
            return None
        result_quantity = min(result_quantity, capacity_left)
        if price > 0:
            affordable = cache.rhodes_island.materials_resouce[1] // price
            result_quantity = min(result_quantity, affordable)
        if result_quantity <= 0:
            return None
        total_price = price * result_quantity
        cache.rhodes_island.materials_resouce[resouce_id] += result_quantity
        cache.rhodes_island.materials_resouce[1] -= total_price
        _adjust_supply_demand_after_trade(resouce_id, result_quantity, True)
    # 卖出操作
    else:
        available = cache.rhodes_island.materials_resouce[resouce_id]
        result_quantity = min(result_quantity, available)
        # 无法卖出任何数量
        if result_quantity <= 0:
            return None
        total_price = price * result_quantity
        cache.rhodes_island.materials_resouce[resouce_id] -= result_quantity
        cache.rhodes_island.materials_resouce[1] += total_price
        _adjust_supply_demand_after_trade(resouce_id, result_quantity, False)

    cache.rhodes_island.today_trade_resource_count.setdefault(resouce_id, 0)
    cache.rhodes_island.today_trade_resource_count[resouce_id] += result_quantity

    return {
        "quantity": result_quantity,
        "price": price,
        "total_price": price * result_quantity,
    }

def auto_trade_resources() -> None:
    """根据自动交易设置执行买卖"""

    if not cache.rhodes_island.trade_operator_ids_list:
        return

    summary_lines: List[str] = []
    for res_type in get_trade_resource_types():
        # 跳过无效或货币类资源
        if res_type in {"无", "货币"}:
            continue
        main_id = cache.rhodes_island.resource_type_main_trader.get(res_type, 0)
        if not main_id:
            continue

        for resouce_id, resouce_data in game_config.config_resouce.items():
            if resouce_id == 0 or resouce_data.type != res_type:
                continue
            settings = _ensure_trade_setting(resouce_id)
            buy_on = settings.get("buy_on", False)
            buy_stock = settings.get("buy_stock", 0)
            buy_percent = settings.get("buy_price_percent", 0)
            sell_on = settings.get("sell_on", False)
            sell_stock = settings.get("sell_stock", 0)
            sell_percent = settings.get("sell_price_percent", 0)
            cache.rhodes_island.materials_resouce.setdefault(resouce_id, 0)

            # 自动买入
            if (
                buy_on and
                buy_stock > 0 and
                buy_percent > 0 and
                resouce_data.cant_buy == 0 and
                cache.rhodes_island.materials_resouce[resouce_id] < buy_stock
            ):
                price_now, percent_buy = get_resouce_price(resouce_id, True)
                base_price = resouce_data.price if resouce_data.price > 0 else price_now
                if price_now <= base_price * buy_percent / 100:
                    need_qty = buy_stock - cache.rhodes_island.materials_resouce[resouce_id]
                    trade_ret = perform_trade(resouce_id, need_qty, True)
                    if trade_ret:
                        summary_lines.append(
                            _("  · 自动买入{0} x {1}，单价{2}，总计{3}").format(
                                _(resouce_data.name),
                                trade_ret["quantity"],
                                trade_ret["price"],
                                trade_ret["total_price"],
                            )
                        )

            # 自动卖出
            if (
                sell_on and
                sell_stock >= 0 and
                sell_percent > 0 and
                cache.rhodes_island.materials_resouce[resouce_id] > sell_stock
            ):
                price_now, percent_sell = get_resouce_price(resouce_id, False)
                base_price = resouce_data.price if resouce_data.price > 0 else price_now
                if price_now >= base_price * sell_percent / 100:
                    need_qty = cache.rhodes_island.materials_resouce[resouce_id] - sell_stock
                    trade_ret = perform_trade(resouce_id, need_qty, False)
                    if trade_ret:
                        summary_lines.append(
                            _("  · 自动卖出{0} x {1}，单价{2}，总计{3}").format(
                                _(resouce_data.name),
                                trade_ret["quantity"],
                                trade_ret["price"],
                                trade_ret["total_price"],
                            )
                        )

    if summary_lines:
        info_draw = draw.WaitDraw()
        info_draw.text = _("\n自动贸易执行结果：\n") + "\n".join(summary_lines) + "\n"
        info_draw.draw()

def get_resouce_price(resouce_id: int, buy_or_sell_flag: bool, self_check: bool = True) -> Tuple[int, float]:
    """
    获取指定资源的交易价格及波动百分比
    输入:
        resouce_id(int) 资源ID
        buy_or_sell_flag(bool) 买入(True)/卖出(False)
        self_check(bool) 是否进行自检，默认为True
    输出: (int价格, float波动百分比)
    功能: 返回价格和供需波动百分比
    """
    resouce_data = game_config.config_resouce[resouce_id]
    base_price = resouce_data.price
    # 非本地特产的价格为1.5倍
    if resouce_data.type == _("特产") and resouce_data.specialty == cache.rhodes_island.current_location[0]:
        base_price *= 1.5
    else:
        base_price = 1.1 * base_price if buy_or_sell_flag else 0.9 * base_price
    cache.rhodes_island.supply_demand_dict.setdefault(resouce_id, 1)
    # 供需影响
    supply_demand = cache.rhodes_island.supply_demand_dict[resouce_id]
    # 交易员影响
    multiplier, tem1, tem2 = calculate_trade_multiplier(resouce_id, buy_or_sell_flag)
    # 总影响
    final_adjustment = supply_demand * multiplier
    # 计算最终价格
    price = base_price * final_adjustment
    # 买入价格不能低于卖出价格，卖出价格不能高于买入价格
    if buy_or_sell_flag and self_check:
        sell_price = get_resouce_price(resouce_id, False, self_check=False)[0]
        price = max(price, sell_price)
        final_adjustment = max(final_adjustment, sell_price / base_price)
    elif not buy_or_sell_flag and self_check:
        buy_price = get_resouce_price(resouce_id, True, self_check=False)[0]
        price = min(price, buy_price)
        final_adjustment = min(final_adjustment, buy_price / base_price)
    # 计算波动百分比（相对基础价格）
    percent = (final_adjustment - 1) * 100
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
        # 今日买入卖出数量归零
        cache.rhodes_island.today_trade_resource_count[res_id] = 0
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

    # 供需波动后尝试执行自动交易
    auto_trade_resources()

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
        self.show_resource_type_dict: Dict = {_("材料"): False, _("药剂"): False, _("乳制品"): False, _("香水"): False, _("基建"): False, _("特产"): False}
        """ 显示的资源类型 """
        self.buy_or_sell_flag = True
        """ 交易状态，True为买入，False为卖出 """
        self.now_select_resouce_id = 11
        """ 当前选择的资源id，默认为11号资源（普通药材） """
        self.quantity_of_resouce = 0
        """ 交易数量，默认为0 """

    def draw(self):
        """绘制对象"""

        title_text = _("资源交易")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 资源数据
            resouce_data = game_config.config_resouce[self.now_select_resouce_id] # 资源数据
            now_resouce_stock = cache.rhodes_island.materials_resouce[self.now_select_resouce_id] # 当前资源库存
            warehouse_capacity = cache.rhodes_island.warehouse_capacity # 仓库容量
            cant_buy_flag = True if resouce_data.cant_buy == 1 else False # 检测该商品是否可以购买
            money = cache.rhodes_island.materials_resouce[1] # 当前龙门币数量

            # 绘制交易信息
            all_info_draw = draw.NormalDraw()
            now_text = ""
            money_text = _("当前龙门币数量")
            now_text += ("  {0}：{1}\n").format(attr_calculation.pad_display_width(money_text, 16), money)
            resouce_text = _("交易资源")
            now_text += ("  {0}：{1}").format(attr_calculation.pad_display_width(resouce_text, 16), resouce_data.name)
            now_text += " " * 8
            all_info_draw.text = now_text
            all_info_draw.draw()

            button_text = _(" [更改交易资源] ")
            button_draw = draw.CenterButton(
                _(button_text),
                _("{0}").format(button_text),
                len(button_text) * 2,
                cmd_func=self.select_exchange_resouce,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw()

            quantity_text = _("交易数量")
            now_text = ("  {0}：{1}\n").format(attr_calculation.pad_display_width(quantity_text, 16), self.quantity_of_resouce)
            rescouce_change_text = _("资源库存变化")
            now_text += ("  {0}：").format(attr_calculation.pad_display_width(rescouce_change_text, 16))
            now_text += ("{0}/{1} ± {2} = {3}/{1} ~ {4}/{1}\n").format(now_resouce_stock, warehouse_capacity, self.quantity_of_resouce, now_resouce_stock - self.quantity_of_resouce, now_resouce_stock + self.quantity_of_resouce)
            all_info_draw.text = now_text
            all_info_draw.draw()

            res_type_key = _get_resource_type_key(self.now_select_resouce_id)
            settings = _ensure_trade_setting(self.now_select_resouce_id)
            main_id = cache.rhodes_island.resource_type_main_trader.get(res_type_key, 0)
            main_name = cache.character_data[main_id].name if main_id > 0 else _("空缺")
            main_text = main_name
            main_level = cache.character_data[main_id].ability.get(40, 0) if main_id > 0 else 0
            if main_id and main_level:
                main_text += _("(话术lv{0})").format(main_level)
            sub_names = [cache.character_data[cid].name for cid in cache.rhodes_island.trade_operator_ids_list if cid != main_id and cid in cache.character_data]
            sub_text = "、".join(sub_names) if sub_names else _("空缺")

            trade_npc_text = _("交易员")
            now_text = _("  {0}：主-{1}，副-{2}").format(attr_calculation.pad_display_width(trade_npc_text, 16), main_name, sub_text)
            now_text += " " * 8
            all_info_draw.text = now_text
            all_info_draw.draw()
            manage_button_text = _(" [交易员管理] ")
            manage_button = draw.CenterButton(
                manage_button_text,
                manage_button_text,
                len(manage_button_text) * 2,
                cmd_func=self.manage_trade_operator,
            )
            return_list.append(manage_button.return_text)
            manage_button.draw()
            line_feed.draw()
            if main_id:
                auto_trade_text = _("自动交易")
                now_text = _("  {0}：").format(attr_calculation.pad_display_width(auto_trade_text, 16))
                if settings["buy_on"]:
                    now_text += _("买入至{0}/{1}%").format(settings["buy_stock"], settings["buy_price_percent"])
                else:
                    now_text += _("未设置自动买入")
                now_text += "，"
                if settings["sell_on"]:
                    now_text += _("卖出至{0}/{1}%").format(settings["sell_stock"], settings["sell_price_percent"])
                else:
                    now_text += _("未设置自动卖出")
                now_text += " " * 8
                all_info_draw.text = now_text
                all_info_draw.draw()
                auto_button_text = _(" [自动交易设置] ")
                auto_button = draw.CenterButton(
                    auto_button_text,
                    auto_button_text,
                    len(auto_button_text) * 2,
                    cmd_func=self.auto_trade_setting,
                    args=(self.now_select_resouce_id,),
                )
                return_list.append(auto_button.return_text)
                auto_button.draw()
                line_feed.draw()

            # 显示价格
            buy_price, buy_percent = get_resouce_price(self.now_select_resouce_id, True)
            sell_price, sell_percent = get_resouce_price(self.now_select_resouce_id, False)
            price_text = _("交易价格")
            all_info_draw.text = ("  {0}：").format(attr_calculation.pad_display_width(price_text, 16))
            all_info_draw.draw()

            # 显示价格波动百分比
            if buy_percent > 0:
                buy_percent_str = f"(+{buy_percent:.1f}%)"
            elif buy_percent < 0:
                buy_percent_str = f"({buy_percent:.1f}%)"
            else:
                buy_percent_str = ""
            if sell_percent > 0:
                sell_percent_str = f"(+{sell_percent:.1f}%)"
            elif sell_percent < 0:
                sell_percent_str = f"({sell_percent:.1f}%)"
            else:
                sell_percent_str = ""
            max_len_price = max(len(str(buy_price)), len(str(sell_price)))
            all_info_draw.text = _("买入 {0} 龙门币/1单位 {1}，总价 {0} * {2} = {3} 龙门币\n").format(attr_calculation.pad_display_width(str(buy_price), max_len_price), buy_percent_str, self.quantity_of_resouce, buy_price * self.quantity_of_resouce)
            all_info_draw.text += " " * 20
            all_info_draw.text += _("卖出 {0} 龙门币/1单位 {1}，总价 {0} * {2} = {3} 龙门币\n").format(attr_calculation.pad_display_width(str(sell_price), max_len_price), sell_percent_str, self.quantity_of_resouce, sell_price * self.quantity_of_resouce)
            all_info_draw.draw()
            line_feed.draw()

            # 绘制数量变更按钮
            quantity_change_text = _("数量变更")
            all_info_draw.text = ("  {0}：").format(attr_calculation.pad_display_width(quantity_change_text, 16))
            all_info_draw.draw()
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
            line_feed.draw()

            # 输出特殊提示
            all_info_draw.text = ""
            if buy_price * self.quantity_of_resouce > money:
                all_info_draw.text += _("  ●龙门币不足，无法购买\n")
            # 如果是不可购买的则显示提示
            if cant_buy_flag:
                all_info_draw.text += _("  ●该资源无法购买，只能卖出\n")
            # 如果有文本，则在文本前加个换行
            if len(all_info_draw.text) > 0:
                all_info_draw.text = "\n" + all_info_draw.text
            all_info_draw.draw()

            line_feed.draw()

            buy_button = draw.CenterButton(
                _("[买入]"),
                _("买入"),
                int(window_width / 3),
                cmd_func=self.execute_trade,
                args=(True,),
            )
            sell_button = draw.CenterButton(
                _("[卖出]"),
                _("卖出"),
                int(window_width / 3),
                cmd_func=self.execute_trade,
                args=(False,),
            )
            # 以下情况绘制买入按钮
            # 钱足够且该资源可以买入
            if self.quantity_of_resouce > 0 and money > buy_price * self.quantity_of_resouce and not cant_buy_flag:
                buy_button.draw()
                return_list.append(buy_button.return_text)
            # 以下情况绘制卖出按钮
            # 库存大于等于预定卖出的资源数量，且卖出资源不是特产或不是本地特产
            if (
                self.quantity_of_resouce > 0 and
                (now_resouce_stock >= self.quantity_of_resouce) and
                (resouce_data.type != _("特产") or resouce_data.specialty == cache.rhodes_island.current_location[0])
                ):
                sell_button.draw()
                return_list.append(sell_button.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), int(window_width / 3))
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def execute_trade(self, buy_or_sell_flag: bool):
        """
        执行资源交易
        输入: 无
        输出: 无
        功能: 根据当前买入/卖出状态和数量，结算资源与龙门币变动
        """
        trade_result = perform_trade(self.now_select_resouce_id, self.quantity_of_resouce, buy_or_sell_flag)
        if not trade_result:
            info_draw = draw.WaitDraw()
            info_draw.text = _("\n交易未能执行，请检查资金、仓库或库存限制。\n")
            info_draw.draw()
            line_feed.draw()
            return

        price = trade_result["price"]
        actual_quantity = trade_result["quantity"]
        total_price = trade_result["total_price"]
        money_delta = "-" + str(total_price) if buy_or_sell_flag else "+" + str(total_price)
        resource_delta = "+" + str(actual_quantity) if buy_or_sell_flag else "-" + str(actual_quantity)

        info_draw = draw.WaitDraw()
        info_draw_text = _("\n交易成功！\n当前龙门币数量：{0}({1})\n资源{2}数量：{3}/{4}({5})\n").format(
            cache.rhodes_island.materials_resouce[1],
            money_delta,
            game_config.config_resouce[self.now_select_resouce_id].name,
            cache.rhodes_island.materials_resouce[self.now_select_resouce_id],
            cache.rhodes_island.warehouse_capacity,
            resource_delta,
        )
        if actual_quantity != self.quantity_of_resouce:
            info_draw_text += _("(本次实际成交{0}单位)\n").format(actual_quantity)
        info_draw.text = info_draw_text
        info_draw.draw()
        line_feed.draw()
        self.quantity_of_resouce = 0

    def manage_trade_operator(self):
        """交易员管理界面"""

        from Script.Design import basement
        from Script.UI.Panel import manage_basement_panel

        while 1:
            basement.update_work_people()
            title = draw.TitleLineDraw(_("交易员管理"), self.width)
            title.draw()
            return_list = []

            info = draw.NormalDraw()
            info.text = _("当前交易相关干员数量：{0}").format(len(cache.rhodes_island.trade_operator_ids_list))
            info.draw()
            line_feed.draw()

            adjust_button_text = _("[交易员增减]")
            adjust_button = draw.CenterButton(
                adjust_button_text,
                adjust_button_text,
                len(adjust_button_text) * 2,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=self.width,
            )
            return_list.append(adjust_button.return_text)
            adjust_button.draw()
            line_feed.draw(); line_feed.draw()

            trade_types = get_trade_resource_types()
            main_ids = set()
            for res_type in trade_types:
                # 跳过无效或货币类资源
                if res_type in {_("无"), _("货币")}:
                    continue
                main_id = cache.rhodes_island.resource_type_main_trader.get(res_type, 0)
                if main_id:
                    main_ids.add(main_id)
                main_name = cache.character_data[main_id].name if main_id > 0 else _("空缺")
                main_level = cache.character_data[main_id].ability.get(40, 0) if main_id > 0 else 0
                row = draw.NormalDraw()
                row.text = _("{0} 主交易员：{1}").format(attr_calculation.pad_display_width(res_type, 8, align="center"), main_name)
                if main_id and main_level:
                    row.text += _("(话术lv{0})").format(main_level)
                row.draw()

                assign_button = draw.CenterButton(
                    _("[任命]"),
                    f"assign_{res_type}",
                    len(_("[任命]")) * 2,
                    cmd_func=self.assign_main_trader,
                    args=(res_type,),
                )
                return_list.append(assign_button.return_text)
                assign_button.draw()

                clear_button = draw.CenterButton(
                    _("[清空]"),
                    f"clear_{res_type}",
                    len(_("[清空]")) * 2,
                    cmd_func=self.clear_main_trader,
                    args=(res_type,),
                )
                return_list.append(clear_button.return_text)
                clear_button.draw()
                line_feed.draw()

            line_feed.draw()
            sub_ids = [cid for cid in cache.rhodes_island.trade_operator_ids_list if cid not in main_ids and cid in cache.character_data]
            sub_draw = draw.NormalDraw()
            if sub_ids:
                sub_names = "、".join(cache.character_data[cid].name for cid in sub_ids)
                sub_draw.text = _("副交易员：") + sub_names + "\n"
            else:
                sub_draw.text = _("副交易员：暂无\n")
            sub_draw.draw()
            line_feed.draw()

            back_button = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            return_list.append(back_button.return_text)
            back_button.draw()
            line_feed.draw()

            choice = flow_handle.askfor_all(return_list)
            if choice == back_button.return_text:
                break

    def clear_main_trader(self, res_type: str):
        """清空指定资源类型的主交易员"""

        cache.rhodes_island.resource_type_main_trader[res_type] = 0

    def assign_main_trader(self, res_type: str):
        """任命指定资源类型的主交易员"""

        from Script.Design import basement
        from Script.UI.Panel import common_select_NPC
        from Script.UI.Moudle import panel

        basement.update_work_people()
        target_type = res_type
        current_main = cache.rhodes_island.resource_type_main_trader.get(target_type, 0)

        def _make(chara_id: int):
            self._do_assign_main_trader(target_type, chara_id)

        npc_panel: panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, True, False, 0)
        select_state = {}

        while 1:
            info_text = _("请选择一名交易员担任【{0}】的主交易员：\n").format(_(target_type))
            candidate_list = []
            for npc_id in cache.rhodes_island.trade_operator_ids_list:
                if npc_id == 0:
                    continue
                candidate_list.append([npc_id, _make, [current_main]])
            if not candidate_list:
                info_text += _("当前没有可任命的交易员，请先安排干员担任贸易相关工作。\n")
            npc_panel.text_list = candidate_list
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(
                npc_panel,
                _("任命主交易员"),
                info_text,
                select_state,
            )
            choice = flow_handle.askfor_all(return_list)
            if choice == _("返回"):
                break
            current_main = cache.rhodes_island.resource_type_main_trader.get(target_type, 0)

    def _do_assign_main_trader(self, res_type: str, chara_id: int):
        """执行主交易员任命/撤销操作"""

        if chara_id not in cache.rhodes_island.trade_operator_ids_list:
            return
        current = cache.rhodes_island.resource_type_main_trader.get(res_type, 0)
        if current == chara_id:
            cache.rhodes_island.resource_type_main_trader[res_type] = 0
        else:
            cache.rhodes_island.resource_type_main_trader[res_type] = chara_id

    def auto_trade_setting(self, res_id: int):
        """调整指定资源类型的自动交易设置"""

        target_type = _get_resource_type_key(res_id)
        resource_data = game_config.config_resouce[res_id]
        while 1:
            settings = _ensure_trade_setting(res_id)
            title = draw.TitleLineDraw(_("自动交易设置 - {0}").format(resource_data.name), self.width)
            title.draw()
            return_list = []

            main_id = cache.rhodes_island.resource_type_main_trader.get(target_type, 0)
            info_draw = draw.NormalDraw()
            if not main_id:
                info_draw.text = _("当前资源类型尚未任命主交易员，无法配置自动交易。\n")
                info_draw.draw()
                back_button = draw.CenterButton(_("[返回]"), _("返回"), self.width)
                return_list.append(back_button.return_text)
                back_button.draw()
                line_feed.draw()
                choice = flow_handle.askfor_all(return_list)
                if choice == back_button.return_text:
                    break
                continue

            # 显示当前资源的名称与库存量
            current_stock = cache.rhodes_island.materials_resouce.get(res_id, 0)
            stock_draw = draw.NormalDraw()
            stock_draw.text = _("当前资源：{0}，库存量：{1}\n").format(resource_data.name, current_stock)
            stock_draw.draw()
            line_feed.draw()

            # 自动买入开关
            buy_on_button_text = _("[自动买入：{0}]").format(_("开启") if settings["buy_on"] else _("关闭"))
            buy_on_button = draw.CenterButton(
                buy_on_button_text,
                f"{res_id}_buy_on_toggle",
                len(buy_on_button_text) * 2,
                cmd_func=self.toggle_auto_trade,
                args=(res_id, "buy_on"),
            )
            return_list.append(buy_on_button.return_text)
            buy_on_button.draw()
            line_feed.draw()
            # 如果买入开启，显示买入设置
            if settings["buy_on"]:
                # 买入库存
                stock_buy_draw = draw.NormalDraw()
                stock_buy_draw.text = ("{0}：").format(attr_calculation.pad_display_width(_("自动买入目标库存"), 20, align="center"))
                stock_buy_draw.text += str(settings["buy_stock"])
                stock_buy_draw.draw()
                stock_buttons = [(" [-1000] ", -1000), (" [-100] ", -100), (" [-10] ", -10), (" [-1] ", -1), (" [+1] ", 1), (" [+10] ", 10), (" [+100] ", 100), (" [+1000] ", 1000)]
                for label, delta in stock_buttons:
                    button = draw.CenterButton(
                        _(label),
                        f"{res_id}_buy_stock_{label.strip()}",
                        len(label) * 2,
                        cmd_func=self.adjust_auto_trade_value,
                        args=(res_id, "buy_stock", delta, False, False),
                    )
                    return_list.append(button.return_text)
                    button.draw()
                reset_button = draw.CenterButton(
                    _("[重置]"),
                    f"{res_id}_buy_stock_reset",
                    len(_("[重置]")) * 2,
                    cmd_func=self.adjust_auto_trade_value,
                    args=(res_id, "buy_stock", 0, False, True),
                )
                return_list.append(reset_button.return_text)
                reset_button.draw()
                line_feed.draw()

                # 买入价格
                price_buy_draw = draw.NormalDraw()
                price_buy_draw.text = ("{0}：").format(attr_calculation.pad_display_width(_("自动买入触发价格"), 20, align="center"))
                price_buy_draw.text += ("{0}%").format(settings["buy_price_percent"])
                price_buy_draw.draw()
                price_buttons = [(" [-20%] ", -20), (" [-5%] ", -5), (" [-1%] ", -1), (" [+1%] ", 1), (" [+5%] ", 5), (" [+20%] ", 20)]
                for label, delta in price_buttons:
                    button = draw.CenterButton(
                        _(label),
                        f"{res_id}_buy_price_{label.strip()}",
                        len(label) * 2,
                        cmd_func=self.adjust_auto_trade_value,
                        args=(res_id, "buy_price_percent", delta, True, False),
                    )
                    return_list.append(button.return_text)
                    button.draw()
                reset_button = draw.CenterButton(
                    _("[重置]"),
                    f"{res_id}_buy_price_reset",
                    len(_("[重置]")) * 2,
                    cmd_func=self.adjust_auto_trade_value,
                    args=(res_id, "buy_price_percent", 100, True, True),
                )
                return_list.append(reset_button.return_text)
                reset_button.draw()
                line_feed.draw()

                # 显示要进行的买入操作预览，当库存低于目标且价格低于触发价时，将买入至目标库存
                preview_buy_draw = draw.NormalDraw()
                preview_buy_draw_text = _("{0}：").format(attr_calculation.pad_display_width("买入操作预览", 20, align="center"))
                preview_buy_draw_text += _("在0点结算时，如果库存低于 {0} 且买价低于基准价的 {1}% 时，买入至库存为 {0} 。\n").format(settings["buy_stock"], settings["buy_price_percent"])
                preview_buy_draw.text = preview_buy_draw_text
                preview_buy_draw.draw()
            line_feed.draw()

            # 自动卖出开关
            sell_on_button_text = _("[自动卖出：{0}]").format(_("开启") if settings["sell_on"] else _("关闭"))
            sell_on_button = draw.CenterButton(
                sell_on_button_text,
                f"{res_id}_sell_on_toggle",
                len(sell_on_button_text) * 2,
                cmd_func=self.toggle_auto_trade,
                args=(res_id, "sell_on"),
            )
            return_list.append(sell_on_button.return_text)
            sell_on_button.draw()
            line_feed.draw()
            # 如果卖出开启，显示卖出设置
            if settings["sell_on"]:
                # 卖出库存
                stock_sell_draw = draw.NormalDraw()
                stock_sell_draw.text = ("{0}：").format(attr_calculation.pad_display_width(_("自动卖出目标库存"), 20, align="center"))
                stock_sell_draw.text += str(settings["sell_stock"])
                stock_sell_draw.draw()
                for label, delta in stock_buttons:
                    button = draw.CenterButton(
                        _(label),
                        f"{res_id}_sell_stock_{label.strip()}",
                        len(label) * 2,
                        cmd_func=self.adjust_auto_trade_value,
                        args=(res_id, "sell_stock", delta, False, False),
                    )
                    return_list.append(button.return_text)
                    button.draw()
                reset_button = draw.CenterButton(
                    _("[重置]"),
                    f"{res_id}_sell_stock_reset",
                    len(_("[重置]")) * 2,
                    cmd_func=self.adjust_auto_trade_value,
                    args=(res_id, "sell_stock", 0, False, True),
                )
                return_list.append(reset_button.return_text)
                reset_button.draw()
                line_feed.draw()

                # 卖出价格
                price_sell_draw = draw.NormalDraw()
                price_sell_draw.text = ("{0}：").format(attr_calculation.pad_display_width(_("自动卖出触发价格"), 20, align="center"))
                price_sell_draw.text += ("{0}%").format(settings["sell_price_percent"])
                price_sell_draw.draw()
                for label, delta in price_buttons:
                    button = draw.CenterButton(
                        _(label),
                        f"{res_id}_sell_price_{label.strip()}",
                        len(label) * 2,
                        cmd_func=self.adjust_auto_trade_value,
                        args=(res_id, "sell_price_percent", delta, True, False),
                    )
                    return_list.append(button.return_text)
                    button.draw()
                reset_button = draw.CenterButton(
                    _("[重置]"),
                    f"{res_id}_sell_price_reset",
                    len(_("[重置]")) * 2,
                    cmd_func=self.adjust_auto_trade_value,
                    args=(res_id, "sell_price_percent", 100, True, True),
                )
                return_list.append(reset_button.return_text)
                reset_button.draw()
                line_feed.draw()
                # 显示要进行的卖出操作预览，当库存高于目标且价格高于触发价时，将卖出至目标库存
                preview_sell_draw = draw.NormalDraw()
                preview_sell_draw_text = _("{0}：").format(attr_calculation.pad_display_width("卖出操作预览", 20, align="center"))
                preview_sell_draw_text += _("在0点结算时，如果库存高于 {0} 且卖价高于基准价的 {1}% 时，卖出至库存为 {0} 。\n").format(settings["sell_stock"], settings["sell_price_percent"])
                preview_sell_draw.text = preview_sell_draw_text
                preview_sell_draw.draw()

            line_feed.draw()
            back_button = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            return_list.append(back_button.return_text)
            back_button.draw()
            line_feed.draw()

            choice = flow_handle.askfor_all(return_list)
            if choice == back_button.return_text:
                break

    def toggle_auto_trade(self, res_id: int, key: str):
        """切换自动交易配置的开关状态"""

        settings = _ensure_trade_setting(res_id)
        settings[key] = not settings.get(key, False)

    def adjust_auto_trade_value(self, res_id: int, key: str, delta: int, is_percent: bool = False, reset: bool = False):
        """调整自动交易配置的单个数值"""

        settings = _ensure_trade_setting(res_id)
        if reset:
            settings[key] = 0
            return

        new_value = settings.get(key, 0) + delta
        if new_value < 0:
            new_value = 0
        if is_percent:
            new_value = min(300, new_value)
        else:
            max_capacity = cache.rhodes_island.warehouse_capacity
            if max_capacity > 0:
                new_value = min(max_capacity, new_value)
        settings[key] = new_value

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
                resouce_list = [_("材料"), _("药剂"), _("乳制品"), _("香水"), _("基建"), _("特产")]
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

    def settle_quantity(self, button_text):
        """结算交易数量变更"""
        add_num = int(button_text[2:-2])
        self.quantity_of_resouce += add_num
        # 交易数量不能超过可购买数量和可卖出数量中的较大值
        limit = max(cache.rhodes_island.materials_resouce[self.now_select_resouce_id], cache.rhodes_island.warehouse_capacity - cache.rhodes_island.materials_resouce[self.now_select_resouce_id])
        self.quantity_of_resouce = min(self.quantity_of_resouce, limit)
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
