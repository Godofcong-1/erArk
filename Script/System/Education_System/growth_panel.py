"""养成总览面板（Plan 22 一期 §5.4）

一屏看完一个孩子的状态：当前阶段与已成长天数、18 门科目的等级、出勤与缺课、
四对性格倾向、养成事件履历（三期 §5.2）、待处理的成绩单与炫耀 flag。

⚠️ 成长天数必须标明是**日历天**还是**可游玩天**（总纲 §2.3-7）：erArk 的一年只有
   3/6/9/12 四个月，日历天与实际能玩到的天数约为 3:1，不写清楚玩家会按现实直觉误判。
"""
import datetime
from types import FunctionType
from typing import List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation
from Script.System.Education_System.class_schedule_panel import SUBJECT_ABILITY_LIST
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

STAGE_TALENT_NAME = {101: "婴儿", 102: "幼女", 103: "萝莉", 104: "少女"}
""" 成长链的四个年龄素质（growth_handle.CHILD_TALENT_SET）对应的阶段名 """

PERSONALITY_PAIR_NAME = {
    0: ("勤劳", "懒散"),
    1: ("坚强", "脆弱"),
    2: ("热情", "孤僻"),
    3: ("开放", "羞耻"),
}
""" 四对性格倾向：值为正偏前者、为负偏后者（game_type.CHILD_GROWTH.personality_point）。
    ⚠️ 三期的养成事件是它的主要写入方，全为0时显示「尚未形成」 """

HISTORY_SHOW_MAX = 8
""" 养成履历最多列出的条数。养到成年会攒下几十条，全列出来会把总览面板顶爆 """

HISTORY_TEXT_MAX = 24
""" 履历里事件正文的截断长度，只留能认出是哪件事的开头 """


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

    def draw_page(self, return_list: List[str]):
        """
        绘制本页内容
        输入类型: return_list(List[str])，容器的共享返回值列表，本页的按钮往里加
        输出类型: 无
        功能: 孩子页签 + 总览正文。
              ⚠️ 只画不取输入，askfor_all 由容器 Education_Manage_Panel 统一调用
        """
        from Script.System.Education_System import course_select_panel

        # 每轮重算：孩子会在游戏过程中出生与长大，不能在 __init__ 里快照
        self.student_list = course_select_panel.get_student_candidate_list()
        if not self.student_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  目前还没有在养成中的孩子\n")
            info_draw.draw()
            return
        # 选中态失效（首次进入，或原来那个孩子已不在列表里）时回落到第一个
        if self.now_student not in self.student_list:
            self.now_student = self.student_list[0]

        for student_id in self.student_list:
            name = cache.character_data[student_id].name
            tab_width = max(1, int(self.width / max(1, len(self.student_list))))
            if student_id == self.now_student:
                now_draw = draw.CenterDraw()
                now_draw.text = f"[{name}]"
                now_draw.style = "onbutton"
                now_draw.width = tab_width
                now_draw.draw()
            else:
                now_draw = draw.CenterButton(f"[{name}]", f"\nGSTU_{student_id}", tab_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

        self._draw_stage(self.now_student)
        self._draw_subject(self.now_student)
        self._draw_attendance(self.now_student)
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
        功能: 切换孩子。本页是只读总览，没有别的可点项
        """
        if not self.student_list:
            return
        for student_id in self.student_list:
            if yrn == f"\nGSTU_{student_id}":
                self.now_student = student_id
                return

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
        for talent_id in sorted(STAGE_TALENT_NAME.keys()):
            if character_data.talent.get(talent_id, 0):
                stage_name = _(STAGE_TALENT_NAME[talent_id])
                break
        # 成长天数由妊娠系统统一计算（含成长加速药），这里只取用不重算
        grow_day = pregnancy_handle.get_child_grow_day(character_id)
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        # ⚠️ 必须写明是「可游玩天」：一年只有3/6/9/12四个月，与现实日历天约为1:3
        info_draw.text = _("\n  当前阶段：{0}｜本阶段已成长 {1} 个可游玩天（非日历天）\n").format(
            stage_name, grow_day)
        info_draw.draw()

    def _draw_subject(self, character_id: int):
        """
        绘制18门科目的等级
        输入类型: character_id(int)
        输出类型: 无
        功能: 每行4门，0级的也灰显列出，好让玩家知道还有哪些没学
        """
        character_data: game_type.Character = cache.character_data[character_id]
        draw.LittleTitleLineDraw(_("科目水平"), self.width).draw()
        for index, ability_id in enumerate(SUBJECT_ABILITY_LIST):
            level = int(character_data.ability.get(ability_id, 0))
            now_draw = draw.LeftDraw()
            now_draw.width = int(self.width / 4)
            now_draw.text = _(" {0}：{1}").format(
                game_config.config_ability[ability_id].name, attr_calculation.judge_grade(level))
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
        info_draw.text = _("  听课 {0} 节，缺课 {1} 节（出勤率 {2}%）\n").format(
            growth_data.attend_class_count, growth_data.absent_count, int(rate * 100))
        info_draw.draw()

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
        for pair_id in sorted(PERSONALITY_PAIR_NAME.keys()):
            point = growth_data.personality_point.get(pair_id, 0.0)
            front, back = PERSONALITY_PAIR_NAME[pair_id]
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
        if len(history_list) > HISTORY_SHOW_MAX:
            omit_draw = draw.NormalDraw()
            omit_draw.width = self.width
            omit_draw.text = _("  （更早的 {0} 条已略去）\n").format(len(history_list) - HISTORY_SHOW_MAX)
            omit_draw.style = "deep_gray"
            omit_draw.draw()
            history_list = history_list[-HISTORY_SHOW_MAX:]
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
                time_text, event_data.get("text", "").split("\n")[0][:HISTORY_TEXT_MAX], choice_text)
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
        from Script.System.Official_Event_System import official_event_handle

        wait_count = official_event_handle.get_official_event_queue_count(character_id)
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
