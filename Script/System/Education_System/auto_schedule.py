"""一键自动排课（Plan 22 一期 §9.3，兑现总纲口径 23）

口径 23 立这个功能的动机是**操作量**：全局课表是「10 教室 × 7 天 × 9 节」，
个人课表是「7 天 × 9 节 × 每个孩子」，全靠手点排不完。

本模块是纯函数层：只算与写数据，不碰任何绘制，面板只负责画按钮与报结果
（照 Dormitory_System/common.py 的 pick_dormitory_room 分层）。

排出来的课表必须是**无冲突**的。口径 29 明确「运行时不做兜错逻辑」，
   同一个教师被排进同一节次的两间教室，运行时不会有人来收拾。

结果必须**可复现**：同样的存档点两次一键，排出来的课表要一模一样。
   所以凡是遍历 set 的地方都先 sorted()——schedule_handle.get_teacher_candidate_list()
   遍历的 cache.npc_id_got 是 set，直接用会让每次排课结果都不同。
"""
from typing import Dict, List, Tuple

from Script.Core import cache_control, game_type
from Script.Design import game_time
from Script.System.Education_System import education_constant, schedule_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def get_auto_subject_list() -> List[int]:
    """
    取自动排课可用的科目列表
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 科目能力id列表，按id升序
    功能: 全部科目去掉男性专属的那些（女学生排了也吃不到加成）
    """
    # 取副本返回：调用方会按需求排序与裁剪，不能让它改到常量表本身
    return list(education_constant.FEMALE_SUBJECT_LIST)


def judge_subject_fit_classroom(ability_id: int, course_type: int) -> bool:
    """
    判断某科目适不适合排进某课型的教室
    Keyword arguments:
    ability_id -- 科目能力id
    course_type -- 课型编号
    Return arguments:
    bool -- 是否适合
    功能: 实践课只收动手类与性技（方案 §3.3），理论课与公开课来者不拒
    """
    if course_type != education_constant.COURSE_TYPE_PRACTICE:
        return True
    # 性技科目（70~77）属于「性技理论」，与动手类一并算进实践课
    return ability_id in education_constant.PRACTICE_SUBJECT_SET or ability_id >= 70


def pick_best_teacher(ability_id: int, week_day: int, period: int, classroom: str, teacher_list: List[int]) -> int:
    """
    在本节空闲的教师里挑该科目等级最高的一个
    Keyword arguments:
    ability_id -- 科目能力id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    classroom -- 教室场景名
    teacher_list -- 候选教师id列表（须已按id升序，保证并列时取id小者）
    Return arguments:
    int -- 教师角色id，一个都排不了则为-1
    """
    best_id = -1
    best_level = -1
    for teacher_id in teacher_list:
        # judge_teacher_conflict 返回的是冲突原因文本，空串才表示不冲突
        if schedule_handle.judge_teacher_conflict(teacher_id, week_day, period, classroom):
            continue
        teacher_data: game_type.Character = cache.character_data[teacher_id]
        # ability 的值可能是 float，比较前一律 int()
        now_level = int(teacher_data.ability.get(ability_id, 0))
        if now_level > best_level:
            best_level = now_level
            best_id = teacher_id
    return best_id


def auto_fill_class_schedule() -> Tuple[int, int]:
    """
    一键把全部已开放教室的空格子排满
    Keyword arguments:
    无
    Return arguments:
    Tuple[int, int] -- (新排上的格数, 因为没有空闲教师而留空的格数)
    功能: 学科均衡铺满、每格配该科等级最高且本节空闲的教师。
          只填空格，已有的排课一格都不动——所以重复点击是幂等的，不会弄丢手排内容
    """
    room_list = schedule_handle.get_classroom_list()
    if not room_list:
        return 0, 0
    # 必须 sorted：get_teacher_candidate_list 遍历的是 set，顺序不定会让结果不可复现
    teacher_list = sorted(schedule_handle.get_teacher_candidate_list())
    if not teacher_list:
        return 0, 0
    subject_list = get_auto_subject_list()
    # 先建一次映射：get_course_type_by_classroom 每次调用都全扫 place_data，
    #    在 10教室×5天×9节=450 格的循环里逐格调会很慢
    course_type_by_room: Dict[str, int] = {
        room: schedule_handle.get_course_type_by_classroom(room) for room in room_list}
    # 均衡的实现：记账每门科目已经被排了几次，每次都从排得最少的那门开始试
    used_count: Dict[int, int] = {ability_id: 0 for ability_id in subject_list}

    filled_count = 0
    skip_count = 0
    period_count = len(game_time.CLASS_PERIOD_START)
    for classroom in room_list:
        course_type = course_type_by_room.get(classroom, -1)
        fit_subject_list = [a for a in subject_list if judge_subject_fit_classroom(a, course_type)]
        if not fit_subject_list:
            continue
        for week_day in range(education_constant.AUTO_SCHEDULE_WEEK_DAY_MAX):
            for period in range(period_count):
                if schedule_handle.get_class_cell(classroom, week_day, period) is not None:
                    continue
                # 按「已排次数少→科目id小」的顺序试，第一个能配到教师的科目胜出。
                # 先定科目再找教师会白白浪费格子——某些科目全岛教师本节都占满了
                now_filled = False
                for ability_id in sorted(fit_subject_list, key=lambda a: (used_count[a], a)):
                    teacher_id = pick_best_teacher(ability_id, week_day, period, classroom, teacher_list)
                    if teacher_id == -1:
                        continue
                    schedule_handle.set_class_cell(classroom, week_day, period, ability_id, teacher_id)
                    used_count[ability_id] += 1
                    filled_count += 1
                    now_filled = True
                    break
                if not now_filled:
                    # 本节全岛教师都排满了，这一格留空。
                    # 不排「无教师自习」——玩家想要自习可以手动排，自动塞会让课表看起来排满了其实全是自习
                    skip_count += 1
    return filled_count, skip_count


def auto_fill_selected_course(character_id: int) -> Tuple[int, int]:
    """
    一键把某个孩子个人课表上的空节次选满
    Keyword arguments:
    character_id -- 孩子的角色id
    Return arguments:
    Tuple[int, int] -- (新选上的节数, 因为当节没有任何教室开课而跳过的节数)
    功能: 有课就上。同一节有多间教室开课时，选这孩子该科等级最低的那门——
          等级越低离升级越近，收益也越大（get_learn_speed 的师生等级差曲线）。
          只填空格，已有的选课一节都不动
    """
    if character_id not in cache.character_data:
        return 0, 0
    room_list = schedule_handle.get_classroom_list()
    if not room_list:
        return 0, 0
    course_type_by_room: Dict[str, int] = {
        room: schedule_handle.get_course_type_by_classroom(room) for room in room_list}
    character_data: game_type.Character = cache.character_data[character_id]

    filled_count = 0
    skip_count = 0
    period_count = len(game_time.CLASS_PERIOD_START)
    # 遍历整整7天而不是只遍历自动排课铺的5天：玩家可能手排过周末的课
    for week_day in range(education_constant.WEEK_DAY_COUNT):
        for period in range(period_count):
            if schedule_handle.get_selected_course(character_id, week_day, period) is not None:
                continue
            best_room = ""
            best_level = -1
            for classroom in room_list:
                cell = schedule_handle.get_class_cell(classroom, week_day, period)
                if cell is None:
                    continue
                now_level = int(character_data.ability.get(cell[0], 0))
                # 取等级最低的那门；并列时取教室顺序靠前的（room_list 已按理论→实践→大礼堂排好）
                if best_room == "" or now_level < best_level:
                    best_room = classroom
                    best_level = now_level
            if best_room == "":
                skip_count += 1
                continue
            schedule_handle.set_selected_course(
                character_id, week_day, period, course_type_by_room.get(best_room, -1), best_room)
            filled_count += 1
    return filled_count, skip_count
