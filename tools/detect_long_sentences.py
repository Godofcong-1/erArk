#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV文件长句检测工具
用于检测指定目录及其子目录下所有CSV文件中第5列文本的过长句子
"""

import os
import csv
import pandas as pd
from typing import List, Tuple


def detect_long_sentences_in_text(text: str, max_length: int = 110) -> List[Tuple[str, int]]:
    """
    检测文本中的过长句子
    
    参数:
        text (str): 要检测的文本内容
        max_length (int): 句子最大长度限制，默认110字符
    
    返回值:
        List[Tuple[str, int]]: 过长句子列表，包含句子内容和长度
    """
    # 如果文本为空或不是字符串，返回空列表
    if not isinstance(text, str) or not text.strip():
        return []
    
    # 使用换行符分割文本为句子
    sentences = text.split('\\n')
    long_sentences = []
    
    # 检查每个句子的长度
    for sentence in sentences:
        # 去除首尾空白字符
        sentence = sentence.strip()
        if len(sentence) > max_length:
            long_sentences.append((sentence, len(sentence)))
    
    return long_sentences


def process_csv_file(file_path: str) -> List[dict]:
    """
    处理单个CSV文件，检测第5列中的过长句子
    
    参数:
        file_path (str): CSV文件路径
    
    返回值:
        List[dict]: 包含过长句子信息的字典列表
    """
    results = []
    
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # 检查是否至少有5列
        if df.shape[1] < 5:
            print(f"警告: 文件 {file_path} 列数不足5列，跳过处理")
            return results
        
        # 获取第5列数据（索引为4）
        fifth_column = df.iloc[:, 4]
        
        # 遍历第5列的每一行
        for row_index, text_content in enumerate(fifth_column):
            # 检测当前行文本中的过长句子
            long_sentences = detect_long_sentences_in_text(str(text_content))
            
            # 为每个过长句子创建记录
            for sentence, length in long_sentences:
                result = {
                    '文件路径': file_path,
                    '行号': row_index + 1,  # CSV行号从1开始
                    '过长句子': sentence,
                    '句子长度': length,
                    '最大长度限制': 110
                }
                results.append(result)
                
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    return results


def scan_directory_for_csv_files(directory: str) -> List[str]:
    """
    扫描指定目录及其子目录，查找所有CSV文件
    
    参数:
        directory (str): 要扫描的目录路径
    
    返回值:
        List[str]: CSV文件路径列表
    """
    csv_files = []
    
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件扩展名是否为.csv
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                csv_files.append(file_path)
    
    return csv_files


def save_results_to_csv(results: List[dict], output_file: str) -> None:
    """
    将检测结果保存到CSV文件
    
    参数:
        results (List[dict]): 检测结果列表
        output_file (str): 输出CSV文件路径
    
    返回值:
        None
    """
    # 如果没有检测到过长句子
    if not results:
        print("未检测到任何过长句子")
        # 创建空的结果文件
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['文件路径', '行号', '过长句子', '句子长度', '最大长度限制'])
        return
    
    # 将结果保存到CSV文件
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False, encoding='utf-8')
    print(f"检测结果已保存到: {output_file}")
    print(f"共发现 {len(results)} 个过长句子")


def main():
    """
    主函数：执行完整的检测流程
    
    参数:
        无
    
    返回值:
        None
    """
    # 获取用户输入的目录路径
    # target_directory = input("请输入要检测的目录路径: ").strip()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 文件路径
    target_directory = os.path.join(base_dir, 'data', 'talk')

    # 检查目录是否存在
    if not os.path.exists(target_directory):
        print(f"错误: 目录 {target_directory} 不存在")
        return
    
    if not os.path.isdir(target_directory):
        print(f"错误: {target_directory} 不是一个有效的目录")
        return
    
    print(f"开始扫描目录: {target_directory}")
    
    # 扫描目录获取所有CSV文件
    csv_files = scan_directory_for_csv_files(target_directory)
    
    if not csv_files:
        print("在指定目录中未找到任何CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 处理所有CSV文件
    all_results = []
    for i, csv_file in enumerate(csv_files, 1):
        print(f"正在处理文件 {i}/{len(csv_files)}: {csv_file}")
        results = process_csv_file(csv_file)
        all_results.extend(results)
    
    # 设置输出文件路径
    output_file = os.path.join(target_directory, "long_sentences_detection_results.csv")
    
    # 保存结果到CSV文件
    save_results_to_csv(all_results, output_file)


if __name__ == "__main__":
    main()