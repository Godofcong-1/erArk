import random
import uuid
from types import FunctionType
from typing import Dict, Set
from Script.Core.game_type import Recipes, Food
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def init_recipes():
    """初始化菜谱数据"""
    cache = cache_control.cache
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
    return cache.recipe_data


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
    food_recipe=-1,
    food_quality=5,
    food_maker="",
) -> Food:
    """
    创建食物对象
    Keyword arguments:
    food_id -- 食物配置id
    food_recipe -- 食谱id(为-1时表示不是用食谱制作出来的基础食材)
    food_quality -- 食物品质
    food_maker -- 食物制作者
    Return arguments:
    Food -- 食物对象
    """
    recipe_data: game_type.Recipes = cache.recipe_data[food_recipe]
    food = Food()
    food.id = food_id
    food.uid = uuid.uuid4()
    food.quality = food_quality
    food.maker = food_maker
    food.recipe = food_recipe
    food.name = recipe_data.name
    return food


# 烹饪问题库的四个阶段（顺序固定：备料->烹饪->调味->装盘），值与 cook_question csv 中 stage 列一致
COOK_QUESTION_STAGES = [_("备料"), _("烹饪"), _("调味"), _("装盘")]
""" 烹饪问题库阶段顺序 """


def get_good_quality_cap() -> int:
    """
    获取标准模式（及精细模式基础值）的品质上限——美味（食物质量cid=3）的料理技能上限值
    Return arguments:
    int -- 美味品质对应的上限值
    """
    return game_config.config_food_quality[3].ability_level


def get_max_food_quality() -> int:
    """
    获取食物品质的绝对上限——所有质量等级中的最大料理技能上限值（绝珍）
    Return arguments:
    int -- 食物品质绝对上限值
    """
    return max(quality.ability_level for quality in game_config.config_food_quality.values())


def get_base_food_quality(character_id: int = 0) -> int:
    """
    获取制作食物的基础品质：玩家料理技能(ability[43])，封顶到美味上限
    Keyword arguments:
    character_id -- 角色id，默认为0（玩家）
    Return arguments:
    int -- 基础品质值（不超过美味上限）
    """
    character_data = cache.character_data[character_id]
    return min(character_data.ability[43], get_good_quality_cap())


def is_special_seasoning(seasoning_cid: int) -> bool:
    """
    判断调味是否为特殊调味（精液/药物等，cid>=11）
    Keyword arguments:
    seasoning_cid -- 调味cid
    Return arguments:
    bool -- 是否为特殊调味
    """
    return seasoning_cid >= 11


def get_special_seasoning_question_stage(special_seasoning: int):
    """
    获取特殊调味对应的烹饪问题阶段替换规则
    选择特殊调味进行精细烹饪时，其对应的常规阶段问题池会被替换为特殊阶段的问题池
    Keyword arguments:
    special_seasoning -- 调味cid
    Return arguments:
    tuple -- (被替换的常规阶段, 替换用的特殊阶段)，无替换规则则返回 None
    """
    # 射入精液（巧妙地混入食物中，cid11）：替换调味阶段为精液调味题
    if special_seasoning == 11:
        return (_("调味"), _("调味_精液"))
    # 射入精液（不作掩饰直接射上去，cid12）：替换装盘阶段为精液装盘题
    if special_seasoning == 12:
        return (_("装盘"), _("装盘_精液"))
    # 加入药物（所有药物cid均>100）：替换调味阶段为药物调味题
    if special_seasoning > 100:
        return (_("调味"), _("调味_药物"))
    # 其他调味无替换规则（母乳暂未在游戏中实装）
    return None


def has_cook_question_library(food_id: int) -> bool:
    """
    判断指定食物是否拥有可用的烹饪问题库（至少一个阶段存在题目）
    Keyword arguments:
    food_id -- 食物（菜谱）id
    Return arguments:
    bool -- 是否存在可用题库
    """
    stage_data = game_config.config_cook_question.get(food_id, {})
    for stage in COOK_QUESTION_STAGES:
        if stage_data.get(stage):
            return True
    return False


def get_food_cook_questions(food_id: int) -> Dict[str, list]:
    """
    获取指定食物的烹饪问题库（阶段 -> 问题列表）
    Keyword arguments:
    food_id -- 食物（菜谱）id
    Return arguments:
    Dict -- 阶段到问题列表的映射
    """
    return game_config.config_cook_question.get(food_id, {})


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
    return create_food("", recipe_id, cook_level, maker)


def init_food_shop_data(update_restaurant_id: int = -2, new_day_flag: bool = False):
    """
    初始化食物商店内的食物数据\n
    Keyword arguments:\n
    update_restaurant_id -- 餐馆id，默认为-2，如果不是-2则仅刷新对应id的餐馆的食物\n
    new_day_flag -- 是否为新的一天，默认为False\n
    """
    cache = cache_control.cache
    # 如果是新的一天则清空食物数据
    if new_day_flag:
        cache.rhodes_island.dining_hall_data = {}
    max_people = len(cache.npc_id_got)
    # 初始化食堂内的食物
    if update_restaurant_id in [-1,-2]:
        cook_index = 0
        while 1:
            recipes_id_list = list(cache.recipe_data.keys())
            recipes_id = random.choice(recipes_id_list)
            food_list = {}
            now_recipe_data = cache.recipe_data[recipes_id]
            # 只能制作预制菜
            if now_recipe_data.type != 5:
                continue
            # 随机1~5的烹饪技能等级
            cook_level = random.randint(1, 5)
            new_food = cook(food_list, recipes_id, cook_level, "")
            cache.rhodes_island.dining_hall_data.setdefault(str(recipes_id), {})
            cache.rhodes_island.dining_hall_data[str(recipes_id)][new_food.uid] = new_food
            cook_index += 1
            if cook_index >= max_people * 3:
                break
    # 初始化餐馆内的食物
    for restaurant_id in game_config.config_restaurant:
        # 仅刷新指定id的餐馆
        if update_restaurant_id >= 0:
            if restaurant_id != update_restaurant_id:
                continue
        cook_index = 0
        cache.rhodes_island.restaurant_data[restaurant_id] = {}
        while 1:
            food_list = {}
            # 只能选择该餐馆自己的食谱
            recipes_id_list = [ x for x in game_config.config_recipes if game_config.config_recipes[x].restaurant == restaurant_id]
            recipes_id = random.choice(recipes_id_list)
            now_recipe_data = cache.recipe_data[recipes_id]
            # 难度上无法制作的菜谱直接跳过
            if now_recipe_data.difficulty == 999:
                continue
            # 无法制作的种类的菜谱直接跳过
            if now_recipe_data.type in {4,5,8,9}:
                continue
            cook_level = random.randint(3, 7)
            new_food = cook(food_list, recipes_id, cook_level, "")
            cache.rhodes_island.restaurant_data.setdefault(restaurant_id, {})
            cache.rhodes_island.restaurant_data[restaurant_id].setdefault(str(recipes_id), {})
            cache.rhodes_island.restaurant_data[restaurant_id][str(recipes_id)][new_food.uid] = new_food
            cook_index += 1
            if cook_index >= max_people:
                break
    # 如果是新的一天则初始化地摊小贩的食物
    if new_day_flag:
        cook_index = 0
        cache.rhodes_island.stall_vendor_data[0] = {}
        while 1:
            food_list = {}
            # 选择零食和饮料类型的食谱
            recipes_id_list = [ x for x in game_config.config_recipes if game_config.config_recipes[x].type in [1, 2]]
            recipes_id = random.choice(recipes_id_list)
            now_recipe_data = cache.recipe_data[recipes_id]
            cook_level = random.randint(1, 8)
            new_food = cook(food_list, recipes_id, cook_level, "")
            cache.rhodes_island.stall_vendor_data[0].setdefault(str(recipes_id), {})
            cache.rhodes_island.stall_vendor_data[0][str(recipes_id)][new_food.uid] = new_food
            cook_index += 1
            if cook_index >= max_people or cook_index >= 10:
                break

def get_character_cookable_recipes(character_id: int = 0, weight_flag = False, food_type: int = -1) -> list[int]:
    """
    获取角色可以制作的食物食谱列表
    Keyword arguments:
    character_id -- 角色id，默认为0
    输出权重标记 -- 是否根据食谱难度的权重输出列表，默认为False
    food_type -- 食物类型，默认为-1表示不限制类型
    Return arguments:
    list -- 食谱id列表
    """
    character_data = cache.character_data[character_id]
    cookable_recipes_list = []
    for recipe_id, recipe in cache.recipe_data.items():
        # 难度上无法制作的菜谱直接跳过
        if recipe.difficulty >= 100:
            continue
        # 无法制作的种类的菜谱直接跳过
        if recipe.type in {4,5,9}:
            continue
        # 限制食物类型时，非指定类型的菜谱直接跳过
        if food_type != -1 and recipe.type != food_type:
            continue
        # 非玩家跳过咖啡
        if character_id != 0 and recipe.type in {8}:
            continue
        # 非玩家跳过庆典料理（庆典只由博士发起）
        if character_id != 0 and recipe.type == 10:
            continue
        # 难度高于烹饪技能的菜谱直接跳过
        if character_data.ability[43] < recipe.difficulty:
            continue
        # 如果所在位置是博士房间，则菜谱难度大于5的跳过
        if handle_premise.handle_in_dr_room(character_id) and recipe.difficulty > 5:
            continue
        # 根据权重输出列表，最大权重为8，最小权重为1
        if weight_flag:
            weight_num = min(recipe.difficulty, 8)
            weight_num = max(weight_num, 1)
            cookable_recipes_list.extend([recipe_id] * weight_num)
        # 直接输出列表
        else:
            cookable_recipes_list.append(recipe_id)
    return cookable_recipes_list

def init_makefood_data():
    """
    初始化玩家做饭区内可制作的菜谱数据\n
    延迟创建：此处仅记录玩家当前可制作的菜谱id，实际的食物对象在玩家选定菜谱并制作时才创建，\n
    以减少不必要的内存占用和性能消耗。\n
    """
    cache.rhodes_island.makefood_data = {}
    cookable_recipes_list = get_character_cookable_recipes()
    for recipes_id in cookable_recipes_list:
        cache.rhodes_island.makefood_data[str(recipes_id)] = recipes_id


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
        if food_data.recipe != -1:
            food_name = cache.recipe_data[food_data.recipe].name
            food_list.setdefault(food_name, set())
            food_list[food_name].add(food_uid)
    return food_list


def get_food_list_from_food_shop(food_type: str, restaurant_id = -1) -> Dict[uuid.UUID, str]:
    """
    获取餐馆内指定类型的食物种类
    Keyword arguments:
    food_type -- 食物类型
    restaurant_id -- 餐馆id，默认为-1表示食堂
    Return arguments:
    dict -- 食物列表 食物id:食物名字
    """
    # print(f"debug food_type = {food_type}, restaurant_id = {restaurant_id}")
    food_list = {}
    # 食堂内的食物
    if restaurant_id == -1:
        for food_id in cache.rhodes_island.dining_hall_data:
            if not len(cache.rhodes_island.dining_hall_data[food_id]):
                continue
            now_food_uid = list(cache.rhodes_island.dining_hall_data[food_id].keys())[0]
            now_food: game_type.Food = cache.rhodes_island.dining_hall_data[food_id][now_food_uid]
            if now_food.recipe != -1:
                food_list[food_id] = cache.recipe_data[int(food_id)].name
    # 餐馆的食物
    elif restaurant_id in cache.rhodes_island.restaurant_data:
        for food_id in cache.rhodes_island.restaurant_data[restaurant_id]:
            if not len(cache.rhodes_island.restaurant_data[restaurant_id][food_id]):
                continue
            now_food_uid = list(cache.rhodes_island.restaurant_data[restaurant_id][food_id].keys())[0]
            now_food: game_type.Food = cache.rhodes_island.restaurant_data[restaurant_id][food_id][now_food_uid]
            if now_food.recipe != -1:
                food_list[food_id] = cache.recipe_data[int(food_id)].name
    # 地摊小贩的食物
    elif restaurant_id == "Stall_Vendor":
        for food_id in cache.rhodes_island.stall_vendor_data[0]:
            if not len(cache.rhodes_island.stall_vendor_data[0][food_id]):
                continue
            now_food_uid = list(cache.rhodes_island.stall_vendor_data[0][food_id].keys())[0]
            now_food: game_type.Food = cache.rhodes_island.stall_vendor_data[0][food_id][now_food_uid]
            if now_food.recipe != -1:
                food_list[food_id] = cache.recipe_data[int(food_id)].name
    return food_list


def get_cook_from_makefood_data_by_food_type(food_type: str) -> Dict[uuid.UUID, str]:
    """
    按食物种类从做饭区获取可以烹饪的的食物列表
    Keyword arguments:
    food_type -- 食物类型
    Return arguments:
    dict -- 食物列表 食物id:食物名字
    """
    food_list = {}
    for food_id in cache.rhodes_island.makefood_data:
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
        elif food_type == _("庆典") and cache.recipe_data[int(food_id)].type != 10:
            continue

        # 跳过时间为999的食谱
        if cache.recipe_data[int(food_id)].time >= 999:
            continue

        food_list[food_id] = cache.recipe_data[int(food_id)].name
    return food_list


def get_filtered_sorted_cook_data(food_type: str) -> list:
    """
    按食物种类从做饭区获取经过筛选和排序的食物列表
    Keyword arguments:
    food_type -- 食物类型
    Return arguments:
    list -- 食物列表 [(食物id, 食物名字), ...]
    """
    # 获取基础食物列表
    base_food_dict = get_cook_from_makefood_data_by_food_type(food_type)
    food_list = list(base_food_dict.items())
    
    # 获取筛选/排序配置
    filter_type = cache.rhodes_island.makefood_filter_type
    filter_difficulty = cache.rhodes_island.makefood_filter_difficulty
    filter_time = cache.rhodes_island.makefood_filter_time
    sort_type = cache.rhodes_island.makefood_sort_type
    sort_order = cache.rhodes_island.makefood_sort_order
    
    # 应用筛选
    if filter_type or filter_difficulty != -1 or filter_time != -1:
        filtered_list = []
        for food_id, food_name in food_list:
            recipe = cache.recipe_data[int(food_id)]
            
            # 类型筛选
            if filter_type and recipe.type not in filter_type:
                continue
            
            # 难度筛选（档位：0简单0-3，1中等4-6，2困难7+）
            if filter_difficulty != -1:
                if filter_difficulty == 0 and recipe.difficulty > 3:
                    continue
                elif filter_difficulty == 1 and (recipe.difficulty < 4 or recipe.difficulty > 6):
                    continue
                elif filter_difficulty == 2 and recipe.difficulty < 7:
                    continue
            
            # 时间筛选（档位：0快速0-30，1中等31-60，2耗时61+）
            if filter_time != -1:
                if filter_time == 0 and recipe.time > 30:
                    continue
                elif filter_time == 1 and (recipe.time < 31 or recipe.time > 60):
                    continue
                elif filter_time == 2 and recipe.time < 61:
                    continue
            
            filtered_list.append((food_id, food_name))
        food_list = filtered_list
    
    # 应用排序
    if sort_type != 0 and food_list:
        reverse = (sort_order == 1)
        if sort_type == 1:  # 按难度排序
            food_list.sort(key=lambda x: cache.recipe_data[int(x[0])].difficulty, reverse=reverse)
        elif sort_type == 2:  # 按时间排序
            food_list.sort(key=lambda x: cache.recipe_data[int(x[0])].time, reverse=reverse)
        elif sort_type == 3:  # 按类型排序
            food_list.sort(key=lambda x: cache.recipe_data[int(x[0])].type, reverse=reverse)
    
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
    # 食物的菜谱难度
    food_recipe_id = pl_character_data.behavior.target_food.recipe
    food_recipe_data: game_type.Recipes = cache.recipe_data[food_recipe_id]
    food_difficulty = food_recipe_data.difficulty
    # 食物的品质
    food_quality = pl_character_data.behavior.target_food.quality
    # 口才+菜谱难度+食物品质的双重加成判定
    accept_rate = pl_character_data.ability[40] * 10 + food_difficulty * 5 + food_quality * 5
    accept_rate = max(accept_rate,5) # 保底5%几率
    # 「掩味」不再改接受率，改为**被拒绝时大幅降低反感**（见 Settle/default.handle_high_obscenity_failed_adjust）

    # debug模式直接过
    # if cache.debug_mode:
        # return 1
    # 567异常则直接通过
    if handle_premise.handle_unnormal_567(character_id):
        return 1
    # 普通调味直接通过
    elif handle_premise.handle_pl_action_food_normal(0):
        return 1
    # 其他特殊调味
    else:
        # 精液判定
        if handle_premise.handle_pl_action_food_sement_hidden(0) or handle_premise.handle_pl_action_food_sement_direct(0):
            # 精爱味觉或淫乱可以通过
            if target_data.talent[31] or target_data.talent[40]:
                target_data.sp_flag.find_food_weird = True
                # 精爱味觉触发一次绝顶
                if target_data.talent[31]:
                    from Script.Settle.default import base_chara_climix_common_settle
                    base_chara_climix_common_settle(character_id, 0)
                return 1
            # 性无知会直接接受精液食物
            if target_data.talent[222]:
                target_data.sp_flag.find_food_weird = False
                return 1

            # 精液_巧妙混合
            if handle_premise.handle_pl_action_food_sement_hidden(0):
                # 3级爱情系或至少2级隶属系的话才接受
                for talent_id in {203,204,212,213,214}:
                    if target_data.talent[talent_id]:
                        target_data.sp_flag.find_food_weird = True
                        return 1
                # 进行概率判定，难度*5，但不会高于50
                if min(return_d100 * 5, 50) <= accept_rate:
                    target_data.sp_flag.find_food_weird = False
                    return 1
                else:
                    target_data.sp_flag.find_food_weird = True
                    return 0
            # 精液_直接盖上
            elif handle_premise.handle_pl_action_food_sement_direct(0):
                # 4级爱情系或至少3级隶属系的话才接受
                for talent_id in {204,213,214}:
                    if target_data.talent[talent_id]:
                        target_data.sp_flag.find_food_weird = True
                        return 1
                # 进行概率判定，难度*10，但不会高于80
                if min(return_d100 * 10, 80) <= accept_rate:
                    target_data.sp_flag.find_food_weird = False
                    return 1
                else:
                    target_data.sp_flag.find_food_weird = True
                    return 0
        # 药物判定
        elif handle_premise.handle_pl_action_food_medicine(0):
            # 进行概率判定，难度*2，但不会高于40
            if min(return_d100 * 2, 40) <= accept_rate:
                target_data.sp_flag.find_food_weird = False
                return 1
            else:
                target_data.sp_flag.find_food_weird = True
                return 0

    return 0


def find_character_birthplace_restaurant(character_id: int) -> int:
    """
    寻找干员出身地的餐厅
    Keyword arguments:
    character_id -- 干员id
    Return arguments:
    int -- 餐厅id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 莱茵生命的选哥伦比亚咖啡馆，其他哥伦比亚的选约翰老妈汉堡店
    if character_data.relationship.birthplace == 4:
        if character_data.relationship.nation == 42:
            return 2
        return 4
    # 维多利亚的选七城风情餐厅
    elif character_data.relationship.birthplace == 13:
        return 3
    # 龙门的选龙门食坊，其他炎国的选山城茶馆
    elif character_data.relationship.birthplace == 17:
        if character_data.relationship.nation in [13,14,15]:
            return 6
        return 1
    # 拉特兰的选瓦莱丽蛋糕店
    elif character_data.relationship.birthplace == 7:
        return 0
    # 叙拉古的选快捷连锁披萨店
    elif character_data.relationship.birthplace == 16:
        return 7
    return -1

def handle_food_deterioration(character_id: int):
    """
    结算角色持有食物的变质与过期\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:
    int -- 过期食物数量
    """
    character_data = cache.character_data[character_id]
    remove_food_uid_list = []
    # NPC只有在持有食物大于1个时才进行变质与过期结算
    if character_id != 0 and len(character_data.food_bag) <= 1:
        return 0
    for food_uid in character_data.food_bag:
        food_data: Food = character_data.food_bag[food_uid]
        # 食物变质；本菜装了「耐放」型自选特技时损耗更慢（EX 阶只掉 1 点）
        if get_food_special_dim(food_data) == "耐放":
            if is_dish_special_ex(food_data.recipe):
                food_data.quality = food_data.quality - 1
            else:
                food_data.quality = min(food_data.quality - 1, food_data.quality * 3 // 4)
        else:
            food_data.quality = min(food_data.quality - 1, food_data.quality // 2)
        # 食物过期
        if food_data.quality <= 0:
            remove_food_uid_list.append(food_uid)
    for food_uid in remove_food_uid_list:
        character_data.food_bag.pop(food_uid)
    return len(remove_food_uid_list)

# ================= 庆典料理（博士专属会食宴） =================
# 菜谱本体（名称/时间/难度/价格/介绍/type=10）在 data/csv/Recipes.csv 中维护，
# 本文件只保存庆典特有的结算数据与行为逻辑，新增菜谱请改 CSV 而非本块。

FEAST_TYPE = 10
""" 庆典料理的菜谱类型id """
FEAST_TAB_NAME = _("庆典")
""" 烹饪面板庆典页签名 """

FEAST_DATA_BY_CID = {
    9001: {"effect": "home", "mult": 1.0},
    9002: {"effect": "reunion", "mult": 1.0},
    9003: {"effect": "hearty", "mult": 1.0},
    9004: {"effect": "melody", "mult": 1.0},
    9005: {"effect": "starlight", "mult": 1.0},
    9006: {"effect": "sakura", "mult": 1.0},
    9007: {"effect": "family", "mult": 1.0},
    9008: {"effect": "tea", "mult": 1.0},
    9009: {"effect": "golden", "mult": 1.25},
    9010: {"effect": "anniversary", "mult": 1.5},
}
""" 庆典料理特有数据：effect 为会食附加效果名（＝这道菜自带的固定特技），mult 为进食基础效果倍率 """

FEAST_EFFECT_TEXT = {
    "base": (_("无"), _("无额外效果")),
    "home": (_("家常"), _("入席者疲劳 −10；对你的好感与信赖 +15%")),
    "reunion": (_("团圆"), _("入席者疲劳 −50、怒气清零、解除对你的生气")),
    "hearty": (_("饱足"), _("入席者疲劳 −30")),
    "melody": (_("安眠曲"), _("入席者欲望 −30")),
    "starlight": (_("星光助兴"), _("入席者疲劳 −20，且更兴奋")),
    "sakura": (_("花见之情"), _("入席者对你的好感 +25%")),
    "family": (_("家规约束"), _("你亲手做的这桌：信赖 +50%")),
    "tea": (_("清茶淡点"), _("轻食：入席者不易吃饱（饥饿值只降到一半），可以接着吃")),
    "golden": (_("黄金满席"), _("进食收益 ×1.25")),
    "anniversary": (_("周年同庆"), _("进食收益 ×1.5")),
}
""" 会食效果（＝庆典料理的固定特技）的名字与效果说明：菜自带、不随熟练度、不入档 """


def get_feast_effect_text(food_cid) -> str:
    """
    获取某道庆典料理自带的固定效果文案（非庆典或无效 effect 时为空字符串）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    str -- 「名字：说明」；无则空字符串
    """
    data = FEAST_DATA_BY_CID.get(_fid(food_cid))
    if not data:
        return ""
    name, desc = FEAST_EFFECT_TEXT.get(data["effect"], (_("无"), _("无额外效果")))
    return _("{0}：{1}").format(name, desc)


def _get_feast_npcs() -> list:
    """
    获取当前与博士同场景、清醒且状态正常的干员名单
    Return arguments:
    list -- 干员角色id列表（不含博士）
    """
    pl = cache.character_data[0]
    eaters = []
    try:
        from Script.Design import map_handle
        scene_ids = map_handle.get_chara_now_scene_all_chara_id_list(0)
    except Exception:
        return []
    for cid in scene_ids:
        if cid == 0 or cid not in cache.character_data:
            continue
        cd = cache.character_data[cid]
        if getattr(cd, "dead", False):
            continue
        if handle_premise.handle_action_sleep(cid):
            continue
        if not handle_premise.handle_normal_6(cid):
            continue
        if handle_premise.handle_unconscious_flag_ge_1(cid):
            continue
        eaters.append(cid)
    return eaters


def get_feast_eater_count(include_player: bool = False) -> int:
    """
    获取一场会食的参与人数
    Keyword arguments:
    include_player -- 是否把博士计入，默认为False
    Return arguments:
    int -- 参与人数
    """
    n = len(_get_feast_npcs())
    if include_player:
        n += 1
    return n


# ================= 烹饪辅助（大师/收藏/熟练度） =================

MASTER_ABILITY_REQUIRE = 8
""" 大师模式解锁门槛：料理技能达到绝珍品质所需等级 """
MAX_FAVORITES_TOTAL = 100
""" 总收藏方案上限 """
MAX_FAVORITES_PER_RECIPE = 9
""" 单个菜谱收藏方案上限（每行3个，3行共9个） """
FAVORITES_ATTR = "recipe_favorites"
""" 收藏制作方案的玩家属性名 """
# 熟练度只影响本菜耗时与「自选特技槽」，**不提供任何品质加成**；
# 品质只由料理技能（≤美味）、精细答题（≤绝珍）、大师模式（绝珍）三者决定。
# 9 级梯级（与 attr_calculation.judge_grade 的 9 档评级一致）：G 初见 … EX 本命
PROF_TIER_COUNTS = [3, 6, 10, 16, 25, 40, 60, 90]
""" 熟练度各阶门槛（累计制作次数；8 个阈值 → 0–8 共 9 档） """
PROF_TIER_NAMES = [_("初见"), _("眼熟"), _("上手"), _("熟练"), _("娴熟"), _("拿手"), _("看家"), _("独门"), _("本命")]
""" 熟练度各阶名称（关系轴：我与这道菜的关系，不是人的头衔） """
PROF_TIER_LETTERS = ["G", "F", "E", "D", "C", "B", "A", "S", "EX"]
""" 熟练度各阶字母（复用 attr_calculation.judge_grade 的 9 档评级与配色） """
PROF_TIER_PAYOFF = {
    1: _("本菜耗时-5%"),
    2: _("特技池预览"),
    3: _("本菜耗时-10%"),
    4: _("本菜耗时-15%"),
    5: _("解锁自选特技槽"),
    6: _("本菜耗时-20%"),
    7: _("本菜耗时-30%"),
    8: _("已装特技效果×1.5"),
}
""" 各阶收益（用于确认页「距下一阶」提示） """
PROF_TIME_MULT_STEPS = [(1, 0.95), (3, 0.90), (4, 0.85), (6, 0.80), (7, 0.70)]
""" 本菜耗时倍率：按当前阶取最高档、不叠加 """
PROF_PREVIEW_TIER = 2
""" 特技池预览阶（E 上手，累计 6 次）：只读展示 4 条候选，还不能选 """
PROF_SLOT_TIER = 5
""" 自选特技槽解锁阶（B 拿手，累计 25 次） """
PROF_EX_TIER = 8
""" 顶阶 EX（累计 90 次） """
PROF_EX_UPGRADE = 1.5
""" EX 阶对已装自选特技的数值加成（升级已装效果，不新增效果） """
PROF_GAIN_PER_MAKE = 1
""" 每次成功制作一道菜获得的熟练度（不论本次份数，与上游"经验按单次行为结算"的惯例一致） """
PROFICIENCY_ATTR = "recipe_proficiency"
""" 菜谱熟练度的玩家属性名 """
SPECIAL_EFFECTS_ATTR = "recipe_special"
""" 菜谱自选特技的玩家属性名（Dict[菜谱id, 候选名]，每菜最多 1 个；庆典的固定效果不入档） """
MASKED_REJECT_MULT = 0.35
""" 「掩味」对"被喂特殊调味、判定失败"时反感增量的折扣（药剂类，调味 ≥100） """
MASKED_REJECT_MULT_EX = 0.20
""" 同上，EX 阶 """
MASKED_REJECT_MULT_SEMEN = 0.15
""" 「掩味」对精液类调味（11 巧妙混入 / 12 不作掩饰）的折扣：压不住多少，仍保留反发刻印压力 """
MASKED_REJECT_MULT_SEMEN_EX = 0.08
""" 同上，EX 阶：实测连续 4 次喂食也涨不到反发刻印 1 级（第 6 次才到） """
SEMEN_SEASONING_SET = (11, 12)
""" 精液类特殊调味：11 射入精液（巧妙混入）/ 12 射入精液（不作掩饰直接射上去） """
CHEER_MIN_DEDUCT = 1500
""" 「抚慰」型自选特技的最低扣除量：扣除 = max(当前值 × 比例, 本值)，**不设上限**
数值依据（真实存档状态存量 + 结算公式复算）：
一次重度单体事件（苦痛·大量）≈1060、常规反感事件 ≈65；一天按 3–4 顿计，
下限 1500 ⇒ 一顿 ≥ 一次重度事件量级，一天 4 顿 ≈6000 < 一次反感重击（≈10560） """


def is_master_unlocked() -> bool:
    """
    大师模式是否解锁（料理技能达到门槛或调试模式）
    Return arguments:
    bool -- 是否解锁
    """
    pl = cache.character_data[0]
    return pl.ability[43] >= MASTER_ABILITY_REQUIRE or cache.debug_mode


def _fid(food_cid) -> int:
    """
    把可能为字符串的菜谱id统一转为 int
    Keyword arguments:
    food_cid -- 菜谱id（int或str）
    Return arguments:
    int -- 规范化后的菜谱id
    """
    try:
        return int(food_cid)
    except (TypeError, ValueError):
        return int(0)


def get_favorites() -> dict:
    """
    获取玩家收藏制作方案字典
    Return arguments:
    dict -- 键为菜谱id，值为方案列表
    """
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return {}
    data = getattr(ri, FAVORITES_ATTR, None)
    if data is None:
        data = {}
        setattr(ri, FAVORITES_ATTR, data)
    return data


def get_recipe_favorites(food_cid) -> list:
    """
    获取某菜谱的收藏方案列表
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    list -- 方案字典列表
    """
    return get_favorites().get(_fid(food_cid), [])


def save_favorite(food_cid, make_count, cook_mode, special_seasoning) -> str:
    """
    收藏当前制作方案，同状态去重
    Keyword arguments:
    food_cid -- 菜谱id
    make_count -- 制作数量
    cook_mode -- 烹饪模式
    special_seasoning -- 调味cid
    Return arguments:
    str -- added/updated/per_recipe_limit/total_limit/invalid
    """
    fid = _fid(food_cid)
    if fid not in game_config.config_recipes and fid not in cache.recipe_data:
        return "invalid"
    favorites = get_favorites()
    presets = favorites.setdefault(fid, [])
    for idx, preset in enumerate(presets):
        if (preset.get("seasoning") == special_seasoning
                and preset.get("cook_mode") == cook_mode
                and preset.get("make_count") == make_count):
            presets[idx] = {
                "seasoning": special_seasoning,
                "cook_mode": cook_mode,
                "make_count": make_count,
            }
            return "updated"
    if len(presets) >= MAX_FAVORITES_PER_RECIPE:
        return "per_recipe_limit"
    if sum(len(v) for v in favorites.values()) >= MAX_FAVORITES_TOTAL:
        return "total_limit"
    presets.append({
        "seasoning": special_seasoning,
        "cook_mode": cook_mode,
        "make_count": make_count,
    })
    return "added"


def remove_favorite(food_cid, index: int) -> bool:
    """
    删除某菜谱的第 index 个收藏方案
    Keyword arguments:
    food_cid -- 菜谱id
    index -- 方案序号
    Return arguments:
    bool -- 是否删除成功
    """
    fid = _fid(food_cid)
    favorites = get_favorites()
    presets = favorites.get(fid)
    if presets is None or index < 0 or index >= len(presets):
        return False
    del presets[index]
    if not presets:
        del favorites[fid]
    return True


def has_favorites(food_cid) -> bool:
    """
    某菜谱是否已有收藏方案
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    bool -- 是否存在收藏
    """
    return bool(get_recipe_favorites(food_cid))


def get_favorite_recipe_ids() -> list:
    """
    返回有收藏的菜谱id列表
    Return arguments:
    list -- 按id排序的菜谱id列表
    """
    return sorted(get_favorites().keys())


def find_favorite_index(food_cid, seasoning, cook_mode, make_count) -> int:
    """
    查找与给定状态一致的收藏方案序号
    Keyword arguments:
    food_cid -- 菜谱id
    seasoning -- 调味cid
    cook_mode -- 烹饪模式
    make_count -- 制作数量
    Return arguments:
    int -- 方案序号，未找到返回-1
    """
    presets = get_recipe_favorites(food_cid)
    for idx, preset in enumerate(presets):
        if (preset.get("seasoning") == seasoning
                and preset.get("cook_mode") == cook_mode
                and preset.get("make_count") == make_count):
            return idx
    return -1


def get_prof_count(food_cid: int) -> int:
    """
    获取某菜谱的累计制作次数
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    int -- 制作次数
    """
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return 0
    return getattr(ri, PROFICIENCY_ATTR, {}).get(_fid(food_cid), 0)


def get_prof_tier(food_cid: int) -> int:
    """
    获取某菜谱的熟练度阶（0 初见 ~ 8 本命，字母 G–EX）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    int -- 熟练度阶
    """
    count = get_prof_count(food_cid)
    for tier, threshold in enumerate(PROF_TIER_COUNTS):
        if count < threshold:
            return tier
    return len(PROF_TIER_COUNTS)


def add_proficiency(food_cid: int) -> None:
    """
    制作完成后累计熟练度，跨入宗师时赋予该菜谱配置的特技
    Keyword arguments:
    food_cid -- 菜谱id
    """
    ri = cache.rhodes_island
    data = getattr(ri, PROFICIENCY_ATTR, None)
    if data is None:
        data = {}
        setattr(ri, PROFICIENCY_ATTR, data)
    fid = _fid(food_cid)
    old_tier = get_prof_tier(fid)
    # 熟练度按"制作一次"结算，不随份数倍增（批量制作不再一次拉满）
    data[fid] = data.get(fid, 0) + PROF_GAIN_PER_MAKE
    # 自选特技由玩家自己在确认页选择（见 set_dish_special_choice），跨阶不再自动写档


def get_prof_time_mult(food_cid: int) -> float:
    """
    获取熟练度提供的耗时倍率（按当前阶取最高档、不叠加；小于1为缩短）
    若本菜已装「耗时」型自选特技，再乘一份（EX 阶为 ×1.5 升级后的数值）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    float -- 耗时倍率
    """
    tier = get_prof_tier(food_cid)
    mult = 1.0
    for min_tier, step_mult in PROF_TIME_MULT_STEPS:
        if tier >= min_tier:
            mult = step_mult
    if tier >= PROF_SLOT_TIER and get_dish_special_dim(food_cid) == "耗时":
        mult *= 0.85 if is_dish_special_ex(food_cid) else 0.90
    return mult


def get_food_special(food) -> tuple:
    """
    取「某一份食物」自己带的特技候选元组（食物实例在制作时就定下了名字，之后换槽不影响已有成品）

    Keyword arguments:
    food -- Food 实例（可为 None）
    Return arguments:
    tuple -- (候选名, 维度, 基础效果, EX 效果)；没选时为 ()
    """
    if food is None:
        return ()
    name = getattr(food, "dish_special", "") or ""
    recipe_id = getattr(food, "recipe", -1)
    if not name:
        # 老存档的食物没有该字段，回落到"菜谱当前选择"（与改动前行为一致）
        return get_dish_special(recipe_id)
    for item in get_dish_special_candidates(recipe_id):
        if item[0] == name:
            return item
    return ()


def get_food_special_choice(food) -> str:
    """ 取某一份食物上的自选特技名（可能为空字符串） """
    item = get_food_special(food)
    return item[0] if item else ""


def get_food_special_dim(food) -> str:
    """ 取某一份食物上的自选特技维度（可能为空字符串） """
    item = get_food_special(food)
    return item[1] if item else ""


def food_special_effect_text(food) -> str:
    """ 取某一份食物上的自选特技效果文案（EX 阶取升级后的数值） """
    item = get_food_special(food)
    if not item:
        return ""
    return item[3] if is_dish_special_ex(getattr(food, "recipe", -1)) else item[2]


def get_dish_special_candidates(food_cid) -> list:
    """
    获取某道菜的自选特技候选（每菜 4 条，维度互不重复）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    list -- [(候选名, 效果维度, 基础效果, EX 升级后效果), ...]；无候选时为空列表
    """
    fid = _fid(food_cid)
    out = []
    for slot in range(1, 5):
        row = game_config.config_dish_special.get(fid * 10 + slot)
        if row is None:
            continue
        out.append((row.name, row.dim, row.base, row.ex))
    return out


def get_dish_special_choice(food_cid) -> str:
    """
    获取玩家为这道菜选定的自选特技名（未选择或已失效时为空字符串）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    str -- 候选名
    """
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return ""
    name = getattr(ri, SPECIAL_EFFECTS_ATTR, {}).get(_fid(food_cid), "")
    names = [c[0] for c in get_dish_special_candidates(food_cid)]
    return name if name in names else ""


def set_dish_special_choice(food_cid, name: str) -> None:
    """
    设定/取消这道菜的自选特技（name 传空字符串表示取消）
    Keyword arguments:
    food_cid -- 菜谱id
    name -- 候选名（必须在该菜候选表内，否则视为取消）
    """
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return
    data = getattr(ri, SPECIAL_EFFECTS_ATTR, None)
    if data is None:
        data = {}
        setattr(ri, SPECIAL_EFFECTS_ATTR, data)
    fid = _fid(food_cid)
    names = [c[0] for c in get_dish_special_candidates(fid)]
    if name in names:
        data[fid] = name
    else:
        data.pop(fid, None)


def get_dish_special(food_cid) -> tuple:
    """
    获取已装自选特技的完整条目
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    tuple -- (候选名, 效果维度, 基础效果, EX 升级后效果)；未装时返回空元组
    """
    name = get_dish_special_choice(food_cid)
    if not name:
        return ()
    for item in get_dish_special_candidates(food_cid):
        if item[0] == name:
            return item
    return ()


def get_dish_special_dim(food_cid) -> str:
    """
    获取已装自选特技的效果维度（未装时为空字符串）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    str -- 效果维度
    """
    item = get_dish_special(food_cid)
    return item[1] if item else ""


def is_dish_special_ex(food_cid) -> bool:
    """
    这道菜是否已达 EX 阶（已装自选特技的数值按 PROF_EX_UPGRADE 升级）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    bool -- 是否升级
    """
    return get_prof_tier(food_cid) >= PROF_EX_TIER


def dish_special_effect_text(food_cid) -> str:
    """
    已装自选特技的效果文案（EX 阶自动取升级后的数值）
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    str -- 效果说明
    """
    item = get_dish_special(food_cid)
    if not item:
        return ""
    return item[3] if is_dish_special_ex(food_cid) else item[2]


def get_helpers() -> list:
    """
    获取当前可协助烹饪的帮厨名单
    优先使用玩家名单制助理（multi_assistant 风格），无名单时退回原版单助理；
    只取智能跟随(1)且与博士同场景者，最多3名。
    Return arguments:
    list -- 帮厨角色id列表
    """
    pl = cache.character_data[0]
    ids = getattr(pl, "mod_assistant_ids", None)
    if ids is None:
        ids = [pl.assistant_character_id] if pl.assistant_character_id else []
    helpers = []
    try:
        from Script.Design import map_handle as _mh
        pl_scene = _mh.get_map_system_path_str_for_list(pl.position)
        for aid in ids:
            if aid == 0 or aid not in cache.character_data:
                continue
            a = cache.character_data[aid]
            if a.sp_flag.is_follow != 1:
                continue
            if _mh.get_map_system_path_str_for_list(a.position) != pl_scene:
                continue
            helpers.append(aid)
            if len(helpers) >= 3:
                break
    except Exception:
        return []
    return helpers


def get_helper_time_mult() -> float:
    """
    获取帮厨耗时系数：每名-10%，最多3名
    Return arguments:
    float -- 耗时倍率（小于1为缩短）
    """
    return 1.0 - 0.1 * len(get_helpers())


def prof_summary_text(food_cid: int) -> str:
    """
    生成确认页的熟练度摘要文本
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    str -- 摘要文本
    """
    count = get_prof_count(food_cid)
    tier = get_prof_tier(food_cid)
    text = _("熟练度: {0} {1}（累计{2}次）").format(PROF_TIER_LETTERS[tier], PROF_TIER_NAMES[tier], count)
    # 当前已经拿到的收益（不能只显示"下一阶给什么"）
    _now = []
    _steps = [s for s in PROF_TIME_MULT_STEPS if tier >= s[0]]
    if _steps:
        _now.append(_("本菜耗时 -{0}%").format(int(round((1 - _steps[-1][1]) * 100))))
    if tier >= PROF_SLOT_TIER:
        _now.append(_("自选特技槽已解锁"))
    if tier >= PROF_EX_TIER:
        _now.append(_("已装特技效果 ×{0}").format(PROF_EX_UPGRADE))
    if _now:
        text += _("｜当前：{0}").format("、".join(_now))
    if tier < len(PROF_TIER_COUNTS):
        next_tier = tier + 1
        need = max(0, PROF_TIER_COUNTS[tier] - count)
        text += _("｜距 {0} {1} 还差 {2} 次：{3}").format(
            PROF_TIER_LETTERS[next_tier], PROF_TIER_NAMES[next_tier], need, PROF_TIER_PAYOFF[next_tier]
        )
    else:
        text += _("｜已至顶阶")
    return text


def dish_special_summary_text(food_cid) -> str:
    """
    生成确认页的「本菜自选特技」摘要行
    Keyword arguments:
    food_cid -- 菜谱id
    Return arguments:
    str -- 摘要文本（无可选特技时为空字符串）
    """
    candidates = get_dish_special_candidates(food_cid)
    if not candidates:
        return ""
    tier = get_prof_tier(food_cid)
    if tier < PROF_SLOT_TIER:
        return _("本菜特技: 未解锁（累计 {0} 次 / {1} {2} 解锁 4 选 1）").format(
            PROF_TIER_COUNTS[PROF_SLOT_TIER - 1], PROF_TIER_LETTERS[PROF_SLOT_TIER], PROF_TIER_NAMES[PROF_SLOT_TIER]
        )
    item = get_dish_special(food_cid)
    if not item:
        return _("本菜特技: 未选择（4 选 1）")
    ex_text = _("｜EX 已升级") if is_dish_special_ex(food_cid) else ""
    return _("本菜特技: {0}（{1}，{2}）{3}").format(item[0], item[1], dish_special_effect_text(food_cid), ex_text)
