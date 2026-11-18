# -*- coding: UTF-8 -*-
"""跨天与睡眠结算：新开局基地上的新一天结算全链与每日重置、资源上限、浮点库存的流水线与自动卖出、睡眠结算与自动存档钩子、持续一天以上的长行为结算"""
from _bootstrap import *  # noqa: F401,F403
import traceback

from Script.Design import basement
from Script.Settle import past_day_settle, realtime_settle, sleep_settle
from Script.System.Cooking_System import cooking
from Script.System.Medical_System import medical_service
from Script.UI.Flow import creator_character_flow
from Script.UI.Panel import resource_exchange_panel

random.seed(20260913)
_SAVE_DIR = os.path.join(ROOT, "save")
""" 仓库里的真实存档目录：本文件不该新建或改动它 """


def save_dir_state() -> list:
    """
    记录仓库存档目录的状态
    Keyword arguments:
    无
    Return arguments:
    list -- [(相对路径, 大小, 修改时间), ...]；目录不存在时为 None
    """
    if not os.path.isdir(_SAVE_DIR):
        return None
    result = []
    for dir_path, dir_name_list, file_name_list in os.walk(_SAVE_DIR):
        for name in dir_name_list + file_name_list:
            stat = os.stat(os.path.join(dir_path, name))
            result.append((os.path.relpath(os.path.join(dir_path, name), _SAVE_DIR), stat.st_size, stat.st_mtime_ns))
    return sorted(result)


SAVE_DIR_BEFORE = save_dir_state()
""" 跑测试前存档目录的状态 """

# ==== 桩：自动存档（本文件绝不写盘） ====
# sleep_settle.update_save 在函数内 `from Script.Core import save_handle` 后调 establish_save("auto")，取的是模块属性，
#    把它换成只记录参数的桩即可截住；write_save_data 换成直接报错的桩，万一有别的路径绕过 establish_save 写档，测试会当场失败
save_call_list = []
""" establish_save 桩收到的存档 id """


def _stub_establish_save(save_id: str):
    """
    自动存档桩：只记录存档 id，不写盘
    Keyword arguments:
    save_id -- 存档id
    Return arguments:
    无
    """
    save_call_list.append(save_id)


def _forbid_write_save_data(*args, **kwargs):
    """
    写档桩：本文件里任何写档都是错误
    Keyword arguments:
    args -- 任意参数
    kwargs -- 任意关键字参数
    Return arguments:
    无（总是抛出 AssertionError）
    """
    raise AssertionError("test_day_settle 不允许写存档")


save_handle.establish_save = _stub_establish_save
save_handle.write_save_data = _forbid_write_save_data

# ==== 1. 新开局的罗德岛 ====
section("新开局基地 fixture")
# 照 creator_character_flow 开新游戏的顺序初始化基地（不跑角色名单、宿舍分配等要完整干员名册的部分）
cache.rhodes_island = basement.get_base_zero()
creator_character_flow.first_bonus_and_setting_updata()
cooking.init_recipes()
cooking.init_food_shop_data(new_day_flag=True)
cache.country = attr_calculation.get_country_reset(cache.country)
basement.get_base_updata()
medical_service.init_medical_department_data(reset_runtime=True)
ri = cache.rhodes_island
check("开局基地：仓库容量、流水线 0、药田与温室线 0 都已建好", ri.warehouse_capacity > 0 and 0 in ri.assembly_line and 0 in ri.herb_garden_line and 0 in ri.green_house_line,
      (ri.warehouse_capacity, ri.assembly_line, ri.herb_garden_line, ri.green_house_line))

trader = make_character(101, "交易员", 111)
worker = make_character(102, "工人", 121)
farmer = make_character(103, "药田种植员", 161)
fallen = make_character(104, "陷落干员", 0)
fallen.talent[201] = 1  # 1 级陷落素质 → 周日提供 20 张粉红凭证
npc_list = [trader, worker, farmer, fallen]
DAIRY_TYPE = game_config.config_resouce[32].type
""" 母乳酸奶（32）所属的资源类型（乳制品） """

# ==== 2. 新一天结算：每日重置 ====
section("新一天结算（周日 00:05）：不抛异常，且每日重置都已发生")
set_time(datetime.datetime(2026, 9, 13, 0, 5))
cache.pre_game_time = datetime.datetime(2026, 9, 12, 23, 50)
check("fixture：新的一天是周日（周结算分支要跑到）", cache.game_time.weekday() == 6)
cache.today_taiggered_event_record = {"昨天触发的事件"}
cache.daily_intsruce = []
for one in npc_list:
    one.sp_flag.aromatherapy = 1
    one.sp_flag.find_food_weird = True
    one.sp_flag.swim = 1
    one.entertainment.entertainment_type = [0, 0, 0]
    one.ability[33] = 2
    one.desire_point = 0
pl.sp_flag.aromatherapy = 1
# 助理问候 flag 的清零规则：已问候过（2）或服务关闭时清零，服务开启且还没问候（1）的留着
trader.assistant_services[5] = 1
trader.sp_flag.morning_salutation = 2
trader.assistant_services[6] = 1
trader.sp_flag.night_salutation = 1
worker.assistant_services[5] = 1
worker.sp_flag.morning_salutation = 1
worker.assistant_services[6] = 0
worker.sp_flag.night_salutation = 1
# 玩家背包：品质 1 的食物当天过期丢弃，品质 8 的变质成 4，一份母乳（品质 8）先变质、再在母乳结算里折成鲜母乳
food_expire = game_type.Food()
food_expire.quality = 1
food_keep = game_type.Food()
food_keep.quality = 8
food_milk = game_type.Food()
food_milk.quality = 8
food_milk.milk_ml = 20
pl.food_bag = {food_expire.uid: food_expire, food_keep.uid: food_keep, food_milk.uid: food_milk}
# 基地的每日结算输入
ri.materials_resouce[12] = 0
ri.materials_resouce[31] = 0
ri.total_semen_count = 120
ri.milk_in_fridge = {fallen.cid: 30}
ri.total_favorability_increased = 350
ri.week_fall_chara_pink_certificate_add = 0
pink_before = ri.materials_resouce[4]
ri.today_trade_resource_count[11] = 99
ri.assembly_line[0][4] = 20
ri.remaining_aromatherapy_sessions_today = 0
# 主交易员的有效性：101 是交易员，留着；102 是工人，挂在乳制品上应被撤掉
ri.resource_type_main_trader[game_config.config_resouce[11].type] = trader.cid
ri.resource_type_main_trader[DAIRY_TYPE] = worker.cid
ri.party_day_of_week[cache.game_time.weekday()] = 0
drawn_text.clear()


def run_new_day() -> bool:
    """
    跑一次新一天结算，异常时打印回溯
    Keyword arguments:
    无
    Return arguments:
    bool -- 是否没有抛出异常
    """
    try:
        past_day_settle.update_new_day()
        return True
    except Exception:
        traceback.print_exc()
        return False


check("update_new_day 不抛异常", run_new_day())
check("当天已触发事件的记录清空", cache.today_taiggered_event_record == set(), cache.today_taiggered_event_record)
check("pre_game_time 推进到当前时间（主循环靠它判「跨天」，不推进就会每一轮都再结算一次新一天）", cache.pre_game_time == cache.game_time, (cache.pre_game_time, cache.game_time))
check("每日指令记录追加了当天的日期抬头", len(cache.daily_intsruce) == 1 and game_time.get_date_until_day() in cache.daily_intsruce[0], cache.daily_intsruce)
check("全员（含玩家）香薰疗愈 flag 清零", all(one.sp_flag.aromatherapy == 0 for one in npc_list + [pl]))
check("NPC 的「食物不对劲」flag 清零", all(one.sp_flag.find_food_weird is False for one in npc_list))
check("NPC 的游泳 flag 清零，三个娱乐时段都重新抽成了真实的娱乐项目",
      all(one.sp_flag.swim == 0 and len(one.entertainment.entertainment_type) == 3
          and all(e and e in game_config.config_entertainment for e in one.entertainment.entertainment_type) for one in npc_list),
      [one.entertainment.entertainment_type for one in npc_list])
check("欲望值按欲望等级增加 [等级, 2×等级]", all(2 <= one.desire_point <= 4 for one in npc_list), [one.desire_point for one in npc_list])
check("早安问候：已问候过的（2）清零，服务开启且未问候的（1）留着", trader.sp_flag.morning_salutation == 0 and worker.sp_flag.morning_salutation == 1,
      (trader.sp_flag.morning_salutation, worker.sp_flag.morning_salutation))
check("晚安问候：服务开启的留着，服务关闭的清零", trader.sp_flag.night_salutation == 1 and worker.sp_flag.night_salutation == 0,
      (trader.sp_flag.night_salutation, worker.sp_flag.night_salutation))
check("玩家背包：品质 1 的食物过期丢弃，品质 8 的变质为 4，母乳折成鲜母乳后移出背包",
      list(pl.food_bag) == [food_keep.uid] and food_keep.quality == 4, [(one.quality, one.milk_ml) for one in pl.food_bag.values()])
check("过期丢弃有提示", _("你持有的{0}个食物因过期变质而自动丢弃了\n").format(1) in drawn_text)
check("精液转化：当日射精量计入矿石病药材并清零计数", ri.materials_resouce[12] == 120 and ri.total_semen_count == 0, (ri.materials_resouce[12], ri.total_semen_count))
check("母乳转化：冰箱 30 + 背包 20 计入鲜母乳，冰箱清空", ri.materials_resouce[31] == 50 and ri.milk_in_fridge == {}, (ri.materials_resouce[31], ri.milk_in_fridge))
check("粉红凭证：好感 350 折 3 张 + 周日陷落 1 级干员 20 张，两个计数都清零",
      ri.materials_resouce[4] - pink_before == 23 and ri.total_favorability_increased == 0 and ri.week_fall_chara_pink_certificate_add == 0,
      (ri.materials_resouce[4] - pink_before, ri.total_favorability_increased, ri.week_fall_chara_pink_certificate_add))
check("今日交易量清零", ri.today_trade_resource_count.get(11) == 0, ri.today_trade_resource_count.get(11))
check("流水线的上次结算时刻重置为当前小时", ri.assembly_line[0][4] == cache.game_time.hour, ri.assembly_line[0])
check("香薰疗愈次数按疗养庭院等级刷新（1 级 1 次）", ri.remaining_aromatherapy_sessions_today == 1, ri.remaining_aromatherapy_sessions_today)
check("全局效率落在 [50, 200]", 50 <= ri.effectiveness <= 200, ri.effectiveness)
check("岗位名单按在编角色重建：交易员 / 工人 / 药田种植员 / 无岗位",
      ri.all_work_npc_set[111] == {101} and ri.all_work_npc_set[121] == {102} and ri.all_work_npc_set[161] == {103} and 104 in ri.all_work_npc_set[0]
      and ri.trade_operator_ids_list == [101] and ri.production_worker_ids == [102] and ri.herb_garden_operator_ids == [103],
      (ri.all_work_npc_set[111], ri.all_work_npc_set[121], ri.all_work_npc_set[161], ri.trade_operator_ids_list, ri.production_worker_ids, ri.herb_garden_operator_ids))
check("主交易员有效性：仍是交易员的留着，已不是交易员的撤销",
      ri.resource_type_main_trader[game_config.config_resouce[11].type] == 101 and ri.resource_type_main_trader[DAIRY_TYPE] == 0,
      (ri.resource_type_main_trader[game_config.config_resouce[11].type], ri.resource_type_main_trader[DAIRY_TYPE]))

# ==== 3. 每日资源结算的仓库上限 ====
section("鲜母乳与矿石病药材的每日结算不超过仓库容量")
# 16f1f3ea4：每日结算时鲜母乳和矿石病药材可以超过仓库容量上限
ri.materials_resouce[31] = ri.warehouse_capacity - 10
ri.milk_in_fridge = {fallen.cid: 30}
basement.settle_milk()
check("鲜母乳：差 10 满仓时冰箱再进 30，封顶在仓库容量", ri.materials_resouce[31] == ri.warehouse_capacity and ri.milk_in_fridge == {}, (ri.materials_resouce[31], ri.warehouse_capacity))
ri.materials_resouce[12] = ri.warehouse_capacity - 10
ri.total_semen_count = 50
basement.settle_semen()
check("矿石病药材：差 10 满仓时再进 50，封顶在仓库容量", ri.materials_resouce[12] == ri.warehouse_capacity and ri.total_semen_count == 0, (ri.materials_resouce[12], ri.warehouse_capacity))

# ==== 4. 锁定修复：浮点库存的鲜母乳 ====
section("锁定修复 551a91174：旧存档的浮点鲜母乳经流水线做成乳制品后一次自动卖出 50 个以上，跨日结算不报错")
# 旧存档（2025-10 前榨乳存入冰箱的母乳未取整）的鲜母乳库存可能是小数。流水线用它做母乳酸奶（配方 5：20 鲜母乳 → 1 酸奶）时，
#    原料是瓶颈的话产量是 float，酸奶库存随之变成 float；第二天贸易部自动卖出 50 个以上，供需调整里的 range(float) 就会抛 TypeError
check("fixture：配方 5 是 20 鲜母乳 → 1 母乳酸奶", game_config.config_productformula[5].product_id == 32 and game_config.config_productformula_data[5] == {31: 20},
      (game_config.config_productformula[5].product_id, game_config.config_productformula_data[5]))
set_time(datetime.datetime(2026, 9, 14, 0, 5))
cache.pre_game_time = datetime.datetime(2026, 9, 13, 23, 50)
ri.materials_resouce[31] = 105.5
ri.materials_resouce[32] = 60
ri.assembly_line[0] = [5, 0, 0.0, 0, 0]
ri.resource_type_main_trader[DAIRY_TYPE] = trader.cid
sell_setting = resource_exchange_panel._ensure_trade_setting(32)
sell_setting.update({"sell_on": True, "sell_stock": 0, "sell_price_percent": 1})
drawn_text.clear()
check("update_new_day 不抛异常（浮点鲜母乳 → 流水线 → 自动卖出 65 个酸奶）", run_new_day())
check("流水线按整数产量生产：鲜母乳只扣掉 5 份原料（105.5 → 5.5）", ri.materials_resouce[31] == 5.5, ri.materials_resouce[31])
check("母乳酸奶 60 + 5 = 65 个全部自动卖出，库存回到整数 0", ri.materials_resouce[32] == 0 and isinstance(ri.materials_resouce[32], int), repr(ri.materials_resouce[32]))
check("今日卖出量记为整数 65", ri.today_trade_resource_count.get(32) == 65 and isinstance(ri.today_trade_resource_count.get(32), int), repr(ri.today_trade_resource_count.get(32)))
check("贸易部结算提示里有这笔自动卖出", any(_("自动卖出") in text and str(65) in text for text in drawn_text))
check("龙门币仍是整数", isinstance(ri.materials_resouce[1], int), repr(ri.materials_resouce[1]))
sell_setting["sell_on"] = False

# ==== 5. 睡眠结算 ====
section("玩家入睡时的结算（update_sleep）")
set_time(datetime.datetime(2026, 9, 14, 23, 0))
# 宝珠：状态值清零并换成珠；苦痛 / 恐怖 / 抑郁换成 1/4 的本珠与 1/2 的反发珠；反发珠按 1 好意抵 2 反发
fallen.status_data[0] = 1000
fallen.juel[0] = 0
worker.status_data[17] = 400
worker.juel[17] = 0
worker.juel[20] = 0
farmer.juel[20] = 10
farmer.juel[15] = 3
for juel_id in (10, 11, 12, 13):
    farmer.juel[juel_id] = 0
# 玩家：射精槽、今日首次射精、理智成长（今日消耗 100 → 上限 +2）
pl.eja_point = 500
pl.action_info.day_first_shoot_semen = False
pl.pl_ability.today_sanity_point_cost = 100
pl.sanity_point_max = 100
# 助理 101：早安问候开启、晚安问候开启且在睡觉、跟随服务开启但没在跟随
pl.assistant_character_id = trader.cid
trader.assistant_services[5] = 1
trader.sp_flag.morning_salutation = 1
trader.assistant_services[6] = 1
trader.sp_flag.night_salutation = 1
trader.behavior.behavior_id = constant.Behavior.SLEEP
trader.assistant_services[2] = 1
trader.sp_flag.is_follow = 0
# NPC 的每日 flag 与 H 状态
for one in npc_list:
    one.angry_point = 99
    one.action_info.h_interrupt = 1
    one.first_record.day_first_meet = 0
    one.sp_flag.sleep_h_awake = True
fallen.h_state.orgasm_count[0] = [3, 2]
fallen.h_state.time_stop_orgasm_count[0] = 5
cache.pl_sleep_save_flag = False
try:
    sleep_settle.update_sleep()
    check("update_sleep 不抛异常", True)
except Exception as error:
    traceback.print_exc()
    check("update_sleep 不抛异常", False, repr(error))
check("宝珠：皮肤状态 1000 换成对应的珠，状态值清零", fallen.juel[0] == attr_calculation.get_juel(1000) and fallen.status_data[0] == 0, (fallen.juel[0], fallen.status_data[0]))
_juel_400 = attr_calculation.get_juel(400)
check("宝珠：苦痛 400 换成 1/4 苦痛珠与 1/2 反发珠", worker.juel[17] == _juel_400 // 4 and worker.juel[20] == _juel_400 // 2 and worker.status_data[17] == 0,
      (worker.juel[17], worker.juel[20], _juel_400))
check("反发珠抵消：3 个屈服珠抵掉 6 个反发珠（10 → 4，屈服 3 → 0）", farmer.juel[20] == 4 and farmer.juel[15] == 0, (farmer.juel[20], farmer.juel[15]))
check("玩家：射精槽清零、重置今日首次射精", pl.eja_point == 0 and pl.action_info.day_first_shoot_semen is True)
check("玩家：理智上限按今日消耗 /50 成长（100 → 102），今日消耗清零", pl.sanity_point_max == 102 and pl.pl_ability.today_sanity_point_cost == 0,
      (pl.sanity_point_max, pl.pl_ability.today_sanity_point_cost))
check("助理：早安问候清零、在睡的晚安问候清零、跟随服务开启时改为跟随",
      trader.sp_flag.morning_salutation == 0 and trader.sp_flag.night_salutation == 0 and trader.sp_flag.is_follow == 1,
      (trader.sp_flag.morning_salutation, trader.sp_flag.night_salutation, trader.sp_flag.is_follow))
check("NPC：生气程度重抽为 [1, 34]", all(1 <= one.angry_point <= 34 for one in npc_list), [one.angry_point for one in npc_list])
check("NPC：H 被撞破 flag 清零、重置每天第一次见面、清零睡奸中醒来",
      all(one.action_info.h_interrupt == 0 and one.first_record.day_first_meet == 1 and one.sp_flag.sleep_h_awake is False for one in npc_list))
check("NPC：H 状态重置（部位绝顶计数归零），时停绝顶计数保留", fallen.h_state.orgasm_count[0] == [0, 0] and fallen.h_state.time_stop_orgasm_count[0] == 5,
      (fallen.h_state.orgasm_count[0], fallen.h_state.time_stop_orgasm_count[0]))
check("置位睡觉存档 flag（主循环据此调 update_save）", cache.pl_sleep_save_flag is True)

section("睡觉自动存档钩子（update_save，establish_save 已打桩）")
drawn_text.clear()
sleep_settle.update_save()
check("自动存档只请求了一次，存档 id 为 auto", save_call_list == ["auto"], save_call_list)
check("存档前画出了今日小贴士", any(_("请博士在保存时阅读今日的小贴士：") in text for text in drawn_text))

section("充足睡眠的次日额外精液（refresh_temp_semen_max）")
pl.semen_point_max = 100
pl.semen_point = 100
pl.tem_extra_semen_point = 0
pl.behavior.duration = 480
sleep_settle.refresh_temp_semen_max()
check("睡满 6 小时：未用精液的一半转为次日额外精液，未达 4 倍上限不给浓厚精液", pl.tem_extra_semen_point == 50 and pl.talent[33] == 0, (pl.tem_extra_semen_point, pl.talent[33]))
pl.tem_extra_semen_point = 380
sleep_settle.refresh_temp_semen_max()
check("额外精液封顶在 4 倍上限，并获得浓厚精液", pl.tem_extra_semen_point == 400 and pl.talent[33] == 1, (pl.tem_extra_semen_point, pl.talent[33]))
pl.behavior.duration = 300
sleep_settle.refresh_temp_semen_max()
check("睡不满 6 小时不转化", pl.tem_extra_semen_point == 400, pl.tem_extra_semen_point)
pl.talent[33] = 0

# ==== 6. 锁定修复：持续一天以上的行为 ====
section("锁定修复 151e48c67：单次行为持续一天以上时，体力气力消耗按完整时长结算")
LONG_BEHAVIOR_ID = "make_food"
""" 做饭：双方中量体力 / 气力消耗（每分钟 3 / 6），update.log 里的例子就是断电时做费时的料理 """
check("fixture：做饭行为带中量体力与气力消耗", LONG_BEHAVIOR_ID in game_config.config_behavior_effect_data
      and {13, 14} <= set(game_config.config_behavior_effect_data[LONG_BEHAVIOR_ID]), game_config.config_behavior_effect_data.get(LONG_BEHAVIOR_ID))
SETTLE_NOW = datetime.datetime(2026, 9, 15, 12, 0)
""" 长行为的结算时刻 """
LONG_FOOD = game_type.Food()
""" 正在做的菜：真实的做饭行为总带着 target_food，口上前提会读它的调味 """
LONG_FOOD.recipe = sorted(game_config.config_recipes)[0]
LONG_FOOD.name = game_config.config_recipes[LONG_FOOD.recipe].name


def settle_long_behavior(minute: int) -> tuple:
    """
    让玩家做一次已进行 minute 分钟的饭，并结算行为
    Keyword arguments:
    minute -- 行为开始到结算时刻经过的分钟数（负数表示结算时刻早于开始时间）
    Return arguments:
    tuple -- (体力减少量, 气力减少量, 料理经验增加量)
    """
    pl.hit_point_max = pl.hit_point = 10 ** 7
    pl.mana_point_max = pl.mana_point = 10 ** 7
    pl.target_character_id = 0
    pl.behavior.behavior_id = LONG_BEHAVIOR_ID
    pl.behavior.duration = max(minute, 1)
    pl.behavior.start_time = SETTLE_NOW - datetime.timedelta(minutes=minute)
    pl.behavior.target_food = LONG_FOOD
    exp_before = pl.experience.get(83, 0)
    settle_behavior.handle_settle_behavior(0, SETTLE_NOW)
    return 10 ** 7 - pl.hit_point, 10 ** 7 - pl.mana_point, pl.experience.get(83, 0) - exp_before


# 桩：二段结算（高潮、刻印、道具等）的体力气力消耗是与时长无关的定额，触发与否取决于前面各段留下的状态，
#    会把「按时长线性消耗」的断言搅乱；本段只测一段结算里按 add_time 计的消耗，测完还原
_real_check_second_effect = settle_behavior.second_behavior.check_second_effect
settle_behavior.second_behavior.check_second_effect = lambda *args, **kwargs: None
cost_60 = settle_long_behavior(60)
check("对照：60 分钟消耗体力 180、气力 360", cost_60[:2] == (180, 360), cost_60)
cost_1440 = settle_long_behavior(1440)
check("恰好一整天（1440 分钟）：体力 4320、气力 8640，并照常得到料理经验", cost_1440[:2] == (4320, 8640) and cost_1440[2] > 0, cost_1440)
cost_1500 = settle_long_behavior(1500)
check("一天以上（1500 分钟）：按完整的 1500 分钟结算，不是只算不满一天的 60 分钟", cost_1500[:2] == (4500, 9000), cost_1500)
cost_neg = settle_long_behavior(-5)
check("结算时刻早于开始时间：不结算（不会把 -5 分钟当成 1435 分钟）", cost_neg == (0, 0, 0), cost_neg)

# ==== 6.1 锁定修复：行为跨季末午夜 ====
section("锁定修复：行为跨季末午夜时，结算时长不把被时钟跳过的月份算进去")
SEASON_END_START_LIST = [
    datetime.datetime(2026, 9, 30, 23, 40),
    datetime.datetime(2026, 12, 31, 23, 40),
    datetime.datetime(2027, 3, 31, 23, 40),
    datetime.datetime(2027, 6, 30, 23, 40),
    datetime.datetime(2027, 12, 31, 23, 40),
]
""" 各季月最后一天的 23:40：从这里开始的 30 分钟行为会跨过季末午夜（最后一项跨的是含闰年二月的那次换季） """


def settle_behavior_from(start_time: datetime.datetime, minute: int) -> tuple:
    """
    让玩家从 start_time 起做 minute 分钟的饭，按行为循环的算法（开始时间 + 时长，见 character_behavior.judge_character_status）取结算时刻并结算
    Keyword arguments:
    start_time -- 行为开始时间
    minute -- 行为时长（分钟）
    Return arguments:
    tuple -- (结算时刻, 体力减少量, 气力减少量)
    """
    pl.hit_point_max = pl.hit_point = 10 ** 7
    pl.mana_point_max = pl.mana_point = 10 ** 7
    pl.target_character_id = 0
    pl.behavior.behavior_id = LONG_BEHAVIOR_ID
    pl.behavior.duration = minute
    pl.behavior.start_time = start_time
    pl.behavior.target_food = LONG_FOOD
    end_time = game_time.get_sub_date(minute=minute, old_date=start_time)
    settle_behavior.handle_settle_behavior(0, end_time)
    return end_time, 10 ** 7 - pl.hit_point, 10 ** 7 - pl.mana_point


season_cost_list = [settle_behavior_from(now_start, 30) for now_start in SEASON_END_START_LIST]
check("fixture：这些行为的结束时刻都被季月归并到下一个季月 1 日 00:10", all(now_cost[0].day == 1 and now_cost[0].month in (3, 6, 9, 12) and (now_cost[0].hour, now_cost[0].minute) == (0, 10)
      for now_cost in season_cost_list), [now_cost[0] for now_cost in season_cost_list])
check("季末 23:40 起做 30 分钟饭：按 30 分钟结算（体力 90、气力 180），不是按公历差的约 8.8 万分钟", all(now_cost[1:] == (90, 180) for now_cost in season_cost_list),
      [now_cost[1:] for now_cost in season_cost_list])
settle_behavior.second_behavior.check_second_effect = _real_check_second_effect
pl.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
pl.behavior.duration = 1500
pl.behavior.start_time = SETTLE_NOW - datetime.timedelta(minutes=1500)
check("实时结算的真实经过时间同样按完整时长算（1500 分钟）", realtime_settle.get_true_add_time(0, SETTLE_NOW, pl.behavior.start_time) == 1500,
      realtime_settle.get_true_add_time(0, SETTLE_NOW, pl.behavior.start_time))
pl.behavior.duration = 0
pl.hit_point_max = pl.hit_point = 100
pl.mana_point_max = pl.mana_point = 100

# ==== 6.2 锁定修复：实时结算与等待类时长跨季末午夜 ====
section("锁定修复：实时结算与等待类时长跨季末午夜时按时钟上实际经过的时间算")
SEASON_LAST_NIGHT = datetime.datetime(2026, 9, 30, 22, 0)
""" 秋季最后一天的 22:00 """
SEASON_FIRST_MORNING = datetime.datetime(2026, 12, 1, 6, 0)
""" 冬季第一天的 06:00：时钟上是 SEASON_LAST_NIGHT 的 8 小时之后 """
check("fixture：季末 22:00 起的 8 小时，结束在下一个季月 1 日 06:00", game_time.get_sub_date(minute=480, old_date=SEASON_LAST_NIGHT) == SEASON_FIRST_MORNING)
pl.behavior.behavior_id = constant.Behavior.SLEEP
pl.behavior.start_time = SEASON_LAST_NIGHT
pl.behavior.duration = 480
check("实时结算的真实经过时间：季末那一夜睡 8 小时计 480 分钟，不是约 8.8 万分钟", realtime_settle.get_true_add_time(0, SEASON_FIRST_MORNING, SEASON_LAST_NIGHT) == 480,
      realtime_settle.get_true_add_time(0, SEASON_FIRST_MORNING, SEASON_LAST_NIGHT))


def eja_point_after(eja_time: datetime.datetime, now_time: datetime.datetime) -> int:
    """
    让玩家在 eja_time 射精后发呆到 now_time，做一次实时结算，返回结算后的射精值
    Keyword arguments:
    eja_time -- 上次射精的时间（同时是这段发呆的开始时间）
    now_time -- 结算时的游戏时间
    Return arguments:
    int -- 结算后的射精值（结算前固定为 5000）
    """
    cache.game_time = now_time
    pl.sp_flag.is_h = False
    pl.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    pl.behavior.start_time = eja_time
    pl.behavior.duration = max(1, int(game_time.count_play_second(eja_time, now_time) / 60))
    pl.action_info.last_eaj_add_time = eja_time
    pl.eja_point = 5000
    realtime_settle.character_aotu_change_value(0, now_time, eja_time)
    return pl.eja_point


check("对照：同一天内射精后 15 分钟仍在冷却、射精值不回落；45 分钟后回落",
      eja_point_after(datetime.datetime(2026, 9, 15, 12, 0), datetime.datetime(2026, 9, 15, 12, 15)) == 5000
      and eja_point_after(datetime.datetime(2026, 9, 15, 12, 0), datetime.datetime(2026, 9, 15, 12, 45)) == 5000 - 450)
eja_cross_season = eja_point_after(datetime.datetime(2026, 9, 30, 23, 55), datetime.datetime(2026, 12, 1, 0, 10))
check("季末 23:55 射精、下一个季月 00:10 结算（时钟上只过了 15 分钟）：仍在 30 分钟冷却内，射精值不回落", eja_cross_season == 5000, eja_cross_season)
set_time(DEFAULT_TIME)
pl.eja_point = 0
pl.behavior = game_type.Behavior()
pl.behavior.start_time = DEFAULT_TIME

from Script.Design import character_behavior, handle_npc_ai_in_h, update as update_module  # noqa: E402
from Script.Settle import default as settle_default  # noqa: E402

WAIT_NPC_ID = 9301
""" 本段用的干员 fixture：与玩家同处一室 """
wait_npc = make_character(WAIT_NPC_ID, "换季等待测试干员", position=pl.position)

# H 中 / 木头人的干员：行动锁成等待，时长补成「玩家这一步的长度」
wait_npc.hypnosis.blockhead = True
pl.behavior = game_type.Behavior()
cache.game_time = datetime.datetime(2026, 12, 1, 0, 10)
wait_npc.behavior = game_type.Behavior()
handle_npc_ai_in_h.judge_character_h_obscenity_unconscious(WAIT_NPC_ID, datetime.datetime(2026, 9, 30, 23, 50))
check("木头人干员的等待时长 = 玩家这一步的长度：季末 23:50 → 下一个季月 00:10 是 20 分钟",
      wait_npc.behavior.behavior_id == constant.Behavior.WAIT and wait_npc.behavior.duration == 20, (wait_npc.behavior.behavior_id, wait_npc.behavior.duration))
wait_npc.hypnosis.blockhead = False

# 「等待至对方行动结束」两个结算效果（事件选项在用）
flow_call_list = []
""" 时间推进入口被调用时传入的分钟数 """
_real_game_update_flow = update_module.game_update_flow
update_module.game_update_flow = lambda add_time: flow_call_list.append(add_time)


def player_wait_target(target_start: datetime.datetime, target_duration: int, now_time: datetime.datetime) -> tuple:
    """
    结算「玩家等待至交互对象行动结束」：交互对象从 target_start 起做 target_duration 分钟的事，玩家在 now_time 开始等
    Keyword arguments:
    target_start -- 交互对象行动的开始时间
    target_duration -- 交互对象行动的时长（分钟）
    now_time -- 结算时间
    Return arguments:
    tuple -- (玩家行为id, 玩家行为时长, 时间推进入口收到的分钟数列表)
    """
    flow_call_list.clear()
    pl.behavior = game_type.Behavior()
    pl.behavior.behavior_id = constant.Behavior.CHAT
    pl.behavior.duration = 5
    pl.target_character_id = WAIT_NPC_ID
    wait_npc.behavior.start_time = target_start
    wait_npc.behavior.duration = target_duration
    settle_default.handle_wait_unitl_traget_action_end(0, 1, game_type.CharacterStatusChange(), now_time)
    return pl.behavior.behavior_id, pl.behavior.duration, list(flow_call_list)


def npc_wait_player(player_start: datetime.datetime, player_duration: int, now_time: datetime.datetime) -> int:
    """
    结算「自己等待至玩家行动结束」：玩家从 player_start 起做 player_duration 分钟的事，干员在 now_time 开始等
    Keyword arguments:
    player_start -- 玩家行动的开始时间
    player_duration -- 玩家行动的时长（分钟）
    now_time -- 结算时间
    Return arguments:
    int -- 干员的等待时长（分钟）
    """
    pl.behavior.start_time = player_start
    pl.behavior.duration = player_duration
    wait_npc.behavior = game_type.Behavior()
    settle_default.handle_wait_unitl_player_action_end(WAIT_NPC_ID, 1, game_type.CharacterStatusChange(), now_time)
    return wait_npc.behavior.duration


try:
    wait_result = player_wait_target(datetime.datetime(2026, 9, 15, 12, 0), 60, datetime.datetime(2026, 9, 15, 12, 10))
    check("对照：对方 12:00 起做 60 分钟，玩家 12:10 开始等 → 等 50 分钟", wait_result == (constant.Behavior.WAIT, 50, [50]), wait_result)
    wait_result = player_wait_target(datetime.datetime(2026, 9, 30, 23, 30), 60, datetime.datetime(2026, 9, 30, 23, 40))
    check("对方的行动跨季末午夜（23:30 起 60 分钟），玩家 23:40 开始等 → 等 50 分钟", wait_result == (constant.Behavior.WAIT, 50, [50]), wait_result)
    wait_result = player_wait_target(datetime.datetime(2026, 12, 1, 0, 0), 5, datetime.datetime(2026, 12, 1, 0, 10))
    check("对方的行动已经结束时不等待：玩家的行为不变，也不拿负数去推进时间", wait_result == (constant.Behavior.CHAT, 5, []), wait_result)
    check("对照：玩家 12:00 起做 60 分钟，干员 12:10 开始等 → 等 51 分钟", npc_wait_player(datetime.datetime(2026, 9, 15, 12, 0), 60, datetime.datetime(2026, 9, 15, 12, 10)) == 51)
    npc_wait = npc_wait_player(datetime.datetime(2026, 9, 30, 23, 30), 60, datetime.datetime(2026, 9, 30, 23, 40))
    check("玩家的行动跨季末午夜（23:30 起 60 分钟），干员 23:40 开始等 → 等 51 分钟", npc_wait == 51, npc_wait)
    npc_wait = npc_wait_player(datetime.datetime(2026, 12, 1, 0, 0), 5, datetime.datetime(2026, 12, 1, 0, 10))
    check("玩家的行动已经结束时，干员的等待时长至少 1 分钟（不出现 0 或负数时长）", npc_wait == 1, npc_wait)
finally:
    update_module.game_update_flow = _real_game_update_flow

# 负时长的行为：必须被行为循环拦下并重置，否则在季月 1 日附近它的结束时间会被归并到月底
wait_npc.behavior = game_type.Behavior()
wait_npc.behavior.behavior_id = constant.Behavior.WAIT
wait_npc.behavior.start_time = datetime.datetime(2026, 12, 1, 0, 5)
wait_npc.behavior.duration = -10
wait_npc.target_character_id = WAIT_NPC_ID
wait_npc.sp_flag.is_h = False
time_over_result = character_behavior.judge_character_status_time_over(WAIT_NPC_ID, datetime.datetime(2026, 12, 1, 0, 5))
check("季月 1 日 00:05 开始、时长 -10 分钟的异常行为：被拦下并重置为从当前时间起的 1 分钟空闲",
      time_over_result == 0 and wait_npc.behavior.duration == 1 and wait_npc.behavior.start_time == datetime.datetime(2026, 12, 1, 0, 5),
      (time_over_result, wait_npc.behavior.duration, wait_npc.behavior.start_time))
remove_character(WAIT_NPC_ID)
pl.target_character_id = 0
pl.behavior = game_type.Behavior()
set_time(DEFAULT_TIME)

# ==== 6.3 锁定修复：按天数累计的概率与权重跨季 ====
section("锁定修复：访客来访率与训练欲望按时钟上实际经过的天数算")
from Script.UI.Panel import invite_visitor_panel  # noqa: E402


def visitor_arrive_count(last_visit: datetime.datetime, now_time: datetime.datetime, dice: int) -> int:
    """
    跑一次访客抵达与离开的每日结算，返回「按时间产生访客」被触发的次数
    Keyword arguments:
    last_visit -- 上次访客来访的时间
    now_time -- 当前游戏时间
    dice -- 让 1~100 的来访判定固定掷出的点数（来访率 >= 它才会来）
    Return arguments:
    int -- 访客抵达结算被调用的次数
    """
    arrive_list = []
    saved = (invite_visitor_panel.settle_visitor_arrivals, random.randint, cache.rhodes_island.visitor_info, cache.rhodes_island.base_move_visitor_flag,
             cache.rhodes_island.last_visitor_time, cache.game_time)
    invite_visitor_panel.settle_visitor_arrivals = lambda *args, **kwargs: arrive_list.append(1)
    random.randint = lambda low, high: dice
    try:
        cache.rhodes_island.visitor_info = {}
        cache.rhodes_island.base_move_visitor_flag = False
        cache.rhodes_island.last_visitor_time = last_visit
        cache.game_time = now_time
        invite_visitor_panel.settle_visitor_arrivals_and_departures()
    finally:
        (invite_visitor_panel.settle_visitor_arrivals, random.randint, cache.rhodes_island.visitor_info, cache.rhodes_island.base_move_visitor_flag,
         cache.rhodes_island.last_visitor_time, cache.game_time) = saved
    return len(arrive_list)


check("对照：同一季月内距上次来访 24 天，来访率 72%，掷出 50 点时来访、掷出 80 点时不来",
      visitor_arrive_count(datetime.datetime(2026, 9, 1, 8, 0), datetime.datetime(2026, 9, 25, 8, 0), 50) == 1
      and visitor_arrive_count(datetime.datetime(2026, 9, 1, 8, 0), datetime.datetime(2026, 9, 25, 8, 0), 80) == 0)
check("上次来访在 9/25，换季后第一天（12/1）时钟上只过了 6 天，来访率 18%：掷出 50 点不来访（按公历差是 67 天、201%，必定来访）",
      visitor_arrive_count(datetime.datetime(2026, 9, 25, 8, 0), datetime.datetime(2026, 12, 1, 8, 0), 50) == 0
      and visitor_arrive_count(datetime.datetime(2026, 9, 25, 8, 0), datetime.datetime(2026, 12, 1, 8, 0), 18) == 1)


def train_weight(last_training: datetime.datetime, now_time: datetime.datetime) -> int:
    """
    求玩家「距离上次战斗训练已经超过两天」前提的权重
    Keyword arguments:
    last_training -- 上次战斗训练的时间
    now_time -- 当前游戏时间
    Return arguments:
    int -- 前提权重
    """
    saved = (pl.action_info.last_training_time, cache.game_time)
    try:
        pl.action_info.last_training_time = last_training
        cache.game_time = now_time
        return handle_premise.handle_have_trained(0)
    finally:
        pl.action_info.last_training_time, cache.game_time = saved


check("对照：同一季月内 3 天没训练权重 20，不满 2 天为 0，上次训练的记录晚于当前时间为 0",
      train_weight(datetime.datetime(2026, 9, 7, 10, 0), datetime.datetime(2026, 9, 10, 10, 0)) == 20
      and train_weight(datetime.datetime(2026, 9, 7, 10, 0), datetime.datetime(2026, 9, 8, 18, 0)) == 0
      and train_weight(datetime.datetime(2026, 9, 7, 11, 0), datetime.datetime(2026, 9, 7, 10, 0)) == 0)
season_train_weight = train_weight(datetime.datetime(2026, 9, 29, 10, 0), datetime.datetime(2026, 12, 1, 10, 0))
check("9/29 训练、换季后第一天（12/1）时钟上只过了 2 天：权重 10，不是按公历 63 天算的 620", season_train_weight == 10, season_train_weight)
check("从未训练过（记录是公元 1 年的缺省值）时照常给出权重，不报错", train_weight(datetime.datetime(1, 1, 1), datetime.datetime(2026, 9, 7, 10, 0)) > 0)

# ==== 6.4 锁定修复：药效的失效时刻跨季 ====
section("锁定修复：利尿剂、安眠药、事前避孕药的失效时刻落在时钟能走到的时刻上")
from Script.Settle import item_effect  # noqa: E402

DRUG_NPC_ID = 9302
""" 本段用的干员 fixture：被博士用药的对象 """
drug_npc = make_character(DRUG_NPC_ID, "换季药效测试干员", position=pl.position)
pl.target_character_id = DRUG_NPC_ID


def drug_end_time(effect_func, item_index: int, use_time: datetime.datetime) -> datetime.datetime:
    """
    博士在 use_time 对 fixture 干员用一次药，返回记下的失效时刻
    Keyword arguments:
    effect_func -- 用药的结算函数
    item_index -- 这种药在 h_state.body_item 里的下标（8 利尿剂 / 9 安眠药 / 11 事前避孕药）
    use_time -- 用药时间
    Return arguments:
    datetime.datetime -- 记下的失效时刻
    """
    drug_npc.h_state.body_item[item_index][1] = False
    drug_npc.h_state.body_item[item_index][2] = None
    effect_func(0, 1, game_type.CharacterStatusChange(), use_time)
    return drug_npc.h_state.body_item[item_index][2]


check("对照：同一季月内利尿剂管 4 小时、安眠药管 8 小时",
      drug_end_time(item_effect.handle_target_diuretics_on, 8, datetime.datetime(2026, 9, 15, 12, 0)) == datetime.datetime(2026, 9, 15, 16, 0)
      and drug_end_time(item_effect.handle_target_add_tired_tosleep, 9, datetime.datetime(2026, 9, 15, 20, 0)) == datetime.datetime(2026, 9, 16, 4, 0))
drug_end_list = [
    drug_end_time(item_effect.handle_target_diuretics_on, 8, datetime.datetime(2026, 9, 30, 22, 30)),
    drug_end_time(item_effect.handle_target_add_tired_tosleep, 9, datetime.datetime(2026, 9, 30, 20, 0)),
    drug_end_time(item_effect.handle_target_no_pregnancy_next_day, 11, datetime.datetime(2026, 9, 15, 10, 0)),
    drug_end_time(item_effect.handle_target_no_pregnancy_next_day, 11, datetime.datetime(2026, 9, 1, 10, 0)),
]
check("季末 22:30 用的利尿剂在下一个季月 1 日 02:30 失效；季末 20:00 的安眠药在 1 日 04:00 失效；9/15 服的事前避孕药管满 30 个游戏日到 12/15、9/1 服的到 12/1",
      drug_end_list == [datetime.datetime(2026, 12, 1, 2, 30), datetime.datetime(2026, 12, 1, 4, 0), datetime.datetime(2026, 12, 15, 10, 0), datetime.datetime(2026, 12, 1, 10, 0)],
      drug_end_list)
check("失效时刻都落在季月里（时钟走不到的月份不会出现）", all(now_end.month in (3, 6, 9, 12) for now_end in drug_end_list), drug_end_list)
# 端到端：季末 22:30 用的利尿剂，换季后的 00:10 还在生效，到 02:30 才失效
drug_end_time(item_effect.handle_target_diuretics_on, 8, datetime.datetime(2026, 9, 30, 22, 30))
drug_npc.sp_flag.is_h = False
cache.game_time = datetime.datetime(2026, 12, 1, 0, 10)
realtime_settle.change_character_persistent_state(DRUG_NPC_ID)
diuretics_on_after_midnight = drug_npc.h_state.body_item[8][1]
cache.game_time = datetime.datetime(2026, 12, 1, 2, 30)
realtime_settle.change_character_persistent_state(DRUG_NPC_ID)
check("季末 22:30 用的利尿剂：换季后 00:10 仍在生效，02:30 失效", diuretics_on_after_midnight and not drug_npc.h_state.body_item[8][1],
      (diuretics_on_after_midnight, drug_npc.h_state.body_item[8][1]))
remove_character(DRUG_NPC_ID)
pl.target_character_id = 0
set_time(DEFAULT_TIME)

# ==== 6.5 锁定修复：体外卵的受精判定延迟与被吵醒的剩余时间跨季 ====
section("锁定修复：体外卵的受精判定延迟、被吵醒的剩余分钟数按时钟上实际经过的时间算")
from Script.System.Pregnancy_System import pregnancy_constant, soft_egg_handle  # noqa: E402
from Script.UI.Panel import character_info_head  # noqa: E402

SOFT_EGG_DELAY_MINUTE = pregnancy_constant.SOFT_EGG_FERTILIZATION_DELAY_HOUR * 60
""" 体外卵排出到受精判定的延迟（分钟） """


def soft_egg_remain(lay_time: datetime.datetime, now_time: datetime.datetime) -> int:
    """
    求 lay_time 排出的体外卵在 now_time 距离受精判定还剩的分钟数
    Keyword arguments:
    lay_time -- 卵排出的时间
    now_time -- 当前游戏时间
    Return arguments:
    int -- 剩余分钟数
    """
    saved_time = cache.game_time
    try:
        cache.game_time = now_time
        return soft_egg_handle.get_soft_egg_remain_minute({"lay_time": lay_time})
    finally:
        cache.game_time = saved_time


check("对照：同一天内排出 40 分钟后，离受精判定还剩（延迟 - 40）分钟", soft_egg_remain(datetime.datetime(2026, 9, 15, 12, 0), datetime.datetime(2026, 9, 15, 12, 40)) == SOFT_EGG_DELAY_MINUTE - 40)
soft_egg_cross = soft_egg_remain(datetime.datetime(2026, 9, 30, 23, 30), datetime.datetime(2026, 12, 1, 0, 10))
check("季末 23:30 排出、下一个季月 00:10（时钟上过了 40 分钟）：同样还剩（延迟 - 40）分钟，不会被当成已到期", soft_egg_cross == SOFT_EGG_DELAY_MINUTE - 40, soft_egg_cross)

DISTURBED_NPC_ID = 9303
""" 本段用的干员 fixture：睡觉中被吵醒 """
disturbed_npc = make_character(DISTURBED_NPC_ID, "换季吵醒测试干员", position=pl.position)
disturbed_npc.action_info.sleep_disturbed_end_time = datetime.datetime(2026, 12, 1, 0, 30)
cache.game_time = datetime.datetime(2026, 9, 30, 23, 45)
status_draw_list = character_info_head.get_character_status_list(DISTURBED_NPC_ID)[0]
disturbed_tip_list = [getattr(now_draw, "tooltip", "") for now_draw in status_draw_list if _("刚被吵醒") in str(getattr(now_draw, "tooltip", ""))]
check("季末 23:45 时，要到下一个季月 00:30 才重新想睡的干员：状态栏提示还需 45 分钟，不是约 8.8 万分钟",
      disturbed_tip_list == [_("刚被吵醒，还需{0}分钟才会重新想睡").format(45)], disturbed_tip_list)
remove_character(DISTURBED_NPC_ID)
set_time(DEFAULT_TIME)

# ==== 7. 写盘守卫 ====
section("本文件没有写存档")
check("自动存档之外没有任何 establish_save 调用", save_call_list == ["auto"], save_call_list)
check("仓库 save 目录前后一致（不存在的仍不存在；存在的话文件名、大小、修改时间都没变）", save_dir_state() == SAVE_DIR_BEFORE)

finish()
