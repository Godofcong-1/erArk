import random
import bisect
import itertools
import math
import numpy
from typing import Dict, List


def two_bit_array_to_dict(array: tuple) -> dict:
    """
    将二维数组转换为字典
    Keyword arguments:
    array -- 要转换的二维数组
    """
    return dict(array)


def get_rand_value_for_value_region(value_list: List[int]) -> int:
    """
    以列表中每个元素的值作为权重随机获取一个元素
    Keyword arguments:
    value_list -- 要计算的列表
    Return arguments:
    int -- 获得的元素
    """
    return random.choices(value_list, weights=value_list)[0]
    # key_list = [math.ceil(i) for i in value_list]
    # now_data = dict(zip(itertools.accumulate(key_list), value_list))
    # weight_max = sum(key_list)
    # weight_region_list = list(now_data.keys())
    # now_weight = random.randint(0, weight_max - 1)
    # weight_region = get_next_value_for_list(now_weight, weight_region_list)
    # return now_data[weight_region]


def get_region_list(now_data: Dict[any, int]) -> dict:
    """
    按dict中每个value的值对key进行排序，并计算权重区域列表
    Keyword arguments:
    now_data -- 需要进行计算权重的dict数据
    """
    sort_data = sorted_dict_for_values(now_data)
    return dict(zip(itertools.accumulate(sort_data.values()), sort_data.keys()))


def sorted_dict_for_values(old_dict: Dict[any, int]) -> dict:
    """
    按dict中每个value的值对key进行排序生成新dict
    Keyword arguments:
    old_dict -- 需要进行排序的数据
    """
    return two_bit_array_to_dict(sorted(old_dict.items(), key=lambda x: x[1]))


def get_random_for_weight(data: Dict[any, int]) -> any:
    """
    按权重随机获取dict中的一个key
    Keyword arguments:
    data -- 需要随机获取key的dict数据
    """
    keys = list(data.keys())
    weights = list(data.values())
    return random.choices(keys, weights=weights)[0]


def get_next_value_for_list(now_int: int, int_list: List[int]) -> int:
    """
    获取列表中第一个比指定值大的数
    Keyword arguments:
    now_int -- 作为获取参考的指定数值
    int_list -- 用于取值的列表
    """
    now_id = bisect.bisect_left(int_list, now_int)
    return int_list[now_id]


def get_old_value_for_list(now_int: int, int_list: List[int]) -> int:
    """
    获取列表中第一个比指定值小的数
    Keyword arguments:
    now_int -- 作为获取参考的指定数值
    int_list -- 用于取值的列表
    Return arguments:
    int -- 查询到的值
    """
    now_id = bisect.bisect_right(int_list, now_int)
    return int_list[now_id - 1]


def list_of_groups(init_list: list, children_list_len: int) -> List[List[any]]:
    """
    将列表分割为指定长度的列表集合
    Keyword arguments:
    init_list -- 原始列表
    children_list_len -- 指定长度
    Return arguments:
    List[list] -- 新列表
    """
    list_of_groups = zip(*(iter(init_list),) * children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    if count:
        end_list.append(init_list[-count:])
    return end_list


def get_gauss_rand(min_value: int, max_value: int) -> int:
    """
    通过正态分布获取两个值之间的随机值
    Keyword arguments:
    min_value -- 最小值
    max_value -- 最大值
    Return arguments:
    int -- 获取的随机值
    """
    mu = (min_value + max_value) / 2
    single = mu - min_value
    value = numpy.random.normal(mu, single)
    value = numpy.clip(value, min_value, max_value)
    return int(value)
