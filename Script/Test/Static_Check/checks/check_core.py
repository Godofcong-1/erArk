# -*- coding: UTF-8 -*-
"""
静态检查系统 - 核心示例检查
提供两个最基础的角色索引一致性检查，用于验证静态检查框架自身管线可用，后续领域检查模块可参照本文件的写法接入。
"""
from typing import List

from Script.Core import cache_control
from ..check_registry import CheckFailure, register_check, make_failure


@register_check("CORE-01", "角色索引一致性")
def check_npc_id_got_consistency() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表，cache.npc_id_got中所有id均存在于cache.character_data时返回空列表
    功能:
        校验cache.npc_id_got（已拥有的干员id集合）中的每个id都能在cache.character_data（角色对象数据缓存组）中找到对应角色对象，
        避免出现"已拥有但无角色数据"的野指针式状态
    """
    cache = cache_control.cache
    failures = []
    for character_id in cache.npc_id_got:
        if character_id not in cache.character_data:
            failures.append(
                make_failure(
                    "CORE-01",
                    "角色索引一致性",
                    f"npc_id_got中的角色id={character_id}在character_data中不存在",
                    [character_id],
                )
            )
    return failures


@register_check("CORE-02", "交互对象有效性")
def check_target_character_id_validity() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表，全部角色的target_character_id均指向character_data中现存角色时返回空列表
    功能:
        校验cache.character_data中每个角色的target_character_id（角色当前交互对象id）指向的角色确实存在于character_data中。
        自指（target_character_id == cid）是"无交互对象"的约定值：角色初始化时写的就是target_character_id = character_id
        （Script/Design/character_handle.py:66），上线重置也是指向自身（Script/Settle/default.py:4467）。
        target_character_id == 0 不是通用的"无交互对象"哨兵——对NPC而言它表示"交互对象是0号玩家"，是有意义的真实目标，
        Script/Design/settle_behavior.py:118-133专门以该条件识别并互换双方结算数据；因此本条统一按"是否在character_data中"判定，
        自指与指向玩家都自然通过，不对0值做特殊豁免
    """
    cache = cache_control.cache
    failures = []
    for character_id, character_data in cache.character_data.items():
        target_id = character_data.target_character_id
        if target_id not in cache.character_data:
            failures.append(
                make_failure(
                    "CORE-02",
                    "交互对象有效性",
                    f"角色id={character_id}的target_character_id={target_id}在character_data中不存在",
                    [character_id],
                )
            )
    return failures
