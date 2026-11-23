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

# ==== 8.11 解手的结算 ====
section("解手后清空记下的目标厕所，不会被派回自己的宿舍")
PEE_NPC_ID = 9420
""" 解手的干员 fixture """
CLEAR_TOILET_EFFECT = constant_effect.BehaviorEffect.CLEAR_TARGET_TOILET_PATH
GO_DORMITORY_EFFECT = constant_effect.BehaviorEffect.MOVE_TO_OWN_DORMITORY
pee_effect_list = list(game_config.config_behavior_effect_data.get(constant.Behavior.PEE, []))
check("解手行为的结算里有「清空记下的目标厕所」（1712），没有「前往自己的宿舍」（1721）——两个编号只差数字换位，表里曾把前者写成后者",
      CLEAR_TOILET_EFFECT in pee_effect_list and GO_DORMITORY_EFFECT not in pee_effect_list, pee_effect_list)
toilet_path = map_handle.get_map_system_path_for_str(constant.place_data["Toilet_Female"][0])
pee_npc = make_character(PEE_NPC_ID, "解手测试干员", position=toilet_path)
check("fixture：她的宿舍不是这间洗手间（被派回宿舍的话会动身）", pee_npc.dormitory != scene_str(toilet_path), pee_npc.dormitory)
pee_npc.target_character_id = PEE_NPC_ID
pee_npc.urinate_point = 240
pee_npc.sp_flag.pee = True
pee_npc.action_info.find_another_toilet = list(toilet_path)
pee_npc.behavior.behavior_id = constant.Behavior.PEE
pee_npc.behavior.duration = 5
pee_npc.behavior.start_time = cache.game_time
pee_npc.state = constant.CharacterStatus.STATUS_PEE
pee_error = ""
try:
    settle_behavior.handle_settle_behavior(PEE_NPC_ID, cache.game_time + datetime.timedelta(minutes=5))
except Exception as error:  # noqa: BLE001  报错作为断言失败的附加信息
    pee_error = repr(error)
check("解手结算不报错，尿意清零、解手需求撤掉", pee_error == "" and pee_npc.urinate_point == 0 and not pee_npc.sp_flag.pee, (pee_error, pee_npc.urinate_point, pee_npc.sp_flag.pee))
check("解手后清空了记下的目标厕所（否则下次解手会直奔上次记下的那一间，而不是就近找）", pee_npc.action_info.find_another_toilet == [], pee_npc.action_info.find_another_toilet)
check("解手后没有被设上移动终点、也没有动身（否则干员每次上完厕所都要走回宿舍，走到了才继续工作或上课）",
      pee_npc.behavior.move_final_target == [] and pee_npc.behavior.behavior_id != constant.Behavior.MOVE, (pee_npc.behavior.move_final_target, pee_npc.behavior.behavior_id))
remove_character(PEE_NPC_ID)

# ==== 8.12 H 中吵醒同屋睡觉的人 ====
section("H 中吵醒了同屋另一个睡觉的人：醒来的人按目击 H 处理，不再一律把博士推出房间（#328）")
from Script.Design import character_behavior, handle_npc_ai_in_h, instuct_judege  # noqa: E402
from Script.Settle import default as settle_default  # noqa: E402
from Script.System.Instruct_System import handle_instruct  # noqa: E402

WAKE_H_TARGET_ID = 9430
""" 被博士睡奸的干员 fixture """
WAKE_SLEEPER_ID = 9431
""" 同屋睡觉、会被吵醒的干员 fixture """
DORM_ENTRANCE = ["宿舍", "1区", "0"]
""" 博士走进宿舍前所在的宿舍区入口，被推出房间时回到这里 """
DORM_CORRIDOR = ["宿舍", "1区", "外走廊"]
""" 宿舍房间相邻的外走廊，室友是从这里走进房间的 """


def settle_pl_behavior(minute: int):
    """
    update.game_update_flow 的替身：不进真实主循环，只结算一次博士当前的行为（主循环推进时间后对博士做的正是这一步；博士空闲时主循环不结算）
    Keyword arguments:
    minute -- 推进的分钟数（不使用）
    Return arguments:
    无
    """
    if pl.behavior.behavior_id != constant.Behavior.SHARE_BLANKLY:
        character_behavior.judge_character_status(0)


pl_settled_log = []
""" 吵醒过程中博士每次行为结算的 (行为id, 结算时博士是否仍在 H 中) """
real_handle_settle_behavior = settle_behavior.handle_settle_behavior


def record_settle_behavior(character_id: int, *args, **kwargs):
    """
    settle_behavior.handle_settle_behavior 的记录包装：记下博士每次结算的行为，再照常结算
    Keyword arguments:
    character_id -- 角色id
    其余参数原样转交
    Return arguments:
    原函数的返回值
    """
    if character_id == 0:
        pl_settled_log.append((pl.behavior.behavior_id, pl.sp_flag.is_h))
    return real_handle_settle_behavior(character_id, *args, **kwargs)


def run_wake_case(in_h: bool, choice: str = "", judge_pass: bool = True, sleeping_pill: bool = False, wake_id: int = WAKE_SLEEPER_ID, fall_level=None) -> tuple:
    """
    在宿舍里摆好一场睡奸（或博士只是待在屋里），让同屋睡觉的人被吵醒，按 choice 在目击 H 面板里选择应对
    Keyword arguments:
    in_h -- 博士是否正在睡奸
    choice -- 目击 H 面板里选的按钮（1 支开对方 / 5 尴尬地结束H）
    judge_pass -- 实行值判定是否一律通过（支开对方、睡奸对象醒来后的反应都看它）
    sleeping_pill -- 睡奸对象是否服用了安眠药（吵不醒）
    wake_id -- 被吵醒的人：默认同屋室友，传睡奸对象时走睡奸对象本人中途醒来的流程
    fall_level -- 睡奸对象醒来时按多少陷落等级裁决反应，None 为不干预
    Return arguments:
    tuple -- (睡奸对象, 被吵醒的室友, 吵醒前博士与睡奸对象是否都在 H 中, 面板运行时的异常)
    """
    h_target = make_character(WAKE_H_TARGET_ID, "睡奸对象")
    sleeper = make_character(WAKE_SLEEPER_ID, "同屋室友")
    sleeper.action_info.past_move_position_list = [list(DORM_CORRIDOR)]
    move_to(0, SCENE_DORM)
    # 博士体力、气力回满：前面的结算会消耗体力，体力见底时结算中途会转去力竭结束 H（并进入真实主循环）
    pl.hit_point = pl.hit_point_max
    pl.mana_point = pl.mana_point_max
    pl.action_info.past_move_position_list = [list(DORM_ENTRANCE), list(SCENE_DORM)]
    pl.target_character_id = WAKE_H_TARGET_ID
    for chara_data in (h_target, sleeper):
        chara_data.behavior.behavior_id = constant.Behavior.SLEEP
        chara_data.state = constant.CharacterStatus.STATUS_SLEEP
        chara_data.behavior.duration = 480
        chara_data.behavior.start_time = cache.game_time
        chara_data.sleep_point = 10  # 浅睡，吵醒判定只看随机数
        chara_data.tired_point = 100
    # 进入睡奸：先给对象挂上无意识标记，再照真实的「进入H」行为结算（双方变为 H 中、关门）
    if in_h:
        settle_default.handle_unconscious_flag_to_1(WAKE_H_TARGET_ID, 1, game_type.CharacterStatusChange(), cache.game_time)
        pl.behavior.behavior_id = constant.Behavior.H
        pl.state = constant.CharacterStatus.STATUS_H
        pl.behavior.duration = 5
        pl.behavior.start_time = cache.game_time
        settle_behavior.handle_settle_behavior(0, cache.game_time + datetime.timedelta(minutes=5))
    if sleeping_pill:
        h_target.h_state.body_item[9][1] = 1
    all_in_h = pl.sp_flag.is_h and h_target.sp_flag.is_h

    def wake():
        """
        博士的一次动作吵醒了 wake_id（randint 恒为 1：必定吵醒）
        Keyword arguments:
        无
        Return arguments:
        无
        """
        real_fall_level = attr_calculation.get_character_fall_level
        with mock.patch.object(handle_npc_ai_in_h, "random", mock.Mock(randint=lambda low, high: 1)), \
                mock.patch.object(instuct_judege, "calculation_instuct_judege", lambda *args, **kwargs: [1 if judge_pass else 0, 1, 1.0]), \
                mock.patch.object(attr_calculation, "get_character_fall_level", lambda *args, **kwargs: real_fall_level(*args, **kwargs) if fall_level is None else fall_level), \
                mock.patch.object(settle_behavior, "handle_settle_behavior", record_settle_behavior), \
                mock.patch.object(handle_instruct.update, "game_update_flow", settle_pl_behavior), \
                mock.patch.object(handle_instruct.achievement_panel, "achievement_flow", lambda *args, **kwargs: None):
            handle_npc_ai_in_h.judge_weak_up_in_sleep_h(0, wake_id)

    pl_settled_log.clear()
    panel_error = run_panel(wake, [choice] if choice else [])
    return h_target, sleeper, all_in_h, panel_error


def clean_wake_case():
    """
    撤掉本节的 fixture 角色，把博士与宿舍复原
    Keyword arguments:
    无
    Return arguments:
    无
    """
    for chara_id in (WAKE_H_TARGET_ID, WAKE_SLEEPER_ID):
        remove_character(chara_id)
    pl.sp_flag.is_h = False
    pl.target_character_id = 0
    pl.behavior = game_type.Behavior()
    pl.behavior.start_time = cache.game_time
    pl.action_info.past_move_position_list = []
    cache.scene_data[scene_str(SCENE_DORM)].close_flag = 0
    move_to(0, SCENE_DORM)


enable_clickable_buttons()

h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=False)
check("不在 H 中时照旧：被吵醒的室友直接把博士推回宿舍区入口，不弹目击 H 面板",
      panel_error is None and not ask_log and pl.position == DORM_ENTRANCE and sleeper.behavior.behavior_id == constant.Behavior.WAKE_UP_BY_NOISE,
      (repr(panel_error), len(ask_log), pl.position, sleeper.behavior.behavior_id))
clean_wake_case()

h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, choice="1")
check("fixture：睡奸开始后博士与睡奸对象都在 H 中", all_in_h)
find_text = _("\n{0}发现了{1}，要怎么做？\n").format(sleeper.name, _("你正在无意识奸{0}").format(h_target.name))
check("睡奸中吵醒室友：先提示谁被吵醒，再以她为发现者弹出目击 H 面板（修复前直接把博士推出房间，博士仍在 H 中、结束H类指令全都不出现）",
      panel_error is None and len(ask_log) == 1 and _("\n{0}被{1}的动静吵醒了\n").format(sleeper.name, pl.name) in drawn_text and find_text in drawn_text,
      (repr(panel_error), len(ask_log), drawn_text[:4]))
check("醒来的室友记为已目击本次 H，一小时内不会再产生睡觉需求", sleeper.sp_flag.see_pl_h and sleeper.action_info.sleep_disturbed_end_time > cache.game_time,
      (sleeper.sp_flag.see_pl_h, sleeper.action_info.sleep_disturbed_end_time))
check("成功支开室友后博士留在房间里，睡奸照常继续，睡奸对象仍在睡",
      pl.position == list(SCENE_DORM) and pl.sp_flag.is_h and h_target.sp_flag.is_h and h_target.behavior.behavior_id == constant.Behavior.SLEEP,
      (pl.position, pl.sp_flag.is_h, h_target.sp_flag.is_h, h_target.behavior.behavior_id))
check("被支开的室友走出自己的房间、去她来时的外走廊（修复前「前往自己的宿舍」对已在宿舍里的人不移动，口上说她离开了，她却留在屋里）",
      sleeper.behavior.behavior_id == constant.Behavior.MOVE and sleeper.behavior.move_final_target == DORM_CORRIDOR,
      (sleeper.behavior.behavior_id, sleeper.behavior.move_final_target))
clean_wake_case()

h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, choice="5")
check("选择结束 H：室友打断了这场 H，博士留在房间里、已不在 H 中",
      panel_error is None and sleeper.behavior.behavior_id == constant.Behavior.SEE_H_AND_INTERRUPT and pl.position == list(SCENE_DORM) and not pl.sp_flag.is_h,
      (repr(panel_error), sleeper.behavior.behavior_id, pl.position, pl.sp_flag.is_h))
check("睡奸对象也被这场骚动吵醒：提示她惊醒，睡眠结束，无意识与 H 标记都已清掉（修复前被改成原地等待、却仍挂着无意识标记）",
      _("\n因为{0}的动作，{1}从梦中惊醒过来\n").format(sleeper.name, h_target.name) in drawn_text
      and h_target.behavior.behavior_id != constant.Behavior.SLEEP and h_target.sp_flag.unconscious_h == 0 and not h_target.sp_flag.is_h,
      (h_target.behavior.behavior_id, h_target.sp_flag.unconscious_h, h_target.sp_flag.is_h))
clean_wake_case()

h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, choice="5", sleeping_pill=True)
check("服用安眠药的睡奸对象吵不醒：H 照常结束，她继续睡",
      panel_error is None and not pl.sp_flag.is_h and not h_target.sp_flag.is_h and h_target.behavior.behavior_id == constant.Behavior.SLEEP,
      (repr(panel_error), pl.sp_flag.is_h, h_target.sp_flag.is_h, h_target.behavior.behavior_id))
clean_wake_case()

h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, choice="5", fall_level=3)
check("结束 H 时睡奸对象已陷落、本可继续 H：博士的「被打断」赶在双方 H 数据重置前结算一次（修复前在重置之后才结算，本次 H 的绝顶奖励被清零）",
      panel_error is None and pl_settled_log == [(constant.Behavior.H_INTERRUPT, True)] and not pl.sp_flag.is_h and not h_target.sp_flag.is_h,
      (repr(panel_error), pl_settled_log, pl.sp_flag.is_h, h_target.sp_flag.is_h))
clean_wake_case()

# 睡奸对象本人被动静吵醒（原有流程）：不继续 H 时收尾的两段行为当场成对结算，之后推进时间不再结算一遍
h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, judge_pass=False, wake_id=WAKE_H_TARGET_ID)
check("睡奸对象醒来、H 失败：H 失败与「结束无意识H」各结算一次（修复前推进时间时又结算了一遍「结束无意识H」，口上与消耗重复）",
      panel_error is None and [behavior_id for behavior_id, is_h in pl_settled_log] == [constant.Behavior.DO_H_FAIL, constant.Behavior.NO_CONSCIOUS_H_END]
      and not pl.sp_flag.is_h and h_target.sp_flag.unconscious_h == 0,
      (repr(panel_error), pl_settled_log, pl.sp_flag.is_h, h_target.sp_flag.unconscious_h))
clean_wake_case()

h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, wake_id=WAKE_H_TARGET_ID, fall_level=-1)
check("睡奸对象醒来时愤怒：按 H 失败收尾，不再把博士刚结算过的指令对已醒的她再结算一遍",
      panel_error is None and [behavior_id for behavior_id, is_h in pl_settled_log] == [constant.Behavior.DO_H_FAIL, constant.Behavior.NO_CONSCIOUS_H_END]
      and h_target.sp_flag.angry_with_player,
      (repr(panel_error), pl_settled_log, h_target.sp_flag.angry_with_player))
clean_wake_case()

# 「等待五分钟」在场景里已没有 H 对象时会转去结束 H；此时交互对象是博士自己
pl.sp_flag.is_h = True
pl.sp_flag.is_follow = 0
pl.target_character_id = 0
with mock.patch.object(handle_instruct.update, "game_update_flow", lambda minute: None):
    handle_instruct.handle_h_end()
check("交互对象是博士自己时结束 H 不会把博士设为跟随状态", pl.sp_flag.is_follow == 0, pl.sp_flag.is_follow)
clean_wake_case()
pl.sp_flag.is_follow = 0

# 睡奸对象在 H 中仍被博士搬运（搬运与 H 互斥，只会出现在旧存档里）时中途醒来：醒来的反应由睡奸的恢复流程结算，搬运随之结束，不再叠加「被搬运时醒来」
from Script.Design import handle_npc_ai  # noqa: E402
from Script.Settle import realtime_settle  # noqa: E402

pl.action_info.carry_chara_id = WAKE_H_TARGET_ID
h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, judge_pass=False, wake_id=WAKE_H_TARGET_ID)
carry_after_recover = pl.action_info.carry_chara_id
handle_npc_ai.run_npc_pre_behavior_checks(WAKE_H_TARGET_ID, cache.game_time)
check("被搬运的睡奸对象醒来：睡奸的恢复流程结束搬运，之后的行动前检查不再让她执行「被搬运时醒来」（否则同一次醒来结算两遍反应）",
      panel_error is None and carry_after_recover == 0 and h_target.behavior.behavior_id != constant.Behavior.WAKE_UP_WHEN_CARRIED,
      (repr(panel_error), carry_after_recover, h_target.behavior.behavior_id))
clean_wake_case()
pl.action_info.carry_chara_id = 0

# ==== 8.13 被搬运的干员醒不来 ====
section("干员睡着后被博士搬运：醒来时清掉残留的睡眠无意识标记，恢复意识就执行「被搬运时醒来」、博士放下她")
CARRY_NPC_ID = 9440
""" 被博士搬运的干员 fixture """
disgust_state_id = 20
""" 反感状态id """


def make_carried_sleeper(stale_unconscious: bool = False) -> game_type.Character:
    """
    在宿舍里摆好一名正在睡觉、被博士搬运着的干员，博士在同一房间、交互对象是她
    Keyword arguments:
    stale_unconscious -- 是否带着睡奸结束后残留的睡眠无意识标记（unconscious_h=1，不在 H 中）
    Return arguments:
    game_type.Character -- 被搬运的干员
    """
    npc = make_character(CARRY_NPC_ID, "被搬运的干员")
    move_to(0, SCENE_DORM)
    pl.target_character_id = CARRY_NPC_ID
    pl.action_info.carry_chara_id = CARRY_NPC_ID
    npc.behavior.behavior_id = constant.Behavior.SLEEP
    npc.state = constant.CharacterStatus.STATUS_SLEEP
    npc.behavior.duration = 480
    npc.behavior.start_time = cache.game_time
    npc.target_character_id = CARRY_NPC_ID
    npc.sleep_point = 70  # 熟睡
    npc.tired_point = 0
    if stale_unconscious:
        npc.sp_flag.unconscious_h = 1
    return npc


def end_sleep(character_id: int):
    """
    让角色的睡眠按时长到点结束（主循环里睡够了、或睡饱提前醒走的都是这一步）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    character_behavior.judge_character_status_time_over(character_id, cache.game_time, end_now=2)


def clean_carry_case():
    """
    撤掉本节的 fixture 角色，复原博士与时停、醉酒等全局状态
    Keyword arguments:
    无
    Return arguments:
    无
    """
    remove_character(CARRY_NPC_ID)
    pl.action_info.carry_chara_id = 0
    pl.target_character_id = 0
    cache.time_stop_mode = False
    move_to(0, SCENE_DORM)


carry_behavior = game_config.config_behavior.get(constant.Behavior.WAKE_UP_WHEN_CARRIED)
carry_talk_count = sum(1 for talk_data in game_config.config_talk.values() if getattr(talk_data, "behavior_id", "") == constant.Behavior.WAKE_UP_WHEN_CARRIED)
check("「被搬运时醒来」已注册：NPC 行为、时长 10 分钟、挂着结算 1727，有通用口上",
      carry_behavior is not None and carry_behavior.duration == 10
      and constant_effect.BehaviorEffect.WAKE_UP_WHEN_CARRIED_ADJUST in game_config.config_behavior_effect_data.get(constant.Behavior.WAKE_UP_WHEN_CARRIED, [])
      and carry_talk_count >= 1,
      (carry_behavior, game_config.config_behavior_effect_data.get(constant.Behavior.WAKE_UP_WHEN_CARRIED), carry_talk_count))

# 残留标记：睡奸结束而对方仍在睡时，结束 H 只清 is_h；她之后睡醒，这个标记必须随之清掉
npc = make_carried_sleeper(stale_unconscious=True)
pl.action_info.carry_chara_id = 0
end_sleep(CARRY_NPC_ID)
check("不在 H 中时睡醒：残留的睡眠无意识标记被清掉，不再显示睡眠、异常位 6 恢复正常（修复前一直留着，博士在场时她被当作在睡、原地发呆醒不来）",
      npc.sp_flag.unconscious_h == 0 and not handle_premise.handle_unconscious_flag_1(CARRY_NPC_ID) and handle_premise.handle_normal_6(CARRY_NPC_ID),
      (npc.sp_flag.unconscious_h, handle_premise.handle_normal_6(CARRY_NPC_ID)))
clean_carry_case()
npc = make_carried_sleeper(stale_unconscious=True)
npc.sp_flag.is_h = True
end_sleep(CARRY_NPC_ID)
check("H 中睡醒时不动这个标记（睡奸中的醒来由无意识H的恢复流程处理）", npc.sp_flag.unconscious_h == 1, npc.sp_flag.unconscious_h)
clean_carry_case()

# 仍在睡时照旧被带着走
npc = make_carried_sleeper()
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("仍在睡时照旧被搬运，行为不变", pl.action_info.carry_chara_id == CARRY_NPC_ID and npc.behavior.behavior_id == constant.Behavior.SLEEP,
      (pl.action_info.carry_chara_id, npc.behavior.behavior_id))
clean_carry_case()


def wake_carried(stale_unconscious: bool = False, setup=None) -> game_type.Character:
    """
    被搬运的干员按时睡醒，再跑一遍NPC行动前检查（AI 给她挑新行动之前的那一步）
    Keyword arguments:
    stale_unconscious -- 是否带着残留的睡眠无意识标记
    setup -- 睡醒前对她做的额外设置，参数为角色对象
    Return arguments:
    game_type.Character -- 被搬运的干员
    """
    now_npc = make_carried_sleeper(stale_unconscious)
    if setup is not None:
        setup(now_npc)
    end_sleep(CARRY_NPC_ID)
    drawn_text.clear()
    handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
    return now_npc


# 二段行为在同一次结算里就被结算并归零，所以记下触发了哪些，而不是事后去看标记
from Script.Design import second_behavior as second_behavior_module  # noqa: E402

second_behavior_calls = []
real_get_second_behavior = second_behavior_module.character_get_second_behavior


def record_get_second_behavior(character_id: int, second_behavior_id: str, *args, **kwargs):
    """
    second_behavior.character_get_second_behavior 的记录包装：记下被搬运者获得的二段行为，再照常处理
    Keyword arguments:
    character_id -- 角色id
    second_behavior_id -- 二段行为id
    其余参数原样转交
    Return arguments:
    原函数的返回值
    """
    if character_id == CARRY_NPC_ID:
        second_behavior_calls.append(second_behavior_id)
    return real_get_second_behavior(character_id, second_behavior_id, *args, **kwargs)


with mock.patch.object(second_behavior_module, "character_get_second_behavior", record_get_second_behavior):
    npc = wake_carried(stale_unconscious=True, setup=lambda now_npc: setattr(now_npc.dirty, "body_semen_in_unconscious", [2]))
check("被搬运的干员睡醒：原地执行「被搬运时醒来」10 分钟、交互对象是博士，博士放下她（修复前搬运一直不结束，醒来后每一步都被瞬移回博士身边）",
      npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED and npc.behavior.duration == 10 and npc.target_character_id == 0
      and pl.action_info.carry_chara_id == 0,
      (npc.behavior.behavior_id, npc.behavior.duration, npc.target_character_id, pl.action_info.carry_chara_id))
check("醒来时出口上，并结算无意识期间被射上的精液（二段行为）",
      any(npc.name in text and pl.name in text for text in drawn_text)
      and npc.dirty.body_semen_in_unconscious == [] and "in_unconscious_cum_on_body_2" in second_behavior_calls,
      (drawn_text[:3], npc.dirty.body_semen_in_unconscious, second_behavior_calls))
check("无陷落时醒来增加反感，不生气", npc.status_data[disgust_state_id] > 0 and not npc.sp_flag.angry_with_player,
      (npc.status_data[disgust_state_id], npc.sp_flag.angry_with_player))
clean_carry_case()

npc = wake_carried(setup=lambda now_npc: now_npc.talent.__setitem__(203, 1))
check("爱情系陷落 3 级时默许：不加反感、不生气，博士继续搬运她", npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED
      and npc.status_data[disgust_state_id] == 0 and not npc.sp_flag.angry_with_player
      and pl.action_info.carry_chara_id == CARRY_NPC_ID and npc.action_info.awake_when_carried,
      (npc.behavior.behavior_id, npc.status_data[disgust_state_id], pl.action_info.carry_chara_id, npc.action_info.awake_when_carried))
# 「被搬运时醒来」结束后仍被搬运：不再结算一遍，也不交给 AI，原地等待、时长跟博士本步一致
character_behavior.judge_character_status_time_over(CARRY_NPC_ID, cache.game_time, end_now=2)
pl.behavior.duration = 30
drawn_text.clear()
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("默许后继续被搬运：醒来的行为结束后不再结算一遍，行为锁为等待、时长跟博士本步一致（不交给 AI）",
      npc.behavior.behavior_id == constant.Behavior.WAIT and npc.behavior.duration == 30 and pl.action_info.carry_chara_id == CARRY_NPC_ID
      and not any(npc.name in text for text in drawn_text),
      (npc.behavior.behavior_id, npc.behavior.duration, pl.action_info.carry_chara_id, drawn_text[:2]))
# 博士放下她之后照常交给 AI
pl.target_character_id = CARRY_NPC_ID
settle_default.handle_target_not_be_carried(0, 1, game_type.CharacterStatusChange(), cache.game_time)
npc.behavior = game_type.Behavior()
npc.behavior.start_time = cache.game_time
check("博士放下她之后，行动前检查不再接管她", not handle_npc_ai_in_h.judge_carried_character_regain_consciousness(CARRY_NPC_ID, cache.game_time)
      and npc.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY, npc.behavior.behavior_id)
# 再次搬运时从头算（搬运的结算 1723 把标记归零）
settle_default.handle_target_be_carried(0, 1, game_type.CharacterStatusChange(), cache.game_time)
check("再次开始搬运时，「已在被搬运时醒来并默许」的标记归零", pl.action_info.carry_chara_id == CARRY_NPC_ID and not npc.action_info.awake_when_carried,
      (pl.action_info.carry_chara_id, npc.action_info.awake_when_carried))
clean_carry_case()
pl.behavior = game_type.Behavior()
pl.behavior.start_time = cache.game_time

npc = wake_carried(setup=lambda now_npc: setattr(now_npc.sp_flag, "imprisonment", 1))
check("被监禁时默许：不加反感、不生气，博士继续搬运她", npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED
      and npc.status_data[disgust_state_id] == 0 and not npc.sp_flag.angry_with_player and pl.action_info.carry_chara_id == CARRY_NPC_ID,
      (npc.behavior.behavior_id, npc.status_data[disgust_state_id], pl.action_info.carry_chara_id))
# 默许后又失去意识（如被灌到烂醉）：照旧被搬运，下次恢复意识时重新结算
npc.drunk_point = 90
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("默许后又失去意识：照旧被搬运，标记归零，下次恢复意识时重新结算",
      pl.action_info.carry_chara_id == CARRY_NPC_ID and not npc.action_info.awake_when_carried, (pl.action_info.carry_chara_id, npc.action_info.awake_when_carried))
clean_carry_case()

npc = wake_carried(setup=lambda now_npc: now_npc.talent.__setitem__(211, 1))
check("隶属系陷落时愤怒：怒气 +100、生博士的气，博士放下她", npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED
      and npc.angry_point >= 100 and npc.sp_flag.angry_with_player and pl.action_info.carry_chara_id == 0,
      (npc.behavior.behavior_id, npc.angry_point, npc.sp_flag.angry_with_player, pl.action_info.carry_chara_id))
clean_carry_case()

# 被博士的动静吵醒：不执行「睡觉中被吵醒」（那条会把博士推出房间），结算被吵醒的后果，醒来的反应交给行动前检查
npc = make_carried_sleeper()
npc.sleep_point = 10
pl.action_info.past_move_position_list = [list(DORM_ENTRANCE), list(SCENE_DORM)]
with mock.patch.object(handle_npc_ai_in_h, "random", mock.Mock(randint=lambda low, high: 1)):
    handle_npc_ai_in_h.judge_weak_up_in_sleep_h(0, CARRY_NPC_ID)
check("被搬运时被博士吵醒：不执行「睡觉中被吵醒」、博士没被推出房间，一小时内不会再产生睡觉需求",
      npc.behavior.behavior_id not in (constant.Behavior.SLEEP, constant.Behavior.WAKE_UP_BY_NOISE) and pl.position == list(SCENE_DORM)
      and npc.action_info.sleep_disturbed_end_time > cache.game_time,
      (npc.behavior.behavior_id, pl.position, npc.action_info.sleep_disturbed_end_time))
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("被吵醒后在行动前检查里执行「被搬运时醒来」", npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED and pl.action_info.carry_chara_id == 0,
      (npc.behavior.behavior_id, pl.action_info.carry_chara_id))
pl.action_info.past_move_position_list = []
clean_carry_case()

# 睡饱自然醒（熟睡值降到 0）：带着残留标记、博士在场且交互对象是她时，不走睡奸的恢复流程
recover_calls = []
npc = make_carried_sleeper(stale_unconscious=True)
npc.sleep_point = 5
with mock.patch.object(handle_npc_ai_in_h, "recover_from_unconscious_h", lambda *args, **kwargs: recover_calls.append(args)):
    realtime_settle.settle_sleep(CARRY_NPC_ID, 10)
check("被搬运时睡饱自然醒：不走睡奸的恢复流程（H 已结束，按 H 失败收尾不合适），睡眠结束、残留标记清掉",
      recover_calls == [] and npc.behavior.behavior_id != constant.Behavior.SLEEP and npc.sp_flag.unconscious_h == 0,
      (recover_calls, npc.behavior.behavior_id, npc.sp_flag.unconscious_h))
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("自然醒后在行动前检查里执行「被搬运时醒来」", npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED, npc.behavior.behavior_id)
clean_carry_case()

# 时停中被搬运：时停解除前一直带着走，解除后恢复意识
npc = make_carried_sleeper()
npc.behavior = game_type.Behavior()
npc.behavior.behavior_id = constant.Behavior.WAIT
npc.behavior.duration = 30
npc.behavior.start_time = cache.game_time
cache.time_stop_mode = True
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
still_carried_in_time_stop = pl.action_info.carry_chara_id == CARRY_NPC_ID
cache.time_stop_mode = False
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("时停中照旧被搬运，时停解除后执行「被搬运时醒来」（修复前时停解除也不会放下她）",
      still_carried_in_time_stop and npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED and pl.action_info.carry_chara_id == 0,
      (still_carried_in_time_stop, npc.behavior.behavior_id, pl.action_info.carry_chara_id))
clean_carry_case()

# 烂醉时被搬运：醉酒等级 2 及以上照旧带着走，酒醒到 1 级以下才恢复意识
npc = make_carried_sleeper()
npc.behavior = game_type.Behavior()
npc.behavior.start_time = cache.game_time
carried_by_drunk_point = {}
for drunk_point in (90, 70, 40):
    npc.drunk_point = drunk_point
    handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
    carried_by_drunk_point[drunk_point] = pl.action_info.carry_chara_id == CARRY_NPC_ID
check("烂醉、醉酒时照旧被搬运，酒醒到微醺时执行「被搬运时醒来」",
      carried_by_drunk_point == {90: True, 70: True, 40: False} and npc.behavior.behavior_id == constant.Behavior.WAKE_UP_WHEN_CARRIED,
      (carried_by_drunk_point, npc.behavior.behavior_id))
clean_carry_case()

# H 中仍被搬运（旧存档）时恢复意识：只结束搬运，不叠加「被搬运时醒来」
npc = make_carried_sleeper()
npc.behavior = game_type.Behavior()
npc.behavior.start_time = cache.game_time
npc.sp_flag.is_h = True
handle_npc_ai.run_npc_pre_behavior_checks(CARRY_NPC_ID, cache.game_time)
check("H 中恢复意识时只结束搬运，不执行「被搬运时醒来」",
      pl.action_info.carry_chara_id == 0 and npc.behavior.behavior_id != constant.Behavior.WAKE_UP_WHEN_CARRIED,
      (pl.action_info.carry_chara_id, npc.behavior.behavior_id))
clean_carry_case()

# ==== 8.14 睡奸中醒来的装睡、醉奸结束后的残留标记 ====
section("睡奸中醒来裁决继续 H 时装睡；醉奸结束后的醉酒无意识标记在博士离开或酒醒时清掉")

# 已陷落的睡奸对象被吵醒、裁决继续 H：结束她的睡眠之前先记下她在睡，装睡与睡奸醒来状态才会生效
h_target, sleeper, all_in_h, panel_error = run_wake_case(in_h=True, wake_id=WAKE_H_TARGET_ID, fall_level=3)
check("已陷落的睡奸对象被吵醒、继续 H：装睡、仍为睡眠无意识、获得睡奸醒来状态，H 照常继续（修复前睡眠先被结束，两处「是否在睡」永远不成立）",
      panel_error is None and h_target.h_state.pretend_sleep and h_target.sp_flag.unconscious_h == 1 and h_target.sp_flag.sleep_h_awake
      and h_target.sp_flag.is_h and handle_premise.handle_self_sleep_h_awake_but_pretend_sleep(WAKE_H_TARGET_ID),
      (repr(panel_error), h_target.h_state.pretend_sleep, h_target.sp_flag.unconscious_h, h_target.sp_flag.sleep_h_awake, h_target.sp_flag.is_h))
handle_npc_ai.run_npc_pre_behavior_checks(WAKE_H_TARGET_ID, cache.game_time)
check("装睡的 H 进行中，行动前检查不动她的睡眠无意识标记", h_target.sp_flag.unconscious_h == 1, h_target.sp_flag.unconscious_h)
settle_default.handle_both_h_state_reset(0, 1, game_type.CharacterStatusChange(), cache.game_time)
handle_npc_ai.run_npc_pre_behavior_checks(WAKE_H_TARGET_ID, cache.game_time)
check("装睡的 H 结束、博士仍在场：睡眠无意识标记清掉，不再一直被当作在睡",
      not h_target.sp_flag.is_h and h_target.sp_flag.unconscious_h == 0 and not handle_premise.handle_unconscious_flag_1(WAKE_H_TARGET_ID),
      (h_target.sp_flag.is_h, h_target.sp_flag.unconscious_h))
clean_wake_case()

DRUNK_NPC_ID = 9450
""" 被醉奸的干员 fixture """


def make_drunk_h_ended(drunk_point: int) -> game_type.Character:
    """
    摆好一场刚结束的醉奸：博士与她在同一房间，她身上留着醉酒无意识标记，双方 H 状态已归零
    Keyword arguments:
    drunk_point -- 结束时她的醉酒值
    Return arguments:
    game_type.Character -- 被醉奸的干员
    """
    now_npc = make_character(DRUNK_NPC_ID, "醉奸对象")
    move_to(0, SCENE_DORM)
    pl.target_character_id = DRUNK_NPC_ID
    now_npc.drunk_point = drunk_point
    settle_default.handle_unconscious_flag_to_2(DRUNK_NPC_ID, 1, game_type.CharacterStatusChange(), cache.game_time)
    now_npc.sp_flag.is_h = True
    pl.sp_flag.is_h = True
    settle_default.handle_both_h_state_reset(0, 1, game_type.CharacterStatusChange(), cache.game_time)
    return now_npc


def clean_drunk_case():
    """
    撤掉醉奸 fixture，复原博士
    Keyword arguments:
    无
    Return arguments:
    无
    """
    remove_character(DRUNK_NPC_ID)
    pl.sp_flag.is_h = False
    pl.target_character_id = 0
    move_to(0, SCENE_DORM)


npc = make_drunk_h_ended(70)
handle_npc_ai.run_npc_pre_behavior_checks(DRUNK_NPC_ID, cache.game_time)
still_flag_when_drunk = npc.sp_flag.unconscious_h == 2
npc.drunk_point = 0
handle_npc_ai.run_npc_pre_behavior_checks(DRUNK_NPC_ID, cache.game_time)
pl.behavior.behavior_id = constant.Behavior.CHAT
chat_weight, _unused = handle_premise.get_weight_from_premise_dict({"high_1"}, 0, {})
pl.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
check("醉奸结束后博士在场：还醉着时保留醉酒无意识标记，酒醒到清醒时清掉，普通口上恢复显示（修复前一直留着，普通口上权重为 0）",
      still_flag_when_drunk and npc.sp_flag.unconscious_h == 0 and chat_weight > 0, (still_flag_when_drunk, npc.sp_flag.unconscious_h, chat_weight))
before_disgust = npc.status_data[disgust_state_id]
settle_default.handle_self_add_middle_disgust(DRUNK_NPC_ID, 1, game_type.CharacterStatusChange(), cache.game_time)
check("酒醒后反感等负面状态照常结算", npc.status_data[disgust_state_id] > before_disgust, (before_disgust, npc.status_data[disgust_state_id]))
clean_drunk_case()

npc = make_drunk_h_ended(70)
move_to(0, DORM_CORRIDOR)
handle_npc_ai.run_npc_pre_behavior_checks(DRUNK_NPC_ID, cache.game_time)
check("醉奸结束后博士离开她所在的地点：即使还醉着也清掉醉酒无意识标记", npc.sp_flag.unconscious_h == 0, npc.sp_flag.unconscious_h)
clean_drunk_case()

npc = make_drunk_h_ended(0)
npc.sp_flag.is_h = True
handle_npc_ai.run_npc_pre_behavior_checks(DRUNK_NPC_ID, cache.game_time)
check("醉奸进行中（在 H 中）不动醉酒无意识标记", npc.sp_flag.unconscious_h == 2, npc.sp_flag.unconscious_h)
clean_drunk_case()

# ==== 8.15 搬运与 H 互斥 ====
section("搬运与 H 互斥：博士或被搬运的干员进入 H 时，博士把被搬运的干员放下")
OTHER_NPC_ID = 9442
""" 搬运期间同屋的另一名清醒干员 fixture """


def settle_behavior_now(character_id: int, behavior_id: str):
    """
    让角色照真实的行为结算走一遍指定行为（5 分钟）
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 行为id
    Return arguments:
    无
    """
    chara_data = cache.character_data[character_id]
    chara_data.behavior.behavior_id = behavior_id
    chara_data.behavior.duration = 5
    chara_data.behavior.start_time = cache.game_time
    settle_behavior.handle_settle_behavior(character_id, cache.game_time + datetime.timedelta(minutes=5))


def clean_carry_h_case():
    """
    撤掉本节的 fixture 角色，复原博士的 H 状态、行为与宿舍门
    Keyword arguments:
    无
    Return arguments:
    无
    """
    remove_character(OTHER_NPC_ID)
    pl.sp_flag.is_h = False
    pl.behavior = game_type.Behavior()
    pl.behavior.start_time = cache.game_time
    cache.scene_data[scene_str(SCENE_DORM)].close_flag = 0
    clean_carry_case()


# 搬着睡着的她回房间后选睡奸：指令照旧可选，进入 H 时博士把她原地放下
npc = make_carried_sleeper()
pl.hit_point = pl.hit_point_max
pl.mana_point = pl.mana_point_max
sleep_h_selectable = see_instruct_panel.judge_single_instruct_filter(constant.Instruct.SLEEP_H, {}, constant.InstructType.OBSCENITY, use_type_filter_flag=False)[0]
settle_default.handle_unconscious_flag_to_1(CARRY_NPC_ID, 1, game_type.CharacterStatusChange(), cache.game_time)
settle_behavior_now(0, constant.Behavior.H)
check("搬运着睡着的干员时选睡奸：照旧可选，进入 H 时博士把她原地放下（修复前搬运状态一直带进 H）",
      sleep_h_selectable and pl.sp_flag.is_h and npc.sp_flag.is_h and pl.action_info.carry_chara_id == 0 and npc.position == pl.position,
      (sleep_h_selectable, pl.sp_flag.is_h, npc.sp_flag.is_h, pl.action_info.carry_chara_id, npc.position, pl.position))
clean_carry_h_case()

# 搬运中被另一名干员逆推：博士进入 H，同样放下被搬运的干员
npc = make_carried_sleeper()
other = make_character(OTHER_NPC_ID, "另一名干员")
other.target_character_id = 0
settle_behavior_now(OTHER_NPC_ID, constant.Behavior.H_BY_ACTIVE)
check("搬运中被另一名干员逆推：博士进入 H，放下被搬运的干员", pl.sp_flag.is_h and pl.action_info.carry_chara_id == 0,
      (pl.sp_flag.is_h, pl.action_info.carry_chara_id))
clean_carry_h_case()

# 博士只让交互对象进入 H、自己不进入 H 状态（隐奸等）：同样放下被搬运的干员
npc = make_carried_sleeper()
other = make_character(OTHER_NPC_ID, "另一名干员")
pl.target_character_id = OTHER_NPC_ID
settle_default.handle_t_h_flag_to_1(0, 1, game_type.CharacterStatusChange(), cache.game_time)
check("搬运中博士让另一名干员进入 H（博士自己不进入 H 状态）：同样放下被搬运的干员",
      other.sp_flag.is_h and not pl.sp_flag.is_h and pl.action_info.carry_chara_id == 0, (other.sp_flag.is_h, pl.sp_flag.is_h, pl.action_info.carry_chara_id))
clean_carry_h_case()

# 被搬运的干员自己进入 H（如被拉进群交）：放下；与博士无关的干员进入 H：不动搬运
npc = make_carried_sleeper()
other = make_character(OTHER_NPC_ID, "另一名干员")
settle_default.handle_h_flag_to_1(OTHER_NPC_ID, 1, game_type.CharacterStatusChange(), cache.game_time)
carry_after_other_h = pl.action_info.carry_chara_id
settle_default.handle_h_flag_to_1(CARRY_NPC_ID, 1, game_type.CharacterStatusChange(), cache.game_time)
check("与博士无关的干员进入 H 不动搬运；被搬运的干员自己进入 H 时放下她",
      carry_after_other_h == CARRY_NPC_ID and pl.action_info.carry_chara_id == 0, (carry_after_other_h, pl.action_info.carry_chara_id))
clean_carry_h_case()

# ==== 8.16 蚀刻章的结算 id 与数值 ====
section("蚀刻章：母女一起群交结算「母女丼」906（不再误发 905），完全催眠 1 名干员即获得「安眠旋律」622，乱伦 H 100 次才获得「血脉相连」942")
from Script.UI.Panel import achievement_panel  # noqa: E402

GS_MOTHER_ID, GS_DAUGHTER_ID = 9451, 9452
""" 群交中的母亲与女儿 fixture """
saved_pl_position = list(pl.position)
gs_mother = make_character(GS_MOTHER_ID, "群交母亲")
gs_daughter = make_character(GS_DAUGHTER_ID, "群交女儿", daughter=True, mother_id=GS_MOTHER_ID)
for chara_id in (0, GS_MOTHER_ID, GS_DAUGHTER_ID):
    move_to(chara_id, SCENE_DORM)
gs_mother.sp_flag.is_h = True
gs_daughter.sp_flag.is_h = True
# 群交开始时的记录初始化（同 settle default 的群交开始结算）
cache.achievement.group_sex_record = {1: [], 2: []}
for achievement_id in (905, 906, 622):
    cache.achievement.achievement_dict[achievement_id] = False
with mock.patch.object(achievement_panel.handle_premise, "handle_group_sex_mode_off", lambda character_id: 0):
    got_list = achievement_panel.settle_chara_group_sex()
check("母女同在场且都在 H 中：获得「母女丼」906，不误发「你来的正是时候」905（修复前写成 905，906 永远拿不到）",
      906 in got_list and 905 not in got_list, got_list)
gs_mother.sp_flag.is_h = False
cache.achievement.achievement_dict[906] = False
with mock.patch.object(achievement_panel.handle_premise, "handle_group_sex_mode_off", lambda character_id: 0):
    got_list = achievement_panel.settle_chara_group_sex()
check("母亲在场但不在 H 中：不获得 906", 906 not in got_list, got_list)
remove_character(GS_MOTHER_ID)
remove_character(GS_DAUGHTER_ID)
move_to(0, saved_pl_position)
cache.achievement.group_sex_record = {}

# 完全催眠：只让一名角色算作完全催眠
saved_npc_id_got = set(cache.npc_id_got)
hypnosis_npc = make_character(GS_MOTHER_ID, "完全催眠干员")
cache.npc_id_got.add(GS_MOTHER_ID)
with mock.patch.object(achievement_panel.handle_premise, "handle_self_has_been_complete_hypnosis", lambda character_id: character_id == GS_MOTHER_ID):
    got_list = achievement_panel.settle_chara_hypnosis()
check("完全催眠 1 名干员：获得「安眠旋律」622（修复前数值需求是 5，与描述不符）", 622 in got_list, got_list)
remove_character(GS_MOTHER_ID)
cache.npc_id_got.clear()
cache.npc_id_got.update(saved_npc_id_got)

# 乱伦 H 的次数：描述是 100 次
# achievement_flow 每次都会先算好全部数值类成就的判断值，其中要读龙门币，无头 fixture 的资源表可能是空的
cache.rhodes_island.materials_resouce.setdefault(1, 0)
saved_daughter_h_count = cache.achievement.h_with_daughter_count
cache.achievement.achievement_dict[942] = False
cache.achievement.h_with_daughter_count = 99
achievement_panel.achievement_flow(_("乱伦"))
got_942_at_99 = cache.achievement.achievement_dict.get(942, False)
cache.achievement.h_with_daughter_count = 100
achievement_panel.achievement_flow(_("乱伦"))
check("与女儿乱伦 H 99 次不获得「血脉相连」942，100 次获得（修复前数值需求是 5，与描述的 100 次不符）",
      not got_942_at_99 and cache.achievement.achievement_dict.get(942, False), (got_942_at_99, cache.achievement.achievement_dict.get(942)))
cache.achievement.h_with_daughter_count = saved_daughter_h_count

finish()
