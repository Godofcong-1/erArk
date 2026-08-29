"""
无壳卵生子系统：体外排卵 → 体外无壳卵（玩家收藏品持有）→ 体外受精 → 受精卵回写母亲的卵字典进入孵化

流程：
1. 排卵日当天（周期5）无壳卵生角色获得一次体外排卵机会（PREGNANCY.external_ovulation_chance）
2. 与玩家同处一地时，性绝顶（普通及以上）按部位/程度概率触发二段行为 lay_soft_egg，消耗机会
3. 二段结算生成一枚体外无壳卵（PLAYER_COLLECTION.soft_eggs），子宫与小穴八成精液转移到卵上
4. 玩家可在同一地点射精时选择射在卵上；身体栏显示卵上的精液量
5. 排出满1小时后进行无限轮衰减受精判定，受精卵逐枚回写母亲 pregnancy.eggs（identified=True, soft=True），之后走带壳卵生的孵化/破壳链
"""
import random
from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.Config import normal_config
from Script.Design import attr_calculation, handle_premise, map_handle, second_behavior, talk
from Script.UI.Moudle import draw
from Script.System.Pregnancy_System import pregnancy_constant, egg_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def have_external_ovulation_chance(character_id: int) -> bool:
    """
    判断角色今天是否还有体外排卵机会（无壳卵生、处于排卵日且机会未使用）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否有机会
    """
    if not egg_handle.is_egg_soft(character_id):
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.pregnancy.reproduction_period != 5:
        return False
    return bool(getattr(character_data.pregnancy, "external_ovulation_chance", False))


def get_external_ovulation_rate(character_id: int, orgasm_part: int, orgasm_degree: int) -> float:
    """
    计算一次性绝顶触发体外排卵的概率
    \n小绝顶不触发；基准值按程度查表，阴道×2、子宫×4，子宫超强绝顶固定100%；
    \n排卵促进药与催眠强制排卵各×5（效果保留到当日排卵机会结束，判定本身不消耗）；上限100
    Keyword arguments:
    character_id -- 角色id
    orgasm_part -- 绝顶部位的快感状态id（4阴道、7子宫，其他为其他部位）
    orgasm_degree -- 绝顶程度（0小、1普通、2强、3超强）
    Return arguments:
    float -- 概率（百分比）
    """
    if orgasm_degree < 1:
        return 0.0
    character_data: game_type.Character = cache.character_data[character_id]
    # 子宫超强绝顶必定排卵
    if orgasm_part == 7 and orgasm_degree >= 3:
        return 100.0
    now_rate = float(pregnancy_constant.EXTERNAL_OVULATION_RATE.get(orgasm_degree, 0))
    if orgasm_part == 4:
        now_rate *= pregnancy_constant.EXTERNAL_OVULATION_V_MULT
    elif orgasm_part == 7:
        now_rate *= pregnancy_constant.EXTERNAL_OVULATION_W_MULT
    # 排卵促进药与催眠强制排卵改为提升排卵概率
    if character_data.h_state.body_item[10][1]:
        now_rate *= pregnancy_constant.EXTERNAL_OVULATION_DRUG_MULT
    if character_data.hypnosis.force_ovulation:
        now_rate *= pregnancy_constant.EXTERNAL_OVULATION_DRUG_MULT
    return min(100.0, now_rate)


def judge_external_ovulation(character_id: int, orgasm_part: int, orgasm_degree: int) -> bool:
    """
    绝顶结算中的体外排卵判定：满足条件且概率命中时赋予二段行为 lay_soft_egg 并消耗本日机会
    \n条件：NPC、无壳卵生、排卵日且机会未用、与玩家同一地点、已初潮、非未装生育模组的机械
    Keyword arguments:
    character_id -- 角色id
    orgasm_part -- 绝顶部位的快感状态id
    orgasm_degree -- 绝顶程度（0小、1普通、2强、3超强）
    Return arguments:
    bool -- 是否触发了体外排卵
    """
    if character_id == 0:
        return False
    if not have_external_ovulation_chance(character_id):
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    if not handle_premise.handle_in_player_scene(character_id):
        return False
    if handle_premise.handle_menarche_1(character_id):
        return False
    if character_data.race == 2 and character_data.talent[171] == 0:
        return False
    now_rate = get_external_ovulation_rate(character_id, orgasm_part, orgasm_degree)
    if now_rate <= 0:
        return False
    if random.randint(1, 100) > now_rate:
        return False
    # 命中：消耗本日机会，排卵促进药与催眠强制排卵效果随之结束
    character_data.pregnancy.external_ovulation_chance = False
    character_data.h_state.body_item[10][1] = False
    character_data.hypnosis.force_ovulation = False
    second_behavior.character_get_second_behavior(character_id, pregnancy_constant.LAY_SOFT_EGG_SECOND_BEHAVIOR)
    return True


def lay_soft_egg(character_id: int) -> int:
    """
    体外排卵的数据结算：在玩家收藏品中生成一枚体外无壳卵，把子宫与小穴中八成的精液转移到卵上，并提示玩家
    Keyword arguments:
    character_id -- 排卵的角色id
    Return arguments:
    int -- 新卵的编号
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_collection = pl_character_data.pl_collection
    # 精液转移：子宫(7)与小穴(6)各转移八成，部位剩余量与等级同步刷新（累计量不动）
    transfer_count = 0
    for part_cid in (6, 7):
        now_semen_data = character_data.dirty.body_semen[part_cid]
        move_count = int(now_semen_data[1] * pregnancy_constant.SOFT_EGG_SEMEN_TRANSFER_RATE)
        if move_count <= 0:
            continue
        now_semen_data[1] = max(now_semen_data[1] - move_count, 0)
        now_semen_data[2] = attr_calculation.get_semen_now_level(now_semen_data[1], part_cid, 0)
        transfer_count += move_count
    # 登记体外卵
    egg_id = pl_collection.next_soft_egg_id
    pl_collection.soft_eggs[egg_id] = {
        "mother_id": character_id,
        "lay_time": cache.game_time,
        "position": list(character_data.position),
        "semen_count": float(transfer_count),
    }
    pl_collection.next_soft_egg_id += 1
    # 提示玩家
    draw_text = "\n※※※※※※※※※\n"
    if transfer_count > 0:
        draw_text += _("\n{0}的体内排出了一大团裹在黏稠凝胶里的无壳卵块，成百上千颗细小的卵粒在半透明的胶质中若隐若现，子宫与小穴中的{1}ml精液随之渗进了凝胶\n").format(character_data.name, transfer_count)
    else:
        draw_text += _("\n{0}的体内排出了一大团裹在黏稠凝胶里的无壳卵块，成百上千颗细小的卵粒在半透明的胶质中若隐若现，凝胶里还没有任何精液\n").format(character_data.name)
    draw_text += _("\n请在{0}小时内尽量多地把精液射在这团卵块上，精液需要穿过凝胶层才能与卵粒结合，精液越多，受精的概率与受精卵粒的数量就越高\n").format(pregnancy_constant.SOFT_EGG_FERTILIZATION_DELAY_HOUR)
    draw_text += "\n※※※※※※※※※\n"
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = draw_text
    now_draw.draw()
    return egg_id


def get_soft_eggs_in_scene(position: list) -> dict:
    """
    获取指定地点的全部体外无壳卵
    Keyword arguments:
    position -- 场景路径列表
    Return arguments:
    dict -- {卵编号: 卵数据}
    """
    pl_collection = cache.character_data[0].pl_collection
    soft_eggs = getattr(pl_collection, "soft_eggs", {})
    return {egg_id: egg_data for egg_id, egg_data in soft_eggs.items() if list(egg_data["position"]) == list(position)}


def get_mother_soft_eggs(mother_id: int) -> dict:
    """
    获取某角色排出的、尚未进行受精判定的全部体外无壳卵
    Keyword arguments:
    mother_id -- 母亲角色id
    Return arguments:
    dict -- {卵编号: 卵数据}
    """
    pl_collection = cache.character_data[0].pl_collection
    soft_eggs = getattr(pl_collection, "soft_eggs", {})
    return {egg_id: egg_data for egg_id, egg_data in soft_eggs.items() if egg_data["mother_id"] == mother_id}


def add_semen_to_soft_egg(egg_id: int, semen_count: int):
    """
    向体外无壳卵追加精液
    Keyword arguments:
    egg_id -- 卵编号
    semen_count -- 精液量（毫升）
    """
    soft_eggs = cache.character_data[0].pl_collection.soft_eggs
    if egg_id not in soft_eggs:
        return
    soft_eggs[egg_id]["semen_count"] = max(soft_eggs[egg_id]["semen_count"] + semen_count, 0)


def get_soft_egg_semen_level(semen_count: float) -> int:
    """
    体外无壳卵的精液污浊等级（0~15）
    \n0：无精液；1~10：以5000ml为基数按部位精液等级的比例阶梯换算；超过5000ml后每1000ml加一级，上限15级（10000ml）
    Keyword arguments:
    semen_count -- 卵上精液量（毫升）
    Return arguments:
    int -- 污浊等级
    """
    if semen_count <= 0:
        return 0
    base_volume = pregnancy_constant.SOFT_EGG_SEMEN_LEVEL_MAX_VOLUME
    if semen_count < base_volume:
        return attr_calculation.get_semen_level_by_volume(semen_count, base_volume)
    extra_level = int((semen_count - base_volume) / pregnancy_constant.SOFT_EGG_SEMEN_LEVEL_EXTRA_STEP)
    return min(10 + extra_level, pregnancy_constant.SOFT_EGG_SEMEN_LEVEL_MAX)


def get_soft_egg_name(egg_id: int) -> str:
    """
    体外无壳卵块的显示名（"{母亲}排出的卵块"；一团卵块=凝胶包裹的成百上千颗卵粒）
    Keyword arguments:
    egg_id -- 卵块编号
    Return arguments:
    str -- 显示名
    """
    soft_eggs = cache.character_data[0].pl_collection.soft_eggs
    if egg_id not in soft_eggs:
        return _("无壳卵块")
    mother_id = soft_eggs[egg_id]["mother_id"]
    mother_name = cache.character_data[mother_id].name if mother_id in cache.character_data else _("某人")
    return _("{0}排出的卵块").format(mother_name)


def get_soft_egg_scene_name(egg_data: dict) -> str:
    """
    体外无壳卵所在地点的场景名
    Keyword arguments:
    egg_data -- 卵数据
    Return arguments:
    str -- 场景名（查不到时返回路径字符串）
    """
    scene_path_str = map_handle.get_map_system_path_str_for_list(egg_data["position"])
    if scene_path_str in cache.scene_data:
        return cache.scene_data[scene_path_str].scene_name
    return scene_path_str


def get_soft_egg_remain_minute(egg_data: dict) -> int:
    """
    体外无壳卵距离受精判定还剩的分钟数（已到期返回0）
    Keyword arguments:
    egg_data -- 卵数据
    Return arguments:
    int -- 剩余分钟
    """
    passed_minute = (cache.game_time - egg_data["lay_time"]).total_seconds() / 60
    remain_minute = pregnancy_constant.SOFT_EGG_FERTILIZATION_DELAY_HOUR * 60 - passed_minute
    return max(int(remain_minute), 0)


def get_soft_egg_fertilization_rate(semen_count: float) -> float:
    """
    体外受精单轮概率：(精液量/1500)^2*100 + 卵污浊等级*3，上限100；不乘生理周期倍率、不受药物/催眠/浓厚精液影响
    Keyword arguments:
    semen_count -- 当轮用于判定的精液量（毫升）
    Return arguments:
    float -- 概率（百分比）
    """
    now_level = get_soft_egg_semen_level(semen_count)
    now_rate = (semen_count / pregnancy_constant.SOFT_EGG_RATE_DIVISOR) ** 2 * 100 + now_level * pregnancy_constant.SOFT_EGG_LEVEL_RATE
    return min(100.0, now_rate)


def check_soft_eggs_fertilization():
    """
    体外受精判定：对所有排出满1小时的体外无壳卵进行无限轮衰减判定（每轮后精液量衰减30%，低于5ml停止），
    \n每一轮成功即为一枚受精卵回写母亲的卵字典（已鉴定、无壳、孵化计时自体外排出起算）；无论结果都从玩家收藏品中删除该卵并提示
    \n挂钩于每次玩家行动后的实时结算与睡眠结算
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_collection = pl_character_data.pl_collection
    soft_eggs = getattr(pl_collection, "soft_eggs", None)
    if not soft_eggs:
        return
    for egg_id in list(soft_eggs.keys()):
        egg_data = soft_eggs[egg_id]
        if get_soft_egg_remain_minute(egg_data) > 0:
            continue
        mother_id = egg_data["mother_id"]
        semen_total = egg_data["semen_count"]
        now_semen = semen_total
        success_count = 0
        # 无限轮衰减判定，直到剩余精液量低于阈值
        while now_semen >= pregnancy_constant.SOFT_EGG_MIN_SEMEN:
            if random.randint(1, 100) <= get_soft_egg_fertilization_rate(now_semen):
                success_count += 1
            now_semen *= 1 - pregnancy_constant.MULTIPLE_BIRTH_SEMEN_DECAY
        egg_name = get_soft_egg_name(egg_id)
        del soft_eggs[egg_id]
        draw_text = "\n※※※※※※※※※\n"
        if success_count >= 1 and mother_id in cache.character_data:
            mother_character_data: game_type.Character = cache.character_data[mother_id]
            for _index in range(success_count):
                new_egg_id = egg_handle.add_egg(mother_id, True, soft=True)
                new_egg_data = mother_character_data.pregnancy.eggs[new_egg_id]
                new_egg_data["identified"] = True
                new_egg_data["identify_time"] = cache.game_time
                # 孵化计时自体外排出起算，与带壳卵生以排出时间为基准一致
                new_egg_data["lay_time"] = egg_data["lay_time"]
            draw_text += _("\n{1}ml精液渗过了{0}的凝胶层，与其中的卵粒完成了结合，共有{2}颗卵粒受精，已送往育儿室孵化\n").format(egg_name, int(semen_total), success_count)
            second_behavior.character_get_second_behavior(mother_id, pregnancy_constant.SOFT_EGG_FERTILIZED_SECOND_BEHAVIOR)
            talk.must_show_talk_check(mother_id)
        else:
            draw_text += _("\n{1}ml精液没能穿透{0}的凝胶层与卵粒结合，没有一颗卵粒受精，整团卵块失去了活性\n").format(egg_name, int(semen_total))
        draw_text += "\n※※※※※※※※※\n"
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = draw_text
        now_draw.draw()
