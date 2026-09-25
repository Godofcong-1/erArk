"""日程模板面板（Plan 22 二期 §5.1）

面板管的是"孩子没课的时候干什么"，分两层操作：

    编辑模板       —— 改的是模板本体，所有套用该模板的孩子一起变
    批量套用       —— 把一套模板一次性挂到多个孩子身上（口径 4 的核心操作）

单孩微调不在本面板，而在个人课表面板的「日程」一行（§5.2），
因为微调是"看着这个孩子的课表决定她空闲时段干什么"，和课表放一起才顺手。

只用 Script/UI/Moudle/draw.py 的抽象绘制类，不直接碰 Tk 或 HTML；
   Web_Draw_System/web_draw_adapter.py 在启动时包装这些抽象类，双模式才能同时成立。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation
from Script.System.Education_System import education_constant, schedule_template_handle, growth_handle
from Script.UI.Moudle import draw, panel

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
        self.template_id_by_return: Dict[str, int] = {}
        """ 本轮模板行按钮的返回值 → 模板编号，由 draw_page 写、handle_yrn 读 """

    def draw_page(self, return_list: List[str]):
        """
        绘制本页内容
        输入类型: return_list(List[str])，容器的共享返回值列表，本页的按钮往里加
        输出类型: 无
        功能: 画模板表 + 批量套用入口。
              只画不取输入，askfor_all 由容器 Education_Manage_Panel 统一调用。
                 本页原本自带的 [返回] 与容器的 [返回] return_text 完全相同（都是「返回」），
                 同屏时 Tk 下会把先画的那个变成不可点的灰字、Web 下会画出两个，所以已删除
        """
        draw.TitleLineDraw(_("日程模板"), self.width).draw()
        self._draw_head()
        self.template_id_by_return = self._draw_template_table()
        return_list.extend(self.template_id_by_return.keys())

        line_feed.draw()
        draw.LineDraw("-", self.width).draw()
        create_draw = draw.CenterButton(_("[新建模板]"), _("新建模板"), int(self.width / 2))
        create_draw.draw()
        return_list.append(create_draw.return_text)
        apply_draw = draw.CenterButton(_("[批量套用到多个孩子]"), _("批量套用"), int(self.width / 2))
        apply_draw.draw()
        return_list.append(apply_draw.return_text)
        line_feed.draw()

    def handle_yrn(self, yrn: str):
        """
        处理本页按钮的选择结果
        输入类型: yrn(str)，容器 askfor_all 的返回值
        输出类型: 无
        功能: 批量套用 / 编辑某套模板
        """
        if yrn == _("批量套用"):
            self._batch_apply()
            return
        if yrn == _("新建模板"):
            self._create_template()
            return
        if yrn in self.template_id_by_return:
            self._edit_template(self.template_id_by_return[yrn])

    def _draw_head(self):
        """
        绘制表头一行
        输入类型: 无
        输出类型: 无
        功能: 编号 / 模板名 / 三个时段 / 套用人数。
              与 _draw_template_table 引用同一组列宽常量，两边都走 pad_display_width——
                 手写空格的表头对不上按显示宽补齐的数据行
        """
        head_text = education_constant.COLUMN_INDENT
        for column_text, column_width in (
                (_("编号"), education_constant.COLUMN_WIDTH_ID),
                (_("模板名"), education_constant.COLUMN_WIDTH_NAME),
                (_("上午"), education_constant.COLUMN_WIDTH_SLOT),
                (_("下午"), education_constant.COLUMN_WIDTH_SLOT),
                (_("晚上"), education_constant.COLUMN_WIDTH_SLOT)):
            head_text += attr_calculation.pad_display_width(column_text, column_width)
        head_text += _("套用中") + "\n"
        head_draw = draw.NormalDraw()
        head_draw.width = self.width
        head_draw.text = head_text
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
            # 0 显示为「自由选择娱乐活动」而不是「--」：空着的时段并不是没安排，而是保留当天的随机娱乐
            slot_text_list = [
                schedule_template_handle.get_activity_name(template_data.get("slot", {}).get(slot, 0))
                for slot in range(education_constant.SLOT_COUNT)]
            use_count = schedule_template_handle.get_template_use_count(template_id)
            # 不能用 "{:<10}".format()：str 的 <10 按 len()（字符数）补齐，而终端按显示列排版、
            #    中文占2列。同一个 {:<10} 对「读书」产出12列、对「上课（无课时自习）」产出19列，
            #    四套模板的行字符数全都是57、显示列宽却是82/75/71/61，没有一列对得齐
            row_text = education_constant.COLUMN_INDENT
            for column_text, column_width in (
                    (str(template_id), education_constant.COLUMN_WIDTH_ID),
                    (template_data["name"], education_constant.COLUMN_WIDTH_NAME),
                    (slot_text_list[0], education_constant.COLUMN_WIDTH_SLOT),
                    (slot_text_list[1], education_constant.COLUMN_WIDTH_SLOT),
                    (slot_text_list[2], education_constant.COLUMN_WIDTH_SLOT)):
                row_text += attr_calculation.pad_display_width(column_text, column_width)
            row_text += _("{0} 人").format(use_count)
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
            for slot in range(education_constant.SLOT_COUNT):
                now_name = schedule_template_handle.get_activity_name(template_data.get("slot", {}).get(slot, 0))
                now_draw = draw.LeftButton(
                    _("[{0}：{1}]").format(education_constant.SLOT_NAME[slot], now_name),
                    f"SLOT_{slot}", int(self.width / 2))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                slot_by_return[now_draw.return_text] = slot
                line_feed.draw()
            draw.LineDraw("-", self.width).draw()
            is_preset = schedule_template_handle.judge_template_is_preset(template_id)
            rename_draw = draw.CenterButton(_("[重命名]"), _("重命名"), int(self.width / 3))
            rename_draw.draw()
            return_list.append(rename_draw.return_text)
            # 预设四套不给删按钮，只画同宽灰字占位：直接省略会让右边的[返回]整体左移，
            #    玩家在预设与自建模板之间来回切时按钮会跳位
            if is_preset:
                null_draw = draw.CenterDraw()
                null_draw.width = int(self.width / 3)
                null_draw.style = "deep_gray"
                null_draw.text = _("（预设模板不可删除）")
                null_draw.draw()
                delete_draw = None
            else:
                delete_draw = draw.CenterButton(_("[删除本模板]"), _("删除本模板"), int(self.width / 3))
                delete_draw.draw()
                return_list.append(delete_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回编辑"), int(self.width / 3))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            if yrn == rename_draw.return_text:
                new_name = self._ask_template_name(_("给这套模板起个新名字"))
                schedule_template_handle.rename_template(template_id, new_name)
                continue
            if delete_draw is not None and yrn == delete_draw.return_text:
                if schedule_template_handle.delete_template(template_id):
                    break
                continue
            if yrn in slot_by_return:
                slot = slot_by_return[yrn]
                entertainment_id = self._select_activity()
                if entertainment_id is not None:
                    schedule_template_handle.set_template_slot(template_id, slot, entertainment_id)

    def _ask_template_name(self, ask_text: str) -> str:
        """
        向玩家要一个模板名
        输入类型: ask_text(str)，提示语
        输出类型: str，玩家输入的名字，取消或空输入为空串
        功能: 走 panel.AskForOneMessage，Tk 与 Web 两种模式共用同一条输入链
        """
        ask_panel = panel.AskForOneMessage()
        ask_panel.set(ask_text, education_constant.TEMPLATE_NAME_MAX)
        line_feed.draw()
        return ask_panel.draw().strip()

    def _create_template(self):
        """
        新建一套模板并直接进入编辑
        输入类型: 无
        输出类型: 无
        功能: 兑现方案 §1 的「可定义**若干套**日程模板」。
              建完立刻进编辑页：新模板三个时段全空，不进去配一遍等于没建，
                 而空模板套到孩子身上是「三格都不改写」，玩家会以为功能坏了
        """
        new_name = self._ask_template_name(_("给新模板起个名字（直接回车用默认名）"))
        new_id = schedule_template_handle.create_template(new_name)
        if new_id:
            self._edit_template(new_id)

    def _select_activity(self):
        """
        从娱乐候选表里挑一项活动
        输入类型: 无
        输出类型: Optional[int]，娱乐cid；0为「自由选择娱乐活动」（该时段不改写、保留随机）；None为取消
        功能: 每行6个，分三组画（schedule_template_handle.get_schedule_activity_rows）：
              第一行固定是 上课（无课时自习）与 自由选择娱乐活动；
              第二行是有年龄需求的活动（过家家 / 跟随母亲 / 自由玩耍），按钮上标注「限幼女/萝莉」——
              套了这种活动的模板给不符合年龄的干员用时，那个时段会退回到自由选择；
              第三行起是其余娱乐。
              原实现整个循环里没有任何换行，29个按钮×38列＝1102列画在同一逻辑行上，
                 靠终端软换行硬折，不是网格。
              原来的「清空该时段」与「自由选择娱乐活动」是同一个值 0，只保留后者一个出口
        """
        # 每行6个：190/6=31列，6×31=186≤190
        cell_width = int(self.width / 6)
        while 1:
            return_list: List[str] = []
            id_by_return: Dict[str, int] = {}
            draw.TitleLineDraw(_("选择活动"), self.width).draw()

            first_row, age_row, other_list = schedule_template_handle.get_schedule_activity_rows()

            def draw_activity(entertainment_id):
                """画一个活动按钮并登记返回值；有年龄限制的把限制写在名字后面"""
                name = schedule_template_handle.get_activity_name(entertainment_id)
                limit_text = schedule_template_handle.get_activity_age_limit_text(entertainment_id)
                if limit_text:
                    name = _("{0}（{1}）").format(name, limit_text)
                now_draw = draw.LeftButton(_("[{0}]").format(name), f"ACT_{entertainment_id}", cell_width)
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = entertainment_id

            for entertainment_id in first_row:
                draw_activity(entertainment_id)
            if first_row:
                line_feed.draw()
            for entertainment_id in age_row:
                draw_activity(entertainment_id)
            if age_row:
                line_feed.draw()
            index = 0
            for entertainment_id in other_list:
                draw_activity(entertainment_id)
                index += 1
                if index % 6 == 0:
                    line_feed.draw()
            if index % 6:
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[取消]"), _("取消选择活动"), self.width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return None
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
        # 必须走一期的 get_student_candidate_list 而不是「有成长素质就算孩子」：
        #    世界设定「萝莉化」(cache.world_setting[1]) 会给全岛干员挂上萝莉素质103
        #    (character_handle.py:434)，只按素质筛会把整个罗德岛列进这份名单；
        #    另外婴儿(101)也排不了自习读书，那份名单已经把两件事一并挡掉了
        child_list = growth_handle.get_student_candidate_list()
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
            # 模板取不到（编号非法，或已被删掉）就直接退出，不画一个空面板
            if template_data is None:
                return
            draw.TitleLineDraw(_("批量套用：{0}").format(template_data["name"]), self.width).draw()
            # 每行6个：190/6=31列。原来整个循环没有换行，孩子一多就会串行
            index = 0
            for child_id in child_list:
                child_data: game_type.Character = cache.character_data[child_id]
                mark = "√" if child_id in selected_set else "  "
                now_draw = draw.LeftButton(
                    _("[{0}{1}]").format(mark, child_data.name),
                    f"CHILD_{child_id}", int(self.width / 6))
                now_draw.draw()
                return_list.append(now_draw.return_text)
                id_by_return[now_draw.return_text] = child_id
                index += 1
                if index % 6 == 0:
                    line_feed.draw()
            if index % 6:
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
        输出类型: Optional[int]，模板编号；0为不套用（恢复每日随机娱乐）；None为取消
        功能: 供批量套用与个人课表面板的单孩换模板共用。
              两个调用点都必须用 `is None` 判取消而不是判真假——
                 0 是「不套用」这个有效选项，用真假判会把它当成取消给吞掉
        """
        return_list: List[str] = []
        id_by_return: Dict[str, int] = {}
        draw.TitleLineDraw(_("选择模板"), self.width).draw()
        # 每行6个：190/6=31列。原来整个循环没有换行，模板一多就会串行
        index = 0
        for template_id in schedule_template_handle.get_all_template_id():
            template_data = schedule_template_handle.get_template_data(template_id)
            # 编号来自 get_all_template_id，正常取得到；取不到就跳过这一项，不崩在下标上
            if template_data is None:
                continue
            now_draw = draw.LeftButton(
                _("[{0}]").format(template_data["name"]),
                f"PICK_{template_id}", int(self.width / 6))
            now_draw.draw()
            return_list.append(now_draw.return_text)
            id_by_return[now_draw.return_text] = template_id
            index += 1
            if index % 6 == 0:
                line_feed.draw()
        if index % 6:
            line_feed.draw()
        # 「不套用」是模板编号0，apply_template 早就支持，只是此前面板没给出口——
        # 少了它，孩子一旦套上日程就再也回不到「每日随机娱乐」的状态
        none_draw = draw.CenterButton(_("[不套用日程（恢复随机）]"), _("不套用日程"), int(self.width / 2))
        none_draw.draw()
        return_list.append(none_draw.return_text)
        id_by_return[none_draw.return_text] = 0
        back_draw = draw.CenterButton(_("[取消]"), _("取消选择模板"), int(self.width / 2))
        back_draw.draw()
        return_list.append(back_draw.return_text)
        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn in id_by_return:
            return id_by_return[yrn]
        return None
