# -*- coding: UTF-8 -*-
"""玩家诊疗专用交互面板"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from types import FunctionType

from Script.Config import game_config, normal_config
from Script.Core import cache_control, constant, game_type, get_text, flow_handle
from Script.Design import basement, instuct_judege, update
from Script.System.medical import medical_constant, medical_service
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 全局缓存对象 """
_: FunctionType = get_text._
""" 翻译函数 """
window_width: int = normal_config.config_normal.text_width
""" 默认面板宽度 """
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1

_MEDICAL_FACILITY_ID = 6
"""医疗部设施 ID，与医疗系统保持一致"""


def start_player_diagnose_flow() -> bool:
    """启动玩家亲自诊疗流程。

    功能:
        构建并绘制玩家诊疗专用面板，结合界面返回值判断是否需要拦截原始指令。

    参数:
        无。

    返回:
        bool: 当函数返回 True 时，表示面板已经完整接管并消耗原本的行为结算。
    """

    panel = MedicalPlayerDiagnosePanel(window_width)
    return panel.draw()


class MedicalPlayerDiagnosePanel:
    """负责绘制与驱动玩家诊疗流程的面板。

    该类封装诊疗会话的创建、界面刷新、操作响应以及会话收束时的时间成本结算，
    避免在其他模块中散落处理流程的细节。
    """

    def __init__(self, width: int):
        """初始化面板实例并尝试创建诊疗会话。

        参数:
            width (int): 面板默认绘制宽度，用于控制文本换行表现。

        返回:
            None: 构造函数仅更新内部状态，不返回任何值。
        """
        self.width = width
        self.player: Optional[game_type.Character] = cache.character_data.get(0)
        self.patient: Optional[medical_constant.MedicalPatient] = None
        self.session_active: bool = False
        self.feedback_text: str = ""
        self.last_check_results: List[Dict[str, object]] = []
        self.treatment_result: Optional[Dict[str, object]] = None
        self._should_close: bool = False
        self._treatment_committed: bool = False
        self._abort_requested: bool = False
        self._checks_executed: int = 0
        self.menu_expanded: bool = False
        self.expanded_systems: Set[int] = set()
        self.expanded_parts: Dict[int, Set[int]] = {}

        if self.player is not None:
            self.patient = medical_service.start_player_diagnose_session(self.player)
        if self.patient is not None:
            self.session_active = True
            self.check_catalog: Dict[int, Dict[str, object]] = medical_service.build_player_check_catalog(self.patient)
        else:
            self.check_catalog = {}

        self.player_med_level = 0
        if self.player is not None:
            self.player_med_level = int(self.player.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)

        self.target_complication_count = 0
        if self.patient is not None and getattr(self.patient, "complications", None):
            self.target_complication_count = len(self.patient.complications)

        self.max_parallel = max(1, self.target_complication_count or 1)
        self.max_checks = max(1, self.player_med_level * 2)

    def draw(self) -> bool:
        """循环绘制诊疗面板，并根据用户操作决定会话去向。

        参数:
            无。

        返回:
            bool: True 表示面板已经接管原指令，False 理论上不会出现（无病人时也返回 True）。
        """

        if not self.session_active:
            title_draw = draw.TitleLineDraw(_("医疗诊疗"), self.width)
            title_draw.draw()
            tip_draw = draw.NormalDraw()
            tip_draw.width = self.width
            tip_draw.text = _("当前医疗部暂无可供玩家亲自诊疗的病人。") + "\n"
            tip_draw.draw()
            return True

        while not self._should_close:
            title_draw = draw.TitleLineDraw(_("医疗诊疗"), self.width)
            title_draw.draw()
            return_list: List[str] = []

            pending_checks = self._get_pending_checks()
            confirmed_complications = self._get_confirmed_complications()
            used_checks = 0
            if self.patient is not None:
                used_checks = int(self.patient.metadata.get("player_used_checks", 0) or 0)

            self._draw_patient_overview()
            self._draw_hint_section()
            self._draw_check_status(pending_checks, confirmed_complications, used_checks)
            self._draw_check_menu(return_list, pending_checks, confirmed_complications, used_checks)
            self._draw_treatment_methods(confirmed_complications, used_checks)
            self._draw_feedback()

            self._draw_operation_buttons(return_list, pending_checks, confirmed_complications, used_checks)
            if not return_list:
                # 至少提供一个默认返回项避免阻塞
                default_back = draw.CenterButton(_("[返回]"), "back", self.width, cmd_func=self._handle_abort)
                default_back.draw()
                return_list.append(default_back.return_text)

            choice = flow_handle.askfor_all(return_list)
            if choice == "back":
                self._handle_abort()

        self._finalize_session()
        return True

    # --- 绘制逻辑 ---------------------------------------------------------

    def _draw_patient_overview(self) -> None:
        """绘制病患基础信息与主诉描述。

        参数:
            无。

        返回:
            None: 仅负责界面输出，不返回数据。
        """
        if self.patient is None:
            return
        info_draw = draw.NormalDraw()
        info_draw.width = self.width

        severity_name = self.patient.metadata.get("severity_name")
        if not severity_name:
            config = game_config.config_medical_severity.get(self.patient.severity_level)
            severity_name = config.name if config else _("未知病情")

        race_name = _("未知种族")
        race_config = game_config.config_race.get(self.patient.race_id)
        if race_config is not None:
            race_name = race_config.name

        info_draw.text = _(
            "患者编号：{pid} | 病情：{severity}\n年龄：{age} 岁 | 种族：{race}\n"
        ).format(
            pid=self.patient.patient_id,
            severity=severity_name,
            age=self.patient.age,
            race=race_name,
        )

        complaint_lines: List[str] = []
        trace_list = self.patient.metadata.get("complication_trace", [])
        for entry in trace_list:
            comp_config = game_config.config_medical_complication.get(entry.get("cid", entry.get("complication_id", 0)))
            if comp_config is None:
                continue
            system_id = int(entry.get("system_id", 0) or 0)
            part_id = int(entry.get("part_id", 0) or 0)
            system_map = game_config.config_medical_body_system_by_system.get(system_id, {})
            part_info = system_map.get(part_id)
            system_name = part_info.system_name if part_info else _("未知系统")
            part_name = part_info.part_name if part_info else _("未知部位")
            statement = comp_config.patient_statement_clear
            if self.patient.personality_type == medical_constant.MedicalPatientPersonality.IRRATIONAL:
                statement = comp_config.patient_statement_vague
            complaint_lines.append(
                _("· {name} ({system}/{part})\n  外观：{appearance}\n  病人自述：{statement}").format(
                    name=comp_config.name,
                    system=system_name,
                    part=part_name,
                    appearance=comp_config.appearance_indicator,
                    statement=statement,
                )
            )

        if complaint_lines:
            info_draw.text += "\n" + "\n".join(complaint_lines) + "\n"
        info_draw.draw()
        line_feed.draw()

    def _draw_hint_section(self) -> None:
        """绘制诊疗提示状态及具体提示文本。

        参数:
            无。

        返回:
            None: 状态展示性函数。
        """
        if self.patient is None:
            return
        hint_enabled = bool(self.patient.metadata.get("player_hint_enabled", False))
        status_draw = draw.NormalDraw()
        status_draw.width = self.width
        status_draw.text = _("治病提示：{status}\n").format(status=_("开启") if hint_enabled else _("关闭"))
        status_draw.draw()

        if hint_enabled:
            hint_text = self._build_hint_text()
            if hint_text:
                hint_draw = draw.NormalDraw()
                hint_draw.width = self.width
                hint_draw.text = hint_text + "\n"
                hint_draw.draw()
        line_feed.draw()

    def _draw_check_status(
        self,
        pending: List[Dict[str, int]],
        confirmed: List[int],
        used_checks: int,
    ) -> None:
        """展示检查次数、待执行检查以及已确诊列表。

        参数:
            pending (List[Dict[str, int]]): 当前已勾选待执行的检查集合。
            confirmed (List[int]): 已确诊的并发症 ID 列表。
            used_checks (int): 本次会话已使用的检查次数。

        返回:
            None: 在界面上输出状态信息。
        """
        if self.patient is None:
            return

        status_draw = draw.NormalDraw()
        status_draw.width = self.width
        status_draw.text = _("检查次数：{used}/{limit}（单次可并行 {parallel} 项）\n").format(
            used=used_checks,
            limit=self.max_checks,
            parallel=self.max_parallel,
        )
        if pending:
            pend_lines = []
            catalog = self.check_catalog
            for option in pending:
                system_info = catalog.get(option["system_id"], {})
                if not isinstance(system_info, dict):
                    system_info = {}
                part_map = system_info.get("parts") if isinstance(system_info, dict) else {}
                if not isinstance(part_map, dict):
                    part_map = {}
                part_info = part_map.get(option["part_id"], {}) if isinstance(part_map, dict) else {}
                if not isinstance(part_info, dict):
                    part_info = {}
                comp_config = game_config.config_medical_complication.get(option["cid"])
                name = comp_config.name if comp_config else str(option["cid"])
                pend_lines.append(
                    _("· {name} ({system}/{part}/{severity})").format(
                        name=name,
                        system=system_info.get("system_name", "-"),
                        part=part_info.get("part_name", "-"),
                        severity=self._translate_severity(option["severity_level"]),
                    )
                )
            status_draw.text += _("待执行检查：\n") + "\n".join(pend_lines) + "\n"
        else:
            status_draw.text += _("待执行检查：暂无选项\n")

        if confirmed:
            confirmed_lines = []
            for cid in confirmed:
                config = game_config.config_medical_complication.get(cid)
                if config is None:
                    continue
                confirmed_lines.append(f"· {config.name}")
            if confirmed_lines:
                status_draw.text += _("已确诊并发症：\n") + "\n".join(confirmed_lines) + "\n"
        status_draw.draw()

        if self.last_check_results:
            result_draw = draw.NormalDraw()
            result_draw.width = self.width
            lines = []
            for result in self.last_check_results[-5:]:
                name = result.get("name", str(result.get("cid", "")))
                outcome = str(result.get("result", ""))
                message = result.get("message", "")
                lines.append(_("· [{outcome}] {name} —— {message}").format(outcome=self._translate_outcome(outcome), name=name, message=message))
            result_draw.text = _("最近一次检查结果：\n") + "\n".join(lines) + "\n"
            result_draw.draw()
        line_feed.draw()

    def _draw_check_menu(
        self,
        return_list: List[str],
        pending: List[Dict[str, int]],
        confirmed: List[int],
        used_checks: int,
    ) -> None:
        """绘制折叠式检查目录，允许逐级展开与勾选。

        参数:
            return_list (List[str]): 当前循环可用的返回键集合，用于注册按钮行为。
            pending (List[Dict[str, int]]): 已勾选的检查集合。
            confirmed (List[int]): 已确诊的并发症 ID 列表。
            used_checks (int): 当前累计的检查次数。

        返回:
            None: 界面绘制函数，无返回值。
        """
        if self.patient is None:
            return

        if not self._should_show_check_menu(confirmed, used_checks):
            self.menu_expanded = False
            self.expanded_systems.clear()
            self.expanded_parts.clear()
            if pending:
                tip_draw = draw.NormalDraw()
                tip_draw.width = self.width
                tip_draw.text = _("已选择 {0} 项检查，执行后即可获得新的诊断线索。\n").format(len(pending))
                tip_draw.draw()
                line_feed.draw()
            return

        toggle_label = _("[展开检查菜单]") if not self.menu_expanded else _("[收起检查菜单]")
        toggle_button = draw.LeftButton(
            toggle_label,
            "toggle_check_menu",
            max(len(toggle_label) * 2 + 4, 22),
            cmd_func=self._toggle_check_menu,
        )
        toggle_button.draw()
        return_list.append(toggle_button.return_text)

        if not self.menu_expanded:
            hint_draw = draw.NormalDraw()
            hint_draw.width = self.width
            if pending:
                hint_draw.text = _("当前已选择 {0} 项检查，若需调整请展开菜单。\n").format(len(pending))
            else:
                hint_draw.text = _("展开检查菜单以从系统 → 部位 → 并发症逐级挑选检查项目。\n")
            hint_draw.draw()
            line_feed.draw()
            return

        self._ensure_expansion_defaults()

        for system_id in sorted(self.check_catalog.keys()):
            raw_info = self.check_catalog.get(system_id)
            if not isinstance(raw_info, dict):
                continue
            system_name = str(raw_info.get("system_name", system_id))
            system_expanded = system_id in self.expanded_systems
            system_prefix = "[-]" if system_expanded else "[+]"
            system_label = f"{system_prefix} {system_name}"
            system_button = draw.LeftButton(
                system_label,
                f"sys_toggle_{system_id}",
                max(len(system_label) * 2 + 4, 26),
                cmd_func=self._toggle_system_expand,
                args=(system_id,),
            )
            system_button.draw()
            return_list.append(system_button.return_text)
            line_feed.draw()

            if not system_expanded:
                continue

            part_map = raw_info.get("parts")
            if not isinstance(part_map, dict):
                continue

            for part_id in sorted(part_map.keys()):
                part_info = part_map.get(part_id)
                if not isinstance(part_info, dict):
                    continue
                part_name = str(part_info.get("part_name", part_id))
                part_expanded = part_id in self.expanded_parts.get(system_id, set())
                part_prefix = "    [-]" if part_expanded else "    [+]"
                part_label = f"{part_prefix} {part_name}"
                part_button = draw.LeftButton(
                    part_label,
                    f"part_toggle_{system_id}_{part_id}",
                    max(len(part_label) * 2 + 4, 30),
                    cmd_func=self._toggle_part_expand,
                    args=(system_id, part_id),
                )
                part_button.draw()
                return_list.append(part_button.return_text)
                line_feed.draw()

                if not part_expanded:
                    continue

                options = part_info.get("options", [])
                for option in options:
                    if not isinstance(option, dict):
                        continue
                        # 针对并发症选项绘制勾选按钮，支持在列表中直接开关。
                    cid = int(option.get("cid", 0) or 0)
                    severity_text = self._translate_severity(int(option.get("severity_level", 0) or 0))
                    name = str(option.get("name", cid))
                    exam_method = option.get("exam_method", "-")
                    selected = any(item["cid"] == cid for item in pending)
                    checkbox = "[✔]" if selected else "[ ]"
                    option_label = f"        {checkbox} {severity_text} | {name} | {exam_method}"
                    option_button = draw.LeftButton(
                        option_label,
                        f"toggle_option_{system_id}_{part_id}_{cid}",
                        min(self.width, max(len(option_label) * 2 // 3, 44)),
                        cmd_func=self._toggle_pending_option,
                        args=(system_id, part_id, cid),
                    )
                    option_button.draw()
                    return_list.append(option_button.return_text)
                line_feed.draw()

        if pending:
            summary_draw = draw.NormalDraw()
            summary_draw.width = self.width
            summary_draw.text = _("已选择 {0} 项检查，执行时会按照列出的顺序一次性完成。\n").format(len(pending))
            summary_draw.draw()
        line_feed.draw()

    def _should_show_check_menu(self, confirmed: List[int], used_checks: int) -> bool:
        """根据会话状态判断是否展示检查菜单。

        参数:
            confirmed (List[int]): 已确诊的并发症 ID 列表。
            used_checks (int): 已使用的检查次数。

        返回:
            bool: True 代表仍需继续检查，False 则隐藏菜单。
        """
        if self.patient is None:
            return False
        if used_checks >= self.max_checks:
            return False
        target = self.target_complication_count
        if target <= 0 and getattr(self.patient, "complications", None):
            target = len(self.patient.complications)
        return target > 0 and len(confirmed) < target

    def _toggle_check_menu(self) -> None:
        """切换检查目录展开与折叠状态。

        参数:
            无。

        返回:
            None。
        """
        self.menu_expanded = not self.menu_expanded
        if not self.menu_expanded:
            self.expanded_systems.clear()
            self.expanded_parts.clear()

    def _toggle_system_expand(self, system_id: int) -> None:
        """切换指定系统的展开状态。

        参数:
            system_id (int): 需要展开或折叠的系统 ID。

        返回:
            None。
        """
        if system_id in self.expanded_systems:
            self.expanded_systems.remove(system_id)
            self.expanded_parts.pop(system_id, None)
        else:
            self.expanded_systems.add(system_id)
            self.expanded_parts.setdefault(system_id, set())

    def _toggle_part_expand(self, system_id: int, part_id: int) -> None:
        """切换指定部位的展开状态。

        参数:
            system_id (int): 所属系统 ID。
            part_id (int): 需要操作的部位 ID。

        返回:
            None。
        """
        part_set = self.expanded_parts.setdefault(system_id, set())
        if part_id in part_set:
            part_set.remove(part_id)
        else:
            part_set.add(part_id)

    def _toggle_pending_option(self, system_id: int, part_id: int, complication_id: int) -> None:
        """在折叠菜单中勾选或取消待检查项。

        参数:
            system_id (int): 并发症所属的系统 ID。
            part_id (int): 并发症所在部位 ID。
            complication_id (int): 并发症（或检查项目）唯一标识。

        返回:
            None。
        """
        if self.patient is None:
            return

        pending = self._get_pending_checks()
        option_info = self._resolve_option_info(system_id, part_id, complication_id)
        option_name = option_info.get("name") or str(complication_id)

        for index, item in enumerate(pending):
            if item["cid"] == complication_id:
                pending.pop(index)
                self.patient.metadata["player_pending_checks"] = pending
                self.feedback_text = _("已移除待检查项目：{0}").format(option_name)
                return

        used_checks = int(self.patient.metadata.get("player_used_checks", 0) or 0)
        if used_checks >= self.max_checks:
            self.feedback_text = _("检查次数已耗尽，无法继续添加。")
            return
        if len(pending) >= self.max_parallel:
            self.feedback_text = _("当前已达到可并行检查的数量上限。")
            return
        if complication_id in self._get_confirmed_complications():
            self.feedback_text = _("该并发症已确诊，无需重复检查。")
            return

        pending.append(
            {
                "cid": complication_id,
                "system_id": system_id,
                "part_id": part_id,
                "severity_level": int(option_info.get("severity_level", 0)),
            }
        )
        self.patient.metadata["player_pending_checks"] = pending
        self.feedback_text = _("已选择检查项目：{0}").format(option_name)

    def _ensure_expansion_defaults(self) -> None:
        """在首次展开菜单时提供默认展开项，减少空白界面。

        参数:
            无。

        返回:
            None。
        """
        if not self.menu_expanded or not self.check_catalog:
            return
        if not self.expanded_systems:
            first_system = next(iter(sorted(self.check_catalog.keys())), None)
            if first_system is not None:
                self.expanded_systems.add(int(first_system))
        for system_id in list(self.expanded_systems):
            info = self.check_catalog.get(system_id)
            if not isinstance(info, dict):
                self.expanded_systems.discard(system_id)
                self.expanded_parts.pop(system_id, None)
                continue
            part_map = info.get("parts")
            if not isinstance(part_map, dict) or not part_map:
                self.expanded_parts.pop(system_id, None)
                continue
            part_set = self.expanded_parts.setdefault(system_id, set())
            if not part_set:
                first_part = next(iter(sorted(part_map.keys())), None)
                if first_part is not None:
                    part_set.add(int(first_part))

    def _draw_treatment_methods(self, confirmed: List[int], used_checks: int) -> None:
        """绘制治疗摘要或建议，用于引导下一步行为。

        参数:
            confirmed (List[int]): 已确诊的并发症 ID 列表。
            used_checks (int): 当前会话已用检查次数。

        返回:
            None。
        """
        if self.patient is None:
            return

        should_show = bool(confirmed) or used_checks >= self.max_checks
        if not should_show:
            return

        summary_draw = draw.NormalDraw()
        summary_draw.width = self.width
        lines: List[str] = []

        if confirmed:
            lines.append(_("已确诊的并发症与治疗方案："))
            for cid in confirmed:
                config = game_config.config_medical_complication.get(cid)
                if config is None:
                    continue
                severity_text = self._translate_severity(int(getattr(config, "severity_level", 0) or 0))
                plan_text = getattr(config, "treatment_plan", "") or _("暂无详细治疗方案。")
                lines.append(_("· {severity} {name}").format(severity=severity_text, name=config.name))
                lines.append(_("  治疗方案：{plan}").format(plan=plan_text))
        else:
            lines.append(_("检查次数已达上限，以下为可能的异常线索："))
            suggestions = self._build_suspect_suggestions()
            if suggestions:
                lines.extend(f"  {item}" for item in suggestions)
            else:
                lines.append(_("  暂无明确线索，请考虑切换提示或交由其他医生继续诊疗。"))

        preview = medical_service.estimate_patient_treatment_summary(self.patient)
        if preview.get("success"):
            diagnose_income = preview.get("diagnose_income", 0)
            medicine_income = preview.get("predicted_medicine_income", 0)
            lines.append(
                _("预计诊疗收益：{diagnose} 龙门币 | 预估药费收益：{medicine} 龙门币").format(
                    diagnose=diagnose_income,
                    medicine=medicine_income,
                )
            )
            resources_raw = preview.get("resources")
            resources: List[Dict[str, Any]] = []
            if isinstance(resources_raw, list):
                for entry in resources_raw:
                    if isinstance(entry, dict):
                        resources.append(entry)
            if resources:
                lines.append(_("药品需求："))
                for item in resources:
                    lines.append(
                        _("  · {name} × {amount:.1f}").format(
                            name=item.get("name", "-"),
                            amount=float(item.get("amount", 0.0) or 0.0),
                        )
                    )

        summary_draw.text = "\n".join(lines) + "\n"
        summary_draw.draw()
        line_feed.draw()

    def _build_suspect_suggestions(self) -> List[str]:
        """整理检查记录，生成可能的异常建议。

        参数:
            无。

        返回:
            List[str]: 每一项为格式化后的提示文本。
        """
        if self.patient is None:
            return []
        records = self.patient.metadata.get("player_check_records", [])
        suggestions: List[str] = []
        seen: Set[Tuple[int, int]] = set()
        for record in reversed(records):
            if not isinstance(record, dict) or record.get("result") != "recheck":
                continue
            system_id = int(record.get("system_id", 0) or 0)
            part_id = int(record.get("part_id", 0) or 0)
            key = (system_id, part_id)
            if key in seen:
                continue
            seen.add(key)

            system_info = self.check_catalog.get(system_id, {}) if isinstance(self.check_catalog, dict) else {}
            system_name = "-"
            part_name = "-"
            if isinstance(system_info, dict):
                system_name = str(system_info.get("system_name", system_id))
                part_map = system_info.get("parts", {})
                if isinstance(part_map, dict):
                    part_info = part_map.get(part_id, {})
                    if isinstance(part_info, dict):
                        part_name = str(part_info.get("part_name", part_id))

            hint_severity = int(record.get("hint_severity", -1)) if record.get("hint_severity") is not None else -1
            severity_text = self._translate_severity(hint_severity) if hint_severity >= 0 else _("未知等级")
            exam_method = record.get("exam_method") or record.get("name") or "-"
            suggestions.append(
                _("· {system}/{part} 可能存在{severity}异常，建议改用其他检查（当前方法：{method}）。").format(
                    system=system_name,
                    part=part_name,
                    severity=severity_text,
                    method=exam_method,
                )
            )
        return suggestions

    def _resolve_option_info(self, system_id: int, part_id: int, complication_id: int) -> Dict[str, Any]:
        """从检查目录中解析指定选项的详细信息。

        参数:
            system_id (int): 所属系统 ID。
            part_id (int): 所属部位 ID。
            complication_id (int): 并发症或检查项目 ID。

        返回:
            Dict[str, Any]: 包含名称、严重程度等字段的描述字典。
        """
        system_info = self.check_catalog.get(system_id, {}) if isinstance(self.check_catalog, dict) else {}
        if not isinstance(system_info, dict):
            system_info = {}
        part_map = system_info.get("parts", {}) if isinstance(system_info, dict) else {}
        if not isinstance(part_map, dict):
            part_map = {}
        part_info = part_map.get(part_id, {}) if isinstance(part_map, dict) else {}
        if not isinstance(part_info, dict):
            part_info = {}
        options = part_info.get("options", []) if isinstance(part_info, dict) else []
        for option in options:
            if not isinstance(option, dict):
                continue
            if int(option.get("cid", 0) or 0) == complication_id:
                return option
        comp_config = game_config.config_medical_complication.get(complication_id)
        if comp_config is not None:
            return {
                "cid": complication_id,
                "name": comp_config.name,
                "severity_level": int(getattr(comp_config, "severity_level", 0) or 0),
            }
        return {"cid": complication_id, "name": str(complication_id), "severity_level": 0}

    def _draw_feedback(self) -> None:
        """展示底部反馈栏，用于提示最新操作结果。

        参数:
            无。

        返回:
            None。
        """
        if not self.feedback_text:
            return
        feedback_draw = draw.NormalDraw()
        feedback_draw.width = self.width
        feedback_draw.text = f"{self.feedback_text}\n"
        feedback_draw.draw()
        line_feed.draw()

    # --- 操作按钮 ---------------------------------------------------------

    def _draw_operation_buttons(
        self,
        return_list: List[str],
        pending: List[Dict[str, int]],
        confirmed: List[int],
        used_checks: int,
    ) -> None:
        """根据当前状态绘制并注册所有操作按钮。

        参数:
            return_list (List[str]): 按钮返回值集合，供主循环选择。
            pending (List[Dict[str, int]]): 已勾选待检查集合。
            confirmed (List[int]): 已确诊并发症列表。
            used_checks (int): 已使用的检查次数。

        返回:
            None。
        """
        if self.patient is None:
            return

        hint_button = draw.LeftButton(
            _("[切换提示]"),
            "toggle_hint",
            16,
            cmd_func=self._toggle_hint,
        )
        hint_button.draw()
        return_list.append(hint_button.return_text)

        if pending:
            clear_button = draw.LeftButton(
                _("[清空待检查]"),
                "clear_option",
                18,
                cmd_func=self._clear_pending,
            )
            clear_button.draw()
            return_list.append(clear_button.return_text)

        allow_execute = pending and used_checks < self.max_checks
        if allow_execute:
            execute_button = draw.LeftButton(
                _("[执行所选检查]"),
                "run_checks",
                20,
                cmd_func=self._execute_checks,
            )
            execute_button.draw()
            return_list.append(execute_button.return_text)
        else:
            disabled = draw.CenterDraw()
            disabled.width = 22
            if not pending:
                disabled.text = _("[请选择检查项目]")
            else:
                disabled.text = _("[检查次数耗尽]")
            disabled.draw()

        allow_treat = bool(confirmed) or used_checks >= self.max_checks
        if allow_treat:
            treat_button = draw.LeftButton(
                _("[开药并治疗]"),
                "commit_treat",
                18,
                cmd_func=self._commit_treatment,
            )
            treat_button.draw()
            return_list.append(treat_button.return_text)
        else:
            disabled = draw.CenterDraw()
            disabled.width = 18
            disabled.text = _("[待诊断完成]")
            disabled.draw()

        abort_button = draw.LeftButton(
            _("[提前结束诊疗并返回]"),
            "abort_session",
            28,
            cmd_func=self._handle_abort,
        )
        abort_button.draw()
        return_list.append(abort_button.return_text)

    # --- 事件处理 ---------------------------------------------------------

    def _toggle_hint(self) -> None:
        """切换当前病人的提示开关状态。

        参数:
            无。

        返回:
            None。
        """
        if self.patient is None:
            return
        new_status = not bool(self.patient.metadata.get("player_hint_enabled", False))
        self.patient.metadata["player_hint_enabled"] = new_status
        self.feedback_text = _("治病提示已{0}。\n").format(_("开启") if new_status else _("关闭"))

    def _clear_pending(self) -> None:
        """清空所有待执行检查项。

        参数:
            无。

        返回:
            None。
        """
        if self.patient is None:
            return
        self.patient.metadata["player_pending_checks"] = []
        self.feedback_text = _("已清空待执行的检查项目。")

    def _execute_checks(self) -> None:
        """调用医疗服务执行所选检查，并记录结果。

        参数:
            无。

        返回:
            None。
        """
        if self.patient is None:
            return
        pending = self._get_pending_checks()
        if not pending:
            self.feedback_text = _("请先选择需要执行的检查项目。")
            return
        result = medical_service.execute_player_diagnose_checks(pending, patient=self.patient)
        if not result.get("success"):
            self.feedback_text = _("执行检查失败：{0}").format(result.get("reason", "unknown"))
            return
        raw_results = result.get("results", [])
        normalized: List[Dict[str, object]] = []
        if isinstance(raw_results, list):
            for entry in raw_results:
                if isinstance(entry, dict):
                    normalized.append(entry)
        self.last_check_results = normalized
        self._checks_executed += 1
        summary = self._summarize_check_results(self.last_check_results)
        self.feedback_text = summary

    def _commit_treatment(self) -> None:
        """确认治疗结果，计算收益并结束会话。

        参数:
            无。

        返回:
            None。
        """
        if self.patient is None or self.player is None:
            return
        outcome = medical_service.commit_player_diagnose_session(
            self.player,
            patient=self.patient,
            apply_medicine=True,
        )
        if not outcome.get("success"):
            self.feedback_text = _("治疗操作失败：{0}").format(outcome.get("reason", "unknown"))
            return
        self.treatment_result = outcome
        self.feedback_text = _(
            "已完成诊疗，诊断收益 {diag} 龙门币，药费收益 {med} 龙门币。"
        ).format(diag=outcome.get("diagnose_income", 0), med=outcome.get("medicine_income", 0))
        self._treatment_committed = True
        self._should_close = True

    def _handle_abort(self) -> None:
        """提前终止诊疗流程，并回滚会话状态。

        参数:
            无。

        返回:
            None。
        """
        if self.patient is None or self.player is None:
            self._should_close = True
            self._abort_requested = True
            return
        medical_service.abort_player_diagnose_session(self.player, patient=self.patient)
        self.feedback_text = _("已结束本次诊疗流程。")
        self._abort_requested = True
        self._should_close = True

    # --- 会话收束 ---------------------------------------------------------

    def _finalize_session(self) -> None:
        """在面板退出时统一结算时间成本。

        参数:
            无。

        返回:
            None。
        """
        if self._treatment_committed and self.player is not None:
            duration = self._resolve_duration_minutes(30)
            self._apply_time_cost(duration)
        elif self._abort_requested and self.player is not None:
            duration = 0
            if self._checks_executed > 0:
                duration = self._resolve_duration_minutes(10)
            if duration > 0:
                self._apply_time_cost(duration)

    def _apply_time_cost(self, minutes: int) -> None:
        """将指定分钟数应用到玩家的行为时间线上。

        参数:
            minutes (int): 需要消耗的时间长度，单位为分钟。

        返回:
            None。
        """
        if minutes <= 0 or self.player is None:
            return
        instuct_judege.init_character_behavior_start_time(0, cache.game_time)
        self.player.behavior.behavior_id = constant.Behavior.WAIT
        self.player.behavior.duration = minutes
        self.player.behavior.start_time = cache.game_time
        update.game_update_flow(minutes)
        self.player.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
        self.player.behavior.duration = 1
        self.player.behavior.start_time = cache.game_time

    # --- 工具方法 ---------------------------------------------------------

    def _get_pending_checks(self) -> List[Dict[str, int]]:
        """读取并清洗 metadata 中的待执行检查列表。

        参数:
            无。

        返回:
            List[Dict[str, int]]: 标准化后的检查集合。
        """
        if self.patient is None:
            return []
        data = self.patient.metadata.get("player_pending_checks", [])
        pending: List[Dict[str, int]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            pending.append(
                {
                    "cid": int(item.get("cid", 0) or 0),
                    "system_id": int(item.get("system_id", 0) or 0),
                    "part_id": int(item.get("part_id", 0) or 0),
                    "severity_level": int(item.get("severity_level", 0) or 0),
                }
            )
        return pending

    def _get_confirmed_complications(self) -> List[int]:
        """获取当前会话已经确诊的并发症列表。

        参数:
            无。

        返回:
            List[int]: 已确诊并发症的 ID 列表。
        """
        if self.patient is None:
            return []
        return list(int(cid) for cid in self.patient.metadata.get("player_confirmed_complications", []))

    def _resolve_duration_minutes(self, base_minutes: int) -> int:
        """根据设施效率换算行为持续时间。

        参数:
            base_minutes (int): 理论基础耗时。

        返回:
            int: 实际需要消耗的分钟数。
        """
        efficiency = max(basement.calc_facility_efficiency(_MEDICAL_FACILITY_ID), 0.1)
        duration = max(int(round(base_minutes / efficiency)), 5)
        return duration

    def _build_hint_text(self) -> str:
        """根据档案线索与玩家医疗等级生成提示文本。

        参数:
            无。

        返回:
            str: 已格式化的提示字符串，若无法提供则为空串。
        """
        if self.patient is None:
            return ""
        med_level = self.player_med_level
        if med_level <= 0:
            return ""
        trace_list = self.patient.metadata.get("complication_trace", [])
        if not trace_list:
            return ""

        system_names: List[str] = []
        part_names: List[str] = []
        exam_hint: Dict[int, List[str]] = {0: [], 1: [], 2: []}
        for entry in trace_list:
            comp_config = game_config.config_medical_complication.get(entry.get("cid", entry.get("complication_id", 0)))
            system_id = int(entry.get("system_id", 0) or 0)
            part_id = int(entry.get("part_id", 0) or 0)
            system_map = game_config.config_medical_body_system_by_system.get(system_id, {})
            part_info = system_map.get(part_id)
            if part_info is not None:
                if part_info.system_name not in system_names:
                    system_names.append(part_info.system_name)
                if part_info.part_name not in part_names:
                    part_names.append(part_info.part_name)
            if comp_config is not None:
                exam_method = comp_config.exam_method
                severity = comp_config.severity_level
                if exam_method and exam_method not in exam_hint[severity]:
                    exam_hint[severity].append(exam_method)

        lines: List[str] = []
        if med_level >= 1 and system_names:
            lines.append(_("涉及系统：{0}").format("、".join(system_names)))
        if med_level >= 2 and part_names:
            lines.append(_("疑似部位：{0}").format("、".join(part_names)))
        if med_level >= 3 and exam_hint[0]:
            lines.append(_("轻症推荐检查：{0}").format("、".join(exam_hint[0])))
        if med_level >= 5 and exam_hint[1]:
            lines.append(_("中症推荐检查：{0}").format("、".join(exam_hint[1])))
        if med_level >= 7 and exam_hint[2]:
            lines.append(_("重症推荐检查：{0}").format("、".join(exam_hint[2])))
        return "\n".join(lines)

    @staticmethod
    def _translate_severity(severity_level: int) -> str:
        """将严重程度等级转换为文本描述。

        参数:
            severity_level (int): 枚举化的严重程度层级。

        返回:
            str: 对应的文本说明，若未知则返回 "-"。
        """
        mapping = {
            0: _("轻症"),
            1: _("中症"),
            2: _("重症"),
        }
        return mapping.get(int(severity_level), "-")

    @staticmethod
    def _translate_outcome(result: str) -> str:
        """将检查结果代码转换成文本。

        参数:
            result (str): 医疗服务返回的结果关键字。

        返回:
            str: 面向玩家展示的文案。
        """
        mapping = {
            "positive": _("阳性"),
            "negative": _("阴性"),
            "recheck": _("需再检"),
        }
        return mapping.get(result, result)

    @staticmethod
    def _summarize_check_results(results: List[Dict[str, object]]) -> str:
        """将原始检查结果列表整理为可阅读的段落。

        参数:
            results (List[Dict[str, object]]): 医疗服务返回的检查结果列表。

        返回:
            str: 格式化后的摘要文本。
        """
        if not results:
            return _("本次检查未获得有效结果。")
        lines: List[str] = []
        for item in results:
            name = item.get("name", str(item.get("cid", "")))
            outcome = MedicalPlayerDiagnosePanel._translate_outcome(str(item.get("result", "")))
            message = item.get("message", "")
            lines.append(_("· [{outcome}] {name} —— {message}").format(outcome=outcome, name=name, message=message))
        return "\n".join(lines)