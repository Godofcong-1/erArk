from Script.Core import cache_control, game_type
from Script.Design import talk
from Script.UI.Moudle import draw
from Script.Config import normal_config, game_config


window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class DrawEventTextPanel(draw.LineFeedWaitDraw):
    """
    用于绘制事件描述文本的面板对象
    Keyword arguments:
    event_id -- 事件id
    character_id -- 触发事件的角色id
    """

    def __init__(self, event_id: str,character_id: int, event_type: int):
        """初始化绘制对象"""
        self.width: int = window_width
        """ 绘制的最大宽度 """
        self.event_id: str = event_id
        """ 事件id """
        self.character_id: int = character_id
        """ 触发事件的角色id """
        self.event_type: int = event_type
        """ 事件的类型 """
        self.text: str = ""
        """ 当前绘制的文本 """
        player_data: game_type.Character = cache.character_data[0]
        if cache.is_collection:
            if character_id and character_id not in player_data.collection_character:
                return
        character_data: game_type.Character = cache.character_data[character_id]
        if player_data.position not in [character_data.position, character_data.behavior.move_target]:
            return

        # 子事件的文本里去掉选项内容
        if "option_son" in game_config.config_event[event_id].premise:
            now_event_text: str = "\n" + game_config.config_event[event_id].text.split("|")[1]
        else:
            now_event_text: str = "\n" + game_config.config_event[event_id].text

        # 代码词语
        now_event_text = talk.code_text_to_draw_text(now_event_text, character_id)
        self.text = now_event_text
