from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QMenu, QComboBox, QTextEdit, QMenuBar, QWidgetAction
from PySide6.QtGui import QFont, QActionGroup
from PySide6.QtCore import Qt
import cache_control
from ui.effect_menu import EffectMenu

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)


class ItemEffectList(QWidget):
    """结算表单主体"""

    def __init__(self):
        """初始化结算表单主体"""
        super(ItemEffectList, self).__init__()
        self.font = font
        self.setFont(self.font)
        main_layout = QVBoxLayout()  # 主布局
        # 标题布局
        title_layout = QVBoxLayout()
        label = QLabel()
        label.setText("结算列表")
        title_layout.addWidget(label)
        # 按钮布局
        button_layout1 = QHBoxLayout()
        change_button = QPushButton("整体修改")
        change_button.clicked.connect(self.change)
        button_layout1.addWidget(change_button)
        reset_button = QPushButton("整体清零")
        reset_button.clicked.connect(self.reset)
        button_layout1.addWidget(reset_button)
        title_layout.addLayout(button_layout1)
        main_layout.addLayout(title_layout)

        button_layout2 = QHBoxLayout()
        # CVE_button = QPushButton("综合型基础数值结算")
        # CVE_button.clicked.connect(self.CVE)
        # button_layout2.addWidget(CVE_button)
        CSE_button = QPushButton("综合指令状态结算")
        CSE_button.clicked.connect(self.CSE)
        button_layout2.addWidget(CSE_button)
        title_layout.addLayout(button_layout2)
        # 文字说明
        info_label = QLabel()
        info_label.setText("右键删除该结算，双击替换该结算")
        # 结算列表布局
        list_layout = QHBoxLayout()
        self.item_list = QListWidget()
        self.item_list.setWordWrap(True)
        self.item_list.adjustSize()
        self.item_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.item_list.customContextMenuRequested.connect(self.show_context_menu)
        self.item_list.itemDoubleClicked.connect(self.change_this_item)
        list_layout.addWidget(self.item_list)
        main_layout.addWidget(info_label)
        main_layout.addLayout(list_layout)
        self.setLayout(main_layout)

    def update(self):
        """更新结算列表"""
        self.item_list.clear()
        if cache_control.now_edit_type_flag == 1:
            for effect in cache_control.now_event_data[cache_control.now_select_id].effect:
                item = QListWidgetItem(cache_control.effect_data[effect])
                item.setToolTip(item.text())
                self.item_list.addItem(item)

    def change(self):
        """展开结算菜单"""
        menu = EffectMenu()
        menu.exec()

    def change_this_item(self, item):
        """删除该结算并展开结算菜单"""
        self.item_list.takeItem(self.item_list.row(item))
        for effect in cache_control.effect_data:
            if cache_control.effect_data[effect] == item.text():
                effect_cid = effect
                break
        if effect_cid in cache_control.now_event_data[cache_control.now_select_id].effect:
            del cache_control.now_event_data[cache_control.now_select_id].effect[effect_cid]
        menu = EffectMenu()
        menu.exec()

    def reset(self):
        """清零结算列表"""
        cache_control.now_event_data[cache_control.now_select_id].effect = {}
        self.item_list.clear()

    def show_context_menu(self, pos):
        """删除该结算"""
        item = self.item_list.itemAt(pos)
        if item is not None:
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            action = menu.exec_(self.item_list.mapToGlobal(pos))
            if action == delete_action:
                self.item_list.takeItem(self.item_list.row(item))
                for effect in cache_control.effect_data:
                    if cache_control.effect_data[effect] == item.text():
                        effect_cid = effect
                        break
                if effect_cid in cache_control.now_event_data[cache_control.now_select_id].effect:
                    del cache_control.now_event_data[cache_control.now_select_id].effect[effect_cid]

    def CSE(self):
        """展开CSE菜单"""
        if cache_control.now_select_id != "":
            menu = CSEMenu()
            menu.exec()


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
        self.cvp_text = QLabel("用于实现指令状态方面的综合型万用结算，目前仅支持触发玩家的指令")
        self.cvp_text.setFont(self.font)
        self.layout.addWidget(self.cvp_text)

        self.text_label = QLabel("玩家对")
        self.text_label.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.text_label)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cvp_a = QComboBox()
        # self.cvp_a.addItems(["自己", "交互对象", "角色id为"])
        self.cvp_a.addItems(["自己", "交互对象"])
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
        cvp_a = self.cvp_a.currentText()
        if cvp_a == "自己":
            cvp_a_value = "A1"
        elif cvp_a == "交互对象":
            cvp_a_value = "A2"
        elif cvp_a == "角色id为":
            cvp_a_value = "A3|" + self.cvp_a2.toPlainText()
            cvp_a = "角色id为" + self.cvp_a2.toPlainText()

        # cvp_b为状态的名字，cvp_b_value为状态的cid
        cvp_b = self.status_menu.title()
        for cid in cache_control.status_data:
            if cache_control.status_data[cid] == cvp_b:
                cvp_b_value = cid
                break

        # 拼接结算字符串
        cse_str = f"综合指令状态结算  {cvp_a}{cvp_b}"
        cse_value_str = f"CSE_{cvp_a_value}_{cvp_b_value}"
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
            self.cvp_a2.setVisible(True)
        else:
            self.cvp_a2.setVisible(False)
