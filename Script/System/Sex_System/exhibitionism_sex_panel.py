from typing import List
from types import FunctionType
from Script.System.Instruct_System import handle_instruct
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import normal_config
from Script.Design import handle_premise, map_handle

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

def update_exhibiionism_sex_mode():
    """更新露出H模式"""
    character_data: game_type.Character = cache.character_data[0]
    # 如果不在露出模式则直接返回
    if character_data.sp_flag.exhibitionism_sex_mode == 0:
        return
    # 如果当前周围有人
    if handle_premise.handle_scene_over_two(0):
        # 如果当前周围有人清醒
        if handle_premise.handle_scene_others_conscious(0):
            new_mode = 3
        # 否则
        else:
            new_mode = 4
    # 如果当前周围无人
    else:
        # 如果在室外
        if handle_premise.handle_place_outdoor(0):
            new_mode = 2
        # 否则在室内
        else:
            new_mode = 1
    # 更新模式
    character_data.sp_flag.exhibitionism_sex_mode = new_mode
    # 获取场景内露出对象
    now_scene_character_list = map_handle.get_chara_now_scene_all_chara_id_list(0,remove_own_character=True)
    for chara_id in now_scene_character_list:
        target_character_data: game_type.Character = cache.character_data[chara_id]
        if target_character_data.sp_flag.exhibitionism_sex_mode != 0:
            target_character_data.sp_flag.exhibitionism_sex_mode = new_mode
            break


class Select_Exhibitionism_Sex_Mode_Panel:
    """
    用于选择露出H模式的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int, sex_be_discovered_flag: bool = False):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.sex_be_discovered_flag: bool = sex_be_discovered_flag
        """ 是否是从被发现面板跳转过来 """
        self.now_panel = _("选择露出H模式")
        """ 当前绘制的页面 """

    def draw(self) -> None:
        """绘制对象"""

        title_text = _("选择露出H模式")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        mode_desc_list = [
            _("[1]无人室内露出：在场景内没有其他人，且没有锁门的室内进行露出H"),
            _("[2]无人室外露出：在场景内没有其他人的户外进行露出H"),
            _("[3]人前露出：在场景内有其他人的情况下，直接进行露出H"),
            _("[4]无意识人前露出：在场景内有其他人，且其他人都在无意识的情况下进行露出H"),
        ]

        info_text = _("\n请选择要进行的露出H模式：\n\n")

        while 1:
            return_list: List[str] = []
            title_draw.draw()

            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()

            for index, button_text in enumerate(mode_desc_list):
                mode_id = index + 1
                can_use = self._mode_available(mode_id)
                if cache.debug_mode:
                    can_use = True
                if can_use:
                    button_draw = draw.LeftButton(
                        button_text,
                        str(mode_id),
                        self.width,
                        cmd_func=self.select_this_mode,
                        args=(mode_id,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                else:
                    now_draw = draw.NormalDraw()
                    now_draw.text = button_text
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                line_feed.draw()

            line_feed.draw()
            line_feed.draw()
            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _( "返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_this_mode(self, mode_id: int) -> None:
        """选择露出H模式"""
        from Script.Design import instuct_judege
        character_data: game_type.Character = cache.character_data[0]
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]

        # 判断是否成功邀请露出
        if instuct_judege.calculation_instuct_judege(0, target_character_id, _("露出"))[0]:
            character_data.sp_flag.exhibitionism_sex_mode = mode_id
            target_character_data.sp_flag.exhibitionism_sex_mode = mode_id
            target_character_data.sp_flag.is_follow = 0
            handle_premise.settle_chara_unnormal_flag(target_character_id, 3)
            now_scene_character_list = map_handle.get_chara_now_scene_all_chara_id_list(0)
            other_chara_count = len(now_scene_character_list) - 2
            # 成就初始化
            cache.achievement.exhibitionism_sex_record = {1: mode_id, 2: other_chara_count, 3: 0, 4: 0}
            # 如果是从被发现面板跳转过来
            if self.sex_be_discovered_flag:
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.OTHER_SEX_BE_FOUND_TO_EXHIBITIONISM_SEX)
            # 否则正常结算
            else:
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.ASK_EXHIBITIONISM_SEX)
        else:
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n邀请露出失败\n")
            now_draw.draw()
            # 如果是从被发现面板跳转过来
            if self.sex_be_discovered_flag:
                character_data.behavior.behavior_id = constant.Behavior.H_INTERRUPT
            # 否则正常结算
            else:
                handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.ASK_EXHIBITIONISM_SEX_FAIL)

    @staticmethod
    def _mode_available(mode_id: int) -> bool:
        """检查指定模式是否可用，默认恒为True，后续由前提判定补充"""
        if mode_id == 1:
            # 无人室内露出
            if handle_premise.handle_scene_only_two(0) and handle_premise.handle_place_door_open(0) and handle_premise.handle_place_indoor(0):
                return True
        elif mode_id == 2:
            # 无人室外露出
            if handle_premise.handle_scene_only_two(0) and handle_premise.handle_place_outdoor(0):
                return True
        elif mode_id == 3:
            # 人前露出
            if handle_premise.handle_scene_over_two(0) and handle_premise.handle_scene_others_conscious(0):
                return True
        elif mode_id == 4:
            # 无意识人前露出
            if handle_premise.handle_scene_over_two(0) and handle_premise.handle_scene_all_others_unconscious_or_sleep(0):
                return True
        return False
