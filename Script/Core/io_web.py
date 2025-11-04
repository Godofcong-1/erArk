#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web模式下的IO操作适配器
用于替换原有的tkinter界面IO操作
"""

import threading
import json
import copy
from typing import Dict, Any
from Script.Core import cache_control
from Script.Core.web_server import update_game_state

# 全局变量
cache = cache_control.cache

# Web绘制历史记录设置
MAX_HISTORY_LENGTH = 500
HISTORY_ELEMENT_TYPES = {
    "text",
    "line",
    "title",
    "image",
    "center_image",
    "character",
    "bar",
    "info_bar",
    "info_character",
    "line_wait",
}


def _ensure_current_draw_list() -> None:
    """
    确保当前绘制元素列表存在

    参数：无

    返回值类型：无
    功能描述：初始化当前绘制元素缓存列表
    """
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []


def _ensure_history_list() -> None:
    """
    确保历史绘制缓存存在

    参数：无

    返回值类型：无
    功能描述：初始化Web绘制历史缓存列表
    """
    if not hasattr(cache, "web_draw_history"):
        cache.web_draw_history = []
    if not hasattr(cache, "web_draw_history_line_total"):
        cache.web_draw_history_line_total = 0


def _calculate_element_lines(element: Dict[str, Any]) -> int:
    """
    计算绘制元素占用的行数

    参数:
    element (dict): 绘制元素

    返回值类型：int
    功能描述：根据元素类型估算行数，用于限制历史长度
    """
    elem_type = element.get("type")
    if elem_type == "text":
        text = element.get("text", "")
        if text == "":
            return 1
        # 拆分换行符，避免末尾空行导致额外统计
        lines = text.split("\n")
        # 如果文本以换行结尾，split会产生一个额外的空字符串，剔除
        if lines and lines[-1] == "":
            lines = lines[:-1]
        return max(len(lines), 1)
    if elem_type in {"image", "center_image", "character", "bar"}:
        return 1
    if elem_type in {"info_bar", "info_character"}:
        total = 1
        if element.get("text"):
            total += _calculate_element_lines({"type": "text", "text": element["text"]})
        for item in element.get("draw_list", []):
            total += _calculate_element_lines(item)
        return max(total, 1)
    return 1


def _record_history_element(element: Dict[str, Any]) -> None:
    """
    记录历史绘制元素

    参数:
    element (dict): 绘制元素

    返回值类型：无
    功能描述：按类型过滤并维护固定长度的历史缓存
    """
    if not isinstance(element, dict):
        return
    if element.get("type") not in HISTORY_ELEMENT_TYPES:
        return
    _ensure_history_list()
    lines = _calculate_element_lines(element)
    history_entry = {"element": copy.deepcopy(element), "line_count": lines}
    cache.web_draw_history.append(history_entry)
    cache.web_draw_history_line_total += lines
    while cache.web_draw_history and cache.web_draw_history_line_total > MAX_HISTORY_LENGTH:
        removed = cache.web_draw_history.pop(0)
        cache.web_draw_history_line_total -= removed.get("line_count", 0)


def append_current_draw_element(element: Dict[str, Any], record_history: bool = True) -> None:
    """
    添加绘制元素并根据需要记录历史

    参数:
    element (dict): 绘制元素
    record_history (bool): 是否记录到历史缓存

    返回值类型：无
    功能描述：统一处理绘制元素的追加和历史维护
    """
    _ensure_current_draw_list()
    cache.current_draw_elements.append(element)
    elem_type = element.get("type")
    if elem_type in {"line_wait", "wait"}:
        wait_id = element.get("wait_id")
        text_preview = element.get("text", "")
        if isinstance(text_preview, str) and len(text_preview) > 30:
            text_preview = text_preview[:27] + "..."
        # print(
        #     f"[io_web] appended element type={elem_type} wait_id={wait_id} record_history={record_history} text={text_preview!r}"
        # )
    if record_history:
        _record_history_element(element)
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
    _ensure_current_draw_list()
    cache.current_draw_elements = []

    # 回填历史内容
    if hasattr(cache, "web_draw_history") and cache.web_draw_history:
        history_snapshot = [copy.deepcopy(entry["element"]) for entry in cache.web_draw_history]
        cache.current_draw_elements.extend(history_snapshot)

    # 更新Web界面状态
    update_game_state(cache.current_draw_elements, None)

def era_print(string, style="standard", tooltip: str = ""):
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
        "style": style,
        "tooltip": tooltip or "",
    }
    
    # 添加到当前绘制元素列表
    append_current_draw_element(text_element, record_history=True)

def io_print_cmd(
    cmd_str,
    cmd_number,
    normal_style="standard",
    on_style="onbutton",
    tooltip: str = "",
):
    """
    打印一个命令按钮
    
    参数:
    cmd_str (str): 命令文本
    cmd_number (int): 命令编号
    normal_style (str): 正常显示样式
    on_style (str): 鼠标悬停样式
    tooltip (str): 悬停提示文本
    
    返回值类型：无
    将按钮元素添加到当前绘制元素列表
    """
    # 创建按钮元素
    button_element = {
        "type": "button",
        "text": cmd_str,
        "return_text": str(cmd_number),
        "style": normal_style,
        "tooltip": tooltip or "",
    }
    
    # 添加到当前绘制元素列表
    append_current_draw_element(button_element, record_history=False)

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