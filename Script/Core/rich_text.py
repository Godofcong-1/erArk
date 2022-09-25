from Script.Core import (
    cache_control,
    game_type,
)
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def get_rich_text_print(text_message: str, default_style: str) -> list:
    """
    获取文本的富文本样式列表
    Keyword arguments:
    text_message -- 原始文本
    default_style -- 无富文本样式时的默认样式
    """
    style_name_list = game_config.config_font_data
    style_index = 0
    style_last_index = None
    style_max_index = None
    style_list = []
    for key in style_name_list:
        if key == default_style:
            continue
        style_text_head = "<" + key + ">"
        if style_text_head in text_message:
            style_index = 1
            break
    if style_index == 0:
        style_list = [default_style] * len(text_message)
    else:
        # print(f"debug default_style = {default_style}")
        # print(f"debug text_message = {text_message}")
        cache.output_text_style = default_style
        for i in range(0, len(text_message)):
            # print(f"debug i = {i}")
            input_text_style_size = text_message.find(">", i) + 1
            input_text_style = text_message[i + 1 : input_text_style_size - 1]
            # print(f"debug input_text_style = {input_text_style}")
            if text_message[i] == "<" and (
                (input_text_style in style_name_list) or (input_text_style[1:] in style_name_list)
            ):
                style_last_index = i
                style_max_index = input_text_style_size
                if input_text_style[0] == "/":
                    if cache.text_style_position == 1:
                        cache.output_text_style = default_style
                        cache.text_style_position = 0
                        cache.text_style_cache = [default_style]
                    else:
                        cache.output_text_style = default_style
                        cache.text_style_position = 0
                        cache.text_style_cache = [default_style]
                else:
                    cache.text_style_position = len(cache.text_style_cache)
                    cache.text_style_cache.append(input_text_style)
                    cache.output_text_style = cache.text_style_cache[cache.text_style_position]
            else:
                if style_last_index is not None:
                    if i == len(text_message):
                        cache.text_style_position = 0
                        cache.output_text_style = "standard"
                        cache.text_style_cache = ["standard"]
                    if i not in range(style_last_index, style_max_index):
                        style_list.append(cache.output_text_style)
                else:
                    style_list.append(cache.output_text_style)
        # print(f"debug style_list = {style_list}")
    return style_list


def remove_rich_cache(string: str) -> str:
    """
    移除文本中的富文本标签
    Keyword arguments:
    string -- 原始文本
    """
    style_name_list = list(game_config.config_font_data.keys())
    for i in range(0, len(style_name_list)):
        style_text_head = "<" + style_name_list[i] + ">"
        style_text_tail = "</" + style_name_list[i] + ">"
        if style_text_head in string:
            string = string.replace(style_text_head, "")
            string = string.replace(style_text_tail, "")
    return string
