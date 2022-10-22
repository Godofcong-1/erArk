from Script.Config import game_config

'''
自动生成前提的文件
'''


# 1前提生成
mode = 1
command_str = "t_lubrication_l_7"
capital_command = command_str.upper()
dataname = "润滑"
# A:能力数值,S:状态数值,T:素质
datetype = "S"

# 数据初始化
game_config.init()

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

if mode == 1:
    with open("Script\\Design\\handle_premise.py", "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入前提文件末尾")
