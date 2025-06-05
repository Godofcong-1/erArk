from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_text, game_time

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
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.center_status: bool = center_status
        """ 居中绘制状态文本 """
        character_data = cache.character_data[character_id]
        pl_character_data = cache.character_data[0]
        type_data = _("肉体情况")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        body_text_list = []
        if character_id != 0:
            # 总信息#
            now_text = _("\n 【总】\n")
            semen_count = 0
            for body_part in game_config.config_body_part:
                semen_count += character_data.dirty.body_semen[body_part][3]
            if semen_count == 0:
                now_text += _("  未接触过精液\n")
            else:
                now_text += _("  全身总共被射上过{0}ml精液\n").format(semen_count)
            body_text_list.append(now_text)
            # 口部信息#
            now_text = _("\n 【口】\n")
            now_text += _("  初吻情况：")
            if character_data.talent[4]:
                now_text += _("保有初吻\n")
            elif character_data.first_record.first_kiss_id != -1:
                kiss_id = character_data.first_record.first_kiss_id
                kiss_time = character_data.first_record.first_kiss_time
                now_text += _("于{kiss_time}在{kiss_palce}，向{character_name}博士").format(
                    character_name=cache.character_data[kiss_id].name,
                    kiss_time=str(kiss_time.month) + "月" + str(kiss_time.day) + "日",
                    kiss_palce=attr_text.get_scene_path_text(character_data.first_record.first_kiss_place),
                )
                if character_data.first_record.first_kiss_body_part == 1:
                    now_text += _("的阴茎")
                now_text += _("献上了初吻\n")
            if character_data.ability[71] == 0:
                now_text += _("  普普通通的舌头\n")
            if character_data.dirty.body_semen[2][3] == 0:
                now_text += _("  未品尝过精液\n")
            else:
                if character_data.dirty.body_semen[15][3] == 0:
                    now_text += _("  总共喝过{0}ml精液\n").format(character_data.dirty.body_semen[2][3])
                else:
                    add_semen = character_data.dirty.body_semen[2][3] + character_data.dirty.body_semen[15][3]
                    now_text += _("  总共喝过{0}ml精液（有{1}ml精液在食道直接射进了胃里）\n").format(
                        add_semen,
                        character_data.dirty.body_semen[15][3],
                    )
            body_text_list.append(now_text)
            # 胸部信息#
            now_text = _("\n 【胸】\n")
            # 根据胸部大小的素质来显示信息
            for bust_cid in [121,122,123,124,125]:
                if character_data.talent[bust_cid]:
                    info_text = game_config.config_talent[bust_cid].info
                    now_text += f"  {info_text}\n"
            if character_data.dirty.body_semen[3][3] == 0:
                now_text += _("  未淋上过精液\n")
            else:
                now_text += _("  总共被淋上过{0}ml精液\n").format(character_data.dirty.body_semen[3][3])
            # 收集的乳汁
            if character_id in pl_character_data.pl_collection.milk_total:
                milk_total = pl_character_data.pl_collection.milk_total[character_id]
                if milk_total > 0:
                    now_text += _("  总共收集了{0}ml乳汁\n").format(milk_total)
            body_text_list.append(now_text)
            # 指部信息#
            now_text = _("\n 【指】\n")
            if character_data.dirty.body_semen[5][3] == 0:
                now_text += _("  未淋上过精液\n")
            else:
                now_text += _("  总共被淋上过{0}ml精液\n").format(character_data.dirty.body_semen[5][3])
            body_text_list.append(now_text)
            # 足部信息#
            now_text = _("\n 【足】\n")
            if character_data.dirty.body_semen[11][3] == 0:
                now_text += _("  未淋上过精液\n")
            else:
                now_text += _("  总共被淋上过{0}ml精液\n").format(character_data.dirty.body_semen[11][3])
            body_text_list.append(now_text)
            # 膣部信息#
            now_text = _("\n 【膣】\n")
            now_text += _("  处女情况：")
            ui_text = ""
            if character_data.talent[0]:
                now_text += _("保有处女\n")
                ui_text = game_config.ui_text_data['ability']['V感觉0']
            elif character_data.first_record.first_sex_id != -1:
                sex_id = character_data.first_record.first_sex_id
                sex_time = character_data.first_record.first_sex_time
                sex_posture = character_data.first_record.first_sex_posture

                now_text += _("于{time}在{palce}，被{character_name}博士以{posture}夺走了处女\n").format(
                    character_name=cache.character_data[sex_id].name,
                    time=game_time.get_date_until_day(sex_time),
                    palce=attr_text.get_scene_path_text(character_data.first_record.first_sex_place),
                    posture=sex_posture,
                )
                ui_text_lv = (character_data.ability[4] + 1 ) // 2
                ui_text_lv = max(1, ui_text_lv)
                ui_text_lv = min(4, ui_text_lv)
                ui_text_cid = f"V感觉{ui_text_lv}"
                ui_text = game_config.ui_text_data['ability'][ui_text_cid]
            # V感觉描述
            now_text += f"  {ui_text}\n"
            if character_data.dirty.body_semen[6][3] == 0:
                now_text += _("  未射入过精液\n")
            else:
                now_text += _("  总共被射入过{0}ml精液\n").format(character_data.dirty.body_semen[6][3])
            body_text_list.append(now_text)
            # 肛部信息#
            now_text = _("\n 【肛】\n")
            now_text += "  后庭处女情况："
            ui_text = ""
            if character_data.talent[1]:
                now_text += _("保有后庭处女\n")
                ui_text = game_config.ui_text_data['ability']['A感觉0']
            elif character_data.first_record.first_a_sex_id != -1:
                a_sex_id = character_data.first_record.first_a_sex_id
                a_sex_time = character_data.first_record.first_a_sex_time
                a_sex_posture = character_data.first_record.first_a_sex_posture

                now_text += _("于{time}在{palce}，被{character_name}博士以{posture}夺走了A处女\n").format(
                    character_name=cache.character_data[a_sex_id].name,
                    time=game_time.get_date_until_day(a_sex_time),
                    palce=attr_text.get_scene_path_text(character_data.first_record.first_a_sex_place),
                    posture=a_sex_posture,
                )
                ui_text_lv = (character_data.ability[5] + 1 ) // 2
                ui_text_lv = max(1, ui_text_lv)
                ui_text_lv = min(4, ui_text_lv)
                ui_text_cid = f"A感觉{ui_text_lv}"
                ui_text = game_config.ui_text_data['ability'][ui_text_cid]
            # 精液量描述
            now_text += f"  {ui_text}\n"
            if character_data.dirty.body_semen[8][3] == 0:
                now_text += _("  未射入过精液\n")
            else:
                now_text += _("  总共被射入过{0}ml精液\n").format(character_data.dirty.body_semen[8][3])
            body_text_list.append(now_text)
            # 子宫信息#
            now_text = _("\n 【宫】\n")
            # W感觉描述
            ui_text_lv = (character_data.ability[7] + 1 ) // 2
            ui_text_cid = f"W感觉{ui_text_lv}"
            ui_text = game_config.ui_text_data['ability'][ui_text_cid]
            now_text += f"  {ui_text}\n"
            # 精液量描述
            if character_data.dirty.body_semen[7][3] == 0:
                now_text += _("  未射入过精液\n")
            else:
                now_text += _("  总共被射入过{0}ml精液\n").format(character_data.dirty.body_semen[7][3])
            # 怀孕情况
            start_date = cache.game_time
            end_date = character_data.pregnancy.fertilization_time
            past_day = (start_date - end_date).days
            if character_data.talent[20]:
                now_text += _("  已受精{0}天，").format(past_day)
                now_text += _("但从外表上还看不出来\n")
            elif character_data.talent[21]:
                now_text += _("  已受精{0}天，").format(past_day)
                now_text += _("[妊娠]中，肚子已经大起来了\n")
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
            if character_data.dirty.body_semen[9][3] == 0:
                now_text += _("  未射入过精液\n")
            else:
                now_text += _("  总共被射入过{0}ml精液\n").format(character_data.dirty.body_semen[9][3])
            # 圣水情况
            if character_id in pl_character_data.pl_collection.urine_total:
                urine_total = pl_character_data.pl_collection.urine_total[character_id]
                if urine_total > 0:
                    now_text += _("  总共收集了{0}ml圣水\n").format(urine_total)
            # 其他信息
            now_text += _("\n 【其他】")
            if character_data.dirty.absorbed_total_semen > 0:
                now_text += _("  肠胃一共吸收了{0}ml精液\n").format(character_data.dirty.absorbed_total_semen)
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

