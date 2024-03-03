#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import shutil

po_dir_path = os.path.join("data","po")
po_dir_list = os.listdir(po_dir_path)
po_dir = os.path.join(po_dir_path,"zh_CN","LC_MESSAGES")
po_path = os.path.join(po_dir, "erArk.po")
if os.path.exists(po_path):
    os.remove(po_path)
# 在当前目录及其子目录中查找所有的.py文件，并将这些文件的路径写入到一个名为POTFILES的文件中
with open('POTFILES', 'w') as f:
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.py'):
                f.write(os.path.join(dirpath, filename) + '\n')

# 从这些.py文件中提取出所有的可翻译字符串，并将这些字符串写入到erArk.po文件中
os.system("xgettext --from-code=UTF-8 -L python -o erArk.pot -f POTFILES")

# 删除POTFILES文件
os.remove('POTFILES')

# 将erArk.pot文件复制到zh_CN目录下，并将其重命名为erArk.po
shutil.copy('erArk.pot', po_path)

# 删除erArk.pot文件
os.remove('erArk.pot')