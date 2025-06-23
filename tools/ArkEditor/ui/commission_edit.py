# -*- coding: utf-8 -*-
"""
委托属性编辑UI组件
功能：
    - 显示并编辑单个外勤委托的所有属性
    - 支持属性修改，发出保存信号
"""
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QTextEdit, QSpinBox, QPushButton, QComboBox, QDialog, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
import cache_control

def explain_commission_text(text: str) -> str:
    """
    解析委托需求/奖励字符串，转为可理解的中文说明
    参数:
        text: str 需求或奖励字符串（如 a_30_5&r_1_100  ）
    返回:
        str 解释后的中文文本
    功能:
        支持多项（&分隔），支持各类型（a_, r_, e_, t_, j_, c_, 声望_, 特产_, 好感_, 信赖_, 攻略_等）
    """
    # 结果列表
    result = []
    # 多项用&分隔
    items = text.split('&')
    for item in items:
        item = item.strip()
        if not item:
            continue
        # 能力类 a_类型_数量
        if item.startswith('a_'):
            parts = item.split('_')
            if len(parts) == 3:
                ability_id = parts[1]
                value = parts[2]
                ability_name = cache_control.ability_data.get(ability_id, f"ID{ability_id}")
                result.append(f"出勤干员能力[{ability_name}]合计达到{value}级")
            else:
                result.append(item)
        # 资源类 r_类型_数量
        elif item.startswith('r_'):
            parts = item.split('_')
            if len(parts) == 3:
                res_id = parts[1]
                value = parts[2]
                res_name = cache_control.resource_data.get(res_id, f"ID{res_id}")
                result.append(f"资源[{res_name}]{value}个")
            else:
                result.append(item)
        # 经验类 e_类型_数量
        elif item.startswith('e_'):
            parts = item.split('_')
            if len(parts) == 3:
                exp_id = parts[1]
                value = parts[2]
                exp_name = cache_control.experience_data.get(exp_id, f"ID{exp_id}")
                result.append(f"经验[{exp_name}]+{value}")
            else:
                result.append(item)
        # 宝珠类 j_类型_数量
        elif item.startswith('j_'):
            parts = item.split('_')
            if len(parts) == 3:
                juel_id = parts[1]
                value = parts[2]
                juel_name = cache_control.juel_data.get(juel_id, f"ID{juel_id}")
                result.append(f"宝珠[{juel_name}]+{value}")
            else:
                result.append(item)
        # 素质类 t_类型_数量
        elif item.startswith('t_'):
            parts = item.split('_')
            if len(parts) == 3:
                talent_id = parts[1]
                value = parts[2]
                talent_name = cache_control.talent_data.get(talent_id, f"ID{talent_id}")
                if value == '1':
                    result.append(f"获得素质[{talent_name}]")
                else:
                    result.append(f"失去素质[{talent_name}]")
            else:
                result.append(item)
        # 角色类 c_角色ID_1/0
        elif item.startswith('c_'):
            parts = item.split('_')
            if len(parts) == 3:
                chara_id = parts[1]
                flag = parts[2]
                chara_name = cache_control.now_chara_data.Name if hasattr(cache_control.now_chara_data, 'Name') else f"ID{chara_id}"
                if flag == '1':
                    result.append(f"需要角色[{chara_name}]上场或获得该角色")
                else:
                    result.append(f"不包含角色[{chara_name}]")
            else:
                result.append(item)
        # 任务类 m_任务ID_-1/1
        elif item.startswith('m_'):
            parts = item.split('_')
            if len(parts) == 3:
                mission_id = parts[1]
                flag = parts[2]
                mission_name = f"ID{mission_id}"
                if flag == '1':
                    result.append(f"任务[{mission_name}]已完成")
                else:
                    result.append(f"任务[{mission_name}]不可完成")
            else:
                result.append(item)
        # 声望类 声望_势力ID_变化值
        elif item.startswith('声望_'):
            parts = item.split('_')
            if len(parts) == 3:
                nation_id = parts[1]
                value = float(parts[2]) * 0.01
                nation_name = cache_control.nation_data.get(nation_id, f"ID{nation_id}")
                if nation_id == '0':
                    nation_name = "当前国家"
                result.append(f"声望[{nation_name}]{value}")
            else:
                result.append(item)
        # 特产类 特产_出生地ID_数量
        elif item.startswith('特产_'):
            parts = item.split('_')
            if len(parts) == 3:
                birthplace_id = parts[1]
                value = parts[2]
                # 判断地点id是否为0
                if birthplace_id == '0':
                    result.append(f"当前国家的特产，数量{value}")
                else:
                    country_name = cache_control.birthplace_data.get(birthplace_id, f'ID{birthplace_id}')
                    result.append(f"{country_name}的特产，数量{value}")
            else:
                result.append(item)
        # 好感类 好感_角色ID_数值
        elif item.startswith('好感_'):
            parts = item.split('_')
            if len(parts) == 3:
                chara_id = parts[1]
                value = parts[2]
                chara_name = cache_control.now_chara_data.Name if hasattr(cache_control.now_chara_data, 'Name') else f"ID{chara_id}"
                result.append(f"好感[{chara_name}]增加{value}")
            else:
                result.append(item)
        # 信赖类 信赖_角色ID_数值
        elif item.startswith('信赖_'):
            parts = item.split('_')
            if len(parts) == 3:
                chara_id = parts[1]
                value = parts[2]
                chara_name = cache_control.now_chara_data.Name if hasattr(cache_control.now_chara_data, 'Name') else f"ID{chara_id}"
                result.append(f"信赖[{chara_name}]增加{value}")
            else:
                result.append(item)
        # 攻略类 攻略_角色ID_等级
        elif item.startswith('攻略_'):
            parts = item.split('_')
            if len(parts) == 3:
                chara_id = parts[1]
                value = parts[2]
                chara_name = cache_control.now_chara_data.Name if hasattr(cache_control.now_chara_data, 'Name') else f"ID{chara_id}"
                result.append(f"[{chara_name}]攻略等级为{value}")
            else:
                result.append(item)
        # 其他类型，直接显示
        else:
            result.append(item)
    return '\n'.join(result)

class CommissionEditWidget(QWidget):
    """
    外勤委托属性编辑控件
    输入：
        commission: Commission 委托对象
    输出：
        emit commission_saved(Commission) 信号，表示保存修改
    """
    commission_saved = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.commission = None
        self.init_ui()

    def init_ui(self):
        """
        初始化UI控件
        """
        self.layout = QFormLayout(self)
        # 获取全局字体设置
        font = QFont()
        font.setPointSize(cache_control.now_font_size)
        font.setFamily(cache_control.now_font_name)
        # 各属性输入框
        self.cid_edit = QLineEdit(); self.cid_edit.setFont(font)
        self.name_edit = QLineEdit(); self.name_edit.setFont(font)
        # 国家ID下拉框，内容来自cache_control.birthplace_data
        self.country_id_edit = QComboBox()
        self.country_id_edit.setFont(font)
        self.country_id_map = {}  # id到显示名映射
        self.country_id_edit.addItem("-1 通用", -1)
        self.country_id_map[-1] = "通用"
        for k, v in cache_control.birthplace_data.items():
            # k为id，v为名称
            self.country_id_edit.addItem(f"{k} {v}", int(k))
            self.country_id_map[int(k)] = v
        self.level_edit = QSpinBox(); self.level_edit.setRange(1, 99); self.level_edit.setFont(font)
        self.type_edit = QLineEdit(); self.type_edit.setFont(font)
        self.people_edit = QSpinBox(); self.people_edit.setRange(1, 99); self.people_edit.setFont(font)
        self.time_edit = QSpinBox(); self.time_edit.setRange(1, 999); self.time_edit.setFont(font)
        self.demand_edit = QLineEdit(); self.demand_edit.setFont(font)
        self.reward_edit = QLineEdit(); self.reward_edit.setFont(font)
        self.related_id_edit = QSpinBox(); self.related_id_edit.setRange(-1, 9999); self.related_id_edit.setFont(font)
        self.special_edit = QSpinBox(); self.special_edit.setRange(0, 1); self.special_edit.setFont(font)
        self.description_edit = QTextEdit(); self.description_edit.setFont(font)
        # 需求和奖励说明显示框
        self.demand_explain = QTextEdit()
        self.demand_explain.setReadOnly(True)
        self.demand_explain.setFont(font)
        self.reward_explain = QTextEdit()
        self.reward_explain.setReadOnly(True)
        self.reward_explain.setFont(font)
        # 添加到表单
        self.layout.addRow("ID", self.cid_edit)
        self.layout.addRow("名称", self.name_edit)
        self.layout.addRow("国家ID", self.country_id_edit)
        self.layout.addRow("等级", self.level_edit)
        self.layout.addRow("类型", self.type_edit)
        self.layout.addRow("人数", self.people_edit)
        self.layout.addRow("耗时(天)", self.time_edit)
        self.layout.addRow("需求", self.demand_edit)
        self.layout.addRow("需求说明", self.demand_explain)
        self.layout.addRow("奖励", self.reward_edit)
        self.layout.addRow("奖励说明", self.reward_explain)
        self.layout.addRow("前置委托ID", self.related_id_edit)
        self.layout.addRow("特殊委托", self.special_edit)
        self.layout.addRow("描述", self.description_edit)
        # 保存按钮
        self.save_btn = QPushButton("保存修改"); self.save_btn.setFont(font)
        self.save_btn.clicked.connect(self.save_commission)
        self.layout.addRow(self.save_btn)
        # 设置表单label字体
        label_font = font
        for i in range(self.layout.rowCount()):
            label_item = self.layout.itemAt(i, QFormLayout.LabelRole)
            if label_item is not None and label_item.widget() is not None:
                label_item.widget().setFont(label_font)

        # 需求和奖励输入变化时自动更新说明
        self.demand_edit.textChanged.connect(self.update_demand_explain)
        self.reward_edit.textChanged.connect(self.update_reward_explain)
        # 增加“添加”按钮
        self.demand_add_btn = QPushButton("添加"); self.demand_add_btn.setFont(font)
        self.reward_add_btn = QPushButton("添加"); self.reward_add_btn.setFont(font)
        self.layout.insertRow(self.layout.getWidgetPosition(self.demand_edit)[0]+1, "", self.demand_add_btn)
        self.layout.insertRow(self.layout.getWidgetPosition(self.reward_edit)[0]+1, "", self.reward_add_btn)
        self.demand_add_btn.clicked.connect(self.add_demand_item)
        self.reward_add_btn.clicked.connect(self.add_reward_item)

    def update_demand_explain(self):
        """
        实时更新需求说明
        """
        text = self.demand_edit.text()
        self.demand_explain.setPlainText(explain_commission_text(text))

    def update_reward_explain(self):
        """
        实时更新奖励说明
        """
        text = self.reward_edit.text()
        self.reward_explain.setPlainText(explain_commission_text(text))

    def set_commission(self, commission):
        """
        显示当前委托属性
        """
        self.commission = commission
        self.cid_edit.setText(str(commission.cid))
        self.name_edit.setText(commission.name)
        # 设置下拉框选中项
        idx = self.country_id_edit.findData(commission.country_id)
        if idx >= 0:
            self.country_id_edit.setCurrentIndex(idx)
        self.level_edit.setValue(commission.level)
        self.type_edit.setText(commission.type)
        self.people_edit.setValue(commission.people)
        self.time_edit.setValue(commission.time)
        self.demand_edit.setText(commission.demand)
        self.reward_edit.setText(commission.reward)
        self.related_id_edit.setValue(commission.related_id)
        self.special_edit.setValue(commission.special)
        self.description_edit.setPlainText(commission.description)
        # 设置说明文本
        self.demand_explain.setPlainText(explain_commission_text(commission.demand))
        self.reward_explain.setPlainText(explain_commission_text(commission.reward))

    def save_commission(self):
        """
        保存属性到对象并发出信号
        """
        c = self.commission
        c.cid = int(self.cid_edit.text())
        c.name = self.name_edit.text()
        # 取下拉框选中的国家id
        c.country_id = self.country_id_edit.currentData()
        c.level = self.level_edit.value()
        c.type = self.type_edit.text()
        c.people = self.people_edit.value()
        c.time = self.time_edit.value()
        c.demand = self.demand_edit.text()
        c.reward = self.reward_edit.text()
        c.related_id = self.related_id_edit.value()
        c.special = self.special_edit.value()
        c.description = self.description_edit.toPlainText()
        self.commission_saved.emit(c)

    def add_demand_item(self):
        dialog = CommissionItemAddDialog(self)
        if dialog.exec():
            new_item = dialog.get_result()
            old = self.demand_edit.text().strip()
            if old:
                self.demand_edit.setText(old + '&' + new_item)
            else:
                self.demand_edit.setText(new_item)

    def add_reward_item(self):
        dialog = CommissionItemAddDialog(self)
        if dialog.exec():
            new_item = dialog.get_result()
            old = self.reward_edit.text().strip()
            if old:
                self.reward_edit.setText(old + '&' + new_item)
            else:
                self.reward_edit.setText(new_item)

class CommissionItemAddDialog(QDialog):
    """
    委托需求/奖励项添加对话框
    输入：
        parent: QWidget 父窗口
    输出：
        用户选择的需求/奖励项字符串
    功能：
        提供类型、子项、数值的选择与输入，生成格式化字符串
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标题
        self.setWindowTitle("添加需求/奖励项")
        # 设置字体
        font = QFont()
        font.setPointSize(cache_control.now_font_size)
        font.setFamily(cache_control.now_font_name)
        self.setFont(font)
        # 主垂直布局
        main_layout = QVBoxLayout(self)
        # 横向布局用于放置类型、子项、数值
        h_layout = QHBoxLayout()
        # A: 类型选择下拉框
        self.type_combo = QComboBox(); self.type_combo.setFont(font)
        self.type_combo.addItems([
            "能力", "资源", "经验", "宝珠", "素质", "角色", "任务", "声望", "特产", "好感", "信赖", "攻略"
        ])
        # 设置类型下拉框宽度
        self.type_combo.setMinimumWidth(120)
        # 添加类型标签和控件
        type_label = QLabel("类型", self)
        type_label.setFont(font)
        type_label.setMinimumWidth(40)
        h_layout.addWidget(type_label)
        h_layout.addWidget(self.type_combo)
        # B: 子项选择/输入
        self.sub_combo = QComboBox(); self.sub_combo.setFont(font)
        self.sub_combo.setMinimumWidth(160)
        self.sub_edit = QLineEdit(); self.sub_edit.setFont(font)
        self.sub_edit.setMinimumWidth(160)
        self.current_sub_widget = self.sub_combo  # 记录当前插入的控件
        # 添加子项标签和控件
        sub_label = QLabel("子项", self)
        sub_label.setFont(font)
        sub_label.setMinimumWidth(40)
        h_layout.addWidget(sub_label)
        h_layout.addWidget(self.sub_combo)
        # C: 数值输入框
        self.value_edit = QLineEdit(); self.value_edit.setFont(font)
        self.value_edit.setText("1")
        self.value_edit.setMinimumWidth(100)
        # 添加数值标签和控件
        value_label = QLabel("数值", self)
        value_label.setFont(font)
        value_label.setMinimumWidth(40)
        h_layout.addWidget(value_label)
        h_layout.addWidget(self.value_edit)
        # 添加横向布局到主布局
        main_layout.addLayout(h_layout)
        # 确定按钮
        self.ok_btn = QPushButton("确定"); self.ok_btn.setFont(font)
        self.ok_btn.clicked.connect(self.accept)
        main_layout.addWidget(self.ok_btn)
        self.setLayout(main_layout)
        # 类型切换时刷新子项
        self.type_combo.currentTextChanged.connect(self.update_sub_items)
        self.update_sub_items(self.type_combo.currentText())

    def update_sub_items(self, type_name):
        # 只移除当前插入的控件
        from PySide6.QtWidgets import QHBoxLayout
        h_layout = self.layout().itemAt(0).layout()
        # 子项控件在h_layout的第3和第4个位置
        if hasattr(self, 'current_sub_widget') and self.current_sub_widget is not None:
            h_layout.removeWidget(self.current_sub_widget)
            self.current_sub_widget.setParent(None)
        # 再插入对应控件，并更新current_sub_widget
        if type_name == "能力":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            for k, v in cache_control.ability_data.items():
                self.sub_combo.addItem(f"{v}", k)
            h_layout.insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        elif type_name == "资源":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            for k, v in cache_control.resource_data.items():
                self.sub_combo.addItem(f"{v}", k)
            h_layout.insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        elif type_name == "经验":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            for k, v in cache_control.experience_data.items():
                self.sub_combo.addItem(f"{v}", k)
            h_layout.insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        elif type_name == "宝珠":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            for k, v in cache_control.juel_data.items():
                self.sub_combo.addItem(f"{v}", k)
            h_layout.insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        elif type_name == "素质":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            for k, v in cache_control.talent_data.items():
                self.sub_combo.addItem(f"{v}", k)
            h_layout.insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        elif type_name == "声望":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            for k, v in cache_control.nation_data.items():
                self.sub_combo.addItem(f"{v}", k)
            h_layout.insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        elif type_name == "特产":
            self.sub_combo = QComboBox(); self.sub_combo.setFont(self.font())
            # 先选择国家，id为0时显示“当前国家”
            self.sub_combo.addItem("当前国家", 0)
            for k, v in cache_control.birthplace_data.items():
                # 跳过0
                if int(k) == 0:
                    continue
                self.sub_combo.addItem(f"{v}", int(k))
            self.layout().itemAt(0).layout().insertWidget(3, self.sub_combo)
            self.current_sub_widget = self.sub_combo
        else:
            self.sub_edit = QLineEdit(); self.sub_edit.setFont(self.font())
            h_layout.insertWidget(3, self.sub_edit)
            self.current_sub_widget = self.sub_edit

    def get_result(self):
        type_name = self.type_combo.currentText()
        if type_name in ["能力", "资源", "经验", "宝珠", "素质", "声望", "特产"]:
            sub_id = self.sub_combo.currentData()
        else:
            sub_id = self.sub_edit.text()
        value = self.value_edit.text()
        # 生成格式化字符串
        if type_name == "能力":
            return f"a_{sub_id}_{value}"
        elif type_name == "资源":
            return f"r_{sub_id}_{value}"
        elif type_name == "经验":
            return f"e_{sub_id}_{value}"
        elif type_name == "宝珠":
            return f"j_{sub_id}_{value}"
        elif type_name == "素质":
            return f"t_{sub_id}_{value}"
        elif type_name == "角色":
            return f"c_{sub_id}_{value}"
        elif type_name == "任务":
            return f"m_{sub_id}_{value}"
        elif type_name == "声望":
            return f"声望_{sub_id}_{value}"
        elif type_name == "特产":
            # 判断地点id是否为0，若为0则用0，否则用选中的id
            sub_id = self.sub_combo.currentData()
            if str(sub_id) == '0':
                sub_id = 0  # 固定为0，表示当前国家
            return f"特产_{sub_id}_{value}"
        elif type_name == "好感":
            return f"好感_{sub_id}_{value}"
        elif type_name == "信赖":
            return f"信赖_{sub_id}_{value}"
        elif type_name == "攻略":
            return f"攻略_{sub_id}_{value}"
        else:
            return ""
