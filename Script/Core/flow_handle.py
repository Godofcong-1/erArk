# -*- coding: UTF-8 -*-
import time
from types import FunctionType
from Script.Core import (
    text_handle,
    io_init,
    get_text,
    game_type,
    cache_control,
    constant,
)

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def null_func():
    """
    占位用空函数
    """
    return


# 管理flow
default_flow = null_func


def set_default_flow(func, arg=(), kw={}):
    """
    设置默认流程
    Keyword arguments:
    func -- 对应的流程函数，
    arg -- 传给func的顺序参数
    kw -- 传给kw的顺序参数
    """
    global default_flow
    if not isinstance(arg, tuple):
        arg = (arg,)
    if func == null_func:
        default_flow = null_func
        return

    def run_func():
        func(*arg, **kw)

    default_flow = run_func


def call_default_flow():
    """
    运行默认流程函数
    """
    default_flow()


def clear_default_flow():
    """
    清楚当前默认流程函数，并是设置为空函数
    """
    global default_flow, null_func
    set_default_flow(null_func)


cmd_map = constant.cmd_map


def default_tail_deal_cmd_func(order):
    """
    结尾命令处理空函数，用于占位
    """
    return


tail_deal_cmd_func = default_tail_deal_cmd_func


def set_tail_deal_cmd_func(func):
    """
    设置结尾命令处理函数
    Keyword arguments:
    func -- 结尾命令处理函数
    """
    global tail_deal_cmd_func
    tail_deal_cmd_func = func


def deco_set_tail_deal_cmd_func(func):
    """
    为结尾命令设置函数提供装饰器功能
    Keyword arguments:
    func -- 结尾命令处理函数
    """
    set_tail_deal_cmd_func(func)
    return func


def bind_cmd(cmd_number, cmd_func, arg=(), kw={}):
    """
    绑定命令数字与命令函数
    Keyword arguments:
    cmd_number -- 命令数字
    cmd_func -- 命令函数
    arg -- 传给命令函数的顺序参数
    kw -- 传给命令函数的字典参数
    """
    if not isinstance(arg, tuple):
        arg = (arg,)
    if cmd_func == null_func:
        cmd_map[cmd_number] = null_func
        return
    elif cmd_func is None:
        cmd_map[cmd_number] = null_func
        return

    def run_func():
        cmd_func(*arg, **kw)

    cmd_map[cmd_number] = run_func


def print_cmd(
    cmd_str,
    cmd_number,
    cmd_func=null_func,
    arg=(),
    kw={},
    normal_style="standard",
    on_style="onbutton",
):
    """
    输出命令数字
    Keyword arguments:
    cmd_str -- 命令对应文字
    cmd_number -- 命令数字
    cmd_func -- 命令函数
    arg -- 传给命令函数的顺序参数
    kw -- 传给命令函数的字典参数
    normal_style -- 正常状态下命令显示样式
    on_style -- 鼠标在其上的时候命令显示样式
    """
    bind_cmd(cmd_number, cmd_func, arg, kw)
    io_init.io_print_cmd(cmd_str, cmd_number, normal_style, on_style)
    return cmd_str


def cmd_clear(*number):
    """
    清楚绑定命令
    Keyword arguments:
    number -- 清楚绑定命令数字
    """
    set_tail_deal_cmd_func(default_tail_deal_cmd_func)
    if number:
        for num in number:
            del cmd_map[num]
            io_init.io_clear_cmd(num)
    else:
        cmd_map.clear()
        io_init.io_clear_cmd()


def _cmd_deal(order_number):
    """
    执行命令
    Keyword arguments:
    order_number -- 对应命令数字
    """
    cmd_map[order_number]()


def _cmd_valid(order_number):
    """
    判断命令数字是否有效
    Keyword arguments:
    order_number -- 对应命令数字
    """
    return (order_number in cmd_map) and (
        cmd_map[order_number] != null_func and cmd_map[order_number] is not None
    )


__skip_flag__ = False
exit_flag = False


# 处理输入
def order_deal(flag="order", print_order=True, donot_return_null_str=True):
    """
    处理命令函数
    Keyword arguments:
    flag -- 类型，默认为order，如果为console，这回执行输入得到的内容
    print_order -- 是否将输入的order输出到屏幕上
    donot_return_null_str -- 不接受输入空字符串
    """
    global __skip_flag__
    __skip_flag__ = False
    while True:
        time.sleep(0.01)
        if not donot_return_null_str and cache.wframe_mouse.w_frame_up:
            return ""
        while not io_init._order_queue.empty():
            order = io_init.get_order()
            if print_order and order != "":
                io_init.era_print("\n" + order + "\n")
            if flag == "str":
                if order.isdigit():
                    order = str(int(order))
                return order
            if flag == "console":
                exec(order)
            if flag == "order":
                if _cmd_valid(order):
                    _cmd_deal(order)
                    return
                else:
                    global tail_deal_cmd_func
                    tail_deal_cmd_func(int(order))
                    return


def askfor_str(donot_return_null_str=True, print_order=False):
    """
    用于请求一个字符串为结果的输入
    Keyword arguments:
    donot_return_null_str -- 不接受输入空字符串
    print_order -- 是否将输入的order输出到屏幕上
    """
    while True:
        if not donot_return_null_str and cache.wframe_mouse.w_frame_up:
            cache.wframe_mouse.w_frame_up = 0
            return ""
        order = order_deal("str", print_order, donot_return_null_str)
        if donot_return_null_str and order != "":
            return order
        elif not donot_return_null_str:
            return order


def askfor_all(input_list: list, print_order=False):
    """
    用于请求一个位于列表中的输入，如果输入没有在列表中，则告知用户出错。
    Keyword arguments:
    input_list -- 用于判断的列表内容
    print_order -- 是否将输入的order输出到屏幕上
    """
    while 1:
        order = order_deal("str", print_order)
        if order in input_list:
            io_init.era_print(order + "\n")
            if _cmd_valid(order):
                _cmd_deal(order)
            return order
        elif order == "":
            continue
        else:
            io_init.era_print(order + "\n")
            io_init.era_print(_("您输入的选项无效，请重试\n"))
            continue


def askfor_int(list, print_order=False):
    """
    用于请求位于列表中的整数的输入，如果输入没有在列表中，则告知用户出错。
    Keyword arguments:
    list -- 用于判断的列表内容
    print_order -- 是否将输入的order输出到屏幕上
    """
    while True:
        order = order_deal("str", print_order)
        order = text_handle.full_to_half_text(order)
        if order in list:
            io_init.era_print(order + "\n\n")
            return order
        elif order == "":
            continue
        else:
            io_init.era_print(order + "\n")
            io_init.era_print(_("您输入的选项无效，请重试\n"))
            continue


def askfor_wait():
    """用于请求一个暂停动作，输入任何数都可以继续"""
    cache.wframe_mouse.w_frame_up = 0
    while not cache.wframe_mouse.w_frame_up:
        re = askfor_str(donot_return_null_str=False)
        if re == "":
            break
