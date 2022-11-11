from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QMainWindow, QWidget


class Window(QMainWindow):
    """编辑器主窗体"""

    def __init__(self):
        """初始化编辑器主窗体"""
        super(Window, self).__init__()
        self.setWindowTitle("Dieloli事件编辑器")
        self.showFullScreen()
        self.main_layout: QHBoxLayout = QHBoxLayout()
        self.tool_layout: QVBoxLayout = QVBoxLayout()

    def add_main_widget(self, widget: QWidget, stretch: int):
        """
        添加小部件到布局中
        Keyword arguments:
        widget -- 小部件
        stretch -- 空间占比
        """
        self.main_layout.addWidget(widget, stretch)

    def add_tool_widget(self, widget: QWidget):
        """
        添加工具部件
        Keyword arguments:
        widget -- 小部件
        """
        self.tool_layout.addWidget(widget)

    def completed_layout(self):
        """布局完成"""
        widget = QWidget()
        layout = QVBoxLayout()
        tool_widget = QWidget()
        tool_widget.setLayout(self.tool_layout)
        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        layout.addWidget(tool_widget)
        layout.addWidget(main_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
