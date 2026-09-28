# -*- coding: UTF-8 -*-
"""
静态检查系统 - 领域检查模块汇总入口
各领域检查模块在此以显式静态import接入，使其内部的@register_check装饰器在模块载入时完成注册。
每个模块独立隔离导入异常：一个模块失败只损失自身注册项，其后模块仍继续注册；显式import也保证PyInstaller能够静态收集。
导入顺序：check_core打头，其余按模块名字母序排列。
"""
from .. import check_log

try:
    from . import check_core  # noqa: F401  核心示例检查（CORE-01…CORE-02）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_behavior  # noqa: F401  行为/时间/状态机检查（BEHAV-01…BEHAV-22）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_body  # noqa: F401  服装/污浊/身体检查（BODY-01…BODY-35）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_education  # noqa: F401  养成与课表检查（EDU-01…EDU-12）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_h_group  # noqa: F401  H/群交检查（HGROUP-01…HGROUP-31）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_island  # noqa: F401  基建/岛屿检查（ISLAND-01…ISLAND-33）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_mind  # noqa: F401  意识/催眠检查（MIND-01…MIND-30）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_numeric  # noqa: F401  数值范围检查（NUM-01…NUM-30）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_observable  # noqa: F401  可观察矛盾检查（OBS-01…OBS-18）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_official  # noqa: F401  公务检查（OFFICIAL-01…OFFICIAL-02）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_place  # noqa: F401  位置/场景/交互对象检查（PLACE-01…PLACE-31）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_roster  # noqa: F401  名册/派生身份表检查（ROSTER-01…ROSTER-33）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_setting  # noqa: F401  生育与烹饪设置检查（BIRTH-01…02、COOK-01…02）
except Exception as _e:
    check_log.write_self_error_log(_e)

try:
    from . import check_supplement  # noqa: F401  补充盲点检查（SUPP-01…SUPP-08）
except Exception as _e:
    check_log.write_self_error_log(_e)
