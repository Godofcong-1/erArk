from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import undress_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.UNDRESS)
def undress_flow():
    """脱衣服面板"""
    now_panel = undress_panel.Undress_Panel(width)
    now_panel.draw()
