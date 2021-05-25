from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import game_info_panel, see_character_info_panel
from Script.Core import (
    get_text,
    cache_control,
    game_type,
    flow_handle,
    text_handle,
    value_handle,
    constant,
    py_cmd,
)
from Script.Design import attr_text, map_handle, handle_instruct, handle_premise
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class InScenePanel:
    """
    用于查看场景互动界面面板对象
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
        title_draw = draw.TitleLineDraw(_("场景"), self.width)
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        character_handle_panel = panel.PageHandlePanel(
            [],
            see_character_info_panel.SeeCharacterInfoByNameDrawInScene,
            10,
            5,
            self.width,
            1,
            0,
            len(constant.handle_instruct_name_data),
            null_button_text=character_data.target_character_id,
        )
        while 1:
            if character_data.dead:
                cache.wframe_mouse.w_frame_skip_wait_mouse = 0
                now_draw = draw.LineFeedWaitDraw()
                now_draw.text = _("已死亡！")
                now_draw.width = self.width
                now_draw.draw()
                continue
            character_set = scene_data.character_list.copy()
            character_set.remove(0)
            if cache.is_collection:
                character_list = [i for i in character_set if i in character_data.collection_character]
            else:
                character_list = list(character_set)
            character_handle_panel.text_list = character_list
            if character_data.target_character_id not in scene_data.character_list:
                character_data.target_character_id = 0
            if not character_data.target_character_id and len(character_list):
                character_data.target_character_id = character_list[0]
            game_time_draw = game_info_panel.GameTimeInfoPanel(self.width / 2)
            game_time_draw.now_draw.width = len(game_time_draw)
            position_text = attr_text.get_scene_path_text(character_data.position)
            now_position_text = _("当前位置:") + position_text
            now_position_draw = draw.NormalDraw()
            now_position_draw.text = now_position_text
            now_position_draw.width = self.width - len(game_time_draw)
            meet_draw = draw.NormalDraw()
            meet_draw.text = _("你在这里遇到了:")
            meet_draw.width = self.width
            see_instruct_panel = SeeInstructPanel(self.width)
            cache.wframe_mouse.w_frame_skip_wait_mouse = 0
            if cache.now_panel_id != constant.Panel.IN_SCENE:
                break
            character_handle_panel.null_button_text = character_data.target_character_id
            line_feed.draw()
            title_draw.draw()
            game_time_draw.draw()
            now_position_draw.draw()
            line_feed.draw()
            ask_list = []
            if len(character_list) and character_data.target_character_id not in character_list:
                character_data.target_character_id = character_list[0]
            if not len(character_list):
                character_data.target_character_id = 0
            if len(character_list):
                meet_draw.draw()
                line_feed.draw()
                character_handle_panel.update()
                character_handle_panel.draw()
                ask_list.extend(character_handle_panel.return_list)
                line_draw = draw.LineDraw("-.-", self.width)
                line_draw.draw()
            character_info_draw_list = []
            if character_data.target_character_id:
                character_head_draw = see_character_info_panel.CharacterInfoHead(
                    character_data.cid, self.width
                )
                target_head_draw = see_character_info_panel.CharacterInfoHead(
                    character_data.target_character_id, self.width
                )
                character_head_draw_list = [y for x in character_head_draw.draw_list for y in x]
                character_head_draw_list[0].text += " " + character_head_draw_list[2].text
                del character_head_draw_list[2]
                target_head_draw_list = [y for x in target_head_draw.draw_list for y in x]
                target_head_draw_list[0].text += " " + target_head_draw_list[2].text
                del target_head_draw_list[2]
                for value_tuple in character_head_draw_list:
                    value_tuple.draw()
                line_feed.draw()
                for value_tuple in target_head_draw_list:
                    value_tuple.draw()
                line_feed.draw()
                # character_info_draw_list = list(zip(character_head_draw_list, target_head_draw_list))
            else:
                character_head_draw = see_character_info_panel.CharacterInfoHead(
                    character_data.cid, self.width
                )
                character_info_draw_list = character_head_draw.draw_list
                for value_tuple in character_info_draw_list:
                    for value in value_tuple:
                        value.draw()
                    # line_feed.draw()
                line_feed.draw()
            character_clothing_draw_list = []
            # if character_data.target_character_id:
            #     character_clothing_draw = see_character_info_panel.CharacterWearClothingList(
            #         0, self.width / 2, 2
            #     )
            #     target_clothing_draw = see_character_info_panel.CharacterWearClothingList(
            #         character_data.target_character_id, self.width / 2 - 1, 2
            #     )
            #     now_line = len(character_clothing_draw.draw_list)
            #     if len(target_clothing_draw.draw_list) > now_line:
            #         now_line = len(target_clothing_draw.draw_list)
            #     for i in range(now_line):
            #         c_draw = None
            #         if i in range(len(character_clothing_draw.draw_list)):
            #             c_draw = character_clothing_draw.draw_list[i]
            #         else:
            #             c_draw = draw.NormalDraw()
            #             c_draw.text = " " * int(self.width / 2)
            #             c_draw.width = self.width / 2
            #         t_draw = None
            #         if i in range(len(target_clothing_draw.draw_list)):
            #             t_draw = target_clothing_draw.draw_list[i]
            #         else:
            #             t_draw = draw.NormalDraw()
            #             t_draw.text = " " * int(self.width / 2 - 1)
            #             t_draw.width = self.width / 2 - 1
            #         character_clothing_draw_list.append((c_draw, t_draw))
            # else:
            #     character_clothing_draw_list = see_character_info_panel.CharacterWearClothingList(
            #         0, self.width, 4
            #     ).draw_list
            # for label in character_clothing_draw_list:
            #     if isinstance(label, tuple):
            #         index = 0
            #         for value in label:
            #             if isinstance(value, list):
            #                 for value_draw in value:
            #                     value_draw.draw()
            #             else:
            #                 value.line_feed = 0
            #                 value.draw()
            #             if not index:
            #                 fix_draw = draw.NormalDraw()
            #                 fix_draw.width = 1
            #                 fix_draw.text = "|"
            #                 fix_draw.draw()
            #                 index = 1
            #         line_feed.draw()
            #     elif isinstance(label, list):
            #         for value in label:
            #             value.draw()
            #         line_feed.draw()
            #     else:
            #         label.draw()
            character_status_draw_list = []
            if character_data.target_character_id:
                character_status_draw = see_character_info_panel.SeeCharacterStatusPanel(
                    character_data.cid, self.width / 2, 3, 0
                )
                target_status_draw = see_character_info_panel.SeeCharacterStatusPanel(
                    character_data.target_character_id, self.width / 2 - 1, 3, 0
                )
                now_line = len(character_status_draw.draw_list)
                if len(target_status_draw.draw_list) > now_line:
                    now_line = len(target_status_draw.draw_list)
                for i in range(now_line):
                    c_draw = None
                    if i in range(len(character_status_draw.draw_list)):
                        c_draw = character_status_draw.draw_list[i]
                    else:
                        c_draw = draw.NormalDraw()
                        c_draw.text = " " * int(self.width / 2)
                        c_draw.width = self.width / 2
                    t_draw = None
                    if i in range(len(target_status_draw.draw_list)):
                        t_draw = target_status_draw.draw_list[i]
                    else:
                        t_draw = draw.NormalDraw()
                        t_draw.text = " " * int(self.width / 2 - 1)
                        t_draw.width = self.width / 2 - 1
                    character_status_draw_list.append((c_draw, t_draw))
            else:
                character_status_draw = see_character_info_panel.SeeCharacterStatusPanel(
                    character_data.cid, self.width, 6
                )
                character_status_draw_list = character_status_draw.draw_list
            for label in character_status_draw_list:
                if isinstance(label, tuple):
                    index = 0
                    for value in label:
                        if isinstance(value, list):
                            for value_draw in value:
                                value_draw.draw()
                        else:
                            value.line_feed = 0
                            value.draw()
                        if not index:
                            fix_draw = draw.NormalDraw()
                            fix_draw.width = 1
                            fix_draw.text = "|"
                            fix_draw.draw()
                            index = 1
                    line_feed.draw()
                elif isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()
            see_instruct_panel.draw()
            ask_list.extend(see_instruct_panel.return_list)
            flow_handle.askfor_all(ask_list)
            py_cmd.clr_cmd()


class SeeInstructPanel:
    """
    查看操作菜单面板
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        if cache.instruct_filter == {}:
            for instruct_type in game_config.config_instruct_type:
                cache.instruct_filter[instruct_type] = 0
            cache.instruct_filter[0] = 1

    def draw(self):
        """绘制操作菜单面板"""
        self.return_list = []
        line = draw.LineDraw("-.-", self.width)
        line.draw()
        fix_draw = draw.NormalDraw()
        fix_width = int(
            (self.width - int(self.width / len(cache.instruct_filter)) * len(cache.instruct_filter)) / 2
        )
        fix_draw.width = fix_width
        fix_draw.text = " " * fix_width
        fix_draw.draw()
        for now_type in cache.instruct_filter:
            now_config = game_config.config_instruct_type[now_type]
            if cache.instruct_filter[now_type]:
                now_button = draw.CenterButton(
                    f"[{now_config.name}]",
                    now_config.name,
                    self.width / len(cache.instruct_filter),
                    " ",
                    "onbutton",
                    "standard",
                    cmd_func=self.change_filter,
                    args=(now_type,),
                )
            else:
                now_button = draw.CenterButton(
                    f"[{now_config.name}]",
                    now_config.name,
                    self.width / len(cache.instruct_filter),
                    cmd_func=self.change_filter,
                    args=(now_type,),
                )
            now_button.width = int(self.width / len(cache.instruct_filter))
            self.return_list.append(now_button.return_text)
            now_button.draw()
        line_feed.draw()
        line = draw.LineDraw("~..", self.width)
        line.draw()
        now_instruct_list = []
        now_premise_data = {}
        for now_type in cache.instruct_filter:
            if cache.instruct_filter[now_type] and now_type in constant.instruct_type_data:
                for instruct in constant.instruct_type_data[now_type]:
                    premise_judge = 0
                    if instruct in constant.instruct_premise_data:
                        for premise in constant.instruct_premise_data[instruct]:
                            if premise in now_premise_data:
                                if now_premise_data[premise]:
                                    continue
                                premise_judge = 1
                                break
                            else:
                                now_premise_value = handle_premise.handle_premise(premise, 0)
                                now_premise_data[premise] = now_premise_value
                                if not now_premise_value:
                                    premise_judge = 1
                                    break
                    if premise_judge:
                        continue
                    now_instruct_list.append(instruct)
        now_instruct_list.sort()
        instruct_group = value_handle.list_of_groups(now_instruct_list, 5)
        now_draw_list = []
        for instruct_list in instruct_group:
            for instruct_id in instruct_list:
                instruct_name = constant.handle_instruct_name_data[instruct_id]
                id_text = text_handle.id_index(instruct_id)
                now_text = f"{id_text}{instruct_name}"
                now_draw = draw.LeftButton(
                    now_text,
                    str(instruct_id),
                    int(self.width / len(instruct_group)),
                    cmd_func=self.handle_instruct,
                    args=(instruct_id,),
                )
                now_draw_list.append(now_draw)
                self.return_list.append(now_draw.return_text)
        now_draw = panel.VerticalDrawTextListGroup(self.width)
        now_group = value_handle.list_of_groups(now_draw_list, 5)
        now_draw.draw_list = now_group
        now_draw.draw()

    def change_filter(self, now_type: int):
        """
        更改指令类型过滤状态
        Keyword arguments:
        now_type -- 指令类型
        """
        if cache.instruct_filter[now_type]:
            cache.instruct_filter[now_type] = 0
        else:
            cache.instruct_filter[now_type] = 1

    def handle_instruct(self, instruct_id: int):
        """
        处理玩家操作指令
        Keyword arguments:
        instruct_id -- 指令id
        """
        py_cmd.clr_cmd()
        handle_instruct.handle_instruct(instruct_id)
