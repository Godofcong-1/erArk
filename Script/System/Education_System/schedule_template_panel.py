"""日程模板面板（Plan 22 二期 §5.1）

面板管的是"孩子没课的时候干什么"，分两层操作：

    编辑模板       —— 改的是模板本体，所有套用该模板的孩子一起变
    批量套用       —— 把一套模板一次性挂到多个孩子身上（口径 4 的核心操作）

单孩微调不在本面板，而在个人课表面板的「日程」一行（§5.2），
因为微调是"看着这个孩子的课表决定她空闲时段干什么"，和课表放一起才顺手。

⚠️ 只用 Script/UI/Moudle/draw.py 的抽象绘制类，不直接碰 Tk 或 HTML；
   Web_Draw_System/web_draw_adapter.py 在启动时包装这些抽象类，双模式才能同时成立。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.System.Education_System import schedule_template_handle
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


class Schedule_Template_Panel:
    """
    日程模板面板（方案 §5.1）
    输入类型: width(int)
    输出类型: 无
    功能: 列出全部模板与其三个时段的活动，可编辑模板、批量套用到多个孩子
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width

    def draw(self):
        """
        绘制主循环
        输入类型: 无
        输出类型: 无
        功能: 画模板表 + 两个操作按钮，直到玩家返回
        """
        while 1:
            return_list: List[str] = []
            draw.TitleLineDraw(_("日程模板"), self.width).draw()
            self._draw_head()
            template_id_by_return = self._draw_template_table()
            return_list.extend(template_id_by_return.keys())

            line_feed.draw()
            draw.LineDraw("-", self.width).draw()
            apply_draw = draw.CenterButton(_("[批量套用到多个孩子]"), _("批量套用"), int(self.width / 2))
            apply_draw.draw()
            return_list.append(apply_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            if yrn == apply_draw.return_text:
                self._batch_apply()
                continue
            if yrn in template_id_by_return:
                self._edit_template(template_id_by_return[yrn])

    def _draw_head(self):
        """
        绘制表头一行
        输入类型: 无
        输出类型: 无
        功能: 编号 / 模板名 / 三个时段 / 套用人数
        """
        head_draw = draw.NormalDraw()
        head_draw.width = self.width
        head_draw.text = _(" 编号  模板名        上午          下午          晚上        套用中\n")
        head_draw.style = "gold_enrod"
        head_draw.draw()

    def _draw_template_table(self) -> Dict[str, int]:
        """
        绘制全部模板，每行是一个可点的按钮
        输入类型: 无
        输出类型: Dict[str, int]，按钮返回值 → 模板编号
        功能: 点某一行即进入该模板的编辑
        """
        template_id_by_return: Dict[str, int] = {}
        for template_id in schedule_template_handle.get_all_template_id():
            template_data = schedule_template_handle.get_template_data(template_id)
            if template_data is None:
                continue
            slot_text_list = []
            for slot in range(schedule_template_handle.SLOT_COUNT):
                entertainment_id = template_data.get("slot", {}).get(slot, 0)
                if entertainment_id and entertainment_id in game_config.config_entertainment:
                    slot_text_list.append(game_config.config_entertainment[entertainment_id].name)
                else:
                    slot_text_list.append("--")
            use_count = schedule_template_handle.get_template_use_count(template_id)
            row_text = _("  {0}   {1:<10}  {2:<10}  {3:<10}  {4:<10}  {5} 人").format(
                template_id, template_data["name"],
                slot_text_list[0], slot_text_list[1], slot_text_list[2], use_count)
            now_draw = draw.LeftButton(row_text, f"TEMPLATE_{template_id}", self.width)
            now_draw.draw()
            template_id_by_return[now_draw.return_text] = template_id
            line_feed.draw()
        return template_id_by_return

    def _edit_template(self, template_id: int):
        """
        编辑一套模板：选一个时段，再给它挑活动
        输入类型: template_id(int)
        输出类型: 无
        功能: 改的是模板本体，所有套用它的孩子一起变
        """
        template_data = schedule_template_handle.get_template_data(template_id)
        if template_data is None:
            return
        while 1:
            return_list: List[str] = []
            slot_by_return: Dict[str, int] = {}
            draw.TitleLineDraw(_("编辑模板：{0}").format(template_data["name"]), self.width).draw()
            for slot in range(schedule_template_handle.SLOT_COUNT):
                entertainment_id = template_data.get("slot", {}).get(slot, 0)
                if entertainment_id and entertainment_id in game_config.config_entertainment:
                    now_name = game_config.config_entertainment[entertainment_id].name
                else:
                    now_name = _("未设置")
                now_draw = draw.LeftButton(
                    _("[{0}：{1}]").format(schedule_template_handle.SLOT_NAME[slot], now_name),
                    f"SLOT_{slot}", int(self.width / 2))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                slot_by_return[now_draw.return_text] = slot
                line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回编辑"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            if yrn in slot_by_return:
                slot = slot_by_return[yrn]
                entertainment_id = self._select_activity()
                if entertainment_id is not None:
                    schedule_template_handle.set_template_slot(template_id, slot, entertainment_id)

    def _select_activity(self):
        """
        从娱乐候选表里挑一项活动
        输入类型: 无
        输出类型: Optional[int]，娱乐cid；0为清空该时段；None为取消
        功能: 候选表即全部娱乐配置，含本期新增的跟随母亲 / 自由玩耍 / 自习
        """
        while 1:
            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            draw.TitleLineDraw(_("选择活动"), self.width).draw()
            for entertainment_id in schedule_template_handle.get_schedule_activity_candidate():
                entertainment_data = game_config.config_entertainment[entertainment_id]
                now_draw = draw.LeftButton(
                    _("[{0}]").format(entertainment_data.name),
                    f"ACT_{entertainment_id}", int(self.width / 5))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = entertainment_id
            line_feed.draw()
            clear_draw = draw.CenterButton(_("[清空该时段]"), _("清空该时段"), int(self.width / 2))
            clear_draw.draw()
            return_list.append(clear_draw.return_text)
            back_draw = draw.CenterButton(_("[取消]"), _("取消选择活动"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return None
            if yrn == clear_draw.return_text:
                return 0
            if yrn in id_by_return:
                return id_by_return[yrn]

    def _batch_apply(self):
        """
        批量套用：先选模板，再多选孩子，一次套完
        输入类型: 无
        输出类型: 无
        功能: 口径 4 的核心操作——给三个孩子改日程是改一个模板 + 一次套用，而不是逐个改
        """
        template_id = self._select_template()
        if template_id is None:
            return
        child_list = schedule_template_handle.get_child_candidate_list()
        if not child_list:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("\n当前没有可安排日程的孩子\n")
            info_draw.style = "deep_gray"
            info_draw.draw()
            return
        # 多选：选中的孩子存在集合里，再点一次取消选中，最后一次性套用
        selected_set = set()
        while 1:
            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            template_data = schedule_template_handle.get_template_data(template_id)
            draw.TitleLineDraw(_("批量套用：{0}").format(template_data["name"]), self.width).draw()
            for child_id in child_list:
                child_data: game_type.Character = cache.character_data[child_id]
                mark = "√" if child_id in selected_set else "  "
                now_draw = draw.LeftButton(
                    _("[{0}{1}]").format(mark, child_data.name),
                    f"CHILD_{child_id}", int(self.width / 4))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = child_id
            line_feed.draw()
            confirm_draw = draw.CenterButton(_("[确认套用]"), _("确认套用"), int(self.width / 2))
            confirm_draw.draw()
            return_list.append(confirm_draw.return_text)
            back_draw = draw.CenterButton(_("[取消]"), _("取消批量套用"), int(self.width / 2))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            if yrn == confirm_draw.return_text:
                count = schedule_template_handle.batch_apply_template(sorted(selected_set), template_id)
                info_draw = draw.NormalDraw()
                info_draw.width = self.width
                info_draw.text = _("\n已把[{0}]套用到 {1} 名孩子\n").format(template_data["name"], count)
                info_draw.style = "gold_enrod"
                info_draw.draw()
                return
            if yrn in id_by_return:
                child_id = id_by_return[yrn]
                if child_id in selected_set:
                    selected_set.discard(child_id)
                else:
                    selected_set.add(child_id)

    def _select_template(self):
        """
        选一套模板
        输入类型: 无
        输出类型: Optional[int]，模板编号；None为取消
        功能: 供批量套用与个人课表面板的单孩换模板共用
        """
        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        draw.TitleLineDraw(_("选择模板"), self.width).draw()
        for template_id in schedule_template_handle.get_all_template_id():
            template_data = schedule_template_handle.get_template_data(template_id)
            now_draw = draw.LeftButton(
                _("[{0}]").format(template_data["name"]),
                f"PICK_{template_id}", int(self.width / 4))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = template_id
        line_feed.draw()
        back_draw = draw.CenterButton(_("[取消]"), _("取消选择模板"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn in id_by_return:
            return id_by_return[yrn]
        return None
