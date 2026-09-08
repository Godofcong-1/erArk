import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    get_text,
)
from Script.Design import (
    game_time,
    handle_premise,
    handle_npc_ai,
    attr_calculation,
    basement,
)
from Script.UI.Moudle import draw
from Script.Config import normal_config

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

def update_new_day():
    """
    新一天的刷新\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.System.Cooking_System import cooking
    from Script.UI.Panel import nation_diplomacy_panel, navigation_panel, assistant_panel
    from Script.System.Pregnancy_System import pregnancy_handle, egg_handle
    from Script.System.Education_System import schedule_template_handle, semester_handle, growth_event_handle
    from Script.System.Official_Event_System import official_event_handle

    from Script.System.Education_System import sex_class_handle

    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = _("\n已过24点，开始结算各种数据\n\n")
    now_draw.draw()

    # 清理过期的临时性技实操课，避免字典随游戏天数无限膨胀并进存档（Plan 22 四期 §7-16）
    # ⚠️ 该函数会跳过 running 为真的那条：下课时间由玩家决定，一节课可以从昨天一直上到今天，
    #    把正在上的这节删掉，下课时就找不到课程数据了（§7-27）
    sex_class_handle.clean_expired_temp_class()

    # 角色刷新
    all_chara_id_set = cache.npc_id_got.copy()
    all_chara_id_set.add(0)  # 包含玩家
    for character_id in all_chara_id_set:
        character_data: game_type.Character = cache.character_data[character_id]
        # 处理持有食物变质与过期，并获取过期食物数量
        if cache.all_system_setting.base_setting.get(10, 1):
            expired_food_num = cooking.handle_food_deterioration(character_id)
            if expired_food_num > 0 and character_id == 0:
                now_draw.text = _("你持有的{0}个食物因过期变质而自动丢弃了\n").format(expired_food_num)
                now_draw.draw()
        # 清零香薰疗愈的flag
        character_data.sp_flag.aromatherapy = 0
        # 清零翘课flag：翘课只翘一天，次日重新按课表走（Plan 22 §3.19）
        if character_data.child_growth is not None:
            character_data.child_growth.skip_class_flag = False
            # 清零见学flag（Plan 22 二期）：见学是「此刻」的状态，跨日一律重判。
            # ⚠️ 这是兜底的第四处清位——AI 整天没跑到那个角色（睡着、H中、被抱走）时，
            #    class_ai 的三处清位一处都摸不着，标记会一直粘着
            character_data.child_growth.follow_mother_flag = False
        if character_id:
            # 全量重算异常位掩码，兜底修复各状态修改点漏刷新导致的过期缓存位（每日一次，开销可忽略）
            handle_premise.refresh_unnormal_flag(character_id)
            # 排卵日结束仍未结算（玩家当天未睡觉）时的兜底：受精判定与排卵结算
            if character_data.pregnancy.ovulation_flag:
                pregnancy_handle.get_fertilization_rate(character_id)
                pregnancy_handle.check_fertilization(character_id)
                egg_handle.check_ovulation(character_id)
            # 刷新娱乐活动
            handle_npc_ai.get_chara_entertainment(character_id)
            # 持有需照料的卵的卵生角色，随机一个娱乐时段替换为照料卵
            egg_handle.replace_entertainment_for_eggs(character_id)
            # 孩子按日程模板改写今日的三个娱乐时段（Plan 22 二期）
            # ⚠️ 必须在上面的 get_chara_entertainment 之后：顺序颠倒会被当天的随机值冲掉
            schedule_template_handle.apply_schedule_for_child(character_id)
            # 刷新生理周期
            pregnancy_handle.update_reproduction_period(character_id)
            # 清零助理服务的flag
            if character_data.sp_flag.morning_salutation == 2 or character_data.assistant_services[5] == 0:
                character_data.sp_flag.morning_salutation = 0
            if character_data.sp_flag.night_salutation == 2 or character_data.assistant_services[6] == 0:
                character_data.sp_flag.night_salutation = 0
            # 清零食物不对劲的flag
            character_data.sp_flag.find_food_weird = False
            # 根据欲望等级增加欲望值
            character_data.desire_point += random.randint(character_data.ability[33], character_data.ability[33] * 2)
            # 每周一次，如果已陷落则提供粉红凭证
            if cache.game_time.weekday() == 6:
                fall_chara_give_pink_voucher(character_id)

    # 非角色部分
    # 学期切换（Plan 22 一期 §3.13）：一个季月即一个学期，切季月即切学期，期末给每个在学的女儿出成绩单
    # ⚠️ 必须排在上面的角色刷新之后：出勤数要等昨天的课全部结算完才算数
    # ⚠️ settle_semester_change 靠逐孩比对学期号来判定，本身幂等，不需要额外的「今天是否已结算」标记
    report_character_list = semester_handle.settle_semester_change()
    if report_character_list:
        growth_event_handle.push_semester_event_for_list(report_character_list)
        now_draw.text = _("\n【学期结束】{0}的成绩单出来了，可以用「检查成绩单」指令查看\n").format(
            "、".join(cache.character_data[one].name for one in report_character_list))
        # ⚠️ now_draw 是本函数复用的同一个对象，改了 style 必须改回来，否则后面所有输出都变成金色
        now_draw.style = "gold_enrod"
        now_draw.draw()
        now_draw.style = "standard"
    basement.update_base_resouce_newday() # 更新基地资源
    navigation_panel.judge_arrive() # 判断是否到达目的地
    # 每周一次
    if cache.game_time.weekday() == 6:
        nation_diplomacy_panel.judge_diplomatic_policy() # 结算外交政策
        nation_diplomacy_panel.settle_all_country_infection_rate() # 结算全国度的源石病感染率变化
    # 每周一的助理轮换
    if cache.game_time.weekday() == 0 and handle_premise.handle_pl_assistant_change_every_week_on(0):
        assistant_panel.select_random_assistant()
    # 按前提筛选并入队今日的公务事件（Plan 23）。⚠️ 必须在上面的角色刷新之后：
    # 事件前提要读当天刷新过的状态，顺序颠倒会拿到昨天的数据
    official_event_handle.check_new_day_official_event()
    # 清空今日触发事件记录
    cache.today_taiggered_event_record = set()
    # 更新游戏时间
    cache.pre_game_time = cache.game_time
    # 每日指令输入记录
    cache.daily_intsruce.append('\n\n' + game_time.get_date_until_day() + '\n\n')

def fall_chara_give_pink_voucher(character_id: int):
    """
    陷落角色给予粉红凭证\n
    Keyword arguments:\n
    character_id -- 角色id
    """
    # 如果已陷落则给予粉红凭证
    character_fall_level = attr_calculation.get_character_fall_level(character_id)
    if character_fall_level <= 3:
        cache.rhodes_island.week_fall_chara_pink_certificate_add += character_fall_level * 20
    else:
        cache.rhodes_island.week_fall_chara_pink_certificate_add += 100

