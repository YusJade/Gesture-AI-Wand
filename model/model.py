import keras
import tensorflow as tf
from tensorflow.keras.models import load_model, save_model  # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences  # type: ignore
import keras.layers as layers


class GestureClassifier():
    def __init__(self, num_classes=3, sequence_length=150, num_channels=3):
        super(GestureClassifier, self).__init__()
        self.num_classes = num_classes
        self.num_channels = num_channels
        self.sequence_length = sequence_length

        # 网络结构 使用 Sequential API 构建连接关系（Subclassing 会导致 Layer._inbound_node 为空）
        inputs = layers.Input(shape=(sequence_length, num_channels))
        x = layers.Conv1D(
            filters=50, kernel_size=3, strides=3, padding='valid')(inputs)
        x = layers.LeakyReLU()(x)
        x = layers.Conv1D(filters=10, kernel_size=5,
                          strides=5, padding='valid')(x)
        x = layers.Flatten()(x)
        x = layers.LeakyReLU()(x)
        x = layers.Dense(num_classes)(x)
        outputs = layers.Softmax()(x)

        self.model = keras.models.Model(inputs=inputs, outputs=outputs)
