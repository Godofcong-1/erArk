from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, py_cmd, constant
from Script.Design import talk, handle_premise
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

def get_target_chara_diy_instruct(character_id: int = 0):
    """
    获得交互对象的角色自定义指令\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    int -- 子事件数量\n
    list -- 子事件列表\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    son_event_list = [] # 子事件列表
    if character_data.target_character_id:
        target_character_data = cache.character_data[character_data.target_character_id]
        # 判断是否存在该行为对应的事件
        if constant.CharacterStatus.STATUS_CHARA_DIY_INSTRUCT in game_config.config_event_status_data_by_chara_adv:
            all_chara_diy_instruct_event_list = game_config.config_event_status_data_by_chara_adv[constant.CharacterStatus.STATUS_CHARA_DIY_INSTRUCT]
            # 判断交互对象是否有该行为事件
            if target_character_data.adv in all_chara_diy_instruct_event_list:
                target_diy_instruct_event_list = all_chara_diy_instruct_event_list[target_character_data.adv]
                # 遍历事件列表
                for event_id in target_diy_instruct_event_list:
                    event_config = game_config.config_event[event_id]
                    # 计算总权重
                    now_weight = handle_premise.get_weight_from_premise_dict(event_config.premise, character_id, unconscious_pass_flag = True)
                    # 判定通过，加入到子事件的列表中
                    if now_weight:
                        son_event_list.append(event_id)

    return len(son_event_list), son_event_list


def check_son_event_list_from_event_list(event_list: list, character_id: int, event_parent_chid_id: int, event_parent_value: int):
    """
    检查事件列表中是否有子事件\n
    Keyword arguments:\n
    event_list -- 事件列表\n
    character_id -- 角色id\n
    event_parent_chid_id -- 子事件的序号id（非事件id）\n
    event_parent_value -- 子事件的值\n
    Return arguments:\n
    son_event_list -- 子事件列表\n
    """
    son_event_list = [] # 子事件列表

    # 开始遍历当前行为的事件表
    for event_id in event_list:
        event_config = game_config.config_event[event_id]
        # 需要含有综合数值前提中的子嵌套事件前提
        son_premise = "CVP_A1_Son|{0}_E_{1}".format(event_parent_chid_id, event_parent_value)
        # 需要有该子事件的前提
        if son_premise in event_config.premise:
            premise_dict = event_config.premise.copy()
            # 从前提集中去掉子事件前提
            premise_dict.pop(son_premise)
            # 如果前提集不为空
            if len(premise_dict):
                # 计算总权重
                now_weight = handle_premise.get_weight_from_premise_dict(premise_dict, character_id, unconscious_pass_flag = True)
                # 判定通过，加入到子事件的列表中
                if now_weight:
                    son_event_list.append(event_id)
            # 前提集为空，直接加入到子事件的列表中
            else:
                son_event_list.append(event_id)
    return son_event_list


class Event_option_Panel:
    """
    总面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width: int = width
        """ 绘制的最大宽度 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        line_feed.draw()
        character_data: game_type.Character = cache.character_data[self.character_id]
        behavior_id = character_data.behavior.behavior_id
        father_event_id = character_data.event.event_id

        # 获取父事件的前提信息
        father_event_data: game_type.Event = game_config.config_event[father_event_id]
        self.handle_panel = panel.PageHandlePanel([], SonEventDraw, 20, 1, self.width, 1, 1, 0)
        father_promise = father_event_data.premise

        son_event_list = []

        # 开始遍历当前行为的事件表
        if behavior_id in game_config.config_event_status_data:
            for event_id in game_config.config_event_status_data[behavior_id]:
                event_config = game_config.config_event[event_id]
                son_flag = True
                # 需要含有子事件前提
                if len(event_config.premise) and "option_son" in event_config.premise:
                    for premise in father_promise:
                        # 子事件的前提必须完全包含父事件的前提
                        if premise not in event_config.premise:
                            son_flag = False
                            break
                    # 加入到子事件的列表中
                    if son_flag:
                        son_event_list.append([event_id, self.character_id])

        while 1:
            py_cmd.clr_cmd()

            self.handle_panel.text_list = son_event_list
            self.handle_panel.update()
            return_list = []
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break


class multi_layer_event_option_Panel:
    """
    多层嵌套的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int, event_parent_chid_id: int, event_parent_value: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width: int = width
        """ 绘制的最大宽度 """
        self.event_parent_chid_id = event_parent_chid_id
        """ 嵌套父子事件的序号id（非事件id） """
        self.event_parent_value = event_parent_value
        """ 嵌套父子事件的值 """
        self.handle_panel: panel.PageHandlePanel = panel.PageHandlePanel([], SonEventDraw, 20, 1, self.width, 1, 1, 0)
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        line_feed.draw()
        character_data: game_type.Character = cache.character_data[self.character_id]
        target_character_data = cache.character_data[character_data.target_character_id]
        behavior_id = character_data.behavior.behavior_id

        tem_event_list = [] # 临时事件列表
        son_event_list = [] # 子事件列表

        # 开始遍历当前行为的事件表
        if behavior_id in game_config.config_event_status_data_by_chara_adv:
            if character_data.adv in game_config.config_event_status_data_by_chara_adv[behavior_id]:
                tem_event_list += game_config.config_event_status_data_by_chara_adv[behavior_id][character_data.adv]
            if target_character_data.adv in game_config.config_event_status_data_by_chara_adv[behavior_id]:
                tem_event_list += game_config.config_event_status_data_by_chara_adv[behavior_id][target_character_data.adv]

        # 从临时事件列表中筛选出子事件
        son_event_list = check_son_event_list_from_event_list(tem_event_list, self.character_id, self.event_parent_chid_id, self.event_parent_value)

        # 如果没有子事件，直接返回
        if len(son_event_list) == 0:
            return
        else:
            draw_event_list = []
            for son_event_id in son_event_list:
                draw_event_list.append([son_event_id, self.character_id])
        # 如果有子事件，继续绘制
        while 1:
            py_cmd.clr_cmd()

            self.handle_panel.text_list = draw_event_list
            self.handle_panel.update()
            return_list = []
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break


class SonEventDraw:
    """
    显示子事件选项对象
    Keyword arguments:
    value_list -- 事件id,人物id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, value_list: list, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.event_id = value_list[0]
        """ 事件id """
        self.character_id = value_list[1]
        """ 绘制的角色id """
        self.son_event = game_config.config_event[self.event_id]
        """ 子事件 """
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
        name_draw = draw.NormalDraw()
        # print("text :",text)
        option_text = self.son_event.text.split("|")[0]
        option_text = talk.code_text_to_draw_text(option_text, self.character_id)
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}{option_text}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.run_son_event
                )
            else:
                button_text = f"[{option_text}]"
                name_draw = draw.CenterButton(
                    button_text, option_text, self.width, cmd_func=self.run_son_event
                )
                self.button_return = option_text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{option_text}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """


    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def run_son_event(self):
        """点击后运行对应的子事件"""
        character_data: game_type.Character = cache.character_data[self.character_id]
        character_data.event.son_event_id = self.event_id

