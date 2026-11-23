# -*- coding: UTF-8 -*-
"""蚀刻章：各组成就的计数、触发点与结算——醉奸、医疗、体液收藏、信物"""
from _bootstrap import *  # noqa: F401,F403
from unittest import mock

from Script.Settle import orgasm_settle
from Script.System.Instruct_System import handle_instruct
from Script.UI.Panel import ejaculation_panel

# achievement_flow 每次都会先算好全部数值类成就的判断值，其中要读龙门币，无头 fixture 的资源表是空的
cache.rhodes_island.materials_resouce.setdefault(1, 0)
achievement_dict = cache.achievement.achievement_dict


def reset_achievement(id_list: list):
    """
    把指定的蚀刻章都重置为未达成
    Keyword arguments:
    id_list -- 蚀刻章id列表
    Return arguments:
    无
    """
    for achievement_id in id_list:
        achievement_dict[achievement_id] = False


def got_list(id_list: list) -> list:
    """
    列出已达成的蚀刻章
    Keyword arguments:
    id_list -- 要查的蚀刻章id列表
    Return arguments:
    list -- 其中已达成的id
    """
    return [achievement_id for achievement_id in id_list if achievement_dict.get(achievement_id)]


# ==== 1. 醉奸 ====
section("醉奸：射精与绝顶计入醉奸记录（不混进睡奸记录），结束无意识奸时按次数与对方是否仍烂醉结算")
DRUNK_ID_LIST = [951, 952, 953]
""" 醉奸的两级普通蚀刻章与烂醉的隐藏蚀刻章 """
DRUNK_TARGET_ID = 9601
drunk_target = make_character(DRUNK_TARGET_ID, "醉奸测试干员")
pl.target_character_id = DRUNK_TARGET_ID
drunk_target.sp_flag.unconscious_h = 2
config_row = {achievement_id: game_config.config_achievement.get(achievement_id) for achievement_id in DRUNK_ID_LIST}
check("配置：951、952 为「醉奸」类普通蚀刻章（952 以 951 为前置），953 为隐藏蚀刻章",
      all(config_row.values()) and all(data.type == _("醉奸") for data in config_row.values())
      and config_row[952].pre_id == 951 and not config_row[951].special and not config_row[952].special and config_row[953].special,
      {achievement_id: data and (data.type, data.value, data.pre_id, data.special) for achievement_id, data in config_row.items()})

# 醉奸开始时的记录初始化（同 handle_instruct 进入醉奸模式）
cache.achievement.drunk_sex_record = {1: 0, 2: 0, 3: 0}
cache.achievement.sleep_sex_record = {1: 0, 2: 0, 3: 0}
with mock.patch.object(ejaculation_panel, "common_ejaculation", return_value=("射精了", 10)):
    ejaculation_panel.ejaculation_flow(1, 0, DRUNK_TARGET_ID, draw_flag=False)
check("醉奸中射精：醉奸记录的射精次数 +1，睡奸记录不动",
      cache.achievement.drunk_sex_record[2] == 1 and cache.achievement.sleep_sex_record[2] == 0,
      (cache.achievement.drunk_sex_record, cache.achievement.sleep_sex_record))
orgasm_settle.orgasm_settle_in_second_behavior(DRUNK_TARGET_ID, game_type.CharacterStatusChange(), normal_orgasm_dict={4: 1})
check("被醉奸的干员绝顶：醉奸记录的绝顶次数 +1，睡奸记录不动",
      cache.achievement.drunk_sex_record[3] == 1 and cache.achievement.sleep_sex_record[3] == 0,
      (cache.achievement.drunk_sex_record, cache.achievement.sleep_sex_record))


def end_unconscious_h(ejaculation_count: int, climax_count: int, drunk_point: int, unconscious_flag: int = 2) -> list:
    """
    设好本次醉奸的次数与对方醉酒值后，走一遍「结束无意识奸」指令（推进时间打桩），返回其后已达成的醉奸蚀刻章
    Keyword arguments:
    ejaculation_count -- 本次射精次数
    climax_count -- 对方绝顶次数
    drunk_point -- 对方醉酒值（80 以下为醉酒，以上为烂醉）
    unconscious_flag -- 对方的无意识标记，2 为醉酒、1 为睡眠
    Return arguments:
    list -- 已达成的醉奸蚀刻章id
    """
    reset_achievement(DRUNK_ID_LIST)
    cache.achievement.drunk_sex_record = {1: 0, 2: ejaculation_count, 3: climax_count}
    drunk_target.drunk_point = drunk_point
    drunk_target.sp_flag.unconscious_h = unconscious_flag
    with mock.patch.object(handle_instruct.update, "game_update_flow", lambda *args, **kwargs: None):
        handle_instruct.handle_unconscious_h_end()
    return got_list(DRUNK_ID_LIST)


now_got = end_unconscious_h(1, 1, 60)
check("醉奸射精 1 次、对方醉酒未烂醉：只获得第一级", now_got == [951], now_got)
now_got = end_unconscious_h(3, 3, 60)
check("射精 3 次、对方绝顶 3 次：获得两级普通蚀刻章，对方没烂醉不获得隐藏蚀刻章", now_got == [951, 952], now_got)
now_got = end_unconscious_h(3, 3, 100)
check("射精 3 次、绝顶 3 次，结束时对方仍烂醉：同时获得隐藏蚀刻章", now_got == [951, 952, 953], now_got)
now_got = end_unconscious_h(3, 2, 100)
check("对方烂醉但只绝顶 2 次：不获得第二级与隐藏蚀刻章", now_got == [951], now_got)
now_got = end_unconscious_h(3, 3, 100, unconscious_flag=1)
check("结束的是睡奸（对方无意识标记为睡眠）：不结算醉奸蚀刻章", now_got == [], now_got)
reset_achievement(DRUNK_ID_LIST)
cache.achievement.drunk_sex_record = {}
cache.achievement.sleep_sex_record = {}
remove_character(DRUNK_TARGET_ID)

# ==== 2. 医疗 ====
section("医疗：医疗部累计收入与博士亲自诊疗人数各三级，亲自诊疗危重病人结算隐藏蚀刻章")
from Script.System.Medical_System import clinic_patient_management, medical_constant, medical_core, medical_player_diagnose_function, medical_service  # noqa: E402

INCOME_ID_LIST = [1081, 1082, 1083]
""" 医疗部累计收入，三级 """
DIAGNOSE_ID_LIST = [1086, 1087, 1088]
""" 博士累计亲自诊疗的病人数，三级 """
CRITICAL_ID = 1091
""" 博士亲自诊疗危重病人 """
MEDICAL_ID_LIST = INCOME_ID_LIST + DIAGNOSE_ID_LIST + [CRITICAL_ID]
RI = cache.rhodes_island
medical_core._ensure_runtime_dict(RI)
config_row = {achievement_id: game_config.config_achievement.get(achievement_id) for achievement_id in MEDICAL_ID_LIST}
check("配置：两组三级蚀刻章类型为「医疗」、逐级以上一级为前置、门槛递增、都不隐藏；危重病人为隐藏蚀刻章",
      all(config_row.values()) and all(data.type == _("医疗") for data in config_row.values())
      and [config_row[achievement_id].pre_id for achievement_id in INCOME_ID_LIST + DIAGNOSE_ID_LIST] == [0, 1081, 1082, 0, 1086, 1087]
      and all(config_row[id_list[i]].value < config_row[id_list[i + 1]].value for id_list in (INCOME_ID_LIST, DIAGNOSE_ID_LIST) for i in range(2))
      and not any(config_row[achievement_id].special for achievement_id in INCOME_ID_LIST + DIAGNOSE_ID_LIST) and config_row[CRITICAL_ID].special,
      {achievement_id: data and (data.type, data.value, data.pre_id, data.special) for achievement_id, data in config_row.items()})

# 累计收入：门槛边界与每日医疗结算
from Script.UI.Panel import achievement_panel  # noqa: E402

reset_achievement(MEDICAL_ID_LIST)
cache.achievement.player_diagnose_count = 0
RI.medical_income_total = config_row[1081].value - 1
check("累计收入差 1 龙门币到第一级：不获得", achievement_panel.settle_medical() == [], got_list(MEDICAL_ID_LIST))
RI.medical_income_total = config_row[1081].value
medical_service.settle_medical_department(target_base=RI, draw_flag=False)
check("累计收入到第一级门槛后的每日医疗结算：获得第一级", got_list(INCOME_ID_LIST) == [1081], got_list(MEDICAL_ID_LIST))
RI.medical_income_total = config_row[1082].value
check("累计收入到第二级门槛：获得第二级", achievement_panel.settle_medical() == [1082], got_list(MEDICAL_ID_LIST))
RI.medical_income_total = 0


def player_diagnose(severity_level: int) -> dict:
    """
    让博士接诊并完成一名指定病情等级的门诊病人
    Keyword arguments:
    severity_level -- 病情等级
    Return arguments:
    dict -- 诊疗结算摘要
    """
    patient = clinic_patient_management.create_patient_stub(severity_level)
    RI.medical_patients_today = {patient.patient_id: patient}
    RI.medical_player_current_patient_id = 0
    pl.work.medical_patient_id = 0
    medical_player_diagnose_function.start_player_diagnose_session(pl, target_base=RI)
    return medical_player_diagnose_function.commit_player_diagnose_session(pl, patient=patient, target_base=RI)


reset_achievement(MEDICAL_ID_LIST)
outcome = player_diagnose(0)
check("博士亲自诊疗一名轻症病人：诊疗计数 +1，获得第一级，不获得危重的隐藏蚀刻章",
      outcome.get("success") and cache.achievement.player_diagnose_count == 1 and got_list(MEDICAL_ID_LIST) == [1086],
      (outcome, cache.achievement.player_diagnose_count, got_list(MEDICAL_ID_LIST)))
outcome = player_diagnose(medical_constant.CRITICAL_SEVERITY_LEVEL)
check("博士亲自诊疗一名危重病人：获得隐藏蚀刻章", outcome.get("success") and cache.achievement.player_diagnose_count == 2 and CRITICAL_ID in got_list(MEDICAL_ID_LIST),
      (outcome, got_list(MEDICAL_ID_LIST)))
cache.achievement.player_diagnose_count = config_row[1087].value - 1
player_diagnose(0)
check("累计亲自诊疗人数到第二级门槛：获得第二级", 1087 in got_list(DIAGNOSE_ID_LIST), (cache.achievement.player_diagnose_count, got_list(DIAGNOSE_ID_LIST)))
reset_achievement(MEDICAL_ID_LIST)
cache.achievement.player_diagnose_count = 0
RI.medical_patients_today = {}
RI.player_examined_patient_ids.clear()

# ==== 3. 体液收藏 ====
section("体液收藏：挤奶、搾乳机、采尿器、绝顶喷乳 / 漏尿被收集时存进冰箱并计入收藏，累计母乳与圣水各三级，收集了亲生女儿的母乳为隐藏蚀刻章")
from Script.Settle import Second_effect, default as settle_default  # noqa: E402

MILK_ID_LIST = [226, 227, 228]
""" 累计收集的母乳，三级 """
URINE_ID_LIST = [231, 232, 233]
""" 累计收集的圣水，三级 """
DAUGHTER_MILK_ID = 236
""" 收集了亲生女儿的母乳 """
FLUID_ID_LIST = MILK_ID_LIST + URINE_ID_LIST + [DAUGHTER_MILK_ID]
config_row = {achievement_id: game_config.config_achievement.get(achievement_id) for achievement_id in FLUID_ID_LIST}
check("配置：两组三级蚀刻章类型为「体液收藏」、逐级以上一级为前置、门槛递增、都不隐藏；亲生女儿的母乳为隐藏蚀刻章",
      all(config_row.values()) and all(data.type == _("体液收藏") for data in config_row.values())
      and [config_row[achievement_id].pre_id for achievement_id in MILK_ID_LIST + URINE_ID_LIST] == [0, 226, 227, 0, 231, 232]
      and all(config_row[id_list[i]].value < config_row[id_list[i + 1]].value for id_list in (MILK_ID_LIST, URINE_ID_LIST) for i in range(2))
      and not any(config_row[achievement_id].special for achievement_id in MILK_ID_LIST + URINE_ID_LIST) and config_row[DAUGHTER_MILK_ID].special,
      {achievement_id: data and (data.type, data.value, data.pre_id, data.special) for achievement_id, data in config_row.items()})

FLUID_TARGET_ID = 9611
fluid_target = make_character(FLUID_TARGET_ID, "体液收藏测试干员")
pl_collection = pl.pl_collection
pl_collection.milk_total = {}
pl_collection.urine_total = {}
RI.milk_in_fridge = {}
RI.urine_in_fridge = {}
reset_achievement(FLUID_ID_LIST)

# 搾乳机：50ml 进冰箱与收藏，获得第一级；提示先于成就
fluid_target.h_state.body_item[4][1] = True
fluid_target.pregnancy.milk = 50
fluid_target.behavior.duration = 10
drawn_text.clear()
Second_effect.handle_milking_machine(FLUID_TARGET_ID, game_type.CharacterStatusChange())
drawn_joined = "\n".join(drawn_text)
check("搾乳机榨出 50ml：存进冰箱、计入收藏，获得母乳的第一级",
      RI.milk_in_fridge.get(FLUID_TARGET_ID) == 50 and pl_collection.milk_total.get(FLUID_TARGET_ID) == 50 and got_list(FLUID_ID_LIST) == [226],
      (RI.milk_in_fridge, pl_collection.milk_total, got_list(FLUID_ID_LIST)))
check("成就提示显示在榨乳文本之后",
      _("被搾乳机榨出了") in drawn_joined and _("获得蚀刻章") in drawn_joined and drawn_joined.index(_("被搾乳机榨出了")) < drawn_joined.index(_("获得蚀刻章")))
fluid_target.h_state.body_item[4][1] = False

# 绝顶喷乳：没戴搾乳机时不收集
fluid_target.pregnancy.milk_max = 200
fluid_target.pregnancy.milk = 200
Second_effect.handle_b_orgasm_to_milk(FLUID_TARGET_ID, game_type.CharacterStatusChange())
check("没戴搾乳机时绝顶喷乳：喷出的乳汁不进冰箱也不计入收藏", pl_collection.milk_total.get(FLUID_TARGET_ID) == 50, pl_collection.milk_total)
# 绝顶喷乳：戴着搾乳机时收集
fluid_target.h_state.body_item[4][1] = True
fluid_target.pregnancy.milk = 200
Second_effect.handle_b_orgasm_to_milk(FLUID_TARGET_ID, game_type.CharacterStatusChange())
check("戴着搾乳机绝顶喷乳：喷出的 160ml 计入收藏（200 + 40 - 80）", pl_collection.milk_total.get(FLUID_TARGET_ID) == 210, pl_collection.milk_total)
fluid_target.h_state.body_item[4][1] = False

# 博士亲手挤奶（行为结算）
pl.target_character_id = FLUID_TARGET_ID
fluid_target.pregnancy.milk = 30
settle_default.handle_milk_add_adjust(0, 1, game_type.CharacterStatusChange(), cache.game_time)
check("博士亲手挤奶 30ml：计入收藏", pl_collection.milk_total.get(FLUID_TARGET_ID) == 240 and fluid_target.pregnancy.milk == 0, pl_collection.milk_total)

# 采尿器与绝顶漏尿
fluid_target.h_state.body_item[5][1] = True
fluid_target.urinate_point = 30
Second_effect.handle_urine_collector(FLUID_TARGET_ID, game_type.CharacterStatusChange())
check("采尿器吸出 30ml：存进冰箱、计入收藏，获得圣水的第一级",
      RI.urine_in_fridge.get(FLUID_TARGET_ID) == 30 and pl_collection.urine_total.get(FLUID_TARGET_ID) == 30 and got_list(URINE_ID_LIST) == [231],
      (RI.urine_in_fridge, pl_collection.urine_total, got_list(URINE_ID_LIST)))
fluid_target.urinate_point = 200
Second_effect.handle_u_orgasm_to_pee(FLUID_TARGET_ID, game_type.CharacterStatusChange())
check("戴着采尿器绝顶漏尿：漏出的 152ml 计入收藏（200 + 48 - 96）", pl_collection.urine_total.get(FLUID_TARGET_ID) == 182, pl_collection.urine_total)
fluid_target.h_state.body_item[5][1] = False

# 门槛按全部干员合计
pl_collection.milk_total = {FLUID_TARGET_ID: config_row[227].value // 2, FLUID_TARGET_ID + 1: config_row[227].value // 2 - 1}
check("两名干员合计差 1ml 到母乳第二级：不获得", achievement_panel.settle_body_fluid_collection() == [], got_list(FLUID_ID_LIST))
pl_collection.milk_total[FLUID_TARGET_ID + 1] += 1
check("两名干员合计到母乳第二级门槛：获得第二级（按全部干员合计）", achievement_panel.settle_body_fluid_collection() == [227], got_list(FLUID_ID_LIST))

# 亲生女儿的母乳
DAUGHTER_ID = 9612
daughter = make_character(DAUGHTER_ID, "博士的女儿", daughter=True)
pl_collection.milk_total = {FLUID_TARGET_ID: 10}
check("收藏里只有非女儿干员的母乳：不获得隐藏蚀刻章", DAUGHTER_MILK_ID not in achievement_panel.settle_body_fluid_collection())
daughter.h_state.body_item[4][1] = True
daughter.pregnancy.milk = 20
daughter.behavior.duration = 10
Second_effect.handle_milking_machine(DAUGHTER_ID, game_type.CharacterStatusChange())
check("用搾乳机收集到亲生女儿的母乳：获得隐藏蚀刻章", DAUGHTER_MILK_ID in got_list(FLUID_ID_LIST), got_list(FLUID_ID_LIST))
reset_achievement(FLUID_ID_LIST)
pl_collection.milk_total = {}
pl_collection.urine_total = {}
RI.milk_in_fridge = {}
RI.urine_in_fridge = {}
remove_character(DAUGHTER_ID)
remove_character(FLUID_TARGET_ID)

# ==== 4. 信物 ====
section("信物：告白成功或戴上项圈获得信物时结算，累计信物数三级，获得亲生女儿的信物为隐藏蚀刻章")
from Script.Design import instuct_judege  # noqa: E402

TOKEN_ID_LIST = [241, 242, 243]
""" 累计获得的信物数，三级 """
DAUGHTER_TOKEN_ID = 246
""" 获得了亲生女儿的信物 """
ALL_TOKEN_ID_LIST = TOKEN_ID_LIST + [DAUGHTER_TOKEN_ID]
config_row = {achievement_id: game_config.config_achievement.get(achievement_id) for achievement_id in ALL_TOKEN_ID_LIST}
check("配置：三级蚀刻章类型为「信物」、逐级以上一级为前置、门槛递增、都不隐藏；亲生女儿的信物为隐藏蚀刻章",
      all(config_row.values()) and all(data.type == _("信物") for data in config_row.values())
      and [config_row[achievement_id].pre_id for achievement_id in TOKEN_ID_LIST] == [0, 241, 242]
      and config_row[241].value < config_row[242].value < config_row[243].value
      and not any(config_row[achievement_id].special for achievement_id in TOKEN_ID_LIST) and config_row[DAUGHTER_TOKEN_ID].special,
      {achievement_id: data and (data.type, data.value, data.pre_id, data.special) for achievement_id, data in config_row.items()})

TOKEN_TARGET_ID, TOKEN_DAUGHTER_ID = 9621, 9622
token_target = make_character(TOKEN_TARGET_ID, "信物测试干员")
token_daughter = make_character(TOKEN_DAUGHTER_ID, "信物测试女儿", daughter=True)
token_list = pl.pl_collection.token_list
saved_token_list = dict(token_list)
token_list.clear()
token_list.update({TOKEN_TARGET_ID: False, TOKEN_DAUGHTER_ID: False})
reset_achievement(ALL_TOKEN_ID_LIST)


def run_token_instruct(target_id: int, handler):
    """
    让交互对象满足信赖度、实行值判定通过（推进时间打桩），执行告白或戴上项圈指令
    Keyword arguments:
    target_id -- 交互对象id
    handler -- 指令处理函数
    Return arguments:
    无
    """
    pl.target_character_id = target_id
    cache.character_data[target_id].trust = 200
    with mock.patch.object(instuct_judege, "calculation_instuct_judege", lambda *args, **kwargs: [1, 1, 1.0]), \
            mock.patch.object(handle_instruct.update, "game_update_flow", lambda *args, **kwargs: None):
        handler()


drawn_text.clear()
run_token_instruct(TOKEN_TARGET_ID, handle_instruct.handle_confession)
drawn_joined = "\n".join(drawn_text)
check("告白成功获得非女儿干员的信物：获得第一级，不获得隐藏蚀刻章",
      token_list[TOKEN_TARGET_ID] and got_list(ALL_TOKEN_ID_LIST) == [241], (token_list, got_list(ALL_TOKEN_ID_LIST)))
check("成就提示显示在获得信物的文本之后",
      _("获得蚀刻章") in drawn_joined and drawn_joined.index(_("的信物：")) < drawn_joined.index(_("获得蚀刻章")))
run_token_instruct(TOKEN_DAUGHTER_ID, handle_instruct.handle_give_necklace)
check("给亲生女儿戴上项圈获得她的信物：获得隐藏蚀刻章", token_list[TOKEN_DAUGHTER_ID] and DAUGHTER_TOKEN_ID in got_list(ALL_TOKEN_ID_LIST), got_list(ALL_TOKEN_ID_LIST))

# 门槛：只数已获得（值为真）的信物
second_value = config_row[242].value
token_list.clear()
token_list.update({90000 + index: True for index in range(second_value - 1)})
token_list.update({91000 + index: False for index in range(5)})
check("已获得的信物差一个到第二级（未获得的不计）：不获得", achievement_panel.settle_token() == [], got_list(ALL_TOKEN_ID_LIST))
token_list[90000 + second_value] = True
check("已获得的信物到第二级门槛：获得第二级", achievement_panel.settle_token() == [242], got_list(ALL_TOKEN_ID_LIST))
reset_achievement(ALL_TOKEN_ID_LIST)
token_list.clear()
token_list.update(saved_token_list)
remove_character(TOKEN_DAUGHTER_ID)
remove_character(TOKEN_TARGET_ID)

finish()
