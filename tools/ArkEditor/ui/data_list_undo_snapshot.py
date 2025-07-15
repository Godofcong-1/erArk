"""
undo_snapshot.py
用于DataList的快照式撤销功能。
"""
import copy
import cache_control

class UndoSnapshotManager:
    """
    快照式撤销管理器
    用于保存和恢复所有条目的快照。
    """
    def __init__(self):
        # 撤销栈，每个元素为一个快照字典
        self.snapshot_stack = []

    def save_snapshot(self):
        """
        保存当前所有条目的快照
        输入：无
        输出：无
        功能：将当前数据的深拷贝压入撤销栈
        """
        snapshot = {
            'now_talk_data': copy.deepcopy(cache_control.now_talk_data),
            'now_event_data': copy.deepcopy(cache_control.now_event_data),
            'now_select_id': copy.deepcopy(cache_control.now_select_id),
            'now_edit_type_flag': copy.deepcopy(cache_control.now_edit_type_flag),
        }
        self.snapshot_stack.append(snapshot)
        # print("快照已保存，当前撤销栈大小:", len(self.snapshot_stack))

    def undo(self):
        """
        撤销到上一个快照
        输入：无
        输出：bool，是否成功撤销
        功能：弹出撤销栈顶快照并恢复
        """
        if not self.snapshot_stack:
            print("没有可撤销的快照")
            return False
        snapshot = self.snapshot_stack.pop()
        cache_control.now_talk_data = snapshot['now_talk_data']
        cache_control.now_event_data = snapshot['now_event_data']
        cache_control.now_select_id = snapshot['now_select_id']
        cache_control.now_edit_type_flag = snapshot['now_edit_type_flag']
        # print("撤销成功")
        return True

# 单例
undo_snapshot_manager = UndoSnapshotManager()
