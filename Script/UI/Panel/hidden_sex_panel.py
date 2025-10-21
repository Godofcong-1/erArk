from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise, attr_calculation, map_handle, character_behavior
from Script.UI.Panel import dirty_panel

import random

panel_info_data = {}

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

def handle_hidden_sex_flow(character_id: int = 0, add_flag = None, now_duration = 0, now_intensity = 0) -> None:
    """
    处理隐奸整体流程：先结算隐蔽值，再判断是否被发现
    参数:
        character_id (int): 角色id，默认为0（玩家）
        add_flag (bool): 是否增加隐蔽值，默认为None，表示根据行为类型判断
        now_duration (int): 行为持续时间，默认为0，表示使用当前行为的持续时间
        now_intensity (int): 行为强度，默认为0，表示使用当前行为的默认强度
    返回:
        None
    """
    # 需要场景中存在未处于隐奸模式且处于有意识状态的角色
    if not handle_premise.handle_place_someone_not_in_hidden_and_conscious(character_id):
        return
    # 先结算隐蔽值增减
    settle_hidden_value_by_action(character_id, add_flag, now_duration, now_intensity)
    # 获取角色数据
    character_data = cache.character_data[character_id]
    # 判断是否被发现
    discovered = check_hidden_sex_discovery(character_data.h_state.hidden_sex_discovery_dregree)
    # 被发现时
    if discovered:
        settle_discovered(character_id)

def get_hidden_level(value: int):
    """
    按当前隐蔽值返回当前隐蔽等级的str\n
    Keyword arguments:\n
    value -- 隐蔽值\n
    Return arguments:\n
    int -- 隐蔽等级,0-3\n
    str -- 隐蔽等级名
    """
    for now_cid in game_config.config_hidden_level:
        now_data = game_config.config_hidden_level[now_cid]
        if value > now_data.hidden_point:
            continue
        else:
            return now_cid,now_data.name
    # 如果没有找到对应的等级，则返回最大等级
    return 3, game_config.config_hidden_level[3].name

def get_hidden_sex_targets(character_id: int) -> List[int]:
    """
    功能: 返回指定玩家的隐奸对象角色id列表
    参数:
        character_id (int): 玩家角色id
    返回:
        List[int]: 同场景中除玩家以外处于隐奸模式的角色id列表
    """
    # 获取玩家当前位置

    position = cache.character_data[character_id].position
    scene_path = map_handle.get_map_system_path_str_for_list(position)
    scene_data: game_type.Scene = cache.scene_data[scene_path]
    result: List[int] = []
    # 遍历场景中所有角色
    for chara_id in scene_data.character_list:
        # 跳过玩家自身
        if chara_id == character_id:
            continue
        # 如果该角色处于隐奸模式，则加入结果列表
        if handle_premise.handle_hidden_sex_mode_ge_1(chara_id):
            result.append(chara_id)

    # 返回所有符合条件的角色id
    return result

def get_nearby_conscious_unfallen_characters(character_id: int) -> List[int]:
    """
    功能: 返回指定角色所在地点中，不在隐奸中，有意识且未睡眠的其他角色列表
    参数:
        character_id (int): 角色id
    返回:
        List[int]: 符合条件的角色id列表
    """
    # 获取角色当前位置对应的场景路径字符串
    position = cache.character_data[character_id].position
    scene_path = map_handle.get_map_system_path_str_for_list(position)
    # 从缓存中取出该场景数据
    scene_data: game_type.Scene = cache.scene_data[scene_path]

    result: List[int] = []
    # 遍历场景中所有角色
    for chara_cid in scene_data.character_list:
        if chara_cid == character_id:
            # 排除自身
            continue
        # 去掉在隐奸中
        if handle_premise.handle_hidden_sex_mode_ge_1(chara_cid):
            continue
        # 跳过无意识或睡眠状态的角色
        if handle_premise.handle_unconscious_flag_ge_1(chara_cid):
            continue
        if handle_premise.handle_action_sleep(chara_cid):
            continue

        # 符合所有条件，添加到结果列表
        result.append(chara_cid)

    return result

def settle_hidden_value_by_action(character_id = 0, add_flag = None, now_duration = 0, now_intensity = 0) -> None:
    """
    根据玩家当前的行为和其他因素来结算角色的隐蔽值
    参数:
        character_id (int): 角色id，默认为0，表示玩家角色
        add_flag (bool): 是否增加隐蔽值，默认为None，表示根据行为类型判断
        now_duration (int): 行为持续时间，默认为0，表示使用当前行为的持续时间
        now_intensity (int): 行为强度，默认为0，表示使用当前行为的默认强度
    返回:
        None
    """
    character_data = cache.character_data[character_id]
    # 获取当前行为
    now_behavior_id = character_data.behavior.behavior_id
    behavior_data = game_config.config_behavior[now_behavior_id]
    # 如果没有指定，则根据行为类型判断是否需要增加隐蔽值
    if add_flag == None:
        add_flag = False
        for tag in {_("猥亵"), _("性爱")}:
            if tag in behavior_data.tag:
                add_flag = True
                break
        # 等待状态减少隐蔽值
        if now_behavior_id == constant.Behavior.WAIT:
            add_flag = False
    # 如果没有指定时间，则获取行为持续时间
    if now_duration == 0:
        now_duration = character_data.behavior.duration
    # 模式
    mode_adjust = 1
    # 双不隐容易被发现
    if handle_premise.handle_hidden_sex_mode_1(character_id):
        mode_adjust = 2
    # 双隐不容易被发现
    elif handle_premise.handle_hidden_sex_mode_4(character_id):
        mode_adjust = 0.5
    # 如果没有指定强度，则根据行为类型获取默认强度
    if now_intensity == 0:
        now_intensity = 1
        tag_list = behavior_data.tag.split("|")
        for tag in tag_list:
            if tag == _("道具"):
                now_intensity = max(4, now_intensity)
            elif tag == _("插入"):
                now_intensity = max(3, now_intensity)
            elif tag == _("侍奉"):
                now_intensity = max(2, now_intensity)
    # 隐蔽能力
    now_ability_lv = character_data.ability[90]
    abi_adjust = attr_calculation.get_ability_adjust(now_ability_lv)
    # 在场人数
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    other_chara_adjust = max(len(scene_data.character_list) - 2, 1)
    # 增加
    if add_flag:
        adjust = now_intensity * mode_adjust / abi_adjust * other_chara_adjust
    # 减少
    else:
        adjust = -2 / mode_adjust * abi_adjust
    # 最终值
    delta = int(now_duration * adjust)
    # 将计算出的增益累加到角色隐蔽发现度上
    character_data.h_state.hidden_sex_discovery_dregree += delta
    # 最大为100，最小为0
    character_data.h_state.hidden_sex_discovery_dregree = min(character_data.h_state.hidden_sex_discovery_dregree, 100)
    character_data.h_state.hidden_sex_discovery_dregree = max(character_data.h_state.hidden_sex_discovery_dregree, 0)

def check_hidden_sex_discovery(now_degree: int) -> bool:
    """
    判断隐奸行为是否被发现
    参数:
        now_degree (int): 当前隐蔽值
    返回:
        bool: True-已被发现, False-未被发现
    """
    # 根据发现度获取等级
    hidden_lv, _ = get_hidden_level(now_degree)
    # 小于2级则直接返回未被发现
    if hidden_lv < 2:
        return False
    # 获取被发现概率
    discover_rate = (now_degree - game_config.config_hidden_level[1].hidden_point) * 3
    # 用随机数判断是否被发现
    random_value = random.randint(0, 100)
    if discover_rate >= random_value:
        return True
    return False

def settle_discovered(character_id: int) -> None:
    """
    隐奸被发现时的结算函数
    参数:
        character_id (int): 角色id
    返回:
        None
    """
    # 获取角色数据
    character_data = cache.character_data[character_id]
    # 退出隐奸模式
    character_data.sp_flag.hidden_sex_mode = 0
    # 获取隐奸对象
    hidden_sex_target_id_list = get_hidden_sex_targets(character_id)
    if len(hidden_sex_target_id_list):
        character_data.target_character_id = hidden_sex_target_id_list[0]
    else:
        print(f"debug : 隐奸被发现时未找到隐奸对象，角色id:{character_id}")
        return
    # 寻找是否有会发现的人
    interrupt_chara_list = get_nearby_conscious_unfallen_characters(character_id)
    # 存在则进入被发现面板
    if len(interrupt_chara_list):
        from Script.UI.Panel import sex_be_discovered_panel
        now_panel = sex_be_discovered_panel.Sex_Be_Discovered_Panel(
            window_width,
            interrupt_chara_list[0],
        )
        now_panel.draw()

class See_Hidden_Sex_InfoPanel:
    """
    显示隐奸栏数据面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, type_number: int, center_status: bool = True):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.column = column
        """ 每行状态最大个数 """
        self.draw_list: List = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.center_status: bool = center_status
        """ 居中绘制状态文本 """
        self.type_number = type_number
        """ 显示的状态类型 """

        type_line = draw.LittleTitleLineDraw(_("隐奸"), width, ":")
        # print("type_data.name :",type_data.name)
        now_draw = panel.LeftDrawTextListPanel()
        text_draw = draw.NormalDraw()

        pl_character_data = cache.character_data[0]
        all_text = ""

        # 被发现文本
        now_dregree = pl_character_data.h_state.hidden_sex_discovery_dregree
        # 根据隐蔽程度数值判断状态文本
        hidden_level, hidden_text = get_hidden_level(now_dregree)
        all_text += _(" 隐蔽程度：{0}").format(hidden_text)

        # 阴茎文本
        insert_chara_id = dirty_panel.get_inserted_character_id()
        if insert_chara_id != 0:
            insert_character_data = cache.character_data[insert_chara_id]
            chara_name = insert_character_data.name
            insert_text = " "
            # 显示阴茎位置的文本
            now_position_index = insert_character_data.h_state.insert_position
            position_text_cid = f"阴茎位置{str(now_position_index)}"
            insert_position_text = game_config.ui_text_data['h_state'][position_text_cid]
            sex_position_index = pl_character_data.h_state.current_sex_position
            # 如果是阴茎位置为阴道、子宫、后穴、尿道，且博士有体位数据，则显示性交姿势
            if now_position_index in {6,7,8,9} and sex_position_index != -1:
                sex_position_text_cid = f"体位{str(sex_position_index)}"
                sex_position_text = game_config.ui_text_data['h_state'][sex_position_text_cid]
                insert_text += _("悄悄地以{0}对{1}").format(sex_position_text, chara_name)
            # 否则为侍奉
            else:
                insert_text += _("{0}正在偷偷给你").format(chara_name)
            insert_text += insert_position_text
            all_text += insert_text

        # 如果文本不为空，则加入到绘制列表中
        if all_text != "":
            all_text = all_text + "\n"
            self.draw_list.append(type_line)
        text_draw.text = all_text
        now_draw.draw_list.append(text_draw)
        now_draw.width += len(text_draw.text)

        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()


class Select_Hidden_Sex_Mode_Panel:
    """
    用于选择隐奸模式的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int, sex_be_discovered_flag: bool = False):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.sex_be_discovered_flag: bool = sex_be_discovered_flag
        """ 是否是从被发现面板跳转过来 """
        self.now_panel = _("选择隐奸模式")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("选择隐奸模式")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = _("\n请选择要进行的隐奸：\n")
            info_text += _("○需要在没有其他人，或者其他人都无意识下才可以选择单方或者双方隐藏\n")
            info_text += _("  隐奸被发现的概率取决于隐奸模式、隐蔽技能等级、指令动作、在场人数、地点环境等\n")
            info_text += "\n"
            info_draw.text = info_text
            info_draw.draw()

            button_text_list = []
            button_text_list.append(_("[1]不隐藏：双方身体均暴露在外，仅靠视线遮挡来避免被发现，容易被察觉"))
            button_text_list.append(_("[2]干员隐藏：博士不隐藏，干员藏起来不让别人看见，隐蔽程度中等"))
            button_text_list.append(_("[3]博士隐藏：干员不隐藏，博士藏起来不让别人看见，隐蔽程度中等"))
            button_text_list.append(_("[4]双方隐藏：博士和干员都藏起来不让别人看见，很难被察觉"))
            for i in range(len(button_text_list)):
                button_text = button_text_list[i]
                can_use = True
                if i >= 1:
                    can_use = False
                    if handle_premise.handle_scene_only_two(0) or handle_premise.handle_scene_all_others_unconscious_or_sleep(0):
                        can_use = True
                # debug模式下不限制
                if cache.debug_mode:
                    can_use = True
                if can_use:
                    button_draw = draw.LeftButton(
                        button_text,
                        str(i + 1),
                        self.width,
                        cmd_func=self.select_this_mode,
                        args=(i + 1,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                # 否则为灰色文字，不可选
                else:
                    now_draw = draw.NormalDraw()
                    now_draw.text = button_text
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                line_feed.draw()

            line_feed.draw()
            line_feed.draw()
            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _( "返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_this_mode(self, mode_id):
        """选择隐奸模式"""
        from Script.Design import instuct_judege, handle_instruct
        character_data: game_type.Character = cache.character_data[0]
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]

        # 判断是否成功邀请隐奸
        if instuct_judege.calculation_instuct_judege(0, target_character_id, _("隐奸"))[0]:
            character_data.sp_flag.hidden_sex_mode = mode_id
            target_character_data.sp_flag.hidden_sex_mode = mode_id
            target_character_data.sp_flag.is_follow = 0
            # 在场其他角色数量
            scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]
            other_chara_count = len(scene_data.character_list) - 2
            # 成就初始化
            cache.achievement.hidden_sex_record = {1: mode_id, 2: other_chara_count, 3: 0, 4: 0}
            # 如果男不隐，则玩家取消H状态
            if mode_id in {1,2}:
                character_data.sp_flag.is_h = False
            # 如果是从被发现面板跳转过来
            if self.sex_be_discovered_flag:
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.OTHER_SEX_BE_FOUND_TO_HIDDEN_SEX)
            # 否则正常结算隐奸
            else:
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.ASK_HIDDEN_SEX)
        else:
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n邀请隐奸失败\n")
            now_draw.draw()
            # 如果是从被发现面板跳转过来
            if self.sex_be_discovered_flag:
                character_data.behavior.behavior_id = constant.Behavior.H_INTERRUPT
            # 否则正常结算隐奸失败
            else:
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.ASK_HIDDEN_SEX_FAIL)
