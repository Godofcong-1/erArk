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

# ==== 7. 写盘守卫 ====
section("本文件没有写存档")
check("自动存档之外没有任何 establish_save 调用", save_call_list == ["auto"], save_call_list)
check("仓库 save 目录前后一致（不存在的仍不存在；存在的话文件名、大小、修改时间都没变）", save_dir_state() == SAVE_DIR_BEFORE)

finish()
