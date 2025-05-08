from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.Design import map_handle, handle_premise
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
        self.handle_panel: panel.PageHandlePanel = panel.PageHandlePanel([], MoveSonPanel, 60, 3, window_width, 1, 0, 0)
        """ 当前名字列表控制面板 """
        self.select_type = 0
        """ 当前筛选类型 """
        self.name_search = ""
        """ 当前搜索的名字 """
        self.move_type = 0
        """ 当前移动类型 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("干员位置一览", self.width)

        # 非中文则每行只显示两个
        if normal_config.config_normal.language != "zh_CN":
            self.handle_panel: panel.PageHandlePanel = panel.PageHandlePanel([], MoveSonPanel, 40, 2, window_width, 1, 0, 0)
        select_type_list = [_("不筛选"), _("筛选收藏干员(可在角色设置中收藏)"), _("筛选访客干员"), _("筛选未陷落干员"), _("筛选已陷落干员"), _("按名称筛选"), _("筛选同区块干员"), _("筛选无意识干员")]
        move_type_list = [_("召集到办公室"), _("召集到自己当前位置"), _("自己前去对方位置"), _("debug用对方智能跟随")]
        self.break_flag = False
        # 读取缓存中的筛选与移动类型
        self.select_type = cache.all_npc_position_panel_select_type
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
            # info_draw.width = self.width
            info_draw.draw()
            for select_type_id in range(len(select_type_list)):
                # 每五个换行
                if select_type_id % 5 == 0 and select_type_id != 0:
                    line_feed.draw()
                    empty_draw = draw.NormalDraw()
                    empty_draw.text = "  " * len(info_text)
                    # empty_draw.width = self.width
                    empty_draw.draw()
                # 已选中的为高亮显示
                if select_type_id == self.select_type:
                    select_type_text = f"▶{select_type_list[select_type_id]}          "
                    if select_type_id == 5:
                        select_type_text = f"▶{select_type_list[select_type_id]}:{self.name_search}          "
                    now_draw = draw.NormalDraw()
                    now_draw.text = select_type_text
                    now_draw.style = "gold_enrod"
                    # now_draw.width = self.width / 3
                    now_draw.draw()
                # 未选中的为按钮
                else:
                    draw_text = f"  {select_type_list[select_type_id]}    "
                    now_draw_width = min(len(draw_text) * 2, self.width / 2.5)
                    now_draw = draw.LeftButton(
                        draw_text, select_type_list[select_type_id], now_draw_width, cmd_func=self.select_type_change, args=(select_type_id,)
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()

            # 移动类型切换按钮
            info_text = _("选择召集/移动方式：")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            # info_draw.width = self.width
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
                    # now_draw.width = self.width / 3
                    now_draw.draw()
                else:
                    draw_text = f"  {move_type_text}  "
                    now_draw_width = min(len(draw_text) * 2, self.width / 3)
                    now_draw = draw.LeftButton(
                        draw_text, move_type_text, now_draw_width, cmd_func=self.move_type_change, args=(move_type_id,)
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line_feed.draw()

            # 遍历角色id
            npc_id_got_list = sorted(cache.npc_id_got)
            final_list = []
            for npc_id in npc_id_got_list:
                if npc_id != 0:
                    character_data = cache.character_data[npc_id]
                    if self.select_type > 0:
                        # 收藏筛选
                        if self.select_type == 1 and character_data.chara_setting[2] != 1:
                            continue
                        # 访客筛选
                        elif self.select_type == 2 and npc_id not in cache.rhodes_island.visitor_info:
                            continue
                        # 未陷落筛选
                        elif self.select_type == 3 and handle_premise.handle_self_fall(npc_id):
                            continue
                        # 已陷落筛选
                        elif self.select_type == 4 and handle_premise.handle_self_not_fall(npc_id):
                            continue
                        # 姓名筛选
                        elif self.select_type == 5 and self.name_search not in character_data.name:
                            continue
                        # 同区块筛选
                        elif self.select_type == 6 and not handle_premise.handle_in_player_zone(npc_id):
                            continue
                        # 无意识筛选
                        elif self.select_type == 7 and handle_premise.handle_unconscious_flag_0(npc_id):
                            continue
                    # 加入列表
                    final_list.append([npc_id, self.move_type])

            # 生成子面板
            self.handle_panel.text_list = final_list
            self.handle_panel.update()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            # 选择玩家移动时，也跳出循环
            if yrn == back_draw.return_text or (yrn in self.handle_panel.return_list and yrn not in {'0', '1'} and self.move_type == 2):
                # cache.now_panel_id = constant.Panel.IN_SCENE
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
        cache.all_npc_position_panel_select_type = new_type
        if new_type == 5:
            ask_name_panel = panel.AskForOneMessage()
            ask_name_panel.set(_("输入要筛选的关键词"), 10)
            now_name = ask_name_panel.draw()
            self.name_search = now_name
            cache.all_npc_position_panel_select_type = 0


class MoveSonPanel:
    """
    移动子面板对象
    Keyword arguments:
    text_list -- 文本列表，0为角色id，1为移动类型
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text_list: list, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.chara_id: int = text_list[0]
        """ 角色id """
        self.move_type: int = text_list[1]
        """ 移动类型 """
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

        character_data: game_type.Character = cache.character_data[self.chara_id]

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

        # 输出干员名字
        now_draw_text = f"[{id}]{name}"
        # 输出跟随信息
        if character_data.sp_flag.is_follow == 1:
            now_draw_text += _("(跟)")
        # 输出访客信息
        if self.chara_id in cache.rhodes_island.visitor_info:
            now_draw_text += _("(访)")
        # 输出地点信息
        now_draw_text += f":{scene_position_str}   "

        status_text = game_config.config_behavior[character_data.state].name
        # 如果是在移动，则输出目的地
        # BUG 需要查明在什么情况下会导致虽然在移动但是move_final_target为空
        if status_text == _("移动") and len(character_data.behavior.move_final_target):
            now_draw_text += _("移动目的地:{0}").format(character_data.behavior.move_final_target[-1])
        # 否则输出状态
        else:
            now_draw_text += _("正在：{0}").format(status_text)

        # 如果有口上颜色的话，使用口上颜色
        if character_data.text_color:
            now_style = character_data.name
        # 否则使用标准颜色
        else:
            now_style = "standard"

        # 输出按钮
        name_draw = draw.LeftButton(
            now_draw_text, name, self.width, cmd_func=self.move, args=(self.chara_id,)
        )
        name_draw.normal_style = now_style
        self.button_return = name_draw.return_text
        self.now_draw = name_draw

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def move(self, character_id: int):
        """移动"""
        from Script.Design import character_move

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
            pre_position = cache.character_data[0].position
            while character_data.position != cache.character_data[0].position:
                target_position = character_data.position
                # target_scene_str = map_handle.get_map_system_path_str_for_list(target_scene)
                character_move.own_charcter_move(target_position)
                # 防止博士因某些原因无法移动，导致死循环，如果博士位置不变则跳出
                if pre_position == cache.character_data[0].position:
                    break
                else:
                    pre_position = cache.character_data[0].position
            # 如果该干员在玩家的位置，那么玩家的交互对象设为该干员
            if character_data.position == cache.character_data[0].position:
                cache.character_data[0].target_character_id = character_id
