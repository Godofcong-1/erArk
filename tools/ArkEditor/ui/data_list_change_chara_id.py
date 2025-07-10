# 新增方法文件用于存放DataList的角色id修改相关方法
# 所有方法均带有详细中文注释

class DataListIdEditMixin:
    def change_current_chara_id(self):
        """
        修改当前选中条目的角色id
        输入：无（直接读取self.chara_id_text_edit的内容）
        输出：无
        功能：将当前选中条目的角色id修改为输入框中的新值
        """
        # 获取新角色id
        new_id = self.chara_id_text_edit.toPlainText()
        # 判断当前编辑类型
        if hasattr(self, 'list_widget') and self.list_widget.currentItem() is not None:
            if hasattr(self, 'cache_control'):
                cache_control = self.cache_control
            else:
                import cache_control
            if cache_control.now_edit_type_flag == 0:
                # 口上模式
                cid = self.list_widget.currentItem().uid
                if cid in cache_control.now_talk_data:
                    cache_control.now_talk_data[cid].adv_id = new_id
            elif cache_control.now_edit_type_flag == 1:
                # 事件模式
                uid = self.list_widget.currentItem().uid
                if uid in cache_control.now_event_data:
                    cache_control.now_event_data[uid].adv_id = new_id
        # 刷新界面
        self.update()

    def change_all_chara_id(self):
        """
        修改所有条目的角色id
        输入：无（直接读取self.chara_id_text_edit的内容）
        输出：无
        功能：将所有条目的角色id批量修改为输入框中的新值
        """
        # 获取新角色id
        new_id = self.chara_id_text_edit.toPlainText()
        if hasattr(self, 'cache_control'):
            cache_control = self.cache_control
        else:
            import cache_control
        if cache_control.now_edit_type_flag == 0:
            # 口上模式
            for talk in cache_control.now_talk_data.values():
                talk.adv_id = new_id
        elif cache_control.now_edit_type_flag == 1:
            # 事件模式
            for event in cache_control.now_event_data.values():
                event.adv_id = new_id
        # 刷新界面
        self.update()
