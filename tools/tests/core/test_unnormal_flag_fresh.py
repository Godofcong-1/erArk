# -*- coding: UTF-8 -*-
"""异常位不过期：排了体检的干员到了自己的时段去体检科（位 3 随时刻变化）、平然催眠的干员关掉时停后按清醒判定（位 5）"""
from unittest import mock

from _bootstrap import *  # noqa: F401,F403
from Script.Design import handle_npc_ai
from Script.Settle import default as settle_default
from Script.UI.Panel import hypnosis_panel, physical_check_and_manage

SM_GO_EXAM = 662
""" 状态机：移动至体检科 """
EXAM_NPC_ID = 9501
HYPNOSIS_NPC_ID = 9502
POST_PATH = map_handle.get_map_system_path_for_str(constant.place_data["Maintenance_Department"][0])
""" 检修工程师的岗位：运维部 """
DAY = DEFAULT_TIME.replace(hour=0, minute=0)
""" 排体检的那个午夜 """
UPPER_CLOTH_ID = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 5)
""" 一件上衣：夹具默认全裸（位 4 异常），工作目标行要求的 normal_all 不成立，所以先给测试干员穿上 """


def book_at_midnight(slot: int) -> int:
    """
    回到午夜，走游戏自己的抽签给全体干员排体检（把抽签结果固定成指定的时段）
    Keyword arguments:
    slot -- 今日体检时间（1 上午，2 下午）
    Return arguments:
    int -- 测试干员被排到的时段
    """
    move_to(EXAM_NPC_ID, POST_PATH)
    set_time(DAY)
    with mock.patch.object(physical_check_and_manage.random, "randint", return_value=slot - 1):
        physical_check_and_manage.settle_health_check()
    return cache.character_data[EXAM_NPC_ID].action_info.health_check_today


def dispatch(hour: int) -> int:
    """
    把时间拨到当天的某个整点，让测试干员在岗位上重新选一次行动
    Keyword arguments:
    hour -- 整点
    Return arguments:
    int -- AI 派发的状态机id，没派发则为 0
    功能: 中间不手动刷新异常位——午夜到这个整点之间，游戏里也没有哪个结算点会去刷新位 3；
          只记下派发的是哪个状态机、不真的执行它（检修工作的状态机要随机挑设施，会读夹具里没有的设施开放表）
    """
    character_data = cache.character_data[EXAM_NPC_ID]
    move_to(EXAM_NPC_ID, POST_PATH)
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 0
    character_data.behavior.move_target = []
    character_data.behavior.move_final_target = []
    character_data.state = constant.CharacterStatus.STATUS_ARDER
    character_data.sp_flag.work_maintenance = 0
    set_time(DAY.replace(hour=hour))
    character_data.action_info.wake_time = cache.game_time
    hit = []
    origin = dict(constant.handle_state_machine_data)
    for state_machine_id in origin:
        constant.handle_state_machine_data[state_machine_id] = (lambda s: (lambda c: hit.append(s)))(state_machine_id)
    try:
        handle_npc_ai.find_character_target(EXAM_NPC_ID, cache.game_time)
    finally:
        constant.handle_state_machine_data.clear()
        constant.handle_state_machine_data.update(origin)
    return hit[0] if hit else 0


section("1. 排了体检的干员：时段前照常工作，到了时段去体检科")
saved_setting = dict(cache.rhodes_island.physical_examination_setting)
saved_examined = set(cache.rhodes_island.examined_operator_ids)
saved_waiting = set(cache.rhodes_island.waiting_for_exam_operator_ids)
# 开启定期体检、每天体检、全体干员、体检过的仍需再检、每天抽 10 人
cache.rhodes_island.physical_examination_setting.update({2: 1, 3: 3, 4: 1, 5: 1, 6: 9})
exam_npc = make_character(EXAM_NPC_ID, "体检异常位测试干员", 21, position=POST_PATH)
# 穿上衣服，再把异常位整体算一遍作为起点
exam_npc.cloth.cloth_wear[5] = [UPPER_CLOTH_ID]
handle_premise.refresh_unnormal_flag(EXAM_NPC_ID)
check("fixture：穿好衣服、没排体检时，她的异常位全部正常", handle_premise.handle_normal_all(EXAM_NPC_ID) == 1)

check("午夜抽签给她排了上午体检", book_at_midnight(1) == 1, exam_npc.action_info.health_check_today)
check("排的是上午，午夜当时还没到时段：位 3 正常", handle_premise.handle_normal_3(EXAM_NPC_ID) == 1)
early_state_machine = dispatch(8)
check("排了上午体检，8:00 还没到时段：她不去体检科", early_state_machine != SM_GO_EXAM, early_state_machine)
slot_state_machine = dispatch(10)
check("排了上午体检，10:00 在时段内：位 3 读成异常（高优先级 AI：体检）", handle_premise.handle_normal_3(EXAM_NPC_ID) == 0)
check("排了上午体检，10:00 在时段内：她放下工作去体检科", slot_state_machine == SM_GO_EXAM, slot_state_machine)

check("午夜抽签给她排了下午体检", book_at_midnight(2) == 2, exam_npc.action_info.health_check_today)
morning_state_machine = dispatch(10)
check("排了下午体检，10:00 还没到时段：她不去体检科", morning_state_machine != SM_GO_EXAM, morning_state_machine)
afternoon_state_machine = dispatch(15)
check("排了下午体检，15:00 在时段内：她放下工作去体检科", afternoon_state_machine == SM_GO_EXAM, afternoon_state_machine)
late_state_machine = dispatch(19)
check("排了下午体检却没去成，19:00 时段已过：位 3 恢复正常，她不再去体检科", handle_premise.handle_normal_3(EXAM_NPC_ID) == 1 and late_state_machine != SM_GO_EXAM, late_state_machine)

cache.rhodes_island.physical_examination_setting.clear()
cache.rhodes_island.physical_examination_setting.update(saved_setting)
cache.rhodes_island.examined_operator_ids = saved_examined
cache.rhodes_island.waiting_for_exam_operator_ids.clear()
cache.rhodes_island.waiting_for_exam_operator_ids.update(saved_waiting)
cache.rhodes_island.today_physical_examination_chara_id_dict = {}
remove_character(EXAM_NPC_ID)
set_time(DEFAULT_TIME)

section("2. 平然催眠的干员：开过一次时停再关掉后按清醒判定")
HYPNOSIS_TYPE_CALM = 1
""" 催眠类型：平然 """
hypnosis_npc = make_character(HYPNOSIS_NPC_ID, "平然异常位测试干员")
hypnosis_npc.cloth.cloth_wear[5] = [UPPER_CLOTH_ID]
handle_premise.refresh_unnormal_flag(HYPNOSIS_NPC_ID)
saved_target = pl.target_character_id
saved_hypnosis_type = pl.pl_ability.hypnosis_type
saved_time_stop = cache.time_stop_mode
saved_unconscious = {now_id: cache.character_data[now_id].sp_flag.unconscious_h for now_id in list(cache.npc_id_got) + [0]}
pl.target_character_id = HYPNOSIS_NPC_ID
pl.pl_ability.hypnosis_type = HYPNOSIS_TYPE_CALM
hypnosis_npc.hypnosis.hypnosis_degree = game_config.config_hypnosis_type[HYPNOSIS_TYPE_CALM].hypnosis_degree
# 催眠完成时顺带的素质获得检测会走成就结算、读基地资源，与异常位无关，这里跳过
with mock.patch.object(hypnosis_panel.handle_talent, "npc_gain_hypnosis_talent", lambda character_id: None):
    hypnosis_done = hypnosis_panel.evaluate_hypnosis_completion(HYPNOSIS_NPC_ID)
check("玩家对她完成平然催眠：进入平然状态，位 5（意识模糊）为异常", hypnosis_done == 1 and hypnosis_npc.sp_flag.unconscious_h == 4 and handle_premise.handle_normal_5(HYPNOSIS_NPC_ID) == 0,
      (hypnosis_done, hypnosis_npc.sp_flag.unconscious_h))
settle_default.handle_time_stop_on(0, 0, game_type.CharacterStatusChange(), cache.game_time)
check("开启时停：位 6（无交互）为异常", handle_premise.handle_normal_6(HYPNOSIS_NPC_ID) == 0)
settle_default.handle_time_stop_off(0, 0, game_type.CharacterStatusChange(), cache.game_time)
check("关闭时停：她的无意识状态清零", hypnosis_npc.sp_flag.unconscious_h == 0, hypnosis_npc.sp_flag.unconscious_h)
check("关闭时停后位 5、位 6 都读成正常", handle_premise.handle_normal_5(HYPNOSIS_NPC_ID) == 1 and handle_premise.handle_normal_6(HYPNOSIS_NPC_ID) == 1,
      (handle_premise.handle_normal_5(HYPNOSIS_NPC_ID), handle_premise.handle_normal_6(HYPNOSIS_NPC_ID)))
check("关闭时停后，玩家指令用的前提「交互对象 5、6 正常」成立", handle_premise.handle_t_normal_5_6(0) == 1)

pl.target_character_id = saved_target
pl.pl_ability.hypnosis_type = saved_hypnosis_type
cache.time_stop_mode = saved_time_stop
for now_id, now_value in saved_unconscious.items():
    if now_id in cache.character_data:
        cache.character_data[now_id].sp_flag.unconscious_h = now_value
remove_character(HYPNOSIS_NPC_ID)
finish()
