from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
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
        self.resize(1000,1000)
        cvp_default_name = "CVP_A1_F_G_1"
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
