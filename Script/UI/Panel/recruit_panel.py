from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle
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


class Recruit_Panel:
    """
    用于招募的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("招募")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "招募"
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = ""
            if len(cache.rhodes_island.recruited_id) == 0:
                now_text += " 当前没有招募到干员\n"
            else:
                now_text += f" 当前已招募待确认的干员有："
                for chara_id in cache.rhodes_island.recruited_id:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    now_text += f" [{str(character_data.adv).rjust(4,'0')}]{character_data.name}"
                now_text += f"\n"

            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            for recruit_line_id in cache.rhodes_island.recruit_line:
                now_text = f"\n {recruit_line_id+1}号招募进度：{cache.rhodes_island.recruit_line[recruit_line_id][0]}"
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 基础数据
                recruitment_strategy_id = cache.rhodes_island.recruit_line[recruit_line_id][1]
                recruitment_strategy_data = game_config.config_recruitment_strategy[recruitment_strategy_id]

                # 招募策略
                now_text = f"\n    招募策略：{recruitment_strategy_data.name}(1/h)      "
                all_info_draw.text = now_text
                all_info_draw.draw()
                button_text = " [调整策略] "
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(f"{button_text}_{recruit_line_id}"),
                    len(button_text) * 2,
                    cmd_func=self.select_recruitment_strategy,
                    args=recruit_line_id,
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

                # 招募效率
                now_level = cache.rhodes_island.facility_level[7]
                facility_cid = game_config.config_facility_effect_data["文职部"][int(now_level)]
                all_effect = 0
                facility_effect = game_config.config_facility_effect[facility_cid].effect
                now_text = f"\n    当前效率加成：["
                # 遍历输出干员的能力效率加成，40号话术技能
                for chara_id in cache.rhodes_island.recruit_line[recruit_line_id][2]:
                    # 第一次循环不加"+"，之后都加
                    if all_effect != 0:
                        now_text += " + "
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = 5 * attr_calculation.get_ability_adjust(character_data.ability[40])
                    all_effect += character_effect
                    now_text += f"{character_data.name}(话术lv{character_data.ability[48]}:{round(character_effect, 1)}%)"
                all_effect *= 1 + (facility_effect / 100)
                now_text += f"] * 效率加成：设施(lv{now_level}:{facility_effect}%)"
                now_text += f" = {round(all_effect, 1)}%      "
                all_info_draw.text = now_text
                all_info_draw.draw()

                line_feed.draw()

            line_feed.draw()
            button_text = "[001]人员增减"
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

    def select_recruitment_strategy(self, recruit_line_id):
        """选择招募策略"""
        while 1:

                line = draw.LineDraw("-", window_width)
                line.draw()
                info_draw = draw.NormalDraw()
                info_draw.width = window_width
                return_list = []

                recruitment_strategy_id = cache.rhodes_island.recruit_line[recruit_line_id][1]
                recruitment_strategy_data = game_config.config_recruitment_strategy[recruitment_strategy_id]

                info_text = f""
                info_text += f" {recruit_line_id+1}号招募当前的策略为：{recruitment_strategy_data.name}"

                info_text += "\n\n 当前可以选择的策略有：\n"
                info_draw.text = info_text
                info_draw.draw()

                # 当前设施等级
                now_level = cache.rhodes_island.facility_level[7]

                # 遍历策略列表，获取每个策略的信息
                for cid in game_config.config_recruitment_strategy.keys():
                    recruitment_strategy_data = game_config.config_recruitment_strategy[cid]

                    if now_level >= cid + 1:

                        # 输出策略信息
                        button_draw = draw.LeftButton(
                            f"[{str(cid).rjust(2,'0')}]{recruitment_strategy_data.name}：{recruitment_strategy_data.introduce}",
                            f"\n{cid}",
                            window_width ,
                            cmd_func=self.change_recruit_line_produce,
                            args=(recruit_line_id ,cid)
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
                for recruit_line_id in cache.rhodes_island.recruit_line:
                    if self.now_chara_id in cache.rhodes_island.recruit_line[recruit_line_id][2]:
                        old_position = recruit_line_id
                        break
            else:
                now_select_npc_name = "未选择"

            all_info_draw = draw.NormalDraw()
            now_text = f"\n○当前的决定： 把 {now_select_npc_name} 从 {old_position + 1} 号招募调整到 {self.target_position + 1} 号招募"
            all_info_draw.text = now_text
            all_info_draw.draw()

            # 遍历全干员
            now_text = f"\n可选招募专员有：\n"
            all_info_draw.text = now_text
            all_info_draw.draw()
            flag_not_empty = False
            # 去掉玩家
            cache.npc_id_got.discard(0)
            # 去掉访客
            id_list = [i for i in cache.npc_id_got if i not in cache.rhodes_island.visitor_info]
            for chara_id in id_list:
                character_data: game_type.Character = cache.character_data[chara_id]
                # 找到职业是招募专员的
                if character_data.work.work_type == 71:
                    character_effect = 5 * attr_calculation.get_ability_adjust(character_data.ability[40])
                    button_text = f" [{character_data.name}(话术lv{character_data.ability[40]}:{round(character_effect, 1)}%)] "
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

            # 如果没有工作是招募专员的干员则输出提示
            if not flag_not_empty:
                now_text = f" 暂无工作是招募专员的干员"
                all_info_draw.text = now_text
                all_info_draw.draw()

            line_feed.draw()

            for recruit_line_id in cache.rhodes_island.recruit_line:
                now_text = f"\n {recruit_line_id+1}号招募："

                # 招募

                recruitment_strategy_id = cache.rhodes_island.recruit_line[recruit_line_id][1]
                recruitment_strategy_data = game_config.config_recruitment_strategy[recruitment_strategy_id]

                now_text += f"\n    当前招募策略：{recruitment_strategy_data.name}      "
                all_info_draw.text = now_text
                all_info_draw.draw()

                button_text = f" [选择该招募] "
                button_draw = draw.CenterButton(
                _(button_text),
                _(f"{button_text}_{recruit_line_id}"),
                int(len(button_text)*2),
                cmd_func=self.settle_assembly_line_id,
                args=recruit_line_id,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 生产效率
                now_text = f"\n    当前招募专员："
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.recruit_line[recruit_line_id][2]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = 5 * attr_calculation.get_ability_adjust(character_data.ability[40])
                    now_text += f" + {character_data.name}(话术lv{character_data.ability[40]}:{round(character_effect, 1)}%)"
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
            # 确定的话就进行id的转移结算
            elif yrn == yes_draw.return_text:
                cache.rhodes_island.recruit_line[old_position][2].discard(self.now_chara_id)
                cache.rhodes_island.recruit_line[self.target_position][2].add(self.now_chara_id)
                basement.get_base_updata()
                break

    def change_recruit_line_produce(self, asrecruit_line_id, recruitment_strategy_cid):
        """更改招募线的策略"""
        cache.rhodes_island.recruit_line[asrecruit_line_id][1] = recruitment_strategy_cid

    def settle_npc_id(self, chara_id):
        """结算干员的id变更"""
        self.now_chara_id = chara_id

    def settle_assembly_line_id(self, asrecruit_line_id):
        """结算流水线的id变更"""
        self.target_position = asrecruit_line_id
