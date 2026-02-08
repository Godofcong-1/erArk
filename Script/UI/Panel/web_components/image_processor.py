# -*- coding: utf-8 -*-
"""
图片处理模块
负责处理Web模式下的角色立绘图片裁切和缓存

主要功能：
1. 自动裁切图片的透明边缘区域
2. LRU缓存机制（最多缓存10张图片）
3. 支持在保存存档时清理缓存
"""

import io
import os
from collections import OrderedDict
from typing import Optional, Tuple

# 尝试导入PIL，如果失败则设置为不可用
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[图片处理器] 警告: PIL/Pillow未安装，图片裁切功能将不可用")


class ImageProcessor:
    """
    图片处理器
    负责裁切图片透明区域并管理LRU缓存
    
    缓存机制：
    - 使用OrderedDict实现LRU缓存
    - 最大缓存数量为10张图片
    - 每次访问图片时更新其顺序为最新
    - 新增图片时，如果超过缓存上限则删除最旧的图片
    - 保存存档时清理所有缓存
    """
    
    # 最大缓存图片数量
    MAX_CACHE_SIZE = 10
    
    # 单例实例
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化图片处理器"""
        if self._initialized:
            return
        
        # LRU缓存：key=图片路径, value=(裁切后的图片字节数据, 原始尺寸, 裁切后尺寸, 裁切偏移量)
        # 使用OrderedDict来维护访问顺序
        self._cache: OrderedDict[str, Tuple[bytes, Tuple[int, int], Tuple[int, int], Tuple[int, int]]] = OrderedDict()
        
        self._initialized = True
        print(f"[图片处理器] 初始化完成, PIL可用: {PIL_AVAILABLE}, 最大缓存: {self.MAX_CACHE_SIZE}张")
    
    def get_cropped_image(self, image_path: str) -> Optional[Tuple[bytes, dict]]:
        """
        获取裁切透明区域后的图片
        
        Keyword arguments:
        image_path -- 原始图片的完整路径
        
        Returns:
        Tuple[bytes, dict] | None -- (裁切后的图片字节数据, 元数据字典) 或 None（如果处理失败）
        元数据字典包含：
            - original_width: 原始图片宽度
            - original_height: 原始图片高度
            - cropped_width: 裁切后图片宽度
            - cropped_height: 裁切后图片高度
            - offset_x: 裁切区域相对于原图左上角的X偏移
            - offset_y: 裁切区域相对于原图左上角的Y偏移
        """
        if not PIL_AVAILABLE:
            return None
        
        # 规范化路径
        normalized_path = os.path.normpath(image_path)
        
        # 检查缓存
        if normalized_path in self._cache:
            # 更新访问顺序（移到末尾表示最近使用）
            self._cache.move_to_end(normalized_path)
            cached_data = self._cache[normalized_path]
            image_bytes, original_size, cropped_size, offset = cached_data
            metadata = {
                "original_width": original_size[0],
                "original_height": original_size[1],
                "cropped_width": cropped_size[0],
                "cropped_height": cropped_size[1],
                "offset_x": offset[0],
                "offset_y": offset[1],
            }
            # 缓存命中时不打印日志，减少控制台输出
            # print(f"[图片处理器] 缓存命中: {os.path.basename(normalized_path)}")
            return image_bytes, metadata
        
        # 缓存未命中，进行裁切处理
        result = self._crop_and_cache(normalized_path)
        return result
    
    def _crop_and_cache(self, image_path: str) -> Optional[Tuple[bytes, dict]]:
        """
        裁切图片并加入缓存
        
        Keyword arguments:
        image_path -- 图片的完整路径
        
        Returns:
        Tuple[bytes, dict] | None -- (裁切后的图片字节数据, 元数据字典) 或 None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"[图片处理器] 文件不存在: {image_path}")
                return None
            
            # 打开图片
            with Image.open(image_path) as img:
                # 记录原始尺寸
                original_size = img.size
                
                # 确保图片有alpha通道
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 获取透明区域的边界框
                bbox = self._get_non_transparent_bbox(img)
                
                if bbox is None:
                    # 整张图都是透明的，返回原图
                    print(f"[图片处理器] 图片完全透明: {os.path.basename(image_path)}")
                    bbox = (0, 0, img.width, img.height)
                
                # 计算偏移量（裁切区域左上角相对于原图左上角的位置）
                offset = (bbox[0], bbox[1])
                
                # 裁切图片
                cropped_img = img.crop(bbox)
                cropped_size = cropped_img.size
                
                # 将裁切后的图片转换为PNG字节数据
                buffer = io.BytesIO()
                cropped_img.save(buffer, format='PNG', optimize=True)
                image_bytes = buffer.getvalue()
                
                # 添加到缓存
                self._add_to_cache(image_path, image_bytes, original_size, cropped_size, offset)
                
                # 构建元数据
                metadata = {
                    "original_width": original_size[0],
                    "original_height": original_size[1],
                    "cropped_width": cropped_size[0],
                    "cropped_height": cropped_size[1],
                    "offset_x": offset[0],
                    "offset_y": offset[1],
                }
                
                print(f"[图片处理器] 裁切完成: {os.path.basename(image_path)}, "
                      f"原始: {original_size}, 裁切后: {cropped_size}, 偏移: {offset}")
                
                return image_bytes, metadata
                
        except Exception as e:
            print(f"[图片处理器] 处理图片失败: {image_path}, 错误: {e}")
            return None
    
    def _get_non_transparent_bbox(self, img: 'Image.Image') -> Optional[Tuple[int, int, int, int]]:
        """
        获取图片中非透明区域的边界框
        
        Keyword arguments:
        img -- PIL Image对象（必须为RGBA模式）
        
        Returns:
        Tuple[int, int, int, int] | None -- (left, top, right, bottom) 边界框坐标，
                                            如果图片完全透明则返回None
        """
        # 获取alpha通道
        alpha = img.split()[3]
        
        # 获取非透明像素的边界框
        # getbbox() 返回非零像素的边界框 (left, top, right, bottom)
        bbox = alpha.getbbox()
        
        return bbox
    
    def _add_to_cache(self, path: str, image_bytes: bytes, 
                      original_size: Tuple[int, int], 
                      cropped_size: Tuple[int, int],
                      offset: Tuple[int, int]):
        """
        将图片添加到缓存中
        
        Keyword arguments:
        path -- 图片路径（作为缓存key）
        image_bytes -- 裁切后的图片字节数据
        original_size -- 原始图片尺寸 (width, height)
        cropped_size -- 裁切后图片尺寸 (width, height)
        offset -- 裁切区域偏移量 (x, y)
        """
        # 如果缓存已满，删除最旧的项目（OrderedDict的第一个元素）
        while len(self._cache) >= self.MAX_CACHE_SIZE:
            oldest_key, _ = self._cache.popitem(last=False)
            print(f"[图片处理器] 缓存已满，移除最旧: {os.path.basename(oldest_key)}")
        
        # 添加新项目到缓存末尾
        self._cache[path] = (image_bytes, original_size, cropped_size, offset)
        print(f"[图片处理器] 已缓存: {os.path.basename(path)}, 当前缓存数: {len(self._cache)}/{self.MAX_CACHE_SIZE}")
    
    def clear_cache(self):
        """
        清空所有缓存
        用于保存存档时调用
        """
        cache_count = len(self._cache)
        self._cache.clear()
        print(f"[图片处理器] 缓存已清空，共清理 {cache_count} 张图片")
    
    def get_cache_info(self) -> dict:
        """
        获取缓存状态信息
        
        Returns:
        dict -- 包含缓存信息的字典
        """
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.MAX_CACHE_SIZE,
            "cached_images": [os.path.basename(path) for path in self._cache.keys()],
            "pil_available": PIL_AVAILABLE,
        }
    
    def is_available(self) -> bool:
        """
        检查图片处理功能是否可用
        
        Returns:
        bool -- PIL是否可用
        """
        return PIL_AVAILABLE


# 全局单例实例
image_processor = ImageProcessor()


def get_cropped_image(image_path: str) -> Optional[Tuple[bytes, dict]]:
    """
    便捷函数：获取裁切后的图片
    
    Keyword arguments:
    image_path -- 图片路径
    
    Returns:
    Tuple[bytes, dict] | None -- (图片字节数据, 元数据) 或 None
    """
    return image_processor.get_cropped_image(image_path)


def clear_image_cache():
    """
    便捷函数：清空图片缓存
    """
    image_processor.clear_cache()


def is_image_processor_available() -> bool:
    """
    便捷函数：检查图片处理功能是否可用
    
    Returns:
    bool -- 是否可用
    """
    return image_processor.is_available()
