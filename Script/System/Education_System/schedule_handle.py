"""课表读写与查询（Plan 22 一期）

两层课表：
    全局课表 Rhodes_Island.class_schedule —— 只排班级式的教室课（理论/实践/公开），
        结构为 {教室场景名: {星期: {节次: [科目能力id, 授课教师id]}}}
    个人课表 Character.child_growth.selected_course —— 承载学生的选课与个人式课程
        （体育/兴趣/实习），结构为 {星期: {节次: [课型, 目标]}}

教师视角不另存字段，由全局课表反查得到，避免两处数据互相追赶。
"""
from types import FunctionType
from typing import Dict, List, Optional, Tuple
from Script.Core import cache_control, game_type, constant, get_text
from Script.Config import game_config
from Script.Design import game_time, map_handle
from Script.System.Education_System import education_constant

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def judge_scene_open(scene_name: str) -> bool:
    """
    校验一个场景当前是否已开放（Plan 26 §3.8：由 judge_classroom_open 泛化而来，个人式课的上课地点也要查）
    Keyword arguments:
    scene_name -- 场景名
    Return arguments:
    bool -- 是否已开放
    功能: constant.place_data 装的是**全部**场景——它在配置载入期由 data/map/ 的目录树
             静态构建（map_config.load_dir_now），与存档、facility_level、facility_open 全都无关。
             所以开放与否必须另查 Rhodes_Island.facility_open，与寻路的 wait_open 判定（map_handle.judge_scene_accessible）同口径。
             理论教室一 / 实践教室一 / 大礼堂等 Lv1 基础设施压根不在 Facility_open.csv 里，
             不给它们兜底会被误判成未开放，面板直接空掉（宿舍区同样处理，见 Dormitory_System/common.py）
    """
    if scene_name not in game_config.config_facility_open_name_set:
        return True
    open_cid = game_config.config_facility_open_name_to_cid[scene_name]
    return bool(cache.rhodes_island.facility_open.get(open_cid, False))


def judge_classroom_open(classroom: str) -> bool:
    """
    校验一间教室当前是否已开放（judge_scene_open 的别名，教室列表沿用这个名字）
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    bool -- 是否已开放
    """
    return judge_scene_open(classroom)


def get_classroom_sort_key(classroom: str) -> int:
    """
    取教室名在同类教室中的排序键
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    int -- 末尾中文数字的数值（一为0、二为1……），没有中文数字后缀的排在最后
    """
    for index, word in enumerate(education_constant.CLASSROOM_NUMBER_ORDER):
        if classroom.endswith(word):
            return index
    return len(education_constant.CLASSROOM_NUMBER_ORDER)


def get_classroom_list(course_type: int = -1) -> List[str]:
    """
    取可排课的教室场景名列表
    Keyword arguments:
    course_type -- 课型编号，-1为全部班级式课型
    Return arguments:
    List[str] -- 已开放的教室场景名列表，顺序为 理论教室一~六 → 实践教室一~三 → 大礼堂
    功能: 按课型分组而不是全表 sorted()：全表排序会把三类教室混排、
             并让默认页签落在「大礼堂」上，而玩家最常用的是理论教室一
    """
    if course_type == -1:
        type_list = sorted(education_constant.CLASSROOM_TAG_BY_COURSE_TYPE.keys())
    elif course_type in education_constant.CLASSROOM_TAG_BY_COURSE_TYPE:
        type_list = [course_type]
    else:
        return []
    room_list = []
    for now_type in type_list:
        now_group = []
        for scene_path_str in constant.place_data.get(education_constant.CLASSROOM_TAG_BY_COURSE_TYPE[now_type], []):
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]
            if not judge_classroom_open(scene_data.scene_name):
                continue
            now_group.append(scene_data.scene_name)
        room_list.extend(sorted(now_group, key=get_classroom_sort_key))
    return room_list


def get_course_type_by_classroom(classroom: str) -> int:
    """
    按教室场景名反查它承载的班级式课型
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    int -- 课型编号，查不到则为-1
    """
    for course_type, tag in education_constant.CLASSROOM_TAG_BY_COURSE_TYPE.items():
        for scene_path_str in constant.place_data.get(tag, []):
            if cache.scene_data[scene_path_str].scene_name == classroom:
                return course_type
    return -1


def get_course_type_by_position(position: List[str]) -> int:
    """
    按所在位置判一节课的课型（玩家手动授课用，Plan 31 收拢）
    Keyword arguments:
    position -- 场景路径
    Return arguments:
    int -- 所在场景是理论 / 实践教室、大礼堂时为对应课型，其余一律按理论课
    功能: 玩家手动发起的授课不在课表上，结算 512 与 CVP 的回落（handle_premise.get_player_manual_teach_course）都按这里判课型，
          两处共用一个定义，口上读到的课型与实际结算不会分叉。只读
    """
    scene_path_str = map_handle.get_map_system_path_str_for_list(position)
    if scene_path_str in cache.scene_data:
        course_type = get_course_type_by_classroom(cache.scene_data[scene_path_str].scene_name)
        if course_type != -1:
            return course_type
    return education_constant.COURSE_TYPE_THEORY


def get_classroom_position(classroom: str) -> List[str]:
    """
    按教室场景名取它的场景路径，供移动使用
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    List[str] -- 场景路径列表，查不到则为空列表
    """
    for tag in education_constant.CLASSROOM_TAG_BY_COURSE_TYPE.values():
        for scene_path_str in constant.place_data.get(tag, []):
            if cache.scene_data[scene_path_str].scene_name == classroom:
                return map_handle.get_map_system_path_for_str(scene_path_str)
    return []


def get_today_temp_class(week_day: int, period: int) -> Optional[dict]:
    """
    取覆盖层要用的临时性技实操课：只在查询的星期正好是今天时才有，且已下课（ended）的不算
    Keyword arguments:
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    Return arguments:
    Optional[dict] -- 临时课程数据，没有则为None
    功能: 临时课程是一次性的（键含具体日期序数），不能像 class_schedule 那样每周重复上演，
          所以只有「今天」的那一节才覆盖；下了课的那一节交还给原来的课表（2026-09-12 第五轮），
          否则该节剩余时间里选修生会对着「授课者=玩家」空等
    """
    if week_day != cache.game_time.weekday():
        return None
    from Script.System.Education_System import sex_class_handle

    return sex_class_handle.get_active_temp_class(cache.game_time.date().toordinal(), period)


def get_class_cell(classroom: str, week_day: int, period: int, include_temp: bool = True) -> Optional[List[int]]:
    """
    取全局课表上的一个格子
    Keyword arguments:
    classroom -- 教室场景名
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    include_temp -- 是否叠加今天的临时性技实操课。要写进**每周循环**的个人课表时（一键选课、选课第一屏）
                    必须传 False，否则一次性的临时课会被当成每周固定的课选进去
    Return arguments:
    Optional[List[int]] -- [科目能力id, 授课教师id]，未排课则为None
    """
    # 临时性技实操课的覆盖层（Plan 22 四期 §3.28.3）：这是全局课表的唯一读取入口，
    # 在这里插一层，下游的 get_now_course / 派课 / 移动 / 课表面板 / <课>标识 就全部自动跟上
    if include_temp:
        temp_class = get_today_temp_class(week_day, period)
        if temp_class is not None and temp_class.get("classroom", "") == classroom:
            # 教师id为0即玩家亲自授课
            return [temp_class.get("ability_id", -1), 0]
    schedule = cache.rhodes_island.class_schedule
    return schedule.get(classroom, {}).get(week_day, {}).get(period, None)


def set_class_cell(classroom: str, week_day: int, period: int, ability_id: int, teacher_id: int) -> None:
    """
    往全局课表上排一节课
    Keyword arguments:
    classroom -- 教室场景名
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    ability_id -- 科目能力id
    teacher_id -- 授课教师的角色id，-1表示未指派教师（本节降级为自习）
    Return arguments:
    无
    """
    schedule = cache.rhodes_island.class_schedule
    schedule.setdefault(classroom, {}).setdefault(week_day, {})[period] = [ability_id, teacher_id]


def clear_class_cell(classroom: str, week_day: int, period: int) -> None:
    """
    清空全局课表上的一个格子
    Keyword arguments:
    classroom -- 教室场景名
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    Return arguments:
    无
    """
    schedule = cache.rhodes_island.class_schedule
    if classroom in schedule and week_day in schedule[classroom]:
        schedule[classroom][week_day].pop(period, None)


def get_teacher_cell(teacher_id: int, week_day: int, period: int, include_temp: bool = True) -> Optional[Tuple[str, int]]:
    """
    反查某位教师在某节次要去哪间教室教什么（教师个人课表由全局课表反查，不另存字段）
    Keyword arguments:
    teacher_id -- 教师的角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    include_temp -- 是否叠加今天的临时性技实操课。排课的撞课判定（judge_teacher_conflict）必须传 False：
                    每周课表是每周循环的，被今天的临时课顶掉的那一格下周照样要上（Plan 26 §3.6）
    Return arguments:
    Optional[Tuple[str, int]] -- (教室场景名, 科目能力id)，该节次没课则为None
    """
    # 临时性技实操课的覆盖层（Plan 22 四期），与 get_class_cell 同口径：只在查询的星期正好是今天时覆盖
    temp_class = get_today_temp_class(week_day, period) if include_temp else None
    # 授课者恒为玩家，所以查玩家时直接命中。这里不能只靠下面那个循环：临时课的教室未必在 class_schedule 里有键，
    #    玩家也从不出现在全局课表的教师位上，漏了这一层就会像 4-C 的主修口上那样"玩家永远查不到自己"
    if teacher_id == 0 and temp_class is not None:
        return temp_class.get("classroom", ""), temp_class.get("ability_id", -1)
    for classroom, week_data in cache.rhodes_island.class_schedule.items():
        cell = week_data.get(week_day, {}).get(period, None)
        if cell is None or cell[1] != teacher_id:
            continue
        # 这一格今天被临时实操课顶掉了：原来排在这里的 NPC 教师这节不用来（2026-09-12 第五轮）。
        #    不跳过的话她会按课表走进教室，在玩家的课堂 H 里原地开讲
        if temp_class is not None and temp_class.get("classroom", "") == classroom:
            continue
        return classroom, cell[0]
    return None


def judge_schedule_teacher(character_id: int) -> bool:
    """
    校验一个角色的教师反查（get_now_teaching / get_upcoming_teaching）是否生效（Plan 31 §3.10）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 玩家恒为True；NPC 只在教师岗时为True
    功能: 改了岗或离岛的教师还挂在全局课表上。运行时 class_ai.judge_teacher_available 会挡住她，学生降级自习；
             但前教师改当学生后，CVP Course / CourseType 与 561 都先问教师反查，取到的是她旧的授课格，而不是她自己的课。
          与 class_ai.get_teacher_duty 同口径。玩家的授课只来自当天的临时实操课，他从不在全局课表的教师位上，不看岗位。
          全局课表面板、撞课判定读的是 get_teacher_cell / get_teacher_week_schedule，不经过这里，照旧看得到她
    """
    if character_id == 0:
        return True
    return cache.character_data[character_id].work.work_type == education_constant.TEACHER_WORK_TYPE


def get_upcoming_teaching(character_id: int, minute_limit: int = education_constant.UPCOMING_MINUTE) -> Optional[dict]:
    """
    取教师接下来 minute_limit 分钟内要开始的那一节课（到岗时间与课间用，2026-09-12 第五轮）
    Keyword arguments:
    character_id -- 教师的角色id
    minute_limit -- 往后看多少分钟
    Return arguments:
    Optional[dict] -- 与 get_now_teaching 同结构；没有、或角色不是玩家且不在教师岗（Plan 31 §3.10）则为None
    功能: 8:40 到岗时 get_now_teaching 查不到第一节，教师若先随便去一间教室、9:00 再挪，
          第一节就会迟到；按「马上要上的那一节」提前去对的教室
    """
    import datetime

    # 教师反查只认教师岗（Plan 31 §3.10），与 get_now_teaching 同口径
    if not judge_schedule_teacher(character_id):
        return None
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    for period, (hour, minute) in enumerate(game_time.CLASS_PERIOD_START):
        start_time = now_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if start_time <= now_time:
            continue
        if start_time - now_time > datetime.timedelta(minutes=minute_limit):
            break
        cell = get_teacher_cell(character_id, now_time.weekday(), period)
        if cell is None:
            return None
        classroom, ability_id = cell
        return {
            "course_type": get_course_type_by_classroom(classroom),
            "classroom": classroom,
            "ability_id": ability_id,
            "period": period,
        }
    return None


def get_teacher_week_schedule(teacher_id: int) -> Dict[int, Dict[int, Tuple[str, int]]]:
    """
    反查某位教师的整周课表
    Keyword arguments:
    teacher_id -- 教师的角色id
    Return arguments:
    Dict[int, Dict[int, Tuple[str, int]]] -- {星期: {节次: (教室场景名, 科目能力id)}}
    """
    result: Dict[int, Dict[int, Tuple[str, int]]] = {}
    for classroom, week_data in cache.rhodes_island.class_schedule.items():
        for week_day, period_data in week_data.items():
            for period, cell in period_data.items():
                if cell[1] == teacher_id:
                    result.setdefault(week_day, {})[period] = (classroom, cell[0])
    # 玩家的周课表再并入今天的临时实操课，与 get_teacher_cell 的覆盖层保持一致（已下课的不算）
    if teacher_id == 0:
        from Script.System.Education_System import sex_class_handle

        today = cache.game_time.date().toordinal()
        for class_key, temp_class in cache.rhodes_island.temp_sex_class.items():
            date_ordinal, period = sex_class_handle.parse_class_key(class_key)
            if date_ordinal == today and not temp_class.get("ended", False):
                result.setdefault(cache.game_time.weekday(), {})[period] = (temp_class.get("classroom", ""), temp_class.get("ability_id", -1))
    return result


def get_selected_course(character_id: int, week_day: int, period: int) -> Optional[List]:
    """
    取某角色个人课表上的一个格子
    Keyword arguments:
    character_id -- 角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    Return arguments:
    Optional[List] -- [课型int, 目标]，未选课则为None
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return None
    return growth_data.selected_course.get(week_day, {}).get(period, None)


def set_selected_course(character_id: int, week_day: int, period: int, course_type: int, target) -> None:
    """
    往某角色的个人课表上填一个格子

    这里是**直接覆盖**。所以方案 §3.14 列的三类冲突里，「学生撞课」在本结构下
       根本不可能发生——一个 (星期, 节次) 只存一门课，重选即替换。
       原先为它写的 judge_student_conflict 是死代码，已删
    Keyword arguments:
    character_id -- 角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    course_type -- 课型编号0~5
    target -- 目标：班级式课为教室场景名str，体育课为训练场场景名str，兴趣课为娱乐cid int，实习课为工作cid int
    Return arguments:
    无
    """
    from Script.System.Education_System import growth_handle

    growth_data = growth_handle.get_child_growth(character_id)
    growth_data.selected_course.setdefault(week_day, {})[period] = [course_type, target]


def clear_selected_course(character_id: int, week_day: int, period: int) -> None:
    """
    清空某角色个人课表上的一个格子
    Keyword arguments:
    character_id -- 角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    Return arguments:
    无
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return
    if week_day in growth_data.selected_course:
        growth_data.selected_course[week_day].pop(period, None)


def get_period_left_minute(character_id: int, default_minute: int = game_time.CLASS_PERIOD_MINUTE) -> int:
    """
    取角色此刻所在节次还剩多少分钟（上课类行为的时长用，2026-09-12 第五轮）
    Keyword arguments:
    character_id -- 角色id
    default_minute -- 不在节次内时返回的时长
    Return arguments:
    int -- 剩余分钟数，最少1
    功能: 节次首尾相接没有课间，走班的人一迟到，照满45分钟上就会压进下一节，一节节滚下去越迟越多；
          把授课 / 听课 / 自习 / 个人式课的时长截到本节结束，下一节就能按时换教室
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    period = game_time.get_class_period_by_time(now_time)
    if period == -1:
        return default_minute
    hour, minute = game_time.CLASS_PERIOD_START[period]
    end_minute = hour * 60 + minute + game_time.CLASS_PERIOD_MINUTE
    return max(1, end_minute - (now_time.hour * 60 + now_time.minute))


def get_now_course(character_id: int) -> Optional[dict]:
    """
    取角色当前这一节次要上的课（Plan 22 的统一入口，供 AI、结算与 <课> 状态标识共用）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Optional[dict] -- 不在节次内、角色不在学生岗（Plan 31 §3.8）、没排课、班级式课那一格已停课（全局课表空着，Plan 27）、
        或个人式课这一节上不成（场所未开放、兴趣课条件不符，Plan 28；兴趣课读书借不到书，Plan 29）时为None，否则为：
        {"course_type": 课型int, "target": 目标, "period": 节次int, "week_day": 星期int,
         "classroom": 教室场景名str（仅班级式课）, "ability_id": 科目能力id int（仅班级式课，-1为未知）,
         "teacher_id": 授课教师id int（仅班级式课，-1为无教师即自习）}
    """
    period = game_time.get_class_period(character_id)
    if period == -1:
        return None
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    return get_course_at(character_id, now_time, period)


def get_upcoming_course(character_id: int, minute_limit: int = education_constant.UPCOMING_MINUTE) -> Optional[dict]:
    """
    取学生接下来 minute_limit 分钟内要开始的那一节课（到岗时间与课间用）
    Keyword arguments:
    character_id -- 角色id
    minute_limit -- 往后看多少分钟
    Return arguments:
    Optional[dict] -- 与 get_now_course 同结构，窗口内没有节次开始、或那一节没排课则为None
    功能: 2026-09-12 第五轮为到岗时间（8:40~9:00、13:40~14:00）而加：学生岗不走工作链，没人再把她们送去第一节课的教室。
          Plan 25 起节次内也看下一节，与教师的 get_upcoming_teaching 同口径：没课的节次里在娱乐的学生，下一节开课前也要先去上课地点。
          调用方都只在本节没课（get_now_course 为 None）时才问它，不会用下一节顶掉本节的课。
          参照时刻一律取角色的行为开始时刻（Plan 25 初稿为打断规则留的 now_time 参数从未被用上，Plan 26 删去）
    """
    import datetime

    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    for period, (hour, minute) in enumerate(game_time.CLASS_PERIOD_START):
        start_time = now_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if start_time <= now_time:
            continue
        if start_time - now_time > datetime.timedelta(minutes=minute_limit):
            return None
        return get_course_at(character_id, start_time, period)
    return None


def get_course_at(character_id: int, now_time, period: int) -> Optional[dict]:
    """
    取角色在某一天某一节要上的课（get_now_course / get_upcoming_course 的共用实现）
    Keyword arguments:
    character_id -- 角色id
    now_time -- 那一节所在的时刻（取它的日期与星期）
    period -- 节次0~8
    Return arguments:
    Optional[dict] -- 结构见 get_now_course；角色不在学生岗（Plan 31 §3.8）、没排课、班级式课的全局课表那一格已停课、
        或个人式课这一节上不成（Plan 28）则为None
    """
    # 课表只对学生岗生效（Plan 24 口径 1），取数口在这里统一收窄（Plan 31 §3.8）：
    #    改了岗的女儿课表还残留着。此前 <课> 标识的个人式课分支、CVP Course / CourseType 按残留的课表判「在上课」——
    #    改任厨师的女儿在厨房上班，每逢残留的「实习：厨师」节次都显示在上课（实习地点按谁在岗取，连她自己也算）。
    #    下游（561 的学生分支、548 的计出勤、552 的实习课、实习导师认学徒）一并跟上；
    #    get_course_stage、judge_selected_cell_real 等已有的岗位判断保留，冗余无害。
    #    点名必修的覆盖也在这之后：必修名单只收学生岗，名单开出后改了岗的，不再被带去实操教室
    if cache.character_data[character_id].work.work_type != education_constant.STUDENT_WORK_TYPE:
        return None
    week_day = now_time.weekday()
    course = get_selected_course(character_id, week_day, period)
    # 被玩家点名必修的性技实操课优先于她自己的课表（口径 60「无论原本排了什么都来」，2026-09-12 第五轮）：
    #    预到岗只把人带到教室门口，一开课上课判定读的是个人课表，不在这里改写的话她会走回原来的课，
    #    本节没排课的则交回 AI 去娱乐。改在这一处，派课 / 移动 / <课>标识 / 前提就全部跟上
    temp_class = get_today_temp_class(week_day, period) if now_time.date() == cache.game_time.date() else None
    if temp_class is not None and character_id in temp_class.get("must_attend", []):
        temp_classroom = temp_class.get("classroom", "")
        course = [get_course_type_by_classroom(temp_classroom), temp_classroom]
    if course is None:
        return None
    course_type, target = course[0], course[1]
    result = {
        "course_type": course_type,
        "target": target,
        "period": period,
        "week_day": week_day,
        "classroom": "",
        "ability_id": -1,
        "teacher_id": -1,
    }
    # 班级式课：科目与教师要到全局课表里查，学生只记了"这节去哪间教室"
    if course_type in education_constant.CLASSROOM_COURSE_TYPE_SET:
        cell = get_class_cell(target, week_day, period)
        # 全局课表那一格（含当天临时课的覆盖层）空着，就是这一节停课了，视为没课（Plan 27 §3.3，用户拍板）：
        #    个人课表面板上这种格子写的是「已停课」，此前却照样判成有课——学生去空教室自习，还按「有课」记一节出勤。
        #    必修生覆盖与预约在每周课表空格上的实操课不受影响：覆盖层给出的格子非空；
        #    教师来不了（格子在、教师为 -1 或缺席）也不受影响，仍是一节课，降级自习并计出勤
        if cell is None:
            return None
        result["classroom"] = target
        result["ability_id"] = cell[0]
        result["teacher_id"] = cell[1]
    # 个人式课（体育/兴趣/实习）这一节上不成——场所未开放、或兴趣课的活动条件不符（孩子长大了、复制来的课表）——
    #    同样视为没课（Plan 28 §3.2，与上面的已停课同一口径）。此前只有「在 / 不在上课地点」两行交回既有 AI，
    #    体力闸与心情闸照样按有课判：记一节缺课、翘课，日程自习还多记一节出勤，幼女这一节也不见学。
    #    必修覆盖不受影响（覆盖后是教室课）；实习课本节无人在岗时地点仍解析得出，照旧是一节课、降级见习
    elif not judge_personal_course_valid(character_id, result):
        return None
    return result


def get_now_teaching(character_id: int) -> Optional[dict]:
    """
    取角色当前这一节次要教的课（教师视角，由全局课表反查）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Optional[dict] -- 角色不是玩家且不在教师岗（Plan 31 §3.10）、不在节次内或本节没课时为None，否则为
        {"course_type": 课型int, "classroom": 教室场景名str, "ability_id": 科目能力id int, "period": 节次int}
    """
    # 教师反查只认教师岗（Plan 31 §3.10）：前教师改当学生后，CVP 与 561 不再按她旧的授课格取课，改按她自己的课表
    if not judge_schedule_teacher(character_id):
        return None
    period = game_time.get_class_period(character_id)
    if period == -1:
        return None
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    cell = get_teacher_cell(character_id, now_time.weekday(), period)
    if cell is None:
        return None
    classroom, ability_id = cell
    # 玩家的授课只来自当天的临时实操课（他从不出现在全局课表的教师位上）：人不在那间教室时，
    #    此刻的手动授课与那节课无关，不能把那门性技当成本节科目（Plan 26 §3.7）
    if character_id == 0:
        now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        if now_scene_str not in cache.scene_data or cache.scene_data[now_scene_str].scene_name != classroom:
            return None
    return {
        "course_type": get_course_type_by_classroom(classroom),
        "classroom": classroom,
        "ability_id": ability_id,
        "period": period,
    }


def get_teacher_candidate_list() -> List[int]:
    """
    取可被排进课表的教师候选列表（只有教师岗位的干员，不做临时调度）
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表
    """
    result = []
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        if character_data.work.work_type == education_constant.TEACHER_WORK_TYPE:
            result.append(character_id)
    return result


def judge_teacher_conflict(teacher_id: int, week_day: int, period: int, classroom: str) -> str:
    """
    判断把某教师排进某格子会不会与他已有的课撞车（排课冲突在面板上直接阻止，不留到运行时兜错）
    Keyword arguments:
    teacher_id -- 教师的角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    classroom -- 想排入的教室场景名
    Return arguments:
    str -- 空字符串表示不冲突，否则为冲突原因文本
    功能: 照每周课表判，不叠加今天的临时实操课（Plan 26 §3.6）：被临时课顶掉的教师今天不用来，
          但每周课表里她这一节仍排在那间教室，别处再排她就是撞课
    """
    cell = get_teacher_cell(teacher_id, week_day, period, include_temp=False)
    if cell is not None and cell[0] != classroom:
        return _("第{0}节已在{1}").format(period + 1, cell[0])
    return ""


def get_intern_mentor(character_id: int, work_type_id: int) -> int:
    """
    找实习课的带教导师：此刻和自己在同一场景、且正干着这个岗位的干员
    导师不预先指派（方案 §3.21 口径 53）——"实习课就是跟着目前在做这份工作的人"，
       所以只能在结算的当口按现场情况找，找不到就是无人在岗，学徒降级为见习
    Keyword arguments:
    character_id -- 学徒的角色id
    work_type_id -- 实习岗位的工作id
    Return arguments:
    int -- 导师的角色id，无人在岗则为-1
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if scene_path_str not in cache.scene_data:
        return -1
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for other_id in scene_data.character_list:
        if other_id == character_id:
            continue
        other_data: game_type.Character = cache.character_data[other_id]
        if other_data.work.work_type == work_type_id:
            return other_id
    return -1


def get_course_place(now_course: dict) -> List[str]:
    """
    取一节课该去的场景路径（六种课型统一入口，供AI与状态机共用）
    Keyword arguments:
    now_course -- get_now_course() 的返回值
    Return arguments:
    List[str] -- 场景路径列表，解析不出（含场所未开放，Plan 26 §3.8）则为空列表
    """
    course_type = now_course["course_type"]
    # 班级式：目标就是教室名
    if course_type in education_constant.CLASSROOM_COURSE_TYPE_SET:
        return get_classroom_position(now_course["classroom"])
    place_tag = ""
    # 体育课：目标是训练场的场景名，标签查固定表
    if course_type == education_constant.COURSE_TYPE_PE:
        place_tag = education_constant.PE_PLACE_DATA.get(now_course["target"], ("", "", 0))[0]
    # 兴趣课：目标是娱乐cid，地点标签直接读 Entertainment.csv
    elif course_type == education_constant.COURSE_TYPE_INTEREST:
        if now_course["target"] in game_config.config_entertainment:
            place_tag = game_config.config_entertainment[now_course["target"]].place_tag
    # 实习课：目标是工作cid，地点标签直接读 WorkType.csv
    elif course_type == education_constant.COURSE_TYPE_INTERN:
        if now_course["target"] in game_config.config_work_type:
            place_tag = game_config.config_work_type[now_course["target"]].place_tag
    if not place_tag:
        return []
    scene_list = constant.place_data.get(place_tag, [])
    if not scene_list:
        return []
    # 体育课要精确到具体那间房（木桩房与射击房同属 Training_Room）；那间房还没开放就解析不出（Plan 26 §3.8）
    if course_type == education_constant.COURSE_TYPE_PE:
        for scene_path_str in scene_list:
            scene_name = cache.scene_data[scene_path_str].scene_name
            if scene_name == now_course["target"]:
                if not judge_scene_open(scene_name):
                    return []
                return map_handle.get_map_system_path_for_str(scene_path_str)
        return []
    # 实习课：同一标签下的房间并不等价，取第一间会让学徒扑空——
    #    急诊室与门诊室同属 Clinic 但坐诊医生只在门诊室；舍管房有9间各区管理员只守自己那间；
    #    射击房与木桩房、生产车间1~5 同理。
    #    所以按"谁在岗就去谁那间"优先（口径53：实习就是跟着此刻在做这份工作的人，有人在岗的房间自然已开放），
    #    其次取与岗位 place 同名且已开放的那间，都取不到才退回第一间已开放的
    if course_type == education_constant.COURSE_TYPE_INTERN:
        work_type_id = now_course["target"]
        for scene_path_str in scene_list:
            for other_id in cache.scene_data[scene_path_str].character_list:
                if cache.character_data[other_id].work.work_type == work_type_id:
                    return map_handle.get_map_system_path_for_str(scene_path_str)
        work_place = game_config.config_work_type[work_type_id].place
        for scene_path_str in scene_list:
            if cache.scene_data[scene_path_str].scene_name == work_place and judge_scene_open(work_place):
                return map_handle.get_map_system_path_for_str(scene_path_str)
    # 兴趣课与实习课的回落：取第一间已开放的。整组都没开放（咖啡馆、温室之类还没建）就解析不出，
    #    交回既有 AI（Plan 24 §3.7），不再派人走到门口、因寻路 wait_open 一分钟一分钟地空转（Plan 26 §3.8）
    for scene_path_str in scene_list:
        if judge_scene_open(cache.scene_data[scene_path_str].scene_name):
            return map_handle.get_map_system_path_for_str(scene_path_str)
    return []


def judge_course_need_pass(character_id: int, course: dict) -> bool:
    """
    校验这名学生满不满足一节课的活动条件（Plan 26 §3.8）
    Keyword arguments:
    character_id -- 角色id
    course -- get_now_course() / get_course_at() 的返回值
    Return arguments:
    bool -- 是否满足；只有兴趣课有条件（娱乐的 need 列），其余课型恒为 True
    功能: 兴趣课的目标是一项娱乐，娱乐自带 need（如过家家限幼女 / 萝莉）。个人课表面板不让选条件不符的，
          但课表写好之后孩子会长大、会换岗，残留的格子要在上课判定里再挡一次，否则 716 照常执行
    """
    if course["course_type"] != education_constant.COURSE_TYPE_INTEREST:
        return True
    from Script.System.Education_System import schedule_template_handle

    return schedule_template_handle.judge_activity_need_pass(character_id, course["target"])


def judge_personal_course_real(character_id: int, course: dict) -> bool:
    """
    校验一节个人式课（体育/兴趣/实习）是不是确有的课：兴趣课的活动条件相符、上课地点解析得出（Plan 30 §3.6）
    Keyword arguments:
    character_id -- 角色id
    course -- 课程dict，至少含 course_type 与 target
    Return arguments:
    bool -- 是否确有
    功能: 与 judge_personal_course_valid 的区别只在不看读书课此刻借不借得到书——那是一时的状态，
          必修名单的「*会顶替」与「有课」「同班同学」前提看的是排在课表上的那节课本身，不该随书库借没借空忽隐忽现。只读不写
    """
    return judge_course_need_pass(character_id, course) and bool(get_course_place(course))


def judge_personal_course_valid(character_id: int, course: dict) -> bool:
    """
    校验一节个人式课（体育/兴趣/实习）这名学生上不上得成（Plan 28 §3.2）
    Keyword arguments:
    character_id -- 角色id
    course -- 课程dict，至少含 course_type 与 target，结构见 get_now_course
    Return arguments:
    bool -- 兴趣课的活动条件相符、上课地点解析得出（含场所已开放）、兴趣课读书借得到书为True
    功能: get_course_at 判不过就视为没课。
          只读不写，前提路径上可以调用。实习课本节无人在岗时地点仍解析得出（回落到已开放的那间），照旧算一节课。
          兴趣课的行为是读书时再要求借得到书（手上有借着的书，或书库里有没被借走、读得了、没读完的书，Plan 29 §3.2）：
             借不到书的这一节视为没课，与 Plan 28 的口径相同；真正借书在状态机 716 里做，这里一行都不写。
          必修名单的「*会顶替」、「有课」「同班同学」看的是排在课表上的那节课本身，改用不看借书的 judge_personal_course_real（Plan 30）
    """
    if not judge_personal_course_real(character_id, course):
        return False
    if judge_interest_course_is_read_book(course):
        # UI 层模块，顶层 import 会成环，照现有写法延迟
        from Script.UI.Panel import borrow_book_panel

        return borrow_book_panel.judge_can_get_read_book(character_id)
    return True


def judge_interest_course_is_read_book(course: dict) -> bool:
    """
    校验一节课是不是行为为读书的兴趣课（Plan 29 §3.2）
    按 Entertainment.csv 的 behavior_id 反查行为名与 READ_BOOK 比对，不写死娱乐编号
    Keyword arguments:
    course -- 课程dict，至少含 course_type 与 target
    Return arguments:
    bool -- 是否为读书兴趣课
    """
    if course.get("course_type") != education_constant.COURSE_TYPE_INTEREST:
        return False
    target = course.get("target")
    if target not in game_config.config_entertainment:
        return False
    return get_behavior_name_by_cid(game_config.config_entertainment[target].behavior_id) == constant.Behavior.READ_BOOK


_BEHAVIOR_NAME_BY_CID: Dict[int, str] = {}
""" 行为cid → en_name 的反查缓存。config_behavior 是按 en_name 索引的，没有现成的反向表 """


def get_behavior_name_by_cid(behavior_cid: int) -> str:
    """
    按行为cid反查它的en_name
    Entertainment.csv 的 behavior_id 列存的是行为cid，而 Character.behavior.behavior_id 存的是
       en_name 字符串，两者之间需要这一层转换
    Keyword arguments:
    behavior_cid -- 行为cid
    Return arguments:
    str -- 行为的en_name，查不到则为空字符串
    """
    if not _BEHAVIOR_NAME_BY_CID:
        for en_name in game_config.config_behavior:
            _BEHAVIOR_NAME_BY_CID[game_config.config_behavior[en_name].cid] = en_name
    return _BEHAVIOR_NAME_BY_CID.get(behavior_cid, "")
