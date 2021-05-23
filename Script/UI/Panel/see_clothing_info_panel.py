from uuid import UUID
from types import FunctionType
from typing import List, Tuple
from Script.Core import cache_control, game_type, text_handle, get_text, flow_handle, py_cmd
from Script.Config import game_config
from Script.UI.Moudle import draw, panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class SeeCharacterPutOnClothingListPanel:
    """
    显示角色已穿戴服装面板
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

    def draw(self):
        """绘制面板"""
        character_data = cache.character_data[self.character_id]
        title_draw = draw.TitleLineDraw(_("人物服装"), self.width)
        title_draw.draw()
        draw_list = []
        self.return_list = []
        id_width = 0
        for clothing_type in game_config.config_clothing_type:
            type_data = game_config.config_clothing_type[clothing_type]
            type_draw = draw.LittleTitleLineDraw(type_data.name, self.width, ":")
            draw_list.append(type_draw)
            if clothing_type in character_data.put_on and isinstance(
                character_data.put_on[clothing_type], UUID
            ):
                now_draw = ClothingInfoDrawPanel(
                    self.character_id,
                    clothing_type,
                    character_data.put_on[clothing_type],
                    self.width,
                    1,
                    len(self.return_list),
                )
                self.return_list.append(str(len(self.return_list)))
                now_id_width = text_handle.get_text_index(now_draw.text_list[0])
                if now_id_width > id_width:
                    id_width = now_id_width
            else:
                now_text = _("未穿戴")
                if not self.character_id:
                    now_id = len(self.return_list)
                    now_id_text = text_handle.id_index(now_id)
                    now_width = self.width - len(now_id_text)
                    now_text = text_handle.align(now_text, "center", text_width=now_width)
                    now_text = f"{now_id_text}{now_text}"
                    now_draw = draw.Button(
                        now_text, str(now_id), cmd_func=self.see_clothing_list, args=(clothing_type,)
                    )
                    self.return_list.append(str(now_id))
                else:
                    now_draw = draw.CenterDraw()
                    now_draw.text = now_text
                now_draw.width = self.width
            draw_list.append(now_draw)
            draw_list.append(line_feed)
        for value in draw_list:
            if "id_width" in value.__dict__:
                value.id_width = id_width
            value.draw()

    def see_clothing_list(self, clothing_type: int):
        """
        查看换装列表
        Keyword arguments:
        clothing_type -- 查看的服装类型
        """
        now_draw = WearClothingListPanel(clothing_type, self.width)
        now_draw.draw()


class ClothingDescribeDraw:
    """
    服装描述绘制对象
    Keyword arguments:
    clothing_id -- 服装模板id
    width -- 绘制宽度
    """

    def __init__(self, clothing_id: int, width: int):
        """初始化绘制对象"""
        self.clothing_id: int = clothing_id
        """ 服装id """
        self.width: int = width
        """ 绘制宽度 """

    def draw(self):
        """绘制对象"""
        clothing_config = game_config.config_clothing_tem[self.clothing_id]
        info_draw = draw.WaitDraw()
        info_draw.text = clothing_config.describe
        info_draw.width = self.width
        info_draw.draw()
        line_feed.draw()


class ClothingInfoDrawPanel:
    """
    服装信息绘制面板
    Keyword arguments:
    character_id -- 角色id
    clothing_type -- 服装类型
    clothing_type -- 服装id
    width -- 绘制宽度
    draw_button -- 是否按按钮绘制
    button_id -- 绘制按钮时的id
    """

    def __init__(
        self,
        character_id: int,
        clothing_type: int,
        clothing_id: UUID,
        width: int,
        draw_button: bool = False,
        button_id: int = 0,
    ):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 服装所属的角色id """
        character_data = cache.character_data[character_id]
        self.clothing_data: game_type.Clothing = character_data.clothing[clothing_type][clothing_id]
        """ 当前服装数据 """
        self.width: int = width
        """ 最大绘制宽度 """
        self.draw_button: bool = draw_button
        """ 是否按按钮绘制 """
        self.button_id: int = button_id
        """ 绘制按钮时的id """
        self.id_width: int = 0
        """ 绘制时计算用的id宽度 """
        now_id_text = ""
        if self.draw_button:
            now_id_text = text_handle.id_index(self.button_id)
        fix_width = self.width - len(now_id_text)
        value_dict = {
            _("可爱"): self.clothing_data.sweet,
            _("性感"): self.clothing_data.sexy,
            _("帅气"): self.clothing_data.handsome,
            _("清新"): self.clothing_data.fresh,
            _("典雅"): self.clothing_data.elegant,
            _("清洁"): self.clothing_data.cleanliness,
            _("保暖"): self.clothing_data.warm,
        }
        describe_list = [_("可爱的"), _("性感的"), _("帅气的"), _("清新的"), _("典雅的"), _("清洁的"), _("保暖的")]
        value_list = list(value_dict.values())
        describe_id = value_list.index(max(value_list))
        describe = describe_list[describe_id]
        clothing_config = game_config.config_clothing_tem[self.clothing_data.tem_id]
        clothing_name = f"{self.clothing_data.evaluation}{describe}{clothing_config.name}"
        fix_width -= text_handle.get_text_index(clothing_name)
        value_text = ""
        for value_id in value_dict:
            value = str(value_dict[value_id])
            if len(value) < 4:
                value = (4 - len(value)) * " " + value
            value_text += f"|{value_id}:{value}"
        value_text += "|"
        id_text = ""
        if self.draw_button:
            id_text = f"{now_id_text} {clothing_name}"
        else:
            id_text = clothing_name
        self.text_list: List[str] = [id_text, value_text]
        """ 绘制的文本列表 """

    def draw(self):
        self.text_list[1] = text_handle.align(self.text_list[1], "center", 0, 1, self.width - self.id_width)
        text_width = text_handle.get_text_index(self.text_list[0])
        if text_width < self.id_width:
            self.text_list[0] += " " * (self.id_width - text_width)
        now_text = f"{self.text_list[0]}{self.text_list[1]}"
        if self.draw_button:
            now_draw = draw.Button(now_text, str(self.button_id), cmd_func=self.see_clothing_info)
        else:
            now_draw = draw.NormalDraw()
            now_draw.text = now_text
        now_draw.width = self.width
        now_draw.draw()

    def see_clothing_info(self):
        """查看服装信息"""
        py_cmd.clr_cmd()
        now_draw = ClothingDescribeDraw(self.clothing_data.tem_id, self.width)
        now_draw.width = self.width
        now_draw.draw()
        if not self.character_id:
            wear_draw = WearClothingListPanel(self.clothing_data.wear, self.width)
            wear_draw.draw()


class WearClothingListPanel:
    """
    穿戴服装列表绘制面板
    Keyword arguments:
    clothing_type -- 服装类型
    width -- 绘制宽度
    """

    def __init__(self, clothing_type: int, width: int):
        """初始化绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        self.width: int = width
        """ 绘制宽度 """
        self.handle_panel: panel.ClothingPageHandlePanel = None
        """ 页面控制对象 """
        if clothing_type in character_data.clothing:
            clothing_list = character_data.clothing[clothing_type].keys()
            now_list = [(i, clothing_type) for i in clothing_list]
            self.handle_panel = panel.ClothingPageHandlePanel(
                now_list, ChangeClothingDraw, 10, 1, width, 1, 1
            )

    def draw(self):
        """绘制对象"""
        py_cmd.clr_cmd()
        if self.handle_panel is not None:
            while 1:
                line_feed.draw()
                title_draw = draw.TitleLineDraw(_("更衣室"), self.width)
                title_draw.draw()
                self.return_list = []
                self.handle_panel.update()
                self.handle_panel.update_button()
                self.handle_panel.draw()
                self.return_list.extend(self.handle_panel.return_list)
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
                back_draw.draw()
                line_feed.draw()
                self.return_list.append(back_draw.return_text)
                yrn = flow_handle.askfor_all(self.return_list)
                py_cmd.clr_cmd()
                if yrn == back_draw.return_text:
                    break
        else:
            now_text = _("空无一物")
            now_draw = draw.WaitDraw()
            now_draw.text = now_text
            now_draw.width = self.width
            now_draw.draw()
            line_feed.draw()


class ChangeClothingDraw:
    """
    换装面板按服装id绘制服装缩略信息
    Keyword arguments:
    text -- 服装id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮的id
    """

    def __init__(self, text: Tuple, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text: UUID = text[0]
        """ 服装id """
        self.clothing_type: int = text[1]
        """ 服装类型 """
        self.width: int = width
        """ 绘制宽度 """
        self.draw_text: str = ""
        """ 服装缩略信息绘制文本 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        character_data: game_type.Character = cache.character_data[0]
        now_id_text = ""
        now_id_text = text_handle.id_index(self.button_id)
        fix_width = self.width - len(now_id_text)
        self.clothing_data: game_type.Clothing = character_data.clothing[self.clothing_type][self.text]
        value_dict = {
            _("可爱"): self.clothing_data.sweet,
            _("性感"): self.clothing_data.sexy,
            _("帅气"): self.clothing_data.handsome,
            _("清新"): self.clothing_data.fresh,
            _("典雅"): self.clothing_data.elegant,
            _("清洁"): self.clothing_data.cleanliness,
            _("保暖"): self.clothing_data.warm,
        }
        describe_list = [_("可爱的"), _("性感的"), _("帅气的"), _("清新的"), _("典雅的"), _("清洁的"), _("保暖的")]
        value_list = list(value_dict.values())
        describe_id = value_list.index(max(value_list))
        describe = describe_list[describe_id]
        wear_text = ""
        if (
            self.clothing_type in character_data.put_on
            and character_data.put_on[self.clothing_type] == self.clothing_data.uid
        ):
            wear_text = _("(已穿戴)")
        clothing_config = game_config.config_clothing_tem[self.clothing_data.tem_id]
        clothing_name = f"{self.clothing_data.evaluation}{describe}{clothing_config.name}{wear_text}"
        fix_width -= text_handle.get_text_index(clothing_name)
        value_text = ""
        for value_id in value_dict:
            value = str(value_dict[value_id])
            if len(value) < 4:
                value = (4 - len(value)) * " " + value
            value_text += f"|{value_id}:{value}"
        value_text += "|"
        id_text = ""
        id_text = f"{now_id_text} {clothing_name}"
        self.text_list: List[str] = [id_text, value_text]
        """ 绘制的文本列表 """
        self.id_width: int = text_handle.get_text_index(id_text)
        """ id部分的绘制宽度 """
        self.draw_text = " " * self.width

    def draw(self):
        """绘制对象"""
        self.text_list[1] = text_handle.align(
            self.text_list[1], "center", text_width=self.width - self.id_width
        )
        text_width = text_handle.get_text_index(self.text_list[0])
        self.text_list[0] += " " * (self.id_width - text_width)
        now_text = f"{self.text_list[0]}{self.text_list[1]}"
        now_text = now_text.rstrip()
        now_text = text_handle.align(now_text, "center", text_width=self.width)
        now_draw = draw.Button(now_text, str(self.button_id), cmd_func=self.change_clothing)
        now_draw.width = self.width
        now_draw.draw()

    def change_clothing(self):
        """更换角色服装"""
        py_cmd.clr_cmd()
        info_draw = ClothingDescribeDraw(self.clothing_data.tem_id, self.width)
        info_draw.draw()
        cache.character_data[0].put_on[self.clothing_type] = self.clothing_data.uid
