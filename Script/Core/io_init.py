# -*- coding: UTF-8 -*-
import threading
import queue
import json
import sys
import importlib
from Script.Core import main_frame
from Script.Config import game_config, normal_config
from Script.Core import cache_control

# 获取全局缓存
cache = cache_control.cache

# 判断是否使用Web模式
WEB_MODE = cache.web_mode
""" 是否使用Web模式，由game.py中设置 """

# 尝试导入Web版IO模块
web_io = None
if WEB_MODE:
    try:
        # 导入Web版IO模块
        from Script.Core import io_web
        # 导入Web服务器模块
        from Script.Core.web_server import update_game_state
        # Web IO模块加载成功
        web_io = io_web
        print("Web IO loaded successfully.")
    except ImportError:
        # 导入失败时，保持使用原始IO
        web_io = None

input_evnet = threading.Event()
_send_queue = queue.Queue()
_order_queue = queue.Queue()
order_swap = None


def _input_evnet_set(order):
    """
    推送一个命令
    
    参数:
    order (str) -- 命令
    
    返回值类型：无
    功能描述：将命令推送到队列中
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的推送命令函数
        web_io._input_event_set(order)
    else:
        # 原始逻辑
        put_order(order)


def get_order():
    """
    获取一个命令
    
    参数：无
    
    返回值类型：str
    功能描述：从命令队列中获取一个命令
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的获取命令函数
        return web_io.get_order()
    else:
        # 原始逻辑
        return _order_queue.get()


# tkinter模式下的绑定
if not WEB_MODE:
    main_frame.bind_return(_input_evnet_set)
    main_frame.bind_queue(_send_queue)


def _get_input_event():
    """
    获取输入事件锁
    
    参数：无
    
    返回值类型：threading.Event
    功能描述：获取用于同步的输入事件锁
    """
    # Web模式下也使用同样的事件锁
    return input_evnet


def run(open_func: object):
    """
    运行游戏
    
    参数:
    open_func (function) -- 开场流程函数
    
    返回值类型：无
    功能描述：启动游戏主流程
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的运行函数
        return web_io.run(open_func)
    else:
        # 原始逻辑
        global _flowthread
        _flowthread = threading.Thread(target=open_func, name="flowthread")
        _flowthread.start()
        main_frame.run()


def put_queue(message: str):
    """
    向输出队列中推送信息
    
    参数:
    message (str) -- 推送的信息
    
    返回值类型：无
    功能描述：将消息推送到输出队列中
    """
    # Web模式下不使用队列
    if not WEB_MODE:
        _send_queue.put_nowait(message)


def put_order(message: str):
    """
    向命令队列中推送信息
    
    参数:
    message (str) -- 推送的命令信息
    
    返回值类型：无
    功能描述：将命令推送到命令队列中
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的put_order函数
        web_io.put_order(message)
    else:
        # 原始逻辑
        _order_queue.put_nowait(message)


# #######################################################################
# json 构建函数


def new_json():
    """
    定义一个通用json结构
    
    参数：无
    
    返回值类型：dict
    功能描述：创建一个基本的JSON结构
    """
    flow_json = {}
    flow_json["content"] = []
    return flow_json


def text_json(string: str, style: tuple or str, tooltip: str = ""):
    """
    定义一个文本json
    
    参数:
    string (str) -- 要显示的文本
    style (tuple或str) -- 显示时的样式
    
    返回值类型：dict
    功能描述：创建一个文本JSON对象
    """
    re = {}
    re["type"] = "text"
    re["text"] = string
    if isinstance(style, tuple):
        re["style"] = style
    if isinstance(style, str):
        re["style"] = (style,)
    re["tooltip"] = tooltip or ""
    return re


def cmd_json(
    cmd_str: str,
    cmd_num: int,
    normal_style: tuple or str,
    on_style: tuple or str,
    tooltip: str = "",
):
    """
    定义一个命令json
    
    参数:
    cmd_str (str) -- 命令文本
    cmd_num (int) -- 命令数字
    normal_style (tuple或str) -- 正常显示样式
    on_style (tuple或str) -- 鼠标在其上时显示样式
    
    返回值类型：dict
    功能描述：创建一个命令JSON对象
    """
    re = {}
    re["type"] = "cmd"
    re["text"] = cmd_str
    re["num"] = cmd_num
    if isinstance(normal_style, tuple):
        re["normal_style"] = normal_style
    if isinstance(normal_style, str):
        re["normal_style"] = (normal_style,)
    if isinstance(on_style, tuple):
        re["on_style"] = on_style
    if isinstance(on_style, str):
        re["on_style"] = (on_style,)
    re["tooltip"] = tooltip or ""
    return re


def style_json(
    style_name: str,
    foreground: str,
    background: str,
    font: str,
    fontsize: str,
    bold: str,
    underline: str,
    italic: str,
):
    """
    定义一个样式json
    
    参数:
    style_name (str) -- 样式名称
    foreground (str) -- 前景色/字体颜色
    background (str) -- 背景色
    font (str) -- 字体
    fontsize (str) -- 字号
    bold (str) -- 加粗
    underline (str) -- 下划线
    italic (str) -- 斜体
    
    返回值类型：dict
    功能描述：创建一个样式JSON对象
    """
    re = {}
    re["style_name"] = style_name
    re["foreground"] = foreground
    re["background"] = background
    re["font"] = font
    re["fontsize"] = fontsize
    re["bold"] = bold
    re["underline"] = underline
    re["italic"] = italic
    return re


# #######################################################################
# 输出格式化


def era_print(string: str, style="standard", tooltip: str = ""):
    """
    输出命令
    
    参数:
    string (str) -- 输出文本
    style (str) -- 显示样式
    
    返回值类型：无
    功能描述：输出格式化文本到界面
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的era_print函数
        web_io.era_print(string, style, tooltip=tooltip)
    else:
        # 原始逻辑
        json_str = new_json()
        json_str["content"].append(text_json(string, style, tooltip))
        put_queue(json.dumps(json_str, ensure_ascii=False))


def image_print(image_name: str):
    """
    图片输出命令
    
    参数:
    image_name (str) -- 图片名称
    
    返回值类型：无
    功能描述：输出图片到界面
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None and hasattr(web_io, 'image_print'):
        # 使用Web版IO的image_print函数
        web_io.image_print(image_name)
    else:
        # 原始逻辑
        json_str = new_json()
        image_json = {"image_name": image_name}
        json_str["image"] = image_json
        put_queue(json.dumps(json_str, ensure_ascii=False))


def clear_screen():
    """
    清屏
    
    参数：无
    
    返回值类型：无
    功能描述：清空显示界面
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的clear_screen函数
        web_io.clear_screen()
    else:
        # 原始逻辑
        json_str = new_json()
        json_str["clear_cmd"] = "true"
        put_queue(json.dumps(json_str, ensure_ascii=False))


def frame_style_def(
    style_name: str,
    foreground: str,
    background: str,
    font: str,
    fontsize: str,
    bold: str,
    underline: str,
    italic: str,
):
    """
    推送一条在前端定义样式的信息
    
    参数:
    style_name (str) -- 样式名称
    foreground (str) -- 前景色/字体颜色
    background (str) -- 背景色
    font (str) -- 字体
    fontsize (str) -- 字号
    bold (str) -- 加粗， 用1表示使用
    underline (str) -- 下划线，用1表示使用
    italic (str) -- 斜体，用1表示使用
    
    返回值类型：无
    功能描述：定义一个样式并推送到前端
    """
    # Web模式下暂不处理样式定义
    if not WEB_MODE:
        json_str = new_json()
        json_str["set_style"] = style_json(
            style_name,
            foreground,
            background,
            font,
            fontsize,
            bold,
            underline,
            italic,
        )
        put_queue(json.dumps(json_str, ensure_ascii=False))


def set_background(color: str):
    """
    设置前端背景颜色
    
    参数:
    color (str) -- 颜色
    
    返回值类型：无
    功能描述：设置界面的背景颜色
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None and hasattr(web_io, 'set_background'):
        # 使用Web版IO的set_background函数
        web_io.set_background(color)
    else:
        # 原始逻辑
        json_str = new_json()
        json_str["bgcolor"] = color
        put_queue(json.dumps(json_str, ensure_ascii=False))


def clear_order():
    """
    清除前端已经设置的命令
    
    参数：无
    
    返回值类型：无
    功能描述：清除界面上的所有命令按钮
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的clear_order函数
        web_io.clear_order()
    else:
        # 原始逻辑
        json_str = new_json()
        json_str["clearorder_cmd"] = "true"
        put_queue(json.dumps(json_str, ensure_ascii=False))


def io_print_cmd(
    cmd_str: str,
    cmd_number: int,
    normal_style="standard",
    on_style="onbutton",
    tooltip: str = "",
):
    """
    打印一条指令
    
    参数:
    cmd_str (str) -- 命令文本
    cmd_number (int) -- 命令数字
    normal_style (str) -- 正常显示样式
    on_style (str) -- 鼠标在其上时显示样式
    
    返回值类型：无
    功能描述：在界面上显示一个可点击的命令按钮
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的io_print_cmd函数
        web_io.io_print_cmd(cmd_str, cmd_number, normal_style, on_style, tooltip)
    else:
        # 原始逻辑
        json_str = new_json()
        json_str["content"].append(
            cmd_json(cmd_str, cmd_number, normal_style, on_style, tooltip)
        )
        put_queue(json.dumps(json_str, ensure_ascii=False))


def io_print_image_cmd(cmd_str: str, cmd_number: int, tooltip: str = ""):
    """
    打印图片指令
    
    参数:
    cmd_str (str) -- 命令文本
    cmd_number (int) -- 命令数字
    
    返回值类型：无
    功能描述：在界面上显示一个图片按钮
    """
    # Web模式下暂不支持图片命令
    if not WEB_MODE:
        json_str = new_json()
        data = {}
        data["type"] = "image_cmd"
        data["text"] = cmd_str
        data["num"] = cmd_number
        if tooltip:
            data["tooltip"] = tooltip
        json_str["content"].append(data)
        put_queue(json.dumps(json_str, ensure_ascii=False))


def io_clear_cmd(*cmd_numbers: int):
    """
    清除命令
    
    参数:
    cmd_numbers (int) -- 命令数字，不输入则清除当前已有的全部命令
    
    返回值类型：无
    功能描述：清除指定的命令按钮，或者所有命令按钮
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None and hasattr(web_io, 'io_clear_cmd'):
        # 使用Web版IO的io_clear_cmd函数
        web_io.io_clear_cmd(*cmd_numbers)
    else:
        # 原始逻辑
        json_str = new_json()
        if cmd_numbers:
            json_str["clearcmd_cmd"] = cmd_numbers
        else:
            json_str["clearcmd_cmd"] = "all"
        put_queue(json.dumps(json_str, ensure_ascii=False))


def style_def():
    """
    样式定义占位函数
    
    参数：无
    
    返回值类型：无
    功能描述：提供一个样式定义的占位函数，会在init_style中被覆盖
    """
    pass


def init_style():
    """
    富文本样式初始化
    
    参数：无
    
    返回值类型：无
    功能描述：初始化所有游戏中使用的样式
    """
    # 检查是否在Web模式下
    if WEB_MODE and web_io is not None:
        # 使用Web版IO的init_style函数
        if hasattr(web_io, 'init_style'):
            web_io.init_style()
        return
    
    # 原始逻辑
    global style_def

    def new_style_def(
        style_name,
        foreground,
        background,
        font,
        fontsize,
        bold,
        underline,
        italic,
    ):
        frame_style_def(
            style_name,
            foreground,
            background,
            font,
            fontsize,
            bold,
            underline,
            italic,
        )

    style_def = new_style_def
    style_list = game_config.config_font
    standard_data = style_list[0]
    for style_id in style_list:
        style = style_list[style_id]
        for k in standard_data.__dict__:
            if k not in style.__dict__:
                style.__dict__[k] = standard_data.__dict__[k]
        if "font" not in style.__dict__ or style.font == "":
            style.font = normal_config.config_normal.font
        style_def(
            style.name,
            style.foreground,
            style.background,
            style.font,
            normal_config.config_normal.font_size,
            style.bold,
            style.underline,
            style.italic,
        )
    # 额外注册三个通用修饰符 tag，便于在文本中单独使用或与基础样式组合：
    # 这些 tag 注册时不改变前景色/背景色/字体，只设置字体属性（bold/underline/italic）
    # 使用空的 foreground/background ("") 以及默认字体，以便只体现修饰符效果
    modifier_font = normal_config.config_normal.font
    modifier_size = normal_config.config_normal.font_size
    # bold
    style_def("bold", "", "", modifier_font, modifier_size, "1", "0", "0")
    # underline
    style_def("underline", "", "", modifier_font, modifier_size, "0", "1", "0")
    # italic
    style_def("italic", "", "", modifier_font, modifier_size, "0", "0", "1")
    # 为了让修饰符与基础样式组合时也能生效，预先为每个基础样式注册所有修饰符的组合样式。
    # 组合名采用 base_mod1_mod2 形式，例如 "green_bold_italic"，不会包含空格，方便前端作为 tag 使用。
    modifier_names = ["bold", "underline", "italic"]
    # 生成所有非空子集组合（共 2^3 - 1 = 7 种）
    from itertools import combinations

    base_style_names = list(game_config.config_font_data.keys())
    for base in base_style_names:
        # 找到基础样式的数据（若存在于 config_font）以复制颜色/字体设置
        style_obj = None
        if base in game_config.config_font_data:
            base_id = game_config.config_font_data[base]
            if base_id in game_config.config_font:
                style_obj = game_config.config_font[base_id]
        # 若没找到 style_obj，则使用标准样式作为基准
        if style_obj is None:
            style_obj = standard_data

        # 对 1..3 个修饰符的所有组合进行注册
        for r in range(1, len(modifier_names) + 1):
            for combo in combinations(modifier_names, r):
                combo_name = base + "_" + "_".join(combo)
                bold_flag = "1" if "bold" in combo else "0"
                underline_flag = "1" if "underline" in combo else "0"
                italic_flag = "1" if "italic" in combo else "0"
                style_def(
                    combo_name,
                    style_obj.foreground,
                    style_obj.background,
                    style_obj.font if hasattr(style_obj, 'font') and style_obj.font else normal_config.config_normal.font,
                    normal_config.config_normal.font_size,
                    bold_flag,
                    underline_flag,
                    italic_flag,
                )
