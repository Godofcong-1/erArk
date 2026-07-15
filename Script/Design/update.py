import logging
from Script.Design import character_behavior, game_time
from Script.Core import py_cmd, cache_control, get_text, io_init, web_server


def game_update_flow(add_time: int):
    """
    游戏流程刷新
    Keyword arguments:
    add_time -- 游戏步进的时间
    """
    # 深度达到上限时拒绝继续嵌套，防止递归调用导致死循环
    if cache_control.cache.game_update_flow_running >= 2:
        return
    
    # 保存调用者深度，并进入当前更新层级
    caller_depth = cache_control.cache.game_update_flow_running
    cache_control.cache.game_update_flow_running = caller_depth + 1
    start_time = cache_control.cache.game_time
    
    try:
        # 去掉了第一次结算
        # character_behavior.init_character_behavior()
        game_time.sub_time_now(add_time)
        character_behavior.init_character_behavior()
        py_cmd.focus_cmd()
        # 只有最外层更新在全部结算后按游戏时钟净差显示实际经过时间
        if caller_depth == 0 and (elapsed_minutes := int((cache_control.cache.game_time - start_time).total_seconds() / 60)) > 0:
            elapsed_text = get_text._("\n\n {0}分钟过去了\n").format(str(elapsed_minutes))
            if cache_control.cache.web_mode:
                cache_control.cache.web_instruct_texts.append(elapsed_text)
                web_server.emit_realtime_text(elapsed_text, "instruct")
            else:
                io_init.era_print(elapsed_text)
    finally:
        # 无论是否发生异常，都恢复调用者进入前的深度
        cache_control.cache.game_update_flow_running = caller_depth
