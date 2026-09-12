from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def add_premise(premise: str) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        # 直接注册原函数：原先的 return_wrapper 只做纯转发，
        # 每次前提判定都要白付一层函数调用（热路径每百tick百万次级），故移除
        constant.handle_premise_data[premise] = func
        return func

    return decoraror


@add_premise(constant_promise.Premise.HAVE_WORK)
def handle_have_work(character_id: int) -> int:
    """
    自己有工作
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type > 0


@add_premise(constant_promise.Premise.TARGET_HAVE_WORK)
def handle_t_have_work(character_id: int) -> int:
    """
    交互对象有工作
    have_work 判的是行为发起者自己，跟随母亲见学一类「按对方岗位分差分」的口上
       必须用本前提，否则读到的是孩子自己那个恒为真的152学生岗（Plan 22 二期）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_have_work(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HAVE_WORK)
def handle_t_not_have_work(character_id: int) -> int:
    """
    交互对象没有工作
    与 t_have_work 成对，专供「对方没有工作」那一侧的口上做排他
       —— 口上是加权随机不是最具体独占，不写反向前提的那一档会在两种情形下都出场
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_have_work(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_POWER_OPERATOR)
def handle_work_is_power_operator(character_id: int) -> int:
    """
    自己的工作为供能调控员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 11


@add_premise(constant_promise.Premise.TARGET_WORK_IS_POWER_OPERATOR)
def handle_t_work_is_power_operator(character_id: int) -> int:
    """
    交互对象的工作为供能调控员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_power_operator(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_MAINTENANCE_ENGINEER)
def handle_work_is_maintenance_engineer(character_id: int) -> int:
    """
    自己的工作为检修工程师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 21


@add_premise(constant_promise.Premise.TARGET_WORK_IS_MAINTENANCE_ENGINEER)
def handle_t_work_is_maintenance_engineer(character_id: int) -> int:
    """
    交互对象的工作为检修工程师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_maintenance_engineer(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_BLACKSMITH)
def handle_work_is_blacksmith(character_id: int) -> int:
    """
    自己的工作为铁匠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 22


@add_premise(constant_promise.Premise.TARGET_WORK_IS_BLACKSMITH)
def handle_t_work_is_blacksmith(character_id: int) -> int:
    """
    交互对象的工作为铁匠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_blacksmith(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_DOCTOR)
def handle_work_is_doctor(character_id: int) -> int:
    """
    自己的工作为坐诊医生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 61


@add_premise(constant_promise.Premise.TARGET_WORK_IS_DOCTOR)
def handle_t_work_is_doctor(character_id: int) -> int:
    """
    交互对象的工作为坐诊医生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_doctor(character_data.target_character_id)

@add_premise(constant_promise.Premise.WORK_IS_HOSPITAL_DOCTOR)
def handle_work_is_hospital_doctor(character_id: int) -> int:
    """
    自己的工作为住院医生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 62

@add_premise(constant_promise.Premise.TARGET_WORK_IS_HOSPITAL_DOCTOR)
def handle_t_work_is_hospital_doctor(character_id: int) -> int:
    """
    交互对象的工作为住院医生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_hospital_doctor(character_data.target_character_id)

@add_premise(constant_promise.Premise.WORK_IS_HR)
def handle_work_is_hr(character_id: int) -> int:
    """
    自己的工作为人事
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 71


@add_premise(constant_promise.Premise.TARGET_WORK_IS_HR)
def handle_t_work_is_hr(character_id: int) -> int:
    """
    交互对象的工作为人事
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_hr(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_LIBRARY_MANAGER)
def handle_work_is_library_manager(character_id: int) -> int:
    """
    自己的工作为图书馆管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 101


@add_premise(constant_promise.Premise.TARGET_WORK_IS_LIBRARY_MANAGER)
def handle_t_work_is_library_manager(character_id: int) -> int:
    """
    交互对象的工作为图书馆管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_library_manager(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_RESOURCE_TRADER)
def handle_work_is_resource_trader(character_id: int) -> int:
    """
    自己的工作为资源交易员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 111


@add_premise(constant_promise.Premise.TARGET_WORK_IS_RESOURCE_TRADER)
def handle_t_work_is_resource_trader(character_id: int) -> int:
    """
    交互对象的工作为资源交易员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_resource_trader(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_TEACHER)
def handle_work_is_teacher(character_id: int) -> int:
    """
    自己的工作为教师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 151


@add_premise(constant_promise.Premise.TARGET_WORK_IS_TEACHER)
def handle_t_work_is_teacher(character_id: int) -> int:
    """
    交互对象的工作为教师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_teacher(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_STUDENT)
def handle_work_is_student(character_id: int) -> int:
    """
    自己的工作为学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 152


@add_premise(constant_promise.Premise.TARGET_WORK_IS_STUDENT)
def handle_t_work_is_student(character_id: int) -> int:
    """
    交互对象的工作为学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_student(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_NURSERY_WORKER)
def handle_work_is_nursery_worker(character_id: int) -> int:
    """
    自己的工作为保育员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 153


@add_premise(constant_promise.Premise.TARGET_WORK_IS_NURSERY_WORKER)
def handle_t_work_is_nursery_worker(character_id: int) -> int:
    """
    交互对象的工作为保育员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_nursery_worker(character_data.target_character_id)


# ---------------------------------------------------------------------------
# 教师 / 学生的工作链前提（Plan 24，target.csv 组 07 教师 / 组 08 学生）
# 状态一律从 class_ai.get_teacher_duty / get_course_stage 取，保证同组的行两两互斥；非本岗一律返回 0。
# 同一个前提在一次决策里按名缓存、被多行共享，这里只读不写
# ---------------------------------------------------------------------------


@add_premise(constant_promise.Premise.TEACHER_HAVE_CLASS_NOW)
def handle_teacher_have_class_now(character_id: int) -> int:
    """
    自己是教师且本节有课要教（全局课表反查，含当天临时课覆盖层，不看星期）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_teacher_duty(character_id)[0] == education_constant.TEACHER_DUTY_NOW)


@add_premise(constant_promise.Premise.TEACHER_HAVE_UPCOMING_CLASS)
def handle_teacher_have_upcoming_class(character_id: int) -> int:
    """
    自己是教师，本节没课但20分钟内开始的下一节有课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_teacher_duty(character_id)[0] == education_constant.TEACHER_DUTY_UPCOMING)


@add_premise(constant_promise.Premise.TEACHER_NO_CLASS_DUTY)
def handle_teacher_no_class_duty(character_id: int) -> int:
    """
    自己是教师，本节与20分钟内都没课
    get_teacher_duty 对非教师也返回 NONE，所以必须先判岗位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.TEACHER_WORK_TYPE:
        return 0
    return int(class_ai.get_teacher_duty(character_id)[0] == education_constant.TEACHER_DUTY_NONE)


@add_premise(constant_promise.Premise.TEACHER_IN_DUTY_CLASSROOM)
def handle_teacher_in_duty_classroom(character_id: int) -> int:
    """
    自己是教师，本节或20分钟内有课，且人在该课的教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    duty, classroom = class_ai.get_teacher_duty(character_id)
    if duty == education_constant.TEACHER_DUTY_NONE:
        return 0
    return int(class_ai.judge_in_scene(character_id, classroom))


@add_premise(constant_promise.Premise.TEACHER_NOT_IN_DUTY_CLASSROOM)
def handle_teacher_not_in_duty_classroom(character_id: int) -> int:
    """
    自己是教师，本节或20分钟内有课，但人不在该课的教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    duty, classroom = class_ai.get_teacher_duty(character_id)
    if duty == education_constant.TEACHER_DUTY_NONE:
        return 0
    return int(not class_ai.judge_in_scene(character_id, classroom))


@add_premise(constant_promise.Premise.SELF_SEX_CLASS_PENDING)
def handle_self_sex_class_pending(character_id: int) -> int:
    """
    自己是学生，下一节是自己要上的性技实操课（必修或选修）且10分钟内开始
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_course_stage(character_id) == education_constant.COURSE_STAGE_SEX_PENDING)


@add_premise(constant_promise.Premise.SELF_IN_PENDING_SEX_CLASS_ROOM)
def handle_self_in_pending_sex_class_room(character_id: int) -> int:
    """
    自己是学生，有待赴的性技实操课且人已在那间教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai

    classroom = class_ai.get_pending_sex_classroom(character_id)
    if not classroom:
        return 0
    return int(class_ai.judge_in_scene(character_id, classroom))


@add_premise(constant_promise.Premise.SELF_NOT_IN_PENDING_SEX_CLASS_ROOM)
def handle_self_not_in_pending_sex_class_room(character_id: int) -> int:
    """
    自己是学生，有待赴的性技实操课但人不在那间教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai

    classroom = class_ai.get_pending_sex_classroom(character_id)
    if not classroom:
        return 0
    return int(not class_ai.judge_in_scene(character_id, classroom))


@add_premise(constant_promise.Premise.SELF_COURSE_ABSENT_BY_HP)
def handle_self_course_absent_by_hp(character_id: int) -> int:
    """
    自己是学生，本节有课但体力低于30%且不是必修实操课（本节缺课）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_course_stage(character_id) == education_constant.COURSE_STAGE_ABSENT_HP)


@add_premise(constant_promise.Premise.SELF_COURSE_SKIP)
def handle_self_course_skip(character_id: int) -> int:
    """
    自己是学生，本节有课且不是必修实操课，今日已翘课或本节掷中翘课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_course_stage(character_id) == education_constant.COURSE_STAGE_SKIP)


@add_premise(constant_promise.Premise.SELF_COURSE_ATTEND)
def handle_self_course_attend(character_id: int) -> int:
    """
    自己是学生，本节有课且照常上课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_course_stage(character_id) == education_constant.COURSE_STAGE_ATTEND)


@add_premise(constant_promise.Premise.SELF_COURSE_UPCOMING)
def handle_self_course_upcoming(character_id: int) -> int:
    """
    自己是学生，不在节次内且20分钟内开始的那一节有课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant

    return int(class_ai.get_course_stage(character_id) == education_constant.COURSE_STAGE_UPCOMING)


@add_premise(constant_promise.Premise.SELF_COURSE_IS_CLASSROOM)
def handle_self_course_is_classroom(character_id: int) -> int:
    """
    自己是学生，本节的课是班级式教室课（理论/实践/公开）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import education_constant, schedule_handle

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return 0
    now_course = schedule_handle.get_now_course(character_id)
    return int(now_course is not None and now_course["course_type"] in education_constant.CLASSROOM_COURSE_TYPE_SET)


@add_premise(constant_promise.Premise.SELF_COURSE_IS_PERSONAL)
def handle_self_course_is_personal(character_id: int) -> int:
    """
    自己是学生，本节的课是个人式课（体育/兴趣/实习）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import education_constant, schedule_handle

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return 0
    now_course = schedule_handle.get_now_course(character_id)
    return int(now_course is not None and now_course["course_type"] not in education_constant.CLASSROOM_COURSE_TYPE_SET)


@add_premise(constant_promise.Premise.SELF_IN_COURSE_PLACE)
def handle_self_in_course_place(character_id: int) -> int:
    """
    自己是学生，人在本节（节次外为马上开始的那一节）的上课地点
    地点解析不出时与 self_not_in_course_place 同为 0，没有行命中，交回既有 AI（Plan 24 §3.7）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design import map_handle
    from Script.System.Education_System import class_ai, education_constant

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return 0
    to_place = class_ai.get_course_place_now_or_upcoming(character_id)
    if not to_place:
        return 0
    return int(map_handle.get_map_system_path_str_for_list(character_data.position) == map_handle.get_map_system_path_str_for_list(to_place))


@add_premise(constant_promise.Premise.SELF_NOT_IN_COURSE_PLACE)
def handle_self_not_in_course_place(character_id: int) -> int:
    """
    自己是学生，上课地点可解析但人不在那里
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design import map_handle
    from Script.System.Education_System import class_ai, education_constant

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return 0
    to_place = class_ai.get_course_place_now_or_upcoming(character_id)
    if not to_place:
        return 0
    return int(map_handle.get_map_system_path_str_for_list(character_data.position) != map_handle.get_map_system_path_str_for_list(to_place))


@add_premise(constant_promise.Premise.SELF_COURSE_TEACHER_AVAILABLE)
def handle_self_course_teacher_available(character_id: int) -> int:
    """
    自己是学生，本节是教室课且授课教师能到岗
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant, schedule_handle

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return 0
    now_course = schedule_handle.get_now_course(character_id)
    if now_course is None or now_course["course_type"] not in education_constant.CLASSROOM_COURSE_TYPE_SET:
        return 0
    return int(class_ai.judge_teacher_available(now_course["teacher_id"]))


@add_premise(constant_promise.Premise.SELF_COURSE_TEACHER_UNAVAILABLE)
def handle_self_course_teacher_unavailable(character_id: int) -> int:
    """
    自己是学生，本节是教室课但授课教师来不了（或课表没排教师）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Education_System import class_ai, education_constant, schedule_handle

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return 0
    now_course = schedule_handle.get_now_course(character_id)
    if now_course is None or now_course["course_type"] not in education_constant.CLASSROOM_COURSE_TYPE_SET:
        return 0
    return int(not class_ai.judge_teacher_available(now_course["teacher_id"]))


@add_premise(constant_promise.Premise.NURSERY_HAVE_WORK_TO_DO)
def handle_nursery_have_work_to_do(character_id: int) -> int:
    """
    育儿室有保育工作可做（所在场景有持可鉴定卵的角色，或存在孵化中的卵，或所在场景有婴儿）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Pregnancy_System import egg_handle
    from Script.Design import map_handle
    character_data: game_type.Character = cache.character_data[character_id]
    # 所在场景有持可鉴定卵的角色（含自己）
    if egg_handle.find_identifiable_egg_owner_in_scene(character_id) != -1:
        return 1
    # 存在孵化中的卵（受精卵均存放于育儿室）
    if egg_handle.any_hatching_eggs_exist():
        return 1
    # 所在场景有婴儿
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        if chara_id and cache.character_data[chara_id].talent[101]:
            return 1
    return 0


@add_premise(constant_promise.Premise.WORK_IS_COMBAT_TRAINING)
def handle_work_is_combat_training(character_id: int) -> int:
    """
    自己的工作为训练学员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 91


@add_premise(constant_promise.Premise.TARGET_WORK_IS_COMBAT_TRAINING)
def handle_t_work_is_combat_training(character_id: int) -> int:
    """
    交互对象的工作为训练学员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_combat_training(character_data.target_character_id)   


@add_premise(constant_promise.Premise.WORK_IS_FITNESS_TRAINER)
def handle_work_is_fitness_trainer(character_id: int) -> int:
    """
    自己的工作为健身锻炼员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 92


@add_premise(constant_promise.Premise.TARGET_WORK_IS_FITNESS_TRAINER)
def handle_t_work_is_fitness_trainer(character_id: int) -> int:
    """
    交互对象的工作为健身锻炼员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_fitness_trainer(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_COOK)
def handle_work_is_cook(character_id: int) -> int:
    """
    自己的工作为厨师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 51

@add_premise(constant_promise.Premise.TARGET_WORK_IS_COOK)
def handle_t_work_is_cook(character_id: int) -> int:
    """
    交互对象的工作为厨师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_cook(character_data.target_character_id)

@add_premise(constant_promise.Premise.WORK_IS_PRODUCTION_WORKER)
def handle_work_is_production_worker(character_id: int) -> int:
    """
    自己的工作为生产工人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 121

@add_premise(constant_promise.Premise.TARGET_WORK_IS_PRODUCTION_WORKER)
def handle_t_work_is_production_worker(character_id: int) -> int:
    """
    交互对象的工作为生产工人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_production_worker(character_data.target_character_id)

@add_premise(constant_promise.Premise.WORK_IS_MASSAGE_THERAPIST)
def handle_work_is_massage_therapist(character_id: int) -> int:
    """
    自己的工作为按摩师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 171


@add_premise(constant_promise.Premise.TARGET_WORK_IS_MASSAGE_THERAPIST)
def handle_t_work_is_massage_therapist(character_id: int) -> int:
    """
    交互对象的工作为按摩师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_massage_therapist(character_data.target_character_id)

@add_premise(constant_promise.Premise.WORK_IS_DIPLOMAT)
def handle_work_is_diplomat(character_id: int) -> int:
    """
    自己的工作为外交官
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 131


@add_premise(constant_promise.Premise.TARGET_WORK_IS_DIPLOMAT)
def handle_t_work_is_diplomat(character_id: int) -> int:
    """
    交互对象的工作为外交官
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_diplomat(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_INVITATION_COMMISSIONER)
def handle_work_is_invitation_commissioner(character_id: int) -> int:
    """
    自己的工作为邀请专员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 132


@add_premise(constant_promise.Premise.TARGET_WORK_IS_INVITATION_COMMISSIONER)
def handle_t_work_is_invitation_commissioner(character_id: int) -> int:
    """
    交互对象的工作为邀请专员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_invitation_commissioner(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_MEDICINAL_PLANTER)
def handle_work_is_medicinal_planter(character_id: int) -> int:
    """
    自己的工作为药材种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 161


@add_premise(constant_promise.Premise.TARGET_WORK_IS_MEDICINAL_PLANTER)
def handle_t_work_is_medicinal_planter(character_id: int) -> int:
    """
    交互对象的工作为药材种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_medicinal_planter(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_FLORAL_PLANTER)
def handle_work_is_floral_planter(character_id: int) -> int:
    """
    自己的工作为花草种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 162


@add_premise(constant_promise.Premise.TARGET_WORK_IS_FLORAL_PLANTER)
def handle_t_work_is_floral_planter(character_id: int) -> int:
    """
    交互对象的工作为花草种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_floral_planter(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_SEX_TRAINEE)
def handle_work_is_sex_trainee(character_id: int) -> int:
    """
    自己的工作为性爱练习生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 193


@add_premise(constant_promise.Premise.TARGET_WORK_IS_SEX_TRAINEE)
def handle_t_work_is_sex_trainee(character_id: int) -> int:
    """
    交互对象的工作为性爱练习生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_sex_trainee(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_WARDEN)
def handle_work_is_warden(character_id: int) -> int:
    """
    自己的工作为监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 191


@add_premise(constant_promise.Premise.T_WORK_IS_WARDEN)
def handle_t_work_is_warden(character_id: int) -> int:
    """
    交互对象的工作为监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_warden(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_WORK_IS_NOT_WARDEN)
def handle_t_work_is_not_warden(character_id: int) -> int:
    """
    交互对象的工作不是监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_work_is_warden(character_data.target_character_id)

@add_premise(constant_promise.Premise.WORK_IS_DORMITORY_MANAGER)
def handle_work_is_dormitory_manager(character_id: int) -> int:
    """
    自己的工作为宿舍管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 31

@add_premise(constant_promise.Premise.TARGET_WORK_IS_DORMITORY_MANAGER)
def handle_t_work_is_dormitory_manager(character_id: int) -> int:
    """
    交互对象的工作为宿舍管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_dormitory_manager(character_data.target_character_id)

@add_premise(constant_promise.Premise.HAVE_WARDEN)
def handle_have_warden(character_id: int) -> int:
    """
    当前有监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.current_warden_id


@add_premise(constant_promise.Premise.HAVE_NO_PATIENT_NEED_SURGERY)
def handle_have_no_patient_need_surgery(character_id: int) -> int:
    """
    自身没有需要进行手术的患者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.surgery_patient_id == 0

@add_premise(constant_promise.Premise.HAVE_PATIENT_NEED_SURGERY)
def handle_have_patient_need_surgery(character_id: int) -> int:
    """
    自身有需要进行手术的患者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_have_no_patient_need_surgery(character_id)

@add_premise(constant_promise.Premise.DORMITORY_MANAGER_ACTION_0)
def handle_dormitory_manager_action_0(character_id: int) -> int:
    """
    自身宿舍管理员行动阶段_到岗整理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.dormitory_admin_phase == 0

@add_premise(constant_promise.Premise.DORMITORY_MANAGER_ACTION_1)
def handle_dormitory_manager_action_1(character_id: int) -> int:
    """
    自身宿舍管理员行动阶段_移动处理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.dormitory_admin_phase == 1

@add_premise(constant_promise.Premise.PATIENT_WAIT)
def handle_patient_wait(character_id: int) -> int:
    """
    有患者正等待就诊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Medical_System import medical_constant
    waiting_states = medical_constant.WAITING_QUEUE_STATE_SET
    # 计算等待就诊的患者数量
    waiting_count = sum(
        1
        for patient in cache.rhodes_island.medical_patients_today.values()
        if patient.state in waiting_states
    )
    if waiting_count > 0:
        return 1
    return 0

@add_premise(constant_promise.Premise.MEDICAL_WARD_WAIT)
def handle_medical_ward_wait(character_id: int) -> int:
    """
    有住院患者需要照护
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    hospitalized = getattr(cache.rhodes_island, "medical_hospitalized", {})
    if hospitalized:
        return 1
    return 0


@add_premise(constant_promise.Premise.MEDICAL_SURGERY_WAIT)
def handle_medical_surgery_wait(character_id: int) -> int:
    """
    有住院患者等待手术
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.System.Medical_System import medical_constant
    hospitalized = getattr(cache.rhodes_island, "medical_hospitalized", {})
    if not hospitalized:
        return 0
    for patient in hospitalized.values():
        if getattr(patient, "state", None) != medical_constant.MedicalPatientState.HOSPITALIZED:
            continue
        if getattr(patient, "need_surgery", False) and not getattr(patient, "surgery_blocked", False):
            return 1
    return 0

@add_premise(constant_promise.Premise.HAVE_PATIENT_NEED_SURGERY_AND_CAN_DO)
def handle_have_patient_need_surgery_and_can_do(character_id: int) -> int:
    """
    有住院患者等待手术且满足进行的条件
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 先判断有没有患者等待手术
    if not handle_medical_surgery_wait(character_id):
        return 0

    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return 0

    from Script.System.Medical_System import hospital_doctor_service

    # 获取所有可进行手术的患者列表
    available_patients_list = hospital_doctor_service.get_surgery_candidate_patient_ids(
        doctor_character=character_data,
        target_base=cache.rhodes_island,
    )
    return len(available_patients_list)

@add_premise(constant_promise.Premise.NEW_NPC_WAIT)
def handle_new_npc_wait(character_id: int) -> int:
    """
    有已招募待确认的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.rhodes_island.recruited_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_OFFICE_WORK_NEED_TO_DO)
def handle_have_office_work_need_to_do(character_id: int) -> int:
    """
    有需要处理的公务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.office_work > 0


@add_premise(constant_promise.Premise.NOT_HAVE_OFFICE_WORK_NEED_TO_DO)
def handle_not_have_office_work_need_to_do(character_id: int) -> int:
    """
    没有需要处理的公务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_have_office_work_need_to_do(character_id)


@add_premise(constant_promise.Premise.PINK_CERTIFICATE_G_10)
def handle_pink_certificate_g_10(character_id: int) -> int:
    """
    拥有粉红凭证数量大于10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.materials_resouce[4] > 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.PRISONER_IN_CUSTODY)
def handle_prisoner_in_custody(character_id: int) -> int:
    """
    当前有关押的囚犯
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.rhodes_island.current_prisoners):
        return 1
    return 0


@add_premise(constant_promise.Premise.PRISONER_DAILY_MANAGEMENT_SET)
def handle_prisoner_daily_management_set(character_id: int) -> int:
    """
    已设定对囚犯的日常管理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.confinement_training_setting[1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_INTERN_STUDENT)
def handle_have_intern_student(character_id: int) -> int:
    """
    校验此刻同场景有人正在自己这个岗位上实习（Plan 22 §3.21 的带教侧）
    这是 schedule_handle.get_intern_mentor() 的反向查询：学徒侧靠它找导师，
       导师侧靠本前提知道自己身边有人在跟岗。两边读的是同一份判据，不会出现单向成立
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design import map_handle
    from Script.System.Education_System import education_constant, schedule_handle

    character_data: game_type.Character = cache.character_data[character_id]
    work_type_id = character_data.work.work_type
    if not work_type_id:
        return 0
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if scene_path_str not in cache.scene_data:
        return 0
    for other_id in cache.scene_data[scene_path_str].character_list:
        if other_id == character_id:
            continue
        other_data: game_type.Character = cache.character_data[other_id]
        if other_data.behavior.behavior_id != constant.Behavior.INTERN_CLASS:
            continue
        now_course = schedule_handle.get_now_course(other_id)
        if now_course is None:
            continue
        if now_course["course_type"] == education_constant.COURSE_TYPE_INTERN and now_course["target"] == work_type_id:
            return 1
    return 0


@add_premise(constant_promise.Premise.NOT_HAVE_INTERN_STUDENT)
def handle_not_have_intern_student(character_id: int) -> int:
    """
    校验此刻同场景没有人在自己这个岗位上实习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_have_intern_student(character_id):
        return 0
    return 1
