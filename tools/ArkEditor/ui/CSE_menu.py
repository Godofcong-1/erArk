from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QMenu,
    QComboBox,
    QMenuBar,
    QWidgetAction,
)
from PySide6.QtGui import QFont, QActionGroup
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

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
        for status_type in cache_control.behavior_type_data:
            status_menu = QMenu(status_type, self.status_menu)
            for cid in cache_control.behavior_type_data[status_type]:
                if cid is cache_control.now_behavior:
                    continue
                if cid == "0":
                    continue
                now_action: QWidgetAction = QWidgetAction(self)
                now_action.setText(cache_control.behavior_data[cid])
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
        self.status_menu.setTitle(cache_control.behavior_data[cid])
        self.status_menu.clear()
        status_group = QActionGroup(self.status_menu)
        for status_type in cache_control.behavior_type_data:
            status_menu = QMenu(status_type, self.status_menu)
            for cid in cache_control.behavior_type_data[status_type]:
                if cid == "0":
                    continue
                now_action: QWidgetAction = QWidgetAction(self)
                now_action.setText(cache_control.behavior_data[cid])
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
        cse_a_value = "A1"
        if cse_a == "自己":
            cse_a_value = "A1"
        elif cse_a == "交互对象":
            cse_a_value = "A2"
        elif cse_a == "角色id为":
            cse_a_value = "A3|" + self.cse_a2.toPlainText()
            cse_a = "角色id为" + self.cse_a2.toPlainText()

        # cse_b为状态的名字，cse_b_value为状态的cid
        cse_b = self.status_menu.title()
        for cid in cache_control.behavior_data:
            if cache_control.behavior_data[cid] == cse_b:
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
