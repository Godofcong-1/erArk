from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config, normal_config
from Script.Design import attr_text, game_time
from Script.UI.Panel import character_info_head, hypnosis_panel

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

_fold_state: dict = {}
""" 各周目各分组的折叠状态（键"{周目数}_{折叠槽位序号}"→bool是否展开；当前周目含体液数据组共7个槽位、历史周目6个；仅会话内有效，不进存档） """

_selected_round: int = -1
""" 履历面板当前查看的周目数（-1为跟随当前周目；无效选择时回退为当前周目；仅会话内有效，不进存档） """


def _select_round(round_num: int):
    """
    切换履历面板当前查看的周目
    Keyword arguments:
    round_num -- 要查看的周目数
    """
    global _selected_round
    _selected_round = round_num

_GROUP_NAME_LIST = [
    _("部位初体验"),
    _("初次被射精"),
    _("初次绝顶履历"),
    _("陷落与刻印履历"),
    _("H模式初体验"),
    _("特殊履历"),
]
""" 履历面板的6个履历分组名（初吻条目并入部位初体验组） """

_FLUID_GROUP_NAME = _("体液数据")
""" 体液数据分组名（读取实时污浊/收藏数据，仅当前周目块显示） """

_PART_SEX_NAME_DICT = {
    0: _("发交"),
    1: _("脸交"),
    2: _("口交"),
    3: _("乳交"),
    4: _("腋交"),
    5: _("手交"),
    6: _("V性交"),
    7: _("子宫性交"),
    8: _("A性交"),
    9: _("U性交"),
    10: _("腿交"),
    11: _("足交"),
    12: _("尾交"),
    13: _("兽角蹭"),
    14: _("兽耳蹭"),
    15: _("深喉"),
}
""" 部位交类型编号到交型名的映射（同h_state.insert_position的身体部位编号） """

_PART_SEX_VIRGIN_NAME_DICT = {
    6: _("处女"),
    7: _("子宫处女"),
    8: _("后庭处女"),
    9: _("尿道处女"),
}
""" 四类插入部位对应的处女名（破处条目沿用肉体情况页原句式） """

_ITEM_NAME_DICT = {
    0: _("手指"),
    1: _("振动棒"),
    2: _("采尿器"),
}
""" 部位交道具编号到道具名的映射 """

_MARK_TYPE_LIST = [
    ("happy", 13, 3),
    ("yield", 14, 3),
    ("pain", 15, 3),
    ("time", 16, 3),
    ("terror", 17, 3),
    ("hate", 18, 3),
    ("unconscious", 19, 6),
]
""" 刻印类型列表 [(二段行为id前缀, 刻印能力id, 最大等级)] """

_ORGASM_STATE_ID_LIST = [0, 1, 2, 4, 5, 6, 7, 21, 22, 23]
""" 绝顶履历遍历的快感部位id列表（NPC专用面板，排除3阴茎） """


def _toggle_fold(fold_key: str, default_expand: bool):
    """
    翻转指定分组的折叠状态
    Keyword arguments:
    fold_key -- 折叠状态键（"{周目数}_{组序号}"）\n
    default_expand -- 该分组的默认展开状态
    """
    _fold_state[fold_key] = not _fold_state.get(fold_key, default_expand)


def _format_time(now_time) -> str:
    """
    格式化履历时间文本（切掉"时间:"前缀的全库惯例，对异常时间数据做防御）
    Keyword arguments:
    now_time -- datetime时间\n
    Return arguments:
    str -- 格式化后的时间文本，无法解析时为"未知时间"
    """
    try:
        return game_time.get_date_until_day(now_time)[3:]
    except Exception:
        return _("未知时间")


def _format_place(place) -> str:
    """
    格式化履历地点文本（对旧数据缺失地点做防御）
    Keyword arguments:
    place -- 场景路径列表\n
    Return arguments:
    str -- 场景路径文本，无法解析时为"未知地点"
    """
    try:
        return attr_text.get_scene_path_text(place)
    except KeyError:
        return _("未知地点")


def _get_character_name(character_id: int) -> str:
    """
    获取履历中对象角色的名字
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    str -- 角色名，查不到时为空串
    """
    if character_id in cache.character_data:
        return cache.character_data[character_id].name
    return ""


def _build_part_sex_text(first_record) -> str:
    """
    构建部位初体验分组文本（初吻条目+各部位交条目；V/A/U/W破处条目沿用肉体情况页原句式，其余用统一简句式；未记录的条目不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    Return arguments:
    str -- 分组文本
    """
    now_text = ""
    # 初吻条目（句式沿用肉体情况页原详情句）
    first_kiss_id = getattr(first_record, "first_kiss_id", -1)
    if first_kiss_id != -1:
        now_text += _("  初吻：于{kiss_time}在{kiss_palce}，向{character_name}博士").format(
            character_name=_get_character_name(first_kiss_id),
            kiss_time=_format_time(getattr(first_record, "first_kiss_time", None)),
            kiss_palce=_format_place(getattr(first_record, "first_kiss_place", ["0"])),
        )
        if getattr(first_record, "first_kiss_body_part", -1) == 1:
            now_text += _("的阴茎")
        now_text += _("献上了初吻\n")
    # 各部位交条目
    part_sex_dict = getattr(first_record, "first_part_sex_dict", {})
    for part_id in _PART_SEX_NAME_DICT:
        part_name = _PART_SEX_NAME_DICT[part_id]
        record = part_sex_dict.get(part_id, None)
        if record is None:
            continue
        target_name = _get_character_name(record.get("id", -1)) if record.get("id", -1) != -1 else ""
        time_text = _format_time(record.get("time", None))
        place_text = _format_place(record.get("place", ["0"]))
        posture = record.get("posture", "")
        # V/A/U/W破处条目沿用原句式
        if part_id in _PART_SEX_VIRGIN_NAME_DICT and target_name and posture:
            now_text += _("  {part_name}：于{time}在{palce}，被{character_name}博士以{posture}夺走了{virgin_name}").format(
                part_name=part_name,
                time=time_text,
                palce=place_text,
                character_name=target_name,
                posture=posture,
                virgin_name=_PART_SEX_VIRGIN_NAME_DICT[part_id],
            )
        # 其余部位交条目用统一的简句式
        else:
            now_text += _("  {part_name}：于{time}在{palce}").format(
                part_name=part_name,
                time=time_text,
                palce=place_text,
            )
            if target_name:
                now_text += _("，与{character_name}博士初次体验").format(character_name=target_name)
            else:
                now_text += _("初次体验")
            if posture:
                now_text += _("（姿势：{0}）").format(posture)
        item = record.get("item", -1)
        if item in _ITEM_NAME_DICT:
            now_text += _("（使用道具：{0}）").format(_ITEM_NAME_DICT[item])
        now_text += "\n"
    return now_text


def _build_shoot_body_text(first_record) -> str:
    """
    构建初次被射精分组文本（按BodyPart.csv全部位遍历，未记录的部位不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    Return arguments:
    str -- 分组文本
    """
    now_text = ""
    shoot_body_dict = getattr(first_record, "first_shoot_body_dict", {})
    for part_cid in game_config.config_body_part:
        part_name = game_config.config_body_part[part_cid].name
        record = shoot_body_dict.get(part_cid, None)
        if record is None:
            continue
        now_text += _("  {0}：于{1}在{2}\n").format(part_name, _format_time(record[0]), _format_place(record[1]))
    return now_text


def _build_orgasm_text(first_record) -> str:
    """
    构建初次绝顶履历分组文本（强绝顶/超强绝顶/多重绝顶三小节，无记录的小节与条目不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    Return arguments:
    str -- 分组文本
    """
    now_text = ""
    strong_dict = getattr(first_record, "first_strong_orgasm_dict", {})
    super_dict = getattr(first_record, "first_super_orgasm_dict", {})
    plural_dict = getattr(first_record, "first_plural_orgasm_dict", {})
    # 强绝顶与超强绝顶按快感部位列表遍历
    for degree_name, degree_dict in ((_("强绝顶"), strong_dict), (_("超强绝顶"), super_dict)):
        if not len(degree_dict):
            continue
        now_text += _(" 【{0}】\n").format(degree_name)
        for state_id in _ORGASM_STATE_ID_LIST:
            state_name = game_config.config_character_state[state_id].name
            record = degree_dict.get(state_id, None)
            if record is None:
                continue
            now_text += _("  {0}：于{1}在{2}\n").format(state_name, _format_time(record[0]), _format_place(record[1]))
    # 多重绝顶按等级升序遍历，未达成的等级不列出
    if len(plural_dict):
        now_text += _(" 【多重绝顶】\n")
        for part_count in sorted(plural_dict):
            record = plural_dict[part_count]
            part_name_list = []
            for state_id in record[2]:
                if state_id in game_config.config_character_state:
                    part_name_list.append(game_config.config_character_state[state_id].name)
            now_text += _("  {0}重绝顶：于{1}在{2}，参与部位：{3}\n").format(
                part_count, _format_time(record[0]), _format_place(record[1]), _("、").join(part_name_list))
    return now_text


def _build_fall_and_mark_text(first_record) -> str:
    """
    构建陷落与刻印履历分组文本（陷落素质/刻印两小节，无记录的小节与条目不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    Return arguments:
    str -- 分组文本
    """
    now_text = ""
    fall_dict = getattr(first_record, "fall_talent_time_dict", {})
    mark_dict = getattr(first_record, "first_mark_dict", {})
    # 陷落素质小节：爱情系201-204与隶属系211-214，只列已获得项
    if len(fall_dict):
        now_text += _(" 【陷落素质】\n")
        for talent_id in (201, 202, 203, 204, 211, 212, 213, 214):
            talent_name = game_config.config_talent[talent_id].name
            record = fall_dict.get(talent_id, None)
            if record is None:
                continue
            now_text += _("  {0}：于{1}在{2}获得\n").format(talent_name, _format_time(record[0]), _format_place(record[1]))
    # 刻印小节：按刻印类型分行，未达成的等级不列出
    if len(mark_dict):
        now_text += _(" 【刻印】\n")
        for mark_type, ability_id, max_level in _MARK_TYPE_LIST:
            for now_level in range(1, max_level + 1):
                mark_key = f"{mark_type}_mark_{now_level}"
                record = mark_dict.get(mark_key, None)
                if record is None:
                    continue
                mark_name = game_config.config_ability[ability_id].name
                now_text += _("  {0}{1}级：于{2}在{3}\n").format(
                    mark_name, now_level, _format_time(record[0]), _format_place(record[1]))
    return now_text


def _build_h_mode_text(first_record) -> str:
    """
    构建H模式初体验分组文本（固定11项：无意识7类型+群交/露出H/隐奸H/装睡H，未体验的条目不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    Return arguments:
    str -- 分组文本
    """
    now_text = ""
    h_mode_dict = getattr(first_record, "first_h_mode_dict", {})
    # 组装11项固定条目 [(模式键, 条目名)]
    mode_list = []
    for unconscious_type in range(1, 8):
        mode_list.append((f"unconscious_{unconscious_type}", _("第一次{0}H").format(hypnosis_panel.unconscious_list[unconscious_type])))
    mode_list.append(("group_sex", _("第一次群交")))
    mode_list.append(("exhibitionism", _("第一次露出H")))
    mode_list.append(("hidden_sex", _("第一次隐奸H")))
    mode_list.append(("pretend_sleep", _("第一次装睡H")))
    for mode_key, mode_name in mode_list:
        record = h_mode_dict.get(mode_key, None)
        if record is None:
            continue
        now_text += _("  {0}：于{1}在{2}").format(mode_name, _format_time(record[0]), _format_place(record[1]))
        extra_data = record[2] if len(record) > 2 else ""
        if extra_data:
            if mode_key == "group_sex":
                now_text += _("（当时场景内共{0}人）").format(extra_data)
            else:
                now_text += _("（{0}）").format(extra_data)
        now_text += "\n"
    return now_text


def _build_special_record_text(first_record) -> str:
    """
    构建特殊履历分组文本（FirstRecordSpecial.csv配表驱动，配表加行后自动跟随；未达成的条目不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    Return arguments:
    str -- 分组文本
    """
    now_text = ""
    special_dict = getattr(first_record, "first_special_record_dict", {})
    for special_cid in sorted(game_config.config_first_record_special):
        special_name = game_config.config_first_record_special[special_cid].name
        record = special_dict.get(special_cid, None)
        if record is None:
            continue
        now_text += _("  {0}：于{1}在{2}").format(special_name, _format_time(record[0]), _format_place(record[1]))
        extra_data = record[2] if len(record) > 2 else ""
        if extra_data:
            now_text += _("（{0}）").format(extra_data)
        now_text += "\n"
    return now_text


def _build_fluid_text(character_id: int) -> str:
    """
    构建体液数据分组文本（自肉体情况页迁移而来；无数据的条目不显示）
    读取的是当前实时数据（dirty/pl_collection），不入FIRST_RECORD，因此仅当前周目块显示
    喝过的精液量并入口腔行、食道直入胃量与肠胃吸收量并入胃部行，不再单独成行
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    str -- 分组文本
    """
    character_data = cache.character_data[character_id]
    pl_character_data = cache.character_data[0]
    now_text = ""
    # 全身累计被射精液量
    semen_count = 0
    for body_part in game_config.config_body_part:
        semen_count += character_data.dirty.body_semen[body_part][3]
    if semen_count:
        now_text += _("  全身总共被射上过{0}ml精液\n").format(semen_count)
        # 各身体部位的累计被射精液量（只列非零部位）
        now_text += _(" 【各部位累计被射精液量】\n")
        for part_cid in game_config.config_body_part:
            part_semen = character_data.dirty.body_semen[part_cid][3]
            part_name = game_config.config_body_part[part_cid].name
            # 口腔行：累计被射入口腔的精液即喝下的精液，以喝过量的形式显示
            if part_cid == 2:
                if part_semen:
                    now_text += _("  {0}：总共喝过{1}ml精液\n").format(part_name, part_semen)
                continue
            # 胃部行：累计被射精量即食道直入胃的精液量，其后以逗号接肠胃吸收的精液量
            if part_cid == 15:
                absorbed_semen = character_data.dirty.absorbed_total_semen
                if part_semen or absorbed_semen:
                    stomach_text_list = []
                    if part_semen:
                        stomach_text_list.append(_("有{0}ml精液在食道直接射进了胃里").format(part_semen))
                    if absorbed_semen:
                        stomach_text_list.append(_("肠胃一共吸收了{0}ml精液").format(absorbed_semen))
                    now_text += _("  {0}：{1}\n").format(part_name, _("，").join(stomach_text_list))
                continue
            if part_semen:
                # 其余部位行同样用完整文本叙述：腔内部位用"射入"句式、体表部位用"淋上"句式（沿用肉体情况页原措辞）
                if part_cid in (6, 7, 8, 9):
                    now_text += _("  {0}：总共被射入过{1}ml精液\n").format(part_name, part_semen)
                else:
                    now_text += _("  {0}：总共被淋上过{1}ml精液\n").format(part_name, part_semen)
    # 收集的乳汁与圣水
    milk_total = pl_character_data.pl_collection.milk_total.get(character_id, 0)
    if milk_total > 0:
        now_text += _("  总共收集了{0}ml乳汁\n").format(milk_total)
    urine_total = pl_character_data.pl_collection.urine_total.get(character_id, 0)
    if urine_total > 0:
        now_text += _("  总共收集了{0}ml圣水\n").format(urine_total)
    return now_text


_GROUP_BUILD_FUNC_LIST = [
    _build_part_sex_text,
    _build_shoot_body_text,
    _build_orgasm_text,
    _build_fall_and_mark_text,
    _build_h_mode_text,
    _build_special_record_text,
]
""" 6个分组的文本构建函数列表（与_GROUP_NAME_LIST顺序一致） """


def build_group_text(first_record, group_index: int) -> str:
    """
    构建指定分组的履历文本（当前周目与历史周目块共用，未记录的条目一律不显示）
    Keyword arguments:
    first_record -- FIRST_RECORD实例（当前记录或历史周目快照）\n
    group_index -- 分组序号(0~5)\n
    Return arguments:
    str -- 分组文本
    """
    return _GROUP_BUILD_FUNC_LIST[group_index](first_record)


class FirstRecordText:
    """
    显示角色性行为履历面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.draw_list: List = []
        """ 绘制的对象列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

        character_data = cache.character_data[character_id]
        type_line = draw.LittleTitleLineDraw(_("性行为履历"), width, ":")
        self.draw_list.append(type_line)

        # 单周目显示：只渲染当前查看的一个周目，默认为当前周目
        # 可查看的周目列表：各历史周目升序 + 当前周目
        first_record_history = getattr(character_data, "first_record_history", {})
        available_round_list = sorted(first_record_history)
        available_round_list.append(cache.game_round)
        # 当前查看的周目（无效选择时回退为当前周目）
        now_round = _selected_round if _selected_round in available_round_list else cache.game_round
        is_current = now_round == cache.game_round
        if is_current:
            first_record = character_data.first_record
        else:
            first_record = first_record_history[now_round]

        # 周目切换按钮行（存在历史周目时才显示，▶标记当前查看的周目）
        if len(available_round_list) > 1:
            switch_tip_draw = draw.NormalDraw()
            switch_tip_draw.text = _("\n周目切换：")
            switch_tip_draw.width = width
            self.draw_list.append(switch_tip_draw)
            for round_num in available_round_list:
                if round_num == cache.game_round:
                    button_label = _("第{0}周目(当前)").format(round_num)
                else:
                    button_label = _("第{0}周目").format(round_num)
                if round_num == now_round:
                    button_text = f"▶{button_label}"
                else:
                    button_text = f"[{button_label}]"
                round_button_draw = draw.LeftButton(
                    button_text,
                    f"first_record_round_{round_num}",
                    int(self.width / 6),
                    cmd_func=_select_round,
                    args=(round_num,),
                )
                self.draw_list.append(round_button_draw)
                self.return_list.append(round_button_draw.return_text)
            self.draw_list.append(line_feed)

        # 周目块标题
        round_title_draw = draw.NormalDraw()
        if is_current:
            round_title_draw.text = _("\n◆ 第{0}周目（当前）\n").format(now_round)
        else:
            round_title_draw.text = _("\n◆ 第{0}周目\n").format(now_round)
        round_title_draw.width = width
        self.draw_list.append(round_title_draw)
        # 组装本周目的分组列表：6个履历组 +（仅当前周目）体液数据组，体液组插在初次被射精之后
        # 元组为(分组名, 履历组序号)，体液组用序号-1标识
        group_entry_list = [(_GROUP_NAME_LIST[group_index], group_index) for group_index in range(len(_GROUP_NAME_LIST))]
        if is_current:
            group_entry_list.insert(2, (_FLUID_GROUP_NAME, -1))
        # 每组组头一个折叠按钮（无论查看哪个周目，默认只展开部位初体验组，其余全部收起）
        for fold_index, (group_name, group_index) in enumerate(group_entry_list):
            fold_key = f"{now_round}_{fold_index}"
            default_expand = group_index == 0
            now_expand = _fold_state.get(fold_key, default_expand)
            if now_expand:
                button_text = f"▼{group_name}"
            else:
                button_text = f"▶{group_name}"
            button_draw = draw.LeftButton(
                button_text,
                f"first_record_fold_{fold_key}",
                int(self.width / 3),
                cmd_func=_toggle_fold,
                args=(fold_key, default_expand),
            )
            self.draw_list.append(button_draw)
            self.return_list.append(button_draw.return_text)
            self.draw_list.append(line_feed)
            # 展开时绘制该分组的文本（体液组读实时数据，履历组读记录结构体）
            if now_expand:
                if group_index == -1:
                    group_text = _build_fluid_text(character_id)
                else:
                    group_text = build_group_text(first_record, group_index)
                if not group_text:
                    group_text = _("  无记录\n")
                group_draw = draw.NormalDraw()
                group_draw.text = group_text
                group_draw.width = width
                self.draw_list.append(group_draw)
            # 组与组之间以一个空行分隔
            self.draw_list.append(line_feed)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            label.draw()


class See_Character_First_Record_Panel:
    """
    显示角色属性面板中的性行为履历分页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = character_info_head.CharacterInfoHead(character_id, width)
        record_draw = FirstRecordText(character_id, width)
        self.draw_list: List = [
            head_draw,
            record_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        # 每帧先清空监听列表再收集（本面板含折叠按钮，不能省略）
        self.return_list = []
        for label in self.draw_list:
            label.draw()
            if hasattr(label, "return_list"):
                self.return_list.extend(label.return_list)
