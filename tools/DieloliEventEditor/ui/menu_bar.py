from PySide6.QtWidgets import QMenuBar, QMenu, QWidgetAction


class MenuBar(QMenuBar):
    """顶部菜单栏"""

    def __init__(self):
        """初始化顶部菜单栏"""
        super(MenuBar, self).__init__()
        file_menu = QMenu("文件", self)
        self.select_event_file_action = QWidgetAction(self)
        self.select_event_file_action.setText("选择事件文件    Ctrl+O")
        self.new_event_file_action = QWidgetAction(self)
        self.new_event_file_action.setText("新建事件文件    Ctrl+N")
        self.save_event_action = QWidgetAction(self)
        self.save_event_action.setText("保存事件        Ctrl+S")
        self.exit_action = QWidgetAction(self)
        self.exit_action.setText("关闭编辑器      Ctrl+Q")
        file_menu.addActions(
            [
                self.select_event_file_action,
                self.new_event_file_action,
                self.save_event_action,
                self.exit_action,
            ]
        )
        self.addMenu(file_menu)
