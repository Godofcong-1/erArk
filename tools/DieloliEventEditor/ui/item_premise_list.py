from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
import cache_control


class ItemPremiseList(QWidget):
    """前提表单主体"""

    def __init__(self):
        """初始化前提表单主体"""
        super(ItemPremiseList, self).__init__()
        self.font = QFont()
        self.font.setPointSize(12)
        self.setFont(self.font)
        layout = QVBoxLayout()
        label = QLabel()
        label.setText("前提列表")
        layout.addWidget(label)
        self.item_list = QListWidget()
        layout.addWidget(self.item_list)
        self.setLayout(layout)

    def update(self):
        """更新前提列表"""
        self.item_list.clear()
        for premise in cache_control.now_event_data[cache_control.now_event_id].premise:
            item = QListWidgetItem(cache_control.premise_data[premise])
            item.setToolTip(item.text())
            self.item_list.addItem(item)
