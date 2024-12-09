from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, handle_premise

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
    # 获取指令tag
    status_data = game_config.config_status[state_id]
    tag_list = status_data.tag.split("|")
    # 遍历tag
    if not len(tag_list):
        return
    # 阴茎插入
    if _("插入") in tag_list:
        now_template_data[0]["penis"] = [target_character_id, state_id]
        now_template_data[1] = [[-1], -1]
    # 阴茎侍奉
    elif _("侍奉") in tag_list:
        now_template_data[0]["penis"] = [-1, -1]
        # 如果新指令，则重置数据
        if now_template_data[1][1] != state_id:
            now_template_data[1] = [[target_character_id], state_id]
        # 否则则只将角色id加进角色列表里
        elif target_character_id not in now_template_data[1][0]:
            now_template_data[1][0].append(target_character_id)
    # 口
    elif _("口") in tag_list:
        now_template_data[0]["mouth"] = [target_character_id, state_id]
    # 手
    elif _("手") in tag_list:
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
    elif _("肛") in tag_list:
        now_template_data[0]["anal"] = [target_character_id, state_id]

    # 特殊指令特殊处理
    if status_data.name == _("六九式"):
        now_template_data[0]["mouth"] = [target_character_id, state_id]
        now_template_data[1] = [[target_character_id], state_id]


def count_group_sex_instruct_list():
    """
    统计群交指令列表
    """
    # 变量定义
    group_sex_instruct_list = []
    full_list_of_target_id_and_state_id = []
    player_character_data: game_type.Character = cache.character_data[0]
    # 获取全模板
    template_data_list = []
    A_template_data = player_character_data.h_state.group_sex_body_template_dict["A"]
    template_data_list.append(A_template_data)
    if player_character_data.h_state.all_group_sex_temple_run:
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

        # 部位英语对中文的字典
        body_part_name_dict = {
            "mouth": "嘴",
            "L_hand": "左手",
            "R_hand": "右手",
            "penis": "阴茎",
            "anal": "肛门",
        }

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
                all_part_text += _("{0}{1}{2} ").format(body_part_name, state_name, target_chara_name)

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
            all_part_text = character_data.name + all_part_text + "\n"
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

