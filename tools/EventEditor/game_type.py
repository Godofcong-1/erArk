class Event:
    """事件对象"""

    def __init__(self):
        """初始化事件对象"""
        self.uid: str = ""
        """ 事件唯一id """
        self.adv_id: str = ""
        """ 事件所属advnpcid """
        self.status_id: str = ""
        """ 事件所属状态id """
        self.start: bool = 0
        """ 是否是状态开始时的事件 """
        self.type: int = 1
        """ 事件类型(0不进行指令结算，1正常，2结算后置) """
        self.text: str = ""
        """ 事件描述文本 """
        self.premise: dict = {}
        """ 事件的前提集合 """
        self.settle: dict = {}
        """ 事件的结算器集合 """
        self.effect: dict = {}
        """ 事件的结算集合 """
