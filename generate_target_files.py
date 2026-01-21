"""
批量生成目标文件脚本
在 .github/prompts/AI文本生成工作流/生成目标文件 目录下生成指定数量的CSV文件
"""
import os

# 文件模板内容
TEMPLATE_CONTENT = """cid,behavior_id,adv_id,premise,context
口上id,触发口上的行为id,口上限定的剧情npcid,前提id,口上内容
str,str,int,str,str
0,0,0,0,1
口上配置数据,,,,
"""

def generate_files(start_num, end_num, target_dir):
    """
    生成指定范围的目标文件
    
    Keyword arguments:
    start_num -- 起始序号
    end_num -- 结束序号
    target_dir -- 目标目录
    
    Return:
    生成的文件数量
    """
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    generated_count = 0
    
    for i in range(start_num, end_num + 1):
        file_path = os.path.join(target_dir, f"生成目标文件{i}.csv")
        
        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f"跳过已存在的文件: {file_path}")
            continue
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(TEMPLATE_CONTENT)
        
        generated_count += 1
        print(f"已生成: {file_path}")
    
    return generated_count

if __name__ == "__main__":
    # 配置参数
    START_NUM = 21
    END_NUM = 128
    TARGET_DIR = r".github\prompts\AI文本生成工作流\生成目标文件"
    
    print(f"开始生成文件，范围: {START_NUM} 到 {END_NUM}")
    print(f"目标目录: {TARGET_DIR}")
    print("-" * 50)
    
    count = generate_files(START_NUM, END_NUM, TARGET_DIR)
    
    print("-" * 50)
    print(f"完成！共生成 {count} 个文件")
