# -*- coding: UTF-8 -*-
"""医疗系统：检查目录与按钮文本、病人生成、检查判定、接诊/中止/结算会话、诊疗面板检查菜单（#327）与按钮驱动的完整诊疗流程"""
from _bootstrap import *  # noqa: F401,F403
from Script.System.Instruct_System import handle_instruct
from Script.System.Medical_System import (
    clinic_patient_management,
    medical_constant,
    medical_core,
    medical_player_diagnose_function,
    medical_player_diagnose_panel,
)

MC = medical_constant
DIAG = medical_player_diagnose_function
PANEL = medical_player_diagnose_panel
RI = cache.rhodes_island
medical_core._ensure_runtime_dict(RI)
random.seed(20261118)

# 博士：医疗能力 8 级（解锁全部诊疗提示等级）、话术 3 级（检查次数上限 6）
pl.ability[MC.MEDICAL_ABILITY_ID] = 8
pl.ability[PANEL.TALK_ABILITY_ID] = 3
pl.target_character_id = 0

# 诊疗面板退出时会调指令通用结算，那会进入真实主循环；改成只记录参数
settle_calls = []
""" 记录 _finalize_session 发起的指令结算 (behavior_id, duration, force_taget_wait) """


def _record_settle(behavior_id, duration=1, force_taget_wait=False, *args, **kwargs):
    """
    指令通用结算桩：只记录参数，不进入主循环
    Keyword arguments:
    behavior_id -- 行为id
    duration -- 持续时间
    force_taget_wait -- 是否强制交互对象等待
    Return arguments:
    无
    """
    settle_calls.append((behavior_id, duration, force_taget_wait))


handle_instruct.chara_handle_instruct_common_settle = _record_settle

# ==== 按钮记录：按钮的绘制桩会登记 返回文本 → (回调, 参数)，供脚本化的 askfor_all 模拟点击 ====
frame_buttons = []
""" 当前一帧画出的按钮 (显示文本, 返回文本, 样式, 回调, 参数)，每次 askfor_all 之后清空 """


def _record_button(self, *args, **kwargs):
    """
    按钮绘制桩：记录按钮并把文本收进 drawn_text
    Keyword arguments:
    self -- 按钮对象
    Return arguments:
    无
    """
    frame_buttons.append((str(self.text), self.return_text, getattr(self, "normal_style", "standard"), self.cmd_func, tuple(self.args or ())))
    drawn_text.append(str(self.text))


for _button_cls in (draw.Button, draw.CenterButton, draw.LeftButton):
    _button_cls.draw = _record_button


def system_button_names() -> list:
    """
    取本帧画出的系统按钮名（"   [+] 名称" / "   [-] 名称"）
    Keyword arguments:
    无
    Return arguments:
    list -- 系统名列表，按绘制顺序
    """
    return [text[7:] for text, _rt, _style, _f, _a in frame_buttons if text.startswith(("   [+] ", "   [-] "))]


def button_style(return_text: str) -> str:
    """
    取本帧中某个返回文本的按钮样式
    Keyword arguments:
    return_text -- 按钮返回文本
    Return arguments:
    str -- 样式名，没画出时为空串
    """
    for _text, now_return, style, _f, _a in frame_buttons:
        if now_return == return_text:
            return style
    return ""


# ==== 配置辅助 ====
SYSTEM_NAME = {sid: next(iter(part_map.values())).system_name for sid, part_map in game_config.config_medical_body_system_by_system.items()}
""" 系统id → 系统名 """
ALL_SYSTEM_NAMES = [SYSTEM_NAME[sid] for sid in sorted(SYSTEM_NAME)]
""" 按系统id排序的全部系统名，即检查菜单应有的系统顺序 """
FEMALE_ONLY_PARTS = {
    part_id for part_map in game_config.config_medical_body_system_by_system.values() for part_id, part in part_map.items() if int(part.gender_limit) == 0
}
""" 性别限制为 0 的部位（检查菜单与病人生成都跳过） """


def comp_list(system_id: int, part_id: int = 0, severity: int = -1) -> list:
    """
    按系统 / 部位 / 等级筛选并发症配置
    Keyword arguments:
    system_id -- 系统id
    part_id -- 部位id，0 为不限
    severity -- 严重等级，-1 为不限
    Return arguments:
    list -- 并发症配置列表，按 cid 排序
    """
    result = []
    for comp in game_config.config_medical_complication.values():
        if comp.system_id != system_id or (part_id and comp.part_id != part_id) or (severity >= 0 and comp.severity_level != severity):
            continue
        result.append(comp)
    return sorted(result, key=lambda comp: comp.cid)


def part_with_levels(system_id: int, levels: tuple) -> int:
    """
    找一个同时有这几个严重等级并发症、且不是女性限定的部位
    Keyword arguments:
    system_id -- 系统id
    levels -- 需要具备的严重等级
    Return arguments:
    int -- 部位id，找不到时为 0
    """
    for part_id in sorted(game_config.config_medical_body_system_by_system[system_id]):
        if part_id in FEMALE_ONLY_PARTS:
            continue
        if all(comp_list(system_id, part_id, level) for level in levels):
            return part_id
    return 0


def make_patient(comps: list, severity_level: int = 1, state=MC.MedicalPatientState.REFRESHED) -> MC.MedicalPatient:
    """
    造一个带指定并发症的病人
    Keyword arguments:
    comps -- 并发症配置列表
    severity_level -- 病情等级
    state -- 初始流程状态
    Return arguments:
    MC.MedicalPatient -- 病人对象
    """
    patient = clinic_patient_management.create_patient_stub(severity_level)
    patient.complications = [comp.cid for comp in comps]
    patient.complication_trace = [{"cid": comp.cid, "system_id": comp.system_id, "part_id": comp.part_id, "severity_level": comp.severity_level} for comp in comps]
    patient.need_resources[MC.MedicalMedicineResource.NORMAL.value] = 0.05
    clinic_patient_management.set_patient_state(patient, state)
    return patient


def reset_ward(*patient_list):
    """
    清空门诊并放入给定病人，同时解除博士的接诊绑定
    Keyword arguments:
    patient_list -- 病人对象
    Return arguments:
    无
    """
    RI.medical_patients_today = {patient.patient_id: patient for patient in patient_list}
    RI.medical_player_current_patient_id = 0
    RI.medical_patient_priority_mode = MC.MedicalPatientPriority.NORMAL.value
    pl.work.medical_patient_id = 0


def set_hint(value: int):
    """
    设置诊疗提示等级（系统设置第 12 项）
    Keyword arguments:
    value -- 提示等级
    Return arguments:
    无
    """
    cache.all_system_setting.base_setting[12] = value


NERVE = 10
""" 神经系统：检查菜单里排第一的系统 """
nerve_part = part_with_levels(NERVE, (0, 1))
other_nerve_part = next(pid for pid in sorted(game_config.config_medical_body_system_by_system[NERVE]) if pid != nerve_part and comp_list(NERVE, pid))
DIGEST = 40
""" 消化系统：排在中间的系统 """
CIRC = 30
""" 循环系统 """

section("检查目录与按钮文本")
probe_patient = make_patient(comp_list(NERVE, nerve_part, 1)[:1])
catalog = DIAG.build_player_check_catalog(probe_patient)
check("目录按系统id收录全部 8 个系统", sorted(catalog) == sorted(SYSTEM_NAME), sorted(catalog))
catalog_cids = []
for system_info in catalog.values():
    for part_info in system_info["parts"].values():
        catalog_cids.extend(option["cid"] for option in part_info["options"])
check("每条并发症在目录中恰好出现一次", sorted(catalog_cids) == sorted(game_config.config_medical_complication), len(catalog_cids))
bad_option = []
for system_id, system_info in catalog.items():
    for part_id, part_info in system_info["parts"].items():
        for option in part_info["options"]:
            comp = game_config.config_medical_complication[option["cid"]]
            if (comp.system_id, comp.part_id, comp.severity_level) != (system_id, part_id, option["severity_level"]):
                bad_option.append(option["cid"])
check("目录选项的系统 / 部位 / 等级与配置一致", not bad_option, bad_option[:20])
# Tk 模式下按钮按返回文本绑定回调（cmd_map），同一帧里两个按钮返回文本相同时后画的会顶掉先画的，点前一个就会执行后一个
fixed_button_texts = {_("切换检查菜单"), _("切换提示"), _("执行所选检查"), _("清空已选待检项"), _("开药并结束诊疗"), _("开药并接诊下一位"), _("提前结束诊疗并返回"), _("返回")}
collide = []
system_names = [info["system_name"] for info in catalog.values()]
if len(set(system_names)) != len(system_names):
    collide.append(("系统名重复", system_names))
for system_id, system_info in catalog.items():
    part_names = [info["part_name"] for info in system_info["parts"].values()]
    if len(set(part_names)) != len(part_names):
        collide.append(("部位名重复", system_id))
    for part_id, part_info in system_info["parts"].items():
        frame_texts = set(system_names) | set(part_names) | fixed_button_texts
        option_texts = [attr_calculation.pad_display_width(str(option["name"]), 38) for option in part_info["options"]]
        if len(set(option_texts)) != len(option_texts):
            collide.append(("同部位并发症名重复", part_id))
        hit = [text for text in option_texts if text in frame_texts or text.strip() in frame_texts]
        if hit:
            collide.append(("并发症名与系统 / 部位 / 固定按钮同名", part_id, hit))
check("检查菜单同一帧内的按钮返回文本互不相同", not collide, collide[:10])

section("病人生成")
random.seed(1)
gen_patient_list = []
for severity_level in sorted(game_config.config_medical_severity):
    for _i in range(60):
        gen_patient_list.append(clinic_patient_management.generate_patient(severity_level, RI))
check("各病情等级都能生成病人", all(patient is not None for patient in gen_patient_list))
bad_trace = []
bad_count = []
dup_part = []
for patient in gen_patient_list:
    severity_config = game_config.config_medical_severity[patient.severity_level]
    plan_count = int(severity_config.minor_complication_count) + int(severity_config.moderate_complication_count) + int(severity_config.severe_complication_count)
    if len(patient.complications) > plan_count or (plan_count and not patient.complications):
        bad_count.append((patient.severity_level, len(patient.complications), plan_count))
    trace_cids = [entry["cid"] for entry in patient.complication_trace]
    if trace_cids != patient.complications:
        bad_trace.append(patient.patient_id)
    for entry in patient.complication_trace:
        comp = game_config.config_medical_complication[entry["cid"]]
        if (comp.system_id, comp.part_id, comp.severity_level) != (entry["system_id"], entry["part_id"], entry["severity_level"]):
            bad_trace.append(patient.patient_id)
    part_ids = [entry["part_id"] for entry in patient.complication_trace]
    if len(set(part_ids)) != len(part_ids):
        dup_part.append(patient.patient_id)
check("并发症数量不超过病情配置的计划数、有计划时至少一条", not bad_count, bad_count[:10])
check("complication_trace 与 complications 一一对应且系统 / 部位 / 等级与配置一致", not bad_trace, bad_trace[:10])
check("同一病人的并发症不落在同一部位", not dup_part, dup_part[:10])
female_hit = [patient.patient_id for patient in gen_patient_list for entry in patient.complication_trace if entry["part_id"] in FEMALE_ONLY_PARTS]
check("病人生成不选性别限制为 0 的部位（检查菜单不显示这些部位，生成了就查不出来）", not female_hit, female_hit[:10])
check("生成的病人都有普通药需求", all(patient.need_resources.get(MC.MedicalMedicineResource.NORMAL.value, 0) > 0 for patient in gen_patient_list))

section("执行检查：阳性 / 需再检 / 阴性")
true_comp = comp_list(NERVE, nerve_part, 1)[0]
same_part_comp = comp_list(NERVE, nerve_part, 0)[0]
other_part_comp = comp_list(NERVE, other_nerve_part)[0]
patient = make_patient([true_comp])
patient.player_used_checks = 0


def selection(comp) -> dict:
    """
    把并发症配置转成一条待检选项
    Keyword arguments:
    comp -- 并发症配置
    Return arguments:
    dict -- 待检选项
    """
    return {"cid": comp.cid, "system_id": comp.system_id, "part_id": comp.part_id, "severity_level": comp.severity_level}


patient.player_pending_checks = [selection(same_part_comp), selection(other_part_comp)]
result = DIAG.execute_player_diagnose_checks(list(patient.player_pending_checks), patient=patient, target_base=RI)
records = {record["cid"]: record for record in result["results"]}
check("同部位换了等级 → 需再检，提示的是该部位的实际最高等级", records[same_part_comp.cid]["result"] == "recheck" and records[same_part_comp.cid]["hint_severity"] == 1, records[same_part_comp.cid])
check("需再检的提示文本取中症档", records[same_part_comp.cid]["message"] == (same_part_comp.recheck_hint_moderate or _("该部位存在其他异常，需更换检查方法。")))
check("别的部位 → 阴性", records[other_part_comp.cid]["result"] == "negative", records[other_part_comp.cid])
check("一次执行多项只计 1 次检查次数，并清空待检项", result["used_checks"] == 1 and patient.player_used_checks == 1 and patient.player_pending_checks == [])
check("未命中时不确诊", patient.player_confirmed_complications == [])
result = DIAG.execute_player_diagnose_checks([selection(true_comp)], patient=patient, target_base=RI)
check("命中实际并发症 → 阳性并确诊", result["results"][0]["result"] == "positive" and patient.player_confirmed_complications == [true_comp.cid], result["results"][0])
check("检查记录带第几次检查的序号", [record["check_index"] for record in patient.player_check_records] == [1, 1, 2])
empty_result = DIAG.execute_player_diagnose_checks([], patient=patient, target_base=RI)
check("空选择不执行、不计次数", not empty_result["success"] and patient.player_used_checks == 2)
for _i in range(12):
    DIAG.execute_player_diagnose_checks([selection(other_part_comp), selection(same_part_comp), selection(true_comp)], patient=patient, target_base=RI)
check("检查记录只保留最近 30 条", len(patient.player_check_records) == 30 and patient.player_check_records[-1]["check_index"] == 14)

section("接诊 / 中止 / 结算会话")
mild = make_patient([true_comp], severity_level=0)
critical = make_patient([true_comp], severity_level=MC.CRITICAL_SEVERITY_LEVEL)
other_doctor = make_patient([true_comp], severity_level=MC.CRITICAL_SEVERITY_LEVEL)
other_doctor.assigned_doctor_id = 999
waiting_medicine = make_patient([true_comp], severity_level=MC.CRITICAL_SEVERITY_LEVEL, state=MC.MedicalPatientState.WAITING_MEDICATION)
reset_ward(other_doctor, waiting_medicine, mild, critical)
picked = DIAG.start_player_diagnose_session(pl, target_base=RI)
check("默认策略优先接危重病人，跳过别的医生在看的与已进入发药流程的", picked is critical, getattr(picked, "patient_id", None))
check("接诊后病人进入玩家诊疗状态并锁定", critical.state == MC.MedicalPatientState.IN_TREATMENT_PLAYER and RI.medical_player_current_patient_id == critical.patient_id)
check("接诊后博士与病人互相绑定", pl.work.medical_patient_id == critical.patient_id and critical.assigned_doctor_id == 0 and critical.player_session_active)
critical.player_used_checks = 1
again = DIAG.start_player_diagnose_session(pl, target_base=RI)
check("已锁定病人时再次接诊返回同一个，会话数据不被重置", again is critical and critical.player_used_checks == 1)
DIAG.abort_player_diagnose_session(pl, patient=critical, target_base=RI)
check("中止后病人回到接诊前的状态", critical.state == MC.MedicalPatientState.REFRESHED)
check("中止后清空会话数据并解除锁定", not critical.player_session_active and critical.player_used_checks == 0 and RI.medical_player_current_patient_id == 0 and pl.work.medical_patient_id == 0)
reset_ward(other_doctor, mild, critical)
RI.medical_patient_priority_mode = MC.MedicalPatientPriority.FOCUS_MILD.value
check("轻症优先策略接轻症病人", DIAG.start_player_diagnose_session(pl, target_base=RI) is mild)
DIAG.abort_player_diagnose_session(pl, patient=mild, target_base=RI)

reset_ward(mild)
RI.materials_resouce[1] = RI.materials_resouce.get(1, 0)
for resource_id in MC.ALL_MEDICINE_RESOURCE_IDS:
    RI.materials_resouce[resource_id] = 100
DIAG.start_player_diagnose_session(pl, target_base=RI)
mild.player_used_checks = 1
mild.player_confirmed_complications = [true_comp.cid]
income_before = RI.medical_income_today
money_before = RI.materials_resouce[1]
expected_income = clinic_patient_management.estimate_patient_diagnose_income(mild, target_base=RI)
outcome = DIAG.commit_player_diagnose_session(pl, patient=mild, target_base=RI)
check("结算成功、库存充足时直接发药", outcome.get("success") and outcome.get("medicine_success") and mild.state == MC.MedicalPatientState.MEDICINE_GRANTED, outcome)
check("诊疗收益含检查次数加成并计入当日医疗收入与龙门币", outcome["diagnose_income"] == expected_income and RI.medical_income_today - income_before >= expected_income and RI.materials_resouce[1] - money_before >= expected_income)
check("结算后解除锁定并记入博士看过的病人", RI.medical_player_current_patient_id == 0 and mild.patient_id in RI.player_examined_patient_ids)

section("诊疗面板：检查菜单（#327）")


def open_panel(patient) -> PANEL.MedicalPlayerDiagnosePanel:
    """
    门诊只放这一个病人，打开诊疗面板（构造时即接诊）
    Keyword arguments:
    patient -- 病人对象，None 为门诊空无一人
    Return arguments:
    PANEL.MedicalPlayerDiagnosePanel -- 面板对象
    """
    if patient is None:
        reset_ward()
    else:
        reset_ward(patient)
    return PANEL.MedicalPlayerDiagnosePanel(190)


def draw_menu(panel, confirmed: list, used_checks: int = 1, expand: bool = True) -> list:
    """
    以给定确诊列表画一帧检查菜单，返回画出的系统名
    Keyword arguments:
    panel -- 面板对象
    confirmed -- 已确诊并发症id列表
    used_checks -- 已用检查次数
    expand -- 是否处于展开状态
    Return arguments:
    list -- 画出的系统名
    """
    panel.patient.player_confirmed_complications = list(confirmed)
    panel.patient.player_used_checks = used_checks
    panel.menu_expanded = expand
    frame_buttons.clear()
    drawn_text.clear()
    panel._draw_check_menu([], [], list(confirmed), used_checks)
    return system_button_names()


nerve_a = comp_list(NERVE, nerve_part, 1)[0]
nerve_b = comp_list(NERVE, other_nerve_part)[0]
circ_c = comp_list(CIRC)[0]
digest_d = comp_list(DIGEST)[0]
panel = open_panel(make_patient([nerve_a, nerve_b, circ_c]))
set_hint(0)
check("未确诊时展开菜单画出全部系统", draw_menu(panel, []) == ALL_SYSTEM_NAMES, system_button_names())
shown = draw_menu(panel, [nerve_a.cid, nerve_b.cid])
check("提示关闭、排第一的系统已确诊：仍画出全部系统（#327 截图 2 的情形，原先一个都不画）", shown == ALL_SYSTEM_NAMES, shown)
check("该系统按钮灰显、其余系统保持默认样式", button_style(SYSTEM_NAME[NERVE]) == "deep_gray" and button_style(SYSTEM_NAME[CIRC]) == "standard")
set_hint(1)
shown = draw_menu(panel, [nerve_a.cid, nerve_b.cid])
check("提示开启、已确诊完的系统不再高亮：仍画出全部系统（#327）", shown == ALL_SYSTEM_NAMES, shown)
check("提示开启时只高亮仍有未确诊并发症的系统", button_style(SYSTEM_NAME[CIRC]) == "gold_enrod" and button_style(SYSTEM_NAME[NERVE]) == "deep_gray")
DIAG.abort_player_diagnose_session(pl, patient=panel.patient, target_base=RI)
panel = open_panel(make_patient([digest_d, circ_c]))
set_hint(0)
shown = draw_menu(panel, [digest_d.cid])
check("已确诊系统排在中间：其后的系统不缺失（#327「部分选项缺失」）", shown == ALL_SYSTEM_NAMES, shown)
draw_menu(panel, [digest_d.cid, circ_c.cid])
check("全部确诊后不再显示检查菜单", not any(rt == _("切换检查菜单") for _t, rt, _s, _f, _a in frame_buttons))
draw_menu(panel, [], used_checks=panel.max_checks)
check("检查次数用完后不再显示检查菜单", not any(rt == _("切换检查菜单") for _t, rt, _s, _f, _a in frame_buttons))
panel.expanded_system_id = 60
draw_menu(panel, [])
part_texts = [text for text, _rt, _s, _f, _a in frame_buttons if text.startswith("     [")]
female_names = {game_config.config_medical_body_system_by_system[60][pid].part_name for pid in FEMALE_ONLY_PARTS if pid in game_config.config_medical_body_system_by_system[60]}
check("展开系统后列出其部位，性别限制为 0 的部位不显示", part_texts and not any(text[9:] in female_names for text in part_texts), part_texts)
panel.expanded_system_id = DIGEST
panel.expanded_part_id = digest_d.part_id
panel.executed_complication_ids = [digest_d.cid]
draw_menu(panel, [])
check("已执行过的检查项以（已检查）灰字画出、不再是按钮", any(text.startswith(_("（已检查）")) for text in drawn_text) and not any(args == (DIGEST, digest_d.part_id, digest_d.cid) for _t, _rt, _s, _f, args in frame_buttons))
DIAG.abort_player_diagnose_session(pl, patient=panel.patient, target_base=RI)

section("诊疗面板：按钮驱动的完整流程")


class ScriptedChoice:
    """
    脚本化的 askfor_all：每一步给一个按钮匹配函数，找到本帧对应按钮后执行其回调并返回其返回文本
    """

    def __init__(self, step_list: list):
        """
        初始化
        Keyword arguments:
        step_list -- 步骤列表，每项为 (说明, 匹配函数(显示文本, 返回文本, 参数) -> bool)
        Return arguments:
        无
        """
        self.step_list = list(step_list)
        self.error = ""
        self.done = []

    def __call__(self, return_list, *args, **kwargs):
        """
        选择本帧的一个按钮
        Keyword arguments:
        return_list -- 本帧可选的返回文本
        Return arguments:
        str -- 选中的返回文本
        """
        if not self.step_list or self.error:
            # 步骤用完还没退出面板：记下错误并强行结束，避免死循环
            self.error = self.error or "步骤用完面板仍未关闭"
            raise RuntimeError(self.error)
        label, matcher = self.step_list.pop(0)
        for text, return_text, _style, cmd_func, args in frame_buttons:
            if matcher(text, return_text, args) and return_text in return_list:
                frame_buttons.clear()
                self.done.append(label)
                if cmd_func is not None:
                    cmd_func(*args)
                return return_text
        self.error = "找不到按钮：" + label
        raise RuntimeError(self.error)


def run_panel(patient, step_list: list) -> tuple:
    """
    打开诊疗面板并按脚本点击，直到面板关闭
    Keyword arguments:
    patient -- 病人对象
    step_list -- 点击步骤
    Return arguments:
    tuple -- (面板对象, 脚本对象, 异常文本)
    """
    settle_calls.clear()
    frame_buttons.clear()
    chooser = ScriptedChoice(step_list)
    flow_handle.askfor_all = chooser
    now_panel = open_panel(patient)
    error_text = ""
    try:
        now_panel.draw()
    except RuntimeError as error:
        error_text = str(error)
    return now_panel, chooser, error_text


def by_return(text: str):
    """
    按返回文本匹配按钮
    Keyword arguments:
    text -- 返回文本
    Return arguments:
    function -- 匹配函数
    """
    return lambda now_text, return_text, args: return_text == text


set_hint(0)
flow_comp = comp_list(CIRC)[0]
flow_patient = make_patient([flow_comp], severity_level=1)
step_list = [
    ("展开检查菜单", by_return(_("切换检查菜单"))),
    ("展开系统", by_return(SYSTEM_NAME[CIRC])),
    ("展开部位", by_return(game_config.config_medical_body_system_by_system[CIRC][flow_comp.part_id].part_name)),
    ("勾选并发症", lambda now_text, return_text, args: args == (CIRC, flow_comp.part_id, flow_comp.cid)),
    ("执行检查", by_return(_("执行所选检查"))),
    ("开药并结束", by_return(_("开药并结束诊疗"))),
]
flow_panel, chooser, error_text = run_panel(flow_patient, step_list)
check("按钮流程走完：展开 → 勾选 → 检查 → 开药结束", not error_text and len(chooser.done) == 6, (error_text, chooser.done))
check("检查结果阳性并确诊", flow_patient.player_confirmed_complications == [flow_comp.cid] and flow_panel.last_check_results[0]["result"] == "positive")
check("结束后病人离开待诊队列、解除锁定", flow_patient.state not in MC.WAITING_QUEUE_STATE_SET and RI.medical_player_current_patient_id == 0, flow_patient.state)
check("退出面板按诊疗行为结算，耗时为检查次数 × 10 分钟", settle_calls == [(constant.Behavior.CURE_PATIENT, 10, False)], settle_calls)

two_comp = [comp_list(CIRC)[0], comp_list(DIGEST)[0]]
two_patient = make_patient(two_comp, severity_level=1)
step_list = [
    ("展开检查菜单", by_return(_("切换检查菜单"))),
    ("展开系统", by_return(SYSTEM_NAME[CIRC])),
    ("展开部位", by_return(game_config.config_medical_body_system_by_system[CIRC][two_comp[0].part_id].part_name)),
    ("勾选并发症", lambda now_text, return_text, args: args == (CIRC, two_comp[0].part_id, two_comp[0].cid)),
    ("执行检查", by_return(_("执行所选检查"))),
    ("开药并结束（还有未确诊）", by_return(_("开药并结束诊疗"))),
    ("返回继续检查", by_return(_("[返回继续检查]"))),
    ("再展开检查菜单（确诊后仍能展开其余系统）", by_return(_("切换检查菜单"))),
    ("展开另一个系统", by_return(SYSTEM_NAME[DIGEST])),
    ("开药并结束", by_return(_("开药并结束诊疗"))),
    ("确认就这样治疗", by_return(_("[确认就这样治疗]"))),
]
two_panel, chooser, error_text = run_panel(two_patient, step_list)
check("有未确诊项时开药要二次确认，可返回继续检查，确诊一项后菜单仍完整（#327）", not error_text and len(chooser.done) == len(step_list), (error_text, chooser.done))
check("确认后按 1 次检查结算", settle_calls == [(constant.Behavior.CURE_PATIENT, 10, False)], settle_calls)

abort_patient = make_patient([flow_comp], severity_level=1)
abort_panel, chooser, error_text = run_panel(abort_patient, [("提前结束", by_return(_("提前结束诊疗并返回")))])
check("未做检查时可提前结束，病人回到待诊", not error_text and abort_patient.state == MC.MedicalPatientState.REFRESHED and RI.medical_player_current_patient_id == 0, error_text)
check("提前结束按等待结算 5 分钟", settle_calls == [(constant.Behavior.WAIT, 5, True)], settle_calls)

empty_panel, chooser, error_text = run_panel(None, [])
check("门诊没有病人时面板直接提示并返回", not error_text and any(_("暂无可供博士亲自诊疗的病人") in text for text in drawn_text) and settle_calls == [])

finish()
