import uuid
from PySide6.QtWidgets import QListWidget, QMenuBar, QWidgetAction, QListWidgetItem, QAbstractItemView, QPushButton, QHBoxLayout, QWidget, QTextEdit, QLabel, QGridLayout, QMenu, QCheckBox, QSizePolicy, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor, QColor
from ui.list_item import ListItem
import cache_control
import game_type


class CharaList(QWidget):
    """表单主体"""

    def __init__(self):
        """初始化表单主体"""
        super(CharaList, self).__init__()
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignTop)  # 设置布局对齐方式为顶部对齐

        # 条目列表
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)

        self.top_layouts = [QHBoxLayout() for _ in range(12)]
        for layout in self.top_layouts:
            layout.setAlignment(Qt.AlignLeft)  # 设置布局对齐方式为左对齐

        # 说明文本
        labels_text = ["编号", "姓名", "性别", "职业", "种族", "势力", "初始HP", "初始MP", "信物", "人物介绍", "字体颜色"]
        labels = [self.create_label(text) for text in labels_text]

        self.chara_id_text_edit = self.create_text_edit("0", self.update_adv_id)
        self.chara_name_text_edit = self.create_text_edit("0", self.update_chara_name)

        self.chara_sex_combo_box = QComboBox()
        self.chara_sex_combo_box.addItems("女")
        self.profession_combo_box = QComboBox()
        for i in cache_control.profession_data:
            profession_name = cache_control.profession_data[i]
            self.profession_combo_box.addItems([profession_name])
        self.race_combo_box = QComboBox()
        for i in cache_control.race_data:
            race_name = cache_control.race_data[i]
            self.race_combo_box.addItems([race_name])

        # 上方布局
        for i, label in enumerate(labels):
            self.top_layouts[i].addWidget(label)
            if i == 0:
                self.top_layouts[i].addWidget(self.chara_id_text_edit)
            elif i == 1:
                self.top_layouts[i].addWidget(self.chara_name_text_edit)
            elif i == 2:
                self.top_layouts[i].addWidget(self.chara_sex_combo_box)
            elif i == 3:
                self.top_layouts[i].addWidget(self.profession_combo_box)
            elif i == 4:
                self.top_layouts[i].addWidget(self.race_combo_box)

        # 总布局
        for i, layout in enumerate(self.top_layouts):
            self.layout.addLayout(layout, i, 0)

    def create_label(self, text):
        """创建一个带有固定宽度和大小策略的标签"""
        label = QLabel(text)
        label.setFixedWidth(100)  # 设置固定宽度
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)  # 设置大小策略
        return label

    def create_text_edit(self, initial_text, update_function):
        """创建一个文本编辑框"""
        text_edit = QTextEdit(initial_text)
        text_edit.textChanged.connect(update_function)
        text_edit.setFixedHeight(32)
        text_edit.setFixedWidth(200)
        return text_edit

    def update_adv_id(self):
        """根据文本编辑框更新当前的角色id"""
        now_adv_id = self.chara_id_text_edit.toPlainText()
        cache_control.now_chara_data.AdvNpc = now_adv_id

    def update_chara_name(self):
        """根据文本编辑框更新当前的角色姓名"""
        now_chara_name = self.chara_name_text_edit.toPlainText()
        cache_control.now_chara_data.Name = now_chara_name

    def update_chara_sex(self):
        """根据文本编辑框更新当前的角色性别"""
        now_chara_sex = 1
        cache_control.now_chara_data.Sex = now_chara_sex

    def update_profession(self):
        """根据文本编辑框更新当前的角色职业"""
        now_profession = self.profession_combo_box.currentIndex()
        cache_control.now_chara_data.Profession = now_profession

    def update_race(self):
        """根据文本编辑框更新当前的角色种族"""
        now_race = self.race_combo_box.currentIndex()
        cache_control.now_chara_data.Race = now_race

    def update(self):
        """更新"""
        now_AdvNpc = cache_control.now_chara_data.AdvNpc
        self.chara_id_text_edit.setText(str(now_AdvNpc))
        now_Name = cache_control.now_chara_data.Name
        self.chara_name_text_edit.setText(str(now_Name))
        # now_chara_sex = cache_control.now_chara_data.Sex
        # self.chara_sex_text_edit.setText(str(now_chara_sex))
        now_profession = cache_control.now_chara_data.Profession
        self.profession_combo_box.setCurrentIndex(now_profession)
        now_race = cache_control.now_chara_data.Race
        self.race_combo_box.setCurrentIndex(now_race)