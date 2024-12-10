from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import game_info_panel, see_character_info_panel, dirty_panel, cloth_panel, group_sex_panel
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
from Script.Design import attr_text, map_handle, handle_instruct, handle_premise, cross_section_image, character_image, talk
from Script.Config import game_config
import logging, time

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

def judge_single_instruct_filter(instruct_id: int, now_premise_data: dict, now_type: int, use_type_filter_flag: bool = True):
    """
    判断单个指令是否通过过滤\n
    Keyword arguments：\n
    instruct_id -- 指令id\n
    now_premise_data -- 当前记录的前提数据\n
    now_type -- 当前指令类型\n
    use_sub_type -- 是否使用子类过滤\n
    Returns：\n
    bool -- 是否通过过滤\n
    now_premise_data -- 当前记录的前提数据\n
    """
    filter_judge = True
    # 如果该指令不存在，则置为存在
    if instruct_id not in cache.instruct_index_filter:
        cache.instruct_index_filter[instruct_id] = 1
    # 如果在过滤列表里，则过滤
    if not cache.instruct_index_filter[instruct_id]:
        filter_judge = False
    # H子类指令过滤
    if use_type_filter_flag and handle_premise.handle_is_h(0) and now_type == constant.InstructType.SEX:
        now_sub_type = constant.instruct_sub_type_data[instruct_id]
        if cache.instruct_sex_type_filter[now_sub_type] == 0:
            filter_judge = False
    # 前提判断
    if filter_judge:
        premise_judge = True
        if instruct_id in constant.instruct_premise_data:
            for premise in constant.instruct_premise_data[instruct_id]:
                if premise in now_premise_data:
                    if now_premise_data[premise]:
                        continue
                    premise_judge = False
                    break
                else:
                    now_premise_value = handle_premise.handle_premise(premise, 0)
                    now_premise_data[premise] = now_premise_value
                    if not now_premise_value:
                        premise_judge = False
                        break
        # 如果前提不满足，则过滤
        if not premise_judge:
            filter_judge = False
    # 如果是debug模式，则强制通过
    if cache.debug_mode:
        filter_judge = True

    return filter_judge, now_premise_data

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
        title_draw = draw.TitleLineDraw(_("场景"), self.width)
        while 1:
            if cache.now_panel_id != constant.Panel.IN_SCENE:
                break
            # 绘制的开始时间
            start_draw = time.time()
            # 和上一次主界面绘制之间的空行数量，由系统设置决定
            len_str = game_config.config_system_setting_option[1][cache.system_setting[1]]
            len_line = int(len_str[:1])
            for i in range(len_line):
                line_feed.draw()
            # 绘制标题
            title_draw.draw()
            # 玩家数据
            pl_character_data: game_type.Character = cache.character_data[0]
            # 场景数据
            scene_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]
            # 场景角色数据
            character_handle_panel = panel.PageHandlePanel(
                [],
                see_character_info_panel.SeeCharacterInfoByNameDrawInScene,
                20,
                10,
                self.width,
                1,
                0,
                999,
                null_button_text=pl_character_data.target_character_id,
            )
            character_set = scene_data.character_list.copy()
            character_set.remove(0) # 移除玩家自己
            if cache.is_collection:
                character_list = [i for i in character_set if i in pl_character_data.collection_character]
            else:
                character_list = list(character_set)
            character_handle_panel.text_list = character_list

            # if pl_character_data.dead:
            #     cache.wframe_mouse.w_frame_skip_wait_mouse = 0
            #     now_draw = draw.LineFeedWaitDraw()
            #     now_draw.text = _("已死亡！")
            #     now_draw.width = self.width
            #     now_draw.draw()
            #     continue
            # print("character_handle_panel.text_list :",character_handle_panel.text_list)
            # 如果玩家的交互对象不在场景中，则将交互对象设为自己
            if pl_character_data.target_character_id not in scene_data.character_list:
                pl_character_data.target_character_id = 0
            # 如果没有交互对象，而且场景中有角色，则将交互对象设为场景中的第一个角色
            if not pl_character_data.target_character_id and len(character_list):
                pl_character_data.target_character_id = character_list[0]
            # 游戏时间
            game_time_draw = game_info_panel.GameTimeInfoPanel(self.width / 2)
            game_time_draw.now_draw.width = len(game_time_draw)
            game_time_draw.draw()
            # 当前位置
            position_text = attr_text.get_scene_path_text(pl_character_data.position)
            now_position_text = _("当前位置:") + position_text
            now_position_draw = draw.NormalDraw()
            now_position_draw.text = now_position_text
            now_position_draw.draw()
            line_feed.draw()

            # 当前位置的角色一览
            meet_draw = draw.NormalDraw()
            meet_draw.text = _("当前位置的角色一览:    ")
            # meet_draw.width = self.width
            cache.wframe_mouse.w_frame_skip_wait_mouse = 0
            character_handle_panel.null_button_text = pl_character_data.target_character_id

            # 开始绘制主界面标题栏
            ask_list = []
            if len(character_list) and pl_character_data.target_character_id not in character_list:
                pl_character_data.target_character_id = character_list[0]
            if not len(character_list):
                pl_character_data.target_character_id = 0
            if len(character_list):
                meet_draw.draw()
                character_handle_panel.update()
                character_handle_panel.draw()
                ask_list.extend(character_handle_panel.return_list)
                line_draw = draw.LineDraw("-.-", self.width)
                line_draw.draw()

                # 收起与展开按钮
                return_text = self.draw_show_and_hide_button(0, _("收起状态栏"), _("展开状态栏"))
                ask_list.append(return_text)
                return_text = self.draw_show_and_hide_button(1, _("收起服装栏"), _("展开服装栏"))
                ask_list.append(return_text)
                return_text = self.draw_show_and_hide_button(2, _("收起身体栏"), _("展开身体栏"))
                ask_list.append(return_text)
                return_text = self.draw_show_and_hide_button(4, _("收起图片栏"), _("展开图片栏"))
                ask_list.append(return_text)
                line_feed.draw()
                line_draw = draw.LineDraw(".--", self.width)
                line_draw.draw()

            now_draw_character_list = []
            now_draw_character_list = character_list
            # （已废弃）有bug的人物绘制列表
            # for page_draw in character_handle_panel.draw_list:
            #     if "character_id" in page_draw.__dict__:
            #         now_draw_character_list.append(page_draw.character_id)
            # ↓角色信息面板↓#
            character_info_draw_list = []
            character_head_draw = see_character_info_panel.CharacterInfoHead(
                pl_character_data.cid, self.width
            )
            target_head_draw = see_character_info_panel.CharacterInfoHead(
                pl_character_data.target_character_id, self.width
            )
            character_head_draw_list = [y for x in character_head_draw.draw_list for y in x]
            target_head_draw_list = [y for x in target_head_draw.draw_list for y in x]
            for value_tuple in character_head_draw_list:
                value_tuple.draw()
            line_feed.draw()
            # 只有在有交互对象的情况下才绘制交互对象
            if pl_character_data.target_character_id:
                for value_tuple in target_head_draw_list:
                    value_tuple.draw()
                line_feed.draw()
            # character_clothing_draw_list = []
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
            # ↓以下为状态栏的内容↓#
            character_status_draw_list = []
            if pl_character_data.target_character_id and cache.scene_panel_show[0]:
                character_status_draw = see_character_info_panel.SeeCharacterStatusPanel(
                    pl_character_data.cid, self.width / 2, 7, 0, 0
                )
                target_status_draw = see_character_info_panel.SeeCharacterStatusPanel(
                    pl_character_data.target_character_id, self.width, 7, 0, 0
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
                    character_status_draw_list = target_status_draw.draw_list
                    # character_status_draw_list.append((t_draw))
            # else:
            # character_status_draw = see_character_info_panel.SeeCharacterStatusPanel(
            #     character_data.cid, self.width, 9, 0
            # )
            # character_status_draw_list = character_status_draw.draw_list
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

            # ↓以下为服装栏的内容↓#
            # 移动至服装文件中
            if cache.scene_panel_show[1] and pl_character_data.target_character_id:
                character_cloth_draw = cloth_panel.SeeCharacterClothPanel(
                    pl_character_data.cid, self.width, 20, 0, 0
                )
                character_cloth_draw.draw()

            # ↓以下为身体栏的内容↓#
            if cache.scene_panel_show[2] and pl_character_data.target_character_id:
                character_body_draw = dirty_panel.SeeCharacterBodyPanel(
                    pl_character_data.cid, self.width, 9, 0, 0
                )
                character_body_draw.draw()

            # ↓以下为群交栏的内容↓#
            if cache.group_sex_mode:
                character_group_sex_draw = group_sex_panel.SeeGroupSexInfoPanel(
                    pl_character_data.cid, self.width, 9, 0, 0
                )
                character_group_sex_draw.draw()

            # 以下为图片面板#
            if len(character_list) and cache.scene_panel_show[4]:
                line_draw = draw.LineDraw("-.-", self.width)
                line_draw.draw()
                # fix_draw = draw.CharaDraw()
                # fix_draw.width = 10
                # fix_draw.set(1)
                # fix_draw.draw()
                # line_feed.draw()
                character_image_list_draw = CharacterImageListDraw(self.width, now_draw_character_list)
                character_image_list_draw.draw()
                ask_list.extend(character_image_list_draw.return_list)
                """
                character_image_list=character_list
                character_image_list.reverse()
                for image_cid in character_image_list:
                    image_character_data = cache.character_data[image_cid]
                    flow_handle.print_image_cmd(image_character_data.name,"立绘按钮")
                """
                line_feed.draw()
            # 以下为指令面板#
            mid_draw = time.time()
            logging.debug(f'————————')
            logging.debug(f'截止到指令面板绘制前总时间为{mid_draw - start_draw}')
            see_instruct_panel = SeeInstructPanel(self.width)
            see_instruct_panel.draw()
            ask_list.extend(see_instruct_panel.return_list)
            logging.debug(f'————————')
            logging.debug(f'指令外，ask_list = {ask_list}')
            flow_handle.askfor_all(ask_list)
            mid_3_draw = time.time()
            logging.debug(f'————————')
            logging.debug(f'指令外，中间时间3号，截至flow_handle总时间为 {mid_3_draw - mid_draw}')
            py_cmd.clr_cmd()
            end_draw = time.time()
            logging.debug(f'指令部分绘制总时间为{end_draw - mid_draw}')

    def draw_show_and_hide_button(self, index, hide_text, show_text):
        """绘制显示与隐藏按钮"""
        if cache.scene_panel_show[index]:
            now_button = draw.CenterButton(
                f" [{hide_text}] ",
                hide_text,
                (len(hide_text) + 4) * 2,
                cmd_func=self.show_and_hide_panel,
                args=(index,),
            )
        else:
            now_button = draw.CenterButton(
                f" [{show_text}] ",
                show_text,
                (len(show_text) + 4) * 2,
                cmd_func=self.show_and_hide_panel,
                args=(index,),
            )
        now_button.draw()
        return now_button.return_text

    def show_and_hide_panel(self, index):
        """显示与隐藏面板栏"""
        if cache.scene_panel_show[index]:
            cache.scene_panel_show[index] = False
        else:
            cache.scene_panel_show[index] = True



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

        # 初始化指令类型过滤
        if cache.instruct_type_filter == {}:
            cache.instruct_type_filter[0] = 1
            cache.instruct_type_filter[1] = 1
            cache.instruct_type_filter[2] = 1
            cache.instruct_type_filter[3] = 1
            cache.instruct_type_filter[4] = 1
        for instruct_type in game_config.config_instruct_type:
            if instruct_type not in cache.instruct_type_filter:
                cache.instruct_type_filter[instruct_type] = 0
        cache.instruct_type_filter[6] = 1

        # 初始化性爱子类类型过滤
        for instruct_type in game_config.config_instruct_sex_type:
            if instruct_type not in cache.instruct_sex_type_filter:
                if instruct_type == 0:
                    cache.instruct_sex_type_filter[instruct_type] = 1
                else:
                    cache.instruct_sex_type_filter[instruct_type] = 0

        # 初始化命令过滤
        if cache.instruct_index_filter == {}:
            for now_type in cache.instruct_type_filter:
                for instruct in constant.instruct_type_data[now_type]:
                    cache.instruct_index_filter[instruct] = 1

    def draw(self):
        """绘制操作菜单面板"""
        start_instruct = time.time()
        self.return_list = []

        line = draw.LineDraw("-.-", self.width)
        line.draw()
        fix_draw = draw.NormalDraw()
        # 根据是否是H模式，进行指令类型过滤相关变量的区分
        if handle_premise.handle_is_h(0):
            instruct_type_len = len(cache.instruct_sex_type_filter) + 1
            now_instruct_type_list = cache.instruct_sex_type_filter
            now_instruct_config = game_config.config_instruct_sex_type
        else:
            instruct_type_len = len(cache.instruct_type_filter) - 1
            now_instruct_type_list = cache.instruct_type_filter
            now_instruct_config = game_config.config_instruct_type
        # 排版修正用的宽度
        fix_width = int(
            (self.width - int(self.width / instruct_type_len) * instruct_type_len) / 2
        )
        fix_draw.width = fix_width
        fix_draw.text = " " * fix_width
        fix_draw.draw()
        for now_type in now_instruct_type_list:
            # 正常模式下，跳过系统类和性爱类的大类选择按钮
            if not handle_premise.handle_is_h(0):
                if now_type == constant.InstructType.SYSTEM:
                    continue
                if now_type == constant.InstructType.SEX:
                    continue
            now_config = now_instruct_config[now_type]
            # 已选择的指令类型变成对应颜色
            if now_instruct_type_list[now_type]:
                now_button = draw.CenterButton(
                    f"[{now_config.name}]",
                    now_config.name,
                    self.width / (instruct_type_len - 1),
                    " ",
                    now_instruct_config[now_type].color,
                    "standard",
                    cmd_func=self.change_filter,
                    args=(now_type,),
                )
            else:
                now_button = draw.CenterButton(
                    f"[{now_config.name}]",
                    now_config.name,
                    self.width / (instruct_type_len - 1),
                    normal_style = "deep_gray",
                    cmd_func=self.change_filter,
                    args=(now_type,),
                )
            now_button.width = int(self.width / (instruct_type_len - 1))
            self.return_list.append(now_button.return_text)
            now_button.draw()

        # 如果交互对象是临盆、产后或婴儿的话，则在常规指令类里不显示性骚扰和H类指令
        if handle_premise.handle_t_parturient_1(0) or handle_premise.handle_t_postpartum_1(0) or handle_premise.handle_t_baby_1(0):
            cache.instruct_type_filter[5] = 0
            cache.instruct_type_filter[6] = 0

        line_feed.draw()
        line = draw.LineDraw("~..", self.width)
        line.draw()
        now_instruct_list = []
        now_premise_data = {}
        # 遍历指令过滤
        for now_type in cache.instruct_type_filter:
            # 当前类没有开启的指令则过滤
            if not cache.instruct_type_filter[now_type]:
                continue
            # 需要是注册过的指令类型，或者是系统指令
            if now_type in constant.instruct_type_data or now_type == constant.InstructType.SYSTEM:
                for instruct in constant.instruct_type_data[now_type]:
                    # 检测指令是否通过过滤
                    filter_judge, now_premise_data = judge_single_instruct_filter(instruct, now_premise_data, now_type)
                    if filter_judge:
                        now_instruct_list.append(instruct)
        now_instruct_list.sort()
        instruct_group = value_handle.list_of_groups(now_instruct_list, 5)
        now_draw_list = []
        system_draw_list = []
        # 遍历指令绘制
        for instruct_list in instruct_group:
            for instruct_id in instruct_list:
                instruct_name = constant.handle_instruct_name_data[instruct_id]
                id_text = text_handle.id_index(instruct_id)
                now_text = f"{id_text}{instruct_name}"
                now_draw = draw.LeftButton(
                    now_text,
                    str(instruct_id),
                    int(self.width / 5),
                    cmd_func=self.handle_instruct,
                    args=(instruct_id,),
                )
                # 根据指令类型赋予不同的颜色
                for instruct_type in constant.instruct_type_data:
                    if instruct_id in constant.instruct_type_data[instruct_type]:
                        now_draw.normal_style = game_config.config_instruct_type[instruct_type].color
                        break
                # 如果是H模式，则单独读取H子类的颜色
                if handle_premise.handle_is_h(0):
                    now_sub_type = constant.instruct_sub_type_data[instruct_id]
                    now_draw.normal_style = game_config.config_instruct_sex_type[now_sub_type].color
                # 系统指令单独加入系统指令列表
                if instruct_id in constant.instruct_type_data[constant.InstructType.SYSTEM]:
                    system_draw_list.append(now_draw)
                else:
                    now_draw_list.append(now_draw)
                self.return_list.append(now_draw.return_text)
        # 角色自定义特殊指令检测与绘制
        from Script.UI.Panel import event_option_panel
        len_son_event_list, son_event_list = event_option_panel.get_target_chara_diy_instruct(0)
        if len_son_event_list:
            count = 0
            for event_id in son_event_list:
                count += 1
                # 获取事件数据
                event_data = game_config.config_event[event_id]
                pl_character_data = cache.character_data[0]
                target_character_data = cache.character_data[pl_character_data.target_character_id]
                chara_adv = target_character_data.adv
                # 获取选项文本
                option_text = event_data.text.split("|")[0]
                option_text = talk.code_text_to_draw_text(option_text, 0)
                now_text = f"[{chara_adv}_{count}]{option_text}"
                return_text = f"{chara_adv}_{count}"
                # 绘制按钮
                now_draw = draw.LeftButton(
                    now_text,
                    return_text,
                    int(self.width / 5),
                    cmd_func=self.handle_chara_diy_instruct,
                    args=(event_id,),
                )
                # 检查是否要使用口上颜色
                if target_character_data.text_color:
                    now_draw.normal_style = target_character_data.name
                now_draw_list.append(now_draw)
                self.return_list.append(now_draw.return_text)
        now_draw = panel.DrawTextListPanel()
        now_draw.set(now_draw_list, self.width, 5)
        # now_draw = panel.VerticalDrawTextListGroup(self.width)
        # now_group = value_handle.list_of_groups(now_draw_list, 5)
        # now_draw.draw_list = now_group
        now_draw.draw()
        line_feed.draw()
        line = draw.LineDraw("-.-", self.width)
        line.draw()
        system_draw = panel.DrawTextListPanel()
        system_draw.set(system_draw_list, self.width, 5)
        system_draw.draw()

    def change_filter(self, now_type: int):
        """
        更改指令类型过滤状态
        Keyword arguments:
        now_type -- 指令类型
        """
        if handle_premise.handle_is_h(0):
            if cache.instruct_sex_type_filter[now_type]:
                cache.instruct_sex_type_filter[now_type] = 0
            else:
                cache.instruct_sex_type_filter[now_type] = 1
        else:
            if cache.instruct_type_filter[now_type]:
                cache.instruct_type_filter[now_type] = 0
            else:
                cache.instruct_type_filter[now_type] = 1

    def handle_instruct(self, instruct_id: int):
        """
        处理玩家操作指令
        Keyword arguments:
        instruct_id -- 指令id
        """
        py_cmd.clr_cmd()
        # 指令名称绘制
        instruct_name = constant.handle_instruct_name_data[instruct_id]
        now_draw_1 = draw.NormalDraw()
        now_draw_1.text = f"{instruct_name}"
        # 如果是重复指令，则加上连续标记
        if len(cache.pl_pre_status_instruce) >= 2:
            if cache.pl_pre_status_instruce[-1] == cache.pl_pre_status_instruce[-2]:
                now_draw_1.text += _("(连续)")
        now_draw_1.text += "\n"
        now_draw_1.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        # 指令结算
        handle_instruct.handle_instruct(instruct_id)

    def handle_chara_diy_instruct(self, event_id: str):
        """
        处理角色自定义指令
        Keyword arguments:
        event_id -- 事件id
        """
        event_data = game_config.config_event[event_id]
        py_cmd.clr_cmd()
        # 指令名称绘制
        option_text = event_data.text.split("|")[0]
        option_text = talk.code_text_to_draw_text(option_text, 0)
        instruct_name = option_text
        now_draw_1 = draw.NormalDraw()
        now_draw_1.text = f"{instruct_name}"
        # 如果是重复指令，则加上连续标记
        if len(cache.pl_pre_status_instruce) >= 2:
            if cache.pl_pre_status_instruce[-1] == cache.pl_pre_status_instruce[-2]:
                now_draw_1.text += _("(连续)")
        now_draw_1.text += "\n"
        now_draw_1.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        # 指令结算
        pl_character_data = cache.character_data[0]
        pl_character_data.event.event_id = event_id
        pl_character_data.event.chara_diy_event_flag = True
        handle_instruct.handle_instruct(constant.Instruct.CHARA_DIY_INSTRUCT)


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
