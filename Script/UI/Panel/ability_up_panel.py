from math import e
import re
from typing import Dict, List
from types import FunctionType

from numpy import info
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import see_character_info_panel, talent_up_panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    py_cmd,
    flow_handle,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, settle_behavior, handle_premise

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

class Characterabi_show_Text:
    """
    角色能力升级显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        self.character_data = cache.character_data[self.character_id]
        """ 角色数据 """

    def draw(self):
        """绘制对象"""
        self.return_list = []
        # 绘制标题#
        line_feed.draw()
        title_text = _("能力")
        type_line = draw.LittleTitleLineDraw(title_text, self.width, ":")
        type_line.draw()
        ability_list = game_config.config_ability_type_data
        for anility_type in ability_list:
            type_set = ability_list[anility_type]
            # 刻印单独处理
            if anility_type == 2:
                # 跳过玩家
                if self.character_id == 0:
                    continue
                # 遍历刻印
                for ability_id in type_set:
                    # 当前刻印等级
                    now_mark_level = self.character_data.ability[ability_id]
                    button_text = f" {game_config.config_ability[ability_id].name}   {now_mark_level} "
                    # 要求：已经记录了刻印升级条件，小于3级，不是负面刻印
                    if (
                        ability_id in game_config.config_mark_up_data_by_ability and 
                        now_mark_level < 3 and 
                        ability_id not in {17, 18}
                        ):
                        button_draw = draw.LeftButton(
                            _(button_text),
                            _(game_config.config_ability[ability_id].name),
                            self.width / 10,
                            cmd_func=self.mark_up_show,
                            args=(ability_id),
                        )
                        self.return_list.append(button_draw.return_text)
                        button_draw.draw()
                    # 要求：已经记录了刻印降级条件，大于0级
                    elif (
                        ability_id in game_config.config_mark_down_data_by_ability and 
                        now_mark_level > 0
                        ):
                        button_draw = draw.LeftButton(
                            _(button_text),
                            _(game_config.config_ability[ability_id].name),
                            self.width / 10,
                            cmd_func=self.mark_down_show,
                            args=(ability_id),
                        )
                        self.return_list.append(button_draw.return_text)
                        button_draw.draw()
                    # 未记录刻印升级条件的刻印
                    else:
                        button_draw = draw.LeftButton(
                            _(button_text),
                            _(game_config.config_ability[ability_id].name),
                            self.width / 10,
                            normal_style='deep_gray',
                            cmd_func=self.mark_can_up_show,
                        )
                        self.return_list.append(button_draw.return_text)
                        button_draw.draw()
            else:
                for ability_id in type_set:
                    # 去掉与性别不符的感度与扩张
                    if self.character_data.sex == 0:
                        if ability_id in {2, 4, 7, 9, 12, 73, 74}:
                            continue
                    elif self.character_data.sex == 1:
                        if ability_id == 3:
                            continue
                    # 这个_1是为了补空格让格式对齐#
                    now_exp = 0
                    now_exp = self.character_data.ability[ability_id]
                    button_text = " "
                    button_text += game_config.config_ability[ability_id].name
                    button_text += " "
                    # 根据不同的类型补不同数量的空格#
                    if anility_type != 2 and anility_type != 4 and anility_type != 6:
                        button_text += "  "
                        if anility_type == 3 or anility_type == 5:
                            button_text += "  "
                    button_text += attr_calculation.judge_grade(now_exp)
                    button_text += " "
                    button_text += str(now_exp)
                    now_abi_up_panel = Characterabi_cmd_Text(self.character_id, self.width, ability_id)
                    button_draw = draw.LeftButton(
                        _(button_text),
                        _(game_config.config_ability[ability_id].name),
                        self.width / 10,
                        cmd_func=now_abi_up_panel.draw)
                    self.return_list.append(button_draw.return_text)
                    button_draw.draw()
                    # py_cmd.clr_cmd()
                    # if yrn == self.back_draw.return_text:
                    #     break
            # 只有不是最后一个类型就补个换行#
            if anility_type != 6:
                new_draw_n = draw.NormalDraw()
                new_draw_n.text = "\n"
                new_draw_n.width = 1
                new_draw_n.draw()
        # yrn = flow_handle.askfor_all(self.return_list)

    def mark_up_show(self, ability_id: int):
        """显示刻印升级面板"""
        # 获取刻印升级数据
        now_mark_level = self.character_data.ability[ability_id]
        mark_up_data_id = game_config.config_mark_up_data_by_ability[ability_id][now_mark_level]
        mark_up_data = game_config.config_mark_up_data[mark_up_data_id]
        need_state_all_value = mark_up_data.need_state_all_value
        now_state_all_value, state_text = settle_behavior.get_now_state_all_value_and_text_from_mark_up_data(mark_up_data_id, self.character_id)
        # 文本信息
        info_text = _("○部分刻印除了其原本的升级获取方式之外，还可以通过消耗大量宝珠来直接升级\n\n")
        info_text += _("当前刻印及等级为：{0}{1}\n").format(game_config.config_ability[ability_id].name, now_mark_level)
        info_text += _("升级需要的总值为：{0}\n").format(need_state_all_value)
        info_text += _("当前角色状态可以提供的总值为：")
        # 如果为空，则输出无
        if state_text == "":
            state_text = _("无")
        # 加到文本信息中
        info_text += state_text + "\n"
        # 需要的宝珠值为
        need_juel = int(need_state_all_value - now_state_all_value)
        need_juel = max(need_juel, 0)
        # 宝珠信息
        juel_type_id = mark_up_data.need_juel_type
        juel_name = game_config.config_juel[juel_type_id].name
        now_juel = self.character_data.juel[juel_type_id]
        juel_text = _("减去提供值后需要消耗的宝珠为：{0} {1}，当前拥有：{2}\n").format(juel_name, need_juel, now_juel)
        info_text += juel_text

        # 开始绘制
        while 1:
            return_list = []
            title_line = draw.TitleLineDraw(_("使用宝珠升级刻印"), self.width, ":")
            title_line.draw()
            line_feed.draw()
            # 绘制信息文本
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()
            line_feed.draw()
            # 如果当前宝珠足够，绘制升级按钮
            if now_juel >= need_juel:
                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width / 3, cmd_func=self.mark_up, args=(ability_id, need_juel))
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            # 绘制返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            # 等待玩家选择
            yrn = flow_handle.askfor_all(return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn in return_list:
                break

    def mark_down_show(self, ability_id: int):
        """显示刻印降级面板"""
        # 调整使用的宝珠
        # 获取刻印降级数据
        now_mark_level = self.character_data.ability[ability_id]
        mark_down_data_id = game_config.config_mark_down_data_by_ability[ability_id][now_mark_level]
        mark_down_data = game_config.config_mark_down_data[mark_down_data_id]
        need_juel_all_value = mark_down_data.need_juel_all_value
        # 宝珠信息
        juel_type_id_list = []
        juel_type_id_list.append(mark_down_data.need_juel_1)
        juel_type_id_list.append(mark_down_data.need_juel_2)
        juel_type_id_list.append(mark_down_data.need_juel_3)
        # 如果有1号，则替换为全快感珠
        if '1' in juel_type_id_list:
            juel_type_id_list.remove('1')
            for state_id in game_config.config_character_state:
                if game_config.config_character_state[state_id].type == 0:
                    juel_type_id_list.append(str(state_id))
        self.jewel_use_dict: Dict[int, int] = {}
        # 关押区的等级效果
        now_level = cache.rhodes_island.facility_level[19]
        facility_cid = game_config.config_facility_effect_data[_("关押区")][int(now_level)]
        facility_effect = game_config.config_facility_effect[facility_cid].effect
        # 文本信息
        info_text = _("○非正面刻印除了通过源石技艺降级之外，还可以通过消耗大量宝珠来直接降级\n\n")
        info_text += _("当前刻印及等级为：{0}{1}\n").format(game_config.config_ability[ability_id].name, now_mark_level)
        info_text += _("降级需要的总值为：{0}\n").format(need_juel_all_value)
        # 被关押区等级影响
        if handle_premise.handle_imprisonment_1(self.character_id):
            need_juel_all_value = int(need_juel_all_value * (1 - facility_effect / 100))
            info_text += _("该干员已被关押，当前关押区等级为{0}，降级所需宝珠值降低{1}%，降级所需宝珠值为{2}\n").format(now_level, facility_effect, need_juel_all_value)

        # 开始绘制
        while 1:
            mark_down_data_all_value = 0
            return_list = []
            title_line = draw.TitleLineDraw(_("使用宝珠降低刻印"), self.width, ":")
            title_line.draw()
            line_feed.draw()
            # 绘制信息文本
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()
            line_feed.draw()
            # 遍历可用宝珠
            for need_juel in juel_type_id_list:
                # 跳过空值
                if need_juel == '0':
                    continue
                if '|' in need_juel:
                    juel_id = int(need_juel.split('|')[0])
                    adjust = float(need_juel.split('|')[1])
                else:
                    juel_id = int(need_juel)
                    adjust = 1
                # 初始化使用量
                self.jewel_use_dict.setdefault(juel_id, 0)
                jewel_name = game_config.config_juel[juel_id].name
                now_jewel_value = int(self.jewel_use_dict[juel_id] * adjust)
                # 绘制调整按钮
                button_text = _("[{0}]{1} 当前用量:{2}，当前总值{3}").format(juel_id, jewel_name, self.jewel_use_dict[juel_id], now_jewel_value)
                btn = draw.LeftButton(button_text, _(jewel_name), self.width, cmd_func=self.input_juel_count, args=(juel_id, adjust, mark_down_data_all_value, need_juel_all_value))
                btn.draw()
                return_list.append(btn.return_text)
                mark_down_data_all_value += now_jewel_value
                line_feed.draw()
            # 计算当前宝珠总值
            juel_info_text = ("\n当前宝珠总值为：{0}\n").format(mark_down_data_all_value)
            info_draw.text = juel_info_text
            info_draw.draw()
            line_feed.draw()
            # 如果当前宝珠足够，绘制降低按钮
            yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width / 3, cmd_func=self.mark_down, args=(ability_id))
            if mark_down_data_all_value >= need_juel_all_value:
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            # 绘制返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            # 等待玩家选择
            yrn = flow_handle.askfor_all(return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn == back_draw.return_text or yrn == yes_draw.return_text:
                break

    def input_juel_count(self, juel_id: int, adjust: float, mark_down_data_all_value: int, need_juel_all_value: int):
        """
        输入宝珠使用量
        参数:
        juel_id: int -- 宝珠id
        adjust: float -- 宝珠调整值
        mark_down_data_all_value: int -- 当前宝珠总值
        need_juel_all_value: int -- 需要的宝珠总值
        """
        max_count = self.character_data.juel[juel_id]
        guess_num = 0
        # 计算预计需要的宝珠数量
        if mark_down_data_all_value >= need_juel_all_value:
            guess_num = 0
        else:
            guess_num = int((need_juel_all_value - mark_down_data_all_value) / adjust)
        ask_text = _("\n请输入要使用的宝珠数量，最多可以使用{0}个{1}，当前使用量为{2}，预计需要{3}个\n").format(max_count, game_config.config_juel[juel_id].name, self.jewel_use_dict[juel_id], guess_num)
        ask_panel = panel.AskForOneMessage()
        ask_panel.set(ask_text, 99)
        # 获取输入
        get_text = ask_panel.draw()
        # 如果输入不是数字，则返回
        if get_text.isdigit() == False:
            return
        new_num = int(get_text)
        if new_num < 0:
            new_num = 0
        elif new_num > max_count:
            new_num = max_count
        self.jewel_use_dict[juel_id] = new_num

    def mark_up(self, ability_id: int, need_juel: int):
        """升级刻印"""
        now_mark_level = self.character_data.ability[ability_id]
        mark_up_data_id = game_config.config_mark_up_data_by_ability[ability_id][now_mark_level]
        mark_up_data = game_config.config_mark_up_data[mark_up_data_id]
        # 扣除宝珠
        juel_type_id = mark_up_data.need_juel_type
        self.character_data.juel[juel_type_id] -= need_juel
        # 刻印等级+1
        self.character_data.ability[ability_id] += 1
        # 赋予二段行为
        second_behavior_id = mark_up_data.second_behavior
        self.character_data.second_behavior[second_behavior_id] = 1
        # 结算二段行为
        settle_behavior.second_behavior_effect(self.character_id, game_type.CharacterStatusChange(), [second_behavior_id])

    def mark_down(self, ability_id: int):
        """降级刻印"""
        # 刻印等级-1
        self.character_data.ability[ability_id] -= 1
        # 扣除宝珠
        for juel_id in self.jewel_use_dict:
            # 扣除宝珠
            self.character_data.juel[juel_id] -= self.jewel_use_dict[juel_id]
        # 输出降级信息
        info_draw = draw.WaitDraw()
        info_draw.text = _("\n刻印降级成功，{0}降至{1}级\n").format(game_config.config_ability[ability_id].name, self.character_data.ability[ability_id])
        info_draw.style = "gold_enrod"
        info_draw.draw()


    def mark_can_up_show(self):
        """显示无法升级的刻印信息"""
        now_draw = draw.WaitDraw()
        now_draw.text = _("\n该刻印当前无法使用宝珠升级\n")
        now_draw.draw()

class Characterabi_cmd_Text:
    """
    角色能力升级指令面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    ability_id -- 能力id
    """

    def __init__(self, character_id: int, width: int, ability_id: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.ability_id = ability_id
        """ 当前的能力id """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        self.character_data = cache.character_data[self.character_id]
        """ 角色数据 """
        self.ability_level = self.character_data.ability[ability_id]
        """ 能力等级 """

    def draw(self):
        """绘制对象"""
        self.return_list = []
        self.jule_dict = {}
        judge = 1
        # 绘制标题#
        while 1:
            # 如果已经到最高级就不绘制了#
            if self.ability_level == 8:
                break

            # 读取该能力在对应等级下的升级需求
            need_list = game_config.config_ability_up_data[self.ability_id][self.ability_level]
            line = draw.LineDraw(".", self.width)
            line.draw()
            line_feed.draw()

            # 遍历升级需求，并输出信息
            for need_text in need_list:
                # print(f"debug need_text = {need_text}")
                need_type = need_text.split('|')[0][0]
                need_type_id = int(need_text.split('|')[0][1:])
                need_value = int(need_text.split('|')[1])
                if need_type == "A":
                    abi_name = game_config.config_ability[need_type_id].name
                    now_value = self.character_data.ability[need_type_id]
                    button_text = _("需要能力 : {0} 至少为{1}，当前为{2}\n").format(abi_name, need_value, now_value)
                elif need_type == "J":
                    juel_name = game_config.config_juel[need_type_id].name
                    now_value = self.character_data.juel[need_type_id]
                    button_text = _("需要宝珠 : {0} 至少为{1}，当前为{2}\n").format(juel_name, need_value, now_value)
                    self.jule_dict[need_type_id] = need_value
                elif need_type == "E":
                    experience_name = game_config.config_experience[need_type_id].name
                    now_value = self.character_data.experience[need_type_id]
                    button_text = _("需要经验 : {0} 至少为{1}，当前为{2}\n").format(experience_name, need_value, now_value)
                if now_value < need_value:
                    judge = 0
                now_draw = draw.NormalDraw()
                now_draw.text = button_text
                now_draw.draw()

            # 技巧的额外处理
            if self.ability_id == 30:
                # 玩家的情况
                if self.character_id == 0:
                    now_ability_level = self.character_data.ability[self.ability_id]
                    now_other_ability_level = 0
                    for tem_ability_cid in game_config.config_ability:
                        if game_config.config_ability[tem_ability_cid].ability_type == 5:
                            now_other_ability_level += self.character_data.ability[tem_ability_cid]
                    info_text = _("博士的技巧升级需要额外满足以下条件：\n")
                    info_text += _("○[指技]、[舌技]、[腰技]、[隐蔽]能力等级之和大于等于技巧等级*2\n")
                    info_text += _("  当前技巧等级为{0}，当前[指技]、[舌技]、[腰技]等级之和为{1}\n").format(now_ability_level, now_other_ability_level)
                    if now_other_ability_level < now_ability_level * 2:
                        judge = 0
                    now_draw = draw.NormalDraw()
                    now_draw.text = info_text
                    now_draw.draw()
                # NPC的情况
                else:
                    now_ability_level = self.character_data.ability[self.ability_id]
                    now_other_ability_level = 0
                    for tem_ability_cid in game_config.config_ability:
                        if game_config.config_ability[tem_ability_cid].ability_type == 5:
                            now_other_ability_level += self.character_data.ability[tem_ability_cid]
                    info_text = _("干员的技巧升级需要额外满足以下条件：\n")
                    info_text += _("○全子性技的等级之和，即[指技]、[舌技]、[足技]、[胸技]、[膣技]、[肛技]、[隐蔽]能力等级之和大于等于技巧等级*3\n")
                    info_text += _("  当前技巧等级为{0}，当前全子性技的等级和为{1}\n").format(now_ability_level, now_other_ability_level)
                    if now_other_ability_level < now_ability_level * 3:
                        judge = 0
                    now_draw = draw.NormalDraw()
                    now_draw.text = info_text
                    now_draw.draw()

            # debug模式下无需判断
            if cache.debug_mode:
                judge = 1

            line_feed.draw()
            # 判断是否可以升级
            if self.ability_level == 8:
                now_draw = draw.NormalDraw()
                now_draw.text = _("已达到最高级\n")
                now_draw.draw()
                break
            elif judge:
                now_draw_succed = draw.NormalDraw()
                now_draw_succed.text = _("满足条件，要升级吗？\n")
                now_draw_succed.draw()
            else:
                now_draw_failed = draw.NormalDraw()
                now_draw_failed.text = _("不满足条件，无法升级\n")
                now_draw_failed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
            back_draw.draw()
            self.return_list.append(back_draw.return_text)
            if judge:
                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width / 3, cmd_func=self.level_up)
                yes_draw.draw()
                self.return_list.append(yes_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn in self.return_list:
                break

    def level_up(self):
        for need_type_id in self.jule_dict:
            cache.character_data[self.character_id].juel[need_type_id] -= self.jule_dict[need_type_id]
        cache.character_data[self.character_id].ability[self.ability_id] += 1


class Character_abi_up_main_Handle:
    """
    带返回的角色能力上升主面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    character_list -- 角色id列表
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
        now_panel_id = _("属性升级")
        while 1:
            self.return_list = []
            now_character_panel = Character_abi_up_sub_Handle(self.character_id, self.width)
            now_character_panel.change_panel(now_panel_id)
            now_character_panel.draw()
            back_draw.draw()
            line_feed.draw()
            self.return_list.extend(now_character_panel.return_list)
            self.return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn == back_draw.return_text:
                break
            elif yrn in now_character_panel.draw_data:
                now_panel_id = yrn


class Character_abi_up_sub_Handle:
    """
    角色能力上升子面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel: str = _("属性升级")
        """ 当前的属性页id """
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        main_first_draw = Character_abi_up_main_panel(character_id, width)
        self.draw_data = {
            _("属性升级"): main_first_draw,
        }
        """ 按钮文本对应属性面板 """
        self.handle_panel = panel.CenterDrawButtonListPanel()
        """ 属性列表的控制面板 """
        self.handle_panel.set(
            [f"[{text}]" for text in self.draw_data.keys()],
            list(self.draw_data.keys()),
            width,
            4,
            f"[{self.now_panel}]",
            self.change_panel,
        )

    def change_panel(self, panel_id: str):
        """
        切换当前面板
        Keyword arguments:
        panel_id -- 要切换的面板id
        """
        self.now_panel = panel_id
        self.handle_panel.set(
            [f"[{text}]" for text in self.draw_data.keys()],
            list(self.draw_data.keys()),
            self.width,
            4,
            f"[{self.now_panel}]",
            self.change_panel,
        )

    def draw(self):
        """绘制面板"""
        self.draw_data[self.now_panel].draw()
        self.return_list = []
        self.return_list.extend(self.draw_data[self.now_panel].return_list)
        line_feed.draw()
        line = draw.LineDraw("=", self.width)
        line.draw()
        self.handle_panel.draw()
        self.return_list.extend(self.handle_panel.return_list)


class Character_abi_up_main_panel:
    """
    角色能力升级面板第一页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = see_character_info_panel.CharacterInfoHead(character_id, width)
        Juel_draw = see_character_info_panel.CharacterJuelText(character_id, width, 8, 0)
        Experience_draw = see_character_info_panel.CharacterExperienceText(character_id, width, 8, 0)
        abi_draw = Characterabi_show_Text(character_id, width)
        tal_draw = talent_up_panel.Character_talent_show_Text(character_id, width)
        if character_id == 0:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                Juel_draw,
                Experience_draw,
                abi_draw,
            ]
        else:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                Juel_draw,
                Experience_draw,
                abi_draw,
                tal_draw,
            ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()
            if "return_list" in label.__dict__:
                self.return_list.extend(label.return_list)
