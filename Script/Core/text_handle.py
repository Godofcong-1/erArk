from wcwidth import wcswidth
from Script.Config import game_config, normal_config
import functools
import re

# 预编译样式标签的正则，按需构建一次
_STYLE_PATTERN = None

def align(text: str, just="left", only_fix=False, columns=1, text_width=None) -> str:
    """
    文本对齐处理函数
    Keyword arguments:
    text -- 需要进行对齐处理的文本
    just -- 文本的对齐方式(right/center/left) (default 'left')
    only_fix -- 只返回对齐所需要的补全文本 (default False)
    columns -- 将行宽平分指定列后，再进行对齐补全 (default 1)
    text_width -- 指定行宽，为None时将使用game_config中的配置 (default None)
    Return arguments:
    str -- 对齐后的文本
    """
    count_index = get_text_index(text)
    if text_width is None:
        width = normal_config.config_normal.text_width
        width = int(width / columns)
    else:
        width = int(text_width)
    if just == "right":
        if only_fix:
            return " " * (width - count_index)
        else:
            return " " * (width - count_index) + text
    elif just == "left":
        if only_fix:
            return " " * (width - count_index)
        else:
            return text + " " * (width - count_index)
    elif just == "center":
        width_i = width / 2
        count_i = count_index / 2
        if only_fix:
            return " " * int(width_i - count_i)
        else:
            return " " * int(width_i - count_i) + text + " " * int(width_i - count_i)
    return ""

def _build_style_pattern():
    global _STYLE_PATTERN
    # 样式名来自 config_font_data 的 key，形如 <name> 与 </name>
    style_names = list(game_config.config_font_data.keys())
    if not style_names:
        _STYLE_PATTERN = None
        return
    # 对样式名做转义，避免正则特殊字符
    escaped = [re.escape(n) for n in style_names]
    # 形如 </?(name1|name2|...)>
    _STYLE_PATTERN = re.compile(r"</?(?:%s)>" % "|".join(escaped))

@functools.lru_cache(maxsize=256)
def _char_width(ch: str) -> int:
    """单字符显示宽度的小缓存；wcswidth(ch)<=0 时按 1 处理"""
    w = wcswidth(ch)
    return 1 if (w is None or w < 0) else w

@functools.lru_cache(maxsize=8192)
def get_text_index(text: str) -> int:
    """
    计算文本最终显示的真实长度（带样式标签的文本）
    - 若包含样式标签，先移除；再用 wcswidth 一次性计算
    - wcswidth 返回负值时回退为逐字符求和
    - 启用 LRU 缓存（8192 项）以复用常见 UI 文本与模板
    """
    # fast path：无样式符号，直接整串 wcswidth
    cleaned = text
    if "<" in text:
        # 按需构建样式正则（仅首次）
        if _STYLE_PATTERN is None:
            _build_style_pattern()
        if _STYLE_PATTERN is not None:
            cleaned = _STYLE_PATTERN.sub("", text)
        else:
            # 无样式配置时退化为原文本
            cleaned = text

    total = wcswidth(cleaned)
    if total is not None and total >= 0:
        return total

    # 回退：逐字符求宽
    s = 0
    for ch in cleaned:
        s += _char_width(ch)
    return s


def full_to_half_text(ustring: str) -> str:
    """
    将全角字符串转换为半角
    Keyword arguments:
    ustring -- 要转换的全角字符串
    """
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif inside_code >= 65281 and inside_code <= 65374:
            inside_code -= 65248
        aaa = chr(inside_code)
        rstring += aaa
    return rstring


def id_index(now_id: int) -> str:
    """
    生成命令id文本
    Keyword arguments:
    now_id -- 命令id
    Return arguments:
    str -- id文本
    """
    return f"[{str(now_id).zfill(3)}]"


def number_to_symbol_string(value: float) -> str:
    """
    数字转换为带正负数符号的数字字符串
    Keyword arguments:
    value -- 要转换的数字
    Return arguments:
    str -- 转换后的字符串
    """
    symbol = ""
    if value >= 0:
        symbol = "+"
    return f"{symbol}{value}"
