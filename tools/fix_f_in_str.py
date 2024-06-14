"""
该脚本用来将所有_(f"xxx")的字符串进行处理，将其转换为_("{xxx}").format(xxx)的形式，或者对于没有{}的直接去掉f
"""

import os
# 在当前目录及其子目录中查找所有的.py文件
for dirpath, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if filename.endswith('.py') and not filename.startswith('test_') and not filename.startswith('fix_'):
            # 逐行遍历该文件
            with open(os.path.join (dirpath, filename), 'r', encoding='utf-8') as file:
                lines = file.readlines()
            # 替换文件中的行
            with open(os.path.join (dirpath, filename), 'w', encoding='utf-8') as file:
                for line in lines:
                    # 如果发现有_(f"xxx")这样的字符串，则提取出该字符串
                    if '_(f"' in line and '")' in line:
                        translation = line.split('_(f"')[1].split('")')[0]
                        if '{' in translation:
                            new_line = line
                            translation_copy = translation
                            # 遍历提取出{}中的内容，将句子的格式改为format的形式
                            # 先算出{}的个数
                            count = translation_copy.count('{')
                            # 用于存放{}中的内容
                            values = []
                            # 用于存放{}的位置
                            positions = []
                            # 用于存放{}的内容
                            for i in range(count):
                                # 提取出{}中的内容
                                value = translation_copy.split('{')[1].split('}')[0]
                                values.append(value)
                                # 提取出{}的位置
                                position = translation_copy.find('{')
                                positions.append(position)
                                translation_copy = translation_copy.replace('{' + value + '}', '', 1)
                            # 根据translation和translation_copy，将句子的格式改为format的形式
                            new_translation = translation
                            for i in range(count):
                                new_translation = new_translation.replace('{' + values[i] + '}', '{' + str(i) + '}')
                            new_line = line.replace('_(f"' + translation + '")', '_("' + new_translation + '").format(' + ', '.join(values) + ')')
                        # 如果里面没有{}，则直接替换，去掉f
                        else:
                            new_line = line.replace('_(f"', '_("')
                        file.write(new_line)
                    else:
                        file.write(line)

