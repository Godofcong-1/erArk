from Script.Core import (
    cache_control,
    game_type,
)
from Script.Config import game_config
from Script.UI.Moudle import draw, panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

def get_rich_text_draw_panel(now_text: str) -> panel.LeftDrawTextListPanel:
    """
    根据带富文本标识的字符串构造富文本绘制面板
    参数:
        now_text (str): 含有富文本标签的原始文本
    返回:
        object: 富文本绘制面板对象，包含绘制列表和宽度等属性
    """
    # 创建左侧文本绘制面板实例
    now_draw = panel.LeftDrawTextListPanel()
    rich_text_draw_list = get_rich_text_draw_list(now_text)
    # 将富文本绘制列表添加到绘制面板中
    now_draw.draw_list.append(rich_text_draw_list)
    # 计算绘制面板的总宽度
    for rich_draw in rich_text_draw_list:
        now_draw.width += len(rich_draw.text)
    # 返回构造好的富文本绘制面板
    return now_draw

def get_rich_text_draw_list(now_text: str, base_style: str = "standard", wait_flag: bool = False) -> list:
    """
    获取富文本绘制列表
    Keyword arguments:
    now_text -- 带富文本标识的字符串
    base_style -- 无富文本样式时的默认样式，默认为 "standard"
    wait_flag -- 是否需要等待绘制，默认为False
    """
    rich_text_draw_list = []
    # 调用已有函数获取各字符对应的富文本样式列表
    now_style_list = get_rich_text_print(now_text, base_style)
    # 调用已有函数移除原始文本中的富文本标签，获得实际文本列表
    new_x_list = remove_rich_cache(now_text)
    # 循环处理文本列表，生成绘制对象并合并相同样式的连续文本
    while len(new_x_list) > 0:
        # 创建新的文本绘制对象实例
        now_rich_draw = draw.NormalDraw()
        if wait_flag:
            now_rich_draw = draw.LineFeedWaitDraw()
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
        # 将构造好的绘制对象添加到绘制列表中
        rich_text_draw_list.append(now_rich_draw)
    # 返回构造好的富文本绘制列表
    return rich_text_draw_list

def get_rich_text_print(text_message: str, default_style: str) -> list:
    """
    获取文本的富文本样式列表
    Keyword arguments:
    text_message -- 原始文本
    default_style -- 无富文本样式时的默认样式
    """
    # 解析富文本标签并为每个字符返回其最终要使用的样式。
    # 支持两类标签：
    # 1) 颜色/样式标签：这些由 data/csv/FontConfig.csv 中的名字提供，例如 <green>...</green>
    # 2) 字体修饰符：固定支持的三个标识符 <bold>, <underline>, <italic>，可嵌套/组合使用
    #
    # 返回值为一个与原始文本等长的列表，每个元素是一个样式描述：
    # - 若只有基础样式（颜色）则为字符串，例如 "standard"；
    # - 若包含修饰符则为元组，例如 ("green", "bold", "italic")，以便在 tkinter/web 层
    #   将多个 tag 一起应用（Text.insert 接受一个样式元组）。

    # 可用的基础样式名集合（颜色/字体样式）
    style_name_set = set(game_config.config_font_data.keys())
    # 固定的修饰符集合
    modifier_names = {"bold", "underline", "italic"}
    # 修饰符拼接顺序必须与 Script/Core/io_init.py 中注册组合的顺序一致
    modifier_order = ["bold", "underline", "italic"]

    # 快速判断：如果文本中不包含任何 "<" 则直接返回默认样式列表
    if "<" not in text_message:
        return [default_style] * len(text_message)

    style_list: list = []

    # 使用两个栈来维护当前打开的样式：基础样式栈和修饰符栈。
    # 初始为默认样式与空修饰符集合
    base_stack = [default_style]
    modifier_stack = [set()]

    i = 0
    L = len(text_message)
    while i < L:
        ch = text_message[i]
        if ch == "<":
            # 尝试找到匹配的 '>'，若未找到则把 '<' 当作普通字符处理
            j = text_message.find(">", i)
            if j == -1:
                # 没有闭合，作为普通字符输出当前样式
                current_base = base_stack[-1]
                current_mods = modifier_stack[-1]
                if current_mods:
                    # 生成复合样式名，例如 base_bold_italic
                    # 若基础样式是默认（standard）且未在 config 中声明，则仍返回元组以保持兼容性
                    if current_base in game_config.config_font_data:
                        combo_parts = [m for m in modifier_order if m in current_mods]
                        combo_name = current_base + "_" + "_".join(combo_parts)
                        style_list.append(combo_name)
                    else:
                        style_list.append(tuple([current_base] + [m for m in modifier_order if m in current_mods]))
                else:
                    style_list.append(current_base)
                i += 1
                continue

            tag = text_message[i + 1 : j]
            # 调试打印：解析到的标签以及当前栈顶信息
            # print(f"[RICH_PARSE] pos={i} tag={tag!r} base_stack={base_stack} modifier_stack_top={modifier_stack[-1]}")
            # 结束标签
            if tag.startswith("/"):
                name = tag[1:]
                if name in style_name_set:
                    # 结束基础样式：弹出一个基础样式（如果栈长度大于1）
                    if len(base_stack) > 1:
                        base_stack.pop()
                elif name in modifier_names:
                    # 结束修饰符：弹出修饰符快照（如果栈长度大于1）
                    if len(modifier_stack) > 1:
                        modifier_stack.pop()
                # 忽略未知结束标签
            else:
                # 开始标签
                if tag in style_name_set:
                    base_stack.append(tag)
                elif tag in modifier_names:
                    # 推入新的修饰符集合（基于当前集合加上新修饰符）
                    new_set = set(modifier_stack[-1])
                    new_set.add(tag)
                    modifier_stack.append(new_set)
                else:
                    # 未知标签：忽略（不改变栈）
                    pass

            # 跳过整个标签
            i = j + 1
            continue

        # 普通字符，记录当前样式
        current_base = base_stack[-1]
        current_mods = modifier_stack[-1]
        # ch 是当前字符
        ch = text_message[i]
        if current_mods:
            # 优先使用与注册一致的复合样式名（按 modifier_order 顺序拼接）
            if current_base in game_config.config_font_data:
                combo_parts = [m for m in modifier_order if m in current_mods]
                combo_name = current_base + "_" + "_".join(combo_parts)
                # 打印将要 append 的复合样式名
                # print(f"[RICH_STYLE_APPEND] char={ch!r} -> {combo_name!r} (base={current_base}, mods={combo_parts})")
                style_list.append(combo_name)
            else:
                app = tuple([current_base] + [m for m in modifier_order if m in current_mods])
                # print(f"[RICH_STYLE_APPEND] char={ch!r} -> tuple {app!r}")
                style_list.append(app)
        else:
            # print(f"[RICH_STYLE_APPEND] char={ch!r} -> base {current_base!r}")
            style_list.append(current_base)
        i += 1

    return style_list

def remove_rich_cache(string: str) -> str:
    """
    移除文本中的富文本标签
    Keyword arguments:
    string -- 原始文本
    """
    # 移除基础样式标签（来自 config_font_data）以及我们新增的修饰符标签
    style_name_list = list(game_config.config_font_data.keys())
    modifier_names = ["bold", "underline", "italic"]

    for name in style_name_list:
        head = "<" + name + ">"
        tail = "</" + name + ">"
        if head in string:
            string = string.replace(head, "")
        if tail in string:
            string = string.replace(tail, "")

    # 移除修饰符标签
    for name in modifier_names:
        head = f"<{name}>"
        tail = f"</{name}>"
        if head in string:
            string = string.replace(head, "")
        if tail in string:
            string = string.replace(tail, "")

    return string
