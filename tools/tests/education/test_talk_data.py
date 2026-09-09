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
check("教育相关口上总量 ≥ 2800 条", len(talk_list) >= 2800, len(talk_list))
count_by_behavior = {}
for talk in talk_list:
    count_by_behavior[talk.behavior_id] = count_by_behavior.get(talk.behavior_id, 0) + 1
for behavior in sorted(EDU_BEHAVIOR):
    check(f"{behavior} 有口上（{count_by_behavior.get(behavior, 0)} 条）", count_by_behavior.get(behavior, 0) > 0)
check("翘课被抓有 ≥ 16 条", count_by_behavior.get("caught_skip_class", 0) >= 16)
for behavior in ("teach", "attent_class", "self_study", "show_off_study"):
    subject_hit = set()
    for talk in talk_list:
        if talk.behavior_id != behavior:
            continue
        premise = str(talk.premise)
        for ability_id in E.SUBJECT_ABILITY_LIST:
            if f"Course|{ability_id}_" in premise or f"CourseShowOff|{ability_id}_" in premise:
                subject_hit.add(ability_id)
    check(f"{behavior} 覆盖全部 18 门科目", subject_hit == set(E.SUBJECT_ABILITY_LIST), sorted(set(E.SUBJECT_ABILITY_LIST) - subject_hit))

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
                                                  for name in ("sex_class_mode_on", "self_in_sex_class", "self_follow_mother", "self_have_classmate", "work_is_student")))
check("ArkEditor 效果表已同步 552~556", all(f"\n{eid}," in open(os.path.join("tools", "ArkEditor", "csv", "Effect.csv"), encoding="utf-8").read() for eid in (552, 553, 554, 555, 556)))

finish()
