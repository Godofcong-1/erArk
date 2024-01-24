from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QPushButton,
    QComboBox,
    QTextEdit,
    QVBoxLayout,
    QMenu,
    QLabel
)
from PySide6.QtGui import QFont, Qt
import cache_control
import function


class TreeItem(QTreeWidgetItem):
    """树选框对象"""

    def __init__(self, any):
        """初始化树选框对象"""
        super(TreeItem, self).__init__(any)
        self.cid = ""
        """ 对象配表id """

class PremiseMenu(QDialog):
    """前提选择对象"""

    def __init__(self):
        """初始化前提复选框"""
        super(PremiseMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        else:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = QFont()
        self.font.setPointSize(11)
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
        all_type_list = sorted(list(cache_control.premise_type_data.keys()))
        range_index = int(len(all_type_list) / 2) + 1
        range_a = all_type_list[:range_index]
        range_b = all_type_list[range_index :]
        range_list = [range_a, range_b]
        index = 1
        self.tree_list = []
        for type_list in range_list:
            tree = QTreeWidget()
            tree.setHeaderLabel("前提列表" + str(index))
            index += 1
            tree.setSelectionMode(QAbstractItemView.SingleSelection)
            tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            tree.setWordWrap(True)  # 设置 wordWrap 属性为 True
            tree.adjustSize()
            # 设置列的宽度为一个固定的值
            tree.setColumnWidth(0, 2000)

            root_list = []
            # 在index==2的时候，单独增加一个自定义前提群的type
            if index == 2:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, "自定义前提群")
                premise_group_list = list(cache_control.premise_group_data.keys())
                premise_group_list.sort()
                for premise_group in premise_group_list:
                    premise_group_node = TreeItem(now_root)
                    premise_group_node.cid = premise_group
                    # 根据前提群的cid，获取前提群的所有前提cid，然后把名字拼接成一个字符串
                    now_premise_group_list = cache_control.premise_group_data[premise_group]
                    now_premise_group_all_name = ""
                    for premise_cid in now_premise_group_list:
                        if "CVP" in premise_cid:
                            now_premise_group_all_name += function.read_CVP(premise_cid)
                        else:
                            now_premise_group_all_name += cache_control.premise_data[premise_cid]
                        if premise_cid != now_premise_group_list[-1]:
                            now_premise_group_all_name += "&"
                    premise_group_node.setText(0, now_premise_group_all_name)
                    premise_group_node.setToolTip(0,premise_group_node.text(0))
                    if cache_control.now_edit_type_flag == 1:
                        if premise_group in cache_control.now_event_data[cache_control.now_select_id].premise:
                            premise_group_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_group_node.setCheckState(0, Qt.Unchecked)
                    else:
                        if premise_group in cache_control.now_talk_data[cache_control.now_select_id].premise:
                            premise_group_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_group_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            # 正常的前提type
            for now_type in type_list:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, now_type)
                premise_list = list(cache_control.premise_type_data[now_type])
                premise_list.sort()
                for premise in premise_list:
                    premise_node = TreeItem(now_root)
                    premise_node.cid = premise
                    premise_node.setText(0, cache_control.premise_data[premise])
                    premise_node.setToolTip(0,premise_node.text(0))
                    if cache_control.now_edit_type_flag == 1:
                        if premise in cache_control.now_event_data[cache_control.now_select_id].premise:
                            premise_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_node.setCheckState(0, Qt.Unchecked)
                    else:
                        if premise in cache_control.now_talk_data[cache_control.now_select_id].premise:
                            premise_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            tree.addTopLevelItems(root_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.tree_list.append(tree)
            self.tree_layout.addWidget(tree)  # 将 tree 添加到 QHBoxLayout 中
        self.layout.addLayout(self.tree_layout)
        self.setLayout(self.layout)

    def update_premise(self, item, data):
        """
        删除前提
        Keyword arguments:
        item -- 删除的对象
        data -- 当前事件数据
        """
        if item.cid in cache_control.premise_group_data:
            for premise_cid in cache_control.premise_group_data[item.cid]:
                if premise_cid in data.premise:
                    del data.premise[premise_cid]
        else:
            if item.cid in data.premise:
                del data.premise[item.cid]

    def add_premise(self, item, data):
        """
        添加前提
        Keyword arguments:
        item -- 添加的对象
        data -- 当前事件数据
        """
        if item.cid in cache_control.premise_group_data:
            for premise_cid in cache_control.premise_group_data[item.cid]:
                data.premise[premise_cid] = 1
        else:
            data.premise[item.cid] = 1

    def click_item(self, item: TreeItem, column: int):
        """
        点击选项时勾选选框并更新事件前提
        Keyword arguments:
        item -- 点击的对象
        column -- 点击位置
        """
        if "cid" not in item.__dict__:
            return

        if cache_control.now_edit_type_flag == 1:
            data = cache_control.now_event_data[cache_control.now_select_id]
        else:
            data = cache_control.now_talk_data[cache_control.now_select_id]

        if item.checkState(column) == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
            self.update_premise(item, data)
        else:
            item.setCheckState(0, Qt.Checked)
            self.add_premise(item, data)

        cache_control.item_premise_list.update()

    def search(self):
        """搜索前提"""
        search_text = self.search_text.toPlainText()
        if not len(search_text):
            return
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    if search_text in child.text(0):
                        child.setHidden(False)
                    else:
                        child.setHidden(True)

    def reset(self):
        """重置搜索"""
        self.search_text.setText("")
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    child.setHidden(False)


    # def contextMenuEvent(self, event):
    #     """右键菜单"""
    #     menu = QMenu(self)
    #     delete_action = menu.addAction("删除")
    #     # 获取鼠标右键点击的项
    #     item = event.pos()
    #     # 将获取到的项传递给 delete_group 方法
    #     delete_action.triggered.connect(lambda: self.delete_group(item))
    #     menu.exec_(event.globalPos())

    def delete_group(self, item):
        """删除前提组"""
        # 找到前提群cid
        premise_group_cid = ""
        print(f"debug premise_group_cid: {premise_group_cid}")
        # 根据cid在cache_control.premise_group_data中删掉该前提群
        if premise_group_cid in cache_control.premise_group_data:
            del cache_control.premise_group_data[premise_group_cid]
        # 在文件中删除该前提群
        # with open(cache_control.now_file_path, "r", encoding="utf-8") as now_file:
        #     now_read = now_file.readlines()
        # with open(cache_control.now_file_path, "w", encoding="utf-8") as now_file:
        #     for line in now_read:
        #         if premise_group_cid in line:
        #             continue
        #         now_file.write(line)
        # 更新前提列表
        self.update()


class CVPMenu(QDialog):
    """综合型基础数值前提选择对象"""

    def __init__(self):
        """初始化综合型基础数值前提复选框"""
        super(CVPMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        else:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = QFont()
        self.font.setPointSize(11)
        self.layout: QVBoxLayout = QVBoxLayout()
        self.ABCD_button_layout = QHBoxLayout()
        self.resize(1000,50)

        # 一段说明文字，用来介绍各个功能，位置在最上面的第一行
        self.cvp_text = QLabel("用于实现数值方面的综合型万用前提")
        self.cvp_text.setFont(self.font)
        self.layout.addWidget(self.cvp_text)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cvp_a = QComboBox()
        self.cvp_a.addItems(["自己", "交互对象", "角色id为"])
        self.cvp_a.setCurrentIndex(0)
        self.cvp_a.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cvp_a)
        self.cvp_a2 = QTextEdit("0")
        self.cvp_a2.setFont(self.font)
        self.cvp_a2.setFixedHeight(32)
        self.cvp_a2.setFixedWidth(50)
        self.cvp_a2.setVisible(False)
        self.ABCD_button_layout.addWidget(self.cvp_a2)
        self.cvp_a.currentIndexChanged.connect(self.change_a2)

        # B数值为属性，A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖
        self.cvp_b1 = QComboBox()
        self.cvp_b1.addItems(["待选择", "好感", "信赖", "能力", "素质", "宝珠", "经验", "状态", "攻略程度", "时间"])
        self.cvp_b1.setCurrentIndex(0)
        self.cvp_b1.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cvp_b1)

        # b2根据b1会出现不同的选项
        self.cvp_b2 = QComboBox()
        self.cvp_b2.addItems([""])
        self.cvp_b2.setCurrentIndex(0)
        self.cvp_b2.setFont(self.font)
        self.cvp_b2.setVisible(False)
        self.cvp_b1.currentIndexChanged.connect(self.change_b2)
        self.ABCD_button_layout.addWidget(self.cvp_b2)

        # C数值为判定方式
        self.cvp_c = QComboBox()
        self.cvp_c.addItems(["大于", "小于", "等于", "大于等于", "小于等于", "不等于"])
        self.cvp_c.setCurrentIndex(0)
        self.cvp_c.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cvp_c)

        # D数值为判定值
        self.cvp_d = QTextEdit("0")
        self.cvp_d.setFont(self.font)
        self.cvp_d.setFixedHeight(32)
        self.cvp_d.setFixedWidth(50)
        self.ABCD_button_layout.addWidget(self.cvp_d)

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
        cvp_a = self.cvp_a.currentText()
        if cvp_a == "自己":
            cvp_a_value = "A1"
        elif cvp_a == "交互对象":
            cvp_a_value = "A2"
        elif cvp_a == "角色id为":
            cvp_a_value = "A3|" + self.cvp_a2.toPlainText()
            cvp_a = "角色id为" + self.cvp_a2.toPlainText()
        cvp_b1 = self.cvp_b1.currentText()
        if len(self.cvp_b2.currentText().split("|")) == 2:
            cvp_b2 = self.cvp_b2.currentText().split("|")[1]
        else:
            cvp_b2 = ""
        if cvp_b1 == "待选择":
            cvp_b_value = ""
        elif cvp_b1 == "好感":
            cvp_b_value = "F"
        elif cvp_b1 == "信赖":
            cvp_b_value = "X"
        elif cvp_b1 == "能力":
            cvp_b_value = "A|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "素质":
            cvp_b_value = "T|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "宝珠":
            cvp_b_value = "J|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "经验":
            cvp_b_value = "E|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "状态":
            cvp_b_value = "S|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "攻略程度":
            cvp_b_value = "G"
        elif cvp_b1 == "时间":
            cvp_b_value = "Time"
        cvp_c = self.cvp_c.currentText()
        if cvp_c == "大于":
            cvp_c_value = "G"
        elif cvp_c == "小于":
            cvp_c_value = "L"
        elif cvp_c == "等于":
            cvp_c_value = "E"
        elif cvp_c == "大于等于":
            cvp_c_value = "GE"
        elif cvp_c == "小于等于":
            cvp_c_value = "LE"
        elif cvp_c == "不等于":
            cvp_c_value = "NE"
        cvp_d = self.cvp_d.toPlainText()
        cvp_d_value = cvp_d

        # 拼接前提字符串
        cvp_str = f"综合数值前提  {cvp_a}{cvp_b1}{cvp_b2}{cvp_c}{cvp_d}"
        cvp_value_str = f"CVP_{cvp_a_value}_{cvp_b_value}_{cvp_c_value}_{cvp_d_value}"
        # print(f"debug cvp_str: {cvp_str}, cvp_value_str: {cvp_value_str}")

        # 更新前提数据
        cache_control.premise_data[cvp_value_str] = cvp_str

        # 更新前提列表
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].premise[cvp_value_str] = 1
        else:
            cache_control.now_talk_data[cache_control.now_select_id].premise[cvp_value_str] = 1
        cache_control.item_premise_list.update()
        self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cvp_a2.setVisible(True)
        else:
            self.cvp_a2.setVisible(False)

    def change_b2(self, index: int):
        """改变b2的选项"""
        self.cvp_b2.setVisible(True)
        if index == 0:
            self.cvp_b2.setVisible(False)
        elif index == 1:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("好感度的-1~8级分别为：负数，100，500，100，2500，5000，10000，50000，100000")
        elif index == 2:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("信赖度的-1~8级分别为：负数，25%，50%，75%，100%，150%，200%，250%，300%")
        elif index == 3:
            self.cvp_b2.clear()
            for ability_id, ability_name in cache_control.ability_data.items():
                self.cvp_b2.addItem(f"{ability_id}|{ability_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("能力最高为8级")
        elif index == 4:
            self.cvp_b2.clear()
            for talent_id, talent_name in cache_control.talent_data.items():
                self.cvp_b2.addItem(f"{talent_id}|{talent_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("1为有该素质，0为无该素质")
        elif index == 5:
            self.cvp_b2.clear()
            for juel_id, juel_name in cache_control.juel_data.items():
                self.cvp_b2.addItem(f"{juel_id}|{juel_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("宝珠是用来升级能力或获得素质的")
        elif index == 6:
            self.cvp_b2.clear()
            for experience_id, experience_name in cache_control.experience_data.items():
                self.cvp_b2.addItem(f"{experience_id}|{experience_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("每次指令都会获得1对应经验")
        elif index == 7:
            self.cvp_b2.clear()
            for state_id, state_name in cache_control.state_data.items():
                self.cvp_b2.addItem(f"{state_id}|{state_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("状态值的1~10级分别为：100，500，3000，10000，30000，60000，100000，150000，500000，999999")
        elif index == 8:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("攻略有正数的【爱情系】和负数的【隶属系】两种路线\n爱情系的1~4分别为思慕、恋慕、恋人、爱侣，隶属系的-1~-4分别为屈从、驯服、宠物、奴隶\n备注：数值不会到0，如，当选择爱情系的≤2时，只会到1的思慕，而不会到0或者负数的隶属系，其他情况同理")
        elif index == 9:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("时间也是一天24小时，如果要定起止时间的话，可以搭配使用【时间大于等于A】和【时间小于等于B】的两个前提来实现")
        self.cvp_b = self.cvp_b2
