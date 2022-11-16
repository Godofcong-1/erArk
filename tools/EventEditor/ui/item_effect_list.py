from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
import cache_control


class ItemEffectList(QWidget):
    """结算表单主体"""

    def __init__(self):
        """初始化结算表单主体"""
        super(ItemEffectList, self).__init__()
        self.font = QFont()
        self.font.setPointSize(12)
        self.setFont(self.font)
        layout = QVBoxLayout()
        label = QLabel()
        label.setText("结算列表")
        layout.addWidget(label)
        self.item_list = QListWidget()
        self.item_list.setWordWrap(True)
        self.item_list.adjustSize()
        layout.addWidget(self.item_list)
        self.setLayout(layout)

    def update(self):
        """更新结算列表"""
        self.item_list.clear()
        for effect in cache_control.now_event_data[cache_control.now_event_id].effect:
            item = QListWidgetItem(cache_control.effect_data[effect])
            item.setToolTip(item.text())
            self.item_list.addItem(item)
