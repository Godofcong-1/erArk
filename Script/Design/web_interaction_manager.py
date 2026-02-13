# -*- coding: utf-8 -*-
"""
Web模式交互类型管理器
处理大类/小类的选择、切换和记忆功能

【重构说明】2026-01-19
- 大类和小类不再使用数字，改为小写英语字符串标识符
- 如嘴类从 0 改为 'mouth'，手类从 1 改为 'hand'
- 小类同理，如嘴对话从 0 改为 'mouth_talk'

【排序说明】2026-02-14
- 指令列表按照 Instruct.py 中定义的顺序排序，而非 handle_instruct.py 的装饰器执行顺序
"""

from typing import Dict, List, Optional, Set, Union
from Script.Core import constant, cache_control, game_type
from Script.Config import game_config
from Script.System.Instruct_System.Instruct import Instruct


# 生成指令ID到顺序的映射（基于 Instruct.py 中的定义顺序）
# 使用 __dict__ 而非 dir() 以保持正确的定义顺序
_INSTRUCT_ORDER_MAP: Dict[str, int] = {}
_order_index = 0
for attr_name, attr_value in Instruct.__dict__.items():
    if not attr_name.startswith('_') and isinstance(attr_value, str):
        _INSTRUCT_ORDER_MAP[attr_value] = _order_index
        _order_index += 1


def _get_instruct_sort_key(instruct_id: str) -> int:
    """
    获取指令的排序键值，基于 Instruct.py 中的定义顺序
    
    Keyword arguments:
    instruct_id -- 指令id字符串
    
    Returns:
    int -- 排序键值，越小越靠前；未找到的指令返回最大值
    """
    return _INSTRUCT_ORDER_MAP.get(instruct_id, 999999)

cache: game_type.Cache = cache_control.cache


def get_current_major_type() -> Optional[str]:
    """获取当前选中的大类型（字符串标识符）"""
    return cache.web_current_major_type


def get_current_minor_type() -> Optional[str]:
    """获取当前选中的小类型（字符串标识符）"""
    return cache.web_current_minor_type


def select_major_type(major_type: str) -> Optional[str]:
    """
    选择大类型，返回对应的小类型（如果有记忆则恢复，否则返回None）
    
    Keyword arguments:
    major_type -- 大类型id（字符串标识符，如'mouth'/'hand'/'penis'/'tool'/'arts'/'stop'/'other'）
    
    Returns:
    Optional[str] -- 该大类下记忆的小类型id（字符串标识符），或None
    """
    # 保存当前大类的小类选择到记忆
    if cache.web_current_major_type is not None and cache.web_current_minor_type is not None:
        cache.web_major_type_memory[cache.web_current_major_type] = cache.web_current_minor_type
    
    # 切换到新的大类
    cache.web_current_major_type = major_type
    
    # 从记忆中恢复该大类的小类选择（字典方式，使用get避免KeyError）
    remembered_minor = cache.web_major_type_memory.get(major_type)
    if remembered_minor is not None:
        cache.web_current_minor_type = remembered_minor
        return remembered_minor
    else:
        cache.web_current_minor_type = None
        return None

def select_minor_type(minor_type: str):
    """
    选择小类型
    
    Keyword arguments:
    minor_type -- 小类型id（字符串标识符，如'mouth_talk'/'hand_touch'等）
    """
    cache.web_current_minor_type = minor_type
    # 同时更新记忆
    if cache.web_current_major_type is not None:
        cache.web_major_type_memory[cache.web_current_major_type] = minor_type


def clear_selection():
    """清除当前选择"""
    cache.web_current_major_type = None
    cache.web_current_minor_type = None


def get_available_major_types() -> List[Dict]:
    """
    获取可用的大类型列表
    
    Returns:
    List[Dict] -- 大类型信息列表，包含id和名称
    """
    result = []
    for major_type in constant.MAJOR_TYPE_ORDER:
        result.append({
            "id": major_type,
            "name": constant.get_major_type_name(major_type),
            "selected": cache.web_current_major_type == major_type,
        })
    return result


def get_available_minor_types(major_type: Optional[str] = None) -> List[Dict]:
    """
    获取指定大类下可用的小类型列表
    
    Keyword arguments:
    major_type -- 大类型id（字符串标识符），默认使用当前选中的大类
    
    Returns:
    List[Dict] -- 小类型信息列表，包含id和名称
    """
    if major_type is None:
        major_type = cache.web_current_major_type
    if major_type is None:
        return []
    
    result = []
    for minor_type in constant.get_minor_types(major_type):
        result.append({
            "id": minor_type,
            "name": constant.get_minor_type_name(minor_type),
            "selected": cache.web_current_minor_type == minor_type,
        })
    return result


def get_instructs_by_minor_type(minor_type: Optional[str] = None, check_premise: bool = True) -> List[str]:
    """
    获取指定小类型下的指令列表
    
    Keyword arguments:
    minor_type -- 小类型id（字符串标识符），默认使用当前选中的小类
    check_premise -- 是否检查前提条件
    
    Returns:
    List[str] -- 指令id列表，按照 Instruct.py 中的定义顺序排序
    """
    if minor_type is None:
        minor_type = cache.web_current_minor_type
    if minor_type is None:
        return []
    
    result = []
    premise_cache = {}  # 前提缓存，避免重复判断
    for instruct_id, stored_minor_type in constant.instruct_minor_type_data.items():
        # 判断是否是系统类指令,跳过
        if constant.instruct_category_data.get(instruct_id) == constant.InstructCategory.SYSTEM_PANEL:
            continue
        if stored_minor_type == minor_type:
            if check_premise:
                # 检查前提条件
                if _check_single_instruct_premise(instruct_id, premise_cache):
                    result.append(instruct_id)
            else:
                result.append(instruct_id)
    
    # 按照 Instruct.py 中的定义顺序排序
    result.sort(key=_get_instruct_sort_key)
    return result


def get_instructs_by_body_part(body_part: str, minor_type: Optional[int] = None, check_premise: bool = True) -> List[int]:
    """
    获取指定身体部位关联的指令列表
    
    Keyword arguments:
    body_part -- 身体部位名称
    minor_type -- 小类型id过滤（字符串标识符），默认使用当前选中的小类
    check_premise -- 是否检查前提条件
    
    Returns:
    List[str] -- 指令id列表，按照 Instruct.py 中的定义顺序排序
    """
    result = []
    premise_cache = {}  # 前提缓存，避免重复判断
    
    for instruct_id, body_parts in constant.instruct_body_parts_data.items():
        if body_part in body_parts:
            # 如果指定了小类型，则过滤
            if minor_type is not None:
                stored_minor_type = constant.instruct_minor_type_data.get(instruct_id)
                if stored_minor_type != minor_type:
                    continue
            
            if check_premise:
                # 检查前提条件
                if _check_single_instruct_premise(instruct_id, premise_cache):
                    result.append(instruct_id)
            else:
                result.append(instruct_id)
    
    # 按照 Instruct.py 中的定义顺序排序
    result.sort(key=_get_instruct_sort_key)
    return result


def get_drug_list() -> List[Dict]:
    """
    获取可用药物列表
    
    Returns:
    List[Dict] -- 药物信息列表，包含id和名称
    """
    result = []
    # 从道具配置中获取药物类道具
    for item_id, item_config in game_config.config_item.items():
        if item_config.type == "药物":
            result.append({
                "id": item_id,
                "name": item_config.name,
                "selected": cache.web_selected_drug_id == item_id,
            })
    return result


def get_item_list() -> List[Dict]:
    """
    获取可用道具列表
    
    Returns:
    List[Dict] -- 道具信息列表，包含id和名称
    """
    result = []
    # 从道具配置中获取H道具类道具
    for item_id, item_config in game_config.config_item.items():
        if item_config.type in ("H道具", "调教道具", "玩具"):
            result.append({
                "id": item_id,
                "name": item_config.name,
                "selected": cache.web_selected_item_id == item_id,
            })
    return result


def select_drug(drug_id: int):
    """选择药物"""
    cache.web_selected_drug_id = drug_id


def select_item(item_id: int):
    """选择道具"""
    cache.web_selected_item_id = item_id


def get_interaction_state() -> Dict:
    """
    获取当前交互状态（用于前端显示）
    
    Returns:
    Dict -- 交互状态信息
    """
    state = {
        "major_type": cache.web_current_major_type,
        "major_type_name": constant.get_major_type_name(cache.web_current_major_type) if cache.web_current_major_type is not None else None,
        "minor_type": cache.web_current_minor_type,
        "minor_type_name": constant.get_minor_type_name(cache.web_current_minor_type) if cache.web_current_minor_type is not None else None,
        "selected_drug_id": cache.web_selected_drug_id,
        "selected_item_id": cache.web_selected_item_id,
        "available_major_types": get_available_major_types(),
        "available_minor_types": get_available_minor_types(),
    }
    
    # 如果是道具大类，添加药物/道具列表
    if cache.web_current_major_type == constant.InteractionMajorType.TOOL:
        if cache.web_current_minor_type == constant.InteractionMinorType.TOOL_DRUG:
            state["drug_list"] = get_drug_list()
        elif cache.web_current_minor_type == constant.InteractionMinorType.TOOL_ITEM:
            state["item_list"] = get_item_list()
    
    return state


def _check_single_instruct_premise(instruct_id: str, premise_cache: Dict) -> bool:
    """
    检查单个指令的前提条件是否满足
    
    Keyword arguments:
    instruct_id -- 指令id（字符串标识符）
    premise_cache -- 前提条件判断结果缓存（用于优化重复判断）
    
    Returns:
    bool -- 是否满足所有前提条件
    """
    from Script.Design import handle_premise
    
    # 如果没有前提条件，则视为满足
    if instruct_id not in constant.instruct_premise_data:
        return True
    
    # 如果当前是debug模式，跳过前提条件检查
    if cache.debug_mode:
        return True
    
    premises = constant.instruct_premise_data[instruct_id]
    
    for premise in premises:
        # 使用缓存优化重复判断
        if premise in premise_cache:
            if not premise_cache[premise]:
                return False
        else:
            # 调用前提判断函数，角色id固定为0（玩家）
            result = handle_premise.handle_premise(premise, 0)
            premise_cache[premise] = result
            if not result:
                return False
    
    return True
