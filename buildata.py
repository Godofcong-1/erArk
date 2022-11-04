from Script.Config import game_config

'''
自动生成前提的文件
'''


# 1前提生成到py里,2前提文件转csv,3csv转前提文件
mode = 2
command_str = "t_lubrication_l_7"
capital_command = command_str.upper()
dataname = "润滑"
# A:能力数值,S:状态数值,T:素质
datetype = "S"

# 数据初始化
game_config.init()

def constand_2_handle():
    '''
    输出constand_promise里的标准格式，以及自动填入handle_premise.py里
    '''

    # 判断数据编号
    if datetype == "A":
        datetype_str = "ability"
        for config_data_index in game_config.config_ability:
            if game_config.config_ability[config_data_index].name == dataname:
                data_index = config_data_index
                break
    elif datetype == "S":
        datetype_str = "status_data"
        for config_data_index in game_config.config_character_state:
            if game_config.config_character_state[config_data_index].name == dataname:
                data_index = config_data_index
                break
    elif datetype == "T":
        datetype_str = "talent"
        for config_data_index in game_config.config_talent:
            if game_config.config_talent[config_data_index].name == dataname:
                data_index = config_data_index
                break
    print(f"数据名 = {dataname}，类型 = {datetype_str}，id = {config_data_index}")

    command_list = command_str.split('_')

    # 判断运算符号
    operation = "=="
    for str_part in command_list:
        if str_part == "ge":
            operation = ">="
            break
        elif str_part == "le":
            operation = "<="
            break
        elif str_part == "g":
            operation = ">"
            break
        elif str_part == "l":
            operation = "<"
            break

    #判断是否为交互对象
    target_flag = False
    for str_part in command_list:
        if str_part == "t":
            target_flag = True
            break

    # 进行变量名输出
    out_str = "\n"
    out_str += f"    {capital_command} = \"{command_str}\"\n"
    if not target_flag:
        out_str += f"    \"\"\" {dataname}{operation}{command_list[-1]} \"\"\"\n"
    else:
        out_str += f"    \"\"\" 交互对象{dataname}{operation}{command_list[-1]} \"\"\"\n"
    print(out_str)

    # 进行前提输出
    out_str = "\n\n"
    out_str += f"@add_premise(constant_promise.Premise.{capital_command})\n"
    out_str += f"def handle_{command_str}(character_id: int) -> int:\n"
    out_str += f"    \"\"\"\n"
    if not target_flag:
        out_str += f"    校验角色是否{dataname}{operation}{command_list[-1]}\n"
    else:
        out_str += f"    校验交互对象是否{dataname}{operation}{command_list[-1]}\n"
    out_str += f"    Keyword arguments:\n"
    out_str += f"    character_id -- 角色id\n"
    out_str += f"    Return arguments:\n"
    out_str += f"    int -- 权重\n"
    out_str += f"    \"\"\"\n"
    out_str += f"    character_data = cache.character_data[character_id]\n"
    if target_flag:
        out_str += f"    target_data = cache.character_data[character_data.target_character_id]\n"
        out_str += f"    if target_data.{datetype_str}[{config_data_index}] {operation} {command_list[-1]}:\n"
    else:
        out_str += f"    if character_data.{datetype_str}[{config_data_index}] {operation} {command_list[-1]}:\n"
    out_str += f"        return 1\n"
    out_str += f"    return 0\n"

    # 开始保存
    with open("Script\\Design\\handle_premise.py", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入前提文件末尾")

    return out_str

def constand_2_csv():
    with open("Script\\Core\\constant_promise.py", "r",encoding="utf-8") as f:
        a=f.readlines()
        f.close()
    promise_text_list,promise_type_list,promise_cid_list = [],[],[]
    out_str = "\n"

    for line in a:
        if len(line) >= 3 and line[-2] == "\"":
            if line[-3] == "\"":
                promise_text = line.split("\"")[-4].strip()
                if promise_text != "前提id":
                    promise_type,promise_info = promise_text.split(" ")[0],promise_text.split(" ")[1]
                    out_str += f"{promise_type},{promise_info}\n"
                # print(f"debug promise_text = {promise_text}")
            else:
                promise_cid = line.split("\"")[-2].strip()
                out_str += f"{promise_cid},"
                # print(f"debug promise_cid = {promise_cid}")
        elif len(line) == 1:
            out_str += "\n"

    # 开始保存
    with open("tools\\premise.csv", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入csv文件末尾")

    return out_str

def csv_2_constand():
    with open("tools\\premise.csv", "r",encoding="utf-8") as f:
        a=f.readlines()
        # print(a)
        f.close()

    out_str = "\n"
    for line in a:
        promise_text = line.strip().split(",")
        # print(f"debug promise_text = {promise_text}")
        if len(promise_text) == 1:
            out_str += "\n"
        elif promise_text[0] != "cid":
            out_str += f"    {promise_text[0].upper()} = \"{promise_text[0]}\"\n"
            out_str += f"    \"\"\" {promise_text[1]} {promise_text[2]} \"\"\"\n"


    # 开始保存
    with open("Script\\Core\\constant_promise.py", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入前提文件末尾")

    return out_str

if __name__ == "__main__":
    if mode == 1:
        out_str = constand_2_handle()
    elif mode == 2:
        constand_2_csv()
    elif mode == 3:
        csv_2_constand()
