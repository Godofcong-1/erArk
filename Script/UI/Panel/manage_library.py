from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, attr_calculation, update, attr_text
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
import random

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


class Manage_Library_Panel:
    """
    用于管理图书馆的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("管理图书馆")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""


        title_text = "管理图书馆"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            # line = draw.LineDraw("-", window_width)
            # line.draw()
            cinfo_draw = draw.NormalDraw()
            info_text = f"\n要进行哪方面的管理呢？\n"
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            # 选项面板
            # button_all_draw = panel.LeftDrawTextListPanel()

            button0_text = f"[001]催还书"
            button0_draw = draw.LeftButton(
                _(button0_text),
                _("1"),
                window_width,
                cmd_func=self.urge_return_book_list,
                args=(),
                )
            line_feed.draw()
            button0_draw.draw()
            return_list.append(button0_draw.return_text)

            if 1:
                button1_text = f"[002]图书进货(未实装)"
                button1_draw = draw.LeftButton(
                    _(button1_text),
                    _("2"),
                    window_width,
                    cmd_func=self.get_new_book,
                    args=(),
                    )
                line_feed.draw()
                button1_draw.draw()
                return_list.append(button1_draw.return_text)

            if 1:
                button2_text = f"[003]阅读推荐"
                button2_draw = draw.LeftButton(
                    _(button2_text),
                    _("3"),
                    window_width,
                    cmd_func=self.read_recommend,
                    args=(),
                    )
                line_feed.draw()
                button2_draw.draw()
                return_list.append(button2_draw.return_text)

            if 1:
                button3_text = f"[004]读书会"
                button3_draw = draw.LeftButton(
                    _(button3_text),
                    _("4"),
                    window_width,
                    cmd_func=self.reading_party,
                    args=(),
                    )
                line_feed.draw()
                button3_draw.draw()
                return_list.append(button3_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


    def urge_return_book_list(self):
        """催还书的大列表"""

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()
            book_count = 0

            # 按类型遍历全图书，寻找已经被借出的书籍
            for book_type_cid in game_config.config_book_type:
                book_type_data = game_config.config_book_type[book_type_cid]
                for book_cid in game_config.config_book_type_data[book_type_cid]:
                    book_data = game_config.config_book[book_cid]
                    if cache.base_resouce.book_borrow_dict[book_cid] > 0 :
                        book_count += 1
                        book_text = f"  [{str(book_count).rjust(3,'0')}]({book_type_data.son_type_name}){book_data.name}"
                        borrow_npc_id = cache.base_resouce.book_borrow_dict[book_cid]
                        borrow_npc_name = cache.character_data[borrow_npc_id].name
                        book_text += f"  (被{borrow_npc_name}借走)"

                        button_draw = draw.LeftButton(
                            _(book_text),
                            _(str(book_count)),
                            self.width,
                            cmd_func=self.return_book,
                            args=(borrow_npc_id,),
                            )
                        # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                        line_feed.draw()
                        button_draw.draw()
                        return_list.append(button_draw.return_text)

            # 没有人借书时输出提示信息
            if book_count == 0:
                now_draw = draw.NormalDraw()
                now_draw.width = window_width
                now_draw.text = _(f"\n  目前无人借书，不需要催还\n")
                now_draw.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn == back_draw.return_text:
                break


    def return_book(self,chara_id):
        """角色还书"""

        character_data = cache.character_data[chara_id]
        character_data.entertainment.book_return_possibility += 100
        character_data.entertainment.entertainment_type = [101] * len(character_data.entertainment.entertainment_type)
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n{character_data.name}将在空闲时间前往图书馆还书\n")
        now_draw.draw()


    def get_new_book(self):
        """图书进货"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n暂未实装\n")
        now_draw.draw()


    def read_recommend(self):
        """阅读推荐"""

        self.handle_panel = panel.PageHandlePanel([], SelectRecommendBookButton, 999, 6, self.width, 1, 1, 0)

        while 1:

            # 显示提示信息
            line = draw.LineDraw("-", self.width)
            line.draw()
            info_draw = draw.NormalDraw()
            can_recommend_count = 3 - len(cache.base_resouce.recommend_book_type_set)
            info_draw.text = f"\n 当前剩余可选推荐 {can_recommend_count}\n"
            info_draw.draw()
            line_feed.draw()

            # 按类型遍历全图书，寻找已经被借出的书籍
            book_type_list = [i for i in game_config.config_book_type]
            self.handle_panel.text_list = book_type_list
            self.handle_panel.update()
            self.handle_panel.draw()
            return_list = []
            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


    def reading_party(self):
        """读书会"""

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()

            # 提示信息
            now_draw = draw.NormalDraw()
            now_draw.width = window_width
            now_draw.text = _(f"\n  要把哪一天定为读书会呢？\n")
            now_draw.draw()

            # 遍历一周七天
            for i in range(7):
                week_date_data = game_config.config_week_day[i]
                button_text = f"  [{i}]:{week_date_data.name}"
                party_entertain_id = cache.base_resouce.party_day_of_week[i]
                if party_entertain_id:
                    button_text += f" ({game_config.config_entertainment[party_entertain_id].name})"

                button_draw = draw.LeftButton(
                    _(button_text),
                    _(str(i)),
                    self.width,
                    cmd_func=self.choice_read_party,
                    args=(i,),
                    )
                # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                line_feed.draw()
                button_draw.draw()
                return_list.append(button_draw.return_text)


            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn == back_draw.return_text:
                break

    def choice_read_party(self,week_day):
        """选择读书会之日"""

        party_entertain_id = cache.base_resouce.party_day_of_week[week_day]

        if party_entertain_id == 101:
            cache.base_resouce.party_day_of_week[week_day] = 0
        elif party_entertain_id:
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = _(f"\n这一天已经被选为其他活动了\n")
            now_draw.draw()
        else:
            # 先取消掉其他日子可能有的读书会
            for i in range(7):
                party_entertain_all_id = cache.base_resouce.party_day_of_week[i]
                if party_entertain_all_id == 101:
                    cache.base_resouce.party_day_of_week[i] = 0

            # 再把指定日子变成读书会
            cache.base_resouce.party_day_of_week[week_day] = 101


class SelectRecommendBookButton:
    """
    点击后可选择作为推荐书籍类别的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, book_type_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.book_type_id: int = book_type_id
        """ 书籍类型编号 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        type_data = game_config.config_book_type[self.book_type_id]
        button_text = f"[{str(type_data.cid).rjust(2,'0')}]：{type_data.father_type_name}-{type_data.son_type_name}"
        name_draw = draw.LeftDraw()
        if self.book_type_id in cache.base_resouce.recommend_book_type_set:
            button_text += f" (已推荐)"
            name_draw = draw.LeftButton(button_text, self.button_return, self.width,normal_style = "nowmap", cmd_func=self.button_0)
        else:
            name_draw = draw.LeftButton(button_text, self.button_return, self.width, cmd_func=self.button_0)

        """ 绘制的对象 """
        self.now_draw = name_draw

    def button_0(self):
        """选项1"""
        if self.book_type_id in cache.base_resouce.recommend_book_type_set:
            cache.base_resouce.recommend_book_type_set.remove(self.book_type_id)
        elif 3 - len(cache.base_resouce.recommend_book_type_set):
            cache.base_resouce.recommend_book_type_set.add(self.book_type_id)

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

