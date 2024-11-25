# -*- coding: UTF-8 -*-
from Script.Core import py_cmd, cache_control, game_type, flow_handle, constant


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def start_frame():
    """
    游戏主流程
    """
    while True:
        py_cmd.clr_cmd()
        constant.panel_data[cache.now_panel_id]()
