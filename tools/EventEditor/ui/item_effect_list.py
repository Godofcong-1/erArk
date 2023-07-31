from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont
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
        change_button = QPushButton("修改")
        change_button.clicked.connect(self.change)
        button_layout.addWidget(change_button)
        reset_button = QPushButton("清零")
        reset_button.clicked.connect(self.reset)
        button_layout.addWidget(reset_button)
        title_layout.addLayout(button_layout)
        main_layout.addLayout(title_layout)
        # 结算列表布局
        list_layout = QHBoxLayout()
        self.item_list = QListWidget()
        self.item_list.setWordWrap(True)
        self.item_list.adjustSize()
        list_layout.addWidget(self.item_list)
        main_layout.addLayout(list_layout)
        self.setLayout(main_layout)

    def update(self):
        """更新结算列表"""
        self.item_list.clear()
        for effect in cache_control.now_event_data[cache_control.now_event_id].effect:
            item = QListWidgetItem(cache_control.effect_data[effect])
            item.setToolTip(item.text())
            self.item_list.addItem(item)

    def change(self):
        """展开结算菜单"""
        menu = EffectMenu()
        menu.exec()

    def reset(self):
        """清零结算列表"""
        cache_control.now_event_data[cache_control.now_event_id].effect = {}
        self.item_list.clear()
