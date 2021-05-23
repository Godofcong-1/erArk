from Script.Core import constant
from Script.Design import handle_panel
from Script.Config import normal_config
from Script.UI.Panel import see_map_panel

width: int = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.SEE_MAP)
def see_map_flow():
    """查看地图面板"""
    now_panel = see_map_panel.SeeMapPanel(width)
    now_panel.draw()
