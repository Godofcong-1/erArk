#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实现Web版本的绘制类，用于生成HTML元素
"""
from Script.Core import cache_control, game_type, io_init, flow_handle, text_handle
from typing import List, Dict, Any

cache: game_type.Cache = cache_control.cache


class WebDrawBase:
    """基础绘制类"""
    def __init__(self):
        """
        初始化基础绘制类
        
        属性:
        text (str): 要绘制的文本
        width (int): 绘制宽度
        style (str): 样式
        return_text (str): 返回文本
        """
        self.text = ""
        self.width = 0
        self.style = ""
        self.return_text = ""
    
    def to_html(self):
        """
        将绘制对象转换为HTML元素
        
        返回值类型：dict
        返回HTML元素描述字典
        """
        return {
            "type": "text",
            "text": self.text,
            "style": self.style,
            "width": self.width
        }
    
    def draw(self):
        """
        绘制对象到Web接口
        
        返回值类型：无
        """
        # 将HTML元素添加到当前绘制元素列表中
        html_element = self.to_html()
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(html_element)

class WebNormalDraw(WebDrawBase):
    """普通文本绘制类"""
    def __len__(self):
        """
        获取文本长度
        
        返回值类型：int
        返回文本索引长度
        """
        return text_handle.get_text_index(self.text)

class WebButton(WebDrawBase):
    """按钮绘制类"""
    def __init__(self, text="", return_text="", width=None, cmd_func=None, args=(), normal_style="standard"):
        """
        初始化按钮绘制类
        
        参数:
        text (str): 按钮文本
        return_text (str): 返回文本
        width (int): 按钮宽度
        cmd_func (function): 点击命令函数
        args (tuple): 命令函数参数
        normal_style (str): 正常状态样式
        """
        super().__init__()
        self.text = text
        self.return_text = return_text
        self.width = width
        self.cmd_func = cmd_func
        self.args = args
        self.normal_style = normal_style
    
    def to_html(self):
        """
        将按钮转换为HTML元素
        
        返回值类型：dict
        返回HTML按钮元素描述字典
        """
        return {
            "type": "button",
            "text": self.text,
            "return_text": self.return_text,
            "style": self.normal_style,
            "width": self.width
        }

class WebLeftButton(WebButton):
    """左对齐按钮类"""
    pass

class WebCenterButton(WebButton):
    """居中按钮类"""
    pass

class WebTitleLineDraw(WebDrawBase):
    """标题行绘制类"""
    def to_html(self):
        """
        将标题行转换为HTML元素
        
        返回值类型：dict
        返回HTML标题元素描述字典
        """
        return {
            "type": "title",
            "text": self.text,
            "width": self.width
        }

class WebLineDraw(WebDrawBase):
    """分隔线绘制类"""
    def __init__(self, text, width):
        """
        初始化分隔线绘制类
        
        参数:
        text (str): 分隔线文本
        width (int): 分隔线宽度
        """
        super().__init__()
        self.text = text
        self.width = width
    
    def to_html(self):
        """
        将分隔线转换为HTML元素
        
        返回值类型：dict
        返回HTML分隔线元素描述字典
        """
        return {
            "type": "line",
            "text": self.text,
            "width": self.width
        }

class WebWaitDraw(WebNormalDraw):
    """等待玩家输入的绘制类"""
    def draw(self):
        """
        绘制等待输入元素
        
        返回值类型：无
        """
        # 创建特殊的等待元素
        html_element = self.to_html()
        html_element["type"] = "wait"
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(html_element)