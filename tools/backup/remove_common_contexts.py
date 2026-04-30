"""
功能：批量清理body_part目录下csv文件中context列与common_s_A.csv重复的行，并覆盖原文件。
输入参数：无（直接操作指定目录下的文件）
输出：无返回值，直接覆盖原csv文件
"""

import os
import csv

# 定义常量，指定要处理的目录和基准文件
BODY_PART_DIR = r"data\talk_common\body_part"
COMMON_FILE = "common_s_A.csv"

def get_common_contexts(common_file_path):
    """
    功能：读取common_s_A.csv文件，收集所有context列的内容
    输入参数：
        common_file_path (str): common_s_A.csv的完整路径
    返回值：
        set[str]: 所有context列的字符串集合
    """
    common_contexts = set()
    # 打开common_s_A.csv文件
    with open(common_file_path, encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        # 遍历每一行，收集context列
        for row in reader:
            # 只收集非空context
            context = row.get("context", "").strip()
            if context:
                common_contexts.add(context)
    return common_contexts

def clean_csv_file(file_path, common_contexts):
    """
    功能：删除csv文件中context列在common_contexts中的行，并覆盖原文件。
    输入参数：
        file_path (str): 需要处理的csv文件路径
        common_contexts (set[str]): 需要去重的context集合
    返回值：无
    """
    # 读取原文件所有行，保留原始内容
    with open(file_path, encoding="utf-8", newline='') as f:
        lines = f.readlines()
    # 如果文件为空，直接返回
    if not lines:
        return
    # 解析header，获取context列索引
    header = lines[0]
    output_lines = [header]  # 保留header
    # 获取字段名列表
    fieldnames = [h.strip() for h in header.strip().split(',')]
    # 查找context列索引
    try:
        context_idx = fieldnames.index('context')
    except ValueError:
        # 没有context列，直接保留所有行
        output_lines.extend(lines[1:])
        with open(file_path, "w", encoding="utf-8", newline='') as f:
            f.writelines(output_lines)
        return
    # 逐行处理数据部分
    for line in lines[1:]:
        # 如果是空白行，直接保留
        if line.strip() == '':
            output_lines.append(line)
            continue
        # 用逗号分割字段，注意保留分隔符内的内容
        row_fields = list(csv.reader([line]))[0]
        # 如果字段数不足，直接保留
        if len(row_fields) <= context_idx:
            output_lines.append(line)
            continue
        # 获取context字段内容
        context_val = row_fields[context_idx].strip()
        # 如果context在common_contexts中，则跳过该行
        if context_val in common_contexts:
            continue
        # 否则保留该行
        output_lines.append(line)
    # 覆盖写回原文件，保留所有空白行
    with open(file_path, "w", encoding="utf-8", newline='') as f:
        f.writelines(output_lines)

def main():
    """
    功能：主函数，遍历目录并处理所有目标csv文件
    输入参数：无
    返回值：无
    """
    # 获取common_s_A.csv的完整路径
    common_file_path = os.path.join(BODY_PART_DIR, COMMON_FILE)
    # 获取所有需要去重的context
    common_contexts = get_common_contexts(common_file_path)
    # 遍历body_part目录下所有csv文件
    for filename in os.listdir(BODY_PART_DIR):
        # 跳过common_s_A.csv和不含'_A'的文件
        if filename == COMMON_FILE or "_A" not in filename or not filename.endswith(".csv"):
            continue
        file_path = os.path.join(BODY_PART_DIR, filename)
        # 清理文件
        clean_csv_file(file_path, common_contexts)

if __name__ == "__main__":
    # 运行主函数
    main()