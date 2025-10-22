from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise, instuct_judege
from Script.Settle import default
from Script.UI.Panel import achievement_panel

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

class Sex_Be_Discovered_Panel:
    """
    H中被发现后的选择面板
    Keyword arguments:
    width -- 绘制宽度
    character_id -- 触发事件的角色id
    """

    def __init__(self, width: int, character_id: int = 0):
        """初始化绘制对象"""
        self.width = width
        """ 绘制宽度 """
        self.character_id = character_id
        """ 发现H的角色id """
        self.find_chara_data: game_type.Character = cache.character_data[self.character_id]
        """ 发现H的角色数据 """
        self.pl_chara_data: game_type.Character = cache.character_data[0]
        """ 玩家角色数据 """
        self.target_chara_data = cache.character_data[self.pl_chara_data.target_character_id]
        """ 玩家交互对象数据 """

    def draw(self) -> None:
        """绘制面板"""

        title_draw = draw.TitleLineDraw(_("H中被发现"), self.width)

        # 性行为情况名
        sex_type_text = _("你正在和{0}单独H").format(self.target_chara_data.name)
        if handle_premise.handle_hidden_sex_mode_ge_1(0):
            sex_type_text = _("你和{0}的隐奸").format(self.target_chara_data.name)
        elif handle_premise.handle_exhibitionism_sex_mode_ge_1(0):
            sex_type_text = _("你和{0}的露出").format(self.target_chara_data.name)
        elif handle_premise.handle_is_unconscious_h(0):
            sex_type_text = _("你正在无意识奸{0}").format(self.target_chara_data.name)
        elif handle_premise.handle_t_npc_active_h(0):
            sex_type_text = _("{0}正在逆推你").format(self.target_chara_data.name)
        elif handle_premise.handle_group_sex_mode_on(0):
            sex_type_text = _("你正在和{0}等多人群交").format(self.target_chara_data.name)

        find_text = _("\n{0}发现了{1}，要怎么做？\n").format(
            self.find_chara_data.name,
            sex_type_text,
        )

        # 记录发现者名字
        self.pl_chara_data.behavior.h_interrupt_chara_name = self.find_chara_data.name
        # 重置发现者的逆推状态
        default.handle_masturebate_to_pl_flag_0(self.character_id, 1, game_type.CharacterStatusChange(), cache.game_time)
        # 发现者的目标对象转为玩家
        default.handle_target_to_player(self.character_id, 1, game_type.CharacterStatusChange(), cache.game_time)
        # 发现者获得目击H的flag
        default.handle_see_pl_h(self.character_id, 1, game_type.CharacterStatusChange(), cache.game_time)
        # 发现者的行为持续时间设为保底1分钟
        self.find_chara_data.behavior.duration = 1

        while 1:

            return_list: List[str] = []
            title_draw.draw()
            info_draw = draw.NormalDraw()
            info_draw.text = find_text
            info_draw.draw()
            line_feed.draw()

            talk_button = draw.LeftButton(
                _("[1]用花言巧语支开对方"),
                "1",
                self.width,
                cmd_func=self._let_find_chara_away,
            )
            talk_button.draw()
            return_list.append(talk_button.return_text)
            line_feed.draw()

            # 需要非隐奸、非群交
            if not handle_premise.handle_hidden_sex_mode_ge_1(0) and not handle_premise.handle_group_sex_mode_on(0):
                hidden_button = draw.LeftButton(
                    _("[2]迅速地隐藏起来，转为隐奸"),
                    "2",
                    self.width,
                    cmd_func=self._switch_to_hidden_sex
                )
                hidden_button.draw()
                return_list.append(hidden_button.return_text)
                line_feed.draw()

            # 需要非露出、非群交
            if not handle_premise.handle_exhibitionism_sex_mode_ge_1(0) and not handle_premise.handle_group_sex_mode_on(0):
                exhibitionism_button = draw.LeftButton(
                    _("[3]光明正大地展示，转为露出"),
                    "3",
                    self.width,
                    cmd_func=self._continue_exhibitionism_sex,
                )
                exhibitionism_button.draw()
                return_list.append(exhibitionism_button.return_text)
                line_feed.draw()
            # 如果是正在露出，则显示为继续露出
            elif handle_premise.handle_exhibitionism_sex_mode_ge_1(0):
                exhibitionism_button = draw.LeftButton(
                    _("[3]无视对方，正常继续"),
                    "3",
                    self.width,
                    cmd_func=self._continue_exhibitionism_sex,
                )
                exhibitionism_button.draw()
                return_list.append(exhibitionism_button.return_text)
                line_feed.draw()

            group_button = draw.LeftButton(
                _("[4]邀请对方加入群交"),
                "4",
                self.width,
                cmd_func=self._invite_find_char_to_join,
            )
            group_button.draw()
            return_list.append(group_button.return_text)
            line_feed.draw()

            cancel_button = draw.LeftButton(
                _("[5]尴尬地结束H"),
                "5",
                self.width,
                cmd_func=self._end_current_h,
            )
            cancel_button.draw()
            return_list.append(cancel_button.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def _let_find_chara_away(self) -> None:
        """选择用花言巧语支开对方"""
        pass_flag = False
        now_draw_text = ""
        if self.find_chara_data.talent[222]:
            now_draw_text = _("{0}还不懂这是什么意义，被你随口糊弄走了\n").format(self.find_chara_data.name)
            pass_flag = True
        elif instuct_judege.calculation_instuct_judege(0, self.character_id, _("目击H后被话术支开"))[0]:
            pass_flag = True
        # 如果通过
        if pass_flag:
            self.find_chara_data.behavior.behavior_id = constant.Behavior.SEE_H_BUT_DECEIVED
            self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
            # 绘制结果
            now_draw = draw.NormalDraw()
            now_draw.text = now_draw_text
            now_draw.draw()
        # 未通过
        else:
            self._end_current_h()

    def _switch_to_hidden_sex(self) -> None:
        """选择转为隐奸"""
        from Script.UI.Panel.hidden_sex_panel import Select_Hidden_Sex_Mode_Panel
        select_panel = Select_Hidden_Sex_Mode_Panel(self.width, sex_be_discovered_flag = True)
        select_panel.draw()
        # 如果邀请失败，则结束当前H
        if self.pl_chara_data.behavior.behavior_id == constant.Behavior.H_INTERRUPT:
            self._end_current_h()
        else:
            # 结算成就
            if self.pl_chara_data.sp_flag.hidden_sex_mode == 1:
                achievement_panel.get_achievement_judge_by_value(914, 1)

    def _continue_exhibitionism_sex(self) -> None:
        """选择转为露出"""
        # 如果当前已经是露出模式
        if handle_premise.handle_exhibitionism_sex_mode_ge_1(0):
            # 判断对方的实行值
            # 如果是也愿意露出的等级，则无视
            if instuct_judege.calculation_instuct_judege(0, self.character_id, _("露出"))[0]:
                self.find_chara_data.behavior.behavior_id = constant.Behavior.SEE_H_BUT_IGNORE
                self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
            # 如果是能接受H的等级，则自己离开
            elif instuct_judege.calculation_instuct_judege(0, self.character_id, _("H模式"))[0]:
                self.find_chara_data.behavior.behavior_id = constant.Behavior.SEE_H_AND_LEAVE
                self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
            # 否则打断当前H
            else:
                self._end_current_h()
        else:
            from Script.UI.Panel.exhibitionism_sex_panel import Select_Exhibitionism_Sex_Mode_Panel
            select_panel = Select_Exhibitionism_Sex_Mode_Panel(self.width, sex_be_discovered_flag = True)
            select_panel.draw()
            # 如果邀请失败，则结束当前H
            if self.pl_chara_data.behavior.behavior_id == constant.Behavior.H_INTERRUPT:
                self._end_current_h()

    def _invite_find_char_to_join(self) -> None:
        """选择邀请对方加入群交"""
        from Script.Design import handle_instruct
        # 判断是否满足加入群交条件
        if handle_premise.handle_instruct_judge_group_sex(self.character_id):
            # 如果当前在群交中，则直接加入
            if handle_premise.handle_group_sex_mode_on(0):
                self.find_chara_data.behavior.behavior_id = constant.Behavior.JOIN_GROUP_SEX
                self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
            # 不在群交中则转为群交
            else:
                self.find_chara_data.behavior.behavior_id = constant.Behavior.DISCOVER_OTHER_SEX_AND_JOIN
                self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.OTHER_SEX_BE_FOUND_TO_GROUP_SEX)
                # 结算成就
                achievement_panel.get_achievement_judge_by_value(905, 1)
        else:
            # 如果当前在群交中，则拒绝加入
            if handle_premise.handle_group_sex_mode_on(0):
                self.find_chara_data.behavior.behavior_id = constant.Behavior.REFUSE_JOIN_GROUP_SEX
                self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
            # 不在群交中则结束当前H
            else:
                self._end_current_h()

    def _end_current_h(self) -> None:
        """选择结束当前H"""
        from Script.Design import handle_instruct, character_behavior
        # 交互对象进入被打断状态
        self.target_chara_data.action_info.h_interrupt = 1
        # 发现者变为打断行为
        self.find_chara_data.behavior.behavior_id = constant.Behavior.SEE_H_AND_INTERRUPT
        self.find_chara_data.behavior.duration = game_config.config_behavior[self.find_chara_data.behavior.behavior_id].duration
        # 手动结算该状态
        character_behavior.judge_character_status(self.character_id)
        # 如果是在群交中，则结束群交
        if handle_premise.handle_group_sex_mode_on(0):
            self.pl_chara_data.behavior.behavior_id = constant.Behavior.GROUP_SEX_END
            handle_instruct.handle_group_sex_end()
        # 否则结束当前H
        else:
            # 玩家变为被打断行为
            self.pl_chara_data.behavior.behavior_id = constant.Behavior.H_INTERRUPT
            # 调用结束H处理
            handle_instruct.handle_end_h()
