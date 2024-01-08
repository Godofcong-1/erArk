from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import cache_control
from ui.premise_menu import PremiseMenu, CVPMenu


class ItemPremiseList(QWidget):
    """前提表单主体"""

    def __init__(self):
        """初始化前提表单主体"""
        super(ItemPremiseList, self).__init__()
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        main_layout = QVBoxLayout()  # 主布局
        # 标题布局
        title_layout = QVBoxLayout()
        label = QLabel()
        label.setText("前提列表")
        title_layout.addWidget(label)
        # 按钮布局
        button_layout = QHBoxLayout()
        CVP_button = QPushButton("综合型基础数值前提")
        CVP_button.clicked.connect(self.CVP)
        button_layout.addWidget(CVP_button)
        change_button = QPushButton("整体修改")
        change_button.clicked.connect(self.change)
        button_layout.addWidget(change_button)
        reset_button = QPushButton("整体清零")
        reset_button.clicked.connect(self.reset)
        button_layout.addWidget(reset_button)
        title_layout.addLayout(button_layout)
        main_layout.addLayout(title_layout)
        # 文字说明
        info_label = QLabel()
        info_label.setText("右键删除该前提，双击替换该前提")
        # 前提列表布局
        list_layout = QHBoxLayout()
        self.item_list = QListWidget()
        self.item_list.setWordWrap(True)
        self.item_list.adjustSize()
        self.item_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.item_list.customContextMenuRequested.connect(self.show_context_menu)
        self.item_list.itemDoubleClicked.connect(self.change_this_item)
        list_layout.addWidget(self.item_list)
        main_layout.addWidget(info_label)
        main_layout.addLayout(list_layout)
        self.setLayout(main_layout)

    def update(self):
        """更新前提列表"""
        self.item_list.clear()
        if cache_control.now_edit_type_flag == 0:
            for premise in cache_control.now_talk_data[cache_control.now_select_id].premise:
                item = QListWidgetItem(cache_control.premise_data[premise])
                item.setToolTip(item.text())
                self.item_list.addItem(item)
        else:
            for premise in cache_control.now_event_data[cache_control.now_select_id].premise:
                item = QListWidgetItem(cache_control.premise_data[premise])
                item.setToolTip(item.text())
                self.item_list.addItem(item)

    def CVP(self):
        """展开CVP菜单"""
        if cache_control.now_select_id != "":
            menu = CVPMenu()
            menu.exec()

    def change(self):
        """展开前提菜单"""
        if cache_control.now_select_id != "":
            menu = PremiseMenu()
            menu.exec()

    def change_this_item(self, item):
        """删除该前提并展开前提菜单"""
        # 先遍历找到cid
        for premise in cache_control.premise_data:
            if cache_control.premise_data[premise] == item.text():
                premise_cid = premise
                break
        # 根据cid删除前提
        if cache_control.now_edit_type_flag == 1:
            if premise_cid in cache_control.now_event_data[cache_control.now_select_id].premise:
                del cache_control.now_event_data[cache_control.now_select_id].premise[premise_cid]
        else:
            if premise_cid in cache_control.now_talk_data[cache_control.now_select_id].premise:
                del cache_control.now_talk_data[cache_control.now_select_id].premise[premise_cid]
        # 展开前提菜单
        self.change()

    def reset(self):
        """清零前提列表"""
        if cache_control.now_select_id != "":
            if cache_control.now_edit_type_flag == 1:
                cache_control.now_event_data[cache_control.now_select_id].premise = {}
            else:
                cache_control.now_talk_data[cache_control.now_select_id].premise = {}
            self.item_list.clear()

    def show_context_menu(self, pos):
        """删除该前提"""
        item = self.item_list.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            action = menu.exec_(self.item_list.mapToGlobal(pos))
            if action == delete_action:
                self.item_list.takeItem(self.item_list.row(item))
                # 先遍历找到cid
                for premise in cache_control.premise_data:
                    if cache_control.premise_data[premise] == item.text():
                        premise_cid = premise
                        break
                # 根据cid删除前提
                if cache_control.now_edit_type_flag == 1:
                    if premise_cid in cache_control.now_event_data[cache_control.now_select_id].premise:
                        del cache_control.now_event_data[cache_control.now_select_id].premise[premise_cid]
                else:
                    if premise_cid in cache_control.now_talk_data[cache_control.now_select_id].premise:
                        del cache_control.now_talk_data[cache_control.now_select_id].premise[premise_cid]
