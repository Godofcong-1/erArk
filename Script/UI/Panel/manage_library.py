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
                button1_text = f"[002]图书进货"
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


            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn == back_draw.return_text:
                break


    def return_book(self,chara_id):
        """角色还书"""

        cache.character_data[chara_id].entertainment.book_return_possibility = 100


    def get_new_book(self):
        """图书进货"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n暂未实装\n")
        now_draw.draw()

    def read_recommend(self):
        """阅读推荐"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n暂未实装\n")
        now_draw.draw()

    def reading_party(self):
        """读书会"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n暂未实装\n")
        now_draw.draw()
