# -*- coding: UTF-8 -*-
"""
破处类行为的处女判定

处女类素质指素质 0~4：阴道处女、肛门处女、尿道处女、子宫处女、无接吻经验。
一个行为的tag里带「破处」，且带角色仍保有的某个处女类素质所对应的部位tag时，判定为「会夺走她还保有的处女」。
子宫（W）的破处行为结算时也会走阴道破处的结算、清掉阴道处女，所以阴道处女同时对应 V 与 W。

NPC主动H（逆推）、群交模板各部位的行为列表、调教助手可用的行为，这三处自动替玩家挑选行为的地方都用它跳过这类行为：
干员的各项第一次只能由玩家亲自用指令拿走，不会被自动挑选的行为顺手带走。

行为的tag不随语言翻译，这里一律用中文原文比较。
"""
from typing import Collection, Dict, Tuple

VIRGIN_TALENT_TAGS: Dict[int, Tuple[str, ...]] = {
    0: ("V", "W"),
    1: ("A",),
    2: ("U",),
    3: ("W",),
    4: ("N",),
}
""" 处女类素质id: 对应的部位tag，破处行为带其中任意一个就算会夺走该处女 """


def takes_kept_virginity(tag_list: Collection[str], talent: Dict[int, int]) -> bool:
    """
    按行为的tag判断它是否会夺走角色仍保有的某项处女
    Keyword arguments:
    tag_list -- 行为的tag列表（已按 | 拆开）
    talent -- 角色的素质数据，素质id: 素质值
    Return arguments:
    bool -- tag里带「破处」，且带角色仍保有的某个处女类素质对应的部位tag时为 True
    """
    if "破处" not in tag_list:
        return False
    for talent_id, part_tag_tuple in VIRGIN_TALENT_TAGS.items():
        if not talent.get(talent_id, 0):
            continue
        for part_tag in part_tag_tuple:
            if part_tag in tag_list:
                return True
    return False
