import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise_place, attr_calculation
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏内缓存数据 """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def get_base_zero() -> dict:
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
            for room_id in  game_config.config_facility_open:
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


def update_base_resouce_newday():
    """
    刷新基地资源数据\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.UI.Panel import invite_visitor_panel, aromatherapy_panel, agriculture_production_panel, manage_assembly_line_panel

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
    # 刷新香薰疗愈次数
    aromatherapy_panel.settle_aromatherapy_sessions()
    # 结算粉红凭证
    settle_pink_certificate()


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
        if handle_premise_place.handle_in_library(id):
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
    # 总工作量为设施等级和*10
    all_work = all_facility_level * 10
    # 根据当前剩余工作量和总工作量的比例，计算效率
    effectiveness_change = ((all_work / 2) - now_work) / all_work * 100
    if effectiveness_change > 0:
        effectiveness_change *= 2
    cache.rhodes_island.effectiveness = 100 + effectiveness_change
    # 效率不会小于50，也不会大于200
    cache.rhodes_island.effectiveness = min(cache.rhodes_island.effectiveness,200)
    cache.rhodes_island.effectiveness = max(cache.rhodes_island.effectiveness,50)
    # 取0.3~0.7的随机数，作为新增的工作量
    add_work = random.randint(30,70) / 100 * all_work
    # 把新增的工作量加入当前剩余工作量
    cache.rhodes_island.office_work += add_work
    # 工作量不会小于0，也不会大于总工作量
    cache.rhodes_island.office_work = min(cache.rhodes_island.office_work,all_work)
    cache.rhodes_island.office_work = max(cache.rhodes_island.office_work,0)
    # 输出提示信息
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n今日剩余待处理公务量为{0}，因此今日罗德岛的各设施的总效率为{1}%\n").format(now_work, cache.rhodes_island.effectiveness)
    now_draw.draw()


def settle_income():
    """
    结算收入
    """

    # 计算医疗部收入
    today_cure_income = int(cache.rhodes_island.cure_income)
    # 计算总收入
    today_all_income = int(today_cure_income * cache.rhodes_island.effectiveness / 100)
    # 转化为龙门币
    cache.rhodes_island.materials_resouce[1] += today_all_income

    # 刷新新病人数量，已治愈病人数量和治疗收入归零
    cache.rhodes_island.patient_now = random.randint(cache.rhodes_island.patient_max / 2,cache.rhodes_island.patient_max)
    cache.rhodes_island.patient_cured = 0
    cache.rhodes_island.cure_income = 0
    cache.rhodes_island.all_income = 0

    # 输出提示信息
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n今日罗德岛总收入为： 医疗部收入{0}，乘以效率后最终收入为{1}，已全部转化为龙门币\n").format(today_cure_income, today_all_income)
    now_draw.draw()


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
