from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from Script.Design import attr_calculation, handle_premise, map_handle
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

import random

from Script.UI.Panel import achievement_panel

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

def show_endure_ejaculation_panel():
    """
    进行是否忍住射精的判断
    return
    bool -- 是否忍住 True为忍住 False为射出
    """
    character_data: game_type.Character = cache.character_data[0]
    now_lv = character_data.ability[30]
    now_count = character_data.h_state.endure_not_shot_count

    # 判断忍耐几率
    if now_count <= now_lv:
        now_rate = 100
        endure_text = _("必定忍住")
    else:
        # 超出的次数
        over_count = now_count - now_lv
        # 下降的动态几率
        down_rate = 50 - now_lv * 5
        # 当前忍耐几率
        now_rate = 100 - over_count * down_rate
        now_rate = max(0, now_rate)
        if now_rate >= 75:
            endure_text = _("高")
        elif now_rate >= 50:
            endure_text = _("中")
        elif now_rate >= 25:
            endure_text = _("低")
        else:
            endure_text = _("无")

    return_flag = judge_endure_ejaculation(now_rate)

    while 1:
        line = draw.LineDraw("-", window_width)
        line.draw()
        line_feed.draw()
        return_list = []

        # 询问是否要忍住
        now_draw = draw.NormalDraw()
        now_draw_text = _("要射精了，是否要忍住射精，忍耐次数越多则射精量越多（当前已忍住{0}次，忍耐几率 {1}）\n").format(now_count, endure_text)
        now_draw.text = now_draw_text
        now_draw.width = window_width
        now_draw.draw()
        line_feed.draw()

        # 选择是否忍住
        yes_draw = draw.CenterButton(_("[忍住]"), _("忍住"), int(window_width / 3))
        yes_draw.draw()
        return_list.append(yes_draw.return_text)
        no_draw = draw.CenterButton(_("[射出]"), _("射出"), int(window_width / 3))
        no_draw.draw()
        return_list.append(no_draw.return_text)

        line_feed.draw()

        yrn = flow_handle.askfor_all(return_list)
        if yrn in return_list:
            # 如果是射出，则返回False
            if yrn == _("射出"):
                return_flag = False
            break

    # 忍住的结算
    if return_flag:
        character_data.h_state.endure_not_shot_count += 1
        character_data.eja_point = 0
        endure_text = _("\n{0}忍住了射精\n").format(character_data.name)
        now_draw = draw.NormalDraw()
        now_draw.text = endure_text
        now_draw.width = window_width
        now_draw.draw()

    line.draw()

    return return_flag


def judge_endure_ejaculation(endure_rate: int) -> bool:
    """
    计算是否忍住射精
    Keyword arguments:
    endure_rate -- 忍住射精的几率
    """
    if random.randint(1, 100) <= endure_rate:
        return True
    else:
        return False


def common_ejaculation():
    """
    通用射精结算，进行一次射精，并返回射精文本和射精量
    return
    semen_text 射精文本
    semen_count 射精量
    """
    character_data: game_type.Character = cache.character_data[0]

    # 乘以一个随机数补正
    random_weight = random.uniform(0.8, 1.2)

    # 额外调整的文本提示
    extra_text = ""

    # 如果已经没有精液了，则不射精
    if handle_premise.handle_pl_semen_le_2(0):
        return _("只流出了些许前列腺液，已经射不出精液了"),0
    else:
        # 基础射精值，小中多射精区分
        if character_data.second_behavior["p_orgasm_strong"] == 1:
            semen_count = int(50 * random_weight) * (character_data.h_state.endure_not_shot_count + 1)
            semen_text = _("超大量射精，射出了")
        elif character_data.second_behavior["p_orgasm_normal"] == 1:
            semen_count = int(20 * random_weight) * (character_data.h_state.endure_not_shot_count + 1)
            semen_text = _("大量射精，射出了")
        else:
            semen_count = int(10 * random_weight)
            semen_text = _("射精，射出了")

        # 如果有交互对象，则根据交互对象的榨精能力等级来调整射精量
        if character_data.target_character_id > 0:
            target_data: game_type.Character = cache.character_data[character_data.target_character_id]
            squeeze_adjust = attr_calculation.get_ability_adjust(target_data.ability[77])
            # 根据榨精能力等级调整射精量
            semen_count *= squeeze_adjust
            if squeeze_adjust > 1:
                extra_text += _("（{0}榨精+）").format(target_data.name)

        # 如果使用了精液精力剂，则本次射精量翻倍
        if character_data.h_state.used_semen_energy_agent:
            semen_count *= 2
            character_data.h_state.used_semen_energy_agent = False
            extra_text += _("（精力剂+）")

        # 如果施加了香薰疗愈-射精状态，则射精量翻倍
        if handle_premise.handle_aromatherapy_flag_7(0):
            semen_count *= 2
            extra_text += ("（{0}+）").format(game_config.config_aromatherapy_recipes[7].name)

        # 如果当前的临时精液量大于等于最大精液量，则射精量翻倍
        if handle_premise.handle_pl_semen_tmp_ge_max(0):
            semen_count *= 2
            extra_text += _("（积攒精液+）")

        # 如果当前是浓厚精液的话，则射精量翻倍
        if handle_premise.handle_self_semen_thick_1(0):
            semen_count *= 2
            extra_text += _("（浓厚精液+）")

        # 射精量不高于剩余精液值
        semen_count = min(int(semen_count), character_data.semen_point + character_data.tem_extra_semen_point)
        # 组合射精文本
        semen_text += str(semen_count) + _("ml精液") + extra_text

        character_data.h_state.orgasm_level[3] += 1 # 更新射精次数
        character_data.h_state.just_shoot = 1 # 更新刚射精状态
        character_data.dirty.penis_dirty_dict["semen"] = True # 更新阴茎精液污浊状态
        cache.rhodes_island.total_semen_count += semen_count # 更新总精液量
        character_data.h_state.endure_not_shot_count = 0 # 清零忍住不射次数

        # # 更新精液值，目前弃用
        # if semen_count > character_data.semen_point:
        #     semen_count = character_data.semen_point

        # 优先扣除临时额外精液值，不够的再扣除基础精液值
        if character_data.tem_extra_semen_point > semen_count:
            character_data.tem_extra_semen_point -= semen_count
        else:
            semen_count -= character_data.tem_extra_semen_point
            character_data.tem_extra_semen_point = 0
            character_data.semen_point -= semen_count
        character_data.semen_point = max(0, character_data.semen_point)

        return semen_text,semen_count


def update_semen_dirty(character_id: int, part_cid: int, part_type: int, semen_count: int, update_shoot_position_flag: bool = True):
    """
    更新部位的被射精污浊数据
    Keyword arguments:
    character_id -- 角色id
    part_cid -- 部位cid
    part_type -- 部位类型，0为身体，1为穿着服装，2为浴场衣柜，3为宿舍衣柜
    semen_count -- 精液量
    update_shoot_position_flag -- 是否更新射精部位
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 判断部位类型
    if part_type == 0:
        # 检查是否有该部位
        if part_cid == 12 and not character_data.talent[113]:
            return
        elif part_cid == 13 and not character_data.talent[112]:
            return
        elif part_cid == 14 and not character_data.talent[111]:
            return
        # 更新身体部位被射精污浊数据
        now_semen_data = character_data.dirty.body_semen[part_cid]
    elif part_type == 1:
        # 检查该部位是否有服装
        if not len(character_data.cloth.cloth_wear[part_cid]):
            return
        # 更新服装部位被射精污浊数据
        now_semen_data = character_data.dirty.cloth_semen[part_cid]
    elif part_type == 2:
        # 检查该部位是否有服装
        if not len(character_data.cloth.cloth_locker_in_shower[part_cid]):
            return
        now_semen_data = character_data.dirty.cloth_locker_semen[part_cid]
    elif part_type == 3:
        # 检查该部位是否有服装
        if not len(character_data.cloth.cloth_locker_in_dormitory[part_cid]):
            return
        now_semen_data = character_data.dirty.cloth_locker_semen[part_cid]

    # 进行统一结算
    # 该部位增加当前精液量
    now_semen_data[1] += semen_count
    now_semen_data[1] = max(now_semen_data[1], 0)
    # 在精液量为正的情况下
    if semen_count > 0:
        # 该部位增加总精液量
        now_semen_data[3] += semen_count
    # 该部位更新精液等级
    now_semen_data[2] = attr_calculation.get_semen_now_level(now_semen_data[1], part_cid, part_type)
    # 记录射精部位
    if update_shoot_position_flag:
        if part_type == 0:
            character_data.h_state.shoot_position_body = part_cid
            # 无意识中则记录部位精液
            if handle_premise.handle_unconscious_flag_ge_1(character_id) and part_cid not in character_data.dirty.body_semen_in_unconscious:
                character_data.dirty.body_semen_in_unconscious.append(part_cid)
        else:
            character_data.h_state.shoot_position_cloth = part_cid
            if handle_premise.handle_unconscious_flag_ge_1(character_id) and part_cid not in character_data.dirty.cloth_semen_in_unconscious:
                character_data.dirty.cloth_semen_in_unconscious.append(part_cid)
        # 重置部位插入
        if semen_count > 0:
            pl_character_data.h_state.insert_position = -1
            character_data.h_state.insert_position = -1
    # A部位射精时如果已经持有灌肠肛塞道具，且设置已开启，则结算精液灌肠
    if (
        part_type == 0 and
        part_cid == 8 and
        cache.all_system_setting.base_setting[8] and
        handle_premise.handle_have_clyster_tools(0)
        ):
        character_data.dirty.a_clean = 3
        if now_semen_data[2] <= 3:
            character_data.dirty.enema_capacity = 1
        elif now_semen_data[2] <= 5:
            character_data.dirty.enema_capacity = 2
        elif now_semen_data[2] == 6:
            character_data.dirty.enema_capacity = 3
        elif now_semen_data[2] == 7:
            character_data.dirty.enema_capacity = 4
        else:
            character_data.dirty.enema_capacity = 5
        # 如果自己的身体插入部位是A，则清零
        if character_data.h_state.insert_position == 8:
            character_data.h_state.insert_position = -1
        # 如果此时在群交中，且阴茎状态为肛交，则清零阴茎状态
        if handle_premise.handle_group_sex_mode_on(0):
            now_template_data = pl_character_data.h_state.group_sex_body_template_dict["A"]
            behavior_id = now_template_data[0]["penis"][1]
            # 如果没有阴茎状态，则不处理
            if behavior_id == -1:
                return
            behavior_data = game_config.config_behavior[behavior_id]
            # 如果为肛交，则清零阴茎状态
            if "A" in behavior_data.tag:
                now_template_data[0]["penis"] = [-1, -1]
    # print(f"debug update_semen_dirty name = {character_data.name}, part_cid = {part_cid}, part_type = {part_type}, semen_count = {semen_count}")


def calculate_semen_flow(character_id: int, part_cid: int, part_type: int, semen_count: int):
    """
    计算精液流动
    Keyword arguments:
    character_id -- 角色id
    part_cid -- 部位cid
    part_type -- 部位类型，0为身体，1为穿着服装
    semen_count -- 精液量
    """
    if character_id != 0:
        character_data: game_type.Character = cache.character_data[character_id]
        # 创建精液流通情况字典
        all_flow_dict = {}
        all_flow_dict["source"] = {"type": part_type, "id": part_cid}
        all_flow_dict["targets"] = []

        # 判断部位类型，0为身体部位，1为服装部位
        if part_type == 0:
            # 判断是否满溢
            max_volume = game_config.config_body_part[part_cid].max_volume
            # 满溢时使用满溢流动表，且仅计算额外溢出来的部分
            if character_data.dirty.body_semen[part_cid][1] > max_volume:
                flow_list = game_config.config_body_part_full_flow[part_cid]
                semen_count = character_data.dirty.body_semen[part_cid][1] - max_volume
            # 未满溢时使用正常流动表
            else:
                flow_list = game_config.config_body_part_normal_flow[part_cid]
        elif part_type == 1:
            # 判断是否满溢
            max_volume = game_config.config_clothing_type[part_cid].max_volume
            # 满溢时使用满溢流动表，且仅计算额外溢出来的部分
            if character_data.dirty.cloth_semen[part_cid][1] > max_volume:
                flow_list = game_config.config_cloth_part_full_flow[part_cid]
                semen_count = character_data.dirty.cloth_semen[part_cid][1] - max_volume
            # 未满溢时使用正常流动表
            else:
                flow_list = game_config.config_cloth_part_normal_flow[part_cid]

        # 遍历流动表，计算应该向各部位流动多少，添加到精液流通情况字典中
        for flow_str in flow_list:
            # 获取流动类型，部位cid，流动比例
            flow_type = flow_str[0]
            flow_cid = int(flow_str[1:].split("-")[0])
            flow_rate = int(flow_str[1:].split("-")[1])
            # 创建流动情况字典
            now_flow_dict = {}
            # 判断流动类型，0为身体部位，1为服装部位，2为环境滴落
            if flow_type == "B":
                now_flow_dict["type"] = 0
            elif flow_type == "C":
                now_flow_dict["type"] = 1
            elif flow_type == "E":
                now_flow_dict["type"] = 2
            # 添加流动目标部位cid和流动量
            now_flow_dict["id"] = flow_cid
            now_flow_dict["remaining_volume"] = max(1, int(semen_count * flow_rate / 100))
            # 添加到精液流通情况字典中
            all_flow_dict["targets"].append(now_flow_dict)

        # 添加到目标角色的精液流通情况列表中
        character_data.dirty.semen_flow.append(all_flow_dict)
        # print(f"debug calculate_semen_flow name = {character_data.name},all_flow_dict = {all_flow_dict}")


def ejaculation_flow(part_cid: int, part_type: int, target_character_id: int = 0, draw_flag: bool = True):
    """
    射精流程的总函数
    Keyword arguments:
    part_cid -- 部位cid
    part_type -- 部位类型，0为身体，1为穿着服装，2为浴场衣柜，3为宿舍衣柜
    target_character_id -- 目标角色id
    """
    character_data: game_type.Character = cache.character_data[0]
    # 如果没有赋值目标角色id，则默认为当前目标角色
    if target_character_id == 0:
        target_character_id = character_data.target_character_id
    target_data: game_type.Character = cache.character_data[target_character_id]

    semen_text, semen_count = common_ejaculation()

    if semen_count > 0:
        # 记录射精量
        character_data.h_state.shoot_semen_amount += semen_count
        # 群交中
        if handle_premise.handle_group_sex_mode_on(0):
            # 成就记录
            cache.achievement.group_sex_record.setdefault(1, [])
            if target_character_id not in cache.achievement.group_sex_record[1]:
                cache.achievement.group_sex_record[1].append(target_character_id)
        # 隐奸状态下
        elif handle_premise.handle_hidden_sex_mode_ge_1(0):
            # 成就统计
            cache.achievement.hidden_sex_record.setdefault(3, 0)
            cache.achievement.hidden_sex_record[3] += 1
        # 露出状态下
        elif handle_premise.handle_exhibitionism_sex_mode_ge_1(0):
            # 成就统计
            cache.achievement.exhibitionism_sex_record.setdefault(3, 0)
            cache.achievement.exhibitionism_sex_record[3] += 1
        # 睡奸状态下
        elif handle_premise.handle_t_unconscious_flag_1(0):
            # 成就统计
            cache.achievement.sleep_sex_record.setdefault(2, 0)
            cache.achievement.sleep_sex_record[2] += 1
        # 正常射精时
        if character_data.h_state.body_item[13][1] == False:
            # 在有目标对象时
            if target_character_id > 0:
                cache.shoot_position = part_cid
                # 更新被射精污浊数据
                update_semen_dirty(target_character_id, part_cid, part_type, semen_count)
                # 计算精液流动
                if part_type in [0, 1]:
                    calculate_semen_flow(target_character_id, part_cid, part_type, semen_count)
                # 更新怀孕概率
                from Script.Design import pregnancy
                pregnancy.get_fertilization_rate(target_character_id)
                # 只有在交互对象正确的时候才会显示对方的名字和部位
                if part_type == 0:
                    part_name = game_config.config_body_part[part_cid].name
                    now_text = _("在{0}的{1}{2}").format(target_data.name, part_name, semen_text)
                    # 更新无意识妊娠flag
                    if part_cid in [6, 7] and target_data.sp_flag.unconscious_h == 0:
                        target_data.pregnancy.unconscious_fertilization = False
                elif part_type in [1, 2, 3]:
                    cloth_text = game_config.config_clothing_type[part_cid].name
                    now_text = _("在{0}的{1}{2}").format(target_data.name, cloth_text, semen_text)
            # 否则只显示自己的名字
            else:
                now_text = character_data.name + semen_text
        # 戴着避孕套射精时
        else:
            cache.shoot_position = 0
            # 将射精量转化为避孕套中的精液量
            character_data.h_state.condom_count[0] += 1
            character_data.h_state.condom_count[1] += semen_count
            # 去掉避孕套状态
            character_data.h_state.body_item[13][1] = False
            # 获取射精文本
            now_text = _("在避孕套里") + semen_text

    else:
        # 没有射精时
        now_text = character_data.name + semen_text

    # 绘制射精文本
    if draw_flag:
        line_feed.draw()
        line = draw.LineDraw("-", window_width)
        line.draw()
        line_feed.draw()
        now_draw = draw.WaitDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.style = 'semen'
        now_draw.draw()
        line_feed.draw()
        line_feed.draw()

    # 结算成就
    achievement_panel.achievement_flow(_("射精"))

class Ejaculation_Panel:
    """
    用于显示射精界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("身体")
        """ 当前绘制的射精页面 """

    def draw(self):
        """绘制对象"""
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        # 如果当前交互对象不是NPC的话，则跳过部位选择
        if character_data.target_character_id == 0:
            self.shoot_here(6, 0)
        # 群交模式下手动选择对象与部位
        elif cache.group_sex_mode:
            self.draw_choose_target_chara_in_group_sex()
            self.draw_choose_part()
        # 如果没有选择射精部位，则直接在当前阴茎位置射精
        elif not cache.all_system_setting.base_setting[3]:
            now_position = target_data.h_state.insert_position
            if now_position != -1:
                # 身体
                if now_position < 20:
                    self.shoot_here(now_position, 0)
                # 衣服
                else:
                    self.shoot_here(now_position - 20, 1)
            # 如果没有插入位置，则也手动选择射精部位
            else:
                self.draw_choose_part()
        # 手动选择射精部位
        else:
            self.draw_choose_part()

    def part_can_choose(self, body_part_cid: int):
        """判断该部位是否可以绘制"""
        from Script.Design import clothing

        character_data: game_type.Character = cache.character_data[0]

        # 不插在对应部位，则无法射在对应部位
        if body_part_cid == 6 and not (handle_premise.handle_penis_in_t_vagina(0) or handle_premise.handle_penis_in_t_womb(0)):
            return False
        elif body_part_cid == 7 and not handle_premise.handle_penis_in_t_womb(0):
            return False
        elif body_part_cid == 8 and not handle_premise.handle_penis_in_t_anal(0):
            return False
        elif body_part_cid == 9 and not handle_premise.handle_penis_in_t_nrethral(0):
            return False
        elif body_part_cid == 15 and not handle_premise.handle_last_cmd_deep_throat(0):
            return False

        # 获取没有穿衣服的部位列表
        no_cloth_body_list = clothing.get_exposed_body_parts(character_data.target_character_id, ignore_panties=True)

        # 如果该部位没有穿衣服，则可以
        if body_part_cid in no_cloth_body_list:
            return True
        return False

    def draw_choose_target_chara_in_group_sex(self):
        """绘制选择射精对象"""

        title_name = _("选择射精对象")
        title_draw = draw.TitleLineDraw(title_name, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            character_data: game_type.Character = cache.character_data[0]
            scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]

            # 当前场景的角色列表
            for chara_id in scene_data.character_list:
                # 不显示自己
                if chara_id == 0:
                    continue
                now_character_data: game_type.Character = cache.character_data[chara_id]
                chara_name = now_character_data.name
                chara_adv = now_character_data.adv
                draw_text = f"[{chara_adv}]{chara_name}"
                name_draw = draw.CenterButton(
                    draw_text, chara_name, (len(draw_text) + 1) * 3, cmd_func=self.change_shoot_target, args=(chara_id)
                )
                name_draw.draw()
                return_list.append(name_draw.return_text)

            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn in return_list:
                break

    def draw_choose_part(self):
        """绘制选择射精部位"""

        title_name = _("选择射精部位")
        title_draw = draw.TitleLineDraw(title_name, self.width)
        while 1:

            character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[character_data.target_character_id]

            return_list = []
            title_draw.draw()

            # 绘制身体部位按钮
            body_count = 0
            for body_part_cid in game_config.config_body_part:
                part_name = game_config.config_body_part[body_part_cid].name
                draw_text = f"[{body_part_cid}]{part_name}"
                # print("debug draw_text = ",draw_text)
                body_count += 1
                show_flag = self.part_can_choose(body_part_cid)
                if show_flag:
                    name_draw = draw.CenterButton(
                        draw_text, '\n' + part_name, (len(draw_text) + 1) * 2, cmd_func=self.shoot_here, args=(body_part_cid, 0)
                    )
                    name_draw.draw()
                    return_list.append(name_draw.return_text)
                    if body_count > 0 and body_count % 8 == 0:
                        line_feed.draw()

            line_feed.draw()

            # 绘制服装部位按钮
            cloth_count = 0
            for clothing_type in game_config.config_clothing_type:
                cloth_name = game_config.config_clothing_type[clothing_type].name
                draw_text = f"[{clothing_type}]{cloth_name}"
                cloth_count += 1
                show_flag = len(target_data.cloth.cloth_wear[clothing_type])
                if show_flag:
                    name_draw = draw.CenterButton(
                        draw_text, cloth_name, (len(draw_text) + 1) * 2, cmd_func=self.shoot_here, args=(clothing_type, 1)
                    )
                    name_draw.draw()
                    return_list.append(name_draw.return_text)
                    if cloth_count > 0 and cloth_count % 8 == 0:
                        line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn not in [_('身体'), _('服装')]:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_shoot_target(self, target_character_id: int):
        """更改射精目标"""
        character_data: game_type.Character = cache.character_data[0]
        character_data.target_character_id = target_character_id

    def shoot_here(self, part_cid: int, part_type: int):
        """结算射精"""
        py_cmd.clr_cmd()
        # 更新阴茎插入部位
        character_data: game_type.Character = cache.character_data[0]
        target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if part_type == 0:
            character_data.h_state.insert_position = part_cid
            target_character_data.h_state.insert_position = part_cid
            # 如果是深喉插入状态，则将部位改为食道射精
            if handle_premise.handle_last_cmd_deep_throat(0):
                part_cid = 15
        else:
            character_data.h_state.insert_position = part_cid + 20
            target_character_data.h_state.insert_position = part_cid + 20
        ejaculation_flow(part_cid, part_type)
