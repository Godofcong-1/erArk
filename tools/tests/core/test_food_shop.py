# -*- coding: UTF-8 -*-
"""食物商店与食物背包：食堂/餐馆/地摊的识别与购买不变式（博士免费）、购买期间商店刷新后继续购买、地摊或餐馆被买光的提示与错字、背包清理菜谱已不存在的食物"""
from _bootstrap import *  # noqa: F401,F403
from Script.Design import basement
from Script.System.Cooking_System import cooking, food_bag_panel
from Script.UI.Panel import food_shop_panel

# ==== 0. fixture：新档罗德岛数据、运行时菜谱表、三类食物商店场景 ====
cache.rhodes_island = basement.get_base_zero()
cooking.init_recipes()
W = food_shop_panel.window_width
""" 面板宽度 """
DINING = ["生娱", "食堂"]
""" 食堂（场景 tag 只有 Dining_hall，按「既非地摊也非餐馆」归为食堂） """
EATERY = ["贸易", "龙门食坊"]
""" 餐馆：龙门食坊 """
STALL = ["贸易", "地摊小贩"]
""" 地摊小贩 """
EATERY_ID = next(rid for rid, data in game_config.config_restaurant.items() if data.tag_name == "Lungmen_Eatery")
""" 龙门食坊的餐馆id """
EMPTY_TIP = _("\n该商店已经没有可购买的食物了，请明天再来\n")
""" 商店被买光时的提示 """
DINING_RECIPES = sorted(rid for rid, data in cache.recipe_data.items() if data.type == 5)[:3]
""" 食堂卖的预制食物菜谱 """
EATERY_RECIPES = sorted(rid for rid, data in game_config.config_recipes.items() if data.restaurant == EATERY_ID and data.difficulty != 999 and data.type not in {4, 5, 8, 9})[:3]
""" 龙门食坊自己的菜谱 """
STALL_RECIPES = sorted(rid for rid, data in game_config.config_recipes.items() if data.type in {1, 2})[:2]
""" 地摊卖的零食/饮料菜谱 """
assert len(DINING_RECIPES) == 3 and len(EATERY_RECIPES) == 3 and len(STALL_RECIPES) == 2
D1, D2, D3 = DINING_RECIPES
R1, R2, R3 = EATERY_RECIPES
S1, S2 = STALL_RECIPES


def new_food(recipe_id: int, quality: int = 5, maker: str = "") -> game_type.Food:
    """
    按菜谱造一份食物
    Keyword arguments:
    recipe_id -- 菜谱id
    quality -- 品质
    maker -- 制作者
    Return arguments:
    game_type.Food -- 食物对象
    """
    return cooking.create_food("", recipe_id, quality, maker)


def shelf(*recipe_counts) -> dict:
    """
    造一份商店货架数据 {菜谱id字符串: {uid: 食物}}，与 init_food_shop_data 的结构一致
    Keyword arguments:
    recipe_counts -- 若干 (菜谱id, 份数)
    Return arguments:
    dict -- 货架数据
    """
    data = {}
    for recipe_id, count in recipe_counts:
        data[str(recipe_id)] = {}
        for _index in range(count):
            food = new_food(recipe_id)
            data[str(recipe_id)][food.uid] = food
    return data


# ==== 1. 时间推进打桩：购买会调 update.game_update_flow 进真实主循环，换成记录 + 可选的「商店刷新」钩子 ====
update_calls = []
""" game_update_flow 的调用参数记录 """
refresh_hooks = []
""" 依次在每次时间推进时执行的商店刷新函数（模拟期间跨日或 NPC 补货） """


def fake_update_flow(add_time: int):
    """
    game_update_flow 的桩：记录推进的分钟数，并执行下一个排队的刷新钩子
    Keyword arguments:
    add_time -- 推进的分钟数
    Return arguments:
    无
    """
    update_calls.append(add_time)
    if refresh_hooks:
        refresh_hooks.pop(0)()


food_shop_panel.update.game_update_flow = fake_update_flow

# ==== 2. 按钮可点：用 headless_base 的可点击按钮桩与脚本化 askfor_all（plan / ask_log / missed / button_map 见该文件） ====
enable_clickable_buttons()
_base_run_panel = run_panel
""" headless_base 的 run_panel，下面的同名函数在它外面再清理本文件的记录 """


def run_panel(func, choices: list):
    """
    清空记录后按选择序列跑一段面板流程，异常不外抛而是返回给调用方做断言
    Keyword arguments:
    func -- 无参的面板入口
    choices -- 选择序列
    Return arguments:
    Exception | None -- 流程中抛出的异常
    """
    update_calls.clear()
    try:
        return _base_run_panel(func, choices)
    finally:
        refresh_hooks.clear()


def pick_food(recipe_id: int):
    """
    选择谓词：商店首页里该菜谱的食物名按钮
    Keyword arguments:
    recipe_id -- 菜谱id
    Return arguments:
    function -- 谓词
    """

    def want(option) -> bool:
        """
        该选项是否绑定到这个菜谱的「查看食物列表」
        Keyword arguments:
        option -- 选项返回值
        Return arguments:
        bool -- 是否命中
        """
        bound = button_map.get(option)
        owner = getattr(bound[0], "__self__", None) if bound else None
        return getattr(owner, "cid", None) == str(recipe_id)

    return want


def pick_buy(recipe_id: int):
    """
    选择谓词：食物列表里该菜谱的任一[购买]按钮（返回值为「菜谱id_uid前三位」）
    Keyword arguments:
    recipe_id -- 菜谱id
    Return arguments:
    function -- 谓词
    """
    return lambda option: str(option).startswith(f"{recipe_id}_")


def offered(index: int) -> set:
    """
    第 index 次 askfor_all 时商店首页列出的菜谱id集合（越界返回空集）
    Keyword arguments:
    index -- 第几次询问，从 0 开始
    Return arguments:
    set -- 菜谱id字符串集合
    """
    if index >= len(ask_log):
        return set()
    result = set()
    for func, _arg in ask_log[index][2].values():
        if getattr(func, "__name__", "") == "see_food_shop_food_list":
            result.add(func.__self__.cid)
    return result


def bag_recipes() -> list:
    """
    玩家背包里各食物的菜谱id（排序）
    Keyword arguments:
    无
    Return arguments:
    list -- 菜谱id列表
    """
    return sorted(food.recipe for food in pl.food_bag.values())


def open_shop():
    """
    按真实入口打开当前场景的食物商店面板
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache.now_panel_id = constant.Panel.FOOD_SHOP
    food_shop_panel.FoodShopPanel(W).draw()


# ==== 3. 商店识别 ====
section("按场景识别食物商店")
move_to(0, DINING)
check("食堂场景 → 食堂（None）", food_shop_panel.get_now_food_shop_id() is None)
move_to(0, EATERY)
check("餐馆场景 → 对应餐馆id", food_shop_panel.get_now_food_shop_id() == EATERY_ID)
move_to(0, STALL)
check("地摊场景 → Stall_Vendor", food_shop_panel.get_now_food_shop_id() == "Stall_Vendor")
cache.rhodes_island.restaurant_data.pop(EATERY_ID, None)
check("还没进货的餐馆取到空货架而不是报错", food_shop_panel.get_food_shop_data(EATERY_ID) == {})

# ==== 4. 食堂购买 ====
section("食堂购买：食物进背包、货架减一、博士免费")
move_to(0, DINING)
cache.rhodes_island.dining_hall_data = shelf((D1, 2), (D2, 1))
cache.rhodes_island.materials_resouce[1] = 12345
pl.food_bag = {}
err = run_panel(open_shop, [pick_food(D1), pick_buy(D1)])
check("面板流程不报错", err is None, repr(err))
check("首页列出食堂的两种食物", offered(0) == {str(D1), str(D2)}, offered(0))
check("没有选不到的按钮", not missed, missed)
check("买到一份：背包里多了这份食物", bag_recipes() == [D1], bag_recipes())
bought = next(iter(pl.food_bag.values()), None)
check("货架上该菜谱减一、另一种不变", len(cache.rhodes_island.dining_hall_data[str(D1)]) == 1 and len(cache.rhodes_island.dining_hall_data[str(D2)]) == 1)
check("买走的那份已不在货架上", bought is not None and bought.uid not in cache.rhodes_island.dining_hall_data[str(D1)])
check("博士免费：龙门币不变，按钮上标明（博士免费）", cache.rhodes_island.materials_resouce[1] == 12345 and any(_("(博士免费)") in text for text in drawn_text))
check("购买行为：BUY_FOOD、时长 1、目标食物为买到的那份", pl.behavior.behavior_id == constant.Behavior.BUY_FOOD and pl.state == constant.CharacterStatus.STATUS_BUY_FOOD
      and pl.behavior.duration == 1 and pl.behavior.target_food is bought)
check("购买推进 1 分钟时间（且只推进一次）", update_calls == [1], update_calls)
check("买完回到首页仍列出剩余食物，[返回]后回到场景", offered(2) == {str(D1), str(D2)} and cache.now_panel_id == constant.Panel.IN_SCENE, offered(2))

section("自制食物放进食堂")
seasoned = new_food(D2, maker="博士")
seasoned.special_seasoning = 11
plain = new_food(D2, maker="博士")
pl.food_bag = {seasoned.uid: seasoned, plain.uid: plain}
food_shop_panel.put_selfmade_food_in()
check("正常调味的食物放进食堂对应菜谱下", plain.uid in cache.rhodes_island.dining_hall_data[str(D2)] and plain.uid not in pl.food_bag)
check("特殊调味的食物留在背包", seasoned.uid in pl.food_bag and seasoned.uid not in cache.rhodes_island.dining_hall_data[str(D2)])

# ==== 5. 购买期间商店刷新 ====
section("餐馆购买期间重新进货，继续购买不报错")
move_to(0, EATERY)
cache.rhodes_island.restaurant_data[EATERY_ID] = shelf((R1, 2), (R2, 1))
pl.food_bag = {}


def restock_eatery():
    """
    刷新钩子：龙门食坊重新进货，换成只有另一种菜谱的货架（与 init_food_shop_data 一样整体替换）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache.rhodes_island.restaurant_data[EATERY_ID] = shelf((R3, 1))


refresh_hooks[:] = [restock_eatery]
err = run_panel(open_shop, [pick_food(R1), pick_buy(R1), pick_food(R3), pick_buy(R3)])
check("刷新后继续购买不报错（5e17eae46）", err is None, repr(err))
check("刷新后的首页只列新进的货，不再列已不存在的菜谱", offered(2) == {str(R3)}, offered(2))
check("刷新前后各买到一份", bag_recipes() == sorted([R1, R3]), bag_recipes())
check("新货被买光后提示已无可购买的食物并退出", EMPTY_TIP in drawn_text and len(ask_log) == 4 and cache.now_panel_id == constant.Panel.IN_SCENE, len(ask_log))

section("食堂购买期间跨日刷新，继续购买不报错")
move_to(0, DINING)
cache.rhodes_island.dining_hall_data = shelf((D1, 1), (D2, 1))
pl.food_bag = {}


def new_day_dining_hall():
    """
    刷新钩子：跨日后食堂数据整体换新（init_food_shop_data(new_day_flag=True) 先置空字典再补货）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache.rhodes_island.dining_hall_data = shelf((D3, 2))


refresh_hooks[:] = [new_day_dining_hall]
err = run_panel(open_shop, [pick_food(D1), pick_buy(D1), pick_food(D3), pick_buy(D3)])
check("跨日刷新后继续购买不报错（5e17eae46）", err is None, repr(err))
check("跨日后的首页只列新一天的食物", offered(2) == {str(D3)}, offered(2))
check("跨日前后各买到一份，新货架减一", bag_recipes() == sorted([D1, D3]) and len(cache.rhodes_island.dining_hall_data[str(D3)]) == 1, bag_recipes())

# ==== 6. 被买光 ====
section("地摊被买光时提示而不报错（ab50df9b8）")
move_to(0, STALL)
cache.rhodes_island.stall_vendor_data[0] = {str(S1): {}, str(S2): {}}
cache.rhodes_island.dining_hall_data = shelf((D1, 2))
err = run_panel(open_shop, [])
check("打开已被买光的地摊不报错", err is None, repr(err))
check("提示已经没有可购买的食物，直接退回场景", EMPTY_TIP in drawn_text and not ask_log and cache.now_panel_id == constant.Panel.IN_SCENE, len(ask_log))
check("没有把食堂的食物当成地摊的货列出来", not any(offered(index) for index in range(len(ask_log))))
empty_tip_texts = [text for text in drawn_text if "没有" in text and "食物" in text]
check("买光提示文本没有错字「没有没有」（d117462df）", empty_tip_texts == [EMPTY_TIP], empty_tip_texts)
cache.rhodes_island.stall_vendor_data[0] = shelf((S1, 1))
pl.food_bag = {}
err = run_panel(open_shop, [pick_food(S1), pick_buy(S1)])
check("买走地摊最后一份后不报错", err is None, repr(err))
check("最后一份进了背包、地摊清空", bag_recipes() == [S1] and not cache.rhodes_island.stall_vendor_data[0][str(S1)], bag_recipes())
check("继续停留时提示已经没有可购买的食物并退出", EMPTY_TIP in drawn_text and len(ask_log) == 2 and cache.now_panel_id == constant.Panel.IN_SCENE, len(ask_log))

section("餐馆被买光时同样提示")
move_to(0, EATERY)
cache.rhodes_island.restaurant_data[EATERY_ID] = {str(R1): {}}
err = run_panel(open_shop, [])
check("打开已被买光的餐馆不报错并提示", err is None and EMPTY_TIP in drawn_text and not ask_log, repr(err))

# ==== 7. 进货 ====
section("进货：货架内容与刷新范围（init_food_shop_data）")
saved_npc_id_got = cache.npc_id_got
cache.npc_id_got = set(range(1, 13))  # 进货份数按在岛干员人数算（只读 len），12 人
cooking.init_food_shop_data(new_day_flag=True)
rhodes = cache.rhodes_island


def shelf_foods(shelf_data: dict) -> list:
    """
    展开货架为 (菜谱id字符串, uid, 食物) 列表
    Keyword arguments:
    shelf_data -- 货架数据
    Return arguments:
    list -- 展开后的列表
    """
    return [(key, uid, food) for key, foods in shelf_data.items() for uid, food in foods.items()]


def shelf_consistent(shelf_data: dict) -> bool:
    """
    货架结构是否自洽：键是食物菜谱id的字符串、uid 键与食物 uid 一致
    Keyword arguments:
    shelf_data -- 货架数据
    Return arguments:
    bool -- 是否自洽
    """
    return all(key == str(food.recipe) and uid == food.uid for key, uid, food in shelf_foods(shelf_data))


dining_foods = shelf_foods(rhodes.dining_hall_data)
check("新的一天：食堂进 人数×3 份，全是预制食物", len(dining_foods) == 36 and all(cache.recipe_data[food.recipe].type == 5 for _k, _u, food in dining_foods), len(dining_foods))
restaurant_ok = True
for restaurant_id in game_config.config_restaurant:
    foods = shelf_foods(rhodes.restaurant_data.get(restaurant_id, {}))
    recipes = [game_config.config_recipes[food.recipe] for _k, _u, food in foods]
    if len(foods) != 12 or not all(r.restaurant == restaurant_id and r.difficulty != 999 and r.type not in {4, 5, 8, 9} for r in recipes):
        restaurant_ok = False
check("新的一天：各餐馆各进 人数 份，只卖本店可做的菜", restaurant_ok)
stall_foods = shelf_foods(rhodes.stall_vendor_data[0])
check("新的一天：地摊最多 10 份，只卖零食与饮品", len(stall_foods) == 10 and all(cache.recipe_data[food.recipe].type in {1, 2} for _k, _u, food in stall_foods), len(stall_foods))
check("货架结构自洽（键 = 菜谱id字符串，uid 一致）", shelf_consistent(rhodes.dining_hall_data) and shelf_consistent(rhodes.stall_vendor_data[0])
      and all(shelf_consistent(data) for data in rhodes.restaurant_data.values()))
before_restaurants = dict(rhodes.restaurant_data)
before_dining = rhodes.dining_hall_data
before_stall = rhodes.stall_vendor_data[0]
cooking.init_food_shop_data(EATERY_ID)
check("单店补货（NPC 发现该餐馆空了）：只换这一家的货架",
      rhodes.restaurant_data[EATERY_ID] is not before_restaurants[EATERY_ID] and all(rhodes.restaurant_data[rid] is before_restaurants[rid] for rid in before_restaurants if rid != EATERY_ID))
check("单店补货：食堂与地摊不动", rhodes.dining_hall_data is before_dining and len(shelf_foods(before_dining)) == 36 and rhodes.stall_vendor_data[0] is before_stall)
before_restaurants = dict(rhodes.restaurant_data)
cooking.init_food_shop_data(-1)
check("食堂补货（NPC 发现食堂空了，-1）：在原货架上补 人数×3 份", rhodes.dining_hall_data is before_dining and len(shelf_foods(before_dining)) == 72 and rhodes.stall_vendor_data[0] is before_stall)
# 疑似 BUG：docstring 写「不是 -2 则仅刷新对应 id」，-1 在本模块里即食堂；但餐馆循环只在 id>=0 时跳过别家，-1 会把九家餐馆的货架全部清空重做
check("食堂补货（-1）不清空重做各餐馆的货架", all(rhodes.restaurant_data[rid] is before_restaurants[rid] for rid in before_restaurants),
      [rid for rid in before_restaurants if rhodes.restaurant_data[rid] is not before_restaurants[rid]])
cache.npc_id_got = saved_npc_id_got

# ==== 8. 食物背包 ====
section("食物背包清理菜谱已不存在的食物（da9301a68）")
move_to(0, DINING)
pl.target_character_id = 0
good = new_food(D1)
ghost = new_food(D2)
ghost.recipe = max(cache.recipe_data) + 1000  # 菜谱被移除 / 回退到旧版本后读到的食物
ghost.name = ""
legacy = new_food(D2)
del legacy.milk_ml  # 更早版本的食物没有 milk_ml 属性
pl.food_bag = {good.uid: good, ghost.uid: ghost, legacy.uid: legacy}
cache.now_panel_id = constant.Panel.FOOD_BAG
err = run_panel(food_bag_panel.FoodBagPanel(W).draw, [])
check("背包里有菜谱已不存在的食物时，打开食物背包不报错", err is None, repr(err))
check("菜谱已不存在的食物被自动清理", ghost.uid not in pl.food_bag)
check("缺字段的旧版本食物同样被清理", legacy.uid not in pl.food_bag)
check("正常食物保留", good.uid in pl.food_bag)
check("提示检测到异常食物并已删除", any("检测到因版本变更导致的食物数据异常" in text for text in drawn_text))
check("正常食物照常分组显示", any(cache.recipe_data[D1].name in text and "x1" in text for text in drawn_text))
check("[返回]后回到场景", cache.now_panel_id == constant.Panel.IN_SCENE)
group_normal, group_special = food_bag_panel.FoodBagPanel(W, _("食用")).get_food_group()
check("再次分组只剩正常食物", list(group_normal) == [(D1, 0)] and not group_special, (group_normal, group_special))

finish()
