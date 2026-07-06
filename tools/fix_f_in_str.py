"""
该脚本用来将所有_(f"xxx")的字符串进行处理，将其转换为_("{xxx}").format(xxx)的形式，或者对于没有{}的直接去掉f
"""

import os


SKIP_DIRS = {'.git', '.conda', '.venv', 'venv', '__pycache__', 'node_modules', 'build', 'dist', 'data', 'save', 'image', '.github'}
READ_ENCODINGS = ('utf-8', 'utf-8-sig', 'gbk', 'latin-1')


def read_lines_with_fallback(file_path: str):
    """
    输入：file_path(str)
    输出：tuple[list[str], str]，分别为文件行与读取所用编码
    功能：按候选编码顺序读取文件，避免单一utf-8导致脚本中断
    """
    last_error = None
    for encoding in READ_ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.readlines(), encoding
        except UnicodeDecodeError as error:
            last_error = error
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"未知读取错误: {file_path}")


# 在当前目录及其子目录中查找所有的.py文件
for dirpath, dirnames, filenames in os.walk('.'):
    # 原地裁剪子目录，避免进入虚拟环境和构建目录
    dirnames[:] = [dirname for dirname in dirnames if dirname not in SKIP_DIRS]

    # 打印当前目录名
    print(f"正在处理目录: {dirpath}")

    for filename in filenames:
        if filename.endswith('.py') and not filename.startswith('test_') and not filename.startswith('fix_'):
            file_path = os.path.join(dirpath, filename)

            try:
                # 逐行遍历该文件
                lines, file_encoding = read_lines_with_fallback(file_path)
            except UnicodeDecodeError as error:
                print(f"[跳过] 无法解码文件: {file_path} | {error}")
                continue

            # 替换文件中的行（保持原编码写回）
            with open(file_path, 'w', encoding=file_encoding) as file:
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

