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
        from Script.Design import handle_instruct
        character_data: game_type.Character = cache.character_data[0]
        gift_data = game_config.config_gift_items[gift_id]

        # 检查是否可以赠送礼物
        if not self.check_gift_available(gift_id):
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
            effective_flag = not target_character_data.talent[27]
            if not effective_flag:
                draw_text = _("\n  {0}已经在【泌乳】了，无法使用泌乳药\n").format(target_character_data.name)
        # 停乳药：如果目标没有泌乳素质则无效
        elif drug_id == 34:
            effective_flag = target_character_data.talent[27]
            if not effective_flag:
                draw_text = _("\n  {0}没有在【泌乳】，无法使用停乳药\n").format(target_character_data.name)
        
        # 如果药物无效，则绘制提示信息
        if not effective_flag:
            now_draw = draw.WaitDraw()
            now_draw.text = draw_text
            now_draw.draw()

        return effective_flag
