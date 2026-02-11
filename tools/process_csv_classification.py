"""
CSV文件分类统计脚本
功能：从第6行开始遍历CSV文件，根据第2列进行分类统计
"""
import csv
from collections import defaultdict
from pathlib import Path


def process_csv_file(csv_file_path):
    """
    处理CSV文件并统计第2列的分类信息
    
    参数:
        csv_file_path: CSV文件路径
    """
    # 用于存储分类统计：{第2列的值: 行数列表}
    classification = defaultdict(list)
    
    # 读取CSV文件
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # 跳过前5行（索引0-4）
        for i in range(5):
            next(reader, None)
        
        # 从第6行开始处理（索引5开始）
        row_number = 6  # 实际行号
        for row in reader:
            if len(row) >= 2:  # 确保行至少有2列
                type_id = row[1]  # 第2列（索引1）
                classification[type_id].append(row_number)
            row_number += 1
    
    # 输出统计结果
    print("=" * 60)
    print("CSV文件分类统计结果")
    print("=" * 60)
    print(f"\n总分类数：{len(classification)}")
    print(f"\n详细统计：\n")
    
    # 按分类输出
    for idx, (type_id, rows) in enumerate(sorted(classification.items()), 1):
        print(f"分类 {idx}:")
        print(f"  第2列值：{type_id}")
        print(f"  行数：{len(rows)}")
        print(f"  行号范围：{min(rows)} - {max(rows)}")
        print()
    
    # 输出总行数
    total_rows = sum(len(rows) for rows in classification.values())
    print("=" * 60)
    print(f"处理的总行数：{total_rows}")
    print("=" * 60)
    
    return classification


def main():
    # CSV文件路径
    csv_file = Path(__file__).parent.parent / ".github" / "prompts" / "AI文本生成工作流" / "生成完待处理数据.csv"
    
    if not csv_file.exists():
        print(f"错误：找不到文件 {csv_file}")
        print("请确保CSV文件存在，或者修改脚本中的文件路径。")
        return
    
    print(f"正在处理文件：{csv_file}\n")
    
    # 处理文件
    process_csv_file(csv_file)


if __name__ == "__main__":
    main()
