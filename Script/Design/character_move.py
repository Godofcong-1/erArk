from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import map_handle, update
from Script.UI.Moudle import draw
from types import FunctionType

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

_: FunctionType = get_text._
""" 翻译api """


def own_charcter_move(target_scene: list):
    """
    主角寻路至目标场景
    Keyword arguments:
    target_scene -- 寻路目标场景(在地图系统下的绝对坐标)
    """
    while 1:
        character_data: game_type.Character = cache.character_data[0]
        if character_data.sp_flag.move_stop:
            character_data.sp_flag.move_stop = 0
            break
        # 如果当前场景已锁，离开时会把锁解开
        # 已弃用，改为在 Script/Design/map_handle.py#character_move_scene() 中处理
        if character_data.position != target_scene:
            (
                move_now,
                now_path_list,
                now_target_position,
                now_need_time,
            ) = character_move(0, target_scene)
            break_list = ["null","wait_open","door_lock"]
            if move_now in break_list :
                break
            character_data.behavior.behavior_id = constant.Behavior.MOVE
            character_data.behavior.move_target = now_target_position
            character_data.behavior.move_src = character_data.position
            character_data.behavior.move_final_target = target_scene
            character_data.behavior.duration = now_need_time
            character_data.behavior.start_time = cache.game_time
            character_data.state = constant.CharacterStatus.STATUS_MOVE
            character_data.action_info.ask_close_door_flag = False
            # print(f"debug pl start_time = {character_data.behavior.start_time}")
            update.game_update_flow(now_need_time)
        else:
            move_now = "end"
            break
    cache.character_data[0].target_character_id = 0
    if move_now in ["Null","wait_open","door_lock"]:
        cache.now_panel_id = constant.Panel.SEE_MAP
    else:
        cache.now_panel_id = constant.Panel.IN_SCENE


def character_move(character_id: int, target_scene: list) -> (str, list, list, int):
    """
    通用角色移动控制 \n
    Keyword arguments: \n
    character_id -- 角色id \n
    target_scene -- 寻路目标场景(在地图系统下的 绝对坐标) \n
    Return arguments: \n
    str:null -- 未找到路径 \n
    str:end -- 当前位置已是路径终点 \n
    list -- 路径 \n
    list -- 本次移动到的位置 \n
    int -- 本次移动花费的时间 \n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    # if not character_id:
    #     print(f"debug now_position = {now_position},target_scene = {target_scene}")
    if now_position == target_scene:
        return "end", [], [], 0
    now_position_str = map_handle.get_map_system_path_str_for_list(now_position)
    target_scene_str = map_handle.get_map_system_path_str_for_list(target_scene)
    # target_scene_data = cache.scene_data[target_scene_str]
    # if character_data.name == "阿米娅":
    #     print(f"debug 阿米娅，now_position_str = {now_position_str},target_scene_str = {target_scene_str}")
    if (
        now_position_str not in map_handle.scene_path_edge
        or target_scene_str not in map_handle.scene_path_edge[now_position_str]
    ):
        return "null", [], [], 0
    now_path_data = map_handle.scene_path_edge[now_position_str][target_scene_str]
    access_type = "open"
    # 如果已经到门前了，则判断目标场景是否可进入，不可进入则输出原因
    if now_path_data[0] == target_scene:
        access_type = map_handle.judge_scene_accessible(target_scene_str,character_id)
        # 玩家移动，且目标地点锁门时
        if character_id == 0 and access_type == "door_lock":
            now_scene_data = cache.scene_data[target_scene_str]
            # 如果这是宿舍或客房，且玩家持有一次性钥匙则消耗钥匙并解锁
            if ("Dormitory" in now_scene_data.scene_tag or "Guest_Room" in now_scene_data.scene_tag) and character_data.item[152] >= 1:
                info_draw = draw.WaitDraw()
                info_draw.text = _("\n  ●你拿出了一次性万能钥匙，悄悄打开了门\n\n")
                info_draw.draw()
                character_data.item[152] -= 1
                now_scene_data.close_flag = 0
                access_type = "open"
        # 其他不可进入情况
        if access_type not in ["open","private"]:
            return access_type, [], [], 0
    return access_type, [], now_path_data[0], now_path_data[1]


def judge_character_move_to_private(character_id: int, move_path: []) -> int:
    """
    结算角色是否移动到私密房间\n
    Keyword arguments:\n
    character_id -- 角色id\n
    move_path -- 移动路径\n
    Return arguments:\n
    move_flag -- true的话就是移动\n
    wait_flag -- true的话就是等待\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    move_flag = True # true的话就是移动
    wait_flag = False # true的话就是等待
    # 移动路径为空，直接返回
    if move_path == []:
        return False, True
    # 进行私密跟随判断
    target_scene_str = map_handle.get_map_system_path_str_for_list(move_path)
    access_type = map_handle.judge_scene_accessible(target_scene_str,character_id)
    if access_type == "private":
        # 超时后取消跟随
        if character_data.chara_setting[0] == 0:
            if character_data.action_info.follow_wait_time >= 30:
                character_data.sp_flag.is_follow = 0
                now_draw = draw.NormalDraw()
                now_draw.text = _("因为等待时间过长，所以{0}不再继续跟随\n").format(character_data.name)
                now_draw.draw()
            else:
                wait_flag = True
            move_flag = False
        # 超时后仍继续等待
        elif character_data.chara_setting[0] == 1:
            move_flag = False
            wait_flag = True
        # 超时后直接闯入
        elif character_data.chara_setting[0] == 2:
            if character_data.action_info.follow_wait_time < 30:
                move_flag = False
                wait_flag = True
            else:
                now_draw = draw.NormalDraw()
                now_draw.text = _("{0}等不下去了，决定直接进来\n").format(character_data.name)
                now_draw.draw()
        # 一直跟随，无视私密地点
        elif character_data.chara_setting[0] == 3:
            pass

        # 等待时输出提示信息
        if wait_flag:
            now_draw = draw.NormalDraw()
            now_draw.text = _("因为不方便进来，所以{0}正在外面等待\n").format(character_data.name)
            now_draw.draw()

    return move_flag, wait_flag
