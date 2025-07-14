from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QMenu,
    QComboBox,
    QMenuBar,
    QWidgetAction,
    QLineEdit  # 新增 QLineEdit
)
from PySide6.QtGui import QFont, Qt, QActionGroup
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

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
        self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.resize(1000,1000)
        # 增加一个搜索框，确定键，重置键，三个合在一起，放在最上面作为一个横向的搜索栏
        # 搜索框改为 QLineEdit，便于回车直接触发搜索
        self.search_text = QLineEdit()
        self.search_text.setFont(self.font)
        self.search_text.setFixedHeight(32)
        self.search_text.setFixedWidth(200)
        self.search_text.returnPressed.connect(self.search)  # 回车直接触发搜索
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search)
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset)
        # 放在tree的上面，作为一个横向的搜索栏
        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(self.search_text)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.reset_button)
        self.layout.addLayout(self.search_layout)
        # 创建一个新的 QHBoxLayout，用于左右排列两个 tree
        self.tree_layout = QHBoxLayout()
        all_type_list = sorted([k for k in cache_control.effect_type_data.keys() if k is not None])
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
                    if effect in cache_control.now_event_data[cache_control.now_select_id].effect:
                        effect_node.setCheckState(0, Qt.Checked)
                    else:
                        effect_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            tree.addTopLevelItems(root_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.tree_list.append(tree)
            self.tree_layout.addWidget(tree)  # 将 tree 添加到 QHBoxLayout 中
        self.layout.addLayout(self.tree_layout)
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
            if item.cid in cache_control.now_event_data[cache_control.now_select_id].effect:
                del cache_control.now_event_data[cache_control.now_select_id].effect[item.cid]
        else:
            item.setCheckState(0, Qt.Checked)
            cache_control.now_event_data[cache_control.now_select_id].effect[item.cid] = 1
        cache_control.item_effect_list.update()

    def search(self):
        """搜索结算器"""
        search_text = self.search_text.text()  # QLineEdit 获取文本用 text()
        if not len(search_text):
            return
        for tree in self.tree_list:
            for i in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(i)
                has_visible_child = False  # 标记该type下是否有可见子项
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    if search_text in child.text(0):
                        child.setHidden(False)
                        has_visible_child = True
                    else:
                        child.setHidden(True)
                # 如果没有任何子项可见，则隐藏该type（root）
                root.setHidden(not has_visible_child)

    def reset(self):
        """清零前提列表"""
        self.search_text.setText("")
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                root.setHidden(False)  # 重置时显示所有type
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    child.setHidden(False)

