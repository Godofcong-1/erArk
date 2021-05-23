from types import FunctionType
from typing import List
from Script.Core import cache_control, game_type, get_text, flow_handle, py_cmd, constant
from Script.Design import attr_text, character_move, course
from Script.Config import game_config
from Script.UI.Moudle import panel, draw


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


# class SchoolTimeTablePanel:
#     """
#     用于查看课程表界面面板对象
#     Keyword arguments:
#     width -- 绘制宽度
#     """

#     def __init__(self, width: int):
#         """初始化绘制对象"""
#         self.width: int = width
#         """ 绘制的最大宽度 """

#     def draw(self):
#         """绘制对象"""
#         character_data: game_type.Character = cache.character_data[0]
#         if character_data.age <= 18:
#             now_draw = StudentTimeTablePanel(self.width)
#             now_draw.draw()
#         else:
#             if 0 in cache.teacher_school_timetable:
#                 now_draw = TeacherTimeTablePanel(self.width)
#                 now_draw.draw()
#             else:
#                 title_draw = draw.TitleLineDraw(_("课程表"), self.width)
#                 title_draw.draw()
#                 now_draw = draw.WaitDraw()
#                 now_draw.width = self.width
#                 now_draw.text = _("无课时安排")
#                 now_draw.draw()
#                 cache.now_panel_id = constant.Panel.IN_SCENE


# class StudentTimeTablePanel:
#     """
#     学生查看课程表界面面板对象
#     Keyword arguments:
#     width -- 绘制宽度
#     """

#     def __init__(self, width: int):
#         """初始化绘制对象"""
#         self.width: int = width
#         """ 绘制的最大宽度 """
#         self.now_week: int = cache.game_time.weekday()
#         """ 当前星期 """

#     def draw(self):
#         """绘制对象"""
#         school_id, phase = course.get_character_school_phase(0)
#         time_table = cache.course_time_table_data[school_id][phase]
#         weekday_text_list = [game_config.config_week_day[i].name for i in game_config.config_week_day]
#         character_data: game_type.Character = cache.character_data[0]
#         now_time_value = cache.game_time.hour * 100 + cache.game_time.minute
#         while 1:
#             now_week_text = game_config.config_week_day[self.now_week].name
#             title_draw = draw.TitleLineDraw(_("课程表"), self.width)
#             title_draw.draw()
#             index = 0
#             return_list = []
#             for week_text in weekday_text_list:
#                 if week_text == now_week_text:
#                     if index == cache.game_time.weekday():
#                         week_text = week_text + _("(今日)")
#                     now_draw = draw.CenterDraw()
#                     now_draw.text = f"[{week_text}]"

#                     now_draw.style = "onbutton"
#                     now_draw.width = self.width / len(weekday_text_list)
#                     now_draw.draw()
#                 else:
#                     if index == cache.game_time.weekday():
#                         week_text = week_text + _("(今日)")
#                     now_draw = draw.CenterButton(
#                         f"[{week_text}]",
#                         week_text,
#                         self.width / len(weekday_text_list),
#                         cmd_func=self.change_now_week,
#                         args=(index,),
#                     )
#                     now_draw.draw()
#                     return_list.append(now_draw.return_text)
#                 index += 1
#             line_feed.draw()
#             line = draw.LineDraw("+", self.width)
#             line.draw()
#             title_list = [_("课时"), _("科目"), _("教师"), _("上课时间"), _("下课时间")]
#             title_list_draw = panel.CenterDrawTextListPanel()
#             title_list_draw.set(title_list, self.width, 5)
#             title_list_draw.draw()
#             now_text_list = []
#             times_judge = 1
#             if self.now_week not in time_table:
#                 now_text_list.append(_("休息日"))
#             else:
#                 for times in range(0, len(time_table[self.now_week]) + 1):
#                     course_time_id = game_config.config_school_session_data[school_id][times]
#                     course_time_config = game_config.config_school_session[course_time_id]
#                     course_time = str(course_time_config.start_time)
#                     minute = course_time[-2:]
#                     hour = course_time[:-2]
#                     course_time_text = f"{hour}:{minute}"
#                     course_end_time = str(course_time_config.end_time)
#                     end_minute = course_end_time[-2:]
#                     end_hour = course_end_time[:-2]
#                     course_end_time_text = f"{end_hour}:{end_minute}"
#                     now_time_judge = 0
#                     if times_judge:
#                         if self.now_week == cache.game_time.weekday():
#                             if now_time_value < course_time_config.end_time:
#                                 now_time_judge = 1
#                                 times_judge = 0
#                     if not times:
#                         now_class_text = _("早读课")
#                         if now_time_judge:
#                             now_class_text += _("(当前)")
#                         now_text = [now_class_text, "", "", course_time_text, course_end_time_text]
#                         now_text_list.append(now_text)
#                         continue
#                     cache.class_timetable_teacher_data.setdefault(school_id, {})
#                     cache.class_timetable_teacher_data[school_id].setdefault(phase, {})
#                     cache.class_timetable_teacher_data[school_id][phase].setdefault(
#                         character_data.classroom, {}
#                     )
#                     cache.class_timetable_teacher_data[school_id][phase][
#                         character_data.classroom
#                     ].setdefault(self.now_week, {})
#                     course_id = time_table[self.now_week][times]
#                     course_config = game_config.config_course[course_id]
#                     course_name = course_config.name
#                     times_text = _("第{times}节").format(times=times)
#                     if now_time_judge:
#                         times_text += _("(当前)")
#                     if (
#                         times
#                         in cache.class_timetable_teacher_data[school_id][phase][character_data.classroom][
#                             self.now_week
#                         ]
#                     ):
#                         teacher_id = cache.class_timetable_teacher_data[school_id][phase][
#                             character_data.classroom
#                         ][self.now_week][times]
#                         teacher_data: game_type.Character = cache.character_data[teacher_id]
#                         teacher_name = teacher_data.name
#                         now_text = [
#                             times_text,
#                             course_name,
#                             teacher_name,
#                             course_time_text,
#                             course_end_time_text,
#                         ]
#                     else:
#                         now_text = [
#                             times_text,
#                             course_name,
#                             _("自习"),
#                             course_time_text,
#                             course_end_time_text,
#                         ]
#                     now_text_list.append(now_text)
#             for now_text in now_text_list:
#                 now_draw = panel.LeftDrawTextListPanel()
#                 now_draw.set(now_text, self.width, 5)
#                 now_draw.draw()
#             line_draw = draw.LineDraw("-", self.width)
#             line_draw.draw()
#             back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
#             back_draw.draw()
#             line_feed.draw()
#             return_list.append(back_draw.return_text)
#             yrn = flow_handle.askfor_all(return_list)
#             if yrn == back_draw.return_text:
#                 cache.now_panel_id = constant.Panel.IN_SCENE
#                 break

#     def change_now_week(self, week: int):
#         """
#         切换当前面板显示的星期类型
#         Keyword arguments:
#         week -- 切换的星期
#         """
#         self.now_week = week


# class TeacherTimeTablePanel:
#     """
#     教师查看课程表界面面板对象
#     Keyword arguments:
#     width -- 绘制宽度
#     """

#     def __init__(self, width: int):
#         """初始化绘制对象"""
#         self.width: int = width
#         """ 绘制的最大宽度 """

#     def draw(self):
#         """绘制对象"""
#         timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[0]
#         text_list = []
#         args_list = []
#         line_feed.draw()
#         title_draw = draw.TitleLineDraw(_("课程表"), self.width)
#         title_draw.draw()
#         for timetable in timetable_list:
#             class_name = attr_text.get_scene_path_text(timetable.class_room)
#             now_time = str(timetable.time)
#             minute = now_time[-2:]
#             hour = now_time[:-2]
#             now_time_text = f"{hour}:{minute}"
#             now_text = _("{weekday} 第{times}节 班级:{class_name} 科目:{course} 上课时间:{time}").format(
#                 weekday=game_config.config_week_day[timetable.week_day].name,
#                 times=timetable.class_times,
#                 class_name=class_name,
#                 course=game_config.config_course[timetable.course].name,
#                 time=now_time_text,
#             )
#             text_list.append(now_text)
#             args_list.append(timetable.class_room)
#         now_draw = panel.LeftDrawIDButtonListPanel()
#         now_draw.set(text_list, 0, self.width, 1, "", self.move_now, args_list)
#         now_draw.draw()
#         line_draw = draw.LineDraw("-", self.width)
#         line_draw.draw()
#         back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
#         back_draw.draw()
#         line_feed.draw()
#         return_list = now_draw.return_list
#         return_list.append(back_draw.return_text)
#         yrn = flow_handle.askfor_all(return_list)
#         if yrn == back_draw.return_text:
#             cache.now_panel_id = constant.Panel.IN_SCENE

#     def move_now(self, move_path: List[str]):
#         """
#         移动到指定教室
#         Keyword arguments:
#         move_path -- 教室位置
#         """
#         py_cmd.clr_cmd()
#         line_feed.draw()
#         cache.wframe_mouse.w_frame_skip_wait_mouse = 1
#         character_move.own_charcter_move(move_path)
