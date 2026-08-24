from types import FunctionType
from Script.Core import cache_control, game_type, get_text, text_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

UP_GEN = 1
""" 谱系图向上显示的代数（上1代+中心+下2代，共4代） """
DOWN_GEN = 2
""" 谱系图向下显示的代数 """
GAP = 2
""" 相邻家庭块之间的最小间隔（半角单位），保证排版行的连线段互不粘连 """


def get_chara_name(character_id: int) -> str:
    """
    获取角色名（角色不存在时返回占位文本）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 角色名
    """
    if character_id in cache.character_data:
        return cache.character_data[character_id].name
    return _("（不在册）")


def get_valid_parent(character_id: int, parent_type: str) -> int:
    """
    获取角色的有效父/母id
    Keyword arguments:
    character_id -- 角色id
    parent_type -- "father" 或 "mother"
    Return arguments:
    int -- 父/母id，无效时返回-1
    """
    if character_id not in cache.character_data:
        return -1
    relationship = cache.character_data[character_id].relationship
    parent_id = relationship.father_id if parent_type == "father" else relationship.mother_id
    if parent_id == -1 or parent_id not in cache.character_data:
        return -1
    return parent_id


def chara_has_parents(character_id: int) -> bool:
    """
    判断角色是否有在册的父母
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否有父母
    """
    return get_valid_parent(character_id, "father") != -1 or get_valid_parent(character_id, "mother") != -1


def chara_has_children(character_id: int) -> bool:
    """
    判断角色是否有在册的孩子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否有孩子
    """
    if character_id not in cache.character_data:
        return False
    return len(get_valid_children(character_id)) > 0


def get_valid_children(character_id: int) -> list:
    """
    获取角色在册的孩子id列表（保持原顺序、去重）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    list -- 孩子id列表
    """
    if character_id not in cache.character_data:
        return []
    result = []
    for child_id in cache.character_data[character_id].relationship.child_id_list:
        if child_id in cache.character_data and child_id not in result:
            result.append(child_id)
    return result


def _get_other_parent(child_id: int, parent_id: int) -> int:
    """
    获取孩子相对某位家长的另一位家长id
    Keyword arguments:
    child_id -- 孩子id
    parent_id -- 已知家长id
    Return arguments:
    int -- 另一位家长id，无效或与已知家长相同时返回-1
    """
    relationship = cache.character_data[child_id].relationship
    other_id = relationship.mother_id if relationship.father_id == parent_id else relationship.father_id
    if other_id == parent_id or other_id == -1 or other_id not in cache.character_data:
        return -1
    return other_id


def _text_token(text: str, style: str = "") -> dict:
    """
    构造纯文本token
    Keyword arguments:
    text -- 文本
    style -- 绘制样式（空为标准样式）
    Return arguments:
    dict -- token字典
    """
    token = {"type": "text", "text": text}
    if style:
        token["style"] = style
    return token


def _person_token(character_id: int, center_id: int, more_flag: bool = False) -> dict:
    """
    构造人物token（面板渲染为可点击按钮，中心人物渲染为•前缀高亮文本；名后…表示图外还有未显示的父母或子女）
    Keyword arguments:
    character_id -- 角色id
    center_id -- 谱系图中心角色id
    more_flag -- 是否有图外未显示的父母/子女
    Return arguments:
    dict -- token字典
    """
    center_flag = character_id == center_id
    text = ("•" if center_flag else "") + get_chara_name(character_id) + ("…" if more_flag else "")
    return {"type": "person", "chara_id": character_id, "text": text, "is_center": center_flag}


def _token_width(token: dict) -> int:
    """
    计算token的显示宽度
    Keyword arguments:
    token -- token字典
    Return arguments:
    int -- 显示宽度（半角单位）
    """
    return text_handle.get_text_index(token["text"])


def _build_blood_depth(center_id: int) -> dict:
    """
    从中心向下BFS构建血缘代深字典（中心=0，子女=1，孙辈=2；多路径时取先到的浅层）
    Keyword arguments:
    center_id -- 中心角色id
    Return arguments:
    dict -- {角色id: 代深}
    """
    depth_data = {center_id: 0}
    now_layer = [center_id]
    for now_depth in range(1, DOWN_GEN + 1):
        next_layer = []
        for person_id in now_layer:
            for child_id in get_valid_children(person_id):
                if child_id not in depth_data:
                    depth_data[child_id] = now_depth
                    next_layer.append(child_id)
        now_layer = next_layer
    return depth_data


def _expand_person(person_id: int, depth: int, blood_depth: dict, placed_set: set, expand_flag: bool = True) -> dict:
    """
    构建人物节点并向下展开其夫妇框
    \n归属规则：孩子的另一位家长是更深的血缘节点时跳过该组（孩子挂在对方节点下），
    \n避免同一人因多条亲缘路径（父本恒为玩家）被重复放置；placed_set先到先得兜底
    Keyword arguments:
    person_id -- 人物id
    depth -- 当前向下代深（中心=0）
    blood_depth -- 血缘代深字典
    placed_set -- 已放置人物id集合
    expand_flag -- 是否向下展开（同辈等不展开的人物传False）
    Return arguments:
    dict -- 节点字典 {"chara_id", "more_flag", "boxes": [夫妇框]}
    """
    node = {"chara_id": person_id, "more_flag": False, "boxes": []}
    if not expand_flag or depth >= DOWN_GEN:
        # 到达显示深度下限：有孩子未显示时标记省略号
        node["more_flag"] = chara_has_children(person_id)
        return node
    group_order = []
    group_data = {}
    for child_id in get_valid_children(person_id):
        if child_id in placed_set:
            continue
        other_id = _get_other_parent(child_id, person_id)
        if other_id != -1 and other_id in blood_depth and blood_depth[other_id] > blood_depth.get(person_id, depth):
            continue
        if other_id not in group_data:
            group_data[other_id] = []
            group_order.append(other_id)
        group_data[other_id].append(child_id)
    for other_id in group_order:
        children_nodes = []
        for child_id in group_data[other_id]:
            if child_id in placed_set:
                continue
            placed_set.add(child_id)
            children_nodes.append(_expand_person(child_id, depth + 1, blood_depth, placed_set))
        if not children_nodes:
            continue
        # 配偶（右侧人物）自己的父母不在图中：有父母时标记省略号
        box = {
            "left_id": person_id,
            "left_more": False,
            "right_id": other_id,
            "right_more": other_id != -1 and chara_has_parents(other_id),
            "children": children_nodes,
        }
        node["boxes"].append(box)
    return node


def _build_family_blocks(center_id: int) -> list:
    """
    构建顶层家族块列表（分页以家族为单位，家族不可拆散）
    \n中心有父母时=单一父母树家族；无父母时=中心的每个夫妇框各为一个家族（玩家名按父本位置重复）
    Keyword arguments:
    center_id -- 中心角色id
    Return arguments:
    list -- 家族块列表，元素为 {"kind": "box"|"person", "box"/"node": ...}
    """
    blood_depth = _build_blood_depth(center_id)
    placed_set = {center_id}
    center_node = _expand_person(center_id, 0, blood_depth, placed_set)
    father_id = get_valid_parent(center_id, "father")
    mother_id = get_valid_parent(center_id, "mother")
    if father_id != -1 or mother_id != -1:
        # 父母树家族：连线语义要求同辈确实出自该夫妇（仅同父同母或同单亲的兄弟姐妹）
        left_id = father_id if father_id != -1 else mother_id
        right_id = mother_id if father_id != -1 else -1
        children_nodes = [center_node]
        for sibling_id in get_valid_children(left_id):
            if sibling_id in placed_set or _get_other_parent(sibling_id, left_id) != right_id:
                continue
            placed_set.add(sibling_id)
            children_nodes.append(_expand_person(sibling_id, 0, blood_depth, placed_set, expand_flag=False))
        # 父母行人物有自己的父母（祖辈不在图中）时标记省略号
        parent_box = {
            "left_id": left_id,
            "left_more": chara_has_parents(left_id),
            "right_id": right_id,
            "right_more": right_id != -1 and chara_has_parents(right_id),
            "children": children_nodes,
        }
        return [{"kind": "box", "box": parent_box}]
    if center_node["boxes"]:
        return [{"kind": "box", "box": now_box} for now_box in center_node["boxes"]]
    return [{"kind": "person", "node": center_node}]


def _measure_node(node: dict, center_id: int):
    """
    递归计算节点的显示宽度并重建token（写入node["width"]等字段）
    Keyword arguments:
    node -- 节点字典
    center_id -- 中心角色id
    """
    node["self_token"] = _person_token(node["chara_id"], center_id, node["more_flag"])
    if not node["boxes"]:
        node["width"] = _token_width(node["self_token"])
        return
    for now_box in node["boxes"]:
        _measure_box(now_box, center_id)
    node["width"] = sum(now_box["width"] for now_box in node["boxes"]) + GAP * (len(node["boxes"]) - 1)


def _measure_box(box: dict, center_id: int):
    """
    递归计算夫妇框的显示宽度并重建token（写入box["width"]/["couple_width"]/["tokens"]字段）
    Keyword arguments:
    box -- 夫妇框字典
    center_id -- 中心角色id
    """
    tokens = [_person_token(box["left_id"], center_id, box["left_more"])]
    if box["right_id"] != -1:
        # 夫妇连接符╤自带向下接头，排版行连线以其所在列为起点
        tokens.append(_text_token("╤"))
        tokens.append(_person_token(box["right_id"], center_id, box["right_more"]))
    box["tokens"] = tokens
    box["couple_width"] = sum(_token_width(token) for token in tokens)
    for child_node in box["children"]:
        _measure_node(child_node, center_id)
    children_width = sum(child_node["width"] for child_node in box["children"]) + GAP * (len(box["children"]) - 1)
    box["width"] = max(box["couple_width"], children_width)


def _measure_block(block: dict, center_id: int) -> int:
    """
    计算家族块的显示宽度
    Keyword arguments:
    block -- 家族块字典
    center_id -- 中心角色id
    Return arguments:
    int -- 显示宽度
    """
    if block["kind"] == "box":
        _measure_box(block["box"], center_id)
        return block["box"]["width"]
    _measure_node(block["node"], center_id)
    return block["node"]["width"]


_LINK_CHAR_MAP = {
    (True, True, True, True): "┼",
    (True, True, False, True): "├",
    (True, True, True, False): "┤",
    (True, False, True, True): "┴",
    (True, False, False, True): "└",
    (True, False, True, False): "┘",
    (False, True, True, True): "┬",
    (False, True, False, True): "┌",
    (False, True, True, False): "┐",
    (False, False, True, True): "─",
    (True, True, False, False): "│",
}
""" 排版行连线字形表：键为(上接、下接、向左延伸、向右延伸) """


def _add_link_cells(link_chars: dict, gen: int, drop_col: int, child_cols: list):
    """
    向排版行写入一个夫妇框的过渡连线字符（跨度限于该框内部，相邻框因GAP互不粘连）
    Keyword arguments:
    link_chars -- {代际: {列: 字符}} 排版行字符表
    gen -- 夫妇所在代际（连线连接gen与gen+1）
    drop_col -- 下坠点列（夫妇连接符╤所在列；无配偶时为人名中点列）
    child_cols -- 各子辈名字中点列（上接点）列表
    """
    if not child_cols:
        return
    child_col_set = set(child_cols)
    left_col = min(child_cols + [drop_col])
    right_col = max(child_cols + [drop_col])
    row_chars = link_chars.setdefault(gen, {})
    for now_col in range(left_col, right_col + 1):
        char_key = (now_col == drop_col, now_col in child_col_set, now_col > left_col, now_col < right_col)
        if char_key in _LINK_CHAR_MAP:
            row_chars[now_col] = _LINK_CHAR_MAP[char_key]


def _place_node(node: dict, start_col: int, gen: int, names_cells: dict, link_chars: dict) -> int:
    """
    自顶向下放置人物节点（写入名字行cell与排版行连线），返回其名字中点列供上一代连线
    Keyword arguments:
    node -- 节点字典（需已measure）
    start_col -- 起始列
    gen -- 所在代际（名字行序号）
    names_cells -- {代际: [(列, token)]} 名字行cell表
    link_chars -- {代际: {列: 字符}} 排版行字符表
    Return arguments:
    int -- 名字中点列（上接点）
    """
    if not node["boxes"]:
        names_cells.setdefault(gen, []).append((start_col, node["self_token"]))
        return start_col + node["width"] // 2
    cursor_col = start_col
    up_attach_col = start_col
    for box_index, now_box in enumerate(node["boxes"]):
        attach_col = _place_box(now_box, cursor_col, gen, names_cells, link_chars)
        if box_index == 0:
            up_attach_col = attach_col
        cursor_col += now_box["width"] + GAP
    return up_attach_col


def _place_box(box: dict, start_col: int, gen: int, names_cells: dict, link_chars: dict) -> int:
    """
    自顶向下放置夫妇框：夫妇文本与子块跨度互相近似居中，写入夫妇行cell、递归放置子辈并画排版行连线
    Keyword arguments:
    box -- 夫妇框字典（需已measure）
    start_col -- 起始列
    gen -- 夫妇所在代际（名字行序号）
    names_cells -- {代际: [(列, token)]} 名字行cell表
    link_chars -- {代际: {列: 字符}} 排版行字符表
    Return arguments:
    int -- 左侧人物名字中点列（供上一代连线的上接点）
    """
    couple_col = start_col + max(0, (box["width"] - box["couple_width"]) // 2)
    now_col = couple_col
    for token in box["tokens"]:
        names_cells.setdefault(gen, []).append((now_col, token))
        now_col += _token_width(token)
    left_center_col = couple_col + _token_width(box["tokens"][0]) // 2
    if box["right_id"] != -1:
        # 下坠点=夫妇连接符╤所在列（紧随左侧人物之后）
        drop_col = couple_col + _token_width(box["tokens"][0])
    else:
        # 无配偶（不在册）时无连接符，仍从人名中点下坠
        drop_col = couple_col + box["couple_width"] // 2
    children_width = sum(child_node["width"] for child_node in box["children"]) + GAP * (len(box["children"]) - 1)
    child_col = start_col + max(0, (box["width"] - children_width) // 2)
    child_attach_cols = []
    for child_node in box["children"]:
        child_attach_cols.append(_place_node(child_node, child_col, gen + 1, names_cells, link_chars))
        child_col += child_node["width"] + GAP
    _add_link_cells(link_chars, gen, drop_col, child_attach_cols)
    return left_center_col


def _collect_block_ids(block: dict) -> set:
    """
    收集家族块中显示的全部角色id（用于折叠时精确统计被隐藏的人数）
    Keyword arguments:
    block -- 家族块字典
    Return arguments:
    set -- 角色id集合
    """
    id_set = set()

    def _collect_node(node: dict):
        id_set.add(node["chara_id"])
        for now_box in node["boxes"]:
            _collect_box(now_box)

    def _collect_box(now_box: dict):
        id_set.add(now_box["left_id"])
        if now_box["right_id"] != -1:
            id_set.add(now_box["right_id"])
        for child_node in now_box["children"]:
            _collect_node(child_node)

    if block["kind"] == "box":
        _collect_box(block["box"])
    else:
        _collect_node(block["node"])
    return id_set


def _remove_one_leaf_from_box(box: dict) -> bool:
    """
    从夫妇框的最右侧削减一个显示元素（右侧折叠；每框至少保留1个孩子）
    Keyword arguments:
    box -- 夫妇框字典
    Return arguments:
    bool -- 是否成功削减
    """
    last_child = box["children"][-1]
    if last_child["boxes"]:
        return _remove_one_leaf_node(last_child)
    if len(box["children"]) > 1:
        box["children"].pop()
        return True
    return False


def _remove_one_leaf_node(node: dict) -> bool:
    """
    从人物节点的最右侧削减一个显示元素（末框削到最小后整框摘除，节点最终退化为单人）
    Keyword arguments:
    node -- 节点字典
    Return arguments:
    bool -- 是否成功削减
    """
    if not node["boxes"]:
        return False
    if _remove_one_leaf_from_box(node["boxes"][-1]):
        return True
    node["boxes"].pop()
    return True


def _fit_family_block(block: dict, max_width: int, center_id: int) -> int:
    """
    单个家族独占一页仍超宽时的兜底：从右侧逐个折叠显示元素直到放得下或不可再削
    Keyword arguments:
    block -- 家族块字典
    max_width -- 单页最大显示宽度
    center_id -- 中心角色id
    Return arguments:
    int -- 被完全隐藏的人物数（其余位置仍显示的人不计入）
    """
    ids_before = _collect_block_ids(block)
    while _measure_block(block, center_id) > max_width:
        if block["kind"] != "box" or not _remove_one_leaf_from_box(block["box"]):
            break
    _measure_block(block, center_id)
    return len(ids_before - _collect_block_ids(block))


def paginate_family_blocks(blocks: list, max_width: int, center_id: int) -> list:
    """
    以家族为单位对顶层家族块分页：从左到右贪心装填，家族永不拆散，一页至少一个家族
    Keyword arguments:
    blocks -- 家族块列表（需已measure）
    max_width -- 单页最大显示宽度
    center_id -- 中心角色id
    Return arguments:
    list -- 分页列表，每页为家族块列表
    """
    pages = []
    now_page_blocks = []
    now_page_width = 0
    for block in blocks:
        block_width = _measure_block(block, center_id)
        need_width = block_width if not now_page_blocks else GAP + block_width
        if now_page_blocks and now_page_width + need_width > max_width:
            pages.append(now_page_blocks)
            now_page_blocks = [block]
            now_page_width = block_width
        else:
            now_page_blocks.append(block)
            now_page_width += need_width
    if now_page_blocks:
        pages.append(now_page_blocks)
    return pages


def build_family_tree_chart(center_id: int, max_width: int, page_index: int = 0) -> dict:
    """
    以某角色为中心构建带完整连线的传统家谱图（上1代+中心+下2代共4代，代间夹排版行；超宽时按家族分页）
    \n列位以 text_handle.get_text_index（wcwidth）为单位制，跨行对齐依赖等距更纱黑体的字符度量
    Keyword arguments:
    center_id -- 中心角色id
    max_width -- 单页最大显示宽度
    page_index -- 页码（0起，越界自动钳位）
    Return arguments:
    dict -- {"width": 当前页图宽, "total_page": 总页数, "now_page": 当前页码,
             "rows": [{"type": "names"|"link", "cells": [{"col": 列位, "token": token}]}]}
    """
    empty_chart = {"width": 0, "total_page": 1, "now_page": 0, "rows": []}
    if center_id not in cache.character_data:
        return empty_chart
    blocks = _build_family_blocks(center_id)
    for block in blocks:
        _measure_block(block, center_id)
    pages = paginate_family_blocks(blocks, max_width, center_id)
    if not pages:
        return empty_chart
    total_page = len(pages)
    now_page = min(max(page_index, 0), total_page - 1)
    page_blocks = pages[now_page]

    # 单家族独占一页仍超宽时的兜底折叠
    hidden_count = 0
    if len(page_blocks) == 1 and _measure_block(page_blocks[0], center_id) > max_width:
        hidden_count = _fit_family_block(page_blocks[0], max_width, center_id)

    # 放置当前页的各家族块并收集名字行/排版行
    names_cells = {}
    link_chars = {}
    cursor_col = 0
    for block in page_blocks:
        if block["kind"] == "box":
            _place_box(block["box"], cursor_col, 0, names_cells, link_chars)
            cursor_col += block["box"]["width"] + GAP
        else:
            _place_node(block["node"], cursor_col, 0, names_cells, link_chars)
            cursor_col += block["node"]["width"] + GAP
    chart_width = cursor_col - GAP if page_blocks else 0

    # 兜底折叠的隐藏人数以行尾省略号标注在最深名字行末
    if hidden_count:
        deepest_gen = max(names_cells)
        names_cells[deepest_gen].append((chart_width + 1, _text_token(_("…(+{0}人)").format(hidden_count), style="gold_enrod")))

    # 按 名字行/排版行 交替组装输出行
    rows = []
    for gen in sorted(names_cells):
        row_cells = [{"col": col, "token": token} for col, token in sorted(names_cells[gen], key=lambda cell: cell[0])]
        rows.append({"type": "names", "cells": row_cells})
        if gen in link_chars and link_chars[gen]:
            rows.append({"type": "link", "cells": _merge_link_chars(link_chars[gen])})
    return {"width": chart_width, "total_page": total_page, "now_page": now_page, "rows": rows}


def _merge_link_chars(row_chars: dict) -> list:
    """
    把排版行的逐列字符合并为连续文本cell（减少绘制次数）
    Keyword arguments:
    row_chars -- {列: 字符}
    Return arguments:
    list -- cell列表 [{"col": 起始列, "token": 文本token}]
    """
    cells = []
    now_start = -1
    now_text = ""
    for col in sorted(row_chars):
        if now_start != -1 and col == now_start + text_handle.get_text_index(now_text):
            now_text += row_chars[col]
        else:
            if now_text:
                cells.append({"col": now_start, "token": _text_token(now_text)})
            now_start = col
            now_text = row_chars[col]
    if now_text:
        cells.append({"col": now_start, "token": _text_token(now_text)})
    return cells
