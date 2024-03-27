import time
from typing import List
from types import FunctionType
from Script.Core import (
    text_handle,
    io_init,
    py_cmd,
    flow_handle,
    cache_control,
    game_type,
)
from Script.Config import game_config

bar_list = set(game_config.config_bar_data.keys())
chara_list = set(game_config.config_image_data.keys())
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


class NormalDraw:
    """通用文本绘制类型"""

    style: str = "standard"
    """ 文本的样式 """

    def __init__(self):
        """初始化绘制对象"""
        self.width: int = 0
        """ 当前最大可绘制宽度 """
        self.text = ""
        """ 当前要绘制的文本 """

    def __len__(self) -> int:
        """
        获取当前要绘制的文本的长度
        Return arguments:
        int -- 文本长度
        """
        text_index = text_handle.get_text_index(self.text)
        if text_index > self.width:
            return int(self.width)
        return int(text_index)

    def draw(self):
        """绘制文本"""
        if int(len(self)) > int(self.width):
            now_text = ""
            if self.width > 0:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                    break
                now_text = now_text[:-2] + "~"
            io_init.era_print(now_text, self.style)
        else:
            io_init.era_print(self.text, self.style)


class WaitDraw(NormalDraw):
    """绘制并等待玩家鼠标左右键或输入回车"""

    def draw(self):
        """绘制文本"""
        if int(len(self)) > int(self.width):
            now_text = ""
            if self.width > 0:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                    break
                now_text = now_text[:-2] + "~"
            io_init.era_print(now_text, self.style)
        else:
            io_init.era_print(self.text, self.style)
        if not cache.wframe_mouse.w_frame_skip_wait_mouse and int(len(self)):
            flow_handle.askfor_wait()


class LineFeedWaitDraw(NormalDraw):
    """每次换行时等待玩家左右键输入或输入回车"""

    def draw(self):
        """绘制文本"""
        text_list = self.text.split(r"\n")
        for text in text_list:
            now_width = text_handle.get_text_index(text)
            if int(now_width) > int(self.width):
                now_text = ""
                if now_width > 0:
                    for i in text:
                        if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < now_width:
                            now_text += i
                        break
                    now_text = now_text[:-2] + "~"
                io_init.era_print(now_text, self.style)
            else:
                io_init.era_print(text, self.style)
            if not cache.wframe_mouse.w_frame_skip_wait_mouse:
                flow_handle.askfor_wait()
            else:
                time.sleep(0.001)
            io_init.era_print("\n")


class ImageDraw:
    """
    图片绘制
    Keyword arguments:
    image_name -- 图片id
    image_path -- 图片所在路径 (default '')
    """

    def __init__(self, image_name: str):
        """初始化绘制对象"""
        self.image_name = image_name
        """ 图片id """
        self.width = 1
        """ 图片宽度 """

    def draw(self):
        """绘制图片"""
        io_init.image_print(self.image_name)

    def __len__(self) -> int:
        """图片绘制宽度"""
        return int(self.width)


class BarDraw:
    """比例条绘制"""

    def __init__(self):
        """初始化绘制对象"""
        self.width = 0
        """ 比例条最大长度 """
        self.bar_id = ""
        """ 比例条类型id """
        self.draw_list: List[ImageDraw] = []
        """ 比例条绘制对象列表 """

    def set(self, bar_id: str, max_value: int, value: int):
        """
        设置比例条数据
        Keyword arguments:
        bar_id -- 比例条id
        max_value -- 最大数值
        value -- 当前数值
        """
        if self.width > 0:
            proportion = 0
            if self.width > 1:
                proportion = int(value / max_value * self.width)
            fix_bar = int(self.width - proportion)
            # print("bar_id =",bar_id)
            # print("game_config.config_bar_data[bar_id] =",game_config.config_bar_data[bar_id])
            # print("game_config.config_bar[game_config.config_bar_data[bar_id]] =",game_config.config_bar[game_config.config_bar_data[bar_id]])
            style_data = game_config.config_bar[game_config.config_bar_data[bar_id]]
            for i in range(proportion):
                now_draw = ImageDraw(style_data.ture_bar)
                now_draw.width = style_data.width
                self.draw_list.append(now_draw)
            for i in range(fix_bar):
                now_draw = ImageDraw(style_data.null_bar)
                now_draw.width = style_data.width
                self.draw_list.append(now_draw)

    def draw(self):
        """绘制比例条"""
        for bar in self.draw_list:
            bar.draw()

    def __len__(self) -> int:
        """
        获取比例条长度
        Return arguments:
        int -- 比例条长度
        """
        return len(self.draw_list)


class CharaDraw:
    """人物图片绘制"""

    def __init__(self):
        """初始化绘制对象"""
        self.width = 0
        """ 人物最大长度 """
        self.chara_id = ""
        """ 人物类型id """
        self.draw_list: List[ImageDraw] = []
        """ 人物绘制对象列表 """

    def set(self, chara_id: int):
        """
        设置人物数据
        Keyword arguments:
        chara_id -- 人物id
        max_value -- 最大数值
        value -- 当前数值
        """
        if self.width > 0:
            # print("chara_id =",chara_id)
            # print("game_config.config_image_data[chara_id] =",game_config.config_image_data[chara_id])
            # print("game_config.config_image[game_config.config_image_data[chara_id]] =",game_config.config_image[game_config.config_image_data[chara_id]])
            style_data = game_config.config_image[game_config.config_image_data[chara_id]]
            now_draw = ImageDraw(style_data.image_name)
            now_draw.width = style_data.width
            self.draw_list.append(now_draw)

    def draw(self):
        """绘制人物"""
        for bar in self.draw_list:
            bar.draw()

    def __len__(self) -> int:
        """
        获取人物长度
        Return arguments:
        int -- 人物长度
        """
        return len(self.draw_list)


class InfoBarDraw:
    """带有文本和数值描述的比例条 例: 生命:[图片](2000/2000)"""

    def __init__(self):
        """初始化绘制对象"""
        self.width: int = 0
        """ 比例条最大长度 """
        self.bar_id: str = ""
        """ 比例条类型id """
        self.text: str = ""
        """ 比例条描述文本 """
        self.draw_list: List[ImageDraw] = []
        """ 比例条绘制对象列表 """
        self.scale: float = 1
        """ 比例条绘制区域占比 """
        self.max_value: int = 0
        """ 最大数值 """
        self.value: int = 0
        """ 当前数值 """

    def set(self, bar_id: str, max_value: int, value: int, text: str):
        """
        设置比例条数据
        Keyword arguments:
        bar_id -- 比例条id
        max_value -- 最大数值
        value -- 当前数值
        text -- 描述文本
        """
        self.text = text
        self.max_value = max_value
        self.value = value
        now_max_width = int(self.width * self.scale)
        info_draw = NormalDraw()
        info_draw.width = int(now_max_width / 3)
        info_draw.text = f"{text}["
        value_draw = NormalDraw()
        value_draw.width = int(now_max_width / 3)
        value_draw.text = f"]({value}/{max_value})"
        self.bar_id = bar_id
        bar_draw = BarDraw()
        bar_draw.width = now_max_width - len(info_draw) - len(value_draw)
        bar_draw.set(self.bar_id, max_value, value)
        fix_width = int((self.width - now_max_width) / 2)
        fix_draw = NormalDraw()
        fix_draw.text = " " * fix_width
        fix_draw.width = fix_width
        self.draw_list = [fix_draw, info_draw, bar_draw, value_draw, fix_draw]

    def draw(self):
        """绘制比例条"""
        for bar in self.draw_list:
            bar.draw()


class InfoCharaDraw:
    """带有文本的人物图像 例: [阿米娅]:[图片]"""

    def __init__(self):
        """初始化绘制对象"""
        self.width: int = 0
        """ 比例条最大长度 """
        self.bar_id: str = ""
        """ 比例条类型id """
        self.text: str = ""
        """ 比例条描述文本 """
        self.draw_list: List[ImageDraw] = []
        """ 比例条绘制对象列表 """
        self.scale: float = 1
        """ 比例条绘制区域占比 """
        self.max_value: int = 0
        """ 最大数值 """
        self.value: int = 0
        """ 当前数值 """

    def set(self, bar_id: str, max_value: int, value: int, text: str):
        """
        设置比例条数据
        Keyword arguments:
        bar_id -- 比例条id
        max_value -- 最大数值
        value -- 当前数值
        text -- 描述文本
        """
        self.text = text
        self.max_value = max_value
        self.value = value
        now_max_width = int(self.width * self.scale)
        info_draw = NormalDraw()
        info_draw.width = int(now_max_width / 3)
        info_draw.text = f"{text}["
        value_draw = NormalDraw()
        value_draw.width = int(now_max_width / 3)
        value_draw.text = f"]({value}/{max_value})"
        self.bar_id = bar_id
        bar_draw = BarDraw()
        bar_draw.width = now_max_width - len(info_draw) - len(value_draw)
        bar_draw.set(self.bar_id, max_value, value)
        fix_width = int((self.width - now_max_width) / 2)
        fix_draw = NormalDraw()
        fix_draw.text = " " * fix_width
        fix_draw.width = fix_width
        self.draw_list = [fix_draw, info_draw, bar_draw, value_draw, fix_draw]

    def draw(self):
        """绘制比例条"""
        for bar in self.draw_list:
            bar.draw()


class Button:
    """
    按钮绘制
    Keyword arguments:
    text -- 按钮文本
    return_text -- 点击按钮响应文本
    normal_style -- 按钮默认样式
    on_mouse_style -- 鼠标悬停时样式
    cmd_func -- 按钮响应事件函数
    args -- 传给事件响应函数的参数列表
    """

    def __init__(
            self,
            text: str,
            return_text: str,
            normal_style="standard",
            on_mouse_style="onbutton",
            cmd_func=None,
            args=(),
    ):
        """初始化绘制对象"""
        self.text: str = text
        """ 按钮文本 """
        self.return_text: str = return_text
        """ 点击按钮响应文本 """
        self.normal_style: str = normal_style
        """ 按钮默认样式 """
        self.on_mouse_style: str = on_mouse_style
        """ 鼠标悬停时样式 """
        self.width: int = 0
        """ 按钮文本的最大宽度 """
        self.cmd_func: FunctionType = cmd_func
        """ 按钮响应事件函数 """
        self.args = args
        """ 传给事件响应函数的参数列表 """

    def __len__(self) -> int:
        """
        获取按钮文本长度
        Return arguments:
        int -- 文本长度
        """
        return text_handle.get_text_index(self.text)

    def __lt__(self, other):
        """
        比较两个button对象的文本长度
        Keyword arguments:
        other -- 要比较的button对象
        Return arguments:
        bool -- 大小校验
        """
        return len(self) < len(other)

    def draw(self):
        """绘制按钮"""
        if self.width < len(self):
            now_text = ""
            if self.width > 0:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                        continue
                    break
                now_text = now_text[:-2] + "~"
            py_cmd.pcmd(
                now_text,
                self.return_text,
                normal_style=self.normal_style,
                on_style=self.on_mouse_style,
            )
        else:
            py_cmd.pcmd(
                self.text,
                self.return_text,
                normal_style=self.normal_style,
                on_style=self.on_mouse_style,
                cmd_func=self.cmd_func,
                arg=self.args,
            )


class ImageButton:
    """
    图片按钮绘制
    Keyword arguments:
    text -- 图片id
    return_text -- 点击按钮响应文本
    width -- 按钮的文本宽度(自己定义，对齐函数以其为参照)
    cmd_func -- 按钮响应事件函数
    args -- 传给事件响应函数的参数列表
    """

    def __init__(
            self,
            text: str,
            return_text: str,
            width: int,
            cmd_func=None,
            args=(),
    ):
        """初始化绘制对象"""
        self.text: str = text
        """ 按钮文本 """
        self.return_text: str = return_text
        """ 点击按钮响应文本 """
        self.width: int = 0
        """ 按钮文本的最大宽度 """
        self.cmd_func: FunctionType = cmd_func
        """ 按钮响应事件函数 """
        self.args = args
        """ 传给事件响应函数的参数列表 """

    def __len__(self) -> int:
        """
        获取图片的绘制宽度
        Return arguments:
        int -- 绘制宽度
        """
        return self.width

    def draw(self):
        """绘制按钮"""
        py_cmd.pimagecmd(self.text, self.return_text, self.cmd_func, self.args)


class CenterButton:
    """
    居中按钮绘制
    Keyword arguments:
    text -- 按钮原始文本
    return_text -- 点击按钮响应文本
    width -- 按钮最大绘制宽度
    fix_text -- 对齐用补全文本
    normal_style -- 按钮默认样式
    on_mouse_style -- 鼠标悬停时样式
    cmd_func -- 按钮响应事件函数
    args -- 传给事件响应函数的参数列表
    """

    def __init__(
            self,
            text: str,
            return_text: str,
            width: int,
            fix_text=" ",
            normal_style="standard",
            on_mouse_style="onbutton",
            cmd_func: FunctionType = None,
            args=(),
    ):
        """初始化绘制对象"""
        self.text: str = text
        """ 按钮文本 """
        self.return_text: str = return_text
        """ 点击按钮响应文本 """
        self.fix_text: str = fix_text
        """ 对齐用补全文本 """
        self.normal_style: str = normal_style
        """ 按钮默认样式 """
        self.on_mouse_style: str = on_mouse_style
        """ 鼠标悬停时样式 """
        self.width: int = width
        """ 按钮文本的最大宽度 """
        self.cmd_func: FunctionType = cmd_func
        """ 按钮响应事件函数 """
        self.args = args
        """ 传给事件响应函数的参数列表 """

    def __len__(self) -> int:
        """
        获取按钮文本长度
        Return arguments:
        int -- 文本长度
        """
        return int(self.width)

    def __it__(self, other: Button):
        """
        比较两个button对象的文本长度
        Keyword arguments:
        other -- 要比较的button对象
        Return arguments:
        bool -- 大小校验
        """
        return self.width < other.width

    def draw(self):
        """绘制按钮"""
        if self.width < text_handle.get_text_index(self.text):
            now_text = ""
            if self.width > 0:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                    break
                now_text = now_text[:-2] + "~"
        else:
            now_text = text_handle.align(self.text, "center", 0, 1, self.width)
            now_width = self.width - text_handle.get_text_index(now_text)
            now_text = " " * int(now_width) + now_text
        py_cmd.pcmd(
            now_text,
            self.return_text,
            normal_style=self.normal_style,
            on_style=self.on_mouse_style,
            cmd_func=self.cmd_func,
            arg=self.args,
        )


class LeftButton(CenterButton):
    """
    左对齐按钮绘制
    Keyword arguments:
    text -- 按钮原始文本
    return_text -- 点击按钮响应文本
    width -- 按钮最大绘制宽度
    fix_text -- 对齐用补全文本
    normal_style -- 按钮默认样式
    on_mouse_style -- 鼠标悬停时样式
    cmd_func -- 按钮响应事件函数
    args -- 传给事件响应函数的参数列表
    """

    def draw(self):
        """绘制按钮"""
        if self.width < text_handle.get_text_index(self.text):
            now_text = ""
            if self.width > 0:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                    break
                now_text = now_text[:-2] + "~"
        else:
            now_text = text_handle.align(self.text, "left", 0, 1, self.width)
            now_width = self.width - text_handle.get_text_index(now_text)
            now_text = " " * int(now_width) + now_text
        py_cmd.pcmd(
            now_text,
            self.return_text,
            normal_style=self.normal_style,
            on_style=self.on_mouse_style,
            cmd_func=self.cmd_func,
            arg=self.args,
        )


class LineDraw:
    """
    绘制线条文本
    Keyword arguments:
    text -- 用于绘制线条的文本
    width -- 线条宽度
    style -- 当前默认文本样式
    """

    def __init__(self, text: str, width: int, style="standard"):
        """初始化绘制对象"""
        self.text = text
        """ 用于绘制线条的文本 """
        self.style = style
        """ 文本样式 """
        self.width = width
        """ 线条宽度 """

    def __len__(self) -> int:
        """
        获取当前要绘制的文本的长度
        Return arguments:
        int -- 文本长度
        """
        return self.width

    def draw(self):
        """绘制线条"""
        text_index = text_handle.get_text_index(self.text)
        text_num = self.width / text_index
        now_draw = NormalDraw()
        now_draw.width = self.width
        now_draw.text = self.text * int(text_num) + "\n"
        now_draw.style = self.style
        now_draw.draw()


class TitleLineDraw:
    """
    绘制标题线文本
    Keyword arguments:
    text -- 标题
    width -- 标题线线条宽度
    line -- 用于绘制线条的文本
    frame -- 用于绘制标题边框的文本
    style -- 线条样式
    title_style -- 标题样式
    frame_style -- 标题边框样式
    """

    def __init__(
            self,
            title: str,
            width: int,
            line: str = "=",
            frame="口",
            style="standard",
            title_style="littletitle",
            frame_style="littletitle",
    ):
        """初始化绘制对象"""
        self.title = title
        """ 标题 """
        self.width = width
        """ 线条宽度 """
        self.line = line
        """ 用于绘制线条的文本 """
        self.frame = frame
        """ 用于绘制标题边框的文本 """
        self.style = style
        """ 线条默认样式 """
        self.title_style = title_style
        """ 标题样式 """
        self.frame_style = frame_style
        """ 标题边框样式 """

    def draw(self):
        """绘制线条"""
        title_draw = NormalDraw()
        title_draw.width = self.width
        title_draw.style = self.title_style
        title_draw.text = f" {self.title} "
        fix_width = self.width - len(title_draw)
        if fix_width < 0:
            fix_width = 0
        frame_width = int(fix_width / 2)
        frame_draw = NormalDraw()
        frame_draw.width = frame_width
        frame_draw.style = self.frame_style
        frame_draw.text = self.frame
        line_width = int(fix_width / 2 - len(frame_draw))
        if line_width < 0:
            line_width = 0
        line_draw = NormalDraw()
        line_draw.width = line_width
        line_draw.style = self.style
        line_draw.text = self.line * line_width
        for text in [line_draw, frame_draw, title_draw, frame_draw, line_draw]:
            text.draw()
        io_init.era_print("\n")


class LittleTitleLineDraw:
    """
    绘制小标题线文本
    Keyword arguments:
    title -- 标题
    width -- 标题线线条宽度
    line -- 用于绘制线条的文本
    style -- 线条样式
    title_style -- 标题样式
    """

    def __init__(self, title: str, width: int, line: str = "=", style="standard", title_style="sontitle"):
        """初始化绘制对象"""
        self.title = title
        """ 标题 """
        self.width = width
        """ 线条宽度 """
        self.line = line
        """ 用于绘制线条的文本 """
        self.style = style
        """ 线条默认样式 """
        self.title_style = title_style
        """ 标题样式 """
        self.line_feed: bool = True
        """ 线尾换行 """

    def draw(self):
        """绘制线条"""
        title_draw = NormalDraw()
        title_draw.width = self.width
        title_draw.text = self.title
        title_draw.style = self.title_style
        line_a_width = int(self.width / 16) - len(title_draw)
        if line_a_width < 0:
            line_a_width = 0
        line_a = NormalDraw()
        line_a.width = line_a_width
        line_a.style = self.style
        line_a.text = self.line * line_a_width
        line_b = NormalDraw()
        line_b.width = self.width - len(title_draw) - len(line_a)
        line_b.style = self.style
        line_b.text = self.line * int(line_b.width)
        for value in [line_a, title_draw, line_b]:
            value.draw()
        if self.line_feed:
            io_init.era_print("\n")


class CenterDraw(NormalDraw):
    """居中绘制文本"""

    def __gt__(self, other) -> bool:
        return int(len(self)) > int(len(other))

    def draw(self):
        """绘制文本"""
        self.width = int(self.width)
        # print("int(len(self)) :",int(len(self)))
        # print("int(self.width) :",int(self.width))
        # print("self.text :",self.text)
        if int(len(self)) > int(self.width):
            # print("第一个分支")
            now_text = ""
            if self.width > 0:
                for i in self.text:
                    print("i :", i)
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        # print("now_text（中间的第一次） :",now_text)
                        now_text += i
                        # print("now_text（中间的第二次） :",now_text)
                    break
                now_text = now_text[:-2] + "~"
            # print("now_text（第一次） :",now_text)
            io_init.era_print(now_text, self.style)
        elif int(len(self)) > int(self.width) - 1:
            now_text = " " + self.text
        elif int(len(self)) > int(self.width) - 2:
            now_text = " " + self.text + " "
        else:
            now_text = text_handle.align(self.text, "center", 0, 1, self.width)
        if int(len(self)) < int(self.width):
            now_text += " " * (int(self.width) - text_handle.get_text_index(now_text))
        # print("now_text（第二次） :",now_text)
        io_init.era_print(now_text, self.style)


class CenterDrawImage(NormalDraw):
    """居中绘制图片_现阶段为立绘限定"""

    def __gt__(self, other) -> bool:
        return int(len(self)) > int(len(other))

    def draw(self):
        """绘制图片"""
        self.width = int(self.width)
        print("int(len(self)) :", int(len(self)))
        print("int(self.width) :", int(self.width))
        if int(len(self)) > int(self.width):
            print("第一个分支")
            now_image = ""
            if self.width > 0:
                for i in self.text:
                    if text_handle.get_text_index(now_image) + text_handle.get_text_index(i) < self.width:
                        now_image += i
                    break
                now_image = now_image[:-2] + "~"
            io_init.era_print(now_image)
        elif int(len(self)) > int(self.width) - 1:
            now_image = " " + self.text
        elif int(len(self)) > int(self.width) - 2:
            now_image = " " + self.text + " "
        else:
            now_image = text_handle.align(self.text, "center", 0, 1, self.width)
        if int(len(self)) < int(self.width):
            now_image += " " * (int(self.width) - text_handle.get_text_index(now_image))
        io_init.era_print(now_image)


class CenterMergeDraw:
    """
    将绘制列表合并在一起并居中绘制
    Keyword arguments:
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大宽度 """
        self.draw_list: List[NormalDraw] = []
        """ 绘制列表 """

    def __len__(self) -> int:
        """获取当前绘制对象宽度"""
        return self.width

    def __gt__(self, other) -> int:
        return int(len(self)) > int(len(other))

    def draw(self):
        """绘制列表"""
        now_width = 0
        for value in self.draw_list:
            now_width += len(value)
        now_text = " " * now_width
        fix_text = text_handle.align(now_text, "center", 1, 1, self.width)
        fix_draw = NormalDraw()
        fix_draw.text = fix_text
        fix_draw.width = len(fix_text)
        fix_draw.draw()
        for value in self.draw_list:
            value.draw()
        now_width = fix_draw.width * 2 + now_width
        if now_width < self.width:
            fix_draw.text += int(self.width - now_width) * " "
        fix_draw.draw()


class LeftMergeDraw:
    """
    将绘制列表合并在一起并左对齐绘制
    Keyword arguments:
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大宽度 """
        self.draw_list: List[NormalDraw] = []
        """ 绘制列表 """
        self.column: int = 0
        """ 每行最大元素数 """

    def __len__(self) -> int:
        """获取当前绘制对象宽度"""
        return self.width

    def __gt__(self, other) -> int:
        return int(len(self)) > int(len(other))

    def draw(self):
        """绘制列表"""
        now_width = 0
        for value in self.draw_list:
            now_width += len(value)
        now_text = " " * now_width
        fix_text = text_handle.align(now_text, "left", 1, 1, self.width)
        fix_draw = NormalDraw()
        fix_draw.text = fix_text
        fix_draw.width = len(fix_text)
        # fix_draw.draw()
        for value in self.draw_list:
            value.draw()
        now_width = fix_draw.width * 2 + now_width
        if now_width < self.width:
            fix_draw.text += int(self.width - now_width) * " "
        fix_draw.draw()


class RightDraw(NormalDraw):
    """右对齐绘制文本"""

    def draw(self):
        """绘制文本"""
        if int(len(self)) > int(self.width):
            now_text = ""
            if self.width:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                    break
                now_text = now_text[:-2] + "~"
        elif int(len(self)) > int(self.width) - 2:
            now_text = " " + self.text
        else:
            now_text = text_handle.align(self.text, "right", 0, 1, self.width)
        io_init.era_print(now_text, self.style)


class LeftDraw(NormalDraw):
    """左对齐绘制文本"""

    def draw(self):
        """绘制文本"""
        if int(len(self)) > int(self.width):
            now_text = ""
            if self.width:
                for i in self.text:
                    if text_handle.get_text_index(now_text) + text_handle.get_text_index(i) < self.width:
                        now_text += i
                    break
                now_text = now_text[:-2] + "~"
        else:
            now_text = text_handle.align(self.text, "left", 0, 1, self.width)
        io_init.era_print(now_text, self.style)


class ExpLevelDraw:
    """
    将经验数字转换为对应评级文本
    Keyword arguments:
    experience -- 经验值
    """

    def __init__(self, experience: int):
        """初始化绘制对象"""
        grade = ""
        if experience <= 0:
            grade = "G"
        elif experience == 1:
            grade = "F"
        elif experience == 2:
            grade = "E"
        elif experience == 3:
            grade = "D"
        elif experience == 4:
            grade = "C"
        elif experience == 5:
            grade = "B"
        elif experience == 6:
            grade = "A"
        elif experience == 7:
            grade = "S"
        elif experience >= 8:
            grade = "EX"
        style = f"level{grade.lower()}"
        now_draw = NormalDraw()
        now_draw.width = len(grade)
        now_draw.style = style
        now_draw.text = grade
        self.grade_draw = now_draw
        """ 生成的等级绘制对象 """

    def __len__(self) -> int:
        """
        获取等级文本长度
        Return arguments:
        int -- 等级文本长度
        """
        return len(self.grade_draw)

    def draw(self):
        """绘制文本"""
        self.grade_draw.draw()
