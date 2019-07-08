import keras
from keras import backend as K
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Flatten
from keras.layers import Input
from keras.models import Model
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def cnn_model():
    if K.image_data_format() == 'channels_first':
        input_shape = (3, 50, 50)
    else:
        input_shape = (50, 50, 3)

    model = keras.models.Sequential(name='image')
    model.add(keras.layers.InputLayer(input_shape=input_shape, name='AOI_Image'))
    model.add(Conv2D(32, (3, 3), activation='relu'))  # , input_shape=input_shape, name='Conv2D_1'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(32, (3, 3), activation='relu', name='Conv2D_2'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu', name='Conv2D_3'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(keras.layers.Dense(128, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    # model.add(Dense(10, activation='softmax'))
    # model.summary()
    return model


def combin_model():
    cnn = cnn_model()
    one_hot = Input(shape=(43,), name='AOI_Result')
    x = keras.layers.concatenate([one_hot, cnn.output])
    # x = keras.layers.Dense(128, activation='relu')(x)
    # x = keras.layers.Dropout(0.5)(x)
    main_output = keras.layers.Dense(12, activation='softmax')(x)
    model = Model(inputs=[one_hot, cnn.input], outputs=[main_output])
    return model


if __name__ == "__main__":
    model = combin_model()
    model.compile(
        loss='categorical_crossentropy',
        optimizer=keras.optimizers.adam(lr=0.001, decay=4e-4),
        metrics=['accuracy']
    )
    model.summary()
