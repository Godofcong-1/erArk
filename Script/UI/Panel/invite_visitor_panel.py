from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, map_handle, game_time, character_handle, character, character_handle
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import manage_basement_panel, recruit_panel
import random

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


def get_empty_guest_room_id():
    """
    判断是否有空闲客房，如果有的话返回客房id
    """
    # 遍历全部客房
    guest_rooms = [room_id for room_id in cache.rhodes_island.facility_open if 1200 < room_id < 1300]
    for room_id in guest_rooms:
        # 跳过未开放的客房
        if not cache.rhodes_island.facility_open[room_id]:
            continue
        room_name = game_config.config_facility_open[room_id].name
        # 遍历全部访客
        have_visitor_flag = False
        for chara_id in cache.rhodes_island.visitor_info:
            # 如果该房间已经有访客，则跳过
            if cache.character_data[chara_id].dormitory == room_name:
                have_visitor_flag = True
                break
        if have_visitor_flag:
            continue
        # 发现没有人住的房间，返回客房id
        else:
            return room_id
    # 如果没有空闲客房，则返回False
    return False

def update_invite_visitor():
    """刷新邀请访客栏位"""

    # 未选择邀请目标则跳过
    if cache.rhodes_island.invite_visitor[0] == 0:
        return

    # 如果超过100则进行结算
    if cache.rhodes_island.invite_visitor[1] >= 100:

        # 成功邀请时
        if settle_visitor_arrivals(visitor_id = cache.rhodes_island.invite_visitor[0]):
            cache.rhodes_island.invite_visitor[0] = 0
            cache.rhodes_island.invite_visitor[1] = 0

def visitor_to_operator(character_id: int):
    """
    访客留下成为干员
    Keyword arguments:
    character_id -- 角色id
    """

    character_data = cache.character_data[character_id]

    # flag置为已访问
    character_data.sp_flag.vistor = 2

    # 从访客列表中移除
    del cache.rhodes_island.visitor_info[character_id]

    # 如果满足设施开放的前提条件，则开放该设施
    for open_cid in game_config.config_facility_open:
        if game_config.config_facility_open[open_cid].NPC_id and game_config.config_facility_open[open_cid].NPC_id == character_data.adv:
            cache.rhodes_island.facility_open[open_cid] = True

    # 重新分配角色宿舍
    character_handle.new_character_get_dormitory(character_id)

def settle_visitor_arrivals(visitor_id = 0):
    """
    结算访客抵达
    visitor_id = 0 时，随机抽取一名访客
    return 0 时，没有访客抵达
    return 1 时，有访客抵达
    """
    from Script.UI.Panel import recruit_panel
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.style = "gold_enrod"

    # 判断是否有空闲客房
    if len(cache.rhodes_island.visitor_info) >= cache.rhodes_island.visitor_max:
        # 输出提示信息
        now_draw.text = _("\n ●由于没有空闲的客房，罗德岛没有接待到一名新抵达的访客\n")
        now_draw.draw()
        return 0
    else:
        # 随机抽取一名访客
        if visitor_id == 0:
            # 未招募的干员id列表
            not_recruit_npc_id_list = recruit_panel.find_recruitable_npc()
            # 根据当前基地的位置筛选出同国度且没有招募的干员
            now_country_id = cache.rhodes_island.current_location[0]
            now_country_npc_id_list = []
            # 开始筛选
            for npc_id in not_recruit_npc_id_list:
                if cache.character_data[npc_id].relationship.birthplace == now_country_id:
                    now_country_npc_id_list.append(npc_id)
            # 随机抽取一名访客
            if len(now_country_npc_id_list):
                visitor_id = random.choice(now_country_npc_id_list)
            else:
                return 0
        # 处理获得新访客
        character_handle.get_new_character(visitor_id, True)
        # 输出提示信息
        now_draw.text = _("\n ○【{0}】作为临时访客抵达了罗德岛\n").format(cache.character_data[visitor_id].name)
        now_draw.draw()
        return 1

def visitor_leave(character_id: int):
    """
    访客离开
    Keyword arguments:
    character_id -- 角色id
    """

    character_data = cache.character_data[character_id]

    # flag置为已访问
    character_data.sp_flag.vistor = 2

    # 从访客列表中移除
    del cache.rhodes_island.visitor_info[character_id]

    # 从已有干员列表中移除
    cache.npc_id_got.discard(character_id)

    # 位置初始化
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if character_id in cache.scene_data[scene_path_str].character_list:
        cache.scene_data[scene_path_str].character_list.remove(character_id)
    character_data.position = ["0", "0"]

def settle_visitor_arrivals_and_departures():
    """
    结算访客抵达和离开
    """
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.style = "gold_enrod"

    # 因罗德岛移动而产生的访客
    if cache.rhodes_island.base_move_visitor_flag:
        # 将flag重置为False
        cache.rhodes_island.base_move_visitor_flag = False
        settle_visitor_arrivals()

    # 根据时间而产生的访客
    add_day = game_time.count_day_for_datetime(cache.rhodes_island.last_visitor_time, cache.game_time)
    visitor_come_possibility = add_day * 3
    if random.randint(1, 100) <= visitor_come_possibility:
        # 刷新访客来访时间
        cache.rhodes_island.last_visitor_time = cache.game_time
        settle_visitor_arrivals()

    # 访客离开
    # 遍历全部访客
    now_visitor_id_list = list(cache.rhodes_island.visitor_info.keys())
    for visitor_id in now_visitor_id_list:
        character_data: game_type.Character = cache.character_data[visitor_id]
        # 判断是否已经超过停留时间
        if game_time.judge_date_big_or_small(cache.game_time, cache.rhodes_island.visitor_info[visitor_id]):
            # 计算访客留下概率
            tem_1, tem_2, stay_posibility = character.calculation_instuct_judege(0, visitor_id, _("访客留下"))
            # 遍历所有留下态度
            for attitude_id in game_config.config_visitor_stay_attitude:
                attitude_data = game_config.config_visitor_stay_attitude[attitude_id]
                if stay_posibility >= attitude_data.rate:
                    continue
                # 获得留下态度对应的文本
                stay_text = attitude_data.name
                break
            now_draw.text = _("\n 访客【{0}】预定的停留期限到了，她当前的留下意愿为：【{1}】").format(character_data.name, stay_text)
            # 随机计算访客是否留下
            if random.random() < stay_posibility:
                # 访客留下
                visitor_to_operator(visitor_id)
                # 输出提示信息
                now_draw.text += _("\n ○【{0}】决定放弃离开，留在罗德岛成为一名正式干员\n").format(character_data.name)
                now_draw.draw()
            else:
                # 访客离开
                visitor_leave(visitor_id)
                # 输出提示信息
                now_draw.text += _("\n ●【{0}】打包好行李，离开了罗德岛\n").format(character_data.name)
                now_draw.draw()


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
