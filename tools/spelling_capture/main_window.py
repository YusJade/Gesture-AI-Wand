from PyQt6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QPushButton, QComboBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from dataset_logic import DatasetLogic
from file_window import FileWindow
from line_chart_window import LineChartWindow


class MainWindow(QMainWindow):
    
    run_logic_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_open_serial = False
        self.worker_thread = QThread()
        self.dataset_logic = DatasetLogic()
        self.file_window = FileWindow()
        # self.serial_window = SerialWindow()
        self.line_chart_window = LineChartWindow()        
        self.file_window.file_selected_signal.connect(self.line_chart_window.slot_read_file_and_plot)
        
        self.setup_ui()
        
    
    def slot_open_serial_btn_clicked(self):
        if self.is_open_serial:
            self.is_open_serial = False
            self.open_btn.setText("打开串口")
            return
        try:
            port_index = self.port_combo.currentIndex()
            baudrate = int(self.baudrate_combo.currentText())
            
            from dataset_logic import DatasetLogic 
            
            self.dataset_logic = DatasetLogic(gesture=str(self.gesute_textedit.text()))
            self.dataset_logic.prepare_directory()
            self.file_window.set_directory(self.dataset_logic.get_dataset_dir())
            self.dataset_logic.open_serial(port_index, int(self.baudrate_combo.currentText()))
            self.dataset_logic.moveToThread(self.worker_thread)
            self.dataset_logic.get_serial_signal.connect(lambda _: self.dataset_logic.update_gesture(self.gesute_textedit.text()))
            
            self.run_logic_signal.connect(self.dataset_logic.start_collection)
            self.worker_thread.start()
            self.run_logic_signal.emit()
            
            # self.dataset_logic.get_serial_signal.connect(self.serial_window.write_data)
            self.dataset_logic.directory_changed.connect(self.file_window.slot_refresh_directory)
            self.is_open_serial = True
            self.open_btn.setText("关闭串口")
        except Exception as e:
            self.open_btn.setText("打开串口")
            QMessageBox.warning(self, '错误', f'错误: {e}')
    
    def setup_ui(self):
        self.setWindowTitle('赛博魔杖-数据集采集工具     by YusJade.')
        self.setGeometry(100, 100, 1000, 600)
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        control_layout = QVBoxLayout()
        
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        
        # 串口控制按钮
        self.open_btn = QPushButton("打开串口")
        # 波特率配置
        baudrate_label = QLabel("设置波特率")
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baudrate_combo.setCurrentText('115200')
        # 串口选择下拉框
        from PyQt6.QtSerialPort import QSerialPortInfo
        self.port_combo = QComboBox()
        ports = [f'{port.portName()} {port.description()}' for port in QSerialPortInfo.availablePorts()]
        self.port_combo.addItems(ports)
        # 手势选择
        self.gesute_label = QLabel("录制手势")
        self.gesute_textedit = QLineEdit()
        self.gesute_textedit.setText("unknown")
        
        control_layout = QHBoxLayout()
        control_layout.addWidget(baudrate_label)
        control_layout.addWidget(self.baudrate_combo)
        control_layout.addWidget(self.port_combo)
        control_layout.addWidget(self.open_btn)
        control_layout.addWidget(self.gesute_label)
        control_layout.addWidget(self.gesute_textedit)
        control_layout.addStretch()      
        
        # 连接信号槽
        self.open_btn.clicked.connect(self.slot_open_serial_btn_clicked)

        # control_group.setLayout(control_layout)
        left_layout.addLayout(control_layout)
        serial_display_layout = QHBoxLayout()
        # serial_display_layout.addWidget(self.serial_window)
        left_layout.addLayout(serial_display_layout)
        
        imu_preview_layout = QHBoxLayout()
        imu_preview_layout.addWidget(self.line_chart_window)
        left_layout.addLayout(imu_preview_layout)
        
        right_layout.addWidget(self.file_window)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
        
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())