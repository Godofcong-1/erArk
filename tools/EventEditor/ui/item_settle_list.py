from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
import cache_control


class ItemSettleList(QWidget):
    """结算器表单主体"""

    def __init__(self):
        """初始化结算器表单主体"""
        super(ItemSettleList, self).__init__()
        self.font = QFont()
        self.font.setPointSize(12)
        self.setFont(self.font)
        layout = QVBoxLayout()
        label = QLabel()
        label.setText("结算器列表")
        layout.addWidget(label)
        self.item_list = QListWidget()
        layout.addWidget(self.item_list)
        self.setLayout(layout)

    def update(self):
        """更新结算器列表"""
        self.item_list.clear()
        for settle in cache_control.now_event_data[cache_control.now_event_id].settle:
            item = QListWidgetItem(cache_control.settle_data[settle])
            item.setToolTip(item.text())
            self.item_list.addItem(item)
