from PySide6.QtWidgets import QMenuBar, QMenu, QWidgetAction, QDialog, QTextEdit, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont, QAction, QFontMetrics

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

        # 添加按钮
        self.new_button_action = QAction("说明", self)
        self.new_button_action.triggered.connect(self.show_dialog)
        self.addAction(self.new_button_action)

    def show_dialog(self):
        """显示只读文本框的对话框"""
        dialog = QDialog(self)
        text_edit = QTextEdit(dialog)
        text_edit.setFont(self.font)
        text = "本编辑器用于编辑游戏 erArk 的口上文件和事件文件。\n\n"
        text += "流程简述：\n"
        text += "  ①根据你要编辑口上还是事件，在菜单里选择创建/读取对应的文件。\n  ②在左侧的条目栏中新建一个条目。\n  ③在左侧选择触发的指令，在右上编辑前提（事件则还需要选择结算），在右下编辑条目的文本。\n  ④保存\n\n"
        text += "UI介绍：\n"
        text += "  ①左边，口上/事件的条目列表。选择对应条目即可对该条目进行编辑。如果是新建的文件的话，需要先新建一个条目出来。此处还可以更改当前条目的角色id、触发命令，以及如果是事件的话，还可以更改事件的触发方式。\n"
        text += "  ②右上，前提选择栏。点击修改按钮来进行编辑，以及还有一个清空按钮。在前提上右键可以选择删除该前提。结算选择栏同理\n"
        text += "  ③右下，文本编辑框。在修改完文本后别忘了手动点一下保存按钮。同时在框里鼠标右键可以直接插入对应的一些代码文本。\n\n"
        text += "口上的触发方式：\n"
        text += "  ①在玩家/NPC使用一个指令时，会搜寻【本角色和通用角色的】【本指令下的】所有口上（如果是对他人使用，则还会搜索【对象角色的】），这里将搜到的所有口上定义为A。\n"
        text += "  ②遍历A里每个口上的前提，查看是否满足条件。如果某一条口上的所有前提都被满足，则根据前提量计一个权重大小，该口上进入选择池。这里将选择池里的所有口上定义为B，显然，B是A的一个子集。\n"
        text += "  ③在B中根据权重比例来随机选择一个口上作为当前的结果口上，假如B中有3个口上，权重分别为2,1,1，那么随机到这三个口上的概率分别为1/2，1/4，1/4。\n\n"
        text += "事件的触发方式：\n"
        text += "  事件的触发优先于指令的触发，由事件决定是否要触发指令下的口上输出与数值结算。\n"
        text += "  ①跳过指令，适用于大部分情况。比如写一个玩家和NPC吃饭的事件，那么玩家点击吃饭后，应当只发生事件的吃饭，只出现事件的文本和数值结算，不应再出现指令原本的口上文本和结算。所以在这种事件类型里，应当把指令本身的相关处理全部跳过。\n"
        text += "  ②指令前置，通常适用于移动触发的事件。比如写一个玩家或NPC进入房间的事件，那么此时应当先结算指令，让人物先移动过去，然后再触发事件。这种事件如果把指令跳过了，那就变成在房间外面触发了房间内的事件了，显然是不合理的。\n"
        text += "  ③指令后置，同理，先触发事件，再结算指令。\n\n"
        text += "带选项的父子事件：\n"
        text += "  带分支选项的事件被称为父子事件。选项之前的为一个单独的父事件，每个选项各自为一个单独的子事件。父子事件的构成需要满足以下三个条件：\n"
        text += "  ①父事件的结算中需要有一个[系统状态]里的【开启子选项面板】。\n"
        text += "  ②子事件的前提需要在和父事件一样的基础上，再额外加一个[系统状态]里的【选项的子事件】。\n"
        text += "  ③子事件的文本分为两个部分，分别是选项上显示的文本，以及点击选项之后出来的文本。这两个文本都写在子事件的文本里，中间用|分隔开。\n"
        text_edit.setText(text)
        text_edit.setReadOnly(True)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        font_metrics = QFontMetrics(text_edit.font())
        text_edit.setFixedWidth(1000)
        line_count = text.count('\n') + 1
        text_edit.setFixedHeight(font_metrics.lineSpacing() * line_count * 1.5)

        layout = QVBoxLayout(dialog)
        layout.addWidget(text_edit)
        dialog.exec_()
