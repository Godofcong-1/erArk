# -*- coding: utf-8 -*-
"""
公务事件属性编辑UI组件（Plan 23）
功能：
    - 右侧表单编辑一条公务事件的基本字段
    - 四个选项块各自一个 QGroupBox，含文本、前提、置灰原因、后果提示、结算
    - 前提与结算复用编辑器既有的选择器（PremiseMenu / CVPMenu / EffectMenu / CVEMenu）

那几个选择器都是直接往 `cache_control.now_event_data[now_select_id].premise/effect` 里写的，
   本模块用一个**临时载体**顶上去（打开弹窗前换、关闭后换回），
   这样既不用改那6个文件，也不会污染正在编辑的口上/事件数据。
"""
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QScrollArea,
    QLabel,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

SUBJECT_TEXT = {0: "0 无主体（部门事务）", 1: "1 角色"}
""" 事件主体的下拉项 """

ONCE_TEXT = {0: "0 普通", 1: "1 里程碑（仅标注）"}
""" once 列的下拉项。它已经不影响触发：所有事件都对同一个角色只发生一次 """


class SelectorShim:
    """
    给既有前提/结算选择器用的临时载体
    输入：
        text: str 弹窗标题用的文字
        premise: dict 前提集合
        effect: dict 结算集合
    输出：无
    功能：冒充 cache_control.now_event_data 里的一条事件，接住选择器写进来的内容
    """

    def __init__(self, text: str, premise: dict, effect: dict):
        self.text = text
        self.premise = premise
        self.effect = effect


class DummyItemList:
    """
    冒充 item_premise_list / item_effect_list 的空壳
    输入：无
    输出：无
    功能：选择器写完会调它的 update()，这里什么也不做
    """

    def update(self):
        """什么也不做"""
        return


def text_to_dict(text: str) -> dict:
    """
    把 & 连接的串拆成选择器要的 dict
    参数:
        text: str 前提串或结算串
    返回:
        dict 键为token
    """
    result = {}
    for one in text.split("&"):
        one = one.strip()
        if one:
            result[one] = 1
    return result


def dict_to_text(data: dict) -> str:
    """
    把选择器写好的 dict 拼回 & 连接的串
    参数:
        data: dict token集合
    返回:
        str 串
    """
    return "&".join([one for one in data if data[one]])


class OfficialEventEditWidget(QWidget):
    """
    公务事件属性编辑控件
    输入：
        department_name_data: dict 部门id -> 部门名，用于下拉显示
    输出：
        emit event_saved(OfficialEvent) 保存了一条事件
    """

    event_saved = Signal(object)

    def __init__(self, department_name_data: dict = None, parent=None):
        super().__init__(parent)
        self.now_event = None
        """ 当前编辑的事件 """
        self.department_name_data = department_name_data or {}
        """ 部门id -> 部门名 """
        self.init_ui()

    def init_ui(self):
        """
        初始化UI控件
        参数: 无
        返回: 无
        """
        outer_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        self.form_layout = QFormLayout(inner)
        # 基本字段
        self.cid_edit = QLineEdit()
        self.file_label = QLabel("")
        self.department_edit = QComboBox()
        if self.department_name_data:
            for department in sorted(self.department_name_data):
                self.department_edit.addItem(f"{department} {self.department_name_data[department]}", department)
        else:
            for department in range(0, 21):
                self.department_edit.addItem(str(department), department)
        self.subject_edit = QComboBox()
        for key in sorted(SUBJECT_TEXT):
            self.subject_edit.addItem(SUBJECT_TEXT[key], key)
        self.sub_key_edit = QSpinBox()
        self.sub_key_edit.setRange(0, 9999)
        self.once_edit = QComboBox()
        for key in sorted(ONCE_TEXT):
            self.once_edit.addItem(ONCE_TEXT[key], key)
        self.weight_edit = QSpinBox()
        self.weight_edit.setRange(1, 9999)
        self.premise_edit = QLineEdit()
        self.text_edit = QTextEdit()
        self.text_edit.setFixedHeight(90)
        self.form_layout.addRow("所属文件", self.file_label)
        self.form_layout.addRow("事件cid", self.cid_edit)
        self.form_layout.addRow("部门", self.department_edit)
        self.form_layout.addRow("事件主体", self.subject_edit)
        self.form_layout.addRow("子桶键(养成填阶段素质id)", self.sub_key_edit)
        self.form_layout.addRow("里程碑标注", self.once_edit)
        self.form_layout.addRow("入队权重", self.weight_edit)
        self.form_layout.addRow("触发前提", self.make_token_row(self.premise_edit, True))
        self.form_layout.addRow("事件正文", self.text_edit)
        # 四个选项块
        self.option_widget_list = []
        for index in range(1, 5):
            box = QGroupBox(f"选项 {index}")
            box.setFont(font)
            box_layout = QFormLayout(box)
            option_text = QTextEdit()
            option_text.setFixedHeight(60)
            option_premise = QLineEdit()
            option_reason = QLineEdit()
            option_tip = QLineEdit()
            option_effect = QLineEdit()
            box_layout.addRow("选项文本", option_text)
            box_layout.addRow("选项前提", self.make_token_row(option_premise, True))
            box_layout.addRow("置灰原因", option_reason)
            box_layout.addRow("后果提示", option_tip)
            box_layout.addRow("选项结算", self.make_token_row(option_effect, False))
            self.option_widget_list.append(
                {"text": option_text, "premise": option_premise, "reason": option_reason, "tip": option_tip, "effect": option_effect}
            )
            self.form_layout.addRow(box)
        self.save_btn = QPushButton("保存修改")
        self.save_btn.clicked.connect(self.save_event)
        self.form_layout.addRow(self.save_btn)
        # 统一字体
        for widget in self.findChildren(QWidget):
            widget.setFont(font)
        scroll.setWidget(inner)
        outer_layout.addWidget(scroll)

    def make_token_row(self, edit: QLineEdit, is_premise: bool) -> QWidget:
        """
        造一个「输入框 + 两个选择按钮」的横排
        参数:
            edit: QLineEdit 承载token串的输入框
            is_premise: bool True为前提行，False为结算行
        返回:
            QWidget 横排控件
        """
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(edit)
        if is_premise:
            list_btn = QPushButton("选前提")
            list_btn.clicked.connect(lambda: self.open_premise_menu(edit))
            value_btn = QPushButton("综合前提")
            value_btn.clicked.connect(lambda: self.open_cvp_menu(edit))
        else:
            list_btn = QPushButton("选结算")
            list_btn.clicked.connect(lambda: self.open_effect_menu(edit))
            value_btn = QPushButton("综合结算")
            value_btn.clicked.connect(lambda: self.open_cve_menu(edit))
        row_layout.addWidget(list_btn)
        row_layout.addWidget(value_btn)
        return row

    def run_with_shim(self, edit: QLineEdit, is_premise: bool, dialog_maker):
        """
        用临时载体顶替全局数据，打开一个既有的选择器弹窗，关闭后把结果写回输入框
        参数:
            edit: QLineEdit 要写回的输入框
            is_premise: bool 操作的是前提还是结算
            dialog_maker: Callable 造弹窗的函数（在载体装好之后才调用）
        返回: 无
        功能:
            五个全局都要存下来再还原：选择器认的是
               now_edit_type_flag / now_event_data / now_select_id 与两个列表面板
        """
        old_flag = cache_control.now_edit_type_flag
        old_event_data = cache_control.now_event_data
        old_select_id = getattr(cache_control, "now_select_id", "")
        old_premise_list = getattr(cache_control, "item_premise_list", None)
        old_effect_list = getattr(cache_control, "item_effect_list", None)
        premise_dict = text_to_dict(edit.text()) if is_premise else {}
        effect_dict = {} if is_premise else text_to_dict(edit.text())
        shim = SelectorShim(self.text_edit.toPlainText()[:20], premise_dict, effect_dict)
        cache_control.now_edit_type_flag = 1
        cache_control.now_event_data = {"0": shim}
        cache_control.now_select_id = "0"
        cache_control.item_premise_list = DummyItemList()
        cache_control.item_effect_list = DummyItemList()
        try:
            dialog = dialog_maker()
            dialog.exec()
        finally:
            cache_control.now_edit_type_flag = old_flag
            cache_control.now_event_data = old_event_data
            cache_control.now_select_id = old_select_id
            if old_premise_list is not None:
                cache_control.item_premise_list = old_premise_list
            if old_effect_list is not None:
                cache_control.item_effect_list = old_effect_list
        edit.setText(dict_to_text(shim.premise if is_premise else shim.effect))

    def open_premise_menu(self, edit: QLineEdit):
        """
        打开前提列表选择器
        参数:
            edit: QLineEdit 要写回的输入框
        返回: 无
        """
        from ui.premise_menu import PremiseMenu

        self.run_with_shim(edit, True, PremiseMenu)

    def open_cvp_menu(self, edit: QLineEdit):
        """
        打开综合数值前提构造器
        参数:
            edit: QLineEdit 要写回的输入框
        返回: 无
        """
        from ui.CVP_menu import CVPMenu

        self.run_with_shim(edit, True, CVPMenu)

    def open_effect_menu(self, edit: QLineEdit):
        """
        打开结算列表选择器
        参数:
            edit: QLineEdit 要写回的输入框
        返回: 无
        """
        from ui.effect_menu import EffectMenu

        self.run_with_shim(edit, False, EffectMenu)

    def open_cve_menu(self, edit: QLineEdit):
        """
        打开综合数值结算构造器
        参数:
            edit: QLineEdit 要写回的输入框
        返回: 无
        """
        from ui.CVE_menu import CVEMenu

        self.run_with_shim(edit, False, CVEMenu)

    def set_event(self, event):
        """
        把一条事件填进表单
        参数:
            event: OfficialEvent 事件对象
        返回: 无
        """
        self.now_event = event
        if event is None:
            return
        self.file_label.setText(event.file_name)
        self.cid_edit.setText(str(event.cid))
        index = self.department_edit.findData(event.department)
        if index >= 0:
            self.department_edit.setCurrentIndex(index)
        index = self.subject_edit.findData(event.subject)
        if index >= 0:
            self.subject_edit.setCurrentIndex(index)
        self.sub_key_edit.setValue(event.sub_key)
        index = self.once_edit.findData(event.once)
        if index >= 0:
            self.once_edit.setCurrentIndex(index)
        self.weight_edit.setValue(max(1, event.weight))
        self.premise_edit.setText(event.premise)
        self.text_edit.setPlainText(event.text)
        for i, widget_data in enumerate(self.option_widget_list):
            option = event.options[i]
            widget_data["text"].setPlainText(option["text"])
            widget_data["premise"].setText(option["premise"])
            widget_data["reason"].setText(option["reason"])
            widget_data["tip"].setText(option["tip"])
            widget_data["effect"].setText(option["effect"])

    def save_event(self):
        """
        把表单内容写回事件对象并发出保存信号
        参数: 无
        返回: 无
        """
        if self.now_event is None:
            return
        self.now_event.cid = self.cid_edit.text().strip()
        self.now_event.department = self.department_edit.currentData()
        self.now_event.subject = self.subject_edit.currentData()
        self.now_event.sub_key = self.sub_key_edit.value()
        self.now_event.once = self.once_edit.currentData()
        self.now_event.weight = self.weight_edit.value()
        self.now_event.premise = self.premise_edit.text().strip()
        self.now_event.text = self.text_edit.toPlainText().strip()
        for i, widget_data in enumerate(self.option_widget_list):
            self.now_event.options[i] = {
                "text": widget_data["text"].toPlainText().strip(),
                "premise": widget_data["premise"].text().strip(),
                "reason": widget_data["reason"].text().strip(),
                "tip": widget_data["tip"].text().strip(),
                "effect": widget_data["effect"].text().strip(),
            }
        self.event_saved.emit(self.now_event)
