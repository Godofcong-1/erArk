import random
import uuid
from types import FunctionType
from typing import Dict, Set
from Script.Core.game_type import Recipes, Food
from Script.Core import cache_control, value_handle, game_type, get_text
from Script.Config import game_config
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def init_recipes():
    """初始化菜谱数据"""
    cache.recipe_data = {}
    for recipe_id in game_config.config_recipes:
        recipe_data = game_config.config_recipes[recipe_id]
        recipe = create_recipe(
            recipe_data.name,
            recipe_data.time,
            recipe_data.difficulty,
            recipe_data.money,
            recipe_data.introduce,
            recipe_data.type,
        )
        cache.recipe_data[recipe_id] = recipe


def create_recipe(name: str, time: int, difficulty: int, money: int, introduce: str, type: int) -> Recipes:
    """
    创建菜谱对象
    Keyword arguments:
    name -- 菜谱名字
    time -- 烹饪用时
    difficulty -- 烹饪难度
    Return arguments:
    Recipes -- 菜谱对象
    """
    recipe = Recipes()
    recipe.name = name
    recipe.time = time
    recipe.difficulty = difficulty
    recipe.money = money
    recipe.introduce = introduce
    recipe.type = type
    return recipe


def create_food(
    food_id: str,
    # food_weight: int,
    # food_feel={},
    food_recipe=-1,
    food_quality=5,
    food_maker="",
) -> Food:
    """
    创建食物对象
    Keyword arguments:
    food_id -- 食物配置id
    food_quality -- 食物品质
    food_weight -- 食物重量
    food_feel -- 食物效果
    food_maker -- 食物制作者
    food_recipe -- 食谱id(为-1时表示不是用食谱制作出来的基础食材)
    Return arguments:
    Food -- 食物对象
    """
    recipe_data: game_type.Recipes = cache.recipe_data[food_recipe]
    food = Food()
    food.id = food_id
    food.uid = uuid.uuid4()
    # if food_id != "":
    #     food_config = game_config.config_food[food_id]
    #     if food_id in game_config.config_food_feel_data:
    #         food_feel_data = game_config.config_food_feel_data[food_id]
    #         for feel in food_feel_data:
    #             food.feel.setdefault(feel, 0)
    #             food.feel[feel] += food_feel_data[feel] / 100 * food.weight
    #     food.cook = food_config.cook
    #     food.eat = food_config.eat
    #     food.seasoning = food_config.seasoning
    #     food.fruit = food_config.fruit
    # else:
    #     food.feel = food_feel
    #     food.eat = 1
    #     food.cook = 0
    #     food.seasoning = 0
    food.quality = food_quality
    food.maker = food_maker
    food.recipe = food_recipe
    food.name = recipe_data.name
    return food


def separate_weight_food(old_food: Food, weight: int) -> Food:
    """
    从指定食物中分离出指定重量的食物并创建新食物对象
    Keyword arguments:
    old_food -- 原本的食物对象
    Return arguments:
    Food -- 分离得到的食物对象
    """
    new_food = Food()
    if old_food.weight < weight:
        weight = old_food.weight
    new_food.cook = old_food.cook
    new_food.eat = old_food.eat
    new_food.fruit = old_food.fruit
    new_food.id = old_food.id
    new_food.uid = uuid.uuid4()
    new_food.maker = old_food.maker
    new_food.quality = old_food.quality
    new_food.recipe = old_food.recipe
    new_food.seasoning = old_food.seasoning
    new_food.weight = weight
    for feel in old_food.feel:
        now_feel_num = old_food.feel[feel] / old_food.weight * weight
        new_food.feel[feel] = now_feel_num
        old_food.feel[feel] -= now_feel_num
    old_food.weight -= weight
    return new_food


def create_rand_food(food_id: str, food_weight=-1, food_quality=-1) -> Food:
    """
    创建随机食材
    Keyword arguments:
    food_id -- 食物配置id
    food_weight -- 食物重量(为-1时随机)
    food_quality -- 食物品质(为-1时随机)
    Return arguments:
    Food -- 食物对象
    """
    if food_weight == -1:
        food_weight = random.randint(1, 1000000)
    if food_quality == -1:
        food_quality = random.randint(0, 4)
    return create_food(food_id, food_quality, food_weight)


def cook(food_data: Dict[str, Food], recipe_id: int, cook_level: int, maker: str) -> Food:
    """
    按食谱烹饪食物
    Keyword arguments:
    food_data -- 食材数据
    recipe_id -- 菜谱id
    cook_level -- 烹饪技能等级
    maker -- 制作者
    Return arguments:
    Food -- 食物对象
    """
    recipe = cache.recipe_data[recipe_id]
    cook_judge = True
    feel_data = {}
    # quality_data = game_config.config_food_quality_weight_data[cook_level]
    # now_quality = int(value_handle.get_random_for_weight(quality_data))
    # now_weight = 0
    # for food in recipe.base:
    #     if food not in food_data:
    #         cook_judge = False
    #         break
    #     now_food = food_data[food]
    #     rand_weight = random.randint(75, 125)
    #     if now_food.weight < rand_weight:
    #         cook_judge = False
    #         break
    #     for feel in now_food.feel:
    #         feel_data.setdefault(feel, 0)
    #         feel_data[feel] += now_food.feel[feel] / now_food.weight * rand_weight
    #     now_food.weight -= rand_weight
    #     now_weight += rand_weight
    # if not cook_judge:
    #     return create_food(65, now_quality, now_weight, [])
    # for food in recipe.ingredients:
    #     if food not in food_data:
    #         cook_judge = False
    #         break
    #     now_food = food_data[food]
    #     rand_weight = random.randint(25, 75)
    #     if now_food.weight < rand_weight:
    #         cook_judge = False
    #         break
    #     for feel in now_food.feel:
    #         feel_data.setdefault(feel, 0)
    #         feel_data[feel] += now_food.feel[feel] / now_food.weight * rand_weight
    #     now_food.weight -= rand_weight
    #     now_weight += rand_weight
    # if not cook_judge:
    #     return create_food(65, now_quality, now_weight, [])
    # for food in recipe.seasoning:
    #     if food not in food_data:
    #         cook_judge = False
    #         break
    #     now_food = food_data[food]
    #     rand_weight = random.randint(3, 7)
    #     if now_food.weight < rand_weight:
    #         cook_judge = False
    #         break
    #     for feel in now_food.feel:
    #         feel_data.setdefault(feel, 0)
    #         now_feel_num = now_food.feel[feel] / now_food.weight * rand_weight
    #         feel_data[feel] += now_feel_num
    #         now_food.feel[feel] -= now_feel_num
    #     now_food.weight -= rand_weight
    #     now_weight += rand_weight
    # if not cook_judge:
    #     return create_food(65, now_quality, now_weight, [])
    return create_food("", recipe_id, cook_level, maker)


def init_restaurant_data():
    """初始化餐馆内的食物数据"""
    cache.restaurant_data = {}
    max_people = len(cache.npc_id_got)
    cook_index = 0
    while 1:
        recipes_id_list = list(cache.recipe_data.keys())
        recipes_id = random.choice(recipes_id_list)
        food_list = {}
        recipes = cache.recipe_data[recipes_id]
        # 难度上无法制作的菜谱直接跳过
        if recipes.difficulty == 999:
            continue
        # 无法制作的种类的菜谱直接跳过
        if recipes.type in {4,8,9}:
            continue
        # for food_id in recipes.ingredients:
        #     if food_id not in cache.restaurant_data or not len(cache.restaurant_data[food_id]):
        #         food_judge = False
        #         break
        #     food_id_list = list(cache.restaurant_data[food_id].keys())
        #     now_food_id = food_id_list[0]
        #     now_food = cache.restaurant_data[food_id][now_food_id]
        #     food_list[now_food.id] = now_food
        # if not food_judge:
        #     continue
        # for food_id in recipes.seasoning:
        #     if food_id not in cache.restaurant_data or not len(cache.restaurant_data[food_id]):
        #         food_judge = False
        #         break
        #     food_id_list = list(cache.restaurant_data[food_id].keys())
        #     now_food_id = food_id_list[0]
        #     now_food = cache.restaurant_data[food_id][now_food_id]
        #     food_list[now_food.id] = now_food
        # if not food_judge:
        #     continue
        new_food = cook(food_list, recipes_id, 5, "")
        cache.restaurant_data.setdefault(str(recipes_id), {})
        cache.restaurant_data[str(recipes_id)][new_food.uid] = new_food
        # for food_id in food_list:
        #     now_food = food_list[food_id]
        #     if now_food.weight <= 0:
        #         del cache.restaurant_data[now_food.id][now_food.uid]
        #     else:
        #         cache.restaurant_data[now_food.id][now_food.uid] = now_food
        cook_index += 1
        if cook_index == max_people*3:
            break


def init_makefood_data():
    """初始化做饭区内的食物数据"""
    recipe_data = cache.recipe_data
    character_data = cache.character_data[0]
    food_list = {}
    cache.makefood_data = {}
    for recipes_id in recipe_data:
        if character_data.ability[43] >= recipe_data[recipes_id].difficulty:
            new_food = cook(food_list, recipes_id, 5, "")
            cache.makefood_data.setdefault(str(recipes_id), {})
            cache.makefood_data[str(recipes_id)][new_food.uid] = new_food


def get_character_food_bag_type_list_buy_food_type(character_id: int, food_type: str) -> Dict[str, Set]:
    """
    获取角色背包内指定类型的食物种类
    Keyword arguments:
    character_id -- 角色id
    food_type -- 食物类型
    Return arguments:
    Dict -- 食物名字数据 食物名字:uid集合
    """
    food_list = {}
    character_data = cache.character_data[character_id]
    for food_uid in character_data.food_bag:
        food_data: Food = character_data.food_bag[food_uid]
        # if food_data.id in game_config.config_food_feel_data:
        #     food_feel_data = game_config.config_food_feel_data[food_data.id]
        # else:
        #     food_feel_data = {}
        # if food_type == _("主食"):
        if food_data.recipe != -1:
            food_name = cache.recipe_data[food_data.recipe].name
            food_list.setdefault(food_name, set())
            food_list[food_name].add(food_uid)
        # elif food_type == _("零食"):
        #     if food_data.recipe == -1:
        #         food_config = game_config.config_food[food_data.id]
        #         if food_config.eat:
        #             food_name = food_config.name
        #             food_list.setdefault(food_name, set())
        #             food_list[food_name].add(food_uid)
        # elif food_type == _("饮品"):
        #     if food_data.recipe == -1:
        #         if (
        #             28 in food_feel_data
        #             and not food_config.fruit
        #             and food_config.eat
        #             and (27 not in food_feel_data or food_feel_data[28] > food_feel_data[27])
        #         ):
        #             food_name = food_config.name
        #             food_list.setdefault(food_name, set())
        #             food_list[food_name].add(food_uid)
        #     else:
        #         if 28 in food_data.feel and (
        #             27 not in food_data.feel or food_data.feel[28] > food_data.feel[27]
        #         ):
        #             food_name = cache.recipe_data[food_data.recipe].name
        #             food_list.setdefault(food_name, set())
        #             food_list[food_name].add(food_uid)
        # elif food_type == _("水果"):
        #     if food_data.recipe == -1:
        #         if food_config.fruit:
        #             food_name = food_config.name
        #             food_list.setdefault(food_name, set())
        #             food_list[food_name].add(food_uid)
        # elif food_type == _("食材"):
        #     if food_data.recipe == -1:
        #         if food_config.cook:
        #             food_name = food_config.name
        #             food_list.setdefault(food_name, set())
        #             food_list[food_name].add(food_uid)
        # elif food_type == _("调料"):
        #     if food_data.recipe == -1:
        #         if food_config.seasoning:
        #             food_name = food_config.name
        #             food_list.setdefault(food_name, set())
        #             food_list[food_name].add(food_uid)
    return food_list


def get_restaurant_food_type_list_buy_food_type(food_type: str) -> Dict[uuid.UUID, str]:
    """
    获取餐馆内指定类型的食物种类
    Keyword arguments:
    food_type -- 食物类型
    Return arguments:
    dict -- 食物列表 食物id:食物名字
    """
    food_list = {}
    for food_id in cache.restaurant_data:
        if not len(cache.restaurant_data[food_id]):
            continue
        if food_type == _("主食"):
            now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
            now_food: game_type.Food = cache.restaurant_data[food_id][now_food_uid]
            if now_food.recipe != -1:
                food_list[food_id] = cache.recipe_data[int(food_id)].name
        # elif food_type == _("零食"):
        #     now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
        #     now_food: game_type.Food = cache.restaurant_data[food_id][now_food_uid]
        #     if now_food.recipe == -1:
        #         food_config = game_config.config_food[food_id]
        #         if food_config.eat:
        #             food_list[food_id] = food_config.name
        # elif food_type == _("饮品"):
        #     now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
        #     now_food: game_type.Food = cache.restaurant_data[food_id][now_food_uid]
        #     if now_food.recipe == -1:
        #         food_config = game_config.config_food[food_id]
        #         if food_id in game_config.config_food_feel_data:
        #             food_feel_data = game_config.config_food_feel_data[food_id]
        #             if (
        #                 28 in food_feel_data
        #                 and (not food_config.fruit)
        #                 and food_config.eat
        #                 and ((27 not in food_feel_data) or (food_feel_data[28] > food_feel_data[27]))
        #             ):
        #                 food_list[food_id] = food_config.name
        #     else:
        #         now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
        #         now_food = cache.restaurant_data[food_id][now_food_uid]
        #         if 28 in now_food.feel and (
        #             27 not in now_food.feel or now_food.feel[28] > now_food.feel[27]
        #         ):
        #             food_list[food_id] = cache.recipe_data[int(food_id)].name
        # elif food_type == _("水果"):
        #     now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
        #     now_food: game_type.Food = cache.restaurant_data[food_id][now_food_uid]
        #     if now_food.recipe == -1:
        #         food_config = game_config.config_food[now_food.id]
        #         if food_config.fruit:
        #             food_list[food_id] = food_config.name
        # elif food_type == "食材":
        #     now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
        #     now_food: game_type.Food = cache.restaurant_data[food_id][now_food_uid]
        #     if now_food.recipe == -1:
        #         food_config = game_config.config_food[now_food.id]
        #         if food_config.cook:
        #             food_list[food_id] = food_config.name
        # elif food_type == "调料":
        #     now_food_uid = list(cache.restaurant_data[food_id].keys())[0]
        #     now_food: game_type.Food = cache.restaurant_data[food_id][now_food_uid]
        #     if now_food.recipe == -1:
        #         food_config = game_config.config_food[now_food.id]
        #         if food_config.seasoning:
        #             food_list[food_id] = food_config.name
    return food_list

def get_cook_level_food_type(food_type: str) -> Dict[uuid.UUID, str]:
    """
    获取可以烹饪的的食物种类
    Keyword arguments:
    food_type -- 食物类型
    Return arguments:
    dict -- 食物列表 食物id:食物名字
    """
    food_list = {}
    for food_id in cache.makefood_data:
        if not len(cache.makefood_data[food_id]):
            continue

        # 选择对应食物种类
        if food_type == _("主食") and cache.recipe_data[int(food_id)].type != 0:
            continue
        elif food_type == _("零食") and cache.recipe_data[int(food_id)].type != 1:
            continue
        elif food_type == _("饮品") and cache.recipe_data[int(food_id)].type != 2:
            continue
        elif food_type == _("酒类") and cache.recipe_data[int(food_id)].type != 3:
            continue
        elif food_type == _("咖啡") and cache.recipe_data[int(food_id)].type != 8:
            continue
        elif food_type == _("其他") and cache.recipe_data[int(food_id)].type != 9:
            continue

        # 赋予食物其他属性
        now_food_uid = list(cache.makefood_data[food_id].keys())[0]
        now_food: game_type.Food = cache.makefood_data[food_id][now_food_uid]
        if now_food.recipe != -1:
            food_list[food_id] = cache.recipe_data[int(food_id)].name
    return food_list

def judge_accept_special_seasoning_food(character_id: int):
    """
    是否接受特殊调味的食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 接受或不接受
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_id]
    return_d100 = random.randint(1,100)
    # 口才+厨艺的双重加成判定
    accept_rate = pl_character_data.ability[40] *10 + pl_character_data.ability[43] * 10
    accept_rate = max(accept_rate,5) # 保底5%几率

    # debug模式直接过
    if cache.debug_mode:
        return 1
    # 567异常则直接通过
    if handle_premise.handle_unnormal_567(character_id):
        return 1
    # 普通调味直接进行判定
    if pl_character_data.behavior.food_seasoning <= 10:
        if return_d100 <= accept_rate:
            target_data.sp_flag.find_food_weird = 0
            return 1
        else:
            target_data.sp_flag.find_food_weird = 1
            return 0
    # 其他特殊调味
    else:
        # 精液判定
        if pl_character_data.behavior.food_seasoning in {11,12}:
            # 性无知则直接接受精液食物
            if target_data.talent[222]:
                target_data.sp_flag.find_food_weird = 0
                return 1
            # 精爱味觉或淫乱则直接通过
            if target_data.talent[31] or target_data.talent[40]:
                target_data.sp_flag.find_food_weird = 1
                return 1

            # 精液_巧妙混合
            if pl_character_data.behavior.food_seasoning == 11:
                # 3级爱情系或至少2级隶属系的话才接受
                for talent_id in {203,204,212,213,214}:
                    if target_data.talent[talent_id]:
                        target_data.sp_flag.find_food_weird = 1
                        return 1
                # 进行概率判定，难度*5
                if return_d100 * 5 <= accept_rate:
                    target_data.sp_flag.find_food_weird = 0
                    return 1
                else:
                    target_data.sp_flag.find_food_weird = 1
                    return 0
            # 精液_直接盖上
            elif pl_character_data.behavior.food_seasoning == 12:
                # 4级爱情系或至少3级隶属系的话才接受
                for talent_id in {204,213,214}:
                    if target_data.talent[talent_id]:
                        target_data.sp_flag.find_food_weird = 1
                        return 1
                # 进行概率判定，难度*10
                if return_d100 * 10 <= accept_rate:
                    target_data.sp_flag.find_food_weird = 0
                    return 1
                else:
                    target_data.sp_flag.find_food_weird = 1
                    return 0
        # 药物判定
        elif pl_character_data.behavior.food_seasoning >= 101:
            # 进行概率判定，难度*2
            if return_d100 * 2 <= accept_rate:
                target_data.sp_flag.find_food_weird = 0
                return 1
            else:
                target_data.sp_flag.find_food_weird = 1
                return 0

    return 0
