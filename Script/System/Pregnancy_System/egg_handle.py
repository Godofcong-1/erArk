import random
from types import FunctionType
from typing import Optional
from Script.Core import (
    cache_control,
    game_type,
    get_text,
)
from Script.Design import (
    talk,
    second_behavior,
    game_time,
)
from Script.Design import handle_premise
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.System.Pregnancy_System import pregnancy_constant

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def get_birth_type(character_id: int) -> int:
    """
    获取角色的生育方式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 生育方式（1单胎胎生，2多胎胎生，11带壳卵生；12无壳卵生本期未实装，归一化为1）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    race_config = game_config.config_race.get(character_data.race)
    if race_config is None:
        return pregnancy_constant.BIRTH_TYPE_SINGLE
    # CSV空值字段会被删除，缺列时兜底为单胎胎生
    birth_type = getattr(race_config, "birth_type", pregnancy_constant.BIRTH_TYPE_SINGLE)
    # 12无壳卵生本期按胎生处理，胎生链不感知12的存在
    if birth_type == pregnancy_constant.BIRTH_TYPE_EGG_SOFT:
        return pregnancy_constant.BIRTH_TYPE_SINGLE
    return birth_type


def is_viviparous(character_id: int) -> bool:
    """
    判断角色是否为胎生种族（单胎胎生或多胎胎生，供妊娠加速药/假孕药等胎生限定功能使用）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否胎生
    """
    return get_birth_type(character_id) in (pregnancy_constant.BIRTH_TYPE_SINGLE, pregnancy_constant.BIRTH_TYPE_MULTIPLE)


def is_multiple_birth(character_id: int) -> bool:
    """
    判断角色是否为多胎胎生种族
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否多胎胎生
    """
    return get_birth_type(character_id) == pregnancy_constant.BIRTH_TYPE_MULTIPLE


def add_egg(character_id: int, fertilized: bool):
    """
    为角色新增一枚卵
    Keyword arguments:
    character_id -- 角色id
    fertilized -- 是否受精（排出时即确定，鉴定只是揭示）
    Return arguments:
    int -- 新卵的编号
    """
    character_data: game_type.Character = cache.character_data[character_id]
    egg_id = character_data.pregnancy.next_egg_id
    character_data.pregnancy.eggs[egg_id] = {
        "lay_time": cache.game_time,
        "identified": False,
        "fertilized": fertilized,
        "identify_time": None,
        "father_id": 0,
        "hatch_stage": 0,
        "held_by_player": False,
        "acceleration_days": 0.0,
    }
    character_data.pregnancy.next_egg_id += 1
    return egg_id


def get_unidentified_eggs(character_id: int, exclude_held: bool = True) -> dict:
    """
    获取角色的未鉴定卵
    Keyword arguments:
    character_id -- 角色id
    exclude_held -- 是否排除已被玩家拿走的卵（默认排除）
    Return arguments:
    dict -- {卵编号: 卵数据字典}
    """
    character_data: game_type.Character = cache.character_data[character_id]
    result = {}
    for egg_id, egg_data in character_data.pregnancy.eggs.items():
        if egg_data["identified"]:
            continue
        if exclude_held and egg_data.get("held_by_player", False):
            continue
        result[egg_id] = egg_data
    return result


def get_identifiable_eggs(character_id: int) -> dict:
    """
    获取角色当前可鉴定的未鉴定卵（排出日早于今天且未被玩家拿走）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    dict -- {卵编号: 卵数据字典}
    """
    result = {}
    for egg_id, egg_data in get_unidentified_eggs(character_id).items():
        # 按日历日比较（两端都截到当日0点再算天数）：排出次日起可鉴定
        lay_day_time = egg_data["lay_time"].replace(hour=0, minute=0, second=0, microsecond=0)
        now_day_time = cache.game_time.replace(hour=0, minute=0, second=0, microsecond=0)
        if game_time.count_day_for_datetime(lay_day_time, now_day_time) >= 1:
            result[egg_id] = egg_data
    return result


def get_hatching_eggs(character_id: int) -> dict:
    """
    获取角色孵化中的卵（已鉴定且受精）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    dict -- {卵编号: 卵数据字典}
    """
    character_data: game_type.Character = cache.character_data[character_id]
    result = {}
    for egg_id, egg_data in character_data.pregnancy.eggs.items():
        if egg_data["identified"] and egg_data["fertilized"]:
            result[egg_id] = egg_data
    return result


def get_hatch_day(egg_data: dict) -> int:
    """
    计算卵的有效孵化天数（自排出日起的自然天数+孵化加速药累计的加速天数）
    Keyword arguments:
    egg_data -- 卵数据字典
    Return arguments:
    int -- 有效孵化天数
    """
    # 旧存档的卵可能缺加速键，一律.get兜底
    return game_time.count_day_for_datetime(egg_data["lay_time"], cache.game_time) + int(egg_data.get("acceleration_days", 0))


def get_egg_acceleration_amount(egg_data: dict) -> float:
    """
    计算孵化加速药对该卵单次可入账的加速天数（破壳前一天封顶，剂量基数为孵化总天数265）
    Keyword arguments:
    egg_data -- 卵数据字典
    Return arguments:
    float -- 可入账加速天数（<=0时表示已到极限无法使用）
    """
    from Script.System.Pregnancy_System import pregnancy_handle
    now_acc = egg_data.get("acceleration_days", 0)
    return pregnancy_handle.get_acceleration_amount(now_acc, get_hatch_day(egg_data), pregnancy_constant.HATCH_TOTAL_DAY - 1, pregnancy_constant.HATCH_TOTAL_DAY)


def get_accelerable_hatching_eggs(character_id: int) -> dict:
    """
    获取角色可被孵化加速药加速的孵化中卵（可入账加速量>0）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    dict -- {卵编号: 卵数据字典}
    """
    result = {}
    for egg_id, egg_data in get_hatching_eggs(character_id).items():
        if get_egg_acceleration_amount(egg_data) > 0:
            result[egg_id] = egg_data
    return result


def have_need_tend_eggs(character_id: int) -> bool:
    """
    判断角色是否持有需要照料的卵（可鉴定的未鉴定卵 或 孵化中的卵）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否持有
    """
    if len(get_identifiable_eggs(character_id)):
        return True
    if len(get_hatching_eggs(character_id)):
        return True
    return False


def any_hatching_eggs_exist() -> bool:
    """
    判断是否存在任何角色持有孵化中的卵（受精卵均存放于育儿室孵化）
    Return arguments:
    bool -- 是否存在
    """
    for chara_id in cache.npc_id_got:
        if chara_id == 0:
            continue
        if len(get_hatching_eggs(chara_id)):
            return True
    return False


def find_identifiable_egg_owner_in_scene(character_id: int) -> int:
    """
    在自己所在场景中寻找持有可鉴定卵的角色（含自己）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 持卵角色id，无则返回-1
    """
    from Script.Design import map_handle
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        if chara_id == 0:
            continue
        if len(get_identifiable_eggs(chara_id)):
            return chara_id
    return -1


def nursery_worker_on_duty_in_scene(character_id: int) -> bool:
    """
    判断自己所在场景中是否有处于工作时间内的保育员（排除下班后滞留的保育员，防止持卵角色白等）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否有在班保育员在场
    """
    from Script.Design import map_handle, handle_premise
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        if chara_id == 0 or chara_id == character_id:
            continue
        other_character_data: game_type.Character = cache.character_data[chara_id]
        if other_character_data.work.work_type != pregnancy_constant.NURSERY_WORKER_WORK_ID:
            continue
        if handle_premise.handle_premise("work_time", chara_id):
            return True
    return False


def check_ovulation(character_id: int):
    """
    排卵结算：每个排卵日必排一枚卵（受精判定成功则为受精卵并清受精素质，否则为无精卵）
    \n由本周期排卵日事件待办标记驱动（周期推进到排卵日时置位，0点结算有兜底，玩家不睡觉也不会错过）；
    \n各分支均消费标记，保证每周期至多结算一次
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 仅在本周期排卵日事件待处理时进行结算
    if not character_data.pregnancy.ovulation_flag:
        return
    # 守卫：非带壳卵生角色不排卵（0点兜底会对全角色调用；胎生的标记已由受精判定消费，此处为种族中途变更等情况兜底）
    if get_birth_type(character_id) != 11:
        character_data.pregnancy.ovulation_flag = False
        return
    # 排卵结算即本周期排卵日事件的消费，以下豁免分支同样视为本周期已处理
    character_data.pregnancy.ovulation_flag = False
    # 未初潮不排卵
    if handle_premise.handle_menarche_1(character_id):
        return
    # 机械体且未安装生育模组不排卵
    if character_data.race == 2 and character_data.talent[171] == 0:
        return
    # 安全兜底：处于胎生妊娠链中的角色（种族被中途修改等）不排卵
    if handle_premise.handle_pregnancy_1(character_id) or handle_premise.handle_parturient_1(character_id):
        return
    # 受精判定成功则排出受精卵并消费受精素质，否则排出无精卵
    fertilized = bool(handle_premise.handle_fertilization_1(character_id))
    if fertilized:
        character_data.talent[20] = 0
        # 受精素质已被卵消费，无意识妊娠素质一并转移到卵的流程中
        character_data.talent[35] = 0
    add_egg(character_id, fertilized)
    # 触发排出卵的二段行为
    second_behavior.character_get_second_behavior(character_id, "lay_egg")
    talk.must_show_talk_check(character_id)


def npc_identify_eggs_settle(character_id: int, identifier_id: Optional[int] = None):
    """
    鉴定卵结算：一次揭示角色当前全部可鉴定的未鉴定卵
    \n未受精卵静默删除（不通知玩家）；受精卵置已鉴定并通知玩家、进入孵化流程
    Keyword arguments:
    character_id -- 持卵角色id
    identifier_id -- 执行鉴定的角色id（None或与持卵角色相同时视为本人自行鉴定，否则为保育员代为鉴定）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    identifiable_eggs = get_identifiable_eggs(character_id)
    if not len(identifiable_eggs):
        return
    fertilized_count = 0
    for egg_id, egg_data in identifiable_eggs.items():
        if egg_data["fertilized"]:
            egg_data["identified"] = True
            egg_data["identify_time"] = cache.game_time
            fertilized_count += 1
        else:
            # 未受精卵静默废弃
            del character_data.pregnancy.eggs[egg_id]
    # 鉴定出受精卵时通知玩家
    if fertilized_count:
        second_behavior.character_get_second_behavior(character_id, "egg_fertilized")
        talk.must_show_talk_check(character_id)
        draw_text = "\n※※※※※※※※※\n"
        if identifier_id is not None and identifier_id != character_id:
            identifier_data: game_type.Character = cache.character_data[identifier_id]
            draw_text += _("\n保育员{0}在育儿室为{1}鉴定了产下的卵，发现其中{2}枚已经受精\n").format(identifier_data.name, character_data.name, fertilized_count)
        else:
            draw_text += _("\n{0}在育儿室鉴定了自己产下的卵，发现其中{1}枚已经受精\n").format(character_data.name, fertilized_count)
        draw_text += _("\n受精卵将一直放在育儿室中照料孵化\n")
        draw_text += "\n※※※※※※※※※\n"
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = draw_text
        now_draw.draw()


def check_egg_born(character_id: int):
    """
    破壳判定：孵化中的卵自排出起满孵化总天数则触发破壳事件
    Keyword arguments:
    character_id -- 角色id
    """
    for egg_id, egg_data in get_hatching_eggs(character_id).items():
        # 刷新孵化阶段展示值
        egg_data["hatch_stage"] = get_hatch_day(egg_data)
        if get_hatch_day(egg_data) >= pregnancy_constant.HATCH_TOTAL_DAY:
            # 每晚仅处理一枚卵的破壳事件
            from Script.System.Pregnancy_System import born_event_panel
            draw_panel = born_event_panel.Born_Panel(character_id, egg_mode=True, egg_id=egg_id)
            draw_panel.draw()
            return


def take_eggs_from_chara(target_character_id: int):
    """
    拿走交互对象的全部未鉴定卵（卵详细数据留在原角色处并标记被拿走，玩家收藏品中记录索引）
    Keyword arguments:
    target_character_id -- 交互对象id
    Return arguments:
    int -- 拿走的卵数量
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[target_character_id]
    take_count = 0
    for egg_id, egg_data in get_unidentified_eggs(target_character_id).items():
        egg_data["held_by_player"] = True
        held_id = pl_character_data.pl_collection.next_held_egg_id
        pl_character_data.pl_collection.held_eggs[held_id] = (target_character_id, egg_id)
        pl_character_data.pl_collection.next_held_egg_id += 1
        take_count += 1
    if take_count:
        draw_text = _("\n从{0}处拿走了{1}枚未鉴定的卵\n").format(target_data.name, take_count)
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = draw_text
        now_draw.draw()
    return take_count


def identify_held_eggs_settle():
    """
    鉴定玩家临时持有的全部卵，并经索引同步回写原角色的卵数据
    \n未受精则删除原角色的该卵；受精则置已鉴定并进入孵化流程（回到原角色的常规孵化轨道）
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    held_eggs = dict(pl_character_data.pl_collection.held_eggs)
    fertilized_chara_count = {}
    for held_id, (chara_id, egg_id) in held_eggs.items():
        # 索引即将消耗，先行删除
        del pl_character_data.pl_collection.held_eggs[held_id]
        # 原角色或卵已不存在时静默清理索引
        if chara_id not in cache.character_data:
            continue
        character_data: game_type.Character = cache.character_data[chara_id]
        if egg_id not in character_data.pregnancy.eggs:
            continue
        egg_data = character_data.pregnancy.eggs[egg_id]
        if egg_data["fertilized"]:
            egg_data["identified"] = True
            egg_data["identify_time"] = cache.game_time
            egg_data["held_by_player"] = False
            fertilized_chara_count.setdefault(chara_id, 0)
            fertilized_chara_count[chara_id] += 1
        else:
            # 未受精卵直接删除
            del character_data.pregnancy.eggs[egg_id]
    # 逐角色通知鉴定出的受精卵
    for chara_id, count in fertilized_chara_count.items():
        character_data = cache.character_data[chara_id]
        second_behavior.character_get_second_behavior(chara_id, "egg_fertilized")
        talk.must_show_talk_check(chara_id)
        draw_text = "\n※※※※※※※※※\n"
        draw_text += _("\n经过鉴定，{0}产下的卵中有{1}枚已经受精\n").format(character_data.name, count)
        draw_text += _("\n受精卵将一直放在育儿室中进行孵化\n")
        draw_text += "\n※※※※※※※※※\n"
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = draw_text
        now_draw.draw()


def replace_entertainment_for_eggs(character_id: int):
    """
    每日娱乐替换钩子：持有需要照料的卵的带壳卵生角色，随机一个娱乐时段替换为照料卵
    \n需在每日娱乐刷新（get_chara_entertainment）之后调用；派对日、监禁等无法自由活动的角色跳过
    Keyword arguments:
    character_id -- 角色id
    """
    if character_id == 0:
        return
    if get_birth_type(character_id) != 11:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 监禁中的角色跳过（其未鉴定卵由玩家指令代办）
    if character_data.sp_flag.imprisonment:
        return
    # 派对日全时段为派对娱乐，跳过
    week_day = cache.game_time.weekday()
    if hasattr(cache.rhodes_island, "party_day_of_week") and cache.rhodes_island.party_day_of_week.get(week_day, 0):
        return
    # 幼女不进行照料卵（其娱乐固定为过家家）
    if handle_premise.handle_self_is_child(character_id):
        return
    # 没有需要照料的卵则跳过
    if not have_need_tend_eggs(character_id):
        return
    now_time_slot = random.randint(0, 2)
    character_data.entertainment.entertainment_type[now_time_slot] = pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID
