#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重新实现流程控制函数，适配Web UI
"""
from Script.Core import cache_control, io_init, constant
from Script.Core.web_server import get_button_response, get_wait_response, get_input_response, update_game_state, update_input_request
import time
from typing import List, Optional

# 获取全局缓存
cache = cache_control.cache
cmd_map = constant.cmd_map  # 命令映射字典

# 初始化尾处理命令函数变量
tail_deal_cmd_func = None  # 保存尾处理命令函数，全局变量

def askfor_all(return_list: List[str]) -> str:
    """
    等待用户选择一个选项
    
    参数:
    return_list (List[str]): 可选择的返回值列表
    
    返回值类型：str
    返回用户选择的选项
    
    在Web UI中，这变成等待用户通过API发送选择
    """
    # 更新Web界面状态
    update_game_state(cache.current_draw_elements, None)
    # 将当前的返回列表保存到缓存中
    cache.current_return_list = return_list
    
    # Web版本中，轮询等待用户响应
    response = None
    while response is None:
        # 检查是否有按钮点击响应
        response = get_button_response()
        if response is not None:
            # 检查响应是否在返回列表中
            if response in return_list:
                # 首先输出该响应
                io_init.era_print(response + "\n")
                # 然后判断值是否有效，有效则执行该命令
                if _cmd_valid(response):
                    _cmd_deal(response)
                elif response == "999":
                    from Script.Core import save_handle
                    # 保存到自动存档
                    save_handle.establish_save("auto")
                    # 退出游戏
                    import os, psutil, signal
                    parent = psutil.Process(os.getpid())
                    children = parent.children(recursive=True)
                    for process in children:
                        process.send_signal(signal.SIGTERM)
                    os._exit(0)
                return response
            elif response == "":
                continue
            else:
                io_init.era_print(response + "\n")
                io_init.era_print("您输入的选项无效，请重试\n")
                response = None  # 重置响应，继续等待
                continue
        # 短暂休眠以避免CPU占用过高
        time.sleep(0.1)
    
    return response

def _cmd_deal(order_number):
    """
    执行命令
    
    参数:
    order_number (str/int) -- 对应命令数字
    
    返回值类型：无
    功能描述：执行与命令ID绑定的函数
    """
    if order_number in cmd_map:
        cmd_func, args, kwargs = cmd_map[order_number]
        if cmd_func:
            if not isinstance(args, tuple):
                args = (args,)
            cmd_func(*args, **kwargs)

def _cmd_valid(order_number):
    """
    判断命令数字是否有效
    
    参数:
    order_number (str/int) -- 对应命令数字
    
    返回值类型：bool
    功能描述：判断命令ID是否有效
    """
    return (order_number in cmd_map and 
            cmd_map[order_number] is not None and 
            cmd_map[order_number][0] is not None)

def askfor_wait() -> None:
    """
    等待用户任意点击继续
    
    返回值类型：None
    
    在Web UI中，这变成等待用户通过API发送继续指令
    """
    # Web版本中，轮询等待用户响应
    while not get_wait_response():
        # 短暂休眠以避免CPU占用过高
        time.sleep(0.1)

def askfor_str(message: str, default_str: str = "") -> str:
    """
    请求用户输入字符串
    
    参数:
    message (str): 提示信息
    default_str (str): 默认字符串
    
    返回值类型：str
    返回用户输入的字符串
    """
    # Web版本中，创建输入请求元素
    cache.current_input_request = {
        "type": "string",
        "message": message,
        "default": default_str
    }
    # 将请求发送给前端
    update_game_state(cache.current_draw_elements, None)
    update_input_request(cache.current_input_request)
    
    # 轮询等待用户输入
    response = None
    while response is None:
        # 检查是否有输入响应
        response = get_input_response()
        if response is not None:
            break
        # 短暂休眠以避免CPU占用过高
        time.sleep(0.1)
    
    # 如果没有响应，返回默认值
    return response if response is not None else default_str

def askfor_int(message: str, default_int: int = 0) -> int:
    """
    请求用户输入整数
    
    参数:
    message (str): 提示信息
    default_int (int): 默认整数
    
    返回值类型：int
    返回用户输入的整数
    """
    # Web版本中，创建输入请求元素
    cache.current_input_request = {
        "type": "integer",
        "message": message,
        "default": default_int
    }
    # 将请求发送给前端
    update_game_state(cache.current_draw_elements, None)
    update_input_request(cache.current_input_request)
    
    # 轮询等待用户输入
    response = None
    while response is None:
        # 检查是否有输入响应
        response = get_input_response()
        if response is not None:
            break
        # 短暂休眠以避免CPU占用过高
        time.sleep(0.1)
    
    # 如果没有响应，返回默认值
    return response if response is not None else default_int

def clear_screen() -> None:
    """
    清空屏幕
    
    返回值类型：None
    
    在Web UI中通过前端JavaScript实现
    """
    # 在Web版本中，这会清空当前绘制元素缓存
    cache.current_draw_elements = []

def order_deal(flag: str = "order", print_order: bool = True, donot_return_null_str: bool = True) -> str:
    """
    处理命令函数 - Web版本
    
    参数:
    flag (str): 类型，默认为order，如果为console，这会执行输入得到的内容
    print_order (bool): 是否将输入的order输出到屏幕上
    donot_return_null_str (bool): 不接受输入空字符串
    
    返回值类型：str
    返回用户输入的命令
    
    这个函数替代了原始flow_handle中的order_deal，解决了死循环问题
    """
    # 创建命令输入请求
    cache.current_input_request = {
        "type": "command",
        "message": "请输入命令:",
        "default": ""
    }
    
    # 修复死循环：使用轮询机制获取响应，而不是等待队列
    response = None
    
    # 如果为按钮命令，等待按钮点击响应
    if flag == "order":
        while response is None:
            response = get_button_response()
            if response is not None:
                break
            time.sleep(0.1)
    # 否则等待文本输入
    else:
        while response is None:
            response = get_input_response()
            if response is not None and (not donot_return_null_str or response != ""):
                break
            time.sleep(0.1)
    
    # 如果需要打印命令，将其添加到绘制元素
    if print_order and response:
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        
        # 添加命令文本元素
        cache.current_draw_elements.append({
            "type": "text",
            "text": f"\n{response}\n",
            "style": "normal"
        })
    
    return response if response is not None else ""

# 添加退出标志和命令处理相关变量
exit_flag = False

def bind_cmd(cmd_number: str, cmd_func: callable, arg: tuple = (), kw: dict = {}) -> None:
    """
    绑定命令数字与命令函数
    
    参数:
    cmd_number (str): 命令数字或标识符
    cmd_func (callable): 命令函数
    arg (tuple): 传给命令函数的顺序参数
    kw (dict): 传给命令函数的字典参数
    
    返回值类型：None
    """
    # 在Web版本中，我们保存命令函数及其参数
    cmd_map[cmd_number] = (cmd_func, arg, kw)

def print_cmd(cmd_str: str, cmd_number: str, cmd_func=None, arg: tuple = (), 
             kw: dict = {}, normal_style: str = "standard", on_style: str = "onbutton") -> str:
    """
    输出命令按钮
    
    参数:
    cmd_str (str): 命令对应文字
    cmd_number (str): 命令数字或标识符
    cmd_func (callable): 命令函数
    arg (tuple): 传给命令函数的顺序参数
    kw (dict): 传给命令函数的字典参数
    normal_style (str): 正常状态下命令显示样式
    on_style (str): 鼠标在其上的时候命令显示样式
    
    返回值类型：str
    返回命令文本
    """
    # 绑定命令
    bind_cmd(cmd_number, cmd_func, arg, kw)
    
    # 在Web版本中，创建按钮元素并添加到当前绘制元素列表
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []
    
    # 创建按钮元素
    button_element = {
        "type": "button",
        "text": cmd_str,
        "return_text": str(cmd_number),
        "style": normal_style
    }
    
    # 添加到当前绘制元素列表
    cache.current_draw_elements.append(button_element)
    
    return cmd_str

def cmd_clear(*numbers) -> None:
    """
    清除绑定命令
    
    参数:
    numbers (tuple): 要清除的命令标识符，不传则清除所有
    
    返回值类型：None
    """
    
    # 在Web版本中，从绘制元素中移除按钮并清除命令映射
    
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []
    
    if numbers:
        # 清除指定命令
        for num in numbers:
            if num in cmd_map:
                del cmd_map[num]
            
            # 从绘制元素中移除对应按钮
            cache.current_draw_elements = [elem for elem in cache.current_draw_elements 
                                         if not (elem.get('type') == 'button' and 
                                                elem.get('return_text') == str(num))]
    else:
        # 清除所有命令
        cmd_map.clear()
        
        # 从绘制元素中移除所有按钮
        cache.current_draw_elements = [elem for elem in cache.current_draw_elements 
                                     if elem.get('type') != 'button']



def set_tail_deal_cmd_func(func: callable) -> None:
    """
    设置尾处理命令函数
    参数:
        func (callable): 尾处理命令函数，用于流程结束时调用
    返回值类型: None
    功能描述: 将传入的函数赋值给全局尾处理命令函数变量
    """
    global tail_deal_cmd_func  # 声明使用全局变量
    tail_deal_cmd_func = func  # 设置尾处理命令函数

def deco_set_tail_deal_cmd_func(func: callable) -> callable:
    """
    装饰器，用于设置尾处理命令函数
    参数:
        func (callable): 需要设置为尾处理命令函数的函数
    返回值类型: callable
    功能描述: 使用装饰器方式将指定函数注册为尾处理命令函数，并返回原函数
    """
    set_tail_deal_cmd_func(func)  # 注册尾处理命令函数
    return func  # 返回原函数保持其行为不变

def call_default_flow() -> None:
    """
    调用默认流程处理函数
    返回值类型: None
    功能描述: 如果已设置尾处理命令函数，则调用该函数处理默认流程
    """
    # 判断是否存在尾处理命令函数
    if tail_deal_cmd_func is not None:
        tail_deal_cmd_func()  # 调用尾处理命令函数