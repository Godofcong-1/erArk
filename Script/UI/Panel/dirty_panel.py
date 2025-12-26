from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, rich_text
from Script.Design import map_handle, clothing, attr_calculation
from Script.Design import handle_premise
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
        self.draw_list: List = []
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
                target_character_data.dirty.body_semen[i] = [part_name,0,0,0]

            # 最开始先计算腹部整体的精液量累积
            if i in [5,7,8,15]:
                abdomen_all_semen += target_character_data.dirty.body_semen[i][1]

            # 判定部位是否被衣服遮挡，且没有透视中
            if i not in no_cloth_body_list and visual_flag == 0:
                continue

            # 然后腔内透视判定
            if visual_flag <= 1 and i in {7,9,15}:
                continue

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

            # 处子血判定
            if i == 6 and visual_flag >= 2:
                # 今日破处
                if not target_character_data.talent[0] and handle_premise.handle_first_sex_in_today(character_data.target_character_id):
                    # 是否显示完整污浊文本
                    dirty_text_cid = "破处血1"
                    if cache.all_system_setting.draw_setting[10]:
                        dirty_text = game_config.ui_text_data['dirty_full'][dirty_text_cid]
                        dirty_text += '\n'
                        all_part_text_list.append(f"  [破处]:{dirty_text}")
                    else:
                        dirty_text = game_config.ui_text_data['dirty'][dirty_text_cid]
                        all_part_text_list.append(f" <{dirty_text}>")

            # 尿液污浊
            if i == 9:
                if handle_premise.handle_urinate_le_12(character_data.target_character_id):
                    text_index = "尿液0"
                elif handle_premise.handle_urinate_le_49(character_data.target_character_id):
                    text_index = "尿液1"
                elif handle_premise.handle_urinate_le_79(character_data.target_character_id):
                    text_index = "尿液2"
                elif handle_premise.handle_urinate_ge_125(character_data.target_character_id) == 0:
                    text_index = "尿液3"
                else:
                    text_index = "尿液4"
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
                enema_capacity_text = game_config.ui_text_data['dirty_full'][text_index]
                enema_capacity_text = f"<semen>{enema_capacity_text}</semen>\n"
                enema_capacity_text = _(' [灌肠]:') + enema_capacity_text
                all_part_text_list.append(f" {enema_capacity_text}")
            else:
                enema_capacity_text = game_config.ui_text_data['dirty'][text_index]
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
        # 情趣玩具档位文本
        sex_toy_level = target_character_data.sp_flag.sex_toy_level
        if sex_toy_level == 0:
            sex_toy_lv_text = _("(关)")
        elif sex_toy_level == 1:
            sex_toy_lv_text = _("(弱)")
        elif sex_toy_level == 2:
            sex_toy_lv_text = _("(中)")
        else:
            sex_toy_lv_text = _("(强)")
        # 身体道具数据
        body_item_dict = target_character_data.h_state.body_item
        for i in range(len(body_item_dict)):
            # print("status_type :",status_type)
            if body_item_dict[i][1]:
                body_item_data = game_config.config_body_item[i]
                status_text = body_item_dict[i][0]
                # 如果是猥亵型装备且当前不在H中，则显示档位文本
                if body_item_data.type == 2:
                    status_text += sex_toy_lv_text
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
        rich_text_draw_list = rich_text.get_rich_text_draw_list(all_part_text)
        # 加入到绘制列表中
        self.draw_list.extend(rich_text_draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

