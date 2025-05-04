from Script.Core import (
    cache_control,
    game_type,
)
from Script.Config import game_config
from Script.UI.Moudle import draw, panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

def get_rich_text_draw_panel(now_text: str) -> object:
    """
    根据带富文本标识的字符串构造富文本绘制面板
    参数:
        now_text (str): 含有富文本标签的原始文本
    返回:
        object: 富文本绘制面板对象，包含绘制列表和宽度等属性
    """
    # 创建左侧文本绘制面板实例
    now_draw = panel.LeftDrawTextListPanel()
    # 调用已有函数获取各字符对应的富文本样式列表
    now_style_list = get_rich_text_print(now_text, "standard")
    # 调用已有函数移除原始文本中的富文本标签，获得实际文本列表
    new_x_list = remove_rich_cache(now_text)
    # 循环处理文本列表，生成绘制对象并合并相同样式的连续文本
    while len(new_x_list) > 0:
        # 创建新的文本绘制对象实例
        now_rich_draw = draw.NormalDraw()
        # 为当前绘制对象初始化文本和样式
        now_rich_draw.text = new_x_list[0]
        now_rich_draw.style = now_style_list[0]
        # 移除已处理的首个字符及对应样式
        now_style_list = now_style_list[1:]
        new_x_list = new_x_list[1:]
        # 合并连续字符样式相同的文本
        while len(new_x_list) > 0:
            # 如果下一字符的样式与当前绘制对象样式不同，则跳出合并循环
            if now_style_list[0] != now_rich_draw.style:
                break
            # 合并文本，并移除合并的字符和对应样式
            now_rich_draw.text += new_x_list[0]
            now_style_list = now_style_list[1:]
            new_x_list = new_x_list[1:]
        # 将构造好的绘制对象添加到绘制面板中，并更新面板宽度
        now_draw.draw_list.append(now_rich_draw)
        now_draw.width += len(now_rich_draw.text)
    # 返回构造好的富文本绘制面板
    return now_draw

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
