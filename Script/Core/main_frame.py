# -*- coding: UTF-8 -*-
import os
import json
import uuid
import psutil
import signal
import sys

# Windows高DPI支持：必须在创建任何窗口之前设置DPI感知
# 这解决了打包后游戏窗口在高分屏上模糊的问题
if sys.platform == "win32":
    try:
        import ctypes
        # 尝试使用 Windows 8.1+ 的 Per-Monitor DPI 感知
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except AttributeError:
            # Windows 8.1 之前的系统使用 SetProcessDPIAware
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from tkinter import (
    ttk,
    Tk,
    Text,
    StringVar,
    END,
    N,
    W,
    E,
    S,
    VERTICAL,
    font,
    Entry,
    PhotoImage,
    Toplevel,  # Tooltip 浮窗使用的顶层窗口组件
)
from Script.Core import (
    text_handle,
    game_type,
    cache_control,
)
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def close_window():
    """
    关闭游戏，会终止当前进程和所有子进程
    """
    parent = psutil.Process(os.getpid())
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(signal.SIGTERM)
    os._exit(0)

def get_resource_path(file_name: str) -> str:
    """
    获取资源文件绝对路径
    参数:
        file_name (str): 资源文件相对路径，例如 "image/logo.png"
    返回:
        str: 资源文件的绝对路径
    """
    # 如果是 PyInstaller 打包后的环境，资源会被解压到 _MEIPASS 目录
    if getattr(sys, "frozen", False):
        # 获取当前工作目录作为资源根路径
        base_path = os.getcwd()
    else:
        # 开发环境：资源在项目根目录
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
        )
    # 将类似 "image/logo.png" 拆分并拼接成正确的绝对路径
    return os.path.join(base_path, *file_name.split('/'))

def load_local_fonts(tk_root: Tk) -> None:
    """加载 static/fonts 下的字体文件供 Tk 窗口使用"""
    fonts_dir = None
    fonts_dir_candidates = []

    # 如果是在打包环境下运行，字体文件可能在可执行文件同级目录的 static/fonts 下
    if hasattr(sys, "_MEIPASS") or getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
        fonts_dir_candidates.append(os.path.join(base_dir, "static", "fonts"))
        fonts_dir_candidates.append(os.path.join(base_dir, "fonts"))
    # 开发环境下，字体文件在项目的 static/fonts 目录
    else:
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
        )
        fonts_dir_candidates.append(os.path.join(project_root, "static", "fonts"))

    for candidate in fonts_dir_candidates:
        if os.path.isdir(candidate):
            fonts_dir = candidate
            break

    if fonts_dir is None:
        return

    alias_overrides = {
        "等距更纱黑体": ["等距更纱黑体 SC", "Sarasa Mono SC", "SarasaMonoSC"],
        "等距更纱黑体.ttf": ["等距更纱黑体 SC", "Sarasa Mono SC", "SarasaMonoSC"],
        "emoji": ["EmojiSupport"],
        "emoji.ttf": ["EmojiSupport"],
    }

    existing_fonts = set(map(str, tk_root.tk.call("font", "names")))

    for entry in os.scandir(fonts_dir):
        if not entry.is_file():
            continue
        name_lower = entry.name.lower()
        if not name_lower.endswith((".ttf", ".otf", ".ttc")):
            continue

        font_path = entry.path.replace("\\", "/")
        base_name = os.path.splitext(entry.name)[0]

        alias_candidates = []
        for candidate in (
            base_name,
            base_name.replace("_", " "),
            base_name.replace("_", ""),
            entry.name,
        ):
            cleaned = candidate.strip()
            if cleaned and cleaned not in alias_candidates:
                alias_candidates.append(cleaned)

        for extra in alias_overrides.get(entry.name, []):
            cleaned = extra.strip()
            if cleaned and cleaned not in alias_candidates:
                alias_candidates.append(cleaned)
        for extra in alias_overrides.get(base_name, []):
            cleaned = extra.strip()
            if cleaned and cleaned not in alias_candidates:
                alias_candidates.append(cleaned)

        primary_alias = None
        first_success_alias = None
        source_desc = None
        failed_aliases = []

        # 首先检查是否已存在同名字体
        for alias in alias_candidates:
            if alias in existing_fonts:
                primary_alias = alias
                first_success_alias = alias
                source_desc = "existing"
                break

        # 优先尝试从本地字体文件创建
        if primary_alias is None:
            for alias in alias_candidates:
                if alias in existing_fonts:
                    continue
                try:
                    tk_root.tk.call("font", "create", alias, "-family", f"@{font_path}")
                    primary_alias = alias
                    first_success_alias = alias
                    source_desc = font_path
                    existing_fonts.add(alias)
                    break
                except Exception:
                    failed_aliases.append(alias)

        # 若本地字体加载失败，尝试系统字体
        if primary_alias is None:
            try:
                system_families = set(map(str, tk_root.tk.call("font", "families")))
            except Exception:
                system_families = set()

            for alias in alias_candidates:
                if alias in existing_fonts:
                    primary_alias = alias
                    first_success_alias = alias
                    source_desc = "existing"
                    break
                if alias not in system_families:
                    failed_aliases.append(alias)
                    continue
                try:
                    tk_root.tk.call("font", "create", alias, "-family", alias)
                    primary_alias = alias
                    first_success_alias = alias
                    source_desc = "system"
                    existing_fonts.add(alias)
                    break
                except Exception:
                    failed_aliases.append(alias)

        # 为其余别名创建引用
        if primary_alias is not None:
            for alias in alias_candidates:
                if alias == primary_alias or alias in existing_fonts:
                    continue
                try:
                    tk_root.tk.call("font", "create", alias, "-family", primary_alias)
                    existing_fonts.add(alias)
                except Exception:
                    # 若别名创建失败且存在同名系统字体，再尝试直接使用系统字体
                    try:
                        tk_root.tk.call("font", "create", alias, "-family", alias)
                        existing_fonts.add(alias)
                    except Exception:
                        failed_aliases.append(alias)

        # 输出加载结果
        if primary_alias is not None:
            if source_desc == font_path:
                print(f"[load_local_fonts] 成功加载字体 {first_success_alias} <- {font_path}")
            elif source_desc == "system":
                print(f"[load_local_fonts] 使用系统字体 {first_success_alias} (未找到本地文件 {font_path})")
            elif source_desc == "existing":
                # 字体已存在，无需重复加载
                pass
        else:
            print(
                f"[load_local_fonts] 无法加载字体文件: {font_path} "
                f"(别名尝试: {', '.join(alias_candidates)})"
            )


# 显示主框架
game_name = normal_config.config_normal.game_name
game_version = normal_config.config_normal.verson
title_text = game_name + " " + game_version + " -α测"
root = Tk()
load_local_fonts(root)
# normal_config.config_normal.window_width = root.maxsize()[0]
#读取屏幕长宽
screen_weight = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
#如果设定长宽大于屏幕长宽，则缩小为屏幕长宽
if normal_config.config_normal.window_width + 30 > screen_weight:
    normal_config.config_normal.window_width = screen_weight - 30
if normal_config.config_normal.window_hight + 30 > screen_height:
    normal_config.config_normal.window_hight = screen_height - 30
#字体大小为屏幕宽度除以行数，输入字体大小为普通字体大小-2
now_font_size = int(normal_config.config_normal.window_width / normal_config.config_normal.text_width) * 2
normal_config.config_normal.font_size = now_font_size
normal_config.config_normal.order_font_size = now_font_size - 2
# 设置DPI缩放
# tk_dpi配置说明：100=100%缩放(1.0)，125=125%缩放(1.25)，150=150%缩放(1.5)，0=自动(1.0)
config_dpi = getattr(normal_config.config_normal, 'tk_dpi', 0)
if config_dpi > 0:
    # 使用配置文件指定的DPI值，以100为基准计算scaling
    scaling_factor = config_dpi / 100.0
else:
    # 自动模式：从系统读取实际DPI并计算
    system_dpi = root.winfo_fpixels("1i")
    # 96是Windows标准DPI，以此为基准计算scaling
    scaling_factor = system_dpi / 96.0
root.tk.call("tk", "scaling", scaling_factor)
root.title(title_text)
width = normal_config.config_normal.window_width
#根窗口左上角x坐标-当前窗口左上角x坐标
frm_width = root.winfo_rootx() - root.winfo_x()
win_width = width + 2 * frm_width
height = normal_config.config_normal.window_hight
#同理y坐标
titlebar_height = root.winfo_rooty() - root.winfo_y()
win_height = height + titlebar_height + frm_width
x = root.winfo_screenwidth() // 2 - win_width // 2
y = root.winfo_screenheight() // 2 - win_height // 2
# 从窗口改为最大化
#root.geometry("{}x{}+{}+{}".format(width, height, x, y))
root.state('zoomed')
#隐藏窗口
root.deiconify()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.protocol("WM_DELETE_WINDOW", close_window)
main_frame = ttk.Frame(root, borderwidth=2)
main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

# 使用通用函数获取 logo.png 的绝对路径，兼容打包与开发环境
logo_path = get_resource_path("image/logo.png")

# 将 logo.png 设为主窗口图标，后续所有 Toplevel 窗口会继承该图标
root.iconphoto(True, PhotoImage(file=logo_path))

# 显示窗口
textbox = Text(
    main_frame,
    width=normal_config.config_normal.textbox_width,
    height=normal_config.config_normal.textbox_hight,
    highlightbackground=normal_config.config_normal.background,
    bd=0,
    cursor="",
    #123分别是，\n的上行间距，自动换行行间距，\n的下行间距
    spacing1 = 1,
    spacing2 = 1,
    spacing3 = 1
)
textbox.grid(column=0, row=0, sticky=(N, W, E, S))

# 垂直滚动条
s_vertical = ttk.Scrollbar(main_frame, orient=VERTICAL, command=textbox.yview)
textbox.configure(yscrollcommand=s_vertical.set)
s_vertical.grid(column=1, row=0, sticky=(N, E, S), rowspan=2)

# 输入框背景容器
order_font_data = game_config.config_font[1]
for k in game_config.config_font[0].__dict__:
    if k not in order_font_data.__dict__:
        order_font_data.__dict__[k] = game_config.config_font[0].__dict__[k]
        order_font_data.font = normal_config.config_normal.font
        order_font_data.font_size = normal_config.config_normal.order_font_size
input_background_box = Text(
    main_frame,
    highlightbackground=normal_config.config_normal.background,
    background=normal_config.config_normal.background,
    bd=0,
)
input_background_box.grid(column=0, row=1, sticky=(W, E, S))

cursor_text = "~$"
cursor_width = text_handle.get_text_index(cursor_text)
input_background_box_cursor = Text(
    input_background_box,
    width=cursor_width,
    height=1,
    highlightbackground=order_font_data.background,
    background=order_font_data.background,
    bd=0,
)
input_background_box_cursor.grid(column=0, row=0, sticky=(W, E, S))
input_background_box_cursor.insert("end", cursor_text)
input_background_box_cursor.config(foreground=order_font_data.foreground)

# 输入栏
order = StringVar()
order_font = font.Font(family=order_font_data.font, size=order_font_data.font_size)
inputbox = Entry(
    input_background_box,
    borderwidth=0,
    insertborderwidth=0,
    selectborderwidth=0,
    highlightthickness=0,
    bg=order_font_data.background,
    foreground=order_font_data.foreground,
    selectbackground=order_font_data.selectbackground,
    textvariable=order,
    font=order_font,
    width=normal_config.config_normal.inputbox_width,
)
inputbox.grid(column=1, row=0, sticky=(N, E, S))
normal_font = font.Font(family=order_font_data.font, size=normal_config.config_normal.font_size)


input_event_func = None
send_order_state = False
# when false, send 'skip'; when true, send cmd


from Script.Core import era_image


def send_input(*args):
    """
    发送一条指令
    """
    global input_event_func
    order = get_order()
    if len(cache.input_cache) >= 21:
        if not (order) == "":
            del cache.input_cache[0]
            cache.input_cache.append(order)
            cache.input_position = 0
    else:
        if not (order) == "":
            cache.input_cache.append(order)
            cache.input_position = 0
    input_event_func(order)
    clear_order()


# #######################################################################
# 运行函数
flow_thread = None


def read_queue():
    """
    从队列中获取在前端显示的信息
    """
    while not main_queue.empty():
        quene_str = main_queue.get()
        json_data = json.loads(quene_str)

        if "clear_cmd" in json_data and json_data["clear_cmd"] == "true":
            clear_screen()
        if "clearorder_cmd" in json_data and json_data["clearorder_cmd"] == "true":
            clear_order()
        if "clearcmd_cmd" in json_data:
            cmd_nums = json_data["clearcmd_cmd"]
            if cmd_nums == "all":
                io_clear_cmd()
            else:
                io_clear_cmd(tuple(cmd_nums))
        if "bgcolor" in json_data:
            set_background(json_data["bgcolor"])
        if "set_style" in json_data:
            temp = json_data["set_style"]
            frame_style_def(
                temp["style_name"],
                temp["foreground"],
                temp["background"],
                temp["font"],
                temp["fontsize"],
                temp["bold"],
                temp["underline"],
                temp["italic"],
            )
        if "image" in json_data:
            textbox.image_create("end",image=era_image.image_data[json_data["image"]["image_name"]])

        for c in json_data["content"]:
            if c["type"] == "text":
                c["style"][0] = c["style"][0].replace(" ","")
                now_print(c["text"], style=tuple(c["style"]), tooltip=c.get("tooltip", ""))
            if c["type"] == "cmd":
                c["normal_style"][0] = c["normal_style"][0].replace(" ", "")
                c["on_style"][0] = c["on_style"][0].replace(" ", "")
                io_print_cmd(
                    c["text"],
                    c["num"],
                    c["normal_style"],
                    c["on_style"],
                    c.get("tooltip", ""),
                )
            if c["type"] == "image_cmd":
                io_print_image_cmd(c["text"], c["num"], c.get("tooltip", ""))
            if "\n" in c["text"]:
                if textbox.get("1.0", END).count("\n") > normal_config.config_normal.text_hight * 10:
                    textbox.delete("1.0", str(normal_config.config_normal.text_hight * 5) + ".0")
    root.after(1, read_queue)


def run():
    """
    启动屏幕
    """
    root.after(1, read_queue)
    root.mainloop()


def see_end():
    """
    输出END信息
    """
    textbox.see(END)


def set_background(color):
    """
    设置背景颜色
    Keyword arguments:
    color -- 背景颜色
    """
    textbox.config(insertbackground=color)
    textbox.configure(background=color, selectbackground="red")


# ######################################################################
# ######################################################################
# ######################################################################
# 双框架公共函数

main_queue = None


def bind_return(func):
    """
    绑定输入处理函数
    Keyword arguments:
    func -- 输入处理函数
    """
    global input_event_func
    input_event_func = func


def bind_queue(q):
    """
    绑定信息队列
    Keyword arguments:
    q -- 消息队列
    """
    global main_queue
    main_queue = q


# #######################################################################
# 输出格式化

sys_print = print


def now_print(string, style=("standard",), tooltip: str = ""):
    """
    输出文本
    Keyword arguments:
    string -- 字符串
    style -- 样式序列
    tooltip -- 悬浮提示文本，用于在 Tk 端展示说明
    """
    tooltip_text = tooltip or ""
    start_index = None
    if tooltip_text and string:
        # 记录插入前的位置，便于为新增文本打标签
        start_index = textbox.index("end-1c")
    textbox.insert("end", string, style)
    if tooltip_text and string and start_index is not None:
        end_index = textbox.index("end-1c")
        if textbox.compare(start_index, "<", end_index):
            tag_name = f"text_tooltip_{uuid.uuid4().hex}"
            textbox.tag_add(tag_name, start_index, end_index)

            def enter_func(event=None):
                """鼠标进入文本范围时展示提示。"""
                coords = (event.x_root, event.y_root) if event is not None else None
                _schedule_tooltip(tooltip_text, coords)

            def leave_func(event=None):
                """鼠标离开文本范围时隐藏提示。"""
                _hide_tooltip()

            def motion_func(event=None):
                """鼠标移动时更新提示位置。"""
                if event is not None:
                    _update_tooltip_coords((event.x_root, event.y_root))

            textbox.tag_bind(tag_name, "<Enter>", enter_func)
            textbox.tag_bind(tag_name, "<Leave>", leave_func)
            textbox.tag_bind(tag_name, "<Motion>", motion_func)
    if not string and tooltip_text:
        # 空字符串不创建标签，直接取消已安排的提示
        _hide_tooltip()
    see_end()


def print_cmd(string, style=("standard",)):
    """
    输出文本
    Keyword arguments:
    string -- 字符串
    style -- 样式序列
    """
    textbox.insert("end", string, style)
    see_end()


def clear_screen():
    """
    清屏
    """
    io_clear_cmd()
    textbox.delete("1.0", END)


def frame_style_def(
    style_name: str,
    foreground: str,
    background: str,
    font: str,
    font_size: int,
    bold: str,
    under_line: str,
    italic: str,
):
    """
    定义样式
    Keyword arguments:
    style_name -- 样式名称
    foreground -- 前景色/字体颜色
    background -- 背景色
    font -- 字体
    fontsize -- 字号
    bold -- 加粗
    underline -- 下划线
    italic -- 斜体
    """
    style_name = style_name.replace(" ", "")
    font_list = []
    font_list.append(font)
    font_list.append(font_size)
    if bold == "1":
        font_list.append("bold")
    if under_line == "1":
        font_list.append("underline")
    if italic == "1":
        font_list.append("italic")
    textbox.tag_configure(
        style_name,
        foreground=foreground,
        background=background,
        font=tuple(font_list),
    )


# #########################################################3
# 输入处理函数


def get_order():
    """
    获取命令框中的内容
    """
    return order.get()


def set_order(order_str: str):
    """
    设置命令框中内容
    """
    order.set(order_str)


def clear_order():
    """
    清空命令框
    """
    order.set("")


cmd_tag_map = {}
tooltip_window = None  # 当前悬浮提示所使用的顶层窗口引用
tooltip_after_id = None  # 利用 after() 注册的延时任务编号，用于取消定时器
tooltip_text_cache = ""  # 待显示的提示文本缓存
tooltip_coords = (0, 0)  # 鼠标进入时记录的屏幕坐标，用于定位提示窗口
TOOLTIP_DELAY_MS = 350  # 提示延迟显示的时长，毫秒


def _cancel_tooltip_schedule():
    """取消已经注册的 tooltip 定时任务，无输入，返回值为 None。"""
    global tooltip_after_id
    if tooltip_after_id is not None and textbox.winfo_exists():
        try:
            textbox.after_cancel(tooltip_after_id)
        except Exception:
            pass
    tooltip_after_id = None


def _destroy_tooltip():
    """销毁已有的 tooltip 顶层窗口，无输入，返回值为 None。"""
    global tooltip_window
    if tooltip_window is not None:
        try:
            tooltip_window.destroy()
        except Exception:
            pass
    tooltip_window = None


def _position_tooltip():
    """按照记录的屏幕坐标重新定位 tooltip，无输入，返回值为 None。"""
    if tooltip_window is None:
        return
    x, y = tooltip_coords
    tooltip_window.wm_geometry(f"+{x + 12}+{y + 18}")

def _show_tooltip():
    """显示 tooltip 浮窗，无输入且无返回值。"""
    global tooltip_window, tooltip_after_id
    tooltip_after_id = None
    if not tooltip_text_cache:
        return
    _destroy_tooltip()
    window = Toplevel(textbox)
    window.wm_overrideredirect(True)
    try:
        window.wm_attributes("-topmost", True)
    except Exception:
        pass
    # 计算合适的换行长度，避免提示过宽，从取最大值改为取最小值
    # wrap_length = max(textbox.winfo_width() // 2, 240)
    wrap_length = min(textbox.winfo_width() // 2, 600)
    # 使用全局 now_font_size 作为提示文字字号，保持与游戏文本一致
    tooltip_font = font.Font(family=normal_config.config_normal.font, size=now_font_size)
    label = ttk.Label(
        window,
        text=tooltip_text_cache,
        justify="left",
        background="#fef3c7",
        foreground="#1f2933",
        relief="solid",
        borderwidth=1,
        padding=(6, 3),
        wraplength=wrap_length,
        font=tooltip_font,
    )
    label.pack()
    tooltip_window = window
    _position_tooltip()


def _schedule_tooltip(text: str, coords=None):
    """
    注册 tooltip 的延迟显示任务。
    输入：text 为提示内容字符串，coords 为可选的 (x, y) 坐标；
    输出：无返回值，仅安排 after 定时任务。
    """
    global tooltip_text_cache, tooltip_coords, tooltip_after_id
    tooltip_text_cache = text or ""
    tooltip_coords = coords or (textbox.winfo_pointerx(), textbox.winfo_pointery())
    _cancel_tooltip_schedule()
    if not tooltip_text_cache:
        _destroy_tooltip()
        return
    tooltip_after_id = textbox.after(TOOLTIP_DELAY_MS, _show_tooltip)


def _hide_tooltip():
    """立即隐藏 tooltip，输入输出均为空。"""
    global tooltip_text_cache
    tooltip_text_cache = ""
    _cancel_tooltip_schedule()
    _destroy_tooltip()


def _update_tooltip_coords(coords):
    """
    更新 tooltip 的参考坐标。
    输入：coords 为 (x, y) 元组，表示最新的屏幕坐标；输出：None。
    """
    global tooltip_coords
    tooltip_coords = coords
    if tooltip_window is not None:
        _position_tooltip()


def io_print_cmd(
    cmd_str: str,
    cmd_number: int,
    normal_style="standard",
    on_style="onbutton",
    tooltip: str = "",
):
    """
    打印一条指令
    Keyword arguments:
    cmd_str -- 命令对应文字
    cmd_number -- 命令数字
    normal_style -- 正常显示样式
    on_style -- 鼠标在其上时显示样式
    tooltip -- 鼠标悬停提示文本
    """
    global cmd_tag_map
    cmd_tag_name = str(uuid.uuid1())
    textbox.tag_configure(cmd_tag_name)

    if cmd_number in cmd_tag_map:
        io_clear_cmd(cmd_number)
    cmd_tag_map[cmd_number] = cmd_tag_name

    tooltip_text = tooltip or ""

    def send_cmd(event=None):
        """处理按钮点击事件，输入 event 为 Tk 事件对象，可为 None；无返回值。"""
        global send_order_state
        send_order_state = True
        order.set(cmd_number)
        textbox.configure(cursor="")
        _hide_tooltip()
        send_input(order)

    def enter_func(event=None):
        """响应鼠标进入事件，输入 event 为 Tk 事件对象；无返回值。"""
        # 进入文本按钮时切换高亮样式，并根据需求准备 tooltip
        textbox.tag_remove(
            normal_style,
            textbox.tag_ranges(cmd_tag_name)[0],
            textbox.tag_ranges(cmd_tag_name)[1],
        )
        textbox.tag_add(
            on_style,
            textbox.tag_ranges(cmd_tag_name)[0],
            textbox.tag_ranges(cmd_tag_name)[1],
        )
        cache.wframe_mouse.mouse_leave_cmd = 0
        if tooltip_text:
            coords = (event.x_root, event.y_root) if event is not None else None
            _schedule_tooltip(tooltip_text, coords)

    def leave_func(event=None):
        """响应鼠标离开事件，输入 event 为 Tk 事件对象；无返回值。"""
        # 鼠标离开时恢复原样式并关闭 tooltip
        textbox.tag_add(
            normal_style,
            textbox.tag_ranges(cmd_tag_name)[0],
            textbox.tag_ranges(cmd_tag_name)[1],
        )
        textbox.tag_remove(
            on_style,
            textbox.tag_ranges(cmd_tag_name)[0],
            textbox.tag_ranges(cmd_tag_name)[1],
        )
        textbox.configure(cursor="")
        cache.wframe_mouse.mouse_leave_cmd = 1
        _hide_tooltip()

    def motion_func(event=None):
        """响应鼠标移动事件，输入 event 为 Tk 事件对象；无返回值。"""
        # 鼠标在按钮上移动时更新 tooltip 的屏幕坐标
        if tooltip_text and event is not None:
            _update_tooltip_coords((event.x_root, event.y_root))

    textbox.tag_bind(cmd_tag_name, "<1>", send_cmd)
    textbox.tag_bind(cmd_tag_name, "<Enter>", enter_func)
    textbox.tag_bind(cmd_tag_name, "<Leave>", leave_func)
    textbox.tag_bind(cmd_tag_name, "<Motion>", motion_func)
    print_cmd(cmd_str, style=(cmd_tag_name, normal_style))


def io_print_image_cmd(cmd_str: str, cmd_number: int, tooltip: str = ""):
    """
    打印一个图片按钮
    Keyword arguments:
    cmd_str -- 命令对应图片名称
    cmd_number -- 点击图片响应数字
    tooltip -- 鼠标悬停提示文本
    """
    global cmd_tag_map
    cmd_tag_name = str(uuid.uuid1())
    textbox.tag_configure(cmd_tag_name)
    if cmd_number in cmd_tag_map:
        io_clear_cmd(cmd_number)
    cmd_tag_map[cmd_number] = cmd_tag_name

    tooltip_text = tooltip or ""

    def send_cmd(event=None):
        """处理图片按钮点击事件，输入 event 为 Tk 事件对象，可为 None；无返回值。"""
        global send_order_state
        send_order_state = True
        order.set(cmd_number)
        textbox.configure(cursor="")
        _hide_tooltip()
        send_input(order)

    def enter_func(event=None):
        """响应鼠标进入图片按钮事件，输入 event 为 Tk 事件对象；无返回值。"""
        # 鼠标进入图片按钮时安排 tooltip 延迟显示
        if tooltip_text:
            coords = (event.x_root, event.y_root) if event is not None else None
            _schedule_tooltip(tooltip_text, coords)

    def leave_func(event=None):
        """响应鼠标离开图片按钮事件，输入 event 为 Tk 事件对象；无返回值。"""
        # 鼠标离开图片按钮时立即隐藏 tooltip
        _hide_tooltip()

    def motion_func(event=None):
        """响应鼠标在图片按钮内移动事件，输入 event 为 Tk 事件对象；无返回值。"""
        # 鼠标在图片按钮上移动时刷新 tooltip 位置
        if tooltip_text and event is not None:
            _update_tooltip_coords((event.x_root, event.y_root))

    index = textbox.index("end -1c")
    textbox.image_create(index, image=era_image.image_data[cmd_str])
    textbox.tag_add(cmd_tag_name, index, f"{index} + 1 char")
    textbox.tag_bind(cmd_tag_name, "<1>", send_cmd)
    textbox.tag_bind(cmd_tag_name, "<Enter>", enter_func)
    textbox.tag_bind(cmd_tag_name, "<Leave>", leave_func)
    textbox.tag_bind(cmd_tag_name, "<Motion>", motion_func)
    see_end()


# 清除命令函数
def io_clear_cmd(*cmd_numbers: list):
    """
    清除命令
    Keyword arguments:
    cmd_number -- 命令数字，不输入则清楚当前已有的全部命令
    """
    global cmd_tag_map
    if cmd_numbers:
        for num in cmd_numbers:
            if num in cmd_tag_map:
                tag_ranges = textbox.tag_ranges(cmd_tag_map[num])
                if len(tag_ranges):
                    index_first = tag_ranges[0]
                    index_last = tag_ranges[1]
                    for tag_name in textbox.tag_names(index_first):
                        textbox.tag_remove(tag_name, index_first, index_last)
                    textbox.tag_add("standard", index_first, index_last)
                    textbox.tag_delete(cmd_tag_map[num])
                del cmd_tag_map[num]
    else:
        for num in list(cmd_tag_map.keys()):
            tag_tuple = textbox.tag_ranges(cmd_tag_map[num])
            if len(tag_tuple):
                index_first = tag_tuple[0]
                index_lskip_one_waitast = tag_tuple[1]
                for tag_name in textbox.tag_names(index_first):
                    textbox.tag_remove(tag_name, index_first, index_lskip_one_waitast)
                textbox.tag_add("standard", index_first, index_lskip_one_waitast)
            textbox.tag_delete(cmd_tag_map[num])
        cmd_tag_map.clear()
