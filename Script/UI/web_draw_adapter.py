#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web绘制适配器，用于转换原有绘制类到Web界面
"""

import time
from typing import List, Dict, Any, Optional
from Script.Core import cache_control, web_server
from Script.UI.Moudle import draw
from Script.Config import normal_config

# 获取全局缓存
cache = cache_control.cache

class WebDrawAdapter:
    """
    Web绘制适配器基类
    用于将原有的tkinter绘制适配到Web界面
    """
    
    @staticmethod
    def adapt_normal_draw(normal_draw: draw.NormalDraw):
        """
        适配普通文本绘制类
        
        参数:
        normal_draw (draw.NormalDraw): 原始的普通文本绘制对象
        
        返回值类型: 无
        功能描述: 将普通文本绘制适配到Web界面
        """
        # 创建Web文本元素
        web_element = {
            "type": "text",
            "text": normal_draw.text,
            "font": normal_draw.style,
            "width": normal_draw.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_center_draw(center_draw: draw.CenterDraw):
        """
        适配居中文本绘制类
        
        参数:
        center_draw (draw.CenterDraw): 原始的居中文本绘制对象
        
        返回值类型: 无
        功能描述: 将居中文本绘制适配到Web界面
        """
        # 创建Web文本元素，添加居中标记
        web_element = {
            "type": "text",
            "text": center_draw.text,
            "font": center_draw.style,  # 添加居中样式
            "width": center_draw.width,
            "align": "center"
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)

    @staticmethod
    def adapt_right_draw(right_draw: draw.RightDraw):
        """
        适配右对齐文本绘制类
        
        参数:
        right_draw (draw.RightDraw): 原始的右对齐文本绘制对象
        
        返回值类型: 无
        功能描述: 将右对齐文本绘制适配到Web界面
        """
        # 创建Web文本元素，并添加右对齐标记
        web_element = {
            "type": "text",
            "text": right_draw.text,
            "font": right_draw.style,  # 添加右对齐样式
            "width": right_draw.width,
            "align": "right"
        }
        
        # 检查是否存在当前绘制元素列表，如果不存在则创建
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        # 将右对齐文本元素添加到绘制列表中
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态，刷新显示绘制列表
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_button(button: draw.Button):
        """
        适配按钮绘制类
        
        参数:
        button (draw.Button): 原始的按钮绘制对象
        
        返回值类型: 无
        功能描述: 将按钮绘制适配到Web界面，同时保持原有的命令处理流程
        """
        # 创建Web按钮元素
        web_element = {
            "type": "button",
            "text": button.text,
            "return_text": button.return_text,
            "font": button.normal_style,
            "width": button.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 关键修复：调用py_cmd.pcmd()注册按钮事件处理函数
        from Script.Core import flow_handle
        flow_handle.bind_cmd(button.return_text, button.cmd_func, button.args)

        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
        

    @staticmethod
    def adapt_line_draw(line_draw: draw.LineDraw):
        """
        适配线条绘制类
        
        参数:
        line_draw (draw.LineDraw): 原始的线条绘制对象
        
        返回值类型: 无
        功能描述: 将线条绘制适配到Web界面
        """
        # 创建Web分隔线元素
        web_element = {
            "type": "line",
            "text": line_draw.text,
            "font": line_draw.style,
            "width": line_draw.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_title_line_draw(title_line: draw.TitleLineDraw):
        """
        适配标题线绘制类
        
        参数:
        title_line (draw.TitleLineDraw): 原始的标题线绘制对象
        
        返回值类型: 无
        功能描述: 将标题线绘制适配到Web界面
        """
        # 创建Web标题元素
        web_element = {
            "type": "title",
            "text": title_line.title,
            "font": title_line.title_style,
            "width": title_line.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_wait_draw(wait_draw: draw.WaitDraw):
        """
        适配等待绘制类
        
        参数:
        wait_draw (draw.WaitDraw): 原始的等待绘制对象
        
        返回值类型: 无
        功能描述: 将等待绘制适配到Web界面
        """
        # 创建Web等待元素
        web_element = {
            "type": "wait",
            "text": wait_draw.text,
            "font": wait_draw.style,
            "width": wait_draw.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)

    @staticmethod
    def adapt_image_draw(image_draw: draw.ImageDraw):
        """
        适配图片绘制类
        
        参数:
        image_draw (draw.ImageDraw): 原始的图片绘制对象
        
        返回值类型: 无
        功能描述: 将图片绘制适配到Web界面
        """
        # 创建Web图片元素
        web_element = {
            "type": "image",
            "image_name": image_draw.image_name,
            "width": image_draw.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_bar_draw(bar_draw: draw.BarDraw):
        """
        适配比例条绘制类
        
        参数:
        bar_draw (draw.BarDraw): 原始的比例条绘制对象
        
        返回值类型: 无
        功能描述: 将比例条绘制适配到Web界面
        """
        # 获取比例条元素列表
        bar_elements = []
        for bar_item in bar_draw.draw_list:
            bar_elements.append({
                "image_name": bar_item.image_name,
                "width": bar_item.width
            })
            
        # 创建Web比例条元素
        web_element = {
            "type": "bar",
            "bar_elements": bar_elements,
            "width": bar_draw.width,
            "bar_id": bar_draw.bar_id
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_chara_draw(chara_draw: draw.CharaDraw):
        """
        适配人物图片绘制类
        
        参数:
        chara_draw (draw.CharaDraw): 原始的人物图片绘制对象
        
        返回值类型: 无
        功能描述: 将人物图片绘制适配到Web界面
        """
        # 获取人物图片元素列表
        chara_elements = []
        for chara_item in chara_draw.draw_list:
            chara_elements.append({
                "image_name": chara_item.image_name,
                "width": chara_item.width
            })
            
        # 创建Web人物图片元素
        web_element = {
            "type": "character",
            "character_elements": chara_elements,
            "width": chara_draw.width,
            "chara_id": chara_draw.chara_id
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_info_bar_draw(info_bar_draw: draw.InfoBarDraw):
        """
        适配带有文本和数值描述的比例条绘制类
        
        参数:
        info_bar_draw (draw.InfoBarDraw): 原始的带有文本和数值描述的比例条绘制对象
        
        返回值类型: 无
        功能描述: 将带有文本和数值描述的比例条绘制适配到Web界面
        """
        # 创建Web带有文本和数值描述的比例条元素
        web_element = {
            "type": "info_bar",
            "text": info_bar_draw.text,
            "max_value": info_bar_draw.max_value,
            "value": info_bar_draw.value,
            "bar_id": info_bar_draw.bar_id,
            "width": info_bar_draw.width,
            "scale": info_bar_draw.scale,
            "chara_state": info_bar_draw.chara_state
        }
        
        # 获取绘制列表中的元素
        draw_list_elements = []
        for item in info_bar_draw.draw_list:
            if isinstance(item, draw.NormalDraw):
                draw_list_elements.append({
                    "type": "text",
                    "text": item.text,
                    "font": item.style,
                    "width": item.width
                })
            elif isinstance(item, draw.BarDraw):
                bar_items = []
                for bar_item in item.draw_list:
                    bar_items.append({
                        "image_name": bar_item.image_name,
                        "width": bar_item.width
                    })
                draw_list_elements.append({
                    "type": "bar",
                    "bar_elements": bar_items,
                    "width": item.width,
                    "bar_id": item.bar_id
                })
            elif isinstance(item, draw.StatusLevelDraw):
                draw_list_elements.append({
                    "type": "status_level",
                    "text": item.grade_draw.text,
                    "font": item.grade_draw.style,
                    "width": item.grade_draw.width
                })
                
        web_element["draw_list"] = draw_list_elements
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_info_chara_draw(info_chara_draw: draw.InfoCharaDraw):
        """
        适配带有文本的人物图像绘制类
        
        参数:
        info_chara_draw (draw.InfoCharaDraw): 原始的带有文本的人物图像绘制对象
        
        返回值类型: 无
        功能描述: 将带有文本的人物图像绘制适配到Web界面
        """
        # 创建Web带有文本的人物图像元素
        web_element = {
            "type": "info_character",
            "text": info_chara_draw.text,
            "max_value": info_chara_draw.max_value,
            "value": info_chara_draw.value,
            "bar_id": info_chara_draw.bar_id,
            "width": info_chara_draw.width,
            "scale": info_chara_draw.scale
        }
        
        # 获取绘制列表中的元素
        draw_list_elements = []
        for item in info_chara_draw.draw_list:
            if isinstance(item, draw.NormalDraw):
                draw_list_elements.append({
                    "type": "text",
                    "text": item.text,
                    "font": item.style,
                    "width": item.width
                })
            elif isinstance(item, draw.BarDraw):
                bar_items = []
                for bar_item in item.draw_list:
                    bar_items.append({
                        "image_name": bar_item.image_name,
                        "width": bar_item.width
                    })
                draw_list_elements.append({
                    "type": "bar",
                    "bar_elements": bar_items,
                    "width": item.width,
                    "bar_id": item.bar_id
                })
                
        web_element["draw_list"] = draw_list_elements
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_image_button(image_button: draw.ImageButton):
        """
        适配图片按钮绘制类
        
        参数:
        image_button (draw.ImageButton): 原始的图片按钮绘制对象
        
        返回值类型: 无
        功能描述: 将图片按钮绘制适配到Web界面
        """
        # 创建Web图片按钮元素
        web_element = {
            "type": "image_button",
            "image_name": image_button.text,
            "return_text": image_button.return_text,
            "width": image_button.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 关键修复：调用py_cmd.pimagecmd()注册图片按钮事件处理函数
        from Script.Core import flow_handle
        flow_handle.bind_cmd(image_button.return_text, image_button.cmd_func, image_button.args)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)
    
    @staticmethod
    def adapt_center_draw_image(center_draw_image: draw.CenterDrawImage):
        """
        适配居中图片绘制类
        
        参数:
        center_draw_image (draw.CenterDrawImage): 原始的居中图片绘制对象
        
        返回值类型: 无
        功能描述: 将居中图片绘制适配到Web界面
        """
        # 创建Web居中图片元素
        web_element = {
            "type": "center_image",
            "text": center_draw_image.text,
            "font": center_draw_image.style,
            "width": center_draw_image.width
        }
        
        # 添加到当前绘制元素列表
        if not hasattr(cache, "current_draw_elements"):
            cache.current_draw_elements = []
        cache.current_draw_elements.append(web_element)
        
        # 更新Web界面状态
        web_server.update_game_state(cache.current_draw_elements, None)

# 包装原始绘制类的draw方法，使其在Web模式下调用适配器

def wrap_draw_method(cls, adapter_method):
    """
    包装绘制类的draw方法
    
    参数:
    cls (class): 要包装的类
    adapter_method (function): 适配器方法
    
    返回值类型: function
    功能描述: 返回包装后的draw方法
    """
    original_draw = cls.draw
    
    def wrapped_draw(self):
        """
        包装后的draw方法
        
        参数: 无
        
        返回值类型: 无
        功能描述: 根据运行模式选择绘制方法
        """
        # 检查是否在Web模式下
        if hasattr(cache, "web_mode") and cache.web_mode:
            # 使用Web适配器
            adapter_method(self)
        else:
            # 使用原始绘制方法
            original_draw(self)
    
    return wrapped_draw

# 包装所有绘制类的draw方法

def apply_web_adapters():
    """
    应用Web适配器到所有绘制类
    
    参数: 无
    
    返回值类型: 无
    功能描述: 包装所有绘制类的draw方法，使其在Web模式下使用适配器
    """
    # 设置Web模式标志
    cache.web_mode = True

    # 修改基础长度
    normal_config.config_normal.text_width = int(normal_config.config_normal.text_width * 1)
    
    # 包装普通文本绘制类
    draw.NormalDraw.draw = wrap_draw_method(draw.NormalDraw, WebDrawAdapter.adapt_normal_draw)
    
    # 包装居中文本绘制类
    draw.CenterDraw.draw = wrap_draw_method(draw.CenterDraw, WebDrawAdapter.adapt_center_draw)
    # 包装右对齐文本绘制类
    draw.RightDraw.draw = wrap_draw_method(draw.RightDraw, WebDrawAdapter.adapt_right_draw)
    
    # 包装按钮绘制类
    draw.Button.draw = wrap_draw_method(draw.Button, WebDrawAdapter.adapt_button)
    draw.CenterButton.draw = wrap_draw_method(draw.CenterButton, WebDrawAdapter.adapt_button)
    draw.LeftButton.draw = wrap_draw_method(draw.LeftButton, WebDrawAdapter.adapt_button)
    
    # 包装线条绘制类
    draw.LineDraw.draw = wrap_draw_method(draw.LineDraw, WebDrawAdapter.adapt_line_draw)
    
    # 包装标题线绘制类
    draw.TitleLineDraw.draw = wrap_draw_method(draw.TitleLineDraw, WebDrawAdapter.adapt_title_line_draw)
    
    # 包装等待绘制类
    draw.WaitDraw.draw = wrap_draw_method(draw.WaitDraw, WebDrawAdapter.adapt_wait_draw)
    
    # 包装图片绘制类
    draw.ImageDraw.draw = wrap_draw_method(draw.ImageDraw, WebDrawAdapter.adapt_image_draw)
    
    # 包装比例条绘制类
    draw.BarDraw.draw = wrap_draw_method(draw.BarDraw, WebDrawAdapter.adapt_bar_draw)
    
    # 包装人物图片绘制类
    draw.CharaDraw.draw = wrap_draw_method(draw.CharaDraw, WebDrawAdapter.adapt_chara_draw)
    
    # 包装带有文本和数值描述的比例条绘制类
    draw.InfoBarDraw.draw = wrap_draw_method(draw.InfoBarDraw, WebDrawAdapter.adapt_info_bar_draw)
    
    # 包装带有文本的人物图像绘制类
    draw.InfoCharaDraw.draw = wrap_draw_method(draw.InfoCharaDraw, WebDrawAdapter.adapt_info_chara_draw)
    
    # 包装图片按钮绘制类
    draw.ImageButton.draw = wrap_draw_method(draw.ImageButton, WebDrawAdapter.adapt_image_button)
    
    # 包装居中图片绘制类
    draw.CenterDrawImage.draw = wrap_draw_method(draw.CenterDrawImage, WebDrawAdapter.adapt_center_draw_image)
    
    print("已应用Web绘制适配器到所有绘制类")