import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise, attr_calculation, character_handle, game_time, character
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
    base_data.assembly_line[0] = [0,set(),0,0,0]

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
            if game_config.config_facility_open[open_cid].zone_cid == facility_cid:
                # print(f"debug zone_cid = {game_config.config_facility_open[open_cid].zone_cid}")
                # print(f"debug facility_cid = {facility_cid}")
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
            cache.rhodes_island.patient_now = random.randint(cache.rhodes_island.patient_max / 2,cache.rhodes_island.patient_max)
        # 初始化科研区设施数量上限
        elif facility_name == _("科研部"):
            cache.rhodes_island.research_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化商店数量上限
        elif facility_name == _("贸易区"):
            cache.rhodes_island.shop_max = game_config.config_facility_effect[facility_cid].effect
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
            for room_id in cache.rhodes_island.facility_open:
                # 跳过非客房
                if room_id <= 1200 or room_id >= 1300:
                    continue
                # 跳过未开放的客房
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

    now_draw = draw.WaitDraw()
    now_draw.width = window_width

    # 结算公务工作
    settle_office_work()
    # 结算精液转化
    settle_semen()
    # 结算母乳转化
    settle_milk()
    # 结算流水线
    settle_assembly_line(newdayflag=True)
    # 结算农业生产
    settle_agriculture_line()
    # 结算访客抵达和离开
    settle_visitor_arrivals_and_departures()
    # 结算收入
    settle_income()
    # 刷新香薰疗愈次数
    settle_aromatherapy_sessions()
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
                # 未分配则分配
                if select_index == -1:
                    line_id_list = list(cache.rhodes_island.recruit_line.keys())
                    select_index = random.choice(line_id_list)
                    cache.rhodes_island.recruit_line[select_index][2].add(chara_id)

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


def check_random_borrow_book(character_id):
    """
    检查角色是否有借书，有的话跳过，没有的话随机借一本书
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 已借书则跳过
    if len(character_data.entertainment.borrow_book_id_set):
        return 1
    # 未借书则随机借书
    else:
        # 遍历获得所有没借的书id
        recommend_book_id_set,book_id_set = [],[]
        for book_id in cache.rhodes_island.book_borrow_dict:
            # 未被借出则加入book_id_set
            if cache.rhodes_island.book_borrow_dict[book_id] == -1:
                book_id_set.append(book_id)
                # 如果类型在推荐列表里，则加入recommend_book_id_set
                if game_config.config_book[book_id].type in cache.rhodes_island.recommend_book_type_set:
                    recommend_book_id_set.append(book_id)
        # 如果推荐列表有书，则有一半的概率在推荐列表里借书，否则在全列表里借书
        if len(recommend_book_id_set) and random.randint(0,1) == 1:
            borrow_book_id = random.choice(recommend_book_id_set)
        else:
            borrow_book_id = random.choice(book_id_set)
        cache.rhodes_island.book_borrow_dict[borrow_book_id] = character_id
        character_data.entertainment.borrow_book_id_set.add(borrow_book_id)
        # print(f"debug {character_data.name}借了书{borrow_book_id}")
        return 0

def check_return_book(character_id):
    """
    检查并决定是否归还当前书籍
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 未借书则跳过
    if len(character_data.entertainment.borrow_book_id_set) == 0:
        return 0
    # 已借书则d100和还书概率比大小
    else:
        return_d100 = random.randint(1,100)
        # 小于还书概率则还书
        # print(f"debug return_d100 = {return_d100},book_return_possibility = {character_data.entertainment.book_return_possibility}")
        if return_d100 < character_data.entertainment.book_return_possibility:
            for book_id in character_data.entertainment.borrow_book_id_set:
                cache.rhodes_island.book_borrow_dict[book_id] = -1
                character_data.entertainment.borrow_book_id_set.discard(book_id)
                # print(f"debug {character_data.name}还了书{book_id}")
                return 1


def settle_assembly_line(newdayflag = False):
    """
    结算流水线的生产
    """
    

    # 遍历流水线
    for assembly_line_id in cache.rhodes_island.assembly_line:
        now_formula_id = cache.rhodes_island.assembly_line[assembly_line_id][0]
        if now_formula_id != 0:
            formula_data_now = game_config.config_productformula_data[now_formula_id]
            formula_now = game_config.config_productformula[now_formula_id]
            product_id = formula_now.product_id
            # 最大生产时间
            if newdayflag:
                max_time = 24 + cache.game_time.hour - cache.rhodes_island.assembly_line[assembly_line_id][4]
            else:
                max_time = cache.game_time.hour - cache.rhodes_island.assembly_line[assembly_line_id][4]
            # 生产效率
            produce_effect = cache.rhodes_island.assembly_line[assembly_line_id][2]
            # 公务的总效率
            produce_effect *= cache.rhodes_island.effectiveness / 100
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect / 100)
            produce_num = produce_num_max
            # print(f"debug 流水线{assembly_line_id},max_time = {max_time}，produce_effect = {produce_effect}，最大生产数为{produce_num_max}")

            # 遍历全部原料，判断是否足够
            for need_type in formula_data_now:
                # 当前种类的原料最大生产数
                now_type_max_produce_num = cache.rhodes_island.materials_resouce[need_type] // formula_data_now[need_type]
                # 不超过总最大生产数
                produce_num = min(produce_num,now_type_max_produce_num)
            # print(f"debug 流水线{assembly_line_id}，实际生产数为{produce_num}")

            # 结算实际生产
            if produce_num > 0:
                # 结算实际消耗的原料
                for need_type in formula_data_now:
                    cache.rhodes_island.materials_resouce[need_type] -= produce_num * formula_data_now[need_type]
                # 结算实际生产的产品
                cache.rhodes_island.materials_resouce[product_id] += produce_num

                now_text = _(f"\n 流水线{assembly_line_id}:")
                now_text += _(f"上次结算是{cache.rhodes_island.assembly_line[assembly_line_id][4]}时，到现在已过{max_time}小时，")
                if produce_num < produce_num_max:
                    now_text += _(f"由于原料不足，最大可以生产{produce_num}个，实际")
                now_text += _(f"共生产了{produce_num}个{game_config.config_resouce[product_id].name}")
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[product_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[product_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _(f"，由于仓库容量不足，{game_config.config_resouce[product_id].name}已达上限数量{cache.rhodes_island.warehouse_capacity}")
                now_text += f"\n"
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                now_draw.text = now_text
                now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.assembly_line[assembly_line_id][4] = cache.game_time.hour


def settle_agriculture_line():
    """
    结算农业的生产
    """
    # print("debug 开始结算农业生产")
    # 遍历药田
    for agriculture_line_id in cache.rhodes_island.herb_garden_line:
        resouce_id = cache.rhodes_island.herb_garden_line[agriculture_line_id][0]
        # print(f"debug 药田{agriculture_line_id}，种植的作物id为{resouce_id}")
        if resouce_id != 0:
            resouce_data = game_config.config_resouce[resouce_id]

            # 每天生产一次
            max_time = 10
            produce_effect = cache.rhodes_island.herb_garden_line[agriculture_line_id][2]
            # 公务的总效率
            produce_effect *= cache.rhodes_island.effectiveness / 100
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect / 100)
            produce_num = produce_num_max
            # print(f"debug 药田{agriculture_line_id},max_time = {max_time}，produce_effect = {produce_effect}，最大生产数为{produce_num_max}")

            # 结算实际生产
            if produce_num > 0:
                # 结算实际生产的产品
                cache.rhodes_island.materials_resouce[resouce_id] += produce_num

                now_text = _(f"\n今日药田共生产了{produce_num}个{resouce_data.name}")
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[resouce_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[resouce_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _(f"，由于仓库容量不足，{resouce_data.name}已达上限数量{cache.rhodes_island.warehouse_capacity}")
                now_text += f"\n"
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                now_draw.text = now_text
                now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.herb_garden_line[agriculture_line_id][4] = cache.game_time.hour

    # 遍历温室
    for agriculture_line_id in cache.rhodes_island.green_house_line:
        resouce_id = cache.rhodes_island.green_house_line[agriculture_line_id][0]
        # print(f"debug 温室{agriculture_line_id}，种植的作物id为{resouce_id}")
        if resouce_id != 0:
            resouce_data = game_config.config_resouce[resouce_id]

            # 每天生产一次
            max_time = 10
            produce_effect = cache.rhodes_island.green_house_line[agriculture_line_id][2]
            # 公务的总效率
            produce_effect *= cache.rhodes_island.effectiveness / 100
            # 计算最大生产数
            produce_num_max = int(max_time * produce_effect / 100)
            produce_num = produce_num_max
            # print(f"debug 温室{agriculture_line_id},max_time = {max_time}，produce_effect = {produce_effect}，最大生产数为{produce_num_max}")

            # 结算实际生产
            if produce_num > 0:
                # 结算实际生产的产品
                cache.rhodes_island.materials_resouce[resouce_id] += produce_num

                now_text = _(f"\n今日温室共生产了{produce_num}个{resouce_data.name}")
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[resouce_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[resouce_id] = cache.rhodes_island.warehouse_capacity
                    now_text += _(f"，由于仓库容量不足，{resouce_data.name}已达上限数量{cache.rhodes_island.warehouse_capacity}")
                now_text += f"\n"
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                now_draw.text = now_text
                now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.green_house_line[agriculture_line_id][4] = cache.game_time.hour


def update_recruit():
    """刷新招募栏位"""

    # 遍历全招募栏
    for recruit_line_id in cache.rhodes_island.recruit_line:

        # 如果超过100则进行结算
        if cache.rhodes_island.recruit_line[recruit_line_id][0] >= 100:
            cache.rhodes_island.recruit_line[recruit_line_id][0] = 0

            # 招募策略
            recruitment_strategy = cache.rhodes_island.recruit_line[recruit_line_id][1]

            # 绘制信息
            now_draw = draw.WaitDraw()
            now_draw.width = width
            now_draw.style = "gold_enrod"

            # 开始获得招募npc的id
            wait_id_set = []
            for i in range(len(cache.npc_tem_data)):
                chara_id = i + 1
                # 本地招募
                if recruitment_strategy == 0:
                    if chara_id not in cache.character_data:
                        continue
                    character_data = cache.character_data[chara_id]
                    # 筛选出未招募且出生地是当前所在地的角色
                    if chara_id in cache.npc_id_got or character_data.relationship.birthplace != cache.rhodes_island.current_location[0]:
                        continue
                    else:
                            wait_id_set.append(chara_id)
                # 全泰拉招募
                # TODO 当前其他招聘策略均由全泰拉招聘代替，需要实装
                elif recruitment_strategy == 1 or recruitment_strategy in {2,3,4}:
                    # 筛选出未招募的角色
                    if chara_id not in cache.npc_id_got:
                        wait_id_set.append(chara_id)
            if len(wait_id_set):
                choice_id = random.choice(wait_id_set)
                cache.rhodes_island.recruited_id.add(choice_id)

                now_draw.text = _(f"\n\n   ※ 招募到了新的干员，请前往博士办公室确认 ※\n\n")
                now_draw.draw()
            else:
                now_draw.text = _(f"\n\n   ※ 当前招募策略无可招募npc，招募失败 ※\n\n")
                now_draw.draw()
                cache.rhodes_island.recruit_line[recruit_line_id][0] = 100


def update_invite_visitor():
    """刷新邀请访客栏位"""

    # 未选择邀请目标则跳过
    if cache.rhodes_island.invite_visitor[0] == 0:
        return

    # 如果超过100则进行结算
    if cache.rhodes_island.invite_visitor[1] >= 100:

        # 成功邀请时
        if settle_visitor_arrivals(visitor_id = cache.rhodes_island.invite_visitor[0]):
            cache.rhodes_island.invite_visitor[0] = 0
            cache.rhodes_island.invite_visitor[1] = 0


def check_facility_open():
    """
    判断是否有空闲客房，暂时没有用
    """
    # 遍历全部客房
    for room_id in cache.rhodes_island.facility_open:
        # 跳过非客房
        if room_id <= 1200 or room_id >= 1300:
            continue
        # 跳过未开放的客房
        if not cache.rhodes_island.facility_open[room_id]:
            continue
        room_name = game_config.config_facility_open[room_id].name
        # 遍历全部访客
        have_visitor_flag = False
        for chara_id in cache.rhodes_island.visitor_info:
            # 如果该房间已经有访客，则跳过
            if cache.character_data[chara_id].dormitory == room_name:
                have_visitor_flag = True
                break
        if have_visitor_flag:
            continue
        # 发现没有人住的房间，返回True
        else:
            return True
    # 如果没有空闲客房，则返回False
    return False


def settle_visitor_arrivals_and_departures():
    """
    结算访客抵达和离开
    """
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.style = "gold_enrod"

    # 因罗德岛移动而产生的访客
    if cache.rhodes_island.base_move_visitor_flag:
        # 将flag重置为False
        cache.rhodes_island.base_move_visitor_flag = False
        settle_visitor_arrivals()

    # 根据时间而产生的访客
    add_day = game_time.count_day_for_datetime(cache.rhodes_island.last_visitor_time, cache.game_time)
    visitor_come_possibility = add_day * 3
    if random.randint(1, 100) <= visitor_come_possibility:
        # 刷新访客来访时间
        cache.rhodes_island.last_visitor_time = cache.game_time
        settle_visitor_arrivals()

    # 访客离开
    # 遍历全部访客
    now_visitor_id_list = list(cache.rhodes_island.visitor_info.keys())
    for visitor_id in now_visitor_id_list:
        character_data: game_type.Character = cache.character_data[visitor_id]
        # 判断是否已经超过停留时间
        if game_time.judge_date_big_or_small(cache.game_time, cache.rhodes_island.visitor_info[visitor_id]):
            # 计算访客留下概率
            tem_1, tem_2, stay_posibility = character.calculation_instuct_judege(0, visitor_id, _("访客留下"))
            # 遍历所有留下态度
            for attitude_id in game_config.config_visitor_stay_attitude:
                attitude_data = game_config.config_visitor_stay_attitude[attitude_id]
                if stay_posibility >= attitude_data.rate:
                    continue
                # 获得留下态度对应的文本
                stay_text = attitude_data.name
                break
            now_draw.text = _(f"\n 访客【{character_data.name}】预定的停留期限到了，她当前的留下意愿为：【{stay_text}】")
            # 随机计算访客是否留下
            if random.random() < stay_posibility:
                # 访客留下
                character_handle.visitor_to_operator(visitor_id)
                # 输出提示信息
                now_draw.text += _(f"\n ○【{character_data.name}】决定放弃离开，留在罗德岛成为一名正式干员\n")
                now_draw.draw()
            else:
                # 访客离开
                character_handle.visitor_leave(visitor_id)
                # 输出提示信息
                now_draw.text += _(f"\n ●【{character_data.name}】打包好行李，离开了罗德岛\n")
                now_draw.draw()


def settle_visitor_arrivals(visitor_id = 0):
    """
    结算访客抵达
    visitor_id = 0 时，随机抽取一名访客
    return 0 时，没有访客抵达
    return 1 时，有访客抵达
    """
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.style = "gold_enrod"

    # 判断是否有空闲客房
    if len(cache.rhodes_island.visitor_info) >= cache.rhodes_island.visitor_max:
        # 输出提示信息
        now_draw.text = _(f"\n ●由于没有空闲的客房，罗德岛没有接待到一名新抵达的访客\n")
        now_draw.draw()
        return 0
    else:
        # 随机抽取一名访客
        if visitor_id == 0:
            # 未招募的干员id
            not_recruit_npc_id_list = [id for id in range(1, len(cache.npc_tem_data) + 1) if id not in cache.npc_id_got]
            # 根据当前基地的位置筛选出同国度且没有招募的干员
            now_country_id = cache.rhodes_island.current_location[0]
            now_country_npc_id_list = []
            # 开始筛选
            for npc_id in not_recruit_npc_id_list:
                if cache.character_data[npc_id].relationship.birthplace == now_country_id:
                    now_country_npc_id_list.append(npc_id)
            # 随机抽取一名访客
            if len(now_country_npc_id_list):
                visitor_id = random.choice(now_country_npc_id_list)
            else:
                return 0
        # 处理获得新访客
        character_handle.get_new_character(visitor_id, True)
        # 输出提示信息
        now_draw.text = _(f"\n ○【{cache.character_data[visitor_id].name}】作为临时访客抵达了罗德岛\n")
        now_draw.draw()
        return 1


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
        now_draw.text = _(f"\n今日共有{all_milk}ml母乳未使用，已全部转化为【鲜母乳】\n")
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
        now_draw.text = _(f"\n今日共射出{today_semen}ml精液，已全部转化为【矿石病药材】\n")
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
    now_draw.text = _(f"\n今日剩余待处理公务量为{now_work}，因此今日罗德岛的各设施的总效率为{cache.rhodes_island.effectiveness}%\n")
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
    now_draw.text = _(f"\n今日罗德岛总收入为： 医疗部收入{today_cure_income}，乘以效率后最终收入为{today_all_income}，已全部转化为龙门币\n")
    now_draw.draw()


def settle_aromatherapy_sessions():
    """
    结算香薰疗愈次数
    """

    level = cache.rhodes_island.facility_level[16]

    # 刷新香薰疗愈次数
    if level >= 5:
        cache.rhodes_island.remaining_aromatherapy_sessions_today = 3
    elif level == 4:
        cache.rhodes_island.remaining_aromatherapy_sessions_today = 2
    elif level <= 3:
        cache.rhodes_island.remaining_aromatherapy_sessions_today = 1


def settle_pink_certificate():
    """
    结算粉红凭证
    """

    # 输出好感度合计与粉红凭证增加
    pink_certificate_add = int(cache.rhodes_island.total_favorability_increased / 100)
    cache.rhodes_island.materials_resouce[4] += pink_certificate_add
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _(f"\n今日全角色总好感度上升为： {int(cache.rhodes_island.total_favorability_increased)}，折合为{pink_certificate_add}粉红凭证\n")
    now_draw.draw()
    # 清零好感度合计计数
    cache.rhodes_island.total_favorability_increased = 0
