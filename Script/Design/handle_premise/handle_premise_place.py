from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.Design import map_handle
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def add_premise(premise: str) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_premise_data[premise] = return_wrapper
        return return_wrapper

    return decoraror


def common_place_judge_by_SceneName(character_id: int, scene_name: str, judge_in_flag: bool = True) -> bool:
    """
    通用型检测角色是否在特定名称的地点中的函数
    Keyword arguments:
    character_id -- 角色id
    scene_name -- 地点名
    judge_in_flag -- 判断在还是不在，默认为Ture，判断在
    Return arguments:
    bool -- 是否满足
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if scene_name == now_scene_data.scene_name:
        return judge_in_flag
    else:
        return not judge_in_flag


def common_place_judge_by_SceneTag(character_id: int, scene_tag: str, judge_in_flag: bool = True) -> bool:
    """
    通用型检测角色是否在有特定标签的地点中的函数
    Keyword arguments:
    character_id -- 角色id
    scene_tag -- 地点标签名
    judge_in_flag -- 判断在还是不在，默认为Ture，判断在
    Return arguments:
    bool -- 是否满足
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if scene_tag in now_scene_data.scene_tag:
        return judge_in_flag
    else:
        return not judge_in_flag


@add_premise(constant_promise.Premise.IN_PLAYER_SCENE)
def handle_in_player_scene(character_id: int) -> int:
    """
    校验角色是否与玩家处于同场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if now_character_data.position == cache.character_data[0].position:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_PLAYER_SCENE)
def handle_not_in_player_scene(character_id: int) -> int:
    """
    校验角色是否不与玩家处于同场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_player_scene(character_id)


@add_premise(constant_promise.Premise.PLAYER_COME_SCENE)
def handle_player_come_scene(character_id: int) -> int:
    """
    校验玩家来到该角色所在的地点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    pl_character_data: game_type.Character = cache.character_data[0]
    if (
        len(pl_character_data.behavior.move_src) and
        len(pl_character_data.behavior.move_target) and
        pl_character_data.behavior.move_src != pl_character_data.behavior.move_target
    ):
        scene_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        if character_id > 0 and character_id in scene_data.character_list:
            return 1
    return 0


@add_premise(constant_promise.Premise.PLAYER_LEAVE_SCENE)
def handle_player_leave_scene(character_id: int) -> int:
    """
    校验玩家离开该角色所在的地点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    pl_character_data: game_type.Character = cache.character_data[0]
    now_character_data: game_type.Character = cache.character_data[character_id]
    if (
            pl_character_data.behavior.move_src == now_character_data.position
            and pl_character_data.behavior.move_target != now_character_data.position
            # and pl_character_data.position != target_data.position
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.TATGET_COME_SCENE)
def handle_target_come_scene(character_id: int) -> int:
    """
    校验该角色来到玩家所在的地点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    pl_character_data: game_type.Character = cache.character_data[0]
    now_character_data: game_type.Character = cache.character_data[character_id]
    if (
            now_character_data.behavior.move_src != pl_character_data.position
            and now_character_data.behavior.move_target == pl_character_data.position
            and now_character_data.position == pl_character_data.position
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.TATGET_LEAVE_SCENE)
def handle_target_leave_scene(character_id: int) -> int:
    """
    校验角色是否是从玩家场景离开
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    now_character_data: game_type.Character = cache.character_data[character_id]
    if (
            now_character_data.behavior.move_src == cache.character_data[0].position
            and now_character_data.behavior.move_target != cache.character_data[0].position
            and now_character_data.position != cache.character_data[0].position
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_ONLY_TWO)
def handle_scene_only_two(character_id: int) -> int:
    """
    该地点仅有两个角色(可以不含玩家)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    return len(character_list) == 2


@add_premise(constant_promise.Premise.SCENE_OVER_TWO)
def handle_scene_over_two(character_id: int) -> int:
    """
    该地点有超过两个角色(可以不含玩家)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    return len(character_list) > 2


@add_premise(constant_promise.Premise.SCENE_ONLY_ONE)
def handle_scene_only_one(character_id: int) -> int:
    """
    该地点里没有自己外的其他角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    return len(character_list) == 1


@add_premise(constant_promise.Premise.IN_PLAYER_ZONE)
def handle_in_player_zone(character_id: int) -> int:
    """
    与玩家处于相同大区域
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if now_character_data.position[0] == cache.character_data[0].position[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_OVER_ONE)
def handle_scene_over_one(character_id: int) -> int:
    """
    该地点里有除了自己之外的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    return len(character_list) > 1


@add_premise(constant_promise.Premise.SCENE_SOMEONE_CAN_BE_INTERACT)
def handle_scene_someone_can_be_interact(character_id: int) -> int:
    """
    房间内存在可交互对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design import handle_npc_ai
    target_id = handle_npc_ai.select_random_free_character(character_id)
    if target_id != -1:
        return 1
    return 0


@add_premise(constant_promise.Premise.MOVE_TO_SAME_TARGET_WITH_PL)
def handle_move_to_same_target_with_pl(character_id: int) -> int:
    """
    该角色与玩家有相同的移动目标地点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    pl_character_data: game_type.Character = cache.character_data[0]
    now_character_data: game_type.Character = cache.character_data[character_id]
    if (
            now_character_data.behavior.move_final_target == pl_character_data.behavior.move_final_target
            or now_character_data.behavior.move_target == pl_character_data.behavior.move_target
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_IS_H)
def handle_scene_someone_is_h(character_id: int) -> int:
    """
    该地点有其他角色在和玩家H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_self_is_h
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于2时进行检测，不再排除自己的跟随和H状态
    # if len(scene_data.character_list) > 2 and not (character_data.sp_flag.is_follow or character_data.sp_flag.is_h):
    if len(character_list) <= 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 遍历非自己且非玩家的角色
        if chara_id == character_id or chara_id == 0:
            continue
        # 检测是否在H
        if handle_self_is_h(chara_id):
            return 999
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_H_BUT_NOT_HIDDEN_SEX)
def handle_scene_someone_h_but_not_hidden_sex(character_id: int) -> int:
    """
    该地点有其他角色在和玩家进行非隐奸的H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_hidden_sex_mode_0
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于2时进行检测，不再排除自己的跟随和H状态
    # if len(scene_data.character_list) > 2 and not (character_data.sp_flag.is_follow or character_data.sp_flag.is_h):
    if len(character_list) <= 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 遍历非自己且非玩家的角色
        if chara_id != character_id and chara_id != 0:
            other_character_data: game_type.Character = cache.character_data[chara_id]
            # 检测是否在非隐奸H
            if other_character_data.sp_flag.is_h and handle_hidden_sex_mode_0(chara_id):
                return 999
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_NO_FALL)
def handle_scene_someone_no_fall(character_id: int) -> int:
    """
    该地点有未拥有陷落素质的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_self_not_fall,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_self_not_fall(chara_id):
            return 999
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_HP_1)
def handle_scene_someone_hp_1(character_id: int) -> int:
    """
    该地点有HP1或太疲劳的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_self_tired,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_self_tired(chara_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_UNCONSCIOUS)
def handle_scene_someone_unconscious(character_id: int) -> int:
    """
    该地点有无意识状态的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_unconscious_flag_ge_1,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_unconscious_flag_ge_1(chara_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_NOT_UNCONSCIOUS)
def handle_scene_someone_not_unconscious(character_id: int) -> int:
    """
    该地点有玩家以外的非无意识状态的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_unconscious_flag_0,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_unconscious_flag_0(chara_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_NOT_IN_HIDDEN_AND_CONSCIOUS)
def handle_place_someone_not_in_hidden_and_conscious(character_id: int) -> int:
    """
    场景中存在未处于隐奸模式且处于有意识状态的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_unconscious_flag_0, handle_hidden_sex_mode_0
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_hidden_sex_mode_0(chara_id) and handle_unconscious_flag_0(chara_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_ALL_UNCONSCIOUS)
def handle_scene_all_unconscious(character_id: int) -> int:
    """
    该地点有玩家以外的角色，且所有角色都处于无意识状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_unconscious_flag_0,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_unconscious_flag_0(chara_id):
            return 0
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_ALL_UNCONSCIOUS_OR_SLEEP)
def handle_scene_all_unconscious_or_sleep(character_id: int) -> int:
    """
    该地点有玩家以外的角色，且所有角色都处于无意识或睡眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_action_sleep,
        handle_unconscious_flag_ge_1,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_unconscious_flag_ge_1(chara_id):
            continue
        if handle_action_sleep(chara_id):
            continue
        return 0
    return 1


@add_premise(constant_promise.Premise.SCENE_ALL_OTHERS_UNCONSCIOUS_OR_SLEEP)
def handle_scene_all_others_unconscious_or_sleep(character_id: int) -> int:
    """
    该地点除了自己和交互对象以外的角色都处于无意识或睡眠状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_action_sleep,
        handle_unconscious_flag_ge_1,
    )
    character_data: game_type.Character = cache.character_data[character_id]
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过自己、交互对象、玩家
        if chara_id == character_id or chara_id == character_data.target_character_id or chara_id == 0:
            continue
        if handle_unconscious_flag_ge_1(chara_id):
            continue
        if handle_action_sleep(chara_id):
            continue
        return 0
    return 1


@add_premise(constant_promise.Premise.SCENE_OTHERS_CONSCIOUS)
def handle_scene_others_conscious(character_id: int) -> int:
    """
    该地点除了自己、交互对象和玩家之外还有有意识且没睡觉的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_action_sleep,
        handle_unconscious_flag_0,
    )
    character_data: game_type.Character = cache.character_data[character_id]
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过自己、交互对象、玩家
        if chara_id == character_id or chara_id == character_data.target_character_id or chara_id == 0:
            continue
        if handle_unconscious_flag_0(chara_id) and not handle_action_sleep(chara_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_IS_MASTUREBATE)
def handle_scene_someone_is_masturebate(character_id: int) -> int:
    """
    该地点有角色在自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过自己、玩家
        if chara_id == character_id or chara_id == 0:
            continue
        other_character_data: game_type.Character = cache.character_data[chara_id]
        # 检测是否在自慰
        if other_character_data.behavior.behavior_id == constant.Behavior.MASTUREBATE:
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_HAVE_ASSISTANT)
def handle_place_have_assistant(character_id: int) -> int:
    """
    该地点有助理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if chara_id == pl_character_data.assistant_character_id:
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_FALL_LE_1)
def handle_scene_someone_fall_le_1(character_id: int) -> int:
    """
    该地点有玩家以外的角色，且有角色的陷落等级小于等于1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_self_not_fall,
        handle_self_fall_1,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_self_not_fall(chara_id) or handle_self_fall_1(chara_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_ALL_FALL_GE_2)
def handle_scene_all_fall_ge_2(character_id: int) -> int:
    """
    该地点有玩家以外的角色，且所有角色都至少有2级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_self_not_fall,
        handle_self_fall_1,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_self_not_fall(chara_id) or handle_self_fall_1(chara_id):
            return 0
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_ALL_NOT_TIRED)
def handle_scene_all_not_tired(character_id: int) -> int:
    """
    该地点有玩家以外的角色，且所有角色都未疲劳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_self_tired,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_self_tired(chara_id):
            return 0
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_ALL_NOT_H)
def handle_scene_all_not_h(character_id: int) -> int:
    """
    该地点有玩家以外的角色，且所有角色都未在H中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_self_is_h
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_self_is_h(chara_id):
            return 0
        return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_HAVE_MULTI_MASTUREBATE_TO_PL_CHARA)
def handle_scene_have_multi_masturebate_to_pl_chara(character_id: int) -> int:
    """
    该地点有多个要逆推玩家来自慰的角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_masturebate_to_pl_flag_1
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    count = 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        # 如果是自慰逆推玩家的角色，计数加一
        if handle_masturebate_to_pl_flag_1(chara_id):
            count += 1
    if count >= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.TEACHER_TEACHING_IN_CLASSROOM)
def handle_teacher_teaching_in_classroom(character_id: int) -> int:
    """
    当前有教师在教室里讲课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        # 首先需要是老师，然后正在授课
        if (
            character_data.work.work_type == 151
            and character_data.behavior.behavior_id == constant.Behavior.TEACH
        ):
            # 接着需要地点在教室里
            now_position = character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]
            if "Class_Room" in now_scene_data.scene_tag:
                return 1
    return 0


@add_premise(constant_promise.Premise.STUDENT_NOT_STUDY_IN_CLASSROOM)
def handle_student_not_study_in_classroom(character_id: int) -> int:
    """
    教室里有没在上课的学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        # 首先需要是学生，而且没有在上课
        if character_data.work.work_type == 152 and character_data.behavior.behavior_id != constant.Behavior.ATTENT_CLASS:
            # 接着需要地点在教室里
            now_position = character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]
            if "Class_Room" in now_scene_data.scene_tag:
                return 1
    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_NOT_MASSAGE_THERAPIST)
def handle_scene_someone_not_massage_therapist(character_id: int) -> int:
    """
    该地点有非按摩师的其他角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_work_is_massage_therapist,
    )
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    # 场景角色数大于等于2时进行检测
    if len(character_list) < 2:
        return 0
    # 遍历当前角色列表
    for chara_id in character_list:
        # 跳过玩家
        if chara_id == 0:
            continue
        if handle_work_is_massage_therapist(chara_id):
            continue
        return 1
    return 0

@add_premise(constant_promise.Premise.PLACE_EXPOSED)
def handle_place_exposed(character_id: int) -> int:
    """
    校验角色当前地点暴露
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.exposed:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_COVERT)
def handle_place_covert(character_id: int) -> int:
    """
    校验角色当前地点隐蔽
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.exposed:
        return 0
    return 1


@add_premise(constant_promise.Premise.PLACE_INDOOR)
def handle_place_indoor(character_id: int) -> int:
    """
    校验角色当前地点为室内
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    return now_scene_data.in_door


@add_premise(constant_promise.Premise.PLACE_OUTDOOR)
def handle_place_outdoor(character_id: int) -> int:
    """
    校验角色当前地点为室外
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_place_indoor(character_id)


@add_premise(constant_promise.Premise.PLACE_FURNITURE_GE_1)
def handle_place_furniture_ge_1(character_id: int) -> int:
    """
    校验角色当前地点有家具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.have_furniture:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_FURNITURE_GE_2)
def handle_place_furniture_ge_2(character_id: int) -> int:
    """
    当前地点至少有办公级家具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.have_furniture >= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_FURNITURE_1)
def handle_place_furniture_1(character_id: int) -> int:
    """
    当前地点仅有基础家具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.have_furniture == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_FURNITURE_2)
def handle_place_furniture_2(character_id: int) -> int:
    """
    当前地点为办公级家具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.have_furniture == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_FURNITURE_3)
def handle_place_furniture_3(character_id: int) -> int:
    """
    当前地点为卧室级家具（即含床）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.have_furniture == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_FURNITURE_0)
def handle_place_furniture_0(character_id: int) -> int:
    """
    校验角色当前地点没家具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.have_furniture:
        return 0
    return 1


@add_premise(constant_promise.Premise.PLACE_DOOR_LOCKABLE)
def handle_place_door_lockable(character_id: int) -> int:
    """
    当前地点可以正常锁门（非内隔间锁）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    return now_scene_data.close_type == 1


@add_premise(constant_promise.Premise.PLACE_DOOR_NOT_LOCKABLE)
def handle_place_door_not_lockable(character_id: int) -> int:
    """
    当前地点可以不能锁门（非内隔间锁）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_place_door_lockable(character_id)


@add_premise(constant_promise.Premise.PLACE_ALL_DOOR_LOCKABLE)
def handle_place_all_door_lockable(character_id: int) -> int:
    """
    当前地点可以正常锁门（含内隔间锁）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    return now_scene_data.close_type in {1, 2}


@add_premise(constant_promise.Premise.PLACE_DOOR_OPEN)
def handle_place_door_open(character_id: int) -> int:
    """
    地点的门是开着的（不含内隔间关门）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.close_flag == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_DOOR_CLOSE)
def handle_place_door_close(character_id: int) -> int:
    """
    地点的门是锁着的（不含内隔间关门）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.close_flag == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_INSIDE_DOOR_CLOSE)
def handle_place_inside_door_close(character_id: int) -> int:
    """
    地点的内隔间正关门中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.close_flag == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_INSIDE_DOOR_NOT_CLOSE)
def handle_place_inside_door_not_close(character_id: int) -> int:
    """
    该地点没有已关门的内隔间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_place_inside_door_close(character_id)


@add_premise(constant_promise.Premise.PLACE_LADIES_ONLY)
def handle_place_ladies_only(character_id: int) -> int:
    """
    该地点男士止步（女洗手间/更衣室/浴室等）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Ladies_Only" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.PALCE_IN_COLLECTION_LIST)
def handle_place_in_collection_list(character_id: int) -> int:
    """
    当前地点在收藏列表中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position in cache.collect_position_list:
        return 1
    return 0


@add_premise(constant_promise.Premise.PLACE_NOT_IN_COLLECTION_LIST)
def handle_place_not_in_collection_list(character_id: int) -> int:
    """
    当前地点不在收藏列表中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_place_in_collection_list(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.DR_OFFICE_NOT_FULL)
def handle_dr_office_not_full(character_id: int) -> int:
    """
    博士办公室未满员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_position = ['中枢', '博士办公室']
    now_position_str = map_handle.get_map_system_path_str_for_list(now_position)
    if map_handle.judge_scene_is_full(now_position_str):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_KITCHEN)
def handle_in_kitchen(character_id: int) -> int:
    """
    校验角色是否在厨房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Kitchen")


@add_premise(constant_promise.Premise.NOT_IN_KITCHEN)
def handle_not_in_kitchen(character_id: int) -> int:
    """
    校验角色是否不在厨房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_kitchen(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_DINING_HALL)
def handle_in_dining_hall(character_id: int) -> int:
    """
    校验角色是否在食堂中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Dining_hall")


@add_premise(constant_promise.Premise.NOT_IN_DINING_HALL)
def handle_not_in_dining_hall(character_id: int) -> int:
    """
    校验角色是否不在食堂中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_dining_hall(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_TAKE_FOOD)
def handle_in_take_food(character_id: int) -> int:
    """
    校验角色是否在取餐区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Take_Food_Area")


@add_premise(constant_promise.Premise.NOT_IN_TAKE_FOOD)
def handle_not_in_take_food(character_id: int) -> int:
    """
    校验角色是否不在取餐区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_take_food(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_FOOD_SHOP)
def handle_in_food_shop(character_id: int) -> int:
    """
    校验角色是否在食物商店
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Food_Shop")


@add_premise(constant_promise.Premise.NOT_IN_FOOD_SHOP)
def handle_not_in_food_shop(character_id: int) -> int:
    """
    校验角色是否不在食物商店
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_food_shop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_AI_FOOD_SHOP)
def handle_in_ai_food_shop(character_id: int) -> int:
    """
    在AI要去吃饭的食物商店
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    # 去食堂的
    if character_data.action_info.eat_food_restaurant == -1:
        if handle_in_take_food(character_id):
            return 1
    # 去指定餐厅的
    else:
        restaurant_id = character_data.action_info.eat_food_restaurant
        place_tag = game_config.config_restaurant[restaurant_id].tag_name
        if place_tag in now_scene_data.scene_tag:
            return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_AI_FOOD_SHOP)
def handle_not_in_ai_food_shop(character_id: int) -> int:
    """
    校验角色是否不在食物商店
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_ai_food_shop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_OFFICE)
def handle_in_office(character_id: int) -> int:
    """
    校验角色是否在办公室（含全部办公室）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    for single_tag in now_scene_data.scene_tag:
        if "Office" in single_tag:
            return 1
    return 0


@add_premise(constant_promise.Premise.IN_DR_OFFICE)
def handle_in_dr_office(character_id: int) -> int:
    """
    校验角色是否在博士办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Dr_Office")


@add_premise(constant_promise.Premise.NOT_IN_DR_OFFICE)
def handle_not_in_dr_office(character_id: int) -> int:
    """
    校验角色是否不在博士办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_dr_office(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_DR_OFFICE_OR_DEBUG)
def handle_in_dr_office_or_debug(character_id: int) -> int:
    """
    校验角色是否在博士办公室中或处于debug模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_dr_office(character_id) or cache.debug_mode:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_DR_ROOM)
def handle_in_dr_room(character_id: int) -> int:
    """
    校验角色是否在博士房间中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Dr_room")


@add_premise(constant_promise.Premise.IN_COMMAND_ROOM)
def handle_in_command_room(character_id: int) -> int:
    """
    校验角色是否在指挥室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Command_Room")


@add_premise(constant_promise.Premise.IN_OUT_EXIT)
def handle_in_out_exit(character_id: int) -> int:
    """
    在罗德岛出口
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Out_Exit")


@add_premise(constant_promise.Premise.IN_COMMAND_ROOM_OR_OUT_EXIT)
def handle_in_command_room_or_out_exit(character_id: int) -> int:
    """
    在指挥室或罗德岛出口
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_command_room(character_id) or handle_in_out_exit(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_DORMITORY)
def handle_in_dormitory(character_id: int) -> int:
    """
    校验角色是否在自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_list = map_handle.get_map_system_path_for_str(character_data.dormitory)
    # 因为在这里出现过BUG，所以加一个额外的修正判定，强制将博士的宿舍定为中枢\博士房间
    if character_id == 0 and character_data.dormitory == "":
        character_data.dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"])
    # 在其他语言中将被翻译的宿舍名进行修正
    elif scene_list[0] == _("中枢") or scene_list[0] == _("控制中枢"):
        character_data.dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"])
    # print(f"debug {character_data.name}的宿舍前提判定，当前位置为{now_position}，宿舍位置为{character_data.dormitory}")
    return now_position == character_data.dormitory


@add_premise(constant_promise.Premise.NOT_IN_DORMITORY)
def handle_not_in_dormitory(character_id: int) -> int:
    """
    校验角色是否不在自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_dormitory(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_DORMITORY_OR_HOTEL)
def handle_in_dormitory_or_hotel(character_id: int) -> int:
    """
    在自己宿舍中或在已经入住的旅馆中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_dormitory(character_id):
        return 1
    elif cache.rhodes_island.love_hotel_room_lv > 0 and handle_in_love_hotel(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_TARGET_DORMITORY)
def handle_in_target_dormitory(character_id: int) -> int:
    """
    校验角色是否在自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_in_dormitory(character_data.target_character_id)


@add_premise(constant_promise.Premise.IN_TOILET_MAN)
def handle_in_toilet_man(character_id: int) -> int:
    """
    校验角色是否在男士洗手间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Toilet_Male")


@add_premise(constant_promise.Premise.IN_TOILET_FEMALE)
def handle_in_toilet_female(character_id: int) -> int:
    """
    校验角色是否在女士洗手间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Toilet_Female")


@add_premise(constant_promise.Premise.NOT_IN_TOILET_FEMALE)
def handle_not_in_toilet_female(character_id: int) -> int:
    """
    校验角色是否不在女士洗手间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_toilet_female(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_IN_TOILET)
def handle_not_in_toilet(character_id: int) -> int:
    """
    校验角色是否不在洗手间（含宿舍）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Toilet_Male" in now_scene_data.scene_tag:
        return 0
    if "Toilet_Female" in now_scene_data.scene_tag:
        return 0
    if "Dormitory" in now_scene_data.scene_tag:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_TOILET_OR_DORMITORY)
def handle_in_toilet_or_dormitory(character_id: int) -> int:
    """
    在洗手间或自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_not_in_toilet(character_id)


@add_premise(constant_promise.Premise.IN_REST_ROOM)
def handle_in_rest_room(character_id: int) -> int:
    """
    校验角色是否在休息室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Rest_Room")


@add_premise(constant_promise.Premise.NOT_IN_REST_ROOM)
def handle_not_in_rest_room(character_id: int) -> int:
    """
    校验角色是否不在休息室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_rest_room(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_REST_ROOM_OR_DORMITORY)
def handle_in_rest_room_or_dormitory(character_id: int) -> int:
    """
    校验角色是否在休息室或自己宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_rest_room(character_id):
        return 1
    elif handle_in_dormitory(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_CORRIDOR)
def handle_in_corridor(character_id: int) -> int:
    """
    校验角色是否在走廊中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Corridor")


@add_premise(constant_promise.Premise.IN_POWER_DISPATCH)
def handle_in_power_dispatch(character_id: int) -> int:
    """
    校验角色是否在动力控制室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Power_Dispatch")


@add_premise(constant_promise.Premise.NOT_IN_POWER_DISPATCH)
def handle_not_in_power_dispatch(character_id: int) -> int:
    """
    校验角色是否不在动力控制室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_power_dispatch(character_id)

@add_premise(constant_promise.Premise.IN_HUMAN_POWER_ROOM)
def handle_in_human_power_room(character_id: int) -> int:
    """
    校验角色是否在人力发电室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Human_Power_Room")

@add_premise(constant_promise.Premise.NOT_IN_HUMAN_POWER_ROOM)
def handle_not_in_human_power_room(character_id: int) -> int:
    """
    校验角色是否不在人力发电室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_human_power_room(character_id)

@add_premise(constant_promise.Premise.IN_MUSIC_ROOM)
def handle_in_music_room(character_id: int) -> int:
    """
    校验角色是否在音乐室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Modern_Musicroom" in now_scene_data.scene_tag:
        return 1
    if "Classic_Musicroom" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_CLASSIC_MUSIC_ROOM)
def handle_in_classic_music_room(character_id: int) -> int:
    """
    校验角色是否在夕照区音乐室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Classic_Musicroom")

@add_premise(constant_promise.Premise.NOT_IN_CLASSIC_MUSIC_ROOM)
def handle_not_in_classic_music_room(character_id: int) -> int:
    """
    校验角色是否不在夕照区音乐室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_classic_music_room(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_MODEN_MUSIC_ROOM)
def handle_in_moden_music_room(character_id: int) -> int:
    """
    校验角色是否在现代音乐排练室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Modern_Musicroom")

@add_premise(constant_promise.Premise.NOT_IN_MODEN_MUSIC_ROOM)
def handle_not_in_moden_music_room(character_id: int) -> int:
    """
    校验角色是否不在现代音乐排练室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_moden_music_room(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_MULTIMEDIA_ROOM)
def handle_in_multimedia_room(character_id: int) -> int:
    """
    校验角色是否在多媒体室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Multimedia_Room")

@add_premise(constant_promise.Premise.NOT_IN_MULTIMEDIA_ROOM)
def handle_not_in_multimedia_room(character_id: int) -> int:
    """
    校验角色是否不在多媒体室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_multimedia_room(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_PHOTOGRAPHY_STUDIO)
def handle_in_photography_studio(character_id: int) -> int:
    """
    校验角色是否在摄影爱好者影棚中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Photography_Studio")

@add_premise(constant_promise.Premise.NOT_IN_PHOTOGRAPHY_STUDIO)
def handle_not_in_photography_studio(character_id: int) -> int:
    """
    校验角色是否不在摄影爱好者影棚中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_photography_studio(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_AQUAPIT_EXPERIENTORIUM)
def handle_in_aquapit_experientorium(character_id: int) -> int:
    """
    校验角色是否在大水坑快活体验屋中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Aquapit_Experientorium")

@add_premise(constant_promise.Premise.NOT_IN_AQUAPIT_EXPERIENTORIUM)
def handle_not_in_aquapit_experientorium(character_id: int) -> int:
    """
    校验角色是否不在大水坑快活体验屋中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_aquapit_experientorium(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_BOARD_GAMES_ROOM)
def handle_in_board_games_room(character_id: int) -> int:
    """
    校验角色是否在棋牌室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Board_Games_Room")

@add_premise(constant_promise.Premise.NOT_IN_BOARD_GAMES_ROOM)
def handle_not_in_board_games_room(character_id: int) -> int:
    """
    校验角色是否不在棋牌室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_board_games_room(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_FAIRY_BANQUET)
def handle_in_fairy_banquet(character_id: int) -> int:
    """
    校验角色是否在糖果仙子宴会厅中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Fairy_Banquet")

@add_premise(constant_promise.Premise.NOT_IN_FAIRY_BANQUET)
def handle_not_in_fairy_banquet(character_id: int) -> int:
    """
    校验角色是否不在糖果仙子宴会厅中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_fairy_banquet(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_COMMERCE_ZONE)
def handle_in_commerce_zone(character_id: int) -> int:
    """
    校验角色是否在贸易区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] == "贸易":
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_IN_COMMERCE_ZONE)
def handle_not_in_commerce_zone(character_id: int) -> int:
    """
    校验角色是否不在贸易区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_commerce_zone(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_BROADCAST_CENTER)
def handle_in_broadcast_center(character_id: int) -> int:
    """
    校验角色是否在直播间中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Broadcast_Center")

@add_premise(constant_promise.Premise.NOT_IN_BROADCAST_CENTER)
def handle_not_in_broadcast_center(character_id: int) -> int:
    """
    校验角色是否不在直播间中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_broadcast_center(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_AVANT_GARDE_ARCADE)
def handle_in_avant_garde_arcade(character_id: int) -> int:
    """
    校验角色是否在前卫街机厅中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Avant_Garde_Arcade")

@add_premise(constant_promise.Premise.NOT_IN_AVANT_GARDE_ARCADE)
def handle_not_in_avant_garde_arcade(character_id: int) -> int:
    """
    校验角色是否不在前卫街机厅中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_avant_garde_arcade(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_SWIMMING_POOL)
def handle_in_swimming_pool(character_id: int) -> int:
    """
    校验角色是否在游泳池中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Swimming_Pool")

@add_premise(constant_promise.Premise.NOT_IN_SWIMMING_POOL)
def handle_not_in_swimming_pool(character_id: int) -> int:
    """
    校验角色是否不在游泳池中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_swimming_pool(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_BAR)
def handle_in_bar(character_id: int) -> int:
    """
    校验角色是否在酒吧中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Bar")

@add_premise(constant_promise.Premise.NOT_IN_BAR)
def handle_not_in_bar(character_id: int) -> int:
    """
    校验角色是否不在酒吧中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_bar(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_HAIR_SALON)
def handle_in_hair_salon(character_id: int) -> int:
    """
    校验角色是否在理发店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Hair_Salon")

@add_premise(constant_promise.Premise.NOT_IN_HAIR_SALON)
def handle_not_in_hair_salon(character_id: int) -> int:
    """
    校验角色是否不在理发店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_hair_salon(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_STYLING_STUDIO)
def handle_in_styling_studio(character_id: int) -> int:
    """
    校验角色是否在造型工作室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Styling_Studio")

@add_premise(constant_promise.Premise.NOT_IN_STYLING_STUDIO)
def handle_not_in_styling_studio(character_id: int) -> int:
    """
    校验角色是否不在造型工作室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_styling_studio(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_WALYRIA_CAKE_SHOP)
def handle_in_walyria_cake_shop(character_id: int) -> int:
    """
    校验角色是否在瓦莱丽蛋糕店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Walyria_Cake_Shop")

@add_premise(constant_promise.Premise.NOT_IN_WALYRIA_CAKE_SHOP)
def handle_not_in_walyria_cake_shop(character_id: int) -> int:
    """
    校验角色是否不在瓦莱丽蛋糕店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_walyria_cake_shop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_RESTAURANT)
def handle_in_restaurant(character_id: int) -> int:
    """
    校验角色是否在餐馆（含所有正餐餐馆）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Restaurant")


@add_premise(constant_promise.Premise.NOT_IN_RESTAURANT)
def handle_not_in_restaurant(character_id: int) -> int:
    """
    校验角色是否不在餐馆（含所有正餐餐馆）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_restaurant(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_SEVEN_CITIES_RESTAURANT)
def handle_in_seven_cities_restaurant(character_id: int) -> int:
    """
    校验角色是否在七城风情餐厅中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Seven_Cities_Restaurant")

@add_premise(constant_promise.Premise.NOT_IN_SEVEN_CITIES_RESTAURANT)
def handle_not_in_seven_cities_restaurant(character_id: int) -> int:
    """
    校验角色是否不在七城风情餐厅中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_seven_cities_restaurant(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_GOLDEN_GAME_ROOM)
def handle_in_golden_game_room(character_id: int) -> int:
    """
    校验角色是否在黄澄澄游戏室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Golden_Game_Room")

@add_premise(constant_promise.Premise.NOT_IN_GOLDEN_GAME_ROOM)
def handle_not_in_golden_game_room(character_id: int) -> int:
    """
    校验角色是否不在黄澄澄游戏室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_golden_game_room(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_TEAHOUSE)
def handle_in_teahouse(character_id: int) -> int:
    """
    校验角色是否在山城茶馆中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Teahouse")

@add_premise(constant_promise.Premise.NOT_IN_TEAHOUSE)
def handle_not_in_teahouse(character_id: int) -> int:
    """
    校验角色是否不在山城茶馆中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_teahouse(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_BURGER)
def handle_in_burger_joint(character_id: int) -> int:
    """
    校验角色是否在约翰老妈汉堡店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Burger")

@add_premise(constant_promise.Premise.NOT_IN_BURGER)
def handle_not_in_burger_joint(character_id: int) -> int:
    """
    校验角色是否不在约翰老妈汉堡店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_burger_joint(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_HEALTHY_DINER)
def handle_in_healthy_diner(character_id: int) -> int:
    """
    校验角色是否在健康快餐店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Healthy_Diner")

@add_premise(constant_promise.Premise.NOT_IN_HEALTHY_DINER)
def handle_not_in_healthy_diner(character_id: int) -> int:
    """
    校验角色是否不在健康快餐店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_healthy_diner(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_LUNGMEN_EATERY)
def handle_in_lungmen_eatery(character_id: int) -> int:
    """
    校验角色是否在龙门食坊中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Lungmen_Eatery")

@add_premise(constant_promise.Premise.NOT_IN_LUNGMEN_EATERY)
def handle_not_in_lungmen_eatery(character_id: int) -> int:
    """
    校验角色是否不在龙门食坊中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_lungmen_eatery(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_PIZZERIA)
def handle_in_pizzeria(character_id: int) -> int:
    """
    校验角色是否在快捷连锁披萨店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Pizzeria")

@add_premise(constant_promise.Premise.NOT_IN_PIZZERIA)
def handle_not_in_pizzeria(character_id: int) -> int:
    """
    校验角色是否不在快捷连锁披萨店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_pizzeria(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_CAFÉ)
def handle_in_café(character_id: int) -> int:
    """
    校验角色是否在哥伦比亚咖啡中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Café")

@add_premise(constant_promise.Premise.NOT_IN_CAFÉ)
def handle_not_in_café(character_id: int) -> int:
    """
    校验角色是否不在哥伦比亚咖啡中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_café(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.IN_LIGHT_STORE)
def handle_in_light_store(character_id: int) -> int:
    """
    校验角色是否在花草灯艺屋中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return common_place_judge_by_SceneTag(character_id, "Light_Store")

@add_premise(constant_promise.Premise.NOT_IN_LIGHT_STORE)
def handle_not_in_light_store(character_id: int) -> int:
    """
    校验角色是否不在花草灯艺屋中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_light_store(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_LIBRARY)
def handle_in_library(character_id: int) -> int:
    """
    校验角色是否在图书馆中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Library" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_LIBRARY_ZONE)
def handle_in_library_zone(character_id: int) -> int:
    """
    校验角色是否在图书馆区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] == "书":
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_LIBRARY)
def handle_not_in_library(character_id: int) -> int:
    """
    校验角色是否不在图书馆中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_library(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_COLLECTION_ROOM)
def handle_in_collection_room(character_id: int) -> int:
    """
    校验角色是否在藏品馆中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Collection" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_GYM_ROOM)
def handle_in_gym_room(character_id: int) -> int:
    """
    校验角色是否在健身区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Gym" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_GYM_ROOM)
def handle_not_in_gym_room(character_id: int) -> int:
    """
    校验角色是否不在健身区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_gym_room(character_id)


@add_premise(constant_promise.Premise.IN_TRAINING_ROOM)
def handle_in_training_room(character_id: int) -> int:
    """
    校验角色是否在训练室中（包括木桩房和射击房）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Training_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_TRAINING_ROOM)
def handle_not_in_training_room(character_id: int) -> int:
    """
    校验角色是否不在训练室中（包括木桩房和射击房）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_training_room(character_id)


@add_premise(constant_promise.Premise.IN_FIGHT_ROOM)
def handle_in_fight_room(character_id: int) -> int:
    """
    校验角色是否在木桩房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Fight_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_SHOOT_ROOM)
def handle_in_shoot_room(character_id: int) -> int:
    """
    校验角色是否在射击房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Shoot_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_BUILDING_ROOM)
def handle_in_building_room(character_id: int) -> int:
    """
    校验角色是否在基建部中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Building_Room" in now_scene_data.scene_tag:
        return 1
    return 0

@add_premise(constant_promise.Premise.IN_SERVER_ROOM)
def handle_in_server_room(character_id: int) -> int:
    """
    校验角色是否在机房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Server_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_BLACKSMITH_SHOP)
def handle_in_blacksmith_shop(character_id: int) -> int:
    """
    校验角色是否在铁匠铺中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Blacksmith_Shop" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_BLACKSMITH_SHOP)
def handle_not_in_blacksmith_shop(character_id: int) -> int:
    """
    校验角色是否不在铁匠铺中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Blacksmith_Shop" in now_scene_data.scene_tag:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_MAINTENANCE_DEPARTMENT)
def handle_in_maintenance_department(character_id: int) -> int:
    """
    校验角色是否在运维部中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Maintenance_Department" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_MAINTENANCE_DEPARTMENT)
def handle_not_in_maintenance_department(character_id: int) -> int:
    """
    校验角色是否不在运维部中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Maintenance_Department" in now_scene_data.scene_tag:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_MAINTENANCE_PLACE)
def handle_in_maintenance_place(character_id: int) -> int:
    """
    校验角色是否在自己对应的检修地点(maintenance_place)中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    if character_id in cache.rhodes_island.maintenance_place and now_scene_str == cache.rhodes_island.maintenance_place[character_id]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_MAINTENANCE_PLACE)
def handle_not_in_maintenance_place(character_id: int) -> int:
    """
    校验角色是否不在自己对应的检修地点(maintenance_place)中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    if character_id in cache.rhodes_island.maintenance_place and now_scene_str == cache.rhodes_island.maintenance_place[character_id]:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_ANY_MAINTENANCE_PLACE)
def handle_in_any_maintenance_place(character_id: int) -> int:
    """
    校验角色是否在任意检修地点中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    if now_scene_str == cache.rhodes_island.facility_damage_data:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_DR_OFF_OR_SERVER_ROOM_OR_DEBUG)
def handle_in_dr_off_or_server_room_or_debug(character_id: int) -> int:
    """
    校验角色是否在博士办公室/机房/debug模式中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Server_Room" in now_scene_data.scene_tag:
        return 1
    elif "Dr_Office" in now_scene_data.scene_tag:
        return 1
    elif cache.debug_mode:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_MEDICAL_ZONE)
def handle_in_medical_zone(character_id: int) -> int:
    """
    校验角色是否在医疗部中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] == "医疗":
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_CLINIC)
def handle_in_clinic(character_id: int) -> int:
    """
    校验角色是否在门诊室中（含急诊室）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Clinic" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_CLINIC)
def handle_not_in_clinic(character_id: int) -> int:
    """
    校验角色是否不在门诊室中（含急诊室）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_clinic(character_id)

@add_premise(constant_promise.Premise.IN_PHYSICAL_EXAMINATION)
def handle_in_physical_examination(character_id: int) -> int:
    """
    校验角色是否在体检科中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Physical_Examination" in now_scene_data.scene_tag:
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_IN_PHYSICAL_EXAMINATION)
def handle_not_in_physical_examination(character_id: int) -> int:
    """
    校验角色是否不在体检科中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_physical_examination(character_id)


@add_premise(constant_promise.Premise.IN_SURGERY_ROOM)
def handle_in_surgery_room(character_id: int) -> int:
    """
    校验角色是否在手术室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Surgery_Room" in now_scene_data.scene_tag:
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_IN_SURGERY_ROOM)
def handle_not_in_surgery_room(character_id: int) -> int:
    """
    校验角色是否不在手术室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_surgery_room(character_id)

@add_premise(constant_promise.Premise.IN_INPATIENT_DEPARTMENT)
def handle_in_inpatient_department(character_id: int) -> int:
    """
    校验角色是否在住院部中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Inpatient_Department" in now_scene_data.scene_tag:
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_IN_INPATIENT_DEPARTMENT)
def handle_not_in_inpatient_department(character_id: int) -> int:
    """
    校验角色是否不在住院部中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_inpatient_department(character_id)

@add_premise(constant_promise.Premise.IN_MEDICAL_OFFICE)
def handle_in_medical_office(character_id: int) -> int:
    """
    校验角色是否在医疗部办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Medical_Office" in now_scene_data.scene_tag:
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_IN_MEDICAL_OFFICE)
def handle_not_in_medical_office(character_id: int) -> int:
    """
    校验角色是否不在医疗部办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_medical_office(character_id)

@add_premise(constant_promise.Premise.IN_HR_OFFICE)
def handle_in_hr_office(character_id: int) -> int:
    """
    校验角色是否在人事部办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "HR_Office" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_HR_OFFICE)
def handle_not_in_hr_office(character_id: int) -> int:
    """
    校验角色是否不在人事部办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_hr_office(character_id)


@add_premise(constant_promise.Premise.IN_HR_MEETING_ROOM)
def handle_in_hr_meeting_room(character_id: int) -> int:
    """
    校验角色是否在人事部会议室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "HR_Meeting_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_BATHROOM)
def handle_in_bathroom(character_id: int) -> int:
    """
    校验角色是否在淋浴区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Bathroom" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_BATHROOM)
def handle_not_in_bathroom(character_id: int) -> int:
    """
    校验角色是否不在淋浴区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_bathroom(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_BATHROOM_EXCEPT_DR_ROOM)
def handle_in_bathroom_except_dr_room(character_id: int) -> int:
    """
    校验角色是否在淋浴区且不在博士房间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Bathroom" in now_scene_data.scene_tag and "Dr_room" not in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_FOOT_BATH)
def handle_in_foot_bath(character_id: int) -> int:
    """
    校验角色是否在足浴区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Foot_Bath" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_FOOT_BATH)
def handle_not_in_foot_bath(character_id: int) -> int:
    """
    校验角色是否不在足浴区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_foot_bath(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_SAUNA)
def handle_in_sauna(character_id: int) -> int:
    """
    校验角色是否在桑拿房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Sauna" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_SAUNA)
def handle_not_in_sauna(character_id: int) -> int:
    """
    校验角色是否不在桑拿房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_sauna(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_SPA_ROOM)
def handle_in_spa_room(character_id: int) -> int:
    """
    校验角色是否在水疗房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Spa_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_SPA_ROOM)
def handle_not_in_spa_room(character_id: int) -> int:
    """
    校验角色是否不在水疗房中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_spa_room(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_ONSEN)
def handle_in_onsen(character_id: int) -> int:
    """
    校验角色是否在温泉中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Onsen" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_ONSEN)
def handle_not_in_onsen(character_id: int) -> int:
    """
    校验角色是否不在温泉中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_onsen(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_LIBRARY_OFFICE)
def handle_in_library_office(character_id: int) -> int:
    """
    校验角色是否在图书馆办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Library_Office" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_LIBRARY_OFFICE)
def handle_not_in_library_office(character_id: int) -> int:
    """
    校验角色是否不在图书馆办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_library_office(character_id)


@add_premise(constant_promise.Premise.IN_LIBRARY_OR_LIBRARY_OFFICE)
def handle_in_library_or_library_office(character_id: int) -> int:
    """
    校验角色是否在图书馆或图书馆办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Library_Office" in now_scene_data.scene_tag or "Library" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_LIBRARY_OR_LIBRARY_OFFICE)
def handle_not_in_library_or_library_office(character_id: int) -> int:
    """
    校验角色是否不在图书馆或图书馆办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Library_Office" in now_scene_data.scene_tag or "Library" in now_scene_data.scene_tag:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_LOCKER_ROOM)
def handle_in_locker_room(character_id: int) -> int:
    """
    校验角色是否在任意更衣室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Locker_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_BATHZONE_LOCKER_ROOM)
def handle_in_bathzone_locker_room(character_id: int) -> int:
    """
    校验角色是否在大浴场的更衣室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Locker_Room" in now_scene_data.scene_tag and "大浴场" in now_scene_str:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_BATHZONE_LOCKER_ROOM)
def handle_not_in_bathzone_locker_room(character_id: int) -> int:
    """
    校验角色是否不在大浴场的更衣室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Locker_Room" in now_scene_data.scene_tag and "大浴场" in now_scene_str:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_BATHZONE_REST_ROOM)
def handle_in_bathzone_rest_room(character_id: int) -> int:
    """
    校验角色是否在大浴场的休息室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Rest_Room" in now_scene_data.scene_tag and "大浴场" in now_scene_str:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_BATHZONE_REST_ROOM)
def handle_not_in_bathzone_rest_room(character_id: int) -> int:
    """
    校验角色是否不在大浴场的休息室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Rest_Room" in now_scene_data.scene_tag and "大浴场" in now_scene_str:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_TRAINING_LOCKER_ROOM)
def handle_in_training_locker_room(character_id: int) -> int:
    """
    校验角色是否在训练场的更衣室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Locker_Room" in now_scene_data.scene_tag and "训练" in now_scene_str:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_TRAINING_LOCKER_ROOM)
def handle_not_in_training_locker_room(character_id: int) -> int:
    """
    校验角色是否不在训练场的更衣室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Locker_Room" in now_scene_data.scene_tag and "训练" in now_scene_str:
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_LOCKER_ROOM_OR_DORMITORY)
def handle_in_locker_room_or_dormitory(character_id: int) -> int:
    """
    校验角色是否在更衣室或宿舍
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Locker_Room" in now_scene_data.scene_tag or "Dormitory" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_NURSERY)
def handle_in_nursery(character_id: int) -> int:
    """
    校验角色是否在育儿室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Nursery" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_H_SHOP)
def handle_in_h_shop(character_id: int) -> int:
    """
    校验角色是否在成人用品商店
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "H_Shop" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_H_SHOP)
def handle_not_in_h_shop(character_id: int) -> int:
    """
    校验角色是否不在成人用品商店
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_h_shop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_RESOURCE_EXCHANGE)
def handle_in_resource_exchange(character_id: int) -> int:
    """
    校验角色是否在资源交易所
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Resource_Exchange" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_RESOURCE_EXCHANGE)
def handle_not_in_resource_exchange(character_id: int) -> int:
    """
    校验角色是否不在资源交易所
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_resource_exchange(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_LOVE_HOTEL)
def handle_in_love_hotel(character_id: int) -> int:
    """
    校验角色是否在爱情旅馆
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Love_Hotel" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_LOVE_HOTEL)
def handle_not_in_love_hotel(character_id: int) -> int:
    """
    校验角色是否不在爱情旅馆
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_love_hotel(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_PRODUCTION_WORKSHOP)
def handle_in_production_workshop(character_id: int) -> int:
    """
    校验角色是否在生产车间
    Keyword arguments:  
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Production_Workshop" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_PRODUCTION_WORKSHOP)
def handle_not_in_production_workshop(character_id: int) -> int:
    """
    校验角色是否不在生产车间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_production_workshop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_DIPLOMATIC_OFFICE)
def handle_in_diplomatic_office(character_id: int) -> int:
    """
    校验角色是否在外交办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Diplomatic_Office" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_DIPLOMATIC_OFFICE)
def handle_not_in_diplomatic_office(character_id: int) -> int:
    """
    校验角色是否不在外交办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_diplomatic_office(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_FIELD_ASSEMBLY_POINT)
def handle_in_field_assembly_point(character_id: int) -> int:
    """
    校验角色是否在外勤集合点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Field_Assembly_Point" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_FIELD_ASSEMBLY_POINT)
def handle_not_in_field_assembly_point(character_id: int) -> int:
    """
    校验角色是否不在外勤集合点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_field_assembly_point(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_GARAGE)
def handle_in_garage(character_id: int) -> int:
    """
    校验角色是否在格纳库
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Garage" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_GARAGE)
def handle_not_in_garage(character_id: int) -> int:
    """
    校验角色是否不在格纳库
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_garage(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_CLASS_ROOM)
def handle_in_class_room(character_id: int) -> int:
    """
    校验角色是否在教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Class_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_CLASS_ROOM)
def handle_not_in_class_room(character_id: int) -> int:
    """
    校验角色是否不在教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_class_room(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_HERB_GARDEN)
def handle_in_herb_garden(character_id: int) -> int:
    """
    校验角色是否在药田
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Herb_Garden" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_HERB_GARDEN)
def handle_not_in_herb_garden(character_id: int) -> int:
    """
    校验角色是否不在药田
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_herb_garden(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_GREENHOUSE)
def handle_in_greenhouse(character_id: int) -> int:
    """
    校验角色是否在温室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Greenhouse" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_GREENHOUSE)
def handle_not_in_greenhouse(character_id: int) -> int:
    """
    校验角色是否不在温室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_greenhouse(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_HERB_GARDEN_OR_GREENHOUSE)
def handle_in_herb_garden_or_greenhouse(character_id: int) -> int:
    """
    校验角色是否在药田或温室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_herb_garden(character_id) or handle_in_greenhouse(character_id):
        return 1
    return 0

@add_premise(constant_promise.Premise.IN_AROMATHERAPY_ROOM)
def handle_in_aromatherapy_room(character_id: int) -> int:
    """
    校验角色是否在香薰治疗室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Aromatherapy_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_AROMATHERAPY_ROOM)
def handle_not_in_aromatherapy_room(character_id: int) -> int:
    """
    校验角色是否不在香薰治疗室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_aromatherapy_room(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_BREEDING_FARM)
def handle_in_breeding_farm(character_id: int) -> int:
    """
    校验角色是否在磐蟹养殖场
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Breeding_Farm" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_BREEDING_FARM)
def handle_not_in_breeding_farm(character_id: int) -> int:
    """
    校验角色是否不在磐蟹养殖场
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_breeding_farm(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_TEACHER_OFFICE)
def handle_in_teacher_office(character_id: int) -> int:
    """
    校验角色是否在教师办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Teacher_Office" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_TEACHER_OFFICE)
def handle_not_in_teacher_office(character_id: int) -> int:
    """
    校验角色是否不在教师办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_teacher_office(character_id)


@add_premise(constant_promise.Premise.IN_DETENTION_AREA)
def handle_in_detention_area(character_id: int) -> int:
    """
    校验角色是否在关押区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    if "关押" in now_scene_str:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_DETENTION_AREA)
def handle_not_in_detention_area(character_id: int) -> int:
    """
    校验角色是否不在关押区
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_detention_area(character_id)


@add_premise(constant_promise.Premise.IN_PRISON)
def handle_in_prison(character_id: int) -> int:
    """
    校验角色是否在监牢
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Prison" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_PRISON)
def handle_not_in_prison(character_id: int) -> int:
    """
    校验角色是否不在监牢
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_prison(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_HUMILIATION_ROOM)
def handle_in_humiliation_room(character_id: int) -> int:
    """
    校验角色是否在调教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Humiliation_Room" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_HUMILIATION_ROOM)
def handle_not_in_humiliation_room(character_id: int) -> int:
    """
    校验角色是否不在调教室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_humiliation_room(character_id)


@add_premise(constant_promise.Premise.IN_WARDEN_OFFICE)
def handle_in_warden_office(character_id: int) -> int:
    """
    校验角色是否在监狱长办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Warden_Office" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_WARDEN_OFFICE)
def handle_not_in_warden_office(character_id: int) -> int:
    """
    校验角色是否不在监狱长办公室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_in_warden_office(character_id)


@add_premise(constant_promise.Premise.IN_HUMILIATION_ROOM_OR_DR_ROOM)
def handle_in_humiliation_room_or_dr_room(character_id: int) -> int:
    """
    校验角色是否在调教室或博士房间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_humiliation_room(character_id) or handle_in_dr_room(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_DECK)
def handle_in_deck(character_id: int) -> int:
    """
    校验角色是否在甲板
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if "Deck" in now_scene_data.scene_tag:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_DECK)
def handle_not_in_deck(character_id: int) -> int:
    """
    校验角色是否不在甲板
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_in_deck(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.IN_AEGIR)
def handle_in_aegir(character_id: int) -> int:
    """
    校验罗德岛是否在阿戈尔
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 1


@add_premise(constant_promise.Premise.IN_BOLIVAR)
def handle_in_bolivar(character_id: int) -> int:
    """
    校验罗德岛是否在玻利瓦尔
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 2

@add_premise(constant_promise.Premise.IN_HIGASHI)
def handle_in_higashi(character_id: int) -> int:
    """
    校验罗德岛是否在东
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 3

@add_premise(constant_promise.Premise.IN_COLUMBIA)
def handle_in_columbia(character_id: int) -> int:
    """
    校验罗德岛是否在哥伦比亚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 4

@add_premise(constant_promise.Premise.IN_KAZIMIERZ)
def handle_in_kazimierz(character_id: int) -> int:
    """
    校验罗德岛是否在卡西米尔
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 5

@add_premise(constant_promise.Premise.IN_KAZDEL)
def handle_in_kazdel(character_id: int) -> int:
    """
    校验罗德岛是否在卡兹戴尔
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 6

@add_premise(constant_promise.Premise.IN_LATERANO)
def handle_in_laterano(character_id: int) -> int:
    """
    校验罗德岛是否在拉特兰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 7

@add_premise(constant_promise.Premise.IN_LEITHANIEN)
def handle_in_leithanien(character_id: int) -> int:
    """
    校验罗德岛是否在莱塔尼亚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 8

@add_premise(constant_promise.Premise.IN_RIM_BILLITON)
def handle_in_rim_billiton(character_id: int) -> int:
    """
    校验罗德岛是否在雷姆必拓
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 9

@add_premise(constant_promise.Premise.IN_MINOS)
def handle_in_minos(character_id: int) -> int:
    """
    校验罗德岛是否在米诺斯
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 10

@add_premise(constant_promise.Premise.IN_SARGON)
def handle_in_sargon(character_id: int) -> int:
    """
    校验罗德岛是否在萨尔贡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 11

@add_premise(constant_promise.Premise.IN_SAMI)
def handle_in_sami(character_id: int) -> int:
    """
    校验罗德岛是否在萨米
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 12

@add_premise(constant_promise.Premise.IN_VICTORIA)
def handle_in_victoria(character_id: int) -> int:
    """
    校验罗德岛是否在维多利亚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 13

@add_premise(constant_promise.Premise.IN_URSUS)
def handle_in_ursus(character_id: int) -> int:
    """
    校验罗德岛是否在乌萨斯
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 14

@add_premise(constant_promise.Premise.IN_KJERAG)
def handle_in_kjerag(character_id: int) -> int:
    """
    校验罗德岛是否在谢拉格
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 15

@add_premise(constant_promise.Premise.IN_SIRACUSA)
def handle_in_siracusa(character_id: int) -> int:
    """
    校验罗德岛是否在叙拉古
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 16

@add_premise(constant_promise.Premise.IN_YAN)
def handle_in_yan(character_id: int) -> int:
    """
    校验罗德岛是否在炎
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 17

@add_premise(constant_promise.Premise.IN_IBERIA)
def handle_in_iberia(character_id: int) -> int:
    """
    校验罗德岛是否在伊比利亚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 18

@add_premise(constant_promise.Premise.IN_DURIN)
def handle_in_durin(character_id: int) -> int:
    """
    校验罗德岛是否在杜林
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 19

@add_premise(constant_promise.Premise.IN_SIESTA)
def handle_in_siesta(character_id: int) -> int:
    """
    校验罗德岛是否在汐斯塔
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 20

@add_premise(constant_promise.Premise.IN_NORTHERN)
def handle_in_northern(character_id: int) -> int:
    """
    校验罗德岛是否在北地
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 21

@add_premise(constant_promise.Premise.IN_FOEHN_HOTLANDS)
def handle_in_foehn_hotlands(character_id: int) -> int:
    """
    校验罗德岛是否在焚风热土
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 22

@add_premise(constant_promise.Premise.IN_KARLAN)
def handle_in_karlan(character_id: int) -> int:
    """
    校验罗德岛是否在喀兰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 23

@add_premise(constant_promise.Premise.IN_DAN)
def handle_in_dan(character_id: int) -> int:
    """
    校验罗德岛是否在檀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 24

@add_premise(constant_promise.Premise.IN_VOUVIRE)
def handle_in_vouivre(character_id: int) -> int:
    """
    校验罗德岛是否在瓦伊凡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 25

@add_premise(constant_promise.Premise.IN_INFY_ICEFIELD)
def handle_in_infy_icefield(character_id: int) -> int:
    """
    校验罗德岛是否在无尽冰原
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_country = cache.rhodes_island.current_location[0]
    return now_country == 26


@add_premise(constant_promise.Premise.MOVE_TO_TOILET_FEMALE)
def handle_move_to_toilet_female(character_id: int) -> int:
    """
    校验角色抵达女士洗手间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if (
            character_data.behavior.move_target == character_data.position
            and "Toilet_Female" in now_scene_data.scene_tag
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.MOVE_TO_LOCKER_ROOM)
def handle_move_to_locker_room(character_id: int) -> int:
    """
    角色抵达更衣室
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if (
            character_data.behavior.move_target == character_data.position
            and "Locker_Room" in now_scene_data.scene_tag
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.MOVE_TO_DORMITORY)
def handle_move_to_dormitory(character_id: int) -> int:
    """
    角色抵达宿舍
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if (
            character_data.behavior.move_target == character_data.position
            and "Dormitory" in now_scene_data.scene_tag
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.MOVE_FROM_DORMITORY)
def handle_move_from_dormitory(character_id: int) -> int:
    """
    角色离开宿舍
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    src_scene_str = map_handle.get_map_system_path_str_for_list(character_data.behavior.move_src)
    if character_id == 0 and src_scene_str != "":
        src_scene_data = cache.scene_data[src_scene_str]
        # print(f"debug move_src = {character_data.behavior.move_src},place_name = {src_scene_data.scene_name},tag = {src_scene_data.scene_tag}")
        # print(f"debug now_position = {now_position},place_name = {now_scene_data.scene_name},tag = {now_scene_data.scene_tag}")
        if "Dormitory" in src_scene_data.scene_tag:
            return 1
    return 0


@add_premise(constant_promise.Premise.MOVE_TO_LADIES_ONLY)
def handle_move_to_ladies_only(character_id: int) -> int:
    """
    角色抵达男士止步的地点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if (
            character_data.behavior.move_target == character_data.position
            and "Ladies_Only" in now_scene_data.scene_tag
    ):
        return 1
    return 0


@add_premise(constant_promise.Premise.MOVE_TO_SOMEONE_MASTUREBATE)
def handle_move_to_someone_masturebate(character_id: int) -> int:
    """
    角色抵达有人自慰的地点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if (
        character_data.behavior.move_target == character_data.position and
        len(now_scene_data.character_list) >= 2
    ):
        # 遍历当前角色列表
        for chara_id in now_scene_data.character_list:
            # 遍历非自己且非玩家的角色
            if chara_id != character_id and chara_id != 0:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                # 检测是否在自慰
                if other_character_data.behavior.behavior_id == constant.Behavior.MASTUREBATE:
                    return 1
    return 0


@add_premise(constant_promise.Premise.NOT_MOVE_TO_SOMEONE_MASTUREBATE)
def handle_not_move_to_someone_masturebate(character_id: int) -> int:
    """
    角色抵达的地点没有人自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_move_to_someone_masturebate(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.MOVE_NOT_FINISH)
def handle_move_not_finish(character_id: int) -> int:
    """
    角色移动未完成(权重为10)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.move_final_target != []:
        return 10
    return 0
