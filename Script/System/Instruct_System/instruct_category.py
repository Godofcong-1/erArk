# -*- coding: utf-8 -*-
"""
指令分类常量定义
用于Web模式下的指令分类系统

此文件定义了指令的大类和子类型，用于在Web模式下
将指令分配到不同的UI区域（面板选项卡栏 vs 角色交互区）

指令分类说明：
1. 系统面板类（SYSTEM_PANEL）：函数内容为 cache.now_panel_id = xxx 的指令
   - 触发方式：点击选项卡栏的按钮
   - 效果：切换到对应的面板进行绘制
   
2. 角色交互类（CHARACTER）：普通的角色交互指令
   - 触发方式：选择交互类型 → 点击身体部位
   - 效果：直接执行交互并结算
   
3. 角色交互面板类（CHARACTER_PANEL）：函数内容带有 now_panel.draw() 的指令
   - 触发方式：选择交互类型 → 点击身体部位（同角色交互类）
   - 效果：创建临时选项卡面板，在面板中选择后再结算，结算后退出临时选项卡
"""


class InstructCategory:
    """
    指令大类
    用于区分指令应显示在哪个UI区域和执行方式
    """
    
    SYSTEM_PANEL = 0
    """
    系统面板类指令
    函数内容为 cache.now_panel_id = xxx 的指令
    点击后将游戏画面从主交互面板切换到特定系统面板
    显示位置：画面最上方的选项卡栏
    包含：系统功能、查看类功能等需要切换面板的功能
    """
    
    CHARACTER = 1
    """
    角色交互类指令
    对当前交互对象进行各种互动的指令
    显示位置：画面左侧的交互类型栏 → 点击身体部位触发
    交互流程：选择交互类型 → 点击角色身体部位 → 直接执行并结算
    """
    
    CHARACTER_PANEL = 2
    """
    角色交互面板类指令
    函数内容带有 now_panel.draw() 的指令
    触发方式与角色交互类相同，但执行后会打开一个临时面板
    显示位置：画面左侧的交互类型栏 → 点击身体部位触发
    交互流程：选择交互类型 → 点击角色身体部位 → 打开临时面板 → 
              在面板中进行选择 → 结算 → 自动退出临时面板
    """


# 注意：交互类型分类已迁移到 interaction_types.py
# 使用 InteractionMajorType（嘴/手/阴茎/道具/其他）和 InteractionMinorType（对话/亲吻/抚摸等）
# 相关映射和工具函数请从 interaction_types.py 导入


class BodyPart:
    """
    身体部位常量
    用于指定指令关联的身体部位
    
    基于 BodyPart.csv 定义的可交互部位:
    0-头发, 1-脸部, 2-口腔, 3-胸部, 4-腋部, 5-手部, 6-小穴, 7-子宫, 
    8-后穴, 9-尿道, 10-腿部, 11-脚部, 12-尾巴, 13-兽角, 14-兽耳, 
    15-胃部, 16-胯部, 17-腹部, 18-背部
    
    COCO-WholeBody 17个关键点映射:
    0-鼻子, 1-左眼, 2-右眼, 3-左耳, 4-右耳, 5-左肩, 6-右肩,
    7-左肘, 8-右肘, 9-左手腕, 10-右手腕, 11-左胯, 12-右胯,
    13-左膝, 14-右膝, 15-左脚踝, 16-右脚踝
    """
    
    # ========== 基于 BodyPart.csv 的可交互部位 ==========
    HAIR = "hair"
    """ 头发 (csv id:0) - 位置：头顶，基于鼻子(0)正上方 """
    
    FACE = "face"
    """ 脸部 (csv id:1) - 位置：基于鼻子(0)、左眼(1)、右眼(2) """
    
    MOUTH = "mouth"
    """ 口腔 (csv id:2) - 位置：基于鼻子(0)正下方 """
    
    CHEST = "chest"
    """ 胸部 (csv id:3) - 位置：左肩(5)和右肩(6)的正中间 """
    
    ARMPIT = "armpit"
    """ 腋部 (csv id:4) - 位置：基于双肩(5,6)位置 """
    
    HAND = "hand"
    """ 手部 (csv id:5) - 位置：基于左手腕(9)和右手腕(10)，合并为同一个 """
    
    VAGINA = "vagina"
    """ 小穴 (csv id:6) - 位置：臀部区域，左胯(11)和右胯(12)正中间，点击臀部展开 """
    
    WOMB = "womb"
    """ 子宫 (csv id:7) - 位置：臀部区域，点击臀部展开 """
    
    ANUS = "anus"
    """ 后穴 (csv id:8) - 位置：臀部区域，点击臀部展开 """
    
    URETHRA = "urethra"
    """ 尿道 (csv id:9) - 位置：臀部区域，点击臀部展开 """
    
    LEG = "leg"
    """ 腿部 (csv id:10) - 位置：基于左膝(13)和右膝(14)，合并为同一个 """
    
    FOOT = "foot"
    """ 脚部 (csv id:11) - 位置：基于左脚踝(15)和右脚踝(16)，合并为同一个 """
    
    TAIL = "tail"
    """ 尾巴 (csv id:12) - 位置：臀部区域，点击臀部展开 """
    
    HORN = "horn"
    """ 兽角 (csv id:13) - 位置：双耳(3,4)的正上方 """
    
    BEAST_EARS = "beast_ears"
    """ 兽耳 (csv id:14) - 位置：基于左耳(3)和右耳(4) """
    
    STOMACH = "stomach"
    """ 胃部 (csv id:15) - 内部器官，不直接显示为按钮 """
    
    CROTCH = "crotch"
    """ 胯部 (csv id:16) - 位置：基于左胯(11)和右胯(12) """
    
    BELLY = "belly"
    """ 腹部 (csv id:17) - 位置：胸部和胯部之间 """
    
    BACK = "back"
    """ 背部 (csv id:18) - 位置：角色背面，通常不显示 """
    
    # ========== 复合/虚拟部位 ==========
    HEAD = "head"
    """ 头部 - 包含头发、脸部的综合区域，基于鼻子(0)正上方 """
    
    HIP = "hip"
    """ 臀部 - 复合部位，点击时展开：小穴、子宫、后穴、尿道、尾巴 """
    
    # ========== CSV ID 到部位的映射 ==========
    @classmethod
    def get_csv_id_mapping(cls):
        """获取 CSV ID 到部位常量的映射"""
        return {
            0: cls.HAIR,
            1: cls.FACE,
            2: cls.MOUTH,
            3: cls.CHEST,
            4: cls.ARMPIT,
            5: cls.HAND,
            6: cls.VAGINA,
            7: cls.WOMB,
            8: cls.ANUS,
            9: cls.URETHRA,
            10: cls.LEG,
            11: cls.FOOT,
            12: cls.TAIL,
            13: cls.HORN,
            14: cls.BEAST_EARS,
            15: cls.STOMACH,
            16: cls.CROTCH,
            17: cls.BELLY,
            18: cls.BACK,
        }


# 身体部位的中文名称映射（基于 BodyPart.csv）
BODY_PART_NAMES = {
    BodyPart.HAIR: "头发",
    BodyPart.FACE: "脸部",
    BodyPart.MOUTH: "口腔",
    BodyPart.CHEST: "胸部",
    BodyPart.ARMPIT: "腋部",
    BodyPart.HAND: "手部",
    BodyPart.VAGINA: "小穴",
    BodyPart.WOMB: "子宫",
    BodyPart.ANUS: "后穴",
    BodyPart.URETHRA: "尿道",
    BodyPart.LEG: "腿部",
    BodyPart.FOOT: "脚部",
    BodyPart.TAIL: "尾巴",
    BodyPart.HORN: "兽角",
    BodyPart.BEAST_EARS: "兽耳",
    BodyPart.STOMACH: "胃部",
    BodyPart.CROTCH: "胯部",
    BodyPart.BELLY: "腹部",
    BodyPart.BACK: "背部",
    BodyPart.HEAD: "头部",
    BodyPart.HIP: "臀部",
}


# 臀部展开的子部位列表
HIP_SUB_PARTS = [
    BodyPart.VAGINA,
    BodyPart.WOMB,
    BodyPart.ANUS,
    BodyPart.URETHRA,
    BodyPart.TAIL,
]


# 头部展开的子部位列表（头发默认显示，兽角和兽耳需要角色有对应特征才显示）
HEAD_SUB_PARTS = [
    BodyPart.HAIR,       # 头发（始终显示）
    BodyPart.HORN,       # 兽角（需要角色有兽角特征）
    BodyPart.BEAST_EARS, # 兽耳（需要角色有兽耳特征）
]


# COCO-WholeBody 17个关键点到部位的映射
# 格式: {关键点索引: (对应部位, 位置类型)}
# 位置类型: "direct"=直接使用, "above"=正上方, "below"=正下方, "center"=需要与其他点计算中心
COCO_KEYPOINT_MAPPING = {
    0: (BodyPart.FACE, "direct"),      # 鼻子 -> 脸部（直接），头部在其上方
    1: (BodyPart.FACE, "direct"),      # 左眼 -> 脸部
    2: (BodyPart.FACE, "direct"),      # 右眼 -> 脸部
    3: (BodyPart.BEAST_EARS, "direct"), # 左耳 -> 兽耳，兽角在其上方
    4: (BodyPart.BEAST_EARS, "direct"), # 右耳 -> 兽耳，兽角在其上方
    5: (BodyPart.ARMPIT, "direct"),    # 左肩 -> 腋部
    6: (BodyPart.ARMPIT, "direct"),    # 右肩 -> 腋部
    7: None,                            # 左肘 -> 不使用
    8: None,                            # 右肘 -> 不使用
    9: (BodyPart.HAND, "direct"),      # 左手腕 -> 手部
    10: (BodyPart.HAND, "direct"),     # 右手腕 -> 手部
    11: (BodyPart.HIP, "direct"),      # 左胯 -> 臀部
    12: (BodyPart.HIP, "direct"),      # 右胯 -> 臀部
    13: (BodyPart.LEG, "direct"),      # 左膝 -> 腿部
    14: (BodyPart.LEG, "direct"),      # 右膝 -> 腿部
    15: (BodyPart.FOOT, "direct"),     # 左脚踝 -> 脚部
    16: (BodyPart.FOOT, "direct"),     # 右脚踝 -> 脚部
}


# 需要通过多个关键点计算中心位置的部位
# 格式: {部位: [(关键点1, 关键点2, ...), 位置偏移]}
COMPUTED_BODY_PARTS = {
    BodyPart.HEAD: {
        "keypoints": [1, 2],  # 基于左眼(1)和右眼(2)中间
        "offset": (0, -0.03),  # 向上偏移图像高度的3%（双眼中间偏上一点）
    },
    BodyPart.HAIR: {
        "keypoints": [1, 2],  # 基于左眼(1)和右眼(2)中间
        "offset": (0, -0.12),  # 向上偏移图像高度的12%（头发位置）
    },
    BodyPart.MOUTH: {
        "keypoints": [0],  # 基于鼻子
        "offset": (0, 0.03),  # 向下偏移图像高度的3%
    },
    BodyPart.CHEST: {
        "keypoints": [5, 6],  # 双肩中心
        "offset": (0, 0.05),  # 向下偏移一点
    },
    BodyPart.HORN: {
        "keypoints": [3, 4],  # 双耳中心
        "offset": (0, -0.08),  # 向上偏移
    },
    BodyPart.BELLY: {
        "keypoints": [5, 6, 11, 12],  # 双肩和双胯的中心
        "offset": (0, 0),
    },
    BodyPart.CROTCH: {
        "keypoints": [11, 12],  # 双胯中心
        "offset": (0, 0),
    },
}


# 主要可点击部位列表（按身体从上到下排序）
# 这些是在角色立绘上直接显示为按钮的部位
# 注意：头发、兽角、兽耳已合并为头部的子部位（类似臀部的子部位机制）
CLICKABLE_BODY_PARTS = [
    BodyPart.HEAD,      # 头部（点击展开子部位：头发、兽角、兽耳）
    BodyPart.FACE,      # 脸部
    BodyPart.MOUTH,     # 口腔
    BodyPart.CHEST,     # 胸部
    BodyPart.ARMPIT,    # 腋部
    BodyPart.HAND,      # 手部
    BodyPart.BELLY,     # 腹部
    BodyPart.HIP,       # 臀部（点击展开子部位）
    BodyPart.LEG,       # 腿部
    BodyPart.FOOT,      # 脚部
]
