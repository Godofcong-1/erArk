# -*- coding: UTF-8 -*-
from Script.Core import py_cmd, constant, cache_control, game_type


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def start_frame():
    """
    游戏主流程
    """
    # 尝试导入Web模式的面板切换异常
    PanelChangeException = None
    if getattr(cache, 'web_mode', False):
        try:
            from Script.Core.flow_handle_web import PanelChangeException
        except ImportError:
            pass
    
    while True:
        py_cmd.clr_cmd()
        py_cmd.focus_cmd()
        try:
            constant.panel_data[cache.now_panel_id]()
        except Exception as e:
            # 在Web模式下，捕获面板切换异常
            if PanelChangeException is not None and isinstance(e, PanelChangeException):
                # 面板切换异常，正常流程，继续主循环
                # print(f"[start_frame] 捕获到面板切换异常，继续主循环")
                continue
            else:
                # 其他异常，重新抛出
                raise
