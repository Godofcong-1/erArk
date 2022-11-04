from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QFont
import cache_control


class ToolsBar(QMenuBar):
    """筛选表单用菜单栏"""

    def __init__(self):
        """初始化顶部筛选栏"""
        super(ToolsBar, self).__init__()
        self.font = QFont()
        self.font.setPointSize(12)
        self.npc_menu: QMenu = QMenu("0", self)
        self.npc_menu.setFixedWidth(50)
        self.addMenu(self.npc_menu)
        self.status_menu: QMenu = QMenu(cache_control.status_data[cache_control.now_status], self)
        self.status_menu.setFont(self.font)
        self.addMenu(self.status_menu)
        self.start_menu: QMenu = QMenu(cache_control.start_status, self)
        self.start_menu.setFont(self.font)
        self.addMenu(self.start_menu)
        self.setFont(self.font)
