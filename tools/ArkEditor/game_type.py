class Talk:
    """口上对象"""

    def __init__(self):
        """初始化事件对象"""
        self.cid: str = ""
        """ 口上id """
        self.adv_id: str = ""
        """ 口上限定的剧情npcid """
        self.behavior_id: str = ""
        """ 触发口上的行为状态id """
        self.text: str = ""
        """ 口上文本 """
        self.premise: dict = {}
        """ 口上的前提集合 """

class Event:
    """事件对象"""

    def __init__(self):
        """初始化事件对象"""
        self.uid: str = ""
        """ 事件唯一id """
        self.adv_id: str = ""
        """ 事件所属advnpcid """
        self.behavior_id: str = ""
        """ 事件所属状态id """
        self.start: bool = 0
        """ 是否是状态开始时的事件 """
        self.type: int = 1
        """ 事件类型(0跳过指令，1指令前事件后，2事件前指令后) """
        self.text: str = ""
        """ 事件描述文本 """
        self.premise: dict = {}
        """ 事件的前提集合 """
        self.settle: dict = {}
        """ 事件的结算器集合 """
        self.effect: dict = {}
        """ 事件的结算集合 """
        self.comment: str = ""
        """ 事件注释 """

class Chara_Data:
    """角色属性对象"""

    def __init__(self):
        """初始化事件对象"""
        self.AdvNpc: int = 0
        """ 干员编号 """
        self.Name: str = ""
        """ 干员名称 """
        self.Sex: int = 0
        """ 性别 """
        self.Profession: int = 1
        """ 职业 """
        self.Race: int = 1
        """ 种族 """
        self.Nation: int = 0
        """ 势力 """
        self.Birthplace: int = 0
        """ 出身地 """
        self.Hp: int = 0
        """ 初始体力 """
        self.Mp: int = 0
        """ 初始气力 """
        self.Dormitory: str = ""
        """ 初始宿舍 """
        self.Token: str = ""
        """ 信物 """
        self.Introduce_1: str = ""
        """ 人物介绍_1 """
        self.TextColor: str = ""
        """ 字体颜色 """
        self.Ability: dict= {}
        """ 能力 """
        self.Experience: dict = {}
        """ 经验 """
        self.Talent: dict = {}
        """ 素质 """
        self.Cloth: dict = {}
        """ 服装 """

class Commission:
    """
    外勤委托数据结构
    参数:
        cid: int 委托ID
        name: str 委托名称
        country_id: int 国家ID
        level: int 委托等级
        type: str 委托类型
        people: int 需要人数
        time: int 耗时天数
        demand: str 需求字符串
        reward: str 奖励字符串
        related_id: int 前置委托ID
        special: int 是否特殊委托
        description: str 委托描述
    返回:
        None
    功能:
        存储单个外勤委托的全部属性
    """
    def __init__(self, cid, name, country_id, level, type, people, time, demand, reward, related_id, special, description):
        # 初始化各属性
        self.cid = int(cid)
        self.name = name
        self.country_id = int(country_id)
        self.level = int(level)
        self.type = type
        self.people = int(people)
        self.time = int(time)
        self.demand = demand
        self.reward = reward
        self.related_id = int(related_id)
        self.special = int(special)
        self.description = description


class OfficialEvent:
    """
    公务事件数据结构（Plan 23）
    参数:
        row: dict CSV 的一行（键为列名）
        file_name: str 所属文件名（不含扩展名），既是分组名也是 uid 前缀
    返回:
        None
    功能:
        存储单条公务事件的全部属性。选项统一收在 options 里，
        每项为 {"text", "premise", "reason", "tip", "effect"}，
        空着的选项也占位保留，保存时按空串写回。
    """

    OPTION_SUFFIX = ["", "_premise", "_reason", "_tip", "_effect"]

    def __init__(self, row: dict, file_name: str = ""):
        # 基本字段
        self.file_name = file_name
        self.cid = row.get("cid", "")
        self.department = int(row.get("department", 0) or 0)
        self.subject = int(row.get("subject", 1) or 0)
        self.sub_key = int(row.get("sub_key", 0) or 0)
        self.once = int(row.get("once", 0) or 0)
        self.weight = int(row.get("weight", 10) or 0)
        self.premise = row.get("premise", "")
        self.text = row.get("text", "")
        # 四个选项块
        self.options = []
        for index in range(1, 5):
            self.options.append(
                {
                    "text": row.get(f"option_{index}", ""),
                    "premise": row.get(f"option_{index}_premise", ""),
                    "reason": row.get(f"option_{index}_reason", ""),
                    "tip": row.get(f"option_{index}_tip", ""),
                    "effect": row.get(f"option_{index}_effect", ""),
                }
            )

    def to_row(self) -> list:
        """
        转成 CSV 的一行（28 列）
        参数: 无
        返回: list 一行的全部字段
        """
        row = [
            str(self.cid),
            str(self.department),
            str(self.subject),
            str(self.sub_key),
            str(self.once),
            str(self.weight),
            self.premise,
            self.text,
        ]
        for one in self.options:
            row.extend([one["text"], one["premise"], one["reason"], one["tip"], one["effect"]])
        return row
