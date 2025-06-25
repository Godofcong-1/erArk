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
        # 创建四个一级菜单
        chara_menu = self.right_click_menu.addMenu("角色名")
        chara_nick_menu = self.right_click_menu.addMenu("角色称呼")
        common_text_menu = self.right_click_menu.addMenu("纸娃娃文本")
        clothing_menu = self.right_click_menu.addMenu("服装名")
        scene_menu = self.right_click_menu.addMenu("场景名")
        food_menu = self.right_click_menu.addMenu("食物名")
        other_menu = self.right_click_menu.addMenu("其他")
        draw_menu = self.right_click_menu.addMenu("绘制")

        # 角色名菜单项
        chara_items = [
            {"text": "文本触发者名字", "slot": lambda: self.insert_text('{Name}')},
            {"text": "文本触发者的交互对象名字", "slot": lambda: self.insert_text('{TargetName}')},
            {"text": "玩家名字", "slot": lambda: self.insert_text('{PlayerName}')},
            {"text": "玩家的交互对象的名字", "slot": lambda: self.insert_text('{PlayerTargetName}')},
            {"text": "当前场景中随机一名角色名字", "slot": lambda: self.insert_text('{SceneOneCharaName}')},
            {"text": "移动目标场景中随机一名角色名字", "slot": lambda: self.insert_text('{TargetOneCharaName}')},
            {"text": "移动出发场景中随机一名角色名字", "slot": lambda: self.insert_text('{SrcOneCharaName}')},
            {"text": "H行为被打断时的闯入者的名字", "slot": lambda: self.insert_text('{HInterruptCharaName}')},
        ]

        # 角色称呼菜单项
        chara_nick_items = [
            {"text": "玩家对触发者的称呼", "slot": lambda: self.insert_text('{NickName}')},
            {"text": "触发者对玩家的称呼", "slot": lambda: self.insert_text('{NickNameToPl}')},
            {"text": "玩家对交互对象的称呼", "slot": lambda: self.insert_text('{TargetNickName}')},
            {"text": "交互对象对玩家的称呼", "slot": lambda: self.insert_text('{TargetNickNameToPl}')},
            {"text": "触发者与交互对象中非玩家的那个对玩家的称呼", "slot": lambda: self.insert_text('{PlayerNickName}')},
        ]

        # 纸娃娃文本菜单项
        common_text_items = [
            {"text": "玩家阴茎描述长句", "slot": lambda: self.insert_text('{penis}')},
            {"text": "玩家阴茎描述短词", "slot": lambda: self.insert_text('{penis_s}')},
            {"text": "玩家交互对象口腔描述长句", "slot": lambda: self.insert_text('{mouth}')},
            {"text": "玩家交互对象口腔描述短句", "slot": lambda: self.insert_text('{mouth_s}')},
            {"text": "玩家交互对象头发描述长句", "slot": lambda: self.insert_text('{hair}')},
            {"text": "玩家交互对象头发描述短词", "slot": lambda: self.insert_text('{hair_s}')},
            {"text": "玩家交互对象脸部描述长句", "slot": lambda: self.insert_text('{face}')},
            {"text": "玩家交互对象脸部描述短词", "slot": lambda: self.insert_text('{face_s}')},
            {"text": "玩家交互对象胸部描述短词", "slot": lambda: self.insert_text('{breast_s}')},
            {"text": "玩家交互对象腋部描述短词", "slot": lambda: self.insert_text('{armpit_s}')},
            {"text": "玩家交互对象手部描述短词", "slot": lambda: self.insert_text('{hands_s}')},
            {"text": "玩家交互对象阴道描述短词", "slot": lambda: self.insert_text('{vagina_s}')},
            {"text": "玩家交互对象子宫描述短词", "slot": lambda: self.insert_text('{womb_s}')},
            {"text": "玩家交互对象后穴描述短词", "slot": lambda: self.insert_text('{anal_s}')},
            {"text": "玩家交互对象尿道描述短词", "slot": lambda: self.insert_text('{urethra_s}')},
            {"text": "玩家交互对象腿部描述短词", "slot": lambda: self.insert_text('{legs_s}')},
            {"text": "玩家交互对象腿部描述短词", "slot": lambda: self.insert_text('{feet_s}')},
        ]

        # 服装名菜单项
        clothing_items = [
            {"text": "玩家的交互对象的胸衣名字", "slot": lambda: self.insert_text('{TagetBraName}')},
            {"text": "玩家的交互对象的裙子名字", "slot": lambda: self.insert_text('{TagetSkiName}')},
            {"text": "玩家的交互对象的内裤名字", "slot": lambda: self.insert_text('{TagetPanName}')},
            {"text": "玩家的交互对象的袜子名字", "slot": lambda: self.insert_text('{TagetSocName}')},
            {"text": "自己穿着的内裤名字", "slot": lambda: self.insert_text('{PanName}')},
            {"text": "自己穿着的袜子名字", "slot": lambda: self.insert_text('{SocName}')},
        ]

        # 场景名菜单项
        scene_items = [
            {"text": "当前场景名字", "slot": lambda: self.insert_text('{SceneName}')},
            {"text": "移动目标场景名字", "slot": lambda: self.insert_text('{TargetSceneName}')},
            {"text": "移动出发场景名字", "slot": lambda: self.insert_text('{SrcSceneName}')},
        ]

        # 食物名菜单项
        food_items = [
            {"text": "当前行为中食物名字", "slot": lambda: self.insert_text('{FoodName}')},
            {"text": "食物制作时间", "slot": lambda: self.insert_text('{MakeFoodTime}')},
            {"text": "当前背包里所有食物名字", "slot": lambda: self.insert_text('{AllFoodName}')},
        ]

        # 其他名菜单项
        other_items = [
            {"text": "当前书籍名字", "slot": lambda: self.insert_text('{BookName}')},
            {"text": "当前行为榨出母乳的毫升数", "slot": lambda: self.insert_text('{MilkMl}')},
        ]

        # 绘制菜单项
        draw_items = [
            {"text": "跳过每行确认，直接显示到最后一行", "slot": lambda: self.insert_text('{Jump}')},
        ]

        # 将菜单项添加到对应的一级菜单中
        menu_items = [
            (chara_menu, chara_items),
            (chara_nick_menu, chara_nick_items),
            (common_text_menu, common_text_items),
            (clothing_menu, clothing_items),
            (scene_menu, scene_items),
            (food_menu, food_items),
            (other_menu, other_items),
            (draw_menu, draw_items),
        ]

        # 遍历菜单项，添加到对应的菜单中
        for menu, items in menu_items:
            for item in items:
                action = QAction(item["text"], self)
                action.triggered.connect(item["slot"])
                menu.addAction(action)

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
        if cache_control.now_edit_type_flag == 1 and cache_control.now_select_id in cache_control.now_event_data:
            cache_control.now_event_data[cache_control.now_select_id].text = now_text
        elif cache_control.now_edit_type_flag == 0 and cache_control.now_select_id in cache_control.now_talk_data:
            cache_control.now_talk_data[cache_control.now_select_id].text = now_text
        # 检测英文双引号，直接删除，防止csv文件解析出错
        now_text = now_text.replace("\"", "")

    def show_right_click_menu(self, pos):
        """显示右键菜单"""
        self.right_click_menu.exec_(self.label_text.mapToGlobal(pos))
