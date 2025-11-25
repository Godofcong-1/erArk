# -*- coding: UTF-8 -*-
import time
import os
import psutil
import signal
from types import FunctionType
from Script.Core import (
    text_handle,
    io_init,
    get_text,
    game_type,
    cache_control,
    constant,
)

# 全局缓存
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

# 翻译函数
_: FunctionType = get_text._
""" 翻译api """

# 判断是否使用Web模式
WEB_MODE = cache.web_mode
""" 是否使用Web模式，由game.py中设置 """

# 尝试导入Web版flow_handle
if WEB_MODE:
    try:
        # 导入Web版flow_handle模块
        from Script.Core import flow_handle_web
        # 导入Web服务器模块中的函数
        from Script.Core.web_server import get_button_response, get_wait_response, get_input_response
        # 设置Web模式标志
        WEB_MODE = True
    except ImportError:
        # 导入失败时，保持使用原始flow_handle
        WEB_MODE = False

# 如果在Web模式下，使用下面的函数来处理输入输出
if WEB_MODE:
    # 使用Web版本的函数，这些内容会在Web模式下覆盖原函数的实现
    print("已启用Web模式，使用Web版本的流程控制函数")


def null_func():
    """
    占位用空函数
    
    参数：无
    返回值类型：无
    功能描述：提供一个什么都不做的函数作为占位符
    """
    return


# 管理flow
default_flow = null_func


def set_default_flow(func, arg=(), kw={}):
    """
    设置默认流程
    
    参数：
    func (function) -- 对应的流程函数
    arg (tuple) -- 传给func的顺序参数
    kw (dict) -- 传给func的字典参数
    
    返回值类型：无
    功能描述：设置默认的流程函数，供后续调用
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        return flow_handle_web.set_default_flow(func, arg, kw) if hasattr(flow_handle_web, 'set_default_flow') else None
    
    # 原始逻辑
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
    
    参数：无
    返回值类型：无
    功能描述：调用之前设置的默认流程函数
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        return flow_handle_web.call_default_flow() if hasattr(flow_handle_web, 'call_default_flow') else None
    
    # 原始逻辑
    default_flow()


def clear_default_flow():
    """
    清除当前默认流程函数，并设置为空函数
    
    参数：无
    返回值类型：无
    功能描述：清除当前默认流程函数
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        return flow_handle_web.clear_default_flow() if hasattr(flow_handle_web, 'clear_default_flow') else None
    
    # 原始逻辑
    global default_flow, null_func
    set_default_flow(null_func)


cmd_map = constant.cmd_map


def default_tail_deal_cmd_func(order):
    """
    结尾命令处理空函数，用于占位
    
    参数：
    order (str) -- 命令文本
    
    返回值类型：无
    功能描述：默认的结尾命令处理函数，什么都不做
    """
    # 在Web模式下没有特别处理
    return


tail_deal_cmd_func = default_tail_deal_cmd_func


def set_tail_deal_cmd_func(func):
    """
    设置结尾命令处理函数
    
    参数：
    func (function) -- 结尾命令处理函数
    
    返回值类型：无
    功能描述：设置用于处理结尾命令的函数
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 将func保存到Web版flow_handle中
        if hasattr(flow_handle_web, 'set_tail_deal_cmd_func'):
            flow_handle_web.set_tail_deal_cmd_func(func)
        return
    
    # 原始逻辑
    global tail_deal_cmd_func
    tail_deal_cmd_func = func


def deco_set_tail_deal_cmd_func(func):
    """
    为结尾命令设置函数提供装饰器功能
    
    参数：
    func (function) -- 结尾命令处理函数
    
    返回值类型：function
    功能描述：作为装饰器使用，设置结尾命令处理函数
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 调用Web版的装饰器函数
        if hasattr(flow_handle_web, 'deco_set_tail_deal_cmd_func'):
            return flow_handle_web.deco_set_tail_deal_cmd_func(func)
    
    # 原始逻辑
    set_tail_deal_cmd_func(func)
    return func


def bind_cmd(cmd_number, cmd_func, arg=(), kw={}):
    """
    绑定命令数字与命令函数
    
    参数：
    cmd_number (str/int) -- 命令数字
    cmd_func (function) -- 命令函数
    arg (tuple) -- 传给命令函数的顺序参数
    kw (dict) -- 传给命令函数的字典参数
    
    返回值类型：无
    功能描述：将命令ID与对应的处理函数绑定
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 调用Web版的绑定函数
        return flow_handle_web.bind_cmd(cmd_number, cmd_func, arg, kw)
    
    # 原始逻辑
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
    tooltip: str = "",
):
    """
    输出命令数字
    
    参数：
    cmd_str (str) -- 命令对应文字
    cmd_number (str/int) -- 命令数字
    cmd_func (function) -- 命令函数
    arg (tuple) -- 传给命令函数的顺序参数
    kw (dict) -- 传给命令函数的字典参数
    normal_style (str) -- 正常状态下命令显示样式
    on_style (str) -- 鼠标在其上的时候命令显示样式
    
    返回值类型：str
    功能描述：创建一个可点击的命令按钮
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的print_cmd函数
        return flow_handle_web.print_cmd(cmd_str, cmd_number, cmd_func, arg, kw, normal_style, on_style, tooltip)
    
    # 原始逻辑
    bind_cmd(cmd_number, cmd_func, arg, kw)
    io_init.io_print_cmd(cmd_str, cmd_number, normal_style, on_style, tooltip)
    return cmd_str


def print_image_cmd(
    cmd_str,
    cmd_number,
    cmd_func=null_func,
    arg=(),
    kw={},
    tooltip: str = "",
):
    """
    绘制图片按钮
    
    参数：
    cmd_str (str) -- 命令对应文字
    cmd_number (str/int) -- 命令数字
    cmd_func (function) -- 命令函数
    arg (tuple) -- 传给命令函数的顺序参数
    kw (dict) -- 传给命令函数的字典参数
    
    返回值类型：str
    功能描述：创建一个图片按钮
    """
    # 检查是否在Web模式下
    if WEB_MODE and hasattr(flow_handle_web, 'print_image_cmd'):
        # 使用Web版的print_image_cmd函数
        return flow_handle_web.print_image_cmd(cmd_str, cmd_number, cmd_func, arg, kw, tooltip)
    
    # 原始逻辑
    bind_cmd(cmd_number, cmd_func, arg, kw)
    io_init.io_print_image_cmd(cmd_str, cmd_number, tooltip)
    return cmd_str


def cmd_clear(*number):
    """
    清除绑定命令
    
    参数：
    number (tuple) -- 清除绑定命令数字，不提供则清除所有
    
    返回值类型：无
    功能描述：清除指定或所有的命令绑定
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的cmd_clear函数
        return flow_handle_web.cmd_clear(*number)
    
    # 原始逻辑
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
    
    参数：
    order_number (str/int) -- 对应命令数字
    
    返回值类型：无
    功能描述：执行与命令ID绑定的函数
    """
    # 检查是否在Web模式下
    if WEB_MODE and hasattr(flow_handle_web, '_cmd_deal'):
        # 使用Web版的_cmd_deal函数
        return flow_handle_web._cmd_deal(order_number)
    
    # 原始逻辑
    cmd_map[order_number]()


def _cmd_valid(order_number):
    """
    判断命令数字是否有效
    
    参数：
    order_number (str/int) -- 对应命令数字
    
    返回值类型：bool
    功能描述：判断命令ID是否有效
    """
    # 检查是否在Web模式下
    if WEB_MODE and hasattr(flow_handle_web, '_cmd_valid'):
        # 使用Web版的_cmd_valid函数
        return flow_handle_web._cmd_valid(order_number)
    
    # 原始逻辑
    return (order_number in cmd_map) and (
        cmd_map[order_number] != null_func and cmd_map[order_number] is not None
    )


__skip_flag__ = False
exit_flag = False


# 处理输入
def order_deal(flag="order", print_order=True, donot_return_null_str=True):
    """
    处理命令函数
    
    参数：
    flag (str) -- 类型，默认为order，如果为console，会执行输入得到的内容
    print_order (bool) -- 是否将输入的order输出到屏幕上
    donot_return_null_str (bool) -- 不接受输入空字符串
    
    返回值类型：str
    功能描述：处理用户输入的命令
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的order_deal函数
        return flow_handle_web.order_deal(flag, print_order, donot_return_null_str)
    
    # 原始逻辑 - tkinter模式
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
    
    参数：
    donot_return_null_str (bool) -- 不接受输入空字符串
    print_order (bool) -- 是否将输入的order输出到屏幕上
    
    返回值类型：str
    功能描述：获取用户输入的字符串
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的askfor_str函数
        message = "请输入文本："  # 在Web模式下需要提供提示信息
        return flow_handle_web.askfor_str(message, "")
    
    # 原始逻辑
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
    
    参数：
    input_list (list) -- 用于判断的列表内容
    print_order (bool) -- 是否将输入的order输出到屏幕上
    
    返回值类型：str
    功能描述：获取用户在指定列表中选择的输入
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的askfor_all函数
        return flow_handle_web.askfor_all(input_list)
    
    # 原始逻辑
    while 1:
        order = order_deal("str", print_order)
        if order in input_list:
            io_init.era_print(order + "\n")
            if _cmd_valid(order):
                _cmd_deal(order)
            elif order == "999":
                from Script.Core import save_handle
                # 保存到自动存档
                save_handle.establish_save("auto")
                # 退出游戏
                parent = psutil.Process(os.getpid())
                children = parent.children(recursive=True)
                for process in children:
                    process.send_signal(signal.SIGTERM)
                os._exit(0)
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
    
    参数：
    list (list) -- 用于判断的列表内容
    print_order (bool) -- 是否将输入的order输出到屏幕上
    
    返回值类型：str
    功能描述：获取用户在指定整数列表中的选择
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的askfor_int函数
        message = "请输入数字："  # 在Web模式下需要提供提示信息
        return flow_handle_web.askfor_int(message, 0)
    
    # 原始逻辑
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
    """
    用于请求一个暂停动作，输入任何数都可以继续
    
    参数：无
    返回值类型：无
    功能描述：等待用户任意输入后继续
    """
    # 检查是否在Web模式下
    if WEB_MODE:
        # 使用Web版的askfor_wait函数
        return flow_handle_web.askfor_wait()

    # 原始逻辑
    # 基准模式下直接跳过等待，避免自动化流程阻塞
    if getattr(cache, "benchmark_mode", False):
        return

    cache.wframe_mouse.w_frame_up = 0
    while not cache.wframe_mouse.w_frame_up:
        re = askfor_str(donot_return_null_str=False)
        if re == "":
            break
