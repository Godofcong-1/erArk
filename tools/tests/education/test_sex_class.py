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
# 季月最后一天的下一天是下个季月的 1 日（9/30 周三 → 12/1 周二），星期跟着跳（第五轮）
set_time(datetime.datetime(2026, 9, 29, 10, 0))
month_jump = sex_class_handle.get_date_ordinal_by_week_day(4, 0)
check("月底预约周五 → 按游戏时钟落在 12/4，而不是永远不会到的 10/2", month_jump == datetime.date(2026, 12, 4).toordinal(), datetime.date.fromordinal(month_jump))
check("月底预约周三 → 就是明天 9/30", sex_class_handle.get_date_ordinal_by_week_day(2, 0) == datetime.date(2026, 9, 30).toordinal())
set_time(period_time(3))

section("谁能参加")
check("玩家自己不算", not sex_class_handle.judge_can_join_sex_class(0))
check("不存在的角色不算", not sex_class_handle.judge_can_join_sex_class(999))
# 前置修习（口径 63 宽松版，第五轮）：个人课表里没有性技科目的教室课就不能来
check("没修过性技课：不能参加", not sex_class_handle.judge_has_sex_skill_course(201) and not sex_class_handle.judge_can_join_sex_class(201))
check("点名必修豁免前置修习", sex_class_handle.judge_can_join_sex_class(201, check_course=False))
schedule_handle.set_class_cell(ROOM_P, weekday, 8, 74, -1)
schedule_handle.set_class_cell(_("理论教室一"), weekday, 8, 45, -1)
schedule_handle.set_selected_course(202, weekday, 8, education_constant.COURSE_TYPE_THEORY, _("理论教室一"))
check("只修了学识：仍不能参加", not sex_class_handle.judge_has_sex_skill_course(202))
schedule_handle.set_selected_course(201, weekday, 8, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
schedule_handle.set_selected_course(202, (weekday + 1) % 7, 8, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
schedule_handle.set_class_cell(ROOM_P, (weekday + 1) % 7, 8, 71, -1)
check("个人课表里有性技教室课：可以参加", sex_class_handle.judge_has_sex_skill_course(201) and sex_class_handle.judge_has_sex_skill_course(202))
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
student_a.work.work_type = 21
check("选修名单只收学生岗：改了岗的女儿课表里还留着这一格，也不算「会来」（Plan 28 §3.4）", sex_class_handle.get_selected_student_list(ROOM_P, weekday, 2) == [])
student_a.work.work_type = 152
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
# 预约的课下课后条目留到跨天，但打上已下课标记，覆盖层不再认它（第五轮）
set_time(period_time(4) + datetime.timedelta(minutes=20))
check("预约的课下课：条目保留、标记 ended", sex_class_handle.get_temp_class(today, 4) is reserved and reserved.get("ended") is True)
check("已下课：不再是有效临时课", sex_class_handle.get_active_temp_class(today, 4) is None)
check("已下课：课表格子交还原来的课", schedule_handle.get_class_cell(ROOM_P, weekday, 4) is None)
check("已下课：玩家的教师反查也取不到", schedule_handle.get_teacher_cell(0, weekday, 4) is None)
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

section("当场开的课下课即删（第五轮）")
impromptu_key = sex_class_handle.get_running_class_key()
check("当场开的课正在进行", impromptu_key == sex_class_handle.get_class_key(today, 5))
sex_class_handle.end_sex_class()
check("当场开的课下课后条目直接删掉", impromptu_key not in cache.rhodes_island.temp_sex_class)
cache.sex_class_mode = False
cache.group_sex_mode = False

section("出勤只给女儿与学生岗记（第五轮）")
adult_attend = make_character(302, "路过的成年干员", 21)
sex_class_handle.settle_attend(302)
check("非学生的成年干员：不记、不惰性创建养成数据", adult_attend.child_growth is None)
adult_student = make_character(303, "成年学生", 152)
sex_class_handle.settle_attend(303)
check("成年学生：记一节", adult_student.child_growth is not None and adult_student.child_growth.attend_class_count == 1)

section("Plan 26 §3.5：提前几分钟开讲预约的课，开的就是预约那节")
cache.rhodes_island.temp_sex_class = {}
cache.sex_class_mode = False
cache.group_sex_mode = False
newbie = make_character(204, "没修过性技课的必修生", 152, daughter=True, stage=103, mother_id=102)
move_to(0, classroom_path(ROOM_P))
move_to(204, classroom_path(ROOM_P))
reserved = sex_class_handle.set_temp_class(today, 6, ROOM_P, 72, must_attend=[204])
early = period_time(6) - datetime.timedelta(minutes=5)
set_time(early)
key_6 = sex_class_handle.get_class_key(today, 6)
check("找得到这间教室半小时内开讲的预约", sex_class_handle.find_reserved_class(ROOM_P, early) == (key_6, reserved))
check("别的教室、开课前 45 分钟都找不到", sex_class_handle.find_reserved_class(_("大礼堂"), early) == ("", None)
      and sex_class_handle.find_reserved_class(ROOM_P, period_time(6) - datetime.timedelta(minutes=45)) == ("", None))
check("必修名单：不给教室按当前节次取（取不到），给了教室按这间教室的预约取", sex_class_handle.get_must_attend_set() == set() and sex_class_handle.get_must_attend_set(ROOM_P) == {204})
check("开课前的场景学生名单含没修过性技课的必修生", 204 in sex_class_handle.get_scene_student_list(), sex_class_handle.get_scene_student_list())
check("开课指令预读得到预约（不再重问主修）", sex_class_handle.find_class_to_start(ROOM_P, early)[1] is reserved)
now_class = sex_class_handle.start_sex_class(72)
check("复用预约条目：运行中、标记预约、键还是第 6 节", now_class is reserved and reserved["running"] and reserved["reserved"] and sex_class_handle.get_running_class_key() == key_6)
check("没有另开一节当场课", list(cache.rhodes_island.temp_sex_class.keys()) == [key_6], list(cache.rhodes_island.temp_sex_class.keys()))
set_time(period_time(6) + datetime.timedelta(minutes=45))
check("按预约的节次判档：到点下课是「按时」", sex_class_handle.judge_end_type() == 1)
sex_class_handle.end_sex_class()
check("下课后预约那条打上 ended、不再覆盖", reserved.get("ended") is True and sex_class_handle.get_active_temp_class(today, 6) is None)
set_time(period_time(6) + datetime.timedelta(minutes=20))
check("已下课的预约不再被当成等着开讲的", sex_class_handle.find_reserved_class(ROOM_P, cache.game_time) == ("", None))
check("同一节下课后在同一间教室重开：沿用那条", sex_class_handle.find_class_to_start(ROOM_P, cache.game_time)[1] is reserved)
reopen = sex_class_handle.start_sex_class(72, [])
check("重开：清掉已下课标记、仍是预约", reopen is reserved and reserved["ended"] is False and reserved["running"])
sex_class_handle.end_sex_class()

section("Plan 26 L4：别的教室当场开课，把占着键的预约挪过来而不是覆盖")
moved = sex_class_handle.set_temp_class(today, 7, ROOM_P, 73, must_attend=[204])
set_time(period_time(7) + datetime.timedelta(minutes=5))
move_to(0, classroom_path(_("大礼堂")))
started = sex_class_handle.start_sex_class(71, [])
check("挪用：还是那一条，教室改成大礼堂，必修名单保留、算预约", started is moved and moved["classroom"] == _("大礼堂") and moved["must_attend"] == [204] and moved["reserved"], moved)
sex_class_handle.end_sex_class()
move_to(0, classroom_path(ROOM_P))

section("Plan 26 §3.10：课堂 H 只收学生岗")
student_b.work.work_type = 51
check("改了岗的女儿：点名必修也不能参加", not sex_class_handle.judge_can_join_sex_class(202, check_course=False))
check("改了岗的女儿不进场景学生名单", 202 not in sex_class_handle.get_scene_student_list())
student_b.work.work_type = 152
check("改回学生岗恢复", sex_class_handle.judge_can_join_sex_class(202))

section("Plan 26 L8：开课前半小时的提醒写实")
cache.rhodes_island.temp_sex_class = {}
sex_class_handle.set_temp_class(today, 8, ROOM_P, 70)
text_list = sex_class_handle.check_and_send_notify(period_time(8) - datetime.timedelta(minutes=40), period_time(8) - datetime.timedelta(minutes=25))
check("提醒写的是开课前 10 分钟动身，不再说「已经在往教室走了」", len(text_list) == 1 and "10" in text_list[0] and "已经在往教室走了" not in text_list[0], text_list)
cache.rhodes_island.temp_sex_class = {}

section("Plan 27 L2（按设计保留）：同一节里下课后再开一次实操课，到场学生再记一节出勤")
cache.sex_class_mode = False
cache.group_sex_mode = False
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
student_a.sp_flag.is_h = False
set_time(period_time(1) + datetime.timedelta(minutes=5))
_attend = growth_handle.get_child_growth(201).attend_class_count
sex_class_handle.start_sex_class(70)
sex_class_handle.end_sex_class()
_first = growth_handle.get_child_growth(201).attend_class_count
student_a.sp_flag.is_h = False
set_time(period_time(1) + datetime.timedelta(minutes=15))
sex_class_handle.start_sex_class(70)
sex_class_handle.end_sex_class()
check("每次开课单独记一次（用户拍板，复查时别当成重复计数去重）：开课 +1，同一节下课后再开又 +1",
      _first == _attend + 1 and growth_handle.get_child_growth(201).attend_class_count == _attend + 2,
      (_attend, _first, growth_handle.get_child_growth(201).attend_class_count))
student_a.sp_flag.is_h = False
cache.rhodes_island.temp_sex_class = {}

section("Plan 30 §3.4：这一节已记缺课的学生，开课与 722 晚到都不记出勤")
cache.sex_class_mode = False
cache.group_sex_mode = False
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
set_time(period_time(2) + datetime.timedelta(minutes=5))
growth_handle.get_child_growth(201).last_absent_period = [cache.game_time.toordinal(), 2]
_attend = growth_handle.get_child_growth(201).attend_class_count
sex_class_handle.start_sex_class(70, [201])
check("开课时到场的学生这一节已缺课：不记出勤（开课传 cache.game_time）", growth_handle.get_child_growth(201).attend_class_count == _attend)
sex_class_handle.end_sex_class()
student_a.sp_flag.is_h = False
sex_class_handle.settle_attend(201)
check("722 晚到（取学生的行为开始时刻）：同一节同样不记", growth_handle.get_child_growth(201).attend_class_count == _attend)
set_time(period_time(3) + datetime.timedelta(minutes=5))
sex_class_handle.settle_attend(201)
check("下一节没缺课：照常记", growth_handle.get_child_growth(201).attend_class_count == _attend + 1)
growth_handle.get_child_growth(201).last_absent_period = []
cache.rhodes_island.temp_sex_class = {}

section("Plan 31 M1：实操课门槛的实行值只判不扣——门槛与前提求值多次，不扣理智、不累加今日消耗、不解除催眠")
from Script.Design import instuct_judege  # noqa: E402

cache.sex_class_mode = False
cache.group_sex_mode = False
set_time(period_time(3))
_hypno_day = (cache.game_time.weekday() + 3) % 7
hypno = make_character(305, "心控中的成年学生", 152)
hypno.talent[72] = 1  # 被深层催眠
hypno.sp_flag.unconscious_h = 7  # 心控：不在 normal 5 / 6 里，门槛一路走到实行值计算的催眠补正段
schedule_handle.set_class_cell(ROOM_P, _hypno_day, 8, 74, -1)
schedule_handle.set_selected_course(305, _hypno_day, 8, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
move_to(0, classroom_path(ROOM_P))
move_to(305, classroom_path(ROOM_P))
pl.sanity_point_max = 2000
pl.sanity_point = 2000
pl.pl_ability.today_sanity_point_cost = 0
pl.talent[332] = 0
check("M1 前置：成年非女儿的学生岗、排过性技教室课、好感为 0；玩家没有中级催眠时实行值不足，进不了课堂",
      hypno.relationship.father_id != 0 and sex_class_handle.judge_has_sex_skill_course(305) and hypno.favorability.get(0, 0) == 0
      and not sex_class_handle.judge_can_join_sex_class(305))
pl.talent[332] = 1  # 中级催眠：对深层催眠的目标，实行值不足的部分由理智折算补上
_m1_list = []
for _index in range(4):
    _m1_list.append(sex_class_handle.judge_can_join_sex_class(305))
    _m1_list.append(bool(handle_premise.handle_premise("scene_have_sex_class_student", 0)))
check("M1 理智够时门槛照样成立（催眠补正照算）：门槛与指令 5209 的前提 scene_have_sex_class_student 各求值 4 次都成立", all(_m1_list), _m1_list)
check("M1 求值 8 次后玩家理智不变、今日消耗不累加（此前每求值一次扣一回）", pl.sanity_point == 2000 and pl.pl_ability.today_sanity_point_cost == 0,
      (pl.sanity_point, pl.pl_ability.today_sanity_point_cost))
check("M1 她的心控没被动过", hypno.sp_flag.unconscious_h == 7, hypno.sp_flag.unconscious_h)
cache.sex_class_mode = True
cache.group_sex_mode = True
_m1_running = sex_class_handle.set_temp_class(today, 3, ROOM_P, 74, running=True)
hypno.sp_flag.is_h = True
_m1_in_class = [bool(handle_premise.handle_premise("self_in_sex_class", 305)) for _index in range(3)]
hypno.sp_flag.is_h = False
_m1_joinable = [class_ai.judge_pending_class_joinable(305, _m1_running, ROOM_P) for _index in range(3)]
check("M1 口上前提 self_in_sex_class 与她自己决策时的入课判定（judge_pending_class_joinable）各求值 3 次都成立，理智仍不变",
      all(_m1_in_class) and all(_m1_joinable) and pl.sanity_point == 2000 and pl.pl_ability.today_sanity_point_cost == 0,
      (_m1_in_class, _m1_joinable, pl.sanity_point, pl.pl_ability.today_sanity_point_cost))
cache.sex_class_mode = False
cache.group_sex_mode = False
cache.rhodes_island.temp_sex_class = {}
pl.sanity_point = 0
check("M1 理智为 0：没有补正，门槛不成立", not sex_class_handle.judge_can_join_sex_class(305))
handle_premise.handle_premise("scene_have_sex_class_student", 0)
check("M1 理智为 0 时判门槛、求值前提都不解除她的催眠（此前心控被清零），今日消耗仍为 0",
      hypno.sp_flag.unconscious_h == 7 and pl.sanity_point == 0 and pl.pl_ability.today_sanity_point_cost == 0,
      (hypno.sp_flag.unconscious_h, pl.sanity_point, pl.pl_ability.today_sanity_point_cost))
pl.sanity_point = 2000
_m1_default = instuct_judege.calculation_instuct_judege(0, 305, _("H模式"), not_draw_flag=True)
_m1_cost = 2000 - pl.sanity_point
check("M1 其它系统的缺省调用（settle_hypnosis=True）照旧：补正后通过、扣理智、累加今日消耗",
      _m1_default[0] == 1 and _m1_cost > 0 and pl.pl_ability.today_sanity_point_cost == _m1_cost, (_m1_default, _m1_cost, pl.pl_ability.today_sanity_point_cost))
pl.sanity_point = 0
instuct_judege.calculation_instuct_judege(0, 305, _("H模式"), not_draw_flag=True)
check("M1 缺省调用在理智不足时照旧解除催眠", hypno.sp_flag.unconscious_h == 0, hypno.sp_flag.unconscious_h)
pl.talent[332] = 0
pl.sanity_point = 0
pl.sanity_point_max = 0
pl.pl_ability.today_sanity_point_cost = 0
schedule_handle.clear_class_cell(ROOM_P, _hypno_day, 8)
remove_character(305)

section("Plan 31 L3：提前几分钟开讲预约的实操课，按那一节判「本节已缺课」；L12：记出勤时累计实操课次数")
cache.rhodes_island.temp_sex_class = {}
cache.sex_class_mode = False
cache.group_sex_mode = False
move_to(0, classroom_path(ROOM_P))
move_to(201, classroom_path(ROOM_P))
student_a.sp_flag.is_h = False
_g201 = growth_handle.get_child_growth(201)
_l3_early = period_time(5) - datetime.timedelta(minutes=5)
check("L3 前置：14:40 开讲还在上一节（节次 4），预约的是 14:45 开始的节次 5", game_time.get_class_period_by_time(_l3_early) == 4)
sex_class_handle.set_temp_class(today, 5, ROOM_P, 70)
set_time(_l3_early)
_g201.last_absent_period = [today, 4]
_attend, _sex = _g201.attend_class_count, _g201.sex_class_count
sex_class_handle.start_sex_class(70, [201])
check("L3 提前 5 分钟开讲、上一节缺过课：出勤 +1（此前按开讲时刻判成本节已缺课，出勤记不上）", _g201.attend_class_count == _attend + 1, (_attend, _g201.attend_class_count))
check("L12 记出勤的同时累计实操课次数 +1，养成数值 25 读得到",
      _g201.sex_class_count == _sex + 1 and growth_handle.get_growth_value(201, education_constant.GROWTH_VALUE_SEX_CLASS) == _sex + 1, (_sex, _g201.sex_class_count))
_g201.last_absent_period = [today, 5]
_attend, _sex = _g201.attend_class_count, _g201.sex_class_count
sex_class_handle.settle_attend(201)
check("L3 722 晚到（取行为开始时刻 14:40）同样按那一节判：这一节已缺课，出勤与实操课次数都不加",
      _g201.attend_class_count == _attend and _g201.sex_class_count == _sex, (_attend, _g201.attend_class_count, _sex, _g201.sex_class_count))
_g201.last_absent_period = [today, 4]
sex_class_handle.settle_attend(201)
check("L3 722 晚到、只有上一节缺过课：出勤与实操课次数照记",
      _g201.attend_class_count == _attend + 1 and _g201.sex_class_count == _sex + 1, (_attend, _g201.attend_class_count, _sex, _g201.sex_class_count))
sex_class_handle.end_sex_class()
cache.rhodes_island.temp_sex_class = {}
sex_class_handle.set_temp_class(today, 5, ROOM_P, 70)
set_time(_l3_early)
_g201.last_absent_period = [today, 5]
_attend, _sex = _g201.attend_class_count, _g201.sex_class_count
sex_class_handle.start_sex_class(70, [201])
check("L3 提前开讲、这一节本身已记缺课：开课时出勤与实操课次数都不加",
      _g201.attend_class_count == _attend and _g201.sex_class_count == _sex, (_attend, _g201.attend_class_count, _sex, _g201.sex_class_count))
sex_class_handle.end_sex_class()
cache.rhodes_island.temp_sex_class = {}
set_time(datetime.datetime(_l3_early.year, _l3_early.month, _l3_early.day, 12, 30))
_g201.last_absent_period = [today, 3]
_attend, _sex = _g201.attend_class_count, _g201.sex_class_count
sex_class_handle.start_sex_class(70, [201])
check("L3 节次外的当场课（节次 -1）没有开始时刻，照旧按参照时刻判：不报错，出勤与实操课次数照记",
      sex_class_handle.get_running_class_key() == sex_class_handle.get_class_key(today, -1)
      and _g201.attend_class_count == _attend + 1 and _g201.sex_class_count == _sex + 1, (sex_class_handle.get_running_class_key(), _attend, _g201.attend_class_count))
sex_class_handle.end_sex_class()
_g201.last_absent_period = []
cache.rhodes_island.temp_sex_class = {}

finish()
