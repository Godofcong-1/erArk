# -*- coding: utf-8 -*-
"""
交互处理组件
负责处理Web模式下的用户交互逻辑

支持大类/小类嵌套结构：
- 大类（InteractionMajorType）：嘴、手、阴茎、道具、其他
- 小类（InteractionMinorType）：每个大类下的具体交互方式
"""

from typing import Dict, List, Set, Optional
from Script.Core import cache_control, game_type, constant
from Script.Config import game_config
from Script.Design import web_interaction_manager
from Script.System.Instruct_System import interaction_types
from Script.System.Instruct_System.instruct_category import HIP_SUB_PARTS, HEAD_SUB_PARTS, BodyPart

cache: game_type.Cache = cache_control.cache


class InteractionHandler:
    """
    交互处理器
    负责处理交互类型选择和身体部位点击
    
    使用大类/小类嵌套结构：
    - 大类作为选项卡，可切换
    - 每个大类下显示对应的小类按钮
    - 支持大类切换记忆功能
    """

    def __init__(self):
        """初始化交互处理器"""
        self._current_interaction_type: Optional[str] = None
        self._available_body_parts: List[str] = []
        self._selected_body_part: Optional[str] = None

    @property
    def current_interaction_type(self) -> Optional[str]:
        """获取当前选中的交互类型"""
        return self._current_interaction_type

    @property
    def available_body_parts(self) -> List[str]:
        """获取当前可用的身体部位列表"""
        return self._available_body_parts

    def select_major_type(self, major_type_id: str) -> dict:
        """
        选择大类型
        
        Keyword arguments:
        major_type_id -- 大类型ID（字符串标识符，如 'mouth', 'hand', 'penis', 'tool', 'arts', 'stop', 'other'）
        
        Returns:
        dict -- 包含该大类下的小类列表和记忆的小类
        """
        # 使用web_interaction_manager处理大类选择和记忆
        remembered_minor = web_interaction_manager.select_major_type(major_type_id)
        
        # 获取该大类下的小类列表
        minor_types = web_interaction_manager.get_available_minor_types(major_type_id)
        
        # 清除当前选择状态
        self._current_interaction_type = None
        self._available_body_parts = []
        self._selected_body_part = None
        
        return {
            "major_type": major_type_id,
            "major_type_name": interaction_types.MAJOR_TYPE_NAMES.get(major_type_id, ""),
            "minor_types": minor_types,
            "remembered_minor_type": remembered_minor,
            "interaction_state": self.get_interaction_types(),
        }

    def select_minor_type(self, minor_type_id: str) -> dict:
        """
        选择小类型
        
        Keyword arguments:
        minor_type_id -- 小类型ID（字符串标识符，如 'mouth_talk', 'hand_touch', 'arts_hypnosis' 等）
        
        Returns:
        dict -- 包含该小类对应的可用部位和指令
        """
        # 使用web_interaction_manager处理小类选择
        web_interaction_manager.select_minor_type(minor_type_id)
        
        # 更新内部状态
        self._current_interaction_type = minor_type_id
        
        # 获取该小类型对应的可用部位
        self._available_body_parts = self._get_available_body_parts_by_minor_type(minor_type_id)
        
        # 获取该小类型下的指令列表
        instructs = web_interaction_manager.get_instructs_by_minor_type(minor_type_id, check_premise=True)
        
        return {
            "minor_type": minor_type_id,
            "minor_type_name": interaction_types.MINOR_TYPE_NAMES.get(minor_type_id, ""),
            "available_body_parts": self._available_body_parts,
            "instructs_count": len(instructs),
            "interaction_state": self.get_interaction_types(),
        }

    def _get_available_body_parts_by_minor_type(self, minor_type_id: str) -> List[str]:
        """
        根据小类型获取可用的身体部位
        
        Keyword arguments:
        minor_type_id -- 小类型ID（字符串标识符）
        
        Returns:
        List[str] -- 可用部位名称列表
        """
        # 从指令元数据中获取该小类型涉及的所有部位
        # 需要遍历所有指令，找出minor_type == minor_type_id的指令，收集它们的body_parts
        
        body_parts = set()
        for instruct_id, stored_minor_type in constant.instruct_minor_type_data.items():
            if stored_minor_type == minor_type_id:
                parts = constant.instruct_body_parts_data.get(instruct_id, [])
                body_parts.update(parts)
        
        # 检查是否包含臀部子部位（小穴、子宫、后穴、尿道、尾巴、胯部等）
        # 如果包含则将臀部也添加到可用部位列表中，使臀部显示高亮
        hip_sub_part_names = set(HIP_SUB_PARTS)  # 使用 HIP_SUB_PARTS 定义的子部位
        # 同时检查胯部(crotch)，因为它也属于臀部区域
        hip_sub_part_names.add(BodyPart.CROTCH)
        if body_parts & hip_sub_part_names:
            body_parts.add(BodyPart.HIP)
        
        # 检查是否包含头部子部位（头发、兽角等）
        # 如果包含则将头部也添加到可用部位列表中，使头部显示高亮
        head_sub_part_names = set(HEAD_SUB_PARTS)  # 使用 HEAD_SUB_PARTS 定义的子部位
        if body_parts & head_sub_part_names:
            body_parts.add(BodyPart.HEAD)
        
        return list(body_parts)

    def clear_selection(self):
        """清除当前选择状态"""
        self._current_interaction_type = None
        self._available_body_parts = []
        self._selected_body_part = None

    def get_interaction_types(self) -> Dict:
        """
        获取所有可用的交互类型（大类/小类嵌套结构）
        
        返回数据结构包含：
        - major_types: 大类列表，每个大类包含id、name、selected、minor_types
        - minor_types: 当前大类下的小类列表（单独提供便于前端直接渲染）
        - current_major_type: 当前选中的大类型ID
        - current_minor_type: 当前选中的小类型ID
        
        Returns:
        Dict -- 交互类型数据
        """
        # 获取当前选中的大类和小类
        current_major = web_interaction_manager.get_current_major_type()
        current_minor = web_interaction_manager.get_current_minor_type()
        
        # 如果没有选中的大类，默认选择第一个（嘴）
        if current_major is None:
            current_major = interaction_types.MAJOR_TYPE_ORDER[0]
            web_interaction_manager.select_major_type(current_major)
            current_major = web_interaction_manager.get_current_major_type()
            current_minor = web_interaction_manager.get_current_minor_type()
        
        # 构建大类列表
        major_types = []
        for major_id in interaction_types.MAJOR_TYPE_ORDER:
            major_name = interaction_types.MAJOR_TYPE_NAMES.get(major_id, f"类型{major_id}")
            is_selected = (current_major == major_id)
            
            # 获取该大类下的小类
            minor_list = []
            for minor_id in interaction_types.MAJOR_TO_MINOR_TYPES.get(major_id, []):
                minor_name = interaction_types.MINOR_TYPE_NAMES.get(minor_id, f"子类型{minor_id}")
                minor_list.append({
                    "id": minor_id,
                    "name": minor_name,
                    "selected": (current_minor == minor_id),
                })
            
            major_types.append({
                "id": major_id,
                "name": major_name,
                "selected": is_selected,
                "minor_types": minor_list,
            })
        
        # 获取当前大类下的小类列表（便于前端直接渲染）
        current_minor_types = web_interaction_manager.get_available_minor_types(current_major)
        
        return {
            "major_types": major_types,
            "minor_types": current_minor_types,
            "current_major_type": current_major,
            "current_minor_type": current_minor,
            "current_major_type_name": interaction_types.MAJOR_TYPE_NAMES.get(current_major, ""),
            "current_minor_type_name": interaction_types.MINOR_TYPE_NAMES.get(current_minor, "") if current_minor is not None else "",
        }
