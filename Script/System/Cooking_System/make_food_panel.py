from typing import Tuple
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import update, attr_calculation
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

def draw_q(val: int):
    """
    绘制品质预测文本
    Keyword arguments:
    val -- 食物品质值
    """
    _level, quality_name = attr_calculation.get_food_quality(val)
    d = draw.NormalDraw()
    d.text = f"[{quality_name}+{val}]"
    if val >= 7:
        d.style = "green"
    d.draw()


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
        # 烹饪模式与制作数量改为按做饭类型记忆在罗德岛数据里（与做饭面板的筛选/排序一致）
        # 进入面板时做一次值域校验，防止旧存档或模组写入的非法值导致两个模式按钮都不高亮
        if not isinstance(cache.rhodes_island.makefood_cook_mode, dict):
            cache.rhodes_island.makefood_cook_mode = {}
        if not isinstance(cache.rhodes_island.makefood_make_count, dict):
            cache.rhodes_island.makefood_make_count = {}
        if cache.rhodes_island.makefood_cook_mode.get(self.make_food_type, 0) not in {0, 1, 2}:
            cache.rhodes_island.makefood_cook_mode[self.make_food_type] = 0
        self.show_favorites_only = False
        """ 是否只显示收藏菜谱 """

    @property
    def cook_mode(self) -> int:
        """
        当前的烹饪模式（读罗德岛缓存，按做饭类型记忆玩家上一次的选择）
        Return arguments:
        int -- 烹饪模式：0标准，1精细
        """
        return cache.rhodes_island.makefood_cook_mode.get(self.make_food_type, 0)

    @cook_mode.setter
    def cook_mode(self, cook_mode: int):
        """
        设置烹饪模式并写回罗德岛缓存，使下次打开同类型面板时沿用
        Keyword arguments:
        cook_mode -- 烹饪模式：0标准，1精细
        """
        cache.rhodes_island.makefood_cook_mode[self.make_food_type] = cook_mode

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
        # 做饭面板追加庆典与收藏入口（泡咖啡/调酒保持原样）
        if self.make_food_type == 0:
            food_type_list.append(cooking.FEAST_TAB_NAME)
            food_type_list.append(_("收藏"))
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
            info_draw.text = _("○筛选：\n")
            info_draw.draw()
            filter_text, sort_text = self.get_filter_sort_status_text()
            filter_text = "[{0}]".format(filter_text)
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
            
            empty_draw = draw.NormalDraw()
            empty_draw.text = "  "
            empty_draw.draw()
            
            reset_button = draw.CenterButton(
                _("[重置]"),
                _("重置所有"),
                int(self.width / 16),
                cmd_func=self.clear_filter_and_sort,
            )
            reset_button.draw()
            return_list.append(reset_button.return_text)
            # 只看收藏切换（做饭面板专属）
            if self.make_food_type == 0:
                fav_filter_text = _("[只看收藏]") if not self.show_favorites_only else _("[显示全部]")
                fav_filter_button = draw.CenterButton(
                    fav_filter_text, _("切换只看收藏"), int(self.width / 16),
                    cmd_func=self.toggle_favorites_only,
                )
                fav_filter_button.draw()
                return_list.append(fav_filter_button.return_text)
            line_feed.draw()
            
            # 排序维度 (直接列出两行)
            sort_title = draw.NormalDraw()
            sort_title.text = _("○排序维度：")
            sort_title.draw()
            sort_type_options = [(0, _("无")), (1, _("难度")), (2, _("时间")), (3, _("类型"))]
            for sort_id, sort_name in sort_type_options:
                if sort_id == cache.rhodes_island.makefood_sort_type:
                    btn_text = f"[●{sort_name}]"
                else:
                    btn_text = f"[{sort_name}]"
                btn = draw.CenterButton(
                    btn_text, f"sort_type_{sort_id}", int(self.width / 6),
                    cmd_func=self.set_sort_type, args=(sort_id,)
                )
                btn.draw()
                return_list.append(btn.return_text)
            line_feed.draw()

            # 排序顺序 (直接列出两行)
            order_title = draw.NormalDraw()
            order_title.text = _("○排序顺序：")
            order_title.draw()
            sort_order_options = [(0, _("升序")), (1, _("降序"))]
            for order_id, order_name in sort_order_options:
                if order_id == cache.rhodes_island.makefood_sort_order:
                    btn_text = f"[●{order_name}]"
                else:
                    btn_text = f"[{order_name}]"
                btn = draw.CenterButton(
                    btn_text, f"sort_order_{order_id}", int(self.width / 6),
                    cmd_func=self.set_sort_order, args=(order_id,)
                )
                btn.draw()
                return_list.append(btn.return_text)
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
            # 大师模式行（料理技能达标后解锁，免答题稳定绝珍）
            if cooking.is_master_unlocked():
                if self.cook_mode == 2:
                    master_draw = draw.CenterDraw()
                    master_draw.text = _("[大师模式]")
                    master_draw.style = "gold_enrod"
                    master_draw.width = mode_button_width
                    master_draw.draw()
                else:
                    master_draw = draw.CenterButton(
                        _("[大师模式]"), _("大师模式"), mode_button_width,
                        cmd_func=self.change_cook_mode, args=(2,),
                    )
                    master_draw.draw()
                    return_list.append(master_draw.return_text)
                master_info = draw.NormalDraw()
                master_info.text = _("：免答题直接烹饪，稳定达到绝珍品质\n")
                master_info.draw()
            
            # 品质预测绘制
            q_label = draw.NormalDraw()
            q_label.text = _("○品质预测：")
            q_label.draw()
            
            base_quality = cooking.get_base_food_quality(0)
            max_quality = base_quality
            if self.cook_mode == 1:
                max_quality = min(base_quality + 4, cooking.get_max_food_quality())
            elif self.cook_mode == 2 and cooking.is_master_unlocked():
                max_quality = cooking.get_max_food_quality()
                
            if self.cook_mode == 2 and cooking.is_master_unlocked():
                draw_q(cooking.get_max_food_quality())
                stable_draw = draw.NormalDraw()
                stable_draw.text = _("（稳定）")
                stable_draw.draw()
            else:
                draw_q(base_quality)
                if max_quality != base_quality:
                    tilde = draw.NormalDraw()
                    tilde.text = "~"
                    tilde.draw()
                    draw_q(max_quality)
            
            line_feed.draw()
            line_feed.draw()

            # 食物面板
            now_draw = draw.NormalDraw()
            now_draw.text = _("○选择要制作的食物：\n")
            # now_draw.width = 1
            now_draw.draw()

            food_line = draw.LineDraw("-", self.width)
            food_line.draw()

            if self.now_panel == _("收藏"):
                food_name_list = []
                for fid in cooking.get_favorite_recipe_ids():
                    try:
                        recipe = game_config.config_recipes[fid]
                        food_name_list.append((str(fid), recipe.name))
                    except Exception:
                        pass
            else:
                food_name_list = cooking.get_filtered_sorted_cook_data(self.now_panel)
                if self.show_favorites_only:
                    food_name_list = [x for x in food_name_list if cooking.has_favorites(x[0])]
            # 将调味、烹饪模式、做饭类型增加进去
            food_name_list = [(x[0], x[1], self.special_seasoning, self.cook_mode, self.make_food_type) for x in food_name_list]
            
            # 填满行数，保持翻页时高度一致（每页50个物品：10行5列）
            pad_count = 50 - (len(food_name_list) % 50)
            # 如果刚好是50的倍数且列表非空，则不需要填充
            if pad_count == 50 and len(food_name_list) > 0:
                pad_count = 0
            if pad_count > 0:
                # 使用 "-1" 作为 cid 标识空项，让 SeeFoodListByFoodNameDraw 绘制空白
                food_name_list.extend([("-1", "", self.special_seasoning, self.cook_mode, self.make_food_type)] * pad_count)

            self.handle_panel.text_list = food_name_list
            self.handle_panel.update()
            self.handle_panel.draw()
            
            food_line = draw.LineDraw("-", self.width)
            food_line.draw()

            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            
            # 进入本轮输入前重置二级确认结果，避免沿用上一次状态
            SeeFoodListByFoodNameDraw.last_confirm_result = ""
            
            yrn = flow_handle.askfor_all(return_list)
            
            # 判定结果
            if yrn in self.handle_panel.return_list and SeeFoodListByFoodNameDraw.last_confirm_result == _("取消"):
                # 按下取消按钮回到选择菜品列表
                pass
            elif (yrn == back_draw.return_text or 
            (yrn in self.handle_panel.return_list and SeeFoodListByFoodNameDraw.last_confirm_result == _("确认"))):
                # 选择返回或者确认制作成功后，退出面板
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, food_type: str):
        """
        切换当前面板显示的食物类型
        Keyword arguments:
        food_type -- 要切换的食物类型
        """
        self.now_panel = food_type

        if self.now_panel == _("收藏"):
            food_name_list = []
            for fid in cooking.get_favorite_recipe_ids():
                try:
                    recipe = game_config.config_recipes[fid]
                    food_name_list.append((str(fid), recipe.name))
                except Exception:
                    pass
        else:
            food_name_list = cooking.get_filtered_sorted_cook_data(self.now_panel)
            if self.show_favorites_only:
                food_name_list = [x for x in food_name_list if cooking.has_favorites(x[0])]
        # 将调味、烹饪模式、做饭类型增加进去
        food_name_list = [(x[0], x[1], self.special_seasoning, self.cook_mode, self.make_food_type) for x in food_name_list]

        # 同样在这里进行行数填充
        pad_count = 50 - (len(food_name_list) % 50)
        if pad_count == 50 and len(food_name_list) > 0:
            pad_count = 0
        if pad_count > 0:
            food_name_list.extend([("-1", "", self.special_seasoning, self.cook_mode, self.make_food_type)] * pad_count)

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
        cook_mode -- 烹饪模式：0标准，1精细，2大师
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
        if type_id in cache.rhodes_island.makefood_filter_type:
            cache.rhodes_island.makefood_filter_type.remove(type_id)
        else:
            cache.rhodes_island.makefood_filter_type.append(type_id)

    def set_filter_difficulty(self, difficulty: int):
        """设置难度筛选"""
        cache.rhodes_island.makefood_filter_difficulty = difficulty

    def set_filter_time(self, time_level: int):
        """设置时间筛选"""
        cache.rhodes_island.makefood_filter_time = time_level

    def clear_filter(self):
        """清除所有筛选"""
        cache.rhodes_island.makefood_filter_type = []
        cache.rhodes_island.makefood_filter_difficulty = -1
        cache.rhodes_island.makefood_filter_time = -1
        
    def toggle_favorites_only(self):
        """切换普通列表是否只看收藏"""
        self.show_favorites_only = not getattr(self, "show_favorites_only", False)

    def clear_filter_and_sort(self):
        """清除筛选和排序"""
        self.clear_filter()
        cache.rhodes_island.makefood_sort_type = 0
        cache.rhodes_island.makefood_sort_order = 0

    def open_sort_panel(self):
        """
        打开排序设置面板
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
        cache.rhodes_island.makefood_sort_type = sort_type

    def set_sort_order(self, sort_order: int):
        """设置排序顺序"""
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
        self, text: Tuple[str, str, int, int, int], width: int, is_button: bool, num_button: bool, button_id: int,
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
        self.make_food_type = text[4]
        """ 做饭类型：0普通做饭，1泡咖啡，2酒类 """
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
        self.mod_recipe_master: bool = False
        """ 本菜谱大师模式开关（熟练度精通III解锁，仅此菜生效） """
        self._recipe_master_return = None
        """ 本菜谱大师开关按钮的返回值 """

        # 如果是用来占位的空白项，绘制一个固定宽度的空白文本
        if self.cid == "-1":
            self.draw_text = " "
            name_draw = draw.CenterDraw()
            name_draw.text = " "
            name_draw.width = self.width
            self.now_draw = name_draw
            return

        # 延迟创建：此处仅根据菜谱id读取菜谱信息，不创建食物对象
        self.food_cid: str = self.cid
        """ 菜谱id字符串 """
        food_recipe = game_config.config_recipes[int(self.food_cid)]
        self.food_name = food_recipe.name
        food_diffucty = food_recipe.difficulty
        self.make_food_time = food_recipe.time
        if food_recipe.type == 8:
            self.add_coffee = True

        diff_text = _("难度{0}").format(food_diffucty)

        # 按钮绘制 (加上难度等级)
        name_draw = draw.NormalDraw()
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}[{diff_text}] {self.food_name}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.make_food_for_sure
                )
            else:
                button_text = f"[[{diff_text}] {self.food_name}]"
                name_draw = draw.CenterButton(
                    button_text, str(self.text), self.width, cmd_func=self.make_food_for_sure
                )
            self.button_return = name_draw.return_text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[[{diff_text}] {self.food_name}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def make_food_for_sure(self):
        """确认是否制作食物，并选择制作数量（含收藏方案/大师模式/熟练度/帮厨）"""
        from Script.Design import basement
        from Script.Design import handle_premise

        character_data: game_type.Character = cache.character_data[0]
        food_recipe = game_config.config_recipes[int(self.food_cid)]
        food_name = self.food_name
        food_diffucty = food_recipe.difficulty
        seasoning_name = game_config.config_seasoning[self.special_seasoning].name
        facility_adjust = basement.calc_facility_efficiency(5)
        recipe_cid = int(self.food_cid)

        # 预先计算基础品质（熟练度精通I起+1，封顶绝珍）
        base_quality = cooking.get_base_food_quality(0) + cooking.get_prof_quality_bonus(recipe_cid)
        # 如果当前是酒类，且当前地点在酒吧，则品质额外+1
        if food_recipe.type == 3 and handle_premise.handle_in_bar(0):
            base_quality += 1
        base_quality = min(base_quality, cooking.get_max_food_quality())
        # 大师模式：全局模式2 + 技能达标；或本菜谱开关 + 熟练度精通III；或宗师“稳定发挥”特技
        global_master = cooking.is_master_unlocked()
        master_active = (
            (self.cook_mode == 2 and global_master)
            or (getattr(self, "mod_recipe_master", False) and cooking.get_prof_tier(recipe_cid) >= 3)
            or cooking.prof_std_master_active(recipe_cid)
        )
        max_quality = base_quality
        if master_active:
            max_quality = cooking.get_max_food_quality()
        elif self.cook_mode == 1 and cooking.has_cook_question_library(recipe_cid):
            max_quality = min(base_quality + 4, cooking.get_max_food_quality())

        # 预估消耗函数：对齐上游做饭行为链 DOWN_BOTH_MEDIUM（自/交互对象各扣 HP3/分、MP6/分）
        def estimate_cost(total_time):
            hp_cost = int(total_time * 3)
            mp_cost = int(total_time * 6)
            return hp_cost, mp_cost

        def can_afford(count):
            check_time = int(self.make_food_time * (1 + (count - 1) * 0.1))
            check_time = int(check_time * cooking.get_prof_time_mult(recipe_cid) * cooking.get_helper_time_mult())
            if facility_adjust != 1.0 and check_time > 0:
                check_time = int(check_time / facility_adjust)
            hp_cost, mp_cost = estimate_cost(check_time)
            return hp_cost <= character_data.hit_point - 1 and mp_cost <= character_data.mana_point

        # 计算最大可制作数量（上限99+宗师批量特技；药物调味受库存/庆典3份限制；再受体力气力上限约束）
        max_count = 99 + cooking.get_prof_batch_bonus(recipe_cid)
        if self.special_seasoning > 100:
            consume = 3 if food_recipe.type == cooking.FEAST_TYPE else 1
            max_count = min(max_count, character_data.item[self.special_seasoning] // consume)
        while max_count > 1 and not can_afford(max_count):
            max_count -= 1
        max_count = max(1, max_count)
        # 沿用上次在同类型做饭面板中选择的制作数量，并按本次可制作上限钳制
        remember_count = cache.rhodes_island.makefood_make_count.get(self.make_food_type, 1)
        if not isinstance(remember_count, int) or remember_count < 1:
            remember_count = 1
        make_count = min(remember_count, max_count)

        while 1:
            py_cmd.clr_cmd()
            line_feed.draw()

            # 计算总耗时：基础时间 + 每多一份增加10%，再乘熟练度与帮厨系数，最后按设施效率调整
            base_total_time = int(self.make_food_time * (1 + (make_count - 1) * 0.1))
            base_total_time = int(base_total_time * cooking.get_prof_time_mult(recipe_cid) * cooking.get_helper_time_mult())
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
            # 如果是酒类，则显示酒精程度
            if food_recipe.type == 3:
                alcohol_level = food_recipe.alcohol
                alcohol_name = game_config.config_alcohol_level[alcohol_level].name
                confirm_text += _("酒精程度: {0}\n").format(alcohol_name)
            confirm_text += _("制作数量: {0} （最多 {1}）\n").format(make_count, max_count)
            confirm_text += _("预计耗时: {0} 分钟{1}\n").format(make_food_time, facility_adjust_str)
            confirm_text += _("当前调味: {0}\n").format(seasoning_name)
            hp_cost, mp_cost = estimate_cost(make_food_time)
            cost_str = _("预计消耗: 体力 -{0} / 气力 -{1}").format(hp_cost, mp_cost)
            if character_data.target_character_id != character_data.cid:
                cost_str += _("（交互对象同额）")
            confirm_text += cost_str + _("\n")
            # 帮厨与熟练度信息行
            helpers = cooking.get_helpers()
            if helpers:
                helper_names = "、".join(cache.character_data[h].name for h in helpers)
                confirm_text += _("帮厨: {0}（-{1:.0f}%）\n").format(helper_names, (1 - cooking.get_helper_time_mult()) * 100)
            if cooking.get_prof_count(recipe_cid) > 0 or cooking.get_prof_tier(recipe_cid) > 0:
                confirm_text += cooking.prof_summary_text(recipe_cid) + _("\n")
            
            info_draw = draw.NormalDraw()
            info_draw.text = confirm_text
            info_draw.draw()
            
            # 品质预测绘制（大师模式显示稳定绝珍）
            q_label = draw.NormalDraw()
            q_label.text = _("品质预测: ")
            q_label.draw()
            if master_active:
                draw_q(cooking.get_max_food_quality())
                stable_draw = draw.NormalDraw()
                stable_draw.text = _("（稳定）")
                stable_draw.draw()
            else:
                draw_q(base_quality)
                if max_quality != base_quality:
                    tilde = draw.NormalDraw()
                    tilde.text = "~"
                    tilde.draw()
                    draw_q(max_quality)
            
            intro_draw = draw.NormalDraw()
            intro_draw.text = _("\n介绍    : {0}\n").format(food_recipe.introduce)
            intro_draw.draw()
            
            line_feed.draw()

            # 收藏方案区
            return_list = []
            favorites = cooking.get_recipe_favorites(recipe_cid)
            if favorites:
                fav_title = draw.NormalDraw()
                fav_title.text = _("○收藏方案：\n")
                fav_title.draw()
                mode_names = [_("标准"), _("精细"), _("大师")]
                season_short = {
                    0: _("正常"), 1: _("酸"), 2: _("甜"), 3: _("苦"), 4: _("辣"),
                    11: _("精液巧混"), 12: _("精液直射"),
                    102: _("事后避孕药"), 103: _("媚药"), 105: _("利尿剂"),
                    106: _("持续利尿"), 107: _("安眠药"), 108: _("排卵药"),
                }
                for idx, preset in enumerate(favorites):
                    preset_season = season_short.get(preset["seasoning"], _("调味{0}").format(preset["seasoning"]))
                    preset_mode = mode_names[preset["cook_mode"]] if preset["cook_mode"] in (0, 1, 2) else mode_names[0]
                    btn_text = _("[收藏{0}]{1} / {2} / ×{3}").format(idx + 1, preset_season, preset_mode, preset["make_count"])
                    fav_btn = draw.CenterButton(btn_text, f"feast_fav_{idx}", int(window_width / 3))
                    fav_btn.draw()
                    return_list.append(fav_btn.return_text)
                    if (idx + 1) % 3 == 0:
                        line_feed.draw()
                if len(favorites) % 3 != 0:
                    line_feed.draw()

            # 本菜谱大师开关（全局未解锁但该菜谱熟练度达精通III时出现）
            if not global_master and cooking.get_prof_tier(recipe_cid) >= 3:
                rm_state = _("已开启") if getattr(self, "mod_recipe_master", False) else _("已关闭")
                rm_text = _("[大师模式（本菜谱）] {0}（熟练度精通III解锁，免答题稳定绝珍）").format(rm_state)
                rm_draw = draw.LeftButton(rm_text, "feast_recipe_master", self.width)
                rm_draw.draw()
                return_list.append(rm_draw.return_text)
                self._recipe_master_return = rm_draw.return_text

            # 数量调整按钮
            min_draw = draw.CenterButton(_("[最小]"), _("最小"), int(window_width / 6))
            min_draw.draw()
            return_list.append(min_draw.return_text)
            minus10_draw = draw.CenterButton(_("[-10]"), _("减十"), int(window_width / 6))
            minus10_draw.draw()
            return_list.append(minus10_draw.return_text)
            minus_draw = draw.CenterButton(_("[-1]"), _("减少"), int(window_width / 6))
            minus_draw.draw()
            return_list.append(minus_draw.return_text)
            plus_draw = draw.CenterButton(_("[+1]"), _("增加"), int(window_width / 6))
            plus_draw.draw()
            return_list.append(plus_draw.return_text)
            plus10_draw = draw.CenterButton(_("[+10]"), _("加十"), int(window_width / 6))
            plus10_draw.draw()
            return_list.append(plus10_draw.return_text)
            max_draw = draw.CenterButton(_("[最大]"), _("最大"), int(window_width / 6))
            max_draw.draw()
            return_list.append(max_draw.return_text)
            line_feed.draw()

            # 收藏当前方案/取消当前收藏
            save_fav_btn = draw.CenterButton(_("[收藏当前方案]"), "feast_fav_save", int(window_width / 2))
            save_fav_btn.draw()
            return_list.append(save_fav_btn.return_text)
            current_fav_idx = cooking.find_favorite_index(recipe_cid, self.special_seasoning, self.cook_mode, make_count)
            if current_fav_idx >= 0:
                del_fav_btn = draw.CenterButton(_("[取消当前收藏]"), "feast_fav_delete", int(window_width / 2))
                del_fav_btn.draw()
                return_list.append(del_fav_btn.return_text)
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
            if yrn == minus10_draw.return_text:
                make_count = max(1, make_count - 10)
            elif yrn == minus_draw.return_text:
                make_count = max(1, make_count - 1)
            elif yrn == min_draw.return_text:
                make_count = 1
            elif yrn == plus_draw.return_text:
                make_count = min(max_count, make_count + 1)
            elif yrn == plus10_draw.return_text:
                make_count = min(max_count, make_count + 10)
            elif yrn == max_draw.return_text:
                make_count = max_count
            elif self._recipe_master_return is not None and yrn == self._recipe_master_return:
                self.mod_recipe_master = not getattr(self, "mod_recipe_master", False)
            elif yrn == "feast_fav_save":
                result = cooking.save_favorite(recipe_cid, make_count, self.cook_mode, self.special_seasoning)
                info_text = {
                    "added": _("已收藏当前方案\n"),
                    "updated": _("已更新当前收藏方案\n"),
                    "per_recipe_limit": _("该菜谱收藏方案已达上限\n"),
                    "total_limit": _("总收藏方案已达上限\n"),
                    "invalid": _("无法收藏该菜谱\n"),
                }.get(result, _("\n"))
                py_cmd.clr_cmd()
                line_feed.draw()
                info_draw = draw.NormalDraw()
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()
                continue
            elif yrn == "feast_fav_delete":
                if current_fav_idx >= 0:
                    cooking.remove_favorite(recipe_cid, current_fav_idx)
                continue
            elif yrn.startswith("feast_fav_"):
                try:
                    idx = int(yrn.split("_")[-1])
                    preset = favorites[idx]
                    self.special_seasoning = preset["seasoning"]
                    self.cook_mode = preset["cook_mode"]
                    make_count = preset["make_count"]
                except Exception:
                    pass
                continue
            elif yrn == confirm_draw.return_text:
                # 记忆本次的制作数量，供下次打开同类型做饭面板时沿用
                cache.rhodes_island.makefood_make_count[self.make_food_type] = make_count
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
        recipe_cid = int(self.food_cid)

        # 计算食物品质：基础品质为玩家料理技能，封顶到美味
        base_quality = cooking.get_base_food_quality(0) + cooking.get_prof_quality_bonus(recipe_cid)
        # 如果当前是酒类，且当前地点在酒吧，则品质额外+1
        if food_recipe.type == 3 and handle_premise.handle_in_bar(0):
            base_quality += 1
        base_quality = min(base_quality, cooking.get_max_food_quality())
        food_quality = base_quality
        # 大师模式（全局模式2/本菜谱开关/宗师稳定发挥）：免答题稳定绝珍
        global_master = cooking.is_master_unlocked()
        master_active = (
            (self.cook_mode == 2 and global_master)
            or (getattr(self, "mod_recipe_master", False) and cooking.get_prof_tier(recipe_cid) >= 3)
            or cooking.prof_std_master_active(recipe_cid)
        )
        if master_active:
            food_quality = cooking.get_max_food_quality()
        # 精细模式且存在题库时，进入答题流程（特殊调味会替换对应阶段的问题），答对可提升品质（封顶绝珍）
        elif (
            self.cook_mode == 1
            and cooking.has_cook_question_library(recipe_cid)
        ):
            food_quality = cook_question_panel.run_cook_question_flow(
                recipe_cid, base_quality, self.special_seasoning
            )

        # 按数量逐个创建食物对象（延迟创建：仅在制作时才创建对应菜谱的食物对象）
        drug_consume = 3 if food_recipe.type == cooking.FEAST_TYPE else 1
        real_count = 0
        for _i in range(make_count):
            # 药物调味则每份扣除对应数量的药物，库存不足时停止制作
            if self.special_seasoning > 100:
                if character_data.item[self.special_seasoning] < drug_consume:
                    break
                character_data.item[self.special_seasoning] -= drug_consume
            # 精液调味则每份扣除一次精液量，库存不足时停止制作
            if self.special_seasoning in {11, 12}:
                semen_text, semen_count = ejaculation_panel.common_ejaculation()
                if semen_count <= 0:
                    break
            # 创建食物对象并赋予名字、作者、品质、味道
            new_food = cooking.create_food("", recipe_cid, food_quality, character_data.name)
            new_food.special_seasoning = self.special_seasoning
            if self.special_seasoning in {11, 12}:
                new_food.special_seasoning_amount = semen_count
            # 放到玩家背包里
            character_data.food_bag[new_food.uid] = new_food
            character_data.behavior.target_food = new_food
            # 成就计数
            cache.achievement.make_food_count += 1
            real_count += 1

        # 如果实际制作数量为0，则不进行后续处理并输出提示信息
        if real_count <= 0:
            py_cmd.clr_cmd()
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = _("制作失败：没有足够的调味材料或精液量！\n")
            info_draw.draw()
            line_feed.draw()
            return
        # 如果实际制作数量小于请求数量，则输出提示信息
        elif real_count < make_count:
            py_cmd.clr_cmd()
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = _("因为调味材料或精液量不足，实际制作数量为 {0} 个\n").format(real_count)
            info_draw.draw()
            line_feed.draw()

        # 累计熟练度
        cooking.add_proficiency(recipe_cid, real_count)

        # 烹饪行为
        character_data.behavior.make_food_time = new_make_food_time
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