from Script.Config import game_config

'''
自动生成前提的文件
'''


# 1单条前提生成到三个文件里,2前提文件转csv,3csv转前提文件,4结算文件转csv,5csv转结算文件,6前提文件转在线表格,7行为文件转status
mode = 4
command_str = "lactation_1"
capital_command = command_str.upper()
dataname = "泌乳"
datetype = "T"
premise_type_diy = "自定义内容"
premise_type_dict = {"A":"属性_能力","S":"属性_状态","T":"属性_素质","X":premise_type_diy}
premise_type = premise_type_dict[datetype]

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
    elif datetype == "X":
        datetype_str,data_index = "数据类型","数据序号"
    print(f"数据名 = {dataname}，类型 = {datetype_str}，id = {data_index}")

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

    # 生成constant_promise的out_str
    out_str = "\n"
    out_str += f"    {command_str.upper()} = \"{command_str}\"\n"
    out_str += f"    \"\"\" {premise_type} "
    if target_flag:
        out_str += f"交互对象"
    else:
        out_str += f"自己"
    out_str += f"{dataname}{operation}{command_list[-1]} \"\"\"\n"
    print(out_str)

    # 输出到constant_promise里，还没写出来
    '''
    break_flag = 0
    with open("Script\\Core\\constant_promise.py", "r+",encoding="utf-8") as f:
        while 1:
            a=f.readline() # 逐行读取
            if len(a) >= 3 and a[-3] == "\"": # 锁定到文字行
                promise_text = a.split("\"")[-4].strip()
                if promise_text != "前提id":
                    # print(f"debug promise_text = {promise_text}")
                    promise_type,promise_info = promise_text.split(" ")[0],promise_text.split(" ")[1]
                    if promise_type == premise_type:
                        break_flag = 1
                    if break_flag == 1 and promise_type != premise_type:
                        f.write(out_str)
                        break
        f.close()
    out_str = "\n"
    '''

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
        out_str += f"    if target_data.{datetype_str}[{data_index}] {operation} {command_list[-1]}:\n"
    else:
        out_str += f"    if character_data.{datetype_str}[{data_index}] {operation} {command_list[-1]}:\n"
    out_str += f"        return 1\n"
    out_str += f"    return 0\n"

    # 开始保存
    with open("Script\\Design\\handle_premise.py", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入前提文件末尾")

    return out_str

def constand_promise_2_csv():
    with open("Script\\Core\\constant_promise.py", "r",encoding="utf-8") as f:
        a=f.readlines()
        f.close()
    out_str = "cid,premise_name,premise_type,premise\n"

    for line in a:
        if len(line) >= 3 and line[-2] == "\"" and "#" not in line:
            if line[-3] == "\"":
                promise_text = line.split("\"")[-4].strip()
                if promise_text != "前提id":
                    promise_type,promise_info = promise_text.split(" ")[0],promise_text.split(" ")[1]
                    out_str += f"{promise_type},{promise_info}\n"
                    # out_str += f"未分类,{promise_text}\n"
                # print(f"debug promise_text = {promise_text}")
            else:
                promise_cid = line.split("\"")[-2].strip()
                promise_name = line.split(" =")[0].strip()
                out_str += f"{promise_cid},{promise_name},"
                # print(f"debug promise_name = {promise_name}")
        elif len(line) == 1:
            out_str += "\n"

    # 开始保存
    with open("tools\\ArkEditor\\csv\\premise.csv", "w",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入csv文件末尾")

    return out_str

def csv_2_constand():
    with open("tools\\csv\\premise.csv", "r",encoding="utf-8") as f:
        a=f.readlines()
        # print(a)
        f.close()

    out_str = "\n"
    for line in a:
        promise_text = line.strip().split(",")
        print(f"debug promise_text = {promise_text}")
        if len(promise_text) == 1:
            out_str += "\n"
        elif promise_text[0] != "cid" and len(promise_text) == 4:
            out_str += f"    {promise_text[1]} = \"{promise_text[0]}\"\n"
            out_str += f"    \"\"\" {promise_text[2]} {promise_text[3]} \"\"\"\n"


    # 开始保存
    with open("Script\\Core\\constant_promise.py", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入前提文件末尾")

    return out_str

def constand_effect_2_csv():
    with open("Script\\Core\\constant_effect.py", "r",encoding="utf-8") as f:
        a=f.readlines()
        f.close()
    out_str = "cid,effect_name,effect_type,effect\n"

    for line in a:
        # 到二段结算则跳出
        if "二段结算" in line:
            break
        if len(line) >= 3 and "#" not in line:
            if line[-3] == "\"" and " " in line:
                effect_text = line.split("\"")[-4].strip().split(" ")
                if len(effect_text) == 2:
                    # print(f"debug effect_text = {effect_text}")
                    out_str += f"{effect_text[0]},{effect_text[1]}\n"
                else:
                    out_str += f"二段结算,{str(effect_text)[2:-2]}\n"
            elif "=" in line:
                effect_name = line.split("\"")[-1].strip().split(" ")[0]
                effect_cid = line.split("\"")[-1].strip().split(" ")[-1]
                out_str += f"{effect_cid},{effect_name},"
                # print(f"debug {effect_cid},{effect_name},")
        elif len(line) == 1:
            out_str += "\n"

    # 开始保存
    with open("tools\\ArkEditor\\csv\\Effect.csv", "w",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入csv文件末尾")

    return out_str

def csv_2_constand_effect():
    with open("tools\\csv\\Effect.csv", "r",encoding="utf-8") as f:
        a=f.readlines()
        # print(a)
        f.close()

    out_str = "\n"
    for line in a:
        effect_text = line.strip().split(",")
        # print(f"debug promise_text = {promise_text}")
        if len(effect_text) == 1:
            out_str += "\n"
        elif effect_text[0] != "cid":
            out_str += f"    {effect_text[1]} = {effect_text[0]}\n"
            out_str += f"    \"\"\" {effect_text[2]} {effect_text[3]} \"\"\"\n"


    # 开始保存
    with open("Script\\Core\\constant_effect.py", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入结算文件末尾")

    return out_str


if __name__ == "__main__":
    if mode == 1:
        out_str = constand_2_handle()
    elif mode == 2:
        constand_promise_2_csv()
    elif mode == 3:
        csv_2_constand()
    elif mode == 4:
        constand_effect_2_csv()
    elif mode == 5:
        csv_2_constand_effect()
