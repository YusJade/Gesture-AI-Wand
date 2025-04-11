from loguru import logger
import loguru
import serial
import serial.tools
import serial.tools.list_ports
import re
import os
import argparse

# IMU: x_acc=%f, y_acc=%f, z_acc=%f, pitch=%f, roll=%f, yaw=%f
# 使用正则匹配，开发板需按照该格式向串口打印传感器数据
PATTERN = r"IMU: x_acc=([-+]?\d*\.?\d+), y_acc=([-+]?\d*\.?\d+), z_acc=([-+]?\d*\.?\d+), pitch=([-+]?\d*\.?\d+), roll=([-+]?\d*\.?\d+), yaw=([-+]?\d*\.?\d+)"
BAUD_RATE = 115200


def get_imu_data(str):
    match = re.match(PATTERN, str)
    if not match:
        logger.error("string not match")
    x_acc, y_acc, z_acc, pitch, roll, yaw = re.match(PATTERN, str).groups()
    return x_acc, y_acc, z_acc, pitch, roll, yaw


def init_serialcom(selected_com_index):
    available_serialcoms = [
        com.device for com in serial.tools.list_ports.comports()]
    logger.info(f"available serial coms: {available_serialcoms}")
    while selected_com_index <= 0 or selected_com_index >= len(available_serialcoms):
        print(f"invalid index ({0}~{len(available_serialcoms)} required)")
        selected_com_index = int(
            input("select com want to open by input index: "))

    return serial.Serial(port=available_serialcoms[selected_com_index],
                         baudrate=BAUD_RATE,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=0.5)


def get_run_time():
    folder_pattern = r"run(\d+)"
    run_time = 0
    print(os.listdir("./dataset/runs"))
    for item in os.listdir("./dataset/runs"):
        match = re.match(folder_pattern, item)
        if not match:
            continue
        if int(match.groups()[0]) > run_time:
            run_time = int(match.groups()[0])
    return run_time + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample_count", type=int,
                        default=150, help="size of collected imu data for every record.")
    parser.add_argument("--gesture_name", required=True,
                        type=str, help="name of gesture for these records.")
    parser.add_argument("--record_count", type=int,
                        default=10, help="total size of collected record.")
    parser.add_argument("--serial_com", type=int,
                        default=10, help="index of serial com to open, use 'check_serial_com.py' to look available coms.")
    opts = parser.parse_args()

    # 创建数据集目录
    if not os.path.exists("dataset/runs"):
        os.makedirs("dataset/runs")

    saved_directory = f"dataset/runs/run{get_run_time()}"
    if not os.path.exists(saved_directory):
        os.makedirs(saved_directory)
    logger.info(
        f"dataset will be saved to {saved_directory}")

    serialcom = init_serialcom(opts.serial_com)

    current_record_count = 0
    while current_record_count < opts.record_count:
        current_sample_count = 0
        # 对每次动作采样 sample_count 条传感器数据
        while current_sample_count < opts.sample_count:
            recevied_data_raw = serialcom.read_until()
            try:
                recevied_data = recevied_data_raw.decode("utf-8")
            except UnicodeDecodeError as e:
                loguru.logger.error(
                    f'faild to parse data {recevied_data_raw}, err: {e}')
            if len(recevied_data) == 0:
                continue
            if not re.match(PATTERN, recevied_data):
                print(recevied_data)
                continue
            x_acc, y_acc, z_acc, pitch, roll, yaw = get_imu_data(recevied_data)
            saved_file_name = f"{opts.gesture_name.lower()}_imu_data_{current_record_count}.txt"

            with open(f"{saved_directory}/{saved_file_name}", "a") as file:
                # 新建记录时加入表头
                if current_sample_count == 0:
                    file.write("x_acc, y_acc, z_acc, pitch, roll, yaw\n")
                file.write(
                    f"{x_acc}, {y_acc}, {z_acc}, {pitch}, {roll}, {yaw}\n")

            current_sample_count += 1
            logger.info(
                f"{current_sample_count} sampled from imu: {x_acc}, {y_acc}, {z_acc}, {pitch}, {roll}, {yaw}")
        current_record_count += 1
        logger.info("collected one record")
