"""个人课表面板（Plan 22 一期 §5.3）

一次展示一个学生的周表（7 天 × 9 节），点格子先选课型、再选具体目标。
学生 = 职业为学生的全部干员（含成年）∪ 养成中的女儿（一期方案 §9.8.2），
顶部的人名页签每页 8 人、超出翻页（§9.8.1）。

⚠️ 「复制到其他学生」是多人场景下的关键操作（已确认口径 4）：不做这个，
   操作量会随学生数线性翻倍，三个学生就得把同一张表排三遍。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import game_time
from Script.System.Education_System import education_constant, schedule_handle, growth_handle, schedule_template_handle, student_tab_bar
from Script.System.Education_System.class_schedule_panel import get_period_time_text
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


class Course_Select_Panel:
    """
    个人课表面板（方案 §5.3）
    输入类型: width(int)
    输出类型: 无
    功能: 按学生展示与编辑个人课表
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        self.now_student: int = -1
        """ 当前展示的学生角色id，-1表示尚未选择，由 draw_page 回落到第一个 """
        self.student_list: List[int] = []
        """ 本轮可排课的学生列表，每轮在 draw_page 里重算 """
        self.cell_return: Dict[str, tuple] = {}
        """ 本轮课表格子按钮的返回值 → (星期, 节次)，由 draw_page 写、handle_yrn 读 """
        self.tab_bar = student_tab_bar.Student_Tab_Bar(width, "\nSTU_")
        """ 顶部的人名页签栏，每页8人。⚠️ 页码存在它身上，容器每轮重画也不会丢 """

    def draw_page(self, return_list: List[str]):
        """
        绘制本页内容
        输入类型: return_list(List[str])，容器的共享返回值列表，本页的按钮往里加
        输出类型: 无
        功能: 学生页签（每页8人，可翻页）+ 周表 + 选课入口。
              ⚠️ 只画不取输入，askfor_all 由容器 Education_Manage_Panel 统一调用
        """
        # 每轮重算：孩子会在游戏过程中出生与长大、干员会换岗，不能在 __init__ 里快照。
        # ⚠️ 口径是「职业为学生的全部干员 ∪ 养成中的女儿」，与养成总览的「只看女儿」不同（方案 §9.8.2）
        self.student_list = growth_handle.get_course_candidate_list()
        # ⚠️ 先清空派发字典再早退，否则 handle_yrn 会拿上一轮的残留去匹配
        self.cell_return = {}
        if not self.student_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  目前还没有职业为学生的干员\n")
            info_draw.draw()
            return
        # 选中态失效（首次进入，或原来那个学生已不在列表里）时回落到第一个，并把页签栏翻到她所在的那页
        if self.now_student not in self.student_list:
            self.now_student = self.student_list[0]
            self.tab_bar.jump_to(self.student_list, self.now_student)

        self.tab_bar.draw(self.student_list, self.now_student, return_list)

        self.cell_return = self._draw_week_table(self.now_student)
        return_list.extend(self.cell_return.keys())
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

        # 日程一行：管的是这个孩子没课的时段干什么（Plan 22 二期 §5.2）
        schedule_draw = draw.LeftButton(
            _(" 日程：{0} [改]").format(schedule_template_handle.get_child_schedule_text(self.now_student)),
            "EDIT_SCHEDULE", self.width)
        schedule_draw.draw()
        return_list.append(schedule_draw.return_text)
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

        auto_draw = draw.CenterButton(_("[一键选课]"), _("一键选课"), int(self.width / 3))
        auto_draw.draw()
        return_list.append(auto_draw.return_text)
        copy_draw = draw.CenterButton(_("[复制到其他学生]"), _("复制"), int(self.width / 3))
        copy_draw.draw()
        return_list.append(copy_draw.return_text)
        clear_draw = draw.CenterButton(_("[清空]"), _("清空"), int(self.width / 3))
        clear_draw.draw()
        return_list.append(clear_draw.return_text)
        line_feed.draw()

    def handle_yrn(self, yrn: str):
        """
        处理本页按钮的选择结果
        输入类型: yrn(str)，容器 askfor_all 的返回值
        输出类型: 无
        功能: 翻页 / 切换学生 / 清空 / 复制 / 改日程 / 编辑某一格
        """
        # 翻页与选中的学生无关，先判掉
        if self.tab_bar.handle_page_yrn(yrn):
            return
        if not self.student_list:
            return
        if yrn == _("一键选课"):
            self._auto_fill_course(self.now_student)
            return
        if yrn == _("清空"):
            self._clear_student(self.now_student)
            return
        if yrn == _("复制"):
            self._copy_to_others(self.now_student, self.student_list)
            return
        if yrn == "EDIT_SCHEDULE":
            self._edit_schedule(self.now_student)
            return
        if yrn in self.cell_return:
            week_day, period = self.cell_return[yrn]
            self._edit_cell(self.now_student, week_day, period)
            return
        student_id = self.tab_bar.get_student_by_yrn(yrn, self.student_list)
        if student_id != -1:
            self.now_student = student_id

    def _draw_week_table(self, character_id: int) -> Dict[str, tuple]:
        """
        绘制一个学生的周表
        输入类型: character_id(int)
        输出类型: Dict[str, tuple]，按钮返回值 → (星期, 节次)
        功能: 班级式课显示"科目名/教室名"，个人式课显示"[课型缩写]目标"
        """
        cell_return: Dict[str, tuple] = {}
        head_width = 14
        cell_width = max(8, int((self.width - head_width) / len(education_constant.WEEK_NAME)))

        head_draw = draw.NormalDraw()
        head_draw.width = head_width
        head_draw.text = _("  节次        ")
        head_draw.draw()
        for name in education_constant.WEEK_NAME:
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
            for week_day in range(len(education_constant.WEEK_NAME)):
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
        功能: 未排课为 --。
              班级式课（理论/实践/公开）的目标是教室名，光看教室不知道这节上什么，
              所以回查全局课表把科目名一并写出来，成"学识技能/理论教室一"。
              ⚠️ 班级式课**不加课型缩写**：「理论教室一」本身就说明了是理论课。
                 个人式的三种课型才需要「[体]」「[兴]」「[实]」——它们的目标名看不出课型
        """
        course = schedule_handle.get_selected_course(character_id, week_day, period)
        if course is None:
            return "--"
        course_type, target = course[0], course[1]
        if course_type in education_constant.CLASSROOM_COURSE_TYPE_SET:
            # ⚠️ 必须走 get_class_cell：它是全局课表的唯一读取入口，
            #    直接读 class_schedule 会漏掉临时性技实操课的覆盖层
            cell = schedule_handle.get_class_cell(target, week_day, period)
            if cell is not None and cell[0] in game_config.config_ability:
                return "{0}/{1}".format(game_config.config_ability[cell[0]].name, target)
            # 选了这间教室，但那节课后来被清掉了——照实显示，别让玩家以为还有课
            return _("{0}/已停课").format(target)
        short = education_constant.COURSE_TYPE_SHORT.get(course_type, "?")
        if course_type == education_constant.COURSE_TYPE_INTEREST:
            target = game_config.config_entertainment[target].name
        elif course_type == education_constant.COURSE_TYPE_INTERN:
            target = game_config.config_work_type[target].name
        return "[{0}]{1}".format(short, target)

    def _auto_fill_course(self, character_id: int):
        """
        一键把这个学生个人课表上的空节次选满
        输入类型: character_id(int)
        输出类型: 无
        功能: 有课就上。同一节有多间教室开课时选她该科等级最低的那门。
              ⚠️ 只填空格，已有的选课一节不动
        """
        from Script.System.Education_System import auto_schedule

        filled_count, skip_count = auto_schedule.auto_fill_selected_course(character_id)
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.style = "gold_enrod"
        name = cache.character_data[character_id].name
        if filled_count:
            info_draw.text = _("\n已为{0}选上 {1} 节课").format(name, filled_count)
            if skip_count:
                info_draw.text += _("；另有 {0} 节全岛都没有教室开课，留给日程模板").format(skip_count)
            info_draw.text += "\n"
        elif skip_count:
            info_draw.text = _("\n没能选上任何一节课：全岛课表上还没排课，先去「全局课表」排好再来\n")
        else:
            info_draw.text = _("\n{0}的课表已经选满了\n").format(name)
        info_draw.draw()

    def _clear_student(self, character_id: int):
        """
        清空一个学生的全部选课
        输入类型: character_id(int)
        输出类型: 无
        功能: 逐格调用 clear_selected_course
        """
        for week_day in range(len(education_constant.WEEK_NAME)):
            for period in range(len(game_time.CLASS_PERIOD_START)):
                schedule_handle.clear_selected_course(character_id, week_day, period)

    def _edit_schedule(self, character_id: int):
        """
        单孩日程微调：换模板，或对某个时段单独覆盖
        输入类型: character_id(int)
        输出类型: 无
        功能: 覆盖只存在这个孩子身上，不影响模板本体与其他孩子（方案 §5.2）
        """
        from Script.System.Education_System import schedule_template_panel

        template_panel = schedule_template_panel.Schedule_Template_Panel(self.width)
        while 1:
            return_list: List[str] = []
            slot_by_return: Dict[str, int] = {}
            draw.TitleLineDraw(
                _("{0}的日程").format(cache.character_data[character_id].name), self.width).draw()
            # 当前套用的模板
            change_draw = draw.LeftButton(
                _(" 日程模板：{0} [改]").format(
                    schedule_template_handle.get_child_schedule_text(character_id)),
                "CHANGE_TEMPLATE", self.width)
            change_draw.draw()
            return_list.append(change_draw.return_text)
            line_feed.draw()
            draw.LineDraw("-", self.width).draw()
            # 三个时段，点进去单独覆盖
            for slot in range(education_constant.SLOT_COUNT):
                entertainment_id = schedule_template_handle.get_child_slot_activity(character_id, slot)
                if entertainment_id and entertainment_id in game_config.config_entertainment:
                    now_name = game_config.config_entertainment[entertainment_id].name
                else:
                    now_name = _("未设置")
                growth_data = cache.character_data[character_id].child_growth
                override_mark = ""
                if growth_data is not None and slot in growth_data.schedule_override:
                    override_mark = _("（单独指定）")
                now_draw = draw.LeftButton(
                    _(" [{0}：{1}{2}]").format(
                        education_constant.SLOT_NAME[slot], now_name, override_mark),
                    f"CHILD_SLOT_{slot}", int(self.width / 2))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                slot_by_return[now_draw.return_text] = slot
                line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回日程"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            if yrn == change_draw.return_text:
                template_id = template_panel._select_template()
                if template_id is not None:
                    schedule_template_handle.apply_template(character_id, template_id)
                continue
            if yrn in slot_by_return:
                entertainment_id = template_panel._select_activity()
                if entertainment_id is not None:
                    schedule_template_handle.set_child_override(
                        character_id, slot_by_return[yrn], entertainment_id)

    def _copy_to_others(self, character_id: int, student_list: List[int]):
        """
        把当前学生的课表整份复制给另一个学生
        输入类型: character_id(int), student_list(List[int])
        输出类型: 无
        功能: 覆盖式复制；⚠️ 教室课复制过去后可能与对方已有的课冲突，所以先清空再写。
              名单每行6个（190/6=31列）：成年学生也进名单之后一行一个会拉得很长
        """
        draw.TitleLineDraw(_("复制课表到"), self.width).draw()
        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        count = 0
        for other_id in student_list:
            if other_id == character_id:
                continue
            now_draw = draw.LeftButton(
                _("[{0}]").format(cache.character_data[other_id].name),
                f"COPY_{other_id}", int(self.width / 6))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = other_id
            count += 1
            if count % 6 == 0:
                line_feed.draw()
        if count % 6:
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
        for week_day in range(len(education_constant.WEEK_NAME)):
            for period in range(len(game_time.CLASS_PERIOD_START)):
                course = schedule_handle.get_selected_course(character_id, week_day, period)
                if course is None:
                    continue
                schedule_handle.set_selected_course(target_id, week_day, period, course[0], course[1])

    def _edit_cell(self, character_id: int, week_day: int, period: int):
        """
        编辑一个个人课表格子
        输入类型: character_id(int), week_day(int), period(int)
        输出类型: 无
        功能: 班级式课（理论/实践/公开）在第一屏直接列出「本节各教室都有什么课」，看得见再选；
              体育/兴趣/实习三类没有全局课表可查，仍是先选类型再选目标（方案 §3.21）
        """
        result = self._select_course(character_id, week_day, period)
        if result is None:
            return
        if result == "CLEAR":
            schedule_handle.clear_selected_course(character_id, week_day, period)
            return
        course_type, target = result
        schedule_handle.set_selected_course(character_id, week_day, period, course_type, target)

    def _select_course(self, character_id: int, week_day: int, period: int):
        """
        选课第一屏：本节可上的教室课 + 三类个人式课型入口
        输入类型: character_id(int), week_day(int), period(int)
        输出类型: (课型int, 目标) 元组；"CLEAR"为清空该格；None为取消
        功能: ⚠️ 班级式课不再让玩家「先猜课型、再看有没有课」——课型信息本就蕴含在教室名里
                 （理论教室→理论课、实践教室→实践课、大礼堂→公开课），
                 所以直接列出本节各教室实际排了什么，玩家选的是「去上哪节课」而不是「什么类型的课」
        """
        draw.TitleLineDraw(_("选择课程"), self.width).draw()
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  {0}｜{1} 第{2}节 {3}\n\n").format(
            cache.character_data[character_id].name, _(education_constant.WEEK_NAME[week_day]),
            period + 1, get_period_time_text(period))
        info_draw.draw()

        return_list: List[str] = []
        result_by_return: Dict[str, tuple] = {}

        # ---- 段一：本节各教室分别有什么课 ----
        head_draw = draw.NormalDraw()
        head_draw.width = self.width
        head_draw.style = "gold_enrod"
        head_draw.text = _("  本节各教室的课（选中即去上这节课）：\n")
        head_draw.draw()
        class_count = 0
        # ⚠️ 必须逐间走 get_class_cell：它是全局课表的唯一读取入口，
        #    直接遍历 class_schedule 会漏掉临时性技实操课的覆盖层，也漏掉从没排过课的教室
        for classroom in schedule_handle.get_classroom_list():
            cell = schedule_handle.get_class_cell(classroom, week_day, period)
            if cell is None:
                now_draw = draw.LeftDraw()
                now_draw.width = int(self.width / 2)
                now_draw.style = "deep_gray"
                now_draw.text = _(" {0}（本节没有课）").format(classroom)
                now_draw.draw()
                line_feed.draw()
                continue
            class_count += 1
            teacher_name = _("无教师（自习）")
            if cell[1] in cache.character_data:
                teacher_name = cache.character_data[cell[1]].name
            course_type = schedule_handle.get_course_type_by_classroom(classroom)
            now_draw = draw.LeftButton(
                _("[{0}] {1}/{2}（{3}）").format(
                    classroom, game_config.config_ability[cell[0]].name, teacher_name,
                    education_constant.COURSE_TYPE_NAME.get(course_type, _("未知"))),
                f"CLS_{classroom}", int(self.width / 2))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            result_by_return[now_draw.return_text] = (course_type, classroom)
            line_feed.draw()
        if not class_count:
            empty_draw = draw.NormalDraw()
            empty_draw.width = self.width
            empty_draw.style = "deep_gray"
            empty_draw.text = _("  本节所有教室都没有排课，先去「全局课表」排好再来选\n")
            empty_draw.draw()

        # ---- 段二：三类个人式课型 ----
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()
        type_head_draw = draw.NormalDraw()
        type_head_draw.width = self.width
        type_head_draw.style = "gold_enrod"
        type_head_draw.text = _("  不去教室，改上：\n")
        type_head_draw.draw()
        type_by_return: Dict[str, int] = {}
        for course_type in (education_constant.COURSE_TYPE_PE,
                            education_constant.COURSE_TYPE_INTEREST,
                            education_constant.COURSE_TYPE_INTERN):
            now_draw = draw.CenterButton(
                _("[{0}]").format(education_constant.COURSE_TYPE_NAME[course_type]),
                f"CT_{course_type}", int(self.width / 6))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            type_by_return[now_draw.return_text] = course_type
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
            return None
        if yrn == clear_draw.return_text:
            return "CLEAR"
        if yrn in result_by_return:
            return result_by_return[yrn]
        if yrn in type_by_return:
            course_type = type_by_return[yrn]
            target = self._select_target(character_id, week_day, period, course_type)
            if target is None:
                return None
            return (course_type, target)
        return None

    def _select_target(self, character_id: int, week_day: int, period: int, course_type: int):
        """
        选个人式课型的具体目标
        输入类型: character_id(int), week_day(int), period(int), course_type(int)
        输出类型: 目标值（str或int），取消则为None
        功能: 只处理体育/兴趣/实习三类，三类都是每行6个按钮。
              班级式课不走这里——它在 _select_course 的第一屏就选完了。
              实习课周日整列不可选（方案 §3.21）
        """
        draw.TitleLineDraw(_("选择{0}的内容").format(
            education_constant.COURSE_TYPE_NAME[course_type]), self.width).draw()
        return_list: List[str] = []
        target_by_return: Dict[str, object] = {}
        empty_flag = True
        # 每行6个：190/6=31列，6×31=186≤190
        cell_width = int(self.width / 6)
        index = 0

        # 体育课：四处训练场地点
        if course_type == education_constant.COURSE_TYPE_PE:
            for place_name in education_constant.PE_PLACE_DATA:
                if not schedule_handle.get_course_place(
                        {"course_type": course_type, "target": place_name}):
                    now_draw = draw.LeftDraw()
                    now_draw.width = cell_width
                    now_draw.style = "deep_gray"
                    now_draw.text = _(" {0}（未开放）").format(place_name)
                    now_draw.draw()
                else:
                    empty_flag = False
                    now_draw = draw.LeftButton(
                        _("[{0}]").format(place_name), f"TG_{place_name}", cell_width)
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
                    target_by_return[now_draw.return_text] = place_name
                index += 1
                if index % 6 == 0:
                    line_feed.draw()

        # 兴趣课：class_ok == 1 的娱乐项
        elif course_type == education_constant.COURSE_TYPE_INTEREST:
            for cid in game_config.config_entertainment:
                if not game_config.config_entertainment[cid].class_ok:
                    continue
                empty_flag = False
                now_draw = draw.LeftButton(
                    _("[{0}]").format(game_config.config_entertainment[cid].name),
                    f"TG_{cid}", cell_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
                target_by_return[now_draw.return_text] = cid
                index += 1
                if index % 6 == 0:
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
                for cid in game_config.config_work_type:
                    work_data = game_config.config_work_type[cid]
                    if work_data.tag or cid in education_constant.EXCLUDE_INTERN_WORK_TYPE or not work_data.ability_id:
                        continue
                    empty_flag = False
                    now_draw = draw.LeftButton(
                        _("[{0}]").format(work_data.name), f"TG_{cid}", cell_width)
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
                    target_by_return[now_draw.return_text] = cid
                    index += 1
                    if index % 6 == 0:
                        line_feed.draw()
        if index % 6:
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
