import uuid
from PySide6.QtWidgets import QListWidget, QMenu, QWidgetAction, QListWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QFont, QCursor
from ui.list_item import ListItem
from ui.premise_menu import PremiseMenu
from ui.settle_menu import SettleMenu
import cache_control
import game_type


class DataList(QListWidget):
    """表单主体"""

    def __init__(self):
        """初始化表单主体"""
        super(DataList, self).__init__()
        self.font = QFont()
        self.font.setPointSize(14)
        self.setFont(self.font)
        self.close_flag = 1
        self.edited_item = self.currentItem()
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.doubleClicked.connect(self.item_double_clicked)
        self.currentItemChanged.connect(self.close_edit)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_button_menu)
        self.update_clear = 0

    def item_double_clicked(self, model_index: QModelIndex):
        """
        双击事件
        Keyword arguments:
        model_index -- 事件序号
        """
        self.close_edit()
        item = self.item(model_index.row())
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)

    def close_edit(self):
        """关闭编辑"""
        item: QListWidgetItem = self.edited_item
        if isinstance(item,QListWidgetItem) and item and self.isPersistentEditorOpen(item):
            uid = item.uid
            cache_control.now_event_data[uid].text = item.text()
            self.closePersistentEditor(item)

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
        if self.itemAt(old_position):
            copy_action: QWidgetAction = QWidgetAction(self)
            copy_action.setText("复制事件")
            copy_action.triggered.connect(self.copy_event)
            menu.addAction(copy_action)
            delete_action: QWidgetAction = QWidgetAction(self)
            delete_action.setText("删除事件")
            delete_action.triggered.connect(self.delete_event)
            menu.addAction(delete_action)
            premise_action: QWidgetAction = QWidgetAction(self)
            premise_action.setText("设置前提")
            premise_action.triggered.connect(self.setting_premise)
            menu.addAction(premise_action)
            clean_premise_action: QWidgetAction = QWidgetAction(self)
            clean_premise_action.setText("清除前提")
            clean_premise_action.triggered.connect(self.clean_premise)
            menu.addAction(clean_premise_action)
            settle_action: QWidgetAction = QWidgetAction(self)
            settle_action.setText("设置结算器")
            settle_action.triggered.connect(self.setting_settle)
            menu.addAction(settle_action)
            clean_settle_action: QWidgetAction = QWidgetAction(self)
            clean_settle_action.setText("清除结算器")
            clean_settle_action.triggered.connect(self.clean_settle)
            menu.addAction(clean_settle_action)
        menu.exec(position)

    def create_event(self):
        """新增事件"""
        item = ListItem("空事件")
        item.uid = str(uuid.uuid4())
        event = game_type.Event()
        event.uid = item.uid
        event.status_id = cache_control.now_status
        if cache_control.start_status == "开始":
            event.start = 1
        event.text = item.text()
        cache_control.now_event_data[event.uid] = event
        self.addItem(item)
        self.close_edit()

    def delete_event(self):
        """删除事件"""
        event_index = self.currentRow()
        item = self.item(event_index)
        if not self.update_clear:
            del cache_control.now_event_data[item.uid]
        self.takeItem(event_index)
        self.close_edit()

    def copy_event(self):
        """复制事件"""
        event_index = self.currentRow()
        old_item = self.item(event_index)
        old_event = cache_control.now_event_data[old_item.uid]
        new_item = ListItem(old_item.text() + "(复制)")
        new_item.uid = str(uuid.uuid4())
        event = game_type.Event()
        event.uid = new_item.uid
        event.status_id = old_event.status_id
        event.start = old_event.start
        for premise in old_event.premise:
            event.premise[premise] = old_event.premise[premise]
        for settle in old_event.settle:
            event.settle[settle] = old_event.settle[settle]
        event.text = old_event.text + "(复制)"
        cache_control.now_event_data[event.uid] = event
        self.insertItem(event_index + 1, new_item)
        self.close_edit()

    def setting_premise(self):
        """设置事件前提"""
        event_index = self.currentRow()
        item = self.item(event_index)
        cache_control.now_event_id = item.uid
        menu = PremiseMenu()
        menu.exec()

    def clean_premise(self):
        """清除事件前提"""
        event_index = self.currentRow()
        item = self.item(event_index)
        cache_control.now_event_data[item.uid].premise = {}
        self.close_edit()

    def setting_settle(self):
        """设置事件结算器"""
        event_index = self.currentRow()
        item = self.item(event_index)
        cache_control.now_event_id = item.uid
        menu = SettleMenu()
        menu.exec()

    def clean_settle(self):
        """清除事件结算器"""
        event_index = self.currentRow()
        item = self.item(event_index)
        cache_control.now_event_data[item.uid].settle = {}
        self.close_edit()

    def update(self):
        """根据选项刷新当前绘制的列表"""
        self.update_clear = 1
        self.edited_item = None
        self.close_edit()
        self.clear()
        self.update_clear = 0
        for uid in cache_control.now_event_data:
            now_event: game_type.Event = cache_control.now_event_data[uid]
            if now_event.status_id != cache_control.now_status:
                continue
            now_start = cache_control.start_status == "开始"
            if now_event.start != now_start:
                continue
            item = ListItem(now_event.text)
            item.uid = uid
            self.addItem(item)
        self.close_edit()
