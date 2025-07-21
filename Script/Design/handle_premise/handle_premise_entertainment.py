
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type
from Script.Design import game_time, map_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

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


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_READ)
def handle_entertainment_is_read(character_id: int) -> int:
    """
    自己当前时段的娱乐为读书
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 101


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_SING)
def handle_entertainment_is_sing(character_id: int) -> int:
    """
    自己当前时段的娱乐为唱歌
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 51


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_CLASSIC_INSTRUMENT)
def handle_entertainment_is_play_classic_instrument(character_id: int) -> int:
    """
    自己当前时段的娱乐为演奏传统乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 53


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_MODEN_INSTRUMENT)
def handle_ENTERTAINMENT_IS_PLAY_MODEN_INSTRUMENT(character_id: int) -> int:
    """
    自己当前时段的娱乐为演奏现代乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 54


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_WATCH_MOVIE)
def handle_entertainment_is_watch_movie(character_id: int) -> int:
    """
    自己当前时段的娱乐为看电影
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 55


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PHOTOGRAPHY)
def handle_entertainment_is_photography(character_id: int) -> int:
    """
    自己当前时段的娱乐为摄影
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 56


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_WATER)
def handle_entertainment_is_play_water(character_id: int) -> int:
    """
    自己当前时段的娱乐为玩水
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 57


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_CHESS)
def handle_entertainment_is_play_chess(character_id: int) -> int:
    """
    自己当前时段的娱乐为下棋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 58


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_MAHJONG)
def handle_entertainment_is_play_mahjong(character_id: int) -> int:
    """
    自己当前时段的娱乐为打麻将
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 59


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_CARDS)
def handle_entertainment_is_play_cards(character_id: int) -> int:
    """
    自己当前时段的娱乐为打牌
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 60


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_REHEARSE_DANCE)
def handle_entertainment_is_rehearse_dance(character_id: int) -> int:
    """
    自己当前时段的娱乐为排演舞剧
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 61


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_ARCADE_GAME)
def handle_entertainment_is_play_arcade_game(character_id: int) -> int:
    """
    自己当前时段的娱乐为玩街机游戏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 111


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_SWIMMING)
def handle_entertainment_is_swimming(character_id: int) -> int:
    """
    自己当前时段的娱乐为游泳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 91


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_WINE)
def handle_entertainment_is_taste_wine(character_id: int) -> int:
    """
    自己当前时段的娱乐为品酒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 62


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_TEA)
def handle_entertainment_is_taste_tea(character_id: int) -> int:
    """
    自己当前时段的娱乐为品茶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 112


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_COFFEE)
def handle_entertainment_is_taste_coffee(character_id: int) -> int:
    """
    自己当前时段的娱乐为品咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 113


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_DESSERT)
def handle_entertainment_is_taste_dessert(character_id: int) -> int:
    """
    自己当前时段的娱乐为品尝点心
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 114


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_TASTE_FOOD)
def handle_entertainment_is_taste_food(character_id: int) -> int:
    """
    自己当前时段的娱乐为品尝美食
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 115


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_PLAY_HOUSE)
def handle_entertainment_is_play_house(character_id: int) -> int:
    """
    自己当前时段的娱乐为过家家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 151


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_STYLE_HAIR)
def handle_entertainment_is_style_hair(character_id: int) -> int:
    """
    自己当前时段的娱乐为修整发型
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 116


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_FULL_BODY_STYLING)
def handle_entertainment_is_full_body_styling(character_id: int) -> int:
    """
    自己当前时段的娱乐为全身造型服务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 117


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_BATHHOUSE_TYPE)
def handle_entertainment_is_bathhouse_type(character_id: int) -> int:
    """
    自己当前时段的娱乐为大浴场类的娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    for cid in {171,172,173,174,175,176}:
        if character_data.entertainment.entertainment_type[i] == cid:
            return 1

    return 0


@add_premise(constant_promise.Premise.SCENE_SOMEONE_ENTERTAINMENT_IS_BATHHOUSE_TYPE)
def handle_scene_someone_entertainment_is_bathhouse_type(character_id: int) -> int:
    """
    当前场景里有人当前时段的娱乐为大浴场类的娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于1时进行检测
    if len(scene_data.character_list) > 1:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 遍历非自己的角色
            if chara_id != character_id:
                other_character_data: game_type.Character = cache.character_data[chara_id]

                # 开始判定
                i = game_time.judge_entertainment_time(character_id)
                if i:
                    i -= 1
                else:
                    continue

                for cid in {171,172,173,174,175,176}:
                    if other_character_data.entertainment.entertainment_type[i] == cid:
                        return 1

    return 0


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_BATHHOUSE_SHOWER_CLOTH_TYPE)
def handle_entertainment_is_bathhouse_shower_cloth_type(character_id: int) -> int:
    """
    自己当前时段的娱乐为大浴场类_需要换浴衣的娱乐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    for cid in {172,173,174}:
        if character_data.entertainment.entertainment_type[i] == cid:
            return 1

    return 0


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_SOAK_FEET)
def handle_entertainment_is_soak_feet(character_id: int) -> int:
    """
    自己当前时段的娱乐为泡脚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 171


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_STEAM_SAUNA)
def handle_entertainment_is_steam_sauna(character_id: int) -> int:
    """
    自己当前时段的娱乐为蒸桑拿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 172


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_HYDROTHERAPY_TREATMENT)
def handle_entertainment_is_hydrotherapy_treatment(character_id: int) -> int:
    """
    自己当前时段的娱乐为水疗护理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 173


@add_premise(constant_promise.Premise.ENTERTAINMENT_IS_ONSEN_BATH)
def handle_entertainment_is_onsen_bath(character_id: int) -> int:
    """
    自己当前时段的娱乐为泡温泉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]

    i = game_time.judge_entertainment_time(character_id)
    if i:
        i -= 1
    else:
        return 0

    return character_data.entertainment.entertainment_type[i] == 174

