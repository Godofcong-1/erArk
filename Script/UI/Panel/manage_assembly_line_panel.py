from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Design import attr_calculation
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

    def draw(self):
        """绘制对象"""

        title_text = "产品生产"
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = ""
            now_text += f" 当前lv{cache.base_resouce.facility_level[3]}仓库容量（单资源存放上限）：{cache.base_resouce.warehouse_capacity}\n"

            # 遍历全资源类型
            self.resouce_list = ["货币", "材料", "药剂"]
            for resouce in self.resouce_list:
                now_text += f"\n {resouce}："
                # 遍历该类型的资源
                for material_id in cache.base_resouce.materials_resouce:
                    material_data  = game_config.config_resouce[material_id]
                    if material_data.type == resouce:
                        now_text += f"  {material_data.name}：{cache.base_resouce.materials_resouce[material_id]}"
                now_text += "\n"

            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            for assembly_line_id in cache.base_resouce.assembly_line:
                now_text = f"\n {assembly_line_id+1}号流水线："

                # 生产产品
                formula_id = cache.base_resouce.assembly_line[assembly_line_id][0]
                formula_data = game_config.config_productformula[formula_id]
                product_id = formula_data.product_id
                product_data = game_config.config_resouce[product_id]
                now_text += f"\n    当前生产：{product_data.name}(1/h)      "
                all_info_draw.text = now_text
                all_info_draw.draw()
                button_text = " [生产调整] "
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(f"{button_text}_{assembly_line_id}"),
                    len(button_text) * 2,
                    cmd_func=self.select_assembly_line_produce,
                    args=assembly_line_id,
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

                # 生产效率
                now_level = cache.base_resouce.facility_level[12]
                facility_cid = game_config.config_facility_effect_data["制造加工区"][int(now_level)]
                all_effect = 0
                facility_effect = game_config.config_facility_effect[facility_cid].effect
                all_effect += facility_effect
                now_text = f"\n    当前效率加成：设施(lv{now_level}:{facility_effect}%)"
                # 遍历输出干员的能力效率加成
                for chara_id in cache.base_resouce.assembly_line[assembly_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    all_effect += character_effect
                    now_text += f" + {character_data.name}(制造lv{character_data.ability[48]}:{character_effect}%)"
                now_text += f" = {all_effect}%      "
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 生产消耗
                now_text = f"\n    当前生产消耗："
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
            button_text = "[001]工人增减"
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
            button_text = "[002]工位调整"
            button_draw = draw.LeftButton(
                _(button_text),
                _(button_text),
                self.width,
                cmd_func=self.select_npc_position,
                args=assembly_line_id,
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
                break

    def select_assembly_line_produce(self, assembly_line_id):
        """选择流水线生产的产品"""
        while 1:

                line = draw.LineDraw("-", window_width)
                line.draw()
                line_feed.draw()
                info_draw = draw.NormalDraw()
                info_draw.width = window_width
                return_list = []

                info_text = f"{assembly_line_id+1}号流水线当前生产的产品为："

                formula_now_id = cache.base_resouce.assembly_line[assembly_line_id][0]
                formula_now_data = game_config.config_productformula[formula_now_id]
                product_now_id = formula_now_data.product_id
                product_now_data = game_config.config_resouce[product_now_id]

                info_text += f"{product_now_data.name}"
                info_text += "\n当前可以生成的产品有：\n"
                info_draw.text = info_text
                info_draw.draw()

                # 遍历配方列表，获取每个配方的信息
                for cid in game_config.config_productformula.keys():
                    formula_data = game_config.config_productformula[cid]
                    formula_cid = game_config.config_productformula[cid].cid
                    product_id = formula_data.product_id
                    product_data = game_config.config_resouce[product_id]
                    product_name = product_data.name
                    product_describe = product_data.info

                    # 判断当前配方是否可以生产，未解锁则跳过
                    flag_open = True
                    # for open_cid in game_config.config_facility_open:
                    #     if game_config.config_facility_open[open_cid].name == work_place:
                    #         if not cache.base_resouce.facility_open[open_cid]:
                    #             flag_open = False
                    #         break

                    if flag_open:

                        # 输出配方信息
                        button_draw = draw.LeftButton(
                            f"[{str(formula_cid).rjust(3,'0')}]{product_name}：{product_describe}",
                            f"\n{formula_cid}",
                            window_width ,
                            cmd_func=self.change_assembly_line_produce,
                            args=(assembly_line_id ,formula_cid)
                        )
                        button_draw.draw()
                        return_list.append(button_draw.return_text)

                        formula_text = formula_data.formula
                        now_text = f"\n     生产消耗："
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
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
                back_draw.draw()
                line_feed.draw()
                return_list.append(back_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list:
                    break

    def change_assembly_line_produce(self, assembly_line_id, formula_cid):
        """更改流水线生产的产品"""
        cache.base_resouce.assembly_line[assembly_line_id][0] = formula_cid

    def select_npc_position(self, assembly_line_id):
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
                for assembly_line_id in cache.base_resouce.assembly_line:
                    if self.now_chara_id in cache.base_resouce.assembly_line[assembly_line_id][1]:
                        old_position = assembly_line_id
                        break
            else:
                now_select_npc_name = "未选择"

            all_info_draw = draw.NormalDraw()
            now_text = f"\n○当前的决定： 把 {now_select_npc_name} 从 {old_position + 1} 号流水线调整到 {self.target_position + 1} 号流水线"
            all_info_draw.text = now_text
            all_info_draw.draw()

            # 遍历全干员
            now_text = f"\n可选工人有：\n"
            all_info_draw.text = now_text
            all_info_draw.draw()
            flag_not_empty = False
            cache.npc_id_got.discard(0)
            for chara_id in cache.npc_id_got:
                character_data: game_type.Character = cache.character_data[chara_id]
                # 找到职业是生产工人的
                if character_data.work.work_type == 121:
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    button_text = f" [{character_data.name}(制造lv{character_data.ability[48]}:{character_effect}%)] "
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
                now_text = f" 暂无工作是生产工人的干员"
                all_info_draw.text = now_text
                all_info_draw.draw()

            line_feed.draw()

            for assembly_line_id in cache.base_resouce.assembly_line:
                now_text = f"\n {assembly_line_id+1}号流水线："

                # 生产产品
                formula_id = cache.base_resouce.assembly_line[assembly_line_id][0]
                formula_data = game_config.config_productformula[formula_id]
                product_id = formula_data.product_id
                product_data = game_config.config_resouce[product_id]
                now_text += f"\n    当前生产：{product_data.name}(1/h)      "
                all_info_draw.text = now_text
                all_info_draw.draw()

                button_text = f" [选择该流水线] "
                button_draw = draw.CenterButton(
                _(button_text),
                _(f"{button_text}_{assembly_line_id}"),
                int(len(button_text)*2),
                cmd_func=self.settle_assembly_line_id,
                args=assembly_line_id,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 生产效率
                now_text = f"\n    当前工人："
                # 遍历输出干员的能力效率加成
                for chara_id in cache.base_resouce.assembly_line[assembly_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    now_text += f" + {character_data.name}(制造lv{character_data.ability[48]}:{character_effect}%)"
                all_info_draw.text = now_text
                all_info_draw.draw()
                line_feed.draw()

            line_feed.draw()
            yes_draw = draw.CenterButton(_("[确定]"), _("确定"), window_width / 2)
            yes_draw.draw()
            return_list.append(yes_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width / 2)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            elif yrn == yes_draw.return_text:
                cache.base_resouce.assembly_line[old_position][1].discard(self.now_chara_id)
                cache.base_resouce.assembly_line[self.target_position][1].add(self.now_chara_id)
                break

    def settle_npc_id(self, chara_id):
        """结算干员的id变更"""
        self.now_chara_id = chara_id

    def settle_assembly_line_id(self, assembly_line_id):
        """结算流水线的id变更"""
        self.target_position = assembly_line_id
