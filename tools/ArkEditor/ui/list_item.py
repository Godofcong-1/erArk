from PySide6.QtWidgets import QListWidgetItem


class ListItem(QListWidgetItem):
    """表单对象"""

    def __init__(self, any):
        """初始化表单对象"""
        super(ListItem, self).__init__(any)
        self.uid = ""
        """ id """
