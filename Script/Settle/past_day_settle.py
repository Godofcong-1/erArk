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
    pregnancy,
    basement,
)
from Script.UI.Moudle import draw
from Script.UI.Panel import nation_diplomacy_panel, navigation_panel, assistant_panel
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
    from Script.Design import cooking

    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = _("\n已过24点，开始结算各种数据\n\n")
    now_draw.draw()

    # 角色刷新
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        # 处理持有食物变质与过期，并获取过期食物数量
        if cache.all_system_setting.base_setting[10]:
            expired_food_num = cooking.handle_food_deterioration(character_id)
        if expired_food_num > 0 and character_id == 0:
            now_draw.text = _("你持有的{0}个食物因过期变质而自动丢弃了\n").format(expired_food_num)
            now_draw.draw()
        if character_id:
            # 刷新娱乐活动
            handle_npc_ai.get_chara_entertainment(character_id)
            # 刷新生理周期
            pregnancy.update_reproduction_period(character_id)
            # 清零助理服务的flag
            if character_data.sp_flag.morning_salutation == 2 or character_data.assistant_services[5] == 0:
                character_data.sp_flag.morning_salutation = 0
            if character_data.sp_flag.night_salutation == 2 or character_data.assistant_services[6] == 0:
                character_data.sp_flag.night_salutation = 0
            # 清零香薰疗愈的flag
            character_data.sp_flag.aromatherapy = 0
            # 清零食物不对劲的flag
            character_data.sp_flag.find_food_weird = False
            # 根据欲望等级增加欲望值
            character_data.desire_point += random.randint(character_data.ability[33], character_data.ability[33] * 2)
            # 每周一次，如果已陷落则提供粉红凭证
            if cache.game_time.weekday() == 6:
                fall_chara_give_pink_voucher(character_id)

    # 非角色部分
    basement.update_base_resouce_newday() # 更新基地资源
    navigation_panel.judge_arrive() # 判断是否到达目的地
    # 每周一次
    if cache.game_time.weekday() == 6:
        nation_diplomacy_panel.judge_diplomatic_policy() # 结算外交政策
    # 每周一的助理轮换
    if cache.game_time.weekday() == 0 and handle_premise.handle_pl_assistant_change_every_week_on(0):
        assistant_panel.select_random_assistant()
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

