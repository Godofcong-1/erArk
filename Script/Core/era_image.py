import os
from PIL.ImageTk import PhotoImage
from PIL import Image
from Script.Core import main_frame, game_type, cache_control

image_data = {}
image_text_data = {}
image_lock = 0
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
image_dir_path = os.path.join("image")
for image_file_path_id in os.listdir(image_dir_path):
    image_file_path = os.path.join(image_dir_path, image_file_path_id)
    if not image_file_path.endswith(".png"):
        continue
    image_file_name = image_file_path_id.rstrip(".png")
    old_image = PhotoImage(file=image_file_path)
    old_height = old_image.height()
    old_weight = old_image.width()
    font_scaling = main_frame.normal_font.measure("A") / 11
    now_height = int(old_height * font_scaling)
    now_weight = int(old_weight * font_scaling)
    new_image = Image.open(image_file_path).resize((now_weight, now_height))
    image_data[image_file_name] = PhotoImage(new_image)
