"""全局课表面板（Plan 22 一期 §5.2）与教育管理系统的页签容器

课表是「10 教室 × 7 天 × 9 节」的三维数据，一次全画必然超出终端宽度。
   本面板一次只展示**一间教室**的周表（7 天 × 9 节），教室用上方的横向标签页切换——
   降一个维度之后 Tk 与 Web 都画得下（方案 §5.2）。

只用 Script/UI/Moudle/draw.py 的抽象绘制类，不直接碰 Tk 或 HTML；
   Web_Draw_System/web_draw_adapter.py 在启动时包装这些抽象类，双模式才能同时成立。
"""
import datetime
from types import FunctionType
from typing import Dict, List, Protocol

from Script.Core import cache_control, game_type, get_text, flow_handle, constant, text_handle
from Script.Config import game_config, normal_config
from Script.Design import game_time, attr_calculation, basement
from Script.System.Education_System import education_constant, schedule_handle
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


def get_teacher_absent_mark(teacher_id: int, short: bool = False) -> str:
    """
    取课表格子上教师名字后的缺位标注（Plan 31 §3.10，全局课表与个人课表选课页共用；Plan 32 §3.13 加监禁）
    Keyword arguments:
    teacher_id -- 格子上排的教师角色id；-1 为没排教师，0 为玩家（临时实操课的授课者）
    short -- 是否取短写「（离岗）」「（监禁）」「（离岛）」。全局周表一格只有 25 列（190 宽），「学识技能/三字名（不在岛上）」就有 27 列，
             会被截成「~」把标注吃掉；周表用短写（四个字的名字也放得下）、悬停提示写全称，个人课表选课页等宽裕的地方用全称
    Return arguments:
    str -- 「（已离岗）」「（被监禁）」「（不在岛上）」（短写为「（离岗）」「（监禁）」「（离岛）」）或空字符串
    功能: 改了岗、被监禁、或不在岛上（不在 npc_id_got）的教师，运行时 class_ai.judge_teacher_available 判来不了、学生降级自习；
             但一键排课只填空格、不会替换她，这些格子每周都是自习。面板照写名字不加提示，玩家看不出要手动换人。
          被监禁的教师仍在岛上、仍挂教师岗（Plan 32 §3.13 L21）：此前格子不灰不标，关着的这段时间每节都是自习。
          几种同时成立时按「已离岗 → 被监禁 → 不在岛上」取第一种：改了岗的人放出来、回岛都不会再授课，一定要换人；
             被监禁的人要等玩家放人；不在岛上的人回来就能照常授课。
          只标这几种长期状态，睡着、H 中这类一节之内会恢复的不标；玩家与没排教师的格子不标
    """
    if teacher_id <= 0 or teacher_id not in cache.character_data:
        return ""
    teacher_data: game_type.Character = cache.character_data[teacher_id]
    if teacher_data.work.work_type != education_constant.TEACHER_WORK_TYPE:
        return _("（离岗）") if short else _("（已离岗）")
    if teacher_data.sp_flag.imprisonment:
        return _("（监禁）") if short else _("（被监禁）")
    if teacher_id not in cache.npc_id_got:
        return _("（离岛）") if short else _("（不在岛上）")
    return ""


def fit_text_width(text: str, width: int) -> str:
    """
    把文本按显示宽度截到不超过 width（Plan 31 §3.10）
    Keyword arguments:
    text -- 原文本
    width -- 最大显示宽度（列数），不足 0 时截成空串
    Return arguments:
    str -- 截好的文本；原文本放得下时原样返回
    功能: 全局周表的格子先截教师名、再拼离岗 / 离岛标注：整格超宽时 CenterButton 从尾部截成「~」，
          异格干员这类五六个字的名字会把标注整个吃掉，只剩灰字；全名与后果写在悬停提示里
    """
    if text_handle.get_text_index(text) <= width:
        return text
    now_text = ""
    for char in text:
        if text_handle.get_text_index(now_text + char) > width:
            break
        now_text += char
    return now_text


class SubPanelProtocol(Protocol):
    """
    四个页签子面板共同遵守的接口
    输入类型: 无
    输出类型: 无
    功能: 容器 Education_Manage_Panel 只按这两个方法调用子面板，全面板唯一的 askfor_all 在容器里。
          写成 Protocol 而不是把 panel_map 标成 object，是为了让类型检查器认得这两个调用，
          又不必在文件顶层 import 三个子面板类——那会造成循环导入，见 Education_Manage_Panel.__init__ 里的说明
    """

    def draw_page(self, return_list: List[str]) -> None:
        """
        绘制本页内容
        Keyword arguments:
        return_list -- 容器的共享返回值列表，本页的按钮返回值往里加
        Return arguments:
        无
        """
        ...

    def handle_yrn(self, yrn: str) -> None:
        """
        处理属于本页的那一份返回值
        Keyword arguments:
        yrn -- 容器的 askfor_all 拿到的返回值
        Return arguments:
        无
        """
        ...


class Education_Manage_Panel:
    """
    教育管理系统主面板（教师办公室入口，方案 §5.1）
    输入类型: width(int)
    输出类型: 无
    功能: 三个子页的页签容器——全局课表 / 个人课表 / 养成总览
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        # course_select_panel 在自己的模块顶层反向 import 本模块（取 get_period_time_text），
        #    所以只能在函数内 import，提到文件顶层会循环导入。
        #    共用常量已集中到 education_constant，不再是造成这个环的原因
        from Script.System.Education_System import course_select_panel, growth_panel, schedule_template_panel

        self.width: int = width
        self.now_panel: str = _("全局课表")
        self.panel_list: List[str] = [_("全局课表"), _("个人课表"), _("日程模板"), _("养成总览")]
        """ 四个页签的显示名，同时也是 panel_map 的键 """
        # 子面板实例只创建一次并存起来：容器每轮 while 都会重画，
        #    如果每轮 new 一个，子面板里的选中态（当前教室 / 当前孩子）必然被重置
        self.panel_map: Dict[str, SubPanelProtocol] = {
            _("全局课表"): Class_Schedule_Panel(width),
            _("个人课表"): course_select_panel.Course_Select_Panel(width),
            _("日程模板"): schedule_template_panel.Schedule_Template_Panel(width),
            _("养成总览"): growth_panel.Growth_Panel(width),
        }
        """ 页签名到子面板实例的映射 """

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 绘制页签并分发到对应子页面。
              全面板**只有这一处** askfor_all：子面板只负责往共享的 return_list 里加按钮、
                 以及事后处理自己那份 yrn。子面板一旦自带 while+askfor_all，
                 页签按钮就会因为不在当前 return_list 里而报「选项无效」
        """
        title_draw = draw.TitleLineDraw(_("教育管理系统"), self.width)

        while 1:
            # 按设施等级刷新各房间的开放状态，教室列表要靠它（照宿舍管理面板的写法）
            basement.get_base_updata()
            return_list: List[str] = []
            tab_return_map: Dict[str, str] = {}
            title_draw.draw()
            self._draw_semester_head()
            for now_panel in self.panel_list:
                panel_width = int(self.width / len(self.panel_list))
                if now_panel == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{now_panel}]"
                    now_draw.style = "onbutton"
                    now_draw.width = panel_width
                    now_draw.draw()
                else:
                    # 这里不能用 cmd_func：askfor_all 是先执行 cmd_func 再 return，
                    #    那样返回时 self.now_panel 已经变了，下面就会把本屏的 yrn 派发给新页签的面板
                    now_draw = draw.CenterButton(f"[{now_panel}]", f"\n{now_panel}", panel_width)
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
                    tab_return_map[now_draw.return_text] = now_panel
            line_feed.draw()
            draw.LineDraw("+", self.width).draw()

            now_sub_panel = self.panel_map[self.now_panel]
            now_sub_panel.draw_page(return_list)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break
            if yrn in tab_return_map:
                self.change_panel(tab_return_map[yrn])
                continue
            now_sub_panel.handle_yrn(yrn)

    def _draw_semester_head(self):
        """
        绘制学期抬头
        输入类型: 无
        输出类型: 无
        功能: 一行学期名与进度，四个页签共用；过半时追加改课表的提示（方案 §3.13 第3条）
        """
        from Script.System.Education_System import semester_handle

        head_draw = draw.NormalDraw()
        head_draw.width = self.width
        head_draw.text = "  {0}".format(semester_handle.get_semester_head_text())
        head_draw.draw()
        # 学期中途改课表是允许的，但要让玩家知道改动只在剩下的日子里生效，别以为整个学期都算数
        if semester_handle.judge_semester_half_passed():
            tip_draw = draw.NormalDraw()
            tip_draw.width = self.width
            tip_draw.text = _("　本学期已过半，现在改课表只影响剩下的 {0} 天").format(
                semester_handle.get_semester_left_day())
            tip_draw.style = "gold_enrod"
            tip_draw.draw()
        line_feed.draw()

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
        self.now_room: str = ""
        """ 当前展示的教室场景名，空串表示尚未选择，由 draw_page 回落到第一间 """
        self.room_list: List[str] = []
        """ 本轮可排课的教室列表，每轮在 draw_page 里重算 """
        self.cell_return: Dict[str, tuple] = {}
        """ 本轮课表格子按钮的返回值 → (星期, 节次)，由 draw_page 写、handle_yrn 读 """

    def draw_page(self, return_list: List[str]):
        """
        绘制本页内容
        输入类型: return_list(List[str])，容器的共享返回值列表，本页的按钮往里加
        输出类型: 无
        功能: 教室页签 + 周表 + 排课入口。
              只画不取输入，askfor_all 由容器 Education_Manage_Panel 统一调用
        """
        # 每轮重算：教室会在游戏过程中解锁，不能在 __init__ 里快照
        self.room_list = schedule_handle.get_classroom_list()
        # 先清空派发字典再早退，否则 handle_yrn 会拿上一轮的残留去匹配
        self.cell_return = {}
        if not self.room_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n  尚未开放任何教室\n")
            info_draw.draw()
            return
        # 选中态失效（首次进入，或原教室被移除）时回落到第一间
        if self.now_room not in self.room_list:
            self.now_room = self.room_list[0]

        # 教室页签：只列已开放的。
        # constant.place_data 装的是**全部**教室（配置载入期由 data/map/ 的目录树静态构建），
        #    开放与否由 schedule_handle.get_classroom_list() 里的 judge_classroom_open 另查 facility_open
        for room in self.room_list:
            room_width = max(1, int(self.width / max(1, len(self.room_list))))
            if room == self.now_room:
                now_draw = draw.CenterDraw()
                now_draw.text = f"[{room}]"
                now_draw.style = "onbutton"
                now_draw.width = room_width
                now_draw.draw()
            else:
                # 加 ROOM_ 前缀：教室名取自场景数据，和容器页签的 return_text 同处一个列表，不加前缀留有撞名的余地
                now_draw = draw.CenterButton(f"[{room}]", f"\nROOM_{room}", room_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

        course_type = schedule_handle.get_course_type_by_classroom(self.now_room)
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  {0}｜承载课型：{1}\n").format(
            self.now_room, education_constant.COURSE_TYPE_NAME.get(course_type, _("未知")))
        info_draw.draw()

        self.cell_return = self._draw_week_table(self.now_room)
        return_list.extend(self.cell_return.keys())
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

        auto_draw = draw.CenterButton(_("[一键排满全部教室]"), _("一键排课"), int(self.width / 2))
        auto_draw.draw()
        return_list.append(auto_draw.return_text)
        clear_draw = draw.CenterButton(_("[清空本教室]"), _("清空本教室"), int(self.width / 2))
        clear_draw.draw()
        return_list.append(clear_draw.return_text)
        line_feed.draw()

    def handle_yrn(self, yrn: str):
        """
        处理本页按钮的选择结果
        输入类型: yrn(str)，容器 askfor_all 的返回值
        输出类型: 无
        功能: 切换教室 / 清空本教室 / 编辑某一格
        """
        if not self.room_list:
            return
        if yrn == _("一键排课"):
            self._auto_fill_schedule()
            return
        if yrn == _("清空本教室"):
            self._clear_room(self.now_room)
            return
        if yrn in self.cell_return:
            week_day, period = self.cell_return[yrn]
            self._edit_cell(self.now_room, week_day, period)
            return
        for room in self.room_list:
            if yrn == f"\nROOM_{room}":
                self.now_room = room
                return

    def _draw_week_table(self, classroom: str) -> Dict[str, tuple]:
        """
        绘制一间教室的周表
        输入类型: classroom(str)
        输出类型: Dict[str, tuple]，按钮返回值 → (星期, 节次)
        功能: 9 行节次 × 7 列星期，每格显示"科目/教师"；
              教师已离岗 / 被监禁 / 不在岛上的格子名字后加标注、整格灰字（Plan 31 §3.10；监禁为 Plan 32 §3.13）
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
            now_draw.text = name
            now_draw.draw()
        line_feed.draw()

        for period in range(len(game_time.CLASS_PERIOD_START)):
            head_draw = draw.NormalDraw()
            head_draw.width = head_width
            head_draw.text = "  {0} {1} ".format(period + 1, get_period_time_text(period)[:5])
            head_draw.draw()
            for week_day in range(len(education_constant.WEEK_NAME)):
                cell = schedule_handle.get_class_cell(classroom, week_day, period)
                # 格子上的教师已离岗 / 不在岛上：名字后加标注、整格灰字（Plan 31 §3.10），这一节每周都是自习，要玩家手动换人。
                #    一格只有 25 列，格子里写短标注，悬停提示写全称与后果（见 get_teacher_absent_mark 的 short）
                absent_mark = ""
                absent_tip = ""
                if cell is None:
                    cell_text = "--"
                else:
                    ability_name = game_config.config_ability[cell[0]].name
                    # 今天被临时实操课顶替的格子加「[临]」：格子上显示的是临时课，底下的每周课表还在（Plan 26 §3.6）
                    temp_class = schedule_handle.get_today_temp_class(week_day, period)
                    temp_prefix = _("[临]") if temp_class is not None and temp_class.get("classroom", "") == classroom else ""
                    if cell[1] in cache.character_data:
                        teacher_name = cache.character_data[cell[1]].name
                        absent_mark = get_teacher_absent_mark(cell[1], short=True)
                        if absent_mark:
                            absent_tip = _("{0}{1}：她来不了，这一节学生会降级为自习；点格子可改排教师").format(teacher_name, get_teacher_absent_mark(cell[1]))
                            # 名字太长时先截名字、不截标注：整格超宽时 CenterButton 从尾部截成「~」，标注会被吃掉（Plan 31 §3.10）
                            name_width = cell_width - text_handle.get_text_index(temp_prefix + ability_name + "/" + absent_mark)
                            teacher_name = fit_text_width(teacher_name, name_width)
                        cell_text = "{0}{1}/{2}{3}".format(temp_prefix, ability_name, teacher_name, absent_mark)
                    else:
                        cell_text = "{0}{1}/{2}".format(temp_prefix, ability_name, _("待定"))
                now_draw = draw.CenterButton(
                    cell_text, "\nCELL_{0}_{1}".format(week_day, period), cell_width,
                    normal_style="deep_gray" if absent_mark else "standard", tooltip=absent_tip)
                now_draw.draw()
                cell_return[now_draw.return_text] = (week_day, period)
            line_feed.draw()
        return cell_return

    def _auto_fill_schedule(self):
        """
        一键把全部已开放教室的空格子排满
        输入类型: 无
        输出类型: 无
        功能: 只填空格，已有的排课一格不动，所以重复点击是幂等的。
              排的是**全部教室**而不是当前这间——口径23立这个功能就是为了省下630格的操作量
        """
        from Script.System.Education_System import auto_schedule

        filled_count, skip_count = auto_schedule.auto_fill_class_schedule()
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.style = "gold_enrod"
        if filled_count:
            info_draw.text = _("\n已自动排课 {0} 节（周一~周五）").format(filled_count)
            if skip_count:
                info_draw.text += _("；另有 {0} 节因为当时没有空闲教师而留空").format(skip_count)
            info_draw.text += "\n"
        elif skip_count:
            info_draw.text = _("\n没能排上任何一节课：{0} 个空格子在当时都找不到空闲教师\n").format(skip_count)
        else:
            info_draw.text = _("\n课表已经排满了，没有空格子可排\n")
        info_draw.draw()

    def _clear_room(self, classroom: str):
        """
        清空一间教室的全部排课
        输入类型: classroom(str)
        输出类型: 无
        功能: 逐格调用 clear_class_cell
        """
        for week_day in range(len(education_constant.WEEK_NAME)):
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
        # -2 是「排一节性技实操课」：那是一次性的临时课程，不写全局课表（Plan 22 四期 §3.28.3）
        if ability_id == -2:
            self._edit_sex_class(classroom, week_day, period)
            return
        if ability_id == 0:
            schedule_handle.clear_class_cell(classroom, week_day, period)
            return
        teacher_id = self._select_teacher(classroom, week_day, period, ability_id)
        if teacher_id == -2:
            return
        schedule_handle.set_class_cell(classroom, week_day, period, ability_id, teacher_id)

    def _edit_sex_class(self, classroom: str, week_day: int, period: int):
        """
        排一节临时的性技实操课
        输入类型: classroom(str), week_day(int), period(int)
        输出类型: 无
        功能: 选主修科目、指定必修学生、显示会来几个人。
              临时课程是**一次性**的，键含具体日期序数，不写进 class_schedule——
                 那里的键是星期，写进去这节课会每周同一时间重演一次
        """
        from Script.System.Education_System import sex_class_handle
        from Script.System.Pregnancy_System import pregnancy_panel

        date_ordinal = sex_class_handle.get_date_ordinal_by_week_day(week_day, period)
        now_class = sex_class_handle.get_temp_class(date_ordinal, period)
        # 临时课的键不含教室：这一节若已在别的教室排了实操课，读到的就是那一条（Plan 26 §3.6，L4），
        #    确定后会改到本教室，要在页面上说清楚
        other_classroom = ""
        if now_class is not None and now_class.get("classroom", "") != classroom:
            other_classroom = now_class.get("classroom", "")
        # 新排的默认取第一门（指技），已排过的沿用原来的
        ability_id = now_class.get("ability_id", education_constant.SEX_CLASS_ABILITY_LIST[0]) if now_class else education_constant.SEX_CLASS_ABILITY_LIST[0]
        must_attend = list(now_class.get("must_attend", [])) if now_class else []

        while 1:
            draw.TitleLineDraw(_("排一节性技实操课"), self.width).draw()
            # 用游戏里的季节月名（「秋月12日」），不用日历月份——游戏时钟没有 10 月、11 月这种说法
            date_value = datetime.date.fromordinal(date_ordinal)
            date_text = pregnancy_panel.get_date_text(datetime.datetime(date_value.year, date_value.month, date_value.day))
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("  教室：{0}\n  日期：{1}（{2}）\n  节次：第{3}节 {4}\n\n").format(
                classroom, date_text, education_constant.WEEK_NAME[week_day], period + 1, get_period_time_text(period))
            info_draw.draw()
            if other_classroom:
                move_draw = draw.NormalDraw()
                move_draw.width = self.width
                move_draw.style = "gold_enrod"
                move_draw.text = _("  该节已在{0}排了实操课，确定后改到本教室\n\n").format(other_classroom)
                move_draw.draw()

            # 主修科目：只列女学生学得了的七门，76腰技是男性专属，列出来只会让人白选
            subject_draw = draw.NormalDraw()
            subject_draw.width = self.width
            subject_draw.text = _("  主修科目（这一门的相关动作有额外经验加成，其他动作照样能做）：\n")
            subject_draw.draw()
            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            for now_ability_id in education_constant.SEX_CLASS_ABILITY_LIST:
                ability_name = game_config.config_ability[now_ability_id].name
                if now_ability_id == ability_id:
                    button_text = _("[{0}]").format(ability_name)
                else:
                    button_text = _(" {0} ").format(ability_name)
                # 选中的主修科目用金色高亮。只改 normal_style，on_mouse_style 保持默认，
                # 动它会破坏全局的悬停一致性；文本上的 [x] / x 差异也保留——两者宽度刻意相等，不会跳动
                now_draw = draw.CenterButton(
                    button_text, "SUB_%d" % now_ability_id, int(self.width / 8),
                    normal_style="gold_enrod" if now_ability_id == ability_id else "standard")
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = now_ability_id
            line_feed.draw()
            line_feed.draw()

            # 这一行是必做项不是装饰：选课逻辑零改动的代价就是可能一个人都不来，
            #    玩家必须在排课当场就看得到会有几个人
            # 选修生分三份（Plan 31 §3.12）：
            #    1. 没排过性技科目教室课的（前置修习，口径 63 宽松版）：会到场，但进不了实操课
            #    2. 修过、但此刻进不了课堂的：成年学生 H 模式实行值不足，或状态异常（临盆 / 意识模糊 / 离线 / 监禁等），开课拉人时不收她们。
            #       判据与开课拉人是同一个 judge_can_join_sex_class，它只判不扣（§3.3），画这一页不改任何数据
            #    3. 其余才算「本节选修本教室的学生」，与同一页必修名单的门槛同口径
            #    点名必修的人先从三份里去掉（Plan 32 §3.8 L12）：她只列在下面的必修行。此前三份名单不对照必修名单，
            #       没修过性技理论的必修生同时列在「必修」与「不能参加（点名必修可豁免）」两行
            all_selected_list = [cid for cid in sex_class_handle.get_selected_student_list(classroom, week_day, period) if cid not in must_attend]
            course_ok_list = [cid for cid in all_selected_list if sex_class_handle.judge_has_sex_skill_course(cid)]
            # 前置修习已在上一行分出，这里传 check_course=False，只判状态与实行值
            selected_list = [cid for cid in course_ok_list if sex_class_handle.judge_can_join_sex_class(cid, check_course=False)]
            name_list = [cache.character_data[cid].name for cid in selected_list if cid in cache.character_data]
            student_draw = draw.NormalDraw()
            student_draw.width = self.width
            if selected_list:
                student_draw.text = _("  本节选修本教室的学生：{0} 人（{1}）\n").format(
                    len(selected_list), "、".join(name_list))
            elif all_selected_list:
                # 有人选了这一节、但一个都进不了课堂：不能再写「没有学生会来」，下面的行会写她们照样到场
                student_draw.text = _("  本节选修本教室的学生：0 人 —— 选修的人都进不了课堂（见下），建议指定必修学生\n")
            elif must_attend:
                # 选修的人都已被点名、或只有点名的人会来（Plan 32 §3.8 L12）：必修行写着谁会来，不能再写「没有学生会来」
                student_draw.text = _("  本节选修本教室的学生：0 人（点名必修的学生照常会来，见下）\n")
            else:
                student_draw.text = _("  本节选修本教室的学生：0 人 —— 没有学生会来，建议指定必修学生\n")
            student_draw.draw()
            blocked_name_list = [cache.character_data[cid].name for cid in course_ok_list if cid not in selected_list and cid in cache.character_data]
            # 点名必修只豁免前置修习：状态与成年学生的实行值开课拉人时照判（check_course=False），
            #    点名之后才被监禁、意识模糊或实行值跌破的必修生，同样列进这一行（实施复审补）
            blocked_name_list += [cache.character_data[cid].name for cid in must_attend
                                  if cid in cache.character_data and not sex_class_handle.judge_can_join_sex_class(cid, check_course=False)]
            if blocked_name_list:
                blocked_draw = draw.NormalDraw()
                blocked_draw.width = self.width
                blocked_draw.style = "deep_gray"
                blocked_draw.text = _("  另有 {0} 人会到场，但此刻进不了课堂（实行值不足或状态异常）：{1}\n").format(
                    len(blocked_name_list), "、".join(blocked_name_list))
                blocked_draw.draw()
            no_course_name_list = [cache.character_data[cid].name for cid in all_selected_list if cid not in course_ok_list and cid in cache.character_data]
            if no_course_name_list:
                no_course_draw = draw.NormalDraw()
                no_course_draw.width = self.width
                no_course_draw.style = "deep_gray"
                no_course_draw.text = _("  另有 {0} 人会到场但没修过性技科目的课，不能参加（点名必修可豁免）：{1}\n").format(
                    len(no_course_name_list), "、".join(no_course_name_list))
                no_course_draw.draw()

            must_name_list = [cache.character_data[cid].name for cid in must_attend if cid in cache.character_data]
            must_draw = draw.NormalDraw()
            must_draw.width = self.width
            must_draw.text = _("  必修（无论原本排了什么都来，且不会翘课）：{0}\n\n").format(
                "、".join(must_name_list) if must_name_list else _("无"))
            must_draw.draw()

            add_draw = draw.CenterButton(_("[指定必修学生]"), "ADD_MUST", int(self.width / 3))
            add_draw.draw()
            return_list.append(add_draw.return_text)
            ok_draw = draw.CenterButton(_("[确定]"), "OK", int(self.width / 3))
            ok_draw.draw()
            return_list.append(ok_draw.return_text)
            line_feed.draw()
            if now_class is not None:
                del_draw = draw.CenterButton(_("[删除本节临时课]"), "DEL", int(self.width / 3))
                del_draw.draw()
                return_list.append(del_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), "BACK", int(self.width / 3))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            if now_class is not None and yrn == del_draw.return_text:
                sex_class_handle.del_temp_class(date_ordinal, period)
                return
            if yrn == ok_draw.return_text:
                sex_class_handle.set_temp_class(
                    date_ordinal, period, classroom, ability_id, must_attend=must_attend)
                return
            if yrn == add_draw.return_text:
                must_attend = self._select_must_attend(must_attend, classroom, week_day, period)
                continue
            if yrn in id_by_return:
                ability_id = id_by_return[yrn]

    def _select_must_attend(self, must_attend: List[int], classroom: str, week_day: int, period: int) -> List[int]:
        """
        指定必修这节实操课的学生
        输入类型: must_attend(List[int]) 当前名单, classroom(str), week_day(int), period(int)
        输出类型: List[int]，新的名单
        功能: 列出可参加的学生，每行6个，点一下切换选中状态。
              会顶掉一节确有的课的学生名字后标「*」，具体顶掉哪一节集中列在下方——
                 一个格位只有31列，「（将顶替 X 的 Y）」这种尾注放不下。
              确有的课不分课型（Plan 28 §3.5）：体育 / 兴趣 / 实习课一样会被顶掉；已停课的教室课、上不成的个人式课不算
        """
        from Script.System.Education_System import sex_class_handle, growth_handle
        from Script.UI.Panel import character_info_head

        must_attend = list(must_attend)
        while 1:
            draw.TitleLineDraw(_("指定必修学生"), self.width).draw()
            tip_draw = draw.NormalDraw()
            tip_draw.width = self.width
            tip_draw.text = _("  被点名的学生无论原本排了什么课都会来，且不会翘课。名字前的√为已选中。\n")
            tip_draw.draw()

            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            replace_text_list = []
            # 人口来源：职业为学生的全部干员，含成年学生（Plan 25 §3.7），与个人课表名单同口径——
            #    课表只对学生岗生效（Plan 24 口径 1），改了岗的女儿点了名也不会来上课。
            # judge_can_join_sex_class 保留作状态守卫（死亡/临盆/意识模糊/监禁等）；成年学生仍须满足 H 模式实行值（口径 63 第二层），
            #    否则必修名单就成了绕开全部 H 前提的旁路
            student_width = int(self.width / 6)
            count = 0
            for character_id in growth_handle.get_course_candidate_list():
                character_data: game_type.Character = cache.character_data[character_id]
                # 必修名单豁免前置修习（口径 63 宽松版）：点名本身就是玩家的决定，这里只做状态守卫
                if not sex_class_handle.judge_can_join_sex_class(character_id, check_course=False):
                    continue
                mark = "√" if character_id in must_attend else "  "
                # 会顶掉她原本的哪一节——按钮里只放一个「*」，明细汇总到下方。
                #    只标确有的课（Plan 28 §3.5）：必修覆盖顶掉的是这一节的任何课，体育 / 兴趣 / 实习课也一样；
                #    每周课表上已停课的教室课、上不成的个人式课本来就算没课，不标。
                #    个人式课不看书库此刻借没借空（Plan 30 §3.7）：顶掉的是排在某一天的那节课，那天借不借得到书排课时不知道
                old_course = schedule_handle.get_selected_course(character_id, week_day, period)
                replace_text = ""
                if old_course is not None and old_course[0] in education_constant.CLASSROOM_COURSE_TYPE_SET:
                    # 顶替的是她每周固定的那节课，不叠加临时课覆盖层（否则今天这格读到的就是临时课自己）
                    old_cell = schedule_handle.get_class_cell(old_course[1], week_day, period, include_temp=False)
                    if old_cell is not None and old_cell[0] in game_config.config_ability:
                        replace_text = _("{0}→{1}的{2}").format(character_data.name, old_course[1], game_config.config_ability[old_cell[0]].name)
                    elif old_cell is not None:
                        replace_text = _("{0}→{1}").format(character_data.name, old_course[1])
                elif old_course is not None:
                    old_course_data = {"course_type": old_course[0], "target": old_course[1]}
                    if schedule_handle.judge_personal_course_real(character_id, old_course_data):
                        replace_text = _("{0}→{1}").format(character_data.name, character_info_head.get_course_text(old_course_data))
                replace_mark = "*" if replace_text else ""
                if replace_text:
                    replace_text_list.append(replace_text)
                now_draw = draw.LeftButton(
                    _("[{0}{1}{2}]").format(mark, character_data.name, replace_mark),
                    "MUST_%d" % character_id, student_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = character_id
                count += 1
                if count % 6 == 0:
                    line_feed.draw()
            if count % 6:
                line_feed.draw()
            if not count:
                empty_draw = draw.NormalDraw()
                empty_draw.width = self.width
                empty_draw.text = _("\n  目前没有可参加的学生\n")
                empty_draw.draw()

            if replace_text_list:
                replace_draw = draw.NormalDraw()
                replace_draw.width = self.width
                replace_draw.style = "deep_gray"
                replace_draw.text = _("  *会顶替原本的课：{0}\n").format("、".join(replace_text_list))
                replace_draw.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[完成]"), "DONE", int(self.width / 3))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return must_attend
            if yrn in id_by_return:
                character_id = id_by_return[yrn]
                if character_id in must_attend:
                    must_attend.remove(character_id)
                else:
                    must_attend.append(character_id)

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
            classroom, education_constant.WEEK_NAME[week_day], period + 1, get_period_time_text(period))
        info_draw.draw()
        # 今天这一格被临时实操课顶替（Plan 26 §3.6）：格子上看到的是临时课，这一页改的、清的却是底下每周循环的那节，要写清楚
        temp_class = schedule_handle.get_today_temp_class(week_day, period)
        overlay_flag = temp_class is not None and temp_class.get("classroom", "") == classroom
        if overlay_flag:
            from Script.System.Education_System import sex_class_handle

            week_cell = schedule_handle.get_class_cell(classroom, week_day, period, include_temp=False)
            if week_cell is None:
                week_text = _("未排课")
            elif week_cell[1] in cache.character_data:
                # 教师已离岗 / 不在岛上的标注与周表格子一致（Plan 31 §3.10）
                week_text = "{0}/{1}{2}".format(
                    game_config.config_ability[week_cell[0]].name, cache.character_data[week_cell[1]].name, get_teacher_absent_mark(week_cell[1]))
            else:
                week_text = "{0}/{1}".format(game_config.config_ability[week_cell[0]].name, _("待定"))
            overlay_draw = draw.NormalDraw()
            overlay_draw.width = self.width
            overlay_draw.style = "gold_enrod"
            overlay_draw.text = _("  今天这一节由临时实操课（主修{0}）顶替；每周课表这一格：{1}\n  下面选科目、清空改的都是每周课表这一格；临时课请从「排一节性技实操课」进去修改或删除\n").format(
                sex_class_handle.get_ability_name(temp_class.get("ability_id", -1)), week_text)
            overlay_draw.draw()
        line_feed.draw()

        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        for index, ability_id in enumerate(education_constant.SUBJECT_ABILITY_LIST):
            now_draw = draw.LeftButton(
                _("[{0}]{1}").format(index, game_config.config_ability[ability_id].name),
                str(index), int(self.width / 4))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = ability_id
            if index % 4 == 3:
                line_feed.draw()
        line_feed.draw()
        # 性技实操课只在实践教室与大礼堂开（方案 §3.28.2），别的教室不列这个入口
        sex_class_draw = None
        if schedule_handle.get_course_type_by_classroom(classroom) in (
                education_constant.COURSE_TYPE_PRACTICE, education_constant.COURSE_TYPE_PUBLIC):
            sex_class_draw = draw.CenterButton(
                _("[排一节性技实操课]"), _("排一节性技实操课"), int(self.width / 2))
            sex_class_draw.draw()
            return_list.append(sex_class_draw.return_text)
            line_feed.draw()
        line_feed.draw()
        back_draw = draw.CenterButton(_("[取消]"), _("取消"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        # 被临时课顶替的格子，按钮文字写明清的是每周课表那一格；返回值哨兵不变
        clear_text = _("[清空每周课表这一格]") if overlay_flag else _("[清空本格]")
        clear_draw = draw.CenterButton(clear_text, _("清空本格"), int(self.width / 2))
        clear_draw.draw()
        return_list.append(clear_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn == back_draw.return_text:
            return -1
        if sex_class_draw is not None and yrn == sex_class_draw.return_text:
            return -2
        if yrn == clear_draw.return_text:
            return 0
        return id_by_return.get(yrn, -1)

    def _select_teacher(self, classroom: str, week_day: int, period: int, ability_id: int) -> int:
        """
        选教师
        输入类型: classroom(str), week_day(int), period(int), ability_id(int) 本节要教的科目
        输出类型: int，教师角色id；-1为本节不排教师（学生自习），-2为取消
        功能: 只列教师岗干员，每行6个，名字后跟该科目的等级；默认按等级降序，可切升序。
              撞课的置灰并标"第N节已在X教室"
        """
        sort_desc = True
        """ 是否按该科目等级降序排。玩家找的通常是「谁教这门最好」，所以默认降序 """
        ability_name = game_config.config_ability[ability_id].name if ability_id in game_config.config_ability else _("该科目")

        while 1:
            draw.TitleLineDraw(_("选择授课教师"), self.width).draw()
            tip_draw = draw.NormalDraw()
            tip_draw.width = self.width
            tip_draw.text = _("  名字后是该教师的{0}等级与本周已排的节数；灰色的是本节已在别处上课的。\n").format(ability_name)
            tip_draw.draw()

            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            sort_draw = draw.CenterButton(
                _("[按{0}等级↓]").format(ability_name) if sort_desc else _("[按{0}等级↑]").format(ability_name),
                "SORT_TEACHER", int(self.width / 3))
            sort_draw.draw()
            return_list.append(sort_draw.return_text)
            line_feed.draw()
            draw.LineDraw("-", self.width).draw()

            # ability 的值可能是 float，一律套 int() 再比较与显示
            teacher_list = sorted(
                schedule_handle.get_teacher_candidate_list(),
                key=lambda cid: (int(cache.character_data[cid].ability.get(ability_id, 0)), -cid),
                reverse=sort_desc)
            # 每行6个：190/6=31列，6×31=186≤190
            teacher_width = int(self.width / 6)
            count = 0
            for teacher_id in teacher_list:
                teacher_data: game_type.Character = cache.character_data[teacher_id]
                level = int(teacher_data.ability.get(ability_id, 0))
                # 本周已排节数：反查全局课表数出来，让玩家一眼看出谁已经被排满了。
                # 不能只看本节冲不冲——不冲突的老师里也有已经排了三十节的
                week_load = sum(len(one) for one in schedule_handle.get_teacher_week_schedule(teacher_id).values())
                level_text = "{0}{1}/{2}节".format(attr_calculation.judge_grade(level), level, week_load)
                conflict = schedule_handle.judge_teacher_conflict(teacher_id, week_day, period, classroom)
                if conflict:
                    # 撞课的不做成按钮，但仍占一个格位，否则整行网格会左移错位。
                    # 具体撞在哪一节写在按钮上放不下，缩成「※」，完整冲突信息在下方汇总
                    now_draw = draw.LeftDraw()
                    now_draw.width = teacher_width
                    now_draw.style = "deep_gray"
                    now_draw.text = _(" {0} {1}※").format(teacher_data.name, level_text)
                    now_draw.draw()
                else:
                    now_draw = draw.LeftButton(
                        _("[{0} {1}]").format(teacher_data.name, level_text),
                        str(teacher_id), teacher_width)
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
                    id_by_return[now_draw.return_text] = teacher_id
                count += 1
                if count % 6 == 0:
                    line_feed.draw()
            if count % 6:
                line_feed.draw()

            # 撞课的教师逐个说明撞在哪——按钮格位里塞不下，集中放在列表下方
            conflict_text_list = []
            for teacher_id in teacher_list:
                conflict = schedule_handle.judge_teacher_conflict(teacher_id, week_day, period, classroom)
                if conflict:
                    conflict_text_list.append("{0}（{1}）".format(cache.character_data[teacher_id].name, conflict))
            if conflict_text_list:
                conflict_draw = draw.NormalDraw()
                conflict_draw.width = self.width
                conflict_draw.style = "deep_gray"
                conflict_draw.text = _("  ※本节已有课：{0}\n").format("、".join(conflict_text_list))
                conflict_draw.draw()
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
            if yrn == sort_draw.return_text:
                sort_desc = not sort_desc
                continue
            return id_by_return.get(yrn, -2)
