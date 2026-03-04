# -*- coding: utf-8 -*-
"""
选项卡菜单组件
负责处理Web模式下的面板选项卡栏

选项卡类型说明：
1. 主面板选项卡（active）：当前正在显示的主面板
2. 系统面板类选项卡：所有满足前提条件的系统面板类指令
3. 临时选项卡：非主面板显示时，自动添加的当前面板选项卡

选项卡样式采用网页选项卡形式，当前选项卡高亮显示

注意：
- 系统面板类指令通过 web_category (InstructCategory.SYSTEM_PANEL) 判断，而非指令类型
- 只有满足所有前提条件的指令才会显示，不满足则不出现（而非禁用）
- 子面板模式下，其他选项卡会变灰且不可点击
"""

from typing import List, Dict, Set, Any, Union, Optional
from Script.Core import cache_control, game_type, constant
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache

# 主面板选项卡标识
MAIN_PANEL_TAB_ID = "__main_panel__"
MAIN_PANEL_TAB_NAME = "主面板"


def filter_instructs_by_premise(instruct_ids: Union[List, Set]) -> List[str]:
    """
    过滤指令列表，只返回满足所有前提条件的指令
    
    这是一个通用的前提条件过滤函数，可在任何需要判断指令前提的地方使用。
    
    Keyword arguments:
    instruct_ids -- 指令ID列表或集合（可以是字符串或整数ID）
    
    Returns:
    List[str] -- 满足所有前提条件的指令ID列表
    """
    result = []
    premise_cache: Dict[str, Any] = {}  # 本次调用的前提缓存
    
    for instruct_id in instruct_ids:
        # 确保 instruct_id 是字符串
        instruct_id_str = str(instruct_id) if not isinstance(instruct_id, str) else instruct_id
        if _check_single_instruct_premise(instruct_id_str, premise_cache):
            result.append(instruct_id_str)
    # print(f"debug : 满足前提条件的指令列表：{result}")
    return result


def _check_single_instruct_premise(instruct_id: str, premise_cache: Dict[str, Any]) -> bool:
    """
    检查单个指令的前提条件是否满足
    
    Keyword arguments:
    instruct_id -- 指令ID
    premise_cache -- 前提条件判断结果缓存（用于优化重复判断）
    
    Returns:
    bool -- 是否满足所有前提条件
    """
    # 如果没有前提条件，则视为满足
    if instruct_id not in constant.instruct_premise_data:
        return True
    # 如果当前是debug模式，跳过前提条件检查
    if handle_premise.handle_debug_mode_on(0):
        return True
    
    premises = constant.instruct_premise_data[instruct_id]
    
    for premise in premises:
        # 使用缓存优化重复判断
        if premise in premise_cache:
            if not premise_cache[premise]:
                return False
        else:
            result = handle_premise.handle_premise(premise, 0)
            premise_cache[premise] = result
            if not result:
                # print(f"debug : 指令 {instruct_id} 不满足前提条件 {premise}")
                return False
    
    return True


class TabMenu:
    """
    选项卡菜单管理器
    负责管理面板类指令的选项卡显示
    
    选项卡包含：
    - 主面板作为当前激活的选项卡
    - 所有满足条件的系统面板类指令作为可切换的选项卡
    - 子面板模式下，当前面板作为临时选项卡显示（如果不在已有选项卡中）
    """

    def __init__(self):
        """初始化选项卡菜单管理器"""
        # 当前激活的选项卡ID，默认为主面板
        self._active_tab: str = MAIN_PANEL_TAB_ID

    def get_panel_tabs(self) -> List[dict]:
        """
        获取所有面板类选项卡
        
        选项卡来源：
        1. 主面板（始终存在）
        2. 所有满足前提条件的系统面板类指令
        3. 子面板模式下，当前面板作为临时选项卡（如果不在已有选项卡中）
        
        子面板模式行为：
        - 其他选项卡变灰（disabled: True）且不可点击
        - 当前面板（临时或已有）亮起但也不可点击
        
        Returns:
        List[dict] -- 选项卡信息列表，每个元素包含：
            - id: 选项卡ID（主面板为 __main_panel__，其他为指令ID）
            - name: 选项卡显示名称
            - type: 选项卡类型（"main", "panel", "temp"）
            - available: 是否可用（子面板模式下其他选项卡为False）
            - active: 是否为当前激活的选项卡
            - disabled: 是否禁用（变灰）
        """
        tabs = []
        
        # 检查是否处于子面板模式
        sub_panel_mode = getattr(cache, 'web_sub_panel_mode', False)
        sub_panel_id = getattr(cache, 'web_sub_panel_id', None)
        sub_panel_name = getattr(cache, 'web_sub_panel_name', '')
        
        # 1. 添加主面板选项卡（始终存在）
        main_tab = {
            "id": MAIN_PANEL_TAB_ID,
            "name": MAIN_PANEL_TAB_NAME,
            "type": "main",
            "available": not sub_panel_mode,  # 子面板模式下不可用
            "active": self._active_tab == MAIN_PANEL_TAB_ID and not sub_panel_mode,
            "disabled": sub_panel_mode,  # 子面板模式下变灰
        }
        tabs.append(main_tab)
        
        # 2. 获取所有满足条件的系统面板类指令
        panel_instructs = self._get_available_system_panel_instructs()
        
        # 记录是否已经找到当前子面板在已有选项卡中
        found_sub_panel_in_tabs = False
        
        for instruct_info in panel_instructs:
            is_current_sub_panel = sub_panel_mode and instruct_info["id"] == sub_panel_id
            if is_current_sub_panel:
                found_sub_panel_in_tabs = True
            
            tab = {
                "id": instruct_info["id"],
                "name": instruct_info["name"],
                "type": "panel",
                # 子面板模式下：当前面板可用但不可点击（在前端处理），其他面板不可用
                "available": not sub_panel_mode or is_current_sub_panel,
                "active": is_current_sub_panel or (self._active_tab == instruct_info["id"] and not sub_panel_mode),
                "disabled": sub_panel_mode and not is_current_sub_panel,  # 子面板模式下非当前面板变灰
            }
            tabs.append(tab)
        
        # 3. 如果处于子面板模式且当前面板不在已有选项卡中，添加临时选项卡
        if sub_panel_mode and not found_sub_panel_in_tabs and sub_panel_id:
            temp_tab = {
                "id": sub_panel_id,
                "name": sub_panel_name or sub_panel_id,
                "type": "temp",  # 临时选项卡
                "available": True,  # 可用但不可点击（在前端处理）
                "active": True,  # 当前激活
                "disabled": False,  # 不变灰（是当前面板）
            }
            tabs.append(temp_tab)
        
        return tabs

    def _get_available_system_panel_instructs(self) -> List[dict]:
        """
        获取所有满足条件的系统面板类指令
        
        系统面板类指令判断依据：
        - 通过 instruct_meta.get_panel_instructs_from_constant() 获取所有 web_category 为 SYSTEM_PANEL 的指令
        - 只返回满足所有前提条件的指令（不满足则不显示，而非禁用）
        
        Returns:
        List[dict] -- 指令信息列表（只包含满足前提条件的指令）
        """
        from Script.System.Instruct_System import instruct_meta
        
        result = []
        
        # 通过 web_category 获取所有系统面板类指令（而非遍历所有系统类型指令）
        all_panel_instructs = instruct_meta.get_panel_instructs_from_constant()
        
        # 过滤出满足所有前提条件的指令
        available_instructs = filter_instructs_by_premise(all_panel_instructs)
        
        for instruct_id in available_instructs:
            # 检查是否有对应的面板ID（没有面板ID的系统面板指令不显示）
            panel_id = constant.instruct_panel_id_data.get(instruct_id, None)
            if panel_id is None:
                continue
            
            # 获取指令名称
            name = constant.handle_instruct_name_data.get(instruct_id, instruct_id)
            
            result.append({
                "id": instruct_id,
                "name": name,
                "available": True,  # 能出现在这里的都是满足前提条件的
                "panel_id": panel_id,
            })
        # print(f"debug : 可用的系统面板类指令列表：{result}")
        
        return result

    def set_active_tab(self, tab_id: str):
        """
        设置当前激活的选项卡
        
        Keyword arguments:
        tab_id -- 选项卡ID
        """
        self._active_tab = tab_id

    def get_active_tab(self) -> str:
        """
        获取当前激活的选项卡
        
        Returns:
        str -- 当前激活的选项卡ID
        """
        return self._active_tab

    def is_main_panel_active(self) -> bool:
        """
        判断主面板是否为当前激活的选项卡
        
        Returns:
        bool -- 主面板是否激活
        """
        return self._active_tab == MAIN_PANEL_TAB_ID

    def get_state(self) -> dict:
        """
        获取选项卡菜单状态
        
        注：前提条件判断现在在 filter_instructs_by_premise() 中每次都使用新缓存，
        确保使用最新数据，无需额外清除缓存操作。
        
        Returns:
        dict -- 选项卡菜单状态数据
        """
        return {
            "tabs": self.get_panel_tabs(),
            "active_tab": self._active_tab,
            "is_main_panel": self.is_main_panel_active(),
            "sub_panel_mode": getattr(cache, 'web_sub_panel_mode', False),
        }


def enter_sub_panel_mode(panel_id: str, panel_name: str = ""):
    """
    进入子面板模式
    
    在主界面内显示非主面板时调用，设置子面板模式的相关状态。
    
    Keyword arguments:
    panel_id -- 子面板的指令ID
    panel_name -- 子面板的名称（用于临时选项卡显示，默认使用panel_id）
    """
    cache.web_sub_panel_mode = True
    cache.web_sub_panel_id = panel_id
    cache.web_sub_panel_name = panel_name or panel_id


def exit_sub_panel_mode():
    """
    退出子面板模式
    
    从子面板返回主面板时调用，清除子面板模式的相关状态。
    """
    cache.web_sub_panel_mode = False
    cache.web_sub_panel_id = None
    cache.web_sub_panel_name = ""


def is_in_sub_panel_mode() -> bool:
    """
    检查是否处于子面板模式
    
    Returns:
    bool -- 是否处于子面板模式
    """
    return getattr(cache, 'web_sub_panel_mode', False)
