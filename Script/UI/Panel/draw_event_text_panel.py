from Script.Core import cache_control, game_type
from Script.Design import map_handle
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
        now_event_text: str = "\n" + game_config.config_event[event_id].text
        scene_path = character_data.position
        scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        scene_name = scene_data.scene_name
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        src_scene_name = ""
        if len(player_data.behavior.move_src):
            src_scene_path_str = map_handle.get_map_system_path_str_for_list(player_data.behavior.move_src)
            src_scene_data: game_type.Scene = cache.scene_data[src_scene_path_str]
            src_scene_name = src_scene_data.scene_name
        target_scene_name = ""
        if len(character_data.behavior.move_target):
            target_scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.behavior.move_target)
            target_scene_data: game_type.Scene = cache.scene_data[target_scene_path_str]
            target_scene_name = target_scene_data.scene_name
        now_event_text = now_event_text.format(
            NickName=player_data.nick_name,
            FoodName=character_data.behavior.food_name,
            Name=character_data.name,
            SceneName=scene_name,
            TargetName=target_data.name,
            TargetSceneName=target_scene_name,
            SrcSceneName=src_scene_name,
        )
        self.text = now_event_text
