from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle,attr_text,attr_calculation
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

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

class Borrow_Book_Panel:
    """
    用于显示借书界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("技能类书籍")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "借阅书籍"
        book_father_type_list = [_("技能类书籍"), _("娱乐类书籍"), _("色情类书籍")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for book_fater_type in book_father_type_list:
                if book_fater_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{book_fater_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(book_father_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{book_fater_type}]",
                        f"\n{book_fater_type}",
                        self.width / len(book_father_type_list),
                        cmd_func=self.change_panel,
                        args=(book_fater_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 当前借书数量限制信息
            borrow_count = 0
            for book_id in cache.base_resouce.book_borrow_dict:
                if cache.base_resouce.book_borrow_dict[book_id] == 0:
                    borrow_count += 1
            borrow_limit_draw = draw.NormalDraw()
            borrow_limit_text = f"\n已借书量/最大借书量：{borrow_count}/3\n"
            borrow_limit_draw.text = borrow_limit_text
            borrow_limit_draw.width = self.width
            borrow_limit_draw.draw()

            # 书籍总览信息
            now_draw = panel.LeftDrawTextListPanel()

            now_draw.draw_list.append(line_feed)
            now_draw.width += 1

            # 初始化变量
            book_count = 0
            book_can_borrow_count = 0

            # 遍历书籍类型列表，寻找符合当前书籍父类别的书籍类型cid
            for book_type_cid in game_config.config_book_type:
                book_type_data = game_config.config_book_type[book_type_cid]
                if book_type_data.father_type_name in self.now_panel:
                    # 遍历该cid下的书籍
                    for book_cid in game_config.config_book_type_data[book_type_cid]:
                        book_data = game_config.config_book[book_cid]
                        book_count += 1
                        book_text = f"  [{str(book_count).rjust(3,'0')}]({book_type_data.son_type_name}){book_data.name}"
                        if cache.base_resouce.book_borrow_dict[book_cid] == -1:
                            book_text += "  (可借阅)"
                            book_style = "standard"
                            book_can_borrow_count += 1
                        elif cache.base_resouce.book_borrow_dict[book_cid] == 0:
                            book_text += f"  (已被博士借走)"
                            book_style = "nowmap"
                        else:
                            borrow_npc_id = cache.base_resouce.book_borrow_dict[book_cid]
                            borrow_npc_name = cache.character_data[borrow_npc_id].name
                            book_text += f"  (已被{borrow_npc_name}借走)"
                            book_style = "nullcmd"

                        button_draw = draw.LeftButton(
                            _(book_text),
                            _(str(book_count)),
                            self.width,
                            normal_style = book_style,
                            cmd_func=self.borrow,
                            args=(book_cid,),
                            )
                        # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                        return_list.append(button_draw.return_text)
                        now_draw.draw_list.append(button_draw)
                        now_draw.width += len(button_draw.text)
                        now_draw.draw_list.append(line_feed)
                        now_draw.width += 1

            resouce_draw = draw.NormalDraw()
            resouce_text = "\n当前藏书情况："
            resouce_text += f"\n  {self.now_panel}在馆量/总藏书量：{book_can_borrow_count}/{book_count}\n"
            resouce_draw.text = resouce_text
            resouce_draw.width = self.width
            resouce_draw.draw()

            self.draw_list: List[draw.NormalDraw] = []
            """ 绘制的文本列表 """
            self.draw_list.extend(now_draw.draw_list)

            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, building_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        building_type -- 要切换的面板类型
        """

        self.now_panel = building_type

    def borrow(self, book_cid: int):
        """
        借阅书籍
        Keyword arguments:
        facility_cid -- 建筑效果编号
        """

        # 当前借书数量限制信息
        borrow_count = 0
        for book_id in cache.base_resouce.book_borrow_dict:
            if cache.base_resouce.book_borrow_dict[book_id] == 0:
                borrow_count += 1

        if cache.base_resouce.book_borrow_dict[book_cid] == 0:
            cache.base_resouce.book_borrow_dict[book_cid] = -1
        elif borrow_count < 3:
            cache.base_resouce.book_borrow_dict[book_cid] = 0
        else:
            borrow_limit_draw = draw.WaitDraw()
            borrow_limit_text = f"\n已达到最大借书上限，无法继续借阅\n"
            borrow_limit_draw.text = borrow_limit_text
            borrow_limit_draw.width = self.width
            borrow_limit_draw.draw()

