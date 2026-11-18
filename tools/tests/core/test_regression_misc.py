# -*- coding: UTF-8 -*-
"""零散的锁定修复：通用占位符嵌套替换、体检 AI（跟随中不去体检、体检科满员放弃当天体检）、失去泌乳后罩杯缩回、照料婴儿的干员不算离线、三处事件数据、隐奸高潮口上的人名、脱鞋袜进大浴场衣柜的精液表、生产事件的接生人选"""
from _bootstrap import *  # noqa: F401,F403
import csv
from unittest import mock

from Script.Design import handle_talent, talk
from Script.Settle import default_cloth
from Script.StateMachine import default as state_machine_default
from Script.System.Pregnancy_System import born_event_panel

# ==== 1. 通用占位符嵌套 ====
section("通用占位符嵌套：里层排在外层前面时也全部替换")


def always_pass(premise_set, character_id, calculated_premise_dict, **kwargs) -> tuple:
    """
    让每条候选文本都通过前提，只测替换逻辑本身
    Keyword arguments:
    premise_set -- 前提集合
    character_id -- 角色id
    calculated_premise_dict -- 已算过的前提
    Return arguments:
    tuple -- (权重 1, 原样的已算前提)
    """
    return 1, calculated_premise_dict


# 构造三层嵌套：outer 插入 {mid}，mid 插入 {inner}；加载顺序取最坏的 inner → mid → outer（只替换一遍时外层插入的里层占位符会原样留下）
fake_common_data = {
    "t_outer_1": mock.Mock(context="外[{mid}]", type_id="outer"),
    "t_mid_1": mock.Mock(context="中<{inner}>", type_id="mid"),
    "t_inner_1": mock.Mock(context="内", type_id="inner"),
}
fake_common_order = {"inner": ["t_inner_1"], "mid": ["t_mid_1"], "outer": ["t_outer_1"]}
with mock.patch.object(game_config, "config_talk_common_cid_list_by_type", fake_common_order), \
        mock.patch.object(game_config, "config_talk_common_data", fake_common_data), \
        mock.patch.object(game_config, "config_talk_common_premise_data", {now_cid: set() for now_cid in fake_common_data}), \
        mock.patch.object(game_config, "config_talk_common_cid_list_by_part", {}), \
        mock.patch.object(handle_premise, "get_weight_from_premise_dict", always_pass):
    nested_result = talk.talk_common_judge("{outer}", 0)
check("三层嵌套、里层的占位符类型排在外层前面：全部替换成最终文本", nested_result == "外[中<内>]", nested_result)

# ==== 2. 体检 AI ====
section("体检 AI：跟随中的干员不去体检，体检科满员时放弃当天体检")
HEALTH_TARGET_LIST = [now_cid for now_cid in game_config.config_target_premise_data if str(now_cid) in {"default210500", "default220505", "default220510"}]
""" AI 目标：去体检科（今日体检 / 等待名单）与在体检科原地等待。目标 cid 在载入时带上所在目录名作前缀（data/target/default） """
check("fixture：三条体检相关的 AI 目标都在目标表里", len(HEALTH_TARGET_LIST) == 3, HEALTH_TARGET_LIST)
bad = [now_cid for now_cid in HEALTH_TARGET_LIST if "not_follow" not in game_config.config_target_premise_data.get(now_cid, set())]
check("去体检科与等待体检的三条 AI 目标都要求「没有在跟随」（否则智能跟随中的干员在体检科与博士之间来回走）", not bad,
      {now_cid: sorted(game_config.config_target_premise_data.get(now_cid, set())) for now_cid in bad})

EXAM_NPC_ID = 9401
""" 排了体检的干员 fixture """
exam_room_str = constant.place_data["Physical_Examination"][0]
exam_room = cache.scene_data[exam_room_str]
exam_npc = make_character(EXAM_NPC_ID, "体检测试干员")
waiting_set = cache.rhodes_island.waiting_for_exam_operator_ids
saved_exam_list = set(exam_room.character_list)
saved_waiting = set(waiting_set)
check("fixture：体检科没满", not map_handle.judge_scene_is_full(exam_room_str))
exam_npc.action_info.health_check_today = 1
exam_npc.behavior = game_type.Behavior()
exam_npc.behavior.start_time = cache.game_time
state_machine_default.character_move_to_physical_examination(EXAM_NPC_ID)
check("体检科没满：排了体检的干员照常动身去体检科，今日体检不变", exam_npc.action_info.health_check_today == 1 and exam_npc.behavior.behavior_id == constant.Behavior.MOVE,
      (exam_npc.action_info.health_check_today, exam_npc.behavior.behavior_id))
exam_room.character_list.update(range(9410, 9420))
check("fixture：体检科坐满 10 人后满员", map_handle.judge_scene_is_full(exam_room_str))
exam_npc.action_info.health_check_today = 1
waiting_set.add(EXAM_NPC_ID)
exam_npc.behavior = game_type.Behavior()
exam_npc.behavior.start_time = cache.game_time
state_machine_default.character_move_to_physical_examination(EXAM_NPC_ID)
check("体检科满员：清掉今日体检并退出等待名单，原地发呆 1 分钟后回到日常行动（不在门口反复重试）",
      exam_npc.action_info.health_check_today == 0 and EXAM_NPC_ID not in waiting_set
      and exam_npc.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY and exam_npc.behavior.duration == 1,
      (exam_npc.action_info.health_check_today, EXAM_NPC_ID in waiting_set, exam_npc.behavior.behavior_id, exam_npc.behavior.duration))
exam_room.character_list.clear()
exam_room.character_list.update(saved_exam_list)
waiting_set.clear()
waiting_set.update(saved_waiting)
remove_character(EXAM_NPC_ID)

# ==== 3. 涨奶的罩杯 ====
section("失去泌乳后，涨奶时变大的罩杯缩回去")
CUP_TALENT_LIST = [121, 122, 123, 124, 125]
""" 罩杯素质：绝壁、贫乳、普乳、巨乳、爆乳 """
MILK_NPC_ID = 9402
milk_npc = make_character(MILK_NPC_ID, "涨奶测试干员")


def settle_cup() -> tuple:
    """
    跑一次涨奶罩杯结算
    Keyword arguments:
    无
    Return arguments:
    tuple -- (当前的罩杯素质id列表, 涨奶标记)
    """
    handle_talent.npc_b_talent_change_for_lactation_flag(MILK_NPC_ID)
    return [now_talent for now_talent in CUP_TALENT_LIST if milk_npc.talent[now_talent]], bool(milk_npc.pregnancy.lactation_flag)


for now_talent in CUP_TALENT_LIST:
    milk_npc.talent[now_talent] = 0
milk_npc.talent[122] = 1
milk_npc.talent[27] = 1
milk_npc.pregnancy.milk_max = 190
milk_npc.pregnancy.milk = 190
milk_npc.pregnancy.lactation_flag = False
check("泌乳中的贫乳干员涨奶：罩杯变成普乳并记下涨奶标记", settle_cup() == ([123], True))
milk_npc.talent[27] = 0
cup_after_stop = settle_cup()
check("失去泌乳素质（停乳药、育儿结束）后的下一次结算：罩杯缩回贫乳、清掉涨奶标记", cup_after_stop == ([122], False), cup_after_stop)
check("再结算一次不会继续缩", settle_cup() == ([122], False))
remove_character(MILK_NPC_ID)

# ==== 4. 离线判定 ====
section("照料婴儿的干员不算离线")
CARER_ID, BABY_ID = 9403, 9404
carer = make_character(CARER_ID, "保育测试干员")
baby = make_character(BABY_ID, "婴儿", daughter=True, stage=101, mother_id=CARER_ID)
carer.target_character_id = BABY_ID
handle_premise.refresh_unnormal_flag(CARER_ID)
check("交互对象是婴儿的干员重算异常位后仍在线（离线看的是她自己是不是婴儿，不是交互对象）", handle_premise.handle_normal_7(CARER_ID) == 1, handle_premise.handle_normal_7(CARER_ID))
handle_premise.refresh_unnormal_flag(BABY_ID)
check("婴儿自己是离线的", handle_premise.handle_normal_7(BABY_ID) == 0)
carer.target_character_id = CARER_ID
remove_character(BABY_ID)
remove_character(CARER_ID)

# ==== 5. 事件数据 ====
section("事件数据：袭击事件不解开博士锁的门、两个选项子事件能被选项面板列出")


def find_event(uid_prefix: str):
    """
    按 uid 前缀找一条事件
    Keyword arguments:
    uid_prefix -- 事件 uid 的前 8 位
    Return arguments:
    game_type.Event -- 事件对象，找不到为 None
    """
    for now_uid, now_event in game_config.config_event.items():
        if now_uid.startswith(uid_prefix):
            return now_event
    return None


ambush_event_list = [find_event("3bbe039d"), find_event("5ad89e16")]
check("fixture：找到干员袭击事件的两条「逆来顺受」（移动时与等待时各一条），它们都让博士进入被逆推的 H",
      all(now_event is not None and "CSE_A2_h_by_active" in now_event.effect for now_event in ambush_event_list))
check("「逆来顺受」的结算里没有「开门」（753）：博士原来锁上的门保持锁着", all(now_event is not None and "753" not in now_event.effect for now_event in ambush_event_list),
      [sorted(now_event.effect) for now_event in ambush_event_list if now_event is not None])
move_parent, move_son = find_event("da8a5d84"), find_event("5925c54e")
check("通用移动事件的选项子事件「不进去」带着父事件的全部前提（选项面板只列出前提包含父事件前提的子事件）",
      move_parent is not None and move_son is not None and set(move_parent.premise) <= set(move_son.premise) | {"option_father"},
      sorted(set(move_parent.premise) - set(move_son.premise)) if move_parent is not None and move_son is not None else "找不到事件")
chat_parent, chat_son = find_event("110b756a"), find_event("108c4126")
check("星熊聊天的选项子事件「爱抚」与父事件属于同一行为（选项面板只在当前行为的事件里找子事件）",
      chat_parent is not None and chat_son is not None and chat_son.behavior_id == chat_parent.behavior_id,
      (chat_parent.behavior_id if chat_parent is not None else None, chat_son.behavior_id if chat_son is not None else None))

# ==== 6. 高潮口上的人名 ====
section("隐奸高潮口上：高潮的人写成 {Name}")
CLIMAX_TALK_DIR = os.path.join(ROOT, "data", "talk", "system", "second_climax")
""" 系统的绝顶口上目录：这些口上由绝顶的干员本人触发，{Name} 是她自己，{TargetName} 是她的交互对象（通常是博士） """
bad = []
for file_name in sorted(os.listdir(CLIMAX_TALK_DIR)):
    if not file_name.endswith(".csv"):
        continue
    with open(os.path.join(CLIMAX_TALK_DIR, file_name), encoding="utf-8") as talk_file:
        for row in csv.reader(talk_file):
            if len(row) >= 5 and "hidden_sex_mode" in row[3] and "{TargetName}" in row[4]:
                bad.append((file_name, row[0]))
check("隐奸中的绝顶口上不用 {TargetName} 指代绝顶的干员（否则会把博士写成绝顶的人）", not bad, (len(bad), bad[:8]))

# ==== 7. 衣柜精液表 ====
section("脱鞋袜进大浴场衣柜：衣柜精液表补齐全部服装部位，穿回时精液回到鞋上")
LOCKER_NPC_ID = 9405
locker_npc = make_character(LOCKER_NPC_ID, "泡脚测试干员")
SHOE_SEMEN = 30
""" 脱鞋前鞋上的精液量（ml） """
sock_id = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 10 and now_tem.tag != 6)
shoe_id = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 11 and now_tem.tag != 6)
locker_npc.cloth.cloth_wear[10] = [sock_id]
locker_npc.cloth.cloth_wear[11] = [shoe_id]
# 新开局、新招募的角色衣柜精液表是空的（game_type.DIRTY 的默认值），最小 fixture 用 get_zero_dirty 建出来的是满表，这里还原成真实角色的样子
locker_npc.dirty.cloth_locker_semen = {}
locker_npc.dirty.cloth_semen[11][1] = SHOE_SEMEN
default_cloth.handle_foot_cloth_to_shower_locker(LOCKER_NPC_ID, 5, game_type.CharacterStatusChange(), cache.game_time)
check("鞋袜进了大浴场衣柜，鞋上的精液跟着进了衣柜的表", locker_npc.cloth.cloth_locker_in_shower[10] == [sock_id] and locker_npc.cloth.cloth_locker_in_shower[11] == [shoe_id]
      and locker_npc.dirty.cloth_semen[11][1] == 0 and locker_npc.dirty.cloth_locker_semen[11][1] == SHOE_SEMEN)
check("衣柜精液表覆盖全部服装部位（穿回时按全部部位读这张表）", sorted(locker_npc.dirty.cloth_locker_semen) == sorted(game_config.config_clothing_type),
      sorted(locker_npc.dirty.cloth_locker_semen))
check("衣柜表与穿着表的各部位不共用同一个列表", all(locker_npc.dirty.cloth_locker_semen[now_type] is not locker_npc.dirty.cloth_semen[now_type]
      for now_type in locker_npc.dirty.cloth_locker_semen if now_type in locker_npc.dirty.cloth_semen))
wear_back_error = ""
try:
    default_cloth.handle_shower_locker_to_wear(LOCKER_NPC_ID, 5, game_type.CharacterStatusChange(), cache.game_time)
except Exception as error:  # noqa: BLE001  要把异常类型写进断言的附带信息
    wear_back_error = repr(error)
check("泡完脚穿回鞋袜不报错，鞋袜回到身上、精液回到鞋上", wear_back_error == "" and locker_npc.cloth.cloth_wear[10] == [sock_id] and locker_npc.cloth.cloth_wear[11] == [shoe_id]
      and locker_npc.dirty.cloth_semen[11][1] == SHOE_SEMEN, (wear_back_error, locker_npc.cloth.cloth_wear[10], locker_npc.cloth.cloth_wear[11], locker_npc.dirty.cloth_semen[11][1]))
remove_character(LOCKER_NPC_ID)

section("穿着与衣柜两张服装精液表互不共用：往穿着的衣服上射精不会同时改衣柜的表")
from Script.Core import old_chara_to_new  # noqa: E402


def shared_part_list(dirty_data: game_type.DIRTY) -> list:
    """
    找出穿着表与衣柜表共用同一个列表对象的服装部位
    Keyword arguments:
    dirty_data -- 污浊数据
    Return arguments:
    list -- 共用列表的服装部位id
    """
    return [now_type for now_type in dirty_data.cloth_semen
            if now_type in dirty_data.cloth_locker_semen and dirty_data.cloth_semen[now_type] is dirty_data.cloth_locker_semen[now_type]]


zero_dirty = attr_calculation.get_zero_dirty()
check("新建的空污浊数据：两张表各部位各有各的列表", zero_dirty.cloth_semen is not zero_dirty.cloth_locker_semen and shared_part_list(zero_dirty) == [], shared_part_list(zero_dirty))
SHARE_NPC_ID = 9409
share_npc = make_character(SHARE_NPC_ID, "精液表测试干员")
upper_id = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 5 and now_tem.tag != 6)
# 两张表都缺某个部位时（旧存档、表被清空过的角色），转移衣服的结算会给两边各补一项
for move_effect in (default_cloth.handle_wear_to_shower_locker, default_cloth.handle_wear_to_dormitory_locker):
    share_npc.cloth = attr_calculation.get_cloth_zero()
    share_npc.cloth.cloth_locker_in_dormitory = attr_calculation.get_cloth_locker_in_dormitory_zero()
    share_npc.cloth.cloth_locker_in_shower = attr_calculation.get_shower_cloth_locker_zero()
    share_npc.cloth.cloth_wear[5] = [upper_id]
    share_npc.dirty.cloth_semen = {}
    share_npc.dirty.cloth_locker_semen = {}
    move_effect(SHARE_NPC_ID, 5, game_type.CharacterStatusChange(), cache.game_time)
    check("两张表都缺部位时把衣服转移到衣柜（%s）：补出来的两边不共用列表" % move_effect.__name__,
          sorted(share_npc.dirty.cloth_semen) == sorted(game_config.config_clothing_type) and shared_part_list(share_npc.dirty) == [], shared_part_list(share_npc.dirty))
# 读档：存档里两张表可能已经是同一个 dict（旧版本「检查衣柜」造成），或各部位共用列表
saved_pl_dirty = pl.dirty
pl.dirty = attr_calculation.get_zero_dirty()
pl.dirty.cloth_locker_semen = pl.dirty.cloth_semen
old_chara_to_new.update_chara_cloth(pl, None)
pl.dirty.cloth_semen[5][1] = 25
check("读档后：原本是同一个 dict 的两张表被拆开，往穿着的上衣上射精不改衣柜的表",
      pl.dirty.cloth_semen is not pl.dirty.cloth_locker_semen and shared_part_list(pl.dirty) == [] and pl.dirty.cloth_locker_semen[5][1] == 0,
      (pl.dirty.cloth_semen is pl.dirty.cloth_locker_semen, shared_part_list(pl.dirty)))
# 读档：很旧的存档里两张表是按部位顺序排的列表（长度与服装部位数相同，不会被当成长度不符而重置）
pl.dirty = attr_calculation.get_zero_dirty()
old_format_list = [[game_config.config_clothing_type[now_type].name, now_type * 10, 0, now_type * 10] for now_type in sorted(game_config.config_clothing_type)]
pl.dirty.cloth_semen = old_format_list
pl.dirty.cloth_locker_semen = old_format_list
old_format_error = ""
try:
    old_chara_to_new.update_chara_cloth(pl, None)
except Exception as error:  # noqa: BLE001  要把异常类型写进断言的附带信息
    old_format_error = repr(error)
check("读档后：列表形式的两张旧表都换成以服装部位为键的 dict，数值不变、互不共用（此前读这种存档会直接报错）",
      old_format_error == "" and isinstance(pl.dirty.cloth_semen, dict) and isinstance(pl.dirty.cloth_locker_semen, dict)
      and sorted(pl.dirty.cloth_semen) == sorted(pl.dirty.cloth_locker_semen) == sorted(game_config.config_clothing_type)
      and all(pl.dirty.cloth_semen[now_type][1] == pl.dirty.cloth_locker_semen[now_type][1] == now_type * 10 for now_type in game_config.config_clothing_type)
      and shared_part_list(pl.dirty) == [],
      (old_format_error, type(pl.dirty.cloth_semen).__name__, type(pl.dirty.cloth_locker_semen).__name__))
pl.dirty = saved_pl_dirty
remove_character(SHARE_NPC_ID)

# ==== 8. 生产事件的接生人选 ====
section("生产事件：没有凯尔希也没有医疗干员时照常选出接生的人，且不会选到产妇本人")
MOTHER_ID, HELPER_ID, MEDIC_ID = 9406, 9407, 9408
saved_npc_id_got = set(cache.npc_id_got)
cache.npc_id_got.clear()
mother = make_character(MOTHER_ID, "产妇测试干员")
check("岛上只有产妇一名干员时不报错、也不让她给自己接生（返回 0，事件文本里写成医疗部的产科干员）", born_event_panel.get_born_doctor_id(MOTHER_ID) == 0,
      born_event_panel.get_born_doctor_id(MOTHER_ID))
helper = make_character(HELPER_ID, "普通测试干员")
random.seed(20261118)
doctor_pick_list = {born_event_panel.get_born_doctor_id(MOTHER_ID) for _sample in range(40)}
check("没有凯尔希也没有医疗干员、但有别的干员时：由别的干员接生", doctor_pick_list == {HELPER_ID}, doctor_pick_list)
medic = make_character(MEDIC_ID, "医疗测试干员")
medic.profession = 3
mother.profession = 3
mother.name = _("凯尔希")
doctor_pick_list = {born_event_panel.get_born_doctor_id(MOTHER_ID) for _sample in range(40)}
check("产妇是凯尔希时由别的医疗干员接生（她自己虽是医疗干员也不会被选中）", doctor_pick_list == {MEDIC_ID}, doctor_pick_list)
mother.name = "产妇测试干员"
mother.profession = 0
helper.name = _("凯尔希")
check("凯尔希在岛上且不是产妇时由凯尔希接生", born_event_panel.get_born_doctor_id(MOTHER_ID) == HELPER_ID)
for now_cid in (MOTHER_ID, HELPER_ID, MEDIC_ID):
    remove_character(now_cid)
cache.npc_id_got.clear()
cache.npc_id_got.update(saved_npc_id_got)

# ==== 8.1 能力面板：被监禁干员的刻印降级 ====
section("能力面板：被监禁的干员宝珠够用时，刻印照常判为可降级")
from Script.UI.Panel import ability_up_panel, new_round, see_character_info_panel  # noqa: E402

MARK_NPC_ID = 9411
mark_npc = make_character(MARK_NPC_ID, "刻印测试干员")
mark_ability_id = sorted(game_config.config_mark_down_data_by_ability)[0]
""" 一个可以用宝珠降级的刻印 """
mark_down_data = game_config.config_mark_down_data[game_config.config_mark_down_data_by_ability[mark_ability_id][1]]
mark_npc.ability[mark_ability_id] = 1
for now_juel_id in mark_npc.juel:
    mark_npc.juel[now_juel_id] = mark_down_data.need_juel_all_value
mark_panel = object.__new__(ability_up_panel.Characterabi_show_Text)
mark_panel.character_id = MARK_NPC_ID
mark_panel.character_data = mark_npc
# debug 模式下判定出错时一律当作可降级，会把问题盖住；这里固定按非 debug 判
saved_debug_mode = cache.debug_mode
cache.debug_mode = False
mark_npc.sp_flag.imprisonment = 0
check("对照：没被监禁、宝珠够用时可以降级", mark_panel.check_ability_change_possible(mark_ability_id)[1] is True)
mark_npc.sp_flag.imprisonment = 1
mark_can_down = mark_panel.check_ability_change_possible(mark_ability_id)[1]
check("被监禁（降级需求按关押区等级打折）、宝珠够用时同样可以降级", mark_can_down is True, mark_can_down)
remove_character(MARK_NPC_ID)

# ==== 8.2 技能书读完的奖励 ====
section("读完技能书的经验奖励按难度：难度 1 加 10、难度 2 加 20、难度 3 加 40")
from Script.Settle import default as settle_default  # noqa: E402


def read_exp_delta(book_id: int, progress_before: int) -> int:
    """
    让博士读一次书，返回这次阅读让对应技能经验增加了多少
    Keyword arguments:
    book_id -- 书籍id
    progress_before -- 读之前的阅读进度（99 时这一次必定读完，0 时读不完）
    Return arguments:
    int -- 对应技能经验的增量
    """
    exp_id = game_config.config_book_type[game_config.config_book[book_id].type].exp_id
    pl.target_character_id = 0
    pl.behavior.book_id = book_id
    pl.entertainment.read_book_progress[book_id] = progress_before
    exp_before = pl.experience.get(exp_id, 0)
    settle_default.handle_read_add_adjust(0, 30, game_type.CharacterStatusChange(), cache.game_time)
    return pl.experience.get(exp_id, 0) - exp_before


finish_bonus = {}
""" 难度 -> 读完时比没读完多得的经验 """
# 桩：读完一本书会走成就结算（读最小世界里没有的仓库数据，且可能写文件），与本段无关
_real_achievement_flow = settle_default.achievement_panel.achievement_flow
settle_default.achievement_panel.achievement_flow = lambda *args, **kwargs: None
try:
    for now_difficulty in (1, 2, 3):
        skill_book_id = next(now_cid for now_cid, now_book in sorted(game_config.config_book.items())
                             if now_book.difficulty == now_difficulty and game_config.config_book_type[now_book.type].exp_id != 0)
        finish_bonus[now_difficulty] = read_exp_delta(skill_book_id, 99) - read_exp_delta(skill_book_id, 0)
finally:
    settle_default.achievement_panel.achievement_flow = _real_achievement_flow
check("读完技能书的额外经验：难度 1 / 2 / 3 分别是 10 / 20 / 40", finish_bonus == {1: 10, 2: 20, 3: 40}, finish_bonus)
cache.debug_mode = saved_debug_mode

# ==== 8.3 按性别过滤的经验与宝珠 ====
section("女性角色的经验与宝珠列表不列男性专属项")
MALE_ONLY_EXP_LIST = [3, 13, 21, 73]
""" 男性专属经验：阴茎经验、阴茎绝顶经验、射精经验、无意识阴茎经验 """
FEMALE_NPC_ID = 9412
female_npc = make_character(FEMALE_NPC_ID, "性别过滤测试干员")
female_npc.sex = 1
for now_exp_id in MALE_ONLY_EXP_LIST:
    female_npc.experience[now_exp_id] = 5
female_npc.experience[0] = 5


def panel_text(panel_object) -> str:
    """
    画出一个面板对象，返回它画出的全部文字
    Keyword arguments:
    panel_object -- 带 draw() 的面板对象
    Return arguments:
    str -- 画出的文字拼成的一串
    """
    drawn_text.clear()
    panel_object.draw()
    return "".join(str(text) for text in drawn_text)


male_exp_label_list = [" %s:" % game_config.config_experience[now_exp_id].name for now_exp_id in MALE_ONLY_EXP_LIST]
info_exp_text = panel_text(see_character_info_panel.CharacterExperienceText(FEMALE_NPC_ID, 100, 5))
check("fixture：经验列表照常列出她有的普通经验", " %s:" % game_config.config_experience[0].name in info_exp_text, info_exp_text[:120])
check("人物信息的经验列表：女性角色不列男性专属经验", not [label for label in male_exp_label_list if label in info_exp_text], [label for label in male_exp_label_list if label in info_exp_text])
round_exp_text = panel_text(new_round.CharacterExperienceText(FEMALE_NPC_ID, 100, 5, 50))
check("新周目继承面板的经验列表：女性角色不列男性专属经验", " %s:" % game_config.config_experience[0].name in round_exp_text
      and not [label for label in male_exp_label_list if label in round_exp_text], [label for label in male_exp_label_list if label in round_exp_text])
info_juel_text = panel_text(see_character_info_panel.CharacterJuelText(FEMALE_NPC_ID, 100, 5))
check("人物信息的宝珠列表：女性角色不列阴茎快感珠", " %s:" % game_config.config_juel[3].name not in info_juel_text and " %s:" % game_config.config_juel[2].name in info_juel_text,
      info_juel_text[:160])
remove_character(FEMALE_NPC_ID)

# ==== 8.4 指令类型过滤设置 ====
section("交互对象是婴儿（或临盆、产后）时隐藏技艺 / 猥亵 / 性爱指令，但不改写玩家的指令类型过滤设置")
from Script.System.Instruct_System import see_instruct_panel  # noqa: E402

FILTER_BABY_ID, FILTER_ADULT_ID = 9413, 9414
filter_baby = make_character(FILTER_BABY_ID, "过滤测试婴儿", daughter=True, stage=101, position=pl.position)
filter_adult = make_character(FILTER_ADULT_ID, "过滤测试干员", position=pl.position)
saved_instruct_filter = dict(cache.instruct_type_filter)
cache.instruct_type_filter.clear()
cache.instruct_type_filter.update({now_type: True for now_type in range(7)})
pl.target_character_id = FILTER_BABY_ID
check("交互对象是婴儿时：技艺、猥亵、性爱三类指令不显示，日常类照常显示",
      [handle_premise.instruct_type_shown(now_type) for now_type in (constant.InstructType.DAILY, constant.InstructType.ARTS, constant.InstructType.OBSCENITY, constant.InstructType.SEX)]
      == [True, False, False, False])
check("对应的三个「指令面板可见」前提此时不成立", (handle_premise.handle_arts_panel_show(0), handle_premise.handle_obscenity_panel_show(0), handle_premise.handle_sex_panel_show(0)) == (0, 0, 0),
      (handle_premise.handle_arts_panel_show(0), handle_premise.handle_obscenity_panel_show(0), handle_premise.handle_sex_panel_show(0)))
instruct_panel_error = ""
# 画指令面板会把每条指令的前提都算一遍，其中有的要读博士的道具数量；最小世界里博士的道具表是空的，先按 0 个补齐
saved_pl_item = dict(pl.item)
for now_item_id in game_config.config_item:
    pl.item.setdefault(now_item_id, 0)
try:
    drawn_text.clear()
    see_instruct_panel.SeeInstructPanel(100).draw()
except Exception as error:  # noqa: BLE001  面板在最小世界里画不出来时要变成失败的断言
    instruct_panel_error = repr(error)
pl.item.clear()
pl.item.update(saved_pl_item)
check("对着婴儿画一次 Tk 指令面板后，玩家的技艺、猥亵类型过滤设置仍是开着的（此前会被面板直接写成关闭，换回别人也回不来）",
      instruct_panel_error == "" and cache.instruct_type_filter[constant.InstructType.ARTS] is True and cache.instruct_type_filter[constant.InstructType.OBSCENITY] is True,
      (instruct_panel_error, dict(cache.instruct_type_filter)))
pl.target_character_id = FILTER_ADULT_ID
check("换回成年的交互对象：三类指令恢复按玩家的设置显示", [handle_premise.instruct_type_shown(now_type) for now_type in (constant.InstructType.ARTS, constant.InstructType.OBSCENITY)] == [True, True]
      and handle_premise.handle_obscenity_panel_show(0) == 1)
cache.instruct_type_filter[constant.InstructType.OBSCENITY] = False
check("玩家自己关掉的类型照常不显示", handle_premise.instruct_type_shown(constant.InstructType.OBSCENITY) is False and handle_premise.handle_obscenity_panel_show(0) == 0)
cache.instruct_type_filter.clear()
cache.instruct_type_filter.update(saved_instruct_filter)
pl.target_character_id = 0
remove_character(FILTER_BABY_ID)
remove_character(FILTER_ADULT_ID)

# ==== 8.5 指令的 H 模式显示类型与疲劳类型 ====
section("指令配置的「H模式显示类型」「疲劳类型」两列对每条指令都生效（前提条件集为空的也一样）")
from Script.Core import constant_promise  # noqa: E402
from Script.System.Instruct_System import handle_instruct as instruct_module  # noqa: E402,F401  导入即注册全部指令

P = constant_promise.Premise
H_MODE_PREMISE = {1: {P.NOT_H, P.NOT_SHOW_NON_H_IN_HIDDEN_SEX}, 2: {P.TARGET_IS_H}}
""" H模式显示类型 -> 应带的前提（1 非H显示 / 2 H显示） """
TIRED_PREMISE = {1: {P.TIRED_LE_84, P.HP_G_1, P.DRUNK_LEVEL_NOT_3}, 2: {P.TIRED_LE_74, P.HP_G_1, P.DRUNK_LEVEL_NOT_3}}
""" 疲劳类型 -> 应带的前提（1 轻度疲劳 / 2 重度疲劳） """
bad = []
empty_premise_checked = 0
for now_instruct_id, now_premise_set in constant.instruct_premise_data.items():
    now_config_cid = game_config.config_instruct_by_id.get(now_instruct_id)
    if now_config_cid is None:
        continue
    now_config = game_config.config_instruct[now_config_cid]
    need_set = H_MODE_PREMISE.get(getattr(now_config, "h_mode_show_type", None), set()) | TIRED_PREMISE.get(getattr(now_config, "tired_type", None), set())
    if need_set and not getattr(now_config, "premise_set", None):
        empty_premise_checked += 1
    if not need_set <= set(now_premise_set):
        bad.append((now_instruct_id, sorted(need_set - set(now_premise_set))))
check("fixture：有前提条件集为空、但填了这两列的指令（读写存档、系统设置等）", empty_premise_checked > 0, empty_premise_checked)
check("每条指令都带上了这两列对应的前提（否则 H 中仍会列出读写存档、系统设置等标了「非H显示」的指令）", not bad, bad[:10])

# ==== 8.5.1 导入游戏模块不留下不会结束的线程 ====
section("游戏模块导入完后没有留下不会结束的线程")
import threading  # noqa: E402

alive_thread_list = [thread.name for thread in threading.enumerate() if thread is not threading.main_thread() and not thread.daemon and thread.is_alive()]
check("导入指令处理等模块后，除主线程外没有非守护线程在跑（否则 Web 模式要按两次 Ctrl+C 才退出、脚本跑完进程也不结束）", alive_thread_list == [], alive_thread_list)

# ==== 8.6 重新扫描模组 ====
section("重新扫描模组文件夹后，各模组保留启动时的加载状态与错误信息")
import inspect  # noqa: E402
import json  # noqa: E402
import tempfile  # noqa: E402

from Script.Core import mod_manager  # noqa: E402

with tempfile.TemporaryDirectory() as temp_mod_dir:
    for now_mod_id in ("test_mod_ok", "test_mod_bad"):
        os.makedirs(os.path.join(temp_mod_dir, now_mod_id))
        with open(os.path.join(temp_mod_dir, now_mod_id, "mod_info.json"), "w", encoding="utf-8") as mod_info_file:
            json.dump({"mod_id": now_mod_id, "name": now_mod_id}, mod_info_file)
    # ModManager 是单例：这里另建一个不走单例的实例，指向临时文件夹，不碰游戏真正的模组管理器
    temp_manager = object.__new__(mod_manager.ModManager)
    temp_manager._initialized = True
    temp_manager.mod_folder = temp_mod_dir
    temp_manager.mods = {}
    temp_manager.enabled_mods = []
    temp_manager.load_order = []
    temp_manager.get_mod_folder_path = lambda: temp_mod_dir
    temp_manager.scan_mods()
    check("fixture：扫描到两个模组，初始都是未加载", sorted(temp_manager.mods) == ["test_mod_bad", "test_mod_ok"] and not any(now_mod.loaded for now_mod in temp_manager.mods.values()))
    # 模拟启动时的加载结果：一个加载成功，一个加载失败并记下了错误信息
    temp_manager.mods["test_mod_ok"].loaded = True
    temp_manager.mods["test_mod_bad"].error_message = "脚本加载失败"
    temp_manager.scan_mods()
    check("再扫描一次（打开或刷新模组面板）后：加载成功的仍显示已加载，加载失败的仍带着错误信息",
          temp_manager.mods["test_mod_ok"].loaded is True and temp_manager.mods["test_mod_bad"].error_message == "脚本加载失败",
          (temp_manager.mods["test_mod_ok"].loaded, temp_manager.mods["test_mod_bad"].error_message))

# ==== 8.7 综合数值前提与结算的解析 ====
section("综合数值前提 / 结算：结算记录对象必须由调用方传入，主体写错的数据不报错")
change_data_default = inspect.signature(settle_behavior.handle_comprehensive_value_effect).parameters["change_data"].default
check("综合数值结算的 change_data 没有默认值（默认值是定义函数时建好的同一个对象，各次调用会共用）", change_data_default is inspect.Parameter.empty, change_data_default)
bad_subject_result = []
for now_call in (lambda: handle_premise.handle_comprehensive_value_premise(0, ["A9", "F", "G", "0"]),
                 lambda: settle_behavior.handle_comprehensive_value_effect(0, ["A9", "F", "G", "1"], game_type.CharacterStatusChange())):
    try:
        bad_subject_result.append(now_call())
    except Exception as error:  # noqa: BLE001  要把异常类型写进断言的附带信息
        bad_subject_result.append(repr(error))
check("主体段写错（既不是 A1 / A2 也不是 A3|编号）的综合数值前提按不成立处理、结算按未结算处理，都不抛异常", bad_subject_result == [0, 0], bad_subject_result)
favor_before = pl.favorability.get(0, 0)
check("对照：格式正确的综合数值前提与结算照常工作", handle_premise.handle_comprehensive_value_premise(0, ["A1", "A|0", "GE", "0"]) == 1
      and bool(settle_behavior.handle_comprehensive_value_effect(0, ["A1", "A|0", "G", "1"], game_type.CharacterStatusChange())) and pl.ability[0] >= 1,
      (handle_premise.handle_comprehensive_value_premise(0, ["A1", "A|0", "GE", "0"]), pl.ability[0]))
pl.ability[0] = 0
del favor_before

# ==== 8.8 角色扮演的口上编号 ====
section("女仆惩罚调教（111）与女仆咖啡厅里菜单（112）的催眠地文各归各的编号")
ROLEPLAY_TALK_PATH = os.path.join(ROOT, "data", "talk", "arts", "roleplay.csv")
roleplay_name = {now_cid: game_config.config_roleplay[now_cid].name for now_cid in (111, 112)}
bad = []
with open(ROLEPLAY_TALK_PATH, encoding="utf-8") as talk_file:
    for row in csv.reader(talk_file):
        if len(row) < 5:
            continue
        for now_cid, wrong_word in ((111, "咖啡厅"), (112, "惩罚")):
            if "Roleplay|%d_" % now_cid in row[3] and wrong_word in row[4]:
                bad.append((row[0], now_cid))
check("fixture：游戏表里 111 是惩罚调教、112 是咖啡厅", "惩罚" in roleplay_name[111] and "咖啡厅" in roleplay_name[112], roleplay_name)
check("前提写 111 的地文不讲咖啡厅、写 112 的不讲惩罚（此前两者写反，选一个播的是另一个的地文）", not bad, bad)

# ==== 9. 同名图片的取舍 ====
section("同名图片：按固定规则取一个文件，并列出重名")
import tempfile  # noqa: E402

from Script.Core import image_path_index  # noqa: E402


def touch_image(root: str, *part_list) -> str:
    """
    在临时目录里建一个空文件（取舍只看路径，不读内容）
    Keyword arguments:
    root -- 临时的图片根目录
    part_list -- 相对路径的各段
    Return arguments:
    str -- 建好的文件路径
    """
    file_path = os.path.join(root, *part_list)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    open(file_path, "wb").close()
    return file_path


with tempfile.TemporaryDirectory() as temp_dir:
    image_root = os.path.join(temp_dir, "image")
    # 两个分类文件夹下同层级的重名：干员在特殊NPC之前（主支 image/ 里现有的 10 组重名都是这种）
    operator_half = touch_image(image_root, "立绘", "干员", "电弧", "电弧_半身.png")
    npc_half = touch_image(image_root, "立绘", "特殊NPC", "电弧", "电弧_半身.png")
    # 角色主文件夹与更深一层的子文件夹重名：主文件夹里的优先
    main_full = touch_image(image_root, "立绘", "干员", "莱伊", "莱伊_全身.png")
    draft_full = touch_image(image_root, "立绘", "干员", "莱伊", "构思", "莱伊_全身.png")
    # 不重名的图片与非图片文件
    single_half = touch_image(image_root, "立绘", "干员", "莱伊", "莱伊_半身.png")
    touch_image(image_root, "立绘", "干员", "莱伊", "莱伊_body.json")
    image_index, image_duplicates = image_path_index.build_image_path_index(image_root)
check("每个图片名只取一个文件：同层级重名取干员文件夹的，主文件夹与子文件夹重名取主文件夹的",
      image_index == {"电弧_半身": operator_half, "莱伊_全身": main_full, "莱伊_半身": single_half}, image_index)
# ==== 8.9 按编号清除命令 ====
section("按编号清除命令：逐个清除给出的编号，其余命令保留")
from Script.Core import io_init, py_cmd  # noqa: E402

saved_cmd_map = dict(flow_handle.cmd_map)
flow_handle.cmd_map.clear()
for cmd_number in (901, 902, 903):
    flow_handle.bind_cmd(cmd_number, flow_handle.null_func)
cleared_number_list = []
clear_error = None
with mock.patch.object(io_init, "io_clear_cmd", lambda *number_list: cleared_number_list.append(number_list)):
    try:
        py_cmd.clr_cmd(901, 902, clr_default_flow=False)
    except Exception as error:  # noqa: BLE001  旧代码把整个元组当成一个编号去删，会报 KeyError
        clear_error = repr(error)
    left_after_some = sorted(flow_handle.cmd_map)
    py_cmd.clr_cmd(clr_default_flow=False)
    left_after_all = sorted(flow_handle.cmd_map)
check("清除 901、902 两个命令：命令表里只剩 903，前端收到的是逐个编号", clear_error is None and left_after_some == [903] and cleared_number_list[:2] == [(901,), (902,)],
      (clear_error, left_after_some, cleared_number_list))
check("不给编号时清除全部命令", left_after_all == [] and cleared_number_list[-1] == (), (left_after_all, cleared_number_list))
flow_handle.cmd_map.clear()
flow_handle.cmd_map.update(saved_cmd_map)

# ==== 8.10 字体配置里的加粗 / 下划线 / 斜体 ====
section("字体配置里的加粗 / 下划线 / 斜体送到 Tk 前端时是布尔值，警告样式不带下划线")
style_flag_data = {}
warning_style = game_config.config_font[game_config.config_font_data["warning"]]
# 表里留空的格子载入后没有对应的属性（init_style 会按默认样式补 0），所以用 getattr 取
warning_flag = tuple(getattr(warning_style, flag_name, 0) for flag_name in ("bold", "underline", "italic"))
check("警告样式不带下划线（字体修饰生效后保持原来的外观，维护者的决定）", not any(warning_flag), warning_flag)
saved_warning_dict = dict(warning_style.__dict__)
warning_style.bold, warning_style.underline, warning_style.italic = 1, 0, 1  # 临时给一个样式开上加粗与斜体，看它们会不会原样到达前端
try:
    with mock.patch.object(io_init, "frame_style_def", lambda style_name, _fg, _bg, _font, _size, bold, underline, italic: style_flag_data.__setitem__(style_name, (bold, underline, italic))):
        io_init.init_style()
finally:
    warning_style.__dict__.clear()
    warning_style.__dict__.update(saved_warning_dict)
not_bool = [name for name, flag_tuple in style_flag_data.items() if not all(type(flag) is bool for flag in flag_tuple)]
check("每个样式送给前端的三个开关都是布尔值（旧代码送的是整数或 \"0\"/\"1\" 字符串，前端只认字符串 \"1\"，配置里设的修饰从不生效）", len(style_flag_data) > 0 and not not_bool, not_bool[:8])
check("配置里开了加粗与斜体的样式、三个通用修饰符、组合样式，开关都如实送到",
      (style_flag_data.get("warning"), style_flag_data.get("standard"), style_flag_data.get("bold"), style_flag_data.get("underline"), style_flag_data.get("italic"), style_flag_data.get("standard_bold_italic"))
      == ((True, False, True), (False, False, False), (True, False, False), (False, True, False), (False, False, True), (True, False, True)),
      (style_flag_data.get("warning"), style_flag_data.get("standard"), style_flag_data.get("bold"), style_flag_data.get("underline"), style_flag_data.get("italic"), style_flag_data.get("standard_bold_italic")))

check("重名的图片被列出来，第一个是取中的文件", image_duplicates == {"电弧_半身": [operator_half, npc_half], "莱伊_全身": [main_full, draft_full]}, image_duplicates)

finish()
