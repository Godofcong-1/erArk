import uuid
from PySide6.QtWidgets import QVBoxLayout, QMenuBar, QWidgetAction, QListWidgetItem, QSplitter, QPushButton, QHBoxLayout, QWidget, QTextEdit, QLabel, QGridLayout, QMenu, QCheckBox, QSizePolicy, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
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

        self.first_layouts = [QHBoxLayout() for _ in range(14)]
        for layout in self.first_layouts:
            layout.setAlignment(Qt.AlignLeft)  # 设置布局对齐方式为左对齐
        self.second_layouts = [QHBoxLayout() for _ in range(4)]
        for layout in self.second_layouts:
            layout.setAlignment(Qt.AlignLeft)  # 设置布局对齐方式为左对齐

        # 说明文本
        labels_text_1 = ["编号", "姓名", "性别", "职业", "种族", "势力", "出身地", "初始HP", "初始MP", "初始宿舍", "信物", "人物介绍", "字体颜色", "额外说明"]
        labels_1 = [self.create_label(text) for text in labels_text_1]
        labels_text_2 = ["能力", "经验", "素质", "服装"]
        labels_2 = [self.create_label(text) for text in labels_text_2]


        # 新增介绍文本
        intro_labels_text = ["HP（体力）基础1500，可上下浮动最多1000\nMP（气力）基础1000，可上下浮动最多1000\n初始宿舍默认为无，自动分配到宿舍，有特殊需求的请专门联系作者"]
        intro_labels = [self.create_label(text, 1000) for text in intro_labels_text]

        self.chara_id_text_edit = self.create_text_edit("0")
        self.chara_name_text_edit = self.create_text_edit("0")
        self.chara_hp_text_edit = self.create_text_edit("0")
        self.chara_mp_text_edit = self.create_text_edit("0")
        self.chara_dormitory_text_edit = self.create_text_edit("0")
        self.chara_token_text_edit = self.create_text_edit("0")
        self.chara_introduce_text_edit = self.create_text_edit("0")
        self.chara_textcolor_text_edit = self.create_text_edit("0")

        self.chara_sex_combo_box = self.create_qcombo_box(["女"])
        self.profession_combo_box = self.create_qcombo_box([cache_control.profession_data[i] for i in cache_control.profession_data])
        self.race_combo_box = self.create_qcombo_box([cache_control.race_data[i] for i in cache_control.race_data])
        self.nation_combo_box = self.create_qcombo_box([cache_control.nation_data[i] for i in cache_control.nation_data])
        self.birthplace_combo_box = self.create_qcombo_box([cache_control.birthplace_data[i] for i in cache_control.birthplace_data])

        self.ability_widget = MenuWidget()

        # 上方布局
        for i, label in enumerate(labels_1):
            self.first_layouts[i].addWidget(label)
            if i == 0:
                self.first_layouts[i].addWidget(self.chara_id_text_edit)
            elif i == 1:
                self.first_layouts[i].addWidget(self.chara_name_text_edit)
            elif i == 2:
                self.first_layouts[i].addWidget(self.chara_sex_combo_box)
            elif i == 3:
                self.first_layouts[i].addWidget(self.profession_combo_box)
            elif i == 4:
                self.first_layouts[i].addWidget(self.race_combo_box)
            elif i == 5:
                self.first_layouts[i].addWidget(self.nation_combo_box)
            elif i == 6:
                self.first_layouts[i].addWidget(self.birthplace_combo_box)
            elif i == 7:
                self.first_layouts[i].addWidget(self.chara_hp_text_edit)
            elif i == 8:
                self.first_layouts[i].addWidget(self.chara_mp_text_edit)
            elif i == 9:
                self.first_layouts[i].addWidget(self.chara_dormitory_text_edit)
            elif i == 10:
                self.first_layouts[i].addWidget(self.chara_token_text_edit)
            elif i == 11:
                self.first_layouts[i].addWidget(self.chara_introduce_text_edit)
            elif i == 12:
                self.first_layouts[i].addWidget(self.chara_textcolor_text_edit)
            elif i == 13:
                self.first_layouts[i].addWidget(intro_labels[0])
            elif i == 14:
                self.first_layouts[i].addWidget(self.ability_widget)

        for i, label in enumerate(labels_2):
            self.second_layouts[i].addWidget(label)
            # if i == 0:
            #     self.first_layouts[i].addWidget(self.ability_widget)

        # 创建确定按钮和重置按钮
        self.apply_button = QPushButton("应用并保存")
        self.reset_button = QPushButton("重置")

        # 连接按钮的点击信号到相应的槽函数
        self.apply_button.clicked.connect(self.apply_changes)
        self.reset_button.clicked.connect(self.reset_values)

        # 总布局
        for i, layout in enumerate(self.first_layouts):
            self.layout.addLayout(layout, i, 0)
        for i, layout in enumerate(self.second_layouts):
            self.layout.addLayout(layout, i, 1)

        # 将按钮添加到布局中
        self.layout.addWidget(self.apply_button, 18, 0)
        self.layout.addWidget(self.reset_button, 19, 0)

    def create_label(self, text, width = 100):
        """创建一个带有固定宽度和大小策略的标签"""
        label = QLabel(text)
        label.setFixedWidth(width)  # 设置固定宽度
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)  # 设置大小策略
        return label

    def create_text_edit(self, initial_text):
        """创建一个文本编辑框"""
        text_edit = QTextEdit(initial_text)
        text_edit.setFixedHeight(30)
        text_edit.setFixedWidth(200)
        return text_edit

    def create_qcombo_box(self, initial_text_list):
        """创建一个下拉框"""
        combo_box = QComboBox()
        # combo_box.setFixedHeight(30)
        # combo_box.setFixedWidth(200)
        # combo_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        for initial_text in initial_text_list:
            combo_box.addItem(initial_text)
        return combo_box

    def apply_changes(self):
        """应用更改"""
        self.update_adv_id()
        self.update_chara_name()
        self.update_chara_sex()
        self.update_profession()
        self.update_race()
        self.update_nation()
        self.update_birthplace()
        self.update_chara_hp()
        self.update_chara_mp()
        self.update_chara_dormitory()
        self.update_chara_token()
        self.update_chara_introduce()
        self.update_chara_textcolor()

    def reset_values(self):
        """重置值"""
        self.update()

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

    def update_nation(self):
        """根据文本编辑框更新当前的角色势力"""
        now_nation = self.nation_combo_box.currentIndex()
        cache_control.now_chara_data.Nation = now_nation

    def update_birthplace(self):
        """根据文本编辑框更新当前的角色出身地"""
        now_birthplace = self.birthplace_combo_box.currentIndex()
        cache_control.now_chara_data.Birthplace = now_birthplace

    def update_chara_hp(self):
        """根据文本编辑框更新当前的角色初始体力"""
        now_chara_hp = self.chara_hp_text_edit.toPlainText()
        cache_control.now_chara_data.Hp = now_chara_hp

    def update_chara_mp(self):
        """根据文本编辑框更新当前的角色初始气力"""
        now_chara_mp = self.chara_mp_text_edit.toPlainText()
        cache_control.now_chara_data.Mp = now_chara_mp

    def update_chara_dormitory(self):
        """根据文本编辑框更新当前的角色初始宿舍"""
        now_chara_dormitory = self.chara_dormitory_text_edit.toPlainText()
        cache_control.now_chara_data.Dormitory = now_chara_dormitory

    def update_chara_token(self):
        """根据文本编辑框更新当前的角色信物"""
        now_chara_token = self.chara_token_text_edit.toPlainText()
        cache_control.now_chara_data.Token = now_chara_token

    def update_chara_introduce(self):
        """根据文本编辑框更新当前的角色介绍"""
        now_chara_introduce = self.chara_introduce_text_edit.toPlainText()
        cache_control.now_chara_data.Introduce_1 = now_chara_introduce

    def update_chara_textcolor(self):
        """根据文本编辑框更新当前的角色字体颜色"""
        now_chara_textcolor = self.chara_textcolor_text_edit.toPlainText()
        cache_control.now_chara_data.TextColor = now_chara_textcolor

        # 设置字体颜色
        palette = self.chara_textcolor_text_edit.palette()
        palette.setColor(QPalette.Text, QColor(now_chara_textcolor))
        # 设置背景颜色
        palette.setColor(QPalette.Base, "#000")

        self.chara_textcolor_text_edit.setPalette(palette)

    def update(self):
        """更新"""
        now_AdvNpc = cache_control.now_chara_data.AdvNpc
        self.chara_id_text_edit.setText(str(now_AdvNpc))
        now_Name = cache_control.now_chara_data.Name
        self.chara_name_text_edit.setText(str(now_Name))
        now_chara_hp = cache_control.now_chara_data.Hp
        self.chara_hp_text_edit.setText(str(now_chara_hp))
        now_chara_mp = cache_control.now_chara_data.Mp
        self.chara_mp_text_edit.setText(str(now_chara_mp))
        now_chara_dormitory = cache_control.now_chara_data.Dormitory
        self.chara_dormitory_text_edit.setText(str(now_chara_dormitory))
        now_chara_token = cache_control.now_chara_data.Token
        self.chara_token_text_edit.setText(str(now_chara_token))
        now_chara_introduce = cache_control.now_chara_data.Introduce_1
        self.chara_introduce_text_edit.setText(str(now_chara_introduce))
        now_chara_textcolor = cache_control.now_chara_data.TextColor
        self.chara_textcolor_text_edit.setText(str(now_chara_textcolor))
        # now_chara_sex = cache_control.now_chara_data.Sex
        # self.chara_sex_text_edit.setText(str(now_chara_sex))
        now_profession = cache_control.now_chara_data.Profession
        self.profession_combo_box.setCurrentIndex(now_profession)
        now_race = cache_control.now_chara_data.Race
        self.race_combo_box.setCurrentIndex(now_race)
        now_nation = cache_control.now_chara_data.Nation
        self.nation_combo_box.setCurrentIndex(now_nation)
        now_birthplace = cache_control.now_chara_data.Birthplace
        self.birthplace_combo_box.setCurrentIndex(now_birthplace)
        self.apply_changes()



class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.addButton = QPushButton("添加", self)
        self.addButton.clicked.connect(self.addItems)
        self.layout.addWidget(self.addButton)

        self.removeButton = QPushButton("删除", self)
        self.removeButton.clicked.connect(self.removeItems)
        self.layout.addWidget(self.removeButton)

        self.items = []

    def addItems(self):
        comboBox = QComboBox(self)
        textEdit = QTextEdit(self)

        # 赋予下拉框初始值
        initial_text_list = [cache_control.ability_data[i] for i in cache_control.ability_data]
        for initial_text in initial_text_list:
            comboBox.addItem(initial_text)

        # 设定文本编辑框的大小
        textEdit.setFixedHeight(30)
        textEdit.setFixedWidth(200)


        self.layout.addWidget(comboBox)
        self.layout.addWidget(textEdit)

        self.items.append((comboBox, textEdit))

    def removeItems(self):
        if self.items:
            comboBox, textEdit = self.items.pop()

            comboBox.deleteLater()
            textEdit.deleteLater()
