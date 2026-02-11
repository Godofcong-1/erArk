# -*- coding: utf-8 -*-
"""
身体部位按钮组件
负责处理Web模式下角色立绘上的身体部位点击交互

基于 COCO-WholeBody 17个关键点和 BodyPart.csv 定义的部位进行映射：
- COCO关键点用于定位身体部位的像素位置
- BodyPart.csv 定义了可交互的部位列表
- 臀部点击时展开子部位：小穴、子宫、后穴、尿道、尾巴
- 头部点击时展开子部位：头发、兽角（需要角色有兽角）、兽耳（需要角色有兽耳）
"""

from typing import Dict, List, Optional, Tuple
from Script.System.Instruct_System.instruct_category import (
    BodyPart,
    BODY_PART_NAMES,
    HIP_SUB_PARTS,
    HEAD_SUB_PARTS,
    COCO_KEYPOINT_MAPPING,
    COMPUTED_BODY_PARTS,
    CLICKABLE_BODY_PARTS,
)


class BodyPartButton:
    """
    身体部位按钮管理器
    负责管理角色立绘上的部位按钮数据
    
    支持功能：
    1. 基于COCO-WholeBody 17个关键点计算部位位置
    2. 合并左右对称的部位（如左右手、左右腿）
    3. 臀部点击展开子部位菜单
    4. 头部点击展开子部位菜单（头发、兽角、兽耳）
    """

    def __init__(self):
        """初始化身体部位按钮管理器"""
        # 原始的COCO关键点数据 (17个点)
        self._coco_keypoints: List[Tuple[float, float]] = []
        # 计算后的部位位置数据
        self._body_parts_data: Dict[str, dict] = {}
        # 当前可见的部位列表
        self._visible_parts: List[str] = []
        # 当前悬停的部位
        self._hovered_part: Optional[str] = None
        # 臀部是否展开
        self._hip_expanded: bool = False
        # 头部是否展开
        self._head_expanded: bool = False
        # 角色是否有兽耳
        self._has_beast_ears: bool = False
        # 角色是否有兽角
        self._has_horn: bool = False
        # 图像尺寸
        self._image_size: Tuple[int, int] = (0, 0)

    def load_coco_keypoints(self, keypoints: List[Tuple[float, float]], image_size: Tuple[int, int]):
        """
        从COCO-WholeBody格式的关键点数据加载
        
        Keyword arguments:
        keypoints -- COCO关键点列表，格式为 [(x1, y1), (x2, y2), ...] 共17个点
                    点的顺序: 0-鼻子, 1-左眼, 2-右眼, 3-左耳, 4-右耳, 5-左肩, 6-右肩,
                             7-左肘, 8-右肘, 9-左手腕, 10-右手腕, 11-左胯, 12-右胯,
                             13-左膝, 14-右膝, 15-左脚踝, 16-右脚踝
        image_size -- 图像尺寸 (width, height)
        """
        self._coco_keypoints = keypoints
        self._image_size = image_size
        self._calculate_body_parts()

    def _calculate_body_parts(self):
        """
        根据COCO关键点计算所有身体部位的位置
        成对的部位（手、腿、脚、腋、耳）分开显示为左右两个按钮
        """
        if len(self._coco_keypoints) < 17:
            return
        
        width, height = self._image_size
        self._body_parts_data = {}
        
        # 定义成对部位的映射：部位基础名 -> [(左关键点索引, 左后缀), (右关键点索引, 右后缀)]
        paired_parts = {
            BodyPart.HAND: [(9, "_left"), (10, "_right")],      # 左手腕、右手腕
            BodyPart.LEG: [(13, "_left"), (14, "_right")],      # 左膝、右膝
            BodyPart.FOOT: [(15, "_left"), (16, "_right")],     # 左脚踝、右脚踝
            BodyPart.ARMPIT: [(5, "_left"), (6, "_right")],     # 左肩、右肩
            BodyPart.BEAST_EARS: [(3, "_left"), (4, "_right")], # 左耳、右耳
        }
        
        # 1. 处理成对部位 - 分开显示为左右两个按钮
        for part_name, pairs in paired_parts.items():
            for kp_idx, suffix in pairs:
                kp = self._coco_keypoints[kp_idx]
                if kp[0] == 0 and kp[1] == 0:
                    continue  # 无效点
                
                part_key = f"{part_name}{suffix}"
                self._body_parts_data[part_key] = {
                    "center": list(kp),
                    "radius": self._get_default_radius(part_name, width, height),
                    "base_part": part_name,  # 记录基础部位名，用于交互逻辑
                }
        
        # 2. 处理单一部位（脸部、头部、口腔基于不同的关键点计算）
        # 脸部：基于鼻子位置，半径为到最近耳朵的距离
        nose = self._coco_keypoints[0]  # 鼻子
        left_eye = self._coco_keypoints[1]  # 左眼
        right_eye = self._coco_keypoints[2]  # 右眼
        left_ear = self._coco_keypoints[3]  # 左耳
        right_ear = self._coco_keypoints[4]  # 右耳
        
        if nose[0] != 0 or nose[1] != 0:
            # 计算到左右耳的距离，取较近的
            face_radius = self._get_default_radius(BodyPart.FACE, width, height)
            
            if (left_ear[0] != 0 or left_ear[1] != 0) and (right_ear[0] != 0 or right_ear[1] != 0):
                # 两只耳朵都有效，取较近的距离
                dist_left = ((nose[0] - left_ear[0]) ** 2 + (nose[1] - left_ear[1]) ** 2) ** 0.5
                dist_right = ((nose[0] - right_ear[0]) ** 2 + (nose[1] - right_ear[1]) ** 2) ** 0.5
                face_radius = int(min(dist_left, dist_right))
            elif left_ear[0] != 0 or left_ear[1] != 0:
                face_radius = int(((nose[0] - left_ear[0]) ** 2 + (nose[1] - left_ear[1]) ** 2) ** 0.5)
            elif right_ear[0] != 0 or right_ear[1] != 0:
                face_radius = int(((nose[0] - right_ear[0]) ** 2 + (nose[1] - right_ear[1]) ** 2) ** 0.5)
            
            self._body_parts_data[BodyPart.FACE] = {
                "center": list(nose),
                "radius": face_radius,
            }
            
            # 口腔：基于鼻子向下偏移
            mouth_offset = 0.03 * height
            self._body_parts_data[BodyPart.MOUTH] = {
                "center": [nose[0], nose[1] + mouth_offset],
                "radius": self._get_default_radius(BodyPart.MOUTH, width, height),
            }
        
        # 头部：使用双眼中间偏上一点的位置
        # 检查双眼是否有效
        left_eye_valid = left_eye[0] != 0 or left_eye[1] != 0
        right_eye_valid = right_eye[0] != 0 or right_eye[1] != 0
        
        if left_eye_valid and right_eye_valid:
            # 双眼中间
            eyes_center_x = (left_eye[0] + right_eye[0]) / 2
            eyes_center_y = (left_eye[1] + right_eye[1]) / 2
            # 向上偏移一点（图像高度的3%）
            head_center_y = eyes_center_y - 0.03 * height
            head_center = [eyes_center_x, head_center_y]
            head_radius = self._get_default_radius(BodyPart.HEAD, width, height)
        elif left_eye_valid:
            head_center = [left_eye[0], left_eye[1] - 0.03 * height]
            head_radius = self._get_default_radius(BodyPart.HEAD, width, height)
        elif right_eye_valid:
            head_center = [right_eye[0], right_eye[1] - 0.03 * height]
            head_radius = self._get_default_radius(BodyPart.HEAD, width, height)
        elif nose[0] != 0 or nose[1] != 0:
            # 回退到鼻子位置
            head_center = [nose[0], nose[1] - 0.15 * height]
            head_radius = self._get_default_radius(BodyPart.HEAD, width, height)
        else:
            head_center = None
            head_radius = 0
        
        if head_center:
            self._body_parts_data[BodyPart.HEAD] = {
                "center": head_center,
                "radius": head_radius,
            }
        
        # 3. 处理需要计算中心的部位（使用 COMPUTED_BODY_PARTS 但排除已处理的）
        for part_name, config in COMPUTED_BODY_PARTS.items():
            # 跳过已处理的部位
            if part_name in [BodyPart.HEAD, BodyPart.FACE, BodyPart.MOUTH, BodyPart.HAIR]:
                continue
            
            kp_indices = config["keypoints"]
            offset = config["offset"]
            
            # 计算关键点的中心
            valid_points = []
            for idx in kp_indices:
                if idx < len(self._coco_keypoints):
                    kp = self._coco_keypoints[idx]
                    if kp[0] != 0 or kp[1] != 0:
                        valid_points.append(kp)
            
            if not valid_points:
                continue
            
            center_x = sum(p[0] for p in valid_points) / len(valid_points)
            center_y = sum(p[1] for p in valid_points) / len(valid_points)
            
            # 应用偏移
            center_x += offset[0] * width
            center_y += offset[1] * height
            
            self._body_parts_data[part_name] = {
                "center": [center_x, center_y],
                "radius": self._get_default_radius(part_name, width, height)
            }
        
        # 4. 处理臀部（需要合并左右胯）
        left_hip = self._coco_keypoints[11]
        right_hip = self._coco_keypoints[12]
        if (left_hip[0] != 0 or left_hip[1] != 0) or (right_hip[0] != 0 or right_hip[1] != 0):
            if left_hip[0] != 0 and right_hip[0] != 0:
                hip_center = [(left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2]
            elif left_hip[0] != 0:
                hip_center = list(left_hip)
            else:
                hip_center = list(right_hip)
            
            self._body_parts_data[BodyPart.HIP] = {
                "center": hip_center,
                "radius": self._get_default_radius(BodyPart.HIP, width, height)
            }
            
            # 计算臀部子部位的位置（环绕臀部中心）
            self._calculate_hip_sub_parts(hip_center, width, height)

    def _get_default_radius(self, part_name: str, width: int, height: int) -> int:
        """
        获取部位的默认点击半径
        
        Keyword arguments:
        part_name -- 部位名称
        width -- 图像宽度
        height -- 图像高度
        
        Returns:
        int -- 点击半径（像素）
        """
        base_size = min(width, height)
        
        # 根据部位设置不同的半径
        radius_map = {
            BodyPart.HEAD: 0.06,
            BodyPart.HAIR: 0.05,
            BodyPart.FACE: 0.05,
            BodyPart.MOUTH: 0.025,
            BodyPart.BEAST_EARS: 0.03,
            BodyPart.HORN: 0.025,
            BodyPart.CHEST: 0.06,
            BodyPart.ARMPIT: 0.03,
            BodyPart.HAND: 0.035,
            BodyPart.BELLY: 0.05,
            BodyPart.HIP: 0.06,
            BodyPart.CROTCH: 0.04,
            BodyPart.LEG: 0.04,
            BodyPart.FOOT: 0.03,
        }
        
        ratio = radius_map.get(part_name, 0.04)
        return int(base_size * ratio)

    def _calculate_hip_sub_parts(self, hip_center: List[float], width: int, height: int):
        """
        计算臀部子部位的位置（环绕臀部中心排列）
        
        Keyword arguments:
        hip_center -- 臀部中心位置 [x, y]
        width -- 图像宽度
        height -- 图像高度
        """
        import math
        
        sub_parts = HIP_SUB_PARTS
        num_parts = len(sub_parts)
        base_radius = min(width, height) * 0.08  # 子部位环绕的半径
        part_radius = min(width, height) * 0.025  # 子部位的点击半径
        
        for i, part_name in enumerate(sub_parts):
            # 按扇形排列
            angle = math.pi / 2 + (i - (num_parts - 1) / 2) * (math.pi / 4)
            offset_x = base_radius * math.cos(angle)
            offset_y = base_radius * math.sin(angle)
            
            self._body_parts_data[part_name] = {
                "center": [hip_center[0] + offset_x, hip_center[1] + offset_y],
                "radius": int(part_radius),
                "is_hip_sub_part": True
            }

    def load_body_parts(self, body_parts_json: dict):
        """
        从JSON格式加载身体部位数据（兼容旧格式）
        
        Keyword arguments:
        body_parts_json -- 身体部位JSON数据
        """
        if "keypoints" in body_parts_json:
            # 新格式：包含COCO关键点
            keypoints = body_parts_json["keypoints"]
            image_size = body_parts_json.get("image_size", {})
            self._image_size = (image_size.get("width", 0), image_size.get("height", 0))
            self.load_coco_keypoints(keypoints, self._image_size)
        else:
            # 旧格式：直接是部位位置数据
            self._image_size = (
                body_parts_json.get("image_size", {}).get("width", 0),
                body_parts_json.get("image_size", {}).get("height", 0)
            )
            self._body_parts_data = body_parts_json.get("body_parts", {})

    def set_visible_parts(self, parts: List[str]):
        """
        设置可见的部位
        会自动将成对部位展开为左右两个
        
        Keyword arguments:
        parts -- 要显示的部位名称列表（基础部位名，如 "hand" 而非 "hand_left"）
        """
        # 成对部位列表
        paired_part_names = [BodyPart.HAND, BodyPart.LEG, BodyPart.FOOT, BodyPart.ARMPIT, BodyPart.BEAST_EARS]
        
        expanded_parts = []
        for part in parts:
            if part in paired_part_names:
                # 成对部位展开为左右两个
                left_key = f"{part}_left"
                right_key = f"{part}_right"
                if left_key in self._body_parts_data:
                    expanded_parts.append(left_key)
                if right_key in self._body_parts_data:
                    expanded_parts.append(right_key)
            else:
                # 非成对部位直接添加
                if part in self._body_parts_data:
                    expanded_parts.append(part)
        
        self._visible_parts = expanded_parts

    def get_visible_parts(self) -> List[str]:
        """
        获取当前可见的部位列表
        
        Returns:
        List[str] -- 可见部位名称列表
        """
        return self._visible_parts

    def set_default_visible_parts(self):
        """
        设置默认的可见部位列表（主要可点击部位）
        """
        self._visible_parts = [
            part for part in CLICKABLE_BODY_PARTS
            if part in self._body_parts_data
        ]

    def get_part_position(self, part_name: str) -> Optional[dict]:
        """
        获取部位的位置和大小信息
        
        Keyword arguments:
        part_name -- 部位名称
        
        Returns:
        dict -- 部位位置数据，包含center和radius
        """
        return self._body_parts_data.get(part_name)

    def get_part_display_name(self, part_name: str) -> str:
        """
        获取部位的中文显示名称
        
        Keyword arguments:
        part_name -- 部位英文名称（可能带 _left 或 _right 后缀）
        
        Returns:
        str -- 部位中文名称
        """
        # 处理成对部位的后缀
        if part_name.endswith("_left"):
            base_name = part_name[:-5]  # 去掉 "_left"
            base_display = BODY_PART_NAMES.get(base_name, base_name)
            return f"左{base_display}"
        elif part_name.endswith("_right"):
            base_name = part_name[:-6]  # 去掉 "_right"
            base_display = BODY_PART_NAMES.get(base_name, base_name)
            return f"右{base_display}"
        else:
            return BODY_PART_NAMES.get(part_name, part_name)

    def get_image_size(self) -> Tuple[int, int]:
        """
        获取图像尺寸
        
        Returns:
        Tuple[int, int] -- (宽度, 高度)
        """
        return self._image_size

    def expand_hip(self):
        """
        展开臀部子部位
        当点击臀部时调用，将子部位添加到可见列表
        """
        self._hip_expanded = True
        for sub_part in HIP_SUB_PARTS:
            if sub_part in self._body_parts_data and sub_part not in self._visible_parts:
                self._visible_parts.append(sub_part)

    def collapse_hip(self):
        """
        收起臀部子部位
        """
        self._hip_expanded = False
        for sub_part in HIP_SUB_PARTS:
            if sub_part in self._visible_parts:
                self._visible_parts.remove(sub_part)

    def is_hip_expanded(self) -> bool:
        """
        检查臀部是否展开
        
        Returns:
        bool -- 是否展开
        """
        return self._hip_expanded

    def is_hip_sub_part(self, part_name: str) -> bool:
        """
        检查是否是臀部子部位
        
        Keyword arguments:
        part_name -- 部位名称
        
        Returns:
        bool -- 是否是臀部子部位
        """
        return part_name in HIP_SUB_PARTS

    def expand_head(self, has_horn: bool = False, has_beast_ears: bool = False):
        """
        展开头部子部位
        当点击头部时调用，将满足条件的子部位添加到可见列表
        
        Keyword arguments:
        has_horn -- 角色是否有兽角
        has_beast_ears -- 角色是否有兽耳
        """
        self._head_expanded = True
        self._has_horn = has_horn
        self._has_beast_ears = has_beast_ears
        
        for sub_part in HEAD_SUB_PARTS:
            if sub_part in self._body_parts_data and sub_part not in self._visible_parts:
                # 头发始终显示
                if sub_part == BodyPart.HAIR:
                    self._visible_parts.append(sub_part)
                # 兽角需要角色有兽角特征
                elif sub_part == BodyPart.HORN and has_horn:
                    self._visible_parts.append(sub_part)
                # 兽耳需要角色有兽耳特征
                elif sub_part == BodyPart.BEAST_EARS and has_beast_ears:
                    self._visible_parts.append(sub_part)

    def collapse_head(self):
        """
        收起头部子部位
        """
        self._head_expanded = False
        for sub_part in HEAD_SUB_PARTS:
            if sub_part in self._visible_parts:
                self._visible_parts.remove(sub_part)

    def is_head_expanded(self) -> bool:
        """
        检查头部是否展开
        
        Returns:
        bool -- 是否展开
        """
        return self._head_expanded

    def is_head_sub_part(self, part_name: str) -> bool:
        """
        检查是否是头部子部位
        
        Keyword arguments:
        part_name -- 部位名称
        
        Returns:
        bool -- 是否是头部子部位
        """
        return part_name in HEAD_SUB_PARTS

    def set_has_beast_features(self, has_horn: bool, has_beast_ears: bool):
        """
        设置角色是否有兽类特征
        
        Keyword arguments:
        has_horn -- 是否有兽角
        has_beast_ears -- 是否有兽耳
        """
        self._has_horn = has_horn
        self._has_beast_ears = has_beast_ears

    def get_buttons_data(self) -> List[dict]:
        """
        获取所有可见部位按钮的渲染数据
        
        Returns:
        List[dict] -- 按钮渲染数据列表
        """
        buttons = []
        
        for part_name in self._visible_parts:
            position = self.get_part_position(part_name)
            if position:
                # 获取基础部位名（用于交互逻辑）
                base_part = position.get("base_part", part_name)
                buttons.append({
                    "part_name": part_name,
                    "display_name": self.get_part_display_name(part_name),
                    "center": position.get("center", [0, 0]),
                    "radius": position.get("radius", 30),
                    "is_hip_sub_part": position.get("is_hip_sub_part", False),
                    "is_head_sub_part": position.get("is_head_sub_part", False),
                    "base_part": base_part,  # 基础部位名，用于指令匹配
                })
        
        return buttons

    def set_hovered_part(self, part_name: Optional[str]):
        """
        设置当前悬停的部位
        
        Keyword arguments:
        part_name -- 部位名称，None表示没有悬停
        """
        self._hovered_part = part_name

    def get_hovered_part(self) -> Optional[str]:
        """
        获取当前悬停的部位
        
        Returns:
        str -- 当前悬停的部位名称
        """
        return self._hovered_part

    def check_click(self, x: int, y: int, scale: float = 1.0, offset_x: int = 0, offset_y: int = 0) -> Optional[str]:
        """
        检查点击位置是否命中某个部位
        
        Keyword arguments:
        x -- 点击的X坐标
        y -- 点击的Y坐标
        scale -- 图像缩放比例
        offset_x -- 图像X偏移
        offset_y -- 图像Y偏移
        
        Returns:
        str -- 命中的部位名称，None表示未命中
        """
        for part_name in self._visible_parts:
            position = self.get_part_position(part_name)
            if not position:
                continue
            
            center = position.get("center", [0, 0])
            radius = position.get("radius", 30)
            
            # 计算实际位置（考虑缩放和偏移）
            actual_x = center[0] * scale + offset_x
            actual_y = center[1] * scale + offset_y
            actual_radius = radius * scale
            
            # 检查是否在圆形区域内
            distance = ((x - actual_x) ** 2 + (y - actual_y) ** 2) ** 0.5
            if distance <= actual_radius:
                return part_name
        
        return None

    def handle_click(self, part_name: str) -> dict:
        """
        处理部位点击事件
        
        Keyword arguments:
        part_name -- 被点击的部位名称
        
        Returns:
        dict -- 处理结果，包含：
                - action: "expand_hip" | "expand_head" | "collapse_hip" | "collapse_head" | "select"
                - part_name: 实际选择的部位
                - sub_parts: 展开时的子部位列表
        """
        if part_name == BodyPart.HIP:
            if not self._hip_expanded:
                self.expand_hip()
                return {
                    "action": "expand_hip",
                    "part_name": part_name,
                    "sub_parts": [
                        {
                            "part_name": sp,
                            "display_name": self.get_part_display_name(sp)
                        }
                        for sp in HIP_SUB_PARTS
                        if sp in self._body_parts_data
                    ]
                }
            else:
                self.collapse_hip()
                return {
                    "action": "collapse_hip",
                    "part_name": part_name
                }
        elif part_name == BodyPart.HEAD:
            if not self._head_expanded:
                self.expand_head(self._has_horn, self._has_beast_ears)
                # 获取应显示的子部位
                visible_sub_parts = []
                for sp in HEAD_SUB_PARTS:
                    if sp == BodyPart.HAIR:
                        # 头发始终显示
                        visible_sub_parts.append(sp)
                    elif sp == BodyPart.HORN and self._has_horn:
                        # 兽角需要角色有兽角特征
                        visible_sub_parts.append(sp)
                    elif sp == BodyPart.BEAST_EARS and self._has_beast_ears:
                        # 兽耳需要角色有兽耳特征
                        visible_sub_parts.append(sp)
                return {
                    "action": "expand_head",
                    "part_name": part_name,
                    "sub_parts": [
                        {
                            "part_name": sp,
                            "display_name": self.get_part_display_name(sp)
                        }
                        for sp in visible_sub_parts
                        if sp in self._body_parts_data
                    ]
                }
            else:
                self.collapse_head()
                return {
                    "action": "collapse_head",
                    "part_name": part_name
                }
        else:
            # 如果点击了其他部位，收起臀部和头部
            if self._hip_expanded and not self.is_hip_sub_part(part_name):
                self.collapse_hip()
            if self._head_expanded and not self.is_head_sub_part(part_name):
                self.collapse_head()
            
            return {
                "action": "select",
                "part_name": part_name,
                "display_name": self.get_part_display_name(part_name)
            }

    def clear(self):
        """清除所有数据"""
        self._coco_keypoints = []
        self._body_parts_data = {}
        self._visible_parts = []
        self._hovered_part = None
        self._hip_expanded = False
        self._head_expanded = False
        self._has_horn = False
        self._has_beast_ears = False
        self._image_size = (0, 0)

    def get_state(self) -> dict:
        """
        获取部位按钮状态
        
        Returns:
        dict -- 部位按钮状态数据
        """
        return {
            "image_size": {"width": self._image_size[0], "height": self._image_size[1]},
            "buttons": self.get_buttons_data(),
            "hovered_part": self._hovered_part,
            "hip_expanded": self._hip_expanded,
            "head_expanded": self._head_expanded,
            "has_horn": self._has_horn,
            "has_beast_ears": self._has_beast_ears
        }