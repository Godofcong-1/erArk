"""全局课表面板（Plan 22 一期 §5.2）与教育管理系统的页签容器

⚠️ 课表是「10 教室 × 7 天 × 9 节」的三维数据，一次全画必然超出终端宽度。
   本面板一次只展示**一间教室**的周表（7 天 × 9 节），教室用上方的横向标签页切换——
   降一个维度之后 Tk 与 Web 都画得下（方案 §5.2）。

⚠️ 只用 Script/UI/Moudle/draw.py 的抽象绘制类，不直接碰 Tk 或 HTML；
   Web_Draw_System/web_draw_adapter.py 在启动时包装这些抽象类，双模式才能同时成立。
"""
import datetime
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Config import game_config, normal_config
from Script.Design import game_time, attr_calculation, basement
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
        # ⚠️ 这三个模块在自己的模块顶层反向 import 本模块（取 WEEK_NAME 等共用常量），
        #    所以只能在函数内 import，提到文件顶层会循环导入
        from Script.System.Education_System import course_select_panel, growth_panel, schedule_template_panel

        self.width: int = width
        self.now_panel: str = _("全局课表")
        self.panel_list: List[str] = [_("全局课表"), _("个人课表"), _("日程模板"), _("养成总览")]
        """ 四个页签的显示名，同时也是 panel_map 的键 """
        # ⚠️ 子面板实例只创建一次并存起来：容器每轮 while 都会重画，
        #    如果每轮 new 一个，子面板里的选中态（当前教室 / 当前孩子）必然被重置
        self.panel_map: Dict[str, object] = {
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
              ⚠️ 全面板**只有这一处** askfor_all：子面板只负责往共享的 return_list 里加按钮、
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
            for now_panel in self.panel_list:
                panel_width = int(self.width / len(self.panel_list))
                if now_panel == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{now_panel}]"
                    now_draw.style = "onbutton"
                    now_draw.width = panel_width
                    now_draw.draw()
                else:
                    # ⚠️ 这里不能用 cmd_func：askfor_all 是先执行 cmd_func 再 return，
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
              ⚠️ 只画不取输入，askfor_all 由容器 Education_Manage_Panel 统一调用
        """
        # 每轮重算：教室会在游戏过程中解锁，不能在 __init__ 里快照
        self.room_list = schedule_handle.get_classroom_list()
        # ⚠️ 先清空派发字典再早退，否则 handle_yrn 会拿上一轮的残留去匹配
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
        # ⚠️ constant.place_data 装的是**全部**教室（配置载入期由 data/map/ 的目录树静态构建），
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
                # ⚠️ 加 ROOM_ 前缀：教室名取自场景数据，和容器页签的 return_text 同处一个列表，不加前缀留有撞名的余地
                now_draw = draw.CenterButton(f"[{room}]", f"\nROOM_{room}", room_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
        line_feed.draw()
        draw.LineDraw("-", self.width).draw()

        course_type = schedule_handle.get_course_type_by_classroom(self.now_room)
        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("  {0}｜承载课型：{1}\n").format(
            self.now_room, schedule_handle.COURSE_TYPE_NAME.get(course_type, _("未知")))
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

    def _auto_fill_schedule(self):
        """
        一键把全部已开放教室的空格子排满
        输入类型: 无
        输出类型: 无
        功能: 只填空格，已有的排课一格不动，所以重复点击是幂等的。
              ⚠️ 排的是**全部教室**而不是当前这间——口径23立这个功能就是为了省下630格的操作量
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
              ⚠️ 临时课程是**一次性**的，键含具体日期序数，不写进 class_schedule——
                 那里的键是星期，写进去这节课会每周同一时间重演一次
        """
        from Script.System.Education_System import sex_class_handle

        date_ordinal = sex_class_handle.get_date_ordinal_by_week_day(week_day, period)
        now_class = sex_class_handle.get_temp_class(date_ordinal, period)
        # 新排的默认取第一门（指技），已排过的沿用原来的
        ability_id = now_class.get("ability_id", sex_class_handle.SEX_CLASS_ABILITY_LIST[0]) if now_class else sex_class_handle.SEX_CLASS_ABILITY_LIST[0]
        must_attend = list(now_class.get("must_attend", [])) if now_class else []

        while 1:
            draw.TitleLineDraw(_("排一节性技实操课"), self.width).draw()
            date_text = datetime.date.fromordinal(date_ordinal).strftime("%m月%d日")
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("  教室：{0}\n  日期：{1}（{2}）\n  节次：第{3}节 {4}\n\n").format(
                classroom, date_text, _(WEEK_NAME[week_day]), period + 1, get_period_time_text(period))
            info_draw.draw()

            # 主修科目：只列女学生学得了的七门，76腰技是男性专属，列出来只会让人白选
            subject_draw = draw.NormalDraw()
            subject_draw.width = self.width
            subject_draw.text = _("  主修科目（这一门的相关动作有额外经验加成，其他动作照样能做）：\n")
            subject_draw.draw()
            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            for now_ability_id in sex_class_handle.SEX_CLASS_ABILITY_LIST:
                ability_name = game_config.config_ability[now_ability_id].name
                if now_ability_id == ability_id:
                    button_text = _("[{0}]").format(ability_name)
                else:
                    button_text = _(" {0} ").format(ability_name)
                # 选中的主修科目用金色高亮。⚠️ 只改 normal_style，on_mouse_style 保持默认，
                # 动它会破坏全局的悬停一致性；文本上的 [x] / x 差异也保留——两者宽度刻意相等，不会跳动
                now_draw = draw.CenterButton(
                    button_text, "SUB_%d" % now_ability_id, int(self.width / 8),
                    normal_style="gold_enrod" if now_ability_id == ability_id else "standard")
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = now_ability_id
            line_feed.draw()
            line_feed.draw()

            # ⚠️ 这一行是必做项不是装饰：选课逻辑零改动的代价就是可能一个人都不来，
            #    玩家必须在排课当场就看得到会有几个人
            selected_list = sex_class_handle.get_selected_student_list(classroom, week_day, period)
            name_list = [cache.character_data[cid].name for cid in selected_list if cid in cache.character_data]
            student_draw = draw.NormalDraw()
            student_draw.width = self.width
            if selected_list:
                student_draw.text = _("  本节选修本教室的学生：{0} 人（{1}）\n").format(
                    len(selected_list), "、".join(name_list))
            else:
                student_draw.text = _("  本节选修本教室的学生：0 人 —— 没有学生会来，建议指定必修学生\n")
            student_draw.draw()

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
              ⚠️ 会顶掉原有课的学生名字后标「*」，具体顶掉哪一节集中列在下方——
                 一个格位只有31列，「（将顶替 X 的 Y）」这种尾注放不下
        """
        from Script.System.Education_System import sex_class_handle, growth_handle

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
            # 人口来源与个人课表、养成总览共用一份口径：玩家的女儿且处于幼女/萝莉/少女阶段。
            # judge_can_join_sex_class 保留作状态守卫（死亡/临盆/意识模糊/监禁等）
            student_width = int(self.width / 6)
            count = 0
            for character_id in growth_handle.get_student_candidate_list():
                if not sex_class_handle.judge_can_join_sex_class(character_id):
                    continue
                character_data: game_type.Character = cache.character_data[character_id]
                mark = "√" if character_id in must_attend else "  "
                # 会顶掉她原本的哪一节——按钮里只放一个「*」，明细汇总到下方
                old_course = schedule_handle.get_selected_course(character_id, week_day, period)
                replace_mark = ""
                if old_course is not None and old_course[0] in schedule_handle.CLASSROOM_COURSE_TYPE_SET:
                    replace_mark = "*"
                    old_cell = schedule_handle.get_class_cell(old_course[1], week_day, period)
                    if old_cell is not None and old_cell[0] in game_config.config_ability:
                        replace_text_list.append(_("{0}→{1}的{2}").format(
                            character_data.name, old_course[1],
                            game_config.config_ability[old_cell[0]].name))
                    else:
                        replace_text_list.append(_("{0}→{1}").format(character_data.name, old_course[1]))
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
        # 性技实操课只在实践教室与大礼堂开（方案 §3.28.2），别的教室不列这个入口
        sex_class_draw = None
        if schedule_handle.get_course_type_by_classroom(classroom) in (
                schedule_handle.COURSE_TYPE_PRACTICE, schedule_handle.COURSE_TYPE_PUBLIC):
            sex_class_draw = draw.CenterButton(
                _("[排一节性技实操课]"), _("排一节性技实操课"), int(self.width / 2))
            sex_class_draw.draw()
            return_list.append(sex_class_draw.return_text)
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
            tip_draw.text = _("  名字后是该教师的{0}等级；灰色的是本节已在别处上课的。\n").format(ability_name)
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

            # ⚠️ ability 的值可能是 float，一律套 int() 再比较与显示
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
                level_text = "{0}{1}".format(attr_calculation.judge_grade(level), level)
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
