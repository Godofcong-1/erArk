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
    # 立绘根目录，用于遍历全部立绘子目录（干员、特殊NPC、路人、女儿等）
    PORTRAIT_ROOT_DIR = "image/立绘"
    # 优先搜索的立绘子目录名，其余子目录按字典序排在其后
    PRIOR_PORTRAIT_SUB_DIRS = ["干员", "特殊NPC", "路人", "女儿"]

    # 默认部位布局所使用的参考图像边长（正方形，仅作为归一化坐标的基准）
    DEFAULT_BODY_IMAGE_SIZE = 1024
    # 默认部位布局所使用的COCO-17关键点（通用人形站姿的归一化坐标）
    # 用于角色缺少 {角色名}_body.json 时兜底生成部位按钮
    # 注意：left/right 为角色自身的左右，因此在画面上左右是相反的
    DEFAULT_BODY_LANDMARKS = [
        ("nose", 0.500, 0.120),
        ("left_eye", 0.530, 0.105),
        ("right_eye", 0.470, 0.105),
        ("left_ear", 0.560, 0.115),
        ("right_ear", 0.440, 0.115),
        ("left_shoulder", 0.600, 0.215),
        ("right_shoulder", 0.400, 0.215),
        ("left_elbow", 0.645, 0.310),
        ("right_elbow", 0.355, 0.310),
        ("left_wrist", 0.665, 0.410),
        ("right_wrist", 0.335, 0.410),
        ("left_hip", 0.570, 0.490),
        ("right_hip", 0.430, 0.490),
        ("left_knee", 0.565, 0.690),
        ("right_knee", 0.435, 0.690),
        ("left_ankle", 0.560, 0.890),
        ("right_ankle", 0.440, 0.890),
    ]

    # 图像数据缓存，key为 (角色ID, 解析出的立绘名)
    # 使用类级缓存，让不同位置创建的渲染器实例共享结果，避免重复扫描目录
    _image_path_cache: Dict[tuple, dict] = {}
    # 全部立绘子目录的缓存
    _portrait_sub_dirs_cache: Optional[List[str]] = None

    def __init__(self):
        """初始化角色渲染器"""
        self._body_parts_cache: Dict[int, dict] = {}

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

        character_data: game_type.Character = cache.character_data.get(character_id)
        if not character_data:
            return self._get_empty_image_data()

        character_name = character_data.name

        # 以「角色ID + 当前解析出的立绘名」作为缓存key
        # 因为立绘名会随差分（换装、心情、体型等）变化，仅用角色ID缓存会导致差分永远不刷新
        resolved_name = self._get_resolved_image_name(character_id)
        cache_key = (character_id, resolved_name)
        if cache_key in self._image_path_cache:
            return self._image_path_cache[cache_key]

        # 检测角色是否有兽耳和兽角特征（用于部位显示判断）
        # talent[111] = 兽耳, talent[112] = 兽角
        # 兽耳作为独立部位显示，需满足交互对象有兽耳的前提才会显示
        has_beast_ears = character_data.talent.get(111, 0) == 1 if hasattr(character_data, 'talent') else False
        has_horn = character_data.talent.get(112, 0) == 1 if hasattr(character_data, 'talent') else False
        
        # 查找各图层立绘路径
        full_body_image = self._find_full_body_image(character_name, character_id)
        half_body_image = self._find_half_body_image(character_name, character_id)

        # 构建图像数据
        image_data = {
            "character_id": character_id,
            "character_name": character_name,
            "full_body_image": full_body_image,
            "half_body_image": half_body_image,
            "head_image": self._find_head_image(character_name, character_id),
            "body_parts": self._load_body_parts_data(character_name, has_beast_ears, full_body_image or half_body_image),
            "clothing_layers": [],  # 服装图层（待扩展）
            "effect_layers": [],    # 特效图层（待扩展）
            "has_beast_ears": has_beast_ears,  # 角色是否有兽耳（用于兽耳部位显示）
            "has_horn": has_horn,              # 角色是否有兽角（用于头部子部位显示）
        }

        # 缓存结果
        self._image_path_cache[cache_key] = image_data

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

    def _get_portrait_sub_dirs(self) -> List[str]:
        """
        获取全部立绘子目录（干员、特殊NPC、路人、女儿等）

        Returns:
        List[str] -- 立绘子目录路径列表，按搜索优先级排序

        说明：
        原实现只硬编码了「干员」和「特殊NPC」两个目录，
        导致「路人」「女儿」等目录下的角色在Web模式下永远找不到立绘。
        这里改为动态遍历 image/立绘 下的全部子目录。
        """
        # 使用类级缓存，避免每次绘制都扫描目录
        if CharacterRenderer._portrait_sub_dirs_cache is not None:
            return CharacterRenderer._portrait_sub_dirs_cache

        sub_dirs = []
        if os.path.isdir(self.PORTRAIT_ROOT_DIR):
            all_names = sorted(
                name for name in os.listdir(self.PORTRAIT_ROOT_DIR)
                if os.path.isdir(os.path.join(self.PORTRAIT_ROOT_DIR, name))
            )
            # 优先目录排在前面，其余目录按字典序追加
            ordered_names = [name for name in self.PRIOR_PORTRAIT_SUB_DIRS if name in all_names]
            ordered_names += [name for name in all_names if name not in ordered_names]
            sub_dirs = [f"{self.PORTRAIT_ROOT_DIR}/{name}" for name in ordered_names]

        CharacterRenderer._portrait_sub_dirs_cache = sub_dirs
        return sub_dirs

    def _get_resolved_image_name(self, character_id: int) -> str:
        """
        获取角色当前应显示的立绘名（含差分）

        Keyword arguments:
        character_id -- 角色ID

        Returns:
        str -- 立绘图片名（不含扩展名），获取失败时返回空字符串

        说明：
        直接复用tk模式的 character_image.find_character_image_name，
        使Web模式与tk模式的立绘选择逻辑保持一致（差分、女儿、母亲萝莉图等）。
        """
        if character_id < 0:
            return ""
        try:
            from Script.Design import character_image

            return character_image.find_character_image_name(character_id)
        except Exception:
            # 角色数据不完整等异常情况下退化为无差分名，由调用方继续按角色名查找
            return ""

    def _get_era_image_path(self, image_name: str) -> str:
        """
        通过 era_image 的图片路径索引查找图片的真实路径

        Keyword arguments:
        image_name -- 图片名（不含扩展名）

        Returns:
        str -- 图片相对路径（正斜杠分隔），不存在时返回空字符串

        说明：
        era_image.image_path_data 是启动时遍历整个 image 目录建立的「图片名 -> 路径」索引，
        覆盖了立绘下的全部子目录，Web模式的 /api/get_image_paths 已经在使用它，复用不产生额外开销。
        """
        if not image_name:
            return ""
        try:
            from Script.Core import era_image

            image_path = era_image.image_path_data.get(image_name, "")
        except Exception:
            return ""
        if not image_path:
            return ""
        # 统一为正斜杠，供前端拼接URL使用
        image_path = image_path.replace("\\", "/")
        if not os.path.exists(image_path):
            return ""
        return image_path

    def _resolve_image_path_by_id(self, character_id: int, part: str) -> str:
        """
        根据角色ID解析指定图层的立绘路径（支持差分）

        Keyword arguments:
        character_id -- 角色ID
        part -- 图层后缀，取值为 "全身" / "半身" / "头部"

        Returns:
        str -- 立绘相对路径，找不到时返回空字符串
        """
        image_name = self._get_resolved_image_name(character_id)
        if not image_name:
            return ""

        # 去掉已有的图层后缀，得到差分基名
        base_name = image_name
        for suffix in ("_全身", "_半身", "_头部"):
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break

        # 构造候选图片名列表
        candidates = []
        if base_name != image_name:
            # 解析结果本身带图层后缀时，优先换成目标图层
            candidates.append(f"{base_name}_{part}")
        candidates.append(f"{image_name}_{part}")
        if part != "头部":
            # 差分图（如 阿米娅_半裸）与扁平结构（如 女儿_1、菲林_龙门）直接使用原名
            candidates.append(image_name)
            other_part = "半身" if part == "全身" else "全身"
            candidates.append(f"{base_name}_{other_part}")

        for candidate in candidates:
            image_path = self._get_era_image_path(candidate)
            if image_path:
                return image_path

        return ""

    def _find_image_in_all_dirs(self, character_name: str, part: str) -> str:
        """
        在全部立绘子目录中按角色名查找指定图层的立绘

        Keyword arguments:
        character_name -- 角色名称
        part -- 图层后缀，取值为 "全身" / "半身" / "头部"

        Returns:
        str -- 立绘相对路径，找不到时返回空字符串

        说明：
        同时兼容两种目录结构：
        1. 文件夹结构：{立绘目录}/{角色名}/{角色名}_{图层}.png（干员、特殊NPC）
        2. 扁平结构：  {立绘目录}/{角色名}.png（路人、女儿）
        """
        if not character_name:
            return ""

        for portrait_dir in self._get_portrait_sub_dirs():
            char_dir = f"{portrait_dir}/{character_name}"
            # 文件夹结构下的指定图层图
            part_path = f"{char_dir}/{character_name}_{part}.png"
            if os.path.exists(part_path):
                return part_path
            # 头部图不做进一步回退，避免把全身图当作头像
            if part == "头部":
                continue
            # 文件夹结构下不含下划线的原始图片
            if os.path.isdir(char_dir):
                for filename in sorted(os.listdir(char_dir)):
                    if filename.endswith('.png') and '_' not in filename:
                        return f"{char_dir}/{filename}"
            # 扁平结构下的图片
            flat_path = f"{portrait_dir}/{character_name}.png"
            if os.path.exists(flat_path):
                return flat_path

        return ""

    def _find_full_body_image(self, character_name: str, character_id: int = -1) -> str:
        """
        查找角色全身立绘

        Keyword arguments:
        character_name -- 角色名称
        character_id -- 角色ID，传入时可支持差分立绘，默认为-1表示仅按角色名查找

        Returns:
        str -- 全身立绘路径
        """
        # 优先使用与tk模式一致的差分解析结果
        image_path = self._resolve_image_path_by_id(character_id, "全身")
        if image_path:
            return image_path

        # 其次在全部立绘子目录中按角色名查找
        image_path = self._find_image_in_all_dirs(character_name, "全身")
        if image_path:
            return image_path

        # 如果没有全身图，暂时使用半身图作为替代
        return self._find_half_body_image(character_name, character_id)

    def _find_half_body_image(self, character_name: str, character_id: int = -1) -> str:
        """
        查找角色半身立绘

        Keyword arguments:
        character_name -- 角色名称
        character_id -- 角色ID，传入时可支持差分立绘，默认为-1表示仅按角色名查找

        Returns:
        str -- 半身立绘路径
        """
        # 优先使用与tk模式一致的差分解析结果
        image_path = self._resolve_image_path_by_id(character_id, "半身")
        if image_path:
            return image_path

        # 其次在全部立绘子目录中按角色名查找
        image_path = self._find_image_in_all_dirs(character_name, "半身")
        if image_path:
            return image_path

        # 最后查找默认立绘目录下的同名图片
        default_path = f"{self.DEFAULT_PORTRAIT_DIR}/{character_name}.png"
        if os.path.exists(default_path):
            return default_path

        return ""

    def _find_head_image(self, character_name: str, character_id: int = -1) -> str:
        """
        查找角色头部图片

        Keyword arguments:
        character_name -- 角色名称
        character_id -- 角色ID，传入时可支持差分立绘，默认为-1表示仅按角色名查找

        Returns:
        str -- 头部图片路径
        """
        # 优先使用与tk模式一致的差分解析结果
        image_path = self._resolve_image_path_by_id(character_id, "头部")
        if image_path:
            return image_path

        # 其次在全部立绘子目录中按角色名查找
        return self._find_image_in_all_dirs(character_name, "头部")

    def _find_body_json_path(self, character_name: str, portrait_path: str = "") -> str:
        """
        查找角色的身体部位关键点数据文件

        Keyword arguments:
        character_name -- 角色名称
        portrait_path -- 已解析出的立绘路径，用于在同目录下查找关键点文件，默认为空

        Returns:
        str -- 关键点json文件路径，找不到时返回空字符串
        """
        candidates = []

        # 优先在立绘所在目录下查找（可覆盖差分立绘、路人、女儿等各种目录结构）
        if portrait_path:
            portrait_dir = os.path.dirname(portrait_path)
            # 去掉图层/差分后缀，得到基名，例如 阿米娅_半裸 -> 阿米娅
            file_base = os.path.splitext(os.path.basename(portrait_path))[0]
            base_names = [file_base, file_base.split("_")[0], character_name]
            for base_name in base_names:
                if not base_name:
                    continue
                candidates.append(f"{portrait_dir}/{base_name}_body.json")
            candidates.append(f"{portrait_dir}/body_parts.json")

        # 其次在全部立绘子目录下按角色名查找
        for portrait_dir in self._get_portrait_sub_dirs():
            candidates.append(f"{portrait_dir}/{character_name}/{character_name}_body.json")
            candidates.append(f"{portrait_dir}/{character_name}/body_parts.json")

        for json_path in candidates:
            if os.path.exists(json_path):
                return json_path

        return ""

    def _get_nose_position(self, character_name: str, portrait_path: str = "") -> tuple:
        """
        获取角色的鼻子位置（归一化坐标）

        Keyword arguments:
        character_name -- 角色名称
        portrait_path -- 已解析出的立绘路径，用于在同目录下查找关键点文件，默认为空

        Returns:
        tuple -- (nose_x, nose_y) 归一化坐标，如果找不到则返回 (0.5, 0.25) 作为默认值
        """
        # 尝试加载 body.json 文件
        json_path = self._find_body_json_path(character_name, portrait_path)

        if json_path:
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

    def get_avatar_info(self, character_name: str, character_id: int = -1) -> dict:
        """
        获取角色头像信息

        优先使用现成的头像文件，如果没有则返回截取信息

        Keyword arguments:
        character_name -- 角色名称
        character_id -- 角色ID，传入时可支持差分立绘，默认为-1表示仅按角色名查找

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
        head_path = self._find_head_image(character_name, character_id)
        if head_path:
            result["has_avatar_file"] = True
            result["avatar_path"] = head_path
            return result

        # 没有现成头像，尝试获取全身图和鼻子位置
        full_body_path = self._find_full_body_image(character_name, character_id)
        if full_body_path and os.path.exists(full_body_path):
            nose_x, nose_y = self._get_nose_position(character_name, full_body_path)
            result["full_body_path"] = full_body_path
            result["nose_x"] = nose_x
            result["nose_y"] = nose_y
            result["need_crop"] = True
        
        return result

    def _load_body_parts_data(self, character_name: str, has_beast_ears: bool = False, portrait_path: str = "") -> dict:
        """
        加载角色的身体部位位置数据

        Keyword arguments:
        character_name -- 角色名称
        has_beast_ears -- 角色是否有兽耳（用于条件部位显示）
        portrait_path -- 已解析出的立绘路径，用于在同目录下查找关键点文件，默认为空

        Returns:
        dict -- 身体部位位置数据

        说明：
        当角色没有关键点数据文件时，会退化为一套通用人形的默认部位布局，
        以保证任何角色都能通过点击部位来发起交互，而不会出现「没有部位按钮所以无法互动」的情况。
        """
        # 查找 {角色名}_body.json（COCO-WholeBody格式）或旧格式 body_parts.json
        json_path = self._find_body_json_path(character_name, portrait_path)

        if json_path:
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    body_data = self._convert_body_data(raw_data, has_beast_ears)
                    # 关键点数据有效时直接返回，否则继续退化为默认布局
                    if body_data.get("body_parts"):
                        return body_data
            except (json.JSONDecodeError, IOError):
                pass

        # 没有可用的关键点数据，退化为默认部位布局
        return self._build_default_body_parts(has_beast_ears)

    def _build_default_body_parts(self, has_beast_ears: bool = False) -> dict:
        """
        构建默认的身体部位布局

        Keyword arguments:
        has_beast_ears -- 角色是否有兽耳（用于条件部位显示）

        Returns:
        dict -- 身体部位位置数据，附带 is_default 标记表示位置为估算值

        说明：
        使用一套通用人形站姿的COCO关键点，走与真实关键点完全相同的转换流程，
        使没有关键点数据的角色（新增干员、路人、女儿等）也能显示部位按钮。
        """
        raw_data = {
            "image_width": self.DEFAULT_BODY_IMAGE_SIZE,
            "image_height": self.DEFAULT_BODY_IMAGE_SIZE,
            "landmarks": [
                {"name": name, "x": x, "y": y, "score": 1.0}
                for name, x, y in self.DEFAULT_BODY_LANDMARKS
            ],
        }
        result = self._convert_body_data(raw_data, has_beast_ears)
        # 标记为默认布局，前端可据此使用更淡的样式提示部位位置为估算值
        result["is_default"] = True
        return result

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
                        avatar_info = self.get_avatar_info(char_data.name, char_id)
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
