import os
from PIL.ImageTk import PhotoImage
from PIL import Image
from Script.Core import main_frame, game_type, cache_control

image_data = {}
image_data_index_by_chara = {}
image_text_data = {}
image_lock = 0
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
image_dir_path = os.path.join("image")

def load_images_from_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                image_file_path = os.path.join(root, file)
                image_file_name = file.rstrip(".png")
                old_image = PhotoImage(file=image_file_path)
                old_height = old_image.height()
                old_weight = old_image.width()
                font_scaling = main_frame.normal_font.measure("A") / 11
                now_height = int(old_height * font_scaling)
                now_weight = int(old_weight * font_scaling)
                new_image = Image.open(image_file_path).resize((now_weight, now_height))
                image_data[image_file_name] = PhotoImage(new_image)
                # print(f"加载图片：{image_file_name}")
                # 如果图片的文件名中有_的话，则为差分图片，选取_的第一部分作为角色名
                if "_" in image_file_name:
                    character_name = image_file_name.split("_")[0]
                    if character_name not in image_data_index_by_chara:
                        image_data_index_by_chara[character_name] = []
                    image_data_index_by_chara[character_name].append(image_file_name)

load_images_from_directory(image_dir_path)