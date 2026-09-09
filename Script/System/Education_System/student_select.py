"""「选择学生」入口（2026-09-09，Plan 22 二期方案 §9.2.5）

个人课表与养成总览原来在顶部铺一排人名页签（每页 8 人、翻页），现在改为一个「选择学生」按钮：
点开走既有的通用 NPC 选择面板（Script/UI/Panel/common_select_NPC.py），名单由调用方预筛后传入
（个人课表 = 学生岗 ∪ 女儿，养成总览 = 养成中的女儿），玩家再在那个面板里按收藏 / 名字 / 区块等筛一遍挑人。
没选人时不写「尚未选择学生」，[选择学生] 按钮直接顶在行首（2026-09-09 第三轮调整）；已选人时才是「当前学生：X」+ 居中的 [选择学生]。

⚠️ 通用面板的人名按钮靠 cmd_func 把选中者传回来，而无头测试的 askfor_all 桩不执行 cmd_func，
   所以退出循环后若闭包没被触发，再按返回值（角色名）反查一次——只在闭包未触发时兜底，同名角色不会被覆盖。
⚠️ 只用 Script/UI/Moudle/draw.py 的抽象绘制类，Web 模式由 web_draw_adapter 接管。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import normal_config
from Script.System.Education_System import education_constant
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


def draw_select_student_line(width: int, now_student: int, return_list: List[str]) -> bool:
    """
    绘制选人行：已选人时是「当前学生：X」+ 居中的「[选择学生]」；没选人时不写「尚未选择」，「[选择学生]」直接顶在行首，再画一行提示
    Keyword arguments:
    width -- 整行宽度
    now_student -- 当前选中的角色id，-1 为尚未选择
    return_list -- 容器的共享返回值列表，「选择学生」按钮的哨兵往里加
    Return arguments:
    bool -- 是否已有选中的学生（False 时调用方应直接返回，不画正文）
    功能: 两个面板共用，只画不取输入；按钮返回值是不翻译的哨兵 SELECT_STUDENT_RETURN
    """
    half_width = int(width / 2)
    selected_flag = now_student != -1 and now_student in cache.character_data
    if selected_flag:
        # 已选人：左半写「当前学生：X」，右半居中一个 [选择学生] 用来换人
        now_draw = draw.LeftDraw()
        now_draw.width = half_width
        now_draw.text = _("  当前学生：{0}").format(cache.character_data[now_student].name)
        now_draw.draw()
        button_draw = draw.CenterButton(_("[选择学生]"), education_constant.SELECT_STUDENT_RETURN, half_width)
    else:
        # 没选人：不写「尚未选择学生」，[选择学生] 直接顶在行首（2026-09-09 第三轮调整）
        button_draw = draw.LeftButton(_("[选择学生]"), education_constant.SELECT_STUDENT_RETURN, half_width)
    button_draw.draw()
    return_list.append(button_draw.return_text)
    line_feed.draw()
    draw.LineDraw("-", width).draw()
    if not selected_flag:
        info_draw = draw.NormalDraw()
        info_draw.width = width
        info_draw.text = _("\n  点击[选择学生]从名单里挑一个人，再查看或编辑她的内容\n")
        info_draw.style = "deep_gray"
        info_draw.draw()
        return False
    return True


def select_student(candidate_list: List[int], title_text: str, info_text: str, now_student: int) -> int:
    """
    打开通用 NPC 选择面板让玩家从预筛好的名单里挑一个人
    Keyword arguments:
    candidate_list -- 预筛后的候选角色id列表
    title_text -- 面板标题
    info_text -- 标题下的说明文字
    now_student -- 当前选中的角色id（在名单里高亮；玩家点[返回]时原样返回）
    Return arguments:
    int -- 选中的角色id；取消则为传入的 now_student
    功能: 照 assistant_panel.chose_assistant 的写法：每轮重设 text_list（通用函数会按筛选条件就地过滤它），
          点人名或[返回]即退出（返回值在 return_list 里且不在 other_return_list 里）
    """
    from Script.UI.Panel import common_select_NPC

    selected = {"id": now_student, "hit": False}

    def on_select(character_id: int):
        """通用面板人名按钮的 cmd_func：记下选中者"""
        selected["id"] = character_id
        selected["hit"] = True

    now_draw_panel: panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 80, 8, window_width, 1, 0, 0)
    select_state: dict = {}
    name_to_id: Dict[str, int] = {}
    yrn = ""
    while 1:
        name_to_id = {}
        final_list = []
        for character_id in candidate_list:
            if character_id not in cache.character_data:
                continue
            final_list.append([character_id, on_select, [now_student]])
            name_to_id.setdefault(cache.character_data[character_id].name, character_id)
        now_draw_panel.text_list = final_list
        return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, title_text, info_text, select_state)
        yrn = flow_handle.askfor_all(return_list)
        if yrn in return_list and yrn not in other_return_list:
            break
    # cmd_func 没跑到（无头测试桩）时按角色名反查
    if not selected["hit"] and yrn in name_to_id:
        selected["id"] = name_to_id[yrn]
    return selected["id"]
