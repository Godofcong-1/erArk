from typing import Dict, List, Set
from types import FunctionType


class CharacterStatus:
    """角色状态id"""

    STATUS_ARDER = 0
    """ 休闲状态 """
    STATUS_MOVE = 1
    """ 移动状态 """
    STATUS_REST = 2
    """ 休息状态 """
    STATUS_ATTEND_CLASS = 3
    """ 上课状态 """
    STATUS_EAT = 4
    """ 进食状态 """
    STATUS_CHAT = 5
    """ 闲聊状态 """
    STATUS_PLAY_PIANO = 6
    """ 弹钢琴 """
    STATUS_SINGING = 7
    """ 唱歌 """
    STATUS_TOUCH_HEAD = 8
    """ 摸头 """
    STATUS_SLEEP = 9
    """ 睡觉 """
    STATUS_EMBRACE = 10
    """ 拥抱 """
    STATUS_KISS = 11
    """ 亲吻 """
    STATUS_HAND_IN_HAND = 12
    """ 牵手 """
    STATUS_DEAD = 13
    """ 死亡 """
    STATUS_STROKE = 14
    """ 抚摸 """
    STATUS_TOUCH_CHEST = 15
    """ 摸胸 """
    STATUS_TEACHING = 16
    """ 教学 """
    STATUS_PLAY_GUITAR = 17
    """ 弹吉他 """
    STATUS_SELF_STUDY = 18
    """ 自习 """


class Behavior:
    """行为id"""

    SHARE_BLANKLY = 0
    """ 发呆 """
    MOVE = 1
    """ 移动 """
    REST = 2
    """ 休息 """
    ATTEND_CLASS = 3
    """ 上课 """
    EAT = 4
    """ 进食 """
    CHAT = 5
    """ 闲聊 """
    PLAY_PIANO = 6
    """ 弹钢琴 """
    SINGING = 7
    """ 唱歌 """
    TOUCH_HEAD = 8
    """ 摸头 """
    SLEEP = 9
    """ 睡觉 """
    EMBRACE = 10
    """ 拥抱 """
    KISS = 11
    """ 亲吻 """
    HAND_IN_HAND = 12
    """ 牵手 """
    DEAD = 13
    """ 死亡 """
    STROKE = 14
    """ 抚摸 """
    TOUCH_CHEST = 15
    """ 摸胸 """
    TEACHING = 16
    """ 教学 """
    PLAY_GUITAR = 17
    """ 弹吉他 """
    SELF_STUDY = 18
    """ 自习 """


class StateMachine:
    """状态机id"""

    MOVE_TO_CLASS = 0
    """ 移动到所属教室 """
    MOVE_TO_RAND_CAFETERIA = 1
    """ 移动到随机取餐区 """
    BUY_RAND_FOOD_AT_CAFETERIA = 2
    """ 在取餐区购买随机食物 """
    MOVE_TO_RAND_RESTAURANT = 3
    """ 移动至随机就餐区 """
    EAT_BAG_RAND_FOOD = 4
    """ 食用背包内随机食物 """
    CHAT_RAND_CHARACTER = 5
    """ 和场景里随机对象闲聊 """
    WEAR_CLEAN_UNDERWEAR = 6
    """ 穿干净的上衣 """
    WEAR_CLEAN_UNDERPANTS = 7
    """ 穿干净的内裤 """
    WEAR_CLEAN_BRA = 8
    """ 穿干净的胸罩 """
    WEAR_CLEAN_PANTS = 9
    """ 穿干净的裤子 """
    WEAR_CLEAN_SKIRT = 10
    """ 穿干净的短裙 """
    WEAR_CLEAN_SHOES = 11
    """ 穿干净的鞋子 """
    WEAR_CLEAN_SOCKS = 12
    """ 穿干净的袜子 """
    PLAY_PIANO = 13
    """ 弹钢琴 """
    MOVE_TO_MUSIC_ROOM = 14
    """ 移动至音乐室 """
    SINGING = 15
    """ 唱歌 """
    SING_RAND_CHARACTER = 16
    """ 唱歌给场景里随机对象听 """
    PLAY_PIANO_RAND_CHARACTER = 17
    """ 弹奏钢琴给场景里随机对象听 """
    TOUCH_HEAD_TO_BEYOND_FRIENDSHIP_TARGET_IN_SCENE = 18
    """ 对场景中抱有超越友谊想法的随机对象摸头 """
    MOVE_TO_DORMITORY = 19
    """ 移动至所属宿舍 """
    SLEEP = 20
    """ 睡觉 """
    REST = 21
    """ 休息一会儿 """
    MOVE_TO_RAND_SCENE = 22
    """ 移动至随机场景 """
    EMBRACE_TO_BEYOND_FRIENDSHIP_TARGET_IN_SCENE = 23
    """ 对场景中抱有超越友谊想法的随机对象拥抱 """
    KISS_TO_LIKE_TARGET_IN_SCENE = 24
    """ 和场景中自己喜欢的随机对象接吻 """
    MOVE_TO_LIKE_TARGET_SCENE = 25
    """ 移动至随机某个自己喜欢的人所在场景 """
    HAND_IN_HAND_TO_LIKE_TARGET_IN_SCENE = 26
    """ 牵住场景中自己喜欢的随机对象的手 """
    KISS_TO_NO_FIRST_KISS_TARGET_IN_SCENE = 27
    """ 和场景中自己喜欢的还是初吻的随机对象接吻 """
    MOVE_TO_NO_FIRST_KISS_LIKE_TARGET_SCENE = 28
    """ 移动至喜欢的还是初吻的人所在的场景 """
    DRINK_RAND_DRINKS = 29
    """ 饮用背包内随机饮料 """
    BUY_RAND_DRINKS_AT_CAFETERIA = 30
    """ 在取餐区购买随机饮料 """
    ATTEND_CLASS = 31
    """ 在教室上课 """
    TEACH_A_LESSON = 32
    """ 在教室教课 """
    MOVE_TO_GROVE = 33
    """ 移动至加工站入口场景 """
    MOVE_TO_ITEM_SHOP = 34
    """ 移动至训练场入口场景 """
    BUY_GUITAR = 35
    """ 购买吉他 """
    PLAY_GUITAR = 36
    """ 弹吉他 """
    SELF_STUDY = 37
    """ 自习 """


class Panel:
    """面板id"""

    TITLE = 0
    """ 标题面板 """
    CREATOR_CHARACTER = 1
    """ 创建角色面板 """
    IN_SCENE = 2
    """ 场景互动面板 """
    SEE_MAP = 3
    """ 查看地图面板 """
    FOOD_SHOP = 4
    """ 食物商店面板 """
    FOOD_BAG = 5
    """ 食物背包面板 """
    ITEM_SHOP = 6
    """ 道具商店面板 """
    # VIEW_SCHOOL_TIMETABLE = 7
    # """ 查看课程表 """


class Premise:
    """前提id"""

    IN_CAFETERIA = 0
    """ 处于取餐区 """
    IN_RESTAURANT = 1
    """ 处于就餐区 """
    IN_BREAKFAST_TIME = 2
    """ 处于早餐时间段 """
    IN_LUNCH_TIME = 3
    """ 处于午餐时间段 """
    IN_DINNER_TIME = 4
    """ 处于晚餐时间段 """
    HUNGER = 5
    """ 处于饥饿状态 """
    HAVE_FOOD = 6
    """ 拥有食物 """
    NOT_HAVE_FOOD = 7
    """ 未拥有食物 """
    HAVE_TARGET = 8
    """ 拥有交互对象 """
    TARGET_NO_PLAYER = 9
    """ 交互对象不是玩家 """
    HAVE_DRAW_ITEM = 10
    """ 拥有绘画类道具 """
    HAVE_SHOOTING_ITEM = 11
    """ 拥有射击类道具 """
    HAVE_GUITAR = 12
    """ 拥有吉他 """
    HAVE_HARMONICA = 13
    """ 拥有口琴 """
    HAVE_BAM_BOO_FLUTE = 14
    """ 拥有竹笛 """
    HAVE_BASKETBALL = 15
    """ 拥有篮球 """
    HAVE_FOOTBALL = 16
    """ 拥有足球 """
    HAVE_TABLE_TENNIS = 17
    """ 拥有乒乓球 """
    IN_SWIMMING_POOL = 18
    """ 在游泳池中 """
    IN_CLASSROOM = 19
    """ 在教室中 """
    IS_STUDENT = 20
    """ 是学生 """
    IS_TEACHER = 21
    """ 是老师 """
    IN_SHOP = 22
    """ 在商店中 """
    IN_SLEEP_TIME = 23
    """ 处于睡觉时间 """
    IN_SIESTA_TIME = 24
    """ 处于午休时间 """
    TARGET_IS_FUTA_OR_WOMAN = 25
    """ 目标是扶她或女性 """
    TARGET_IS_FUTA_OR_MAN = 26
    """ 目标是扶她或男性 """
    IS_MAN = 27
    """ 角色是男性 """
    IS_WOMAN = 28
    """ 角色是女性 """
    TARGET_SAME_SEX = 29
    """ 目标与自身性别相同 """
    TARGET_AGE_SIMILAR = 30
    """ 目标与自身年龄相差不大 """
    TARGET_AVERAGE_HEIGHT_SIMILAR = 31
    """ 目标身高与平均身高相差不大 """
    TARGET_AVERAGE_HEIGHT_LOW = 32
    """ 目标身高低于平均身高 """
    TARGET_IS_PLAYER = 33
    """ 目标是玩家角色 """
    TARGET_AVERGAE_STATURE_SIMILAR = 34
    """ 目标体型与平均体型相差不大 """
    TARGET_NOT_PUT_ON_UNDERWEAR = 35
    """ 目标没穿上衣 """
    TARGET_NOT_PUT_ON_SKIRT = 36
    """ 目标没穿短裙 """
    IS_PLAYER = 37
    """ 是玩家角色 """
    NO_PLAYER = 38
    """ 不是玩家角色 """
    IN_PLAYER_SCENE = 39
    """ 与玩家处于相同场景 """
    LEAVE_PLAYER_SCENE = 40
    """ 离开玩家所在场景 """
    TARGET_IS_ADORE = 41
    """ 目标是爱慕对象 """
    TARGET_IS_ADMIRE = 42
    """ 目标是恋慕对象 """
    PLAYER_IS_ADORE = 43
    """ 玩家是爱慕对象 """
    EAT_SPRING_FOOD = 44
    """ 食用了春药品质的食物 """
    IS_HUMOR_MAN = 45
    """ 是一个幽默的人 """
    TARGET_IS_BEYOND_FRIENDSHIP = 46
    """ 对目标抱有超越友谊的想法 """
    IS_BEYOND_FRIENDSHIP_TARGET = 47
    """ 目标对自己抱有超越友谊的想法 """
    SCENE_HAVE_OTHER_CHARACTER = 48
    """ 场景中有自己外的其他角色 """
    NO_WEAR_UNDERWEAR = 49
    """ 没穿上衣 """
    NO_WEAR_UNDERPANTS = 50
    """ 没穿内裤 """
    NO_WEAR_BRA = 51
    """ 没穿胸罩 """
    NO_WEAR_PANTS = 52
    """ 没穿裤子 """
    NO_WEAR_SKIRT = 53
    """ 没穿短裙 """
    NO_WEAR_SHOES = 54
    """ 没穿鞋子 """
    NO_WEAR_SOCKS = 55
    """ 没穿袜子 """
    WANT_PUT_ON = 56
    """ 想穿衣服 """
    HAVE_UNDERWEAR = 57
    """ 拥有上衣 """
    HAVE_UNDERPANTS = 58
    """ 拥有内裤 """
    HAVE_BRA = 59
    """ 拥有胸罩 """
    HAVE_PANTS = 60
    """ 拥有裤子 """
    HAVE_SKIRT = 61
    """ 拥有短裙 """
    HAVE_SHOES = 62
    """ 拥有鞋子 """
    HAVE_SOCKS = 63
    """ 拥有袜子 """
    IN_DORMITORY = 64
    """ 在宿舍中 """
    CHEST_IS_NOT_CLIFF = 65
    """ 胸围不是绝壁 """
    EXCELLED_AT_PLAY_MUSIC = 66
    """ 擅长演奏 """
    EXCELLED_AT_SINGING = 67
    """ 擅长演唱 """
    IN_MUSIC_ROOM = 68
    """ 处于音乐室 """
    NO_EXCELLED_AT_SINGING = 69
    """ 不擅长演唱 """
    SCENE_NO_HAVE_OTHER_CHARACTER = 70
    """ 场景中没有有自己外的其他角色 """
    TARGET_HEIGHT_LOW = 71
    """ 交互对象身高低于自身身高 """
    TARGET_ADORE = 72
    """ 被交互对象爱慕 """
    NO_EXCELLED_AT_PLAY_MUSIC = 73
    """ 不擅长演奏 """
    ARROGANT_HEIGHT = 74
    """ 傲慢情绪高涨 """
    IS_LIVELY = 75
    """ 是一个活跃的人 """
    IS_INFERIORITY = 76
    """ 是一个自卑的人 """
    IS_AUTONOMY = 77
    """ 是一个自律的人 """
    SCENE_CHARACTER_ONLY_PLAYER_AND_ONE = 78
    """ 场景中只有包括玩家在内的两个角色 """
    IS_SOLITARY = 79
    """ 是一个孤僻的人 """
    NO_BEYOND_FRIENDSHIP_TARGET = 80
    """ 目标对自己没有有超越友谊的想法 """
    TARGET_IS_HEIGHT = 81
    """ 目标比自己高 """
    BEYOND_FRIENDSHIP_TARGET_IN_SCENE = 82
    """ 对场景中某个角色抱有超越友谊的想法 """
    HYPOSTHENIA = 83
    """ 体力不足 """
    PHYSICAL_STRENGHT = 84
    """ 体力充沛 """
    IS_INDULGE = 85
    """ 是一个放纵的人 """
    IN_FOUNTAIN = 86
    """ 在会客室入口场景 """
    TARGET_IS_SOLITARY = 87
    """ 交互对象是一个孤僻的人 """
    TARGET_CHEST_IS_CLIFF = 88
    """ 交互对象胸围是绝壁 """
    TARGET_ADMIRE = 89
    """ 被交互对象恋慕 """
    IS_ENTHUSIASM = 90
    """ 是一个热情的人 """
    TARGET_AVERAGE_STATURE_HEIGHT = 91
    """ 目标体型比平均体型更胖 """
    TARGET_NO_FIRST_KISS = 92
    """ 交互对象初吻还在 """
    NO_FIRST_KISS = 93
    """ 初吻还在 """
    IS_TARGET_FIRST_KISS = 94
    """ 是交互对象的初吻对象 """
    HAVE_OTHER_TARGET_IN_SCENE = 95
    """ 场景中有自己和交互对象以外的其他人 """
    NO_HAVE_OTHER_TARGET_IN_SCENE = 96
    """ 场景中没有自己和交互对象以外的其他人 """
    TARGET_HAVE_FIRST_KISS = 97
    """ 交互对象初吻不在了 """
    HAVE_FIRST_KISS = 98
    """ 初吻不在了 """
    HAVE_LIKE_TARGET = 99
    """ 有喜欢的人 """
    HAVE_LIKE_TARGET_IN_SCENE = 100
    """ 场景中有喜欢的人 """
    TARGET_IS_STUDENT = 101
    """ 交互对象是学生 """
    TARGET_IS_ASTUTE = 102
    """ 交互对象是一个机敏的人 """
    TARGET_IS_INFERIORITY = 103
    """ 交互对象是一个自卑的人 """
    TARGET_IS_ENTHUSIASM = 104
    """ 交互对象是一个热情的人 """
    TARGET_IS_SELF_CONFIDENCE = 105
    """ 交互对象是一个自信的人 """
    IS_ASTUTE = 106
    """ 是一个机敏的人 """
    TARGET_IS_HEAVY_FEELING = 107
    """ 交互对象是一个重情的人 """
    TARGET_NO_FIRST_HAND_IN_HAND = 108
    """ 交互对象没有牵过手 """
    NO_FIRST_HAND_IN_HAND = 109
    """ 没有和牵过手 """
    IS_HEAVY_FEELING = 110
    """ 是一个重情的人 """
    HAVE_NO_FIRST_KISS_LIKE_TARGET_IN_SCENE = 111
    """ 有自己喜欢的还是初吻的人在场景中 """
    HAVE_LIKE_TARGET_NO_FIRST_KISS = 112
    """ 有自己喜欢的人的初吻还在 """
    TARGET_IS_APATHY = 113
    """ 交互对象是一个冷漠的人 """
    TARGET_UNARMED_COMBAT_IS_HIGHT = 114
    """ 交互对象徒手格斗技能比自己高 """
    TARGET_DISGUST_IS_HIGHT = 115
    """ 交互对象反感情绪高涨 """
    TARGET_LUST_IS_HIGHT = 116
    """ 交互对象色欲高涨 """
    TARGET_IS_WOMAN = 117
    """ 交互对象是女性 """
    TARGET_IS_NAKED = 118
    """ 交互对象一丝不挂 """
    TARGET_CLITORIS_LEVEL_IS_HIGHT = 119
    """ 交互对象阴蒂开发度高 """
    TARGET_IS_MAN = 120
    """ 交互对象是男性 """
    SEX_EXPERIENCE_IS_HIGHT = 121
    """ 性技熟练 """
    IS_COLLECTION_SYSTEM = 122
    """ 玩家已启用收藏模式 """
    UN_COLLECTION_SYSTEM = 123
    """ 玩家未启用收藏模式 """
    TARGET_IS_COLLECTION = 124
    """ 交互对象已被玩家收藏 """
    TARGET_IS_NOT_COLLECTION = 125
    """ 交互对象未被玩家收藏 """
    TARGET_IS_LIVE = 126
    """ 交互对象未死亡 """
    THIRSTY = 127
    """ 处于口渴状态 """
    HAVE_DRINKS = 128
    """ 背包中有饮料 """
    NO_HAVE_DRINKS = 129
    """ 背包中没有饮料 """
    ATTEND_CLASS_TODAY = 130
    """ 今日需要上课 """
    APPROACHING_CLASS_TIME = 131
    """ 临近上课时间 """
    IN_CLASS_TIME = 132
    """ 处于上课时间 """
    NO_IN_CLASSROOM = 133
    """ 不在教室中 """
    TEACHER_NO_IN_CLASSROOM = 134
    """ 角色所属班级的老师不在教室中 """
    TEACHER_IN_CLASSROOM = 135
    """ 角色所属班级的老师在教室中 """
    IS_NAKED = 136
    """ 角色一丝不挂 """
    IS_BEYOND_FRIENDSHIP_TARGET_IN_SCENE = 137
    """ 场景中有角色对自己抱有超越友谊的想法 """
    HAVE_STUDENTS_IN_CLASSROOM = 138
    """ 有所教班级的学生在教室中 """
    GOOD_AT_ELOQUENCE = 139
    """ 角色擅长口才 """
    GOOD_AT_LITERATURE = 140
    """ 角色擅长文学 """
    GOOD_AT_WRITING = 141
    """ 角色擅长写作 """
    GOOD_AT_DRAW = 142
    """ 角色擅长绘画 """
    GOOD_AT_ART = 143
    """ 角色擅长艺术 """
    TARGET_LITTLE_KNOWLEDGE_OF_RELIGION = 144
    """ 交互对象对宗教一知半解 """
    TARGET_LITTLE_KNOWLEDGE_OF_FAITH = 145
    """ 交互对象对信仰一知半解 """
    TARGET_LITTLE_KNOWLEDGE_OF_ASTRONOMY = 146
    """ 交互对象对天文学一知半解 """
    TARGET_LITTLE_KNOWLEDGE_OF_ASTROLOGY = 147
    """ 交互对象对占星学一知半解 """
    RICH_EXPERIENCE_IN_SEX = 148
    """ 角色性经验丰富 """
    TARGET_IS_SLEEP = 149
    """ 交互对象正在睡觉 """
    IN_ROOFTOP_SCENE = 150
    """ 处于天台场景 """
    TONIGHT_IS_FULL_MOON = 151
    """ 今夜是满月 """
    IS_STARAIGHTFORWARD = 152
    """ 是一个爽直的人 """
    NO_GOOD_AT_ELOQUENCE = 153
    """ 角色不擅长口才 """
    TARGET_NO_EXPERIENCE_IN_SEX = 154
    """ 交互对象没有性经验 """
    LUST_IS_HIGHT = 155
    """ 角色色欲高涨 """
    IN_GROVE = 156
    """ 处于加工站入口场景 """
    NO_IN_GROVE = 157
    """ 未处于加工站入口场景 """
    NAKED_CHARACTER_IN_SCENE = 158
    """ 场景中有人一丝不挂 """
    TARGET_IS_SING = 159
    """ 交互对象正在唱歌 """
    NO_HAVE_GUITAR = 160
    """ 未拥有吉他 """
    IN_ITEM_SHOP = 161
    """ 不在训练场入口中 """
    NO_IN_ITEM_SHOP = 162
    """ 在训练场入口中 """


class BehaviorEffect:
    """行为结算效果函数"""

    ADD_SMALL_HIT_POINT = 0
    """ 增加少量体力 """
    ADD_SMALL_MANA_POINT = 1
    """ 增加少量气力 """
    ADD_INTERACTION_FAVORABILITY = 2
    """ 增加基础互动好感 """
    SUB_SMALL_HIT_POINT = 3
    """ 减少少量体力 """
    SUB_SMALL_MANA_POINT = 4
    """ 减少少量气力 """
    MOVE_TO_TARGET_SCENE = 5
    """ 移动至目标场景 """
    EAT_FOOD = 6
    """ 食用指定食物 """
    ADD_SOCIAL_FAVORABILITY = 7
    """ 增加社交关系好感 """
    ADD_INTIMACY_FAVORABILITY = 8
    """ 增加亲密行为好感(关系不足2则增加反感) """
    ADD_INTIMATE_FAVORABILITY = 9
    """ 增加私密行为好感(关系不足3则增加反感) """
    ADD_SMALL_SING_EXPERIENCE = 10
    """ 增加少量唱歌技能经验 """
    ADD_SMALL_ELOQUENCE_EXPERIENCE = 11
    """ 增加少量口才技能经验 """
    ADD_SMALL_PLAY_MUSIC_EXPERIENCE = 12
    """ 增加少量演奏技能经验 """
    ADD_SMALL_PERFORM_EXPERIENCE = 13
    """ 增加少量表演技能经验 """
    ADD_SMALL_CEREMONY_EXPERIENCE = 14
    """ 增加少量礼仪技能经验 """
    ADD_SMALL_SEX_EXPERIENCE = 15
    """ 增加少量性爱技能经验 """
    ADD_SMALL_MOUTH_SEX_EXPERIENCE = 16
    """ 增加少量嘴部性爱经验 """
    ADD_SMALL_MOUTH_HAPPY = 17
    """ 增加少量嘴部快感 """
    FIRST_KISS = 18
    """ 记录初吻 """
    FIRST_HAND_IN_HAND = 19
    """ 记录初次牵手 """
    ADD_MEDIUM_HIT_POINT = 20
    """ 增加中量体力 """
    ADD_MEDIUM_MANA_POINT = 21
    """ 增加中量气力 """
    TARGET_ADD_SMALL_CHEST_SEX_EXPERIENCE = 22
    """ 交互对象增加少量胸部性爱经验 """
    TARGET_ADD_SMALL_CHEST_HAPPY = 23
    """ 交互对象增加少量胸部快感 """
    TARGET_ADD_SMALL_CLITORIS_SEX_EXPERIENCE = 24
    """ 交互对象增加少量阴蒂性爱经验 """
    TARGET_ADD_SMALL_PENIS_SEX_EXPERIENCE = 25
    """ 交互对象增加少量阴茎性爱经验 """
    TARGET_ADD_SMALL_CLITORIS_HAPPY = 26
    """ 交互对象增加少量阴蒂快感 """
    TARGET_ADD_SMALL_PENIS_HAPPY = 27
    """ 交互对象增加少量阴茎经验 """
    ADD_SMALL_LUST = 28
    """ 自身增加少量色欲 """
    TARGET_ADD_SMALL_LUST = 29
    """ 交互对象增加少量色欲 """
    INTERRUPT_TARGET_ACTIVITY = 30
    """ 打断交互对象活动 """
    TARGET_ADD_SMALL_ELOQUENCE_EXPERIENCE = 31
    """ 交互对象增加少量口才技能经验 """
    TARGET_ADD_FAVORABILITY_FOR_ELOQUENCE = 32
    """ 按口才技能增加交互对象好感 """
    ADD_SMALL_ATTEND_CLASS_EXPERIENCE = 33
    """ 按学习课程增加少量对应技能经验 """
    ADD_STUDENTS_COURSE_EXPERIENCE_FOR_IN_CLASS_ROOM = 34
    """ 按课程增加教室内本班级学生的技能经验 """
    TARGET_ADD_FAVORABILITY_FOR_PERFORMANCE = 35
    """ 按表演技能增加交互对象好感 """
    TARGET_ADD_FAVORABILITY_FOR_SING = 36
    """ 按演唱技能增加交互对象好感 """
    TARGET_ADD_FAVORABILITY_FOR_PLAY_MUSIC = 37
    """ 按演奏技能增加交互对象好感 """
    TARGET_ADD_FAVORABILITY_FOR_TARGET_INTEREST = 38
    """ 按交互对象兴趣增加交互对象好感 """


class InstructType:
    """指令类型"""

    # DIALOGUE = 0
    # """ 对话 """
    # ACTIVE = 1
    # """ 主动 """
    # PASSIVE = 2
    # """ 被动 """
    # PERFORM = 3
    # """ 表演 """
    # OBSCENITY = 4
    # """ 猥亵 """
    # PLAY = 5
    # """ 娱乐 """
    # BATTLE = 6
    # """ 战斗 """
    # STUDY = 7
    # """ 学习 """
    # REST = 8
    # """ 休息 """
    # SEX = 9
    # """ 性爱 """
    # SYSTEM = 10
    # """ 系统 """

    #以下为改变#
    SYSTEM = 0
    """ 系统 """
    DAILY = 1
    """ 日常 """
    PLAY = 2
    """ 娱乐 """
    WORK = 3
    """ 工作 """
    OBSCENITY = 4
    """ 猥亵 """
    SEX = 5
    """ 性爱 """


class Instruct:
    """指令id"""

    CHAT = 0
    """ 闲聊 """
    REST = 0
    """ 休息 """
    SLEEP = 0
    """ 睡觉 """
    SINGING = 0
    """ 唱歌 """
    PLAY_PIANO = 0
    """ 弹钢琴 """
    PLAY_GUITAR = 0
    """ 弹吉他 """
    TOUCH_HEAD = 0
    """ 摸头 """
    TOUCH_CHEST = 0
    """ 摸胸 """
    STROKE = 0
    """ 抚摸 """
    HAND_IN_HAND = 0
    """ 牵手 """
    EMBRACE = 0
    """ 拥抱 """
    KISS = 0
    """ 亲吻 """
    EAT = 0
    """ 进食 """
    DRINK_SPRING = 0
    """ 喝泉水 """
    BUY_FOOD = 0
    """ 购买食物 """
    BUY_ITEM = 0
    """ 购买道具 """
    MOVE = 0
    """ 移动 """
    ATTEND_CLASS = 0
    """ 上课 """
    TEACH_A_LESSON = 0
    """ 教课 """
    SELF_STUDY = 0
    """ 自习 """
    # VIEW_THE_SCHOOL_TIMETABLE = 0
    # """ 查看课程表 """
    SEE_ATTR = 0
    """ 查看属性 """
    SEE_OWNER_ATTR = 0
    """ 查看自身属性 """
    COLLECTION_CHARACTER = 0
    """ 收藏角色 """
    UN_COLLECTION_CHARACTER = 0
    """ 取消收藏 """
    COLLECTION_SYSTEM = 0
    """ 启用收藏模式 """
    UN_COLLECTION_SYSTEM = 0
    """ 关闭收藏模式 """
    SAVE = 0
    """ 读写存档 """


i = 0
for k in Instruct.__dict__:
    if isinstance(Instruct.__dict__[k], int):
        setattr(Instruct, k, i)
        i += 1


handle_premise_data: Dict[str, FunctionType] = {}
""" 前提处理数据 """
handle_instruct_data: Dict[int, FunctionType] = {}
""" 指令处理数据 """
handle_instruct_name_data: Dict[int, str] = {}
""" 指令对应文本 """
instruct_type_data: Dict[int, Set] = {}
""" 指令类型拥有的指令集合 """
instruct_premise_data: Dict[int, Set] = {}
""" 指令显示的所需前提集合 """
handle_state_machine_data: Dict[int, FunctionType] = {}
""" 角色状态机函数 """
family_region_list: Dict[int, str] = {}
""" 姓氏区间数据 """
boys_region_list: Dict[int, str] = {}
""" 男孩名字区间数据 """
girls_region_list: Dict[int, str] = {}
""" 女孩名字区间数据 """
family_region_int_list: List[int] = []
""" 姓氏权重区间数据 """
boys_region_int_list: List[int] = []
""" 男孩名字权重区间数据 """
girls_region_int_list: List[int] = []
""" 女孩名字权重区间数据 """
panel_data: Dict[int, FunctionType] = {}
"""
面板id对应的面板绘制函数集合
面板id:面板绘制函数对象
"""
place_data: Dict[str, List[str]] = {}
""" 按房间类型分类的场景列表 场景标签:场景路径列表 """
cmd_map: Dict[int, FunctionType] = {}
""" cmd存储 """
settle_behavior_effect_data: Dict[int, FunctionType] = {}
""" 角色行为结算处理器 处理器id:处理器 """
