# -*- coding: UTF-8 -*-
"""sex_class_handle：临时课程、提醒、开课下课、旁观结算"""
from _bootstrap import *  # noqa: F401,F403

open_all_classroom()
clear_schedules()
ROOM_P = _("实践教室一")
mother = make_character(102, "母亲", 0)
student_a = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102)
student_b = make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102)
adult = make_character(301, "成年干员", 21)
today = cache.game_time.date().toordinal()

section("键与存取")
check("键格式", sex_class_handle.get_class_key(739510, 3) == "739510-3")
check("解析", sex_class_handle.parse_class_key("739510-3") == (739510, 3) and sex_class_handle.parse_class_key("739510--1") == (739510, -1))
check("非法键 (-1, -1)", sex_class_handle.parse_class_key("abc") == (-1, -1) and sex_class_handle.parse_class_key("1-x") == (-1, -1))
check("没排时 None", sex_class_handle.get_temp_class(today, 0) is None)
data = sex_class_handle.set_temp_class(today, 2, ROOM_P, 70, must_attend=[201])
check("排课数据", data["classroom"] == ROOM_P and data["ability_id"] == 70 and data["must_attend"] == [201]
      and data["notified"] == [False, False, False] and not data["running"] and not data["reserved"])
check("读回同一条", sex_class_handle.get_temp_class(today, 2) is data)
check("当场开课的 notified 全为已发", sex_class_handle.set_temp_class(today, 3, ROOM_P, 71, running=True)["notified"] == [True, True, True])
check("运行中的那条", sex_class_handle.get_running_class()["ability_id"] == 71 and sex_class_handle.get_running_class_key() == sex_class_handle.get_class_key(today, 3))
sex_class_handle.del_temp_class(today, 3)
check("删掉后没有运行中的课", sex_class_handle.get_running_class() is None and sex_class_handle.get_running_class_key() == "")
sex_class_handle.del_temp_class(today, 99)
check("删不存在的不报错", True)

section("过期清理")
sex_class_handle.set_temp_class(today - 1, 1, ROOM_P, 70)
sex_class_handle.set_temp_class(today - 2, 1, ROOM_P, 70, running=True)
sex_class_handle.set_temp_class(today + 1, 1, ROOM_P, 70)
check("清掉昨天的、保留运行中的与今后的", sex_class_handle.clean_expired_temp_class() == 1
      and sex_class_handle.get_temp_class(today - 2, 1) is not None and sex_class_handle.get_temp_class(today + 1, 1) is not None)
cache.rhodes_island.temp_sex_class = {}

section("星期 → 日期")
set_time(period_time(3))
weekday = cache.game_time.weekday()
check("今天、还没开始的节次 → 今天", sex_class_handle.get_date_ordinal_by_week_day(weekday, 5) == today)
check("今天、已开始的节次 → 下周", sex_class_handle.get_date_ordinal_by_week_day(weekday, 3) == today + 7)
check("别的星期 → 未来 1~6 天内", 1 <= sex_class_handle.get_date_ordinal_by_week_day((weekday + 2) % 7, 0) - today <= 6)

section("谁能参加")
check("玩家自己不算", not sex_class_handle.judge_can_join_sex_class(0))
check("不存在的角色不算", not sex_class_handle.judge_can_join_sex_class(999))
check("女儿零门槛", sex_class_handle.judge_can_join_sex_class(201))
student_a.sp_flag.imprisonment = True
check("被监禁不算", not sex_class_handle.judge_can_join_sex_class(201))
student_a.sp_flag.imprisonment = False
student_a.dead = True
check("死亡不算", not sex_class_handle.judge_can_join_sex_class(201))
student_a.dead = False
try:
    adult_ok = sex_class_handle.judge_can_join_sex_class(301)
    check("成年干员走实行值判定（无实行值 → 不能）", adult_ok is False, adult_ok)
except Exception as error:
    check("成年干员实行值判定不抛异常", False, repr(error))
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
move_to(202, classroom_path(ROOM_P))
check("场景学生名单", sex_class_handle.get_scene_student_list() == [201, 202] or sorted(sex_class_handle.get_scene_student_list()) == [201, 202])
check("指定场景为空场景", sex_class_handle.get_scene_student_list(SCENE_EDU_ENTRY) == [])
schedule_handle.set_selected_course(201, weekday, 2, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
check("选修名单：这一节选了这间教室的人", sex_class_handle.get_selected_student_list(ROOM_P, weekday, 2) == [201])
check("在实践教室 → 可开课场所", sex_class_handle.judge_in_sex_class_place(0))
move_to(0, SCENE_DORM)
check("在宿舍 → 不是", not sex_class_handle.judge_in_sex_class_place(0))
move_to(0, classroom_path(ROOM_P))

section("提醒")
now_a = datetime.datetime(2026, 9, 7, 13, 0)
check("跨越判定", sex_class_handle.judge_time_crossed(now_a, now_a - datetime.timedelta(minutes=5), now_a)
      and not sex_class_handle.judge_time_crossed(now_a, now_a, now_a + datetime.timedelta(minutes=5))
      and not sex_class_handle.judge_time_crossed(None, now_a, now_a))
check("补齐旧档的 notified", sex_class_handle.fix_notified({"notified": [True]}) == [True, False, False] and sex_class_handle.fix_notified({"notified": "x"}) == [False, False, False])
check("节次起止时刻", sex_class_handle.get_period_start_time(today, 4) == period_time(4) and sex_class_handle.get_period_end_time(today, 4) == period_time(4) + datetime.timedelta(minutes=45)
      and sex_class_handle.get_period_start_time(today, 9) is None)
cache.rhodes_island.temp_sex_class = {}
reserved = sex_class_handle.set_temp_class(today, 4, ROOM_P, 70, must_attend=[201])
text_list = sex_class_handle.check_and_send_notify(period_time(4) - datetime.timedelta(minutes=60), period_time(4) - datetime.timedelta(minutes=20))
check("跨过开始前 30 分钟 → 第二次提醒", len(text_list) == 1 and reserved["notified"][1])
check("再结算一次不重发", sex_class_handle.check_and_send_notify(period_time(4) - datetime.timedelta(minutes=20), period_time(4)) == [])
check("没在上课时不发第三次", sex_class_handle.check_and_send_notify(period_time(4) + datetime.timedelta(minutes=40), period_time(4) + datetime.timedelta(minutes=50)) == [])
reserved["running"] = True
check("上课中跨过下课时刻 → 第三次提醒", len(sex_class_handle.check_and_send_notify(period_time(4) + datetime.timedelta(minutes=40), period_time(4) + datetime.timedelta(minutes=50))) == 1 and reserved["notified"][2])
reserved["running"] = False
set_time(period_time(0))
first_text = sex_class_handle.get_today_class_notify_text()
check("起床提醒含教室与科目", ROOM_P in first_text and game_config.config_ability[70].name in first_text and reserved["notified"][0])
check("起床提醒只发一次", sex_class_handle.get_today_class_notify_text() == "")

section("开课与下课")
set_time(period_time(4))
student_a.child_growth.attend_class_count = 0
now_class = sex_class_handle.start_sex_class(70)
check("预约的那节：复用条目、标记预约", now_class is reserved and now_class["running"] and now_class["reserved"])
check("到场学生记出勤", student_a.child_growth.attend_class_count == 1 and growth_handle.get_child_growth(202).attend_class_count == 1)
check("当前主修科目 70", sex_class_handle.get_now_class_ability() == 70)
check("主修经验 id = 指技的升级需求经验", sex_class_handle.get_now_bonus_exp_id() == growth_handle.get_subject_exp_id(70) > 0)
check("玩家在课中", sex_class_handle.judge_in_running_class(0) and sex_class_handle.judge_in_running_class(201))
move_to(202, SCENE_DORM)
check("不在那间教室的学生不算在课中", not sex_class_handle.judge_in_running_class(202))
move_to(202, classroom_path(ROOM_P))
set_time(period_time(4) + datetime.timedelta(minutes=10))
check("下课类型：提前", sex_class_handle.judge_end_type() == 0)
set_time(period_time(4) + datetime.timedelta(minutes=43))
check("下课类型：按时", sex_class_handle.judge_end_type() == 1)
set_time(period_time(4) + datetime.timedelta(minutes=70))
check("下课类型：拖堂", sex_class_handle.judge_end_type() == 2)
pl.ability[70] = 6
bonus = sex_class_handle.get_subject_bonus(201)
check("主修加成 = 2.0 × 速度(1+0.25×6) × 教育区", abs(bonus - education_constant.SUBJECT_BONUS * 2.5 * growth_handle.get_education_zone_adjust()) < 1e-9, bonus)
check("不存在的学生加成 1.0", sex_class_handle.get_subject_bonus(999) == 1.0)
sex_class_handle.end_sex_class()
check("下课后没有运行中的课、类型 -1、加成 1.0", sex_class_handle.get_running_class() is None and sex_class_handle.judge_end_type() == -1 and sex_class_handle.get_subject_bonus(201) == 1.0)
sex_class_handle.end_sex_class()
check("重复下课不报错", True)
cache.rhodes_island.temp_sex_class = {}
set_time(period_time(5))
new_class = sex_class_handle.start_sex_class(71)
check("当场开课：新建条目、非预约、运行中", new_class["reserved"] is False and new_class["running"] and new_class["classroom"] == ROOM_P and new_class["ability_id"] == 71)

section("旁观")
check("体力不足只旁观", (setattr(student_b, "hit_point", 10), sex_class_handle.judge_hp_low_only_watch(202))[1] and not sex_class_handle.judge_hp_low_only_watch(201) and not sex_class_handle.judge_hp_low_only_watch(999))
student_b.hit_point = 100
cache.sex_class_mode = False
check("没开课堂模式没有旁观者", sex_class_handle.get_watcher_list() == [])
cache.sex_class_mode = True
cache.group_sex_mode = True
student_a.sp_flag.is_h = True
student_b.sp_flag.is_h = True
watcher_list = sex_class_handle.get_watcher_list()
check("在场、H 中、不在模板里的都是旁观者", sorted(watcher_list) == [201, 202], watcher_list)
student_b.sp_flag.is_h = False
check("不在 H 状态的不算旁观", sex_class_handle.get_watcher_list() == [201])
student_b.sp_flag.is_h = True
exp_id = sex_class_handle.get_now_bonus_exp_id()
change = game_type.CharacterStatusChange()
change.target_change.setdefault(202, game_type.TargetChange())
change.target_change[202].experience[exp_id] = 40
exp_before = student_a.experience.get(exp_id, 0)
shy_before = student_a.status_data.get(16, 0)
_orig_random = random.random
random.random = lambda: 0.99
sex_class_handle.settle_watcher(5, change)
random.random = _orig_random
check("旁观者拿 25% 主修经验", student_a.experience.get(exp_id, 0) - exp_before == 10)
check("旁观者羞耻上升", student_a.status_data.get(16, 0) > shy_before)
check("变更记录里也记了旁观者", change.target_change[201].experience.get(exp_id, 0) == 10)
exp_before = student_a.experience.get(exp_id, 0)
sex_class_handle.settle_watcher(0, change)
check("add_time=0 不结算", student_a.experience.get(exp_id, 0) == exp_before)

finish()
