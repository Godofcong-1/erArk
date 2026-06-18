from types import FunctionType
from typing import Any, Dict, List, Tuple

from Script.Core import cache_control, game_type, get_text, flow_handle, constant, constant_promise
from Script.Design import basement, handle_premise
from Script.System.Dormitory_System import common
from Script.UI.Moudle import draw
from Script.Config import normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


class Manage_Dormitory_Panel:
    """
    宿舍管理系统主面板
    输入类型: width(int)
    输出类型: 无
    功能: 提供宿舍总览、干员宿舍调整、宿舍管理员调整三个子页
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        self.now_panel: str = _("宿舍总览")
        self.show_dormitory_detail: bool = False
        """ 是否显示宿舍具体居住情况 """
        self.temp_blank_character_ids: List[int] = []
        """ 临时空白位中的干员id列表 """
        self.dormitory_select_state: Dict[str, Any] = {}
        """ 干员选择面板的筛选状态 """

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 绘制页签并分发到对应子页面
        """
        title_text = _("宿舍管理系统")
        panel_list = [_("宿舍总览"), _("调整宿舍管理员")]
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            basement.get_base_updata()
            basement.update_work_people()
            return_list: List[str] = []

            title_draw.draw()
            for now_panel in panel_list:
                panel_width = int(self.width / len(panel_list))
                if now_panel == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{now_panel}]"
                    now_draw.style = "onbutton"
                    now_draw.width = panel_width
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{now_panel}]",
                        f"\n{now_panel}",
                        panel_width,
                        cmd_func=self.change_panel,
                        args=(now_panel,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            draw.LineDraw("+", self.width).draw()

            if self.now_panel == _("宿舍总览"):
                self._draw_overview_page(return_list)
            elif self.now_panel == _("调整宿舍管理员"):
                self._draw_manage_dormitory_manager_page(return_list)

            line_feed.draw()
            line_feed.draw()
            lock_panel_leave = self._is_character_dormitory_page_locked()
            back_style = "deep_gray" if lock_panel_leave else "standard"
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width, normal_style=back_style)
            back_draw.draw()
            return_list.append(back_draw.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                if lock_panel_leave:
                    self._draw_temp_blank_lock_hint()
                    continue
                reset_count = self._reset_unassigned_dormitory_manager_work_type()
                if reset_count > 0:
                    info_draw = draw.WaitDraw()
                    info_draw.width = self.width
                    info_draw.text = _("\n○已将{0}名未分配楼层的宿舍管理员重置为无岗位\n").format(reset_count)
                    info_draw.draw()
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, now_panel: str):
        """
        切换当前页签
        输入类型: now_panel(str)
        输出类型: 无
        功能: 更新当前显示页签
        """
        if now_panel != self.now_panel and self._is_character_dormitory_page_locked():
            self._draw_temp_blank_lock_hint()
            return
        self.now_panel = now_panel

    def _draw_overview_page(self, return_list: List[str]):
        """
        绘制宿舍总览
        输入类型: return_list(List[str])
        输出类型: 无
        功能: 显示宿舍等级、开放层数/房间数、管理员状态和基础恢复效率，并提供进入干员宿舍调整的入口
        """
        dormitory_level = cache.rhodes_island.facility_level.get(4, 1)
        open_rooms_by_layer = self._get_open_rooms_by_layer()
        open_layers = sorted(open_rooms_by_layer.keys())
        efficiency = basement.calc_facility_efficiency(4)
        max_open_layer = common.get_dormitory_max_open_layer()
        npc_count = str(len(cache.npc_id_got))

        temp_blank_list = self._get_temp_blank_character_ids()
        temp_blank_names = []
        for character_id in temp_blank_list:
            if character_id in cache.character_data:
                temp_blank_names.append(cache.character_data[character_id].name)

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("\n 当前宿舍区块等级：{0}\n").format(dormitory_level)
        info_draw.text += _(" 干员总数/宿舍容量：{0}/{1}\n").format(npc_count, cache.rhodes_island.people_max)
        info_draw.text += _(" 按等级已开放至：{0}层，").format(max_open_layer)
        info_draw.text += _("当前开放层数：{0} 层\n").format(len(open_layers))
        info_draw.text += _(" 当前开放房间数：{0} 间\n").format(sum(len(open_rooms_by_layer[layer]) for layer in open_layers))
        info_draw.text += _(" 当前基础恢复效率：{0:.0f}%\n").format(efficiency * 100)
        if len(temp_blank_names):
            info_draw.text += _(" 临时空白位：{0}人（{1}）\n").format(len(temp_blank_names), "、".join(temp_blank_names))
        else:
            info_draw.text += _(" 临时空白位：0人\n")
        info_draw.text += _("\n\n 各层管理员状态：\n")

        for layer in open_layers:
            manager_id = cache.rhodes_island.dormitory_managers.get(layer, 0)
            if manager_id and manager_id in cache.character_data:
                manager_name = cache.character_data[manager_id].name
                info_draw.text += _("  {0}层：{1}\n").format(layer, manager_name)
            else:
                info_draw.text += _("  {0}层：未任命\n").format(layer)
        if not len(open_layers):
            info_draw.text += _("  暂无开放层\n")
        info_draw.draw()
        line_feed.draw()

        # 是否显示具体居住情况的按钮
        if not self.show_dormitory_detail:
            detail_button_text = _(" ▶[具体居住情况]")
            button_draw = draw.LeftButton(detail_button_text, _("显示具体居住情况"), len(detail_button_text) * 2, cmd_func=self.show_dormitory_detail_func)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed.draw()
        # 如果选择显示具体居住情况，则按层展示每个宿舍的居住干员
        else:
            detail_button_text = _(" ▼[具体居住情况]")
            button_draw = draw.LeftButton(detail_button_text, _("显示具体居住情况"), len(detail_button_text) * 2, cmd_func=self.show_dormitory_detail_func)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed.draw()
            now_draw = draw.NormalDraw()
            now_draw.text = common.get_dormitory_occupants_text()
            now_draw.width = self.width
            now_draw.draw()
            line_feed.draw()

        line_feed.draw()

        # 提供进入干员宿舍调整的入口
        select_draw = draw.CenterButton(
            _("[选择要调整宿舍的干员]"),
            _("\n打开宿舍调整干员选择"),
            int(self.width / 3),
            cmd_func=self._prompt_select_character_for_dormitory,
        )
        select_draw.draw()
        return_list.append(select_draw.return_text)

        # 如果存在临时空白位，则提供自动排序入口
        if len(temp_blank_names):
            auto_sort_text = _("[自动排序临时空白位]")
            auto_sort_draw = draw.CenterButton(
                auto_sort_text,
                _("\n自动排序临时空白位"),
                int(self.width / 3),
                cmd_func=self._auto_sort_temp_blank_characters,
            )
            auto_sort_draw.draw()
            return_list.append(auto_sort_draw.return_text)

        line_feed.draw()

    def show_dormitory_detail_func(self):
        """
        显示/隐藏宿舍具体居住情况
        输入类型: 无
        输出类型: 无
        功能: 切换show_dormitory_detail状态以控制是否在总览页显示每个宿舍的具体居住干员信息
        """
        self.show_dormitory_detail = not self.show_dormitory_detail

    def _prompt_select_character_for_dormitory(self):
        """
        弹出通用干员选择面板并进入宿舍调整
        输入类型: 无
        输出类型: 无
        功能: 复用通用NPC选择按钮列表函数进行筛选与选择
        """
        from Script.UI.Moudle import panel
        from Script.UI.Panel import common_select_NPC

        now_draw_panel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, True, False, 0)

        while 1:
            chara_ids = sorted([cid for cid in cache.npc_id_got if cid != 0], key=lambda x: cache.character_data[x].adv)
            final_list = []
            for chara_id in chara_ids:
                final_list.append([chara_id, self._choose_new_dormitory, []])
            now_draw_panel.text_list = final_list

            info_text = _("请选择一名干员以调整宿舍（仅显示已拥有干员）：\n")
            return_list, other_return_list, self.dormitory_select_state = common_select_NPC.common_select_npc_button_list_func(
                now_draw_panel,
                _("调整干员宿舍"),
                info_text,
                self.dormitory_select_state,
            )

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list and yrn not in other_return_list:
                break

    def _draw_manage_dormitory_manager_page(self, return_list: List[str]):
        """
        绘制宿舍管理员调整页
        输入类型: return_list(List[str])
        输出类型: 无
        功能: 按层展示当前管理员并支持进入层级任命/撤换
        """
        from Script.UI.Panel import manage_basement_panel
        open_rooms_by_layer = self._get_open_rooms_by_layer()
        open_layers = sorted(open_rooms_by_layer.keys())

        # 显示已被任命为宿舍管理员，但是还没有被分配层级的干员
        manager_pool = sorted(list(cache.rhodes_island.all_work_npc_set.get(31, set())), key=lambda x: cache.character_data[x].adv)
        now_text = _("\n 以下干员已被任命为宿舍管理员，但尚未分配管理层级：")
        unassigned_managers = []
        for chara_id in manager_pool:
            character_data = cache.character_data[chara_id]
            if chara_id in cache.rhodes_island.dormitory_managers.values():
                continue
            unassigned_managers.append(character_data.name)

        if unassigned_managers:
            now_draw = draw.NormalDraw()
            now_draw.width = self.width
            now_draw.text = now_text + " ".join(unassigned_managers)
            now_draw.draw()
            line_feed.draw()

        # 显示增减命令
        adjust_pool_text = _("[宿舍管理员增减]")
        adjust_pool_draw = draw.CenterButton(
            adjust_pool_text,
            _("\n宿舍管理员增减"),
            int(self.width / 4),
            cmd_func=manage_basement_panel.change_npc_work_out,
            args=(self.width, [31]),
        )
        adjust_pool_draw.draw()
        return_list.append(adjust_pool_draw.return_text)
        line_feed.draw()

        info_draw = draw.NormalDraw()
        info_draw.width = self.width
        info_draw.text = _("\n 选择层级后可进行任命或撤换：\n")
        info_draw.draw()

        for layer in open_layers:
            manager_id = cache.rhodes_island.dormitory_managers.get(layer, 0)
            if manager_id and manager_id in cache.character_data:
                manager_name = cache.character_data[manager_id].name
                layer_text = _("[{0}层] 当前管理员：{1}").format(layer, manager_name)
                now_draw = draw.LeftButton(
                    layer_text,
                    f"\n{layer}",
                    self.width,
                    cmd_func=self._remove_manager_for_layer,
                    args=(layer,),
                )
            else:
                layer_text = _("[{0}层] 当前管理员：未任命").format(layer)
                now_draw = draw.LeftButton(
                    layer_text,
                    f"\n{layer}",
                    self.width,
                    cmd_func=self._appoint_manager_for_layer,
                    args=(layer,),
                )
            now_draw.draw()
            return_list.append(now_draw.return_text)
            line_feed.draw()

        if not len(open_layers):
            wait_draw = draw.NormalDraw()
            wait_draw.width = self.width
            wait_draw.text = _("\n 暂无可管理的开放层。\n")
            wait_draw.draw()

    def _choose_new_dormitory(self, character_id: int):
        """
        进入单角色换宿舍流程
        输入类型: character_id(int)
        输出类型: 无
        功能: 校验前提并从可入住房间中选择目标宿舍
        """
        if not handle_premise.handle_premise(constant_promise.Premise.CAN_MANUAL_CHANGE_DORMITORY, character_id):
            now_draw = draw.WaitDraw()
            now_draw.width = self.width
            now_draw.style = "gold_enrod"
            now_draw.text = _("\n○当前角色处于特殊状态，暂不可手动更换宿舍\n")
            now_draw.draw()
            return

        character_data = cache.character_data[character_id]
        open_rooms_by_layer = self._get_open_rooms_by_layer()
        occupancy = self._get_room_occupancy()
        temp_blank_list = self._get_temp_blank_character_ids()

        room_candidates: List[Tuple[int, str, str]] = []
        for layer in sorted(open_rooms_by_layer.keys()):
            for room_name, room_path in open_rooms_by_layer[layer]:
                room_count = occupancy.get(room_path, 0)
                if room_path != character_data.dormitory and room_count < 2:
                    room_candidates.append((layer, room_name, room_path))

        while 1:
            return_list: List[str] = []
            title_draw = draw.TitleLineDraw(_("调整宿舍：{0}").format(character_data.name), self.width)
            title_draw.draw()

            now_dormitory_text = self._get_dormitory_name(character_data.dormitory)
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n 当前宿舍：{0}\n").format(now_dormitory_text)
            if character_id in temp_blank_list:
                info_draw.text += _(" 当前状态：临时空白位\n")
            info_draw.text += _(" 请选择目标宿舍（仅显示已开放且未满员）：\n\n")
            info_draw.draw()

            if character_id not in temp_blank_list:
                temp_blank_text = _("[移入临时空白位]")
                temp_blank_draw = draw.CenterButton(
                    temp_blank_text,
                    _("\n移入临时空白位"),
                    int(self.width / 3),
                    cmd_func=self._move_character_to_temp_blank,
                    args=(character_id,),
                )
                temp_blank_draw.draw()
                return_list.append(temp_blank_draw.return_text)
                line_feed.draw()
            line_feed.draw()

            line_count = 0
            for layer, room_name, room_path in room_candidates:
                room_count = occupancy.get(room_path, 0)
                room_text = _("[{0}层] {1} ({2}/2)").format(layer, room_name, room_count)
                # 如果该宿舍有角色，则显示这些角色的名字
                if room_path in occupancy and occupancy[room_path] > 0:
                    occupants = [cache.character_data[cid].name for cid in cache.character_data if cache.character_data[cid].dormitory == room_path]
                    room_text += " - " + "、".join(occupants)
                room_draw = draw.LeftButton(
                    room_text,
                    f"\n{room_name}",
                    int(self.width / 4),
                    cmd_func=self._set_character_dormitory,
                    args=(character_id, room_path),
                )
                room_draw.draw()
                return_list.append(room_draw.return_text)
                # 每4个宿舍换行一次
                line_count += 1
                if line_count >= 4:
                    line_feed.draw()
                    line_count = 0

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text or yrn in return_list:
                break

    def _set_character_dormitory(self, character_id: int, dormitory_path: str):
        """
        应用角色宿舍变更
        输入类型: character_id(int), dormitory_path(str)
        输出类型: 无
        功能: 更新角色 dormitory 字段，不修改 pre_dormitory
        """
        character_data = cache.character_data[character_id]
        old_text = self._get_dormitory_name(character_data.dormitory)
        new_text = self._get_dormitory_name(dormitory_path)
        character_data.dormitory = dormitory_path
        self._remove_from_temp_blank(character_id)

        info_draw = draw.WaitDraw()
        info_draw.width = self.width
        info_draw.text = _("\n○{0} 的宿舍已从 {1} 调整为 {2}\n").format(character_data.name, old_text, new_text)
        info_draw.draw()

    def _move_character_to_temp_blank(self, character_id: int):
        """
        将干员移入临时空白位
        输入类型: character_id(int)
        输出类型: 无
        功能: 角色离开当前宿舍并加入临时空白位列表
        """
        character_data = cache.character_data[character_id]
        temp_blank_list = self._get_temp_blank_character_ids()
        if character_id not in temp_blank_list:
            temp_blank_list.append(character_id)
        old_text = self._get_dormitory_name(character_data.dormitory)
        character_data.dormitory = ""

        info_draw = draw.WaitDraw()
        info_draw.width = self.width
        info_draw.text = _("\n○{0} 已从 {1} 移入临时空白位\n").format(character_data.name, old_text)
        info_draw.draw()

    def _auto_sort_temp_blank_characters(self):
        """
        将临时空白位干员自动排序入住宿舍可用位
        输入类型: 无
        输出类型: 无
        功能: 按列表顺序将临时空白位干员填入当前可用宿舍位置
        """
        temp_blank_list = self._get_temp_blank_character_ids()
        if not len(temp_blank_list):
            return

        open_rooms_by_layer = self._get_open_rooms_by_layer()
        occupancy = self._get_room_occupancy()
        free_slots: List[str] = []

        for layer in sorted(open_rooms_by_layer.keys()):
            for room_name, room_path in open_rooms_by_layer[layer]:
                room_count = occupancy.get(room_path, 0)
                for _slot_idx in range(max(0, 2 - room_count)):
                    free_slots.append(room_path)

        assigned_count = 0
        while len(temp_blank_list) and len(free_slots):
            character_id = temp_blank_list[0]
            target_room = free_slots.pop(0)
            if character_id in cache.character_data:
                cache.character_data[character_id].dormitory = target_room
                assigned_count += 1
            temp_blank_list.pop(0)

        info_draw = draw.WaitDraw()
        info_draw.width = self.width
        if assigned_count:
            info_draw.text = _("\n○已自动安置{0}名干员进入宿舍\n").format(assigned_count)
            if len(temp_blank_list):
                info_draw.text += _("○仍有{0}名干员留在临时空白位（宿舍可用位置不足）\n").format(len(temp_blank_list))
        else:
            info_draw.text = _("\n○当前没有可用宿舍位置，无法进行自动排序\n")
        info_draw.draw()

    def _appoint_manager_for_layer(self, layer: int):
        """
        为指定层任命管理员
        输入类型: layer(int)
        输出类型: 无
        功能: 选择干员并更新 dormitory_managers 与工作岗位
        """
        while 1:
            return_list: List[str] = []
            title_draw = draw.TitleLineDraw(_("选择{0}层宿舍管理员").format(layer), self.width)
            title_draw.draw()

            basement.update_work_people()
            manager_pool = sorted(list(cache.rhodes_island.all_work_npc_set.get(31, set())), key=lambda x: cache.character_data[x].adv)

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n 请选择一名干员任命为宿舍管理员（仅显示宿舍管理员岗位干员）：\n")
            info_draw.draw()

            for chara_id in manager_pool:
                character_data = cache.character_data[chara_id]
                button_text = f"[{str(character_data.adv).rjust(4, '0')}] {character_data.name}"
                now_draw = draw.LeftButton(
                    button_text,
                    f"\n{character_data.name}",
                    int(self.width / 3),
                    cmd_func=self._do_appoint_manager,
                    args=(layer, chara_id),
                )
                now_draw.draw()
                return_list.append(now_draw.return_text)
            line_feed.draw()

            if not len(manager_pool):
                wait_draw = draw.NormalDraw()
                wait_draw.width = self.width
                wait_draw.text = _("\n 当前没有可任命的宿舍管理员，请先通过[宿舍管理员增减]将干员调整到该岗位。\n")
                wait_draw.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text or yrn in return_list:
                break

    def _do_appoint_manager(self, layer: int, character_id: int):
        """
        执行任命管理员
        输入类型: layer(int), character_id(int)
        输出类型: 无
        功能: 同步更新层管理员、角色 work_type 与工作缓存
        """
        old_manager_id = cache.rhodes_island.dormitory_managers.get(layer, 0)

        # 先把该角色在其他层的任命清掉，保证一人只管理一层
        for other_layer, other_character_id in list(cache.rhodes_island.dormitory_managers.items()):
            if other_layer != layer and other_character_id == character_id:
                cache.rhodes_island.dormitory_managers[other_layer] = 0
                # 重置玩家的该楼层钥匙
                key_item_id = 300 + other_layer
                pl_character_data = cache.character_data[0]
                if pl_character_data.item[key_item_id] > 0:
                    pl_character_data.item[key_item_id] = 0
                    info_draw = draw.NormalDraw()
                    info_draw.width = self.width
                    info_draw.text = _("\n○{0}的{1}层管理员任命已被撤销，博士持有的该层钥匙已被收回\n").format(cache.character_data[character_id].name, other_layer)
                    info_draw.draw()

        # 替换当前层旧管理员：仅撤掉该层归属，不立即撤掉岗位，离开面板时统一清理未分配楼层者

        cache.rhodes_island.dormitory_managers[layer] = character_id
        cache.character_data[character_id].work.work_type = 31
        basement.update_work_people()

        info_draw = draw.WaitDraw()
        info_draw.width = self.width
        info_draw.text = _("\n○已任命 {0} 为 {1}层宿舍管理员\n").format(cache.character_data[character_id].name, layer)
        info_draw.draw()

    def _remove_manager_for_layer(self, layer: int):
        """
        撤换指定层管理员
        输入类型: layer(int)
        输出类型: 无
        功能: 清空层管理员并将原管理员岗位重置为无
        """
        manager_id = cache.rhodes_island.dormitory_managers.get(layer, 0)
        if not manager_id:
            info_draw = draw.WaitDraw()
            info_draw.width = self.width
            info_draw.text = _("\n○该层当前没有已任命管理员\n")
            info_draw.draw()
            return

        # 仅撤掉该层归属，不立即撤掉岗位，便于后续快速改派到其他楼层。
        cache.rhodes_island.dormitory_managers[layer] = 0
        basement.update_work_people()
        # 重置玩家的该楼层钥匙
        key_item_id = 300 + layer
        pl_character_data = cache.character_data[0]
        if pl_character_data.item[key_item_id] > 0:
            pl_character_data.item[key_item_id] = 0
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n○{0}的{1}层管理员任命已被撤销，博士持有的该层钥匙已被收回\n").format(cache.character_data[manager_id].name, layer)
            info_draw.draw()

        info_draw = draw.WaitDraw()
        info_draw.width = self.width
        info_draw.text = _("\n○已撤换 {0}层宿舍管理员\n").format(layer)
        info_draw.draw()

    def _reset_unassigned_dormitory_manager_work_type(self) -> int:
        """
        离开面板时清理未分配楼层的宿舍管理员岗位
        输入类型: 无
        输出类型: int
        功能: 若干员工作岗位为宿舍管理员但未被分配到任何楼层，则将其岗位重置为无
        """
        assigned_manager_ids = set(cache.rhodes_island.dormitory_managers.values())
        assigned_manager_ids.discard(0)

        reset_count = 0
        for character_id in cache.npc_id_got:
            if character_id == 0:
                continue
            character_data = cache.character_data.get(character_id)
            if character_data is None:
                continue
            if character_data.work.work_type != 31:
                continue
            if character_id in assigned_manager_ids:
                continue
            character_data.work.work_type = 0
            reset_count += 1

        if reset_count > 0:
            basement.update_work_people()
        return reset_count

    def _get_temp_blank_character_ids(self) -> List[int]:
        """
        获取并清洗临时空白位干员列表
        输入类型: 无
        输出类型: List[int]
        功能: 确保列表存在，去重并移除无效角色id
        """
        temp_blank_list = self.temp_blank_character_ids

        valid_ids = []
        for character_id in temp_blank_list:
            if character_id in cache.character_data and character_id not in valid_ids:
                valid_ids.append(character_id)
        self.temp_blank_character_ids = valid_ids
        return self.temp_blank_character_ids

    def _remove_from_temp_blank(self, character_id: int):
        """
        将角色从临时空白位列表移除
        输入类型: character_id(int)
        输出类型: 无
        功能: 当角色被分配到宿舍后，从临时空白位列表删除
        """
        temp_blank_list = self._get_temp_blank_character_ids()
        if character_id in temp_blank_list:
            temp_blank_list.remove(character_id)

    def _is_character_dormitory_page_locked(self) -> bool:
        """
        判断当前是否处于临时空白位锁定状态
        输入类型: 无
        输出类型: bool
        功能: 当处于管理干员所属宿舍页且临时空白位不为空时，锁定离开行为
        """
        return self.now_panel == _("管理干员所属宿舍") and len(self._get_temp_blank_character_ids()) > 0

    def _draw_temp_blank_lock_hint(self):
        """
        绘制临时空白位锁定提示
        输入类型: 无
        输出类型: 无
        功能: 提示用户先清空临时空白位后再切换页面或返回
        """
        temp_count = len(self._get_temp_blank_character_ids())
        info_draw = draw.WaitDraw()
        info_draw.width = self.width
        info_draw.text = _("\n○当前有{0}名干员处于临时空白位，请先完成安置后再切换页面或返回\n").format(temp_count)
        info_draw.draw()

    def _get_open_rooms_by_layer(self) -> Dict[int, List[Tuple[str, str]]]:
        """
        统计已开放宿舍房间
        输入类型: 无
        输出类型: Dict[int, List[Tuple[str,str]]]
        功能: 返回已开放房间，key=层号，value=[(房间名, 场景路径)]
        """
        return common.get_open_dormitory_rooms_by_layer()

    def _get_room_occupancy(self) -> Dict[str, int]:
        """
        统计宿舍占用人数
        输入类型: 无
        输出类型: Dict[str,int]
        功能: 统计每个宿舍路径当前住了几名干员
        """
        occupancy: Dict[str, int] = {}
        for character_id in cache.npc_id_got:
            if character_id == 0:
                continue
            dormitory_path = cache.character_data[character_id].dormitory
            if dormitory_path:
                occupancy[dormitory_path] = occupancy.get(dormitory_path, 0) + 1
        return dict(occupancy)

    def _get_dormitory_max_open_layer(self) -> int:
        """
        根据宿舍区等级获取理论开放层上限
        输入类型: 无
        输出类型: int
        功能: 从 Facility_effect.csv 对应等级说明中解析“开放至X区”，失败时使用保底映射
        """
        return common.get_dormitory_max_open_layer()

    def _get_dormitory_name(self, dormitory_path: str) -> str:
        """
        获取宿舍显示名
        输入类型: dormitory_path(str)
        输出类型: str
        功能: 将宿舍路径转换为可读中文场景名
        """
        if dormitory_path == "":
            return _("暂无")
        if dormitory_path not in cache.scene_data:
            return dormitory_path.split("\\")[-1]
        return cache.scene_data[dormitory_path].scene_name
