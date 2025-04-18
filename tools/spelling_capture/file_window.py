from turtle import mode
from PyQt6.QtWidgets import QWidget, QTreeView, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir, pyqtSignal


class FileWindow(QWidget):
    file_selected_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.tree_view = QTreeView()
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setAlternatingRowColors(True)

        layout = QVBoxLayout()
        dir_layout = QHBoxLayout()
        selected_button = QPushButton("选择目录")
        self.selected_label = QLabel("当前目录: ")
        dir_layout.addWidget(self.selected_label)
        dir_layout.addWidget(selected_button)
        selected_button.clicked.connect(self.slot_open_directory)
        
        layout.addLayout(dir_layout)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

    def slot_open_directory(self):
        file_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if file_path:
            self.set_directory(file_path)

    def slot_refresh_directory(self, path):
        self.set_directory(path)

    def set_directory(self, path):
        model = QFileSystemModel()
        model.setRootPath(QDir(path).absolutePath())
        print(QDir(path).absolutePath())
        self.tree_view.setModel(model)
        # 设置 QTreeView 的根索引
        root_index = model.index(QDir(path).absolutePath())
        self.tree_view.setRootIndex(root_index)
        self.tree_view.doubleClicked.connect(self.on_double_click)

    def on_double_click(self, index):
        model = self.tree_view.model()
        file_path = model.filePath(index)
        self.file_selected_signal.emit(file_path)
        
    
