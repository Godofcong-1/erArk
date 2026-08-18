# -*- coding: UTF-8 -*-

from Script.Core import cache_control, constant

cache = cache_control.cache
""" 游戏缓存数据 """


def get_last_valid_sex_behavior_id() -> str:
    """
    获取玩家最近一条非中断H指令的behavior_id
    输入：
        无
    返回：
        str -- 最近一条非中断H指令的behavior_id；若列表为空则返回基础空闲行为id
    功能：
        从cache.pl_pre_behavior_instruce尾部向前遍历，
        跳过constant.special_end_H_list中的中断指令，
        返回第一条有效指令，避免破处体位被记录为中断类指令。
    """
    for behavior_id in reversed(cache.pl_pre_behavior_instruce):
        if behavior_id not in constant.special_end_H_list:
            return behavior_id
    return constant.Behavior.SHARE_BLANKLY
