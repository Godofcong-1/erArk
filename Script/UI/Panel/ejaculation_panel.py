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
    通用射精结算，进行一次射精，并返回射精文本和射精量
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

        # 更新射精计数和总精液量
        character_data.h_state.orgasm_level[3] += 1
        cache.rhodes_island.total_semen_count += semen_count

        # # 更新精液值，目前弃用
        # if semen_count > character_data.semen_point:
        #     semen_count = character_data.semen_point

        # 优先扣除临时额外精液值，不够的再扣除基础精液值
        if character_data.tem_extra_semen_point > semen_count:
            character_data.tem_extra_semen_point -= semen_count
        else:
            semen_count -= character_data.tem_extra_semen_point
            character_data.tem_extra_semen_point = 0
        character_data.semen_point -= semen_count
        character_data.semen_point = max(0, character_data.semen_point)

        return semen_text,semen_count


def update_semen_dirty(character_id: int, part_cid: int, part_type: int, semen_count: int, update_shoot_position_flag: bool = True):
    """
    更新部位的被射精污浊数据
    Keyword arguments:
    character_id -- 角色id
    part_cid -- 部位cid
    part_type -- 部位类型
    semen_count -- 精液量
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 判断部位类型，0为身体部位，1为服装部位
    if part_type == 0:
        # 更新身体部位被射精污浊数据
        character_data.dirty.body_semen[part_cid][1] += semen_count
        character_data.dirty.body_semen[part_cid][1] = max(character_data.dirty.body_semen[part_cid][1], 0)
        if semen_count > 0:
            character_data.dirty.body_semen[part_cid][3] += semen_count
        character_data.dirty.body_semen[part_cid][2] = attr_calculation.get_semen_now_level(character_data.dirty.body_semen[part_cid][1], part_cid, 0)
        # 记录射精部位
        if update_shoot_position_flag:
            character_data.h_state.shoot_position_body = part_cid
    elif part_type == 1:
        character_data.dirty.cloth_semen[part_cid][1] += semen_count
        character_data.dirty.cloth_semen[part_cid][1] = max(character_data.dirty.cloth_semen[part_cid][1], 0)
        if semen_count > 0:
            character_data.dirty.cloth_semen[part_cid][3] += semen_count
        character_data.dirty.cloth_semen[part_cid][2] = attr_calculation.get_semen_now_level(character_data.dirty.cloth_semen[part_cid][1], part_cid, 1)
        if update_shoot_position_flag:
            character_data.h_state.shoot_position_cloth = part_cid


def calculate_semen_flow(character_id: int, part_cid: int, part_type: int, semen_count: int):
    """
    计算精液流动
    Keyword arguments:
    character_id -- 角色id
    part_cid -- 部位cid
    part_type -- 部位类型
    semen_count -- 精液量
    """
    if character_id != 0:
        character_data: game_type.Character = cache.character_data[character_id]
        # 创建精液流通情况字典
        all_flow_dict = {}
        all_flow_dict["source"] = {"type": part_type, "id": part_cid}
        all_flow_dict["target"] = []

        # 判断部位类型，0为身体部位，1为服装部位
        if part_type == 0:
            # 判断是否满溢
            voluem_data_list = game_config.config_body_part_volume[part_cid]
            # 满溢时使用满溢流动表
            if character_data.dirty.body_semen[part_cid][1] > voluem_data_list[-1]:
                flow_list = game_config.config_body_part_full_flow[part_cid]
            # 未满溢时使用正常流动表
            else:
                flow_list = game_config.config_body_part_normal_flow[part_cid]
            # 遍历流动表，计算应该向各部位流动多少，添加到精液流通情况字典中
            for flow_str in flow_list:
                # 获取流动类型，部位cid，流动比例
                flow_type = flow_str[0]
                flow_cid = int(flow_str[1:].split("-")[0])
                flow_rate = int(flow_str[1:].split("-")[1])
                # 创建流动情况字典
                now_flow_dict = {}
                # 判断流动类型，0为身体部位，1为服装部位，2为环境滴落
                if flow_type == "B":
                    now_flow_dict["type"] = 0
                elif flow_type == "C":
                    now_flow_dict["type"] = 1
                elif flow_type == "E":
                    now_flow_dict["type"] = 2
                # 添加流动目标部位cid和流动量
                now_flow_dict["id"] = flow_cid
                now_flow_dict["remaining_volume"] = max(1, int(semen_count * flow_rate / 100))
                # 添加到精液流通情况字典中
                all_flow_dict["target"].append(now_flow_dict)
        elif part_type == 1:
            return 0
        # 添加到目标角色的精液流通情况列表中
        character_data.dirty.semen_flow.append(all_flow_dict)


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

        # 如果没有选择射精部位，则直接在当前阴茎位置射精
        if not cache.system_setting.choose_shoot_where:
            now_position = target_data.h_state.insert_position
            self.shoot_here(now_position, 0)
        # 手动选择射精部位
        else:
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

        # 更新被射精污浊数据
        update_semen_dirty(character_data.target_character_id, part_cid, part_type, semen_count)

        # 计算精液流动
        calculate_semen_flow(character_data.target_character_id, part_cid, part_type, semen_count)

        # 获取射精文本
        if part_type == 0:
            part_name = game_config.config_body_part[part_cid].name
            now_text = "在" + target_data.name + "的" + part_name+ semen_text
        elif part_type == 1:
            cloth_text = game_config.config_clothing_type[part_cid].name
            now_text = "在" + target_data.name + "的" + cloth_text + semen_text

        # 绘制射精文本
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
