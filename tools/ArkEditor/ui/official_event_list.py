# -*- coding: utf-8 -*-
"""
公务事件列表UI组件（Plan 23）
功能：
    - 左侧按「部门文件」分组显示全部公务事件
    - 点击后发出信号，右侧显示该事件的全部属性与四个选项块
    - 右键可新增/复制/删除条目，结构性改动**立即落盘**
      （外勤委托那边右键增删不落盘，要再点一次保存，这里不继承那个毛病）
"""
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor, QFont
import game_type
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

TITLE_TEXT_MAX = 18
""" 列表里正文预览的截断长度，只留能认出是哪条事件的开头 """


class OfficialEventListWidget(QWidget):
    """
    公务事件列表控件（带文件筛选、搜索栏与右键菜单）
    输入：
        event_list: list[OfficialEvent] 全部事件
        file_name_list: list[str] 全部事件文件名
    输出：
        emit event_selected(OfficialEvent) 选中某条事件
        emit event_changed(str) 某个文件的条目增删了，参数为文件名（不含扩展名）
    """

    event_selected = Signal(object)
    event_changed = Signal(str)

    def __init__(self, event_list, file_name_list, parent=None):
        super().__init__(parent)
        self.event_list = event_list
        """ 全部事件 """
        self.file_name_list = file_name_list
        """ 全部文件名（不含扩展名） """
        self.filtered_list = list(event_list)
        """ 筛选后的事件 """
        self.layout = QVBoxLayout(self)
        # 顶部：文件筛选 + 关键字搜索
        self.top_layout = QHBoxLayout()
        self.file_box = QComboBox()
        self.file_box.addItem("全部部门", "")
        for file_name in file_name_list:
            self.file_box.addItem(file_name, file_name)
        self.file_box.currentIndexChanged.connect(self.refresh_filter)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键字后回车")
        self.search_edit.returnPressed.connect(self.refresh_filter)
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_search)
        self.top_layout.addWidget(self.file_box)
        self.top_layout.addWidget(self.search_edit)
        self.top_layout.addWidget(self.reset_btn)
        self.layout.addLayout(self.top_layout)
        # 列表
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        for widget in (self.file_box, self.search_edit, self.reset_btn, self.list_widget):
            widget.setFont(font)
        self.refresh_list()

    def get_item_text(self, event) -> str:
        """
        取一条事件在列表里显示的文字
        参数:
            event: OfficialEvent 事件对象
        返回:
            str 显示文字
        """
        return f"[{event.file_name}] {event.cid} {event.text[:TITLE_TEXT_MAX]}"

    def refresh_list(self):
        """
        按当前筛选结果重画列表
        参数: 无
        返回: 无
        """
        self.list_widget.clear()
        for event in self.filtered_list:
            item = QListWidgetItem(self.get_item_text(event))
            item.setData(1000, event)
            item.setFont(font)
            self.list_widget.addItem(item)

    def refresh_filter(self):
        """
        按文件与关键字重新筛选
        参数: 无
        返回: 无
        """
        file_name = self.file_box.currentData()
        key_text = self.search_edit.text().strip()
        self.filtered_list = []
        for event in self.event_list:
            if file_name and event.file_name != file_name:
                continue
            if key_text and key_text not in event.text and key_text not in str(event.cid):
                continue
            self.filtered_list.append(event)
        self.refresh_list()

    def reset_search(self):
        """
        清空筛选
        参数: 无
        返回: 无
        """
        self.search_edit.clear()
        self.file_box.setCurrentIndex(0)
        self.refresh_filter()

    def on_item_clicked(self, item):
        """
        点击条目时把该事件发出去
        参数:
            item: QListWidgetItem 被点击的条目
        返回: 无
        """
        event = item.data(1000)
        if event is not None:
            self.event_selected.emit(event)

    def get_new_cid(self, file_name: str) -> str:
        """
        取该文件内下一个空闲的 cid
        参数:
            file_name: str 文件名（不含扩展名）
        返回:
            str 新的 cid
        功能:
            自动分配而不是让作者手填，手填撞号会在构建时被静默覆盖
        """
        max_cid = 0
        for event in self.event_list:
            if event.file_name != file_name:
                continue
            if str(event.cid).isdigit():
                max_cid = max(max_cid, int(event.cid))
        return str(max_cid + 1)

    def add_event(self):
        """
        在当前文件下新增一条空事件
        参数: 无
        返回: 无
        """
        file_name = self.file_box.currentData()
        if not file_name:
            # 没选具体文件时，默认加到第一个文件里
            file_name = self.file_name_list[0] if self.file_name_list else ""
        if not file_name:
            return
        template = {"cid": self.get_new_cid(file_name), "department": "15", "subject": "1", "sub_key": "0", "once": "0", "weight": "10", "premise": "", "text": "新事件"}
        event = game_type.OfficialEvent(template, file_name)
        self.event_list.append(event)
        self.refresh_filter()
        self.event_changed.emit(file_name)
        self.event_selected.emit(event)

    def copy_event(self, event):
        """
        复制一条事件
        参数:
            event: OfficialEvent 被复制的事件
        返回: 无
        """
        row = dict(zip(["cid", "department", "subject", "sub_key", "once", "weight", "premise", "text"], event.to_row()[:8]))
        row["cid"] = self.get_new_cid(event.file_name)
        new_event = game_type.OfficialEvent(row, event.file_name)
        new_event.options = [dict(one) for one in event.options]
        self.event_list.insert(self.event_list.index(event) + 1, new_event)
        self.refresh_filter()
        self.event_changed.emit(event.file_name)
        self.event_selected.emit(new_event)

    def delete_event(self, event):
        """
        删除一条事件
        参数:
            event: OfficialEvent 被删除的事件
        返回: 无
        """
        if event not in self.event_list:
            return
        self.event_list.remove(event)
        self.refresh_filter()
        self.event_changed.emit(event.file_name)

    def show_context_menu(self, pos):
        """
        右键菜单：新增、复制、删除
        参数:
            pos: QPoint 右键位置
        返回: 无
        """
        item = self.list_widget.itemAt(pos)
        menu = QMenu(self)
        menu.setFont(font)
        add_action = menu.addAction("新增事件")
        copy_action = None
        delete_action = None
        if item is not None:
            copy_action = menu.addAction("复制该事件")
            delete_action = menu.addAction("删除该事件")
        action = menu.exec(QCursor.pos())
        if action is None:
            return
        if action == add_action:
            self.add_event()
        elif copy_action is not None and action == copy_action:
            self.copy_event(item.data(1000))
        elif delete_action is not None and action == delete_action:
            self.delete_event(item.data(1000))
