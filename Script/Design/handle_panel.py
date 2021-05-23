from functools import wraps
from types import FunctionType
from Script.Core import constant


def add_panel(panel: int) -> FunctionType:
    """
    添加面板
    Keyword arguments:
    panel -- 面板id
    Return arguments:
    FunctionType -- 面板绘制对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.panel_data[panel] = return_wrapper
        return return_wrapper

    return decoraror
