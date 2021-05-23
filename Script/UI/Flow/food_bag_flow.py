from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import food_bag_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.FOOD_BAG)
def food_bag_flow():
    """食物商店面板"""
    now_panel = food_bag_panel.FoodBagPanel(width)
    now_panel.draw()
