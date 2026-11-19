# -*- coding: UTF-8 -*-
"""
静态检查系统 - 全局状态快照序列化
将调用方传入的cache递归转换为JSON可序列化的数据结构，供检查失败时随日志一并落盘，方便事后调试。
"""
import datetime
import json

# 快照时排除的Cache顶层字段名单
# 这些字段要么是静态配置数据（游戏启动后不再随玩家操作变化，快照价值低且体积巨大），
# 要么是纯渲染/绘制用的中间缓存（不反映游戏逻辑状态，只会让快照膨胀并干扰阅读）
EXCLUDED_TOP_LEVEL_FIELDS = {
    "map_data",  # 地图静态数据
    "npc_tem_data",  # npc模板静态数据
    "random_npc_list",  # 随机npc模板数据
    "recipe_data",  # 菜谱静态数据
    "sun_phase",  # 太阳位置缓存表
    "moon_phase",  # 月相缓存表
    "wframe_mouse",  # 主页监听控制流程用变量组（渲染相关）
    "cmd_data",  # cmd绘制数据
    "input_cache_draft",  # 玩家正在编辑但尚未发送的输入草稿
    "output_text_style",  # 富文本记录输出样式临时缓存
    "text_style_position",  # 富文本回溯样式记录用定位
    "daily_intsruce",  # 每日指令文本流水（长期游玩可达MB级；最近行为已在日志条目头部单列，流水全文无排查价值）
    "taiggered_event_record",  # 已触发事件id全集（只增流水，与状态自洽无关）
}
# 字段名前缀黑名单：以这些前缀开头的字段均为渲染缓存/Web模式专用中间数据，一并排除
EXCLUDED_FIELD_PREFIXES = ("web_", "current_", "text_")

# rhodes_island内部排除的子字段：当日随机生成的内容数据（病人队列含大量生成文本，实测可达1MB），
# 每日重新生成、无任何检查依赖、与状态自洽无关
EXCLUDED_RHODES_ISLAND_FIELDS = {"medical_patients_today"}

# 递归转换时的最大深度，超过后直接使用repr兜底，防止极端嵌套结构导致快照过大或递归过深
MAX_DEPTH = 15

# 单次快照最多转储的涉事角色数量：首次检查时若存在大范围失败（如某检查对上百个角色逐一命中），
# 涉事角色并集可达数百人，全部转储仍会让单份快照膨胀到数MB。超出上限的角色只记id不转储数据
MAX_SNAPSHOT_CHARACTERS = 30


def _is_excluded_top_level_field(field_name: str) -> bool:
    """
    参数:
        field_name (str): Cache对象的顶层字段名
    返回值:
        bool: 是否应当在快照中排除该字段
    功能:
        判断某个Cache顶层字段是否命中排除名单或排除前缀，命中则该字段不进入快照
    """
    if field_name in EXCLUDED_TOP_LEVEL_FIELDS:
        return True
    return field_name.startswith(EXCLUDED_FIELD_PREFIXES)


def _to_json_safe(value, depth: int, visited: set):
    """
    参数:
        value (Any): 待转换的任意对象
        depth (int): 当前递归深度，从0开始
        visited (set): 已访问对象id集合，用于检测循环引用
    返回值:
        Any: 转换后的JSON可序列化数据（仅由dict/list/str/int/float/bool/None构成）
    功能:
        递归地将任意Python对象转换为JSON可序列化结构：
        基础类型原样返回；datetime转为isoformat字符串；set/tuple转为列表（能排序则排序，保证快照可复现比较）；
        dict的键统一转为字符串；带__dict__的自定义对象取其字段字典递归转换；
        出现循环引用、超过最大深度或转换失败时，均以repr(value)兜底，保证函数不会抛出异常
    """
    # 基础可直接JSON化的类型
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    # 日期时间类型转为可读字符串
    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
        return value.isoformat()
    # 深度超限，直接使用repr兜底，避免递归过深
    if depth >= MAX_DEPTH:
        try:
            return repr(value)
        except Exception:
            return "<不可repr对象>"
    # 循环引用检测：容器与自定义对象才需要记录，基础类型不会成环
    obj_id = id(value)
    if obj_id in visited:
        return f"<循环引用: {type(value).__name__}>"
    if isinstance(value, dict):
        visited = visited | {obj_id}
        result = {}
        for k, v in value.items():
            try:
                safe_key = k if isinstance(k, str) else repr(k)
                result[safe_key] = _to_json_safe(v, depth + 1, visited)
            except Exception as e:
                result[repr(k)] = f"<转换失败: {e}>"
        return result
    if isinstance(value, (set, frozenset, tuple, list)):
        visited = visited | {obj_id}
        try:
            items = list(value)
            # 集合/元组尽量排序后输出，保证同一状态下多次快照结果一致，便于anti-spam做去重比较
            if isinstance(value, (set, frozenset)):
                try:
                    items = sorted(items)
                except TypeError:
                    pass
            return [_to_json_safe(item, depth + 1, visited) for item in items]
        except Exception as e:
            return f"<转换失败: {e}>"
    # 自定义对象：取其__dict__字段递归转换
    if hasattr(value, "__dict__"):
        visited = visited | {obj_id}
        try:
            return _to_json_safe(vars(value), depth + 1, visited)
        except Exception as e:
            try:
                return repr(value)
            except Exception:
                return f"<不可repr对象: {e}>"
    # 其余一律使用repr兜底（如函数、模块、枚举等）
    try:
        return repr(value)
    except Exception:
        return "<不可repr对象>"


def build_snapshot(cache, involved_character_ids=None) -> dict:
    """
    参数:
        cache: 当前游戏缓存对象
        involved_character_ids (Set[int]): 本次失败涉及的角色id集合，默认为None时character_data全量保留
    返回值:
        dict: 当前全局状态的JSON可序列化快照
    功能:
        将传入cache的顶层字段逐一转换为JSON可序列化数据（排除静态配置/渲染缓存字段，见EXCLUDED_TOP_LEVEL_FIELDS）。
        character_data字段在传入involved_character_ids时仅保留涉事角色与玩家（全量354个角色的快照可达数MB，
        而排查一次失败通常只需要涉事角色的数据），未传入时全量保留；
        scene_data字段仅保留角色集合非空的场景（角色所在位置是排查问题的关键信息，空场景则无排查价值）
    """
    if cache is None:
        return {}
    snapshot = {}
    for field_name, field_value in vars(cache).items():
        if _is_excluded_top_level_field(field_name):
            continue
        if field_name == "scene_data":
            # 仅保留角色集合非空的场景，过滤掉大量空场景以控制快照体积
            filtered_scene_data = {scene_path: scene for scene_path, scene in field_value.items() if getattr(scene, "character_list", None)}
            snapshot[field_name] = _to_json_safe(filtered_scene_data, 0, set())
            continue
        if field_name == "rhodes_island":
            # 整体转换后剔除当日生成的内容型子字段，以占位说明替代
            ri_snapshot = _to_json_safe(field_value, 0, set())
            if isinstance(ri_snapshot, dict):
                for sub_field in EXCLUDED_RHODES_ISLAND_FIELDS:
                    if sub_field in ri_snapshot:
                        ri_snapshot[sub_field] = "<当日生成的内容数据，已从快照排除>"
            snapshot[field_name] = ri_snapshot
            continue
        if field_name == "character_data" and involved_character_ids is not None and isinstance(field_value, dict):
            # 仅保留涉事角色与玩家（id 0）的完整数据，且总数不超过MAX_SNAPSHOT_CHARACTERS，其余角色只记id
            keep_ids = sorted((set(involved_character_ids) | {0}) & set(field_value))
            dumped_ids = keep_ids[:MAX_SNAPSHOT_CHARACTERS]
            filtered_character_data = {cid: field_value[cid] for cid in dumped_ids}
            snapshot[field_name] = _to_json_safe(filtered_character_data, 0, set())
            snapshot["character_data_omitted"] = f"共{len(field_value)}个角色，涉事{len(keep_ids)}个，仅转储前{len(dumped_ids)}个{dumped_ids}，未转储的涉事角色id={keep_ids[MAX_SNAPSHOT_CHARACTERS:]}"
            continue
        try:
            snapshot[field_name] = _to_json_safe(field_value, 0, set())
        except Exception as e:
            snapshot[field_name] = f"<字段快照失败: {e}>"
    return snapshot


def _json_default_fallback(obj):
    """
    参数:
        obj (Any): json.dumps遇到的无法直接序列化的对象
    返回值:
        str: 该对象的repr字符串
    功能:
        作为json.dumps的default兜底函数，理论上build_snapshot已将所有内容转换为JSON安全类型，
        此函数仅作为双重保险，防止个别遗漏对象导致dump_snapshot_json抛出异常
    """
    try:
        return repr(obj)
    except Exception:
        return "<不可序列化对象>"


def dump_snapshot_json(cache, involved_character_ids=None) -> str:
    """
    参数:
        cache: 当前游戏缓存对象
        involved_character_ids (Set[int]): 本次失败涉及的角色id集合，默认为None时character_data全量保留
    返回值:
        str: 当前全局状态快照的JSON字符串（ensure_ascii=False，保留中文可读性）
    功能:
        调用build_snapshot获取快照字典，并序列化为紧凑的单行JSON字符串，供写入日志文件
    """
    snapshot = build_snapshot(cache, involved_character_ids)
    try:
        return json.dumps(snapshot, ensure_ascii=False, default=_json_default_fallback)
    except Exception as e:
        return f"<快照序列化失败: {e}>"
