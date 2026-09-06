"""个人课表面板（Plan 22 一期 §5.3）

一次展示一个孩子的周表（7 天 × 9 节），点格子先选课型、再选具体目标。

⚠️ 「复制到其他孩子」是多孩场景下的关键操作（已确认口径 4）：不做这个，
   操作量会随孩子数线性翻倍，三个孩子就得把同一张表排三遍。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import game_time
from Script.System.Education_System import schedule_handle, growth_handle
from Script.System.Education_System.class_schedule_panel import (
    WEEK_NAME, get_period_time_text)
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

COURSE_TYPE_SHORT = {0: "理", 1: "践", 2: "公", 3: "体", 4: "兴", 5: "实"}
""" 课型在格子里的单字缩写，格子宽度只够放一个字 """

EXCLUDE_INTERN_WORK_TYPE = {151, 152}
""" 实习课不开放的岗位：教师与学生是孩子自己在学校里的身份，作为"实习"语义重复（方案 §3.21） """


def get_student_candidate_list() -> List[int]:
    """
    取可排个人课表的角色列表
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表，孩子在前
    """
    child_list = []
    other_list = []
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        if growth_handle.judge_is_child(character_id):
            child_list.append(character_id)
        elif character_data.child_growth is not None and character_data.child_growth.selected_course:
            # 成年干员自选了课时也要能改（已确认口径 24）
            other_list.append(character_id)
    return child_list + other_list


class Course_Select_Panel:
    """
    个人课表面板（方案 §5.3）
    输入类型: width(int)
    输出类型: 无
    功能: 按孩子展示与编辑个人课表
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 孩子页签 + 周表 + 选课入口
        """
        student_list = get_student_candidate_list()
        if not student_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  目前还没有需要排课的孩子\n")
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
                    now_draw = draw.CenterButton(f"[{name}]", f"\nSTU_{student_id}", tab_width)
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            draw.LineDraw("-", self.width).draw()

            cell_return = self._draw_week_table(now_student)
            return_list.extend(cell_return.keys())
            line_feed.draw()
            draw.LineDraw("-", self.width).draw()

            copy_draw = draw.CenterButton(_("[复制到其他孩子]"), _("复制"), int(self.width / 3))
            copy_draw.draw()
            return_list.append(copy_draw.return_text)
            clear_draw = draw.CenterButton(_("[清空]"), _("清空"), int(self.width / 3))
            clear_draw.draw()
            return_list.append(clear_draw.return_text)
            back_draw = draw.CenterButton(_("[返回上级]"), _("返回上级"), int(self.width / 3))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            if yrn == clear_draw.return_text:
                self._clear_student(now_student)
                continue
            if yrn == copy_draw.return_text:
                self._copy_to_others(now_student, student_list)
                continue
            if yrn in cell_return:
                week_day, period = cell_return[yrn]
                self._edit_cell(now_student, week_day, period)
                continue
            for student_id in student_list:
                if yrn == f"\nSTU_{student_id}":
                    now_student = student_id
                    break

    def _draw_week_table(self, character_id: int) -> Dict[str, tuple]:
        """
        绘制一个孩子的周表
        输入类型: character_id(int)
        输出类型: Dict[str, tuple]，按钮返回值 → (星期, 节次)
        功能: 每格显示"[课型缩写] 目标"
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
                now_draw = draw.CenterButton(
                    self._get_cell_text(character_id, week_day, period),
                    "\nMYCELL_{0}_{1}".format(week_day, period), cell_width)
                now_draw.draw()
                cell_return[now_draw.return_text] = (week_day, period)
            line_feed.draw()
        return cell_return

    def _get_cell_text(self, character_id: int, week_day: int, period: int) -> str:
        """
        取一个格子的显示文本
        输入类型: character_id(int), week_day(int), period(int)
        输出类型: str
        功能: 未排课为 --，否则为"[课型缩写]目标"
        """
        course = schedule_handle.get_selected_course(character_id, week_day, period)
        if course is None:
            return "--"
        course_type, target = course[0], course[1]
        short = COURSE_TYPE_SHORT.get(course_type, "?")
        if course_type == schedule_handle.COURSE_TYPE_INTEREST:
            target = game_config.config_entertainment[target].name
        elif course_type == schedule_handle.COURSE_TYPE_INTERN:
            target = game_config.config_work_type[target].name
        return "[{0}]{1}".format(short, target)

    def _clear_student(self, character_id: int):
        """
        清空一个孩子的全部选课
        输入类型: character_id(int)
        输出类型: 无
        功能: 逐格调用 clear_selected_course
        """
        for week_day in range(len(WEEK_NAME)):
            for period in range(len(game_time.CLASS_PERIOD_START)):
                schedule_handle.clear_selected_course(character_id, week_day, period)

    def _copy_to_others(self, character_id: int, student_list: List[int]):
        """
        把当前孩子的课表整份复制给另一个孩子
        输入类型: character_id(int), student_list(List[int])
        输出类型: 无
        功能: 覆盖式复制；⚠️ 教室课复制过去后可能与对方已有的课冲突，所以先清空再写
        """
        draw.TitleLineDraw(_("复制课表到"), self.width).draw()
        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        for other_id in student_list:
            if other_id == character_id:
                continue
            now_draw = draw.LeftButton(
                _("[{0}]").format(cache.character_data[other_id].name),
                f"COPY_{other_id}", int(self.width / 2))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = other_id
            line_feed.draw()
        back_draw = draw.CenterButton(_("[取消]"), _("取消"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn not in id_by_return:
            return
        target_id = id_by_return[yrn]
        self._clear_student(target_id)
        for week_day in range(len(WEEK_NAME)):
            for period in range(len(game_time.CLASS_PERIOD_START)):
                course = schedule_handle.get_selected_course(character_id, week_day, period)
                if course is None:
                    continue
                schedule_handle.set_selected_course(target_id, week_day, period, course[0], course[1])

    def _edit_cell(self, character_id: int, week_day: int, period: int):
        """
        编辑一个个人课表格子：先选课型、再选目标
        输入类型: character_id(int), week_day(int), period(int)
        输出类型: 无
        功能: 各课型的候选表见方案 §3.21
        """
        course_type = self._select_course_type(character_id, week_day, period)
        if course_type == -1:
            return
        if course_type == -2:
            schedule_handle.clear_selected_course(character_id, week_day, period)
            return
        target = self._select_target(character_id, week_day, period, course_type)
        if target is None:
            return
        schedule_handle.set_selected_course(character_id, week_day, period, course_type, target)

    def _select_course_type(self, character_id: int, week_day: int, period: int) -> int:
        """
        选课型
        输入类型: character_id(int), week_day(int), period(int)
        输出类型: int，课型编号；-1为取消，-2为清空该格
        功能: 六种课型
        """
        draw.TitleLineDraw(_("选择课型"), self.width).draw()
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  {0}｜{1} 第{2}节 {3}\n").format(
            cache.character_data[character_id].name, _(WEEK_NAME[week_day]),
            period + 1, get_period_time_text(period))
        info_draw.draw()

        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        for course_type in sorted(schedule_handle.COURSE_TYPE_NAME.keys()):
            now_draw = draw.LeftButton(
                _("[{0}]").format(schedule_handle.COURSE_TYPE_NAME[course_type]),
                f"CT_{course_type}", int(self.width / 3))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = course_type
            if course_type % 3 == 2:
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
        if yrn == clear_draw.return_text:
            return -2
        return id_by_return.get(yrn, -1)

    def _select_target(self, character_id: int, week_day: int, period: int, course_type: int):
        """
        选具体目标
        输入类型: character_id(int), week_day(int), period(int), course_type(int)
        输出类型: 目标值（str或int），取消则为None
        功能: 教室课只列该节次已排课的教室；实习课周日整列不可选（方案 §3.21）
        """
        draw.TitleLineDraw(_("选择{0}的内容").format(
            schedule_handle.COURSE_TYPE_NAME[course_type]), self.width).draw()
        return_list: List[str] = []
        target_by_return: Dict[str, object] = {}
        empty_flag = True

        # 班级式：只列该节次已经排了课的教室，格子上直接把"科目/教师"写出来，看得见再选
        if course_type in schedule_handle.CLASSROOM_COURSE_TYPE_SET:
            for classroom in schedule_handle.get_classroom_list(course_type):
                cell = schedule_handle.get_class_cell(classroom, week_day, period)
                if cell is None:
                    now_draw = draw.LeftDraw()
                    now_draw.width = int(self.width / 2)
                    now_draw.style = "deep_gray"
                    now_draw.text = _(" {0}（本节没有课）").format(classroom)
                    now_draw.draw()
                    line_feed.draw()
                    continue
                empty_flag = False
                teacher_name = _("无教师（自习）")
                if cell[1] in cache.character_data:
                    teacher_name = cache.character_data[cell[1]].name
                now_draw = draw.LeftButton(
                    _("[{0}] {1}/{2}").format(
                        classroom, game_config.config_ability[cell[0]].name, teacher_name),
                    f"TG_{classroom}", int(self.width / 2))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                target_by_return[now_draw.return_text] = classroom
                line_feed.draw()

        # 体育课：四处训练场地点
        elif course_type == schedule_handle.COURSE_TYPE_PE:
            for place_name in schedule_handle.PE_PLACE_DATA:
                if not schedule_handle.get_course_place(
                        {"course_type": course_type, "target": place_name}):
                    now_draw = draw.LeftDraw()
                    now_draw.width = int(self.width / 2)
                    now_draw.style = "deep_gray"
                    now_draw.text = _(" {0}（尚未开放）").format(place_name)
                    now_draw.draw()
                    line_feed.draw()
                    continue
                empty_flag = False
                now_draw = draw.LeftButton(
                    _("[{0}]").format(place_name), f"TG_{place_name}", int(self.width / 2))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                target_by_return[now_draw.return_text] = place_name
                line_feed.draw()

        # 兴趣课：class_ok == 1 的娱乐项
        elif course_type == schedule_handle.COURSE_TYPE_INTEREST:
            index = 0
            for cid in game_config.config_entertainment:
                if not game_config.config_entertainment[cid].class_ok:
                    continue
                empty_flag = False
                now_draw = draw.LeftButton(
                    _("[{0}]").format(game_config.config_entertainment[cid].name),
                    f"TG_{cid}", int(self.width / 4))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                target_by_return[now_draw.return_text] = cid
                index += 1
                if index % 4 == 0:
                    line_feed.draw()
            line_feed.draw()

        # 实习课：tag == 0 且非教师/学生的岗位；周日无人在岗，整列不可选
        else:
            if week_day == 6:
                now_draw = draw.NormalDraw()
                now_draw.width = self.width
                now_draw.style = "deep_gray"
                now_draw.text = _("\n  周日全岛无人上班，实习课找不到带教干员，本日不可排\n")
                now_draw.draw()
            else:
                index = 0
                for cid in game_config.config_work_type:
                    work_data = game_config.config_work_type[cid]
                    if work_data.tag or cid in EXCLUDE_INTERN_WORK_TYPE or not work_data.ability_id:
                        continue
                    empty_flag = False
                    now_draw = draw.LeftButton(
                        _("[{0}]").format(work_data.name), f"TG_{cid}", int(self.width / 4))
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
                    target_by_return[now_draw.return_text] = cid
                    index += 1
                    if index % 4 == 0:
                        line_feed.draw()
                line_feed.draw()

        if empty_flag:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  本节次没有可选的内容\n")
            info_draw.draw()
        line_feed.draw()
        back_draw = draw.CenterButton(_("[取消]"), _("取消"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        return target_by_return.get(yrn, None)
