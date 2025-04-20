#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
界面适配器模块，处理tkinter和WebUI之间的兼容
"""
from Script.Core import cache_control
from Script.UI.web_draw import *
import importlib
import sys

# 定义Web模式的标志
WEB_MODE = True

def get_normal_draw():
    """
    获取基础绘制类
    
    返回值类型：Class
    根据当前模式返回适合的绘制类
    """
    if WEB_MODE:
        return WebNormalDraw
    else:
        # 动态导入tkinter绘制类，避免直接依赖
        try:
            tk_draw = importlib.import_module("Script.UI.tk_draw")
            return tk_draw.NormalDraw
        except ImportError:
            print("错误：未找到tkinter绘制模块")
            return WebNormalDraw

def get_button(position="normal"):
    """
    获取按钮类
    
    参数:
    position (str): 按钮位置类型
    
    返回值类型：Class
    根据当前模式返回适合的按钮类
    """
    if WEB_MODE:
        if position == "left":
            return WebLeftButton
        elif position == "center":
            return WebCenterButton
        else:
            return WebButton
    else:
        # 动态导入tkinter按钮类
        try:
            tk_draw = importlib.import_module("Script.UI.tk_draw")
            if position == "left":
                return tk_draw.LeftButton
            elif position == "center":
                return tk_draw.CenterButton
            else:
                return tk_draw.Button
        except ImportError:
            print("错误：未找到tkinter绘制模块")
            if position == "left":
                return WebLeftButton
            elif position == "center":
                return WebCenterButton
            else:
                return WebButton

def get_title_draw():
    """
    获取标题绘制类
    
    返回值类型：Class
    根据当前模式返回适合的标题绘制类
    """
    if WEB_MODE:
        return WebTitleLineDraw
    else:
        try:
            tk_draw = importlib.import_module("Script.UI.tk_draw")
            return tk_draw.TitleLineDraw
        except ImportError:
            print("错误：未找到tkinter绘制模块")
            return WebTitleLineDraw

def get_line_draw():
    """
    获取分隔线绘制类
    
    返回值类型：Class
    根据当前模式返回适合的分隔线绘制类
    """
    if WEB_MODE:
        return WebLineDraw
    else:
        try:
            tk_draw = importlib.import_module("Script.UI.tk_draw")
            return tk_draw.LineDraw
        except ImportError:
            print("错误：未找到tkinter绘制模块")
            return WebLineDraw

def get_wait_draw():
    """
    获取等待绘制类
    
    返回值类型：Class
    根据当前模式返回适合的等待绘制类
    """
    if WEB_MODE:
        return WebWaitDraw
    else:
        try:
            tk_draw = importlib.import_module("Script.UI.tk_draw")
            return tk_draw.WaitDraw
        except ImportError:
            print("错误：未找到tkinter绘制模块")
            return WebWaitDraw

def clear_screen():
    """
    清空屏幕
    
    返回值类型：无
    根据当前模式执行清屏操作
    """
    if WEB_MODE:
        # Web模式下清空当前绘制元素
        cache_control.cache.current_draw_elements = []
    else:
        try:
            # tkinter模式下调用原始清屏函数
            tk_flow = importlib.import_module("Script.UI.Flow")
            tk_flow.clear_screen()
        except (ImportError, AttributeError):
            print("错误：未找到tkinter清屏函数")
            # 备用清屏方法
            cache_control.cache.current_draw_elements = []