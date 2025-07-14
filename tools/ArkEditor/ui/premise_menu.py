from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QPushButton,
    QVBoxLayout,
    QLineEdit
)
from PySide6.QtGui import QFont, Qt
import cache_control
import function

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class TreeItem(QTreeWidgetItem):
    """树选框对象"""

    def __init__(self, any):
        """初始化树选框对象"""
        super(TreeItem, self).__init__(any)
        self.cid = ""
        """ 对象配表id """

class PremiseMenu(QDialog):
    """前提选择对象"""

    def __init__(self):
        """初始化前提复选框"""
        super(PremiseMenu, self).__init__()
        if cache_control.now_edit_type_flag == 1:
            self.setWindowTitle(cache_control.now_event_data[cache_control.now_select_id].text)
        elif cache_control.now_edit_type_flag == 0:
            self.setWindowTitle(cache_control.now_talk_data[cache_control.now_select_id].text)
        self.font = font
        self.layout: QVBoxLayout = QVBoxLayout()
        self.resize(1000,1000)
        # 增加一个搜索框，确定键，重置键，三个合在一起，放在最上面作为一个横向的搜索栏
        # 将搜索框改为 QLineEdit，便于回车直接触发搜索
        self.search_text = QLineEdit()
        self.search_text.setFont(self.font)
        self.search_text.setFixedHeight(32)
        self.search_text.setFixedWidth(200)
        self.search_text.returnPressed.connect(self.search)  # 回车直接触发搜索
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search)
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset)
        # 放在tree的上面，作为一个横向的搜索栏
        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(self.search_text)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.reset_button)
        self.layout.addLayout(self.search_layout)
        # 创建一个新的 QHBoxLayout，用于左右排列两个 tree
        self.tree_layout = QHBoxLayout()
        all_type_list = sorted(list(cache_control.premise_type_data.keys()))
        range_index = int(len(all_type_list) / 2) + 1
        range_a = all_type_list[:range_index]
        range_b = all_type_list[range_index :]
        range_list = [range_a, range_b]
        index = 1
        self.tree_list = []
        for type_list in range_list:
            tree = QTreeWidget()
            tree.setHeaderLabel("前提列表" + str(index))
            index += 1
            tree.setSelectionMode(QAbstractItemView.SingleSelection)
            tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            tree.setWordWrap(True)  # 设置 wordWrap 属性为 True
            tree.adjustSize()
            # 设置列的宽度为一个固定的值
            tree.setColumnWidth(0, 2000)

            root_list = []
            # 在index==2的时候，单独增加一个自定义前提群的type
            if index == 2:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, "自定义前提群")
                premise_group_list = list(cache_control.premise_group_data.keys())
                premise_group_list.sort()
                for premise_group in premise_group_list:
                    premise_group_node = TreeItem(now_root)
                    premise_group_node.cid = premise_group
                    # 根据前提群的cid，获取前提群的所有前提cid，然后把名字拼接成一个字符串
                    now_premise_group_list = cache_control.premise_group_data[premise_group]
                    now_premise_group_all_name = ""
                    for premise_cid in now_premise_group_list:
                        if "CVP" in premise_cid:
                            now_premise_group_all_name += function.read_CVP(premise_cid)
                        else:
                            now_premise_group_all_name += cache_control.premise_data[premise_cid]
                        if premise_cid != now_premise_group_list[-1]:
                            now_premise_group_all_name += "&"
                    premise_group_node.setText(0, now_premise_group_all_name)
                    premise_group_node.setToolTip(0,premise_group_node.text(0))
                    if cache_control.now_edit_type_flag == 1:
                        if premise_group in cache_control.now_event_data[cache_control.now_select_id].premise:
                            premise_group_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_group_node.setCheckState(0, Qt.Unchecked)
                    elif cache_control.now_edit_type_flag == 0:
                        if premise_group in cache_control.now_talk_data[cache_control.now_select_id].premise:
                            premise_group_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_group_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            # 正常的前提type
            for now_type in type_list:
                now_root = QTreeWidgetItem(tree)
                now_root.setText(0, now_type)
                premise_list = list(cache_control.premise_type_data[now_type])
                premise_list.sort()
                for premise in premise_list:
                    premise_node = TreeItem(now_root)
                    premise_node.cid = premise
                    premise_node.setText(0, cache_control.premise_data[premise])
                    premise_node.setToolTip(0,premise_node.text(0))
                    if cache_control.now_edit_type_flag == 1:
                        if premise in cache_control.now_event_data[cache_control.now_select_id].premise:
                            premise_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_node.setCheckState(0, Qt.Unchecked)
                    elif cache_control.now_edit_type_flag == 0:
                        if premise in cache_control.now_talk_data[cache_control.now_select_id].premise:
                            premise_node.setCheckState(0, Qt.Checked)
                        else:
                            premise_node.setCheckState(0, Qt.Unchecked)
                root_list.append(now_root)
            tree.addTopLevelItems(root_list)
            tree.itemClicked.connect(self.click_item)
            tree.setFont(self.font)
            self.tree_list.append(tree)
            self.tree_layout.addWidget(tree)  # 将 tree 添加到 QHBoxLayout 中
        self.layout.addLayout(self.tree_layout)
        self.setLayout(self.layout)

    def update_premise(self, item, data):
        """
        删除前提
        Keyword arguments:
        item -- 删除的对象
        data -- 当前事件数据
        """
        if item.cid in cache_control.premise_group_data:
            for premise_cid in cache_control.premise_group_data[item.cid]:
                if premise_cid in data.premise:
                    del data.premise[premise_cid]
        else:
            if item.cid in data.premise:
                del data.premise[item.cid]

    def add_premise(self, item, data):
        """
        添加前提
        Keyword arguments:
        item -- 添加的对象
        data -- 当前事件数据
        """
        if item.cid in cache_control.premise_group_data:
            for premise_cid in cache_control.premise_group_data[item.cid]:
                data.premise[premise_cid] = 1
        else:
            data.premise[item.cid] = 1

    def click_item(self, item: TreeItem, column: int):
        """
        点击选项时勾选选框并更新事件前提
        Keyword arguments:
        item -- 点击的对象
        column -- 点击位置
        """
        if "cid" not in item.__dict__:
            return

        if cache_control.now_edit_type_flag == 1:
            data = cache_control.now_event_data[cache_control.now_select_id]
        elif cache_control.now_edit_type_flag == 0:
            data = cache_control.now_talk_data[cache_control.now_select_id]

        if item.checkState(column) == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
            self.update_premise(item, data)
        else:
            item.setCheckState(0, Qt.Checked)
            self.add_premise(item, data)

        cache_control.item_premise_list.update()

    def search(self):
        """搜索前提"""
        search_text = self.search_text.text()  # QLineEdit 获取文本用 text()
        if not len(search_text):
            return
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                has_visible_child = False  # 标记该type下是否有可见子项
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    if search_text in child.text(0):
                        child.setHidden(False)
                        has_visible_child = True
                    else:
                        child.setHidden(True)
                # 如果没有任何子项可见，则隐藏该type（root）
                root.setHidden(not has_visible_child)

    def reset(self):
        """重置搜索"""
        self.search_text.setText("")  # QLineEdit 设置文本
        for tree in self.tree_list:
            for root_index in range(tree.topLevelItemCount()):
                root = tree.topLevelItem(root_index)
                root.setHidden(False)  # 重置时显示所有type
                for child_index in range(root.childCount()):
                    child = root.child(child_index)
                    child.setHidden(False)


    # def contextMenuEvent(self, event):
    #     """右键菜单"""
    #     menu = QMenu(self)
    #     delete_action = menu.addAction("删除")
    #     # 获取鼠标右键点击的项
    #     item = event.pos()
    #     # 将获取到的项传递给 delete_group 方法
    #     delete_action.triggered.connect(lambda: self.delete_group(item))
    #     menu.exec_(event.globalPos())

    def delete_group(self, item):
        """删除前提组"""
        # 找到前提群cid
        premise_group_cid = ""
        # print(f"debug premise_group_cid: {premise_group_cid}")
        # 根据cid在cache_control.premise_group_data中删掉该前提群
        if premise_group_cid in cache_control.premise_group_data:
            del cache_control.premise_group_data[premise_group_cid]
        # 在文件中删除该前提群
        # with open(cache_control.now_file_path, "r", encoding="utf-8") as now_file:
        #     now_read = now_file.readlines()
        # with open(cache_control.now_file_path, "w", encoding="utf-8") as now_file:
        #     for line in now_read:
        #         if premise_group_cid in line:
        #             continue
        #         now_file.write(line)
        # 更新前提列表
        self.update()
