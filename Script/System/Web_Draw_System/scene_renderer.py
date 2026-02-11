# -*- coding: utf-8 -*-
"""
场景背景渲染组件
负责处理Web模式下的场景背景图片显示
"""

import os
from Script.Core import cache_control, game_type
from Script.Design import map_handle

cache: game_type.Cache = cache_control.cache


class SceneRenderer:
    """
    场景背景渲染器
    负责获取和处理场景背景图片路径
    """

    # 默认背景图
    DEFAULT_BACKGROUND = "宿舍_白天"
    # 背景图片目录
    BACKGROUND_DIR = "image/场景"

    def __init__(self):
        """初始化场景渲染器"""
        self._cached_scene_name = None
        self._cached_background_path = None

    def get_scene_background(self, scene_name: str = "") -> dict:
        """
        获取场景背景信息
        
        Keyword arguments:
        scene_name -- 场景名称，为空时自动获取当前场景
        
        Returns:
        dict -- 包含场景名称和背景图片路径的字典
        """
        # 如果没有指定场景名，获取当前场景
        if scene_name == "":
            scene_name = self._get_current_scene_name()
        
        # 尝试使用缓存
        if scene_name == self._cached_scene_name and self._cached_background_path:
            return {
                "name": scene_name,
                "background_image": self._cached_background_path
            }
        
        # 查找背景图片
        background_path = self._find_background_image(scene_name)
        
        # 更新缓存
        self._cached_scene_name = scene_name
        self._cached_background_path = background_path
        
        return {
            "name": scene_name,
            "background_image": background_path
        }

    def _get_current_scene_name(self) -> str:
        """
        获取当前场景名称
        
        Returns:
        str -- 当前场景名称
        """
        try:
            pl_character_data: game_type.Character = cache.character_data[0]
            scene_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]
            if scene_data.scene_img:
                return scene_data.scene_img
        except (KeyError, AttributeError):
            pass
        return self.DEFAULT_BACKGROUND

    def _find_background_image(self, scene_name: str) -> str:
        """
        查找场景背景图片路径
        
        Keyword arguments:
        scene_name -- 场景名称
        
        Returns:
        str -- 背景图片路径
        """
        # 尝试查找同名图片
        target_path = f"{self.BACKGROUND_DIR}/{scene_name}.png"
        if os.path.exists(target_path):
            return target_path
        
        # 使用默认背景
        default_path = f"{self.BACKGROUND_DIR}/{self.DEFAULT_BACKGROUND}.png"
        if os.path.exists(default_path):
            return default_path
        
        # 如果默认背景也不存在，返回空
        return ""

    def clear_cache(self):
        """清除缓存"""
        self._cached_scene_name = None
        self._cached_background_path = None
