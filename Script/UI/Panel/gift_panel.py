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
from Script.Design import game_time

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
        now_draw.text += handle_talent.body_part_talent_update(character_id, [103, 104, 105, 106, 107], True, _("外表年龄"))
    elif drug_id == 32:  # 外表年龄减少药
        now_draw.text += handle_talent.body_part_talent_update(character_id, [103, 104, 105, 106, 107], False, _("外表年龄"))
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
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        gift_data = game_config.config_gift_items[gift_id]
        # 药物礼物的情况
        if gift_data.type == 11:
            if not self.is_drug_effective(gift_id, target_character_data):
                return
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
                return
            else:
                # 更新最后赠送时间
                target_character_data.action_info.last_gift_time = cache.game_time
        # 道歉礼物的情况
        elif gift_data.type == 2:
            if target_character_data.ability[18] == 0 and target_character_data.sp_flag.angry_with_player == False:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}没有生气，不需要赠送道歉礼物\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
                return
            elif target_character_data.ability[18] >= 2:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}的反发刻印大于等于2级，道歉礼物无效，需要先降低到1级\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
                return
            else:
                target_character_data.ability[18] = 0
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}的反发刻印从1级降为了0\n\n").format(target_character_data.name)
                now_draw.style = 'gold_enrod'
                now_draw.text = draw_text
                now_draw.draw()

        # 礼物持有数量-1
        item_id = gift_data.item_id
        character_data.item[item_id] -= 1
        # 开始赠送礼物
        character_data.behavior.gift_id = gift_id
        handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.GIVE_GIFT,force_taget_wait=True)

    def is_drug_effective(self, drug_id: int, target_character_data: game_type.Character) -> bool:
        """
        检查药物是否对目标角色有效
        Keyword arguments:
        drug_id -- 药物ID
        target_character_data -- 目标角色数据
        """
        return_flag = True
        # 泌乳药：如果目标已有泌乳素质则无效
        if drug_id == 33:
            return_flag = not target_character_data.talent[27]
            if not return_flag:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}已经有泌乳素质了，无法使用泌乳药\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
        # 停乳药：如果目标没有泌乳素质则无效
        elif drug_id == 34:
            return_flag = target_character_data.talent[27]
            if return_flag:
                now_draw = draw.WaitDraw()
                draw_text = _("\n  {0}没有泌乳素质，无法使用停乳药\n").format(target_character_data.name)
                now_draw.text = draw_text
                now_draw.draw()
        # 其他药物都有效（身体部位修改药物等）
        return return_flag
