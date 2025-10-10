from typing import Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.Design import basement,character_handle, handle_premise, attr_calculation, clothing, map_handle
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
import os
import json
import csv

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def build_csv_config(file_path: str, file_name: str, chara_adv_id: int, character_talk_data: dict):
    """
    输入：
        file_path (str): 文件路径
        file_name (str): 文件名
        talk (bool): 是否为talk
        target (bool): 是否为target
    返回：None
    功能：读取csv并更新全局配置数据
    """
    # print(f"debug file_path = {file_path}")
    with open(file_path, encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        now_docstring_data = {}
        now_type_data = {}
        get_text_data = {}
        file_id = file_name.split(".")[0]
        path_list = file_path.split(os.sep)
        file_id = path_list[-2] + "_" + file_id
        i = 0
        class_text = ""
        type_text = file_id
        type_text = "Talk"
        if "premise" in file_name:
            type_text = "TalkPremise"
        character_talk_data.setdefault(type_text, {})
        character_talk_data[type_text].setdefault("data", [])
        character_talk_data[type_text].setdefault("gettext", {})
        for row in now_read:
            # 获得当前的行数
            now_index = now_read.line_num
            if not i:
                for k in row:
                    now_docstring_data[k] = row[k]
                i += 1
                continue
            elif i == 1:
                for k in row:
                    now_type_data[k] = row[k]
                i += 1
                continue
            elif i == 2:
                for k in row:
                    get_text_data[k] = int(row[k])
                i += 1
                continue
            elif i == 3:
                class_text = list(row.values())[0]
                i += 1
                continue
            # 跳过非指定角色的行
            if int(row["adv_id"]) != chara_adv_id:
                continue
            for k in now_type_data:
                now_type = now_type_data[k]
                # print(f"debug row = {row}")
                if not len(row[k]):
                    del row[k]
                    continue
                if now_type == "int":
                    row[k] = int(row[k])
                elif now_type == "str":
                    row[k] = str(row[k]).replace('"','\\"') # 转义引号防止造成po文件混乱
                elif now_type == "bool":
                    row[k] = int(row[k])
                elif now_type == "float":
                    row[k] = float(row[k])
                if k == "cid":
                    # if "-" in file_id:
                    #     print(f"debug file_id = {file_id}")
                    row[k] = file_id + row[k]
            # 设置版本号，默认为1
            row["version"] = 1
            # 如果口上的文件名中存在下划线标记的版本号，则将最后一个下划线之后的数字记录为版本号
            if int(row["adv_id"]) != 0 and file_id.count("_") == 3:
                # print(f"debug file_id = {file_id}")
                row["version"] = int(file_id.rsplit("_", 1)[-1])
            # 记录口上数据
            character_talk_data[type_text]["data"].append(row)
        get_text_data["version"] = 0
        character_talk_data[type_text]["gettext"] = get_text_data

def build_chara_talk(chara_adv_id : int = 0):
    """"
    "构建角色对话数据"
    """
    talk_dir = os.path.join("data", "talk")
    character_talk_data_path = os.path.join("data", "Character_Talk.json")
    # 在开始时读取 JSON，若读取失败则用空对象
    try:
        if chara_adv_id == 0:
            character_talk_data = {}
        else:
            with open(character_talk_data_path, "r", encoding="utf-8") as f:
                character_talk_data = json.load(f)
            # 如果指定了特定角色，则将该角色重置
            for key in character_talk_data["Talk"]["data"].copy():
                if key["adv_id"] == chara_adv_id:
                    character_talk_data["Talk"]["data"].remove(key)
    except:
        character_talk_data = {}

    talk_file_list = os.listdir(talk_dir)
    # 遍历 talk 文件夹下的所有文件和子目录
    for i in talk_file_list:
        # 跳过 ai 文件夹
        if i == "ai":
            continue
        now_dir = os.path.join(talk_dir, i)
        # 判断当前路径是否为目录
        if os.path.isdir(now_dir):
            # 如果是目录，则递归遍历子目录
            for root, dirs, files in os.walk(now_dir):
                for f in files:
                    now_f = os.path.join(root, f)
                    build_csv_config(now_f, f, chara_adv_id, character_talk_data)
        else:
            # 如果不是目录，直接处理文件
            build_csv_config(now_dir, i, chara_adv_id, character_talk_data)
    # 写入 talk 数据
    with open(character_talk_data_path, "w", encoding="utf-8") as talk_data_file:
        json.dump(character_talk_data, talk_data_file, ensure_ascii=0)


class TALK_QUICK_TEST:
    """
    用于快速测试口上的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("快速测试口上")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("快速测试口上")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        from Script.Design import talk

        while 1:
            return_list = []
            title_draw.draw()
            info_draw = draw.NormalDraw()
            info_draw.width = self.width

            info_text = _("本功能用于快速测试当前数据情况下，指定角色的指定id口上的触发情况，包括触发者与交互对象、是否能够触发、每个前提是否满足、最终输出文本等\n\n")
            info_text += _("刷新口上文件，用于在不重启游戏的情况，重新刷新并读取发生了变更的口上文件。即可以在编辑器中写完新的条目、保存，然后在游戏中点击该刷新按钮，读取刚写好的条目并进行测试\n\n\n")
            info_draw.text = info_text
            info_draw.draw()

            button_text = _("[001]刷新口上文件后测试")
            button1_draw = draw.LeftButton(button_text, button_text, len(button_text)*2, cmd_func=self.refresh_talk_file)
            button1_draw.draw()
            return_list.append(button1_draw.return_text)
            line_feed.draw()

            button_text = _("[002]直接开始测试")
            button2_draw = draw.LeftButton(button_text, button_text, len(button_text)*2, cmd_func=self.nothing)
            button2_draw.draw()
            return_list.append(button2_draw.return_text)
            line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width / 4)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                return
            elif yrn == button1_draw.return_text or yrn == button2_draw.return_text:
                break

        while 1:
            py_cmd.clr_cmd()
            return_list = []
            line = draw.LineDraw("-", window_width)
            line.draw()
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n\n测试开始\n\n")
            info_draw.draw()
            # 获取角色id
            change_value_panel = panel.AskForOneMessage()
            change_value_panel.set(_("请输入角色id"), 100)
            chara_adv_id = int(change_value_panel.draw())
            pl_character_data = cache.character_data[0]
            target_chara_id = 0
            for tem_chara_id in cache.character_data:
                tem_character_data = cache.character_data[tem_chara_id]
                if tem_character_data.adv == chara_adv_id:
                    target_chara_id = tem_chara_id
                    break
            target_character_data = cache.character_data[target_chara_id]
            line_feed.draw()
            # 获取口上id
            change_value_panel = panel.AskForOneMessage()
            change_value_panel.set(_("请输入口上id"), 100)
            talk_id = int(change_value_panel.draw())
            # 在chara_adv_id在前面补零为4位数
            full_adv_id = str(chara_adv_id).rjust(4, '0')
            chara_name = target_character_data.name
            full_talk_id = f"chara_{full_adv_id}_{chara_name}{talk_id}"
            # 获取口上数据
            find_talk_flag = False
            if full_talk_id in game_config.config_talk:
                find_talk_flag = True

            # 开始打印测试结果
            line_feed.draw()
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            draw_text = "\n"
            if target_chara_id == 0:
                draw_text += _("未找到该角色，请确认是否输入正确\n")
            elif not find_talk_flag:
                draw_text += _("未找到该口上，请确认是否输入正确\n")
            else:
                pass_flag = True
                # 输出角色信息
                draw_text += _("测试角色：{0}\n").format(target_character_data.name)
                # 是否已获得该角色
                if target_chara_id not in cache.npc_id_got:
                    draw_text += _("  博士未获得该角色(X)\n")
                    pass_flag = False
                else:
                    draw_text += _("  博士已获得该角色(√)\n")
                # 当前交互对象是否是该角色
                if pl_character_data.target_character_id != target_chara_id:
                    draw_text += _("  博士当前交互对象不是该角色(X)\n")
                    pass_flag = False
                else:
                    draw_text += _("  博士当前交互对象是该角色(√)\n")
                # 指令状态
                now_behavior_id = game_config.config_talk[full_talk_id].behavior_id
                draw_text += _("\n指令状态：{0}\n").format(game_config.config_behavior[now_behavior_id].name)
                # 判断触发人与交互对象
                draw_text += _("\n触发人与交互对象：\n")
                if "sys_0" in game_config.config_talk_premise_data[full_talk_id]:
                    draw_text += _("  触发人：博士\n")
                    start_chara_id = 0
                elif "sys_1" in game_config.config_talk_premise_data[full_talk_id]:
                    draw_text += _("  触发人：NPC\n")
                    start_chara_id = target_chara_id
                else:
                    if game_config.config_behavior[now_behavior_id].trigger == "npc":
                        draw_text += _("  触发人：未填写，本测试中默认选择为NPC\n")
                        start_chara_id = target_chara_id
                    else:
                        draw_text += _("  触发人：未填写，本测试中默认选择为博士\n")
                        start_chara_id = 0
                if "二段结算" in game_config.config_behavior[now_behavior_id].tag:
                    draw_text += _("  交互对象：同触发人，二段结算的交互对象只能是触发人自己\n")
                    end_chara_id = start_chara_id
                elif "sys_4" in game_config.config_talk_premise_data[full_talk_id]:
                    draw_text += _("  交互对象：博士\n")
                    end_chara_id = 0
                elif "sys_5" in game_config.config_talk_premise_data[full_talk_id]:
                    draw_text += _("  交互对象：NPC\n")
                    end_chara_id = target_chara_id
                else:
                    if start_chara_id == 0:
                        draw_text += _("  交互对象：未填写，本测试中默认选择为NPC\n")
                        end_chara_id = target_chara_id
                    else:
                        draw_text += _("  交互对象：未填写，本测试中默认选择为博士\n")
                        end_chara_id = 0
                # 设置交互对象
                cache.character_data[start_chara_id].target_character_id = end_chara_id

                # 输出口上文本
                talk_context = game_config.config_talk[full_talk_id].context
                draw_text += _("\n口上原文本：\n  {0}\n").format(talk_context)
                draw_text += _("口上输出文本：\n  {0}\n").format(talk.code_text_to_draw_text(talk_context, start_chara_id))
                # 遍历前提条件
                draw_text += _("\n前提条件：\n")
                for premise in game_config.config_talk_premise_data[full_talk_id]:
                    # 综合数值前提判定
                    if "CVP" in premise:
                        premise_all_value_list = premise.split("_")[1:]
                        now_add_weight = handle_premise.handle_comprehensive_value_premise(start_chara_id, premise_all_value_list)
                    # 其他正常口上判定
                    else:
                        now_add_weight = constant.handle_premise_data[premise](start_chara_id)
                    if now_add_weight:
                        draw_text += _("  {0}：满足(√)\n").format(premise)
                    else:
                        draw_text += _("  {0}：不满足(X)\n").format(premise)
                        pass_flag = False

                # 输出测试结果
                if pass_flag:
                    draw_text += _("\n最终结果：\n  测试通过，该口上可以触发\n")
                else:
                    draw_text += _("\n最终结果：\n  测试未通过，该口上无法触发\n")
            now_draw = draw.WaitDraw()
            now_draw.text = draw_text
            now_draw.draw()


            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


    def refresh_talk_file(self):
        """刷新口上文件"""

        # 要求输入角色的id
        change_value_panel = panel.AskForOneMessage()
        change_value_panel.set(_("请输入角色id"), 100)
        chara_adv_id = int(change_value_panel.draw())

        line = draw.LineDraw("-", window_width)
        line.draw()
        now_draw = draw.NormalDraw()
        draw_text = _("\n\n开始刷新口上文件，请稍等\n")
        now_draw.text = draw_text
        now_draw.draw()
        for i in range(5):
            line_feed.draw()

        # 构建角色口上数据
        build_chara_talk(chara_adv_id)

        # 旧的口上数据计数
        all_count_old = 0
        for i in game_config.config_talk_data:
            all_count_old += len(game_config.config_talk_data[i])

        game_config.reload_talk_data()

        # 新的口上数据计数
        all_count_new = 0
        for i in game_config.config_talk_data:
            all_count_new += len(game_config.config_talk_data[i])

        now_draw = draw.WaitDraw()
        draw_text = _("\n口上文件刷新完毕\n")
        draw_text += _("原数据总数为{0}，新数据总数为{1}，新增数据总数为{2}\n\n").format(all_count_old, all_count_new, all_count_new - all_count_old)
        now_draw.text = draw_text
        now_draw.draw()

    def nothing(self):
        pass



class Debug_Panel:
    """
    用于显示debug界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("常用更改")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "debug面板"
        department_type_list = [_("常用更改"),_("全局变量"),_("NPC角色")]

        title_draw = draw.TitleLineDraw(title_text, self.width)

        # 进行一轮刷新
        basement.update_work_people()
        basement.update_facility_people()

        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for department_type in department_type_list:
                if department_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{department_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(department_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{department_type}]",
                        f"\n{department_type}",
                        self.width / len(department_type_list),
                        cmd_func=self.change_panel,
                        args=(department_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # facility_draw = draw.NormalDraw()
            # facility_text = "\n当前设施情况："
            # facility_draw.text = facility_text
            # facility_draw.width = self.width
            # facility_draw.draw()

            now_draw = panel.LeftDrawTextListPanel()

            # 全局变量
            if self.now_panel == _("全局变量"):

                all_info_draw = draw.NormalDraw()
                all_info_text = _("全局变量一览：")
                all_info_draw.text = all_info_text
                all_info_draw.width = self.width
                now_draw.draw_list.append(all_info_draw)
                now_draw.width += len(all_info_draw.text)

                now_draw.draw_list.append(line_feed)
                now_draw.width += line_feed.width

                # 要输出的变量名称以及注释
                draw_text_list = []
                draw_text_list.append(f"[000]:游戏时间：{cache.game_time}")
                draw_text_list.append(f"[001]:已拥有的干员id列表：{cache.npc_id_got}")
                draw_text_list.append(f"[002]:全干员id列表（太长了无法显示）")
                draw_text_list.append(f"[003]:龙门币：{cache.rhodes_island.materials_resouce[1]}")
                draw_text_list.append(f"[004]:合成玉：{cache.rhodes_island.materials_resouce[2]}")
                draw_text_list.append(f"[005]:粉红凭证：{cache.rhodes_island.materials_resouce[4]}")
                draw_text_list.append(f"[006]:基地当前所有待开放设施的开放情况")
                draw_text_list.append(f"[007]:一周内的派对计划，周一0~周日6:娱乐id：{cache.rhodes_island.party_day_of_week}")
                draw_text_list.append(f"[008]:当前招募进度：{cache.rhodes_island.recruit_line}")
                draw_text_list.append(f"[009]:已招募待确认的干员id：{cache.rhodes_island.recruited_id}")

                for i in range(len(draw_text_list)):

                    button_draw = draw.LeftButton(
                        draw_text_list[i],
                        f"\n{i}",
                        self.width ,
                        cmd_func=self.change_value,
                        args=i
                    )
                    now_draw.draw_list.append(button_draw)
                    now_draw.width += len(button_draw.text)
                    now_draw.draw_list.append(line_feed)
                    return_list.append(button_draw.return_text)

            elif self.now_panel == _("常用更改"):

                all_info_draw = draw.NormalDraw()
                all_info_text = _("！！！特别注意事项！！！\n！debug前请一定要进行存档备份，不正确和过大的数值修改可能会出现数据超限、跳过中间值结算、数据类型错误和长度错误等问题\n！这些问题会导致游戏的部分结算和功能无法运行和使用，进而坏档\n！总之请一定要进行存档备份，存档数据很珍贵的，坏档了就太痛了\n！！！特别注意事项！！！\n\n")
                all_info_text += _("玩家的各项属性")
                all_info_draw.text = all_info_text
                all_info_draw.width = self.width
                now_draw.draw_list.append(all_info_draw)
                now_draw.width += len(all_info_draw.text)

                now_draw.draw_list.append(line_feed)
                now_draw.width += line_feed.width

                # 要输出的变量名称以及注释
                draw_text_list = []
                draw_text_list.append(f"[000]:当前HP：{cache.character_data[0].hit_point}")
                draw_text_list.append(f"[001]:最大HP：{cache.character_data[0].hit_point_max}")
                draw_text_list.append(f"[002]:当前MP：{cache.character_data[0].mana_point}")
                draw_text_list.append(f"[003]:最大MP：{cache.character_data[0].mana_point_max}")
                draw_text_list.append(f"[004]:当前射精槽：{cache.character_data[0].eja_point}")
                draw_text_list.append(f"[005]:疲劳值 6m=1点，16h=160点(max)：{cache.character_data[0].tired_point}")
                draw_text_list.append(f"[006]:尿意值 1m=1点，4h=240点(max)：{cache.character_data[0].urinate_point}")
                draw_text_list.append(f"[007]:饥饿值 1m=1点，4h=240点(max)：{cache.character_data[0].hunger_point}")
                draw_text_list.append(f"[008]:全源石技艺全开，理智9999")
                draw_text_list.append(f"[009]:资源全99999")
                draw_text_list.append(f"[010]:设施全满级、全开放")
                draw_text_list.append(f"[011]:重置全角色特殊flag")
                draw_text_list.append(f"[012]:重置全角色服装")
                draw_text_list.append(f"[013]:重置全角色位置至宿舍")
                draw_text_list.append(f"[014]:重置文职部的招募数据")
                draw_text_list.append(f"[015]:交互对象全部位快感增加")
                draw_text_list.append(f"[016]:招募指定adv_id的干员")
                draw_text_list.append(f"[017]:重置全角色娱乐")


                for i in range(len(draw_text_list)):

                    button_draw = draw.LeftButton(
                        draw_text_list[i],
                        f"\n{i}",
                        self.width ,
                        cmd_func=self.change_value,
                        args=i
                    )
                    now_draw.draw_list.append(button_draw)
                    now_draw.width += len(button_draw.text)
                    now_draw.draw_list.append(line_feed)
                    return_list.append(button_draw.return_text)

            elif self.now_panel == _("NPC角色"):

                all_info_draw = draw.NormalDraw()
                all_info_text = "选择角色："
                all_info_draw.text = all_info_text
                all_info_draw.width = self.width
                now_draw.draw_list.append(all_info_draw)
                now_draw.width += len(all_info_draw.text)

                now_draw.draw_list.append(line_feed)
                now_draw.width += line_feed.width

                id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
                id_list.append(0)
                npc_count = 0

                for NPC_id in id_list:
                    # if NPC_id not in cache.character_data:
                    #     continue
                    target_data: game_type.Character = cache.character_data[NPC_id]
                    button_text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}"

                    button_draw = draw.LeftButton(
                        button_text,
                        f"\n{NPC_id}",
                        self.width/6 ,
                        cmd_func=self.change_target_character,
                        args=NPC_id
                    )
                    now_draw.draw_list.append(button_draw)
                    now_draw.width += len(button_draw.text)
                    return_list.append(button_draw.return_text)
                    npc_count += 1
                    if npc_count % 6 == 0:
                        now_draw.draw_list.append(line_feed)
                now_draw.draw_list.append(line_feed)


            self.draw_list: List[draw.NormalDraw] = []
            """ 绘制的文本列表 """
            self.draw_list.extend(now_draw.draw_list)

            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, department_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        department_type -- 要切换的面板类型
        """

        self.now_panel = department_type


    def change_target_character(self,NPC_id):
        """
        选择目标角色
        """
        self.target_character_id = NPC_id

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            return_list = []
            now_draw = panel.LeftDrawTextListPanel()

            target_data: game_type.Character = cache.character_data[self.target_character_id]
            info_text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}\n\n"
            info_draw.text = info_text
            info_draw.draw()

            # 要输出的变量名称以及注释
            draw_text_list = []
            draw_text_list.append(f"[000]:基础属性（已实装）")
            draw_text_list.append(f"[001]:道具")
            draw_text_list.append(f"[002]:衣服")
            draw_text_list.append(f"[003]:当前行为状态")
            draw_text_list.append(f"[004]:当前二段行为状态（已实装）")
            draw_text_list.append(f"[005]:当前事件状态")
            draw_text_list.append(f"[006]:状态（已实装）")
            draw_text_list.append(f"[007]:能力（已实装）")
            draw_text_list.append(f"[008]:经验（已实装）")
            draw_text_list.append(f"[009]:宝珠（已实装）")
            draw_text_list.append(f"[010]:素质（已实装）")
            draw_text_list.append(f"[011]:初次状态记录")
            draw_text_list.append(f"[012]:污浊（已实装）")
            draw_text_list.append(f"[013]:本次H（已实装）")
            draw_text_list.append(f"[014]:助理情况（已实装）")
            draw_text_list.append(f"[015]:行动记录")
            draw_text_list.append(f"[016]:工作")
            draw_text_list.append(f"[017]:娱乐（已实装）")
            draw_text_list.append(f"[018]:怀孕（已实装）")
            draw_text_list.append(f"[019]:社会关系（已实装）")
            draw_text_list.append(f"[020]:特殊flag（已实装）")
            draw_text_list.append(f"[021]:催眠（已实装）")


            for i in range(len(draw_text_list)):

                button_draw = draw.LeftButton(
                    draw_text_list[i],
                    f"\n{i}",
                    self.width ,
                    cmd_func=self.change_target_value,
                    args=i
                )
                now_draw.draw_list.append(button_draw)
                now_draw.width += len(button_draw.text)
                now_draw.draw_list.append(line_feed)
                return_list.append(button_draw.return_text)

            self.draw_list: List[draw.NormalDraw] = []
            """ 绘制的文本列表 """
            self.draw_list.extend(now_draw.draw_list)

            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


    def change_value(self,key_index):
        """
        调整该变量的值
        """

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            return_list = []


            if self.now_panel == "全局变量":
                if key_index == 0:
                    info_text = f"[000]:游戏时间：{cache.game_time}      年月日分别为0,1,2"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()

                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    # print(f"debug value_index = {value_index},new_value = {new_value}")

                    # 根据第几项更改对应值
                    if len(value_index) == 1:
                        info_draw.text = "\n输出格式错误，请重试\n"
                        info_draw.draw()
                        continue
                    if value_index[1] == 0:
                        cache.game_time = cache.game_time.replace(year = new_value)
                    elif value_index[1] == 1:
                        cache.game_time = cache.game_time.replace(month = new_value)
                    elif value_index[1] == 2:
                        cache.game_time = cache.game_time.replace(day = new_value)


                elif key_index == 1:
                    info_text = f"[001]:已拥有的干员id列表：\n"
                    for chara_id in cache.npc_id_got:
                        name = cache.character_data[chara_id].name
                        info_text += f"{chara_id}:{name} "
                    info_text += f"\n\n全干员id列表：\n"
                    for i in range(len(cache.npc_tem_data)):
                        chara_id = i + 1
                        name = cache.character_data[chara_id].name
                        info_text += f"{chara_id}:{name} "
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    line_feed.draw()

                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入要改变第几号角色，以及这一项变成0或者1，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    if len(value_index) == 1:
                        info_draw.text = "\n输出格式错误，请重试\n"
                        info_draw.draw()
                        continue
                    elif value_index[1] == 0:
                        cache.npc_id_got.discard(value_index[0])
                    elif value_index[1] == 1:
                        character_handle.get_new_character(value_index[0])
                elif key_index == 3:
                    info_text = f"[003]:龙门币：{cache.rhodes_island.materials_resouce[1]}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.rhodes_island.materials_resouce[1] = new_value
                elif key_index == 4:
                    info_text = f"[004]:合成玉：{cache.rhodes_island.materials_resouce[2]}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.rhodes_island.materials_resouce[2] = new_value
                elif key_index == 5:
                    info_text = f"[005]:粉红凭证：{cache.rhodes_island.materials_resouce[4]}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.rhodes_island.materials_resouce[4] = new_value
                elif key_index == 6:
                    info_text = f"[006]:基地当前所有待开放设施的开放情况"
                    info_text += f"{cache.rhodes_island.facility_open}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    # cache.base_resouce.materials_resouce[1] = new_value
                elif key_index == 7:
                    info_text = f"[007]:一周内的派对计划，周一0~周日6:娱乐id：{cache.rhodes_island.party_day_of_week}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.rhodes_island.party_day_of_week = new_value
                elif key_index == 8:
                    info_text = f"[008]:当前招募进度：{cache.rhodes_island.recruit_line}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.rhodes_island.recruit_line = new_value
                elif key_index == 9:
                    info_text = f"[009]:已招募待确认的干员id：{cache.rhodes_island.recruited_id}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.rhodes_island.recruited_id = new_value

            elif self.now_panel == "常用更改":

                # 当前HP
                if key_index == 0:
                    info_text = f"[000]:当前HP：{cache.character_data[0].hit_point}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].hit_point = new_value
                # 最大HP
                elif key_index == 1:
                    info_text = f"[001]:最大HP：{cache.character_data[0].hit_point_max}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].hit_point_max = new_value
                # 当前MP
                elif key_index == 2:
                    info_text = f"[002]:当前MP：{cache.character_data[0].mana_point}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].mana_point = new_value
                # 最大MP
                elif key_index == 3:
                    info_text = f"[003]:最大MP：{cache.character_data[0].mana_point_max}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].mana_point_max = new_value
                # 当前射精槽
                elif key_index == 4:
                    info_text = f"[004]:当前射精槽：{cache.character_data[0].eja_point}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].eja_point = new_value
                # 疲劳值
                elif key_index == 5:
                    info_text = f"[005]:疲劳值 6m=1点，16h=160点(max)：{cache.character_data[0].tired_point}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].tired_point = new_value
                # 尿意值
                elif key_index == 6:
                    info_text = f"[006]:尿意值 1m=1点，4h=240点(max)：{cache.character_data[0].urinate_point}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].urinate_point = new_value
                # 饥饿值
                elif key_index == 7:
                    info_text = f"[007]:饥饿值 1m=1点，4h=240点(max)：{cache.character_data[0].hunger_point}"
                    info_draw.text = info_text
                    info_draw.draw()
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    cache.character_data[0].hunger_point = new_value
                # 全源石技艺全开，理智9999
                elif key_index == 8:
                    for talent_id in {304,305,306,307,308,309,310,311,312,316,317,318,331,332,333,334}:
                        cache.character_data[0].talent[talent_id] = 1
                        cache.character_data[0].sanity_point = 9999
                        cache.character_data[0].sanity_point_max = 9999
                # 资源全99999
                elif key_index == 9:
                    for material_id in cache.rhodes_island.materials_resouce:
                        cache.rhodes_island.materials_resouce[material_id] = 99999
                # 设施全满级、全开放
                elif key_index == 10:
                    for all_cid in cache.rhodes_island.facility_level:
                        cache.rhodes_island.facility_level[all_cid] = 5
                        for cid in cache.rhodes_island.facility_open:
                            cache.rhodes_island.facility_open[cid] = 1
                        basement.get_base_updata()
                # 重置全角色特殊flag
                elif key_index == 11:
                    cache.npc_id_got.discard(0)
                    for chara_id in cache.npc_id_got:
                        character_data = cache.character_data[chara_id]
                        character_data.sp_flag = game_type.SPECIAL_FLAG()
                # 重置全角色服装
                elif key_index == 12:
                    cache.npc_id_got.discard(0)
                    for chara_id in cache.npc_id_got:
                        clothing.get_npc_cloth(chara_id)
                # 重置全角色位置至宿舍
                elif key_index == 13:
                    cache.npc_id_got.discard(0)
                    for chara_id in cache.npc_id_got:
                        character_data = cache.character_data[chara_id]
                        # 将字符串中的"01区"替换为"1区"
                        character_data.dormitory = character_data.dormitory.replace("01区","1区")
                        character_data.position = map_handle.get_map_system_path_for_str(character_data.dormitory)
                # 重置文职部的招募数据
                elif key_index == 14:
                    for i in range(len(cache.rhodes_island.recruit_line)):
                        cache.rhodes_island.recruit_line[i] = [0,0,0,0]
                    cache.rhodes_island.recruited_id = set()
                # 交互对象全部位快感增加
                elif key_index == 15:
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    target_id = cache.character_data[0].target_character_id
                    target_character_data = cache.character_data[target_id]
                    for state_id in game_config.config_character_state:
                        if game_config.config_character_state[state_id].type == 0:
                            target_character_data.status_data[state_id] += new_value
                # 招募指定adv_id的干员
                elif key_index == 16:
                    from Script.Design import character
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入adv_id"), 100)
                    new_value = int(change_value_panel.draw())
                    character_id = character.get_character_id_from_adv(new_value)
                    if character_id not in cache.npc_id_got:
                        cache.rhodes_island.recruited_id.add(character_id)
                        info_draw.text = _("\n招募成功\n")
                    else:
                        info_draw.text = _("\n已招募过\n")
                    info_draw.draw()
                    line_feed.draw()
                # 重置全角色娱乐
                elif key_index == 17:
                    from Script.Design import handle_npc_ai
                    cache.npc_id_got.discard(0)
                    for chara_id in cache.npc_id_got:
                        handle_npc_ai.get_chara_entertainment(chara_id)

            line_feed.draw()
            # back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            # back_draw.draw()
            # line_feed.draw()
            # return_list.append(back_draw.return_text)
            # yrn = flow_handle.askfor_all(return_list)
            # if yrn == back_draw.return_text:
            #     break
            break


    def change_target_value(self,key_index):
        """
        调整目标角色变量的值
        """

        change_draw_flag = True

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()

            target_data: game_type.Character = cache.character_data[self.target_character_id]
            name_draw,info_draw = draw.NormalDraw(),draw.NormalDraw()
            name_draw.text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}\n\n"
            name_draw.width = self.width
            name_draw.draw()
            return_list = []

            # 基础属性
            if key_index == 0:
                draw_text_list = []
                draw_text_list.append(f"[000]:当前HP：{target_data.hit_point}")
                draw_text_list.append(f"[001]:最大HP：{target_data.hit_point_max}")
                draw_text_list.append(f"[002]:当前MP：{target_data.mana_point}")
                draw_text_list.append(f"[003]:最大MP：{target_data.mana_point_max}")
                draw_text_list.append(f"[004]:当前理智：{target_data.sanity_point}")
                draw_text_list.append(f"[005]:最大理智：{target_data.sanity_point_max}")
                draw_text_list.append(f"[011]:疲劳值 6m=1点，16h=160点(max)：{target_data.tired_point}")
                draw_text_list.append(f"[012]:尿意值 1m=1点，4h=240点(max)：{target_data.urinate_point}")
                draw_text_list.append(f"[013]:饥饿值 1m=1点，4h=240点(max)：{target_data.hunger_point}")
                draw_text_list.append(f"[014]:熟睡值 1m=10点，10min=100点(max)：{target_data.sleep_point}")
                draw_text_list.append(f"[015]:愤怒槽：{target_data.angry_point}")
                draw_text_list.append(f"[016]:射精槽：{target_data.eja_point}")
                draw_text_list.append(f"[017]:对玩家的好感度：{target_data.favorability[0]}")
                draw_text_list.append(f"[018]:信赖度：{target_data.trust}")
                draw_text_list.append(f"[019]:乳汁量：{target_data.pregnancy.milk}")
                draw_text_list.append(f"[020]:乳汁上限：{target_data.pregnancy.milk_max}")
                draw_text_list.append(f"[021]:欲望值：{target_data.desire_point}")
                draw_text_list.append(f"[022]:精液值：{target_data.semen_point}")
                draw_text_list.append(f"[023]:精液值上限：{target_data.semen_point_max}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    if value_index == 0:
                        target_data.hit_point = new_value
                    elif value_index == 1:
                        target_data.hit_point_max = new_value
                    elif value_index == 2:
                        target_data.mana_point = new_value
                    elif value_index == 3:
                        target_data.mana_point_max = new_value
                    elif value_index == 4:
                        target_data.sanity_point = new_value
                    elif value_index == 5:
                        target_data.sanity_point_max = new_value
                    elif value_index == 11:
                        target_data.tired_point = new_value
                    elif value_index == 12:
                        target_data.urinate_point = new_value
                    elif value_index == 13:
                        target_data.hunger_point = new_value
                    elif value_index == 14:
                        target_data.sleep_point = new_value
                    elif value_index == 15:
                        target_data.angry_point = new_value
                    elif value_index == 16:
                        target_data.eja_point = new_value
                    elif value_index == 17:
                        target_data.favorability[0] = new_value
                    elif value_index == 18:
                        target_data.trust = new_value
                    elif value_index == 19:
                        target_data.pregnancy.milk = new_value
                    elif value_index == 20:
                        target_data.pregnancy.milk_max = new_value
                    elif value_index == 21:
                        target_data.desire_point = new_value
                    elif value_index == 22:
                        target_data.semen_point = new_value
                    elif value_index == 23:
                        target_data.semen_point_max = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 二段状态数据
            elif key_index == 4:
                draw_text_list = []
                info_text = f"\n"
                for cid in target_data.second_behavior:
                    name = game_config.config_behavior[cid].name
                    info_text += f"({cid}){name}:{target_data.second_behavior[cid]}  "
                    if cid % 5 == 0:
                        info_text += "\n"
                draw_text_list.append(f"[000]:二段行为列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.second_behavior[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue
            # 状态数据
            elif key_index == 6:
                draw_text_list = []
                info_text = f"\n"
                for cid in game_config.config_character_state:
                    name = game_config.config_character_state[cid].name
                    info_text += f"{cid}:{name}={target_data.status_data[cid]} "
                draw_text_list.append(f"[000]:状态列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.status_data[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue
            # 能力数据
            elif key_index == 7:
                draw_text_list = []
                info_text = f"\n"
                for cid in game_config.config_ability:
                    name = game_config.config_ability[cid].name
                    info_text += f"{cid}:{name}={target_data.ability[cid]} "
                draw_text_list.append(f"[000]:能力列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.ability[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 经验数据
            elif key_index == 8:
                draw_text_list = []
                info_text = f"\n"
                for cid in target_data.experience:
                    name = game_config.config_experience[cid].name
                    info_text += f"{cid}:{name}={target_data.experience[cid]} "
                draw_text_list.append(f"[000]:经验列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.experience[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 宝珠数据
            elif key_index == 9:
                draw_text_list = []
                info_text = f"\n"
                for cid in target_data.juel:
                    name = game_config.config_juel[cid].name
                    info_text += f"{cid}:{name}={target_data.juel[cid]} "
                draw_text_list.append(f"[000]:宝珠列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.juel[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 素质数据
            elif key_index == 10:
                draw_text_list = []
                info_text = f"\n"
                for cid in target_data.talent:
                    name = game_config.config_talent[cid].name
                    info_text += f"{cid}:{name}={target_data.talent[cid]} "
                draw_text_list.append(f"[000]:素质列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.talent[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 污浊数据
            elif key_index == 12:
                draw_text_list = []
                draw_text_list.append(f"[000]:身体精液情况，编号int:[部位名str,当前精液量int,当前精液等级int,总精液量int]：\n{target_data.dirty.body_semen}")
                draw_text_list.append(f"\n[001]:服装精液情况，编号int:[部位名str,当前精液量int,当前精液等级int,总精液量int]：\n{target_data.dirty.cloth_semen}")
                draw_text_list.append(f"\n[002]:衣柜里的服装精液情况，编号int:[部位名str,当前精液量int,当前精液等级int,总精液量int]：\n{target_data.dirty.cloth_locker_semen}")
                draw_text_list.append(f"\n[003]:A是否干净 [0脏污,1灌肠中,2已灌肠,3精液灌肠中,4已精液灌肠]：{target_data.dirty.a_clean}")
                draw_text_list.append(f"[004]:身体部位:当前精液量int，输入4,0,5即可把0号部位的精液量改为5")
                draw_text_list.append(f"[005]:身体部位:当前精液等级int，输入5,0,1即可把0号部位的精液等级改为1")
                draw_text_list.append(f"[006]:服装部位:当前精液量int，输入6,1,5即可把1号服装的精液量改为5")
                draw_text_list.append(f"[007]:服装部位:当前精液等级int，输入7,1,1即可把1号服装的精液等级改为1")
                draw_text_list.append(f"[008]:增加身体、服装、衣柜服装全部位精液量int")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    # 根据第几项更改对应值
                    if value_index == 3:
                        target_data.dirty.a_clean = new_value
                    elif value_index == 8:
                        for i in range(len(target_data.dirty.body_semen)):
                            target_data.dirty.body_semen[i][1] += new_value
                            target_data.dirty.body_semen[i][2] = attr_calculation.get_semen_now_level(target_data.dirty.body_semen[i][1], i, 0)
                        for i in range(len(target_data.dirty.cloth_semen)):
                            target_data.dirty.cloth_semen[i][1] += new_value
                            target_data.dirty.cloth_semen[i][2] = attr_calculation.get_semen_now_level(target_data.dirty.cloth_semen[i][1], i, 1)
                        for i in range(len(target_data.dirty.cloth_locker_semen)):
                            target_data.dirty.cloth_locker_semen[i][1] += new_value
                            target_data.dirty.cloth_locker_semen[i][2] = attr_calculation.get_semen_now_level(target_data.dirty.cloth_locker_semen[i][1], i, 2)
                    elif value_index[0] == 0:
                        target_data.dirty.body_semen[value_index[1]][value_index[2]] = new_value
                    elif value_index[0] == 1:
                        target_data.dirty.cloth_semen[value_index[1]][value_index[2]] = new_value
                    elif value_index[0] == 2:
                        target_data.dirty.cloth_locker_semen[value_index[1]][value_index[2]] = new_value
                    elif value_index[0] == 4:
                        target_data.dirty.body_semen[value_index[1]][1] = new_value
                        target_data.dirty.body_semen[value_index[1]][2] = attr_calculation.get_semen_now_level(new_value, value_index[1], 0)
                    elif value_index[0] == 5:
                        target_data.dirty.body_semen[value_index[1]][2] = new_value
                    elif value_index[0] == 6:
                        target_data.dirty.cloth_semen[value_index[1]][1] = new_value
                        target_data.dirty.cloth_semen[value_index[1]][2] = attr_calculation.get_semen_now_level(new_value, value_index[1], 1)
                    elif value_index[0] == 7:
                        target_data.dirty.cloth_semen[value_index[1]][2] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 本次H数据
            elif key_index == 13:
                draw_text_list = []
                draw_text_list.append(f"[000]:身体道具情况:编号int:[道具名str,当前有无bool,状态的结束时间datetime.datetime]：\n{target_data.h_state.body_item}")
                draw_text_list.append(f"\n[001]:绳子捆绑情况:编号int：{target_data.h_state.bondage}")
                draw_text_list.append(f"\n[002]:阴茎插入位置，int，-1为未插入，其他同身体部位：{target_data.h_state.insert_position}")
                draw_text_list.append(f"\n[003]:身体上的射精位置，int，-1为未射精，其他同身体部位：{target_data.h_state.shoot_position_body}")
                draw_text_list.append(f"\n[004]:衣服上的射精位置，int，-1为未射精，其他同衣服部位：{target_data.h_state.shoot_position_cloth}")
                draw_text_list.append(f"\n[005]:高潮程度记录，每3级一个循环，1为小绝顶，2为普绝顶，3为强绝顶：\n{target_data.h_state.orgasm_level}")
                draw_text_list.append(f"\n[006]:衣服上的射精位置，int，-1为未射精，其他同衣服部位：\n{target_data.h_state.orgasm_count}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    # 根据第几项更改对应值
                    if value_index == 1:
                        target_data.h_state.bondage = new_value
                    elif value_index == 2:
                        target_data.h_state.insert_position = new_value
                    elif value_index == 3:
                        target_data.h_state.shoot_position_body = new_value
                    elif value_index == 4:
                        target_data.h_state.shoot_position_cloth = new_value
                    elif value_index[0] == 0:
                        target_data.h_state.body_item[value_index[1]][value_index[2]] = new_value
                    elif value_index[0] == 5:
                        target_data.h_state.orgasm_level[value_index[1]] = new_value
                    elif value_index[0] == 6:
                        target_data.h_state.orgasm_count[value_index[1]] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 助理数据
            elif key_index == 14:
                draw_text_list = []
                info_text = f"\n"
                for cid in target_data.assistant_services:
                    name = game_config.config_assistant_services[cid].name
                    info_text += f"{cid}:{name}={target_data.assistant_services[cid]} "
                draw_text_list.append(f"[000]:服务列表：\n{info_text}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    line_feed.draw()
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())

                    target_data.assistant_services[value_index] = new_value

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue


            # 娱乐数据
            elif key_index == 17:
                info_text = f"[000]:娱乐活动的类型：{target_data.entertainment.entertainment_type}\n"
                info_text += f"[001]:借的书的id：{target_data.entertainment.borrow_book_id_set}\n"
                info_text += f"[002]:归还当前阅读书籍的可能性比例：{target_data.entertainment.book_return_possibility}\n"
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()
                line_feed.draw()

                if change_draw_flag:
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变的项目，中间用英文小写逗号隔开。娱乐活动输入三个int；借还书则先输入0为删除1为增加，然后再输入书籍编号；可能性直接输入对应数字"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    if value_index[0] == 0:
                        target_data.entertainment.entertainment_type = [value_index[1], value_index[2], value_index[3]]
                    elif value_index[0] == 1:
                        if value_index[1] == 1:
                            target_data.entertainment.borrow_book_id_set.add(value_index[2])
                        else:
                            target_data.entertainment.borrow_book_id_set.remove(value_index[2])
                    elif value_index[0] == 2:
                        target_data.entertainment.book_return_possibility = value_index[1]

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue


            # 怀孕数据
            elif key_index == 18:
                draw_text_list = []
                draw_text_list.append(f"[000]:受精概率：{target_data.pregnancy.fertilization_rate}")
                reproduction_period = target_data.pregnancy.reproduction_period
                now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
                period_cid = f"生理期{now_reproduction_period_type}"
                reproduction_text = game_config.ui_text_data['h_state'][period_cid]
                draw_text_list.append(f"[001]:生殖周期的第几天(0安全1普通2危险3排卵，0110232)：{target_data.pregnancy.reproduction_period},{reproduction_text}")
                draw_text_list.append(f"[002]:开始受精的时间：{target_data.pregnancy.fertilization_time}      年月日分别为0,1,2")
                draw_text_list.append(f"[003]:当前妊娠素质：0受精-{target_data.talent[20]}，1妊娠-{target_data.talent[21]}，2临盆-{target_data.talent[22]}，3产后-{target_data.talent[23]}，4育儿-{target_data.talent[24]}")
                draw_text_list.append(f"[004]:出生的时间：{target_data.pregnancy.born_time}      年月日分别为0,1,2")
                draw_text_list.append(f"[005]:一键触发生产事件")
                draw_text_list.append(f"[006]:一键触发育儿+育儿完成事件")
                draw_text_list.append(f"[007]:角色当前乳汁量：{target_data.pregnancy.milk}")
                draw_text_list.append(f"[008]:角色最大乳汁量：{target_data.pregnancy.milk_max}")

                # 进行显示
                for i in range(len(draw_text_list)):
                    info_draw.text = draw_text_list[i]
                    info_draw.draw()
                    line_feed.draw()
                line_feed.draw()

                # 如果需要输入，则进行两次输入
                if change_draw_flag:
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变第几项，如果是带子项的项的话，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    # print(f"debug value_index = {value_index},new_value = {new_value}")

                    # 根据第几项更改对应值
                    if value_index == 0:
                        target_data.pregnancy.fertilization_rate = new_value
                        # print(f"debug value_index = {value_index},new_value = {new_value}")
                    elif value_index == 1:
                        target_data.pregnancy.reproduction_period = new_value
                    elif value_index == 5:
                        target_data.talent[22] = 1
                        target_data.pregnancy.fertilization_time = cache.game_time
                        new_year = target_data.pregnancy.fertilization_time.year - 1
                        target_data.pregnancy.fertilization_time = target_data.pregnancy.fertilization_time.replace(year = new_year)
                    elif value_index == 6:

                        child_id = target_data.relationship.child_id_list[-1]
                        child_character_data: game_type.Character = cache.character_data[child_id]
                        new_year = child_character_data.pregnancy.born_time.year - 1
                        child_character_data.pregnancy.born_time = child_character_data.pregnancy.born_time.replace(year = new_year)
                    elif value_index == 7:
                        target_data.pregnancy.milk = new_value
                    elif value_index == 8:
                        target_data.pregnancy.milk_max = new_value
                    elif value_index[0] == 2:
                        if len(value_index) == 1:
                            info_draw.text = "\n输出格式错误，请重试\n"
                            info_draw.draw()
                            continue
                        if value_index[1] == 0:
                            target_data.pregnancy.fertilization_time = target_data.pregnancy.fertilization_time.replace(year = new_value)
                        elif value_index[1] == 1:
                            target_data.pregnancy.fertilization_time = target_data.pregnancy.fertilization_time.replace(month = new_value)
                        elif value_index[1] == 2:
                            target_data.pregnancy.fertilization_time = target_data.pregnancy.fertilization_time.replace(day = new_value)
                    elif value_index[0] == 3:
                        if len(value_index) == 1:
                            info_draw.text = "\n输出格式错误，请重试\n"
                            info_draw.draw()
                            continue
                        target_data.talent[20 + value_index[1]] = new_value
                        target_data.pregnancy.fertilization_time = cache.game_time
                    elif value_index[0] == 4:
                        if len(value_index) == 1:
                            info_draw.text = "\n输出格式错误，请重试\n"
                            info_draw.draw()
                            continue
                        if value_index[1] == 0:
                            target_data.pregnancy.born_time = target_data.pregnancy.born_time.replace(year = new_value)
                        elif value_index[1] == 1:
                            target_data.pregnancy.born_time = target_data.pregnancy.born_time.replace(month = new_value)
                        elif value_index[1] == 2:
                            target_data.pregnancy.born_time = target_data.pregnancy.born_time.replace(day = new_value)

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 社会关系数据
            elif key_index == 19:
                info_text = f"[000]:父亲id：{target_data.relationship.father_id}\n"
                info_text += f"[001]:母亲id：{target_data.relationship.mother_id}\n"
                info_text += f"[002]:孩子id列表：{target_data.relationship.child_id_list}\n"
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()
                line_feed.draw()

                if change_draw_flag:
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变的项目，如果是列表则输入要改变第几号数据，以及这一项变成0或者1，中间用英文小写逗号隔开。列表的内容元素0为删除1为增加"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        value_index = int(value_index)
                    if value_index[0] == 0:
                        target_data.relationship.father_id = value_index[1]
                    elif value_index[0] == 1:
                        target_data.relationship.mother_id = value_index[1]
                    elif value_index[0] == 2:
                        if value_index[1] == 1:
                            target_data.relationship.child_id_list.append(value_index[2])
                        else:
                            target_data.relationship.child_id_list.remove(value_index[2])

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue


            # 特殊flag数据
            elif key_index == 20:
                info_text = f"1~7异常状态：，正常为1"
                info_text += f"    \n1:基础生理需求：睡觉、休息、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰：{handle_premise.handle_normal_1(self.target_character_id)}"
                info_text += f"    \n2:AI行动基本停止：临盆、产后、监禁：{handle_premise.handle_normal_2(self.target_character_id)}"
                info_text += f"    \n3:高优先级AI：助理、跟随、体检：{handle_premise.handle_normal_3(self.target_character_id)}"
                info_text += f"    \n4:服装异常：大致全裸、全裸：{handle_premise.handle_normal_4(self.target_character_id)}"
                info_text += f"    \n5:意识模糊，或弱交互：醉酒，平然：{handle_premise.handle_normal_5(self.target_character_id)}"
                info_text += f"    \n6:完全意识不清醒，或无交互：睡眠（熟睡或完全深眠），时停，空气：{handle_premise.handle_normal_6(self.target_character_id)}"
                info_text += f"    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中：{handle_premise.handle_normal_7(self.target_character_id)}"
                info_text += f"\n\n"
                info_text += f"[000]:在H模式中：{target_data.sp_flag.is_h}\n"
                info_text += f"[001]:AI行动里的原地发呆判定：{target_data.sp_flag.wait_flag}\n"
                info_text += f"[002]:跟随玩家，int [0不跟随,1智能跟随,2强制跟随,3前往博士办公室,4前往博士当前位置]：{target_data.sp_flag.is_follow}\n"
                info_text += f"[003]:疲劳状态（HP=1）：{target_data.sp_flag.tired}\n"
                info_text += f"[004]:被玩家惹生气：{target_data.sp_flag.angry_with_player}\n"
                info_text += f"[005]:角色停止移动：{target_data.sp_flag.move_stop}\n"
                info_text += f"[006]:被装袋搬走状态：{target_data.sp_flag.be_bagged}\n"
                info_text += f"[007]:玩家正在装袋搬走的角色的id：{target_data.sp_flag.bagging_chara_id}\n"
                info_text += f"[008]:被监禁状态：{target_data.sp_flag.imprisonment}\n"
                info_text += f"[009]:洗澡状态，int [0无,1要更衣,2要洗澡,3要披浴巾,4洗完澡]：{target_data.sp_flag.shower}\n"
                info_text += f"[010]:吃饭状态，int [0无,1要取餐,2要吃饭]：{target_data.sp_flag.eat_food}\n"
                info_text += f"[011]:要睡觉状态：{target_data.sp_flag.sleep}\n"
                info_text += f"[012]:要休息状态：{target_data.sp_flag.rest}\n"
                info_text += f"[013]:要撒尿状态：{target_data.sp_flag.pee}\n"
                info_text += f"[014]:发现食物不对劲：{target_data.sp_flag.find_food_weird}\n"
                info_text += f"[015]:游泳状态，int [0无,1要换泳衣,2要游泳]：{target_data.sp_flag.swim}\n"
                info_text += f"[016]:要检修状态：{target_data.sp_flag.work_maintenance}\n"
                info_text += f"[017]:帮忙买午饭状态，int [0无,1要买饭,2要买第二份饭,3要送饭]：{target_data.sp_flag.help_buy_food}\n"
                info_text += f"[018]:帮忙做饭状态，int [0无,1要做饭,2要送饭]：{target_data.sp_flag.help_make_food}\n"
                info_text += f"[019]:早安问候状态，int [0无,1要问候,2已问候]：{target_data.sp_flag.morning_salutation}\n"
                info_text += f"[020]:晚安问候状态，int [0无,1要问候,2已问候]：{target_data.sp_flag.night_salutation}\n"
                info_text += f"[021]:大浴场娱乐状态，int [0无,1要更衣,2要娱乐]：{target_data.sp_flag.bathhouse_entertainment}\n"
                info_text += f"[022]:要挤奶状态：{target_data.sp_flag.milk}\n"
                info_text += f"[023]:要自慰状态：{target_data.sp_flag.masturebate}，要找玩家逆推来自慰的状态：{target_data.sp_flag.npc_masturebate_for_player}\n"
                info_text += f"[024]:访客状态，int [0无,1访问中,2访问过]：{target_data.sp_flag.vistor}\n"
                info_text += f"[025]:香薰疗愈状态，int [0无,1回复,2习得,3反感,4快感,5好感,6催眠]：{target_data.sp_flag.aromatherapy}\n"
                info_text += f"[026]:外勤委托状态，0为未外勤，否则为对应外勤委托编号：{target_data.sp_flag.field_commission}\n"
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()
                line_feed.draw()

                if change_draw_flag:
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变的项目，如果是列表则输入要改变第几号数据，以及这一项变成几，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        info_draw.text = "\n输出格式错误，请重试\n"
                        info_draw.draw()
                        continue
                    if value_index[0] == 0:
                        target_data.sp_flag.is_h = value_index[1]
                    elif value_index[0] == 1:
                        target_data.sp_flag.wait_flag = value_index[1]
                    elif value_index[0] == 2:
                        target_data.sp_flag.is_follow = value_index[1]
                    elif value_index[0] == 3:
                        target_data.sp_flag.tired = value_index[1]
                    elif value_index[0] == 4:
                        target_data.sp_flag.angry_with_player = value_index[1]
                    elif value_index[0] == 5:
                        target_data.sp_flag.move_stop = value_index[1]
                    elif value_index[0] == 6:
                        target_data.sp_flag.be_bagged = value_index[1]
                    elif value_index[0] == 7:
                        target_data.sp_flag.bagging_chara_id = value_index[1]
                    elif value_index[0] == 8:
                        target_data.sp_flag.imprisonment = value_index[1]
                    elif value_index[0] == 9:
                        target_data.sp_flag.shower = value_index[1]
                    elif value_index[0] == 10:
                        target_data.sp_flag.eat_food = value_index[1]
                    elif value_index[0] == 11:
                        target_data.sp_flag.sleep = value_index[1]
                    elif value_index[0] == 12:
                        target_data.sp_flag.rest = value_index[1]
                    elif value_index[0] == 13:
                        target_data.sp_flag.pee = value_index[1]
                    elif value_index[0] == 14:
                        target_data.sp_flag.find_food_weird = value_index[1]
                    elif value_index[0] == 15:
                        target_data.sp_flag.swim = value_index[1]
                    elif value_index[0] == 16:
                        target_data.sp_flag.work_maintenance = value_index[1]
                    elif value_index[0] == 17:
                        target_data.sp_flag.help_buy_food = value_index[1]
                    elif value_index[0] == 18:
                        target_data.sp_flag.help_make_food = value_index[1]
                    elif value_index[0] == 19:
                        target_data.sp_flag.morning_salutation = value_index[1]
                    elif value_index[0] == 20:
                        target_data.sp_flag.night_salutation = value_index[1]
                    elif value_index[0] == 21:
                        target_data.sp_flag.bathhouse_entertainment = value_index[1]
                    elif value_index[0] == 22:
                        target_data.sp_flag.milk = value_index[1]
                    elif value_index[0] == 23:
                        target_data.sp_flag.masturebate = value_index[1]

                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            # 催眠数据
            elif key_index == 21:
                info_text = f""
                info_text += f"[000]:催眠程度：{target_data.hypnosis.hypnosis_degree}\n"
                info_text += f"[001]:体控-敏感度提升：{target_data.hypnosis.increase_body_sensitivity}\n"
                info_text += f"[002]:体控-强制排卵：{target_data.hypnosis.force_ovulation}\n"
                info_text += f"[003]:体控-木头人：{target_data.hypnosis.blockhead}\n"
                info_text += f"[004]:体控-逆推：{target_data.hypnosis.active_h}\n"
                info_text += f"[005]:心控-角色扮演，0为无，其他见Roleplay.csv：{target_data.hypnosis.roleplay}\n"
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()
                line_feed.draw()

                if change_draw_flag:
                    value_index_panel = panel.AskForOneMessage()
                    value_index_panel.set(_("输入改变的项目，如果是列表则输入要改变第几号数据，以及这一项变成几，中间用英文小写逗号隔开"), 100)
                    value_index = value_index_panel.draw()
                    if "," in value_index: # 转成全int的list
                        value_index = list(map(int, value_index.split(",")))
                    else:
                        info_draw.text = "\n输出格式错误，请重试\n"
                        info_draw.draw()
                        continue
                    if value_index[0] == 0:
                        target_data.hypnosis.hypnosis_degree = value_index[1]
                    elif value_index[0] == 1:
                        target_data.hypnosis.increase_body_sensitivity = value_index[1]
                    elif value_index[0] == 2:
                        target_data.hypnosis.force_ovulation = value_index[1]
                    elif value_index[0] == 3:
                        target_data.hypnosis.blockhead = value_index[1]
                    elif value_index[0] == 4:
                        target_data.hypnosis.active_h = value_index[1]
                    elif value_index[0] == 5:
                        target_data.hypnosis.roleplay.append(value_index[1])
                    # 接着刷新一遍显示新内容
                    change_draw_flag = False
                    continue

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width/2)
            back_draw.draw()
            again_draw = draw.CenterButton(_("[继续修改]"), _("继续修改"), window_width/2)
            again_draw.draw()
            return_list.append(again_draw.return_text)
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            else:
                change_draw_flag = True
                continue


class ChangeWorkButtonList:
    """
    点击后可选择NPC的工作的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, NPC_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.NPC_id: int = NPC_id
        """ 指令名字绘制文本 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        target_data: game_type.Character = cache.character_data[NPC_id]
        button_text = f"[{target_data.adv}：{target_data.name}]"
        self.button_return = str(NPC_id)

        # 按钮绘制

        name_draw = draw.CenterButton(
            button_text, self.button_return, self.width, cmd_func=self.button_0
        )
        self.now_draw = name_draw
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw


    def button_0(self):
        """选项1"""

        while 1:

            line = draw.LineDraw("-", window_width)
            line.draw()
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.width = window_width
            return_list = []

            target_data: game_type.Character = cache.character_data[self.NPC_id]
            info_text = f"{target_data.name}的当前工作为："
            if target_data.work.work_type == 61:
                info_text += "坐诊(玩家属性)"
            elif target_data.work.work_type == 71:
                info_text += "招募(NPC角色)"
            elif target_data.work.work_type == 101:
                info_text += "图书馆管理员(图书馆)"
            else:
                info_text += "无"
            info_text += "\n 可指派的新工作有：\n"
            info_draw.text = info_text
            info_draw.draw()

            # 遍历工作列表，获取每个工作的信息
            for cid in game_config.config_work_type.keys():
                if cid:
                    work_cid = game_config.config_work_type[cid].cid
                    work_name = game_config.config_work_type[cid].name
                    work_place = game_config.config_work_type[cid].place
                    work_describe = game_config.config_work_type[cid].describe

                    button_draw = draw.LeftButton(
                        f"[{str(work_cid).rjust(3,'0')}]{work_name}({work_place})：{work_describe}",
                        f"\n{work_cid}",
                        window_width ,
                        cmd_func=self.select_new_work,
                        args=work_cid
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def select_new_work(self,work_id: int):
        """赋予新的工作id"""
        target_data: game_type.Character = cache.character_data[self.NPC_id]
        target_data.work.work_type = work_id
        basement.update_work_people()
