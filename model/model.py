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


class GestureClassifierV1():
    def __init__(self, num_classes=5, sequence_length=300, num_channels=3):
        super(GestureClassifierV1, self).__init__()
        self.num_classes = num_classes
        self.num_channels = num_channels
        self.sequence_length = sequence_length

        # 网络结构 使用 Sequential API 构建连接关系（Subclassing 会导致 Layer._inbound_node 为空）
        inputs = layers.Input(shape=(sequence_length, num_channels))
        x = layers.Conv1D(
            filters=16, kernel_size=3, strides=2, padding='valid')(inputs)
        x = layers.LeakyReLU()(x)
        x = layers.Conv1D(
            filters=32, kernel_size=3, strides=2, padding='valid')(x)
        x = layers.LeakyReLU()(x)

        x0 = layers.Conv1D(
            filters=16, kernel_size=1, strides=1, padding='valid')(x)
        x0 = layers.LeakyReLU()(x0)

        x1 = layers.Conv1D(
            filters=16, kernel_size=1, strides=1, padding='valid')(x)
        x1 = layers.LeakyReLU()(x1)
        x2 = layers.Conv1D(
            filters=16, kernel_size=1, strides=1, padding='valid')(x1)
        x2 = layers.LeakyReLU()(x2)
        x3 = layers.Conv1D(
            filters=16, kernel_size=1, strides=1, padding='valid')(x2)
        x3 = layers.LeakyReLU()(x3)

        x = layers.concatenate([x0, x1, x2, x3], axis=0)
        x = layers.Flatten()(x)
        x = layers.Dense(self.num_channels)(x)
        outputs = layers.Softmax()(x)

        self.model = keras.models.Model(inputs=inputs, outputs=outputs)


if __name__ == '__main__':
    import keras.losses as losses
    import keras.optimizers as optimizers

    classifier = GestureClassifierV1()
    classifier.model.compile(optimizer=optimizers.Adam(),
                             loss=losses.CategoricalCrossentropy())
    classifier.model.summary()
