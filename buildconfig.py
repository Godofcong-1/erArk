import csv
import os
import json
import ast
import time

# 文件路径
config_dir = os.path.join("data", "csv")
event_dir = os.path.join("data", "event")
talk_dir = os.path.join("data", "talk")
talk_common_dir = os.path.join("data", "talk_common")
target_dir = os.path.join("data", "target")
character_dir = os.path.join("data","character")
ui_text_dir = os.path.join("data", "ui_text")
po_csv_path = os.path.join("data","po","zh_CN","LC_MESSAGES", "erArk_csv.po")
po_talk_path = os.path.join("data","po","zh_CN","LC_MESSAGES", "erArk_talk.po")
po_common_talk_path = os.path.join("data","po","zh_CN","LC_MESSAGES", "erArk_common_talk.po")
po_event_path = os.path.join("data","po","zh_CN","LC_MESSAGES", "erArk_event.po")
data_path = os.path.join("data","Character.json")
config_data_path = os.path.join("data", "data.json")
ui_text_data_path = os.path.join("data", "ui_text.json")
character_talk_data_path = os.path.join("data", "Character_Talk.json")
character_event_data_path = os.path.join("data", "Character_Event.json")
talk_common_data_path = os.path.join("data", "Talk_Common.json")
config_path = os.path.join("Script", "Config", "config_def.py")

# 全局变量
config_data = {}
character_data = {}
ui_text_data = {}
character_talk_data = {}
character_event_data = {}
talk_common_data = {}
built = set()
msgData = set()
class_data = set()
config_def_str = ""
# 使用列表累积 PO 行，减少大量字符串拼接导致的性能损耗
config_po_lines = []
talk_po_lines = []
common_talk_po_lines = []
event_po_lines = []

# 控制台调试输出开关（大量文件时打印会显著拖慢速度）
DEBUG_LOG = False

# 是否覆盖原有数据
BUILD_CONFIG = True
BUILD_EVENT = True
BUILD_TALK = True
BUILD_TALK_COMMON = True
BUILD_CHARACTER = True
BUILD_UI_TEXT = True
BUILD_TARGET = True
BUILD_PO = True
BUILD_CHARA_ID = 0

# 在开始时读取 JSON，若读取失败则用空对象
try:
    if BUILD_CHARA_ID == 0:
        character_talk_data = {}
        character_event_data = {}
    else:
        with open(character_talk_data_path, "r", encoding="utf-8") as f:
            character_talk_data = json.load(f)
        with open(character_event_data_path, "r", encoding="utf-8") as f:
            character_event_data = json.load(f)
        # 如果指定了特定角色，则将该角色重置
        for key in character_talk_data["Talk"]["data"].copy():
            if key["adv_id"] == BUILD_CHARA_ID:
                character_talk_data["Talk"]["data"].remove(key)
        for key in character_event_data["Event"]["data"].copy():
            if key["adv_id"] == BUILD_CHARA_ID:
                character_event_data["Event"]["data"].remove(key)
except:
    character_talk_data = {}

def build_csv_config(file_path: str, file_name: str, talk: bool, target: bool, talk_common: bool = False):
    """
    输入：
        file_path (str): 文件路径
        file_name (str): 文件名
        talk (bool): 是否为talk
        target (bool): 是否为target
        talk_common (bool): 是否为talk_common
    返回：None
    功能：读取csv并更新全局配置数据
    """
    if DEBUG_LOG:
        print(f"debug file_path = {file_path}")
    # newline="" 可提升 csv 解析性能并避免额外换行处理
    with open(file_path, encoding="utf-8", newline="") as now_file:
        now_read = csv.DictReader(now_file)
        now_docstring_data = {}
        now_type_data = {}
        get_text_data = {}
        file_id = file_name.split(".")[0]
        if talk or target:
            path_list = file_path.split(os.sep)
            if talk:
                file_id = path_list[-2] + "_" + file_id
        i = 0
        class_text = ""
        type_text = file_id
        if talk:
            type_text = "Talk"
            if "premise" in file_name:
                type_text = "TalkPremise"
        if target:
            if "target" in file_name:
                type_text = "Target"
            elif "premise" in file_name:
                type_text = "TargetPremise"
            elif "effect" in file_name:
                type_text = "TargetEffect"
        if talk_common:
            type_text = "Talk_Common"
        if talk:
            character_talk_data.setdefault(type_text, {})
            character_talk_data[type_text].setdefault("data", [])
            character_talk_data[type_text].setdefault("gettext", {})
        elif talk_common:
            talk_common_data.setdefault(type_text, {})
            talk_common_data[type_text].setdefault("data", [])
            talk_common_data[type_text].setdefault("gettext", {})
        else:
            config_data.setdefault(type_text, {})
            config_data[type_text].setdefault("data", [])
            config_data[type_text].setdefault("gettext", {})
        for row in now_read:
            # 获得当前的行数
            now_index = now_read.line_num
            if not i:
                for k in row:
                    now_docstring_data[k] = row[k]
                i += 1
                continue
            elif i == 1:
                for k in row:
                    now_type_data[k] = row[k]
                i += 1
                continue
            elif i == 2:
                for k in row:
                    get_text_data[k] = int(row[k])
                i += 1
                continue
            elif i == 3:
                class_text = list(row.values())[0]
                i += 1
                continue
            # 跳过非指定角色的行
            if talk and BUILD_CHARA_ID != 0:
                if int(row["adv_id"]) != BUILD_CHARA_ID:
                    continue
            for k in now_type_data:
                now_type = now_type_data[k]
                # print(f"debug row = {row}")
                if not len(row[k]):
                    del row[k]
                    continue
                try:
                    if now_type == "int":
                        row[k] = int(row[k])
                    elif now_type == "str":
                        row[k] = str(row[k]).replace('"','\\"') # 转义引号防止造成po文件混乱
                    elif now_type == "bool":
                        row[k] = int(row[k])
                    elif now_type == "float":
                        row[k] = float(row[k])
                except Exception as e:
                    print(f"Error processing row: {row}, key: {k}, type: {now_type}, error: {e}")
                # 使用文件名+cid名作为数据内的cid，以防不同文件的cid冲突
                if k == "cid" and talk:
                    # if "-" in file_id:
                    #     print(f"debug file_id = {file_id}")
                    row[k] = file_id + row[k]
                if k == "cid" and talk_common:
                    row[k] = file_id + row[k]
                if k == "talk_id" and talk:
                    row[k] = file_id.split("-")[0] + row[k]
                if k == "cid" and target:
                    row[k] = path_list[-2] + row[k]
                elif k == "target_id" and target:
                    row[k] = path_list[-2] + row[k]
                if get_text_data[k]:
                    build_config_po(row[k], file_path, now_index, talk = talk, common_talk = talk_common)
            if talk:
                row["version"] = 1
                # 如果口上的文件名中存在下划线标记的版本号，则将最后一个下划线之后的数字记录为版本号
                if int(row["adv_id"]) != 0 and file_id.count("_") == 3:
                    # print(f"debug file_id = {file_id}")
                    row["version"] = int(file_id.rsplit("_", 1)[-1])
                character_talk_data[type_text]["data"].append(row)
            elif talk_common:
                talk_common_data[type_text]["data"].append(row)
            else:
                config_data[type_text]["data"].append(row)
        if talk:
            get_text_data["version"] = 0
            character_talk_data[type_text]["gettext"] = get_text_data
        elif talk_common:
            talk_common_data[type_text]["gettext"] = get_text_data
        else:
            config_data[type_text]["gettext"] = get_text_data
        build_config_def(type_text, now_type_data, now_docstring_data, class_text)


def build_config_def(class_name: str, value_type: dict, docstring: dict, class_text: str):
    """
    输入：
        class_name (str): 类名
        value_type (dict): 类型定义字典
        docstring (dict): 参数说明字典
        class_text (str): 类文档字符串
    返回：None
    功能：构建配置定义字符串
    """
    global config_def_str
    if class_name not in class_data:
        # 给talk补上一个头部空行
        if class_name == "Talk":
            config_def_str += "\n\n"
        config_def_str += "class " + class_name + ":"
        config_def_str += '\n    """ ' + class_text + ' """\n'
        for k in value_type:
            config_def_str += "\n    " + k + ": " + value_type[k] + "\n"
            config_def_str += "    " + '""" ' + docstring[k] + ' """'
        class_data.add(class_name)
    # 去掉因为talk的csv文件而多出的尾部空行
    else:
        count_flag = 0
        for i in range(3):
            if config_def_str[-i] == "\n":
                count_flag += 1
        if count_flag >= 2:
            config_def_str = config_def_str[:-2]


def build_config_po(message: str, file_path: str, now_index: int, talk: bool = False, common_talk: bool = False, event: bool = False):
    """
    输入：
        message (str): 文本内容
        file_path (str): 文件路径
        now_index (int): 当前行数
        talk (bool): 是否为talk
        common_talk (bool): 是否为common talk
        event (bool): 是否为event
    返回：None
    功能：构建配置po文本
    """
    global built, config_po_lines, talk_po_lines, common_talk_po_lines, event_po_lines
    if message not in built:
        lines = (
            talk_po_lines if talk else
            common_talk_po_lines if common_talk else
            event_po_lines if event else
            config_po_lines
        )
        lines.append(f"#: .\{file_path}:{now_index}\n")
        lines.append(f'msgid "{message}"\n')
        lines.append('msgstr ""\n\n')
        built.add(message)


def build_scene_config(data_path):
    """
    输入：
        data_path: 场景数据路径
    返回：None
    功能：构建场景配置并提取文本
    """
    global config_po_lines
    for i in os.listdir(data_path):
        now_path = os.path.join(data_path, i)
        if os.path.isfile(now_path):
            if i == "Scene.json":
                with open(now_path, "r", encoding="utf-8") as now_file:
                    scene_data = json.loads(now_file.read())
                    scene_name = scene_data["SceneName"]
                    if not scene_name in built:
                        config_po_lines.append(f"#: /'{now_path}:2\n")
                        config_po_lines.append(f'msgid "{scene_name}"\n')
                        config_po_lines.append('msgstr ""\n\n')
                        built.add(scene_name)
            elif i == "Map.json":
                with open(now_path, "r", encoding="utf-8") as now_file:
                    map_data = json.loads(now_file.read())
                    map_name = map_data["MapName"]
                    if not map_name in built:
                        config_po_lines.append(f"#: /'{now_path}:2\n")
                        config_po_lines.append(f'msgid "{map_name}"\n')
                        config_po_lines.append('msgstr ""\n\n')
                        built.add(map_name)
        else:
            build_scene_config(now_path)


def build_character_config(file_path:str,file_name:str):
    """
    输入：
        file_path (str): 文件路径
        file_name (str): 文件名
    返回：None
    功能：读取角色CSV并更新全局角色数据
    """
    global config_po_lines,built
    with open(file_path,encoding="utf-8", newline="") as now_file:
        now_read = csv.DictReader(now_file)
        file_id = file_name.split(".")[0]
        now_data = {}
        # now_type_data = {}
        i = 0
        for row in now_read:
            # 获得当前的行数
            now_index = now_read.line_num
            if not i:
                i += 1
                continue
            i += 1
            if row["type"] == 'int':
                now_data[row["key"]] = int(row["value"])
            elif row["type"] == 'str':
                now_data[row["key"]] = str(row["value"])
            elif row["type"] == 'dict':
                now_data[row["key"]] = ast.literal_eval(row["value"])
            else:
                now_data[row["key"]] = row["value"]
            if row["get_text"] and row["type"] == 'str' and row["value"] not in built:
                config_po_lines.append(f"#: .\{file_path}:{now_index}\n")
                config_po_lines.append("msgid" + " " + '"' + row["value"] + '"' + "\n")
                config_po_lines.append('msgstr ""\n\n')
                built.add(row["value"])
        character_data[file_id] = now_data

def build_ui_text(file_path:str,file_name:str):
    """
    输入：
        file_path (str): 文件路径
        file_name (str): 文件名
    返回：None
    功能：读取UI文本CSV并更新全局UI数据
    """
    global config_po_lines,built
    with open(file_path,encoding="utf-8", newline="") as now_file:
        now_read = csv.DictReader(now_file)
        file_id = file_name.split(".")[0]
        now_data = {}
        i = 0
        for row in now_read:
            # 获得当前的行数
            now_index = now_read.line_num
            i += 1
            if i <= 4:
                continue
            # print(f"debug row = {row}")
            now_data[row["cid"]] = row["context"]
            if row["context"] not in msgData and row["context"] not in built:
                config_po_lines.append(f"#: .\{file_path}:{now_index}\n")
                config_po_lines.append("msgid" + " " + '"' + row["context"] + '"' + "\n")
                config_po_lines.append('msgstr ""\n\n')
                built.add(row["context"])
        ui_text_data[file_id] = now_data

def build_po_text():
    """
    输入：
        po: 原始po字符串
    返回：str
    功能：生成po文件的头部内容
    """
    from datetime import datetime, timezone, timedelta
    po = "\n"
    po += '# SOME DESCRIPTIVE TITLE.\n'
    po += '# Copyright (C) YEAR Free Software Foundation, Inc.\n'
    po += '# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n'
    po += '#\n'
    po += 'msgid ""\n'
    po += 'msgstr ""\n'
    po += '"Project-Id-Version: PACKAGE VERSION\\n"\n'
    po += '"Report-Msgid-Bugs-To: \\n"\n'
    creation_date = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M%z")
    po += f'"POT-Creation-Date: {creation_date}\\n"\n'
    po += '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
    po += '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n'
    po += '"Language-Team: LANGUAGE <LANGUAGE-TEAM-EMAIL@ADDRESS>\\n"\n'
    po += '"Language: zh_CN\\n"\n'
    po += '"MIME-Version: 1.0\\n"\n'
    po += '"Content-Type: text/plain; charset=UTF-8\\n"\n'
    po += '"Content-Transfer-Encoding: 8bit\\n"\n\n'
    return po

print("开始加载游戏数据\n")

if BUILD_PO:
    header_text = build_po_text()
    config_po_lines.append(header_text)
    talk_po_lines.append(header_text)
    common_talk_po_lines.append(header_text)
    event_po_lines.append(header_text)

file_list = os.listdir(config_dir)
index = 0
for i in file_list:
    if i.split(".")[1] != "csv":
        continue
    if index:
        config_def_str += "\n\n\n"
    now_file = os.path.join(config_dir, i)
    build_csv_config(now_file, i, False, False)
    index += 1

# 在写入 talk 数据时根据 BUILD_TALK 判断是否覆盖
if BUILD_TALK:
    # 获取talk目录下的文件列表
    talk_file_list = os.listdir(talk_dir)
    # 递归统计talk目录及其所有子目录下的csv文件总数
    def count_csv_files(dir_path):
        """
        输入：
            dir_path (str): 目录路径
        返回：int，总的csv文件数量
        功能：递归统计目录下所有csv文件数量
        """
        count = 0
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            if os.path.isdir(full_path):
                count += count_csv_files(full_path)
            elif entry.endswith('.csv'):
                count += 1
        return count

    # 递归统计talk目录及其所有子目录下的csv文件总数和总大小
    def count_csv_files_and_size(dir_path):
        """
        输入：
            dir_path (str): 目录路径
        返回：(int, int)，总的csv文件数量和总字节数
        功能：递归统计目录下所有csv文件数量和总大小
        """
        count = 0
        total_size = 0
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            if os.path.isdir(full_path):
                sub_count, sub_size = count_csv_files_and_size(full_path)
                count += sub_count
                total_size += sub_size
            elif entry.endswith('.csv'):
                count += 1
                total_size += os.path.getsize(full_path)
        return count, total_size

    # 统计talk目录及其所有子目录下的csv文件总数和总大小
    total_files, total_bytes = count_csv_files_and_size(talk_dir)
    # 已处理文件计数
    processed_files = 0
    # 已处理文件字节数
    processed_bytes = 0
    # 记录上次打印进度的时间
    last_print_time = time.time()
    print(f"[进度] 开始处理角色口上，总共有 {total_files} 个文件需要处理，总大小 {total_bytes/1024/1024:.2f} MB")
    for i in talk_file_list:
        # 跳过 ai 文件夹
        if i == "ai":
            continue
        now_path = os.path.join(talk_dir, i)
        # 如果是目录，则递归遍历其子目录
        if os.path.isdir(now_path):
            for root, dirs, files in os.walk(now_path):
                for f in files:
                    # 跳过非 csv 文件
                    if not f.endswith(".csv"):
                        continue
                    # 在配置定义字符串中添加空行
                    config_def_str += "\n"
                    # 构建子目录下的 talk csv 配置
                    csv_path = os.path.join(root, f)
                    build_csv_config(csv_path, f, True, False)
                    # 每处理完一个csv文件，计数加一
                    processed_files += 1
                    # 累加已处理文件的字节数
                    processed_bytes += os.path.getsize(csv_path)
                    # 获取当前时间
                    now_time = time.time()
                    # 如果距离上次打印超过1秒，则打印进度
                    if now_time - last_print_time >= 1 or processed_files == total_files:
                        percent = processed_files / total_files * 100
                        print(f"[进度] 已处理 {processed_files}/{total_files} 个文件 ({percent:.2f}%)，已处理 {processed_bytes/1024/1024:.2f}/{total_bytes/1024/1024:.2f} MB")
                        last_print_time = now_time
        else:
            # 如果是单个 csv 文件，则直接构建
            if i.endswith(".csv"):
                config_def_str += "\n"
                build_csv_config(now_path, i, True, False)
                # 每处理完一个csv文件，计数加一
                processed_files += 1
                # 累加已处理文件的字节数
                processed_bytes += os.path.getsize(now_path)
                # 获取当前时间
                now_time = time.time()
                # 如果距离上次打印超过1秒，则打印进度
                if now_time - last_print_time >= 1 or processed_files == total_files:
                    percent = processed_files / total_files * 100
                    print(f"[进度] 已处理 {processed_files}/{total_files} 个文件 ({percent:.2f}%)，已处理 {processed_bytes/1024/1024:.2f}/{total_bytes/1024/1024:.2f} MB")
                    last_print_time = now_time
    # 写入 talk 数据
    with open(character_talk_data_path, "w", encoding="utf-8") as talk_data_file:
        json.dump(character_talk_data, talk_data_file, ensure_ascii=False)
else:
    # 不覆盖 talk 数据，保持原有数据
    pass

if BUILD_TALK_COMMON:
    # 递归统计talk_common目录及其所有子目录下的csv文件总数和总大小
    def count_csv_files_and_size(dir_path):
        """
        输入：
            dir_path (str): 目录路径
        返回：(int, int)，总的csv文件数量和总字节数
        功能：递归统计目录下所有csv文件数量和总大小
        """
        count = 0
        total_size = 0
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            if os.path.isdir(full_path):
                sub_count, sub_size = count_csv_files_and_size(full_path)
                count += sub_count
                total_size += sub_size
            elif entry.endswith('.csv'):
                count += 1
                total_size += os.path.getsize(full_path)
        return count, total_size

    talk_common_file_list = os.listdir(talk_common_dir)
    # 统计talk_common目录及其所有子目录下的csv文件总数和总大小
    total_files, total_bytes = count_csv_files_and_size(talk_common_dir)
    processed_files = 0
    processed_bytes = 0
    last_print_time = time.time()
    print(f"[进度] 开始处理通用口上，总共有 {total_files} 个文件需要处理，总大小 {total_bytes/1024/1024:.2f} MB")
    for i in talk_common_file_list:
        now_path = os.path.join(talk_common_dir, i)
        # 如果是目录，则递归遍历其子目录
        if os.path.isdir(now_path):
            for root, dirs, files in os.walk(now_path):
                for f in files:
                    # 跳过非 csv 文件
                    if not f.endswith(".csv"):
                        continue
                    # 在配置定义字符串中添加空行
                    config_def_str += "\n"
                    # 构建子目录下的 talk csv 配置
                    csv_path = os.path.join(root, f)
                    build_csv_config(csv_path, f, False, False, talk_common=True)
                    processed_files += 1
                    processed_bytes += os.path.getsize(csv_path)
                    now_time = time.time()
                    if now_time - last_print_time >= 1 or processed_files == total_files:
                        percent = processed_files / total_files * 100 if total_files else 100
                        print(f"[进度] 已处理 {processed_files}/{total_files} 个文件 ({percent:.2f}%)，已处理 {processed_bytes/1024/1024:.2f}/{total_bytes/1024/1024:.2f} MB")
                        last_print_time = now_time
        else:
            # 如果是单个 csv 文件，则直接构建
            if i.endswith(".csv"):
                config_def_str += "\n"
                build_csv_config(now_path, i, False, False, talk_common=True)
    # 写入 talk_common 数据
            # 文件总数和大小的处理过程打印
                processed_files += 1
                processed_bytes += os.path.getsize(now_path)
                now_time = time.time()
                if now_time - last_print_time >= 1 or processed_files == total_files:
                    percent = processed_files / total_files * 100 if total_files else 100
                    print(f"[进度] 已处理 {processed_files}/{total_files} 个文件 ({percent:.2f}%)，已处理 {processed_bytes/1024/1024:.2f}/{total_bytes/1024/1024:.2f} MB")
                    last_print_time = now_time
    with open(talk_common_data_path, "w", encoding="utf-8") as talk_common_data_file:
        json.dump(talk_common_data, talk_common_data_file, ensure_ascii=False)

# 在写入 target 数据时根据 BUILD_TARGET 判断是否覆盖
if BUILD_TARGET:
    target_file_list = os.listdir(target_dir)
    for i in target_file_list:
        now_dir = os.path.join(target_dir, i)
        for f in os.listdir(now_dir):
            config_def_str += "\n\n\n"
            now_f = os.path.join(now_dir, f)
            build_csv_config(now_f, f, False, True)

if BUILD_CHARACTER:
    character_file_list = os.listdir(character_dir)
    for i in character_file_list:
        now_path = os.path.join(character_dir,i)
        build_character_config(now_path,i)

if BUILD_UI_TEXT:
    ui_text_file_list = os.listdir(ui_text_dir)
    for i in ui_text_file_list:
        now_path = os.path.join(ui_text_dir,i)
        build_ui_text(now_path,i)

# 在写入 event 数据时根据 BUILD_EVENT 判断是否覆盖
if BUILD_EVENT:
    event_list = []
    for root, dirs, files in os.walk(event_dir):
        for file in files:
            # 跳过非json文件
            if file.split(".")[-1] != "json":
                continue
            now_event_path = os.path.join(root, file)
            with open(now_event_path, "r", encoding="utf-8") as event_file:
                now_event_data = json.loads(event_file.read())
                for event_id in now_event_data:
                    now_event = now_event_data[event_id]
                    event_list.append(now_event)
                    now_event_text = now_event["text"]
                    if now_event_text not in msgData and not now_event_text in built:
                        event_po_lines.append(f"#: Event:{event_id}\n")
                        event_po_lines.append(f'msgid "{now_event_text}"\n')
                        event_po_lines.append('msgstr ""\n\n')
                        built.add(now_event_text)
                        msgData.add(now_event_text)
    character_event_data["Event"] = {}
    character_event_data["Event"]["data"] = event_list
    character_event_data["Event"]["gettext"] = {}
    character_event_data["Event"]["gettext"]["text"] = 1
    with open(character_event_data_path, "w", encoding="utf-8") as event_data_file:
        json.dump(character_event_data, event_data_file, ensure_ascii=False)
else:
    # 不覆盖 event 数据，保持原有数据
    pass

map_path = os.path.join("data", "map")
build_scene_config(map_path)

# 在写入时根据flag判断是否覆盖
if BUILD_CHARACTER:
    with open(data_path,"w",encoding="utf-8") as character_data_file:
        json.dump(character_data,character_data_file,ensure_ascii=False)

config_def_str += "\n"
if BUILD_CONFIG:
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write(config_def_str)
    with open(config_data_path, "w", encoding="utf-8") as config_data_file:
        json.dump(config_data, config_data_file, ensure_ascii=False)

if BUILD_UI_TEXT:
    with open(ui_text_data_path, "w", encoding="utf-8") as ui_text_data_file:
        json.dump(ui_text_data, ui_text_data_file, ensure_ascii=False)

if BUILD_CONFIG:  # 与po输出相关的配置
    with open(po_csv_path, "w", encoding="utf-8") as po_file:
        po_file.write(''.join(config_po_lines))

if BUILD_PO:
    if BUILD_TALK:
        with open(po_talk_path, "w", encoding="utf-8") as po_file:
            po_file.write(''.join(talk_po_lines))
        with open(po_event_path, "w", encoding="utf-8") as po_file:
            po_file.write(''.join(event_po_lines))
    if BUILD_TALK_COMMON:
        with open(po_common_talk_path, "w", encoding="utf-8") as po_file:
            po_file.write(''.join(common_talk_po_lines))

print("加载完毕")
