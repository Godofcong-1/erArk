from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
)
from PySide6.QtGui import QFont, Qt
import cache_control


class SettleTreeItem(QTreeWidgetItem):
    """结算器树选框对象"""

    def __init__(self, any):
        """初始化结算器树选框对象"""
        super(SettleTreeItem, self).__init__(any)
        self.settle_id = ""
        """ 结算器id """


class SettleMenu(QDialog):
    """结算器选择对象"""

    def __init__(self):
        """初始化事件结算器复选框"""
        super(SettleMenu, self).__init__()
        self.setWindowTitle(cache_control.now_event_data[cache_control.now_event_id].text)
        self.font = QFont()
        self.font.setPointSize(12)
        self.resize(1000,1000)
        self.layout: QHBoxLayout = QHBoxLayout()
        all_type_list = list(cache_control.settle_type_data.keys())
        all_type_list.sort()
        range_index = int(len(all_type_list) / 3) + 1
        range_a = all_type_list[:range_index]
        range_b = all_type_list[range_index : range_index * 2]
        range_c = all_type_list[range_index * 2 :]
        range_list = [range_a, range_b, range_c]
        index = 1
        for type_list in range_list:
            tree = QTreeWidget()
            tree.setHeaderLabel("结算器列表" + str(index))
            index += 1
            tree.setSelectionMode(QAbstractItemView.SingleSelection)
            tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            now_type_list = []
            for now_type in type_list:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, now_type)
                son_type_list = list(cache_control.settle_type_data[now_type].keys())
                for son_type in son_type_list:
                    son_root = QTreeWidgetItem(now_root)
                    son_root.setText(0, son_type)
                    settle_list = list(cache_control.settle_type_data[now_type][son_type])
                    settle_list.sort()
                    for settle in settle_list:
                        settle_node = SettleTreeItem(son_root)
                        settle_node.settle_id = settle
                        settle_node.setText(0,cache_control.settle_data[settle])
                        settle_node.setToolTip(0,cache_control.settle_data[settle])
                        if settle in cache_control.now_event_data[cache_control.now_event_id].settle:
                            settle_node.setCheckState(0, Qt.Checked)
                        else:
                            settle_node.setCheckState(0, Qt.Unchecked)
                        cache_control.item_settle_list.update()
                now_type_list.append(now_root)
            tree.addTopLevelItems(now_type_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.layout.addWidget(tree)
        self.setLayout(self.layout)

    def click_item(self, item: SettleTreeItem, column: int):
        """
        点击选项时勾选选框并更新事件结算器
        Keyword arguments:
        item -- 点击的对象
        column -- 点击位置
        """
        if "settle_id" not in item.__dict__:
            return
        if item.checkState(column) == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
            if item.settle_id in cache_control.now_event_data[cache_control.now_event_id].settle:
                del cache_control.now_event_data[cache_control.now_event_id].settle[item.settle_id]
        else:
            item.setCheckState(0, Qt.Checked)
            cache_control.now_event_data[cache_control.now_event_id].settle[item.settle_id] = 1
        cache_control.item_settle_list.update()
