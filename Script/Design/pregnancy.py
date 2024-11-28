import math
import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    get_text,
)
from Script.Design import (
    character_handle,
    game_time,
    talk,
    attr_calculation
)
from Script.UI.Moudle import draw
from Script.UI.Panel import sp_event_panel
from Script.Config import game_config, normal_config

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """


def get_fertilization_rate(character_id: int):
    """
    根据当前V精液量计算受精概率
    """

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    draw_text = ""

    semen_count = character_data.dirty.body_semen[7][1]
    semen_level = character_data.dirty.body_semen[7][2]
    now_reproduction = character_data.pregnancy.reproduction_period
    # 基础概率
    now_rate = math.pow(semen_count / 1000,2) * 100 + semen_level * 5

    # 事前避孕药修正
    if character_data.h_state.body_item[11][1]:
        now_rate = 0
        if game_time.judge_date_big_or_small(cache.game_time,character_data.h_state.body_item[11][2]):
            character_data.h_state.body_item[11][1] = False
    # 事后避孕药修正
    if character_data.h_state.body_item[12][1]:
        now_rate = 0
        character_data.h_state.body_item[12][1] = False
    if semen_count > 0:
        # 如果避孕的话绘制信息
        if now_rate == 0:
            draw_text += _("\n在避孕药的影响下，{0}的精子无法受精\n").format(pl_character_data.name)
        # 其他修正
        else:
            # 生理周期修正
            now_rate *= game_config.config_reproduction_period[now_reproduction].type
            # 排卵促进药
            if character_data.h_state.body_item[10][1]:
                new_rate = min(100, now_rate * 5)
                draw_text += _("\n在排卵促进药的影响下，怀孕概率由{0}上升到了{1}%\n").format(character_data.pregnancy.fertilization_rate, new_rate)
                character_data.pregnancy.fertilization_rate = new_rate
                character_data.h_state.body_item[10][1] = False
            # 排卵催眠
            if character_data.hypnosis.force_ovulation:
                new_rate = min(100, now_rate * 5)
                draw_text += _("\n在催眠-强制排卵的影响下，怀孕概率由{0}上升到了{1}%\n").format(character_data.pregnancy.fertilization_rate, new_rate)
                character_data.pregnancy.fertilization_rate = new_rate
                character_data.hypnosis.force_ovulation = False
            # 浓厚精液
            if pl_character_data.talent[33] == 1:
                new_rate = min(100, now_rate * 2)
                draw_text += _("\n在浓厚精液的影响下，怀孕概率由{0}上升到了{1}%\n").format(character_data.pregnancy.fertilization_rate, new_rate)
                character_data.pregnancy.fertilization_rate = new_rate
    character_data.pregnancy.fertilization_rate = now_rate


def check_fertilization(character_id: int):
    """
    根据受精概率并判断是否受精
    """
    character_data: game_type.Character = cache.character_data[character_id]
    draw_text = ""

    # 仅在排卵日进行判定
    if character_data.pregnancy.reproduction_period != 5:
        return 0

    # 消除强制排卵状态
    if character_data.hypnosis.force_ovulation:
        character_data.hypnosis.force_ovulation = False
    # 如果当前已受精，则跳过判断
    for i in {20,21,22}:
        if character_data.talent[i] == 1:
            character_data.pregnancy.fertilization_rate = 0
            return 0

    # 只判断有受精可能的
    if character_data.pregnancy.fertilization_rate:

        # 如果未初潮，则无法受精并触发对话
        if character_data.talent[6] == 1:
            draw_text += _("\n因为{0}还没有迎来初潮，所以精子只能在阴道内徒劳地寻找不存在的卵子，无法完成受精\n").format(character_data.name)

        # 种族是机械的则需要判断是否有生育模组
        elif character_data.race == 2:
            if character_data.talent[171] == 0:
                character_data.pregnancy.fertilization_rate = 0
                draw_text += _("\n{0}是机械体，且未安装生育模组，无法受精\n").format(character_data.name)

        # 正常情况下可以受精
        else:

            # 由随机数判断是否受精
            if random.randint(1,100) <= character_data.pregnancy.fertilization_rate:
                draw_text += "\n※※※※※※※※※\n"
                draw_text += _("\n博士的精子与{0}的卵子结合，成功在子宫里着床了\n").format(character_data.name)
                draw_text += _("\n{0}获得了[受精]\n").format(character_data.name)
                draw_text += "\n※※※※※※※※※\n"
                character_data.talent[20] = 1
                character_data.pregnancy.fertilization_time = cache.game_time
                # 判断是否是无意识妊娠
                if character_data.pregnancy.unconscious_fertilization:
                    character_data.talent[35] = 1
                    draw_text += _("\n{0}从未在有意识下被中出过，因此不会意识到自己已经怀孕了\n").format(character_data.name)
                    draw_text += _("\n{0}获得了[无意识妊娠]\n").format(character_data.name)
                    draw_text += "\n※※※※※※※※※\n"
                # 触发受精的二段行动
                character_data.second_behavior[1311] = 1
            else:
                if character_data.h_state.body_item[11][1] or character_data.h_state.body_item[12][1]:
                    draw_text += _("\n在避孕药的影响下——")
                draw_text += _("\n精子在{0}的阴道中游荡，但未能成功受精\n").format(character_data.name)
                character_data.second_behavior[1312] = 1

        character_data.pregnancy.fertilization_rate = 0
    else:
        if character_data.h_state.body_item[11][1] or character_data.h_state.body_item[12][1]:
            draw_text += _("\n在避孕药的影响下——\n精子在{0}的阴道中游荡，但未能成功受精\n").format(character_data.name)

    # 绘制输出
    talk.must_show_talk_check(character_id)
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = draw_text
    now_draw.draw()


def check_pregnancy(character_id: int):
    """
    判断是否由受精变为怀孕
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是受精状态
    if character_data.talent[20]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.fertilization_time
        past_day = (start_date - end_date).days
        # 90天在游戏内实际体验是30天
        if past_day >= 90:
            character_data.talent[20] = 0
            character_data.talent[21] = 1
            character_data.talent[26] = 1
            character_data.talent[27] = 1
            character_data.second_behavior[1313] = 1
            talk.must_show_talk_check(character_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += _("\n随着怀孕的进程，{0}挺起了大肚子，隆起的曲线下是正在孕育的新生命\n").format(character_data.name)
            draw_text += _("\n{0}有孕在身，将会暂停工作和部分娱乐\n").format(character_data.name)
            draw_text += _("\n{0}从[受精]转变为[妊娠]\n").format(character_data.name)
            draw_text += _("\n{0}获得了[孕肚]\n").format(character_data.name)
            draw_text += _("\n{0}获得了[泌乳]\n").format(character_data.name)
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_near_born(character_id: int):
    """
    判断是否开始临盆
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是妊娠状态
    if character_data.talent[21]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.fertilization_time
        past_day = (start_date - end_date).days
        # 从受精开始算，标准妊娠时间是265天
        if past_day >= 260:
            # 清零污浊结构体
            character_data.dirty = attr_calculation.get_dirty_reset(character_data.dirty)
            # 赋予对应素质和二段行动
            character_data.talent[21] = 0
            character_data.talent[22] = 1
            character_data.second_behavior[1314] = 1
            talk.must_show_talk_check(character_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += _("\n随着怀孕的进程，{0}临近生产，即将诞下爱的结晶\n").format(character_data.name)
            draw_text += _("\n{0}在临盆期内会一直躺在医疗部住院区的病床上，多去陪陪她，静候生产的来临吧\n").format(character_data.name)
            draw_text += _("\n{0}从[妊娠]转变为[临盆]\n").format(character_data.name)
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_born(character_id: int):
    """
    判断是否开始生产
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是临盆状态
    if character_data.talent[22]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.fertilization_time
        past_day = (start_date - end_date).days - 260
        # 每过一天+20%几率判断是否生产
        now_rate = past_day * 20
        # print(f"debug {character_data.name}进入生产检测，当前生产几率为{now_rate}%")
        if random.randint(1,100) <= now_rate:
            draw_panel = sp_event_panel.Born_Panel(character_id)
            draw_panel.draw()


def check_rearing(character_id: int):
    """
    判断是否开始育儿
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是产后状态
    if character_data.talent[23]:
        # 计算经过的天数
        child_id = character_data.relationship.child_id_list[-1]
        child_character_data: game_type.Character = cache.character_data[child_id]
        start_date = cache.game_time
        end_date = child_character_data.pregnancy.born_time
        past_day = (start_date - end_date).days
        # 
        if past_day >= 2:
            character_data.talent[23] = 0
            character_data.talent[24] = 1
            character_data.second_behavior[1318] = 1
            talk.must_show_talk_check(character_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += _("\n{0}的产后休息结束了\n").format(character_data.name)
            draw_text += _("\n{0}接下来的行动重心会以照顾{1}为主\n").format(character_data.name, child_character_data.name)
            draw_text += _("\n{0}从[产后]转变为[育儿]\n").format(character_data.name)
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_rearing_complete(character_id: int):
    """
    判断是否完成育儿
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要已经是育儿状态
    if character_data.talent[24]:
        # 计算经过的天数
        child_id = character_data.relationship.child_id_list[-1]
        child_character_data: game_type.Character = cache.character_data[child_id]
        start_date = cache.game_time
        end_date = child_character_data.pregnancy.born_time
        past_day = (start_date - end_date).days
        # 90天在游戏内实际体验是30天
        if past_day >= 90:
            character_data.talent[24] = 0
            character_data.talent[27] = 0
            character_handle.get_new_character(child_id)
            character_data.second_behavior[1319] = 1
            talk.must_show_talk_check(character_id)
            child_character_data.talent[101] = 0
            child_character_data.talent[102] = 1
            child_character_data.work.work_type = 152
            draw_text = "\n※※※※※※※※※\n"
            draw_text += _("\n在{0}的悉心照料下，{1}顺利长大了\n").format(character_data.name, child_character_data.name)
            draw_text += _("\n{0}完成了育儿行动，开始回到正常的工作生活中来\n").format(character_data.name)
            draw_text += _("\n{0}能够初步独立了，在长大成人之前会一直在教育区上课学习\n").format(child_character_data.name)
            if len(cache.rhodes_island.all_work_npc_set[151]) == 0:
                draw_text += _("\n当前教育区没有进行授课工作的老师，请尽快安排一名干员负责教师工作\n")
            draw_text += _("\n{0}失去了[育儿]\n").format(character_data.name)
            draw_text += _("\n{0}失去了[泌乳]\n").format(character_data.name)
            draw_text += _("\n{0}从[婴儿]成长为了[幼女]\n").format(child_character_data.name)
            draw_text += _("\n{0}成为了一名准干员\n").format(child_character_data.name)
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_grow_to_loli(character_id: int):
    """
    判断是否成长为萝莉
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要是女儿，而且已经是幼女状态
    if character_data.relationship.father_id == 0 and character_data.talent[102]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.born_time
        past_day = (start_date - end_date).days
        # 在幼女后又过了两个月
        if past_day >= 270:
            character_data.second_behavior[1320] = 1
            talk.must_show_talk_check(character_id)
            character_data.talent[102] = 0
            character_data.talent[103] = 1
            character_data.talent[6] = 0
            chest_grow_text = chest_grow(character_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += _("\n{0}的身体渐渐成长，开始进入青春期，在第二性征发育的同时，也迎来了第一次的初潮\n").format(character_data.name)
            draw_text += _("\n{0}从[幼女]成长为了[萝莉]\n").format(character_data.name)
            draw_text += _("\n{0}失去了[未初潮]\n").format(character_data.name)
            draw_text += chest_grow_text
            draw_text += _("\n{0}可以参加上课以外的工作了\n").format(character_data.name)
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_grow_to_girl(character_id: int):
    """
    判断是否成长为少女
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 需要是女儿，而且已经是萝莉状态
    if character_data.relationship.father_id == 0 and character_data.talent[103]:
        # 计算经过的天数
        start_date = cache.game_time
        end_date = character_data.pregnancy.born_time
        past_day = (start_date - end_date).days
        # 在萝莉后又过了两个月
        if past_day >= 450:
            character_data.second_behavior[1321] = 1
            talk.must_show_talk_check(character_id)
            character_data.talent[103] = 0
            character_data.talent[104] = 1
            character_data.talent[7] = 0
            chest_grow_text = chest_grow(character_id)
            body_part_grow_text = body_part_grow(character_id)
            draw_text = "\n※※※※※※※※※\n"
            draw_text += _("\n{0}的身体完全长成，迎来了自己的成人礼，成为了一位亭亭玉立的少女\n").format(character_data.name)
            draw_text += _("\n{0}从[萝莉]成长为了[少女]\n").format(character_data.name)
            draw_text += _("\n{0}失去了[未成年]\n").format(character_data.name)
            draw_text += chest_grow_text
            draw_text += body_part_grow_text
            draw_text += _("\n{0}可以进行正常的工作了\n").format(character_data.name)
            draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()


def check_all_pregnancy(character_id: int):
    """
    进行受精怀孕的全流程检查
    \n\n包括刷新受精概率、是否受精、是否由受精变为怀孕、是否结束怀孕
    """

    get_fertilization_rate(character_id)
    check_fertilization(character_id)
    check_pregnancy(character_id)
    check_near_born(character_id)
    check_born(character_id)
    check_rearing(character_id)
    check_rearing_complete(character_id)
    check_grow_to_loli(character_id)
    check_grow_to_girl(character_id)


def update_reproduction_period(character_id: int):
    """
    刷新生理周期
    """

    character_data: game_type.Character = cache.character_data[character_id]
    now_reproduction = character_data.pregnancy.reproduction_period
    if now_reproduction == 6:
        character_data.pregnancy.reproduction_period = 0
    else:
        character_data.pregnancy.reproduction_period += 1


def chest_grow(character_id: int,print_flag = False):
    """
    进行胸部生长判定
    """

    character_data: game_type.Character = cache.character_data[character_id]
    mom_id = character_data.relationship.mother_id
    mom_character_data: game_type.Character = cache.character_data[mom_id]
    # 获得本人的旧胸部大小和母亲的胸部大小
    for i in {121,122,123,124,125}:
        if character_data.talent[i]:
            old_chest_id = i
        if mom_character_data.talent[i]:
            mom_chest_id = i

    # 用随机数计算生长，可能长3、长2或者长1，母亲胸部越大生长比例就越高
    # 母亲胸部0时从长0~长3生长比例是 0.6 0.25 0.1 0.05，母亲胸部6时反过来
    randow_grow = random.randint(1,100)
    grow_rate = mom_chest_id - 121
    grow_0 = 60 - 11 * grow_rate
    grow_1 = 25 - 3 *grow_rate
    grow_2 = 10 + 3 *grow_rate
    if randow_grow > grow_0 + grow_1 + grow_2:
        new_chest_id = min(old_chest_id + 3 ,125)
    elif randow_grow > grow_0 + grow_1:
        new_chest_id = min(old_chest_id + 2 ,125)
    elif randow_grow > grow_0 :
        new_chest_id = min(old_chest_id + 1 ,125)
    else:
        new_chest_id = old_chest_id

    # 把旧的胸部素质换成新的
    character_data.talent[old_chest_id] = 0
    character_data.talent[new_chest_id] = 1

    # 根据flag判定是否要绘制输出
    old_name = game_config.config_talent[old_chest_id].name
    new_name = game_config.config_talent[new_chest_id].name
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    if new_chest_id != old_chest_id:
        now_text = _("\n{0}的胸部从[{1}]成长为了[{2}]\n").format(character_data.name, old_name, new_name)
    else:
        now_text = _("\n{0}的胸部依旧保持在[{1}]没有成长\n").format(character_data.name, old_name)
    if print_flag:
        now_draw.text = now_text
        now_draw.draw()

    # 返回胸部成长情况的文本
    return now_text

def body_part_grow(character_id: int,print_flag = False):
    """
    进行除胸部外其他部位的生长判定
    """

    character_data: game_type.Character = cache.character_data[character_id]
    mom_id = character_data.relationship.mother_id
    mom_character_data: game_type.Character = cache.character_data[mom_id]
    now_text = ""

    old_talent_id_list, new_talent_id_list = [], []
    # 获得本人的臀部大小和母亲的臀部大小
    for i in {126,127,128,129,130,131,132}:
        if character_data.talent[i]:
            old_talent_id_list.append(i)
        if mom_character_data.talent[i]:
            new_talent_id_list.append(i)

    # 把旧的素质换成新的
    for old_talent_id in old_talent_id_list:
        character_data.talent[old_talent_id] = 0
    for new_talent_id in new_talent_id_list:
        character_data.talent[new_talent_id] = 1

    # 根据flag判定是否要绘制输出
    for i in range(len(old_talent_id_list)):
        old_talent_id = old_talent_id_list[i]
        new_talent_id = new_talent_id_list[i]
        old_name = game_config.config_talent[old_talent_id].name
        new_name = game_config.config_talent[new_talent_id].name
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        if new_talent_id != old_talent_id:
            now_text += _("\n{0}的[{1}]成长为了[{2}]\n").format(character_data.name, old_name, new_name)
        if print_flag:
            now_draw.text = now_text
            now_draw.draw()

    # 返回成长情况的文本
    return now_text
