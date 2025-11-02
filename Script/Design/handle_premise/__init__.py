from functools import wraps
from types import FunctionType
from typing import Callable, Optional
from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import attr_calculation, character, instuct_judege
from Script.Config import game_config

# 导入所有的其他handle_premise模块函数
from Script.Design.handle_premise.handle_premise_other import *
from Script.Design.handle_premise.handle_premise_sp_flag import *
from Script.Design.handle_premise.handle_premise_time import *
from Script.Design.handle_premise.handle_premise_place import *
from Script.Design.handle_premise.handle_premise_cloth import *
from Script.Design.handle_premise.handle_premise_entertainment import *
from Script.Design.handle_premise.handle_premise_arts import *
from Script.Design.handle_premise.handle_premise_base_value import *
from Script.Design.handle_premise.handle_premise_ability import *
from Script.Design.handle_premise.handle_premise_talent import *
from Script.Design.handle_premise.handle_premise_fall import *
from Script.Design.handle_premise.handle_premise_H import *
from Script.Design.handle_premise.handle_premise_dirty import *
from Script.Design.handle_premise.handle_premise_first import *
from Script.Design.handle_premise.handle_premise_last_cmd import *
from Script.Design.handle_premise.handle_premise_assistant import *
from Script.Design.handle_premise.handle_premise_body_manage import *
from Script.Design.handle_premise.handle_premise_work import *


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

UNNORMAL_FLAG_BITS = {index: 1 << (index - 1) for index in range(1, 8)}
""" 异常状态位对应的bit值映射 """

_UNNORMAL_FLAG_HANDLERS: dict[int, Callable[[int], int]] = {}


def _ensure_unnormal_flag_storage(character_data: game_type.Character) -> game_type.UnnormalFlagMask:
    """确保角色异常状态使用位掩码存储，兼容旧存档的dict结构。"""
    unnormal_flag = character_data.sp_flag.unnormal_flag
    if isinstance(unnormal_flag, dict):
        character_data.sp_flag.unnormal_flag = game_type.UnnormalFlagMask(unnormal_flag)
    elif not isinstance(unnormal_flag, game_type.UnnormalFlagMask):
        character_data.sp_flag.unnormal_flag = game_type.UnnormalFlagMask()
    return character_data.sp_flag.unnormal_flag


def _get_unnormal_flag_handlers() -> dict[int, Callable[[int], int]]:
    """延迟构建各异常判定函数映射。"""
    if not _UNNORMAL_FLAG_HANDLERS:
        _UNNORMAL_FLAG_HANDLERS.update({
            1: handle_normal_1,
            2: handle_normal_2,
            3: handle_normal_3,
            4: handle_normal_4,
            5: handle_normal_5,
            6: handle_normal_6,
            7: handle_normal_7,
        })
    return _UNNORMAL_FLAG_HANDLERS


def _calculate_unnormal_flag_mask(character_id: int) -> int:
    """计算角色全部异常状态的位掩码。"""
    mask = 0
    for index, handler in _get_unnormal_flag_handlers().items():
        if not handler(character_id):
            mask |= UNNORMAL_FLAG_BITS[index]
    return mask


def refresh_unnormal_flag(character_id: int) -> int:
    """重新结算并返回角色的异常位掩码。"""
    character_data = cache.character_data[character_id]
    unnormal_flag = _ensure_unnormal_flag_storage(character_data)
    unnormal_flag.reset()
    new_mask = _calculate_unnormal_flag_mask(character_id)
    unnormal_flag.set_mask(new_mask)
    return new_mask


def get_unnormal_flag_mask(character_id: int, refresh: bool = False) -> int:
    """获取角色的异常位掩码，可选择是否同时刷新。"""
    if refresh:
        return refresh_unnormal_flag(character_id)
    character_data = cache.character_data[character_id]
    unnormal_flag = _ensure_unnormal_flag_storage(character_data)
    return unnormal_flag.mask


def has_unnormal_flag(character_id: int, mask: int, *, require_all: bool = False, refresh: bool = False) -> bool:
    """按位判定指定异常是否存在。"""
    current_mask = get_unnormal_flag_mask(character_id, refresh=refresh)
    if require_all:
        return (current_mask & mask) == mask
    return bool(current_mask & mask)


def _quick_check_normal_by_mask(character_id: int, index: int) -> Optional[int]:
    """若异常位掩码已知，则快速给出normal判定结果。"""
    character_data = cache.character_data[character_id]
    unnormal_flag = character_data.sp_flag.unnormal_flag
    if isinstance(unnormal_flag, game_type.UnnormalFlagMask) and unnormal_flag.is_known(index):
        return 0 if unnormal_flag[index] else 1
    return None

def add_premise(premise: str) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_premise_data[premise] = return_wrapper  # type: ignore[assignment]
        return return_wrapper

    return decoraror


def handle_premise(premise: str, character_id: int) -> int:
    """
    调用前提id对应的前提处理函数
    Keyword arguments:
    premise -- 前提id
    character_id -- 角色id
    Return arguments:
    int -- 前提权重加成
    """
    if premise in constant.handle_premise_data:
        return constant.handle_premise_data[premise](character_id)
    elif "CVP" in premise:
        premise_all_value_list = premise.split("_")[1:]
        return handle_comprehensive_value_premise(character_id, premise_all_value_list)
    else:
        return 0


def get_weight_from_premise_dict(talk_premise_dict: set, character_id: int, calculated_premise_dict: dict, weight_all_to_1_flag: bool = False, unconscious_pass_flag: bool = False) -> tuple[int, dict]:
    """
    遍历前提字典，计算总权重
    Keyword arguments:
    talk_premise_set -- 当前口上的前提集合
    character_id -- 角色id
    calculated_premise_dict -- 已计算的前提字典，默认空字典
    weight_all_to_1_flag -- 将所有非high的前提权重转换为1，默认为False
    unconscious_h_pass_flag -- 跳过无意识判定，默认为false，不可以跳过
    Return arguments:
    now_weight -- int，总权重
    """

    character_data: game_type.Character = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    target_character_data = cache.character_data[target_character_id]
    behavior_id = character_data.behavior.behavior_id
    now_weight = 0 # 总权重
    now_premise_data = {} # 记录已经计算过的前提
    if calculated_premise_dict:
        # 如果有已计算的前提，则直接使用
        now_premise_data = calculated_premise_dict
    fixed_weight = 0 # 固定权重

    # 无意识模式判定
    if unconscious_pass_flag == False and handle_unconscious_flag_ge_1(target_character_id):
        # 有技艺tag的行为则直接通过
        behavior_data = game_config.config_behavior[behavior_id]
        if _("技艺") in behavior_data.tag:
            unconscious_pass_flag = True
        # 需要前提里有无意识的判定
        for now_premise in talk_premise_dict:
            # 如果前提里有无意识，则正常通过
            if "unconscious" in now_premise:
                unconscious_pass_flag = True
                break
        # 如果没有无意识的前提，则直接返回0
        if not unconscious_pass_flag:
            return 0, now_premise_data

    # 口球判定
    if (
        (handle_self_now_gag(character_id) and "self_now_gag" not in talk_premise_dict and behavior_id not in {constant.Behavior.GAG_ON, constant.Behavior.GAG_OFF, constant.SecondBehavior.GAG}) or
        handle_self_now_gag(target_character_id) and "target_now_gag" not in talk_premise_dict and behavior_id not in {constant.Behavior.GAG_ON, constant.Behavior.GAG_OFF, constant.SecondBehavior.GAG}
        ):
        return 0, now_premise_data

    # 遍历前提字典
    for premise in talk_premise_dict:
        # 判断是否为权重类空白前提
        if premise[:5] == "high_":
            high_flag = True
        else:
            high_flag = False
        # 已录入前提的判定
        if premise in now_premise_data:
            if not now_premise_data[premise]:
                now_weight = 0
                break
            else:
                if weight_all_to_1_flag and not high_flag:
                    now_weight += 1
                else:
                    now_weight += now_premise_data[premise]
        else:
            # 综合数值前提判定
            if "CVP" in premise:
                premise_all_value_list = premise.split("_")[1:]
                # 如果是权重前提
                if premise_all_value_list[1] == "Weight|0":
                    fixed_weight = int(premise_all_value_list[-1])
                    # 最小为1，最大为999
                    fixed_weight = max(1, min(fixed_weight, 999))
                    continue
                now_add_weight = handle_comprehensive_value_premise(character_id, premise_all_value_list)
                now_premise_data[premise] = now_add_weight
            # 其他正常口上判定
            else:
                # 正常前提
                if premise in constant.handle_premise_data:
                    now_add_weight = constant.handle_premise_data[premise](character_id)
                    now_premise_data[premise] = now_add_weight
                # 不存在的前提
                else:
                    now_add_weight = 0
                    now_premise_data[premise] = 0
                    print(f"\ndebug 前提{premise}不存在，请检查前提是否正确\n")
            # 计算总权重
            if now_add_weight:
                if weight_all_to_1_flag and not high_flag:
                    now_weight += 1
                else:
                    now_weight += now_add_weight
            else:
                now_weight = 0
                break
    # 如果权重大于0且有固定权重，则变为固定权重
    if now_weight > 0 and fixed_weight > 0:
        now_weight = fixed_weight
    return now_weight, now_premise_data


def handle_comprehensive_value_premise(character_id: int, premise_all_value_list: list) -> int:
    """
    综合型基础数值前提
    Keyword arguments:
    character_id -- 角色id
    premise_all_value_list -- 前提的各项数值
    Return arguments:
    int -- 前提权重加成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data = cache.character_data[0]
    pl_target_character_id = pl_character_data.target_character_id
    pl_target_character_data = cache.character_data[pl_target_character_id]
    # print(f"debug character_id = {character_id}, premise_all_value_list = {premise_all_value_list}")

    # 进行主体A的判别，A1为自己，A2为交互对象，A3为指定id角色(格式为A3|15)
    if premise_all_value_list[0] == "A1":
        final_character_id = character_id
        final_character_data = character_data
    elif premise_all_value_list[0] == "A2":
        # 如果没有交互对象，则返回0
        if character_data.target_character_id == character_id:
            return 0
        final_character_id = character_data.target_character_id
        final_character_data = cache.character_data[character_data.target_character_id]
    elif premise_all_value_list[0][:2] == "A3":
        final_character_adv = int(premise_all_value_list[0][3:])
        final_character_id = character.get_character_id_from_adv(final_character_adv)
        final_character_data = cache.character_data[final_character_id]
        # 如果还没拥有该角色，则返回0
        if final_character_id not in cache.npc_id_got:
            return 0

    # 进行数值B的判别,A能力,T素质,Time时间,J宝珠,E经验,S状态,F好感度,Flag作者用flag,X信赖,G攻略程度,Instruct指令,Son子嵌套事件,OtherChara其他角色在场,Dirty污浊,Bondage绳子捆绑,Roleplay角色扮演,PenisPos阴茎位置,ShootPos射精位置,Relationship身份关系
    if (
        len(premise_all_value_list[1]) > 1 and
        "Time" not in premise_all_value_list[1] and
        "Dirty" not in premise_all_value_list[1] and
        "PenisPos" not in premise_all_value_list[1] and
        "ShootPos" not in premise_all_value_list[1] and
        "Relationship" not in premise_all_value_list[1] and
        "Instruct" not in premise_all_value_list[1]
        ):
        type_son_id = int(premise_all_value_list[1].split("|")[1])
    if "Son" in premise_all_value_list[1]:
        return 0
    if premise_all_value_list[1][0] == "A":
        final_value = final_character_data.ability.get(type_son_id, 0)
    elif premise_all_value_list[1][0] == "T":
        if "Time" in premise_all_value_list[1]:
            final_value = final_character_data.behavior.start_time.hour
        else:
            final_value = final_character_data.talent.get(type_son_id, 0)
    elif premise_all_value_list[1][0] == "J":
        final_value = final_character_data.juel.get(type_son_id, 0)
    elif premise_all_value_list[1][0] == "E":
        final_value = final_character_data.experience.get(type_son_id, 0)
    elif premise_all_value_list[1][0] == "S":
        if "ShootPos" in premise_all_value_list[1]:
            b2_value = premise_all_value_list[1].split("ShootPos|")[1]
            part_type = b2_value[0]
            part_cid = int(b2_value[1:])
            # 区分是身体还是服装
            if part_type == "B":
                if pl_target_character_data.h_state.shoot_position_body == part_cid:
                    return 1
            else:
                if pl_target_character_data.h_state.shoot_position_cloth == part_cid:
                    return 1
            return 0
        else:
            final_value = final_character_data.status_data.get(type_son_id, 0)
    elif premise_all_value_list[1][0] == "F":
        if "Flag" in premise_all_value_list[1]:
            final_character_data.author_flag.chara_int_flag_dict.setdefault(type_son_id, 0)
            final_value = final_character_data.author_flag.chara_int_flag_dict[type_son_id]
        else:
            final_value = final_character_data.favorability[0]
    elif premise_all_value_list[1][0] == "X":
        final_value = final_character_data.trust
    elif premise_all_value_list[1][0] == "D":
        if "Dirty" in premise_all_value_list[1]:
            b2_value = premise_all_value_list[1].split("Dirty|")[1]
            part_type = b2_value[0]
            part_cid = int(b2_value[1:])
            # 区分是身体还是服装
            if part_type == "B":
                final_value = final_character_data.dirty.body_semen[part_cid][1]
            else:
                final_value = final_character_data.dirty.cloth_semen[part_cid][1]
    elif premise_all_value_list[1][0] == "G":
        # 礼物前提
        if "Gift" in premise_all_value_list[1]:
            if final_character_data.behavior.gift_id == type_son_id:
                return 1
            else:
                return 0
        final_value = attr_calculation.get_character_fall_level(final_character_id, minus_flag=True)
    elif premise_all_value_list[1][0] == "B":
        if "Bondage" in premise_all_value_list[1]:
            if final_character_data.h_state.bondage == type_son_id:
                final_value = 1
            else:
                final_value = 0
    elif premise_all_value_list[1][0] == "R":
        if "Roleplay" in premise_all_value_list[1]:
            if type_son_id in final_character_data.hypnosis.roleplay:
                final_value = 1
            else:
                final_value = 0
        elif "Relationship" in premise_all_value_list[1]:
            target_character_type = premise_all_value_list[1].split("|")[1]
            if target_character_type == "是玩家的":
                target_character_data = cache.character_data[0]
            elif target_character_type == "是自己的":
                target_character_data = final_character_data
            elif target_character_type == "是交互对象的":
                target_character_data = cache.character_data[final_character_data.target_character_id]
            elif target_character_type == "是指定id角色的":
                target_character_adv = int(premise_all_value_list[3])
                target_character_id = character.get_character_id_from_adv(target_character_adv)
                target_character_data = cache.character_data[target_character_id]
            relation_type = premise_all_value_list[2]
            if relation_type == "父亲":
                return final_character_id == target_character_data.relationship.father_id
            elif relation_type == "母亲":
                return final_character_id == target_character_data.relationship.mother_id
            elif relation_type == "女儿":
                return final_character_id in target_character_data.relationship.child_id_list

    elif premise_all_value_list[1][0] == "P":
        if "PenisPos" in premise_all_value_list[1]:
            b2_value = premise_all_value_list[1].split("PenisPos|")[1]
            part_type = b2_value[0]
            part_cid = int(b2_value[1:])
            # 区分是身体还是服装
            if part_type == "B":
                if pl_target_character_data.h_state.insert_position == part_cid:
                    return 1
            else:
                if pl_target_character_data.h_state.insert_position - 20 == part_cid:
                    return 1
            return 0

    # 前指令的单独计算
    elif premise_all_value_list[1][0] == "I":
        if "Instruct" in premise_all_value_list[1]:
            len_pre_behavior = len(cache.pl_pre_behavior_instruce)
            behavior_id_str = "_".join(premise_all_value_list[1:-2])
            premise_all_value_list[1] = behavior_id_str
            premise_all_value_list = premise_all_value_list[:2] + premise_all_value_list[-2:]
            behavior_id = behavior_id_str.split("|")[1]
            # print(f"debug behavior_id = {behavior_id}, premise_all_value_list = {premise_all_value_list}")
            # 指令计数
            count = 0
            for i in range(len_pre_behavior):
                last_cmd = cache.pl_pre_behavior_instruce[len_pre_behavior - 1 - i]
                # 跳过当前指令
                if count == 0:
                    count += 1
                    continue
                if last_cmd == behavior_id:
                    # 判定是否为该指令
                    if premise_all_value_list[2] == "E":
                        return 1
                    if premise_all_value_list[2] == "NE":
                        return 0
                if premise_all_value_list[2] == "E":
                    return 0
                if premise_all_value_list[2] == "NE":
                    return 1
            return 0

    # 进行方式C和数值D的判别
    judge_value = int(premise_all_value_list[3])
    # print(f"debug final_value = {final_value}, judge_value = {judge_value}")

    # 攻略程度的不过0处理
    if premise_all_value_list[1][0] == "G":
        # 如果当前值与判定值的正负号不同，则直接返回0
        if (final_value > 0 and judge_value < 0) or (final_value < 0 and judge_value > 0):
            return 0
        # 如果是在大于，或者大于等于负数的情况下，则当前值最大为0
        if premise_all_value_list[2] in {"G", "GE"} and judge_value < 0:
            final_value = min(0, final_value)
        # 如果是在小于，或者小于等于正数的情况下，则当前值最小为0
        elif premise_all_value_list[2] in {"L", "LE"} and judge_value > 0:
            final_value = max(0, final_value)


    # 其他角色在场的判定
    if premise_all_value_list[1][0] == "O":
        if "OtherChara" in premise_all_value_list[1]:
            if character_data.position == final_character_data.position:
                return 1 if judge_value >= 1 else 0
            else:
                return 0 if judge_value >= 1 else 1

    # 正常的运算符判定
    if premise_all_value_list[2] == "G":
        if final_value > judge_value:
            # print(f"debug 成功进入G判定，返回值为1")
            return 1
    elif premise_all_value_list[2] == "L":
        if final_value < judge_value:
            return 1
    elif premise_all_value_list[2] == "E":
        if final_value == judge_value:
            return 1
    elif premise_all_value_list[2] == "GE":
        if final_value >= judge_value:
            return 1
    elif premise_all_value_list[2] == "LE":
        if final_value <= judge_value:
            return 1
    elif premise_all_value_list[2] == "NE":
        if final_value != judge_value:
            return 1

    return 0

def settle_chara_unnormal_flag(character_id: int, unnormal_flag_index: Optional[int]) -> None:
    """
    结算角色异常状态标记并同步位掩码，索引为None或0时重新结算全部异常。
    Keyword arguments:
    character_id -- 角色id
    unnormal_flag_index -- 异常状态标记索引
    Return arguments:
    None
    """
    character_data: game_type.Character = cache.character_data[character_id]
    unnormal_flag = _ensure_unnormal_flag_storage(character_data)
    if not unnormal_flag_index:
        unnormal_flag.set_mask(_calculate_unnormal_flag_mask(character_id))
        return
    handler = _get_unnormal_flag_handlers().get(unnormal_flag_index)
    if handler is None:
        return
    unnormal_flag.mark_unknown(unnormal_flag_index)
    is_normal = bool(handler(character_id))
    unnormal_flag.update(unnormal_flag_index, not is_normal)


@add_premise(constant_promise.Premise.HIGH_1)
def handle_high_1(character_id: int) -> int:
    """
    优先度为1的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 1


@add_premise(constant_promise.Premise.HIGH_2)
def handle_high_2(character_id: int) -> int:
    """
    优先度为2的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 2


@add_premise(constant_promise.Premise.HIGH_5)
def handle_high_5(character_id: int) -> int:
    """
    优先度为5的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 5


@add_premise(constant_promise.Premise.HIGH_10)
def handle_high_10(character_id: int) -> int:
    """
    优先度为10的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 10


@add_premise(constant_promise.Premise.HIGH_999)
def handle_high_999(character_id: int) -> int:
    """
    优先度为999的空白前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 999


@add_premise(constant_promise.Premise.PLAYER_CAN_BE_INTERACT)
def handle_player_can_be_interact(character_id: int) -> int:
    """
    玩家当前可被交互（非睡觉、非隐藏等），自己非空气催眠
    输入：character_id: int - 角色id
    输出：int - 权重
    """
    # 非睡觉状态
    if handle_pl_action_sleep(0):
        return 0
    # 非隐藏状态
    if handle_hidden_sex_mode_3(0):
        return 0
    if handle_hidden_sex_mode_4(0):
        return 0
    # 自己非空气催眠
    if handle_unconscious_flag_5(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_LOW_OBSCENITY)
def handle_instruct_judge_low_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值足以对自己轻度性骚扰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    if instuct_judege.calculation_instuct_judege(0, character_id, _("初级骚扰"), not_draw_flag = True)[0]:
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_INSTRUCT_JUDGE_LOW_OBSCENITY)
def handle_target_instruct_judge_low_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值足以对交互对象轻度性骚扰
    输入：character_id: int - 角色id
    输出：int - 权重
    """
    # 获取角色数据
    character_data = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    # 如果角色没有交互对象则返回0
    if character_id == target_character_id:
        return 0
    # 判断交互对象是否满足低级骚扰条件（调用计算函数判断低级骚扰）
    if instuct_judege.calculation_instuct_judege(character_id, target_character_id, _("初级骚扰"), not_draw_flag=True)[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INSTRUCT_NOT_JUDGE_LOW_OBSCENITY)
def handle_target_instruct_not_judge_low_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值不足以对交互对象轻度性骚扰
    输入：character_id: int - 角色id
    输出：int - 权重
    """
    return not handle_target_instruct_judge_low_obscenity(character_id)


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_HIGH_OBSCENITY)
def handle_instruct_judge_high_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值足以对自己重度性骚扰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    if instuct_judege.calculation_instuct_judege(0, character_id, _("严重骚扰"), not_draw_flag = True)[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INSTRUCT_JUDGE_HIGH_OBSCENITY)
def handle_target_instruct_judge_high_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值足以对交互对象重度性骚扰
    参数:
        character_id (int): 角色id
    返回:
        int: 权重（1 表示满足，0 表示不满足）
    """
    # 获取当前角色数据
    character_data = cache.character_data[character_id]
    # 获取交互对象id
    target_character_id = character_data.target_character_id
    # 如果角色没有交互对象，则直接返回0
    if character_id == target_character_id:
        return 0
    # 调用评价函数判断交互对象是否满足“严重骚扰”条件
    if instuct_judege.calculation_instuct_judege(character_id, target_character_id, _("严重骚扰"), not_draw_flag=True)[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INSTRUCT_NOT_JUDGE_HIGH_OBSCENITY)
def handle_target_instruct_not_judge_high_obscenity(character_id: int) -> int:
    """
    口上用：当前实行值不足以对交互对象重度性骚扰
    参数:
        character_id (int): 角色id
    返回:
        int: 权重（1 表示满足，0 表示不满足）
    """
    return not handle_target_instruct_judge_high_obscenity(character_id)


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_H)
def handle_instruct_judge_h(character_id: int) -> int:
    """
    口上用：当前实行值足以对自己邀请H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    if instuct_judege.calculation_instuct_judege(0, character_id, _("H模式"), not_draw_flag = True)[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INSTRUCT_JUDGE_H)
def handle_target_instruct_judge_h(character_id: int) -> int:
    """
    口上用：当前实行值足以对交互对象邀请H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    if character_id == target_character_id:
        return 0
    if instuct_judege.calculation_instuct_judege(character_id, target_character_id, _("H模式"), not_draw_flag = True)[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INSTRUCT_NOT_JUDGE_H)
def handle_target_instruct_not_judge_h(character_id: int) -> int:
    """
    口上用：当前实行值不足以对交互对象邀请H
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_target_instruct_judge_h(character_id)


@add_premise(constant_promise.Premise.INSTRUCT_JUDGE_GROUP_SEX)
def handle_instruct_judge_group_sex(character_id: int) -> int:
    """
    口上用：当前实行值足以对自己邀请群交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id == 0:
        return 0
    if instuct_judege.calculation_instuct_judege(0, character_id, _("群交"), not_draw_flag = True)[0]:
        return 1
    return 0


@add_premise(constant_promise.Premise.INSTRUCT_NOT_JUDGE_GROUP_SEX)
def handle_instruct_not_judge_group_sex(character_id: int) -> int:
    """
    口上用：当前实行值不足以对自己邀请群交
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_instruct_judge_group_sex(character_id)


@add_premise(constant_promise.Premise.TARGET_HAVE_CHARA_DIY_INSTRUCT)
def handle_target_have_chara_diy_instruct(character_id: int) -> int:
    """
    交互对象有角色自定义指令且至少有一个序号0的子事件满足全前提
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.UI.Panel import event_option_panel
    len_son_event_list, son_event_list = event_option_panel.get_target_chara_diy_instruct(character_id)
    if len_son_event_list:
        return 1
    return 0


@add_premise(constant_promise.Premise.NO_TARGET_OR_TARGET_CAN_COOPERATE)
def handle_no_target_or_target_can_cooperate(character_id: int) -> int:
    """
    无交互对象或交互对象可以协同指令
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == 0:
        return 1
    # 交互对象：HP正常，未疲劳，未睡眠，267正常
    elif (
        handle_target_hp_ne_1(character_id) and
        handle_t_tired_le_84(character_id) and
        handle_t_action_not_sleep(character_id) and
        handle_normal_2(character_data.target_character_id) and
        handle_normal_6(character_data.target_character_id) and
        handle_normal_7(character_data.target_character_id)
        ):
        return 1
    return 0


@add_premise(constant_promise.Premise.NO_TARGET_OR_TARGET_CAN_COOPERATE_OR_IMPRISONMENT_1)
def handle_no_target_or_target_can_cooperate_or_imprisonment_1(character_id: int) -> int:
    """
    无交互对象或交互对象可以协同指令或交互对象被监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_no_target_or_target_can_cooperate(character_id):
        return 1
    elif handle_t_imprisonment_1(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.NORMAL_ALL)
def handle_normal_all(character_id: int) -> int:
    """
    没有任何异常的绝对正常状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_1_2_4)
def handle_normal_1_2_4(character_id: int) -> int:
    """
    124正常的普通状态
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n包括2:临盆、产后、监禁
    \n包括4:大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_4(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2_3_4)
def handle_normal_2_3_4(character_id: int) -> int:
    """
    234正常的普通状态
    \n包括2:临盆、产后、监禁
    \n包括3:助理、跟随、体检
    \n包括4:大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2_5_6)
def handle_normal_2_5_6(character_id: int) -> int:
    """
    256正常的普通状态
    \n包括2:临盆、产后、监禁
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_1)
def handle_normal_1(character_id: int) -> int:
    """
    1正常的普通状态
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 1)
    if quick_result is not None:
        return quick_result
    if(
        handle_rest_flag_1(character_id)
        or handle_sleep_flag_1(character_id)
        or handle_pee_flag_1(character_id)
        or handle_eat_food_flag_ge_1(character_id)
        or handle_shower_flag_123(character_id)
        or handle_milk_flag_1(character_id)
        or handle_masturebate_flag_g_0(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_2)
def handle_normal_2(character_id: int) -> int:
    """
    \n2:AI行动基本停止：临盆、产后、监禁
    \n包括2:临盆、产后、监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 2)
    if quick_result is not None:
        return quick_result
    if(
        handle_parturient_1(character_id)
        or handle_postpartum_1(character_id)
        or handle_imprisonment_1(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_3)
def handle_normal_3(character_id: int) -> int:
    """
    3正常的普通状态
    \n3:高优先级AI：助理、跟随、体检
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 3)
    if quick_result is not None:
        return quick_result
    if(
        handle_is_assistant(character_id)
        or handle_is_follow(character_id)
        or handle_self_in_health_check_action_chain(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_4)
def handle_normal_4(character_id: int) -> int:
    """
    4正常的普通状态
    \n4:服装异常：大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 4)
    if quick_result is not None:
        return quick_result
    if(
        handle_cloth_off(character_id)
        or handle_cloth_most_off(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_5)
def handle_normal_5(character_id: int) -> int:
    """
    5正常的普通状态
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 5)
    if quick_result is not None:
        return quick_result
    if(
        (handle_sleep_level_0(character_id) and (handle_action_sleep(character_id) or handle_unconscious_flag_1(character_id)))
        or handle_unconscious_flag_4(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_6)
def handle_normal_6(character_id: int) -> int:
    """
    6正常的普通状态
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 6)
    if quick_result is not None:
        return quick_result
    if(
         (handle_sleep_level_ge_1(character_id) and (handle_action_sleep(character_id) or handle_unconscious_flag_1(character_id)))
        or handle_unconscious_flag_5(character_id)
        or (handle_time_stop_on(character_id) or handle_unconscious_flag_3(character_id))
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_7)
def handle_normal_7(character_id: int) -> int:
    """
    7正常的普通状态
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    quick_result = _quick_check_normal_by_mask(character_id, 7)
    if quick_result is not None:
        return quick_result
    if(
        handle_be_bagged_1(character_id)
        or handle_field_commission_1(character_id)
        or handle_t_baby_1(character_id)
        or handle_in_diplomatic_visit_1_and_other_country(character_id)
        or handle_escaping_1(character_id)
    ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_2_4)
def handle_normal_2_4(character_id: int) -> int:
    """
    24正常的普通状态
    \n包括2:临盆、产后、监禁
    \n包括4:大致全裸、全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_4(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_267)
def handle_normal_267(character_id: int) -> int:
    """
    267正常（可能基础异常、高优先级AI、服装异常或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_2467)
def handle_normal_2467(character_id: int) -> int:
    """
    2467正常（可能基础异常、高优先级AI或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_2467)
def handle_t_normal_2467(character_id: int) -> int:
    """
    交互对象2467正常（可能基础异常、高优先级AI或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_2(target_chara_id) and 
        handle_normal_4(target_chara_id) and 
        handle_normal_6(target_chara_id) and 
        handle_normal_7(target_chara_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_23467)
def handle_normal_23467(character_id: int) -> int:
    """
    23467正常（可能基础异常或意识模糊）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n3:高优先级AI：助理、跟随、体检
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_24567)
def handle_normal_24567(character_id: int) -> int:
    """
    24567正常（可能基础异常、高优先级AI）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_24567)
def handle_t_normal_24567(character_id: int) -> int:
    """
    交互对象24567正常（可能基础异常、高优先级AI）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_2(target_chara_id) and 
        handle_normal_4(target_chara_id) and 
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id) and 
        handle_normal_7(target_chara_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_124567)
def handle_normal_124567(character_id: int) -> int:
    """
    124567正常（可能基础异常、高优先级AI）
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n2:AI行动基本停止：临盆、产后、监禁
    \n4:服装异常：大致全裸、全裸
    \n5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_1267)
def handle_normal_1267(character_id: int) -> int:
    """
    1267正常（可能高优先级AI、服装异常或意识模糊）
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n2:AI行动基本停止：临盆、产后、监禁
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.NORMAL_123467)
def handle_normal_123467(character_id: int) -> int:
    """
    123467正常（可能意识模糊）
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    \n2:AI行动基本停止：临盆、产后、监禁
    \n3:高优先级AI：助理、跟随、体检
    \n4:服装异常：大致全裸、全裸
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_1(character_id) and 
        handle_normal_2(character_id) and 
        handle_normal_3(character_id) and 
        handle_normal_4(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_1)
def handle_t_normal_1(character_id: int) -> int:
    """
    交互对象1正常的普通状态
    \n1:基础生理需求：休息、睡觉、解手、吃饭、沐浴（不含已洗澡）、挤奶、自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_normal_2(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_2)
def handle_t_normal_2(character_id: int) -> int:
    """
    交互对象2正常的普通状态
    \n包括2:临盆、产后、监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_normal_2(character_data.target_character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_6)
def handle_t_normal_6(character_id: int) -> int:
    """
    交互对象6正常的普通状态
    \n6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_normal_6(target_chara_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.UNNORMAL)
def handle_unnormal(character_id: int) -> int:
    """
    有特殊需求的异常状态
    \n包括1~7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return 1 if refresh_unnormal_flag(character_id) else 0


@add_premise(constant_promise.Premise.UNNORMAL_2)
def handle_unnormal_2(character_id: int) -> int:
    """
    2异常
    \n2:AI行动基本停止：临盆、产后、监禁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.UNNORMAL_27)
def handle_unnormal_27(character_id: int) -> int:
    """
    27异常（AI停止或离线）
    \n2:AI行动基本停止：临盆、产后、监禁
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_2(character_id) and 
        handle_normal_7(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_NORMAL_5_6)
def handle_t_normal_5_6(character_id: int) -> int:
    """
    交互对象56正常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_NORMAL_5_6_OR_UNCONSCIOUS_FLAG_4_7)
def handle_t_normal_5_6_or_unconscious_flag_4_7(character_id: int) -> int:
    """
    交互对象56正常或平然或心控
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_t_normal_5_6(character_id) or handle_t_unconscious_flag_4(character_id) or handle_t_unconscious_flag_7(character_id):
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.T_UNNORMAL_5_6)
def handle_t_unnormal_5_6(character_id: int) -> int:
    """
    交互对象5异常或6异常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_UNNORMAL_6)
def handle_t_unnormal_6(character_id: int) -> int:
    """
    交互对象6异常
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if handle_normal_6(target_chara_id):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.UNNORMAL_567)
def handle_unnormal_567(character_id: int) -> int:
    """
    自身5或6或7异常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if (
        handle_normal_5(character_id) and 
        handle_normal_6(character_id) and 
        handle_normal_7(character_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG)
def handle_t_normal_256_or_unconscious_flag(character_id: int) -> int:
    """
    交互对象256正常或无意识
    \n包括2:临盆、产后、监禁
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_2(target_chara_id) and 
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 1
    if target_data.sp_flag.unconscious_h != 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NORMAL_56_OR_UNCONSCIOUS_FLAG)
def handle_t_normal_56_or_unconscious_flag(character_id: int) -> int:
    """
    交互对象56正常或无意识
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id)
        ):
        return 1
    if target_data.sp_flag.unconscious_h != 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UNNORMAL_567)
def handle_t_unnormal_567(character_id: int) -> int:
    """
    交互对象5或6或7异常
    \n包括5:意识模糊，或弱交互：睡眠（半梦半醒），醉酒，平然
    \n包括6:完全意识不清醒，或无交互：睡眠（浅睡或熟睡或完全深眠），时停，空气
    \n7:角色离线：装袋搬走、外勤、婴儿、他国外交访问、逃跑中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_chara_id = character_data.target_character_id
    if (
        handle_normal_5(target_chara_id) and 
        handle_normal_6(target_chara_id) and 
        handle_normal_7(target_chara_id)
        ):
        return 0
    else:
        return 1


@add_premise(constant_promise.Premise.NORMAL_ALL_EXCEPT_SPECIAL_HYPNOSIS)
def handle_normal_all_except_special_hypnosis(character_id: int) -> int:
    """
    没有任何异常的普通状态或被空气或体控催眠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_normal_all(character_id):
        return 1
    elif (
        handle_unconscious_flag_5(character_id) or
        handle_unconscious_flag_6(character_id)
        ):
        return 1
    else:
        return 0

@add_premise(constant_promise.Premise.HAVE_INSTRUMENT_OR_IN_MUSIC_ROOM)
def handle_have_instrument_or_in_music_room(character_id: int) -> int:
    """
    校验角色是否已持有乐器或在乐器练习室里
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_have_instrument(character_id):
        return 1
    if handle_in_music_room(character_id):
        return 1
    return 0

@add_premise(constant_promise.Premise.DESIRE_POINT_GE_80_OR_MASTUREBATE_TO_PL_FLAG_1)
def handle_masturebate_to_pl_flag_1_or_desire_point_ge_80(character_id: int) -> int:
    """
    校验角色自身欲望值≥80或要找玩家逆推来自慰状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_desire_point_ge_80(character_id):
        return 1
    if handle_masturebate_to_pl_flag_1(character_id):
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_IS_ASSISTANT_AND_IN_DR_ROOM)
def handle_not_is_assistant_and_in_dr_room(character_id: int) -> int:
    """
    不符合自己是当前的助理干员且正在博士房间里的条件
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_is_assistant(character_id) and handle_in_dr_room(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.T_WORK_IS_WARDEN_OR_T_ASSISTANT)
def handle_t_work_is_warden_or_t_assistant(character_id: int) -> int:
    """
    交互对象的工作为监狱长或交互对象是助理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_work_is_warden(character_data.target_character_id):
        return 1
    if handle_is_assistant(character_data.target_character_id):
        return 1
    return 0
