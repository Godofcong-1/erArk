import uuid
from PySide6.QtWidgets import QListWidget, QMenuBar, QWidgetAction, QListWidgetItem, QAbstractItemView, QPushButton, QHBoxLayout, QWidget, QTextEdit, QLabel, QGridLayout, QMenu, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor, QColor
from ui.list_item import ListItem
import cache_control
import game_type
import function

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class DataList(QWidget):
    """表单主体"""

    def __init__(self):
        """初始化表单主体"""
        super(DataList, self).__init__()
        self.layout = QGridLayout(self)
        self.top_layout = QHBoxLayout()
        self.second_layout = QHBoxLayout()
        self.chara_id_text_edit = QTextEdit("0")
        self.text_id_text_edit = QTextEdit("0")
        self.text_id_change_button = QPushButton("修改序号")
        self.text_id_change_button.clicked.connect(self.update_text_id)
        self.info_button = QPushButton("使用说明书")
        self.info_button.clicked.connect(function.show_talk_introduce)
        # 新增条目、复制条目、删除条目
        self.new_text_button = QPushButton("新增条目")
        self.new_text_button.clicked.connect(self.buton_add)
        self.copy_text_button = QPushButton("复制条目")
        self.copy_text_button.clicked.connect(self.copy_text)
        self.delete_text_button = QPushButton("删除条目")
        self.delete_text_button.clicked.connect(self.delete_text)
        # 只显示当前指令
        self.select_now_instruct_check_box = QCheckBox("只显示当前指令")
        self.select_now_instruct_check_box.stateChanged.connect(self.select_now_instruct)
        self.select_now_instruct_flag = 0
        # 文本搜索框
        self.text_search_edit = QTextEdit()
        self.text_search_edit.setFixedHeight(32)
        # self.search_edit.setFixedWidth(400)
        self.text_search_edit.setPlaceholderText("根据文本内容中的关键字搜索")
        self.text_search_button = QPushButton("根据内容搜索条目")
        self.text_search_button.clicked.connect(self.text_search)
        self.text_search_reset_button = QPushButton("内容搜索重置")
        self.text_search_reset_button.clicked.connect(self.text_search_reset)
        self.text_search_flag = 0
        # 前提搜索按钮
        self.premise_search_edit = QTextEdit()
        self.premise_search_edit.setFixedHeight(32)
        self.premise_search_edit.setPlaceholderText("根据前提中的关键字搜索")
        self.premise_search_button = QPushButton("根据前提搜索条目(不含综合数值前提)")
        self.premise_search_button.clicked.connect(self.premise_search)
        self.premise_search_reset_button = QPushButton("前提搜索重置")
        self.premise_search_reset_button.clicked.connect(self.premise_search_reset)
        self.premise_search_flag = 0
        # 条目列表
        self.list_widget = QListWidget()
        self.font = font
        self.setFont(self.font)
        self.list_widget.setFont(self.font)
        self.close_flag = 1
        self.delet_text_id_flag = 1 # 是否删除条目序号相关的控件
        self.edited_item = self.list_widget.currentItem()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.right_button_menu)
        self.update_clear = 0
        self.now_in_moving_flag = False # 是否正在移动条目

        # 连接 self.text_edit 的 textChanged 信号到 update_adv_id 方法
        self.chara_id_text_edit.textChanged.connect(self.update_adv_id)
        # 初始化菜单
        self.menu_bar = QMenuBar(self)
        self.status_menu: QMenu = QMenu(cache_control.status_data[cache_control.now_status], self)
        self.type_menu : QMenu = QMenu(cache_control.now_type, self)
        self.menu_bar.addMenu(self.status_menu)
        self.menu_bar.addMenu(self.type_menu)
        self.status_menu.setFont(self.font)
        self.type_menu.setFont(self.font)

        # 根据文字长度设置菜单栏宽度
        status_menu_width = self.status_menu.fontMetrics().boundingRect(cache_control.status_data[cache_control.now_status]).width()
        type_menu_width = self.type_menu.fontMetrics().boundingRect(cache_control.now_type).width()
        menu_bar_width = max(status_menu_width, type_menu_width) * 2
        self.menu_bar.setFixedWidth(menu_bar_width)

        # 说明文本
        label1_text = QLabel("角色id")
        label2_text = QLabel("触发指令与状态")
        self.label3_text = QLabel("指令信息")
        self.label4_text = QLabel("条目序号")

        # 上方布局
        self.top_layout.addWidget(label1_text)
        self.top_layout.addWidget(self.chara_id_text_edit)
        self.top_layout.addWidget(self.label4_text)
        self.top_layout.addWidget(self.text_id_text_edit)
        self.top_layout.addWidget(self.text_id_change_button)
        self.top_layout.addWidget(self.info_button)

        self.second_layout.addWidget(self.text_search_edit)
        self.second_layout.addWidget(label2_text)
        self.second_layout.addWidget(self.menu_bar)
        self.second_layout.addWidget(self.label3_text)
        self.second_layout.addWidget(self.select_now_instruct_check_box)

        # 设置编辑框的高度和宽度
        self.chara_id_text_edit.setFixedHeight(32)
        self.chara_id_text_edit.setFixedWidth(100)
        self.text_id_text_edit.setFixedHeight(32)
        self.text_id_text_edit.setFixedWidth(100)

        # 总布局
        self.layout.addLayout(self.top_layout, 0, 0, 1, -1)
        self.layout.addLayout(self.second_layout, 1, 0, 1, -1)
        self.layout.addWidget(self.new_text_button, 2, 0)
        self.layout.addWidget(self.copy_text_button, 2, 1)
        self.layout.addWidget(self.delete_text_button, 2, 2)
        self.layout.addWidget(self.text_search_edit, 3, 0)
        self.layout.addWidget(self.text_search_button, 3, 1)
        self.layout.addWidget(self.text_search_reset_button, 3, 2)
        self.layout.addWidget(self.premise_search_edit, 4, 0)
        self.layout.addWidget(self.premise_search_button, 4, 1)
        self.layout.addWidget(self.premise_search_reset_button, 4, 2)
        self.layout.addWidget(self.list_widget, 5, 0, 1, 6)

        # 设置拉伸因子，保证新建条目、复制条目、搜索框的宽度相等
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

    def update_font(self, font):
        print(font)
        self.font = font
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

    def right_button_menu(self, old_position):
        """
        右键菜单
        Keyword arguments:
        position -- 鼠标点击位置
        """
        menu = QMenu()
        if not len(cache_control.now_file_path):
            return
        menu.setFont(self.font)
        position = QCursor.pos()

        # 移动状态下不显示移动以外的选项
        if cache_control.now_edit_type_flag == 1 and self.now_in_moving_flag == False:
            create_action: QWidgetAction = QWidgetAction(self)
            create_action.setText("新增事件")
            create_action.triggered.connect(self.create_event)
            menu.addAction(create_action)
            if self.list_widget.itemAt(old_position):
                copy_action: QWidgetAction = QWidgetAction(self)
                copy_action.setText("复制事件")
                copy_action.triggered.connect(self.copy_event)
                menu.addAction(copy_action)
                delete_action: QWidgetAction = QWidgetAction(self)
                delete_action.setText("删除事件")
                delete_action.triggered.connect(self.delete_event)
                menu.addAction(delete_action)
        elif cache_control.now_edit_type_flag == 0 and self.now_in_moving_flag == False:
            create_action: QWidgetAction = QWidgetAction(self)
            create_action.setText("新增口上")
            create_action.triggered.connect(self.create_talk)
            menu.addAction(create_action)
            if self.list_widget.itemAt(old_position):
                copy_action: QWidgetAction = QWidgetAction(self)
                copy_action.setText("复制口上")
                copy_action.triggered.connect(self.copy_talk)
                menu.addAction(copy_action)
                delete_action: QWidgetAction = QWidgetAction(self)
                delete_action.setText("删除口上")
                delete_action.triggered.connect(self.delete_talk)
                menu.addAction(delete_action)
        # 移动相关
        if self.list_widget.itemAt(old_position):
            if self.now_in_moving_flag == False:
                move_action: QWidgetAction = QWidgetAction(self)
                move_action.setText("移动该条目")
                move_action.triggered.connect(self.move_item)
                menu.addAction(move_action)
            else:
                move_up_action: QWidgetAction = QWidgetAction(self)
                move_up_action.setText("移至选中条目上方")
                move_up_action.triggered.connect(self.move_to_up)
                menu.addAction(move_up_action)
                move_down_action: QWidgetAction = QWidgetAction(self)
                move_down_action.setText("移至选中条目下方")
                move_down_action.triggered.connect(self.move_to_down)
                menu.addAction(move_down_action)
                move_cancel_action: QWidgetAction = QWidgetAction(self)
                move_cancel_action.setText("取消移动")
                move_cancel_action.triggered.connect(self.move_cancel)
                menu.addAction(move_cancel_action)
        menu.exec(position)

    def buton_add(self):
        """新增条目"""
        if cache_control.now_edit_type_flag == 1:
            self.create_event()
        elif cache_control.now_edit_type_flag == 0:
            self.create_talk()
        function.save_data()

    def copy_text(self):
        """复制条目"""
        old_item = self.list_widget.currentItem()
        if old_item is None:
            return
        if cache_control.now_edit_type_flag == 1:
            self.copy_event()
        elif cache_control.now_edit_type_flag == 0:
            self.copy_talk()
        function.save_data()

    def delete_text(self):
        """删除条目"""
        if cache_control.now_edit_type_flag == 1:
            self.delete_event()
        elif cache_control.now_edit_type_flag == 0:
            self.delete_talk()

    def text_search(self):
        """文本搜索"""
        search_text = self.text_search_edit.toPlainText()
        if not search_text:
            self.update()
            return
        self.text_search_flag = 1
        self.update()

    def text_search_reset(self):
        """重置文本搜索"""
        self.text_search_edit.setText("")
        self.text_search_flag = 0
        self.update()

    def premise_search(self):
        """前提搜索"""
        search_text = self.premise_search_edit.toPlainText()
        if not search_text:
            self.update()
            return
        self.premise_search_flag = 1
        self.update()

    def premise_search_reset(self):
        """重置前提搜索"""
        self.premise_search_edit.setText("")
        self.premise_search_flag = 0
        self.update()

    def select_now_instruct(self):
        """只显示当前指令"""
        if self.select_now_instruct_check_box.isChecked():
            self.select_now_instruct_flag = 1
        else:
            self.select_now_instruct_flag = 0
        self.update()

    def create_event(self):
        """新增事件"""
        item = ListItem("空事件")
        item.uid = str(uuid.uuid4())
        event = game_type.Event()
        event.uid = item.uid
        event.status_id = cache_control.now_status
        event.adv_id = cache_control.now_adv_id
        if cache_control.now_type == "跳过指令":
            event.type = 0
        elif cache_control.now_type == "指令前置":
            event.type = 1
        elif cache_control.now_type == "指令后置":
            event.type = 2
        event.text = item.text()
        event.effect["9999"] = 1
        cache_control.now_event_data[event.uid] = event
        self.list_widget.addItem(item)
        cache_control.now_select_id = event.uid
        self.update()

    def delete_event(self):
        """删除事件"""
        event_index = self.list_widget.currentRow()
        item = self.list_widget.item(event_index)
        if not self.update_clear:
            del cache_control.now_event_data[item.uid]
        self.list_widget.takeItem(event_index)

    def copy_event(self):
        """复制事件"""
        event_index = self.list_widget.currentRow()
        old_item = self.list_widget.item(event_index)
        old_event = cache_control.now_event_data[old_item.uid]
        new_item = ListItem(old_item.text() + "(复制)")
        new_item.uid = str(uuid.uuid4())
        event = game_type.Event()
        event.uid = new_item.uid
        event.status_id = old_event.status_id
        event.type = old_event.type
        event.adv_id = old_event.adv_id
        for premise in old_event.premise:
            event.premise[premise] = old_event.premise[premise]
        for effect in old_event.effect:
            event.effect[effect] = old_event.effect[effect]
        event.text = old_event.text + "(复制)"
        cache_control.now_event_data[event.uid] = event
        self.list_widget.insertItem(event_index + 1, new_item)
        cache_control.now_select_id = event.uid
        self.update()

    def create_talk(self):
        """新增口上"""
        item = ListItem("空口上")
        item.uid = 1
        while str(item.uid) in cache_control.now_talk_data:
            item.uid += 1
        talk = game_type.Talk()
        talk.cid = str(item.uid)
        talk.status_id = cache_control.now_status
        talk.adv_id = str(cache_control.now_adv_id)
        talk.text = item.text()
        talk.premise["high_1"] = 1
        cache_control.now_talk_data[talk.cid] = talk
        self.list_widget.addItem(item)
        cache_control.now_select_id = talk.cid
        self.update()

    def delete_talk(self):
        """删除口上"""
        talk_index = self.list_widget.currentRow()
        item = self.list_widget.item(talk_index)
        if not self.update_clear:
            del cache_control.now_talk_data[item.uid]
        self.list_widget.takeItem(talk_index)

    def copy_talk(self):
        """复制口上"""
        talk_index = self.list_widget.currentRow()
        old_item = self.list_widget.item(talk_index)
        old_talk = cache_control.now_talk_data[old_item.uid]
        new_item = ListItem(old_item.text() + "(复制)")

        new_item.uid = int(old_talk.cid) + 1
        while str(new_item.uid) in cache_control.now_talk_data:
            new_item.uid += 1

        talk = game_type.Talk()
        talk.cid = str(new_item.uid)
        talk.status_id = old_talk.status_id
        talk.adv_id = old_talk.adv_id
        for premise_id in old_talk.premise:
            talk.premise[premise_id] = old_talk.premise[premise_id]
        # talk.premise = old_talk.premise # 因为是引用类型，所以这样赋值会导致原始数据被修改
        talk.text = old_talk.text + "(复制)"
        cache_control.now_talk_data[talk.cid] = talk
        self.list_widget.insertItem(talk_index + 1, new_item)
        cache_control.now_select_id = talk.cid
        self.update()

    def move_item(self):
        """移动条目"""
        # 重置所有筛选
        self.select_now_instruct_flag = 0
        self.text_search_reset()
        self.premise_search_reset()
        self.update()
        # 设置移动标志
        self.now_in_moving_flag = True
        self.edited_item = self.list_widget.currentItem()
        if self.edited_item is not None:
            self.edited_item.setBackground(QColor("light green"))

    def move_to_up(self):
        """移至选中条目上方"""
        if self.edited_item is None:
            return
        # 获取当前选中的条目的cid
        current_select_cid = self.list_widget.currentItem().uid
        # 获取要移动的条目的cid
        need_move_cid = self.edited_item.uid
        if current_select_cid == need_move_cid:
            return
        # 获取当前选中的条目
        current_row = self.list_widget.currentRow()
        if current_row == -1:
            return
        # 判断编辑类型
        if cache_control.now_edit_type_flag == 0:
            # 将其加入临时数据中，然后删除原始数据中的要移动的条目
            cache_control.tem_talk_data[str(int(current_select_cid))] = cache_control.now_talk_data[need_move_cid]
            cache_control.tem_talk_data[str(int(current_select_cid))].cid = str(int(current_select_cid))
            del cache_control.now_talk_data[need_move_cid]
            # 更新当前选中的条目的cid
            cache_control.now_select_id = current_select_cid
            # 遍历全部条目
            for i in range(self.list_widget.count()):
                # 获取cid
                now_cid = self.list_widget.item(i).uid
                # 跳过与移动的条目相同的条目
                if now_cid == need_move_cid:
                    continue
                # 检测是否为当前选中的条目
                if now_cid == current_select_cid:
                    # 将其序号+1然后加入临时数据中
                    # print(f"debug now_cid: {now_cid},type = {type(now_cid)}")
                    cache_control.tem_talk_data[str(int(now_cid) + 1)] = cache_control.now_talk_data[now_cid]
                    cache_control.tem_talk_data[str(int(now_cid) + 1)].cid = str(int(now_cid) + 1)
                    # 删除原始数据中的当前选中的条目
                    del cache_control.now_talk_data[now_cid]
                    # 序号+1来更新当前选中的条目的cid
                    current_select_cid = str(int(current_select_cid) + 1)
            # 如果临时数据中有数据，则将其更新至原始数据中
            if len(cache_control.tem_talk_data):
                cache_control.now_talk_data.update(cache_control.tem_talk_data)
                cache_control.tem_talk_data.clear()
                self.now_in_moving_flag = False
        # 处理事件移动
        elif cache_control.now_edit_type_flag == 1:
            # print("开始处理事件移动，移动到上方")
            # 获取事件 uid
            need_move_uid = self.edited_item.uid
            # 获取当前选中的事件 uid
            current_select_item = self.list_widget.currentItem()
            if not current_select_item:
                return
            current_select_uid = current_select_item.uid
            # print(f"debug need_move_uid: {need_move_uid}, current_select_uid: {current_select_uid}")
            # 新建一个空白字典，用于存放移动后的事件
            new_event_data = {}
            # 遍历事件数据，将选中的事件之前的事件加入新的事件数据中，到选中的事件时，将要移动的事件加入新的事件数据中，然后加入选中的事件，最后将选中的事件之后的事件加入新的事件数据中
            for uid in cache_control.now_event_data:
                if uid == need_move_uid:
                    continue
                if uid == current_select_uid:
                    new_event_data[need_move_uid] = cache_control.now_event_data[need_move_uid]
                new_event_data[uid] = cache_control.now_event_data[uid]
            cache_control.now_event_data = new_event_data
            self.now_in_moving_flag = False

        # 更新界面
        self.update()

    def move_to_down(self):
        """移至选中条目下方"""
        if self.edited_item is None:
            return
        # 获取当前选中的条目的cid
        current_select_cid = self.list_widget.currentItem().uid
        # 获取要移动的条目的cid
        need_move_cid = self.edited_item.uid
        if current_select_cid == need_move_cid:
            return
        # 获取当前选中的条目
        current_row = self.list_widget.currentRow()
        if current_row == -1:
            return
        # 判断编辑类型
        if cache_control.now_edit_type_flag == 0:
            # 将其加入临时数据中，然后删除原始数据中的要移动的条目
            cache_control.tem_talk_data[str(int(current_select_cid) + 1)] = cache_control.now_talk_data[need_move_cid]
            cache_control.tem_talk_data[str(int(current_select_cid) + 1)].cid = str(int(current_select_cid) + 1)
            del cache_control.now_talk_data[need_move_cid]
            # 更新当前选中的条目的cid
            current_select_cid = str(int(current_select_cid) + 1)
            cache_control.now_select_id = current_select_cid
            # 遍历全部条目
            for i in range(self.list_widget.count()):
                # 获取cid
                now_cid = self.list_widget.item(i).uid
                # 跳过与移动的条目相同的条目
                if now_cid == need_move_cid:
                    continue
                # 检测是否为当前选中的条目
                if now_cid == current_select_cid:
                    # 将其序号+1然后加入临时数据中
                    cache_control.tem_talk_data[str(int(now_cid) + 1)] = cache_control.now_talk_data[now_cid]
                    cache_control.tem_talk_data[str(int(now_cid) + 1)].cid = str(int(now_cid) + 1)
                    # 删除原始数据中的当前选中的条目
                    del cache_control.now_talk_data[now_cid]
                    # 序号+1来更新当前选中的条目的cid
                    current_select_cid = str(int(current_select_cid) + 1)
            # 如果临时数据中有数据，则将其更新至原始数据中
            if len(cache_control.tem_talk_data):
                cache_control.now_talk_data.update(cache_control.tem_talk_data)
                cache_control.tem_talk_data.clear()
                self.now_in_moving_flag = False
        # 处理事件移动
        elif cache_control.now_edit_type_flag == 1:
            # print("开始处理事件移动，移动到下方")
            # 获取事件 uid
            need_move_uid = need_move_cid
            # 获取当前选中的事件 uid
            current_select_uid = current_select_cid
            # print(f"debug need_move_uid: {need_move_uid}, current_select_uid: {current_select_uid}")
            # 新建一个空白字典，用于存放移动后的事件
            new_event_data = {}
            # 遍历事件数据，将选中的事件之前的事件加入新的事件数据中，到选中的事件时，将要移动的事件加入新的事件数据中，然后加入选中的事件，最后将选中的事件之后的事件加入新的事件数据中
            skip_flag = False
            for uid in cache_control.now_event_data:
                if uid == need_move_uid:
                    continue
                new_event_data[uid] = cache_control.now_event_data[uid]
                if uid == current_select_uid and not skip_flag:
                    new_event_data[need_move_uid] = cache_control.now_event_data[need_move_uid]
                    skip_flag = True
                    # print(f"移动到下方，加入{need_move_uid}")
            # print(f"debug 前now_event_data: {cache_control.now_event_data}")
            cache_control.now_event_data = new_event_data
            # print(f"debug 后now_event_data: {cache_control.now_event_data}")
            self.now_in_moving_flag = False
        # 更新界面
        self.update()

    def move_cancel(self):
        """取消移动"""
        self.now_in_moving_flag = False
        self.edited_item.setBackground(QColor("white"))

    def update_adv_id(self):
        """根据文本编辑框更新当前的角色id"""
        cache_control.now_adv_id = self.chara_id_text_edit.toPlainText()
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].adv_id = cache_control.now_adv_id
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].adv_id = cache_control.now_adv_id

    def update_text_id(self):
        """根据文本编辑框更新当前的条目序号"""
        now_text_id = self.text_id_text_edit.toPlainText()
        # 如果不是int，弹出提示
        if not now_text_id.isdigit():
            self.text_id_text_edit.setText("请输入正整数")
            return
        if cache_control.now_edit_type_flag == 0:
            # 检查是否有已经有该条目序号，有的话弹出提示
            if now_text_id in cache_control.now_talk_data:
                self.text_id_text_edit.setText(f"已有{now_text_id}号")
                return
            cache_control.now_talk_data[now_text_id] = cache_control.now_talk_data[cache_control.now_select_id]
            cache_control.now_talk_data[now_text_id].cid = now_text_id
            del cache_control.now_talk_data[cache_control.now_select_id]
            cache_control.now_select_id = now_text_id
        elif cache_control.now_edit_type_flag == 1:
            self.text_id_text_edit.setText("事件没有序号")
            return
        self.update()

    def update(self):
        """根据选项刷新当前绘制的列表"""
        self.edited_item = None
        self.list_widget.clear()
        self.update_clear = 0
        status_cid = cache_control.now_status
        self.now_in_moving_flag = False

        if cache_control.now_edit_type_flag == 0:
            # 按cid排序整个cache_control.now_talk_data
            cache_control.now_talk_data = dict(sorted(cache_control.now_talk_data.items(), key=lambda x: int(x[0])))
            # self.menu_bar 中去掉 self.type_menu
            self.menu_bar.removeAction(self.type_menu.menuAction())
            for cid in cache_control.now_talk_data:
                now_talk: game_type.Talk = cache_control.now_talk_data[cid]
                item_text = f"{now_talk.cid} | " + now_talk.text
                item = ListItem(item_text)
                item.uid = cid
                # 仅显示当前指令
                if self.select_now_instruct_flag:
                    if now_talk.status_id != cache_control.now_status:
                        continue
                # 搜索
                if self.text_search_flag:
                    if self.text_search_edit.toPlainText() not in item.text():
                        continue
                if self.premise_search_flag:
                    premise_flag = 0
                    for premise_id in now_talk.premise:
                        premise_name = cache_control.premise_data[premise_id]
                        if self.premise_search_edit.toPlainText() in premise_name:
                            premise_flag = 1
                            break
                    if not premise_flag:
                        continue
                self.list_widget.addItem(item)
            if cache_control.now_select_id:
                status_cid = cache_control.now_talk_data[cache_control.now_select_id].status_id
                status_text = cache_control.status_data[status_cid]
                chara_id = cache_control.now_talk_data[cache_control.now_select_id].adv_id
                cache_control.now_status = status_cid
                self.status_menu.setTitle(status_text)
                self.chara_id_text_edit.setText(chara_id)
                self.text_id_text_edit.setText(cache_control.now_select_id)
                # self.text_id_text_edit.setText(cache_control.now_talk_data[cache_control.now_select_id].cid)

                # 遍历 list_widget 中的所有 item
                for i in range(self.list_widget.count()):
                    item = self.list_widget.item(i)
                    # 如果 item 的 uid 等于 now_select_id，则将其滚动到可见区域的中心位置
                    if item.uid == cache_control.now_select_id:
                        self.list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                        # 设置 item 的背景色为淡蓝色
                        item.setBackground(QColor("light blue"))
                        # 将其设定为当前行
                        self.list_widget.setCurrentItem(item)
                        break

        elif cache_control.now_edit_type_flag == 1:

            # 清除self.info_button的连接
            self.info_button.clicked.disconnect()
            self.info_button.clicked.connect(function.show_event_introduce)

            # 如果还没有删除，则删除self.label4_text和self.text_id_text_edit和self.text_id_change_button
            if self.delet_text_id_flag:
                self.delet_text_id_flag = 0
                self.label4_text.deleteLater()
                self.text_id_text_edit.deleteLater()
                self.text_id_change_button.deleteLater()

                if self.second_layout.parent() is not None:
                    # 如果有父级，尝试将其从父级中移除
                    self.second_layout.setParent(None)

                self.layout.addLayout(self.second_layout, 1, 1, 1, -1)

            type_text_list = ["跳过指令", "指令前置", "指令后置"]
            for uid in cache_control.now_event_data:
                now_event: game_type.Event = cache_control.now_event_data[uid]
                # if now_event.status_id != cache_control.now_status:
                #     continue
                # if type_text_list[now_event.type] != cache_control.now_type:
                #     continue
                if self.select_now_instruct_flag:
                    if now_event.status_id != cache_control.now_status:
                        continue
                if self.text_search_flag:
                    if self.text_search_edit.toPlainText() not in now_event.text:
                        continue
                if self.premise_search_flag:
                    premise_flag = 0
                    for premise_id in now_event.premise:
                        premise_name = cache_control.premise_data[premise_id]
                        if self.premise_search_edit.toPlainText() in premise_name:
                            premise_flag = 1
                            break
                    if not premise_flag:
                        continue
                item = ListItem(now_event.text)
                item.uid = uid
                self.list_widget.addItem(item)
            if cache_control.now_select_id and cache_control.now_select_id in cache_control.now_event_data:
                status_cid = cache_control.now_event_data[cache_control.now_select_id].status_id
                status_text = cache_control.status_data[status_cid]
                type_id = cache_control.now_event_data[cache_control.now_select_id].type
                type_text = type_text_list[type_id]
                chara_id = cache_control.now_event_data[cache_control.now_select_id].adv_id
                cache_control.now_status = status_cid
                self.status_menu.setTitle(status_text)
                self.type_menu.setTitle(type_text)
                self.chara_id_text_edit.setText(str(chara_id))

                # 遍历 list_widget 中的所有 item
                for i in range(self.list_widget.count()):
                    item = self.list_widget.item(i)
                    # 如果 item 的 uid 等于 now_select_id，则将其滚动到可见区域的中心位置
                    if item.uid == cache_control.now_select_id:
                        self.list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                        # 设置 item 的背景色为淡蓝色
                        item.setBackground(QColor("light blue"))
                        # 将其设定为当前行
                        self.list_widget.setCurrentItem(item)
                        break

        # 更新状态耗时与触发人信息
        status_duration = int(cache_control.status_all_data[status_cid]["duration"])
        status_trigger = cache_control.status_all_data[status_cid]["trigger"]
        info_text = "耗时"
        if status_duration >= 0:
            info_text += f"{status_duration}分"
        else:
            info_text += "不定"
        info_text += ",触发人:"
        if status_trigger == "pl":
            info_text += "仅玩家"
        elif status_trigger == "npc":
            info_text += "仅npc"
        elif status_trigger == "both":
            info_text += "玩家和npc均可"
        self.label3_text.setText(info_text)
