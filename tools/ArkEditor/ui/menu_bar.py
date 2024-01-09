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
        self.talk_introduce_action = QAction("口上说明", self)
        self.talk_introduce_action.triggered.connect(self.show_talk_introduce)
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
        self.event_introduce_action.triggered.connect(self.show_event_introduce)
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
        chara_menu = QMenu("角色csv", self)
        self.new_chara_file_action = QWidgetAction(self)
        self.new_chara_file_action.setText("新建角色csv文件")
        self.select_chara_file_action = QWidgetAction(self)
        self.select_chara_file_action.setText("读取角色csv文件")
        self.save_chara_action = QWidgetAction(self)
        self.save_chara_action.setText("保存角色csv        Ctrl+S")
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        chara_menu.addActions(
            [
                self.new_chara_file_action,
                self.select_chara_file_action,
                self.save_chara_action,
            ]
        )
        chara_menu.setFont(self.font)
        # self.addMenu(chara_menu)


    def show_talk_introduce(self):
        """显示只读文本框的对话框"""
        dialog = QDialog(self)
        text_edit = QTextEdit(dialog)
        text_edit.setFont(self.font)
        text = "本编辑器可用于编辑游戏 erArk 的口上文件。\n\n"
        text += "流程简述：\n"
        text += "  ①创建/读取对应的文件。\n  ②在左侧的条目栏中新建/选择一个条目。\n  ③在左上选择触发的指令，在右上编辑前提，在右下编辑条目的文本。\n  ④保存\n\n"
        text += "\nUI介绍：\n"
        text += "  ①左边，口上的条目列表。这里处理每条口上的序号、由什么指令触发、是否限定某角色触发。\n"
        text += "  ②右上，前提选择栏。这里处理口上的触发逻辑，使用【前提】的形式来实现代码的处理，同一口上的所有前提按逻辑“和”来运算。\n"
        text += "  ③右下，文本编辑框。这里处理口上的文本，包括人物名、地名之类代码文字。\n\n"
        text += "\n简单的口上逻辑：\n"
        text += "  绝大部分的情况下，都是【玩家】对【某数据的】【某NPC】使用【某指令】。\n"
        text += "  例，【玩家】对【1000好感以上的】【阿米娅】使用【聊天】时文本为【你好】。\n"
        text += "  此时，指令=[聊天]、角色id=[1]（阿米娅id）、前提=[玩家触发+交互对象好感＞1000]、文本内容=[你好]。\n\n"
        text += "\n\n\n（如果你真的需要理解的话，再来看下面这段）\n\n详细的口上逻辑：\n"
        text += "  ①在玩家/NPC使用一个指令时，会搜寻【本角色和通用角色的】【本指令下的】所有口上（如果是对他人使用，则还会搜索【对象角色的】），这里将搜到的所有口上定义为A。\n"
        text += "  ②遍历A里每个口上的前提，查看是否满足条件。如果某一条口上的所有前提都被满足，则根据前提量计一个权重大小，该口上进入选择池。这里将选择池里的所有口上定义为B，显然，B是A的一个子集。\n"
        text += "  ③在B中根据权重比例来随机选择一个口上作为当前的结果口上，假如B中有3个口上，权重分别为2,1,1，那么随机到这三个口上的概率分别为1/2，1/4，1/4。\n\n"
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

    def show_event_introduce(self):
        """显示只读文本框的对话框"""
        dialog = QDialog(self)
        text_edit = QTextEdit(dialog)
        text_edit.setFont(self.font)
        text = "本编辑器可用于编辑游戏 erArk 的事件文件。\n\n"
        text += "请先阅读并理解口上的部分后，再来看本部分\n"
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
