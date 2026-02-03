# -*- coding: utf-8 -*-
"""
选项卡菜单组件
负责处理Web模式下的面板选项卡栏

选项卡类型说明：
1. 主面板选项卡（active）：当前正在显示的主面板
2. 系统面板类选项卡：所有满足前提条件的系统面板类指令

选项卡样式采用网页选项卡形式，当前选项卡高亮显示

注意：
- 系统面板类指令通过 web_category (InstructCategory.SYSTEM_PANEL) 判断，而非指令类型
- 只有满足所有前提条件的指令才会显示，不满足则不出现（而非禁用）
"""

from typing import List, Dict, Set, Any, Union
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
    """

    def __init__(self):
        """初始化选项卡菜单管理器"""
        # 当前激活的选项卡ID，默认为主面板
        self._active_tab: str = MAIN_PANEL_TAB_ID

    def get_panel_tabs(self) -> List[dict]:
        """
        获取所有面板类选项卡
        
        选项卡来源：
        1. 主面板（始终存在，默认激活）
        2. 所有满足前提条件的系统面板类指令
        
        Returns:
        List[dict] -- 选项卡信息列表，每个元素包含：
            - id: 选项卡ID（主面板为 __main_panel__，其他为指令ID）
            - name: 选项卡显示名称
            - type: 选项卡类型（"main" 或 "panel"）
            - available: 是否可用
            - active: 是否为当前激活的选项卡
        """
        tabs = []
        
        # 1. 添加主面板选项卡（始终存在，默认激活）
        main_tab = {
            "id": MAIN_PANEL_TAB_ID,
            "name": MAIN_PANEL_TAB_NAME,
            "type": "main",
            "available": True,
            "active": self._active_tab == MAIN_PANEL_TAB_ID,
        }
        tabs.append(main_tab)
        
        # 2. 获取所有满足条件的系统面板类指令
        panel_instructs = self._get_available_system_panel_instructs()
        
        for instruct_info in panel_instructs:
            tab = {
                "id": instruct_info["id"],
                "name": instruct_info["name"],
                "type": "panel",
                "available": instruct_info["available"],
                "active": self._active_tab == instruct_info["id"],
            }
            tabs.append(tab)
        
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
        }
