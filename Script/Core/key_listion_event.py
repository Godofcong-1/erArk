from tkinter import Event
from Script.Core import main_frame, py_cmd, game_type, cache_control

wframe = main_frame.root


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def _set_history_order(history_index: int):
    """
    设置历史命令并同步回溯定位
    Keyword arguments:
    history_index -- 历史命令索引
    """
    cache.input_position = history_index
    main_frame.set_order(cache.input_cache[history_index])


def _get_previous_distinct_index(history_index: int):
    """
    获取向上浏览时的上一条不同命令索引
    Keyword arguments:
    history_index -- 当前历史命令索引
    Return arguments:
    int -- 上一条不同命令索引，若不存在则返回-1
    """
    current_order = cache.input_cache[history_index]
    previous_index = history_index - 1
    while previous_index >= 0 and cache.input_cache[previous_index] == current_order:
        previous_index -= 1
    return previous_index


def _get_next_distinct_index(history_index: int):
    """
    获取向下浏览时的下一条不同命令索引
    Keyword arguments:
    history_index -- 当前历史命令索引
    Return arguments:
    int -- 下一条不同命令索引，若不存在则返回-1
    """
    current_order = cache.input_cache[history_index]
    next_index = history_index + 1
    while next_index < len(cache.input_cache) and cache.input_cache[next_index] == current_order:
        next_index += 1
    if next_index >= len(cache.input_cache):
        return -1
    return next_index


def on_wframe_listion():
    """
    对按键事件进行绑定
    """
    wframe.bind("<ButtonPress-1>", mouse_left_check)
    wframe.bind("<ButtonPress-3>", mouse_right_check)
    wframe.bind("<Return>", main_frame.send_input)
    wframe.bind("<KP_Enter>", main_frame.send_input)
    wframe.bind("<Up>", key_up)
    wframe.bind("<Down>", key_down)


def mouse_left_check(event: Event):
    """
    鼠标左键事件处理
    Keyword arguments:
    event -- 鼠标事件
    """
    # 渲染期输入门禁：未上膛时（黑屏/渲染中、界面未定型）直接丢弃左键，
    # 避免滞留点击在 w_frame_up==0 时提前把逐字等待推进（提前吃掉下一个"按任意键继续"）。
    if not main_frame.input_armed:
        return
    py_cmd.focus_cmd()
    if not cache.wframe_mouse.w_frame_up:
        set_wframe_up()
        # 一次性门：推进逐字等待同样视作消费一次输入，立即撤膛，防止连点残留；
        # 下一次 order_deal 入口的标记会重新上膛。
        main_frame.input_armed = False
    else:
        mouse_check_push(event)


def mouse_right_check(event: Event):
    """
    鼠标右键事件处理
    Keyword arguments:
    event -- 鼠标事件
    """
    cache.wframe_mouse.mouse_right = 1
    cache.text_wait = 0
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    # 渲染期输入门禁：右键"催渲染跳过"是其本职（上方三个标志），渲染期必须保留，故不设门；
    # 但未上膛时不推进逐字等待、也不注入输入，避免右键在渲染期提前推进/打出未见过的命令。
    if not main_frame.input_armed:
        return
    if not cache.wframe_mouse.w_frame_up:
        set_wframe_up()
    else:
        mouse_check_push(event)


def key_up(event: Event):
    """
    键盘上键事件处理
    Keyword arguments:
    event -- 键盘事件
    """
    if len(cache.input_cache) == 0:
        return

    if not cache.input_cache_browsing:
        cache.input_cache_draft = main_frame.get_order()
        cache.input_cache_browsing = True
        cache.input_position = len(cache.input_cache)

    if cache.input_position > len(cache.input_cache):
        cache.input_position = len(cache.input_cache)

    if cache.input_position == len(cache.input_cache):
        cache.input_position -= 1
        _set_history_order(cache.input_position)
    elif cache.input_position > 0:
        previous_index = _get_previous_distinct_index(cache.input_position)
        if previous_index >= 0:
            cache.input_position = previous_index
            _set_history_order(cache.input_position)


def key_down(event: Event):
    """
    键盘下键事件处理
    Keyword arguments:
    event -- 键盘事件
    """
    if len(cache.input_cache) == 0:
        return

    if not cache.input_cache_browsing:
        return

    if cache.input_position < len(cache.input_cache) - 1:
        next_index = _get_next_distinct_index(cache.input_position)
        if next_index >= 0:
            cache.input_position = next_index
            _set_history_order(next_index)
            return

    if cache.input_position == len(cache.input_cache) - 1:
        cache.input_position = 0
        cache.input_cache_browsing = False
        main_frame.set_order(cache.input_cache_draft)
        cache.input_cache_draft = ""


def set_wframe_up():
    """
    修正逐字输出状态为nowait
    """
    cache.wframe_mouse.w_frame_up = 1
    cache.wframe_mouse.w_frame_lines_up = 1


def mouse_check_push(event: Event = None):
    """
    点击时现场判断落点是否命中指令按钮 tag，据此决定是否推进"按任意键继续"等待
    Keyword arguments:
    event -- 鼠标事件对象；用其屏幕坐标换算 textbox 内坐标做命中查询，None 时直接推进"按任意键继续"等待
    """
    # 无事件对象时无法做命中查询，直接推进等待输入
    if event is None:
        main_frame.send_input()
        return
    textbox = main_frame.textbox
    # 窗口级绑定的 event.x/y 相对 event.widget，不可直接用，故以屏幕坐标换算 textbox 内部坐标
    tx = event.x_root - textbox.winfo_rootx()
    ty = event.y_root - textbox.winfo_rooty()
    # 落点若在 textbox 边界外，视作空白点击，推进等待输入
    if tx < 0 or ty < 0 or tx >= textbox.winfo_width() or ty >= textbox.winfo_height():
        main_frame.send_input()
        return
    # 取落点处的所有 tag，与已登记的指令按钮 tag（含文字与图片按钮，均登记在 cmd_tag_map）求交
    point_tags = set(textbox.tag_names(f"@{tx},{ty}"))
    cmd_tags = set(main_frame.cmd_tag_map.values())
    # 命中任一指令按钮 tag → 本次为按钮点击，已由按钮回调处理，不再重复注入输入
    if point_tags & cmd_tags:
        return
    # 未命中按钮 → 推进等待输入
    main_frame.send_input()
