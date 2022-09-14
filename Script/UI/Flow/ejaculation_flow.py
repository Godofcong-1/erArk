from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import ejaculation_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.EJACULATION)
def ejaculation_flow():
    """射精面板"""
    now_panel = ejaculation_panel.Ejaculation_Panel(width)
    now_panel.draw()
