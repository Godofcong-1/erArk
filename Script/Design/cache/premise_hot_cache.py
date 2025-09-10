"""
热前提缓存与 normal 位图支持 (最小实现)

使用方式：
- 在 handle_premise 内部调用 get_premise_cached() 包裹原前提函数
- 通过 increase_normal_status_version(character_id) 使与 normal 状态相关的缓存失效
- normal_XXXX 形式的组合前提由位图快速判定

注意：
- 这里假设有 cache_control.cache 可用
- 如需更细粒度失效，可再扩展 category -> version
"""

from __future__ import annotations
from typing import Dict, Tuple, Callable
from Script.Core import cache_control, game_type
from Script.Core.constant import Behavior

cache = cache_control.cache

# 角色 -> { premise_id: (version, value) }
_premise_cache: Dict[int, Dict[str, Tuple[int, int]]] = {}

# 角色 -> normal 状态位图版本号
_normal_version: Dict[int, int] = {}
# 角色 -> 最近一次计算的 normal 位图 (int)
_normal_mask: Dict[int, int] = {}

# 全局：角色 normal 状态版本统一计数器（也可按角色各自维护，这里简单共享增量）
_global_normal_epoch: int = 1

# 基础 normal 状态 bit 映射 (示例：你要根据真实“normal_1..7” 或 “2 5 6”等含义修改)
# 假设 1~7 对应：
# 1 = 意识正常, 2 = 未被催眠, 3 = 非睡眠, 4 = 非跟随异常, 5 = 服装正常, 6 = 未被监禁, 7 = 其他可行动
# 真实请替换为项目内部判断来源
NORMAL_BIT_DESC = {
    1: "conscious",
    2: "not_hypnosis",
    3: "not_sleeping",
    4: "can_move",
    5: "cloth_ok",
    6: "not_imprisoned",
    7: "other_ok",
}

def increase_normal_status_version(character_id: int):
    """当任何一个基础 normal 相关状态变化后调用，使该角色的 normal 前提与依赖缓存失效。"""
    global _global_normal_epoch
    _global_normal_epoch += 1
    _normal_version[character_id] = _global_normal_epoch
    # 同时清理该角色相关前提缓存（也可以只删除 normal_* 相关，这里简单全删）
    _premise_cache.pop(character_id, None)


def _compute_normal_mask(character_id: int) -> int:
    """
    计算角色当前 normal 基础位图。
    这里放示例逻辑，需替换为真实判定：
    返回一个整数，每一位代表一个基础 normal 条件满足(=1)。
    """
    char: game_type.Character = cache.character_data[character_id]
    if not char:
        return 0

    # TODO: 根据真实字段替换以下示例：
    # 下方示例假设：
    # char.sp_flag.xxx 或 char.state / char.behavior 等字段可判断
    mask = 0
    # 1 conscious
    if char.sp_flag.unconscious_h == 0:
        mask |= (1 << 0)
    # 2 not hypnosis
    if char.sp_flag.unconscious_h > 0:
        mask |= (1 << 1)
    # 3 not sleeping
    if char.behavior.behavior_id != Behavior.SLEEP:
        mask |= (1 << 2)
    # 4 can move
    if not getattr(char.sp_flag, "cant_move", 0):
        mask |= (1 << 3)
    # 5 cloth ok
    if not getattr(char.sp_flag, "cloth_abnormal", 0):
        mask |= (1 << 4)
    # 6 not imprisoned
    if not getattr(char.sp_flag, "imprisoned", 0):
        mask |= (1 << 5)
    # 7 other ok
    mask |= (1 << 6)

    return mask


def get_normal_mask(character_id: int) -> Tuple[int, int]:
    """
    返回 (normal_mask, version)
    如果版本更新或未计算则重新计算。
    """
    current_ver = _normal_version.get(character_id, 0)
    last_mask = _normal_mask.get(character_id)
    if last_mask is None:
        # 首次
        current_ver = _global_normal_epoch
        _normal_version[character_id] = current_ver
        mask_val = _compute_normal_mask(character_id)
        _normal_mask[character_id] = mask_val
        return mask_val, current_ver
    return last_mask, current_ver


def fast_check_normal_premise(premise_id: str, character_id: int) -> int:
    """
    针对 normal_* 组合做快速判断。
    支持格式：
        normal_123467 (任意顺序数字指代全部必须满足)
        normal_2_5_6  (下划线分隔)
        normal_all
        normal_all_except_special_hypnosis (示例)
    返回 0/1 （你原来部分返回高权重，可在这里统一返回 1，需要的话外层可再转换）
    """
    lower = premise_id.lower()
    if lower == "normal_all":
        # 要求 1..7 全部
        mask, _ver = get_normal_mask(character_id)
        needed = (1 << 7) - 1  # 7 bits
        return 1 if (mask & needed) == needed else 0
    if lower == "normal_all_except_special_hypnosis":
        # 例：排除第二位 hypnosis
        mask, _ver = get_normal_mask(character_id)
        # bits 0..6 except bit1
        needed = ((1 << 7) - 1) & ~(1 << 1)
        return 1 if (mask & needed) == needed else 0
    if lower.startswith("normal_"):
        # 抽取数字（支持 123467 或 2_5_6）
        core = lower[len("normal_") :]
        digits = []
        if "_" in core:
            for part in core.split("_"):
                if part.isdigit():
                    digits.append(int(part))
        else:
            for ch in core:
                if ch.isdigit():
                    digits.append(int(ch))
        if not digits:
            return 0
        mask, _ver = get_normal_mask(character_id)
        for d in digits:
            if d < 1 or d > 7:
                return 0
            if not (mask & (1 << (d - 1))):
                return 0
        return 1
    return -1  # 表示不是 normal 组合前提


def get_premise_cached(character_id: int, premise_id: str, version_seed: int, compute: Callable[[], int]) -> int:
    """
    通用缓存入口。
    version_seed 用于外部附加（例如：normal_version 或 游戏时间版本号等）。
    目前简单传 normal_version，后续可拓展加 (normal_version << 某偏移) | other_version
    """
    role_cache = _premise_cache.setdefault(character_id, {})
    entry = role_cache.get(premise_id)
    if entry and entry[0] == version_seed:
        return entry[1]
    value = compute()
    role_cache[premise_id] = (version_seed, value)
    return value