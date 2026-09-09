# -*- coding: UTF-8 -*-
"""auto_schedule：一键排课与一键选课"""
from _bootstrap import *  # noqa: F401,F403

open_all_classroom()
clear_schedules()
room_list = schedule_handle.get_classroom_list()
period_count = len(game_time.CLASS_PERIOD_START)

section("科目与教室的适配")
check("自动排课科目 = 女儿学得了的 17 门", auto_schedule.get_auto_subject_list() == education_constant.FEMALE_SUBJECT_LIST
      and 76 not in auto_schedule.get_auto_subject_list())
check("返回的是副本", auto_schedule.get_auto_subject_list() is not education_constant.FEMALE_SUBJECT_LIST)
check("实践教室只收动手类与性技", auto_schedule.judge_subject_fit_classroom(42, education_constant.COURSE_TYPE_PRACTICE)
      and auto_schedule.judge_subject_fit_classroom(70, education_constant.COURSE_TYPE_PRACTICE)
      and not auto_schedule.judge_subject_fit_classroom(40, education_constant.COURSE_TYPE_PRACTICE))
check("理论与公开课来者不拒", auto_schedule.judge_subject_fit_classroom(40, education_constant.COURSE_TYPE_THEORY)
      and auto_schedule.judge_subject_fit_classroom(40, education_constant.COURSE_TYPE_PUBLIC))

section("没有教师 / 没有教室")
check("没有教师时 (0, 0)", auto_schedule.auto_fill_class_schedule() == (0, 0))
teacher_a = make_character(101, "教师甲", 151)
teacher_b = make_character(102, "教师乙", 151)
teacher_c = make_character(103, "教师丙", 151)
teacher_a.ability[45] = 5
teacher_b.ability[45] = 5
teacher_c.ability[43] = 7

section("最优教师")
check("等级最高者胜出", auto_schedule.pick_best_teacher(43, 0, 0, room_list[0], [101, 102, 103]) == 103)
check("并列取 id 小者", auto_schedule.pick_best_teacher(45, 0, 0, room_list[0], [101, 102, 103]) == 101)
schedule_handle.set_class_cell(room_list[1], 0, 0, 45, 101)
check("撞课的教师被跳过", auto_schedule.pick_best_teacher(45, 0, 0, room_list[0], [101, 102, 103]) == 102)
check("全撞课时 -1", auto_schedule.pick_best_teacher(45, 0, 0, room_list[0], [101]) == -1)
clear_schedules()

section("一键排课")
filled, skipped = auto_schedule.auto_fill_class_schedule()
check("排上了课", filled > 0, (filled, skipped))
weekend_cells = [schedule_handle.get_class_cell(room, day, p) for room in room_list for day in (5, 6) for p in range(period_count)]
check("周末一格不排", all(cell is None for cell in weekend_cells))
weekday_total = 10 * education_constant.AUTO_SCHEDULE_WEEK_DAY_MAX * period_count
check("排上 + 留空 = 工作日全部格数", filled + skipped == weekday_total, (filled, skipped, weekday_total))
# 三个教师同一节最多教三间教室：每个节次最多 3 格有课
conflict_ok = True
for day in range(5):
    for p in range(period_count):
        teacher_used = [schedule_handle.get_class_cell(room, day, p)[1] for room in room_list if schedule_handle.get_class_cell(room, day, p) is not None]
        if len(teacher_used) != len(set(teacher_used)):
            conflict_ok = False
check("同一节次没有教师被排进两间教室", conflict_ok)
practice_ok = all(
    auto_schedule.judge_subject_fit_classroom(schedule_handle.get_class_cell(room, day, p)[0], education_constant.COURSE_TYPE_PRACTICE)
    for room in schedule_handle.get_classroom_list(education_constant.COURSE_TYPE_PRACTICE)
    for day in range(5) for p in range(period_count) if schedule_handle.get_class_cell(room, day, p) is not None)
check("实践教室里只有动手类与性技", practice_ok)
check("没排上 76 腰技", not any(schedule_handle.get_class_cell(room, day, p) is not None and schedule_handle.get_class_cell(room, day, p)[0] == 76
                          for room in room_list for day in range(5) for p in range(period_count)))
snapshot = {room: {d: dict(v) for d, v in week.items()} for room, week in cache.rhodes_island.class_schedule.items()}
check("重复点击幂等", auto_schedule.auto_fill_class_schedule() == (0, skipped))
check("幂等后课表未变", cache.rhodes_island.class_schedule == snapshot)
clear_schedules()
auto_schedule.auto_fill_class_schedule()
check("结果可复现", cache.rhodes_island.class_schedule == snapshot)
# 手排的格子不被动
clear_schedules()
schedule_handle.set_class_cell(room_list[0], 0, 0, 40, 102)
auto_schedule.auto_fill_class_schedule()
check("手排的格子一格不动", schedule_handle.get_class_cell(room_list[0], 0, 0) == [40, 102])

section("一键选课")
student = make_character(201, "女儿A", 152, daughter=True, stage=103)
check("角色不存在时 (0, 0)", auto_schedule.auto_fill_selected_course(999) == (0, 0))
filled_c, skipped_c = auto_schedule.auto_fill_selected_course(201)
check("选上了课", filled_c > 0, (filled_c, skipped_c))
check("覆盖 7 天：周末没课的节次计入跳过", filled_c + skipped_c == 7 * period_count, (filled_c, skipped_c))
check("周末节次全部跳过", skipped_c >= 2 * period_count)
check("重复点击幂等", auto_schedule.auto_fill_selected_course(201) == (0, skipped_c))
# 该科等级最低优先：给学生某科高等级，同节次若有该科与别科，应选别科
student.ability[45] = 8
clear_schedules()
schedule_handle.set_class_cell(room_list[0], 0, 0, 45, 101)
schedule_handle.set_class_cell(room_list[1], 0, 0, 43, 103)
cache.character_data[201].child_growth.selected_course = {}
auto_schedule.auto_fill_selected_course(201)
check("同节多课时选自己等级最低的那门", schedule_handle.get_selected_course(201, 0, 0) == [education_constant.COURSE_TYPE_THEORY, room_list[1]])

finish()
