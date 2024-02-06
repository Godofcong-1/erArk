#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import json
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
                if effect not in cache_control.effect_data:
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
    save_data()
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
                sub_key = int(now_key.lstrip("C|"))
                now_chara_data.Cloth.setdefault(sub_key,[])
                now_chara_data.Cloth[sub_key].append(now_value)
            # print(f"debug now_key = {now_key}, sub_key = {sub_key}, now_value = {now_value}")
    cache_control.now_chara_data = now_chara_data
    cache_control.now_edit_type_flag = 2
    chara_list.update()

    main_window.add_grid_chara_data_layout(chara_list)
    main_window.completed_layout()


def save_data():
    """保存文件"""
    if len(cache_control.now_file_path):
        # 保存事件
        if cache_control.now_edit_type_flag == 1:
            with open(cache_control.now_file_path, "w", encoding="utf-8") as event_data_file:
                now_data = {}
                for k in cache_control.now_event_data:
                    now_data[k] = cache_control.now_event_data[k].__dict__
                json.dump(now_data, event_data_file, ensure_ascii=0)

        # 保存口上
        elif cache_control.now_edit_type_flag == 0:
            save_talk_data()


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
                # print(f"debug row = {row}")
                if not len(row[k]):
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
        save_talk_data()
        load_talk_data_to_cache()


def save_talk_data():
    """保存口上文件"""
    if len(cache_control.now_file_path):
        # 通用开头
        out_data = ""
        out_data += "cid,behavior_id,adv_id,premise,context\n"
        out_data += "口上id,触发口上的行为id,口上限定的剧情npcid,前提id,口上内容\n"
        out_data += "str,int,int,str,str\n"
        out_data += "0,0,0,0,1\n"
        out_data += "口上配置数据,,,,\n"

        # 遍历数据
        for k in cache_control.now_talk_data:
            now_talk: game_type.Talk = cache_control.now_talk_data[k]
            out_data += f"{now_talk.cid},{now_talk.status_id},{now_talk.adv_id},"
            # 如果前提为空，就写入空白前提
            if len(now_talk.premise) == 0:
                out_data += "high_1"
            # 如果前提不为空，就正常写入，并在最后去掉多余的&
            else:
                for premise in now_talk.premise:
                    out_data += f"{premise}&"
                out_data = out_data[:-1]
            out_data += f",{now_talk.text}\n"

        # 写入文件
        with open(cache_control.now_file_path, "w",encoding="utf-8") as f:
            f.write(out_data)
            f.close()


def exit_editor():
    """关闭编辑器"""
    os._exit(0)


def change_status_menu(action: QWidgetAction):
    """
    更新状态菜单
    Keyword arguments:
    action -- 触发的菜单
    """
    cid = action.data()
    data_list.status_menu.setTitle(cache_control.status_data[cid])
    cache_control.now_status = cid
    data_list.status_menu.clear()
    status_group = QActionGroup(data_list.status_menu)
    font = QFont()
    font.setPointSize(11)
    for status_type in cache_control.status_type_data:
        status_menu = QMenu(status_type, data_list.status_menu)
        for cid in cache_control.status_type_data[status_type]:
            if cid is cache_control.now_status:
                continue
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
    data_list.status_menu.addActions(action_list)
    if cache_control.now_select_id != '':
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].status_id = cache_control.now_status
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].status_id = cache_control.now_status


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


data_list.list_widget.clicked.connect(update_premise_and_settle_list)
status_group = QActionGroup(data_list.status_menu)
font = QFont()
font.setPointSize(11)
for status_type in cache_control.status_type_data:
    status_menu = QMenu(status_type, data_list.status_menu)
    for cid in cache_control.status_type_data[status_type]:
        if cid is cache_control.now_status:
            continue
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
        if v == cache_control.now_type:
            continue
        now_action: QWidgetAction = QWidgetAction(data_list)
        now_action.setText(v)
        now_action.setActionGroup(type_group)
        now_action.setData(v)
        action_list.append(now_action)
    type_group.triggered.connect(change_type_menu)
    data_list.type_menu.addActions(action_list)

menu_bar.select_event_file_action.triggered.connect(load_event_data)
menu_bar.new_event_file_action.triggered.connect(create_event_data)
menu_bar.save_event_action.triggered.connect(save_data)
menu_bar.select_talk_file_action.triggered.connect(load_talk_data)
menu_bar.new_talk_file_action.triggered.connect(create_talk_data)
menu_bar.save_talk_action.triggered.connect(save_talk_data)
menu_bar.select_chara_file_action.triggered.connect(load_chara_data)
menu_bar.new_chara_file_action.triggered.connect(create_chara_data)

# 将文本编辑器的保存键绑定到口上事件列表的更新与文件的更新
item_text_edit.save_button.clicked.connect(data_list.update)
item_text_edit.save_button.clicked.connect(save_data)

# main_window.setMenuBar(menu_bar)
main_window.add_tool_widget(menu_bar)
main_window.completed_layout()
# QShortcut(QKeySequence(main_window.tr("Ctrl+O")),main_window,load_event_data)
# QShortcut(QKeySequence(main_window.tr("Ctrl+N")),main_window,create_event_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+S")),main_window,save_data)
QShortcut(QKeySequence(main_window.tr("Ctrl+Q")),main_window,exit_editor)
main_window.show()
app.exec()
