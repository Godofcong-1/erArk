from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import game_time, handle_premise
from Script.System.Pregnancy_System import pregnancy_constant

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

def handle_drug_use_effect(character_id: int, drug_id: int):
    """
    处理药物使用效果
    Keyword arguments:
    character_id -- 角色id
    drug_id -- 药物id
    """
    from Script.Design import handle_talent
    
    character_data: game_type.Character = cache.character_data[character_id]
    now_draw = draw.WaitDraw()
    now_draw.text = '\n  '
    # 身体部位修改药剂处理
    if drug_id == 21:  # 丰胸药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [121, 122, 123, 124, 125], True, _("胸部"))
    elif drug_id == 22:  # 缩胸药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [121, 122, 123, 124, 125], False, _("胸部"))
    elif drug_id == 23:  # 丰臀药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [126, 127, 128], True, _("臀部"))
    elif drug_id == 24:  # 缩臀药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [126, 127, 128], False, _("臀部"))
    elif drug_id == 25:  # 丰腿药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [129, 130], True, _("腿部"))
    elif drug_id == 26:  # 瘦腿药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [129, 130], False, _("腿部"))
    elif drug_id == 27:  # 丰足药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [131, 132], True, _("足部"))
    elif drug_id == 28:  # 瘦足药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [131, 132], False, _("足部"))
    elif drug_id == 31:  # 外表年龄增长药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [102, 103, 104, 105, 106, 107], True, _("外表年龄"))
    elif drug_id == 32:  # 外表年龄减少药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [102, 103, 104, 105, 106, 107], False, _("外表年龄"))
    elif drug_id == 33:  # 泌乳药
        character_data.talent[27] = 1
        now_draw.text += _("{0}获得了【泌乳】\n").format(character_data.name)
    elif drug_id == 34:  # 停乳药
        character_data.talent[27] = 0
        now_draw.text += _("{0}失去了【泌乳】\n").format(character_data.name)
    elif drug_id == 35:  # 妊娠加速药
        from Script.System.Pregnancy_System import pregnancy_handle, pregnancy_panel
        add_day = pregnancy_handle.get_pregnancy_acceleration_amount(character_id)
        if add_day > 0:
            character_data.pregnancy.acceleration_days += add_day
            now_acc = int(character_data.pregnancy.acceleration_days)
            # 预计日期用游戏时间函数计算，自动归并到四季月
            predict_time = game_time.get_sub_date(day=pregnancy_constant.PARTURIENT_DAY - now_acc, old_date=character_data.pregnancy.fertilization_time)
            now_draw.text += _("本次加速{0}天，累计加速{1}天，{2}的预计临盆日期提前到了{3}\n").format(int(add_day), now_acc, character_data.name, pregnancy_panel.get_date_text(predict_time))
        else:
            # 兜底：结算时已到加速极限则不生效（正常已被送出前校验拦截）
            now_draw.text += _("{0}的孕期已经加速到极限，药物没有产生效果\n").format(character_data.name)
    elif drug_id == 36:  # 孵化加速药
        from Script.System.Pregnancy_System import egg_handle, pregnancy_panel
        pl_character_data: game_type.Character = cache.character_data[0]
        egg_id = getattr(pl_character_data.behavior, "gift_egg_id", -1)
        pl_character_data.behavior.gift_egg_id = -1
        egg_data = character_data.pregnancy.eggs.get(egg_id)
        # 兜底：选中的卵已不存在或不在孵化中则不生效
        if egg_data is None or not (egg_data["identified"] and egg_data["fertilized"]):
            now_draw.text += _("选中的卵已经不存在，药物没有产生效果\n")
        else:
            add_day = egg_handle.get_egg_acceleration_amount(egg_data)
            if add_day > 0:
                egg_data["acceleration_days"] = egg_data.get("acceleration_days", 0) + add_day
                now_acc = int(egg_data["acceleration_days"])
                predict_time = game_time.get_sub_date(day=pregnancy_constant.HATCH_TOTAL_DAY - now_acc, old_date=egg_data["lay_time"])
                now_draw.text += _("本次加速{0}天，累计加速{1}天，这枚卵的预计破壳日期提前到了{2}\n").format(int(add_day), now_acc, pregnancy_panel.get_date_text(predict_time))
            else:
                now_draw.text += _("这枚卵已经加速到极限，药物没有产生效果\n")
    elif drug_id == 37:  # 假孕药
        character_data.talent[25] = 1
        now_draw.text += _("{0}获得了【假孕孕肚】，肚子像真正的孕妇一样隆起来了\n").format(character_data.name)
    elif drug_id == 38:  # 假孕终止药
        character_data.talent[25] = 0
        now_draw.text += _("{0}失去了【假孕孕肚】，隆起的肚子恢复了原状\n").format(character_data.name)
    elif drug_id == 39:  # 成长加速药
        from Script.System.Pregnancy_System import pregnancy_handle, pregnancy_panel
        pl_character_data: game_type.Character = cache.character_data[0]
        child_id = getattr(pl_character_data.behavior, "gift_child_id", -1)
        pl_character_data.behavior.gift_child_id = -1
        # 兜底：选中的孩子已不是目标名下的婴儿则不生效
        if child_id not in pregnancy_handle.get_baby_id_list(character_id):
            now_draw.text += _("选中的婴儿已经不在婴儿期，药物没有产生效果\n")
        else:
            child_character_data: game_type.Character = cache.character_data[child_id]
            add_day = pregnancy_handle.get_child_growth_acceleration_amount(child_id)
            if add_day > 0:
                child_character_data.pregnancy.growth_acceleration_days = getattr(child_character_data.pregnancy, "growth_acceleration_days", 0) + add_day
                now_acc = int(child_character_data.pregnancy.growth_acceleration_days)
                predict_time = game_time.get_sub_date(day=pregnancy_constant.REARING_COMPLETE_DAY - now_acc, old_date=child_character_data.pregnancy.born_time)
                now_draw.text += _("本次加速{0}天，累计加速{1}天，{2}预计将在{3}成长为幼女\n").format(int(add_day), now_acc, child_character_data.name, pregnancy_panel.get_date_text(predict_time))
            else:
                now_draw.text += _("{0}已经快要成长为幼女了，药物没有产生效果\n").format(child_character_data.name)
    elif drug_id == 40:  # 成长停滞药
        character_data.talent[28] = 1
        now_draw.text += _("{0}获得了【成长停滞】，在使用成长继续药之前她会一直保持在当前的阶段\n").format(character_data.name)
    elif drug_id == 41:  # 成长继续药
        character_data.talent[28] = 0
        now_draw.text += _("{0}失去了【成长停滞】，她会继续正常成长\n").format(character_data.name)

    # 绘制结果
    now_draw.style = 'gold_enrod'
    now_draw.draw()


class Gift_Panel:
    """
    用于赠送礼物的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """
        初始化绘制对象
        参数：
            width (int): 绘制的最大宽度
        返回值：
            None
        """
        self.width: int = width
        """ 绘制的最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.show_drug_gift: bool = False
        # 药物类礼物展开/收起标志，默认为收起

    def toggle_drug_gift(self):
        """
        切换药物类礼物的展开/收起状态
        参数：无
        返回值：无
        """
        self.show_drug_gift = not self.show_drug_gift

    def draw(self):
        """
        绘制对象
        参数：无
        返回值：无
        """
        character_data: game_type.Character = cache.character_data[0]
        title_text = _("赠送礼物")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            # 是否已绘制药物类展开/收起按钮
            drug_toggle_drawn = False
            # 遍历礼物数据
            for gift_id in game_config.config_gift_items:
                gift_data = game_config.config_gift_items[gift_id]
                # 检查是否到药物类分组的起始id
                if gift_id == 21 and not drug_toggle_drawn:
                    # 根据展开标志显示不同按钮
                    if self.show_drug_gift:
                        drug_toggle_text = _("▼药物类")
                    else:
                        drug_toggle_text = _("▶药物类")
                    drug_toggle_button = draw.LeftButton(
                        _(drug_toggle_text),
                        _(drug_toggle_text),
                        self.width,
                        cmd_func=self.toggle_drug_gift,
                        args=(),
                    )
                    return_list.append(drug_toggle_button.return_text)
                    drug_toggle_button.draw()
                    line_feed.draw()
                    drug_toggle_drawn = True
                # 如果是药物类礼物且未展开，则跳过显示
                if gift_data.type == 11 and not self.show_drug_gift:
                    continue
                cant_flag = False
                item_id = gift_data.item_id
                item_data = game_config.config_item[item_id]
                gift_id_text = str(gift_id).rjust(2,'0')
                if gift_data.todo == 1:
                    gift_text = f"[{gift_id_text}]{gift_data.info}"
                    gift_text += _("(未实装)")
                    cant_flag = True
                else:
                    gift_text = f"[{gift_id_text}]{item_data.name}：{item_data.info}"
                if character_data.item[item_id] <= 0:
                    gift_text += _("(未拥有)")
                    cant_flag = True

                # 如果未拥有或者未实装则不显示按钮，仅打印灰色文本
                if cant_flag:
                    text_draw = draw.NormalDraw()
                    text_draw.text = gift_text
                    text_draw.style = 'deep_gray'
                    text_draw.draw()
                else:
                    button_draw = draw.LeftButton(
                        _(gift_text),
                        _(str(gift_id)),
                        self.width,
                        cmd_func=self.select_gift,
                        args=(gift_id,),
                        )
                    # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                line_feed.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_gift(self, gift_id):
        """礼物的确认选择"""
        from Script.System.Instruct_System import handle_instruct
        character_data: game_type.Character = cache.character_data[0]
        gift_data = game_config.config_gift_items[gift_id]

        # 检查是否可以赠送礼物
        if not self.check_gift_available(gift_id):
            return

        # 孵化加速药需要先选择目标卵（玩家取消则不送出）
        if gift_id == 36:
            if not self.select_target_egg():
                return
        # 成长加速药需要先选择目标婴儿（玩家取消则不送出）
        if gift_id == 39:
            if not self.select_target_baby():
                return

        # 将礼物id赋予角色行为数据
        character_data.behavior.gift_id = gift_id
        # 药剂礼物需要轻度猥亵条件
        if gift_data.type == 11:
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.GIVE_GIFT, judge = _("初级骚扰"), force_taget_wait=True)
        # 阴茎倒模需要严重猥亵条件
        elif gift_data.type == 13:
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.GIVE_GIFT, judge = _("严重骚扰"), force_taget_wait=True)
        else:
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.GIVE_GIFT, force_taget_wait=True)

    def select_target_egg(self) -> bool:
        """
        孵化加速药的选卵交互：绘制交互对象全部可加速的孵化中卵供玩家选择\n
        仅一枚可加速卵时跳过选择直接选中\n
        Returns:\n
        bool -- 是否完成了选择（False为玩家取消或无可选卵）
        """
        from Script.System.Pregnancy_System import egg_handle, pregnancy_panel
        character_data: game_type.Character = cache.character_data[0]
        target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
        accelerable_eggs = egg_handle.get_accelerable_hatching_eggs(target_character_data.cid)
        if not len(accelerable_eggs):
            return False
        # 仅一枚可加速卵时跳过选择直接选中
        if len(accelerable_eggs) == 1:
            character_data.behavior.gift_egg_id = list(accelerable_eggs.keys())[0]
            return True
        # 多枚卵时绘制选择列表
        title_draw = draw.TitleLineDraw(_("选择要加速孵化的卵"), self.width)
        while 1:
            return_list = []
            title_draw.draw()
            for egg_id, egg_data in accelerable_eggs.items():
                hatch_day = egg_handle.get_hatch_day(egg_data)
                acc_day = int(egg_data.get("acceleration_days", 0))
                born_time = game_time.get_sub_date(day=pregnancy_constant.HATCH_TOTAL_DAY - acc_day, old_date=egg_data["lay_time"])
                egg_text = _("[{0}号卵] 孵化第{1}天（已加速{2}天，预计{3}破壳）").format(egg_id, hatch_day, acc_day, pregnancy_panel.get_date_text(born_time))
                button_draw = draw.LeftButton(
                    egg_text,
                    str(egg_id),
                    self.width,
                    cmd_func=self.select_egg_id,
                    args=(egg_id,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回选卵"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return False
            return True

    def select_egg_id(self, egg_id: int):
        """
        选卵按钮回调：把选中的卵编号写入玩家行为数据\n
        Keyword arguments:\n
        egg_id -- 选中的卵编号
        """
        character_data: game_type.Character = cache.character_data[0]
        character_data.behavior.gift_egg_id = egg_id

    def select_target_baby(self) -> bool:
        """
        成长加速药的选婴儿交互：绘制交互对象名下全部可加速的婴儿供玩家选择\n
        仅一名可加速婴儿时跳过选择直接选中\n
        Returns:\n
        bool -- 是否完成了选择（False为玩家取消或无可选婴儿）
        """
        from Script.System.Pregnancy_System import pregnancy_handle, pregnancy_panel
        character_data: game_type.Character = cache.character_data[0]
        target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
        accelerable_babies = pregnancy_handle.get_accelerable_babies(target_character_data.cid)
        if not len(accelerable_babies):
            return False
        # 仅一名可加速婴儿时跳过选择直接选中
        if len(accelerable_babies) == 1:
            character_data.behavior.gift_child_id = accelerable_babies[0]
            return True
        # 多名婴儿时绘制选择列表
        title_draw = draw.TitleLineDraw(_("选择要加速成长的婴儿"), self.width)
        while 1:
            return_list = []
            title_draw.draw()
            for child_id in accelerable_babies:
                child_character_data: game_type.Character = cache.character_data[child_id]
                grow_day = pregnancy_handle.get_child_grow_day(child_id)
                acc_day = int(getattr(child_character_data.pregnancy, "growth_acceleration_days", 0))
                grow_time = game_time.get_sub_date(day=pregnancy_constant.REARING_COMPLETE_DAY - acc_day, old_date=child_character_data.pregnancy.born_time)
                baby_text = _("[{0}] 出生第{1}天（已加速{2}天，预计{3}成长为幼女）").format(child_character_data.name, grow_day, acc_day, pregnancy_panel.get_date_text(grow_time))
                button_draw = draw.LeftButton(
                    baby_text,
                    str(child_id),
                    self.width,
                    cmd_func=self.select_child_id,
                    args=(child_id,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回选婴儿"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return False
            return True

    def select_child_id(self, child_id: int):
        """
        选婴儿按钮回调：把选中的婴儿角色id写入玩家行为数据\n
        Keyword arguments:\n
        child_id -- 选中的婴儿角色id
        """
        character_data: game_type.Character = cache.character_data[0]
        character_data.behavior.gift_child_id = child_id

    def check_gift_available(self, gift_id: int) -> bool:
        """
        检查是否可以赠送礼物\n
        Keyword arguments:\n
        gift_id -- 礼物ID\n
        Returns:\n
        bool -- 是否可以赠送\n
        """
        character_data: game_type.Character = cache.character_data[0]
        target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
        gift_data = game_config.config_gift_items[gift_id]
        # 药物礼物的情况
        if gift_data.type == 11:
            if not self.is_drug_effective(gift_id, target_character_data):
                return False
        # 好感礼物的情况
        elif gift_data.type == 3:
            last_gift_time = target_character_data.action_info.last_gift_time
            days_diff = game_time.count_day_for_datetime(last_gift_time, cache.game_time)
            # 如果和今天是同一天，则不能重复赠送
            if days_diff <= 0:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}今天已经收过好感礼物了，不能重复赠送\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
                return False
        # 道歉礼物的情况
        elif gift_data.type == 2:
            if target_character_data.ability[18] >= 2:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}的反发刻印大于等于2级，道歉礼物无效，需要先降低到1级\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
                return False
            elif target_character_data.ability[18] == 0 and target_character_data.sp_flag.angry_with_player == False:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}没有生气，不需要赠送道歉礼物\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
                return False
        # 阴茎倒模的情况
        elif gift_data.type == 13:
            # 检查对方是否已经拥有
            if handle_premise.handle_target_have_penis_mold(0):
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}已经拥有了你的阴茎倒模，不能重复赠送\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
                return False
        # 否则返回True
        return True

    def is_drug_effective(self, drug_id: int, target_character_data: game_type.Character) -> bool:
        """
        检查药物是否对目标角色有效
        Keyword arguments:
        drug_id -- 药物ID
        target_character_data -- 目标角色数据
        """
        effective_flag = True
        draw_text = ""
        # 丰胸药：如果目标已是爆乳则无效
        if drug_id == 21:
            effective_flag = not target_character_data.talent[125]
            if not effective_flag:
                draw_text = _("\n  {0}已经是最大的【爆乳】了，无法使用丰胸药\n").format(target_character_data.name)
        # 缩胸药：如果目标已是绝壁则无效
        elif drug_id == 22:
            effective_flag = not target_character_data.talent[121]
            if not effective_flag:
                draw_text = _("\n  {0}已经是最小的【绝壁】了，无法使用缩胸药\n").format(target_character_data.name)
        # 丰臀药：如果目标已是巨臀则无效
        elif drug_id == 23:
            effective_flag = not target_character_data.talent[128]
            if not effective_flag:
                draw_text = _("\n  {0}已经是最大的【巨臀】了，无法使用丰臀药\n").format(target_character_data.name)
        # 缩臀药：如果目标已是小臀则无效
        elif drug_id == 24:
            effective_flag = not target_character_data.talent[126]
            if not effective_flag:
                draw_text = _("\n  {0}已经是最小的【小臀】了，无法使用缩臀药\n").format(target_character_data.name)
        # 丰腿药：如果目标已是肉腿则无效
        elif drug_id == 25:
            effective_flag = not target_character_data.talent[130]
            if not effective_flag:
                draw_text = _("\n  {0}已经是【肉腿】了，无法使用丰腿药\n").format(target_character_data.name)
        # 瘦腿药：如果目标已是细腿则无效
        elif drug_id == 26:
            effective_flag = not target_character_data.talent[129]
            if not effective_flag:
                draw_text = _("\n  {0}已经是【细腿】了，无法使用瘦腿药\n").format(target_character_data.name)
        # 丰足药：如果目标已是长足则无效
        elif drug_id == 27:
            effective_flag = not target_character_data.talent[132]
            if not effective_flag:
                draw_text = _("\n  {0}已经是【长足】了，无法使用丰足药\n").format(target_character_data.name)
        # 瘦足药：如果目标已是小足则无效
        elif drug_id == 28:
            effective_flag = not target_character_data.talent[131]
            if not effective_flag:
                draw_text = _("\n  {0}已经是【小足】了，无法使用瘦足药\n").format(target_character_data.name)
        # 外表年龄增长药：如果目标已是熟女或人妻则无效
        elif drug_id == 31:
            if target_character_data.talent[106] or target_character_data.talent[107]:
                effective_flag = False
            if not effective_flag:
                draw_text = _("\n  {0}已经是最大的【熟女】或【人妻】了，无法使用外表年龄增长药\n").format(target_character_data.name)
        # 外表年龄减少药：如果目标已是幼女则无效
        elif drug_id == 32:
            effective_flag = not target_character_data.talent[102]
            if not effective_flag:
                draw_text = _("\n  {0}已经是最小的【幼女】了，无法使用外表年龄减少药\n").format(target_character_data.name)
        # 泌乳药：如果目标已有泌乳素质则无效
        elif drug_id == 33:
            effective_flag = not handle_premise.handle_lactation_1(target_character_data.cid)
            if not effective_flag:
                draw_text = _("\n  {0}已经在【泌乳】了，无法使用泌乳药\n").format(target_character_data.name)
        # 停乳药：如果目标没有泌乳素质则无效
        elif drug_id == 34:
            effective_flag = bool(handle_premise.handle_lactation_1(target_character_data.cid))
            if not effective_flag:
                draw_text = _("\n  {0}没有在【泌乳】，无法使用停乳药\n").format(target_character_data.name)
        # 妊娠加速药：仅对受精或妊娠状态的胎生干员有效，且未达加速上限
        elif drug_id == 35:
            from Script.System.Pregnancy_System import pregnancy_handle, egg_handle
            if not (handle_premise.handle_fertilization_1(target_character_data.cid) or handle_premise.handle_pregnancy_1(target_character_data.cid)):
                effective_flag = False
                draw_text = _("\n  {0}没有处于受精或妊娠状态，无法使用妊娠加速药\n").format(target_character_data.name)
            elif egg_handle.get_birth_type(target_character_data.cid) != 1:
                effective_flag = False
                draw_text = _("\n  {0}的种族不是胎生，无法使用妊娠加速药\n").format(target_character_data.name)
            elif pregnancy_handle.get_pregnancy_acceleration_amount(target_character_data.cid) <= 0:
                effective_flag = False
                draw_text = _("\n  {0}的孕期已经加速到极限了，无法继续使用妊娠加速药\n").format(target_character_data.name)
        # 孵化加速药：玩家需在育儿室（受精卵均存放于育儿室孵化），且目标持有可加速的孵化中卵
        elif drug_id == 36:
            from Script.System.Pregnancy_System import egg_handle
            if not handle_premise.handle_in_nursery(0):
                effective_flag = False
                draw_text = _("\n  只能在育儿室使用孵化加速药\n")
            elif not len(egg_handle.get_hatching_eggs(target_character_data.cid)):
                effective_flag = False
                draw_text = _("\n  {0}没有正在孵化中的卵，无法使用孵化加速药\n").format(target_character_data.name)
            elif not len(egg_handle.get_accelerable_hatching_eggs(target_character_data.cid)):
                effective_flag = False
                draw_text = _("\n  {0}的卵都已经加速到极限了，无法继续使用孵化加速药\n").format(target_character_data.name)
        # 假孕药：仅对不处于任何怀孕相关状态的胎生干员有效
        elif drug_id == 37:
            from Script.System.Pregnancy_System import egg_handle
            if egg_handle.get_birth_type(target_character_data.cid) != 1:
                effective_flag = False
                draw_text = _("\n  {0}的种族不是胎生，无法使用假孕药\n").format(target_character_data.name)
            else:
                # 受精/妊娠/临盆/产后/育儿/假孕孕肚/孕肚外观 任一为真即处于怀孕相关状态
                pregnancy_premise_list = [
                    handle_premise.handle_fertilization_1,
                    handle_premise.handle_pregnancy_1,
                    handle_premise.handle_parturient_1,
                    handle_premise.handle_postpartum_1,
                    handle_premise.handle_rearing_1,
                    handle_premise.handle_fake_inflation_1,
                    handle_premise.handle_inflation_1,
                ]
                for premise_func in pregnancy_premise_list:
                    if premise_func(target_character_data.cid):
                        effective_flag = False
                        draw_text = _("\n  {0}正处于怀孕相关状态中，无法使用假孕药\n").format(target_character_data.name)
                        break
        # 假孕终止药：仅对处于假孕状态的干员有效
        elif drug_id == 38:
            effective_flag = bool(handle_premise.handle_fake_inflation_1(target_character_data.cid))
            if not effective_flag:
                draw_text = _("\n  {0}没有处于假孕状态，不需要使用假孕终止药\n").format(target_character_data.name)
        # 成长加速药：玩家需在育儿室，且目标名下有可加速的婴儿
        elif drug_id == 39:
            from Script.System.Pregnancy_System import pregnancy_handle
            if not handle_premise.handle_in_nursery(0):
                effective_flag = False
                draw_text = _("\n  只能在育儿室使用成长加速药\n")
            elif not len(pregnancy_handle.get_baby_id_list(target_character_data.cid)):
                effective_flag = False
                draw_text = _("\n  {0}没有正在婴儿期的孩子，无法使用成长加速药\n").format(target_character_data.name)
            elif not len(pregnancy_handle.get_accelerable_babies(target_character_data.cid)):
                effective_flag = False
                draw_text = _("\n  {0}的孩子都已经快要长成幼女了，无法使用成长加速药\n").format(target_character_data.name)
        # 成长停滞药：仅对处于幼女或萝莉阶段、且未处于成长停滞的女儿有效
        elif drug_id == 40:
            if not handle_premise.handle_self_is_player_daughter(target_character_data.cid):
                effective_flag = False
                draw_text = _("\n  {0}不是博士的女儿，无法使用成长停滞药\n").format(target_character_data.name)
            elif not handle_premise.handle_self_child_or_loli_1(target_character_data.cid):
                effective_flag = False
                draw_text = _("\n  {0}不处于幼女或萝莉阶段，无法使用成长停滞药\n").format(target_character_data.name)
            elif handle_premise.handle_growth_stop_1(target_character_data.cid):
                effective_flag = False
                draw_text = _("\n  {0}已经处于【成长停滞】状态了，无法重复使用成长停滞药\n").format(target_character_data.name)
        # 成长继续药：仅对处于幼女或萝莉阶段、且已处于成长停滞的女儿有效
        elif drug_id == 41:
            if not handle_premise.handle_self_is_player_daughter(target_character_data.cid):
                effective_flag = False
                draw_text = _("\n  {0}不是博士的女儿，无法使用成长继续药\n").format(target_character_data.name)
            elif not handle_premise.handle_self_child_or_loli_1(target_character_data.cid):
                effective_flag = False
                draw_text = _("\n  {0}不处于幼女或萝莉阶段，无法使用成长继续药\n").format(target_character_data.name)
            elif not handle_premise.handle_growth_stop_1(target_character_data.cid):
                effective_flag = False
                draw_text = _("\n  {0}没有处于【成长停滞】状态，不需要使用成长继续药\n").format(target_character_data.name)

        # 如果药物无效，则绘制提示信息
        if not effective_flag:
            now_draw = draw.WaitDraw()
            now_draw.text = draw_text
            now_draw.draw()

        return effective_flag
