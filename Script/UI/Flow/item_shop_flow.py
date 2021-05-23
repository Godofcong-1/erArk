from Script.Core import constant
from Script.UI.Panel import item_shop_panel
from Script.Config import normal_config
from Script.Design import handle_panel

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.ITEM_SHOP)
def item_shop_flow():
    """道具商店面板"""
    now_panel = item_shop_panel.ItemShopPanel(width)
    now_panel.draw()
