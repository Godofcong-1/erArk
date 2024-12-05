from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, cooking, update
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.UI.Panel import ejaculation_panel

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
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板make_food_type """
        self.make_food_type = make_food_type
        """ 0普通做饭，1泡咖啡 """
        self.special_seasoning = 0
        """ 调味类型 """

    def draw(self):
        """绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        title_draw = draw.TitleLineDraw(_("制作食物"), self.width)
        food_type_list = [_("主食"), _("零食")]
        if self.make_food_type == 1:
            food_type_list = [_("咖啡")]
            self.now_panel = _("咖啡")
        # food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        self.handle_panel = panel.PageHandlePanel([], SeeFoodListByFoodNameDraw, 50, 5, self.width, 1, 1, 0)
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

            # 加料说明
            now_seasoning_name = game_config.config_seasoning[self.special_seasoning].name
            now_draw = draw.NormalDraw()
            now_draw.text = _("○当前的调味： {0}").format(now_seasoning_name)
            now_draw.width = 1
            now_draw.draw()

            # 加料面板
            for seasoning_cid in game_config.config_seasoning:
                # 如果泡加料咖啡则跳过普通味道
                if self.now_panel == _("咖啡") and seasoning_cid <= 10:
                    continue
                if seasoning_cid == 0:
                    button_width = self.width/16
                    now_draw = draw.NormalDraw()
                    now_draw.text = _("\n  基础:    ")
                    now_draw.width = 1
                    now_draw.draw()
                # 精液或下药则换行并加长文本宽度
                if seasoning_cid == 11:
                    button_width = self.width/4
                    now_draw = draw.NormalDraw()
                    now_draw.text = _("\n  精液:    ")
                    now_draw.width = 1
                    now_draw.draw()
                elif seasoning_cid == 102:
                    button_width = self.width/8
                    now_draw = draw.NormalDraw()
                    now_draw.text = _("\n  药物:    ")
                    now_draw.width = 1
                    now_draw.draw()
                # 如果是加药物需要已拥有药物
                if seasoning_cid > 100:
                    if not character_data.item[seasoning_cid] and not cache.debug_mode:
                        continue

                button_text = f"[{game_config.config_seasoning[seasoning_cid].name}]"
                button_draw = draw.LeftButton(
                    _(button_text),
                    _(button_text),
                    button_width,
                    cmd_func=self.choice_seasoning,
                    args=(seasoning_cid,),
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()
            line_feed.draw()
            line_feed.draw()


            # 食物面板
            now_draw = draw.NormalDraw()
            now_draw.text = _("○选择要制作的食物：\n")
            now_draw.width = 1
            now_draw.draw()
            food_name_list = list(
                cooking.get_cook_level_food_type(self.now_panel).items()
            )
            # 将调味增加进去
            food_name_list = [(x[0], x[1], self.special_seasoning) for x in food_name_list]
            
            self.handle_panel.text_list = food_name_list
            self.handle_panel.update()
            self.handle_panel.draw()


            return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text or yrn in self.handle_panel.return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, food_type: str):
        """
        切换当前面板显示的食物类型
        Keyword arguments:
        food_type -- 要切换的食物类型
        """
        self.now_panel = food_type

        food_name_list = list(
            cooking.get_cook_level_food_type(self.now_panel).items()
        )
        # 将调味增加进去
        food_name_list = [(x[0], x[1], self.special_seasoning) for x in food_name_list]

        self.handle_panel = panel.PageHandlePanel(
            food_name_list, SeeFoodListByFoodNameDraw, 50, 5, self.width, 1, 1, 0
        )

    def choice_seasoning(self, seasoning_cid):
        """选择味道"""
        self.special_seasoning = seasoning_cid


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
        self, text: Tuple[str, UUID, int], width: int, is_button: bool, num_button: bool, button_id: int,
    ):
        """初始化绘制对象"""
        self.cid: str = text[0]
        """ 食物商店索引id """
        self.text: UUID = text[1]
        """ 食物uid """
        self.special_seasoning = text[2]
        """ 调味类型 """
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
        # self.draw_effect_draw = draw.NormalDraw()
        # """ 做饭效果绘制 """
        self.food_name: str = ""
        """ 食物名字 """
        # food_data: game_type.Food = cache.restaurant_data[str(self.cid)][self.text]
        # draw_effect_text = ""

        # print("debug self.text :",self.text)
        # print("debug self.cid :",self.text)

        # 转换为正确格式
        now_food_list = [(self.cid, x) for x in cache.rhodes_island.makefood_data[self.cid]]
        # print("debug now_food_list = ",now_food_list)
        self.food_cid: str = now_food_list[0][0]
        """ 食物商店索引id """
        self.food_uid: UUID = now_food_list[0][1]
        """ 食物uid """

        if isinstance(self.food_cid, str):
            food_recipe: game_type.Recipes = cache.recipe_data[int(self.food_cid)]
            self.food_name = food_recipe.name
            self.make_food_time = food_recipe.time
            # draw_effect_text += "制作用时" + self.make_food_time + "分钟\n"

        # print("index_text :",index_text)
        # print("debug self.make_food_time :",self.make_food_time)

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
                    button_text, self.text, self.width, cmd_func=self.make_food_for_sure
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
        """确认是否制作食物"""

        line_feed.draw()

        food_recipe = cache.recipe_data[int(self.food_cid)]
        food_name = self.food_name
        food_diffucty = food_recipe.difficulty
        make_food_time = self.make_food_time
        seasoning_name = game_config.config_seasoning[self.special_seasoning].name

        # 输出食物的名字、预计制作耗时、介绍、调味，询问是否确认
        confirm_text = _(
            f"食物名字: {food_name}\n"
            f"菜谱难度: {food_diffucty}\n"
            f"预计耗时: {make_food_time} 分钟\n"
            f"当前调味: {seasoning_name}\n"
            "是否确认制作该食物？"
        )

        info_draw = draw.NormalDraw()
        info_draw.text = confirm_text
        info_draw.draw()
        line_feed.draw()
        line_feed.draw()

        confirm_draw = draw.CenterButton(_("[确认]"), _("确认"), window_width / 2)
        confirm_draw.draw()
        cancel_draw = draw.CenterButton(_("[取消]"), _("取消"), window_width / 2)
        cancel_draw.draw()
        line_feed.draw()

        # 确认则制作食物
        yrn = flow_handle.askfor_all([confirm_draw.return_text, cancel_draw.return_text])
        if yrn == confirm_draw.return_text:
            self.make_food()


    def make_food(self):
        """玩家制作食物"""
        character_data: game_type.Character = cache.character_data[0]
        # 赋予名字、作者和味道
        cache.rhodes_island.makefood_data[self.food_cid][self.food_uid].name = self.food_name
        cache.rhodes_island.makefood_data[self.food_cid][self.food_uid].maker = character_data.name
        cache.rhodes_island.makefood_data[self.food_cid][self.food_uid].special_seasoning = self.special_seasoning
        cache.rhodes_island.makefood_data[self.food_cid][self.food_uid].quality = character_data.ability[43]
        # 药物调味则扣除药物
        if self.special_seasoning > 100:
            character_data.item[self.special_seasoning] -= 1
        # 放到玩家背包里
        character_data.food_bag[self.food_uid] = cache.rhodes_island.makefood_data[self.food_cid][self.food_uid]
        # 精液调味则将精液量加到食物数据里
        if self.special_seasoning in {11,12} :
            semen_text, semen_count = ejaculation_panel.common_ejaculation()
            cache.rhodes_island.makefood_data[self.food_cid][self.food_uid].special_seasoning_amount = semen_count
        # 烹饪行为
        character_data.behavior.food_name = self.food_name
        character_data.behavior.make_food_time = self.make_food_time
        character_data.behavior.food_seasoning = self.special_seasoning
        character_data.behavior.behavior_id = constant.Behavior.MAKE_FOOD
        character_data.behavior.duration = self.make_food_time
        character_data.state = constant.CharacterStatus.STATUS_MAKE_FOOD
        update.game_update_flow(self.make_food_time)

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

