#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新行为常量脚本

从Behavior_Data.csv文件读取数据，自动更新Script/Core/constant/Behavior.py文件中的常量定义。
此脚本会保留原文件的头部注释，并根据CSV文件中的行为数据更新Behavior类的常量定义。

使用方法:
    python update_behavior.py

注意事项:
    - CSV文件需要包含英文名称和描述列
    - 脚本会跳过CSV文件的前4行（表头、中文说明、类型定义、值映射）
    - 确保有足够的权限读写相关文件
"""

import csv
import os
import re


def read_behavior_data(csv_path):
    """
    读取行为数据CSV文件
    
    参数：
        csv_path (str): CSV文件路径
        
    返回：
        list: 包含行为数据的列表 [(id, en_name, description), ...]
    """
    behavior_data = []
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        # 跳过前4行（表头、中文说明、类型定义、值映射）
        for _ in range(4):
            next(csvfile)
            
        csv_reader = csv.reader(csvfile)
        
        for row in csv_reader:
            # 确保行有足够的列，且ID是数字
            if len(row) >= 6 and row[0] and row[0].strip().isdigit():
                behavior_id = row[0].strip()
                en_name = row[1].strip()
                description = row[2].strip()
                
                # 只添加有效的行为数据
                if en_name and description:
                    behavior_data.append((behavior_id, en_name, description))
    
    return behavior_data





def update_behavior_file(behavior_py_path, behavior_data):
    """
    更新Behavior.py文件
    
    参数：
        behavior_py_path (str): Behavior.py文件路径
        behavior_data (list): 行为数据列表
        
    返回：
        bool: 更新是否成功
    """
    try:
        # 读取原文件的头部信息
        file_header = ""
        if os.path.exists(behavior_py_path):
            with open(behavior_py_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 检查是否有文件头注释
                header_match = re.match(r'^(.*?)class\s+Behavior', content, re.DOTALL)
                if header_match:
                    file_header = header_match.group(1)
        
        # 生成新的类代码
        code = 'class Behavior:\n    """行为id字符串常量"""\n\n'
        
        for _, en_name, description in behavior_data:
            if en_name and en_name.strip():
                constant_name = en_name.upper()
                code += f'    {constant_name} = "{en_name}"\n'
                code += f'    """ {description} """\n'
        
        # 写入文件
        with open(behavior_py_path, 'w', encoding='utf-8') as file:
            if file_header:
                file.write(file_header)
            file.write(code)
        
        return True
    except Exception as e:
        print(f"更新文件失败: {e}")
        return False


def main():
    """
    主函数，执行行为常量更新流程
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 文件路径
    csv_path = os.path.join(base_dir, 'data', 'csv', 'Behavior_Data.csv')
    behavior_py_path = os.path.join(base_dir, 'Script', 'Core', 'constant', 'Behavior.py')
    
    print(f"读取 CSV 文件: {csv_path}")
    behavior_data = read_behavior_data(csv_path)
    print(f"读取到 {len(behavior_data)} 行行为数据")
    
    print(f"更新 Behavior.py 文件: {behavior_py_path}")
    if update_behavior_file(behavior_py_path, behavior_data):
        print("Behavior.py 更新成功！")
    else:
        print("Behavior.py 更新失败")


if __name__ == "__main__":
    main()