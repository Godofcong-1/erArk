from types import FunctionType
from Script.Core import cache_control, game_type, text_handle, get_text, flow_handle, py_cmd, constant
from Script.Design import map_handle
from Script.Config import game_config, normal_config
from Script.UI.Moudle import panel, draw
from Script.UI.Panel import see_item_info_panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

body_item_list = [_("乳头夹"),_("阴蒂夹"),_("V震动棒"),_("A震动棒"),_("搾乳机"),_("采尿器"),_("眼罩"),_("肛门拉珠"),_("持续性利尿剂"),_("安眠药"),_("排卵促进药"),_("事前避孕药"),_("事后避孕药"),_("避孕套")]

def get_item_id_from_body_item_list(body_item_id : int):
    """根据身体道具序号获取道具id"""
    # 对应的id字典
    item_id_dict = {
        0 : 122,
        1 : 123,
        2 : 125,
        3 : 125,
        4 : 133,
        5 : 134,
        6 : 132,
        7 : 129,
        8 : 106,
        9 : 107,
        10 : 108,
        11 : 101,
        12 : 102,
        13 : 120,
    }
    if body_item_id in item_id_dict:
        return item_id_dict[body_item_id]
    return -1

class HItemShopPanel:
    """
    用于查看成人用品商店界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """

    def draw(self):
        """绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        scene_position = character_data.position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        # scene_name = cache.scene_data[scene_position_str].scene_name
        title_draw = draw.TitleLineDraw(_("成人用品商店"), self.width)
        now_level = cache.rhodes_island.facility_level[11] # 获取设施等级

        # 按类别统计全部道具
        item_list_all = []
        item_list_Drug = []
        item_list_Machine = []
        item_list_Consumables = []
        item_list_H_Drug = []
        item_list_H_Machine = []
        item_list_SM = []
        item_list_type = [_("药品"),_("机器"),_("消耗品"),_("H药品"),_("H用机器"),_("SM器具")]
        item_list = [i for i in game_config.config_item]
        for i in item_list:
            # 跳过等级高于设施等级的道具
            if game_config.config_item[i].level > now_level:
                continue
            if game_config.config_item[i].type == "Drug":
                item_list_Drug.append(i)
            elif game_config.config_item[i].type == "Machine":
                item_list_Machine.append(i)
            elif game_config.config_item[i].type == "Consumables":
                item_list_Consumables.append(i)
            elif game_config.config_item[i].type == "H_Drug":
                item_list_H_Drug.append(i)
            elif game_config.config_item[i].type == "H_Machine":
                item_list_H_Machine.append(i)
            elif game_config.config_item[i].type == "SM":
                item_list_SM.append(i)
        item_list_all.append(item_list_Drug)
        item_list_all.append(item_list_Machine)
        item_list_all.append(item_list_Consumables)
        item_list_all.append(item_list_H_Drug)
        item_list_all.append(item_list_H_Machine)
        item_list_all.append(item_list_SM)

        handle_panel = panel.PageHandlePanel([], BuyItemByItemNameDraw, 50, 3, self.width, 1, 1, 0)

        while 1:
            return_list = []
            title_draw.draw()

            # 显示等级的提示信息
            level_text = _("当前设施等级：{0}，提升设施等级可解锁更多道具").format(now_level)
            level_draw = draw.NormalDraw()
            level_draw.text = level_text
            level_draw.width = self.width
            level_draw.draw()
            line_feed.draw()

            # 绘制粉色凭证
            money_text = _("当前持有粉色凭证：{0}").format(str(cache.rhodes_island.materials_resouce[4]))
            now_draw = draw.NormalDraw()
            now_draw.text = money_text
            now_draw.width = self.width
            now_draw.draw()
            line_feed.draw()
            line_feed.draw()

            # 商店里显示全部道具
            # item_list = [i for i in game_config.config_item if i not in character_data.item]

            # 遍历输出每个类型的面板
            for i in range(len(item_list_all)):
                # 输出类别文字
                type_text = f"————{item_list_type[i]}————"
                now_draw = draw.NormalDraw()
                now_draw.text = type_text
                now_draw.width = self.width
                now_draw.draw()
                line_feed.draw()

                # 输出面板
                handle_panel.text_list = item_list_all[i]
                handle_panel.update()
                handle_panel.draw()

            # 将道具列表输入可返回列表中
            for i in item_list:
                return_list.append(str(i))
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


class BuyItemByItemNameDraw:
    """
    点击后可购买道具的道具名字按钮对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(self, text: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text = text
        """ 道具id """
        self.draw_text: str = ""
        """ 道具名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(text)
        """ 按钮返回值 """
        self.character_data: game_type.Character = cache.character_data[0]
        """ 人物属性 """
        self.now_draw = draw.NormalDraw()
        item_config = game_config.config_item[self.text]
        index_text = text_handle.id_index(button_id)
        # print("debug self.text = ",self.text,"  self.character_data.item, = ",self.character_data.item)
        # print("debug self.text in self.character_data.item",self.text in self.character_data.item)

        # 判断是否是消耗品、是否已达99个堆叠上限，是否已拥有
        flag_consumables = item_config.type in ["Drug","H_Drug","Consumables"]
        flag_not_max = self.character_data.item[self.text] < 99
        flag_have = self.character_data.item[self.text] > 0

        # print("debug flag_consumables = ",flag_consumables,"  flag_not_max = ",flag_not_max,"  flag_have = ",flag_have)

        # 可购买：1消耗品且数量小于99，2非消耗品且未持有
        if (flag_consumables and flag_not_max) or (not flag_consumables and not flag_have):
            if num_button:
                button_text = f"{index_text}{item_config.name}：{item_config.price}"
                button_text += _("凭证")
                draw_style = "standard"
                if flag_consumables:
                    button_text += _("(持有：") + str(self.character_data.item[self.text]) + ")"
                    if self.character_data.item[self.text] > 0:
                        draw_style = "dark_green"
                else:
                    button_text += _("(未持有)")
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, normal_style = draw_style, cmd_func=self.show_item_info
                )
            self.draw_text = button_text
        else:
            name_draw = draw.LeftDraw()
            name_draw.text = f"{index_text}{item_config.name}：{item_config.price}"
            name_draw.text += _("凭证")
            if flag_consumables:
                name_draw.text += _("(持有：") + str(self.character_data.item[self.text]) + ")"
                if not flag_not_max:
                    name_draw.text += _("(已达上限)")
            else:
                name_draw.text += _("(已持有)")
            name_draw.style = "gold_enrod"
            name_draw.width = self.width
            self.draw_text = name_draw.text

            name_draw.width = self.width
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def show_item_info(self):
        """显示道具信息"""
        line_feed.draw()
        line_draw = draw.LineDraw("-", window_width)
        line_draw.draw()
        now_draw = see_item_info_panel.ItemInfoDraw(self.text, window_width)
        now_draw.draw()
        item_config = game_config.config_item[self.text]
        while 1:
            return_list = []
            line_feed.draw()
            if item_config.type in ["Drug","H_Drug","Consumables"]:
                buy_one_draw = draw.CenterButton(_("[购买一个]"), _("[购买一个]"), window_width / 3, cmd_func=self.buy_item)
                buy_one_draw.draw()
                return_list.append(buy_one_draw.return_text)
                buy_many_draw = draw.CenterButton(_("[购买多个]"), _("[购买多个]"), window_width / 3, cmd_func=self.buy_many)
                buy_many_draw.draw()
                return_list.append(buy_many_draw.return_text)
                return_draw = draw.CenterButton(_("[返回]"), _("[返回]"), window_width / 3)
                return_draw.draw()
                return_list.append(return_draw.return_text)
                line_feed.draw()
            else:
                yes_draw = draw.CenterButton(_("[购买]"), _("[购买]"), window_width / 2, cmd_func=self.buy_item)
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
                return_draw = draw.CenterButton(_("[返回]"), _("[返回]"), window_width / 2)
                return_draw.draw()
                return_list.append(return_draw.return_text)
                line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def buy_many(self):
        """购买多个道具"""
        while True:
            line_feed.draw()
            ask_number_panel = panel.AskForOneMessage()
            ask_number_panel.set(_("请输入要购买多少个"), 10)
            now_number = ask_number_panel.draw()
            # 如果可以的话，将输入的文本转换为数字
            try:
                now_number = int(now_number)
            except ValueError:
                now_number = 0

            # 检查 now_number 是否为大于0的正整数
            if isinstance(now_number, int) and now_number > 0:
                now_number = min(now_number, 99 - self.character_data.item[self.text])
                break
            else:
                info_draw = draw.LeftDraw()
                info_draw.text = _("请输入一个大于0的正整数")
                info_draw.width = window_width
                info_draw.draw()
        self.buy_item(now_number)

    def buy_item(self, number: int = 1):
        """购买道具"""
        from Script.UI.Panel import achievement_panel
        py_cmd.clr_cmd()
        line = draw.LineDraw("-", window_width)
        line.draw()
        item_config = game_config.config_item[self.text]
        now_price = item_config.price * number
        if cache.rhodes_island.materials_resouce[4] >= now_price or cache.debug_mode:
            self.character_data.item[self.text] += number
            self.character_data.item[self.text] = min(self.character_data.item[self.text], 99)
            cache.rhodes_island.materials_resouce[4] -= now_price
            now_text = _("{0}花费了{1}粉红凭证，购买了{2}个{3}").format(self.character_data.nick_name, now_price, number, item_config.name)
            # 结算成就
            cache.achievement.buy_item_count_list.append(self.text)
        elif self.character_data.item[self.text] == 99:
            now_text = _("已达到最高堆叠上限")
        else:
            now_text = _("你没有足够的粉色凭证")
        now_draw = draw.WaitDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()
        line_feed.draw()
        line_feed.draw()
        # 结算成就
        # achievement_panel.achievement_flow(_("购买道具"))
