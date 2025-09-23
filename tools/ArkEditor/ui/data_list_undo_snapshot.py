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
        self.snapshot_stack = []  # 存放“修改前”状态
        self.redo_stack = []      # 存放“撤销前(修改后)”状态，用于 Ctrl+Y 重做
        self.max_depth = 100      # 默认最大深度
        self._listeners = []      # 状态监听回调列表

    def _make_snapshot(self):
        """生成当前全量数据快照（内部使用）。"""
        import copy
        return {
            'now_talk_data': copy.deepcopy(cache_control.now_talk_data),
            'now_event_data': copy.deepcopy(cache_control.now_event_data),
            'now_select_id': copy.deepcopy(cache_control.now_select_id),
            'now_edit_type_flag': copy.deepcopy(cache_control.now_edit_type_flag),
        }

    def save_snapshot(self):
        """
        保存当前所有条目的快照
        输入：无
        输出：无
        功能：将当前数据的深拷贝压入撤销栈
        """
        snapshot = self._make_snapshot()
        self.snapshot_stack.append(snapshot)
        # 超出最大深度，丢弃最早的
        if len(self.snapshot_stack) > self.max_depth:
            self.snapshot_stack.pop(0)
        # 新的分支产生，清空 redo 栈
        self.redo_stack.clear()
        self._notify()
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
        # 当前是“修改后”状态，需保存到 redo 栈以支持重做
        current_snapshot = self._make_snapshot()
        self.redo_stack.append(current_snapshot)
        # 取出上一个“修改前”状态
        snapshot = self.snapshot_stack.pop()
        cache_control.now_talk_data = snapshot['now_talk_data']
        cache_control.now_event_data = snapshot['now_event_data']
        cache_control.now_select_id = snapshot['now_select_id']
        cache_control.now_edit_type_flag = snapshot['now_edit_type_flag']
        self._notify()
        # print("撤销成功")
        return True

    def redo(self):
        """
        重做到被撤销前的状态（Ctrl+Y）
        输入：无
        输出：bool，是否成功重做
        功能：弹出 redo 栈顶快照并恢复，同时将当前状态压回撤销栈，形成可再次撤销的链。
        """
        if not self.redo_stack:
            print("没有可重做的快照")
            return False
        # 将当前（撤销后的）状态压入撤销栈，保持对称
        self.snapshot_stack.append(self._make_snapshot())
        redo_snapshot = self.redo_stack.pop()
        cache_control.now_talk_data = redo_snapshot['now_talk_data']
        cache_control.now_event_data = redo_snapshot['now_event_data']
        cache_control.now_select_id = redo_snapshot['now_select_id']
        cache_control.now_edit_type_flag = redo_snapshot['now_edit_type_flag']
        self._notify()
        # print("重做成功")
        return True

    # ---------------- 新增：监听与包装 ---------------
    def add_listener(self, callback):
        """添加一个监听器，在撤销/重做/保存快照后调用。"""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self):
        for cb in list(self._listeners):
            try:
                cb(len(self.snapshot_stack), len(self.redo_stack))
            except Exception:
                pass

    def undoable(self, func=None, *, auto_snapshot=True):
        """
        装饰器/包装器：在执行修改逻辑前自动保存快照，并可清理 redo。
        使用：@undo_snapshot_manager.undoable
        或：wrapped = undo_snapshot_manager.undoable(fn)
        """
        def decorator(inner_func):
            def wrapper(*args, **kwargs):
                if auto_snapshot:
                    self.save_snapshot()
                return inner_func(*args, **kwargs)
            return wrapper
        if func is not None:
            return decorator(func)
        return decorator

# 单例
undo_snapshot_manager = UndoSnapshotManager()
