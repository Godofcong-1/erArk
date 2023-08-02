import uuid
from PySide6.QtWidgets import QListWidget, QMenuBar, QWidgetAction, QListWidgetItem, QAbstractItemView, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLabel, QGridLayout, QMenu
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QFont, QCursor
from ui.list_item import ListItem
import cache_control
import game_type


class DataList(QWidget):
    """表单主体"""

    def __init__(self):
        """初始化表单主体"""
        super(DataList, self).__init__()
        self.layout = QGridLayout(self)
        self.top_layout = QHBoxLayout()
        self.text_edit = QTextEdit("0")
        self.menu_bar: QMenuBar = None
        self.status_menu: QMenu = None
        self.type_menu: QMenu = None
        self.list_widget = QListWidget()
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        self.list_widget.setFont(self.font)
        self.close_flag = 1
        self.edited_item = self.list_widget.currentItem()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.right_button_menu)
        self.update_clear = 0

        # 连接 self.text_edit 的 textChanged 信号到 update_adv_id 方法
        self.text_edit.textChanged.connect(self.update_adv_id)

        # 初始化菜单
        self.menu_bar = QMenuBar(self)
        self.status_menu: QMenu = QMenu(cache_control.status_data[cache_control.now_status], self)
        self.type_menu : QMenu = QMenu(cache_control.now_type, self)
        self.menu_bar.addMenu(self.status_menu)
        self.menu_bar.addMenu(self.type_menu)
        self.status_menu.setFont(self.font)
        self.type_menu.setFont(self.font)

        # 说明文本
        label1_text = QLabel("角色id")
        label2_text = QLabel("触发指令与状态")

        # 上方布局
        self.top_layout.addWidget(label1_text)
        self.top_layout.addWidget(self.text_edit)
        self.top_layout.addWidget(label2_text)
        self.top_layout.addWidget(self.menu_bar)

        # 设置编辑框的高度和宽度
        self.text_edit.setFixedHeight(32)
        self.text_edit.setFixedWidth(40)

        # 总布局
        self.layout.addLayout(self.top_layout, 0, 0)
        self.layout.addWidget(self.list_widget, 1, 0, 1, 6)


    def right_button_menu(self, old_position):
        """
        右键菜单
        Keyword arguments:
        position -- 鼠标点击位置
        """
        menu = QMenu()
        if not len(cache_control.now_file_path):
            return
        create_action: QWidgetAction = QWidgetAction(self)
        create_action.setText("新增事件")
        create_action.triggered.connect(self.create_event)
        menu.addAction(create_action)
        menu.setFont(self.font)
        position = QCursor.pos()
        font = QFont()
        font.setPointSize(13)
        if self.list_widget.itemAt(old_position):
            copy_action: QWidgetAction = QWidgetAction(self)
            copy_action.setText("复制事件")
            copy_action.triggered.connect(self.copy_event)
            menu.addAction(copy_action)
            delete_action: QWidgetAction = QWidgetAction(self)
            delete_action.setText("删除事件")
            delete_action.triggered.connect(self.delete_event)
            menu.addAction(delete_action)
        menu.exec(position)

    def create_event(self):
        """新增事件"""
        item = ListItem("空事件")
        item.uid = str(uuid.uuid4())
        event = game_type.Event()
        event.uid = item.uid
        event.status_id = cache_control.now_status
        event.adv_id = cache_control.now_adv_id
        if cache_control.now_type == "指令正常":
            event.type = 1
        elif cache_control.now_type == "跳过指令":
            event.type = 0
        elif cache_control.now_type == "事件后置":
            event.type = 2
        event.text = item.text()
        cache_control.now_event_data[event.uid] = event
        self.list_widget.addItem(item)

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
        for premise in old_event.premise:
            event.premise[premise] = old_event.premise[premise]
        for effect in old_event.effect:
            event.effect[effect] = old_event.effect[effect]
        event.text = old_event.text + "(复制)"
        cache_control.now_event_data[event.uid] = event
        self.list_widget.insertItem(event_index + 1, new_item)

    def update_adv_id(self):
        """根据文本编辑框更新当前的角色id"""
        cache_control.now_adv_id = self.text_edit.toPlainText()
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].adv_id = cache_control.now_adv_id
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].adv_id = cache_control.now_adv_id

    def update(self):
        """根据选项刷新当前绘制的列表"""
        self.update_clear = 1
        self.edited_item = None
        self.list_widget.clear()
        self.update_clear = 0

        if cache_control.now_edit_type_flag == 0:
            for uid in cache_control.now_talk_data:
                now_talk: game_type.Talk = cache_control.now_talk_data[uid]
                item = ListItem(now_talk.text)
                item.uid = uid
                self.list_widget.addItem(item)
            if cache_control.now_select_id:
                now_cid = cache_control.now_talk_data[cache_control.now_select_id].status_id
                status_text = cache_control.status_data[now_cid]
                chara_id = cache_control.now_talk_data[cache_control.now_select_id].adv_id
                self.status_menu.setTitle(status_text)
                self.text_edit.setText(chara_id)

        elif cache_control.now_edit_type_flag == 1:
            type_text_list = ["指令正常", "跳过指令", "事件后置"]
            for uid in cache_control.now_event_data:
                now_event: game_type.Event = cache_control.now_event_data[uid]
                # if now_event.status_id != cache_control.now_status:
                #     continue
                # if type_text_list[now_event.type] != cache_control.now_type:
                #     continue
                item = ListItem(now_event.text)
                item.uid = uid
                self.list_widget.addItem(item)
            if cache_control.now_select_id:
                now_cid = cache_control.now_event_data[cache_control.now_select_id].status_id
                print(f"debug now_cid:{now_cid}")
                status_text = cache_control.status_data[now_cid]
                print(f"debug status_text:{status_text}")
                type_id = cache_control.now_event_data[cache_control.now_select_id].type
                type_text = type_text_list[type_id]
                chara_id = cache_control.now_event_data[cache_control.now_select_id].adv_id
                self.status_menu.setTitle(status_text)
                self.type_menu.setTitle(type_text)
                self.text_edit.setText(chara_id)
