from types import FunctionType
from Script.Core import cache_control, game_type, text_handle, get_text, flow_handle, py_cmd, constant
from Script.Design import map_handle
from Script.Config import game_config, normal_config
from Script.UI.Moudle import panel, draw

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
        title_draw = draw.TitleLineDraw("成人用品商店", self.width)

        # 按类别统计全部道具
        item_list_all = []
        item_list_Drug = []
        item_list_Machine = []
        item_list_Consumables = []
        item_list_H_Drug = []
        item_list_H_Machine = []
        item_list_SM = []
        item_list_type = ["药品","机器","消耗品","H药品","H用机器","SM器具"]
        item_list = [i for i in game_config.config_item]
        for i in item_list:
            if game_config.config_item[i].tag == "Drug":
                item_list_Drug.append(i)
            elif game_config.config_item[i].tag == "Machine":
                item_list_Machine.append(i)
            elif game_config.config_item[i].tag == "Consumables":
                item_list_Consumables.append(i)
            elif game_config.config_item[i].tag == "H_Drug":
                item_list_H_Drug.append(i)
            elif game_config.config_item[i].tag == "H_Machine":
                item_list_H_Machine.append(i)
            elif game_config.config_item[i].tag == "SM":
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

            # 绘制粉色凭证
            money_text = f"当前持有粉色凭证：{str(cache.rhodes_island.materials_resouce[4])}"
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
        flag_consumables = item_config.tag in ["Drug","H_Drug","Consumables"]
        flag_not_max = self.character_data.item[self.text] <= 99
        flag_have = self.character_data.item[self.text] > 0

        # print("debug flag_consumables = ",flag_consumables,"  flag_not_max = ",flag_not_max,"  flag_have = ",flag_have)

        # 可购买：1消耗品且数量小于99，2非消耗品且未持有
        if (flag_consumables and flag_not_max) or (not flag_consumables and not flag_have):
            if num_button:
                button_text = f"{index_text}{item_config.name}：{item_config.price}凭证"
                if flag_consumables:
                    button_text += "(持有：" + str(self.character_data.item[self.text]) + ")"
                else:
                    button_text += "(未持有)"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.buy_item
                )
            self.draw_text = button_text
        else:
            name_draw = draw.LeftDraw()
            name_draw.text = f"{index_text}{item_config.name}：{item_config.price}凭证"
            if flag_consumables:
                name_draw.text += "(持有：" + str(self.character_data.item[self.text]) + ")"
            else:
                name_draw.text += "(已持有)"
            name_draw.width = self.width
            self.draw_text = name_draw.text

            name_draw.width = self.width
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def buy_item(self):
        py_cmd.clr_cmd()
        line = draw.LineDraw("-", window_width)
        line.draw()
        item_config = game_config.config_item[self.text]
        if cache.rhodes_island.materials_resouce[4] >= item_config.price:
            self.character_data.item[self.text] += 1
            cache.rhodes_island.materials_resouce[4] -= item_config.price
            now_text = _("{nickname}购买了{item_name}").format(
                nickname=self.character_data.nick_name, item_name=item_config.name
            )
        elif self.character_data.item[self.text] == 99:
            now_text = "已达到最高堆叠上限"
        else:
            now_text = "你没有足够的粉色凭证"
        now_draw = draw.WaitDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()
        line_feed.draw()
        line_feed.draw()
