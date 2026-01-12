from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.Design import game_time, attr_calculation, talk, handle_premise
import random

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """

def update_field_commission():
    """
    刷新外勤委托的相关数据
    """
    judge_field_commission_finish()
    find_nation_field_commission()

def get_commission_demand_and_reward(commission_id: int, send_npc_list = [], demand_or_reward: bool = False, deduction_or_increase: bool = False) -> List[str]:
    """
    获取委托需求或奖励\n
    Keyword arguments:\n
    commission_id -- 委托编号\n
    send_npc_list -- 派遣人员列表，默认为空\n
    demand_or_reward -- False为需求，True为奖励，默认为False\n
    deduction_or_increase -- 是否扣除或增加资源，默认为False\n
    Return arguments:\n
    return_list -- [是否满足, 需求类型文本, 需求全文]
    """
    commission_data = game_config.config_commission[commission_id]
    # 获取需求或奖励文本
    if demand_or_reward == False:
        all_text = commission_data.demand
    else:
        all_text = commission_data.reward
    # 文本可能以“&”分隔
    if "&" in all_text:
        text_list = all_text.split("&")
    else:
        text_list = [all_text]
    # 初始化变量
    satify_flag = True # 是否满足
    type_text = "" # 类型文本
    full_text = "" # 全文

    # 遍历文本列表
    for now_text in text_list:
        type_text, full_text, satify_flag = process_commission_text(now_text, demand_or_reward, deduction_or_increase, send_npc_list, type_text, full_text, satify_flag)

    # 特殊奖励单独处理
    if demand_or_reward == True and deduction_or_increase == True:
        if commission_id == 1104:
            cache.rhodes_island.vehicles[51][0] += 1
            info_draw = draw.WaitDraw()
            info_draw.text = _("\n获得了一辆新的载具：{0}\n").format(game_config.config_vehicle[51].name)
            info_draw.style = "gold_enrod"
            info_draw.width = window_width
            info_draw.draw()
        # 抓捕
        elif "追捕" in commission_data.reward:
            from Script.Settle import default
            from Script.UI.Panel import confinement_and_training
            fugitive_id = int(commission_data.reward.split("_")[1])
            # 需要有空房间
            empty_room = confinement_and_training.get_unused_prison_dormitory()
            if empty_room != "":
                character_data: game_type.Character = cache.character_data[fugitive_id]
                character_data.position = ["关押", f"{empty_room}"]
                confinement_and_training.chara_become_prisoner(fugitive_id)
                default.handle_chara_on_line(fugitive_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)

    return_list = [satify_flag, type_text, full_text]
    return return_list


def process_commission_text(now_text, demand_or_reward, deduction_or_increase, send_npc_list, type_text, full_text, satify_flag):
    """
    处理委托文本\n
    Keyword arguments:\n
    now_text -- 当前文本\n
    demand_or_reward -- False为需求，True为奖励\n
    deduction_or_increase -- 是否扣除或增加资源\n
    send_npc_list -- 派遣人员列表\n
    type_text -- 类型文本\n
    full_text -- 全文\n
    satify_flag -- 是否满足\n
    Return arguments:\n
    type_text -- 类型文本\n
    full_text -- 全文\n
    satify_flag -- 是否满足
    """
    from Script.Design import character

    # 无则直接返回
    if now_text == _("无"):
        type_text += _("无 ")
        full_text += _("无 ")
        satify_flag = True
        return type_text, full_text, satify_flag

    # 处理文本
    text_list = now_text.split("_")
    item_id = int(text_list[1])
    item_num = int(text_list[2])
    item_type = ""
    item_name = ""

    # 资源
    if text_list[0] == "r":
        item_name = game_config.config_resouce[item_id].name
        item_type = game_config.config_resouce[item_id].type
        now_have_item_num = cache.rhodes_island.materials_resouce[item_id]
    # 能力
    elif text_list[0] == "a":
        item_name = game_config.config_ability[item_id].name
        item_type = item_name
        # 如果字符串里带"技能"，则删去
        if _("技能") in item_name:
            item_type = item_name.replace(_("技能"), "")
        now_have_item_num = sum(cache.character_data[character_id].ability[item_id] for character_id in send_npc_list)
        now_have_item_num = 0
        for character_id in send_npc_list:
            now_have_item_num += cache.character_data[character_id].ability[item_id]
            # 如果装备完美维护，则能力值+1，但不超过8级
            if handle_premise.handle_self_equipment_maintenance_ge_2(character_id) and cache.character_data[character_id].ability[item_id] < 8:
                now_have_item_num += 1
            # 如果装备中度损坏，则能力值-1，但不低于0
            if handle_premise.handle_self_equipment_damaged_ge_2(character_id) and cache.character_data[character_id].ability[item_id] > 0:
                now_have_item_num -= 1
    # 经验
    elif text_list[0] == "e":
        item_name = game_config.config_experience[item_id].name
        item_type = item_name
        # 如果是奖励，则只显示大类
        if demand_or_reward:
            item_type = _("经验")
        now_have_item_num = sum(cache.character_data[character_id].experience[item_id] for character_id in send_npc_list)
    # 宝珠
    elif text_list[0] == "j":
        item_name = game_config.config_juel[item_id].name
        item_type = item_name
        # 如果是奖励，则只显示大类
        if demand_or_reward:
            item_type = _("宝珠")
        now_have_item_num = sum(cache.character_data[character_id].juel[item_id] for character_id in send_npc_list)
    # 素质
    elif text_list[0] == "t":
        item_name = game_config.config_talent[item_id].name
        item_type = item_name
        # 如果是奖励，则只显示大类
        if demand_or_reward:
            item_type = _("素质")
        now_have_item_num = sum(cache.character_data[character_id].talent[item_id] for character_id in send_npc_list)
    # 委托
    elif text_list[0] == "m":
        item_name = _("委托")
        item_type = _("委托")
        now_have_item_num = 0
    # 角色adv编号
    elif text_list[0] == "c":
        item_name = _("指定干员")
        item_type = _("指定干员")
        chara_id = character.get_character_id_from_adv(item_id)
        need_chara_name = cache.character_data[chara_id].name
        item_name = f"[{item_id}]{need_chara_name}"
        now_have_item_num = 0
        # 1的话需要出场
        if item_num == 1:
            item_name += _("出勤")
            if item_id in send_npc_list:
                now_have_item_num = 1
        # 否则禁止出场
        else:
            item_name += _("禁止出勤")
            if item_id in send_npc_list:
                now_have_item_num = -1
                satify_flag = False
    # 特产
    elif text_list[0] == "特产":
        # 默认值
        item_name = _("特产")
        item_type = _("特产")
        now_have_item_num = 0
        # 获取当前地点的特产
        now_location = cache.rhodes_island.current_location[0]
        nation_specialty_list = game_config.config_resouce_data_of_nation.get(now_location, [])
        # 如果有特产的话，获取特产数量
        if len(nation_specialty_list):
            item_id = nation_specialty_list[0]
            item_name = game_config.config_resouce[item_id].name
            now_have_item_num = cache.rhodes_island.materials_resouce[item_id]
    # 声望
    elif text_list[0] == "声望":
        item_name = _("声望")
        item_type = _("声望")
        # 声望的显示为实际值的百分之一
        item_num *= 0.01
        # 0为当前国家
        if item_id == 0:
            now_country = cache.rhodes_island.current_location[0]
            for nation_id in game_config.config_nation_data_of_country_subordinate:
                nation_data = game_config.config_nation[nation_id]
                if nation_data.country == now_country:
                    item_id = nation_id
                    item_name = nation_data.name + item_name
                    now_have_item_num = cache.country.nation_reputation[nation_id]
                    break
        else:
            item_name = game_config.config_nation[item_id].name + item_name
            now_have_item_num = cache.country.nation_reputation[item_id]
    # 好感
    elif text_list[0] == "好感":
        item_name = _("好感")
        item_type = _("好感")
        item_id = character.get_character_id_from_adv(item_id)
        character_id = item_id
        item_name = cache.character_data[character_id].name + item_name
        now_have_item_num = cache.character_data[character_id].favorability[0]
    # 信赖
    elif text_list[0] == "信赖":
        item_name = _("信赖")
        item_type = _("信赖")
        item_id = character.get_character_id_from_adv(item_id)
        character_id = item_id
        item_name = cache.character_data[character_id].name + item_name
        now_have_item_num = cache.character_data[character_id].trust
    # 攻略
    elif text_list[0] == "攻略":
        item_name = _("攻略程度")
        item_type = _("攻略程度")
        item_id = character.get_character_id_from_adv(item_id)
        character_id = item_id
        item_name = cache.character_data[character_id].name + item_name
        now_have_item_num = attr_calculation.get_character_fall_level(character_id)
    # 招募
    elif text_list[0] == _("招募"):
        if item_num == 0:
            item_name = _("未招募")
        else:
            item_name = _("已招募")
        item_type = _("招募")
        item_id = character.get_character_id_from_adv(item_id)
        character_id = item_id
        item_name =  item_name + cache.character_data[character_id].name
        now_have_item_num = 1
        # 如果不在当前干员中，且没有离线，则未招募
        if character_id not in cache.npc_id_got and handle_premise.handle_normal_7(character_id):
            now_have_item_num = 0
    # 追捕
    elif text_list[0] == "追捕":
        item_name = _("追捕")
        item_type = _("追捕")
        item_id = character.get_character_id_from_adv(item_id)
        character_id = item_id
        item_name += cache.character_data[character_id].name
        now_have_item_num = 1

    # 需求
    if not demand_or_reward:
        # 如果不够数量，设为不满足
        if now_have_item_num < item_num:
            satify_flag = False
        else:
            # 扣除资源
            if deduction_or_increase and text_list[0] == "r":
                cache.rhodes_island.materials_resouce[item_id] -= item_num
            elif deduction_or_increase and text_list[0] == _("声望"):
                # 将不再扣除声望
                # cache.country.nation_reputation[item_id] -= item_num
                pass
    # 奖励
    else:
        # 增加资源
        if deduction_or_increase:
            # 资源
            if text_list[0] == "r":
                cache.rhodes_island.materials_resouce[item_id] += item_num
            # 经验
            elif text_list[0] == "e":
                for character_id in send_npc_list:
                    cache.character_data[character_id].experience[item_id] += item_num
            # 宝珠
            elif text_list[0] == "j":
                for character_id in send_npc_list:
                    cache.character_data[character_id].juel[item_id] += item_num
            # 素质
            elif text_list[0] == "t":
                for character_id in send_npc_list:
                    if item_num > 0:
                        cache.character_data[character_id].talent[item_id] = 1
                    elif item_num < 0:
                        cache.character_data[character_id].talent[item_id] = 0
            # 角色
            elif text_list[0] == "c":
                # 如果未获得该干员，则获得
                if item_id not in cache.npc_id_got and handle_premise.handle_normal_7(item_id):
                    cache.rhodes_island.recruited_id.add(item_id)
                item_name = cache.character_data[item_id].name
                item_num = _("成为干员")
            # 特产
            elif text_list[0] == _("特产"):
                cache.rhodes_island.materials_resouce[item_id] += item_num
            # 委托部分，-1不可完成，0可以进行，1已完成
            elif text_list[0] == "m":
                if item_num == -1:
                    cache.rhodes_island.shut_down_field_commissions_set.add(item_id)
                elif item_num == 0:
                    if item_id in cache.rhodes_island.shut_down_field_commissions_set:
                        cache.rhodes_island.shut_down_field_commissions_set.remove(item_id)
                    elif item_id in cache.rhodes_island.finished_field_commissions_set:
                        cache.rhodes_island.finished_field_commissions_set.remove(item_id)
                elif item_num == 1:
                    cache.rhodes_island.finished_field_commissions_set.add(item_id)
            # 声望
            elif text_list[0] == _("声望"):
                # 在前面已经乘过了，不需要再乘一遍
                # item_num *= 0.01
                cache.country.nation_reputation[item_id] += item_num
            # 好感
            elif text_list[0] == _("好感"):
                cache.character_data[item_id].favorability[0] += item_num
            # 信赖
            elif text_list[0] == _("信赖"):
                cache.character_data[item_id].trust += item_num

    # 添加类型文本
    if item_type not in type_text:
        type_text += f"{item_type}　"

    # 添加全文
    if not demand_or_reward:
        full_text += f"{item_name}:{now_have_item_num}/{item_num} "
    else:
        full_text += f"{item_name}:{item_num} "

    return type_text, full_text, satify_flag


def judge_field_commission_finish():
    """
    判断与结算外勤委托的完成
    """

    from Script.Settle import default
    from Script.UI.Panel import achievement_panel, equipmen_panel
    from Script.Design import second_behavior
    from Script.UI.Panel import manage_vehicle_panel

    now_ongoing_field_commissions = cache.rhodes_island.ongoing_field_commissions.copy()
    draw_text = ""
    for commision_id in now_ongoing_field_commissions:
        end_time = cache.rhodes_island.ongoing_field_commissions[commision_id][1]
        if game_time.judge_date_big_or_small(cache.game_time, end_time) or cache.debug_mode:
            # 获取派遣人员列表
            send_npc_list = cache.rhodes_island.ongoing_field_commissions[commision_id][0]
            # 获取奖励
            reward_return_list = get_commission_demand_and_reward(commision_id, send_npc_list, True, True)
            reward_text = reward_return_list[2]
            # 加入已完成的委托
            if commision_id not in cache.rhodes_island.finished_field_commissions_set:
                cache.rhodes_island.finished_field_commissions_set.add(commision_id)
            # 奖励信息
            commision_name = game_config.config_commission[commision_id].name
            draw_text += "\n"
            # 结算队长
            if len(send_npc_list):
                leader_id = send_npc_list[0]
                second_behavior.character_get_second_behavior(leader_id, "end_field_commission_as_leader")
                talk.must_show_talk_check(leader_id)
            # 遍历派遣人员
            for character_id in send_npc_list:
                cache.character_data[character_id].sp_flag.field_commission = 0
                handle_premise.settle_chara_unnormal_flag(character_id, 7)
                # 派遣人员上线
                default.handle_chara_on_line(character_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)
                draw_text += f"{cache.character_data[character_id].name} "
            # 载具损坏与回收
            vehicle_text = manage_vehicle_panel.settle_vehicle(commision_id)
            draw_text += vehicle_text
            # 判断是否会招募到新干员
            recruited_text = settle_recruit_new_chara(commision_id)
            # 装备损坏
            equipment_damage_text = equipmen_panel.settle_equipment_damage_in_commission(commision_id)
            # 移除委托
            cache.rhodes_island.ongoing_field_commissions.pop(commision_id)
            # 最后总结
            draw_text += _("完成了委托：{0}，获得奖励：{1}\n\n").format(commision_name, reward_text)
            draw_text += recruited_text
            draw_text += equipment_damage_text
            # 结算成就
            cache.achievement.field_commission_count += 1
            achievement_panel.achievement_flow(_("外勤"))
            if "追捕" in game_config.config_commission[commision_id].reward:
                achievement_panel.achievement_flow(_("外勤"), 306)

    # 绘制完成委托
    if len(draw_text):
        info_draw = draw.WaitDraw()
        info_draw.text = draw_text
        info_draw.style = "gold_enrod"
        info_draw.width = window_width
        info_draw.draw()


def settle_recruit_new_chara(commision_id: int) -> str:
    """
    结算新干员招募
    Keyword arguments:
    commision_id -- 委托编号
    Return arguments:
    recruited_text -- 招募信息
    """
    from Script.UI.Panel import recruit_panel
    recruited_text = ""
    # 招募概率与等级相关
    base_rate = 0.01 * game_config.config_commission[commision_id].level
    recruited_text = ""
    if random.random() < base_rate:
        recruitable_npc_id_list = recruit_panel.find_recruitable_npc()
        wait_id_list = []
        # 只能招募到当地的干员
        for chara_id in recruitable_npc_id_list:
            character_data = cache.character_data[chara_id]
            # 筛选出出生地是当前罗德岛所在地的角色
            if character_data.relationship.birthplace != cache.rhodes_island.current_location[0]:
                continue
            else:
                wait_id_list.append(chara_id)
        # 如果有符合条件的干员，随机招募一个
        if len(wait_id_list):
            choice_id = random.choice(wait_id_list)
            cache.rhodes_island.recruited_id.add(choice_id)
            # 绘制招募信息
            recruited_text = _("※ 在进行委托时队员们意外遇到了一个同行的路人{0}，在短暂的相处中，她对罗德岛产生了兴趣，愿意加入我们成为一名新的干员（请前往博士办公室确认） ※\n\n").format(cache.character_data[choice_id].name)

    return recruited_text


def find_nation_field_commission():
    """
    寻找来自势力的外勤委托
    Keyword arguments:
    Return arguments:
    """
    # TODO: 未实装

def create_temp_commission(
    name: str,
    level: int,
    type: str,
    people: int,
    time: int,
    demand: str,
    reward: str,
    description: str,
    commission_id: int = 10001,
    related_id: int = -1,
    special: int = 1,
    country_id: int = -1,
):
    """
    通用函数：创建一个临时的委托数据并加入 game_config.config_commission，
    使用 config_def 中的 Commission 类
    """
    from Script.Config.config_def import Commission
    # 防止重复
    while commission_id in game_config.config_commission:
        commission_id += 1
    temp_commission = Commission()
    temp_commission.cid = commission_id
    temp_commission.name = name
    temp_commission.level = level
    temp_commission.type = type
    temp_commission.people = people
    temp_commission.time = time
    temp_commission.demand = demand
    temp_commission.reward = reward
    temp_commission.description = description
    # 设置默认值
    temp_commission.related_id = related_id      # 默认无关联委托
    temp_commission.special = special  # 默认为特殊委托
    temp_commission.country_id = country_id      # 通用委托，国家id设为 -1

    game_config.config_commission[commission_id] = temp_commission
    game_config.config_commission_id_by_country[country_id].append(commission_id)
    # 对路径data\csv\Commission.csv进行更新，在最后一行加入新的委托数据
    new_commission_data = f"{commission_id},{name},{country_id},{level},{type},{people},{time},{demand},{reward},{related_id},{special},{description}\n"
    with open("data/csv/Commission.csv", "a", encoding="utf-8") as f:
        f.write(new_commission_data)

def create_capture_fugitive_commission(fugitive_id: int):
    """
    创建“追捕逃跑囚犯干员”委托
    Keyword arguments:
    fugitive_id -- 逃跑囚犯干员编号
    """
    fugitive_character = cache.character_data[fugitive_id]
    fugitive_combat = fugitive_character.ability[42] * 2
    required_combat = fugitive_combat * 2
    # 需求为2倍战斗能力
    demand_text = f"a_42_{required_combat}"
    # 特殊奖励单独处理
    create_temp_commission(
        name=_("追捕囚犯{0}").format(fugitive_character.name),
        level=2,
        type=_("追捕"),
        people=3,
        time=3,
        demand=demand_text,
        reward="追捕_{0}_1".format(fugitive_id),
        description=_("囚犯{0}从监狱逃跑了，请尽快将其抓回。").format(fugitive_character.name),
    )

