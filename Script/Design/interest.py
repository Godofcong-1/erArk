import numpy
from Script.Core import cache_control, game_type, value_handle
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def init_character_interest():
    """
    初始化全部角色兴趣/精力/天赋数值分配
    """
    for character in cache.character_data:
        numpy.random.shuffle(knowledge_skills)
        numpy.random.shuffle(language_skills)
        for knowledge in knowledge_skills:
            cache.character_data[character].knowledge_interest[knowledge] = value_handle.get_gauss_rand(
                0.5, 1.5
            )
        for language in language_skills:
            cache.character_data[character].language_interest[language] = value_handle.get_gauss_rand(
                0.5, 1.5
            )
