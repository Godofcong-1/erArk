from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.Design import update, character

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


class Aromatherapy_Panel:
    """
    用于香薰疗愈的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("香薰疗愈")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.now_choice_recipe_id = 0
        """ 当前选择的配方id """

    def draw(self):
        """绘制对象"""

        title_text = _("香薰疗愈")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        pl_character_data = cache.character_data[0]
        target_character_data = cache.character_data[pl_character_data.target_character_id]

        while 1:
            return_list = []
            title_draw.draw()

            # 绘制交易信息
            all_info_draw = draw.NormalDraw()
            all_info_draw.width = self.width

            now_text = ""
            now_text += _(f"\n！实装中！\n")
            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()

            # 剩余调香次数
            now_text = ""
            now_text += _(f"\n  今日剩余调香次数    ：  {cache.rhodes_island.remaining_aromatherapy_sessions_today}次")
            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()

            # 当前调香对象
            now_text = ""
            now_text += _(f"\n  当前调香对象        ：  {target_character_data.name}")
            # 判断对方今日是否已调香
            if target_character_data.sp_flag.aromatherapy != 0:
                # 输出调香状态
                now_text += _(f"(今日已调香-{game_config.config_aromatherapy_recipes[target_character_data.sp_flag.aromatherapy].name})")
            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()

            # 资源信息
            now_text = ""
            now_text += _(f"\n  当前调香资源        ：")
            for recipes_id in cache.rhodes_island.materials_resouce:
                recipes_data  = game_config.config_resouce[recipes_id]
                if recipes_data.name == _("香料") or recipes_data.type == _("香水"):
                    now_text += f"  {recipes_data.name}：{cache.rhodes_island.materials_resouce[recipes_id]}"
            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()

            # 当前配方
            now_text = ""
            now_text += _(f"\n  当前选择的调香配方  ：")
            now_text += _(f"  {game_config.config_aromatherapy_recipes[self.now_choice_recipe_id].name}")
            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()
            line_feed.draw()

            button_text = _(" [001]选择配方 ")
            button_draw = draw.CenterButton(
                _(button_text),
                _("1"),
                len(button_text) * 2,
                cmd_func=self.select_recipe,
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()

            line_feed.draw()
            line_feed.draw()
            yes_draw = draw.CenterButton(_("[确定]"), _("确定"), window_width / 2)
            # 判断是否可以进行调香，需要已选择配方，有剩余调香次数，对方今日未调香
            yes_show_flag = False
            if (
                self.now_choice_recipe_id != 0 and
                cache.rhodes_island.remaining_aromatherapy_sessions_today > 0 and
                target_character_data.sp_flag.aromatherapy == 0
                ):
                yes_show_flag = True
            if yes_show_flag:
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width / 2)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break
            elif yrn == yes_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                self.run_aromatherapy()
                break

    def select_recipe(self):
        """选择配方"""
        while 1:
            line = draw.LineDraw("-", window_width)
            line.draw()
            all_info_draw = draw.NormalDraw()
            all_info_draw.width = self.width
            return_list = []

            now_text = ""
            now_text += _(f"\n\n当前可选的配方有：\n")
            all_info_draw.text = now_text
            all_info_draw.draw()

            for recipes_id in game_config.config_aromatherapy_recipes:
                recipes_data = game_config.config_aromatherapy_recipes[recipes_id]
                if recipes_id == 0:
                    continue
                # 判断当前配方是否可以生产，未解锁则跳过
                flag_open = True
                # now_level = 1
                # if recipes_data.difficulty > now_level:
                #     flag_open = False
                # 可以生产的话则输出
                if flag_open:
                    line_feed.draw()
                    button_draw = draw.LeftButton(
                        f"[{str(recipes_id).rjust(3,'0')}]{recipes_data.name}：{recipes_data.info}",
                        f"\n{recipes_id}",
                        window_width ,
                        cmd_func=self.change_now_choice_recipe_id,
                        args=(recipes_id)
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

                    formula_text = recipes_data.formula
                    now_text = _(f"\n     调香消耗：")
                    # 以&为分割判定是否有多个需求
                    if "&" not in formula_text:
                        need_list = []
                        need_list.append(formula_text)
                    else:
                        need_list = formula_text.split('&')
                    for need_text in need_list:
                        need_type = int(need_text.split('|')[0])
                        need_value = int(need_text.split('|')[1])
                        now_text += f"  {game_config.config_resouce[need_type].name}：{need_value}"

                    all_info_draw.text = now_text
                    all_info_draw.draw()
                    line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def change_now_choice_recipe_id(self, recipe_id):
        """更改当前选择的配方id"""
        self.now_choice_recipe_id = recipe_id

    def run_aromatherapy(self):
        """进行调香"""
        # 检查是否有足够的资源
        recipes_data = game_config.config_aromatherapy_recipes[self.now_choice_recipe_id]
        formula_text = recipes_data.formula
        # 以&为分割判定是否有多个需求
        if "&" not in formula_text:
            need_list = []
            need_list.append(formula_text)
        else:
            need_list = formula_text.split('&')
        flag = True
        for need_text in need_list:
            need_type = int(need_text.split('|')[0])
            need_value = int(need_text.split('|')[1])
            if cache.rhodes_island.materials_resouce[need_type] < need_value:
                flag = False
                break
        if flag:
            # 消耗资源
            for need_text in need_list:
                need_type = int(need_text.split('|')[0])
                need_value = int(need_text.split('|')[1])
                cache.rhodes_island.materials_resouce[need_type] -= need_value
            # 减少调香次数
            cache.rhodes_island.remaining_aromatherapy_sessions_today -= 1
            # 对方施加调香效果
            pl_character_data = cache.character_data[0]
            target_character_data = cache.character_data[pl_character_data.target_character_id]
            target_character_data.sp_flag.aromatherapy = self.now_choice_recipe_id
            # 行动时间
            cost_time = 60
            character.init_character_behavior_start_time(0, cache.game_time)
            pl_character_data.behavior.duration = cost_time
            # 根据序号获得对应的状态
            aromatherapy_dict = {
                1: (constant.Behavior.AROMATHERAPY_1, constant.CharacterStatus.STATUS_AROMATHERAPY_1),
                2: (constant.Behavior.AROMATHERAPY_2, constant.CharacterStatus.STATUS_AROMATHERAPY_2),
                3: (constant.Behavior.AROMATHERAPY_3, constant.CharacterStatus.STATUS_AROMATHERAPY_3),
                4: (constant.Behavior.AROMATHERAPY_4, constant.CharacterStatus.STATUS_AROMATHERAPY_4),
                5: (constant.Behavior.AROMATHERAPY_5, constant.CharacterStatus.STATUS_AROMATHERAPY_5),
            }
            if self.now_choice_recipe_id in aromatherapy_dict:
                pl_character_data.behavior.behavior_id, pl_character_data.state = aromatherapy_dict[self.now_choice_recipe_id]
            # 对方停止并等待同样的时间
            character.init_character_behavior_start_time(pl_character_data.target_character_id, cache.game_time)
            target_character_data.target_character_id = pl_character_data.target_character_id
            target_character_data.behavior.behavior_id = constant.Behavior.WAIT
            target_character_data.behavior.duration = cost_time
            target_character_data.state = constant.CharacterStatus.STATUS_WAIT
            # 更新游戏时间
            update.game_update_flow(cost_time)
