
import argparse
import os
import re
import serial.tools.list_ports
import serial.tools
import serial
import loguru
from loguru import logger

from PyQt6.QtCore import pyqtSignal, QObject, QThread

# IMU: x_acc=%f, y_acc=%f, z_acc=%f, pitch=%f, roll=%f, yaw=%f
# 使用正则匹配，开发板需按照该格式向串口打印传感器数据
PATTERN = r"IMU: x_acc=([-+]?\d*\.?\d+), y_acc=([-+]?\d*\.?\d+), z_acc=([-+]?\d*\.?\d+), pitch=([-+]?\d*\.?\d+), roll=([-+]?\d*\.?\d+), yaw=([-+]?\d*\.?\d+)"
DATASET_DIR = "../../dataset/runs"

class DatasetLogic(QObject):
    error_signal = pyqtSignal(str)
    warning_signal = pyqtSignal(str)
    get_serial_signal = pyqtSignal(str)
    directory_changed = pyqtSignal(str)

    def __init__(self, sample_count=150, record_count=30, gesture='unknown'):
        super().__init__()
        self.sample_count = sample_count
        self.record_count = record_count
        self.gesture = gesture
    
    def update_gesture(self, gesture):
        self.gesture = gesture

    def get_run_time(self):
        folder_pattern = r"run(\d+)"
        run_time = 0
        for item in os.listdir(DATASET_DIR):
            match = re.match(folder_pattern, item)
            if not match:
                continue
            if int(match.groups()[0]) > run_time:
                run_time = int(match.groups()[0])
        return run_time + 1

    def prepare_directory(self):
        """准备保存数据集的目录
        """
        if not os.path.exists(DATASET_DIR):
            os.makedirs(DATASET_DIR)
        saved_directory = f"{DATASET_DIR}/run{self.get_run_time()}"
        if not os.path.exists(saved_directory):
            os.makedirs(saved_directory)
        logger.info(
            f"本次录制的数据集将会保存至: {saved_directory}")
        self.saved_directory = saved_directory

    def open_serial(self, serial_com_index=0, daudrate=115200):
        """打开串口
        Args:
            serial_com_index (int, optional): 串口索引. Defaults to 0.
            daudrate (int, optional): 波特率. Defaults to 115200.
        """
        available_serialcoms = [
            com.device for com in serial.tools.list_ports.comports()]
        logger.info(
            f"当前可用串口: {available_serialcoms}")
        logger.info(
            f"选择串口编号: {serial_com_index}, 波特率: {daudrate}")
        try:
            self.serial = serial.Serial(port=available_serialcoms[serial_com_index],
                                        baudrate=daudrate,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        timeout=0.5)
        except Exception as e:
            self.serial = None
            logger.error(f'无法打开串口, {e}')

    def start_collection(self):
        if self.serial == None:
            logger.error(f'串口未打开')
            return
        self.prepare_directory()
        current_record_count = 0
        while True:
            current_sample_count = 0
            saved_file_name = f"{self.gesture.lower()}_imu_data_{current_record_count}.txt"
            file_path = f"{self.saved_directory}/{saved_file_name}"
            with open(file_path, "a") as file:
                file.write("x_acc, y_acc, z_acc, pitch, roll, yaw\n")
                # 对每次动作采样 sample_count 条传感器数据
                while current_sample_count < self.sample_count:
                    recevied_data_raw = self.serial.read_until()
                    try:
                        recevied_data = recevied_data_raw.decode("utf-8")
                        self.get_serial_signal.emit(recevied_data)
                    except UnicodeDecodeError as e:
                        loguru.logger.error(
                            f'无法解析串口数据 {recevied_data_raw}, {e}')
                    if len(recevied_data) == 0:
                        continue
                    if not re.match(PATTERN, recevied_data):
                        print(recevied_data)
                        continue

                    x_acc, y_acc, z_acc, pitch, roll, yaw = self.parse_imu_data(
                        recevied_data)
                    file.write(
                        f"{x_acc}, {y_acc}, {z_acc}, {pitch}, {roll}, {yaw}\n")

                    current_sample_count += 1
                    logger.info(
                        f"{current_sample_count} sampled from imu: {x_acc}, {y_acc}, {z_acc}, {pitch}, {roll}, {yaw}")
            current_record_count += 1
            logger.info(f"保存至 {file_path}")
            logger.info(f"已采集数据 {current_record_count} 项")
            self.directory_changed.emit(self.saved_directory)

    def parse_imu_data(self, str):
        match = re.match(PATTERN, str)
        if not match:
            logger.error("无法提取传感器数据, 请检查数据输出格式")
        x_acc, y_acc, z_acc, pitch, roll, yaw = re.match(PATTERN, str).groups()
        return x_acc, y_acc, z_acc, pitch, roll, yaw

    def get_dataset_dir(self):
        return self.saved_directory
