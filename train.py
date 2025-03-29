from cProfile import label
import os
import re
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
import keras.utils as utils
from sklearn.model_selection import train_test_split
import argparse


def split_train_valid(dataset_x: np.ndarray, dataset_y: np.ndarray, valid_ratio=0.3, test_ratio=0.1):
    x_train, x_test, y_train, y_test = train_test_split(
        dataset_x, dataset_y, test_size=test_ratio, train_size=1 - test_ratio
    )

    x_train, x_valid, y_train, y_valid = train_test_split(
        x_train, y_train, test_size=valid_ratio, train_size=1 - valid_ratio
    )

    return {
        'x_train': x_train,
        'y_train': y_train,
        'x_valid': x_valid,
        'y_valid': y_valid,
        'x_test': x_test,
        'y_test': y_test,
    }


def read_dataset_directory(dataset_dir: str, target_columns: list):
    dataset_x = []
    dataset_y = []
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
            dataset_y.append(label)

            df = pd.read_csv(f'{dataset_dir}/{file}', skipinitialspace=True)
            df = df[target_columns]
            dataset_x.append(df.to_numpy())
    return dataset_x, dataset_y


def train_model(x_train, y_train, x_valid, y_valid, input_shape: tuple):
    classifier = GestureClassifier()
    # input_shape = [None] + input_shape
    # print(type(x_train))
    # input_tensor = keras.layers.Input(shape=input_shape, dtype='float32')
    # output = classifier.model(input_tensor)
    classifier.model.compile(optimizer=optimizers.Adam(),
                             loss=losses.CategoricalCrossentropy(),
                             metrics=['accuracy'])
    classifier.model.summary()
    # print(classifier.model.conv1d1._inbound_nodes,
    #       classifier.model.input_layer._inbound_nodes)

    early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10)
    checkpoint = callbacks.ModelCheckpoint(
        'best.tf', monitor='val_accuracy', save_best_only=True)

    # print(output.shape, input_tensor.shape, x_train.shape, y_train.shape)
    history = classifier.model.fit(
        x=x_train,
        y=y_train,
        batch_size=1,
        epochs=1,
        validation_data=(x_valid, y_valid),
        shuffle=True,
        callbacks=[early_stopping, checkpoint]
    )

    nnom.generate_model(classifier.model, x_test=x_valid, name="weight.h")

    del classifier.model
    tf.keras.backend.clear_session()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str)
    parser.add_argument('--num_classes', type=int, default=3)
    parser.add_argument('--sequence_length', type=int, default=150)
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--input_shape', nargs='+', type=int, required=True)
    parser.add_argument('--labels', nargs='+', type=str, required=True)
    parser.add_argument('--enable_channels', nargs='+',
                        choices=['x_acc', 'y_acc', 'z_acc',
                                 'pitch', 'roll', 'yaw'],
                        default=['x_acc', 'y_acc', 'z_acc'])

    opts = parser.parse_args()
    if len(opts.labels) != opts.num_classes:
        loguru.logger.error(
            'args: length of --labels must equal to --num_calsses')
    # print(opts.labels)
    label_to_index = {label: idx for idx, label in enumerate(opts.labels)}

    for idx in range(len(opts.labels)):
        label_to_index[opts.labels[idx]] = idx
    # 读取传感器数据集，包括各指标的值和动作的标签
    dataset_x, dataset_y_labels = read_dataset_directory(
        opts.dataset, opts.enable_channels)
    # 将标签转化为 one-hot 编码
    dataset_y = []
    for label in dataset_y_labels:
        dataset_y.append(label_to_index[label])
    dataset_x = utils.pad_sequences(
        dataset_x, padding='post', maxlen=opts.sequence_length, dtype='float32')

    dataset_y = utils.to_categorical(dataset_y, num_classes=opts.num_classes)
    split_dataset_dict = split_train_valid(dataset_x, dataset_y)

    train_model(
        x_train=split_dataset_dict['x_train'],
        y_train=split_dataset_dict['y_train'],
        x_valid=split_dataset_dict['x_valid'],
        y_valid=split_dataset_dict['y_valid'],
        input_shape=opts.input_shape
    )
    # print(split_dataset_dict)
