from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text

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


@add_premise(constant_promise.Premise.LAST_CMD_MAKING_OUT)
def handle_last_cmd_makeing_out(character_id: int) -> int:
    """
    前一指令为身体爱抚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.MAKING_OUT)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_KISS_H)
def handle_last_cmd_kiss_h(character_id: int) -> int:
    """
    前一指令为接吻（H）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.KISS_H)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BREAST_CARESS)
def handle_last_cmd_breast_caress(character_id: int) -> int:
    """
    前一指令为胸爱抚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.BREAST_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_TWIDDLE_NIPPLES)
def handle_last_cmd_twiddle_nipples(character_id: int) -> int:
    """
    前一指令为玩弄乳头
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.TWIDDLE_NIPPLES)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BREAST_SUCKING)
def handle_last_cmd_breast_sucking(character_id: int) -> int:
    """
    前一指令为舔吸乳头
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.BREAST_SUCKING)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_CLIT_CARESS)
def handle_last_cmd_clit_caress(character_id: int) -> int:
    """
    前一指令为阴蒂爱抚
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.CLIT_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_OPEN_LABIA)
def handle_last_cmd_open_labia(character_id: int) -> int:
    """
    前一指令为掰开阴唇观察
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.OPEN_LABIA)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_CUNNILINGUS)
def handle_last_cmd_cunnilingus(character_id: int) -> int:
    """
    前一指令为舔阴
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.CUNNILINGUS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FINGER_INSERTION)
def handle_last_cmd_finger_insertion(character_id: int) -> int:
    """
    前一指令为手指插入(V)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FINGER_INSERTION)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_ANAL_CARESS)
def handle_last_cmd_anal_caress(character_id: int) -> int:
    """
    前一指令为手指插入(A)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.ANAL_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_MAKE_MASTUREBATE)
def handle_last_cmd_make_masturebate(character_id: int) -> int:
    """
    前一指令为让对方自慰（H）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.MAKE_MASTUREBATE)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB)
def handle_last_cmd_blowjob(character_id: int) -> int:
    """
    前一指令为口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input and (last_cmd == str(constant.Instruct.BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HANDJOB)
def handle_last_cmd_handjob(character_id: int) -> int:
    """
    前一指令为手交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HANDJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_PAIZURI)
def handle_last_cmd_paizuri(character_id: int) -> int:
    """
    前一指令为乳交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.PAIZURI)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FOOTJOB)
def handle_last_cmd_footjob(character_id: int) -> int:
    """
    前一指令为足交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FOOTJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HAIRJOB)
def handle_last_cmd_hairjob(character_id: int) -> int:
    """
    前一指令为发交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HAIRJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_AXILLAJOB)
def handle_last_cmd_axillajob(character_id: int) -> int:
    """
    前一指令为腋交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.AXILLAJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_RUB_BUTTOCK)
def handle_last_cmd_rub_buttock(character_id: int) -> int:
    """
    前一指令为素股
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.RUB_BUTTOCK)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_LEGJOB)
def handle_last_cmd_legjob(character_id: int) -> int:
    """
    前一指令为腿交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.LEGJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_TAILJOB)
def handle_last_cmd_tailjob(character_id: int) -> int:
    """
    前一指令为尾交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.TAILJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FACE_RUB)
def handle_last_cmd_face_rub(character_id: int) -> int:
    """
    前一指令为阴茎蹭脸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FACE_RUB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HORN_RUB)
def handle_last_cmd_horn_rub(character_id: int) -> int:
    """
    前一指令为阴茎蹭角
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HORN_RUB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_EARS_RUB)
def handle_last_cmd_ears_rub(character_id: int) -> int:
    """
    前一指令为阴茎蹭耳朵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.EARS_RUB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HAND_BLOWJOB)
def handle_last_cmd_hand_blowjob(character_id: int) -> int:
    """
    前一指令为手交口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.HAND_BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_TITS_BLOWJOB)
def handle_last_cmd_tits_blowjob(character_id: int) -> int:
    """
    前一指令为乳交口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.TITS_BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_DEEP_THROAT)
def handle_last_cmd_deep_throat(character_id: int) -> int:
    """
    前一指令为深喉插入
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.pl_pre_behavior_instruce):
        last_behavior = cache.pl_pre_behavior_instruce[-1]
        if last_behavior == constant.Behavior.DEEP_THROAT:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_FOCUS_BLOWJOB)
def handle_last_cmd_focus_blowjob(character_id: int) -> int:
    """
    前一指令为真空口交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.FOCUS_BLOWJOB)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_NORMAL_SEX)
def handle_last_cmd_normal_sex(character_id: int) -> int:
    """
    前一指令为正常位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.NORMAL_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BACK_SEX)
def handle_last_cmd_back_sex(character_id: int) -> int:
    """
    前一指令为背后位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.BACK_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_RIDING_SEX)
def handle_last_cmd_riding_sex(character_id: int) -> int:
    """
    前一指令为骑乘位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.RIDING_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_FACE_SEAT_SEX)
def handle_last_cmd_face_seat_sex(character_id: int) -> int:
    """
    前一指令为对面座位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.FACE_SEAT_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BACK_SEAT_SEX)
def handle_last_cmd_back_seat_sex(character_id: int) -> int:
    """
    前一指令为背面座位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.BACK_SEAT_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_FACE_STAND_SEX)
def handle_last_cmd_face_stand_sex(character_id: int) -> int:
    """
    前一指令为对面立位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.FACE_STAND_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BACK_STAND_SEX)
def handle_last_cmd_back_stand_sex(character_id: int) -> int:
    """
    前一指令为背面立位
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd == str(constant.Instruct.BACK_STAND_SEX):
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_STIMULATE_G_POINT)
def handle_last_cmd_stimulate_g_point(character_id: int) -> int:
    """
    前一指令为刺激G点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.STIMULATE_G_POINT)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_WOMB_OS_CARESS)
def handle_last_cmd_womb_os_caress(character_id: int) -> int:
    """
    前一指令为玩弄子宫口
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 2]
    if len_input and (last_cmd == str(constant.Instruct.WOMB_OS_CARESS)):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_PENIS_POSITION)
def handle_last_cmd_penis_position(character_id: int) -> int:
    """
    前一指令为阴茎位置相关指令_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.NORMAL_SEX), str(constant.Instruct.BACK_SEX),
        str(constant.Instruct.RIDING_SEX), str(constant.Instruct.BACK_RIDING_SEX),
        str(constant.Instruct.FACE_SEAT_SEX), str(constant.Instruct.BACK_SEAT_SEX),
        str(constant.Instruct.FACE_STAND_SEX), str(constant.Instruct.BACK_STAND_SEX),
        str(constant.Instruct.FACE_HUG_SEX), str(constant.Instruct.BACK_HUG_SEX),
        str(constant.Instruct.FACE_LAY_SEX), str(constant.Instruct.BACK_LAY_SEX),
        str(constant.Instruct.STIMULATE_G_POINT), str(constant.Instruct.WOMB_OS_CARESS),
        str(constant.Instruct.WOMB_INSERTION),
        str(constant.Instruct.NORMAL_ANAL_SEX), str(constant.Instruct.BACK_ANAL_SEX),
        str(constant.Instruct.RIDING_ANAL_SEX), str(constant.Instruct.BACK_RIDING_ANAL_SEX),
        str(constant.Instruct.FACE_SEAT_ANAL_SEX), str(constant.Instruct.BACK_SEAT_ANAL_SEX),
        str(constant.Instruct.FACE_STAND_ANAL_SEX), str(constant.Instruct.BACK_STAND_ANAL_SEX),
        str(constant.Instruct.FACE_HUG_ANAL_SEX), str(constant.Instruct.BACK_HUG_ANAL_SEX),
        str(constant.Instruct.FACE_LAY_ANAL_SEX), str(constant.Instruct.BACK_LAY_ANAL_SEX),
        str(constant.Instruct.STIMULATE_SIGMOID_COLON), str(constant.Instruct.STIMULATE_VAGINA),
        str(constant.Instruct.URETHRAL_SEX),
        str(constant.Instruct.HANDJOB), str(constant.Instruct.HAND_BLOWJOB),
        str(constant.Instruct.BLOWJOB), str(constant.Instruct.PAIZURI),
        str(constant.Instruct.TITS_BLOWJOB), str(constant.Instruct.FOCUS_BLOWJOB),
        str(constant.Instruct.DEEP_THROAT), str(constant.Instruct.SIXTY_NINE),
        str(constant.Instruct.FOOTJOB), str(constant.Instruct.HAIRJOB),
        str(constant.Instruct.AXILLAJOB), str(constant.Instruct.RUB_BUTTOCK),
        str(constant.Instruct.LEGJOB), str(constant.Instruct.TAILJOB),
        str(constant.Instruct.FACE_RUB), str(constant.Instruct.HORN_RUB),
        str(constant.Instruct.EARS_RUB),
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_OR_HANDJOB)
def handle_last_cmd_blowjob_or_handjob(character_id: int) -> int:
    """
    前一指令为口交或手交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.HANDJOB)):
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_OR_PAIZURI)
def handle_last_cmd_blowjob_or_paizuri(character_id: int) -> int:
    """
    前一指令为口交或乳交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.PAIZURI)):
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_OR_CUNNILINGUS)
def handle_last_cmd_blowjob_or_cunnilingus(character_id: int) -> int:
    """
    前一指令为口交或舔阴_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    if len_input:
        if (last_cmd == str(constant.Instruct.BLOWJOB)) or (last_cmd == str(constant.Instruct.CUNNILINGUS)):
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_SEX)
def handle_last_cmd_sex(character_id: int) -> int:
    """
    前一指令为V性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)

    sex = {
        str(constant.Instruct.NORMAL_SEX), str(constant.Instruct.BACK_SEX),
        str(constant.Instruct.RIDING_SEX), str(constant.Instruct.BACK_RIDING_SEX),
        str(constant.Instruct.FACE_SEAT_SEX), str(constant.Instruct.BACK_SEAT_SEX),
        str(constant.Instruct.FACE_STAND_SEX), str(constant.Instruct.BACK_STAND_SEX),
        str(constant.Instruct.FACE_HUG_SEX), str(constant.Instruct.BACK_HUG_SEX),
        str(constant.Instruct.FACE_LAY_SEX), str(constant.Instruct.BACK_LAY_SEX),
        str(constant.Instruct.STIMULATE_G_POINT), str(constant.Instruct.WOMB_OS_CARESS),
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_W_SEX)
def handle_last_cmd_w_sex(character_id: int) -> int:
    """
    前一指令为W性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    sex = {
        str(constant.Instruct.WOMB_INSERTION), str(constant.Instruct.WOMB_SEX)
    }
    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_SEX_OR_W_SEX)
def handle_last_cmd_sex_or_w_sex(character_id: int) -> int:
    """
    前一指令为V性交或W性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_last_cmd_sex(character_id):
        return 1
    elif handle_last_cmd_w_sex(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_A_SEX)
def handle_last_cmd_a_sex(character_id: int) -> int:
    """
    前一指令为A性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    sex = {
        str(constant.Instruct.NORMAL_ANAL_SEX), str(constant.Instruct.BACK_ANAL_SEX),
        str(constant.Instruct.RIDING_ANAL_SEX), str(constant.Instruct.BACK_RIDING_ANAL_SEX),
        str(constant.Instruct.FACE_SEAT_ANAL_SEX), str(constant.Instruct.BACK_SEAT_ANAL_SEX),
        str(constant.Instruct.FACE_STAND_ANAL_SEX), str(constant.Instruct.BACK_STAND_ANAL_SEX),
        str(constant.Instruct.FACE_HUG_ANAL_SEX), str(constant.Instruct.BACK_HUG_ANAL_SEX),
        str(constant.Instruct.FACE_LAY_ANAL_SEX), str(constant.Instruct.BACK_LAY_ANAL_SEX),
        str(constant.Instruct.STIMULATE_SIGMOID_COLON), str(constant.Instruct.STIMULATE_VAGINA)
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_U_SEX)
def handle_last_cmd_u_sex(character_id: int) -> int:
    """
    前一指令为U性交_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    sex = {
        str(constant.Instruct.URETHRAL_SEX)
    }

    for i in range(len_input):
        last_cmd = cache.input_cache[len_input - 1 - i]
        if last_cmd == _("确定"):
            continue
        if last_cmd in sex:
            return 1
        return 0


@add_premise(constant_promise.Premise.LAST_CMD_BREAST_CARESS_TYPE)
def handle_last_cmd_breast_caress_type(character_id: int) -> int:
    """
    前一指令为胸部爱抚类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.BREAST_CARESS), str(constant.Instruct.TWIDDLE_NIPPLES),
        str(constant.Instruct.BREAST_SUCKING)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_HANDJOB_TYPE)
def handle_last_cmd_handjob_type(character_id: int) -> int:
    """
    前一指令为手交类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.HANDJOB), str(constant.Instruct.HAND_BLOWJOB)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_BLOWJOB_TYPE)
def handle_last_cmd_blowjob_type(character_id: int) -> int:
    """
    前一指令为口交类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.BLOWJOB), str(constant.Instruct.HAND_BLOWJOB),
        str(constant.Instruct.TITS_BLOWJOB), str(constant.Instruct.FOCUS_BLOWJOB),
        str(constant.Instruct.DEEP_THROAT), str(constant.Instruct.SIXTY_NINE), str(constant.Instruct.CLEAN_BLOWJOB)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0


@add_premise(constant_promise.Premise.LAST_CMD_PAIZURI_TYPE)
def handle_last_cmd_paizuri_type(character_id: int) -> int:
    """
    前一指令为乳交类_指令触发用
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    len_input = len(cache.input_cache)
    if not len_input:
        return 0
    last_cmd = cache.input_cache[len(cache.input_cache) - 1]
    sex = {
        str(constant.Instruct.PAIZURI), str(constant.Instruct.TITS_BLOWJOB)
    }
    if len_input:
        if last_cmd in sex:
            return 1
    return 0
