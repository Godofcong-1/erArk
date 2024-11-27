from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QMenu,
    QComboBox,
    QMenuBar,
    QWidgetAction
)
from PySide6.QtGui import QFont, Qt, QActionGroup
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class TreeItem(QTreeWidgetItem):
    """树选框对象"""

    def __init__(self, any):
        """初始化树选框对象"""
        super(TreeItem, self).__init__(any)
        self.cid = ""
        """ 对象配表id """


class EffectMenu(QDialog):
    """事件效果选择对象"""

    def __init__(self):
        """初始化事件效果复选框"""
        super(EffectMenu, self).__init__()
        self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.resize(1000,1000)
        # 增加一个搜索框，确定键，重置键，三个合在一起，放在最上面作为一个横向的搜索栏
        self.search_text = QTextEdit()
        self.search_text.setFont(self.font)
        self.search_text.setFixedHeight(32)
        self.search_text.setFixedWidth(200)
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search)
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset)
        # 放在tree的上面，作为一个横向的搜索栏
        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(self.search_text)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.reset_button)
        self.layout.addLayout(self.search_layout)
        # 创建一个新的 QHBoxLayout，用于左右排列两个 tree
        self.tree_layout = QHBoxLayout()
        all_type_list = sorted([k for k in cache_control.effect_type_data.keys() if k is not None])
        range_index = int(len(all_type_list) / 2) + 1
        range_a = all_type_list[:range_index]
        range_b = all_type_list[range_index :]
        range_list = [range_a, range_b]
        index = 1
        self.tree_list = []
        for type_list in range_list:
            tree = QTreeWidget()
            tree.setHeaderLabel("结算列表" + str(index))
            tree.setWordWrap(True)
            tree.adjustSize()
            index += 1
            tree.setSelectionMode(QAbstractItemView.SingleSelection)
            tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            root_list = []
            for now_type in type_list:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, now_type)
                effect_list = list(cache_control.effect_type_data[now_type])
                effect_list.sort()
                for effect in effect_list:
                    effect_node = TreeItem(now_root)
                    effect_node.cid = effect
                    effect_node.setText(0, cache_control.effect_data[effect])
                    effect_node.setToolTip(0,effect_node.text(0))
                    if effect in cache_control.now_event_data[cache_control.now_select_id].effect:
                        effect_node.setCheckState(0, Qt.Checked)
                    else:
                        effect_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            tree.addTopLevelItems(root_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.tree_list.append(tree)
            self.tree_layout.addWidget(tree)  # 将 tree 添加到 QHBoxLayout 中
        self.layout.addLayout(self.tree_layout)
        self.setLayout(self.layout)

    def click_item(self, item: TreeItem, column: int):
        """
        点击选项时勾选选框并更新事件效果
        Keyword arguments:
        item -- 点击的对象
        column -- 点击位置
        """
        if "cid" not in item.__dict__:
            return
        if item.checkState(column) == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
            if item.cid in cache_control.now_event_data[cache_control.now_select_id].effect:
                del cache_control.now_event_data[cache_control.now_select_id].effect[item.cid]
        else:
            item.setCheckState(0, Qt.Checked)
            cache_control.now_event_data[cache_control.now_select_id].effect[item.cid] = 1
        cache_control.item_effect_list.update()

    def search(self):
        """搜索结算器"""
        search_text = self.search_text.toPlainText()
        if not len(search_text):
            return
        for tree in self.tree_list:
            for i in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(i)
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    if search_text in child.text(0):
                        child.setHidden(False)
                    else:
                        child.setHidden(True)

    def reset(self):
        """清零前提列表"""
        self.search_text.setText("")
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    child.setHidden(False)


class CVEMenu(QDialog):
    """综合型基础数值结算选择对象"""

    def __init__(self):
        """初始化综合型基础数值结算复选框"""
        super(CVEMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        elif cache_control.now_edit_type_flag == 0:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.ABCD_button_layout = QHBoxLayout()
        self.resize(1000,50)

        # 一段说明文字，用来介绍各个功能，位置在最上面的第一行
        self.cve_text = QLabel("用于实现数值方面的综合型万用结算")
        self.cve_text.setFont(self.font)
        self.layout.addWidget(self.cve_text)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cve_a = QComboBox()
        self.cve_a.addItems(["自己", "交互对象", "角色id为"])
        self.cve_a.setCurrentIndex(0)
        self.cve_a.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cve_a)
        self.cve_a2 = QTextEdit("0")
        self.cve_a2.setFont(self.font)
        self.cve_a2.setFixedHeight(32)
        self.cve_a2.setFixedWidth(50)
        self.cve_a2.setVisible(False)
        self.ABCD_button_layout.addWidget(self.cve_a2)
        self.cve_a.currentIndexChanged.connect(self.change_a2)

        # B数值为属性，A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖
        self.cve_b1 = QComboBox()
        self.cve_b1.addItems(["待选择", "好感", "信赖", "能力", "素质", "宝珠", "经验", "状态", "口上用flag", "绝顶", "嵌套父事件", "指定角色id为交互对象"])
        self.cve_b1.setCurrentIndex(0)
        self.cve_b1.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cve_b1)

        # b2根据b1会出现不同的选项
        self.cve_b2 = QComboBox()
        self.cve_b2.addItems([""])
        self.cve_b2.setCurrentIndex(0)
        self.cve_b2.setFont(self.font)
        self.cve_b2.setVisible(False)
        self.cve_b1.currentIndexChanged.connect(self.change_b2)
        self.ABCD_button_layout.addWidget(self.cve_b2)

        # C数值为判定方式
        self.cve_c = QComboBox()
        self.cve_c.addItems(["增加", "减少", "变为"])
        self.cve_c.setCurrentIndex(0)
        self.cve_c.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cve_c)

        # D数值为判定值
        self.cve_d = QTextEdit("0")
        self.cve_d.setFont(self.font)
        self.cve_d.setFixedHeight(32)
        self.cve_d.setFixedWidth(50)
        self.ABCD_button_layout.addWidget(self.cve_d)

        self.layout.addLayout(self.ABCD_button_layout)

        # 添加确定按钮与取消按钮
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.ok)
        self.ok_button.setFont(self.font)
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFont(self.font)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def ok(self):
        """点击确定按钮"""
        # 获得当前abcd的值
        cve_a = self.cve_a.currentText()
        if cve_a == "自己":
            cve_a_value = "A1"
        elif cve_a == "交互对象":
            cve_a_value = "A2"
        elif cve_a == "角色id为":
            cve_a_value = "A3|" + self.cve_a2.toPlainText()
            cve_a = "角色id为" + self.cve_a2.toPlainText()
        cve_b1 = self.cve_b1.currentText()
        if len(self.cve_b2.currentText().split("|")) == 2:
            cve_b2 = self.cve_b2.currentText().split("|")[1]
        elif len(self.cve_b2.currentText().split("|")) == 1:
            cve_b2 = self.cve_b2.currentText().split("|")[0]
        else:
            cve_b2 = ""
        if cve_b1 == "待选择":
            cve_b_value = ""
        elif cve_b1 == "好感":
            cve_b_value = "F"
        elif cve_b1 == "信赖":
            cve_b_value = "X"
        elif cve_b1 == "能力":
            cve_b_value = "A|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "素质":
            cve_b_value = "T|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "宝珠":
            cve_b_value = "J|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "经验":
            cve_b_value = "E|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "状态":
            cve_b_value = "S|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "口上用flag":
            cve_b_value = "Flag|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "绝顶":
            cve_b_value = "Climax|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "嵌套父事件":
            cve_b_value = "Father|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "指定角色id为交互对象":
            cve_b_value = "ChangeTargetId|0"
        cve_c = self.cve_c.currentText()
        if cve_c == "增加":
            cve_c_value = "G"
        elif cve_c == "减少":
            cve_c_value = "L"
        elif cve_c == "变为":
            cve_c_value = "E"
        cve_d = self.cve_d.toPlainText()
        cve_d_value = cve_d
        # 空值时默认为0
        if cve_d_value == "":
            cve_d_value = "0"

        # 指定角色id为交互对象时特殊处理
        if cve_b1 == "指定角色id为交互对象":
            # 不显示c和d
            cve_c = ""
            cve_d = ""

        # 拼接结算字符串
        cve_str = f"综合数值结算  {cve_a}{cve_b1}{cve_b2}{cve_c}{cve_d}"
        cve_value_str = f"CVE_{cve_a_value}_{cve_b_value}_{cve_c_value}_{cve_d_value}"
        # print(f"debug cve_str: {cve_str}, cve_value_str: {cve_value_str}")

        # 更新结算数据
        cache_control.effect_data[cve_value_str] = cve_str

        # 更新结算列表
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].effect[cve_value_str] = 1
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].effect[cve_value_str] = 1
        cache_control.item_effect_list.update()
        self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cve_a2.setVisible(True)
        else:
            self.cve_a2.setVisible(False)

    def reset_c(self):
        """重置c的选项"""
        self.cve_c.clear()
        self.cve_c.addItems(["增加", "减少", "变为"])
        self.cve_c.setCurrentIndex(0)
        self.cve_c.setFont(self.font)
        self.cve_c.setVisible(True)

    def change_b2(self, index: int):
        """改变b2的选项"""
        # 获取cve_a的items数量
        items_count = self.cve_a.count()
        if items_count != 3:
            self.cve_a.clear()
            self.cve_a.addItems(["自己", "交互对象", "角色id为"])
            self.cve_a.setVisible(True)
        self.cve_b2.setVisible(True)
        self.reset_c()
        self.cve_d.setVisible(True)
        if index == 0:
            self.cve_b2.setVisible(False)
        elif index == 1:
            self.cve_b2.setVisible(False)
            self.cve_text.setText("好感度的-1级和1~8级分别为：负数，100，500，1000，2500，5000，10000，50000，100000，此处使用的为好感的具体数值，不是等级")
        elif index == 2:
            self.cve_b2.setVisible(False)
            self.cve_text.setText("信赖度的-1级和18级分别为：负数，25%，50%，75%，100%，150%，200%，250%，300%，此处使用的为信赖度的具体数值，不是等级")
        elif index == 3:
            self.cve_b2.clear()
            for ability_id, ability_name in cache_control.ability_data.items():
                self.cve_b2.addItem(f"{ability_id}|{ability_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("能力最高为8级")
        elif index == 4:
            self.cve_b2.clear()
            for talent_id, talent_name in cache_control.talent_data.items():
                self.cve_b2.addItem(f"{talent_id}|{talent_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("1为有该素质，0为无该素质")
        elif index == 5:
            self.cve_b2.clear()
            for juel_id, juel_name in cache_control.juel_data.items():
                self.cve_b2.addItem(f"{juel_id}|{juel_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("宝珠是用来升级能力或获得素质的")
        elif index == 6:
            self.cve_b2.clear()
            for experience_id, experience_name in cache_control.experience_data.items():
                self.cve_b2.addItem(f"{experience_id}|{experience_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("每次指令都会获得1对应经验")
        elif index == 7:
            self.cve_b2.clear()
            for state_id, state_name in cache_control.state_data.items():
                self.cve_b2.addItem(f"{state_id}|{state_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("状态值的1~10级分别为：100，500，3000，10000，30000，60000，100000，150000，500000，999999，此处使用的为状态值的具体数值，不是等级")
        elif index == 8:
            self.cve_b2.clear()
            # b2提供一个文本框，用来输入flag的编号，最多支持10个flag
            for i in range(50):
                self.cve_b2.addItem(str(i))
            self.cve_text.setText("口上用flag是用来实现供口上作者自定义的数据变量，可以用来实现一些特殊的前提\n口上用flag的数据类型为int，默认值为0，最多支持50个flag（即编号为0~49）\n口上用flag无法独立使用，需要用编辑器的事件中的结算来进行修改\n如【用flag0来记录触发某个指令或某句口上的次数】，【用flag1来记录自己设定的某种攻略的阶段】，【用flag2来衡量自己设定的角色对玩家的某种感情】等等")
        elif index == 9:
            self.cve_b2.clear()
            for organ_id, organ_name in cache_control.organ_data.items():
                self.cve_b2.addItem(f"{organ_id}|{organ_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_c.clear()
            self.cve_c.addItems(["增加", "变为"])
            self.cve_c.setCurrentIndex(0)
            self.cve_text.setText("触发一次该部位的绝顶，0为小绝顶，1为普绝顶，2为强绝顶。\n选择[增加]时，效果为从小绝顶开始，同时触发多次不同强度的绝顶，如增加 1 即为同时触发0小绝顶和1普绝顶，以此类推\n选择[变为]则变为哪个就触发哪个，如变为 2 即为触发强绝顶")
        elif index == 10:
            self.cve_a.setVisible(False)
            self.cve_b2.clear()
            for i in range(100):
                self.cve_b2.addItem(str(i))
            self.cve_c.clear()
            self.cve_c.addItems(["变为"])
            self.cve_c.setCurrentIndex(0)
            self.cve_text.setText("嵌套父事件，用于在事件编辑中展开多层嵌套父子事件\n\n①如果仅需要单层的父子选项事件请使用[整体修改]-[系统量]-[基础]\n②本前提需要配合[综合数值前提]中的[嵌套子事件]使用\n③同数字的父事件会展开同数字的子事件，如，序号0的嵌套父事件会检索序号0的嵌套子事件，以此类推\n\n例子：父事件A1（嵌套父事件=0）\n  一级子事件B1（嵌套子事件=0↔A1，嵌套父事件=1）、B2（嵌套子事件=0↔A1，嵌套父事件=2）\n  二级子事件C1（嵌套子事件=1↔B1），C2（嵌套子事件=1↔B1），C3（嵌套子事件=2↔B2），C4（嵌套子事件=2↔B2）\n")
        elif index == 11:
            self.cve_a.clear()
            self.cve_a.addItems(["角色id为"])
            self.cve_a2.setVisible(True)
            self.cve_b2.setVisible(False)
            self.cve_c.setVisible(False)
            self.cve_d.setVisible(False)
            self.cve_text.setText("选择当前场景中的指定id的角色作为自己的交互对象\n\n需要搭配综合数值前提中的，当前场景中有特定id的角色存在，的前提一同使用，当前场景中没有该id角色时会无法起效\n当有多个结算时，本结算需要放到第一个，以便第一个执行\n玩家的id固定为0")

        self.cve_b = self.cve_b2


class CSEMenu(QDialog):
    """综合指令状态结算选择对象"""

    def __init__(self):
        """初始化综合指令状态结算复选框"""
        super(CSEMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        elif cache_control.now_edit_type_flag == 0:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.ABCD_button_layout = QHBoxLayout()
        self.resize(1000,50)

        # 一段说明文字，用来介绍各个功能，位置在最上面的第一行
        self.cse_text = QLabel("用于实现指令状态方面的综合型万用结算，目前仅支持触发玩家的指令")
        self.cse_text.setFont(self.font)
        self.layout.addWidget(self.cse_text)

        self.text_label = QLabel("玩家对")
        self.text_label.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.text_label)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cse_a = QComboBox()
        # self.cse_a.addItems(["自己", "交互对象", "角色id为"])
        self.cse_a.addItems(["自己", "交互对象"])
        self.cse_a.setCurrentIndex(0)
        self.cse_a.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cse_a)
        self.cse_a2 = QTextEdit("0")
        self.cse_a2.setFont(self.font)
        self.cse_a2.setFixedHeight(32)
        self.cse_a2.setFixedWidth(50)
        self.cse_a2.setVisible(False)
        self.ABCD_button_layout.addWidget(self.cse_a2)
        self.cse_a.currentIndexChanged.connect(self.change_a2)

        # 在ABCD_button_layout中加入一个文本的空白label，用来占位
        self.text_label = QLabel(" 使用指令 ")
        self.text_label.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.text_label)

        # 加入菜单，用来选择B的数值
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setFont(self.font)  # 设置菜单栏的字体
        self.status_menu: QMenu = QMenu("待选择", self)
        self.status_menu.setFont(self.font)  # 设置菜单的字体
        self.menu_bar.addMenu(self.status_menu)
        self.ABCD_button_layout.addWidget(self.menu_bar)

        # 创建一个动作组并将其关联到change_status_menu函数
        status_group = QActionGroup(self.status_menu)
        status_group.triggered.connect(self.change_status_menu)

        # 添加每个状态作为一个动作到菜单中
        for status_type in cache_control.status_type_data:
            status_menu = QMenu(status_type, self.status_menu)
            for cid in cache_control.status_type_data[status_type]:
                if cid is cache_control.now_status:
                    continue
                if cid == "0":
                    continue
                now_action: QWidgetAction = QWidgetAction(self)
                now_action.setText(cache_control.status_data[cid])
                now_action.setActionGroup(status_group)
                now_action.setData(cid)
                status_menu.addAction(now_action)
                status_menu.setFont(self.font)
            self.status_menu.addMenu(status_menu)

        self.layout.addLayout(self.ABCD_button_layout)

        # 添加确定按钮与取消按钮
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.ok)
        self.ok_button.setFont(self.font)
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFont(self.font)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    # 将change_status_menu函数定义为一个实例方法
    def change_status_menu(self, action: QWidgetAction):
        """
        更新状态菜单
        Keyword arguments:
        action -- 触发的菜单
        """
        cid = action.data()
        self.status_menu.setTitle(cache_control.status_data[cid])
        self.status_menu.clear()
        status_group = QActionGroup(self.status_menu)
        for status_type in cache_control.status_type_data:
            status_menu = QMenu(status_type, self.status_menu)
            for cid in cache_control.status_type_data[status_type]:
                if cid == "0":
                    continue
                now_action: QWidgetAction = QWidgetAction(self)
                now_action.setText(cache_control.status_data[cid])
                now_action.setActionGroup(status_group)
                now_action.setData(cid)
                status_menu.addAction(now_action)
                status_menu.setFont(self.font)
            self.status_menu.addMenu(status_menu)
        status_group.triggered.connect(self.change_status_menu)


    def ok(self):
        """点击确定按钮"""
        # 获得当前abcd的值
        cse_a = self.cse_a.currentText()
        if cse_a == "自己":
            cse_a_value = "A1"
        elif cse_a == "交互对象":
            cse_a_value = "A2"
        elif cse_a == "角色id为":
            cse_a_value = "A3|" + self.cse_a2.toPlainText()
            cse_a = "角色id为" + self.cse_a2.toPlainText()

        # cse_b为状态的名字，cse_b_value为状态的cid
        cse_b = self.status_menu.title()
        for cid in cache_control.status_data:
            if cache_control.status_data[cid] == cse_b:
                cse_b_value = cid
                break

        # 拼接结算字符串
        cse_str = f"综合指令状态结算  玩家对{cse_a} 进行 {cse_b}"
        cse_value_str = f"CSE_{cse_a_value}_{cse_b_value}"
        # print(f"debug cse_str: {cse_str}, cse_value_str: {cse_value_str}")

        # 更新结算数据
        cache_control.effect_data[cse_value_str] = cse_str

        # 更新结算列表
        cache_control.now_event_data[cache_control.now_select_id].effect[cse_value_str] = 1
        cache_control.item_effect_list.update()
        self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cse_a2.setVisible(True)
        else:
            self.cse_a2.setVisible(False)
