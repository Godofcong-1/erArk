"""养成总览面板（Plan 22 一期 §5.4）

一屏看完一个孩子的状态：当前阶段与已成长天数、18 门科目的等级、出勤与缺课、
四对性格倾向、养成事件履历（三期 §5.2）、待处理的成绩单与炫耀 flag。
顶部的孩子页签每页 8 人、超出翻页（一期 §9.8.1）；口径仍是养成中的女儿，
与个人课表放宽后的「职业为学生的全部干员」不同（§9.8.2）。

⚠️ 成长天数必须标明是**日历天**还是**可游玩天**（总纲 §2.3-7）：erArk 的一年只有
   3/6/9/12 四个月，日历天与实际能玩到的天数约为 3:1，不写清楚玩家会按现实直觉误判。
"""
import datetime
from types import FunctionType
from typing import List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation
from Script.System.Education_System import education_constant, semester_handle, growth_handle, student_tab_bar
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


class Growth_Panel:
    """
    养成总览面板（方案 §5.4）
    输入类型: width(int)
    输出类型: 无
    功能: 按孩子展示成长状态
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        self.now_student: int = -1
        """ 当前展示的孩子角色id，-1表示尚未选择，由 draw_page 回落到第一个 """
        self.student_list: List[int] = []
        """ 本轮在养成中的孩子列表，每轮在 draw_page 里重算 """
        self.report_card_index: int = -1
        """ 成绩单历史当前翻到第几份（0起），-1表示尚未翻过、由 _draw_report_card 回落到最新那份。
            ⚠️ 必须是面板的状态而不是局部变量：容器每轮 while 都重画，局部变量会被冲掉 """
        self.tab_bar = student_tab_bar.Student_Tab_Bar(width, "\nGSTU_")
        """ 顶部的孩子页签栏，每页8人。页码同样存在它身上 """

    def draw_page(self, return_list: List[str]):
        """
        绘制本页内容
        输入类型: return_list(List[str])，容器的共享返回值列表，本页的按钮往里加
        输出类型: 无
        功能: 孩子页签（每页8人，可翻页）+ 总览正文。
              ⚠️ 只画不取输入，askfor_all 由容器 Education_Manage_Panel 统一调用
        """
        # 每轮重算：孩子会在游戏过程中出生与长大，不能在 __init__ 里快照。
        # ⚠️ 直接走数据层的女儿名单，不再绕经 course_select_panel——那边的口径已放宽为「职业为学生」，
        #    养成总览要看的仍然只是女儿（方案 §9.8.2）
        self.student_list = growth_handle.get_student_candidate_list()
        if not self.student_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  目前还没有在养成中的孩子\n")
            info_draw.draw()
            return
        # 选中态失效（首次进入，或原来那个孩子已不在列表里）时回落到第一个，并把页签栏翻到她所在的那页
        if self.now_student not in self.student_list:
            self.now_student = self.student_list[0]
            self.tab_bar.jump_to(self.student_list, self.now_student)

        self.tab_bar.draw(self.student_list, self.now_student, return_list)

        self._draw_stage(self.now_student)
        self._draw_subject(self.now_student)
        self._draw_attendance(self.now_student)
        self._draw_report_card(self.now_student, return_list)
        self._draw_personality(self.now_student)
        self._draw_event_history(self.now_student)
        self._draw_flag(self.now_student)

        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

    def handle_yrn(self, yrn: str):
        """
        处理本页按钮的选择结果
        输入类型: yrn(str)，容器 askfor_all 的返回值
        输出类型: 无
        功能: 翻页签、切换孩子、翻成绩单。除此之外本页是只读总览
        """
        # 成绩单翻页与页签翻页都与孩子无关，先判掉，省得白扫一遍名单
        if yrn == education_constant.REPORT_CARD_PREV:
            self.report_card_index -= 1
            return
        if yrn == education_constant.REPORT_CARD_NEXT:
            self.report_card_index += 1
            return
        if self.tab_bar.handle_page_yrn(yrn):
            return
        if not self.student_list:
            return
        student_id = self.tab_bar.get_student_by_yrn(yrn, self.student_list)
        if student_id != -1:
            # ⚠️ 换孩子必须把成绩单下标清掉：上一个孩子翻到第3份、换过来的孩子只有1份时，
            #    留着旧下标会莫名其妙地跳页（虽然会被夹回去，但表现很怪）
            self.now_student = student_id
            self.report_card_index = -1

    def _draw_stage(self, character_id: int):
        """
        绘制当前成长阶段
        输入类型: character_id(int)
        输出类型: 无
        功能: 显示阶段名与已成长天数
        """
        from Script.System.Pregnancy_System import pregnancy_handle

        character_data: game_type.Character = cache.character_data[character_id]
        stage_name = _("已成年")
        for talent_id in sorted(education_constant.STAGE_TALENT_NAME.keys()):
            if character_data.talent.get(talent_id, 0):
                stage_name = _(education_constant.STAGE_TALENT_NAME[talent_id])
                break
        # 成长天数由妊娠系统统一计算（含成长加速药），这里只取用不重算
        grow_day = pregnancy_handle.get_child_grow_day(character_id)
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        # ⚠️ 必须写明是「可游玩天」：一年只有3/6/9/12四个月，与现实日历天约为1:3
        info_draw.text = _("\n  当前阶段：{0}｜本阶段已成长 {1} 个可游玩天（非日历天）\n").format(
            stage_name, grow_day)
        info_draw.draw()
        # 胎教带来的初始经验是这孩子上学前就有的「底子」，只有出生时提示过一次，
        # 之后玩家再也看不到，放在阶段行下面正好（四期方案 §3.19）
        from Script.System.Education_System import baby_growth_handle

        prenatal_exp_dict = baby_growth_handle.get_prenatal_exp_dict(character_id)
        if prenatal_exp_dict:
            prenatal_draw = draw.NormalDraw()
            prenatal_draw.width = self.width
            prenatal_draw.text = _("  胎教底子：出生时{0}门科目各获得了 {1} 点初始经验\n").format(
                len(prenatal_exp_dict), list(prenatal_exp_dict.values())[0])
            prenatal_draw.style = "deep_gray"
            prenatal_draw.draw()

    def _draw_subject(self, character_id: int):
        """
        绘制18门科目的等级与本学期增量（方案 §5.4）
        输入类型: character_id(int)
        输出类型: 无
        功能: 每行4门，0级的也灰显列出，好让玩家知道还有哪些没学；
              本学期涨过级的标出涨了几级并高亮——光看等级看不出这学期的课有没有白上
        """
        character_data: game_type.Character = cache.character_data[character_id]
        draw.LittleTitleLineDraw(_("科目水平"), self.width).draw()
        # 本学期的增量走 semester_handle 的唯一算口（现等级 - 学期基线），不在这里另算一遍
        level_change = semester_handle.get_semester_level_change(character_id)
        for index, ability_id in enumerate(education_constant.SUBJECT_ABILITY_LIST):
            level = int(character_data.ability.get(ability_id, 0))
            now_draw = draw.LeftDraw()
            now_draw.width = int(self.width / 4)
            grade_text = attr_calculation.judge_grade(level)
            if ability_id in level_change:
                old_level, new_level = level_change[ability_id]
                now_draw.text = _(" {0}：{1}（本学期+{2}）").format(
                    game_config.config_ability[ability_id].name, grade_text, new_level - old_level)
                now_draw.style = "gold_enrod"
            else:
                now_draw.text = _(" {0}：{1}").format(
                    game_config.config_ability[ability_id].name, grade_text)
                if level == 0:
                    now_draw.style = "deep_gray"
            now_draw.draw()
            if index % 4 == 3:
                line_feed.draw()
        line_feed.draw()

    def _draw_attendance(self, character_id: int):
        """
        绘制出勤情况
        输入类型: character_id(int)
        输出类型: 无
        功能: 听课节数、缺课节数与出勤率
        """
        growth_data = cache.character_data[character_id].child_growth
        if growth_data is None:
            return
        draw.LittleTitleLineDraw(_("出勤"), self.width).draw()
        total = growth_data.attend_class_count + growth_data.absent_count
        rate = growth_data.attend_class_count / total if total else 1.0
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  累计：听课 {0} 节，缺课 {1} 节（出勤率 {2}%）\n").format(
            growth_data.attend_class_count, growth_data.absent_count, int(rate * 100))
        info_draw.draw()
        # 本学期的数走 semester_handle 的唯一算口（累计减学期基线），不在这里另算一遍
        semester_attend, semester_absent = semester_handle.get_semester_attend(character_id)
        now_draw = draw.NormalDraw()
        now_draw.width = self.width
        now_draw.text = _("  本学期：听课 {0} 节，缺课 {1} 节（出勤率 {2}%）\n").format(
            semester_attend, semester_absent,
            semester_handle.get_semester_attend_rate(semester_attend, semester_absent))
        now_draw.draw()

    def _draw_report_card(self, character_id: int, return_list: List[str]):
        """
        绘制历年成绩单，一次一份，可前后翻页
        输入类型: character_id(int), return_list(List[str]) 容器的共享返回值列表
        输出类型: 无
        功能: 列出学期切换时冻结的那些快照。还没经历过学期切换就整节不画。
              ⚠️ 翻页下标存在面板上而不是每次重算：容器每轮 while 都会重画本函数，
                 算出来的下标会被冲掉，玩家点一次「上一学期」马上又跳回最新那份
        """
        history_list = semester_handle.get_report_card_history(character_id)
        if not history_list:
            return
        # 下标越界（换了个孩子、或旧的那几份被上限挤掉了）时回落到最新那份
        if not 0 <= self.report_card_index < len(history_list):
            self.report_card_index = len(history_list) - 1
        report_data = history_list[self.report_card_index]
        draw.LittleTitleLineDraw(_("学期成绩单"), self.width).draw()
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  {0}　评定：{1}　出勤 {2} 节／缺课 {3} 节（出勤率 {4}%）\n").format(
            semester_handle.get_semester_name(report_data.get("year", 0), report_data.get("month", 0)),
            _(education_constant.REPORT_GRADE_NAME.get(
                report_data.get("grade", education_constant.REPORT_GRADE_NO_CLASS), "无课可评")),
            report_data.get("attend", 0), report_data.get("absent", 0), report_data.get("rate", 100))
        info_draw.draw()
        level_text = semester_handle.get_level_change_text(report_data.get("level_change", {}))
        now_draw = draw.NormalDraw()
        now_draw.width = self.width
        if level_text:
            now_draw.text = _("  那个学期的进步：{0}\n").format(level_text)
        else:
            now_draw.text = _("  那个学期没有科目升级\n")
            now_draw.style = "deep_gray"
        now_draw.draw()

        # 只有一份时不画翻页按钮：两个点不动的箭头比没有箭头更让人困惑
        if len(history_list) <= 1:
            return
        button_width = int(self.width / 3)
        if self.report_card_index > 0:
            prev_draw = draw.CenterButton(_("[← 上一学期]"), education_constant.REPORT_CARD_PREV, button_width)
            prev_draw.draw()
            return_list.append(prev_draw.return_text)
        else:
            # 到头了也要占住格位，否则中间那行「第N/M份」会整体左移
            blank_draw = draw.CenterDraw()
            blank_draw.width = button_width
            blank_draw.style = "deep_gray"
            blank_draw.text = _("　← 上一学期")
            blank_draw.draw()
        index_draw = draw.CenterDraw()
        index_draw.width = button_width
        index_draw.text = _("第 {0} / {1} 份（含最近一份）").format(
            self.report_card_index + 1, len(history_list))
        index_draw.draw()
        if self.report_card_index < len(history_list) - 1:
            next_draw = draw.CenterButton(_("[下一学期 →]"), education_constant.REPORT_CARD_NEXT, button_width)
            next_draw.draw()
            return_list.append(next_draw.return_text)
        else:
            blank_draw = draw.CenterDraw()
            blank_draw.width = button_width
            blank_draw.style = "deep_gray"
            blank_draw.text = _("　下一学期 →")
            blank_draw.draw()
        line_feed.draw()

    def _draw_personality(self, character_id: int):
        """
        绘制四对性格倾向
        输入类型: character_id(int)
        输出类型: 无
        功能: 正数偏前者、负数偏后者；主要写入方是三期的养成事件与四期的照料行为
        """
        growth_data = cache.character_data[character_id].child_growth
        if growth_data is None:
            return
        draw.LittleTitleLineDraw(_("性格倾向"), self.width).draw()
        for pair_id in sorted(education_constant.PERSONALITY_PAIR_NAME.keys()):
            point = growth_data.personality_point.get(pair_id, 0.0)
            front, back = education_constant.PERSONALITY_PAIR_NAME[pair_id]
            now_draw = draw.LeftDraw()
            now_draw.width = int(self.width / 4)
            if point > 0:
                now_draw.text = _(" 偏{0}（{1:.0f}）").format(_(front), point)
            elif point < 0:
                now_draw.text = _(" 偏{0}（{1:.0f}）").format(_(back), -point)
            else:
                now_draw.text = _(" {0}/{1}：尚未形成").format(_(front), _(back))
                now_draw.style = "deep_gray"
            now_draw.draw()
        line_feed.draw()

    def _draw_event_history(self, character_id: int):
        """
        绘制养成事件履历（Plan 22 三期 §5.2）
        输入类型: character_id(int)
        输出类型: 无
        功能: 列出已触发过的养成事件与当时的选择，读 child_growth.event_history
        """
        from Script.Config import game_config as _game_config

        growth_data = cache.character_data[character_id].child_growth
        if growth_data is None or not growth_data.event_history:
            return
        draw.LittleTitleLineDraw(_("养成履历"), self.width).draw()
        # 按发生时间正序，最近的排在最后，读起来是一条成长线而不是一堆条目
        # ⚠️ 缺 time 的旧记录要给一个 datetime 兜底，混着int排序会直接 TypeError
        history_list = sorted(
            growth_data.event_history.items(),
            key=lambda one: one[1].get("time") or datetime.datetime(1, 1, 1))
        # 只列最近的HISTORY_SHOW_MAX条：养到成年会攒下几十条，全列出来会把总览面板顶爆
        if len(history_list) > education_constant.HISTORY_SHOW_MAX:
            omit_draw = draw.NormalDraw()
            omit_draw.width = self.width
            omit_draw.text = _("  （更早的 {0} 条已略去）\n").format(len(history_list) - education_constant.HISTORY_SHOW_MAX)
            omit_draw.style = "deep_gray"
            omit_draw.draw()
            history_list = history_list[-education_constant.HISTORY_SHOW_MAX:]
        for uid, record in history_list:
            event_data = _game_config.config_official_event.get(uid)
            # 配置里已删掉的事件只留一条占位，不让履历出现空行
            if event_data is None:
                continue
            choice_index = record.get("choice", 0)
            choice_text = event_data.get(f"option_{choice_index}", _("（未作选择）"))
            now_draw = draw.NormalDraw()
            now_draw.width = self.width
            time_data = record.get("time")
            time_text = time_data.strftime("%Y/%m/%d") if hasattr(time_data, "strftime") else ""
            now_draw.text = _("  {0} {1} → {2}\n").format(
                time_text, event_data.get("text", "").split("\n")[0][:education_constant.HISTORY_TEXT_MAX], choice_text)
            now_draw.draw()
        line_feed.draw()

    def _draw_flag(self, character_id: int):
        """
        绘制待处理的几个 flag
        输入类型: character_id(int)
        输出类型: 无
        功能: 成绩单待查看、有待炫耀的能力、今日翘课中
        """
        growth_data = cache.character_data[character_id].child_growth
        if growth_data is None:
            return
        text_list = []
        if growth_data.report_card_flag:
            text_list.append(_("本学期成绩单待查看（用「检查成绩单」指令）"))
        if growth_data.show_off_ability:
            name_list = [game_config.config_ability[ability_id].name
                         for ability_id in growth_data.show_off_ability
                         if ability_id in game_config.config_ability]
            text_list.append(_("有想炫耀的进步：{0}（下次见到你时会说）").format("、".join(name_list)))
        if growth_data.skip_class_flag:
            text_list.append(_("今天正在翘课"))
        # 队列是全岛共用的，这里只数这个孩子的那几条（Plan 23）
        # ⚠️ 不提示的话玩家不知道要去博士办公室处理公务，事件会一直躺在队列里
        # ⚠️ 走教育侧的封装而不是直接调公务事件系统：养成事件的口径由 growth_event_handle 负责，
        #    面板越过它直接问底层，日后那边改了口径这里不会跟着变
        from Script.System.Education_System import growth_event_handle

        wait_count = growth_event_handle.get_growth_event_queue_count(character_id)
        if wait_count:
            text_list.append(_("有 {0} 件关于她的事等你在博士办公室「处理公务」时决断").format(wait_count))
        if not text_list:
            return
        draw.LittleTitleLineDraw(_("待处理"), self.width).draw()
        for text in text_list:
            now_draw = draw.NormalDraw()
            now_draw.width = self.width
            now_draw.text = "  ○{0}\n".format(text)
            now_draw.draw()
