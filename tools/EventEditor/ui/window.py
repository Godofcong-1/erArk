from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QMainWindow, QWidget, QGridLayout, QLabel


class Window(QMainWindow):
    """编辑器主窗体"""

    def __init__(self):
        """初始化编辑器主窗体"""
        super(Window, self).__init__()
        self.setWindowTitle("ErArk事件编辑器")
        self.main_layout: QGridLayout = QGridLayout()
        self.tool_layout: QVBoxLayout = QVBoxLayout()

    def add_grid_layout(self, label1: QWidget, label2: QWidget, label3: QWidget, label4: QWidget):
        """
        进行部件的布局，1：0行0列，占2行1列；2：0行1列；3：0行2列；4：1行1列，占1行2列
        Keyword arguments:
        widget -- 小部件
        """
        self.main_layout.addWidget(label1, 0, 0, 2, 1)
        self.main_layout.addWidget(label2, 0, 1)
        self.main_layout.addWidget(label3, 0, 2)
        self.main_layout.addWidget(label4, 1, 1, 1, 2)

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
        self.showMaximized()
