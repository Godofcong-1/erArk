from PySide6.QtWidgets import QMenuBar, QMenu, QWidgetAction
from PySide6.QtGui import QFont

class MenuBar(QMenuBar):
    """顶部菜单栏"""

    def __init__(self):
        """初始化顶部菜单栏"""
        super(MenuBar, self).__init__()

        # 事件菜单
        event_menu = QMenu("事件", self)
        self.new_event_file_action = QWidgetAction(self)
        self.new_event_file_action.setText("新建事件文件    Ctrl+N")
        self.select_event_file_action = QWidgetAction(self)
        self.select_event_file_action.setText("读取事件文件    Ctrl+O")
        self.save_event_action = QWidgetAction(self)
        self.save_event_action.setText("保存事件        Ctrl+S")
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        event_menu.addActions(
            [
                self.new_event_file_action,
                self.select_event_file_action,
                self.save_event_action,
            ]
        )
        event_menu.setFont(self.font)
        self.addMenu(event_menu)
