import os
import polib

po_dir = os.path.join("data", "po", "en_US", "LC_MESSAGES")
po_path = os.path.join(po_dir, "erArk.po")
mo_path = os.path.join(po_dir, "erArk.mo")

# 读取PO文件
po = polib.pofile(po_path)

# 创建一个字典来存储msgid和msgstr的对应关系
msgid_msgstr_dict = {}

# 遍历PO文件中的每一个条目
for entry in po:
    # 将msgid和msgstr的对应关系存储到字典中
    msgid_msgstr_dict[entry.msgid] = entry.msgstr

# 创建一个新的PO文件
new_po = polib.POFile()

# 遍历字典中的每一个条目
for msgid, msgstr in msgid_msgstr_dict.items():
    # 创建一个新的PO条目
    entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
    # 将新的PO条目添加到新的PO文件中
    new_po.append(entry)

# 将新的PO文件保存到磁盘
new_po.save(po_path)

os.system("msgfmt " + po_path + " -o " + mo_path)
