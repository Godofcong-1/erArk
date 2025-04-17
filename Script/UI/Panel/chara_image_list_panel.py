from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    get_text,
    cache_control,
    game_type,
    text_handle,
)
from Script.Design import handle_premise, cross_section_image, character_image

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class CharacterImageListDraw:
    """
    查看角色图片列表
    Keyword arguments:
    width -- 绘制宽度
    character_list -- 绘制的角色列表
    """

    def __init__(self, width: int, character_list: List[int]):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大绘制宽度 """
        self.character_list: List[int] = character_list
        """ 绘制的角色列表 """
        self.return_list: List[str] = []
        """ 返回的按钮列表 """

    def draw(self):
        """绘制列表"""
        head_width = len(self.character_list) * 16
        head_width = min(head_width,160) # 最多修正十个人
        center_fix = text_handle.align("*" * head_width, "center", 1, 1)
        fix_draw = draw.NormalDraw()
        fix_draw.width = self.width
        fix_draw.text = center_fix
        fix_draw.draw()
        self.return_list = []

        # 优先绘制当前交互对象
        if len(self.character_list):
            text_draw = draw.NormalDraw()
            text_draw.width = 1
            text_draw.text = "▷ "
            text_draw.draw()

            # 绘制交互对象
            player_data: game_type.Character = cache.character_data[0]
            if player_data.target_character_id != 0:
                now_draw = CharacterImageButton(player_data.target_character_id, self.width)
                now_draw.draw()
                self.return_list.append(now_draw.return_text)

            # H状态下，且玩家开启了腔内透视
            if handle_premise.handle_is_h(0) and handle_premise.handle_intermediate_penetrating_vision(0) and handle_premise.handle_penetrating_vision_on(0):
                text_draw.text = "    "
                text_draw.draw()
                cross_section_image.draw_cross_section_image()
                text_draw.text = "  "
                text_draw.draw()

            text_draw = draw.NormalDraw()
            text_draw.width = 1
            text_draw.text = " ◁ "
            text_draw.draw()

        # 超过10人，则只绘制10个
        if len(self.character_list) <= 10:
            npc_darw_list = self.character_list
        else:
            # 修正超过数据范围的起始点
            if cache.npc_image_index >= len(self.character_list):
                cache.npc_image_index = len(self.character_list) - 1
            start_index = cache.npc_image_index
            npc_darw_list = self.character_list[start_index:min((10 + start_index), len(self.character_list))]
            # print(f"debug npc_darw_list = {npc_darw_list}")

        # 绘制非交互对象
        for now_character in npc_darw_list:
            if now_character == player_data.target_character_id:
                continue
            now_draw = CharacterImageButton(now_character, self.width)
            now_draw.draw()
            space_draw = draw.NormalDraw()
            space_draw.width = 1
            space_draw.text = " "
            space_draw.draw()
            self.return_list.append(now_draw.return_text)

        # 绘制下一页按钮
        if len(self.character_list) > 10:
            now_button = draw.CenterButton(
                f"[下一页]",
                "下一页",
                8,
                cmd_func=self.next_page,
            )
            now_button.draw()
            self.return_list.append(now_button.return_text)

    def next_page(self):
        """跳到下一页"""
        if cache.npc_image_index + 10 <= len(self.character_list):
            cache.npc_image_index += 10
        else:
            cache.npc_image_index = 0


class CharacterImageButton:
    """
    角色图片按钮
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 角色id """
        self.width: int = width
        """ 绘制宽度 """
        self.return_text = ""
        """ 返回的按钮 """

    def draw(self):
        """绘制图片对象"""
        character_data: game_type.Character = cache.character_data[self.character_id]
        # print(f"debug {character_data.name} = {character_data.relationship.father_id}")
        image_name = character_image.find_character_image_name(self.character_id)
        now_draw = draw.ImageButton(image_name, character_data.name + "头像", self.width, self.change_target)
        now_draw.draw()
        self.return_text = character_data.name + "头像"

    def change_target(self):
        """改变玩家当前交互对象"""
        player_data: game_type.Character = cache.character_data[0]
        if self.character_id:
            player_data.target_character_id = self.character_id
