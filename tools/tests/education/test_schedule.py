# -*- coding: UTF-8 -*-
"""schedule_handle：教室、全局课表、个人课表、当前课程、上课地点、实习导师"""
from _bootstrap import *  # noqa: F401,F403

section("教室列表与开放判定")
clear_schedules()
cache.rhodes_island.facility_open = {}
base_list = schedule_handle.get_classroom_list()
check("只开三间基础教室", len(base_list) == 3, base_list)
check("基础教室是 理论教室一/实践教室一/大礼堂", base_list == [_("理论教室一"), _("实践教室一"), _("大礼堂")], base_list)
open_all_classroom()
room_list = schedule_handle.get_classroom_list()
check("全开后 10 间教室", len(room_list) == 10, room_list)
check("顺序为 理论→实践→大礼堂", room_list[0] == _("理论教室一") and room_list[5] == _("理论教室六")
      and room_list[6] == _("实践教室一") and room_list[-1] == _("大礼堂"), room_list)
check("按课型筛：理论课 6 间", len(schedule_handle.get_classroom_list(education_constant.COURSE_TYPE_THEORY)) == 6)
check("按课型筛：非法课型为空", schedule_handle.get_classroom_list(99) == [])
check("教室反查课型", schedule_handle.get_course_type_by_classroom(_("理论教室二")) == education_constant.COURSE_TYPE_THEORY
      and schedule_handle.get_course_type_by_classroom(_("实践教室三")) == education_constant.COURSE_TYPE_PRACTICE
      and schedule_handle.get_course_type_by_classroom(_("大礼堂")) == education_constant.COURSE_TYPE_PUBLIC
      and schedule_handle.get_course_type_by_classroom("不存在的教室") == -1)
room_path = schedule_handle.get_classroom_position(_("理论教室一"))
check("教室场景路径可达", room_path and scene_str(room_path) in cache.scene_data, room_path)
check("排序键：中文数字序", [schedule_handle.get_classroom_sort_key(_("理论教室") + w) for w in "一二三四五六"] == [0, 1, 2, 3, 4, 5])

section("全局课表格子")
ROOM1 = _("理论教室一")
ROOM2 = _("理论教室二")
teacher = make_character(101, "教师甲", 151)
teacher_b = make_character(102, "教师乙", 151)
check("初始格子为空", schedule_handle.get_class_cell(ROOM1, 0, 0) is None)
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
check("写入后可读", schedule_handle.get_class_cell(ROOM1, 0, 0) == [45, 101])
check("教师反查", schedule_handle.get_teacher_cell(101, 0, 0) == (ROOM1, 45))
check("别的教师反查为空", schedule_handle.get_teacher_cell(102, 0, 0) is None)
check("冲突：同节次排进另一间", schedule_handle.judge_teacher_conflict(101, 0, 0, ROOM2) != "")
check("不冲突：同一间", schedule_handle.judge_teacher_conflict(101, 0, 0, ROOM1) == "")
check("不冲突：别的节次", schedule_handle.judge_teacher_conflict(101, 0, 1, ROOM2) == "")
schedule_handle.set_class_cell(ROOM2, 2, 3, 43, 101)
week = schedule_handle.get_teacher_week_schedule(101)
check("教师周表含两格", sum(len(v) for v in week.values()) == 2 and week[2][3] == (ROOM2, 43), week)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
check("清空后为空", schedule_handle.get_class_cell(ROOM1, 0, 0) is None)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
check("重复清空不报错", True)
check("教师候选只列教师岗", sorted(schedule_handle.get_teacher_candidate_list()) == [101, 102])

section("临时实操课覆盖层")
today = cache.game_time.date().toordinal()
sex_class_handle.set_temp_class(today, 2, _("实践教室一"), 70, must_attend=[])
check("覆盖层：今天该节次读到主修科目与教师0", schedule_handle.get_class_cell(_("实践教室一"), cache.game_time.weekday(), 2) == [70, 0])
other_day = (cache.game_time.weekday() + 1) % 7
check("覆盖层不影响别的星期", schedule_handle.get_class_cell(_("实践教室一"), other_day, 2) is None)
check("玩家的教师反查走覆盖层", schedule_handle.get_teacher_cell(0, cache.game_time.weekday(), 2) == (_("实践教室一"), 70))
check("玩家周表并入今天的临时课", 2 in schedule_handle.get_teacher_week_schedule(0).get(cache.game_time.weekday(), {}))
# 第五轮：要写进每周循环的个人课表时不叠加覆盖层
check("include_temp=False 读的是每周固定的课表本身", schedule_handle.get_class_cell(_("实践教室一"), cache.game_time.weekday(), 2, include_temp=False) is None)
temp_student = make_character(209, "临时课测试", 152, daughter=True, stage=103)
auto_schedule.auto_fill_selected_course(209)
check("一键选课不会把一次性的临时课选进每周课表", schedule_handle.get_selected_course(209, cache.game_time.weekday(), 2) is None)
remove_character(209)
cache.rhodes_island.temp_sex_class = {}

section("个人课表与当前课程")
student = make_character(201, "女儿A", 152, daughter=True, stage=103)
check("初始个人课表为空", schedule_handle.get_selected_course(201, 0, 0) is None)
check("没有养成数据也不会被凭空创建", cache.character_data[201].child_growth is None)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
check("写入后可读", schedule_handle.get_selected_course(201, 0, 0) == [education_constant.COURSE_TYPE_THEORY, ROOM1])
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
set_time(period_time(0))
now_course = schedule_handle.get_now_course(201)
check("第1节：当前课程解析出科目与教师", now_course is not None and now_course["ability_id"] == 45 and now_course["teacher_id"] == 101
      and now_course["classroom"] == ROOM1 and now_course["period"] == 0, now_course)
check("教师视角 get_now_teaching", schedule_handle.get_now_teaching(101) == {
    "course_type": education_constant.COURSE_TYPE_THEORY, "classroom": ROOM1, "ability_id": 45, "period": 0})
check("学生没排课的节次为 None", (set_time(period_time(1)), schedule_handle.get_now_course(201))[1] is None)
set_time(DEFAULT_TIME.replace(hour=13, minute=0))
check("不在节次内为 None", schedule_handle.get_now_course(201) is None and schedule_handle.get_now_teaching(101) is None)
set_time(period_time(0))
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, -1)
now_course = schedule_handle.get_now_course(201)
check("格子在、没排教师：仍是一节课，教师为 -1（到了教室降级自习）", now_course is not None and now_course["ability_id"] == 45 and now_course["teacher_id"] == -1, now_course)
schedule_handle.clear_class_cell(ROOM1, 0, 0)
check("全局课表那一格被清掉（个人课表显示「已停课」）：视为这节没课（Plan 27 §3.3，此前科目 / 教师为 -1、照样去自习记出勤）",
      schedule_handle.get_now_course(201) is None and schedule_handle.get_course_at(201, period_time(0), 0) is None)
schedule_handle.clear_selected_course(201, 0, 0)
check("清空个人课表格子", schedule_handle.get_selected_course(201, 0, 0) is None)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_PE, _("木桩房"))
check("重选即覆盖（学生撞课结构上不可能）", schedule_handle.get_selected_course(201, 0, 0) == [education_constant.COURSE_TYPE_PE, _("木桩房")])

section("上课地点解析")
pe_course = schedule_handle.get_now_course(201)
pe_place = schedule_handle.get_course_place(pe_course)
check("体育课：木桩房精确到那间房", pe_place and cache.scene_data[scene_str(pe_place)].scene_name == _("木桩房"), pe_place)
interest_cid = next(cid for cid in game_config.config_entertainment if game_config.config_entertainment[cid].class_ok)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_INTEREST, interest_cid)
interest_place = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
check("兴趣课：按 Entertainment.csv 的地点标签解析出场景", bool(interest_place), interest_cid)
intern_work = next(cid for cid in game_config.config_work_type
                   if cid and not game_config.config_work_type[cid].tag and game_config.config_work_type[cid].ability_id
                   and cid not in education_constant.EXCLUDE_INTERN_WORK_TYPE and game_config.config_work_type[cid].place_tag in constant.place_data)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_INTERN, intern_work)
intern_place = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
check("实习课：按 WorkType.csv 的地点标签解析出场景", bool(intern_place), intern_work)
mentor = make_character(103, "在岗干员", intern_work, position=intern_place)
intern_place_2 = schedule_handle.get_course_place(schedule_handle.get_now_course(201))
check("实习课优先去在岗干员所在的那间房", intern_place_2 == mentor.position, intern_place_2)
move_to(201, intern_place_2)
check("实习导师 = 同场景同岗位的干员", schedule_handle.get_intern_mentor(201, intern_work) == 103)
move_to(103, SCENE_DORM)
check("导师离场则无人在岗", schedule_handle.get_intern_mentor(201, intern_work) == -1)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_INTEREST, 99999)
check("目标非法：解析为空列表而不是报错；这一节视为没课（Plan 28 §3.2，此前照样返回课）",
      schedule_handle.get_course_place({"course_type": education_constant.COURSE_TYPE_INTEREST, "target": 99999}) == [] and schedule_handle.get_now_course(201) is None)
schedule_handle.set_selected_course(201, 0, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
# 教室课要在全局课表上有这一格，空格子按「已停课」算没课（Plan 27 §3.3）
schedule_handle.set_class_cell(ROOM1, 0, 0, 45, 101)
check("教室课地点 = 教室场景路径", schedule_handle.get_course_place(schedule_handle.get_now_course(201)) == room_path)

section("行为cid反查")
check("213 → teach", schedule_handle.get_behavior_name_by_cid(213) == "teach")
check("查不到为空串", schedule_handle.get_behavior_name_by_cid(-99) == "")

section("Plan 26 §3.6 / §3.7：撞课照每周课表判；玩家授课只在临时课的教室里读临时课")
clear_schedules()
set_time(period_time(0))
today = cache.game_time.date().toordinal()
weekday = cache.game_time.weekday()
ROOM_P = _("实践教室一")
schedule_handle.set_class_cell(ROOM_P, weekday, 2, 43, 101)
sex_class_handle.set_temp_class(today, 2, ROOM_P, 70)
check("被今天的临时课顶掉：工作链的反查查不到她", schedule_handle.get_teacher_cell(101, weekday, 2) is None)
check("include_temp=False 照每周课表查得到", schedule_handle.get_teacher_cell(101, weekday, 2, include_temp=False) == (ROOM_P, 43))
check("撞课判定照每周课表：同一节再排进别的教室判撞课", schedule_handle.judge_teacher_conflict(101, weekday, 2, ROOM1) != "")
check("玩家在 include_temp=False 时查不到临时课", schedule_handle.get_teacher_cell(0, weekday, 2, include_temp=False) is None)
set_time(period_time(2))
move_to(0, room_path)
check("玩家人在理论教室一：get_now_teaching(0) 不返回别处的临时课", schedule_handle.get_now_teaching(0) is None)
move_to(0, schedule_handle.get_classroom_position(ROOM_P))
now_teaching = schedule_handle.get_now_teaching(0)
check("玩家就在临时课的教室里：返回那节课", now_teaching is not None and now_teaching["classroom"] == ROOM_P and now_teaching["ability_id"] == 70, now_teaching)
move_to(0, SCENE_DORM)
clear_schedules()

section("Plan 26 §3.8：个人式课的场所开放与活动条件")
pool = _("游泳池")
pool_open_cid = game_config.config_facility_open_name_to_cid[pool]
pe_pool = {"course_type": education_constant.COURSE_TYPE_PE, "target": pool}
cache.rhodes_island.facility_open[pool_open_cid] = False
check("场景开放判定：未解锁的游泳池为否，不在 Facility_open 表里的基础教室恒为是", not schedule_handle.judge_scene_open(pool) and schedule_handle.judge_scene_open(ROOM1)
      and schedule_handle.judge_classroom_open(ROOM1))
check("体育课排在未解锁的游泳池：解析不出", schedule_handle.get_course_place(pe_pool) == [])
cache.rhodes_island.facility_open[pool_open_cid] = True
check("解锁后恢复", bool(schedule_handle.get_course_place(pe_pool)))
lockable = None
for _cid in game_config.config_entertainment:
    _cfg = game_config.config_entertainment[_cid]
    _names = [cache.scene_data[s].scene_name for s in constant.place_data.get(_cfg.place_tag, [])] if _cfg.class_ok else []
    if _names and all(n in game_config.config_facility_open_name_set for n in _names):
        lockable = (_cid, _names)
        break
check("有地点全靠解锁的兴趣课", lockable is not None)
if lockable is not None:
    _cid, _names = lockable
    interest_course = {"course_type": education_constant.COURSE_TYPE_INTEREST, "target": _cid}
    for _name in _names:
        cache.rhodes_island.facility_open[game_config.config_facility_open_name_to_cid[_name]] = False
    check("兴趣课的场所全未开放：解析不出（此前取第一间，派人去门口空转）", schedule_handle.get_course_place(interest_course) == [], _names)
    cache.rhodes_island.facility_open[game_config.config_facility_open_name_to_cid[_names[-1]]] = True
    _place = schedule_handle.get_course_place(interest_course)
    check("开放其中一间：解析到已开放的那间", bool(_place) and cache.scene_data[scene_str(_place)].scene_name == _names[-1], _place)
    open_all_classroom()
teen = make_character(210, "少女", 152, daughter=True, stage=104)
play_house = {"course_type": education_constant.COURSE_TYPE_INTEREST, "target": education_constant.ENTERTAINMENT_PLAY_HOUSE}
check("活动条件：过家家对少女不成立、对萝莉成立，其余课型恒成立", not schedule_handle.judge_course_need_pass(210, play_house) and schedule_handle.judge_course_need_pass(201, play_house)
      and schedule_handle.judge_course_need_pass(210, pe_pool))
remove_character(210)
import inspect  # noqa: E402

check("get_upcoming_course 删掉了无人传入的 now_time 参数（L8）", "now_time" not in inspect.signature(schedule_handle.get_upcoming_course).parameters)

section("Plan 27 §3.3：已停课视为没课，临时课覆盖层给出的格子照算")
clear_schedules()
set_time(period_time(0))
_today_weekday = cache.game_time.weekday()
_today_ordinal = cache.game_time.date().toordinal()
schedule_handle.set_selected_course(201, _today_weekday, 0, education_constant.COURSE_TYPE_PRACTICE, ROOM_P)
check("选了实践教室一、每周课表那一格空着：没课", schedule_handle.get_now_course(201) is None)
sex_class_handle.set_temp_class(_today_ordinal, 0, ROOM_P, 70)
_course = schedule_handle.get_now_course(201)
check("今天在这间教室预约了实操课：覆盖层给出格子，选修生照样有课（授课者为玩家）", _course is not None and _course["classroom"] == ROOM_P and _course["teacher_id"] == 0
      and _course["ability_id"] == 70, _course)
schedule_handle.clear_selected_course(201, _today_weekday, 0)
sex_class_handle.set_temp_class(_today_ordinal, 0, ROOM_P, 70, must_attend=[201])
_course = schedule_handle.get_now_course(201)
check("点名必修、自己这节没排课：覆盖到临时课的教室，照样有课", _course is not None and _course["classroom"] == ROOM_P, _course)
clear_schedules()

section("Plan 28 §3.2：个人式课这一节上不成视为没课")
set_time(period_time(0))
_wd = cache.game_time.weekday()
teen_b = make_character(211, "少女B", 152, daughter=True, stage=104)
schedule_handle.set_selected_course(211, _wd, 0, education_constant.COURSE_TYPE_INTEREST, education_constant.ENTERTAINMENT_PLAY_HOUSE)
check("judge_personal_course_valid：少女的过家家不成立、萝莉的成立", not schedule_handle.judge_personal_course_valid(211, play_house)
      and schedule_handle.judge_personal_course_valid(201, play_house))
check("少女的过家家：get_now_course / get_course_at 为 None（此前照样返回，两道闸与出勤都按有课判）", schedule_handle.get_now_course(211) is None
      and schedule_handle.get_course_at(211, period_time(0), 0) is None)
schedule_handle.set_selected_course(201, _wd, 0, education_constant.COURSE_TYPE_INTEREST, education_constant.ENTERTAINMENT_PLAY_HOUSE)
check("同一格对萝莉照常是一节课", schedule_handle.get_now_course(201) is not None)
cache.rhodes_island.facility_open[pool_open_cid] = False
schedule_handle.set_selected_course(201, _wd, 0, education_constant.COURSE_TYPE_PE, pool)
check("体育课排在未解锁的游泳池：不成立，视为没课", not schedule_handle.judge_personal_course_valid(201, pe_pool) and schedule_handle.get_now_course(201) is None)
cache.rhodes_island.facility_open[pool_open_cid] = True
check("解锁后照常是一节课", schedule_handle.get_now_course(201) is not None and schedule_handle.get_now_course(201)["target"] == pool)
schedule_handle.set_selected_course(201, _wd, 0, education_constant.COURSE_TYPE_INTERN, intern_work)
check("实习课本节无人在岗：地点仍解析得出（回落到已开放的那间），照旧是一节课（降级见习）", schedule_handle.get_intern_mentor(201, intern_work) == -1
      and schedule_handle.get_now_course(201) is not None)
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 0, ROOM_P, 70, must_attend=[211])
_course = schedule_handle.get_now_course(211)
check("必修覆盖不受影响：少女这节上不成的兴趣课被点名必修，照样指向临时课的教室", _course is not None and _course["classroom"] == ROOM_P, _course)
remove_character(211)
schedule_handle.clear_selected_course(201, _wd, 0)
clear_schedules()

section("Plan 29 §3.2：兴趣课读书借不到书的这一节视为没课（judge_personal_course_valid 只读）")
set_time(period_time(0))
_read_cid = next(cid for cid in game_config.config_entertainment if game_config.config_entertainment[cid].class_ok
                 and schedule_handle.get_behavior_name_by_cid(game_config.config_entertainment[cid].behavior_id) == constant.Behavior.READ_BOOK)
read_course = {"course_type": education_constant.COURSE_TYPE_INTEREST, "target": _read_cid}
check("judge_interest_course_is_read_book：读书课成立，过家家与体育课不成立",
      schedule_handle.judge_interest_course_is_read_book(read_course) and not schedule_handle.judge_interest_course_is_read_book(play_house)
      and not schedule_handle.judge_interest_course_is_read_book(pe_pool))
schedule_handle.set_selected_course(201, _wd, 0, education_constant.COURSE_TYPE_INTEREST, _read_cid)
_reader = cache.character_data[201]
check("书库有书：成立，是一节课", schedule_handle.judge_personal_course_valid(201, read_course) and schedule_handle.get_now_course(201) is not None)
_saved_borrow = dict(cache.rhodes_island.book_borrow_dict)
for _book_id in cache.rhodes_island.book_borrow_dict:
    cache.rhodes_island.book_borrow_dict[_book_id] = 999
check("书库全被借走：不成立，视为没课（此前照样是课，到了图书馆读 0 号书）",
      not schedule_handle.judge_personal_course_valid(201, read_course) and schedule_handle.get_now_course(201) is None)
_easy_book = next(b for b in game_config.config_book if game_config.config_book[b].difficulty <= 1)
_reader.entertainment.borrow_book_id_set.add(_easy_book)
check("手上有借着的书：照常成立", schedule_handle.judge_personal_course_valid(201, read_course) and schedule_handle.get_now_course(201) is not None)
_reader.entertainment.borrow_book_id_set.discard(_easy_book)
cache.rhodes_island.book_borrow_dict[_easy_book] = -1
_reader.entertainment.read_book_progress[_easy_book] = 100
check("书库里只剩一本读完了的书：不成立", not schedule_handle.judge_personal_course_valid(201, read_course))
_reader.entertainment.read_book_progress[_easy_book] = 50
check("那本没读完：成立", schedule_handle.judge_personal_course_valid(201, read_course))
del _reader.entertainment.read_book_progress[_easy_book]
cache.rhodes_island.book_borrow_dict[_easy_book] = 999
_hard_book = next((b for b in game_config.config_book if game_config.config_book[b].difficulty == 3
                   and game_config.config_book_type[game_config.config_book[b].type].father_type_name == _("技能")
                   and game_config.config_book_type[game_config.config_book[b].type].ability_id), None)
check("书库里有难度 3 的技能书", _hard_book is not None)
if _hard_book is not None:
    cache.rhodes_island.book_borrow_dict[_hard_book] = -1
    _hard_ability = game_config.config_book_type[game_config.config_book[_hard_book].type].ability_id
    _hard_level = _reader.ability.get(_hard_ability, 0)
    _reader.ability[_hard_ability] = 0
    check("只剩一本能力不够读的书：不成立（与 check_random_borrow_book 的筛选同口径）", not schedule_handle.judge_personal_course_valid(201, read_course))
    _reader.ability[_hard_ability] = 6
    check("能力够了：成立", schedule_handle.judge_personal_course_valid(201, read_course))
    _reader.ability[_hard_ability] = _hard_level
check("判定不写数据：没借书、书库借出状态没被改", not _reader.entertainment.borrow_book_id_set and all(v != 201 for v in cache.rhodes_island.book_borrow_dict.values()))
cache.rhodes_island.book_borrow_dict.update(_saved_borrow)
schedule_handle.clear_selected_course(201, _wd, 0)
clear_schedules()

section("Plan 31 §3.8（L4）：取数口 get_course_at 只对学生岗生效；§3.10（L6）：教师反查只认教师岗")
clear_schedules()
set_time(period_time(0))
_wd = cache.game_time.weekday()
_today = cache.game_time.date().toordinal()
growth_handle.get_child_growth(201).selected_course = {}
schedule_handle.set_class_cell(ROOM1, _wd, 0, 45, 101)
schedule_handle.set_class_cell(ROOM1, _wd, 1, 43, 101)
schedule_handle.set_selected_course(201, _wd, 0, education_constant.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_selected_course(201, _wd, 1, education_constant.COURSE_TYPE_THEORY, ROOM1)
schedule_handle.set_selected_course(201, _wd, 2, education_constant.COURSE_TYPE_PE, _("木桩房"))
sex_class_handle.set_temp_class(_today, 3, ROOM_P, 70, must_attend=[201])
_must_course = schedule_handle.get_course_at(201, period_time(3), 3)
check("L4 对照：学生岗时本节的教室课、个人式课、点名必修的覆盖都取得到",
      schedule_handle.get_now_course(201) is not None and schedule_handle.get_course_at(201, period_time(2), 2) is not None
      and _must_course is not None and _must_course["classroom"] == ROOM_P, _must_course)
_before_period_1 = period_time(1) - datetime.timedelta(minutes=10)
set_time(_before_period_1)
_upcoming = schedule_handle.get_upcoming_course(201)
check("L4 对照：开课前 10 分钟，get_upcoming_course 取得到下一节", _upcoming is not None and _upcoming["period"] == 1, _upcoming)
student.work.work_type = 21
check("L4 改了岗（岗位 21）：马上开始的下一节为 None", schedule_handle.get_upcoming_course(201) is None)
set_time(period_time(0))
check("L4 改了岗：get_now_course 与各节的 get_course_at 都为 None（此前按残留的课表判在上课，<课> 与 CVP 跟着错）",
      schedule_handle.get_now_course(201) is None and schedule_handle.get_course_at(201, period_time(0), 0) is None
      and schedule_handle.get_course_at(201, period_time(2), 2) is None)
check("L4 改了岗：点名必修的覆盖同样不再生效（必修名单只收学生岗）", schedule_handle.get_course_at(201, period_time(3), 3) is None)
check("L4 取数口只读：个人课表原样保留", schedule_handle.get_selected_course(201, _wd, 0) == [education_constant.COURSE_TYPE_THEORY, ROOM1])
student.work.work_type = 152
check("L4 改回学生岗：恢复", schedule_handle.get_now_course(201) is not None and schedule_handle.get_course_at(201, period_time(3), 3) is not None)
check("L6 对照：教师岗时教师反查生效、本节取得到授课格", schedule_handle.judge_schedule_teacher(101) and schedule_handle.get_now_teaching(101) is not None)
set_time(_before_period_1)
_upcoming_teaching = schedule_handle.get_upcoming_teaching(101)
check("L6 对照：开课前 10 分钟，get_upcoming_teaching 取得到下一节", _upcoming_teaching is not None and _upcoming_teaching["period"] == 1, _upcoming_teaching)
teacher.work.work_type = 152
check("L6 前教师改当学生：get_upcoming_teaching 为 None", schedule_handle.get_upcoming_teaching(101) is None)
set_time(period_time(0))
check("L6 前教师改当学生：教师反查失效、get_now_teaching 为 None（此前 CVP 与 561 先按她旧的授课格取课）",
      not schedule_handle.judge_schedule_teacher(101) and schedule_handle.get_now_teaching(101) is None)
check("L6 全局课表的格子原样保留：get_teacher_cell 照查得到、撞课判定照旧（面板据此标「已离岗」）",
      schedule_handle.get_teacher_cell(101, _wd, 0) == (ROOM1, 45) and schedule_handle.judge_teacher_conflict(101, _wd, 0, ROOM2) != "")
teacher.work.work_type = 151
check("L6 改回教师岗：恢复", schedule_handle.get_now_teaching(101) is not None)
sex_class_handle.set_temp_class(_today, 0, ROOM_P, 70)
move_to(0, schedule_handle.get_classroom_position(ROOM_P))
check("L6 玩家不看岗位（岗位为 0）：人在当天临时课的教室里照常取得到授课",
      pl.work.work_type != education_constant.TEACHER_WORK_TYPE and schedule_handle.judge_schedule_teacher(0) and schedule_handle.get_now_teaching(0) is not None)
move_to(0, SCENE_DORM)
check("L18 get_now_course 的返回说明写全：不在学生岗、兴趣课读书借不到书", all(k in (schedule_handle.get_now_course.__doc__ or "") for k in ("学生岗", "借不到书")))
growth_handle.get_child_growth(201).selected_course = {}
clear_schedules()

section("Plan 32 §3.13（L21）：教师候选排除被监禁的教师，一键排课不再把她排进空格子")
clear_schedules()
open_all_classroom()
check("L21 对照：两名教师岗都在候选里", sorted(schedule_handle.get_teacher_candidate_list()) == [101, 102], sorted(schedule_handle.get_teacher_candidate_list()))
teacher_b.sp_flag.imprisonment = True
check("L21 被监禁的教师不在候选里（此前在岛、在岗照列，一键排课与选教师页会把她排进空格子，关着的这段时间每节都降级自习）",
      sorted(schedule_handle.get_teacher_candidate_list()) == [101], sorted(schedule_handle.get_teacher_candidate_list()))
auto_schedule.auto_fill_class_schedule()
_l21_teacher_set = {cell[1] for week_data in cache.rhodes_island.class_schedule.values() for period_data in week_data.values() for cell in period_data.values()}
check("L21 一键排课排上的格子里没有被监禁的教师", 101 in _l21_teacher_set and 102 not in _l21_teacher_set, _l21_teacher_set)
teacher_b.sp_flag.imprisonment = False
check("L21 放出来之后回到候选名单", sorted(schedule_handle.get_teacher_candidate_list()) == [101, 102], sorted(schedule_handle.get_teacher_candidate_list()))
clear_schedules()

finish()
