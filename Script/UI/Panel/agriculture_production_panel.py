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


class Agriculture_Production_Panel:
    """
    用于农业生产的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("农业生产")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("农业生产")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = ""
            now_text += _(f" 当前仓库等级：{cache.rhodes_island.facility_level[3]}，容量（单资源存放上限）：{cache.rhodes_island.warehouse_capacity}\n")

            # 遍历该类型的资源
            for material_id in [11, 16]:
                material_data  = game_config.config_resouce[material_id]
                now_text += f"  {material_data.name}：{cache.rhodes_island.materials_resouce[material_id]}"
            now_text += "\n"

            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            for agriculture_line_id in cache.rhodes_island.agriculture_line:
                now_text = f"\n 农田："
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 基础数据
                resouce_id = cache.rhodes_island.agriculture_line[agriculture_line_id][0]
                resouce_data = game_config.config_resouce[resouce_id]

                # 生产产品
                now_text = _(f"\n    当前生产：{resouce_data.name}(10/d)      ")
                all_info_draw.text = now_text
                all_info_draw.draw()
                button_text = _(" [生产调整] ")
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(f"{button_text}_{agriculture_line_id}"),
                    len(button_text) * 2,
                    cmd_func=self.select_agriculture_line_produce,
                    args=agriculture_line_id,
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

                # 生产效率
                now_level = cache.rhodes_island.facility_level[12]
                facility_cid = game_config.config_facility_effect_data["疗养庭院"][int(now_level)]
                all_effect = 0
                facility_effect = game_config.config_facility_effect[facility_cid].effect
                all_effect += facility_effect
                now_text = _(f"\n    当前效率加成：设施(lv{now_level}:{facility_effect}%)")
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.agriculture_line[agriculture_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[47]))
                    all_effect += character_effect
                    now_text += _(f" + {character_data.name}(农业lv{character_data.ability[47]}:{character_effect}%)")
                now_text += f" = {all_effect}%      "
                all_info_draw.text = now_text
                all_info_draw.draw()
                line_feed.draw()

            line_feed.draw()
            button_text = _("[001]种植员增减")
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
            button_text = _("[002]位置调整")
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

    def select_agriculture_line_produce(self, agriculture_line_id):
        """选择农田生产的产品"""
        while 1:

                line = draw.LineDraw("-", window_width)
                line.draw()
                info_draw = draw.NormalDraw()
                info_draw.width = window_width
                return_list = []

                now_level = cache.rhodes_island.facility_level[12]
                resouce_id = cache.rhodes_island.agriculture_line[agriculture_line_id][0]
                resouce_data = game_config.config_resouce[resouce_id]

                info_text = f""
                info_text += _(f" 农田当前种植的是：{resouce_data.name}")

                info_text += _("\n\n 当前可以种植的有：\n\n")
                info_draw.text = info_text
                info_draw.draw()

                # 遍历配方列表，获取每个配方的信息
                for cid in [11]:
                    resouce_now_data = game_config.config_resouce[cid]

                    # 判断当前配方是否可以生产，未解锁则跳过
                    flag_open = True
                    # if product_difficulty > now_level:
                    #     flag_open = False

                    if flag_open:

                        # 输出配方信息
                        button_draw = draw.LeftButton(
                            f"[{str(cid).rjust(3,'0')}]{resouce_now_data.name}：{resouce_now_data.info}",
                            f"\n{cid}",
                            window_width ,
                            cmd_func=self.change_agriculture_line_produce,
                            args=(agriculture_line_id ,cid)
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
                for agriculture_line_id in cache.rhodes_island.agriculture_line:
                    if self.now_chara_id in cache.rhodes_island.agriculture_line[agriculture_line_id][1]:
                        old_position = agriculture_line_id
                        break
            else:
                now_select_npc_name = _("未选择")

            all_info_draw = draw.NormalDraw()
            now_text = _(f"\n○当前的决定： 把 {now_select_npc_name} 从 {old_position + 1} 号农田调整到 {self.target_position + 1} 号农田")
            all_info_draw.text = now_text
            all_info_draw.draw()

            # 遍历全干员
            now_text = _(f"\n可选种植员有：\n")
            all_info_draw.text = now_text
            all_info_draw.draw()
            flag_not_empty = False
            # 去掉玩家
            cache.npc_id_got.discard(0)
            # 去掉访客
            id_list = [i for i in cache.npc_id_got if i not in cache.rhodes_island.visitor_info]
            for chara_id in id_list:
                character_data: game_type.Character = cache.character_data[chara_id]
                # 找到职业是生产种植员的
                if character_data.work.work_type == 161:
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[47]))
                    button_text = _(f" [{character_data.name}(农业lv{character_data.ability[47]}:{character_effect}%)] ")
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

            # 如果没有工作是种植员的干员则输出提示
            if not flag_not_empty:
                now_text = _(f" 暂无工作是种植员的干员")
                all_info_draw.text = now_text
                all_info_draw.draw()

            line_feed.draw()

            for agriculture_line_id in cache.rhodes_island.agriculture_line:
                now_text = _(f"\n 农田：")

                resouce_id = cache.rhodes_island.agriculture_line[agriculture_line_id][0]
                resouce_data = game_config.config_resouce[resouce_id]
                now_text += _(f"\n    当前生产：{resouce_data.name}(10/d)      ")
                all_info_draw.text = now_text
                all_info_draw.draw()

                button_text = _(f" [将选择种植员调整至该农田] ")
                button_draw = draw.CenterButton(
                _(button_text),
                _(f"{button_text}_{agriculture_line_id}"),
                int(len(button_text)*2),
                cmd_func=self.settle_agriculture_line_id,
                args=agriculture_line_id,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 生产效率
                now_text = _(f"\n    当前种植员：")
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.agriculture_line[agriculture_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[47]))
                    now_text += _(f" + {character_data.name}(农业lv{character_data.ability[47]}:{character_effect}%)")
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
                cache.rhodes_island.agriculture_line[old_position][1].discard(self.now_chara_id)
                cache.rhodes_island.agriculture_line[self.target_position][1].add(self.now_chara_id)
                basement.get_base_updata()
                break

    def change_agriculture_line_produce(self, agriculture_line_id, formula_cid):
        """更改农田的种植"""
        if cache.rhodes_island.agriculture_line[agriculture_line_id][0] != 0 and cache.rhodes_island.agriculture_line[agriculture_line_id][4] != cache.game_time.hour:
            pass
        else:
            cache.rhodes_island.agriculture_line[agriculture_line_id][0] = formula_cid

    def settle_npc_id(self, chara_id):
        """结算干员的id变更"""
        self.now_chara_id = chara_id

    def settle_agriculture_line_id(self, agriculture_line_id):
        """结算农田的id变更"""
        self.target_position = agriculture_line_id
