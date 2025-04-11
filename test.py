from cProfile import label
import os
import re
from turtle import mode
import keras
import loguru
import nnom
import numpy as np
import pandas as pd
from model.model import GestureClassifier
import tensorflow as tf
import keras.losses as losses
import keras.optimizers as optimizers
import keras.callbacks as callbacks
from sklearn.model_selection import train_test_split
import argparse
import utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_names', nargs='+', type=str, required=True)
    parser.add_argument('--dataset', type=str, required=True)
    opts = parser.parse_args()

    label_to_index = {label: idx for idx,
                      label in enumerate(opts.target_names)}
    dataset_x, dataset_y_labels = utils.read_dataset_directory(
        opts.dataset, ['x_acc', 'y_acc', 'z_acc'])
    for idx in range(len(opts.target_names)):
        label_to_index[opts.target_names[idx]] = idx
    # 将标签转化为 one-hot 编码
    dataset_y = []
    for label in dataset_y_labels:
        dataset_y.append(label_to_index[label])
    dataset_x = keras.utils.pad_sequences(
        dataset_x, padding='post', maxlen=150, dtype='float32')
    _, test_x, _, true_y = train_test_split(
        dataset_x, dataset_y, test_size=0.99)
    true_y = keras.utils.to_categorical(
        true_y, num_classes=len(opts.target_names))
    # 加载模型进行测试
    model = keras.models.load_model('best.tf')
    pred_y = model.predict(test_x)
    pred_y_classes = np.argmax(pred_y, axis=1)
    true_y_classes = np.argmax(true_y, axis=1)
    print(f'数据集数量: {len(test_x)}, 预测结果数量: {len(pred_y_classes)}')
    from sklearn.metrics import classification_report
    print(classification_report(true_y_classes,
          pred_y_classes, target_names=opts.target_names))
