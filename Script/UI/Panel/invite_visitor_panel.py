from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, map_handle, game_time
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import manage_basement_panel, recruit_panel

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


class Invite_Visitor_Panel:
    """
    用于邀请访客的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("邀请访客")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("邀请访客")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = ""
            now_text += _(" 当前的访客上限为：{0}人\n").format(cache.rhodes_island.visitor_max)
            if len(cache.rhodes_island.visitor_info) == 0:
                now_text += _(" 目前没有访客\n")
            else:
                now_text += _(" 目前的访客有：")
                for chara_id in cache.rhodes_island.visitor_info:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    live_room = character_data.dormitory.split("\\")[-1]
                    leav_time = game_time.get_date_until_day(cache.rhodes_island.visitor_info[chara_id])
                    now_text += _(" [{0}]{1}，居住房间：{2}，离开{3}\n").format(str(character_data.adv).rjust(4,'0'), character_data.name, live_room, leav_time)
                now_text += f"\n"

            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            # 邀请目标
            now_level = cache.rhodes_island.facility_level[13]
            now_text = _("\n 当前邀请目标：")
            if now_level <= 1:
                now_text += _(" 需要访客区至少为2级才可以邀请访客\n")
            elif cache.rhodes_island.invite_visitor[0] == 0:
                now_text += _(" 无")
            else:
                chara_id = cache.rhodes_island.invite_visitor[0]
                character_data: game_type.Character = cache.character_data[chara_id]
                now_text += f" [{chara_id}]{character_data.name}"

                # 邀请进度
                now_text += _("\n 邀请进度：{0}%").format(cache.rhodes_island.invite_visitor[1])
                # 邀请效率加成
                all_effect = 0
                now_text += _("\n 邀请效率加成：")

                # 去掉玩家
                cache.npc_id_got.discard(0)
                # 去掉访客
                id_list = [i for i in cache.npc_id_got if i not in cache.rhodes_island.visitor_info]
                for chara_id in id_list:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    # 找到职业是外交官的
                    if character_data.work.work_type == 131:
                        character_data: game_type.Character = cache.character_data[chara_id]
                        character_effect = 5 * attr_calculation.get_ability_adjust(character_data.ability[40])
                        now_text += f" {character_data.name}"
                        # 邀请效率
                        now_text += _("(话术lv{0}:+{1}%)").format(character_data.ability[40], round(character_effect, 1))
                        all_effect += character_effect
                now_text += f" = {round(all_effect, 1)}%"
            all_info_draw.text = now_text
            all_info_draw.draw()

            line_feed.draw()
            button_text = _("[001]人员增减")
            button_draw = draw.LeftButton(
                _(button_text),
                _(button_text),
                self.width,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=self.width
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw()
            if now_level >= 2:
                button_text = _("[002]目标选择")
                button_draw = draw.LeftButton(
                    _(button_text),
                    _(button_text),
                    self.width,
                    cmd_func=self.select_target,
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()

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


    def select_target(self):
        """选择邀请目标"""
        from Script.Design import handle_premise

        while 1:
            line = draw.LineDraw("-", window_width)
            line.draw()
            return_list = []
            all_info_draw = draw.NormalDraw()

            # 邀请目标
            now_text = _("\n 当前邀请目标：")
            if cache.rhodes_island.invite_visitor[0] == 0:
                now_text += _(" 无\n")
            else:
                chara_id = cache.rhodes_island.invite_visitor[0]
                character_data: game_type.Character = cache.character_data[chara_id]
                now_text += f" [{str(character_data.adv).rjust(4,'0')}]{character_data.name}\n"

            # 访客区设施信息
            now_level = cache.rhodes_island.facility_level[13]
            facility_cid = game_config.config_facility_effect_data[_("访客区")][int(now_level)]
            facility_effect = game_config.config_facility_effect[facility_cid].effect
            now_text += _(" 访客区等级：{0}\n").format(now_level)
            now_text += _(" 访客停留时长：{0}天\n").format(facility_effect)
            now_text += _(" 访客数量上限：{0}人\n").format(cache.rhodes_island.visitor_max)

            # 可邀请范围
            now_country_id = cache.rhodes_island.current_location[0]
            now_country_name = game_config.config_birthplace[now_country_id].name
            if now_level == 2:
                now_invitation_range = now_country_name
                now_text += _(" 可邀请范围：{0}\n\n").format(now_invitation_range)
            elif now_level == 3:
                # 临近地点
                map_path_str = map_handle.get_map_system_path_str_for_list(['泰拉'])
                map_data: game_type.Map = cache.map_data[map_path_str]
                path_edge = map_data.path_edge  
                near_scene_path = path_edge[now_country_name].copy()
                # 仅需要keys
                now_invitation_range = list(near_scene_path.keys())
                now_text += _(" 可邀请范围：")
                all_country_id_list = []
                for country_name in now_invitation_range:
                    now_text += f" {country_name}"
                    # 寻找该国家的id
                    for country_id in game_config.config_birthplace:
                        if game_config.config_birthplace[country_id].name == country_name:
                            all_country_id_list.append(country_id)
                            break
                now_text += f"\n\n"
            elif now_level >= 4:
                now_invitation_range = _("全泰拉")
                now_text += _(" 可邀请范围：{0}\n\n").format(now_invitation_range)

            # 可邀请目标
            recruitable_npc_id_list = recruit_panel.find_recruitable_npc()
            target_id_list = []
            for chara_id in recruitable_npc_id_list:
                # 本地
                if now_level == 2:
                    character_data = cache.character_data[chara_id]
                    # 出生地是当前所在地的角色
                    if character_data.relationship.birthplace != now_country_id:
                        continue
                    else:
                        target_id_list.append(chara_id)
                # 临近
                elif now_level == 3:
                    character_data = cache.character_data[chara_id]
                    # 出生地在地点列表中的角色
                    if character_data.relationship.birthplace not in all_country_id_list:
                        continue
                    else:
                        target_id_list.append(chara_id)
                # 全泰拉招募
                elif now_level >= 4:
                    target_id_list.append(chara_id)

            # 可邀请目标绘制
            if len(target_id_list):
                now_text += _(" 当前可邀请目标有（更改后会重置邀请进度）：")
                all_info_draw.text = now_text
                all_info_draw.draw()
                line_feed.draw()
                chara_id_count = 0
                for chara_id in target_id_list:
                    chara_id_count += 1
                    character_data: game_type.Character = cache.character_data[chara_id]
                    # 均绘制为可选按钮
                    button_text = f" [{str(character_data.adv).rjust(4,'0')}]{character_data.name}"
                    button_draw = draw.LeftButton(
                        button_text,
                        button_text,
                        int(len(button_text)*2),
                        cmd_func=self.change_invite_target,
                        args=chara_id
                        )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    # 每行5个
                    if chara_id_count % 8 == 0:
                        line_feed.draw()
            else:
                now_text += _(" 当前没有可邀请目标\n")
                all_info_draw.text = now_text
                all_info_draw.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def change_invite_target(self, chara_id: int):
        """更改邀请目标"""
        cache.rhodes_island.invite_visitor[0] = chara_id
        cache.rhodes_island.invite_visitor[1] = 0
