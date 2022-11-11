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


class EffectMenu(QDialog):
    """事件效果选择对象"""

    def __init__(self):
        """初始化事件效果复选框"""
        super(EffectMenu, self).__init__()
        self.setWindowTitle(cache_control.now_event_data[cache_control.now_event_id].text)
        self.font = QFont()
        self.font.setPointSize(12)
        self.layout: QHBoxLayout = QHBoxLayout()
        self.resize(1000,1000)
        all_type_list = sorted(list(cache_control.effect_type_data.keys()))
        range_index = int(len(all_type_list) / 2) + 1
        range_a = all_type_list[:range_index]
        range_b = all_type_list[range_index :]
        range_list = [range_a, range_b]
        index = 1
        self.tree_list = []
        for type_list in range_list:
            tree = QTreeWidget()
            tree.setHeaderLabel("结算列表" + str(index))
            tree.setWordWrap(True)
            tree.adjustSize()
            index += 1
            tree.setSelectionMode(QAbstractItemView.SingleSelection)
            tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            root_list = []
            for now_type in type_list:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, now_type)
                effect_list = list(cache_control.effect_type_data[now_type])
                effect_list.sort()
                for effect in effect_list:
                    effect_node = TreeItem(now_root)
                    effect_node.cid = effect
                    effect_node.setText(0, cache_control.effect_data[effect])
                    effect_node.setToolTip(0,effect_node.text(0))
                    if effect in cache_control.now_event_data[cache_control.now_event_id].effect:
                        effect_node.setCheckState(0, Qt.Checked)
                    else:
                        effect_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            tree.addTopLevelItems(root_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.tree_list.append(tree)
            self.layout.addWidget(tree)
        self.setLayout(self.layout)

    def click_item(self, item: TreeItem, column: int):
        """
        点击选项时勾选选框并更新事件效果
        Keyword arguments:
        item -- 点击的对象
        column -- 点击位置
        """
        if "cid" not in item.__dict__:
            return
        if item.checkState(column) == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
            if item.cid in cache_control.now_event_data[cache_control.now_event_id].effect:
                del cache_control.now_event_data[cache_control.now_event_id].effect[item.cid]
        else:
            item.setCheckState(0, Qt.Checked)
            cache_control.now_event_data[cache_control.now_event_id].effect[item.cid] = 1
        cache_control.item_effect_list.update()
