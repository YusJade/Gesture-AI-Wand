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
import keras.utils as utils
from sklearn.model_selection import train_test_split
import argparse


def split_train_valid(dataset_x: np.ndarray, dataset_y: np.ndarray, valid_ratio=0.25, test_ratio=0.05):
    x_train, x_test, y_train, y_test = train_test_split(
        dataset_x, dataset_y, test_size=test_ratio, train_size=1 - test_ratio, random_state=31
    )

    x_train, x_valid, y_train, y_valid = train_test_split(
        x_train, y_train, test_size=valid_ratio, train_size=1 - valid_ratio, random_state=32
    )

    size_train = len(x_train)
    size_valid = len(x_valid)
    size_test = len(x_test)
    result = {
        'x_train': x_train,
        'y_train': y_train,
        'x_valid': x_valid,
        'y_valid': y_valid,
        'x_test': x_test,
        'y_test': y_test,
    }
    loguru.logger.info(
        f'划分数据集 {size_train}/{size_valid}/{size_test}')
    loguru.logger.info(f'{result}')

    return result


def read_dataset_directory(dataset_dir: str, target_columns: list):
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


def train_model(x_train, y_train, x_valid, y_valid, num_channels: int, num_classes=3, batch_size=10, epochs=10):
    classifier = GestureClassifier(
        num_classes=num_classes, num_channels=num_channels)
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
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(x_valid, y_valid),
        shuffle=True,
        callbacks=[early_stopping, checkpoint]
    )

    nnom.generate_model(classifier.model, x_test=x_valid, name="weights.h")

    del classifier.model
    tf.keras.backend.clear_session()

    return history


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
    split_dataset_dict = split_train_valid(
        dataset_x, dataset_y, valid_ratio=0.3, test_ratio=0.3)

    history = train_model(
        x_train=split_dataset_dict['x_train'],
        y_train=split_dataset_dict['y_train'],
        x_valid=split_dataset_dict['x_valid'],
        y_valid=split_dataset_dict['y_valid'],
        num_channels=len(opts.enable_channels),
        num_classes=opts.num_classes,
        batch_size=opts.batch_size,
        epochs=opts.epochs
    )

    val_accuracy = history.history['val_accuracy'][-1]
    print(f'验证集精确度：{val_accuracy: .4f}')

    # 加载模型进行测试
    model = keras.models.load_model('best.tf')
    test_x = split_dataset_dict['x_test']
    # print(f'输入测试数据:\n {test_data}')
    y_pred = model.predict(split_dataset_dict['x_test'])
    y_true = split_dataset_dict['y_test']
    # print(y_pred)
    # print(y_true)
    y_true_classes = np.argmax(y_true, axis=1)
    y_pred_classes = np.argmax(y_pred, axis=1)

    from sklearn.metrics import classification_report
    print(classification_report(y_true_classes,
          y_pred_classes, target_names=opts.labels))

    print('nnom evaluation:\n')
    nnom.evaluate_model(model, test_x, y_true)
    print(test_x[0], y_true[0])
    nnom.generate_test_bin(test_x, y_true, name='test_data.bin')
