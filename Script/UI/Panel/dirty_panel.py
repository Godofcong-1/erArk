from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, rich_text, constant, py_cmd
from Script.Design import map_handle, clothing, attr_calculation
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

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


def get_v_and_w_semen_count(character_id: int) -> int:
    """
    获取角色的小穴和子宫精液总量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 精液总量
    """
    character_data: game_type.Character = cache.character_data[character_id]
    all_semen_count = character_data.dirty.body_semen[6][1] + character_data.dirty.body_semen[7][1]
    return all_semen_count

class Dirty_Panel:
    """
    用于显示污浊界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("身体")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        title_text = target_data.name + _("污浊情况")
        dirty_type_list = [_("身体"), _("服装")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], Dirty_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for dirty_type in dirty_type_list:
                if dirty_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{dirty_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(dirty_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{dirty_type}]",
                        dirty_type,
                        self.width / len(dirty_type_list),
                        cmd_func=self.change_panel,
                        args=(dirty_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            name_draw = draw.NormalDraw()

            # 遍历全部位并输出结果
            now_text = ""
            if self.now_panel == _("身体"):
                a_clean_list = [_(" <脏污>"), _(" <灌肠中>"), _(" <已灌肠清洁过>"), _(" <精液灌肠中>"), _(" <已精液灌肠过>")]
                now_text = "\n"
                for i in range(len(game_config.config_body_part)):
                    now_text += "  " + target_data.dirty.body_semen[i][0] + "："

                    # 腔内透视判定
                    if i in {6,7,8,9}:
                        if not (character_data.pl_ability.visual and character_data.talent[308]):
                            now_text += _("<未知>（需要腔内透视）\n")
                            continue

                    # 小穴
                    if i == 6:
                        # 处女判定
                        if not target_data.talent[0]:
                            now_day = cache.game_time.day
                            first_day = target_data.first_record.first_sex_time.day
                            if now_day == first_day:
                                now_text += _(" <破处血>")

                        # 润滑判定
                        if target_data.status_data[8]:
                            level = attr_calculation.get_status_level(target_data.status_data[8])
                            if level <= 2:
                                now_text += _(" <些许爱液>")
                            elif level <= 4:
                                now_text += _(" <充分湿润>")
                            elif level <= 6:
                                now_text += _(" <泛滥的一塌糊涂>")
                            else:
                                now_text += _(" <泛滥的一塌糊涂>")

                    # 后穴
                    if i == 8:
                        a_clean_text = a_clean_list[target_data.dirty.a_clean]
                        now_text += a_clean_text

                    # 尿道
                    if i == 9:
                        if target_data.urinate_point <= 30:
                            now_text += _(" <残留的尿渍>")
                        elif target_data.urinate_point <= 120:
                            now_text += _(" <洁净>")
                        elif target_data.urinate_point <= 191:
                            now_text += _(" <些许尿意>")
                        elif target_data.urinate_point >= 192:
                            now_text += _(" <充盈的尿意>")
                    if target_data.dirty.body_semen[i][1]:
                        now_text += _(" <{0}ml精液>").format(str(target_data.dirty.body_semen[i][1]))
                    now_text += "\n"
                now_text += "\n"

            elif self.now_panel == _("服装"):

                now_text = ""
                # 遍历全部衣服类型
                for clothing_type in game_config.config_clothing_type:
                    type_name = game_config.config_clothing_type[clothing_type].name
                    # 当该类型里有衣服存在的时候才显示
                    if len(target_data.cloth.cloth_wear[clothing_type]):
                        now_text += f"  [{type_name}]:"
                        # 正常情况下不显示胸部和内裤的服装,debug或该部位可以显示则显示
                        if clothing_type in {6, 9} and not cache.debug_mode:
                            if not target_data.cloth.cloth_see[clothing_type]:
                                now_text += _(" 未知（需要内衣透视）\n")
                                continue
                        # 如果有多件衣服，则依次显示
                        for cloth_id in target_data.cloth.cloth_wear[clothing_type]:
                            cloth_name = game_config.config_clothing_tem[cloth_id].name
                            now_text += f" {cloth_name}"
                            # 如果该部位有精液，则显示精液信息
                            if target_data.dirty.cloth_semen[clothing_type][1] != 0:
                                now_text += _(" ({0}ml精液)").format(str(target_data.dirty.cloth_semen[clothing_type][1]))
                        now_text += "\n"

            name_draw.text = now_text
            name_draw.width = self.width
            name_draw.draw()

            return_list.extend(handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, dirty_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        dirty_type -- 要切换的面板类型
        """

        self.now_panel = dirty_type


def get_inserted_character_id() -> int:
    """
    获取玩家同场景中阴茎插入数据不为 -1 的角色id。
    参数: 无
    返回值: int -- 如果找到符合条件的角色则返回该角色id，否则返回0。
    """
    # 获取玩家数据，玩家角色id固定为0
    pl_character_data = cache.character_data[0]
    # 获取玩家的交互对象id
    target_id: int = pl_character_data.target_character_id
    # 检查玩家的交互对象是否存在且其阴茎插入数据符合条件（不为 -1）
    if target_id != 0:
        target_character = cache.character_data[target_id]
        # 如果交互对象符合条件，则返回该角色id
        if target_character.h_state.insert_position != -1:
            return target_id

    # 如果交互对象不符合条件，遍历场景内其他角色（排除玩家和交互对象）
    scene_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for character_id in scene_data.character_list:
        # 排除玩家和已检测的交互对象
        if character_id == 0 or character_id == target_id:
            continue
        now_character_data = cache.character_data[character_id]
        # 如果该角色的阴茎插入数据不为 -1，则返回该角色id
        if now_character_data.h_state.insert_position != -1:
            return character_id

    # 如果没有找到符合条件的角色则返回0
    return 0


class Dirty_Draw:
    """
    污浊绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, text: int, width: int):
        """初始化绘制对象"""
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """

        name_draw = draw.NormalDraw()

        name_draw.text = ""
        name_draw.width = self.width
        self.draw_text = ""
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


class SeeCharacterBodyPanel:
    """
    显示角色身体面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, type_number: int, center_status: bool = True):
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
        self.type_number = type_number
        """ 显示的状态类型 """
        character_data = cache.character_data[0]
        target_character_data = cache.character_data[character_data.target_character_id]
        # print("game_config.config_character_state_type :",game_config.config_character_state_type)
        # print("game_config.config_character_state_type_data :",game_config.config_character_state_type_data)

        type_line = draw.LittleTitleLineDraw(_("身体"), width, ":")
        # print("type_data.name :",type_data.name)

        # 全部位文本
        all_part_text_list = []
        # 腹部整体精液量统计
        abdomen_all_semen = 0

        # 获取没有穿服装的部位列表
        no_cloth_body_list = clothing.get_exposed_body_parts(character_data.target_character_id)

        # 是否透视中
        visual_flag = 0
        if character_data.pl_ability.visual:
            # 生理透视
            if character_data.talent[309]:
                visual_flag = 3
            # 腔内透视
            elif character_data.talent[308]:
                visual_flag = 2
            # 服装透视
            else:
                visual_flag = 1

        # 遍历全部位并输出结果
        for i in range(len(game_config.config_body_part)):
            body_part_data = game_config.config_body_part[i]
            part_name = body_part_data.name

            # 检查脏污数据中是否包含该部位，如果没有则补上
            if len(target_character_data.dirty.body_semen) <= i:
                target_character_data.dirty.body_semen.append([part_name,0,0,0])

            # 最开始先计算腹部整体的精液量累积
            if i in [5,7,8,15]:
                abdomen_all_semen += target_character_data.dirty.body_semen[i][1]

            # 判定部位是否被衣服遮挡，且没有透视中
            if i not in no_cloth_body_list and visual_flag == 0:
                continue

            # 然后腔内透视判定
            if visual_flag <= 1:
                if i in {7,9,15}:
                    continue
                # 处子血判定
                elif i == 6:
                    if not character_data.talent[0]:
                        now_day = cache.game_time.day
                        first_day = character_data.first_record.first_sex_time.day
                        if now_day == first_day:
                            # 是否显示完整污浊文本
                            dirty_text_cid = "破处血1"
                            if cache.all_system_setting.draw_setting[10]:
                                dirty_text = game_config.ui_text_data['dirty_full'][dirty_text_cid]
                                dirty_text += '\n'
                                all_part_text_list.append(f" {dirty_text}")
                            else:
                                dirty_text = game_config.ui_text_data['dirty'][dirty_text_cid]
                                all_part_text_list.append(f" <{dirty_text}>")

            # 爱液文本
            if i == 6 and target_character_data.status_data[8]:
                level = attr_calculation.get_status_level(target_character_data.status_data[8])
                if level <= 2:
                    text_index = "爱液1"
                elif level <= 4:
                    text_index = "爱液2"
                elif level <= 6:
                    text_index = "爱液3"
                else:
                    text_index = "爱液4"
                # 是否显示完整污浊文本
                if cache.all_system_setting.draw_setting[10]:
                    now_part_text = game_config.ui_text_data['dirty_full'][text_index]
                    now_part_text = f"<lavender>{now_part_text}</lavender>\n"
                    now_part_text = _(' [爱液]:') + now_part_text
                else:
                    now_part_text = game_config.ui_text_data['dirty'][text_index]
                all_part_text_list.append(f" {now_part_text}")

            # 尿液污浊
            if i == 9:
                if target_character_data.urinate_point <= 30:
                    text_index = "尿液0"
                elif target_character_data.urinate_point <= 120:
                    text_index = "尿液1"
                elif target_character_data.urinate_point <= 191:
                    text_index = "尿液2"
                else:
                    text_index = "尿液3"
                # 是否显示完整污浊文本
                if cache.all_system_setting.draw_setting[10]:
                    now_part_text = game_config.ui_text_data['dirty_full'][text_index]
                    now_part_text = f"<khaki>{now_part_text}</khaki>\n"
                    now_part_text = _(' [尿液]:') + now_part_text
                else:
                    now_part_text = game_config.ui_text_data['dirty'][text_index]
                all_part_text_list.append(f" {now_part_text}")

            # 精液污浊判定
            if target_character_data.dirty.body_semen[i][2]:
                semen_level = target_character_data.dirty.body_semen[i][2]
                dirty_text_cid = f"{_(part_name, revert_translation = True)}精液污浊{str(semen_level)}"
                # 是否显示完整污浊文本
                if cache.all_system_setting.draw_setting[10]:
                    dirty_text_context = game_config.ui_text_data['dirty_full'][dirty_text_cid]
                    dirty_text_context = f"<semen>{dirty_text_context}</semen>\n"
                    now_part_text = f"  [{part_name}]:{dirty_text_context}"
                else:
                    dirty_text_context = game_config.ui_text_data['dirty'][dirty_text_cid]
                    now_part_text = f" {part_name}{dirty_text_context}"
                all_part_text_list.append(now_part_text)

        # 如果腹部整体有精液，则显示腹部整体精液污浊
        if abdomen_all_semen:
            now_level = attr_calculation.get_semen_now_level(abdomen_all_semen, 20, 0)
            if now_level >= 2:
                dirty_text_cid = f"腹部整体精液污浊{str(now_level)}"
                # 是否显示完整污浊文本
                if cache.all_system_setting.draw_setting[10]:
                    dirty_text_context = game_config.ui_text_data['dirty_full'][dirty_text_cid]
                    dirty_text_context = f"<semen>{dirty_text_context}</semen>\n"
                    dirty_text_context = _(' [腹部]:') + dirty_text_context
                else:
                    dirty_text_context = game_config.ui_text_data['dirty'][dirty_text_cid]
                now_part_text = f" {dirty_text_context}"
                all_part_text_list.append(now_part_text)

        # 灌肠文本
        if target_character_data.dirty.a_clean:
            text_index = f"灌肠{str(target_character_data.dirty.a_clean)}"
            # 是否显示完整污浊文本
            if cache.all_system_setting.draw_setting[10]:
                enemas_text = game_config.ui_text_data['dirty_full'][text_index]
                enemas_text = f"<semen>{enemas_text}</semen>\n"
                enemas_text = _(' [肠道]:') + enemas_text
                all_part_text_list.append(f" {enemas_text}")
            else:
                enemas_text = game_config.ui_text_data['dirty'][text_index]
                all_part_text_list.append(f" <{enemas_text}>")
        if target_character_data.dirty.enema_capacity:
            text_index = f"灌肠液量{str(target_character_data.dirty.enema_capacity)}"
            # 是否显示完整污浊文本
            if cache.all_system_setting.draw_setting[10]:
                enema_capacity_text = game_config.ui_text_data['dirty_full'][dirty_text_cid]
                enema_capacity_text = f"<semen>{enema_capacity_text}</semen>\n"
                enema_capacity_text = _(' [灌肠]:') + enema_capacity_text
                all_part_text_list.append(f" {enema_capacity_text}")
            else:
                enema_capacity_text = game_config.ui_text_data['dirty'][dirty_text_cid]
                all_part_text_list.append(f" <{enema_capacity_text}>")

        # 如果有腔内透视
        if visual_flag >= 2:
            # 如果有奶水，则显示奶水量
            if target_character_data.pregnancy.milk:
                lactation_text = _(" 乳汁量为{0}ml").format(target_character_data.pregnancy.milk)
                all_part_text_list.append(lactation_text)

        # 如果有生理透视，则显示当前生理周期、受精概率、欲望值
        if visual_flag >= 3:
            # 生理周期文本
            reproduction_period = target_character_data.pregnancy.reproduction_period
            now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
            period_cid = f"生理期{now_reproduction_period_type}"
            reproduction_text = game_config.ui_text_data['h_state'][period_cid]
            # 受精概率文本
            fertilization_text = _("受精概率{0}%").format(target_character_data.pregnancy.fertilization_rate)
            # 欲望值文本
            desire_text = _("欲望值{0}%").format(target_character_data.desire_point)
            # 组合文本
            now_text = _(" 当前为{0},{1},{2}").format(reproduction_text, fertilization_text, desire_text)
            all_part_text_list.append(now_text)

        # 阴茎位置文本，因为是直接调用ui文本，所以不需要调用翻译组件，下同
        if target_character_data.h_state.insert_position != -1:
            insert_text = " "
            # 显示阴茎位置的文本
            now_position_index = target_character_data.h_state.insert_position
            position_text_cid = f"阴茎位置{str(now_position_index)}"
            insert_position_text = game_config.ui_text_data['h_state'][position_text_cid]
            sex_position_index = character_data.h_state.current_sex_position
            # 如果是阴茎位置为阴道、子宫、后穴、尿道，且博士有体位数据，则显示性交姿势
            if now_position_index in {6,7,8,9} and sex_position_index != -1:
                sex_position_text_cid = f"体位{str(sex_position_index)}"
                sex_position_text = game_config.ui_text_data['h_state'][sex_position_text_cid]
                insert_text += _("以{0}").format(sex_position_text)
            insert_text += insert_position_text
            all_part_text_list.append(insert_text)

        # 绳子捆绑文本
        if target_character_data.h_state.bondage:
            bondage_id = target_character_data.h_state.bondage
            bondage_name = game_config.config_bondage[bondage_id].name
            bondage_text = _(" 被绳子捆成了{0}").format(bondage_name)
            all_part_text_list.append(bondage_text)

        # H道具文本
        now_text = ""
        body_item_dict = target_character_data.h_state.body_item
        for i in range(len(body_item_dict)):
            # print("status_type :",status_type)
            if body_item_dict[i][1]:
                status_text = body_item_dict[i][0]
                now_text += f" <{status_text}>"
        if now_text != "":
            all_part_text_list.append(now_text)

        # 避孕套文本
        if not len(character_data.h_state.condom_count):
            character_data.h_state.condom_count = [0, 0]
        if character_data.h_state.condom_count[0]:
            condom_text = _(" 用掉了{0}个避孕套，总精液量{1}ml").format(str(character_data.h_state.condom_count[0]), str(character_data.h_state.condom_count[1]))
            all_part_text_list.append(condom_text)

        # 香薰疗愈文本
        if target_character_data.sp_flag.aromatherapy != 0:
            aromatherapy_text = game_config.config_aromatherapy_recipes[target_character_data.sp_flag.aromatherapy].name
            all_part_text_list.append(f" <{aromatherapy_text}>")

        # 如果文本不为空，则加入到绘制列表中
        all_part_text = ""
        if len(all_part_text_list):
            self.draw_list.append(type_line)
            # 遍历总文本列表，最多每行有6个信息
            for i in range(len(all_part_text_list)):
                now_text = all_part_text_list[i]
                all_part_text += now_text
                if i % 6 == 0 and i != 0 and now_text[-1] != "\n":
                    all_part_text += "\n"
                # 如果文本的最后不是换行符，则加入换行符
                if i == len(all_part_text_list) - 1 and all_part_text[-1] != "\n":
                    all_part_text += "\n"

        # 获取富文本绘制对象
        now_draw = rich_text.get_rich_text_draw_panel(all_part_text)

        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

