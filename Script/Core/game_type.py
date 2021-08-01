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
        self.Weight: str = ""
        """ 体重模板 """
        self.BodyFat: str = ""
        """ 体脂率模板 """
        self.Chest: int = 0
        """ 罩杯模板 """
        self.MotherTongue: str = ""
        """ 母语 """
        self.SexExperienceTem: str = ""
        """ 性经验模板 """
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
        self.Hp: int = 0
        """ HP预设 """
        self.Mp: int = 0
        """ MP预设 """


class Measurements:
    """三围数据结构体"""

    def __init__(self):
        self.bust: float = 0
        """ 胸围 """
        self.waist: float = 0
        """ 腰围 """
        self.hip: float = 0
        """ 臀围 """


class Chest:
    """胸围差数据结构体"""

    def __init__(self):
        self.target_chest: int = 0
        """ 预期最终胸围差 """
        self.now_chest: int = 0
        """ 当前胸围差 """
        self.sub_chest: int = 0
        """ 每日胸围差增量 """


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
    proportion_teacher: int
    """ 生成教师权重 """
    proportion_student: int
    """ 生成学生权重 """
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


class Clothing:
    """服装数据结构体"""

    def __init__(self):
        self.uid: UUID = ""
        """ 服装对象的唯一id """
        self.tem_id: int = 0
        """ 服装配表id """
        self.sexy: int = 0
        """ 服装性感属性 """
        self.handsome: int = 0
        """ 服装帅气属性 """
        self.elegant: int = 0
        """ 服装典雅属性 """
        self.fresh: int = 0
        """ 服装清新属性 """
        self.sweet: int = 0
        """ 服装可爱属性 """
        self.warm: int = 0
        """ 服装保暖属性 """
        self.cleanliness: int = 0
        """ 服装清洁属性 """
        self.price: int = 0
        """ 服装价值属性 """
        self.evaluation: str = ""
        """ 服装评价文本 """
        self.wear: int = 0
        """ 穿戴部位 """


class Height:
    """身高数据结构体"""

    def __init__(self):
        self.now_height: float = 0
        """ 当前身高 """
        self.growth_height: float = 0
        """ 每日身高增量 """
        self.expect_age: int = 0
        """ 预期结束身高增长年龄 """
        self.development_age: int = 0
        """ 预期发育期结束时间 """
        self.expect_height: float = 0
        """ 预期的最终身高 """


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
        self.course_id: int = 0
        """ 上课时所学/教的课程 """
        self.make_food_time: int = 0
        """ 前提结算用:做饭指令用时 """


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
        self.scene_tag: str = ""
        """ 场景标签 """
        self.character_list: set = set()
        """ 场景内角色列表 """


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
        self.age: int = 17
        """ 角色年龄 """
        self.end_age: int = 74
        """ 角色预期寿命 """
        self.intimate: int = 0
        """ 角色与玩家的亲密度 """
        self.graces: int = 0
        """ 角色的魅力值 """
        self.hit_point_max: int = 0
        """ 角色最大HP """
        self.hit_point: int = 0
        """ 角色当前HP """
        self.mana_point_max: int = 0
        """ 角色最大MP """
        self.mana_point: int = 0
        """ 角色当前MP """
        self.sex_experience: Dict[int, int] = {}
        """ 角色的性经验数据 """
        self.sex_grade: Dict[str, str] = {}
        """ 角色的性等级描述数据 """
        self.state: int = 0
        """ 角色当前状态 """
        self.engraving: Dict[str, int] = {}
        """ 角色的刻印数据 """
        self.clothing: Dict[int, Dict[UUID, Clothing]] = {}
        """
        角色拥有的服装数据
        服装穿戴位置:服装唯一id:服装数据
        """
        self.clothing_data: Dict[int, Set] = {}
        """
        角色拥有的服装类型数据集合
        服装表id:服装唯一id
        """
        self.item: Set = set()
        """ 角色拥有的道具id集合 """
        self.height: Height = Height()
        """ 角色的身高数据 """
        self.weight: float = 0
        """ 角色的体重数据 """
        self.measurements: Measurements = Measurements()
        """ 角色的三围数据 """
        self.behavior: Behavior = Behavior()
        """ 角色当前行为状态数据 """
        self.gold: int = 0
        """ 角色所持金钱数据 """
        self.position: List[str] = ["0"]
        """ 角色当前坐标数据 """
        self.classroom: str = ""
        """ 角色所属班级坐标 """
        self.officeroom: List[str] = []
        """ 角色所属办公室坐标 """
        self.knowledge: Dict[int, int] = {}
        """ 角色知识技能等级数据 """
        self.language: Dict[int, int] = {}
        """
        角色语言技能等级数据
        语言id:经验
        """
        self.mother_tongue: int = 0
        """ 角色母语 """
        self.knowledge_interest: Dict[int, int] = {}
        """ 角色天赋数据 """
        self.language_interest: Dict[int, int] = {}
        """ 角色语言天赋数据 """
        self.dormitory: str = ""
        """ 角色宿舍坐标 """
        self.birthday: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 角色生日数据 """
        self.weight_tem: int = 1
        """ 角色体重模板 """
        self.bodyfat_tem: int = 1
        """ 角色体脂率模板 """
        self.bodyfat: int = 0
        """ 角色体脂率数据 """
        self.sex_experience_tem: int = 0
        """ 角色性经验模板 """
        self.clothing_tem: int = 0
        """ 角色生成服装模板 """
        self.chest_tem: int = 0
        """ 角色罩杯模板 """
        self.chest: Chest = Chest()
        """ 角色罩杯数据 """
        self.nature: Dict[int, int] = {}
        """ 角色性格数据 """
        self.status: Dict[int, int] = {}
        """ 角色状态数据 状态id:状态数值 """
        self.put_on: Dict[int, UUID] = {}
        """
        角色已穿戴服装数据
        穿着类型:服装id
        """
        self.hit_point_tem: int = 1
        """ 角色HP模板 """
        self.mana_point_tem: int = 1
        """ 角色MP模板 """
        self.social_contact: Dict[int, Set] = {}
        """ 角色社交关系数据 关系类型:角色id集合 """
        self.social_contact_data: Dict[int, int] = {}
        """ 角色社交关系数据 角色id:关系类型 """
        self.social_contact_last_time: Dict[int, datetime.datetime] = {}
        """ 指定角色最后与自己社交的时间 """
        self.social_contact_last_cut_down_time: Dict[int, datetime.datetime] = {}
        """ 指定角色上次扣除好感时间 """
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
        self.first_kiss_id: int = -1
        """ 初吻对象 -1为无 """
        self.first_kiss_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 初吻时间 """
        self.first_kiss_place: List[str] = ["0"]
        """ 初吻地点 """
        self.taste_semen: int = 0
        """ 饮精精液量计数 """
        self.first_sex_id: int = -1
        """ 处女对象 -1为无 """
        self.first_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ 处女时间 """
        self.first_sex_place: List[str] = ["0"]
        """ 处女地点 """
        self.sex_semen: int = 0
        """ V注入精液量计数 """
        self.first_a_sex_id: int = -1
        """ A处女对象 -1为无 """
        self.first_a_sex_time: datetime.datetime = datetime.datetime(1, 1, 1)
        """ A处女时间 """
        self.first_a_sex_place: List[str] = ["0"]
        """ A处女地点 """
        self.a_sex_semen: int = 0
        """ A注入精液量计数 """
        self.breast_semen: int = 0
        """ 胸部精液量计数 """
        self.hand_semen: int = 0
        """ 手部精液ml数 """
        self.foot_semen: int = 0
        """ 脚部精液ml数 """
        self.urethral_semen: int = 0
        """ 尿道精液ml数 """
        self.first_hand_in_hand: int = -1
        """ 初次牵手对象 -1为无 """
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
        self.talk_count : int = 0
        """ 角色聊天次数计数器 """
        self.talk_time: datetime.datetime = None
        """ 角色上次聊天时间 """
        self.is_h : bool = 0
        """ 在H模式中 """
        self.is_follow : bool = 0
        """ 正跟随玩家 """


class TeacherTimeTable:
    """教师上课时间数据结构体"""

    def __init__(self):
        self.class_room: List[str] = []
        """ 上课教室 """
        self.week_day: int = 0
        """ 周几 """
        self.class_times: int = 0
        """ 第几节课 """
        self.course: int = 0
        """ 科目 """
        self.time: int = 0
        """ 上课时间 """
        self.end_time: int = 0
        """ 下课时间 """


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
        self.course_data: Dict[int, Dict[int, Dict[int, int]]] = {}
        """
        各个学校各年级各科目课时数据
        学校id:年级:科目id:每周课时
        """
        self.course_time_table_data: Dict[int, Dict[int, Dict[int, Dict[int, int]]]] = {}
        """
        各个学校各年级课程表数据
        学校id:年级:周几:第几节课:科目id
        """
        self.course_school_phase_knowledge_experience: Dict[int, Dict[int, Dict[int, Dict[int, int]]]] = {}
        """
        各个学校各学年各技能理论增长经验总量
        学校id:年级:课程:技能:经验
        """
        self.course_school_phase_language_experience: Dict[int, Dict[int, Dict[int, Dict[int, int]]]] = {}
        """
        各个学校各学年各语言理论增长经验总量
        学校id:年级:课程:语言:经验
        """
        self.teacher_course_experience: Dict[int, Dict[int, int]] = {}
        """
        教师科目经验
        科目id:教师id:经验
        """
        self.classroom_teacher_data: Dict[str, Dict[str, Dict[int, Set]]] = {}
        """
        各班级各科目教师配置数据
        年级房间标签(Classroom_n):教室路径:科目id:教师集合
        """
        self.teacher_school_timetable: Dict[int, List[TeacherTimeTable]] = {}
        """
        各老师每周上课数据
        老师id:上课数据列表
        """
        self.teacher_class_week_day_data: Dict[int, Set] = {}
        """ 各老师每周工作日集合 """
        self.class_timetable_teacher_data: Dict[int, Dict[int, Dict[str, Dict[int, Dict[int, int]]]]] = {}
        """
        各学校各班级上课时间对应教师数据
        学校id:年级id:班级id:星期:课时:老师id
        """
        self.teacher_class_time_table: Dict[
            int, Dict[int, Dict[int, Dict[int, Dict[int, Dict[str, int]]]]]
        ] = {}
        """
        各班级各老师上课时间表
        周几:学校id:年级id:上课时间:教师id:教室id:科目
        """
        self.teacher_phase_table: Dict[int, int] = {}
        """ 各老师所在年级 """
        self.classroom_students_data: Dict[str, Set[str]] = {}
        """ 各班级学生集合 """
        self.old_character_id: int = 0
        """ 离开场景面板前在场景中查看的角色id """
        self.total_number_of_people_of_all_ages: Dict[str, int] = {}
        """ 各年龄段总人数 """
        self.total_bodyfat_by_age: dict = {}
        """ 各年龄段总体脂率 """
        self.average_bodyfat_by_age: dict = {}
        """ 各年龄段平均体脂率 """
        self.total_height_by_age: dict = {}
        """ 各年龄段总身高 """
        self.average_height_by_age: dict = {}
        """ 各年龄段平均身高 """
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
        self.course_time_status: dict = {}
        """ 当前上课时间状态 """
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


class TargetChange:
    """角色关系变化结构体"""

    def __init__(self):
        self.old_social: int = 0
        """ 旧关系 """
        self.new_social: int = 0
        """ 新关系 """
        self.status: Dict[int, int] = {}
        """ 状态变化 """
        self.favorability: int = 0
        """ 好感度变化 """
        self.trust: int = 0
        """ 信赖度变化 """
        self.sex_experience: Dict[int, int] = {}
        """ 性经验变化 """
        self.experience: Dict[int, int] = {}
        """ 经验变化 """


class CharacterStatusChange:
    """角色属性状态变更结构体"""

    def __init__(self):
        self.hit_point: int = 0
        """ hp变化 """
        self.mana_point: int = 0
        """ mp变化 """
        self.status: Dict[int, int] = {}
        """ 状态变化 """
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
