from typing import List
from types import FunctionType
from Script.Core import game_type, cache_control, rich_text, get_text, constant, py_cmd, text_handle, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, handle_premise, clothing, update, character
from Script.UI.Moudle import draw, panel

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


def cloth_off_after_settle(character_id: int):
    """
    结算后的脱衣服操作
    Keyword arguments:
    character_id -- 角色id
    """
    character_data = cache.character_data[character_id]
    for i in game_config.config_clothing_type:
        # 去重
        character_data.cloth.cloth_off[i] = list(set(character_data.cloth.cloth_off[i]))
        # 如果某个脱掉的衣服还在穿着，则从脱掉的衣服列表中移除
        for j in character_data.cloth.cloth_off[i]:
            if j in character_data.cloth.cloth_wear[i]:
                character_data.cloth.cloth_off[i].remove(j)

class SeeCharacterClothPanel:
    """
    显示角色服装面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, type_number: int, center_status: bool = True):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.column = column
        """ 每行状态最大个数 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.center_status: bool = center_status
        """ 居中绘制状态文本 """
        self.type_number = type_number
        """ 显示的状态类型 """
        character_data = cache.character_data[0]
        target_character_data = cache.character_data[character_data.target_character_id]

        type_line = draw.LittleTitleLineDraw(_("服装"), width, ":")
        self.draw_list.append(type_line)

        # cloth_text_list = []
        now_text = ""
        # 遍历全部衣服类型
        # print(f"debug target_character_data.cloth.cloth_wear = {target_character_data.cloth.cloth_wear}")
        for clothing_type in game_config.config_clothing_type:
            type_name = game_config.config_clothing_type[clothing_type].name
            # 当该类型里有衣服存在的时候才显示
            if len(target_character_data.cloth.cloth_wear[clothing_type]):
                # 正常情况下不显示胸部和内裤的服装,debug或该部位可以显示则显示
                if clothing_type in {6, 9} and not cache.debug_mode:
                    # print(f"debug {target_character_data.name}.cloth_see[clothing_type] = {target_character_data.cloth_see[clothing_type]}")
                    # 以下情况自动显示：
                    # 1.开启透视能力
                    # 2.没穿对应部位外面的衣服
                    if (
                            (character_data.pl_ability.visual and character_data.talent[307])
                            or len(target_character_data.cloth.cloth_wear[clothing_type - 1]) == 0
                    ):
                        target_character_data.cloth.cloth_see[clothing_type] = True
                    else:
                        target_character_data.cloth.cloth_see[clothing_type] = False
                    # 如果不显示，则不显示（废话
                    if not target_character_data.cloth.cloth_see[clothing_type]:
                        continue
                # 当显示到下衣8的时候，换行
                if clothing_type == 8 and now_text != "":
                    now_text += "\n"
                now_text += f"  [{type_name}]:"
                # 如果有多个衣服，则依次显示
                for cloth_id in target_character_data.cloth.cloth_wear[clothing_type]:
                    cloth_name = game_config.config_clothing_tem[cloth_id].name
                    now_text += f" {cloth_name}"
                    # 这里出现过BUG，所以加一层检测是否为空的判断
                    if len(target_character_data.dirty.cloth_semen) == 0:
                        empty_dirty_data = attr_calculation.get_dirty_reset(target_character_data.dirty)
                        target_character_data.dirty.cloth_semen = empty_dirty_data.cloth_semen
                    # 如果该部位有精液，则显示精液信息
                    if target_character_data.dirty.cloth_semen[clothing_type][1] != 0:
                        semen_level = target_character_data.dirty.cloth_semen[clothing_type][2]
                        dirty_text_cid = "{0}精液污浊{1}".format(_(type_name, revert_translation = True), str(semen_level))
                        dirty_text_context = game_config.ui_text_data['dirty'][dirty_text_cid]
                        now_text += f"<semen>({dirty_text_context})</semen>"
            # 当显示到下衣8的时候，换行
            if clothing_type == 8 and len(target_character_data.cloth.cloth_wear[8]) == 0:
                now_text += "\n"
            # 真空的胸衣和内裤单独显示
            if clothing_type in {6, 9} and not len(target_character_data.cloth.cloth_wear[clothing_type]):
                if not cache.debug_mode:
                    # print(f"debug {target_character_data.name}.cloth.cloth_see[clothing_type] = {target_character_data.cloth.cloth_see[clothing_type]}")
                    if not target_character_data.cloth.cloth_see[clothing_type]:
                        continue
                now_text += _("  [{0}]: 真空").format(type_name)
        now_text += "\n"
        # cloth_text_list.append(now_text)

        no_cloth_flag = True
        for clothing_type in game_config.config_clothing_type:
            if len(target_character_data.cloth.cloth_wear[clothing_type]):
                no_cloth_flag = False
                break
        if no_cloth_flag:
            now_text = _("  全裸\n")
            # cloth_text_list.append(now_text)

        # 计算脱下的衣服
        off_text = _("  [已脱下]:")
        count = 0
        for cloth_type in target_character_data.cloth.cloth_off:
            for cloth_id in target_character_data.cloth.cloth_off[cloth_type]:
                cloth_name = game_config.config_clothing_tem[cloth_id].name
                off_text += f" {cloth_name}"
                # 每8个衣服换行
                count += 1
                if count % 8 == 0:
                    off_text += "\n           "
        # 最后一个字符不是换行符则换行
        if off_text[-1] != "\n":
            off_text += "\n"
        # 如果有脱下的衣服，且在H中则显示
        if count != 0 and handle_premise.handle_is_h(0):
            now_text += off_text

        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()

        # 富文本模组
        now_style_list = rich_text.get_rich_text_print(now_text, "standard")
        new_x_list = rich_text.remove_rich_cache(now_text)
        # test_flag = False
        # if 'emoji' in now_style_list:
        #     test_flag = True
        #     print(f"debug 总：now_style_list = {now_style_list}")
        #     print(f"debug 总：new_x_list = {new_x_list}")
        while 1:
            if not len(new_x_list):
                break
            # now_rich_draw = game_type.MapDrawText()
            now_rich_draw = draw.NormalDraw()
            now_rich_draw.text = new_x_list[0]
            now_rich_draw.style = now_style_list[0]
            now_style_list = now_style_list[1:]
            new_x_list = new_x_list[1:]
            # if test_flag:
            #     print(f"debug now_rich_draw.style = {now_rich_draw.style}")
            while 1:
                if not len(new_x_list):
                    break
                if now_style_list[0] != now_rich_draw.style:
                    break
                now_rich_draw.text += new_x_list[0]
                now_style_list = now_style_list[1:]
                new_x_list = new_x_list[1:]
                # if test_flag:
                #     print(f"debug 分：now_rich_draw.text = {now_rich_draw.text}")
                #     print(f"debug 分：now_style_list = {now_style_list}")
                #     print(f"debug 分：new_x_list = {new_x_list}")
            now_draw.draw_list.append(now_rich_draw)
            now_draw.width += len(now_rich_draw.text)

        # now_draw.set(cloth_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()


class Undress_Panel:
    """
    用于查看脱衣服面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("脱衣服")
        """ 当前绘制的面板类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("脱衣服"), self.width)

        self.handle_panel = panel.PageHandlePanel([], SeeUndressButtonList, 10, 1, self.width, 1, 1, 0)
        while 1:
            py_cmd.clr_cmd()
            button_text_list = [_("脱到只穿内衣      "),_("脱到只穿袜子手套等"),_("脱到全裸          "),_("把内裤收走        ")]

            self.handle_panel.text_list = button_text_list
            self.handle_panel.update()
            title_draw.draw()
            return_list = []

            line_feed.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class SeeUndressButtonList:
    """
    点击后可选择脱衣服选项的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: str, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.button_name_text: str = text
        """ 指令名字绘制文本 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        # 按钮绘制
        name_draw = draw.NormalDraw()
        text_flag = False

        index_text = text_handle.id_index(button_id)
        button_text = f"{index_text}{self.button_name_text}"
        # print(f"debug button_id = {button_id}")
        # print(f"debug target_data.cloth = {target_data.cloth}")


        # 0号指令,脱到只穿内衣
        if self.button_id == 0:
            cloth_count = len(target_data.cloth.cloth_wear[5]) + len(target_data.cloth.cloth_wear[8])
            if cloth_count:
                button_text += _(" ：会脱掉")
                for i in {5,8}:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += _(" ：无可脱的衣服")
                text_flag = True

        # 1号指令,脱到只穿袜子手套等
        elif self.button_id == 1:
            cloth_count = len(target_data.cloth.cloth_wear[5]) + len(target_data.cloth.cloth_wear[6]) + len(target_data.cloth.cloth_wear[8]) + len(target_data.cloth.cloth_wear[9])
            if cloth_count:
                button_text += _(" ：会脱掉")
                for i in {5,6,8,9}:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += _(" ：无可脱的衣服")
                text_flag = True

        # 2号指令,脱到全裸
        elif self.button_id == 2:
            cloth_count = 0
            for i in game_config.config_clothing_type:
                cloth_count += len(target_data.cloth.cloth_wear[i])
            if cloth_count:
                button_text += _(" ：会脱掉")
                for i in game_config.config_clothing_type:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += _(" ：无可脱的衣服")
                text_flag = True

        # 3号指令,把内裤收走
        if self.button_id == 3:
            cloth_count = len(target_data.cloth.cloth_wear[9])
            if cloth_count:
                button_text += _(" ：会收走")
                for i in {9}:
                    for j in target_data.cloth.cloth_wear[i]:
                        cloth_name = game_config.config_clothing_tem[j].name
                        button_text += f" {cloth_name}"
            else:
                button_text += _(" ：无可收的内裤")
                text_flag = True

        # 如果按钮不可选则变成文本
        if not text_flag:
            name_draw = draw.LeftButton(
                button_text, self.button_return, self.width, cmd_func=self.chose_button
            )
        else:
            name_draw = draw.LeftDraw()
            name_draw.text = button_text
            name_draw.width = self.width

        self.button_return = text
        self.now_draw = name_draw
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw

    def chose_button(self):
        """玩家点击了选项"""
        character.init_character_behavior_start_time(0, cache.game_time)
        character_data = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        character_data.behavior.duration = 5
        update.game_update_flow(5)

        # 0号指令,脱到只穿内衣
        if self.button_id == 0:

            for i in {5,8}:
                target_data.cloth.cloth_off[i].extend(target_data.cloth.cloth_wear[i])
            clothing.undress_out_cloth(character_data.target_character_id)
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

        # 1号指令,脱到只穿袜子手套等
        elif self.button_id == 1:
            for i in {5,6,8,9}:
                target_data.cloth.cloth_off[i].extend(target_data.cloth.cloth_wear[i])
            clothing.strip_down_till_socks_and_gloves_left(character_data.target_character_id)
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

        # 2号指令,脱到全裸
        elif self.button_id == 2:
            for i in game_config.config_clothing_type:
                target_data.cloth.cloth_off[i].extend(target_data.cloth.cloth_wear[i])
            clothing.get_all_cloth_off(character_data.target_character_id)
            # character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
            # character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

        # 3号指令,把内裤收走
        elif self.button_id == 3:
            clothing.pl_get_chara_pan(character_data.target_character_id)

        # 后处理
        cloth_off_after_settle(character_data.target_character_id)

        # debug用打印
        # print(f"debug target_data.cloth.cloth_wear = {target_data.cloth.cloth_wear}")
        # print(f"debug target_data.cloth.cloth_off = {target_data.cloth.cloth_off}")

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
