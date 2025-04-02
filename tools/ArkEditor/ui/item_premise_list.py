from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import cache_control
import function
from ui.premise_menu import PremiseMenu, CVPMenu

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class ItemPremiseList(QWidget):
    """前提表单主体"""

    def __init__(self):
        """初始化前提表单主体"""
        super(ItemPremiseList, self).__init__()
        self.font = font
        self.setFont(self.font)
        main_layout = QVBoxLayout()  # 主布局
        # 标题布局
        title_layout = QVBoxLayout()
        label = QLabel()
        label.setText("前提列表")
        title_layout.addWidget(label)

        # 按钮布局
        button_layout1 = QHBoxLayout()
        change_button = QPushButton("整体修改")
        change_button.clicked.connect(self.change)
        button_layout1.addWidget(change_button)
        reset_button = QPushButton("整体清零")
        reset_button.clicked.connect(self.reset)
        button_layout1.addWidget(reset_button)
        title_layout.addLayout(button_layout1)

        button_layout2 = QHBoxLayout()
        CVP_button = QPushButton("综合型基础数值前提")
        CVP_button.clicked.connect(self.CVP)
        button_layout2.addWidget(CVP_button)
        add_group_button = QPushButton("将当前的所有前提设为新前提组")
        add_group_button.clicked.connect(self.add_group)
        button_layout2.addWidget(add_group_button)
        title_layout.addLayout(button_layout2)

        main_layout.addLayout(title_layout)
        # 文字说明
        self.info_label = QLabel()
        self.info_label.setText("○双击替换，右键展开删除、复制、粘贴菜单\n○指令(一段结算)需要区分触发者自己和交互对象\n○二段结算仅触发者自己，没有交互对象")
        # 前提列表布局
        list_layout = QHBoxLayout()
        self.item_list = QListWidget()
        self.item_list.setWordWrap(True)
        self.item_list.adjustSize()
        self.item_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.item_list.customContextMenuRequested.connect(self.show_context_menu)
        self.item_list.itemDoubleClicked.connect(self.change_this_item)
        list_layout.addWidget(self.item_list)
        main_layout.addWidget(self.info_label)
        main_layout.addLayout(list_layout)
        self.setLayout(main_layout)

    def update(self):
        """更新前提列表"""
        self.item_list.clear()
        add_now_talk_weight, final_weight = 0, 1
        fixed_weight = 0
        if cache_control.now_edit_type_flag == 0:
            for premise in cache_control.now_talk_data[cache_control.now_select_id].premise:
                # 如果是CVP前提，读取CVP前提的内容
                if "CVP" in premise and premise not in cache_control.premise_data:
                    cvp_str = function.read_CVP(premise)
                    cache_control.premise_data[premise] = cvp_str
                # 如果是固定权重前提，读取固定权重
                if "CVP" in premise and "Weight" in premise:
                    fixed_weight = int(premise.split("_")[-1])
                # 计算权重并更新到info_label的文本中
                if premise[:5] == "high_":
                    add_weignt = int(premise[5:])
                    add_now_talk_weight += add_weignt
                item = QListWidgetItem(cache_control.premise_data[premise])
                item.setToolTip(item.text())
                self.item_list.addItem(item)
        elif cache_control.now_edit_type_flag == 1:
            for premise in cache_control.now_event_data[cache_control.now_select_id].premise:
                if "CVP" in premise and premise not in cache_control.premise_data:
                    cvp_str = function.read_CVP(premise)
                    cache_control.premise_data[premise] = cvp_str
                if premise[:5] == "high_":
                    add_weignt = int(premise[5:])
                    add_now_talk_weight += add_weignt
                item = QListWidgetItem(cache_control.premise_data[premise])
                item.setToolTip(item.text())
                self.item_list.addItem(item)
        draw_text = f"○双击替换，右键展开删除、复制、粘贴菜单\n○指令(一段结算)需要区分触发者自己和交互对象\n○二段结算仅触发者自己，没有交互对象\n○当前该文本的出现权重="
        # 如果有固定权重，则显示固定权重
        if fixed_weight != 0:
            draw_text += f"固定值{fixed_weight}"
        else:
            draw_text += "1"
            if add_now_talk_weight:
                draw_text += f" + {add_now_talk_weight}"
                final_weight += add_now_talk_weight
            # 是NPC的专属口上时，权重翻三倍
            if cache_control.now_adv_id != 0 and cache_control.now_adv_id != "0":
                draw_text += f"，角色口上再乘3"
                final_weight = final_weight * 3
            if final_weight != 1:
                draw_text += f"，最终权重：{final_weight}"
        self.info_label.setText(draw_text)

    def CVP(self):
        """展开CVP菜单"""
        if cache_control.now_select_id != "":
            menu = CVPMenu()
            menu.exec()

    def change(self):
        """展开前提菜单"""
        if cache_control.now_select_id != "":
            menu = PremiseMenu()
            menu.exec()

    def change_this_item(self, item):
        """删除该前提并展开前提菜单"""
        # 先遍历找到cid
        for premise in cache_control.premise_data:
            if cache_control.premise_data[premise] == item.text():
                premise_cid = premise
                break
        # 根据cid删除前提
        if cache_control.now_edit_type_flag == 1:
            if premise_cid in cache_control.now_event_data[cache_control.now_select_id].premise:
                del cache_control.now_event_data[cache_control.now_select_id].premise[premise_cid]
        elif cache_control.now_edit_type_flag == 0:
            if premise_cid in cache_control.now_talk_data[cache_control.now_select_id].premise:
                del cache_control.now_talk_data[cache_control.now_select_id].premise[premise_cid]
        # 展开前提菜单
        self.change()

    def reset(self):
        """清零前提列表"""
        if cache_control.now_select_id != "":
            if cache_control.now_edit_type_flag == 1:
                cache_control.now_event_data[cache_control.now_select_id].premise = {}
            elif cache_control.now_edit_type_flag == 0:
                cache_control.now_talk_data[cache_control.now_select_id].premise = {}
            self.item_list.clear()

    def show_context_menu(self, pos):
        """右键菜单"""
        item = self.item_list.itemAt(pos)
        if item is not None:
            # 先遍历找到cid
            for premise in cache_control.premise_data:
                if cache_control.premise_data[premise] == item.text():
                    premise_cid = premise
                    break
            # 获取data对象
            if cache_control.now_edit_type_flag == 1:
                data = cache_control.now_event_data[cache_control.now_select_id]
            elif cache_control.now_edit_type_flag == 0:
                data = cache_control.now_talk_data[cache_control.now_select_id]
            # 创建右键菜单
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            copy_action = menu.addAction("复制")  # 添加“复制”按钮，将复制当前项的文本
            paste_action = menu.addAction("粘贴")  # 添加“粘贴”按钮，用于将复制的文本粘贴到列表中
            # 显示菜单，等待用户选择操作
            action = menu.exec_(self.item_list.mapToGlobal(pos))
            # 删除
            if action == delete_action:
                self.item_list.takeItem(self.item_list.row(item))
                # 根据cid删除前提
                if premise_cid in data.premise:
                    del data.premise[premise_cid]
            # 复制
            elif action == copy_action:
                # 复制当前项文本，复制后的内容存入 cache_control.now_copied_premise
                cache_control.now_copied_premise = premise_cid
            # 粘贴
            elif action == paste_action:
                premise_cid = cache_control.now_copied_premise
                # 检查全局复制变量是否有内容，如果有则判断列表中不存在该前提，再创建一个新的列表项并显示
                if premise_cid != "":
                    # 遍历前提组数据，判断是否存在该前提组，如果存在则将该前提添加到该组中
                    if premise_cid in cache_control.premise_group_data:
                        for now_cid in cache_control.premise_group_data[premise_cid]:
                            data.premise[now_cid] = 1
                    # 如果不存在该前提组，则将该前提添加到当前的前提列表中
                    else:
                        data.premise[premise_cid] = 1
                    # 在列表中添加新的项
                    self.item_list.addItem(cache_control.premise_data[cache_control.now_copied_premise])

    def add_group(self):
        """将当前的所有前提设为新前提组"""
        # 获得新的前提组cid
        new_cid_int = 1
        new_cid = f"g_{new_cid_int}"
        while new_cid in cache_control.premise_group_data:
            new_cid_int += 1
            new_cid = f"g_{new_cid_int}"
        # 获得当前所有前提
        premise_list = []
        if cache_control.now_edit_type_flag == 1:
            premise_list = list(cache_control.now_event_data[cache_control.now_select_id].premise.keys())
        elif cache_control.now_edit_type_flag == 0:
            premise_list = list(cache_control.now_talk_data[cache_control.now_select_id].premise.keys())
        premise_list.sort()
        # 添加前提组
        cache_control.premise_group_data[new_cid] = premise_list
        # 保存前提组到文件
        with open("PremiseGroup.csv", "a", encoding="utf-8") as now_file:
            now_file.write(f"{new_cid},{'&'.join(premise_list)}\n")
        # 更新前提列表
        self.update()

