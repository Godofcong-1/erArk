from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import building_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.BUILDING)
def building_flow():
    """基建面板"""
    now_panel = building_panel.Building_Panel(width)
    now_panel.draw()
