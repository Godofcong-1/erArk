# -*- coding: UTF-8 -*-
"""模式 B：在真实存档上带护栏地跑行为循环，看孩子按课表上课、循环收敛、跨天结算不炸

只读：读档只用 input_load_save，绝不 establish_save；行为循环是自建的带轮数上限的副本，
   不 inline 调用 init_character_behavior()（其结尾的成就结算可能写文件）。
"""
from _bootstrap import *  # noqa: F401,F403
from Script.Design import character_behavior, instuct_judege, handle_npc_ai
from Script.Settle import past_day_settle
from Script.UI.Panel import character_info_head

E = education_constant

section("挑一个女儿最多的存档")
best_id = ""
best_count = -1
for save_id in sorted(name for name in os.listdir(os.path.join(ROOT, "save")) if name.isdigit()):
    if not save_handle.judge_save_file_exist(save_id):
        continue
    try:
        save_handle.input_load_save(save_id)
    except Exception as error:
        print("  存档", save_id, "载入失败", repr(error))
        continue
    count = len(growth_handle.get_student_candidate_list())
    print(f"  存档 {save_id}: 在学女儿 {count} 人，游戏时间 {cache.game_time}")
    if count > best_count:
        best_count = count
        best_id = save_id
check("找到了存档", best_id != "", best_id)
if best_count <= 0:
    print("  没有任何存档里有在学的女儿，用最近的存档 + 自建女儿继续")
save_handle.input_load_save(best_id)
daughter_list = growth_handle.get_student_candidate_list()
if not daughter_list:
    mother_id = next(cid for cid in sorted(cache.npc_id_got) if cid in cache.character_data)
    for index in range(3):
        make_character(9001 + index, f"测试女儿{index + 1}", 152, daughter=True, stage=103, mother_id=mother_id, born_days=300, position=SCENE_EDU_ENTRY)
    daughter_list = growth_handle.get_student_candidate_list()
check("有在学的女儿", len(daughter_list) > 0, daughter_list)

section("环境：教师、教室、课表")
teacher_list = schedule_handle.get_teacher_candidate_list()
if len(teacher_list) < 2:
    for cid in sorted(cache.npc_id_got):
        cd = cache.character_data[cid]
        if cid in daughter_list or cd.dead or growth_handle.judge_is_child(cid) or cd.work.work_type in (E.TEACHER_WORK_TYPE,):
            continue
        cd.work.work_type = E.TEACHER_WORK_TYPE
        if len(schedule_handle.get_teacher_candidate_list()) >= 3:
            break
teacher_list = schedule_handle.get_teacher_candidate_list()
check("至少 2 名教师", len(teacher_list) >= 2, teacher_list)
# 把时间拨到本月的一个工作日 09:00（第一节课开始）
now = cache.game_time
day = now.replace(hour=9, minute=0, second=0, microsecond=0)
while day.weekday() >= 5:
    day += datetime.timedelta(days=1)
if day.month != now.month:
    day = now.replace(day=1, hour=9, minute=0, second=0, microsecond=0)
    while day.weekday() >= 5:
        day += datetime.timedelta(days=1)
set_time(day)
cache.pre_game_time = day
for cid in daughter_list:
    cd = cache.character_data[cid]
    cd.sp_flag.is_h = False
    cd.sp_flag.imprisonment = False
    cd.hit_point = cd.hit_point_max
    cd.mana_point = cd.mana_point_max
    cd.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    cd.behavior.duration = 0
    cd.state = constant.CharacterStatus.STATUS_ARDER
cache.rhodes_island.class_schedule = {}
filled, skipped = auto_schedule.auto_fill_class_schedule()
check("一键排课", filled > 0, (filled, skipped))
for cid in daughter_list:
    growth_handle.get_child_growth(cid).selected_course = {}
    auto_schedule.auto_fill_selected_course(cid)
check("每个女儿第一节都有课", all(schedule_handle.get_selected_course(cid, day.weekday(), 0) is not None for cid in daughter_list))
# 心情翘课的随机在本测试里关掉，只验课表链
_orig_rate = class_ai.get_skip_class_rate
class_ai.get_skip_class_rate = lambda cid: 0.0

section("带护栏的行为循环")


def run_one_round(minute: int) -> tuple:
    """
    复刻一次「玩家等待 minute 分钟」后的完整行为循环
    Return arguments:
    tuple -- (玩家阶段轮数, NPC 阶段轮数, 未收敛的角色列表)
    """
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    pl.state = constant.CharacterStatus.STATUS_WAIT
    pl.behavior.behavior_id = constant.Behavior.WAIT
    pl.behavior.duration = minute
    game_time.sub_time_now(minute)
    cache.over_behavior_character = set()
    pl_round = 0
    pl_start = pl.behavior.start_time
    while 0 not in cache.over_behavior_character:
        pl_round += 1
        if pl_round > 30:
            break
        character_behavior.character_behavior(0, cache.game_time, pl_start)
    id_list = cache.npc_id_got.copy()
    id_list.discard(0)
    npc_pass = 0
    # 上限 60 而不是 skill 里的 25：真实存档里总有几个没事可做的干员在「空闲 1 分钟」里一分钟一分钟地挪，
    #    45 分钟的一轮要挪 45 步才追平时钟，那不是卡死（清空课表的基线跑出来一模一样）；卡死是 60 步还追不上
    while len(cache.over_behavior_character) <= len(id_list):
        npc_pass += 1
        if npc_pass > 60:
            break
        for cid in id_list:
            if cid in cache.over_behavior_character:
                continue
            character_behavior.character_behavior(cid, cache.game_time, pl_start)
    stuck = [cid for cid in id_list if cid not in cache.over_behavior_character]
    return pl_round, npc_pass, stuck


error_list = []
round_log = []
in_class_log = []
for index in range(6):
    try:
        pl_round, npc_pass, stuck = run_one_round(45)
    except Exception as error:
        import traceback

        traceback.print_exc()
        error_list.append(repr(error))
        break
    round_log.append((pl_round, npc_pass, len(stuck)))
    in_class = 0
    for cid in daughter_list:
        cd = cache.character_data[cid]
        tip = character_info_head.get_now_class_tip(cid)
        if cd.behavior.behavior_id in (constant.Behavior.ATTENT_CLASS, constant.Behavior.SELF_STUDY, constant.Behavior.INTERN_CLASS) or tip is not None:
            in_class += 1
    in_class_log.append(in_class)
    stuck_text = ""
    if stuck:
        stuck_text = " 未收敛：" + "、".join(f"{cid}{cache.character_data[cid].name}({cache.character_data[cid].behavior.behavior_id})" for cid in stuck[:6])
    print(f"  第 {index + 1} 轮 {cache.game_time}: 玩家 {pl_round} 轮 / NPC {npc_pass} 轮 / 未收敛 {len(stuck)} / 女儿在课 {in_class}/{len(daughter_list)}{stuck_text}")
check("六轮循环没有抛异常", not error_list, error_list)
check("每轮都收敛（玩家 ≤ 30 轮、NPC ≤ 60 轮、无卡死角色）", all(r[0] <= 30 and r[1] <= 60 and r[2] == 0 for r in round_log), round_log)
attend_total = sum(growth_handle.get_child_growth(cid).attend_class_count for cid in daughter_list)
check("女儿们累计听课节数 > 0", attend_total > 0, attend_total)
# 前四轮（09:45 ~ 12:00）都在上午的节次里，第五、六轮已是午休，所以只看前四轮
check("上课节次内绝大多数女儿都在上课 / 自习 / 教室里", all(count >= len(daughter_list) * 0.8 for count in in_class_log[1:4]), in_class_log)
class_ai.get_skip_class_rate = _orig_rate

section("跨天结算")
set_time(cache.game_time.replace(hour=0, minute=1))
try:
    past_day_settle.update_new_day()
    check("update_new_day 不抛异常", True)
except Exception as error:
    import traceback

    traceback.print_exc()
    check("update_new_day 不抛异常", False, repr(error))
check("跨天后翘课与见学 flag 都清了", all(not growth_handle.get_child_growth(cid).skip_class_flag and not growth_handle.get_child_growth(cid).follow_mother_flag for cid in daughter_list))
check("跨天后学期结算幂等", semester_handle.settle_semester_change() == [])

finish()
