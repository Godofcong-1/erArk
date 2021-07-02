from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import make_food_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.MAKE_FOOD)
def make_food_flow():
    """食物商店面板"""
    now_panel = make_food_panel.Make_food_Panel(width)
    now_panel.draw()
