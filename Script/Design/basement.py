import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise, attr_calculation, map_handle, cooking
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏内缓存数据 """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def get_base_zero() -> game_type.Rhodes_Island:
    """
    基地情况结构体，设为空
    """

    base_data = game_type.Rhodes_Island()

    # 遍历全设施清单
    for all_cid in game_config.config_facility:
        # 全设施等级设为1
        base_data.facility_level[all_cid] = 1

    # 遍历全设施开放
    for all_cid in game_config.config_facility_open:
        # 全设施初始关闭
        base_data.facility_open[all_cid] = False

    # 遍历全资源清单
    for all_cid in game_config.config_resouce:
        # 全资源数量设为0
        base_data.materials_resouce[all_cid] = 0

    # 遍历全部书籍
    for book_id in game_config.config_book:
        # 全书籍设为未借出
        base_data.book_borrow_dict[book_id] = -1

    # 派对设为空
    for i in range(7):
        base_data.party_day_of_week[i] = 0

    # 工作干员合集设为空
    for all_cid in game_config.config_work_type:
        base_data.all_work_npc_set[all_cid] = set()

    # 位置设为炎国
    base_data.current_location = [17, 1701]

    # 访客来访时间初始化
    base_data.last_visitor_time = cache.game_time

    # 初始化流水线
    base_data.assembly_line[0] = [1,set(),0,0,0]

    # 初始化招募
    base_data.recruit_line[0] = [0,0,set(),0]

    # 初始化邀请
    base_data.invite_visitor = [0,0,0]

    # 初始化药田
    base_data.herb_garden_line[0] = [0,set(),0,0,0]
    # 初始化温室
    base_data.green_house_line[0] = [0,set(),0,0,0]

    # 初始化公务工作
    base_data.office_work += 200
    base_data.effectiveness = 100

    return base_data

def get_base_updata():
    """
    遍历基地情况结构体，根据设施等级更新全部数值
    """
    cache = cache_control.cache

    cache.rhodes_island.power_use = 0

    # 遍历全设施清单
    for all_cid in game_config.config_facility:
        # 全设施等级设为对应值
        level = cache.rhodes_island.facility_level[all_cid]

        # 累加全设施的用电量
        facility_name = game_config.config_facility[all_cid].name
        facility_cid = game_config.config_facility_effect_data[facility_name][level]
        facility_effect = game_config.config_facility_effect[facility_cid].effect
        cache.rhodes_island.power_use += game_config.config_facility_effect[facility_cid].power_use

        # 如果满足设施开放的前提条件，则开放该设施
        for open_cid in game_config.config_facility_open:
            if game_config.config_facility_open[open_cid] == True:
                continue
            # 如果zone_cid和facility_cid相等，则开放该设施
            if game_config.config_facility_open[open_cid].zone_cid == facility_cid:
                # print(f"debug zone_cid = {game_config.config_facility_open[open_cid].zone_cid}")
                # print(f"debug facility_cid = {facility_cid}")
                cache.rhodes_island.facility_open[open_cid] = True
            # 如果zone_cid和facility_cid除以十的除数相等，且facility_cid的个位数大于等于zone_cid的个位数，则开放该设施
            elif game_config.config_facility_open[open_cid].zone_cid // 10 == facility_cid // 10 and facility_cid % 10 >= game_config.config_facility_open[open_cid].zone_cid % 10:
                cache.rhodes_island.facility_open[open_cid] = True

    # print(f"debug power_use = {base_data.power_use}")

        # 初始化供电量
        if facility_name == _("动力区"):
            cache.rhodes_island.power_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化仓库容量
        elif facility_name == _("仓储区"):
            cache.rhodes_island.warehouse_capacity = game_config.config_facility_effect[facility_cid].effect
        # 初始化干员人数上限
        elif facility_name == _("宿舍区"):
            cache.rhodes_island.people_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化生活娱乐区设施数量上限
        elif facility_name == _("生活娱乐区"):
            cache.rhodes_island.life_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化患者人数上限，并刷新当天患者人数
        elif facility_name == _("医疗部"):
            cache.rhodes_island.patient_max = game_config.config_facility_effect[facility_cid].effect
            cache.rhodes_island.patient_now = random.randint(int(cache.rhodes_island.patient_max / 2),cache.rhodes_island.patient_max)
        # 初始化科研区设施数量上限
        elif facility_name == _("科研部"):
            cache.rhodes_island.research_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化战斗时干员数量上限
        elif facility_name == _("指挥室"):
            cache.rhodes_island.soldier_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化招募条
        elif facility_name == _("文职部"):
            if 0 not in cache.rhodes_island.recruit_line:
                cache.rhodes_island.recruit_line[0] = [0,0,set(),0]
            if level >= 3 and 1 not in cache.rhodes_island.recruit_line:
                cache.rhodes_island.recruit_line[1] = [0,0,set(),0]
            if level >= 4 and 2 not in cache.rhodes_island.recruit_line:
                cache.rhodes_island.recruit_line[2] = [0,0,set(),0]
            if level >= 5 and 3 not in cache.rhodes_island.recruit_line:
                cache.rhodes_island.recruit_line[3] = [0,0,set(),0]
            # 计算当前总效率
            for recruit_line_id in cache.rhodes_island.recruit_line:
                # 遍历输出干员的能力效率加成
                all_effect = 0
                for chara_id in cache.rhodes_island.recruit_line[recruit_line_id][2]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = 5 * attr_calculation.get_ability_adjust(character_data.ability[40])
                    all_effect += character_effect
                    # 检测角色的工作类型是否为招聘专员，如果不是则将工作类型改为招聘专员
                    if character_data.work.work_type != 71:
                        character_data.work.work_type = 71
                all_effect *= 1 + (facility_effect / 100)
                cache.rhodes_island.recruit_line[recruit_line_id][3] = all_effect
        elif facility_name == _("制造加工区"):
            # 初始化流水线
            if 0 not in cache.rhodes_island.assembly_line:
                cache.rhodes_island.assembly_line[0] = [0,set(),0,0,0]
            if level >= 2 and 1 not in cache.rhodes_island.assembly_line:
                cache.rhodes_island.assembly_line[1] = [0,set(),0,0,0]
            if level >= 3 and 2 not in cache.rhodes_island.assembly_line:
                cache.rhodes_island.assembly_line[2] = [0,set(),0,0,0]
            if level >= 4 and 3 not in cache.rhodes_island.assembly_line:
                cache.rhodes_island.assembly_line[3] = [0,set(),0,0,0]
            if level >= 5 and 4 not in cache.rhodes_island.assembly_line:
                cache.rhodes_island.assembly_line[4] = [0,set(),0,0,0]
            # 计算当前总效率
            for assembly_line_id in cache.rhodes_island.assembly_line:
                cache.rhodes_island.assembly_line[assembly_line_id][2] = 100 + facility_effect
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.assembly_line[assembly_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[48]))
                    cache.rhodes_island.assembly_line[assembly_line_id][2] += character_effect
        elif facility_name == _("访客区"):
            # 刷新最大访客数量
            # 遍历全部客房
            room_count = 0
            for room_id in game_config.config_facility_open:
                # 跳过非客房和未开放的客房
                if _("客房") not in game_config.config_facility_open[room_id].name:
                    continue
                # 跳过未开放的客房
                cache.rhodes_island.facility_open.setdefault(room_id,False)
                if not cache.rhodes_island.facility_open[room_id]:
                    continue
                room_count += 1
            cache.rhodes_island.visitor_max = room_count
        elif facility_name == _("疗养庭院"):
            # 药田
            # 初始化流水线
            if 0 not in cache.rhodes_island.herb_garden_line:
                cache.rhodes_island.herb_garden_line[0] = [0,set(),0,0,0]
            # 计算当前总效率
            for agriculture_line_id in cache.rhodes_island.herb_garden_line:
                cache.rhodes_island.herb_garden_line[agriculture_line_id][2] = 100 + facility_effect
                # print(f"debug agriculture_line_id = {agriculture_line_id},facility_effect = {facility_effect}, final_effect = {cache.rhodes_island.agriculture_line[agriculture_line_id][2]}")
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.herb_garden_line[agriculture_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[47]))
                    cache.rhodes_island.herb_garden_line[agriculture_line_id][2] += character_effect
            # 温室
            # 初始化流水线
            if 0 not in cache.rhodes_island.green_house_line:
                cache.rhodes_island.green_house_line[0] = [0,set(),0,0,0]
            # 计算当前总效率
            for agriculture_line_id in cache.rhodes_island.green_house_line:
                cache.rhodes_island.green_house_line[agriculture_line_id][2] = 100 + facility_effect
                # 遍历输出干员的能力效率加成
                for chara_id in cache.rhodes_island.green_house_line[agriculture_line_id][1]:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    character_effect = int(10 * attr_calculation.get_ability_adjust(character_data.ability[47]))
                    cache.rhodes_island.green_house_line[agriculture_line_id][2] += character_effect
            # 香薰治疗室
            # 刷新香薰疗愈次数
            if level >= 5:
                cache.rhodes_island.remaining_aromatherapy_sessions_today = 3
            elif level == 4:
                cache.rhodes_island.remaining_aromatherapy_sessions_today = 2
            elif level <= 3:
                cache.rhodes_island.remaining_aromatherapy_sessions_today = 1

def calc_facility_efficiency(facility_cid: int = -1) -> float:
    """
    计算区块的工作效率（百分比）
    输入:
        facility_cid -- 设施编号，默认为-1表示计算全局效率
    输出:
        float - 效率（例如 1.1 表示 110%）
    说明:
        根据设施编号计算对应区块的工作效率，若设施编号为-1则计算全局效率
    """
    adjust = 1.0
    # 参数校验
    if facility_cid == -1 or facility_cid not in game_config.config_facility:
        return adjust
    # 获取设施数据
    facility_data = game_config.config_facility[facility_cid]
    facility_name = facility_data.name
    now_level = cache.rhodes_island.facility_level[facility_cid]
    # 设施效果数据
    facility_effect_cid = game_config.config_facility_effect_data[facility_name][int(now_level)]
    facility_effect = game_config.config_facility_effect[facility_effect_cid].effect
    # 子设施获得父区块的供电策略
    zone_cid = facility_cid
    if facility_data.type >= 0:
        zone_cid = facility_data.type
    # 供电策略的调整
    now_power_strategy = cache.rhodes_island.power_supply_strategy.get(zone_cid, 0)
    now_power_strategy_adjust = game_config.config_supply_strategy[now_power_strategy].adjust
    # 设施路径名
    room_full_str = ""
    # TODO 厨房，因为没有单独设施id所以用区块id代替
    if facility_cid == 5:
        room_full_str = map_handle.get_map_system_path_str_for_list(["生娱", "厨房"])
    elif facility_cid == 22:
        room_full_str = map_handle.get_map_system_path_str_for_list(["中枢", "博士办公室"])
    # 设施损坏调整
    damage_adjust = 0.0
    if room_full_str in cache.rhodes_island.facility_damage_data:
        damage_adjust = cache.rhodes_island.facility_damage_data[room_full_str] * 0.01
    # 有特殊计算公式的区块
    # 宿舍区
    if facility_cid == 4:
        adjust += now_level * 0.02
        adjust -= (1 - now_power_strategy_adjust) / 4
    # 其他直接乘以供电策略
    else:
        # 厨房、博士办公室
        if facility_cid in [5, 22]:
            adjust += facility_effect / 100
            adjust -= damage_adjust
        adjust *= now_power_strategy_adjust
    # 效率不会小于20%
    adjust = max(adjust, 0.2)
    return adjust

def update_base_resouce_newday():
    """
    每日刷新基地资源数据\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.UI.Panel import invite_visitor_panel, aromatherapy_panel, agriculture_production_panel, manage_assembly_line_panel, physical_check_and_manage, confinement_and_training, resource_exchange_panel

    now_draw = draw.WaitDraw()
    now_draw.width = window_width

    # 结算公务工作
    settle_office_work()
    # 结算精液转化
    settle_semen()
    # 结算母乳转化
    settle_milk()
    # 结算流水线
    manage_assembly_line_panel.settle_assembly_line(newdayflag=True)
    # 结算农业生产
    agriculture_production_panel.settle_agriculture_line()
    # 结算访客抵达和离开
    invite_visitor_panel.settle_visitor_arrivals_and_departures()
    # 结算收入
    settle_income()
    # 结算资源的供需涨跌
    resource_exchange_panel.daily_supply_demand_fluctuation()
    # 刷新香薰疗愈次数
    aromatherapy_panel.settle_aromatherapy_sessions()
    # 结算粉红凭证
    settle_pink_certificate()
    # 结算体检
    physical_check_and_manage.settle_health_check()
    # 刷新食堂食物
    cooking.init_food_shop_data(new_day_flag=True)
    # 囚犯逃跑结算
    confinement_and_training.settle_prisoners()

def update_work_people():
    """
    刷新各干员的职位和当前正在工作的干员
    """

    # 初始化各职位的干员集合
    cache.rhodes_island.work_people_now = 0
    for all_cid in game_config.config_work_type:
        cache.rhodes_island.all_work_npc_set[all_cid] = set()

    # 清空各流水线中的角色
    for recruit_line_id in cache.rhodes_island.recruit_line:
        for chara_id in cache.rhodes_island.recruit_line[recruit_line_id][2].copy():
            character_data = cache.character_data[chara_id]
            # 如果已经不是招聘专员，则从该流水线中移除
            if character_data.work.work_type != 71:
                cache.rhodes_island.recruit_line[recruit_line_id][2].discard(chara_id)
    for assembly_line_id in cache.rhodes_island.assembly_line:
        for chara_id in cache.rhodes_island.assembly_line[assembly_line_id][1].copy():
            character_data = cache.character_data[chara_id]
            # 如果已经不是工人，则从该流水线中移除
            if character_data.work.work_type != 121:
                cache.rhodes_island.assembly_line[assembly_line_id][1].discard(chara_id)
    cache.rhodes_island.herb_garden_line[0][1].clear()
    cache.rhodes_island.green_house_line[0][1].clear()

    # 遍历所有干员，将有职位的干员加入对应职位集合
    cache.npc_id_got.discard(0)
    for chara_id in cache.npc_id_got:
        character_data = cache.character_data[chara_id]

        # 如果干员有职位，将干员加入对应职位集合
        if character_data.work.work_type:
            cache.rhodes_island.all_work_npc_set[character_data.work.work_type].add(chara_id)
            cache.rhodes_island.work_people_now += 1

            # 如果是供能调控员，则加入供能调控员列表
            if character_data.work.work_type == 11:
                if chara_id not in cache.rhodes_island.power_operator_ids_list:
                    cache.rhodes_island.power_operator_ids_list.append(chara_id)
            # 如果不是供能调控员，则从供能调控员列表中移除
            else:
                if chara_id in cache.rhodes_island.power_operator_ids_list:
                    cache.rhodes_island.power_operator_ids_list.remove(chara_id)

            # 如果不是检修工程师，则清空该角色的检修目标
            if character_data.work.work_type != 21:
                if chara_id in cache.rhodes_island.maintenance_place:
                    cache.rhodes_island.maintenance_place.pop(chara_id)

            # 如果不是铁匠，则清空该角色的维修装备
            if character_data.work.work_type != 22:
                if chara_id in cache.rhodes_island.maintenance_equipment_chara_id:
                    cache.rhodes_island.maintenance_equipment_chara_id.pop(chara_id)

            # 招聘专员如果没有安排到招聘线，则随机分配
            if character_data.work.work_type == 71:
                select_index = -1
                for recruit_line_id in cache.rhodes_island.recruit_line:
                    # 已分配则跳过
                    if chara_id in cache.rhodes_island.recruit_line[recruit_line_id][2]:
                        select_index = recruit_line_id
                        break
                # 未分配则按顺序分配到没满人的招聘线
                if select_index == -1:
                    now_level = cache.rhodes_island.facility_level[7]
                    for recruit_line_id in cache.rhodes_island.recruit_line:
                        if len(cache.rhodes_island.recruit_line[recruit_line_id][2]) < 2 * now_level:
                            cache.rhodes_island.recruit_line[recruit_line_id][2].add(chara_id)
                            break

            # 工人如果没有被分配到流水线，则随机分配
            if character_data.work.work_type == 121:
                select_index = -1
                for assembly_line_id in cache.rhodes_island.assembly_line:
                    if chara_id in cache.rhodes_island.assembly_line[assembly_line_id][1]:
                        select_index = assembly_line_id
                        break
                if select_index == -1:
                    line_id_list = list(cache.rhodes_island.assembly_line.keys())
                    select_index = random.choice(line_id_list)
                    cache.rhodes_island.assembly_line[select_index][1].add(chara_id)

            # 将旧的外交官改为新的邀请专员
            if character_data.work.work_type == 131 and character_data.sp_flag.in_diplomatic_visit == 0:
                character_data.work.work_type = 132

            # 药材种植员默认分配到药田0里
            if character_data.work.work_type == 161:
                if chara_id not in cache.rhodes_island.herb_garden_line[0][1]:
                    cache.rhodes_island.herb_garden_line[0][1].add(chara_id)
            # 花草种植员默认分配到温室0里
            if character_data.work.work_type == 162:
                if chara_id not in cache.rhodes_island.green_house_line[0][1]:
                    cache.rhodes_island.green_house_line[0][1].add(chara_id)

        else:
            cache.rhodes_island.all_work_npc_set[0].add(chara_id)
        # print(f"debug cache.base_resouce.all_work_npc_set = {cache.base_resouce.all_work_npc_set}")


def update_facility_people():
    """
    更新当前基地各设施使用人数
    """

    cache.rhodes_island.reader_now = 0

    cache.npc_id_got.discard(0)
    for id in cache.npc_id_got:
        # 图书馆读者统计
        if handle_premise.handle_in_library(id):
            cache.rhodes_island.reader_now += 1


def settle_milk():
    """
    结算母乳转化
    """

    all_milk = 0

    # 结算冰箱中的母乳
    for character_id in cache.rhodes_island.milk_in_fridge:
        now_milk = cache.rhodes_island.milk_in_fridge[character_id]
        cache.rhodes_island.materials_resouce[31] += now_milk
        all_milk += now_milk
        # print(f"debug {cache.character_data[character_id].name}的母乳（{now_milk}ml）已转化为罗德岛的母乳")
    cache.rhodes_island.milk_in_fridge = {}

    # 结算所有角色携带的母乳
    chara_id_list = list(cache.character_data.keys())
    chara_id_list.append(0)
    for character_id in chara_id_list:
        character_data: game_type.Character = cache.character_data[character_id]

        # 遍历角色背包
        for food_id in character_data.food_bag.copy():
            food: game_type.Food = character_data.food_bag[food_id]
            # 如果是母乳，则转化，并删掉原物品
            if food.milk_ml > 0:
                cache.rhodes_island.materials_resouce[31] += food.milk_ml
                all_milk += food.milk_ml
                # print(f"debug {character_data.name}携带的母乳（{food.ml}ml）已转化为罗德岛的母乳")
                del character_data.food_bag[food.uid]

    # 输出提示信息
    if all_milk > 0:
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n今日共有{0}ml母乳未使用，已全部转化为【鲜母乳】\n").format(all_milk)
        now_draw.draw()

    # 检测是否超出仓库容量上限
    if cache.rhodes_island.materials_resouce[31] > cache.rhodes_island.warehouse_capacity:
        cache.rhodes_island.materials_resouce[31] = cache.rhodes_island.warehouse_capacity
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n由于仓库容量不足，【鲜母乳】已达上限数量{0}\n").format(cache.rhodes_island.warehouse_capacity)
        now_draw.draw()


def settle_semen():
    """
    结算精液转化
    """

    today_semen = cache.rhodes_island.total_semen_count
    cache.rhodes_island.materials_resouce[12] += today_semen
    cache.rhodes_island.total_semen_count = 0

    # 输出提示信息
    if today_semen:
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n今日共射出{0}ml精液，已全部转化为【矿石病药材】\n").format(today_semen)
        now_draw.draw()

    # 检测是否超出仓库容量上限
    if cache.rhodes_island.materials_resouce[12] > cache.rhodes_island.warehouse_capacity:
        cache.rhodes_island.materials_resouce[12] = cache.rhodes_island.warehouse_capacity
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n由于仓库容量不足，【矿石病药材】已达上限数量{0}\n").format(cache.rhodes_island.warehouse_capacity)
        now_draw.draw()


def settle_office_work():
    """
    结算公务
    """

    now_work = cache.rhodes_island.office_work
    all_facility_level = 0
    # 遍历全设施，获取等级的和
    for facility_cid in cache.rhodes_island.facility_level:
        all_facility_level += cache.rhodes_island.facility_level[facility_cid]
    # 总工作量为设施等级和*10+干员数量
    all_work = all_facility_level * 10 + len(cache.npc_id_got)
    # 根据当前剩余工作量和总工作量的比例，计算效率
    effectiveness_change = ((all_work / 2) - now_work) / all_work * 100
    if effectiveness_change > 0:
        effectiveness_change *= 2
    # 计算设施损坏
    max_damage_down = 0
    for facility_str in cache.rhodes_island.facility_damage_data:
        if max_damage_down < cache.rhodes_island.facility_damage_data[facility_str]:
            max_damage_down = cache.rhodes_island.facility_damage_data[facility_str]
    # 如果没有设备出现严重损坏，则增加全局效率
    if max_damage_down < 5:
        effectiveness_change += 5
    # 否则减少全局效率
    else:
        effectiveness_change -= max_damage_down
    # 结算能源系统
    # from Script.UI.Panel import manage_power_system_panel
    # shortage_ratio, text = manage_power_system_panel.settle_power_system(draw_flag=True)
    # # 如果能源系统出现供电不足，则降低效率
    # effectiveness_change -= shortage_ratio / 2
    cache.rhodes_island.effectiveness = 100 + int(effectiveness_change)
    # 效率不会小于50，也不会大于200
    cache.rhodes_island.effectiveness = min(cache.rhodes_island.effectiveness,200)
    cache.rhodes_island.effectiveness = max(cache.rhodes_island.effectiveness,50)
    # 保留一位小数
    cache.rhodes_island.effectiveness = round(cache.rhodes_island.effectiveness,1)
    # 取0.3~0.7的随机数，作为新增的工作量
    add_work = random.randint(30,70) / 100 * all_work
    # 把新增的工作量加入当前剩余工作量
    cache.rhodes_island.office_work += add_work
    # 工作量不会小于0，也不会大于总工作量
    cache.rhodes_island.office_work = min(cache.rhodes_island.office_work,all_work)
    cache.rhodes_island.office_work = max(cache.rhodes_island.office_work,0)
    # 输出提示信息
    now_draw_text = _("\n今日剩余待处理公务量为{0}，").format(now_work)
    if max_damage_down < 5:
        now_draw_text += _("且各区块设施运行基本正常，")
    else:
        now_draw_text += _("且部分区块设施出现较大故障，")
    # if shortage_ratio == 0:
    #     now_draw_text += _("能源系统供电充足，")
    # else:
    #     now_draw_text += _("但能源系统出现供电不足，")
    now_draw_text += _("因此今日罗德岛的各设施的总效率为{0}%\n").format(cache.rhodes_island.effectiveness)
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = now_draw_text
    now_draw.draw()


def settle_income():
    """
    结算收入
    """
    from Script.UI.Panel import achievement_panel

    # 计算医疗部收入
    today_cure_income = int(cache.rhodes_island.cure_income)
    # 计算设施损坏
    damage_down = 0
    for facility_str in cache.rhodes_island.facility_damage_data:
        if '医疗' in facility_str:
            damage_down = cache.rhodes_island.facility_damage_data[facility_str] * 2
    # 计算总调整值
    adjust = (cache.rhodes_island.effectiveness - damage_down) / 100
    # 计算总收入
    today_all_income = int(today_cure_income * adjust)
    # 转化为龙门币
    cache.rhodes_island.materials_resouce[1] += today_all_income

    # 刷新新病人数量，已治愈病人数量和治疗收入归零
    cache.rhodes_island.patient_now = random.randint(int(cache.rhodes_island.patient_max / 2), cache.rhodes_island.patient_max)
    cache.rhodes_island.patient_cured = 0
    cache.rhodes_island.cure_income = 0
    cache.rhodes_island.all_income = 0

    # 输出提示信息
    now_draw_text = "\n"
    if damage_down:
        now_draw_text += _("医疗部设施损坏，效率降低{0}%\n").format(damage_down)
    now_draw_text += _("今日罗德岛总收入为： 医疗部收入{0}，乘以效率后最终收入为{1}，已全部转化为龙门币\n").format(today_cure_income, today_all_income)
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = now_draw_text
    now_draw.draw()

    # 结算龙门币成就
    achievement_panel.achievement_flow(_("龙门币"))

def settle_pink_certificate():
    """
    结算粉红凭证
    """

    # 根据好感度结算粉红凭证增加
    pink_certificate_add = int(cache.rhodes_island.total_favorability_increased / 100)
    pink_certificate_add = max(pink_certificate_add, 0)
    cache.rhodes_island.materials_resouce[4] += pink_certificate_add
    # 结算陷落角色提供的的粉红凭证
    cache.rhodes_island.materials_resouce[4] += cache.rhodes_island.week_fall_chara_pink_certificate_add
    # 输出提示信息
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n今日全角色总好感度上升为：{0}，折合为 {1} 粉红凭证\n").format(int(cache.rhodes_island.total_favorability_increased), pink_certificate_add)
    if cache.rhodes_island.week_fall_chara_pink_certificate_add:
        now_draw.text += _("本周全陷落角色提供的粉红凭证为：{0}\n").format(cache.rhodes_island.week_fall_chara_pink_certificate_add)
    now_draw.draw()
    # 清零计数
    cache.rhodes_island.total_favorability_increased = 0
    cache.rhodes_island.week_fall_chara_pink_certificate_add = 0


def draw_todo():
    """
    绘制待办事项
    """
    from Script.UI.Panel import manage_assembly_line_panel, agriculture_production_panel, invite_visitor_panel, manage_power_system_panel

    # 如果系统设置中关闭了待办事项，直接返回
    if cache.all_system_setting.draw_setting[5] == 0:
        return

    draw_text = ""

    # 供电是否不足
    power_generation = manage_power_system_panel.get_theoretical_power_generation()
    power_consumption = manage_power_system_panel.get_theoretical_power_consumption()
    # if power_generation < power_consumption:
    #     draw_text += _("  当前供电不足，可能影响基地正常运转\n")

    # 是否有已招募待确认的干员
    if len(cache.rhodes_island.recruited_id):
        draw_text += _("  当前有干员已招募，等待确认\n")

    # 是否有人正在等待体检
    if len(cache.rhodes_island.waiting_for_exam_operator_ids):
        draw_text += _("  当前有干员正在体检科等待体检\n")

    # 流水线生产是否正常
    un_normal, now_text = manage_assembly_line_panel.settle_assembly_line(draw_flag=False)
    if un_normal:
        draw_text += now_text[1:] + ' '

    # 农业生产是否正常
    un_normal, now_text = agriculture_production_panel.settle_agriculture_line(draw_flag=False)
    if un_normal:
        draw_text += now_text[1:] + ' '

    # 检查今日是否有访客离开
    departing_visitors = invite_visitor_panel.get_today_departing_visitors()
    if len(departing_visitors):
        draw_text += _("  今日有访客要离开罗德岛，且其留下意愿较低\n")

    # 如果有待办事项，输出待办事项
    if draw_text:
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = '\n' + draw_text
        now_draw.style = "gold_enrod"
        now_draw.draw()


def find_facility_damage():
    """
    检查设施损坏
    """
    tem_data = cache.rhodes_island.facility_damage_data.copy()
    # 去掉已经有人在修理的地点
    for character_id in cache.rhodes_island.maintenance_place:
        if cache.rhodes_island.maintenance_place[character_id] in tem_data:
            tem_data.pop(cache.rhodes_island.maintenance_place[character_id])
    target_scene_str = ''
    # 如果当前有损坏地点，则根据每个地点的数值大小作为权重选择一个
    if len(tem_data):
        # 计算总权重
        total_weight = 0
        for place_str in tem_data:
            total_weight += tem_data[place_str]
        # 随机一个数
        rand_num = random.randint(1, total_weight)
        # 遍历地点，减去权重，当权重小于0时，选中该地点
        for place_str in tem_data:
            rand_num -= tem_data[place_str]
            if rand_num <= 0:
                target_scene_str = place_str
                break
    # 否则随机选一个地点
    if not target_scene_str:
        # 指定的地点需要是可进入的
        while 1:
            target_scene_str = random.choice(constant.place_data["Room"])
            close_type = map_handle.judge_scene_accessible(target_scene_str,0,draw_flag=False)
            if close_type == "open":
                break
    return target_scene_str
