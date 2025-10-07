from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, basement
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.UI.Panel import achievement_panel

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


def calculate_agriculture_line_efficiency(line_id: int, agriculture_type: int) -> Tuple[str, float]:
    """
    计算某条农业生产线的效率加成，并返回描述字符串和效率倍率\n
    输入:\n
        line_id: 生产线id\n
        agriculture_type: 农业类型，0药田，1温室\n
    返回:\n
        detail_str: str 描述字符串\n
        total_bonus: float 效率倍率，例如 1.25 表示125%\n
    说明:\n
        主种植员提供100%个人加成，副种植员提供20%个人加成，总加成乘以设施效率\n
    """
    ri = cache.rhodes_island
    # 设施效率（疗养庭院 facility 16）
    facility_effect = basement.calc_facility_efficiency(16)
    facility_effect_str = _("* 设施效率调整{0}%").format(round(facility_effect * 100, 1))

    # 获取主种植员与候选列表
    if agriculture_type == 0:
        # 药田
        main_id = ri.herb_garden_line.get(line_id, [0, 0, 0, 0, 0])[1]
        operator_ids = ri.herb_garden_operator_ids
        # 全部主种植员集合（仅药田）
        main_ids = {ri.herb_garden_line[i][1] if isinstance(ri.herb_garden_line[i][1], int) else 0 for i in ri.herb_garden_line}
    else:
        # 温室
        main_id = ri.green_house_line.get(line_id, [0, 0, 0, 0, 0])[1]
        operator_ids = ri.green_house_operator_ids
        # 全部主种植员集合（仅温室）
        main_ids = {ri.green_house_line[i][1] if isinstance(ri.green_house_line[i][1], int) else 0 for i in ri.green_house_line}

    # 计算主/副人员的加成
    total_bonus = 0.0
    sub_bonus = 0.0
    parts_str = "["
    # 主
    if isinstance(main_id, int) and main_id in cache.character_data and main_id != 0:
        c = cache.character_data[main_id]
        base_effect = 10 * attr_calculation.get_ability_adjust(c.ability.get(47, 0))
        total_bonus += base_effect
        parts_str += _("主:{0}(农业lv{1}:{2}%)").format(c.name, c.ability.get(47, 0), round(base_effect, 1))
    else:
        parts_str += _("主:空缺")

    # 副（不在任一主列表中的其他该岗位干员）
    for cid in operator_ids:
        if cid == 0 or cid not in cache.character_data:
            continue
        if cid == main_id:
            continue
        if cid in main_ids:
            # 已在其他生产线担任主种植员，不计入副
            continue
        c = cache.character_data[cid]
        base = 10 * attr_calculation.get_ability_adjust(c.ability.get(47, 0))
        sub_bonus += base / 5
    total_bonus += sub_bonus
    parts_str += _("，副:{0}%]").format(round(sub_bonus, 1))

    # 折算为倍率，并乘以设施效率
    # total_bonus 当前为百分比加成，转换为倍率：100%基础 + total_bonus%
    ratio = (100.0 + total_bonus) / 100.0
    ratio *= facility_effect

    detail_str = _("当前效率加成：{0} {1} = {2}%").format(parts_str, facility_effect_str, round(ratio * 100, 1))
    return detail_str, ratio

def settle_agriculture_line(draw_flag = True):
    """
    结算农业的生产
    Keyword arguments:
    draw_flag -- 是否绘制结算信息
    Return arguments:
    un_normal -- bool 是否有异常
    return_text -- str 结算信息
    """
    # print("debug 开始结算农业生产")
    # 生产是否有问题
    un_normal = False
    return_text = ""
    # 计算设施损坏
    damage_down = 0
    for facility_str in cache.rhodes_island.facility_damage_data:
        if '疗养庭院' in facility_str:
            damage_down = cache.rhodes_island.facility_damage_data[facility_str] * 2

    # 遍历药田
    for agriculture_line_id in cache.rhodes_island.herb_garden_line:
        resouce_id = cache.rhodes_island.herb_garden_line[agriculture_line_id][0]
        # print(f"debug 药田{agriculture_line_id}，种植的作物id为{resouce_id}")
        if resouce_id != 0:
            resouce_data = game_config.config_resouce[resouce_id]

            # 每天生产一次
            max_time = 10
            # 计算效率倍率（含设施效率）
            detail_str, produce_effect = calculate_agriculture_line_efficiency(agriculture_line_id, 0)
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect)
            produce_num = produce_num_max
            # print(f"debug 药田{agriculture_line_id},max_time = {max_time}，produce_effect = {produce_effect}，最大生产数为{produce_num_max}")

            # 结算实际生产
            if produce_num > 0:
                # 结算实际生产的作物
                cache.rhodes_island.materials_resouce[resouce_id] += produce_num
                cache.achievement.harvest_count += produce_num

                now_text = _("\n今日药田共生产了{0}个{1}").format(produce_num, resouce_data.name)
                # 如果有设备故障，则输出信息
                if damage_down > 0:
                    now_text += _("，由于设备故障，生产效率下降{0}%").format(damage_down)
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[resouce_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[resouce_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _("，由于仓库容量不足，{0}已达上限数量{1}").format(resouce_data.name, cache.rhodes_island.warehouse_capacity)
                    un_normal = True
                now_text += f"\n"
                return_text += now_text
                if draw_flag:
                    now_draw = draw.WaitDraw()
                    now_draw.width = window_width
                    now_draw.text = now_text
                    now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.herb_garden_line[agriculture_line_id][4] = cache.game_time.hour

    # 遍历温室
    for agriculture_line_id in cache.rhodes_island.green_house_line:
        resouce_id = cache.rhodes_island.green_house_line[agriculture_line_id][0]
        # print(f"debug 温室{agriculture_line_id}，种植的作物id为{resouce_id}")
        if resouce_id != 0:
            resouce_data = game_config.config_resouce[resouce_id]

            # 每天生产一次
            max_time = 10
            # 计算效率倍率（含设施效率）
            detail_str, produce_effect = calculate_agriculture_line_efficiency(agriculture_line_id, 1)
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect)
            produce_num = produce_num_max
            # print(f"debug 温室{agriculture_line_id},max_time = {max_time}，produce_effect = {produce_effect}，最大生产数为{produce_num_max}")

            # 结算实际生产
            if produce_num > 0:
                # 结算实际生产的产品
                cache.rhodes_island.materials_resouce[resouce_id] += produce_num
                cache.achievement.harvest_count += produce_num

                now_text = _("\n今日温室共生产了{0}个{1}").format(produce_num, resouce_data.name)
                # 如果有设备故障，则输出信息
                if damage_down > 0:
                    now_text += _("，由于设备故障，生产效率下降{0}%").format(damage_down)
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[resouce_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[resouce_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _("，由于仓库容量不足，{0}已达上限数量{1}").format(resouce_data.name, cache.rhodes_island.warehouse_capacity)
                    un_normal = True
                now_text += f"\n"
                return_text += now_text
                if draw_flag:
                    now_draw = draw.WaitDraw()
                    now_draw.width = window_width
                    now_draw.text = now_text
                    now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.green_house_line[agriculture_line_id][4] = cache.game_time.hour

    # 结算成就
    achievement_panel.achievement_flow(_("种植"))

    return un_normal, return_text


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
            basement.get_base_updata()
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = ""
            now_text += _(" 当前仓库等级：{0}，容量（单资源存放上限）：{1}\n").format(cache.rhodes_island.facility_level[3], cache.rhodes_island.warehouse_capacity)

            # 遍历该类型的资源
            for material_id in [11, 16]:
                material_data  = game_config.config_resouce[material_id]
                now_text += f"  {material_data.name}：{cache.rhodes_island.materials_resouce[material_id]}"
            now_text += "\n"

            all_info_draw.text = now_text
            all_info_draw.draw()

            for agriculture_line_id in cache.rhodes_island.herb_garden_line:
                now_text = _("\n 药田：")
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 基础数据
                resouce_id = cache.rhodes_island.herb_garden_line[agriculture_line_id][0]
                resouce_data = game_config.config_resouce[resouce_id]
                # 生产效率
                detail_str, produce_effect = calculate_agriculture_line_efficiency(agriculture_line_id, 0)
                new_produce_value = int(10 * produce_effect)

                # 生产产品
                now_text = _("\n    当前生产：{0}").format(resouce_data.name)
                now_text += ("({0}/d)      ").format(new_produce_value)
                all_info_draw.text = now_text
                all_info_draw.draw()
                button_text = _(" [生产调整] ")
                button_draw = draw.CenterButton(
                    _(button_text),
                    _("{0}_药田_{1}").format(button_text, agriculture_line_id),
                    len(button_text) * 2,
                    cmd_func=self.select_agriculture_line_produce,
                    args = (agriculture_line_id, 0)
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()

                # 生产效率绘制
                all_info_draw.text = "    " + detail_str
                all_info_draw.draw()
                line_feed.draw()

            # 已开放温室再显示温室的生产情况
            if cache.rhodes_island.facility_open[71]:
                for agriculture_line_id in cache.rhodes_island.green_house_line:
                    now_text = _("\n 温室：")
                    all_info_draw.text = now_text
                    all_info_draw.draw()

                    # 基础数据
                    resouce_id = cache.rhodes_island.green_house_line[agriculture_line_id][0]
                    resouce_data = game_config.config_resouce[resouce_id]
                    # 生产效率
                    detail_str, produce_effect = calculate_agriculture_line_efficiency(agriculture_line_id, 1)
                    new_produce_value = int(10 * produce_effect)


                    # 生产产品
                    now_text = _("\n    当前生产：{0}").format(resouce_data.name)
                    now_text += ("({0}/d)      ").format(new_produce_value)
                    all_info_draw.text = now_text
                    all_info_draw.draw()
                    button_text = _(" [生产调整] ")
                    button_draw = draw.CenterButton(
                        _(button_text),
                        _("{0}_温室_{1}").format(button_text, agriculture_line_id),
                        len(button_text) * 2,
                        cmd_func=self.select_agriculture_line_produce,
                        args = (agriculture_line_id, 1)
                        )
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()

                    all_info_draw.text = "    " + detail_str
                    all_info_draw.draw()
                    line_feed.draw()

            line_feed.draw()
            button_text = _("[001]种植员管理")
            button_draw = draw.LeftButton(
                _(button_text),
                _(button_text),
                self.width,
                cmd_func=self.select_agri_position,
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
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_agri_position(self):
        """种植员管理(任命各线主种植员)"""
        ri = cache.rhodes_island
        from Script.UI.Panel import manage_basement_panel
        while 1:
            basement.update_work_people()
            title = draw.TitleLineDraw(_("种植员管理"), self.width)
            title.draw()
            return_list = []

            info = draw.NormalDraw()
            info.text = _("当前药田种植员数量：{0}，温室种植员数量：{1}").format(len(ri.herb_garden_operator_ids), len(ri.green_house_operator_ids))
            info.text += "      "
            info.draw()

            # 增减按钮
            button_text = _("[种植员增减]")
            button_draw = draw.CenterButton(
                _(button_text),
                _(button_text),
                len(button_text) * 2 + 2,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=self.width
            )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw(); line_feed.draw()

            # 药田各线任命
            for line_id in ri.herb_garden_line:
                main_id = ri.herb_garden_line[line_id][1]
                name = cache.character_data[main_id].name if main_id != 0 and main_id in cache.character_data else _("(空缺)")
                row = draw.NormalDraw()
                row.text = _("药田{0}号线 主种植员: {1}  ").format(line_id+1, name)
                row.draw()
                def _make(idx):
                    return lambda : self._appoint_main_agri(idx, 0)
                btn = draw.CenterButton(_("[任命]"), _("任命")+str(line_id+1)+_("药田主种植员"), 12, cmd_func=_make(line_id))
                btn.draw(); return_list.append(btn.return_text)
                line_feed.draw()
            line_feed.draw()

            # 药田副种植员
            main_ids = {ri.herb_garden_line[i][1] for i in ri.herb_garden_line}
            other_ops = [cid for cid in ri.herb_garden_operator_ids if cid not in main_ids]
            other_draw = draw.NormalDraw()
            if other_ops:
                names = [cache.character_data[cid].name for cid in other_ops if cid in cache.character_data]
                other_draw.text = _("药田副种植员：") + "、".join(names) + "\n"
            else:
                other_draw.text = _("药田副种植员：暂无\n")
            other_draw.draw()
            line_feed.draw(); line_feed.draw()

            # 温室（仅开放后显示）
            if cache.rhodes_island.facility_open.get(71, False):
                for line_id in ri.green_house_line:
                    main_id = ri.green_house_line[line_id][1]
                    name = cache.character_data[main_id].name if main_id != 0 and main_id in cache.character_data else _("(空缺)")
                    row = draw.NormalDraw()
                    row.text = _("温室{0}号线 主种植员: {1}  ").format(line_id+1, name)
                    row.draw()
                    def _make2(idx):
                        return lambda : self._appoint_main_agri(idx, 1)
                    btn = draw.CenterButton(_("[任命]"), _("任命温室主种植员")+str(line_id+1), 12, cmd_func=_make2(line_id))
                    btn.draw(); return_list.append(btn.return_text)
                    line_feed.draw()
                line_feed.draw()

                main_ids = {ri.green_house_line[i][1] for i in ri.green_house_line}
                other_ops = [cid for cid in ri.green_house_operator_ids if cid not in main_ids]
                other_draw = draw.NormalDraw()
                if other_ops:
                    names = [cache.character_data[cid].name for cid in other_ops if cid in cache.character_data]
                    other_draw.text = _("温室副种植员：") + "、".join(names) + "\n"
                else:
                    other_draw.text = _("温室副种植员：暂无\n")
                other_draw.draw()
                line_feed.draw(); line_feed.draw()

            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _appoint_main_agri(self, line_id: int, agriculture_type: int):
        """任命某条农业线主种植员(重复选择同一人可撤销)"""
        from Script.UI.Panel import common_select_NPC
        ri = cache.rhodes_island
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, True, False, 0)
        select_state = {}
        def _make(chara_id):
            self._do_appoint_main_agri(line_id, agriculture_type, chara_id)
        while 1:
            if agriculture_type == 0:
                op_list = ri.herb_garden_operator_ids
                now_main = ri.herb_garden_line[line_id][1]
                type_name = _("药田")
            else:
                op_list = ri.green_house_operator_ids
                now_main = ri.green_house_line[line_id][1]
                type_name = _("温室")
            info_text = _("请选择一名种植员担任{0}{1}号线主种植员:\n").format(type_name, line_id+1)
            final_list = []
            for npc_id in op_list:
                if npc_id == 0:
                    continue
                final_list.append([npc_id, _make, [now_main]])
            now_draw_panel.text_list = final_list
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("任命主种植员"), info_text, select_state)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def _do_appoint_main_agri(self, line_id: int, agriculture_type: int, chara_id: int):
        ri = cache.rhodes_island
        if agriculture_type == 0:
            if chara_id not in ri.herb_garden_operator_ids:
                return
            # 撤销/任命
            if ri.herb_garden_line[line_id][1] == chara_id:
                ri.herb_garden_line[line_id][1] = 0
            else:
                for lid in ri.herb_garden_line:
                    if lid != line_id and ri.herb_garden_line[lid][1] == chara_id:
                        ri.herb_garden_line[lid][1] = 0
                ri.herb_garden_line[line_id][1] = chara_id
        else:
            if chara_id not in ri.green_house_operator_ids:
                return
            if ri.green_house_line[line_id][1] == chara_id:
                ri.green_house_line[line_id][1] = 0
            else:
                for lid in ri.green_house_line:
                    if lid != line_id and ri.green_house_line[lid][1] == chara_id:
                        ri.green_house_line[lid][1] = 0
                ri.green_house_line[line_id][1] = chara_id

    def select_agriculture_line_produce(self, agriculture_line_id, agriculture_type):
        """
        选择生产的资源\n
        agriculture_line_id: int 生产线id\n
        agriculture_type: int 农业类型，0药田，1温室\n
        """
        if agriculture_type == 0:
            resouce_id_list = [11]
        elif agriculture_type == 1:
            resouce_id_list = [16]
        while 1:

                line = draw.LineDraw("-", window_width)
                line.draw()
                info_draw = draw.NormalDraw()
                return_list = []

                # now_level = cache.rhodes_island.facility_level[16]
                resouce_id = cache.rhodes_island.herb_garden_line[agriculture_line_id][0]
                resouce_data = game_config.config_resouce[resouce_id]

                info_text = f""
                info_text += _(" 当前种植的是：{0}").format(resouce_data.name)

                info_text += _("\n\n 当前可以种植的有：\n\n")
                info_draw.text = info_text
                info_draw.draw()

                # 遍历配方列表，获取每个配方的信息
                for cid in resouce_id_list:
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
                            args=(agriculture_line_id ,cid, agriculture_type)
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

    def change_agriculture_line_produce(self, agriculture_line_id, formula_cid, agriculture_type):
        """更改农产品的种植"""
        if agriculture_type == 0:
            if cache.rhodes_island.herb_garden_line[agriculture_line_id][0] != 0 and cache.rhodes_island.herb_garden_line[agriculture_line_id][4] != cache.game_time.hour:
                pass
            else:
                cache.rhodes_island.herb_garden_line[agriculture_line_id][0] = formula_cid
        elif agriculture_type == 1:
            if cache.rhodes_island.green_house_line[agriculture_line_id][0] != 0 and cache.rhodes_island.green_house_line[agriculture_line_id][4] != cache.game_time.hour:
                pass
            else:
                cache.rhodes_island.green_house_line[agriculture_line_id][0] = formula_cid
