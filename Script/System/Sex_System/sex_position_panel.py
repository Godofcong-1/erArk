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
from Script.Design import attr_calculation, map_handle

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

class Sex_Position_Panel:
    """
    H中被发现后的选择面板
    Keyword arguments:
    width -- 绘制宽度
    character_id -- 触发事件的角色id
    """

    def __init__(self, width: int, sex_type: int = 1, change_position: bool = False) -> None:
        """初始化绘制对象"""
        self.width = width
        """ 绘制宽度 """
        self.sex_type = sex_type
        """ 性交类型，默认1为阴道性交，2为子宫口性交，3为子宫性交，4为肛门性交，5为尿道性交 """
        self.change_position = change_position
        """ 是否为切换体位 """

    def draw(self) -> None:
        """绘制面板"""

        title_draw = draw.TitleLineDraw(_("性交体位"), self.width)
        # 获取当前角色数据
        character_data: game_type.Character = cache.character_data[0]
        pl_tec_lv = character_data.ability[76]
        # 当前性交体位
        now_sex_position_id = character_data.h_state.current_sex_position
        # 当前房间的家具等级
        now_position = character_data.position
        now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
        now_scene_furniture = cache.scene_data[now_scene_str].have_furniture

        while 1:
            return_list = []
            title_draw.draw()

            line_feed.draw()

            # 遍历性交体位数据
            for sex_position_id in game_config.config_sex_position_data:
                # 跳过无
                if sex_position_id <= 0:
                    continue
                sex_position_data = game_config.config_sex_position_data[sex_position_id]
                sex_position_id_text = str(sex_position_id).rjust(2,'0')
                sex_position_name = attr_calculation.pad_display_width(sex_position_data.name, 10)
                sex_position_furniture_req = sex_position_data.furniture_req
                sex_position_skill_req = sex_position_data.skill_req
                sex_position_stamina_cost = sex_position_data.stamina_cost
                # 绘制文本
                sex_position_text = f"[{sex_position_id_text}]{sex_position_name}："
                # 用于判断是否可以选择该体位
                cant_flag = False

                # 已选判定
                if sex_position_id == now_sex_position_id:
                    sex_position_text += _("(当前体位)")
                    cant_flag = True

                # 显示体力消耗程度
                if sex_position_stamina_cost == 1:
                    sex_position_text += _("(体力消耗小)")
                elif sex_position_stamina_cost == 2:
                    sex_position_text += _("(体力消耗中)")
                elif sex_position_stamina_cost == 3:
                    sex_position_text += _("(体力消耗大)")

                # 地点判定
                if sex_position_furniture_req > now_scene_furniture:
                    if sex_position_furniture_req == 1:
                        sex_position_text += _("(需要房间内有桌椅等级的家具)")
                    elif sex_position_furniture_req == 3:
                        sex_position_text += _("(需要房间内有床铺等级的家具)")
                    cant_flag = True

                # 技巧判定
                if sex_position_skill_req > pl_tec_lv:
                    sex_position_text += _("(需要博士腰技至少为{0}级)").format(sex_position_skill_req)
                    cant_flag = True

                # 体位说明
                sex_position_text += sex_position_data.info

                # 当前的体位不可选择
                if sex_position_id == now_sex_position_id:
                    text_draw = draw.NormalDraw()
                    text_draw.text = sex_position_text
                    text_draw.style = 'gold_enrod'
                    text_draw.draw()
                # 如果不能施展则不显示按钮，仅打印灰色文本
                elif cant_flag:
                    text_draw = draw.NormalDraw()
                    text_draw.text = sex_position_text
                    text_draw.style = 'deep_gray'
                    text_draw.draw()
                # 如果可以施展则显示按钮
                else:
                    button_draw = draw.LeftButton(
                        _(sex_position_text),
                        _(str(sex_position_id)),
                        self.width,
                        cmd_func=self.select_sex_position,
                        args=(sex_position_id,),
                        )
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
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_sex_position(self, sex_position_id):
        """结算选择的性交体位"""
        from Script.Design import handle_instruct
        sex_position_data = game_config.config_sex_position_data[sex_position_id]
        character_data: game_type.Character = cache.character_data[0]
        if self.change_position:
            # 切换体位的情况则记录该数据
            character_data.h_state.pre_sex_position = character_data.h_state.current_sex_position
        else:
            # 不是切换体位则重置该数据
            character_data.h_state.pre_sex_position = -1
        # 阴道性交
        if self.sex_type == 1:
            behavior_id = sex_position_data.vaginal_sex_behavior_id
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, judge = _("性交"), force_taget_wait=True)
        # 子宫口性交的情况
        elif self.sex_type == 2:
            behavior_id = sex_position_data.cervix_sex_behavior_id
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, judge = _("U性交"), force_taget_wait=True)
        # 子宫性交的情况
        elif self.sex_type == 3:
            behavior_id = sex_position_data.womb_sex_behavior_id
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, judge = _("U性交"), force_taget_wait=True)
        # 肛门性交的情况
        elif self.sex_type == 4:
            behavior_id = sex_position_data.anal_sex_behavior_id
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, judge = _("A性交"), force_taget_wait=True)
        # 尿道性交的情况
        elif self.sex_type == 5:
            behavior_id = sex_position_data.urethral_sex_behavior_id
            handle_instruct.chara_handle_instruct_common_settle(behavior_id, judge = _("U性交"), force_taget_wait=True)
