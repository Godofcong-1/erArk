from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
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


@add_premise(constant_promise.Premise.H_IN_LOVE_HOTEL)
def handle_h_in_love_hotel(character_id: int) -> int:
    """
    当前正在爱情旅馆中H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.h_in_love_hotel:
        return 1
    return 0


@add_premise(constant_promise.Premise.H_NOT_IN_LOVE_HOTEL)
def handle_h_not_in_love_hotel(character_id: int) -> int:
    """
    当前不在爱情旅馆中H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_h_in_love_hotel(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_LIVE_IN_LOVE_HOTEL)
def handle_not_live_inlove_hotel(character_id: int) -> int:
    """
    还未在爱情旅馆中入住
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.LIVE_IN_LOVE_HOTEL)
def handle_live_inlove_hotel(character_id: int) -> int:
    """
    已在爱情旅馆中入住
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.LOVE_HOTEL_ROOM_V1)
def handle_love_hotel_room_v1(character_id: int) -> int:
    """
    在爱情旅馆中入住房间为标间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.LOVE_HOTEL_ROOM_V2)
def handle_love_hotel_room_v2(character_id: int) -> int:
    """
    在爱情旅馆中入住房间为情趣主题房
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.LOVE_HOTEL_ROOM_V3)
def handle_love_hotel_room_v3(character_id: int) -> int:
    """
    在爱情旅馆中入住房间为顶级套房
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.love_hotel_room_lv == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.H_IN_BATHROOM)
def handle_h_in_bathroom(character_id: int) -> int:
    """
    当前正在浴室中H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.h_in_bathroom:
        return 1
    return 0


@add_premise(constant_promise.Premise.H_NOT_IN_BATHROOM)
def handle_h_not_in_bathroom(character_id: int) -> int:
    """
    当前不在浴室中H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_h_in_bathroom(character_id)


@add_premise(constant_promise.Premise.PENIS_IN_T_ANYPART)
def handle_penis_in_t_anypart(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_任意存在位置
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position != -1:
        return 1
    return 0

@add_premise(constant_promise.Premise.PENIS_IN_T_HAIR)
def handle_penis_in_t_hair(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_发交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_FACE)
def handle_penis_in_t_face(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_阴茎蹭脸中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_MOUSE)
def handle_penis_in_t_mouse(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_口交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_NOT_IN_T_MOUSE)
def handle_penis_not_in_t_mouse(character_id: int) -> int:
    """
    当前阴茎位置不为交互对象_口交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_penis_in_t_mouse(character_id)


@add_premise(constant_promise.Premise.PENIS_IN_T_BREAST)
def handle_penis_in_t_breast(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_乳交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_AXILLA)
def handle_penis_in_t_axilla(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_腋交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_HAND)
def handle_penis_in_t_hand(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_手交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_VAGINA)
def handle_penis_in_t_vagina(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_V插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 6:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_WOMB)
def handle_penis_in_t_womb(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_W插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_ANAL)
def handle_penis_in_t_anal(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_A插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 8:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_NOT_IN_T_ANAL)
def handle_penis_not_in_t_anal(character_id: int) -> int:
    """
    当前阴茎位置不为交互对象_A插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_penis_in_t_anal(character_id)


@add_premise(constant_promise.Premise.PENIS_IN_T_URETHRAL)
def handle_penis_in_t_nrethral(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_U插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 9:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_NOT_IN_T_URETHRAL)
def handle_penis_not_in_t_nrethral(character_id: int) -> int:
    """
    当前阴茎位置不为交互对象_U插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_penis_in_t_nrethral(character_id)


@add_premise(constant_promise.Premise.PENIS_IN_T_LEG)
def handle_penis_in_t_leg(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_腿交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_FOOT)
def handle_penis_in_t_foot(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_足交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 11:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_TAIL)
def handle_penis_in_t_tail(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_尾交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 12:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_HORN)
def handle_penis_in_t_horn(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_阴茎蹭角中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 13:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_EARS)
def handle_penis_in_t_ears(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_阴茎蹭耳朵中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.insert_position == 14:
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_MOUSE_OR_BREAST)
def handle_penis_in_t_mouse_or_breast(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_口交中或乳交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_penis_in_t_mouse(character_id) or handle_penis_in_t_breast(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_MOUSE_OR_HAND)
def handle_penis_in_t_mouse_or_hand(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_口交中或手交中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_penis_in_t_mouse(character_id) or handle_penis_in_t_hand(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_IN_T_VAGINA_OR_WOMB)
def handle_penis_in_t_vagina_or_womb(character_id: int) -> int:
    """
    当前阴茎位置为交互对象_V插入中或W插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_penis_in_t_vagina(character_id) or handle_penis_in_t_womb(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PENIS_NOT_IN_T_VAGINA_OR_WOMB)
def handle_penis_not_in_t_vagina_or_womb(character_id: int) -> int:
    """
    当前阴茎位置不为交互对象_V插入中且不为W插入中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_penis_in_t_vagina_or_womb(character_id)


@add_premise(constant_promise.Premise.DR_POSITION_NULL)
def handle_dr_position_null(character_id: int) -> int:
    """
    博士体位为无
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == -1


@add_premise(constant_promise.Premise.DR_HAVE_SEX_POSITION)
def handle_dr_have_sex_position(character_id: int) -> int:
    """
    博士有任意体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_dr_position_null(character_id)


@add_premise(constant_promise.Premise.DR_POSITION_NORMAL)
def handle_dr_position_normal(character_id: int) -> int:
    """
    博士体位为正常体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 1


@add_premise(constant_promise.Premise.DR_POSITION_BACK)
def handle_dr_position_back(character_id: int) -> int:
    """
    博士体位为后背体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 2


@add_premise(constant_promise.Premise.DR_POSITION_FACE_RIDE)
def handle_dr_position_face_ride(character_id: int) -> int:
    """
    博士体位为对面骑乘体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 3


@add_premise(constant_promise.Premise.DR_POSITION_BACK_RIDE)
def handle_dr_position_back_ride(character_id: int) -> int:
    """
    博士体位为背面骑乘体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 4


@add_premise(constant_promise.Premise.DR_POSITION_FACE_SEAT)
def handle_dr_position_face_seat(character_id: int) -> int:
    """
    博士体位为对面座体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 5


@add_premise(constant_promise.Premise.DR_POSITION_BACK_SEAT)
def handle_dr_position_back_seat(character_id: int) -> int:
    """
    博士体位为背面座体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 6


@add_premise(constant_promise.Premise.DR_POSITION_FACE_STAND)
def handle_dr_position_face_stand(character_id: int) -> int:
    """
    博士体位为对面立体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 7


@add_premise(constant_promise.Premise.DR_POSITION_BACK_STAND)
def handle_dr_position_back_stand(character_id: int) -> int:
    """
    博士体位为背面立体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 8


@add_premise(constant_promise.Premise.DR_POSITION_FACE_HUG)
def handle_dr_position_face_hug(character_id: int) -> int:
    """
    博士体位为对面抱体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 9


@add_premise(constant_promise.Premise.DR_POSITION_BACK_HUG)
def handle_dr_position_back_hug(character_id: int) -> int:
    """
    博士体位为背面抱体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 10


@add_premise(constant_promise.Premise.DR_POSITION_FACE_LIE)
def handle_dr_position_face_lie(character_id: int) -> int:
    """
    博士体位为对面卧体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 11


@add_premise(constant_promise.Premise.DR_POSITION_BACK_LIE)
def handle_dr_position_back_lie(character_id: int) -> int:
    """
    博士体位为背面卧体位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_sex_position == 12


@add_premise(constant_promise.Premise.DR_WOMB_POSITION_NULL)
def handle_dr_womb_position_null(character_id: int) -> int:
    """
    博士子宫性交位置为无
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_womb_sex_position == 0


@add_premise(constant_promise.Premise.DR_HAVE_WOMB_POSITION)
def handle_dr_have_womb_position(character_id: int) -> int:
    """
    博士有任意子宫性交位置
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_dr_womb_position_null(character_id)


@add_premise(constant_promise.Premise.DR_WOMB_POSITION_INSERT)
def handle_dr_womb_position_insert(character_id: int) -> int:
    """
    博士子宫性交位置为子宫口插入
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_womb_sex_position == 1


@add_premise(constant_promise.Premise.DR_WOMB_POSITION_SEX)
def handle_dr_womb_position_sex(character_id: int) -> int:
    """
    博士子宫性交位置为子宫奸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    return character_data.h_state.current_womb_sex_position == 2


@add_premise(constant_promise.Premise.SHOOT_IN_T_BODY)
def handle_shoot_in_t_body(character_id: int) -> int:
    """
    在交互对象的身体上射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body != -1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_HAIR)
def handle_shoot_in_t_hair(character_id: int) -> int:
    """
    在交互对象的头发射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_FACE)
def handle_shoot_in_t_face(character_id: int) -> int:
    """
    在交互对象的脸部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_MOUSE)
def handle_shoot_in_t_mouse(character_id: int) -> int:
    """
    在交互对象的口腔射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_BREAST)
def handle_shoot_in_t_breast(character_id: int) -> int:
    """
    在交互对象的胸部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_AXILLA)
def handle_shoot_in_t_axilla(character_id: int) -> int:
    """
    在交互对象的腋部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_HAND)
def handle_shoot_in_t_hand(character_id: int) -> int:
    """
    在交互对象的手部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_VAGINA)
def handle_shoot_in_t_vagina(character_id: int) -> int:
    """
    在交互对象的小穴射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 6:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_WOMB)
def handle_shoot_in_t_womb(character_id: int) -> int:
    """
    在交互对象的子宫射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_ANAL)
def handle_shoot_in_t_anal(character_id: int) -> int:
    """
    在交互对象的后穴射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 8:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_URETHRAL)
def handle_shoot_in_t_nrethral(character_id: int) -> int:
    """
    在交互对象的尿道射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 9:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_LEG)
def handle_shoot_in_t_leg(character_id: int) -> int:
    """
    在交互对象的腿部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_FOOT)
def handle_shoot_in_t_foot(character_id: int) -> int:
    """
    在交互对象的脚部射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 11:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_TAIL)
def handle_shoot_in_t_tail(character_id: int) -> int:
    """
    在交互对象的尾巴射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 12:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_HORN)
def handle_shoot_in_t_horn(character_id: int) -> int:
    """
    在交互对象的兽角射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 13:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_EARS)
def handle_shoot_in_t_ears(character_id: int) -> int:
    """
    在交互对象的兽耳射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_body == 14:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOOT_IN_T_CLOTH)
def handle_shoot_in_t_cloth(character_id: int) -> int:
    """
    在交互对象的衣服上射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.shoot_position_cloth != -1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_ORGASM_0)
def handle_t_turn_orgasm_0(character_id: int) -> int:
    """
    交互对象本次H中还没有绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            if target_data.h_state.orgasm_count[state_id][1]:
                return 0
    return 1


@add_premise(constant_promise.Premise.T_TURN_ORGASM_G_1)
def handle_t_turn_orgasm_g_1(character_id: int) -> int:
    """
    交互对象本次H中绝顶次数>1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    count = 0
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            count += target_data.h_state.orgasm_count[state_id][1]
            if count > 1:
                return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_ORGASM_G_5)
def handle_t_turn_orgasm_g_5(character_id: int) -> int:
    """
    交互对象本次H中绝顶次数>5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    count = 0
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            count += target_data.h_state.orgasm_count[state_id][1]
            if count > 5:
                return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_ORGASM_G_10)
def handle_t_turn_orgasm_g_10(character_id: int) -> int:
    """
    交互对象本次H中绝顶次数>10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    count = 0
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            count += target_data.h_state.orgasm_count[state_id][1]
            if count > 10:
                return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_S_ORGASM_G_3)
def handle_t_turn_s_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中S绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[0][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_B_ORGASM_G_3)
def handle_t_turn_b_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中B绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[1][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_C_ORGASM_G_3)
def handle_t_turn_c_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中C绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[2][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TURN_P_ORGASM_G_1)
def handle_turn_p_orgasm_g_1(character_id: int) -> int:
    """
    玩家本次H中射精次数>1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.h_state.orgasm_count[3][1] > 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TURN_P_ORGASM_G_3)
def handle_turn_p_orgasm_g_3(character_id: int) -> int:
    """
    玩家本次H中射精次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[0]
    if character_data.h_state.orgasm_count[3][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_V_ORGASM_G_3)
def handle_t_turn_v_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中V绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[4][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_A_ORGASM_G_3)
def handle_t_turn_a_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中A绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[5][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_U_ORGASM_G_3)
def handle_t_turn_u_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中U绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[6][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_W_ORGASM_G_3)
def handle_t_turn_w_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中W绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[7][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TURN_M_ORGASM_G_3)
def handle_t_turn_m_orgasm_g_3(character_id: int) -> int:
    """
    交互对象本次H中M绝顶次数>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.orgasm_count[8][1] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_LE_2)
def handle_pl_semen_le_2(character_id: int) -> int:
    """
    玩家当前精液量小于等于2ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point <= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_G_2)
def handle_pl_semen_g_2(character_id: int) -> int:
    """
    玩家当前精液量大于2ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point > 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_LE_50)
def handle_pl_semen_le_50(character_id: int) -> int:
    """
    玩家当前精液量小于等于50ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point <= 50:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_GE_50)
def handle_pl_semen_ge_50(character_id: int) -> int:
    """
    玩家当前精液量大于等于50ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point >= 50:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_L_100)
def handle_pl_semen_l_100(character_id: int) -> int:
    """
    玩家当前精液量小于100ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point < 100:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_GE_100)
def handle_pl_semen_ge_100(character_id: int) -> int:
    """
    玩家当前精液量大于等于100ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.semen_point + pl_character_data.tem_extra_semen_point >= 100:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_SEMEN_TMP_GE_MAX)
def handle_pl_semen_tmp_ge_max(character_id: int) -> int:
    """
    玩家当前临时精液量大于等于最大精液量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.tem_extra_semen_point >= pl_character_data.semen_point_max:
        return 1
    return 0

@add_premise(constant_promise.Premise.PL_JUST_SHOOT)
def handle_pl_just_shoot(character_id: int) -> int:
    """
    玩家前指令射精了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.h_state.just_shoot:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_NOT_JUST_SHOOT)
def handle_pl_not_just_shoot(character_id: int) -> int:
    """
    玩家前指令未射精
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_pl_just_shoot(0):
        return 0
    return 1


@add_premise(constant_promise.Premise.PL_EJA_POINT_LOW)
def handle_pl_eja_point_low(character_id: int) -> int:
    """
    玩家当前射精欲低
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.eja_point <= 300:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_EJA_POINT_MIDDLE)
def handle_pl_eja_point_middle(character_id: int) -> int:
    """
    玩家当前射精欲中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.eja_point <= 600:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_EJA_POINT_HIGH)
def handle_pl_eja_point_high(character_id: int) -> int:
    """
    玩家当前射精欲高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.eja_point <= 900:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_EJA_POINT_EXTREME)
def handle_pl_eja_point_extreme(character_id: int) -> int:
    """
    玩家当前射精欲极
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.eja_point > 900:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_EJA_POINT_LOW_OR_MIDDLE)
def handle_pl_eja_point_low_or_middle(character_id: int) -> int:
    """
    玩家当前射精欲低或中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_pl_eja_point_low(character_id) or handle_pl_eja_point_middle(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_EJA_POINT_HIGH_OR_EXTREME)
def handle_pl_eja_point_high_or_extreme(character_id: int) -> int:
    """
    玩家当前射精欲高或极
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_pl_eja_point_high(character_id) or handle_pl_eja_point_extreme(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_ORGASM_EDGE)
def handle_self_orgasm_edge(character_id: int) -> int:
    """
    自己正在被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.orgasm_edge == 1


@add_premise(constant_promise.Premise.SELF_NOT_ORGASM_EDGE)
def handle_self_not_orgasm_edge(character_id: int) -> int:
    """
    自己没有被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.orgasm_edge == 0


@add_premise(constant_promise.Premise.SELF_ORGASM_EDGE_RELAESE)
def handle_self_orgasm_edge_relase(character_id: int) -> int:
    """
    自己被绝顶寸止解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.orgasm_edge == 2


@add_premise(constant_promise.Premise.TARGET_ORGASM_EDGE)
def handle_target_orgasm_edge(character_id: int) -> int:
    """
    交互对象正在被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_orgasm_edge(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_ORGASM_EDGE)
def handle_target_not_orgasm_edge(character_id: int) -> int:
    """
    交互对象没有被绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_not_orgasm_edge(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_ORGASM_EDGE_RELAESE)
def handle_target_orgasm_edge_relase(character_id: int) -> int:
    """
    交互对象被绝顶寸止解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_orgasm_edge_relase(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_TIME_STOP_ORGASM_RELAESE)
def handle_self_time_stop_orgasm_relase(character_id: int) -> int:
    """
    自己被时停解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.time_stop_release


@add_premise(constant_promise.Premise.TARGET_TIME_STOP_ORGASM_RELAESE)
def handle_target_time_stop_orgasm_relase(character_id: int) -> int:
    """
    交互对象被时停解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_time_stop_orgasm_relase(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_ORGASM_EDGE_RELAESE_OR_TIME_STOP_ORGASM_RELAESE)
def handle_self_orgasm_edge_relase_or_time_stop_orgasm_relase(character_id: int) -> int:
    """
    自己被绝顶寸止解放或时停解放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_orgasm_edge_relase(character_id) or handle_self_time_stop_orgasm_relase(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_S)
def handle_self_plural_orgasm_have_S(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含S绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 0 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_S)
def handle_target_plural_orgasm_have_S(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含S绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_S(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_B)
def handle_self_plural_orgasm_have_B(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含B绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 1 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_B)
def handle_target_plural_orgasm_have_B(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含B绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_B(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_C)
def handle_self_plural_orgasm_have_C(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含C绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 2 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_C)
def handle_target_plural_orgasm_have_C(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含C绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_C(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_V)
def handle_self_plural_orgasm_have_V(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含V绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 4 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_V)
def handle_target_plural_orgasm_have_V(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含V绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_V(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_A)
def handle_self_plural_orgasm_have_A(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含A绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 5 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_A)
def handle_target_plural_orgasm_have_A(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含A绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_A(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_U)
def handle_self_plural_orgasm_have_U(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含U绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 6 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_U)
def handle_target_plural_orgasm_have_U(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含U绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_U(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_PLURAL_ORGASM_HAVE_W)
def handle_self_plural_orgasm_have_W(character_id: int) -> int:
    """
    自己的本次多重绝顶中包含W绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return 7 in character_data.h_state.plural_orgasm_set


@add_premise(constant_promise.Premise.TARGET_PLURAL_ORGASM_HAVE_W)
def handle_target_plural_orgasm_have_W(character_id: int) -> int:
    """
    交互对象的本次多重绝顶中包含W绝顶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_plural_orgasm_have_W(character_data.target_character_id)


@add_premise(constant_promise.Premise.NPC_ACTIVE_H)
def handle_npc_active_h(character_id: int) -> int:
    """
    自己正在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.npc_active_h:
        return 1
    return 0


@add_premise(constant_promise.Premise.NPC_NOT_ACTIVE_H)
def handle_npc_not_active_h(character_id: int) -> int:
    """
    自己没有在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.npc_active_h:
        return 0
    return 1


@add_premise(constant_promise.Premise.T_NPC_ACTIVE_H)
def handle_t_npc_active_h(character_id: int) -> int:
    """
    交互对象正在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.npc_active_h:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NPC_NOT_ACTIVE_H)
def handle_t_npc_not_active_h(character_id: int) -> int:
    """
    交互对象没有在主动H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.h_state.npc_active_h:
        return 0
    return 1


@add_premise(constant_promise.Premise.GROUP_SEX_FAIL_AND_SELF_AGREE)
def handle_group_sex_fail_and_self_agree(character_id: int) -> int:
    """
    群交邀请失败了，但自己不是拒绝者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if character_id in pl_character_data.action_info.ask_group_sex_refuse_chara_id_list:
        return 0
    return 1


@add_premise(constant_promise.Premise.GROUP_SEX_FAIL_AND_SELF_REFUSE)
def handle_group_sex_fail_and_self_refuse(character_id: int) -> int:
    """
    群交邀请失败了，自己是拒绝者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_group_sex_fail_and_self_agree(character_id)


@add_premise(constant_promise.Premise.HAVE_ONE_GRUOP_SEX_TEMPLE)
def handle_have_one_group_sex_temple(character_id: int) -> int:
    """
    当前存在一个群交模板
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    group_sex_temple_flag = False
    # 获取群交模板数据
    pl_character_data = cache.character_data[0]
    pl_group_sex_A_data = pl_character_data.h_state.group_sex_body_template_dict["A"]
    # 遍历模板的对单部分
    for body_part in pl_group_sex_A_data[0]:
        # 如果某个部位的指令id不为-1，则返回为True
        if pl_group_sex_A_data[0][body_part][1] != -1:
            group_sex_temple_flag = True
            break
    # 如果flag为false，则继续检测对多部分
    if not group_sex_temple_flag:
        if pl_group_sex_A_data[1][1] != -1:
            group_sex_temple_flag = True
    # 返回flag
    return group_sex_temple_flag


@add_premise(constant_promise.Premise.HAVE_OVER_ONE_GRUOP_SEX_TEMPLE)
def handle_have_over_one_group_sex_temple(character_id: int) -> int:
    """
    当前存在多个群交模板
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    group_sex_temple_flag = False
    # 获取群交模板数据
    pl_character_data = cache.character_data[0]
    pl_group_sex_B_data = pl_character_data.h_state.group_sex_body_template_dict["B"]
    # 遍历模板的对单部分
    for body_part in pl_group_sex_B_data[0]:
        # 如果某个部位的指令id不为-1，则返回为True
        if pl_group_sex_B_data[0][body_part][1] != -1:
            group_sex_temple_flag = True
            break
    # 如果flag为false，则继续检测对多部分
    if not group_sex_temple_flag:
        if pl_group_sex_B_data[1][1] != -1:
            group_sex_temple_flag = True
    # 返回
    if handle_have_one_group_sex_temple(character_id) and group_sex_temple_flag:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.ALL_GROUP_SEX_TEMPLE_RUN_ON)
def handle_all_group_sex_temple_run_on(character_id: int) -> int:
    """
    开启了运行全群交模板
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    return pl_character_data.h_state.all_group_sex_temple_run


@add_premise(constant_promise.Premise.ALL_GROUP_SEX_TEMPLE_RUN_OFF)
def handle_all_group_sex_temple_run_off(character_id: int) -> int:
    """
    关闭了运行全群交模板
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_all_group_sex_temple_run_on(character_id)


@add_premise(constant_promise.Premise.NPC_AI_TYPE_0_IN_GROUP_SEX)
def handle_npc_ai_type_0_in_group_sex(character_id: int) -> int:
    """
    未在模板中的NPC在群交中无行动
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    return pl_character_data.h_state.npc_ai_type_in_group_sex == 0


@add_premise(constant_promise.Premise.NPC_AI_TYPE_1_IN_GROUP_SEX)
def handle_npc_ai_type_1_in_group_sex(character_id: int) -> int:
    """
    未在模板中的NPC在群交中仅自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    return pl_character_data.h_state.npc_ai_type_in_group_sex == 1


@add_premise(constant_promise.Premise.NPC_AI_TYPE_2_IN_GROUP_SEX)
def handle_npc_ai_type_2_in_group_sex(character_id: int) -> int:
    """
    未在模板中的NPC在群交中优先自动补位、无位则自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    return pl_character_data.h_state.npc_ai_type_in_group_sex == 2


@add_premise(constant_promise.Premise.NPC_AI_TYPE_3_IN_GROUP_SEX)
def handle_npc_ai_type_3_in_group_sex(character_id: int) -> int:
    """
    未在模板中的NPC在群交中随机抢占替换当前位置，无位则自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    return pl_character_data.h_state.npc_ai_type_in_group_sex == 3


@add_premise(constant_promise.Premise.SLEF_NOW_GO_TO_JOIN_GROUP_SEX)
def handle_self_now_go_to_join_group_sex(character_id: int) -> int:
    """
    自己正在前往加入群交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.sp_flag.go_to_join_group_sex


@add_premise(constant_promise.Premise.SLEF_NOT_GO_TO_JOIN_GROUP_SEX)
def handle_self_not_go_to_join_group_sex(character_id: int) -> int:
    """
    自己没有前往加入群交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_now_go_to_join_group_sex(character_id)


@add_premise(constant_promise.Premise.SEX_ASSISTANT_ON)
def handle_sex_assistant_on(character_id: int) -> int:
    """
    开启了性爱助手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.confinement_training_setting[12] > 0


@add_premise(constant_promise.Premise.SEX_ASSISTANT_OFF)
def handle_sex_assistant_off(character_id: int) -> int:
    """
    没有开启性爱助手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_sex_assistant_on(character_id)


@add_premise(constant_promise.Premise.SEX_ASSISTANT_1)
def handle_sex_assistant_1(character_id: int) -> int:
    """
    性爱助手目标为玩家同部位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.confinement_training_setting[12] == 1


@add_premise(constant_promise.Premise.SEX_ASSISTANT_2)
def handle_sex_assistant_2(character_id: int) -> int:
    """
    性爱助手目标为避开玩家部位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.confinement_training_setting[12] == 2


@add_premise(constant_promise.Premise.SEX_ASSISTANT_3)
def handle_sex_assistant_3(character_id: int) -> int:
    """
    性爱助手目标为指定指令列表
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.confinement_training_setting[12] == 3


@add_premise(constant_promise.Premise.SELF_SLEEP_H_AWAKE_BUT_PRETEND_SLEEP)
def handle_self_sleep_h_awake_but_pretend_sleep(character_id: int) -> int:
    """
    自己在睡奸中醒来但是装睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.pretend_sleep


@add_premise(constant_promise.Premise.SELF_NOT_SLEEP_H_AWAKE_BUT_PRETEND_SLEEP)
def handle_self_not_sleep_h_awake_but_pretend_sleep(character_id: int) -> int:
    """
    自己没有在睡奸中醒来但是装睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_sleep_h_awake_but_pretend_sleep(character_id)


@add_premise(constant_promise.Premise.TARGET_SLEEP_H_AWAKE_BUT_PRETEND_SLEEP)
def handle_target_sleep_h_awake_but_pretend_sleep(character_id: int) -> int:
    """
    交互对象在睡奸中醒来但是装睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_sleep_h_awake_but_pretend_sleep(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_SLEEP_H_AWAKE_BUT_PRETEND_SLEEP)
def handle_target_not_sleep_h_awake_but_pretend_sleep(character_id: int) -> int:
    """
    交互对象没有在睡奸中醒来但是装睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_target_sleep_h_awake_but_pretend_sleep(character_id)



@add_premise(constant_promise.Premise.HAVE_FOOD)
def handle_have_food(character_id: int) -> int:
    """
    校验角色是否拥有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 0
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id]:
            food_index += 1
    return food_index


@add_premise(constant_promise.Premise.NOT_HAVE_FOOD)
def handle_not_have_food(character_id: int) -> int:
    """
    校验角色是否没有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 1
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id]:
            return 0
    return food_index


@add_premise(constant_promise.Premise.HAVE_CAMERA)
def handle_have_camera(character_id: int) -> int:
    """
    校验角色是否已持有相机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[50] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_VIDEO_RECORDER)
def handle_have_video_recorder(character_id: int) -> int:
    """
    校验角色是否已持有录像机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[51] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_INSTRUMENT)
def handle_have_instrument(character_id: int) -> int:
    """
    校验角色是否已持有乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[52] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_NIPPLE_CLAMP)
def handle_have_nipple_clamp(character_id: int) -> int:
    """
    校验角色是否已持有乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[122] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_NIPPLE_CLAMP)
def handle_self_now_nipple_clamp(character_id: int) -> int:
    """
    校验自己是否正在乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[0][1]


@add_premise(constant_promise.Premise.TARGET_NOW_NIPPLE_CLAMP)
def handle_target_now_nipple_clamp(character_id: int) -> int:
    """
    校验交互对象是否正在乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_nipple_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_NIPPLE_CLAMP)
def handle_target_not_nipple_clamp(character_id: int) -> int:
    """
    校验交互对象是否没有在乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_target_now_nipple_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.HAVE_LOVE_EGG)
def handle_have_love_egg(character_id: int) -> int:
    """
    校验角色是否已持有跳蛋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[121] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CLIT_CLAMP)
def handle_have_clit_clamp(character_id: int) -> int:
    """
    校验角色是否已持有阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[123] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_CLIT_CLAMP)
def handle_self_now_clit_clamp(character_id: int) -> int:
    """
    校验自己是否正在阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[1][1]


@add_premise(constant_promise.Premise.TARGET_NOW_CLIT_CLAMP)
def handle_target_now_clit_clamp(character_id: int) -> int:
    """
    校验交互对象是否正在阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_clit_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_CLIT_CLAMP)
def handle_target_not_clit_clamp(character_id: int) -> int:
    """
    校验交互对象是否没有在阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_clit_clamp(character_data.target_character_id)


@add_premise(constant_promise.Premise.HAVE_ELECTRIC_MESSAGE_STICK)
def handle_have_electric_message_stick(character_id: int) -> int:
    """
    校验角色是否已持有电动按摩棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[124] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_VIBRATOR)
def handle_have_vibrator(character_id: int) -> int:
    """
    校验角色是否已持有震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[125] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_VIBRATOR_INSERTION)
def handle_self_now_vibrator_insertion(character_id: int) -> int:
    """
    校验自己V正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[2][1]


@add_premise(constant_promise.Premise.TARGET_NOW_VIBRATOR_INSERTION)
def handle_target_now_vibrator_insertion(character_id: int) -> int:
    """
    校验交互对象V正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_vibrator_insertion(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION)
def handle_target_not_vibrator_insertion(character_id: int) -> int:
    """
    校验交互对象V没有在插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_vibrator_insertion(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_NOW_VIBRATOR_INSERTION_ANAL)
def handle_self_now_vibrator_insertion_anal(character_id: int) -> int:
    """
    校验自己A正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[3][1]


@add_premise(constant_promise.Premise.TARGET_NOW_VIBRATOR_INSERTION_ANAL)
def handle_target_now_vibrator_insertion_anal(character_id: int) -> int:
    """
    校验交互对象A正插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_vibrator_insertion_anal(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL)
def handle_target_not_vibrator_insertion_anal(character_id: int) -> int:
    """
    校验交互对象A没有在插入震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_vibrator_insertion_anal(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_A_EMPTY)
def handle_self_a_empty(character_id: int) -> int:
    """
    校验自己A无任何道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_enema,
    )
    # 震动棒
    if handle_self_now_vibrator_insertion_anal(character_id):
        return 0
    # 拉珠
    if handle_self_now_anal_beads(character_id):
        return 0
    # 灌肠中
    if handle_enema(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_A_EMPTY)
def handle_target_a_empty(character_id: int) -> int:
    """
    交互对象A无任何道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_a_empty(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_MILKING_MACHINE)
def handle_target_now_milking_machine(character_id: int) -> int:
    """
    交互对象正在搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[4][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_MILKING_MACHINE)
def handle_target_not_milking_machine(character_id: int) -> int:
    """
    交互对象没有在搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[4][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_NOW_URINE_COLLECTOR)
def handle_target_now_urine_collector(character_id: int) -> int:
    """
    交互对象正在采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[5][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_URINE_COLLECTOR)
def handle_target_not_urine_collector(character_id: int) -> int:
    """
    交互对象没有在采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[5][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_NOW_PATCH)
def handle_self_now_patch(character_id: int) -> int:
    """
    自己戴着眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[6][1]


@add_premise(constant_promise.Premise.SELF_NOT_PATCH)
def handle_self_not_patch(character_id: int) -> int:
    """
    自己没有戴着眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_now_patch(character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_PATCH)
def handle_target_now_patch(character_id: int) -> int:
    """
    交互对象戴着眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_patch(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_PATCH)
def handle_target_not_patch(character_id: int) -> int:
    """
    交互对象没有戴着眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_patch(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_NOW_GAG)
def handle_self_now_gag(character_id: int) -> int:
    """
    自己戴着口球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.body_item[14][1]


@add_premise(constant_promise.Premise.SELF_NOT_GAG)
def handle_self_not_gag(character_id: int) -> int:
    """
    自己没有戴着口球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_now_gag(character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_GAG)
def handle_target_now_gag(character_id: int) -> int:
    """
    交互对象戴着口球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_gag(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_GAG)
def handle_target_not_gag(character_id: int) -> int:
    """
    交互对象没有戴着口球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_now_gag(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_SEELP_PIILS)
def handle_self_sleep_pills(character_id: int) -> int:
    """
    自己已服用安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[9][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_SEELP_PIILS)
def handle_self_not_sleep_pills(character_id: int) -> int:
    """
    自己没有服用安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_sleep_pills(character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_BIRTH_CONTROL_PILLS_BEFORE)
def handle_target_now_birth_control_pills_before(character_id: int) -> int:
    """
    交互对象已服用事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[11][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_BIRTH_CONTROL_PILLS_BEFORE)
def handle_target_not_birth_control_pills_before(character_id: int) -> int:
    """
    交互对象没有服用事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_target_now_birth_control_pills_before(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_NOW_BIRTH_CONTROL_PILLS_AFTER)
def handle_target_now_birth_control_pills_after(character_id: int) -> int:
    """
    交互对象已服用事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.h_state.body_item[12][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_BIRTH_CONTROL_PILLS_AFTER)
def handle_target_not_birth_control_pills_after(character_id: int) -> int:
    """
    交互对象没有服用事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_target_now_birth_control_pills_after(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_SEMEN_ENERGY_AGENT)
def handle_self_semen_energy_agent(character_id: int) -> int:
    """
    自己已服用精力剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.used_semen_energy_agent


@add_premise(constant_promise.Premise.SELF_NOT_SEMEN_ENERGY_AGENT)
def handle_self_not_semen_energy_agent(character_id: int) -> int:
    """
    自己没有服用精力剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_semen_energy_agent(character_id)


@add_premise(constant_promise.Premise.TARGET_SEMEN_ENERGY_AGENT)
def handle_target_semen_energy_agent(character_id: int) -> int:
    """
    交互对象已服用精力剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_semen_energy_agent(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_SEMEN_ENERGY_AGENT)
def handle_target_not_semen_energy_agent(character_id: int) -> int:
    """
    交互对象没有服用精力剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_semen_energy_agent(character_data.target_character_id)


@add_premise(constant_promise.Premise.NOW_CONDOM)
def handle_now_condom(character_id: int) -> int:
    """
    自己正戴着避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[13][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOW_NOT_CONDOM)
def handle_now_not_condom(character_id: int) -> int:
    """
    自己没有戴着避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[13][1]:
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_USE_CONDOM_IN_H)
def handle_not_use_condom_in_h(character_id: int) -> int:
    """
    本次H中没有已用掉的避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_1)
def handle_use_condom_in_h_ge_1(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_3)
def handle_use_condom_in_h_ge_3(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_5)
def handle_use_condom_in_h_ge_5(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.USE_CONDOM_IN_H_GE_10)
def handle_use_condom_in_h_ge_10(character_id: int) -> int:
    """
    本次H中已用掉的避孕套数量大于等于10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.condom_count[0] >= 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_BONDAGE)
def handle_self_now_bondage(character_id: int) -> int:
    """
    自己正在被绳子捆绑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.h_state.bondage > 0


@add_premise(constant_promise.Premise.SELF_NOT_BONDAGE)
def handle_self_not_bondage(character_id: int) -> int:
    """
    自己没有被绳子捆绑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_now_bondage(character_id)


@add_premise(constant_promise.Premise.TARGET_NOW_BONDAGE)
def handle_target_now_bondage(character_id: int) -> int:
    """
    交互对象正在被绳子捆绑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_now_bondage(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_BONDAGE)
def handle_target_not_bondage(character_id: int) -> int:
    """
    交互对象没有被绳子捆绑
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_target_now_bondage(character_id)


@add_premise(constant_promise.Premise.HAVE_MILKING_MACHINE)
def handle_have_milking_machine(character_id: int) -> int:
    """
    校验角色是否已持有搾乳机
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[133] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_URINE_COLLECTOR)
def handle_have_urine_collector(character_id: int) -> int:
    """
    校验角色是否已持有采尿器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[134] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BONDAGE)
def handle_have_bondage(character_id: int) -> int:
    """
    校验角色是否已持有绳子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[131] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_PATCH)
def handle_have_patch(character_id: int) -> int:
    """
    校验角色是否已持有眼罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[132] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_GAG)
def handle_have_gag(character_id: int) -> int:
    """
    校验角色是否已持有口球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[140] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BIG_VIBRATOR)
def handle_have_big_vibrator(character_id: int) -> int:
    """
    校验角色是否已持有加粗震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[126] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_HUGE_VIBRATOR)
def handle_have_huge_vibrator(character_id: int) -> int:
    """
    校验角色是否已持有巨型震动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[127] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CLYSTER_TOOLS)
def handle_have_clyster_tools(character_id: int) -> int:
    """
    校验角色是否已持有灌肠套装
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[128] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_ANAL_BEADS)
def handle_have_anal_beads(character_id: int) -> int:
    """
    校验角色是否已持有肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[129] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOW_ANAL_BEADS)
def handle_self_now_anal_beads(character_id: int) -> int:
    """
    校验自己是否正在肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.h_state.body_item[7][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOW_ANAL_BEADS)
def handle_target_now_anal_beads(character_id: int) -> int:
    """
    校验交互对象是否正在肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_now_anal_beads(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_ANAL_BEADS)
def handle_target_not_anal_beads(character_id: int) -> int:
    """
    校验交互对象是否没有在肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_now_anal_beads(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.HAVE_ANAL_PLUG)
def handle_have_anal_plug(character_id: int) -> int:
    """
    校验角色是否已持有肛塞
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    # if character_data.item[130] > 0:
    # return 1
    return 0
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1


@add_premise(constant_promise.Premise.HAVE_WHIP)
def handle_have_whip(character_id: int) -> int:
    """
    校验角色是否已持有鞭子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[135] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_NEEDLE)
def handle_have_needle(character_id: int) -> int:
    """
    校验角色是否已持有针
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[137] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CONDOM)
def handle_have_condom(character_id: int) -> int:
    """
    校验角色是否已持有避孕套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[120] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_SAFE_CANDLES)
def handle_have_safe_candles(character_id: int) -> int:
    """
    校验角色是否已持有低温蜡烛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[136] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_COTTON_STICK)
def handle_have_cotton_stick(character_id: int) -> int:
    """
    校验角色是否已持有无菌棉签
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[139] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BIRTH_CONTROL_PILLS_BEFORE)
def handle_have_birth_control_pills_before(character_id: int) -> int:
    """
    校验角色是否已持有事前避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[101] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BIRTH_CONTROL_PILLS_AFTER)
def handle_have_birth_control_pills_after(character_id: int) -> int:
    """
    校验角色是否已持有事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[102] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BODY_LUBRICANT)
def handle_have_body_lubricant(character_id: int) -> int:
    """
    校验角色是否已持有润滑液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[100] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_PHILTER)
def handle_have_philter(character_id: int) -> int:
    """
    校验角色是否已持有媚药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[103] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_ENEMAS)
def handle_have_enemas(character_id: int) -> int:
    """
    校验角色是否已持有灌肠液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[104] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_DIURETICS_ONCE)
def handle_have_diuretics_once(character_id: int) -> int:
    """
    校验角色是否已持有一次性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[105] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_DIURETICS_PERSISTENT)
def handle_have_diuretics_persistent(character_id: int) -> int:
    """
    校验角色是否已持有持续性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[106] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_SLEEPING_PILLS)
def handle_have_sleeping_pills(character_id: int) -> int:
    """
    校验角色是否已持有安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[107] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_CLOMID)
def handle_have_clomid(character_id: int) -> int:
    """
    校验角色是否已持有排卵促进药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[108] > 0:
        return 1
    # 在爱情旅馆的顶级套房中则临时持有
    if handle_h_in_love_hotel(character_id) and handle_love_hotel_room_v3(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_RING)
def handle_have_ring(character_id: int) -> int:
    """
    已持有戒指
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[201] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_COLLAR)
def handle_have_collar(character_id: int) -> int:
    """
    已持有项圈
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[202] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_BAG)
def handle_have_bag(character_id: int) -> int:
    """
    已持有干员携袋
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[151] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_PENIS_MOLD)
def handle_have_penis_mold(character_id: int) -> int:
    """
    自己已持有阴茎倒模
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.item[175] > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HAVE_PENIS_MOLD)
def handle_target_have_penis_mold(character_id: int) -> int:
    """
    交互对象已持有阴茎倒模
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_have_penis_mold(character_data.target_character_id)

