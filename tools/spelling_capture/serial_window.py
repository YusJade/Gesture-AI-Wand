from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout
from loguru import logger

class SerialWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def append_data(self, data):
        self.text_edit.append(data)
        
    def clear_data(self):
        self.text_edit.clear()
        
    def write_data(self, data):
        self.text_edit.insertPlainText(data)
        