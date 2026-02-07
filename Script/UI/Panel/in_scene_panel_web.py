# -*- coding: utf-8 -*-
"""
Web模式主场景面板
用于Web绘制模式的图形化交互界面

此文件是tk模式 in_scene_panel.py 的Web版本替代
在 config.ini 中 web_draw = 1 时使用
"""

from types import FunctionType
from typing import Dict, List, Optional
from Script.Core import (
    get_text,
    cache_control,
    game_type,
    flow_handle,
    constant,
)
from Script.Design import attr_text, map_handle, game_time, handle_premise
from Script.Config import game_config
from Script.UI.Panel.web_components import (
    SceneRenderer,
    CharacterRenderer,
    InteractionHandler,
    DialogBox,
    StatusPanel,
    TabMenu,
    BodyPartButton,
    MAIN_PANEL_TAB_ID,
)

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

# 特殊的刷新指令ID，用于在指令执行后触发面板刷新
WEB_REFRESH_SIGNAL = "__WEB_REFRESH__"


class InScenePanelWeb:
    """
    Web模式场景交互界面面板
    负责收集和组织所有需要发送到前端的数据
    
    Keyword arguments:
    width -- 绘制宽度（保留兼容性，Web模式不使用）
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        
        # 初始化各组件
        self.scene_renderer = SceneRenderer()
        self.character_renderer = CharacterRenderer()
        self.interaction_handler = InteractionHandler()
        self.dialog_box = DialogBox()
        self.status_panel = StatusPanel()
        self.tab_menu = TabMenu()
        self.body_part_button = BodyPartButton()
        
        # 状态缓存（用于增量更新）
        self._last_state: Dict = {}
        
        # 当前交互对象ID
        self._current_target_id: int = -1

    def draw(self):
        """
        绘制对象
        在Web模式下，此方法收集数据并通过WebSocket推送到前端
        """
        from Script.Core import io_init
        from Script.System.Instruct_System import handle_instruct as instruct_handler
        
        # 在进入主界面循环前，彻底清空屏幕和历史记录
        # 这样可以避免显示之前的杂乱信息，保持主界面整洁
        io_init.clear_screen_and_history()
        
        while True:
            if cache.now_panel_id != constant.Panel.IN_SCENE:
                break
            
            # 每次主循环迭代时，确保选项卡状态与当前面板一致
            # 当从其他面板返回时，cache.now_panel_id 为 IN_SCENE，
            # 此时应将选项卡设置为主面板
            if not self.tab_menu.is_main_panel_active():
                self.tab_menu.set_active_tab(MAIN_PANEL_TAB_ID)
            
            # 清屏（Web模式），但保留历史记录用于循环内的更新
            io_init.clear_screen()
            io_init.clear_order()
            
            # 收集当前游戏状态
            game_state = self._collect_game_state()
            
            # 注意：由于前端 renderNewUIContent() 每次都完全重新渲染UI，
            # 增量更新会导致缺失字段的UI组件不被渲染。
            # 因此这里始终发送完整状态，确保所有UI组件都能正确显示。
            # 如果将来前端支持增量合并更新，可以重新启用增量计算。
            
            # 检查是否需要完整刷新（如切换交互对象后）
            if getattr(cache, 'web_need_full_refresh', False):
                # 清除刷新标志
                cache.web_need_full_refresh = False
                # 清除上次状态缓存
                self._last_state = {}
            
            # 始终发送完整状态
            self._push_state_to_frontend(game_state)
            
            # 更新缓存（用于未来可能的增量优化）
            self._last_state = game_state.copy()
            
            # 绑定面板选项卡指令并等待用户选择
            ask_list = self._bind_panel_tabs_and_get_ask_list()
            
            # 等待前端输入（通过按钮点击）
            flow_handle.askfor_all(ask_list)
    
    def _bind_panel_tabs_and_get_ask_list(self) -> List[str]:
        """
        绑定面板选项卡指令并返回可选列表
        
        对于主面板选项卡，绑定返回主面板的处理函数
        对于其他面板选项卡，绑定对应的指令处理函数
        同时添加刷新信号到列表，用于在交互指令执行后触发面板刷新
        
        Returns:
        List[str] -- 可选择的指令ID列表
        """
        from Script.System.Instruct_System import handle_instruct as instruct_handler
        
        ask_list = []
        tabs = self.tab_menu.get_panel_tabs()
        
        for tab in tabs:
            if tab.get("available", True):
                tab_id = tab["id"]
                ask_list.append(tab_id)
                
                if tab_id == MAIN_PANEL_TAB_ID:
                    # 主面板选项卡：绑定返回主面板的处理函数
                    flow_handle.bind_cmd(
                        tab_id,
                        self._handle_return_to_main_panel,
                        ()
                    )
                else:
                    # 其他面板选项卡：绑定对应的指令处理函数
                    flow_handle.bind_cmd(
                        tab_id,
                        instruct_handler.handle_instruct,
                        (tab_id,)
                    )
        
        # 添加刷新信号到列表，用于在交互指令执行后触发面板刷新
        # 该信号由 web_server.py 的 handle_execute_instruct 设置
        ask_list.append(WEB_REFRESH_SIGNAL)
        # 绑定空处理函数，仅用于让 askfor_all 返回并触发下一次循环
        flow_handle.bind_cmd(WEB_REFRESH_SIGNAL, self._handle_refresh_signal, ())
        
        return ask_list

    def _handle_refresh_signal(self):
        """
        处理刷新信号
        
        当交互指令执行完成后，此信号被触发以刷新面板数据
        此函数不需要做任何事情，只需让主循环继续即可
        """
        pass

    def _handle_return_to_main_panel(self):
        """
        处理返回主面板的操作
        
        将 cache.now_panel_id 重置为 IN_SCENE，使主循环继续在本面板运行
        """
        # 重置面板ID到主场景面板
        cache.now_panel_id = constant.Panel.IN_SCENE
        # 更新选项卡状态
        self.tab_menu.set_active_tab(MAIN_PANEL_TAB_ID)

    def _collect_game_state(self) -> Dict:
        """
        收集当前游戏状态数据
        
        Returns:
        Dict -- 完整的游戏状态数据
        """
        # 获取玩家数据
        pl_character_data: game_type.Character = cache.character_data[0]
        
        # 获取当前交互对象
        target_id = pl_character_data.target_character_id
        self._current_target_id = target_id
        
        # 构建游戏状态
        state = {
            # 场景信息栏（场景名+游戏时间）
            "scene_info_bar": self._get_scene_info_bar(),
            
            # 场景信息
            "scene": self.scene_renderer.get_scene_background(),
            
            # 玩家信息
            "player_info": self.status_panel.get_player_info(),
            
            # 交互对象信息
            "target_info": self._get_target_info(target_id),
            
            # 交互对象附加信息
            "target_extra_info": self.status_panel.get_target_extra_info(target_id),
            
            # 场景内其他角色
            "scene_characters": self._get_scene_characters(),
            
            # 可用交互类型
            "interaction_types": self.interaction_handler.get_interaction_types(),
            
            # 面板选项卡
            "panel_tabs": self.tab_menu.get_panel_tabs(),
            
            # 对话框状态
            "dialog": self.dialog_box.get_state(),
            
            # 当前交互类型和可用部位
            "current_interaction_type": self.interaction_handler.current_interaction_type,
            "available_body_parts": self.interaction_handler.available_body_parts,
        }
        
        return state

    def _get_scene_info_bar(self) -> Dict:
        """
        获取场景信息栏数据（顶部信息栏，显示场景名和游戏时间）
        
        Returns:
        Dict -- 场景信息栏数据，包含 scene_name 和 game_time
        """
        # 获取玩家数据
        pl_character_data: game_type.Character = cache.character_data[0]
        
        # 获取当前位置/场景名
        position_text = attr_text.get_scene_path_text(pl_character_data.position)
        if handle_premise.handle_place_door_close(0):
            position_text += _("(锁)")
        scene_name = _("当前位置:") + position_text
        
        # 获取游戏时间信息
        year_text = game_time.get_year_text()
        month_text = game_time.get_month_text()
        day_time_text = game_time.get_day_and_time_text()
        week_day_text = game_time.get_week_day_text()
        
        # 获取时段信息
        sun_time = game_time.get_sun_time(cache.game_time)
        sun_time_config = game_config.config_sun_time[sun_time]
        sun_time_text = sun_time_config.name
        
        # 判断是否是饭点
        if handle_premise.handle_eat_time(0):
            sun_time_text += _("(饭点)")
        
        # 判断是工作日还是休息日
        is_work_day = game_time.judge_work_today(0)
        work_rest_text = _("工作日") if is_work_day else _("休息")
        
        # 组合时间文本
        time_text = f"{year_text} {month_text} {day_time_text} {week_day_text} {sun_time_text} {work_rest_text}"
        
        return {
            "scene_name": scene_name,
            "game_time": time_text,
        }

    def _get_target_info(self, target_id: int) -> Dict:
        """
        获取交互对象的完整信息
        
        Keyword arguments:
        target_id -- 交互对象ID
        
        Returns:
        Dict -- 交互对象信息
        """
        if target_id < 0:
            return {}
        
        # 基础信息
        basic_info = self.status_panel.get_target_info(target_id)
        
        # 图像数据
        image_data = self.character_renderer.get_character_image_data(target_id)
        
        # 合并数据
        basic_info["image_data"] = image_data
        
        return basic_info

    def _get_scene_characters(self) -> List[Dict]:
        """
        获取场景内其他角色的头像信息
        
        Returns:
        List[Dict] -- 角色头像信息列表
        """
        # 排除玩家(0)和当前交互对象
        exclude_ids = [0]
        if self._current_target_id >= 0:
            exclude_ids.append(self._current_target_id)
        
        return self.character_renderer.get_scene_characters_avatars(exclude_ids)

    def _calculate_diff(self, new_state: Dict) -> Dict:
        """
        计算状态差异，用于增量更新
        
        Keyword arguments:
        new_state -- 新的游戏状态
        
        Returns:
        Dict -- 差异数据（仅包含变化的部分）
        """
        if not self._last_state:
            # 首次更新，返回完整状态
            return new_state
        
        diff = {}
        
        for key, new_value in new_state.items():
            old_value = self._last_state.get(key)
            
            # 简单比较，如果不同则包含在diff中
            if new_value != old_value:
                diff[key] = new_value
        
        return diff

    def _push_state_to_frontend(self, state: Dict):
        """
        推送状态到前端
        
        Keyword arguments:
        state -- 要推送的状态数据
        """
        if not state:
            return
        
        try:
            # 将新UI数据转换为前端可以渲染的元素列表
            elements = self._convert_state_to_elements(state)
            # 添加到 cache.current_draw_elements，让 askfor_all 统一发送
            if not hasattr(cache, 'current_draw_elements') or cache.current_draw_elements is None:
                cache.current_draw_elements = []
            cache.current_draw_elements.extend(elements)
        except Exception as e:
            # 如果推送失败，记录错误但不中断游戏
            import logging
            logging.error(f"推送游戏状态失败: {e}")
    
    def _convert_state_to_elements(self, state: Dict) -> List[Dict]:
        """
        将游戏状态转换为前端可渲染的元素列表
        
        Keyword arguments:
        state -- 游戏状态数据
        
        Returns:
        List[Dict] -- 可渲染的元素列表
        """
        elements = []
        
        # 添加新UI容器元素，包含完整的游戏状态
        # 前端会检测到这个特殊类型并使用新的渲染方式
        elements.append({
            "type": "new_ui_container",
            "panel_type": "in_scene",
            "game_state": state
        })
        
        return elements

    def handle_body_part_click(self, part_name: str) -> Dict:
        """
        处理身体部位点击
        
        Keyword arguments:
        part_name -- 部位名称
        
        Returns:
        Dict -- 响应数据（包含可执行的指令列表）
        """
        result = self.interaction_handler.click_body_part(part_name)
        return result

    def handle_target_switch(self, character_id: int):
        """
        处理交互对象切换
        
        Keyword arguments:
        character_id -- 新的交互对象ID
        """
        pl_character_data: game_type.Character = cache.character_data[0]
        pl_character_data.target_character_id = character_id
        self._current_target_id = character_id
        
        # 清除当前交互状态
        self.interaction_handler.clear_selection()
        self.body_part_button.clear()

    def clear_cache(self):
        """清除所有缓存"""
        self._last_state = {}
        self.scene_renderer.clear_cache()
        self.character_renderer.clear_cache()
        self.interaction_handler.clear_selection()
        self.body_part_button.clear()
