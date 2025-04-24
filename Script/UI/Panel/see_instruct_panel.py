from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    get_text,
    cache_control,
    game_type,
    text_handle,
    value_handle,
    constant,
    py_cmd,
)
from Script.Design import handle_instruct, handle_premise, talk
from Script.Config import game_config
import time

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

def judge_single_instruct_filter(instruct_id: int, now_premise_data: dict, now_type: int, use_type_filter_flag: bool = True, skip_h_judge: bool = False, skip_not_h_judge: bool = False) -> tuple:
    """
    判断单个指令是否通过过滤\n
    Keyword arguments：\n
    instruct_id -- 指令id\n
    now_premise_data -- 当前记录的前提数据\n
    now_type -- 当前指令类型\n
    use_sub_type -- 是否使用子类过滤\n
    skip_h_judge -- 是否跳过H类指令判断\n
    skip_not_h_judge -- 是否跳过非H类指令判断\n
    Returns：\n
    bool -- 是否通过过滤\n
    now_premise_data -- 当前记录的前提数据\n
    """
    filter_judge = True
    # 如果该指令不存在，则置为存在
    if instruct_id not in cache.instruct_index_filter:
        cache.instruct_index_filter[instruct_id] = 1
    # 如果在过滤列表里，则过滤
    if not cache.instruct_index_filter[instruct_id]:
        filter_judge = False
    # H子类指令过滤
    if use_type_filter_flag and handle_premise.handle_now_show_h_instruct(0) and now_type == constant.InstructType.SEX:
        now_sub_type = constant.instruct_sub_type_data[instruct_id]
        if cache.instruct_sex_type_filter[now_sub_type] == 0:
            filter_judge = False
    # 前提判断
    if filter_judge:
        premise_judge = True
        if instruct_id in constant.instruct_premise_data:
            for premise in constant.instruct_premise_data[instruct_id]:
                # 忽略子类时（即非主界面），NPC逆推模式下则忽略NPC逆推的相关前提
                if use_type_filter_flag == False and handle_premise.handle_t_npc_active_h(0) and premise == 't_npc_not_active_h':
                    continue
                if premise in now_premise_data:
                    if now_premise_data[premise]:
                        continue
                    premise_judge = False
                    break
                # 如果跳过H类指令判断，则不进行H类前提判断
                elif skip_h_judge and premise == 'is_h':
                    now_premise_data[premise] = 1
                # 如果跳过非H类指令判断，则不进行非H类前提判断
                elif skip_not_h_judge and premise == 'not_h':
                    now_premise_data[premise] = 1
                else:
                    now_premise_value = handle_premise.handle_premise(premise, 0)
                    now_premise_data[premise] = now_premise_value
                    if not now_premise_value:
                        premise_judge = False
                        break
        # 如果前提不满足，则过滤
        if not premise_judge:
            filter_judge = False
    # 如果是debug模式，则强制通过
    if cache.debug_mode:
        filter_judge = True

    return filter_judge, now_premise_data


class SeeInstructPanel:
    """
    查看操作菜单面板
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        # 初始化指令类型过滤
        if cache.instruct_type_filter == {}:
            cache.instruct_type_filter[0] = 1
            cache.instruct_type_filter[1] = 1
            cache.instruct_type_filter[2] = 1
            cache.instruct_type_filter[3] = 1
            cache.instruct_type_filter[4] = 1
        for instruct_type in game_config.config_instruct_type:
            if instruct_type not in cache.instruct_type_filter:
                cache.instruct_type_filter[instruct_type] = 0
        cache.instruct_type_filter[6] = 1

        # 初始化性爱子类类型过滤
        for instruct_type in game_config.config_instruct_sex_type:
            if instruct_type not in cache.instruct_sex_type_filter:
                if instruct_type == 0:
                    cache.instruct_sex_type_filter[instruct_type] = 1
                else:
                    cache.instruct_sex_type_filter[instruct_type] = 0

        # 初始化命令过滤
        if cache.instruct_index_filter == {}:
            for now_type in cache.instruct_type_filter:
                for instruct in constant.instruct_type_data[now_type]:
                    cache.instruct_index_filter[instruct] = 1

    def draw(self):
        """绘制操作菜单面板"""
        start_instruct = time.time()
        self.return_list = []

        line = draw.LineDraw("-.-", self.width)
        line.draw()
        fix_draw = draw.NormalDraw()
        # 根据是否是显示H指令，进行指令类型过滤相关变量的区分
        if handle_premise.handle_now_show_h_instruct(0):
            instruct_type_len = len(cache.instruct_sex_type_filter) + 1
            now_instruct_type_list = cache.instruct_sex_type_filter
            now_instruct_config = game_config.config_instruct_sex_type
        else:
            instruct_type_len = len(cache.instruct_type_filter) - 1
            now_instruct_type_list = cache.instruct_type_filter
            now_instruct_config = game_config.config_instruct_type
        # 排版修正用的宽度
        fix_width = int(
            (self.width - int(self.width / instruct_type_len) * instruct_type_len) / 2
        )
        fix_draw.width = fix_width
        fix_draw.text = " " * fix_width
        fix_draw.draw()
        for now_type in now_instruct_type_list:
            # 正常模式下，跳过系统类和性爱类的大类选择按钮
            if handle_premise.handle_now_show_non_h_instruct(0):
                if now_type == constant.InstructType.SYSTEM:
                    continue
                if now_type == constant.InstructType.SEX:
                    continue
            now_config = now_instruct_config[now_type]
            # 已选择的指令类型变成对应颜色
            if now_instruct_type_list[now_type]:
                now_button = draw.CenterButton(
                    f"[{now_config.name}]",
                    now_config.name,
                    self.width / (instruct_type_len - 1),
                    " ",
                    now_instruct_config[now_type].color,
                    "standard",
                    cmd_func=self.change_filter,
                    args=(now_type,),
                )
            else:
                now_button = draw.CenterButton(
                    f"[{now_config.name}]",
                    now_config.name,
                    self.width / (instruct_type_len - 1),
                    normal_style = "deep_gray",
                    cmd_func=self.change_filter,
                    args=(now_type,),
                )
            now_button.width = int(self.width / (instruct_type_len - 1))
            self.return_list.append(now_button.return_text)
            now_button.draw()

        # 如果交互对象是临盆、产后或婴儿的话，则在常规指令类里不显示技艺、猥亵、H类指令
        if handle_premise.handle_t_parturient_1(0) or handle_premise.handle_t_postpartum_1(0) or handle_premise.handle_t_baby_1(0):
            cache.instruct_type_filter[4] = 0
            cache.instruct_type_filter[5] = 0
            cache.instruct_type_filter[6] = 0

        line_feed.draw()
        line = draw.LineDraw("~..", self.width)
        line.draw()
        now_instruct_list = []
        now_premise_data = {}
        # 遍历指令过滤
        for now_type in cache.instruct_type_filter:
            # 当前类没有开启的指令则过滤
            if not cache.instruct_type_filter[now_type]:
                continue
            # 不在H模式中则过滤H指令
            if handle_premise.handle_now_show_non_h_instruct(0) and now_type == constant.InstructType.SEX:
                continue
            # 男隐或双隐中对非H角色无法使用指令
            if handle_premise.handle_hidden_sex_mode_3_or_4(0) and handle_premise.handle_target_not_in_hidden_sex_mode(0):
                continue
            # 需要是注册过的指令类型，或者是系统指令
            if now_type in constant.instruct_type_data or now_type == constant.InstructType.SYSTEM:
                for instruct in constant.instruct_type_data[now_type]:
                    # 隐奸中且显示非H时，跳过not_h的前提
                    if handle_premise.handle_show_non_h_in_hidden_sex(0):
                        filter_judge, now_premise_data = judge_single_instruct_filter(instruct, now_premise_data, now_type, skip_not_h_judge=True)
                    # 检测指令是否通过过滤
                    else:
                        filter_judge, now_premise_data = judge_single_instruct_filter(instruct, now_premise_data, now_type)
                    if filter_judge:
                        now_instruct_list.append(instruct)
        now_instruct_list.sort()
        instruct_group = value_handle.list_of_groups(now_instruct_list, 5)
        now_draw_list = []
        system_draw_list = []
        # 遍历指令绘制
        for instruct_list in instruct_group:
            for instruct_id in instruct_list:
                instruct_name = constant.handle_instruct_name_data[instruct_id]
                id_text = text_handle.id_index(instruct_id)
                now_text = f"{id_text}{instruct_name}"
                now_draw = draw.LeftButton(
                    now_text,
                    str(instruct_id),
                    int(self.width / 5),
                    cmd_func=self.handle_instruct,
                    args=(instruct_id,),
                )
                # 根据指令类型赋予不同的颜色
                for instruct_type in constant.instruct_type_data:
                    if instruct_id in constant.instruct_type_data[instruct_type]:
                        now_draw.normal_style = game_config.config_instruct_type[instruct_type].color
                        break
                # 如果是H模式，则单独读取H子类的颜色
                if handle_premise.handle_now_show_h_instruct(0):
                    now_sub_type = constant.instruct_sub_type_data[instruct_id]
                    now_draw.normal_style = game_config.config_instruct_sex_type[now_sub_type].color
                # 系统指令单独加入系统指令列表
                if instruct_id in constant.instruct_type_data[constant.InstructType.SYSTEM]:
                    system_draw_list.append(now_draw)
                else:
                    now_draw_list.append(now_draw)
                self.return_list.append(now_draw.return_text)
        # 角色自定义特殊指令检测与绘制
        from Script.UI.Panel import event_option_panel
        len_son_event_list, son_event_list = event_option_panel.get_target_chara_diy_instruct(0)
        if len_son_event_list:
            count = 0
            for event_id in son_event_list:
                count += 1
                # 获取事件数据
                event_data = game_config.config_event[event_id]
                pl_character_data = cache.character_data[0]
                target_character_data = cache.character_data[pl_character_data.target_character_id]
                chara_adv = target_character_data.adv
                # 获取选项文本
                option_text = event_data.text.split("|")[0]
                option_text = talk.code_text_to_draw_text(option_text, 0)
                now_text = f"[{chara_adv}_{count}]{option_text}"
                return_text = f"{chara_adv}_{count}"
                # 绘制按钮
                now_draw = draw.LeftButton(
                    now_text,
                    return_text,
                    int(self.width / 5),
                    cmd_func=self.handle_chara_diy_instruct,
                    args=(event_id,),
                )
                # 检查是否要使用口上颜色
                if target_character_data.text_color:
                    now_draw.normal_style = target_character_data.name
                now_draw_list.append(now_draw)
                self.return_list.append(now_draw.return_text)
        now_draw = panel.DrawTextListPanel()
        now_draw.set(now_draw_list, self.width, 5)
        # now_draw = panel.VerticalDrawTextListGroup(self.width)
        # now_group = value_handle.list_of_groups(now_draw_list, 5)
        # now_draw.draw_list = now_group
        now_draw.draw()
        line_feed.draw()
        line = draw.LineDraw("-.-", self.width)
        line.draw()
        system_draw = panel.DrawTextListPanel()
        system_draw.set(system_draw_list, self.width, 5)
        system_draw.draw()

    def change_filter(self, now_type: int):
        """
        更改指令类型过滤状态
        Keyword arguments:
        now_type -- 指令类型
        """
        if handle_premise.handle_now_show_h_instruct(0):
            if cache.instruct_sex_type_filter[now_type]:
                cache.instruct_sex_type_filter[now_type] = 0
            else:
                cache.instruct_sex_type_filter[now_type] = 1
        else:
            if cache.instruct_type_filter[now_type]:
                cache.instruct_type_filter[now_type] = 0
            else:
                cache.instruct_type_filter[now_type] = 1

    def handle_instruct(self, instruct_id: int):
        """
        处理玩家操作指令
        Keyword arguments:
        instruct_id -- 指令id
        """
        py_cmd.clr_cmd()
        # 指令名称绘制
        instruct_name = constant.handle_instruct_name_data[instruct_id]
        now_draw_1 = draw.NormalDraw()
        now_draw_1.text = f"{instruct_name}"
        # 如果是重复指令，则加上连续标记
        if len(cache.pl_pre_status_instruce) >= 2:
            if cache.pl_pre_status_instruce[-1] == cache.pl_pre_status_instruce[-2]:
                now_draw_1.text += _("(连续)")
        now_draw_1.text += "\n"
        now_draw_1.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        # 指令结算
        handle_instruct.handle_instruct(instruct_id)

    def handle_chara_diy_instruct(self, event_id: str):
        """
        处理角色自定义指令
        Keyword arguments:
        event_id -- 事件id
        """
        event_data = game_config.config_event[event_id]
        py_cmd.clr_cmd()
        # 指令名称绘制
        option_text = event_data.text.split("|")[0]
        option_text = talk.code_text_to_draw_text(option_text, 0)
        instruct_name = option_text
        now_draw_1 = draw.NormalDraw()
        now_draw_1.text = f"{instruct_name}"
        # 如果是重复指令，则加上连续标记
        if len(cache.pl_pre_status_instruce) >= 2:
            if cache.pl_pre_status_instruce[-1] == cache.pl_pre_status_instruce[-2]:
                now_draw_1.text += _("(连续)")
        now_draw_1.text += "\n"
        now_draw_1.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()
        # 指令结算
        pl_character_data = cache.character_data[0]
        pl_character_data.event.event_id = event_id
        pl_character_data.event.chara_diy_event_flag = True
        handle_instruct.handle_instruct(constant.Instruct.CHARA_DIY_INSTRUCT)

