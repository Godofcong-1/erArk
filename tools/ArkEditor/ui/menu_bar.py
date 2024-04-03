from PySide6.QtWidgets import QMenuBar, QMenu, QWidgetAction, QDialog, QTextEdit, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont, QAction, QFontMetrics
import function

class MenuBar(QMenuBar):
    """顶部菜单栏"""

    def __init__(self):
        """初始化顶部菜单栏"""
        super(MenuBar, self).__init__()

        # 口上菜单
        talk_menu = QMenu("口上", self)
        self.new_talk_file_action = QWidgetAction(self)
        self.new_talk_file_action.setText("新建口上文件")
        self.select_talk_file_action = QWidgetAction(self)
        self.select_talk_file_action.setText("读取口上文件")
        self.save_talk_action = QWidgetAction(self)
        self.save_talk_action.setText("保存口上        Ctrl+S")
        self.talk_introduce_action = QAction("口上说明", self)
        self.talk_introduce_action.triggered.connect(function.show_talk_introduce)
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        talk_menu.addActions(
            [
                self.new_talk_file_action,
                self.select_talk_file_action,
                self.save_talk_action,
                self.talk_introduce_action,
            ]
        )
        talk_menu.setFont(self.font)
        self.addMenu(talk_menu)

        # 事件菜单
        event_menu = QMenu("事件", self)
        self.new_event_file_action = QWidgetAction(self)
        self.new_event_file_action.setText("新建事件文件")
        self.select_event_file_action = QWidgetAction(self)
        self.select_event_file_action.setText("读取事件文件")
        self.save_event_action = QWidgetAction(self)
        self.save_event_action.setText("保存事件        Ctrl+S")
        self.event_introduce_action = QAction("事件说明", self)
        self.event_introduce_action.triggered.connect(function.show_event_introduce)
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        event_menu.addActions(
            [
                self.new_event_file_action,
                self.select_event_file_action,
                self.save_event_action,
                self.event_introduce_action,
            ]
        )
        event_menu.setFont(self.font)
        self.addMenu(event_menu)

        # 角色菜单
        chara_menu = QMenu("角色属性", self)
        self.new_chara_file_action = QWidgetAction(self)
        self.new_chara_file_action.setText("新建角色属性文件")
        self.select_chara_file_action = QWidgetAction(self)
        self.select_chara_file_action.setText("读取角色属性文件")
        self.chara_introduce_action = QAction("角色说明", self)
        self.chara_introduce_action.triggered.connect(function.show_chara_introduce)
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        chara_menu.addActions(
            [
                self.new_chara_file_action,
                self.select_chara_file_action,
                self.chara_introduce_action,
            ]
        )
        chara_menu.setFont(self.font)
        self.addMenu(chara_menu)
