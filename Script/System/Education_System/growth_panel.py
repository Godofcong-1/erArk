"""养成总览面板（Plan 22 一期 §5.4）

一屏看完一个孩子的状态：当前阶段与已成长天数、18 门科目的等级、出勤与缺课、
四对性格倾向、待处理的成绩单与炫耀 flag。

⚠️ 成长天数必须标明是**日历天**还是**可游玩天**（总纲 §2.3-7）：erArk 的一年只有
   3/6/9/12 四个月，日历天与实际能玩到的天数约为 3:1，不写清楚玩家会按现实直觉误判。
"""
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
    ⚠️ 写入方在三期与四期，本期只读不写，全为0时显示「尚未形成」 """


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

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 孩子页签 + 总览正文
        """
        from Script.System.Education_System import course_select_panel

        student_list = course_select_panel.get_student_candidate_list()
        if not student_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  目前还没有在养成中的孩子\n")
            info_draw.draw()
            return
        now_student = student_list[0]

        while 1:
            return_list: List[str] = []
            for student_id in student_list:
                name = cache.character_data[student_id].name
                tab_width = max(1, int(self.width / max(1, len(student_list))))
                if student_id == now_student:
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

            self._draw_stage(now_student)
            self._draw_subject(now_student)
            self._draw_attendance(now_student)
            self._draw_personality(now_student)
            self._draw_flag(now_student)

            line_feed.draw()
            draw.LineDraw("-", self.width).draw()
            back_draw = draw.CenterButton(_("[返回上级]"), _("返回上级"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            for student_id in student_list:
                if yrn == f"\nGSTU_{student_id}":
                    now_student = student_id
                    break

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
        功能: 正数偏前者、负数偏后者；⚠️ 写入方在三期与四期，本期恒为0
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
        if not text_list:
            return
        draw.LittleTitleLineDraw(_("待处理"), self.width).draw()
        for text in text_list:
            now_draw = draw.NormalDraw()
            now_draw.width = self.width
            now_draw.text = "  ○{0}\n".format(text)
            now_draw.draw()
