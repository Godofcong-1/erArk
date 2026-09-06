"""生长养成的能力成长计算（Plan 22 一期）

⚠️ 本模块**完全复用既有的能力成长链**，不另造一套平行的经验体系：

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
       所以性技理论课只能攒珠，经验要靠实操课（四期）来补 —— 理论与实操天然两条腿。
"""
from typing import Dict, Optional
from Script.Core import cache_control, game_type
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

CHILD_TALENT_SET = {101, 102, 103, 104}
""" 成长链的四个年龄素质：101婴儿 / 102幼女 / 103萝莉 / 104少女 """

EDUCATION_ZONE_NAME = "教育区"
""" 教育区在 Facility_effect.csv 中的设施名（该表按名字索引） """

EDUCATION_ZONE_CID = 15
""" 教育区在 Facility.csv:22 中的设施id，用于查 Rhodes_Island.facility_level """

LEARN_STATE_ID = 9
""" 习得状态id（CharacterState.csv:15），睡眠结算时换算为习得珠(juel 9) """

COURSE_LEARN_BASE = {
    0: 30,   # 理论课，沿用既有授课结算的默认基础值
    1: 50,   # 实践课，教室容量小、单位收益更高
    2: 15,   # 大礼堂公开课，容纳全部孩子、单位收益低
    5: 40,   # 实习课，实地跟岗，介于理论(30)与实践(50)之间
}
""" 各班级式课型的单节课习得基础值（草案，实施时以实测为准）。
    最终习得值 = (上课分钟数 + 本值) × 速度系数 × 教育区加成 × 素质修正 """

COURSE_EXP_BASE = {
    0: 3,    # 理论课
    1: 5,    # 实践课
    2: 1,    # 大礼堂公开课
    5: 4,    # 实习课
}
""" 各班级式课型的单节课科目经验基础值（草案）。科目经验是分科的，决定单科能升到多高 """

SELF_STUDY_LEARN_BASE = 15
""" 自习（本节无教师）的习得基础值；无教师则无等级差可算，速度系数恒取1.0 """

SELF_STUDY_EXP_BASE = 1
""" 自习的科目经验基础值 """

CLASSROOM_COURSE_TYPE_SET = {0, 1, 2}
""" 班级式课型（理论/实践/公开）。⚠️ 与 schedule_handle 同名常量一致，此处另写一份是为了
    避免两个模块互相 import——schedule_handle 已经在函数里反向 import 了 growth_handle """


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


def judge_is_child(character_id: int) -> bool:
    """
    校验角色是否处于成长链的四个年龄阶段之一（婴儿/幼女/萝莉/少女）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否为成长中的孩子
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for talent_id in CHILD_TALENT_SET:
        if character_data.talent.get(talent_id, 0):
            return True
    return False


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
    ⚠️ Facility_effect.csv 里教育区各级的 effect 列（Lv1=0 / Lv2=5 / Lv3=20 / Lv4=50 / Lv5=100）
       此前在代码中从未被读取，介绍文案却已向玩家承诺了"成长效率加成提升至20%/50%/100%"。
       本计划把它接到上课结算上，兑现这个承诺。
    Keyword arguments:
    无
    Return arguments:
    float -- 倍率，如 Lv5 时为 2.0
    """
    now_level = cache.rhodes_island.facility_level.get(EDUCATION_ZONE_CID, 1)
    cid_list = game_config.config_facility_effect_data.get(EDUCATION_ZONE_NAME, [])
    # 该表的列表下标即设施等级（构建时补了个0占位），越界则按无加成处理
    if now_level < len(cid_list):
        effect_cid = cid_list[now_level]
        if effect_cid:
            return 1.0 + game_config.config_facility_effect[effect_cid].effect / 100
    return 1.0


def get_class_adjust(ability_id: int, student_id: int, teacher_id: int) -> float:
    """
    算一节课的总倍率（速度系数 × 教育区加成）
    Keyword arguments:
    ability_id -- 科目能力id
    student_id -- 学生的角色id
    teacher_id -- 授课教师的角色id，-1表示本节无教师（降级为自习）
    Return arguments:
    float -- 总倍率
    """
    zone_adjust = get_education_zone_adjust()
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
) -> None:
    """
    一节课的学生侧结算：累加习得状态值与该科目的经验
    ⚠️ 等级不在此处提升，而是走既有链在玩家睡觉时兑现（见模块头注释）
    Keyword arguments:
    student_id -- 学生的角色id
    teacher_id -- 授课教师的角色id，-1表示本节无教师（降级为自习）
    ability_id -- 科目能力id
    course_type -- 课型编号，决定基础值
    add_time -- 本次结算的分钟数
    change_data -- 结算信息记录对象
    change_data_to_target_change -- 交互对象的结算信息记录对象
    Return arguments:
    无
    """
    if not add_time:
        return
    # 延迟导入：Script.Settle 的包 __init__ 会连带载入指令系统，必须等配置初始化之后
    from Script.Settle import common_default

    no_teacher = teacher_id == -1 or teacher_id not in cache.character_data
    learn_base = COURSE_LEARN_BASE.get(course_type, COURSE_LEARN_BASE[0])
    exp_base = COURSE_EXP_BASE.get(course_type, COURSE_EXP_BASE[0])
    if no_teacher:
        # 教室课没老师就是自习，有一套自己的低档基础值；
        # 实习课没导师则是"见习"——照方案 §3.21 只把本岗位的基础值减半，而不是掉到自习档
        if course_type in CLASSROOM_COURSE_TYPE_SET:
            learn_base = SELF_STUDY_LEARN_BASE
            exp_base = SELF_STUDY_EXP_BASE
        else:
            learn_base = max(1, learn_base // 2)
            exp_base = max(1, exp_base // 2)
    adjust = get_class_adjust(ability_id, student_id, teacher_id)

    # 习得状态：ability_level 传 -1 表示不吃"教师能力修正"，避免与速度系数双重加成；
    # 倍率统一走 extra_adjust，这样 (上课分钟数 + 基础值) 整体被缩放
    common_default.base_chara_state_common_settle(
        student_id,
        add_time,
        LEARN_STATE_ID,
        base_value=learn_base,
        ability_level=-1,
        extra_adjust=adjust - 1.0,
        change_data=change_data,
        change_data_to_target_change=change_data_to_target_change,
    )

    # 科目经验：决定单科能升到多高
    exp_id = get_subject_exp_id(ability_id)
    if exp_id:
        final_exp = max(1, int(exp_base * adjust))
        common_default.base_chara_experience_common_settle(
            student_id,
            exp_id,
            base_value=final_exp,
            change_data=change_data,
            change_data_to_target_change=change_data_to_target_change,
        )

    # 记一节出勤
    growth_data = get_child_growth(student_id)
    growth_data.attend_class_count += 1


def settle_teacher_class_gain(
        teacher_id: int,
        ability_id: int,
        add_time: int,
        change_data=None,
) -> None:
    """
    一节课的教师侧结算：教师自己也获得当节所授科目的习得与经验（教学相长）
    ⚠️ 与既有实现的区别：既有 handle_teach_add_just 写死加学识，本函数改为加**当节所授科目**
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
        LEARN_STATE_ID,
        ability_level=int(teacher_data.ability.get(ability_id, 0)),
        change_data=change_data,
    )
    exp_id = get_subject_exp_id(ability_id)
    if exp_id:
        common_default.base_chara_experience_common_settle(teacher_id, exp_id, change_data=change_data)
