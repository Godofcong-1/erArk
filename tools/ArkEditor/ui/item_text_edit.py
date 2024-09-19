from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel, QPushButton, QMenu, QHBoxLayout
from PySide6.QtGui import QFont, QAction
from PySide6.QtCore import Qt
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class ItemTextEdit(QWidget):
    """文本编辑框主体"""

    def __init__(self):
        """初始化文本编辑框主体"""
        super(ItemTextEdit, self).__init__()
        self.font = font
        self.setFont(self.font)
        label_layout = QVBoxLayout()
        # 加入标题
        self.info_label = QLabel()
        self.info_label.setText("文本编辑")
        label_layout.addWidget(self.info_label)
        # 加入保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save)
        # 加入文本触发者名字按钮
        self.insert_name_button = QPushButton("插入文本触发者名字")
        self.insert_name_button.clicked.connect(lambda: self.insert_text('{Name}'))
        # 加入文本触发者的交互对象名字按钮
        self.insert_target_name_button = QPushButton("插入文本触发者的交互对象名字")
        self.insert_target_name_button.clicked.connect(lambda: self.insert_text('{TargetName}'))
        # 加入玩家名字按钮
        self.insert_player_name_button = QPushButton("插入玩家名字")
        self.insert_player_name_button.clicked.connect(lambda: self.insert_text('{PlayerName}'))
        # 加入一行文本提示
        self.max_length = 0
        self.info_label = QLabel()
        self.info_label.setText(f"右键可浏览全部代码文本进行插入，当前最长行字符总长度为{self.max_length}，建议不要超过100")
        # 上述三个按钮的布局变成横向
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.insert_name_button)
        button_layout.addWidget(self.insert_target_name_button)
        button_layout.addWidget(self.insert_player_name_button)
        label_layout.addLayout(button_layout)
        label_layout.addWidget(self.info_label)
        # 加入文本编辑框
        self.now_text = ""
        self.label_text = QTextEdit(self.now_text)
        label_layout.addWidget(self.label_text)
        self.setLayout(label_layout)

        # 创建右键菜单
        self.right_click_menu = QMenu(self)
        self.right_click_menu.setFont(self.font)
        # 创建菜单项
        self.create_right_click_menu()
        # 将右键菜单绑定到文本编辑框上
        self.label_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_text.customContextMenuRequested.connect(self.show_right_click_menu)

    def create_right_click_menu(self):
        """创建右键菜单"""
        menu_items = [
            {"text": "插入文本触发者名字", "slot": lambda: self.insert_text('{Name}')},
            {"text": "插入文本触发者的交互对象名字", "slot": lambda: self.insert_text('{TargetName}')},
            {"text": "插入玩家对触发者的称呼", "slot": lambda: self.insert_text('{NickName}')},
            {"text": "插入触发者对玩家的称呼", "slot": lambda: self.insert_text('{NickNameToPl}')},
            {"text": "插入玩家对交互对象的称呼", "slot": lambda: self.insert_text('{TargetNickName}')},
            {"text": "插入交互对象对玩家的称呼", "slot": lambda: self.insert_text('{TargetNickNameToPl}')},
            {"text": "插入玩家名字", "slot": lambda: self.insert_text('{PlayerName}')},
            {"text": "插入当前行为中食物名字", "slot": lambda: self.insert_text('{FoodName}')},
            {"text": "插入食物制作时间", "slot": lambda: self.insert_text('{MakeFoodTime}')},
            {"text": "插入当前背包里所有食物名字", "slot": lambda: self.insert_text('{AllFoodName}')},
            {"text": "插入当前书籍名字", "slot": lambda: self.insert_text('{BookName}')},
            {"text": "插入当前行为榨出母乳的毫升数", "slot": lambda: self.insert_text('{MilkMl}')},
            {"text": "插入H行为被打断时的闯入者的名字", "slot": lambda: self.insert_text('{HInterruptCharaName}')},
            {"text": "插入当前场景名字", "slot": lambda: self.insert_text('{SceneName}')},
            {"text": "插入当前场景中随机一名角色名字", "slot": lambda: self.insert_text('{SceneOneCharaName}')},
            {"text": "插入移动目标场景名字", "slot": lambda: self.insert_text('{TargetSceneName}')},
            {"text": "插入移动目标场景中随机一名角色名字", "slot": lambda: self.insert_text('{TargetOneCharaName}')},
            {"text": "插入移动出发场景名字", "slot": lambda: self.insert_text('{SrcSceneName}')},
            {"text": "插入移动出发场景中随机一名角色名字", "slot": lambda: self.insert_text('{SrcOneCharaName}')},
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
        elif cache_control.now_edit_type_flag == 0:
            self.now_text = cache_control.now_talk_data[cache_control.now_select_id].text
        # 将换行符"\n"换成真正的换行
        self.now_text = self.now_text.replace("\\n", "\n")
        self.label_text.setText(self.now_text)
        # 计算最长行长度
        max_length = 0
        for line in self.now_text.split("\n"):
            if len(line) > max_length:
                max_length = len(line)
        self.max_length = max_length
        # 更新提示文本
        self.info_label.setText(f"右键菜单可插入更多文本，当前最长行字符总长度为{self.max_length}，建议不要超过100")

    def save(self):
        """保存文本内容"""
        now_text = self.label_text.toPlainText()
        # 检测里面的","，换成"，"，防止csv文件解析出错
        now_text = now_text.replace(",", "，")
        # 检测换行符，换成"\n"，防止csv文件解析出错
        now_text = now_text.replace("\n", "\\n")
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].text = now_text
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].text = now_text
        # 检测英文双引号，直接删除，防止csv文件解析出错
        now_text = now_text.replace("\"", "")

    def show_right_click_menu(self, pos):
        """显示右键菜单"""
        self.right_click_menu.exec_(self.label_text.mapToGlobal(pos))
