from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def get_current_h_mode_text(character_id: int) -> str:
    """
    获取角色当前H模式的描述文本（基于前提判定系统的通用函数）\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    str -- 非H/正常H/各特殊H模式名（同时处于多个特殊模式时以顿号连接）
    """
    character_data = cache.character_data[character_id]
    if not handle_premise.handle_self_is_h(character_id):
        return _("非H")
    mode_text_list = []
    # 无意识H按类型显示（hypnosis_panel延迟导入，规避 hypnosis_panel→handle_talent→first_record_handle 的导入链在启动期成环）
    if handle_premise.handle_unconscious_flag_ge_1(character_id):
        from Script.UI.Panel import hypnosis_panel
        mode_text_list.append(_("{0}H").format(hypnosis_panel.unconscious_list[character_data.sp_flag.unconscious_h]))
    if handle_premise.handle_group_sex_mode_on(character_id):
        mode_text_list.append(_("群交"))
    if handle_premise.handle_exhibitionism_sex_mode_ge_1(character_id):
        mode_text_list.append(_("露出H"))
    if handle_premise.handle_hidden_sex_mode_ge_1(character_id):
        mode_text_list.append(_("隐奸H"))
    if handle_premise.handle_self_sleep_h_awake_but_pretend_sleep(character_id):
        mode_text_list.append(_("装睡H"))
    if handle_premise.handle_self_is_player_daughter(character_id):
        mode_text_list.append(_("乱伦H"))
    if handle_premise.handle_h_in_love_hotel(character_id):
        mode_text_list.append(_("爱情旅馆H"))
    if handle_premise.handle_h_in_bathroom(character_id):
        mode_text_list.append(_("浴室H"))
    if handle_premise.handle_npc_active_h(character_id):
        mode_text_list.append(_("逆推H"))
    if handle_premise.handle_imprisonment_1(character_id):
        mode_text_list.append(_("监禁H"))
    if not len(mode_text_list):
        return _("正常H")
    return _("、").join(mode_text_list)
