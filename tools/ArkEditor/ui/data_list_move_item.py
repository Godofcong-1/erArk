"""
move_item_utils.py
用于处理DataList中条目移动相关的功能。
"""
from PySide6.QtGui import QColor
import cache_control
from collections import OrderedDict
from .data_list_undo_snapshot import undo_snapshot_manager  # 导入快照式撤销管理器

# 以下函数为条目移动相关的功能，供DataList调用

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
        # 只调整受影响区间的cid，区间内编号递增
        affected_start = min(move_idx, target_idx)
        affected_end = max(move_idx, target_idx)
        # 获取区间内原编号的最小值
        min_cid = min(int(items[i][0]) for i in range(affected_start, affected_end+1))
        for offset, idx in enumerate(range(affected_start, affected_end+1)):
            new_cid = str(min_cid + offset)
            items[idx][1].cid = new_cid
            items[idx] = (new_cid, items[idx][1])
        # 其它区间编号不变
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
        # 只调整受影响区间的cid，区间内编号递增
        affected_start = min(move_idx, target_idx)
        affected_end = max(move_idx, target_idx)
        min_cid = min(int(items[i][0]) for i in range(affected_start, affected_end+1))
        for offset, idx in enumerate(range(affected_start, affected_end+1)):
            new_cid = str(min_cid + offset)
            items[idx][1].cid = new_cid
            items[idx] = (new_cid, items[idx][1])
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
        new_order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            new_order.append(item.uid)
        new_data = {uid: cache_control.now_talk_data[uid] for uid in new_order}
        cache_control.now_talk_data = new_data
    elif cache_control.now_edit_type_flag == 1:
        # 事件模式
        new_order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            new_order.append(item.uid)
        new_data = {uid: cache_control.now_event_data[uid] for uid in new_order}
        cache_control.now_event_data = new_data
    # 刷新界面
    self.update()
