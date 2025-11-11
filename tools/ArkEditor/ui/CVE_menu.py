from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
)
from PySide6.QtGui import QFont
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class CVEMenu(QDialog):
    """综合型基础数值结算选择对象"""

    def __init__(self):
        """初始化综合型基础数值结算复选框"""
        super(CVEMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        elif cache_control.now_edit_type_flag == 0:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.ABCD_button_layout = QHBoxLayout()
        self.resize(1000,50)

        # 一段说明文字，用来介绍各个功能，位置在最上面的第一行
        self.cve_text = QLabel("用于实现数值方面的综合型万用结算")
        self.cve_text.setFont(self.font)
        self.layout.addWidget(self.cve_text)

        # A数值为对象，仅在"角色id为"时出现a2文本框
        self.cve_a = QComboBox()
        self.cve_a.addItems(["自己", "交互对象", "角色id为"])
        self.cve_a.setCurrentIndex(0)
        self.cve_a.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cve_a)
        self.cve_a2 = QTextEdit("0")
        self.cve_a2.setFont(self.font)
        self.cve_a2.setFixedHeight(32)
        self.cve_a2.setFixedWidth(50)
        self.cve_a2.setVisible(False)
        self.ABCD_button_layout.addWidget(self.cve_a2)
        self.cve_a.currentIndexChanged.connect(self.change_a2)

        # B数值为属性，A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖
        self.cve_b1 = QComboBox()
        self.cve_b1.addItems(["待选择", "好感", "信赖", "能力", "素质", "宝珠", "经验", "状态", "口上用flag", "绝顶", "嵌套父事件", "指定角色id为交互对象", "移动"])
        self.cve_b1.setCurrentIndex(0)
        self.cve_b1.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cve_b1)

        # b2根据b1会出现不同的选项
        self.cve_b2 = QComboBox()
        self.cve_b2.addItems([""])
        self.cve_b2.setCurrentIndex(0)
        self.cve_b2.setFont(self.font)
        self.cve_b2.setVisible(False)
        self.cve_b1.currentIndexChanged.connect(self.change_b2)
        self.ABCD_button_layout.addWidget(self.cve_b2)

        # C数值为判定方式
        self.cve_c = QComboBox()
        self.cve_c.addItems(["增加", "减少", "变为"])
        self.cve_c.setCurrentIndex(0)
        self.cve_c.setFont(self.font)
        self.ABCD_button_layout.addWidget(self.cve_c)

        # D数值为判定值
        self.cve_d = QTextEdit("0")
        self.cve_d.setFont(self.font)
        self.cve_d.setFixedHeight(32)
        self.cve_d.setFixedWidth(50)
        self.ABCD_button_layout.addWidget(self.cve_d)

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
        cve_a = self.cve_a.currentText()
        cve_a_value = "A1"
        if cve_a == "自己":
            cve_a_value = "A1"
        elif cve_a == "交互对象":
            cve_a_value = "A2"
        elif cve_a == "角色id为":
            cve_a_value = "A3|" + self.cve_a2.toPlainText()
            cve_a = "角色id为" + self.cve_a2.toPlainText()
        cve_b1 = self.cve_b1.currentText()
        if len(self.cve_b2.currentText().split("|")) == 2:
            cve_b2 = self.cve_b2.currentText().split("|")[1]
        elif len(self.cve_b2.currentText().split("|")) == 1:
            cve_b2 = self.cve_b2.currentText().split("|")[0]
        else:
            cve_b2 = ""
        if cve_b1 == "待选择":
            cve_b_value = ""
        elif cve_b1 == "好感":
            cve_b_value = "F"
        elif cve_b1 == "信赖":
            cve_b_value = "X"
        elif cve_b1 == "能力":
            cve_b_value = "A|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "素质":
            cve_b_value = "T|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "宝珠":
            cve_b_value = "J|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "经验":
            cve_b_value = "E|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "状态":
            cve_b_value = "S|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "口上用flag":
            cve_b_value = "Flag|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "绝顶":
            cve_b_value = "Climax|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "嵌套父事件":
            cve_b_value = "Father|" + self.cve_b2.currentText().split("|")[0]
        elif cve_b1 == "指定角色id为交互对象":
            cve_b_value = "ChangeTargetId|0"
        elif cve_b1 == "移动":
            cve_b_value = "Move|0"
        cve_c = self.cve_c.currentText()
        if cve_c == "增加":
            cve_c_value = "G"
        elif cve_c == "减少":
            cve_c_value = "L"
        elif cve_c == "变为":
            cve_c_value = "E"
        else:
            cve_c_value = cve_c
        cve_d = self.cve_d.toPlainText()
        cve_d_value = cve_d
        # 空值时默认为0
        if cve_d_value == "":
            cve_d_value = "0"

        # 指定角色id为交互对象时特殊处理
        if cve_b1 == "指定角色id为交互对象":
            # 不显示c和d
            cve_c = ""
            cve_d = ""

        # 拼接结算字符串
        cve_str = f"综合数值结算  {cve_a}{cve_b1}{cve_b2}{cve_c}{cve_d}"
        cve_value_str = f"CVE_{cve_a_value}_{cve_b_value}_{cve_c_value}_{cve_d_value}"
        # print(f"debug cve_str: {cve_str}, cve_value_str: {cve_value_str}")

        # 更新结算数据
        cache_control.effect_data[cve_value_str] = cve_str

        # 更新结算列表
        if cache_control.now_edit_type_flag == 1:
            cache_control.now_event_data[cache_control.now_select_id].effect[cve_value_str] = 1
        cache_control.item_effect_list.update()
        # self.close()

    def cancel(self):
        """点击取消按钮"""
        self.close()

    def change_a2(self, index: int):
        """改变a2的选项"""
        if index == 2:
            self.cve_a2.setVisible(True)
        else:
            self.cve_a2.setVisible(False)

    def reset_c(self):
        """重置c的选项"""
        self.cve_c.clear()
        self.cve_c.addItems(["增加", "减少", "变为"])
        self.cve_c.setCurrentIndex(0)
        self.cve_c.setFont(self.font)
        self.cve_c.setVisible(True)

    def reset_option(self):
        """重置选项"""
        self.cve_a.setVisible(True)
        items_count = self.cve_a.count()
        if items_count != 3:
            self.cve_a.clear()
            self.cve_a.addItems(["自己", "交互对象", "角色id为"])
            self.cve_a.setVisible(True)
        self.cve_b2.setVisible(True)
        self.cve_b2.clear()

        self.cve_c.clear()
        self.cve_c.addItems(["增加", "减少", "变为"])
        self.cve_c.setCurrentIndex(0)
        self.cve_c.setFont(self.font)
        self.cve_c.setVisible(True)

        self.cve_d.setPlainText("0")
        self.cve_d.setVisible(True)

    def change_b2(self, index: int):
        """改变b2的选项"""
        self.reset_option()
        if index == 0:
            self.cve_b2.setVisible(False)
        elif index == 1:
            self.cve_b2.setVisible(False)
            self.cve_text.setText("好感度的-1级和1~8级分别为：负数，100，500，1000，2500，5000，10000，50000，100000，此处使用的为好感的具体数值，不是等级")
        elif index == 2:
            self.cve_b2.setVisible(False)
            self.cve_text.setText("信赖度的-1级和18级分别为：负数，25%，50%，75%，100%，150%，200%，250%，300%\n此处使用的为信赖度的具体数值，不是等级，只填数字，不加百分号")
        elif index == 3:
            self.cve_b2.clear()
            for ability_id, ability_name in cache_control.ability_data.items():
                self.cve_b2.addItem(f"{ability_id}|{ability_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("能力最高为8级")
        elif index == 4:
            self.cve_b2.clear()
            for talent_id, talent_name in cache_control.talent_data.items():
                self.cve_b2.addItem(f"{talent_id}|{talent_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("1为有该素质，0为无该素质")
        elif index == 5:
            self.cve_b2.clear()
            for juel_id, juel_name in cache_control.juel_data.items():
                self.cve_b2.addItem(f"{juel_id}|{juel_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("宝珠是用来升级能力或获得素质的")
        elif index == 6:
            self.cve_b2.clear()
            for experience_id, experience_name in cache_control.experience_data.items():
                self.cve_b2.addItem(f"{experience_id}|{experience_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("每次指令都会获得1对应经验")
        elif index == 7:
            self.cve_b2.clear()
            for state_id, state_name in cache_control.state_data.items():
                self.cve_b2.addItem(f"{state_id}|{state_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_text.setText("状态值的0~10级的升级阈值分别为：100，500，1000，2500，6000，12000，30000，50000，75000，99999，100000，此处使用的为状态值的具体数值，不是等级")
        elif index == 8:
            self.cve_b2.clear()
            # b2提供一个文本框，用来输入flag的编号，最多支持10个flag
            for i in range(50):
                self.cve_b2.addItem(str(i))
            self.cve_text.setText("口上用flag是用来实现供口上作者自定义的数据变量，可以用来实现一些特殊的前提\n口上用flag的数据类型为int，默认值为0，最多支持50个flag（即编号为0~49）\n口上用flag无法独立使用，需要用编辑器的事件中的结算来进行修改\n如【用flag0来记录触发某个指令或某句口上的次数】，【用flag1来记录自己设定的某种攻略的阶段】，【用flag2来衡量自己设定的角色对玩家的某种感情】等等")
        elif index == 9:
            self.cve_b2.clear()
            for organ_id, organ_name in cache_control.organ_data.items():
                self.cve_b2.addItem(f"{organ_id}|{organ_name}")
            self.cve_b2.setCurrentIndex(0)
            self.cve_c.clear()
            self.cve_c.addItems(["变为", "增加"])
            self.cve_c.setCurrentIndex(0)
            self.cve_text.setText("触发一次该部位的绝顶或射精，NPC的0为小绝顶，1为普绝顶，2为强绝顶，玩家则为0射精，1大量射精，2超大量射精。\n\n选择[增加]时，效果为从小绝顶开始，同时触发多次不同强度的绝顶，如增加 1 即为同时触发0小绝顶和1普绝顶，以此类推\n选择[变为]则变为哪个就触发哪个，如变为 2 即为触发强绝顶\n\n射精时，如果玩家的阴茎已经在NPC的某部位(包括身体部位和服装部位)，则默认在该部位射精，否则将弹出部位选择面板\n如果想指定指定射精部位，请使用 [H_阴茎位置] 中的 [改变阴茎位置] 的结算进行指定后，再使用本结算进行射精")
        elif index == 10:
            self.cve_a.clear()
            self.cve_a.setVisible(False)
            self.cve_b2.clear()
            for i in range(100):
                self.cve_b2.addItem(str(i))
            self.cve_c.clear()
            self.cve_c.addItems(["变为"])
            self.cve_c.setCurrentIndex(0)
            self.cve_text.setText("嵌套父事件，用于在事件编辑中展开多层嵌套父子事件\n\n①如果仅需要单层的父子选项事件请使用[整体修改]-[系统量]-[基础]\n②本前提需要配合[综合数值前提]中的[嵌套子事件]使用\n③同数字的父事件会展开同数字的子事件，如，序号0的嵌套父事件会检索序号0的嵌套子事件，以此类推\n\n例子：父事件A1（嵌套父事件=0）\n  一级子事件B1（嵌套子事件=0↔A1，嵌套父事件=1）、B2（嵌套子事件=0↔A1，嵌套父事件=2）\n  二级子事件C1（嵌套子事件=1↔B1），C2（嵌套子事件=1↔B1），C3（嵌套子事件=2↔B2），C4（嵌套子事件=2↔B2）\n")
        elif index == 11:
            self.cve_a.clear()
            self.cve_a.addItems(["角色id为"])
            self.cve_a2.setVisible(True)
            self.cve_b2.setVisible(False)
            self.cve_c.setVisible(False)
            self.cve_d.setVisible(False)
            self.cve_text.setText("选择当前场景中的指定id的角色作为自己的交互对象\n\n需要搭配综合数值前提中的，当前场景中有特定id的角色存在，的前提一同使用，当前场景中没有该id角色时会无法起效\n当有多个结算时，本结算需要放到第一个，以便第一个执行\n玩家的id固定为0")
        elif index == 12:
            self.cve_b2.setVisible(False)
            self.cve_c.clear()
            self.cve_c.addItems(["寻路"])
            self.cve_c.addItems(["瞬移"])
            self.cve_c.setCurrentIndex(0)
            # self.cve_d的值改为Dr_Office，宽度改为200
            self.cve_d.setPlainText("Dr_Office")
            self.cve_d.setFixedWidth(200)
            self.cve_text.setText("用来实现角色在场景中的移动，通过输入一个Scenetag而移动到一个地点\n\n依靠地点的[Scenetag]属性来指定目标地点，在游戏根目录下的[data\map]文件夹中有全地点的数据\n如[data\map\中枢\博士办公室\Scene.json]可以查询到[博士办公室]的 SceneTag = Dr_Office\n每个地点的SceneTag都至少有一个，可以有多个\n如果输入的SceneTag不只有一个，而是有多个对应地点，则随机选取一个为目标进行移动\n如果SceneTag没有对应地点，则不进行移动\n如[龙门食坊]有以下SceneTag：Lungmen_Eatery|Restaurant|Food_Shop\nLungmen_Eatery：仅龙门食坊有的单独tag\nRestaurant：包括龙门食坊在内的，贸易街的所有餐馆都有该tag\nFood_Shop：包括贸易街餐馆、小贩、食堂取餐区在内的所有可以买食物的地方都有该tag\n\n移动方式有[寻路]和[瞬移]两种，推荐使用[寻路]，仅在特殊情况下再使用[瞬移]\n[寻路]：游戏中角色正常移动方式，角色会获取从当前地点到目标地点的完整路径，随着时间的前进，每步移动到下一个地点\n        每次移动时判定时间流逝的影响、路上遇到的其他角色、每个地点的情况等结算，直到抵达最终目标地点而停止\n        中途可能因打招呼、疲劳休息等结算而短暂搁置到处理完毕后再继续移动，或因门锁、未开放等结算而提前终止移动\n        玩家的移动会自带时间前进，NPC的移动不带时间前进\n[瞬移]：无视所有情况，跳过一切判定，不进行任何其他结算，直接从当前位置瞬间移动到指定位置")

        self.cve_b = self.cve_b2

