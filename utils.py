import pandas as pd
import loguru
import re
import os


def read_dataset_directory(dataset_dir: str, target_columns: list):
    """读取数据集目录

    Args:
        dataset_dir (str): 数据集所在的目录
        target_columns (list): 读取指定列的数据

    Returns:
        tuple: 
    """
    dataset_x = []
    dataset_y = []
    loguru.logger.info(f'加载数据集 {dataset_dir}')
    for file in os.listdir(dataset_dir):
        if file.endswith('.txt'):
            match = re.match(
                r'^(\w+)_imu_data_\d+\.txt$', file)
            if not match:
                label = 'None'
                loguru.logger.error(
                    f'failed to get label from \"{file}\", fallback to \"None\"')
            else:
                label = match.group(1)
            try:
                df = pd.read_csv(f'{dataset_dir}/{file}',
                                 skipinitialspace=True)
            except Exception as e:
                loguru.logger.warning(f'跳过项 {e}')
                continue
            df = df[target_columns]
            dataset_y.append(label)
            dataset_x.append(df.to_numpy())
            loguru.logger.info(f'加载项 {file}')
    return dataset_x, dataset_y
