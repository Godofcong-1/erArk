from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, basement, handle_ability
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


def calculate_assembly_line_efficiency(line_id:int) -> Tuple[str, float]:
    """
    计算某条生产线当前总效率(百分比值), 同时更新缓存结构中 index2
    输入参数:
    line_id -- 流水线id
    输出参数:
    流水线效率(百分比值, 例如 123.5)
    """
    ri = cache.rhodes_island
    if line_id not in ri.assembly_line:
        return _("无此生产线"), 0.0
    # 设施效率(返回例如 1.15)
    facility_effect_ratio = basement.calc_facility_efficiency(12)
    facility_effect_str = _("* 设施效率调整{0}%").format(round((facility_effect_ratio)*100,1))
    base = facility_effect_ratio * 100
    # 如果不是int，则转为0
    if not isinstance(ri.assembly_line[line_id][1], (int)):
        ri.assembly_line[line_id][1] = 0
    line_main_id = ri.assembly_line[line_id][1]
    # 收集全部主生产工人，防止副工人重复计入
    main_ids = {ri.assembly_line[lid][1] for lid in ri.assembly_line if isinstance(ri.assembly_line[lid][1], int)}
    total = base
    sub_bonus = 0.0
    # 主工人加成
    worker_str = "["
    if line_main_id in cache.character_data and line_main_id != 0:
        char_data: game_type.Character = cache.character_data[line_main_id]
        main_bonus = 10 * handle_ability.get_ability_adjust(char_data.ability[48])
        total += main_bonus
        worker_str = _("主:{0}(制造lv{1}:{2}%)").format(char_data.name, char_data.ability[48], round(main_bonus,1))
    else:
        worker_str += _("主:空缺")
    # 副工人加成
    for cid in ri.production_worker_ids:
        if cid == 0 or cid not in cache.character_data:
            continue
        if cid in main_ids:
            continue
        char_data: game_type.Character = cache.character_data[cid]
        base_effect = 2 * handle_ability.get_ability_adjust(char_data.ability.get(48,0))
        sub_bonus += base_effect
    total += sub_bonus
    worker_str += _("，副:{0}%]").format(round(sub_bonus,1))
    # 写回
    ri.assembly_line[line_id][2] = round(total,2)
    detail_str = _("当前效率加成：{0} {1} = {2}%").format(worker_str, facility_effect_str, round(total,1))
    return detail_str, ri.assembly_line[line_id][2]


def settle_assembly_line(newdayflag = False, draw_flag = True):
    """
    结算流水线的生产\n
    Keyword arguments:\n
    newdayflag -- 是否是新的一天\n
    draw_flag -- 是否绘制结算信息\n
    Return arguments:\n
    un_normal -- 是否有异常\n
    return_text -- 结算信息\n
    """

    # 生产是否有问题
    un_normal = False
    return_text = "\n"

    # 新一天的时候输出提示
    if newdayflag and draw_flag:
        return_text += _("○制造加工部结算：\n")

    # 计算设施损坏
    damage_down = 0
    for facility_str in cache.rhodes_island.facility_damage_data:
        if '制造加工' in facility_str:
            damage_down = cache.rhodes_island.facility_damage_data[facility_str] * 2

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
            # 生产效率(动态计算)
            detail_str, produce_effect = calculate_assembly_line_efficiency(assembly_line_id)
            produce_effect = produce_effect / 100
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect)
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
                cache.achievement.production_count += produce_num

                now_text = _("\n 流水线{0}:").format(assembly_line_id)
                now_text += _("上次结算是{0}时，到现在已过{1}小时，").format(cache.rhodes_island.assembly_line[assembly_line_id][4], max_time)
                # 如果有设备故障，则输出信息
                if damage_down > 0:
                    now_text += _("由于设备故障，生产效率下降{0}%，").format(damage_down)
                if produce_num < produce_num_max:
                    now_text += _("由于原料不足，最大可以生产{0}个，实际").format(produce_num)
                    un_normal = True
                now_text += _("共生产了{0}个{1}").format(produce_num, game_config.config_resouce[product_id].name)
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[product_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[product_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _("，由于仓库容量不足，{0}已达上限数量{1}").format(game_config.config_resouce[product_id].name, cache.rhodes_island.warehouse_capacity)
                    un_normal = True
                now_text += f"\n"
                return_text += now_text
                if draw_flag:
                    now_draw = draw.WaitDraw()
                    now_draw.width = window_width
                    now_draw.text = now_text
                    now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.assembly_line[assembly_line_id][4] = cache.game_time.hour
    # 结算成就
    achievement_panel.achievement_flow(_("生产"))

    return un_normal, return_text


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
        self.show_resource_type_dict: Dict = {_("药剂"): False, _("乳制品"): False, _("香水"): False, _("基建"): False}

    def draw(self):
        """绘制对象"""
        title_text = _("产品生产")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        settle_assembly_line(draw_flag=False)

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = _(" 当前仓库等级：{0}，容量（单资源存放上限）：{1}\n").format(cache.rhodes_island.facility_level[3], cache.rhodes_island.warehouse_capacity)

            # 遍历全资源类型
            self.resouce_list = [_("材料"), _("药剂"), _("乳制品"), _("香水"), _("基建")]
            for resouce in self.resouce_list:
                now_text += f"\n {attr_calculation.pad_display_width(resouce, 8)}："
                # 遍历该类型的资源
                for material_id in cache.rhodes_island.materials_resouce:
                    material_data  = game_config.config_resouce[material_id]
                    if material_data.type == resouce:
                        now_text += f"  {material_data.name}：{cache.rhodes_island.materials_resouce[material_id]}"

            all_info_draw.text = now_text
            all_info_draw.draw()
            line_feed.draw()
            line_feed.draw()

            for assembly_line_id in cache.rhodes_island.assembly_line:
                now_text = _("\n {0}号流水线：").format(assembly_line_id+1)
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 基础数据
                formula_id = cache.rhodes_island.assembly_line[assembly_line_id][0]
                formula_data = game_config.config_productformula[formula_id]
                product_id = formula_data.product_id
                product_data = game_config.config_resouce[product_id]

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
                line_feed.draw()

                # 生产效率展示
                detail_str, total_eff = calculate_assembly_line_efficiency(assembly_line_id)
                all_info_draw.text = "    " + detail_str
                all_info_draw.draw()

                # 生产消耗
                now_text = _("\n    当前生产消耗：")
                formula_text = formula_data.formula
                # 以&为分割判定是否有多个需求
                if "&" not in formula_text:
                    need_list = [formula_text]
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
            # 管理按钮
            button_text = _("[001]生产工人管理")
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

    def select_npc_position(self):
        """生产工人管理(任命各线主生产工人 & 管理副工人列表)"""
        ri = cache.rhodes_island
        from Script.UI.Panel import manage_basement_panel
        while 1:
            # 刷新一下
            basement.update_work_people()
            title = draw.TitleLineDraw(_("生产工人管理"), self.width)
            title.draw()
            return_list = []

            # 提示信息
            info = draw.NormalDraw()
            info.text = _("当前生产工人数量：{0}").format(len(ri.production_worker_ids))
            info.text += "      "
            info.draw()

            # 生产工人增减按钮
            button_text = _("[生产工人增减]")
            btn = draw.CenterButton(
                _(button_text),
                _(button_text),
                len(button_text)*2+2,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=(self.width, [121])
                )
            btn.draw(); return_list.append(btn.return_text)
            line_feed.draw(); line_feed.draw()

            # 各生产线主生产工人显示与任命按钮
            for line_id in ri.assembly_line:
                main_id = ri.assembly_line[line_id][1]
                name = cache.character_data[main_id].name if main_id != 0 else _("(空缺)")
                row = draw.NormalDraw()
                row.text = _("{0}号生产线 主生产工人: {1}  ").format(line_id+1, name)
                row.draw()
                def _make(lid):
                    return lambda : self._appoint_main_worker(lid)
                appoint_btn = draw.CenterButton(_("[任命]"), _("任命")+str(line_id+1), 12, cmd_func=_make(line_id))
                appoint_btn.draw(); return_list.append(appoint_btn.return_text)
                line_feed.draw()
                line_feed.draw()
            line_feed.draw()

            # 显示所有副生产工人
            main_ids = {ri.assembly_line[i][1] for i in ri.assembly_line}
            others = [cid for cid in ri.production_worker_ids if cid not in main_ids and cid in cache.character_data]
            other_draw = draw.NormalDraw()
            other_draw.text = _("副生产工人：") + ("、".join([cache.character_data[c].name for c in others]) if others else _("暂无")) + "\n"
            other_draw.draw()
            line_feed.draw(); line_feed.draw()

            # 返回按钮
            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _appoint_main_worker(self, line_id:int):
        """任命主生产工人(重复选择撤销)"""
        ri = cache.rhodes_island
        from Script.UI.Panel import common_select_NPC
        now_panel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50,5, window_width, True, False, 0)
        select_state = {}
        def _handler(chara_id):
            if chara_id not in ri.production_worker_ids:
                return
            # 选择了当前主生产工人则撤销，否则任命
            if ri.assembly_line[line_id][1] == chara_id:
                ri.assembly_line[line_id][1] = 0
            else:
                # 如果该工人在其它线已是主生产工人则先撤销
                for lid in ri.assembly_line:
                    if lid != line_id and ri.assembly_line[lid][1] == chara_id:
                        ri.assembly_line[lid][1] = 0
                ri.assembly_line[line_id][1] = chara_id
        while 1:
            info_text = _("请选择一名生产工人担任第{0}号生产线主生产工人:\n").format(line_id+1)
            final_list = []
            # 遍历生产工人列表
            for npc_id in ri.production_worker_ids:
                if npc_id == 0: continue
                final_list.append([npc_id, _handler, [ri.assembly_line[line_id][1]]])
            now_panel.text_list = final_list
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_panel, _("任命主生产工人"), info_text, select_state)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def select_assembly_line_produce(self, assembly_line_id):
        """选择流水线生产的产品"""
        while 1:

            line = draw.LineDraw("-", window_width)
            line.draw()
            info_draw = draw.NormalDraw()
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

            resouce_list = [_("药剂"), _("乳制品"), _("香水"), _("基建")]

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
