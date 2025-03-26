from types import FunctionType
from uuid import UUID
from Script.Core import get_text, game_type, cache_control, constant, flow_handle
from Script.UI.Moudle import panel, draw
from Script.Design import cooking, update, attr_calculation, handle_premise
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
        self.handle_panel_normal: panel.PageHandlePanel = None
        """ 正常调味食物列表控制面板 """
        self.handle_panel_special: panel.PageHandlePanel = None
        """ 特殊调味食物列表控制面板 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("食物背包"), self.width)
        food_type_list = [_("当前持有食物")]
        # food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        self.handle_panel_normal = panel.PageHandlePanel(
            [], SeeFoodListByFoodNameDraw, 10, 1, window_width, 1, 0, 0
        )
        self.handle_panel_special = panel.PageHandlePanel(
            [], SeeFoodListByFoodNameDraw, 10, 1, window_width, 1, 0, 0
        )
        while 1:
            character_data: game_type.Character = cache.character_data[0]
            if cache.now_panel_id != constant.Panel.FOOD_BAG:
                break

            # 读取背包食物，并只提取uid列表
            id_list_normal,id_list_special = [],[]
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
                elif food_data.special_seasoning in [11,12] and not hasattr(food_data, "special_seasoning_amount"):
                    del cache.character_data[0].food_bag[i]
                    del_food_flag = True
                    continue
                if food_data.special_seasoning == 0:
                    id_list_normal.append(i)
                else:
                    id_list_special.append(i)

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
                    now_draw.width = self.width / len(food_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{food_type}]",
                        food_type,
                        self.width / len(food_type_list),
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
            now_draw.width = 1
            now_draw.draw()
            line_feed.draw()

            character_data: game_type.Character = cache.character_data[0]
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

            now_draw = draw.NormalDraw()
            now_draw.text = _("○正常调味食物\n")
            if handle_premise.handle_hunger_le_79(0):
                now_draw.text += _("  现在不饿，无法吃东西。\n\n")
            now_draw.width = 1
            now_draw.draw()
            self.handle_panel_normal.draw()
            line_feed.draw()

            now_draw = draw.NormalDraw()
            now_draw.text = _("○特殊调味食物\n")
            if character_data.target_character_id == 0:
                now_draw.text += _("  当前没有目标，无法食用特殊调味食物。\n\n")
            elif handle_premise.handle_hunger_le_79(character_data.target_character_id):
                now_draw.text += _("  {0}现在不饿，无法吃东西。\n\n").format(target_character_data.name)
            now_draw.width = 1
            now_draw.draw()
            self.handle_panel_special.draw()

            return_list.extend(self.handle_panel_normal.return_list)
            return_list.extend(self.handle_panel_special.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list and yrn not in ["0","1"]:
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

        # 读取背包食物，并只提取uid列表
        id_list_normal,id_list_special = [],[]
        for i in character_data.food_bag:
            food_data: game_type.Food = cache.character_data[0].food_bag[i]
            if food_data.special_seasoning == 0:
                id_list_normal.append(i)
            else:
                id_list_special.append(i)

        self.handle_panel_normal.text_list = id_list_normal
        self.handle_panel_normal.update()
        self.handle_panel_special.text_list = id_list_special
        self.handle_panel_special.update()

        self.handle_panel_normal = panel.PageHandlePanel(
            id_list_normal, SeeFoodListByFoodNameDraw, 10, 5, window_width, 1, 0, 0
        )
        self.handle_panel_special = panel.PageHandlePanel(
            id_list_special, SeeFoodListByFoodNameDraw, 10, 5, window_width, 1, 0, 0
        )


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
        self, text: UUID, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.text: UUID = text
        """ 食物id """
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
        name_draw = draw.NormalDraw()
        # print(f"debug self.text = {self.text}")
        food_data: game_type.Food = cache.character_data[0].food_bag[self.text]
        # quality_text_data = [_("垃圾"), _("饲料"), _("粮食"), _("美味"), _("春药")]
        food_name = ""
        if food_data.recipe != -1:
            food_recipe: game_type.Recipes = cache.recipe_data[food_data.recipe]
            food_name = food_recipe.name
            food_introduce = food_recipe.introduce
        food_quality_level, food_quality_str = attr_calculation.get_food_quality(food_data.quality)
        food_quality_str = f"({food_quality_str})"
        # 如果是母乳，则不显示质量，而是显示母乳的ml
        if food_data.milk_ml > 0:
            food_quality_str = ""
            milk_ml = f"({food_data.milk_ml}ml)"
        else:
            milk_ml = ""
        # 如果不是正常调味，则标注味道
        food_seasoning = ""
        if food_data.special_seasoning != 0:
            food_seasoning += f"({game_config.config_seasoning[food_data.special_seasoning].name})"
        
        button_text = f"  {food_name}{food_seasoning}"
        button_text += f"{food_quality_str}"
        button_text += f"{milk_ml}"
        if food_data.maker != "":
            button_text += f"(by {food_data.maker})"
        button_text += f"：{food_introduce}"

        # 判断是否需要绘制按钮
        draw_button_flag = True
        character_data: game_type.Character = cache.character_data[0]
        # 正常调味的情况下
        if food_data.special_seasoning == 0:
            # 自己已经吃饱了则不显示按钮
            if handle_premise.handle_hunger_le_79(0):
                draw_button_flag = False
        else:
            # 特殊调味的情况下，如果没有目标则不显示按钮
            if character_data.target_character_id == 0:
                draw_button_flag = False
            # 如果目标已经吃饱了则不显示按钮
            if handle_premise.handle_hunger_le_79(character_data.target_character_id):
                draw_button_flag = False

        if draw_button_flag:
            # 将uuid的前三位作为按钮的返回值
            return_text = f"\n{food_name}_{str(self.text)[:3]}"
            name_draw = draw.LeftButton(
                button_text, return_text, self.width, cmd_func=self.eat_food
            )
            self.draw_text = button_text
            self.button_return = name_draw.return_text
        else:
            name_draw = draw.LeftDraw()
            name_draw.text = button_text
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def eat_food(self):
        """食用食物"""
        character_data: game_type.Character = cache.character_data[0]
        now_food = character_data.food_bag[self.text]
        character_data.behavior.food_name = now_food.name
        character_data.behavior.food_seasoning = now_food.special_seasoning
        character_data.behavior.food_quality = now_food.quality
        character_data.behavior.target_food = now_food
        character_data.behavior.duration = 5
        character_data.behavior.behavior_id = constant.Behavior.EAT
        character_data.state = constant.CharacterStatus.STATUS_EAT
        # 特殊调味的食物则需要进行食用判定，失败则变为拒绝食用
        if now_food.special_seasoning != 0:
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
        line_feed.draw()
        cache.now_panel_id = constant.Panel.IN_SCENE
        update.game_update_flow(5)
