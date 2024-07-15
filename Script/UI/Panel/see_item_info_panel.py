from typing import List
from types import FunctionType
from Script.Core import cache_control, text_handle, get_text, flow_handle, constant, py_cmd, game_type
from Script.UI.Moudle import panel, draw
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """


class SeeCharacterItemBagPanel:
    """
    查看角色道具背包面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 绘制的角色id """
        self.width: int = width
        """ 最大绘制宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.character_data = cache.character_data[character_id]

        # 按类别统计全部道具
        self.item_list_all = []
        item_list_Drug = []
        item_list_Machine = []
        item_list_Consumables = []
        item_list_H_Drug = []
        item_list_H_Machine = []
        item_list_SM = []
        self.item_list = [i for i in game_config.config_item]
        for item_id in self.item_list:
            if self.character_data.item[item_id] >= 1:
                if game_config.config_item[item_id].tag == "Drug":
                    item_list_Drug.append(item_id)
                elif game_config.config_item[item_id].tag == "Machine":
                    item_list_Machine.append(item_id)
                elif game_config.config_item[item_id].tag == "Consumables":
                    item_list_Consumables.append(item_id)
                elif game_config.config_item[item_id].tag == "H_Drug":
                    item_list_H_Drug.append(item_id)
                elif game_config.config_item[item_id].tag == "H_Machine":
                    item_list_H_Machine.append(item_id)
                elif game_config.config_item[item_id].tag == "SM":
                    item_list_SM.append(item_id)
        self.item_list_all.append(item_list_Drug)
        self.item_list_all.append(item_list_Machine)
        self.item_list_all.append(item_list_Consumables)
        self.item_list_all.append(item_list_H_Drug)
        self.item_list_all.append(item_list_H_Machine)
        self.item_list_all.append(item_list_SM)

        item_panel = panel.PageHandlePanel([], ItemNameDraw, 50, 5, width, 1, 1, 0)
        self.handle_panel = item_panel
        """ 页面控制对象 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("人物道具"), self.width)
        item_list_type = [_("药品"), _("机器"), _("消耗品"), _("H药品"), _("H用机器"), _("SM器具")]
        while 1:
            title_draw.draw()
            # 绘制粉红凭证
            money_text = _("当前持有粉红凭证：{0}").format(str(cache.rhodes_island.materials_resouce[4]))
            now_draw = draw.NormalDraw()
            now_draw.text = money_text
            now_draw.width = self.width
            now_draw.draw()
            line_feed.draw()

            # 绘制道具面板

            # 遍历输出每个类型的面板
            for i in range(len(self.item_list_all)):
                # 输出类别文字
                type_text = f"————{item_list_type[i]}————"
                now_draw = draw.NormalDraw()
                now_draw.text = type_text
                now_draw.width = self.width
                now_draw.draw()
                line_feed.draw()

                # 输出面板
                self.handle_panel.text_list = self.item_list_all[i]
                self.handle_panel.update()
                self.handle_panel.draw()

            # 将道具列表输入可返回列表中
            self.return_list = []
            for i in self.item_list:
                self.return_list.append(str(i))
            # self.return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            self.return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


class ItemNameDraw:
    """
    按道具id绘制道具名
    Keyword arguments:
    text -- 道具的配表id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    butoon_id -- 数字按钮的id
    """

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text: int = int(text)
        """ 道具的配表id """
        self.draw_text: str = ""
        """ 道具名绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(text)
        """ 按钮返回值 """
        item_config = game_config.config_item[self.text]
        item_name = item_config.name
        character_data = cache.character_data[0]
        flag_consumables = item_config.tag in ["Drug", "H_Drug", "Consumables"]
        self.use_drug_flag = False
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                self.draw_text = f"{index_text} {item_name}"
                if flag_consumables:
                    self.draw_text += _("(持有数量:") + str(character_data.item[self.text]) + ")"
                if item_config.tag == "Drug":
                    self.use_drug_flag = True
            else:
                self.draw_text = item_name
        else:
            self.draw_text = f"[{item_name}]"

        self.button_return = str(text)

    def draw(self):
        """绘制道具"""
        if self.is_button:
            now_draw = draw.LeftButton(self.draw_text, self.button_return, self.width, cmd_func=self.draw_item_info)
        else:
            now_draw = draw.NormalDraw()
            now_draw.text = self.draw_text
        now_draw.width = self.width
        now_draw.draw()

    def draw_item_info(self):
        """绘制道具信息"""
        now_draw = ItemInfoDraw(self.text, window_width)
        now_draw.draw()
        if self.use_drug_flag:
            while 1:
                line_feed.draw()
                use_draw = draw.CenterButton(_("[使用]"), _("[使用]"), window_width / 2)
                use_draw.draw()
                return_draw = draw.CenterButton(_("[返回]"), _("[返回]"), window_width / 2)
                return_draw.draw()
                line_feed.draw()
                yrn = flow_handle.askfor_all([use_draw.return_text, return_draw.return_text])
                if yrn == use_draw.return_text:
                    self.use_drug()
                    break
                elif yrn == return_draw.return_text:
                    break

    def use_drug(self):
        """使用药剂"""
        pl_character_data = cache.character_data[0]
        # 道具数量减少1
        pl_character_data.item[self.text] -= 1
        # 根据道具id获取道具效果
        sanity_point_add = game_config.config_item[self.text].effect
        # 药剂效果
        now_draw = draw.WaitDraw()
        # 理智恢复剂
        if self.text <= 3:
            pl_character_data.sanity_point = min(pl_character_data.sanity_point + sanity_point_add, pl_character_data.sanity_point_max)
            now_draw.text = _("\n{0}使用了{1}，理智值增加{2}，现在为{3}/{4}\n\n").format(pl_character_data.name, game_config.config_item[self.text].name, sanity_point_add, pl_character_data.sanity_point, pl_character_data.sanity_point_max)
        # 精力恢复剂
        elif self.text == 11:
            pl_character_data.semen_point = min(pl_character_data.semen_point + sanity_point_add, pl_character_data.semen_point_max)
            now_draw.text = _("\n{0}使用了{1}，精液量增加了{2}，现在为{3}/{4}\n\n").format(pl_character_data.name, game_config.config_item[self.text].name, sanity_point_add, pl_character_data.semen_point, pl_character_data.semen_point_max)
        # 绘制使用道具信息
        now_draw.width = window_width
        now_draw.draw()


class ItemInfoDraw:
    """
    按道具id绘制道具数据
    Keyword arguments
    cid -- 道具id
    width -- 最大绘制宽度
    """

    def __init__(self, cid: int, width: int):
        """初始化绘制对象"""
        self.cid: int = int(cid)
        """ 道具的配表id """
        self.width: int = width
        """ 最大宽度 """

    def draw(self):
        """绘制道具信息"""
        py_cmd.clr_cmd()
        item_config = game_config.config_item[self.cid]
        item_draw = draw.WaitDraw()
        item_draw.text = f"{item_config.name}:{item_config.info}"
        item_draw.width = self.width
        item_draw.draw()
        line_feed = draw.NormalDraw()
        line_feed.text = "\n"
        line_feed.width = 1
        line_feed.draw()
