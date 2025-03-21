import os
import pandas as pd
import argparse
import matplotlib.pyplot as plt

# 可视化数据集
if __name__ == "__main__":
    parser = argparse.ArgumentParser("tool for visualization of dataset.")
    parser.add_argument("--dataset", type=str, help="directory of dataset.")
    opts = parser.parse_args()

    # 读取数据集目录内可用的记录
    dataset_files = []
    for filename in os.listdir(opts.dataset):
        if filename.endswith(".txt"):
            dataset_files.append(filename)

    # 设置样式
    try:
        plt.style.use("seaborn-v0_8-bright")
    except OSError:
        print("not supported style")
    plot_pos = 1
    for file in dataset_files:
        records = pd.read_csv(f"{opts.dataset}/{file}", header=0)
        record_size = range(0, len(records))
        records.columns = records.columns.str.strip()

        plt.subplot(1, 3, plot_pos)
        plt.title(file)
        plt.grid(True)
        for col in records.columns:
            plt.plot(record_size, records[col])
        plot_pos += 1
        if plot_pos > 3:
            plt.tight_layout()
            plt.show()
            plot_pos = 1

    if plot_pos != 1:
        plt.tight_layout()
        plt.show()
