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

@add_premise(constant_promise.Premise.PL_ACTION_FOOD_NORMAL)
def handle_pl_action_food_normal(character_id: int) -> int:
    """
    校验食物调味_正常
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SOUR)
def handle_pl_action_food_sour(character_id: int) -> int:
    """
    校验食物调味_酸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SWEET)
def handle_pl_action_food_sweet(character_id: int) -> int:
    """
    校验食物调味_甜
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_BITTER)
def handle_pl_action_food_bitter(character_id: int) -> int:
    """
    校验食物调味_苦
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SPICY)
def handle_pl_action_food_spicy(character_id: int) -> int:
    """
    校验食物调味_辣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SEMEN_HIDDEN)
def handle_pl_action_food_sement_hidden(character_id: int) -> int:
    """
    校验食物调味_巧妙加精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 11:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SEMEN_DIRECT)
def handle_pl_action_food_sement_direct(character_id: int) -> int:
    """
    校验食物调味_直接加精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 12:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_MEDICINE)
def handle_pl_action_food_medicine(character_id: int) -> int:
    """
    校验食物调味_加药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning >= 100:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_BIRTH_CONTROL_AFTER)
def handle_pl_action_food_birth_control_after(character_id: int) -> int:
    """
    校验食物调味_加事后避孕药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 102:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_PHILTER)
def handle_pl_action_food_philter(character_id: int) -> int:
    """
    校验食物调味_加媚药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 103:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_DIURETICS_ONCE)
def handle_pl_action_food_diuretics_once(character_id: int) -> int:
    """
    校验食物调味_加一次性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 105:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_DIURETICS_PERSISTENT)
def handle_pl_action_food_diuretics_persistent(character_id: int) -> int:
    """
    校验食物调味_加持续性利尿剂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 106:
        return 1
    return 0

@add_premise(constant_promise.Premise.PL_ACTION_FOOD_SLEEPING_PILLS)
def handle_pl_action_food_sleeping_pills(character_id: int) -> int:
    """
    校验食物调味_加安眠药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 107:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_ACTION_FOOD_CLOMID)
def handle_pl_action_food_clomid(character_id: int) -> int:
    """
    校验食物调味_加排卵促进药
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.special_seasoning == 108:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_QUALITY_LOW)
def handle_food_quality_low(character_id: int) -> int:
    """
    食物品质低
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.quality <= 3:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_QUALITY_MEDIUM)
def handle_food_quality_medium(character_id: int) -> int:
    """
    食物品质中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 4 <= character_data.behavior.target_food.quality <= 5:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_QUALITY_HIGH)
def handle_food_quality_high(character_id: int) -> int:
    """
    食物品质高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 6 <= character_data.behavior.target_food.quality <= 7:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_QUALITY_HIGHEST)
def handle_food_quality_highest(character_id: int) -> int:
    """
    食物品质最高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.target_food.quality >= 8:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_RECIPE_DIFFICULTY_LOW)
def handle_food_recipe_difficulty_low(character_id: int) -> int:
    """
    食物食谱难度低
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.difficulty <= 3:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_RECIPE_DIFFICULTY_MEDIUM)
def handle_food_recipe_difficulty_medium(character_id: int) -> int:
    """
    食物食谱难度中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if 4 <= recipe_data.difficulty <= 5:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_RECIPE_DIFFICULTY_HIGH)
def handle_food_recipe_difficulty_high(character_id: int) -> int:
    """
    食物食谱难度高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if 6 <= recipe_data.difficulty <= 7:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_RECIPE_DIFFICULTY_HIGHEST)
def handle_food_recipe_difficulty_highest(character_id: int) -> int:
    """
    食物食谱难度最高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.difficulty >= 8:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_0)
def handle_food_type_0(character_id: int) -> int:
    """
    食物种类正餐
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 0:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_1)
def handle_food_type_1(character_id: int) -> int:
    """
    食物种类零食
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 1:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_2)
def handle_food_type_2(character_id: int) -> int:
    """
    食物种类饮品
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 2:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_3)
def handle_food_type_3(character_id: int) -> int:
    """
    食物种类酒类
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 3:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_4)
def handle_food_type_4(character_id: int) -> int:
    """
    食物种类乳制品
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 4:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_5)
def handle_food_type_5(character_id: int) -> int:
    """
    食物种类预制食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 5:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_8)
def handle_food_type_8(character_id: int) -> int:
    """
    食物种类加料咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 8:
        return 1
    return 0

@add_premise(constant_promise.Premise.FOOD_TYPE_9)
def handle_food_type_9(character_id: int) -> int:
    """
    食物种类其他
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    recipe_id = character_data.behavior.target_food.recipe
    if recipe_id == -1:
        return 0
    recipe_data = cache.recipe_data[recipe_id]
    if recipe_data.type == 9:
        return 1
    return 0

@add_premise(constant_promise.Premise.FIND_FOOD_WEIRD_FLAG_0)
def handlefind_food_weird_flag_0(character_id: int) -> int:
    """
    自身没有发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.find_food_weird == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.FIND_FOOD_WEIRD_FLAG_1)
def handlefind_food_weird_flag_1(character_id: int) -> int:
    """
    自身发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.find_food_weird == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_FIND_FOOD_WEIRD_FLAG_0)
def handlefind_t_food_weird_flag_0(character_id: int) -> int:
    """
    交互对象没有发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.find_food_weird == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_FIND_FOOD_WEIRD_FLAG_1)
def handlefind_t_food_weird_flag_1(character_id: int) -> int:
    """
    交互对象发现食物有问题
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.find_food_weird == 1:
        return 1
    else:
        return 0
