"""学生页签栏（Plan 22 一期 §9.8.1）

个人课表与养成总览顶部那排「按人切换」的页签，两个面板共用这一个组件。

⚠️ 原来两处各自把全部学生铺成一排、按人数均分整行宽度——女儿一多每个页签只剩几列，
   名字被截得认不出来。现在每页固定列 STUDENT_TAB_PER_PAGE 个人，超出翻页。

⚠️ 页码必须是组件的属性而不是局部变量：容器 Education_Manage_Panel 每轮 while 都会重画子页，
   局部变量会被冲掉，玩家点一次「下一页」马上又跳回第一页（与成绩单翻页同一教训）。
"""
from types import FunctionType
from typing import List

from Script.Core import cache_control, game_type, get_text
from Script.System.Education_System import education_constant
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1


class Student_Tab_Bar:
    """
    学生页签栏：每页最多 STUDENT_TAB_PER_PAGE 个人名页签，多页时带翻页行
    输入类型: width(int) 整行宽度, return_prefix(str) 人名页签返回值的前缀，如 "\nSTU_"
    输出类型: 无
    功能: 只画不取输入，askfor_all 由容器统一调用；翻页哨兵与人名页签都往容器的 return_list 里加
    """

    def __init__(self, width: int, return_prefix: str):
        """初始化绘制对象"""
        self.width: int = width
        self.return_prefix: str = return_prefix
        """ 人名页签返回值的前缀。⚠️ 两个面板各用一个前缀（STU_ / GSTU_），同一个容器里不会撞名 """
        self.page: int = 0
        """ 当前页（0起）。越界时由 draw 夹回最后一页 """

    def get_total_page(self, student_list: List[int]) -> int:
        """
        取总页数
        输入类型: student_list(List[int])
        输出类型: int，至少为1
        功能: 向上取整；空列表也算一页，免得除零与负页码
        """
        return max(1, (len(student_list) + education_constant.STUDENT_TAB_PER_PAGE - 1) // education_constant.STUDENT_TAB_PER_PAGE)

    def jump_to(self, student_list: List[int], student_id: int):
        """
        把页码跳到某人所在的那一页
        输入类型: student_list(List[int]), student_id(int)
        输出类型: 无
        功能: 面板做「选中态失效、回落到第一个」时调用，让回落后的选中者可见。
              ⚠️ draw 里**不**自动跟随选中者跳页：玩家翻到第 2 页找人时会被拉回第 1 页
        """
        if student_id in student_list:
            self.page = student_list.index(student_id) // education_constant.STUDENT_TAB_PER_PAGE

    def draw(self, student_list: List[int], now_student: int, return_list: List[str]):
        """
        绘制本页的人名页签与翻页行
        输入类型: student_list(List[int]) 全部学生, now_student(int) 当前选中者, return_list(List[str]) 容器的共享返回值列表
        输出类型: 无
        功能: 页签固定宽度（整行 / 每页人数），不按本页人数均分——翻页时名字的位置不跳。
              只有多页时才画翻页行：两个点不动的箭头比没有箭头更让人困惑。
              末尾补一个换行与一条分割线，与原两个面板的画法一致
        """
        total_page = self.get_total_page(student_list)
        # 人数减少（孩子长大、成年学生换岗）后页码可能越界，夹回最后一页
        if not 0 <= self.page < total_page:
            self.page = total_page - 1
        start = self.page * education_constant.STUDENT_TAB_PER_PAGE
        page_list = student_list[start:start + education_constant.STUDENT_TAB_PER_PAGE]

        tab_width = max(1, int(self.width / education_constant.STUDENT_TAB_PER_PAGE))
        for student_id in page_list:
            name = cache.character_data[student_id].name
            if student_id == now_student:
                now_draw = draw.CenterDraw()
                now_draw.text = f"[{name}]"
                now_draw.style = "onbutton"
                now_draw.width = tab_width
                now_draw.draw()
            else:
                now_draw = draw.CenterButton(f"[{name}]", f"{self.return_prefix}{student_id}", tab_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
        line_feed.draw()

        if total_page > 1:
            button_width = int(self.width / 3)
            if self.page > 0:
                prev_draw = draw.CenterButton(_("[← 上一页]"), education_constant.STUDENT_PAGE_PREV, button_width)
                prev_draw.draw()
                return_list.append(prev_draw.return_text)
            else:
                # 到头了也要占住格位，否则中间那行「第N/M页」会整体左移
                blank_draw = draw.CenterDraw()
                blank_draw.width = button_width
                blank_draw.style = "deep_gray"
                blank_draw.text = _("　← 上一页")
                blank_draw.draw()
            index_draw = draw.CenterDraw()
            index_draw.width = button_width
            index_draw.text = _("第 {0} / {1} 页（共 {2} 人）").format(self.page + 1, total_page, len(student_list))
            index_draw.draw()
            if self.page < total_page - 1:
                next_draw = draw.CenterButton(_("[下一页 →]"), education_constant.STUDENT_PAGE_NEXT, button_width)
                next_draw.draw()
                return_list.append(next_draw.return_text)
            else:
                blank_draw = draw.CenterDraw()
                blank_draw.width = button_width
                blank_draw.style = "deep_gray"
                blank_draw.text = _("　下一页 →")
                blank_draw.draw()
            line_feed.draw()
        draw.LineDraw("-", self.width).draw()

    def handle_page_yrn(self, yrn: str) -> bool:
        """
        处理翻页哨兵
        输入类型: yrn(str)，容器 askfor_all 的返回值
        输出类型: bool，是否是翻页操作（已处理）
        功能: 只改页码，越界交给下一轮 draw 夹回
        """
        if yrn == education_constant.STUDENT_PAGE_PREV:
            self.page -= 1
            return True
        if yrn == education_constant.STUDENT_PAGE_NEXT:
            self.page += 1
            return True
        return False

    def get_student_by_yrn(self, yrn: str, student_list: List[int]) -> int:
        """
        判断点的是哪个人的页签
        输入类型: yrn(str), student_list(List[int])
        输出类型: int，角色id；不是人名页签则为 -1
        功能: 只认本组件前缀的返回值，别的面板的 STU_ 与本面板的 GSTU_ 不会互相吃掉
        """
        for student_id in student_list:
            if yrn == f"{self.return_prefix}{student_id}":
                return student_id
        return -1
