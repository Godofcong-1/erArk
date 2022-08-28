from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import see_item_info_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.ITEM)
def see_item_info_flow():
    """道具栏面板"""
    now_panel = see_item_info_panel.SeeCharacterItemBagPanel(0,width)
    now_panel.draw()
