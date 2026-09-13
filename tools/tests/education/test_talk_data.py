# -*- coding: UTF-8 -*-
"""静态数据校验：教育相关口上的行为id / 前提 / 正文卫生，公务事件表体检"""
import subprocess

from _bootstrap import *  # noqa: F401,F403

open_all_classroom()
mother = make_character(102, "母亲", 0)
student = make_character(201, "女儿A", 152, daughter=True, stage=103, mother_id=102, born_days=300, position=classroom_path(_("理论教室一")))
pl.target_character_id = 201
E = education_constant

EDU_BEHAVIOR = {
    "teach", "attent_class", "self_study", "skip_class", "intern_class", "follow_mother", "free_play", "check_report_card",
    "show_off_study", "caught_skip_class", "start_sex_class", "end_sex_class", "join_sex_class", "watch_sex_class",
    "prenatal_talk", "prenatal_music", "prenatal_touch",
    "hold_child", "sing_children_song", "nuirse_child", "change_diapers", "teach_talk", "give_toy",
}
""" 生长养成系统涉及的行为（带教口上挂在导师自己的工作行为上，按前提 have_intern_student 另收） """

section("口上覆盖")
talk_list = [t for t in game_config.config_talk.values()
             if getattr(t, "behavior_id", "") in EDU_BEHAVIOR or "have_intern_student" in str(getattr(t, "premise", ""))]
# Plan 31 删掉 52 条腰技炫耀（M4）与 2 条授课 / 听课占位（L15）、新增 4 条档位 3 的检查成绩单口上（L14），总量约 2797 条
check("教育相关口上总量 ≥ 2750 条", len(talk_list) >= 2750, len(talk_list))
count_by_behavior = {}
for talk in talk_list:
    count_by_behavior[talk.behavior_id] = count_by_behavior.get(talk.behavior_id, 0) + 1
for behavior in sorted(EDU_BEHAVIOR):
    check(f"{behavior} 有口上（{count_by_behavior.get(behavior, 0)} 条）", count_by_behavior.get(behavior, 0) > 0)
check("翘课被抓有 ≥ 16 条", count_by_behavior.get("caught_skip_class", 0) >= 16)
for behavior in ("teach", "attent_class", "self_study", "show_off_study"):
    # M4（Plan 31）：炫耀只在科目升级成功后出，男性专属的腰技女儿永远升不上去，炫耀口上按女儿可学的 17 门覆盖；授课 / 听课 / 自习照旧 18 门
    subject_list = E.FEMALE_SUBJECT_LIST if behavior == "show_off_study" else E.SUBJECT_ABILITY_LIST
    subject_hit = set()
    for talk in talk_list:
        if talk.behavior_id != behavior:
            continue
        premise = str(talk.premise)
        for ability_id in subject_list:
            if f"Course|{ability_id}_" in premise or f"CourseShowOff|{ability_id}_" in premise:
                subject_hit.add(ability_id)
    check(f"{behavior} 覆盖全部 {len(subject_list)} 门科目", subject_hit == set(subject_list), sorted(set(subject_list) - subject_hit))
male_only_show_off = [
    talk.cid
    for talk in talk_list
    if talk.behavior_id == "show_off_study"
    and "daughter" in str(talk.premise)
    and any(f"CourseShowOff|{ability_id}_" in str(talk.premise) for ability_id in E.MALE_ONLY_SUBJECT_SET)
]
check("M4 男性专属科目（腰技）没有带女儿前提的炫耀口上（女儿的腰技永远升不上去，这类口上是死内容）", not male_only_show_off, male_only_show_off[:10])
check("M4 守卫：男性专属科目集合非空（为空时上一条恒真）", len(E.MALE_ONLY_SUBJECT_SET) > 0, E.MALE_ONLY_SUBJECT_SET)
check("M4 腰技炫耀口上文件已删除", not os.path.exists(os.path.join("data", "talk", "system", "second_show_off_study", "show_off_waist_skill.csv")))

section("行为与前提")
check("每条口上的行为都存在", all(talk.behavior_id in game_config.config_behavior for talk in talk_list))
bad_premise = []
bad_token = []
seen_token = set()
set_time(period_time(0))
for talk in talk_list:
    premise_text = str(getattr(talk, "premise", ""))
    if not premise_text or premise_text == "0":
        bad_premise.append(talk.cid)
        continue
    for token in premise_text.split("&"):
        token = token.strip()
        if not token:
            continue
        if token in seen_token:
            continue
        seen_token.add(token)
        if token in constant.handle_premise_data:
            continue
        if not token.startswith("CVP_"):
            bad_token.append((talk.cid, token))
            continue
        try:
            handle_premise.handle_premise(token, 201)
            handle_premise.handle_premise(token, 0)
        except Exception as error:
            bad_token.append((talk.cid, token, repr(error)))
check("没有前提为空的口上", not bad_premise, bad_premise[:10])
check("全部前提 token 已注册或可解析", not bad_token, bad_token[:10])
check(f"不同前提 token 共 {len(seen_token)} 个", len(seen_token) > 100)

section("正文卫生")
bad_context = []
for talk in talk_list:
    context = str(getattr(talk, "context", ""))
    if not context.strip() or "{}" in context or "{ Name}" in context:
        bad_context.append(talk.cid)
check("正文非空且无裸花括号", not bad_context, bad_context[:10])
check("正文占位符只用已知的几种", not [t.cid for t in talk_list if "{Nmae}" in str(t.context) or "{TargetNmae}" in str(t.context)])

section("公务事件表")
proc = subprocess.run([sys.executable, os.path.join("tools", "official_event_check.py"), "--quiet"], cwd=ROOT, capture_output=True, timeout=120)
check("official_event_check 通过", proc.returncode == 0, proc.stdout.decode("utf-8", errors="replace")[-600:])
growth_uid_list = [uid for uid, data in game_config.config_official_event.items() if data.get("department") == E.GROWTH_EVENT_DEPARTMENT]
check("养成事件 ≥ 250 条", len(growth_uid_list) >= 250, len(growth_uid_list))
check("毕业典礼与成年纪念存在", E.GRADUATION_EVENT_UID in game_config.config_official_event and E.ADULT_MEMORIAL_EVENT_UID in game_config.config_official_event)
check("期末桶 16 条且 sub_key 为保留键", len(game_config.config_official_event_by_sub_key.get((E.GROWTH_EVENT_DEPARTMENT, E.SEMESTER_EVENT_SUB_KEY), ())) >= 16)
# Plan 30 §3.2：期末事件在学期基线重置之后推送，前提不许读本学期的养成数值 4 / 5 / 6
import csv  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "tools"))
import official_event_check  # noqa: E402

with open(os.path.join("data", "official_event", "期末.csv"), encoding="utf-8", newline="") as _event_file:
    _event_rows = list(csv.reader(_event_file))
_row_9 = dict(zip(_event_rows[0], next(r for r in _event_rows[5:] if r and r[0] == "9")))
check("期末 9 / 10 的前提不再读本学期出勤率（此前带 6_L_70，推送时永远判不过）",
      all("Growth|6_" not in game_config.config_official_event[uid]["premise"] for uid in ("期末9", "期末10")) and "Growth|6_" not in _row_9["premise"])
_checker = official_event_check.Checker()
_checker.check_row("期末.csv", 14, dict(_row_9), set(), set())
check("校验工具：现在的期末 9 不报错", _checker.error_list == [], _checker.error_list)
_bad_row = dict(_row_9)
_bad_row["premise"] += "&CVP_A1_Growth|6_L_70"
_bad_row["option_2_premise"] = "CVP_A1_Growth|4_GE_1"
_bad_row["option_2_reason"] = "测试用"
_checker = official_event_check.Checker()
_checker.check_row("期末.csv", 14, _bad_row, set(), set())
check("校验工具新规则：期末事件的主前提、选项前提读养成数值 4 / 5 / 6 各报一条", sum("期末事件在学期基线重置之后推送" in one for one in _checker.error_list) == 2, _checker.error_list)
# ==== Plan 31：事件表的前提与正文对齐（L10 / L11 / L13），校验工具的新规则（L16 / M2） ====
NEW_PREMISE_LIST = [
    constant_promise.Premise.SELF_HAVE_THEORY_COURSE,
    constant_promise.Premise.SELF_HAVE_PRACTICE_COURSE,
    constant_promise.Premise.SELF_HAVE_PE_COURSE,
    constant_promise.Premise.SELF_HAVE_INTEREST_COURSE,
    constant_promise.Premise.SELF_HAVE_INTERN_COURSE,
    constant_promise.Premise.SELF_BIRTHDAY_TODAY,
]
""" Plan 31 新增的 6 个前提名（方案 §4.1）：按课型查课表的 5 个与生日前提 """
EVENT_PREMISE_EXPECT = {
    "L10": {
        "萝莉1": "CVP_A1_Growth|0_GE_20&CVP_A1_Growth|23_E_1&CVP_A1_Growth|7_NE_3",
        "萝莉6": "CVP_A1_Growth|4_GE_20&CVP_A1_Growth|5_E_0&self_have_any_course",
        "萝莉20": "self_have_any_course&CVP_A1_Growth|23_E_1&CVP_A1_Growth|7_NE_3",
        "萝莉26": "self_have_sibling_child&CVP_A1_Growth|23_E_1&CVP_A1_Growth|7_NE_3",
    },
    "L11": {
        "萝莉7": "self_have_pe_course",
        "萝莉8": "self_have_intern_course",
        "萝莉9": "self_have_interest_course",
        "萝莉16": "self_have_practice_course",
        "幼女1": "CVP_A1_Growth|0_GE_1&self_have_theory_course",
        "幼女22": "self_have_practice_course",
    },
    "L13": {
        "通用3": "CVP_A1_T|101_E_0&self_birthday_today",
        "通用15": "CVP_A1_Growth|9_GE_90",
        "婴儿4": "CVP_A1_Growth|3_GE_50",
        "婴儿50": "self_mother_available&CVP_A1_Growth|3_GE_60",
    },
}
""" Plan 31 方案 §4.3 改过前提的事件：发现编号 -> {事件uid: 新前提串} """
for finding, expect_dict in EVENT_PREMISE_EXPECT.items():
    for uid, premise_text in expect_dict.items():
        now_premise = game_config.config_official_event.get(uid, {}).get("premise", "")
        check(f"{finding} {uid} 的前提按方案 §4.3 改为 {premise_text}", now_premise == premise_text, now_premise)
check(
    "L11 / L13 事件表用到的 6 个新前提已注册（处理函数在 handle_premise_other，名字取自 constant_promise）",
    all(name in constant.handle_premise_data for name in NEW_PREMISE_LIST),
    [name for name in NEW_PREMISE_LIST if name not in constant.handle_premise_data],
)
premise_name_set = {value for key, value in vars(constant_promise.Premise).items() if key.isupper() and isinstance(value, str)}
bad_event_token = []
for expect_dict in EVENT_PREMISE_EXPECT.values():
    for uid, premise_text in expect_dict.items():
        for token in premise_text.split("&"):
            if token.startswith("CVP_"):
                try:
                    handle_premise.handle_premise(token, 201)
                except Exception as error:
                    bad_event_token.append((uid, token, repr(error)))
            elif token not in premise_name_set or token not in constant.handle_premise_data:
                bad_event_token.append((uid, token))
check("L10 / L11 / L13 改过的事件前提逐个 token 校验：前提名与 constant_promise 拼写一致且已注册，CVP 可解析", not bad_event_token, bad_event_token)
with open(os.path.join("data", "official_event", "萝莉.csv"), encoding="utf-8", newline="") as _event_file:
    _loli_rows = list(csv.reader(_event_file))
_loli_row = {r[0]: dict(zip(_loli_rows[0], r)) for r in _loli_rows[5:] if r and r[0].strip()}
check(
    "L10 萝莉 1 的正文与选项 2 不再点名「学识」「战斗」（成绩单只记涨了的科目，点名的科目她未必上过）",
    all(word not in _loli_row["1"]["text"] + _loli_row["1"]["option_2"] for word in ("学识", "战斗")),
    _loli_row["1"]["text"],
)
check("L10 萝莉 20 不再写「掉了两级」（科目只升不降），改为「一级都没涨」", "掉了两级" not in _loli_row["20"]["text"] and "一级都没涨" in _loli_row["20"]["text"], _loli_row["20"]["text"])
# L16：期末桶另禁养成数值 9 / 23，未成年（不许改能力）与宿舍（不许写育儿室）两条规则并入期末桶
check(
    "L16 校验工具抄的期末桶键与 education_constant 一致，且已并入未成年与宿舍两条规则",
    official_event_check.SEMESTER_SUB_KEY == E.SEMESTER_EVENT_SUB_KEY
    and E.SEMESTER_EVENT_SUB_KEY in official_event_check.CHILD_SUB_KEY
    and E.SEMESTER_EVENT_SUB_KEY in official_event_check.DORM_SUB_KEY,
)
_bad_row = dict(_row_9)
_bad_row["premise"] += "&CVP_A1_Growth|9_GE_50"
_bad_row["option_1_premise"] = "CVP_A1_Growth|23_E_1"
_bad_row["option_1_reason"] = "测试用"
_checker = official_event_check.Checker()
_checker.check_row("期末.csv", 14, _bad_row, set(), set())
check(
    "L16 校验工具新规则：期末事件的主前提读养成数值 9（推送当天恒为 0）、选项前提读 23（推送时恒为 1）各报一条",
    sum("期末事件在学期基线重置之后推送" in one for one in _checker.error_list) == 2,
    _checker.error_list,
)
_bad_row = dict(_row_9)
_bad_row["option_1_effect"] += "&CVE_A1_A|12_G_1"
_checker = official_event_check.Checker()
_checker.check_row("期末.csv", 14, _bad_row, set(), set())
check("L16 校验工具新规则：期末事件的选项改能力报一条（期末桶只推给幼女 / 萝莉，按未成年算）", sum("未成年阶段的事件选错不该掉能力" in one for one in _checker.error_list) == 1, _checker.error_list)
_bad_row = dict(_row_9)
_bad_row["text"] += "她说想先回育儿室看看。"
_checker = official_event_check.Checker()
_checker.check_row("期末.csv", 14, _bad_row, set(), set())
check("L16 校验工具新规则：期末事件的正文写育儿室报一条（幼女期起住自己的宿舍）", sum("正文不该再出现育儿室" in one for one in _checker.error_list) == 1, _checker.error_list)
_ok_row = dict(_loli_row["1"])
_ok_row["premise"] += "&CVP_A1_Growth|9_GE_50"
_checker = official_event_check.Checker()
_checker.check_row("萝莉.csv", 6, _ok_row, set(), set())
check("L16 对照：萝莉桶的事件读养成数值 9 不报错（新规则只拦期末桶；改过的萝莉 1 整行也通过）", _checker.error_list == [], _checker.error_list)
# M2：成年桶只收成年结算显式推入的事件
with open(os.path.join("data", "official_event", "通用.csv"), encoding="utf-8", newline="") as _event_file:
    _common_rows = list(csv.reader(_event_file))
_common_row = {r[0]: dict(zip(_common_rows[0], r)) for r in _common_rows[5:] if r and r[0].strip()}
check(
    "M2 校验工具抄的成年桶 uid 与 education_constant 一致（毕业典礼、成年纪念与 ADULT_EXTRA_EVENT_UID_LIST）",
    official_event_check.ADULT_EVENT_UID_SET == {E.GRADUATION_EVENT_UID, E.ADULT_MEMORIAL_EVENT_UID, *E.ADULT_EXTRA_EVENT_UID_LIST} and official_event_check.ADULT_SUB_KEY == 104,
)
check(
    "M2 通用 59 / 60 仍在养成部门的成年桶（sub_key 104），只能靠成年结算推入",
    all(
        game_config.config_official_event.get(uid, {}).get("department") == E.GROWTH_EVENT_DEPARTMENT and game_config.config_official_event.get(uid, {}).get("sub_key") == 104
        for uid in E.ADULT_EXTRA_EVENT_UID_LIST
    ),
)
_checker = official_event_check.Checker()
for _cid in ("1", "2", "59", "60"):
    _checker.check_row("通用.csv", 0, dict(_common_row[_cid]), set(), set())
check("M2 对照：成年结算显式推入的通用 1 / 2 / 59 / 60 放在成年桶里不报错", _checker.error_list == [], _checker.error_list)
_bad_row = dict(_common_row["59"])
_bad_row["cid"] = "61"
_checker = official_event_check.Checker()
_checker.check_row("通用.csv", 66, _bad_row, set(), set())
check("M2 校验工具新规则：成年桶里写了成年结算不推的事件（通用 61）报一条", sum("成年桶只有成年结算显式推入的事件会出现" in one for one in _checker.error_list) == 1, _checker.error_list)
_bad_row = dict(_loli_row["1"])
_bad_row["sub_key"] = "104"
_checker = official_event_check.Checker()
_checker.check_row("萝莉.csv", 6, _bad_row, set(), set())
check("M2 同上：萝莉的事件挪进成年桶同样报一条（uid 按「文件名 + cid」判）", sum("成年桶只有成年结算显式推入的事件会出现" in one for one in _checker.error_list) == 1, _checker.error_list)

section("Plan 31 口上对齐")


def talk_premise(talk_cid: str) -> str:
    """
    取一条口上的前提串（口上的 cid 在构建时拼成「上级目录名_文件名 + cid」，如 daily_check_report_card1014，见 buildconfig.build_csv_config）
    Keyword arguments:
    talk_cid -- 口上cid
    Return arguments:
    str -- 前提串，没有这条口上时为空串
    """
    talk_data = game_config.config_talk.get(talk_cid)
    return str(getattr(talk_data, "premise", "")) if talk_data is not None else ""


def premise_all(premise_text: str, character_id: int) -> bool:
    """
    逐个 token 判一串 & 连接的前提，全部成立才算成立（与口上 / 事件的前提口径一致）
    Keyword arguments:
    premise_text -- & 连接的前提串
    character_id -- 求值的角色id
    Return arguments:
    bool -- 是否全部成立；前提串为空时为 False，取不到口上时不会误判成立
    """
    token_list = [token.strip() for token in premise_text.split("&") if token.strip()]
    return bool(token_list) and all(handle_premise.handle_premise(token, character_id) for token in token_list)


OLD_HAND_TALK_LIST = ("sex_class_join_sex_class1053", "sex_class_join_sex_class1054", "sex_class_watch_sex_class1054", "sex_class_watch_sex_class1055")
""" 写「上过很多次实操课 / 老学生」的四条实操课口上（L12） """
FIRST_TIME_TALK_LIST = ("sex_class_join_sex_class1055", "sex_class_join_sex_class1056")
""" 写「第一次来上这种课」的两条实操课到场口上（L12） """
check(
    "L12 「老学生」四条改读累计实操课次数 Growth|25_GE_5，不再读含全部课型的累计听课节数",
    all("CVP_A1_Growth|25_GE_5" in talk_premise(cid) and "Growth|0_" not in talk_premise(cid) for cid in OLD_HAND_TALK_LIST),
    [talk_premise(cid) for cid in OLD_HAND_TALK_LIST],
)
check(
    "L12 「第一次来」两条改读累计实操课次数 Growth|25_LE_1",
    all("CVP_A1_Growth|25_LE_1" in talk_premise(cid) and "Growth|0_" not in talk_premise(cid) for cid in FIRST_TIME_TALK_LIST),
    [talk_premise(cid) for cid in FIRST_TIME_TALK_LIST],
)
check("L12 翘课 1004「第一次真的没去」带累计翘课数 ≤ 1", "CVP_A1_Growth|24_LE_1" in talk_premise("work_skip_class1004"), talk_premise("work_skip_class1004"))
growth_data = growth_handle.get_child_growth(201)
growth_data.attend_class_count = 20
growth_data.sex_class_count = 0
check("L12 上过 20 节普通课、一次实操课都没上过：「老学生」四条都判不过（改前读累计听课节数，四条都判得过）", not any(premise_all(talk_premise(cid), 201) for cid in OLD_HAND_TALK_LIST))
check("L12 同上：「第一次来」读的计数判得过", bool(handle_premise.handle_premise("CVP_A1_Growth|25_LE_1", 201)))
growth_data.sex_class_count = 5
check("L12 实操课上满 5 次：「老学生」四条都判得过", all(premise_all(talk_premise(cid), 201) for cid in OLD_HAND_TALK_LIST))
check("L12 同上：「第一次来」读的计数判不过", not handle_premise.handle_premise("CVP_A1_Growth|25_LE_1", 201))
growth_data.skip_count = 1
check("L12 累计翘课 1 节时翘课 1004 成立", premise_all(talk_premise("work_skip_class1004"), 201))
growth_data.skip_count = 2
check("L12 累计翘课 2 节时翘课 1004 不再成立", not premise_all(talk_premise("work_skip_class1004"), 201))
growth_data.attend_class_count = 0
growth_data.sex_class_count = 0
growth_data.skip_count = 0
# L14：档位 3（无课可评）的新成绩单
REPORT_NO_CLASS_TALK = {"daily_check_report_card1014": 102, "daily_check_report_card1015": 102, "daily_check_report_card1016": 103, "daily_check_report_card1017": 103}
""" Plan 31 新增的四条档位 3 口上：口上cid -> 限定的成长阶段素质 """
check(
    "L14 检查成绩单新增 4 条档位 3 口上（幼女 / 萝莉各 2 条），前提带档位 3 与成绩单待查看",
    all(
        "target_is_player_daughter" in talk_premise(cid)
        and f"CVP_A2_T|{stage}_E_1" in talk_premise(cid)
        and "CVP_A2_Growth|7_E_3" in talk_premise(cid)
        and "CVP_A2_Growth|23_E_1" in talk_premise(cid)
        for cid, stage in REPORT_NO_CLASS_TALK.items()
    ),
    [talk_premise(cid) for cid in REPORT_NO_CLASS_TALK],
)
check(
    "L14 讲「这学期每门课的心得」「那门课我上得最认真」的 1004 / 1005 加了档位不为 3",
    all("CVP_A2_Growth|7_NE_3" in talk_premise(cid) for cid in ("daily_check_report_card1004", "daily_check_report_card1005")),
)
growth_data.report_card_history = [{"grade": E.REPORT_GRADE_NO_CLASS}]
growth_data.report_card_flag = True
check(
    "L14 萝莉拿着档位 3 的新成绩单：萝莉的两条档位 3 口上成立，1004 / 1005 不再成立",
    premise_all(talk_premise("daily_check_report_card1016"), 0)
    and premise_all(talk_premise("daily_check_report_card1017"), 0)
    and not premise_all(talk_premise("daily_check_report_card1004"), 0)
    and not premise_all(talk_premise("daily_check_report_card1005"), 0),
)
growth_data.report_card_history = [{"grade": E.REPORT_GRADE_POOR}]
check(
    "L14 对照：档位 2 时 1004 / 1005 照旧成立，档位 3 口上不成立",
    premise_all(talk_premise("daily_check_report_card1004"), 0) and premise_all(talk_premise("daily_check_report_card1005"), 0) and not premise_all(talk_premise("daily_check_report_card1016"), 0),
)
growth_data.report_card_history = []
growth_data.report_card_flag = False
# L15：授课 / 听课的开发占位行
placeholder_list = [cid for cid, talk_data in game_config.config_talk.items() if talk_data.behavior_id in ("teach", "attent_class") and "指令的地文" in str(talk_data.context)]
check("L15 授课 / 听课的开发占位地文已删除（改前与正式口上同场按权重抽，NPC 教师开讲时约 1/3 抽中）", not placeholder_list, placeholder_list)
for behavior in ("teach", "attent_class"):
    with open(os.path.join("data", "talk", "work", f"{behavior}.csv"), encoding="utf-8", newline="") as _talk_file:
        _talk_rows = list(csv.reader(_talk_file))
    check(f"L15 {behavior}.csv 只剩表头 5 行（正式口上在同名子目录里）", len(_talk_rows) == 5, len(_talk_rows))

section("配置一致性")
check("Entertainment.csv 带 class_ok 列且 16 项可排兴趣课", sum(1 for cid in game_config.config_entertainment if getattr(game_config.config_entertainment[cid], "class_ok", 0)) == 16)
from Script.System.Pregnancy_System import pregnancy_constant

check("教育区娱乐排在 15x 段：151 过家家 / 152 照料卵 / 153 跟随母亲 / 154 自由玩耍 / 155 上课",
      [E.ENTERTAINMENT_PLAY_HOUSE, pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID, E.ENTERTAINMENT_FOLLOW_MOTHER, E.ENTERTAINMENT_FREE_PLAY, E.ENTERTAINMENT_SELF_STUDY] == [151, 152, 153, 154, 155]
      and all(cid in game_config.config_entertainment for cid in (151, 152, 153, 154, 155)))
check("旧编号 175~178 已不存在", not any(cid in game_config.config_entertainment for cid in (175, 176, 177, 178)))
check("过家家 / 跟随母亲 / 自由玩耍限幼女或萝莉", all(game_config.config_entertainment[cid].need == "T102|1/T103|1" for cid in (E.ENTERTAINMENT_PLAY_HOUSE, E.ENTERTAINMENT_FOLLOW_MOTHER, E.ENTERTAINMENT_FREE_PLAY)))
check("上课（无课时自习）限学生岗", game_config.config_entertainment[E.ENTERTAINMENT_SELF_STUDY].need == "W152|1")
check("日程专用三项不进随机池的集合与常量一致", E.SCHEDULE_ONLY_ENTERTAINMENT_SET == {153, 154, 155})
# 指令面板按 cid 排序并把 cid 显示为编号，段错了会排进别的类型（2026-09-09 第三轮把 2040 / 6906 / 6907 归位为 1036 / 5209 / 6021）
INSTRUCT_TYPE_SEGMENT = {"SYSTEM": 0, "DAILY": 1, "WORK": 2, "PLAY": 3, "ARTS": 4, "OBSCENITY": 5, "SEX": 6}
check("全部指令的 cid 都落在自己类型的段内（系统 1~99、日常 1xxx、工作 2xxx、娱乐 3xxx、技艺 4xxx、猥亵 5xxx、性爱 6xxx）",
      all(cfg.cid // 1000 == INSTRUCT_TYPE_SEGMENT.get(cfg.instruct_type, -1) for cfg in game_config.config_instruct.values()))
check("养成相关指令编号：1036 检查成绩单 / 2010 授课 / 2039 教育管理系统 / 3031~3033 胎教 / 5209 性技实操课 / 6021 结束性技实操课",
      [game_config.config_instruct_by_id.get(k) for k in ("check_report_card", "teach", "education_manage", "prenatal_talk", "prenatal_music", "prenatal_touch", "start_sex_class", "end_sex_class")]
      == [1036, 2010, 2039, 3031, 3032, 3033, 5209, 6021])
check("教师 / 学生 / 保育员岗位", all(cid in game_config.config_work_type for cid in (E.TEACHER_WORK_TYPE, E.STUDENT_WORK_TYPE, 153)))
check("四个成长阶段素质与成长停滞素质", all(t in game_config.config_talent for t in (28, 101, 102, 103, 104)))
check("四对性格素质", all(t in game_config.config_talent for pair in E.PERSONALITY_PAIR_TALENT.values() for t in pair))
check("科目 18 门 = 10 技能 + 8 性技", len(E.SUBJECT_ABILITY_LIST) == 18 and len(E.FEMALE_SUBJECT_LIST) == 17 and len(E.SEX_CLASS_ABILITY_LIST) == 7)
check("每门科目都能解出经验 id", all(growth_handle.get_subject_exp_id(a) for a in E.SUBJECT_ABILITY_LIST))
check("教育区设施效果 Lv1~Lv5 有配置", len(game_config.config_facility_effect_data.get(E.EDUCATION_ZONE_NAME, [])) >= 6)
check("10 间教室都在场景数据里", len(schedule_handle.get_classroom_list()) == 10)
check("四处体育课地点都存在", all(schedule_handle.get_course_place({"course_type": E.COURSE_TYPE_PE, "target": name}) for name in E.PE_PLACE_DATA))
check("ArkEditor 前提表已同步实操课与养成前提", all(name in open(os.path.join("tools", "ArkEditor", "csv", "Premise.csv"), encoding="utf-8").read()
                                                  for name in ("sex_class_mode_on", "self_in_sex_class", "self_follow_mother", "self_have_classmate", "work_is_student",
                                                               "teacher_have_class_now", "self_course_attend", "target_report_card_checkable")))
check("ArkEditor 效果表已同步 552~556", all(f"\n{eid}," in open(os.path.join("tools", "ArkEditor", "csv", "Effect.csv"), encoding="utf-8").read() for eid in (552, 553, 554, 555, 556)))

# Plan 31 §3.16（L17）：ArkEditor 前提表补全截断的描述、同步 6 个新前提；buildata 的生成器按第一个空格切一刀
with open(os.path.join("tools", "ArkEditor", "csv", "Premise.csv"), encoding="utf-8") as _premise_csv_file:
    _premise_csv_line_list = _premise_csv_file.read().splitlines()
check("L11 / L13 ArkEditor 前提表已同步 6 个新前提", all(any(line.startswith(f"{name},") for line in _premise_csv_line_list) for name in NEW_PREMISE_LIST))
_truncated_line_list = [line for line in _premise_csv_line_list if line.endswith("（Plan")]
check("L17 ArkEditor 前提表没有截断在「（Plan」的描述（同胞、母亲可跟随、跟随见学三行已补全）", not _truncated_line_list, _truncated_line_list)
import ast  # noqa: E402
import re  # noqa: E402

# buildata.py 顶层会调 game_config.init()，测试进程里不能 import 它（会把配置再载一遍）：只用 ast 取出纯函数 build_promise_csv_text 单独执行
with open("buildata.py", encoding="utf-8") as _buildata_file:
    _buildata_tree = ast.parse(_buildata_file.read())
_builder_node_list = [node for node in _buildata_tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_promise_csv_text"]
check("L17 buildata 有生成前提表的纯函数 build_promise_csv_text", len(_builder_node_list) == 1)
if _builder_node_list:
    _builder_scope = {}
    exec(compile(ast.Module(body=_builder_node_list, type_ignores=[]), "buildata.py", "exec"), _builder_scope)
    with open(os.path.join("Script", "Core", "constant_promise.py"), encoding="utf-8") as _promise_file:
        _promise_line_list = _promise_file.readlines()
    _generated_text = _builder_scope["build_promise_csv_text"](_promise_line_list)
    # 期望值另从 constant_promise.py 直接取：常量行紧跟单行 docstring「分类 描述」时，生成器应产出「前提id,常量名,分类,描述」，
    #    描述是 docstring 第一个空格之后的全部。按片段查而不是按行查：前面若有没带 docstring 的常量，行首会粘着别的前提（生成器的既有限制，与本条无关）
    _expect_fragment = {}
    _spaced_name_set = set()
    for _index, _line in enumerate(_promise_line_list[:-1]):
        _doc_line = _promise_line_list[_index + 1]
        _match = re.fullmatch(r'\s*([A-Z0-9_]+) = "([a-z0-9_]+)"\n', _line)
        if not _match or not _doc_line.endswith('"""\n') or "#" in _doc_line or _doc_line.count('"') != 6:
            continue
        _doc_text = _doc_line.strip().strip('"').strip()
        if " " not in _doc_text:
            continue
        _doc_type, _doc_desc = _doc_text.split(" ", 1)
        _expect_fragment[_match.group(2)] = f"{_match.group(2)},{_match.group(1)},{_doc_type},{_doc_desc}\n"
        if " " in _doc_desc:
            # 描述里本身带空格：改前按每个空格切、只取第二段，这些前提的描述都会截断
            _spaced_name_set.add(_match.group(2))
    _mismatch = [name for name in _spaced_name_set if _expect_fragment[name] not in _generated_text]
    check(f"L17 生成器按第一个空格切一刀：描述里带空格的 {len(_spaced_name_set)} 个前提，生成的描述与 docstring 完全一致", bool(_spaced_name_set) and not _mismatch, _mismatch[:10])
    _three_name = ("self_have_sibling_child", "self_mother_available", "self_follow_mother")
    check(
        "L17 同上：同胞、母亲可跟随、跟随见学三行带着完整描述（改前截断在「（Plan」）",
        all(name in _expect_fragment and _expect_fragment[name] in _generated_text for name in _three_name),
        [_expect_fragment.get(name) for name in _three_name],
    )
    check("L17 同上：6 个新前提都生成了完整的行", all(name in _expect_fragment and _expect_fragment[name] in _generated_text for name in NEW_PREMISE_LIST))
# L18：校验工具 TEXT_DUP_LEN 的 docstring 归位
with open(os.path.join("tools", "official_event_check.py"), encoding="utf-8") as _tool_file:
    _tool_line_list = _tool_file.read().splitlines()
_dup_index = next((index for index, line in enumerate(_tool_line_list) if line.startswith("TEXT_DUP_LEN")), -1)
check(
    "L18 校验工具 TEXT_DUP_LEN 的 docstring 紧跟在定义之后（改前游离在 PLACEHOLDER_RE 的 docstring 之后）",
    0 <= _dup_index < len(_tool_line_list) - 1 and "查重" in _tool_line_list[_dup_index + 1] and sum("查重时比对的正文前缀长度" in line for line in _tool_line_list) == 1,
)

finish()
