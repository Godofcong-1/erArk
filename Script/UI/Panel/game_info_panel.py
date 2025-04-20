from types import FunctionType
from Script.UI.Moudle import draw
from Script.Design import game_time, handle_premise
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
        year_draw = draw.NormalDraw()
        # year_draw.width = self.width
        year_draw.text = f"{game_time.get_year_text()} "
        now_draw.draw_list.append(year_draw)
        now_width += len(year_draw)
        solar_period = game_time.get_solar_period(cache.game_time)
        # 月
        month_draw = draw.NormalDraw()
        month_draw.text = f"{game_time.get_month_text()} "
        month_draw.style = "season"
        # month_draw.width = self.width - now_width
        now_draw.draw_list.append(month_draw)
        now_width += len(month_draw)
        # 日和时间和星期
        day_draw = draw.NormalDraw()
        day_draw.text = f"{game_time.get_day_and_time_text()} {game_time.get_week_day_text()} "
        now_draw.draw_list.append(day_draw)
        now_width += len(day_draw)
        # TODO 注释掉节气部分，之后需要在这里换成节日
        # judge, solar_period = game_time.judge_datetime_solar_period(cache.game_time)
        # if judge:
        #     solar_period_config = game_config.config_solar_period[solar_period]
        #     solar_period_draw = draw.NormalDraw()
        #     solar_period_draw.text = f"{solar_period_config.name} "
        #     solar_period_draw.width = self.width - now_width
        #     solar_period_draw.style = "solarperiod"
        #     now_draw.draw_list.append(solar_period_draw)
        #     now_width += len(solar_period_draw)
        # 时段
        sun_time = game_time.get_sun_time(cache.game_time)
        sun_time_config = game_config.config_sun_time[sun_time]
        sun_time_draw = draw.NormalDraw()
        sun_time_draw.text = f"{sun_time_config.name}"
        judge = handle_premise.handle_eat_time(0) # 饭点判断
        if judge:
            sun_time_draw.text += _("(饭点)")
        sun_time_draw.text += " "
        # sun_time_draw.width = self.width - now_width
        now_draw.draw_list.append(sun_time_draw)
        now_width += len(sun_time_draw)
        # 月相
        if sun_time <= 2 or sun_time >= 10:
            moon_phase = game_time.get_moon_phase(cache.game_time)
            moon_phase_config = game_config.config_moon[moon_phase]
            moon_phase_draw = draw.NormalDraw()
            moon_phase_draw.text = f"{moon_phase_config.name} "
            # moon_phase_draw.width = self.width - now_width
            moon_phase_draw.style = "moon"
            now_draw.draw_list.append(moon_phase_draw)
            now_width += len(moon_phase_draw)
        now_judge = game_time.judge_work_today(0)
        work_ro_rest = _("休息")
        if now_judge:
            work_ro_rest = _("工作日")
        work_ro_rest += " "
        work_ro_rest_draw = draw.NormalDraw()
        work_ro_rest_draw.text = work_ro_rest
        # work_ro_rest_draw.width = self.width - now_width
        now_draw.draw_list.append(work_ro_rest_draw)
        now_width += len(work_ro_rest_draw)
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
