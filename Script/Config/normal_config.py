import os
import json
import configparser
import sys
from Script.Core import game_type, game_path_config


config_normal: game_type.NormalConfig = game_type.NormalConfig()
""" 游戏通用配置数据 """
package_path = os.path.join("package.json")


def get_config_ini_path() -> str:
    """获取 config.ini 的绝对路径"""
    candidate_paths = []
    if getattr(sys, "frozen", False):
        candidate_paths.append(os.path.join(os.path.dirname(sys.executable), "config.ini"))
    candidate_paths.append(os.path.join(game_path_config.game_path, "config.ini"))
    candidate_paths.append(os.path.abspath("config.ini"))
    for candidate_path in candidate_paths:
        if os.path.exists(candidate_path):
            return candidate_path
    return candidate_paths[0]


def init_normal_config():
    """初始化游戏通用配置数据"""
    ini_config = configparser.ConfigParser()
    ini_config.read(get_config_ini_path(), encoding="utf8")
    ini_data = ini_config["game"]
    for k in ini_data.keys():
        try:
            config_normal.__dict__[k] = int(ini_data[k])
        except:
            config_normal.__dict__[k] = ini_data[k]
    if os.path.exists(package_path):
        with open(package_path, "r") as package_file:
            version_data = json.load(package_file)
            config_normal.verson = version_data["version"]
    else:
        config_normal.verson = "Orgin"
