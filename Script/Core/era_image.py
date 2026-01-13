import os
from PIL.ImageTk import PhotoImage
from PIL import Image
from Script.Core import main_frame, game_type, cache_control
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

image_data = {}
image_path_data = {} # 图片路径数据
image_data_index_by_chara = {}
image_text_data = {}
image_lock = 0
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
image_dir_path = os.path.join("image")

# 延迟加载相关
_images_loaded = False
_font_scaling = None
_image_load_lock = threading.Lock()
_pending_images = {}  # 存储待转换的PIL图像 {name: (pil_image, path)}

def _get_font_scaling():
    """
    获取字体缩放比例（缓存结果避免重复计算）
    """
    global _font_scaling
    if _font_scaling is None:
        _font_scaling = main_frame.normal_font.measure("A") / 11
    return _font_scaling

def _load_single_image(args):
    """
    加载单张图片（用于多线程）
    返回: (image_file_name, resized_pil_image, image_file_path, character_name) 或 None
    """
    root, file, font_scaling = args
    image_file_path = os.path.join(root, file)
    # 使用切片而不是rstrip，避免误删文件名中的字符
    # 例如 "panpan.png".rstrip(".png") 会变成 "panpa" 而不是 "panpan"
    image_file_name = file[:-4]  # 去掉 ".png" 4个字符
    
    try:
        # 只用PIL.Image加载一次
        with Image.open(image_file_path) as img:
            old_width, old_height = img.size
            now_width = int(old_width * font_scaling)
            now_height = int(old_height * font_scaling)
            
            # 使用BILINEAR，比LANCZOS快且质量可接受
            resized_img = img.resize((now_width, now_height), Image.Resampling.BILINEAR)
            # 需要复制，因为with块结束后img会关闭
            resized_img = resized_img.copy()
        
        # 提取角色名
        character_name = None
        if "_" in image_file_name:
            character_name = image_file_name.split("_")[0]
        
        return (image_file_name, resized_img, image_file_path, character_name)
        
    except Exception as e:
        print(f"  加载图片失败: {image_file_path} - {e}")
        return None

def get_image(image_name):
    """
    获取图片（延迟加载版本）
    如果图片尚未转换为PhotoImage，则在此时转换
    
    Keyword arguments:
    image_name -- 图片名称（不含扩展名）
    
    返回: PhotoImage 对象，如果不存在返回 None
    """
    global _pending_images
    
    # 使用dict的方法直接检查，避免触发__contains__
    if dict.__contains__(image_data, image_name):
        return dict.__getitem__(image_data, image_name)
    
    # 如果在待转换列表中，进行延迟转换
    with _image_load_lock:
        if image_name in _pending_images:
            pil_image, _ = _pending_images[image_name]
            try:
                photo_image = PhotoImage(pil_image)
                # 使用dict的方法直接设置，避免触发__setitem__
                dict.__setitem__(image_data, image_name, photo_image)
                del _pending_images[image_name]  # 释放PIL图像内存
                return photo_image
            except Exception as e:
                print(f"  转换图片失败: {image_name} - {e}")
                return None
    
    return None

def load_images_from_directory(directory):
    """
    从目录加载所有图片（延迟加载优化版本）
    
    优化点：
    1. 只用PIL.Image加载一次，避免重复加载
    2. 缓存font_scaling避免重复计算
    3. 使用多线程并行加载PIL图片
    4. 延迟转换PhotoImage：只在首次使用时转换
    5. 添加进度提示
    """
    import time
    global _images_loaded, _pending_images
    
    start_time = time.time()
    
    # 先收集所有png文件路径
    png_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                png_files.append((root, file))
    
    total_files = len(png_files)
    if total_files == 0:
        print("未找到任何图片文件")
        return
    
    # print(f"正在加载 {total_files} 张图片...")
    
    # 预先获取缩放比例
    font_scaling = _get_font_scaling()
    
    # 准备多线程参数
    args_list = [(root, file, font_scaling) for root, file in png_files]
    
    # 使用线程池并行加载PIL图片（IO密集型任务适合多线程）
    loaded_count = 0
    last_progress = 0
    
    # 根据CPU核心数决定线程数，但不超过16
    max_workers = min(16, (os.cpu_count() or 4) * 2)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_load_single_image, args): args for args in args_list}
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                image_file_name, resized_img, image_file_path, character_name = result
                
                # 存储待转换的PIL图像（延迟转换）
                _pending_images[image_file_name] = (resized_img, image_file_path)
                image_path_data[image_file_name] = image_file_path
                
                # 建立角色索引
                if character_name is not None:
                    if character_name not in image_data_index_by_chara:
                        image_data_index_by_chara[character_name] = []
                    image_data_index_by_chara[character_name].append(image_file_name)
            
            loaded_count += 1
            
            # 每10%记录并显示一次进度
            progress = (loaded_count * 100) // total_files
            if progress >= last_progress + 10:
                last_progress = progress
                # print(f"  加载进度: {progress}% ({loaded_count}/{total_files})")
    
    _images_loaded = True
    elapsed_time = time.time() - start_time
    print(f"图片预加载完成！共 {len(_pending_images)} 张，耗时 {elapsed_time:.2f} 秒")
    # print(f"  (图片将在首次使用时转换为显示格式)")


# 为了兼容现有代码，重写 image_data 的访问方式
class _LazyImageDict(dict):
    """
    延迟加载的图片字典
    当访问不存在的键时，尝试从_pending_images中转换
    """
    def __getitem__(self, key):
        # 先检查是否已在dict中（已转换过的）
        if super().__contains__(key):
            return super().__getitem__(key)
        
        # 尝试延迟加载（在_pending_images中但未转换的）
        img = get_image(key)
        if img is not None:
            return img
        
        raise KeyError(key)
    
    def __contains__(self, key):
        if super().__contains__(key):
            return True
        return key in _pending_images
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


# 替换原有的image_data字典
image_data = _LazyImageDict()

load_images_from_directory(image_dir_path)