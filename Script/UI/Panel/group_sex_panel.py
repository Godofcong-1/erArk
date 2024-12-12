from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    constant,
    flow_handle
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, handle_premise, map_handle

panel_info_data = {}

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

# 部位英语对中文的字典
body_part_name_dict = {
    "mouth": _("嘴"),
    "L_hand": _("左手"),
    "R_hand": _("右手"),
    "penis": _("阴茎"),
    "anal": _("肛门"),
}

def group_sex_settle(
        character_id: int,
        target_character_id: int,
        state_id: int,
):
    """
    群交结算
    Keyword arguments:
    character_id -- 角色id
    target_character_id -- 目标角色id
    """
    # 如果是非群交模式，则返回
    if not cache.group_sex_mode:
        return
    # 非玩家或无交互对象返回
    if character_id != 0 or target_character_id == character_id:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    now_template_data = character_data.h_state.group_sex_body_template_dict["A"]
    # 如果当前群交模板已锁死，则返回
    if character_data.h_state.group_sex_lock_flag:
        return
    # 阴茎插入
    if state_id in game_config.config_status_id_list_of_group_sex_body_part[_("插入")]:
        now_template_data[0]["penis"] = [target_character_id, state_id]
        now_template_data[1] = [[-1], -1]
    # 阴茎侍奉
    elif state_id in game_config.config_status_id_list_of_group_sex_body_part[_("侍奉")]:
        now_template_data[0]["penis"] = [-1, -1]
        # 如果新指令，则重置数据
        if now_template_data[1][1] != state_id:
            now_template_data[1] = [[target_character_id], state_id]
        # 否则则只将角色id加进角色列表里
        elif target_character_id not in now_template_data[1][0]:
            now_template_data[1][0].append(target_character_id)
    # 口
    elif state_id in game_config.config_status_id_list_of_group_sex_body_part[_("口")]:
        now_template_data[0]["mouth"] = [target_character_id, state_id]
    # 手
    elif state_id in game_config.config_status_id_list_of_group_sex_body_part[_("手")]:
        # 如果L是空的，或当前对象是L对象，则赋给L
        if now_template_data[0]["L_hand"][1] == -1 or now_template_data[0]["L_hand"][0] == target_character_id:
            now_template_data[0]["L_hand"] = [target_character_id, state_id]
        # R同理
        elif now_template_data[0]["R_hand"][1] == -1 or now_template_data[0]["R_hand"][0] == target_character_id:
            now_template_data[0]["R_hand"] = [target_character_id, state_id]
        # 否则，全部更新，左等于右，右等于新
        else:
            now_template_data[0]["L_hand"] = now_template_data[0]["R_hand"]
            now_template_data[0]["R_hand"] = [target_character_id, state_id]
    # 肛
    elif state_id in game_config.config_status_id_list_of_group_sex_body_part[_("肛")]:
        now_template_data[0]["anal"] = [target_character_id, state_id]

    # 特殊指令特殊处理
    status_data = game_config.config_status[state_id]
    if status_data.name == _("六九式"):
        now_template_data[0]["mouth"] = [target_character_id, state_id]
        now_template_data[1] = [[target_character_id], state_id]


def count_group_sex_instruct_list():
    """
    统计群交指令列表\n
    Return arguments:\n
    [], [] -- 已去重的群交指令列表，[角色id列表，状态id]
    """
    # 变量定义
    group_sex_instruct_list = []
    full_list_of_target_id_and_state_id = []
    player_character_data: game_type.Character = cache.character_data[0]
    # 获取全模板
    template_data_list = []
    A_template_data = player_character_data.h_state.group_sex_body_template_dict["A"]
    template_data_list.append(A_template_data)
    if handle_premise.handle_all_group_sex_temple_run_on(0):
        B_template_data = player_character_data.h_state.group_sex_body_template_dict["B"]
        template_data_list.append(B_template_data)
    # 遍历模板
    for template_data in template_data_list:
        # 对单
        for body_part in template_data[0]:
            target_chara_id = [template_data[0][body_part][0]]
            state_id = template_data[0][body_part][1]
            if state_id != -1:
                group_sex_instruct_list.append(state_id)
                full_list_of_target_id_and_state_id.append([target_chara_id, state_id])
        # 对多
        target_chara_id_list = template_data[1][0]
        state_id = template_data[1][1]
        if state_id != -1:
            group_sex_instruct_list.append(state_id)
            full_list_of_target_id_and_state_id.append([target_chara_id_list, state_id])
    # 去重
    group_sex_instruct_list = list(set(group_sex_instruct_list))

    # 返回
    return group_sex_instruct_list, full_list_of_target_id_and_state_id


def count_group_sex_character_list():
    """
    统计群交模板中的角色列表\n
    Return arguments:\n
    [] -- 已去重的群交角色列表
    """
    # 变量定义
    group_sex_chara_id_list = []
    player_character_data: game_type.Character = cache.character_data[0]
    # 获取全模板
    template_data_list = []
    A_template_data = player_character_data.h_state.group_sex_body_template_dict["A"]
    template_data_list.append(A_template_data)
    if handle_premise.handle_all_group_sex_temple_run_on(0):
        B_template_data = player_character_data.h_state.group_sex_body_template_dict["B"]
        template_data_list.append(B_template_data)
    # 遍历模板
    for template_data in template_data_list:
        # 对单
        for body_part in template_data[0]:
            target_chara_id = template_data[0][body_part][0]
            if target_chara_id != -1:
                group_sex_chara_id_list.append(target_chara_id)
        # 对多
        target_chara_id_list = template_data[1][0]
        if -1 not in target_chara_id_list:
            group_sex_chara_id_list += target_chara_id_list
    # 去重
    group_sex_chara_id_list = list(set(group_sex_chara_id_list))

    # 返回
    return group_sex_chara_id_list


def get_status_id_list_from_group_sex_body_part(body_part: str):
    """
    从群交部位获取状态id列表\n
    Keyword arguments:\n
    body_part -- 群交部位\n
    Return arguments:\n
    [] -- 状态id列表
    """
    from Script.UI.Panel import in_scene_panel

    new_status_id_list = []
    # 获取状态id列表
    if body_part == "mouth":
        status_id_list = game_config.config_status_id_list_of_group_sex_body_part[_("口")]
    elif body_part == "L_hand" or body_part == "R_hand":
        status_id_list = game_config.config_status_id_list_of_group_sex_body_part[_("手")]
    elif body_part == "penis":
        status_id_list = game_config.config_status_id_list_of_group_sex_body_part[_("插入")]
    elif body_part == _("侍奉"):
        status_id_list = game_config.config_status_id_list_of_group_sex_body_part[_("侍奉")]
    elif body_part == "anal":
        status_id_list = game_config.config_status_id_list_of_group_sex_body_part[_("肛")]
    # 遍历状态id
    now_premise_data = {}
    new_status_id_list = []
    for status_id in status_id_list:
        if status_id in constant.state_id_to_instruct_id:
            # 获取指令id
            instruct_id = constant.state_id_to_instruct_id[status_id]
            # 检查指令是否可用
            filter_judge, now_premise_data = in_scene_panel.judge_single_instruct_filter(instruct_id, now_premise_data, constant.InstructType.SEX, use_type_filter_flag=False)
            # 去掉有破处判定且当前为处的
            if filter_judge:
                status_data = game_config.config_status[status_id]
                status_tag_list = status_data.tag
                status_tag_list = status_data.tag.split("|")
                pl_character_data = cache.character_data[0]
                if pl_character_data.target_character_id == 0:
                    target_character_data = cache.character_data[pl_character_data.target_character_id]
                    # 如果NPC为处，则跳过破处类
                    if target_character_data.talent[0] and _("V") in status_tag_list and _("破处") in status_tag_list:
                        continue
                    if target_character_data.talent[1] and _("A") in status_tag_list and _("破处") in status_tag_list:
                        continue
                    if target_character_data.talent[2] and _("U") in status_tag_list and _("破处") in status_tag_list:
                        continue
                    if target_character_data.talent[3] and _("W") in status_tag_list and _("破处") in status_tag_list:
                        continue
                    if target_character_data.talent[4] and _("N") in status_tag_list and _("破处") in status_tag_list:
                        continue

            # 加入到新列表中
            if filter_judge:
                new_status_id_list.append(status_id)

    return new_status_id_list


class SeeGroupSexInfoPanel:
    """
    显示群交栏数据面板对象
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

        type_line = draw.LittleTitleLineDraw(_("群交"), width, ":")
        # print("type_data.name :",type_data.name)
        now_draw = panel.LeftDrawTextListPanel()
        text_draw = draw.NormalDraw()

        character_data = cache.character_data[0]
        now_template_data = character_data.h_state.group_sex_body_template_dict["A"]

        # 全部位文本
        all_part_text = ""

        # 对单遍历各部位
        for body_part in now_template_data[0]:
            state_id = now_template_data[0][body_part][1]
            if state_id != -1:
                target_chara_id = now_template_data[0][body_part][0]
                target_chara_name = cache.character_data[target_chara_id].name
                state_name = game_config.config_status[state_id].name
                body_part_name = body_part_name_dict[body_part]
                all_part_text += _("{0}-{1}-{2} ").format(body_part_name, state_name, target_chara_name)

        # 对多
        target_chara_id_list = now_template_data[1][0]
        state_id = now_template_data[1][1]
        if state_id != -1:
            state_name = game_config.config_status[state_id].name
            all_target_chara_name = ""
            for target_chara_id in target_chara_id_list:
                all_target_chara_name += cache.character_data[target_chara_id].name
                # 除最后一个人名字之外其他都加一个顿号
                if target_chara_id != target_chara_id_list[-1]:
                    all_target_chara_name += "、"
            # 如果人数大于1，则加一个"一起"
            if len(target_chara_id_list) > 1:
                all_target_chara_name += _("一起")
            all_part_text += _("阴茎正在被{0}{1} ").format(all_target_chara_name, state_name)

        # 如果文本不为空，则加入到绘制列表中
        if all_part_text != "":
            all_part_text = character_data.name + " " + all_part_text + "\n"
            self.draw_list.append(type_line)
        text_draw.text = all_part_text
        now_draw.draw_list.append(text_draw)
        now_draw.width += len(text_draw.text)

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


class Edit_Group_Sex_Temple_Panel:
    """
    总面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家角色数据 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("编辑群交行动", self.width)

        while 1:
            title_draw.draw()
            return_list = []

            # 刷新玩家角色数据
            self.pl_character_data = cache.character_data[0]
            now_template_data = self.pl_character_data.h_state.group_sex_body_template_dict["A"]

            # 人员筛选
            info_text = _("当前群交状态：\n")
            info_text += _("○群交时同一角色无法同时占用多个部位\n")
            info_text += _("○插入和侍奉只能二选一，插入为单人，侍奉可最多四人\n\n")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = self.width
            info_draw.draw()

            # 对单遍历各部位
            for body_part in now_template_data[0]:
                # 部位名字绘制
                now_name = body_part_name_dict[body_part].ljust(8, "　")
                if body_part == "penis":
                    now_name = _("阴茎（插入）").ljust(8, "　")
                body_part_name = f"  {now_name}"
                body_part_name_draw = draw.NormalDraw()
                body_part_name_draw.text = body_part_name
                body_part_name_draw.width = self.width / 4
                body_part_name_draw.draw()
                # 交互对象按钮绘制
                target_chara_id = now_template_data[0][body_part][0]
                if target_chara_id == -1:
                    target_chara_name = _("未选择角色")
                else:
                    target_chara_name = cache.character_data[target_chara_id].name
                target_chara_button = draw.CenterButton(
                    f"▶{target_chara_name}", body_part_name + target_chara_name, self.width / 4, cmd_func=self.show_target_chara_list, args=("A", body_part)
                )
                target_chara_button.draw()
                return_list.append(target_chara_button.return_text)
                # 状态名字绘制
                state_id = now_template_data[0][body_part][1]
                if state_id == -1:
                    state_name = _("未选择指令")
                else:
                    state_name = game_config.config_status[state_id].name
                state_name_button = draw.CenterButton(
                    f"▶{state_name}", body_part_name + state_name, self.width / 5, cmd_func=self.show_status_list, args=("A", body_part)
                )
                state_name_button.draw()
                return_list.append(state_name_button.return_text)
                line_feed.draw()

                # 阴茎栏中额外增加一个侍奉行
                if body_part == "penis":
                    now_name = _("阴茎（侍奉）").ljust(8, "　")
                    body_part_name = f"  {now_name}"
                    body_part_name_draw = draw.NormalDraw()
                    body_part_name_draw.text = body_part_name
                    body_part_name_draw.width = self.width / 2
                    body_part_name_draw.draw()
                    # 交互对象按钮绘制
                    target_chara_id_list = now_template_data[1][0]
                    if -1 in target_chara_id_list:
                        target_chara_name_text = _("未选择角色")
                    else:
                        target_chara_name_text = ""
                        for target_chara_id in target_chara_id_list:
                            target_chara_name_text += cache.character_data[target_chara_id].name
                            target_chara_name_text += " "
                    target_chara_button = draw.CenterButton(
                        f"▶{target_chara_name_text}", body_part_name + target_chara_name_text, self.width / 4, cmd_func=self.show_target_chara_list, args=("A", _("侍奉"))
                    )
                    target_chara_button.draw()
                    return_list.append(target_chara_button.return_text)
                    # 状态名字绘制
                    state_id = now_template_data[1][1]
                    if state_id == -1:
                        state_name = _("未选择指令")
                    else:
                        state_name = game_config.config_status[state_id].name
                    state_name_button = draw.CenterButton(
                        f"▶{state_name}", body_part_name + state_name, self.width / 5, cmd_func=self.show_status_list, args=("A", _("侍奉"))
                    )
                    state_name_button.draw()
                    return_list.append(state_name_button.return_text)
                    line_feed.draw()

            # 轮流用副模板
            line_feed.draw()
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = _("轮流用副模板：在当前状态之外新增一套副模板，可在两套模板之间切换，或者使用轮流群交指令，可轮流进行一次双模板中的群交指令\n")
            info_draw.text += "              "
            info_draw.width = self.width
            info_draw.draw()
            now_B_text = _("未启用")
            if handle_premise.handle_all_group_sex_temple_run_on(0):
                now_B_text = _("已启用")
            B_change_button = draw.LeftButton(
                f"▶{now_B_text}", _("轮流用副模板"), len(now_B_text) * 4 + 1, cmd_func=self.change_B_temple_flag
            )
            B_change_button.draw()
            return_list.append(B_change_button.return_text)
            if handle_premise.handle_all_group_sex_temple_run_on(0):
                change_temple_button = draw.CenterButton(
                    _("切换模板"), _("切换"), len(now_B_text) * 4 + 1, cmd_func=self.change_temple
                )
                change_temple_button.draw()
                return_list.append(change_temple_button.return_text)

            # 锁定按钮
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = _("锁定群交模板：锁定后使用指令时不会再自动调整状态，仅可在当前编辑面板中修改\n")
            info_draw.text += "              "
            info_draw.width = self.width
            info_draw.draw()

            now_lock_text = _("已锁定")
            if self.pl_character_data.h_state.group_sex_lock_flag == False:
                now_lock_text = _("未锁定")
            lock_change_button = draw.LeftButton(
                f"▶{now_lock_text}", _("锁定群交模板"), len(now_lock_text) * 4 + 1, cmd_func=self.change_lock_flag
            )
            lock_change_button.draw()
            return_list.append(lock_change_button.return_text)

            # NPC行动调整按钮
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = _("调整干员行动：没有在上述位置中的干员会\n")
            info_draw.text += "              "
            info_draw.width = self.width
            info_draw.draw()

            npc_ai_text = _("无行动")
            if handle_premise.handle_npc_ai_type_1_in_group_sex(0):
                npc_ai_text = _("自慰")
            elif handle_premise.handle_npc_ai_type_2_in_group_sex(0):
                npc_ai_text = _("优先补空位，无空位则自慰")
            npc_ai_change_button = draw.LeftButton(
                f"▶{npc_ai_text}", _("调整干员行动"), len(npc_ai_text) * 4 + 1, cmd_func=self.change_npc_ai
            )
            npc_ai_change_button.draw()
            return_list.append(npc_ai_change_button.return_text)

            # 邀请其他干员按钮
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = _("邀请其他干员：邀请不在场的干员来这里参加群交，只能邀请实行值足够同意的\n")
            info_draw.text += "              "
            info_draw.width = self.width
            info_draw.draw()

            invite_other_npc_text = _("邀请")
            invite_other_npc_button = draw.LeftButton(
                f"▶{invite_other_npc_text}", _("邀请其他干员"), len(npc_ai_text) * 4 + 1, cmd_func=self.show_invite_npc_panel
            )
            invite_other_npc_button.draw()
            return_list.append(invite_other_npc_button.return_text)

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                self.reset_unfinish_select()
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def show_target_chara_list(self, temple_id: str, body_part: str):
        """绘制可选择的交互对象角色列表"""
        # 全NPC列表
        scene_path_str = map_handle.get_map_system_path_str_for_list(self.pl_character_data.position)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        all_character_list = scene_data.character_list
        # 全模板中的角色id列表
        group_sex_chara_id_list = count_group_sex_character_list()
        # 获取已选的角色id
        if body_part != "侍奉":
            selected_chara_id_list = [self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][0][body_part][0]]
        else:
            selected_chara_id_list = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][1][0]
        # 从全模板角色id列表中去掉已选的角色id
        group_sex_chara_id_list = [chara_id for chara_id in group_sex_chara_id_list if chara_id not in selected_chara_id_list]
        # 去掉列表中可能存在的玩家id
        all_character_list = [chara_id for chara_id in all_character_list if chara_id != 0]
        # 去掉列表中已在其他部位中的角色id
        all_character_list = [chara_id for chara_id in all_character_list if chara_id not in group_sex_chara_id_list]
        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()
            line_feed.draw()
            return_list = []
            # 生成角色名的按钮，让玩家选择
            chara_count = 0
            for chara_id in all_character_list:
                character_data = cache.character_data[chara_id]
                button_text = f"[{str(character_data.adv).rjust(4,'0')}]{character_data.name}"
                name_draw = draw.LeftButton(button_text, character_data.name, self.width / 5, cmd_func=self.set_target_chara, args=(temple_id, body_part, chara_id))
                # 如果已经选中，则改变绘制颜色
                if chara_id in selected_chara_id_list:
                    name_draw = draw.LeftButton(button_text, character_data.name, self.width / 5, normal_style='gold_enrod', cmd_func=self.set_target_chara, args=(temple_id, body_part, chara_id))
                name_draw.draw()
                return_list.append(name_draw.return_text)
                # 每五个换行一次
                chara_count += 1
                if chara_count != 0 and chara_count % 5 == 0:
                    line_feed.draw()
            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def show_status_list(self, temple_id: str, body_part: str):
        """绘制可选择的状态列表"""
        # 如果当前已指定对象角色id，则将其设为玩家的交互对象
        if body_part != _("侍奉"):
            target_chara_id = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][0][body_part][0]
            if target_chara_id != -1:
                self.pl_character_data.target_character_id = target_chara_id
        else:
            target_chara_id_list = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][1][0]
            # 侍奉中则将最后一位设为玩家的交互对象
            if -1 not in target_chara_id_list:
                target_chara_id = target_chara_id_list[-1]
                self.pl_character_data.target_character_id = target_chara_id
        new_status_id_list = get_status_id_list_from_group_sex_body_part(body_part)
        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()
            line_feed.draw()
            return_list = []
            # 生成状态名的按钮，让玩家选择
            status_count = 0
            for status_id in new_status_id_list:
                status_data = game_config.config_status[status_id]
                button_text = f"[{str(status_id).rjust(4,'0')}]{status_data.name}"
                name_draw = draw.LeftButton(button_text, status_data.name, self.width / 5, cmd_func=self.set_status, args=(temple_id, body_part, status_id))
                name_draw.draw()
                return_list.append(name_draw.return_text)
                # 每五个换行一次
                status_count += 1
                if status_count != 0 and status_count % 5 == 0:
                    line_feed.draw()
            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def show_invite_npc_panel(self):
        """绘制可邀请的NPC列表"""
        from Script.Design import character
        # 当前地点的角色列表
        scene_path_str = map_handle.get_map_system_path_str_for_list(self.pl_character_data.position)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        now_scene_character_list = scene_data.character_list

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()
            line_feed.draw()
            return_list = []

            # 绘制提示信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("当前可邀请的干员有：\n\n")
            info_draw.width = self.width
            info_draw.draw()

            # 遍历全部已有角色
            chara_count = 0
            for chara_id in cache.npc_id_got:
                # 如果角色已在场景中，则跳过
                if chara_id in now_scene_character_list:
                    continue
                # 判断实行值是否足够，不够的也跳过
                if character.calculation_instuct_judege(0, chara_id, _("群交"), not_draw_flag = True)[0] == False:
                    continue
                now_character_data = cache.character_data[chara_id]
                name_draw_text = f"[{str(now_character_data.adv).rjust(4,'0')}]{now_character_data.name}"
                name_draw = draw.LeftButton(name_draw_text, now_character_data.name, self.width / 5, cmd_func=self.invite_npc, args=(chara_id,))
                # 如果已经被选择过，则改变颜色
                if handle_premise.handle_self_now_go_to_join_group_sex(chara_id):
                    name_draw = draw.LeftButton(name_draw_text, now_character_data.name, self.width / 5, normal_style='gold_enrod', cmd_func=self.invite_npc, args=(chara_id,))
                name_draw.draw()
                return_list.append(name_draw.return_text)
                chara_count += 1
                # 每五个换行一次
                if chara_count != 0 and chara_count % 5 == 0:
                    line_feed.draw()
            
            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def set_target_chara(self, temple_id: str, body_part: str, target_chara_id: int):
        """设置交互对象"""
        if body_part != "侍奉":
            now_template_data = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id]
            now_template_data[0][body_part][0] = target_chara_id
            # 如果是阴茎，则清空侍奉
            if body_part == "penis":
                self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][1] = [[-1], -1]
        else:
            now_template_data_chara_list = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][1][0]
            # 如果已经选中，则取消选中
            if target_chara_id in now_template_data_chara_list:
                now_template_data_chara_list.remove(target_chara_id)
                # 如果没有人了，则加入一个-1
                if len(now_template_data_chara_list) == 0:
                    now_template_data_chara_list.append(-1)
            # 否则选中
            else:
                now_template_data_chara_list.append(target_chara_id)
                # 如果已经超过4个了，则去掉第一个
                if len(now_template_data_chara_list) > 4:
                    now_template_data_chara_list.pop(0)
                # 去掉里面可能存在的-1
                if -1 in now_template_data_chara_list:
                    now_template_data_chara_list.remove(-1)
            # 清空插入
            self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][0]["penis"] = [-1, -1]

    def set_status(self, temple_id: str, body_part: str, status_id: int):
        """设置状态"""
        if body_part != _("侍奉"):
            now_template_data = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id]
            now_template_data[0][body_part][1] = status_id
            # 如果是阴茎，则清空侍奉
            if body_part == "penis":
                self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][1] = [[-1], -1]
        else:
            now_template_data = self.pl_character_data.h_state.group_sex_body_template_dict[temple_id]
            now_template_data[1][1] = status_id
            # 清空插入
            self.pl_character_data.h_state.group_sex_body_template_dict[temple_id][0]["penis"] = [-1, -1]

    def change_lock_flag(self):
        """改变锁定状态"""
        self.pl_character_data.h_state.group_sex_lock_flag = not self.pl_character_data.h_state.group_sex_lock_flag

    def change_npc_ai(self):
        """改变NPC行动逻辑"""
        self.pl_character_data.h_state.npc_ai_type_in_group_sex += 1
        if self.pl_character_data.h_state.npc_ai_type_in_group_sex >= 3:
            self.pl_character_data.h_state.npc_ai_type_in_group_sex = 0

    def change_B_temple_flag(self):
        """改变B模板状态"""
        self.pl_character_data.h_state.all_group_sex_temple_run = not self.pl_character_data.h_state.all_group_sex_temple_run

    def change_temple(self):
        """切换模板"""
        self.pl_character_data.h_state.group_sex_body_template_dict["A"], self.pl_character_data.h_state.group_sex_body_template_dict["B"] = self.pl_character_data.h_state.group_sex_body_template_dict["B"], self.pl_character_data.h_state.group_sex_body_template_dict["A"]

    def invite_npc(self, character_id: int):
        """邀请NPC"""
        from Script.Design import character
        character_data = cache.character_data[character_id]
        # 如果已经邀请，则取消邀请
        if character_data.sp_flag.go_to_join_group_sex:
            character_data.sp_flag.go_to_join_group_sex = False
            info_draw_text = _("\n已取消对{0}的群交邀请，{0}不会来这里参加群交了\n").format(character_data.name)
            # 结算等待
            character.init_character_behavior_start_time(character_id, cache.game_time)
            constant.handle_state_machine_data[0](character_id)
        # 否则邀请
        else:
            character_data.sp_flag.go_to_join_group_sex = True
            info_draw_text = _("\n已邀请{0}来这里参加群交\n").format(character_data.name)
            # 赋予二段行为
            character_data.second_behavior[1366] = 1
            # 结算移动
            character.init_character_behavior_start_time(character_id, cache.game_time)
            constant.handle_state_machine_data[503](character_id)
        # 绘制信息
        info_draw = draw.WaitDraw()
        info_draw.text = info_draw_text
        info_draw.width = self.width
        info_draw.draw()

    def reset_unfinish_select(self):
        """重置角色id或者状态id没有全部填完的项"""
        # 获取全模板
        template_data_list = []
        A_template_data = self.pl_character_data.h_state.group_sex_body_template_dict["A"]
        template_data_list.append(A_template_data)
        if handle_premise.handle_all_group_sex_temple_run_on(0):
            B_template_data = self.pl_character_data.h_state.group_sex_body_template_dict["B"]
            template_data_list.append(B_template_data)
        # 遍历模板
        for template_data in template_data_list:
            # 对单
            for body_part in template_data[0]:
                target_chara_id = template_data[0][body_part][0]
                state_id = template_data[0][body_part][1]
                if state_id == -1 or target_chara_id == -1:
                    template_data[0][body_part] = [-1, -1]
            # 对多
            target_chara_id_list = template_data[1][0]
            state_id = template_data[1][1]
            if state_id == -1 or -1 in target_chara_id_list:
                template_data[1] = [[-1], -1]
