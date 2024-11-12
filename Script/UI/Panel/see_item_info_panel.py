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
                if game_config.config_item[item_id].type == "Drug":
                    item_list_Drug.append(item_id)
                elif game_config.config_item[item_id].type == "Machine":
                    item_list_Machine.append(item_id)
                elif game_config.config_item[item_id].type == "Consumables":
                    item_list_Consumables.append(item_id)
                elif game_config.config_item[item_id].type == "H_Drug":
                    item_list_H_Drug.append(item_id)
                elif game_config.config_item[item_id].type == "H_Machine":
                    item_list_H_Machine.append(item_id)
                elif game_config.config_item[item_id].type == "SM":
                    item_list_SM.append(item_id)
        self.item_list_all.append(item_list_Drug)
        self.item_list_all.append(item_list_Machine)
        self.item_list_all.append(item_list_Consumables)
        self.item_list_all.append(item_list_H_Drug)
        self.item_list_all.append(item_list_H_Machine)
        self.item_list_all.append(item_list_SM)

        item_panel = panel.PageHandlePanel([], ItemNameDraw, 50, 2, width, 1, 1, 0)
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
        self.item_id: int = int(text)
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
        item_tada = game_config.config_item[self.item_id]
        item_name = item_tada.name
        character_data = cache.character_data[0]
        flag_consumables = item_tada.type in ["Drug", "H_Drug", "Consumables"]
        # 消耗品和药剂使用标记初始化
        self.use_drug_flag = False
        self.use_consumables_flag = False
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                self.draw_text = f"{index_text} {item_name}"
                if flag_consumables:
                    self.draw_text += _("(持有数量:") + str(character_data.item[self.item_id]) + ")"
                    if character_data.item[self.item_id] <= 0:
                        self.is_button = False
                # 药剂和消耗品使用标记
                if item_tada.type == "Drug":
                    self.use_drug_flag = True
                elif item_tada.type == "Consumables":
                    self.use_consumables_flag = True
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
            now_draw.style = "deep_gray"
            now_draw.text = self.draw_text
        now_draw.width = self.width
        now_draw.draw()

    def draw_item_info(self):
        """绘制道具信息"""
        now_draw = ItemInfoDraw(self.item_id, window_width)
        now_draw.draw()
        if self.use_drug_flag or self.use_consumables_flag:
            while 1:
                line_feed.draw()
                use_draw = draw.CenterButton(_("[使用]"), _("[使用]"), window_width / 2)
                use_draw.draw()
                return_draw = draw.CenterButton(_("[返回]"), _("[返回]"), window_width / 2)
                return_draw.draw()
                line_feed.draw()
                yrn = flow_handle.askfor_all([use_draw.return_text, return_draw.return_text])
                if yrn == use_draw.return_text:
                    # 消耗品和药剂使用分支
                    if self.use_consumables_flag:
                        self.use_consumables()
                    elif self.use_drug_flag:
                        self.use_drug()
                    break
                elif yrn == return_draw.return_text:
                    break

    def use_consumables(self):
        """使用消耗品"""
        from Script.Design import character
        pl_character_data = cache.character_data[0]
        item_data = game_config.config_item[self.item_id]
        item_tag = item_data.tag

        now_draw = draw.WaitDraw()
        now_draw.text = _("\n{0}使用了{1}\n\n").format(pl_character_data.name, item_data.name)

        # 无法直接使用的道具
        if item_tag == "SP_use":
            now_draw.text = _("\n该道具无法直接使用\n\n")
            now_draw.width = window_width
            now_draw.draw()
            return

        # 道具数量减少1
        pl_character_data.item[self.item_id] -= 1
        # 根据道具id获取道具效果
        # sanity_point_add = game_config.config_item[self.text].effect
        # 消耗品效果
        # 改名卡
        if self.item_id == 161:
            pl_character_data.name = character.input_name_func(_("你能回忆起自己的名字吗？（默认称呼为博士，此处仅输入姓名即可）"))
        # 绘制使用道具信息
        now_draw.width = window_width
        now_draw.draw()

    def use_drug(self):
        """使用药剂"""
        pl_character_data = cache.character_data[0]
        target_character_id = pl_character_data.target_character_id
        target_character_data = cache.character_data[target_character_id]
        # 根据道具id获取道具效果
        item_data = game_config.config_item[self.item_id]
        sanity_point_add = item_data.effect
        item_tag = item_data.tag
        # 如果是对NPC使用的药剂，且当前没有NPC交互对象，则输出错误信息并返回
        if item_tag == "npc_use" and target_character_id == 0:
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n当前没有交互对象，无法使用{0}\n\n").format(item_data.name)
            now_draw.width = window_width
            now_draw.draw()
            return
        # 道具数量减少1
        pl_character_data.item[self.item_id] -= 1
        # 药剂效果
        now_draw = draw.WaitDraw()
        # 理智恢复剂
        if self.item_id <= 3:
            pl_character_data.sanity_point = min(pl_character_data.sanity_point + sanity_point_add, pl_character_data.sanity_point_max)
            now_draw.text = _("\n{0}使用了{1}，理智值增加{2}，现在为{3}/{4}\n\n").format(pl_character_data.name, item_data.name, sanity_point_add, pl_character_data.sanity_point, pl_character_data.sanity_point_max)
        # 精力恢复剂
        elif self.item_id == 11:
            pl_character_data.semen_point = min(pl_character_data.semen_point + sanity_point_add, pl_character_data.semen_point_max)
            now_draw.text = _("\n{0}使用了{1}，精液量增加了{2}，现在为{3}/{4}\n\n").format(pl_character_data.name, item_data.name, sanity_point_add, pl_character_data.semen_point, pl_character_data.semen_point_max)
        # 阴茎增大
        elif self.item_id == 16:
            pl_character_data.pl_ability.jj_size += 1
            pl_character_data.pl_ability.jj_size = min(pl_character_data.pl_ability.jj_size, 3)
            size_name = game_config.config_jj_tem[pl_character_data.pl_ability.jj_size].name
            now_draw.text += _("{0}的阴茎尺寸增加了，现在是{1}\n".format(pl_character_data.name, size_name))
        # 阴茎缩小
        elif self.item_id == 17:
            pl_character_data.pl_ability.jj_size -= 1
            pl_character_data.pl_ability.jj_size = max(pl_character_data.pl_ability.jj_size, 0)
            size_name = game_config.config_jj_tem[pl_character_data.pl_ability.jj_size].name
            now_draw.text += _("{0}的阴茎尺寸减小了，现在是{1}\n".format(pl_character_data.name, size_name))
        # 丰胸药
        elif self.item_id == 21:
            now_draw.text += self.update_talent(target_character_id, [121, 122, 123, 124, 125], True, _("胸部"))
        # 缩胸药
        elif self.item_id == 22:
            now_draw.text += self.update_talent(target_character_id, [121, 122, 123, 124, 125], False, _("胸部"))
        # 丰臀药
        elif self.item_id == 23:
            now_draw.text += self.update_talent(target_character_id, [126, 127, 128], True, _("臀部"))
        # 缩臀药
        elif self.item_id == 24:
            now_draw.text += self.update_talent(target_character_id, [126, 127, 128], False, _("臀部"))
        # 丰腿药
        elif self.item_id == 25:
            now_draw.text += self.update_talent(target_character_id, [129, 130], True, _("腿部"))
        # 瘦腿药
        elif self.item_id == 26:
            now_draw.text += self.update_talent(target_character_id, [129, 130], False, _("腿部"))
        # 丰足药
        elif self.item_id == 27:
            now_draw.text += self.update_talent(target_character_id, [131, 132], True, _("足部"))
        # 瘦足药
        elif self.item_id == 28:
            now_draw.text += self.update_talent(target_character_id, [131, 132], False, _("足部"))
        # 外表年龄增长药
        elif self.item_id == 31:
            now_draw.text += self.update_talent(target_character_id, [103, 104, 105, 106, 107], True, _("外表年龄"))
        # 外表年龄减少药
        elif self.item_id == 32:
            now_draw.text += self.update_talent(target_character_id, [103, 104, 105, 106, 107], False, _("外表年龄"))
        # 泌乳药
        elif self.item_id == 33:
            # 如果已经有泌乳，则不再增加
            if target_character_data.talent[27] == 1:
                now_draw.text += _("{0}已经有【泌乳】了，无法再获得【泌乳】\n".format(target_character_data.name))
                # 道具数量增加1
                pl_character_data.item[self.item_id] += 1
            else:
                target_character_data.talent[27] = 1
                now_draw.text += _("{0}获得了【泌乳】\n".format(target_character_data.name))
        # 停乳药
        elif self.item_id == 34:
            # 如果没有泌乳，则不再减少
            if target_character_data.talent[27] == 0:
                now_draw.text += _("{0}没有【泌乳】，无法失去【泌乳】\n".format(target_character_data.name))
                # 道具数量增加1
                pl_character_data.item[self.item_id] += 1
            else:
                target_character_data.talent[27] = 0
                now_draw.text += _("{0}失去了【泌乳】\n".format(target_character_data.name))

        # 绘制使用道具信息
        now_draw.width = window_width
        now_draw.draw()


    def update_talent(self, character_id, talent_ids, increase, body_part):
        """
        根据素质id表来增加或减少角色素质
        Keyword arguments:
        character_id -- 角色id
        talent_ids -- 素质id列表
        increase -- 是否增加
        body_part -- 身体部位
        """
        now_character_data = cache.character_data[character_id]
        # 获取当前素质id
        for talent_id in talent_ids:
            if now_character_data.talent[talent_id] == 1:
                now_talent_id = talent_id
                break
        # 更新素质id
        if increase:
            new_talent_id = min(now_talent_id + 1, talent_ids[-1])
        else:
            new_talent_id = max(now_talent_id - 1, talent_ids[0])
        now_character_data.talent[now_talent_id] = 0
        now_character_data.talent[new_talent_id] = 1
        # 输出信息
        change_text = _("变大了") if increase else _("变小了")
        return_text = _("{0}的{1}{2}，现在是【{3}】\n".format(now_character_data.name, body_part, change_text, game_config.config_talent[new_talent_id].name))
        return return_text


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
        # 如果是对交互对象使用的，则加上交互对象的名字
        pl_character_data = cache.character_data[0]
        target_character_id = pl_character_data.target_character_id
        item_draw = draw.NormalDraw()
        item_draw.text = f"{item_config.name}: {item_config.info}"
        if item_config.tag == "npc_use" and target_character_id != 0:
            target_character_data = cache.character_data[target_character_id]
            item_draw.text += "\n" + _("○对{0}使用\n".format(target_character_data.name))
        item_draw.width = self.width
        item_draw.draw()
        line_feed.draw()
