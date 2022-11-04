#!/usr/bin/python3
# -*- coding: UTF-8 -*-



import sys
import json
import os

import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6.QtWidgets import QApplication, QFileDialog, QWidgetAction
from PySide6.QtGui import QActionGroup, QKeySequence, QShortcut
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import Qt
from ui.window import Window
from ui.menu_bar import MenuBar
from ui.data_list import DataList
from ui.tools_bar import ToolsBar
from ui.item_premise_list import ItemPremiseList
from ui.item_settle_list import ItemSettleList
import load_csv
import json_handle
import game_type
import cache_control

load_csv.load_config()
app = QApplication(sys.argv)
main_window: Window = Window()
menu_bar: MenuBar = MenuBar()
tools_bar: ToolsBar = ToolsBar()
data_list: DataList = DataList()
item_premise_list: ItemPremiseList = ItemPremiseList()
cache_control.item_premise_list = item_premise_list
item_settle_list: ItemSettleList = ItemSettleList()
cache_control.item_settle_list = item_settle_list

# envpath = '/home/diyun/anaconda3/envs/transformer_py38/lib/python3.8/site-packages/cv2/qt/plugins/platforms'
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath


# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = 'D:\venvforqt\Lib\site-packages\PyQt5\Qt5\plugins\platforms'


def load_event_data():
    """载入事件文件"""
    now_file = QFileDialog.getOpenFileName(menu_bar, "选择文件", ".", "*.json")
    file_path = now_file[0]
    if file_path:
        cache_control.now_file_path = file_path
        now_data = json_handle.load_json(file_path)
        for k in now_data:
            now_event: game_type.Event = game_type.Event()
            now_event.__dict__ = now_data[k]
            delete_premise_list = []
            for premise in now_event.premise:
                if premise not in cache_control.premise_data:
                    delete_premise_list.append(premise)
            for premise in delete_premise_list:
                del now_event.premise[premise]
            delete_settle_list = []
            for settle in now_event.settle:
                if settle not in cache_control.settle_data:
                    delete_settle_list.append(settle)
            for settle in delete_settle_list:
                del now_event.settle[settle]
            cache_control.now_event_data[k] = now_event
        data_list.update()


def create_event_data():
    """新建事件文件"""
    dialog:QFileDialog = QFileDialog(menu_bar)
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setNameFilter("Json (*.json)")
    if dialog.exec():
        file_names = dialog.selectedFiles()
        file_path: str = file_names[0]
        if not file_path.endswith(".json"):
            file_path += ".json"
            cache_control.now_file_path = file_path


def save_event_data():
    """保存事件文件"""
    data_list.close_edit()
    if len(cache_control.now_file_path):
        with open(cache_control.now_file_path, "w", encoding="utf-8") as event_data_file:
            now_data = {}
            for k in cache_control.now_event_data:
                now_data[k] = cache_control.now_event_data[k].__dict__
            json.dump(now_data, event_data_file, ensure_ascii=0)


def exit_editor():
    """关闭编辑器"""
    os._exit(0)


def change_status_menu(action: QWidgetAction):
    """
    更新状态菜单
    Keyword arguments:
    action -- 触发的菜单
    """
    data_list.close_edit()
    cid = action.data()
    tools_bar.status_menu.setTitle(cache_control.status_data[cid])
    cache_control.now_status = cid
    tools_bar.status_menu.clear()
    action_list = []
    status_group = QActionGroup(tools_bar.status_menu)
    for cid in cache_control.status_data:
        if cid == cache_control.now_status:
            continue
        if cid == "0":
            continue
        now_action: QWidgetAction = QWidgetAction(tools_bar)
        now_action.setText(cache_control.status_data[cid])
        now_action.setActionGroup(status_group)
        now_action.setData(cid)
        action_list.append(now_action)
    status_group.triggered.connect(change_status_menu)
    tools_bar.status_menu.addActions(action_list)
    data_list.update()
    item_premise_list.item_list.clear()
    item_settle_list.item_list.clear()


def change_start_menu(action: QWidgetAction):
    """
    更新开始分类菜单
    Keyword arguments:
    action -- 触发的菜单
    """
    data_list.close_edit()
    start = action.data()
    tools_bar.start_menu.setTitle(start)
    cache_control.start_status = start
    tools_bar.start_menu.clear()
    action_list = []
    start_group = QActionGroup(tools_bar.start_menu)
    start_list = {"开始", "结束"}
    for v in start_list:
        if v == cache_control.start_status:
            continue
        now_action: QWidgetAction = QWidgetAction(tools_bar)
        now_action.setText(v)
        now_action.setActionGroup(start_group)
        now_action.setData(v)
        action_list.append(now_action)
    start_group.triggered.connect(change_start_menu)
    tools_bar.start_menu.addActions(action_list)
    data_list.update()
    item_premise_list.item_list.clear()
    item_settle_list.item_list.clear()


def update_premise_and_settle_list(model_index: QModelIndex):
    """
    更新前提和结算器列表
    Keyword arguments:
    model_index -- 事件序号
    """
    data_list.close_edit()
    item = data_list.item(model_index.row())
    if item is not None:
        cache_control.now_event_id = item.uid
        item_premise_list.update()
        item_settle_list.update()


def update_premise_and_settle_list_for_move(model_index: int):
    """
    移动选项时更新前提和结算器列表
    Keyword arguments:
    model_index -- 事件序号
    """
    data_list.close_edit()
    item = data_list.item(model_index)
    if item is not None:
        cache_control.now_event_id = item.uid
        item_premise_list.update()
        item_settle_list.update()


data_list.clicked.connect(update_premise_and_settle_list)
data_list.currentRowChanged.connect(update_premise_and_settle_list_for_move)
action_list = []
status_group = QActionGroup(tools_bar.status_menu)
for cid in cache_control.status_data:
    if cid is cache_control.now_status:
        continue
    if cid == "0":
        continue
    now_action: QWidgetAction = QWidgetAction(tools_bar)
    now_action.setText(cache_control.status_data[cid])
    now_action.setActionGroup(status_group)
    now_action.setData(cid)
    action_list.append(now_action)
status_group.triggered.connect(change_status_menu)
tools_bar.status_menu.addActions(action_list)
start_list = {"开始", "结束"}
action_list = []
start_group = QActionGroup(tools_bar.start_menu)
for v in start_list:
    if v == cache_control.start_status:
        continue
    now_action: QWidgetAction = QWidgetAction(tools_bar)
    now_action.setText(v)
    now_action.setActionGroup(start_group)
    now_action.setData(v)
    action_list.append(now_action)
start_group.triggered.connect(change_start_menu)
tools_bar.start_menu.addActions(action_list)
menu_bar.select_event_file_action.triggered.connect(load_event_data)
menu_bar.new_event_file_action.triggered.connect(create_event_data)
menu_bar.save_event_action.triggered.connect(save_event_data)
menu_bar.exit_action.triggered.connect(exit_editor)
main_window.setMenuBar(menu_bar)
main_window.add_tool_widget(tools_bar)
main_window.add_main_widget(item_premise_list,1)
main_window.add_main_widget(data_list,3)
main_window.add_main_widget(item_settle_list,1)
main_window.completed_layout()
QShortcut(QKeySequence(main_window.tr("Ctrl+O")),main_window,load_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+N")),main_window,create_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+S")),main_window,save_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+Q")),main_window,exit_editor)
main_window.show()
app.exec()
