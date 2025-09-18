from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import common_select_NPC
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


        title_text = _("管理图书馆")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            # line = draw.LineDraw("-", window_width)
            # line.draw()
            cinfo_draw = draw.NormalDraw()
            info_text = _("\n要进行哪方面的管理呢？\n")
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            # 选项面板
            # button_all_draw = panel.LeftDrawTextListPanel()

            button0_text = _("[001]催还书")
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
                button1_text = _("[002]图书进货(未实装)")
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
                button2_text = _("[003]阅读推荐")
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
                button3_text = _("[004]读书会")
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

            if 1:
                button4_text = _("[005]借阅历史记录")
                button4_draw = draw.LeftButton(
                    _(button4_text),
                    _("5"),
                    window_width,
                    cmd_func=self.borrowing_history,
                    args=(),
                    )
                line_feed.draw()
                button4_draw.draw()
                return_list.append(button4_draw.return_text)

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
                if book_type_cid == 0:
                    continue
                book_type_data = game_config.config_book_type[book_type_cid]
                for book_cid in game_config.config_book_type_data[book_type_cid]:
                    book_data = game_config.config_book[book_cid]
                    if cache.rhodes_island.book_borrow_dict[book_cid] > 0 :
                        book_count += 1
                        book_text = f"  [{str(book_count).rjust(3,'0')}]({book_type_data.son_type_name}){book_data.name}"
                        borrow_npc_id = cache.rhodes_island.book_borrow_dict[book_cid]
                        borrow_npc_name = cache.character_data[borrow_npc_id].name
                        book_text += _("  (被{0}借走)").format(borrow_npc_name)

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
                now_draw.text = _("\n  目前无人借书，不需要催还\n")
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
        now_draw.text = _("\n{0}将在空闲时间前往图书馆还书\n").format(character_data.name)
        now_draw.draw()


    def get_new_book(self):
        """图书进货"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n暂未实装\n")
        now_draw.draw()


    def read_recommend(self):
        """阅读推荐"""

        self.handle_panel = panel.PageHandlePanel([], SelectRecommendBookButton, 999, 6, self.width, True, True, 0)

        while 1:

            # 显示提示信息
            line = draw.LineDraw("-", self.width)
            line.draw()
            info_draw = draw.NormalDraw()
            can_recommend_count = 3 - len(cache.rhodes_island.recommend_book_type_set)
            info_draw.text = _("\n 当前剩余可选推荐 {0}\n").format(can_recommend_count)
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
            now_draw.text = _("\n  要把哪一天定为读书会呢？\n")
            now_draw.draw()

            # 遍历一周七天
            for i in range(7):
                week_date_data = game_config.config_week_day[i]
                button_text = f"  [{i}]:{week_date_data.name}"
                party_entertain_id = cache.rhodes_island.party_day_of_week[i]
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

        party_entertain_id = cache.rhodes_island.party_day_of_week[week_day]

        if party_entertain_id == 101:
            cache.rhodes_island.party_day_of_week[week_day] = 0
        elif party_entertain_id:
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = _("\n这一天已经被选为其他活动了\n")
            now_draw.draw()
        else:
            # 先取消掉其他日子可能有的读书会
            for i in range(7):
                party_entertain_all_id = cache.rhodes_island.party_day_of_week[i]
                if party_entertain_all_id == 101:
                    cache.rhodes_island.party_day_of_week[i] = 0

            # 再把指定日子变成读书会
            cache.rhodes_island.party_day_of_week[week_day] = 101

    def borrowing_history(self):
        """借阅历史记录查看"""
        
        # 创建角色列表，包含所有有借阅历史的角色
        character_list = []
        for character_id in cache.character_data:
            if character_id == 0:  # 跳过玩家
                continue
            character_data = cache.character_data[character_id]
            # 检查是否有借阅历史记录
            if hasattr(character_data.entertainment, 'borrow_book_history') and len(character_data.entertainment.borrow_book_history) > 0:
                character_list.append([character_id, self.show_character_history, []])
        
        # 如果没有任何角色有借阅历史
        if not character_list:
            while 1:
                line_feed.draw()
                line = draw.LineDraw("-", window_width)
                line.draw()
                
                no_history_draw = draw.NormalDraw()
                no_history_draw.width = window_width
                no_history_draw.text = _("\n  暂无任何角色的借阅历史记录\n")
                no_history_draw.draw()
                
                line_feed.draw()
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
                back_draw.draw()
                yrn = flow_handle.askfor_all([back_draw.return_text])
                
                if yrn == back_draw.return_text:
                    break
        else:
            # 保存原始角色列表
            original_character_list = character_list.copy()
            # 创建分页面板来显示角色列表
            self.character_handle_panel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 10, 5, window_width, True, False, 0)
            select_state = {}
            
            while 1:
                info_text = _("以下角色拥有借阅历史记录：\n\n")
                
                # 在每次循环开始时恢复原始列表，避免筛选累积
                self.character_handle_panel.text_list = original_character_list.copy()
                
                # 使用通用角色选择面板
                return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(
                    self.character_handle_panel, 
                    _("借阅历史记录"), 
                    info_text,
                    select_state
                )
                
                yrn = flow_handle.askfor_all(return_list)
                
                # 如果点击返回按钮，退出面板
                if yrn == _("返回"):
                    break

    def show_character_history(self, character_id: int):
        """显示指定角色的借阅历史"""
        
        character_data = cache.character_data[character_id]
        
        while 1:
            return_list = []
            
            # 显示标题
            title_text = _("[{0}]的借书卡记录").format(character_data.name)
            title_draw = draw.TitleLineDraw(title_text, window_width)
            title_draw.draw()
            line_feed.draw()
            
            # 检查是否有借阅历史
            if not hasattr(character_data.entertainment, 'borrow_book_history') or len(character_data.entertainment.borrow_book_history) == 0:
                no_history_draw = draw.NormalDraw()
                no_history_draw.width = window_width
                no_history_draw.text = _("\n  该角色暂无借阅历史记录\n")
                no_history_draw.draw()
            else:
                # 显示借阅历史统计信息
                total_books = len(character_data.entertainment.borrow_book_history)
                total_reads = sum(record.get('total_read_count', 0) for record in character_data.entertainment.borrow_book_history)
                
                stats_draw = draw.NormalDraw()
                stats_draw.width = window_width
                stats_text = _("\n  借阅历史统计：共借阅过{0}本书，累计阅读{1}次\n").format(total_books, total_reads)
                stats_draw.text = stats_text
                stats_draw.draw()
                
                line_feed.draw()
                
                # 显示详细的借阅记录
                for i, record in enumerate(reversed(character_data.entertainment.borrow_book_history)):
                    book_id = record.get('book_id', 0)
                    book_name = record.get('book_name', _('未知书籍'))
                    borrow_time = record.get('borrow_time', None)
                    return_time = record.get('return_time', None)
                    read_count = record.get('total_read_count', 0)
                    
                    # 格式化时间显示
                    borrow_time_str = ""
                    return_time_str = ""
                    if borrow_time:
                        if isinstance(borrow_time, str):
                            borrow_time_str = borrow_time
                        else:
                            borrow_time_str = borrow_time.strftime("%Y年%m月%d日 %H:%M")
                    
                    if return_time:
                        if isinstance(return_time, str):
                            return_time_str = return_time
                        else:
                            return_time_str = return_time.strftime("%Y年%m月%d日 %H:%M")
                    else:
                        return_time_str = _("仍在借阅中")
                    
                    # 构建记录文本
                    record_text = _("  [{0}] 《{1}》").format(str(i+1).rjust(2,'0'), book_name)
                    if book_id in game_config.config_book:
                        book_type_data = game_config.config_book_type[game_config.config_book[book_id].type]
                        record_text += _(" ({0})").format(book_type_data.son_type_name)
                    
                    record_text += _("\n      借书时间：{0}").format(borrow_time_str)
                    record_text += _("\n      还书时间：{0}").format(return_time_str)
                    record_text += _("\n      阅读次数：{0}次\n").format(read_count)
                    
                    record_draw = draw.NormalDraw()
                    record_draw.width = window_width
                    record_draw.text = record_text
                    record_draw.draw()
                    
                    line_feed.draw()
            
            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


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
        if self.book_type_id in cache.rhodes_island.recommend_book_type_set:
            button_text += _(" (已推荐)")
            name_draw = draw.LeftButton(button_text, self.button_return, self.width,normal_style = "gold_enrod", cmd_func=self.button_0)
        else:
            name_draw = draw.LeftButton(button_text, self.button_return, self.width, cmd_func=self.button_0)

        """ 绘制的对象 """
        self.now_draw = name_draw

    def button_0(self):
        """选项1"""
        if self.book_type_id in cache.rhodes_island.recommend_book_type_set:
            cache.rhodes_island.recommend_book_type_set.remove(self.book_type_id)
        elif 3 - len(cache.rhodes_island.recommend_book_type_set):
            cache.rhodes_island.recommend_book_type_set.add(self.book_type_id)

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

