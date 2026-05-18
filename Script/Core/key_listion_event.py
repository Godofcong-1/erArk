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
    py_cmd.focus_cmd()
    if not cache.wframe_mouse.w_frame_up:
        set_wframe_up()
    else:
        mouse_check_push()


def mouse_right_check(event: Event):
    """
    鼠标右键事件处理
    Keyword arguments:
    event -- 鼠标事件
    """
    cache.wframe_mouse.mouse_right = 1
    cache.text_wait = 0
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    if not cache.wframe_mouse.w_frame_up:
        set_wframe_up()
    else:
        mouse_check_push()


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


def mouse_check_push():
    """
    更正鼠标点击状态数据映射
    """
    if not cache.wframe_mouse.mouse_leave_cmd == 0:
        main_frame.send_input()
        cache.wframe_mouse.mouse_leave_cmd = 1
