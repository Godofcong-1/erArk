# -*- coding: UTF-8 -*-
"""医疗经营系统核心编排模块

该模块负责协调医生与病人子模块的协同工作，
对外提供初始化、结算等高层接口，并重导出常用的业务函数。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from types import FunctionType

from Script.Config import normal_config
from Script.Core import game_type, get_text

from Script.System.Medical import (
    clinic_doctor_service,
    clinic_patient_management,
    hospital_doctor_service,
    hospital_patient_management,
    log_system,
    medical_constant,
    medical_core,
)

_: FunctionType = get_text._
""" 翻译函数 """

# --- 医生相关函数重导出 ---
assign_doctor_specialization = clinic_doctor_service.assign_doctor_specialization
list_role_doctors = clinic_doctor_service.list_role_doctors
get_specialization_categories = clinic_doctor_service.get_specialization_categories
get_doctor_specialization_overview = clinic_doctor_service.get_doctor_specialization_overview
acquire_patient_for_doctor = clinic_doctor_service.acquire_patient_for_doctor
prepare_doctor_medical_behavior = clinic_doctor_service.prepare_doctor_medical_behavior
update_doctor_assignments = clinic_doctor_service.update_doctor_assignments

conduct_ward_round = hospital_doctor_service.conduct_ward_round
get_surgery_candidate_patient_ids = hospital_doctor_service.get_surgery_candidate_patient_ids
attempt_surgery = hospital_doctor_service.attempt_surgery
consume_surgery_resources = hospital_doctor_service.consume_surgery_resources
evaluate_surgery_preconditions = hospital_doctor_service.evaluate_surgery_preconditions

# --- 病人相关函数重导出 ---
start_player_diagnose_session = clinic_patient_management.start_player_diagnose_session
abort_player_diagnose_session = clinic_patient_management.abort_player_diagnose_session
commit_player_diagnose_session = clinic_patient_management.commit_player_diagnose_session
execute_player_diagnose_checks = clinic_patient_management.execute_player_diagnose_checks
build_player_check_catalog = clinic_patient_management.build_player_check_catalog
estimate_patient_treatment_summary = clinic_patient_management.estimate_patient_treatment_summary
advance_diagnose = clinic_patient_management.advance_diagnose
set_patient_state = clinic_patient_management.set_patient_state
get_patient_table = clinic_patient_management.get_patient_table
get_medical_price_ratio = clinic_patient_management.get_medical_price_ratio
set_medical_price_ratio = clinic_patient_management.set_medical_price_ratio
get_patient_priority_mode = clinic_patient_management.get_patient_priority_mode
set_patient_priority_mode = clinic_patient_management.set_patient_priority_mode
predict_medical_patient_refresh = clinic_patient_management.predict_medical_patient_refresh
refresh_medical_patients = clinic_patient_management.refresh_medical_patients

try_consume_medicine = hospital_patient_management.try_consume_medicine
try_hospitalize = hospital_patient_management.try_hospitalize
process_hospitalized_patients = hospital_patient_management.process_hospitalized_patients
process_single_hospitalized_patient = hospital_patient_management.process_single_hospitalized_patient
resolve_surgery_requirements = hospital_patient_management.resolve_surgery_requirements
discharge_patient = hospital_patient_management.discharge_patient
refresh_patient_hospital_needs = hospital_patient_management.refresh_patient_hospital_needs

# --- 医疗日志相关函数重导出 ---
append_medical_report = log_system.append_medical_report
get_recent_medical_reports = log_system.get_recent_medical_reports
render_medical_reports = log_system.render_medical_reports

def init_medical_department_data(
    target_base: Optional[game_type.Rhodes_Island] = None,
    *,
    reset_runtime: bool = True,
    migrate_legacy: bool = False,
) -> None:
    """初始化医疗系统运行期数据结构。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定目标基地对象，默认读取全局缓存。
        reset_runtime (bool): 为 True 时重置全部运行期字段，通常在新开局或每日结算后调用。
        migrate_legacy (bool): 为 True 时执行旧版字段迁移，保障读档兼容性。
    返回:
        None: 直接在目标基地对象上原地修改，无显式返回值。
    """

    # 解析目标基地对象，若为空则直接返回。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return

    # 需要迁移旧字段时先处理历史数据，避免后续逻辑读到旧状态。
    if migrate_legacy:
        medical_core._migrate_legacy_income(rhodes_island)

    # 根据重置标记决定是否重新初始化所有运行期缓存字段。
    if reset_runtime:
        # 全量刷新运行期容器，消除旧局面遗留的引用。
        rhodes_island.medical_patients_today = {}
        rhodes_island.medical_hospitalized = {}
        rhodes_island.medical_surgery_records = []
        rhodes_island.medical_inventory_accumulator = {
            resource_id: 0.0 for resource_id in medical_constant.ALL_MEDICINE_RESOURCE_IDS
        }
        # 重置收入、计数器与医生配置。
        rhodes_island.medical_income_today = 0
        rhodes_island.medical_income_total = 0
        rhodes_island.medical_daily_counters = medical_constant.MedicalDailyCounters()
        rhodes_island.medical_recent_reports = []
        rhodes_island.medical_clinic_doctor_ids = []
        rhodes_island.medical_clinic_doctor_power = 0.0
        rhodes_island.medical_hospital_doctor_ids = []
        rhodes_island.medical_hospital_doctor_power = 0.0
        rhodes_island.medical_patient_priority_mode = medical_constant.MedicalPatientPriority.NORMAL.value
        rhodes_island.medical_player_current_patient_id = 0
        rhodes_island.medical_doctor_specializations = {}
    else:
        # 如果不重置则确保容器存在，并同步当前玩家诊疗状态。
        medical_core._ensure_runtime_dict(rhodes_island)
        rhodes_island.medical_player_current_patient_id = int(
            getattr(rhodes_island, "medical_player_current_patient_id", 0) or 0
        )

    # 门诊医生的专业结构需要在复用前确保初始化。
    clinic_doctor_service._ensure_specialization_structure(rhodes_island)

    # 没有收费系数时写入默认值，防止后续计算出现零值。
    if not rhodes_island.medical_price_ratio or rhodes_island.medical_price_ratio <= 0:
        rhodes_island.medical_price_ratio = medical_core._resolve_default_price_ratio()

    # 依据当前配置重新计算床位上限并同步旧计数器。
    rhodes_island.medical_bed_limit = medical_core._calculate_medical_bed_limit(rhodes_island)
    medical_core._sync_legacy_patient_counters(rhodes_island)

    # 若没有留存的病人数据则刷新今日病人列表。
    patient_table = getattr(rhodes_island, "medical_patients_today", {})
    should_refresh_patients = reset_runtime or not patient_table
    if should_refresh_patients:
        refresh_medical_patients(target_base=rhodes_island)


def update_medical_save_data_structure(cache_snapshot: Dict[str, Any]) -> None:
    """在读取旧存档时修复医疗系统相关字段。

    参数:
        cache_snapshot (Dict[str, Any]): 读档后的缓存快照，需包含 rhodes_island 键。
    返回:
        None: 函数仅在快照对象上执行补全与迁移操作。
    """

    # 仅当快照中存在合法的罗德岛对象时才执行迁移操作。
    rhodes_island = cache_snapshot.get("rhodes_island")
    if not isinstance(rhodes_island, game_type.Rhodes_Island):
        return

    # 使用运行期初始化逻辑对旧存档进行修复，避免重复代码。
    init_medical_department_data(rhodes_island, reset_runtime=False, migrate_legacy=True)


def settle_medical_department(
    *,
    target_base: Optional[game_type.Rhodes_Island] = None,
    draw_flag: bool = True,
) -> Dict[str, Any]:
    """执行每日医疗经营结算并输出日志。

    参数:
        target_base (Optional[game_type.Rhodes_Island]): 指定要结算的基地实例，默认使用全局缓存。
        draw_flag (bool): 为 True 时立即绘制文本日志，用于在 UI 中回显结算结果。
    返回:
        Dict[str, Any]: 汇总结算成功标记、收入、统计信息、队列快照以及日志文本。
    """

    # 定位当前结算目标的基地对象。
    rhodes_island = medical_core._get_rhodes_island(target_base)
    if rhodes_island is None:
        return {"success": False, "reason": "no_base"}

    # 确保运行期容器完整，防止结算中断。
    medical_core._ensure_runtime_dict(rhodes_island)

    # 先处理住院病人的日常消耗，避免统计落后一步。
    process_hospitalized_patients(target_base=rhodes_island)

    # 拉取显性日常计数器，确保结算阶段使用统一字段。
    counters = medical_core._obtain_daily_counters(rhodes_island)
    stats: Dict[str, int] = counters.as_dict() if counters else {}

    # 拉取实收收入与收费系数，供结算描述使用。
    income_today = int(rhodes_island.medical_income_today or 0)
    price_ratio = float(rhodes_island.medical_price_ratio or 1.0)

    # 统计队列中各状态人数，为日志与 UI 提供摘要。
    waiting_states = medical_constant.WAITING_QUEUE_STATE_SET
    patients = list(rhodes_island.medical_patients_today.values())
    hospitalized_patients = list(rhodes_island.medical_hospitalized.values())

    waiting_count = sum(1 for patient in patients if patient.state in waiting_states)
    waiting_medication = sum(
        1 for patient in patients if patient.state == medical_constant.MedicalPatientState.WAITING_MEDICATION
    )
    hospitalized_count = len(hospitalized_patients)
    need_surgery_count = sum(1 for patient in hospitalized_patients if patient.need_surgery)
    blocked_surgery_count = sum(
        1 for patient in hospitalized_patients if patient.need_surgery and patient.surgery_blocked
    )

    diagnose_outpatient = stats.get("diagnose_completed_outpatient", 0)
    diagnose_hospital = stats.get("diagnose_completed_hospital", 0)
    diagnose_total = diagnose_outpatient + diagnose_hospital
    medicine_outpatient = stats.get("medicine_completed_outpatient", 0)
    medicine_hospital = stats.get("medicine_completed_hospital", 0)
    medicine_total = medicine_outpatient + medicine_hospital
    medicine_consumed = stats.get("medicine_consumed", 0)
    hospitalized_today = stats.get("hospitalized_today", 0)
    discharged_today = stats.get("discharged_today", 0)
    surgeries_performed = stats.get("surgeries_performed", 0)
    outpatient_waiting_medicine = stats.get("outpatient_waiting_medicine", 0)
    hospital_waiting_medicine = stats.get("hospital_waiting_medicine", 0)

    # 拼装结算文本，按行描述核心指标。
    body_lines: List[str] = []
    body_lines.append(_("今日收入：{0} 龙门币").format(income_today))
    body_lines.append(_("收费系数：{0:.0f}%").format(price_ratio * 100))
    body_lines.append(
        _("诊疗完成：{0} 人（门诊 {1} / 住院 {2}）").format(
            diagnose_total,
            diagnose_outpatient,
            diagnose_hospital,
        )
    )
    body_lines.append(
        _("用药完成：{0} 人（门诊 {1} / 住院 {2}）").format(
            medicine_total,
            medicine_outpatient,
            medicine_hospital,
        )
    )
    if outpatient_waiting_medicine or hospital_waiting_medicine:
        body_lines.append(
            _("待发药：门诊 {0} 人 / 住院 {1} 人").format(outpatient_waiting_medicine, hospital_waiting_medicine)
        )
    body_lines.append(_("药品消耗：{0} 单位").format(medicine_consumed))
    body_lines.append(_("今日入院：{0} 人 / 出院：{1} 人").format(hospitalized_today, discharged_today))
    if surgeries_performed or blocked_surgery_count:
        body_lines.append(
            _("手术执行：成功 {0} 例 / 待条件 {1} 例").format(surgeries_performed, blocked_surgery_count)
        )
    body_lines.append(
        _("队列概况：待诊 {0} 人 / 待发药 {1} 人 / 住院 {2} 人 / 待手术 {3} 人").format(
            waiting_count,
            waiting_medication,
            hospitalized_count,
            need_surgery_count,
        )
    )

    # 记录队列快照，供日志与外部查询使用。
    queue_snapshot = {
        "waiting": waiting_count,
        "waiting_medication": waiting_medication,
        "hospitalized": hospitalized_count,
        "need_surgery": need_surgery_count,
        "surgery_blocked": blocked_surgery_count,
    }

    # 将结算结果写入医疗经营日志，供 UI 与历史记录查看。
    log_entry = log_system.append_medical_report(
        {
            "lines": [_("医疗部经营结算")] + body_lines,
            "income": income_today,
            "price_ratio": price_ratio,
            "stats": stats.copy(),
            "queue": queue_snapshot,
        },
        target_base=rhodes_island,
    )

    # 使用统一的日志渲染函数生成文本，并按需绘制在界面上。
    report_text = log_system.render_medical_reports(
        [log_entry],
        width=normal_config.config_normal.text_width,
        draw_flag=draw_flag,
    )

    # 触发成就面板刷新龙门币成就进度。
    from Script.UI.Panel import achievement_panel
    achievement_panel.achievement_flow(_("龙门币"))

    # 结算结束后重置当日收入与计数器，等待下一轮业务累计。
    rhodes_island.medical_income_today = 0
    rhodes_island.all_income = 0
    rhodes_island.medical_daily_counters = medical_constant.MedicalDailyCounters()

    refresh_medical_patients(target_base=rhodes_island)
    rhodes_island.medical_bed_limit = medical_core._calculate_medical_bed_limit(rhodes_island)
    medical_core._sync_legacy_patient_counters(rhodes_island)

    return {
        "success": True,
        "income": income_today,
        "stats": stats,
        "queue": queue_snapshot,
        "report": log_entry,
        "text": report_text,
    }
