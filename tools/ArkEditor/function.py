from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFontMetrics, QFont
import cache_control, game_type
import json

font = QFont()
font.setPointSize(11)

def read_CVP(cvp_value_str: str):
    """读取CVP字符串 A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖"""
    cvp_str_list = cvp_value_str.split("_")
    # print(f"cvp_str_list = {cvp_str_list}")
    cvp_str_list[0] = cvp_str_list[0].replace("CVP", "综合数值前提  ")
    cvp_str_list[1] = cvp_str_list[1].replace("A1", "自己")
    cvp_str_list[1] = cvp_str_list[1].replace("A2", "交互对象")
    cvp_str_list[2] = cvp_str_list[2].replace("F", "好感")
    cvp_str_list[2] = cvp_str_list[2].replace("X", "信赖")
    cvp_str_list[2] = cvp_str_list[2].replace("G", "攻略程度")
    cvp_str_list[2] = cvp_str_list[2].replace("Time", "时间")
    cvp_str_list[3] = cvp_str_list[3].replace("G", "大于")
    cvp_str_list[3] = cvp_str_list[3].replace("L", "小于")
    cvp_str_list[3] = cvp_str_list[3].replace("E", "等于")
    cvp_str_list[3] = cvp_str_list[3].replace("GE", "大于等于")
    cvp_str_list[3] = cvp_str_list[3].replace("LE", "小于等于")
    cvp_str_list[3] = cvp_str_list[3].replace("NE", "不等于")
    # 将cvp_str_list转为str的cvp_str
    cvp_str = ""
    for i in cvp_str_list:
        cvp_str += i
    # print(f"debug cvp_str = {cvp_str}, cvp_str_list = {cvp_str_list}")
    # 处理A3部分
    if "A3" in cvp_str:
        a3_value = cvp_str.split("A3|")[1].split("_")[0]
        cvp_str = cvp_str.replace(f"A3|{a3_value}", f"角色id为{a3_value}")
    # 然后处理B属性部分
    if "A" in cvp_str:
        b2_value = cvp_str_list[2].split("A|")[1]
        b2_name = cache_control.ability_data[b2_value]
        cvp_str = cvp_str.replace(f"A|{b2_value}", f"能力{b2_name}")
    elif "T" in cvp_str:
        b2_value = cvp_str_list[2].split("T|")[1]
        b2_name = cache_control.talent_data[b2_value]
        cvp_str = cvp_str.replace(f"T|{b2_value}", f"素质{b2_name}")
    elif "J" in cvp_str:
        b2_value = cvp_str_list[2].split("J|")[1]
        b2_name = cache_control.juel_data[b2_value]
        cvp_str = cvp_str.replace(f"J|{b2_value}", f"宝珠{b2_name}")
    elif "E" in cvp_str:
        b2_value = cvp_str_list[2].split("E|")[1]
        b2_name = cache_control.experience_data[b2_value]
        cvp_str = cvp_str.replace(f"E|{b2_value}", f"经验{b2_name}")
    elif "S" in cvp_str:
        b2_value = cvp_str_list[2].split("S|")[1]
        b2_name = cache_control.state_data[b2_value]
        cvp_str = cvp_str.replace(f"S|{b2_value}", f"状态{b2_name}")
    # 最后去掉所有的下划线
    cvp_str = cvp_str.replace("_", "")
    return cvp_str


def save_data():
    """保存文件"""
    if len(cache_control.now_file_path):
        # 保存事件
        if cache_control.now_edit_type_flag == 1:
            with open(cache_control.now_file_path, "w", encoding="utf-8") as event_data_file:
                now_data = {}
                for k in cache_control.now_event_data:
                    now_data[k] = cache_control.now_event_data[k].__dict__
                json.dump(now_data, event_data_file, ensure_ascii=0)

        # 保存口上
        elif cache_control.now_edit_type_flag == 0:
            save_talk_data()



def save_talk_data():
    """保存口上文件"""
    if len(cache_control.now_file_path):
        # 通用开头
        out_data = ""
        out_data += "cid,behavior_id,adv_id,premise,context\n"
        out_data += "口上id,触发口上的行为id,口上限定的剧情npcid,前提id,口上内容\n"
        out_data += "str,int,int,str,str\n"
        out_data += "0,0,0,0,1\n"
        out_data += "口上配置数据,,,,\n"

        # 遍历数据
        for k in cache_control.now_talk_data:
            now_talk: game_type.Talk = cache_control.now_talk_data[k]
            out_data += f"{now_talk.cid},{now_talk.status_id},{now_talk.adv_id},"
            # 如果前提为空，就写入空白前提
            if len(now_talk.premise) == 0:
                out_data += "high_1"
            # 如果前提不为空，就正常写入，并在最后去掉多余的&
            else:
                for premise in now_talk.premise:
                    out_data += f"{premise}&"
                out_data = out_data[:-1]
            out_data += f",{now_talk.text}\n"

        # 写入文件
        with open(cache_control.now_file_path, "w",encoding="utf-8") as f:
            f.write(out_data)
            f.close()

def show_talk_introduce():
    """显示只读文本框的对话框"""
    dialog = QDialog()
    text_edit = QTextEdit(dialog)
    text_edit.setFont(font)
    text = "本编辑器可用于编辑游戏 erArk 的口上文件（即角色对话文件）。\n"
    text += "游戏的角色对话文件存放路径为：游戏根目录/data/talk/chara/\n\n"
    text += "流程简述：\n"
    text += "  ①创建/读取对应的文件。\n  ②在左侧的条目栏中新建/选择一个条目。\n  ③在左上选指令，在右上选前提，在右下写文本。\n  ④保存\n\n"
    text += "\nUI介绍：\n"
    text += "  ①左边，口上的条目列表。这里处理每条口上的序号、由什么指令触发、是否限定某角色触发。\n"
    text += "  ②右上，前提选择栏。这里处理口上的触发逻辑，使用【前提】的形式来实现代码的处理，同一口上的所有前提按逻辑“和”来运算。\n"
    text += "  ③右下，文本编辑框。这里处理口上的文本，包括人物名、地名之类代码文字。\n\n"
    text += "\n简单的口上逻辑：\n"
    text += "  绝大部分的情况下，都是【玩家】对【某数据的】【某NPC】使用【某指令】。\n"
    text += "  例，【玩家】对【1000好感以上的】【阿米娅】使用【聊天】时文本为【你好】。\n"
    text += "  此时，指令=[聊天]、角色id=[1]（阿米娅id）、前提=[玩家触发+交互对象好感＞1000]、文本内容=[你好]。\n\n"
    text += "\n常见问题：\n"
    text += "\n①笔记本的系统缩放设置导致编辑器的窗口或UI错误时，右键点击→属性→兼容性→更改高DPI设置→勾选替代高DPI缩放行为\n"
    text += "\n②前提之间是[逻辑和]关系，即一个条目中有两条前提AB时，是既要满足A又要满足B。\n   目前因为技术问题，暂时无法直接实现其他的逻辑关系。比如若想实现[逻辑或]，即满足前提A或满足前提B，则只能建立两条不同的条目，分别为前提A和前提B。\n"
    text += "\n\n\n（如果你真的需要理解的话，再来看下面这段）\n\n详细的口上逻辑：\n"
    text += "  ①在玩家/NPC使用一个指令时，会搜寻【本角色和通用角色的】【本指令下的】所有口上（如果是对他人使用，则还会搜索【对象角色的】），这里将搜到的所有口上定义为A。\n"
    text += "  ②遍历A里每个口上的前提，查看是否满足条件。如果某一条口上的所有前提都被满足，则根据前提量计一个权重大小，该口上进入选择池。这里将选择池里的所有口上定义为B，显然，B是A的一个子集。\n"
    text += "  ③在B中根据权重比例来随机选择一个口上作为当前的结果口上，假如B中有3个口上，权重分别为2,1,1，那么随机到这三个口上的概率分别为1/2，1/4，1/4。\n\n"
    text_edit.setText(text)
    text_edit.setReadOnly(True)
    text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
    font_metrics = QFontMetrics(text_edit.font())
    text_edit.setFixedWidth(1000)
    line_count = text.count('\n') + 1
    text_edit.setFixedHeight(font_metrics.lineSpacing() * line_count * 1.5)

    layout = QVBoxLayout(dialog)
    layout.addWidget(text_edit)
    dialog.exec_()


def show_event_introduce():
    """显示只读文本框的对话框"""
    dialog = QDialog()
    text_edit = QTextEdit(dialog)
    text_edit.setFont(font)
    text = "本编辑器可用于编辑游戏 erArk 的事件文件。\n"
    text += "游戏的事件文件存放路径为：游戏根目录/data/event/\n\n"
    text += "事件的本质就是带结算的口上，请先阅读并理解口上的部分后，再来看本部分\n"
    text += "事件的触发方式：\n"
    text += "  事件的触发优先于指令的触发，由事件决定是否要触发指令下的口上输出与数值结算。\n"
    text += "  ①跳过指令，适用于大部分情况。比如写一个玩家和NPC吃饭的事件，那么玩家点击吃饭后，应当只发生事件的吃饭，只出现事件的文本和数值结算，不应再出现指令原本的口上文本和结算。所以在这种事件类型里，应当把指令本身的相关处理全部跳过。\n"
    text += "  ②指令前置，通常适用于移动触发的事件。比如写一个玩家或NPC进入房间的事件，那么此时应当先结算指令，让人物先移动过去，然后再触发事件。这种事件如果把指令跳过了，那就变成在房间外面触发了房间内的事件了，显然是不合理的。\n"
    text += "  ③指令后置，同理，先触发事件，再结算指令。\n\n"
    text += "带选项的父子事件：\n"
    text += "  带分支选项的事件被称为父子事件。选项之前的为一个单独的父事件，每个选项各自为一个单独的子事件。父子事件的构成需要满足以下三个条件：\n"
    text += "  ①父事件的结算中需要有一个[系统状态]里的【开启子选项面板】。\n"
    text += "  ②子事件的前提需要在和父事件一样的基础上，再额外加一个[系统状态]里的【选项的子事件】。\n"
    text += "  ③子事件的文本分为两个部分，分别是选项上显示的文本，以及点击选项之后出来的文本。这两个文本都写在子事件的文本里，中间用|分隔开。\n"
    text_edit.setText(text)
    text_edit.setReadOnly(True)
    text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
    font_metrics = QFontMetrics(text_edit.font())
    text_edit.setFixedWidth(1000)
    line_count = text.count('\n') + 1
    text_edit.setFixedHeight(font_metrics.lineSpacing() * line_count * 1.5)

    layout = QVBoxLayout(dialog)
    layout.addWidget(text_edit)
    dialog.exec_()


def show_chara_introduce():
    """显示只读文本框的对话框"""
    dialog = QDialog()
    text_edit = QTextEdit(dialog)
    text_edit.setFont(font)
    text = "本编辑器可用于编辑游戏 erArk 的角色属性文件。\n"
    text += "游戏的角色属性文件存放路径为：游戏根目录/data/character/\n\n"
    text += "角色属性文件的结构：\n"
    text += "  角色属性文件是一个csv文件，里面包含了该角色的初始属性。\n"
    text += "  文件的结构是一个字典，字典的键是各属性，字典的值是各属性的值。\n\n"
    text += "  选择【新建角色属性文件】时，会自动读取编辑器目录下的模板人物属性文件，编辑完毕并保存时会在该目录下生成一个新的角色文件。\n"
    text += "  选择【读取角色属性文件】时，需要手动指定路径，保存时会覆盖原文件。\n"
    text_edit.setText(text)
    text_edit.setReadOnly(True)
    text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    font_metrics = QFontMetrics(text_edit.font())
    text_edit.setFixedWidth(1000)
    line_count = text.count('\n') + 1
    text_edit.setFixedHeight(font_metrics.lineSpacing() * line_count * 1.5)

    layout = QVBoxLayout(dialog)
    layout.addWidget(text_edit)
    dialog.exec_()
