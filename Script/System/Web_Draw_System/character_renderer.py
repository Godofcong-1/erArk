# -*- coding: utf-8 -*-
"""
角色图像渲染组件
负责处理Web模式下的角色立绘显示和图层合成
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from Script.Core import cache_control, game_type
from Script.Config import game_config
from Script.System.Web_Draw_System.body_part_button import BodyPartButton
from Script.System.Instruct_System.instruct_category import CLICKABLE_BODY_PARTS

cache: game_type.Cache = cache_control.cache


class CharacterRenderer:
    """
    角色图像渲染器
    负责获取角色立绘路径和身体部位位置数据
    """

    # 立绘目录（按优先级顺序）
    PORTRAIT_DIR = "image/立绘/干员/"
    SPECIAL_NPC_DIR = "image/立绘/特殊NPC/"
    # 默认立绘目录（对于没有差分的角色）
    DEFAULT_PORTRAIT_DIR = "image/立绘/干员"

    def __init__(self):
        """初始化角色渲染器"""
        self._body_parts_cache: Dict[int, dict] = {}
        self._image_path_cache: Dict[int, dict] = {}

    def get_character_image_data(self, character_id: int) -> dict:
        """
        获取角色图像数据
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        dict -- 包含角色图像各图层路径和部位位置数据的字典
               如果没有交互对象（character_id <= 0），返回空字典
        
        说明：
        当 character_id == 0 时，表示玩家没有交互对象（交互对象是自己）
        当 character_id > 0 时，表示有交互对象
        当 character_id < 0 时，表示无效
        """
        # 当没有交互对象时，返回空字典
        if character_id <= 0:
            return {}
        
        # 尝试使用缓存
        if character_id in self._image_path_cache:
            return self._image_path_cache[character_id]
        
        character_data: game_type.Character = cache.character_data[character_id]
        if not character_data:
            return self._get_empty_image_data()
        
        character_name = character_data.name
        
        # 检测角色是否有兽耳和兽角特征（用于部位显示判断）
        # talent[111] = 兽耳, talent[112] = 兽角
        # 兽耳作为独立部位显示，需满足交互对象有兽耳的前提才会显示
        has_beast_ears = character_data.talent.get(111, 0) == 1 if hasattr(character_data, 'talent') else False
        has_horn = character_data.talent.get(112, 0) == 1 if hasattr(character_data, 'talent') else False
        
        # 构建图像数据
        image_data = {
            "character_id": character_id,
            "character_name": character_name,
            "full_body_image": self._find_full_body_image(character_name),
            "half_body_image": self._find_half_body_image(character_name),
            "head_image": self._find_head_image(character_name),
            "body_parts": self._load_body_parts_data(character_name, has_beast_ears),
            "clothing_layers": [],  # 服装图层（待扩展）
            "effect_layers": [],    # 特效图层（待扩展）
            "has_beast_ears": has_beast_ears,  # 角色是否有兽耳（用于兽耳部位显示）
            "has_horn": has_horn,              # 角色是否有兽角（用于头部子部位显示）
        }
        
        # 缓存结果
        self._image_path_cache[character_id] = image_data
        
        return image_data

    def _get_empty_image_data(self) -> dict:
        """
        获取空的图像数据结构
        
        Returns:
        dict -- 空的图像数据字典
        """
        return {
            "character_id": -1,
            "character_name": "",
            "full_body_image": "",
            "half_body_image": "",
            "head_image": "",
            "body_parts": {},
            "clothing_layers": [],
            "effect_layers": [],
            "has_beast_ears": False,
            "has_horn": False,
        }

    def _find_full_body_image(self, character_name: str) -> str:
        """
        查找角色全身立绘
        
        Keyword arguments:
        character_name -- 角色名称
        
        Returns:
        str -- 全身立绘路径
        """
        # 优先查找干员目录下的全身图
        full_body_path = f"{self.PORTRAIT_DIR}/{character_name}/{character_name}_全身.png"
        if os.path.exists(full_body_path):
            return full_body_path
        
        # 查找特殊NPC目录下的全身图
        full_body_path = f"{self.SPECIAL_NPC_DIR}/{character_name}/{character_name}_全身.png"
        if os.path.exists(full_body_path):
            return full_body_path
        
        # 如果没有全身图，暂时使用半身图作为替代
        return self._find_half_body_image(character_name)

    def _find_half_body_image(self, character_name: str) -> str:
        """
        查找角色半身立绘
        
        Keyword arguments:
        character_name -- 角色名称
        
        Returns:
        str -- 半身立绘路径
        """
        # 优先查找干员目录下的半身图
        half_body_path = f"{self.PORTRAIT_DIR}/{character_name}/{character_name}_半身.png"
        if os.path.exists(half_body_path):
            return half_body_path
        
        # 查找干员目录下不含下划线的原始图片
        char_dir = f"{self.PORTRAIT_DIR}/{character_name}"
        if os.path.exists(char_dir):
            for filename in os.listdir(char_dir):
                if filename.endswith('.png') and '_' not in filename:
                    return f"{char_dir}/{filename}"
        
        # 查找特殊NPC目录下的半身图
        half_body_path = f"{self.SPECIAL_NPC_DIR}/{character_name}/{character_name}_半身.png"
        if os.path.exists(half_body_path):
            return half_body_path
        
        # 查找特殊NPC目录下不含下划线的原始图片
        char_dir = f"{self.SPECIAL_NPC_DIR}/{character_name}"
        if os.path.exists(char_dir):
            for filename in os.listdir(char_dir):
                if filename.endswith('.png') and '_' not in filename:
                    return f"{char_dir}/{filename}"
        
        # 查找默认立绘目录
        default_path = f"{self.DEFAULT_PORTRAIT_DIR}/{character_name}.png"
        if os.path.exists(default_path):
            return default_path
        
        return ""

    def _find_head_image(self, character_name: str) -> str:
        """
        查找角色头部图片
        
        Keyword arguments:
        character_name -- 角色名称
        
        Returns:
        str -- 头部图片路径
        """
        # 优先查找干员目录
        head_path = f"{self.PORTRAIT_DIR}/{character_name}/{character_name}_头部.png"
        if os.path.exists(head_path):
            return head_path
        
        # 查找特殊NPC目录
        head_path = f"{self.SPECIAL_NPC_DIR}/{character_name}/{character_name}_头部.png"
        if os.path.exists(head_path):
            return head_path
        
        return ""
    
    def _get_nose_position(self, character_name: str) -> tuple:
        """
        获取角色的鼻子位置（归一化坐标）
        
        Keyword arguments:
        character_name -- 角色名称
        
        Returns:
        tuple -- (nose_x, nose_y) 归一化坐标，如果找不到则返回 (0.5, 0.25) 作为默认值
        """
        # 尝试加载 body.json 文件
        json_path = f"{self.PORTRAIT_DIR}/{character_name}/{character_name}_body.json"
        if not os.path.exists(json_path):
            json_path = f"{self.SPECIAL_NPC_DIR}/{character_name}/{character_name}_body.json"
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    landmarks = raw_data.get("landmarks", [])
                    for lm in landmarks:
                        if lm.get("name") == "nose":
                            return (lm.get("x", 0.5), lm.get("y", 0.25))
            except (json.JSONDecodeError, IOError):
                pass
        
        # 默认位置：假设鼻子大约在图像中心偏左、上方1/4处
        return (0.5, 0.25)
    
    def get_avatar_info(self, character_name: str) -> dict:
        """
        获取角色头像信息
        
        优先使用现成的头像文件，如果没有则返回截取信息
        
        Keyword arguments:
        character_name -- 角色名称
        
        Returns:
        dict -- 头像信息字典，包含：
            - has_avatar_file: 是否有现成头像文件
            - avatar_path: 头像文件路径（如果有）
            - full_body_path: 全身图路径（用于截取）
            - nose_x: 鼻子X坐标（归一化）
            - nose_y: 鼻子Y坐标（归一化）
            - need_crop: 是否需要从全身图截取
        """
        result = {
            "has_avatar_file": False,
            "avatar_path": "",
            "full_body_path": "",
            "nose_x": 0.5,
            "nose_y": 0.25,
            "need_crop": False
        }
        
        # 先检查是否有现成的头像文件
        head_path = self._find_head_image(character_name)
        if head_path:
            result["has_avatar_file"] = True
            result["avatar_path"] = head_path
            return result
        
        # 没有现成头像，尝试获取全身图和鼻子位置
        full_body_path = self._find_full_body_image(character_name)
        if full_body_path and os.path.exists(full_body_path):
            nose_x, nose_y = self._get_nose_position(character_name)
            result["full_body_path"] = full_body_path
            result["nose_x"] = nose_x
            result["nose_y"] = nose_y
            result["need_crop"] = True
        
        return result

    def _load_body_parts_data(self, character_name: str, has_beast_ears: bool = False) -> dict:
        """
        加载角色的身体部位位置数据
        
        Keyword arguments:
        character_name -- 角色名称
        has_beast_ears -- 角色是否有兽耳（用于条件部位显示）
        
        Returns:
        dict -- 身体部位位置数据
        """
        # 优先尝试加载干员目录下的 {角色名}_body.json 文件（COCO-WholeBody格式）
        json_path = f"{self.PORTRAIT_DIR}/{character_name}/{character_name}_body.json"
        if not os.path.exists(json_path):
            # 尝试干员目录旧格式 body_parts.json
            json_path = f"{self.PORTRAIT_DIR}/{character_name}/body_parts.json"
        
        if not os.path.exists(json_path):
            # 尝试特殊NPC目录下的 {角色名}_body.json
            json_path = f"{self.SPECIAL_NPC_DIR}/{character_name}/{character_name}_body.json"
        
        if not os.path.exists(json_path):
            # 尝试特殊NPC目录旧格式 body_parts.json
            json_path = f"{self.SPECIAL_NPC_DIR}/{character_name}/body_parts.json"
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    return self._convert_body_data(raw_data, has_beast_ears)
            except (json.JSONDecodeError, IOError):
                pass
        
        # 返回默认的空数据结构
        return {
            "image_size": {"width": 0, "height": 0},
            "body_parts": {}
        }
    
    def _convert_body_data(self, raw_data: dict, has_beast_ears: bool = False) -> dict:
        """
        转换身体部位数据为前端需要的格式
        使用 BodyPartButton 类处理 COCO 关键点到游戏部位的映射
        
        Keyword arguments:
        raw_data -- 原始JSON数据
        has_beast_ears -- 角色是否有兽耳（用于条件部位显示）
        
        Returns:
        dict -- 转换后的身体部位数据，使用游戏的 BodyPart 系统
        """
        # 获取图像尺寸
        image_width = raw_data.get("image_width", 1024)
        image_height = raw_data.get("image_height", 1024)
        
        result = {
            "image_size": {"width": image_width, "height": image_height},
            "body_parts": {}
        }
        
        # 如果是 landmarks 格式（COCO-WholeBody）
        landmarks = raw_data.get("landmarks", [])
        if landmarks:
            # 使用 BodyPartButton 类处理 COCO 到游戏部位的转换
            body_part_button = BodyPartButton()
            
            # 将 landmarks 转换为 BodyPartButton 需要的格式
            # landmarks 格式: [{"name": "nose", "x": 0.5, "y": 0.3, "score": 0.9}, ...]
            # BodyPartButton 需要: [(x1, y1), (x2, y2), ...] 17个点（像素坐标）
            
            # COCO-WholeBody 17个关键点的顺序
            coco_keypoint_names = [
                "nose", "left_eye", "right_eye", "left_ear", "right_ear",
                "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                "left_wrist", "right_wrist", "left_hip", "right_hip",
                "left_knee", "right_knee", "left_ankle", "right_ankle"
            ]
            
            # 创建关键点映射
            landmark_map = {}
            for lm in landmarks:
                name = lm.get("name", "")
                if name and lm.get("score", 0) >= 0.5:  # 过滤低置信度点
                    # 转换归一化坐标到像素坐标
                    x = lm.get("x", 0) * image_width
                    y = lm.get("y", 0) * image_height
                    landmark_map[name] = (x, y)
            
            # 按 COCO 顺序构建关键点列表
            keypoints: List[Tuple[float, float]] = []
            for name in coco_keypoint_names:
                if name in landmark_map:
                    keypoints.append(landmark_map[name])
                else:
                    keypoints.append((0, 0))  # 无效点
            
            # 加载关键点并计算部位位置
            body_part_button.load_coco_keypoints(keypoints, (image_width, image_height))
            
            # 设置兽耳状态（用于头部子菜单和待功能扩展）
            body_part_button.set_has_beast_features(False, has_beast_ears)
            
            # 初始化可见部位（使用 CLICKABLE_BODY_PARTS，传入兽耳条件）
            body_part_button.set_visible_parts(CLICKABLE_BODY_PARTS, has_beast_ears)
            
            # 获取部位按钮数据
            buttons_data = body_part_button.get_buttons_data()
            
            # 转换为前端需要的格式
            for btn in buttons_data:
                part_name = btn["part_name"]        # 英文部位名（如 "face" 或 "hand_left"）
                display_name = btn["display_name"]  # 中文显示名（如 "脸部" 或 "左手部"）
                center = btn["center"]              # [x, y] 像素坐标
                radius = btn["radius"]              # 点击半径
                base_part = btn.get("base_part", part_name)  # 基础部位名（如 "hand"）
                
                result["body_parts"][display_name] = {
                    "center": {
                        "x": int(center[0]),
                        "y": int(center[1])
                    },
                    "radius": int(radius),
                    "part_id": part_name,      # 完整ID供后端使用
                    "base_part": base_part,    # 基础部位名，用于指令匹配
                    "is_hip_sub_part": btn.get("is_hip_sub_part", False)
                }
        
        # 如果已经是 body_parts 格式，直接返回
        elif "body_parts" in raw_data:
            result["body_parts"] = raw_data["body_parts"]
            if "image_size" in raw_data:
                result["image_size"] = raw_data["image_size"]
        
        return result

    def get_scene_characters_avatars(self, exclude_ids: List[int] = []) -> List[dict]:
        """
        获取场景内所有角色的头像信息（除指定排除的角色外）
        
        Keyword arguments:
        exclude_ids -- 要排除的角色ID列表
        
        Returns:
        List[dict] -- 角色头像信息列表，每个元素包含：
            - id: 角色ID
            - name: 角色名称
            - avatar: 头像文件路径（如果有现成文件）
            - has_dialog: 是否有待显示的对话
            - avatar_info: 头像详细信息（用于动态截取）
                - has_avatar_file: 是否有现成头像文件
                - avatar_path: 头像文件路径
                - full_body_path: 全身图路径
                - nose_x, nose_y: 鼻子位置（归一化坐标）
                - need_crop: 是否需要截取
        """
        if exclude_ids is None:
            exclude_ids = []
        
        avatars = []
        try:
            pl_character_data: game_type.Character = cache.character_data[0]
            from Script.Design import map_handle
            scene_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
            scene_data: game_type.Scene = cache.scene_data[scene_path_str]
            
            if scene_data:
                for char_id in scene_data.character_list:
                    if char_id in exclude_ids:
                        continue
                    char_data = cache.character_data.get(char_id)
                    if char_data:
                        # 获取头像信息
                        avatar_info = self.get_avatar_info(char_data.name)
                        avatars.append({
                            "id": char_id,
                            "name": char_data.name,
                            "avatar": avatar_info.get("avatar_path", ""),
                            "has_dialog": False,  # 结算时更新
                            "avatar_info": avatar_info
                        })
        except (KeyError, AttributeError):
            pass
        
        return avatars

    def clear_cache(self):
        """清除缓存"""
        self._body_parts_cache.clear()
        self._image_path_cache.clear()
