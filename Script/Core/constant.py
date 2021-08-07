from typing import Dict, List, Set
from types import FunctionType


class CharacterStatus:
    """角色状态id"""

    STATUS_ARDER = 0
    """ 休闲状态 """
    STATUS_MOVE = 1
    """ 移动状态 """
    STATUS_H = 2
    """ H状态 """
    STATUS_CHAT = 101
    """ 聊天状态 """
    STATUS_CHAT_FAILED = 102
    """ 谈话次数过多的状态 """
    STATUS_STROKE = 103
    """ 身体接触 """
    STATUS_MAKE_COFFEE = 104
    """ 泡咖啡 """
    STATUS_MAKE_FOOD = 107
    """ 做饭 """
    STATUS_EAT = 108
    """ 进食状态 """
    STATUS_REST = 110
    """ 休息状态 """
    STATUS_SLEEP = 111
    """ 睡觉 """
    STATUS_FOLLOW = 115
    """ NPC跟随玩家 """
    STATUS_TOUCH_HEAD = 301
    """ 摸头 """
    STATUS_TOUCH_BREAST = 302
    """ 摸胸 """
    STATUS_TOUCH_BUTTOCKS = 303
    """ 摸屁股 """
    STATUS_TOUCH_EARS = 304
    """ 摸耳朵 """
    STATUS_TOUCH_HORN = 305
    """ 摸角 """
    STATUS_TOUCH_TAIL = 306
    """ 摸尾巴 """
    STATUS_TOUCH_RING = 307
    """ 摸光环 """
    STATUS_TOUCH_WING = 308
    """ 摸光翼 """
    STATUS_TOUCH_TENTACLE = 309
    """ 摸触手 """
    STATUS_TOUCH_CAR = 310
    """ 摸小车 """
    STATUS_HAND_IN_HAND = 311
    """ 牵手 """
    STATUS_EMBRACE = 312
    """ 拥抱 """
    STATUS_KISS = 313
    """ 亲吻 """
    STATUS_LAP_PILLOW = 314
    """ 膝枕 """
    STATUS_RAISE_SKIRT = 315
    """ 掀起裙子 """
    STATUS_TOUCH_CLITORIS = 317
    """ 阴蒂爱抚 """
    STATUS_TOUCH_VAGINA = 318
    """ 手指插入（V） """
    STATUS_TOUCH_ANUS = 319
    """ 手指插入（A） """
    STATUS_MAKING_OUT = 401
    """ 身体爱抚 """
    STATUS_KISS_H = 402
    """ 接吻 """
    STATUS_BREAST_CARESS = 403
    """ 胸爱抚 """
    STATUS_TWIDDLE_NIPPLES = 404
    """ 玩弄乳头 """
    STATUS_BREAST_SUCKING = 405
    """ 舔吸乳头 """
    STATUS_CLIT_CARESS = 406
    """ 阴蒂爱抚 """
    STATUS_OPEN_LABIA = 407
    """ 掰开阴唇 """
    STATUS_OPEN_ANUS = 408
    """ 掰开肛门 """
    STATUS_CUNNILINGUS = 409
    """ 舔阴 """
    STATUS_LICK_ANAL = 410
    """ 舔肛 """
    STATUS_FINGER_INSERTION = 411
    """ 手指插入(V) """
    STATUS_ANAL_CARESS = 412
    """ 手指插入(A) """
    STATUS_MAKE_MASTUREBATE = 413
    """ 命令对方自慰 """
    STATUS_MAKE_LICK_ANAL = 414
    """ 命令对方舔自己肛门 """
    STATUS_DO_NOTHING = 415
    """ 什么也不做 """
    STATUS_SEDECU = 416
    """ 诱惑对方 """
    STATUS_HANDJOB = 420
    """ 手交 """
    STATUS_BLOWJOB = 421
    """ 口交 """
    STATUS_PAIZURI = 422
    """ 乳交 """
    STATUS_FOOTJOB = 423
    """ 足交 """
    STATUS_HAIRJOB = 424
    """ 发交 """
    STATUS_AXILLAJOB = 425
    """ 腋交 """
    STATUS_RUB_BUTTOCK = 426
    """ 素股 """
    STATUS_HAND_BLOWJOB = 427
    """ 手交口交 """
    STATUS_TITS_BLOWJOB = 428
    """ 乳交口交 """
    STATUS_FOCUS_BLOWJOB = 429
    """ 真空口交 """
    STATUS_DEEP_THROAT = 430
    """ 深喉插入 """
    STATUS_SIXTY_NINE = 431
    """ 六九式 """
    # STATUS_TEACHING = 16
    # """ 教学 """
    # STATUS_PLAY_GUITAR = 17
    # """ 弹吉他 """
    # STATUS_SELF_STUDY = 18
    # """ 自习 """


class Behavior:
    """行为id"""

    SHARE_BLANKLY = 0
    """ 发呆 """
    MOVE = 1
    """ 移动 """
    H = 2
    """ H """
    CHAT = 101
    """ 聊天 """
    CHAT_FAILED = 102
    """ 谈话次数过多而失败 """
    STROKE = 103
    """ 身体接触 """
    MAKE_COFFEE = 104
    """ 泡咖啡 """
    MAKE_FOOD = 107
    """ 做饭 """
    EAT = 108
    """ 进食 """
    REST = 110
    """ 休息 """
    SLEEP = 111
    """ 睡觉 """
    FOLLOW = 115
    """ 让NPC跟随玩家 """
    TOUCH_HEAD = 301
    """ 摸头 """
    TOUCH_BREAST = 302
    """ 摸胸 """
    TOUCH_BUTTOCKS = 303
    """ 摸屁股 """
    TOUCH_EARS = 304
    """ 摸耳朵 """
    TOUCH_HORN = 305
    """ 摸角 """
    TOUCH_TAIL = 306
    """ 摸尾巴 """
    TOUCH_RING = 307
    """ 摸光环 """
    TOUCH_WING = 308
    """ 摸光翼 """
    TOUCH_TENTACLE = 309
    """ 摸触手 """
    TOUCH_CAR = 310
    """ 摸小车 """
    HAND_IN_HAND = 311
    """ 牵手 """
    EMBRACE = 312
    """ 拥抱 """
    KISS = 313
    """ 亲吻 """
    LAP_PILLOW = 314
    """ 膝枕 """
    RAISE_SKIRT = 315
    """ 掀起裙子 """
    TOUCH_CLITORIS = 317
    """ 阴蒂爱抚 """
    TOUCH_VAGINA = 318
    """ 手指插入（V） """
    TOUCH_ANUS = 319
    """ 手指插入（A） """
    MAKING_OUT = 401
    """ 身体爱抚 """
    KISS_H = 402
    """ 接吻 """
    BREAST_CARESS = 403
    """ 胸爱抚 """
    TWIDDLE_NIPPLES = 404
    """ 玩弄乳头 """
    BREAST_SUCKING = 405
    """ 舔吸乳头 """
    CLIT_CARESS = 406
    """ 阴蒂爱抚 """
    OPEN_LABIA = 407
    """ 掰开阴唇观察 """
    OPEN_ANUS = 408
    """ 掰开肛门观察 """
    CUNNILINGUS = 409
    """ 舔阴 """
    LICK_ANAL = 410
    """ 舔肛 """
    FINGER_INSERTION = 411
    """ 手指插入(V) """
    ANAL_CARESS = 412
    """ 手指插入(A) """
    MAKE_MASTUREBATE = 413
    """ 命令对方自慰 """
    MAKE_LICK_ANAL = 414
    """ 命令对方舔自己肛门 """
    DO_NOTHING = 415
    """ 什么也不做 """
    SEDECU = 416
    """ 诱惑对方 """
    HANDJOB = 420
    """ 手交 """
    BLOWJOB = 421
    """ 口交 """
    PAIZURI = 422
    """ 乳交 """
    FOOTJOB = 423
    """ 足交 """
    HAIRJOB = 424
    """ 发交 """
    AXILLAJOB = 425
    """ 腋交 """
    RUB_BUTTOCK = 426
    """ 素股 """
    HAND_BLOWJOB = 427
    """ 手交口交 """
    TITS_BLOWJOB = 428
    """ 乳交口交 """
    FOCUS_BLOWJOB = 429
    """ 真空口交 """
    DEEP_THROAT = 430
    """ 深喉插入 """
    SIXTY_NINE = 431
    """ 六九式 """

    # PLAY_PIANO = 6
    # """ 弹钢琴 """
    # SINGING = 7
    # """ 唱歌 """
    # DEAD = 13
    # """ 死亡 """


class StateMachine:
    """状态机id"""

    WAIT_5_MIN = 0
    """ 原地待机5分钟 """
    WAIT_10_MIN = 1
    """ 原地待机10分钟 """
    WAIT_30_MIN = 2
    """ 原地待机30分钟 """
    REST = 4
    """ 休息一会儿 """
    SLEEP = 5
    """ 睡觉 """
    FOLLOW = 6
    """ 跟随玩家 """
    MOVE_TO_RAND_SCENE = 10
    """ 移动至随机场景 """
    MOVE_TO_DORMITORY = 11
    """ 移动至所属宿舍 """
    MOVE_TO_TOILET = 12
    """ 去洗手间 """
    MOVE_TO_DR_OFFICE = 13
    """ 移动至博士办公室 """
    MOVE_TO_MUSIC_ROOM = 14
    """ 移动至音乐室 """
    CHAT_RAND_CHARACTER = 20
    """ 和场景里随机对象聊天 """
    STROKE_RAND_CHARACTER = 21
    """ 和场景里随机对象身体接触 """
    # MOVE_TO_CLASS = 0
    # """ 移动到所属教室 """
    # MOVE_TO_RAND_CAFETERIA = 1
    # """ 移动到随机取餐区 """
    # BUY_RAND_FOOD_AT_CAFETERIA = 2
    # """ 在取餐区购买随机食物 """
    # MOVE_TO_RAND_RESTAURANT = 3
    # """ 移动至随机就餐区 """
    # EAT_BAG_RAND_FOOD = 4
    # """ 食用背包内随机食物 """
    # WEAR_CLEAN_UNDERWEAR = 6
    # """ 穿干净的上衣 """
    # WEAR_CLEAN_UNDERPANTS = 7
    # """ 穿干净的内裤 """
    # WEAR_CLEAN_BRA = 8
    # """ 穿干净的胸罩 """
    # WEAR_CLEAN_PANTS = 9
    # """ 穿干净的裤子 """
    # WEAR_CLEAN_SKIRT = 10
    # """ 穿干净的短裙 """
    # WEAR_CLEAN_SHOES = 11
    # """ 穿干净的鞋子 """
    # WEAR_CLEAN_SOCKS = 12
    # """ 穿干净的袜子 """
    # PLAY_PIANO = 13
    # """ 弹钢琴 """
    # SINGING = 15
    # """ 唱歌 """
    # SING_RAND_CHARACTER = 16
    # """ 唱歌给场景里随机对象听 """
    # PLAY_PIANO_RAND_CHARACTER = 17
    # """ 弹奏钢琴给场景里随机对象听 """
    # TOUCH_HEAD_TO_BEYOND_FRIENDSHIP_TARGET_IN_SCENE = 18
    # """ 对场景中抱有超越友谊想法的随机对象摸头 """
    # EMBRACE_TO_BEYOND_FRIENDSHIP_TARGET_IN_SCENE = 23
    # """ 对场景中抱有超越友谊想法的随机对象拥抱 """
    # KISS_TO_LIKE_TARGET_IN_SCENE = 24
    # """ 和场景中自己喜欢的随机对象接吻 """
    # MOVE_TO_LIKE_TARGET_SCENE = 25
    # """ 移动至随机某个自己喜欢的人所在场景 """
    # HAND_IN_HAND_TO_LIKE_TARGET_IN_SCENE = 26
    # """ 牵住场景中自己喜欢的随机对象的手 """
    # KISS_TO_NO_FIRST_KISS_TARGET_IN_SCENE = 27
    # """ 和场景中自己喜欢的还是初吻的随机对象接吻 """
    # MOVE_TO_NO_FIRST_KISS_LIKE_TARGET_SCENE = 28
    # """ 移动至喜欢的还是初吻的人所在的场景 """
    # DRINK_RAND_DRINKS = 29
    # """ 饮用背包内随机饮料 """
    # BUY_RAND_DRINKS_AT_CAFETERIA = 30
    # """ 在取餐区购买随机饮料 """
    # ATTEND_CLASS = 31
    # """ 在教室上课 """
    # TEACH_A_LESSON = 32
    # """ 在教室教课 """
    # MOVE_TO_GROVE = 33
    # """ 移动至加工站入口场景 """
    # MOVE_TO_ITEM_SHOP = 34
    # """ 移动至训练场入口场景 """
    # BUY_GUITAR = 35
    # """ 购买吉他 """
    # PLAY_GUITAR = 36
    # """ 弹吉他 """
    # SELF_STUDY = 37
    # """ 自习 """


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
    # GET_UP = 7
    # """ 起床面板 """
    MAKE_FOOD = 7
    """ 做饭面板 """


class Premise:
    """前提id"""

    IS_PLAYER = "sys_0"
    """ 玩家触发的该指令 """
    NO_PLAYER = "sys_1"
    """ NPC触发的该指令 """
    HAVE_TARGET = "sys_2"
    """ 拥有交互对象 """
    HAVE_NO_TARGET = "sys_3"
    """ 没有交互对象 """
    TARGET_IS_PLAYER = "sys_4"
    """ 交互对象是玩家角色 """
    TARGET_NO_PLAYER = "sys_5"
    """ 交互对象不是玩家 """
    IS_MAN = "sex_0"
    """ 触发该指令的是男性 """
    IS_WOMAN = "sex_1"
    """ 触发该指令的是女性 """
    IS_H = "is_h"
    """ 当前为H模式 """
    NOT_H = "not_h"
    """ 当前不是H模式 """
    IS_FOLLOW = "is_follow"
    """ 当前正跟随玩家 """
    NOT_FOLLOW = "not_follow"
    """ 当前没跟随玩家 """

    HIGH_5 = "high_5"
    """ 优先度为5的空白前提 """
    HIGH_10 = "high_10"
    """ 优先度为10的空白前提 """

    HP_LOW = "hp_low"
    """ 自身体力低于30% """
    HP_HIGH = "hp_high"
    """ 自身体力高于70% """
    MP_0 = "mp_0"
    """ 自身气力为0 """
    MP_LOW = "mp_low"
    """ 自身气力低于30% """
    MP_HIGH = "mp_high"
    """ 自身气力高于70% """
    TARGET_HP_LOW = "t_hp_low"
    """ 交互对象体力低于30% """
    TARGET_HP_HIGH = "t_hp_high"
    """ 交互对象体力高于70% """
    TARGET_MP_0 = "t_mp_0"
    """ 交互对象气力为0 """
    TARGET_MP_LOW = "t_mp_low"
    """ 交互对象气力低于30% """
    TARGET_MP_HIGH = "t_mp_high"
    """ 交互对象气力高于70% """

    IN_PLAYER_SCENE = "place_0"
    """ 与玩家处于相同地点 """
    # IN_PLAYER_ZONE = "place_1"
    # """ 与玩家处于相同大区域 """
    PLAYER_COME_SCENE = "place_2"
    """ 玩家来到该角色所在的地点 """
    # PLAYER_COME_ZONE = "place_3"
    # """ 玩家来到该角色所在的区域 """
    PLAYER_LEAVE_SCENE = "place_4"
    """ 玩家离开该角色所在的地点 """
    # PLAYER_LEAVE_ZONE = "place_5"
    # """ 玩家离开该角色所在的区域 """
    TATGET_COME_SCENE = "place_6"
    """ 该角色来到玩家所在的地点 """
    # TATGET_COME_ZONE = "place_7"
    # """ 该角色来到玩家所在的区域 """
    TATGET_LEAVE_SCENE = "place_8"
    """ 该角色离开玩家所在的地点 """
    # TATGET_LEAVE_ZONE = "place_9"
    # """ 该角色离开玩家所在的区域 """
    SCENE_ONLY_TWO = "place_10"
    """ 该地点仅有玩家和该角色 """
    SCENE_OVER_TWO = "place_11"
    """ 该地点里有除了玩家和该角色之外的人 """
    SCENE_ONLY_ONE = "place_12"
    """ 该地点里没有自己外的其他角色 """
    IN_KITCHEN = "in_kit"
    """ 在厨房 """
    IN_DINING_HALL = "in_din"
    """ 在食堂 """

    TIME_DAY = "time_day"
    """ 时间:白天（6点~18点） """
    TIME_NIGHT = "time_night"
    """ 时间:夜晚（18点~6点） """
    TIME_MIDNIGHT = "time_midnight"
    """ 时间:深夜（22点~2点） """
    TIME_MORNING = "time_morning"
    """ 时间:清晨（4点~8点） """
    TIME_MOON = "time_moon"
    """ 时间:中午（10点~14点） """

    COOK_1 = "cook_1"
    """ 自身料理技能==1 """
    COOK_2 = "cook_2"
    """ 自身料理技能==2 """
    COOK_3 = "cook_3"
    """ 自身料理技能==3 """
    COOK_4 = "cook_4"
    """ 自身料理技能==4 """
    COOK_LE_1 = "cook_le_1"
    """ 自身料理技能<=1 """
    COOK_GE_3 = "cook_ge_3"
    """ 自身料理技能>=3 """
    COOK_GE_5 = "cook_ge_5"
    """ 自身料理技能>=5 """
    MUSIC_1 = "music_1"
    """ 自身音乐技能==1 """
    MUSIC_2 = "music_2"
    """ 自身音乐技能==2 """
    MUSIC_3 = "music_3"
    """ 自身音乐技能==3 """
    MUSIC_4 = "music_4"
    """ 自身音乐技能==4 """
    MUSIC_LE_1 = "music_le_1"
    """ 自身音乐技能<=1 """
    MUSIC_GE_3 = "music_ge_3"
    """ 自身音乐技能>=3 """
    MUSIC_GE_5 = "music_ge_5"
    """ 自身音乐技能>=5 """

    TARGET_DESIRE_GE_5 = "desire_ge_5"
    """ 交互对象欲望>=5 """
    TARGET_DESIRE_GE_7 = ""
    """ 交互对象欲望>=7 """
    TARGET_COOK_1 = "t_cook_1"
    """ 交互对象料理技能==1 """
    TARGET_COOK_2 = "t_cook_2"
    """ 交互对象料理技能==2 """
    TARGET_COOK_3 = "t_cook_3"
    """ 交互对象料理技能==3 """
    TARGET_COOK_4 = "t_cook_4"
    """ 交互对象料理技能==4 """
    TARGET_COOK_LE_1 = "t_cook_le_1"
    """ 交互对象料理技能<=1 """
    TARGET_COOK_GE_3 = "t_cook_ge_3"
    """ 交互对象料理技能>=3 """
    TARGET_COOK_GE_5 = "t_cook_ge_5"
    """ 交互对象料理技能>=5 """
    TARGET_MUSIC_1 = "t_music_1"
    """ 交互对象音乐技能==1 """
    TARGET_MUSIC_2 = "t_music_2"
    """ 交互对象音乐技能==2 """
    TARGET_MUSIC_3 = "t_music_3"
    """ 交互对象音乐技能==3 """
    TARGET_MUSIC_4 = "t_music_4"
    """ 交互对象音乐技能==4 """
    TARGET_MUSIC_LE_1 = "t_music_le_1"
    """ 交互对象音乐技能<=1 """
    TARGET_MUSIC_GE_3 = "t_music_ge_3"
    """ 交互对象音乐技能>=3 """
    TARGET_MUSIC_GE_5 = "t_music_ge_5"
    """ 交互对象音乐技能>=5 """

    TARGET_NOT_FALL = "not_fall"
    """ 交互对象无陷落素质 """
    TARGET_LOVE_1 = "love_1"
    """ 交互对象拥有思慕（爱情系第一阶段） """
    TARGET_LOVE_2 = "love_2"
    """ 交互对象拥有恋慕（爱情系第二阶段） """
    TARGET_LOVE_3 = "love_3"
    """ 交互对象拥有恋人（爱情系第三阶段） """
    TARGET_LOVE_4 = "love_4"
    """ 交互对象拥有爱侣（爱情系第四阶段） """
    TARGET_LOVE_GE_1 = "love_ge_1"
    """ 交互对象爱情系>=思慕 """
    TARGET_LOVE_GE_2 = "love_ge_2"
    """ 交互对象爱情系>=恋慕 """
    TARGET_LOVE_GE_3 = "love_ge_3"
    """ 交互对象爱情系>=恋人 """
    TARGET_OBEY_1 = "obey_1"
    """ 交互对象拥有屈从（隶属系第一阶段） """
    TARGET_OBEY_2 = "obey_2"
    """ 交互对象拥有驯服（隶属系第二阶段） """
    TARGET_OBEY_3 = "obey_3"
    """ 交互对象拥有妄信（隶属系第三阶段） """
    TARGET_OBEY_4 = "obey_4"
    """ 交互对象拥有奴隶（隶属系第四阶段） """
    TARGET_OBEY_GE_1 = "obey_ge_1"
    """ 交互对象隶属系>=屈从 """
    TARGET_OBEY_GE_2 = "obey_ge_2"
    """ 交互对象隶属系>=驯服 """
    TARGET_OBEY_GE_3 = "obey_ge_3"
    """ 交互对象隶属系>=妄信 """

    TARGET_NO_FIRST_KISS = "kiss_0"
    """ 交互对象未保有初吻 """
    TARGET_HAVE_FIRST_KISS = "kiss_1"
    """ 交互对象保有初吻 """
    TARGET_NO_VIRGIN = "virgin_0"
    """ 交互对象非处女 """
    TARGET_HAVE_VIRGIN = "virgin_1"
    """ 交互对象是处女 """
    TARGET_NO_A_VIRGIN = "a_virgin_0"
    """ 交互对象非A处女 """
    TARGET_HAVE_A_VIRGIN = "a_virgin_1"
    """ 交互对象是A处女 """

    TARGET_CHEST_IS_CLIFF = "breast_0"
    """ 交互对象胸部大小是绝壁 """
    TARGET_CHEST_IS_SMALL = "breast_1"
    """ 交互对象胸部大小是贫乳 """
    TARGET_CHEST_IS_NORMAL = "breast_2"
    """ 交互对象胸部大小是普乳 """
    TARGET_CHEST_IS_BIG = "breast_3"
    """ 交互对象胸部大小是巨乳 """
    TARGET_CHEST_IS_SUPER = "breast_4"
    """ 交互对象胸部大小是爆乳 """
    TARGET_BUTTOCKS_IS_SMALL = "buttock_0"
    """ 交互对象臀部大小是小尻 """
    TARGET_BUTTOCKS_IS_NORMAL = "buttock_1"
    """ 交互对象臀部大小是普尻 """
    TARGET_BUTTOCKS_IS_BIG = "buttock_2"
    """ 交互对象臀部大小是巨尻 """

    TARGET_HAVE_NO_EARS = "ear_0"
    """ 交互对象没有兽耳 """
    TARGET_HAVE_EARS = "ear_1"
    """ 交互对象有兽耳 """
    TARGET_HAVE_NO_HORN = "horn_0"
    """ 交互对象没有兽角 """
    TARGET_HAVE_HORN = "horn_1"
    """ 交互对象有兽角 """
    TARGET_HAVE_NO_TAIL = "tail_0"
    """ 交互对象没有兽尾 """
    TARGET_HAVE_TAIL = "tail_1"
    """ 交互对象有兽尾 """
    TARGET_HAVE_NO_RING = "ring_0"
    """ 交互对象没有光环 """
    TARGET_HAVE_RING = "ring_1"
    """ 交互对象有光环 """
    TARGET_HAVE_NO_WING = "wing_0"
    """ 交互对象没有光翼 """
    TARGET_HAVE_WING = "wing_1"
    """ 交互对象有光翼 """
    TARGET_HAVE_NO_TENTACLE = "tentacle_0"
    """ 交互对象没有触手 """
    TARGET_HAVE_TENTACLE = "tentacle_1"
    """ 交互对象有触手 """
    TARGET_HAVE_NO_CAR = "car_0"
    """ 交互对象没有小车 """
    TARGET_HAVE_CAR = "car_1"
    """ 交互对象有小车 """

    LAST_CMD_BLOWJOB = "last_cmd_blowjob"
    """ 前一指令为口交 """
    LAST_CMD_BLOWJOB_OR_HANDJOB = "last_cmd_blowjob_or_handjob"
    """ 前一指令为口交或手交 """
    LAST_CMD_BLOWJOB_OR_PAIZURI = "last_cmd_blowjob_or_paizuri"
    """ 前一指令为口交或乳交 """
    LAST_CMD_BLOWJOB_OR_CUNNILINGUS = "last_cmd_blowjob_or_cunnilingus"
    """ 前一指令为口交或舔阴 """


    HYPOSTHENIA = "83"
    """ 体力不足 """
    PHYSICAL_STRENGHT = "84"
    """ 体力充沛 """


    IN_CAFETERIA = "0"
    """ 处于取餐区 """
    IN_RESTAURANT = "1"
    """ 处于就餐区 """
    IN_BREAKFAST_TIME = "2"
    """ 处于早餐时间段 """
    IN_LUNCH_TIME = "3"
    """ 处于午餐时间段 """
    IN_DINNER_TIME = "4"
    """ 处于晚餐时间段 """
    HUNGER = "5"
    """ 处于饥饿状态 """
    HAVE_FOOD = "6"
    """ 拥有食物 """
    NOT_HAVE_FOOD = "7"
    """ 未拥有食物 """
    HAVE_DRAW_ITEM = "10"
    """ 拥有绘画类道具 """
    HAVE_SHOOTING_ITEM = "11"
    """ 拥有射击类道具 """
    HAVE_GUITAR = "12"
    """ 拥有吉他 """
    HAVE_HARMONICA = "13"
    """ 拥有口琴 """
    HAVE_BAM_BOO_FLUTE = "14"
    """ 拥有竹笛 """
    HAVE_BASKETBALL = "15"
    """ 拥有篮球 """
    HAVE_FOOTBALL = "16"
    """ 拥有足球 """
    HAVE_TABLE_TENNIS = "17"
    """ 拥有乒乓球 """
    IN_SWIMMING_POOL = "18"
    """ 在游泳池中 """
    IN_CLASSROOM = "19"
    """ 在教室中 """
    IS_STUDENT = "20"
    """ 是学生 """
    IS_TEACHER = "21"
    """ 是老师 """
    IN_SHOP = "22"
    """ 在商店中 """
    IN_SLEEP_TIME = "23"
    """ 处于睡觉时间 """
    IN_SIESTA_TIME = "24"
    """ 处于午休时间 """
    TARGET_IS_FUTA_OR_WOMAN = "25"
    """ 目标是扶她或女性 """
    TARGET_IS_FUTA_OR_MAN = "26"
    """ 目标是扶她或男性 """
    TARGET_SAME_SEX = "29"
    """ 目标与自身性别相同 """
    TARGET_NOT_PUT_ON_UNDERWEAR = "35"
    """ 目标没穿上衣 """
    TARGET_NOT_PUT_ON_SKIRT = "36"
    """ 目标没穿短裙 """
    TARGET_IS_ADORE = "41"
    """ 目标是爱慕对象 """
    TARGET_IS_ADMIRE = "42"
    """ 目标是恋慕对象 """
    PLAYER_IS_ADORE = "43"
    """ 玩家是爱慕对象 """
    EAT_SPRING_FOOD = "44"
    """ 食用了春药品质的食物 """
    TARGET_IS_BEYOND_FRIENDSHIP = "46"
    """ 对目标抱有超越友谊的想法 """
    IS_BEYOND_FRIENDSHIP_TARGET = "47"
    """ 目标对自己抱有超越友谊的想法 """
    NO_WEAR_UNDERWEAR = "49"
    """ 没穿上衣 """
    NO_WEAR_UNDERPANTS = "50"
    """ 没穿内裤 """
    NO_WEAR_BRA = "51"
    """ 没穿胸罩 """
    NO_WEAR_PANTS = "52"
    """ 没穿裤子 """
    NO_WEAR_SKIRT = "53"
    """ 没穿短裙 """
    NO_WEAR_SHOES = "54"
    """ 没穿鞋子 """
    NO_WEAR_SOCKS = "55"
    """ 没穿袜子 """
    WANT_PUT_ON = "56"
    """ 想穿衣服 """
    HAVE_UNDERWEAR = "57"
    """ 拥有上衣 """
    HAVE_UNDERPANTS = "58"
    """ 拥有内裤 """
    HAVE_BRA = "59"
    """ 拥有胸罩 """
    HAVE_PANTS = "60"
    """ 拥有裤子 """
    HAVE_SKIRT = "61"
    """ 拥有短裙 """
    HAVE_SHOES = "62"
    """ 拥有鞋子 """
    HAVE_SOCKS = "63"
    """ 拥有袜子 """
    IN_DORMITORY = "64"
    """ 在宿舍中 """
    CHEST_IS_NOT_CLIFF = "65"
    """ 胸围不是绝壁 """
    IN_MUSIC_ROOM = "68"
    """ 处于音乐室 """
    NO_EXCELLED_AT_SINGING = "69"
    """ 不擅长演唱 """
    TARGET_HEIGHT_LOW = "71"
    """ 交互对象身高低于自身身高 """
    TARGET_ADORE = "72"
    """ 被交互对象爱慕 """
    NO_EXCELLED_AT_PLAY_MUSIC = "73"
    """ 不擅长演奏 """
    ARROGANT_HEIGHT = "74"
    """ 傲慢情绪高涨 """
    SCENE_CHARACTER_ONLY_PLAYER_AND_ONE = "78"
    """ 场景中只有包括玩家在内的两个角色 """
    NO_BEYOND_FRIENDSHIP_TARGET = "80"
    """ 目标对自己没有有超越友谊的想法 """
    BEYOND_FRIENDSHIP_TARGET_IN_SCENE = "82"
    """ 对场景中某个角色抱有超越友谊的想法 """
    IN_FOUNTAIN = "86"
    """ 在会客室入口场景 """
    TARGET_ADMIRE = "89"
    """ 被交互对象恋慕 """
    IS_ENTHUSIASM = "90"
    """ 是一个热情的人 """
    NO_FIRST_KISS = "93"
    """ 初吻还在 """
    IS_TARGET_FIRST_KISS = "94"
    """ 是交互对象的初吻对象 """
    HAVE_OTHER_TARGET_IN_SCENE = "95"
    """ 场景中有自己和交互对象以外的其他人 """
    NO_HAVE_OTHER_TARGET_IN_SCENE = "96"
    """ 场景中没有自己和交互对象以外的其他人 """
    HAVE_FIRST_KISS = "98"
    """ 初吻不在了 """
    HAVE_LIKE_TARGET = "99"
    """ 有喜欢的人 """
    HAVE_LIKE_TARGET_IN_SCENE = "100"
    """ 场景中有喜欢的人 """
    TARGET_IS_STUDENT = "101"
    """ 交互对象是学生 """
    TARGET_NO_FIRST_HAND_IN_HAND = "108"
    """ 交互对象没有牵过手 """
    NO_FIRST_HAND_IN_HAND = "109"
    """ 没有和牵过手 """
    HAVE_NO_FIRST_KISS_LIKE_TARGET_IN_SCENE = "111"
    """ 有自己喜欢的还是初吻的人在场景中 """
    HAVE_LIKE_TARGET_NO_FIRST_KISS = "112"
    """ 有自己喜欢的人的初吻还在 """
    TARGET_UNARMED_COMBAT_IS_HIGHT = "114"
    """ 交互对象徒手格斗技能比自己高 """
    TARGET_DISGUST_IS_HIGHT = "115"
    """ 交互对象反感情绪高涨 """
    TARGET_LUST_IS_HIGHT = "116"
    """ 交互对象色欲高涨 """
    TARGET_IS_WOMAN = "117"
    """ 交互对象是女性 """
    TARGET_CLITORIS_LEVEL_IS_HIGHT = "119"
    """ 交互对象阴蒂开发度高 """
    TARGET_IS_MAN = "120"
    """ 交互对象是男性 """
    SEX_EXPERIENCE_IS_HIGHT = "121"
    """ 性技熟练 """
    IS_COLLECTION_SYSTEM = "122"
    """ 玩家已启用收藏模式 """
    UN_COLLECTION_SYSTEM = "123"
    """ 玩家未启用收藏模式 """
    TARGET_IS_COLLECTION = "124"
    """ 交互对象已被玩家收藏 """
    TARGET_IS_NOT_COLLECTION = "125"
    """ 交互对象未被玩家收藏 """
    TARGET_IS_LIVE = "126"
    """ 交互对象未死亡 """
    THIRSTY = "127"
    """ 处于口渴状态 """
    HAVE_DRINKS = "128"
    """ 背包中有饮料 """
    NO_HAVE_DRINKS = "129"
    """ 背包中没有饮料 """
    ATTEND_CLASS_TODAY = "130"
    """ 今日需要上课 """
    NO_IN_CLASSROOM = "133"
    """ 不在教室中 """
    TEACHER_IN_CLASSROOM = "135"
    """ 角色所属班级的老师在教室中 """
    IS_BEYOND_FRIENDSHIP_TARGET_IN_SCENE = "137"
    """ 场景中有角色对自己抱有超越友谊的想法 """
    HAVE_STUDENTS_IN_CLASSROOM = "138"
    """ 有所教班级的学生在教室中 """
    TARGET_IS_SLEEP = "149"
    """ 交互对象正在睡觉 """
    IN_ROOFTOP_SCENE = "150"
    """ 处于天台场景 """
    TONIGHT_IS_FULL_MOON = "151"
    """ 今夜是满月 """
    TARGET_NO_EXPERIENCE_IN_SEX = "154"
    """ 交互对象没有性经验 """
    LUST_IS_HIGHT = "155"
    """ 角色色欲高涨 """
    IN_GROVE = "156"
    """ 处于加工站入口场景 """
    NO_IN_GROVE = "157"
    """ 未处于加工站入口场景 """
    TARGET_IS_SING = "159"
    """ 交互对象正在唱歌 """
    NO_HAVE_GUITAR = "160"
    """ 未拥有吉他 """
    IN_ITEM_SHOP = "161"
    """ 不在训练场入口中 """
    NO_IN_ITEM_SHOP = "162"
    """ 在训练场入口中 """

    #旧前提存档#
    # HAVE_TARGET = "8"
    # """ 拥有交互对象 """
    # TARGET_NO_PLAYER = "9"
    # """ 交互对象不是玩家 """
    # TARGET_AGE_SIMILAR = "30"
    # """ 目标与自身年龄相差不大 """
    # TARGET_AVERAGE_HEIGHT_SIMILAR = "31"
    # """ 目标身高与平均身高相差不大 """
    # TARGET_AVERAGE_HEIGHT_LOW = "32"
    # """ 目标身高低于平均身高 """
    # TARGET_IS_PLAYER = "33"
    # """ 目标是玩家角色 """
    # TARGET_AVERGAE_STATURE_SIMILAR = "34"
    # """ 目标体型与平均体型相差不大 """
    # IS_PLAYER = "37"
    # """ 是玩家角色 """
    # NO_PLAYER = "38"
    # """ 不是玩家角色 """
    # EXCELLED_AT_PLAY_MUSIC = "66"
    # """ 擅长演奏 """
    # EXCELLED_AT_SINGING = "67"
    # """ 擅长演唱 """
    # TARGET_IS_HEIGHT = "81"
    # """ 目标比自己高 """
    # TARGET_AVERAGE_STATURE_HEIGHT = "91"
    # """ 目标体型比平均体型更胖 """
    # TARGET_IS_NAKED = "118"
    # """ 交互对象一丝不挂 """
    # APPROACHING_CLASS_TIME = "131"
    # """ 临近上课时间 """
    # IN_CLASS_TIME = "132"
    # """ 处于上课时间 """
    # TEACHER_NO_IN_CLASSROOM = "134"
    # """ 角色所属班级的老师不在教室中 """
    # IS_NAKED = "136"
    # """ 角色一丝不挂 """
    # GOOD_AT_ELOQUENCE = "139"
    # """ 角色擅长口才 """
    # GOOD_AT_LITERATURE = "140"
    # """ 角色擅长文学 """
    # GOOD_AT_WRITING = "141"
    # """ 角色擅长写作 """
    # GOOD_AT_DRAW = "142"
    # """ 角色擅长绘画 """
    # GOOD_AT_ART = "143"
    # """ 角色擅长艺术 """
    # TARGET_LITTLE_KNOWLEDGE_OF_RELIGION = "144"
    # """ 交互对象对宗教一知半解 """
    # TARGET_LITTLE_KNOWLEDGE_OF_FAITH = "145"
    # """ 交互对象对信仰一知半解 """
    # TARGET_LITTLE_KNOWLEDGE_OF_ASTRONOMY = "146"
    # """ 交互对象对天文学一知半解 """
    # TARGET_LITTLE_KNOWLEDGE_OF_ASTROLOGY = "147"
    # """ 交互对象对占星学一知半解 """
    # RICH_EXPERIENCE_IN_SEX = "148"
    # """ 角色性经验丰富 """
    # NO_GOOD_AT_ELOQUENCE = "153"
    # """ 角色不擅长口才 """
    # NAKED_CHARACTER_IN_SCENE = "158"
    # """ 场景中有人一丝不挂 """

    # IS_HUMOR_MAN = "45"
    # """ 是一个幽默的人 """
    # IS_LIVELY = "75"
    # """ 是一个活跃的人 """
    # IS_INFERIORITY = "76"
    # """ 是一个自卑的人 """
    # IS_AUTONOMY = "77"
    # """ 是一个自律的人 """
    # IS_SOLITARY = "79"
    # """ 是一个孤僻的人 """
    # IS_INDULGE = "85"
    # """ 是一个放纵的人 """
    # TARGET_IS_SOLITARY = "87"
    # """ 交互对象是一个孤僻的人 """
    # TARGET_IS_ASTUTE = "102"
    # """ 交互对象是一个机敏的人 """
    # TARGET_IS_INFERIORITY = "103"
    # """ 交互对象是一个自卑的人 """
    # TARGET_IS_ENTHUSIASM = "104"
    # """ 交互对象是一个热情的人 """
    # TARGET_IS_SELF_CONFIDENCE = "105"
    # """ 交互对象是一个自信的人 """
    # IS_ASTUTE = "106"
    # """ 是一个机敏的人 """
    # TARGET_IS_HEAVY_FEELING = "107"
    # """ 交互对象是一个重情的人 """
    # IS_HEAVY_FEELING = "110"
    # """ 是一个重情的人 """
    # TARGET_IS_APATHY = "113"
    # """ 交互对象是一个冷漠的人 """
    # IS_STARAIGHTFORWARD = "152"
    # """ 是一个爽直的人 """


class BehaviorEffect:
    """行为结算效果函数"""

    ADD_SMALL_HIT_POINT = 0
    """ 增加少量体力 """
    ADD_SMALL_MANA_POINT = 1
    """ 增加少量气力 """
    ADD_INTERACTION_FAVORABILITY = 2
    """ 增加基础互动好感 """
    SUB_BOTH_SMALL_HIT_POINT = 3
    """ 双方减少少量体力（若没有交互对象则仅减少自己） """
    SUB_BOTH_SMALL_MANA_POINT = 4
    """ 双方减少少量气力（若没有交互对象则仅减少自己） """
    MOVE_TO_TARGET_SCENE = 5
    """ 移动至目标场景 """
    ADD_SMALL_TRUST = 6
    """ 增加基础互动信赖 """

    FIRST_KISS = 18
    """ 记录初吻 """
    FIRST_HAND_IN_HAND = 19
    """ 记录初次牵手 """
    ADD_MEDIUM_HIT_POINT = 20
    """ 增加中量体力 """
    ADD_MEDIUM_MANA_POINT = 21
    """ 增加中量气力 """
    INTERRUPT_TARGET_ACTIVITY = 30
    """ 打断交互对象活动 """
    TARGET_ADD_SMALL_N_FEEL = 41
    """ 交互对象增加少量Ｎ快 """
    TARGET_ADD_SMALL_B_FEEL = 42
    """ 交互对象增加少量Ｂ快 """
    TARGET_ADD_SMALL_C_FEEL = 43
    """ 交互对象增加少量Ｃ快 """
    TARGET_ADD_SMALL_P_FEEL = 44
    """ 交互对象增加少量Ｐ快 """
    TARGET_ADD_SMALL_V_FEEL = 45
    """ 交互对象增加少量Ｖ快 """
    TARGET_ADD_SMALL_A_FEEL = 46
    """ 交互对象增加少量Ａ快 """
    TARGET_ADD_SMALL_U_FEEL = 47
    """ 交互对象增加少量Ｕ快 """
    TARGET_ADD_SMALL_W_FEEL = 48
    """ 交互对象增加少量Ｗ快 """
    TARGET_ADD_SMALL_LUBRICATION = 49
    """ 交互对象增加少量润滑（欲望补正） """
    TARGET_ADD_SMALL_LEARN = 51
    """ 交互对象增加少量习得（技巧补正） """
    TARGET_ADD_SMALL_RESPECT = 52
    """ 交互对象增加少量恭顺（顺从补正） """
    TARGET_ADD_SMALL_FRIENDLY = 53
    """ 交互对象增加少量好意（亲密补正） """
    TARGET_ADD_SMALL_DESIRE = 54
    """ 交互对象增加少量欲情（欲望补正） """
    TARGET_ADD_SMALL_HAPPY = 55
    """ 交互对象增加少量快乐（快乐刻印补正） """
    TARGET_ADD_SMALL_LEAD = 56
    """ 交互对象增加少量先导（侍奉补正） """
    TARGET_ADD_SMALL_SUBMIT = 57
    """ 交互对象增加少量屈服（屈服刻印补正） """
    TARGET_ADD_SMALL_SHY = 58
    """ 交互对象增加少量羞耻（露出补正） """
    TARGET_ADD_SMALL_PAIN = 59
    """ 交互对象增加少量苦痛（苦痛刻印补正） """
    TARGET_ADD_SMALL_TERROR = 60
    """ 交互对象增加少量恐怖（恐怖刻印补正） """
    TARGET_ADD_SMALL_DEPRESSION = 61
    """ 交互对象增加少量抑郁 """
    TARGET_ADD_SMALL_DISGUST = 62
    """ 交互对象增加少量反感（反发刻印补正） """
    ADD_SMALL_P_FEEL = 70
    """ 自身增加少量Ｐ快 """
    TALK_ADD_ADJUST = 100
    """ （聊天用）根据发起者的话术技能进行双方的好感度、好意、快乐调整，并记录当前谈话时间 """
    COFFEE_ADD_ADJUST = 101
    """ （泡咖啡用）根据发起者的料理技能进行好感度、信赖、好意调整 """
    EAT_FOOD = 102
    """ 进食指定食物 """
    MAKE_FOOD = 103
    """ 制作指定食物 """
    TECH_ADD_N_ADJUST = 110
    """ 根据发起者的技巧技能对交互对象进行N快、欲情调整 """
    TECH_ADD_B_ADJUST = 111
    """ 根据发起者的技巧技能对交互对象进行B快、欲情调整 """
    TECH_ADD_C_ADJUST = 112
    """ 根据发起者的技巧技能对交互对象进行C快、欲情调整 """
    TECH_ADD_P_ADJUST = 113
    """ 根据发起者的技巧技能对交互对象进行P快、欲情调整 """
    TECH_ADD_V_ADJUST = 114
    """ 根据发起者的技巧技能对交互对象进行V快、欲情调整 """
    TECH_ADD_A_ADJUST = 115
    """ 根据发起者的技巧技能对交互对象进行A快、欲情调整 """
    TECH_ADD_U_ADJUST = 116
    """ 根据发起者的技巧技能对交互对象进行U快、欲情调整 """
    TECH_ADD_W_ADJUST = 117
    """ 根据发起者的技巧技能对交互对象进行W快、欲情调整 """
    TECH_ADD_PL_P_ADJUST = 120
    """ 根据对交互对象的技巧技能对发起者进行P快调整 """
    TARGET_ADD_1_N_EXPERIENCE = 200
    """ 交互对象增加1N经验 """
    TARGET_ADD_1_B_EXPERIENCE = 201
    """ 交互对象增加1B经验 """
    TARGET_ADD_1_C_EXPERIENCE = 202
    """ 交互对象增加1C经验 """
    TARGET_ADD_1_P_EXPERIENCE = 203
    """ 交互对象增加1P经验 """
    TARGET_ADD_1_V_EXPERIENCE = 204
    """ 交互对象增加1V经验 """
    TARGET_ADD_1_A_EXPERIENCE = 205
    """ 交互对象增加1A经验 """
    TARGET_ADD_1_U_EXPERIENCE = 206
    """ 交互对象增加1U经验 """
    TARGET_ADD_1_W_EXPERIENCE = 207
    """ 交互对象增加1W经验 """
    TARGET_ADD_1_NClimax_EXPERIENCE = 210
    """ 交互对象增加1N绝顶经验 """
    TARGET_ADD_1_BClimax_EXPERIENCE = 211
    """ 交互对象增加1B绝顶经验 """
    TARGET_ADD_1_CClimax_EXPERIENCE = 212
    """ 交互对象增加1C绝顶经验 """
    TARGET_ADD_1_PClimax_EXPERIENCE = 213
    """ 交互对象增加1P绝顶经验 """
    TARGET_ADD_1_VClimax_EXPERIENCE = 214
    """ 交互对象增加1V绝顶经验 """
    TARGET_ADD_1_AClimax_EXPERIENCE = 215
    """ 交互对象增加1A绝顶经验 """
    TARGET_ADD_1_UClimax_EXPERIENCE = 216
    """ 交互对象增加1U绝顶经验 """
    TARGET_ADD_1_WClimax_EXPERIENCE = 217
    """ 交互对象增加1W绝顶经验 """
    TARGET_ADD_1_Climax_EXPERIENCE = 220
    """ 交互对象增加1绝顶经验 """
    TARGET_ADD_1_Cumming_EXPERIENCE = 221
    """ 交互对象增加1射精经验 """
    TARGET_ADD_1_Milking_EXPERIENCE = 222
    """ 交互对象增加1喷乳经验 """
    TARGET_ADD_1_Peeing_EXPERIENCE = 223
    """ 交互对象增加1放尿经验 """
    TARGET_ADD_1_Cums_EXPERIENCE = 224
    """ 交互对象增加1精液经验 """
    TARGET_ADD_1_CumsDrink_EXPERIENCE = 225
    """ 交互对象增加1饮精经验 """
    TARGET_ADD_1_Creampie_EXPERIENCE = 226
    """ 交互对象增加1膣射经验 """
    TARGET_ADD_1_AnalCums_EXPERIENCE = 227
    """ 交互对象增加1肛射经验 """
    TARGET_ADD_1_plServe_EXPERIENCE = 230
    """ 交互对象增加1奉仕快乐经验 """
    TARGET_ADD_1_Love_EXPERIENCE = 231
    """ 交互对象增加1爱情经验 """
    TARGET_ADD_1_plPain_EXPERIENCE = 232
    """ 交互对象增加1苦痛快乐经验 """
    TARGET_ADD_1_plSadism_EXPERIENCE = 233
    """ 交互对象增加1嗜虐快乐经验 """
    TARGET_ADD_1_plExhibit_EXPERIENCE = 234
    """ 交互对象增加1露出快乐经验 """
    TARGET_ADD_1_Kiss_EXPERIENCE = 240
    """ 交互对象增加1接吻经验 """
    TARGET_ADD_1_Handjob_EXPERIENCE = 241
    """ 交互对象增加1手淫经验 """
    TARGET_ADD_1_Blowjob_EXPERIENCE = 242
    """ 交互对象增加1口淫经验 """
    TARGET_ADD_1_Paizuri_EXPERIENCE = 243
    """ 交互对象增加1乳交经验 """
    TARGET_ADD_1_Footjob_EXPERIENCE = 244
    """ 交互对象增加1足交经验 """
    TARGET_ADD_1_Hairjob_EXPERIENCE = 245
    """ 交互对象增加1发交经验 """
    TARGET_ADD_1_Masterbate_EXPERIENCE = 246
    """ 交互对象增加1自慰经验 """
    TARGET_ADD_1_bdsmMasterbate_EXPERIENCE = 247
    """ 交互对象增加1调教自慰经验 """
    TARGET_ADD_1_Toys_EXPERIENCE = 248
    """ 交互对象增加1道具使用经验 """
    TARGET_ADD_1_Tiedup_EXPERIENCE = 249
    """ 交互对象增加1紧缚经验 """
    TARGET_ADD_1_Insert_EXPERIENCE = 250
    """ 交互对象增加1插入经验 """
    TARGET_ADD_1_sexV_EXPERIENCE = 251
    """ 交互对象增加1V性交经验 """
    TARGET_ADD_1_sexA_EXPERIENCE = 252
    """ 交互对象增加1A性交经验 """
    TARGET_ADD_1_sexU_EXPERIENCE = 253
    """ 交互对象增加1U性交经验 """
    TARGET_ADD_1_sexW_EXPERIENCE = 254
    """ 交互对象增加1W性交经验 """
    TARGET_ADD_1_expandV_EXPERIENCE = 255
    """ 交互对象增加1V扩张经验 """
    TARGET_ADD_1_expandA_EXPERIENCE = 256
    """ 交互对象增加1A扩张经验 """
    TARGET_ADD_1_expandU_EXPERIENCE = 257
    """ 交互对象增加1U扩张经验 """
    TARGET_ADD_1_expandW_EXPERIENCE = 258
    """ 交互对象增加1W扩张经验 """
    TARGET_ADD_1_TWRape_EXPERIENCE = 259
    """ 交互对象增加1时奸经验 """
    TARGET_ADD_1_SlumberRape_EXPERIENCE = 260
    """ 交互对象增加1睡奸经验 """
    TARGET_ADD_1_Abnormal_EXPERIENCE = 261
    """ 交互对象增加1异常经验 """
    TARGET_ADD_1_Axillajob_EXPERIENCE = 262
    """ 交互对象增加1腋交经验 """
    TARGET_ADD_1_UnconsciouslyN_EXPERIENCE = 270
    """ 交互对象增加1无意识N经验 """
    TARGET_ADD_1_UnconsciouslyB_EXPERIENCE = 271
    """ 交互对象增加1无意识B经验 """
    TARGET_ADD_1_UnconsciouslyC_EXPERIENCE = 272
    """ 交互对象增加1无意识C经验 """
    TARGET_ADD_1_UnconsciouslyP_EXPERIENCE = 273
    """ 交互对象增加1无意识P经验 """
    TARGET_ADD_1_UnconsciouslyV_EXPERIENCE = 274
    """ 交互对象增加1无意识V经验 """
    TARGET_ADD_1_UnconsciouslyA_EXPERIENCE = 275
    """ 交互对象增加1无意识A经验 """
    TARGET_ADD_1_UnconsciouslyU_EXPERIENCE = 276
    """ 交互对象增加1无意识U经验 """
    TARGET_ADD_1_UnconsciouslyW_EXPERIENCE = 277
    """ 交互对象增加1无意识W经验 """
    TARGET_ADD_1_UnconsciouslyClimax_EXPERIENCE = 278
    """ 交互对象增加1无意识绝顶经验 """
    TARGET_ADD_1_Chat_EXPERIENCE = 280
    """ 交互对象增加1对话经验 """
    TARGET_ADD_1_Combat_EXPERIENCE = 281
    """ 交互对象增加1战斗经验 """
    TARGET_ADD_1_Learn_EXPERIENCE = 282
    """ 交互对象增加1学习经验 """
    TARGET_ADD_1_Cooking_EXPERIENCE = 283
    """ 交互对象增加1料理经验 """
    TARGET_ADD_1_Date_EXPERIENCE = 284
    """ 交互对象增加1约会经验 """
    TARGET_ADD_1_Music_EXPERIENCE = 285
    """ 交互对象增加1音乐经验 """
    TARGET_ADD_1_GiveBirth_EXPERIENCE = 286
    """ 交互对象增加1妊娠经验 """
    TARGET_ADD_1_ForwardClimax_EXPERIENCE = 300
    """ 交互对象增加1正面位绝顶经验 """
    TARGET_ADD_1_BackClimax_EXPERIENCE = 301
    """ 交互对象增加1后入位绝顶经验 """
    TARGET_ADD_1_RideClimax_EXPERIENCE = 302
    """ 交互对象增加1骑乘位绝顶经验 """
    TARGET_ADD_1_FSeatClimax_EXPERIENCE = 303
    """ 交互对象增加1对面座位绝顶经验 """
    TARGET_ADD_1_BSeatClimax_EXPERIENCE = 304
    """ 交互对象增加1背面座位绝顶经验 """
    TARGET_ADD_1_FStandClimax_EXPERIENCE = 305
    """ 交互对象增加1对面立位绝顶经验 """
    TARGET_ADD_1_BStandClimax_EXPERIENCE = 306
    """ 交互对象增加1背面立位绝顶经验 """
    ADD_1_Kiss_EXPERIENCE = 307
    """ 增加1接吻经验 """
    ADD_1_Handjob_EXPERIENCE = 308
    """ 增加1手淫经验 """
    ADD_1_Blowjob_EXPERIENCE = 309
    """ 增加1口淫经验 """
    ADD_1_Paizuri_EXPERIENCE = 310
    """ 增加1乳交经验 """
    ADD_1_Footjob_EXPERIENCE = 311
    """ 增加1足交经验 """
    ADD_1_Hairjob_EXPERIENCE = 312
    """ 增加1发交经验 """
    ADD_1_Chat_EXPERIENCE = 313
    """ 增加1对话经验 """
    ADD_1_Combat_EXPERIENCE = 314
    """ 增加1战斗经验 """
    ADD_1_Learn_EXPERIENCE = 315
    """ 增加1学习经验 """
    ADD_1_Cooking_EXPERIENCE = 316
    """ 增加1料理经验 """
    ADD_1_Date_EXPERIENCE = 317
    """ 增加1约会经验 """
    ADD_1_Music_EXPERIENCE = 318
    """ 增加1音乐经验 """
    ADD_1_GiveBirth_EXPERIENCE = 319
    """ 增加1妊娠经验 """

#旧结算存档#
    # ADD_SOCIAL_FAVORABILITY = 7
    # """ 增加社交关系好感 """
    # ADD_INTIMACY_FAVORABILITY = 8
    # """ 增加亲密行为好感(关系不足2则增加反感) """
    # ADD_INTIMATE_FAVORABILITY = 9
    # """ 增加私密行为好感(关系不足3则增加反感) """


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
    #日常#
    WAIT = 0
    """ 等待五分钟 """
    CHAT = 0
    """ 聊天 """
    STROKE = 0
    """ 身体接触 """
    MAKE_COFFEE = 0
    """ 冲咖啡 """
    MAKE_COFFEE_ADD = 0
    """ 冲咖啡（加料） """
    MAKE_FOOD = 0
    """ 做饭 """
    EAT = 0
    """ 进食 """
    REST = 0
    """ 休息 """
    BUY_ITEM = 0
    """ 购买道具 """
    BUY_FOOD = 0
    """ 购买食物 """
    FOLLOW = 0
    """ 请求同行 """
    END_FOLLOW = 0
    """ 结束同行 """
    APOLOGIZE = 0
    """ 道歉 """
    LISTEN_COMPLAINT = 0
    """ 听牢骚 """
    PRAY = 0
    """ 祈愿 """
    COLLCET_PANTY = 0
    """ 收起内裤 """
    ASK_DATE = 0
    """ 邀请约会 """
    CONFESSION = 0
    """ 告白 """
    DRINK_ALCOHOL = 0
    """ 劝酒 """
    DO_H = 0
    """ 邀请H """
    STOP_H = 0
    """ H结束 """
    # SINGING = 0
    # """ 唱歌 """
    # PLAY_INSTRUMENT = 0
    # """ 演奏乐器 """
    #工作#
    OFFICIAL_WORK = 0
    """ 处理公务 """
    BATTLE_COMMAND = 0
    """ 指挥作战 """
    LISTEN_MISSION = 0
    """ 听取委托 """
    #猥亵#
    TOUCH_HEAD = 0
    """ 摸头 """
    TOUCH_BREAST = 0
    """ 摸胸 """
    TOUCH_BUTTOCKS = 0
    """ 摸屁股 """
    TOUCH_EARS = 0
    """ 摸耳朵 """
    TOUCH_HORN = 0
    """ 摸角 """
    TOUCH_TAIL = 0
    """ 摸尾巴 """
    TOUCH_RING = 0
    """ 摸光环 """
    TOUCH_WING = 0
    """ 摸光翼 """
    TOUCH_TENTACLE = 0
    """ 摸触手 """
    TOUCH_CAR = 0
    """ 摸小车 """
    HAND_IN_HAND = 0
    """ 牵手 """
    EMBRACE = 0
    """ 拥抱 """
    KISS = 0
    """ 亲吻 """
    LAP_PILLOW = 0
    """ 膝枕 """
    RAISE_SKIRT = 0
    """ 掀起裙子 """
    TOUCH_CLITORIS = 0
    """ 阴蒂爱抚 """
    TOUCH_VAGINA = 0
    """ 手指插入（V） """
    TOUCH_ANUS = 0
    """ 手指插入（A） """
    #性爱#
    MAKING_OUT = 0
    """ 身体爱抚 """
    KISS_H = 0
    """ 接吻 """
    BREAST_CARESS = 0
    """ 胸爱抚 """
    TWIDDLE_NIPPLES = 0
    """ 玩弄乳头 """
    BREAST_SUCKING = 0
    """ 舔吸乳头 """
    CLIT_CARESS = 0
    """ 阴蒂爱抚 """
    OPEN_LABIA = 0
    """ 掰开阴唇观察 """
    OPEN_ANUS = 0
    """ 掰开肛门观察 """
    CUNNILINGUS = 0
    """ 舔阴 """
    LICK_ANAL = 0
    """ 舔肛 """
    FINGER_INSERTION = 0
    """ 手指插入(V) """
    ANAL_CARESS = 0
    """ 手指插入(A) """
    MAKE_MASTUREBATE = 0
    """ 命令对方自慰 """
    MAKE_LICK_ANAL = 0
    """ 命令对方舔自己肛门 """
    DO_NOTHING = 0
    """ 什么也不做 """
    SEDECU = 0
    """ 诱惑 """
    HANDJOB = 0
    """ 手交 """
    BLOWJOB = 0
    """ 口交 """
    PAIZURI = 0
    """ 乳交 """
    FOOTJOB = 0
    """ 足交 """
    HAIRJOB = 0
    """ 发交 """
    AXILLAJOB = 0
    """ 腋交 """
    RUB_BUTTOCK = 0
    """ 素股 """
    HAND_BLOWJOB = 0
    """ 手交口交 """
    TITS_BLOWJOB = 0
    """ 乳交口交 """
    FOCUS_BLOWJOB = 0
    """ 真空口交 """
    DEEP_THROAT = 0
    """ 深喉插入 """
    SIXTY_NINE = 0
    """ 六九式 """
    BIRTH_CONTROL_PILLS = 0
    """ 避孕药 """
    BODY_LUBRICANT = 0
    """ 润滑液 """
    PHILTER = 0
    """ 媚药 """
    ENEMAS = 0
    """ 灌肠液 """
    DIURETICS = 0
    """ 利尿剂 """
    SLEEPING_PILLS = 0
    """ 睡眠药 """
    NIPPLE_CLAMP = 0
    """ 乳头夹 """
    NIPPLES_LOVE_EGG = 0
    """ 乳头跳蛋 """
    CLIT_CLAMP = 0
    """ 阴蒂夹 """
    CLIT_LOVE_EGG = 0
    """ 阴蒂跳蛋 """
    ELECTRIC_MESSAGE_STICK = 0
    """ 电动按摩棒 """
    VIBRATOR_INSERTION = 0
    """ 震动棒 """
    VIBRATOR_INSERTION_ANAL = 0
    """ 肛门振动棒 """
    MILKING_MACHINE = 0
    """ 搾乳机 """
    URINE_COLLECTOR = 0
    """ 采尿器 """
    BONDAGE = 0
    """ 绳子 """
    PATCH = 0
    """ 眼罩 """
    PUT_CONDOM = 0
    """ 避孕套 """
    NORMAL_SEX = 0
    """ 正常位 """
    BACK_SEX = 0
    """ 背后位 """
    RIDING_SEX = 0
    """ 骑乘位 """
    FACE_SEAT_SEX = 0
    """ 对面座位 """
    BACK_SEAT_SEX = 0
    """ 背面座位 """
    FACE_STAND_SEX = 0
    """ 对面立位 """
    BACK_STAND_SEX = 0
    """ 背面立位 """
    STIMULATE_G_POINT = 0
    """ 刺激G点 """
    WOMB_OS_CARESS = 0
    """ 玩弄子宫口 """
    WOMB_INSERTION = 0
    """ 插入子宫 """
    NORMAL_ANAL_SEX = 0
    """ 正常位肛交 """
    BACK_ANAL_SEX = 0
    """ 后背位肛交 """
    RIDING_ANAL_SEX = 0
    """ 骑乘位肛交 """
    FACE_SEAT_ANAL_SEX = 0
    """ 对面座位肛交 """
    BACK_SEAT_ANAL_SEX = 0
    """ 背面座位肛交 """
    FACE_STAND_ANAL_SEX = 0
    """ 对面立位肛交 """
    BACK_STAND_ANAL_SEX = 0
    """ 背面立位肛交 """
    STIMULATE_SIGMOID_COLON = 0
    """ 玩弄s状结肠 """
    STIMULATE_VAGINA = 0
    """ 隔着刺激阴道 """
    DOUBLE_PENETRATION = 0
    """ 二穴插入 """
    URETHRAL_SWAB = 0
    """ 尿道棉棒 """
    PISSING_PLAY = 0
    """ 放尿play """
    URETHRAL_INSERTION = 0
    """ 尿道插入 """
    BEAT_BREAST = 0
    """ 打胸部 """
    SPANKING = 0
    """ 打屁股 """
    SHAME_PLAY = 0
    """ 羞耻play """
    BUNDLED_PLAY = 0
    """ 拘束play """
    TAKE_SHOWER = 0
    """ 淋浴 """
    BUBBLE_BATH = 0
    """ 泡泡浴 """
    CHANGE_TOP_AND_BOTTOM = 0
    """ 交给对方 """
    GIVE_BLOWJOB = 0
    """ 给对方口交 """
    #系统#
    MOVE = 0
    """ 移动 """
    SLEEP = 0
    """ 睡觉 """
    SEE_ATTR = 0
    """ 查看属性 """
    SEE_OWNER_ATTR = 0
    """ 查看自身属性 """
    ITEM = 0
    """ 道具 """
    SAVE = 0
    """ 读写存档 """
    ABL_UP = 0
    """ 属性升级 """

    # ATTEND_CLASS = 0
    # """ 上课 """
    # TEACH_A_LESSON = 0
    # """ 教课 """
    # SELF_STUDY = 0
    # """ 自习 """
    # VIEW_THE_SCHOOL_TIMETABLE = 0
    # """ 查看课程表 """
    # COLLECTION_CHARACTER = 0
    # """ 收藏角色 """
    # UN_COLLECTION_CHARACTER = 0
    # """ 取消收藏 """
    # COLLECTION_SYSTEM = 0
    # """ 启用收藏模式 """
    # UN_COLLECTION_SYSTEM = 0
    # """ 关闭收藏模式 """
    # DRINK_SPRING = 0
    # """ 喝泉水 """
    # #娱乐#
    # PLAY_PIANO = 0
    # """ 弹钢琴 """
    # PLAY_GUITAR = 0
    # """ 弹吉他 """



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
