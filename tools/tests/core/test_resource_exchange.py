# -*- coding: UTF-8 -*-
"""资源交易：特产只在产地按常规价买入、异地按 1.5 倍卖出，大地图移动后异地特产可手动卖出（#326），自动交易同样受限，交易员加成抬高特产卖价，买卖的资金/库存不变式"""
from _bootstrap import *  # noqa: F401,F403
from Script.Design import basement
from Script.UI.Panel import navigation_panel
from Script.UI.Panel import resource_exchange_panel as rep

# ==== 0. fixture：完整的新档罗德岛数据（全资源库存 0、位置在炎国、自动交易设置默认） ====
cache.rhodes_island = basement.get_base_zero()
cache.rhodes_island.warehouse_capacity = 1000
CAPACITY = 1000
""" 仓库容量 """
# 抵达目的地会结算导航成就（会读写成就数据），与交易无关，打桩在调用方模块上
navigation_panel.achievement_panel.achievement_flow = lambda *a, **k: None
W = rep.window_width
""" 面板宽度 """
HOME = 17
""" 新档初始所在国：炎 """
AWAY = 5
""" 大地图移动的目的国：卡西米尔 """
SP_HOME = 261
""" 炎的特产（罐装晌午茶） """
SP_AWAY = 141
""" 卡西米尔的特产（骑士领纪念模型） """
SP_OTHER = 101
""" 第三国阿戈尔的特产（阿戈尔示波器） """
NORMAL = 11
""" 普通资源：普通药材 """
CANT_BUY = 12
""" 不可购买资源：矿石病药材 """
TRADER = 301
""" 交易员 fixture 的角色id """


def price_of(res_id: int) -> int:
    """
    读取资源的配置基础价
    Keyword arguments:
    res_id -- 资源id
    Return arguments:
    int -- 基础价格
    """
    return game_config.config_resouce[res_id].price


def name_of(res_id: int) -> str:
    """
    读取资源名
    Keyword arguments:
    res_id -- 资源id
    Return arguments:
    str -- 资源名
    """
    return game_config.config_resouce[res_id].name


def type_of(res_id: int) -> str:
    """
    读取资源类型（主交易员按类型任命，键直接取配置值）
    Keyword arguments:
    res_id -- 资源id
    Return arguments:
    str -- 资源类型
    """
    return game_config.config_resouce[res_id].type


def stock(res_id: int) -> int:
    """
    读取资源库存
    Keyword arguments:
    res_id -- 资源id
    Return arguments:
    int -- 当前库存
    """
    return cache.rhodes_island.materials_resouce[res_id]


def money() -> int:
    """
    读取龙门币
    Keyword arguments:
    无
    Return arguments:
    int -- 当前龙门币
    """
    return cache.rhodes_island.materials_resouce[1]


def set_stock(res_id: int, num: int):
    """
    设置资源库存（资源 1 即龙门币）
    Keyword arguments:
    res_id -- 资源id
    num -- 数量
    Return arguments:
    无
    """
    cache.rhodes_island.materials_resouce[res_id] = num


def reset_market():
    """
    供需系数、今日交易量、自动交易设置全部回到新档状态，避免各节互相影响
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache.rhodes_island.supply_demand_dict.clear()
    cache.rhodes_island.today_trade_resource_count.clear()
    for setting in cache.rhodes_island.resource_type_auto_trade_setting.values():
        setting.update({"buy_on": False, "buy_stock": 0, "buy_price_percent": 100, "sell_on": False, "sell_stock": 0, "sell_price_percent": 100})


def arrive_at(country_id: int) -> bool:
    """
    走真实的大地图抵达结算（navigation_panel.judge_arrive）把罗德岛移到某国，抵达时间设为当前时间
    Keyword arguments:
    country_id -- 目的国家id
    Return arguments:
    bool -- 是否结算了抵达
    """
    cache.rhodes_island.move_target_and_time = [country_id, 0, cache.game_time]
    return navigation_panel.judge_arrive()


# ==== 1. 按钮可点：用 headless_base 的可点击按钮桩与脚本化 askfor_all（run_panel / plan / ask_log / missed 见该文件） ====
enable_clickable_buttons()


def options(index: int) -> list:
    """
    第 index 次 askfor_all 的可选项（越界返回空列表）
    Keyword arguments:
    index -- 第几次询问，从 0 开始
    Return arguments:
    list -- 可选项列表
    """
    return ask_log[index][0] if index < len(ask_log) else []


def text_after(prefix: str) -> str:
    """
    找到以 prefix 开头的那段绘制文本，返回紧跟其后的一段（资源选择列表里按钮之后就是该资源的价格行）
    Keyword arguments:
    prefix -- 前缀
    Return arguments:
    str -- 紧跟的文本，找不到返回空字符串
    """
    for index, text in enumerate(drawn_text[:-1]):
        if text.startswith(prefix):
            return drawn_text[index + 1]
    return ""


def make_panel(res_id: int, quantity: int = 0) -> rep.Resource_Exchange_Line_Panel:
    """
    建一个选中指定资源、带指定交易数量的交易面板
    Keyword arguments:
    res_id -- 资源id
    quantity -- 交易数量（正买负卖）
    Return arguments:
    Resource_Exchange_Line_Panel -- 面板对象
    """
    panel = rep.Resource_Exchange_Line_Panel(W)
    panel.now_select_resouce_id = res_id
    panel.quantity_of_resouce = quantity
    return panel


def drawn(text: str) -> bool:
    """
    某段文本是否被原样画出
    Keyword arguments:
    text -- 文本
    Return arguments:
    bool -- 是否画出
    """
    return text in drawn_text


BUY_OK = _("确认买入")
SELL_OK = _("确认卖出")
WARN_SP_NOT_ORIGIN = _("  ●特产只能在产地买入，在其他地区只能卖出")
WARN_SP_ORIGIN = _("  ●本地特产只能买入，需要到其他地区才能卖出")


def warn_drawn(warn: str) -> bool:
    """
    预算区块的警示行（多条警示拼在同一段文本里）是否含某条警示
    Keyword arguments:
    warn -- 警示文本
    Return arguments:
    bool -- 是否含有
    """
    return any(warn in text for text in drawn_text)


# ==== 2. 价格规则与买卖方向 ====
section("特产价格与买卖方向（#326）")
reset_market()
check("新档位于炎国", cache.rhodes_island.current_location[0] == HOME, cache.rhodes_island.current_location)
check("非特产资源买卖都不受所在地限制", rep.check_specialty_trade_allowed(NORMAL, True) and rep.check_specialty_trade_allowed(NORMAL, False))
check("产地的特产：能买、不能卖", rep.check_specialty_trade_allowed(SP_HOME, True) and not rep.check_specialty_trade_allowed(SP_HOME, False))
check("异地的特产：不能买、能卖", not rep.check_specialty_trade_allowed(SP_AWAY, True) and rep.check_specialty_trade_allowed(SP_AWAY, False))
buy_home = rep.get_resouce_price(SP_HOME, True)[0]
check("特产在产地按常规买入价（1.1 倍）买入，而不是 1.5 倍（#326）", buy_home == int(price_of(SP_HOME) * 1.1), buy_home)
sell_away = rep.get_resouce_price(SP_AWAY, False)[0]
check("异地特产按 1.5 倍卖出，而不是按 0.9 倍低价卖出（#326）", sell_away == int(price_of(SP_AWAY) * 1.5), sell_away)
check("特产运到异地卖出有差价可赚", sell_away > int(price_of(SP_AWAY) * 1.1))
check("非特产资源：买入 1.1 倍、卖出 0.9 倍", rep.get_resouce_price(NORMAL, True)[0] == int(price_of(NORMAL) * 1.1) and rep.get_resouce_price(NORMAL, False)[0] == int(price_of(NORMAL) * 0.9))

# ==== 3. 产地手动买入 ====
section("产地手动买入本地特产（面板）")
reset_market()
set_stock(1, 1000000)
set_stock(SP_HOME, 0)
panel = make_panel(SP_HOME)
err = run_panel(panel.draw, [" [ +10 ] ", BUY_OK])
check("面板流程不报错", err is None, repr(err))
check("数量调到 +10 后出现[确认买入]", BUY_OK in options(1), options(1))
check("买入 10 个：库存 +10", stock(SP_HOME) == 10, stock(SP_HOME))
check("龙门币恰好减少 单价×数量", money() == 1000000 - buy_home * 10, money())
check("预算区显示的剩余龙门币与实际一致", drawn(_("{0} - {1} = {2} 龙门币").format(1000000, buy_home * 10, 1000000 - buy_home * 10)))
check("成交提示里的龙门币与库存与实际一致", drawn(_("\n交易成功！\n当前龙门币数量：{0}({1})\n资源{2}数量：{3}/{4}({5})\n").format(
    money(), "-" + str(buy_home * 10), name_of(SP_HOME), 10, CAPACITY, "+10")))
check("成交后交易数量归零、面板返回场景", panel.quantity_of_resouce == 0 and cache.now_panel_id == constant.Panel.IN_SCENE)

section("产地不能卖出本地特产")
panel = make_panel(SP_HOME)
panel.settle_max_sell()
check("[最大卖出]对本地特产无效，数量仍为 0", panel.quantity_of_resouce == 0, panel.quantity_of_resouce)
panel.quantity_of_resouce = -5
err = run_panel(panel.draw, [SELL_OK])
check("面板流程不报错", err is None, repr(err))
check("库存足够也不出现[确认卖出]", SELL_OK not in options(0), options(0))
check("提示「本地特产只能买入」", warn_drawn(WARN_SP_ORIGIN))
check("perform_trade 拒绝在产地卖出特产", rep.perform_trade(SP_HOME, 5, False) is None and stock(SP_HOME) == 10)
panel = rep.Resource_Exchange_Line_Panel(W)
panel.show_resource_type_dict[_("特产")] = True
err = run_panel(panel.select_exchange_resouce, [f"\n{SP_HOME}"])
home_line = text_after(f" [{SP_HOME}]")
check("资源列表：本地特产只列买入价，不列卖出价", err is None and _("   买入:{0}龙门币/1单位 {1}").format(buy_home, "(0%)") in home_line and "卖出:" not in home_line, repr(err) + home_line)
check("资源列表：库存为 0 的异地特产不列出", f"\n{SP_OTHER}" not in options(0) and f"\n{SP_AWAY}" not in options(0))
check("资源列表：选中后切换交易资源", panel.now_select_resouce_id == SP_HOME)

# ==== 4. 大地图移动后在异地卖出 ====
section("大地图移动后手动卖出异地特产（#326）")
reset_market()
check("大地图抵达结算把所在地改成目的国", arrive_at(AWAY) and cache.rhodes_island.current_location[0] == AWAY, cache.rhodes_island.current_location)
sell_home_away = rep.get_resouce_price(SP_HOME, False)[0]
check("移动后炎国特产的卖出价为 1.5 倍", sell_home_away == int(price_of(SP_HOME) * 1.5), sell_home_away)
panel = rep.Resource_Exchange_Line_Panel(W)
panel.show_resource_type_dict[_("特产")] = True
err = run_panel(panel.select_exchange_resouce, [f"\n{SP_HOME}"])
home_line = text_after(f" [{SP_HOME}]")
check("资源列表：持有的异地特产列出，只列卖出价", err is None and _("   卖出:{0}龙门币/1单位 {1}\n").format(sell_home_away, "") in home_line and "买入:" not in home_line,
      repr(err) + home_line)
away_line = text_after(f" [{SP_AWAY}]")
check("资源列表：当地特产（库存为 0 也）列出，只列买入价", "买入:" in away_line and "卖出:" not in away_line, away_line)
money_before = money()
panel = make_panel(SP_HOME)
err = run_panel(panel.draw, [_("最大卖出"), SELL_OK])
check("面板流程不报错", err is None, repr(err))
check("[最大卖出]后出现[确认卖出]（#326：此前异地特产不出现卖出按钮）", SELL_OK in options(1), options(1))
check("卖出全部 10 个：库存归零", stock(SP_HOME) == 0, stock(SP_HOME))
check("龙门币恰好增加 1.5 倍单价×数量", money() == money_before + sell_home_away * 10, money() - money_before)
check("预算区显示的卖出后龙门币与实际一致", drawn(_("{0} + {1} = {2} 龙门币").format(money_before, sell_home_away * 10, money_before + sell_home_away * 10)))
check("本地特产不受影响：卡西米尔特产在卡西米尔能买、不能卖",
      rep.check_specialty_trade_allowed(SP_AWAY, True) and not rep.check_specialty_trade_allowed(SP_AWAY, False))

section("异地不能买入别处的特产")
money_before = money()
panel = make_panel(SP_HOME)
panel.settle_max_buy()
check("[最大买入]对异地特产无效，数量仍为 0", panel.quantity_of_resouce == 0, panel.quantity_of_resouce)
panel.quantity_of_resouce = 5
err = run_panel(panel.draw, [BUY_OK])
check("面板流程不报错", err is None, repr(err))
check("钱够也不出现[确认买入]", BUY_OK not in options(0), options(0))
check("提示「特产只能在产地买入」", warn_drawn(WARN_SP_NOT_ORIGIN))
check("perform_trade 拒绝在异地买入特产，资金库存不变", rep.perform_trade(SP_HOME, 5, True) is None and stock(SP_HOME) == 0 and money() == money_before)
panel = rep.Resource_Exchange_Line_Panel(W)
panel.show_resource_type_dict[_("特产")] = True
run_panel(panel.select_exchange_resouce, [])
check("卖光后，资源列表不再列出该异地特产", f"\n{SP_HOME}" not in options(0) and f"\n{SP_AWAY}" in options(0), options(0))

# ==== 5. 交易员加成 ====
section("交易员加成抬高特产卖价")
reset_market()
trader = make_character(TRADER, "交易员甲", work_type=111, position=["贸易", "资源交易所"])
trader.ability[40] = 10
basement.update_work_people()
check("岗位 111 的干员进入交易员名单", cache.rhodes_island.trade_operator_ids_list == [TRADER], cache.rhodes_island.trade_operator_ids_list)
panel = rep.Resource_Exchange_Line_Panel(W)
panel._do_assign_main_trader(type_of(SP_HOME), TRADER)
check("任命为特产的主交易员", cache.rhodes_island.resource_type_main_trader[type_of(SP_HOME)] == TRADER)
multiplier, main_bonus, _sub_bonus = rep.calculate_trade_multiplier(SP_HOME, False)
check("话术 10 级主交易员：卖出乘数 1.05", abs(multiplier - 1.05) < 1e-9 and abs(main_bonus - 0.05) < 1e-9, (multiplier, main_bonus))
sell_with_trader = rep.get_resouce_price(SP_HOME, False)[0]
check("异地特产卖价 = 1.5 倍 × 交易员乘数，没被当地不可用的买入价封顶", sell_with_trader == int(price_of(SP_HOME) * 1.5 * 1.05), sell_with_trader)
check("有交易员时的卖价高于没有交易员时", sell_with_trader > sell_home_away, (sell_with_trader, sell_home_away))
buy_away_trader = rep.get_resouce_price(SP_AWAY, True)[0]
check("产地特产买价同样享受交易员折扣", buy_away_trader == int(price_of(SP_AWAY) * 1.1 * 0.95) and buy_away_trader < int(price_of(SP_AWAY) * 1.1), buy_away_trader)
set_stock(SP_HOME, 10)
money_before = money()
panel = make_panel(SP_HOME)
err = run_panel(panel.draw, [_("最大卖出"), SELL_OK])
check("有交易员时手动卖出：按加成后的单价成交", err is None and stock(SP_HOME) == 0 and money() == money_before + sell_with_trader * 10, (repr(err), money() - money_before))
check("面板显示的卖出价就是成交价", any(text.startswith(_("卖出价: {0} 龙门币").format(sell_with_trader)) for text in drawn_text))

# ==== 6. 自动交易 ====
section("自动交易同样遵守特产买卖地点限制")
reset_market()
set_stock(SP_AWAY, 10)
set_stock(SP_HOME, 10)
set_stock(1, 1000000)
# 第一轮只开自动卖出（触发价 1%，价格条件必定满足），看卖出方向的地点限制
for res_id in (SP_AWAY, SP_HOME):
    rep._ensure_trade_setting(res_id).update({"sell_on": True, "sell_stock": 0, "sell_price_percent": 1})
price_sell_home = rep.get_resouce_price(SP_HOME, False)[0]
drawn_text.clear()
rep.auto_trade_resources()
check("当地特产不会被自动卖出", stock(SP_AWAY) == 10, stock(SP_AWAY))
check("异地特产自动卖出到保留库存", stock(SP_HOME) == 0, stock(SP_HOME))
check("自动卖出的龙门币变化恰好等于成交额", money() == 1000000 + price_sell_home * 10, money() - 1000000)
summary = "".join(drawn_text)
check("贸易部结算明细：只卖出了异地特产", _("  · 自动卖出{0} x {1}，单价{2}，总计{3}").format(name_of(SP_HOME), 10, price_sell_home, price_sell_home * 10) in summary
      and _("自动卖出{0}").format(name_of(SP_AWAY)) not in summary, summary[-300:])
# 第二轮只开自动买入（目标库存 20、触发价 300%，价格条件必定满足），看买入方向的地点限制
for res_id in (SP_AWAY, SP_HOME):
    rep._ensure_trade_setting(res_id).update({"sell_on": False, "buy_on": True, "buy_stock": 20, "buy_price_percent": 300})
set_stock(1, 1000000)
price_buy_away = rep.get_resouce_price(SP_AWAY, True)[0]
drawn_text.clear()
rep.auto_trade_resources()
check("当地特产自动买入到目标库存", stock(SP_AWAY) == 20, stock(SP_AWAY))
check("异地特产不会被自动买入", stock(SP_HOME) == 0, stock(SP_HOME))
check("自动买入的龙门币变化恰好等于成交额", money() == 1000000 - price_buy_away * 10, money() - 1000000)
summary = "".join(drawn_text)
check("贸易部结算明细：只买入了当地特产", _("  · 自动买入{0} x {1}，单价{2}，总计{3}").format(name_of(SP_AWAY), 10, price_buy_away, price_buy_away * 10) in summary
      and _("自动买入{0}").format(name_of(SP_HOME)) not in summary, summary[-300:])
rep._ensure_trade_setting(SP_HOME).update({"sell_on": True, "buy_on": False})
cache.rhodes_island.resource_type_main_trader[type_of(SP_HOME)] = 0
set_stock(SP_HOME, 10)
rep.auto_trade_resources()
check("没有任命主交易员的类型不执行自动交易", stock(SP_HOME) == 10)

# ==== 7. 普通资源的买卖不变式 ====
section("买卖不变式：资金、仓容与持有量")
reset_market()
trader.work.work_type = 0
basement.update_work_people()
check("撤掉岗位后交易员名单清空", cache.rhodes_island.trade_operator_ids_list == [])
buy_normal = rep.get_resouce_price(NORMAL, True)[0]
sell_normal = rep.get_resouce_price(NORMAL, False)[0]
set_stock(1, 2500)
set_stock(NORMAL, 0)
result = rep.perform_trade(NORMAL, 10, True)
check("钱不够时只买得起的数量成交", result is not None and result["quantity"] == 2500 // buy_normal and stock(NORMAL) == 2500 // buy_normal, result)
check("成交额 = 单价 × 实际数量，龙门币恰好减少成交额", result is not None and result["total_price"] == buy_normal * result["quantity"] and money() == 2500 - result["total_price"], money())
set_stock(1, 2500)
set_stock(NORMAL, 0)
panel = make_panel(NORMAL, 10)
err = run_panel(panel.draw, [BUY_OK])
check("钱不够时不出现[确认买入]，并提示龙门币不足", err is None and BUY_OK not in options(0) and warn_drawn(_("  ●龙门币不足，无法以当前数量买入")), (repr(err), options(0)))
check("面板未成交时资金与库存不变", money() == 2500 and stock(NORMAL) == 0)
panel = make_panel(NORMAL)
panel.settle_max_buy()
check("[最大买入] = 资金可负担量", panel.quantity_of_resouce == 2500 // buy_normal, panel.quantity_of_resouce)
set_stock(1, 1000000)
set_stock(NORMAL, CAPACITY - 3)
panel.settle_max_buy()
check("[最大买入] 不超过剩余仓容", panel.quantity_of_resouce == 3, panel.quantity_of_resouce)
panel.quantity_of_resouce = 0
panel.settle_quantity(" [ +100 ] ")
check("数量调节被钳制在剩余仓容内", panel.quantity_of_resouce == 3, panel.quantity_of_resouce)
result = rep.perform_trade(NORMAL, 10, True)
check("买入数量被截断到剩余仓容", result is not None and result["quantity"] == 3 and stock(NORMAL) == CAPACITY, result)
check("仓库已满时无法买入，资金不变", rep.perform_trade(NORMAL, 1, True) is None and money() == 1000000 - buy_normal * 3)
set_stock(NORMAL, 4)
panel = make_panel(NORMAL)
panel.settle_quantity(" [ -10 ] ")
check("卖出数量被钳制在持有量内", panel.quantity_of_resouce == -4, panel.quantity_of_resouce)
panel.quantity_of_resouce = -10
err = run_panel(panel.draw, [SELL_OK])
check("想卖的比持有的多时不出现[确认卖出]", err is None and SELL_OK not in options(0), (repr(err), options(0)))
money_before = money()
result = rep.perform_trade(NORMAL, 10, False)
check("卖出数量被截断到持有量，龙门币恰好增加成交额", result is not None and result["quantity"] == 4 and stock(NORMAL) == 0 and money() == money_before + sell_normal * 4, result)
check("没有库存时无法卖出", rep.perform_trade(NORMAL, 1, False) is None)
check("数量为 0 或负数的交易无效", rep.perform_trade(NORMAL, 0, True) is None and rep.perform_trade(NORMAL, -3, False) is None)
set_stock(CANT_BUY, 0)
panel = make_panel(CANT_BUY)
panel.settle_max_buy()
check("不可购买资源：[最大买入]无效", panel.quantity_of_resouce == 0)
panel.quantity_of_resouce = 5
err = run_panel(panel.draw, [BUY_OK])
check("不可购买资源：不出现[确认买入]并提示只能卖出", err is None and BUY_OK not in options(0) and warn_drawn(_("  ●该资源无法购买，只能卖出")), (repr(err), options(0)))
set_stock(CANT_BUY, 3)
money_before = money()
result = rep.perform_trade(CANT_BUY, 3, False)
check("不可购买资源照常能卖出", result is not None and result["quantity"] == 3 and money() == money_before + int(price_of(CANT_BUY) * 0.9) * 3, result)

section("供需随交易量变化")
reset_market()
set_stock(1, 10000000)
set_stock(NORMAL, 0)
rep.perform_trade(NORMAL, 100, True)
supply_after_buy = cache.rhodes_island.supply_demand_dict[NORMAL]
check("大宗买入推高供需系数与买入价", supply_after_buy > 1 and rep.get_resouce_price(NORMAL, True)[0] > buy_normal, supply_after_buy)
rep.perform_trade(NORMAL, 100, False)
check("大宗卖出压低供需系数", cache.rhodes_island.supply_demand_dict[NORMAL] < supply_after_buy, cache.rhodes_island.supply_demand_dict[NORMAL])
check("普通资源的买入价始终不低于卖出价", rep.get_resouce_price(NORMAL, True)[0] >= rep.get_resouce_price(NORMAL, False)[0])
check("今日交易量累计了买卖两笔", cache.rhodes_island.today_trade_resource_count[NORMAL] == 200, cache.rhodes_island.today_trade_resource_count[NORMAL])

finish()
