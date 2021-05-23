# -*- coding: UTF-8 -*-
import os
import traceback
from Script.Core import flow_handle, io_init, key_listion_event
from Script.Config import normal_config

# 字符串定义###########################################################
NO_EVENT_FUNC = "no_event_func"

# 系统函数#############################################################
# 初始化函数
_main_flow = None
error_path = os.path.join("error.log")


def init(main_flow: object):
    """
    游戏流程初始化
    Keyword argument:
    main_flow -- 游戏主流程
    """
    global def_style
    io_init.clear_screen()
    io_init.clear_order()
    flow_handle.cmd_clear()
    # 载入按键监听
    key_listion_event.on_wframe_listion()
    # 设置背景颜色
    io_init.set_background(normal_config.config_normal.background)
    # 初始化字体
    io_init.init_style()
    # 初始化地图数据
    global _main_flow
    _main_flow = main_flow

    _have_run = False

    def run_main_flow():
        nonlocal _have_run
        while True:
            if not _have_run:
                main_flow()
                _have_run = True
            askfor_order()
            flow_handle.call_default_flow()
            if flow_handle.exit_flag:
                break

    try:
        run_main_flow()
    except Exception:
        traceback.print_exc(file=open(error_path, "a"))
        os._exit(0)


def run(main_func: object):
    """
    执行游戏主流程
    Keyword arguments:
    main_func -- 游戏主流程
    """

    def _init():
        init(main_func)

    io_init.run(_init)


def console_log(string: str):
    """
    向后台打印日志
    Keyword arguments:
    string -- 游戏日志信息
    """
    print("game log:")
    print(string + "\n")


# 请求输入命令
askfor_order = flow_handle.order_deal

# 请求输入一个字符串
askfor_str = flow_handle.askfor_str

# 请求输入一个数字
askfor_int = flow_handle.askfor_int
askfor_all = flow_handle.askfor_all

# 设置尾命令处理函数
set_deal_cmd_func = flow_handle.set_tail_deal_cmd_func

# 设置尾命令处理函数装饰器
set_deal_cmd_func_deco = flow_handle.deco_set_tail_deal_cmd_func
