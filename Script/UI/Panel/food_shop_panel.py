from typing import Tuple
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, cooking, update, attr_calculation
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


def put_selfmade_food_in():
    """
    将自制食物放入食堂
    """
    character_data: game_type.Character = cache.character_data[0]

    # 读取背包食物，并只提取uid列表
    id_list_normal = []
    for i in character_data.food_bag.copy():
        food_data: game_type.Food = character_data.food_bag[i]
        if food_data.special_seasoning == 0:
            id_list_normal.append(i)

    # 绘制提示信息
    if len(id_list_normal):
        info_draw_text = _("{0}开始将身上没有调味的食物放进食堂取餐区里\n").format(character_data.name)
    else:
        info_draw_text = _("{0}身上没有正常调味的食物\n").format(character_data.name)
    info_draw = draw.NormalDraw()
    info_draw.text = info_draw_text
    info_draw.width = window_width
    info_draw.draw()

    # 遍历食物列表，将食物放入食堂
    for uid in id_list_normal:
        food_data = character_data.food_bag[uid]
        recipes_id = str(food_data.recipe)
        food_name = food_data.name
        cache.rhodes_island.dining_hall_data.setdefault(recipes_id, {})
        cache.rhodes_island.dining_hall_data[recipes_id][uid] = cache.character_data[0].food_bag[uid]
        del cache.character_data[0].food_bag[uid]
        # 绘制提示信息
        info_draw = draw.NormalDraw()
        info_draw.text = _("{0}已放入食堂\n").format(food_name)
        info_draw.width = window_width
        info_draw.draw()


class FoodShopPanel:
    """
    用于查看食物商店界面面板对象
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
        scene_position = cache.character_data[0].position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        scene_name = cache.scene_data[scene_position_str].scene_name
        scene_tag = cache.scene_data[scene_position_str].scene_tag
        title_draw = draw.TitleLineDraw(scene_name, self.width)
        food_type_list = [_("当前提供的食物")]
        # food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        self.handle_panel = panel.PageHandlePanel([], SeeFoodListByFoodNameDraw, 30, 5, self.width, 1, 1, 0)
        food_name_list = []

        while 1:
            py_cmd.clr_cmd()

            # 地摊小贩
            if "Stall_Vendor" in scene_tag:
                food_name_list = list(cooking.get_food_list_from_food_shop(self.now_panel, restaurant_id="Stall_Vendor").items())

            # 根据场景标签查找对应的食物商店
            if not len(food_name_list):
                for restaurant_id in game_config.config_restaurant:
                    if game_config.config_restaurant[restaurant_id].tag_name in scene_tag:
                        food_name_list = list(cooking.get_food_list_from_food_shop(self.now_panel, restaurant_id=restaurant_id).items())
                        break
            # 如果都没有找到，则默认为食堂
            if not len(food_name_list):
                food_name_list = list(cooking.get_food_list_from_food_shop(self.now_panel).items())

            self.handle_panel.text_list = food_name_list
            self.handle_panel.update()
            title_draw.draw()
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
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
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
        food_name_list = list(cooking.get_food_list_from_food_shop(self.now_panel).items())
        self.handle_panel = panel.PageHandlePanel(
            food_name_list, SeeFoodListByFoodNameDraw, 10, 5, self.width, 1, 1, 0
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
        self, text: Tuple[str, str], width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.text = text[1]
        """ 食物名字 """
        self.cid = text[0]
        """ 食物在食堂内的表id """
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
        title_draw.draw()
        return_list = []

        scene_position = cache.character_data[0].position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        scene_tag = cache.scene_data[scene_position_str].scene_tag
        now_restaurant_id = None

        # 找到当前场景对应的食物商店
        for restaurant_id in game_config.config_restaurant:
            if game_config.config_restaurant[restaurant_id].tag_name in scene_tag:
                now_restaurant_id = restaurant_id
                break
        if "Stall_Vendor" in scene_tag:
            now_restaurant_id = "Stall_Vendor"

        # 根据食物商店id获取食物列表
        if now_restaurant_id is None:
            now_food_list = [(self.cid, x) for x in cache.rhodes_island.dining_hall_data[self.cid]]
        elif now_restaurant_id == "Stall_Vendor":
            now_food_list = [(self.cid, x) for x in cache.rhodes_island.stall_vendor_data[0][self.cid]]
        else:
            now_food_list = [(self.cid, x) for x in cache.rhodes_island.restaurant_data[now_restaurant_id][self.cid]]

        # 如果食物超过了十个，则只显示十个
        if len(now_food_list) > 10:
            now_food_list = now_food_list[:10]

        while 1:

            for now_cid, now_uid in now_food_list:

                if now_restaurant_id is None:
                    food_data: game_type.Food = cache.rhodes_island.dining_hall_data[now_cid][now_uid]
                elif now_restaurant_id == "Stall_Vendor":
                    food_data: game_type.Food = cache.rhodes_island.stall_vendor_data[0][now_cid][now_uid]
                else:
                    food_data: game_type.Food = cache.rhodes_island.restaurant_data[now_restaurant_id][now_cid][now_uid]
                self.food_name = ""
                if isinstance(now_cid, str):
                    food_recipe: game_type.Recipes = cache.recipe_data[int(now_cid)]
                    self.food_name = food_recipe.name
                    food_money = food_recipe.money
                    food_introduce = food_recipe.introduce
                food_quality_level, food_quality_str = attr_calculation.get_food_quality(food_data.quality)
                button_text = f"[{now_cid}]{self.food_name}"
                button_text += f"({food_quality_str})"
                if food_data.maker != "":
                    button_text += f"(by {food_data.maker})"
                button_text += _("(博士免费)")
                button_text += f"：{food_introduce}"
                button_return = f"{now_cid}_{str(now_uid)[:3]}"
                name_draw = draw.LeftButton(button_text, button_return, window_width, cmd_func=self.buy_food, args=(now_cid, now_uid, now_restaurant_id))
                name_draw.draw()
                return_list.append(name_draw.return_text)
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break
            cache.rhodes_island.dining_hall_data.setdefault(self.cid, {})

    def buy_food(self, cid: str, uid: UUID, restaurant_id: int = None):
        """玩家购买食物"""
        if restaurant_id is None:
            cache.character_data[0].food_bag[uid] = cache.rhodes_island.dining_hall_data[cid][uid]
            del cache.rhodes_island.dining_hall_data[cid][uid]
        elif restaurant_id == "Stall_Vendor":
            cache.character_data[0].food_bag[uid] = cache.rhodes_island.stall_vendor_data[0][cid][uid]
            del cache.rhodes_island.stall_vendor_data[0][cid][uid]
        else:
            cache.character_data[0].food_bag[uid] = cache.rhodes_island.restaurant_data[restaurant_id][cid][uid]
            del cache.rhodes_island.restaurant_data[restaurant_id][cid][uid]
        character_data: game_type.Character = cache.character_data[0]
        character_data.behavior.behavior_id = constant.Behavior.BUY_FOOD
        character_data.state = constant.CharacterStatus.STATUS_BUY_FOOD
        character_data.behavior.food_name = self.food_name
        character_data.behavior.duration = 1
        update.game_update_flow(1)
