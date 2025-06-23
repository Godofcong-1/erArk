from PySide6.QtWidgets import QMenuBar, QMenu, QWidgetAction, QDialog, QTextEdit, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont, QAction, QFontMetrics
import function,cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

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
        self.font = font
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
        chara_menu.addActions(
            [
                self.new_chara_file_action,
                self.select_chara_file_action,
                self.chara_introduce_action,
            ]
        )
        chara_menu.setFont(self.font)
        self.addMenu(chara_menu)

        # 外勤委托菜单
        commission_menu = QMenu("外勤委托", self)
        self.select_commission_file_action = QWidgetAction(self)
        self.select_commission_file_action.setText("读取外勤委托文件")
        commission_menu.addAction(self.select_commission_file_action)
        self.commission_path_info_action = QWidgetAction(self)
        self.commission_path_info_action.setText("外勤委托文件路径说明")
        commission_menu.addAction(self.commission_path_info_action)
        commission_menu.setFont(self.font)
        self.addMenu(commission_menu)
        # 绑定说明弹窗
        def show_commission_path_info():
            dialog = QDialog(self)
            dialog.setWindowTitle("外勤委托文件路径说明")
            layout = QVBoxLayout(dialog)
            text = QTextEdit(dialog)
            text.setReadOnly(True)
            text.setFont(self.font)
            text.setPlainText("外勤委托文件路径为游戏本体目录下，\\data\\csv\\Commission.csv。")
            layout.addWidget(text)
            dialog.setLayout(layout)
            dialog.resize(400, 120)
            dialog.exec()
        self.commission_path_info_action.triggered.connect(show_commission_path_info)

        # 设置菜单
        setting_menu = QMenu("设置", self)
        self.setting_action = QAction("设置", self)
        setting_menu.addAction(self.setting_action)
        setting_menu.setFont(self.font)
        self.addMenu(setting_menu)
