import uuid
from PySide6.QtWidgets import QListWidget, QMenu, QWidgetAction, QListWidgetItem, QAbstractItemView, QVBoxLayout, QWidget, QTextEdit, QLabel, QGridLayout
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
        self.text_edit_introduce = QWidget()
        self.text_edit = QTextEdit("0")
        self.menu_introduce_1 = QWidget()
        self.status_menu: QMenu = QMenu(cache_control.status_data[cache_control.now_status], self)
        self.menu_introduce_2 = QWidget()
        self.list_widget = QListWidget()
        self.font = QFont()
        self.font.setPointSize(12)
        self.list_widget.setFont(self.font)
        self.close_flag = 1
        self.edited_item = self.list_widget.currentItem()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.currentItemChanged.connect(self.close_edit)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.right_button_menu)
        self.update_clear = 0

        # 说明文本
        label1_text = QLabel("角色id")
        label1_layout = QVBoxLayout()
        label1_layout.addWidget(label1_text)
        self.text_edit_introduce.setLayout(label1_layout)
        label2_text = QLabel("触发指令")
        label2_layout = QVBoxLayout()
        label2_layout.addWidget(label2_text)
        self.menu_introduce_1.setLayout(label2_layout)
        label3_text = QLabel("触发类型")
        label3_layout = QVBoxLayout()
        label3_layout.addWidget(label3_text)
        self.menu_introduce_2.setLayout(label3_layout)

        # 设置编辑框的高度和宽度
        self.text_edit.setFixedHeight(26)
        self.text_edit.setFixedWidth(40)

        # 加入布局
        self.layout.addWidget(self.text_edit_introduce, 0, 0)
        self.layout.addWidget(self.text_edit, 0, 1)
        self.layout.addWidget(self.menu_introduce_1, 0, 2)
        self.layout.addWidget(self.status_menu, 0, 3)
        self.layout.addWidget(self.menu_introduce_2, 0, 4)
        self.layout.addWidget(self.status_menu, 0, 5)
        self.layout.addWidget(self.list_widget, 1, 0, 1, 6)

    def item_double_clicked(self, model_index: QModelIndex):
        """
        双击事件
        Keyword arguments:
        model_index -- 事件序号
        """
        self.close_edit()
        item = self.item(model_index.row())
        self.edited_item = item
        self.list_widget.openPersistentEditor(item)
        self.list_widget.editItem(item)

    def close_edit(self):
        """关闭编辑"""
        item: QListWidgetItem = self.edited_item
        if isinstance(item,QListWidgetItem) and item and self.list_widget.isPersistentEditorOpen(item):
            uid = item.uid
            cache_control.now_event_data[uid].text = item.text()
            self.list_widget.closePersistentEditor(item)

    def right_button_menu(self, old_position):
        """
        右键菜单
        Keyword arguments:
        position -- 鼠标点击位置
        """
        menu = QMenu()
        if not len(cache_control.now_file_path):
            return
        self.close_edit()
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
        if cache_control.now_type == "指令正常":
            event.type = 1
        elif cache_control.now_type == "跳过指令":
            event.type = 0
        elif cache_control.now_type == "事件后置":
            event.type = 2
        event.text = item.text()
        cache_control.now_event_data[event.uid] = event
        self.list_widget.addItem(item)
        self.close_edit()

    def delete_event(self):
        """删除事件"""
        event_index = self.list_widget.currentRow()
        item = self.list_widget.item(event_index)
        if not self.update_clear:
            del cache_control.now_event_data[item.uid]
        self.list_widget.takeItem(event_index)
        self.close_edit()

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
        self.close_edit()

    def update(self):
        """根据选项刷新当前绘制的列表"""
        self.update_clear = 1
        self.edited_item = None
        self.close_edit()
        self.list_widget.clear()
        self.update_clear = 0
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
        self.close_edit()
