import os
import polib

base_dir = r"c:\code\era\erArk"
old_po_path = os.path.join(base_dir, "data", "po", "ko_KR", "LC_MESSAGES", "erArk_py.po")
new_po_path = os.path.join(base_dir, "data", "po", "zh_CN", "LC_MESSAGES", "erArk_py.po")

# 读取PO文件
po = polib.pofile(old_po_path)

# 创建一个字典来存储msgid和msgstr的对应关系
old_msgid_msgstr_dict = {}
new_msgid_msgstr_dict = {}

# 遍历PO文件中的每一个条目
for entry in po:
    # 将msgid和msgstr的对应关系存储到字典中
    old_msgid_msgstr_dict[entry.msgid] = entry.msgstr

# 读取新的PO文件
new_po = polib.pofile(new_po_path)

# 遍历新的PO文件中的每一个条目
for entry in new_po:
    # 如果msgid在字典中存在
    if entry.msgid in old_msgid_msgstr_dict:
        # 则跳过
        continue
    # 否则，将该条目加到字典中
    new_msgid_msgstr_dict[entry.msgid] = entry.msgstr
    # print(f"debug add msgid: {entry.msgid}, msgstr: {entry.msgstr}")

# 将新的PO文件中的条目写入到旧的PO文件中
for msgid, msgstr in new_msgid_msgstr_dict.items():
    # print(f"debug new msgid: {msgid}, msgstr: {msgstr}")
    # 创建一个新的PO文件条目
    new_entry = polib.POEntry(
        msgid=msgid,
        msgstr=msgstr
    )
    # 将新的PO文件条目添加到PO文件中
    po.append(new_entry)

# 将PO文件保存到新的文件中
po.save(old_po_path)