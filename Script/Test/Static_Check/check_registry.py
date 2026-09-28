# -*- coding: UTF-8 -*-
"""
静态检查系统 - 检查项注册表
提供 CheckFailure 数据结构、检查项注册表与 register_check 装饰器，供各领域检查模块使用。
"""
from typing import Callable, Dict, List, Tuple


class CheckFailure:
    """
    单条静态检查失败记录
    Keyword arguments:
    check_id -- 检查项唯一编号，例如 "CORE-01"
    check_name -- 检查项中文名称，例如 "角色索引一致性"
    message -- 失败详情描述文本
    involved_character_ids -- 涉及本次失败的角色id列表
    """

    def __init__(self, check_id: str, check_name: str, message: str, involved_character_ids: List[int] = None):
        """
        初始化静态检查失败记录
        参数:
            check_id (str): 检查项唯一编号
            check_name (str): 检查项中文名称
            message (str): 失败详情描述文本
            involved_character_ids (List[int]): 涉及本次失败的角色id列表，默认为空列表
        返回值:
            None
        功能:
            构造一条检查失败记录，用于后续日志写入
        """
        self.check_id: str = check_id
        """ 检查项唯一编号 """
        self.check_name: str = check_name
        """ 检查项中文名称 """
        self.message: str = message
        """ 失败详情描述文本 """
        self.involved_character_ids: List[int] = involved_character_ids if involved_character_ids is not None else []
        """ 涉及本次失败的角色id列表 """


# 检查项注册表，键为检查项id，值为 (检查项中文名称, 检查函数) 二元组
# 使用普通dict即可保持插入顺序（Python3.7+字典有序），保证日志中检查项按注册顺序输出
_check_registry: Dict[str, Tuple[str, Callable[[], List[CheckFailure]]]] = {}


def register_check(check_id: str, check_name: str):
    """
    检查项注册装饰器
    参数:
        check_id (str): 检查项唯一编号，例如 "CORE-01"，要求全局唯一
        check_name (str): 检查项中文名称，用于日志展示
    返回值:
        Callable: 装饰器函数，原样返回被装饰的检查函数
    功能:
        将被装饰的检查函数以 (check_id, (check_name, func)) 的形式登记到全局检查项注册表中，
        供 run_all_checks 遍历调用。检查函数应为无参函数，返回 List[CheckFailure]（空列表代表通过）
    """

    def decorator(func: Callable[[], List[CheckFailure]]) -> Callable[[], List[CheckFailure]]:
        """
        参数:
            func (Callable[[], List[CheckFailure]]): 待注册的检查函数
        返回值:
            Callable[[], List[CheckFailure]]: 原样返回func，不做包装
        功能:
            将func登记进注册表
        """
        if check_id in _check_registry:
            raise ValueError(f"静态检查项id重复注册: {check_id}")
        _check_registry[check_id] = (check_name, func)
        return func

    return decorator


def get_all_checks() -> Dict[str, Tuple[str, Callable[[], List[CheckFailure]]]]:
    """
    参数:
        无
    返回值:
        Dict[str, Tuple[str, Callable[[], List[CheckFailure]]]]: 检查项注册表的浅拷贝，键为检查项id，值为(名称, 函数)
    功能:
        获取当前已注册的全部检查项，供run_all_checks遍历执行；返回浅拷贝以避免调用方误改内部注册表
    """
    return dict(_check_registry)


def make_failure(check_id: str, check_name: str, message: str, involved_character_ids: List[int] = None) -> CheckFailure:
    """
    参数:
        check_id (str): 检查项唯一编号
        check_name (str): 检查项中文名称
        message (str): 失败详情描述文本
        involved_character_ids (List[int]): 涉及本次失败的角色id列表，默认为空列表
    返回值:
        CheckFailure: 构造好的失败记录对象
    功能:
        检查函数内部用于简洁构造CheckFailure的小助手，避免每次都写完整构造语句
    """
    return CheckFailure(check_id, check_name, message, involved_character_ids)
