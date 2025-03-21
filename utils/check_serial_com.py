import serial
import serial.tools
import serial.tools.list_ports

# 检查当前可用串口
if __name__ == "__main__":
    index = 0
    print("# Available serial coms:")
    for com in serial.tools.list_ports.comports():
        print(f"- index: {index}, device: {com.device}, {com.description}")
        index += 1
