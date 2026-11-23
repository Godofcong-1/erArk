# -*- coding: UTF-8 -*-
"""地图预处理文件的语言标记：场景名与地图名是按构建时的语言翻译好再存盘的，预处理文件记着写出时的语言；语言相同时直接读入，语言不同或是没有标记的旧文件时重建"""
import pickle
import shutil
import tempfile
from unittest import mock

from _bootstrap import *  # noqa: F401,F403

PATH_NAME_LIST = ("scene_path_edge_path", "all_scene_data_path", "all_place_data_path", "all_map_data_path")
PICKLE_NAME_LIST = ("all_scene_data_path", "all_place_data_path", "all_map_data_path")
NOW_LANGUAGE = get_text.now_language
OTHER_LANGUAGE = "en_US" if NOW_LANGUAGE != "en_US" else "zh_CN"

# 把四个预处理文件的路径改到一个空的临时目录里，本文件的重建与改写都不碰仓库 data/ 下的那几份
cache_dir = tempfile.mkdtemp(prefix="erArk_test_mapcache_")
saved_path = {name: getattr(map_config, name) for name in PATH_NAME_LIST}
saved_edge_path = map_handle.scene_path_edge_path
for name in PATH_NAME_LIST:
    setattr(map_config, name, os.path.join(cache_dir, os.path.basename(saved_path[name])))
map_handle.scene_path_edge_path = map_config.scene_path_edge_path
real_load_dir_now = map_config.load_dir_now
rebuild_count = [0]


def counting_load_dir_now(data_path: str):
    """给「从 data/map 重建」计数（只数最外层那一次调用）"""
    if data_path == map_config.map_data_path:
        rebuild_count[0] += 1
    return real_load_dir_now(data_path)


def init_and_count() -> int:
    """
    调一次地图数据载入，返回这一次有没有重建
    Keyword arguments:
    无
    Return arguments:
    int -- 这一次载入里重建的次数（0 或 1）
    """
    before = rebuild_count[0]
    with mock.patch.object(map_config, "load_dir_now", counting_load_dir_now):
        map_config.init_map_data()
    return rebuild_count[0] - before


def read_marker(path_name: str):
    """
    读一个预处理文件里数据后面记的语言
    Keyword arguments:
    path_name -- map_config 里的路径变量名
    Return arguments:
    str -- 记的语言；文件里没有这一项时为 None
    """
    with open(getattr(map_config, path_name), "rb") as cache_file:
        pickle.load(cache_file)
        try:
            return pickle.load(cache_file)
        except EOFError:
            return None


def write_marker(path_name: str, language) -> None:
    """
    把一个预处理文件改写成「同样的数据 + 指定的语言标记」（language 为 None 时不写标记，即旧版本的文件格式）
    Keyword arguments:
    path_name -- map_config 里的路径变量名
    language -- 要写的语言，None 表示不写
    Return arguments:
    无
    """
    path = getattr(map_config, path_name)
    with open(path, "rb") as cache_file:
        data = pickle.load(cache_file)
    with open(path, "wb") as cache_file:
        pickle.dump(data, cache_file)
        if language is not None:
            pickle.dump(language, cache_file)


def scene_ok() -> bool:
    """载入后的场景数据可用：宿舍 101 在，名字是当前语言下的名字"""
    dorm_path = scene_str(SCENE_DORM)
    return dorm_path in cache.scene_data and cache.scene_data[dorm_path].scene_name == _("宿舍101房") and len(constant.place_data.get("Dormitory", [])) > 0


section("1. 没有预处理文件时重建，并记下写出时的语言")
first_rebuild = init_and_count()
marker_dict = {name: read_marker(name) for name in PICKLE_NAME_LIST}
check("目录里没有预处理文件时由 data/map 重建", first_rebuild == 1 and all(os.path.exists(getattr(map_config, name)) for name in PATH_NAME_LIST) and scene_ok(), first_rebuild)
check("重建出的三个预处理文件在数据后面记着当前的游戏语言", marker_dict == {name: NOW_LANGUAGE for name in PICKLE_NAME_LIST}, marker_dict)

section("2. 语言相同时直接读入")
check("预处理文件齐全且记的是当前语言时，不重建", init_and_count() == 0 and scene_ok())

section("3. 记的是另一种语言时重建")
for name in PICKLE_NAME_LIST:
    write_marker(name, OTHER_LANGUAGE)
other_rebuild = init_and_count()
marker_dict = {name: read_marker(name) for name in PICKLE_NAME_LIST}
check("预处理文件是在另一种语言下写出的（换语言后第一次启动）：重建，否则场景名、地图名会停留在旧语言", other_rebuild == 1 and scene_ok(), other_rebuild)
check("重建后三个文件记的语言换回当前语言", marker_dict == {name: NOW_LANGUAGE for name in PICKLE_NAME_LIST}, marker_dict)

section("4. 只有一个文件对不上、或是没有标记的旧文件")
write_marker("all_map_data_path", OTHER_LANGUAGE)
check("三个文件里只要有一个记的不是当前语言，就整体重建", init_and_count() == 1 and read_marker("all_map_data_path") == NOW_LANGUAGE)
write_marker("all_scene_data_path", None)
check("没有语言标记的旧版本预处理文件：重建一次并补上标记", init_and_count() == 1 and read_marker("all_scene_data_path") == NOW_LANGUAGE and scene_ok())
check("补上标记后再载入不再重建", init_and_count() == 0)

for name in PATH_NAME_LIST:
    setattr(map_config, name, saved_path[name])
map_handle.scene_path_edge_path = saved_edge_path
shutil.rmtree(cache_dir, ignore_errors=True)
finish()
