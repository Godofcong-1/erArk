from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, basement
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import manage_basement_panel

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


def settle_assembly_line(newdayflag = False):
    """
    结算流水线的生产
    """
    

    # 遍历流水线
    for assembly_line_id in cache.rhodes_island.assembly_line:
        now_formula_id = cache.rhodes_island.assembly_line[assembly_line_id][0]
        if now_formula_id != 0:
            formula_data_now = game_config.config_productformula_data[now_formula_id]
            formula_now = game_config.config_productformula[now_formula_id]
            product_id = formula_now.product_id
            # 最大生产时间
            if newdayflag:
                max_time = 24 + cache.game_time.hour - cache.rhodes_island.assembly_line[assembly_line_id][4]
            else:
                max_time = cache.game_time.hour - cache.rhodes_island.assembly_line[assembly_line_id][4]
            # 生产效率
            produce_effect = cache.rhodes_island.assembly_line[assembly_line_id][2]
            # 公务的总效率
            produce_effect *= cache.rhodes_island.effectiveness / 100
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect / 100)
            produce_num = produce_num_max
            # print(f"debug 流水线{assembly_line_id},max_time = {max_time}，produce_effect = {produce_effect}，最大生产数为{produce_num_max}")

            # 遍历全部原料，判断是否足够
            for need_type in formula_data_now:
                # 当前种类的原料最大生产数
                now_type_max_produce_num = cache.rhodes_island.materials_resouce[need_type] // formula_data_now[need_type]
                # 不超过总最大生产数
                produce_num = min(produce_num,now_type_max_produce_num)
            # print(f"debug 流水线{assembly_line_id}，实际生产数为{produce_num}")

            # 结算实际生产
            if produce_num > 0:
                # 结算实际消耗的原料
                for need_type in formula_data_now:
                    cache.rhodes_island.materials_resouce[need_type] -= produce_num * formula_data_now[need_type]
                # 结算实际生产的产品
                cache.rhodes_island.materials_resouce[product_id] += produce_num

                now_text = _("\n 流水线{0}:").format(assembly_line_id)
                now_text += _("上次结算是{0}时，到现在已过{1}小时，").format(cache.rhodes_island.assembly_line[assembly_line_id][4], max_time)
                if produce_num < produce_num_max:
                    now_text += _("由于原料不足，最大可以生产{0}个，实际").format(produce_num)
                now_text += _("共生产了{0}个{1}").format(produce_num, game_config.config_resouce[product_id].name)
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[product_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[product_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _("，由于仓库容量不足，{0}已达上限数量{1}").format(game_config.config_resouce[product_id].name, cache.rhodes_island.warehouse_capacity)
                now_text += f"\n"
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                now_draw.text = now_text
                now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.assembly_line[assembly_line_id][4] = cache.game_time.hour


class Manage_Assembly_Line_Panel:
    """
    用于生产产品的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("产品生产")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.show_resource_type_dict: Dict = {_("药剂"): False, _("乳制品"): False, _("香水"): False}

    def draw(self):
        """绘制对象"""

        title_text = _("产品生产")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        settle_assembly_line()

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = ""
            now_text += _(" 当前仓库等级：{0}，容量（单资源存放上限）：{1}\n").format(cache.rhodes_island.facility_level[3], cache.rhodes_island.warehouse_capacity)

            # 遍历全资源类型
            self.resouce_list = [_("材料"), _("药剂"), _("乳制品"), _("香水")]
            for resouce in self.resouce_list:
                now_text += f"\n {resouce}："
                # 遍历该类型的资源
                for material_id in cache.rhodes_island.materials_resouce:
                    material_data  = game_config.config_resouce[material_id]
                    if material_data.type == resouce:
                        now_text += f"  {material_data.name}：{cache.rhodes_island.materials_resouce[material_id]}"
                now_text += "\n"

            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            for assembly_line_id in cache.rhodes_island.assembly_line:
                now_text = _("\n {0}号流水线：").format(assembly_line_id+1)
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 基础数据
                formula_id = cache.rhodes_island.assembly_line[assembly_line_id][0]
                formula_data = game_config.config_productformula[formula_id]
                product_id = formula_data.product_id
                product_data = game_config.config_resouce[product_id]

                # 显示结算
                # 改成自动结算了
                # if formula_id != 0 and cache.base_resouce.assembly_line[assembly_line_id][4] != cache.game_time.hour:
                #     line_feed.draw()
                #     button_text = " [生产结算] "
                #     button_draw = draw.CenterButton(
                #         _(button_text),
                #         _("{0}_{1}").format(button_text, assembly_line_id),
                #         len(button_text) * 2,
                #         cmd_func=basement.settle_assembly_line,
                #         )
                #     return_list.append(button_draw.return_text)
                #     button_draw.draw()
                # else:
                #     now_text = f"\n    已结算"
                #     all_info_draw.text = now_text
                #     all_info_draw.draw()

                # 生产产品
                now_text = _("\n    当前生产：{0}(1/h)      ").format(product_data.name)
                all_info_draw.text = now_text
                all_info_draw.draw()
                button_text = _(" [生产调整] ")
                button_draw = draw.CenterButton(
                    _(button_text),
                    "{0}_{1}".format(button_text, assembly_line_id),
                    len(button_text) * 2,
                    cmd_func=self.select_assembly_line_produce,
                    args=assembly_line_id,
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

                # 生产效率
                now_level = cache.rhodes_island.facility_level[12]
                facility_cid = game_config.config_facility_effect_data[_("制造加工区")][int(now_level)]
                all_effect = 0
                facility_effect = game_config.config_facility_effect[facility_cid].effect
                all_effect += facility_effect
                now_text = _("\n    当前效率加成：设施(lv{0}:{1}%)").format(now_level, facility_effect)
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.assembly_line[assembly_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    all_effect += character_effect
                    now_text += _(" + {0}(制造lv{1}:{2}%)").format(character_data.name, character_data.ability[48], character_effect)
                now_text += f" = {all_effect}%      "
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 生产消耗
                now_text = _("\n    当前生产消耗：")
                formula_text = formula_data.formula
                # 以&为分割判定是否有多个需求
                if "&" not in formula_text:
                    need_list = []
                    need_list.append(formula_text)
                else:
                    need_list = formula_text.split('&')
                for need_text in need_list:
                    need_type = int(need_text.split('|')[0])
                    need_value = int(need_text.split('|')[1])
                    now_text += f"  {game_config.config_resouce[need_type].name}:{need_value}/h"

                all_info_draw.text = now_text
                all_info_draw.draw()
                line_feed.draw()

            line_feed.draw()
            button_text = _("[001]工人增减")
            button_draw = draw.LeftButton(
                _(button_text),
                _(button_text),
                self.width,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=self.width
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw()
            button_text = _("[002]工位调整")
            button_draw = draw.LeftButton(
                _(button_text),
                _(button_text),
                self.width,
                cmd_func=self.select_npc_position,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_assembly_line_produce(self, assembly_line_id):
        """选择流水线生产的产品"""
        while 1:

                line = draw.LineDraw("-", window_width)
                line.draw()
                info_draw = draw.NormalDraw()
                info_draw.width = window_width
                return_list = []

                formula_now_id = cache.rhodes_island.assembly_line[assembly_line_id][0]
                formula_now_data = game_config.config_productformula[formula_now_id]
                product_now_id = formula_now_data.product_id
                product_now_data = game_config.config_resouce[product_now_id]
                now_level = cache.rhodes_island.facility_level[12]

                info_text = f""
                # info_text = f" ○需要先结算然后才可以变动生产的产品\n\n"
                info_text += _(" {0}号流水线当前生产的产品为：{1}").format(assembly_line_id+1, product_now_data.name)

                info_text += _("\n\n 当前可以生成的产品有：\n\n")
                info_draw.text = info_text
                info_draw.draw()

                resouce_list = [_("药剂"), _("乳制品"), _("香水")]

                # 遍历全资源类型
                for resouce in resouce_list:

                    # 判断是否显示该类型的资源
                    if self.show_resource_type_dict[resouce]:
                        draw_text = f" ▼[{resouce}]"
                    else:
                        draw_text = f" ▶[{resouce}]"
                    button_draw = draw.LeftButton(
                    f"{draw_text}",
                    f"{resouce}",
                    len(draw_text) * 2,
                    cmd_func=self.settle_show_resource_type,
                    args=(resouce)
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    line_feed.draw()

                    if not self.show_resource_type_dict[resouce]:
                        continue

                    # 遍历该类型的资源
                    for material_id in cache.rhodes_island.materials_resouce:
                        material_data = game_config.config_resouce[material_id]
                        formula_cid = 0
                        if material_data.type == resouce:
                            # 根据资源id来查找配方id
                            for cid in game_config.config_productformula.keys():
                                formula_data = game_config.config_productformula[cid]
                                if formula_data.product_id == material_id:
                                    formula_cid = formula_data.cid
                                    break
                            # 如果没有配方id则跳过
                            if formula_cid == 0:
                                continue
                            # 判断当前配方是否可以生产，未解锁则跳过
                            flag_open = True
                            if formula_data.difficulty > now_level:
                                flag_open = False
                            # 可以生产的话则输出
                            if flag_open:
                                line_feed.draw()
                                button_draw = draw.LeftButton(
                                    f"[{str(formula_cid).rjust(3,'0')}]{material_data.name}：{material_data.info}",
                                    f"\n{formula_cid}",
                                    window_width ,
                                    cmd_func=self.change_assembly_line_produce,
                                    args=(assembly_line_id ,formula_cid)
                                )
                                button_draw.draw()
                                return_list.append(button_draw.return_text)

                                formula_text = formula_data.formula
                                now_text = _("\n     生产消耗：")
                                # 以&为分割判定是否有多个需求
                                if "&" not in formula_text:
                                    need_list = []
                                    need_list.append(formula_text)
                                else:
                                    need_list = formula_text.split('&')
                                for need_text in need_list:
                                    need_type = int(need_text.split('|')[0])
                                    need_value = int(need_text.split('|')[1])
                                    now_text += f"  {game_config.config_resouce[need_type].name}：{need_value}/h"

                                info_draw.text = now_text
                                info_draw.draw()
                                line_feed.draw()
                    line_feed.draw()

                line_feed.draw()
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
                back_draw.draw()
                line_feed.draw()
                return_list.append(back_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list and yrn not in resouce_list:
                    break

    def select_npc_position(self):
        """选择干员的工位"""

        self.now_chara_id = -1
        old_position = 0
        self.target_position = 0

        while 1:
            return_list = []
            line = draw.LineDraw("-", window_width)
            line.draw()

            if self.now_chara_id != -1:
                now_character_data: game_type.Character = cache.character_data[self.now_chara_id]
                now_select_npc_name = now_character_data.name
                for assembly_line_id in cache.rhodes_island.assembly_line:
                    if self.now_chara_id in cache.rhodes_island.assembly_line[assembly_line_id][1]:
                        old_position = assembly_line_id
                        break
            else:
                now_select_npc_name = _("未选择")

            all_info_draw = draw.NormalDraw()
            now_text = _("\n○当前的决定： 把 {0} 从 {1} 号流水线调整到 {2} 号流水线").format(now_select_npc_name, old_position + 1, self.target_position + 1)
            all_info_draw.text = now_text
            all_info_draw.draw()

            # 遍历全干员
            now_text = _("\n可选工人有：\n")
            all_info_draw.text = now_text
            all_info_draw.draw()
            flag_not_empty = False
            # 去掉玩家
            cache.npc_id_got.discard(0)
            # 去掉访客
            id_list = [i for i in cache.npc_id_got if i not in cache.rhodes_island.visitor_info]
            for chara_id in id_list:
                character_data: game_type.Character = cache.character_data[chara_id]
                # 找到职业是生产工人的
                if character_data.work.work_type == 121:
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    button_text = _(" [{0}(制造lv{1}:{2}%)] ").format(character_data.name, character_data.ability[48], character_effect)
                    button_draw = draw.CenterButton(
                    _(button_text),
                    _(button_text),
                    int(len(button_text)*1.5),
                    cmd_func=self.settle_npc_id,
                    args=chara_id,
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    flag_not_empty = True

            # 如果没有工作是生产工人的干员则输出提示
            if not flag_not_empty:
                now_text = _(" 暂无工作是生产工人的干员")
                all_info_draw.text = now_text
                all_info_draw.draw()

            line_feed.draw()

            for assembly_line_id in cache.rhodes_island.assembly_line:
                now_text = _("\n {0}号流水线：").format(assembly_line_id+1)

                # 生产产品
                formula_id = cache.rhodes_island.assembly_line[assembly_line_id][0]
                formula_data = game_config.config_productformula[formula_id]
                product_id = formula_data.product_id
                product_data = game_config.config_resouce[product_id]
                now_text += _("\n    当前生产：{0}(1/h)      ").format(product_data.name)
                all_info_draw.text = now_text
                all_info_draw.draw()

                button_text = _(" [将选择工人调整至该流水线] ")
                button_draw = draw.CenterButton(
                _(button_text),
                "{0}_{1}".format(button_text, assembly_line_id),
                int(len(button_text)*2),
                cmd_func=self.settle_assembly_line_id,
                args=assembly_line_id,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 生产效率
                now_text = _("\n    当前工人：")
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.assembly_line[assembly_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    now_text += _(" + {0}(制造lv{1}:{2}%)").format(character_data.name, character_data.ability[48], character_effect)
                all_info_draw.text = now_text
                all_info_draw.draw()
                line_feed.draw()

            line_feed.draw()
            yes_draw = draw.CenterButton(_("[确定]"), _("确定"), window_width / 2)
            if self.now_chara_id != -1:
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width / 2)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            # 确定的话就进行id的转移结算
            elif yrn == yes_draw.return_text:
                cache.rhodes_island.assembly_line[old_position][1].discard(self.now_chara_id)
                cache.rhodes_island.assembly_line[self.target_position][1].add(self.now_chara_id)
                basement.get_base_updata()
                break

    def change_assembly_line_produce(self, assembly_line_id, formula_cid):
        """更改流水线生产的产品"""
        if cache.rhodes_island.assembly_line[assembly_line_id][0] != 0 and cache.rhodes_island.assembly_line[assembly_line_id][4] != cache.game_time.hour:
            pass
        else:
            cache.rhodes_island.assembly_line[assembly_line_id][0] = formula_cid

    def settle_npc_id(self, chara_id):
        """结算干员的id变更"""
        self.now_chara_id = chara_id

    def settle_assembly_line_id(self, assembly_line_id):
        """结算流水线的id变更"""
        self.target_position = assembly_line_id

    def settle_show_resource_type(self, resouce_type):
        """设置显示的资源类型"""
        self.show_resource_type_dict[resouce_type] = not self.show_resource_type_dict[resouce_type]
