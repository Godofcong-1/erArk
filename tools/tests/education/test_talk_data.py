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
check("期末桶 19 条（Plan 32 L22 挪进 3 条）且 sub_key 为保留键", len(game_config.config_official_event_by_sub_key.get((E.GROWTH_EVENT_DEPARTMENT, E.SEMESTER_EVENT_SUB_KEY), ())) >= 19)
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
        # 萝莉 1 / 20 / 26 在 Plan 32 L22 挪进了期末桶（期末 17 / 18 / 19），前提见文件末尾的 Plan 32 断言
        "萝莉6": "CVP_A1_Growth|4_GE_20&CVP_A1_Growth|5_E_0&self_have_any_course",
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
        # Plan 32 L23：正文写「被人抱着」，另加了不是萝莉
        "通用15": "CVP_A1_Growth|9_GE_90&CVP_A1_T|103_E_0",
        "婴儿4": "CVP_A1_Growth|3_GE_50",
        "婴儿50": "self_mother_available&CVP_A1_Growth|3_GE_60",
    },
}
""" Plan 31 方案 §4.3 改过前提的事件：发现编号 -> {事件uid: 新前提串}（其后 Plan 32 又改过的按现值写） """
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
_semester_row = {r[0]: dict(zip(_event_rows[0], r)) for r in _event_rows[5:] if r and r[0].strip()}
""" 期末.csv 按 cid 取行：Plan 32 L22 把萝莉 1 / 20 / 26 挪成了期末 17 / 18 / 19，Plan 31 L10 对这几条正文的断言跟着改读期末表 """
_row_17 = _semester_row.get("17", {})
_row_18 = _semester_row.get("18", {})
check(
    "L10 萝莉 1（Plan 32 L22 挪成期末 17）的正文与选项 2 不再点名「学识」「战斗」（成绩单只记涨了的科目，点名的科目她未必上过）",
    bool(_row_17) and all(word not in _row_17.get("text", "") + _row_17.get("option_2", "") for word in ("学识", "战斗")),
    _row_17.get("text", ""),
)
check(
    "L10 萝莉 20（Plan 32 L22 挪成期末 18）不再写「掉了两级」（科目只升不降），改为「一级都没涨」",
    "掉了两级" not in _row_18.get("text", "") and "一级都没涨" in _row_18.get("text", ""),
    _row_18.get("text", ""),
)
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
# 萝莉 1 在 Plan 32 L22 挪进了期末桶，对照改用萝莉 6：它读的本学期听课 / 缺课（4 / 5）放在期末桶里同样会被拦
_ok_row = dict(_loli_row.get("6", {"cid": "6"}))
_ok_row["premise"] = _ok_row.get("premise", "") + "&CVP_A1_Growth|9_GE_50"
_checker = official_event_check.Checker()
_checker.check_row("萝莉.csv", 6, _ok_row, set(), set())
check("L16 对照：萝莉桶的事件读养成数值 9 不报错（新规则只拦期末桶；萝莉 6 读的 4 / 5 也照样通过）", _checker.error_list == [], _checker.error_list)
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
# 原用萝莉 1，它在 Plan 32 L22 挪进了期末桶，改用萝莉 2
_bad_row = dict(_loli_row.get("2", {"cid": "2"}))
_bad_row["sub_key"] = "104"
_checker = official_event_check.Checker()
_checker.check_row("萝莉.csv", 7, _bad_row, set(), set())
check("M2 同上：萝莉的事件（萝莉 2）挪进成年桶同样报一条（uid 按「文件名 + cid」判）", sum("成年桶只有成年结算显式推入的事件会出现" in one for one in _checker.error_list) == 1, _checker.error_list)

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

section("Plan 32 §3.14：事件表的前提与正文（M2、L22、L23、L26）")
from Script.Design import talk  # noqa: E402
from Script.System.Official_Event_System import official_event_handle  # noqa: E402

PLAN32_EVENT_PREMISE_EXPECT = {
    "L22": {
        "期末17": "CVP_A1_Growth|0_GE_20&CVP_A1_Growth|7_NE_3&CVP_A1_T|103_E_1",
        "期末18": "self_have_any_course&CVP_A1_Growth|7_NE_3&CVP_A1_T|103_E_1",
        "期末19": "self_have_sibling_child&CVP_A1_Growth|7_NE_3&CVP_A1_T|103_E_1",
    },
    "L23": {
        "通用6": "time_spring&CVP_A1_T|103_E_0",
        "通用15": "CVP_A1_Growth|9_GE_90&CVP_A1_T|103_E_0",
        "通用27": "CVP_A1_T|103_E_0",
    },
    "L26": {
        "通用5": "self_have_sibling_child&CVP_A1_T|101_E_0&self_have_practice_course",
        "萝莉51": "self_have_public_course&CVP_A1_Growth|3_GE_50",
        "萝莉57": "CVP_A1_Growth|3_GE_50&self_have_pe_course",
        "幼女24": "self_have_public_course&CVP_A1_Growth|3_GE_50",
    },
}
""" Plan 32 方案 §4.3 改过前提的事件：发现编号 -> {事件uid: 新前提串}（期末 17 / 18 / 19 是原萝莉 1 / 20 / 26 挪进期末桶后的uid）。
    萝莉 51 / 幼女 24 的公开课前提替换掉被它蕴含的「有课」（实施复审补）：抽取权重按「配置权重 × 前提条数」算，留着被蕴含的旧前提只会平白抬权重。
    通用 5 的「非婴儿」照留：Plan 26 起写会走会说的孩子的 17 条通用事件一律显式排除婴儿（test_growth_event 锁着），实践课是新加的条件 """
for finding, expect_dict in PLAN32_EVENT_PREMISE_EXPECT.items():
    for uid, premise_text in expect_dict.items():
        now_premise = game_config.config_official_event.get(uid, {}).get("premise", "")
        check(f"{finding} {uid} 的前提按 Plan 32 方案 §4.3 改为 {premise_text}", now_premise == premise_text, now_premise)
_bad_token_32 = []
for expect_dict in PLAN32_EVENT_PREMISE_EXPECT.values():
    for uid, premise_text in expect_dict.items():
        for token in premise_text.split("&"):
            if token.startswith("CVP_"):
                try:
                    handle_premise.handle_premise(token, 201)
                except Exception as error:
                    _bad_token_32.append((uid, token, repr(error)))
            elif token not in premise_name_set or token not in constant.handle_premise_data:
                _bad_token_32.append((uid, token))
check(
    "L22 / L23 / L26 改过的事件前提逐个 token 校验：前提名与 constant_promise 拼写一致且已注册（含新前提 self_have_public_course），CVP 可解析",
    not _bad_token_32,
    _bad_token_32,
)
# M2：生日事件改为生日当天插队首推入（growth_event_handle.push_birthday_event），正文不再写死「今天」
_birthday_data = game_config.config_official_event.get(E.BIRTHDAY_EVENT_UID, {})
_birthday_text = _common_row.get("3", {}).get("text", "")
check(
    "M2 生日事件的 uid 常量是通用 3，在养成部门的通用桶（sub_key 0）",
    E.BIRTHDAY_EVENT_UID == "通用3" and _birthday_data.get("department") == E.GROWTH_EVENT_DEPARTMENT and _birthday_data.get("sub_key") == E.STAGE_ANY,
    (_birthday_data.get("department"), _birthday_data.get("sub_key")),
)
check(
    "M2 通用 3 的正文开头改为「{Name}的生日到了。」，不再写死「今天是{Name}的生日」（插了队首，玩家隔几天才处理公务时也不矛盾）",
    _birthday_text.startswith("{Name}的生日到了。") and "今天是{Name}的生日" not in _birthday_text,
    _birthday_text,
)
check("M2 通用 3 的前提不动：非婴儿且今天过生日（推入前照判）", _birthday_data.get("premise") == "CVP_A1_T|101_E_0&self_birthday_today", _birthday_data.get("premise"))
# L22：写成绩单的萝莉 1 / 20 / 26 挪进期末桶，学期切换时与其它期末事件同池抽一条
MOVED_REPORT_EVENT = {"期末17": "萝莉1", "期末18": "萝莉20", "期末19": "萝莉26"}
""" Plan 32 L22 挪进期末桶的三条：新uid -> 原uid """
_moved_old_hit = sorted(set(MOVED_REPORT_EVENT.values()) & set(game_config.config_official_event))
check("L22 萝莉 1 / 20 / 26 已从萝莉桶删去（学期切换那一夜期末事件刚入队，日常派发还抽得到它们，两三条「交成绩单」叠在一起）", not _moved_old_hit, _moved_old_hit)
_semester_uid_set = set(game_config.config_official_event_by_sub_key.get((E.GROWTH_EVENT_DEPARTMENT, E.SEMESTER_EVENT_SUB_KEY), ()))
check("L22 期末 17 / 18 / 19 在期末桶（sub_key 200），期末桶共 19 条", set(MOVED_REPORT_EVENT) <= _semester_uid_set and len(_semester_uid_set) >= 19, sorted(_semester_uid_set))
check(
    "L22 三条的正文照搬原萝莉 1 / 20 / 26",
    "拿着这学期的成绩单站在你面前" in _semester_row.get("17", {}).get("text", "")
    and "一级都没涨" in _semester_row.get("18", {}).get("text", "")
    and "的成绩单同一天发下来" in _semester_row.get("19", {}).get("text", ""),
)
check(
    "L22 三条的配置权重取 2：抽取按「配置权重 × 前提条数」算，三条前提乘出 6 分，落在其余期末事件的 4~8 分之间"
    "（原萝莉桶的 15 / 9 / 10 放进期末池会压过其余期末事件；取 4 时一条 12 分，三条合计约占萝莉期末池的一半，实施复审补）",
    all(official_event_handle.get_event_weight(uid) == 2 for uid in MOVED_REPORT_EVENT),
    [official_event_handle.get_event_weight(uid) for uid in MOVED_REPORT_EVENT],
)
_checker = official_event_check.Checker()
for _cid in ("17", "18", "19"):
    _checker.check_row("期末.csv", 0, dict(_semester_row.get(_cid, {"cid": _cid})), set(), set())
check("L22 校验工具：挪进期末桶的三行不报错（去掉了推送时恒为 1 的 Growth|23，选项不改能力、正文不写育儿室）", _checker.error_list == [], _checker.error_list)
_daily_sub_key_set = {E.STAGE_ANY, *E.STAGE_ALL_CHILD}
""" 日常派发会翻的子桶：通用桶与婴儿 / 幼女 / 萝莉三个阶段桶（成年桶与期末桶只由显式推入） """
_daily_uid_list = [uid for uid, data in game_config.config_official_event.items() if data.get("department") == E.GROWTH_EVENT_DEPARTMENT and data.get("sub_key") in _daily_sub_key_set]
_daily_read_23 = [uid for uid in _daily_uid_list if "Growth|23_" in str(game_config.config_official_event[uid].get("premise", ""))]
check(
    "L22 日常派发的桶里不再有读成绩单待查看（养成数值 23）的事件：讲成绩单的只在期末桶",
    len(_daily_uid_list) > 100 and not _daily_read_23,
    (len(_daily_uid_list), _daily_read_23),
)
_daily_report_text = []
for _file_name in ("通用", "婴儿", "幼女", "萝莉"):
    with open(os.path.join("data", "official_event", f"{_file_name}.csv"), encoding="utf-8", newline="") as _event_file:
        for _row in list(csv.reader(_event_file))[5:]:
            # 只看养成部门的日常桶；通用.csv 里成年桶的四条不由日常派发推出
            if len(_row) > 3 and _row[1] == str(E.GROWTH_EVENT_DEPARTMENT) and _row[3] in {str(key) for key in _daily_sub_key_set} and "成绩单" in "".join(_row):
                _daily_report_text.append(_file_name + _row[0])
check("L22 同上：日常桶的事件正文与选项都不再写成绩单", not _daily_report_text, _daily_report_text)

# 功能断言的夹具：萝莉 201 与幼女 202 互为同胞，都在学生岗、只排一格理论课，都拿着一份良好档的新成绩单
clear_schedules()
set_time(period_time(0))
make_character(202, "女儿B", 152, daughter=True, stage=102, mother_id=102, born_days=150)
schedule_handle.set_class_cell(_("理论教室一"), 0, 0, 45, -1)
_growth_by_cid = {201: growth_handle.get_child_growth(201), 202: growth_handle.get_child_growth(202)}
""" 夹具孩子的养成数据：角色id -> CHILD_GROWTH """
for _cid, _growth in _growth_by_cid.items():
    _growth.selected_course = {}
    schedule_handle.set_selected_course(_cid, 0, 0, E.COURSE_TYPE_THEORY, _("理论教室一"))
    _growth.attend_class_count = 20
    _growth.report_card_history = [{"grade": E.REPORT_GRADE_GOOD}]
    _growth.report_card_flag = True


def event_premise_pass(uid: str, character_id: int, drop_prefix: str = "") -> bool:
    """
    按养成事件派发的判法求一条事件对某个孩子成不成立：先挑互动对象（同胞 / 同学），判定期间把交互对象临时指过去再判前提，不入队
    （与 growth_event_handle.get_candidate_event_list / push_semester_event 同一条路径，只是不做随机抽取）
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    drop_prefix -- 判定时略去以它开头的前提（如阶段进度 CVP_A1_Growth|3_，只看其余条件），空串为不略去
    Return arguments:
    bool -- 前提是否成立；事件不存在为 False
    """
    event_data = game_config.config_official_event.get(uid)
    if event_data is None:
        return False
    token_list = [token for token in str(event_data.get("premise", "")).split("&") if token and not (drop_prefix and token.startswith(drop_prefix))]
    partner_id = growth_event_handle.get_event_partner(uid, character_id)
    return official_event_handle.judge_premise_pass("&".join(token_list), character_id, partner_id) > 0


check(
    "L22 萝莉拿到良好档的新成绩单（听过 20 节课、有真课、有同胞）：期末 17 / 18 / 19 都成立",
    all(event_premise_pass(uid, 201) for uid in MOVED_REPORT_EVENT),
    [uid for uid in MOVED_REPORT_EVENT if not event_premise_pass(uid, 201)],
)
_daily_candidate_hit = sorted((set(MOVED_REPORT_EVENT) | set(MOVED_REPORT_EVENT.values())) & {one[0] for one in growth_event_handle.get_candidate_event_list(201)})
check("L22 同上：她的日常候选里没有这三条（日常派发只翻本阶段桶与通用桶），也没有原萝莉 1 / 20 / 26", not _daily_candidate_hit, _daily_candidate_hit)
check("L22 幼女拿到同样的成绩单：三条都不成立（正文与选项写的是萝莉，前提限 T|103）", not any(event_premise_pass(uid, 202) for uid in MOVED_REPORT_EVENT))
check("L22 对照：略去阶段前提 CVP_A1_T|103_E_1 后三条对这个幼女都成立（挡住她的正是阶段前提）", all(event_premise_pass(uid, 202, "CVP_A1_T|103_") for uid in MOVED_REPORT_EVENT))
_growth_by_cid[201].report_card_history = [{"grade": E.REPORT_GRADE_NO_CLASS}]
check("L22 萝莉的新成绩单是档位 3（这学期没有上课）：三条都不成立（正文写的是各科成绩）", not any(event_premise_pass(uid, 201) for uid in MOVED_REPORT_EVENT))
_growth_by_cid[201].report_card_history = [{"grade": E.REPORT_GRADE_GOOD}]
# L23：正文写被人抱着的通用 6 / 15 / 27 限非萝莉（婴儿、幼女仍可抽到；6 / 15 另挂季节与学期进度，这里只判阶段）
check(
    "L23 不是萝莉（CVP_A1_T|103_E_0）：萝莉判不过、幼女判得过",
    handle_premise.handle_premise("CVP_A1_T|103_E_0", 201) == 0 and bool(handle_premise.handle_premise("CVP_A1_T|103_E_0", 202)),
)
check("L23 通用 27 只挂这一条前提：萝莉判不过、幼女判得过（此前前提为空，萝莉也抽得到「抱着她在舷梯口站一会儿」）", not event_premise_pass("通用27", 201) and event_premise_pass("通用27", 202))
# L26：点名课型的日常事件按课型进候选（阶段进度 Growth|3 随 M1 改按可游玩天，与课型无关，这里略去它，只看课表）
_type_premise_32 = ("self_have_public_course", "self_have_pe_course", "self_have_practice_course")
""" 本轮用到的三个课型前提：公开课（Plan 32 新增）、体育课、实践课 """
check("L26 只排理论课：公开课 / 体育课 / 实践课三个课型前提都不成立", not any(handle_premise.handle_premise(name, 201) for name in _type_premise_32))
check("L26 通用 5「实践课上……分到了同一组」：只排理论课的萝莉判不过（此前只挂同胞，照样抽得到）", not event_premise_pass("通用5", 201))
check(
    "L26 萝莉 51「大礼堂的公开课」、萝莉 57「训练场的记录」：只排理论课判不过",
    not event_premise_pass("萝莉51", 201, "CVP_A1_Growth|3_") and not event_premise_pass("萝莉57", 201, "CVP_A1_Growth|3_"),
)
check("L26 幼女 24「大礼堂有一场公开课」：只排理论课的幼女判不过（此前挂的是任意课）", not event_premise_pass("幼女24", 202, "CVP_A1_Growth|3_"))
schedule_handle.set_class_cell(_("实践教室一"), 0, 1, 43, -1)
schedule_handle.set_selected_course(201, 0, 1, E.COURSE_TYPE_PRACTICE, _("实践教室一"))
check("L26 再排一格实践课：通用 5 判得过", event_premise_pass("通用5", 201))
schedule_handle.set_class_cell(_("大礼堂"), 0, 2, 45, -1)
for _cid in (201, 202):
    schedule_handle.set_selected_course(_cid, 0, 2, E.COURSE_TYPE_PUBLIC, _("大礼堂"))
check(
    "L26 再排一格大礼堂的公开课：萝莉 51 与幼女 24 都判得过（新前提 self_have_public_course），萝莉 57 仍判不过（公开课不是体育课）",
    event_premise_pass("萝莉51", 201, "CVP_A1_Growth|3_") and event_premise_pass("幼女24", 202, "CVP_A1_Growth|3_") and not event_premise_pass("萝莉57", 201, "CVP_A1_Growth|3_"),
)
schedule_handle.set_selected_course(201, 0, 3, E.COURSE_TYPE_PE, _("木桩房"))
check("L26 再排一格体育课：萝莉 57 判得过", event_premise_pass("萝莉57", 201, "CVP_A1_Growth|3_"))

section("Plan 32 §3.14：实操课与检查成绩单的口上（L24、L25）")


def talk_weight_if_pass(character_id: int, talk_cid: str) -> int:
    """
    一条口上在前提全部成立时的抽取权重，照 talk.handle_talk_sub 的算法：weight_all_to_1 下每条非 high_ 前提记 1，
    再乘 talk.handle_special_talk_weight 给的特殊前提倍率（女儿行乘女儿倍率 draw_setting[15]）。
    抽取时先按权重值本身加权挑一个权重档（value_handle.get_rand_value_for_value_region），再在同一档里等概率挑一句，
    所以落在同一个权重档的几句抽中概率相同
    Keyword arguments:
    character_id -- 说这句口上的角色id
    talk_cid -- 口上cid
    Return arguments:
    int -- 权重；没有这条口上时为 0
    """
    premise_set = set(game_config.config_talk_premise_data.get(talk_cid, ()))
    if not premise_set:
        return 0
    return sum(1 for premise in premise_set if not premise.startswith("high_")) * talk.handle_special_talk_weight(character_id, premise_set)


_daughter_mult = cache.all_system_setting.draw_setting.get(15, 5)
""" 女儿倍率（talk.handle_special_talk_weight 读的 draw_setting[15]，默认 5） """
DAUGHTER_JOIN_TALK = {102: ("sex_class_join_sex_class1032", "sex_class_join_sex_class1034"), 103: ("sex_class_join_sex_class1031", "sex_class_join_sex_class1033")}
""" 实操课到场口上里的女儿行：成长阶段 -> (必修, 选修) """
_growth_by_cid[201].sex_class_count = 5
_growth_by_cid[202].sex_class_count = 0
check("L24 守卫：女儿倍率大于 1（为 1 时下面几条同权重的断言恒真）", _daughter_mult > 1, _daughter_mult)
check(
    "L24 「第一次来」两行、「老学生」到场两行与旁观两行都加了 self_is_player_daughter",
    all("self_is_player_daughter" in talk_premise(cid).split("&") for cid in FIRST_TIME_TALK_LIST + OLD_HAND_TALK_LIST),
    [talk_premise(cid) for cid in FIRST_TIME_TALK_LIST + OLD_HAND_TALK_LIST],
)
check("L24 第一次上实操课的幼女女儿：「第一次来」两行前提都成立", all(premise_all(talk_premise(cid), 202) for cid in FIRST_TIME_TALK_LIST))
_first_weight_list = [talk_weight_if_pass(202, cid) for cid in FIRST_TIME_TALK_LIST + DAUGHTER_JOIN_TALK[102]]
check(
    "L24 同上：「第一次来」两行与幼女的女儿行（必修 1032 / 选修 1034）落在同一个权重档（3 条前提 × 女儿倍率），抽中概率同量级",
    len(set(_first_weight_list)) == 1 and _first_weight_list[0] == 3 * _daughter_mult,
    _first_weight_list,
)
_old_first_premise = set(game_config.config_talk_premise_data.get(FIRST_TIME_TALK_LIST[0], ())) - {constant_promise.Premise.SELF_IS_PLAYER_DAUGHTER}
check(
    "L24 对照：去掉女儿前提（改前的前提串）只得 2 分，比女儿行低一个量级（改前幼女第一次到场抽中「第一次来」只有约 3%）",
    len(_old_first_premise) * talk.handle_special_talk_weight(202, _old_first_premise) == 2,
    _old_first_premise,
)
check("L24 实操课上满 5 次的萝莉女儿：「老学生」到场两行与旁观两行前提都成立", all(premise_all(talk_premise(cid), 201) for cid in OLD_HAND_TALK_LIST))
_old_join_weight_list = [talk_weight_if_pass(201, cid) for cid in OLD_HAND_TALK_LIST[:2] + DAUGHTER_JOIN_TALK[103]]
check("L24 同上：到场的「老学生」两行与萝莉的女儿行（必修 1031 / 选修 1033）落在同一个权重档", len(set(_old_join_weight_list)) == 1, _old_join_weight_list)
check(
    "L24 同上：旁观的「老学生」两行也乘女儿倍率（3 × 倍率；女儿旁观行 1050 是 2 × 倍率）",
    all(talk_weight_if_pass(201, cid) == 3 * _daughter_mult for cid in OLD_HAND_TALK_LIST[2:]) and talk_weight_if_pass(201, "sex_class_watch_sex_class1050") == 2 * _daughter_mult,
    [talk_weight_if_pass(201, cid) for cid in OLD_HAND_TALK_LIST[2:] + ("sex_class_watch_sex_class1050",)],
)
make_character(205, "非女儿萝莉", 152, stage=103)
growth_handle.get_child_growth(205).sex_class_count = 5
check("L24 按设计：萝莉化的非女儿学生不再有这几行（方案 §6 风险一栏；她们仍有其余通用行）", not any(premise_all(talk_premise(cid), 205) for cid in OLD_HAND_TALK_LIST))
remove_character(205)
_growth_by_cid[201].sex_class_count = 0
# L25：成年女儿拿到档位 3（这学期没有上课）的新成绩单时，检查成绩单要有口上
ADULT_NO_CLASS_TALK = ("daily_check_report_card1018", "daily_check_report_card1019")
""" Plan 32 L25 新增的两条成年女儿档位 3 口上 """
make_character(203, "成年女儿", 152, daughter=True, stage=104, mother_id=102, born_days=500)
_growth_203 = growth_handle.get_child_growth(203)
_growth_203.report_card_history = [{"grade": E.REPORT_GRADE_NO_CLASS}]
_growth_203.report_card_flag = True
pl.target_character_id = 203
check(
    "L25 检查成绩单新增 2 条成年女儿的档位 3 口上：前提照 1014~1017 的写法（交互对象是女儿、档位 3、成绩单待查看），阶段换成 104",
    all(talk_premise(cid) == "target_is_player_daughter&CVP_A2_T|104_E_1&CVP_A2_Growth|7_E_3&CVP_A2_Growth|23_E_1" for cid in ADULT_NO_CLASS_TALK),
    [talk_premise(cid) for cid in ADULT_NO_CLASS_TALK],
)
check("L25 同上：两条正文写的是这学期没有上课", all("没有上课" in str(getattr(game_config.config_talk.get(cid), "context", "")) for cid in ADULT_NO_CLASS_TALK))
_report_talk_cid_list = sorted(cid for cid in game_config.config_talk if cid.startswith("daily_check_report_card"))
_report_pass_list = [cid for cid in _report_talk_cid_list if premise_all(talk_premise(cid), 0)]
check(
    "L25 成年女儿拿着档位 3 的新成绩单：成立的正好是新增的两条（改前一条都没有：1004 / 1005 排除档位 3，1014~1017 只写幼女 / 萝莉）",
    _report_pass_list == sorted(ADULT_NO_CLASS_TALK),
    _report_pass_list,
)
_growth_203.report_card_history = [{"grade": E.REPORT_GRADE_GOOD}]
_report_pass_list = [cid for cid in _report_talk_cid_list if premise_all(talk_premise(cid), 0)]
check("L25 对照：成年女儿拿着良好档的成绩单，只有 1004 / 1005 成立，新增两条不成立", _report_pass_list == ["daily_check_report_card1004", "daily_check_report_card1005"], _report_pass_list)
pl.target_character_id = 201
remove_character(203)

section("Plan 32 §3.15：target 行说明（L27）")
with open(os.path.join("data", "target", "default", "target.csv"), encoding="utf-8", newline="") as _target_file:
    _target_row = {r[0]: r for r in csv.reader(_target_file) if r}
""" target.csv 按 cid 取行（列：cid、状态机id、前提、行动类型、备注） """
UPCOMING_TARGET = {"210810": ("715", "self_not_in_course_place"), "220830": ("720", "self_in_course_place")}
""" 读 self_course_upcoming 的两行：target cid -> (状态机id, 地点前提) """
check(
    "L27 target 210810 / 220830 的说明补上翘课日例外（今天已翘课的不算）",
    all(len(_target_row.get(cid, [])) == 5 and "今天已翘课的不算" in _target_row[cid][4] for cid in UPCOMING_TARGET),
    [_target_row.get(cid, [""])[-1] for cid in UPCOMING_TARGET],
)
check(
    "L27 同上：两行只改说明，状态机与前提不动",
    all(
        len(_target_row.get(cid, [])) == 5 and _target_row[cid][1] == state_machine_id and _target_row[cid][2] == f"normal_all|work_is_student|self_course_upcoming|{place_premise}"
        for cid, (state_machine_id, place_premise) in UPCOMING_TARGET.items()
    ),
)
_upcoming_premise_line = next((line for line in _premise_csv_line_list if line.startswith("self_course_upcoming,")), "")
check("L27 同上：与 ArkEditor 前提表 self_course_upcoming 的说明同口径", "今天已翘课的不算" in _upcoming_premise_line, _upcoming_premise_line)
# 收尾：还原夹具
for _growth in _growth_by_cid.values():
    _growth.attend_class_count = 0
    _growth.sex_class_count = 0
    _growth.report_card_history = []
    _growth.report_card_flag = False
    _growth.selected_course = {}
remove_character(202)
clear_schedules()

section("Plan 32 实施复审补：ArkEditor 两张表与 CHILD_GROWTH 说明的数据锁（L26 / L27）")
with open(os.path.join("tools", "ArkEditor", "csv", "Effect.csv"), encoding="utf-8") as _effect_csv_file:
    _effect_csv_line_list = _effect_csv_file.read().splitlines()
_effect_line_557 = next((line for line in _effect_csv_line_list if line.startswith("557,")), "")
_effect_line_512 = next((line for line in _effect_csv_line_list if line.startswith("512,")), "")
check("L26 ArkEditor 前提表有新前提 self_have_public_course 一行（常量名 SELF_HAVE_PUBLIC_COURSE）",
      any(line.startswith("self_have_public_course,SELF_HAVE_PUBLIC_COURSE,") for line in _premise_csv_line_list))
check("L27 ArkEditor 效果表 557 的说明改为学生坐下听课时「教师判能到岗」即结算，不再写「学生晚于教师到场」",
      "教师判能到岗" in _effect_line_557 and "晚于教师到场" not in _effect_line_557, _effect_line_557)
check("L27 ArkEditor 效果表 512 的说明补上 NPC 教师只发给「听课节次与自己开讲的节次相同」的学生", "听课节次与自己开讲的节次相同" in _effect_line_512, _effect_line_512)
check("L27 CHILD_GROWTH 的类说明写明「出生时不一定创建」（胎教值大于 0 才建，否则首次写入时惰性建）", "出生时不一定创建" in (game_type.CHILD_GROWTH.__doc__ or ""))

finish()
