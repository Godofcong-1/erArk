# -*- coding: UTF-8 -*-
"""助理的早安榨精 / 晚安榨精：配置注册、可选部位（身上有、已破处、默认服装）、选择面板、执行时的作罢判定、部位交经验与射精、早安榨精先于上交内裤 / 袜子"""
import datetime

from _bootstrap import *  # noqa: F401,F403
import Script.StateMachine.default  # noqa: F401  注册状态机
from Script.Design import assistant_milking, settle_behavior, second_behavior
from Script.UI.Panel import assistant_panel

cache.debug_mode = False
# 射精后的 achievement_flow 每次都会先算好全部数值类成就的判断值，其中要读龙门币，无头 fixture 的资源表是空的
cache.rhodes_island.materials_resouce.setdefault(1, 0)
MORNING, NIGHT = 5, 6
PAN_POSITION = assistant_milking.CLOTH_POSITION_OFFSET + 9
SOCKS_POSITION = assistant_milking.CLOTH_POSITION_OFFSET + 10


def first_cloth_id(cloth_type: int) -> int:
    """
    取一件全员通用的某类型服装
    Keyword arguments:
    cloth_type -- 服装类型id
    Return arguments:
    int -- 服装id
    """
    return min(cid for cid, cloth in game_config.config_clothing_tem.items() if cloth.clothing_type == cloth_type and cloth.npc == 0)


HAT_ID, PAN_ID, SOCKS_ID = first_cloth_id(0), first_cloth_id(9), first_cloth_id(10)


def make_assistant(cid: int, name: str) -> game_type.Character:
    """
    造一名成年、已破处、有兽尾、穿着帽子内裤袜子、信赖 250 的助理，并任命为博士的助理
    Keyword arguments:
    cid -- 角色id
    name -- 角色名
    Return arguments:
    game_type.Character -- 角色对象
    """
    cd = make_character(cid, name)
    for talent_id in range(5):
        cd.talent[talent_id] = 0
    cd.talent[113] = 1
    cd.trust = 250
    cd.cloth.clothing_tem = [HAT_ID, SOCKS_ID]
    cd.cloth.cloth_wear[0] = [HAT_ID]
    cd.cloth.cloth_wear[9] = [PAN_ID]
    cd.cloth.cloth_wear[10] = [SOCKS_ID]
    pl.assistant_character_id = cid
    return cd


def run_state_machine(cd: game_type.Character, state_machine_id: int):
    """
    清空绘制记录后让角色执行一个状态机，开始时间为当前游戏时间
    Keyword arguments:
    cd -- 角色
    state_machine_id -- 状态机id
    Return arguments:
    无
    """
    drawn_text.clear()
    cd.behavior.start_time = cache.game_time
    constant.handle_state_machine_data[state_machine_id](cd.cid)


# ==== 1. 配置注册 ====
section("1. 配置注册")
check("早安服务与晚安服务的第4项是榨精，需求与早安咬一样是信赖250",
      [game_config.config_assistant_services_option[cid][0][4] for cid in (MORNING, NIGHT)] == ["早安榨精", "晚安榨精"]
      and [game_config.config_assistant_services_option[cid][1][4] for cid in (MORNING, NIGHT)] == ["X|250", "X|250"],
      [game_config.config_assistant_services_option[cid] for cid in (MORNING, NIGHT)])
check("榨精行为挂了专用结算 558，开启服务的二段行为必须显示", all(558 in game_config.config_behavior_effect_data[b] for b in ("morning_salutation_4", "night_salutation_4"))
      and all(998 in game_config.config_behavior_effect_data[b] for b in ("morning_service_4", "night_service_4")))
check("状态机 723 / 724 与前提已注册", 723 in constant.handle_state_machine_data and 724 in constant.handle_state_machine_data
      and "assistant_morning_salutation_4" in constant.handle_premise_data and "assistant_night_salutation_4" in constant.handle_premise_data)
target_by_state = {target.state_machine_id: target for target in game_config.config_target.values()}
check("AI 目标在玩家位置、要问候状态、选了榨精时执行 723 / 724", 723 in target_by_state and 724 in target_by_state)
check("每个可选部位都有对应的 H 部位交 / 服装交行为", all(b in game_config.config_behavior for b in list(assistant_milking.BODY_PART_JOB_BEHAVIOR.values()) + list(assistant_milking.CLOTH_TYPE_JOB_BEHAVIOR.values()) + ["trousers_job"]))

adult = make_assistant(9101, "成年助理")

# ==== 2. 可选部位 ====
section("2. 可选部位")
position_list = assistant_milking.get_selectable_position_list(adult.cid)
check("已破处的成年干员：口腔、小穴、子宫、后穴、尿道都可选，兽尾有素质才可选，兽角兽耳没有素质不可选，胃部与胯部腹部背部不在列",
      {2, 6, 7, 8, 9, 12} <= set(position_list) and not {13, 14, 15, 16, 17, 18} & set(position_list), position_list)
check("服装只列默认服装（模板里的帽子、袜子，加上人人都配的胸衣与内裤），附属物不列",
      [p - 20 for p in position_list if p >= 20] == [0, 6, 9, 10], position_list)
adult.talent[0] = 1
adult.talent[4] = 1
position_list = assistant_milking.get_selectable_position_list(adult.cid)
check("还保有阴道处女时小穴与子宫不可选，还没接吻过时口腔不可选，其余照旧",
      not {2, 6, 7} & set(position_list) and {8, 9, 12} <= set(position_list), position_list)
adult.talent[3] = 1
adult.talent[0] = 0
check("阴道已破处、子宫处女还在时子宫仍不可选", 7 not in assistant_milking.get_selectable_position_list(adult.cid) and 6 in assistant_milking.get_selectable_position_list(adult.cid))
for talent_id in range(5):
    adult.talent[talent_id] = 0

# ==== 3. 选择面板 ====
section("3. 选择面板")
enable_clickable_buttons()
panel_obj = assistant_panel.Assistant_Panel(100)
option_len = len(game_config.config_assistant_services_option[MORNING][0])
adult.assistant_services[MORNING] = 3
err = run_panel(lambda: panel_obj.chose_button(MORNING, option_len), [f"milking_position_{PAN_POSITION}"])
check("早安咬切到下一项时弹出部位选择，选内裤后开启早安榨精并记在助理自己身上",
      err is None and adult.assistant_services[MORNING] == 4 and adult.work.assistant_milking_position[MORNING] == PAN_POSITION, (err, adult.assistant_services[MORNING], adult.work.assistant_milking_position))
offered = ask_log[0][0] if ask_log else []
check("面板只列出可选部位", sorted(int(o.split("_")[-1]) for o in offered if o.startswith("milking_position_")) == assistant_milking.get_selectable_position_list(adult.cid), offered)

adult.assistant_services[MORNING] = 3
err = run_panel(lambda: panel_obj.chose_button(MORNING, option_len), [_("取消")])
check("取消选择时与不满足条件一样归零，原来选定的部位不变", err is None and adult.assistant_services[MORNING] == 0 and adult.work.assistant_milking_position[MORNING] == PAN_POSITION,
      (err, adult.assistant_services[MORNING]))

adult.assistant_services[MORNING] = 3
adult.trust = 0
adult.hypnosis.hypnosis_degree = 999
err = run_panel(lambda: panel_obj.chose_button(MORNING, option_len), [])
check("信赖不足时不能用催眠进度代替，开启失败归零", err is None and adult.assistant_services[MORNING] == 0, (err, adult.assistant_services[MORNING]))
adult.trust = 250
adult.hypnosis.hypnosis_degree = 0

pl.assistant_character_id = adult.cid

# ==== 4. 执行与作罢 ====
section("4. 执行与作罢")
adult.assistant_services[MORNING] = 4
adult.sp_flag.morning_salutation = 1
run_state_machine(adult, 723)
check("穿着选定的内裤时执行早安榨精，对象是博士，早安问候记为已完成",
      adult.behavior.behavior_id == constant.Behavior.MORNING_SALUTATION_4 and adult.target_character_id == 0 and adult.sp_flag.morning_salutation == 2)
adult.cloth.cloth_wear[9] = []
adult.sp_flag.morning_salutation = 1
run_state_machine(adult, 723)
check("身上已经没有内裤时无法执行：原地作罢、早安问候记为已完成、告知原因",
      adult.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY and adult.sp_flag.morning_salutation == 2 and any("无法进行早安榨精" in t for t in drawn_text), drawn_text)
adult.cloth.cloth_wear[9] = [PAN_ID]
adult.assistant_services[NIGHT] = 4
adult.work.assistant_milking_position[NIGHT] = 12
adult.talent[113] = 0
adult.sp_flag.night_salutation = 1
run_state_machine(adult, 724)
check("晚安榨精选的兽尾已经没有时作罢，晚安问候照样记为已完成", adult.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY and adult.sp_flag.night_salutation == 2)
adult.talent[113] = 1

# ==== 5. 结算：经验与射精 ====
section("5. 结算：经验与射精")


def settle_milking(cd: game_type.Character, service_cid: int, position: int) -> game_type.CharacterStatusChange:
    """
    设定部位后直接执行专用结算 558
    Keyword arguments:
    cd -- 助理
    service_cid -- 助理服务id
    position -- 部位编码
    Return arguments:
    game_type.CharacterStatusChange -- 结算记录
    """
    cd.work.assistant_milking_position[service_cid] = position
    cd.behavior.behavior_id = assistant_milking.MILKING_SERVICE_BEHAVIOR[service_cid]
    cd.behavior.start_time = cache.game_time
    cd.target_character_id = 0
    pl.semen_point = pl.semen_point_max = 1000
    change_data = game_type.CharacterStatusChange()
    constant.settle_behavior_effect_data[558](cd.cid, 10, change_data, cache.game_time)
    return change_data


before = dict(adult.experience)
pan_semen_before = adult.dirty.cloth_semen[9][1]
settle_milking(adult, MORNING, PAN_POSITION)
check("内裤交：干员得到奉仕与服装交经验，精液射在内裤上",
      adult.experience[30] == before[30] + 1 and adult.experience[47] == before[47] + 1 and adult.dirty.cloth_semen[9][1] > pan_semen_before,
      (adult.experience[30] - before[30], adult.experience[47] - before[47], adult.dirty.cloth_semen[9]))
before, pl_before = dict(adult.experience), dict(pl.experience)
settle_milking(adult, NIGHT, 6)
check("小穴：与博士的骑乘位阴道性交对调发起方，干员得到阴道 / 阴道性交 / 阴道扩张经验，博士得到插入经验，精液射进小穴",
      all(adult.experience[e] == before[e] + 1 for e in (4, 61, 65)) and pl.experience[60] == pl_before[60] + 1 and adult.dirty.body_semen[6][1] > 0,
      ([adult.experience[e] - before[e] for e in (4, 61, 65)], pl.experience[60] - pl_before[60]))
before = dict(adult.experience)
settle_milking(adult, MORNING, 2)
check("口腔：与早安咬一样另加饮精经验", all(adult.experience[e] == before[e] + 1 for e in (42, 153, 25)), [adult.experience[e] - before[e] for e in (42, 153, 25)])

# ==== 6. 早安榨精先于上交 ====
section("6. 早安榨精先于上交")


def reset_day(cd: game_type.Character, position: int):
    """
    重置为今天还没见面、还没早安问候、穿着内裤和袜子、被要求每天上交内裤
    Keyword arguments:
    cd -- 助理
    position -- 早安榨精选定的部位
    Return arguments:
    无
    """
    cd.assistant_services[MORNING] = 4
    cd.work.assistant_milking_position[MORNING] = position
    cd.sp_flag.morning_salutation = 1
    cd.first_record.first_meet = 0
    cd.first_record.day_first_meet = 1
    cd.cloth.cloth_wear[9] = [PAN_ID]
    cd.cloth.cloth_wear[10] = [SOCKS_ID]
    cd.body_manage[1] = 1
    cd.body_manage[2] = 0
    cd.second_behavior["give_pan_in_day_first_meet"] = 0
    cd.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY


reset_day(adult, PAN_POSITION)
second_behavior.judge_character_first_meet(adult.cid)
check("选了内裤：见面时先不上交，每日招呼留着", adult.second_behavior["give_pan_in_day_first_meet"] == 0 and adult.first_record.day_first_meet == 1)
reset_day(adult, SOCKS_POSITION)
second_behavior.judge_character_first_meet(adult.cid)
check("选了袜子但只被要求交内裤：内裤照常在见面时上交", adult.second_behavior["give_pan_in_day_first_meet"] == 1 and adult.first_record.day_first_meet == 0)
reset_day(adult, PAN_POSITION)
adult.sp_flag.morning_salutation = 2
second_behavior.judge_character_first_meet(adult.cid)
check("已经早安问候过（或到中午作罢）后照常上交", adult.second_behavior["give_pan_in_day_first_meet"] == 1)

reset_day(adult, PAN_POSITION)
pl.pl_collection.npc_panties_tem.pop(adult.cid, None)
# 清空内裤上的精液记录：若先上交再射精，射精时身上已没有内裤，update_semen_dirty 不会记下这次射精
adult.dirty.cloth_semen[9][1:] = [0, 0, 0]
run_state_machine(adult, 723)
settle_behavior.handle_settle_behavior(adult.cid, cache.game_time + datetime.timedelta(minutes=10))
check("走完早安榨精的结算：先射在内裤上，结算末尾的每日招呼再把这件内裤交给博士",
      adult.cloth.cloth_wear[9] == [] and pl.pl_collection.npc_panties_tem.get(adult.cid) == [PAN_ID] and adult.first_record.day_first_meet == 0
      and adult.dirty.cloth_semen[9][3] > 0,
      (adult.cloth.cloth_wear[9], pl.pl_collection.npc_panties_tem.get(adult.cid), adult.first_record.day_first_meet))

# ==== 8. 榨精部位前提 ====
section("8. 榨精部位前提")
from Script.Design import handle_premise  # noqa: E402

adult.work.assistant_milking_position = {MORNING: PAN_POSITION, NIGHT: 12}
adult.behavior.behavior_id = constant.Behavior.MORNING_SALUTATION_4
check("榨精部位前提：早安榨精时只认早安选定的内裤，不认袜子、也不认同编号的身体部位（尿道）",
      [handle_premise.handle_premise(p, adult.cid) for p in ("CVP_A1_MilkPos|C9_E_1", "CVP_A1_MilkPos|C10_E_1", "CVP_A1_MilkPos|B9_E_1")] == [1, 0, 0])
adult.behavior.behavior_id = constant.Behavior.NIGHT_SALUTATION_4
check("榨精部位前提：晚安榨精时认晚安选定的兽尾", [handle_premise.handle_premise(p, adult.cid) for p in ("CVP_A1_MilkPos|B12_E_1", "CVP_A1_MilkPos|C9_E_1")] == [1, 0])
adult.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
check("榨精部位前提：不在榨精时不成立", handle_premise.handle_premise("CVP_A1_MilkPos|B12_E_1", adult.cid) == 0)

finish()
