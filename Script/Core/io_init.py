# -*- coding: UTF-8 -*-
import threading
import queue
import json
from Script.Config import game_config, normal_config
from Script.Core import cache_control

# 获取全局缓存
cache = cache_control.cache

# Web模式相关的延迟导入状态
_web_module_loaded = False
""" 是否已加载Web IO模块 """
web_io = None
""" Web版IO模块的引用（延迟导入） """

# Tkinter main_frame 延迟导入状态（解决无显示环境下的导入问题）
_main_frame_module = None
""" main_frame模块的引用（延迟导入） """
_main_frame_load_attempted = False
""" 是否已尝试加载main_frame模块 """


def _get_main_frame():
    """
    延迟获取main_frame模块
    
    参数：无
    返回值类型：module 或 None
    功能描述：只在非Web模式且需要时才导入main_frame，避免在无显示环境下报错
    """
    global _main_frame_module, _main_frame_load_attempted
    
    if _main_frame_module is not None:
        return _main_frame_module
    
    if _main_frame_load_attempted:
        return None
    
    _main_frame_load_attempted = True
    
    # 检查是否配置为Web模式（直接读取配置，不依赖cache）
    web_draw = getattr(normal_config.config_normal, 'web_draw', 0)
    if web_draw:
        # Web模式下不需要加载main_frame
        return None
    
    try:
        from Script.Core import main_frame
        _main_frame_module = main_frame
        return _main_frame_module
    except Exception as e:
        print(f"警告：无法导入Tkinter main_frame模块: {e}")
        print("将尝试使用Web模式...")
        # 强制启用Web模式
        normal_config.config_normal.web_draw = True
        cache.web_mode = True
        return None


def _is_web_mode():
    """
    动态检查是否在Web模式下运行
    
    参数：无
    返回值类型：bool
    功能描述：检查cache.web_mode的当前值，并在首次检测到Web模式时加载相关模块
    
    注意：此函数必须使用动态检查而非模块级变量，因为：
    1. 模组加载可能在cache.web_mode设置之前导入此模块
    2. 模组加载过程中会导入panel.py等模块，间接导入io_init
    3. 如果使用静态变量，会导致WEB_MODE被错误地设置为False
    """
    global _web_module_loaded, web_io
    
    # 动态获取当前的web_mode设置
    web_mode = getattr(cache, 'web_mode', False)
    
    if web_mode and not _web_module_loaded:
        try:
            # 导入Web版IO模块
            from Script.Core import io_web
            web_io = io_web
            # 设置加载标志
            _web_module_loaded = True
            print("Web IO loaded successfully.")
        except ImportError as e:
            print(f"警告：无法导入Web版IO模块: {e}")
            return False
    
    return web_mode and _web_module_loaded

input_evnet = threading.Event()
_send_queue = queue.Queue()
_order_queue = queue.Queue()
order_swap = None

# tkinter模式下的绑定（延迟到首次使用时判断）
_main_frame_bound = False
""" 是否已绑定main_frame """


def _ensure_main_frame_bound():
    """
    确保tkinter模式下main_frame已绑定
    只在非Web模式下执行绑定
    """
    global _main_frame_bound
    if not _main_frame_bound and not _is_web_mode():
        main_frame = _get_main_frame()
        if main_frame is not None:
            main_frame.bind_return(_input_evnet_set)
            main_frame.bind_queue(_send_queue)
            _main_frame_bound = True


def _input_evnet_set(order):
    """
    推送一个命令
    
    参数:
    order (str) -- 命令
    
    返回值类型：无
    功能描述：将命令推送到队列中
    """
    # 检查是否在Web模式下
    if _is_web_mode():
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
    if _is_web_mode():
        # 使用Web版IO的获取命令函数
        return web_io.get_order()
    else:
        # 原始逻辑
        _ensure_main_frame_bound()
        return _order_queue.get()


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
    if _is_web_mode():
        # 使用Web版IO的运行函数
        return web_io.run(open_func)
    else:
        # 原始逻辑
        _ensure_main_frame_bound()
        main_frame = _get_main_frame()
        if main_frame is None:
            print("错误：无法加载Tkinter，且Web模式未启用")
            return
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
    if not _is_web_mode():
        _send_queue.put_nowait(message)


def arm_input():
    """
    向输出队列推送一个"输入上膛"标记

    参数：无

    返回值类型：无
    功能描述：Tk 模式下在某个提示的输入等待入口调用，把独立的 {"input_arm": true} 标记入队，
              待 read_queue 处理到该标记时把 GUI 侧输入门禁置为已上膛，此后才接受该屏输入。
              Web 模式无渲染期滞留点击问题，此处不入队。
    """
    # 隐性前提：绘制队列为单生产者（flow 线程），标记 push 后 flow 即阻塞等待输入，
    # 故标记恒为该屏消息的批尾；若未来出现后台绘制生产者需重新评估此假设。
    if not _is_web_mode():
        _send_queue.put_nowait(json.dumps({"input_arm": True}))


def put_order(message: str):
    """
    向命令队列中推送信息
    
    参数:
    message (str) -- 推送的命令信息
    
    返回值类型：无
    功能描述：将命令推送到命令队列中
    """
    # 检查是否在Web模式下
    if _is_web_mode():
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
    if _is_web_mode():
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
    if _is_web_mode() and hasattr(web_io, 'image_print'):
        # 使用Web版IO的image_print函数
        web_io.image_print(image_name)
    else:
        # 原始逻辑
        json_str = new_json()
        image_json = {"image_name": image_name}
        json_str["image"] = image_json
        put_queue(json.dumps(json_str, ensure_ascii=False))


def image_list_print(image_name_list: list):
    """
    批量图片输出命令

    参数:
    image_name_list (list) -- 图片名称列表

    返回值类型：无
    功能描述：把一组图片合并为一条消息输出到界面。
              比例条等逐格图片若逐张调用 image_print，每格都是一条独立队列消息
              （json序列化/反序列化/队列操作各一次），主界面单屏可达数百条；
              合并后一条比例条只占一条消息。
    """
    if not image_name_list:
        return
    # 检查是否在Web模式下（Tk模式的比例条绘制已被Web适配器整体替换，此处仅为兜底）
    if _is_web_mode():
        if hasattr(web_io, 'image_print'):
            for image_name in image_name_list:
                web_io.image_print(image_name)
        return
    # 原始逻辑：单条消息携带整组图片名
    json_str = new_json()
    json_str["image_list"] = list(image_name_list)
    put_queue(json.dumps(json_str, ensure_ascii=False))


def warm_up_text_metrics():
    """
    预热 Tk 文本行度量

    参数：无

    返回值类型：无
    功能描述：Tk Text 控件对新字形/新内容的行度量是异步惰性完成的，欠账会在
              进入游戏后的前几屏由 see(END) 一次性同步补算，造成 0.3~1 秒的偶发卡顿
              （地图制表符等特殊字形尤其明显）。本函数在启动加载末尾绘制若干屏
              典型内容：①主场景互动面板（in_scene_panel）及其状态栏/服装栏/身体栏/
              图片栏/污浊栏/指令面板所用文本的去重字形集；②data/map 各级目录 Map
              原文件的地图绘制文本（cache.map_data 即其加载结果）。随后推送
              metrics_sync 标记让 GUI 线程强制完成全部行度量，并立即清屏——
              全程在同一渲染批内处理，玩家不可见，度量成本被移入加载期。仅 Tk 模式生效。
    """
    if _is_web_mode():
        return
    # 1. 地图面板内容：cache.map_data 即 data/map 各级目录下 Map 原文件的加载结果。
    #    抽取部分真实行保留行结构（制表符对齐是地图界面度量成本的大头），
    #    其余行的字形并入去重字形集，保证全部地图的字形都被覆盖
    sample_lines = []
    glyph_set = set()
    try:
        raw_line_quota = 40
        for map_data in cache.map_data.values():
            map_draw = getattr(map_data, "map_draw", None)
            if map_draw is None:
                continue
            for draw_line in map_draw.draw_text:
                line_text = "".join(getattr(now_draw, "text", "") for now_draw in draw_line.draw_list)
                if not line_text.strip():
                    continue
                glyph_set.update(line_text)
                if raw_line_quota > 0:
                    sample_lines.append(line_text)
                    raw_line_quota -= 1
    except Exception:
        # 地图数据不可用时仅用字符样本预热
        pass
    # 2. 主场景互动面板典型文本字形：面板固定标签 + 常用字符样本
    glyph_set.update("场景当前位置的角色一览:收起展开状态栏服装身体图片详细污浊(锁)预热样本：体力气力理智熟练欲望快感绝顶0123456789ABCabc[]（），。！？→○◆·—/%+-|")
    try:
        from Script.Core import get_text, constant

        translate = get_text._
        # 主界面各子面板所用配置表的名字字段：
        # 状态栏（状态名）、服装栏（部位名）、身体栏与污浊栏（器官名/部位名）、指令面板（分类名）。
        name_sources = (
            game_config.config_character_state.values(),
            game_config.config_clothing_type.values(),
            game_config.config_organ.values(),
            game_config.config_body_part.values(),
            game_config.config_instruct_type.values(),
            game_config.config_instruct_sex_type.values(),
        )
        for source in name_sources:
            for config_data in source:
                name_text = getattr(config_data, "name", "")
                if name_text:
                    glyph_set.update(translate(name_text))
        # 指令面板：全部指令名
        for instruct_name in constant.handle_instruct_name_data.values():
            glyph_set.update(translate(instruct_name))
    except Exception:
        # 配置表不可用时仅用地图行与固定样本预热
        pass
    # 3. 去重字形按行拼接（去重后仅数十行即可覆盖主界面与全部地图的常见字形）
    glyph_set.difference_update("\n\r\t\x00 ")
    glyph_list = sorted(glyph_set)
    chunk_size = 60
    for i in range(0, len(glyph_list), chunk_size):
        sample_lines.append("".join(glyph_list[i : i + chunk_size]))
    # 逐行入队绘制（与下方的度量同步、清屏在同一渲染批内完成，不会被玩家看到）
    for line_text in sample_lines:
        era_print(line_text + "\n")
    # 4. 字体变体预热：粗体/下划线/斜体是独立的字体实例，字形度量单独缓存
    variant_sample = "预热字体变体样本0123456789体力气力理智"
    for style_name in ("bold", "underline", "italic", "standard_bold"):
        era_print(variant_sample + "\n", style=style_name)
    # 5. 状态条图片预热：首次使用时的 PhotoImage 惰性转换与图片行度量
    try:
        bar_image_names = set()
        for bar_config in game_config.config_bar.values():
            bar_image_names.add(bar_config.ture_bar)
            bar_image_names.add(bar_config.null_bar)
        image_list_print(sorted(bar_image_names))
        era_print("\n")
    except Exception:
        pass
    # 请求 GUI 线程同步完成全部行度量
    put_queue(json.dumps({"metrics_sync": True}))
    # 立即清屏
    clear_screen()


def clear_screen():
    """
    清屏

    参数：无

    返回值类型：无
    功能描述：清空显示界面
    """
    # 检查是否在Web模式下
    if _is_web_mode():
        # 使用Web版IO的clear_screen函数
        web_io.clear_screen()
    else:
        # 原始逻辑
        json_str = new_json()
        json_str["clear_cmd"] = "true"
        put_queue(json.dumps(json_str, ensure_ascii=False))


def clear_screen_and_history():
    """
    清屏并清空历史记录（仅Web模式有效）
    
    参数：无
    
    返回值类型：无
    功能描述：彻底清空显示界面和历史记录，用于进入主界面等需要完全清空屏幕的场景
    """
    # 检查是否在Web模式下
    if _is_web_mode():
        # 使用Web版IO的clear_screen_and_history函数
        web_io.clear_screen_and_history()
    else:
        # 非Web模式下与clear_screen相同
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
    if not _is_web_mode():
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
    if _is_web_mode() and hasattr(web_io, 'set_background'):
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
    if _is_web_mode():
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
    if _is_web_mode():
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
    if not _is_web_mode():
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
    if _is_web_mode() and hasattr(web_io, 'io_clear_cmd'):
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
    if _is_web_mode():
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
