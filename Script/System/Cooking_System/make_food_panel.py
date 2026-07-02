from typing import Tuple
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import update
from Script.System.Cooking_System import cooking, cook_question_panel
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.UI.Panel import achievement_panel, ejaculation_panel

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


class Make_food_Panel:
    """
    用于查看制作食物界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int, make_food_type: int = 0):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("主食")
        """ 当前绘制的食物类型 """
        self.handle_panel: panel.PageHandlePanel
        """ 当前名字列表控制面板make_food_type """
        self.make_food_type = make_food_type
        """ 0普通做饭，1泡咖啡，2酒类 """
        self.special_seasoning = 0
        """ 调味类型 """
        self.cook_mode = 0
        """ 烹饪模式：0标准模式，1精细模式 """

    def draw(self):
        """绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        title_draw = draw.TitleLineDraw(_("制作食物"), self.width)
        food_type_list = [_("主食"), _("零食"), _("饮品"), _("酒类")]
        if self.make_food_type == 1:
            food_type_list = [_("咖啡")]
            self.now_panel = _("咖啡")
        elif self.make_food_type == 2:
            food_type_list = [_("酒类")]
            self.now_panel = _("酒类")
        # food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        self.handle_panel = panel.PageHandlePanel([], SeeFoodListByFoodNameDraw, 50, 5, self.width, True, True, 0)
        while 1:
            cooking.init_makefood_data()
            py_cmd.clr_cmd()
            title_draw.draw()
            return_list = []
            for food_type in food_type_list:
                if food_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{food_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = int(self.width / len(food_type_list))
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{food_type}]",
                        food_type,
                        int(self.width / len(food_type_list)),
                        cmd_func=self.change_panel,
                        args=(food_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 筛选和排序按钮
            info_draw = draw.NormalDraw()
            info_draw.text = _("○筛选和排序：\n")
            info_draw.draw()
            filter_text, sort_text = self.get_filter_sort_status_text()
            filter_text = "[{0}]".format(filter_text)
            sort_text = "[{0}]".format(sort_text)
            empty_draw = draw.NormalDraw()
            empty_draw.text = "  "
            empty_draw.draw()
            filter_button = draw.LeftButton(
                filter_text,
                _("[筛选]"),
                int(self.width),
                cmd_func=self.open_filter_panel,
            )
            filter_button.draw()
            return_list.append(filter_button.return_text)
            line_feed.draw()
            empty_draw.draw()
            sort_button = draw.LeftButton(
                sort_text,
                _("[排序]"),
                int(self.width),
                cmd_func=self.open_sort_panel,
            )
            sort_button.draw()
            return_list.append(sort_button.return_text)
            line_feed.draw()

            # 加料说明
            now_draw = draw.NormalDraw()
            now_draw.text = _("○当前的调味：")
            # now_draw.width = 1
            now_draw.draw()

            # 加料面板
            for seasoning_cid in game_config.config_seasoning:
                # 不再显示基础调味
                if seasoning_cid <= 10:
                    continue
                    button_width = int(self.width / 16)
                    now_draw = draw.NormalDraw()
                    now_draw.text = _("\n  基础:    ")
                    # now_draw.width = 1
                    now_draw.draw()
                # 精液或下药则换行并加长文本宽度
                if seasoning_cid == 11:
                    button_width = int(self.width / 4)
                    now_draw = draw.NormalDraw()
                    now_draw.text = _("\n  精液:    ")
                    # now_draw.width = 1
                    now_draw.draw()
                elif seasoning_cid == 102:
                    button_width = int(self.width / 8 + 1)
                    now_draw = draw.NormalDraw()
                    now_draw.text = _("\n  药物:    ")
                    # now_draw.width = 1
                    now_draw.draw()
                # 如果是加药物需要已拥有药物
                if seasoning_cid > 100:
                    if not character_data.item[seasoning_cid] and not cache.debug_mode:
                        continue
                # 基础的按钮格式
                button_style = 'standard'
                # 如果当前调味为该调味则高亮显示
                if self.special_seasoning == seasoning_cid:
                    button_style = 'gold_enrod'

                button_text = f"[{game_config.config_seasoning[seasoning_cid].name}]"
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(button_text),
                    button_width,
                    normal_style=button_style,
                    cmd_func=self.choice_seasoning,
                    args=(seasoning_cid,),
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()
            line_feed.draw()

            # 烹饪模式面板（标准/精细），特殊调味也可选择精细模式（对应阶段会替换为特殊阶段的问题）
            mode_button_width = int(self.width / 6 + 1)
            mode_title = draw.NormalDraw()
            mode_title.text = _("○烹饪模式：\n")
            mode_title.draw()
            # 标准模式行
            if self.cook_mode == 0:
                std_draw = draw.CenterDraw()
                std_draw.text = _("[标准模式]")
                std_draw.style = "gold_enrod"
                std_draw.width = mode_button_width
                std_draw.draw()
            else:
                std_draw = draw.CenterButton(
                    _("[标准模式]"), _("标准模式"), mode_button_width,
                    cmd_func=self.change_cook_mode, args=(0,),
                )
                std_draw.draw()
                return_list.append(std_draw.return_text)
            std_info = draw.NormalDraw()
            std_info.text = _("：不考虑细节直接烹饪，烹饪出的食物品质与料理技能相关，品质上限为美味，无法达到绝珍的级别\n")
            std_info.draw()
            # 精细模式行
            if self.cook_mode == 1:
                fine_draw = draw.CenterDraw()
                fine_draw.text = _("[精细模式]")
                fine_draw.style = "gold_enrod"
                fine_draw.width = mode_button_width
                fine_draw.draw()
            else:
                fine_draw = draw.CenterButton(
                    _("[精细模式]"), _("精细模式"), mode_button_width,
                    cmd_func=self.change_cook_mode, args=(1,),
                )
                fine_draw.draw()
                return_list.append(fine_draw.return_text)
            fine_info = draw.NormalDraw()
            fine_info.text = _("：仔细考虑烹饪细节，根据细节的处理方式，食物品质能在料理技能的基础上进一步提升，最高可达到绝珍的级别\n")
            fine_info.draw()
            line_feed.draw()
            line_feed.draw()

            # 食物面板
            now_draw = draw.NormalDraw()
            now_draw.text = _("○选择要制作的食物：\n")
            # now_draw.width = 1
            now_draw.draw()
            food_name_list = cooking.get_filtered_sorted_cook_data(self.now_panel)
            # 将调味、烹饪模式增加进去
            food_name_list = [(x[0], x[1], self.special_seasoning, self.cook_mode) for x in food_name_list]
            self.handle_panel.text_list = food_name_list
            self.handle_panel.update()
            self.handle_panel.draw()

            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            # 进入本轮输入前重置二级确认结果，避免沿用上一次状态
            SeeFoodListByFoodNameDraw.last_confirm_result = ""
            if yrn in self.handle_panel.return_list and SeeFoodListByFoodNameDraw.last_confirm_result == _("取消"):
                yrn = _("取消")
            if (yrn == back_draw.return_text or 
            (yrn in self.handle_panel.return_list and yrn not in {self.handle_panel.old_page_return, self.handle_panel.next_page_return, _("取消"), _("[取消]"), _("返回"), _("[返回]")})):
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, food_type: str):
        """
        切换当前面板显示的食物类型
        Keyword arguments:
        food_type -- 要切换的食物类型
        """
        self.now_panel = food_type

        food_name_list = cooking.get_filtered_sorted_cook_data(self.now_panel)
        # 将调味、烹饪模式增加进去
        food_name_list = [(x[0], x[1], self.special_seasoning, self.cook_mode) for x in food_name_list]

        self.handle_panel = panel.PageHandlePanel(
            food_name_list, SeeFoodListByFoodNameDraw, 50, 5, self.width, True, True, 0
        )

    def choice_seasoning(self, seasoning_cid):
        """选择味道"""
        # 如果当前调味为该调味则取消选择
        if self.special_seasoning == seasoning_cid:
            self.special_seasoning = 0
        else:
            self.special_seasoning = seasoning_cid

    def change_cook_mode(self, cook_mode: int):
        """
        切换烹饪模式
        Keyword arguments:
        cook_mode -- 烹饪模式：0标准，1精细
        """
        self.cook_mode = cook_mode

    def get_filter_sort_status_text(self) -> tuple:
        """
        获取筛选和排序的状态文本
        Return arguments:
        tuple -- (筛选状态文本, 排序状态文本)
        """
        # 类型名称映射
        type_name_map = {
            0: _("正餐"), 1: _("零食"), 2: _("饮品"), 3: _("酒类"),
            4: _("乳制品"), 5: _("预制食物"), 8: _("加料咖啡"), 9: _("其他")
        }
        difficulty_name_map = {-1: _("无"), 0: _("简单(0-3)"), 1: _("中等(4-6)"), 2: _("困难(7+)")}
        time_name_map = {-1: _("无"), 0: _("快速(≤30分)"), 1: _("中等(31-60分)"), 2: _("耗时(61+分)")}
        sort_type_name_map = {0: _("无"), 1: _("难度"), 2: _("时间"), 3: _("类型")}
        sort_order_name_map = {0: _("升序"), 1: _("降序")}

        # 构建筛选状态文本
        filter_parts = []
        filter_type = cache.rhodes_island.makefood_filter_type
        filter_difficulty = cache.rhodes_island.makefood_filter_difficulty
        filter_time = cache.rhodes_island.makefood_filter_time
        
        if filter_type:
            type_names = [type_name_map.get(t, str(t)) for t in filter_type]
            filter_parts.append(_("类型:{0}").format(",".join(type_names)))
        if filter_difficulty != -1:
            filter_parts.append(_("难度:{0}").format(difficulty_name_map[filter_difficulty]))
        if filter_time != -1:
            filter_parts.append(_("时间:{0}").format(time_name_map[filter_time]))
        
        if filter_parts:
            filter_text = _("筛选：{0}").format(" ".join(filter_parts))
        else:
            filter_text = _("筛选：无")

        # 构建排序状态文本
        sort_type = cache.rhodes_island.makefood_sort_type
        sort_order = cache.rhodes_island.makefood_sort_order
        
        if sort_type != 0:
            sort_text = _("排序：{0}{1}").format(
                sort_type_name_map[sort_type],
                sort_order_name_map[sort_order]
            )
        else:
            sort_text = _("排序：无")

        return filter_text, sort_text

    def open_filter_panel(self):
        """
        打开筛选设置面板
        设置筛选时会重置排序
        """
        # 类型名称映射
        type_name_map = {
            0: _("正餐"), 1: _("零食"), 2: _("饮品"), 3: _("酒类"),
            4: _("乳制品"), 5: _("预制食物"), 8: _("加料咖啡"), 9: _("其他")
        }
        difficulty_options = [
            (-1, _("不限")), (0, _("简单(0-3)")), (1, _("中等(4-6)")), (2, _("困难(7+)"))
        ]
        time_options = [
            (-1, _("不限")), (0, _("快速(≤30分)")), (1, _("中等(31-60分)")), (2, _("耗时(61+分)"))
        ]
        
        while 1:
            py_cmd.clr_cmd()
            return_list = []
            
            title_draw = draw.TitleLineDraw(_("筛选设置"), self.width)
            title_draw.draw()
            
            # 类型筛选（标签模式，点击切换）
            info_draw = draw.NormalDraw()
            info_draw.text = _("○类型筛选（点击切换）：\n")
            info_draw.draw()
            
            current_filter_type = cache.rhodes_island.makefood_filter_type
            for type_id, type_name in type_name_map.items():
                if type_id in current_filter_type:
                    button_text = f"[√{type_name}]"
                    style = "onbutton"
                else:
                    button_text = f"[{type_name}]"
                    style = "standard"
                type_button = draw.CenterButton(
                    button_text,
                    f"type_{type_id}",
                    int(self.width / 10),
                    cmd_func=self.toggle_filter_type,
                    args=(type_id,),
                )
                type_button.draw()
                return_list.append(type_button.return_text)
            line_feed.draw()
            line_feed.draw()
            
            # 难度筛选
            info_draw = draw.NormalDraw()
            info_draw.text = _("○难度筛选：\n")
            info_draw.draw()
            
            current_difficulty = cache.rhodes_island.makefood_filter_difficulty
            for diff_id, diff_name in difficulty_options:
                if diff_id == current_difficulty:
                    button_text = f"[●{diff_name}]"
                else:
                    button_text = f"[{diff_name}]"
                diff_button = draw.CenterButton(
                    button_text,
                    f"diff_{diff_id}",
                    int(self.width / 10),
                    cmd_func=self.set_filter_difficulty,
                    args=(diff_id,),
                )
                diff_button.draw()
                return_list.append(diff_button.return_text)
            line_feed.draw()
            line_feed.draw()
            
            # 时间筛选
            info_draw = draw.NormalDraw()
            info_draw.text = _("○时间筛选：\n")
            info_draw.draw()
            
            current_time = cache.rhodes_island.makefood_filter_time
            for time_id, time_name in time_options:
                if time_id == current_time:
                    button_text = f"[● {time_name}]"
                else:
                    button_text = f"[  {time_name}]"
                time_button = draw.CenterButton(
                    button_text,
                    f"time_{time_id}",
                    int(self.width / 10),
                    cmd_func=self.set_filter_time,
                    args=(time_id,),
                )
                time_button.draw()
                return_list.append(time_button.return_text)
            line_feed.draw()
            line_feed.draw()
            
            # 清除筛选和返回按钮
            clear_button = draw.CenterButton(_("[清除所有筛选]"), _("清除筛选"), int(self.width / 2))
            clear_button.draw()
            return_list.append(clear_button.return_text)
            back_button = draw.CenterButton(_("[返回]"), _("返回"), int(self.width / 2))
            back_button.draw()
            return_list.append(back_button.return_text)
            line_feed.draw()
            
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_button.return_text:
                break
            elif yrn == clear_button.return_text:
                self.clear_filter()

    def toggle_filter_type(self, type_id: int):
        """切换类型筛选"""
        # 设置筛选时重置排序
        cache.rhodes_island.makefood_sort_type = 0
        cache.rhodes_island.makefood_sort_order = 0
        
        if type_id in cache.rhodes_island.makefood_filter_type:
            cache.rhodes_island.makefood_filter_type.remove(type_id)
        else:
            cache.rhodes_island.makefood_filter_type.append(type_id)

    def set_filter_difficulty(self, difficulty: int):
        """设置难度筛选"""
        # 设置筛选时重置排序
        cache.rhodes_island.makefood_sort_type = 0
        cache.rhodes_island.makefood_sort_order = 0
        
        cache.rhodes_island.makefood_filter_difficulty = difficulty

    def set_filter_time(self, time_level: int):
        """设置时间筛选"""
        # 设置筛选时重置排序
        cache.rhodes_island.makefood_sort_type = 0
        cache.rhodes_island.makefood_sort_order = 0
        
        cache.rhodes_island.makefood_filter_time = time_level

    def clear_filter(self):
        """清除所有筛选"""
        cache.rhodes_island.makefood_filter_type = []
        cache.rhodes_island.makefood_filter_difficulty = -1
        cache.rhodes_island.makefood_filter_time = -1

    def open_sort_panel(self):
        """
        打开排序设置面板
        设置排序时会重置筛选
        """
        sort_type_options = [
            (0, _("无")), (1, _("按难度")), (2, _("按时间")), (3, _("按类型"))
        ]
        sort_order_options = [
            (0, _("升序")), (1, _("降序"))
        ]
        
        while 1:
            py_cmd.clr_cmd()
            return_list = []
            
            title_draw = draw.TitleLineDraw(_("排序设置"), self.width)
            title_draw.draw()
            
            # 排序维度
            info_draw = draw.NormalDraw()
            info_draw.text = _("○排序维度：\n")
            info_draw.draw()
            
            current_sort_type = cache.rhodes_island.makefood_sort_type
            for sort_id, sort_name in sort_type_options:
                if sort_id == current_sort_type:
                    button_text = f"[●{sort_name}]"
                else:
                    button_text = f"[{sort_name}]"
                sort_button = draw.CenterButton(
                    button_text,
                    f"sort_{sort_id}",
                    int(self.width / 10),
                    cmd_func=self.set_sort_type,
                    args=(sort_id,),
                )
                sort_button.draw()
                return_list.append(sort_button.return_text)
            line_feed.draw()
            line_feed.draw()
            
            # 排序顺序
            info_draw = draw.NormalDraw()
            info_draw.text = _("○排序顺序：\n")
            info_draw.draw()
            
            current_sort_order = cache.rhodes_island.makefood_sort_order
            for order_id, order_name in sort_order_options:
                if order_id == current_sort_order:
                    button_text = f"[●{order_name}]"
                else:
                    button_text = f"[{order_name}]"
                order_button = draw.CenterButton(
                    button_text,
                    f"order_{order_id}",
                    int(self.width / 10),
                    cmd_func=self.set_sort_order,
                    args=(order_id,),
                )
                order_button.draw()
                return_list.append(order_button.return_text)
            line_feed.draw()
            line_feed.draw()
            
            # 返回按钮
            back_button = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_button.draw()
            return_list.append(back_button.return_text)
            line_feed.draw()
            
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_button.return_text:
                break

    def set_sort_type(self, sort_type: int):
        """设置排序维度"""
        # 设置排序时重置筛选
        cache.rhodes_island.makefood_filter_type = []
        cache.rhodes_island.makefood_filter_difficulty = -1
        cache.rhodes_island.makefood_filter_time = -1
        
        cache.rhodes_island.makefood_sort_type = sort_type

    def set_sort_order(self, sort_order: int):
        """设置排序顺序"""
        # 设置排序时重置筛选
        cache.rhodes_island.makefood_filter_type = []
        cache.rhodes_island.makefood_filter_difficulty = -1
        cache.rhodes_island.makefood_filter_time = -1
        
        cache.rhodes_island.makefood_sort_order = sort_order


class SeeFoodListByFoodNameDraw:
    """
    点击后可查看食物列表的食物名字按钮对象
    Keyword arguments:
    text -- 食物名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """
    def __init__(
        self, text: Tuple[str, str, int, int], width: int, is_button: bool, num_button: bool, button_id: int,
    ):
        """初始化绘制对象"""
        self.cid: str = text[0]
        """ 菜谱id字符串 """
        self.text: str = text[1]
        """ 食物名字 """
        self.special_seasoning = text[2]
        """ 调味类型 """
        self.cook_mode = text[3]
        """ 烹饪模式：0标准模式，1精细模式 """
        self.draw_text: str = ""
        """ 食物名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        self.make_food_time: int = 0
        """ 做饭所需时间 """
        self.food_name: str = ""
        """ 食物名字 """
        self.add_coffee: bool = False
        """ 是否为加料咖啡 """
        self.last_confirm_result: str = ""
        """ 记录二级确认面板最后一次操作结果（如：取消） """

        # 延迟创建：此处仅根据菜谱id读取菜谱信息，不创建食物对象
        self.food_cid: str = self.cid
        """ 菜谱id字符串 """
        food_recipe: game_type.Recipes = cache.recipe_data[int(self.food_cid)]
        self.food_name = food_recipe.name
        self.make_food_time = food_recipe.time
        if food_recipe.type == 8:
            self.add_coffee = True

        # 按钮绘制
        name_draw = draw.NormalDraw()
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}{self.food_name}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.make_food_for_sure
                )
            else:
                button_text = f"[{self.food_name}]"
                name_draw = draw.CenterButton(
                    button_text, str(self.text), self.width, cmd_func=self.make_food_for_sure
                )
            self.button_return = name_draw.return_text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{self.food_name}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def make_food_for_sure(self):
        """确认是否制作食物，并选择制作数量"""
        from Script.Design import basement

        character_data: game_type.Character = cache.character_data[0]
        food_recipe = cache.recipe_data[int(self.food_cid)]
        food_name = self.food_name
        food_diffucty = food_recipe.difficulty
        seasoning_name = game_config.config_seasoning[self.special_seasoning].name
        facility_adjust = basement.calc_facility_efficiency(5)

        # 计算最大可制作数量（上限10，药物调味时受药物库存限制）
        max_count = 10
        if self.special_seasoning > 100:
            max_count = min(max_count, character_data.item[self.special_seasoning])
        max_count = max(1, max_count)
        make_count = 1

        while 1:
            py_cmd.clr_cmd()
            line_feed.draw()

            # 计算总耗时：基础时间 + 每多一份增加食谱时间的10%，再根据设施效率调整
            base_total_time = int(self.make_food_time * (1 + (make_count - 1) * 0.1))
            make_food_time = base_total_time
            facility_adjust_str = ""
            if facility_adjust != 1.0 and base_total_time > 0:
                make_food_time = int(base_total_time / facility_adjust)
                rate = (make_food_time - base_total_time) / base_total_time
                if rate > 0:
                    facility_adjust_str = _("（+{0:.1f}%）").format(rate * 100)
                elif rate < 0:
                    facility_adjust_str = _("（{0:.1f}%）").format(rate * 100)

            # 输出食物的名字、菜谱难度、制作数量、预计耗时、调味
            confirm_text = ""
            confirm_text += _("食物名字: {0}\n").format(food_name)
            confirm_text += _("菜谱难度: {0}\n").format(food_diffucty)
            confirm_text += _("制作数量: {0} （最多 {1}）\n").format(make_count, max_count)
            confirm_text += _("预计耗时: {0} 分钟{1}\n").format(make_food_time, facility_adjust_str)
            confirm_text += _("当前调味: {0}\n").format(seasoning_name)
            info_draw = draw.NormalDraw()
            info_draw.text = confirm_text
            info_draw.draw()
            line_feed.draw()

            # 数量调整按钮
            return_list = []
            minus_draw = draw.CenterButton(_("[-1]"), _("减少"), int(window_width / 4))
            minus_draw.draw()
            return_list.append(minus_draw.return_text)
            plus_draw = draw.CenterButton(_("[+1]"), _("增加"), int(window_width / 4))
            plus_draw.draw()
            return_list.append(plus_draw.return_text)
            max_draw = draw.CenterButton(_("[最大]"), _("最大"), int(window_width / 4))
            max_draw.draw()
            return_list.append(max_draw.return_text)
            line_feed.draw()
            line_feed.draw()

            # 确认/取消按钮
            confirm_draw = draw.CenterButton(_("[确认制作]"), _("确认"), int(window_width / 2))
            confirm_draw.draw()
            return_list.append(confirm_draw.return_text)
            cancel_draw = draw.CenterButton(_("[取消]"), _("取消"), int(window_width / 2))
            cancel_draw.draw()
            return_list.append(cancel_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == minus_draw.return_text:
                make_count = max(1, make_count - 1)
            elif yrn == plus_draw.return_text:
                make_count = min(max_count, make_count + 1)
            elif yrn == max_draw.return_text:
                make_count = max_count
            elif yrn == confirm_draw.return_text:
                self.make_food(make_food_time, make_count)
                SeeFoodListByFoodNameDraw.last_confirm_result = _("确认")
                break
            else:
                SeeFoodListByFoodNameDraw.last_confirm_result = _("取消")
                break

    def make_food(self, new_make_food_time: int = 0, make_count: int = 1):
        """
        玩家制作食物
        Keyword arguments:
        new_make_food_time -- 本次制作的总耗时（分钟）
        make_count -- 制作数量
        """
        from Script.Design import handle_premise
        character_data: game_type.Character = cache.character_data[0]
        food_recipe: game_type.Recipes = cache.recipe_data[int(self.food_cid)]

        # 计算食物品质：基础品质为玩家料理技能，封顶到美味
        base_quality = cooking.get_base_food_quality(0)
        # 如果当前是酒类，且当前地点在酒吧，则品质额外+1
        if food_recipe.type == 3 and handle_premise.handle_in_bar(0):
            base_quality += 1
        food_quality = base_quality
        # 精细模式且存在题库时，进入答题流程（特殊调味会替换对应阶段的问题），答对可提升品质（封顶绝珍）
        if (
            self.cook_mode == 1
            and cooking.has_cook_question_library(int(self.food_cid))
        ):
            food_quality = cook_question_panel.run_cook_question_flow(
                int(self.food_cid), base_quality, self.special_seasoning
            )

        # 按数量逐个创建食物对象（延迟创建：仅在制作时才创建对应菜谱的食物对象）
        real_count = 0
        for _i in range(make_count):
            # 药物调味则每份扣除一个药物，库存不足时停止制作
            if self.special_seasoning > 100:
                if character_data.item[self.special_seasoning] <= 0:
                    break
                character_data.item[self.special_seasoning] -= 1
            # 精液调味则每份扣除一次精液量，库存不足时停止制作
            if self.special_seasoning in {11, 12}:
                semen_text, semen_count = ejaculation_panel.common_ejaculation()
                if semen_count <= 0:
                    break
            # 创建食物对象并赋予名字、作者、品质、味道
            new_food = cooking.create_food("", int(self.food_cid), food_quality, character_data.name)
            new_food.special_seasoning = self.special_seasoning
            if self.special_seasoning in {11, 12}:
                new_food.special_seasoning_amount = semen_count
            # 放到玩家背包里
            character_data.food_bag[new_food.uid] = new_food
            # 成就计数
            cache.achievement.make_food_count += 1
            real_count += 1

        # 烹饪行为
        character_data.behavior.food_name = self.food_name
        character_data.behavior.make_food_time = new_make_food_time
        character_data.behavior.food_seasoning = self.special_seasoning
        character_data.behavior.cook_difficulty = food_recipe.difficulty
        character_data.behavior.make_food_count = real_count
        character_data.behavior.behavior_id = constant.Behavior.MAKE_FOOD
        character_data.behavior.duration = new_make_food_time
        character_data.state = constant.CharacterStatus.STATUS_MAKE_FOOD
        # 如果是加料咖啡，则标记为正在制作加料咖啡
        if self.add_coffee:
            character_data.behavior.behavior_id = constant.Behavior.MAKE_COFFEE_ADD
            character_data.state = constant.CharacterStatus.STATUS_MAKE_COFFEE_ADD
        update.game_update_flow(new_make_food_time)
        # 结算成就
        achievement_panel.achievement_flow(_("烹饪"))

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

