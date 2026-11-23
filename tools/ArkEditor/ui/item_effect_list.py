from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QMenu, QComboBox, QTextEdit, QMenuBar, QWidgetAction
from PySide6.QtGui import QFont, QActionGroup
from PySide6.QtCore import Qt
import cache_control
from ui.effect_menu import EffectMenu
from ui.CVE_menu import CVEMenu
from ui.CSE_menu import CSEMenu

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
        change_button.setObjectName("btn_change_all")
        change_button.clicked.connect(self.change)
        button_layout1.addWidget(change_button)
        reset_button = QPushButton("整体清零")
        reset_button.setObjectName("btn_reset_all")
        reset_button.clicked.connect(self.reset)
        button_layout1.addWidget(reset_button)
        title_layout.addLayout(button_layout1)
        main_layout.addLayout(title_layout)

        button_layout2 = QHBoxLayout()
        CVE_button = QPushButton("综合型基础数值结算")
        CVE_button.clicked.connect(self.CVE)
        button_layout2.addWidget(CVE_button)
        CSE_button = QPushButton("综合指令状态结算")
        CSE_button.clicked.connect(self.CSE)
        button_layout2.addWidget(CSE_button)
        title_layout.addLayout(button_layout2)
        # 文字说明
        info_label = QLabel()
        info_label.setText("双击替换，右键展开删除、复制、粘贴菜单")
        # 结算列表布局
        list_layout = QHBoxLayout()
        self.item_list = QListWidget()
        self.item_list.setWordWrap(True)
        self.item_list.adjustSize()
        self.item_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.item_list.customContextMenuRequested.connect(self.show_context_menu)
        self.item_list.itemDoubleClicked.connect(self.change_this_item)
        # 启用拖拽移动功能
        self.item_list.setDragDropMode(QListWidget.InternalMove)
        self.item_list.setDefaultDropAction(Qt.MoveAction)
        self.item_list.setSelectionMode(QListWidget.SingleSelection)
        self.item_list.model().rowsMoved.connect(self.on_rows_moved)
        list_layout.addWidget(self.item_list)
        main_layout.addWidget(info_label)
        main_layout.addLayout(list_layout)
        self.setLayout(main_layout)

    def update(self):
        """更新结算列表"""
        self.item_list.clear()
        data = self.selected_event()
        if data is not None:
            for effect in data.effect:
                item = QListWidgetItem(cache_control.effect_data[effect])
                item.setToolTip(item.text())
                self.item_list.addItem(item)

    def selected_event(self):
        """
        取当前选中的事件
        参数:
            无
        返回:
            Event 或 None: 当前选中的事件；编辑的不是事件文件、没有选中条目、或选中的条目已不在当前文件里时为 None（口上没有结算）
        """
        if cache_control.now_edit_type_flag != 1:
            return None
        return cache_control.now_event_data.get(cache_control.now_select_id)

    def change(self):
        """展开结算菜单"""
        if self.selected_event() is not None:
            menu = EffectMenu()
            menu.exec()

    def change_this_item(self, item):
        """删除该结算并展开结算菜单"""
        data = self.selected_event()
        if data is None:
            return
        self.item_list.takeItem(self.item_list.row(item))
        effect_cid = ""
        for effect in cache_control.effect_data:
            if cache_control.effect_data[effect] == item.text():
                effect_cid = effect
                break
        if effect_cid in data.effect:
            del data.effect[effect_cid]
        menu = EffectMenu()
        menu.exec()

    def reset(self):
        """清零结算列表"""
        data = self.selected_event()
        if data is not None:
            data.effect = {}
            self.item_list.clear()

    def show_context_menu(self, pos):
        """右键菜单：删除、复制、粘贴结算
        参数:
            pos (QPoint): 鼠标点击的位置
        返回:
            None
        """
        # 获取当前位置对应的列表项
        item = self.item_list.itemAt(pos)
        if item is not None:
            # 遍历寻找当前结算的cid，匹配结算文本
            effect_cid = ""
            for effect in cache_control.effect_data:
                if cache_control.effect_data[effect] == item.text():
                    effect_cid = effect
                    break
            # 结算数据只在选中的事件上（口上没有结算；换过文件后上一个文件的选中条目已不存在）
            data = self.selected_event()
            # 创建右键菜单
            menu = QMenu(self)
            delete_action = menu.addAction("删除")  # 添加“删除”按钮，删除当前结算
            copy_action = menu.addAction("复制")    # 添加“复制”按钮，复制当前结算
            paste_action = menu.addAction("粘贴")    # 添加“粘贴”按钮，将复制的结算粘贴到列表中
            # 没有选中事件时，删除与粘贴不可选
            delete_action.setEnabled(data is not None)
            paste_action.setEnabled(data is not None)
            # 显示菜单并等待用户选择操作
            action = menu.exec_(self.item_list.mapToGlobal(pos))
            # 如果选择删除操作
            if action == delete_action and data is not None:
                # 从列表中删除该项
                self.item_list.takeItem(self.item_list.row(item))
                # 根据cid删除数据对象中的结算
                if effect_cid in data.effect:
                    del data.effect[effect_cid]
            # 如果选择复制操作
            elif action == copy_action:
                # 将当前结算的cid存入全局复制变量
                cache_control.now_copied_effect = effect_cid
            # 如果选择粘贴操作
            elif action == paste_action and data is not None:
                # 从全局复制变量中获取结算cid
                effect_cid = cache_control.now_copied_effect
                # 检查复制变量是否有内容
                if effect_cid != "":
                    # 如果存在结算组，则将组中所有结算添加到数据对象中
                    if effect_cid in cache_control.effect_group_data:
                        for now_cid in cache_control.effect_group_data[effect_cid]:
                            data.effect[now_cid] = 1
                    # 如果不存在结算组，则直接添加该结算
                    else:
                        data.effect[effect_cid] = 1
                    # 在列表中添加新的结算项
                    self.item_list.addItem(cache_control.effect_data[cache_control.now_copied_effect])

    def CVE(self):
        """展开CVE菜单"""
        if self.selected_event() is not None:
            menu = CVEMenu()
            menu.exec()

    def CSE(self):
        """展开CSE菜单"""
        if self.selected_event() is not None:
            menu = CSEMenu()
            menu.exec()

    def on_rows_moved(self, parent, start, end, dest, row):
        """
        拖拽移动结算条目后，更新数据顺序
        """
        data = self.selected_event()
        if data is not None:
            # 重新按界面顺序排列effect
            new_order = []
            for i in range(self.item_list.count()):
                text = self.item_list.item(i).text()
                # 通过文本反查cid
                for cid, val in cache_control.effect_data.items():
                    if val == text and cid in data.effect:
                        new_order.append(cid)
                        break
            # 重新构建effect字典
            new_effect = {cid: data.effect[cid] for cid in new_order}
            data.effect = new_effect
