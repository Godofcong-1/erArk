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
from Script.System.Education_System import education_constant

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def judge_classroom_open(classroom: str) -> bool:
    """
    校验一间教室当前是否已开放
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    bool -- 是否已开放
    功能: ⚠️ constant.place_data 装的是**全部**教室——它在配置载入期由 data/map/ 的目录树
             静态构建（map_config.load_dir_now），与存档、facility_level、facility_open 全都无关。
             所以开放与否必须另查 Rhodes_Island.facility_open。
          ⚠️ 理论教室一 / 实践教室一 / 大礼堂 是 Lv1 基础设施，压根不在 Facility_open.csv 里，
             不给它们兜底会被误判成未开放，面板直接空掉（宿舍区同样处理，见 Dormitory_System/common.py）
    """
    if classroom not in game_config.config_facility_open_name_set:
        return True
    open_cid = game_config.config_facility_open_name_to_cid[classroom]
    return bool(cache.rhodes_island.facility_open.get(open_cid, False))


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
    功能: ⚠️ 按课型分组而不是全表 sorted()：全表排序会把三类教室混排、
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

    ⚠️ 这里是**直接覆盖**。所以方案 §3.14 列的三类冲突里，「学生撞课」在本结构下
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
    if course_type in education_constant.CLASSROOM_COURSE_TYPE_SET:
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
    """
    cell = get_teacher_cell(teacher_id, week_day, period)
    if cell is not None and cell[0] != classroom:
        return "第{0}节已在{1}".format(period + 1, cell[0])
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
    # 体育课要精确到具体那间房（木桩房与射击房同属 Training_Room）
    if course_type == education_constant.COURSE_TYPE_PE:
        for scene_path_str in scene_list:
            if cache.scene_data[scene_path_str].scene_name == now_course["target"]:
                return map_handle.get_map_system_path_for_str(scene_path_str)
        return []
    # ⚠️ 实习课：同一标签下的房间并不等价，取第一间会让学徒扑空——
    #    急诊室与门诊室同属 Clinic 但坐诊医生只在门诊室；舍管房有9间各区管理员只守自己那间；
    #    射击房与木桩房、生产车间1~5 同理。
    #    所以按"谁在岗就去谁那间"优先（口径53：实习就是跟着此刻在做这份工作的人），
    #    其次取与岗位 place 同名的那间，都取不到才退回第一间
    if course_type == education_constant.COURSE_TYPE_INTERN:
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
