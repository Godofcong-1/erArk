"""
重组 InstructConfig.csv：
1. 列名重命名和移动
2. 按 instruct_type 和 instruct_sub_type 重新分配 cid
3. 重命名 web 相关列
"""
import pandas as pd
import os

def reorganize_csv():
    csv_path = 'data/csv/InstructConfig.csv'
    
    # 读取CSV，跳过前5行元数据（第1行列名，第2-5行是描述和配置行）
    df = pd.read_csv(csv_path, skiprows=5, header=None)
    
    # 手动设置列名
    df.columns = ['cid', 'instruct_id', 'instruct_type', 'name', 'premise_set', 
                  'behavior_id', 'sub_type', 'category', 'panel_id', 
                  'major_type', 'minor_type', 'body_parts']
    
    print(f"原始数据行数: {len(df)}")
    print(f"原始列名: {df.columns.tolist()}")
    
    # 1. 列名重命名
    rename_map = {
        'sub_type': 'instruct_sub_type',
        'category': 'web_category',
        'major_type': 'web_major_type',
        'minor_type': 'web_minor_type'
    }
    df = df.rename(columns=rename_map)
    print(f"\n重命名后列名: {df.columns.tolist()}")
    
    # 2. 重新排列列顺序
    # 目标顺序: cid, instruct_id, name, instruct_type, instruct_sub_type, premise_set, behavior_id, web_category, panel_id, web_major_type, web_minor_type, body_parts
    new_column_order = [
        'cid', 'instruct_id', 'name', 'instruct_type', 'instruct_sub_type',
        'premise_set', 'behavior_id', 'web_category', 'panel_id',
        'web_major_type', 'web_minor_type', 'body_parts'
    ]
    df = df[new_column_order]
    print(f"重排后列名: {df.columns.tolist()}")
    
    # 3. 按 instruct_type 和 instruct_sub_type 重新分配 cid
    # instruct_type 到基础值的映射
    type_base_map = {
        'SYSTEM': 0,
        'DAILY': 1000,
        'WORK': 2000,
        'PLAY': 3000,
        'ARTS': 4000,
        'OBSCENITY': 5000,
        'SEX': 6000
    }
    
    # 为每个 instruct_type 收集其所有 instruct_sub_type
    type_subtype_map = {}
    for itype in type_base_map.keys():
        type_df = df[df['instruct_type'] == itype]
        # 获取去重后的 instruct_sub_type，处理 NaN 和 '0'
        subtypes = type_df['instruct_sub_type'].fillna('0').unique()
        # 过滤掉 '0'，然后排序
        subtypes = sorted([st for st in subtypes if st != '0' and st != 0])
        # 把 '0' 放到最前面
        if '0' in type_df['instruct_sub_type'].fillna('0').values or 0 in type_df['instruct_sub_type'].fillna(0).values:
            subtypes = ['0'] + subtypes
        type_subtype_map[itype] = subtypes
    
    print("\n每个 instruct_type 的 instruct_sub_type 分布:")
    for itype, subtypes in type_subtype_map.items():
        print(f"  {itype}: {subtypes}")
    
    # 分配新的 cid
    # 先按原始顺序给每个组合分配序号
    df['temp_group'] = df['instruct_type'] + '_' + df['instruct_sub_type'].fillna('0').astype(str)
    df['temp_seq'] = df.groupby('temp_group').cumcount() + 1
    
    new_cid_list = []
    for idx, row in df.iterrows():
        itype = row['instruct_type']
        isubtype = row['instruct_sub_type']
        
        if pd.isna(isubtype) or isubtype == '0' or isubtype == 0:
            isubtype = '0'
        
        base = type_base_map.get(itype, 9000)
        
        # 找到 subtype 在列表中的索引
        subtypes = type_subtype_map.get(itype, ['0'])
        if isubtype in subtypes:
            subtype_idx = subtypes.index(isubtype)
        else:
            subtype_idx = 0
        
        # 使用预计算的序号
        seq = row['temp_seq'] - 1  # -1 因为我们从1开始计数的
        
        # 新 cid = base + subtype_idx * 100 + seq + 1
        new_cid = base + subtype_idx * 100 + seq + 1
        new_cid_list.append(new_cid)
    
    df['cid'] = new_cid_list
    
    # 删除临时列
    df = df.drop(columns=['temp_group', 'temp_seq'])
    
    # 按 cid 排序
    df = df.sort_values('cid').reset_index(drop=True)
    
    # 确保数值类型列为整数，空值用 0 填充
    # 【重构更新 2026-01-19】web_major_type 和 web_minor_type 现在是字符串类型
    numeric_cols = ['cid', 'web_category']
    for col in numeric_cols:
        if col in df.columns:
            # 将空字符串和NaN转为0，然后转整数
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    print(f"\n新 cid 范围: {df['cid'].min()} - {df['cid'].max()}")
    print("\n每个 instruct_type 的 cid 范围:")
    for itype in type_base_map.keys():
        type_df = df[df['instruct_type'] == itype]
        if len(type_df) > 0:
            print(f"  {itype}: {type_df['cid'].min()} - {type_df['cid'].max()} (共 {len(type_df)} 条)")
    
    # 4. 准备写回文件，需要加上元数据行
    # 读取原始文件的前5行作为元数据
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        metadata_lines = [f.readline() for _ in range(5)]
    
    # 更新第一行的列名（因为列顺序和名称都变了）
    metadata_lines[0] = ','.join(new_column_order) + '\n'
    
    # 更新第二行的中文描述
    chinese_names = {
        'cid': '指令配置id',
        'instruct_id': '指令id',
        'name': '显示名称',
        'instruct_type': '指令类型',
        'instruct_sub_type': '指令子类型',
        'premise_set': '前提条件集',
        'behavior_id': '行为id',
        'web_category': 'Web三类分类',
        'panel_id': '面板id',
        'web_major_type': 'Web大类型',
        'web_minor_type': 'Web小类型',
        'body_parts': '关联身体部位'
    }
    metadata_lines[1] = ','.join([chinese_names[col] for col in new_column_order]) + '\n'
    
    # 更新第三行的类型描述（instruct_sub_type也是str类型）
    # 【重构更新 2026-01-19】web_major_type 和 web_minor_type 改为 str 类型
    type_desc = {
        'cid': 'int',
        'instruct_id': 'str',
        'name': 'str',
        'instruct_type': 'str',
        'instruct_sub_type': 'str',
        'premise_set': 'str',
        'behavior_id': 'str',
        'web_category': 'int',
        'panel_id': 'str',
        'web_major_type': 'str',
        'web_minor_type': 'str',
        'body_parts': 'str'
    }
    metadata_lines[2] = ','.join([type_desc[col] for col in new_column_order]) + '\n'
    
    # 写回文件
    backup_path = csv_path.replace('.csv', '_backup.csv')
    os.rename(csv_path, backup_path)
    print(f"\n原文件备份到: {backup_path}")
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        # 写入元数据行
        for line in metadata_lines:
            f.write(line)
        # 写入数据（不包含header，因为已经在元数据中）
        df.to_csv(f, index=False, header=False)
    
    print(f"\n新文件已写入: {csv_path}")
    print(f"总数据行数: {len(df)}")
    
    # 显示前10行的 cid 和基本信息
    print("\n前10行预览:")
    print(df[['cid', 'instruct_id', 'name', 'instruct_type', 'instruct_sub_type']].head(10))
    
    return df

if __name__ == '__main__':
    df = reorganize_csv()
    print("\n重组完成！")
