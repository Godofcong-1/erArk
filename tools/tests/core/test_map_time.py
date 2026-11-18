# -*- coding: UTF-8 -*-
"""地图、寻路与游戏时钟：地图缓存与源文件一致、场景/地图归属、通行表与标签、地图内最短路与全场景寻路表、character_move 与场景移动记账、通用移动模块与移动状态机、常用场景查询、季月时钟推进与日期工具"""
from _bootstrap import *  # noqa: F401,F403

import collections
import heapq
import re

from Script.Design import attr_text, character_move
from Script.StateMachine import default as state_machine_default
from Script.System.Dormitory_System import common as dormitory_common

SEP = os.sep
""" 场景路径字符串的分隔符（与 map_handle 一致，用 os.sep） """
TERRA = "泰拉"
""" 泰拉大地图（基地导航用，不参与罗德岛内寻路） """
T = datetime.datetime
""" 时间构造简写 """


# ==== 工具 ====
def path_list(scene_path_str: str) -> list:
    """
    场景路径字符串 → 场景路径列表
    Keyword arguments:
    scene_path_str -- 场景路径字符串
    Return arguments:
    list -- 场景路径列表
    """
    return map_handle.get_map_system_path_for_str(scene_path_str)


def true_scene_str(path: list) -> str:
    """
    把「地图路径 + 节点名」解析成真实场景路径字符串（节点是子地图时取其入口 0）
    get_scene_path_for_true 会就地 append 入参，这里先复制一份
    Keyword arguments:
    path -- 地图路径 + 节点名
    Return arguments:
    str -- 真实场景路径字符串
    """
    return scene_str(map_handle.get_scene_path_for_true(list(path)))


def node_list_of_scene(scene_path: list) -> list:
    """
    场景在哪些地图里充当节点：所在地图里的自身节点；相对位置为 "0"（地图入口）时，它同时是本地图在上级地图里的那个节点，逐级向上
    Keyword arguments:
    scene_path -- 场景路径列表
    Return arguments:
    list -- [(地图路径列表, 节点名)]
    """
    node_list = []
    now_path = list(scene_path)
    while now_path:
        node_list.append((now_path[:-1], now_path[-1]))
        if now_path[-1] != "0" or len(now_path) < 2:
            break
        now_path = now_path[:-1]
    return node_list


def build_step_graph() -> dict:
    """
    按各地图的通行表（path_edge）展开成场景级的一步可达图：场景 → {一步能到的场景: 耗时}
    跨地图只能经由各级入口 "0"，这正是 data/map 的设计
    Keyword arguments:
    无
    Return arguments:
    dict -- {场景路径字符串: {相邻场景路径字符串: 移动耗时}}
    """
    graph = {}
    for now_scene_str in cache.scene_data:
        neighbor = {}
        for map_path, node in node_list_of_scene(path_list(now_scene_str)):
            map_path_str = scene_str(map_path)
            if map_path_str not in cache.map_data or node not in cache.map_data[map_path_str].path_edge:
                continue
            for target_node, need_time in cache.map_data[map_path_str].path_edge[node].items():
                target_str = true_scene_str(map_path + [target_node])
                if target_str != now_scene_str and (target_str not in neighbor or need_time < neighbor[target_str]):
                    neighbor[target_str] = need_time
        graph[now_scene_str] = neighbor
    return graph


def shortest_from(graph: dict, start: str) -> dict:
    """
    最短路（Dijkstra），独立于游戏里的 dijkstra 模块，作为对照
    Keyword arguments:
    graph -- {节点: {可达节点: 耗时}}
    start -- 起点
    Return arguments:
    dict -- {节点: 起点到该节点的最短耗时}，不可达的节点不在其中
    """
    distance = {start: 0}
    queue = [(0, start)]
    while queue:
        now_distance, now_node = heapq.heappop(queue)
        if now_distance > distance[now_node]:
            continue
        for next_node, need_time in graph.get(now_node, {}).items():
            new_distance = now_distance + need_time
            if new_distance < distance.get(next_node, float("inf")):
                distance[next_node] = new_distance
                heapq.heappush(queue, (new_distance, next_node))
    return distance


def load_source_map_data() -> tuple:
    """
    直接读 data/map 下的源文件（Map.json 的 PathEdge 与 Scene.json 所在目录），用来和 pickle 缓存比对
    Keyword arguments:
    无
    Return arguments:
    tuple -- ({地图路径字符串: PathEdge}, {场景路径字符串})
    """
    from Script.Core import json_handle

    map_edge = {}
    scene_set = set()
    map_root = os.path.join("data", "map")
    for now_dir, dir_list, file_list in os.walk(map_root):
        dir_list.sort()
        rel_path = os.path.relpath(now_dir, map_root)
        now_path = [] if rel_path == "." else rel_path.split(os.sep)
        if "Map.json" in file_list:
            map_edge[scene_str(now_path)] = json_handle.load_json(os.path.join(now_dir, "Map.json"))["PathEdge"]
        if "Scene.json" in file_list:
            scene_set.add(scene_str(now_path))
    return map_edge, scene_set


def scene_list_mismatch() -> list:
    """
    全场景角色名单与全角色 position 的一致性：每个角色恰好出现在一个场景的名单里，且就是它 position 所指的场景
    Keyword arguments:
    无
    Return arguments:
    list -- 不一致项
    """
    bad = []
    for now_scene_str, scene_data in cache.scene_data.items():
        for character_id in scene_data.character_list:
            if character_id not in cache.character_data or scene_str(cache.character_data[character_id].position) != now_scene_str:
                bad.append(("名单多出", now_scene_str, character_id))
    for character_id, character_data in cache.character_data.items():
        count = sum(1 for scene_data in cache.scene_data.values() if character_id in scene_data.character_list)
        if count != 1:
            bad.append(("出现次数", character_id, count, character_data.position))
    return bad


def make_npc(cid: int, name: str, position: list) -> game_type.Character:
    """
    造一个移动测试用干员：在 make_character 的基础上补道具与角色设置（钥匙判定与跟随等待会直接下标取）
    Keyword arguments:
    cid -- 角色id
    name -- 角色名
    position -- 初始场景路径列表
    Return arguments:
    game_type.Character -- 角色对象
    """
    character_data = make_character(cid, name, position=position)
    character_data.item = attr_calculation.get_item_zero(character_data.item)
    character_data.chara_setting = attr_calculation.get_chara_setting_zero()
    return character_data


def walk_clock(start: datetime.datetime, step_count: int, **step) -> list:
    """
    从 start 开始，用 sub_time_now 按固定步长推进时钟，记录每一步后的游戏时间
    Keyword arguments:
    start -- 起始时间
    step_count -- 步数
    step -- 传给 sub_time_now 的步长（minute / hour / day）
    Return arguments:
    list -- [起始时间, 第1步后, ..., 第step_count步后]
    """
    set_time(start)
    result = [cache.game_time]
    for _step in range(step_count):
        game_time.sub_time_now(**step)
        result.append(cache.game_time)
    return result


graph = build_step_graph()
""" 场景级一步可达图 """
non_terra_list = [s for s in cache.scene_data if path_list(s)[0] != TERRA]
""" 罗德岛内（泰拉大地图以外）的全部场景 """
non_terra_set = set(non_terra_list)
SCENE_OFFICE = ["中枢", "博士办公室"]
""" 博士办公室 """
SCENE_OUT_CORRIDOR = ["宿舍", "1区", "外走廊"]
""" 宿舍 1 区外走廊，101~116 号房都与它相邻 """
SCENE_DORM_102 = ["宿舍", "1区", "102"]
""" 另一间宿舍（与外走廊相邻） """
SCENE_DORM_103 = ["宿舍", "1区", "103"]
""" 第三间宿舍 """
SCENE_CENTER_DOOR = ["中枢", "0"]
""" 控制中枢入口 """
terra_scene_list = sorted(s for s in cache.scene_data if path_list(s)[0] == TERRA)
""" 泰拉大地图的场景 """

# ==== 1. 地图缓存与源文件 ====
section("地图缓存与 data/map 源文件")
source_edge, source_scene_set = load_source_map_data()
check("缓存的场景集合 = data/map 下全部 Scene.json（不一致请删 data/SceneData 等四个缓存重建）", source_scene_set == set(cache.scene_data),
      (sorted(source_scene_set - set(cache.scene_data))[:10], sorted(set(cache.scene_data) - source_scene_set)[:10]))
edge_diff = [m for m in sorted(set(source_edge) | set(cache.map_data)) if m not in source_edge or m not in cache.map_data or source_edge[m] != cache.map_data[m].path_edge]
check("缓存的各地图通行表 = Map.json 的 PathEdge", not edge_diff, edge_diff[:20])
check("寻路表 data/ScenePath 的场景键 = 全部场景", set(map_handle.scene_path_edge) == set(cache.scene_data),
      len(set(map_handle.scene_path_edge) ^ set(cache.scene_data)))
map_dir = os.path.join(ROOT, "data", "map")
check("地图文件路径 → 地图系统路径（常规安装目录）",
      map_config.get_map_system_path_for_path(os.path.join(map_dir, "宿舍", "1区", "Map.json")) == ["宿舍", "1区"]
      and map_config.get_map_system_path_for_path(os.path.join(map_dir, "Map.json")) == [])
check("地图文件路径 → 地图系统路径：安装目录名里含 map 字样时也不出错",
      map_config.get_map_system_path_for_path(os.path.join("C:" + SEP, "Users", "maple", "erArk", "data", "map", "宿舍", "1区", "Map.json")) == ["宿舍", "1区"],
      map_config.get_map_system_path_for_path(os.path.join("C:" + SEP, "Users", "maple", "erArk", "data", "map", "宿舍", "1区", "Map.json")))

# ==== 2. 场景与地图的归属 ====
section("场景与地图的归属")
bad = []
for now_scene_str, scene_data in cache.scene_data.items():
    now_path = path_list(now_scene_str)
    if scene_str(now_path) != now_scene_str or scene_data.scene_path != now_scene_str or map_handle.get_scene_path_for_true(list(now_path)) != now_path:
        bad.append(now_scene_str)
check("场景路径字符串 ↔ 列表互转一致，scene_path 字段等于键", not bad, bad[:20])
bad = []
for now_scene_str in cache.scene_data:
    now_path = path_list(now_scene_str)
    map_path_str = scene_str(now_path[:-1])
    if map_handle.get_map_for_path(now_path) != now_path[:-1] or map_path_str not in cache.map_data or now_path[-1] not in cache.map_data[map_path_str].path_edge:
        bad.append(now_scene_str)
check("每个场景都是其所在地图的一个节点", not bad, bad[:20])
bad = []
for now_scene_str in cache.scene_data:
    now_path = path_list(now_scene_str)
    if len(now_path) < 2 or any(scene_str(now_path[:i]) not in cache.map_data for i in range(0, len(now_path))):
        bad.append(now_scene_str)
        continue
    try:
        text = attr_text.get_scene_path_text(now_path)
        if not text.endswith(_(cache.scene_data[now_scene_str].scene_name)) or "-" not in text:
            bad.append((now_scene_str, text))
    except Exception as error:  # 地址文本是各面板都在用的显示，任何异常都算失败
        bad.append((now_scene_str, repr(error)))
check("每一级上层路径都是已载入的地图，地址文本（地图名-…-场景名）都能生成", not bad, bad[:20])
check("地址文本样例：宿舍区-宿舍1区-宿舍101房", attr_text.get_scene_path_text(SCENE_DORM) == _("宿舍区") + "-" + _("宿舍1区") + "-" + _("宿舍101房"),
      attr_text.get_scene_path_text(SCENE_DORM))
bad = []
for map_path_str, map_data in cache.map_data.items():
    for node in map_data.path_edge:
        try:
            if true_scene_str(path_list(map_path_str) + [node] if map_path_str else [node]) not in cache.scene_data:
                bad.append((map_path_str, node))
        except RecursionError:
            bad.append((map_path_str, node, "RecursionError"))
check("每个地图节点都能解析为真实场景（子地图节点取其入口 0）", not bad, bad[:20])
bad = []
for map_path_str in cache.map_data:
    if map_path_str == "" or path_list(map_path_str)[0] == TERRA:
        continue
    now_path = path_list(map_path_str)
    parent_str = scene_str(now_path[:-1])
    if parent_str not in cache.map_data or now_path[-1] not in cache.map_data[parent_str].path_edge:
        bad.append(map_path_str)
check("每张子地图都挂在上级地图的通行表上（泰拉大地图除外）", not bad, bad[:20])
check("泰拉大地图与罗德岛不连通（寻路预计算按设计跳过它）", TERRA in cache.map_data and TERRA not in cache.map_data[""].path_edge and len(terra_scene_list) > 0)
terra_by_name = sorted(s for s in cache.scene_data if TERRA in s or _(TERRA) in s)
check("路径里带「泰拉」字样的场景都在泰拉大地图里（寻路预计算按子串跳过泰拉，别处的场景名带泰拉会被误跳过）", terra_by_name == terra_scene_list,
      sorted(set(terra_by_name) ^ set(terra_scene_list))[:20])

# ==== 3. 通行表 ====
section("地图通行表")
missing = []
not_positive = []
one_way = []
uneven = []
for map_path_str, map_data in cache.map_data.items():
    for node, edge in map_data.path_edge.items():
        for target_node, need_time in edge.items():
            if target_node not in map_data.path_edge:
                missing.append((map_path_str, node, target_node))
                continue
            if not isinstance(need_time, int) or need_time <= 0:
                not_positive.append((map_path_str, node, target_node, need_time))
            back_edge = map_data.path_edge[target_node]
            if node not in back_edge:
                one_way.append((map_path_str, node, target_node))
            elif back_edge[node] != need_time and node < target_node:
                uneven.append((map_path_str, node, target_node, need_time, back_edge[node]))
check("通行边的终点都是本地图节点", not missing, missing[:20])
check("通行耗时都是正整数", not not_positive, not_positive[:20])
check("通行边都是双向的（新增场景要加双向边，见地图系统.md）", not one_way, one_way[:20])
# 曾有文职区入口↔外走廊（去 2 回 1）、大地图无尽冰原↔萨米（去 2 回 1，导航面板按它算燃料与天数）两条来回不一致，已统一为 1 与 2
check("同一条边两个方向耗时相同", not uneven, uneven[:20])
bad = []
for map_path_str, map_data in cache.map_data.items():
    node_set = set(map_data.path_edge)
    if not node_set:
        bad.append((map_path_str, "空地图"))
        continue
    first_node = sorted(node_set)[0]
    reverse_edge = collections.defaultdict(dict)
    for node, edge in map_data.path_edge.items():
        for target_node, need_time in edge.items():
            reverse_edge[target_node][node] = need_time
    forward = set(shortest_from(map_data.path_edge, first_node))
    backward = set(shortest_from(reverse_edge, first_node))
    if forward != node_set or backward != node_set:
        bad.append((map_path_str, sorted(node_set - forward), sorted(node_set - backward)))
check("每张地图内任意两个节点互相可达", not bad, bad[:20])
bad = []
for map_path_str, map_data in cache.map_data.items():
    for draw_line in map_data.map_draw.draw_text:
        for draw_text in draw_line.draw_list:
            if getattr(draw_text, "is_button", False) and draw_text.text not in map_data.path_edge:
                bad.append((map_path_str, draw_text.text))
check("AA 地图上的按钮都是本地图节点（否则点击时 get_scene_path_for_true 无限递归）", not bad, bad[:20])

# ==== 4. 场景属性与标签 ====
section("场景属性与标签")
bad = []
for now_scene_str, scene_data in cache.scene_data.items():
    if (scene_data.close_type not in (0, 1, 2) or scene_data.room_area not in (0, 1, 2, 3) or scene_data.have_furniture not in (0, 1, 2, 3)
            or not scene_data.scene_name or not scene_data.scene_tag or "" in scene_data.scene_tag or not isinstance(scene_data.character_list, set)):
        bad.append((now_scene_str, scene_data.close_type, scene_data.room_area, scene_data.have_furniture, scene_data.scene_tag))
check("场景属性取值合法（关门类型0~2、面积0~3、家具0~3、名字与标签非空、角色名单为 set）", not bad, bad[:20])
bad = []
for tag, scene_list in constant.place_data.items():
    if len(scene_list) != len(set(scene_list)):
        bad.append((tag, "重复"))
    for now_scene_str in scene_list:
        if now_scene_str not in cache.scene_data or tag not in cache.scene_data[now_scene_str].scene_tag:
            bad.append((tag, now_scene_str))
for now_scene_str, scene_data in cache.scene_data.items():
    for tag in scene_data.scene_tag:
        if now_scene_str not in constant.place_data.get(tag, []):
            bad.append((now_scene_str, tag, "倒排表缺"))
check("场景标签倒排表 place_data 与各场景的标签一一对应", not bad, bad[:20])
code_tag_set = set()
for now_dir, dir_list, file_list in os.walk("Script"):
    dir_list.sort()
    for file_name in sorted(file_list):
        if file_name.endswith(".py"):
            with open(os.path.join(now_dir, file_name), encoding="utf-8") as source_file:
                source_text = source_file.read()
            code_tag_set.update(re.findall(r"place_data\[\s*[\"']([A-Za-z_0-9]+)[\"']\s*\]", source_text))
            code_tag_set.update(re.findall(r"place_data\.get\(\s*[\"']([A-Za-z_0-9]+)[\"']", source_text))
check("代码里按字面量取用的场景标签在地图数据里都有场景", len(code_tag_set) > 30 and all(constant.place_data.get(tag) for tag in code_tag_set),
      sorted(tag for tag in code_tag_set if not constant.place_data.get(tag)))
bad = []
special_rest_room_count = 0
for now_scene_str in constant.place_data.get("Rest_Room", []):
    for tag in cache.scene_data[now_scene_str].scene_tag:
        match = re.match(r"^(.*)_(\d+)$", tag)
        if not match:
            continue
        prefix, tag_id = match.group(1), int(match.group(2))
        if (prefix == "Nation" and tag_id in game_config.config_nation) or (prefix == "Birthplace" and tag_id in game_config.config_birthplace):
            special_rest_room_count += 1
            continue
        bad.append((now_scene_str, cache.scene_data[now_scene_str].scene_name, tag))
check("休息室上带编号的专属标签都是 Nation_<存在的势力id> / Birthplace_<存在的出身地id>（MOVE_TO_REST_ROOM 按这两种写法拼标签找专属休息室）",
      not bad and special_rest_room_count > 0, bad[:20])

# ==== 5. 地图内最短路 sorted_path ====
section("地图内最短路 sorted_path")
bad_shape = []
bad_time = []
for map_path_str, map_data in cache.map_data.items():
    edge = map_data.path_edge
    for start_node in edge:
        distance = shortest_from(edge, start_node)
        for target_node in edge:
            target_path = map_data.sorted_path.get(start_node, {}).get(target_node)
            if target_path is None:
                bad_shape.append((map_path_str, start_node, target_node, "缺"))
                continue
            if target_node == start_node:
                if target_path.path:
                    bad_shape.append((map_path_str, start_node, target_node, target_path.path))
                continue
            node_path = list(target_path.path)
            prev_node = start_node
            cost = 0
            for node in node_path:
                if node not in edge[prev_node]:
                    cost = None
                    break
                cost += edge[prev_node][node]
                prev_node = node
            if cost is None or not node_path or node_path[-1] != target_node or cost != distance.get(target_node):
                bad_shape.append((map_path_str, start_node, target_node, node_path, cost, distance.get(target_node)))
                continue
            step_time = [edge[a][b] for a, b in zip([start_node] + node_path[:-1], node_path)]
            if list(target_path.time) != step_time:
                bad_time.append((map_path_str, start_node, target_node, node_path, list(target_path.time), step_time))
check("地图内最短路：覆盖全部节点对，终点正确、相邻两步有边、总耗时等于最短距离", not bad_shape, bad_shape[:20])
check("地图内最短路：time[i] 是走到 path[i] 那一步的耗时（identical_map_move 取 path[0] 配 time[0]）", not bad_time,
      f"共{len(bad_time)}处 " + str(bad_time[:6]))

# ==== 6. 全场景寻路表 scene_path_edge ====
section("全场景寻路表 scene_path_edge")
bad = []
for now_scene_str in cache.scene_data:
    target_dict = map_handle.scene_path_edge.get(now_scene_str)
    expect_set = (non_terra_set - {now_scene_str}) if now_scene_str in non_terra_set else set()
    if target_dict is None or set(target_dict) != expect_set:
        bad.append((now_scene_str, None if target_dict is None else len(target_dict), len(expect_set)))
check("寻路表覆盖：罗德岛内任意两个不同场景都有条目，泰拉大地图场景为空表", not bad, bad[:20])
bad_step = []
bad_step_time = []
for now_scene_str in non_terra_list:
    for target_str, (next_path, need_time) in map_handle.scene_path_edge.get(now_scene_str, {}).items():
        next_str = scene_str(next_path)
        if next_str not in graph[now_scene_str]:
            bad_step.append((now_scene_str, target_str, next_str))
        elif graph[now_scene_str][next_str] != need_time:
            bad_step_time.append((now_scene_str, target_str, next_str, need_time, graph[now_scene_str][next_str]))
check("寻路表的下一步都是相邻场景", not bad_step, bad_step[:20])
check("寻路表每一步的耗时 = 通行表上这条边的耗时", not bad_step_time, f"共{len(bad_step_time)}处 " + str(bad_step_time[:8]))
reverse_graph = collections.defaultdict(dict)
for now_scene_str, neighbor in graph.items():
    for next_str, need_time in neighbor.items():
        reverse_graph[next_str][now_scene_str] = need_time
loop_bad = []
dist_bad = []
for target_str in non_terra_list:
    distance = shortest_from(reverse_graph, target_str)
    route_cost = {target_str: 0}
    for start_str in non_terra_list:
        chain = []
        now_str = start_str
        while now_str not in route_cost:
            if now_str in chain or now_str not in map_handle.scene_path_edge or target_str not in map_handle.scene_path_edge[now_str]:
                loop_bad.append((start_str, target_str, now_str))
                break
            chain.append(now_str)
            now_str = scene_str(map_handle.scene_path_edge[now_str][target_str][0])
        else:
            for node_str in reversed(chain):
                next_str = scene_str(map_handle.scene_path_edge[node_str][target_str][0])
                route_cost[node_str] = route_cost[next_str] + graph[node_str].get(next_str, 10**6)
                if route_cost[node_str] != distance.get(node_str):
                    dist_bad.append((node_str, target_str, route_cost[node_str], distance.get(node_str)))
check("沿寻路表一步步走都能到达终点，不绕圈", not loop_bad, loop_bad[:20])
check("沿寻路表走的总耗时 = 场景图上的最短距离", not dist_bad, dist_bad[:20])

# ==== 7. 移动接口 character_move ====
section("移动接口 character_move")
# 设施开放表默认是空 dict，judge_scene_accessible 会直接下标取；测试里先全部置为已开放
for facility_cid in game_config.config_facility_open:
    cache.rhodes_island.facility_open.setdefault(facility_cid, True)
pl.item = attr_calculation.get_item_zero(pl.item)
npc = make_npc(301, "移动员", SCENE_DORM)
dorm_str = scene_str(SCENE_DORM)
office_str = scene_str(SCENE_OFFICE)
check("原地不动 → end", character_move.character_move(301, list(SCENE_DORM)) == ("end", [], [], 0))
check("目标是泰拉大地图场景 → null（不抛异常）", character_move.character_move(301, path_list(terra_scene_list[0])) == ("null", [], [], 0))
check("目标场景不存在 → null", character_move.character_move(301, ["不存在的区块", "不存在的房间"]) == ("null", [], [], 0))
expect_next, expect_time = map_handle.scene_path_edge[dorm_str][office_str]
check("正常寻路：返回 open、下一步与该步耗时（取自寻路表）", character_move.character_move(301, list(SCENE_OFFICE)) == ("open", [], expect_next, expect_time),
      character_move.character_move(301, list(SCENE_OFFICE)))
move_to(301, SCENE_OUT_CORRIDOR)
dorm_102 = cache.scene_data[scene_str(SCENE_DORM_102)]
dorm_101 = cache.scene_data[dorm_str]
dorm_102.close_flag = 1
check("干员到门前、目标锁门 → door_lock，不给路径", character_move.character_move(301, list(SCENE_DORM_102)) == ("door_lock", [], [], 0))
dorm_102.close_flag = 0
check("干员进别人的宿舍 → private，但仍给出这一步（由跟随逻辑决定等不等）", character_move.character_move(301, list(SCENE_DORM_102)) == ("private", [], SCENE_DORM_102, 1))
dorm_101.close_flag = 1
check("自己的宿舍锁着也能进", character_move.character_move(301, list(SCENE_DORM)) == ("open", [], SCENE_DORM, 1))
dorm_101.close_flag = 0
move_to(0, SCENE_OUT_CORRIDOR)
dorm_102.close_flag = 1
drawn_text.clear()
result = character_move.character_move(0, list(SCENE_DORM_102))
check("玩家无钥匙、目标锁门 → door_lock 并提示门锁着", result == ("door_lock", [], [], 0) and dorm_102.close_flag == 1 and any("锁着" in text for text in drawn_text), (result, drawn_text[-3:]))
check("宿舍层号从房间名解析：宿舍102房 → 1 层", dormitory_common.get_layer_by_dormitory_path(scene_str(SCENE_DORM_102)) == 1)
pl.item[301] = 1
drawn_text.clear()
result = character_move.character_move(0, list(SCENE_DORM_102))
check("玩家持有本层复制钥匙 → 开门进入、钥匙不消耗", result == ("open", [], SCENE_DORM_102, 1) and dorm_102.close_flag == 0 and pl.item[301] == 1
      and any("复制钥匙" in text for text in drawn_text), (result, drawn_text[-2:]))
pl.item[301] = 0
pl.item[152] = 1
dorm_102.close_flag = 1
drawn_text.clear()
result = character_move.character_move(0, list(SCENE_DORM_102))
check("玩家持有一次性万能钥匙 → 开门进入、钥匙消耗 1", result == ("open", [], SCENE_DORM_102, 1) and dorm_102.close_flag == 0 and pl.item[152] == 0
      and any("一次性万能钥匙" in text for text in drawn_text), (result, drawn_text[-2:]))
move_to(0, SCENE_DORM)

section("可进入判定 judge_scene_accessible")
dr_room_str = constant.place_data["Dr_room"][0]
dr_room = cache.scene_data[dr_room_str]
check("博士房间：干员 private、玩家 open", map_handle.judge_scene_accessible(dr_room_str, 301, False) == "private" and map_handle.judge_scene_accessible(dr_room_str, 0, False) == "open")
pl.assistant_character_id = 301
check("博士房间：助理可进", map_handle.judge_scene_accessible(dr_room_str, 301, False) == "open")
dr_room.close_flag = 1
check("博士房间锁门：玩家与助理都能进", map_handle.judge_scene_accessible(dr_room_str, 0, False) == "open" and map_handle.judge_scene_accessible(dr_room_str, 301, False) == "open")
pl.assistant_character_id = 0
check("博士房间锁门：其他干员 door_lock", map_handle.judge_scene_accessible(dr_room_str, 301, False) == "door_lock")
dr_room.close_flag = 0
male_toilet_str = constant.place_data["Toilet_Male"][0]
check("男厕所对干员是 private", map_handle.judge_scene_accessible(male_toilet_str, 301, False) == "private")
npc.sp_flag.go_to_join_group_sex = True
dorm_102.close_flag = 1
check("受邀群交的干员：锁门与私密场所都放行", map_handle.judge_scene_accessible(scene_str(SCENE_DORM_102), 301, False) == "open")
npc.sp_flag.go_to_join_group_sex = False
dorm_102.close_flag = 0
surgery_list = [s for s, d in cache.scene_data.items() if d.scene_name == _("手术室")]
check("找到设施开放表里的「手术室」场景", len(surgery_list) == 1 and _("手术室") in game_config.config_facility_open_name_set, surgery_list)
surgery_str = surgery_list[0]
surgery_cid = game_config.config_facility_open_name_to_cid[_("手术室")]
cache.rhodes_island.facility_open[surgery_cid] = False
drawn_text.clear()
check("未开放设施：干员 wait_open（不提示）、玩家 wait_open 并提示解锁条件",
      map_handle.judge_scene_accessible(surgery_str, 301) == "wait_open" and not drawn_text
      and map_handle.judge_scene_accessible(surgery_str, 0) == "wait_open" and any(_("手术室") in text for text in drawn_text), drawn_text[-2:])
cache.rhodes_island.facility_open[surgery_cid] = True
check("设施开放后 → open", map_handle.judge_scene_accessible(surgery_str, 301, False) == "open")
small_room_str = sorted(s for s, d in cache.scene_data.items() if d.room_area == 0 and d.scene_name not in game_config.config_facility_open_name_set
                        and not {"Dormitory", "Dr_room", "Toilet_Male"} & set(d.scene_tag))[0]
small_room = cache.scene_data[small_room_str]
small_room.character_list.update(range(9001, 9010))
check("面积 0 的房间 9 人时未满", not map_handle.judge_scene_is_full(small_room_str) and map_handle.judge_scene_accessible(small_room_str, 301, False) == "open")
small_room.character_list.add(9010)
check("面积 0 的房间 10 人时满员：干员 full、玩家不受限", map_handle.judge_scene_is_full(small_room_str)
      and map_handle.judge_scene_accessible(small_room_str, 301, False) == "full" and map_handle.judge_scene_accessible(small_room_str, 0, False) == "open")
small_room.character_list.difference_update(range(9001, 9011))
big_room_list = sorted(s for s, d in cache.scene_data.items() if d.room_area == 3)
check("面积 3 的房间不设人数上限", len(big_room_list) > 0 and all(not map_handle.judge_scene_is_full(s) for s in big_room_list))

# ==== 8. 场景移动记账 character_move_scene ====
section("场景移动记账 character_move_scene")
walker = make_npc(302, "记账员", SCENE_OUT_CORRIDOR)
corridor = cache.scene_data[scene_str(SCENE_OUT_CORRIDOR)]
room_103 = cache.scene_data[scene_str(SCENE_DORM_103)]
corridor.close_flag = 1
walker.behavior.move_final_target = list(SCENE_DORM_103)
map_handle.character_move_scene(list(SCENE_OUT_CORRIDOR), list(SCENE_DORM_103), 302)
check("移动后 position 指向新场景", walker.position == SCENE_DORM_103)
check("旧场景名单移除、新场景名单加入", 302 not in corridor.character_list and 302 in room_103.character_list)
check("离开锁着的房间时把锁解开", corridor.close_flag == 0)
check("记录本次移动的起点与终点", walker.behavior.move_src == SCENE_OUT_CORRIDOR and walker.behavior.move_target == SCENE_DORM_103)
check("移动历史记下旧场景", walker.action_info.past_move_position_list == [SCENE_OUT_CORRIDOR])
check("到达最终目的地时清空 move_final_target", walker.behavior.move_final_target == [])
walker.behavior.move_final_target = list(SCENE_OFFICE)
map_handle.character_move_scene(list(SCENE_DORM_103), list(SCENE_OUT_CORRIDOR), 302)
check("途经中间场景时保留 move_final_target", walker.behavior.move_final_target == SCENE_OFFICE)
check("移动历史按顺序追加", walker.action_info.past_move_position_list == [SCENE_OUT_CORRIDOR, SCENE_DORM_103])
map_handle.character_move_scene(list(SCENE_DORM_103), list(SCENE_DORM_102), 302)
check("旧场景与历史末尾相同时不重复追加", walker.action_info.past_move_position_list == [SCENE_OUT_CORRIDOR, SCENE_DORM_103] and walker.position == SCENE_DORM_102)
# 上一步故意传了与 position 不符的旧场景，名单里会残留在外走廊，先修正
corridor.character_list.discard(302)
for step_index in range(12):
    old_path, new_path = (SCENE_DORM_102, SCENE_OUT_CORRIDOR) if step_index % 2 == 0 else (SCENE_OUT_CORRIDOR, SCENE_DORM_102)
    map_handle.character_move_scene(list(old_path), list(new_path), 302)
check("移动历史最多保留 10 条", len(walker.action_info.past_move_position_list) == 10 and walker.action_info.past_move_position_list[-1] == SCENE_OUT_CORRIDOR,
      walker.action_info.past_move_position_list)
room_103.character_list.add(302)
map_handle.character_move_scene(list(SCENE_DORM_102), list(SCENE_DORM_103), 302)
check("已在新场景名单里但 position 没跟上时，补上 position", walker.position == SCENE_DORM_103 and 302 not in dorm_102.character_list and 302 in room_103.character_list)

section("沿寻路表逐步走到目的地")
traveler = make_npc(303, "旅行者", SCENE_DORM)
traveler.behavior.move_final_target = list(SCENE_OFFICE)
total_time = 0
step_count = 0
step_bad = []
while traveler.position != SCENE_OFFICE and step_count < 60:
    status, _unused, next_path, need_time = character_move.character_move(303, list(SCENE_OFFICE))
    if status not in ("open", "private") or scene_str(next_path) not in graph[scene_str(traveler.position)] or need_time <= 0:
        step_bad.append((traveler.position, status, next_path, need_time))
        break
    map_handle.character_move_scene(traveler.position, next_path, 303)
    total_time += need_time
    step_count += 1
    if scene_list_mismatch():
        step_bad.append(("名单不一致", traveler.position))
        break
check("从宿舍一步步走到博士办公室，每步都走向相邻场景、名单始终一致", traveler.position == SCENE_OFFICE and not step_bad, (traveler.position, step_bad))
check("全程耗时 = 最短距离，到达后最终目的地清空", total_time == shortest_from(graph, dorm_str)[office_str] and traveler.behavior.move_final_target == [],
      (total_time, shortest_from(graph, dorm_str)[office_str]))
check("全部角色都恰好在自己 position 所指场景的名单里", not scene_list_mismatch(), scene_list_mismatch()[:10])

section("跟随时的私密场所等待 judge_character_move_to_private")
follower = make_npc(304, "跟随者", SCENE_OUT_CORRIDOR)
check("没有下一步 → 不移动、等待", character_move.judge_character_move_to_private(304, []) == (False, True))
check("目标开放 → 直接移动", character_move.judge_character_move_to_private(304, list(SCENE_OUT_CORRIDOR)) == (True, False))
follower.chara_setting[0] = 0
follower.action_info.follow_wait_time = 0
drawn_text.clear()
check("设置0（超时取消跟随）未超时 → 门外等待并提示", character_move.judge_character_move_to_private(304, list(SCENE_DORM_102)) == (False, True)
      and any("外面等待" in text for text in drawn_text))
follower.action_info.follow_wait_time = 30
follower.sp_flag.is_follow = 1
drawn_text.clear()
check("设置0 等满 30 分钟 → 取消跟随", character_move.judge_character_move_to_private(304, list(SCENE_DORM_102)) == (False, False)
      and follower.sp_flag.is_follow == 0 and any("不再继续跟随" in text for text in drawn_text))
follower.chara_setting[0] = 1
check("设置1（一直等）→ 超时也继续等", character_move.judge_character_move_to_private(304, list(SCENE_DORM_102)) == (False, True))
follower.chara_setting[0] = 2
follower.action_info.follow_wait_time = 10
check("设置2（超时闯入）未满 30 分钟 → 等待", character_move.judge_character_move_to_private(304, list(SCENE_DORM_102)) == (False, True))
follower.action_info.follow_wait_time = 30
drawn_text.clear()
check("设置2 满 30 分钟 → 闯入", character_move.judge_character_move_to_private(304, list(SCENE_DORM_102)) == (True, False) and any("等不下去" in text for text in drawn_text))
follower.chara_setting[0] = 3
follower.action_info.follow_wait_time = 0
check("设置3（无视私密）→ 直接进", character_move.judge_character_move_to_private(304, list(SCENE_DORM_102)) == (True, False))

# ==== 9. 通用移动模块与移动状态机 ====
section("通用移动模块与移动状态机")
mover = make_npc(305, "出行者", SCENE_DORM)
check("通用移动模块：寻路成功返回 True", state_machine_default.general_movement_module(305, list(SCENE_OFFICE), False) is True)
check("通用移动模块：赋予移动行为、本步目标与时长、最终目的地",
      mover.behavior.behavior_id == constant.Behavior.MOVE and mover.state == constant.CharacterStatus.STATUS_MOVE and mover.behavior.move_target == expect_next
      and mover.behavior.duration == expect_time and mover.behavior.move_final_target == SCENE_OFFICE,
      (mover.behavior.behavior_id, mover.behavior.move_target, mover.behavior.duration, mover.behavior.move_final_target))
check("通用移动模块：寻路失败（泰拉）返回 False 并改为等待 1 分钟", state_machine_default.general_movement_module(305, path_list(terra_scene_list[0]), False) is False
      and mover.behavior.behavior_id == constant.Behavior.WAIT and mover.behavior.duration == 1 and mover.state == constant.CharacterStatus.STATUS_WAIT)
state_machine_data = constant.handle_state_machine_data
move_to(305, SCENE_CENTER_DOOR)
mover.dormitory = scene_str(SCENE_DORM_103)
state_machine_data[constant.StateMachine.MOVE_TO_DORMITORY](305)
check("回宿舍状态机：最终目的地是自己的宿舍", mover.behavior.move_final_target == SCENE_DORM_103, mover.behavior.move_final_target)
_real_randint = random.randint
birthplace_room = constant.place_data.get("Birthplace_13", [])
mover.relationship.birthplace = 13
random.randint = lambda a, b: 1
state_machine_data[constant.StateMachine.MOVE_TO_REST_ROOM](305)
check("休息室状态机：抽中专属休息室时去出身地专属休息室", len(birthplace_room) == 1 and mover.behavior.move_final_target == path_list(birthplace_room[0]),
      (birthplace_room, mover.behavior.move_final_target))
nation_room = constant.place_data.get("Nation_52", [])
mover.relationship.birthplace = 0
mover.relationship.nation = 52
state_machine_data[constant.StateMachine.MOVE_TO_REST_ROOM](305)
check("休息室状态机：抽中专属休息室时去势力专属休息室", len(nation_room) == 1 and mover.behavior.move_final_target == path_list(nation_room[0]),
      (nation_room, mover.behavior.move_final_target))
random.randint = lambda a, b: 2
state_machine_data[constant.StateMachine.MOVE_TO_REST_ROOM](305)
center_rest_room = [s for s in constant.place_data["Rest_Room"] if path_list(s)[0] == "中枢"]
check("休息室状态机：没抽中专属时优先去所在大区块内的休息室", len(center_rest_room) >= 1 and mover.behavior.move_final_target == path_list(center_rest_room[0]),
      (center_rest_room, mover.behavior.move_final_target))
random.randint = _real_randint

# ==== 10. 常用场景查询 ====
section("常用场景查询")
make_npc(306, "同屋者", SCENE_DORM)
check("同场景角色列表含自己与同屋者，去掉自己后不含自己", {0, 306} <= set(map_handle.get_chara_now_scene_all_chara_id_list(0))
      and 0 not in map_handle.get_chara_now_scene_all_chara_id_list(0, True) and 306 in map_handle.get_chara_now_scene_all_chara_id_list(0, True))
check("场景角色名列表（去掉玩家）", "同屋者" in map_handle.get_scene_character_name_list(dorm_str, True) and "博士" not in map_handle.get_scene_character_name_list(dorm_str, True))
check("场景角色 id 列表", set(map_handle.get_scene_character_id_list(dorm_str)) == set(dorm_101.character_list))
check("按 地图+相对位置 取场景数据：宿舍\\1区 + 101", map_handle.get_scene_data_for_map(scene_str(["宿舍", "1区"]), "101") is dorm_101)
check("按 地图+相对位置 取场景数据：子地图节点取其入口", map_handle.get_scene_data_for_map("", "宿舍") is cache.scene_data[scene_str(["宿舍", "0"])]
      and map_handle.get_scene_data_for_map("宿舍", "1区") is cache.scene_data[scene_str(["宿舍", "1区", "0"])])
check("按相对位置取场景路径：子地图节点逐级取入口 0", map_handle.get_scene_path_for_map_scene_id(["宿舍"], "1区") == ["宿舍", "1区", "0"]
      and map_handle.get_scene_path_for_map_scene_id([], "0") == ["0", "0"])
check("场景所在的直接地图：普通房间只有一张，入口场景逐级向上", map_handle.get_relation_map_list_for_scene_path(list(SCENE_DORM)) == [["宿舍", "1区"]]
      and map_handle.get_relation_map_list_for_scene_path(["宿舍", "1区", "0"]) == [["宿舍", "1区"], ["宿舍"]])
check("场景归属关系：同一地图 common、不同地图 nobelonged", map_handle.judge_scene_affiliation(list(SCENE_DORM), list(SCENE_DORM_102)) == "common"
      and map_handle.judge_scene_affiliation(list(SCENE_DORM), list(SCENE_OFFICE)) == "nobelonged")
check("两个场景的共同地图", map_handle.get_common_map_for_scene_path(list(SCENE_DORM), ["宿舍", "2区", "201"]) == ["宿舍"]
      and map_handle.get_common_map_for_scene_path(list(SCENE_DORM), list(SCENE_OFFICE)) == [])
check("地图下全部场景节点", map_handle.get_scene_list_for_map(scene_str(["宿舍", "1区"])) == list(cache.map_data[scene_str(["宿舍", "1区"])].path_edge))
bad = []
for now_scene_str in constant.place_data.get("Dormitory", []):
    now_path = path_list(now_scene_str)
    zone_match = re.match(r"^(\d)区$", now_path[1]) if now_path[0] == "宿舍" and len(now_path) == 3 else None
    if zone_match and dormitory_common.get_layer_by_dormitory_path(now_scene_str) != int(zone_match.group(1)):
        bad.append((now_scene_str, cache.scene_data[now_scene_str].scene_name, dormitory_common.get_layer_by_dormitory_path(now_scene_str)))
check("宿舍区每间宿舍解析出的层号 = 所在区号（复制钥匙按层发放）", not bad and dorm_str in constant.place_data["Dormitory"], bad[:20])

# ==== 11. 游戏时钟：季月与推进 ====
section("游戏时钟：季月归并与 get_sub_date")
check("月份归并为季月：1,2→3、4,5→6、7,8→9、10,11→12，季月不变", [game_time.get_season_month(m) for m in range(1, 13)] == [3, 3, 3, 6, 6, 6, 9, 9, 9, 12, 12, 12])
base_time = T(2026, 9, 7, 9, 0)
check("同一小时内加分钟", game_time.get_sub_date(minute=30, old_date=base_time) == T(2026, 9, 7, 9, 30))
check("跨小时、跨午夜", game_time.get_sub_date(minute=90, old_date=base_time) == T(2026, 9, 7, 10, 30)
      and game_time.get_sub_date(hour=15, minute=30, old_date=base_time) == T(2026, 9, 8, 0, 30))
check("季月末跨午夜 → 下一个季月 1 日", game_time.get_sub_date(minute=60, old_date=T(2026, 9, 30, 23, 30)) == T(2026, 12, 1, 0, 30))
check("落进被跳过的月份时月份归并、日保留（9/15+30天=10/15 → 12/15，归 1 是 sub_time_now 的事）",
      game_time.get_sub_date(day=30, old_date=T(2026, 9, 15, 10, 0)) == T(2026, 12, 15, 10, 0))
check("目标季月天数不足时夹到月末（3/31+61天=5/31 → 6/30）", game_time.get_sub_date(day=61, old_date=T(2027, 3, 31, 8, 0)) == T(2027, 6, 30, 8, 0))
check("跨年：12/31 → 次年 3/1", game_time.get_sub_date(hour=2, old_date=T(2026, 12, 31, 23, 0)) == T(2027, 3, 1, 1, 0))
check("按月 / 按年加", game_time.get_sub_date(month=3, old_date=base_time) == T(2026, 12, 7, 9, 0)
      and game_time.get_sub_date(month=1, old_date=base_time) == T(2026, 12, 7, 9, 0) and game_time.get_sub_date(year=1, old_date=base_time) == T(2027, 9, 7, 9, 0))
set_time(base_time)
check("缺省以当前游戏时间为起点，且不改动游戏时间", game_time.get_sub_date(minute=10) == T(2026, 9, 7, 9, 10) and cache.game_time == base_time)

section("游戏时钟：sub_time_now 推进")
set_time(base_time)
game_time.sub_time_now(45)
check("推进 45 分钟", cache.game_time == T(2026, 9, 7, 9, 45))
set_time(T(2026, 9, 7, 23, 50))
game_time.sub_time_now(20)
check("跨午夜到次日", cache.game_time == T(2026, 9, 8, 0, 10))
set_time(T(2026, 9, 30, 23, 50))
game_time.sub_time_now(20)
check("季月最后一天跨午夜 → 下一个季月 1 日，时分保留", cache.game_time == T(2026, 12, 1, 0, 10), cache.game_time)
set_time(T(2026, 12, 31, 23, 30))
game_time.sub_time_now(60)
check("跨年：12/31 → 次年 3/1", cache.game_time == T(2027, 3, 1, 0, 30), cache.game_time)
set_time(T(2027, 6, 30, 22, 0))
game_time.sub_time_now(480)
check("睡 8 小时跨季：6/30 22:00 → 9/1 06:00", cache.game_time == T(2027, 9, 1, 6, 0), cache.game_time)
daily_walk = walk_clock(base_time, 400, day=1)
expect_walk = []
now_day = base_time
while len(expect_walk) < len(daily_walk):
    if now_day.month in (3, 6, 9, 12):
        expect_walk.append(now_day)
    now_day += datetime.timedelta(days=1)
first_diff = next((i for i, (a, b) in enumerate(zip(daily_walk, expect_walk)) if a != b), None)
check("逐日推进 400 天：依次走过季月里的每一天，不漏不重（跨年、闰年 2 月都被跳过）", first_diff is None,
      None if first_diff is None else (first_diff, daily_walk[first_diff], expect_walk[first_diff]))
set_time(T(2026, 9, 30, 23, 50))
cache.pre_game_time = cache.game_time
game_time.sub_time_now(5)
same_day = cache.game_time.day == cache.pre_game_time.day
game_time.sub_time_now(10)
check("新一天判据（game_time.day != pre_game_time.day）：同日不触发、跨季月午夜触发", same_day and cache.game_time.day != cache.pre_game_time.day,
      (cache.pre_game_time, cache.game_time))
set_time(T(2026, 9, 7, 10, 0))
game_time.sub_time_now(20)
game_time.sub_time_now(-20)
check("时停回退：前进再回退同样时长回到原时间", cache.game_time == T(2026, 9, 7, 10, 0), cache.game_time)

# 时停模式下主循环结算完玩家行动即还原时间。让真实的 update.game_update_flow → init_character_behavior 跑一遍时停分支（铁律「不进真实主循环」的第二个例外，见 tools/tests/README.md）：
# 逐角色结算 character_behavior.character_behavior 换成「玩家立即完成」的桩并设调用上限（防死循环卡住），成就结算（可能写文件）与输入框聚焦换成空函数；
# 时停分支在玩家阶段之后即 break，不会进入 NPC 阶段、委托刷新与跨日结算
from Script.Core import py_cmd
from Script.Design import update
from Script.Design import character_behavior as character_behavior_module
from Script.UI.Panel import achievement_panel


def run_time_stop_flow(start_time: datetime.datetime, duration: int) -> tuple:
    """
    在时停模式下按真实流程推进一次玩家行动
    Keyword arguments:
    start_time -- 行动开始时的游戏时间
    duration -- 行动时长（分钟）
    Return arguments:
    tuple -- (流程结束后的游戏时间, 时停成就累计时长的增量, 结算玩家行动时的游戏时间列表)
    """
    behavior_time_list = []

    def fake_character_behavior(character_id: int, now_time: datetime.datetime, pl_start_time: datetime.datetime):
        """
        逐角色结算的桩：记下结算时的游戏时间，并让该角色立即完成行动
        Keyword arguments:
        character_id -- 角色id
        now_time -- 结算时的游戏时间
        pl_start_time -- 玩家行动开始时间
        Return arguments:
        无
        """
        behavior_time_list.append(now_time)
        if len(behavior_time_list) > 20:
            raise RuntimeError("时停流程中逐角色结算被调用了 20 次以上，疑似死循环")
        cache.over_behavior_character.add(character_id)

    saved = (character_behavior_module.character_behavior, achievement_panel.achievement_flow, py_cmd.focus_cmd, cache.time_stop_mode, cache.game_update_flow_running)
    character_behavior_module.character_behavior = fake_character_behavior
    achievement_panel.achievement_flow = lambda *args, **kwargs: None
    py_cmd.focus_cmd = lambda: None
    try:
        set_time(start_time)
        cache.time_stop_mode = True
        cache.game_update_flow_running = 0
        pl.behavior.duration = duration
        before_duration = cache.achievement.time_stop_duration
        update.game_update_flow(duration)
        return cache.game_time, cache.achievement.time_stop_duration - before_duration, behavior_time_list
    finally:
        character_behavior_module.character_behavior, achievement_panel.achievement_flow, py_cmd.focus_cmd, cache.time_stop_mode, cache.game_update_flow_running = saved


end_time, add_duration, behavior_time_list = run_time_stop_flow(T(2026, 9, 7, 10, 0), 20)
check("时停中的玩家行动：结算时时钟已前进，结束后还原到行动前、时停时长累计 20 分钟",
      behavior_time_list == [T(2026, 9, 7, 10, 20)] and end_time == T(2026, 9, 7, 10, 0) and add_duration == 20, (behavior_time_list, end_time, add_duration))
# 9/30 23:50 前进 20 分钟被季月归并到 12/1 00:10；曾用 sub_time_now(minute=-20) 倒退，落到 11/30 23:50 又被归并成 12/30 23:50，时钟反而前进约一个月
end_time, add_duration, behavior_time_list = run_time_stop_flow(T(2026, 9, 30, 23, 50), 20)
check("时停中的玩家行动跨季月边界：结算时已到 12/1 00:10，结束后仍还原到 9/30 23:50",
      behavior_time_list == [T(2026, 12, 1, 0, 10)] and end_time == T(2026, 9, 30, 23, 50) and add_duration == 20, (behavior_time_list, end_time, add_duration))
set_time(DEFAULT_TIME)

# ==== 12. 游戏时钟：天数计数与预计日期 ====
section("游戏时钟：天数计数与预计日期")
bad = [k for k, now_time in enumerate(daily_walk) if game_time.count_play_day(daily_walk[0], now_time) != k]
check("count_play_day：时钟每走一天计 1 天（被跳过的月份不算）", not bad, bad[:10])
check("count_play_day：结束早于开始为 0", game_time.count_play_day(T(2026, 9, 8), T(2026, 9, 7)) == 0)
check("count_day_for_datetime 按日历天数（含被跳过的月份）", game_time.count_day_for_datetime(T(2026, 9, 30), T(2026, 12, 1)) == 62)
bad = [k for k, now_time in enumerate(daily_walk) if game_time.count_play_second(daily_walk[0], now_time) != k * 86400]
check("count_play_second：时钟每走一天计 86400 秒（被跳过的月份不算）", not bad, bad[:10])
SEASON_EDGE_LIST = [
    (T(2026, 9, 30, 23, 50), T(2026, 12, 1, 0, 10)),
    (T(2026, 12, 31, 23, 50), T(2027, 3, 1, 0, 10)),
    (T(2027, 3, 31, 23, 50), T(2027, 6, 1, 0, 10)),
    (T(2027, 6, 30, 23, 50), T(2027, 9, 1, 0, 10)),
    (T(2027, 12, 31, 23, 50), T(2028, 3, 1, 0, 10)),
]
""" 时钟跨四个季末午夜的 20 分钟（季末 23:50 → 下一个季月 1 日 00:10），最后一组跨的是含闰年二月的那次换季 """
check("fixture：这些时刻对就是时钟从季末 23:50 走 20 分钟的结果", all(game_time.get_sub_date(minute=20, old_date=edge[0]) == edge[1] for edge in SEASON_EDGE_LIST))
check("count_play_second：跨季末午夜的 20 分钟计 1200 秒，不含被跳过的约两个月", [game_time.count_play_second(*edge) for edge in SEASON_EDGE_LIST] == [1200] * 5,
      [game_time.count_play_second(*edge) for edge in SEASON_EDGE_LIST])
check("count_play_second：有符号，结束早于开始时为负", [game_time.count_play_second(edge[1], edge[0]) for edge in SEASON_EDGE_LIST] == [-1200] * 5
      and game_time.count_play_second(T(2026, 9, 8, 9, 0), T(2026, 9, 7, 9, 0)) == -86400)
check("count_play_second：季月内与公历时长相同（含秒）", game_time.count_play_second(T(2026, 9, 7, 9, 0, 15), T(2026, 9, 9, 10, 30, 45)) == 2 * 86400 + 5430)
check("count_play_second：落在被跳过月份里的时刻按其后第一个季月的 1 日 0 点算", game_time.count_play_second(T(2026, 10, 15, 8, 0), T(2026, 12, 1)) == 0
      and game_time.count_play_second(T(2026, 9, 30), T(2026, 11, 3, 12, 0)) == 86400 and game_time.count_play_second(T(2026, 1, 20), T(2026, 3, 2)) == 86400)
random.seed(20260930)
bad = []
for _sample in range(3000):
    time_a = T(2025, 1, 1) + datetime.timedelta(minutes=random.randint(0, 6 * 365 * 1440))
    time_b = T(2025, 1, 1) + datetime.timedelta(minutes=random.randint(0, 6 * 365 * 1440))
    if game_time.count_play_day(time_a, time_b) != max(0, int(game_time.count_play_second(time_a, time_b) // 86400)):
        bad.append((time_a, time_b, game_time.count_play_day(time_a, time_b), game_time.count_play_second(time_a, time_b)))
check("count_play_second 与 count_play_day 口径一致：任意两个时刻（含落在被跳过月份里的）整天数相同", not bad, bad[:5])
bad = []
prev_date = None
for day in range(0, 200):
    predict = game_time.get_predict_date(day, base_time)
    first_reach = next(now_time for now_time in daily_walk if (now_time - base_time).days >= day)
    if predict.date() != first_reach.date() or (prev_date is not None and predict < prev_date):
        bad.append((day, predict, first_reach))
    prev_date = predict
check("get_predict_date：= 时钟第一次走到「日历上已过 N 天」的那一天，且随 N 单调不减", not bad, bad[:10])
random.seed(20260907)
birthday_list = [game_time.get_rand_day_for_year(2026) for _sample in range(300)]
check("随机生日只落在该年的季月里（被跳过的月份永远过不到）", all(d.year == 2026 and d.month in (3, 6, 9, 12) for d in birthday_list),
      [d for d in birthday_list if d.year != 2026 or d.month not in (3, 6, 9, 12)][:10])

# ==== 13. 游戏时钟：显示与时段 ====
section("游戏时钟：月份显示、星期、工作日与时段")
season_name = {3: _("春"), 6: _("夏"), 9: _("秋"), 12: _("冬")}
check("月份显示为季节名（非季月按归并规则兜底）", [game_time.get_month_text(T(2027, m, 1)) for m in range(1, 13)] == [season_name[game_time.get_season_month(m)] for m in range(1, 13)])
check("完整日期文本含年份与季节", "2026" in game_time.get_date_text(base_time) and _("秋") in game_time.get_date_text(base_time)
      and _("秋") in game_time.get_date_until_day(base_time))
week_text = []
for offset in range(7):
    set_time(base_time + datetime.timedelta(days=offset))
    week_text.append(game_time.get_week_day_text())
check("星期文本：2026-09-07 起依次为周一~周日", len(game_config.config_week_day) == 7 and week_text == [game_config.config_week_day[i].name for i in range(7)], week_text)
work_list = []
premise_bad = []
for offset in range(7):
    set_time(base_time + datetime.timedelta(days=offset))
    work_list.append(int(game_time.judge_work_today(0)))
    workday = constant.handle_premise_data[constant_promise.Premise.TIME_WORKDAYD](0)
    weekend = constant.handle_premise_data[constant_promise.Premise.TIME_WEEKEND](0)
    if bool(workday) == bool(weekend):
        premise_bad.append(offset)
check("工作日 / 周末两个前提互斥且互补", not premise_bad, premise_bad)
check("工作日判定：周一~周五为工作日、周六周日休息（见 judge_work_today 与两个前提的说明、体检日「周末即周六和周日」）", work_list == [1, 1, 1, 1, 1, 0, 0],
      f"周一~周日实际为 {work_list}")
hour_case = [((8, 59), 0), ((9, 0), 1), ((11, 59), 1), ((12, 0), 0), ((14, 0), 2), ((17, 59), 2), ((18, 0), 0), ((19, 0), 3), ((21, 59), 3), ((22, 0), 0)]
bad = []
for (hour, minute), expect in hour_case:
    set_time(T(2026, 9, 7, hour, minute))
    if game_time.judge_entertainment_time(0) != expect:
        bad.append((hour, minute, game_time.judge_entertainment_time(0), expect))
check("娱乐时段：9~12 上午、14~18 下午、19~22 晚上，其余 0", not bad, bad)
check("时间比较：相等 2、晚于 True、早于 False", game_time.judge_date_big_or_small(base_time, base_time) == 2
      and game_time.judge_date_big_or_small(base_time + datetime.timedelta(minutes=1), base_time) is True
      and game_time.judge_date_big_or_small(base_time, base_time + datetime.timedelta(minutes=1)) is False)
sun_list = [game_time.get_sun_time(T(2026, 9, 7, hour, 30)) for hour in range(24)]
sun_count = collections.Counter(sun_list)
check("太阳时段：每个整点都落在配置里，12 个时段各占 2 小时", all(s in game_config.config_sun_time for s in sun_list) and len(sun_count) == 12 and set(sun_count.values()) == {2}, sun_list)
check("正午时段覆盖 12 点", game_config.config_sun_time[game_time.get_sun_time(T(2026, 9, 7, 12, 0))].name == _("正午"))
bad = []
moon_type_set = set()
for offset in range(400):
    now_time = base_time + datetime.timedelta(days=offset)
    try:
        phase = game_time.get_moon_phase(now_time)
        if phase not in game_config.config_moon:
            bad.append((now_time.date(), phase))
        else:
            moon_type_set.add(game_config.config_moon[phase].type)
    except KeyError as error:  # 亮度没落进任何月相区间时 get_moon_phase 会 KeyError
        bad.append((now_time.date(), repr(error)))
check("月相：连续 400 天都能取到配置 id，盈亏两类都出现，缓存不膨胀", not bad and moon_type_set == {0, 1} and len(cache.moon_phase) <= 4, (bad[:10], moon_type_set))
set_time(DEFAULT_TIME)

finish()
