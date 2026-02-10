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
- image_processor: 图片处理组件（透明区域裁切和缓存）
"""

from Script.System.Web_Draw_System.scene_renderer import SceneRenderer
from Script.System.Web_Draw_System.character_renderer import CharacterRenderer
from Script.System.Web_Draw_System.interaction_handler import InteractionHandler
from Script.System.Web_Draw_System.dialog_box import (
    DialogBox,
    add_dialog_text,
    advance_dialog,
    hide_dialog,
    clear_dialog_queue,
    get_dialog_state,
    skip_all_dialogs,
)
from Script.System.Web_Draw_System.status_panel import StatusPanel
from Script.System.Web_Draw_System.tab_menu import TabMenu, MAIN_PANEL_TAB_ID
from Script.System.Web_Draw_System.body_part_button import BodyPartButton
from Script.System.Web_Draw_System.settlement_manager import SettlementManager, SettlementPhase
from Script.System.Web_Draw_System.image_processor import (
    ImageProcessor,
    image_processor,
    get_cropped_image,
    clear_image_cache,
    is_image_processor_available,
)
