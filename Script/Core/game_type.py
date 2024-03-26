from uuid import UUID
from typing import List, Dict, Set, Tuple
import datetime


class FlowContorl:
    """流程控制用结构体"""

    restart_game: bool = 0
    """ 重启游戏 """
    quit_game: bool = 0
    """ 退出游戏 """


class WFrameMouse:
    """鼠标状态结构体"""

    w_frame_up: int = 2
    """ 逐字输出状态 """
    mouse_right: int = 0
    """ 鼠标右键按下 """
    w_frame_lines_up: int = 2
    """ 逐行输出状态 """
    mouse_leave_cmd: int = 1
    """ 鼠标左键事件 """
    w_frame_re_print: int = 0
    """ 再次载入游戏界面 """
    w_frame_lines_state: int = 2
    """ 逐行输出状态 """
    w_frame_mouse_next_line: int = 0
    """ 等待玩家确认后逐行 """
    w_frame_skip_wait_mouse: int = 0
    """ 跳过等待输入后继续输出文本 """


class NpcTem:
    """npc模板用结构体对象"""

    def __init__(self):
        self.Name: str = ""
        """ npc名字 """
        self.Sex: int = 0
        """ npc性别 """
        # self.Age: str = ""
        # """ npc年龄模板 """
        self.Position: List[int] = []
        """ npc出生位置(已废弃) """
        self.AdvNpc: int = 0
        """ 剧情npc校验 """
        # self.Weight: str = ""
        # """ 体重模板 """
        # self.BodyFat: str = ""
        # """ 体脂率模板 """
        # self.Chest: int = 0
        # """ 罩杯模板 """
        # 以下为新加
        self.Favorability: str = {}
        """ 好感度模板 """
        self.Trust: int = 0
        """ 信赖度模板 """
        self.Ability: Dict[int, int] = {}
        """ 能力预设 """
        self.Experience: Dict[int, int] = {}
        """ 经验预设 """
        self.Juel: Dict[int, int] = {}
        """ 宝珠预设 """
        self.Profession: int = 0
        """ 职业预设 """
        self.Race: int = 0
        """ 种族预设 """
        self.Nation: int = 0
        """ 势力预设 """
        self.Birthplace: int = 0
        """ 出生地预设 """
        self.Talent: Dict[int, int] = {}
        """ 素质预设 """
        self.Cloth: list = []
        """ 服装预设 """
        self.Hp: int = 0
        """ HP预设 """
        self.Mp: int = 0
        """ MP预设 """
        self.Mother_id: int = 0
        """ 母亲id """
        self.Dormitory: str = ""
        """ 宿舍预设 """
        self.Token: str = ""
        """ 信物预设 """
        self.Talk_Size: int = 0
        """ 口上大小 """
        self.TextColor: str = ""
        """ 文本颜色 """


# class Measurements:
#     """三围数据结构体"""

#     def __init__(self):
#         self.bust: float = 0
#         """ 胸围 """
#         self.waist: float = 0
#         """ 腰围 """
#         self.hip: float = 0
#         """ 臀围 """


# class Chest:
#     """胸围差数据结构体"""

#     def __init__(self):
#         self.target_chest: int = 0
#         """ 预期最终胸围差 """
#         self.now_chest: int = 0
#         """ 当前胸围差 """
#         self.sub_chest: int = 0
#         """ 每日胸围差增量 """


class Food:
    """食物数据结构体"""

    def __init__(self):
        self.id: str = ""
        """ 食物配置表id """
        self.name: str = ""
        """ 食物名字 """
        self.uid: UUID = None
        """ 食物对象的唯一id """
        self.quality: int = 0
        """ 食物品质 """
        # self.weight: int = 0
        # """ 食物重量 """
        # self.feel: dict = {}
        # """ 食物效果 """
        self.maker: str = ""
        """ 食物制作者 """
        self.recipe: int = -1
        """ 食谱id """
        self.special_seasoning: int = 0
        """ 调味类型 """
        self.special_seasoning_amount: int = 0
        """ 特殊调味的量 """
        # self.cook: bool = False
        # """ 可烹饪 """
        # self.eat: bool = False
        # """ 可食用 """
        self.drink: bool = False
        """ 可作为饮料 """
        # self.seasoning: bool = False
        # """ 可作为调料 """
        # self.fruit: bool = False
        # """ 是否是水果 """
        self.milk_ml: int = 0
        """ 牛奶毫升数 """


class Recipes:
    """菜谱数据结构体"""

    def __init__(self):
        self.name: str = ""
        """ 菜谱名字 """
        self.type: int = 0
        """ 菜的类型（0正餐1零食2饮品8加料咖啡9其他） """
        self.time: int = 0
        """ 标准烹饪时间 """
        self.difficulty: int = 0
        """ 烹饪难度 """
        self.money: int = 0
        """ 菜品价格 """
        self.introduce: str = ""
        """ 说明介绍 """
        # self.base: list = []
        # """ 烹饪所使用的主食材 """
        # self.ingredients: list = []
        # """ 烹饪所使用的辅食材 """
        # self.seasoning: list = []
        # """ 烹饪所使用的调料 """


class NormalConfig:
    """通用配置"""

    game_name: str
    """ 游戏名 """
    verson: str
    """ 游戏版本号 """
    author: str
    """ 作者名 """
    verson_time: str
    """ 版本时间 """
    debug: bool
    """ 是否开启debug模式 """
    background: str
    """ 背景色 """
    language: str
    """ 语言 """
    window_width: int
    """ 窗体宽度 """
    window_hight: int
    """ 窗体高度 """
    textbox_width: int
    """ 文本框字符宽度 """
    textbox_hight: int
    """ 文本框字符高度 """
    text_width: int
    """ 绘制用单行文本宽度 """
    text_hight: int
    """ 绘制用单屏行数 """
    inputbox_width: int
    """ 输入框宽度 """
    year: int
    """ 游戏时间开始年份 """
    month: int
    """ 游戏时间开始月份 """
    day: int
    """ 游戏时间开始日期 """
    hour: int
    """ 游戏时间开始小时数 """
    minute: int
    """ 游戏时间开始分钟数 """
    max_save: int
    """ 游戏存档数量上限 """
    save_page: int
    """ 存档显示页面单页存档数 """
    characterlist_show: int
    """ 角色列表单页显示角色数 """
    text_wait: int
    """ 步进文本等待时间 """
    home_url: str
    """ 开发者主页链接 """
    licenses_url: str
    """ 知识产权共享协议链接 """
    random_npc_max: int
    """ 最大随机npc数量 """
    insceneseeplayer_max: int
    """ 场景单页显示角色数上限 """
    seecharacterclothes_max: int
    """ 角色服装列表单页显示服装数上限 """
    seecharacterwearitem_max: int
    """ 角色可穿戴道具列表单页显示上限 """
    seecharacteritem_max: int
    """ 角色背包单页显示道具数上限 """
    food_shop_item_max: int
    """ 食物商店单页显示道具数上限 """
    food_shop_type_max: int
    """ 食物商店单页显示食物种类数上限 """
    font: str
    """ 字体 """
    font_size: int
    """ 字体大小 """
    order_font_size: int
    """ 输入框字体大小 """


# class Clothing:
#     """服装数据结构体"""

#     def __init__(self):
#         self.uid: UUID = ""
#         """ 服装对象的唯一id """
#         self.tem_id: int = 0
#         """ 服装配表id """
#         self.sexy: int = 0
#         """ 服装性感属性 """
#         self.handsome: int = 0
#         """ 服装帅气属性 """
#         self.elegant: int = 0
#         """ 服装典雅属性 """
#         self.fresh: int = 0
#         """ 服装清新属性 """
#         self.sweet: int = 0
#         """ 服装可爱属性 """
#         self.warm: int = 0
#         """ 服装保暖属性 """
#         self.cleanliness: int = 0
#         """ 服装清洁属性 """
#         self.price: int = 0
#         """ 服装价值属性 """
#         self.evaluation: str = ""
#         """ 服装评价文本 """
#         self.wear: int = 0
#         """ 穿戴部位 """


class DIRTY:
    """污浊情况数据结构体"""

    def __init__(self):
        # 人类正常一次射精量在2～6ml

        self.body_semen: list = []
        """ 身体精液情况    
        同身体部位，编号int:[0部位名str,1当前精液量int,2当前精液等级int,3总精液量int]    
        """
        self.cloth_semen: list = []
        """ 服装精液情况    
        同衣服类型，编号int:[0部位名str,1当前精液量int,2当前精液等级int,3总精液量int]    
        """
        self.cloth_locker_semen: list = []
        """ 衣柜里的服装精液情况    
        同衣服类型，编号int:[0部位名str,1当前精液量int,2当前精液等级int,3总精液量int]    
        """
        self.a_clean: int = 0
        """ A是否干净 [0脏污,1灌肠中,2已灌肠,3精液灌肠中,4已精液灌肠] """
        self.semen_flow: list = []
        """
        精液流通情况，每个子list都是一个字典，字典有源头和目标，所有目标都在一个列表内
        self.semen_flow = [
            {
                "source": {"type": "source_type1", "id": "source_id1"},
                "targets": [
                    {"type": "target_type1", "id": "target_id1", "remaining_volume": 10},
                    {"type": "target_type2", "id": "target_id2", "remaining_volume": 20},
                    # 更多的目标...
                ]
            },
            # 更多的流通...
        ]
        """


class PREGNANCY:
    """受精怀孕情况数据结构体"""

    def __init__(self):

        self.fertilization_rate: int = 0
        """ 受精概率 """
        self.reproduction_period: int = 0
        """ 生殖周期的第几天(0安全1普通2危险3排卵，0110232) """
        self.fertilization_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色开始受精的时间 """
        self.born_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色出生的时间 """
        self.milk: int = 0
        """ 角色当前乳汁量，单位毫升，每3分钟增加2毫升（平均4小时达到80%涨奶） """
        self.milk_max: int = 200
        """ 角色最大乳汁量，单位毫升 """


class RELATIONSHIP:
    """社交关系数据结构体"""

    def __init__(self):

        self.father_id: int = -1
        """ 父亲id """
        self.mother_id: int = -1
        """ 母亲id """
        self.child_id_list: List = []
        """ 孩子id列表 """
        self.firend_id_list: List = []
        """ 朋友id列表 """
        self.birthplace: int = 0
        """ 出生地 """
        self.nation: int = 0
        """ 势力 """


class HYPNOSIS:
    """催眠数据结构体"""

    def __init__(self):

        self.hypnosis_degree: int = 0
        """ 催眠程度 """



class CLOTH:

    # 鞋子比靴子低，前面的是帮，低帮在脚踝下，中帮脚踝一半，高帮盖过脚踝
    # 靴子低筒不过小腿肚，中筒过小腿肚，高筒过膝盖
    def __init__(self):
        self.clothing_tem: List = []
        """ 角色个人服装模板 编号"""
        self.cloth_wear: Dict[int, List] = {}
        """ 角色穿着的服装 部位:衣服id"""
        self.cloth_off: Dict[int, List] = {}
        """ 角色脱下的服装 部位:衣服id"""
        self.cloth_locker: Dict[int, List] = {}
        """ 角色放在衣柜里的服装 部位:衣服id"""
        self.cloth_see: Dict[int, bool] = {}
        """ 角色穿着的服装能否被看见 部位:能否"""


class BODY_H_STATE:
    """H状态结构体"""

    def __init__(self):
        self.body_item: list = []
        """ 身体道具情况    
        0~9共10项，编号int:[道具名str,当前有无bool,状态的结束时间datetime.datetime]    
        部位顺序 [0"乳头夹",1"阴蒂夹",2"V震动棒",3"A震动棒",4"搾乳机",5"采尿器",6"眼罩",7"肛门拉珠",8"持续性利尿剂",9"安眠药",10"排卵促进药",11"事前避孕药",12"事后避孕药"]
        """

        self.bondage: int = 0
        """ 绳子捆绑情况    
        0~9共10项，编号int    
        [0未捆绑,1后高手缚,2直立缚,3驷马捆绑,4直臂缚,5双手缚,6菱绳缚,7龟甲缚,8团缚,9逆团缚,10吊缚,11后手吊缚,12单足吊缚,13后手观音,14苏秦背剑,15五花大绑]
        """

        self.insert_position: int = -1
        """ 阴茎插入位置，int，-1为未插入，其他同身体部位 """
        self.shoot_position_body: int = -1
        """ 身体上的射精位置，int，-1为未射精，其他同身体部位 """
        self.shoot_position_cloth: int = -1
        """ 衣服上的射精位置，int，-1为未射精，其他同衣服部位 """
        self.orgasm_level: Dict[int, int] = {}
        """ 高潮程度记录，每3级一个循环，1为小绝顶，2为普绝顶，3为强绝顶 """
        self.orgasm_count: Dict[int, list] = {}
        """ 本次H里各部位的高潮次数计数，身体部位编号int:[当次计数int，总次计数int] """


class FIRST_RECORD:
    """初次状态记录结构体"""

    def __init__(self):
        self.first_meet: int = 1
        """ 第一次见面，1为未见面过，0为已见面过 """
        self.day_first_meet: int = 1
        """ 每天第一次见面，1为未见面过，0为已见面过 """
        self.first_hand_in_hand: int = -1
        """ 初次牵手对象 -1为无 """
        self.first_kiss_id: int = -1
        """ 初吻对象 -1为无 """
        self.first_kiss_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 初吻时间 """
        self.first_kiss_place: List[str] = ["0"]
        """ 初吻地点 """
        self.first_sex_id: int = -1
        """ 处女对象 -1为无 """
        self.first_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 处女时间 """
        self.first_sex_place: List[str] = ["0"]
        """ 处女地点 """
        self.first_sex_posture: str = ""
        """ 处女姿势 """
        self.first_sex_item: int = -1
        """ 处女道具 -1为无，0为手指，1为振动棒 """
        self.first_a_sex_id: int = -1
        """ A处女对象 -1为无 """
        self.first_a_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ A处女时间 """
        self.first_a_sex_place: List[str] = ["0"]
        """ A处女地点 """
        self.first_a_sex_posture: str = ""
        """ A处女姿势 """
        self.first_a_sex_item: int = -1
        """ A处女道具 -1为无，0为手指，1为振动棒 """


class ACTION_INFO:
    """角色的行动信息结构体"""

    def __init__(self):
        self.talk_count: int = 0
        """ 角色聊天次数计数器 """
        self.talk_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次聊天时间 """
        self.last_move_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次移动的时间 """
        self.last_training_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次训练的时间 """
        self.last_shower_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次淋浴的时间 """
        self.social_contact_last_time: Dict[int, datetime.datetime] = {}
        """ 指定角色最后与自己社交的时间 """
        self.sleep_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次睡觉时间 """
        self.plan_to_sleep_time: list = [18, 0]
        """ 角色计划睡觉的时间，[0时,1分] """
        self.wake_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色醒来时间 """
        self.social_contact_last_cut_down_time: Dict[int, datetime.datetime] = {}
        """ 指定角色上次扣除好感时间 """
        self.h_interrupt: int = 0
        """ 角色H被打断 """
        self.follow_wait_time: int = 0
        """ 无法进入私密场所的等待时间 """
        self.last_eaj_add_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 上次增加射精值的时间 """


class SPECIAL_FLAG:
    """特殊的flag"""

    def __init__(self):
        self.is_h: bool = 0
        """ 在H模式中 """
        self.unconscious_h: int = 0
        """ 在无意识H模式中，int [0否,1睡眠,2醉酒,3时停,4平然,5空气,6体控,7心控] """
        self.wait_flag: bool = 0
        """ AI行动里的原地发呆判定 """
        self.is_follow: int = 0
        """ 跟随玩家，int [0不跟随,1智能跟随,2强制跟随,3前往博士办公室,4前往博士当前位置] """
        self.tired: bool = 0
        """ 疲劳状态（HP=1） """
        self.angry_with_player: bool = 0
        """ 被玩家惹生气 """
        self.move_stop: bool = 0
        """ 角色停止移动 """
        self.be_bagged: bool = 0
        """ 被装袋搬走状态 """
        self.bagging_chara_id: int = 0
        """ 玩家正在装袋搬走的角色的id """
        self.imprisonment: bool = 0
        """ 被监禁状态 """
        self.sleep: bool = 0
        """ 要睡觉状态 """
        self.rest: bool = 0
        """ 要休息状态 """
        self.pee: bool = 0
        """ 要撒尿状态 """
        self.milk: bool = 0
        """ 要挤奶状态 """
        self.shower: int = 0
        """ 洗澡状态，int [0无,1要更衣,2要洗澡,3要披浴巾,4洗完澡] """
        self.eat_food: int = 0
        """ 吃饭状态，int [0无,1要取餐,2要吃饭] """
        self.find_food_weird: bool = 0
        """ 发现食物不对劲 """
        self.swim: int = 0
        """ 游泳状态，int [0无,1要换泳衣,2要游泳] """
        self.bathhouse_entertainment: int = 0
        """ 大浴场娱乐状态，int [0无,1要更衣,2要娱乐] """
        self.work_maintenance: bool = 0
        """ 要检修状态 """
        self.help_buy_food: int = 0
        """ 帮忙买饭状态，int [0无,1要买饭,2要买第二份饭,3要送饭] """
        self.help_make_food: int = 0
        """ 帮忙做饭状态，int [0无,1要做饭,2要送饭] """
        self.morning_salutation: int = 0
        """ 早安问候状态，int [0无,1要问候,2已问候] """
        self.night_salutation: int = 0
        """ 晚安问候状态，int [0无,1要问候,2已问候] """
        self.vistor: int = 0
        """ 访客状态，int [0无,1访问中,2访问过] """
        self.aromatherapy: int = 0
        """ 香薰疗愈状态，int [0无,1回复,2习得,3反感，4快感,5好感] """


class CHARA_WORK:
    """角色的工作信息结构体"""

    def __init__(self):
        self.work_type: int = 0
        """ 角色工作的类型 """
        self.recruit_index: int = -1
        """ 角色当前正在工作的招募位 """


class CHARA_ENTERTAINMENT:
    """角色的娱乐信息结构体"""

    def __init__(self):
        self.entertainment_type: list = [0,0,0]
        """ 角色娱乐活动的类型 """
        self.borrow_book_id_set: set = set()
        """ 借的书的id """
        self.book_return_possibility: int = 0
        """ 角色归还当前阅读书籍的可能性比例 """


class PLAYER_COLLECTION:
    """玩家收集品结构体"""

    def __init__(self):
        self.collection_bonus: Dict[int, bool] = {}
        """ 收藏品的解锁奖励 """
        self.token_list: Dict[int, bool] = {}
        """ 获得的NPC信物 """
        self.first_panties: Dict[int, str] = {}
        """ 获得的处子血胖次 """
        self.npc_panties: Dict[int, list] = {}
        """ 获得的角色胖次 """
        self.npc_panties_tem: Dict[int, list] = {}
        """ 临时获得的角色胖次 """
        self.npc_socks: Dict[int, list] = {}
        """ 获得的角色袜子 """
        self.npc_socks_tem: Dict[int, list] = {}
        """ 临时获得的角色袜子 """
        self.eqip_token: List = [0, [0]]
        """ 装备的信物 """


class PLAYER_ABILITY:
    """玩家能力结构体"""

    def __init__(self):
        self.follow_count: int = 1
        """ 最大同时跟随人数 """
        self.jj_size: int = 1
        """ 阴茎大小，0短小,1普通,2粗大,3巨根 """
        self.hormone: bool = False
        """ 激素系能力开关 """
        self.visual: bool = False
        """ 视觉系能力开关 """
        self.tactile: bool = False
        """ 触觉系能力开关 """
        self.today_sanity_point_cost: int = 0
        """ 今日已消耗的理智值 """
        self.hypnosis_type: int = 0
        """ 催眠类型 """


# class Height:
#     """身高数据结构体"""

#     def __init__(self):
#         self.now_height: float = 0
#         """ 当前身高 """
#         self.growth_height: float = 0
#         """ 每日身高增量 """
#         self.expect_age: int = 0
#         """ 预期结束身高增长年龄 """
#         self.development_age: int = 0
#         """ 预期发育期结束时间 """
#         self.expect_height: float = 0
#         """ 预期的最终身高 """


class Behavior:
    """角色行为状态数据"""

    def __init__(self):
        self.start_time: datetime.datetime = None
        """ 行为开始时间 """
        self.duration: int = 0
        """ 行为持续时间(单位分钟) """
        self.behavior_id: int = 0
        """ 行为id """
        self.move_target: List[str] = []
        """ 移动行为的目标坐标 """
        self.move_src: List[str] = []
        """ 移动行为的出发坐标 """
        self.move_final_target: List[str] = []
        """ 移动行为的最终目标坐标 """
        self.target_food: Food = None
        """ 行为的食物对象 """
        self.food_name: str = ""
        """ 前提结算用:进食行为消耗的食物名字 """
        self.food_quality: int = 0
        """ 前提结算用:进食行为消耗的食物品质 """
        self.make_food_time: int = 0
        """ 前提结算用:做饭指令用时 """
        self.food_seasoning: int = 0
        """ 前提结算用:食物调味类型 0正常，其他见Seasoning.csv """
        self.pan_name: str = ""
        """ 前提结算用:内裤名字 """
        self.socks_name: str = ""
        """ 前提结算用:袜子名字 """
        self.book_id: int = 0
        """ 前提结算用:书籍id """
        self.book_name: str = ""
        """ 前提结算用:书籍名字 """
        self.milk_ml: int = 0
        """ 前提结算用:榨出母乳的毫升数 """


class Chara_Event:
    """角色事件状态数据"""

    def __init__(self):
        self.event_id: str = ""
        """ 角色当前事件id """
        self.son_event_id: str = ""
        """ 角色当前子事件id """


class Map:
    """地图数据"""

    def __init__(self):
        self.map_path: str = ""
        """ 地图路径 """
        self.map_name: str = ""
        """ 地图名字 """
        self.path_edge: Dict[str, Dict[str, int]] = {}
        """
        地图下场景通行路径
        场景id:可直达场景id:移动所需时间
        """
        self.map_draw: MapDraw = MapDraw()
        """ 地图绘制数据 """
        self.sorted_path: Dict[str, Dict[str, TargetPath]] = {}
        """
        地图下场景间寻路路径
        当前节点:目标节点:路径对象
        """


class MapDraw:
    """地图绘制数据"""

    def __init__(self):
        self.draw_text: List[MapDrawLine] = []
        """ 绘制行对象列表 """


class MapDrawLine:
    """地图绘制行数据"""

    def __init__(self):
        self.width: int = 0
        """ 总行宽 """
        self.draw_list: List[MapDrawText] = []
        """ 绘制的对象列表 """


class MapDrawText:
    """地图绘制文本数据"""

    def __init__(self):
        self.text: str = ""
        """ 要绘制的文本 """
        self.is_button: bool = 0
        """ 是否是场景按钮 """
        self.style: str = ""
        """ 绘制的样式 """


class TargetPath:
    """寻路目标路径数据"""

    def __init__(self):
        self.path: List[str] = []
        """ 寻路路径节点列表 """
        self.time: List[int] = []
        """ 移动所需时间列表 """


class Scene:
    """场景数据"""

    def __init__(self):
        self.scene_path: str = ""
        """ 场景路径 """
        self.scene_name: str = ""
        """ 场景名字 """
        self.in_door: bool = 0
        """ 在室内 """
        self.exposed: bool = 0
        """ 地点暴露 """
        self.have_furniture: int = 0
        """ 有家具(1基础家具,2办公机家具,3卧室级家具) """
        self.close_type: int = 0
        """ 关门类型(0无法关门,1正常关门,2小隔间关门) """
        self.close_flag: int = 0
        """ 关门状态 """
        self.scene_tag: list = []
        """ 场景标签 """
        self.character_list: set = set()
        """ 场景内角色列表 """


class Rhodes_Island:
    """罗德岛相关属性"""

    def __init__(self):
        self.facility_level: Dict[int, Tuple[int]] = {}
        """ 基地当前所有设施的等级 """
        self.facility_open: Dict[int, Tuple[bool]] = {}
        """ 基地当前所有待开放设施的开放情况 """
        self.all_work_npc_set: Dict[int, Tuple[set]] = {}
        """ 所有工作的所属的干员id合集,工作id:干员id的集合 """
        self.work_people_now: int = 0
        """ 当前工作干员人数 """
        self.people_max: int = 0
        """ 干员人数上限 """
        self.all_income: int = 0
        """ 今日全部门总收入 """
        self.party_day_of_week: Dict[int, Tuple[int]] = {}
        """ 一周内的派对计划，周一0~周日6:娱乐id """

        # 控制中枢
        self.current_location: List[int] = []
        """ 基地当前所在位置，[0国家id,1城市id] """
        self.office_work: int = 0
        """ 需要处理的公务 """
        self.effectiveness: int = 0
        """ 基地效率 """

        # 动力区
        self.power_use: int = 0
        """ 当前使用电力 """
        self.power_max: int = 0
        """ 总可用电力 """

        # 工程部
        self.maintenance_place: Dict[int, Tuple[str]] = {}
        """ 当前每个角色的待检修地点，角色id:地点 """

        # 生活娱乐区
        self.life_zone_max: int = 0
        """ 生活娱乐区设施数量上限 """
        self.milk_in_fridge: Dict[int, Tuple[int]] = {}
        """ 冰箱里每个干员的当日母乳存量，干员id:母乳ml存量 """

        # 医疗部
        self.patient_now: int = 0
        """ 当前患者人数 """
        self.patient_cured: int = 0
        """ 当前已治疗患者人数 """
        self.patient_max: int = 0
        """ 患者人数上限 """
        self.cure_income: int = 0
        """ 今日总治疗收入 """
        self.patient_cured_all: int = 0
        """ 已治疗的患者总人数 """
        self.cure_income_all: int = 0
        """ 至今为止的治疗总收入 """

        # 文职区
        self.recruit_line: Dict[int, Tuple[float, int ,set, float]] = {}
        """ 当前招募进度 招募线id:[0招募进度, 1招募类型id, 2负责该线的干员id集合, 3招募效率百分比(如2.5)] """
        self.recruited_id: Set = set()
        """ 已招募待确认的干员id """

        # 训练场

        # 图书档案区
        self.book_borrow_dict: Dict[int, Tuple[int]] = {}
        """ 书籍借出情况 书籍id:借出人id(-1为未借出) """
        self.reader_now: int = 0
        """ 当前图书馆中的读者数量 """
        self.recommend_book_type_set: Set = set()
        """ 推荐的阅读类别 """

        # 制造加工区
        self.assembly_line: Dict[int, Tuple[int, set, int ,int]] = {}
        """ 流水线情况 流水线id:[0生产类型id, 1负责该线的干员id集合, 2总效率百分比(如110), 3明日要变成的新生产类型, 4上次收菜的小时] """

        # 访客区
        self.visitor_max: int = 0
        """ 访客人数上限 """
        self.base_move_visitor_flag: bool = False
        """ 因为基地移动而吸引访客 """
        self.visitor_info: Dict[int, Tuple[datetime.datetime]] = {}
        """ 访客统计数据 访客id:[0停留开始时间] """
        self.last_visitor_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 上次访客到来时间 """
        self.invite_visitor: List[int, float, float] = {}
        """ 当前邀请进度 [0目标角色id, 1招募进度, 2招募效率百分比(如2.5)] """

        # 教育区

        # 疗养庭院
        self.herb_garden_line: Dict[int, Tuple[int, set, int]] = {}
        """ 药田生产情况 流水线id:[0生产类型id, 1负责该线的干员id集合, 2总效率百分比(如110), 3明日要变成的新生产类型, 4上次收菜的小时] """
        self.green_house_line: Dict[int, Tuple[int, set, int]] = {}
        """ 温室生产情况 流水线id:[0生产类型id, 1负责该线的干员id集合, 2总效率百分比(如110), 3明日要变成的新生产类型, 4上次收菜的小时] """
        self.remaining_aromatherapy_sessions_today: int = 0
        """ 今日剩余调香次数 """

        self.research_zone_max: int = 0
        """ 科研区设施数量上限 """
        self.shop_max: int = 0
        """ 商店数量上限 """
        self.soldier_max: int = 0
        """ 战斗时干员数量上限 """

        self.money: int = 0
        """ 龙门币数量 """
        self.orundum: int = 0
        """ 合成玉数量 """
        self.Originite_Prime: int = 0
        """ 至纯源石数量 """
        self.pink_certificate: int = 0
        """ 粉红凭证数量 """

        self.total_favorability_increased: int = 0
        """ 每日总好感度提升 """
        self.total_semen_count: int = 0
        """ 每日总射精量 """

        self.warehouse_capacity: int = 0
        """ 仓库容量 """
        self.materials_resouce: Dict[int, Tuple[int]] = {}
        """ 素材资源 """


'''

        self.daily_necessities : int = 0
        """ 生活必需品数量 """
        self.common_medicinal_materials : int = 0
        """ 普通药材数量 """
        self.special_medicinal_materials : int = 0
        """ 矿石病药材数量 """
        self.industrial_raw_materials : int = 0
        """ 工业原材料数量 """
        self.building_materials : int = 0
        """ 碳素建材数量 """
        self.machine_parts : int = 0
        """ 机械零部件数量 """

        self.analgesic : int = 0
        """ 矿石病镇痛剂数量 """
        self.inhibitor_S : int = 0
        """ 感染抑制剂小样数量 """
        self.inhibitor_M : int = 0
        """ 感染抑制合剂数量 """
        self.inhibitor_L : int = 0
        """ 感染抑制剂浓缩液数量 """
'''

class System_Setting:
    """系统设置"""

    def __init__(self):
        self.line_before_main_update: int = 3
        """ 主界面刷新前的行数 """
        self.pl_ability_auto_lvup: bool = False
        """ 是否自动升级玩家的能力 """
        self.npc_ability_auto_lvup: bool = True
        """ 是否自动升级NPC的能力 """
        self.choose_shoot_where: bool = False
        """ 每次射精时手动选择射在哪里 """
        self.dr_need_pee: bool = False
        """ 博士需要尿尿 """
        self.urinate_grow_speed: int = 2
        """ 尿意值的增长速度，0不增长，1为8h增长到最大，2为4h增长到最大，3为2h增长到最大 """
        self.semen_flow: bool = True
        """ 是否开关精液流通功能 """
        self.all_chara_use_common_text: bool = True
        """ 所有角色使用通用文本 """


class Character:
    """角色数据结构体"""

    def __init__(self):
        self.cid: int = 0
        """ 角色id """
        self.name: str = ""
        """ 角色名字 """
        self.nick_name: str = ""
        """ 他人对角色的称呼 """
        self.sex: int = 0
        """ 角色性别 """
        # self.age: int = 18
        # """ 角色年龄 """
        self.hit_point_max: int = 0
        """ 角色最大HP """
        self.hit_point: int = 0
        """ 角色当前HP """
        self.mana_point_max: int = 0
        """ 角色最大MP """
        self.mana_point: int = 0
        """ 角色当前MP """
        self.sanity_point_max: int = 0
        """ 角色最大理智 """
        self.sanity_point: int = 0
        """ 角色当前理智 """
        self.eja_point_max: int = 0
        """ 角色最大射精槽 """
        self.eja_point: int = 0
        """ 角色当前射精槽 """
        self.semen_point_max: int = 0
        """ 角色最大精液槽 """
        self.semen_point: int = 0
        """ 角色当前精液槽 """
        self.tem_extra_semen_point: int = 0
        """ 角色临时最大精液槽 """
        self.angry_point: int = 0
        """ 角色当前愤怒槽 """
        self.tired_point: int = 0
        """ 疲劳值 6m=1点，16h=160点(max)"""
        self.urinate_point: int = 0
        """ 尿意值 1m=1点，4h=240点(max)"""
        self.hunger_point: int = 0
        """ 饥饿值 1m=1点，4h=240点(max)"""
        self.sleep_point: int = 0
        """ 熟睡值 1m=10点，10min=100点(max)"""
        self.state: int = 0
        """ 角色当前状态 """
        self.last_state: List = [0]
        """ 角色之前的状态 """
        self.talk_size: int = 0
        """ 角色口上大小，单位kb """
        self.text_color: str = ""
        """ 角色对话文本颜色 """
        # self.clothing: Dict[int, Dict[UUID, Clothing]] = {}
        # """
        # 角色拥有的服装数据
        # 服装穿戴位置:服装唯一id:服装数据
        # """
        # self.clothing_data: Dict[int, Set] = {}
        # """
        # 角色拥有的服装类型数据集合
        # 服装表id:服装唯一id
        # """
        # self.put_on: Dict[int, UUID] = {}
        # """
        # 角色已穿戴服装数据
        # 穿着类型:服装id
        # """
        # self.item: Set = set()
        # """ 旧：角色拥有的道具id集合 """
        self.item: Dict[int, int] = {}
        """ 角色拥有的道具 道具序号:数量"""
        # self.height: Height = Height()
        # """ 角色的身高数据 """
        # self.measurements: Measurements = Measurements()
        # """ 角色的三围数据 """
        self.cloth: CLOTH = CLOTH()
        """ 角色的衣服数据 """
        self.behavior: Behavior = Behavior()
        """ 角色当前行为状态数据 """
        self.second_behavior: Dict[int, int] = {}
        """ 角色当前二段行为状态数据 """
        self.event: Chara_Event = Chara_Event()
        """ 角色当前事件状态数据 """
        # self.gold: int = 0
        # """ 角色所持金钱数据 """
        self.position: List[str] = ["0", "0"]
        """ 角色当前坐标数据 """
        self.officeroom: List[str] = []
        """ 角色所属办公室坐标 """
        self.dormitory: str = ""
        """ 角色宿舍坐标 """
        self.pre_dormitory: str = ""
        """ 角色前宿舍坐标 """
        self.birthday: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色生日数据 """
        # self.chest_tem: int = 0
        # """ 角色罩杯模板 """
        self.status_data: Dict[int, int] = {}
        """ 角色状态数据 状态id:状态数值 """
        self.hit_point_tem: int = 1
        """ 角色HP模板 """
        self.mana_point_tem: int = 1
        """ 角色MP模板 """
        # self.social_contact: Dict[int, Set] = {}
        # """ 角色社交关系数据 关系类型:角色id集合 """
        # self.social_contact_data: Dict[int, int] = {}
        # """ 角色社交关系数据 角色id:关系类型 """
        self.favorability: Dict[int, int] = {}
        """ 角色好感度数据 角色id:好感度 """
        self.trust: int = 0
        """ 角色信赖度数据 """
        self.food_bag: Dict[UUID, Food] = {}
        """ 角色持有的食物数据 """
        self.target_character_id: int = 0
        """ 角色当前交互对象id """
        self.adv: int = 0
        """ 剧情npc校验 """
        # self.no_wear: bool = 0
        # """ 是否不想穿衣服 """
        self.dead: bool = 0
        """ 角色已死亡 """
        self.collection_character: Set = set()
        """ 收藏的角色列表 """
        self.last_hunger_time: datetime.datetime = None
        """ 最后一次结算饥饿的时间 """
        self.ability: Dict[int, int] = {}
        """ 角色能力 """
        self.experience: Dict[int, int] = {}
        """ 角色经验 """
        self.juel: Dict[int, int] = {}
        """ 角色宝珠 """
        self.profession: int = 0
        """ 角色职业 """
        self.race: int = 0
        """ 角色种族 """
        self.talent: Dict[int, int] = {}
        """ 角色素质 """
        self.token_text: str = ""
        """ 角色信物文本 """
        self.assistant_character_id: int = 0
        """ 助理角色id """
        self.chara_setting: Dict[int, int] = {}
        """ 角色的个人设置 """
        self.assistant_services: Dict[int, int] = {}
        """ 角色作为助理的情况 """
        self.first_record: FIRST_RECORD = FIRST_RECORD()
        """ 角色初次状态记录 """
        self.dirty: DIRTY = DIRTY()
        """ 角色身上污浊的情况 """
        self.h_state: BODY_H_STATE = BODY_H_STATE()
        """ 角色本次H的情况 """
        self.pl_ability: PLAYER_ABILITY = PLAYER_ABILITY()
        """ 玩家的特殊能力 """
        self.pl_collection: PLAYER_COLLECTION = PLAYER_COLLECTION()
        """ 玩家的收藏品 """
        self.sp_flag: SPECIAL_FLAG = SPECIAL_FLAG()
        """ 特殊flag """
        self.action_info: ACTION_INFO = ACTION_INFO()
        """ 角色的行动记录 """
        self.work: CHARA_WORK = CHARA_WORK()
        """ 角色的工作情况 """
        self.entertainment: CHARA_ENTERTAINMENT = CHARA_ENTERTAINMENT()
        """ 角色的娱乐情况 """
        self.pregnancy: PREGNANCY = PREGNANCY()
        """ 角色的怀孕情况 """
        self.relationship: RELATIONSHIP = RELATIONSHIP()
        """ 角色的社会关系 """
        self.hypnosis: HYPNOSIS = HYPNOSIS()
        """ 角色的催眠情况 """


class Cache:
    """游戏缓存数据结构体"""

    def __init__(self):
        self.back_save_panel: bool = 0
        """ 退出存档面板 """
        self.wframe_mouse: WFrameMouse = WFrameMouse()
        """ 主页监听控制流程用变量组 """
        self.character_data: Dict[int, Character] = {}
        """ 角色对象数据缓存组 """
        self.npc_tem_data: List[NpcTem] = []
        """ npc模板列表 """
        self.npc_id_got: Set = set()
        """ 已拥有的干员id数据 """
        self.input_cache: List[str] = []
        """ 玩家指令输入记录（最大20）"""
        self.now_init_map_id: str = ""
        """ 寻路算法用,当前节点所属的地图的id """
        self.collect_position_list: List = []
        """ 收藏地点合集 """
        self.input_position: int = 0
        """ 回溯输入记录用定位 """
        self.instruct_type_filter: Dict[int, bool] = {}
        """ 玩家操作指令面板指令过滤状态数据 指令类型:是否展示"""
        self.instruct_type_filter_cache: Dict[int, bool] = {}
        """ 玩家操作指令面板指令过滤状态数据_的缓存 指令类型:是否展示"""
        self.instruct_index_filter: Dict[int, bool] = {}
        """ 玩家各编号指令过滤状态数据 指令编号:是否展示"""
        self.output_text_style: str = ""
        """ 富文本记录输出样式临时缓存 """
        self.text_style_position: int = 0
        """ 富文本回溯样式记录用定位 """
        # self.clothing_type_data: dict = {}
        # """ 存储服装类型数据 """
        self.text_style_cache: List[str] = []
        """ 富文本样式记录 """
        self.text_one_by_one_rich_cache: dict = {}
        """ 富文本精确样式记录 """
        self.image_id: int = 0
        """ 图片id """
        self.cmd_data: dict = {}
        """ cmd数据 """
        self.game_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 游戏时间 """
        self.pre_game_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 前一循环时的游戏时间 """
        self.now_panel_id: int = 0
        """ 当前游戏面板id """
        self.old_character_id: int = 0
        """ 离开场景面板前在场景中查看的角色id """
        self.npc_image_index: int = 0
        """ 当前绘制人物列表的开始值 """
        self.text_wait: int = 0
        """ 绘制文本输出等待时间 """
        self.scene_panel_show: List = [True, True, True, True, True]
        """ 场景面板中的子面板显示情况,0状态,1服装,2身体,3暂无,4图片 """
        self.map_data: Dict[str, Map] = {}
        """ 游戏地图数据 地图路径:地图数据 """
        self.scene_data: Dict[str, Scene] = {}
        """ 游戏场景数据 场景路径:场景数据 """
        self.random_npc_list: List[NpcTem] = []
        """ 随机npc数据 """
        # self.wear_item_type_data: dict = {}
        # """ 可穿戴道具类型数据 """
        self.over_behavior_character: Set = set()
        """ 本次update中已结束结算的npc """
        self.recipe_data: Dict[int, Recipes] = {}
        """ 菜谱数据 """
        self.restaurant_data: Dict[str, Dict[UUID, Food]] = {}
        """
        食堂内贩卖的食物数据
        食物名字:食物唯一id:食物对象
        """
        self.makefood_data: Dict[str, Dict[UUID, Food]] = {}
        """
        做饭区的食物数据
        食物名字:食物唯一id:食物对象
        """
        self.npc_name_data: Set = set()
        """ 已有的npc姓名集合 """
        self.is_collection: bool = 0
        """ 启用收藏模式 """
        self.sun_phase: Dict[str, Dict[int, Dict[int, int]]] = {}
        """ 指定日期下每分钟太阳位置 日期:时:分:位置id """
        self.moon_phase: Dict[str, int] = {}
        """ 指定日期月相记录 日期:月相id """
        self.shoot_position: int = 0
        """ 记录射精位置 """
        self.debug_mode: bool = False
        """ 是否开启debug模式 """
        self.game_round: int = 1
        """ 当前周目数 """
        self.rhodes_island: Rhodes_Island = Rhodes_Island
        """ 罗德岛相关属性 """
        self.first_bonus: Dict[int, int] = {}
        """ 初期奖励 """
        self.world_setting: Dict[int, int] = {}
        """ 世界设定 """
        # self.system_setting: System_Setting = System_Setting()
        self.system_setting: Dict[int, int] = {}
        """ 系统设定，见System_Setting.csv """

class TargetChange:
    """交互对象角色变化结构体"""

    def __init__(self):
        self.hit_point: int = 0
        """ hp变化 """
        self.mana_point: int = 0
        """ mp变化 """
        self.eja_point: int = 0
        """ 射精变化 """
        self.status_data: Dict[int, int] = {}
        """ 状态变化 """
        self.favorability: int = 0
        """ 好感度变化 """
        self.trust: int = 0
        """ 信赖度变化 """
        self.target_change: Dict[int, TargetChange] = {}
        """ 互动目标状态变化 """
        self.ability: Dict[int, int] = {}
        """ 能力变化 """
        self.experience: Dict[int, int] = {}
        """ 经验变化 """
        self.sanity_point: int = 0
        """ 理智变化 """
        self.hypnosis_degree: int = 0
        """ 催眠程度变化 """


class CharacterStatusChange:
    """角色属性状态变更结构体"""

    def __init__(self):
        self.hit_point: int = 0
        """ hp变化 """
        self.mana_point: int = 0
        """ mp变化 """
        self.eja_point: int = 0
        """ 射精变化 """
        self.status_data: Dict[int, int] = {}
        """ 状态变化 """
        self.favorability: int = 0
        """ 好感度变化 """
        self.trust: int = 0
        """ 信赖度变化 """
        self.language: Dict[int, int] = {}
        """ 语言技能经验变化 """
        self.knowledge: Dict[int, int] = {}
        """ 知识技能经验变化 """
        self.target_change: Dict[int, TargetChange] = {}
        """ 互动目标状态变化 """
        self.sex_experience: Dict[int, int] = {}
        """ 性经验变化 """
        self.ability: Dict[int, int] = {}
        """ 能力变化 """
        self.experience: Dict[int, int] = {}
        """ 经验变化 """
        self.sanity_point: int = 0
        """ 理智变化 """
        self.hypnosis_degree: int = 0
        """ 催眠程度变化 """


class Event:
    """事件数据结构体"""

    def __init__(self):
        """初始化事件对象"""
        self.uid: str = ""
        """ 事件唯一id """
        self.adv_id: str = ""
        """ 事件所属advnpcid """
        self.status_id: str = ""
        """ 事件所属状态id """
        self.start: bool = 0
        """ 是否是行为开始时的事件 """
        self.type: int = 1
        """ 事件类型(0不进行指令结算，1正常) """
        self.text: str = ""
        """ 事件文本 """
        self.premise: dict = {}
        """ 事件的前提集合 """
        self.settle: dict = {}
        """ 事件的结算器集合 """
        self.effect: dict = {}
        """ 事件的结算集合 """


class Target:
    """目标数据结构体"""

    def __init__(self):
        """初始化口上对象"""
        self.uid: str = ""
        """ 目标唯一id """
        self.text: str = ""
        """ 目标描述 """
        self.state_machine_id: str = ""
        """ 执行的状态机id """
        self.premise: dict = {}
        """ 目标的前提集合 """
        self.effect: dict = {}
        """ 目标的效果集合 """
