from turtle import position
from typing import Dict, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import basement,character_handle, handle_premise, attr_calculation, clothing, map_handle
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

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
            if self.now_panel == "全局变量":

                all_info_draw = draw.NormalDraw()
                all_info_text = "全局变量一览："
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

            elif self.now_panel == "常用更改":

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

            elif self.now_panel == "NPC角色":

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
                        cache.rhodes_island.recruit_line[i] = [0,0,set(),0]
                    cache.rhodes_island.recruited_id = set()
                # 交互对象全部位快感增加
                elif key_index == 15:
                    line_feed.draw()
                    change_value_panel = panel.AskForOneMessage()
                    change_value_panel.set(_("输入改变后的值"), 100)
                    new_value = int(change_value_panel.draw())
                    target_id = cache.character_data[0].target_character_id
                    target_character_data = cache.character_data[target_id]
                    for i in range(8):
                        target_character_data.status_data[i] += new_value
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
                    name = game_config.config_status[cid].name
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
                info_text += f"    \n3:助理或跟随：助理、跟随模式下：{handle_premise.handle_normal_3(self.target_character_id)}"
                info_text += f"    \n4:服装异常：大致全裸、全裸：{handle_premise.handle_normal_4(self.target_character_id)}"
                info_text += f"    \n5:意识模糊，或弱交互：醉酒，平然：{handle_premise.handle_normal_5(self.target_character_id)}"
                info_text += f"    \n6:完全意识不清醒，或无交互：睡眠（熟睡或完全深眠），时停，空气：{handle_premise.handle_normal_6(self.target_character_id)}"
                info_text += f"    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问：{handle_premise.handle_normal_7(self.target_character_id)}"
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
                info_text += f"[023]:要自慰状态：{target_data.sp_flag.masturebate}\n"
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
                        target_data.hypnosis.roleplay = value_index[1]
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
