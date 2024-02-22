from turtle import position
from typing import Tuple
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import attr_calculation, handle_premise
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

import random

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

def common_ejaculation():
    """
    通用射精结算
    return
    semen_text 射精文本
    semen_count 射精量
    """
    character_data: game_type.Character = cache.character_data[0]

    # 乘以一个随机数补正
    random_weight = random.uniform(0.5, 1.5)

    # 如果已经没有精液了，则不射精
    if character_data.semen_point <= 1:
        return "只流出了些许前列腺液，已经射不出精液了",0
    else:
        # 基础射精值，小中多射精区分
        if character_data.h_state.orgasm_level[3] % 3 == 0:
            semen_count = int(5 * random_weight)
            semen_text = "射精，射出了" + str(semen_count) + "ml精液"
        if character_data.h_state.orgasm_level[3] % 3 == 1:
            semen_count = int(20 * random_weight)
            semen_text = "大量射精，射出了" + str(semen_count) + "ml精液"
        if character_data.h_state.orgasm_level[3] % 3 == 2:
            semen_count = int(40 * random_weight)
            semen_text = "超大量射精，射出了" + str(semen_count) + "ml精液"

        # 更新射精计数
        character_data.h_state.orgasm_level[3] += 1

        # 更新精液值
        if semen_count > character_data.semen_point:
            semen_count = character_data.semen_point
        character_data.semen_point -= semen_count
        cache.rhodes_island.total_semen_count += semen_count

        return semen_text,semen_count


class Ejaculation_Panel:
    """
    用于显示射精界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("身体")
        """ 当前绘制的射精页面 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        title_name = "射精部位选择"
        title_draw = draw.TitleLineDraw(title_name, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 绘制身体部位按钮
            for body_part_cid in game_config.config_body_part:
                part_name = game_config.config_body_part[body_part_cid].name
                draw_text = f"[{body_part_cid} {part_name}]"
                # print("debug draw_text = ",draw_text)
                show_flag = self.part_can_choose(body_part_cid)
                if show_flag:
                    name_draw = draw.CenterButton(
                        draw_text, part_name, (len(draw_text) + 1) * 2, cmd_func=self.shoot_here, args=(body_part_cid, 0)
                    )
                    name_draw.draw()
                    return_list.append(name_draw.return_text)

            line_feed.draw()

            # 绘制服装部位按钮
            for clothing_type in game_config.config_clothing_type:
                cloth_name = game_config.config_clothing_type[clothing_type].name
                draw_text = f"[{clothing_type} {cloth_name}]"
                show_flag = len(target_data.cloth.cloth_wear[clothing_type])
                if show_flag:
                    name_draw = draw.CenterButton(
                        draw_text, cloth_name, (len(draw_text) + 1) * 2, cmd_func=self.shoot_here, args=(clothing_type, 1)
                    )
                    name_draw.draw()
                    return_list.append(name_draw.return_text)

            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn not in ['身体', '服装']:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def part_can_choose(self, body_part_cid: int):
        """判断该部位是否可以绘制"""

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        # 身体部位所对应的服装部位，-1表示无对应部位，列表表示多个对应部位
        body_cloth = [0, 4, 4, [5, 6], 5, 7, -1, -1, -1, -1, [8, 10], 11, -1, -1, -1, -1, [8, 9], 8, 5]
        clothing = {}

        for clothing_type in game_config.config_clothing_type:
            if len(target_data.cloth.cloth_wear[clothing_type]):
                clothing[clothing_type] = target_data.cloth.cloth_wear[clothing_type]

        # 不插在对应部位，则无法射在对应部位
        if body_part_cid == 6 and not handle_premise.handle_last_cmd_sex(0):
            return False
        elif body_part_cid == 7 and not handle_premise.handle_last_cmd_w_sex(0):
            return False
        elif body_part_cid == 8 and not handle_premise.handle_last_cmd_a_sex(0):
            return False
        elif body_part_cid == 9 and not handle_premise.handle_last_cmd_u_sex(0):
            return False
        elif body_part_cid == 15:
            return False
        # 没有长对应器官，则无法射在对应部位
        elif body_part_cid == 12 and not target_data.talent[113]:
            return False
        elif body_part_cid == 13 and not target_data.talent[112]:
            return False
        elif body_part_cid == 14 and not target_data.talent[111]:
            return False
        # 对应部位有衣服，则无法射在对应部位
        if isinstance(body_cloth[body_part_cid], list):
            def cloth_list(bbc):
                for bc in bbc:
                    if bc in clothing.keys():
                        return False
                return True
            if not cloth_list(body_cloth[body_part_cid]):
                return False
        else:
            if body_cloth[body_part_cid] in clothing.keys():
                return False
        return True

    def shoot_here(self, part_cid: int, part_type: int):
        py_cmd.clr_cmd()

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        cache.shoot_position = part_cid

        semen_text, semen_count = common_ejaculation()

        if part_type == 0:

            part_name = game_config.config_body_part[part_cid].name
            now_text = "在" + target_data.name + "的" + part_name+ semen_text

            # 记录射精部位
            target_data.h_state.shoot_position_body = part_cid

            # 更新污浊类里的身体部位精液参数
            if part_cid == 6:
                target_data.dirty.body_semen[part_cid][1] += 1
                part_cid = 7
            target_data.dirty.body_semen[part_cid][1] += semen_count
            target_data.dirty.body_semen[part_cid][3] += semen_count
            target_data.dirty.body_semen[part_cid][2] = attr_calculation.get_semen_now_level(target_data.dirty.body_semen[part_cid][1], part_cid, 0)

        elif part_type == 1:

            # 记录射精部位
            target_data.h_state.shoot_position_cloth = part_cid

            # 更新污浊类里的服装部位精液参数
            target_data.dirty.cloth_semen[part_cid][1] += semen_count
            target_data.dirty.cloth_semen[part_cid][3] += semen_count
            target_data.dirty.cloth_semen[part_cid][2] = attr_calculation.get_semen_now_level(
                target_data.dirty.cloth_semen[part_cid][1], part_cid, 1)

            cloth_text = game_config.config_clothing_type[part_cid].name
            now_text = "在" + target_data.name + "的" + cloth_text + semen_text

        line_feed.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        line_feed.draw()
        now_draw = draw.WaitDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()
        line_feed.draw()
        line_feed.draw()
