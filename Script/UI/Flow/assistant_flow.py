from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import assistant_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.ASSISTANT)
def assistant_flow():
    """助理面板"""
    now_panel = assistant_panel.Assistant_Panel(width)
    now_panel.draw()
