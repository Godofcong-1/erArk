from PySide6.QtWidgets import QListWidgetItem, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import cache_control
import function
from ui.premise_menu import PremiseMenu, CVPMenu
import os
import csv

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class ItemPremiseList(QWidget):
    """前提表单主体"""

    QUICK_INSERT_FILE = "快速插入前提.csv"

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
        change_button.setObjectName("btn_change_all")
        change_button.clicked.connect(self.change)
        button_layout1.addWidget(change_button)
        reset_button = QPushButton("整体清零")
        reset_button.setObjectName("btn_reset_all")
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

        # 插入/移除四个常用前提的按钮行
        button_layout3 = QHBoxLayout()
        # 插入玩家触发前提按钮
        self.btn_sys0 = QPushButton("玩家触发的该指令")
        self.btn_sys0.clicked.connect(lambda: self.toggle_premise('sys_0'))
        button_layout3.addWidget(self.btn_sys0)
        # 插入NPC触发前提按钮
        self.btn_sys1 = QPushButton("NPC触发的该指令")
        self.btn_sys1.clicked.connect(lambda: self.toggle_premise('sys_1'))
        button_layout3.addWidget(self.btn_sys1)
        # 插入交互对象为玩家前提按钮
        self.btn_sys4 = QPushButton("交互对象是玩家角色")
        self.btn_sys4.clicked.connect(lambda: self.toggle_premise('sys_4'))
        button_layout3.addWidget(self.btn_sys4)
        # 插入交互对象为NPC前提按钮
        self.btn_sys5 = QPushButton("交互对象不是玩家")
        self.btn_sys5.clicked.connect(lambda: self.toggle_premise('sys_5'))
        button_layout3.addWidget(self.btn_sys5)
        # 将新按钮行加入标题布局
        title_layout.addLayout(button_layout3)

        # 快速插入按钮区（多行，每行最多4个按钮）
        self.quick_insert_button_layouts = []  # 存储所有快速插入按钮行
        self.quick_insert_button_area = QVBoxLayout()
        title_layout.addLayout(self.quick_insert_button_area)
        self.refresh_quick_insert_buttons()  # 初始化时刷新

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
        # 启用拖拽移动功能
        self.item_list.setDragDropMode(QListWidget.InternalMove)
        self.item_list.setDefaultDropAction(Qt.MoveAction)
        self.item_list.setSelectionMode(QListWidget.SingleSelection)
        self.item_list.model().rowsMoved.connect(self.on_rows_moved)

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
            # 是NPC的专属口上时，权重翻10倍
            if cache_control.now_adv_id != 0 and cache_control.now_adv_id != "0":
                draw_text += f"，角色口上再乘10"
                final_weight = final_weight * 10
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
            # 自定义快速插入菜单项
            if self.is_in_quick_insert(premise_cid):
                quick_action = menu.addAction("从快速插入列表中删除")
            else:
                quick_action = menu.addAction("加入到快速插入列表")
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
                    # 遍历前提组数据，判断是否存在该前提组，如果存在则将该前提添加到该前提组中
                    if premise_cid in cache_control.premise_group_data:
                        for now_cid in cache_control.premise_group_data[premise_cid]:
                            data.premise[now_cid] = 1
                    # 如果不存在该前提组，则将该前提添加到当前的前提列表中
                    else:
                        data.premise[premise_cid] = 1
                    # 在列表中添加新的项
                    self.item_list.addItem(cache_control.premise_data[cache_control.now_copied_premise])
            # 快速插入菜单逻辑
            elif action == quick_action:
                if self.is_in_quick_insert(premise_cid):
                    self.remove_from_quick_insert(premise_cid)
                else:
                    self.add_to_quick_insert(premise_cid)
                # 快速插入按钮区需要刷新
                self.refresh_quick_insert_buttons()

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

    def on_rows_moved(self, parent, start, end, dest, row):
        """
        拖拽移动前提条目后，更新数据顺序
        """
        if cache_control.now_select_id != "":
            if cache_control.now_edit_type_flag == 0:
                # 口上
                data = cache_control.now_talk_data[cache_control.now_select_id]
            elif cache_control.now_edit_type_flag == 1:
                # 事件
                data = cache_control.now_event_data[cache_control.now_select_id]
            # 重新按界面顺序排列premise
            new_order = []
            for i in range(self.item_list.count()):
                text = self.item_list.item(i).text()
                # 通过文本反查cid
                for cid, val in cache_control.premise_data.items():
                    if val == text and cid in data.premise:
                        new_order.append(cid)
                        break
            # 重新构建premise字典
            new_premise = {cid: data.premise[cid] for cid in new_order}
            data.premise = new_premise

    def toggle_premise(self, premise_cid: str):
        """
        切换指定前提（sys_0、sys_1、sys_4、sys_5 及快速插入）
        参数：
            premise_cid (str): 要切换的前提ID
        返回值：
            None
        功能：
            如果当前条目已有该前提，则移除；否则添加。操作后刷新前提列表。
        """
        # 判断当前是否有选中条目
        if cache_control.now_select_id == "":
            return
        # 根据编辑类型获取当前数据对象
        if cache_control.now_edit_type_flag == 1:
            data = cache_control.now_event_data[cache_control.now_select_id]
        elif cache_control.now_edit_type_flag == 0:
            data = cache_control.now_talk_data[cache_control.now_select_id]
        else:
            return
        # 若为前提组，需特殊处理（此处只处理单前提）
        # 切换前提：有则删，无则加
        if premise_cid in data.premise:
            del data.premise[premise_cid]
        else:
            data.premise[premise_cid] = 1
        # 刷新前提列表
        self.update()
        # 若是快速插入按钮，刷新按钮区（防止文本变化）
        self.refresh_quick_insert_buttons()

    def read_quick_insert_list(self):
        """
        读取快速插入前提csv文件，返回前提cid列表。
        返回值：
            list[str]，快速插入前提cid列表
        """
        if not os.path.exists(self.QUICK_INSERT_FILE):
            return []
        result = []
        try:
            with open(self.QUICK_INSERT_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0]:
                        result.append(row[0])
        except Exception as e:
            print(f"读取快速插入前提csv失败: {e}")
        return result

    def add_to_quick_insert(self, cid: str):
        """
        将指定前提cid加入快速插入csv文件。
        参数：
            cid (str): 前提cid
        返回值：None
        """
        quick_list = self.read_quick_insert_list()
        if cid in quick_list:
            return
        try:
            with open(self.QUICK_INSERT_FILE, "a", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([cid])
        except Exception as e:
            print(f"写入快速插入前提csv失败: {e}")

    def remove_from_quick_insert(self, cid: str):
        """
        从快速插入csv文件中移除指定前提cid。
        参数：
            cid (str): 前提cid
        返回值：None
        """
        quick_list = self.read_quick_insert_list()
        if cid not in quick_list:
            return
        quick_list.remove(cid)
        try:
            with open(self.QUICK_INSERT_FILE, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                for c in quick_list:
                    writer.writerow([c])
        except Exception as e:
            print(f"移除快速插入前提csv失败: {e}")

    def is_in_quick_insert(self, cid: str) -> bool:
        """
        判断指定cid是否在快速插入csv中。
        参数：
            cid (str): 前提cid
        返回值：bool
        """
        return cid in self.read_quick_insert_list()

    def refresh_quick_insert_buttons(self):
        """
        刷新快速插入按钮区，根据csv文件内容动态生成按钮。
        每行最多4个按钮，超出则换行。
        """
        # 清空原有按钮行
        for layout in self.quick_insert_button_layouts:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.quick_insert_button_layouts.clear()
        # 读取快速插入前提cid列表
        quick_list = self.read_quick_insert_list()
        # 按4个一组分行
        for i in range(0, len(quick_list), 4):
            row = quick_list[i:i+4]
            row_layout = QHBoxLayout()
            for cid in row:
                # 获取前提显示文本，如果未找到且为CVP前提则用read_CVP获取
                text = cache_control.premise_data.get(cid, cid)
                # 如果text等于cid且cid中包含CVP，尝试用read_CVP获取
                if text == cid and "CVP" in cid:
                    try:
                        import function  # 避免循环引用
                        text = function.read_CVP(cid)
                    except Exception as e:
                        text = cid  # 若解析失败则回退为cid
                btn = QPushButton(text)
                btn.setToolTip(cid)
                # 修正lambda闭包问题，使用functools.partial确保参数绑定
                import functools
                btn.clicked.connect(functools.partial(self.toggle_premise, cid))
                row_layout.addWidget(btn)
            self.quick_insert_button_area.addLayout(row_layout)
            self.quick_insert_button_layouts.append(row_layout)

