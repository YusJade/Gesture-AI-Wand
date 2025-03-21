# Gesture AI Wand

## 配置 Python 环境

> 确保安装了 Anaconda 或 miniconda。

在本仓库目录下执行：

```sh
# 在本仓库目录下执行
conda create --name GestureAIWand python=3.9
# 激活环境
conda activate GestureAIWand
# 安装项目所需的包
pip install -r ./requirements.txt
```

## 制作数据集

### 查看设备上的可用串口

运行 utils\collect_dataset.py ：

```sh
# available serial coms:
- index: 0, device: COM4, 蓝牙链接上的标准串行 (COM4)
- index: 1, device: COM3, 蓝牙链接上的标准串行 (COM3)
- index: 2, device: COM5, 蓝牙链接上的标准串行 (COM5)
- index: 3, device: COM6, 蓝牙链接上的标准串行 (COM6)
- index: 4, device: COM7, USB-SERIAL CH340 (COM7)
```

### 从指定串口上采集特定动作的数据集

例如：

```sh
python .\util\extract_imu_data.py \
  --sample_count 200 \
  --gesture_name UpAndDow \
  --record_count 100 \
  --serial_com 4
```

各个参数的意义：

- sample_count ： 每次动作的采样数，即用于表征一次动作的传感器数据帧数量。
- gesture_name ： 要采集数据的动作名。
- record_count ： 要采集的记录数量，每个记录代表一次动作。
- serial_com ：要打开的串口的 index，可以通过 `utils\check_serial_com.py` 查看 index 值。

数据集将生成在 `dataset\runs\run<num>\<gesture_name>_imu_data_<num>.txt` 中。
