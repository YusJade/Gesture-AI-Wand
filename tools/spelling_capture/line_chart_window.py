from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColorConstants, QPainter, QColor
from PyQt6.QtWidgets import QCheckBox, QLabel, QGridLayout, QMessageBox
import os
import pandas as pd
import argparse

class LineChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.chart.setBackgroundBrush(QColorConstants.Black)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.axis_y.setRange(-2, 2)
        self.axis_x.setLabelsColor(QColorConstants.White)
        self.axis_y.setLabelsColor(QColorConstants.White)
        self.axis_x.setGridLineColor(QColorConstants.Gray)
        self.axis_y.setGridLineColor(QColorConstants.Gray)
        
        self.series_visibility = {
            'x_acc': True,
            'y_acc': True,
            'z_acc': True,
            'pitch': False,
            'roll': False,
            'yaw': False,
        }
        self.series_data = {
            'x_acc': list(),
            'y_acc': list(),
            'z_acc': list(),
            'pitch': list(),
            'roll': list(),
            'yaw': list(),
        }
        
        x_acc_checkbox = QCheckBox('x_acc')
        x_acc_checkbox.setChecked(True)
        y_acc_checkbox = QCheckBox('y_acc')
        y_acc_checkbox.setChecked(True)
        z_acc_checkbox = QCheckBox('z_acc')
        z_acc_checkbox.setChecked(True)
        pitch_checkbox = QCheckBox('pitch')
        pitch_checkbox.setChecked(False)
        roll_checkbox = QCheckBox('roll')
        roll_checkbox.setChecked(False)
        yaw_checkbox = QCheckBox('yaw')
        yaw_checkbox.setChecked(False)
        view_label = QLabel("绘制视图")
        
        x_acc_checkbox.stateChanged.connect(lambda state: self.slot_series_visibility_changed(state, 'x_acc'))
        y_acc_checkbox.stateChanged.connect(lambda state: self.slot_series_visibility_changed(state, 'y_acc'))
        z_acc_checkbox.stateChanged.connect(lambda state: self.slot_series_visibility_changed(state, 'z_acc'))
        pitch_checkbox.stateChanged.connect(lambda state: self.slot_series_visibility_changed(state, 'pitch'))
        roll_checkbox.stateChanged.connect(lambda state: self.slot_series_visibility_changed(state, 'roll'))
        yaw_checkbox.stateChanged.connect(lambda state: self.slot_series_visibility_changed(state, 'yaw'))
        # view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QGridLayout()
        layout.addWidget(view_label, 0, 0, 0, 0)
        layout.addWidget(x_acc_checkbox, 0, 1)
        layout.addWidget(y_acc_checkbox, 0, 2)
        layout.addWidget(z_acc_checkbox, 0, 3)
        layout.addWidget(pitch_checkbox, 0, 4)
        layout.addWidget(roll_checkbox, 0, 5)
        layout.addWidget(yaw_checkbox, 0, 6)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.chart_view)
        self.setLayout(main_layout)
        
    def slot_read_file_and_plot(self, file_path):
        if file_path is None:
            return
        self.update_chart_data(file_path)
        self.redraw_chart()
    
    def redraw_chart(self):
        series_colors = {
            'x_acc': QColor(255, 245, 50),
            'y_acc': QColor(130, 255, 50),
            'z_acc': QColor(50, 255, 200),
            'pitch': QColor(50, 145, 255),
            'roll': QColor(130, 50, 255),
            'yaw': QColor(255, 50, 200),
        }
        self.chart.removeAllSeries()
        self.chart.removeAxis(self.axis_x)  # 移除旧坐标轴
        self.chart.removeAxis(self.axis_y)  # 移除旧坐标轴
        
        # 设置x轴间隔为50
        self.axis_x.setTickInterval(50)
        self.axis_x.setTickType(QValueAxis.TickType.TicksDynamic)
        self.axis_y.setRange(-3, 3)  # 设置y轴范围
        # 添加坐标轴
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.chart.removeAllSeries()
        
        for col in self.series_data.keys():
            if not self.series_visibility[col]:
                continue
            series = QLineSeries()
            series.setName(col)
            series.setColor(series_colors[col])
            for i in range(len(self.series_data[col])):
                series.append(i, self.series_data[col][i])
            self.chart.addSeries(series)
            
            series.attachAxis(self.axis_x)
            series.attachAxis(self.axis_y)

    
    
    def update_chart_data(self, file_path=None):
        if file_path is None:
            return
        try:
            records = pd.read_csv(file_path, header=0)
            records.columns = records.columns.str.strip()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'错误: {e}')
            return
        self.chart.removeAllSeries()
        self.series_data = {
            'x_acc': list(),
            'y_acc': list(),
            'z_acc': list(),
            'pitch': list(),
            'roll': list(),
            'yaw': list(),
        }
        for col in records.columns:
            if col not in self.series_data.keys():
                continue
            for i in range(1, len(records)):
                self.series_data[col].append(float(records[col][i]))
    
                
    def slot_series_visibility_changed(self, state, label):
        if label not in self.series_visibility.keys():
            return
        self.series_visibility[label] = (state == 2) # Qt.CheckState.Checked: 2
        self.redraw_chart()
