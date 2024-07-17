from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, handle_premise, character_move
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

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


class All_Npc_Position_Panel:
    """
    总面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("干员位置一览")
        """ 当前绘制的食物类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """
        self.select_type = 0
        """ 当前筛选类型 """
        self.move_type = 0
        """ 当前移动类型 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("干员位置一览", self.width)

        draw_width = self.width / 3
        self.handle_panel = panel.PageHandlePanel([], FindDraw, 60, 3, self.width, 1, 1, 0)
        select_type_list = [_("不筛选"), _("筛选收藏干员(可在角色设置中收藏)"), _("筛选访客干员")]
        move_type_list = [_("召集到办公室"), _("召集到自己当前位置"), _("自己前去对方位置"), _("debug用对方智能跟随")]
        self.break_flag = False
        self.move_type = cache.all_npc_position_panel_move_type
        while 1:
            title_draw.draw()
            py_cmd.clr_cmd()
            npc_list,return_list = [],[]

            # 暂时去掉同时跟随干员数量的提示信息
            # info_draw = draw.NormalDraw()
            # follow_count = cache.character_data[0].pl_ability.follow_count
            # if not cache.debug_mode:
            #     info_draw.text = f"●当前最大同时跟随角色数量：{str(follow_count)}，跟随中的角色会带*\n\n"
            # else:
            #     info_draw.text = "●当前最大同时跟随角色数量：999(debug模式)，跟随中的角色会带*\n\n"
            # info_draw.width = self.width
            # info_draw.draw()

            # 全跟随按钮
            if cache.debug_mode:
                text = _("  [debug用一键全跟随]")
                name_draw = draw.LeftButton(text, text, self.width, cmd_func=self.call_all)
                name_draw.draw()
                line_feed.draw()
                line_feed.draw()
                return_list.append(name_draw.return_text)

            # 人员筛选
            info_text = _("选择人员筛选方式：")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = self.width
            info_draw.draw()
            for select_type_id in range(len(select_type_list)):
                if select_type_id == self.select_type:
                    select_type_text = f"▶{select_type_list[select_type_id]}          "
                    now_draw = draw.NormalDraw()
                    now_draw.text = select_type_text
                    now_draw.style = "gold_enrod"
                    now_draw.width = draw_width
                    now_draw.draw()
                else:
                    draw_text = f"  {select_type_list[select_type_id]}     "
                    now_draw = draw.LeftButton(
                        draw_text, select_type_list[select_type_id], len(draw_text) * 2, cmd_func=self.select_type_change, args=(select_type_id,)
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()

            # 移动类型切换按钮
            info_text = _("选择召集/移动方式：")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = self.width
            info_draw.draw()
            for move_type_id in range(len(move_type_list)):
                # 仅在debug模式下显示debug用对方智能跟随
                if move_type_id == 3 and not cache.debug_mode:
                    continue
                move_type_text = move_type_list[move_type_id]
                if move_type_id == self.move_type:
                    move_type_text = f"▶{move_type_text}          "
                    now_draw = draw.NormalDraw()
                    now_draw.text = move_type_text
                    now_draw.style = "gold_enrod"
                    now_draw.width = draw_width
                    now_draw.draw()
                else:
                    draw_text = f"  {move_type_text}     "
                    now_draw = draw.LeftButton(
                        draw_text, move_type_text, len(draw_text) * 2, cmd_func=self.move_type_change, args=(move_type_id,)
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line_feed.draw()

            # 遍历角色id
            chara_count = 0
            npc_id_got_list = sorted(cache.npc_id_got)
            for npc_id in npc_id_got_list:
                if npc_id != 0:
                    character_data = cache.character_data[npc_id]
                    # 收藏筛选
                    if self.select_type == 1 and character_data.chara_setting[2] != 1:
                        continue
                    # 访客筛选
                    if self.select_type == 2 and npc_id not in cache.rhodes_island.visitor_info:
                        continue
                    # npc_list.append(npc_id)

                    # 角色属性与信息
                    name = character_data.name
                    id = str(character_data.adv).rjust(4,'0')
                    scene_position = character_data.position.copy()
                    if normal_config.config_normal.language != "zh_CN":
                        for i in range(len(scene_position)):
                            scene_position[i] = _(scene_position[i])
                    scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
                    # 对于入口的特殊处理
                    if scene_position_str[-2] == "\\" and scene_position_str[-1] == "0":
                        scene_position_str = scene_position_str[:-2] + _("入口")
                    chara_count += 1

                    # 输出干员名字
                    now_draw_text = f"[{id}]{name}"
                    # 输出跟随信息
                    if character_data.sp_flag.is_follow == 1:
                        now_draw_text += _("(跟)")
                    # 输出访客信息
                    if npc_id in cache.rhodes_island.visitor_info:
                        now_draw_text += _("(访)")
                    # 输出地点信息
                    now_draw_text += f":{scene_position_str}   "

                    status_text = game_config.config_status[character_data.state].name
                    # 如果是在移动，则输出目的地
                    # BUG 需要查明在什么情况下会导致虽然在移动但是move_final_target为空
                    if status_text == _("移动") and len(character_data.behavior.move_final_target):
                        now_draw_text += _("移动目的地:{0}").format(character_data.behavior.move_final_target[-1])
                    # 否则输出状态
                    else:
                        now_draw_text += _("正在：{0}").format(status_text)

                    # 输出按钮
                    name_draw = draw.LeftButton(
                        now_draw_text, name, draw_width, cmd_func=self.move, args=(npc_id,)
                    )
                    name_draw.draw()
                    return_list.append(name_draw.return_text)

                    # 每行三个，如果是第三个，且当前不是最后一个则换行
                    if chara_count % 3 == 0 and chara_count != len(cache.npc_id_got):
                        line_feed.draw()

            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text or self.break_flag:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def call_all(self):
        """一键全跟随"""
        for npc_id in cache.npc_id_got:
            if npc_id != 0:
                character_data = cache.character_data[npc_id]
                character_data.sp_flag.is_follow = 1

    def move_type_change(self, new_type: int):
        """移动类型切换"""
        self.move_type = new_type
        cache.all_npc_position_panel_move_type = new_type

    def select_type_change(self, new_type: int):
        """筛选类型切换"""
        self.select_type = new_type

    def move(self, character_id: int):
        """移动"""

        line = draw.LineDraw("-", window_width)
        line.draw()
        character_data: game_type.Character = cache.character_data[character_id]
        now_draw = draw.NormalDraw()
        # 召集干员的情况
        if self.move_type != 2:
            if not handle_premise.handle_normal_24567(character_id):
                now_draw.text = _("***{0}状态异常，无法召集***\n").format(character_data.name)
            elif self.move_type == 0:
                character_data.sp_flag.is_follow = 3
                now_draw.text = character_data.name + _("收到了博士的信息，接下来会前往博士办公室\n")
            elif self.move_type == 1:
                character_data.sp_flag.is_follow = 4
                now_draw.text = character_data.name + _("收到了博士的信息，询问了博士的位置之后开始移动\n")
            elif self.move_type == 3:
                character_data.sp_flag.is_follow = 1
                now_draw.text = character_data.name + _("收到了博士的信息，开始智能跟随\n")
            now_draw.width = 1
            now_draw.draw()
        # 博士前往干员位置的情况
        else:
            while character_data.position != cache.character_data[0].position:
                target_position = character_data.position
                # target_scene_str = map_handle.get_map_system_path_str_for_list(target_scene)
                character_move.own_charcter_move(target_position)
                self.break_flag = True


class FindDraw:
    """
    显示可点击的NPC名字+位置按钮对象
    Keyword arguments:
    npc_id -- 干员角色编号
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, NPC_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.npc_id: int = NPC_id
        """ 干员角色编号 """
        self.draw_text: str = ""
        """ 名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        name_draw = draw.NormalDraw()
        # print("text :",text)

        character_data = cache.character_data[self.npc_id]
        name = character_data.name
        id = str(character_data.adv).rjust(4,'0')
        scene_position = character_data.position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        if scene_position_str[-2] == "\\" and scene_position_str[-1] == "0":
            scene_position_str = scene_position_str[:-2] + "入口"
        # scene_name = cache.scene_data[scene_position_str].scene_name
        # 输出干员名字
        now_draw_text = f"[{id}]{name}"
        # 输出跟随信息
        if character_data.sp_flag.is_follow == 1:
            now_draw_text += "*"
        # 输出地点信息
        now_draw_text += f":{scene_position_str}   "

        status_text = game_config.config_status[character_data.state].name
        # 如果是在移动，则输出目的地
        # BUG 需要查明在什么情况下会导致虽然在移动但是move_final_target为空
        if status_text == _("移动") and len(character_data.behavior.move_final_target):
            now_draw_text += _("移动目的地:{0}").format(character_data.behavior.move_final_target[-1])
        # 否则输出状态
        else:
            now_draw_text += _("正在：{0}").format(status_text)

        name_draw = draw.LeftButton(
            now_draw_text, self.button_return, self.width, cmd_func=self.see_call_list
        )
        self.draw_text = now_draw_text
        self.now_draw = name_draw
        """ 绘制的对象 """


    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_call_list(self):
        """点击后进行召集"""
        # title_draw = draw.TitleLineDraw(self.text, window_width)
        return_list = []
        # title_draw.draw()
        line = draw.LineDraw("-", window_width)
        line.draw()
        character_data: game_type.Character = cache.character_data[self.npc_id]
        now_draw = draw.NormalDraw()
        if not handle_premise.handle_normal_24567(self.npc_id):
            now_draw.text = _("***{0}状态异常，无法召集***\n").format(character_data.name)
        elif character_data.sp_flag.is_follow == 0:
            if cache.debug_mode:
                character_data.sp_flag.is_follow = 1
                now_draw.text = character_data.name + _("收到了博士的信息，询问了博士的位置之后开始移动\n")
            else:
                character_data.sp_flag.is_follow = 3
                now_draw.text = character_data.name + _("收到了博士的信息，接下来会前往博士办公室\n")

            # 去掉其他NPC的跟随
            # if not cache.debug_mode:
            #     for npc_id in cache.npc_id_got:
            #         if npc_id != 0 and npc_id != character_id:
            #             other_character_data = cache.character_data[npc_id]
            #             if other_character_data.sp_flag.is_follow:
            #                 other_character_data.sp_flag.is_follow = 0
            #                 now_draw.text += other_character_data.name + "退出跟随模式\n"
        elif character_data.sp_flag.is_follow == 1 and cache.debug_mode:
            character_data.sp_flag.is_follow = 3
            now_draw.text = character_data.name + _("收到了博士的信息，接下来会前往博士办公室\n")

        else:
            character_data.sp_flag.is_follow = 0
            now_draw.text = character_data.name + _("退出跟随模式\n")
        now_draw.width = 1
        now_draw.draw()
        # back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        # back_draw.draw()
        # line_feed.draw()
        # return_list.append(back_draw.return_text)
        # yrn = flow_handle.askfor_all(return_list)
        # if yrn == back_draw.return_text:
        #     break
