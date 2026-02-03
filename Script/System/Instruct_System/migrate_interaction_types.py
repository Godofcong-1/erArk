# -*- coding: utf-8 -*-
"""
迁移脚本：将 InstructConfig.csv 中的 web_major_type 和 web_minor_type 从数字转换为字符串标识符

运行方式：
  python -c "from Script.System.Instruct_System.migrate_interaction_types import migrate; migrate()"
  
或者在项目根目录下运行：
  python Script/System/Instruct_System/migrate_interaction_types.py
"""

import csv
import os
import shutil
from datetime import datetime

# 旧数字ID到新字符串ID的映射
OLD_MAJOR_TYPE_ID_TO_NEW = {
    0: "mouth",
    1: "hand",
    2: "penis",
    3: "tool",
    4: "other",
}

OLD_MINOR_TYPE_ID_TO_NEW = {
    0: "mouth_talk",
    1: "mouth_kiss",
    2: "mouth_lick",
    10: "hand_touch",
    11: "hand_slap",
    12: "hand_dress",
    20: "penis_rub",
    21: "penis_insert",
    30: "tool_drug",
    31: "tool_item",
    40: "other_misc",
}


def migrate():
    """执行迁移"""
    # 计算 CSV 文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    csv_path = os.path.join(project_root, "data", "csv", "InstructConfig.csv")
    
    if not os.path.exists(csv_path):
        print(f"错误：找不到文件 {csv_path}")
        return False
    
    # 创建备份
    backup_path = csv_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(csv_path, backup_path)
    print(f"已创建备份：{backup_path}")
    
    # 读取 CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if len(rows) < 5:
        print("错误：CSV 文件格式不正确")
        return False
    
    # 找到 web_major_type 和 web_minor_type 的列索引
    header = rows[0]
    try:
        major_type_col = header.index('web_major_type')
        minor_type_col = header.index('web_minor_type')
    except ValueError as e:
        print(f"错误：找不到列 {e}")
        return False
    
    print(f"web_major_type 列索引: {major_type_col}")
    print(f"web_minor_type 列索引: {minor_type_col}")
    
    # 转换数据行（从第5行开始，跳过表头、中文注释、类型行、默认值行、表名行）
    converted_count = 0
    for i in range(5, len(rows)):
        row = rows[i]
        if len(row) <= max(major_type_col, minor_type_col):
            continue
        
        # 转换 major_type
        old_major = row[major_type_col].strip()
        if old_major and old_major.isdigit():
            old_id = int(old_major)
            if old_id in OLD_MAJOR_TYPE_ID_TO_NEW:
                row[major_type_col] = OLD_MAJOR_TYPE_ID_TO_NEW[old_id]
                converted_count += 1
        
        # 转换 minor_type
        old_minor = row[minor_type_col].strip()
        if old_minor and old_minor.isdigit():
            old_id = int(old_minor)
            if old_id in OLD_MINOR_TYPE_ID_TO_NEW:
                row[minor_type_col] = OLD_MINOR_TYPE_ID_TO_NEW[old_id]
                converted_count += 1
    
    # 更新类型行（第3行）
    if len(rows) > 2:
        type_row = rows[2]
        if len(type_row) > major_type_col:
            type_row[major_type_col] = 'str'
        if len(type_row) > minor_type_col:
            type_row[minor_type_col] = 'str'
    
    # 写回 CSV
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"迁移完成！共转换 {converted_count} 个值")
    print(f"原始文件已更新：{csv_path}")
    return True


if __name__ == "__main__":
    migrate()
