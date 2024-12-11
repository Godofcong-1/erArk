from typing import Tuple, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
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


def settle_library_book():
    """
    刷新图书馆的可借阅书籍
    """

    for book_type_cid in game_config.config_book_type:
        game_config.config_book_type_data.setdefault(book_type_cid, [])
        # 如果该类型的书籍超过3本，则随机选择其中的三本
        if len(game_config.config_book_type_data[book_type_cid]) > 3:
            now_choose_list = random.sample(game_config.config_book_type_data[book_type_cid], 3)
        else:
            now_choose_list = game_config.config_book_type_data[book_type_cid]
        cache.rhodes_island.now_show_book_cid_of_type[book_type_cid] = now_choose_list

    # 获取玩家的借书情况
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_borrow = pl_character_data.entertainment.borrow_book_id_set
    # 遍历借的书籍，也加入到展示列表里
    for book_id in pl_borrow:
        book_type = game_config.config_book[book_id].type
        if book_id not in cache.rhodes_island.now_show_book_cid_of_type[book_type]:
            cache.rhodes_island.now_show_book_cid_of_type[book_type].append(book_id)


def check_return_book(character_id):
    """
    检查并决定是否归还当前书籍
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 未借书则跳过
    if len(character_data.entertainment.borrow_book_id_set) == 0:
        return 0
    # 已借书则d100和还书概率比大小
    else:
        return_d100 = random.randint(1,100)
        # 小于还书概率则还书
        # print(f"debug return_d100 = {return_d100},book_return_possibility = {character_data.entertainment.book_return_possibility}")
        if return_d100 < character_data.entertainment.book_return_possibility:
            for book_id in character_data.entertainment.borrow_book_id_set:
                cache.rhodes_island.book_borrow_dict[book_id] = -1
                character_data.entertainment.borrow_book_id_set.discard(book_id)
                # print(f"debug {character_data.name}还了书{book_id}")
                return 1
        return 0


def check_random_borrow_book(character_id):
    """
    检查角色是否有借书，有的话跳过，没有的话随机借一本书
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 已借书则跳过
    if len(character_data.entertainment.borrow_book_id_set):
        return 1
    # 未借书则随机借书
    else:
        # 遍历获得所有没借的书id
        recommend_book_id_set,book_id_set = [],[]
        for book_id in cache.rhodes_island.book_borrow_dict:
            # 未被借出则加入book_id_set
            if cache.rhodes_island.book_borrow_dict[book_id] == -1:
                book_id_set.append(book_id)
                # 如果类型在推荐列表里，则加入recommend_book_id_set
                if game_config.config_book[book_id].type in cache.rhodes_island.recommend_book_type_set:
                    recommend_book_id_set.append(book_id)
        # 如果推荐列表有书，则有一半的概率在推荐列表里借书，否则在全列表里借书
        if len(recommend_book_id_set) and random.randint(0,1) == 1:
            borrow_book_id = random.choice(recommend_book_id_set)
        else:
            borrow_book_id = random.choice(book_id_set)
        cache.rhodes_island.book_borrow_dict[borrow_book_id] = character_id
        character_data.entertainment.borrow_book_id_set.add(borrow_book_id)
        # print(f"debug {character_data.name}借了书{borrow_book_id}")
        return 0


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

        title_text = _("借阅书籍")
        book_father_type_list = [_("技能类书籍"), _("娱乐类书籍"), _("色情类书籍")]

        # 每次初始化可借阅字典
        settle_library_book()

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
            for book_id in cache.rhodes_island.book_borrow_dict:
                if cache.rhodes_island.book_borrow_dict[book_id] == 0:
                    borrow_count += 1
            borrow_limit_draw = draw.NormalDraw()
            borrow_limit_text = _("\n已借书量/最大借书量：{0}/3\n").format(borrow_count)
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
                    now_choose_list = cache.rhodes_island.now_show_book_cid_of_type[book_type_cid]
                    # 遍历该类型下的书籍
                    for book_cid in now_choose_list:
                        book_data = game_config.config_book[book_cid]
                        book_count += 1
                        book_text = f"  [{str(book_count).rjust(3,'0')}]({book_type_data.son_type_name}){book_data.name}"
                        button_flag = True
                        if cache.rhodes_island.book_borrow_dict[book_cid] == -1:
                            book_text += _("  (可借阅)")
                            book_style = "standard"
                            book_can_borrow_count += 1
                        elif cache.rhodes_island.book_borrow_dict[book_cid] == 0:
                            book_text += _("  (已被博士借走)")
                            book_style = "gold_enrod"
                        else:
                            borrow_npc_id = cache.rhodes_island.book_borrow_dict[book_cid]
                            borrow_npc_name = cache.character_data[borrow_npc_id].name
                            book_text += _("  (已被{0}借走)").format(borrow_npc_name)
                            book_style = "nullcmd"
                            button_flag = False

                        if button_flag:
                            button_draw = draw.LeftButton(
                                _(book_text),
                                _(str(book_count)),
                                self.width,
                                normal_style = book_style,
                                cmd_func=self.show_book,
                                args=(book_cid,),
                                )
                            return_list.append(button_draw.return_text)
                        else:
                            button_draw = draw.NormalDraw()
                            button_draw.text = book_text
                            button_draw.width = self.width
                            button_draw.style = book_style

                        # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                        now_draw.draw_list.append(button_draw)
                        now_draw.width += len(button_draw.text)
                        now_draw.draw_list.append(line_feed)
                        now_draw.width += 1

            resouce_draw = draw.NormalDraw()
            resouce_text = _("\n当前藏书情况：")
            resouce_text += _("\n  {0}在馆量/总藏书量：{1}/{2}\n").format(self.now_panel, book_can_borrow_count, book_count)
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

    def show_book(self, book_cid: int):
        """
        显示书籍信息
        Keyword arguments:
        book_cid -- 书籍编号
        """
        book_data = game_config.config_book[book_cid]
        book_name = book_data.name
        book_info = book_data.info
        # 处理换行符
        if "\\n" in book_info:
            book_info = book_info.replace("\\n", "\n")
        book_text = f"\n{book_name}\n\n{book_info}\n"
        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()
            return_list = []
            book_info_draw = draw.CenterDraw()
            book_info_draw.text = book_text
            book_info_draw.width = self.width
            book_info_draw.draw()
            line_feed.draw()

            # 如果已借该书，则显示还书按钮
            if cache.rhodes_island.book_borrow_dict[book_cid] == 0:
                borrow_buttin_text = _("[归还]")
            # 未借该书，则显示借书按钮
            else:
                borrow_buttin_text = _("[借阅]")

            borrow_button = draw.CenterButton(
                borrow_buttin_text, borrow_buttin_text, window_width / 2, cmd_func=self.borrow, args=(book_cid,)
            )
            borrow_button.draw()
            return_list.append(borrow_button.return_text)

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def borrow(self, book_cid: int):
        """
        借阅书籍
        Keyword arguments:
        book_cid -- 书籍编号
        """

        character_data: game_type.Character = cache.character_data[0]

        # 当前借书数量限制信息
        borrow_count = len(character_data.entertainment.borrow_book_id_set)

        # 如果已借该书，则还书
        if cache.rhodes_island.book_borrow_dict[book_cid] == 0:
            cache.rhodes_island.book_borrow_dict[book_cid] = -1
            character_data.entertainment.borrow_book_id_set.discard(book_cid)
        # 未借该书，且借书数量不到上限，则借书
        elif borrow_count < 3:
            cache.rhodes_island.book_borrow_dict[book_cid] = 0
            character_data.entertainment.borrow_book_id_set.add(book_cid)
        # 未借该书，且借书数量已达上限，则输出错误信息
        else:
            borrow_limit_draw = draw.WaitDraw()
            borrow_limit_text = _("\n已达到最大借书上限，无法继续借阅\n")
            borrow_limit_draw.text = borrow_limit_text
            borrow_limit_draw.width = self.width
            borrow_limit_draw.draw()

