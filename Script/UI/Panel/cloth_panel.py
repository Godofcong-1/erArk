from typing import List
from types import FunctionType
from Script.Core import game_type, cache_control, rich_text, get_text
from Script.Config import game_config
from Script.Design import attr_calculation
from Script.UI.Moudle import draw, panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class SeeCharacterClothPanel:
    """
    显示角色服装面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, type_number: int, center_status: bool = True):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.column = column
        """ 每行状态最大个数 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.center_status: bool = center_status
        """ 居中绘制状态文本 """
        self.type_number = type_number
        """ 显示的状态类型 """
        character_data = cache.character_data[0]
        target_character_data = cache.character_data[character_data.target_character_id]

        type_line = draw.LittleTitleLineDraw(_("服装"), width, ":")
        self.draw_list.append(type_line)

        # cloth_text_list = []
        now_text = ""
        # 遍历全部衣服类型
        # print(f"debug target_character_data.cloth.cloth_wear = {target_character_data.cloth.cloth_wear}")
        for clothing_type in game_config.config_clothing_type:
            type_name = game_config.config_clothing_type[clothing_type].name
            # 当该类型里有衣服存在的时候才显示
            if len(target_character_data.cloth.cloth_wear[clothing_type]):
                # 正常情况下不显示胸部和内裤的服装,debug或该部位可以显示则显示
                if clothing_type in {6, 9} and not cache.debug_mode:
                    # print(f"debug {target_character_data.name}.cloth_see[clothing_type] = {target_character_data.cloth_see[clothing_type]}")
                    # 以下情况自动显示：
                    # 1.开启透视能力
                    # 2.没穿对应部位外面的衣服
                    if (
                            (character_data.pl_ability.visual and character_data.talent[307])
                            or len(target_character_data.cloth.cloth_wear[clothing_type - 1]) == 0
                    ):
                        target_character_data.cloth.cloth_see[clothing_type] = True
                    else:
                        target_character_data.cloth.cloth_see[clothing_type] = False
                    # 如果不显示，则不显示（废话
                    if not target_character_data.cloth.cloth_see[clothing_type]:
                        continue
                # 当显示到下衣8的时候，换行
                if clothing_type == 8 and now_text != "":
                    now_text += "\n"
                now_text += f"  [{type_name}]:"
                # 如果有多个衣服，则依次显示
                for cloth_id in target_character_data.cloth.cloth_wear[clothing_type]:
                    cloth_name = game_config.config_clothing_tem[cloth_id].name
                    now_text += f" {cloth_name}"
                    # 这里出现过BUG，所以加一层检测是否为空的判断
                    if len(target_character_data.dirty.cloth_semen) == 0:
                        empty_dirty_data = attr_calculation.get_dirty_zero(target_character_data.dirty)
                        target_character_data.dirty.cloth_semen = empty_dirty_data.cloth_semen
                    # 如果该部位有精液，则显示精液信息
                    if target_character_data.dirty.cloth_semen[clothing_type][1] != 0:
                        semen_level = target_character_data.dirty.cloth_semen[clothing_type][2]
                        dirty_text_cid = "{0}精液污浊{1}".format(_(type_name, revert_translation = True), str(semen_level))
                        dirty_text_context = game_config.ui_text_data['dirty'][dirty_text_cid]
                        now_text += f"<semen>({dirty_text_context})</semen>"
            # 当显示到下衣8的时候，换行
            if clothing_type == 8 and len(target_character_data.cloth.cloth_wear[8]) == 0:
                now_text += "\n"
            # 真空的胸衣和内裤单独显示
            if clothing_type in {6, 9} and not len(target_character_data.cloth.cloth_wear[clothing_type]):
                if not cache.debug_mode:
                    # print(f"debug {target_character_data.name}.cloth.cloth_see[clothing_type] = {target_character_data.cloth.cloth_see[clothing_type]}")
                    if not target_character_data.cloth.cloth_see[clothing_type]:
                        continue
                now_text += _("  [{0}]: 真空").format(type_name)
        now_text += "\n"
        # cloth_text_list.append(now_text)

        no_cloth_flag = True
        for clothing_type in game_config.config_clothing_type:
            if len(target_character_data.cloth.cloth_wear[clothing_type]):
                no_cloth_flag = False
                break
        if no_cloth_flag:
            now_text = _("  全裸\n")
            # cloth_text_list.append(now_text)

        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()

        # 富文本模组
        now_style_list = rich_text.get_rich_text_print(now_text, "standard")
        new_x_list = rich_text.remove_rich_cache(now_text)
        # test_flag = False
        # if 'emoji' in now_style_list:
        #     test_flag = True
        #     print(f"debug 总：now_style_list = {now_style_list}")
        #     print(f"debug 总：new_x_list = {new_x_list}")
        while 1:
            if not len(new_x_list):
                break
            # now_rich_draw = game_type.MapDrawText()
            now_rich_draw = draw.NormalDraw()
            now_rich_draw.text = new_x_list[0]
            now_rich_draw.style = now_style_list[0]
            now_style_list = now_style_list[1:]
            new_x_list = new_x_list[1:]
            # if test_flag:
            #     print(f"debug now_rich_draw.style = {now_rich_draw.style}")
            while 1:
                if not len(new_x_list):
                    break
                if now_style_list[0] != now_rich_draw.style:
                    break
                now_rich_draw.text += new_x_list[0]
                now_style_list = now_style_list[1:]
                new_x_list = new_x_list[1:]
                # if test_flag:
                #     print(f"debug 分：now_rich_draw.text = {now_rich_draw.text}")
                #     print(f"debug 分：now_style_list = {now_style_list}")
                #     print(f"debug 分：new_x_list = {new_x_list}")
            now_draw.draw_list.append(now_rich_draw)
            now_draw.width += len(now_rich_draw.text)

        # now_draw.set(cloth_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

