from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, handle_premise
import random

from Script.UI.Panel import achievement_panel

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


def get_equipment_condition_name(value: float) -> str:
    """
    根据装备condition的float值查找csv区间，返回装备情况名
    输入：value: float
    输出：str 装备情况名
    """
    # 读取装备情况配置表，假设game_config.config_equipment_condition的key为int，value有name和value属性
    # 先按value排序，找到value最接近且不大于输入值的那一项
    condition_list = list(game_config.config_equipment_condition.values())
    # 按value升序排列
    condition_list.sort(key=lambda x: x.value)
    result_name = condition_list[0].name
    for cond in condition_list:
        if value >= cond.value:
            result_name = cond.name
        else:
            break
    return result_name

def show_damaged_equipment():
    """
    显示所有装备损坏（equipment_condition < 0）的干员及其装备情况
    输入/输出：无
    """
    title_text = _("装备损坏情况一览")
    title_draw = draw.TitleLineDraw(title_text, window_width)
    while 1:
        title_draw.draw()
        info_draw = draw.NormalDraw()
        now_text = _("○中度损坏的装备会降低进行外勤委托的干员的能力值，如果装备严重损坏了则无法安排进行外勤委托\n\n")
        damaged_count = 0
        for npc_id in cache.npc_id_got:
            npc_data = cache.character_data[npc_id]
            condition_val = npc_data.cloth.equipment_condition
            if condition_val < 0:
                condition_name = get_equipment_condition_name(condition_val)
                now_text += f"  {npc_data.name}：{condition_name} ({condition_val})\n"
                damaged_count += 1
        if damaged_count == 0:
            now_text += _( "  当前无装备损坏的干员\n")
        info_draw.text = now_text
        info_draw.draw()
        line_feed.draw()
        back_draw = draw.CenterButton(_("[返回]"), _( "返回"), window_width)
        back_draw.draw()
        line_feed.draw()
        yrn = flow_handle.askfor_all([back_draw.return_text])
        if yrn == back_draw.return_text:
            break

def show_maintained_equipment():
    """
    显示所有装备保养（equipment_condition > 0）的干员及其装备情况
    输入/输出：无
    """
    title_text = _("装备保养情况一览")
    title_draw = draw.TitleLineDraw(title_text, window_width)
    while 1:
        title_draw.draw()
        info_draw = draw.NormalDraw()
        now_text = _("○良好保养的装备有更高的耐久度，完美保养的装备还可以为外勤干员提供额外的能力加成\n\n")
        maintained_count = 0
        for npc_id in cache.npc_id_got:
            npc_data = cache.character_data[npc_id]
            condition_val = npc_data.cloth.equipment_condition
            if condition_val > 0:
                condition_name = get_equipment_condition_name(condition_val)
                now_text += f"  {npc_data.name}：{condition_name} ({condition_val})\n"
                maintained_count += 1
        if maintained_count == 0:
            now_text += _( "  当前无装备保养的干员\n")
        info_draw.text = now_text
        info_draw.draw()
        line_feed.draw()
        back_draw = draw.CenterButton(_("[返回]"), _( "返回"), window_width)
        back_draw.draw()
        line_feed.draw()
        yrn = flow_handle.askfor_all([back_draw.return_text])
        if yrn == back_draw.return_text:
            break


def settle_equipment_damage_in_commission(commision_id: int) -> str:
    """
    结算外勤委托中装备的损坏\n
    输入：\n
    commision_id -- 外勤委托id\n
    输出：\n
    str 装备损坏信息
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
        count_damage_rate = 0
        for i, rate in enumerate(damage_rate_list):
            count_damage_rate += rate
            if random_damage_rate < count_damage_rate:
                damage_lv = i
                break
        # 如果损坏等级大于0，则进行装备损坏
        if damage_lv > 0:
            send_npc_data.cloth.equipment_condition = damage_lv * -1
            # 获取装备损坏情况
            equipment_condition = get_equipment_condition_name(send_npc_data.cloth.equipment_condition)
            # 绘制装备损坏信息
            equipment_damage_text += _("{0}的装备损坏了，损坏情况为{1}，需要进行维修。\n").format(send_npc_data.name, equipment_condition)

    return equipment_damage_text


def smith_maintain_equipment_once(smith_chara_id: int, draw_flag: bool = True) -> str:
    """
    铁匠角色进行一次装备的维修保养\n
    输入：\n
    smith_chara_id: int 铁匠角色id\n
    draw_flag: bool 是否绘制结果\n
    输出：\n
    str 操作结果描述
    """
    # 是否优先维修
    repair_equipment_first = cache.rhodes_island.equipment_maintain_setting.get(3, 0) == 0

    # 维修与保养的初始化
    repair_flag, maintain_flag = False, False
    repair_text, maintain_text = "", ""
    target_id = 0
    # 如果铁匠有在维修中的装备，则直接获取该角色id
    if smith_chara_id in cache.rhodes_island.maintenance_equipment_chara_id:
        target_id = cache.rhodes_island.maintenance_equipment_chara_id[smith_chara_id]
        npc_data = cache.character_data[target_id]
        # 如果该角色装备未损坏或在保养中，则跳过维修
        if npc_data.cloth.equipment_condition >= 0:
            # 保养
            maintain_flag, maintain_text = maintain_equipment(smith_chara_id, target_id)
        else:
            # 直接维修
            repair_flag, repair_text = repair_equipment(smith_chara_id, target_id)

    # 先维修
    if repair_equipment_first:
        # 如果未指定维修成功，则随机选择维修
        if repair_flag == False:
            repair_flag, repair_text = repair_equipment(smith_chara_id)
        # 如果未维修，则进行保养
        if repair_flag == False and maintain_flag == False:
            maintain_flag, maintain_text = maintain_equipment(smith_chara_id)
    # 先保养
    else:
        # 如果未指定保养成功，则随机选择保养
        if maintain_flag == False:
            maintain_flag, maintain_text = maintain_equipment(smith_chara_id)
        # 如果未保养，则进行维修
        if maintain_flag == False and repair_flag == False:
            repair_flag, repair_text = repair_equipment(smith_chara_id)
    
    # 绘制结果
    if draw_flag:
        info_draw = draw.NormalDraw()
        info_draw.text = ""
        if repair_text:
            info_draw.text += repair_text + "\n"
        if maintain_text:
            info_draw.text += maintain_text + "\n"
        # 如果没有维修或保养成功，则返回提示
        if not repair_text and not maintain_text:
            info_draw.text = _("没有可维修或可保养的装备。")
        info_draw.draw()
    return repair_flag or maintain_flag


def repair_equipment(smith_chara_id: int, target_chara_id : int = 0) -> str:
    """
    铁匠角色进行一次装备的维修
    输入：
    smith_chara_id: int 铁匠角色id
    target_chara_id: int 目标角色id，如果为0则自动选择
    输出：str 操作结果描述
    """
    # 获取铁匠角色数据和维修能力
    smith_chara_data = cache.character_data[smith_chara_id]
    ability_lv = smith_chara_data.ability[48]
    maintain_value = attr_calculation.get_ability_adjust(ability_lv) / 2
    # 根据随机数变成0.8~1.2倍
    maintain_value *= random.uniform(0.8, 1.2)
    # 获取维修优先度设置
    maintain_priority = cache.rhodes_island.equipment_maintain_setting.get(0, 0)

    # 是否进行装备维修
    repair_flag = False
    repair_text = ""
    
    # 如果没有指定目标，则查找所有损坏装备的角色
    if target_chara_id == 0:
        repair_list = []
        for npc_id in cache.npc_id_got:
            if npc_id == 0:
                continue
            npc_data = cache.character_data[npc_id]
            cond = npc_data.cloth.equipment_condition
            if cond < 0:
                repair_list.append((npc_id, cond))
        if repair_list:
            # 按优先度排序
            if maintain_priority == 0:
                # 优先低损坏度
                repair_list.sort(key=lambda x: x[1], reverse=False)
            else:
                # 优先高损坏度
                repair_list.sort(key=lambda x: x[1], reverse=True)
            target_chara_id, cond = repair_list[0]
    # 如果有需要维修的角色，则进行维修，最大为0
    if target_chara_id > 0:
        npc_data = cache.character_data[target_chara_id]
        # 如果工作是铁匠，则记录维修角色
        if handle_premise.handle_work_is_blacksmith(smith_chara_id):
            cache.rhodes_island.maintenance_equipment_chara_id[smith_chara_id] = target_chara_id
        npc_data.cloth.equipment_condition = min(npc_data.cloth.equipment_condition + maintain_value, 0)
        repair_flag = True
        new_condition_text = get_equipment_condition_name(npc_data.cloth.equipment_condition)
        repair_text = _("{0}维修了{1}的装备，当前情况：{2} ({3})\n").format(smith_chara_data.name, npc_data.name, new_condition_text, round(npc_data.cloth.equipment_condition, 1))
        # 如果维修后装备已无损坏，则清除维修记录
        if smith_chara_id in cache.rhodes_island.maintenance_equipment_chara_id and npc_data.cloth.equipment_condition >= 0:
            del cache.rhodes_island.maintenance_equipment_chara_id[smith_chara_id]
            # 结算成就
            cache.achievement.equipment_repair_count += 1
            # achievement_panel.achievement_flow(_("维修"))
    return repair_flag, repair_text


def maintain_equipment(smith_chara_id: int, target_chara_id : int = 0) -> str:
    """
    铁匠角色进行一次装备的保养
    输入：
    smith_chara_id: int 铁匠角色id
    target_chara_id: int 目标角色id，如果为0则自动选择
    输出：str 操作结果描述
    """
    # 获取铁匠角色数据和维修能力
    smith_chara_data = cache.character_data[smith_chara_id]
    ability_lv = smith_chara_data.ability[48]
    maintain_value = attr_calculation.get_ability_adjust(ability_lv) / 4
    # 根据随机数变成0.8~1.2倍
    maintain_value *= random.uniform(0.8, 1.2)
    # 是否进行装备保养
    maintain_enable = cache.rhodes_island.equipment_maintain_setting.get(1, 0)
    # 保养对象设置
    maintain_target = cache.rhodes_island.equipment_maintain_setting.get(2, 0)
    # 保养目标名单
    maintain_operator_ids = cache.rhodes_island.equipment_maintain_operator_ids if hasattr(cache.rhodes_island, 'equipment_maintain_operator_ids') else []

    # 是否进行装备保养
    maintain_flag = False
    maintain_text = ""
    
    # 如果没有指定目标，则查找可选目标
    if target_chara_id == 0:
        # 获取保养候选
        if maintain_target == 0:
            # 全部干员
            candidate_ids = [i for i in cache.npc_id_got if i != smith_chara_id]
        else:
            # 仅指定目标
            candidate_ids = [i for i in maintain_operator_ids if i != smith_chara_id]
        maintain_list = []
        for npc_id in candidate_ids:
            npc_data = cache.character_data[npc_id]
            cond = npc_data.cloth.equipment_condition
            if cond < maintain_enable:
                maintain_list.append((npc_id, cond))
        if maintain_list:
            # 优先低损坏度
            maintain_list.sort(key=lambda x: x[1])
            target_chara_id, cond = maintain_list[0]
    # 如果有需要保养的角色，则进行保养，最大为0
    if target_chara_id > 0:
        npc_data = cache.character_data[target_chara_id]
        # 如果工作是铁匠，则记录维修角色
        if handle_premise.handle_work_is_blacksmith(smith_chara_id):
            cache.rhodes_island.maintenance_equipment_chara_id[smith_chara_id] = target_chara_id
        npc_data.cloth.equipment_condition = min(npc_data.cloth.equipment_condition + maintain_value, maintain_enable)
        maintain_flag = True
        new_condition_text = get_equipment_condition_name(npc_data.cloth.equipment_condition)
        maintain_text = _("{0}保养了{1}的装备，当前情况：{2} ({3})\n").format(smith_chara_data.name, npc_data.name, new_condition_text, round(npc_data.cloth.equipment_condition, 1))
        # 如果保养后装备已达到保养目标，则清除保养记录
        if smith_chara_id in cache.rhodes_island.maintenance_equipment_chara_id and npc_data.cloth.equipment_condition >= maintain_enable:
            del cache.rhodes_island.maintenance_equipment_chara_id[smith_chara_id]
            # 结算成就
            cache.achievement.equipment_maintenance_count += 1
            # achievement_panel.achievement_flow(_("保养"))
    return maintain_flag, maintain_text


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
            return_list = []
            title_draw.draw()
            line_feed.draw()
            # 维护策略按钮
            button_text1 = _("[001]指定维护策略")
            button_draw1 = draw.LeftButton(
                button_text1, button_text1, len(button_text1) * 3, cmd_func=self.select_maintain_strategy
            )
            button_draw1.draw()
            return_list.append(button_draw1.return_text)
            line_feed.draw()
            # 变更铁匠人数按钮
            button_text2 = _("[002]变更铁匠人数")
            button_draw2 = draw.LeftButton(
                button_text2, button_text2, len(button_text2) * 3, cmd_func=manage_basement_panel.change_npc_work_out, args=self.width
            )
            button_draw2.draw()
            return_list.append(button_draw2.return_text)
            line_feed.draw()
            # 装备损坏一览按钮
            button_text3 = _("[003]干员装备损坏情况一览")
            button_draw3 = draw.LeftButton(
                button_text3, button_text3, len(button_text3) * 3, cmd_func=show_damaged_equipment
            )
            button_draw3.draw()
            return_list.append(button_draw3.return_text)
            line_feed.draw()
            # 装备保养一览按钮
            button_text4 = _("[004]干员装备保养情况一览")
            button_draw4 = draw.LeftButton(
                button_text4, button_text4, len(button_text4) * 3, cmd_func=show_maintained_equipment
            )
            button_draw4.draw()
            return_list.append(button_draw4.return_text)
            line_feed.draw()
            line_feed.draw()
            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _( "返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
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
            cache.rhodes_island.equipment_maintain_operator_ids.append(character_id)
