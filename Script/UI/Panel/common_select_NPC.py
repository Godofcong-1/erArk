from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """

def common_select_npc_button_list_func(now_draw_panel: panel.PageHandlePanel, title_text: str = '', info_text:str = '', select_state: dict = {}) -> list:
    """
    通用npc选择按钮列表函数\n
    Keyword arguments:\n
    now_draw_panel -- 当前绘制面板，即CommonSelectNPCButtonList\n
    now_draw_panel.text_list -- 最终按钮列表，每个子列表里\n：0号元素为角色id，1号元素为按钮要调用的函数source_func，2号元素为已选择角色id列表，默认值为空\n
    title_text -- 标题文本\n
    info_text -- 信息文本\n
    return\n
    return_list -- 返回按钮列表，包括返回按钮 "返回" \n
    other_return_list -- 其他按钮列表，按下去之后不应退出面板\n
    select_state -- 筛选状态字典，包含筛选类型和关键词\n
    """
    # 定义局部状态字典保存筛选类型和关键词
    if not select_state or not isinstance(select_state, dict):
        # 如果没有传入select_state，则初始化一个新的字典
        select_state = {"type": 0, "name": "", "obj_cid": 0, "obj_value": 0}
    else:
        select_state = {
            "type": select_state.get("type", 0),
            "name": select_state.get("name", ""),
            "obj_cid": select_state.get("obj_cid", 0),
            "obj_value": select_state.get("obj_value", 0)
        }
    
    # 内部回调函数，通过返回值更新状态
    def inner_select_type_change(new_type: int):
        # 调用新的筛选类型切换函数，并更新局部状态
        new_state = select_type_change(new_type)
        select_state["type"] = new_state[0]
        select_state["name"] = new_state[1]
        select_state["obj_cid"] = new_state[2]
        select_state["obj_value"] = new_state[3]
    
    line_feed.draw()
    # 绘制标题
    if title_text:
        title_draw = draw.TitleLineDraw(title_text, window_width)
        title_draw.draw()
    # 绘制分割线
    else:
        line_draw = draw.LineDraw("-", window_width)
        line_draw.draw()
    line_feed.draw()
    # 绘制信息
    if info_text:
        info_draw = draw.NormalDraw()
        info_draw.text = info_text
        info_draw.width = window_width
        info_draw.draw()
        line_feed.draw()
    return_list = []
    other_return_list = []

    # 添加筛选功能
    select_type_list = [_("不筛选"), _("筛选收藏干员(可在角色设置中收藏)"), _("筛选访客干员"), _("筛选未陷落干员"), _("筛选已陷落干员"), _("按名称筛选"), _("筛选同区块干员"), _("筛选无意识干员"), _("按能力等级筛选")]
    
    # 绘制筛选选项
    info_text = _("选择人员筛选方式：")
    info_draw = draw.NormalDraw()
    info_draw.text = info_text
    info_draw.width = window_width
    info_draw.draw()
    
    for select_type_id in range(len(select_type_list)):
        # 每五个换行
        if select_type_id % 5 == 0 and select_type_id != 0:
            line_feed.draw()
            empty_draw = draw.NormalDraw()
            empty_draw.text = "  " * len(info_text)
            empty_draw.width = window_width
            empty_draw.draw()
        # 使用局部状态，不再依赖全局变量
        if select_type_id == select_state["type"]:
            select_type_text = f"▶{select_type_list[select_type_id]}          "
            if select_type_id == 5:
                select_type_text = f"▶{select_type_list[select_type_id]}:{select_state['name']}          "
            now_draw = draw.NormalDraw()
            now_draw.text = select_type_text
            now_draw.style = "gold_enrod"
            now_draw.width = window_width / 3
            now_draw.draw()
        # 未选中的为按钮
        else:
            draw_text = f"  {select_type_list[select_type_id]}    "
            now_draw_width = min(len(draw_text) * 2, window_width / 2.5)
            # 将回调函数替换为内部回调 inner_select_type_change
            now_draw = draw.LeftButton(
                draw_text, select_type_list[select_type_id], now_draw_width, cmd_func=inner_select_type_change, args=(select_type_id,)
            )
            now_draw.draw()
            return_list.append(now_draw.return_text)
            other_return_list.append(now_draw.return_text)
    line_feed.draw()
    line_feed.draw()
    
    # 根据局部状态进行筛选，使用select_state而非全局变量
    original_text_list = now_draw_panel.text_list
    filtered_text_list = []
    for item in original_text_list:
        npc_id = item[0]
        if npc_id != 0:  # 跳过玩家
            character_data = cache.character_data[npc_id]
            if select_state["type"] > 0:
                # 收藏筛选
                if select_state["type"] == 1 and character_data.chara_setting[2] != 1:
                    continue
                # 访客筛选
                elif select_state["type"] == 2 and npc_id not in cache.rhodes_island.visitor_info:
                    continue
                # 未陷落筛选
                elif select_state["type"] == 3 and handle_premise.handle_self_fall(npc_id):
                    continue
                # 已陷落筛选
                elif select_state["type"] == 4 and handle_premise.handle_self_not_fall(npc_id):
                    continue
                # 姓名筛选
                elif select_state["type"] == 5 and select_state["name"] not in character_data.name:
                    continue
                # 同区块筛选
                elif select_state["type"] == 6 and not handle_premise.handle_in_player_zone(npc_id):
                    continue
                # 无意识筛选
                elif select_state["type"] == 7 and handle_premise.handle_unconscious_flag_0(npc_id):
                    continue
                # 按能力等级筛选
                elif select_state["type"] == 8:
                    # 获取能力ID和阈值
                    ability_cid = select_state["obj_cid"]
                    threshold = select_state["obj_value"]
                    
                    # 检查角色是否有该能力并且等级达到阈值
                    if ability_cid not in character_data.ability or character_data.ability[ability_cid] < threshold:
                        continue
            # 添加到过滤后的列表
            filtered_text_list.append(item)
    
    # 更新面板中的列表
    now_draw_panel.text_list = filtered_text_list
    # 绘制面板
    now_draw_panel.update()
    now_draw_panel.draw()
    return_list.extend(now_draw_panel.return_list)
    other_return_list.append(now_draw_panel.next_page_return)
    other_return_list.append(now_draw_panel.old_page_return)
    # 绘制返回按钮
    line_feed.draw()
    back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
    back_draw.draw()
    line_feed.draw()
    return_list.append(back_draw.return_text)
    
    return return_list, other_return_list, select_state

def select_type_change(new_type: int) -> tuple:
    """
    筛选类型切换
    输入:
        new_type (int): 新的筛选类型
    输出:
        tuple: 根据筛选类型返回不同的元组
          - 对于类型5: (筛选类型, 筛选关键词, 0, 0)
          - 对于类型8: (筛选类型, "", 能力id, 能力等级阈值)
          - 其他类型: (筛选类型, "", 0, 0)
    """
    if new_type == 5:
        ask_name_panel = panel.AskForOneMessage()
        ask_name_panel.set(_("输入要筛选的关键词"), 10)
        now_name = ask_name_panel.draw()
        return (new_type, now_name, 0, 0)
    elif new_type == 8:
        # 按能力筛选
        line_feed = draw.NormalDraw()
        line_feed.text = "\n"
        line_feed.width = 1
        window_width = normal_config.config_normal.text_width
        
        # 显示标题
        title_draw = draw.TitleLineDraw(_("选择要筛选的能力"), window_width)
        title_draw.draw()
        line_feed.draw()
        
        # 收集所有能力ID和名称
        ability_count = 0
        return_list = []
        
        # 遍历所有能力
        for cid in game_config.config_ability:
            ability_name = game_config.config_ability[cid].name

            # 在特定的能力ID前换行
            if cid in {9, 13, 30, 40, 70} and ability_count % 10 != 0:
                line_feed.draw()
                ability_count = 0

            # 创建能力选择按钮
            ability_button = draw.LeftButton(
                f" [{ability_name}] ", 
                ability_name, 
                window_width / 10,
                cmd_func=lambda selected_cid=cid: selected_cid
            )
            
            # 绘制按钮并添加到返回列表
            ability_button.draw()
            return_list.append(ability_button.return_text)
            ability_count += 1
            
            # 每行10个按钮
            if ability_count % 10 == 0:
                line_feed.draw()

        line_feed.draw()
        line_feed.draw()
        
        # 显示返回按钮
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        back_draw.draw()
        return_list.append(back_draw.return_text)
        
        # 等待用户选择
        return_text = flow_handle.askfor_all(return_list)
        if return_text == back_draw.return_text:
            return (0, "", 0, 0)
        
        # 寻找选中的能力ID
        selected_ability_cid = 0
        for cid in game_config.config_ability:
            ability_name = game_config.config_ability[cid].name
            if return_text == ability_name:
                selected_ability_cid = cid
                break
        
        # 如果成功选择了能力，询问等级阈值
        if selected_ability_cid != 0:
            # 询问能力等级阈值
            ask_level_panel = panel.AskForOneMessage()
            ask_level_panel.set(_("输入能力等级(正整数)，将会筛选出能力等级大于等于该值的干员"), 1)
            level_text = ask_level_panel.draw()
            
            try:
                level_value = int(level_text)
                # 确保等级在有效范围内
                if level_value < 0:
                    level_value = 0
                elif level_value > 8:
                    level_value = 8
                
                return (new_type, "", selected_ability_cid, level_value)
            except ValueError:
                # 输入无效，使用默认值0
                return (new_type, "", selected_ability_cid, 0)
        
        return (0, "", 0, 0)
    else:
        return (new_type, "", 0, 0)



class CommonSelectNPCButtonList:
    """
    通用的从列表中选择目标干员的面板
    Keyword arguments:
    chara_info -- 列表，0号元素为角色id，1号元素为按钮要调用的函数source_func，2号元素为已选择角色id列表，默认值为空
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, chara_info: list, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.chara_id: int = chara_info[0]
        """ 角色id """
        self.source_func = chara_info[1]
        """ 按钮调用的函数 """
        self.chara_id_list: List[int] = chara_info[2] if len(chara_info) > 2 else []
        """ 已选择角色id列表 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        character_data: game_type.Character = cache.character_data[self.chara_id]
        button_text = f"[{str(character_data.adv).rjust(4,'0')}]：{character_data.name}"

        draw_style = 'standard'
        # 如果当前角色已经被选择，则更改按钮样式
        if self.chara_id in self.chara_id_list:
            draw_style = 'gold_enrod'
        # 如果未选中且是有口上颜色的角色，则显示口上颜色
        elif character_data.text_color:
            draw_style = character_data.name

        # 按钮绘制
        name_draw = draw.LeftButton(
            button_text, character_data.name, self.width, normal_style=draw_style, cmd_func=self.source_func, args=(self.chara_id,)
        )
        self.button_return = name_draw.return_text
        """ 绘制的对象 """
        self.now_draw = name_draw
        self.draw_text = button_text

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
