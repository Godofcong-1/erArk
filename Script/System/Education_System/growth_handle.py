"""生长养成的能力成长计算（Plan 22 一期）

本模块**完全复用既有的能力成长链**，不另造一套平行的经验体系：

    上课  →  base_chara_state_common_settle(学生, 状态9 习得)   累加习得状态值
          →  base_chara_experience_common_settle(学生, 科目经验) 累加该科目经验
    玩家睡觉 → sleep_settle.settle_character_juel()  习得状态值 → 习得珠(juel 9)，状态清零
             → handle_ability.gain_ability()         按 AbilityUp.csv 的 J9|n & E<经验>|n 需求升级并扣珠

因此"上课立刻变强"体现为**当场累加习得与科目经验**，等级则在当晚睡眠结算时兑现，
与全游戏所有干员的成长口径完全一致（读书、训练、工作都是这条链）。

由此天然产生的两个性质：
    1. 习得珠是**通用**的、科目经验是**分科**的 —— 专精一门能把它推到高级，
       广泛选课则珠够而各科经验摊薄，总成长量由珠池封顶。
    2. 性技科目（70~77）的升级需求是**真实性交经验**（如膣技要 E61 阴道性交经验），
       课堂与自习对它们只给习得与对应的理论经验（Plan 26，get_class_exp_id），真实经验要靠实操课来补 —— 理论与实操两条腿。
"""
import datetime
from types import FunctionType
from typing import List, Optional
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.System.Education_System import education_constant

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def get_child_growth(character_id: int) -> game_type.CHILD_GROWTH:
    """
    取角色的养成数据结构体，没有则惰性创建（全项目唯一的创建入口）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    game_type.CHILD_GROWTH -- 该角色的养成数据结构体
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.child_growth is None:
        character_data.child_growth = game_type.CHILD_GROWTH()
    return character_data.child_growth


def get_character_stage(character_id: int) -> int:
    """
    取角色当前所处的成长阶段素质id
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 101婴儿/102幼女/103萝莉/104少女，都不是则0
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 必须按 id 升序遍历：成长链正常情况下四个素质只会挂一个，
    #    但世界设定「萝莉化」会批量覆写年龄素质，遍历 set 的哈希序会取到不确定的那个
    for talent_id in sorted(education_constant.CHILD_TALENT_SET):
        if character_data.talent.get(talent_id, 0):
            return talent_id
    return 0


def get_student_candidate_list() -> List[int]:
    """
    取养成中的女儿列表（养成总览、日程批量套用、学期结算共用）
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表，按id升序
    功能: 玩家的女儿中处于幼女/萝莉/少女阶段的。
          个人课表**不再**用这份名单：它已放宽为「职业为学生的全部干员」，走下面的
             get_course_candidate_list()（一期方案 §9.8.2）。养成总览等只关心女儿的地方仍用本函数
          血缘条件不能省：只看年龄素质的话，世界设定「萝莉化」
             (character_handle.handle_character_setting) 会给全岛干员挂上萝莉素质103，
             只按素质筛会把全岛的人都塞进选择学生的名单
          按 id 升序而不是遍历 npc_id_got(set)：名单要交给「选择学生」面板与学期结算逐个处理，
             set 的迭代顺序不定会让每次列出的顺序都不一样
    """
    from Script.Design import handle_premise

    result = []
    for character_id in sorted(cache.npc_id_got):
        if character_id not in cache.character_data:
            continue
        if get_character_stage(character_id) not in education_constant.STUDENT_STAGE_TALENT_SET:
            continue
        if not handle_premise.handle_self_is_player_daughter(character_id):
            continue
        result.append(character_id)
    return result


def get_course_candidate_list() -> List[int]:
    """
    取可排个人课表的角色列表
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表，按id升序
    功能: 职业为学生（WorkType 152）的全部干员（Plan 24 口径 1：课表只对学生岗生效）。
          上课是工作链里学生岗的目标行（target.csv 组 08），改了岗的女儿不会再去上课，所以也不再列出；
             存档里她残留的个人课表不迁移、不清理，没有行会命中，改回学生岗后照常生效。
             女儿长到幼女时会被自动置为学生岗，默认都在名单里。
          成年学生只排课、只上课，不出成绩单、不进养成事件——那些地方仍只遍历女儿。
          与 get_student_candidate_list 一样按 id 升序：「选择学生」面板与必修名单逐个列人，set 的迭代顺序会飘
    """
    result = []
    for character_id in sorted(cache.npc_id_got):
        if character_id not in cache.character_data:
            continue
        character_data: game_type.Character = cache.character_data[character_id]
        if character_data.work.work_type == education_constant.STUDENT_WORK_TYPE:
            result.append(character_id)
    return result


def get_subject_exp_id(ability_id: int) -> int:
    """
    取某个科目（能力）升级所需的经验id，直接从 AbilityUp.csv 的升级需求里解出，不另建映射表
    Keyword arguments:
    ability_id -- 科目能力id
    Return arguments:
    int -- 经验id，解不出则为0
    """
    level_data = game_config.config_ability_up_data.get(ability_id, {})
    for level in sorted(level_data.keys()):
        for need_text in level_data[level]:
            if need_text.startswith("E") and "|" in need_text:
                exp_part = need_text.split("|")[0][1:]
                if exp_part.isdigit():
                    return int(exp_part)
    return 0


def get_class_exp_id(ability_id: int) -> int:
    """
    取教室课与自习给某个科目发的经验id（Plan 26 §3.1）
    Keyword arguments:
    ability_id -- 科目能力id
    Return arguments:
    int -- 经验id；性技科目取对应的理论经验，没有对应理论经验（76腰技）时为0，只给习得
    功能: 性技科目在 AbilityUp.csv 里解出的是真实性交经验（指技→手交、舌技→口交……），
          课堂上发它会让孩子带着性交经验，舌技课还会经 common_default 的钩子补记一条口交初体验；
          所以性技科目改发 Experience.csv 类型 12 的理论经验，其余科目照旧取升级需求里的经验
    """
    if ability_id in education_constant.SEX_SKILL_SUBJECT_SET:
        return education_constant.SEX_SKILL_THEORY_EXP_ID.get(ability_id, 0)
    return get_subject_exp_id(ability_id)


def get_learn_speed(teacher_level: int, student_level: int) -> float:
    """
    按师生等级差算学习速度系数（软约束，无硬墙）
    diff >= 0：speed = 1.0 + 0.25 * diff        学生低于教师，差距越大学得越快
    diff <  0：speed = 1.0 / (1 + 0.5 * |diff|)  学生高于教师，差距越大学得越慢但永不归零
    Keyword arguments:
    teacher_level -- 教师该科目的能力等级0~8
    student_level -- 学生该科目的能力等级0~8
    Return arguments:
    float -- 学习速度系数
    """
    diff = teacher_level - student_level
    if diff >= 0:
        return 1.0 + 0.25 * diff
    return 1.0 / (1 + 0.5 * abs(diff))


def get_education_zone_adjust() -> float:
    """
    取教育区等级带来的成长效率加成倍率
    Facility_effect.csv 里教育区各级的 effect 列（Lv1=0 / Lv2=5 / Lv3=20 / Lv4=50 / Lv5=100）
       此前在代码中从未被读取，介绍文案却已向玩家承诺了"成长效率加成提升至20%/50%/100%"。
       本计划把它接到上课结算上，兑现这个承诺。
    Keyword arguments:
    无
    Return arguments:
    float -- 倍率，如 Lv5 时为 2.0
    """
    now_level = cache.rhodes_island.facility_level.get(education_constant.EDUCATION_ZONE_CID, 1)
    cid_list = game_config.config_facility_effect_data.get(education_constant.EDUCATION_ZONE_NAME, [])
    # 该表的列表下标即设施等级（构建时补了个0占位），越界则按无加成处理
    if now_level < len(cid_list):
        effect_cid = cid_list[now_level]
        if effect_cid:
            return 1.0 + game_config.config_facility_effect[effect_cid].effect / 100
    return 1.0


def get_growth_stop_adjust(character_id: int) -> float:
    """
    取成长停滞带来的学习收益倍率（总纲口径 27）
    Keyword arguments:
    character_id -- 学生的角色id
    Return arguments:
    float -- 有成长停滞素质(28)时为 GROWTH_STOP_LEARN_RATE，否则为 1.0
    功能: 停滞期间可以继续上课，但一切学习收益减半，作为无限期养成的代价。
          只看学生自己的素质，教师停滞与否与教学无关
    """
    if character_id not in cache.character_data:
        return 1.0
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent.get(education_constant.GROWTH_STOP_TALENT_ID, 0):
        return education_constant.GROWTH_STOP_LEARN_RATE
    return 1.0


def get_class_adjust(ability_id: int, student_id: int, teacher_id: int) -> float:
    """
    算一节课的总倍率（速度系数 × 教育区加成 × 成长停滞倍率）
    Keyword arguments:
    ability_id -- 科目能力id
    student_id -- 学生的角色id
    teacher_id -- 授课教师的角色id，-1表示本节无教师（降级为自习）
    Return arguments:
    float -- 总倍率
    功能: 教室课 / 自习 / 实习课都经 settle_student_class_gain 走到这里，
          所以成长停滞的减半（口径 27）放在这一处就覆盖了三种课
    """
    zone_adjust = get_education_zone_adjust() * get_growth_stop_adjust(student_id)
    # 无教师则走自习：没有教师就没有等级差可算，速度系数恒取1.0
    if teacher_id == -1 or teacher_id not in cache.character_data:
        return zone_adjust
    student_data: game_type.Character = cache.character_data[student_id]
    teacher_data: game_type.Character = cache.character_data[teacher_id]
    student_level = int(student_data.ability.get(ability_id, 0))
    teacher_level = int(teacher_data.ability.get(ability_id, 0))
    return get_learn_speed(teacher_level, student_level) * zone_adjust


def settle_student_class_gain(
        student_id: int,
        teacher_id: int,
        ability_id: int,
        course_type: int,
        add_time: int,
        change_data=None,
        change_data_to_target_change=None,
        count_attend: bool = True,
) -> bool:
    """
    一节课的学生侧结算：累加习得状态值与该科目的经验
    等级不在此处提升，而是走既有链在玩家睡觉时兑现（见模块头注释）
    Keyword arguments:
    student_id -- 学生的角色id
    teacher_id -- 授课教师的角色id，-1表示本节无教师（降级为自习）
    ability_id -- 科目能力id
    course_type -- 课型编号，决定基础值
    add_time -- 本次结算的分钟数
    change_data -- 结算信息记录对象
    change_data_to_target_change -- 交互对象的结算信息记录对象
    count_attend -- 是否计一节出勤。只有课表排了课的节次才计（2026-09-12 第五轮）：
                    日程活动「上课（无课时自习）」的自习照常给收益，但不算上过一节课；
                    这一节已记了缺课的也不计（Plan 30）
    Return arguments:
    bool -- 是否真的结算了（同一节已结算过则为False）
    功能: 节次内按 last_attend_period 去重，同一节课只结算一次（2026-09-12 第五轮）。
             NPC 的行为结算发生在行为**开始**时：学生坐下听课时，本节教师判能到岗即由学生自己这一侧结算（557，Plan 31），
             教师开讲那一刻的广播（512）则发给已经坐下听课的学生；两条路都会走到这里，不去重就会发两份。
          节次外（玩家在午休或晚上手动授课）不去重。
          同一节只落一种记录（Plan 30）：开课时体力不足记了缺课、休完才回来上课的，收益照给，出勤不再记
    """
    if not add_time:
        return False
    # 延迟导入：Script.Settle 的包 __init__ 会连带载入指令系统，必须等配置初始化之后
    from Script.Settle import common_default
    from Script.Design import game_time

    growth_data = get_child_growth(student_id)
    now_time = cache.character_data[student_id].behavior.start_time or cache.game_time
    period = game_time.get_class_period(student_id)
    now_mark = []
    if period != -1:
        now_mark = [now_time.toordinal(), period]
        if growth_data.last_attend_period == now_mark:
            return False

    no_teacher = teacher_id == -1 or teacher_id not in cache.character_data
    # 表里没有的课型回落到理论课的基础值，按课型常量取，不写死编号（Plan 32 L28）
    learn_base = education_constant.COURSE_LEARN_BASE.get(course_type, education_constant.COURSE_LEARN_BASE[education_constant.COURSE_TYPE_THEORY])
    exp_base = education_constant.COURSE_EXP_BASE.get(course_type, education_constant.COURSE_EXP_BASE[education_constant.COURSE_TYPE_THEORY])
    if no_teacher:
        # 教室课没老师就是自习，有一套自己的低档基础值；
        # 实习课没导师则是"见习"——照方案 §3.21 只把本岗位的基础值减半，而不是掉到自习档
        if course_type in education_constant.CLASSROOM_COURSE_TYPE_SET:
            learn_base = education_constant.SELF_STUDY_LEARN_BASE
            exp_base = education_constant.SELF_STUDY_EXP_BASE
        else:
            learn_base = max(1, learn_base // 2)
            exp_base = max(1, exp_base // 2)
    adjust = get_class_adjust(ability_id, student_id, teacher_id)

    # 习得状态：ability_level 传 -1 表示不吃"教师能力修正"，避免与速度系数双重加成；
    # 倍率统一走 extra_adjust，这样 (上课分钟数 + 基础值) 整体被缩放
    common_default.base_chara_state_common_settle(
        student_id,
        add_time,
        education_constant.LEARN_STATE_ID,
        base_value=learn_base,
        ability_level=-1,
        extra_adjust=adjust - 1.0,
        change_data=change_data,
        change_data_to_target_change=change_data_to_target_change,
    )

    # 科目经验：决定单科能升到多高；性技科目给的是理论经验、腰技只给习得（Plan 26 §3.1）
    exp_id = get_class_exp_id(ability_id)
    if exp_id:
        final_exp = max(1, int(exp_base * adjust))
        common_default.base_chara_experience_common_settle(
            student_id,
            exp_id,
            base_value=final_exp,
            change_data=change_data,
            change_data_to_target_change=change_data_to_target_change,
        )

    # 记下这一节已结算过，并按需记一节出勤；这一节已记了缺课的不再记出勤（Plan 30）
    if now_mark:
        growth_data.last_attend_period = now_mark
    if count_attend and not (now_mark and judge_absent_this_period(student_id, now_time)):
        growth_data.attend_class_count += 1
    return True


def judge_absent_this_period(character_id: int, now_time) -> bool:
    """
    校验这一节是不是已经记过缺课（Plan 30 §3.4：同一节只落一种记录）
    Keyword arguments:
    character_id -- 角色id
    now_time -- 参照时刻，取它的日期与节次
    Return arguments:
    bool -- 这一节已记了缺课（体力缺课或翘课）为True；角色不存在、没有养成数据、不在节次内为False
    功能: 体力闸在开课那一刻判，原地休息 30 分钟后体力可能回到 30% 以上，这一节剩下的时间里再回去上课。
          三个出勤写入点（settle_student_class_gain / settle_course_attend / sex_class_handle.settle_attend）都先问它：
             收益照给、出勤不记，免得同一节在成绩单上既算一次缺课又算一次出勤。
          只读不写，不惰性创建养成数据
    """
    from Script.Design import game_time

    if character_id not in cache.character_data:
        return False
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None:
        return False
    period = game_time.get_class_period_by_time(now_time)
    if period == -1:
        return False
    return growth_data.last_absent_period == [now_time.toordinal(), period]


def judge_selected_cell_real(character_id: int, week_day: int, period: int) -> bool:
    """
    校验个人课表上的一格是不是每周确有的一节课（Plan 30 §3.6：「有课」「同班同学」的判据）
    Keyword arguments:
    character_id -- 角色id
    week_day -- 星期0~6
    period -- 节次0~8
    Return arguments:
    bool -- 学生岗、这一格选了课、且那节课每周确实有为True
    功能: 改了岗的女儿课表残留（Plan 24 §3.10，改回学生岗即恢复），她不会去上课，不算有课；
          班级式课看每周课表那一格排没排课（不叠加当天的临时课覆盖层，已停课的不算）；
          个人式课看活动条件与上课地点（schedule_handle.judge_personal_course_real），不看此刻借不借得到书——那是一时的状态。
          只读不写，前提路径上可以调用
    """
    from Script.System.Education_System import schedule_handle

    if character_id not in cache.character_data:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return False
    course = schedule_handle.get_selected_course(character_id, week_day, period)
    if course is None:
        return False
    if course[0] in education_constant.CLASSROOM_COURSE_TYPE_SET:
        return schedule_handle.get_class_cell(course[1], week_day, period, include_temp=False) is not None
    return schedule_handle.judge_personal_course_real(character_id, {"course_type": course[0], "target": course[1]})


def judge_have_course_type(character_id: int, course_type: int) -> bool:
    """
    校验个人课表上有没有至少一格是某课型的真课（Plan 31 §3.14：点名课型的养成事件用）
    Keyword arguments:
    character_id -- 角色id
    course_type -- 课型编号（education_constant.COURSE_TYPE_*）
    Return arguments:
    bool -- 学生岗、且至少有一格课型相符并通过 judge_selected_cell_real 为True
    功能: 日常事件在 0 点推送，读「此刻这一节」的 CVP CourseType 恒为 -1，写不出课型前提，这里查整张个人课表。
          只读 child_growth，不惰性创建养成数据，前提路径上可以调用
    """
    if character_id not in cache.character_data:
        return False
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None or not growth_data.selected_course:
        return False
    for week_day, day_data in growth_data.selected_course.items():
        for period, course in day_data.items():
            if course[0] == course_type and judge_selected_cell_real(character_id, week_day, period):
                return True
    return False


def settle_course_attend(character_id: int) -> bool:
    """
    给一节体育课 / 兴趣课记一次出勤（Plan 29 §3.1）
    这两种课是「人到地点，执行该地点既有的行为」（状态机 716）：打木桩 / 锻炼 / 游泳，或该娱乐的行为。
       这些行为全岛共用（成年干员娱乐时也走它们），不能往效果串里加上课结算，所以出勤在 716 派出行为时记。
       实习课不走这里：它的行为 intern_class 的效果 552 经 settle_student_class_gain 记出勤，再记就是两份
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否真的记上了（不是女儿也不是学生岗、不在节次内、同一节已记过、这一节已记了缺课则为False）
    功能: 守卫与 sex_class_handle.settle_attend 相同，只给女儿或学生岗记；
          节次内按 last_attend_period 去重，同一节被打断后再回去上只记一次；与教室课共用这个标记也不会互相挤占——一格只有一门课。
          这一节已记了缺课（开课时体力不足、休完回来）的不记，也不写标记，行为照常派出（Plan 30，同一节只落一种记录）
    """
    from Script.Design import game_time

    if character_id not in cache.character_data:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.relationship.father_id != 0 and character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return False
    period = game_time.get_class_period(character_id)
    if period == -1:
        return False
    now_time = character_data.behavior.start_time or cache.game_time
    if judge_absent_this_period(character_id, now_time):
        return False
    now_mark = [now_time.toordinal(), period]
    growth_data = get_child_growth(character_id)
    if growth_data.last_attend_period == now_mark:
        return False
    growth_data.last_attend_period = now_mark
    growth_data.attend_class_count += 1
    return True


def settle_teacher_class_gain(
        teacher_id: int,
        ability_id: int,
        add_time: int,
        change_data=None,
) -> None:
    """
    一节课的教师侧结算：教师自己也获得当节所授科目的习得与经验（教学相长）
    与既有实现的区别：既有 handle_teach_add_just 写死加学识，本函数改为加**当节所授科目**
    Keyword arguments:
    teacher_id -- 教师的角色id
    ability_id -- 当节所授科目的能力id
    add_time -- 本次结算的分钟数
    change_data -- 结算信息记录对象
    Return arguments:
    无
    """
    if not add_time:
        return
    from Script.Settle import common_default

    teacher_data: game_type.Character = cache.character_data[teacher_id]
    # 教师自身的成长吃自己的该科目等级修正，与既有口径一致
    common_default.base_chara_state_common_settle(
        teacher_id,
        add_time,
        education_constant.LEARN_STATE_ID,
        ability_level=int(teacher_data.ability.get(ability_id, 0)),
        change_data=change_data,
    )
    # 教学相长同一口径：性技科目教师也只拿理论经验（Plan 26 §3.1）
    exp_id = get_class_exp_id(ability_id)
    if exp_id:
        common_default.base_chara_experience_common_settle(teacher_id, exp_id, change_data=change_data)


# ---------------------------------------------------------------------------
# 幼女跟随母亲见学（Plan 22 二期 §3.24）
# ---------------------------------------------------------------------------


def get_mother_work_ability_id(mother_id: int) -> int:
    """
    取母亲当前工作对应的科目能力id
    Keyword arguments:
    mother_id -- 母亲的角色id
    Return arguments:
    int -- 能力id，母亲没有工作（work_type为0）或该岗位不对应能力时为0
    """
    if mother_id not in cache.character_data:
        return 0
    mother_data: game_type.Character = cache.character_data[mother_id]
    work_type_id = mother_data.work.work_type
    if not work_type_id or work_type_id not in game_config.config_work_type:
        return 0
    return game_config.config_work_type[work_type_id].ability_id


def settle_follow_mother_gain(
        character_id: int,
        mother_id: int,
        add_time: int,
        change_data: Optional[game_type.CharacterStatusChange] = None,
) -> None:
    """
    一次见学的结算：按母亲的工作科目加习得与经验，并累加照料值与母女好感

    母亲没有工作时**只加照料值与好感，不加任何学习收益**（方案 §3.24 的回落表最后一行）——
       跟着一个没在工作的母亲，学不到手艺，但相处本身是有意义的。
    不计入 attend_class_count：见学不是课，混进出勤率会让成绩单失真。
    Keyword arguments:
    character_id -- 幼女的角色id
    mother_id -- 母亲的角色id
    add_time -- 结算的分钟数
    change_data -- 结算信息记录对象
    Return arguments:
    无
    """
    if not add_time or mother_id not in cache.character_data:
        return
    from Script.Settle import common_default
    from Script.Design import character_handle

    growth_data = get_child_growth(character_id)
    growth_data.care_point += education_constant.FOLLOW_MOTHER_CARE_POINT

    # 母女好感：直接走 add_favorability，不套 common_default 的好感链——
    # 那条链的信物/连续指令/难度修正都是围绕玩家设计的，母女之间套上去只会得到看不懂的数字
    character_handle.add_favorability(mother_id, character_id, education_constant.FOLLOW_MOTHER_FAVORABILITY, change_data, None)
    character_handle.add_favorability(character_id, mother_id, education_constant.FOLLOW_MOTHER_FAVORABILITY, change_data, None)

    ability_id = get_mother_work_ability_id(mother_id)
    if not ability_id:
        return

    # 速度系数走与教室课同一套曲线：母亲该能力等级 vs 自己的等级；成长停滞同样减半（口径 27）
    child_data: game_type.Character = cache.character_data[character_id]
    mother_data: game_type.Character = cache.character_data[mother_id]
    adjust = get_learn_speed(
        int(mother_data.ability.get(ability_id, 0)),
        int(child_data.ability.get(ability_id, 0)),
    ) * get_education_zone_adjust() * get_growth_stop_adjust(character_id)

    common_default.base_chara_state_common_settle(
        character_id,
        add_time,
        education_constant.LEARN_STATE_ID,
        base_value=education_constant.FOLLOW_MOTHER_LEARN_BASE,
        ability_level=-1,
        extra_adjust=adjust - 1.0,
        change_data=change_data,
    )
    exp_id = get_subject_exp_id(ability_id)
    if exp_id:
        common_default.base_chara_experience_common_settle(
            character_id, exp_id, base_value=max(1, int(education_constant.FOLLOW_MOTHER_EXP_BASE * adjust)),
            change_data=change_data,
        )


# ---------------------------------------------------------------------------
# 成年结算：性格选边 / 发育加成输入 / 职业倾向提示（Plan 22 二期 §3.8）
# ---------------------------------------------------------------------------


def get_care_point_grow_bonus(character_id: int) -> int:
    """
    把照料值折算为身体发育判定的概率偏移（方案 §3.8 的第二输入）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 0~CARE_POINT_CHEST_MAX_BONUS 的百分点偏移
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return 0
    return int(min(education_constant.CARE_POINT_CHEST_MAX_BONUS, max(0.0, growth_data.care_point) / education_constant.CARE_POINT_PER_CHEST_BONUS))


def settle_personality_pair(character_id: int, pair_id: int) -> int:
    """
    按一对性格倾向的符号给这一对性格素质选边（Plan 32 §3.4，自 settle_personality_talent 抽出）
    Keyword arguments:
    character_id -- 角色id
    pair_id -- 性格对编号（0勤劳/懒散 1坚强/脆弱 2热情/孤僻 3开放/羞耻，素质对照见 education_constant.PERSONALITY_PAIR_TALENT）
    Return arguments:
    int -- 写上的素质id；倾向为 0、没有养成数据、角色或性格对不存在时为0（两侧都不动）
    功能: 正值取正向素质、负值取负向素质，并清掉同一对的另一侧；为 0 时不随机选边、两侧都不动（与成年结算同一规则，Plan 22 二期 §3.8）。
          成年结算逐对调它；成年之后改写倾向时由 settle_adult_personality_pair 只重选被改的那一对。
          只读养成数据，不惰性创建
    """
    if character_id not in cache.character_data or pair_id not in education_constant.PERSONALITY_PAIR_TALENT:
        return 0
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return 0
    plus_talent, minus_talent = education_constant.PERSONALITY_PAIR_TALENT[pair_id]
    point = growth_data.personality_point.get(pair_id, 0.0)
    if point > 0:
        got_talent, lost_talent = plus_talent, minus_talent
    elif point < 0:
        got_talent, lost_talent = minus_talent, plus_talent
    else:
        # 这一对没有倾向，两侧都不写
        return 0
    character_data.talent[got_talent] = 1
    # 同一对的另一侧要清掉，避免出现"既勤劳又懒散"
    character_data.talent[lost_talent] = 0
    return got_talent


def settle_adult_personality_pair(character_id: int, pair_id: int) -> int:
    """
    已成年的女儿改写一对性格倾向之后，按新的倾向值重选这一对素质（Plan 32 §3.4）
    Keyword arguments:
    character_id -- 角色id
    pair_id -- 性格对编号（0~3）
    Return arguments:
    int -- 写上的素质id；不是已成年（阶段 104）的女儿、或倾向为 0 时为0（素质不动）
    功能: 成年结算（pregnancy_handle.check_grow_to_girl）只在 103→104 那一刻选一次边，之后毕业典礼、成年纪念、通用 59 / 60
             与成年前入队、成年后才处理的日常事件，选项加的倾向值若不落到素质上，提示里写的「倾向：坚强」就是空话。
          只对已成年的女儿生效：未成年的倾向留到成年结算统一选边；成年学生（非女儿）没有性格养成。
          静默改写，不另出文本：事件选项的提示已写明倾向。由 change_growth_value / set_growth_value 在改写倾向后调用
    """
    from Script.Design import handle_premise

    if character_id not in cache.character_data:
        return 0
    if get_character_stage(character_id) != 104 or not handle_premise.handle_self_is_player_daughter(character_id):
        return 0
    return settle_personality_pair(character_id, pair_id)


def settle_personality_talent(character_id: int) -> str:
    """
    成年时按 personality_point 的符号给四对性格素质选边

    全为 0 时**不随机选边**，输出"性格尚未定型"（方案 §3.8）——
       玩家全程没参与养成就凭空得到一套性格，会让养成事件显得可有可无。
    逐对的选边规则在 settle_personality_pair（Plan 32 §3.4），成年之后改写倾向时重选也走它
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 要输出给玩家的文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return _("\n{0}的性格尚未定型\n").format(character_data.name)
    got_name_list = []
    for pair_id in education_constant.PERSONALITY_PAIR_TALENT:
        got_talent = settle_personality_pair(character_id, pair_id)
        if got_talent:
            got_name_list.append(game_config.config_talent[got_talent].name)
    if not got_name_list:
        return _("\n{0}的性格尚未定型\n").format(character_data.name)
    return _("\n{0}的性格定型为了[{1}]\n").format(character_data.name, "]、[".join(got_name_list))


def get_career_suggestion_text(character_id: int) -> str:
    """
    按当前等级最高的科目反查岗位，给出职业倾向提示

    **只提示、不自动任命**（口径 39）：成年后成为普通干员、可任命到任何岗位，任命权在玩家手里。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 提示文本，没有任何科目有等级时为空串
    """
    character_data: game_type.Character = cache.character_data[character_id]
    best_ability_id = 0
    best_level = 0
    # 只看技能类科目（Ability.csv 类型 4，即 40~49）：性技与其它能力不对应岗位，拿来推岗位没有意义；
    #    科目表从配置现算，不写死编号
    for ability_id in education_constant.SUBJECT_ABILITY_LIST:
        if game_config.config_ability[ability_id].ability_type != education_constant.ABILITY_TYPE_SUBJECT:
            continue
        level = int(character_data.ability.get(ability_id, 0))
        if level > best_level:
            best_level = level
            best_ability_id = ability_id
    if not best_ability_id:
        return ""
    ability_name = game_config.config_ability[best_ability_id].name
    # 反查以该能力为主的岗位。同一能力可能对应多个岗位，取cid最小的那个作为代表
    work_name = ""
    for work_id in sorted(game_config.config_work_type):
        if work_id and game_config.config_work_type[work_id].ability_id == best_ability_id:
            work_name = game_config.config_work_type[work_id].name
            break
    if not work_name:
        return _("\n{0}在[{1}]上的天赋最为突出\n").format(character_data.name, ability_name)
    return _("\n{0}在[{1}]上的天赋最为突出，或许适合去做[{2}]\n").format(
        character_data.name, ability_name, work_name)


# ---------------------------------------------------------------------------
# 养成数值的统一读写口（Plan 22 三期）
# ---------------------------------------------------------------------------


def get_stage_start_day(character_id: int) -> int:
    """
    取角色当前成长阶段的起点（累计有效成长天数）
    阶段阈值是**累计**天数（婴儿0~90 / 幼女90~270 / 萝莉270~450 / 少女450起），起点即上一阶段的阈值
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 起点天数：婴儿0 / 幼女90 / 萝莉270 / 少女450；不在成长阶段时为0
    """
    from Script.System.Pregnancy_System import pregnancy_constant

    stage = get_character_stage(character_id)
    if stage == 102:
        return pregnancy_constant.REARING_COMPLETE_DAY
    if stage == 103:
        return pregnancy_constant.GROW_TO_LOLI_DAY
    if stage == 104:
        return pregnancy_constant.GROW_TO_GIRL_DAY
    return 0


def get_grow_day_time(character_id: int, grow_day: int) -> datetime.datetime:
    """
    把一个有效成长天数换算回日历时刻（Plan 32 §3.2：阶段的起点、终点）
    Keyword arguments:
    character_id -- 角色id
    grow_day -- 有效成长天数（阶段阈值：婴儿0 / 幼女90 / 萝莉270 / 少女450）
    Return arguments:
    datetime.datetime -- 出生时刻 + (有效成长天数 − 成长加速药累计天数) 天；早于出生的按出生算
    功能: 有效成长天数 = 出生以来的日历天数 + 成长加速药累计的天数（pregnancy_handle.get_child_grow_day，加速药取整），
             所以这里算出的就是有效成长天数走到该值的那一刻；用过加速药的，阶段的起点与终点整段往前挪。
          阶段转换（长大）本身仍按有效成长天数判，不走这里。只读
    """
    character_data: game_type.Character = cache.character_data[character_id]
    acceleration_day = int(getattr(character_data.pregnancy, "growth_acceleration_days", 0))
    return character_data.pregnancy.born_time + datetime.timedelta(days=max(0, grow_day - acceleration_day))


def get_stage_day(character_id: int) -> int:
    """
    取角色在当前成长阶段里已经过了几个可游玩天（Plan 29 §3.3；Plan 32 §3.2 起按可游玩天）
    进入该阶段当天为第0天，养成事件的抬头写「第 N+1 天」。
       阶段的起点是有效成长天数走到本阶段阈值的那一刻（get_grow_day_time），从那一刻数到此刻的**可游玩天**（game_time.count_play_day）：
       游戏时钟只有 3 / 6 / 9 / 12 四个季月，按日历天数的话季月交替那一夜会跳约 60 天，「萝莉期第 23 天」一夜变成「第 85 天」。
       成长停滞解除后按阈值一次长大时，这个数会比实际偏大——与养成数值 3（阶段进度）是同一个近似，阶段的实际起点不入档
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 本阶段已过的可游玩天数，不小于0；不是孩子、或没有可认的出生日（born_time 为缺省的公元 1 年）时为0
    """
    from Script.Design import game_time

    if character_id not in cache.character_data or not get_character_stage(character_id):
        return 0
    # born_time 还是缺省值的角色不是在岛上出生的（世界设定「萝莉化」、自带年龄素质的干员），没有可认的阶段起点；
    #    也免得从公元 1 年起逐月累加两千多年
    if cache.character_data[character_id].pregnancy.born_time.year <= 1:
        return 0
    stage_start_time = get_grow_day_time(character_id, get_stage_start_day(character_id))
    return game_time.count_play_day(stage_start_time, cache.game_time)


def get_stage_progress(character_id: int) -> float:
    """
    取角色在当前成长阶段里已经走过的进度百分比（Plan 32 §3.2 起按可游玩天）

    进度 = 本阶段已过的可游玩天（get_stage_day） ÷ 本阶段一共的可游玩天。
       阶段阈值是**累计**的有效成长天数（婴儿0~90 / 幼女90~270 / 萝莉270~450），起点、终点都换算回日历时刻（get_grow_day_time）再数可游玩天，
       于是婴儿期约 30 天、幼女 / 萝莉期约 60 天。按日历天的话季月交替那一夜进度会跳约 68（婴儿）/ 34（幼女、萝莉）个百分点，
       比一次跳跃窄的事件窗口（如婴儿中期 [30, 75)）对多数出生日期一天都开不出来。
       阶段转换（长大）仍按有效成长天数，不变
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    float -- 0~100 的进度百分比；已成年、不在成长阶段、或没有可认的出生日时为100
    """
    from Script.Design import game_time
    from Script.System.Pregnancy_System import pregnancy_handle

    stage_end = pregnancy_handle.get_child_growth_stage_total_day(character_id)
    if not stage_end:
        # 已经不在成长阶段（成年或不是孩子），按走完算
        return 100.0
    if cache.character_data[character_id].pregnancy.born_time.year <= 1:
        # 没有可认的出生日（不是在岛上出生的），与按日历天算时一样按走完算
        return 100.0
    stage_start_time = get_grow_day_time(character_id, get_stage_start_day(character_id))
    stage_end_time = get_grow_day_time(character_id, stage_end)
    stage_total = game_time.count_play_day(stage_start_time, stage_end_time)
    if stage_total <= 0:
        return 100.0
    return max(0.0, min(100.0, get_stage_day(character_id) * 100.0 / stage_total))


def get_growth_value(character_id: int, value_id: int) -> float:
    """
    读取养成数值，供 CVP_A1_Growth|N_运算_值 前提与面板共用

    这是养成数值的**唯一读口**：前提、事件、面板都从这里取，
       免得同一个「出勤率」在三处各算各的、口径不一致
    Keyword arguments:
    character_id -- 角色id
    value_id -- 养成数值编号（GROWTH_VALUE_* 常量）
    Return arguments:
    float -- 数值，角色没有养成数据时一律为0（出勤率为100）
    """
    from Script.System.Education_System import semester_handle

    # 阶段进度不依赖养成数据，要在下面的提前返回之前算：
    #    没有 child_growth 的孩子（旧档、刚出生）照样有成长天数
    if value_id == education_constant.GROWTH_VALUE_STAGE_PROGRESS:
        return get_stage_progress(character_id)
    # 学期进度同理，它是全岛共用的时间量，与这个角色有没有养成数据无关
    if value_id == education_constant.GROWTH_VALUE_SEMESTER_PROGRESS:
        return semester_handle.get_semester_progress()
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None:
        # 没有养成数据时，成绩单档位要回落到 -1（尚无成绩单）而不是 0——
        #    0 是「优秀」，回落成 0 会让全岛没上过学的人都通过优秀档的口上前提
        if value_id == education_constant.GROWTH_VALUE_REPORT_GRADE:
            return float(education_constant.REPORT_GRADE_NONE)
        if value_id in {education_constant.GROWTH_VALUE_ATTEND_RATE, education_constant.GROWTH_VALUE_SEMESTER_ATTEND_RATE}:
            return 100.0
        return 0.0
    if value_id == education_constant.GROWTH_VALUE_ATTEND:
        return float(growth_data.attend_class_count)
    if value_id == education_constant.GROWTH_VALUE_ABSENT:
        return float(growth_data.absent_count)
    if value_id == education_constant.GROWTH_VALUE_ATTEND_RATE:
        total = growth_data.attend_class_count + growth_data.absent_count
        # 一节课都还没轮到过的孩子不该被当成全勤缺席，按满勤算
        if not total:
            return 100.0
        return growth_data.attend_class_count * 100.0 / total
    # 本学期的三个数走 semester_handle：那边是「累计减基线」的唯一算口
    if value_id in {education_constant.GROWTH_VALUE_SEMESTER_ATTEND, education_constant.GROWTH_VALUE_SEMESTER_ABSENT, education_constant.GROWTH_VALUE_SEMESTER_ATTEND_RATE}:
        semester_attend, semester_absent = semester_handle.get_semester_attend(character_id)
        if value_id == education_constant.GROWTH_VALUE_SEMESTER_ATTEND:
            return float(semester_attend)
        if value_id == education_constant.GROWTH_VALUE_SEMESTER_ABSENT:
            return float(semester_absent)
        semester_total = semester_attend + semester_absent
        # 本学期还一节课都没轮到过的孩子不该被当成全勤缺席，按满勤算（与终身出勤率同口径）
        if not semester_total:
            return 100.0
        return semester_attend * 100.0 / semester_total
    last_report_card = semester_handle.get_last_report_card(character_id)
    if value_id == education_constant.GROWTH_VALUE_REPORT_GRADE:
        # 没有成绩单时是 -1 而不是 0：0 是「优秀」档
        if not last_report_card:
            return float(education_constant.REPORT_GRADE_NONE)
        return float(last_report_card.get("grade", education_constant.REPORT_GRADE_NONE))
    if value_id == education_constant.GROWTH_VALUE_REPORT_LEVEL_UP:
        return float(len(last_report_card.get("level_change", {})))
    if education_constant.GROWTH_VALUE_PERSONALITY_BASE <= value_id <= education_constant.GROWTH_VALUE_PERSONALITY_BASE + 3:
        return float(growth_data.personality_point.get(value_id - education_constant.GROWTH_VALUE_PERSONALITY_BASE, 0.0))
    if value_id == education_constant.GROWTH_VALUE_CARE:
        return float(growth_data.care_point)
    if value_id == education_constant.GROWTH_VALUE_PRENATAL:
        return float(growth_data.prenatal_point)
    if value_id == education_constant.GROWTH_VALUE_EVENT_COUNT:
        return float(len(growth_data.event_history))
    # 成绩单待查看（Plan 27 §3.6）：没有养成数据的走上面的提前返回，同样是 0
    if value_id == education_constant.GROWTH_VALUE_REPORT_PENDING:
        return 1.0 if growth_data.report_card_flag else 0.0
    # 累计翘课节数（Plan 30）：翘掉的课也记在编号 1 的累计缺课里，要单看翘课读这一项
    if value_id == education_constant.GROWTH_VALUE_SKIP:
        return float(growth_data.skip_count)
    # 累计实操课次数（Plan 31）：口上里「第一次来 / 老学生」读它，不读含全部课型的编号 0
    if value_id == education_constant.GROWTH_VALUE_SEX_CLASS:
        return float(growth_data.sex_class_count)
    return 0.0


def change_growth_value(character_id: int, value_id: int, add_value: float):
    """
    改写养成数值，供 CVE_A1_Growth|N_G/L/E_值 结算使用

    只有性格倾向与照料值是可写的：出勤数由上课结算记账、胎教值由妊娠期写入，
       让事件去改它们会让面板上的「听课N节」变成一个谁都对不上的数（口径33 也不允许事件动能力）
    已成年的女儿改写性格倾向后即重选这一对素质（Plan 32 §3.4，settle_adult_personality_pair）
    Keyword arguments:
    character_id -- 角色id
    value_id -- 养成数值编号（GROWTH_VALUE_* 常量）
    add_value -- 增减量，已按运算符取好正负；运算符为E时是直接赋的目标值
    Return arguments:
    无
    """
    growth_data = get_child_growth(character_id)
    if education_constant.GROWTH_VALUE_PERSONALITY_BASE <= value_id <= education_constant.GROWTH_VALUE_PERSONALITY_BASE + 3:
        pair_id = value_id - education_constant.GROWTH_VALUE_PERSONALITY_BASE
        growth_data.personality_point[pair_id] = growth_data.personality_point.get(pair_id, 0.0) + add_value
        settle_adult_personality_pair(character_id, pair_id)
    elif value_id == education_constant.GROWTH_VALUE_CARE:
        # 照料值不设上限但不允许为负
        growth_data.care_point = max(0.0, growth_data.care_point + add_value)


def set_growth_value(character_id: int, value_id: int, new_value: float):
    """
    直接把养成数值设为指定值（CVE 的 E 运算）
    已成年的女儿改写性格倾向后即重选这一对素质（Plan 32 §3.4，settle_adult_personality_pair）
    Keyword arguments:
    character_id -- 角色id
    value_id -- 养成数值编号（GROWTH_VALUE_* 常量）
    new_value -- 目标值
    Return arguments:
    无
    """
    growth_data = get_child_growth(character_id)
    if education_constant.GROWTH_VALUE_PERSONALITY_BASE <= value_id <= education_constant.GROWTH_VALUE_PERSONALITY_BASE + 3:
        pair_id = value_id - education_constant.GROWTH_VALUE_PERSONALITY_BASE
        growth_data.personality_point[pair_id] = new_value
        settle_adult_personality_pair(character_id, pair_id)
    elif value_id == education_constant.GROWTH_VALUE_CARE:
        growth_data.care_point = max(0.0, new_value)
