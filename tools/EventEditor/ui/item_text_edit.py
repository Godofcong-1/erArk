from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont
import cache_control


class ItemTextEdit(QWidget):
    """文本编辑框主体"""

    def __init__(self):
        """初始化文本编辑框主体"""
        super(ItemTextEdit, self).__init__()
        self.font = QFont()
        self.font.setPointSize(11)
        self.setFont(self.font)
        label_layout = QVBoxLayout()
        # 加入标题
        label = QLabel()
        label.setText("文本编辑")
        label_layout.addWidget(label)
        # 加入保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save)
        label_layout.addWidget(save_button)
        # 加入文本编辑框
        self.now_text = ""
        self.label_text = QTextEdit(self.now_text)
        label_layout.addWidget(self.label_text)
        self.setLayout(label_layout)

    def update(self):
        """更新文本内容"""
        self.now_text = cache_control.now_event_data[cache_control.now_event_id].text
        self.label_text.setText(self.now_text)
    
    def save(self):
        """保存文本内容"""
        cache_control.now_event_data[cache_control.now_event_id].text = self.label_text.toPlainText()
        