import heapq
from typing import Dict, List, Tuple

class SortedPathData:
    """ 最短路径数据 """

    def __init__(self):
        self.node_id: str = ""
        """ 节点id """
        self.distance: int = 0
        """ 总路程 """
        self.path: List[str] = []
        """ 通往本节点的路径列表 """
        self.path_times: List[int] = []
        """ 通往本节点的路径中各节点路程列表 """


def dijkstra(graph: Dict[str, Dict[str, int]], start: str) -> Dict[str, SortedPathData]:
    """
    使用Dijkstra算法指定节点到其他节点的最短路径
    Keyword arguments:
    graph -- 加权图 {节点id:{可以通往的节点id:路程}}
    start -- 路径起点
    Return arguments:
    Dict[str, SortedPathData] -- 从起点到各个节点的最短路径数据
    """
    distances = {vertex: float('infinity') for vertex in graph}
    previous_nodes = {vertex: None for vertex in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)
        if current_distance > distances[current_vertex]:
            continue
        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_vertex
                heapq.heappush(priority_queue, (distance, neighbor))
    paths_data = {}
    for vertex in graph:
        path_data = SortedPathData()
        path_data.node_id = vertex
        path_data.distance = distances[vertex]
        path_data.path, path_data.path_times = get_path_and_times(previous_nodes, graph, vertex)
        paths_data[vertex] = path_data
    return paths_data


def get_path_and_times(previous_nodes: Dict[str, str], graph: Dict[str, Dict[str, int]], vertex: str) -> Tuple[List[str], List[int]]:
    """
    根据前驱节点字典构建到指定节点的路径和时间列表。
    Keyword arguments:
    previous_nodes -- 存储每个节点的前一个节点的字典。
    graph -- 表示加权图的字典。
    vertex -- 目标节点。
    Return arguments:
    Tuple[List[str], List[str]]从起始节点到目标节点的路径和时间列表。
    """
    path = []
    path_times = [0]
    while vertex is not None:
        path.append(vertex)
        if previous_nodes[vertex] is not None:
            path_times.append(graph[previous_nodes[vertex]][vertex])
        vertex = previous_nodes[vertex]
    return path[::-1], path_times

