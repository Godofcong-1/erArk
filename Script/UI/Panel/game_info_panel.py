from types import FunctionType
from Script.UI.Moudle import draw
from Script.Design import game_time, character
from Script.Core import get_text, cache_control, game_type
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


class GameTimeInfoPanel:
    """
    查看游戏时间面板
    Keyword arguments:
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width = width
        """ 面板的最大宽度 """
        now_width = 0
        now_draw = draw.CenterMergeDraw(self.width)
        date_draw = draw.NormalDraw()
        date_draw.width = self.width
        date_draw.text = f"{game_time.get_date_text()} {game_time.get_week_day_text()} "
        now_draw.draw_list.append(date_draw)
        now_width += len(date_draw)
        solar_period = game_time.get_solar_period(cache.game_time)
        season = game_config.config_solar_period[solar_period].season
        season_config = game_config.config_season[season]
        season_draw = draw.NormalDraw()
        season_draw.text = f"{season_config.name} "
        season_draw.style = "season"
        season_draw.width = self.width - now_width
        now_draw.draw_list.append(season_draw)
        now_width += len(season_draw)
        judge, solar_period = game_time.judge_datetime_solar_period(cache.game_time)
        if judge:
            solar_period_config = game_config.config_solar_period[solar_period]
            solar_period_draw = draw.NormalDraw()
            solar_period_draw.text = f"{solar_period_config.name} "
            solar_period_draw.width = self.width - now_width
            solar_period_draw.style = "solarperiod"
            now_draw.draw_list.append(solar_period_draw)
            now_width += len(solar_period_draw)
        sun_time = game_time.get_sun_time(cache.game_time)
        sun_time_config = game_config.config_sun_time[sun_time]
        sun_time_draw = draw.NormalDraw()
        sun_time_draw.text = f"{sun_time_config.name} "
        sun_time_draw.width = self.width - now_width
        now_draw.draw_list.append(sun_time_draw)
        now_width += len(sun_time_draw)
        if sun_time <= 2 or sun_time >= 10:
            moon_phase = game_time.get_moon_phase(cache.game_time)
            moon_phase_config = game_config.config_moon[moon_phase]
            moon_phase_draw = draw.NormalDraw()
            moon_phase_draw.text = f"{moon_phase_config.name} "
            moon_phase_draw.width = self.width - now_width
            moon_phase_draw.style = "moon"
            now_draw.draw_list.append(moon_phase_draw)
            now_width += len(moon_phase_draw)
        now_judge = game_time.judge_attend_class_today(0)
        attend_class = _("(休息)")
        if now_judge:
            attend_class = _("(工作日)")
        attend_class += " "
        attend_class_draw = draw.NormalDraw()
        attend_class_draw.text = attend_class
        attend_class_draw.width = self.width - now_width
        now_draw.draw_list.append(attend_class_draw)
        now_width += len(attend_class_draw)
        if character.judge_character_in_class_time(0):
            now_attend_class = _("上课时间")
            now_attend_class += " "
            now_attend_class_draw = draw.NormalDraw()
            now_attend_class_draw.text = now_attend_class
            attend_class_draw.width = self.width - now_width
            now_width += len(now_attend_class_draw)
            now_draw.draw_list.append(now_attend_class_draw)
        self.width = now_width
        now_draw.width = self.width
        self.now_draw: draw.NormalDraw = now_draw
        """ 当前面板绘制对象 """

    def __len__(self):
        """获取绘制宽度"""
        return self.width

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
