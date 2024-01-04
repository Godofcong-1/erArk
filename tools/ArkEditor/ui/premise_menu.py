from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QPushButton,
    QComboBox,
    QTextEdit,
)
from PySide6.QtGui import QFont, Qt
import cache_control


class TreeItem(QTreeWidgetItem):
    """树选框对象"""

    def __init__(self, any):
        """初始化树选框对象"""
        super(TreeItem, self).__init__(any)
        self.cid = ""
        """ 对象配表id """


class PremiseMenu(QDialog):
    """前提选择对象"""

    def __init__(self):
        """初始化前提复选框"""
        super(PremiseMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        else:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = QFont()
        self.font.setPointSize(11)
        self.layout: QHBoxLayout = QHBoxLayout()
        self.resize(1000,1000)
        all_type_list = sorted(list(cache_control.premise_type_data.keys()))
        range_index = int(len(all_type_list) / 2) + 1
        range_a = all_type_list[:range_index]
        range_b = all_type_list[range_index :]
        range_list = [range_a, range_b]
        index = 1
        self.tree_list = []
        for type_list in range_list:
            tree = QTreeWidget()
            tree.setHeaderLabel("前提列表" + str(index))
            index += 1
            tree.setSelectionMode(QAbstractItemView.SingleSelection)
            tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            root_list = []
            for now_type in type_list:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, now_type)
                premise_list = list(cache_control.premise_type_data[now_type])
                premise_list.sort()
                for premise in premise_list:
                    premise_node = TreeItem(now_root)
                    premise_node.cid = premise
                    premise_node.setText(0, cache_control.premise_data[premise])
                    premise_node.setToolTip(0,premise_node.text(0))
                    if cache_control.now_edit_type_flag == 1:
                        if premise in cache_control.now_event_data[cache_control.now_select_id].premise:
                            premise_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_node.setCheckState(0, Qt.Unchecked)
                    else:
                        if premise in cache_control.now_talk_data[cache_control.now_select_id].premise:
                            premise_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            tree.addTopLevelItems(root_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.tree_list.append(tree)
            self.layout.addWidget(tree)
        self.setLayout(self.layout)

    def click_item(self, item: TreeItem, column: int):
        """
        点击选项时勾选选框并更新事件前提
        Keyword arguments:
        item -- 点击的对象
        column -- 点击位置
        """
        if "cid" not in item.__dict__:
            return
        if item.checkState(column) == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
            if cache_control.now_edit_type_flag == 1:
                if item.cid in cache_control.now_event_data[cache_control.now_select_id].premise:
                    del cache_control.now_event_data[cache_control.now_select_id].premise[item.cid]
            else:
                if item.cid in cache_control.now_talk_data[cache_control.now_select_id].premise:
                    del cache_control.now_talk_data[cache_control.now_select_id].premise[item.cid]
        else:
            item.setCheckState(0, Qt.Checked)
            if cache_control.now_edit_type_flag == 1:
                cache_control.now_event_data[cache_control.now_select_id].premise[item.cid] = 1
            else:
                cache_control.now_talk_data[cache_control.now_select_id].premise[item.cid] = 1
        cache_control.item_premise_list.update()


class CVPMenu(QDialog):
    """综合型基础数值前提选择对象"""

    def __init__(self):
        """初始化综合型基础数值前提复选框"""
        super(CVPMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        else:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = QFont()
        self.font.setPointSize(11)
        self.layout: QHBoxLayout = QHBoxLayout()
        self.resize(1000,50)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cvp_a = QComboBox()
        self.cvp_a.addItems(["自己", "交互对象", "角色id为"])
        self.cvp_a.setCurrentIndex(0)
        self.cvp_a.setFont(self.font)
        self.layout.addWidget(self.cvp_a)
        self.cvp_a2 = QTextEdit("0")
        self.cvp_a2.setFont(self.font)
        self.cvp_a2.setFixedHeight(32)
        self.cvp_a2.setFixedWidth(50)
        self.cvp_a2.setVisible(False)
        self.layout.addWidget(self.cvp_a2)
        self.cvp_a.currentIndexChanged.connect(self.change_a2)

        # B数值为属性，A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖
        self.cvp_b1 = QComboBox()
        self.cvp_b1.addItems(["待选择", "好感", "信赖", "能力", "素质", "宝珠", "经验", "状态"])
        self.cvp_b1.setCurrentIndex(0)
        self.cvp_b1.setFont(self.font)
        self.layout.addWidget(self.cvp_b1)

        # b2根据b1会出现不同的选项
        self.cvp_b2 = QComboBox()
        self.cvp_b2.addItems([""])
        self.cvp_b2.setCurrentIndex(0)
        self.cvp_b2.setFont(self.font)
        self.cvp_b2.setVisible(False)
        self.cvp_b1.currentIndexChanged.connect(self.change_b2)
        self.layout.addWidget(self.cvp_b2)

        # C数值为判定方式
        self.cvp_c = QComboBox()
        self.cvp_c.addItems(["大于", "小于", "等于", "大于等于", "小于等于", "不等于"])
        self.cvp_c.setCurrentIndex(0)
        self.cvp_c.setFont(self.font)
        self.layout.addWidget(self.cvp_c)

        # D数值为判定值
        self.cvp_d = QTextEdit("0")
        self.cvp_d.setFont(self.font)
        self.cvp_d.setFixedHeight(32)
        self.cvp_d.setFixedWidth(50)
        self.layout.addWidget(self.cvp_d)

        # 添加确定按钮与取消按钮
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.ok)
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def ok(self):
        """点击确定按钮"""
        # 获得当前abcd的值
        cvp_a = self.cvp_a.currentText()
        if cvp_a == "自己":
            cvp_a_value = "A1"
        elif cvp_a == "交互对象":
            cvp_a_value = "A2"
        elif cvp_a == "角色id为":
            cvp_a_value = "A3|" + self.cvp_a2.toPlainText()
            cvp_a = "角色id为" + self.cvp_a2.toPlainText()
        cvp_b1 = self.cvp_b1.currentText()
        if len(self.cvp_b2.currentText().split("|")) == 2:
            cvp_b2 = self.cvp_b2.currentText().split("|")[1]
        else:
            cvp_b2 = ""
        if cvp_b1 == "待选择":
            cvp_b_value = ""
        elif cvp_b1 == "好感":
            cvp_b_value = "F"
        elif cvp_b1 == "信赖":
            cvp_b_value = "X"
        elif cvp_b1 == "能力":
            cvp_b_value = "A|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "素质":
            cvp_b_value = "T|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "宝珠":
            cvp_b_value = "J|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "经验":
            cvp_b_value = "E|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "状态":
            cvp_b_value = "S|" + self.cvp_b2.currentText().split("|")[0]
        cvp_c = self.cvp_c.currentText()
        if cvp_c == "大于":
            cvp_c_value = "G"
        elif cvp_c == "小于":
            cvp_c_value = "L"
        elif cvp_c == "等于":
            cvp_c_value = "E"
        elif cvp_c == "大于等于":
            cvp_c_value = "GE"
        elif cvp_c == "小于等于":
            cvp_c_value = "LE"
        elif cvp_c == "不等于":
            cvp_c_value = "NE"
        cvp_d = self.cvp_d.toPlainText()
        cvp_d_value = cvp_d

        # 拼接前提字符串
        cvp_str = f"综合数值前提  {cvp_a}{cvp_b1}{cvp_b2}{cvp_c}{cvp_d}"
        cvp_value_str = f"CVP_{cvp_a_value}_{cvp_b_value}_{cvp_c_value}_{cvp_d_value}"
        # print(f"debug cvp_str: {cvp_str}, cvp_value_str: {cvp_value_str}")

        # 更新前提数据
        cache_control.premise_data[cvp_value_str] = cvp_str

        # 更新前提列表
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].premise[cvp_value_str] = 1
        else:
            cache_control.now_talk_data[cache_control.now_select_id].premise[cvp_value_str] = 1
        cache_control.item_premise_list.update()
        self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cvp_a2.setVisible(True)
        else:
            self.cvp_a2.setVisible(False)

    def change_b2(self, index: int):
        """改变b2的选项"""
        self.cvp_b2.setVisible(True)
        if index == 0:
            self.cvp_b2.setVisible(False)
        elif index == 1:
            self.cvp_b2.setVisible(False)
        elif index == 2:
            self.cvp_b2.setVisible(False)
        elif index == 3:
            self.cvp_b2.clear()
            for ability_id, ability_name in cache_control.ability_data.items():
                self.cvp_b2.addItem(f"{ability_id}|{ability_name}")
            self.cvp_b2.setCurrentIndex(0)
        elif index == 4:
            self.cvp_b2.clear()
            for talent_id, talent_name in cache_control.talent_data.items():
                self.cvp_b2.addItem(f"{talent_id}|{talent_name}")
            self.cvp_b2.setCurrentIndex(0)
        elif index == 5:
            self.cvp_b2.clear()
            for juel_id, juel_name in cache_control.juel_data.items():
                self.cvp_b2.addItem(f"{juel_id}|{juel_name}")
            self.cvp_b2.setCurrentIndex(0)
        elif index == 6:
            self.cvp_b2.clear()
            for experience_id, experience_name in cache_control.experience_data.items():
                self.cvp_b2.addItem(f"{experience_id}|{experience_name}")
            self.cvp_b2.setCurrentIndex(0)
        elif index == 7:
            self.cvp_b2.clear()
            for state_id, state_name in cache_control.state_data.items():
                self.cvp_b2.addItem(f"{state_id}|{state_name}")
            self.cvp_b2.setCurrentIndex(0)
        self.cvp_b = self.cvp_b2
