#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web模式下的IO操作适配器
用于替换原有的tkinter界面IO操作
"""

import threading
import json
from Script.Core import cache_control, game_type
from Script.Core.web_server import update_game_state

# 全局变量
cache = cache_control.cache
input_event = threading.Event()
_order_queue = []  # 命令队列

def _input_event_set(order):
    """
    推送一个命令到队列
    
    参数:
    order (str): 需要推送的命令
    
    返回值类型：无
    """
    put_order(order)

def get_order():
    """
    从队列中获取一个命令
    
    返回值类型：str
    返回队列中的一个命令，如果队列为空则返回None
    """
    if _order_queue:
        return _order_queue.pop(0)
    return None

def run(open_func):
    """
    在Web模式下运行游戏
    
    参数:
    open_func (function): 游戏开场流程函数
    
    返回值类型：无
    """
    # Web模式下直接调用开场函数，不启动tkinter窗口
    open_func()

def put_order(message):
    """
    向命令队列中推送信息
    
    参数:
    message (str): 推送的命令信息
    
    返回值类型：无
    """
    _order_queue.append(message)

# 以下函数处理文本输出，在Web模式下将输出转换为HTML元素

def clear_screen():
    """
    清空屏幕
    
    返回值类型：无
    清空当前绘制元素缓存
    """
    # 清空当前绘制元素
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []
    else:
        cache.current_draw_elements = []
    
    # 更新Web界面状态
    update_game_state(cache.current_draw_elements, None)

def era_print(string, style="standard"):
    """
    输出文本
    
    参数:
    string (str): 输出的文本内容
    style (str): 显示样式
    
    返回值类型：无
    将文本添加到当前绘制元素列表
    """
    # 创建文本元素
    text_element = {
        "type": "text",
        "text": string,
        "style": style
    }
    
    # 添加到当前绘制元素列表
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []
    cache.current_draw_elements.append(text_element)

def io_print_cmd(cmd_str, cmd_number, normal_style="standard", on_style="onbutton"):
    """
    打印一个命令按钮
    
    参数:
    cmd_str (str): 命令文本
    cmd_number (int): 命令编号
    normal_style (str): 正常显示样式
    on_style (str): 鼠标悬停样式
    
    返回值类型：无
    将按钮元素添加到当前绘制元素列表
    """
    # 创建按钮元素
    button_element = {
        "type": "button",
        "text": cmd_str,
        "return_text": str(cmd_number),
        "style": normal_style
    }
    
    # 添加到当前绘制元素列表
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []
    cache.current_draw_elements.append(button_element)

def set_background(color):
    """
    设置背景颜色
    
    参数:
    color (str): 颜色值
    
    返回值类型：无
    """
    # Web模式下通过CSS处理背景色，这里暂不处理
    pass

def clear_order():
    """
    清除已设置的命令
    
    返回值类型：无
    """
    # 清除命令相关元素
    if hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = [elem for elem in cache.current_draw_elements if elem.get("type") != "button"]

def init_style():
    """
    初始化样式
    
    返回值类型：无
    在Web模式下通过CSS处理样式
    """
    # Web模式下样式由CSS处理，这里不需要特别操作
    pass