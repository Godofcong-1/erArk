"""性技实操课（课堂 H 模式）的核心逻辑（Plan 22 四期 §3.28）

性技实操课是一种**带课堂语境的特殊 H 模式**：玩家作为授课者站在实践教室或大礼堂里，
对到场的学生做实操教学。它与普通群交的区别只有三条，其余全部复用群交的模板机制：

    1. 口上差分 —— 课堂 H 的文本与普通群交完全不同（"讲解示范"而不是"欲望宣泄"）
    2. 前提区分 —— "在上课"与"在群交"要能分开判
    3. 结算差分 —— 课堂 H 要给学生加主修科目经验、给旁观者发观摩收益、记出勤

开课时必须**同时**置 `cache.group_sex_mode = True`：群交模板面板、射精面板、Web 状态栏
   等十余处读取点判的都是那个标志，只置 sex_class_mode 的话整个模板界面都不会出现。

两种发起方式在数据上是**统一的**——当场开课也会创建一条 temp_sex_class 条目并置 running，
只是它的 notified 三项直接标记为已发（当场开课不需要提醒自己）。这样下游的主修加成、
旁观结算、下课流程只有一条代码路径。
"""
import datetime
import random
from types import FunctionType
from typing import Optional, List, Tuple

from Script.Core import cache_control, game_type, get_text
from Script.Design import game_time, map_handle
from Script.System.Education_System import education_constant, growth_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

# ---------------------------------------------------------------------------
# 临时课程的存取
# ---------------------------------------------------------------------------


def get_class_key(date_ordinal: int, period: int) -> str:
    """
    拼出临时课程的字典键
    Keyword arguments:
    date_ordinal -- 日期序数（datetime.date.toordinal()）
    period -- 节次0~8，不在节次内时为-1
    Return arguments:
    str -- 形如"739510-3"的键
    """
    return "%d-%d" % (date_ordinal, period)


def parse_class_key(class_key: str) -> tuple:
    """
    把临时课程的字典键拆回日期序数与节次
    Keyword arguments:
    class_key -- 形如"739510-3"或"739510--1"的键
    Return arguments:
    tuple -- (日期序数int, 节次int)，解析失败为(-1, -1)
    """
    parts = class_key.split("-", 1)
    if len(parts) != 2 or not parts[0].isdigit():
        return -1, -1
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return -1, -1


def get_temp_class(date_ordinal: int, period: int) -> Optional[dict]:
    """
    取某天某节次的临时性技实操课
    Keyword arguments:
    date_ordinal -- 日期序数
    period -- 节次
    Return arguments:
    Optional[dict] -- 课程数据，没有则为None
    """
    return cache.rhodes_island.temp_sex_class.get(get_class_key(date_ordinal, period), None)


def get_active_temp_class(date_ordinal: int, period: int) -> Optional[dict]:
    """
    取某天某节次**还没下课**的临时性技实操课（课表覆盖层与必修判定用）
    Keyword arguments:
    date_ordinal -- 日期序数
    period -- 节次
    Return arguments:
    Optional[dict] -- 课程数据，没有或已下课（ended）则为None
    功能: 预约的那节课下课后条目要留到跨天清理（提醒标记、口上分档都读它），
          但覆盖层与必修判定不能再认它，否则该节剩余时间里全员对着「授课者=玩家」空等（2026-09-12 第五轮）
    """
    temp_class = get_temp_class(date_ordinal, period)
    if temp_class is None or temp_class.get("ended", False):
        return None
    return temp_class


def set_temp_class(date_ordinal: int, period: int, classroom: str, ability_id: int, must_attend: Optional[List[int]] = None, running: bool = False, notified: Optional[list] = None) -> dict:
    """
    排一节临时性技实操课（已存在则覆盖）
    Keyword arguments:
    date_ordinal -- 日期序数
    period -- 节次
    classroom -- 教室场景名
    ability_id -- 主修的性技科目能力id
    must_attend -- 必修学生的角色id列表
    running -- 是否立刻标记为进行中（当场开课为True）
    notified -- 三次提醒的已发标记，None时按running决定
    Return arguments:
    dict -- 新建的课程数据
    """
    if must_attend is None:
        must_attend = []
    if notified is None:
        # 当场开课不需要提醒玩家自己，三项直接标记为已发
        notified = [running, running, running]
    now_data = {
        "classroom": classroom,
        "ability_id": ability_id,
        "must_attend": list(must_attend),
        "notified": notified,
        "running": running,
        # 是否是预约排进课表的那节：开课时由 start_sex_class 按"复用了已有条目"来定，供开课口上分档
        "reserved": False,
    }
    cache.rhodes_island.temp_sex_class[get_class_key(date_ordinal, period)] = now_data
    return now_data


def del_temp_class(date_ordinal: int, period: int) -> None:
    """
    删掉一节临时性技实操课
    Keyword arguments:
    date_ordinal -- 日期序数
    period -- 节次
    Return arguments:
    无
    """
    cache.rhodes_island.temp_sex_class.pop(get_class_key(date_ordinal, period), None)


def get_running_class() -> Optional[dict]:
    """
    取当前正在进行的那节实操课
    Keyword arguments:
    无
    Return arguments:
    Optional[dict] -- 课程数据，没有在进行的则为None
    """
    for now_data in cache.rhodes_island.temp_sex_class.values():
        if now_data.get("running", False):
            return now_data
    return None


def get_running_class_key() -> str:
    """
    取当前正在进行的那节实操课的字典键（供判断提前/按时/拖堂用）
    Keyword arguments:
    无
    Return arguments:
    str -- 字典键，没有在进行的则为空串
    """
    for now_key, now_data in cache.rhodes_island.temp_sex_class.items():
        if now_data.get("running", False):
            return now_key
    return ""


def get_scene_name(scene_path: list) -> str:
    """
    取场景路径对应的场景名（教室名）
    Keyword arguments:
    scene_path -- 场景路径
    Return arguments:
    str -- 场景名，路径不是真实场景时为空串
    """
    scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
    if scene_path_str not in cache.scene_data:
        return ""
    return cache.scene_data[scene_path_str].scene_name


def find_reserved_class(classroom: str, now_time: datetime.datetime) -> Tuple[str, Optional[dict]]:
    """
    在今天的临时课里找这间教室等着开讲的那节预约（Plan 26 §3.5）
    Keyword arguments:
    classroom -- 教室场景名
    now_time -- 参照时刻
    Return arguments:
    Tuple[str, Optional[dict]] -- (字典键, 课程数据)，没有则为 ("", None)
    功能: 只认这间教室、还没开讲（不在 running）、没下过课（不带 ended）的条目，
             且要么就是当前节次，要么开始时刻在 NOTIFY_BEFORE_MINUTE 分钟之内；当前节次优先，其次取开始最早的一节。
          学生按设计在开课前 PRE_ARRIVE_MINUTE 分钟就到场，玩家这时开课正落在上一节（或午休、早上的 -1），
             只按「当前节次」找会取不到预约：另开一节当场课、重问主修、必修生被晾在一边、按时下课被判拖堂
    """
    if not classroom:
        return "", None
    today = now_time.date().toordinal()
    now_period = game_time.get_class_period_by_time(now_time)
    best_key = ""
    best_class = None
    best_start = None
    for class_key, class_data in cache.rhodes_island.temp_sex_class.items():
        date_ordinal, period = parse_class_key(class_key)
        if date_ordinal != today or class_data.get("classroom", "") != classroom:
            continue
        if class_data.get("running", False) or class_data.get("ended", False):
            continue
        # 就是当前这一节：直接取
        if period != -1 and period == now_period:
            return class_key, class_data
        # 还没到点、但半小时内就开始的那节
        start_time = get_period_start_time(date_ordinal, period)
        if start_time is None or start_time <= now_time:
            continue
        if start_time - now_time > datetime.timedelta(minutes=education_constant.NOTIFY_BEFORE_MINUTE):
            continue
        if best_start is None or start_time < best_start:
            best_key, best_class, best_start = class_key, class_data, start_time
    return best_key, best_class


def find_class_to_start(classroom: str, now_time: datetime.datetime) -> Tuple[str, Optional[dict]]:
    """
    取玩家此刻在这间教室开课时要沿用的临时课条目（开课结算与开课指令预读主修共用）
    Keyword arguments:
    classroom -- 教室场景名
    now_time -- 参照时刻
    Return arguments:
    Tuple[str, Optional[dict]] -- (字典键, 课程数据)，都没有时为 ("", None)，由调用方新建当场课
    功能: 先找等着开讲的预约（find_reserved_class，含提前几分钟开讲的）；
          找不到时，当前节次这间教室若已有条目（同一节里下课后又开一次），沿用它，开课时清掉已下课标记
    """
    class_key, class_data = find_reserved_class(classroom, now_time)
    if class_data is not None:
        return class_key, class_data
    today = now_time.date().toordinal()
    period = game_time.get_class_period_by_time(now_time)
    class_data = get_temp_class(today, period)
    if class_data is not None and classroom and class_data.get("classroom", "") == classroom:
        return get_class_key(today, period), class_data
    return "", None


def clean_expired_temp_class() -> int:
    """
    清理过期的临时课程条目（跨天结算时调用）

    必须跳过 running 为真的那条：口径68允许无限拖堂，一节课可以从昨天一直上到今天，
       跨天时若把正在上的这节删掉，下课时就找不到课程数据了。
    Keyword arguments:
    无
    Return arguments:
    int -- 清理掉的条目数
    """
    today = cache.game_time.date().toordinal()
    del_key_list = []
    for now_key, now_data in cache.rhodes_island.temp_sex_class.items():
        if now_data.get("running", False):
            continue
        date_ordinal, _period = parse_class_key(now_key)
        if date_ordinal != -1 and date_ordinal < today:
            del_key_list.append(now_key)
    for now_key in del_key_list:
        del cache.rhodes_island.temp_sex_class[now_key]
    return len(del_key_list)


# ---------------------------------------------------------------------------
# 谁能参加
# ---------------------------------------------------------------------------


def judge_has_sex_skill_course(character_id: int) -> bool:
    """
    判断某角色的个人课表里有没有排过性技科目的教室课（方案 §3.28.7 旁路守卫第3层「前置修习」，宽松版）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否排过
    功能: 口径 63 要求「学生须已选修对应性技科目的理论课」，让实操课成为理论课的下游而不是替代品。
          2026-09-12 第五轮按宽松版实装：只要个人课表里有任一班级式课格、在全局课表上排的是性技科目就算，
             不要求与本节主修科目对上——当场开课时「场景里有没有能来的学生」要在选主修科目之前就判出来。
          查全局课表时不叠加临时课覆盖层：被临时实操课顶掉的那一格不能反过来证明她修过性技理论
    """
    from Script.System.Education_System import schedule_handle

    if character_id not in cache.character_data:
        return False
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None:
        return False
    for week_day, day_data in growth_data.selected_course.items():
        for period, course in day_data.items():
            if course[0] not in education_constant.CLASSROOM_COURSE_TYPE_SET:
                continue
            cell = schedule_handle.get_class_cell(course[1], week_day, period, include_temp=False)
            if cell is not None and cell[0] in education_constant.SEX_SKILL_SUBJECT_SET:
                return True
    return False


def get_must_attend_set(classroom: str = "") -> set:
    """
    取此刻这节实操课的必修名单
    Keyword arguments:
    classroom -- 教室场景名。给了就取这间教室等着开讲的那节预约（find_reserved_class，Plan 26 §3.5）；
                 不给时取今天当前节次还没下课的临时课
    Return arguments:
    set -- 必修学生的角色id集合，没有则为空集
    功能: 正在进行的那节优先。开课前取场景学生名单时要传教室名：学生开课前 10 分钟就到场了，
          此时按「当前节次」取到的是上一节，必修生会被当成没修过性技课漏掉
    """
    now_class = get_running_class()
    if now_class is None:
        if classroom:
            now_class = find_reserved_class(classroom, cache.game_time)[1]
        else:
            now_class = get_active_temp_class(cache.game_time.date().toordinal(), game_time.get_class_period_by_time(cache.game_time))
    if now_class is None:
        return set()
    return set(now_class.get("must_attend", []))


def judge_can_join_sex_class(character_id: int, check_course: bool = True) -> bool:
    """
    判断某角色能不能被拉进课堂H模式（方案 §3.28.7 的旁路守卫第2、3层）

    只收学生岗（Plan 26 §3.10）；学生岗的孩子（玩家的女儿）零门槛——她是玩家自己养的、课是玩家自己排的，两道决策已经做过了；
    成年干员没有这层前置，仍需满足既有的「H模式」实行值（InstructJudge.csv:10，S 350），
    否则这条无实行值要求的入口就成了绕过全部既有H前提的旁路。
    第3层「前置修习」对两者都生效：个人课表里要排过性技科目的教室课（judge_has_sex_skill_course）；
       玩家点名的必修生由调用方传 check_course=False 豁免——点名本身就是玩家的决定
    Keyword arguments:
    character_id -- 角色id
    check_course -- 是否检查前置修习
    Return arguments:
    bool -- 是否可参加
    """
    from Script.Design import instuct_judege
    from Script.Design import handle_premise

    if character_id == 0 or character_id not in cache.character_data:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return False
    # 课堂 H 只收学生岗（Plan 26 §3.10，Plan 24 口径 1「课表只对学生岗生效」的延伸）：改了岗的女儿人在教室也不拉进来。
    #    开课拉人、旁观名单、开课后到场的 JOIN、课堂模式下的邀请都经这里，一并收紧；必修名单本来就只列学生岗
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return False
    # 状态异常的不拉进来：2临盆/产后/监禁、5意识模糊、6意识不清、7离线（外勤/婴儿/外交访问/逃跑）
    # 刻意**不查 4（服装异常）**：课上到一半学生本来就被脱光了，把它算进来会让这份名单
    #    在开课瞬间清空，旁观名单跟着变空，观摩收益整个失效
    for normal_id in (2, 5, 6, 7):
        if not getattr(handle_premise, "handle_normal_%d" % normal_id)(character_id):
            return False
    if character_data.sp_flag.imprisonment:
        return False
    # 前置修习（第3层）：没排过性技科目教室课的不能来，必修生豁免
    if check_course and not judge_has_sex_skill_course(character_id):
        return False
    # 孩子零门槛
    if character_data.relationship.father_id == 0:
        return True
    # 成年干员仍走既有的H模式实行值
    return bool(instuct_judege.calculation_instuct_judege(0, character_id, _("H模式"), not_draw_flag=True)[0])


def get_scene_student_list(scene_path: Optional[list] = None) -> List[int]:
    """
    取某场景内所有可参加实操课的学生

    这是「在场需要有至少一个学生」这条开课前提的取值来源，也是开课时把谁拉进模式的名单。
    Keyword arguments:
    scene_path -- 场景路径，None时取玩家所在场景
    Return arguments:
    List[int] -- 可参加的角色id列表（不含玩家自己）
    """
    if scene_path is None:
        scene_path = cache.character_data[0].position
    scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
    if scene_path_str not in cache.scene_data:
        return []
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 必修名单上的人豁免前置修习：玩家点名要她来，她就算没排过性技理论课也照样上。
    #    传这间教室的名字：开课前取的是这间教室等着开讲的那节预约（Plan 26 §3.5）
    must_attend_set = get_must_attend_set(scene_data.scene_name)
    return [cid for cid in scene_data.character_list if cid and judge_can_join_sex_class(cid, check_course=cid not in must_attend_set)]


def get_selected_student_list(classroom: str, week_day: int, period: int) -> List[int]:
    """
    取选修了这一节次这间教室的学生

    这是排课面板上"本节有 N 名学生会来"那一行的取值来源，**必显示**：
       选课逻辑零改动的代价就是可能一个人都不来——学生的个人课表存的是"这一节去哪间教室"，
       教室里的内容换成性技实操课后她照旧走进来，但没人选这间教室时排了也是空教室。
       玩家必须在排课当场就看得到这个数。
    只收学生岗（Plan 28 §3.4）：课表只对学生岗生效（Plan 24 口径 1），改了岗的女儿课表里还留着这一格，
       但她上课状态恒为 NONE、也进不了课堂（judge_can_join_sex_class 同口径），算进来「会来」的人数就虚高了
    Keyword arguments:
    classroom -- 教室场景名
    week_day -- 星期0~6
    period -- 节次0~8
    Return arguments:
    List[int] -- 选修者的角色id列表
    """
    from Script.System.Education_System import schedule_handle

    result = []
    for character_id in sorted(cache.npc_id_got):
        if cache.character_data[character_id].work.work_type != education_constant.STUDENT_WORK_TYPE:
            continue
        course = schedule_handle.get_selected_course(character_id, week_day, period)
        if course is None:
            continue
        if course[0] in education_constant.CLASSROOM_COURSE_TYPE_SET and course[1] == classroom:
            result.append(character_id)
    return result


def get_date_ordinal_by_week_day(week_day: int, period: int) -> int:
    """
    把课表上的"星期几"换算成最近一个还没过去的具体日期

    临时课程是一次性的（键含具体日期序数），而课表面板的格子是按星期排的，
    所以要在这里把"周三第3节"落到某个具体的哪一天。
    必须按**游戏时钟真正会走到的日子**逐日往后数（2026-09-12 第五轮）：一年只有 3/6/9/12 四个季月，
       季月最后一天的下一天是下个季月的 1 日（如 9/30 → 12/1），星期也跟着跳。按日历直接加天数
       会落到 10 月 2 日这种时钟永远不会走到的日子上，那节课永远不会开、提醒也永远不会发
    Keyword arguments:
    week_day -- 星期0~6
    period -- 节次0~8
    Return arguments:
    int -- 日期序数
    """
    # 从今天的 0 点开始逐日步进；get_predict_date 会把落进非季月的日期归到下个季月的 1 日
    now_date = cache.game_time.replace(hour=0, minute=0, second=0, microsecond=0)
    # 就是今天、但这一节的开始时刻已经过去了，就从明天开始找
    start_time = get_period_start_time(now_date.toordinal(), period)
    if start_time is not None and start_time <= cache.game_time:
        now_date = game_time.get_predict_date(1, now_date)
    # 两周内必然能找到对应的星期（跨季月时星期会跳，给足余量）
    for _index in range(14):
        if now_date.weekday() == week_day:
            break
        now_date = game_time.get_predict_date(1, now_date)
    return now_date.date().toordinal()


def judge_in_sex_class_place(character_id: int) -> bool:
    """
    判断角色是否位于可上实操课的场所（实践教室或大礼堂）

    两条场景前提都是一期建的，这里只是取或，不新增判定。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否在实践教室或大礼堂
    """
    from Script.Design import handle_premise

    if handle_premise.handle_in_practice_room(character_id):
        return True
    return bool(handle_premise.handle_in_auditorium(character_id))


# ---------------------------------------------------------------------------
# 主修科目与加成
# ---------------------------------------------------------------------------


def get_now_class_ability() -> int:
    """
    取当前正在上的这节实操课的主修科目能力id
    Keyword arguments:
    无
    Return arguments:
    int -- 能力id，不在实操课中则为-1
    """
    now_class = get_running_class()
    if now_class is None:
        return -1
    return now_class.get("ability_id", -1)


def judge_in_running_class(character_id: int) -> bool:
    """
    判断角色此刻是否正身处那节在进行的实操课

    授课者恒为玩家（口径38），所以玩家只要有课在进行就算；学生则看人在不在本节课的那间教室——
    不能只看「有课在进行」，否则同一时刻在别的教室上普通课的孩子也会被算成在上实操课。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否正在这节实操课里
    """
    now_class = get_running_class()
    if now_class is None:
        return False
    if character_id == 0:
        return True
    # 场景名比对复用 class_ai 的既有写法，不在这里另写一份
    from Script.System.Education_System import class_ai

    return class_ai.judge_in_scene(character_id, now_class.get("classroom", ""))


def get_now_bonus_exp_id() -> int:
    """
    取当前实操课主修科目对应的经验id

    映射不硬编码：一期的 growth_handle.get_subject_exp_id() 从 AbilityUp.csv 的升级需求串里
       解出，七门性技各自解出的经验id互不重叠（指技70→手交41 / 舌技71→口交42 / 足技72→足交44 /
       胸技73→乳交43 / 膣技74→阴道性交61 / 肛技75→肛肠性交62 / 榨精77→精液24）。
       AbilityUp.csv 是唯一真相源，不在 Behavior_Data.csv 上另开一列标注每个行为属于哪门性技——
       那要给约200个性爱行为逐条填，且与这里的经验需求语义重复，两处一旦不一致就出BUG。
    Keyword arguments:
    无
    Return arguments:
    int -- 经验id，解不出或不在课中则为0
    """
    ability_id = get_now_class_ability()
    if ability_id == -1:
        return 0
    return growth_handle.get_subject_exp_id(ability_id)


def get_subject_bonus(student_id: int) -> float:
    """
    取某学生本节实操课的主修科目经验倍率

    最终倍率 = 课程加成 × 师生等级差速度系数 × 教育区加成 × 成长停滞倍率（口径 27），
    后三项直接用一期已实现的函数，不另造一套公式。教师即玩家。
    Keyword arguments:
    student_id -- 学生的角色id
    Return arguments:
    float -- 经验倍率
    """
    ability_id = get_now_class_ability()
    if ability_id == -1:
        return 1.0
    if student_id not in cache.character_data:
        return 1.0
    pl_data: game_type.Character = cache.character_data[0]
    student_data: game_type.Character = cache.character_data[student_id]
    teacher_level = pl_data.ability.get(ability_id, 0)
    student_level = student_data.ability.get(ability_id, 0)
    speed = growth_handle.get_learn_speed(teacher_level, student_level)
    return (education_constant.SUBJECT_BONUS * speed * growth_handle.get_education_zone_adjust()
            * growth_handle.get_growth_stop_adjust(student_id))


# ---------------------------------------------------------------------------
# 三次提醒的时刻
# ---------------------------------------------------------------------------


def get_period_start_time(date_ordinal: int, period: int) -> Optional[datetime.datetime]:
    """
    取某天某节次的开始时刻
    Keyword arguments:
    date_ordinal -- 日期序数
    period -- 节次0~8
    Return arguments:
    Optional[datetime.datetime] -- 开始时刻，节次非法则为None
    """
    if period < 0 or period >= len(game_time.CLASS_PERIOD_START):
        return None
    hour, minute = game_time.CLASS_PERIOD_START[period]
    now_date = datetime.date.fromordinal(date_ordinal)
    return datetime.datetime(now_date.year, now_date.month, now_date.day, hour, minute)


def get_period_end_time(date_ordinal: int, period: int) -> Optional[datetime.datetime]:
    """
    取某天某节次的结束时刻（即预定的下课时刻）
    Keyword arguments:
    date_ordinal -- 日期序数
    period -- 节次0~8
    Return arguments:
    Optional[datetime.datetime] -- 结束时刻，节次非法则为None
    """
    start_time = get_period_start_time(date_ordinal, period)
    if start_time is None:
        return None
    return start_time + datetime.timedelta(minutes=game_time.CLASS_PERIOD_MINUTE)


def judge_time_crossed(target_time: Optional[datetime.datetime], last_time: datetime.datetime, now_time: datetime.datetime) -> bool:
    """
    判断某个时刻是否被本次结算跨过

    游戏时间是按行为时长跳跃的，不逐分钟走：玩家13:00开始一个60分钟的行为，时间直接跳到14:00，
       13:30这个时刻从来没有被"经过"过。所以提醒一律用跨越判定（上次 < 目标 <= 当前），
       用 now_time == target_time 的等于判定会永远不触发。写法同 game_time.py:153 的切月判定。
    Keyword arguments:
    target_time -- 目标时刻
    last_time -- 上次结算时刻
    now_time -- 当前时刻
    Return arguments:
    bool -- 是否跨过
    """
    if target_time is None:
        return False
    return last_time < target_time <= now_time


def fix_notified(class_data: dict) -> list:
    """
    取出并补齐某节课的三次提醒标记（旧存档里可能只有两项）
    Keyword arguments:
    class_data -- 课程数据
    Return arguments:
    list -- 长度为3的标记列表
    """
    notified = class_data.get("notified", [])
    if not isinstance(notified, list):
        notified = []
    while len(notified) < 3:
        notified.append(False)
    class_data["notified"] = notified
    return notified


def check_and_send_notify(last_time: datetime.datetime, now_time: datetime.datetime) -> List[str]:
    """
    检查第二、三次提醒里有没有该发的，返回要输出的文本

    三次提醒（方案 §3.28.9）：
        1. 预约日当天玩家起床后 —— 走 get_today_class_notify_text()，不在本函数
        2. 节次开始前30分钟
        3. 节次的结束时刻（预定下课时刻），只在课堂H模式进行中才发
    Keyword arguments:
    last_time -- 上次结算时刻
    now_time -- 当前时刻
    Return arguments:
    List[str] -- 要输出的提醒文本
    """
    result = []
    for class_key, class_data in cache.rhodes_island.temp_sex_class.items():
        date_ordinal, period = parse_class_key(class_key)
        if date_ordinal == -1:
            continue
        notified = fix_notified(class_data)
        # 第二次：开始前30分钟
        if not notified[1]:
            start_time = get_period_start_time(date_ordinal, period)
            if start_time is not None:
                notify_time = start_time - datetime.timedelta(minutes=education_constant.NOTIFY_BEFORE_MINUTE)
                if judge_time_crossed(notify_time, last_time, now_time):
                    notified[1] = True
                    result.append(
                        _("\n【课程提醒】还有半小时，你安排在{0}的性技实操课就要开始了，选修与点名必修的学生会在开课前 {1} 分钟动身赶来。\n").format(
                            class_data.get("classroom", ""), education_constant.PRE_ARRIVE_MINUTE
                        )
                    )
        # 第三次：预定的下课时刻，只在课上着的时候才发
        if not notified[2] and class_data.get("running", False):
            end_time = get_period_end_time(date_ordinal, period)
            if judge_time_crossed(end_time, last_time, now_time):
                notified[2] = True
                result.append(
                    _("\n【课程提醒】预定的下课时间到了。你可以就此结束这节课，也可以继续下去——没有人会催你。\n")
                )
    return result


def get_ability_name(ability_id: int) -> str:
    """
    取能力的显示名
    Keyword arguments:
    ability_id -- 能力id
    Return arguments:
    str -- 能力名，查不到则为空串
    """
    from Script.Config import game_config

    if ability_id in game_config.config_ability:
        return game_config.config_ability[ability_id].name
    return ""


def get_today_class_notify_text() -> str:
    """
    取"今天有实操课"的起床提醒文本（第一次提醒）
    Keyword arguments:
    无
    Return arguments:
    str -- 提醒文本，今天没课或已提醒过则为空串
    """
    today = cache.game_time.date().toordinal()
    text_list = []
    for class_key, class_data in cache.rhodes_island.temp_sex_class.items():
        date_ordinal, period = parse_class_key(class_key)
        if date_ordinal != today:
            continue
        notified = fix_notified(class_data)
        if notified[0]:
            continue
        start_time = get_period_start_time(date_ordinal, period)
        if start_time is None:
            continue
        notified[0] = True
        text_list.append(
            _("【今日课程】你在今天{0}安排了一节性技实操课（{1}），地点在{2}。").format(
                start_time.strftime("%H:%M"),
                get_ability_name(class_data.get("ability_id", -1)),
                class_data.get("classroom", ""),
            )
        )
    if not text_list:
        return ""
    return "\n" + "\n".join(text_list) + "\n"


# ---------------------------------------------------------------------------
# 开课与下课
# ---------------------------------------------------------------------------


def start_sex_class(ability_id: int, join_id_list: Optional[List[int]] = None) -> dict:
    """
    开始一节性技实操课

    两种发起方式在这里汇合：预约的那节课把已有条目标记为 running，当场开课则新建一条 running 的。
    之后的主修加成、旁观结算、下课流程只有一条代码路径。
    Keyword arguments:
    ability_id -- 主修的性技科目能力id
    join_id_list -- 到场学生的角色id列表，None时现取场景内的
    Return arguments:
    dict -- 本节课的数据
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    classroom = get_scene_name(pl_character_data.position)
    today = cache.game_time.date().toordinal()
    period = game_time.get_class_period_by_time(cache.game_time)
    # 预约的那节课（含提前几分钟开讲的，Plan 26 §3.5）与同一节里下课后重开的：复用已有条目，保留玩家排课时定的主修科目与必修名单
    now_class = find_class_to_start(classroom, cache.game_time)[1]
    if now_class is None:
        # 当前节次的键被别的教室还没开讲的预约占着：临时课的键不含教室，另开当场课会静默覆盖那条预约。
        #    玩家在这里开课就是决定在这里上，把那条挪过来（Plan 26 §3.5，L4）
        other_class = get_temp_class(today, period)
        if other_class is not None and not other_class.get("running", False) and not other_class.get("ended", False):
            other_class["classroom"] = classroom
            now_class = other_class
    if now_class is not None:
        now_class["running"] = True
        # 同一节里下课后又开一次：清掉已下课标记，覆盖层重新生效
        now_class["ended"] = False
        # 复用了预约条目 → 这是预约的那节课；开课口上按"预约 / 当场"分档（方案 §3.28.10）
        now_class["reserved"] = True
        if ability_id in education_constant.SEX_CLASS_ABILITY_LIST:
            now_class["ability_id"] = ability_id
    else:
        now_class = set_temp_class(today, period, classroom, ability_id, running=True)
        now_class["reserved"] = False
    if join_id_list is None:
        join_id_list = get_scene_student_list(pl_character_data.position)
    # 出勤只在开课时记这一次：拖堂占用的后续节次既不记出勤也不记缺课（方案 §3.28.9）
    for student_id in join_id_list:
        settle_attend(student_id)
    return now_class


def end_sex_class() -> None:
    """
    结束当前的性技实操课

    只由玩家手动触发（口径68），系统永不自动下课。唯二的例外是既有的体力归零兜底
       （group_sex_npc_hp_0_end / group_sex_pl_hp_0_end），那两条本就在群交链上。
    Keyword arguments:
    无
    Return arguments:
    无
    """
    class_key = get_running_class_key()
    if not class_key:
        return
    now_class = cache.rhodes_island.temp_sex_class[class_key]
    now_class["running"] = False
    # 下了课这一节就交还给原来的课表（2026-09-12 第五轮）：当场开的课没有任何后续用处，直接删掉；
    #    预约的课留着条目到跨天清理，只打上已下课标记，覆盖层与必修判定据此不再认它
    if now_class.get("reserved", False):
        now_class["ended"] = True
    else:
        del cache.rhodes_island.temp_sex_class[class_key]


def judge_end_type() -> int:
    """
    判断这次下课属于提前、按时还是拖堂，供口上差分使用
    Keyword arguments:
    无
    Return arguments:
    int -- 0提前 1按时 2拖堂；不在课中则为-1
    """
    class_key = get_running_class_key()
    if not class_key:
        return -1
    date_ordinal, period = parse_class_key(class_key)
    end_time = get_period_end_time(date_ordinal, period)
    if end_time is None:
        return 1
    # 预定下课前5分钟以上算提前，前后5分钟内算按时，再往后算拖堂
    delta = (cache.game_time - end_time).total_seconds() / 60
    if delta < -5:
        return 0
    if delta <= 5:
        return 1
    return 2


def pull_student_into_class(student_id: int) -> None:
    """
    把一名学生拉进正在进行的实操课（课堂 H）
    Keyword arguments:
    student_id -- 学生的角色id
    Return arguments:
    无
    功能: 开课时（效果 10014）与开课后才到场（状态机 722，Plan 25 §3.2）共用：取消移动计划、进 H、看见玩家的 H、派发到场二段口上。
          不记出勤：开课时拉进来的人出勤已由 start_sex_class 记过，晚到的人由 722 自己补记
    """
    from Script.Core import constant
    from Script.Design import character_move, second_behavior

    student_data: game_type.Character = cache.character_data[student_id]
    if not student_data.sp_flag.is_h:
        character_move.cancel_movement_plan(student_id)
    student_data.sp_flag.is_h = True
    student_data.sp_flag.see_pl_h = True
    # 到场的口上走二段行为：一段行为得靠NPC AI派发，而H中的NPC完全不进AI链（handle_npc_ai.find_character_target 开头）
    second_behavior.character_get_second_behavior(student_id, constant.Behavior.JOIN_SEX_CLASS)


def settle_attend(student_id: int) -> None:
    """
    给一名到场学生记一次出勤
    Keyword arguments:
    student_id -- 学生的角色id
    Return arguments:
    无
    """
    # 只给「女儿 ∪ 学生岗」记：凭 H 模式实行值到场的成年非学生干员不是学生，
    #    给她们惰性创建养成数据只会让全岛的存档一起变大（与 semester_handle 的约定一致）
    if student_id not in cache.character_data:
        return
    student_data: game_type.Character = cache.character_data[student_id]
    if student_data.relationship.father_id != 0 and student_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return
    growth_handle.get_child_growth(student_id).attend_class_count += 1


# ---------------------------------------------------------------------------
# 旁观
# ---------------------------------------------------------------------------


def get_watcher_list() -> List[int]:
    """
    取本节课的旁观学生——人在场、已加入课堂H，但没有占用群交模板任何部位的那些

    群交模板一次最多占4~5个部位，一节课若来了8个学生，其余的只能旁观。
    既有H结算只给被操作者加经验，不补这一块的话玩家很快会学会"只排4个学生就够了"，
    这门课就退化成一对一，"课堂"的设定也就空了。

    开头的 sex_class_mode 判定是硬要求不是优化：课堂模式会同时置 group_sex_mode，
       若这里改判群交标志，任何一场普通群交都会给全场围观干员发经验与状态。
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 旁观学生的角色id列表
    """
    from Script.System.Sex_System import group_sex_panel

    if not cache.sex_class_mode:
        return []
    in_template_list = group_sex_panel.count_group_sex_character_list()
    result = []
    for student_id in get_scene_student_list():
        if student_id in in_template_list:
            continue
        student_data: game_type.Character = cache.character_data[student_id]
        if not student_data.sp_flag.is_h:
            continue
        result.append(student_id)
    return result


def judge_hp_low_only_watch(character_id: int) -> bool:
    """
    判断某学生是否因体力不足而只能旁观（口径65）

    体力不足是"做不动"而不是"不想来"，所以人照常到场、不计缺课，只是不进H模板。
    这里实时判一次即可，不必给学生挂"本节只旁观"的flag——状态本来就是实时的。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否只能旁观
    """
    if character_id not in cache.character_data:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if not character_data.hit_point_max:
        return False
    return character_data.hit_point / character_data.hit_point_max < education_constant.ABSENT_HP_RATE


def judge_show_watch_talk() -> bool:
    """
    掷一次旁观口上的触发判定

    只限流口上，收益结算每个动作都给。玩家一节课可能做20个动作，
       每次都描写一遍"学生们看着"会刷满屏幕，但经验与状态该给还是要给。
    Keyword arguments:
    无
    Return arguments:
    bool -- 本次是否出旁观口上
    """
    return random.random() < education_constant.WATCH_TALK_RATE


def settle_watcher(add_time: int, change_data: game_type.CharacterStatusChange) -> None:
    """
    给本节课的旁观学生结算观摩收益：主修科目经验的25% + 少量羞耻与欲情

    由 settle_behavior.handle_settle_behavior() 在玩家每个H动作结算后调用。

    经验**直接写入**而不走 base_chara_experience_common_settle：那个函数里挂着主修科目加成的钩子
       （common_default.py 的经验写入段），本次要发的 main_exp 是从被操作学生的结算结果里读来的、
       **已经含加成**，再过一遍钩子就成了双重加成。
    状态则照常走通用函数（状态没有加成钩子），但必须传 tenths_add=False：
       该参数默认为真会额外加"当前状态值的1/10"，一节课20个动作逐次滚雪球会让旁观者涨得比被操作者还快。
    Keyword arguments:
    add_time -- 本次行为的结算时长
    change_data -- 玩家本次行为的状态变更记录对象
    Return arguments:
    无
    """
    from Script.Settle.common_default import base_chara_state_common_settle
    from Script.Design import second_behavior
    from Script.Core import constant

    if not add_time:
        return
    watcher_list = get_watcher_list()
    if not watcher_list:
        return
    exp_id = get_now_bonus_exp_id()
    # 本次玩家动作给被操作学生加了多少主修经验，旁观者按其比例领
    main_exp = 0
    if exp_id:
        for target_change in change_data.target_change.values():
            main_exp = max(main_exp, target_change.experience.get(exp_id, 0))
    watch_exp = int(main_exp * education_constant.WATCH_EXP_RATE)
    # 口上限流：本轮是否描写旁观者，与收益是否结算无关
    show_talk = judge_show_watch_talk()
    for watcher_id in watcher_list:
        watcher_data: game_type.Character = cache.character_data[watcher_id]
        # 主修科目经验
        if exp_id and watch_exp:
            watcher_data.experience.setdefault(exp_id, 0)
            watcher_data.experience[exp_id] += watch_exp
            change_data.target_change.setdefault(watcher_id, game_type.TargetChange())
            watcher_change: game_type.TargetChange = change_data.target_change[watcher_id]
            watcher_change.experience.setdefault(exp_id, 0)
            watcher_change.experience[exp_id] += watch_exp
        # 羞耻与欲情。能力与状态的配对沿用既有约定：羞耻配露出(34)、欲情配欲望(33)
        base_chara_state_common_settle(
            watcher_id, add_time, 16, base_value=education_constant.WATCH_STATE_BASE,
            ability_level=watcher_data.ability.get(34, 0), tenths_add=False,
            change_data_to_target_change=change_data,
        )
        base_chara_state_common_settle(
            watcher_id, add_time, 12, base_value=education_constant.WATCH_STATE_BASE,
            ability_level=watcher_data.ability.get(33, 0), tenths_add=False,
            change_data_to_target_change=change_data,
        )
        if show_talk:
            second_behavior.character_get_second_behavior(watcher_id, constant.Behavior.WATCH_SEX_CLASS)
