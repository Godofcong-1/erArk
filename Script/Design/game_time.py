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

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
gatech = ephem.Observer()
sun = ephem.Sun()
moon = ephem.Moon()
time_zone = datetime.timezone(datetime.timedelta(hours=+8))


SEASON_MONTH_LIST = (3, 6, 9, 12)
""" 游戏日历的季月：一年只有春夏秋冬 3/6/9/12 四个月，其余月份被时钟跳过 """
SEASON_DAY = 30
""" 游戏日历每个季月固定 30 天，30 日的下一刻就是下一个季月的 1 日，不存在 31 日 """
YEAR_DAY = SEASON_DAY * len(SEASON_MONTH_LIST)
""" 游戏一年的天数（120 天） """
CALENDAR_ANCHOR = datetime.datetime(2019, 3, 1)
""" 游戏日与公历日的对齐基准（默认开局日）：星期、月相从这一天起按游戏日连续推进，开局这一天与公历一致 """


def get_play_time(date: datetime.datetime) -> datetime.timedelta:
    """
    把时间换算成游戏日历上的绝对时长（游戏日序号 + 当日时刻），游戏时间的加减都按它计算
    Keyword arguments:
    date -- 时间（GameTime 或普通 datetime 均可）
    Return arguments:
    datetime.timedelta -- 游戏日历上的绝对时长；
        不在游戏日历上的时间（被时钟跳过的非季月、季月的31日）按下一个季月的1日0时算
    """
    season_month = get_season_month(date.month)
    day_index = date.year * YEAR_DAY + SEASON_MONTH_LIST.index(season_month) * SEASON_DAY
    if season_month != date.month:
        return datetime.timedelta(days=day_index)
    if date.day > SEASON_DAY:
        return datetime.timedelta(days=day_index + SEASON_DAY)
    return datetime.timedelta(days=day_index + date.day - 1, hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)


def to_game_time(date: datetime.datetime) -> "GameTime":
    """
    把任意时间规整成游戏日历上的游戏时间（读旧存档、读配置、普通 datetime 参与推算时用）
    Keyword arguments:
    date -- 时间
    Return arguments:
    GameTime -- 规整后的游戏时间，规则同 get_play_time
    """
    return GameTime.from_play_time(get_play_time(date))


class GameTime(datetime.datetime):
    """
    游戏时间：加减、相减与星期都按游戏日历计算的 datetime\n
    游戏日历只有 3/6/9/12 四个季月、每月 30 天（见 SEASON_MONTH_LIST / SEASON_DAY），30 日的下一刻就是下一个季月的1日；
    datetime 自带的运算按公历走，换季一次会多算约两个月、星期也会跳。
    与普通 datetime 混合相减时（无论左右）同样按游戏日历计算
    """

    __slots__ = ()

    @classmethod
    def from_play_time(cls, play_time: datetime.timedelta) -> "GameTime":
        """
        由游戏日历上的绝对时长（见 get_play_time）还原出游戏时间
        Keyword arguments:
        play_time -- 游戏日历上的绝对时长
        Return arguments:
        GameTime -- 对应的游戏时间
        """
        year, day_index = divmod(play_time.days, YEAR_DAY)
        season_index, day_index = divmod(day_index, SEASON_DAY)
        hour, second = divmod(play_time.seconds, 3600)
        return cls(year, SEASON_MONTH_LIST[season_index], day_index + 1, hour, second // 60, second % 60, play_time.microseconds)

    def __add__(self, other):
        """
        游戏时间加上一段时长，按游戏日历推进（不经过被跳过的非季月）
        Keyword arguments:
        other -- datetime.timedelta 时长
        Return arguments:
        GameTime -- 推进后的游戏时间
        """
        if isinstance(other, datetime.timedelta):
            return GameTime.from_play_time(get_play_time(self) + other)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        """
        游戏时间减去一段时长（得到更早的游戏时间），或减去另一个时间（得到游戏日历上经过的时长）
        Keyword arguments:
        other -- datetime.timedelta 时长，或 datetime.datetime 时间
        Return arguments:
        GameTime | datetime.timedelta -- 回退后的游戏时间，或经过的时长
        """
        if isinstance(other, datetime.timedelta):
            return GameTime.from_play_time(get_play_time(self) - other)
        if isinstance(other, datetime.datetime):
            return get_play_time(self) - get_play_time(other)
        return NotImplemented

    def __rsub__(self, other):
        """
        普通 datetime 减去游戏时间，同样按游戏日历计算经过的时长
        Keyword arguments:
        other -- datetime.datetime 时间
        Return arguments:
        datetime.timedelta -- 经过的时长
        """
        if isinstance(other, datetime.datetime):
            return get_play_time(other) - get_play_time(self)
        return NotImplemented

    def weekday(self) -> int:
        """
        按游戏日连续推算的星期，换季时不跳
        Return arguments:
        int -- 星期0~6（0为周一）
        """
        return get_anchor_date(self).weekday()


def get_anchor_date(date: datetime.datetime) -> datetime.datetime:
    """
    把游戏日换算成以 CALENDAR_ANCHOR 为基准、按天连续的公历日期，供星期、月相这类按天循环的推算使用
    Keyword arguments:
    date -- 时间
    Return arguments:
    datetime.datetime -- 连续的公历日期（0点）
    """
    return CALENDAR_ANCHOR + datetime.timedelta(days=get_play_time(date).days - get_play_time(CALENDAR_ANCHOR).days)


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
    # 配置里的开局日期规整到游戏日历上（不在游戏日历上的日期按下一个季月的1日算）
    game_time = to_game_time(game_time)
    cache.game_time = game_time
    cache.pre_game_time = game_time


def get_season_month(month: int) -> int:
    """
    将任意月份归并为游戏使用的四季月（3春/6夏/9秋/12冬），非季月归到其后的季月：1,2→3、4,5→6、7,8→9、10,11→12
    Keyword arguments:
    month -- 月份（1~12）
    Return arguments:
    int -- 归并后的四季月份（3/6/9/12）
    """
    if month in {1, 2}:
        return 3
    if month in {4, 5}:
        return 6
    if month in {7, 8}:
        return 9
    if month in {10, 11}:
        return 12
    return month


def get_date_text(game_time_data: datetime.datetime = None) -> str:
    """
    获取时间信息描述文本
    Keyword arguments:
    game_timeData -- 时间数据，若为None，则获取当前游戏时间
    """
    if game_time_data is None:
        game_time_data = cache.game_time
    return _("时间:{year}年{month}月{day}日{hour}点{minute}分").format(
        year=game_time_data.year,
        month=get_month_text(game_time_data),
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
    return _("时间:{year}年{month}月{day}日").format(
        year=game_time_data.year,
        month=get_month_text(game_time_data),
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
    # 非四季月（如直接用timedelta相加得到的5月）按归并规则兜底显示为下一个季月
    season_month = get_season_month(game_time_data.month)
    if season_month == 3:
        month_text = _("春")
    elif season_month == 6:
        month_text = _("夏")
    elif season_month == 9:
        month_text = _("秋")
    else:
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
    cache.game_time = get_sub_date(minute, hour, day, month, year)


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
    Return arguments:
    GameTime -- 新日期
    """
    if old_date is None:
        old_date = cache.game_time
    # 普通 datetime（如占位用的默认时间）先规整成游戏时间，保证按游戏日历计算
    new_date = to_game_time(old_date)
    # 年、月按日历推算，落进非季月时按下一个季月的1日0时算
    if month != 0 or year != 0:
        new_date = to_game_time(new_date + relativedelta.relativedelta(years=year, months=month))
    # 天、时、分按游戏日历推进，被跳过的非季月不计入
    return new_date + datetime.timedelta(days=day, hours=hour, minutes=minute)


def get_predict_date(day: int, old_date: datetime.datetime) -> datetime.datetime:
    """
    获取旧日期经过指定天数后、游戏时钟会走到的日期，用于各类"预计X日"的展示
    Keyword arguments:
    day -- 经过的天数
    old_date -- 起始日期
    Return arguments:
    GameTime -- 预计日期
    """
    return get_sub_date(day=day, old_date=old_date)


def get_rand_day_for_year(year: int) -> datetime.datetime:
    """
    随机获取指定年份中一天的日期
    Keyword arguments:
    year -- 年份
    Return arguments:
    time.time -- 随机日期
    """
    start = GameTime(year, SEASON_MONTH_LIST[0], 1)
    end = GameTime(year, SEASON_MONTH_LIST[-1], SEASON_DAY, 23, 59, 59)
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
    计算两个时间之间在游戏日历上经过的天数
    Keyword arguments:
    start_date -- 开始时间
    end_date -- 结束时间
    Return arguments:
    int -- 经过天数，结束早于开始时为负
    """
    return (get_play_time(end_date) - get_play_time(start_date)).days


def count_play_day(
        start_date: datetime.datetime,
        end_date: datetime.datetime,
) -> int:
    """
    计算两个时间之间经过的游戏天数，结束早于开始时取0（Plan 32 §3.2）
    Keyword arguments:
    start_date -- 开始时间
    end_date -- 结束时间
    Return arguments:
    int -- 经过的游戏天数，结束早于开始时为0
    """
    return max(0, count_day_for_datetime(start_date, end_date))


def get_duration_text(day: int) -> str:
    """
    把一段天数换成玩家看的时长文本：满一个季月（30天）的写成「X季月Y天」（Y为0时只写「X季月」），不满一个季月的写成「Y天」
    Keyword arguments:
    day -- 天数（负数按0处理，小数向下取整）
    Return arguments:
    str -- 时长文本，如「2季月5天」「1季月」「12天」
    """
    season_count, rest_day = divmod(max(0, int(day)), SEASON_DAY)
    if season_count == 0:
        return _("{0}天").format(rest_day)
    if rest_day == 0:
        return _("{0}季月").format(season_count)
    return _("{0}季月{1}天").format(season_count, rest_day)


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
        # 按游戏日连续换算出的公历日期推算月相，换季时月相不跳
        new_time = get_anchor_date(now_time)
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


CLASS_PERIOD_START = [(9, 0), (9, 45), (10, 30), (11, 15), (14, 0), (14, 45), (15, 30), (16, 15), (17, 0)]
""" 上课节次的起始时间（Plan 22）：上午4节 + 下午5节，每节45分钟，与既有 teach / attent_class 行为的时长一致。
    晚上时段（19~22）不排课，留给日程活动 """

CLASS_PERIOD_MINUTE = 45
""" 每节课的时长（分钟） """


def get_class_period_by_time(now_time: datetime.datetime) -> int:
    """
    把一个时间点换算为上课节次编号（Plan 22）
    Keyword arguments:
    now_time -- 要换算的时间
    Return arguments:
    int -- 节次编号0~8，不在任何节次内则为-1
    """
    now_minute = now_time.hour * 60 + now_time.minute
    for period, (hour, minute) in enumerate(CLASS_PERIOD_START):
        start = hour * 60 + minute
        if start <= now_minute < start + CLASS_PERIOD_MINUTE:
            return period
    return -1


def get_class_period(character_id: int) -> int:
    """
    校验角色当前处于第几节课（Plan 22）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 节次编号0~8，不在任何节次内则为-1
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    return get_class_period_by_time(now_time)


def get_now_semester() -> tuple:
    """
    取当前学期（Plan 22）。游戏一年只有3/6/9/12四个季月，一个季月即一个学期，不另造时间周期
    Keyword arguments:
    无
    Return arguments:
    tuple -- (年int, 季月int)，季月取值为3/6/9/12
    """
    now_time: datetime.datetime = cache.game_time
    return now_time.year, get_season_month(now_time.month)

