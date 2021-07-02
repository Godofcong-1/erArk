from typing import Set, Tuple
from types import FunctionType
from uuid import UUID
from Script.Core import get_text, game_type, cache_control, constant, flow_handle, text_handle
from Script.UI.Moudle import panel, draw
from Script.Design import cooking, update
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
        self.now_panel = _("主食")
        """ 当前绘制的食物类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("食物背包"), self.width)
        food_type_list = [_("主食")]
        # food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        food_id_list = list(
            cooking.get_character_food_bag_type_list_buy_food_type(0, self.now_panel).items()
        )
        self.handle_panel = panel.PageHandlePanel(
            food_id_list, SeeFoodListByFoodNameDraw, 10, 1, window_width, 1, 1, 0
        )
        while 1:
            if cache.now_panel_id != constant.Panel.FOOD_BAG:
                break
            self.handle_panel.update()
            title_draw.draw()
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
            line = draw.LineDraw("+", self.width)
            line.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
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
        food_id_list = list(
            cooking.get_character_food_bag_type_list_buy_food_type(0, self.now_panel).items()
        )
        self.handle_panel = panel.PageHandlePanel(
            food_id_list, SeeFoodListByFoodNameDraw, 10, 5, window_width, 1, 1, 0
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
        self, text: Tuple[str, Set], width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.text = text[0]
        """ 食物名字 """
        self.uid_list: list = list(text[1])
        """ 背包内指定名字的食物集合 """
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
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}{self.text}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.see_food_shop_food_list
                )
            else:
                button_text = f"[{self.text}]"
                name_draw = draw.CenterButton(
                    button_text, self.text, self.width, cmd_func=self.see_food_shop_food_list
                )
                self.button_return = text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{self.text}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_food_shop_food_list(self):
        """按食物名字显示食物商店的食物列表"""
        title_draw = draw.TitleLineDraw(self.text, window_width)
        page_handle = panel.PageHandlePanel(
            self.uid_list, EatFoodByFoodNameDraw, 10, 1, window_width, 1, 1, 0
        )
        # while 1:
        #     if cache.now_panel_id != constant.Panel.FOOD_BAG:
        #         break
        return_list = []
        title_draw.draw()
        page_handle.update()
        page_handle.draw()
        return_list.extend(page_handle.return_list)
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        back_draw.draw()
        return_list.append(back_draw.return_text)
        yrn = flow_handle.askfor_all(return_list)
            # if yrn == back_draw.return_text:
            #     break


class EatFoodByFoodNameDraw:
    """
    点击后可食用食物的食物名字按钮对象
    Keyword arguments:
    text -- 食物id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(self, text: UUID, width: int, is_button: bool, num_button: bool, button_id: int):
        self.text: UUID = text
        """ 食物id """
        self.draw_text: str = ""
        """ 食物名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = str(button_id)
        """ 按钮返回值 """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        name_draw = draw.NormalDraw()
        food_data: game_type.Food = cache.character_data[0].food_bag[self.text]
        # quality_text_data = [_("垃圾"), _("饲料"), _("粮食"), _("美味"), _("春药")]
        food_name = ""
        if food_data.recipe != -1:
            food_recipe: game_type.Recipes = cache.recipe_data[food_data.recipe]
            food_name = food_recipe.name
        # else:
        #     food_config = game_config.config_food[food_data.id]
        #     food_name = food_config.name
        # hunger_text = _("热量:")
        # if 27 in food_data.feel:
        #     hunger_text = f"{hunger_text}{round(food_data.feel[27],2)}"
        # else:
        #     hunger_text = f"{hunger_text}0.00"
        # thirsty_text = _("水份:")
        # if 28 in food_data.feel:
        #     thirsty_text = f"{thirsty_text}{round(food_data.feel[28],2)}"
        # else:
        #     thirsty_text = f"{thirsty_text}0.00"
        # food_name = (
        #     food_name
        #     + f" {hunger_text} {thirsty_text} "
        #     + _("重量:")
        #     + str(round(food_data.weight, 2))
        #     + _("克")
        #     + " "
        #     + _("品质:")
        #     + quality_text_data[food_data.quality]
        # )
        index_text = text_handle.id_index(button_id)
        button_text = f"{index_text}{food_name}"
        name_draw = draw.LeftButton(button_text, self.button_return, self.width, cmd_func=self.eat_food)
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def eat_food(self):
        """食用食物"""
        update.game_update_flow(0)
        character_data: game_type.Character = cache.character_data[0]
        now_food = character_data.food_bag[self.text]
        character_data.behavior.behavior_id = constant.Behavior.EAT
        character_data.behavior.eat_food = now_food
        character_data.behavior.duration = 1
        character_data.state = constant.CharacterStatus.STATUS_EAT
        update.game_update_flow(1)
        cache.now_panel_id = constant.Panel.IN_SCENE
