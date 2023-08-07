from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QTextEdit

app = QApplication([])
window = QWidget()

window_layout = QVBoxLayout()
window.setLayout(window_layout)

label1 = QWidget()
label2 = QWidget()
label3 = QWidget()
label4 = QWidget()

label1_text = QLabel("This is the text for label 1")
label2_text = QLabel("This is the text for label 2")
label3_text = QLabel("This is the text for label 3")
label4_text = QTextEdit("This is the text for label 4")


def add_grid_layout(label1: QWidget, label2: QWidget, label3: QWidget, label4: QWidget):
    layout = QGridLayout()
    layout.addWidget(label1, 0, 0, 2, 1)
    layout.addWidget(label2, 0, 1)
    layout.addWidget(label3, 0, 2)
    layout.addWidget(label4, 1, 1, 1, 2)
    window_layout.addLayout(layout)

label1_layout = QVBoxLayout()
label1_layout.addWidget(label1_text)
label1.setLayout(label1_layout)

label2_layout = QVBoxLayout()
label2_layout.addWidget(label2_text)
label2.setLayout(label2_layout)

label3_layout = QVBoxLayout()
label3_layout.addWidget(label3_text)
label3.setLayout(label3_layout)

label4_layout = QVBoxLayout()
label4_layout.addWidget(label4_text)
label4.setLayout(label4_layout)


add_grid_layout(label1, label2, label3, label4)

window.show()
app.exec()