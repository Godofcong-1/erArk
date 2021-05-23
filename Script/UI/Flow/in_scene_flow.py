from Script.Core import constant
from Script.Design import handle_panel
from Script.Config import normal_config
from Script.UI.Panel import in_scene_panel


width: int = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.IN_SCENE)
def in_scene_flow():
    """场景互动面板"""
    now_panel = in_scene_panel.InScenePanel(width)
    now_panel.draw()
