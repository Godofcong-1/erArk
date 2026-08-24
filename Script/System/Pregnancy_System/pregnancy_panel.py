import datetime
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.UI.Moudle import draw
from Script.Config import normal_config
from Script.System.Pregnancy_System import egg_handle, family_tree_draw

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

STAGE_NONE = 0
""" 阶段枚举：无 """
STAGE_FERTILIZATION = 1
""" 阶段枚举：受精 """
STAGE_EGG_WAIT = 2
""" 阶段枚举：持卵待鉴定 """
STAGE_PREGNANCY = 3
""" 阶段枚举：妊娠 """
STAGE_HATCHING = 4
""" 阶段枚举：孵化中 """
STAGE_PARTURIENT = 5
""" 阶段枚举：临盆 """
STAGE_POSTPARTUM = 6
""" 阶段枚举：产后 """
STAGE_REARING = 7
""" 阶段枚举：育儿 """

STAGE_NAME_LIST = [_("全部"), _("受精"), _("持卵待鉴定"), _("妊娠"), _("孵化中"), _("临盆"), _("产后"), _("育儿")]
""" 阶段名列表（0位为筛选用的全部） """


def get_chara_pregnancy_stage(character_id: int) -> int:
    """
    获取角色当前的怀孕阶段枚举（同时满足多个时取时序最靠后者）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 阶段枚举值（0为不在任何怀孕阶段）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_stage = STAGE_NONE
    if character_data.talent[20]:
        now_stage = STAGE_FERTILIZATION
    if len(egg_handle.get_unidentified_eggs(character_id, exclude_held=False)):
        now_stage = STAGE_EGG_WAIT
    if character_data.talent[21]:
        now_stage = STAGE_PREGNANCY
    if len(egg_handle.get_hatching_eggs(character_id)):
        now_stage = STAGE_HATCHING
    if character_data.talent[22]:
        now_stage = STAGE_PARTURIENT
    if character_data.talent[23]:
        now_stage = STAGE_POSTPARTUM
    if character_data.talent[24]:
        now_stage = STAGE_REARING
    return now_stage


def get_date_text(now_time: datetime.datetime) -> str:
    """
    将时间格式化为"X月X日"文本
    Keyword arguments:
    now_time -- 时间
    Return arguments:
    str -- 格式化文本
    """
    return _("{0}月{1}日").format(now_time.month, now_time.day)


def get_stage_info_text(character_id: int, now_stage: int) -> str:
    """
    获取角色当前阶段的关键时间说明文本
    Keyword arguments:
    character_id -- 角色id
    now_stage -- 阶段枚举值
    Return arguments:
    str -- 关键时间说明
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if now_stage == STAGE_FERTILIZATION:
        start_time = character_data.pregnancy.fertilization_time
        return _("受精于{0}，预计{1}妊娠").format(get_date_text(start_time), get_date_text(start_time + datetime.timedelta(days=90)))
    if now_stage == STAGE_EGG_WAIT:
        egg_count = len(egg_handle.get_unidentified_eggs(character_id, exclude_held=False))
        return _("{0}枚卵待鉴定").format(egg_count)
    if now_stage == STAGE_PREGNANCY:
        start_time = character_data.pregnancy.fertilization_time
        return _("受精于{0}，预计{1}临盆").format(get_date_text(start_time), get_date_text(start_time + datetime.timedelta(days=260)))
    if now_stage == STAGE_HATCHING:
        hatching_eggs = egg_handle.get_hatching_eggs(character_id)
        first_egg = list(hatching_eggs.values())[0]
        hatch_day = egg_handle.get_hatch_day(first_egg)
        born_time = first_egg["lay_time"] + datetime.timedelta(days=egg_handle.HATCH_TOTAL_DAY)
        return _("孵化第{0}天，预计{1}破壳").format(hatch_day, get_date_text(born_time))
    if now_stage == STAGE_PARTURIENT:
        return _("已在住院区待产，预计近日生产")
    if now_stage == STAGE_POSTPARTUM:
        return _("生产完毕，正在住院区休养")
    if now_stage == STAGE_REARING:
        if len(character_data.relationship.child_id_list):
            child_id = character_data.relationship.child_id_list[-1]
            if child_id in cache.character_data:
                child_data = cache.character_data[child_id]
                born_time = child_data.pregnancy.born_time
                return _("正在育儿室照顾{0}，预计{1}完成育儿").format(child_data.name, get_date_text(born_time + datetime.timedelta(days=90)))
        return _("育儿中")
    return ""


class Pregnancy_Overview_Panel:
    """
    怀孕总览面板对象（总览页+生育谱系图页）
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_page: int = 0
        """ 当前页签（0总览，1生育谱系图） """
        self.tree_center_id: int = 0
        """ 谱系图当前的中心角色id（初始为玩家） """
        self.tree_page: int = 0
        """ 谱系图当前的家族分页页码（0起） """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("怀孕状态总览"), self.width)
        while 1:
            title_draw.draw()
            py_cmd.clr_cmd()
            return_list = []

            # 页签切换按钮
            page_name_list = [_("总览"), _("生育谱系图")]
            for page_id in range(len(page_name_list)):
                if page_id == self.now_page:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{page_name_list[page_id]}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(page_name_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{page_name_list[page_id]}]",
                        page_name_list[page_id],
                        self.width / len(page_name_list),
                        cmd_func=self.change_page,
                        args=(page_id,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line_draw = draw.LineDraw("+", self.width)
            line_draw.draw()

            # 分页绘制
            if self.now_page == 0:
                return_list.extend(self.draw_overview_page())
            else:
                return_list.extend(self.draw_family_tree_page())

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def draw_overview_page(self) -> list:
        """
        绘制总览页（排序/筛选+干员阶段列表）
        Return arguments:
        list -- 监听的按钮返回文本列表
        """
        return_list = []

        # 排序按钮
        info_draw = draw.NormalDraw()
        info_draw.text = _("排序方式：")
        info_draw.draw()
        sort_text = _("[按阶段降序▼]") if cache.pregnancy_panel_sort_type == 0 else _("[按阶段升序▲]")
        sort_draw = draw.LeftButton(sort_text, _("切换排序"), len(sort_text) * 2, cmd_func=self.change_sort_type)
        sort_draw.draw()
        return_list.append(sort_draw.return_text)
        line_feed.draw()

        # 筛选按钮组
        info_draw = draw.NormalDraw()
        info_draw.text = _("阶段筛选：")
        info_draw.draw()
        for stage_id in range(len(STAGE_NAME_LIST)):
            if stage_id == cache.pregnancy_panel_filter_type:
                now_draw = draw.NormalDraw()
                now_draw.text = f"▶{STAGE_NAME_LIST[stage_id]}  "
                now_draw.style = "gold_enrod"
                now_draw.draw()
            else:
                draw_text = f"  {STAGE_NAME_LIST[stage_id]}  "
                now_draw = draw.LeftButton(draw_text, STAGE_NAME_LIST[stage_id], len(draw_text) * 2, cmd_func=self.change_filter_type, args=(stage_id,))
                now_draw.draw()
                return_list.append(now_draw.return_text)
        line_feed.draw()
        line_feed.draw()

        # 收集处于怀孕阶段的干员
        chara_stage_list = []
        for character_id in sorted(cache.npc_id_got):
            if character_id == 0:
                continue
            now_stage = get_chara_pregnancy_stage(character_id)
            if now_stage == STAGE_NONE:
                continue
            if cache.pregnancy_panel_filter_type and now_stage != cache.pregnancy_panel_filter_type:
                continue
            chara_stage_list.append((character_id, now_stage))
        # 按阶段排序（0降序，1升序）
        chara_stage_list.sort(key=lambda data: data[1], reverse=cache.pregnancy_panel_sort_type == 0)

        if not len(chara_stage_list):
            info_draw = draw.NormalDraw()
            info_draw.text = _("当前没有处于怀孕阶段的干员\n")
            info_draw.width = self.width
            info_draw.draw()
            return return_list

        # 逐行绘制：姓名按钮（点击以其为中心打开谱系图）+阶段名+关键时间
        for character_id, now_stage in chara_stage_list:
            character_data = cache.character_data[character_id]
            name_text = f"[{character_data.name}]"
            name_draw = draw.LeftButton(name_text, f"{character_id}_{character_data.name}", 20, cmd_func=self.jump_to_tree, args=(character_id,))
            name_draw.draw()
            return_list.append(name_draw.return_text)
            info_draw = draw.NormalDraw()
            stage_text = STAGE_NAME_LIST[now_stage]
            info_draw.text = f"　{stage_text}　　{get_stage_info_text(character_id, now_stage)}"
            info_draw.width = self.width - 20
            info_draw.draw()
            line_feed.draw()

        return return_list

    def draw_family_tree_page(self) -> list:
        """
        绘制生育谱系图页（带完整连线的传统家谱图：上1代+中心+下2代共4代，夫妇以╤相连并自其所在列
        经代间排版行连线到子女，玩家名按父本位置重复显示，超宽时按家族自动分页，点击角色换中心）
        Return arguments:
        list -- 监听的按钮返回文本列表
        """
        from Script.Core import text_handle
        return_list = []

        # 重置回博士按钮
        reset_draw = draw.LeftButton(_("[重置回博士]"), _("重置回博士"), 24, cmd_func=self.reset_tree_center)
        reset_draw.draw()
        return_list.append(reset_draw.return_text)
        info_draw = draw.NormalDraw()
        info_draw.text = _("　显示上{0}代+下{1}代共4代　夫妇以╤相连并连线到子女　玩家名按父本位置重复显示　超宽时按家族分页　\"…\"表示尚有成员/更深代数未显示　点击图中角色可以其为中心重绘\n").format(
            family_tree_draw.UP_GEN, family_tree_draw.DOWN_GEN
        )
        info_draw.draw()
        line_feed.draw()

        # 中心角色兜底（角色被删除等情况时重置回玩家）
        if self.tree_center_id not in cache.character_data:
            self.tree_center_id = 0

        window_width_int = int(self.width)
        chart_data = family_tree_draw.build_family_tree_chart(self.tree_center_id, window_width_int - 2, self.tree_page)
        self.tree_page = chart_data["now_page"]
        button_count = 0
        # 整图统一前导缩进（全部行同一缩进以保证上下连线的列对齐，缩进内为近似居中）
        pad_width = max(0, (window_width_int - chart_data["width"]) // 2)
        for row_data in chart_data["rows"]:
            now_col = 0
            for cell in row_data["cells"]:
                # 以半角空格把游标补齐到cell的目标列（目标列=统一缩进+图内列位）
                target_col = pad_width + cell["col"]
                if target_col > now_col:
                    space_draw = draw.NormalDraw()
                    space_draw.text = " " * (target_col - now_col)
                    space_draw.draw()
                token = cell["token"]
                if token["type"] == "text":
                    text_draw = draw.NormalDraw()
                    text_draw.text = token["text"]
                    if "style" in token:
                        text_draw.style = token["style"]
                    text_draw.draw()
                elif token["is_center"]:
                    center_draw = draw.NormalDraw()
                    center_draw.text = token["text"]
                    center_draw.style = "gold_enrod"
                    center_draw.draw()
                else:
                    button_count += 1
                    button_draw = draw.LeftButton(
                        token["text"],
                        f"tree{button_count}_{token['text']}",
                        text_handle.get_text_index(token["text"]),
                        cmd_func=self.change_tree_center,
                        args=(token["chara_id"],),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                now_col = target_col + text_handle.get_text_index(token["text"])
            line_feed.draw()

        # 家族分页控制行（仅多页时绘制）
        if chart_data["total_page"] > 1:
            line_feed.draw()
            if chart_data["now_page"] > 0:
                prev_draw = draw.LeftButton(_("[上一页]"), _("谱系图上一页"), 12, cmd_func=self.change_tree_page, args=(-1,))
                prev_draw.draw()
                return_list.append(prev_draw.return_text)
            page_info_draw = draw.NormalDraw()
            page_info_draw.text = _("　第{0}/{1}页　").format(chart_data["now_page"] + 1, chart_data["total_page"])
            page_info_draw.draw()
            if chart_data["now_page"] < chart_data["total_page"] - 1:
                next_draw = draw.LeftButton(_("[下一页]"), _("谱系图下一页"), 12, cmd_func=self.change_tree_page, args=(1,))
                next_draw.draw()
                return_list.append(next_draw.return_text)
            line_feed.draw()

        return return_list

    def change_page(self, page_id: int):
        """
        切换页签
        Keyword arguments:
        page_id -- 页签id
        """
        self.now_page = page_id

    def change_sort_type(self):
        """切换总览页的排序方向"""
        cache.pregnancy_panel_sort_type = 1 - cache.pregnancy_panel_sort_type

    def change_filter_type(self, stage_id: int):
        """
        切换总览页的阶段筛选
        Keyword arguments:
        stage_id -- 阶段枚举值（0为全部）
        """
        cache.pregnancy_panel_filter_type = stage_id

    def jump_to_tree(self, character_id: int):
        """
        从总览页跳转到以某角色为中心的谱系图页
        Keyword arguments:
        character_id -- 角色id
        """
        self.tree_center_id = character_id
        self.tree_page = 0
        self.now_page = 1

    def change_tree_center(self, character_id: int):
        """
        以某角色为新中心重绘谱系图（页码重置）
        Keyword arguments:
        character_id -- 角色id
        """
        self.tree_center_id = character_id
        self.tree_page = 0

    def change_tree_page(self, delta: int):
        """
        谱系图家族分页翻页（下限钳位，上限由绘制时按总页数钳位）
        Keyword arguments:
        delta -- 页码增量（±1）
        """
        self.tree_page = max(0, self.tree_page + delta)

    def reset_tree_center(self):
        """谱系图中心重置回玩家"""
        self.tree_center_id = 0
        self.tree_page = 0
