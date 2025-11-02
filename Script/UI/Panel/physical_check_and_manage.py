from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.Design import handle_premise, handle_instruct, attr_calculation, game_time, attr_text
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
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


def settle_health_check():
    """
    结算体检
    """
    # 重置今日体检数据
    cache.rhodes_island.today_physical_examination_chara_id_dict = {}
    # 如果开启了定期体检
    if handle_premise.handle_periodic_health_check_on(0):
        # 如果今天是体检日，则抽选今日要体检的干员
        if handle_premise.handle_today_is_healty_check_day(0):
            need_physical_examination_chara_id_list = []
            # 遍历所有干员
            for chara_id in cache.npc_id_got:
                if chara_id == 0:
                    continue
                # 重置今日体检时间数据
                cache.character_data[chara_id].action_info.health_check_today = 0
                handle_premise.settle_chara_unnormal_flag(chara_id, 3)
                # 如果干员在体检名单中，则加入要体检的干员列表
                if handle_premise.handle_self_in_health_check_list(chara_id):
                    need_physical_examination_chara_id_list.append(chara_id)
            # 今日的要体检人数
            need_chara_num = int(cache.rhodes_island.physical_examination_setting[6]) + 1
            final_physical_examination_chara_id_list = []
            # 如果要体检的人数大于等于干员总数，则全体体检
            if need_chara_num >= len(need_physical_examination_chara_id_list):
                final_physical_examination_chara_id_list = need_physical_examination_chara_id_list
            else:
                # 随机抽取要体检的干员
                final_physical_examination_chara_id_list = random.sample(need_physical_examination_chara_id_list, need_chara_num)
            # 遍历要体检的干员，一半的几率上午体检，一半的几率下午体检
            for chara_id in final_physical_examination_chara_id_list:
                now_character_data = cache.character_data[chara_id]
                if random.randint(0, 1) == 0:
                    now_character_data.action_info.health_check_today = 1
                else:
                    now_character_data.action_info.health_check_today = 2
                handle_premise.settle_chara_unnormal_flag(chara_id, 3)
        # 重置周期内的已体检干员数据
        if cache.rhodes_island.physical_examination_setting[3] == 0:
            # 每年重置一次
            if cache.game_time.month == 3 and cache.game_time.day == 1:
                cache.rhodes_island.examined_operator_ids = set()
        elif cache.rhodes_island.physical_examination_setting[3] == 1:
            # 每月重置一次
            if cache.game_time.day == 1:
                cache.rhodes_island.examined_operator_ids = set()
        elif cache.rhodes_island.physical_examination_setting[3] == 2:
            # 每周重置一次
            if cache.game_time.weekday() == 0:
                cache.rhodes_island.examined_operator_ids = set()
        elif cache.rhodes_island.physical_examination_setting[3] == 3:
            # 每天重置一次
            cache.rhodes_island.examined_operator_ids = set()


class Physical_Check_And_Manage_Panel:
    """
    用于身体检查与管理的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("身体检查与管理")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的角色数据 """
        self.done_check_behavior_id_set = set()
        """ 已经检查过的行为id集合 """

    def draw(self):
        """绘制对象"""

        title_text = _("身体检查与管理")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            self.pl_character_data = cache.character_data[0] # 更新玩家的角色数据
            target_character_id = self.pl_character_data.target_character_id
            target_character_data = cache.character_data[target_character_id]
            return_list = []
            title_draw.draw()
            cinfo_draw = draw.NormalDraw()
            info_text = _("\n要做什么呢？\n")
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            # 如果对象已经在体检数据中，则直接显示体检数据
            if target_character_id in cache.rhodes_island.today_physical_examination_chara_id_dict:
                self.done_check_behavior_id_set = cache.rhodes_island.today_physical_examination_chara_id_dict[target_character_id]
                button1_text = _("[001]检查身体情况（今日已体检）")
                button1_draw = draw.NormalDraw()
                button1_draw.text = button1_text
                button1_draw.style = "deep_gray"
                button1_draw.width = self.width
                button1_draw.draw()
            elif handle_premise.handle_have_target(0):
                button1_text = _("[001]检查{0}的身体情况").format(target_character_data.name)
                button1_draw = draw.LeftButton(
                    _(button1_text),
                    _("1"),
                    self.width,
                    cmd_func=self.check_target_physical,
                    args=(target_character_id,),
                )
                line_feed.draw()
                button1_draw.draw()
                return_list.append(button1_draw.return_text)
            else:
                button1_text = _("[001]检查身体情况（当前没有查看对象）")
                button1_draw = draw.NormalDraw()
                button1_draw.text = button1_text
                button1_draw.style = "deep_gray"
                button1_draw.width = self.width
                button1_draw.draw()

            if len(self.done_check_behavior_id_set) > 0:
                button2_text = _("[002]对{0}进行身体管理").format(target_character_data.name)
                button2_draw = draw.LeftButton(
                    _(button2_text),
                    _("2"),
                    self.width,
                    cmd_func=self.manage_target_physical,
                    args=(target_character_id,),
                )
                line_feed.draw()
                button2_draw.draw()
                return_list.append(button2_draw.return_text)
            else:
                button2_text = _("\n[002]进行身体管理（需要先进行身体检查）")
                button2_draw = draw.NormalDraw()
                button2_draw.text = button2_text
                button2_draw.style = "deep_gray"
                button2_draw.width = self.width
                button2_draw.draw()

            if 1:
                button3_text = _("[003]取消身体管理")
                button3_draw = draw.LeftButton(
                    _(button3_text),
                    _("3"),
                    window_width,
                    cmd_func=self.cancle_physical_manage_panel,
                    args=(),
                    )
                line_feed.draw()
                button3_draw.draw()
                return_list.append(button3_draw.return_text)

            if 1:
                button4_text = _("[004]调整体检日程")
                button4_draw = draw.LeftButton(
                    _(button4_text),
                    _("4"),
                    window_width,
                    cmd_func=self.adjust_physical_check_schedule,
                    args=(),
                    )
                line_feed.draw()
                button4_draw.draw()
                return_list.append(button4_draw.return_text)

            if len(self.done_check_behavior_id_set) > 0:
                button11_text = _("[011]查看检查报告")
                button11_draw = draw.LeftButton(
                    _(button11_text),
                    _("11"),
                    window_width,
                    cmd_func=self.check_physcial_report,
                    args=(),
                    )
                line_feed.draw()
                button11_draw.draw()
                return_list.append(button11_draw.return_text)
            else:
                button11_text = _("\n[011]查看检查报告（需要先进行身体检查）")
                button11_draw = draw.NormalDraw()
                button11_draw.text = button11_text
                button11_draw.style = "deep_gray"
                button11_draw.width = window_width
                button11_draw.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                self.settle_finish_physical_check(target_character_id)
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def settle_finish_physical_check(self, target_character_id: int):
        """结算完成的体检"""
        # 如果已经体检了
        if len(self.done_check_behavior_id_set) > 0:
            target_character_data = cache.character_data[target_character_id]
            # 记录到今日已体检角色数据中
            cache.rhodes_island.today_physical_examination_chara_id_dict[target_character_id] = self.done_check_behavior_id_set
            # 加入周期内已体检角色名单
            cache.rhodes_island.examined_operator_ids.add(target_character_id)
            # 从等待体检名单中移除
            if target_character_id in cache.rhodes_island.waiting_for_exam_operator_ids:
                handle_premise.settle_chara_unnormal_flag(target_character_id, 3)
            # 清零今日体检时间
            target_character_data.action_info.health_check_today = 0
            cache.rhodes_island.waiting_for_exam_operator_ids.remove(target_character_id)

    def check_target_physical(self, target_character_id: int):
        """查看目标角色的身体情况"""
        target_character_data = cache.character_data[target_character_id]

        # 指令与前置指令的对应表
        cmd_able_dict = {
            "examine_hair_smoothness": "examine_hair",  # 测试头发
            "examine_sucking_and_swallowing": "examine_oral",  # 测试口腔
            "examine_armpit_clamping": "examine_armpit",  # 测试腋下
            "examine_nipple_and_areola": "examine_breast",  # 检查乳头
            "examine_breast_clamping": "examine_breast",  # 测试胸部
            "examine_hands_flexibility": "examine_hands",  # 测试手部
            "examine_foots_flexibility": "examine_foot",  # 测试足部
            "examine_vagina_and_folds": "examine_vulva_and_shape",  # 检查内阴
            "examine_hymen": "examine_vagina_and_folds",  # 检查处女膜
            "examine_orifice": "examine_vagina_and_folds",  # 检查子宫口
            "examine_vagina_firmness": "examine_vagina_and_folds",  # 测试阴道
            "examine_intestine_firmness": "examine_anus",  # 测试肠道
            "examine_urination_status": "examine_urethra",  # 测试排尿
            "examine_urethra_firmness": "examine_urethra",  # 测试尿道
            "examine_tail_flexibility": "examine_tail",  # 测试尾巴
            "examine_horn_sensitivity": "examine_horn",  # 测试兽角
            "examine_ears_sensitivity": "examine_ears",  # 测试兽耳
            "examine_wing_flexibility": "examine_wing",  # 测试翅膀
            "examine_ring_sensitivity": "examine_ring",  # 测试光环
            "examine_tentacle_flexibility": "examine_tentacle",  # 测试触手
        }

        # 部位与素质的对应表
        body_talent_map = {
            "examine_tail": 113,  # 尾巴
            "examine_tail_flexibility": 113,  # 尾巴
            "examine_horn": 112,  # 兽角
            "examine_ears": 111,  # 兽耳
            "examine_wing": 115,  # 翅膀
            "examine_ring": 114,  # 光环
            "examine_tentacle": 116   # 触手
        }

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()
            py_cmd.clr_cmd()
            # 获取医术等级与可用次数，次数为(等级+1)*4-已使用次数
            now_ability_lv = self.pl_character_data.ability[46]
            done_times = len(self.done_check_behavior_id_set)
            now_ability_times = (now_ability_lv + 1) * 4 - done_times
            # 绘制提示信息
            info_text = _("\n可以进行的检查项目/已进行的检查项目：{0}/{1}（每级医术技能+4）\n").format(now_ability_times, done_times)
            info_text += _("请选择要对{0}进行的身体检查：\n\n").format(target_character_data.name)
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()
            # 检索所有的身体检查状态
            count = 0
            for behavior_id in game_config.config_behavior:
                behavior_data = game_config.config_behavior[behavior_id]
                # 跳过非检查类的行为
                if "检查" not in behavior_data.tag:
                    continue
                behavior_text = f"[{str(count).rjust(2,'0')}]：{behavior_data.name}"
                count += 1
                cant_flag = False
                # 已经检查过的不可用
                if behavior_id in self.done_check_behavior_id_set:
                    cant_flag = True
                    behavior_text += _("(已检查)")
                # 部分指令需要有前置指令才能使用
                if behavior_id in cmd_able_dict and cmd_able_dict[behavior_id] not in self.done_check_behavior_id_set:
                    continue
                # 部分指令需要未破处则不可用
                if behavior_id == "examine_sucking_and_swallowing" and target_character_data.talent[4]:
                    cant_flag = True
                    behavior_text += _("(未初吻)")
                elif (behavior_id == "examine_orifice" or behavior_id == "examine_vagina_firmness") and target_character_data.talent[0]:
                    cant_flag = True
                    behavior_text += _("(未破处)")
                elif behavior_id == "examine_intestine_firmness" and target_character_data.talent[1]:
                    cant_flag = True
                    behavior_text += _("(未破处)")
                elif behavior_id == "examine_urethra_firmness" and target_character_data.talent[2]:
                    cant_flag = True
                    behavior_text += _("(未破处)")
                # 观察处女膜指令需要是处女或者今日破处才能使用
                if behavior_id == "examine_hymen" and not (handle_premise.handle_have_virgin(target_character_id) or handle_premise.handle_first_sex_in_today(target_character_id)):
                    cant_flag = True
                    behavior_text += _("(需要是处女或者今日刚破处)")
                # 部分指令需要有对应部位的器官才能使用
                if behavior_id in body_talent_map:
                    talent_id = body_talent_map[behavior_id]
                    if not target_character_data.talent[talent_id]:
                        continue
                # 如果使用次数已经用完，则不可用
                if now_ability_times <= 0:
                    cant_flag = True
                # 绘制按钮
                if cant_flag:
                    status_draw = draw.NormalDraw()
                    status_draw.text = behavior_text
                    status_draw.style = "deep_gray"
                    status_draw.width = window_width
                    status_draw.draw()
                else:
                    status_draw = draw.LeftButton(
                        _(behavior_text),
                        _(str(count)),
                        window_width,
                        cmd_func=self.settle_target_physical_status,
                        args=(behavior_id),
                    )
                    status_draw.draw()
                    return_list.append(status_draw.return_text)
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def settle_target_physical_status(self, behavior_id: str):
        """结算目标角色的身体状态"""
        behavior_data = game_config.config_behavior[behavior_id]
        self.done_check_behavior_id_set.add(behavior_id)
        line = draw.LineDraw("-", window_width)
        line.draw()
        line_feed.draw()
        # 测试类的需要判断轻度猥亵
        if "测试" in behavior_data.tag:
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, judge = _("初级骚扰"), force_taget_wait = True)
        else:
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, force_taget_wait = True)
        info_draw = draw.WaitDraw()
        info_draw.text = "\n"
        info_draw.draw()
        # 结算成就
        cache.achievement.health_check_count += 1
        achievement_panel.achievement_flow(_("身体检查"))
        # 在干员的破处当天进行处女膜检查
        pl_character_data = cache.character_data[0]
        target_character_id = pl_character_data.target_character_id
        if handle_premise.handle_first_sex_in_today(target_character_id) and behavior_id == "examine_hymen":
            # 结算成就
            achievement_panel.achievement_flow(_("身体检查"), 1046)

    def manage_target_physical(self, target_character_id: int):
        """对目标角色进行身体管理"""
        target_character_data = cache.character_data[target_character_id]

        # 判断是否要重置身体管理数据
        if not len(target_character_data.body_manage):
            target_character_data.body_manage = attr_calculation.get_body_manage_zero()
        elif len(target_character_data.body_manage) != len(game_config.config_body_manage_requirement):
            for cid in game_config.config_body_manage_requirement:
                if cid not in target_character_data.body_manage:
                    target_character_data.body_manage[cid] = 0

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()
            # 绘制提示信息
            info_text = _("\n请选择要对{0}进行的身体管理（管理的条件中达成任意一项即可）：\n\n").format(target_character_data.name)
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()

            count = 0
            for manage_cid in game_config.config_body_manage_requirement:
                body_manage_data = game_config.config_body_manage_requirement[manage_cid]
                body_manage_second_behavior_id = body_manage_data.second_behavior_id
                examine_behavior_id = body_manage_data.need_examine_id
                behavior_name = game_config.config_behavior[body_manage_second_behavior_id].name
                # 去掉status_name里的"被要求"字样
                behavior_name = behavior_name.replace(_("被要求"), "")
                count += 1

                # 跳过未实装的
                if body_manage_data.todo:
                    continue

                # 判断是否满足要求
                judge_result, require_text = self.judge_manage_requirement(manage_cid, target_character_id)
                # 去掉开头的或
                if require_text.startswith(" 或 "):
                    require_text = require_text[3:]

                # 已经在进行中的不需要判定
                if target_character_data.body_manage[manage_cid]:
                    judge_result = True
                else:
                    # 跳过没有进行前置检查的
                    if examine_behavior_id != "0" and examine_behavior_id not in self.done_check_behavior_id_set:
                        continue

                # debug模式下直接通过
                if cache.debug_mode:
                    judge_result = True

                # 绘制按钮
                if judge_result:
                    manage_text = f"[{str(count).rjust(2,'0')}]：{behavior_name}"
                    # 如果已进行该身体管理，则显示进行中
                    if target_character_data.body_manage[manage_cid]:
                        manage_text += _("(进行中)")
                    manage_draw = draw.LeftButton(
                        _(manage_text),
                        _(str(count)),
                        window_width,
                        cmd_func=self.settle_target_physical_manage,
                        args=(manage_cid, target_character_id),
                    )
                    return_list.append(manage_draw.return_text)
                    manage_draw.draw()
                    line_feed.draw()
                else:
                    manage_text = f"[{str(count).rjust(2,'0')}]：{behavior_name.ljust(20, '　')}（ {require_text} ）\n"
                    manage_draw = draw.NormalDraw()
                    manage_draw.text = manage_text
                    manage_draw.style = "deep_gray"
                    manage_draw.width = window_width
                    manage_draw.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def judge_manage_requirement(self, manage_cid: int, target_character_id: int):
        """判断是否满足身体管理的要求"""
        body_manage_data = game_config.config_body_manage_requirement[manage_cid]
        body_manage_second_behavior_id = body_manage_data.second_behavior_id
        target_character_data = cache.character_data[target_character_id]
        judge_result = False
        require_text = ""

        if body_manage_second_behavior_id == 'ask_give_pan_everyday':
            # 内裤收藏数
            now_value_1 = len(self.pl_character_data.pl_collection.npc_panties[target_character_id])
            require_value_1 = body_manage_data.need_value_1
            require_text += _("内裤收藏数量{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_give_socks_everyday':
            # 袜子收藏数
            now_value_1 = len(self.pl_character_data.pl_collection.npc_socks[target_character_id])
            require_value_1 = body_manage_data.need_value_1
            require_text += _("袜子收藏数量{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_not_wear_corset':
            # 露出能力
            now_value_1 = target_character_data.ability[34]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("露出能力等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_not_wear_cloth_in_sleep':
            # 被睡奸经验
            now_value_1 = target_character_data.experience[121]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("被睡姦经验{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_wear_different_socks_everyday':
            # 内裤收藏数
            now_value_1 = len(self.pl_character_data.pl_collection.npc_panties[target_character_id])
            require_value_1 = body_manage_data.need_value_1
            require_text += _("内裤收藏数量{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_equip_nipple_clamp_in_day' or body_manage_second_behavior_id == 'ask_equip_nipple_clamp_in_sleep':
            # Ｂ感觉能力
            now_value_1 = target_character_data.ability[1]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ｂ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_equip_clit_clamp_in_day' or body_manage_second_behavior_id == 'ask_equip_clit_clamp_in_sleep':
            # Ｃ感觉能力
            now_value_1 = target_character_data.ability[2]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ｃ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_equip_v_vibrator_in_day' or body_manage_second_behavior_id == 'ask_equip_v_vibrator_in_sleep':
            # Ｖ感觉能力
            now_value_1 = target_character_data.ability[4]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ｖ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_equip_a_vibrator_in_day' or body_manage_second_behavior_id == 'ask_equip_a_vibrator_in_sleep':
            # Ａ感觉能力
            now_value_1 = target_character_data.ability[5]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ａ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_not_wash_semen':
            # V与W总被射入精液
            now_value_1 = target_character_data.dirty.body_semen[6][3] + target_character_data.dirty.body_semen[7][3]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("V与W总被射入精液{0}ml/{1}ml").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_masturbation_before_sleep' or body_manage_second_behavior_id == 'ask_not_masturbation':
            # 自慰经验
            now_value_1 = target_character_data.experience[54]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("自慰经验{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 'ask_not_lock_door_before_sleeping':
            # 被睡奸经验
            now_value_1 = target_character_data.experience[121]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("被睡姦经验{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        # 攻略进度
        now_value_2 = attr_calculation.get_character_fall_level(target_character_id)
        require_value_2 = body_manage_data.need_value_2
        require_text += _(" 或 攻略进度{0}/{1}").format(now_value_2, require_value_2)
        if now_value_2 >= require_value_2:
            judge_result = True
        # 催眠程度
        now_value_3 = target_character_data.hypnosis.hypnosis_degree
        require_value_3 = body_manage_data.need_value_3
        require_text += _(" 或 催眠程度{0}%/{1}%").format(now_value_3, require_value_3)
        if now_value_3 >= require_value_3:
            judge_result = True

        # 处女检查
        if manage_cid == 36:
            require_text += _(" 需要非处女")
            if target_character_data.talent[0]:
                judge_result = False
        elif manage_cid == 37:
            require_text += _(" 需要非A处女")
            if target_character_data.talent[1]:
                judge_result = False

        # 持有阴茎倒模检查
        if manage_cid in range(31, 40):
            require_text += _(" 需要已送给对方自己的阴茎倒模")
            if not handle_premise.handle_target_have_penis_mold(0):
                judge_result = False

        # 冲突检查
        if manage_cid == 22 and handle_premise.handle_ask_not_masturbation(target_character_id):
            require_text += _(" 需要未选择[禁止自慰]")
            judge_result = False
        if manage_cid == 23 and handle_premise.handle_ask_masturbation_before_sleep(target_character_id):
            require_text += _(" 需要未选择[每天晚上睡前都要自慰]")
            judge_result = False
        if manage_cid in range(31, 40) and handle_premise.handle_ask_ge_3_exercises(target_character_id):
            require_text += _(" 最多只能选择3项练习项目")
            judge_result = False

        return judge_result, require_text

    def settle_target_physical_manage(self, manage_cid: int, target_character_id: int):
        """结算目标角色的身体管理"""
        from Script.Design import basement, second_behavior

        body_manage_data = game_config.config_body_manage_requirement[manage_cid]
        body_manage_second_behavior_id = body_manage_data.second_behavior_id
        target_character_data = cache.character_data[target_character_id]

        info_text = "\n"

        # 如果没有进行该身体管理，则进行
        if target_character_data.body_manage[manage_cid] == 0:
            # 结算二段行为
            second_behavior.character_get_second_behavior(target_character_id, body_manage_second_behavior_id)
            # 结算身体管理
            target_character_data.body_manage[manage_cid] = 1
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1, force_taget_wait = True)
            info_text += _("对{0}进行了{1}的身体管理，将在明天睡醒后生效。\n").format(target_character_data.name, game_config.config_behavior[body_manage_second_behavior_id].name)
            # 练习类的身体管理
            if manage_cid in range(31, 40):
                # 如果当前职业不是性爱工作，则调整为性爱练习生工作
                if not handle_premise.handle_work_is_sex_trainee(target_character_id):
                    # 工作结算
                    target_character_data.work.work_type = 193
                    basement.update_work_people()
                    basement.update_facility_people()
                    info_text += _("因为被要求进行性爱的相关练习，所以{0}的工作被调整为特殊职业-{1}了\n").format(target_character_data.name, game_config.config_work_type[193].name)
        # 如果已经进行该身体管理，则取消
        else:
            # 结算身体管理
            target_character_data.body_manage[manage_cid] = 0
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1, force_taget_wait = True)
            info_text += _("取消了对{0}的{1}的身体管理，将在明天睡醒后生效。\n").format(target_character_data.name, game_config.config_behavior[body_manage_second_behavior_id].name)
            # 练习类的身体管理
            if manage_cid in range(31, 40):
                # 如果已经没有练习，且还是性爱工作，则取消该工作
                if handle_premise.handle_ask_none_exercises(target_character_id) and handle_premise.handle_work_is_sex_trainee(target_character_id):
                    target_character_data.work.work_type = 0
                    basement.update_work_people()
                    basement.update_facility_people()
                    info_text += _("因为没有进行性爱的相关练习，所以{0}的特殊职业-{1}被取消了\n").format(target_character_data.name, game_config.config_work_type[193].name)

        info_draw = draw.WaitDraw()
        info_draw.text = info_text
        info_draw.draw()

    def cancle_physical_manage_panel(self):
        """取消身体管理"""

        info_text = _("请选择要取消身体管理的干员，将取消其全部管理：\n")
        # 使用通用角色选择按钮列表函数
        from Script.UI.Panel import common_select_NPC
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, 1, 0, 0)
        select_state = {}
        while 1:
            final_list = []
            # 遍历角色id
            for npc_id in cache.npc_id_got:
                # 跳过玩家
                if npc_id == 0:
                    continue
                now_character_data = cache.character_data[npc_id]
                for body_manage_cid in game_config.config_body_manage_requirement:
                    # 如果当前干员的身体管理数据不为0，则加入列表
                    if now_character_data.body_manage[body_manage_cid] > 0:
                        now_list = [npc_id, self.cancle_physical_manage, []]
                        final_list.append(now_list)
                        break
            now_draw_panel.text_list = final_list
            # 调用通用选择按钮列表函数
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("取消身体管理"), info_text, select_state)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def cancle_physical_manage(self, target_character_id: int):
        """取消目标角色的身体管理"""
        target_character_data = cache.character_data[target_character_id]
        # 取消所有的身体管理
        target_character_data.body_manage = attr_calculation.get_body_manage_zero()
        info_text = _("\n取消了对{0}的全部身体管理，将在明天睡醒后生效。\n").format(target_character_data.name)
        info_draw = draw.WaitDraw()
        info_draw.text = info_text
        info_draw.draw()

    def adjust_physical_check_schedule(self):
        """调整体检日程"""
        title_text = _("调整体检日程")
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
            for cid in game_config.config_physical_exam_setting:
                # 如果当前不是第2个设置，且第2个设置没有开启，则不显示后面的设置
                if cid >= 3 and cache.rhodes_island.physical_examination_setting[2] == 0:
                    break
                line_feed.draw()
                physical_exam_setting_data = game_config.config_physical_exam_setting[cid]
                # 选项名
                button_text = f"  [{physical_exam_setting_data.name}]： "
                button_len = max(len(button_text) * 2, 60)
                button_draw = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.draw_info, args=(cid))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 如果没有该键，则创建一个，并置为0
                if cid not in cache.rhodes_island.physical_examination_setting:
                    cache.rhodes_island.physical_examination_setting[cid] = 0
                now_setting_flag = cache.rhodes_island.physical_examination_setting[cid] # 当前设置的值
                option_len = len(game_config.config_physical_exam_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                button_text = f" [{game_config.config_physical_exam_setting_option[cid][now_setting_flag]}] "
                button_len = max(len(button_text) * 2, 20)

                # 绘制选项
                button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_setting, args=(cid, option_len))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 部分选项有额外的手动选择按钮
                if cid == 4 and cache.rhodes_island.physical_examination_setting[cid] == 2:
                    now_len = len(cache.rhodes_island.manually_selected_exam_operator_ids)
                    button_text = _("[调整干员名单]({0}人)").format(now_len)
                    button_len = max(len(button_text) * 2, 20)
                    button_draw = draw.CenterButton(button_text, str(cid) + button_text, button_len, cmd_func=self.adjust_target_list)
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                elif cid == 7 and cache.rhodes_island.physical_examination_setting[cid] == 1:
                    now_len = len(cache.rhodes_island.manually_selected_exam_week_day_list)
                    button_text = _("[调整体检日]({0}天)").format(now_len)
                    button_len = max(len(button_text) * 2, 20)
                    button_draw = draw.CenterButton(button_text, str(cid) + button_text, button_len, cmd_func=self.adjust_physical_exam_date)
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


    def check_physcial_report(self):
        """查看检查报告"""

        level_text_dict = {
            0: _("缺陷"),
            1: _("普通"),
            2: _("普通"),
            3: _("标准"),
            4: _("标准"),
            5: _("标准"),
            6: _("优良"),
            7: _("优良"),
            8: _("卓越"),
        }

        base_ability_dict = {
            0: _("【基础敏感强度】"),
            1: _("【扩张耐受】"),
            2: _("【SM耐受】"),
            3: _("【受孕适应性】"),
            4: _("【催眠程度】"),
            5: _("【性器】"),
            6: _("【特殊体质】"),
            11: _("【初吻】"),
            12: _("【处女】"),
            13: _("【肛门处女】"),
        }

        # 指令与能力id的对应表
        cmd_ablility_dict = {
            "examine_sucking_and_swallowing": [71, _("【舌部机动】")],
            "examine_breast": [0, _("【胸部敏感】")],
            "examine_breast_clamping": [73, _("【乳压强度】")],
            "examine_cilitoris": [2, _("【阴蒂敏感】")],
            "examine_hands_flexibility": [70, _("【手部机动】")],
            "examine_foots_flexibility": [72, _("【足部机动】")],
            "examine_vulva_and_shape": [4, _("【阴道敏感】")],
            "examine_orifice": [7, _("【子宫敏感】")],
            "examine_vagina_firmness": [74, _("【阴道技巧】")],
            "examine_anus": [5, _("【肛门敏感】")],
            "examine_intestine_firmness": [75, _("【肛门技巧】")],
            "examine_urination_status": [6, _("【尿道敏感】")],
            "examine_tail_flexibility": [30, _("【尾部机动】")],
            "examine_tentacle_flexibility": [30, _("【触手机动】")],
        }

        # TODO 指令与前置指令的对应表
        # cmd_able_dict = {
        #     # "examine_vagina_and_folds": "阴唇形状",  # 检查内阴
        #     # "examine_hymen": "处女膜",  # 检查处女膜
        #     # "examine_orifice": "子宫口",  # 检查子宫口
        #     "examine_vagina_firmness": "穴压强度",  # 测试阴道
        #     "examine_intestine_firmness": "菊压强度",  # 测试肠道
        #     # "examine_urination_status": "排尿情况",  # 测试排尿
        # }

        target_character_id = self.pl_character_data.target_character_id
        target_character_data = cache.character_data[target_character_id]
        all_part_sex_exp = 0
        for exp_id in {61, 62, 63, 64}:
            all_part_sex_exp += target_character_data.experience[exp_id]

        report_text = "\n"
        report_text += _("基础档案：\n")
        report_text += _(" 【代号】") + target_character_data.name + "\n"
        report_text += _(" 【性别】") + game_config.config_sex_tem[target_character_data.sex].name + "\n"
        report_text += _(" 【性交经验】") + str(all_part_sex_exp) + _("次\n")
        report_text += _(" 【无意识性交经验】") + str(target_character_data.experience[79]) + _("次\n")
        report_text += _(" 【出身地】") + game_config.config_birthplace[target_character_data.relationship.birthplace].name + "\n"
        report_text += _(" 【种族】") + game_config.config_race[target_character_data.race].name + "\n"
        report_text += _(" 【矿石病感染情况】\n")
        if handle_premise.handle_target_is_patient(0):
            report_text += _("  参照医学检测报告，确认为感染者。\n")
        else:
            report_text += _("  参照医学检测报告，确认为非感染者。\n")
        report_text += _("\n综合体检测试：\n")

        # 基础
        N_feel = target_character_data.ability[1]
        report_text += (" {0}{1}\n").format(base_ability_dict[0], level_text_dict[N_feel])
        # 扩张
        ave_resist = 0
        for ability_id in {9, 10, 11, 12}:
            ave_resist += target_character_data.ability[ability_id]
        ave_resist = int(ave_resist // 4)
        report_text += (" {0}{1}\n").format(base_ability_dict[1], level_text_dict[ave_resist])
        # SM
        max_sm = 0
        for ability_id in {35, 36}:
            max_sm = max(max_sm, target_character_data.ability[ability_id])
        report_text += (" {0}{1}\n").format(base_ability_dict[2], level_text_dict[max_sm])
        # 受孕
        report_text += " " + base_ability_dict[3]
        # 当前怀孕进度
        all_pregnancy_talent_id_list = [0, 6, 7, 20, 21, 22, 23, 24, 26, 27, 35]
        now_pregnancy_talent_id_list = [20, 21, 22, 23, 24]
        pregnancy_talent_text = " "
        all_pregnancy_flag, now_pregnancy_flag = False, False
        # 遍历怀孕相关的素质
        for talent_id in all_pregnancy_talent_id_list:
            if target_character_data.talent[talent_id]:
                all_pregnancy_flag = True
                pregnancy_talent_text += game_config.config_talent[talent_id].name + " "
                if talent_id in now_pregnancy_talent_id_list:
                    now_pregnancy_flag = True
        # 如果有怀孕相关的素质
        if all_pregnancy_flag:
            report_text += _("{0}").format(pregnancy_talent_text)
        # 未怀孕情况下显示受精概率
        if not now_pregnancy_flag:
            report_text += _("当前受精概率{0}%").format(target_character_data.pregnancy.fertilization_rate)
        # 已生育
        child_id_list = target_character_data.relationship.child_id_list
        if len(child_id_list) > 0:
            report_text += _(" 已经生育了{0}个孩子，分别是：{1}").format(len(child_id_list), "、".join([cache.character_data[cid].name for cid in child_id_list]))
        report_text += "\n"
        # 催眠
        report_text += " " + base_ability_dict[4]
        hypnosis_talent_id_list = [73, 72, 71]
        hypnosis_talent_text = " "
        now_hypnosis_flag = False
        # 遍历催眠相关的素质，仅选择第一个找到的素质
        for talent_id in hypnosis_talent_id_list:
            if target_character_data.talent[talent_id]:
                now_hypnosis_flag = True
                hypnosis_talent_text += game_config.config_talent[talent_id].name + " "
                break
        # 如果有催眠相关的素质
        if now_hypnosis_flag:
            report_text += _("{0}（{1}%）\n").format(hypnosis_talent_text, target_character_data.hypnosis.hypnosis_degree)
        # 否则显示催眠程度
        else:
            report_text += _("{0}%\n").format(target_character_data.hypnosis.hypnosis_degree)
        # 各指令的遍历
        for cmd_id in cmd_ablility_dict:
            if cmd_id not in self.done_check_behavior_id_set:
                continue
            ability_id = cmd_ablility_dict[cmd_id][0]
            now_name = cmd_ablility_dict[cmd_id][1]
            ability_level = target_character_data.ability[ability_id]
            report_text += (" {0}{1}\n").format(now_name, level_text_dict[ability_level])
        # 性器
        body_part_talent_id_list = list(range(111, 133))
        body_part_talent_text = " "
        for talent_id in body_part_talent_id_list:
            if talent_id in target_character_data.talent and target_character_data.talent[talent_id]:
                body_part_talent_text += game_config.config_talent[talent_id].name + " "
        report_text += (" {0}{1}\n").format(base_ability_dict[5], body_part_talent_text)
        # 特殊体质
        special_talent_id_list = list(range(61, 65)) + list(range(151, 180))
        special_talent_text = " "
        for talent_id in special_talent_id_list:
            if talent_id in target_character_data.talent and target_character_data.talent[talent_id]:
                special_talent_text += game_config.config_talent[talent_id].name + " "
        if special_talent_text == " ":
            special_talent_text = _("无")
        report_text += (" {0}{1}\n").format(base_ability_dict[6], special_talent_text)

        # 性爱履历：
        report_text += _("\n性爱履历：\n")

        # 初吻
        now_text = ""
        if target_character_data.talent[4]:
            now_text += _("保有初吻")
        elif target_character_data.first_record.first_kiss_id != -1:
            kiss_id = target_character_data.first_record.first_kiss_id
            kiss_time = target_character_data.first_record.first_kiss_time
            now_text += _("于{kiss_time}在{kiss_palce}，向{character_name}博士").format(
            character_name=cache.character_data[kiss_id].name,
            kiss_time=str(kiss_time.month) + "月" + str(kiss_time.day) + "日",
            kiss_palce=attr_text.get_scene_path_text(target_character_data.first_record.first_kiss_place),
        )
            if target_character_data.first_record.first_kiss_body_part == 1:
                now_text += _("的阴茎")
            now_text += _("献上了初吻")
        report_text += (" {0}{1}\n").format(base_ability_dict[11], now_text)

        # 处女
        now_text = ""
        if target_character_data.talent[0]:
            now_text += _("保有处女")
        elif target_character_data.first_record.first_sex_id != -1:
            sex_id = target_character_data.first_record.first_sex_id
            sex_time = target_character_data.first_record.first_sex_time
            sex_posture = target_character_data.first_record.first_sex_posture
            now_text += _("于{time}在{palce}，被{character_name}博士以{posture}夺走了处女").format(
                character_name=cache.character_data[sex_id].name,
                time=game_time.get_date_until_day(sex_time),
                palce=attr_text.get_scene_path_text(target_character_data.first_record.first_sex_place),
                posture=sex_posture,
            )
        report_text += (" {0}{1}\n").format(base_ability_dict[12], now_text)

        # A处女
        now_text = ""
        if target_character_data.talent[1]:
            now_text += _("保有后庭处女")
        elif target_character_data.first_record.first_a_sex_id != -1:
            a_sex_id = target_character_data.first_record.first_a_sex_id
            a_sex_time = target_character_data.first_record.first_a_sex_time
            a_sex_posture = target_character_data.first_record.first_a_sex_posture
            now_text += _("于{time}在{palce}，被{character_name}博士以{posture}夺走了A处女").format(
                character_name=cache.character_data[a_sex_id].name,
                time=game_time.get_date_until_day(a_sex_time),
                palce=attr_text.get_scene_path_text(target_character_data.first_record.first_a_sex_place),
                posture=a_sex_posture,
            )
        report_text += (" {0}{1}\n").format(base_ability_dict[13], now_text)

        # 检查人与时间
        report_text += _("\n检查人：Dr.{0}\n").format(self.pl_character_data.name)
        report_text += _("检查日期：{0}\n").format(game_time.get_date_until_day()[3:])
        # 成就记录
        cache.achievement.body_report_chara_count_list.append(target_character_id)

        while 1:

            title_draw = draw.TitleLineDraw("检查报告", self.width)
            title_draw.draw()

            report_draw = draw.NormalDraw()
            report_draw.text = report_text
            report_draw.draw()

            return_list = []
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

        # 结算成就
        achievement_panel.achievement_flow(_("体检报告"))

    def draw_info(self, cid: int):
        """绘制体检设置的详细信息"""
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
        # 调整每天抽取体检人数的选项单独处理
        if cid == 6:
            line_feed.draw()
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            line_feed.draw()
            ask_text = _("请输入1~10的数字\n")
            ask_panel = panel.AskForOneMessage()
            ask_panel.set(ask_text, 99)
            value = ask_panel.draw()
            # 防止玩家输入非数字的内容
            if not value or not value.isdigit():
                return
            new_num = int(value) - 1
            if new_num < 0:
                new_num = 0
            elif new_num > 9:
                new_num = 9
            cache.rhodes_island.physical_examination_setting[cid] = new_num
        else:
            if cache.rhodes_island.physical_examination_setting[cid] < option_len - 1:
                cache.rhodes_island.physical_examination_setting[cid] += 1
            else:
                cache.rhodes_island.physical_examination_setting[cid] = 0

    def adjust_target_list(self):
        """调整体检对象名单"""
        from Script.UI.Panel import common_select_NPC
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, 1, 0, 0)
        select_state = {}
        while 1:
            npc_id_got_list = sorted(cache.npc_id_got)
            # 已选择的角色id列表
            selected_id_list = list(cache.rhodes_island.manually_selected_exam_operator_ids)
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
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("体检对象名单"), select_state = select_state)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def switch_chara_in_target_list(self, character_id: int):
        """切换体检对象名单中的角色"""
        if character_id in cache.rhodes_island.manually_selected_exam_operator_ids:
            cache.rhodes_island.manually_selected_exam_operator_ids.remove(character_id)
        else:
            cache.rhodes_island.manually_selected_exam_operator_ids.add(character_id)

    def adjust_physical_exam_date(self):
        """调整体检日期"""
        week_data = game_config.config_week_day

        while 1:
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()
            line_feed.draw()

            return_list = []

            info_text = _("请选择体检日期：\n")
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()

            # 绘制星期
            for week_id in range(7):
                draw_text = f" [{week_id}]{week_data[week_id].name}"
                draw_style = 'standard'
                # 如果已选择该日期，则显示为选中状态
                if week_id in cache.rhodes_island.manually_selected_exam_week_day_list:
                    draw_text += _("(已选择)")
                    draw_style = 'gold_enrod'
                week_draw = draw.LeftButton(draw_text, str(week_id), window_width, normal_style=draw_style, cmd_func=self.set_physical_exam_date, args=(week_id))

                return_list.append(week_draw.return_text)
                week_draw.draw()
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def set_physical_exam_date(self, week_id: int):
        """设置体检日期"""
        if week_id in cache.rhodes_island.manually_selected_exam_week_day_list:
            cache.rhodes_island.manually_selected_exam_week_day_list.remove(week_id)
        else:
            cache.rhodes_island.manually_selected_exam_week_day_list.append(week_id)
