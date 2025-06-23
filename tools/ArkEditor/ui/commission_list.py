# -*- coding: utf-8 -*-
"""
委托列表UI组件
功能：
    - 显示所有外勤委托（左侧列表）
    - 点击后发出信号，主窗口可根据选中项显示详细属性
"""
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Signal

class CommissionListWidget(QListWidget):
    """
    外勤委托列表控件
    输入：
        commissions: list[Commission] 委托对象列表
    输出：
        emit commission_selected(Commission) 信号，表示选中某个委托
    """
    commission_selected = Signal(object)

    def __init__(self, commissions, parent=None):
        super().__init__(parent)
        self.commissions = commissions
        self.refresh_list()
        self.itemClicked.connect(self.on_item_clicked)

    def refresh_list(self):
        """
        刷新列表内容
        """
        self.clear()
        # 遍历所有委托，显示在列表中
        for commission in self.commissions:
            # 列表项显示格式：ID 委托名称
            item = QListWidgetItem(f"{commission.cid} {commission.name}")
            item.setData(1000, commission)  # 存储对象引用
            self.addItem(item)

    def on_item_clicked(self, item):
        """
        处理点击事件，发出选中信号
        """
        commission = item.data(1000)
        self.commission_selected.emit(commission)
