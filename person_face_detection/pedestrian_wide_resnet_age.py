# -*- coding: utf-8 -*-
# @Author: Jie Zhou
# @Time: 2019/6/8 下午8:19
# @Project: Keras_age_gender-master
# @File: pedestrian_wide_resnet.py.py
# @Software: PyCharm

import logging
import sys
import numpy as np
from keras.models import Model
from keras.layers import Input, Activation, add, Dense, Flatten, Dropout
from keras.layers.convolutional import Conv2D, AveragePooling2D
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras import backend as K
from keras.optimizers import SGD, Adam
from keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from PIL import Image
import os
from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler, ModelCheckpoint, EarlyStopping
from sklearn.preprocessing import OneHotEncoder


# import resnet


def read_image(img_name):
    im = Image.open(img_name)
    im = im.resize((128, 128))
    data = np.array(im)
    return data


class WideResNet:
    def __init__(self, image_size_w, image_size_h, depth=16, k=8):
        self._depth = depth
        self._k = k
        self._dropout_probability = 0.0
        self._weight_decay = 0.0000001
        self._use_bias = False
        self._weight_init = "he_normal"

        if K.image_dim_ordering() == "th":
            logging.debug("image_dim_ordering = 'th'")
            self._channel_axis = 1
            self._input_shape = (3, image_size_w, image_size_h)
        else:
            logging.debug("image_dim_ordering = 'tf'")
            self._channel_axis = -1
            self._input_shape = (image_size_w, image_size_h, 3)

    # Wide residual network http://arxiv.org/abs/1605.07146
    def _wide_basic(self, n_input_plane, n_output_plane, stride):
        def f(net):
            # format of conv_params:
            #               [ [kernel_size=("kernel width", "kernel height"),
            #               strides="(stride_vertical,stride_horizontal)",
            #               padding="same" or "valid"] ]
            # B(3,3): orignal <<basic>> block
            conv_params = [[3, 3, stride, "same"],
                           [3, 3, (1, 1), "same"]]

            n_bottleneck_plane = n_output_plane

            # Residual block
            for i, v in enumerate(conv_params):
                if i == 0:
                    if n_input_plane != n_output_plane:
                        net = BatchNormalization(axis=self._channel_axis)(net)
                        net = Activation("relu")(net)
                        convs = net
                    else:
                        convs = BatchNormalization(axis=self._channel_axis)(net)
                        convs = Activation("relu")(convs)

                    convs = Conv2D(n_bottleneck_plane, kernel_size=(v[0], v[1]),
                                   strides=v[2],
                                   padding=v[3],
                                   kernel_initializer=self._weight_init,
                                   kernel_regularizer=l2(self._weight_decay),
                                   use_bias=self._use_bias)(convs)
                else:
                    convs = BatchNormalization(axis=self._channel_axis)(convs)
                    convs = Activation("relu")(convs)
                    if self._dropout_probability > 0:
                        convs = Dropout(self._dropout_probability)(convs)
                    convs = Conv2D(n_bottleneck_plane, kernel_size=(v[0], v[1]),
                                   strides=v[2],
                                   padding=v[3],
                                   kernel_initializer=self._weight_init,
                                   kernel_regularizer=l2(self._weight_decay),
                                   use_bias=self._use_bias)(convs)

            # Shortcut Connection: identity function or 1x1 convolutional
            #  (depends on difference between input & output shape - this
            #   corresponds to whether we are using the first block in each
            #   group; see _layer() ).
            if n_input_plane != n_output_plane:
                shortcut = Conv2D(n_output_plane, kernel_size=(1, 1),
                                  strides=stride,
                                  padding="same",
                                  kernel_initializer=self._weight_init,
                                  kernel_regularizer=l2(self._weight_decay),
                                  use_bias=self._use_bias)(net)
            else:
                shortcut = net

            return add([convs, shortcut])

        return f

    # "Stacking Residual Units on the same stage"
    def _layer(self, block, n_input_plane, n_output_plane, count, stride):
        def f(net):
            net = block(n_input_plane, n_output_plane, stride)(net)
            for i in range(2, int(count + 1)):
                net = block(n_output_plane, n_output_plane, stride=(1, 1))(net)
            return net

        return f

    #    def create_model(self):
    def __call__(self, *args, **kwargs):
        logging.debug("Creating model...")

        assert ((self._depth - 4) % 6 == 0)
        n = (self._depth - 4) / 6

        inputs = Input(shape=self._input_shape)

        n_stages = [16, 16 * self._k, 32 * self._k, 64 * self._k]

        conv1 = Conv2D(filters=n_stages[0], kernel_size=(3, 3),
                       strides=(1, 1),
                       padding="same",
                       kernel_initializer=self._weight_init,
                       kernel_regularizer=l2(self._weight_decay),
                       use_bias=self._use_bias)(inputs)  # "One conv at the beginning (spatial size: 32x32)"

        # Add wide residual blocks
        block_fn = self._wide_basic
        conv2 = self._layer(block_fn, n_input_plane=n_stages[0], n_output_plane=n_stages[1], count=n, stride=(1, 1))(
            conv1)
        conv3 = self._layer(block_fn, n_input_plane=n_stages[1], n_output_plane=n_stages[2], count=n, stride=(2, 2))(
            conv2)
        conv4 = self._layer(block_fn, n_input_plane=n_stages[2], n_output_plane=n_stages[3], count=n, stride=(2, 2))(
            conv3)
        batch_norm = BatchNormalization(axis=self._channel_axis)(conv4)
        relu = Activation("relu")(batch_norm)

        # Classifier block
        pool = AveragePooling2D(pool_size=(8, 8), strides=(1, 1), padding="same")(relu)
        flatten = Flatten()(pool)
        # predictions_g = Dense(units=2, kernel_initializer=self._weight_init, use_bias=self._use_bias,
        #                       kernel_regularizer=l2(self._weight_decay), activation="softmax", name='output_g')(flatten)
        predictions_a = Dense(units=5, kernel_initializer=self._weight_init, use_bias=self._use_bias,
                              kernel_regularizer=l2(self._weight_decay), activation="softmax", name='output_a')(flatten)

        # model = Model(inputs=inputs, outputs=[predictions_g, predictions_a])
        model = Model(inputs=inputs, outputs=[predictions_a])

        return model


if __name__ == '__main__':
    # sgd = SGD(lr=0.0001, momentum=0.9, nesterov=True)
    adm = Adam(lr=0.0001)
    model = WideResNet(128, 128, depth=16, k=2).create_model()
    # model.compile(optimizer=adm, loss={'output_g': "categorical_crossentropy",
    #                                    'output_a': "categorical_crossentropy"},
    #               loss_weights={'output_g': 0.7,
    #                             'output_a': 1.},
    #               metrics=['accuracy'])
    model.compile(optimizer=adm, loss={'output_a': "categorical_crossentropy"}, metrics=['accuracy'])
    logging.debug("Model summary...")
    model.count_params()
    model.summary()
    # model = resnet.ResnetBuilder.build_resnet_18((img_channels, img_rows, img_cols), nb_classes)
    # model.compile(loss='categorical_crossentropy',
    #               optimizer='adam',
    # metrics=['accuracy'])

    # if save_model_plot:
    #     logging.debug("Saving model plot...")
    #     mk_dir(MODEL_PATH)
    #     from keras.utils.visualize_util import plot
    #
    #     plot(model, to_file=os.path.join(MODEL_PATH, 'WRN-{0}-{1}.png'.format(depth, k)), show_shapes=True)

    # Data Augmentation based on page 6 (see README for full details)
    logging.debug("Creating ImageDataGenerators...")

    images = []
    y_a = []
    y_g = []
    female_c = 0
    male_c = 0
    data_dir = '/data/zj/total/'
    for f in os.listdir(data_dir):
        fd = os.path.join(data_dir, f)
        images.append(read_image(fd))
        f = f.split('.')[0]
        if f.split('_')[1] == '15':
            this_age = 0
        elif f.split('_')[1] == '30':
            this_age = 1
        elif f.split('_')[1] == '45':
            this_age = 2
        elif f.split('_')[1] == '60':
            this_age = 3
        elif f.split('_')[1] == '70':
            this_age = 4
        if f.split('_')[2] == 'Male':
            this_gender = 0
            male_c += 1
        elif f.split('_')[2] == 'Female':
            this_gender = 1
            female_c += 1

        y_a.append(this_age)
        y_g.append(this_gender)
    print(female_c)
    print(male_c)

    enc_a = OneHotEncoder()
    enc_a.fit([[0], [1], [2], [3], [4]])
    enc_g = OneHotEncoder()
    enc_g.fit([[0], [1]])

    X = np.array(images)
    y_a, y_g = np.array(y_a).reshape((-1, 1)), np.array(y_g).reshape((-1, 1))
    y_a = enc_a.transform(y_a).toarray()
    y_g = enc_g.transform(y_g).toarray()

    # X_train, X_test, y_a_train, y_a_test, y_g_train, y_g_test = train_test_split(X, y_a, y_g, test_size=0.1,
    #                                                                              random_state=30)
    print(y_a)
    print(y_g)
    # print(y_g_train.shape)
    # y_a_train = np_utils.to_categorical(y_a_train, num_classes=5)
    # y_g_train = np_utils.to_categorical(y_g_train, num_classes=2)
    #
    # y_a_test = np_utils.to_categorical(y_a_test, num_classes=5)
    # y_g_test = np_utils.to_categorical(y_g_test, num_classes=2)

    X_train = X.reshape(-1, 128, 128, 3) / 255.
    # X_test = X_test.reshape(-1, 128, 128, 3) / 255.
    y_a_train, y_g_train = y_a, y_g

    print(X_train.shape)

    # dropout_probability = 0.2  # table 6 on page 10 indicates best value (4.17) CIFAR-10

    # weight_decay = 0.0005  # page 10: "Used in all experiments"

    batch_size = 32  # page 8: "Used in all experiments"
    # Regarding nb_epochs, lr_schedule and sgd, see bottom page 10:
    nb_epochs = 200

    callbacks = [
        ModelCheckpoint('pedestrian_weights_a.{epoch:02d}-{val_loss:.2f}.hdf5',
                        monitor='val_acc',
                        verbose=1,
                        save_best_only=True,
                        mode='auto'),
        EarlyStopping(monitor='val_loss', patience=10)
    ]

    logging.debug("Running training...")
    # fit the model on the batches generated by train_datagen.flow()
    model.fit([X_train], [y_a_train], batch_size=batch_size, shuffle=True, validation_split=0.15,
              nb_epoch=nb_epochs,
              callbacks=callbacks)

    logging.debug("Saving model...")
    with open(os.path.join('./', 'PWRN-{0}-{1}.json'.format(18, 8)), 'w') as f:
        f.write(model.to_json())
    model.save_weights(os.path.join('./', 'PWRN-{0}-{1}.h5'.format(18, 8)), overwrite=True)
