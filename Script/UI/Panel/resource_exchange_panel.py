from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config

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
        self.show_resource_type_dict: Dict = {"材料": False, "药剂": False, "乳制品": False, "香水": False}
        """ 显示的资源类型 """

    def draw(self):
        """绘制对象"""

        title_text = _("资源交易")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        self.now_select_resouce_id = 11
        self.buy_or_sell_flag = True # True为买入，False为卖出
        self.quantity_of_resouce = 0

        while 1:
            return_list = []
            title_draw.draw()

            # 绘制交易信息
            all_info_draw = draw.NormalDraw()
            now_text = ""
            money = cache.rhodes_island.materials_resouce[1]
            now_text += _(f"\n  当前龙门币数量    ：{money}")

            resouce_data  = game_config.config_resouce[self.now_select_resouce_id]
            now_resouce_stock = cache.rhodes_island.materials_resouce[self.now_select_resouce_id]
            warehouse_capacity = cache.rhodes_island.warehouse_capacity
            now_text += _(f"\n\n  要交易的资源为    ：{resouce_data.name}({now_resouce_stock}/{warehouse_capacity})    ")
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
                _(f"{button_text}"),
                len(button_text) * 2,
                cmd_func=self.select_exchange_resouce,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            all_info_draw.text = _(f"\n\n  要交易的数量为    ：{self.quantity_of_resouce}    ")
            all_info_draw.draw()

            # 绘制数量变更按钮
            button_text_list = [" [-100] ", " [-10] ", " [-1] ", " [+1] ", " [+10] ", " [+100] "]
            for button_text in button_text_list:
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(f"{button_text}"),
                    len(button_text) * 2,
                    cmd_func=self.settle_quantity,
                    args=(button_text, ),
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

            button_text = _(" [重置] ")
            button_draw = draw.CenterButton(
                _(button_text),
                _(f"{button_text}"),
                len(button_text) * 2,
                cmd_func=self.reset_quantity,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            # 显示价格
            price = resouce_data.price
            price = 1.2 * price if self.buy_or_sell_flag else 0.8 * price
            price = int(price)
            all_info_draw.text = _(f"\n\n  交易的价格为      ：")
            all_info_draw.draw()

            # 绘制买入还是卖出的按钮
            button_text = _(" [买入] ") if self.buy_or_sell_flag else _(" [卖出] ")
            button_draw = draw.CenterButton(
                _(button_text),
                _(f"{button_text}"),
                len(button_text) * 2,
                cmd_func=self.settle_buy_or_sell,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            # 无法买入的，不显示价格
            if (self.buy_or_sell_flag and not cant_buy_flag) or not self.buy_or_sell_flag:
                all_info_draw.text = _(f" {price}龙门币/1单位 ")
                all_info_draw.draw()
            line_feed.draw()

            # 输出总价
            if self.buy_or_sell_flag:
                all_info_draw.text = _(f"\n  ○预计共花费{price} * {self.quantity_of_resouce} = {price * self.quantity_of_resouce}龙门币\n")
                if price * self.quantity_of_resouce > money:
                    all_info_draw.text += _("  ●龙门币不足，无法购买\n")
                # 如果是不可购买的则显示提示
                if cant_buy_flag:
                    all_info_draw.text = _("\n  ●该资源无法购买，只能卖出\n")
            else:
                all_info_draw.text = _(f"\n  ○预计共获得{price} * {self.quantity_of_resouce} = {price * self.quantity_of_resouce}龙门币\n")
                if self.quantity_of_resouce > now_resouce_stock:
                    all_info_draw.text += _("  ●资源不足，无法出售\n")
            all_info_draw.draw()

            line_feed.draw()
            # 以下情况不绘制确定按钮
            # 买入，且钱不足
            # 买入，但是该资源不可买入
            # 卖出，且资源不足
            if (
                (self.buy_or_sell_flag and price * self.quantity_of_resouce > money) or 
                (self.buy_or_sell_flag and cant_buy_flag) or
                (not self.buy_or_sell_flag and self.quantity_of_resouce > now_resouce_stock)
                ):
                pass
            else:
                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), window_width/2)
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width/2)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break
            elif yrn == yes_draw.return_text:
                if self.buy_or_sell_flag:
                    cache.rhodes_island.materials_resouce[self.now_select_resouce_id] += self.quantity_of_resouce
                    cache.rhodes_island.materials_resouce[1] -= price * self.quantity_of_resouce
                else:
                    cache.rhodes_island.materials_resouce[self.now_select_resouce_id] -= self.quantity_of_resouce
                    cache.rhodes_island.materials_resouce[1] += price * self.quantity_of_resouce
                break


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

                info_text = _(f"当前的交易资源为：{resouce_now_data.name}")
                info_text += _("\n当前可以交易的资源有：\n")
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()

                # 遍历全资源类型
                resouce_list = ["材料", "药剂", "乳制品", "香水"]
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
                            button_draw = draw.LeftButton(
                            f" [{str(resouce_id).rjust(3,'0')}]{resouce_data.name}：{resouce_data.info}",
                            f"\n{resouce_id}",
                            window_width ,
                            cmd_func=self.settle_now_select_resouce_id,
                            args=(resouce_id)
                            )
                            button_draw.draw()
                            return_list.append(button_draw.return_text)

                            now_text = _(f"\n      当前存量：{cache.rhodes_island.materials_resouce[resouce_id]}/{cache.rhodes_island.warehouse_capacity}")
                            # 判断是否可以买入卖出
                            if resouce_data.cant_buy == 0:
                                now_text += _(f"   买入:{int(resouce_data.price * 1.2)}龙门币/1单位")
                            now_text += _(f"   卖出:{int(resouce_data.price * 0.8)}龙门币/1单位\n")
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
        if self.now_select_resouce_id == 12 or resouce_data.type == "药剂":
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
