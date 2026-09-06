"""全局课表面板（Plan 22 一期 §5.2）与教育管理系统的页签容器

⚠️ 课表是「10 教室 × 7 天 × 9 节」的三维数据，一次全画必然超出终端宽度。
   本面板一次只展示**一间教室**的周表（7 天 × 9 节），教室用上方的横向标签页切换——
   降一个维度之后 Tk 与 Web 都画得下（方案 §5.2）。

⚠️ 只用 Script/UI/Moudle/draw.py 的抽象绘制类，不直接碰 Tk 或 HTML；
   Web_Draw_System/web_draw_adapter.py 在启动时包装这些抽象类，双模式才能同时成立。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Config import game_config, normal_config
from Script.Design import game_time
from Script.System.Education_System import schedule_handle
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

WEEK_NAME = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
""" 星期的显示名，下标即 datetime 的 weekday() """

SUBJECT_ABILITY_LIST = list(range(40, 50)) + list(range(70, 78))
""" 可排课的18门科目：40~49 通用技能、70~77 性技（方案 §3.4） """


def get_period_time_text(period: int) -> str:
    """
    取某一节次的起止时间文本
    Keyword arguments:
    period -- 节次，0~8
    Return arguments:
    str -- 如 "09:00~09:45"
    """
    hour, minute = game_time.CLASS_PERIOD_START[period]
    end_minute = minute + game_time.CLASS_PERIOD_MINUTE
    end_hour = hour + end_minute // 60
    end_minute = end_minute % 60
    return "{0:02d}:{1:02d}~{2:02d}:{3:02d}".format(hour, minute, end_hour, end_minute)


class Education_Manage_Panel:
    """
    教育管理系统主面板（教师办公室入口，方案 §5.1）
    输入类型: width(int)
    输出类型: 无
    功能: 三个子页的页签容器——全局课表 / 个人课表 / 养成总览
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        self.now_panel: str = _("全局课表")

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 绘制页签并分发到对应子页面
        """
        from Script.System.Education_System import course_select_panel, growth_panel

        title_draw = draw.TitleLineDraw(_("教育管理系统"), self.width)
        panel_list = [_("全局课表"), _("个人课表"), _("养成总览")]

        while 1:
            return_list: List[str] = []
            title_draw.draw()
            for now_panel in panel_list:
                panel_width = int(self.width / len(panel_list))
                if now_panel == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{now_panel}]"
                    now_draw.style = "onbutton"
                    now_draw.width = panel_width
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{now_panel}]",
                        f"\n{now_panel}",
                        panel_width,
                        cmd_func=self.change_panel,
                        args=(now_panel,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            draw.LineDraw("+", self.width).draw()

            if self.now_panel == _("全局课表"):
                Class_Schedule_Panel(self.width).draw()
            elif self.now_panel == _("个人课表"):
                course_select_panel.Course_Select_Panel(self.width).draw()
            else:
                growth_panel.Growth_Panel(self.width).draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, now_panel: str):
        """
        切换当前页签
        输入类型: now_panel(str)
        输出类型: 无
        功能: 更新当前显示页签
        """
        self.now_panel = now_panel


class Class_Schedule_Panel:
    """
    全局课表面板（方案 §5.2）
    输入类型: width(int)
    输出类型: 无
    功能: 一次展示一间教室的周表，可逐格排课
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 教室页签 + 周表 + 排课入口
        """
        room_list = schedule_handle.get_classroom_list()
        if not room_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  尚未开放任何教室\n")
            info_draw.draw()
            return
        now_room = room_list[0]

        while 1:
            return_list: List[str] = []
            # 教室页签：只列已解锁的（未解锁的教室不会出现在 place_data 里）
            for room in room_list:
                room_width = max(1, int(self.width / max(1, len(room_list))))
                if room == now_room:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{room}]"
                    now_draw.style = "onbutton"
                    now_draw.width = room_width
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(f"[{room}]", f"\n{room}", room_width)
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            draw.LineDraw("-", self.width).draw()

            course_type = schedule_handle.get_course_type_by_classroom(now_room)
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("  {0}｜承载课型：{1}\n").format(
                now_room, schedule_handle.COURSE_TYPE_NAME.get(course_type, _("未知")))
            info_draw.draw()

            cell_return = self._draw_week_table(now_room)
            return_list.extend(cell_return.keys())
            line_feed.draw()
            draw.LineDraw("-", self.width).draw()

            clear_draw = draw.CenterButton(_("[清空本教室]"), _("清空本教室"), int(self.width / 2))
            clear_draw.draw()
            return_list.append(clear_draw.return_text)
            back_draw = draw.CenterButton(_("[返回上级]"), _("返回上级"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            if yrn == clear_draw.return_text:
                self._clear_room(now_room)
                continue
            if yrn in cell_return:
                week_day, period = cell_return[yrn]
                self._edit_cell(now_room, week_day, period)
                continue
            for room in room_list:
                if yrn == f"\n{room}":
                    now_room = room
                    break

    def _draw_week_table(self, classroom: str) -> Dict[str, tuple]:
        """
        绘制一间教室的周表
        输入类型: classroom(str)
        输出类型: Dict[str, tuple]，按钮返回值 → (星期, 节次)
        功能: 9 行节次 × 7 列星期，每格显示"科目/教师"
        """
        cell_return: Dict[str, tuple] = {}
        head_width = 14
        cell_width = max(8, int((self.width - head_width) / len(WEEK_NAME)))

        head_draw = draw.NormalDraw()
        head_draw.width = head_width
        head_draw.text = _("  节次        ")
        head_draw.draw()
        for name in WEEK_NAME:
            now_draw = draw.CenterDraw()
            now_draw.width = cell_width
            now_draw.text = _(name)
            now_draw.draw()
        line_feed.draw()

        for period in range(len(game_time.CLASS_PERIOD_START)):
            head_draw = draw.NormalDraw()
            head_draw.width = head_width
            head_draw.text = "  {0} {1} ".format(period + 1, get_period_time_text(period)[:5])
            head_draw.draw()
            for week_day in range(len(WEEK_NAME)):
                cell = schedule_handle.get_class_cell(classroom, week_day, period)
                if cell is None:
                    cell_text = "--"
                else:
                    ability_name = game_config.config_ability[cell[0]].name
                    if cell[1] in cache.character_data:
                        cell_text = "{0}/{1}".format(ability_name, cache.character_data[cell[1]].name)
                    else:
                        cell_text = "{0}/{1}".format(ability_name, _("待定"))
                now_draw = draw.CenterButton(
                    cell_text, "\nCELL_{0}_{1}".format(week_day, period), cell_width)
                now_draw.draw()
                cell_return[now_draw.return_text] = (week_day, period)
            line_feed.draw()
        return cell_return

    def _clear_room(self, classroom: str):
        """
        清空一间教室的全部排课
        输入类型: classroom(str)
        输出类型: 无
        功能: 逐格调用 clear_class_cell
        """
        for week_day in range(len(WEEK_NAME)):
            for period in range(len(game_time.CLASS_PERIOD_START)):
                schedule_handle.clear_class_cell(classroom, week_day, period)

    def _edit_cell(self, classroom: str, week_day: int, period: int):
        """
        编辑一个课表格子：先选科目、再选教师
        输入类型: classroom(str), week_day(int), period(int)
        输出类型: 无
        功能: 撞课的教师直接置灰并标出原因，冲突在面板上阻止而不留到运行时兜错（方案 §3.14）
        """
        ability_id = self._select_subject(classroom, week_day, period)
        if ability_id == -1:
            return
        if ability_id == 0:
            schedule_handle.clear_class_cell(classroom, week_day, period)
            return
        teacher_id = self._select_teacher(classroom, week_day, period)
        if teacher_id == -2:
            return
        schedule_handle.set_class_cell(classroom, week_day, period, ability_id, teacher_id)

    def _select_subject(self, classroom: str, week_day: int, period: int) -> int:
        """
        选科目
        输入类型: classroom(str), week_day(int), period(int)
        输出类型: int，科目能力id；0为清空该格，-1为取消
        功能: 列出18门科目
        """
        draw.TitleLineDraw(_("选择科目"), self.width).draw()
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  {0}｜{1} 第{2}节 {3}\n").format(
            classroom, _(WEEK_NAME[week_day]), period + 1, get_period_time_text(period))
        info_draw.draw()

        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        for index, ability_id in enumerate(SUBJECT_ABILITY_LIST):
            now_draw = draw.LeftButton(
                _("[{0}]{1}").format(index, game_config.config_ability[ability_id].name),
                str(index), int(self.width / 4))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = ability_id
            if index % 4 == 3:
                line_feed.draw()
        line_feed.draw()
        clear_draw = draw.CenterButton(_("[清空本格]"), _("清空本格"), int(self.width / 2))
        clear_draw.draw()
        return_list.append(clear_draw.return_text)
        back_draw = draw.CenterButton(_("[取消]"), _("取消"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn == back_draw.return_text:
            return -1
        if yrn == clear_draw.return_text:
            return 0
        return id_by_return.get(yrn, -1)

    def _select_teacher(self, classroom: str, week_day: int, period: int) -> int:
        """
        选教师
        输入类型: classroom(str), week_day(int), period(int)
        输出类型: int，教师角色id；-1为本节不排教师（学生自习），-2为取消
        功能: 只列教师岗干员；撞课的置灰并标"第N节已在X教室"
        """
        draw.TitleLineDraw(_("选择授课教师"), self.width).draw()
        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        for teacher_id in schedule_handle.get_teacher_candidate_list():
            teacher_data: game_type.Character = cache.character_data[teacher_id]
            conflict = schedule_handle.judge_teacher_conflict(teacher_id, week_day, period, classroom)
            if conflict:
                # 撞课的不做成按钮，直接置灰并标出他这一节在哪——比事后报错好懂
                now_draw = draw.LeftDraw()
                now_draw.width = int(self.width / 2)
                now_draw.style = "deep_gray"
                now_draw.text = _(" {0}（{1}）").format(teacher_data.name, conflict)
                now_draw.draw()
            else:
                now_draw = draw.LeftButton(
                    _("[{0}]").format(teacher_data.name), str(teacher_id), int(self.width / 2))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = teacher_id
            line_feed.draw()
        line_feed.draw()
        none_draw = draw.CenterButton(_("[本节不排教师（学生自习）]"), _("不排教师"), int(self.width / 2))
        none_draw.draw()
        return_list.append(none_draw.return_text)
        back_draw = draw.CenterButton(_("[取消]"), _("取消"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn == back_draw.return_text:
            return -2
        if yrn == none_draw.return_text:
            return -1
        return id_by_return.get(yrn, -2)
