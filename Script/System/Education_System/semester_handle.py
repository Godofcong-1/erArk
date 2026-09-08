"""学期切换与成绩单（Plan 22 一期 §3.13，兑现总纲口径 35 与 43）

游戏一年只有 3/6/9/12 四个季月（总纲 §2.3-7），天然就是四个学期，
学期起止即季月的切换，不另造时间周期。

⚠️ 本轮之前这条链是**半截**的：`CHILD_GROWTH.report_card_flag` 字段早就有，
   但全仓库没有任何一处把它置 True，「检查成绩单」读的又是**终身累计**的听课与缺课数，
   于是玩家看多少次都是同一份从出生算起的总账。本模块把缺的那半截补上。

本模块是纯函数层：只算与写数据，不碰任何绘制，面板与结算只取用
（照 auto_schedule.py 与 Dormitory_System/common.py 的分层）。

⚠️ **终身累计的语义不变**。attend_class_count / absent_count 仍然只增不减，
   养成总览要用它们展示这孩子一辈子上过多少课；本学期的数一律由「累计 - 学期基线」得出。
   所以上课结算的三个写入点（growth_handle / class_ai / sex_class_handle）一行都不用改。

⚠️ 成绩单必须**冻结**成快照而不是查看时现算：新学期一开课，现算出来的数就变了，
   玩家隔两天再看「同一份」成绩单会得到不一样的内容。
"""
import calendar
from typing import Dict, List, Tuple

from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.Design import game_time, attr_calculation
from Script.System.Education_System import growth_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_ = get_text._
""" 翻译api """

SEMESTER_NAME = {3: "春季学期", 6: "夏季学期", 9: "秋季学期", 12: "冬季学期"}
""" 四个季月各自对应的学期名，键即 game_time.get_season_month() 的返回值 """

REPORT_GRADE_EXCELLENT = 0
""" 成绩档位：优秀 """
REPORT_GRADE_GOOD = 1
""" 成绩档位：良好 """
REPORT_GRADE_POOR = 2
""" 成绩档位：待努力 """
REPORT_GRADE_NO_CLASS = 3
""" 成绩档位：无课可评。本学期一节课都没排，不该被评成「待努力」——那是玩家没排课，不是孩子的问题 """
REPORT_GRADE_NONE = -1
""" 档位读口的空值：这孩子还没有过成绩单。
    ⚠️ 绝不能用0兜底——0是「优秀」，会让全岛没上过学的人都通过优秀档的口上前提 """

REPORT_GRADE_NAME = {
    REPORT_GRADE_EXCELLENT: "优秀",
    REPORT_GRADE_GOOD: "良好",
    REPORT_GRADE_POOR: "待努力",
    REPORT_GRADE_NO_CLASS: "本学期没有排课",
}
""" 各档位的显示名 """

EXCELLENT_RATE = 90
""" 评为优秀所需的出勤率下限（百分比） """

EXCELLENT_LEVEL_UP = 2
""" 评为优秀所需的本学期升级科目数下限。⚠️ 光靠不缺课评不上优秀，还得真学出东西来 """

GOOD_RATE = 70
""" 评为良好所需的出勤率下限（百分比），低于此为待努力 """


def get_semester_name(year: int, month: int) -> str:
    """
    取学期的显示名
    Keyword arguments:
    year -- 年份
    month -- 季月（3/6/9/12）
    Return arguments:
    str -- 如 "2026年 秋季学期"
    """
    return _("{0}年 {1}").format(year, _(SEMESTER_NAME.get(month, "学期")))


def get_semester_day_total(year: int, month: int) -> int:
    """
    取一个学期有多少天
    ⚠️ 学期长度就是**这个季月的日历天数**（28~31），不是笼统的「约30天」：
       切月时 sub_time_now 会把日期 replace(day=1)，非季月被时钟整段跳过，
       所以一个学期恰好等于这个季月本身。写死30会在2月与大月上各错一两天
    Keyword arguments:
    year -- 年份
    month -- 季月（3/6/9/12）
    Return arguments:
    int -- 天数
    """
    return calendar.monthrange(year, month)[1]


def get_semester_progress() -> float:
    """
    取本学期已经过去的进度百分比
    Keyword arguments:
    无
    Return arguments:
    float -- 0~100，季月第1天为0、最后一天为100
    """
    year, month = game_time.get_now_semester()
    day_total = get_semester_day_total(year, month)
    if day_total <= 1:
        return 100.0
    return max(0.0, min(100.0, (cache.game_time.day - 1) * 100.0 / (day_total - 1)))


def get_semester_left_day() -> int:
    """
    取本学期还剩几天（不含今天）
    Keyword arguments:
    无
    Return arguments:
    int -- 剩余天数
    """
    year, month = game_time.get_now_semester()
    return max(0, get_semester_day_total(year, month) - cache.game_time.day)


def judge_semester_half_passed() -> bool:
    """
    校验本学期是否已经过半（方案 §3.13：学期中途也允许改课表，但要给出提示）
    Keyword arguments:
    无
    Return arguments:
    bool -- 是否已过半
    """
    return get_semester_progress() >= 50


def get_semester_head_text() -> str:
    """
    取教育管理系统顶部那行学期抬头
    Keyword arguments:
    无
    Return arguments:
    str -- 如 "2026年 秋季学期 · 第 12 / 30 天（已过 38%）"
    """
    year, month = game_time.get_now_semester()
    return _("{0} · 第 {1} / {2} 天（已过 {3}%）").format(
        get_semester_name(year, month), cache.game_time.day,
        get_semester_day_total(year, month), int(get_semester_progress()))


def get_semester_attend(character_id: int) -> Tuple[int, int]:
    """
    取某个孩子本学期的听课与缺课节数
    ⚠️ 这是「本学期出勤」的唯一算口：累计减学期基线。
       面板、前提读口、成绩单三处都从这里取，免得各算各的
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Tuple[int, int] -- (本学期听课节数, 本学期缺课节数)
    """
    if character_id not in cache.character_data:
        return 0, 0
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None:
        return 0, 0
    # 夹到0：基线理论上不会超过累计，但存档迁移或调试改数时可能出现，负数出勤毫无意义
    attend_count = max(0, growth_data.attend_class_count - growth_data.semester_base_attend)
    absent_count = max(0, growth_data.absent_count - growth_data.semester_base_absent)
    return attend_count, absent_count


def get_semester_attend_rate(attend_count: int, absent_count: int) -> int:
    """
    按听课与缺课节数算出勤率
    Keyword arguments:
    attend_count -- 听课节数
    absent_count -- 缺课节数
    Return arguments:
    int -- 出勤率百分比0~100；一节课都没轮到过时算作100（与终身出勤率同口径）
    """
    total_count = attend_count + absent_count
    if not total_count:
        return 100
    return int(attend_count * 100 / total_count)


def get_semester_level_change(character_id: int) -> Dict[int, List[int]]:
    """
    取某个孩子本学期涨了级的科目
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Dict[int, List[int]] -- 键为科目能力id，值为[本学期开始时的等级, 现在的等级]，只含真涨了的
    """
    # ⚠️ 函数内import：class_schedule_panel 是面板模块，提到文件顶层会循环导入
    from Script.System.Education_System.class_schedule_panel import SUBJECT_ABILITY_LIST

    result: Dict[int, List[int]] = {}
    if character_id not in cache.character_data:
        return result
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return result
    for ability_id in SUBJECT_ABILITY_LIST:
        # ⚠️ ability 的值可能是 float，比较前一律 int()
        now_level = int(character_data.ability.get(ability_id, 0))
        base_level = int(growth_data.semester_base_ability.get(ability_id, 0))
        if now_level > base_level:
            result[ability_id] = [base_level, now_level]
    return result


def get_top_ability(character_id: int) -> Tuple[int, int]:
    """
    取某个孩子当前等级最高的科目
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Tuple[int, int] -- (科目能力id, 等级)，一门都没学过则为(-1, 0)
    """
    from Script.System.Education_System.class_schedule_panel import SUBJECT_ABILITY_LIST

    if character_id not in cache.character_data:
        return -1, 0
    character_data: game_type.Character = cache.character_data[character_id]
    top_ability_id = -1
    top_level = 0
    # ⚠️ SUBJECT_ABILITY_LIST 本身是升序列表，用严格大于比较，并列时取id小的那门，结果可复现
    for ability_id in SUBJECT_ABILITY_LIST:
        now_level = int(character_data.ability.get(ability_id, 0))
        if now_level > top_level:
            top_level = now_level
            top_ability_id = ability_id
    return top_ability_id, top_level


def get_report_grade(attend_count: int, absent_count: int, level_up_count: int) -> int:
    """
    按本学期的出勤与升级情况评出成绩档位
    Keyword arguments:
    attend_count -- 本学期听课节数
    absent_count -- 本学期缺课节数
    level_up_count -- 本学期升级的科目数
    Return arguments:
    int -- REPORT_GRADE_* 常量
    """
    # 一节课都没排过的学期不评档：那是玩家没排课，评成「待努力」是冤枉孩子
    if attend_count + absent_count == 0:
        return REPORT_GRADE_NO_CLASS
    attend_rate = get_semester_attend_rate(attend_count, absent_count)
    # 优秀要「既没缺课、又真学出了东西」，光靠出勤刷不出来
    if attend_rate >= EXCELLENT_RATE and level_up_count >= EXCELLENT_LEVEL_UP:
        return REPORT_GRADE_EXCELLENT
    if attend_rate >= GOOD_RATE:
        return REPORT_GRADE_GOOD
    return REPORT_GRADE_POOR


def build_report_card(character_id: int) -> dict:
    """
    结算一份成绩单快照（纯计算，不写任何字段）
    Keyword arguments:
    character_id -- 孩子的角色id
    Return arguments:
    dict -- 成绩单快照，各字段见函数内注释
    """
    growth_data = growth_handle.get_child_growth(character_id)
    # ⚠️ 学期号取 semester_id 而不是当前学期：学期结算时时钟已经走进新学期了，
    #    这份成绩单属于**刚结束的那个**学期
    if growth_data.semester_id:
        year, month = growth_data.semester_id[0], growth_data.semester_id[1]
    else:
        year, month = game_time.get_now_semester()
    attend_count, absent_count = get_semester_attend(character_id)
    level_change = get_semester_level_change(character_id)
    top_ability_id, top_level = get_top_ability(character_id)
    return {
        "year": year,                   # 这份成绩单属于哪一年
        "month": month,                 # 属于哪个季月（3/6/9/12）
        "attend": attend_count,         # 本学期听课节数
        "absent": absent_count,         # 本学期缺课节数
        "rate": get_semester_attend_rate(attend_count, absent_count),   # 出勤率百分比
        "level_change": level_change,   # {科目能力id: [起始等级, 结束等级]}，只含涨了的
        "top_ability": top_ability_id,  # 学期末等级最高的科目，一门都没学过为-1
        "top_level": top_level,         # 该科目的等级
        "grade": get_report_grade(attend_count, absent_count, len(level_change)),
    }


def reset_semester_baseline(character_id: int, semester_id: List[int]) -> None:
    """
    把某个孩子的学期基线重置为当前值，并记下现在是哪个学期
    Keyword arguments:
    character_id -- 孩子的角色id
    semester_id -- 新学期号 [年int, 季月int]
    Return arguments:
    无
    """
    from Script.System.Education_System.class_schedule_panel import SUBJECT_ABILITY_LIST

    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = growth_handle.get_child_growth(character_id)
    # ⚠️ 存的是 list 的**副本**：直接存传进来的那个对象，多个孩子会共享同一个 list
    growth_data.semester_id = list(semester_id)
    growth_data.semester_base_attend = growth_data.attend_class_count
    growth_data.semester_base_absent = growth_data.absent_count
    growth_data.semester_base_ability = {
        ability_id: int(character_data.ability.get(ability_id, 0)) for ability_id in SUBJECT_ABILITY_LIST}


def settle_semester_change() -> List[int]:
    """
    学期切换的总入口：逐个孩子比对学期号，切了就出成绩单并重置基线

    ⚠️ 用「逐孩比对学期号」而不是全局切月标记，于是天然幂等、天然自愈：
       同一天调两次不会出两份成绩单；学期中途出生的、中途长成幼女的、旧存档里的孩子
       都各自从自己第一次被看到的那天起算，不需要任何全局状态，也不需要存档迁移
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 本次新出了成绩单的孩子角色id列表，没有则为空
    """
    now_semester = list(game_time.get_now_semester())
    report_list: List[int] = []
    # ⚠️ 只遍历在学的女儿。普通干员也能选课攒听课数（口径24），但他们不出成绩单；
    #    改成遍历全角色会给全岛每个人惰性创建 CHILD_GROWTH 并写进存档
    for character_id in growth_handle.get_student_candidate_list():
        growth_data = growth_handle.get_child_growth(character_id)
        # 第一次记账（刚长成幼女 / 旧存档 / 新开局）：只立基线，不出成绩单
        if not growth_data.semester_id:
            reset_semester_baseline(character_id, now_semester)
            continue
        if growth_data.semester_id == now_semester:
            continue
        growth_data.last_report_card = build_report_card(character_id)
        growth_data.report_card_flag = True
        reset_semester_baseline(character_id, now_semester)
        report_list.append(character_id)
    return report_list


def get_level_change_text(level_change: Dict[int, List[int]]) -> str:
    """
    把本学期的等级变化拼成一行文本
    Keyword arguments:
    level_change -- {科目能力id: [起始等级, 结束等级]}
    Return arguments:
    str -- 如 "学识技能 C4→B5、话术技能 D3→C4"，一门都没涨过则为空串
    """
    text_list = []
    # ⚠️ 按能力id排序：虽然构造时已经有序，但这份 dict 会进存档，排一次才不受旧档顺序影响
    for ability_id in sorted(level_change.keys()):
        if ability_id not in game_config.config_ability:
            continue
        old_level, new_level = level_change[ability_id]
        text_list.append("{0} {1}→{2}".format(
            game_config.config_ability[ability_id].name,
            attr_calculation.judge_grade(old_level), attr_calculation.judge_grade(new_level)))
    return "、".join(text_list)


def get_report_card_text(character_id: int, report_data: dict, finished: bool) -> str:
    """
    把一份成绩单拼成可直接打印的正文
    Keyword arguments:
    character_id -- 孩子的角色id
    report_data -- 成绩单快照（build_report_card 的产物）
    finished -- 这个学期是否已经结束，False时抬头改为「本学期尚未结束」
    Return arguments:
    str -- 成绩单正文
    """
    from Script.System.Education_System.class_schedule_panel import SUBJECT_ABILITY_LIST

    character_data: game_type.Character = cache.character_data[character_id]
    semester_text = get_semester_name(report_data.get("year", 0), report_data.get("month", 0))
    info_text = _("\n※※※※※※※※※\n")
    if finished:
        info_text += _("\n{0}　{1}的成绩单\n").format(semester_text, character_data.name)
    else:
        # 学期中途也允许查看（指令随时可用），此时给的是截至目前的进行时数据
        info_text += _("\n{0}　{1}的成绩单（本学期尚未结束，以下是截至目前的情况）\n").format(
            semester_text, character_data.name)
    info_text += _("\n出勤：{0} 节，缺课：{1} 节（出勤率 {2}%）\n").format(
        report_data.get("attend", 0), report_data.get("absent", 0), report_data.get("rate", 100))
    level_text = get_level_change_text(report_data.get("level_change", {}))
    if level_text:
        info_text += _("\n本学期的进步：{0}\n").format(level_text)
    else:
        info_text += _("\n本学期的进步：没有科目升级\n")
    # 各科水平只列已经学出等级的那几门：全18门铺开会把结算界面刷屏
    ability_text_list = []
    for ability_id in SUBJECT_ABILITY_LIST:
        now_level = int(character_data.ability.get(ability_id, 0))
        if now_level > 0:
            ability_text_list.append("{0}{1}".format(
                game_config.config_ability[ability_id].name, attr_calculation.judge_grade(now_level)))
    info_text += _("\n各科水平：{0}\n").format("、".join(ability_text_list) if ability_text_list else _("尚无成绩"))
    info_text += _("\n评定：{0}\n").format(
        _(REPORT_GRADE_NAME.get(report_data.get("grade", REPORT_GRADE_NO_CLASS), "无课可评")))
    info_text += _("\n※※※※※※※※※\n")
    return info_text
