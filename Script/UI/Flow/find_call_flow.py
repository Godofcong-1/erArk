from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import find_call_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.FIND_CALL)
def find_call():
    """查找与召集面板"""
    now_panel = find_call_panel.Find_call_Panel(width)
    now_panel.draw()
