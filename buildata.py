import os

from Script.Config import game_config

'''
自动生成前提的文件
'''


# 1单条前提生成到三个文件里,2前提文件转csv,3csv转前提文件,4结算文件转csv,5csv转结算文件,6前提文件转在线表格,7行为文件转status
mode = 2
command_str = "lactation_1"
capital_command = command_str.upper()
dataname = "泌乳"
datetype = "T"
premise_type_diy = "自定义内容"
premise_type_dict = {"A":"属性_能力","S":"属性_状态","T":"属性_素质","X":premise_type_diy}
premise_type = premise_type_dict[datetype]
premise_module_dict = {"A":"handle_premise_ability.py","S":"handle_premise_other.py","T":"handle_premise_talent.py","X":"handle_premise_other.py"}
""" 各类前提的处理函数写进 handle_premise 包里的哪个模块：能力进能力模块，素质进素质模块，状态与自定义内容进其他通用前提模块 """
premise_module = premise_module_dict[datetype]

# 数据初始化
game_config.init()

def class_end_index(line_list: list, class_name: str) -> int:
    """
    找到一个类的最后一行代码之后的位置，插在这里的代码仍属于这个类
    Keyword arguments:
    line_list -- 代码文件的全部行（readlines() 的结果，每行带换行符）
    class_name -- 类名
    Return arguments:
    int -- 类体最后一个非空行的下一行的下标
    """
    start_index = line_list.index(f"class {class_name}:\n")
    end_index = len(line_list)
    # 类体到下一个顶格的语句为止
    for index in range(start_index + 1, len(line_list)):
        if line_list[index].strip() and line_list[index][0] not in " \t":
            end_index = index
            break
    # 退过类体末尾的空行
    while not line_list[end_index - 1].strip():
        end_index -= 1
    return end_index


def constand_2_handle():
    '''
    输出constand_promise里的标准格式，以及把前提处理函数接到 handle_premise 包里 premise_module 模块的末尾
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
    with open(os.path.join("Script", "Core", "constant_promise.py"), "r+",encoding="utf-8") as f:
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
    # 前提处理函数早已拆成 handle_premise 包（原先的单文件 Script/Design/handle_premise.py 不存在了，往它追加只会新建一个没人导入的文件）
    premise_path = os.path.join("Script", "Design", "handle_premise", premise_module)
    with open(premise_path, "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入{premise_path}末尾")

    return out_str

def build_promise_csv_text(line_list: list) -> str:
    """
    把 constant_promise.py 的全部行转成 ArkEditor 前提表（tools/ArkEditor/csv/Premise.csv）的文本
    只做字符串处理、不读写文件：本模块顶层会调 game_config.init()，回归测试不 import 本模块，
       而是用 ast 单独取出这个函数来跑（tools/tests/education/test_talk_data.py）
    Keyword arguments:
    line_list -- constant_promise.py 的全部行（readlines() 的结果，每行带换行符）
    Return arguments:
    str -- 前提表的完整文本：表头 + 每个前提一行「前提id,常量名,分类,描述」
    """
    out_str = "cid,premise_name,premise_type,premise\n"
    for line in line_list:
        # 只看以引号收尾、不带注释的行：常量行（NAME = "id"）与紧随其后的单行 docstring
        if len(line) >= 3 and line[-2] == "\"" and "#" not in line:
            if line[-3] == "\"":
                # docstring 行：取三引号中间的「分类 描述」
                promise_text = line.split("\"")[-4].strip()
                if promise_text != "前提id":
                    # 按第一个空格切一刀（Plan 31 §3.16）：分类里没有空格，描述里的空格原样保留；
                    #    此前按每个空格切、只取第二段，描述带出处括注（如「Plan 22 三期」）的会截断在「（Plan」
                    part_list = promise_text.split(" ", 1)
                    promise_type = part_list[0]
                    promise_info = part_list[1] if len(part_list) > 1 else ""
                    out_str += f"{promise_type},{promise_info}\n"
            else:
                # 常量行：先写前提id与常量名，分类与描述由下一行的 docstring 补齐
                promise_cid = line.split("\"")[-2].strip()
                promise_name = line.split(" =")[0].strip()
                out_str += f"{promise_cid},{promise_name},"
        elif len(line) == 1:
            out_str += "\n"
    return out_str


def constand_promise_2_csv():
    """
    前提文件转csv（mode 2）：读 constant_promise.py，重新生成 ArkEditor 的前提表
    Keyword arguments:
    无
    Return arguments:
    str -- 写入的前提表文本
    """
    with open(os.path.join("Script", "Core", "constant_promise.py"), "r", encoding="utf-8") as f:
        line_list = f.readlines()
    out_str = build_promise_csv_text(line_list)

    # 开始保存（文件名是 Premise.csv，大小写要写对：在区分大小写的系统上写成 premise.csv 会另建一个文件）
    with open(os.path.join("tools", "ArkEditor", "csv", "Premise.csv"), "w", encoding="utf-8") as f:
        f.write(out_str)
    print("已写入csv文件末尾")

    return out_str

def csv_2_constand():
    with open(os.path.join("tools", "csv", "premise.csv"), "r",encoding="utf-8") as f:
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
    with open(os.path.join("Script", "Core", "constant_promise.py"), "a",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入前提文件末尾")

    return out_str

def constand_effect_2_csv():
    with open(os.path.join("Script", "Core", "constant_effect.py"), "r",encoding="utf-8") as f:
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
    with open(os.path.join("tools", "ArkEditor", "csv", "Effect.csv"), "w",encoding="utf-8") as f:
        f.write(out_str)
        f.close()
    print(f"已写入csv文件末尾")

    return out_str

def csv_2_constand_effect():
    with open(os.path.join("tools", "csv", "Effect.csv"), "r",encoding="utf-8") as f:
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


    # 开始保存：插到 BehaviorEffect 类的末尾，类后面的内容原样保留。
    # 不能追加到文件末尾：文件最后一个类是 SecondEffect（二段结算），追加上去的行为结算常量会变成它的成员
    effect_path = os.path.join("Script", "Core", "constant_effect.py")
    with open(effect_path, "r", encoding="utf-8") as f:
        line_list = f.readlines()
    insert_index = class_end_index(line_list, "BehaviorEffect")
    line_list.insert(insert_index, out_str)
    with open(effect_path, "w", encoding="utf-8") as f:
        f.writelines(line_list)
    print(f"已写入结算文件 BehaviorEffect 类末尾")

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
