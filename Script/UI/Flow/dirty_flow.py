from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import dirty_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.DIRTY)
def dirty_flow():
    """污浊面板"""
    now_panel = dirty_panel.Dirty_Panel(width)
    now_panel.draw()
