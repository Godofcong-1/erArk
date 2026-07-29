from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.Design import instuct_judege, handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def get_drunk_level(character_id: int):
    """
    按角色当前醉酒值返回当前醉酒等级的cid与名称\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    int -- 醉酒等级cid,0-3\n
    str -- 醉酒等级名,清醒-烂醉
    """
    character_data = cache.character_data[character_id]
    value = character_data.drunk_point
    # 如果角色千杯不醉，则醉酒值*0.1
    if handle_premise.handle_self_have_never_drunk(character_id):
        value *= 0.1
    # 如果角色酒量好，则醉酒值*0.8
    elif handle_premise.handle_self_have_good_alcohol_tolerance(character_id):
        value *= 0.8
    # 如果角色酒量差，则醉酒值*1.5
    elif handle_premise.handle_self_have_bad_alcohol_tolerance(character_id):
        value *= 1.5
    # 如果角色一杯就倒，则醉酒值*5
    elif handle_premise.handle_self_have_easily_drunk(character_id):
        value *= 5
    # 遍历醉酒等级配置，找到第一个醉酒值上限大于等于当前值的等级
    for now_cid in game_config.config_drunk_level:
        now_data = game_config.config_drunk_level[now_cid]
        if value > now_data.drunk_point:
            continue
        else:
            return now_cid, now_data.name
    # 超过所有等级上限时，返回最高醉酒等级
    return 3, game_config.config_drunk_level[3].name


def get_food_drunk_value(food: game_type.Food) -> int:
    """
    查询某个食物会增加的醉酒值\n
    Keyword arguments:\n
    food -- 食物对象\n
    Return arguments:\n
    int -- 食用该食物会增加的醉酒值
    """
    # 根据食物的菜谱id查找菜谱数据
    recipe_id = food.recipe
    if recipe_id not in game_config.config_recipes:
        return 0
    # 从菜谱数据中获取该食物的酒精等级cid
    alcohol_level = game_config.config_recipes[recipe_id].alcohol
    # 根据酒精等级cid查找对应的醉酒值变化量
    if alcohol_level not in game_config.config_alcohol_level:
        return 0
    return game_config.config_alcohol_level[alcohol_level].drunk_change

def add_drunk_point(character_id: int, food: game_type.Food, taste_wine_flag: bool = False):
    """
    根据食用的食物增加角色的醉酒值\n
    Keyword arguments:\n
    character_id -- 角色id\n
    food -- 食物对象\n
    taste_wine_flag -- 是否为品酒指令结算的醉酒值增加，默认为False\n
    Return arguments:\n
    None
    """
    # 获取该食物会增加的醉酒值
    character_data = cache.character_data[character_id]
    add_value = get_food_drunk_value(food)
    if add_value <= 0:
        return
    # 如果是品酒指令结算的醉酒值增加，则醉酒值只增加30%
    if taste_wine_flag:
        add_value = round(add_value * 0.3)
    # 增加角色的醉酒值，并确保不超过100
    character_data.drunk_point = min(100, character_data.drunk_point + add_value)
    handle_premise.settle_chara_unnormal_flag(character_id, 5)
    handle_premise.settle_chara_unnormal_flag(character_id, 6)


def reduce_drunk_point(character_id: int, time: int):
    """
    根据时间流逝减少角色的醉酒值\n
    Keyword arguments:\n
    character_id -- 角色id\n
    time -- 流逝的时间(分钟)\n
    Return arguments:\n
    None
    """
    character_data = cache.character_data[character_id]
    # 醉酒值小于等于0时不再减少
    if character_data.drunk_point <= 0:
        return
    # 时间小于5分钟时不减少醉酒值
    if time < 5:
        return
    # 5分钟及以上但小于10分钟时按10分钟计算，其余按每10分钟1点四舍五入计算
    if time < 10:
        base_reduce = 1
    else:
        base_reduce = round(time / 10)
    coefficient = 1.0
    # 根据当前醉酒程度获取修正系数：醉酒×0.8，烂醉×0.5，其他状态不影响
    drunk_cid, drunk_name = get_drunk_level(character_id)
    if drunk_cid == 2:
        coefficient *= 0.8
    elif drunk_cid == 3:
        coefficient *= 0.5
    # 根据当前空腹程度获取修正系数：饥饿×1.2，饱腹×0.8，其他状态不影响
    if handle_premise.handle_hunger_ge_80(character_id):
        coefficient *= 1.2
    elif handle_premise.handle_hunger_le_20(character_id):
        coefficient *= 0.8
    # 如果当前正在睡觉，则醉酒值减少速度加快，按1.5倍计算
    if handle_premise.handle_action_sleep(character_id):
        coefficient *= 1.5
    # 计算最终减少值（保留浮点，最终对醉酒值取整），并确保醉酒值不低于0
    reduce_value = base_reduce * coefficient
    character_data.drunk_point = max(0, round(character_data.drunk_point - reduce_value))
    # 减少的醉酒值同比转化为尿意值
    character_data.urinate_point = min(300, character_data.urinate_point + round(reduce_value * 1.5))
    handle_premise.settle_chara_unnormal_flag(character_id, 5)
    handle_premise.settle_chara_unnormal_flag(character_id, 6)


def judge_accept_alcohol_food(character_id: int, food: game_type.Food) -> bool:
    """
    判断角色是否接受饮用酒类食物\n
    Keyword arguments:\n
    character_id -- 饮用食物的角色id\n
    food -- 食物对象\n
    Return arguments:\n
    bool -- True表示通过判定(可进行后续判定),False表示拒绝饮酒
    """
    # 根据食物的菜谱id查找菜谱数据
    recipe_id = food.recipe
    if recipe_id not in game_config.config_recipes:
        return True
    # 从菜谱数据中获取该食物的酒精等级cid
    alcohol_level = game_config.config_recipes[recipe_id].alcohol
    # 非酒类食物(酒精等级为0)直接通过判定
    if alcohol_level == 0:
        return True
    # 酒精等级cid到实行值判定指令名的映射
    instruct_name_map = {
        1: _("低度饮酒"),
        2: _("中低度饮酒"),
        3: _("中高度饮酒"),
        4: _("高度饮酒"),
        5: _("极高度饮酒"),
    }
    instruct_name = instruct_name_map.get(alcohol_level)
    # 未知的酒精等级默认通过判定
    if instruct_name is None:
        return True
    # 计算实行值判定结果，成功则通过判定
    judge_result = instuct_judege.calculation_instuct_judege(0, character_id, instruct_name, not_draw_flag=True)
    return judge_result[0] == 1

def taste_wine(character_id: int):
    """
    角色品酒，角色随机选一个酒，根据角色的酒量和当前醉酒值选择，酒量越好、醉酒程度越高越可能选择度数更高的酒，并结算部分饮用效果\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    None
    """
    import random
    from Script.System.Cooking_System import cooking
    character_data = cache.character_data[character_id]
    # 获取角色当前醉酒值和醉酒等级
    drunk_value = character_data.drunk_point
    drunk_cid, drunk_name = get_drunk_level(character_id)
    # 角色的酒量基础为3，从一杯就倒到千杯不醉，分别对应为1到5
    alcohol_tolerance = 3
    if handle_premise.handle_self_have_easily_drunk(character_id):
        alcohol_tolerance = 1
    elif handle_premise.handle_self_have_bad_alcohol_tolerance(character_id):
        alcohol_tolerance = 2
    elif handle_premise.handle_self_have_good_alcohol_tolerance(character_id):
        alcohol_tolerance = 4
    elif handle_premise.handle_self_have_never_drunk(character_id):
        alcohol_tolerance = 5
    # 根据醉酒值和酒量计算一个权重值，用于选择酒的度数，醉酒值越高、酒量越好，权重值越高
    weight = drunk_value * 0.5 + alcohol_tolerance * 10
    # 该值随机上下浮动，增加随机性
    weight *= random.uniform(0.5, 1.5)
    # 根据权重值选择酒的度数，权重值越高，选择度数越高的酒的概率越大
    if weight < 20:
        alcohol_level = 1
    elif weight < 40:
        alcohol_level = 2
    elif weight < 60:
        alcohol_level = 3
    elif weight < 80:
        alcohol_level = 4
    else:
        alcohol_level = 5
    # 选择该酒精等级的随机一个酒
    target_wines = [wine for wine in game_config.config_recipes.values() if wine.alcohol == alcohol_level]
    if not target_wines:
        return
    selected_wine_recips = random.choice(target_wines)
    # 创建该酒的食物对象
    new_wine_food = cooking.create_food("", int(selected_wine_recips.cid), 1, "")
    # 将行动的食物对象设置为该酒
    character_data.behavior.target_food = new_wine_food
    add_drunk_point(character_id, new_wine_food, taste_wine_flag=True)
