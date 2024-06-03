from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import handle_premise

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

def draw_cross_section_image():
    """
    选择并绘制断面图
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    # 如果没有目标角色则返回
    if pl_character_data.target_character_id == 0:
        return
    # 判断精液量
    if handle_premise.handle_t_vw_semen_g_1000(0):
        img_name = "精液多"
    elif handle_premise.handle_t_vw_semen_g_200(0):
        img_name = "精液中"
    elif handle_premise.handle_t_vw_semen_g_1(0):
        img_name = "精液少"
    # 判断怀孕
    elif handle_premise.handle_t_fertilization_1(0):
        img_name = "受精"
    elif handle_premise.handle_t_pregnancy_1(0):
        img_name = "妊娠"
    elif handle_premise.handle_t_parturient_1(0):
        img_name = "临盆"
    # 判断生理期
    elif handle_premise.handle_t_reproduction_period_3(0):
        img_name = "排卵期"
    elif handle_premise.handle_t_reproduction_period_2(0):
        img_name = "危险期"
    # 都没有则为标准状态
    else:
        img_name = "标准状态"
    # 判断阴茎位置
    if handle_premise.handle_penis_in_t_vagina(0):
        img_name += "_插入"
    cross_section_draw = draw.ImageDraw(img_name)
    cross_section_draw.draw()
