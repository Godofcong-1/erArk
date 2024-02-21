from PySide6.QtWidgets import QVBoxLayout, QSplitter, QPushButton, QHBoxLayout, QWidget, QTextEdit, QLabel, QSizePolicy, QComboBox
from PySide6.QtGui import QFont, QPalette, QColor
import cache_control


class CharaList(QWidget):
    """表单主体"""

    def __init__(self):
        """初始化表单主体"""
        super(CharaList, self).__init__()
        self.layout = QVBoxLayout(self)

        # 分割窗口
        self.splitter = QSplitter(self)

        # 左右两列
        self.leftColumn = QWidget(self)
        self.rightColumn = QWidget(self)
        self.leftLayout = QVBoxLayout(self.leftColumn)
        self.rightLayout = QVBoxLayout(self.rightColumn)

        # 条目列表
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)

        self.first_layouts = [QHBoxLayout() for _ in range(14)]
        self.second_layouts = [QHBoxLayout() for _ in range(5)]

        # 说明文本
        labels_text_1 = ["编号", "姓名", "性别", "职业", "种族", "势力", "出身地", "初始HP", "初始MP", "初始宿舍", "信物", "人物介绍", "字体颜色", "说明"]
        labels_1 = [self.create_label(text) for text in labels_text_1]
        labels_text_2 = ["能力", "经验", "素质", "服装", "说明"]
        labels_2 = [self.create_label(text) for text in labels_text_2]

        # 新增介绍文本
        intro_labels_text = []
        intro_labels_text.append("HP（体力）基础1500，可上下浮动最多1000\nMP（气力）基础1000，可上下浮动最多1000\n初始宿舍默认为无，自动分配到宿舍，有特殊需求的请联系作者\n字体颜色为16进制颜色代码，如#ffffff为白色")
        intro_labels_text.append("能力最高为8级，除极端人设外，一般初始能力最高不超过3级\n每1经验对应1次相应指令，除极端人设外，一般初始经验最高不超过200\n默认都有的基础素质是处女、A处女和无接吻经验，必选的素质有年龄素质，以及胸部、屁股、腿、脚四个部位的素质\n单个部位的服装可以有多个")
        intro_labels = [self.create_label(text, 700) for text in intro_labels_text]

        self.chara_id_text_edit = self.create_text_edit("0")
        self.chara_name_text_edit = self.create_text_edit("0")
        self.chara_hp_text_edit = self.create_text_edit("0")
        self.chara_mp_text_edit = self.create_text_edit("0")
        self.chara_dormitory_text_edit = self.create_text_edit("0")
        self.chara_token_text_edit = self.create_text_edit("0",height = 100)
        self.chara_introduce_text_edit = self.create_text_edit("0",height = 250)
        self.chara_textcolor_text_edit = self.create_text_edit("0")

        self.chara_sex_combo_box = self.create_qcombo_box(["女"])
        self.profession_combo_box = self.create_qcombo_box([cache_control.profession_data[i] for i in cache_control.profession_data])
        self.race_combo_box = self.create_qcombo_box([cache_control.race_data[i] for i in cache_control.race_data])
        self.nation_combo_box = self.create_qcombo_box([cache_control.nation_data[i] for i in cache_control.nation_data])
        self.birthplace_combo_box = self.create_qcombo_box([cache_control.birthplace_data[i] for i in cache_control.birthplace_data])

        self.ability_widget = MenuWidget(type_flag = 0)
        self.exprience_widget = MenuWidget(type_flag = 1)
        self.talent_widget = MenuWidget(type_flag = 2)
        self.clothing_widget = MenuWidget(type_flag = 3)
        # self.ability_widget.addItems()
        # self.exprience_widget.addItems()
        # self.talent_widget.addItems()
        # self.clothing_widget.addItems()

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

        for i, label in enumerate(labels_2):
            self.second_layouts[i].addWidget(label)
            if i == 0:
                self.second_layouts[i].addWidget(self.ability_widget)
            elif i == 1:
                self.second_layouts[i].addWidget(self.exprience_widget)
            elif i == 2:
                self.second_layouts[i].addWidget(self.talent_widget)
            elif i == 3:
                self.second_layouts[i].addWidget(self.clothing_widget)
            elif i == 4:
                self.second_layouts[i].addWidget(intro_labels[1])

        # 创建确定按钮和重置按钮
        self.apply_button = QPushButton("应用并保存")
        self.reset_button = QPushButton("重置")

        # 连接按钮的点击信号到相应的槽函数
        self.apply_button.clicked.connect(self.apply_changes)
        self.reset_button.clicked.connect(self.reset_values)

        # 总布局
        for layout in self.first_layouts:
            self.leftLayout.addLayout(layout)
        for layout in self.second_layouts:
            self.rightLayout.addLayout(layout)

        self.splitter.addWidget(self.leftColumn)
        self.splitter.addWidget(self.rightColumn)
        self.layout.addWidget(self.splitter)

        # 将按钮添加到布局中
        self.layout.addWidget(self.apply_button)
        self.layout.addWidget(self.reset_button)


    def resizeEvent(self, event):
        super(CharaList, self).resizeEvent(event)

        width = self.width() / 2
        self.splitter.setSizes([width, width])

    def create_label(self, text, width = 100):
        """创建一个带有固定宽度和大小策略的标签"""
        label = QLabel(text)
        label.setFixedWidth(width)  # 设置固定宽度
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)  # 设置大小策略
        return label

    def create_text_edit(self, initial_text, width = 400, height = 30):
        """创建一个文本编辑框"""
        text_edit = QTextEdit(initial_text)
        text_edit.setFixedHeight(height)
        text_edit.setFixedWidth(width)
        return text_edit

    def create_qcombo_box(self, initial_text_list):
        """创建一个下拉框"""
        combo_box = QComboBox()
        # combo_box.setFixedHeight(30)
        combo_box.setFixedWidth(400)
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
        self.update_chara_ability()
        self.update_chara_experience()
        self.update_chara_talent()
        self.update_chara_clothing()
        self.save_csv()

    def save_csv(self):
        """保存csv文件"""
        # 如果是使用的模板，那就新建一个文件
        if cache_control.now_file_path == "999_模板人物属性文件.csv":
            chara_id =  cache_control.now_chara_data.AdvNpc
            chara_name = cache_control.now_chara_data.Name
            cache_control.now_file_path = f"{chara_id}_{chara_name}.csv"

        if len(cache_control.now_file_path):
            # 通用开头
            out_data = ""
            out_data += "key,type,value,get_text,info\n"
            out_data += "键,类型,值,多语言化处理(前面的类型里int则为0,str则为1),备注\n"

            out_data += f"AdvNpc,int,{cache_control.now_chara_data.AdvNpc},0,角色编号\n"
            out_data += f"Name,str,{cache_control.now_chara_data.Name},1,角色姓名\n"
            out_data += f"Sex,int,{cache_control.now_chara_data.Sex},0,角色性别\n"
            out_data += f"Profession,int,{cache_control.now_chara_data.Profession},0,角色职业为{cache_control.profession_data[str(cache_control.now_chara_data.Profession)]}\n"
            out_data += f"Race,int,{cache_control.now_chara_data.Race},0,角色种族为{cache_control.race_data[str(cache_control.now_chara_data.Race)]}\n"
            out_data += f"Nation,int,{cache_control.now_chara_data.Nation},0,角色势力为{cache_control.nation_data[str(cache_control.now_chara_data.Nation)]}\n"
            out_data += f"Birthplace,int,{cache_control.now_chara_data.Birthplace},0,角色出身地为{cache_control.birthplace_data[str(cache_control.now_chara_data.Birthplace)]}\n"
            out_data += f"Hp,int,{cache_control.now_chara_data.Hp},0,角色初始体力\n"
            out_data += f"Mp,int,{cache_control.now_chara_data.Mp},0,角色初始气力\n"
            out_data += f"Dormitory,str,{cache_control.now_chara_data.Dormitory},1,角色初始宿舍\n"
            out_data += f"Token,str,{cache_control.now_chara_data.Token},1,角色信物\n"
            out_data += f"Introduce_1,str,{cache_control.now_chara_data.Introduce_1},1,角色介绍\n"
            if len(cache_control.now_chara_data.TextColor) == 7 and cache_control.now_chara_data.TextColor[0] == "#":
                out_data += f"TextColor,str,{cache_control.now_chara_data.TextColor},1,角色字体颜色为{cache_control.now_chara_data.TextColor}\n"
            if len(cache_control.now_chara_data.Ability):
                for key in cache_control.now_chara_data.Ability:
                    out_data += f"A|{key},int,{cache_control.now_chara_data.Ability[key]},0,角色{cache_control.ability_data[str(key)]}为{cache_control.now_chara_data.Ability[key]}\n"
            if len(cache_control.now_chara_data.Experience):
                for key in cache_control.now_chara_data.Experience:
                    out_data += f"E|{key},int,{cache_control.now_chara_data.Experience[key]},0,角色{cache_control.experience_data[str(key)]}为{cache_control.now_chara_data.Experience[key]}\n"
            if len(cache_control.now_chara_data.Talent):
                for key in cache_control.now_chara_data.Talent:
                    out_data += f"T|{key},int,{cache_control.now_chara_data.Talent[key]},0,角色有{cache_control.talent_data[str(key)]}素质\n"
            if len(cache_control.now_chara_data.Cloth):
                for key in cache_control.now_chara_data.Cloth:
                    for i in range(len(cache_control.now_chara_data.Cloth[key])):
                        out_data += f"C|{key},str,{cache_control.now_chara_data.Cloth[key][i]},1,角色{cache_control.clothing_data[str(key)]}为{cache_control.now_chara_data.Cloth[key][i]}\n"

            # 写入文件
            with open(cache_control.now_file_path, "w", encoding="utf-8") as f:
                f.write(out_data)
            print(f"debug 保存了文件{cache_control.now_file_path}")
        else:
            print(f"debug 未保存文件")


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
        key = int(list(cache_control.nation_data.keys())[list(cache_control.nation_data.values()).index(self.nation_combo_box.currentText())])
        cache_control.now_chara_data.Nation = key

    def update_birthplace(self):
        """根据文本编辑框更新当前的角色出身地"""
        key = int(list(cache_control.birthplace_data.keys())[list(cache_control.birthplace_data.values()).index(self.birthplace_combo_box.currentText())])
        cache_control.now_chara_data.Birthplace = key

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

    def update_chara_ability(self):
        """根据文本编辑框更新当前的角色能力"""
        now_ability_dict = {}
        for item in self.ability_widget.items:
            key = int(list(cache_control.ability_data.keys())[list(cache_control.ability_data.values()).index(item[1].currentText())])
            value = int(item[2].toPlainText())
            now_ability_dict[key] = value
        cache_control.now_chara_data.Ability = now_ability_dict
        # print(f"debug 更新了角色能力，cache_control.now_chara_data.Ability = {cache_control.now_chara_data.Ability}")

    def update_chara_experience(self):
        """根据文本编辑框更新当前的角色经验"""
        now_experience_dict = {}
        for item in self.exprience_widget.items:
            key = int(list(cache_control.experience_data.keys())[list(cache_control.experience_data.values()).index(item[1].currentText())])
            value = int(item[2].toPlainText())
            now_experience_dict[key] = value
        cache_control.now_chara_data.Experience = now_experience_dict

    def update_chara_talent(self):
        """根据文本编辑框更新当前的角色素质"""
        now_talent_dict = {}
        for item in self.talent_widget.items:
            key = int(list(cache_control.talent_data.keys())[list(cache_control.talent_data.values()).index(item[1].currentText())])
            value = int(item[2].toPlainText())
            now_talent_dict[key] = value
        cache_control.now_chara_data.Talent = now_talent_dict

    def update_chara_clothing(self):
        """根据文本编辑框更新当前的角色服装"""
        now_clothing_dict = {}
        for item in self.clothing_widget.items:
            key = int(list(cache_control.clothing_data.keys())[list(cache_control.clothing_data.values()).index(item[1].currentText())])
            if len(item) == 3:
                value = item[2].toPlainText()
                if key in now_clothing_dict:
                    now_clothing_dict[key].append(value)
                else:
                    now_clothing_dict[key] = [value]
            else:
                value = []
                for sub_item in item[2:]:
                    value.append(sub_item.toPlainText())
                now_clothing_dict[key] = value
        cache_control.now_chara_data.Cloth = now_clothing_dict
        # print(f"debug 更新了角色服装，cache_control.now_chara_data.Cloth = {cache_control.now_chara_data.Cloth}")

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
        for i in range(self.nation_combo_box.count()):
            if self.nation_combo_box.itemText(i) == cache_control.nation_data[str(now_nation)]:
                self.nation_combo_box.setCurrentIndex(i)
                break
        now_birthplace = cache_control.now_chara_data.Birthplace
        for i in range(self.birthplace_combo_box.count()):
            if self.birthplace_combo_box.itemText(i) == cache_control.birthplace_data[str(now_birthplace)]:
                self.birthplace_combo_box.setCurrentIndex(i)
                break
        now_ability_dict = cache_control.now_chara_data.Ability
        # print(f"debug 更新了角色能力，cache_control.now_chara_data.Ability = {cache_control.now_chara_data.Ability}")
        self.ability_widget.items = []
        for key in now_ability_dict:
            self.ability_widget.addItems()
            for i in range(self.ability_widget.items[-1][1].count()):
                if self.ability_widget.items[-1][1].itemText(i) == cache_control.ability_data[str(key)]:
                    self.ability_widget.items[-1][1].setCurrentIndex(i)
                    break
            self.ability_widget.items[-1][2].setText(str(now_ability_dict[key]))
        now_experience_dict = cache_control.now_chara_data.Experience
        self.exprience_widget.items = []
        for key in now_experience_dict:
            self.exprience_widget.addItems()
            for i in range(self.exprience_widget.items[-1][1].count()):
                if self.exprience_widget.items[-1][1].itemText(i) == cache_control.experience_data[str(key)]:
                    self.exprience_widget.items[-1][1].setCurrentIndex(i)
                    break
            self.exprience_widget.items[-1][2].setText(str(now_experience_dict[key]))
        now_talent_dict = cache_control.now_chara_data.Talent
        self.talent_widget.items = []
        for key in now_talent_dict:
            self.talent_widget.addItems()
            for i in range(self.talent_widget.items[-1][1].count()):
                if self.talent_widget.items[-1][1].itemText(i) == cache_control.talent_data[str(key)]:
                    self.talent_widget.items[-1][1].setCurrentIndex(i)
                    break
            self.talent_widget.items[-1][2].setText(str(now_talent_dict[key]))
        now_clothing_dict = cache_control.now_chara_data.Cloth
        self.clothing_widget.items = []
        for key in now_clothing_dict:
            # 跳过默认服装
            if key in [5999,8999]:
                continue
            # 只有单个物品时直接显示
            if len(now_clothing_dict[key]) == 1:
                self.clothing_widget.addItems()
                self.clothing_widget.items[-1][1].setCurrentIndex(int(key))
                self.clothing_widget.items[-1][2].setText(now_clothing_dict[key][0])
            # 多个物品时每个单独显示
            else:
                count = 1
                for i in range(len(now_clothing_dict[key])):
                    # 检查是否已经存在具有相同值的comboBox
                    existing_item = None
                    for item in self.clothing_widget.items:
                        if item[1].currentText() == cache_control.clothing_data[str(key)]:
                            count += 1
                            existing_item = list(item)
                            break
                    if existing_item:
                        # 在相同的水平布局中添加一个新的textEdit
                        textEdit = QTextEdit(self.clothing_widget)
                        textEdit.setFixedHeight(30)
                        existing_item[0].addWidget(textEdit)
                        existing_item.append(textEdit)

                        # 计算新的宽度
                        new_width = 600 // count

                        # 设置所有textEdit的宽度
                        for sub_item in existing_item:
                            if isinstance(sub_item, QTextEdit):
                                sub_item.setFixedWidth(new_width)

                        # 设置新textEdit的文本
                        textEdit.setText(now_clothing_dict[key][i])

                        # 找到existing_item在self.clothing_widget.items中的索引，然后用existing_item替换掉它
                        index = self.clothing_widget.items.index(item)
                        self.clothing_widget.items[index] = existing_item

                    else:
                        self.clothing_widget.addItems()
                        self.clothing_widget.items[-1][1].setCurrentIndex(int(key))
                        self.clothing_widget.items[-1][2].setText(now_clothing_dict[key][i])

        self.update_chara_textcolor()


class MenuWidget(QWidget):
    def __init__(self, type_flag = 0):
        super().__init__()

        self.mainLayout = QVBoxLayout(self)

        self.buttonLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.buttonLayout)

        self.addButton = QPushButton("添加", self)
        self.addButton.clicked.connect(self.addItems)
        self.buttonLayout.addWidget(self.addButton)

        self.removeButton = QPushButton("删除", self)
        self.removeButton.clicked.connect(self.removeItems)
        self.buttonLayout.addWidget(self.removeButton)

        self.type_flag = type_flag
        self.items = []
        self.items_per_layout = 0  # 新增属性来跟踪每个水平布局中的项目数量

    def addItems(self):
        comboBox = QComboBox(self)
        textEdit = QTextEdit(self)

        # 赋予下拉框初始值
        have_text_flag = True
        cloth_flag = False
        if self.type_flag == 0:
            initial_text_list = [cache_control.ability_data[i] for i in cache_control.ability_data]
        elif self.type_flag == 1:
            initial_text_list = [cache_control.experience_data[i] for i in cache_control.experience_data]
        elif self.type_flag == 2:
            initial_text_list = [cache_control.talent_data[i] for i in cache_control.talent_data]
            have_text_flag = False
        elif self.type_flag == 3:
            initial_text_list = [cache_control.clothing_data[i] for i in cache_control.clothing_data]
            cloth_flag = True
            self.items_per_layout = 0  # 重置项目数量

        for initial_text in initial_text_list:
            comboBox.addItem(initial_text)

        # 设定文本编辑框的大小
        textEdit.setFixedHeight(30)
        textEdit.setFixedWidth(50)
        if cloth_flag:
            textEdit.setFixedWidth(600)
        # 文本框的值默认为1
        textEdit.setText("1")

        # 创建一个新的水平布局，并将新项目添加到这个新的水平布局中
        if self.items_per_layout % 4 != 0:  # 如果当前水平布局中的项目数量小于3
            layout = self.items[-1][0] if self.items else QHBoxLayout()  # 使用最后一个水平布局
        else:  # 否则创建一个新的水平布局
            layout = QHBoxLayout()
            self.mainLayout.addLayout(layout)
            self.items_per_layout = 0  # 重置项目数量

        layout.addWidget(comboBox)
        layout.addWidget(textEdit)

        self.items.append((layout, comboBox, textEdit))
        self.items_per_layout += 1  # 增加项目数量

    def removeItems(self):
        if self.items:
            layout, comboBox, textEdit = self.items.pop()

            # 从主布局中移除子布局
            self.mainLayout.removeItem(layout)

            comboBox.deleteLater()
            textEdit.deleteLater()
            self.items_per_layout -= 1  # 减少项目数量
