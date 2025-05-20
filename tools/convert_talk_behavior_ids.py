#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
遍历data\talk目录及其子目录的所有文件，将文件中的behavior_id列的int值替换为
Behavior_Data.csv中对应的en_name值。例如:将值1替换为'move'
"""

import os
import re
import json

def read_behavior_data(file_path):
    """
    读取Behavior_Data.csv文件，构建id到en_name的映射
    
    参数:
        file_path: str - Behavior_Data.csv的文件路径
    
    返回:
        dict - 包含id到en_name映射的字典
    """
    id_to_name = {}
    
    # 直接读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 跳过前5行（包括注释行、列名、中文名、类型、默认值）
    skip_count = 0
    data_section = False
    
    for line in lines:
        line = line.strip()
        
        # 跳过注释行
        if line.startswith('//'):
            continue
        
        # 检查是否已经进入数据部分
        if not data_section:
            skip_count += 1
            # 第5行后开始读取数据
            if skip_count >= 5:
                data_section = True
            continue
        
        # 跳过"状态描述配置"行
        if "状态描述配置" in line:
            continue
        
        # 处理数据行
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                behavior_id = int(parts[0])
                en_name = parts[1]
                if en_name and en_name != "0":  # 确保en_name不为空或0
                    id_to_name[behavior_id] = en_name
            except ValueError:
                # 跳过无法转换为整数的行
                pass
    
    return id_to_name

def process_file(file_path, id_to_name, dry_run=False):
    """
    处理单个文件，替换behavior_id为对应的en_name
    
    参数:
        file_path: str - 需要处理的文件路径
        id_to_name: dict - ID到en_name的映射字典
        dry_run: bool - 如果为True，只打印将要进行的更改，不实际修改文件
    
    返回:
        tuple - (替换次数, 未找到映射的ID列表)
    """
    # 文件扩展名检查
    _, ext = os.path.splitext(file_path)
    
    replaced_count = 0
    not_found_ids = set()
    
    # 特殊处理CSV文件
    if ext.lower() == '.csv':
        # CSV文件特殊处理，需要识别behavior_id列的位置并替换值
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 创建修改后的行列表
        new_lines = []
        header_indices = {}  # 存储列名对应的索引
        data_section = False
        header_processed = False
        
        for line_idx, line in enumerate(lines):
            # 保留注释行和空行
            if line.strip().startswith('//') or not line.strip():
                new_lines.append(line)
                continue
            
            # 跳过配置说明行
            if not header_processed and ',' in line:
                parts = line.split(',')
                if len(parts) >= 2 and 'behavior_id' in parts:
                    # 找到behavior_id所在列
                    for i, col in enumerate(parts):
                        if col.strip() == 'behavior_id':
                            header_indices['behavior_id'] = i
                    header_processed = True
                
                # 添加原行
                new_lines.append(line)
                continue
            
            # 处理数据行
            if header_processed and 'behavior_id' in header_indices and ',' in line:
                parts = line.split(',')
                behavior_id_idx = header_indices['behavior_id']
                
                # 确保行有足够的列
                if len(parts) > behavior_id_idx:
                    try:
                        # 尝试将behavior_id转换为整数
                        behavior_id = int(parts[behavior_id_idx])
                        if behavior_id in id_to_name:
                            # 替换为对应的en_name
                            parts[behavior_id_idx] = id_to_name[behavior_id]
                            replaced_count += 1
                        elif behavior_id != 0:  # 不计入ID为0的未找到情况
                            not_found_ids.add(behavior_id)
                        
                        # 重新组合为一行
                        new_lines.append(','.join(parts))
                        continue
                    except ValueError:
                        # 非整数，可能是表头或已替换过的值，保留原样
                        pass
            
            # 默认添加原行
            new_lines.append(line)
        
        # 如果有修改且不是演习模式，写回文件
        if replaced_count > 0 and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        return replaced_count, not_found_ids
    
    # 读取文件内容 (非CSV文件)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 处理JSON文件
    if ext.lower() == '.json':
        try:
            # 尝试解析JSON
            data = json.loads(content)
              # 递归处理JSON对象中的behavior_id和status_id字段
            def process_json_object(obj):
                nonlocal replaced_count, not_found_ids
                
                if isinstance(obj, dict):
                    # 检查当前对象是否有behavior_id字段
                    if 'behavior_id' in obj:
                        if isinstance(obj['behavior_id'], int):
                            behavior_id = obj['behavior_id']
                            if behavior_id in id_to_name:
                                obj['behavior_id'] = id_to_name[behavior_id]
                                replaced_count += 1
                            elif behavior_id != 0:  # 不计入ID为0的未找到情况
                                not_found_ids.add(behavior_id)
                    
                    # 检查当前对象是否有status_id字段
                    if 'status_id' in obj:
                        # status_id可能是字符串形式的数字
                        try:
                            status_id = int(obj['status_id'])
                            if status_id in id_to_name:
                                obj['status_id'] = id_to_name[status_id]
                                replaced_count += 1
                            elif status_id != 0:  # 不计入ID为0的未找到情况
                                not_found_ids.add(status_id)
                        except (ValueError, TypeError):
                            # 如果已经是字符串或其他非数字类型，则不处理
                            pass
                    

                    # 递归处理所有子对象
                    for key, value in obj.items():
                        if isinstance(value, (dict, list)):
                            process_json_object(value)
                
                elif isinstance(obj, list):
                    # 递归处理列表中的所有元素
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            process_json_object(item)
            
            # 处理整个JSON对象
            process_json_object(data)
            
            # 将修改后的JSON写回字符串
            modified_content = json.dumps(data, ensure_ascii=False, indent=4)
            
            if not dry_run and modified_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            return replaced_count, not_found_ids
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，回退到正则表达式处理
            pass
    
    # 对于TXT或JSON解析失败的情况，使用正则表达式
    # 查找形如 "behavior_id":数字 或 "behavior_id": 数字 的模式
    pattern = r'("behavior_id"\s*:\s*)(\d+)'
    
    def replace_behavior_id(match):
        nonlocal replaced_count, not_found_ids
        prefix = match.group(1)  # "behavior_id":
        behavior_id = int(match.group(2))  # 数字部分
        
        if behavior_id in id_to_name:
            replaced_count += 1
            # 返回带引号的en_name
            return f'{prefix}"{id_to_name[behavior_id]}"'
        elif behavior_id != 0:  # 不计入ID为0的未找到情况
            not_found_ids.add(behavior_id)
        
        # 未找到映射，保留原始格式
        return match.group(0)
    
    # 执行替换
    modified_content = re.sub(pattern, replace_behavior_id, content)
    
    # 如果内容有变化且不是演习模式，写回文件
    if not dry_run and modified_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
    
    return replaced_count, not_found_ids

def process_directory(dir_path, id_to_name, dry_run=False):
    """
    递归处理目录中的所有文件
    
    参数:
        dir_path: str - 需要处理的目录路径
        id_to_name: dict - ID到en_name的映射字典
        dry_run: bool - 如果为True，只打印将要进行的更改，不实际修改文件
    """
    total_files = 0
    total_replaced = 0
    all_not_found = set()
    
    print(f"处理目录: {dir_path}")
    
    # 遍历目录中的所有文件和子目录
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # 只处理特定类型的文件
            if file.lower().endswith(('.json', '.txt', '.csv')):
                file_path = os.path.join(root, file)
                total_files += 1
                
                print(f"处理文件: {file_path}")
                replaced, not_found = process_file(file_path, id_to_name, dry_run)
                
                total_replaced += replaced
                all_not_found.update(not_found)
                
                if replaced > 0:
                    print(f"  - 替换了 {replaced} 个behavior_id")
                if not_found:
                    print(f"  - 未找到映射的ID: {sorted(not_found)}")
    
    print(f"\n处理完成:")
    print(f"- 扫描文件数: {total_files}")
    print(f"- 替换总数: {total_replaced}")
    if all_not_found:
        print(f"- 未找到映射的所有ID: {sorted(all_not_found)}")

def main():
    """
    主函数
    """
    base_dir = r"c:\code\era\erArk"
    
    behavior_data_path = os.path.join(base_dir, "data", "csv", "Behavior_Data.csv")
    talk_dir = os.path.join(base_dir, "data", "talk")
    # talk_dir = os.path.join(base_dir, "data", "event")
    
    # 读取behavior_id到en_name的映射
    id_to_name = read_behavior_data(behavior_data_path)
    print(f"读取到 {len(id_to_name)} 个行为ID映射")
    
    # 调试输出部分映射
    print("ID到en_name的部分映射样例:")
    examples = {1, 2, 101, 151, 301, 361, 501, 601, 681, 801}
    for bid in examples:
        if bid in id_to_name:
            print(f"  {bid} -> {id_to_name[bid]}")
    
    # 询问是否为演习模式
    dry_run = input("是否为演习模式(只显示变更而不实际修改文件)? (y/n): ").strip().lower() == 'y'
    
    if dry_run:
        print("\n【演习模式】将显示将要进行的更改，但不会实际修改文件")
    
    # 处理talk目录
    process_directory(talk_dir, id_to_name, dry_run)
    
    if dry_run:
        print("\n演习完成。若要实际进行替换，请重新运行并选择非演习模式。")
    else:
        print("\n所有文件处理完成。")

if __name__ == "__main__":
    main()