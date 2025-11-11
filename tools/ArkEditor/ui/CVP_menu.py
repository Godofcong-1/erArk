from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QPushButton,
    QComboBox,
    QTextEdit,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtGui import QFont, Qt
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class CVPMenu(QDialog):
    """综合型基础数值前提选择对象"""

    def __init__(self):
        """初始化综合型基础数值前提复选框"""
        super(CVPMenu, self).__init__()
        self.setWindowTitle("综合型基础数值前提")
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.ABCD_button_layout = QHBoxLayout()
        self.resize(1000,50)

        # 一段说明文字，用来介绍各个功能，位置在最上面的第一行
        self.cvp_text = QLabel("用于实现数值方面的综合型万用前提")
        self.cvp_text.setFont(self.font)
        self.layout.addWidget(self.cvp_text)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cvp_a = QComboBox()
        self.cvp_a.addItems(["自己", "交互对象", "角色id为"])
        self.cvp_a.setCurrentIndex(0)
        self.cvp_a.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cvp_a)
        self.cvp_a2 = QTextEdit("0")
        self.cvp_a2.setFont(self.font)
        self.cvp_a2.setFixedHeight(32)
        self.cvp_a2.setFixedWidth(50)
        self.cvp_a2.setVisible(False)
        self.ABCD_button_layout.addWidget(self.cvp_a2)
        self.cvp_a.currentIndexChanged.connect(self.change_a2)

        # B数值为属性，A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖
        self.cvp_b1 = QComboBox()
        self.cvp_b1.addItems(["待选择", "好感", "信赖", "能力", "素质", "宝珠", "经验", "状态", "攻略程度", "时间", "口上用flag", "前指令", "嵌套子事件", "其他角色在场", "部位污浊", "触发权重", "绳子捆绑", "角色扮演", "阴茎位置", "射精位置", "身份关系", "礼物"])
        self.cvp_b1.setCurrentIndex(0)
        self.cvp_b1.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cvp_b1)

        # b2根据b1会出现不同的选项
        self.cvp_b2 = QComboBox()
        self.cvp_b2.addItems([""])
        self.cvp_b2.setCurrentIndex(0)
        self.cvp_b2.setFont(self.font)
        self.cvp_b2.setVisible(False)
        self.cvp_b1.currentIndexChanged.connect(self.change_b2)
        self.ABCD_button_layout.addWidget(self.cvp_b2)

        # C数值为判定方式
        self.cvp_c = QComboBox()
        self.cvp_c.addItems(["大于", "小于", "等于", "大于等于", "小于等于", "不等于"])
        self.cvp_c.setCurrentIndex(0)
        self.cvp_c.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cvp_c)

        # D数值为判定值
        self.cvp_d = QTextEdit("0")
        self.cvp_d.setFont(self.font)
        self.cvp_d.setFixedHeight(32)
        self.cvp_d.setFixedWidth(50)
        self.ABCD_button_layout.addWidget(self.cvp_d)

        self.layout.addLayout(self.ABCD_button_layout)

        # 添加确定按钮与取消按钮
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.ok)
        self.ok_button.setFont(self.font)
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFont(self.font)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def ok(self):
        """点击确定按钮"""
        # 获得当前abcd的值
        cvp_a = self.cvp_a.currentText()
        cvp_a_value = "A1"
        if cvp_a == "自己":
            cvp_a_value = "A1"
        elif cvp_a == "交互对象":
            cvp_a_value = "A2"
        elif cvp_a == "角色id为":
            cvp_a_value = "A3|" + self.cvp_a2.toPlainText()
            cvp_a = "角色id为" + self.cvp_a2.toPlainText()
        cvp_b1 = self.cvp_b1.currentText()
        if len(self.cvp_b2.currentText().split("|")) == 2:
            cvp_b2 = self.cvp_b2.currentText().split("|")[1]
        elif len(self.cvp_b2.currentText().split("|")) == 1:
            cvp_b2 = self.cvp_b2.currentText().split('|')[0]
        else:
            cvp_b2 = ""
        if cvp_b1 == "待选择":
            cvp_b_value = ""
        elif cvp_b1 == "好感":
            cvp_b_value = "F"
        elif cvp_b1 == "信赖":
            cvp_b_value = "X"
        elif cvp_b1 == "能力":
            cvp_b_value = "A|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "素质":
            cvp_b_value = "T|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "宝珠":
            cvp_b_value = "J|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "经验":
            cvp_b_value = "E|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "状态":
            cvp_b_value = "S|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "攻略程度":
            cvp_b_value = "G"
        elif cvp_b1 == "时间":
            cvp_b_value = "Time"
        elif cvp_b1 == "口上用flag":
            cvp_b_value = "Flag|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "前指令":
            cvp_b_value = "Instruct|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "嵌套子事件":
            cvp_b_value = "Son|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "其他角色在场":
            cvp_b_value = "OtherChara|0"
        elif cvp_b1 == "部位污浊":
            cvp_b_value = "Dirty|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "触发权重":
            cvp_b_value = "Weight|0"
        elif cvp_b1 == "绳子捆绑":
            cvp_b_value = "Bondage|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "角色扮演":
            cvp_b_value = "Roleplay|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "阴茎位置":
            cvp_b_value = "PenisPos|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "射精位置":
            cvp_b_value = "ShootPos|" + self.cvp_b2.currentText().split("|")[0]
        elif cvp_b1 == "身份关系":
            cvp_b_value = "Relationship|" + self.cvp_b2.currentText()
        elif cvp_b1 == "礼物":
            cvp_b_value = "Gift|" + self.cvp_b2.currentText().split("|")[0]
        cvp_c = self.cvp_c.currentText()
        if cvp_c == "大于":
            cvp_c_value = "G"
        elif cvp_c == "小于":
            cvp_c_value = "L"
        elif cvp_c == "等于":
            cvp_c_value = "E"
        elif cvp_c == "大于等于":
            cvp_c_value = "GE"
        elif cvp_c == "小于等于":
            cvp_c_value = "LE"
        elif cvp_c == "不等于":
            cvp_c_value = "NE"
        else:
            cvp_c_value = cvp_c
        cvp_d = self.cvp_d.toPlainText()
        cvp_d_value = cvp_d

        # 拼接前提字符串
        cvp_str = f"综合数值前提  {cvp_a}{cvp_b1}{cvp_b2}{cvp_c}{cvp_d}"
        cvp_value_str = f"CVP_{cvp_a_value}_{cvp_b_value}_{cvp_c_value}_{cvp_d_value}"
        # print(f"debug cvp_str: {cvp_str}, cvp_value_str: {cvp_value_str}")

        # 更新前提数据
        cache_control.premise_data[cvp_value_str] = cvp_str

        # 更新前提列表
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].premise[cvp_value_str] = 1
        elif cache_control.now_edit_type_flag == 0:
            cache_control.now_talk_data[cache_control.now_select_id].premise[cvp_value_str] = 1
        cache_control.item_premise_list.update()
        # self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cvp_a2.setVisible(True)
        else:
            self.cvp_a2.setVisible(False)

    def reset_option(self):
        """重置选项"""
        self.cvp_a.setVisible(True)
        items_count = self.cvp_a.count()
        if items_count != 3:
            self.cvp_a.clear()
            self.cvp_a.addItems(["自己", "交互对象", "角色id为"])
            self.cvp_a.setVisible(True)
        self.cvp_b2.setVisible(True)
        self.cvp_b2.clear()

        self.cvp_c.clear()
        self.cvp_c.addItems(["大于", "小于", "等于", "大于等于", "小于等于", "不等于"])
        self.cvp_c.setCurrentIndex(0)
        self.cvp_c.setFont(self.font)
        self.cvp_c.setVisible(True)

        self.cvp_d.setVisible(True)

    def change_b2(self, index: int):
        """改变b2的选项"""
        self.reset_option()
        if index == 0:
            self.cvp_b2.setVisible(False)
        elif index == 1:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("好感度的-1级和1~8级分别为：负数，100，500，1000，2500，5000，10000，50000，100000，此处使用的为好感的具体数值，不是等级")
        elif index == 2:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("信赖度的-1级和18级分别为：负数，25%，50%，75%，100%，150%，200%，250%，300%\n此处使用的为信赖度的具体数值，不是等级，只填数字，不加百分号")
        elif index == 3:
            self.cvp_b2.clear()
            for ability_id, ability_name in cache_control.ability_data.items():
                self.cvp_b2.addItem(f"{ability_id}|{ability_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("能力最高为8级")
        elif index == 4:
            self.cvp_b2.clear()
            for talent_id, talent_name in cache_control.talent_data.items():
                self.cvp_b2.addItem(f"{talent_id}|{talent_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("1为有该素质，0为无该素质")
        elif index == 5:
            self.cvp_b2.clear()
            for juel_id, juel_name in cache_control.juel_data.items():
                self.cvp_b2.addItem(f"{juel_id}|{juel_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("宝珠是用来升级能力或获得素质的")
        elif index == 6:
            self.cvp_b2.clear()
            for experience_id, experience_name in cache_control.experience_data.items():
                self.cvp_b2.addItem(f"{experience_id}|{experience_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("每次指令都会获得1对应经验")
        elif index == 7:
            self.cvp_b2.clear()
            for state_id, state_name in cache_control.state_data.items():
                self.cvp_b2.addItem(f"{state_id}|{state_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("状态值的0~10级的升级阈值分别为：100，500，1000，2500，6000，12000，30000，50000，75000，99999，100000，此处使用的为状态值的具体数值，不是等级")
        elif index == 8:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("攻略有正数的【爱情系】和负数的【隶属系】两种路线\n爱情系的1~4分别为思慕、恋慕、恋人、爱侣，隶属系的-1~-4分别为屈从、驯服、宠物、奴隶\n备注：数值会等于但不会越过0，如，当选择爱情系的≤2时，只会有2的恋慕、1的思慕和0的无陷落，不会到负数的隶属系，其他情况同理")
        elif index == 9:
            self.cvp_b2.setVisible(False)
            self.cvp_text.setText("时间为一天24小时制，如果要定起止时间的话，可以搭配使用【时间大于等于A】和【时间小于等于B】的两个前提来实现")
        elif index == 10:
            self.cvp_b2.clear()
            # b2提供一个文本框，用来输入flag的编号，最多支持10个flag
            for i in range(50):
                self.cvp_b2.addItem(str(i))
            self.cvp_text.setText("口上用flag是用来实现供口上作者自定义的数据变量，可以用来实现一些特殊的前提\n口上用flag的数据类型为int，默认值为0，最多支持50个flag（即编号为0~49）\n口上用flag无法独立使用，需要用编辑器的事件中的结算来进行修改\n如【用flag0来记录触发某个指令或某句口上的次数】，【用flag1来记录自己设定的某种攻略的阶段】，【用flag2来衡量自己设定的角色对玩家的某种感情】等等")
        elif index == 11:
            self.cvp_a.setVisible(False)
            self.cvp_b2.clear()
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于", "不等于"])
            for status_id, status_name in cache_control.behavior_data.items():
                status_data = cache_control.behavior_all_data[status_id]
                # 跳过玩家无法触发的状态
                if status_data["trigger"] == "npc":
                    continue
                # 跳过二段结算
                if "二段结算" in status_data["type"]:
                    break
                self.cvp_b2.addItem(f"{status_id}|{status_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_text.setText("前指令可以用来检测玩家上一次输入的指令，用于实现两次指令之间的联动效果\n本前提只判断玩家，所以角色选择会锁定为玩家，且只能使用[等于]或者[不等于]，没有其他逻辑")
        elif index == 12:
            self.cvp_a.setVisible(False)
            self.cvp_b2.clear()
            for i in range(100):
                self.cvp_b2.addItem(str(i))
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_text.setText("嵌套子事件，用于在事件编辑中展开多层嵌套父子事件\n\n①如果仅需要单层的父子选项事件请使用[整体修改]-[系统状态]\n②本前提需要配合[综合数值结算]中的[嵌套父事件]使用\n③同数字的父事件会展开同数字的子事件，如，序号0的嵌套父事件会检索序号0的嵌套子事件，以此类推\n④子事件除本前提外，还可以拥有父事件之外的独立前提。若设置了独立前提，满足时则正常显示，不满足时不显示该子事件的选项\n\n例子：父事件A1（嵌套父事件=0）\n  一级子事件B1（嵌套子事件=0↔A1，嵌套父事件=1）、B2（嵌套子事件=0↔A1，嵌套父事件=2）\n  二级子事件C1（嵌套子事件=1↔B1），C2（嵌套子事件=1↔B1），C3（嵌套子事件=2↔B2），C4（嵌套子事件=2↔B2）\n")
        elif index == 13:
            self.cvp_a.clear()
            self.cvp_a.addItems(["角色id为"])
            self.cvp_a2.setVisible(True)
            self.cvp_b2.setVisible(False)
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_text.setText("检测特定id的角色是否在场的前提，用于和其他角色进行联动\n\n等于1就是在场，等于0就是不在场")
        elif index == 14:
            self.cvp_b2.clear()
            for body_id, body_name in cache_control.body_data.items():
                self.cvp_b2.addItem(f"B{body_id}|{body_name}")
            for cloth_id, cloth_name in cache_control.clothing_data.items():
                self.cvp_b2.addItem(f"C{cloth_id}|{cloth_name}")
            self.cvp_text.setText("检测部位的精液量，包括身体部位与服装部位，单位是ml\n\n如果角色没有该部位，比如没有兽角，或者没有穿内裤等，则该部位精液量固定为0")
        elif index == 15:
            self.cvp_a.setVisible(False)
            self.cvp_b2.setVisible(False)
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_text.setText("自由设定触发本条目的权重，\n正整数，最小为1，最大999\n设定后将锁定为固定值，优先度高于其他任何权重计算")
        elif index == 16:
            self.cvp_b2.clear()
            for bondage_id, bondage_name in cache_control.bondage_data.items():
                self.cvp_b2.addItem(f"{bondage_id}|{bondage_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_text.setText("用于判断被绳子捆绑的姿势\n等于1则为该姿势，等于0则为非该姿势")
        elif index == 17:
            self.cvp_b2.clear()
            for role_id, role_name in cache_control.roleplay_data.items():
                self.cvp_b2.addItem(f"{role_id}|{role_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_text.setText("角色扮演前提，用于判断[心控催眠-角色扮演]的状态\n等于1则正在进行该角色扮演，等于0则没有进行该角色扮演")
        elif index == 18:
            self.cvp_a.clear()
            self.cvp_a.setVisible(False)
            self.cvp_b2.clear()
            for body_id, body_name in cache_control.body_data.items():
                self.cvp_b2.addItem(f"B{body_id}|{body_name}")
            for cloth_id, cloth_name in cache_control.clothing_data.items():
                self.cvp_b2.addItem(f"C{cloth_id}|{cloth_name}")
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_d.setText("1")
            self.cvp_text.setText("检测当前玩家阴茎插入目标角色的部位，包括身体部位与服装部位\n等于1为插入该部位\n在游戏中会显示插入XX中，或XX交中，或蹭XX中\n\n在口腔、小穴、子宫、后穴等部位的实际行动表现一般为插入洞内摩擦\n在头发、胸衣、内裤等部位的表现应为包裹摩擦\n在兽角、脸部、饰品、武器等部位应为表面摩擦\n手、足、尾巴等较为灵活的身体部位与其穿着的手套袜子鞋子等可自由适用以上多类\n\n如果玩家没有在插入，则全部位为0\n如果角色没有该部位，比如没有兽角，或者没有穿内裤等，则该部位无法插入，也是0")
        elif index == 19:
            self.cvp_a.clear()
            self.cvp_a.setVisible(False)
            self.cvp_b2.clear()
            for body_id, body_name in cache_control.body_data.items():
                self.cvp_b2.addItem(f"B{body_id}|{body_name}")
            for cloth_id, cloth_name in cache_control.clothing_data.items():
                self.cvp_b2.addItem(f"C{cloth_id}|{cloth_name}")
            self.cvp_c.clear()
            self.cvp_c.addItems(["等于"])
            self.cvp_d.setText("1")
            self.cvp_text.setText("检测当前玩家阴茎在目标角色的哪个部位射精，包括身体部位与服装部位\n等于1为在该部位射精\n用于和二段行为_射精/大量射精/超大量射精配套使用")
        elif index == 20:
            self.cvp_b2.clear()
            self.cvp_b2.addItems(["是玩家的", "是自己的", "是交互对象的", "是指定id角色的"])
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_c.clear()
            self.cvp_c.addItems(["女儿", "父亲", "母亲"])
            self.cvp_c.setCurrentIndex(0)
            self.cvp_d.setText("0")
            self.cvp_text.setText("身份关系前提，用于判断角色间是否为女儿、父亲、母亲等关系\n\n如果不限定是特定角色的女儿或者其他关系，则使用默认为0的角色id即可\n如果是想限定某个干员生的女儿，可以使用[是指定id角色的]，然后将角色id填入文本框\n\n如[交互对象][是玩家的][女儿][0]，则表示交互对象是玩家的女儿，通用所有女儿角色\n如[交互对象][是指定id角色的][女儿][100]，则表示交互对象是角色id为100的角色的女儿")
        elif index == 21:
            self.cvp_b2.clear()
            for gift_id, item_id in cache_control.gift_items_data.items():
                item_name = cache_control.item_data[item_id]
                self.cvp_b2.addItem(f"{gift_id}|{item_name}")
            self.cvp_b2.setCurrentIndex(0)
            self.cvp_c.setVisible(False)
            self.cvp_d.setVisible(False)
            self.cvp_text.setText("用于在赠送礼物指令中判断当前赠送的是哪个礼物，人物应选择礼物的赠送方\n如自己送给对方道歉礼物")

        self.cvp_b = self.cvp_b2

    def eventFilter(self, obj, event):
        """
        事件过滤器：在搜索栏按下回车时触发搜索
        输入：obj -- 事件源对象，event -- 事件对象
        输出：bool，是否拦截事件
        """
        # 判断事件源是否为搜索栏，且事件类型为按键按下
        if obj == self.search_text and event.type() == event.KeyPress:
            # 判断是否为回车键
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.search()
                return True  # 拦截事件，不再向下传递
        return super().eventFilter(obj, event)
