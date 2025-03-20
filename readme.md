# Gesture AI Wand

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

数据集将生成在 `dataset\runs\run<x>\<gesture_name>_imu_data.txt` 中。
