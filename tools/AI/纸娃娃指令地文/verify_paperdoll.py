# -*- coding: UTF-8 -*-
"""在无头游戏里核对 H 指令纸娃娃地文：五档 + 通用、各无意识差分各自只命中自己那一组，整段展开无残留占位符

用法（buildconfig 之后，在仓库根目录运行）:
    .conda\\python.exe tools/AI/纸娃娃指令地文/verify_paperdoll.py <行为id>... [--samples]
    --all       核对 spec.json 里全部已生成 CSV 的行为
    --samples   每个行为每组打印一段展开样本
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "tests"))
from headless_base import *  # noqa: F401,F403
from Script.Design import talk
from Script.System.Education_System import education_constant

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], os.getcwd()] + sys.argv[1:]
import gen_paperdoll  # noqa: E402

SHOW_SAMPLES = "--samples" in sys.argv
behavior_list = [arg for arg in sys.argv[2:] if not arg.startswith("--")]
if "--all" in sys.argv:
    behavior_list = sorted(game_config.config_talk_common_action_part_type_set & set(gen_paperdoll.load_all_specs()))

npc = make_character(1, "测试干员")
player = cache.character_data[0]
player.target_character_id = 1
player.position = list(npc.position)
# 尾交、蹭角、蹭耳朵需要的素质（兽尾 / 兽角 / 兽耳）
for talent_id in (111, 112, 113):
    npc.talent[talent_id] = 1
# 每个服装部位穿上一件（取模板里该部位第一件不叫「无」的衣物），服装占位符才不会落到兜底文本
for cloth_id, cloth_data in sorted(game_config.config_clothing_tem.items()):
    if cloth_data.clothing_type not in npc.cloth.cloth_wear or not npc.cloth.cloth_wear[cloth_data.clothing_type]:
        if cloth_data.name != "无":
            npc.cloth.cloth_wear[cloth_data.clothing_type] = [cloth_id]

TIER_CASES = [(None, 0), (201, 1), (202, 1), (203, 2), (204, 2), (211, 3), (212, 3), (213, 4), (214, 4)]
FALL_TALENTS = [201, 202, 203, 204, 211, 212, 213, 214]
TIER_NAME = ["未陷落", "思慕·恋慕", "恋人·爱侣", "屈从·驯服", "宠物·奴隶"]
# 无意识差分: (unconscious_h, 是否装睡, 体控模式)
VARIANT_STATE = {
    "睡奸": (1, False, ""),
    "装睡": (1, True, ""),
    "醉酒": (2, False, ""),
    "时停": (3, False, ""),
    "平然": (4, False, ""),
    "空气": (5, False, ""),
    "木头人": (6, False, "blockhead"),
    "逆推": (6, False, "active_h"),
}
SEGMENT_FILES = {"A": ["A"], "B": ["B1", "B2"], "C": ["C1", "C2"]}


def set_fall(talent_id):
    """只保留指定的一个陷落素质"""
    for tid in FALL_TALENTS:
        npc.talent[tid] = 0
    if talent_id:
        npc.talent[talent_id] = 1


def set_variant(unconscious_h, pretend_sleep, hypnosis_mode):
    """设置交互对象的无意识状态"""
    npc.sp_flag.unconscious_h = unconscious_h
    npc.h_state.pretend_sleep = pretend_sleep
    npc.hypnosis.blockhead = hypnosis_mode == "blockhead"
    npc.hypnosis.active_h = hypnosis_mode == "active_h"


def hit_cids(behavior, part):
    """以玩家为主体求某段候选，返回命中的cid集合"""
    with talk.player_target_as(1):
        data, _cache = talk.get_talk_common_weight_data(game_config.config_talk_common_cid_list_by_part[behavior][part], {})
    return {c for cids in data.values() for c in cids}


def expect_cids(behavior, part, group_list):
    """若干组在某段应命中的cid集合"""
    result = set()
    for group in group_list:
        cid_value, _premise = gen_paperdoll.group_cid_premise(group, 0)
        for suffix in SEGMENT_FILES[part]:
            result |= {f"{behavior}_{suffix}{cid_value + i}" for i in range(gen_paperdoll.TEXTS_PER_GROUP)}
    return result


def expand(behavior):
    """以玩家为说话者整段展开一次"""
    return talk.code_text_to_draw_text("{" + behavior + "}", 0, True)


cache.all_system_setting.draw_setting[20] = 2
for behavior in behavior_list:
    section(behavior)
    player.behavior.behavior_id = behavior
    check(f"{behavior} 已登记为动作类分段", behavior in game_config.config_talk_common_action_part_type_set)
    check(f"{behavior} 有ABC三段", sorted(game_config.config_talk_common_cid_list_by_part.get(behavior, {})) == ["A", "B", "C"])
    samples = []
    set_variant(0, False, "")
    for talent_id, tier in TIER_CASES:
        set_fall(talent_id)
        for part in ("A", "B", "C"):
            hit = hit_cids(behavior, part)
            check(f"{behavior} 素质{talent_id} 档{tier} {part}段", hit == expect_cids(behavior, part, [tier, gen_paperdoll.GENERAL_GROUP]), sorted(hit)[:3])
        for _ in range(5):
            text = expand(behavior)
            check(f"{behavior} 档{tier} 整段展开", "{" not in text and "}" not in text and len([x for x in text.split("\n") if x]) == 3, repr(text))
        samples.append((TIER_NAME[tier], text))
    for name, state in VARIANT_STATE.items():
        set_variant(*state)
        # 未陷落与宠物档各查一次：无意识状态下五档与通用文本都不应混进来
        for talent_id in (None, 213):
            set_fall(talent_id)
            for part in ("A", "B", "C"):
                hit = hit_cids(behavior, part)
                check(f"{behavior} {name} 素质{talent_id} {part}段", hit == expect_cids(behavior, part, [name]), sorted(hit)[:3])
        for _ in range(5):
            text = expand(behavior)
            check(f"{behavior} {name} 整段展开", "{" not in text and "}" not in text and len([x for x in text.split("\n") if x]) == 3, repr(text))
        samples.append((name, text))
    set_variant(0, False, "")
    set_fall(None)
    if SHOW_SAMPLES:
        seen = set()
        for name, text in samples:
            if name not in seen:
                seen.add(name)
                print(f"\n【{behavior}·{name}】\n{text}")
finish()
