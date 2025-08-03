from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
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

def get_commission_demand_and_reward(commission_id: int, send_npc_list = [], demand_or_reward: bool = False, deduction_or_increase: bool = False) -> List:
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
        item_id = character.get_character_id_from_adv(item_id)
        need_chara_name = cache.character_data[item_id].name
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
                cache.country.nation_reputation[item_id] -= item_num
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
                item_num *= 0.01
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
    from Script.UI.Panel import manage_vehicle_panel, equipmen_panel, achievement_panel

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
                cache.character_data[leader_id].second_behavior["end_field_commission_as_leader"] = 1
                talk.must_show_talk_check(leader_id)
            # 遍历派遣人员
            for character_id in send_npc_list:
                cache.character_data[character_id].sp_flag.field_commission = 0
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


class Field_Commission_Panel:
    """
    用于显示外勤委托界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("常规外勤")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.send_npc_list = []
        """ 派遣人员列表 """
        self.send_vehicle_dict = {}
        """ 派遣载具字典 """

    def draw(self):
        """绘制对象"""

        title_text = _("外勤委托")
        commission_type_list = [_("常规外勤"), _("特殊外勤")]
        self.handle_panel = panel.PageHandlePanel([], CommissionDraw, 20, 1, self.width)

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制面板类型切换
            for commission_type in commission_type_list:
                if commission_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{commission_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(commission_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{commission_type}]",
                        f"\n{commission_type}",
                        self.width / len(commission_type_list),
                        cmd_func=self.change_panel,
                        args=(commission_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 设施信息
            now_level = cache.rhodes_island.facility_level[14]
            facility_info_text = ""
            facility_info_text += _("○通用委托无论在哪里都可以接到，地区委托则需要罗德岛移动到对应地区时才可接到，能接到的委托等级与机库的等级有关\n")
            facility_info_text += _("○常规外勤委托可以多次反复完成，特殊外勤只能完成一次\n")
            facility_info_text += _("○罗德岛的移动：控制中枢-指挥室-导航，购买载具：机库-格纳库-管理载具\n")
            facility_info_text += _("○当前机库等级：{0}，最高可接到{1}级的委托\n").format(now_level, now_level + 1)

            facility_info_draw = draw.NormalDraw()
            facility_info_draw.text = facility_info_text
            facility_info_draw.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 绘制提示信息
            info_text_list = ["委托等级", "委托类型", "委托名称", "派遣人数与耗时天数", "需求类型", "奖励类型"]
            for info_text in info_text_list:
                info_draw = draw.CenterDraw()
                info_draw.text = info_text
                info_draw.width = self.width / len(info_text_list)
                info_draw.draw()
            line_feed.draw()
            line = draw.LineDraw("~", self.width)
            line.draw()

            # 获取当前国家的委托列表
            now_country_id = cache.rhodes_island.current_location[0]
            if now_country_id in game_config.config_commission_id_by_country:
                now_country_commision_list = game_config.config_commission_id_by_country[now_country_id]
            else:
                now_country_commision_list = []
            common_commision_list = game_config.config_commission_id_by_country[-1]
            # 根据委托的等级对委托列表进行排序
            now_country_commision_list.sort(key=lambda x: game_config.config_commission[x].level)
            common_commision_list.sort(key=lambda x: game_config.config_commission[x].level)
            all_commision_list = now_country_commision_list + common_commision_list

            # 绘制委托信息
            final_commision_list = []
            for commision_id in all_commision_list:
                commision_data = game_config.config_commission[commision_id]
                # 跳过非当前面板的委托
                if self.now_panel == _("常规外勤") and commision_data.special != 0:
                    continue
                if self.now_panel == _("特殊外勤") and commision_data.special == 0:
                    continue
                # 以下为非debug模式下会进行的跳过判断
                if not cache.debug_mode:
                    # 跳过未满足前置委托的委托
                    if commision_data.related_id != -1 and commision_data.related_id not in cache.rhodes_island.finished_field_commissions_set:
                        continue
                    # 特殊外勤只能接受一次
                    if commision_data.special != 0 and commision_id in cache.rhodes_island.finished_field_commissions_set:
                        continue
                    # 跳过已经关闭的委托
                    if commision_id in cache.rhodes_island.shut_down_field_commissions_set:
                        continue
                    # 跳过等级大于设施等级+1的委托
                    if commision_data.level > cache.rhodes_island.facility_level[14] + 1:
                        continue
                    # 跳过含有角色出场且还没有招募到该角色的委托
                    if "c_" in commision_data.demand:
                        chara_adv = int(commision_data.demand.split("_")[1])
                        for character_id in cache.npc_id_got:
                            if cache.character_data[character_id].adv == chara_adv:
                                break
                        else:
                            continue
                # 如果满足条件，则加入最终委托列表
                final_commision_list.append(commision_id)

            # 遍历最终委托列表，绘制委托信息
            self.handle_panel.text_list = final_commision_list
            self.handle_panel.update()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, building_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        building_type -- 要切换的面板类型
        """

        self.now_panel = building_type

class CommissionDraw:
    """
    用于绘制外勤委托的绘制对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, commission_id: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.commission_id: int = commission_id
        """ 委托编号 """
        self.width: int = width
        """ 绘制的最大宽度 """
        self.is_button: bool = is_button
        """ 是否为按钮 """
        self.num_button: bool = num_button
        """ 是否为数字按钮 """
        self.button_id: int = button_id
        """ 按钮编号 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.button_return: str = ""
        """ 按钮返回文本 """
        self.send_npc_list = []
        """ 派遣人员列表 """
        self.send_vehicle_dict = {}
        """ 派遣载具字典 """

        info_text_list = ["委托等级", "委托类型", "委托名称", "派遣人数与耗时天数", "需求类型", "奖励类型"]

        commission_data = game_config.config_commission[self.commission_id]
        # 委托信息
        commission_name = commission_data.name
        commission_level = str(commission_data.level)
        commission_type = commission_data.type
        commission_people = str(commission_data.people) + _("人")
        commission_time = str(commission_data.time) + _("天")
        commission_people_and_time = f"{commission_people}  {commission_time}"
        demand_return_list = get_commission_demand_and_reward(self.commission_id, self.send_npc_list)
        commission_demand = demand_return_list[1]
        reward_return_list = get_commission_demand_and_reward(self.commission_id, self.send_npc_list, True)
        commision_reward = reward_return_list[1]
        # 修正文本宽度
        text_width = int((self.width - 1) / (len(info_text_list)))
        str_text_width = int(text_width / 2)
        if self.commission_id in cache.rhodes_island.ongoing_field_commissions:
            commission_name += _("（进行中）")
        # 最终文本
        commision_text = f"{commission_level.center(text_width,' ')}{commission_type.center(str_text_width,'　')}{commission_name.center(str_text_width,'　')}{commission_people_and_time.center(text_width,' ')}{commission_demand.center(str_text_width,'　')}{commision_reward.center(str_text_width,'　')}"
        # print(f"commision_text: {commision_text}")

        # 可以进行的，绘制为按钮
        if self.commission_id not in cache.rhodes_island.ongoing_field_commissions:
            commision_draw = draw.LeftButton(
                commision_text,
                "\n" + commission_name,
                self.width,
                cmd_func=self.commision_info,
                args=(self.commission_id,),
            )
            self.button_return = commision_draw.return_text
        # 正在进行的，绘制为灰色文字
        else:
            commision_draw = draw.NormalDraw()
            commision_draw.text = commision_text
            commision_draw.width = self.width
            commision_draw.style = "deep_gray"
        self.draw_text = commision_draw.text
        self.now_draw = commision_draw

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


    def commision_info(self, commision_id: int):
        """
        显示委托详细信息
        Keyword arguments:
        commision_id -- 委托编号
        """

        # 委托信息
        commision_data = game_config.config_commission[commision_id]
        commision_name = commision_data.name
        commision_level = str(commision_data.level)
        commision_people = str(commision_data.people) + _("人")
        commision_time = str(commision_data.time) + _("天")
        commision_capacity_int = (commision_data.time - 1) * commision_data.people
        commision_capacity_str = _(" {0}(天数-1) * {1}(人数) = {2}").format(commision_data.time - 1, commision_data.people, commision_capacity_int)
        reward_return_list = get_commission_demand_and_reward(commision_id, self.send_npc_list, True)
        commision_reward = reward_return_list[1]
        commision_description = commision_data.description
        # 将\n替换为换行符
        if "\\n" in commision_description:
            commision_description = commision_description.replace("\\n", "\n      ")

        # 派遣人员与载具
        self.send_npc_list = []
        self.send_vehicle_dict = {}

        while 1:
            # 是否满足条件
            all_satisfy = True
            # 获取需求
            demand_return_list = get_commission_demand_and_reward(commision_id, self.send_npc_list)
            commision_demand = demand_return_list[2]
            deman_satify = demand_return_list[0]

            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制委托信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n委托名称：{0}").format(commision_name)
            info_draw.text += _("\n委托等级：{0}").format(commision_level)
            info_draw.text += _("\n派遣人数：{0}").format(commision_people)
            info_draw.text += _("\n耗时天数：{0}").format(commision_time)
            info_draw.text += _("\n载具运量需求：{0}").format(commision_capacity_str)
            info_draw.text += _("\n其他需求：{0}").format(commision_demand)
            info_draw.text += _("\n奖励：{0}").format(commision_reward)
            info_draw.text += _("\n介绍：{0}").format(commision_description)
            info_draw.width = self.width
            info_draw.draw()

            # 绘制派遣人员与载具是否满足需求
            info_draw_2_text = _("\n\n派遣人员：")
            for chara_id in self.send_npc_list:
                chara_data = cache.character_data[chara_id]
                chara_name = chara_data.name
                info_draw_2_text += f"  {chara_name}"
            info_draw_2_text += _("\n\n派遣载具：")
            now_capacity = 0 # 当前运载量
            for vehicle_id in self.send_vehicle_dict:
                vehicle_name = game_config.config_vehicle[vehicle_id].name
                info_draw_2_text += f"  {vehicle_name} * {self.send_vehicle_dict[vehicle_id]}"
                now_capacity += game_config.config_vehicle[vehicle_id].capacity * self.send_vehicle_dict[vehicle_id]
            info_draw_2_text += _("  总运载量：{0}").format(now_capacity)
            info_draw_2_text += _("\n\n是否满足需求：")
            # 人数需求
            info_draw_2_text += _("人数需求：")
            if len(self.send_npc_list) >= commision_data.people:
                info_draw_2_text += "√"
            else:
                all_satisfy = False
                info_draw_2_text += "X"
            # 载具需求
            info_draw_2_text += _("  载具需求：")
            if now_capacity >= commision_capacity_int:
                info_draw_2_text += "√"
            else:
                all_satisfy = False
                info_draw_2_text += "X"
            # 其他需求
            info_draw_2_text += _("  其他需求：")
            if deman_satify:
                info_draw_2_text += "√"
            else:
                all_satisfy = False
                info_draw_2_text += "X"
            info_draw_2 = draw.NormalDraw()
            info_draw_2.text = info_draw_2_text
            info_draw_2.width = self.width
            info_draw_2.draw()

            # 调整派遣人员
            line_feed.draw()
            line_feed.draw()
            adjust_NPC_button_draw = draw.CenterButton(
                _("【调整派遣人员】"),
                _("\n【调整派遣人员】"),
                self.width / 3,
                cmd_func=self.adjust_send_npc,
                args=(commision_id,),
            )
            adjust_NPC_button_draw.draw()
            return_list.append(adjust_NPC_button_draw.return_text)

            # 调整使用载具
            adjust_vehicle_button_draw = draw.CenterButton(
                _("【调整使用载具】"),
                _("\n【调整使用载具】"),
                self.width / 3,
                cmd_func=self.adjust_send_vehicle,
                args=(commision_capacity_int,),
            )
            adjust_vehicle_button_draw.draw()
            return_list.append(adjust_vehicle_button_draw.return_text)
            line_feed.draw()
            line_feed.draw()

            line_feed.draw()
            yes_draw = draw.CenterButton(
                _("[执行委托]"),
                ("\n执行委托"),
                self.width / 2,
                cmd_func=self.send_commision,
                args=(commision_id,),
            )
            if all_satisfy:
                yes_draw.draw()
                return_list.append(yes_draw.return_text)

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == yes_draw.return_text or yrn == back_draw.return_text:
                break

    def adjust_send_npc(self, commision_id: int):
        """
        调整派遣人员
        Keyword arguments:
        commision_id -- 委托编号
        """

        commision_data = game_config.config_commission[commision_id]
        commision_people = commision_data.people
        self.lead_chara_id = 0
        self.now_commision_id = commision_id

        from Script.UI.Panel import common_select_NPC
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, 1, 0, 0)
        select_state = {}

        while 1:
            info_text = _("可派遣人员（需要{0}人）：\n").format(commision_people)
            info_text += _("（无意识状态下，或装备在严重损坏及以上、或助理、监狱长等特殊职位的干员无法出勤）\n")
            info_text += _("队长：")
            if self.lead_chara_id != 0:
                info_text += cache.character_data[self.lead_chara_id].name
            else:
                info_text += _("无")
            info_text += _("。队员：")
            # 遍历已选择的角色id列表
            for npc_id in self.send_npc_list:
                # 跳过队长
                if npc_id == self.lead_chara_id:
                    continue
                info_text += cache.character_data[npc_id].name + " "
            info_text += _("\n\n")

            npc_id_got_list = sorted(cache.npc_id_got)
            # 已选择的角色id列表
            final_list = []
            # 遍历角色id
            for npc_id in npc_id_got_list:
                if npc_id == 0:
                    continue
                # 跳过访客
                if handle_premise.handle_self_visitor_flag_1(npc_id):
                    continue
                # 跳过助理
                if handle_premise.handle_is_assistant(npc_id):
                    continue
                # 跳过监狱长
                if handle_premise.handle_work_is_warden(npc_id):
                    continue
                # 跳过2、7异常的角色
                if not handle_premise.handle_normal_2(npc_id) :
                    continue
                if not handle_premise.handle_normal_7(npc_id):
                    continue
                # 跳过装备严重损坏及以上的角色
                if handle_premise.handle_self_equipment_damaged_ge_3(npc_id):
                    continue
                now_list = [npc_id, self.select_this_npc, self.send_npc_list]
                final_list.append(now_list)
            now_draw_panel.text_list = final_list

            # 调用通用选择按钮列表函数
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("调整派遣人员"), info_text, select_state)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def select_this_npc(self, character_id: int):
        """
        选择当前人物
        Keyword arguments:
        character_id -- 人物id
        """
        if character_id in self.send_npc_list:
            self.send_npc_list.remove(character_id)
            # 如果队长被取消
            if character_id == self.lead_chara_id:
                # 如果还有其他人，则第一个人为队长
                if len(self.send_npc_list):
                    self.lead_chara_id = self.send_npc_list[0]
                else:
                    self.lead_chara_id = 0
        else:
            # 如果人数已经满了，则不添加
            max_people = game_config.config_commission[self.now_commision_id].people
            if len(self.send_npc_list) >= max_people:
                return
            self.send_npc_list.append(character_id)
            # 第一个被任命的人为队长
            if len(self.send_npc_list) == 1:
                self.lead_chara_id = character_id

    def add_this_vehicle(self, vehicle_id: int):
        """
        增加一辆载具
        Keyword arguments:
        vehicle_id -- 载具id
        """
        if vehicle_id not in self.send_vehicle_dict:
            self.send_vehicle_dict[vehicle_id] = 1
        else:
            self.send_vehicle_dict[vehicle_id] += 1
        # 最大不会超过可派遣数量
        vehicle_count = cache.rhodes_island.vehicles[vehicle_id][0] - cache.rhodes_island.vehicles[vehicle_id][1]
        if self.send_vehicle_dict[vehicle_id] > vehicle_count:
            self.send_vehicle_dict[vehicle_id] = vehicle_count

    def reduce_this_vehicle(self, vehicle_id: int):
        """
        减少一辆载具
        Keyword arguments:
        vehicle_id -- 载具id
        """
        if vehicle_id in self.send_vehicle_dict:
            self.send_vehicle_dict[vehicle_id] -= 1
            if self.send_vehicle_dict[vehicle_id] <= 0:
                self.send_vehicle_dict.pop(vehicle_id)

    def send_commision(self, commision_id: int):
        """
        派遣委托
        Keyword arguments:
        commision_id -- 委托编号
        """

        commision_data = game_config.config_commission[commision_id]
        commision_people = commision_data.people
        if len(self.send_npc_list) < commision_people:
            return

        # 结算队长
        if self.lead_chara_id:
            lead_character_data = cache.character_data[self.lead_chara_id]
            # 将队长的id调为列表的第一位
            self.send_npc_list.remove(self.lead_chara_id)
            self.send_npc_list.insert(0, self.lead_chara_id)
            # 二段行为
            lead_character_data.second_behavior["start_field_commission_as_leader"] = 1
            talk.must_show_talk_check(self.lead_chara_id)

        # 初步预估时间
        commision_time = int(commision_data.time)
        new_time = game_time.get_sub_date(day=commision_time)

        # 添加到进行中的委托
        cache.rhodes_island.ongoing_field_commissions[commision_id] = [self.send_npc_list, new_time, []]
        # 消耗资源
        get_commission_demand_and_reward(commision_id, self.send_npc_list, False, True)
        # 遍历派遣人员，设为派遣状态，并离线
        from Script.Settle import default
        for character_id in self.send_npc_list:
            cache.character_data[character_id].sp_flag.field_commission = commision_id
            default.handle_chara_off_line(character_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)
        # 结算派遣的载具
        now_vehicle_list = []
        for vehicle_id in self.send_vehicle_dict:
            cache.rhodes_island.vehicles[vehicle_id][1] += self.send_vehicle_dict[vehicle_id]
            for i in range(self.send_vehicle_dict[vehicle_id]):
                now_vehicle_list.append(vehicle_id)
        cache.rhodes_island.ongoing_field_commissions[commision_id][2] = now_vehicle_list
        # 结算速度对时间的影响
        min_speed = 9
        for vehicle_id in now_vehicle_list:
            vehicle_speed = game_config.config_vehicle[vehicle_id].speed
            min_speed = min(min_speed, vehicle_speed)
        # 如果有实际速度加成，则减少时间
        if min_speed > 1:
            commision_time_by_min = commision_time * 1440
            # 每点速度则将总时间乘以0.9
            commision_time_by_min = int(commision_time_by_min * (0.9 ** min_speed))
            new_time_by_speed = game_time.get_sub_date(minute=commision_time_by_min)
            new_day = round(commision_time_by_min / 1440, 1)
            # 重新设置时间
            cache.rhodes_island.ongoing_field_commissions[commision_id][1] = new_time_by_speed
        # 如果没有实际速度加成，则不减少时间
        else:
            new_time_by_speed = new_time
            new_day = commision_time

        # 绘制委托信息
        draw_text = ""
        draw_text += _("\n\n已派遣 ")
        for character_id in self.send_npc_list:
            character_data = cache.character_data[character_id]
            character_name = character_data.name
            draw_text += f"{character_name} "
        draw_text += _("执行委托：")
        commision_name = commision_data.name
        draw_text += commision_name
        draw_text += _("，耗时：")
        draw_text += str(new_day)
        draw_text += _("天，将在 ")
        new_time_text = game_time.get_date_until_day(new_time_by_speed)
        draw_text += new_time_text
        draw_text += _(" 返回\n\n")
        info_draw = draw.WaitDraw()
        info_draw.text = draw_text
        info_draw.style = "gold_enrod"
        info_draw.width = window_width
        info_draw.draw()

        # 清空派遣人员与载具
        self.send_npc_list = []
        self.send_vehicle_dict = {}


    def adjust_send_vehicle(self, commision_capacity_int: int):
        """
        调整派遣载具
        Keyword arguments:
        commision_capacity_int -- 需要的载具运量
        """

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制可派遣载具
            info_draw_2 = draw.NormalDraw()
            info_draw_2.text = _("\n可派遣载具：\n\n")
            info_draw_2.width = self.width
            info_draw_2.draw()

            for vehicle_cid in cache.rhodes_island.vehicles:
                # 如果没有可以派遣的载具，则不绘制
                vehicle_count = cache.rhodes_island.vehicles[vehicle_cid][0] - cache.rhodes_island.vehicles[vehicle_cid][1]
                if vehicle_count <= 0:
                    continue
                vehicle_data = game_config.config_vehicle[vehicle_cid]
                vehicle_speed = str(vehicle_data.speed)
                vehicle_capacity = str(vehicle_data.capacity)
                vehicle_special = vehicle_data.special
                now_choice_count = 0
                if vehicle_cid in self.send_vehicle_dict:
                    now_choice_count = self.send_vehicle_dict[vehicle_cid]

                draw_text = _("[{0}] {1} 当前选择/可选择：{2}/{3} 速度：{4} 运载量：{5} 特殊效果：{6}\n").format(str(vehicle_cid).rjust(2,'0'), vehicle_data.name, now_choice_count, vehicle_count, vehicle_speed, vehicle_capacity, vehicle_special)
                info_draw = draw.NormalDraw()
                info_draw.text = draw_text
                info_draw.width = self.width
                info_draw.draw()

                # 增加一辆
                button_draw = draw.CenterButton(
                    _("[增加一辆]"),
                    f"\n{vehicle_cid}+1",
                    self.width / 6,
                    cmd_func=self.add_this_vehicle,
                    args=vehicle_cid,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 减少一辆
                button_draw = draw.CenterButton(
                    _("[减少一辆]"),
                    f"\n{vehicle_cid}-1",
                    self.width / 6,
                    cmd_func=self.reduce_this_vehicle,
                    args=vehicle_cid,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                line_feed.draw()

            now_capacity = 0 # 当前运载量
            now_speed = 99 # 当前速度
            now_effect = [] # 当前效果

            # 遍历已选择的载具
            for vehicle_id in self.send_vehicle_dict:
                vehicle_data = game_config.config_vehicle[vehicle_id]
                now_capacity += vehicle_data.capacity * self.send_vehicle_dict[vehicle_id]
                now_speed = min(now_speed, vehicle_data.speed)
                if vehicle_data.special != "无" and vehicle_data.special not in now_effect:
                    now_effect.append(vehicle_data.special)
            if now_speed == 99:
                now_speed = 1

            # 遍历效果，输出效果文本
            effect_text = ""
            for effect in now_effect:
                effect_text += f"{effect} "

            # 绘制当前载具的总信息
            info_draw = draw.NormalDraw()
            info_draw_text = _("\n")
            info_draw_text += _("当前总运载量/需要运载量：{0}/{1}\n").format(now_capacity, commision_capacity_int)
            info_draw_text += _("当前速度（取决于所有载具中最慢的，能够减少委托时间）：{0}\n").format(now_speed)
            info_draw_text += _("其他效果（未实装）：{0}\n").format(effect_text)
            info_draw.text = info_draw_text
            info_draw.width = self.width
            info_draw.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
