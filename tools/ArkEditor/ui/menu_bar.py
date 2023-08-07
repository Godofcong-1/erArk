from PySide6.QtWidgets import QMenuBar, QMenu, QWidgetAction, QDialog, QTextEdit, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont, QAction, QFontMetrics

class MenuBar(QMenuBar):
    """顶部菜单栏"""

    def __init__(self):
        """初始化顶部菜单栏"""
        super(MenuBar, self).__init__()

        # 添加按钮
        self.new_button_action = QAction("说明", self)
        self.new_button_action.triggered.connect(self.show_dialog)
        self.addAction(self.new_button_action)

        # 口上菜单
        talk_menu = QMenu("口上", self)
        self.new_talk_file_action = QWidgetAction(self)
        self.new_talk_file_action.setText("新建口上文件")
        self.select_talk_file_action = QWidgetAction(self)
        self.select_talk_file_action.setText("读取口上文件")
        self.save_talk_action = QWidgetAction(self)
        self.save_talk_action.setText("保存口上        Ctrl+S")
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        talk_menu.addActions(
            [
                self.new_talk_file_action,
                self.select_talk_file_action,
                self.save_talk_action,
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

    def show_dialog(self):
        """显示只读文本框的对话框"""
        dialog = QDialog(self)
        text_edit = QTextEdit(dialog)
        text_edit.setFont(self.font)
        text = "本编辑器用于编辑游戏 erArk 的口上文件和事件文件。\n\n"
        text += "首先，你需要选择是编辑口上还是事件。点击右边的菜单，读取已有的文件或创建一个新的文件。在编辑完成后，点击保存即可。\n\n"
        text += "编辑器整体分为三个部分，左边的口上/事件条目栏，右上的前提选择栏(编辑事件的话还有结算选择栏)，右下的文本编辑框：\n"
        text += "    ①左边的口上/事件的条目列表，选择对应条目即可对该条目进行编辑。如果是新建的文件的话，需要先新建一个条目出来。此处还可以更改当前条目的角色id、触发命令，以及如果是事件的话，还可以更改事件的触发方式。\n"
        text += "    ②右上的前提选择栏，点击修改按钮来进行编辑，以及还有一个清空按钮。结算选择栏同理\n"
        text += "    ③右下的文本编辑框，在修改完文本后别忘了手动点一下保存按钮。同时在框里鼠标右键可以直接插入对应的一些代码文本。\n"
        text_edit.setText(text)
        text_edit.setReadOnly(True)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        font_metrics = QFontMetrics(text_edit.font())
        text_edit.setFixedWidth(1000)
        line_count = text.count('\n') + 1
        text_edit.setFixedHeight(font_metrics.lineSpacing() * line_count * 2)

        layout = QVBoxLayout(dialog)
        layout.addWidget(text_edit)
        dialog.exec_()
