from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtGui import QFont, QAction
from PySide6.QtCore import Qt
import cache_control


class ItemTextEdit(QWidget):
    """文本编辑框主体"""

    def __init__(self):
        """初始化文本编辑框主体"""
        super(ItemTextEdit, self).__init__()
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        label_layout = QVBoxLayout()
        # 加入标题
        label = QLabel()
        label.setText("文本编辑")
        label_layout.addWidget(label)
        # 加入保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save)
        label_layout.addWidget(self.save_button)
        # 加入文本编辑框
        self.now_text = ""
        self.label_text = QTextEdit(self.now_text)
        label_layout.addWidget(self.label_text)
        self.setLayout(label_layout)

        # 创建右键菜单
        self.right_click_menu = QMenu(self)
        # 创建菜单项
        self.create_right_click_menu()
        # 将右键菜单绑定到文本编辑框上
        self.label_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_text.customContextMenuRequested.connect(self.show_right_click_menu)

    def create_right_click_menu(self):
        """创建右键菜单"""
        menu_items = [
            {"text": "插入玩家名字", "slot": lambda: self.insert_text('{Name}')},
            {"text": "插入玩家的交互对象名字", "slot": lambda: self.insert_text('{TargetName}')},
            {"text": "插入当前场景名字", "slot": lambda: self.insert_text('{SceneName}')},
            {"text": "插入当前食物名字", "slot": lambda: self.insert_text('{FoodName}')},
            {"text": "插入当前书籍名字", "slot": lambda: self.insert_text('{BookName}')},
            {"text": "插入玩家的交互对象的胸衣名字", "slot": lambda: self.insert_text('{TagetBraName}')},
            {"text": "插入玩家的交互对象的裙子名字", "slot": lambda: self.insert_text('{TagetSkiName}')},
            {"text": "插入玩家的交互对象的内裤名字", "slot": lambda: self.insert_text('{TagetPanName}')},
            {"text": "插入玩家的交互对象的袜子名字", "slot": lambda: self.insert_text('{TagetSocName}')},
        ]
        for item in menu_items:
            action = QAction(item["text"], self)
            action.triggered.connect(item["slot"])
            self.right_click_menu.addAction(action)

    def show_right_click_menu(self, pos):
        """显示右键菜单"""
        self.right_click_menu.exec_(self.label_text.mapToGlobal(pos))

    def insert_text(self, text):
        """右键菜单插入文本"""
        self.label_text.insertPlainText(text)

    def update(self):
        """更新文本内容"""
        if cache_control.now_edit_type_flag == 1:
            self.now_text = cache_control.now_event_data[cache_control.now_select_id].text
        else:
            self.now_text = cache_control.now_talk_data[cache_control.now_select_id].text
        self.label_text.setText(self.now_text)
    
    def save(self):
        """保存文本内容"""
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].text = self.label_text.toPlainText()
        else:
            cache_control.now_talk_data[cache_control.now_select_id].text = self.label_text.toPlainText()

    def show_right_click_menu(self, pos):
        """显示右键菜单"""
        self.right_click_menu.exec_(self.label_text.mapToGlobal(pos))

    def insert_text1(self):
        """插入文本1"""
        self.label_text.insertPlainText('{Name}')

    def insert_text2(self):
        """插入文本2"""
        self.label_text.insertPlainText('{TargetName}')

    def insert_text3(self):
        """插入文本3"""
        self.label_text.insertPlainText('{SceneName}')

    def insert_text4(self):
        """插入文本4"""
        self.label_text.insertPlainText('{FoodName}')

    def insert_text5(self):
        """插入文本5"""
        self.label_text.insertPlainText('{BookName}')
