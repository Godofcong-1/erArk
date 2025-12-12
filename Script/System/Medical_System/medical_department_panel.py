# -*- coding: UTF-8 -*-
"""医疗经营系统 UI 面板

该模块提供医疗部总面板及其子页面，便于玩家在单一入口管理医生排班、
收费系数、病患与手术以及财务信息。"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple, cast
from types import FunctionType

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, handle_ability
from Script.UI.Moudle import draw
from Script.System.Medical_System import medical_constant, medical_service

cache: game_type.Cache = cache_control.cache
""" 全局缓存对象 """
_: FunctionType = get_text._
""" 翻译函数 """
window_width: int = normal_config.config_normal.text_width
""" 默认面板宽度 """
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1

class Medical_Department_Panel:
    """医疗部总面板，负责导航至各子页面"""

    def __init__(self, width: int):
        """初始化面板并建立即插即用的子面板

        参数:
            width (int): 面板绘制宽度。
        返回:
            None
        """

        self.width = width
        self.panel_order: List[str] = [
            _("经营概览"),
            _("医生管理"),
            _("收费设置"),
            _("医疗明细"),
            _("手术管理"),
            _("财务报表"),
        ]
        self.current_panel: str = self.panel_order[0]
        self.sub_panels: Dict[str, _BaseSubPanel] = {
            self.panel_order[0]: OverviewSubPanel(width),
            self.panel_order[1]: DoctorManagementSubPanel(width),
            self.panel_order[2]: PriceSettingSubPanel(width),
            self.panel_order[3]: MedicalDetailSubPanel(width),
            self.panel_order[4]: SurgeryManagementSubPanel(width),
            self.panel_order[5]: FinanceReportSubPanel(width),
        }

    def draw(self) -> None:
        """绘制医疗部总面板并响应用户输入"""

        title_draw = draw.TitleLineDraw(_("医疗经营系统"), self.width)

        while True:
            return_list: List[str] = []
            title_draw.draw()

            # 绘制导航标签
            for panel_name in self.panel_order:
                if panel_name == self.current_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{panel_name}]"
                    now_draw.style = "onbutton"
                    now_draw.width = max(12, int(self.width / len(self.panel_order)))
                    now_draw.draw()
                else:
                    button_draw = draw.CenterButton(
                        f"[{panel_name}]",
                        panel_name,
                        max(12, int(self.width / len(self.panel_order))),
                        cmd_func=self.switch_panel,
                        args=(panel_name,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
            line_feed.draw()
            draw.LineDraw("+", self.width).draw()
            line_feed.draw()

            # 绘制当前子面板内容
            sub_panel = self.sub_panels[self.current_panel]
            sub_return_list = sub_panel.draw()
            return_list.extend(sub_return_list)

            line_feed.draw()
            back_button = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_button.draw()
            return_list.append(back_button.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_button.return_text:
                break

    def switch_panel(self, panel_name: str) -> None:
        """切换当前显示的子面板"""

        if panel_name in self.sub_panels:
            self.current_panel = panel_name


class _BaseSubPanel:
    """子面板基类，提供统一接口"""

    def __init__(self, width: int):
        self.width = width

    def draw(self) -> List[str]:
        """绘制子面板内容并返回交互按钮列表"""

        raise NotImplementedError()


class OverviewSubPanel(_BaseSubPanel):
    """经营概览子面板，汇总医疗部关键指标"""

    def draw(self) -> List[str]:
        return_list: List[str] = []
        ri = cache.rhodes_island

        outpatient_table = medical_service.get_patient_table(target_base=ri, hospitalized=False)
        hospital_table = medical_service.get_patient_table(target_base=ri, hospitalized=True)
        patients_today = list(outpatient_table.values())
        hospitalized = list(hospital_table.values())
        bed_limit = int(ri.medical_bed_limit)
        bed_occupied = len(hospital_table)
        price_ratio = medical_service.get_medical_price_ratio()
        priority_mode = medical_service.get_patient_priority_mode()

        pending_queue = sum(
            1
            for patient in patients_today
            if patient.state in medical_constant.WAITING_QUEUE_STATE_SET
        )
        waiting_medication = sum(
            1 for patient in patients_today if patient.state == medical_constant.MedicalPatientState.WAITING_MEDICATION
        )

        overview_draw = draw.NormalDraw()
        overview_draw.width = self.width
        overview_draw.text = _(
            "收费系数：{0:.2f} 倍 | 接诊优先策略：{1}\n"
        ).format(price_ratio, medical_constant.translate_priority(priority_mode))
        overview_draw.text += _(
            "门诊医生：{0} 人（医疗能力总和 {1}） | 住院医生：{2} 人（医疗能力总和 {3}）\n"
        ).format(
            len(ri.medical_clinic_doctor_ids),
            int(ri.medical_clinic_doctor_power or 0),
            len(ri.medical_hospital_doctor_ids),
            int(ri.medical_hospital_doctor_power or 0),
        )
        overview_draw.text += _(
            "门诊排队 {0} 人 | 等待用药 {1} 人 | 住院 {2}/{3} 张床位 | 今日收入 {4} 龙门币\n"
        ).format(
            pending_queue,
            waiting_medication,
            bed_occupied,
            bed_limit,
            int(ri.medical_income_today),
        )
        overview_draw.draw()

        line_feed.draw()

        state_counter: Dict[medical_constant.MedicalPatientState, int] = {
            state: 0 for state in medical_constant.MedicalPatientState
        }
        for patient in patients_today:
            state_counter[patient.state] += 1
        for patient in hospitalized:
            state_counter[patient.state] += 1

        state_draw = draw.NormalDraw()
        state_draw.width = self.width
        state_draw.text = _("病人状态统计：\n")
        for state in medical_constant.MedicalPatientState:
            state_draw.text += f"  {medical_constant.get_state_display_name(state)}：{state_counter.get(state, 0)} 人\n"
        state_draw.draw()

        line_feed.draw()

        accumulator_draw = draw.NormalDraw()
        accumulator_draw.width = self.width
        accumulator_draw.text = _("药品扣除缓存：\n")
        if ri.medical_inventory_accumulator:
            for resource_id, progress in sorted(ri.medical_inventory_accumulator.items()):
                resource_name = game_config.config_resouce.get(resource_id)
                name = getattr(resource_name, "name", str(resource_id))
                accumulator_draw.text += _("  {0}({1})：{2:.2f}\n").format(name, resource_id, float(progress))
        else:
            accumulator_draw.text += _("  暂无扣除记录\n")
        accumulator_draw.draw()

        return return_list


class DoctorManagementSubPanel(_BaseSubPanel):
    """医生管理子面板，提供手动调配与分科"""

    def __init__(self, width: int):
        super().__init__(width)
        self.feedback_text: str = ""

    def draw(self) -> List[str]:
        """绘制医生管理页面并返回所有按钮的返回值列表"""

        return_list: List[str] = []
        ri = cache.rhodes_island

        clinic_ids = medical_service.list_role_doctors(medical_constant.SPECIALIZATION_ROLE_CLINIC)
        hospital_ids = medical_service.list_role_doctors(medical_constant.SPECIALIZATION_ROLE_HOSPITAL)
        bed_limit = int(ri.medical_bed_limit)
        hospital_table = medical_service.get_patient_table(target_base=ri, hospitalized=True)
        bed_occupied = len(hospital_table)

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("门诊医生：{0} 人 | 医疗能力总和 {1}\n").format(
            len(clinic_ids), int(ri.medical_clinic_doctor_power or 0)
        )
        info_draw.text += _("住院医生：{0} 人 | 医疗能力总和 {1}\n").format(
            len(hospital_ids), int(ri.medical_hospital_doctor_power or 0)
        )
        info_draw.text += _("床位上限 {0} 张，当前占用 {1} 张\n").format(bed_limit, bed_occupied)
        estimated_hours = self._estimate_remaining_hours()
        info_draw.text += _("按当前排班预计完成全部门诊耗时约 {0:.2f} 小时\n").format(estimated_hours)
        info_draw.draw()

        line_feed.draw()

        from Script.UI.Panel import manage_basement_panel

        adjust_button = draw.CenterButton(
            _("[医生增减]"),
            _("医生增减"),
            max(len(_("[医生增减]")) * 2, 16),
            cmd_func=manage_basement_panel.change_npc_work_out,
            args=(self.width, [medical_constant.MedicalDoctorProfession.CLINICIAN, medical_constant.MedicalDoctorProfession.HOSPITALIST]),
        )
        adjust_button.draw()
        return_list.append(adjust_button.return_text)
        line_feed.draw()
        line_feed.draw()

        priority_mode = medical_service.get_patient_priority_mode()
        priority_title = draw.NormalDraw()
        priority_title.text = _("当前接诊优先策略：{0}\n").format(medical_constant.translate_priority(priority_mode))
        priority_title.width = self.width
        priority_title.draw()
        for mode, label in medical_constant.PRIORITY_OPTIONS:
            if mode == priority_mode:
                now_draw = draw.CenterDraw()
                now_draw.text = f"[{label}]"
                now_draw.style = "onbutton"
                now_draw.width = max(len(label) * 2 + 4, 16)
                now_draw.draw()
            else:
                button = draw.CenterButton(
                    f"[{label}]",
                    label,
                    max(len(label) * 2 + 4, 16),
                    cmd_func=self._set_priority_mode,
                    args=(mode,),
                )
                button.draw()
                return_list.append(button.return_text)
        line_feed.draw()
        line_feed.draw()

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("○全科医生看诊与治疗所有病人，但效率较低，专科医生仅看诊与治疗对应分科病人，效率更高。\n")
        info_draw.draw()
        line_feed.draw()
        self._draw_specialization_section(medical_constant.SPECIALIZATION_ROLE_CLINIC, return_list)
        line_feed.draw()
        # 仅在医疗区的等级大于等于3级时再显示住院医生分科
        if ri.facility_level.get(medical_constant.MEDICAL_FACILITY_ID, 0) >= 3:
            self._draw_specialization_section(medical_constant.SPECIALIZATION_ROLE_HOSPITAL, return_list)
            line_feed.draw()

        if self.feedback_text:
            feedback_draw = draw.NormalDraw()
            feedback_draw.width = self.width
            feedback_draw.text = f"\n{self.feedback_text}\n"
            feedback_draw.draw()

        return return_list

    def _draw_specialization_section(self, role_key: str, return_list: List[str]) -> None:
        """绘制指定岗位的医生分科信息并提供分配按钮"""

        overview = medical_service.get_doctor_specialization_overview(role_key)
        role_name = medical_constant.ROLE_DISPLAY_NAME.get(role_key, role_key)
        header_draw = draw.NormalDraw()
        header_draw.width = self.width
        header_draw.text = _("{0}科室情况：\n").format(role_name)
        header_draw.draw()

        for category in overview:
            doctor_details = category.get("doctor_details", [])
            doctor_texts = [
                _("{0}(Lv{1},x{2:.2f})").format(
                    detail.get("name", str(detail.get("id"))),
                    detail.get("ability_level", 0),
                    detail.get("bonus_multiplier", 1.0),
                )
                for detail in doctor_details
            ]
            category_draw = draw.NormalDraw()
            category_draw.width = self.width
            category_name = category.get("category_name", category.get("category_key", "-"))
            category_draw.text = _("  {0}（{1} 人，平均倍率 x{2:.2f}）").format(
                attr_calculation.pad_display_width(category_name, 16),
                category.get("doctor_count", 0),
                category.get("average_bonus_multiplier", 1.0),
            )
            category_draw.draw()

            action_label = _("分配到{0}").format(category_name)
            button_text = _("[分配]")
            assign_button = draw.CenterButton(
                button_text,
                role_key + action_label,
                max(len(button_text) * 2, 10),
                cmd_func=self._prompt_assign,
                args=(role_key, category.get("category_key", medical_constant.SPECIALIZATION_GENERAL_KEY)),
            )
            assign_button.draw()
            return_list.append(assign_button.return_text)

            # 绘制医生名字列表
            category_draw.text = _("：{0}").format("、".join(doctor_texts) if doctor_texts else _("空缺"),)
            category_draw.draw()

            line_feed.draw()

    def _prompt_assign(self, role_key: str, category_key: str) -> None:
        """弹出干员选择面板，将医生调整至指定分科"""

        doctor_ids = medical_service.list_role_doctors(role_key)
        if not doctor_ids:
            self.feedback_text = get_text._("当前岗位没有可分配的医生。")
            return

        categories = medical_service.get_specialization_categories()
        category_name = next((item["name"] for item in categories if item.get("key") == category_key), category_key)
        role_name = medical_constant.ROLE_DISPLAY_NAME.get(role_key, role_key)

        from Script.UI.Panel import common_select_NPC
        from Script.UI.Moudle import panel

        select_panel = panel.PageHandlePanel(
            cast(List[Any], []),
            common_select_NPC.CommonSelectNPCButtonList,
            50,
            5,
            self.width,
            True,
            False,
            0,
        )
        select_state: Dict[str, Any] = {}

        overview = medical_service.get_doctor_specialization_overview(role_key)
        assigned_ids = set()
        for category in overview:
            if category.get("category_key") == category_key:
                assigned_ids = set(category.get("doctor_ids", []))
                break

        result_holder: Dict[str, bool] = {"done": False}

        def _assign(doctor_id: int) -> None:
            result = medical_service.assign_doctor_specialization(role_key, doctor_id, category_key)
            if result.get("success"):
                character = cache.character_data.get(doctor_id)
                doctor_name = getattr(character, "name", str(doctor_id))
                self.feedback_text = get_text._("已将 {0} 调整至「{1}」({2})").format(doctor_name, category_name, role_name)
            else:
                self.feedback_text = get_text._("分配失败：{0}").format(result.get("reason", "unknown"))
            result_holder["done"] = True

        while True:
            entries: List[List[Any]] = [[doctor_id, _assign, list(assigned_ids)] for doctor_id in doctor_ids]
            select_panel.text_list = cast(List[Any], entries)
            info_text = get_text._("请选择一名{0}分配至「{1}」：\n").format(role_name, category_name)
            return_options, _, select_state = common_select_NPC.common_select_npc_button_list_func(
                select_panel,
                get_text._("分配医生"),
                info_text,
                select_state,
            )
            if not return_options:
                break
            choice = flow_handle.askfor_all(return_options)
            if choice == get_text._("返回"):
                break
            if result_holder.get("done"):
                break

    def _set_priority_mode(self, mode: medical_constant.MedicalPatientPriority) -> None:
        """切换病人接诊优先策略并提示结果"""
        resolved = medical_service.set_patient_priority_mode(mode)
        mode_text = medical_constant.translate_priority(resolved)
        # self.feedback_text = _("已切换接诊策略为：{0}").format(mode_text)

    def _estimate_remaining_hours(self) -> float:
        """估算当前门诊病人需要的剩余工时"""

        outpatient_table = medical_service.get_patient_table(
            target_base=cache.rhodes_island,
            hospitalized=False,
        )

        total_remaining = 0.0
        for patient in outpatient_table.values():
            if patient.state not in medical_constant.WAITING_QUEUE_STATE_SET:
                continue
            severity_config = game_config.config_medical_severity.get(patient.severity_level)
            if severity_config is None:
                continue
            base_hours = float(severity_config.base_hours)
            remaining = max(base_hours - float(patient.diagnose_progress), 0.0)
            total_remaining += remaining

        total_speed = 0.0
        for doctor_id in cache.rhodes_island.medical_clinic_doctor_ids:
            character = cache.character_data.get(doctor_id)
            if character is None:
                continue
            ability_level = character.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0)
            speed = max(float(handle_ability.get_ability_adjust(ability_level)), 0.25)
            total_speed += speed
        if total_speed <= 0:
            total_speed = 0.25
        return total_remaining / total_speed


class PriceSettingSubPanel(_BaseSubPanel):
    """收费设置子面板，维护医疗价格与预测信息"""

    def __init__(self, width: int):
        super().__init__(width)
        self.feedback_text: str = ""

    def draw(self) -> List[str]:
        """绘制收费设置面板并返回交互按钮列表"""

        return_list: List[str] = []
        ratio = medical_service.get_medical_price_ratio()
        level = cache.rhodes_island.facility_level.get(6, 0)
        preview = medical_service.predict_medical_patient_refresh(price_ratio=ratio, level=level)

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("当前收费系数：{0:.2f} 倍 ({1:.0f}%)\n").format(ratio, ratio * 100)
        info_draw.text += _("预计刷新病人数：{0:.0f} 人/日\n").format(preview.get("predicted_count", 0.0))
        info_draw.text += _(
            "刷新倍率修正：{0:.2f} | 收入倍率：{1:.2f}\n"
        ).format(preview.get("refresh_multiplier", 1.0), preview.get("income_multiplier", 1.0))
        info_draw.text += _("收费系数越高，病人刷新量越低，但单次收入越高。\n")
        info_draw.draw()
        line_feed.draw()

        # 百分比调节按钮
        adjust_options = [
            (-10, _("-10%")),
            (-5, _("-5%")),
            (-1, _("-1%")),
            (1, _("+1%")),
            (5, _("+5%")),
            (10, _("+10%")),
        ]
        for delta, label in adjust_options:
            button = draw.CenterButton(
                f"[{label}]",
                label,
                max(len(label) * 2 + 4, 10),
                cmd_func=self._adjust_ratio,
                args=(delta,),
            )
            button.draw()
            return_list.append(button.return_text)

        reset_button = draw.CenterButton(
            _("[重置为100%]"),
            _("重置收费"),
            max(len(_("[重置为100%]")) * 2, 18),
            cmd_func=self._reset_ratio,
        )
        reset_button.draw()
        return_list.append(reset_button.return_text)
        line_feed.draw()

        if self.feedback_text:
            feedback_draw = draw.NormalDraw()
            feedback_draw.width = self.width
            feedback_draw.text = f"\n{self.feedback_text}\n"
            feedback_draw.draw()

        return return_list

    def _adjust_ratio(self, delta_percent: int) -> None:
        """按百分比调整收费系数并刷新提示"""

        ratio = medical_service.get_medical_price_ratio()
        resolved_ratio = max(ratio + delta_percent / 100.0, 0.10)
        medical_service.set_medical_price_ratio(resolved_ratio)
        self.feedback_text = _("已调整收费系数至 {0:.2f} 倍").format(resolved_ratio)

    def _reset_ratio(self) -> None:
        """将收费系数重置为 1.0"""

        medical_service.set_medical_price_ratio(1.0)
        self.feedback_text = _("收费系数已重置为 1.00 倍")


class MedicalDetailSubPanel(_BaseSubPanel):
    """医疗明细子面板，可查看病患分布与药品缓存"""

    def draw(self) -> List[str]:
        """绘制医疗明细并返回交互按钮列表"""

        return_list: List[str] = []
        ri = cache.rhodes_island

        state_counter: Dict[medical_constant.MedicalPatientState, int] = {
            state: 0 for state in medical_constant.MedicalPatientState
        }
        outpatient_table = medical_service.get_patient_table(target_base=ri, hospitalized=False)
        hospital_table = medical_service.get_patient_table(target_base=ri, hospitalized=True)

        for patient in outpatient_table.values():
            state_counter[patient.state] += 1
        for patient in hospital_table.values():
            state_counter[patient.state] += 1

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("病人状态概览：\n")
        for state, count in state_counter.items():
            info_draw.text += f"  {medical_constant.get_state_display_name(state)}：{count} 人\n"
        info_draw.draw()
        line_feed.draw()

        # 仅展示前若干名病人摘要，避免输出过长
        preview_draw = draw.NormalDraw()
        preview_draw.width = self.width
        preview_draw.text = _("在诊病人示例：\n")
        pending_patients = [
            patient
            for patient in outpatient_table.values()
            if patient.state in medical_constant.WAITING_QUEUE_STATE_SET
        ]
        pending_patients.sort(key=lambda p: (-p.severity_level, p.patient_id))
        for patient in pending_patients[:6]:
            severity_name = patient.severity_name or str(patient.severity_level)
            preview_draw.text += _(
                "  病例#{0} 等级：{1} | 状态：{2} | 并发症数：{3}\n"
            ).format(
                patient.patient_id,
                severity_name,
                medical_constant.get_state_display_name(patient.state),
                len(patient.complications),
            )
        if not pending_patients:
            preview_draw.text += _("  当前无待诊病人\n")
        preview_draw.draw()
        line_feed.draw()

        accumulator_draw = draw.NormalDraw()
        accumulator_draw.width = self.width
        accumulator_draw.text = _("药品扣除缓存：\n")
        for resource_id, progress in sorted(ri.medical_inventory_accumulator.items()):
            resource_name = game_config.config_resouce.get(resource_id)
            name = getattr(resource_name, "name", str(resource_id))
            accumulator_draw.text += f"  {name}({resource_id})：{progress:.2f}\n"
        accumulator_draw.draw()

        return return_list


class SurgeryManagementSubPanel(_BaseSubPanel):
    """手术管理子面板，展示待手术与历史记录"""

    def draw(self) -> List[str]:
        """绘制手术管理界面"""

        return_list: List[str] = []
        ri = cache.rhodes_island

        hospital_table = medical_service.get_patient_table(target_base=ri, hospitalized=True)
        waiting_patients = [
            patient
            for patient in hospital_table.values()
            if patient.need_surgery
        ]
        waiting_patients.sort(key=lambda p: (-p.severity_level, p.patient_id))

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("待手术病人：{0} 人\n").format(len(waiting_patients))
        for patient in waiting_patients[:8]:
            severity_name = patient.severity_name or str(patient.severity_level)
            block_reason = patient.last_surgery_result or "-"
            info_draw.text += _(
                "  病例#{0} 等级：{1} | 阻塞：{2} | 需手术：{3}\n"
            ).format(
                patient.patient_id,
                severity_name,
                block_reason,
                "是" if patient.need_surgery else "否",
            )
        if not waiting_patients:
            info_draw.text += _("  当前无待手术病人\n")
        info_draw.draw()
        line_feed.draw()

        record_draw = draw.NormalDraw()
        record_draw.width = self.width
        record_draw.text = _("近期手术记录：\n")
        for record in cache.rhodes_island.medical_surgery_records[-10:]:
            doctor_data = cache.character_data.get(record.get("doctor_id", 0))
            doctor_name = getattr(doctor_data, "name", "-")
            record_draw.text += _(
                "  时间：{0} | 病例#{1} | 医生：{2} | 结果：{3}\n"
            ).format(
                str(record.get("time", "-")),
                record.get("patient_id", "-"),
                doctor_name or "-",
                record.get("status", "-"),
            )
        if not cache.rhodes_island.medical_surgery_records:
            record_draw.text += _("  暂无手术记录\n")
        record_draw.draw()

        return return_list


class FinanceReportSubPanel(_BaseSubPanel):
    """财务报表子面板，输出医疗收入与用药预估"""

    def draw(self) -> List[str]:
        """绘制财务报表信息"""

        return_list: List[str] = []
        ri = cache.rhodes_island

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("今日医疗收入：{0} 龙门币\n").format(int(ri.medical_income_today))
        info_draw.text += _("累计医疗收入：{0} 龙门币\n").format(int(ri.medical_income_total))

        counters = medical_constant.MedicalDailyCounters.from_mapping(getattr(ri, "medical_daily_counters", None))
        ri.medical_daily_counters = counters
        counter_dict = counters.as_dict()
        if counter_dict:
            info_draw.text += _("今日统计：\n")
            for key, value in counter_dict.items():
                if value is None:
                    continue
                display_name = medical_constant.DISPLAY_NAME_MAPPING.get(key, key)
                if key == "medicine_consumed":
                    consumption_map = medical_constant.MedicalDailyCounters._coerce_consumption_mapping(value)
                    total_units = sum(float(amount or 0.0) for amount in consumption_map.values())
                    info_draw.text += _("  {0}：总计 {1:.2f} 单位\n").format(display_name, total_units)
                    has_detail = False
                    for resource_id in sorted(consumption_map.keys()):
                        units = float(consumption_map.get(resource_id, 0.0) or 0.0)
                        if abs(units) <= medical_constant.FLOAT_EPSILON:
                            continue
                        resource_config = game_config.config_resouce.get(resource_id)
                        resource_name = getattr(resource_config, "name", str(resource_id)) if resource_config else str(resource_id)
                        info_draw.text += _("    {0}({1})：{2:.2f} 单位\n").format(resource_name, resource_id, units)
                        has_detail = True
                    if not has_detail:
                        info_draw.text += _("    暂无药品消耗记录\n")
                    continue
                info_draw.text += _("  {0}：{1}\n").format(display_name, value)
        else:
            info_draw.text += _("今日尚无额外统计数据\n")
        info_draw.draw()
        line_feed.draw()

        # 预估后续药品需求
        need_draw = draw.NormalDraw()
        need_draw.width = self.width
        need_draw.text = _("待诊/住院病人尚需药品：\n")
        aggregated: Dict[int, float] = {}
        outpatient_table = medical_service.get_patient_table(target_base=ri, hospitalized=False)
        hospital_table = medical_service.get_patient_table(target_base=ri, hospitalized=True)
        for group in (outpatient_table.values(), hospital_table.values()):
            for patient in group:
                if patient.state == medical_constant.MedicalPatientState.REFRESHED:
                    continue
                for resource_id, amount in patient.need_resources.items():
                    aggregated[resource_id] = aggregated.get(resource_id, 0.0) + float(amount)
        for resource_id, amount in sorted(aggregated.items()):
            resource = game_config.config_resouce.get(resource_id)
            name = getattr(resource, "name", str(resource_id))
            need_draw.text += _("  {0}({1})：{2:.2f}\n").format(name, resource_id, amount)
        need_draw.draw()

        line_feed.draw()
        log_button = draw.LeftButton(
            _("[401]查看最近经营日志"),
            _("查看最近经营日志"),
            self.width,
            cmd_func=self._show_recent_reports,
        )
        log_button.draw()
        line_feed.draw()
        return_list.append(log_button.return_text)

        return return_list

    def _show_recent_reports(self) -> None:
        """弹出最近几日的医疗经营日志"""

        reports = medical_service.get_recent_medical_reports(limit=3)
        medical_service.render_medical_reports(
            reports,
            width=self.width,
            draw_flag=True,
            empty_message=_("\n暂无医疗经营日志记录。\n"),
        )
