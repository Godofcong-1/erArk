from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.Design import game_time, attr_calculation, talk, handle_premise
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


def settle_equipment_damage_in_commission(commision_id):
    """
    结算外勤委托中装备的损坏
    Keyword arguments:
    commision_id -- 外勤委托id
    """
    equipment_damage_text = ""
    # 获取派遣人员列表
    send_npc_list = cache.rhodes_island.ongoing_field_commissions[commision_id][0]
    commision_lv = game_config.config_commission[commision_id].level
    damage_rate_data = game_config.config_equipment_damage_rate[commision_lv]
    damage_rate_list = [
        damage_rate_data.rate_0,
        damage_rate_data.rate_1,
        damage_rate_data.rate_2,
        damage_rate_data.rate_3,
        damage_rate_data.rate_4,
    ]
    # 遍历派遣人员列表
    for send_npc_id in send_npc_list:
        send_npc_data = cache.character_data[send_npc_id]
        # 获取装备损坏概率，为0~1的随机小数
        random_damage_rate = random.random()
        # 根据装备损坏概率获取损坏等级
        damage_lv = 0
        for i, rate in enumerate(damage_rate_list):
            if random_damage_rate < rate:
                damage_lv = i
                break
        # 如果损坏等级大于0，则进行装备损坏
        if damage_lv > 0:
            send_npc_data.cloth.equipment_condition = damage_lv
            # 获取装备损坏情况
            equipment_condition = game_config.config_equipment_condition[damage_lv].name
            # 绘制装备损坏信息
            equipment_damage_text += _("{0}的装备损坏了，损坏情况为{1}，需要进行维修。\n").format(send_npc_data.name, equipment_condition)

    return equipment_damage_text


class Equipment_Maintain_Panel:
    """
    用于装备维护的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("装备维护")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """
        绘制装备维护主界面
        """
        from Script.UI.Panel import manage_basement_panel

        title_text = _("装备维护")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            title_draw.draw()
            all_info_draw = draw.NormalDraw()
            all_info_draw.width = self.width
            now_text = _("当前有以下干员装备存在损坏：\n")
            # 遍历所有已获得干员，显示装备损坏情况
            damaged_count = 0
            for npc_id in cache.npc_id_got:
                npc_data = cache.character_data[npc_id]
                condition_lv = npc_data.cloth.equipment_condition
                if condition_lv != 0:
                    condition_name = game_config.config_equipment_condition[condition_lv].name
                    now_text += f"  {npc_data.name}：{condition_name}\n"
                    damaged_count += 1
            if damaged_count == 0:
                now_text += _("  当前无装备损坏的干员\n")
            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()

            # 维护策略按钮
            button_text1 = _("[001]指定维护策略")
            button_draw1 = draw.LeftButton(
                button_text1, button_text1, len(button_text1) * 3, cmd_func=self.select_maintain_strategy
            )
            button_draw1.draw()
            line_feed.draw()
            # 变更铁匠人数按钮
            button_text2 = _("[002]变更铁匠人数")
            button_draw2 = draw.LeftButton(
                button_text2, button_text2, len(button_text2) * 3, cmd_func=manage_basement_panel.change_npc_work_out, args=self.width
            )
            button_draw2.draw()
            line_feed.draw()
            line_feed.draw()
            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list = [button_draw1.return_text, button_draw2.return_text, back_draw.return_text]
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_maintain_strategy(self):
        """
        选择装备维护策略和保养目标（基于配置表）
        """
        title_text = _("调整装备维护策略和保养目标")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            line_feed.draw()
            title_draw.draw()

            # 输出提示信息
            now_draw = draw.NormalDraw()
            info_text = _(" \n ○点击[选项标题]显示[选项介绍]，点击[选项本身]即可[改变该选项]\n")
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 遍历全部设置
            for cid in game_config.config_equipment_maintain_setting:
                line_feed.draw()
                equipment_maintain_setting_data = game_config.config_equipment_maintain_setting[cid]
                # 选项名
                button_text = f"  [{equipment_maintain_setting_data.name}]： "
                button_len = max(len(button_text) * 2, 60)
                button_draw = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.draw_info, args=(cid))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 如果没有该键，则创建一个，并置为0
                if cid not in cache.rhodes_island.equipment_maintain_setting:
                    cache.rhodes_island.equipment_maintain_setting[cid] = 0
                now_setting_flag = cache.rhodes_island.equipment_maintain_setting[cid] # 当前设置的值
                option_len = len(game_config.config_equipment_maintain_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                button_text = f" [{game_config.config_equipment_maintain_setting_option[cid][now_setting_flag]}] "
                button_len = max(len(button_text) * 2, 20)

                # 绘制选项
                button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_setting, args=(cid, option_len))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 部分选项有额外的手动选择按钮
                if cid == 2 and cache.rhodes_island.equipment_maintain_setting[cid] == 1:
                    now_len = len(cache.rhodes_island.manually_selected_exam_operator_ids)
                    button_text = _("[调整干员名单]({0}人)").format(now_len)
                    button_len = max(len(button_text) * 2, 20)
                    button_draw = draw.CenterButton(button_text, str(cid) + button_text, button_len, cmd_func=self.adjust_target_list)
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def draw_info(self, cid: int):
        """绘制设置的详细信息"""
        line = draw.LineDraw("-", self.width)
        line.draw()
        now_draw = draw.WaitDraw()
        setting_data = game_config.config_equipment_maintain_setting[cid]
        info_text = f"\n {setting_data.info}\n"
        now_draw.text = info_text
        now_draw.width = self.width
        now_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

    def change_setting(self, cid, option_len):
        """修改设置"""
        if cache.rhodes_island.equipment_maintain_setting[cid] < option_len - 1:
            cache.rhodes_island.equipment_maintain_setting[cid] += 1
        else:
            cache.rhodes_island.equipment_maintain_setting[cid] = 0

    def adjust_target_list(self):
        """调整装备维护名单"""
        from Script.UI.Panel import common_select_NPC
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, 1, 0, 0)
        select_state = {}
        while 1:
            npc_id_got_list = sorted(cache.npc_id_got)
            # 已选择的角色id列表
            selected_id_list = cache.rhodes_island.equipment_maintain_operator_ids
            final_list = []
            # 遍历角色id
            for npc_id in npc_id_got_list:
                if npc_id == 0:
                    continue
                # 跳过2、7异常的角色
                if not handle_premise.handle_normal_2(npc_id) :
                    continue
                if not handle_premise.handle_normal_7(npc_id):
                    continue
                now_list = [npc_id, self.switch_chara_in_target_list, selected_id_list]
                final_list.append(now_list)
            now_draw_panel.text_list = final_list

            # 调用通用选择按钮列表函数
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("装备维护对象名单"), select_state = select_state)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def switch_chara_in_target_list(self, character_id: int):
        """切换对象名单中的角色"""
        if character_id in cache.rhodes_island.equipment_maintain_operator_ids:
            cache.rhodes_island.equipment_maintain_operator_ids.remove(character_id)
        else:
            cache.rhodes_island.equipment_maintain_operator_ids.add(character_id)