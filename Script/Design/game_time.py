import datetime
import time
import random
import math
import ephem
import time
from types import FunctionType
from dateutil import relativedelta
from Script.Core import (
    cache_control,
    game_type,
    get_text,
)
from Script.Config import normal_config, game_config
from Script.Design import character

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
gatech = ephem.Observer()
sun = ephem.Sun()
moon = ephem.Moon()
time_zone = datetime.timezone(datetime.timedelta(hours=+8))


def init_time():
    """
    初始化游戏时间
    """
    game_time = datetime.datetime(
        normal_config.config_normal.year,
        normal_config.config_normal.month,
        normal_config.config_normal.day,
        normal_config.config_normal.hour,
        normal_config.config_normal.minute,
    )
    cache.game_time = game_time
    cache.pre_game_time = game_time


def get_date_text(game_time_data: datetime.datetime = None) -> str:
    """
    获取时间信息描述文本
    Keyword arguments:
    game_timeData -- 时间数据，若为None，则获取当前游戏时间
    """
    if game_time_data is None:
        game_time_data = cache.game_time
    if game_time_data.month == 3:
        month_text = "春"
    elif game_time_data.month == 6:
        month_text = "夏"
    elif game_time_data.month == 9:
        month_text = "秋"
    elif game_time_data.month == 12:
        month_text = "冬"
    return _("时间:{year}年{month}月{day}日{hour}点{minute}分").format(
        year=game_time_data.year,
        month=month_text,
        day=game_time_data.day,
        hour=game_time_data.hour,
        minute=game_time_data.minute,
    )


def get_date_until_day(game_time_data: datetime.datetime = None) -> str:
    """
    获取到日为止的时间信息描述文本
    Keyword arguments:
    game_timeData -- 时间数据，若为None，则获取当前游戏时间
    """
    if game_time_data is None:
        game_time_data = cache.game_time
    if game_time_data.month == 3:
        month_text = "春"
    elif game_time_data.month == 6:
        month_text = "夏"
    elif game_time_data.month == 9:
        month_text = "秋"
    elif game_time_data.month == 12:
        month_text = "冬"
    return _("时间:{year}年{month}月{day}日").format(
        year=game_time_data.year,
        month=month_text,
        day=game_time_data.day,
    )


def get_year_text(game_time_data: datetime.datetime = None) -> str:
    """
    获取年份描述文本
    Keyword arguments:
    game_timeData -- 时间数据，若为None，则获取当前游戏时间
    """
    if game_time_data is None:
        game_time_data = cache.game_time
    return _("时间:{year}年").format(
        year=game_time_data.year,
    )


def get_month_text(game_time_data: datetime.datetime = None) -> str:
    """
    获取月份描述文本
    Keyword arguments:
    game_timeData -- 时间数据，若为None，则获取当前游戏时间
    """
    if game_time_data is None:
        game_time_data = cache.game_time
    if game_time_data.month == 3:
        month_text = _("春")
    elif game_time_data.month == 6:
        month_text = _("夏")
    elif game_time_data.month == 9:
        month_text = _("秋")
    elif game_time_data.month == 12:
        month_text = _("冬")
    return _("{month}").format(
        month=month_text,
    )


def get_day_and_time_text(game_time_data: datetime.datetime = None) -> str:
    """
    获取日和时间描述文本
    Keyword arguments:
    game_timeData -- 时间数据，若为None，则获取当前游戏时间
    """
    if game_time_data is None:
        game_time_data = cache.game_time
    return _("{day}日 {hour}点{minute}分").format(
        day=game_time_data.day,
        hour=game_time_data.hour,
        minute=game_time_data.minute,
    )


def get_week_day_text() -> str:
    """
    获取星期描述文本
    """
    week_day = cache.game_time.weekday()
    week_date_data = game_config.config_week_day[week_day]
    return week_date_data.name


def sub_time_now(minute=0, hour=0, day=0, month=0, year=0) -> datetime.datetime:
    """
    增加当前游戏时间
    Keyword arguments:
    minute -- 增加的分钟
    hour -- 增加的小时
    day -- 增加的天数
    month -- 增加的月数
    year -- 增加的年数
    """
    new_date = get_sub_date(minute, hour, day, month, year)

    # 切月时对全角色的行为开始时间进行重置
    if new_date.month > cache.game_time.month:
        new_date = new_date.replace(day = 1)
        for character_id in cache.npc_id_got:
            character.init_character_behavior_start_time(character_id, new_date)

    cache.game_time = new_date


def get_sub_date(
        minute=0,
        hour=0,
        day=0,
        month=0,
        year=0,
        old_date: datetime.datetime = None,
) -> datetime.datetime:
    """
    获取旧日期增加指定时间后得到的新日期
    Keyword arguments:
    minute -- 增加分钟
    hour -- 增加小时
    day -- 增加天数
    month -- 增加月数
    year -- 增加年数
    old_date -- 旧日期，若为None，则获取当前游戏时间
    """
    if old_date is None:
        old_date = cache.game_time
    new_date = old_date + relativedelta.relativedelta(
        years=year, months=month, days=day, hours=hour, minutes=minute
    )
    # 进行月份调整，保留四个月为春夏秋冬四月，其他月份自动跳转为以上月份
    if new_date.month in {1,2}:
        new_date = new_date.replace(month = 3)
    elif new_date.month in {4,5}:
        new_date = new_date.replace(month = 6)
    elif new_date.month in {7,8}:
        new_date = new_date.replace(month = 9)
    elif new_date.month in {10,11}:
        new_date = new_date.replace(month = 12)
    return new_date


def get_rand_day_for_year(year: int) -> datetime.datetime:
    """
    随机获取指定年份中一天的日期
    Keyword arguments:
    year -- 年份
    Return arguments:
    time.time -- 随机日期
    """
    start = datetime.datetime(year, 1, 1, 0, 0, 0, 0)
    end = datetime.datetime(year, 12, 31, 23, 59, 59)
    return get_rand_day_for_date(start, end)


def timetuple_to_datetime(t: datetime.datetime.timetuple) -> datetime.datetime:
    """
    将timetulp类型数据转换为datetime类型
    Keyword arguments:
    t -- timetulp类型数据
    Return arguments:
    d -- datetime类型数据
    """
    return datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


def get_rand_day_for_date(start_date: datetime.datetime, end_date: datetime.datetime) -> datetime.datetime:
    """
    随机获取两个日期中的日期
    Keyword arguments:
    start_date -- 开始日期
    end_date -- 结束日期
    Return arguments:
    time.localtime -- 随机日期
    """
    sub_day = (end_date - start_date).days
    sub_day = random.randint(0, sub_day)
    return get_sub_date(day=sub_day, old_date=start_date)


def count_day_for_datetime(
        start_date: datetime.datetime,
        end_date: datetime.datetime,
) -> int:
    """
    计算两个时间之间经过的天数
    Keyword arguments:
    start_date -- 开始时间
    end_date -- 结束时间
    Return arguments:
    int -- 经过天数
    """
    return (end_date - start_date).days


def judge_date_big_or_small(time_a: datetime.datetime, time_b: datetime.datetime) -> int:
    """
    比较a时间是否大于或等于b时间\n
    Keyword arguments:\n
    time_a -- 当前时间\n
    time_b -- 旧时间\n
    Return arguments:\n
    0 -- 小于\n
    1 -- 大于\n
    2 -- 等于
    """
    if time_a == time_b:
        return 2
    else:
        return time_a > time_b


def ecliptic_lon(now_time: datetime.datetime) -> float:
    """
    根据日期计算黄经
    now_time -- 日期
    Return arguments:
    float -- 黄经
    """
    s = ephem.Sun(now_time)
    equ = ephem.Equatorial(s.ra, s.dec, epoch=now_time)
    e = ephem.Ecliptic(equ)
    return e.lon


def get_solar_period(now_time: datetime.datetime) -> int:
    """
    根据日期计算对应节气id
    Keyword arguments:
    now_time -- 日期
    Return arguments:
    int -- 节气id
    """
    e = ecliptic_lon(now_time)
    n = int(e * 180.0 / math.pi / 15)
    return n


def get_old_solar_period_time(now_time: datetime.datetime) -> (datetime.datetime, int):
    """
    根据日期计算上个节气的开始日期
    Keyword arguments:
    now_time -- 日期
    Return arguments:
    new_time -- 节气日期
    """
    s1 = get_solar_period(now_time)
    s0 = s1
    dt = 1
    new_time = now_time
    while True:
        new_time = get_sub_date(day=-dt, old_date=new_time)
        s = get_solar_period(new_time)
        if s0 != s:
            s0 = s
            dt = -dt / 2
        if s != s1 and abs(dt) < 1:
            break
    return new_time, s0


def get_next_solar_period_time(now_time: datetime.datetime) -> (datetime.datetime, int):
    """
    根据日期计算下个节气的开始日期
    Keyword arguments:
    now_time -- 日期
    Return arguments:
    new_time -- 节气日期
    """
    s1 = get_solar_period(now_time)
    s0 = s1
    dt = 1
    new_time = now_time
    while True:
        new_time = get_sub_date(day=dt, old_date=new_time)
        s = get_solar_period(new_time)
        if s0 != s:
            s0 = s
            dt = -dt / 2
        if s != s1 and abs(dt) < 1:
            break
    return new_time, s0


def judge_datetime_solar_period(now_time: datetime.datetime) -> (bool, int):
    """
    校验日期是否是节气以及获取节气id
    Keyword arguments:
    now_time -- 日期
    Return arguments:
    bool -- 校验结果
    int -- 节气id
    """
    new_time, solar_period = get_old_solar_period_time(now_time)
    if new_time.year == now_time.year and new_time.month == now_time.month and new_time.day == now_time.day:
        return 1, solar_period
    new_time, solar_period = get_next_solar_period_time(now_time)
    if new_time.year == now_time.year and new_time.month == now_time.month and new_time.day == now_time.day:
        return 1, solar_period
    return 0, 0


def get_sun_time(old_time: datetime.datetime) -> int:
    """
    根据时间获取太阳位置id
    Keyword arguments:
    old_time -- 时间
    Return arguments:
    int -- 太阳位置id
    """
    if "sun_phase" not in cache.__dict__:
        cache.__dict__["sun_phase"] = {}
    now_sun_time = (old_time.hour + 3) // 2
    now_sun_time += 12 if now_sun_time < 0 else 0
    now_sun_time -= 12 if now_sun_time > 11 else 0
    return now_sun_time


def get_sun_phase_for_sun_az(now_az: float) -> int:
    """
    根据太阳夹角获取太阳位置对应配表id
    Keyword arguments:
    now_az -- 太阳夹角
    Return arguments:
    太阳位置配表id
    """
    if 225 <= now_az < 255:
        return 8
    elif 255 <= now_az < 285:
        return 9
    elif 285 <= now_az < 315:
        return 10
    elif 315 <= now_az < 345:
        return 11
    elif now_az >= 345 or now_az < 15:
        return 0
    elif 15 <= now_az < 45:
        return 1
    elif 45 <= now_az < 75:
        return 2
    elif 75 <= now_az < 105:
        return 3
    elif 105 <= now_az < 135:
        return 4
    elif 135 <= now_az < 165:
        return 5
    elif 165 <= now_az < 195:
        return 6
    return 7


def get_moon_phase(now_time: datetime.datetime) -> int:
    """
    根据时间获取月相配置id
    Keyword arguments:
    now_time -- 时间
    Return arguments:
    int -- 月相配置id
    """
    if "moon_phase" not in cache.__dict__:
        cache.__dict__["moon_phase"] = {}
    now_date_str = f"{now_time.year}/{now_time.month}/{now_time.day}"
    if now_date_str not in cache.moon_phase:
        new_time = datetime.datetime(now_time.year, now_time.month, now_time.day)
        new_time.astimezone(time_zone)
        gatech.date = datetime.datetime.utcfromtimestamp(time.mktime(new_time.utctimetuple()))
        moon.compute(gatech)
        now_phase = moon.phase
        gatech.date += 1
        moon.compute(gatech)
        next_phase = moon.phase
        now_type = next_phase > now_phase
        for phase in game_config.config_moon_data[now_type]:
            phase_config = game_config.config_moon[phase]
            if phase_config.min_phase < now_phase <= phase_config.max_phase:
                cache.moon_phase[now_date_str] = phase_config.cid
                break
        if len(cache.moon_phase) > 3:
            del_date = list(cache.moon_phase.keys())[0]
            del cache.moon_phase[del_date]
    return cache.moon_phase[now_date_str]


def judge_work_today(character_id: int) -> bool:
    """
    校验角色今日是否需要工作
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 周一到周五为1，周末为0
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    now_week = now_time.weekday()
    if now_week < 6:
        return 1
    else:
        return 0


def judge_entertainment_time(character_id: int) -> int:
    """
    校验当前娱乐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 0为不在娱乐时间段，1为早上，2为下午，3为晚上
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    now_hour = now_time.hour
    if 9 <= now_hour < 12:
        return 1
    elif 14 <= now_hour < 18:
        return 2
    elif 19 <= now_hour < 22:
        return 3
    return 0


# def judge_attend_class_today(character_id: int) -> bool:
#     """
#     校验角色今日是否需要上课
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 权重
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     now_time: datetime.datetime = character_data.behavior.start_time
#     if now_time is None:
#         now_time = cache.game_time
#     now_week = now_time.weekday()
#     now_month = now_time.month
#     if now_month not in {3, 4, 5, 6, 8, 9, 10, 11, 12}:
#         return 0
#     if character_data.age <= 18:
#         if character_data.age > 15:
#             return 1
#         if character_data.age > 13 and now_week < 6:
#             return 1
#         if now_week < 5:
#             return 1
#     elif (
#         character_id in cache.teacher_phase_table
#         and now_week in cache.teacher_class_week_day_data[character_id]
#     ):
#         return 1
#     return 0
