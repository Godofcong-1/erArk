import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    get_text,
)
from Script.Design import (
    handle_premise,
    attr_calculation,
    pregnancy,
    handle_talent,
    handle_ability,
)
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config

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

def update_sleep():
    """
    玩家睡觉时的刷新\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.UI.Panel import achievement_panel

    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = _("\n博士入睡，开始结算各种数据\n")
    now_draw.draw()
    id_list = cache.npc_id_got.copy()
    id_list.add(0)

    # 角色刷新
    for character_id in id_list:
        character_data: game_type.Character = cache.character_data[character_id]
        # 结算数值为珠
        settle_character_juel(character_id)
        # 玩家结算
        if character_id == 0:
            sanity_point_grow() # 玩家理智成长
            character_data.eja_point = 0 # 清零射精槽
            assistant_id = character_data.assistant_character_id
            # 对玩家助理结算
            if assistant_id > 0:
                assistant_character_data: game_type.Character = cache.character_data[assistant_id]
                # 如果此时助理在睡眠中，则清零助理晚安问候
                if handle_premise.handle_assistant_night_salutation_on(assistant_id) and handle_premise.handle_action_sleep(assistant_id):
                    assistant_character_data.sp_flag.night_salutation = 0
                # 如果助理的跟随服务已开启，且没有在跟随，则让助理跟随
                if assistant_character_data.sp_flag.is_follow != 1 and handle_premise.handle_not_follow_1(assistant_id):
                    assistant_character_data.sp_flag.is_follow = 1
            # 检查是否有可以升级的能力
            if cache.all_system_setting.base_setting[1]:
                handle_ability.gain_ability(character_id)
            line_feed.draw()
        else:
            # 清零并随机重置生气程度
            character_data.angry_point = random.randrange(1,35)
            # 清零H被撞破的flag
            character_data.action_info.h_interrupt = 0
            # 重置每天第一次见面
            character_data.first_record.day_first_meet = 1
            # 新：改为洗澡时清零（清零污浊状态）
            # character_data.dirty = attr_calculation.get_dirty_zero()
            # 检查并处理受精怀孕部分
            pregnancy.check_all_pregnancy(character_id)
            # 检查是否有可以获得的素质
            handle_talent.gain_talent(character_id,now_gain_type = 3)
            # 检查是否有可以升级的能力
            if cache.all_system_setting.base_setting[2]:
                handle_ability.gain_ability(character_id)
            # 清零H状态
            character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
            # 清零睡奸中醒来状态
            character_data.sp_flag.sleep_h_awake = 0

    # 非角色部分
    cache.pl_sleep_save_flag = True
    # 结算成就
    # achievement_panel.achievement_flow(_("周目"))


def settle_character_juel(character_id: int) -> int:
    """
    校验角色状态并结算为珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for status_id in game_config.config_character_state:
        # print("status_type :",status_type)
        # print("status_id :",status_id)
        # print("game_config.config_character_state[status_id] :",game_config.config_character_state[status_id])
        # print("game_config.config_character_state[status_id].name :",game_config.config_character_state[status_id].name)
        #去掉性别里不存在的状态
        if character_data.sex == 0:
            if status_id in {2, 4, 7, 8}:
                continue
        elif character_data.sex == 1:
            if status_id == 3:
                continue
        status_value = 0
        #获得状态值并清零
        if status_id in character_data.status_data:
            status_value = character_data.status_data[status_id]
            cache.character_data[character_id].status_data[status_id] = 0
            # print("status_value :",status_value)
        #只要状态值不为0就结算为对应珠
        if status_value != 0:
            add_juel = attr_calculation.get_juel(status_value)
            character_data.juel.setdefault(status_id, 0)
            if status_id in [17, 18, 19]:
                character_data.juel[status_id] += add_juel // 4
                character_data.juel[20] += add_juel // 2
            else:
                character_data.juel[status_id] += add_juel
            # juel_text = game_config.config_juel[status_id].name
            # print("宝珠名：",juel_text,"。增加了 :",add_juel)
    # 当反感珠大于0时，计算和其他珠的抵消
    if character_data.juel[20] > 0:
        draw_text = _("\n当前共{0}反发珠，抵消了：").format(character_data.juel[20])
        for i in [15, 10, 11, 12, 13]:
            # 1好意抵消2反发
            if character_data.juel[i] > 0:
                juel_down = min(character_data.juel[20], character_data.juel[i] * 2)
                character_data.juel[20] -= juel_down
                character_data.juel[i] -= juel_down // 2
                draw_text += _(" {0}个{1} ").format(juel_down//2, game_config.config_juel[i].name)
        draw_text += _("，剩余{0}个反发珠\n").format(character_data.juel[20])
        now_draw = draw.NormalDraw()
        now_draw.text = draw_text
        # now_draw.draw()
    return 1


def update_save():
    """
    自动存档\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.Core import save_handle

    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n全部结算完毕，开始自动保存\n")
    # 播放一条提示信息
    info_list = []
    for i in game_config.config_tip_data:
        info_list.append(i)
    info_id = random.choice(info_list)
    info_text = game_config.config_tip_data[info_id].info
    now_draw.text += _("\n请博士在保存时阅读今日的小贴士：\n\n  {0}\n\n\n").format(info_text)
    now_draw.draw()
    save_handle.establish_save("auto")


def sanity_point_grow():
    """
    玩家理智值的自然成长\n
    Keyword arguments:
    无
    """
    character_data: game_type.Character = cache.character_data[0]
    today_cost = character_data.pl_ability.today_sanity_point_cost
    character_data.pl_ability.today_sanity_point_cost = 0
    # 消耗超过90时进行成长
    if today_cost >= 50 and character_data.sanity_point_max < 9999:
        # 成长值为消耗值的1/50，四舍五入取整
        grow_value = round(today_cost / 50)
        character_data.sanity_point_max += grow_value
        character_data.sanity_point_max = min(character_data.sanity_point_max,9999)
        # 绘制说明信息
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n在刻苦的锻炼下，博士理智最大值成长了{0}点\n").format(grow_value)
        now_draw.draw()


def refresh_temp_semen_max():
    """
    刷新临时最大精液量\n
    """
    character_data: game_type.Character = cache.character_data[0]
    now_semen = character_data.semen_point
    # 需要睡眠时长至少大于等于6h
    if now_semen and character_data.behavior.duration >= 360:
        # 最大额外精液量为正常上限的4倍
        character_data.tem_extra_semen_point += int(now_semen / 2)
        character_data.tem_extra_semen_point = min(character_data.tem_extra_semen_point, character_data.semen_point_max * 4)
        # 获得浓厚精液
        if character_data.tem_extra_semen_point >= character_data.semen_point_max * 4:
            character_data.talent[33] = 1
        else:
            character_data.talent[33] = 0
        # 绘制说明信息
        now_draw = draw.NormalDraw()
        now_draw.width = window_width
        draw_text = _("\n在充足的睡眠下，今日未消耗的 {0}ml 精液转化为了 {1}ml 次日额外精液").format(now_semen, int(now_semen / 2))
        if character_data.tem_extra_semen_point >= character_data.semen_point_max * 4:
            draw_text += _("，额外精液量已达上限，并获得了为期一天的[浓厚精液]")
        draw_text += "\n"
        now_draw.text = draw_text
        now_draw.draw()
