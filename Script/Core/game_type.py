from uuid import UUID
from typing import List, Dict, Set
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
        self.Sex: str = ""
        """ npc性别 """
        self.Age: str = ""
        """ npc年龄模板 """
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
        #以下为新加
        self.Favorability: str = {}
        """ 好感度模板 """
        self.Trust: int = 0
        """ 信赖度模板 """
        self.Ability: Dict[int,int] = {}
        """ 能力预设 """
        self.Experience: Dict[int,int] = {}
        """ 经验预设 """
        self.Juel: Dict[int,int] = {}
        """ 宝珠预设 """
        self.Profession: str = ""
        """ 职业预设 """
        self.Race: str = ""
        """ 种族预设 """
        self.Talent: Dict[int,int] = {}
        """ 素质预设 """
        self.Cloth: list = []
        """ 服装预设 """
        self.Hp: int = 0
        """ HP预设 """
        self.Mp: int = 0
        """ MP预设 """
        self.Dormitory: int = 0
        """ 宿舍预设 """
        self.Token: int = 0
        """ 信物预设 """


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
        # self.quality: int = 0
        # """ 食物品质 """
        # self.weight: int = 0
        # """ 食物重量 """
        # self.feel: dict = {}
        # """ 食物效果 """
        # self.maker: str = ""
        # """ 食物制作者 """
        self.recipe: int = -1
        """ 食谱id """
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


class Recipes:
    """菜谱数据结构体"""

    def __init__(self):
        self.name: str = ""
        """ 菜谱名字 """
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
        0~13共14项，编号int:[部位名str,当前精液量int,当前精液等级int,总精液量int]    
        部位顺序 [0"头发",1"脸部",2"口腔",3"胸部",4"腋部",5"手部",6"小穴",7"后穴",8"尿道",9"腿部",10"脚部",11"尾巴",12"兽角",13"兽耳"]
        """
        self.cloth_semen: list = []
        """ 服装精液情况    
        同衣服类型，编号int:[部位名str,当前精液量int,当前精液等级int,总精液量int]    
        """
        self.a_clean: int = 0
        """ A是否干净 [0脏污,1灌肠中,2已灌肠,3精液灌肠中,4已精液灌肠] """


class BODY_H_STATE:
    """H状态结构体"""

    def __init__(self):

        self.body_item: list = []
        """ 身体道具情况    
        0~9共10项，编号int:[道具名str,当前有无bool,状态的结束时间datetime.datetime]    
        部位顺序 [0"乳头夹",1"阴蒂夹",2"V震动棒",3"A震动棒",4"搾乳机",5"采尿器",6"眼罩",7"肛门拉珠",8"持续性利尿剂",9"睡眠药"]
        """


        self.bondage: int = 0
        """ 绳子捆绑情况    
        0~9共10项，编号int    
        [0未捆绑,1后高手缚,2直立缚,3驷马捆绑,4直臂缚,5双手缚,6菱绳缚,7龟甲缚,8团缚,9逆团缚,10吊缚,11后手吊缚,12单足吊缚,13后手观音,14苏秦背剑,15五花大绑]
        """

class ASSISTANT_STATE:
    """助理状态结构体"""

    def __init__(self):

        self.always_follow: int = 0
        """ 跟随服务，int[0否,1智能跟随，在非工作时间(饭点/上厕所等)会暂离,2强制跟随,3在博士办公室待机]"""
        self.always_help_work: bool = False
        """ 辅佐服务，仅由助理辅助工作系指令"""
        self.work_until_sleep: bool = False
        """ 加班服务，博士睡觉后自动加班到自己睡觉"""
        self.offer_food: int = 0
        """ 送饭服务，int[0否,1帮忙买午饭,2帮忙买三餐,3亲手做午饭,4亲手做三餐]"""
        self.good_morning: int = 0
        """ 早安服务，int[0否,1早安叫起床,2叫起床+早安吻,3叫起床+早安咬]"""
        self.good_evening: int = 0
        """ 晚安服务，int[0否,1晚安催睡觉,2催睡觉+晚安吻,3催睡觉+早安咬]"""
        self.live_together: bool = False
        """ 同居服务"""
        self.help_chase: bool = False
        """ 助攻服务"""
        self.help_sex: int = 0
        """ 性处理服务，int[0否,1被动接受(非本番),2被动接受(含本番),3主动请求(非本番),4主动请求(含本番)]"""


class FIRST_RECORD:
    """初次状态记录结构体"""

    def __init__(self):

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

        self.talk_count : int = 0
        """ 角色聊天次数计数器 """
        self.talk_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次聊天时间 """
        self.last_move_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次移动的时间 """
        self.last_training_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色上次训练的时间 """
        self.social_contact_last_time: Dict[int, datetime.datetime] = {}
        """ 指定角色最后与自己社交的时间 """
        self.social_contact_last_cut_down_time: Dict[int, datetime.datetime] = {}
        """ 指定角色上次扣除好感时间 """



class PLAYER_COLLECTION:
    """玩家收集品结构体"""

    def __init__(self):

        self.collection_bonus:Dict[int,bool] = {}
        """ 收藏品的解锁奖励 """
        self.token_list:Dict[int,bool] = {}
        """ 获得的NPC信物 """
        self.first_panties: Dict[int,str] = {}
        """ 获得的处子血胖次 """
        self.npc_panties: Dict[int,list] = {}
        """ 获得的角色胖次 """
        self.npc_panties_tem: Dict[int,list] = {}
        """ 临时获得的角色胖次 """
        self.npc_socks: Dict[int,list] = {}
        """ 获得的角色袜子 """
        self.npc_socks_tem: Dict[int,list] = {}
        """ 临时获得的角色袜子 """



class PLAYER_ABILITY:
    """玩家能力结构体"""

    def __init__(self):

        self.follow_count: int = 1
        """ 最大同时跟随人数 """
        self.jj_size: int = 1
        """ 阴茎大小，0短小,1普通,2粗大,3巨根 """


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
        """ 移动行为目标坐标 """
        self.move_src: List[str] = []
        """ 移动行为的出发坐标 """
        self.eat_food: Food = None
        """ 进食行为消耗的食物对象 """
        self.food_name: str = ""
        """ 前提结算用:进食行为消耗的食物名字 """
        self.food_quality: int = 0
        """ 前提结算用:进食行为消耗的食物品质 """
        self.make_food_time: int = 0
        """ 前提结算用:做饭指令用时 """
        self.pan_name: str = ""
        """ 前提结算用:内裤名字 """
        self.socks_name: str = ""
        """ 前提结算用:袜子名字 """


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
        self.scene_tag: list = []
        """ 场景标签 """
        self.character_list: set = set()
        """ 场景内角色列表 """


class Base_resouce:
    """基地资源"""

    def __init__(self):
        self.facility_level: Dict[int,int] = {}
        """ 基地当前所有设施的等级 """
        self.power_use: int = 0
        """ 当前使用电力 """
        self.power_max: int = 0
        """ 总可用电力 """
        self.warehouse_capacity: int = 0
        """ 仓库容量 """
        self.people_max: int = 0
        """ 干员人数上限 """
        self.life_zone_max: int = 0
        """ 生活娱乐区设施数量上限 """
        self.ppatient_max: int = 0
        """ 患者人数上限 """
        self.research_zone_max: int = 0
        """ 科研区设施数量上限 """
        self.shop_max: int = 0
        """ 商店数量上限 """
        self.soldier_max: int = 0
        """ 战斗时干员数量上限 """


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
        self.age: int = 18
        """ 角色年龄 """
        self.hit_point_max: int = 0
        """ 角色最大HP """
        self.hit_point: int = 0
        """ 角色当前HP """
        self.mana_point_max: int = 0
        """ 角色最大MP """
        self.mana_point: int = 0
        """ 角色当前MP """
        self.eja_point_max: int = 0
        """ 角色最大射精槽 """
        self.eja_point: int = 0
        """ 角色当前射精槽 """
        self.angry_point: int = 0
        """ 角色当前愤怒槽 """
        self.sleep_point : int = 0
        """ 困倦值 6m=1点，16h=160点(max)"""
        self.urinate_point : int = 0
        """ 尿意值 1m=1点，4h=240点(max)"""
        self.hunger_point : int = 0
        """ 饥饿值 1m=1点，4h=240点(max)"""
        self.state: int = 0
        """ 角色当前状态 """
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
        self.clothing_tem: int = 0
        """ 角色生成服装模板 """
        self.cloth: Dict[int,List] = {}
        """ 角色穿着的服装 部位:衣服id"""
        self.cloth_off: Dict[int,List] = {}
        """ 角色脱下的服装 部位:衣服id"""
        self.cloth_see: Dict[int,bool] = {}
        """ 角色穿着的服装能否被看见 部位:能否"""
        # self.item: Set = set()
        # """ 旧：角色拥有的道具id集合 """
        self.item: Dict[int,int] = {}
        """ 角色拥有的道具 道具序号:数量"""
        # self.height: Height = Height()
        # """ 角色的身高数据 """
        # self.measurements: Measurements = Measurements()
        # """ 角色的三围数据 """
        self.behavior: Behavior = Behavior()
        """ 角色当前行为状态数据 """
        self.second_behavior: Dict[int,int] = {}
        """ 角色当前二段行为状态数据 """
        # self.gold: int = 0
        # """ 角色所持金钱数据 """
        self.position: List[str] = ["0"]
        """ 角色当前坐标数据 """
        self.officeroom: List[str] = []
        """ 角色所属办公室坐标 """
        self.dormitory: str = ""
        """ 角色宿舍坐标 """
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
        self.social_contact: Dict[int, Set] = {}
        """ 角色社交关系数据 关系类型:角色id集合 """
        self.social_contact_data: Dict[int, int] = {}
        """ 角色社交关系数据 角色id:关系类型 """
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
        self.no_wear: bool = 0
        """ 是否不想穿衣服 """
        self.dead: bool = 0
        """ 角色已死亡 """
        self.collection_character: Set = set()
        """ 收藏的角色列表 """
        self.last_hunger_time: datetime.datetime = None
        """ 最后一次结算饥饿的时间 """
        self.ability:Dict[int,int] = {}
        """ 角色能力类型 """
        self.experience:Dict[int,int] = {}
        """ 角色经验 """
        self.juel:Dict[int,int] = {}
        """ 角色宝珠 """
        self.profession: int = 0
        """ 角色职业 """
        self.race: int = 0
        """ 角色种族 """
        self.talent:Dict[int,int] = {}
        """ 角色素质 """
        self.wait_flag : bool = 0
        """ AI行动里的原地发呆判定 """
        self.is_h : bool = 0
        """ 在H模式中 """
        self.is_follow : int = 0
        """ 跟随玩家，int [0不跟随,1智能跟随,2强制跟随] """
        self.orgasm_level: Dict[int,int] = {}
        """ 高潮程度记录，每3级一个循环，1为小绝顶，2为普绝顶，3为强绝顶 """
        self.orgasm_count: Dict[int,int] = {}
        """ 高潮次数记录 """
        self.token_text: str = ""
        """ 角色信物文本 """
        self.tired : bool = 0
        """ 疲劳状态（HP=1） """
        self.angry_with_player : bool = 0
        """ 被玩家惹生气 """
        self.money : int = 0
        """ 龙门币数量 """
        self.orundum : int = 0
        """ 合成玉数量 """
        self.Originite_Prime : int = 0
        """ 至纯源石数量 """
        self.first_record: FIRST_RECORD = FIRST_RECORD()
        """ 角色初次状态记录 """
        self.dirty: DIRTY = DIRTY()
        """ 角色身上污浊的情况 """
        self.h_state: BODY_H_STATE = BODY_H_STATE()
        """ 角色本次H的情况 """
        self.assistant_character_id: int = 0
        """ 助理角色id """
        self.assistant_state: ASSISTANT_STATE = ASSISTANT_STATE()
        """ 角色作为助理的情况 """
        self.pl_ability: PLAYER_ABILITY = PLAYER_ABILITY()
        """ 玩家的特殊能力 """
        self.pl_collection: PLAYER_COLLECTION = PLAYER_COLLECTION()
        """ 玩家的收藏品 """
        self.action_info: ACTION_INFO = ACTION_INFO()
        """ 角色的行动记录 """

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
        self.input_cache: List[str] = []
        """ 玩家指令输入记录（最大20）"""
        self.now_init_map_id: str = ""
        """ 寻路算法用,当前节点所属的地图的id """
        self.input_position: int = 0
        """ 回溯输入记录用定位 """
        self.instruct_filter: Dict[int, bool] = {}
        """ 玩家操作指令面板指令过滤状态数据 指令类型:是否展示"""
        self.output_text_style: str = ""
        """ 富文本记录输出样式临时缓存 """
        self.text_style_position: int = 0
        """ 富文本回溯样式记录用定位 """
        self.clothing_type_data: dict = {}
        """ 存储服装类型数据 """
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
        self.now_panel_id: int = 0
        """ 当前游面板id """
        self.old_character_id: int = 0
        """ 离开场景面板前在场景中查看的角色id """
        self.text_wait: int = 0
        """ 绘制文本输出等待时间 """
        self.map_data: Dict[str, Map] = {}
        """ 游戏地图数据 地图路径:地图数据 """
        self.scene_data: Dict[str, Scene] = {}
        """ 游戏场景数据 场景路径:场景数据 """
        self.random_npc_list: List[NpcTem] = []
        """ 随机npc数据 """
        self.wear_item_type_data: dict = {}
        """ 可穿戴道具类型数据 """
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
        self.school_longitude: float = 0
        """ 学校经度 """
        self.school_latitude: float = 0
        """ 学校纬度 """
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
        self.base_resouce: Base_resouce = Base_resouce
        """ 基地的资源情况 """


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
        self.money: int = 0
        """ 金钱变化 """


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
        self.money: int = 0
        """ 金钱变化 """
