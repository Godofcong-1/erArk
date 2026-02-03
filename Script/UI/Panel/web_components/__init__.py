# -*- coding: utf-8 -*-
"""
Web模式专用UI组件包
用于Web绘制模式的图形化界面渲染

包含组件：
- scene_renderer: 场景背景渲染组件
- character_renderer: 角色图像渲染组件
- interaction_handler: 交互处理组件
- dialog_box: 对话框组件
- status_panel: 状态面板组件
- tab_menu: 选项卡菜单组件
- body_part_button: 身体部位按钮组件
- settlement_manager: 结算阶段管理组件
"""

from Script.UI.Panel.web_components.scene_renderer import SceneRenderer
from Script.UI.Panel.web_components.character_renderer import CharacterRenderer
from Script.UI.Panel.web_components.interaction_handler import InteractionHandler
from Script.UI.Panel.web_components.dialog_box import (
    DialogBox,
    add_dialog_text,
    advance_dialog,
    hide_dialog,
    clear_dialog_queue,
    get_dialog_state,
    skip_all_dialogs,
)
from Script.UI.Panel.web_components.status_panel import StatusPanel
from Script.UI.Panel.web_components.tab_menu import TabMenu, MAIN_PANEL_TAB_ID
from Script.UI.Panel.web_components.body_part_button import BodyPartButton
from Script.UI.Panel.web_components.settlement_manager import SettlementManager, SettlementPhase
