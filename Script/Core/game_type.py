import uuid
from uuid import UUID
from typing import List, Dict, Set, Tuple, Any
import datetime


class FlowContorl:
    """流程控制用结构体"""

    restart_game: bool = False
    """ 重启游戏 """
    quit_game: bool = False
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
        self.Favorability: Dict[int, int] = {0:0}
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
        self.uid: UUID = uuid.uuid4()
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
        self.urine_ml: int = 0
        """ 圣水的毫升数 """


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
    web_draw: bool
    """ 是否开启Web绘制 """
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
    text_wait: int
    """ 步进文本等待时间 """
    home_url: str
    """ 开发者主页链接 """
    licenses_url: str
    """ 知识产权共享协议链接 """
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

        self.body_semen: dict = {}
        """ 身体精液情况    
        同身体部位，编号int:[0部位名str,1当前精液量int,2当前精液等级int,3总精液量int]    
        """
        self.cloth_semen: dict = {}
        """ 服装精液情况    
        同衣服类型，编号int:[0部位名str,1当前精液量int,2当前精液等级int,3总精液量int]    
        """
        self.cloth_locker_semen: dict = {}
        """ 衣柜里的服装精液情况    
        同衣服类型，编号int:[0部位名str,1当前精液量int,2当前精液等级int,3总精液量int]    
        """
        self.body_semen_in_unconscious: list = []
        """ 无意识中的身体精液情况，同身体部位，编号int """
        self.cloth_semen_in_unconscious: list = []
        """ 无意识中的服装精液情况，同服装类型，编号int """
        self.a_clean: int = 0
        """ A是否干净 [0脏污,1灌肠中,2已灌肠,3精液灌肠中,4已精液灌肠] """
        self.enema_capacity: int = 0
        """ 灌肠容量，int，0为未灌肠，1少2中3大4巨5极 """
        self.semen_flow: list = []
        """
        精液流通情况，每个元素都是一个字典，字典有源头和目标，每个源头可能有多个目标
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
        self.penis_dirty_dict: dict = {}
        """ 阴茎的污浊属性 [semen精液, blood处子血] """
        self.absorbed_total_semen: int = 0
        """ 累计吸收的精液总量，int类 """


class PREGNANCY:
    """受精怀孕情况数据结构体"""

    def __init__(self):

        self.fertilization_rate: float = 0
        """ 受精概率 """
        self.reproduction_period: int = 0
        """ 生殖周期的第几天(0安全1普通2危险3排卵，0011232) """
        self.fertilization_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色开始受精的时间 """
        self.born_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色出生的时间 """
        self.milk: int = 0
        """ 角色当前乳汁量，单位毫升，每3分钟增加2毫升（平均4小时达到80%涨奶） """
        self.milk_max: int = 200
        """ 角色最大乳汁量，单位毫升 """
        self.unconscious_fertilization: bool = True
        """ 无意识妊娠flag，如果进行过有意识下的H就会被置为False """
        self.lactation_flag: bool = False
        """ 涨奶标记 """


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

        self.hypnosis_degree: float = 0
        """ 催眠程度 """
        self.increase_body_sensitivity: bool = False
        """ 体控-敏感度提升 """
        self.force_ovulation: bool = False
        """ 体控-强制排卵 """
        self.blockhead: bool = False
        """ 体控-木头人 """
        self.active_h: bool = False
        """ 体控-逆推 """
        self.roleplay: list = []
        """ 心控-角色扮演，空为无，其他见Roleplay.csv """
        self.pain_as_pleasure: bool = False
        """ 心控-苦痛快感化 """


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
        self.cloth_locker_in_shower: Dict[int, List] = {}
        """ 角色放在大浴场衣柜里的服装 部位:衣服id"""
        self.cloth_locker_in_dormitory: Dict[int, List] = {}
        """ 角色放在宿舍衣柜里的服装 部位:衣服id"""
        self.cloth_see: Dict[int, bool] = {}
        """ 角色穿着的服装能否被看见 部位:能否"""
        self.stolen_panties_in_unconscious: bool = False
        """ 角色在无意识中被偷走了内裤 """
        self.stolen_socks_in_unconscious: bool = False
        """ 角色在无意识中被偷走了袜子 """
        self.equipment_condition: float = 0
        """ 角色装备情况，见对应csv文件 """

class BODY_H_STATE:
    """H状态结构体"""

    def __init__(self):
        self.body_item: dict = {}
        """ 身体道具情况    
        编号int:[道具名str,当前有无bool,状态的结束时间datetime.datetime]    
        部位顺序 [0"乳头夹",1"阴蒂夹",2"V震动棒",3"A震动棒",4"搾乳机",5"采尿器",6"眼罩",7"肛门拉珠",8"持续性利尿剂",9"安眠药",10"排卵促进药",11"事前避孕药",12"事后避孕药",13"避孕套",14"口球"]
        """

        self.bondage: int = 0
        """ 绳子捆绑情况，int，见bondage.csv，0为无捆绑 """

        self.group_sex_body_template_dict: dict = {
            "A":[
                {
                    "mouth": [-1, -1],
                    "L_hand": [-1, -1],
                    "R_hand": [-1, -1],
                    "penis": [-1, -1],
                    "anal": [-1, -1],
                },
                [[-1], -1],
            ],
            "B":[
                {
                    "mouth": [-1, -1],
                    "L_hand": [-1, -1],
                    "R_hand": [-1, -1],
                    "penis": [-1, -1],
                    "anal": [-1, -1],
                },
                [[-1], -1],
            ],
        }
        """
        群交模式下的部位模板\n 
        分为模板A和模板B\n
        模板为列表，0为全对单部位，1为阴茎侍奉\n
        对单部位为 mouth L_hand R_hand penis anal 以上各字典部位\n
        每个字典部位为列表，0为交互对象id，1为指令状态id\n
        阴茎侍奉为列表，0为全交互对象id列表，1为指令状态id
        """

        self.insert_position: int = -1
        """ 阴茎插入位置，int，-1为未插入，0开始同身体部位，20开始同服装部位 """
        self.insert_position_change_save: int = -1
        """ 阴茎插入位置改变记录，用于在插入指令当时不触发阴茎位置二段结算 """
        self.shoot_position_body: int = -1
        """ 身体上的射精位置，int，-1为未射精，其他同身体部位 """
        self.shoot_position_cloth: int = -1
        """ 衣服上的射精位置，int，-1为未射精，其他同衣服部位 """
        self.current_sex_position: int = -1
        """ 当前性交体位，仅博士有的数据，int，-1为无体位，1正常2后背3对面骑乘4背面骑乘5对面座6背面座7对面立8背面立9对面抱10背面抱11对面卧12背面卧 """
        self.current_womb_sex_position: int = 0
        """ 当前子宫性交位置，仅博士有的数据，int，0为未插入，1为子宫口插入，2为子宫奸"""
        self.orgasm_level: Dict[int, int] = {}
        """ 高潮程度记录，部位id:前部位快感等级 """
        self.orgasm_count: Dict[int, list] = {}
        """ 本次H里各部位的高潮次数计数，身体部位编号int:[当次计数int，总次计数int] """
        self.orgasm_edge_count: Dict[int, int] = {}
        """ 绝顶寸止次数 """
        self.time_stop_orgasm_count: Dict[int, int] = {}
        """ 时停中绝顶次数 """
        self.extra_orgasm_feel: Dict[int, int] = {}
        """ 额外高潮快感记录，用于在10级快感后的额外高潮 """
        self.extra_orgasm_count: int = 0
        """ 额外高潮次数，用于在10级快感后的额外高潮 """
        self.plural_orgasm_set: Set = set()
        """ 多重高潮部位数据集合 """
        self.endure_not_shot_count: int = 0
        """ 忍住不射次数 """
        self.just_shoot: int = 0
        """ 刚刚射精了，0没射精，1刚射精，2归零用 """
        self.orgasm_edge: int = 0
        """ 绝顶寸止，0未寸止，1正在寸止，2正常寸止解放，3寸止失败型解放 """
        self.time_stop_release: bool = False
        """ 当前为时停解放状态 """
        self.condom_info_show_flag: bool = False
        """ 避孕套信息输出标记 """
        self.condom_count: List = [0, 0]
        """ 已使用的避孕套计数，[0总个数，1总精液量] """
        self.npc_active_h: bool = False
        """ NPC主动H """
        self.h_in_love_hotel: bool = False
        """ 当前正在爱情旅馆中H """
        self.h_in_bathroom: bool = False
        """ 当前正在浴室中H """
        self.group_sex_lock_flag: bool = False
        """ 群交的模板锁定标记 """
        self.all_group_sex_temple_run: bool = False
        """ 运行全群交模板 """
        self.npc_ai_type_in_group_sex: int = 0
        """ 未在模板中的NPC在群交中的AI逻辑，0为无行动，1为仅自慰，2为优先自动补位、无位则自慰，3为每次指令都重置位置后随机抢位 """
        self.pretend_sleep: bool = False
        """ 睡奸中醒来但是装睡的状态 """
        self.sex_assist: bool = False
        """ 性爱助手状态，False为不进行，True为进行 """
        self.hidden_sex_discovery_dregree: int = 0
        """ 隐奸中被发现的程度，int，初始为0，100时被发现 """
        self.shoot_semen_amount: int = 0
        """ H中射精的精液量，int，单位ml """


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
        self.first_kiss_body_part: int = -1
        """ 初吻部位位置 -1为无，1为阴茎 """
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
        self.first_u_sex_id: int = -1
        """ U处女对象 -1为无 """
        self.first_u_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ U处女时间 """
        self.first_u_sex_place: List[str] = ["0"]  
        """ U处女地点 """
        self.first_u_sex_posture: str = ""
        """ U处女姿势 """
        self.first_u_sex_item: int = -1
        """ U处女道具 -1为无，1为采尿器 """
        self.first_w_sex_id: int = -1
        """ W处女对象 -1为无 """
        self.first_w_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ W处女时间 """
        self.first_w_sex_place: List[str] = ["0"]
        """ W处女地点 """
        self.first_w_sex_posture: str = ""
        """ W处女姿势 """
        self.first_m_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ M处女时间 """


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
        self.plan_to_wake_time: list = [6, 0]
        """ 角色计划起床的时间，[0时,1分] """
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
        self.check_out_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色退房时间 """
        self.eat_food_restaurant: int = 0
        """ 要去吃饭的餐厅，见Restaurant.csv """
        self.ask_group_sex_refuse_chara_id_list = []
        """ 拒绝群P的角色id列表 """
        self.ask_close_door_flag: bool = False
        """ 询问当前地点是否关门的标记，true的话则已询问过，每次玩家移动时重置 """
        self.move_talk_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色触发移动口上的时间，用以避免短时间频繁触发该口上 """
        self.have_shown_waiting_in_now_instruct: bool = False
        """ 角色在本次行动中已经显示过等待的文本 """
        self.health_check_today: int = 0
        """ 角色今天体检的时间，0不需要，1上午，2下午，3新干员立刻体检 """
        self.interacting_character_end_info = [-1, datetime.datetime(1, 1, 1)]
        """ 正在对自己进行交互的对方角色信息，0对方角色id，1对方行动结束时间 """
        self.past_move_position_list: List = []
        """ 角色的过去移动位置记录，list类型，最大长度为10 """
        self.last_gift_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次被赠送好感礼物的时间 """


class AUTHOR_FLAG:
    """角色作者变量结构体"""
    def __init__(self):
        self.chara_int_flag_dict: dict = {}
        """ 角色的int类型flag字典，最大长度为50，默认值为0 """
        self.chara_str_flag_dict: dict = {}
        """ 角色的str类型flag字典 """
        self.chara_float_flag_dict: dict = {}
        """ 角色的float类型flag字典 """
        self.chara_bool_flag_dict: dict = {}
        """ 角色的bool类型flag字典 """


class SPECIAL_FLAG:
    """特殊的flag"""

    def __init__(self):
        self.is_h: bool = False
        """ 在H模式中 """
        self.unconscious_h: int = 0
        """ 在无意识H模式中，int [0否,1睡眠,2醉酒,3时停,4平然,5空气,6体控,7心控] """
        self.hidden_sex_mode: int = 0
        """ 隐奸H模式，int [0否,1双不隐,2女隐,3男隐,4双隐] """
        self.sleep_h_awake: bool = False
        """ 睡奸中醒来 """
        self.wait_flag: bool = False
        """ AI行动里的原地发呆判定 """
        self.is_follow: int = 0
        """ 跟随玩家，int [0不跟随,1智能跟随,2强制跟随,3前往博士办公室,4前往博士当前位置] """
        self.tired: bool = False
        """ 疲劳状态（HP=1） """
        self.angry_with_player: bool = False
        """ 被玩家惹生气 """
        self.move_stop: bool = False
        """ 角色停止移动 """
        self.be_bagged: bool = False
        """ 被装袋搬走状态 """
        self.bagging_chara_id: int = 0
        """ 玩家正在装袋搬走的角色的id """
        self.imprisonment: bool = False
        """ 被监禁状态 """
        self.escaping: bool = False
        """ 逃跑中的状态 """
        self.sleep: bool = False
        """ 要睡觉状态 """
        self.rest: bool = False
        """ 要休息状态 """
        self.pee: bool = False
        """ 要撒尿状态 """
        self.milk: bool = False
        """ 要挤奶状态 """
        self.masturebate: int = 0
        """ 要自慰状态，int [0无,1去洗手间自慰,2去宿舍自慰,3群交自慰]"""
        self.masturebate_before_sleep: int = 0
        """ 睡前自慰状态，int [0无,1要自慰,2已自慰] """
        self.npc_masturebate_for_player: bool = False
        """ NPC找玩家去逆推来代替自慰的状态 """
        self.shower: int = 0
        """ 洗澡状态，int [0无,1要更衣,2要洗澡,3要披浴巾,4洗完澡] """
        self.eat_food: int = 0
        """ 吃饭状态，int [0无,1要取餐,2要吃饭] """
        self.find_food_weird: bool = False
        """ 发现食物不对劲 """
        self.swim: int = 0
        """ 游泳状态，int [0无,1要换泳衣,2要游泳] """
        self.bathhouse_entertainment: int = 0
        """ 大浴场娱乐状态，int [0无,1要更衣,2要娱乐] """
        self.work_maintenance: bool = False
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
        """ 香薰疗愈状态，int [0无,1回复,2习得,3反感,4快感,5好感,6催眠] """
        self.field_commission: int = 0
        """ 外勤委托状态，0为未外勤，否则为对应外勤委托编号 """
        self.in_diplomatic_visit: int = 0
        """ 外交访问状态，0为未访问，否则为对应出身地编号 """
        self.go_to_join_group_sex: bool = False
        """ 正在前往参与群交 """


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
        self.board_game_settle_data: list = [0, 0]
        """ 桌游结算用数据，0桌游类型(0无，1五子棋)，1AI难度(0最简单，越高越难) """
        self.read_book_progress: Dict[int, int] = {}
        """ 已阅读书籍进度记录，int键为书籍编号，int值为阅读进度，100为阅读完毕 """
        self.borrow_book_history: List[Dict[str, Any]] = []
        """ 借书历史记录，每个记录包含：book_id, book_name, borrow_time, return_time, total_read_count """


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
        self.eqip_token: List = [1, []]
        """ 装备的信物，0可装备数量int，1已装备信物的干员id列表list """
        self.milk_total: Dict[int, int] = {}
        """ 收集的各角色总乳汁量，单位毫升 """
        self.urine_total: Dict[int, int] = {}
        """ 收集的各角色总圣水量，单位毫升 """


class ACHIEVEMENT:
    """成就结构体"""

    def __init__(self):
        self.achievement_dict: Dict[int, bool] = {}
        """ 成就字典，键为成就编号，值为是否完成 """
        self.buy_item_count_list: List[int] = []
        """ 购买过道具种类列表 """
        self.field_commission_count: int = 0
        """ 累积完成的外勤委托数量 """
        self.equipment_repair_count: int = 0
        """ 累积维修的装备数量 """
        self.equipment_maintenance_count: int = 0
        """ 累积保养的装备数量 """
        self.time_stop_duration: int = 0
        """ 累积时间停止的时长，单位分钟 """
        self.production_count: int = 0
        """ 累积生产的产品数量 """
        self.harvest_count: int = 0
        """ 累积收获的农作物数量 """
        self.handle_official_business_count: int = 0
        """ 累积处理公务的次数 """
        self.make_food_count: int = 0
        """ 累积制作的食物数量 """
        self.gift_count: int = 0
        """ 累积赠送的礼物数量 """
        self.health_check_count: int = 0
        """ 累积进行的身体检查人数 """
        self.body_report_chara_count_list: List[int] = []
        """ 出具过身体检查报告的干员id列表 """
        self.aromatherapy_count: int = 0
        """ 累积对别人进行香薰疗愈的次数 """
        self.visited_nation_list: List[int] = []
        """ 累积去过的国家id列表 """
        self.group_sex_record: Dict[int, list] = {}
        """ 群交记录，1为对群交中被射精的干员的id列表，2为群交中绝顶的干员id列表 """
        self.hidden_sex_record: Dict[int, int] = {}
        """ 隐奸记录，1为隐奸模式，2为在场其他干员人数，3为射精次数，4为隐奸干员绝顶次数 """
        self.sleep_sex_record: Dict[int, int] = {}
        """ 睡奸记录，1为睡奸模式0正常1装睡，2为射精次数，3为被睡奸干员绝顶次数 """


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
        self.air_hypnosis_position: str = ""
        """ 空气催眠地点 """
        self.carry_chara_id_in_time_stop: int = 0
        """ 时停中正在搬运的角色id """
        self.free_in_time_stop_chara_id: int = 0
        """ 时停中允许自由活动的角色id """


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
        self.start_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 行为开始时间 """
        self.duration: int = 0
        """ 行为持续时间(单位分钟) """
        self.behavior_id: str = "share_blankly"
        """ 行为id """
        self.move_target: List[str] = []
        """ 移动行为的目标坐标 """
        self.move_src: List[str] = []
        """ 移动行为的出发坐标 """
        self.move_final_target: List[str] = []
        """ 移动行为的最终目标坐标 """
        self.target_food: Food = Food()
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
        """ 前提结算用:母乳的毫升数 """
        self.urine_ml: int = 0
        """ 前提结算用:圣水的毫升数 """
        self.h_interrupt_chara_name: str = ""
        """ 前提结算用:打断H的角色的名字 """
        self.board_game_type: int = 0
        """ 前提结算用:桌游类型 """
        self.board_game_ai_difficulty: int = 0
        """ 前提结算用:桌游AI难度 """
        self.gift_id: int = 0
        """ 前提结算用:礼物id """


class Chara_Event:
    """角色事件状态数据"""

    def __init__(self):
        self.event_id: str = ""
        """ 角色当前事件id """
        self.son_event_id: str = ""
        """ 角色当前子事件id """
        self.chara_diy_event_flag: bool = False
        """ 角色自定义事件标记 """
        self.skip_instruct_talk: bool = False
        """ 跳过指令口上标记 """


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
        self.is_button: bool = False
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
        self.in_door: bool = False
        """ 在室内 """
        self.exposed: bool = False
        """ 地点暴露 """
        self.have_furniture: int = 0
        """ 有家具(1基础家具,2办公级家具,3卧室级家具) """
        self.close_type: int = 0
        """ 关门类型(0无法关门,1正常关门,2小隔间关门) """
        self.close_flag: int = 0
        """ 关门状态，同关门类型close_type(0未关门,1正常关门,2小隔间关门) """
        self.room_area: int = 0
        """ 房间面积(0基础10人,1标准50人,2较大100人,3无限制人数) """
        self.scene_tag: list = []
        """ 场景标签 """
        self.character_list: set = set()
        """ 场景内角色列表 """


class Rhodes_Island:
    """罗德岛相关属性"""

    def __init__(self):
        self.facility_level: Dict[int, int] = {}
        """ 基地当前所有设施的等级 """
        self.facility_open: Dict[int, bool] = {}
        """ 基地当前所有待开放设施的开放情况 """
        self.all_work_npc_set: Dict[int, set] = {}
        """ 所有工作的所属的干员id合集,工作id:干员id的集合 """
        self.work_people_now: int = 0
        """ 当前工作干员人数 """
        self.people_max: int = 0
        """ 干员人数上限 """
        self.all_income: int = 0
        """ 今日全部门总收入 """
        self.party_day_of_week: Dict[int, int] = {}
        """ 一周内的派对计划，周一0~周日6:娱乐id """
        self.total_favorability_increased: int = 0
        """ 每日总好感度提升 """
        self.total_semen_count: int = 0
        """ 每日总射精量 """
        self.week_fall_chara_pink_certificate_add: int = 0
        """ 本周陷落干员提供的粉红凭证总数 """

        # 控制中枢
        self.current_location: List[int] = []
        """ 基地当前所在位置，[0国家id,1城市id] """
        self.move_target_and_time: List = [0,0,0]
        """ 基地移动目标和时间, [0国家id,1城市id,2抵达时间] """
        self.office_work: float = 0
        """ 需要处理的公务 """
        self.effectiveness: int = 0
        """ 基地效率 """

        # 动力区
        self.power_use: int = 0
        """ 当前使用电力（2025.9已废弃） """
        self.power_max: int = 0
        """ 总可用电力（2025.9已废弃） """
        self.power_storage: float = 0.0
        """ 当前储能 """
        self.power_storage_max: float = 0.0
        """ 最大可储能，由蓄电池数量与等级计算 """
        self.power_operator_ids_list: List[int] = []
        """ 供能调控员id列表 """
        self.main_power_facility_operator_ids: List[int] = [0, 0, 0, 0]
        """ 主力供能设施的调控员id列表，0~3分别为火水风光发电 """
        self.orundum_reactor_list: List[int] = [1, 3]
        """ 源石反应炉的列表，0号为主反应炉等级，1为已启用的副反应炉数量 """
        self.other_power_facility_list: List[int] = [0, 0, 0]
        """ 其他供能设施列表，0为水力发电机数量，1为风能发电机数量，2为太阳能发电机数量 """
        self.battery_list: List[int] = [0, 0, 0]
        """ 蓄电池列表，0号为1级蓄电池数量，1号为2级蓄电池数量，2号为3级蓄电池数量 """
        self.now_used_extra_clean_energy_module_count: int = 0
        """ 当前正在使用的额外清洁能源模块数量的记录，用于在卖出等减少数量操作时防止超出 """
        self.now_used_extra_battery_count: int = 0
        """ 当前正在使用的额外蓄电池数量的记录，用于在卖出等减少数量操作时防止超出 """
        self.power_supply_strategy: Dict[int, int] = {}
        """ 各主区块供电策略 facility_cid:策略id(见supply_strategy.csv) """

        # 工程部
        self.maintenance_place: Dict[int, str] = {}
        """ 当前每个角色的待检修地点，角色id:地点 """
        self.facility_damage_data: Dict[str, int] = {}
        """ 设施损坏数据，地点名str:损坏值int """
        self.equipment_maintain_setting: Dict[int, int] = {}
        """ 装备维护设置 设置id:设置值 """
        self.equipment_maintain_operator_ids: List[int] = []
        """ 手动选择的装备维护对象干员id列表 """
        self.maintenance_equipment_chara_id: Dict[int, int] = {}
        """ 当前每个角色正在维护中的装备的所属角色id，角色id:角色id """

        # 仓储区
        self.warehouse_capacity: int = 0
        """ 仓库容量 """
        self.materials_resouce: Dict[int, int] = {}
        """ 素材资源 """

        # 生活娱乐区
        self.life_zone_max: int = 0
        """ 生活娱乐区设施数量上限 """
        self.milk_in_fridge: Dict[int, int] = {}
        """ 冰箱里每个干员的当日母乳存量，干员id:母乳ml存量 """
        self.dining_hall_data: Dict[str, Dict[UUID, Food]] = {}
        """
        食堂内贩卖的食物数据
        食谱id(str):食物唯一id:食物对象
        """
        self.makefood_data: Dict[str, Dict[UUID, Food]] = {}
        """
        做饭区的食物数据
        食谱id(str):食物唯一id:食物对象
        """

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
        self.urine_in_fridge: Dict[int, int] = {}
        """ 冷库里每个干员的当日圣水量，干员id:圣水ml存量 """
        self.physical_examination_setting: Dict[int, int] = {}
        """ 体检设置 设置id:设置值 """
        self.today_physical_examination_chara_id_dict: Dict[int, set] = {}
        """ 今日已体检的干员数据 干员id:体检项目id集合 """
        self.examined_operator_ids: Set[int] = set()
        """ 本次体检周期内已体检过的干员id集合 """
        self.waiting_for_exam_operator_ids: Set[int] = set()
        """ 当前正在等待体检的干员id集合 """
        self.manually_selected_exam_operator_ids: Set[int] = set()
        """ 手动选择的体检对象干员id集合 """
        self.manually_selected_exam_week_day_list: List[int] = []
        """ 手动选择的每周的体检日列表 """

        # 文职区
        self.recruit_line: Dict[int, List] = {}
        """ 招募线数据: 招募线id:[0招募进度%, 1招募策略id, 2该线主招聘专员id(0为空缺), 3招募效率百分比(如20.5%)] (2025.09重构) """
        self.hr_operator_ids_list: List[int] = []
        """ 招募专员id列表 """
        self.recruited_id: Set = set()
        """ 已招募待确认的干员id """

        # 训练场

        # 图书档案区
        self.now_show_book_cid_of_type: Dict[int, List] = {}
        """ 当前展示的可借阅书籍，类别id：书籍id列表 """
        self.book_borrow_dict: Dict[int, int] = {}
        """ 书籍借出情况 书籍id:借出人id(-1为未借出) """
        self.reader_now: int = 0
        """ 当前图书馆中的读者数量 """
        self.recommend_book_type_set: Set = set()
        """ 推荐的阅读类别 """

        # 贸易区
        self.shop_open_list = []
        """ 商店开放列表 """
        self.love_hotel_room_lv: int = 0
        """ 在爱情旅馆中的房间级别，0未入住，1标间，2情趣主题房，3顶级套房 """
        self.restaurant_data: Dict[int, Dict] = {}
        """
        餐馆内贩卖的食物数据
        餐馆id:食物名字:食物唯一id:食物对象
        """
        self.stall_vendor_data: Dict[int, Dict] = {}
        """
        地摊小贩的货物数据
        货物类型id（0为食物）:货物字典
        """
        self.supply_demand_dict: Dict[int, float] = {}
        """
        供需关系字典
        货物类型id: 供需系数值
        """
        self.today_trade_resource_count: Dict[int, int] = {}
        """ 资源类型id: 今日买入卖出总量 """

        # 制造加工区
        self.assembly_line: Dict[int, List] = {}
        """ 流水线id: [0生产配方id(formula_id), 1主生产工人id(0为空缺), 2当前总效率百分比(浮点, 如 123.5), 3待切换配方id(次日生效, 0表示无), 4上次结算小时] """
        self.production_worker_ids: List[int] = []
        """ 生产工人id列表 """

        # 访客区
        self.visitor_max: int = 0
        """ 访客人数上限 """
        self.base_move_visitor_flag: bool = False
        """ 因为基地移动而吸引访客 """
        self.visitor_info: Dict[int, datetime.datetime] = {}
        """ 访客统计数据 访客id:[0停留开始时间] """
        self.last_visitor_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 上次访客到来时间 """
        self.invite_visitor: List = []
        """ 当前邀请进度 [0目标角色id, 1招募进度, 2招募效率百分比(如2.5)] """
        self.diplomat_of_country: Dict[int, List] = {}
        """ 负责各的外交官 出身地国家id:[0外交官角色id, 1外交方针id] """

        # 机库
        self.ongoing_field_commissions: Dict[int, List] = {}
        """ 进行中的外勤委托，委托id:0干员id列表List，1返回时间datetime，2使用的载具id列表List """
        self.vehicles: Dict[int, List] = {}
        """ 载具id:[0数量int，1外勤中数量int] """
        self.finished_field_commissions_set: Set = set()
        """ 已完成的外勤委托集合 """
        self.shut_down_field_commissions_set: Set = set()
        """ 已禁止的外勤委托集合 """

        # 教育区

        # 疗养庭院
        self.herb_garden_line: Dict[int, List] = {}
        """ 药田生产情况 流水线id:[0生产类型id, 1主种植员id(0为空缺), 2总效率百分比(显示用, 如110), 3明日要变成的新生产类型, 4上次收菜的小时] """
        self.herb_garden_operator_ids: List[int] = []
        """ 药田种植员id列表 """
        self.green_house_line: Dict[int, List] = {}
        """ 温室生产情况 流水线id:[0生产类型id, 1主种植员id(0为空缺), 2总效率百分比(显示用, 如110), 3明日要变成的新生产类型, 4上次收菜的小时] """
        self.green_house_operator_ids: List[int] = []
        """ 花草种植员id列表 """
        self.remaining_aromatherapy_sessions_today: int = 0
        """ 今日剩余调香次数 """

        # 大浴场

        # 甲板

        # 关押区
        self.current_warden_id: int = 0
        """ 当前监狱长的干员id """
        self.current_prisoners: Dict[int, List] = {}
        """ 当前囚犯干员的数据，干员id: [被关押的时间datetime, 逃脱的概率int] """
        self.confinement_training_setting: Dict[int, int] = {}
        """ 监禁调教设置 设置id:设置值 """
        self.pre_training_cleaning: bool = False
        """ 调教前清洗准备 """
        self.pre_training_lubrication: bool = False
        """ 调教前润滑准备 """
        self.pre_training_tool_dict: Dict[int, int] = {}
        """ 调教前道具使用，同BODY_H_STATE类的body_item """
        self.sex_assistant_ai_behavior_id_list: list = []
        """ 调教助手的AI行为列表 """
        self.sex_assistant_ai_ban_behavior_id_list: list = []
        """ 调教助手的AI禁止行为列表 """

        self.research_zone_max: int = 0
        """ 科研区设施数量上限 """
        self.soldier_max: int = 0
        """ 战斗时干员数量上限 """

class Country:
    """大地图国家数据"""

    def __init__(self):
        self.nation_reputation: Dict[int, float] = {}
        """ 势力声望 """
        self.country_infection_rate: Dict[int, int] = {}
        """ 国家矿石病感染率 """


class System_Setting:
    """系统设置"""

    def __init__(self):
        self.base_setting: Dict[int, int] = {}
        """ 基础系统设定，即base类 """
        self.draw_setting: Dict[int, int] = {}
        """ 绘制设定，即draw类 """
        self.difficulty_setting: Dict[int, int] = {}
        """ 难度设定，即difficulty类 """
        self.line_before_main_update: int = 3
        """ 主界面刷新前的行数 """
        self.value_draw: Dict[str, bool] = {"pl": False, "npc": False}
        """ 数值绘制 """
        self.character_text_version: Dict[int, int] = {}
        """ 角色文本版本，adv_id:版本id """


class Ai_Setting:
    """AI设置"""

    def __init__(self):
        self.ai_chat_setting: Dict[int, int] = {}
        """ ai聊天设定，见Ai_Chat_Setting.csv """
        self.ai_chat_api_key: Dict[str, str] = {}
        """ ai聊天api key """
        self.now_ai_chat_model: str = ""
        """ 当前使用的ai聊天模型 """
        self.now_ai_chat_base_url: str = ""
        """ 当前使用的自定义base url """
        self.now_ai_chat_proxy: list = ["", ""]
        """ 当前使用的代理，[0代理ip,1代理端口] """
        self.ai_chat_translator_setting: int = 0
        """ 是否开启ai聊天翻译功能，0不开启，1仅翻译地文，2翻译地文和口上 """
        self.send_data_flags: Dict[int, bool] = {}
        """ 记录向AI发送哪些数据 """

class Character:
    """角色数据结构体"""

    def __init__(self):
        self.cid: int = 0
        """ 角色id """
        self.name: str = ""
        """ 角色名字 """
        self.nick_name: str = ""
        """ 他人对自己的称呼 """
        self.nick_name_to_pl: str = ""
        """ 自己对玩家的称呼 """
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
        self.desire_point: int = 0
        """ 欲望值 1m=10点，10min=100点(max)"""
        self.state: int = 0
        """ 角色当前状态 """
        self.last_behavior_id_list: List = [0]
        """ 角色之前的行为列表 """
        self.talk_size: int = 0
        """ 角色口上大小，单位kb """
        self.text_color: str = ""
        """ 角色对话文本颜色 """
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
        self.second_behavior: Dict[str, int] = {}
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
        self.trust: float = 0
        """ 角色信赖度数据 """
        self.food_bag: Dict[UUID, Food] = {}
        """ 角色持有的食物数据 """
        self.target_character_id: int = 0
        """ 角色当前交互对象id """
        self.adv: int = 0
        """ 剧情npc校验 """
        # self.no_wear: bool = False
        # """ 是否不想穿衣服 """
        self.dead: bool = False
        """ 角色已死亡 """
        self.collection_character: Set = set()
        """ 收藏的角色列表 """
        self.last_hunger_time: datetime.datetime = datetime.datetime(1, 1, 1)
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
        self.body_manage: Dict[int, int] = {}
        """ 角色的身体管理，见Body_Manage_Requirement.csv """
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
        self.author_flag: AUTHOR_FLAG = AUTHOR_FLAG()
        """ 角色口上作者变量 """


class Cache:
    """游戏缓存数据结构体"""

    def __init__(self):
        self.back_save_panel: bool = False
        """ 退出存档面板 """
        self.wframe_mouse: WFrameMouse = WFrameMouse()
        """ 主页监听控制流程用变量组 """
        self.web_mode: bool = False
        """ 是否为web模式 """
        self.current_draw_elements: List = []
        """ 当前绘制的元素列表 """
        self.web_draw_history: List = []
        """ Web模式下的文本历史缓存 """
        self.web_draw_history_line_total: int = 0
        """ web文本历史累计行数 """
        self.current_return_list: List = []
        """ 当前返回的元素列表 """
        self.current_input_request: List = []
        """ 当前输入请求列表 """
        self.character_data: Dict[int, Character] = {}
        """ 角色对象数据缓存组 """
        self.npc_tem_data: List[NpcTem] = []
        """ npc模板列表 """
        self.npc_id_got: Set = set()
        """ 已拥有的干员id集合 """
        self.forbidden_npc_id: Set = set()
        """ 禁止出现的干员id集合 """
        self.input_cache: List[str] = []
        """ 玩家指令输入记录（最大20）"""
        self.daily_intsruce: List[str] = []
        """ 每日指令输入记录 """
        self.pl_pre_behavior_instruce: List[str] = []
        """ 玩家过去行为指令记录，最大长度为10 """
        self.taiggered_event_record: Set = set()
        """ 触发过的事件记录 """
        self.today_taiggered_event_record: Set = set()
        """ 今日触发过的事件记录 """
        self.now_init_map_id: str = ""
        """ 寻路算法用,当前节点所属的地图的id """
        self.collect_position_list: List = []
        """ 收藏地点合集 """
        self.input_position: int = 0
        """ 回溯输入记录用定位 """
        self.instruct_type_filter: Dict[int, bool] = {}
        """ 玩家操作指令面板指令过滤状态数据 指令类型:是否展示"""
        self.instruct_sex_type_filter: Dict[int, bool] = {}
        """ 玩家操作指令面板中，H类的指令过滤状态数据 指令类型:是否展示"""
        self.instruct_type_filter_cache: Dict[int, bool] = {}
        """ （已弃用）玩家操作指令面板指令过滤状态数据_的缓存 指令类型:是否展示"""
        self.instruct_index_filter: Dict[int, bool] = {}
        """ 玩家各编号指令过滤状态数据 指令编号:是否展示"""
        self.show_non_h_in_hidden_sex: bool = False
        """ 是否在隐奸中显示非H类指令 """
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
        self.font_size: int = 0
        """ 字体大小 """
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
        self.game_update_flow_running: int = 0
        """ 游戏更新流程运行状态标志，用于防止递归调用导致的死循环 """
        self.pl_sleep_save_flag: bool = False
        """ 玩家睡觉，要进行存档 """
        self.recipe_data: Dict[int, Recipes] = {}
        """ 菜谱数据 """
        self.npc_name_data: Set = set()
        """ 已有的npc姓名集合 """
        self.is_collection: bool = False
        """ 启用收藏模式 """
        self.sun_phase: Dict[str, Dict[int, Dict[int, int]]] = {}
        """ 指定日期下每分钟太阳位置 日期:时:分:位置id """
        self.moon_phase: Dict[str, int] = {}
        """ 指定日期月相记录 日期:月相id """
        self.shoot_position: int = 0
        """ 记录射精位置 """
        self.debug_mode: bool = False
        """ debug模式 """
        self.time_stop_mode: bool = False
        """ 时间停止模式 """
        self.group_sex_mode: bool = False
        """ 群交模式 """
        self.game_round: int = 1
        """ 当前周目数 """
        self.all_npc_position_panel_select_type: int = 0
        """ 所有npc位置面板筛选类型 """
        self.all_npc_position_panel_move_type: int = 0
        """ 所有npc位置面板移动类型 """
        self.rhodes_island: Rhodes_Island = Rhodes_Island()
        """ 罗德岛相关属性 """
        self.first_bonus: Dict[int, int] = {}
        """ 初期奖励 """
        self.world_setting: Dict[int, int] = {}
        """ 世界设定 """
        # self.system_setting: Dict[int, int] = {}
        # """ 系统设定，见System_Setting.csv """
        self.all_system_setting: System_Setting = System_Setting()
        """ 新的总系统设定 """
        self.ai_setting: Ai_Setting = Ai_Setting()
        """ ai设定 """
        self.country: Country = Country()
        """ 大地图国家数据 """
        self.achievement: ACHIEVEMENT = ACHIEVEMENT()
        """ 成就 """

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
        self.trust: float = 0
        """ 信赖度变化 """
        self.target_change: Dict[int, TargetChange] = {}
        """ 互动目标状态变化 """
        self.ability: Dict[int, int] = {}
        """ 能力变化 """
        self.experience: Dict[int, int] = {}
        """ 经验变化 """
        self.sanity_point: int = 0
        """ 理智变化 """
        self.hypnosis_degree: float = 0
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
        self.trust: float = 0
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
        self.hypnosis_degree: float = 0
        """ 催眠程度变化 """


class Event:
    """事件数据结构体"""

    def __init__(self):
        """初始化事件对象"""
        self.uid: str = ""
        """ 事件唯一id """
        self.adv_id: str = ""
        """ 事件所属advnpcid """
        self.behavior_id: str = ""
        """ 事件所属行为id """
        self.start: bool = False
        """ 是否是行为开始时的事件 """
        self.type: int = 1
        """ 事件类型(0跳过指令，1指令前事件后，2事件前指令后) """
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
