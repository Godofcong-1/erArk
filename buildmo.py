import os
import polib

po_dir = os.path.join("data", "po", "en_US", "LC_MESSAGES")
po_path = os.path.join(po_dir, "erArk.po")
mo_path = os.path.join(po_dir, "erArk.mo")

def build_po_text(po):
    po = "\n"
    po += '# SOME DESCRIPTIVE TITLE.\n'
    po += '# Copyright (C) YEAR Free Software Foundation, Inc.\n'
    po += '# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n'
    po += '#\n'
    po += 'msgid ""\n'
    po += 'msgstr ""\n'
    po += '"Project-Id-Version: PACKAGE VERSION\\n"\n'
    po += '"Report-Msgid-Bugs-To: \\n"\n'
    po += '"POT-Creation-Date: 2024-03-11 08:00+0800\\n"\n'
    po += '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
    po += '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n'
    po += '"Language-Team: LANGUAGE <LANGUAGE-TEAM-EMAIL@ADDRESS>\\n"\n'
    po += '"Language: en_US\\n"\n'
    po += '"MIME-Version: 1.0\\n"\n'
    po += '"Content-Type: text/plain; charset=UTF-8\\n"\n'
    po += '"Content-Transfer-Encoding: 8bit\\n"\n\n'
    return po
"""
# 读取PO文件
po = polib.pofile(po_path)

# 创建一个字典来存储msgid和msgstr的对应关系
msgid_msgstr_dict = {}

# 遍历PO文件中的每一个条目
for entry in po:
    # 将msgid和msgstr的对应关系存储到字典中
    msgid_msgstr_dict[entry.msgid] = entry.msgstr

# 创建一个新的PO文件
new_po_path = po_path
with open(new_po_path, 'w', encoding='utf-8') as f:
    # 调用build_po_text，将返回的字符串写入到新的PO文件中
    f.write(build_po_text(po))

# 读取新的PO文件
new_po = polib.pofile(new_po_path)

# 遍历字典中的每一个条目
for msgid, msgstr in msgid_msgstr_dict.items():
    # 创建一个新的PO条目
    entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
    # 将新的PO条目添加到新的PO文件中
    new_po.append(entry)

# 将新的PO文件保存到磁盘
new_po.save(po_path)
"""
# 将PO文件编译成MO文件
os.system("msgfmt " + po_path + " -o " + mo_path)
