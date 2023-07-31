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
from ui.item_effect_list import ItemEffectList
from ui.item_text_edit import ItemTextEdit
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
item_effect_list: ItemEffectList = ItemEffectList()
cache_control.item_effect_list = item_effect_list
item_text_edit: ItemTextEdit = ItemTextEdit()
cache_control.item_text_edit = item_text_edit

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
            delete_effect_list = []
            for effect in now_event.effect:
                if effect not in cache_control.effect_data:
                    delete_effect_list.append(effect)
            for effect in delete_effect_list:
                del now_event.effect[effect]
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
    data_list.list_widget.update()
    item_premise_list.item_list.clear()
    # item_settle_list.item_list.clear()
    item_effect_list.item_list.clear()


def change_type_menu(action: QWidgetAction):
    """
    更新类型分类菜单
    Keyword arguments:
    action -- 触发的菜单
    """
    data_list.close_edit()
    type = action.data()
    tools_bar.type_menu.setTitle(type)
    # cache_control.start_status = start # 这一句姑且先保留
    cache_control.now_type = type
    tools_bar.type_menu.clear()
    action_list = []
    type_group = QActionGroup(tools_bar.type_menu)
    type_list = {"指令正常", "跳过指令", "事件后置"}
    for v in type_list:
        if v == cache_control.now_type:
            continue
        now_action: QWidgetAction = QWidgetAction(tools_bar)
        now_action.setText(v)
        now_action.setActionGroup(type_group)
        now_action.setData(v)
        action_list.append(now_action)
    type_group.triggered.connect(change_type_menu)
    tools_bar.type_menu.addActions(action_list)
    data_list.list_widget.update()
    item_premise_list.item_list.clear()
    # item_settle_list.item_list.clear()
    item_effect_list.item_list.clear()


def update_premise_and_settle_list(model_index: QModelIndex):
    """
    更新前提和结算器列表
    Keyword arguments:
    model_index -- 事件序号
    """
    data_list.close_edit()
    item = data_list.list_widget.item(model_index.row())
    if item is not None:
        cache_control.now_event_id = item.uid
        item_premise_list.update()
        item_effect_list.update()
        item_text_edit.update()


def update_all_item_for_move(model_index: int):
    """
    移动选项时更新各子部件
    Keyword arguments:
    model_index -- 事件序号
    """
    data_list.close_edit()
    item = data_list.list_widget.item(model_index)
    if item is not None:
        cache_control.now_event_id = item.uid
        item_premise_list.update()
        item_effect_list.update()
        item_text_edit.update()
        data_list.update()


data_list.list_widget.clicked.connect(update_premise_and_settle_list)
data_list.list_widget.currentRowChanged.connect(update_all_item_for_move)
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
type_list = {"指令正常", "跳过指令", "事件后置"}
action_list = []
type_group = QActionGroup(tools_bar.type_menu)
for v in type_list:
    if v == cache_control.now_type:
        continue
    now_action: QWidgetAction = QWidgetAction(tools_bar)
    now_action.setText(v)
    now_action.setActionGroup(type_group)
    now_action.setData(v)
    action_list.append(now_action)
type_group.triggered.connect(change_type_menu)
tools_bar.type_menu.addActions(action_list)
menu_bar.select_event_file_action.triggered.connect(load_event_data)
menu_bar.new_event_file_action.triggered.connect(create_event_data)
menu_bar.save_event_action.triggered.connect(save_event_data)
menu_bar.exit_action.triggered.connect(exit_editor)
main_window.setMenuBar(menu_bar)
main_window.add_tool_widget(tools_bar)
main_window.add_grid_layout(data_list,item_premise_list,item_effect_list,item_text_edit)
main_window.completed_layout()
QShortcut(QKeySequence(main_window.tr("Ctrl+O")),main_window,load_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+N")),main_window,create_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+S")),main_window,save_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+Q")),main_window,exit_editor)
main_window.show()
app.exec()
