#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本用于批量处理指定目录及子目录下所有CSV文件，将英文双引号替换为中文双引号。
"""

import os


def replace_english_quotes(text):
    """
    替换文本中的英文双引号为中文双引号
    参数:
        text (str): 待处理的文本
    返回:
        str: 已替换完成的文本
    """
    result = []
    toggle = True  # True用于输出开头引号“，False用于输出结尾引号”
    for char in text:
        if char == '"':
            if toggle:
                result.append('“')
            else:
                result.append('”')
            toggle = not toggle
        else:
            result.append(char)
    return ''.join(result)


def process_csv_file(filepath):
    """
    读取CSV文件内容并替换英文双引号，然后写回文件
    参数:
        filepath (str): CSV文件的完整路径
    返回:
        None
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = replace_english_quotes(content)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def batch_process_directory(directory):
    """
    批量处理指定目录及子目录下的所有CSV文件
    参数:
        directory (str): 要处理的根目录路径
    返回:
        None
    """
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(root, filename)
                process_csv_file(file_path)


if __name__ == '__main__':
    # 指定要处理的目录路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 文件路径
    root_dir = os.path.join(base_dir, 'data', 'talk')
    batch_process_directory(root_dir)
