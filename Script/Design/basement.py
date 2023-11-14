import random
from Script.Core import (
    cache_control,
    game_type,
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
        if facility_name == "动力区":
            cache.rhodes_island.power_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化仓库容量
        elif facility_name == "仓储区":
            cache.rhodes_island.warehouse_capacity = game_config.config_facility_effect[facility_cid].effect
        # 初始化干员人数上限
        elif facility_name == "宿舍区":
            cache.rhodes_island.people_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化生活娱乐区设施数量上限
        elif facility_name == "生活娱乐区":
            cache.rhodes_island.life_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化患者人数上限，并刷新当天患者人数
        elif facility_name == "医疗部":
            cache.rhodes_island.patient_max = game_config.config_facility_effect[facility_cid].effect
            cache.rhodes_island.patient_now = random.randint(1,cache.rhodes_island.patient_max)
        # 初始化科研区设施数量上限
        elif facility_name == "科研部":
            cache.rhodes_island.research_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化商店数量上限
        elif facility_name == "贸易区":
            cache.rhodes_island.shop_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化战斗时干员数量上限
        elif facility_name == "指挥室":
            cache.rhodes_island.soldier_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化招募条
        elif facility_name == "文职部":
            if 0 not in cache.rhodes_island.recruit_now:
                cache.rhodes_island.recruit_now[0] = 0
            if level >= 3 and 1 not in cache.rhodes_island.recruit_now:
                cache.rhodes_island.recruit_now[1] = 0
            if level >= 5 and 2 not in cache.rhodes_island.recruit_now:
                cache.rhodes_island.recruit_now[2] = 0
        elif facility_name == "制造加工区":
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

    # 结算流水线
    settle_assembly_line(newdayflag=True)
    # 结算访客抵达和离开
    calculate_visitor_arrivals_and_departures()

    # 输出收入合计
    now_draw.text = f"\n今日罗德岛总收入为： 医疗部收入{cache.rhodes_island.cure_income} = {cache.rhodes_island.all_income}\n"
    now_draw.draw()

    # 刷新新病人数量，已治愈病人数量和治疗收入归零
    cache.rhodes_island.patient_now = random.randint(1,cache.rhodes_island.patient_max)
    cache.rhodes_island.patient_cured = 0
    cache.rhodes_island.cure_income = 0
    cache.rhodes_island.all_income = 0

    # 输出好感度合计与粉红凭证增加
    pink_certificate_add = int(cache.rhodes_island.total_favorability_increased / 100)
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = f"\n今日全角色总好感度上升为： {int(cache.rhodes_island.total_favorability_increased)}，折合为{pink_certificate_add}粉红凭证\n"
    now_draw.draw()
    # 清零好感度合计计数
    cache.rhodes_island.total_favorability_increased = 0


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
    for id in cache.npc_id_got:
        character_data = cache.character_data[id]

        # 如果干员有职位，将干员加入对应职位集合
        if character_data.work.work_type:
            cache.rhodes_island.all_work_npc_set[character_data.work.work_type].add(id)
            cache.rhodes_island.work_people_now += 1
        else:
            cache.rhodes_island.all_work_npc_set[0].add(id)
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

                now_text = f"\n 流水线{assembly_line_id}:"
                now_text += f"上次结算是{cache.rhodes_island.assembly_line[assembly_line_id][4]}时，到现在已过{max_time}小时，"
                if produce_num < produce_num_max:
                    now_text += f"由于原料不足，最大可以生产{produce_num}个，实际"
                now_text += f"共生产了{produce_num}个{game_config.config_resouce[product_id].name}"
                # 不会超过仓库容量
                if cache.rhodes_island.materials_resouce[product_id] > cache.rhodes_island.warehouse_capacity:
                    cache.rhodes_island.materials_resouce[product_id] = cache.rhodes_island.warehouse_capacity
                    now_text += f"，由于仓库容量不足，{game_config.config_resouce[product_id].name}已达上限数量{cache.rhodes_island.warehouse_capacity}"
                now_text += f"\n"
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                now_draw.text = now_text
                now_draw.draw()

        # 重置收菜时间
        cache.rhodes_island.assembly_line[assembly_line_id][4] = cache.game_time.hour


def check_facility_open():
    """
    判断是否有空闲客房
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


def calculate_visitor_arrivals_and_departures():
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
        calculate_random_visitor_arrivals()

    # 根据时间而产生的访客
    add_day = game_time.count_day_for_datetime(cache.rhodes_island.last_visitor_time, cache.game_time)
    visitor_come_possibility = add_day * 3
    if random.randint(1, 100) <= visitor_come_possibility:
        # 刷新访客来访时间
        cache.rhodes_island.last_visitor_time = cache.game_time
        calculate_random_visitor_arrivals()

    # 访客离开
    # 遍历全部访客
    now_visitor_id_list = list(cache.rhodes_island.visitor_info.keys())
    for visitor_id in now_visitor_id_list:
        character_data: game_type.Character = cache.character_data[visitor_id]
        # 判断是否已经超过停留时间
        if game_time.judge_date_big_or_small(cache.game_time, cache.rhodes_island.visitor_info[visitor_id]):
            # 计算访客留下概率
            _, _, stay_posibility = character.calculation_instuct_judege(0, visitor_id, "访客留下")
            # 遍历所有留下态度
            for attitude_id in game_config.config_visitor_stay_attitude:
                attitude_data = game_config.config_visitor_stay_attitude[attitude_id]
                if stay_posibility >= attitude_data.rate:
                    continue
                # 获得留下态度对应的文本
                stay_text = attitude_data.name
                break
            now_draw.text = f"\n 访客{character_data.name}预定的停留期限到了，她当前的留下意愿为：【{stay_text}】"
            # 随机计算访客是否留下
            if random.random() < stay_posibility:
                # 访客留下
                character_handle.visitor_to_operator(visitor_id)
                # 输出提示信息
                now_draw.text += f"\n ○{character_data.name}决定放弃离开，留在罗德岛成为一名正式干员\n"
                now_draw.draw()
            else:
                # 访客离开
                character_handle.visitor_leave(visitor_id)
                # 输出提示信息
                now_draw.text += f"\n ●{character_data.name}打包好行李，离开了罗德岛\n"
                now_draw.draw()


def calculate_random_visitor_arrivals():
    """
    结算随机访客抵达和离开
    """
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.style = "gold_enrod"

    # 判断是否有空闲客房
    if not check_facility_open():
        # 输出提示信息
        now_draw.text = f"\n ●由于没有空闲的客房，罗德岛没有接待到一名新抵达的访客\n"
        now_draw.draw()
    else:
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
        visitor_id = random.choice(now_country_npc_id_list)
        # 处理获得新访客
        character_handle.get_new_character(visitor_id, True)
        # 输出提示信息
        now_draw.text = f"\n ○{cache.character_data[visitor_id].name}作为临时访客抵达了罗德岛\n"
        now_draw.draw()
