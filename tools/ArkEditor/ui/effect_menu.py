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
    QWidgetAction
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
        self.search_text = QTextEdit()
        self.search_text.setFont(self.font)
        self.search_text.setFixedHeight(32)
        self.search_text.setFixedWidth(200)
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
        search_text = self.search_text.toPlainText()
        if not len(search_text):
            return
        for tree in self.tree_list:
            for i in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(i)
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    if search_text in child.text(0):
                        child.setHidden(False)
                    else:
                        child.setHidden(True)

    def reset(self):
        """清零前提列表"""
        self.search_text.setText("")
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    child.setHidden(False)


class CSEMenu(QDialog):
    """综合指令状态结算选择对象"""

    def __init__(self):
        """初始化综合指令状态结算复选框"""
        super(CSEMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        elif cache_control.now_edit_type_flag == 0:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.ABCD_button_layout = QHBoxLayout()
        self.resize(1000,50)

        # 一段说明文字，用来介绍各个功能，位置在最上面的第一行
        self.cse_text = QLabel("用于实现指令状态方面的综合型万用结算，目前仅支持触发玩家的指令")
        self.cse_text.setFont(self.font)
        self.layout.addWidget(self.cse_text)

        self.text_label = QLabel("玩家对")
        self.text_label.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.text_label)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cse_a = QComboBox()
        # self.cse_a.addItems(["自己", "交互对象", "角色id为"])
        self.cse_a.addItems(["自己", "交互对象"])
        self.cse_a.setCurrentIndex(0)
        self.cse_a.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cse_a)
        self.cse_a2 = QTextEdit("0")
        self.cse_a2.setFont(self.font)
        self.cse_a2.setFixedHeight(32)
        self.cse_a2.setFixedWidth(50)
        self.cse_a2.setVisible(False)
        self.ABCD_button_layout.addWidget(self.cse_a2)
        self.cse_a.currentIndexChanged.connect(self.change_a2)

        # 在ABCD_button_layout中加入一个文本的空白label，用来占位
        self.text_label = QLabel(" 使用指令 ")
        self.text_label.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.text_label)

        # 加入菜单，用来选择B的数值
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setFont(self.font)  # 设置菜单栏的字体
        self.status_menu: QMenu = QMenu("待选择", self)
        self.status_menu.setFont(self.font)  # 设置菜单的字体
        self.menu_bar.addMenu(self.status_menu)
        self.ABCD_button_layout.addWidget(self.menu_bar)

        # 创建一个动作组并将其关联到change_status_menu函数
        status_group = QActionGroup(self.status_menu)
        status_group.triggered.connect(self.change_status_menu)

        # 添加每个状态作为一个动作到菜单中
        for status_type in cache_control.status_type_data:
            status_menu = QMenu(status_type, self.status_menu)
            for cid in cache_control.status_type_data[status_type]:
                if cid is cache_control.now_status:
                    continue
                if cid == "0":
                    continue
                now_action: QWidgetAction = QWidgetAction(self)
                now_action.setText(cache_control.status_data[cid])
                now_action.setActionGroup(status_group)
                now_action.setData(cid)
                status_menu.addAction(now_action)
                status_menu.setFont(self.font)
            self.status_menu.addMenu(status_menu)

        self.layout.addLayout(self.ABCD_button_layout)

        # 添加确定按钮与取消按钮
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.ok)
        self.ok_button.setFont(self.font)
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFont(self.font)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    # 将change_status_menu函数定义为一个实例方法
    def change_status_menu(self, action: QWidgetAction):
        """
        更新状态菜单
        Keyword arguments:
        action -- 触发的菜单
        """
        cid = action.data()
        self.status_menu.setTitle(cache_control.status_data[cid])
        self.status_menu.clear()
        status_group = QActionGroup(self.status_menu)
        for status_type in cache_control.status_type_data:
            status_menu = QMenu(status_type, self.status_menu)
            for cid in cache_control.status_type_data[status_type]:
                if cid == "0":
                    continue
                now_action: QWidgetAction = QWidgetAction(self)
                now_action.setText(cache_control.status_data[cid])
                now_action.setActionGroup(status_group)
                now_action.setData(cid)
                status_menu.addAction(now_action)
                status_menu.setFont(self.font)
            self.status_menu.addMenu(status_menu)
        status_group.triggered.connect(self.change_status_menu)


    def ok(self):
        """点击确定按钮"""
        # 获得当前abcd的值
        cse_a = self.cse_a.currentText()
        if cse_a == "自己":
            cse_a_value = "A1"
        elif cse_a == "交互对象":
            cse_a_value = "A2"
        elif cse_a == "角色id为":
            cse_a_value = "A3|" + self.cse_a2.toPlainText()
            cse_a = "角色id为" + self.cse_a2.toPlainText()

        # cse_b为状态的名字，cse_b_value为状态的cid
        cse_b = self.status_menu.title()
        for cid in cache_control.status_data:
            if cache_control.status_data[cid] == cse_b:
                cse_b_value = cid
                break

        # 拼接结算字符串
        cse_str = f"综合指令状态结算  玩家对{cse_a} 进行 {cse_b}"
        cse_value_str = f"CSE_{cse_a_value}_{cse_b_value}"
        # print(f"debug cse_str: {cse_str}, cse_value_str: {cse_value_str}")

        # 更新结算数据
        cache_control.effect_data[cse_value_str] = cse_str

        # 更新结算列表
        cache_control.now_event_data[cache_control.now_select_id].effect[cse_value_str] = 1
        cache_control.item_effect_list.update()
        self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cse_a2.setVisible(True)
        else:
            self.cse_a2.setVisible(False)
