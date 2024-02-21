import csv
import os
import json
import datetime
import ast

config_dir = os.path.join("data", "csv")
# os.system("cp ./tools/DieloliEventEditor/default.json ./data/event/")
event_dir = os.path.join("data", "event")
talk_dir = os.path.join("data", "talk")
target_dir = os.path.join("data", "target")
config_data = {}
config_def_str = ""
config_po = "\n"
msgData = set()
class_data = set()
character_dir = os.path.join("data","character")
character_data = {}
ui_text_dir = os.path.join("data", "ui_text")
ui_text_data = {}


def build_csv_config(file_path: str, file_name: str, talk: bool, target: bool):
    with open(file_path, encoding="utf-8") as now_file:
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
        config_data.setdefault(type_text, {})
        config_data[type_text].setdefault("data", [])
        config_data[type_text].setdefault("gettext", {})
        for row in now_read:
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
                if k == "cid" and talk:
                    row[k] = file_id.split("-")[0] + row[k]
                if k == "talk_id" and talk:
                    row[k] = file_id.split("-")[0] + row[k]
                if k == "cid" and target:
                    row[k] = row[k]
                elif k == "target_id" and target:
                    row[k] = row[k]
                if get_text_data[k]:
                    build_config_po(row[k], type_text, k, row["cid"])
            config_data[type_text]["data"].append(row)
        config_data[type_text]["gettext"] = get_text_data
        build_config_def(type_text, now_type_data, now_docstring_data, class_text)


def build_config_def(class_name: str, value_type: dict, docstring: dict, class_text: str):
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


def build_config_po(message: str, message_class: str, message_type: str, message_id: str):
    global config_po
    if message not in msgData:
        config_po += f"#: class:{message_class} id:{message_id} type:{message_type}\n"
        config_po += f'msgid "{message}"\n'
        config_po += f'msgstr ""\n\n'
        msgData.add(message)


def build_scene_config(data_path):
    global config_po
    for i in os.listdir(data_path):
        now_path = os.path.join(data_path, i)
        if os.path.isfile(now_path):
            if i == "Scene.json":
                with open(now_path, "r", encoding="utf-8") as now_file:
                    scene_data = json.loads(now_file.read())
                    scene_name = scene_data["SceneName"]
                    if scene_name not in msgData:
                        config_po += f"#: Scene:{now_path}\n"
                        config_po += f'msgid "{scene_name}"\n'
                        config_po += 'msgstr ""\n\n'
                        msgData.add(scene_name)
            elif i == "Map.json":
                with open(now_path, "r", encoding="utf-8") as now_file:
                    map_data = json.loads(now_file.read())
                    map_name = map_data["MapName"]
                    if map_name not in msgData:
                        config_po += f"#: Map:{now_path}\n"
                        config_po += f'msgid "{map_name}"\n'
                        config_po += 'msgstr ""\n\n'
                        msgData.add(map_name)
        else:
            build_scene_config(now_path)


def build_character_config(file_path:str,file_name:str):
    global config_po
    with open(file_path,encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        file_id = file_name.split(".")[0]
        now_data = {}
        # now_type_data = {}
        i = 0
        for row in now_read:
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
            if row["get_text"]:
                if row["value"] not in msgData:
                    config_po += f"#: Character:{file_id}\n"
                    config_po += "msgid" + " " + '"' + row["value"] + '"' + "\n"
                    config_po += 'msgstr ""\n\n'
        character_data[file_id] = now_data

def build_ui_text(file_path:str,file_name:str):
    global config_po
    with open(file_path,encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        file_id = file_name.split(".")[0]
        now_data = {}
        i = 0
        for row in now_read:
            i += 1
            if i <= 4:
                continue
            # print(f"debug row = {row}")
            now_data[row["cid"]] = row["context"]
            if row["context"] not in msgData:
                config_po += f"#: ui_text:{file_id}\n"
                config_po += "msgid" + " " + '"' + row["context"] + '"' + "\n"
                config_po += 'msgstr ""\n\n'
        ui_text_data[file_id] = now_data

# print("进入buildconfig.py了")
file_list = os.listdir(config_dir)
index = 0
for i in file_list:
    if i.split(".")[1] != "csv":
        continue
    if index:
        config_def_str += "\n\n\n"
    now_file = os.path.join(config_dir, i)
    build_csv_config(now_file, i, 0, 0)
    index += 1

talk_file_list = os.listdir(talk_dir)
for i in talk_file_list:
    now_dir = os.path.join(talk_dir, i)
    for f in os.listdir(now_dir):
        config_def_str += "\n"
        # config_def_str += "\n\n\n"
        now_f = os.path.join(now_dir, f)
        build_csv_config(now_f, f, 1, 0)

target_file_list = os.listdir(target_dir)
for i in target_file_list:
    now_dir = os.path.join(target_dir, i)
    for f in os.listdir(now_dir):
        config_def_str += "\n\n\n"
        now_f = os.path.join(now_dir, f)
        build_csv_config(now_f, f, 0, 1)

character_file_list = os.listdir(character_dir)
for i in character_file_list:
    now_path = os.path.join(character_dir,i)
    build_character_config(now_path,i)

ui_text_file_list = os.listdir(ui_text_dir)
for i in ui_text_file_list:
    now_path = os.path.join(ui_text_dir,i)
    build_ui_text(now_path,i)

event_file_list = os.listdir(event_dir)
event_list = []
for i in event_file_list:
    if i.split(".")[1] != "json":
        continue
    now_event_path = os.path.join(event_dir, i)
    with open(now_event_path, "r", encoding="utf-8") as event_file:
        now_event_data = json.loads(event_file.read())
        for event_id in now_event_data:
            now_event = now_event_data[event_id]
            event_list.append(now_event)
            now_event_text = now_event["text"]
            if now_event_text not in msgData:
                config_po += f"#: Event:{event_id}\n"
                config_po += f'msgid "{now_event_text}"\n'
                config_po += 'msgstr ""\n\n'
                msgData.add(now_event_text)
config_data["Event"] = {}
config_data["Event"]["data"] = event_list
config_data["Event"]["gettext"] = {}
config_data["Event"]["gettext"]["text"] = 1

map_path = os.path.join("data", "map")
build_scene_config(map_path)

# print("处理到Character.json了")
data_path = os.path.join("data","Character.json")
with open(data_path,"w",encoding="utf-8") as character_data_file:
    json.dump(character_data,character_data_file,ensure_ascii=0)

config_path = os.path.join("Script", "Config", "config_def.py")
config_def_str += "\n"
with open(config_path, "w", encoding="utf-8") as config_file:
    config_file.write(config_def_str)

config_data_path = os.path.join("data", "data.json")
with open(config_data_path, "w", encoding="utf-8") as config_data_file:
    json.dump(config_data, config_data_file, ensure_ascii=0)

ui_text_data_path = os.path.join("data", "ui_text.json")
with open(ui_text_data_path, "w", encoding="utf-8") as ui_text_data_file:
    json.dump(ui_text_data, ui_text_data_file, ensure_ascii=0)

# package_path = os.path.join("package.json")
# with open(package_path, "w", encoding="utf-8") as package_file:
#     now_time = datetime.datetime.now()
#     version = f"{now_time.year}.{now_time.month}.{now_time.day}"
#     version_data = {"version": version}
#     json.dump(version_data, package_file, ensure_ascii=0)

print("Config Building End")
