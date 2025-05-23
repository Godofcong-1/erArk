#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
读取Behavior_Data.csv和BehaviorEffect.csv，创建一个新的BehaviorEffect_converted.csv文件
新文件中将behavior_id列的int值替换为Behavior_Data.csv中对应的en_name值
"""

import os

def read_behavior_data(file_path):
    """
    读取Behavior_Data.csv文件，构建id到en_name的映射
    
    参数:
        file_path: Behavior_Data.csv的文件路径
    
    返回:
        包含id到en_name映射的字典
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

def create_converted_file(behavior_data_path, behavior_effect_path, output_path):
    """
    创建转换后的BehaviorEffect.csv文件
    
    参数:
        behavior_data_path: Behavior_Data.csv的文件路径
        behavior_effect_path: BehaviorEffect.csv的文件路径
        output_path: 输出文件路径
    """
    # 读取behavior_id到en_name的映射
    id_to_name = read_behavior_data(behavior_data_path)
    print(f"读取到 {len(id_to_name)} 个行为ID映射")
    
    # 调试输出部分映射
    print("ID到en_name的部分映射样例:")
    examples = {1, 2, 101, 151, 301, 361, 501, 601, 681, 801}
    for bid in examples:
        if bid in id_to_name:
            print(f"  {bid} -> {id_to_name[bid]}")
    
    # 读取BehaviorEffect.csv文件
    with open(behavior_effect_path, 'r', encoding='utf-8') as f:
        effect_lines = f.readlines()
    
    # 处理文件
    new_lines = []
    replaced_count = 0
    not_found_count = 0
    skip_count = 0
    header_done = False
    
    for line in effect_lines:
        # 保留注释行
        if line.startswith("//"):
            new_lines.append(line)
            continue
        
        # 跳过前几行头部信息
        if not header_done:
            skip_count += 1
            new_lines.append(line)
            # 前4行为表头，之后开始处理数据行
            if skip_count >= 4:
                header_done = True
            continue
        
        # 处理"行为结算器配置"行
        if "行为结算器配置" in line:
            new_lines.append(line)
            continue
        
        # 处理数据行
        parts = line.strip().split(',')
        if len(parts) >= 3:  # 确保有足够的列（cid, behavior_id, effect_id）
            try:
                behavior_id = int(parts[1])
                if behavior_id in id_to_name:
                    parts[1] = id_to_name[behavior_id]
                    new_line = ','.join(parts) + '\n'
                    new_lines.append(new_line)
                    replaced_count += 1
                else:
                    # 如果找不到对应的en_name，保留原值
                    new_lines.append(line)
                    if behavior_id != 0:  # 不显示ID为0的警告
                        print(f"警告: 无法找到ID为 {behavior_id} 的对应en_name")
                    not_found_count += 1
            except ValueError:
                # 非整数值，保留原行
                new_lines.append(line)
        else:
            # 行格式不符合预期，保留原行
            new_lines.append(line)
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"转换完成: 成功替换 {replaced_count} 行, 未找到映射 {not_found_count} 行")

def main():
    """
    主函数
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    behavior_data_path = os.path.join(base_dir, "data", "csv", "Behavior_Data.csv")
    behavior_effect_path = os.path.join(base_dir, "data", "csv", "BehaviorEffect.csv")
    
    # 创建转换后的文件
    output_path = os.path.join(base_dir, "data", "csv", "BehaviorEffect_converted.csv")
    create_converted_file(behavior_data_path, behavior_effect_path, output_path)
    print(f"文件已转换并保存为: {output_path}")
    
    # 询问是否替换原文件
    replace_original = input("是否替换原始的BehaviorEffect.csv文件? (y/n): ").strip().lower()
    if replace_original == 'y':
        # 创建备份
        backup_path = os.path.join(base_dir, "data", "csv", "BehaviorEffect.bak.csv")
        print(f"创建备份: {backup_path}")
        
        import shutil
        shutil.copy2(behavior_effect_path, backup_path)
        
        # 替换原文件
        shutil.copy2(output_path, behavior_effect_path)
        print(f"原文件已替换，备份文件保存为: {backup_path}")
    else:
        print("原文件未被修改。")

if __name__ == "__main__":
    main()