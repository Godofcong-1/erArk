from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import game_info_panel, see_character_info_panel, dirty_panel, cloth_panel, see_instruct_panel, chara_image_list_panel, character_info_head
from Script.Core import (
    get_text,
    cache_control,
    game_type,
    flow_handle,
    constant,
    py_cmd,
)
from Script.Design import attr_text, map_handle, handle_premise
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
        )
        while 1:
            if cache.now_panel_id != constant.Panel.IN_SCENE:
                break
            # web模式下清屏
            if cache.web_mode:
                from Script.Core import io_init
                io_init.clear_screen()
                io_init.clear_order()
            # 绘制的开始时间
            start_draw = time.time()
            # 和上一次主界面绘制之间的空行数量，由系统设置决定
            len_str = game_config.config_draw_setting_option[1][cache.all_system_setting.draw_setting[1]]
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
            character_handle_panel.null_button_text=pl_character_data.target_character_id
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
            # 游戏时间
            game_time_draw = game_info_panel.GameTimeInfoPanel(self.width / 2)
            # game_time_draw.now_draw.width = len(game_time_draw)
            game_time_draw.draw()
            # 当前位置
            position_text = attr_text.get_scene_path_text(pl_character_data.position)
            if handle_premise.handle_place_door_close(0):
                position_text += _("(锁)")
            now_position_text = _("当前位置:") + position_text
            now_position_draw = draw.NormalDraw()
            now_position_draw.text = now_position_text
            now_position_draw.draw()
            line_feed.draw()

            # 当前位置的角色一览
            meet_draw = draw.NormalDraw()
            meet_draw.text = _("当前位置的角色一览:    ")
            # 如果角色数量大于9个人，则换行
            if len(character_list) > 9:
                meet_draw.text += "\n"
            # meet_draw.width = self.width
            cache.wframe_mouse.w_frame_skip_wait_mouse = 0
            character_handle_panel.null_button_text = pl_character_data.target_character_id

            # 交互对象的处理
            # 如果场景中有NPC角色，玩家的交互对象不是自己，也不在场景中，且则将交互对象设为场景中的第一个角色
            if len(character_list) and pl_character_data.target_character_id != 0 and pl_character_data.target_character_id not in character_list:
                pl_character_data.target_character_id = character_list[0]
            # 如果场景中有角色，交互对象不在场景中，刚移动到一个新地点，则将交互对象设为场景中的第一个角色
            elif (
                len(character_list) and
                pl_character_data.target_character_id not in character_list and
                len(cache.pl_pre_behavior_instruce) and
                cache.pl_pre_behavior_instruce[-1] == constant.Behavior.MOVE
                ):
                pl_character_data.target_character_id = character_list[0]
            # 如果场景中没有NPC角色，则将交互对象设为自己
            elif not len(character_list):
                pl_character_data.target_character_id = 0

            # 开始绘制主界面标题栏
            ask_list = []
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
                return_text = self.draw_show_and_hide_button(5, _("收起详细污浊"), _("展开详细污浊"))
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
            character_head_draw = character_info_head.CharacterInfoHead(
                pl_character_data.cid, self.width
            )
            ask_list.extend(character_head_draw.return_list)
            target_head_draw = character_info_head.CharacterInfoHead(
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
            if cache.scene_panel_show[1] and pl_character_data.target_character_id:
                # 如果是在H中，则切换为按钮型的点选服装穿脱面板
                if handle_premise.handle_is_h(0):
                    character_cloth_draw = cloth_panel.SwitchCharacterClothPanel(
                        pl_character_data.cid, self.width, 20, 0, 0
                    )
                # 否则为正常文本绘制服装面板
                else:
                    character_cloth_draw = cloth_panel.SeeCharacterClothPanel(
                        pl_character_data.cid, self.width, 20, 0, 0
                    )
                character_cloth_draw.draw()
                ask_list.extend(character_cloth_draw.return_list)

            # ↓以下为身体栏的内容↓#
            if cache.scene_panel_show[2] and pl_character_data.target_character_id:
                character_body_draw = dirty_panel.SeeCharacterBodyPanel(
                    pl_character_data.cid, self.width, 9, 0, 0
                )
                character_body_draw.draw()

            # ↓以下为群交栏的内容↓#
            if cache.group_sex_mode:
                from Script.System.Sex_System import group_sex_panel
                character_group_sex_draw = group_sex_panel.SeeGroupSexInfoPanel(
                    pl_character_data.cid, self.width, 9, 0, 0
                )
                character_group_sex_draw.draw()

            # ↓以下为隐奸栏的内容↓#
            if handle_premise.handle_hidden_sex_mode_ge_1(0):
                from Script.System.Sex_System import hidden_sex_panel
                character_hidden_sex_draw = hidden_sex_panel.See_Hidden_Sex_InfoPanel(
                    pl_character_data.cid, self.width, 9, 0, 0
                )
                character_hidden_sex_draw.draw()

            # 以下为图片面板#
            if len(character_list) and cache.scene_panel_show[4]:
                line_draw = draw.LineDraw("-.-", self.width)
                line_draw.draw()
                # fix_draw = draw.CharaDraw()
                # fix_draw.width = 10
                # fix_draw.set(1)
                # fix_draw.draw()
                # line_feed.draw()
                character_image_list_draw = chara_image_list_panel.CharacterImageListDraw(self.width, now_draw_character_list)
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
            instruct_panel = see_instruct_panel.SeeInstructPanel(self.width)
            instruct_panel.draw()
            ask_list.extend(instruct_panel.return_list)
            logging.debug(f'————————')
            logging.debug(f'指令外，ask_list = {ask_list}')
            flow_handle.askfor_all(ask_list)
            mid_3_draw = time.time()
            logging.debug(f'————————')
            logging.debug(f'指令外，中间时间3号，截至flow_handle总时间为 {mid_3_draw - mid_draw}')
            py_cmd.clr_cmd()
            end_draw = time.time()
            logging.debug(f'指令部分绘制总时间为{end_draw - mid_draw}')

    def draw_show_and_hide_button(self, index: int, hide_text: str, show_text: str) -> str:
        """
        根据索引绘制显示或隐藏按钮
        参数:
            index (int): 面板索引
            hide_text (str): 隐藏按钮文本
            show_text (str): 显示按钮文本
        返回:
            str: 按钮返回文本
        功能:
            根据当前状态绘制对应的按钮，并返回按钮执行时的返回文本
        """
        # 判断当前面板状态（详细污浊单独处理）
        condition = cache.all_system_setting.draw_setting[10] if index == 5 else cache.scene_panel_show[index]
        # 根据状态确定按钮显示文本
        button_text = hide_text if condition else show_text
        # 计算按钮宽度，宽度与文本长度相关
        button_width = (len(button_text) + 4) * 2
        # 创建并绘制中心按钮对象
        now_button = draw.CenterButton(
            f" [{button_text}] ",
            button_text,
            button_width,
            cmd_func=self.show_and_hide_panel,
            args=(index,),
        )
        now_button.draw()
        return now_button.return_text

    def show_and_hide_panel(self, index: int) -> None:
        """
        根据索引显示或隐藏面板栏
        参数:
            index (int): 面板索引
        返回:
            None
        功能:
            切换相应面板的显示状态
        """
        # 切换面板状态（详细污浊单独处理）
        if index == 5:
            cache.all_system_setting.draw_setting[10] = not cache.all_system_setting.draw_setting[10]
        else:
            cache.scene_panel_show[index] = not cache.scene_panel_show[index]
