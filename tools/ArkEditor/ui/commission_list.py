# -*- coding: utf-8 -*-
"""
委托列表UI组件
功能：
    - 显示所有外勤委托（左侧列表）
    - 点击后发出信号，主窗口可根据选中项显示详细属性
"""
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor, QFont
import game_type
import cache_control
font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class CommissionListWidget(QWidget):
    """
    外勤委托列表控件（带搜索栏和右键菜单）
    输入：
        commissions: list[Commission] 委托对象列表
    输出：
        emit commission_selected(Commission) 信号，表示选中某个委托
    """
    commission_selected = Signal(object)
    commission_add = Signal()  # 新增条目信号
    commission_copy = Signal(object)  # 复制条目信号
    commission_delete = Signal(object)  # 删除条目信号

    def __init__(self, commissions, parent=None):
        super().__init__(parent)
        self.commissions = commissions  # 原始数据
        self.filtered_commissions = commissions.copy()  # 搜索过滤后的数据
        # 主布局
        self.layout = QVBoxLayout(self)
        # 搜索栏布局
        self.search_layout = QHBoxLayout()
        self.search_edit = QTextEdit()
        self.search_edit.setFixedHeight(32)
        self.search_edit.setPlaceholderText("输入关键字")
        self.search_name_btn = QPushButton("按委托名搜索")
        self.search_desc_btn = QPushButton("按描述搜索")
        self.reset_btn = QPushButton("重置")
        self.search_name_btn.clicked.connect(self.search_by_name)
        self.search_desc_btn.clicked.connect(self.search_by_desc)
        self.reset_btn.clicked.connect(self.reset_search)
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addWidget(self.search_name_btn)
        self.search_layout.addWidget(self.search_desc_btn)
        self.search_layout.addWidget(self.reset_btn)
        self.layout.addLayout(self.search_layout)
        # 列表控件
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.refresh_list()
        # 设置全局字体
        self.search_edit.setFont(font)
        self.search_name_btn.setFont(font)
        self.search_desc_btn.setFont(font)
        self.reset_btn.setFont(font)
        # 启用拖拽移动功能
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.model().rowsMoved.connect(self.on_rows_moved)

    def refresh_list(self):
        """
        刷新列表内容，根据当前过滤结果显示
        """
        self.list_widget.clear()
        for commission in self.filtered_commissions:
            item = QListWidgetItem(f"{commission.cid} {commission.name}")
            item.setData(1000, commission)
            self.list_widget.addItem(item)

    def search_by_name(self):
        """
        按委托名搜索
        """
        keyword = self.search_edit.toPlainText().strip()
        if not keyword:
            self.filtered_commissions = self.commissions.copy()
        else:
            self.filtered_commissions = [c for c in self.commissions if keyword in c.name]
        self.refresh_list()

    def search_by_desc(self):
        """
        按描述文本搜索
        """
        keyword = self.search_edit.toPlainText().strip()
        if not keyword:
            self.filtered_commissions = self.commissions.copy()
        else:
            self.filtered_commissions = [c for c in self.commissions if keyword in c.description]
        self.refresh_list()

    def reset_search(self):
        """
        重置搜索，显示全部条目
        """
        self.search_edit.setText("")
        self.filtered_commissions = self.commissions.copy()
        self.refresh_list()

    def on_item_clicked(self, item):
        """
        处理点击事件，发出选中信号
        """
        commission = item.data(1000)
        self.commission_selected.emit(commission)

    def add_commission(self):
        """
        新增委托条目，自动生成唯一ID和默认名称，插入到列表顶部
        """
        # 生成新ID，取当前最大ID+1
        if self.commissions:
            new_cid = max(c.cid for c in self.commissions) + 1
        else:
            new_cid = 1
        new_commission = game_type.Commission(
            cid=new_cid,
            name="新委托",
            country_id=0,
            level=1,
            type="",
            people=1,
            time=1,
            demand="",
            reward="",
            related_id=-1,
            special=0,
            description=""
        )
        self.commissions.insert(0, new_commission)
        self.filtered_commissions = self.commissions.copy()
        self.refresh_list()
        # 选中新建条目
        self.list_widget.setCurrentRow(0)
        self.commission_selected.emit(new_commission)

    def copy_commission(self, commission):
        """
        复制当前选中委托，插入到其下方
        """
        # 生成新ID
        new_cid = max(c.cid for c in self.commissions) + 1
        new_commission = game_type.Commission(
            cid=new_cid,
            name=commission.name + "(复制)",
            country_id=commission.country_id,
            level=commission.level,
            type=commission.type,
            people=commission.people,
            time=commission.time,
            demand=commission.demand,
            reward=commission.reward,
            related_id=commission.related_id,
            special=commission.special,
            description=commission.description
        )
        # 找到原条目在列表中的位置
        idx = self.commissions.index(commission)
        self.commissions.insert(idx + 1, new_commission)
        self.filtered_commissions = self.commissions.copy()
        self.refresh_list()
        # 选中复制后的条目
        self.list_widget.setCurrentRow(idx + 1)
        self.commission_selected.emit(new_commission)

    def delete_commission(self, commission):
        """
        删除当前选中委托
        """
        if commission in self.commissions:
            idx = self.commissions.index(commission)
            self.commissions.remove(commission)
            self.filtered_commissions = self.commissions.copy()
            self.refresh_list()
            # 选中上一个或下一个
            if self.commissions:
                new_idx = max(0, idx - 1)
                self.list_widget.setCurrentRow(new_idx)
                self.commission_selected.emit(self.commissions[new_idx])

    def show_context_menu(self, pos):
        """
        右键菜单，包含新增、复制、删除，直接调用内部操作
        """
        menu = QMenu(self)
        add_action = menu.addAction("新增条目")
        copy_action = menu.addAction("复制条目")
        delete_action = menu.addAction("删除条目")
        item = self.list_widget.itemAt(pos)
        add_action.triggered.connect(self.add_commission)
        if item:
            commission = item.data(1000)
            copy_action.triggered.connect(lambda: self.copy_commission(commission))
            delete_action.triggered.connect(lambda: self.delete_commission(commission))
        else:
            copy_action.setEnabled(False)
            delete_action.setEnabled(False)
        menu.exec(QCursor.pos())

    def update_commissions(self, commissions):
        """
        外部数据变动时可调用此方法刷新数据
        """
        self.commissions = commissions
        self.filtered_commissions = commissions.copy()
        self.refresh_list()

    def on_rows_moved(self, parent, start, end, dest, row):
        """
        拖拽移动条目后，更新self.commissions和self.filtered_commissions的顺序
        参数:
            start: int 被拖动的起始行
            end: int 被拖动的结束行（通常等于start）
            row: int 目标插入位置
        """
        # 只支持单条目拖动
        if start == end:
            item = self.filtered_commissions.pop(start)
            # 拖到下方时row会+1，需修正
            if row > start:
                row = row - 1
            self.filtered_commissions.insert(row, item)
            # 同步原始数据顺序
            # 先清空self.commissions，再按filtered顺序重排
            id_map = {c.cid: c for c in self.commissions}
            self.commissions.clear()
            for c in self.filtered_commissions:
                self.commissions.append(id_map[c.cid])
        # 刷新列表，保持当前顺序
        self.refresh_list()
