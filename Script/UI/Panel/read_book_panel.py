from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import update, instuct_judege
from Script.UI.Panel import borrow_book_panel
import random

panel_info_data = {}

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """

def draw_book_fragment(book_id: int) -> None:
    """
    根据书籍ID绘制书籍片段
    参数:
        book_id (int): 书籍的唯一ID
    返回值:
        None
    功能描述:
        从书籍数据库中选取对应书籍的片段，并将片段内容绘制给玩家
    """
    # 获取书籍数据
    excerpt_list = game_config.config_book_excerpt_list.get(book_id)
    if not excerpt_list:
        return

    # 随机选取一个片段
    fragment = random.choice(excerpt_list)

    # 绘制片段内容
    fragment_draw = draw.NormalDraw()
    fragment_draw.text = f"\n……{fragment}……\n"
    fragment_draw.draw()


class Read_Book_Panel:
    """
    用于读书的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("读书")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = _("读书")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 当前借书数量信息
            book_id_set = character_data.entertainment.borrow_book_id_set

            # 如果未借书的话直接输出提示信息
            if len(book_id_set) == 0:
                info_draw = draw.NormalDraw()
                borrow_limit_text = _("\n当前未持有书籍，请前去图书馆借书\n")
                info_draw.text = borrow_limit_text
                info_draw.width = self.width
                info_draw.draw()
            # 已借书则遍历输出按钮
            else:
                for book_id in book_id_set:
                    book_data = game_config.config_book[book_id]
                    son_type_name = game_config.config_book_type[book_data.type].son_type_name
                    now_progress = character_data.entertainment.read_book_progress.get(book_id, 0)
                    progress_text = _("（阅读进度：{0}%）").format(now_progress)
                    book_text = f"  [{str(book_id).rjust(3,'0')}]({son_type_name}){book_data.name} {progress_text}"

                    button_draw = draw.LeftButton(
                        _(book_text),
                        _(str(book_id)),
                        self.width,
                        cmd_func=self.read,
                        args=(book_id,),
                        )
                    # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def read(self, book_id):
        """读选择的书"""
        instuct_judege.init_character_behavior_start_time(0, cache.game_time)
        character_data: game_type.Character = cache.character_data[0]
        book_data = game_config.config_book[book_id]
        character_data.behavior.behavior_id = constant.Behavior.READ_BOOK
        character_data.state = constant.CharacterStatus.STATUS_READ_BOOK
        character_data.behavior.book_id = book_id
        character_data.behavior.book_name = book_data.name
        character_data.behavior.duration = 30
        # 更新历史记录中的阅读次数
        borrow_book_panel.update_read_count_in_history(0, book_id)
        update.game_update_flow(30)
