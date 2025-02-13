import itertools
import math
import time
from typing import List, Dict, Tuple
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import io_init, flow_handle, text_handle, get_text, value_handle, game_type, cache_control
from Script.Config import normal_config


_: FunctionType = get_text._
""" 翻译api """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


class SingleColumnButton:
    """标准单列按钮监听响应"""

    def __init__(self):
        """初始化绘制对象"""
        self.button_list: List[draw.Button] = []
        """ 绘制的按钮列表 """
        self.return_list: Dict[str, str] = {}
        """
        按钮返回的响应列表
        按钮返回值:按钮文本
        """
        self.width = 0
        """ 绘制的最大宽度 """
        self.max_height = 0
        """ 绘制的最大高度 """

    def set(
        self,
        button_list: List[str],
        return_list: List[str],
        normal_style="standard",
        onbutton_style="onbutton",
    ):
        """
        设置按钮和返回列表
        Keyword arguments:
        button_list -- 按钮列表
        return_list -- 返回列表
        normal_style -- 按钮通常样式
        onbutton_style -- 鼠标悬停时样式
        """
        for i in range(len(button_list)):
            if i <= self.max_height:
                draw_button = draw.Button(button_list[i], return_list[i], normal_style, onbutton_style)
                draw_button.width = self.width
                self.button_list.append(draw_button)
            self.return_list[return_list[i]] = button_list[i]

    def get_width(self) -> int:
        """
        获取按钮列表的最大宽度
        Return arguments:
        int -- 最大宽度
        """
        return max(self.button_list)

    def get_height(self) -> int:
        """
        获取按钮列表的长度:
        Return arguments:
        int -- 长度
        """
        return len(self.button_list)

    def draw(self):
        """绘制按钮列表"""
        for button in self.button_list:
            button.draw()
            io_init.era_print("\n")


class OneMessageAndSingleColumnButton:
    """标准单条消息+单列数字id响应按钮监听面板"""

    def __init__(self):
        """初始化绘制对象"""
        self.message: draw.RichTextDraw = None
        """ 消息 """
        self.button_panel: SingleColumnButton = None
        """ 按钮监听列表 """

    def set(self, button_list: List[str], message: str, start_id=0):
        """
        设置要绘制的信息
        Keyword arguments:
        button_list -- 监听的按钮列表
        message -- 绘制的消息
        start_id -- id的起始位置
        """
        new_button_list = []
        return_list = []
        for i in range(len(button_list)):
            now_id = text_handle.id_index(i + start_id)
            now_id_text = now_id + button_list[i]
            new_button_list.append(now_id_text)
            now_i_str = str(start_id + i)
            return_list.append(now_i_str)
        width = normal_config.config_normal.text_width
        self.message = draw.NormalDraw()
        self.message.text = message
        self.message.width = width
        self.button_panel = SingleColumnButton()
        self.button_panel.width = width
        self.button_panel.max_height = len(return_list)
        self.button_panel.set(new_button_list, return_list)
        self.button_panel.return_list = dict(zip(return_list, button_list))

    def get_return_list(self) -> Dict[str, str]:
        """
        获取按钮响应的id集合
        Return arguments:
        Dict[str,str] -- 按钮响应的id集合 按钮id:按钮文本
        """
        return self.button_panel.return_list

    def draw(self):
        """绘制面板"""
        self.message.draw()
        io_init.era_print("\n")
        self.button_panel.draw()


class AskForOneMessage:
    """标准单条消息+等待玩家输入任意字符面板"""

    def __init__(self):
        """初始化绘制对象"""
        self.message: draw.RichTextDraw = None
        """ 消息 """
        self.input_max: int = 0
        """ 玩家输入文本的最大长度 """

    def set(self, message: str, input_max: int):
        """
        设置要绘制的消息和允许玩家输入的长度
        Keyword arguments:
        message -- 绘制的消息
        input_max -- 允许玩家输入的最大长度
        """
        self.message = draw.NormalDraw()
        self.message.text = message
        self.message.width = normal_config.config_normal.text_width
        self.input_max = input_max

    def draw(self) -> str:
        """
        绘制面板
        Return arguments:
        str -- 玩家输入的字符
        """
        return_text = ""
        while 1:
            self.message.draw()
            return_text = flow_handle.askfor_str(1, 1)
            text_index = text_handle.get_text_index(return_text)
            if text_index <= self.input_max:
                break
            io_init.era_print(_("输入的字符超长，最大{input_max}个英文字符，请重试。").format(input_max=self.input_max))
            io_init.era_print("\n")
        return return_text


class TitleAndRightInfoListPanel:
    """绘制一个标题和一串靠右对齐的列表组合的面板"""

    def __init__(self):
        """初始化绘制对象"""
        self.title = ""
        """ 文本标题 """
        self.width = 0
        """ 面板宽度 """
        self.info_list: List[str] = []
        """ 信息列表 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制列表 """

    def set(self, title_text: str, info_list: List[str], width: int):
        """
        设置绘制信息
        Keyword arguments:
        title_text -- 标题
        info_list -- 信息列表
        width -- 标题宽度
        """
        self.width = width
        line = draw.LineDraw("=", width)
        self.draw_list.append(line)
        title = draw.CenterDraw()
        title.width = self.width
        title.text = title_text
        self.draw_list.append(title)
        for info_text in info_list:
            info = draw.RightDraw()
            info.width = width
            info.text = info_text
            self.draw_list.append(info)
        self.draw_list.append(line)

    def draw(self):
        """绘制面板"""
        for value in self.draw_list:
            value.draw()
            io_init.era_print("\n")


class CenterDrawTextListPanel:
    """绘制一个列表并居中每个元素"""

    def __init__(self):
        """初始化绘制对象"""
        self.width: int = 0
        """ 面板宽度 """
        self.column: int = 0
        """ 每行最大元素数 """
        self.draw_list: List[List[draw.CenterDraw]] = []
        """ 绘制列表 """

    def set(self, info_list: List[str], width: int, column: int):
        """
        设置绘制信息
        Keyword arguments:
        info_list -- 信息列表
        width -- 绘制宽度
        column -- 每行最大元素数
        """
        self.width = width
        self.column = column
        new_info_list = value_handle.list_of_groups(info_list, column)
        for now_info_list in new_info_list:
            now_width = int(width / column)
            now_list = []
            for now_info in now_info_list:
                now_info_draw = draw.CenterDraw()
                now_info_draw.width = now_width
                now_info_draw.text = now_info
                now_list.append(now_info_draw)
            self.draw_list.append(now_list)

    def draw(self):
        """绘制面板"""
        for now_list in self.draw_list:
            for value in now_list:
                value.draw()
            io_init.era_print("\n")


class LeftDrawTextListPanel:
    """绘制一个列表并左对齐每个元素"""

    def __init__(self):
        """初始化绘制对象"""
        self.width: int = 0
        """ 面板宽度 """
        self.column: int = 0
        """ 每行最大元素数 """
        self.draw_list: List[List[draw.LeftDraw]] = []
        """ 绘制列表 """

    def set(self, info_list: List[str], width: int, column: int):
        """
        设置绘制信息
        Keyword arguments:
        info_list -- 信息列表
        width -- 绘制宽度
        column -- 每行最大元素数
        """
        self.width = width
        self.column = column
        new_info_list = value_handle.list_of_groups(info_list, column)
        for now_info_list in new_info_list:
            now_width = int(width / column)
            now_list = []
            index = 0
            now_sub_width = 0
            for now_info in now_info_list:
                if index == len(now_info_list) - 1:
                    now_width = self.width - now_sub_width
                else:
                    index += 1
                    now_sub_width += now_width
                now_info_draw = draw.LeftDraw()
                now_info_draw.width = now_width
                now_info_draw.text = now_info
                now_list.append(now_info_draw)
            self.draw_list.append(now_list)

    def draw(self):
        """绘制面板"""
        for now_list in self.draw_list:
            for value in now_list:
                value.draw()
            io_init.era_print("\n")


class LeftDrawTextListWaitPanel(LeftDrawTextListPanel):
    """绘制一个左对齐列表并等待玩家任意键"""

    def draw(self):
        """绘制面板"""
        for now_list in self.draw_list:
            for value in now_list:
                value.draw()
            io_init.era_print("\n")
        if not cache.wframe_mouse.w_frame_skip_wait_mouse:
            flow_handle.askfor_wait()
        else:
            time.sleep(0.001)

    def __len__(self):
        """获取面板的内容宽度"""
        index = 0
        for now_list in self.draw_list:
            for value in now_list:
                index += len(value)
        return index


class DrawTextListPanel:
    """绘制一个对象列表"""

    def __init__(self):
        """初始化绘制对象"""
        self.width: int = 0
        """ 面板宽度 """
        self.column: int = 0
        """ 每行最大元素数 """
        self.draw_list: List[List[draw.NormalDraw]] = []
        """ 绘制列表 """

    def set(self, info_list: List[draw.NormalDraw], width: int, column: int):
        """
        设置绘制信息
        Keyword arguments:
        info_list -- 绘制对象列表
        width -- 绘制宽度
        column -- 每行最大元素数
        """
        self.width = width
        self.column = column
        self.draw_list = value_handle.list_of_groups(info_list, column)

    def draw(self):
        """绘制面板"""
        for now_list in self.draw_list:
            for value in now_list:
                value.draw()
            io_init.era_print("\n")


class VerticalDrawTextListGroup:
    """
    竖列并排绘制多个文本对象列表
    Keyword arguments:
    width -- 最大绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大绘制宽度 """
        self.draw_list: List[List[draw.NormalDraw]] = []
        """ 绘制的对象列表 """

    def draw(self):
        """绘制对象"""
        new_group = itertools.zip_longest(*self.draw_list)
        for draw_list in new_group:
            now_width = int(self.width / len(draw_list))
            for value in draw_list:
                if value is not None:
                    value.draw()
                else:
                    now_draw = draw.NormalDraw()
                    now_draw.text = " " * now_width
                    now_draw.draw()
            io_init.era_print("\n")


class CenterDrawButtonListPanel:
    """绘制一个按钮列表并居中每个元素"""

    def __init__(self):
        """初始化绘制对象"""
        self.width = 0
        """ 面板宽度 """
        self.column = 0
        """ 每行最大元素数 """
        self.draw_list: List[List[draw.Button]] = []
        """ 绘制按钮列表 """
        self.return_list: List[str] = []
        """
        按钮返回的响应列表
        按钮返回值:响应文本
        """

    def set(
        self,
        text_list: List[str],
        return_list: List[str],
        width: int,
        column: int,
        null_text: str = "",
        cmd_func: FunctionType = None,
        func_args: List[Tuple] = [],
    ):
        """
        设置绘制信息
        Keyword arguments:
        text_list -- 按钮文本列表
        return_list -- 按钮返回列表
        width -- 绘制宽度
        column -- 每行最大元素数
        null_text -- 不作为按钮绘制的文本
        cmd_func -- 列表元素按钮绑定函数
        """
        self.width = width
        self.column = column
        new_text_list = value_handle.list_of_groups(text_list, column)
        index = 0
        self.return_list = return_list
        self.draw_list: List[List[draw.Button]] = []
        for now_text_list in new_text_list:
            now_width = int(width / len(now_text_list))
            now_list = []
            for now_text in now_text_list:
                if now_text != null_text:
                    now_button = draw.CenterButton(
                        now_text,
                        return_list[index],
                        now_width,
                        cmd_func=cmd_func,
                        args=(return_list[index]),
                    )
                    now_list.append(now_button)
                else:
                    now_info_draw = draw.CenterDraw()
                    now_info_draw.width = now_width
                    now_info_draw.text = now_text
                    now_info_draw.style = "onbutton"
                    now_list.append(now_info_draw)
                index += 1
            self.draw_list.append(now_list)

    def draw(self):
        """绘制面板"""
        for now_list in self.draw_list:
            for value in now_list:
                value.draw()
            io_init.era_print("\n")


class LeftDrawIDButtonListPanel:
    """绘制一个被编号的按钮列表并左对齐每个元素"""

    def __init__(self):
        """初始化绘制对象"""
        self.width = 0
        """ 面板宽度 """
        self.column = 0
        """ 每行最大元素数 """
        self.start_id = 0
        """ 编号的启始id """
        self.draw_list: List[List[draw.Button]] = []
        """ 绘制按钮列表 """
        self.return_list: List[str] = []
        """
        按钮返回的响应列表
        按钮返回值:响应文本
        """

    def set(
        self,
        text_list: List[str],
        start_id: int,
        width: int,
        column: int,
        null_text: str = "",
        cmd_func: FunctionType = None,
        func_args: List[Tuple] = [],
    ):
        """
        设置绘制信息
        Keyword arguments:
        text_list -- 按钮文本列表
        start_id -- 编号的启始id
        width -- 绘制宽度
        column -- 每行最大元素数
        null_text -- 不作为按钮绘制的文本
        cmd_func -- 列表元素按钮绑定函数
        """
        self.width = width
        self.column = column
        new_text_list = value_handle.list_of_groups(text_list, column)
        index = start_id
        now_index = 0
        self.draw_list: List[List[draw.Button]] = []
        for now_text_list in new_text_list:
            now_width = int(width / len(now_text_list))
            now_list = []
            for now_text in now_text_list:
                if now_text != null_text:
                    now_text = text_handle.id_index(index) + now_text
                    now_button = draw.LeftButton(
                        now_text,
                        str(index),
                        now_width,
                        cmd_func=cmd_func,
                        args=(func_args[now_index]),
                    )
                    now_list.append(now_button)
                    self.return_list.append(str(index))
                else:
                    now_text = text_handle.id_index(index) + now_text
                    now_info_draw = draw.LeftDraw()
                    now_info_draw.width = now_width
                    now_info_draw.text = now_text
                    now_info_draw.style = "onbutton"
                    now_list.append(now_info_draw)
                index += 1
                now_index += 1
            self.draw_list.append(now_list)

    def draw(self):
        """绘制面板"""
        for now_list in self.draw_list:
            for value in now_list:
                value.draw()
            io_init.era_print("\n")


class ClearScreenPanel:
    """绘制一屏长度的空行"""

    def draw(self):
        """绘制面板"""
        panel = "\n" * 50
        io_init.era_print(panel)


class PageHandleDrawType:
    """
    鸭子类型,用于定义分页绘制对象面板所需接口,text中传入文本或数据,并将最终要显示的文本传入draw_text中,供面板处理
    Keyword arguments:
    text -- 绘制的文本id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    butoon_id -- 数字按钮的id
    """

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text: str = text
        """ 未处理的绘制的文本id """
        self.draw_text: str = ""
        """ 最终绘制的文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: bool = button_id
        """ 数字按钮的id """
        self.button_return: str = ""
        """ 按钮返回值 """

    def draw(self):
        """绘制对象"""


class PageHandlePanel:
    """
    标准分页绘制对象面板
    Keyword arguments:
    text_list -- 绘制的文本列表
    draw_type -- 文本的绘制类型
    limit -- 每页长度
    column -- 每行个数
    width -- 每行最大宽度
    is_button -- 将列表元素绘制成按钮
    num_button -- 将列表元素绘制成数字按钮
    button_start_id -- 数字按钮的开始id
    row_septal_lines -- 每行之间的间隔线,为空则不绘制
    col_septal_lines -- 每列之间的间隔线,为空则不绘制
    null_button_text -- 不作为按钮绘制的文本
    """

    def __init__(
        self,
        text_list: List[str],
        draw_type: type,
        limit: int,
        column: int,
        width: int,
        is_button: bool = False,
        num_button: bool = False,
        button_start_id: int = 0,
        row_septal_lines: str = "",
        col_septal_lines: str = "",
        null_button_text: str = "",
    ):
        """初始化绘制对象"""
        self.text_list: List[str] = text_list
        """ 绘制的文本列表 """
        self.draw_type: type = PageHandleDrawType
        """ 文本对象的绘制类型 """
        self.now_page: int = 0
        """ 当前页数 """
        self.limit: int = limit
        """ 每页长度 """
        self.column: int = column
        """ 每行个数 """
        self.width: int = width
        """ 每行最大宽度 """
        self.row_septal_lines: str = row_septal_lines
        """ 每行之间的间隔线,为空则不绘制 """
        self.col_septal_lines: str = col_septal_lines
        """ 每列之间的间隔线,为空则不绘制 """
        self.return_list: List[str] = []
        """ 按钮返回的id列表 """
        self.next_page_return: str = ""
        """ 切换下一页的按钮返回 """
        self.old_page_return: str = ""
        """ 切换上一页的按钮返回 """
        self.is_button: bool = is_button
        """ 将列表元素绘制成按钮 """
        self.num_button: bool = num_button
        """ 将列表元素绘制成数字按钮 """
        self.button_start_id: int = button_start_id
        """ 数字按钮的开始id """
        self.draw_type = draw_type
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的对象列表 """
        self.null_button_text: str = null_button_text
        """ 不作为按钮绘制的文本 """
        self.end_index: int = 0
        """ 结束时按钮id """

    def update(self):
        """更新绘制对象"""
        self.return_list = []
        start_id = self.now_page * self.limit
        total_page = int((len(self.text_list) - 1) / self.limit)
        if start_id >= len(self.text_list):
            self.now_page = total_page
            start_id = self.now_page * self.limit
        now_page_list = []
        for i in range(start_id, len(self.text_list)):
            if len(now_page_list) >= self.limit:
                break
            now_page_list.append(self.text_list[i])
        draw_text_group = value_handle.list_of_groups(now_page_list, self.column)
        draw_list: List[draw.NormalDraw] = []
        self.end_index = self.button_start_id
        index = self.button_start_id
        line_feed = draw.NormalDraw()
        line_feed.text = "\n"
        line_feed.width = 1
        for draw_text_list in draw_text_group:
            if self.row_septal_lines != "" and index:
                line_draw = draw.LineDraw(self.row_septal_lines, self.width)
                draw_list.append(line_draw)
            now_width = self.width
            if self.col_septal_lines != "":
                col_index = len(draw_text_list) + 1
                col_width = text_handle.get_text_index(self.col_septal_lines)
                now_width -= col_width * col_index
            value_width = int(now_width / self.column)
            col_fix_draw = draw.NormalDraw()
            col_fix_draw.text = self.col_septal_lines
            col_fix_draw.width = 1
            draw_list.append(col_fix_draw)
            for value in draw_text_list:
                is_button = 1
                if value == self.null_button_text:
                    is_button = 0
                value_draw = self.draw_type(value, value_width, is_button, self.num_button, index)
                value_draw.draw_text = text_handle.align(value_draw.draw_text, "center", 0, 1, value_width)
                if self.num_button:
                    self.return_list.append(str(index))
                else:
                    self.return_list.append(value_draw.button_return)
                index += 1
                draw_list.append(value_draw)
                draw_list.append(col_fix_draw)
            draw_list.append(line_feed)
        if self.num_button:
            self.end_index = index
        if total_page:
            now_line = draw.LineDraw("-", self.width)
            draw_list.append(now_line)
            page_change_start_id = self.button_start_id
            if self.num_button:
                page_change_start_id = index
            old_page_index_text = text_handle.id_index(page_change_start_id)
            old_page_button = draw.CenterButton(
                _("{old_page_index_text} 上一页").format(old_page_index_text=old_page_index_text),
                str(page_change_start_id),
                int(self.width / 3),
                cmd_func=self.old_page,
            )
            self.return_list.append(str(page_change_start_id))
            self.old_page_return = old_page_button.return_text
            draw_list.append(old_page_button)
            page_text = f"({self.now_page}/{total_page})"
            page_draw = draw.CenterDraw()
            page_draw.width = int(self.width / 3)
            page_draw.text = page_text
            draw_list.append(page_draw)
            next_page_index_text = text_handle.id_index(page_change_start_id + 1)
            next_page_button = draw.CenterButton(
                _("{next_page_index_text} 下一页").format(next_page_index_text=next_page_index_text),
                str(page_change_start_id + 1),
                int(self.width / 3),
                cmd_func=self.next_page,
            )
            self.end_index = page_change_start_id + 1
            self.return_list.append(str(page_change_start_id + 1))
            self.next_page_return = next_page_button.return_text
            draw_list.append(next_page_button)
            draw_list.append(line_feed)
        self.draw_list = draw_list

    def draw(self):
        """绘制面板"""
        for value in self.draw_list:
            value.draw()

    def next_page(self):
        """将面板切换至下一页"""
        total_page = math.ceil(len(self.text_list) / self.limit)
        if self.now_page >= total_page - 1:
            self.now_page = 0
        else:
            self.now_page += 1

    def old_page(self):
        """将面板切换至上一页"""
        total_page = math.ceil(len(self.text_list) / self.limit)
        if self.now_page <= 0:
            self.now_page = total_page
        else:
            self.now_page -= 1


class ClothingPageHandlePanel(PageHandlePanel):
    """服装缩略信息分页绘制对象面板"""

    def update_button(self):
        """更新绘制宽度"""
        id_width = 0
        for value in self.draw_list:
            if "id_width" in value.__dict__:
                if value.id_width > id_width:
                    id_width = value.id_width
        for value in self.draw_list:
            if "id_width" in value.__dict__:
                value.id_width = id_width
