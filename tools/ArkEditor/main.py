#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import os
import csv

import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6.QtWidgets import QApplication, QFileDialog, QWidgetAction, QMenu
from PySide6.QtGui import QActionGroup, QKeySequence, QShortcut
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QFont
from ui.window import Window
from ui.menu_bar import MenuBar
from ui.data_list import DataList
from ui.tools_bar import ToolsBar
from ui.chara_list import CharaList
from ui.item_premise_list import ItemPremiseList
from ui.item_effect_list import ItemEffectList
from ui.item_text_edit import ItemTextEdit
import load_csv
import json_handle
import game_type
import cache_control
import function

load_csv.load_config()
app = QApplication(sys.argv)
main_window: Window = Window()
menu_bar: MenuBar = MenuBar()
tools_bar: ToolsBar = ToolsBar()
data_list: DataList = DataList()
chara_list: CharaList = CharaList()
item_premise_list: ItemPremiseList = ItemPremiseList()
cache_control.item_premise_list = item_premise_list
item_effect_list: ItemEffectList = ItemEffectList()
cache_control.item_effect_list = item_effect_list
item_text_edit: ItemTextEdit = ItemTextEdit()
cache_control.item_text_edit = item_text_edit

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

# envpath = '/home/diyun/anaconda3/envs/transformer_py38/lib/python3.8/site-packages/cv2/qt/plugins/platforms'
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath


# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = 'D:\venvforqt\Lib\site-packages\PyQt5\Qt5\plugins\platforms'


def load_event_data():
    """载入事件文件"""
    now_file = QFileDialog.getOpenFileName(menu_bar, "选择文件", ".", "*.json")
    cache_control.now_event_data = {}
    file_path = now_file[0]
    if file_path:
        cache_control.now_file_path = file_path
        now_data = json_handle.load_json(file_path)
        for k in now_data:
            now_event: game_type.Event = game_type.Event()
            now_event.__dict__ = now_data[k]
            delete_premise_list = []
            for premise in now_event.premise:
                if "CVP"in premise:
                    cvp_str = function.read_CVP(premise)
                    cache_control.premise_data[premise] = cvp_str
                elif premise not in cache_control.premise_data:
                    delete_premise_list.append(premise)
            for premise in delete_premise_list:
                del now_event.premise[premise]
            delete_effect_list = []
            for effect in now_event.effect:
                if "CVE" in effect:
                    cve_str = function.read_CVE(effect)
                    cache_control.effect_data[effect] = cve_str
                if "CSE" in effect:
                    cse_str = function.read_CSE(effect)
                    cache_control.effect_data[effect] = cse_str
                elif effect not in cache_control.effect_data:
                    delete_effect_list.append(effect)
            for effect in delete_effect_list:
                del now_event.effect[effect]
            cache_control.now_event_data[k] = now_event
        cache_control.now_edit_type_flag = 1
        data_list.update()
        main_window.add_grid_event_layout(data_list,item_premise_list,item_effect_list,item_text_edit)
        main_window.completed_layout()


def create_event_data():
    """新建事件文件"""
    cache_control.now_edit_type_flag = 1
    # 选择路径，创建一个json文件
    now_file = QFileDialog.getSaveFileName(menu_bar, "选择文件", ".", "*.json")
    file_path = now_file[0]
    if not file_path.endswith(".json"):
        file_path += ".json"
    cache_control.now_file_path = file_path
    # 自动打开文件
    function.save_data()
    load_event_data()


def create_chara_data():
    """新建属性文件"""
    cache_control.now_file_path = "999_模板人物属性文件.csv"
    load_chara_data_to_cache()

def load_chara_data(path = ""):
    """载入属性文件"""
    if path != "":
        csv_file = QFileDialog.getOpenFileName(menu_bar, "选择文件", ".", "*.csv")
        file_path = csv_file[0]
    else:
        file_path = path
    if file_path:
        cache_control.now_file_path = file_path
        load_chara_data_to_cache()

def load_chara_data_to_cache():
    """将属性数据传输到缓存中"""
    file_path = cache_control.now_file_path
    cache_control.now_talk_data = {}

    # 读取文件路径中的数据
    with open(file_path, encoding="utf-8") as now_file:
        now_chara_data: game_type.Chara_Data = game_type.Chara_Data()
        now_read = csv.DictReader(now_file)

        for row in now_read:
            # print(f"debug 最开始row = {row}")
            if row["key"] in ["key", "键"] or "说明行" in row["key"]:
                continue
            now_key = row["key"]
            sub_key = 0
            now_type = row["type"]
            # print(f"debug now_key = {now_key}, now_type = {now_type}")
            # 基础数值变换
            if now_type == 'int':
                now_value = int(row["value"])
            elif now_type == 'str':
                now_value = str(row["value"])
            elif now_type == 'bool':
                now_value = int(row["value"])
            # 基础属性赋予
            if now_key == "AdvNpc":
                now_chara_data.AdvNpc = now_value
            elif now_key == "Name":
                now_chara_data.Name = now_value
            elif now_key == "Sex":
                now_chara_data.Sex = now_value
            elif now_key == "Profession":
                now_chara_data.Profession = now_value
            elif now_key == "Race":
                now_chara_data.Race = now_value
            elif now_key == "Nation":
                now_chara_data.Nation = now_value
            elif now_key == "Birthplace":
                now_chara_data.Birthplace = now_value
            elif now_key == "Hp":
                now_chara_data.Hp = now_value
            elif now_key == "Mp":
                now_chara_data.Mp = now_value
            elif now_key == "Dormitory":
                now_chara_data.Dormitory = now_value
            elif now_key == "Token":
                now_chara_data.Token = now_value
            elif now_key == "Introduce_1":
                now_chara_data.Introduce_1 = now_value
            elif now_key == "TextColor":
                now_chara_data.TextColor = now_value
            # 复杂数值变换
            if now_key.startswith("A|"):
                sub_key = int(now_key.lstrip("A|"))
                now_chara_data.Ability[sub_key] = now_value
            elif now_key.startswith("E|"):
                sub_key = int(now_key.lstrip("E|"))
                now_chara_data.Experience[sub_key] = now_value
            elif now_key.startswith("T|"):
                sub_key = int(now_key.lstrip("T|"))
                now_chara_data.Talent[sub_key] = now_value
            elif now_key.startswith("C|"):
                if "-" not in now_key.lstrip("C|"):
                    sub_key = int(now_key.lstrip("C|"))
                else:
                    sub_key = int(now_key.lstrip("C|").split("-")[0])
                now_chara_data.Cloth.setdefault(sub_key,[])
                now_chara_data.Cloth[sub_key].append(now_value)
            # print(f"debug now_key = {now_key}, sub_key = {sub_key}, now_value = {now_value}")
    cache_control.now_chara_data = now_chara_data
    # print(f"debug Cloth = {cache_control.now_chara_data.Cloth}")
    cache_control.now_edit_type_flag = 2
    chara_list.update()

    main_window.add_grid_chara_data_layout(chara_list)
    main_window.completed_layout()


def load_talk_data():
    """载入口上文件"""
    csv_file = QFileDialog.getOpenFileName(menu_bar, "选择文件", ".", "*.csv")
    file_path = csv_file[0]
    if file_path:
        cache_control.now_file_path = file_path
        load_talk_data_to_cache()


def load_talk_data_to_cache():
    """将口上数据传输到缓存中"""

    file_path = cache_control.now_file_path
    cache_control.now_talk_data = {}

    # 读取文件路径中的数据
    with open(file_path, encoding="utf-8") as now_file:
        now_type_data = {}
        now_data = []
        i = 0
        now_read = csv.DictReader(now_file)

        for row in now_read:
            if not i:
                i += 1
                continue
            elif i == 1:
                for k in row:
                    now_type_data[k] = row[k]
                i += 1
                continue
            elif i in {2,3}:
                i += 1
                continue
            for k in now_type_data:
                now_type = now_type_data[k]
                # print(f"debug row = {row}, k = {k}, now_type = {now_type}")
                if row[k] is None or not len(row[k]):
                    del row[k]
                    continue
                if now_type == "int":
                    row[k] = int(row[k])
                elif now_type == "str":
                    row[k] = str(row[k])
                elif now_type == "bool":
                    row[k] = int(row[k])
                elif now_type == "float":
                    row[k] = float(row[k])
            now_data.append(row)
    # print(f"debug now_data = {now_data}")

    # 将读取的数据存入cache_control
    for idnex, value in enumerate(now_data):
        now_talk: game_type.Talk = game_type.Talk()
        now_talk.__dict__ = value

        # 类型名转化
        if 'context' in value:
            now_talk.text = now_talk.context
        else:
            now_talk.text = ""
        now_talk.status_id = str(now_talk.behavior_id)
        now_talk.adv_id = str(now_talk.adv_id)

        # 前提转化
        delete_premise_list = []
        premise_list = now_talk.premise.split('&')
        now_talk.premise = {}
        for premise in premise_list:
            now_talk.premise[premise] = 1
        for premise in now_talk.premise:
            if "CVP"in premise:
                cvp_str = function.read_CVP(premise)
                cache_control.premise_data[premise] = cvp_str
            elif premise not in cache_control.premise_data:
                delete_premise_list.append(premise)
        for premise in delete_premise_list:
            del now_talk.premise[premise]
        cache_control.now_talk_data[now_talk.cid] = now_talk
    cache_control.now_edit_type_flag = 0
    data_list.update()

    main_window.add_grid_talk_layout(data_list,item_premise_list,item_text_edit)
    main_window.completed_layout()

    update_status_menu()

def create_talk_data():
    """新建口上文件"""
    dialog: QFileDialog = QFileDialog(menu_bar)
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setNameFilter("CSV (*.csv)")
    if dialog.exec():
        file_names = dialog.selectedFiles()
        file_path: str = file_names[0]
        if not file_path.endswith(".csv"):
            file_path += ".csv"
        cache_control.now_file_path = file_path
        cache_control.now_edit_type_flag = 0
        function.save_talk_data()
        load_talk_data_to_cache()


def exit_editor():
    """关闭编辑器"""
    os._exit(0)


def update_status_menu():
    """更新状态菜单"""
    data_list.status_menu.clear()
    status_group = QActionGroup(data_list.status_menu)
    for status_type in cache_control.status_type_data:
        # 如果是事件编辑模式，则跳过二段结算
        if cache_control.now_edit_type_flag == 1 and "二段结算"in status_type:
            continue
        status_menu = QMenu(status_type, data_list.status_menu)
        for cid in cache_control.status_type_data[status_type]:
            if cid == "0":
                continue
            now_action: QWidgetAction = QWidgetAction(data_list)
            now_action.setText(cache_control.status_data[cid])
            now_action.setActionGroup(status_group)
            now_action.setData(cid)
            status_menu.addAction(now_action)
            status_menu.setFont(font)
        data_list.status_menu.addMenu(status_menu)
    status_group.triggered.connect(change_status_menu)


def change_status_menu(action: QWidgetAction):
    """
    更新状态菜单
    Keyword arguments:
    action -- 触发的菜单
    """
    cid = action.data()
    data_list.status_menu.setTitle(cache_control.status_data[cid])
    cache_control.now_status = cid
    update_status_menu()
    # 如果有选中的条目，则更新该条目的状态
    if cache_control.now_select_id != '':
        status_cid = cache_control.now_status
        # 更新状态id
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].status_id = status_cid
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].status_id = status_cid
        # 更新状态的触发人和持续时间
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
        data_list.label3_text.setText(info_text)

        # 根据文字长度设置菜单栏宽度
        status_menu_width = data_list.status_menu.fontMetrics().boundingRect(cache_control.status_data[cache_control.now_status]).width()
        status_menu_width = max(status_menu_width * 1.5, 100)
        if cache_control.now_edit_type_flag == 1:
            status_menu_width = max(status_menu_width * 1.5, 160)
        data_list.menu_bar.setFixedWidth(status_menu_width)


def change_type_menu(action: QWidgetAction):
    """
    更新类型分类菜单
    Keyword arguments:
    action -- 触发的菜单
    """
    type = action.data()
    data_list.type_menu.setTitle(type)
    # cache_control.start_status = start # 这一句姑且先保留
    cache_control.now_type = type
    data_list.type_menu.clear()
    action_list = []
    type_group = QActionGroup(data_list.type_menu)
    type_list = ["跳过指令", "指令前置", "指令后置"]
    for v in type_list:
        now_action: QWidgetAction = QWidgetAction(data_list)
        now_action.setText(v)
        now_action.setActionGroup(type_group)
        now_action.setData(v)
        action_list.append(now_action)
    type_group.triggered.connect(change_type_menu)
    data_list.type_menu.addActions(action_list)
    for i in range(len(type_list)):
        if type_list[i] == cache_control.now_type:
            cache_control.now_event_data[cache_control.now_select_id].type = i
            break


def update_premise_and_settle_list(model_index: QModelIndex):
    """
    更新前提和结算器列表
    Keyword arguments:
    model_index -- 事件序号
    """
    item = data_list.list_widget.item(model_index.row())
    if item is not None:
        cache_control.now_select_id = item.uid
        if cache_control.now_edit_type_flag == 0:
            cache_control.now_select_id = str(cache_control.now_select_id)
        item_premise_list.update()
        item_effect_list.update()
        item_text_edit.update()
        data_list.update()


def font_update():
    """更新字体"""
    function.show_setting()
    font.setPointSize(cache_control.now_font_size)
    font.setFamily(cache_control.now_font_name)
    main_window.setFont(font)
    menu_bar.setFont(font)
    tools_bar.setFont(font)
    data_list.setFont(font)
    data_list.list_widget.setFont(font)
    chara_list.setFont(font)
    item_premise_list.setFont(font)
    item_effect_list.setFont(font)
    item_text_edit.setFont(font)


data_list.list_widget.clicked.connect(update_premise_and_settle_list)
update_status_menu()

# for status_type, status_list in cache_control.status_type_data.items():
#     status_menu = QMenu(status_type, data_list.status_menu)
#     for cid in status_list:
#         now_action: QWidgetAction = QWidgetAction(data_list)
#         now_action.setText(cache_control.status_data[cid])
#         now_action.setData(cid)
#         status_menu.addAction(now_action)
#     data_list.status_menu.addMenu(status_menu)



# 仅在事件编辑模式下更新指令类型菜单
if cache_control.now_edit_type_flag == 1:
    type_list = {"跳过指令", "指令前置", "指令后置"}
    action_list = []
    type_group = QActionGroup(data_list.type_menu)
    for v in type_list:
        now_action: QWidgetAction = QWidgetAction(data_list)
        now_action.setText(v)
        now_action.setActionGroup(type_group)
        now_action.setData(v)
        action_list.append(now_action)
    type_group.triggered.connect(change_type_menu)
    data_list.type_menu.addActions(action_list)

menu_bar.select_event_file_action.triggered.connect(load_event_data)
menu_bar.new_event_file_action.triggered.connect(create_event_data)
menu_bar.save_event_action.triggered.connect(function.save_data)
menu_bar.select_talk_file_action.triggered.connect(load_talk_data)
menu_bar.new_talk_file_action.triggered.connect(create_talk_data)
menu_bar.save_talk_action.triggered.connect(function.save_data)
menu_bar.select_chara_file_action.triggered.connect(load_chara_data)
menu_bar.new_chara_file_action.triggered.connect(create_chara_data)
menu_bar.setting_action.triggered.connect(font_update)

# 将文本编辑器的保存键绑定到口上事件列表的更新与文件的更新
item_text_edit.save_button.clicked.connect(data_list.update)
item_text_edit.save_button.clicked.connect(function.save_data)

# main_window.setMenuBar(menu_bar)
main_window.add_tool_widget(menu_bar)
main_window.completed_layout()
# QShortcut(QKeySequence(main_window.tr("Ctrl+O")),main_window,load_event_data)
# QShortcut(QKeySequence(main_window.tr("Ctrl+N")),main_window,create_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+S")),main_window,function.save_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+Q")),main_window,exit_editor)
main_window.show()
app.exec()
