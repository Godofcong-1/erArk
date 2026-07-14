import logging
from Script.Design import character_behavior, game_time
from Script.Core import py_cmd, cache_control


def game_update_flow(add_time: int):
    """
    游戏流程刷新
    Keyword arguments:
    add_time -- 游戏步进的时间
    """
    # 检查是否已经在游戏更新流程中，防止递归调用导致死循环
    if cache_control.cache.game_update_flow_running >= 2:
        return
    
    # 保存调用者深度，并进入当前更新层级
    caller_depth = cache_control.cache.game_update_flow_running
    cache_control.cache.game_update_flow_running = caller_depth + 1
    
    try:
        # 去掉了第一次结算
        # character_behavior.init_character_behavior()
        game_time.sub_time_now(add_time)
        character_behavior.init_character_behavior()
        py_cmd.focus_cmd()
    finally:
        # 无论是否发生异常，都恢复调用者进入前的深度
        cache_control.cache.game_update_flow_running = caller_depth
