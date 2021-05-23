from tkinter import Event
from Script.Core import main_frame, py_cmd, game_type, cache_control

wframe = main_frame.root


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


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
    while cache.input_position == 0:
        cache.input_position = len(cache.input_cache)
    while cache.input_position <= 21 and cache.input_position > 1:
        cache.input_position -= 1
        inpot_id = cache.input_position
        try:
            main_frame.order.set(cache.input_cache[inpot_id])
            break
        except KeyError:
            cache.input_position += 1


def key_down(event: Event):
    """
    键盘下键事件处理
    Keyword arguments:
    event -- 键盘事件
    """
    if cache.input_position > 0 and cache.input_position < len(cache.input_cache) - 1:
        try:
            cache.input_position += 1
            input_id = cache.input_position
            main_frame.order.set(cache.input_cache[input_id])
        except KeyError:
            cache.input_position -= 1
    elif cache.input_position == len(cache.input_cache) - 1:
        cache.input_position = 0
        main_frame.order.set("")


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
