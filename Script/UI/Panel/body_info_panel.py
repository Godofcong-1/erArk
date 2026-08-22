from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
)
from Script.Config import game_config, normal_config

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


def get_ability_lv_ui_text(character_id: int, ability_cid: int) -> str:
    """
    获取能力等级对应的UI文本
    Keyword arguments:
    character_id -- 角色id
    ability_cid -- 能力cid
    Return arguments:
    ui_text -- 能力等级对应的UI文本
    """
    character_data = cache.character_data[character_id]
    ability_lv = character_data.ability[ability_cid]
    ui_text_lv = (ability_lv + 1 ) // 2
    ui_text_lv = max(0, ui_text_lv)
    ui_text_lv = min(4, ui_text_lv)
    ui_text_cid = f"{game_config.config_ability[ability_cid].name}{ui_text_lv}"
    ui_text = game_config.ui_text_data['ability'][ui_text_cid]
    # 如果文本中有换行符的话，则将其替换为实际的换行
    ui_text = ui_text.replace('\\n', '\n  ')
    return ui_text

class CharacterBodyText:
    """
    显示角色肉体面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.column = column
        """ 每行状态最大个数 """
        self.draw_list: List = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.center_status: bool = center_status
        """ 居中绘制状态文本 """

        from Script.Design import handle_talent

        character_data = cache.character_data[character_id]
        type_data = _("肉体情况")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        body_text_list = []
        if character_id != 0:
            # 体液类数据（喝过/被淋精液、乳汁、圣水、肠胃吸收等）已统一迁移到[性行为履历]面板的体液数据组
            # 口部信息#
            now_text = _("\n 【口】\n")
            now_text += _("  初吻情况：")
            # 初吻详情句已统一合并到[性行为履历]面板，此处只保留状态行
            if character_data.talent[4]:
                now_text += _("保有初吻\n")
            else:
                now_text += _("已失去初吻\n")
            # 口感觉描述
            ui_text = get_ability_lv_ui_text(character_id, 100)
            now_text += f"  {ui_text}\n"
            # 舌技描述
            ui_text = get_ability_lv_ui_text(character_id, 71)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 胸部信息#
            now_text = _("\n 【胸】\n")
            # 根据胸部大小的素质来显示信息
            for bust_cid in [121,122,123,124,125]:
                if character_data.talent[bust_cid]:
                    info_text = game_config.config_talent[bust_cid].info
                    now_text += f"  {info_text}\n"
            # B感觉描述
            ui_text = get_ability_lv_ui_text(character_id, 1)
            now_text += f"  {ui_text}\n"
            # 胸技描述
            ui_text = get_ability_lv_ui_text(character_id, 73)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 指部信息#
            now_text = _("\n 【指】\n")
            # 指技描述
            ui_text = get_ability_lv_ui_text(character_id, 70)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 足部信息#
            now_text = _("\n 【足】\n")
            # 足技描述
            ui_text = get_ability_lv_ui_text(character_id, 72)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 膣部信息#
            now_text = _("\n 【膣】\n")
            now_text += _("  处女情况：")
            # 破处详情句已统一合并到[性行为履历]面板，此处只保留状态行；感度描述只看处女素质，与破处记录解耦
            if character_data.talent[0]:
                now_text += _("保有处女\n")
                ui_text = game_config.ui_text_data['ability']['阴道感度0']
            else:
                now_text += _("已失去处女\n")
                ui_text = get_ability_lv_ui_text(character_id, 4)
            # V感觉描述
            now_text += f"  {ui_text}\n"
            # 膣技描述
            ui_text = get_ability_lv_ui_text(character_id, 74)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 肛部信息#
            now_text = _("\n 【肛】\n")
            now_text += _("  处女情况：")
            # 破处详情句已统一合并到[性行为履历]面板，此处只保留状态行；感度描述只看处女素质，与破处记录解耦
            if character_data.talent[1]:
                now_text += _("保有后庭处女\n")
                ui_text = game_config.ui_text_data['ability']['肛肠感度0']
            else:
                now_text += _("已失去后庭处女\n")
                ui_text = get_ability_lv_ui_text(character_id, 5)
            now_text += f"  {ui_text}\n"
            # 肛技描述
            ui_text = get_ability_lv_ui_text(character_id, 75)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 子宫信息#
            now_text = _("\n 【宫】\n")
            now_text += _("  处女情况：")
            # 破处详情句已统一合并到[性行为履历]面板，此处只保留状态行；感度描述只看处女素质，与破处记录解耦
            if character_data.talent[3]:
                now_text += _("保有子宫处女\n")
                ui_text = game_config.ui_text_data['ability']['子宫感度0']
            else:
                now_text += _("已失去子宫处女\n")
                # W感觉描述
                ui_text = get_ability_lv_ui_text(character_id, 7)
            now_text += f"  {ui_text}\n"
            # 怀孕情况
            start_date = cache.game_time
            end_date = character_data.pregnancy.fertilization_time
            past_day = (start_date - end_date).days
            if character_data.talent[20]:
                now_text += _("  已受精{0}天，").format(past_day)
                now_text += _("但从外表上还看不出来\n")
            elif character_data.talent[21]:
                now_text += _("  已受精{0}天，").format(past_day)
                now_text += _("[妊娠]中，肚子已经大起来了")
                last_day = 261 - past_day
                if last_day > 0:
                    now_text += _("，距离临盆预计还有{0}天左右\n").format(last_day)
                else:
                    now_text += "\n"
            elif character_data.talent[22]:
                now_text += _("  已受精{0}天，").format(past_day)
                now_text += _("[临盆]中，即将诞下爱的结晶\n")
            elif character_data.talent[23]:
                now_text += _("  正在[产后]休息\n")
            elif character_data.talent[24]:
                now_text += _("  [育儿]中，正在给宝宝喂奶\n")
            if character_data.experience[86] == 0:
                now_text += _("  未分娩过\n")
            else:
                now_text += _("  为博士生下了  ")
                for chara_id in character_data.relationship.child_id_list:
                    now_text += f"{cache.character_data[chara_id].name}  "
                now_text += _("共{0}个孩子\n").format(len(character_data.relationship.child_id_list))
            body_text_list.append(now_text)
            # 尿道信息#
            now_text = _("\n 【尿】\n")
            now_text += _("  处女情况：")
            # 破处详情句已统一合并到[性行为履历]面板，此处只保留状态行；感度描述只看处女素质，与破处记录解耦
            if character_data.talent[2]:
                now_text += _("保有尿道处女\n")
                ui_text = game_config.ui_text_data['ability']['尿道感度0']
            else:
                now_text += _("已失去尿道处女\n")
                # U感觉描述
                ui_text = get_ability_lv_ui_text(character_id, 6)
            now_text += f"  {ui_text}\n"
            body_text_list.append(now_text)
            # 其他信息
            now_text = _("\n 【其他】\n")
            # 母亲情况
            if character_data.relationship.mother_id != -1:
                mother_data: game_type.Character = cache.character_data[character_data.relationship.mother_id]
                child_id_list = mother_data.relationship.child_id_list
                if character_id in child_id_list:
                    child_index = child_id_list.index(character_id)
                    if child_index != -1:
                        now_text += _("  母亲为：{0}，是母亲的第{1}个孩子\n").format(mother_data.name, child_index + 1)
                else:
                    now_text += _("  母亲为：{0}\n").format(mother_data.name)
            # 喜欢的姿势
            favorite_position_id = handle_talent.settle_favorite_sex_position(character_id)
            if favorite_position_id != -1:
                sex_position_data = game_config.config_sex_position_data[favorite_position_id]
                now_text += _("  喜欢的姿势是：{0}，").format(sex_position_data.name)
                # 获取该姿势的经验
                experience_id = 140 + favorite_position_id
                experience_count = character_data.experience[experience_id]
                now_text += _("该姿势的性交经验为：{0} 次\n").format(experience_count)
            now_text += "\n"
            body_text_list.append(now_text)
        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(body_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

