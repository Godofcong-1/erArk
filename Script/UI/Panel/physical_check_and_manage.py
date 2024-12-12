from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.Design import handle_premise, handle_instruct, attr_calculation, game_time, attr_text
from Script.UI.Moudle import draw
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
        self.done_check_status_id_set = set()
        """ 已经检查过的状态id集合 """

    def draw(self):
        """绘制对象"""

        title_text = _("身体检查与管理")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            self.pl_character_data = cache.character_data[0] # 更新玩家的角色数据
            return_list = []
            title_draw.draw()
            cinfo_draw = draw.NormalDraw()
            info_text = _("\n要做什么呢？\n")
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            if handle_premise.handle_have_target(0):
                target_character_id = self.pl_character_data.target_character_id
                target_character_data = cache.character_data[target_character_id]
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
                button1_text = _("[001]检查身体情况（当前没有查看对象）\n")
                button1_draw = draw.NormalDraw()
                button1_draw.text = button1_text
                button1_draw.style = "deep_gray"
                button1_draw.width = self.width
                button1_draw.draw()

            if len(self.done_check_status_id_set) > 0:
                target_character_id = self.pl_character_data.target_character_id
                target_character_data = cache.character_data[target_character_id]
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

            if cache.debug_mode:
                button3_text = _("[003]调整体检日程(未实装)")
                button3_draw = draw.LeftButton(
                    _(button3_text),
                    _("3"),
                    window_width,
                    cmd_func=self.adjust_physical_check_schedule,
                    args=(),
                    )
                line_feed.draw()
                button3_draw.draw()
                return_list.append(button3_draw.return_text)

            if len(self.done_check_status_id_set) > 0:
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
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def check_target_physical(self, target_character_id: int):
        """查看目标角色的身体情况"""
        target_character_data = cache.character_data[target_character_id]

        # 指令与前置指令的对应表
        cmd_able_dict = {
            851: 850,  # 测试头发
            853: 852,  # 测试口腔
            855: 854,  # 测试腋下
            857: 856,  # 检查乳头
            858: 856,  # 测试胸部
            861: 860,  # 测试手部
            863: 862,  # 测试足部
            872: 871,  # 检查内阴
            873: 872,  # 检查处女膜
            874: 872,  # 检查子宫口
            875: 872,  # 测试阴道
            877: 876,  # 测试肠道
            879: 878,  # 测试排尿
            882: 881,  # 测试尾巴
            888: 887,  # 测试触手
        }

        # 部位与素质的对应表
        body_talent_map = {
            881: 113,  # 尾巴
            882: 113,  # 尾巴
            883: 112,  # 兽角
            884: 111,  # 兽耳
            885: 115,  # 翅膀
            886: 114,  # 光环
            887: 116   # 触手
        }

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()
            py_cmd.clr_cmd()
            # 绘制提示信息
            info_text = _("\n请选择要对{0}进行的身体检查：\n\n").format(target_character_data.name)
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()
            # 检索所有的身体检查状态
            count = 0
            for status_id in range(850, 899):
                if status_id in game_config.config_status:
                    count += 1
                    # 已经检查过的不再显示
                    if status_id in self.done_check_status_id_set:
                        continue
                    # 部分指令需要有前置指令才能使用
                    if status_id in cmd_able_dict and cmd_able_dict[status_id] not in self.done_check_status_id_set:
                        continue
                    # 部分指令需要破处后才能使用
                    if (status_id == 874 or status_id == 875) and target_character_data.talent[0]:
                        continue
                    elif status_id == 877 and target_character_data.talent[1]:
                        continue
                    # 部分指令需要有对应部位的器官才能使用
                    if status_id in body_talent_map:
                        talent_id = body_talent_map[status_id]
                        if not target_character_data.talent[talent_id]:
                            continue
                    # 绘制按钮
                    status_data = game_config.config_status[status_id]
                    status_text = f"[{str(count).rjust(2,'0')}]：{status_data.name}"
                    status_draw = draw.LeftButton(
                        _(status_text),
                        _(str(count)),
                        window_width,
                        cmd_func=self.settle_target_physical_status,
                        args=(status_id),
                    )
                    line_feed.draw()
                    status_draw.draw()
                    return_list.append(status_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def settle_target_physical_status(self, status_id: int):
        """结算目标角色的身体状态"""
        self.done_check_status_id_set.add(status_id)
        line = draw.LineDraw("-", window_width)
        line.draw()
        line_feed.draw()
        handle_instruct.chara_handle_instruct_common_settle(status_id, force_taget_wait = True)
        info_draw = draw.WaitDraw()
        info_draw.text = "\n"
        info_draw.draw()

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
                examine_status_id = body_manage_data.need_examine_id
                status_name = game_config.config_status[body_manage_second_behavior_id].name
                # 去掉status_name里的"被要求"字样
                status_name = status_name.replace(_("被要求"), "")
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
                    if examine_status_id > 0 and examine_status_id not in self.done_check_status_id_set:
                        continue

                # debug模式下直接通过
                if cache.debug_mode:
                    judge_result = True

                # 绘制按钮
                if judge_result:
                    manage_text = f"[{str(count).rjust(2,'0')}]：{status_name}"
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
                    manage_text = f"[{str(count).rjust(2,'0')}]：{status_name.ljust(20, '　')}（ {require_text} ）\n"
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

        if body_manage_second_behavior_id == 1451:
            # 内裤收藏数
            now_value_1 = len(self.pl_character_data.pl_collection.npc_panties[target_character_id])
            require_value_1 = body_manage_data.need_value_1
            require_text += _("内裤收藏数量{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1452:
            # 袜子收藏数
            now_value_1 = len(self.pl_character_data.pl_collection.npc_socks[target_character_id])
            require_value_1 = body_manage_data.need_value_1
            require_text += _("袜子收藏数量{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1453:
            # 露出能力
            now_value_1 = target_character_data.ability[34]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("露出能力等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1454:
            # 被睡奸经验
            now_value_1 = target_character_data.experience[121]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("被睡姦经验{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1461 or body_manage_second_behavior_id == 1465:
            # Ｂ感觉能力
            now_value_1 = target_character_data.ability[1]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ｂ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1462 or body_manage_second_behavior_id == 1466:
            # Ｃ感觉能力
            now_value_1 = target_character_data.ability[2]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ｃ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1463 or body_manage_second_behavior_id == 1467:
            # Ｖ感觉能力
            now_value_1 = target_character_data.ability[4]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ｖ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1464 or body_manage_second_behavior_id == 1468:
            # Ａ感觉能力
            now_value_1 = target_character_data.ability[5]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("Ａ感觉等级{0}/{1}").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1471:
            # V与W总被射入精液
            now_value_1 = target_character_data.dirty.body_semen[6][3] + target_character_data.dirty.body_semen[7][3]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("V与W总被射入精液{0}ml/{1}ml").format(now_value_1, require_value_1)
            if now_value_1 >= require_value_1:
                judge_result = True
        elif body_manage_second_behavior_id == 1472 or body_manage_second_behavior_id == 1473:
            # 自慰经验
            now_value_1 = target_character_data.experience[54]
            require_value_1 = body_manage_data.need_value_1
            require_text += _("自慰经验{0}/{1}").format(now_value_1, require_value_1)
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
        from Script.Design import basement

        body_manage_data = game_config.config_body_manage_requirement[manage_cid]
        body_manage_second_behavior_id = body_manage_data.second_behavior_id
        target_character_data = cache.character_data[target_character_id]

        info_text = "\n"

        # 如果没有进行该身体管理，则进行
        if target_character_data.body_manage[manage_cid] == 0:
            # 结算二段行为
            target_character_data.second_behavior[body_manage_second_behavior_id] = 1
            # 结算身体管理
            target_character_data.body_manage[manage_cid] = 1
            handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_WAIT, duration = 1, force_taget_wait = True)
            info_text += _("对{0}进行了{1}的身体管理，将在明天睡醒后生效。\n").format(target_character_data.name, game_config.config_status[body_manage_second_behavior_id].name)
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
            handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_WAIT, duration = 1, force_taget_wait = True)
            info_text += _("取消了对{0}的{1}的身体管理，将在明天睡醒后生效。\n").format(target_character_data.name, game_config.config_status[body_manage_second_behavior_id].name)
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

    def adjust_physical_check_schedule(self):
        """调整体检日程"""
        # TODO
        pass

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
            853: [71, _("【舌部机动】")],
            856: [0, _("【胸部敏感】")],
            858: [73, _("【乳压强度】")],
            859: [2, _("【阴蒂敏感】")],
            861: [70, _("【手部机动】")],
            863: [72, _("【足部机动】")],
            871: [4, _("【阴道敏感】")],
            874: [7, _("【子宫敏感】")],
            875: [74, _("【阴道技巧】")],
            876: [5, _("【肛门敏感】")],
            877: [75, _("【肛门技巧】")],
            879: [6, _("【尿道敏感】")],
            882: [30, _("【尾部机动】")],
            888: [30, _("【触手机动】")],
        }

        # TODO 指令与前置指令的对应表
        # cmd_able_dict = {
        #     # 872: "阴唇形状",  # 检查内阴
        #     # 873: "处女膜",  # 检查处女膜
        #     # 874: "子宫口",  # 检查子宫口
        #     875: "穴压强度",  # 测试阴道
        #     877: "菊压强度",  # 测试肠道
        #     # 879: "排尿情况",  # 测试排尿
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
            if cmd_id not in self.done_check_status_id_set:
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

