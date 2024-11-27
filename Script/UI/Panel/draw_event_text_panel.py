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
        self.style: str = "standard"
        """ 绘制文本的样式 """
        player_data: game_type.Character = cache.character_data[0]
        if cache.is_collection:
            if character_id and character_id not in player_data.collection_character:
                return
        character_data: game_type.Character = cache.character_data[character_id]
        if player_data.position not in [character_data.position, character_data.behavior.move_target]:
            return

        son_event_flag = False # 子事件标记
        diy_event_flag = False  # diy事件标记

        event_data = game_config.config_event[self.event_id]

        # 如果玩家身上有角色diy事件标记
        if character_data.event.chara_diy_event_flag:
            # 更新事件id
            self.event_id = character_data.event.event_id
            event_data = game_config.config_event[self.event_id]
            # 如果文本中没有两个|，则不是diy事件，不触发
            if event_data.text.count("|") < 2:
                return
            # 清除角色的diy事件标记
            character_data.event.chara_diy_event_flag = False
            # 触发diy事件标记
            diy_event_flag = True

        # 检查是否是子事件
        if "option_son" in event_data.premise:
            son_event_flag = True
        for primise in event_data.premise:
            if "CVP_A1_Son" in primise:
                son_event_flag = True
                break

        # 子事件的文本里去掉选项内容
        if son_event_flag and "|" in event_data.text:
            now_event_text: str = "\n" + event_data.text.split("|")[1]
        # diy事件的文本里去掉选项和行动事件内容
        elif diy_event_flag and "|" in event_data.text:
            now_event_text: str = "\n" + event_data.text.split("|")[2]
        else:
            now_event_text: str = "\n" + event_data.text

        # 代码词语
        now_event_text = talk.code_text_to_draw_text(now_event_text, character_id)
        self.text = now_event_text

        # 口上颜色
        character_data: game_type.Character = cache.character_data[character_id]
        target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
        text_color = character_data.text_color
        tar_text_color = target_character_data.text_color
        if text_color:
            self.style = character_data.name
        elif tar_text_color:
            self.style = target_character_data.name
