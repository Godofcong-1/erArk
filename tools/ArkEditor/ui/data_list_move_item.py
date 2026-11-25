"""
move_item_utils.py
用于处理DataList中条目移动相关的功能。
"""
from PySide6.QtGui import QColor
import cache_control
from collections import OrderedDict
from .data_list_undo_snapshot import undo_snapshot_manager  # 导入快照式撤销管理器

# 以下函数为条目移动相关的功能，供DataList调用

def renumber_talk_range(items, start, end):
    """
    把受影响区间内的口上编号按新顺序重新分配
    输入参数：items（list[tuple[str, Talk]]，移动后的口上顺序，原地修改），start（int，区间起点下标），end（int，区间终点下标，含）
    返回值：无
    功能描述：把区间内原有的编号从小到大依次分给移动后的各条目，区间内编号递增。
    只在区间原有的编号之间重新分配、不生成新编号：编号不连续时（例如新增条目取到的大编号被移到中间），
    若从区间最小编号起逐个加一，会生成区间外已有的编号，重建字典时同号的后一条覆盖前一条，前一条就从数据里消失了。
    """
    cid_list = sorted((items[i][0] for i in range(start, end + 1)), key=int)
    for idx, new_cid in zip(range(start, end + 1), cid_list):
        talk = items[idx][1]
        talk.cid = new_cid
        items[idx] = (new_cid, talk)


def merge_visible_order(data, list_widget):
    """
    把列表控件里拖拽后的条目顺序合回完整数据
    输入参数：data（dict，当前全部条目，键为 uid），list_widget（QListWidget，拖拽后的列表）
    返回值：dict，按新顺序排列的全部条目
    功能描述：开着筛选或搜索时列表只显示部分条目，只重排显示出来的条目所占的那些位置，没显示的条目留在原位，不会因为没显示就从数据里丢掉。
    """
    visible_uid_list = [list_widget.item(i).uid for i in range(list_widget.count())]
    visible_uid_set = set(visible_uid_list)
    visible_uid_iter = iter(visible_uid_list)
    # 原顺序里显示出来的位置依次换成拖拽后的显示顺序，其余位置不动
    new_order = [next(visible_uid_iter) if uid in visible_uid_set else uid for uid in data]
    return {uid: data[uid] for uid in new_order}


def move_item(self):
    """
    移动条目
    输入参数：self（DataList实例）
    返回值：无
    功能描述：重置所有筛选，设置移动标志，准备移动条目。
    """
    # 移动前保存快照
    undo_snapshot_manager.save_snapshot()
    # 重置所有筛选
    self.select_now_instruct_flag = 0
    self.text_search_reset()
    self.premise_search_reset()
    self.update()
    # 设置移动标志
    self.now_in_moving_flag = True
    self.edited_item = self.list_widget.currentItem()
    if self.edited_item is not None:
        self.edited_item.setBackground(QColor("light green"))
    # 记录移动前顺序到撤销栈
    if cache_control.now_edit_type_flag == 0:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'talk_move', 'order': order})
    elif cache_control.now_edit_type_flag == 1:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'event_move', 'order': order})

def move_to_up(self):
    """
    移至选中条目上方
    输入参数：self（DataList实例）
    返回值：无
    功能描述：将被编辑的条目移动到当前选中条目的上方，并重新编号受影响区间。
    """
    if self.edited_item is None:
        return
    current_select_cid = self.list_widget.currentItem().uid
    need_move_cid = self.edited_item.uid
    if current_select_cid == need_move_cid:
        return
    current_row = self.list_widget.currentRow()
    if current_row == -1:
        return
    if cache_control.now_edit_type_flag == 0:
        # 口上模式，精确控制顺序和编号，仅调整受影响区间
        items = list(cache_control.now_talk_data.items())
        move_idx = next((i for i, (cid, _) in enumerate(items) if cid == need_move_cid), None)
        target_idx = next((i for i, (cid, _) in enumerate(items) if cid == current_select_cid), None)
        if move_idx is None or target_idx is None:
            return
        item = items.pop(move_idx)
        # 如果移动后索引大于原索引，需要-1
        if target_idx > move_idx:
            target_idx -= 1
        items.insert(target_idx, item)
        # 只调整受影响区间的cid，区间内编号递增，其它区间编号不变
        renumber_talk_range(items, min(move_idx, target_idx), max(move_idx, target_idx))
        new_data = OrderedDict((cid, talk) for cid, talk in items)
        cache_control.now_talk_data = new_data
        cache_control.now_select_id = items[target_idx][0]
        self.now_in_moving_flag = False
    elif cache_control.now_edit_type_flag == 1:
        # 事件模式
        need_move_uid = self.edited_item.uid
        current_select_item = self.list_widget.currentItem()
        if not current_select_item:
            return
        current_select_uid = current_select_item.uid
        new_event_data = {}
        for uid in cache_control.now_event_data:
            if uid == need_move_uid:
                continue
            if uid == current_select_uid:
                new_event_data[need_move_uid] = cache_control.now_event_data[need_move_uid]
            new_event_data[uid] = cache_control.now_event_data[uid]
        cache_control.now_event_data = new_event_data
        self.now_in_moving_flag = False
    # 记录移动前顺序到撤销栈
    if cache_control.now_edit_type_flag == 0:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'talk_move', 'order': order})
    elif cache_control.now_edit_type_flag == 1:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'event_move', 'order': order})
    self.update()

def move_to_down(self):
    """
    移至选中条目下方
    输入参数：self（DataList实例）
    返回值：无
    功能描述：将被编辑的条目移动到当前选中条目的下方，并重新编号受影响区间。
    """
    if self.edited_item is None:
        return
    current_select_cid = self.list_widget.currentItem().uid
    need_move_cid = self.edited_item.uid
    if current_select_cid == need_move_cid:
        return
    current_row = self.list_widget.currentRow()
    if current_row == -1:
        return
    if cache_control.now_edit_type_flag == 0:
        # 口上模式，精确控制顺序和编号，仅调整受影响区间
        items = list(cache_control.now_talk_data.items())
        move_idx = next((i for i, (cid, _) in enumerate(items) if cid == need_move_cid), None)
        target_idx = next((i for i, (cid, _) in enumerate(items) if cid == current_select_cid), None)
        if move_idx is None or target_idx is None:
            return
        item = items.pop(move_idx)
        # 下方插入，目标索引+1（如果移动后索引大于原索引则不变）
        if target_idx < move_idx:
            target_idx += 1
        items.insert(target_idx, item)
        # 只调整受影响区间的cid，区间内编号递增，其它区间编号不变
        renumber_talk_range(items, min(move_idx, target_idx), max(move_idx, target_idx))
        new_data = OrderedDict((cid, talk) for cid, talk in items)
        cache_control.now_talk_data = new_data
        cache_control.now_select_id = items[target_idx][0]
        self.now_in_moving_flag = False
    elif cache_control.now_edit_type_flag == 1:
        # 事件模式
        need_move_uid = need_move_cid
        current_select_uid = current_select_cid
        new_event_data = {}
        skip_flag = False
        for uid in cache_control.now_event_data:
            if uid == need_move_uid:
                continue
            new_event_data[uid] = cache_control.now_event_data[uid]
            if uid == current_select_uid and not skip_flag:
                new_event_data[need_move_uid] = cache_control.now_event_data[need_move_uid]
                skip_flag = True
        cache_control.now_event_data = new_event_data
        self.now_in_moving_flag = False
    # 记录移动前顺序到撤销栈
    if cache_control.now_edit_type_flag == 0:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'talk_move', 'order': order})
    elif cache_control.now_edit_type_flag == 1:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'event_move', 'order': order})
    self.update()

def move_cancel(self):
    """
    取消移动
    输入参数：self（DataList实例）
    返回值：无
    功能描述：取消条目移动，恢复背景色。
    """
    self.now_in_moving_flag = False
    self.edited_item.setBackground(QColor("white"))

def refresh_item_flags(self):
    """
    为所有条目设置可拖拽和可放置标志
    输入参数：self（DataList实例）
    返回值：无
    功能描述：遍历所有条目，设置拖拽、放置、选择、启用标志。
    """
    from PySide6.QtCore import Qt
    for i in range(self.list_widget.count()):
        item = self.list_widget.item(i)
        item.setFlags(item.flags() | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

def on_rows_moved(self, parent, start, end, dest, row):
    """
    拖拽后重建数据顺序
    输入参数：self（DataList实例），parent, start, end, dest, row（拖拽信号参数）
    返回值：无
    功能描述：根据拖拽后界面顺序，重建数据字典顺序。
    """
    # 记录拖拽前顺序到撤销栈
    if cache_control.now_edit_type_flag == 0:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'talk_move', 'order': order})
    elif cache_control.now_edit_type_flag == 1:
        order = [item.uid for item in [self.list_widget.item(i) for i in range(self.list_widget.count())]]
        self.undo_stack.append({'type': 'event_move', 'order': order})
    if cache_control.now_edit_type_flag == 0:
        # 口上模式
        cache_control.now_talk_data = merge_visible_order(cache_control.now_talk_data, self.list_widget)
    elif cache_control.now_edit_type_flag == 1:
        # 事件模式
        cache_control.now_event_data = merge_visible_order(cache_control.now_event_data, self.list_widget)
    # 刷新界面
    self.update()
