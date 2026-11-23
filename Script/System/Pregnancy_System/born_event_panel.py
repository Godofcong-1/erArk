from typing import Tuple, List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import normal_config
from Script.Design import character_handle, handle_premise, talk, map_handle
import random

from Script.UI.Panel import achievement_panel

panel_info_data = {}

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """


def move_to_inpatient_department_for_born(mother_character_id: int) -> list:
    """
    生育/破壳事件开始时把母亲与玩家瞬移到医疗部住院区（胎生与卵生共用，幂等）
    \n母亲已在住院区则以其所在病房为目标（玩家前去会合），否则随机选一间住院区场景并把母亲移入；
    \n事件在玩家睡眠结算内触发，故直接改场景数据而不走寻路与游戏流程推进；事件结束后两人留在住院区
    Keyword arguments:
    mother_character_id -- 母亲角色id
    Return arguments:
    list -- 事件所在的住院区场景路径
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    mom_character_data: game_type.Character = cache.character_data[mother_character_id]
    mom_scene_str = map_handle.get_map_system_path_str_for_list(mom_character_data.position)
    if "Inpatient_Department" in cache.scene_data[mom_scene_str].scene_tag:
        target_scene_path = list(mom_character_data.position)
    else:
        target_scene_path = map_handle.get_map_system_path_for_str(random.choice(constant.place_data["Inpatient_Department"]))
        map_handle.character_move_scene(mom_character_data.position, target_scene_path, mother_character_id)
    if pl_character_data.position != target_scene_path:
        map_handle.character_move_scene(pl_character_data.position, target_scene_path, 0)
    return target_scene_path


def get_born_doctor_id(mother_character_id: int) -> int:
    """
    选出生产 / 破壳事件里接生的人
    Keyword arguments:
    mother_character_id -- 母亲（产妇）的角色id
    Return arguments:
    int -- 接生者的角色id；岛上除产妇外没有别的干员时为 0
    功能: 凯尔希在岛上且不是产妇时由她接生；否则随机选一名医疗干员；再没有就随机选任何一名干员。
          各步都不会选到产妇本人（她自己是医疗干员、或岛上只有她一名干员时，原先会选中她给自己接生）
    """
    doctor_id_list = []
    other_id_list = []
    dr_k_id = 0
    for character_id in cache.npc_id_got:
        if character_id == mother_character_id or character_id not in cache.character_data:
            continue
        character_data: game_type.Character = cache.character_data[character_id]
        other_id_list.append(character_id)
        if character_data.profession == 3:
            doctor_id_list.append(character_id)
        if character_data.name == _("凯尔希"):
            dr_k_id = character_id
    # 凯尔希优先（产妇是凯尔希时她已被排除，自然落到下面的医疗干员）
    if dr_k_id:
        return dr_k_id
    if doctor_id_list:
        return random.choice(doctor_id_list)
    # 没有医疗干员时随机选取任何一位别的干员来接生
    if other_id_list:
        return random.choice(other_id_list)
    return 0


class Born_Panel:
    """
    生孩子事件的面板对象（胎生生产与卵生破壳共用）
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, mother_character_id: int, egg_mode: bool = False, egg_id_list: list = None):
        """
        初始化绘制对象
        Keyword arguments:
        mother_character_id -- 母亲角色id
        egg_mode -- 是否为卵生破壳模式
        egg_id_list -- 卵生破壳模式下本次孵化的卵编号列表（带壳卵生每晚一枚；无壳卵生同批受精卵一同孵化、逐个取名）
        """
        self.width: int = window_width
        """ 绘制的最大宽度 """
        self.mother_character_id: int = mother_character_id
        """ 母亲角色id """
        self.egg_mode: bool = egg_mode
        """ 是否为卵生破壳模式 """
        self.egg_id_list: list = list(egg_id_list) if egg_id_list else []
        """ 卵生破壳模式下本次孵化的卵编号列表 """
        mom_eggs = cache.character_data[mother_character_id].pregnancy.eggs
        self.soft_egg_mode: bool = egg_mode and any(mom_eggs.get(egg_id, {}).get("soft", False) for egg_id in self.egg_id_list)
        """ 是否为无壳卵孵化模式（文案与二段行为与带壳破壳区分） """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def _draw_born_event_content(self) -> None:
        """生育事件主逻辑绘制。"""
        from Script.Design import second_behavior

        pl_character_data: game_type.Character = cache.character_data[0]
        mom_character_data: game_type.Character = cache.character_data[self.mother_character_id]

        # 事件舞台在医疗部住院区：母亲与玩家先移动到位（胎生兜底 AI 尚未传送的情况，卵生母亲无临盆状态需在此移动）
        move_to_inpatient_department_for_born(self.mother_character_id)

        # 选出接生的人：岛上除了产妇再没有别的干员时，文本里写成医疗部的产科干员
        doctor_id = get_born_doctor_id(self.mother_character_id)
        if doctor_id:
            doctor_name = cache.character_data[doctor_id].name
        else:
            doctor_name = _("医疗部的产科干员")

        # 最外层的大循环
        while 1:
            # 内循环1：等待按键
            while 1:
                line = draw.LineDraw("-", window_width)
                line.draw()
                return_list = []

                if self.soft_egg_mode:
                    second_behavior.character_get_second_behavior(self.mother_character_id, "soft_egg_born")
                elif self.egg_mode:
                    second_behavior.character_get_second_behavior(self.mother_character_id, "egg_born")
                else:
                    second_behavior.character_get_second_behavior(self.mother_character_id, "born")
                talk.must_show_talk_check(self.mother_character_id)
                info_draw = draw.WaitDraw()
                info_draw.width = self.width
                if self.soft_egg_mode:
                    if len(self.egg_id_list) >= 2:
                        info_draw.text = _("\n 得知了{0}在育儿室悉心孵化的{1}颗受精卵粒即将孵化的消息后，你第一时间赶到了医疗部住院区，看着她小心翼翼地捧着那团凝胶里微微搏动的卵粒，静候新生命的到来\n").format(mom_character_data.name, len(self.egg_id_list))
                    else:
                        info_draw.text = _("\n 得知了{0}在育儿室悉心孵化的受精卵粒即将孵化的消息后，你第一时间赶到了医疗部住院区，看着她小心翼翼地捧着那团凝胶里微微搏动的卵粒，静候新生命的到来\n").format(mom_character_data.name)
                elif self.egg_mode:
                    info_draw.text = _("\n 得知了{0}在育儿室悉心孵化的卵即将破壳的消息后，你第一时间赶到了医疗部住院区，看着她小心翼翼地捧着微微颤动的卵，静候新生命的到来\n").format(mom_character_data.name)
                else:
                    info_draw.text = _("\n 得知了{0}即将生产的消息后，你第一时间来到了待产室，在短暂的陪伴后，目送着她被推入产房\n").format(mom_character_data.name)
                info_draw.draw()
                line_feed.draw()
                button_text = _("[焦急等待]")
                button_draw = draw.LeftButton(_(button_text), _("\n"), self.width)
                button_draw.draw()
                return_list.append(button_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list:
                    break
            # 本次生产的孩子数：带壳卵生恒为1、无壳卵生为同批到期的卵数；胎生取本次胎数（旧存档/单胎为0或1时按1处理），同卵双胞胎换用专属文案
            born_count = 1
            identical_twins_flag = False
            if self.egg_mode:
                born_count = max(1, len(self.egg_id_list))
            else:
                born_count = max(1, getattr(mom_character_data.pregnancy, "fetus_count", 0))
                identical_twins_flag = bool(getattr(mom_character_data.pregnancy, "identical_twins", False)) and born_count == 2
            # 内循环2：起名字（按孩子数逐个取名）
            child_name_list = []
            while 1:
                if self.soft_egg_mode:
                    if born_count >= 2:
                        info_draw.text = _(" 在{0}的看护下，凝胶里的卵粒一颗颗地胀大、变得透亮，包裹着它们的胶质终于相继化开，{1}个小小的身影先后从凝胶中挣脱出来，此起彼伏地发出了响亮的啼哭\n").format(doctor_name, born_count)
                        info_draw.text += _(" {0}把刚刚脱出凝胶的{1}个婴儿一一擦拭干净抱在怀里，对着你微微一笑，催促你逐个给孩子起名\n").format(mom_character_data.name, born_count)
                    else:
                        info_draw.text = _(" 在{0}的看护下，凝胶里那颗受精的卵粒一点点胀大、变得透亮，包裹着它的胶质终于化开，一个小小的身影从凝胶中挣脱出来，发出了响亮的啼哭\n").format(doctor_name)
                        info_draw.text += _(" {0}把刚刚脱出凝胶的婴儿擦拭干净抱在怀里，对着你微微一笑，催促你给孩子起名\n").format(mom_character_data.name)
                elif self.egg_mode:
                    info_draw.text = _(" 在{0}的看护下，蛋壳上的裂纹越来越多，终于随着一声清脆的破裂声，一个小小的身影从蛋壳中探出头来，发出了响亮的啼哭\n").format(doctor_name)
                    info_draw.text += _(" {0}轻轻抱起了刚刚破壳而出的婴儿，对着你微微一笑，催促你给孩子起名\n").format(mom_character_data.name)
                elif identical_twins_flag:
                    info_draw.text = _(" 经过了漫长的等待之后，随着响亮的哭声，{0}推开产房的门，告诉你{1}生了一对同卵双胞胎女儿，母女平安\n").format(doctor_name, mom_character_data.name)
                    info_draw.text += _(" {0}躺在床上，怀里抱着两个一模一样的婴儿，对着你微微一笑，催促你分别给她们起名\n").format(mom_character_data.name)
                elif born_count >= 2:
                    info_draw.text = _(" 经过了漫长的等待之后，随着此起彼伏的哭声，{0}推开产房的门，告诉你{1}生了{2}个可爱的女儿，母女平安\n").format(doctor_name, mom_character_data.name, born_count)
                    info_draw.text += _(" {0}躺在床上，怀里抱着{1}个婴儿，对着你微微一笑，催促你逐个给孩子起名\n").format(mom_character_data.name, born_count)
                else:
                    info_draw.text = _(" 经过了漫长的等待之后，随着响亮的哭声，{0}推开产房的门，告诉你{1}生了一个可爱的女儿，母女平安\n").format(doctor_name, mom_character_data.name)
                    info_draw.text += _(" {0}躺在床上，怀里抱着婴儿，对着你微微一笑，催促你给孩子起名\n").format(mom_character_data.name)
                info_draw.draw()
                line_feed.draw()

                from Script.Design import character
                for born_index in range(born_count):
                    # 取名询问文案：同卵双胞胎按姐姐/妹妹，多胞胎按序号，单胎沿用原文
                    if identical_twins_flag:
                        ask_text = _(" 你决定给双胞胎中的姐姐取名为——") if born_index == 0 else _(" 你决定给双胞胎中的妹妹取名为——")
                    elif born_count >= 2:
                        ask_text = _(" 你决定给第{0}个女儿取名为——").format(born_index + 1)
                    else:
                        ask_text = _(" 你决定给女儿取名为——")
                    new_name = character.input_name_func(ask_text)

                    # 创建该角色，born_new_character 返回新角色的id
                    new_child_id = character_handle.born_new_character(self.mother_character_id, new_name)
                    child_character_data: game_type.Character = cache.character_data[new_child_id]
                    child_character_data.pregnancy.born_time = cache.game_time
                    child_name_list.append(child_character_data.name)

                    info_draw.text = _("\n孩子的名字叫做{0}，她是{1}的第{2}个孩子，也是{3}的第{4}个孩子，请慢慢养育她长大成人吧\n").format(child_character_data.name, pl_character_data.name, len(pl_character_data.relationship.child_id_list), mom_character_data.name, len(mom_character_data.relationship.child_id_list))
                    info_draw.draw()
                    line_feed.draw()
                    # 胎教转写（Plan 22 四期 §3.27）：母亲的累积值逐个**全额**写给每个新生儿，多胎不平分——
                    # 胎教是对着孕肚做的，双胞胎都听见了；平分会让多胎变成惩罚
                    from Script.System.Education_System import baby_growth_handle

                    prenatal_text = baby_growth_handle.settle_prenatal_to_child(self.mother_character_id, new_child_id)
                    if prenatal_text:
                        info_draw.text = prenatal_text
                        info_draw.draw()
                        line_feed.draw()
                # 多子总结
                if identical_twins_flag:
                    info_draw.text = _("\n{0}生下了一对同卵双胞胎：{1}与{2}\n").format(mom_character_data.name, child_name_list[0], child_name_list[1])
                    info_draw.draw()
                    line_feed.draw()
                elif self.soft_egg_mode and born_count >= 2:
                    info_draw.text = _("\n{0}的{1}颗受精卵粒一同孵化了：{2}\n").format(mom_character_data.name, born_count, "、".join(child_name_list))
                    info_draw.draw()
                    line_feed.draw()
                elif born_count >= 2:
                    info_draw.text = _("\n{0}一次生下了{1}个孩子：{2}\n").format(mom_character_data.name, born_count, "、".join(child_name_list))
                    info_draw.draw()
                    line_feed.draw()
                # 全部孩子都转写完了才清零母亲侧的胎教累积，下一胎从头攒（Plan 22 四期 §3.27）
                from Script.System.Education_System import baby_growth_handle

                baby_growth_handle.clear_prenatal_point(self.mother_character_id)
                break

            # 本次生产是否撑破了产妇的处女膜（仅胎生），用于结尾结算成就
            virgin_birth_flag = False
            if self.egg_mode:
                # 卵生破壳结算：删除本次孵化的全部卵、直接进入育儿与泌乳，不进入产后
                draw_text = "\n※※※※※※※※※\n"
                for egg_id in self.egg_id_list:
                    if egg_id in mom_character_data.pregnancy.eggs:
                        del mom_character_data.pregnancy.eggs[egg_id]
                mom_character_data.talent[24] = 1
                draw_text += _("\n{0}获得了[育儿]\n").format(mom_character_data.name)
                mom_character_data.talent[27] = 1
                draw_text += _("\n{0}获得了[泌乳]\n").format(mom_character_data.name)
                # 根据罩杯大小修改乳汁上限
                for talent_id in [121, 122, 123, 124, 125]:
                    if mom_character_data.talent[talent_id]:
                        mom_character_data.pregnancy.milk_max = 150 + (talent_id - 121) * 40
                        break
                handle_premise.settle_chara_unnormal_flag(self.mother_character_id, 2)
                mom_character_data.experience[86] += 1
                draw_text += _("\n{0}的妊娠经验+1\n").format(mom_character_data.name)
                draw_text += _("\n{0}接下来的行动重心会以照顾{1}为主\n").format(mom_character_data.name, "、".join(child_name_list) if len(child_name_list) else child_character_data.name)
                draw_text += "\n※※※※※※※※※\n"
            else:
                second_behavior.character_get_second_behavior(self.mother_character_id, "postpartum")
                talk.must_show_talk_check(self.mother_character_id)
                draw_text = "\n※※※※※※※※※\n"
                draw_text += _("\n{0}的生产结束了，但她仍需要在住院部休息几天\n").format(mom_character_data.name)
                mom_character_data.talent[22] = 0
                mom_character_data.talent[23] = 1
                handle_premise.settle_chara_unnormal_flag(self.mother_character_id, 2)
                draw_text += _("\n{0}从[临盆]转变为[产后]\n").format(mom_character_data.name)
                mom_character_data.talent[26] = 0
                draw_text += _("\n{0}失去了[孕肚]\n").format(mom_character_data.name)
                # 仍是阴道处女（如用极细针筒注射器注入精液受孕）时，胎儿经过产道会撑破处女膜
                # 只清素质、不写部位交初体验记录：这不是性行为，履历里不应出现夺走处女的对象与体位
                if mom_character_data.talent[0]:
                    mom_character_data.talent[0] = 0
                    virgin_birth_flag = True
                    draw_text += _("\n{0}从未被插入过的小穴里，那层处女膜在生产时被娩出的胎儿撑破了\n").format(mom_character_data.name)
                    draw_text += _("\n{0}失去了[阴道处女]\n").format(mom_character_data.name)
                # 生产完成，重置妊娠加速药的累计加速天数、本次胎数与同卵双胞胎标记
                mom_character_data.pregnancy.acceleration_days = 0.0
                mom_character_data.pregnancy.fetus_count = 0
                mom_character_data.pregnancy.identical_twins = False
                mom_character_data.experience[65] += 10
                mom_character_data.experience[68] += 10
                mom_character_data.experience[86] += 1
                draw_text += _("\n{0}的Ｖ扩张经验+10，Ｗ扩张经验+10，妊娠经验+1\n").format(mom_character_data.name)
                if mom_character_data.ability[9] < 5:
                    mom_character_data.ability[9] = 5
                    draw_text += _("\n{0}的Ｖ扩张上升至5级\n").format(mom_character_data.name)
                if mom_character_data.ability[12] < 5:
                    mom_character_data.ability[12] = 5
                    draw_text += _("\n{0}的Ｗ扩张上升至5级\n").format(mom_character_data.name)
                draw_text += "\n※※※※※※※※※\n"
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = draw_text
            now_draw.draw()
            now_draw = draw.WaitDraw()
            now_draw.text = "\n"
            now_draw.draw()
            now_draw = draw.WaitDraw()
            now_draw.text = "\n"
            now_draw.draw()

            # 结算成就
            achievement_panel.achievement_flow(_("生育"))
            # 与女儿生育了孩子
            if handle_premise.handle_self_is_player_daughter(self.mother_character_id):
                achievement_panel.achievement_flow(_("生育"), 707)
            # 仍是阴道处女的干员在生产时被胎儿撑破处女膜
            if virgin_birth_flag:
                achievement_panel.achievement_flow(_("生育"), 709)

            break

    def draw(self):
        """绘制对象"""
        from Script.System.Web_Draw_System import (
            BORN_EVENT_PANEL_TAB_ID,
            cleanup_managed_sub_panel_mode,
            enter_managed_sub_panel_mode_by_type,
        )

        sub_panel_context = enter_managed_sub_panel_mode_by_type(BORN_EVENT_PANEL_TAB_ID)
        try:
            self._draw_born_event_content()
        finally:
            # 无论正常退出还是抛出异常，都要清理当前方法进入的子面板
            cleanup_managed_sub_panel_mode(sub_panel_context)

