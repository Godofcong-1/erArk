# -*- coding: UTF-8 -*-
"""玩家诊疗专用交互面板"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Mapping
from types import FunctionType

from Script.Config import game_config, normal_config
from Script.Core import cache_control, constant, game_type, get_text, flow_handle
from Script.Design import attr_calculation, basement
from Script.System.Medical_System import medical_constant, medical_player_diagnose_function
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
# 预定义换行对象，避免多处重复创建临时实例

TALK_ABILITY_ID: int = 40
""" 话术能力 ID，用于计算检查次数上限 """

def _ensure_float(value: object, default: float = 0.0) -> float:
    """将混合类型值转换为 float，避免 UI 计算时类型不确定。"""

    # 针对原生数值类型直接转换以保持精度
    if isinstance(value, (int, float)):
        return float(value)
    # 字符串需要尝试解析，否则退回默认值避免抛异常
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def start_player_diagnose_flow() -> bool:
    """启动玩家亲自诊疗流程。

    功能:
        构建并绘制玩家诊疗专用面板，结合界面返回值判断是否需要拦截原始指令。

    参数:
        无。

    返回:
        bool: 当函数返回 True 时，表示面板已经完整接管并消耗原本的行为结算。
    """

    # 构造专用面板并立即进入绘制循环，返回值用于告知外层是否继续原指令
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
        self._checks_executed: int = 0

        # 统一重置面板运行期标记，确保每次创建或切换病人时都能获得干净状态
        self._reset_runtime_flags()

        # 预先记录博士的医疗能力等级供提示判定使用
        self._calculate_player_med_level()
        # 同步根据博士的话术能力生成检查次数上限
        self._refresh_check_limit()

        # 若玩家处于可控状态，则尝试开启医疗会话并缓存病患信息
        initial_patient: Optional[medical_constant.MedicalPatient] = None
        if self.player is not None:
            initial_patient = medical_player_diagnose_function.start_player_diagnose_session(self.player)

        if initial_patient is not None:
            self._prepare_new_patient_session(initial_patient)
        else:
            # 未成功分配病人时保持面板闲置状态，便于界面直接提示
            self.patient = None
            self.session_active = False

    def _reset_runtime_flags(self) -> None:
        """重置会话运行标记，确保面板以干净状态展开。

        功能:
            清理与单次诊疗会话相关的临时数据，避免上一位病人的残留状态影响新病人。

        参数:
            无。

        返回:
            None。
        """

        # 清除界面文本与检查结果缓存，便于新会话重新绘制
        self.session_active = False
        self.patient = None
        self.feedback_text = ""
        self.last_check_results = []
        self.treatment_result = None
        self._should_close = False
        self._treatment_committed = False
        self._abort_requested = False
        self._awaiting_treatment_confirmation = False
        self.menu_expanded = False
        self.expanded_system_id = None
        self.expanded_part_id = None
        self._pending_continue_after_treatment = False
        # 重置能力快照，避免沿用上一位病人的等级数据
        self.player_med_level = 0
        self.player_talk_level = 0

        # 重置检查目录与目标计数，后续会根据具体病人重新填充
        self.check_catalog = {}
        self.target_complication_count = 0
        self.max_parallel = 1
        self.max_checks = 1

    def _calculate_player_med_level(self) -> int:
        """计算玩家当前用于诊疗提示系统的医疗能力等级。

        功能:
            综合博士本人的医疗能力与当前交互干员的辅助加成，返回诊疗提示系统所需的等级值。

        参数:
            无。

        返回:
            int: 经过辅助加成与最小值限制后的有效医疗能力等级。
        """

        if self.player is None:
            return 0

        # 读取博士的基础医疗能力
        level = int(self.player.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) or 0)

        # 如果存在交互对象，则追加一半能力值并应用最低阈值
        if self.player.target_character_id != 0 and self.player.target_character_id in cache.character_data:
            target_char = cache.character_data[self.player.target_character_id]
            level += int(target_char.ability.get(medical_constant.MEDICAL_ABILITY_ID, 0) / 2 or 0)
            level = min(8, level)
        level = max(0, level)
        
        self.player_med_level = level

        return level

    def _calculate_player_talk_level(self) -> int:
        """计算博士当前的话术能力等级，用于限定检查次数。

        功能:
            从博士角色的能力字典中读取话术能力值，并在缺失时返回 0，确保 UI 计算稳定。

        参数:
            无。

        返回:
            int: 博士当前的话术能力等级，最小值为 0。
        """

        if self.player is None:
            return 0

        # 直接读取博士的话术能力等级，缺省值视为 0
        level = int(self.player.ability.get(TALK_ABILITY_ID, 0) or 0)
        return max(0, level)

    def _refresh_check_limit(self) -> None:
        """刷新玩家诊疗检查次数的上限快照。

        功能:
            重新采样博士话术能力等级，并据此更新当前会话允许的最大检查次数，保证能力变动后立即生效。

        参数:
            无。

        返回:
            None。
        """

        # 拉取博士的话术等级并缓存，避免重复访问能力字典
        self.player_talk_level = self._calculate_player_talk_level()

        # 按照“每级话术提供两次检查”规则刷新上限，至少保留 1 次
        self.max_checks = max(1, self.player_talk_level * 2)

    @staticmethod
    def _format_quantity(value: float) -> str:
        """将数量格式化为可读文本，整数不保留小数。"""

        safe_value = max(0.0, float(value or 0.0))
        rounded = round(safe_value)
        if abs(safe_value - rounded) <= medical_constant.FLOAT_EPSILON:
            return str(int(rounded))
        return f"{safe_value:.1f}"

    def _prepare_new_patient_session(
        self,
        patient: medical_constant.MedicalPatient,
        *,
        initial_feedback: str = "",
    ) -> None:
        """按照指定病人刷新面板上下文。

        功能:
            在完成一次诊疗结算后或面板首次打开时，清理旧状态并加载新病人的检查目录、提示限制等。

        参数:
            patient (medical_constant.MedicalPatient): 即将进入玩家诊疗流程的病人对象。
            initial_feedback (str): 需要在面板底部展示的提示文本，默认为空串。

        返回:
            None。
        """

        # 每次切换病人前先清空界面与状态缓存
        self._reset_runtime_flags()

        self.patient = patient
        self.session_active = True

        # 重新计算医疗能力等级供提示系统使用
        self._calculate_player_med_level()
        # 根据最新的话术能力刷新检查次数上限
        self._refresh_check_limit()

        # 根据病人实际并发症数量设定并行检查上限
        complications = getattr(patient, "complications", []) or []
        self.target_complication_count = len(complications)
        self.max_parallel = max(1, self.target_complication_count or 1)

        # 构建本次会话的检查目录
        self.check_catalog = medical_player_diagnose_function.build_player_check_catalog(patient)

        if initial_feedback:
            self.feedback_text = initial_feedback

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

        # 持续渲染界面直至流程被明确关闭
        while not self._should_close:
            # 每轮绘制前刷新一次检查上限，确保话术能力变化即时生效
            self._refresh_check_limit()
            title_draw = draw.TitleLineDraw(_("医疗诊疗"), self.width)
            title_draw.draw()
            return_list: List[str] = []

            pending_checks = self._get_pending_checks()
            confirmed_complications = self._get_confirmed_complications()
            used_checks = 0
            if self.patient is not None:
                used_checks = int(getattr(self.patient, "player_used_checks", 0) or 0)

            # 顶部帮助文本为玩家提供操作指引与提示系统说明
            hint_draw = draw.NormalDraw()
            hint_draw.width = self.width
            hint_draw.text = _("○展开检查菜单以从系统 → 部位 → 并发症逐级挑选检查项目，项目格式为：病症等级|怀疑病症名|检查方式。\n")
            hint_draw.text += _("○患者愿意进行的检查次数与博士的话术能力等级有关，等级越高可尝试次数就越高。\n")
            hint_draw.text += _("○开启治疗提示后，会根据博士的医疗能力等级（+交互干员的一半）来高亮显示正确的患病系统、部位、症状等，能力越高显示越具体。\n")
            hint_draw.draw()

            # 依次输出提示、病历、检查状态及检查目录
            self._draw_hint_section(return_list)
            self._draw_patient_overview()
            self._draw_check_status(pending_checks, confirmed_complications, used_checks)
            self._draw_check_menu(return_list, pending_checks, confirmed_complications, used_checks)
            self._draw_treatment_methods(confirmed_complications, used_checks)

            # 绘制反馈栏
            self._draw_feedback()

            # 底部交互按钮决定下一步行为
            self._draw_operation_buttons(return_list, pending_checks, confirmed_complications, used_checks)
            if not return_list:
                # 至少提供一个默认返回项避免阻塞
                default_back = draw.CenterButton(_("[返回]"), _("返回"), self.width, cmd_func=self._handle_abort)
                default_back.draw()
                return_list.append(default_back.return_text)

            # 主循环等待玩家选择具体操作，绑定指令字符串控制逻辑
            choice = flow_handle.askfor_all(return_list)
            if choice == _("返回"):
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

        severity_name = getattr(self.patient, "severity_name", "")
        if not severity_name:
            config = game_config.config_medical_severity.get(self.patient.severity_level)
            severity_name = config.name if config else _("未知病情")

        race_name = _("未知种族")
        race_config = game_config.config_race.get(self.patient.race_id)
        if race_config is not None:
            race_name = race_config.name

        info_draw.text = _(
            "患者编号：{pid} | 病情：{severity} | 年龄：{age} 岁 | 种族：{race}\n"
        ).format(
            pid=self.patient.patient_id,
            severity=severity_name,
            age=self.patient.age,
            race=race_name,
        )

        complaint_lines: List[str] = []
        trace_list = getattr(self.patient, "complication_trace", [])
        for index, entry in enumerate(trace_list, start=1):
            comp_config = game_config.config_medical_complication.get(entry.get("cid", entry.get("complication_id", 0)))
            if comp_config is None:
                continue
            statement = comp_config.patient_statement_clear
            if self.patient.personality_type == medical_constant.MedicalPatientPersonality.IRRATIONAL:
                statement = comp_config.patient_statement_vague
            appearance_text = comp_config.appearance_indicator or _("无可见异常")
            # 每条症状记录包含外观观察与病人自述，构成病例文本
            complaint_lines.append(
                _("· 症状记录 {index}\n  外观观察：{appearance}\n  病人自述：{statement}").format(
                    index=index,
                    appearance=appearance_text,
                    statement=statement,
                )
            )

        if complaint_lines:
            info_draw.text += "\n" + "\n".join(complaint_lines) + "\n"
        info_draw.draw()
        line_feed.draw()

    def _draw_hint_section(self, return_list: List[str]) -> None:
        """绘制诊疗提示状态及提示按钮。

        参数:
            return_list (List[str]): 当前循环的按钮返回值注册表。

        返回:
            None: 状态展示性函数。
        """
        if self.patient is None:
            return
        # 拉取系统设置中的提示等级，并根据玩家能力进行合法性校验
        hint_value, _allowed_indices, option_list = self._fetch_hint_setting_context(enforce_bounds=True)
        if option_list and 0 <= hint_value < len(option_list):
            status_text = option_list[hint_value]
        else:
            status_text = _("未配置")
        status_label = _("○治病提示：{status}").format(status=status_text)
        advice_draw = draw.NormalDraw()
        advice_draw.width = self.width
        advice_draw.text = status_label
        advice_draw.draw()

        toggle_text = _("[切换提示]")
        hint_button = draw.CenterButton(
            toggle_text,
            _("切换提示"),
            len(toggle_text) * 2 + 4,
            cmd_func=self._toggle_hint,
        )
        hint_button.draw()
        # 记录按钮返回值以便主循环识别
        return_list.append(hint_button.return_text)

        line_feed.draw()
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
        status_draw.text = _("患者愿意进行的检查次数：{used}/{limit}").format(
            used=used_checks,
            limit=self.max_checks,
        )
        # 如果没有到上限，则显示本次已选项数
        if used_checks < self.max_checks:
            status_draw.text += _("（本次已选 {selected}/{max_parallel} 项）").format(
                selected=len(pending),
                max_parallel=self.max_parallel,
            )
        status_draw.text += "\n"
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
                exam_method = comp_config.exam_method if comp_config and hasattr(comp_config, "exam_method") else "-"
                system_name = system_info.get("system_name", "-")
                part_name = part_info.get("part_name", "-")
                severity_text = self._translate_severity(option["severity_level"])
                # 组装成“系统-部位-严重程度”的复合展示字符串
                pend_lines.append(
                    _("◆ 怀疑 {name}（{system} - {part} - {severity}），进行检查：{exam_method}").format(
                        name=name,
                        system=system_name,
                        part=part_name,
                        severity=severity_text,
                        exam_method=exam_method,
                    )
                )
            status_draw.text += _("待执行检查：\n") + "\n".join(pend_lines) + "\n"
        # else:
        #     status_draw.text += _("待执行检查：暂无选项\n")

        status_draw.draw()

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

        highlight_systems, highlight_parts, highlight_options = self._resolve_hint_highlight_targets()

        if not self._should_show_check_menu(confirmed, used_checks):
            self.menu_expanded = False
            self.expanded_system_id = None
            self.expanded_part_id = None
            if pending:
                tip_draw = draw.NormalDraw()
                tip_draw.width = self.width
                tip_draw.text = _("已选择 {0} 项检查，执行后即可获得新的诊断线索。\n").format(len(pending))
                tip_draw.draw()
                line_feed.draw()
            return

        toggle_label = _(" [展开检查菜单]") if not self.menu_expanded else _(" [收起检查菜单]")
        toggle_button = draw.LeftButton(
            toggle_label,
            _("切换检查菜单"),
            max(len(toggle_label) * 2 + 4, 22),
            cmd_func=self._toggle_check_menu,
        )
        toggle_button.draw()
        return_list.append(toggle_button.return_text)
        line_feed.draw()

        # 未展开时直接返回
        if not self.menu_expanded:
            line_feed.draw()
            return

        # 展开系统列表
        for system_id in sorted(self.check_catalog.keys()):
            raw_info = self.check_catalog.get(system_id)
            if not isinstance(raw_info, dict):
                continue
            system_name = str(raw_info.get("system_name", system_id))
            system_expanded = system_id == self.expanded_system_id
            system_prefix = "   [-]" if system_expanded else "   [+]"
            system_label = f"{system_prefix} {system_name}"
            system_style = "gold_enrod" if system_id in highlight_systems else "standard"
            # 系统按钮支持展开/折叠，并附带提示高亮颜色
            system_button = draw.LeftButton(
                system_label,
                system_name,
                max(len(system_label) * 2 + 4, 26),
                normal_style=system_style,
                cmd_func=self._toggle_system_expand,
                args=(system_id,),
            )
            system_button.draw()
            return_list.append(system_button.return_text)
            line_feed.draw()

            if not system_expanded:
                continue

            # 展开部位列表
            part_map = raw_info.get("parts")
            if not isinstance(part_map, dict):
                continue

            for part_id in sorted(part_map.keys()):
                part_info = part_map.get(part_id)
                if not isinstance(part_info, dict):
                    continue
                gender_limit = int(part_info.get("gender_limit", 2))
                if gender_limit == 0:
                    continue
                part_name = str(part_info.get("part_name", part_id))
                part_expanded = system_expanded and part_id == self.expanded_part_id
                part_prefix = "     [-]" if part_expanded else "     [+]"
                part_label = f"{part_prefix} {part_name}"
                part_style = "gold_enrod" if (system_id, part_id) in highlight_parts else "standard"
                # 部位按钮与系统用同一机制控制展开状态
                part_button = draw.LeftButton(
                    part_label,
                    part_name,
                    max(len(part_label) * 2 + 4, 30),
                    normal_style=part_style,
                    cmd_func=self._toggle_part_expand,
                    args=(system_id, part_id),
                )
                part_button.draw()
                return_list.append(part_button.return_text)
                line_feed.draw()

                if not part_expanded:
                    continue

                # 展开并发症选项列表
                options = part_info.get("options", [])
                for option in options:
                    if not isinstance(option, dict):
                        continue
                    # 针对并发症选项绘制勾选按钮，支持在列表中直接开关。
                    cid = int(option.get("cid", 0) or 0)
                    severity_text = self._translate_severity(int(option.get("severity_level", 0) or 0))
                    name = str(option.get("name", cid))
                    name = attr_calculation.pad_display_width(name, 38)
                    exam_method = option.get("exam_method", "-")
                    selected = any(item["cid"] == cid for item in pending)
                    checkbox = "[✔]" if selected else "[  ]"
                    option_label = f"        {checkbox} {severity_text} | {name} | {exam_method}"
                    option_style = "gold_enrod" if cid in highlight_options else "standard"
                    # 选项按钮被点击后调用 _toggle_pending_option 处理选/取消逻辑
                    option_button = draw.LeftButton(
                        option_label,
                        name,
                        self.width,
                        normal_style=option_style,
                        cmd_func=self._toggle_pending_option,
                        args=(system_id, part_id, cid),
                    )
                    option_button.draw()
                    return_list.append(option_button.return_text)
                    line_feed.draw()

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
            # 检查次数耗尽后强制关闭检查菜单
            return False
        target = self.target_complication_count
        if target <= 0 and getattr(self.patient, "complications", None):
            target = len(self.patient.complications)
        # 仅在尚有未确诊并发症时继续显示目录
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
            # 折叠时同步清空展开状态，避免下次展开时状态错乱
            self.expanded_system_id = None
            self.expanded_part_id = None

    def _toggle_system_expand(self, system_id: int) -> None:
        """切换指定系统的展开状态。

        参数:
            system_id (int): 需要展开或折叠的系统 ID。

        返回:
            None。
        """
        if self.expanded_system_id == system_id:
            # 重复点击同一系统时折叠，并同时重置部位展开状态
            self.expanded_system_id = None
            self.expanded_part_id = None
        else:
            self.expanded_system_id = system_id
            self.expanded_part_id = None

    def _toggle_part_expand(self, system_id: int, part_id: int) -> None:
        """切换指定部位的展开状态。

        参数:
            system_id (int): 所属系统 ID。
            part_id (int): 需要操作的部位 ID。

        返回:
            None。
        """
        if self.expanded_system_id != system_id:
            # 若切换了系统，需要同时更新系统和部位的展开记录
            self.expanded_system_id = system_id
            self.expanded_part_id = part_id
            return
        if self.expanded_part_id == part_id:
            self.expanded_part_id = None
        else:
            self.expanded_part_id = part_id

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

        for index, item in enumerate(pending):
            # 已勾选则取消
            if item["cid"] == complication_id:
                pending.pop(index)
                self.patient.player_pending_checks = pending
                return

        used_checks = int(getattr(self.patient, "player_used_checks", 0) or 0)
        # 检查次数已耗尽
        if used_checks >= self.max_checks:
            return
        # 并行检查数量已达上限
        if len(pending) >= self.max_parallel:
            return
        # 该并发症已确诊
        if complication_id in self._get_confirmed_complications():
            return

        # 所有约束满足后将勾选项写回患者结构，保持会话状态一致
        pending.append(
            {
                "cid": complication_id,
                "system_id": system_id,
                "part_id": part_id,
                "severity_level": int(option_info.get("severity_level", 0)),
            }
        )
        self.patient.player_pending_checks = pending

    def _resolve_inventory_snapshot(self) -> Dict[int, float]:
        """获取当前医疗仓库的药品库存快照。

        返回:
            Dict[int, float]: 资源 ID 到库存数量的映射副本。
        """

        rhodes_island = getattr(cache, "rhodes_island", None)
        if rhodes_island is None:
            return {}
        inventory = getattr(rhodes_island, "materials_resouce", None)
        if not isinstance(inventory, dict):
            return {}

        snapshot: Dict[int, float] = {}
        for resource_id, value in inventory.items():
            try:
                snapshot[int(resource_id)] = float(value or 0.0)
            except (TypeError, ValueError):
                continue
        return snapshot

    def _calculate_shortage(
        self,
        resource_id: int,
        required_amount: float,
        inventory_snapshot: Mapping[int, float],
    ) -> float:
        """计算在当前库存下特定资源的缺口数量。"""

        if required_amount <= medical_constant.FLOAT_EPSILON:
            return 0.0
        available_amount = float(inventory_snapshot.get(resource_id, 0.0) or 0.0)
        shortage = required_amount - available_amount
        if shortage <= medical_constant.FLOAT_EPSILON:
            return 0.0
        return shortage

    def _collect_patient_medicine_shortages(self, inventory_snapshot: Mapping[int, float]) -> List[str]:
        """针对当前病人整理药品缺口描述列表。"""

        if self.patient is None:
            return []

        requirement_map = getattr(self.patient, "need_resources", {}) or {}
        shortage_lines: List[str] = []
        for resource_key, amount in requirement_map.items():
            try:
                resource_id = int(resource_key)
            except (TypeError, ValueError):
                continue
            required_amount = float(amount or 0.0)
            if required_amount <= medical_constant.FLOAT_EPSILON:
                continue
            shortage_amount = self._calculate_shortage(resource_id, required_amount, inventory_snapshot)
            if shortage_amount <= medical_constant.FLOAT_EPSILON:
                continue
            resource_config = game_config.config_resouce.get(resource_id)
            resource_name = getattr(resource_config, "name", str(resource_id)) if resource_config else str(resource_id)
            shortage_text = self._format_quantity(shortage_amount)
            stock_text = self._format_quantity(float(inventory_snapshot.get(resource_id, 0.0) or 0.0))
            shortage_lines.append(
                _("· {name} 缺口 {amount} 单位，当前库存 {stock} 单位。").format(
                    name=resource_name,
                    amount=shortage_text,
                    stock=stock_text,
                )
            )
        return shortage_lines

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

        # 显示最近的检查结果
        if self.last_check_results:
            header_draw = draw.NormalDraw()
            header_draw.width = self.width
            header_draw.text = _("检查报告一览：\n")
            header_draw.draw()

            style_map = {
                "positive": "warning",
                "negative": "green",
                "recheck": "pale_cerulean",
            }
            for result in self.last_check_results:
                name = result.get("name", str(result.get("cid", "")))
                result_key = str(result.get("result", "") or "")
                outcome_text = self._translate_outcome(result_key)
                outcome_text = attr_calculation.pad_display_width(outcome_text, 6, align="center")
                message = result.get("message", "")

                prefix_draw = draw.NormalDraw()
                prefix_draw.text = "·("
                prefix_draw.draw()

                outcome_draw = draw.NormalDraw()
                outcome_draw.text = outcome_text
                outcome_draw.style = style_map.get(result_key, "standard")
                outcome_draw.draw()

                suffix_draw = draw.NormalDraw()
                suffix_draw.width = self.width
                suffix_draw.text = _(") 怀疑 {name}，检查结果：{message}\n").format(name=name, message=message)
                suffix_draw.draw()

            line_feed.draw()

        should_show = bool(confirmed) or used_checks >= self.max_checks
        if not should_show:
            return

        summary_draw = draw.NormalDraw()
        summary_draw.width = self.width
        lines: List[str] = []

        # 计算未确诊并发症数量及调整比例
        actual_complications: Set[int] = set() # 真实并发症 ID 集合
        if getattr(self.patient, "complications", None):
            actual_complications = {int(cid) for cid in self.patient.complications if cid}
        confirmed_set: Set[int] = {int(cid) for cid in confirmed} # 已确诊并发症 ID 集合
        missing_complications: Set[int] = set() # 未确诊并发症 ID 集合
        if actual_complications:
            missing_complications = actual_complications - confirmed_set

        # 根据确诊进度调整预估收益与药品需求
        adjust_ratio = 1.0
        total_complication_count = len(actual_complications)
        if total_complication_count > 0 and missing_complications:
            adjust_ratio = (
                len(confirmed_set) + 0.5 * len(missing_complications)
            ) / total_complication_count

        # 显示确诊或建议
        if confirmed:
            lines.append(_("已确诊的并发症与治疗方案："))
            for cid in confirmed:
                config = game_config.config_medical_complication.get(cid)
                if config is None:
                    continue
                severity_text = self._translate_severity(int(getattr(config, "severity_level", 0) or 0))
                plan_text = getattr(config, "treatment_plan", "") or _("暂无详细治疗方案。")
                lines.append(_("·({severity}){name}").format(severity=severity_text, name=config.name))
                lines.append(_("  治疗方案：{plan}").format(plan=plan_text))
        else:
            lines.append(_("检查次数已达上限，以下为可能的异常线索："))
            suggestions = self._build_suspect_suggestions()
            if suggestions:
                lines.extend(f"  {item}" for item in suggestions)
            else:
                lines.append(_("  暂无明确线索，请考虑切换提示或交由其他医生继续诊疗。"))

        lines.append("\n")

        preview = medical_player_diagnose_function.estimate_patient_treatment_summary(self.patient)
        if preview.get("success"):
            # 成功获取预估信息，结合确诊进度动态调整收益与耗材数量
            diagnose_income = int(round(_ensure_float(preview.get("diagnose_income", 0), 0.0)))
            base_medicine_income = _ensure_float(preview.get("predicted_medicine_income", 0), 0.0)
            display_medicine_income_value = base_medicine_income * adjust_ratio if adjust_ratio != 1.0 else base_medicine_income
            display_medicine_income = int(round(display_medicine_income_value))
            lines.append(
                _("预计诊疗收益：{diagnose} 龙门币 | 预估药费收益：{medicine} 龙门币").format(
                    diagnose=diagnose_income,
                    medicine=display_medicine_income,
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
                inventory_snapshot = self._resolve_inventory_snapshot()
                for item in resources:
                    base_amount = float(item.get("amount", 0.0) or 0.0)
                    display_amount = base_amount * adjust_ratio if adjust_ratio != 1.0 else base_amount
                    try:
                        resource_id = int(item.get("resource_id", 0) or 0)
                    except (TypeError, ValueError):
                        resource_id = 0
                    formatted_amount = self._format_quantity(display_amount)
                    shortage_amount = self._calculate_shortage(resource_id, display_amount, inventory_snapshot)
                    if shortage_amount > medical_constant.FLOAT_EPSILON:
                        shortage_text = self._format_quantity(shortage_amount)
                        stock_text = self._format_quantity(float(inventory_snapshot.get(resource_id, 0.0) or 0.0))
                        lines.append(
                            _("  · {name} × {amount}（缺口 {shortage} 单位，库存 {stock} 单位）").format(
                                name=item.get("name", "-"),
                                amount=formatted_amount,
                                shortage=shortage_text,
                                stock=stock_text,
                            )
                        )
                    else:
                        lines.append(
                            _("  · {name} × {amount}").format(
                                name=item.get("name", "-"),
                                amount=formatted_amount,
                            )
                        )
                if missing_complications:
                    lines.append(
                        _("  * 未确诊 {count} 项并发症，相关药品需求按 50% 计入。").format(
                            count=len(missing_complications)
                        )
                    )
            elif missing_complications:
                lines.append(
                    _("未确诊 {count} 项并发症，相关药品需求按 50% 计入。").format(
                        count=len(missing_complications)
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
        records = getattr(self.patient, "player_check_records", [])
        suggestions: List[str] = []
        seen: Set[Tuple[int, int]] = set()
        # 逆序遍历记录，以便优先展示最新的再检建议
        for record in reversed(records):
            if not isinstance(record, dict) or record.get("result") != "recheck":
                continue
            # 使用系统 ID + 部位 ID 作为合并键，避免重复提示同一位置
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
            suggestions.append(
                _("· {system}/{part} 可能存在{severity}异常，建议改用其他检查。").format(
                    system=system_name,
                    part=part_name,
                    severity=severity_text,
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
            # 当菜单缺失目标项目时，退回配置表提供最小展示信息
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
        line_feed.draw()
        feedback_draw = draw.WaitDraw()
        feedback_draw.text = self.feedback_text + "\n"
        feedback_draw.style = "gold_enrod"
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

        if self._awaiting_treatment_confirmation:
            confirm_text = _("[确认就这样治疗]")
            confirm_button = draw.CenterButton(
                confirm_text,
                confirm_text,
                self.width // 4,
                cmd_func=self._confirm_treatment_after_prompt,
            )
            confirm_button.draw()
            return_list.append(confirm_button.return_text)

            cancel_text = _("[返回继续检查]")
            cancel_button = draw.CenterButton(
                cancel_text,
                cancel_text,
                self.width // 4,
                cmd_func=self._cancel_treatment_confirmation,
            )
            cancel_button.draw()
            return_list.append(cancel_button.return_text)
            return

        allow_execute = pending and used_checks < self.max_checks
        if allow_execute:
            execute_button = draw.CenterButton(
                _("[执行所选检查]"),
                _("执行所选检查"),
                self.width // 4,
                cmd_func=self._execute_checks,
            )
            execute_button.draw()
            return_list.append(execute_button.return_text)

        if pending:
            clear_button = draw.CenterButton(
                _("[清空已选待检项]"),
                _("清空已选待检项"),
                self.width // 4,
                cmd_func=self._clear_pending,
            )
            clear_button.draw()
            # 记录按钮返回值确保事件循环能够捕获指令
            return_list.append(clear_button.return_text)

        # 当至少确诊一项或已耗尽检查次数时允许开药流程
        allow_treat = bool(confirmed) or used_checks >= self.max_checks
        if allow_treat:
            treat_button = draw.CenterButton(
                _("[开药并结束诊疗]"),
                _("开药并结束诊疗"),
                self.width // 4,
                cmd_func=self._handle_treatment_request,
                args=(False,),
            )
            treat_button.draw()
            return_list.append(treat_button.return_text)

            continue_button = draw.CenterButton(
                _("[开药并接诊下一位]"),
                _("开药并接诊下一位"),
                self.width // 4,
                cmd_func=self._handle_treatment_request,
                args=(True,),
            )
            continue_button.draw()
            return_list.append(continue_button.return_text)

        # 仅在尚未消耗检查次数时允许无损退出
        if used_checks == 0:
            abort_button = draw.CenterButton(
                _("[提前结束诊疗并返回]"),
                _("提前结束诊疗并返回"),
                self.width // 4,
                cmd_func=self._handle_abort,
            )
            abort_button.draw()
            return_list.append(abort_button.return_text)

    # --- 事件处理 ---------------------------------------------------------

    def _handle_treatment_request(self, continue_after: bool) -> None:
        """根据需求执行治疗结算或请求确认。

        功能:
            统一处理“结束诊疗”与“结束并继续接诊”两种按钮行为，先评估是否需要二次确认，
            随后根据玩家选择继续或终止会话。

        参数:
            continue_after (bool): 为 True 时在结算完成后尝试接诊下一位病人。

        返回:
            None。
        """

        if self.patient is None or self.player is None:
            self._pending_continue_after_treatment = False
            return

        self._pending_continue_after_treatment = continue_after

        # 计算当前病人的实际并发症集合，用于判断是否存在未确诊条目
        actual_complications: Set[int] = set()
        if getattr(self.patient, "complications", None):
            actual_complications = {int(cid) for cid in self.patient.complications if cid}

        confirmed_set: Set[int] = {int(cid) for cid in self._get_confirmed_complications()}

        if not actual_complications and self.target_complication_count:
            missing_count = max(self.target_complication_count - len(confirmed_set), 0)
        else:
            missing_count = len(actual_complications - confirmed_set)

        used_checks = int(getattr(self.patient, "player_used_checks", 0) or 0)
        remaining_checks = max(self.max_checks - used_checks, 0)

        if (
            not self._awaiting_treatment_confirmation
            and missing_count > 0
            and remaining_checks > 0
        ):
            # 需要二次确认时直接提示玩家并等待下一步指令
            self._awaiting_treatment_confirmation = True
            self.feedback_text = _(
                "仍有 {count} 项疑似并发症尚未确诊，确认要直接结束治疗吗？"
            ).format(count=missing_count)
            return

        # 已确认或无需确认时执行结算
        self._awaiting_treatment_confirmation = False
        self._execute_treatment_commit(continue_after=continue_after)

    def _confirm_treatment_after_prompt(self) -> None:
        """确认在存在未确诊项时仍然继续治疗。

        参数:
            无。

        返回:
            None。
        """

        if self.patient is None or self.player is None:
            return
        self._awaiting_treatment_confirmation = False
        self._execute_treatment_commit(continue_after=self._pending_continue_after_treatment)

    def _cancel_treatment_confirmation(self) -> None:
        """取消强制治疗提示并返回继续检查。

        参数:
            无。

        返回:
            None。
        """

        self._awaiting_treatment_confirmation = False
        self._pending_continue_after_treatment = False
        self.feedback_text = _("已返回诊疗流程，可以继续安排检查。")

    def _execute_treatment_commit(self, *, continue_after: bool) -> None:
        """执行治疗结算并根据后续动作刷新界面。

        参数:
            continue_after (bool): 为 True 时在完成结算后继续接诊；否则直接结束面板。

        返回:
            None。
        """

        if self.patient is None or self.player is None:
            self._pending_continue_after_treatment = False
            return

        # 调用医疗服务层提交诊疗结果
        outcome = medical_player_diagnose_function.commit_player_diagnose_session(
            self.player,
            patient=self.patient,
        )
        # 结算失败时记录原因并返回
        if not outcome.get("success"):
            self.feedback_text = _("治疗操作失败：{0}").format(outcome.get("reason", "unknown"))
            self._pending_continue_after_treatment = False
            return

        # 记录治疗结果并提示收益
        self.treatment_result = outcome
        self._treatment_committed = True

        base_message = _(
            "已完成诊疗，诊断收益 {diag} 龙门币，药费收益 {med} 龙门币。"
        ).format(diag=outcome.get("diagnose_income", 0), med=outcome.get("medicine_income", 0))

        if not outcome.get("medicine_success"):
            inventory_snapshot = self._resolve_inventory_snapshot()
            shortage_lines = self._collect_patient_medicine_shortages(inventory_snapshot)
            if shortage_lines:
                shortage_notice = "\n" + _("当前仍缺少以下药品：") + "\n" + "\n".join(shortage_lines)
            else:
                shortage_notice = "\n" + _("药品库存不足，请补充后再试。")
            base_message += shortage_notice

        next_patient: Optional[medical_constant.MedicalPatient] = None
        if continue_after and self.player is not None:
            next_patient = medical_player_diagnose_function.start_player_diagnose_session(self.player)

        self._pending_continue_after_treatment = False

        if continue_after and next_patient is not None:
            continuation_message = base_message + _(" 已为博士安排下一位病人，请继续诊疗。")
            self._prepare_new_patient_session(next_patient, initial_feedback=continuation_message)
            return

        if continue_after and next_patient is None:
            self.feedback_text = base_message + _(" 当前暂无其他病人需要诊疗，流程已结束。")
        else:
            self.feedback_text = base_message

        self._should_close = True
        self._draw_feedback()

    def _toggle_hint(self) -> None:
        """切换治病提示状态并持久化到全局设置。"""

        # 拉取当前提示设置上下文，确保配置已按能力限制校正
        current_value, allowed_indices, option_list = self._fetch_hint_setting_context(enforce_bounds=True)

        # 当未配置提示选项时直接反馈并退出
        if not option_list:
            self.feedback_text = _("当前版本未配置诊疗提示选项，无法切换。")
            return

        # 当博士能力不足以解锁更高等级时提醒玩家
        if len(allowed_indices) <= 1:
            self.feedback_text = _("博士当前的医疗能力等级不足以启用额外的诊疗提示。")
            return

        # 根据能力范围内的索引循环切换提示等级
        try:
            position = allowed_indices.index(current_value)
        except ValueError:
            position = 0
        next_value = allowed_indices[(position + 1) % len(allowed_indices)]

        # 写回系统设置并输出提示语，便于玩家确认当前等级
        base_setting = getattr(cache.all_system_setting, "base_setting", {})
        if not isinstance(base_setting, dict):
            base_setting = {}
            setattr(cache.all_system_setting, "base_setting", base_setting)
        base_setting[12] = next_value

        # if 0 <= next_value < len(option_list):
        #     self.feedback_text = _("治病提示已调整为：{0}").format(option_list[next_value])
        # else:
        #     self.feedback_text = _("治病提示设置已更新。")

    def _clear_pending(self) -> None:
        """清空所有待执行检查项。"""

        if self.patient is None:
            return
        self.patient.player_pending_checks = []

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
        # 没有选项时直接返回
        if not pending:
            return
        result = medical_player_diagnose_function.execute_player_diagnose_checks(pending, patient=self.patient)
        # 检查执行失败时记录原因并返回
        if not result.get("success"):
            self.feedback_text = _("执行检查失败：{0}").format(result.get("reason", "unknown"))
            return
        raw_results = result.get("results", [])
        normalized: List[Dict[str, object]] = []
        if isinstance(raw_results, list):
            for entry in raw_results:
                if isinstance(entry, dict):
                    # 将返回结果统一成字典列表，过滤掉异常结构
                    normalized.append(entry)
        self.last_check_results.extend(normalized)
        self._checks_executed += 1
        # 因为增加了颜色显示，暂时注释掉文本汇总功能
        # summary = self._summarize_check_results(self.last_check_results)
        # self.feedback_text = summary
        # 如果检查列表为展开状态，则调用一次折叠以刷新界面
        if self.menu_expanded:
            self._toggle_check_menu()

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
        self._awaiting_treatment_confirmation = False
        # 通知医疗服务层撤销会话状态，防止残留数据影响后续诊疗
        medical_player_diagnose_function.abort_player_diagnose_session(self.player, patient=self.patient)
        self.feedback_text = _("已结束本次诊疗流程。")
        self._draw_feedback()
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
        # 基础耗时5分钟
        duration = 5
        # 按检查次数累计耗时，每次检查+10分钟
        if self._checks_executed > 0 and self.player is not None:
            duration = self._checks_executed * 10
        from Script.Design.handle_instruct import chara_handle_instruct_common_settle
        # 如果中途退出，则进行等待结算
        if self._abort_requested:
            chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration=duration, force_taget_wait=True)
        # 正常情况下直接结算
        else:
            chara_handle_instruct_common_settle(constant.Behavior.CURE_PATIENT, duration=duration, force_taget_wait=False)

    # --- 工具方法 ---------------------------------------------------------

    def _get_pending_checks(self) -> List[Dict[str, int]]:
        """读取并清洗患者结构中的待执行检查列表。

        参数:
            无。

        返回:
            List[Dict[str, int]]: 标准化后的检查集合。
        """
        if self.patient is None:
            return []
        data = getattr(self.patient, "player_pending_checks", [])
        pending: List[Dict[str, int]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            # 将可能携带的字符串或 None 统一转成 int，确保后续计算稳定
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
        # 数据可能以字符串存储，因此统一转为 int
        return list(int(cid) for cid in getattr(self.patient, "player_confirmed_complications", []))

    def _resolve_duration_minutes(self, base_minutes: int) -> int:
        """根据设施效率换算行为持续时间。

        参数:
            base_minutes (int): 理论基础耗时。

        返回:
            int: 实际需要消耗的分钟数。
        """
        efficiency = max(basement.calc_facility_efficiency(medical_constant.MEDICAL_FACILITY_ID), 0.1)
        # 将设施效率映射为耗时缩放，限定最低效率避免除零
        duration = max(int(round(base_minutes / efficiency)), 5)
        return duration

    def _resolve_hint_allowed_indices(self, total_options: int) -> List[int]:
        """根据玩家医疗等级推导可使用的提示等级索引集合。

        功能:
            结合博士当前的医疗能力等级与配置中可选的提示项数量，生成一个按升序排列的合法索引列表，
            用于限制玩家切换提示时的可选范围。

        参数:
            total_options (int): 系统设置中“诊疗病人提示”条目的可选项数量。

        返回:
            List[int]: 在当前能力等级下允许选择的提示索引集合，至少包含关闭选项 0。
        """

        # 当选项列表为空时直接返回关闭选项，避免后续出现空集合
        if total_options <= 0:
            return [0]

        # 默认始终允许关闭选项（索引 0），其他选项需满足能力阈值
        allowed_indices: Set[int] = {0}
        unlock_thresholds: Tuple[Tuple[int, int], ...] = (
            (1, 1),
            (2, 2),
            (3, 3),
            (5, 4),
            (7, 5),
        )

        # 逐条比对能力阈值，只有在医疗能力达标且选项存在时才加入可选集合
        for required_level, option_index in unlock_thresholds:
            if option_index >= total_options:
                continue
            if self.player_med_level >= required_level:
                allowed_indices.add(option_index)

        return sorted(allowed_indices)

    def _fetch_hint_setting_context(self, *, enforce_bounds: bool) -> Tuple[int, List[int], List[str]]:
        """拉取提示设置上下文并按需应用能力限制。

        功能:
            读取系统设置中的提示等级，刷新博士当下的医疗能力等级，并依据能力阈值返回合法的提示索引集合。
            当 enforce_bounds 为 True 时，会在能力不足时自动回退到可用的最高等级。

        参数:
            enforce_bounds (bool): 是否在能力不足时立即修正系统设置中的提示等级。

        返回:
            Tuple[int, List[int], List[str]]: (当前提示索引, 合法索引列表, 系统设置选项文本列表)。
        """

        # 读取配置中的提示选项列表，未配置时以空列表返回
        option_list = game_config.config_system_setting_option.get(12, [])
        total_options = len(option_list)

        # 重新计算博士的医疗能力等级，处理过程中能力变动带来的影响
        self._calculate_player_med_level()

        # 根据医疗能力计算允许选择的提示索引集合
        allowed_indices = self._resolve_hint_allowed_indices(total_options)
        if not allowed_indices:
            allowed_indices = [0]

        # 取得系统设置字典，若不存在则初始化为空字典
        base_setting = getattr(cache.all_system_setting, "base_setting", {})
        if not isinstance(base_setting, dict):
            base_setting = {}
            setattr(cache.all_system_setting, "base_setting", base_setting)

        current_value = int(base_setting.get(12, 0) or 0)

        # 在 enforce_bounds 为 True 时确保当前设置落在允许范围内
        if enforce_bounds and current_value not in allowed_indices:
            current_value = allowed_indices[-1]
            base_setting[12] = current_value

        return current_value, allowed_indices, option_list

    def _resolve_hint_highlight_targets(self) -> Tuple[Set[int], Set[Tuple[int, int]], Set[int]]:
        """根据玩家医疗等级确定需要高亮的系统、部位与并发症。"""

        if self.patient is None:
            return set(), set(), set()

        # 读取当前提示等级，若已关闭提示则无需计算高亮范围
        hint_value, _allowed_indices, _option_list = self._fetch_hint_setting_context(enforce_bounds=True)
        if hint_value <= 0:
            return set(), set(), set()

        # 汇总病人追踪记录，提取系统、部位与并发症严重程度索引
        trace_list = getattr(self.patient, "complication_trace", [])
        if not trace_list:
            return set(), set(), set()

        system_targets: Set[int] = set()
        part_targets: Set[Tuple[int, int]] = set()
        complication_by_severity: Dict[int, Set[int]] = {}

        for entry in trace_list:
            system_id = int(entry.get("system_id", 0) or 0)
            part_id = int(entry.get("part_id", 0) or 0)
            comp_id = int(entry.get("cid", entry.get("complication_id", 0)) or 0)
            severity = entry.get("severity_level")
            if severity is None and comp_id:
                comp_config = game_config.config_medical_complication.get(comp_id)
                severity = getattr(comp_config, "severity_level", 0) if comp_config else 0
            severity_level = int(severity or 0)

            # 依据追踪记录累计系统、部位以及严重程度索引
            if system_id:
                system_targets.add(system_id)
            if system_id and part_id:
                part_targets.add((system_id, part_id))
            if comp_id:
                complication_by_severity.setdefault(severity_level, set()).add(comp_id)

        # 按当前提示等级确定实际需要高亮的系统与部位
        highlight_systems = system_targets if hint_value >= 1 else set()
        highlight_parts = part_targets if hint_value >= 2 else set()

        # 根据提示等级递增叠加不同严重度的并发症高亮范围
        highlight_complications: Set[int] = set()
        if hint_value >= 3:
            highlight_complications |= complication_by_severity.get(0, set())
        if hint_value >= 4:
            highlight_complications |= complication_by_severity.get(1, set())
        if hint_value >= 5:
            for severity_level, comp_ids in complication_by_severity.items():
                if severity_level >= 2:
                    highlight_complications |= comp_ids

        return highlight_systems, highlight_parts, highlight_complications

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
        # 默认回退到 "-" 防止未知等级让 UI 出现异常字符
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
        # 未知结果保持原样返回，方便调试阶段定位新类型
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
            # 每条记录按照“结果 + 名称 + 说明”格式输出
            lines.append(_("· [{outcome}] {name} —— {message}").format(outcome=outcome, name=name, message=message))
        return "\n".join(lines)