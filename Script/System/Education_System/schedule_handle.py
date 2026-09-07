"""课表读写与查询（Plan 22 一期）

两层课表：
    全局课表 Rhodes_Island.class_schedule —— 只排班级式的教室课（理论/实践/公开），
        结构为 {教室场景名: {星期: {节次: [科目能力id, 授课教师id]}}}
    个人课表 Character.child_growth.selected_course —— 承载学生的选课与个人式课程
        （体育/兴趣/实习），结构为 {星期: {节次: [课型, 目标]}}

教师视角不另存字段，由全局课表反查得到，避免两处数据互相追赶。
"""
from typing import Dict, List, Optional, Tuple
from Script.Core import cache_control, game_type, constant
from Script.Config import game_config
from Script.Design import game_time, map_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

COURSE_TYPE_THEORY = 0
""" 课型：理论课（教室课，班级式） """
COURSE_TYPE_PRACTICE = 1
""" 课型：实践课（教室课，班级式） """
COURSE_TYPE_PUBLIC = 2
""" 课型：公开课（大礼堂，班级式） """
COURSE_TYPE_PE = 3
""" 课型：体育课（训练场各地点，个人式） """
COURSE_TYPE_INTEREST = 4
""" 课型：兴趣课（娱乐地点，个人式） """
COURSE_TYPE_INTERN = 5
""" 课型：实习课（干员在岗工作，个人式） """

CLASSROOM_COURSE_TYPE_SET = {COURSE_TYPE_THEORY, COURSE_TYPE_PRACTICE, COURSE_TYPE_PUBLIC}
""" 班级式课型（目标为教室场景名，科目与教师查全局课表） """

COURSE_TYPE_NAME = {
    COURSE_TYPE_THEORY: "理论课",
    COURSE_TYPE_PRACTICE: "实践课",
    COURSE_TYPE_PUBLIC: "公开课",
    COURSE_TYPE_PE: "体育课",
    COURSE_TYPE_INTEREST: "兴趣课",
    COURSE_TYPE_INTERN: "实习课",
}
""" 课型编号到中文名的映射，供面板与状态标识使用 """

CLASSROOM_TAG_BY_COURSE_TYPE = {
    COURSE_TYPE_THEORY: "Class_Room",
    COURSE_TYPE_PRACTICE: "Practice_Room",
    COURSE_TYPE_PUBLIC: "Auditorium",
}
""" 班级式课型对应的场景标签，用于列出可排课的教室 """

PE_PLACE_DATA = {
    "木桩房": ("Fight_Room", "training", 205),
    "射击房": ("Shoot_Room", "training", 205),
    "健身区": ("Gym", "exercise", 206),
    "游泳池": ("Swimming_Pool", "swimming", 161),
}
""" 体育课的四处地点（方案 §3.21）：地点名 → (场景标签, 行为en_name, 状态cid)。
    ⚠️ 用固定表而不是查配置，是因为这四处各自对应不同的既有行为，没有一张现成的表能推出来。
    模拟对战室不在其中：它的 SceneTag 只有 Room，全仓库没有任何行为挂在它上面 """

TEACHER_WORK_TYPE = 151
""" 教师岗位的工作id（WorkType.csv:24），只有该岗位的干员可被排进课表 """

STUDENT_WORK_TYPE = 152
""" 学生岗位的工作id（WorkType.csv:25） """


def get_classroom_list(course_type: int = -1) -> List[str]:
    """
    取可排课的教室场景名列表
    Keyword arguments:
    course_type -- 课型编号，-1为全部班级式课型
    Return arguments:
    List[str] -- 教室场景名列表（如["理论教室一", ...]），按场景名排序
    """
    if course_type == -1:
        tag_list = list(CLASSROOM_TAG_BY_COURSE_TYPE.values())
    elif course_type in CLASSROOM_TAG_BY_COURSE_TYPE:
        tag_list = [CLASSROOM_TAG_BY_COURSE_TYPE[course_type]]
    else:
        return []
    room_list = []
    for tag in tag_list:
        for scene_path_str in constant.place_data.get(tag, []):
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]
            room_list.append(scene_data.scene_name)
    return sorted(room_list)


def get_course_type_by_classroom(classroom: str) -> int:
    """
    按教室场景名反查它承载的班级式课型
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    int -- 课型编号，查不到则为-1
    """
    for course_type, tag in CLASSROOM_TAG_BY_COURSE_TYPE.items():
        for scene_path_str in constant.place_data.get(tag, []):
            if cache.scene_data[scene_path_str].scene_name == classroom:
                return course_type
    return -1


def get_classroom_position(classroom: str) -> List[str]:
    """
    按教室场景名取它的场景路径，供移动使用
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    List[str] -- 场景路径列表，查不到则为空列表
    """
    for tag in CLASSROOM_TAG_BY_COURSE_TYPE.values():
        for scene_path_str in constant.place_data.get(tag, []):
            if cache.scene_data[scene_path_str].scene_name == classroom:
                return map_handle.get_map_system_path_for_str(scene_path_str)
    return []


def get_class_cell(classroom: str, week_day: int, period: int) -> Optional[List[int]]:
    """
    取全局课表上的一个格子
    Keyword arguments:
    classroom -- 教室场景名
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    Return arguments:
    Optional[List[int]] -- [科目能力id, 授课教师id]，未排课则为None
    """
    # 临时性技实操课的覆盖层（Plan 22 四期 §3.28.3）：这是全局课表的唯一读取入口，
    # 在这里插一层，下游的 get_now_course / 派课 / 移动 / 课表面板 / <课>标识 就全部自动跟上
    # ⚠️ 只在查询的星期正好是今天时才覆盖——临时课程是一次性的（键含具体日期序数），
    #    不能像 class_schedule 那样每周重复上演
    if week_day == cache.game_time.weekday():
        from Script.System.Education_System import sex_class_handle

        temp_class = sex_class_handle.get_temp_class(cache.game_time.date().toordinal(), period)
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


def get_teacher_cell(teacher_id: int, week_day: int, period: int) -> Optional[Tuple[str, int]]:
    """
    反查某位教师在某节次要去哪间教室教什么（教师个人课表由全局课表反查，不另存字段）
    Keyword arguments:
    teacher_id -- 教师的角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    Return arguments:
    Optional[Tuple[str, int]] -- (教室场景名, 科目能力id)，该节次没课则为None
    """
    for classroom, week_data in cache.rhodes_island.class_schedule.items():
        cell = week_data.get(week_day, {}).get(period, None)
        if cell is not None and cell[1] == teacher_id:
            return classroom, cell[0]
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


def get_now_course(character_id: int) -> Optional[dict]:
    """
    取角色当前这一节次要上的课（Plan 22 的统一入口，供 AI、结算与 <课> 状态标识共用）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Optional[dict] -- 不在节次内或没排课时为None，否则为：
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
    week_day = now_time.weekday()
    course = get_selected_course(character_id, week_day, period)
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
    if course_type in CLASSROOM_COURSE_TYPE_SET:
        result["classroom"] = target
        cell = get_class_cell(target, week_day, period)
        if cell is not None:
            result["ability_id"] = cell[0]
            result["teacher_id"] = cell[1]
    return result


def get_now_teaching(character_id: int) -> Optional[dict]:
    """
    取角色当前这一节次要教的课（教师视角，由全局课表反查）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Optional[dict] -- 不在节次内或本节没课时为None，否则为
        {"course_type": 课型int, "classroom": 教室场景名str, "ability_id": 科目能力id int, "period": 节次int}
    """
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
        if character_data.work.work_type == TEACHER_WORK_TYPE:
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
    """
    cell = get_teacher_cell(teacher_id, week_day, period)
    if cell is not None and cell[0] != classroom:
        return "第{0}节已在{1}".format(period + 1, cell[0])
    return ""


def judge_student_conflict(character_id: int, week_day: int, period: int, target) -> str:
    """
    判断某学生在某节次是否已经选了别的课
    Keyword arguments:
    character_id -- 角色id
    week_day -- 星期，0周一~6周日
    period -- 节次，0~8
    target -- 想选的目标
    Return arguments:
    str -- 空字符串表示不冲突，否则为冲突原因文本
    """
    course = get_selected_course(character_id, week_day, period)
    if course is not None and course[1] != target:
        return "第{0}节已选{1}".format(period + 1, course[1])
    return ""


def get_intern_mentor(character_id: int, work_type_id: int) -> int:
    """
    找实习课的带教导师：此刻和自己在同一场景、且正干着这个岗位的干员
    ⚠️ 导师不预先指派（方案 §3.21 口径 53）——"实习课就是跟着目前在做这份工作的人"，
       所以只能在结算的当口按现场情况找，找不到就是无人在岗，学徒降级为见习
    Keyword arguments:
    character_id -- 学徒的角色id
    work_type_id -- 实习岗位的工作id
    Return arguments:
    int -- 导师的角色id，无人在岗则为-1
    """
    from Script.Design import map_handle

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
    List[str] -- 场景路径列表，解析不出则为空列表
    """
    from Script.Design import map_handle

    course_type = now_course["course_type"]
    # 班级式：目标就是教室名
    if course_type in CLASSROOM_COURSE_TYPE_SET:
        return get_classroom_position(now_course["classroom"])
    place_tag = ""
    # 体育课：目标是训练场的场景名，标签查固定表
    if course_type == COURSE_TYPE_PE:
        place_tag = PE_PLACE_DATA.get(now_course["target"], ("", "", 0))[0]
    # 兴趣课：目标是娱乐cid，地点标签直接读 Entertainment.csv
    elif course_type == COURSE_TYPE_INTEREST:
        if now_course["target"] in game_config.config_entertainment:
            place_tag = game_config.config_entertainment[now_course["target"]].place_tag
    # 实习课：目标是工作cid，地点标签直接读 WorkType.csv
    elif course_type == COURSE_TYPE_INTERN:
        if now_course["target"] in game_config.config_work_type:
            place_tag = game_config.config_work_type[now_course["target"]].place_tag
    if not place_tag:
        return []
    scene_list = constant.place_data.get(place_tag, [])
    if not scene_list:
        return []
    # 体育课要精确到具体那间房（木桩房与射击房同属 Training_Room）
    if course_type == COURSE_TYPE_PE:
        for scene_path_str in scene_list:
            if cache.scene_data[scene_path_str].scene_name == now_course["target"]:
                return map_handle.get_map_system_path_for_str(scene_path_str)
        return []
    # ⚠️ 实习课：同一标签下的房间并不等价，取第一间会让学徒扑空——
    #    急诊室与门诊室同属 Clinic 但坐诊医生只在门诊室；舍管房有9间各区管理员只守自己那间；
    #    射击房与木桩房、生产车间1~5 同理。
    #    所以按"谁在岗就去谁那间"优先（口径53：实习就是跟着此刻在做这份工作的人），
    #    其次取与岗位 place 同名的那间，都取不到才退回第一间
    if course_type == COURSE_TYPE_INTERN:
        work_type_id = now_course["target"]
        for scene_path_str in scene_list:
            for other_id in cache.scene_data[scene_path_str].character_list:
                if cache.character_data[other_id].work.work_type == work_type_id:
                    return map_handle.get_map_system_path_for_str(scene_path_str)
        work_place = game_config.config_work_type[work_type_id].place
        for scene_path_str in scene_list:
            if cache.scene_data[scene_path_str].scene_name == work_place:
                return map_handle.get_map_system_path_for_str(scene_path_str)
    return map_handle.get_map_system_path_for_str(scene_list[0])


_BEHAVIOR_NAME_BY_CID: Dict[int, str] = {}
""" 行为cid → en_name 的反查缓存。config_behavior 是按 en_name 索引的，没有现成的反向表 """


def get_behavior_name_by_cid(behavior_cid: int) -> str:
    """
    按行为cid反查它的en_name
    ⚠️ Entertainment.csv 的 behavior_id 列存的是行为cid，而 Character.behavior.behavior_id 存的是
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
