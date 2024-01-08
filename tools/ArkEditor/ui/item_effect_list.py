from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import cache_control
from ui.effect_menu import EffectMenu


class ItemEffectList(QWidget):
    """结算表单主体"""

    def __init__(self):
        """初始化结算表单主体"""
        super(ItemEffectList, self).__init__()
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        main_layout = QVBoxLayout()  # 主布局
        # 标题布局
        title_layout = QVBoxLayout()
        label = QLabel()
        label.setText("结算列表")
        title_layout.addWidget(label)
        # 按钮布局
        button_layout = QHBoxLayout()
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
        info_label.setText("右键删除该结算，双击替换该结算")
        # 结算列表布局
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
        """更新结算列表"""
        self.item_list.clear()
        if cache_control.now_edit_type_flag == 1:
            for effect in cache_control.now_event_data[cache_control.now_select_id].effect:
                item = QListWidgetItem(cache_control.effect_data[effect])
                item.setToolTip(item.text())
                self.item_list.addItem(item)

    def change(self):
        """展开结算菜单"""
        menu = EffectMenu()
        menu.exec()

    def change_this_item(self, item):
        """删除该结算并展开结算菜单"""
        self.item_list.takeItem(self.item_list.row(item))
        for effect in cache_control.effect_data:
            if cache_control.effect_data[effect] == item.text():
                effect_cid = effect
                break
        if effect_cid in cache_control.now_event_data[cache_control.now_select_id].effect:
            del cache_control.now_event_data[cache_control.now_select_id].effect[effect_cid]
        menu = EffectMenu()
        menu.exec()

    def reset(self):
        """清零结算列表"""
        cache_control.now_event_data[cache_control.now_select_id].effect = {}
        self.item_list.clear()

    def show_context_menu(self, pos):
        """删除该结算"""
        item = self.item_list.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            action = menu.exec_(self.item_list.mapToGlobal(pos))
            if action == delete_action:
                self.item_list.takeItem(self.item_list.row(item))
                for effect in cache_control.effect_data:
                    if cache_control.effect_data[effect] == item.text():
                        effect_cid = effect
                        break
                if effect_cid in cache_control.now_event_data[cache_control.now_select_id].effect:
                    del cache_control.now_event_data[cache_control.now_select_id].effect[effect_cid]
