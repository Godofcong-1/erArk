from typing import List, Tuple
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    text_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation
from Script.UI.Panel import hypnosis_panel

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

def get_now_class_tip(character_id: int):
    """
    取角色当前的上课信息，供 <课> / <翘> 状态标识使用（Plan 22）
    ⚠️ 只在角色**此刻正在上课/授课**时返回内容，而不是"本节有排课"——状态标识描述的是此刻的状态，
       与 <跟> <饿> 的口径一致。孩子因体力不足去休息、或被叫走跟随时不该显示 <课>
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    tuple or None -- 不在上课中则为None，否则为 (是否翘课bool, 悬停提示文本str)
    """
    from Script.System.Education_System import schedule_handle
    from Script.Design import game_time

    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    period = game_time.get_class_period(character_id)

    # 翘课中：本该上课的节次里挂着翘课flag
    if growth_data is not None and growth_data.skip_class_flag and period != -1:
        now_course = schedule_handle.get_now_course(character_id)
        if now_course is not None:
            return True, _("翘课中：本该上 {0}（第{1}节）").format(
                get_course_text(now_course), period + 1)
        return True, _("翘课中（第{0}节）").format(period + 1)

    behavior_id = character_data.behavior.behavior_id
    # 教师视角：正在授课
    if behavior_id == constant.Behavior.TEACH:
        teaching = schedule_handle.get_now_teaching(character_id)
        if teaching is not None:
            ability_name = game_config.config_ability[teaching["ability_id"]].name
            return False, _("授课中：{0}·{1}｜{2}｜第{3}节").format(
                schedule_handle.COURSE_TYPE_NAME.get(teaching["course_type"], _("课")),
                ability_name, teaching["classroom"], teaching["period"] + 1)
        return False, _("授课中")

    # 学生视角：正在听课或自习（自习是本节没有可用教师时的降级，仍然算在上课中）
    if behavior_id in {constant.Behavior.ATTENT_CLASS, constant.Behavior.SELF_STUDY}:
        now_course = schedule_handle.get_now_course(character_id)
        if now_course is None:
            return False, _("上课中")
        text = get_course_text(now_course)
        # ⚠️ 只有班级式的教室课才有"教师缺席降级自习"的说法；
        #    体育/兴趣/实习课本就没有指派教师（teacher_id 恒为 -1），不能误报成自习
        if now_course["course_type"] not in schedule_handle.CLASSROOM_COURSE_TYPE_SET:
            return False, _("{0}｜第{1}节").format(text, period + 1)
        # 本节没有教师、或人已经在自习了，都按自习显示
        if now_course["teacher_id"] == -1 or behavior_id == constant.Behavior.SELF_STUDY:
            return False, _("自习·{0}｜本节无教师，经验减半｜第{1}节").format(text, period + 1)
        teacher_data: game_type.Character = cache.character_data[now_course["teacher_id"]]
        return False, _("{0}｜授课：{1}｜第{2}节").format(text, teacher_data.name, period + 1)

    # 个人式课型：人在该课的地点上，就算在上课
    # ⚠️ 这三种课执行的是既有行为（打木桩、下棋、跟岗），没有专属的"上课"行为可认，
    #    只能靠"本节排了这门课 + 人确实在那个地点"来判定
    if period != -1:
        now_course = schedule_handle.get_now_course(character_id)
        if now_course is not None and now_course["course_type"] not in schedule_handle.CLASSROOM_COURSE_TYPE_SET:
            from Script.Design import map_handle

            to_place = schedule_handle.get_course_place(now_course)
            if to_place and map_handle.get_map_system_path_str_for_list(character_data.position) ==                     map_handle.get_map_system_path_str_for_list(to_place):
                text = get_course_text(now_course)
                # 实习课再补一句导师是谁：导师不预先指派，到点看现场谁在岗
                if now_course["course_type"] == schedule_handle.COURSE_TYPE_INTERN:
                    mentor_id = schedule_handle.get_intern_mentor(character_id, now_course["target"])
                    if mentor_id == -1:
                        return False, _("{0}｜本节无人在岗，降为见习｜第{1}节").format(text, period + 1)
                    mentor_data: game_type.Character = cache.character_data[mentor_id]
                    return False, _("{0}｜带教：{1}｜第{2}节").format(text, mentor_data.name, period + 1)
                return False, _("{0}｜第{1}节").format(text, period + 1)

    return None


def get_course_text(now_course: dict) -> str:
    """
    把一条课程信息拼成"课型·科目｜地点"的可读文本
    Keyword arguments:
    now_course -- schedule_handle.get_now_course() 的返回值
    Return arguments:
    str -- 可读文本
    """
    from Script.System.Education_System import schedule_handle

    type_name = schedule_handle.COURSE_TYPE_NAME.get(now_course["course_type"], _("课"))
    # 班级式课：科目与教室都查得到
    if now_course["course_type"] in schedule_handle.CLASSROOM_COURSE_TYPE_SET:
        if now_course["ability_id"] > 0:
            ability_name = game_config.config_ability[now_course["ability_id"]].name
            return "{0}·{1}｜{2}".format(type_name, ability_name, now_course["classroom"])
        return "{0}｜{1}".format(type_name, now_course["classroom"])
    # 个人式课：目标本身就是地点名或配置cid
    target = now_course["target"]
    if now_course["course_type"] == schedule_handle.COURSE_TYPE_INTEREST:
        target = game_config.config_entertainment[target].name
    elif now_course["course_type"] == schedule_handle.COURSE_TYPE_INTERN:
        target = game_config.config_work_type[target].name
    return "{0}·{1}".format(type_name, target)


def get_character_status_list(character_id: int) -> Tuple[List[draw.LeftDraw], List[str]]:
    """
    获取角色的所有状态标识
    
    Keyword arguments:
    character_id -- 角色id
    
    Return arguments:
    Tuple[List[draw.LeftDraw], List[str]] -- (状态标识的绘制对象列表, 状态文本列表)
    """
    from Script.Design import handle_premise
    from Script.System.Sex_System import drunk_sex_common

    character_data: game_type.Character = cache.character_data[character_id]
    status_list = []
    status_text_list = []
    
    # 智能跟随状态
    follow_draw = draw.LeftDraw()
    follow_draw.style = "spring_green"
    follow_text = ""
    if handle_premise.handle_is_follow_1(character_id):
        follow_text = _(" <跟>")
        follow_draw.tooltip = _("处于智能跟随状态，会自动跟随玩家行动")
    follow_draw.text = follow_text
    status_list.append(follow_draw)
    status_text_list.append(follow_text)

    # 上课状态（Plan 22）：一处改动同时覆盖 Tk 与 Web
    # Web 侧 Web_Draw_System/status_panel.py 的 _get_special_states 复用本函数并原样透传 tooltip
    class_draw = draw.LeftDraw()
    class_draw.style = "light_steel_blue"
    class_text = ""
    class_tip = get_now_class_tip(character_id)
    if class_tip:
        # 翘课时改出红色的 <翘>，这是玩家最该注意到的信号，也是「翘课被抓」事件的前置
        if class_tip[0]:
            class_text = _(" <翘>")
            class_draw.style = "red"
        else:
            class_text = _(" <课>")
        class_draw.tooltip = class_tip[1]
    class_draw.text = class_text
    status_list.append(class_draw)
    status_text_list.append(class_text)

    # 跟随母亲见学状态（Plan 22 二期）：与上面的 <课> 一样，一处改动同时覆盖 Tk 与 Web
    # ⚠️ 函数内延迟 import：UI 层在 Core/UI，教育逻辑在 System，模块级 import 会启动即循环（口径16）
    from Script.System.Education_System import class_ai

    # ⚠️ 用 <学> 而不是 <跟>：<跟> 已经是「智能跟随玩家」的标识，两者语义完全不同
    follow_mother_draw = draw.LeftDraw()
    follow_mother_draw.style = "wheat"
    follow_mother_text = ""
    if class_ai.judge_in_follow_mother(character_id):
        follow_mother_text = _(" <学>")
        follow_mother_draw.tooltip = _("正跟着母亲见学，按母亲当前工作对应的科目获得经验")
    follow_mother_draw.text = follow_mother_text
    status_list.append(follow_mother_draw)
    status_text_list.append(follow_mother_text)
    
    # 非普通时输出当前心情
    angry_draw = draw.LeftDraw()
    angry_text = ""
    if character_id != 0:
        angry_text = attr_calculation.get_angry_text(character_data.angry_point)
        angry_text = "" if angry_text == _("普通") else " " + angry_text
    if angry_text == _(" 愉快"):
        angry_draw.style = "coral"
        angry_draw.tooltip = _("当前心情愉快，部分行为实行值提升")
    else:
        angry_draw.style = "red"
        angry_draw.tooltip = _("当前心情不佳，部分行为实行值下降")
    angry_draw.text = angry_text
    status_list.append(angry_draw)
    status_text_list.append(angry_text)
    
    # 饥饿时进行提示
    hunger_draw = draw.LeftDraw()
    hunger_draw.style = "beige"
    hunger_text = ""
    if character_id != 0:
        hunger_text = _(" <饿>") if handle_premise.handle_hunger_ge_80(character_id) else ""
        start_time = character_data.behavior.start_time.hour
        hunger_text = hunger_text if start_time in {6, 7, 8, 11, 12, 13, 16, 17, 18} else ""
        hunger_draw.tooltip = _("肚子饿了，想要吃点东西")
    # 玩家饥饿提示根据设置决定是否显示，且与饭点时间无关
    elif character_id == 0 and cache.all_system_setting.draw_setting.get(17, 1) == 1:
        hunger_text = _(" <饿>") if handle_premise.handle_hunger_ge_80(character_id) else ""
        hunger_draw.tooltip = _("肚子饿了，想要吃点东西")
    hunger_draw.text = hunger_text
    status_list.append(hunger_draw)
    status_text_list.append(hunger_text)
    
    # 有尿意时进行提示
    urinate_draw = draw.LeftDraw()
    urinate_draw.style = "khaki"
    urinate_text = ""
    if handle_premise.handle_urinate_ge_80(character_id):
        urinate_text = _(" <尿>")
        urinate_draw.tooltip = _("有较强的尿意，想要去洗手间解决")
    # 玩家尿意提示根据设置决定是否显示
    if character_id == 0 and cache.all_system_setting.draw_setting.get(17, 1) == 0:
        urinate_text = ""
    urinate_draw.text = urinate_text
    status_list.append(urinate_draw)
    status_text_list.append(urinate_text)
    
    # 非0疲劳时输出当前疲劳状态
    sleep_draw = draw.LeftDraw()
    sleep_draw.style = "little_dark_slate_blue"
    tired_lv = attr_calculation.get_tired_level(character_data.tired_point)
    sleep_text = " <" + constant.tired_text_list[tired_lv] + ">"
    # 0疲劳的清醒则不输出
    if sleep_text == _(" <清醒>"):
        sleep_text = ""
    if character_id > 0:
        # 睡眠中则输出睡眠程度
        if handle_premise.handle_action_sleep(character_id) or handle_premise.handle_unconscious_flag_1(character_id):
            sleep_lv, sleep_name = attr_calculation.get_sleep_level(character_data.sleep_point)
            sleep_text = f" <{sleep_name}>"
            sleep_draw.tooltip = game_config.config_sleep_level[sleep_lv].introduction
            sleep_draw.style = game_config.config_sleep_level[sleep_lv].color
            # 疲劳已完全恢复，且是白天，且没有服用安眠药，且非醉酒，则提示即将醒来
            if (
                handle_premise.handle_tired_le_0(character_id) and
                handle_premise.handle_time_day(character_id) and
                handle_premise.handle_self_not_sleep_pills(character_id) and
                handle_premise.handle_drunk_level_0(character_id)
            ):
                sleep_text += _("(将醒)")
                sleep_draw.tooltip = _("已经睡饱了，会很快醒来，如果不想被发现最好快点结束")
                sleep_draw.style = "warning"
        # 如果在装睡则输出装睡
        if handle_premise.handle_self_sleep_h_awake_but_pretend_sleep(character_id):
            sleep_text = _(" <装睡>")
            sleep_draw.tooltip = _("已经醒来，但决定装睡来默认你的行为")
        # 如果处于睡觉中被吵醒状态则输出被吵醒，并附上剩余的无法入睡时间
        elif handle_premise.handle_sleep_disturbed_1(character_id):
            sleep_text = _(" <被吵醒>")
            left_minute = int((character_data.action_info.sleep_disturbed_end_time - cache.game_time).total_seconds() // 60)
            left_minute = max(1, left_minute)
            sleep_draw.tooltip = _("刚被吵醒，还需{0}分钟才会重新想睡").format(left_minute)
            sleep_draw.style = "warning"
    sleep_draw.text = sleep_text
    status_list.append(sleep_draw)
    status_text_list.append(sleep_text)

    # 醉酒状态，三种醉的等级分别有对应说明和字体颜色
    drunk_draw = draw.LeftDraw()
    drunk_text = ""
    drunk_level, drunk_name = drunk_sex_common.get_drunk_level(character_id)
    if drunk_level > 0:
        drunk_text = " " + drunk_name
        drunk_draw.tooltip = game_config.config_drunk_level[drunk_level].info
        drunk_draw.style = game_config.config_drunk_level[drunk_level].color
    drunk_draw.text = drunk_text
    status_list.append(drunk_draw)
    status_text_list.append(drunk_text)

    # hp1的完全疲劳状态
    tired_draw = draw.LeftDraw()
    tired_draw.style = "little_dark_slate_blue"
    tired_text = ""
    if handle_premise.handle_self_tired(character_id):
        tired_text = _(" <累>")
        tired_draw.tooltip = _("疲劳度过高，需要回宿舍睡觉")
    tired_draw.text = tired_text
    status_list.append(tired_draw)
    status_text_list.append(tired_text)
    
    # 催眠状态时进行显示
    hypnosis_draw = draw.LeftDraw()
    hypnosis_text = ""
    if (
        cache.all_system_setting.draw_setting[4] and 
        (handle_premise.handle_unconscious_hypnosis_flag(character_id) or
        (character_data.hypnosis.hypnosis_degree > 0 and cache.all_system_setting.draw_setting[4] == 2))
    ):
        hypnosis_text = _(" <催眠")
        # 根据催眠程度来区分颜色
        hypnosis_draw.style = hypnosis_panel.get_hypnosis_degree_color(character_data.hypnosis.hypnosis_degree)
        # 是否显示具体数值
        if cache.all_system_setting.draw_setting[4] == 2:
            # 显示到小数点后一位
            hypnosis_text += f"({round(character_data.hypnosis.hypnosis_degree, 1)}%)"
        # 是否显示催眠类型
        if handle_premise.handle_unconscious_hypnosis_flag(character_id):
            hypnosis_cid = character_data.sp_flag.unconscious_h - 3
            hypnosis_name = game_config.config_hypnosis_type[hypnosis_cid].name
            hypnosis_text += _(":{0}").format(hypnosis_name)
            hypnosis_draw.tooltip = game_config.config_hypnosis_type[hypnosis_cid].introduce
        if handle_premise.handle_hypnosis_increase_body_sensitivity(character_id):
            hypnosis_text += _("(敏感)")
            hypnosis_draw.tooltip = game_config.config_hypnosis_sub_type[1].introduce
        if handle_premise.handle_hypnosis_force_ovulation(character_id):
            hypnosis_text += _("(排卵)")
            hypnosis_draw.tooltip = game_config.config_hypnosis_sub_type[3].introduce
        if handle_premise.handle_hypnosis_blockhead(character_id):
            hypnosis_text += _("(木头人)")
            hypnosis_draw.tooltip = game_config.config_hypnosis_sub_type[4].introduce
        if handle_premise.handle_hypnosis_active_h(character_id):
            hypnosis_text += _("(逆推)")
            hypnosis_draw.tooltip = game_config.config_hypnosis_sub_type[5].introduce
        if handle_premise.handle_hypnosis_roleplay(character_id):
            hypnosis_text += _("(扮演")
            for role_play_cid in character_data.hypnosis.roleplay:
                role_play_name = game_config.config_roleplay[role_play_cid].name
                hypnosis_text += f"-{role_play_name}"
            hypnosis_text += ")"
            hypnosis_draw.tooltip = game_config.config_hypnosis_sub_type[12].introduce
        if handle_premise.handle_hypnosis_pain_as_pleasure(character_id):
            hypnosis_text += _("(痛→快感)")
            hypnosis_draw.tooltip = game_config.config_hypnosis_sub_type[11].introduce
        hypnosis_text += ">"
    hypnosis_draw.text = hypnosis_text
    status_list.append(hypnosis_draw)
    status_text_list.append(hypnosis_text)
    
    # 携袋状态进行提示
    bag_text = ""
    bag_draw = draw.LeftDraw()
    if character_data.sp_flag.bagging_chara_id:
        bag_text = _(" <携袋:{0}>").format(cache.character_data[character_data.sp_flag.bagging_chara_id].name)
        bag_draw.tooltip = _("将失去意识的干员装进了袋子中，用于在关押区监禁到牢房里")
    bag_draw.text = bag_text
    status_list.append(bag_draw)
    status_text_list.append(bag_text)
    
    # 访客
    visitor_text = ""
    visitor_draw = draw.LeftDraw()
    if character_data.sp_flag.vistor == 1:
        visitor_text = _(" <访>")
        visitor_draw.tooltip = _("作为访客来罗德岛参观，不会参与工作和常规活动，在访问期结束后会离开罗德岛或留下成为干员")
    visitor_draw.text = visitor_text
    status_list.append(visitor_draw)
    status_text_list.append(visitor_text)
    
    # 逆推H
    active_h_text = ""
    active_h_draw = draw.LeftDraw()
    active_h_draw.style = "light_pink"
    if handle_premise.handle_npc_active_h(character_id):
        active_h_text = _(" <逆>")
        active_h_draw.tooltip = _("对博士主动进行性行为")
    active_h_draw.text = active_h_text
    status_list.append(active_h_draw)
    status_text_list.append(active_h_text)
    
    # 绝顶寸止
    orgasm_edge_text = ""
    orgasm_edge_draw = draw.LeftDraw()
    if handle_premise.handle_self_orgasm_edge(character_id):
        skill_ability_lv = cache.character_data[0].ability[30]
        orgasm_edge_margin = skill_ability_lv * 3 - sum(value * value for value in character_data.h_state.orgasm_edge_count.values())
        if orgasm_edge_margin >= 3:
            orgasm_edge_text = _(" <寸止>")
            orgasm_edge_draw.style = "hot_pink"
            orgasm_edge_draw.tooltip = _("被进行了绝顶寸止，会无法绝顶高潮")
        elif orgasm_edge_margin >= 0:
            orgasm_edge_text = _(" <寸止!>")
            orgasm_edge_draw.style = "red"
            orgasm_edge_draw.tooltip = _("被进行了绝顶寸止，差不多到了能控制住的极限")
        else:
            orgasm_edge_text = _(" <寸止!!>")
            orgasm_edge_draw.style = "levelex"
            orgasm_edge_draw.tooltip = _("被进行了绝顶寸止，已经超过能控制住的极限")
    orgasm_edge_draw.text = orgasm_edge_text
    status_list.append(orgasm_edge_draw)
    status_text_list.append(orgasm_edge_text)
    
    # 监禁状态
    imprisonment_text = ""
    imprisonment_draw = draw.LeftDraw()
    imprisonment_draw.style = "crimson"
    if handle_premise.handle_imprisonment_1(character_id):
        imprisonment_text = _(" <监>")
        imprisonment_draw.tooltip = _("被监禁，无法自由行动")
    imprisonment_draw.text = imprisonment_text
    status_list.append(imprisonment_draw)
    status_text_list.append(imprisonment_text)
    
    # 时停
    time_stop_text = ""
    time_stop_draw = draw.LeftDraw()
    time_stop_draw.style = "light_sky_blue"
    if handle_premise.handle_unconscious_flag_3(character_id):
        time_stop_text = _(" <停>")
        time_stop_draw.tooltip = _("处于时间停止状态，无法行动")
    time_stop_draw.text = time_stop_text
    status_list.append(time_stop_draw)
    status_text_list.append(time_stop_text)
    
    # 隐奸
    hidden_text = ""
    hidden_draw = draw.LeftDraw()
    hidden_draw.style = "deep_gray"
    if character_id == 0 and (handle_premise.handle_hidden_sex_mode_3(character_id) or handle_premise.handle_hidden_sex_mode_4(character_id)):
        hidden_text = _(" <隐>")
        hidden_draw.tooltip = _("正在偷偷进行性行为，享受避免被他人发现的刺激感")
    elif character_id != 0 and (handle_premise.handle_hidden_sex_mode_2(character_id) or handle_premise.handle_hidden_sex_mode_4(character_id)):
        hidden_text = _(" <隐>")
        hidden_draw.tooltip = _("正在偷偷进行性行为，享受避免被他人发现的刺激感")
    hidden_draw.text = hidden_text
    status_list.append(hidden_draw)
    status_text_list.append(hidden_text)
    
    # 露出
    exhibitionism_text = ""
    exhibitionism_draw = draw.LeftDraw()
    exhibitionism_draw.style = "hot_pink"
    if handle_premise.handle_exhibitionism_sex_mode_ge_1(character_id):
        exhibitionism_text = _(" <露>")
        exhibitionism_draw.tooltip = _("正在进行露出行为，享受被他人看到的刺激感")
    exhibitionism_draw.text = exhibitionism_text
    status_list.append(exhibitionism_draw)
    status_text_list.append(exhibitionism_text)
    
    # 破处
    first_sex_text = ""
    first_sex_draw = draw.LeftDraw()
    first_sex_draw.style = "crimson"
    if handle_premise.handle_first_sex_in_today(character_id):
        if character_id == 0:
            first_sex_text += _(" <P破处>")
            first_sex_draw.tooltip += _("今天失去了童贞")
        else:
            first_sex_text += _(" <V破处>")
            first_sex_draw.tooltip += _("今天失去了阴道处女，还残留着隐痛和扩张感")
    if handle_premise.handle_first_a_sex_in_today(character_id):
        first_sex_text += _(" <A破处>")
        first_sex_draw.tooltip += _("今天失去了肛门处女，还残留着隐痛和扩张感")
    if handle_premise.handle_first_u_sex_in_today(character_id):
        first_sex_text += _(" <U破处>")
        first_sex_draw.tooltip += _("今天失去了尿道处女，还残留着隐痛和扩张感")
    if handle_premise.handle_first_w_sex_in_today(character_id):
        first_sex_text += _(" <W破处>")
        first_sex_draw.tooltip += _("今天失去了子宫处女，还残留着隐痛和扩张感")
    first_sex_draw.text = first_sex_text
    status_list.append(first_sex_draw)
    status_text_list.append(first_sex_text)

    return status_list, status_text_list

class CharacterInfoHead:
    """
    角色信息面板头部面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.draw_title: bool = True
        """ 是否绘制面板标题 """

        from Script.UI.Panel.see_item_info_panel import use_drug, auto_use_sanity_drug

        character_data: game_type.Character = cache.character_data[character_id]
        # sex_text = game_config.config_sex_tem[character_data.sex].name

        # 好感与信赖
        favorability_and_trust_text = ""
        if character_id:
            favorability_lv,tem = attr_calculation.get_favorability_level(character_data.favorability[0])
            favorability_lv_letter = attr_calculation.judge_grade(favorability_lv)
            trust_lv,tem = attr_calculation.get_trust_level(character_data.trust)
            trust_lv_letter = attr_calculation.judge_grade(trust_lv)
            favorability_text = f"{int(character_data.favorability[0])}"
            trust_text = f"{round(character_data.trust, 1)}%"
            # 只显示等级
            if cache.all_system_setting.draw_setting[3] == 1:
                favorability_and_trust_text = _("好感度:{0}，信赖度:{1}").format(favorability_lv_letter, trust_lv_letter)
            # 显示数值和等级
            elif cache.all_system_setting.draw_setting[3] == 2:
                favorability_and_trust_text = _("好感度:{0}({1})，信赖度:{2}({3})").format(favorability_text, favorability_lv_letter, trust_text, trust_lv_letter)

        # 射精欲不为零时进行提示
        eja_text = ""
        if character_id == 0 and character_data.eja_point > 0:
            if character_data.eja_point <= 300:
                eja_text = _(" <射精欲:低>")
            elif character_data.eja_point <= 600:
                eja_text = _(" <射精欲:中>")
            elif character_data.eja_point <= 900:
                eja_text = _(" <射精欲:高>")
            else:
                eja_text = _(" <射精欲:极>")

        # 获取所有角色状态
        status_list, status_text_list = get_character_status_list(character_id)

        if character_id:
            message = (
                "{character_name} {favorability_and_trust}").format(
                character_name=character_data.name,
                favorability_and_trust=favorability_and_trust_text,
            )
        else:
            message = (
                "{character_name}{character_nick_name}{eja}").format(
                # character_id=character_id,
                character_name=character_data.name,
                character_nick_name=character_data.nick_name,
                # sex_text=sex_text,
                eja=eja_text,
            )
        message_draw = draw.CenterDraw()
        # 根据其他状态的长度来调整文本的长度，同时也保证了一个最小长度
        text_width = text_handle.get_text_index(message)
        all_status_text = "".join(status_text_list)
        base_width = width / 3.5 - text_handle.get_text_index(all_status_text)
        max_width = max(base_width, text_width)
        message_draw.width = int(max_width)
        message_draw.text = message
        hp_draw = draw.InfoBarDraw()
        hp_draw.width = int(width / 6)
        hp_draw.scale = 0.8
        hp_draw.set(
            "HitPointbar",
            int(character_data.hit_point_max),
            int(character_data.hit_point),
            _("体力"),
            tooltip = _("体力，最低为1时会疲劳到无法行动")
        )
        mp_draw = draw.InfoBarDraw()
        mp_draw.width = int(width / 6)
        mp_draw.scale = 0.8
        mp_draw.set(
            "ManaPointbar",
            int(character_data.mana_point_max),
            int(character_data.mana_point),
            _("气力"),
            tooltip = _("气力，精神上的耐力，最低为0时使体力的消耗增加")
        )
        if character_id == 0:
            sanity_point_draw = draw.InfoBarDraw()
            sanity_point_draw.width = int(width / 7.5)
            sanity_point_draw.scale = 1
            sanity_point_draw.set(
                "SanityPointbar",
                int(character_data.sanity_point_max),
                int(character_data.sanity_point),
                _("理智"),
                tooltip = _("理智，使用源石技艺时消耗"),
            )
            sanity_item_draw = draw.LeftButton(
                "✚",
                _("快速使用最小理智剂"),
                1,
                normal_style = "sanity",
                cmd_func = auto_use_sanity_drug,
                tooltip=_("使用最小规格的理智恢复剂快速恢复理智"),
            )
            semen_point_draw = draw.InfoBarDraw()
            semen_point_draw.width = int(width / 7.5)
            semen_point_draw.scale = 1
            semen_point_draw.set(
                "SemenPointBar",
                int(character_data.semen_point_max),
                int(character_data.semen_point + character_data.tem_extra_semen_point),
                _("精液"),
                tooltip = _("精液，进行射精时消耗"),
            )
            semen_item_draw = draw.LeftButton(
                "✚",
                _("快速使用精力剂"),
                1,
                normal_style = "semen",
                cmd_func = use_drug,
                args = 11,
                tooltip=_("使用精力恢复剂快速恢复精力"),
            )
        None_draw = draw.CenterDraw()
        None_draw.width = 1
        None_draw.text = (" ")
        self.draw_list: List = [
            tuple([message_draw] + status_list + [hp_draw, None_draw, mp_draw]),
        ]
        if character_id == 0:
            self.draw_list[0] = self.draw_list[0] + (None_draw, None_draw, sanity_point_draw,)
            # 如果有理智恢复剂的话，显示快捷键
            for item_id in [0, 1, 2, 3]:
                if character_data.item[item_id] > 0:
                    self.draw_list[0] = self.draw_list[0] + (sanity_item_draw,)
                    self.return_list.append(sanity_item_draw.return_text)
                    break
            self.draw_list[0] = self.draw_list[0] + (None_draw, None_draw, semen_point_draw,)
            # 如果有精力恢复剂的话，显示快捷键
            if character_data.item[11] > 0:
                self.draw_list[0] = self.draw_list[0] + (semen_item_draw,)
                self.return_list.append(semen_item_draw.return_text)
        """ 要绘制的面板列表 """

    def draw(self):
        """绘制面板"""
        if self.draw_title:
            title_draw = draw.TitleLineDraw(_("人物属性"), self.width)
            title_draw.draw()
        for draw_tuple in self.draw_list:
            for label in draw_tuple:
                label.draw()
            line_feed.draw()
