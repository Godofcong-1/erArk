import os
import json
import configparser
from Script.Core import game_type


config_normal: game_type.NormalConfig = game_type.NormalConfig()
""" 游戏通用配置数据 """
package_path = os.path.join("package.json")


def init_normal_config():
    """初始化游戏通用配置数据"""
    ini_config = configparser.ConfigParser()
    ini_config.read("config.ini", encoding="utf8")
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
