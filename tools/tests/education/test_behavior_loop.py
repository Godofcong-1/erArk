# -*- coding: UTF-8 -*-
"""模式 B：在真实存档上带护栏地跑行为循环，看孩子按课表上课、循环收敛、跨天结算不炸

只读：读档只用 input_load_save，绝不 establish_save；行为循环是自建的带轮数上限的副本，
   不 inline 调用 init_character_behavior()（其结尾的成就结算可能写文件）。
"""
from _bootstrap import *  # noqa: F401,F403
from Script.Design import character_behavior, instuct_judege, handle_npc_ai
from Script.Settle import past_day_settle, realtime_settle
from Script.UI.Panel import character_info_head

E = education_constant

section("挑一个女儿最多的存档")
# 本机没有 save 目录、或里面没有可读的存档时整份跳过（2026-09-15 用户拍板）：存档不入库，换机器、换目录后常常没带过来，
#    这时行为循环的验收由 test_class_ai 的循环段与复现探针兜底。
#    先判目录在不在再调 judge_save_file_exist：后者经 get_save_dir_path 会顺手建出 save 目录，只读的测试不该留下它
_save_dir = os.path.join(ROOT, "save")
_save_id_list = sorted(name for name in os.listdir(_save_dir) if name.isdigit()) if os.path.isdir(_save_dir) else []
_save_id_list = [save_id for save_id in _save_id_list if save_handle.judge_save_file_exist(save_id)]
if not _save_id_list:
    print("  跳过：本机没有可读的存档（save 目录不存在或为空），本文件要在真实存档上跑行为循环")
    finish()
best_id = ""
best_count = -1
for save_id in _save_id_list:
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
# 课表只对学生岗生效（Plan 24 口径 1）：存档里改了岗的女儿按新岗位上班、不去上课，上课检查只看学生岗的女儿。
#    全部女儿的名单另留一份，只用来避免把女儿拉去当教师
all_daughter_list = growth_handle.get_student_candidate_list()
daughter_list = [cid for cid in all_daughter_list if cache.character_data[cid].work.work_type == E.STUDENT_WORK_TYPE]
if not daughter_list:
    mother_id = next(cid for cid in sorted(cache.npc_id_got) if cid in cache.character_data)
    for index in range(3):
        make_character(9001 + index, f"测试女儿{index + 1}", 152, daughter=True, stage=103, mother_id=mother_id, born_days=300, position=SCENE_EDU_ENTRY)
    all_daughter_list = growth_handle.get_student_candidate_list()
    daughter_list = [cid for cid in all_daughter_list if cache.character_data[cid].work.work_type == E.STUDENT_WORK_TYPE]
check("有在学的学生岗女儿", len(daughter_list) > 0, (len(daughter_list), len(all_daughter_list)))

section("环境：教师、教室、课表")
teacher_list = schedule_handle.get_teacher_candidate_list()
if len(teacher_list) < 2:
    for cid in sorted(cache.npc_id_got):
        cd = cache.character_data[cid]
        if cid in all_daughter_list or cd.dead or growth_handle.get_character_stage(cid) or cd.work.work_type in (E.TEACHER_WORK_TYPE,):
            continue
        cd.work.work_type = E.TEACHER_WORK_TYPE
        if len(schedule_handle.get_teacher_candidate_list()) >= 3:
            break
teacher_list = schedule_handle.get_teacher_candidate_list()
check("至少 2 名教师", len(teacher_list) >= 2, teacher_list)
# 把时间拨到本月的一个工作日 08:40（到岗时间，教师会按「马上要上的那一节」先去教室，第五轮）
now = cache.game_time
day = now.replace(hour=8, minute=40, second=0, microsecond=0)
while day.weekday() >= 5:
    day += datetime.timedelta(days=1)
if day.month != now.month:
    day = now.replace(day=1, hour=8, minute=40, second=0, microsecond=0)
    while day.weekday() >= 5:
        day += datetime.timedelta(days=1)
set_time(day)
cache.pre_game_time = day
# 女儿与教师都从空闲开始：存档里带进来的半截行为（睡觉、吃饭、H）会让开头几十分钟的取样全是噪声
for cid in daughter_list + teacher_list:
    cd = cache.character_data[cid]
    cd.sp_flag.is_h = False
    cd.sp_flag.imprisonment = False
    cd.hit_point = cd.hit_point_max
    cd.mana_point = cd.mana_point_max
    cd.sp_flag.sleep = False
    cd.sp_flag.is_follow = 0
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
teacher_log = []
attend_start = sum(growth_handle.get_child_growth(cid).attend_class_count for cid in daughter_list)
# 第一轮从 08:40 走 40 分钟，之后每轮 45 分钟：检查点落在每节课的中段（09:20 / 10:05 / 10:50 / 11:35 …）。
#    第五轮起每节课的时长截到本节结束，节次交界处人人都在换教室，在交界处取样看到的全是「移动中」
for index, minute in enumerate((40, 45, 45, 45, 45, 45)):
    try:
        pl_round, npc_pass, stuck = run_one_round(minute)
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
    # 教师侧（第五轮）：本节有课的教师此刻应在课表上那间教室里授课
    teaching_count = 0
    right_room_count = 0
    for cid in teacher_list:
        teaching = schedule_handle.get_now_teaching(cid)
        if teaching is None:
            continue
        teaching_count += 1
        cd = cache.character_data[cid]
        if cd.behavior.behavior_id == constant.Behavior.TEACH and class_ai.judge_in_scene(cid, teaching["classroom"]):
            right_room_count += 1
        else:
            now_scene = map_handle.get_map_system_path_str_for_list(cd.position)
            print(f"    教师 {cid}{cd.name} 应在{teaching['classroom']}，实际在 {now_scene} 做 {cd.behavior.behavior_id}（{cd.behavior.start_time} +{cd.behavior.duration}）")
    teacher_log.append((right_room_count, teaching_count))
    stuck_text = ""
    if stuck:
        stuck_text = " 未收敛：" + "、".join(f"{cid}{cache.character_data[cid].name}({cache.character_data[cid].behavior.behavior_id})" for cid in stuck[:6])
    print(f"  第 {index + 1} 轮 {cache.game_time}: 玩家 {pl_round} 轮 / NPC {npc_pass} 轮 / 未收敛 {len(stuck)} / 女儿在课 {in_class}/{len(daughter_list)}"
          f" / 教师在对的教室授课 {right_room_count}/{teaching_count}{stuck_text}")
check("六轮循环没有抛异常", not error_list, error_list)
check("每轮都收敛（玩家 ≤ 30 轮、NPC ≤ 60 轮、无卡死角色）", all(r[0] <= 30 and r[1] <= 60 and r[2] == 0 for r in round_log), round_log)
attend_gain = sum(growth_handle.get_child_growth(cid).attend_class_count for cid in daughter_list) - attend_start
check("女儿们累计听课节数 > 0", attend_gain > 0, attend_gain)
# 前四个检查点（09:20 ~ 11:35）都在上午的节次中段，第五、六轮已是午休与下午
check("上课节次内绝大多数女儿都在上课 / 自习 / 教室里", all(count >= len(daughter_list) * 0.8 for count in in_class_log[0:4]), in_class_log)
# 第五轮修的主链：教师按课表走班，实践教室与大礼堂里的课同样有人讲（原先只有站在理论教室里的教师会开讲）。
#    生理需求（吃饭、上厕所）排在上课之前，允许四个检查点里有一人次正好在处理需求
teacher_right_total = sum(right for right, _total in teacher_log[0:4])
teacher_need_total = sum(total for _right, total in teacher_log[0:4])
check("本节有课的教师都在课表上那间教室里授课", teacher_need_total > 0 and teacher_right_total >= teacher_need_total - 1, teacher_log)
check("上午四节里女儿平均每人记到 ≥ 3 节出勤（收益不再取决于谁先到教室）", attend_gain >= len(daughter_list) * 3, (attend_gain, len(daughter_list)))

section("实操课预到岗：上一节在上课的必修生，开课时已在实操教室（Plan 25 §3.1）")
# 第 5 节（14:00）在别的教室上课、第 6 节（14:45）被点名必修的女儿：改前她们在第 5 节听课到 14:45 才动身，开课那一刻一个都不在；
#    改后 14:35 被打断提前退场，到了实操教室原地等开课。需求（吃饭、上厕所）不打断，所以只要求至少一半到场
sex_room = (schedule_handle.get_classroom_list(E.COURSE_TYPE_PRACTICE) + schedule_handle.get_classroom_list(E.COURSE_TYPE_PUBLIC))[0]
must_list = []
old_room = {}
for cid in daughter_list:
    course = schedule_handle.get_selected_course(cid, cache.game_time.weekday(), 4)
    if course is not None and course[0] in E.CLASSROOM_COURSE_TYPE_SET and course[1] != sex_room:
        must_list.append(cid)
        old_room[cid] = course[1]
    if len(must_list) >= 4:
        break
check("挑到了第 5 节在别的教室上课的女儿", len(must_list) > 0, must_list)
sex_class_handle.set_temp_class(cache.game_time.date().toordinal(), 5, sex_room, 70, must_attend=must_list)
pre_round_log = []
for minute in (14 * 60 - (cache.game_time.hour * 60 + cache.game_time.minute), 45):
    pre_round_log.append(run_one_round(minute))
arrived = [cid for cid in must_list if class_ai.judge_in_scene(cid, sex_room)]
print(f"  {cache.game_time}: 必修生在{sex_room} {len(arrived)}/{len(must_list)}，两轮 {[(r[0], r[1], len(r[2])) for r in pre_round_log]}")
for cid in must_list:
    cd = cache.character_data[cid]
    print(f"    {cid}{cd.name} 在 {map_handle.get_map_system_path_str_for_list(cd.position)} 做 {cd.behavior.behavior_id}（{cd.behavior.start_time} +{cd.behavior.duration}）"
          f" 目标 {cd.behavior.move_final_target} 最近 {cd.last_behavior_id_list[-5:]}")
check("两轮都收敛（打断规则没有让 NPC 来回抖动）", all(r[0] <= 30 and r[1] <= 60 and not r[2] for r in pre_round_log), [(r[0], r[1], len(r[2])) for r in pre_round_log])
# 改前她们在第 5 节听课到 14:45 才动身，开课那一刻全都还在原来的教室；改后 14:35 提前退场。
#    路上撞上需求（累了去休息、饿了去吃饭）时需求优先、不截，所以不要求全员到场，只要求没人还坐在上一节的教室里
check("实操课开始那一刻，没有必修生还坐在上一节的教室里（14:35 已提前退场）", not any(class_ai.judge_in_scene(cid, old_room[cid]) for cid in must_list),
      [(cid, old_room[cid]) for cid in must_list if class_ai.judge_in_scene(cid, old_room[cid])])
check("实操课开始那一刻，已有必修生在实操教室里等开课", len(arrived) >= 1, (arrived, must_list))
cache.rhodes_island.temp_sex_class = {}
class_ai.get_skip_class_rate = _orig_rate

section("Plan 32 §3.7（L4）：学生截短排在实时结算之前，截掉的那一段只算一遍（真实存档、真实行为循环）")
# 读档会重建全部角色对象（save_handle.input_load_save），_bootstrap 里的 pl 已不是存档里的玩家 cache.character_data[0]，
#    它的开始时刻不能当这一步的起点：这一段不经 run_one_round，自己把起点显式传给 NPC 阶段；
#    NPC 阶段只让挑出的那名女儿参加（别的角色与本题无关），翘课概率钉成 0（她翘了课，跨天那一段的 flag 断言就随机了）
class_ai.get_skip_class_rate = lambda cid: 0.0
L4_RT_LOG = []
""" 挑出的那名女儿的实时结算记录：(行为id, 行为开始时刻, 行为时长, 这次结算的分钟数) """
_orig_true_add = realtime_settle.get_true_add_time


def l4_clear_need(cid: int) -> None:
    """
    夹具控制：清掉生理需求（饥饿 / 尿意 / 疲劳 / 困意与对应标记），体力气力回满，只看课表链（照 test_class_ai.clear_need）
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    无
    功能: 改了需求标记要同步异常位掩码，否则 normal_1 按旧掩码判
    """
    cd = cache.character_data[cid]
    for name in ("hunger_point", "urinate_point", "tired_point", "sleep_point"):
        if hasattr(cd, name):
            setattr(cd, name, 0)
    for name in ("eat_food", "rest", "pee"):
        if hasattr(cd.sp_flag, name):
            setattr(cd.sp_flag, name, 0)
    cd.sp_flag.sleep = False
    cd.sp_flag.tired = False
    cd.hit_point = cd.hit_point_max
    cd.mana_point = cd.mana_point_max
    handle_premise.refresh_unnormal_flag(cid)


l4_id = -1
""" 挑出的学生岗女儿：不是助理、清掉需求后 normal_all 成立（截短规则要求上课行的门槛成立） """
for cid in daughter_list:
    if cid == cache.character_data[0].assistant_character_id:
        continue
    cache.character_data[cid].sp_flag.is_follow = 0
    l4_clear_need(cid)
    if handle_premise.handle_normal_all(cid):
        l4_id = cid
        break
check("L4 前提：挑到一名能跑工作链的学生岗女儿（不是助理、清掉需求后 normal_all 成立）", l4_id != -1, daughter_list)


def l4_true_add_spy(character_id: int, now_time: datetime.datetime, pl_start_time: datetime.datetime) -> int:
    """
    实时结算取「这次结算多少分钟」的记录包装（realtime_settle.character_aotu_change_value 经模块全局名调用它），只记挑出的那名女儿
    Keyword arguments:
    character_id -- 角色id
    now_time -- 当前时刻
    pl_start_time -- 玩家这一步的开始时刻
    Return arguments:
    int -- 原函数的返回值：这次结算的分钟数
    """
    result = _orig_true_add(character_id, now_time, pl_start_time)
    if character_id == l4_id:
        cd = cache.character_data[character_id]
        L4_RT_LOG.append((cd.behavior.behavior_id, cd.behavior.start_time, cd.behavior.duration, result))
    return result


def run_l4_step(minute: int, class_period: int) -> tuple:
    """
    让挑出的女儿从此刻起在宿舍自由玩耍 minute 分钟，跑一步「玩家走 minute 分钟」的真实行为循环，记下她的实时结算
    Keyword arguments:
    minute -- 玩家这一步的分钟数，也是她这段自由玩耍的时长
    class_period -- 今天给她排一节理论课的节次（那一格在全局课表上排成没有教师、到了教室自习），-1 为一节课都不排
    Return arguments:
    tuple -- (NPC 阶段遍数, 是否收敛, 她的实时结算记录)
    功能: 照 init_character_behavior 的顺序先玩家、后 NPC；玩家置为空闲，只推进时钟，这一步的起点显式传进去。
          交互对象设回自己，否则 judge_character_status_time_over 按「交互对象不在场」把行为的结束改写为这一步的结束；
          护栏 120 遍：没事可做时会一分钟一分钟地挪（README 夹具陷阱），60 分钟一步最多 60 遍
    """
    cd = cache.character_data[l4_id]
    growth_data = growth_handle.get_child_growth(l4_id)
    growth_data.selected_course = {}
    growth_data.skip_class_flag = False
    if class_period >= 0:
        schedule_handle.set_class_cell(l4_room, l4_week_day, class_period, 45, -1)
        schedule_handle.set_selected_course(l4_id, l4_week_day, class_period, E.COURSE_TYPE_THEORY, l4_room)
    step_start = cache.game_time
    move_to(l4_id, l4_home)
    cd.sp_flag.is_h = False
    cd.sp_flag.is_follow = 0
    cd.behavior.behavior_id = constant.Behavior.FREE_PLAY
    cd.behavior.start_time = step_start
    cd.behavior.duration = minute
    cd.behavior.move_target = []
    cd.behavior.move_final_target = []
    cd.state = constant.CharacterStatus.STATUS_ARDER
    cd.target_character_id = l4_id
    cd.action_info.wake_time = step_start
    l4_clear_need(l4_id)
    pl_data = cache.character_data[0]
    pl_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    pl_data.behavior.start_time = step_start
    game_time.sub_time_now(minute)
    cache.over_behavior_character = set()
    L4_RT_LOG.clear()
    npc_pass = 0
    realtime_settle.get_true_add_time = l4_true_add_spy
    try:
        character_behavior.character_behavior(0, cache.game_time, step_start)
        while l4_id not in cache.over_behavior_character:
            npc_pass += 1
            if npc_pass > 120:
                break
            l4_clear_need(l4_id)
            character_behavior.character_behavior(l4_id, cache.game_time, step_start)
    finally:
        realtime_settle.get_true_add_time = _orig_true_add
    return npc_pass, l4_id in cache.over_behavior_character, list(L4_RT_LOG)


def l4_log_text(log: list) -> list:
    """
    把实时结算记录换成便于失败时阅读的简写
    Keyword arguments:
    log -- run_l4_step 返回的实时结算记录
    Return arguments:
    list -- (行为id, 开始 时:分, 时长, 结算分钟数) 的列表
    """
    return [(one[0], one[1].strftime("%H:%M"), one[2], one[3]) for one in log]


l4_room = ""
""" 给她排课用的理论教室：已开放、解析得出场景路径的第一间 """
if l4_id != -1:
    l4_room = next((room for room in schedule_handle.get_classroom_list(E.COURSE_TYPE_THEORY) if schedule_handle.get_classroom_position(room)), "")
check("L4 前提：有一间已开放的理论教室可排课", l4_room != "", l4_room)
if l4_id != -1 and l4_room:
    l4_week_day = cache.game_time.weekday()
    l4_dorm = cache.character_data[l4_id].dormitory
    l4_home = map_handle.get_map_system_path_for_str(l4_dorm) if l4_dorm in cache.scene_data else list(SCENE_EDU_ENTRY)
    # 14:45 起连跑两步：第一步没课作对照；第二步 16:15 有课，开课前 20 分钟（15:55）落在没课的第 7 节里，截短规则 B 截得到
    set_time(cache.game_time.replace(hour=14, minute=45, second=0, microsecond=0))
    pass0, over0, log0 = run_l4_step(60, -1)
    check("L4 对照：这一步没课、14:45 起自由玩耍 60 分钟、玩家一步 60 分钟 → 不截，实时结算合计 60 分钟",
          over0 and bool(log0) and log0[0][2] == 60 and sum(one[3] for one in log0) == 60, (pass0, l4_log_text(log0)))
    pass1, over1, log1 = run_l4_step(60, 7)
    check("L4 16:15 有课、15:45 起自由玩耍：在实时结算之前就截到 15:55（开课前 20 分钟），这一段只结算 10 分钟（此前先按 60 分钟结算、再截短）",
          bool(log1) and log1[0][0] == constant.Behavior.FREE_PLAY and log1[0][2] == 10 and log1[0][3] == 10, l4_log_text(log1))
    check("L4 这一步收敛，她的实时结算合计 60 分钟、与玩家这一步等长（此前 110：15:55~16:45 那一段饥饿、尿意、疲劳算了两遍）",
          over1 and sum(one[3] for one in log1) == 60, (pass1, l4_log_text(log1)))
class_ai.get_skip_class_rate = _orig_rate

section("跨天结算")
set_time(cache.game_time.replace(hour=0, minute=1))
# 跨天只清前一天及更早挂上的翘课 flag（Plan 32 §3.7 L5：一步跨过午夜时，新一天刚挂上的 flag 不能被清掉）。
#    存档当天可能真有女儿翘过课，她的 flag 认的就是今天：统一改成前一天挂上的，下面的断言才不随存档而变
for cid in daughter_list:
    if growth_handle.get_child_growth(cid).skip_class_flag:
        growth_handle.get_child_growth(cid).skip_class_day = cache.game_time.toordinal() - 1
try:
    past_day_settle.update_new_day()
    check("update_new_day 不抛异常", True)
except Exception as error:
    import traceback

    traceback.print_exc()
    check("update_new_day 不抛异常", False, repr(error))
check("跨天后翘课（前一天挂上的）与见学 flag 都清了", all(not growth_handle.get_child_growth(cid).skip_class_flag and not growth_handle.get_child_growth(cid).follow_mother_flag for cid in daughter_list))
check("跨天后学期结算幂等", semester_handle.settle_semester_change() == [])

finish()
