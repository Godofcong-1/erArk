#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为效果数据刷新脚本

根据Behavior_Data.csv的数据顺序，重新组织Behavior_Effect.csv的内容。
输入文件：
- data/csv/Behavior_Data.csv: 行为数据配置文件
- data/csv/Behavior_Effect.csv: 行为结算器配置文件
输出文件：
- data/csv/Behavior_Effect_new.csv: 重新组织后的行为结算器配置文件
"""

import csv
import os
from typing import Dict, List, Tuple


def read_behavior_data(file_path: str) -> List[Tuple[str, str, bool]]:
    """
    读取行为数据文件
    
    参数:
        file_path (str): 行为数据文件路径
    
    返回:
        List[Tuple[str, str, bool]]: 包含(cid, en_name, is_empty_line)的元组列表
                                    is_empty_line为True表示该行是空行
    """
    behavior_data = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # 跳过前3行标题行
        for _ in range(3):
            next(reader)
        
        # 遍历所有数据行，包括空行
        for row in reader:
            # 检查是否为完全空白行（所有字段都为空或只包含空白字符）
            is_empty_line = all(not cell.strip() for cell in row) if row else True
            
            if is_empty_line:
                # 添加空行标记
                behavior_data.append(('', '', True))
            elif len(row) >= 2 and row[0] and row[1]:  # 确保有足够的列且不为空
                cid = row[0].strip()
                en_name = row[1].strip()
                
                # 跳过注释行和无效数据，添加有效数据行
                if cid and en_name and not cid.startswith('状态') and cid != 'int':
                    behavior_data.append((cid, en_name, False))
    
    return behavior_data


def read_behavior_effect(file_path: str) -> Tuple[List[str], Dict[str, str]]:
    """
    读取行为效果文件
    
    参数:
        file_path (str): 行为效果文件路径
    
    返回:
        Tuple[List[str], Dict[str, str]]: 
            - 前3行标题内容
            - 字典，键为behavior_id，值为effect_id
    """
    header_lines = []
    effect_data = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # 读取前3行标题
        for i in range(3):
            header_lines.append(next(reader))
        
        # 读取数据行
        for row in reader:
            if len(row) >= 3 and row[1] and row[2]:  # 确保有behavior_id和effect_id
                behavior_id = row[1].strip()
                effect_id = row[2].strip()
                
                # 跳过标题行和无效数据
                if behavior_id and behavior_id != 'behavior_id':
                    effect_data[behavior_id] = effect_id
    
    return header_lines, effect_data


def write_new_behavior_effect(file_path: str, header_lines: List[str], 
                             behavior_data: List[Tuple[str, str, bool]], 
                             effect_data: Dict[str, str]) -> None:
    """
    写入新的行为效果文件
    
    参数:
        file_path (str): 输出文件路径
        header_lines (List[str]): 文件头部行
        behavior_data (List[Tuple[str, str, bool]]): 行为数据列表，包含(cid, en_name, is_empty_line)
        effect_data (Dict[str, str]): 效果数据字典，键为behavior_id，值为effect_id
    
    返回:
        None
    """
    used_behaviors = set()  # 记录已使用的behavior_id
    
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # 写入标题行
        for header_line in header_lines:
            writer.writerow(header_line)
        
        # 根据Behavior_Data.csv的顺序写入数据，包括空行
        for cid, en_name, is_empty_line in behavior_data:
            if is_empty_line:
                # 写入空行，保持与原文件相同的空行位置
                writer.writerow([])
            else:
                # 在effect_data中查找对应的效果ID
                effect_id = effect_data.get(en_name, '')  # 如果找不到则为空字符串
                
                # 写入数据行，使用原始的cid
                writer.writerow([cid, en_name, effect_id])
                
                # 记录已使用的behavior_id
                if en_name in effect_data:
                    used_behaviors.add(en_name)
        
        # 添加未使用的原始数据
        remaining_behaviors = set(effect_data.keys()) - used_behaviors
        if remaining_behaviors:
            print(f"发现 {len(remaining_behaviors)} 个未匹配的行为效果数据，将追加到文件末尾")
            
            # 获取最大的cid值，用于为剩余数据生成新的cid
            max_cid = 0
            for cid, _, is_empty_line in behavior_data:
                if not is_empty_line:  # 只处理非空行的cid
                    try:
                        cid_num = int(cid)
                        max_cid = max(max_cid, cid_num)
                    except ValueError:
                        # 如果cid不是数字，跳过
                        continue
            
            # 将剩余的数据按原样添加到文件末尾，使用递增的cid
            next_cid = max_cid + 1
            for behavior_id in remaining_behaviors:
                effect_id = effect_data[behavior_id]
                writer.writerow([next_cid, behavior_id, effect_id])
                next_cid += 1


def main():
    """
    主函数，执行数据刷新流程
    
    输入: 无
    输出: 无
    功能: 读取CSV文件，处理数据匹配，生成新的行为效果文件
    """
    # 定义文件路径
    behavior_data_path = 'data/csv/Behavior_Data.csv'
    behavior_effect_path = 'data/csv/Behavior_Effect.csv'
    output_path = 'data/csv/Behavior_Effect_new.csv'
    
    try:
        print("开始读取行为数据文件...")
        # 读取行为数据，包含空行信息
        behavior_data = read_behavior_data(behavior_data_path)
        print(f"成功读取 {len(behavior_data)} 行数据（包含空行）")
        
        print("开始读取行为效果文件...")
        # 读取行为效果数据
        header_lines, effect_data = read_behavior_effect(behavior_effect_path)
        print(f"成功读取 {len(effect_data)} 条行为效果数据")
        
        print("开始生成新的行为效果文件...")
        # 生成新的行为效果文件，保持空行位置
        write_new_behavior_effect(output_path, header_lines, behavior_data, effect_data)
        
        print(f"数据刷新完成！新文件已保存到: {output_path}")
        
        # 统计信息 - 计算有效数据行数（排除空行）
        valid_behavior_count = sum(1 for _, _, is_empty in behavior_data if not is_empty)
        matched_count = sum(1 for _, en_name, is_empty in behavior_data 
                          if not is_empty and en_name in effect_data)
        unmatched_count = valid_behavior_count - matched_count
        empty_line_count = sum(1 for _, _, is_empty in behavior_data if is_empty)
        
        print(f"\n统计信息:")
        print(f"- 总数据行数: {len(behavior_data)}")
        print(f"- 有效行为数据: {valid_behavior_count}")
        print(f"- 空行数量: {empty_line_count}")
        print(f"- 匹配到效果的行为: {matched_count}")
        print(f"- 未匹配到效果的行为: {unmatched_count}")
        print(f"- 原效果数据中剩余未使用: {len(effect_data) - matched_count}")
        
    except FileNotFoundError as e:
        print(f"错误：找不到文件 {e.filename}")
        print("请确保以下文件存在：")
        print(f"- {behavior_data_path}")
        print(f"- {behavior_effect_path}")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


if __name__ == "__main__":
    main()