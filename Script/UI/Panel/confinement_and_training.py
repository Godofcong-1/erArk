from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.Design import handle_premise, handle_instruct, attr_calculation, game_time, attr_text
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
import random

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


class Confinement_And_Training_Manage_Panel:
    """
    用于监禁调教管理的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("监禁调教管理")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的角色数据 """
        self.done_training_status_id_set = set()
        """ 已经调教过的状态id集合 """

    def draw(self):
        """绘制对象"""

        title_text = _("监禁调教管理")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            now_draw = draw.NormalDraw()
            info_text = _(" \n ○点击[选项标题]显示[选项介绍]，点击[选项本身]即可[改变该选项]\n")
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 遍历全部设置
            for cid in game_config.config_confinement_training_setting:
                line_feed.draw()
                confinement_training_setting_data = game_config.config_confinement_training_setting[cid]
                # 选项名
                button_text = f"  [{confinement_training_setting_data.name}]： "
                button_len = max(len(button_text) * 2, 60)
                button_draw = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.draw_info, args=(cid))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 如果没有该键，则创建一个，并置为0
                if cid not in cache.rhodes_island.confinement_training_setting:
                    cache.rhodes_island.confinement_training_setting[cid] = 0
                now_setting_flag = cache.rhodes_island.confinement_training_setting[cid] # 当前设置的值
                option_len = len(game_config.config_confinement_training_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                button_text = f" [{game_config.config_confinement_training_setting_option[cid][now_setting_flag]}] "
                button_len = max(len(button_text) * 2, 20)

                # 绘制选项
                if cid not in {11}:
                    button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_setting, args=(cid, option_len))
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                # 调教前准备单独处理
                elif cid == 11:
                    clean_flag = cache.rhodes_island.pre_training_cleaning
                    lubrication_flag = cache.rhodes_island.pre_training_lubrication
                    tool_dict = cache.rhodes_island.pre_training_tool_dict

                    if clean_flag:
                        clean_text = _(" [进行污浊清洗] ")
                    else:
                        clean_text = _(" [不进行污浊清洗] ")
                    clean_button = draw.LeftButton(clean_text, _("污浊清洗"), len(clean_text) * 2, cmd_func=self.change_pre_training_cleaning)
                    clean_button.draw()
                    return_list.append(clean_button.return_text)
                    if lubrication_flag:
                        lubrication_text = _(" [使用润滑液提前润滑] ")
                    else:
                        lubrication_text = _(" [不使用润滑液提前润滑] ")
                    lubrication_button = draw.LeftButton(lubrication_text, _("润滑液"), len(lubrication_text) * 2, cmd_func=self.change_pre_training_lubrication)
                    lubrication_button.draw()
                    return_list.append(lubrication_button.return_text)
                    tool_text = _(" [调整道具使用] ")
                    tool_button = draw.LeftButton(tool_text, _("道具使用"), len(tool_text) * 2, cmd_func=self.adjust_tool_list)
                    tool_button.draw()
                    return_list.append(tool_button.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def draw_info(self, cid: int):
        """绘制设置的详细信息"""
        line = draw.LineDraw("-", self.width)
        line.draw()
        now_draw = draw.WaitDraw()
        setting_data = game_config.config_physical_exam_setting[cid]
        info_text = f"\n {setting_data.info}\n"
        now_draw.text = info_text
        now_draw.width = self.width
        now_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

    def change_setting(self, cid, option_len):
        """修改设置"""
        if cache.rhodes_island.confinement_training_setting[cid] < option_len - 1:
            cache.rhodes_island.confinement_training_setting[cid] += 1
        else:
            cache.rhodes_island.confinement_training_setting[cid] = 0

    def change_pre_training_cleaning(self):
        """切换是否进行污浊清洗"""
        cache.rhodes_island.pre_training_cleaning = not cache.rhodes_island.pre_training_cleaning

    def change_pre_training_lubrication(self):
        """切换是否使用润滑液提前润滑"""
        cache.rhodes_island.pre_training_lubrication = not cache.rhodes_island.pre_training_lubrication

    def adjust_tool_list(self):
        """调整道具使用"""
        pass

    def adjust_target_list(self):
        """调整体检对象名单"""
        from Script.UI.Panel import normal_panel
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], normal_panel.CommonSelectNPCButtonList, 50, 5, window_width, 1, 0, 0)
        while 1:
            npc_id_got_list = sorted(cache.npc_id_got)
            # 已选择的角色id列表
            selected_id_list = list(cache.rhodes_island.manually_selected_exam_operator_ids)
            final_list = []
            # 遍历角色id
            for npc_id in npc_id_got_list:
                if npc_id == 0:
                    continue
                now_list = [npc_id, self.switch_chara_in_target_list, selected_id_list]
                final_list.append(now_list)
            now_draw_panel.text_list = final_list

            # 调用通用选择按钮列表函数
            return_list = normal_panel.common_select_npc_button_list_func(now_draw_panel, _("体检对象名单"))

            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def switch_chara_in_target_list(self, character_id: int):
        """切换体检对象名单中的角色"""
        if character_id in cache.rhodes_island.manually_selected_exam_operator_ids:
            cache.rhodes_island.manually_selected_exam_operator_ids.remove(character_id)
        else:
            cache.rhodes_island.manually_selected_exam_operator_ids.add(character_id)
