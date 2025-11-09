from Script.UI.Moudle import draw
import re

def draw_image_in_talk(talk_text: str):
    """
    绘制口上中的图片
    """
    # 用正则来查找是否有符合{img:图片名}的格式的图片标签，key为图片名，将所有找到的存储为列表
    img_tags = re.findall(r"\{img:([^\}]+)\}", talk_text)
    for img_name in img_tags:
        cross_section_draw = draw.ImageDraw(img_name)
        cross_section_draw.draw()
        # 将标签替换为空字符串
        talk_text = talk_text.replace(f"{{img:{img_name}}}", "")
    # 返回处理后的文本
    return talk_text
