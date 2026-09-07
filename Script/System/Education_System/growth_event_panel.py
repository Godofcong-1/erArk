"""养成事件的弹出与决断界面（Plan 22 三期 §5.1）

玩家在博士办公室「处理公务」时，待处理队列里的养成事件逐条弹出，每条给2~4个选项。

⚠️ 两条界面口径：
   1. 选项的后果提示**写方向不写数值**（"倾向：坚强"而不是"坚强+2"）——
      写了数值，养成就变成算数题了
   2. 前提不满足的选项**置灰并标明原因**而不是隐藏（口径34）——
      让玩家看见"这里本来有更好的选择，但我没养到"
"""
from types import FunctionType
from typing import List

from Script.Core import cache_control, flow_handle, game_type, get_text, py_cmd, text_handle
from Script.Design import talk
from Script.Config import normal_config
from Script.System.Education_System import growth_event_handle, growth_panel
from Script.UI.Moudle import draw

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


def get_code_text(raw_text: str, character_id: int, partner_id: int) -> str:
    """
    把事件文本里的口上代码转成可显示的文本

    ⚠️ 转换期间把孩子的交互对象指向本次事件的互动对象，使文本里的交互对象代码
       指向对的人（无互动对象时为博士）；转完立刻还原
    Keyword arguments:
    raw_text -- 原始文本
    character_id -- 孩子角色id
    partner_id -- 互动对象角色id
    Return arguments:
    str -- 转换后的文本
    """
    if not raw_text:
        return ""
    character_data: game_type.Character = cache.character_data[character_id]
    old_target_id = character_data.target_character_id
    character_data.target_character_id = partner_id
    try:
        return talk.code_text_to_draw_text(raw_text, character_id)
    finally:
        character_data.target_character_id = old_target_id


def get_event_title(character_id: int) -> str:
    """
    取事件抬头："薇薇安 · 萝莉期第 38 天"
    Keyword arguments:
    character_id -- 孩子角色id
    Return arguments:
    str -- 抬头文本
    """
    from Script.System.Pregnancy_System import pregnancy_handle

    character_data: game_type.Character = cache.character_data[character_id]
    stage = growth_event_handle.get_character_stage(character_id)
    stage_name = _(growth_panel.STAGE_TALENT_NAME.get(stage, "少女"))
    # 成长天数由妊娠系统统一计算（含成长加速药），这里只取用不重算
    grow_day = pregnancy_handle.get_child_grow_day(character_id)
    return _("{0} · {1}期第 {2} 天").format(character_data.name, stage_name, grow_day)


class Growth_Event_Draw:
    """
    单条养成事件的绘制与决断
    Keyword arguments:
    queue_data -- 队列元素dict，含 uid / chara_id / partner_id
    width -- 绘制宽度
    """

    def __init__(self, queue_data: dict, width: int):
        """初始化绘制对象"""
        self.uid: str = queue_data["uid"]
        """ 事件uid """
        self.character_id: int = queue_data["chara_id"]
        """ 孩子角色id """
        self.partner_id: int = queue_data.get("partner_id", 0)
        """ 互动对象角色id，0为博士 """
        self.width: int = width
        """ 绘制宽度 """
        self.option_list: List[dict] = growth_event_handle.get_option_list(
            self.uid, self.character_id, self.partner_id)
        """ 本条事件的选项列表 """

    def draw(self) -> int:
        """
        绘制一条事件并等待玩家决断
        Keyword arguments:
        无
        Return arguments:
        int -- 玩家选定的选项序号（1~4），没有任何可选选项时为0
        """
        from Script.Config import game_config

        event_data = game_config.config_growth_event[self.uid]
        line_feed.draw()
        draw.LittleTitleLineDraw(
            _("【养成事件】{0}").format(get_event_title(self.character_id)), self.width).draw()
        # 事件正文
        text_draw = draw.NormalDraw()
        text_draw.width = self.width
        text_draw.text = "\n  {0}\n\n".format(
            get_code_text(event_data.get("text", ""), self.character_id, self.partner_id))
        text_draw.draw()
        # 没有任何可选选项时不该把玩家卡在这条事件上，直接跳过
        if not [one for one in self.option_list if one["can_use"]]:
            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            info_draw.text = _("  （这件事已经不需要你来决定了）\n")
            info_draw.style = "deep_gray"
            info_draw.draw()
            draw.LineDraw("-", self.width).draw()
            return 0
        return_list = []
        button_index = 0
        for option in self.option_list:
            option_text = get_code_text(option["text"], self.character_id, self.partner_id)
            tip_text = get_code_text(option["tip"], self.character_id, self.partner_id)
            # 前提不满足：置灰保留，并把原因写在后面（口径34）
            if not option["can_use"]:
                reason_text = get_code_text(option["reason"], self.character_id, self.partner_id)
                gray_draw = draw.NormalDraw()
                gray_draw.width = self.width
                gray_draw.style = "deep_gray"
                gray_draw.text = _("   ○ {0}").format(option_text)
                if reason_text:
                    gray_draw.text += _("（{0}）").format(reason_text)
                gray_draw.text += "\n"
                gray_draw.draw()
                continue
            button_index += 1
            button_text = "{0}{1}".format(text_handle.id_index(button_index), option_text)
            if tip_text:
                button_text += _("（{0}）").format(tip_text)
            return_text = f"\nGEVENT_{option['index']}"
            now_draw = draw.LeftButton(button_text, return_text, self.width)
            now_draw.draw()
            line_feed.draw()
            return_list.append(return_text)
        draw.LineDraw("-", self.width).draw()
        yrn = flow_handle.askfor_all(return_list)
        py_cmd.clr_cmd()
        for option in self.option_list:
            if yrn == f"\nGEVENT_{option['index']}":
                return option["index"]
        return 0


def handle_growth_event_queue(width: int = 0):
    """
    逐条处理待决断的养成事件（处理公务指令的入口）

    ⚠️ 出队在先、结算在后：无效项已由 pop_growth_event 静默丢弃，
       弹出的每一条都保证角色与配置都还在（方案 §7-4）
    Keyword arguments:
    width -- 绘制宽度，默认取窗体宽度
    Return arguments:
    无
    """
    if not width:
        width = window_width
    while 1:
        queue_data = growth_event_handle.pop_growth_event()
        if queue_data is None:
            break
        now_draw = Growth_Event_Draw(queue_data, width)
        option_index = now_draw.draw()
        if not option_index:
            continue
        growth_event_handle.settle_growth_event_option(
            queue_data["uid"], queue_data["chara_id"], queue_data.get("partner_id", 0), option_index)
