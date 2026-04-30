import csv

# 定义txt文件路径
txt_path = 'name.txt'
# 定义输出csv文件路径
csv_path = 'output.csv'

# 读取txt文件并按行存入列表
def read_txt_to_list(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    result = []
    current_element = []
    
    for line in lines:
        # 如果读到完全空行，将当前元素加入结果列表
        if line == '\n':
            if current_element:
                # 将除了最后一个换行符之外的换行符都替换为 \n
                element = ''.join(current_element).strip()
                element = element.replace('\n', '\\n')
                element = element.replace('\\n\\n', '\n')
                result.append(element)
                current_element = []
        else:
            current_element.append(line)
    
    # 处理文件末尾没有空行的情况
    if current_element:
        element = ''.join(current_element).strip()
        element = element.replace('\n', '\\n')
        element = element.replace('\\n\\n', '\n')
        result.append(element)
    
    return result

# 将列表数据保存到csv文件
def save_list_to_csv(data, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 初始化条目编号
        count = 1
        for element in data:
            # 按行写入csv文件
            writer.writerow([count, 101, 1, 'high_1', element])
            count += 1

if __name__ == "__main__":
    # 读取txt文件内容
    data = read_txt_to_list(txt_path)
    # 保存内容到csv文件
    save_list_to_csv(data, csv_path)
