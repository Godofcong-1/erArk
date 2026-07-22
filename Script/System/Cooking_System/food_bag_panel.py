from types import FunctionType
from uuid import UUID
from typing import Tuple, List
from Script.Core import get_text, game_type, cache_control, constant, flow_handle
from Script.UI.Moudle import panel, draw
from Script.Design import attr_calculation, handle_premise
from Script.Config import normal_config, game_config

_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class FoodBagPanel:
    """
    用于查看食物背包界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("当前持有食物")
        """ 当前绘制的食物类型 """
        self.handle_panel_normal: panel.PageHandlePanel
        """ 正常调味食物列表控制面板 """
        self.handle_panel_special: panel.PageHandlePanel
        """ 特殊调味食物列表控制面板 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("食物背包"), self.width)
        food_type_list = [_("当前持有食物")]
        # food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        self.handle_panel_normal = panel.PageHandlePanel(
            [], FoodGroupDraw, 10, 1, window_width, True, False, 0
        )
        self.handle_panel_special = panel.PageHandlePanel(
            [], FoodGroupDraw, 10, 1, window_width, True, False, 2
        )
        while 1:
            character_data: game_type.Character = cache.character_data[0]
            if cache.now_panel_id != constant.Panel.FOOD_BAG:
                break

            # 读取背包食物，按(recipe, special_seasoning)分组
            group_normal: dict = {}
            group_special: dict = {}
            del_food_flag = False
            for i in character_data.food_bag.copy():
                food_data: game_type.Food = cache.character_data[0].food_bag[i]
                # 版本更新用修正
                # 如果food_data没有milk_ml属性，则删除该食物
                if not hasattr(food_data, "milk_ml"):
                    del cache.character_data[0].food_bag[i]
                    del_food_flag = True
                    continue
                # 如果food_data是精液调味(调味类型11和12)没有special_seasoning_amount属性，则删除该食物
                elif food_data.special_seasoning in [11, 12] and not hasattr(food_data, "special_seasoning_amount"):
                    del cache.character_data[0].food_bag[i]
                    del_food_flag = True
                    continue
                group_key = (food_data.recipe, food_data.special_seasoning)
                if food_data.special_seasoning == 0:
                    group_normal.setdefault(group_key, [])
                    group_normal[group_key].append(i)
                else:
                    group_special.setdefault(group_key, [])
                    group_special[group_key].append(i)

            id_list_normal = list(group_normal.items())
            id_list_special = list(group_special.items())

            self.handle_panel_normal.text_list = id_list_normal
            self.handle_panel_normal.update()
            self.handle_panel_special.text_list = id_list_special
            self.handle_panel_special.update()
            title_draw.draw()

            # 输出删除食物的提示信息
            if del_food_flag:
                del_food_draw = draw.LeftDraw()
                del_food_draw.text = _("\n检测到因版本变更导致的食物数据异常，已删除部分异常食物，并重置了部分食物的数据，请保存并覆盖原存档。\n")
                del_food_draw.draw()
                line_feed.draw()

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
            now_draw = draw.NormalDraw()
            now_draw.text = _("◆普通食物在场景无人时为独自食用，有人时则与目标一起分享，特殊调味食物仅可让目标食用。\n")
            now_draw.draw()
            line_feed.draw()

            character_data: game_type.Character = cache.character_data[0]
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

            now_draw = draw.NormalDraw()
            now_draw.text = _("○正常调味食物（共 {0} 种，{1} 个）\n").format(
                len(id_list_normal), sum(len(v) for v in group_normal.values())
            )
            if handle_premise.handle_have_no_target(0) and handle_premise.handle_hunger_le_79(0):
                now_draw.text += _("  {0}现在不饿，无法吃东西。\n\n").format(character_data.name)
            elif handle_premise.handle_have_target(0):
                if handle_premise.handle_hunger_le_79(character_data.target_character_id):
                    now_draw.text += _("  {0}现在不饿，无法吃东西。\n\n").format(target_character_data.name)
                elif not handle_premise.handle_t_normal_6(0):
                    now_draw.text += _("  {0}现在意识不清醒，无法吃东西。\n\n").format(target_character_data.name)
            now_draw.draw()
            self.handle_panel_normal.draw()
            line_feed.draw()

            now_draw = draw.NormalDraw()
            now_draw.text = _("○特殊调味食物（共 {0} 种，{1} 个）\n").format(
                len(id_list_special), sum(len(v) for v in group_special.values())
            )
            if handle_premise.handle_have_no_target(0):
                now_draw.text += _("  当前没有目标，无法食用特殊调味食物。\n\n")
            elif handle_premise.handle_have_target(0) and handle_premise.handle_hunger_le_79(character_data.target_character_id):
                now_draw.text += _("  {0}现在不饿，无法吃东西。\n\n").format(target_character_data.name)
            now_draw.draw()
            self.handle_panel_special.draw()

            return_list.extend(self.handle_panel_normal.return_list)
            return_list.extend(self.handle_panel_special.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, food_type: str):
        """
        切换当前面板显示的食物类型
        Keyword arguments:
        food_type -- 要切换的食物类型
        """
        self.now_panel = food_type
        character_data: game_type.Character = cache.character_data[0]

        # 按(recipe, special_seasoning)分组
        group_normal: dict = {}
        group_special: dict = {}
        for i in character_data.food_bag:
            food_data: game_type.Food = cache.character_data[0].food_bag[i]
            group_key = (food_data.recipe, food_data.special_seasoning)
            if food_data.special_seasoning == 0:
                group_normal.setdefault(group_key, [])
                group_normal[group_key].append(i)
            else:
                group_special.setdefault(group_key, [])
                group_special[group_key].append(i)

        id_list_normal = list(group_normal.items())
        id_list_special = list(group_special.items())

        self.handle_panel_normal = panel.PageHandlePanel(
            id_list_normal, FoodGroupDraw, 10, 5, window_width, True, False, 0
        )
        self.handle_panel_special = panel.PageHandlePanel(
            id_list_special, FoodGroupDraw, 10, 5, window_width, True, False, 2
        )


class FoodGroupDraw:
    """
    食物分组按钮对象，外部显示食物名称、数量和最高品质，点击后展开该组的所有食物供选择
    Keyword arguments:
    text -- ((recipe_id, special_seasoning), [uid_list]) 分组键和uid列表
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: Tuple, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        group_key, uid_list = text
        recipe_id, special_seasoning = group_key

        self.uid_list: List[UUID] = uid_list
        """ 该分组下的食物uid列表 """
        self.draw_text: str = ""
        """ 绘制文本，供面板对齐处理使用 """
        self.width: int = width
        """ 最大宽度 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        self.food_name: str = ""
        """ 食物名称 """
        self.food_introduce: str = ""
        """ 食物介绍 """
        self.special_seasoning: int = special_seasoning
        """ 特殊调味类型 """

        # 获取食物名称和介绍
        if recipe_id != -1 and recipe_id in cache.recipe_data:
            food_recipe: game_type.Recipes = cache.recipe_data[recipe_id]
            self.food_name = food_recipe.name
            self.food_introduce = food_recipe.introduce

        # 特殊调味名称
        seasoning_str = ""
        if special_seasoning != 0 and special_seasoning in game_config.config_seasoning:
            seasoning_str = f"({game_config.config_seasoning[special_seasoning].name})"

        # 遍历计算最高品质和是否有制作者
        max_quality = 0
        has_maker = False
        for uid in uid_list:
            if uid in cache.character_data[0].food_bag:
                food_data: game_type.Food = cache.character_data[0].food_bag[uid]
                if food_data.quality > max_quality:
                    max_quality = food_data.quality
                if food_data.maker != "":
                    has_maker = True

        _quality_level, quality_str = attr_calculation.get_food_quality(max_quality)
        count = len(uid_list)
        quality_text = _("(最高品质：{quality_str})").format(quality_str=quality_str) if max_quality > 0 else ""
        # 食谱等级
        recipe_difficulty = 0
        recipe_difficulty_str = ""
        if recipe_id != -1 and recipe_id in cache.recipe_data:
            recipe_difficulty = cache.recipe_data[recipe_id].difficulty
            # 食谱等级大于8的按0级显示
            if recipe_difficulty > 8:
                recipe_difficulty = 0
            recipe_difficulty_str = _("(食谱等级：{recipe_difficulty})").format(recipe_difficulty=recipe_difficulty)

        button_text = f"  {self.food_name}{seasoning_str} {recipe_difficulty_str} {quality_text} x{count}"

        # 判断是否可以点击（与原食用条件保持一致）
        draw_button_flag = True
        character_data: game_type.Character = cache.character_data[0]
        if special_seasoning == 0:
            if handle_premise.handle_have_no_target(0) and handle_premise.handle_hunger_le_79(0):
                draw_button_flag = False
            elif handle_premise.handle_have_target(0):
                if handle_premise.handle_hunger_le_79(character_data.target_character_id):
                    draw_button_flag = False
                elif not handle_premise.handle_t_normal_6(0):
                    draw_button_flag = False
        else:
            if handle_premise.handle_have_no_target(0):
                draw_button_flag = False
            elif handle_premise.handle_have_target(0) and handle_premise.handle_hunger_le_79(character_data.target_character_id):
                draw_button_flag = False

        if draw_button_flag:
            return_text = f"\ngroup_{self.food_name}_{str(uid_list[0])[:3]}"
            name_draw = draw.LeftButton(button_text, return_text, self.width, cmd_func=self.see_food_group_list)
            self.button_return = name_draw.return_text
        else:
            name_draw = draw.LeftDraw()
            name_draw.text = button_text
            name_draw.width = self.width

        self.draw_text = button_text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_food_group_list(self):
        """展开显示该分组下的所有食物，供玩家选择食用"""
        title_draw = draw.TitleLineDraw(self.food_name, window_width)

        intro_draw = draw.NormalDraw()
        if self.food_introduce:
            intro_draw.text = f"{self.food_name}：{self.food_introduce}\n\n"
            intro_draw.width = window_width

        while 1:
            title_draw.draw()
            if self.food_introduce:
                intro_draw.draw()

            return_list = []
            character_data: game_type.Character = cache.character_data[0]
            valid_uids = [uid for uid in self.uid_list if uid in character_data.food_bag]

            for uid in valid_uids:
                food_data: game_type.Food = character_data.food_bag[uid]
                _quality_level, food_quality_str = attr_calculation.get_food_quality(food_data.quality)

                # 构建单个食物的显示文本
                item_text = f"  {self.food_name}"
                if food_data.milk_ml > 0:
                    item_text += f"({food_data.milk_ml}ml)"
                else:
                    item_text += f"({food_quality_str})"
                if food_data.maker != "":
                    item_text += f" (by {food_data.maker})"
                if self.special_seasoning != 0 and self.special_seasoning in game_config.config_seasoning:
                    item_text += f"({game_config.config_seasoning[self.special_seasoning].name})"
                item_text += f"：{self.food_introduce}"

                button_return = f"\neat_{self.food_name}_{str(uid)[:3]}"
                food_btn = draw.LeftButton(item_text, button_return, window_width, cmd_func=self.eat_food, args=(uid,))
                food_btn.draw()
                return_list.append(food_btn.return_text)
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def eat_food(self, uid: UUID):
        """食用指定uid的食物"""
        from Script.System.Cooking_System import cooking
        from Script.UI.Panel import achievement_panel
        from Script.Design import update
        from Script.System.Sex_System import drunk_sex_common
        character_data: game_type.Character = cache.character_data[0]
        now_food: game_type.Food = character_data.food_bag[uid]
        character_data.behavior.target_food = now_food
        character_data.behavior.duration = 5
        character_data.behavior.behavior_id = constant.Behavior.EAT
        character_data.state = constant.CharacterStatus.STATUS_EAT
        # 酒类判定，位于特殊调味判定之前，判定失败则变为拒绝饮酒
        if not drunk_sex_common.judge_accept_alcohol_food(character_data.target_character_id, now_food):
            character_data.behavior.behavior_id = constant.Behavior.REFUSE_DRINK
            character_data.state = constant.CharacterStatus.STATUS_REFUSE_DRINK
        # 特殊调味的食物则需要进行食用判定，失败则变为拒绝食用
        elif now_food.special_seasoning != 0:
            if not cooking.judge_accept_special_seasoning_food(character_data.target_character_id):
                # 味道调味则仅生气
                if now_food.special_seasoning in [1, 2, 3, 4]:
                    character_data.angry_point += 40
                    character_data.sp_flag.angry_with_player = True
                # 检测是否满足高级性骚扰的实行值需求
                elif handle_premise.handle_instruct_judge_high_obscenity(0):
                    character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
                    character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
                else:
                    character_data.behavior.behavior_id = constant.Behavior.REFUSE_EAT
                    character_data.state = constant.CharacterStatus.STATUS_REFUSE_EAT
            # 接受的情况下
            else:
                # 成就结算
                if now_food.special_seasoning in [11, 12] and now_food.special_seasoning_amount > 0:
                    achievement_panel.achievement_flow(_("进食"), 1076)

        line_feed.draw()
        cache.now_panel_id = constant.Panel.IN_SCENE
        update.game_update_flow(5)
