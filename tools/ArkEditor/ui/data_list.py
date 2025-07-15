import uuid
from PySide6.QtWidgets import QListWidget, QMenuBar, QWidgetAction, QListWidgetItem, QAbstractItemView, QPushButton, QHBoxLayout, QWidget, QTextEdit, QLabel, QGridLayout, QMenu, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor, QColor
from ui.list_item import ListItem
import cache_control
import game_type
import function
from .data_list_change_chara_id import DataListIdEditMixin
from .data_list_move_item import move_item, move_to_up, move_to_down, move_cancel, refresh_item_flags, on_rows_moved

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class DataList(DataListIdEditMixin, QWidget):
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

        # 初始化菜单
        self.menu_bar = QMenuBar(self)
        self.status_menu: QMenu = QMenu(cache_control.behavior_data[cache_control.now_behavior], self)
        self.type_menu : QMenu = QMenu(cache_control.now_type, self)
        self.menu_bar.addMenu(self.status_menu)
        self.menu_bar.addMenu(self.type_menu)
        self.status_menu.setFont(self.font)
        self.type_menu.setFont(self.font)

        # 修改当前角色id、修改全部角色id
        self.change_current_chara_id_button = QPushButton("修改当前角色id")
        self.change_current_chara_id_button.setToolTip("只修改当前选中条目的角色id")
        self.change_current_chara_id_button.clicked.connect(self.change_current_chara_id)
        self.change_all_chara_id_button = QPushButton("修改全部角色id")
        self.change_all_chara_id_button.setToolTip("批量修改所有条目的角色id")
        self.change_all_chara_id_button.clicked.connect(self.change_all_chara_id)

        # 根据文字长度设置菜单栏宽度
        status_menu_width = self.status_menu.fontMetrics().boundingRect(cache_control.behavior_data[cache_control.now_behavior]).width()
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
        # 将按钮插入到角色id输入框后面
        self.top_layout.addWidget(self.change_current_chara_id_button)
        self.top_layout.addWidget(self.change_all_chara_id_button)
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


        # 绑定移动相关方法到实例
        self.move_item = move_item.__get__(self)
        self.move_to_up = move_to_up.__get__(self)
        self.move_to_down = move_to_down.__get__(self)
        self.move_cancel = move_cancel.__get__(self)
        self.refresh_item_flags = refresh_item_flags.__get__(self)
        self.on_rows_moved = on_rows_moved.__get__(self)

        # 启用条目拖拽移动功能
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.model().rowsMoved.connect(self.on_rows_moved)

        # 撤销功能：用于存储最近操作的条目信息的栈
        # 每个元素为字典，包含type、item、数据对象、原始索引等
        self.undo_stack = []

        # 快捷键Ctrl+Z绑定撤销操作
        from PySide6.QtGui import QKeySequence, QShortcut
        self.undo_shortcut = QShortcut(QKeySequence('Ctrl+Z'), self)
        self.undo_shortcut.activated.connect(self.undo_delete)
        # 绑定Delete键快捷键，按下时触发删除条目
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.delete_shortcut.activated.connect(self.delete_text)

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
                delete_action.triggered.connect(self.event_delete)
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
                delete_action.triggered.connect(self.talk_delete)
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
            self.event_delete()
        elif cache_control.now_edit_type_flag == 0:
            self.talk_delete()

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
        event.behavior_id = cache_control.now_behavior
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
        self.refresh_item_flags()
        cache_control.now_select_id = event.uid
        # 新增：将新增操作推入撤销栈
        row = self.list_widget.count() - 1
        self.undo_stack.append({
            'type': 'event_add',
            'uid': event.uid,
            'row': row
        })
        self.update()

    def event_delete(self):
        """
        删除事件，并支持撤销（Ctrl+Z）
        无参数，无返回值。
        """
        event_index = self.list_widget.currentRow()
        item = self.list_widget.item(event_index)
        if item is None:
            return
        # 记录删除前的事件数据到撤销栈
        if not self.update_clear:
            event_data = cache_control.now_event_data[item.uid]
            # 深拷贝事件对象，防止后续修改影响撤销内容
            import copy
            event_copy = copy.deepcopy(event_data)
            item_copy = ListItem(item.text())
            item_copy.uid = item.uid
            self.undo_stack.append({
                'type': 'event_delete',
                'uid': item.uid,
                'data': event_copy,
                'item': item_copy,
                'row': event_index
            })
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
        event.behavior_id = old_event.behavior_id
        event.type = old_event.type
        event.adv_id = old_event.adv_id
        for premise in old_event.premise:
            event.premise[premise] = old_event.premise[premise]
        for effect in old_event.effect:
            event.effect[effect] = old_event.effect[effect]
        event.text = old_event.text + "(复制)"
        cache_control.now_event_data[event.uid] = event
        insert_row = event_index + 1
        self.list_widget.insertItem(insert_row, new_item)
        cache_control.now_select_id = event.uid
        # 新增：将复制操作推入撤销栈
        self.undo_stack.append({
            'type': 'event_copy',
            'uid': event.uid,
            'row': insert_row
        })
        self.update()

    def create_talk(self):
        """新增口上"""
        item = ListItem("空口上")
        item.uid = 1
        while str(item.uid) in cache_control.now_talk_data:
            item.uid += 1
        talk = game_type.Talk()
        talk.cid = str(item.uid)
        talk.behavior_id = cache_control.now_behavior
        talk.adv_id = str(cache_control.now_adv_id)
        talk.text = item.text()
        talk.premise["high_1"] = 1
        cache_control.now_talk_data[talk.cid] = talk
        self.list_widget.addItem(item)
        self.refresh_item_flags()
        cache_control.now_select_id = talk.cid
        # 新增：将新增操作推入撤销栈
        row = self.list_widget.count() - 1
        self.undo_stack.append({
            'type': 'talk_add',
            'uid': talk.cid,
            'row': row
        })
        self.update()

    def talk_delete(self):
        """
        删除口上，并支持撤销（Ctrl+Z）
        无参数，无返回值。
        """
        talk_index = self.list_widget.currentRow()
        item = self.list_widget.item(talk_index)
        if item is None:
            return
        # 记录删除前的口上数据到撤销栈
        if not self.update_clear:
            talk_data = cache_control.now_talk_data[item.uid]
            import copy
            talk_copy = copy.deepcopy(talk_data)
            item_copy = ListItem(item.text())
            item_copy.uid = item.uid
            self.undo_stack.append({
                'type': 'talk_delete',
                'uid': item.uid,
                'data': talk_copy,
                'item': item_copy,
                'row': talk_index
            })
            del cache_control.now_talk_data[item.uid]
        self.list_widget.takeItem(talk_index)

    def copy_talk(self):
        """复制口上
        无参数，无返回值。
        新条目插入到符合其cid编号的顺序位置。
        """
        talk_index = self.list_widget.currentRow()
        old_item = self.list_widget.item(talk_index)
        old_talk = cache_control.now_talk_data[old_item.uid]
        new_item = ListItem(old_item.text() + "(复制)")
        # 计算新cid
        new_item.uid = int(old_talk.cid) + 1
        while str(new_item.uid) in cache_control.now_talk_data:
            new_item.uid += 1
        talk = game_type.Talk()
        talk.cid = str(new_item.uid)
        talk.behavior_id = old_talk.behavior_id
        talk.adv_id = old_talk.adv_id
        for premise_id in old_talk.premise:
            talk.premise[premise_id] = old_talk.premise[premise_id]
        talk.text = old_talk.text + "(复制)"
        # 在数据字典按cid顺序插入
        from collections import OrderedDict
        items = list(cache_control.now_talk_data.items())
        insert_index = len(items)
        for i, (cid, _) in enumerate(items):
            try:
                if int(cid) > new_item.uid:
                    insert_index = i
                    break
            except Exception:
                continue
        items.insert(insert_index, (talk.cid, talk))
        cache_control.now_talk_data = OrderedDict(items)
        self.update()
        # update后，找到新条目并高亮
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if hasattr(item, 'uid') and str(item.uid) == talk.cid:
                self.list_widget.setCurrentRow(i)
                self.list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                break
        cache_control.now_select_id = talk.cid
        # 新增：将复制操作推入撤销栈
        self.undo_stack.append({
            'type': 'talk_copy',
            'uid': talk.cid,
            'row': insert_index
        })
        self.update()

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

    def _insert_dict_at(self, d, key, value, index):
        """
        辅助函数：将key-value插入到字典d的指定index位置，返回新字典。
        参数：
            d (dict): 原字典
            key: 要插入的key
            value: 要插入的value
            index (int): 插入位置
        返回：
            dict: 新字典
        """
        # 拆分为有序插入
        from collections import OrderedDict
        items = list(d.items())
        items.insert(index, (key, value))
        return OrderedDict(items)

    def undo_delete(self):
        """
        撤销上一次删除的条目（Ctrl+Z）或撤销上一次新增/复制/移动的条目
        无参数，无返回值。
        """
        if not self.undo_stack:
            return
        undo_info = self.undo_stack.pop()
        # 撤销删除
        if undo_info['type'] == 'talk_delete':
            cache_control.now_talk_data = self._insert_dict_at(
                cache_control.now_talk_data,
                undo_info['uid'],
                undo_info['data'],
                undo_info['row']
            )
            cache_control.now_select_id = undo_info['uid']
        elif undo_info['type'] == 'event_delete':
            cache_control.now_event_data = self._insert_dict_at(
                cache_control.now_event_data,
                undo_info['uid'],
                undo_info['data'],
                undo_info['row']
            )
            cache_control.now_select_id = undo_info['uid']
        # 撤销新增
        elif undo_info['type'] == 'talk_add':
            # 删除刚刚新增的口上
            if undo_info['uid'] in cache_control.now_talk_data:
                del cache_control.now_talk_data[undo_info['uid']]
            # 删除列表项
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if hasattr(item, 'uid') and item.uid == undo_info['uid']:
                    self.list_widget.takeItem(i)
                    break
            cache_control.now_select_id = None
        elif undo_info['type'] == 'event_add':
            if undo_info['uid'] in cache_control.now_event_data:
                del cache_control.now_event_data[undo_info['uid']]
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if hasattr(item, 'uid') and item.uid == undo_info['uid']:
                    self.list_widget.takeItem(i)
                    break
            cache_control.now_select_id = None
        # 撤销复制
        elif undo_info['type'] == 'talk_copy':
            if undo_info['uid'] in cache_control.now_talk_data:
                del cache_control.now_talk_data[undo_info['uid']]
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if hasattr(item, 'uid') and item.uid == undo_info['uid']:
                    self.list_widget.takeItem(i)
                    break
            cache_control.now_select_id = None
        elif undo_info['type'] == 'event_copy':
            if undo_info['uid'] in cache_control.now_event_data:
                del cache_control.now_event_data[undo_info['uid']]
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if hasattr(item, 'uid') and item.uid == undo_info['uid']:
                    self.list_widget.takeItem(i)
                    break
            cache_control.now_select_id = None
        # 撤销移动
        elif undo_info['type'] == 'talk_move':
            # 恢复口上顺序
            new_data = {uid: cache_control.now_talk_data[uid] for uid in undo_info['order'] if uid in cache_control.now_talk_data}
            cache_control.now_talk_data = new_data
            self.update()
            return
        elif undo_info['type'] == 'event_move':
            # 恢复事件顺序
            new_data = {uid: cache_control.now_event_data[uid] for uid in undo_info['order'] if uid in cache_control.now_event_data}
            cache_control.now_event_data = new_data
            self.update()
            return
        self.update()
        # update后自动定位到该行（仅对删除撤销有效）
        if 'uid' in undo_info and undo_info['type'] in ('talk_delete', 'event_delete'):
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if hasattr(item, 'uid') and item.uid == undo_info['uid']:
                    self.list_widget.setCurrentRow(i)
                    self.list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                    break

    def update(self):
        """根据选项刷新当前绘制的列表"""
        self.edited_item = None
        self.list_widget.clear()
        self.update_clear = 0
        status_cid = cache_control.now_behavior
        self.now_in_moving_flag = False

        if cache_control.now_edit_type_flag == 0:
            # 不再排序，直接按当前字典顺序遍历
            # cache_control.now_talk_data = dict(sorted(cache_control.now_talk_data.items(), key=lambda x: int(x[0])))
            self.menu_bar.removeAction(self.type_menu.menuAction())
            for cid in cache_control.now_talk_data:
                now_talk: game_type.Talk = cache_control.now_talk_data[cid]
                item_text = f"{now_talk.cid} | " + now_talk.text
                item = ListItem(item_text)
                item.uid = cid
                # 仅显示当前指令
                if self.select_now_instruct_flag:
                    if now_talk.behavior_id != cache_control.now_behavior:
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
            if cache_control.now_select_id and cache_control.now_select_id in cache_control.now_talk_data:
                status_cid = cache_control.now_talk_data[cache_control.now_select_id].behavior_id
                status_text = cache_control.behavior_data[status_cid]
                chara_id = cache_control.now_talk_data[cache_control.now_select_id].adv_id
                cache_control.now_behavior = status_cid
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
                    if now_event.behavior_id != cache_control.now_behavior:
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
                status_cid = cache_control.now_event_data[cache_control.now_select_id].behavior_id
                status_text = cache_control.behavior_data[status_cid]
                type_id = cache_control.now_event_data[cache_control.now_select_id].type
                type_text = type_text_list[type_id]
                chara_id = cache_control.now_event_data[cache_control.now_select_id].adv_id
                cache_control.now_behavior = status_cid
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
        status_duration = int(cache_control.behavior_all_data[status_cid]["duration"])
        status_trigger = cache_control.behavior_all_data[status_cid]["trigger"]
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
