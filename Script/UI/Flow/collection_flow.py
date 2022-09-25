from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import collection_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.COLLECTION)
def collection_flow():
    """收藏品面板"""
    now_panel = collection_panel.Collection_Panel(width)
    now_panel.draw()
